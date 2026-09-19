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
from actions import capture_screen, execute_tool


class AgentWorker(QObject):
    log = pyqtSignal(str, str)
    thought = pyqtSignal(str)
    action = pyqtSignal(str, str)
    screenshot = pyqtSignal(bytes)
    step = pyqtSignal(int, int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, api_key: str, model: str, goal: str, max_steps: int,
                 action_pause: float, settle_pause: float,
                 base_url: str = None, provider: str = None, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.model = model
        self.base_url = base_url or BASE_URL
        self.provider = provider or "OpenRouter"
        self.goal = goal
        self.max_steps = max_steps
        self.action_pause = action_pause
        self.settle_pause = settle_pause
        self._abort = False
        self.system_prompt = SYSTEM_PROMPT
        self.screen_w, self.screen_h = pyautogui.size()

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

        # Transform TOOLS into Anthropic's input_schema format
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
            elif block.get("type") == "tool_use":
                tool_calls.append(block)

        return thought_text, tool_calls, data.get("content", [])

    @pyqtSlot()
    def run(self):
        try:
            pyautogui.PAUSE = self.action_pause

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

            for step in range(1, self.max_steps + 1):
                if self._abort:
                    summary = "Aborted by user."
                    break

                self.step.emit(step, self.max_steps)
                self.log.emit("step", f"--- Step {step}/{self.max_steps} ---")

                self.status.emit("Capturing screen…")
                jpeg = capture_screen()
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
                            result = execute_tool(
                                fn_name, fn_args, self.screen_w, self.screen_h, self._sleep)
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
                    if "openrouter.ai" in self.base_url:
                        extra_headers = {
                            "HTTP-Referer": "https://localhost", "X-Title": "Cognita-Agent"}

                    try:
                        response = client.chat.completions.create(
                            model=self.model,
                            messages=messages,
                            tools=TOOLS,
                            tool_choice="auto",
                            extra_headers=extra_headers if extra_headers else None,
                            temperature=0.2,
                        )
                    except Exception as e:
                        self.log.emit("error", f"API call failed: {e}")
                        summary = f"API error: {e}"
                        break

                    msg = response.choices[0].message
                    messages.append(msg)
                    if msg.content:
                        self.thought.emit(msg.content.strip())
                    if not msg.tool_calls:
                        summary = msg.content or "Model returned no action."
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
                            result = execute_tool(
                                fn_name, fn_args, self.screen_w, self.screen_h, self._sleep)
                        except pyautogui.FailSafeException:
                            self.log.emit(
                                "error", "PyAutoGUI fail-safe triggered (mouse in corner).")
                            summary, self._abort = "Aborted via fail-safe.", True
                            break
                        except Exception as e:
                            result = f"Tool error: {e}"
                            self.log.emit("error", result)

                        self.log.emit("result", result)
                        messages.append(
                            {"role": "tool", "tool_call_id": tc.id, "content": result})
                        if fn_name == "finish_task":
                            summary, completed, success = fn_args.get(
                                "summary", "Done."), True, True
                            break

                if completed or self._abort:
                    break
                self.status.emit("Letting UI settle…")
                self._sleep(self.settle_pause)

            try:
                self.screenshot.emit(capture_screen())
            except Exception:
                pass
            self.finished.emit(success, summary)
        except Exception:
            self.log.emit("error", traceback.format_exc())
            self.finished.emit(False, "Unhandled exception (see log).")
