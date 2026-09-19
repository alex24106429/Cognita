import io
import sys
import pyautogui


def capture_screen() -> bytes:
    shot = pyautogui.screenshot()
    buf = io.BytesIO()
    shot.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def to_screen_coords(nx: int, ny: int, screen_w: int, screen_h: int):
    return int((nx / 1000.0) * screen_w), int((ny / 1000.0) * screen_h)


def execute_tool(name: str, args: dict, screen_w: int, screen_h: int,
                 sleep_fn=None) -> str:
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

    if name in ("mouse_scroll", "scroll"):
        loc_str = ""
        # Move cursor first if target coordinates are provided
        if "x" in args and "y" in args and args["x"] is not None and args["y"] is not None:
            x, y = to_screen_coords(args["x"], args["y"], screen_w, screen_h)
            pyautogui.moveTo(x, y, duration=0.2)
            loc_str = f" at screen ({x}, {y}) [normalized {args['x']}, {args['y']}]"

        direction = str(args.get("direction", "down")).lower()
        amount = args.get("amount") if args.get(
            "amount") is not None else args.get("clicks", 5)
        try:
            amount = int(amount)
        except (ValueError, TypeError):
            amount = 5

        # In PyAutoGUI, positive is up, negative is down
        if direction == "up":
            clicks = abs(amount)
        elif direction == "down":
            clicks = -abs(amount)
        else:
            clicks = amount

        # Windows WHEEL_DELTA compensation: 1 notch = 120 units in win32 mouse_event.
        # Small click counts (< 50) are scaled so the OS registers visible movement.
        scroll_units = clicks
        if sys.platform == "win32" and abs(clicks) < 50:
            scroll_units = clicks * 120

        pyautogui.scroll(scroll_units)
        dir_label = "up" if clicks > 0 else "down"
        return f"Scrolled {dir_label} by {abs(clicks)} steps{loc_str}."

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
