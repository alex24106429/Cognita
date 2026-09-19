import base64
import json
import time
import traceback
import urllib.request
import urllib.error
import pyautogui
from openai import OpenAI
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from config import SYSTEM_PROMPT, TOOLS, BASE_URL, build_system_prompt, load_vault
from device_bridge import DeviceBridge, LocalDeviceBridge


class AgentWorker(QObject):
    log = pyqtSignal(str, str)
    thought = pyqtSignal(str)
    action = pyqtSignal(str, str)
    screenshot = pyqtSignal(bytes)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, api_key: str, model: str, goal: str,
                 action_pause: float, settle_pause: float,
                 base_url: str = None, provider: str = None,
                 reasoning_effort: str = "default",
                 device_bridge: DeviceBridge = None, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or BASE_URL
        self.provider = provider or "OpenRouter"
        self.reasoning_effort = reasoning_effort or "default"
        self.goal = goal
        self.action_pause = action_pause
        self.settle_pause = settle_pause
        self._abort = False
        self.system_prompt = SYSTEM_PROMPT

        # Inject device bridge (Local or Remote)
        self.device = device_bridge or LocalDeviceBridge(
            action_pause=action_pause)
        try:
            self.screen_w, self.screen_h = self.device.get_screen_size()
        except Exception:
            self.screen_w, self.screen_h = 1920, 1080

    @pyqtSlot()
    def stop(self):
        self._abort = True
        self.log.emit(
            "warn", "Abort requested — stopping after current action…")

    def _sleep(self, seconds: float):
        deadline = time.time() + seconds
        while time.time() < deadline:
            if self._abort:
                return
            time.sleep(0.05)

    def _call_anthropic_api(self, messages_history: list):
        url = self.base_url.rstrip("/")
        if not url.endswith("/messages"):
            url = f"{url}/messages"

        anth_tools = [
            {
                "name": t["function"]["name"],
                "description": t["function"]["description"],
                "input_schema": t["function"]["parameters"],
            }
            for t in TOOLS
        ]

        payload = {
            "model": self.model,
            "system": self.system_prompt,
            "messages": messages_history,
            "tools": anth_tools,
            "max_tokens": 1024,
            "temperature": 0.2,
        }

        # Configure reasoning effort for Anthropic
        if self.reasoning_effort != "default" and self.reasoning_effort in ("low", "medium", "high", "xhigh", "max"):
            payload["output_config"] = {"effort": self.reasoning_effort}
            payload["max_tokens"] = max(payload.get("max_tokens", 1024), 4096)

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
                "User-Agent": "Cognita-Agent",
            },
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=45) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        thought_text = ""
        tool_calls = []
        for block in data.get("content", []):
            if block.get("type") == "text":
                thought_text += block.get("text", "")
            elif block.get("type") == "thinking":
                thought_text += block.get("thinking", "")
            elif block.get("type") == "tool_use":
                tool_calls.append(block)

        return thought_text, tool_calls, data.get("content", [])

    @pyqtSlot()
    def run(self):
        try:
            # Dynamically reload vault data if present
            vault_data = load_vault()
            if vault_data:
                self.system_prompt = build_system_prompt(vault_data)
                self.log.emit(
                    "info", "User vault loaded into context (data/vault.json).")
            else:
                self.system_prompt = build_system_prompt(None)
                self.log.emit("info", "No user vault found.")

            self.log.emit("info", f"Provider: {self.provider}")
            self.log.emit("info", f"Model: {self.model}")
            self.log.emit("info", f"Reasoning effort: {self.reasoning_effort}")
            self.log.emit("info", f"Base URL: {self.base_url}")
            self.log.emit(
                "info", f"Screen resolution: {self.screen_w}×{self.screen_h}")
            self.log.emit("task", f"=== Starting Task: {self.goal} ===")

            is_anthropic = (
                self.provider == "Anthropic" or "api.anthropic.com" in self.base_url)
            client = None
            if not is_anthropic:
                client = OpenAI(base_url=self.base_url,
                                api_key=self.api_key or "dummy-key")

            messages = [] if is_anthropic else [
                {"role": "system", "content": self.system_prompt}]
            summary, success = "Loop ended without an explicit finish_task call.", False

            step = 0
            while True:
                if self._abort:
                    summary = "Aborted by user."
                    break

                step += 1
                self.log.emit("step", f"--- Step {step} ---")

                self.status.emit("Capturing screen…")
                try:
                    jpeg = self.device.capture_screen()
                except Exception as e:
                    self.log.emit("error", f"Screen capture failed: {e}")
                    summary, self._abort = f"Screen capture failed: {e}", True
                    break

                self.screenshot.emit(jpeg)
                img_b64 = base64.b64encode(jpeg).decode("utf-8")

                prompt = (f"Task: {self.goal}" if step == 1 else
                          "Current screen state after the last action. Assess the result and act.")

                self.status.emit("Waiting for model…")

                if is_anthropic:
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image", "source": {"type": "base64",
                                                         "media_type": "image/jpeg", "data": img_b64}}
                        ]
                    })
                    try:
                        thought_text, raw_tool_calls, assistant_content = self._call_anthropic_api(
                            messages)
                    except Exception as e:
                        self.log.emit(
                            "error", f"Anthropic API call failed: {e}")
                        summary = f"API error: {e}"
                        break

                    messages.append(
                        {"role": "assistant", "content": assistant_content})

                    if thought_text:
                        self.thought.emit(thought_text.strip())

                    if not raw_tool_calls:
                        summary = thought_text or "Model returned no action."
                        break

                    self.status.emit("Executing actions…")
                    completed = False
                    tool_results_content = []

                    for tc in raw_tool_calls:
                        if self._abort:
                            break
                        fn_name = tc.get("name")
                        fn_args = tc.get("input", {})
                        tc_id = tc.get("id")

                        self.action.emit(fn_name, json.dumps(
                            fn_args, ensure_ascii=False))
                        try:
                            result = self.device.execute_tool(
                                fn_name, fn_args, self._sleep)
                        except pyautogui.FailSafeException:
                            self.log.emit(
                                "error", "PyAutoGUI fail-safe triggered (mouse in corner).")
                            summary, self._abort = "Aborted via fail-safe.", True
                            break
                        except Exception as e:
                            result = f"Tool error: {e}"
                            self.log.emit("error", result)

                        self.log.emit("result", result)
                        tool_results_content.append({
                            "type": "tool_result",
                            "tool_use_id": tc_id,
                            "content": result,
                        })

                        if fn_name == "finish_task":
                            summary, completed, success = fn_args.get(
                                "summary", "Done."), True, True
                            break

                    messages.append(
                        {"role": "user", "content": tool_results_content})

                else:
                    # Standard OpenAI-compatible format
                    messages.append({
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {
                                "url": f"data:image/jpeg;base64,{img_b64}"}}
                        ],
                    })

                    extra_headers = {}
                    is_openrouter = self.provider == "OpenRouter" or "openrouter.ai" in self.base_url
                    is_openai = self.provider == "OpenAI" or "api.openai.com" in self.base_url
                    is_gemini = self.provider == "Gemini" or "generativelanguage.googleapis.com" in self.base_url
                    is_deepseek = self.provider == "DeepSeek" or "deepseek.com" in self.base_url

                    if is_openrouter:
                        extra_headers = {
                            "HTTP-Referer": "https://localhost", "X-Title": "Cognita-Agent"}

                    create_kwargs = {
                        "model": self.model,
                        "messages": messages,
                        "tools": TOOLS,
                        "tool_choice": "auto",
                        "extra_headers": extra_headers if extra_headers else None,
                        "temperature": 0.2,
                    }

                    # Pass reasoning effort if explicitly configured
                    if self.reasoning_effort != "default":
                        if is_gemini:
                            # Gemini's OpenAI-compatible endpoint accepts reasoning_effort at the top level
                            effort = self.reasoning_effort
                            if effort in ("xhigh", "max"):
                                effort = "high"
                            if effort in ("none", "minimal", "low", "medium", "high"):
                                create_kwargs["reasoning_effort"] = effort
                        elif is_openai:
                            effort = self.reasoning_effort
                            if effort in ("none", "minimal", "low", "medium", "high", "xhigh"):
                                create_kwargs["reasoning_effort"] = effort
                        elif is_deepseek:
                            if self.reasoning_effort == "none" or self.reasoning_effort == "minimal":
                                create_kwargs["extra_body"] = {
                                    "thinking": {"type": "disabled"}
                                }
                            else:
                                effort_map = {
                                    "low": "low",
                                    "medium": "low",
                                    "high": "high",
                                    "xhigh": "high",
                                    "max": "max",
                                    "ultra": "max",
                                }
                                effort = effort_map.get(
                                    self.reasoning_effort, "high")
                                create_kwargs["reasoning_effort"] = effort
                                create_kwargs["extra_body"] = {
                                    "thinking": {"type": "enabled"}
                                }
                        elif is_openrouter:
                            create_kwargs["extra_body"] = {
                                "reasoning": {
                                    "effort": self.reasoning_effort
                                }
                            }
                        else:
                            # Generic OpenAI-compatible local/custom servers
                            create_kwargs["reasoning_effort"] = self.reasoning_effort

                    try:
                        response = client.chat.completions.create(
                            **create_kwargs)
                    except Exception as e:
                        self.log.emit("error", f"API call failed: {e}")
                        summary = f"API error: {e}"
                        break

                    msg = response.choices[0].message
                    messages.append(msg)

                    # Extract reasoning tokens if returned by the model
                    reasoning_text = getattr(msg, "reasoning", None) or getattr(
                        msg, "reasoning_content", None)
                    if isinstance(reasoning_text, dict):
                        reasoning_text = (
                            reasoning_text.get("text")
                            or reasoning_text.get("reasoningContent")
                            or str(reasoning_text)
                        )
                    if isinstance(reasoning_text, str) and reasoning_text.strip():
                        self.thought.emit(reasoning_text.strip())

                    if msg.content:
                        if not reasoning_text:
                            self.thought.emit(msg.content.strip())
                        else:
                            self.log.emit("info", f"💬 {msg.content.strip()}")

                    if not msg.tool_calls:
                        summary = msg.content or (
                            str(reasoning_text) if reasoning_text else "Model returned no action.")
                        break

                    self.status.emit("Executing actions…")
                    completed = False
                    for tc in msg.tool_calls:
                        if self._abort:
                            break
                        fn_name = tc.function.name
                        try:
                            fn_args = json.loads(tc.function.arguments or "{}")
                        except json.JSONDecodeError:
                            fn_args = {}
                        self.action.emit(fn_name, json.dumps(
                            fn_args, ensure_ascii=False))

                        try:
                            result = self.device.execute_tool(
                                fn_name, fn_args, self._sleep)
                        except pyautogui.FailSafeException:
                            self.log.emit(
                                "error", "PyAutoGUI fail-safe triggered (mouse in corner).")
                            summary, self._abort = "Aborted via fail-safe.", True
                            break
                        except Exception as e:
                            result = f"Tool error: {e}"
                            self.log.emit("error", result)

                        self.log.emit("result", result)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "name": fn_name,
                            "content": result,
                        })
                        if fn_name == "finish_task":
                            summary, completed, success = fn_args.get(
                                "summary", "Done."), True, True
                            break

                if completed or self._abort:
                    break
                self.status.emit("Letting UI settle…")
                self._sleep(self.settle_pause)

            try:
                self.screenshot.emit(self.device.capture_screen())
            except Exception:
                pass
            self.finished.emit(success, summary)
        except Exception:
            self.log.emit("error", traceback.format_exc())
            self.finished.emit(False, "Unhandled exception (see log).")
