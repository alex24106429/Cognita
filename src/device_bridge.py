import abc
import io
import time
import requests
import pyautogui
from actions import to_screen_coords, execute_tool


class DeviceBridge(abc.ABC):
    @abc.abstractmethod
    def get_screen_size(self) -> tuple[int, int]:
        """Returns (width, height) in pixels."""
        pass

    @abc.abstractmethod
    def capture_screen(self) -> bytes:
        """Returns screenshot as JPEG bytes."""
        pass

    @abc.abstractmethod
    def execute_tool(self, name: str, args: dict, sleep_fn=None) -> str:
        """Executes a computer-use tool."""
        pass


class LocalDeviceBridge(DeviceBridge):
    """Executes actions directly on the local machine."""

    def __init__(self, action_pause: float = 0.5):
        pyautogui.PAUSE = action_pause

    def get_screen_size(self) -> tuple[int, int]:
        return pyautogui.size()

    def capture_screen(self) -> bytes:
        shot = pyautogui.screenshot()
        buf = io.BytesIO()
        shot.save(buf, format="JPEG", quality=85)
        return buf.getvalue()

    def execute_tool(self, name: str, args: dict, sleep_fn=None) -> str:
        w, h = self.get_screen_size()
        return execute_tool(name, args, w, h, sleep_fn)


class RemoteDeviceBridge(DeviceBridge):
    """Communicates with a remote Cognita target daemon over HTTP."""

    def __init__(self, host: str, port: int = 8765, token: str = "", timeout: float = 10.0):
        self.base_url = f"http://{host.rstrip('/')}:{port}"
        self.token = token
        self.timeout = timeout
        self.session = requests.Session()
        if self.token:
            self.session.headers.update(
                {"Authorization": f"Bearer {self.token}"})

    def get_screen_size(self) -> tuple[int, int]:
        resp = self.session.get(f"{self.base_url}/info", timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()
        return data["width"], data["height"]

    def capture_screen(self) -> bytes:
        resp = self.session.get(
            f"{self.base_url}/screen", timeout=self.timeout)
        resp.raise_for_status()
        return resp.content

    def execute_tool(self, name: str, args: dict, sleep_fn=None) -> str:
        if name == "wait":
            duration = float(args.get("seconds", 2))
            if sleep_fn:
                sleep_fn(duration)
            return f"Waited {duration} seconds."

        payload = {"name": name, "args": args}
        resp = self.session.post(
            f"{self.base_url}/execute", json=payload, timeout=self.timeout + 10)
        resp.raise_for_status()
        return resp.json().get("result", "")
