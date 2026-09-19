import base64
import json
import time
import traceback
import pyautogui
from openai import OpenAI
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from config import SYSTEM_PROMPT, TOOLS, BASE_URL
from actions import capture_screen, execute_tool


class AgentWorker(QObject):
    log = pyqtSignal(str, str)
    thought = pyqtSignal(str)
    action = pyqtSignal(str, str)
    screenshot = pyqtSignal(bytes)
    step = pyqtSignal(int, int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, api_key, model, goal, max_steps,
                 action_pause, settle_pause, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.model = model
        self.goal = goal
        self.max_steps = max_steps
        self.action_pause = action_pause
        self.settle_pause = settle_pause
        self._abort = False
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

    @pyqtSlot()
    def run(self):
        try:
            pyautogui.PAUSE = self.action_pause
            client = OpenAI(base_url=BASE_URL, api_key=self.api_key)
            self.log.emit(
                "info", f"Screen resolution: {self.screen_w}×{self.screen_h}")
            self.log.emit(
                "info", f"Model: {self.model}")
            self.log.emit("task", f"=== Starting Task: {self.goal} ===")

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
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
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{img_b64}"}}
                    ],
                })

                self.status.emit("Waiting for model…")
                try:
                    response = client.chat.completions.create(
                        model=self.model, messages=messages, tools=TOOLS, tool_choice="auto",
                        extra_headers={
                            "HTTP-Referer": "https://localhost", "X-Title": "Cognita-Agent"},
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
                        result = execute_tool(fn_name, fn_args, self.screen_w, self.screen_h,
                                              self._sleep)
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
