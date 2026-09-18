# Cognita

**AI for Good — Hackathon 3: Equal Access**

- **SDG:** SDG 10 — Reduced Inequalities
- **SDG Target:** 10.2 — Promote inclusion irrespective of disability
- **Programming language:** Python
- **Team:** Arbër & Alex
- **Status:** Proof of Concept / Prototype in development

### Current AI stack

- **Computer-use AI:** Nex-N2.5-Pro through OpenRouter
- **Speech-to-text:** Whisper Large V3 Turbo Q5 (`large-v3-turbo-q5_0`) through whisper.cpp — planned / testing
- **Text-to-speech:** Deepgram Flux TTS (`deepgram/flux-tts:free`) through OpenRouter — planned / testing

> The project is still a proof of concept. Models and implementation choices may change during development if testing shows that another option works better.

---

## What is Cognita?

Cognita is an **AI-powered desktop assistant** that helps people interact with their computer using natural language instead of requiring precise mouse and keyboard actions.

Users can give Cognita instructions in two ways:

1. **Typed commands**
2. **Spoken commands**

For example:

```text
Open Notepad and type "My appointment is tomorrow at 10."
```

Cognita looks at the current screen, understands the goal, decides which actions are required, controls the mouse and keyboard and checks whether the task was completed.

The planned voice mode will also allow Cognita to speak back to the user using text-to-speech.

---

## 1. Problem Definition

Most computer interfaces still depend heavily on mouse and keyboard interaction.

This can create barriers for people with **physical or motor impairments**, for example people with:

- limited hand or arm movement;
- tremors;
- reduced fine-motor control;
- paralysis;
- conditions that make prolonged mouse or keyboard use difficult.

The **World Health Organization (WHO)** estimates that approximately **1.3 billion people**, or around **16% of the global population**, experience significant disability.

Digital accessibility problems are also still common. The **WebAIM Million 2026** study found automatically detectable WCAG failures on **95.9% of one million tested homepages**.

Cognita focuses on one specific problem:

> **Some users know exactly what they want to do on a computer, but physically operating the interface can be difficult.**

Cognita aims to reduce the amount of precise mouse and keyboard interaction required.

---

## 2. Target User

Our primary target group is:

> **People with physical or motor impairments who experience difficulty using a conventional mouse and/or keyboard.**

The user does not have to use voice.

Cognita supports both **typed and spoken instructions**, depending on what is most accessible for that user.

### Typed input

A user who can type but has difficulty navigating with a mouse could enter:

```text
Open Chrome and search for THUAS.
```

### Voice input

A user who has difficulty using both the mouse and keyboard could say:

```text
Open Chrome and search for THUAS.
```

Both methods eventually produce the same natural-language task for the computer-use AI.

---

### Who is not the target user?

Cognita is currently not intended to:

- diagnose or treat disabilities;
- replace professional assistive technology;
- operate safety-critical systems;
- perform important actions without user supervision.

Blind or low-vision users could potentially benefit from future voice and text-to-speech features, but they are **not the primary target group of the current prototype**.

Supporting these users properly would require additional accessibility features and testing.

---

## 3. SDG 10 — Reduced Inequalities

Cognita addresses **SDG 10: Reduced Inequalities**, especially **Target 10.2**, which promotes inclusion irrespective of characteristics including disability.

Giving everyone access to the same computer does not automatically mean everyone can interact with it equally.

Someone who has difficulty operating a mouse or keyboard may experience an additional barrier when using digital services.

Cognita provides an alternative interaction method:

```text
Typed command
      OR
Spoken command
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

Cognita has three main AI components.

### A. Computer-use AI

The main Cognita agent currently uses:

```text
Nex-N2.5-Pro
via OpenRouter
```

This AI receives:

- the user's task;
- screenshots of the current computer screen;
- available computer-control tools.

It then decides which action should happen next.

The current process is:

```text
User instruction
       ↓
Python
       ↓
Screenshot
       ↓
Nex-N2.5-Pro
       ↓
Understand screen + task
       ↓
Choose computer action
       ↓
PyAutoGUI
       ↓
Mouse / keyboard action
       ↓
New screenshot
       ↓
AI verifies result
       ↓
Repeat until completed
```

---

### B. Speech-to-text

For voice input, we currently plan to test:

```text
OpenAI Whisper Large V3 Turbo Q5
large-v3-turbo-q5_0
through whisper.cpp
```

Unlike our main computer-use model, Whisper will run **locally on the computer**.

The planned flow is:

```text
Microphone
    ↓
Local Whisper
    ↓
Speech-to-text
    ↓
"Open Notepad and type hello"
    ↓
Cognita computer agent
```

This means that the user's microphone recording does not need to be sent to an external speech-to-text API.

We selected the Q5 quantized version first because it is significantly smaller than the full model while still using the Large V3 Turbo architecture.

We will test its speed and transcription quality on our own hardware before deciding whether it remains the final model.

---

### C. Text-to-speech

For spoken feedback, we currently plan to test:

```text
Deepgram Flux TTS
deepgram/flux-tts:free
through OpenRouter
```

This can allow Cognita to speak short status messages back to the user.

For example:

```text
Cognita:
"Starting your task."
```

and after completion:

```text
Cognita:
"Done. Notepad is open and your message has been typed."
```

The detailed technical logs can still remain visible in the terminal.

TTS should only provide useful, short feedback instead of reading every technical action aloud.

---

## 5. Intended Final Flow

With all three components combined, Cognita could work like this:

```text
                    ┌── Typed command ──────────┐
                    │                           │
User ────────────────┤                           ├──→ Cognita task
                    │                           │
                    └── Voice command           │
                          ↓                     │
                    Local Whisper               │
                          ↓                     │
                    Speech-to-text ─────────────┘
                              ↓
                    Nex-N2.5-Pro
                              ↓
                    Screen understanding
                              ↓
                    Computer actions
                              ↓
                    Result verification
                              ↓
                    Task completed
                              ↓
                    Deepgram Flux TTS
                              ↓
                    Spoken confirmation
```

Typed input remains available even after voice input is added.

---

## 6. Why AI Is Necessary

A normal automation script could use fixed instructions such as:

```python
click(100, 200)
type("notepad")
press("enter")
```

But this only works when the interface always looks exactly the same.

Cognita needs to understand:

- what is currently visible;
- what the user wants;
- where applications and buttons are;
- whether an action succeeded;
- what action should happen next.

The AI can currently select tools such as:

```text
mouse_click
type_text
press_hotkey
wait
finish_task
```

Without the computer-use AI, Cognita would only be a fixed automation script.

---

## 7. Why the Solution Fits the Problem

The problem is:

> **A user has difficulty physically interacting with a computer interface.**

The solution is:

> **The user explains their goal using text or voice, and Cognita performs the required mouse and keyboard interaction.**

The user can choose whichever input method is more accessible.

For example:

```text
Typed:
"Open Notepad."
```

or:

```text
Spoken:
"Open Notepad."
```

Both produce the same task for Cognita.

The AI therefore performs the interaction that may be physically difficult for the intended user.

---

## 8. Working Prototype

The current prototype already works end-to-end using **typed natural-language input**.

### Currently implemented

- [x] Python application
- [x] Live AI API calls
- [x] Nex-N2.5-Pro through OpenRouter
- [x] Natural-language text input
- [x] Screenshot capture
- [x] AI vision input
- [x] AI function/tool calling
- [x] Mouse control
- [x] Keyboard control
- [x] Screen verification after actions
- [x] Maximum step limit
- [x] PyAutoGUI emergency failsafe
- [x] End-to-end computer-control test
- [ ] Local Whisper voice input
- [ ] Microphone recording
- [ ] Deepgram Flux TTS output
- [ ] Confirmation before sensitive actions
- [ ] Accessibility-focused final demo

---

### Technical test

During development we tested Cognita with:

```text
Please run League of Legends and click Play on the Riot Client so it opens the game itself.
```

Cognita successfully:

1. inspected the screen;
2. opened Windows Search;
3. searched for League of Legends;
4. opened the Riot Client;
5. located the Play button;
6. clicked Play;
7. waited for the program to start;
8. inspected the screen again;
9. confirmed that the requested task was complete.

The terminal returned:

```text
[DONE] Task Completed: Launched League of Legends from Windows,
clicked Play in the Riot Client, and confirmed the League of Legends
game client opened successfully.
```

This was **only a technical test**.

Gaming is not the purpose of Cognita.

The test demonstrates that the core:

```text
Observe → Reason → Act → Verify
```

loop works.

---

## 9. Planned Accessibility Demo

For the final demonstration we want to use a task that represents the intended user group.

### Typed example

```text
Open Notepad and type "My appointment is tomorrow at 10."
```

### Voice example

The user says:

```text
"Open Notepad and type my appointment is tomorrow at 10."
```

Whisper converts this to text locally.

Cognita then:

1. receives the task;
2. inspects the current screen;
3. opens Notepad;
4. enters the requested text;
5. checks whether the task succeeded.

Afterwards, Deepgram Flux TTS could say:

```text
"Done. Notepad is open and your message has been typed."
```

---

## 10. Edge Cases and Safety

AI can make mistakes, so Cognita should not blindly assume that an action succeeded.

| Problem | Cognita response |
|---|---|
| AI clicks the wrong location | Take another screenshot and reassess |
| Application is still loading | Wait and check again |
| AI becomes stuck | Stop after the maximum number of steps |
| Command is unclear | Ask the user to clarify |
| Whisper transcribes speech incorrectly | Confirm important commands before acting |
| AI cannot understand the screen | Stop instead of randomly clicking |
| Sensitive action is requested | Ask for user confirmation |
| User needs to stop the agent | Use the PyAutoGUI emergency failsafe |
| TTS fails | Keep the result available as normal text |

---

## 11. Ethical Reflection

The biggest risk is that Cognita could **misunderstand the user's request or perform the wrong computer action**.

For someone who depends on the tool to operate their computer, this could cause actions they did not intend.

Examples include:

- sending the wrong message;
- clicking the wrong option;
- closing important work;
- entering text in the wrong application.

The current prototype limits this risk by:

- taking screenshots after actions;
- checking whether actions succeeded;
- limiting the maximum number of steps;
- using the PyAutoGUI emergency failsafe.

For sensitive actions such as deleting files, sending messages or submitting forms, we plan to require explicit confirmation.

---

### Privacy

Cognita also has an important privacy risk.

The computer-use AI receives screenshots through an external API.

These screenshots could contain personal information.

During the hackathon demo we therefore use non-sensitive information.

A future version should capture only the necessary application or screen region.

For voice input, we currently plan to use **Whisper locally**. This means the microphone recording can be transcribed on-device instead of being uploaded to an external speech-to-text provider.

The transcription text can then be passed to Cognita.

---

### Different accessibility needs

Voice control is not accessible to everyone.

Some users may have both motor and speech impairments.

This is why Cognita supports **both text and voice input** rather than making voice mandatory.

We do not claim that Cognita solves digital accessibility for everyone.

---

## 12. Technology

### Currently used

- **Python**
- **OpenRouter API**
- **Nex-N2.5-Pro**
- **OpenAI-compatible Python client**
- **PyAutoGUI**
- **Pillow**
- **python-dotenv**

### Planned / currently being tested

- **whisper.cpp**
- **Whisper Large V3 Turbo Q5 (`large-v3-turbo-q5_0`)**
- **Microphone input**
- **Deepgram Flux TTS (`deepgram/flux-tts:free`)**
- **Text-to-speech feedback**

---

## 13. AI Model Overview

| Component | Model | Runs where? | Status |
|---|---|---|---|
| Computer control | Nex-N2.5-Pro | OpenRouter API | ✅ Working |
| Speech-to-text | Whisper Large V3 Turbo Q5 | Local / whisper.cpp | 🧪 Planned / testing |
| Text-to-speech | Deepgram Flux TTS | OpenRouter API | 🧪 Planned / testing |

The exact models may still change during development.

Any change will be based on practical testing such as:

- speed;
- accuracy;
- stability;
- hardware usage;
- accessibility;
- API availability.

---

## 14. How to Run

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

## 15. Current Limitations

Cognita is still a **proof of concept**.

Current limitations include:

- voice input is not integrated yet;
- Whisper Q5 still needs to be tested on our hardware;
- text-to-speech is not integrated yet;
- the AI can select an incorrect screen position;
- screenshots may contain private information;
- sensitive actions do not yet require confirmation;
- the main computer-use agent requires internet access;
- TTS requires internet access;
- the prototype has not yet been tested with real users from the target group.

Local Whisper speech-to-text will not require an internet connection after the required model and software have been installed.

---

## 16. Sources

Research and technical documentation used for the project:

- **World Health Organization (WHO)** — Disability and Health
- **WebAIM** — The WebAIM Million 2026
- **W3C Web Accessibility Initiative** — Speech Recognition and Physical Disabilities
- **United Nations** — SDG 10: Reduced Inequalities
- **whisper.cpp** — official model documentation
- **OpenAI Whisper** — Large V3 Turbo
- **OpenRouter** — Nex-N2.5-Pro and Deepgram Flux TTS

---

## 17. Rubric Checklist

| Criterion | Evidence |
|---|---|
| **K1 — AI Tool** | The live AI API is necessary for interpreting screenshots, understanding user requests and selecting computer actions |
| **K2 — SDG Relevance** | Cognita addresses a digital interaction barrier for people with physical or motor impairments under SDG 10.2 |
| **K3 — Scope** | The working prototype performs real end-to-end computer interaction rather than only demonstrating an API call |
| **1. Problem Definition — 2 pts** | A specific accessibility problem is described and supported with WHO, WebAIM and W3C evidence |
| **2. User Group — 2 pts** | Users with motor impairments, their needs and users outside the current scope are described |
| **3. Solution Description — 2 pts** | The full input → AI → computer action → verification flow is documented |
| **4. Problem–Solution Fit — 1 pt** | Cognita reduces the precise mouse/keyboard interaction that is difficult for the intended user |
| **5. Working Prototype — 1 pt** | The current text-controlled prototype already works end-to-end |
| **6. Ethical Reasoning — 2 pts** | Wrong actions, screenshot privacy and accessibility limitations are identified with concrete mitigations |

---

## 18. Next Steps

- [ ] Download and test Whisper Large V3 Turbo Q5
- [ ] Benchmark voice transcription speed
- [ ] Test Dutch and English voice commands
- [ ] Add microphone recording
- [ ] Connect Whisper transcription to the existing Cognita agent
- [ ] Add Deepgram Flux TTS
- [ ] Speak the final `finish_task` result through TTS
- [ ] Add confirmation before sensitive actions
- [ ] Create the final accessibility-focused demo
- [ ] Record the demo
- [ ] Test edge cases
- [ ] Add final team contributions

---

## Proof of Concept Status

The current prototype proves that the core computer-use system works:

```text
Natural-language task
        ↓
AI screen understanding
        ↓
Computer actions
        ↓
Verification
        ↓
Task completion
```

The next proof-of-concept stage adds:

```text
              Typed input
                   │
                   ├──────→ Cognita
                   │
Voice → Whisper ───┘
                       ↓
                 Computer task
                       ↓
                 Task completed
                       ↓
                     TTS
```

The final implementation may still change based on testing.

Our current planned AI stack is therefore:

```text
VOICE INPUT
Whisper Large V3 Turbo Q5
Local through whisper.cpp

          ↓

COMPUTER AGENT
Nex-N2.5-Pro
through OpenRouter

          ↓

VOICE OUTPUT
Deepgram Flux TTS
through OpenRouter
```
