import io
import pyautogui


def capture_screen() -> bytes:
    shot = pyautogui.screenshot()
    buf = io.BytesIO()
    shot.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def to_screen_coords(nx: int, ny: int, screen_w: int, screen_h: int):
    return int((nx / 1000.0) * screen_w), int((ny / 1000.0) * screen_h)


def execute_tool(name: str, args: dict, screen_w: int, screen_h: int,
                 dry_run: bool = False, sleep_fn=None) -> str:
    if dry_run and name not in ("wait", "finish_task"):
        return f"[DRY-RUN] Would have executed {name} with {args}."

    if name == "mouse_click":
        x, y = to_screen_coords(args["x"], args["y"], screen_w, screen_h)
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
        if sleep_fn:
            sleep_fn(duration)
        return f"Waited {duration} seconds."

    if name == "finish_task":
        return f"Task Completed: {args.get('summary')}"

    return f"Unknown tool: {name}"
