import os
import sys
import io
import time
import base64
import json
import pyautogui
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("[Error] OPENAI_API_KEY is not set. Please add it to your .env file.")
    sys.exit(1)

# Safety: Moving mouse to any screen corner immediately aborts the script
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

MODEL_NAME = "nex-agi/nex-n2.5-pro:free"

SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()

def capture_screen_base64() -> str:
    """Captures desktop screenshot, resizes if needed, and returns base64 string."""
    screenshot = pyautogui.screenshot()
    buffered = io.BytesIO()
    screenshot.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def to_screen_coords(norm_x: int, norm_y: int) -> tuple[int, int]:
    """Converts Nex-N2.5 normalized [0, 1000] coordinates to monitor pixels."""
    real_x = int((norm_x / 1000.0) * SCREEN_WIDTH)
    real_y = int((norm_y / 1000.0) * SCREEN_HEIGHT)
    return real_x, real_y

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "mouse_click",
            "description": "Click at a specific coordinate on the screen.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {
                        "type": "integer",
                        "description": "X coordinate in normalized [0-1000] space.",
                    },
                    "y": {
                        "type": "integer",
                        "description": "Y coordinate in normalized [0-1000] space.",
                    },
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
                    "press_enter": {
                        "type": "boolean",
                        "description": "Whether to press Enter key after typing.",
                    },
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
                "properties": {
                    "seconds": {"type": "number", "description": "Seconds to pause."}
                },
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
                    "summary": {
                        "type": "string",
                        "description": "Summary of actions taken and final result.",
                    }
                },
                "required": ["summary"],
            },
        },
    },
]


def execute_tool(name: str, args: dict) -> str:
    """Executes the action on the operating system."""
    print(f"\n[EXECUTION] Tool: {name} | Args: {args}")

    if name == "mouse_click":
        x, y = to_screen_coords(args["x"], args["y"])
        button = args.get("button", "left")

        pyautogui.moveTo(x, y, duration=0.3)
        if button == "double":
            pyautogui.doubleClick()
        elif button == "right":
            pyautogui.rightClick()
        else:
            pyautogui.click()
        return f"Clicked at screen ({x}, {y}) [normalized {args['x']}, {args['y']}]."

    elif name == "type_text":
        text = args["text"]
        pyautogui.write(text, interval=0.03)
        if args.get("press_enter"):
            pyautogui.press("enter")
        return f"Typed '{text}' (press_enter={args.get('press_enter', False)})."

    elif name == "press_hotkey":
        keys = args["keys"]
        pyautogui.hotkey(*keys)
        return f"Pressed hotkey combination: {keys}."

    elif name == "wait":
        duration = args.get("seconds", 2)
        time.sleep(duration)
        return f"Waited {duration} seconds."

    elif name == "finish_task":
        return f"Task Completed: {args.get('summary')}"

    return f"Unknown tool: {name}"


def run_computer_agent(user_goal: str, max_steps: int = 15):
    """Main perception-action-verification loop."""
    print(f"\n=== Starting Task: {user_goal} ===")

    system_prompt = (
        "You are an autonomous computer-use agent. "
        "You operate the desktop by observing screenshots and calling mouse/keyboard tools.\n"
        "Grounding Rules:\n"
        "1. Screen coordinates are normalized: X and Y ranges from 0 to 1000 (top-left is [0, 0], bottom-right is [1000, 1000]).\n"
        "2. Look closely at the latest screenshot to verify if your previous action succeeded.\n"
        "3. Only perform one logical action at a time so you can inspect the visual feedback.\n"
        "4. When the goal is completed, call 'finish_task'."
    )

    messages = [{"role": "system", "content": system_prompt}]

    for step in range(1, max_steps + 1):
        print(f"\n--- Step {step}/{max_steps} ---")

        # 1. Take a screenshot for visual feedback
        img_b64 = capture_screen_base64()

        # 2. Append user / screenshot state
        if step == 1:
            user_content = [
                {"type": "text", "text": f"Task: {user_goal}"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
                },
            ]
        else:
            user_content = [
                {
                    "type": "text",
                    "text": "Current screen state after the last action. Please assess the result and take the next step.",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"},
                },
            ]

        messages.append({"role": "user", "content": user_content})

        # 3. Call LLM via OpenRouter
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            extra_headers={
                "HTTP-Referer": "https://localhost",
                "X-Title": "Nex-N2.5-Pro-Computer-Agent",
            },
            temperature=0.2,
        )

        response_msg = response.choices[0].message
        messages.append(response_msg)

        # Print model's thought process if any text was produced
        if response_msg.content:
            print(f"[LLM Thought]:\n{response_msg.content}")

        # 4. Check if the model called any tools
        if not response_msg.tool_calls:
            print("[Info]: No tool action taken by model. Exiting loop.")
            break

        # 5. Execute tool calls
        completed = False
        for tool_call in response_msg.tool_calls:
            fn_name = tool_call.function.name
            fn_args = json.loads(tool_call.function.arguments)

            result = execute_tool(fn_name, fn_args)

            # Append tool result back into context
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                }
            )

            if fn_name == "finish_task":
                print(f"\n[DONE] {result}")
                completed = True
                break

        if completed:
            break

        # Small pause for the UI to settle before taking the next screenshot
        time.sleep(1.0)


if __name__ == "__main__":
    # Allows passing task via command line argument, or prompts for one interactively
    if len(sys.argv) > 1:
        task = " ".join(sys.argv[1:]).strip()
    else:
        try:
            task = input("Enter the task for the computer agent: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)

    if not task:
        print("[Error] Task cannot be empty.")
        sys.exit(1)

    run_computer_agent(task)