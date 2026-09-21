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
        pyautogui.moveTo(x, y, duration=0)
        if button == "double":
            pyautogui.doubleClick()
        elif button == "right":
            pyautogui.rightClick()
        else:
            pyautogui.click()
        return f"Clicked at screen ({x}, {y}) [normalized {args['x']}, {args['y']}]."

    if name == "click_and_type":
        x, y = to_screen_coords(args["x"], args["y"], screen_w, screen_h)
        pyautogui.moveTo(x, y, duration=0)
        pyautogui.click()

        text = args["text"]

        pyautogui.write(text, interval=0.001)

        if args.get("press_enter"):
            pyautogui.press("enter")
        return f"Clicked at ({x}, {y}) and typed text ({len(text)} chars)."

    if name in ("mouse_scroll", "scroll"):
        # If no coordinates provided, move mouse to safe screen center to avoid scrolling inside textareas
        if "x" in args and "y" in args and args["x"] is not None and args["y"] is not None:
            x, y = to_screen_coords(args["x"], args["y"], screen_w, screen_h)
            pyautogui.moveTo(x, y, duration=0)
            loc_str = f" at screen ({x}, {y})"
        else:
            pyautogui.moveTo(screen_w // 2, screen_h // 2, duration=0)
            loc_str = " at center viewport"

        direction = str(args.get("direction", "down")).lower()
        amount = args.get("amount") if args.get(
            "amount") is not None else args.get("clicks", 5)
        try:
            amount = int(amount)
        except (ValueError, TypeError):
            amount = 5

        clicks = abs(amount) if direction == "up" else -abs(amount)
        scroll_units = clicks * \
            120 if sys.platform == "win32" and abs(clicks) < 50 else clicks

        pyautogui.scroll(scroll_units)
        dir_label = "up" if clicks > 0 else "down"
        return f"Scrolled {dir_label} by {abs(clicks)} steps{loc_str}."

    if name == "type_text":
        text = args["text"]
        pyautogui.write(text, interval=0.01)
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
