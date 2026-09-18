# Cognita

**AI for Good — Hackathon 3: Equal Access**

- **SDG:** SDG 10 — Reduced Inequalities
- **SDG Target:** 10.2 — Promote inclusion irrespective of disability
- **Programming language:** Python
- **AI:** 
- **Team:** Arbër & Alex

---

## What is Cognita?

Cognita is an AI-powered desktop assistant that helps people interact with their computer using **natural language instead of precise mouse and keyboard actions**.

Users can give Cognita a command by **typing or speaking**.

For example:

```text
Open Notepad and type "My appointment is tomorrow at 10."
```

Cognita looks at the screen, decides what actions are needed, controls the mouse and keyboard and checks whether the task was completed.

Voice input and text-to-speech can make the same system usable with very little physical interaction.

---

## 1. Problem Definition

Most computer interfaces still depend heavily on mouse and keyboard interaction.

This can create barriers for people with **physical or motor impairments**, for example people with:

- limited hand or arm movement;
- tremors;
- reduced fine-motor control;
- paralysis;
- conditions that make prolonged mouse use difficult.

The World Health Organization estimates that around **1.3 billion people**, or **16% of the global population**, experience significant disability.

Digital accessibility problems are also still common. The **WebAIM Million 2026** study found automatically detectable WCAG failures on **95.9% of one million tested homepages**.

Cognita focuses on one specific problem:

> **Some users know what they want to do on a computer, but physically operating the interface can be difficult.**

Cognita tries to reduce the amount of precise mouse and keyboard interaction required.

---

## 2. Target User

Our primary target group is:

> **People with physical or motor impairments who experience difficulty using a conventional mouse and/or keyboard.**

Cognita supports two ways to give instructions:

### Typed input

A user who can type but has difficulty navigating with a mouse can enter:

```text
Open Chrome and search for THUAS.
```

### Voice input

A user who has difficulty using both mouse and keyboard can say:

```text
Open Chrome and search for THUAS.
```

Both inputs are converted into the same natural-language task for the AI.

### Who is not the target user?

Cognita is currently not intended to:

- diagnose or treat disabilities;
- replace professional assistive technology;
- operate safety-critical systems;
- perform important actions completely without user supervision.

Blind or low-vision users could potentially benefit from future voice and text-to-speech features, but they are not the main target group of the current prototype.

---

## 3. SDG 10 — Reduced Inequalities

Cognita addresses **SDG 10: Reduced Inequalities**, especially **Target 10.2**, which promotes inclusion irrespective of characteristics including disability.

Giving everyone access to the same computer does not automatically mean everyone can interact with it equally.

Cognita provides an alternative interaction method:

```text
Typed command OR spoken command
              ↓
              AI
              ↓
     Screen understanding
              ↓
       Computer action
```

The goal is to reduce one digital accessibility barrier for people with motor impairments.

---

## 4. How Cognita Works

The current system follows this process:

```text
User types or speaks a task
        ↓
Python receives the command
        ↓
Screenshot of the screen
        ↓
AI API
        ↓
AI understands the screen and task
        ↓
AI selects an action
        ↓
PyAutoGUI controls mouse/keyboard
        ↓
New screenshot
        ↓
AI checks the result
        ↓
Repeat until finished
```

The AI can currently use tools such as:

- `mouse_click`
- `type_text`
- `press_hotkey`
- `wait`
- `finish_task`

---

## 5. Why AI Is Necessary

A normal automation script could use fixed instructions such as:

```python
click(100, 200)
type("notepad")
press("enter")
```

But this only works when the interface is always exactly the same.

Cognita uses AI because it needs to understand:

- what is currently visible;
- what the user wants;
- where buttons and applications are;
- whether an action succeeded;
- what action should happen next.

Without the AI, Cognita would only be a fixed automation script.

---

## 6. Why the Solution Fits the Problem

The problem is:

> A user has difficulty physically interacting with a computer interface.

The solution is:

> The user explains the goal using text or voice, and Cognita performs the mouse and keyboard interaction.

This means the AI is not added only because the hackathon requires AI.

The AI performs the exact interaction that can be difficult for the intended user.

---

## 7. Working Prototype

The current prototype already works end-to-end.

It can:

- [x] accept natural-language text input;
- [x] make live AI API calls;
- [x] capture screenshots;
- [x] let the AI visually interpret the screen;
- [x] receive AI tool calls;
- [x] control the mouse;
- [x] control the keyboard;
- [x] check the screen after actions;
- [x] stop when a task is complete;
- [x] stop after a maximum number of steps;
- [x] use the PyAutoGUI emergency failsafe;
- [ ] accept microphone input;
- [ ] give text-to-speech feedback;
- [ ] request confirmation for sensitive actions.

### Technical test

During development we tested Cognita with:

```text
Open League of Legends and click Play.
```

Cognita successfully opened Windows Search, found League of Legends, opened the Riot Client, clicked Play and confirmed that the game opened.

This was only a **technical test** of the AI computer-control loop.

The final demonstration will use an accessibility-focused scenario.

---

## 8. Planned Demo

### Typed example

```text
User:
Open Notepad and type "My appointment is tomorrow at 10."
```

### Voice example

```text
User says:
"Open Notepad and type my appointment is tomorrow at 10."
```

Cognita should then:

1. understand the request;
2. inspect the screen;
3. open Notepad;
4. enter the text;
5. verify the result;
6. confirm that the task is complete.

With text-to-speech enabled:

```text
Cognita:
"Notepad is open and your message has been typed."
```

---

## 9. Edge Cases and Safety

AI can make mistakes, so Cognita must not blindly assume that every action succeeds.

| Problem | Response |
|---|---|
| AI clicks the wrong location | Take a new screenshot and reassess |
| Application is still loading | Wait and check again |
| AI becomes stuck | Stop after the maximum number of steps |
| Command is unclear | Ask the user for clarification |
| Voice recognition is uncertain | Confirm what the system understood |
| AI cannot understand the screen | Stop instead of randomly clicking |
| Sensitive action | Ask the user for confirmation |
| User needs to stop the agent | PyAutoGUI emergency failsafe |

---

## 10. Ethical Reflection

The biggest risk is that Cognita could **misunderstand the user's request or click the wrong element**.

For someone who depends on the tool to operate their computer, this could cause actions they did not intend, such as sending the wrong message or closing something important.

The current prototype limits this risk by:

- taking a new screenshot after actions;
- checking whether actions succeeded;
- limiting the maximum number of steps;
- using the PyAutoGUI emergency failsafe.

For sensitive actions such as deleting files, sending messages or submitting forms, we plan to require explicit user confirmation.

Another important risk is **privacy**. Cognita sends screenshots to an external AI service. Screenshots may contain personal information. During the demo we therefore use non-sensitive information. A future version should capture only the necessary window or part of the screen.

Voice control also creates an accessibility limitation of its own: not everyone can reliably use speech. This is why Cognita supports **both typed and spoken input** instead of depending completely on voice.

---

## 11. Technology

Cognita currently uses:

- Python
- OpenRouter API
- Nex-N2.5-Pro
- OpenAI-compatible Python client
- PyAutoGUI
- Pillow
- python-dotenv

Planned additions:

- speech-to-text;
- text-to-speech.

---

## 12. How to Run

Clone the repository:

```bash
git clone https://github.com/alex24106429/Cognita.git
cd Cognita
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
OPENAI_API_KEY=your_openrouter_api_key
```

> Never upload the real `.env` file or API key to GitHub.

Run Cognita:

```bash
python main.py
```

The current version asks:

```text
Enter the task for the computer agent:
```

Example:

```text
Open Notepad and type hello.
```

---

## 13. Current Limitations

- Voice input is not implemented yet.
- Text-to-speech is not implemented yet.
- AI can still select the wrong screen position.
- Screenshots may contain private information.
- Sensitive actions do not yet require confirmation.
- Internet and API access are required.
- The prototype has not yet been tested with real users from the target group.

Cognita is currently a **hackathon prototype**, not production-ready assistive technology.

---

## 14. Sources

- **World Health Organization (WHO)** — Disability and Health
- **WebAIM** — The WebAIM Million 2026
- **W3C Web Accessibility Initiative** — Speech Recognition and Physical Disabilities
- **United Nations** — SDG 10: Reduced Inequalities

---

## 15. Rubric Checklist

| Criterion | Evidence |
|---|---|
| **K1 — AI Tool** | AI understands screenshots and natural-language requests and decides which computer action to perform |
| **K2 — SDG Relevance** | Cognita addresses a digital accessibility barrier related to disability and SDG 10.2 |
| **K3 — Scope** | Working computer-use agent with a concrete accessibility use case |
| **1. Problem Definition — 2 pts** | Specific problem supported by WHO, WebAIM and W3C evidence |
| **2. User Group — 2 pts** | Specific users with motor impairments, their needs and excluded users are described |
| **3. Solution Description — 2 pts** | Complete input → AI → action → verification flow is documented |
| **4. Problem–Solution Fit — 1 pt** | AI performs mouse/keyboard interactions that can be difficult for the intended user |
| **5. Working Prototype — 1 pt** | Existing prototype works end-to-end |
| **6. Ethical Reasoning — 2 pts** | Wrong actions, privacy and voice-accessibility risks are identified with mitigations |

---

## 16. Next Steps

- [ ] Add microphone input
- [ ] Add text-to-speech
- [ ] Add confirmation before sensitive actions
- [ ] Create the final accessibility demo
- [ ] Record the demo
- [ ] Test edge cases
- [ ] Add final team contributions
