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

LOG_COLORS = {
    "info": "#8ab4f8",
    "task": "#c792ea",
    "step": "#ffcb6b",
    "action": "#7bd88f",
    "result": "#9aa0b4",
    "think": "#e6e6e6",
    "warn": "#ffb86c",
    "error": "#ff6b6b",
}
