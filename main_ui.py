#!/usr/bin/env python3
import os
import sys
import io
import time
import base64
import json
import traceback

import pyautogui
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

from PyQt6.QtCore import (
    Qt, QObject, QThread, pyqtSignal, pyqtSlot, QSettings, QTimer, QSize
)
from PyQt6.QtGui import QPixmap, QImage, QFont, QIcon, QAction, QTextCursor
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QComboBox, QGroupBox, QSplitter, QPlainTextEdit, QStatusBar,
    QMessageBox, QProgressBar, QFileDialog, QSizePolicy
)

load_dotenv()

pyautogui.FAILSAFE = True          # slam mouse into a corner to abort
pyautogui.PAUSE = 0.5

DEFAULT_MODEL = "nex-agi/nex-n2.5-pro:free"
BASE_URL = "https://openrouter.ai/api/v1"

SYSTEM_PROMPT = (
    "You are an autonomous computer-use agent. "
    "You operate the desktop by observing screenshots and calling mouse/keyboard tools.\n"
    "Grounding Rules:\n"
    "1. Screen coordinates are normalized: X and Y ranges from 0 to 1000 "
    "(top-left is [0, 0], bottom-right is [1000, 1000]).\n"
    "2. Look closely at the latest screenshot to verify if your previous action succeeded.\n"
    "3. Only perform one logical action at a time so you can inspect the visual feedback.\n"
    "4. When the goal is completed, call 'finish_task'."
)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "mouse_click",
            "description": "Click at a specific coordinate on the screen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "X coordinate in normalized [0-1000] space."},
                    "y": {"type": "integer", "description": "Y coordinate in normalized [0-1000] space."},
                    "button": {
                        "type": "string",
                        "enum": ["left", "right", "double"],
                        "description": "Mouse button action to perform.",
                    },
                },
                "required": ["x", "y"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "type_text",
            "description": "Type text into the currently focused input field.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type."},
                    "press_enter": {"type": "boolean", "description": "Whether to press Enter key after typing."},
                },
                "required": ["text"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "press_hotkey",
            "description": "Press key combinations (e.g., ['ctrl', 't'], ['enter'], ['esc']).",
            "parameters": {
                "type": "object",
                "properties": {
                    "keys": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of key names to press in sequence/combination.",
                    }
                },
                "required": ["keys"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "wait",
            "description": "Wait for a given number of seconds for page/app to load.",
            "parameters": {
                "type": "object",
                "properties": {"seconds": {"type": "number", "description": "Seconds to pause."}},
                "required": ["seconds"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "finish_task",
            "description": "Call this tool when the task has been fully completed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "summary": {"type": "string", "description": "Summary of actions taken and final result."}
                },
                "required": ["summary"],
            },
        },
    },
]

#  WORKER  (runs in its own QThread)
class AgentWorker(QObject):
    log        = pyqtSignal(str, str)      # (level, message)
    thought    = pyqtSignal(str)           # model free-text reasoning
    action     = pyqtSignal(str, str)      # (tool name, args json)
    screenshot = pyqtSignal(bytes)         # raw JPEG bytes for preview
    step       = pyqtSignal(int, int)      # (current, total)
    status     = pyqtSignal(str)
    finished   = pyqtSignal(bool, str)     # (success, summary)

    def __init__(self, api_key, model, goal, max_steps, dry_run,
                 action_pause, settle_pause, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.model = model
        self.goal = goal
        self.max_steps = max_steps
        self.dry_run = dry_run
        self.action_pause = action_pause
        self.settle_pause = settle_pause
        self._abort = False
        self.screen_w, self.screen_h = pyautogui.size()

    # ---------------------------------------------------------------- control
    @pyqtSlot()
    def stop(self):
        self._abort = True
        self.log.emit("warn", "Abort requested — stopping after current action…")

    def _sleep(self, seconds: float):
        """Interruptible sleep."""
        deadline = time.time() + seconds
        while time.time() < deadline:
            if self._abort:
                return
            time.sleep(0.05)

    # ------------------------------------------------------------- perception
    def capture_screen(self) -> bytes:
        shot = pyautogui.screenshot()
        buf = io.BytesIO()
        shot.save(buf, format="JPEG", quality=85)
        return buf.getvalue()

    def to_screen_coords(self, nx: int, ny: int):
        return int((nx / 1000.0) * self.screen_w), int((ny / 1000.0) * self.screen_h)

    # ----------------------------------------------------------------- action
    def execute_tool(self, name: str, args: dict) -> str:
        self.action.emit(name, json.dumps(args, ensure_ascii=False))

        if self.dry_run and name not in ("wait", "finish_task"):
            return f"[DRY-RUN] Would have executed {name} with {args}."

        if name == "mouse_click":
            x, y = self.to_screen_coords(args["x"], args["y"])
            button = args.get("button", "left")
            pyautogui.moveTo(x, y, duration=0.3)
            if button == "double":
                pyautogui.doubleClick()
            elif button == "right":
                pyautogui.rightClick()
            else:
                pyautogui.click()
            return f"Clicked at screen ({x}, {y}) [normalized {args['x']}, {args['y']}]."

        if name == "type_text":
            text = args["text"]
            pyautogui.write(text, interval=0.03)
            if args.get("press_enter"):
                pyautogui.press("enter")
            return f"Typed '{text}' (press_enter={args.get('press_enter', False)})."

        if name == "press_hotkey":
            keys = args["keys"]
            pyautogui.hotkey(*keys)
            return f"Pressed hotkey combination: {keys}."

        if name == "wait":
            duration = float(args.get("seconds", 2))
            self._sleep(duration)
            return f"Waited {duration} seconds."

        if name == "finish_task":
            return f"Task Completed: {args.get('summary')}"

        return f"Unknown tool: {name}"

    # ------------------------------------------------------------------- loop
    @pyqtSlot()
    def run(self):
        try:
            pyautogui.PAUSE = self.action_pause
            client = OpenAI(base_url=BASE_URL, api_key=self.api_key)

            self.log.emit("info", f"Screen resolution: {self.screen_w}×{self.screen_h}")
            self.log.emit("info", f"Model: {self.model}"
                                  f"{'   (DRY-RUN: no input will be sent)' if self.dry_run else ''}")
            self.log.emit("task", f"=== Starting Task: {self.goal} ===")

            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            summary = "Loop ended without an explicit finish_task call."
            success = False

            for step in range(1, self.max_steps + 1):
                if self._abort:
                    summary = "Aborted by user."
                    break

                self.step.emit(step, self.max_steps)
                self.log.emit("step", f"--- Step {step}/{self.max_steps} ---")

                # 1) Perceive
                self.status.emit("Capturing screen…")
                jpeg = self.capture_screen()
                self.screenshot.emit(jpeg)
                img_b64 = base64.b64encode(jpeg).decode("utf-8")

                # 2) Build state message
                prompt_text = (
                    f"Task: {self.goal}" if step == 1 else
                    "Current screen state after the last action. "
                    "Please assess the result and take the next step."
                )
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url",
                         "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
                    ],
                })

                # 3) Think
                self.status.emit("Waiting for model…")
                try:
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=TOOLS,
                        tool_choice="auto",
                        extra_headers={
                            "HTTP-Referer": "https://localhost",
                            "X-Title": "Nex-N2.5-Pro-Computer-Agent",
                        },
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
                    self.log.emit("warn", "No tool action taken by model. Exiting loop.")
                    summary = msg.content or "Model returned no action."
                    break

                # 4) Act
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
                        self.log.emit("error", f"Could not parse args for {fn_name}: "
                                               f"{tc.function.arguments!r}")
                    try:
                        result = self.execute_tool(fn_name, fn_args)
                    except pyautogui.FailSafeException:
                        self.log.emit("error", "PyAutoGUI fail-safe triggered (mouse in corner).")
                        summary = "Aborted via fail-safe."
                        self._abort = True
                        break
                    except Exception as e:
                        result = f"Tool error: {e}"
                        self.log.emit("error", result)

                    self.log.emit("result", result)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    })

                    if fn_name == "finish_task":
                        summary = fn_args.get("summary", "Done.")
                        completed = True
                        success = True
                        break

                if completed or self._abort:
                    break

                self.status.emit("Letting the UI settle…")
                self._sleep(self.settle_pause)

            # final screenshot for the record
            try:
                self.screenshot.emit(self.capture_screen())
            except Exception:
                pass

            self.finished.emit(success, summary)

        except Exception:
            self.log.emit("error", traceback.format_exc())
            self.finished.emit(False, "Unhandled exception (see log).")

#  MAIN WINDOW
class MainWindow(QMainWindow):
    request_stop = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cognita")
        self.resize(1180, 760)

        self.settings = QSettings("cognita", "gui")
        self.thread = None
        self.worker = None
        self._last_pixmap = None

        self._build_ui()
        self._load_settings()
        self._apply_style()

    # ------------------------------------------------------------------- UI
    def _build_ui(self):
        central = QWidget()
        root = QVBoxLayout(central)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        # ---------- Config group ----------
        cfg = QGroupBox("Configuration")
        g = QGridLayout(cfg)
        g.setHorizontalSpacing(10)

        g.addWidget(QLabel("OpenRouter API key:"), 0, 0)
        self.key_edit = QLineEdit(os.environ.get("OPENAI_API_KEY", ""))
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_edit.setPlaceholderText("sk-or-v1-…")
        g.addWidget(self.key_edit, 0, 1, 1, 3)

        self.show_key = QCheckBox("Show")
        self.show_key.toggled.connect(
            lambda on: self.key_edit.setEchoMode(
                QLineEdit.EchoMode.Normal if on else QLineEdit.EchoMode.Password)
        )
        g.addWidget(self.show_key, 0, 4)

        g.addWidget(QLabel("Model:"), 1, 0)
        self.model_edit = QComboBox()
        self.model_edit.setEditable(True)
        self.model_edit.addItems([
            DEFAULT_MODEL,
            "nex-agi/nex-n2.5-mini:free",
            "inclusionai/ling-3.0-flash-vl:free",
            "qwen/qwen3.8-27b:free",
            "dots-studio/dots-3-note-preview:free",
        ])
        g.addWidget(self.model_edit, 1, 1, 1, 4)

        g.addWidget(QLabel("Max steps:"), 2, 0)
        self.steps_spin = QSpinBox()
        self.steps_spin.setRange(1, 200)
        self.steps_spin.setValue(15)
        g.addWidget(self.steps_spin, 2, 1)

        g.addWidget(QLabel("Action pause (s):"), 2, 2)
        self.pause_spin = QDoubleSpinBox()
        self.pause_spin.setRange(0.0, 5.0)
        self.pause_spin.setSingleStep(0.1)
        self.pause_spin.setValue(0.5)
        g.addWidget(self.pause_spin, 2, 3)

        g.addWidget(QLabel("Settle pause (s):"), 2, 4)
        self.settle_spin = QDoubleSpinBox()
        self.settle_spin.setRange(0.0, 10.0)
        self.settle_spin.setSingleStep(0.5)
        self.settle_spin.setValue(1.0)
        g.addWidget(self.settle_spin, 2, 5)

        opts = QHBoxLayout()
        self.dry_run_cb = QCheckBox("Dry run (plan only, don't touch mouse/keyboard)")
        self.hide_cb = QCheckBox("Minimise this window while the agent works")
        self.hide_cb.setChecked(True)
        self.autoscroll_cb = QCheckBox("Auto-scroll log")
        self.autoscroll_cb.setChecked(True)
        opts.addWidget(self.dry_run_cb)
        opts.addWidget(self.hide_cb)
        opts.addWidget(self.autoscroll_cb)
        opts.addStretch()
        g.addLayout(opts, 3, 0, 1, 6)

        root.addWidget(cfg)

        # ---------- Task row ----------
        task_box = QGroupBox("Task")
        tl = QHBoxLayout(task_box)
        self.task_edit = QLineEdit()
        self.task_edit.setPlaceholderText(
            "e.g. Open the browser and search for the weather in Berlin")
        self.task_edit.returnPressed.connect(self.start_agent)
        self.task_edit.setMinimumHeight(32)

        self.start_btn = QPushButton("▶  Run Agent")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.setMinimumHeight(34)
        self.start_btn.clicked.connect(self.start_agent)

        self.stop_btn = QPushButton("■  STOP")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setMinimumHeight(34)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_agent)

        tl.addWidget(self.task_edit, 1)
        tl.addWidget(self.start_btn)
        tl.addWidget(self.stop_btn)
        root.addWidget(task_box)

        # ---------- Splitter: log | preview ----------
        splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.addWidget(QLabel("<b>Agent trace</b>"))
        self.log_view = QTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setFont(QFont("Consolas, Menlo, monospace", 10))
        ll.addWidget(self.log_view)

        lbtns = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.log_view.clear)
        save_btn = QPushButton("Save log…")
        save_btn.clicked.connect(self.save_log)
        lbtns.addWidget(clear_btn)
        lbtns.addWidget(save_btn)
        lbtns.addStretch()
        ll.addLayout(lbtns)
        splitter.addWidget(left)

        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.addWidget(QLabel("<b>What the agent sees</b>"))
        self.preview = QLabel("No screenshot yet")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(320, 200)
        self.preview.setObjectName("preview")
        self.preview.setSizePolicy(QSizePolicy.Policy.Ignored,
                                   QSizePolicy.Policy.Ignored)
        rl.addWidget(self.preview, 1)
        splitter.addWidget(right)

        splitter.setSizes([640, 520])
        root.addWidget(splitter, 1)

        # ---------- Status bar ----------
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(220)
        self.progress.setTextVisible(True)
        self.progress.setFormat("step %v / %m")
        self.progress.setVisible(False)

        sb = QStatusBar()
        sb.addPermanentWidget(self.progress)
        self.setStatusBar(sb)
        self.set_status("Idle — fail-safe active: fling the mouse to a screen corner to abort.")

        self.setCentralWidget(central)

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget { background: #1e1f26; color: #e6e6e6; }
            QGroupBox {
                border: 1px solid #34363f; border-radius: 6px;
                margin-top: 10px; padding: 10px 8px 8px 8px; font-weight: 600;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; color: #9aa4ff; }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                background: #262833; border: 1px solid #3a3d4a;
                border-radius: 4px; padding: 5px; selection-background-color: #4b5bd6;
            }
            QPushButton {
                background: #333748; border: 1px solid #454a5e;
                border-radius: 5px; padding: 6px 14px;
            }
            QPushButton:hover  { background: #3d4257; }
            QPushButton:disabled { color: #6b6f7d; background: #262833; }
            QPushButton#startBtn { background: #2f7d4f; border-color: #3a9b62; font-weight: 700; }
            QPushButton#startBtn:hover { background: #379059; }
            QPushButton#stopBtn  { background: #8e2f38; border-color: #ad3a44; font-weight: 700; }
            QPushButton#stopBtn:hover { background: #a3363f; }
            QLabel#preview { border: 1px dashed #3a3d4a; border-radius: 6px; color: #7b8094; }
            QProgressBar { border: 1px solid #3a3d4a; border-radius: 4px; text-align: center; }
            QProgressBar::chunk { background: #4b5bd6; }
        """)

    # -------------------------------------------------------------- settings
    def _load_settings(self):
        s = self.settings
        self.model_edit.setCurrentText(s.value("model", DEFAULT_MODEL))
        self.steps_spin.setValue(int(s.value("max_steps", 15)))
        self.pause_spin.setValue(float(s.value("pause", 0.5)))
        self.settle_spin.setValue(float(s.value("settle", 1.0)))
        self.hide_cb.setChecked(s.value("hide", True, type=bool))
        self.task_edit.setText(s.value("last_task", ""))
        if not self.key_edit.text():
            self.key_edit.setText(s.value("api_key", ""))

    def _save_settings(self):
        s = self.settings
        s.setValue("model", self.model_edit.currentText())
        s.setValue("max_steps", self.steps_spin.value())
        s.setValue("pause", self.pause_spin.value())
        s.setValue("settle", self.settle_spin.value())
        s.setValue("hide", self.hide_cb.isChecked())
        s.setValue("last_task", self.task_edit.text())
        s.setValue("api_key", self.key_edit.text())   # remove this line if you'd rather not persist it

    # ------------------------------------------------------------- log utils
    COLORS = {
        "info":   "#8ab4f8",
        "task":   "#c792ea",
        "step":   "#ffcb6b",
        "action": "#7bd88f",
        "result": "#9aa0b4",
        "think":  "#e6e6e6",
        "warn":   "#ffb86c",
        "error":  "#ff6b6b",
    }

    def append_log(self, level: str, text: str):
        color = self.COLORS.get(level, "#e6e6e6")
        stamp = time.strftime("%H:%M:%S")
        safe = (text.replace("&", "&amp;").replace("<", "&lt;")
                    .replace(">", "&gt;").replace("\n", "<br>"))
        html = (f'<div style="margin:2px 0;">'
                f'<span style="color:#5c6070;">[{stamp}]</span> '
                f'<span style="color:{color};">{safe}</span></div>')
        self.log_view.append(html)
        if self.autoscroll_cb.isChecked():
            self.log_view.moveCursor(QTextCursor.MoveOperation.End)

    def set_status(self, text: str):
        self.statusBar().showMessage(text)

    def save_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save log", "agent_log.txt",
                                              "Text files (*.txt)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_view.toPlainText())
            self.set_status(f"Log saved to {path}")

    # ---------------------------------------------------------------- run/stop
    def start_agent(self):
        if self.thread is not None:
            return

        task = self.task_edit.text().strip()
        key = self.key_edit.text().strip()

        if not key:
            QMessageBox.warning(self, "Missing API key",
                                "Please enter your OpenRouter API key "
                                "(or set OPENAI_API_KEY in your .env file).")
            return
        if not task:
            QMessageBox.warning(self, "Missing task", "Please describe a task for the agent.")
            return

        if not self.dry_run_cb.isChecked():
            confirm = QMessageBox.question(
                self, "Give up control of the mouse & keyboard?",
                "The agent is about to take over your mouse and keyboard.\n\n"
                "Emergency stop: move the mouse into any screen corner, "
                "or press the STOP button.\n\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return

        self._save_settings()
        self._set_running(True)

        self.worker = AgentWorker(
            api_key=key,
            model=self.model_edit.currentText().strip(),
            goal=task,
            max_steps=self.steps_spin.value(),
            dry_run=self.dry_run_cb.isChecked(),
            action_pause=self.pause_spin.value(),
            settle_pause=self.settle_spin.value(),
        )
        self.thread = QThread(self)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.log.connect(self.append_log)
        self.worker.thought.connect(lambda t: self.append_log("think", f"🧠 {t}"))
        self.worker.action.connect(
            lambda n, a: self.append_log("action", f"⚙  {n}  {a}"))
        self.worker.screenshot.connect(self.update_preview)
        self.worker.step.connect(self.update_progress)
        self.worker.status.connect(self.set_status)
        self.worker.finished.connect(self.on_finished)
        self.request_stop.connect(self.worker.stop)

        if self.hide_cb.isChecked() and not self.dry_run_cb.isChecked():
            self.showMinimized()
            QApplication.processEvents()
            time.sleep(0.6)   # let the window animation finish before first shot

        self.thread.start()

    def stop_agent(self):
        if self.worker:
            self.request_stop.emit()
            self.stop_btn.setEnabled(False)
            self.set_status("Stopping…")

    @pyqtSlot(bool, str)
    def on_finished(self, success: bool, summary: str):
        self.append_log("info" if success else "warn",
                        ("✅ DONE — " if success else "⏹ ENDED — ") + summary)
        self.set_status("Finished" if success else "Stopped")
        self.progress.setVisible(False)

        if self.thread:
            self.thread.quit()
            self.thread.wait(3000)
            self.thread.deleteLater()
        if self.worker:
            self.worker.deleteLater()
        self.thread = None
        self.worker = None
        self._set_running(False)

        if self.isMinimized():
            self.showNormal()
            self.raise_()
            self.activateWindow()

    def _set_running(self, running: bool):
        self.start_btn.setEnabled(not running)
        self.stop_btn.setEnabled(running)
        for w in (self.task_edit, self.key_edit, self.model_edit, self.steps_spin,
                  self.pause_spin, self.settle_spin, self.dry_run_cb, self.hide_cb):
            w.setEnabled(not running)
        self.progress.setVisible(running)

    # ------------------------------------------------------------- feedback
    @pyqtSlot(int, int)
    def update_progress(self, current: int, total: int):
        self.progress.setMaximum(total)
        self.progress.setValue(current)

    @pyqtSlot(bytes)
    def update_preview(self, jpeg: bytes):
        img = QImage.fromData(jpeg, "JPEG")
        if img.isNull():
            return
        self._last_pixmap = QPixmap.fromImage(img)
        self._rescale_preview()

    def _rescale_preview(self):
        if self._last_pixmap is None:
            return
        self.preview.setPixmap(self._last_pixmap.scaled(
            self.preview.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._rescale_preview()

    def closeEvent(self, e):
        if self.thread is not None:
            r = QMessageBox.question(
                self, "Agent still running",
                "The agent is still running. Stop it and quit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if r != QMessageBox.StandardButton.Yes:
                e.ignore()
                return
            self.request_stop.emit()
            self.thread.quit()
            self.thread.wait(5000)
        self._save_settings()
        e.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Cognita")
    win = MainWindow()

    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()