import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ICONS_DIR = PROJECT_ROOT / "icons"
DATA_DIR = PROJECT_ROOT / "data"
VAULT_PATH = DATA_DIR / "vault.json"


def load_vault() -> dict | None:
    candidate_paths = [
        VAULT_PATH,
        PROJECT_ROOT / "vault.json",
        Path.cwd() / "data" / "vault.json",
        Path.cwd() / "vault.json",
    ]
    seen = set()
    for p in candidate_paths:
        try:
            resolved = p.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            if resolved.is_file():
                with open(resolved, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            continue
    return None


PROVIDERS = {
    "OpenRouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "models": [
            "nex-agi/nex-n2.5-pro:free",
            "nex-agi/nex-n2.5-mini:free",
            "inclusionai/ling-3.0-flash-vl:free",
            "qwen/qwen3.8-27b:free",
            "dots-studio/dots-3-note-preview:free",
        ],
        "default_model": "nex-agi/nex-n2.5-pro:free",
        "key_required": True,
        "key_placeholder": "sk-or-v1-…",
        "description": "Unified access to all models (free)",
        "icon": str(ICONS_DIR / "openrouter.svg"),
    },
    "OpenAI": {
        "base_url": "https://api.openai.com/v1",
        "models": [
            "gpt-5.6-luna",
            "gpt-4o-mini",
        ],
        "default_model": "gpt-5.6-luna",
        "key_required": True,
        "key_placeholder": "sk-…",
        "description": "OpenAI API (GPT-5.6, GPT-4o)",
        "icon": str(ICONS_DIR / "openai.svg"),
    },
    "Gemini": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "models": [
            "gemini-3.5-flash-lite",
            "gemini-3.8-flash",
        ],
        "default_model": "gemini-3.5-flash-lite",
        "key_required": True,
        "key_placeholder": "AIzaSy…",
        "description": "Google Gemini 3 (free tier available)",
        "icon": str(ICONS_DIR / "gemini.svg"),
    },
    "Anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "models": [
            "claude-haiku-4-5",
            "claude-sonnet-5",
            "claude-opus-5",
        ],
        "default_model": "claude-haiku-4-5",
        "key_required": True,
        "key_placeholder": "sk-ant-…",
        "description": "Anthropic Claude (Haiku, Sonnet, Opus)",
        "icon": str(ICONS_DIR / "claude.svg"),
    },
    "DeepSeek": {
        "base_url": "https://api.deepseek.com",
        "models": [
            "deepseek-flash",
        ],
        "default_model": "deepseek-flash",
        "key_required": True,
        "key_placeholder": "sk-…",
        "description": "DeepSeek v4.1 Flash",
        "icon": str(ICONS_DIR / "deepseek.svg"),
    },
    "Local": {
        "base_url": "http://localhost:8080/v1",
        "models": [
            "local-model",
        ],
        "default_model": "local-model",
        "key_required": False,
        "key_placeholder": "Optional (e.g. not-needed)",
        "description": "Local server (e.g. llama.cpp)",
        "icon": str(ICONS_DIR / "llama-cpp.svg"),
    },
}

DEFAULT_PROVIDER = "OpenRouter"
DEFAULT_MODEL = PROVIDERS[DEFAULT_PROVIDER]["default_model"]
BASE_URL = PROVIDERS[DEFAULT_PROVIDER]["base_url"]

REASONING_EFFORTS = ["default", "none", "minimal",
                     "low", "medium", "high", "xhigh", "max"]
DEFAULT_REASONING_EFFORT = "default"

BASE_SYSTEM_PROMPT = (
    "You are an autonomous computer-use agent. "
    "You operate the desktop by observing screenshots and calling mouse/keyboard tools.\n"
    "Grounding Rules:\n"
    "1. Screen coordinates are normalized: X and Y ranges from 0 to 1000 "
    "(top-left is [0, 0], bottom-right is [1000, 1000]).\n"
    "2. Look closely at the latest screenshot to verify if your previous action succeeded.\n"
    "3. Only perform one logical action at a time so you can inspect the visual feedback.\n"
    "4. When the goal is completed, call 'finish_task'."
)


def build_system_prompt(vault: dict | None = None) -> str:
    if vault is None:
        vault = load_vault()

    if not vault:
        return BASE_SYSTEM_PROMPT

    vault_json_str = json.dumps(vault, indent=2, ensure_ascii=False)
    return (
        f"{BASE_SYSTEM_PROMPT}\n\n"
        "User Profile & Vault Data:\n"
        "You have access to the user's verified personal profile and records provided below. "
        "When performing tasks on behalf of the user (such as filling out forms, applications, "
        "or entering user details), reference and use this information accurately whenever relevant "
        "(e.g., personal identity, BSN, address, contact details, medical conditions, "
        "functional limitations, requested provisions, etc.):\n"
        "```json\n"
        f"{vault_json_str}\n"
        "```"
    )


SYSTEM_PROMPT = build_system_prompt()

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
