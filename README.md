# Cognita

**AI for Good — Hackathon 3: Equal Access**

Cognita is an AI-powered Python desktop accessibility assistant designed to reduce the amount of precise mouse movement and repetitive keyboard interaction required to complete computer tasks.

Users can give Cognita a task by **typing or speaking**. Cognita can then observe the screen, reason about what is visible through a live multimodal LLM API, perform mouse and keyboard actions, observe the result again, and continue until the task is complete.

| | |
|---|---|
| **Hackathon** | AI for Good — Hackathon 3: Equal Access |
| **Assigned SDG** | SDG 10 — Reduced Inequalities |
| **Relevant SDG target** | Target 10.2 — inclusion irrespective of disability |
| **Primary users** | People with physical or motor impairments |
| **Language** | Python |
| **Team** | Arbër & Alex |
| **Status** | Completed Hackathon Prototype |
| **Main AI API** | OpenRouter API |
| **Computer-use model tested** | Nex AGI Nex-N2.5-Pro |
| **Speech-to-text** | Local Whisper Large V3 Turbo Q5 |
| **Text-to-speech API** | Deepgram Flux TTS through OpenRouter |

> **Core idea:** the user describes *what* they want to achieve. Cognita uses AI to determine *how* to interact with the current graphical interface.

[ZET HIER FOTO van de volledige Cognita-hoofdinterface met Task, microfoonknop, Run Agent, Agent Trace en What agent sees zichtbaar]

---

## 1. The Problem

Using a computer still often requires accurate mouse movement, clicking small interface elements, scrolling, keyboard shortcuts and repeated typing.

For people with **physical or motor impairments**, these interactions can create an additional barrier even when the person fully understands the task they want to complete.

Examples include people who experience:

- hand tremors;
- reduced fine-motor control;
- limited movement of the hands or arms;
- muscle weakness;
- paralysis;
- pain during repeated movement;
- fatigue from prolonged mouse or keyboard use.

The World Health Organization estimates that approximately **1.3 billion people — 16% of the global population, or about 1 in 6 people — experience significant disability**.

The W3C Web Accessibility Initiative explains that people with physical disabilities may have difficulty clicking small areas, may make more mistakes while typing or clicking, and may require alternative interaction methods such as speech recognition or other hands-free approaches.

Digital accessibility barriers also remain widespread. The **WebAIM Million 2026** analysis tested the home pages of one million websites and found:

- **95.9%** had automatically detected WCAG 2 failures;
- **56,114,377** distinct accessibility errors were detected;
- this equals an average of **56.1 detected errors per home page**;
- **51%** of home pages had missing form input labels;
- **30.6%** had empty buttons.

These automated results do **not** prove that 95.9% of websites are completely inaccessible. Automated testing detects only a subset of accessibility problems. They do, however, provide quantitative evidence that accessibility barriers remain common across digital interfaces.

### The specific inequality Cognita addresses

Cognita focuses on a specific interaction inequality:

> A user may know exactly what they want to accomplish on a computer, but a physical or motor impairment can make the mouse and keyboard interaction required to accomplish it significantly more difficult.

A multi-step form, for example, may require many small clicks, repeated text entry, scrolling and selections. The cognitive task may be straightforward while the physical interaction remains difficult.

Cognita attempts to reduce that physical interaction burden.

[ZET HIER FOTO van een voorbeeld van een taak met veel muis- en toetsenbordinteractie, bijvoorbeeld de lokale Wmo-oefenformulierpagina]

---

## 2. Intended User Group

### Primary user group

Cognita is primarily designed for:

> **People with physical or motor impairments who have difficulty with precise mouse interaction and/or repetitive keyboard input.**

This includes, for example, users with tremors, reduced dexterity, muscle weakness or limited movement of their hands or arms.

The user does not need to manually execute every individual mouse and keyboard action. Instead, the user can describe the desired outcome.

For example:

```text
Fill in this practice Wmo form using my saved information.
Stop on the confirmation page and do not submit it.
```

Cognita can then perform the repetitive interaction.

### Two input methods

Cognita supports both:

1. **Typed input** — the user types a natural-language task.
2. **Voice input** — the user records a spoken instruction, which is transcribed locally by Whisper and placed into the Task field.

The transcribed text is **not automatically executed**. It first appears in the Task field so that the user can review or edit the transcription before pressing **Run Agent**.

This is an important safety and accessibility choice: voice input reduces typing requirements without removing the user's opportunity to check what the system understood.

[ZET HIER FOTO van Cognita nadat een gesproken opdracht door Whisper in het Task-veld is gezet]

### Conditions of use

The current prototype assumes that:

- the user can express the intended task through text or speech;
- the user can understand the result of the requested task;
- a graphical desktop environment is available;
- an internet connection is available for the cloud AI services;
- the user supervises the agent while it controls the computer;
- the user can use the Stop function or PyAutoGUI emergency fail-safe if necessary.

### Who is not the primary intended user?

Cognita does **not** claim to be a complete accessibility solution for every disability.

The current prototype is not specifically designed for:

- blind or low-vision users who require a properly tested screen-reader-first workflow;
- users for whom speech input is inaccessible — typed input remains available as an alternative;
- users requiring medical diagnosis or treatment advice;
- unsupervised safety-critical computer systems;
- autonomous high-impact actions such as banking, legal submissions or deletion of important data without additional safeguards.

This scope is intentional. Our hackathon problem is specifically **motor-accessibility barriers in desktop interaction**, rather than accessibility in general.

---

## 3. SDG 10 — Reduced Inequalities

Cognita addresses the assigned **United Nations Sustainable Development Goal 10: Reduced Inequalities**.

More specifically, it relates to **Target 10.2**:

> “By 2030, empower and promote the social, economic and political inclusion of all, irrespective of age, sex, disability, race, ethnicity, origin, religion or economic or other status.”

Disability is therefore explicitly included in SDG Target 10.2.

### How Cognita connects to SDG 10.2

Digital participation increasingly affects access to information, communication and services.

However, access to a computer does not automatically mean equal ability to operate it. When a digital task requires precise pointer movement, repeated clicking or extensive typing, a person with a motor impairment can experience an additional interaction barrier.

Cognita attempts to reduce this inequality by allowing part of the physical interaction to be delegated to an AI agent.

```text
User intention
      ↓
Typed task OR spoken task
      ↓
Natural-language instruction
      ↓
AI observes the graphical interface
      ↓
AI decides which computer action is required
      ↓
Cognita performs the action
      ↓
AI observes the result again
      ↓
Task completed
```

Cognita does not claim to “solve disability”. Its contribution is narrower and measurable:

> **Reduce the amount of precise mouse and repetitive keyboard interaction needed to complete selected desktop tasks.**

That directly connects the technical solution to the inclusion objective of SDG 10.2.

[ZET HIER FOTO van SDG 10 Reduced Inequalities, bijvoorbeeld het officiële SDG 10-logo naast een screenshot van Cognita]

---

# 4. What We Built

Cognita is a **Python-native PyQt6 desktop application** that combines three AI components:

| Component | Technology | Local / API | Purpose |
|---|---|---|---|
| Computer-use reasoning | Nex-N2.5-Pro through OpenRouter | **Live API** | Understand screenshots, reason about the task and select computer-control tools |
| Speech-to-text | Whisper Large V3 Turbo Q5 through `pywhispercpp` / whisper.cpp | **Local** | Convert a spoken task into text |
| Text-to-speech | Deepgram Flux TTS through OpenRouter | **Live API** | Speak the completion summary |

The **live LLM API is the core required AI component**. Local Whisper is an additional accessibility input method, while TTS provides an additional output channel.

[ZET HIER FOTO van de Cognita Settings/API-configuratie waarop OpenRouter en het gebruikte Nex-N2.5-Pro model zichtbaar zijn]

---

# 5. Live AI API Integration

The hackathon requires a Python application that makes **real live AI API calls** and meaningfully uses the returned response.

Cognita does this during every agent run.

## Main API: OpenRouter

The final tested Cognita configuration uses the **OpenRouter API** from Python.

OpenRouter provides an OpenAI-compatible API. Cognita's Python code connects to:

```text
https://openrouter.ai/api/v1
```

The computer-use model used during our final development and testing was:

```text
nex-agi/nex-n2.5-pro:free
```

Nex-N2.5-Pro accepts text and image input and supports tool/function calling, which is necessary for Cognita's computer-use workflow.

### What Cognita sends to the API

During an agent step, Cognita sends information including:

- the user's natural-language task;
- the current screenshot;
- system instructions describing the agent's role;
- the available computer-control tools;
- context from previous actions and results;
- saved user data when required for the task.

### What the API returns

The model analyses the task and current screenshot and returns a decision about what should happen next.

Available tool actions include actions such as:

```text
mouse_click
click_and_type
mouse_scroll
type_text
press_hotkey
wait
finish_task
```

Python then validates and executes the requested action through the application's computer-control layer.

The model does **not** directly control the mouse. The flow is:

```text
Python
  ↓
OpenRouter API request
  ↓
Nex-N2.5-Pro
  ↓
Tool/function call
  ↓
Python receives tool call
  ↓
PyAutoGUI / device-control code executes action
```

After the action, Cognita takes another screenshot and makes a new AI request.

This creates the core:

> **Observe → Reason → Act → Observe Again → Verify**

loop.

[ZET HIER FOTO van Agent Trace waarop meerdere AI-stappen/tool calls zichtbaar zijn naast What agent sees]

---

## 5.1 Why the LLM API is necessary

The LLM is not an optional chatbot added to the application.

It performs the central reasoning step required for Cognita to work.

A traditional hard-coded automation might do this:

```python
click(300, 450)
type("Marloes")
press("tab")
```

This assumes that the same field will always be at coordinate `(300, 450)`.

That becomes unreliable when:

- a window moves;
- a page scrolls;
- a dialog appears;
- content changes;
- a website loads more slowly;
- a button changes position;
- a form contains different fields;
- the next required action depends on the current screen.

Cognita instead captures the **current** screen and asks the multimodal LLM to determine the next appropriate action.

Without the LLM API, Cognita would lose:

- visual interpretation of changing interfaces;
- natural-language task understanding;
- adaptive action selection;
- tool/function-call reasoning;
- the ability to reassess the interface after every action;
- the ability to determine when a task is complete.

Removing the AI would therefore fundamentally change the prototype into a fixed macro system.

This is why the AI integration is both **meaningful and necessary**.

---

# 6. Voice Input — Local Whisper

Voice input is fully integrated into the Cognita GUI.

This is particularly relevant to our target group because W3C identifies speech recognition as one of the approaches that can support people with physical disabilities who cannot comfortably use a conventional mouse or keyboard.

## Voice workflow

```text
User clicks microphone
        ↓
Microphone recording starts
        ↓
User speaks the task
        ↓
Recording stops
        ↓
Local Whisper transcription
        ↓
Text appears in Cognita Task field
        ↓
User reviews / edits transcription
        ↓
User presses Run Agent
        ↓
Normal Cognita AI-agent workflow starts
```

The current local model is:

```text
large-v3-turbo-q5_0
```

It runs through `pywhispercpp` / `whisper.cpp`.

The quantized model file is approximately **547 MiB**.

### Why we run speech-to-text locally

Raw microphone audio does not need to be uploaded to an external speech-to-text API.

This has two benefits for the prototype:

- no speech-to-text API quota is required;
- raw microphone recordings can remain on the user's machine.

However, after transcription, the resulting task text can still be included in the cloud LLM request when the agent is run.

### Voice input is optional

Cognita does **not** require speech.

This is important because voice-only interfaces can create a new accessibility barrier for people with speech disabilities or users in environments where speaking is impractical.

Users can choose between **typed and spoken input**.

[ZET HIER FOTO van de microfoonselectie in Cognita Settings]

[ZET HIER FOTO van de microfoonknop tijdens Recording/Transcribing en daarna de correcte transcriptie in het Task-veld]

---

# 7. Text-to-Speech Output

Cognita also supports spoken feedback after successful task completion.

The tested cloud TTS configuration uses:

```text
deepgram/flux-tts:free
```

through the **OpenRouter text-to-speech API**.

When the computer-use agent calls:

```text
finish_task
```

it produces a short completion summary.

If TTS is enabled, Cognita sends that summary to the TTS API and plays the returned speech.

The flow is:

```text
Agent completes task
        ↓
finish_task(summary)
        ↓
Cognita displays result
        ↓
Summary sent to OpenRouter TTS API
        ↓
Deepgram Flux generates speech
        ↓
Cognita plays spoken completion feedback
```

TTS is not responsible for the computer-control reasoning. It is an additional output channel.

[ZET HIER FOTO van de TTS-instellingen met Deepgram Flux/OpenRouter zichtbaar]

---

# 8. Complete End-to-End Architecture

Cognita supports two ways of starting the same computer-use workflow.

```text
                 ┌─────────────────────┐
                 │        USER         │
                 └──────────┬──────────┘
                            │
                 ┌──────────┴──────────┐
                 │                     │
             Typed task            Spoken task
                 │                     │
                 │              Microphone input
                 │                     │
                 │              Local Whisper STT
                 │                     │
                 └──────────┬──────────┘
                            │
                       Task field
                            │
                     User can review
                            │
                       Run Agent
                            │
                    Capture screenshot
                            │
                            ▼
                 ┌─────────────────────┐
                 │   OpenRouter API    │
                 │   Nex-N2.5-Pro      │
                 └──────────┬──────────┘
                            │
                   Screen understanding
                            +
                    Tool-call decision
                            │
                            ▼
                 Python executes action
                            │
              Mouse / keyboard / scroll
                            │
                            ▼
                    New screenshot
                            │
                            └──────► AI re-observes
                                      and continues
                                            │
                                      finish_task
                                            │
                            ┌───────────────┴───────────────┐
                            │                               │
                    Completion in GUI              Optional TTS API
                                                            │
                                                     Spoken summary
```

This means the working end-to-end flow is:

```text
Typed OR spoken input
        ↓
Natural-language task
        ↓
Live multimodal LLM API
        ↓
Tool call
        ↓
Real desktop action
        ↓
New screenshot
        ↓
Further AI reasoning
        ↓
finish_task
        ↓
Visual + optional spoken result
```

No manual code modification is required during this flow.

---

# 9. Meaningful Accessibility Scenario — Wmo Practice Form

To demonstrate Cognita on a realistic accessibility problem rather than only a simple technical test, the repository contains a local multi-step **Wmo practice application form**:

```text
demos/form1.html
```

The form provides a safe environment for testing tasks that normally require substantial mouse and keyboard interaction.

The practice workflow includes multiple stages such as:

1. personal details;
2. disability / functional-limitation information;
3. requested support;
4. confirmation.

Cognita also contains a **User Data** interface.

Information entered there can be stored locally and provided to the computer-use agent when required for a task.

For demonstration purposes, Cognita uses **synthetic example data rather than real personal or medical data**.

## Example accessibility task

```text
Fill in this practice Wmo form using my saved user data.
Stop on the confirmation page and do not submit it.
```

Instead of manually:

- clicking every form field;
- repeatedly entering personal information;
- selecting each option;
- scrolling;
- navigating between sections;

the user provides one high-level instruction and Cognita performs the interaction.

This is the meaningful user value of the prototype.

[ZET HIER FOTO van het lege lokale Wmo-oefenformulier vóórdat Cognita begint]

[ZET HIER FOTO van Cognita terwijl het Wmo-oefenformulier automatisch wordt ingevuld]

[ZET HIER FOTO van de ingevulde confirmation page waarop zichtbaar is dat Cognita vóór Submit is gestopt]

---

# 10. Problem–Solution Fit

The problem Cognita addresses is not a lack of understanding.

The intended user may understand the website or application perfectly but experience difficulty physically operating it.

Therefore, Cognita changes the level at which the user interacts with the computer.

Instead of:

```text
Move mouse
→ locate small field
→ click field
→ type text
→ move mouse
→ click next field
→ type text
→ scroll
→ select option
→ repeat
```

the user can say or type:

```text
Fill in this practice form using my saved information.
```

The AI performs the lower-level interaction.

### Why not just use a fixed macro?

A macro can repeat a known sequence.

Cognita needs to respond to the **current visual state** of the interface.

The next action can depend on:

- what is currently visible;
- whether a previous click worked;
- whether the interface has finished loading;
- where the window is positioned;
- whether scrolling changed the visible controls;
- whether an unexpected dialog appeared;
- whether the requested task has already been completed.

This makes an observe → reason → act → verify AI loop a better fit for the selected problem than fixed coordinates alone.

---

# 11. Working Prototype

The Hackathon 3 version of Cognita works end to end.

| Feature | Status |
|---|---|
| Python-native desktop application | Implemented |
| PyQt6 GUI | Implemented |
| Live LLM API calls | Implemented |
| OpenRouter API integration | Implemented |
| Multimodal screenshot input | Implemented |
| LLM tool/function calling | Implemented |
| Typed natural-language tasks | Implemented |
| Microphone input | Implemented |
| Local Whisper speech-to-text | Implemented |
| Voice transcription integrated into GUI | Implemented |
| User review before executing transcribed command | Implemented |
| Microphone selection | Implemented |
| Screenshot capture | Implemented |
| Mouse clicking | Implemented |
| Click-and-type actions | Implemented |
| Keyboard typing | Implemented |
| Keyboard shortcuts | Implemented |
| Mouse scrolling | Implemented |
| Wait action | Implemented |
| Re-observation after actions | Implemented |
| `finish_task` completion | Implemented |
| Visible Agent Trace | Implemented |
| Current-screen preview | Implemented |
| Stop button | Implemented |
| PyAutoGUI emergency fail-safe | Implemented |
| User Data / form-filling context | Implemented |
| TTS completion feedback | Implemented |
| Deepgram Flux TTS through OpenRouter | Implemented |
| Local/remote target-device support | Implemented / optional |

### Demonstrated end-to-end flows

#### Typed

```text
Typed command
→ API reasoning
→ screen analysis
→ tool calls
→ desktop actions
→ verification
→ finish_task
```

#### Voice

```text
Spoken command
→ local Whisper
→ transcription appears in Task field
→ user reviews it
→ Run Agent
→ API reasoning
→ screen analysis
→ tool calls
→ desktop actions
→ verification
→ finish_task
→ optional spoken completion
```

[ZET HIER FOTO van een succesvolle volledige voice-input run waarbij de opdracht, Agent Trace en eindresultaat tegelijk zichtbaar zijn]

---

# 12. Edge Cases and Bad AI Responses

Because Cognita controls a real computer, handling failures is an important part of the prototype.

A model can misunderstand the task, misread the screenshot, select the wrong coordinates or request an inappropriate action.

Cognita therefore includes multiple controls around the AI loop.

| Edge case | Current behaviour |
|---|---|
| User provides no task | The GUI prevents an empty agent run |
| API is not configured | User is directed to API configuration |
| Voice transcription is incorrect | Transcription is shown in the Task field before execution so the user can edit it |
| No microphone is selected | A system/default microphone can be used or another input can be selected |
| Voice input is unsuitable | User can use typed input instead |
| AI clicks the wrong location | A new screenshot is captured so the model can reassess the resulting screen |
| Page is still loading | Agent can use `wait` before observing again |
| Required element is outside viewport | Agent can use `mouse_scroll` and inspect the new screen |
| Tool execution fails | Error is logged and returned to the agent workflow |
| Screenshot capture fails | Run stops and reports the failure |
| Model returns no usable tool call | Cognita does not invent a local action |
| User sees unwanted behaviour | User can press STOP |
| Local mouse control must be stopped immediately | PyAutoGUI emergency fail-safe is available |
| Agent reaches successful completion | Model calls `finish_task` with a summary |
| TTS API fails | Core task result remains available visually; TTS is not required for task execution |

The most important design principle is:

> **The AI proposes actions, but Python remains responsible for executing the available tools.**

This creates a controlled boundary between model output and operating-system actions.

---

# 13. Ethical Reflection

## Main risk — incorrect autonomous actions

The largest project-specific risk is that Cognita can misunderstand the user's intention or misinterpret the screen and perform the wrong computer action.

For our intended user group, the consequences can be especially important.

A user who relies on Cognita because precise mouse or keyboard interaction is physically difficult may also have more difficulty quickly correcting an unwanted action manually.

A wrong action could, for example:

- enter incorrect information;
- click the wrong button;
- close unsaved work;
- send something unintentionally;
- submit a form too early;
- modify information the user did not intend to change.

### What we currently do to reduce this risk

Cognita already includes several safeguards:

- the user chooses when the agent starts;
- spoken instructions are transcribed into the Task field **before** execution;
- the user can review and edit a voice transcription;
- Cognita captures a new screenshot after actions so the AI can reassess the state;
- the Agent Trace makes the agent's actions visible;
- the GUI shows what the agent currently sees;
- the user can press **STOP**;
- PyAutoGUI provides an emergency fail-safe;
- the Wmo demonstration uses a local practice form;
- synthetic data is used for the demonstration;
- the demo instruction explicitly tells the agent to stop before final submission.

### What should be added before real high-impact use?

For use beyond a controlled prototype, we would add:

- mandatory confirmation immediately before irreversible or sensitive actions;
- a hard maximum action/step limit;
- application-level permissions restricting where the agent can act;
- allow/deny lists for dangerous actions;
- stronger validation before submitting forms;
- undo/recovery mechanisms where possible.

---

## Privacy risk

Cognita sends screenshots to a cloud LLM.

A screenshot can contain:

- names;
- addresses;
- emails;
- messages;
- account information;
- medical information;
- other private screen content.

The User Data functionality can also contain sensitive information.

Although local files such as `.env` and user-data JSON files should be excluded from Git, this does **not** mean that all information stays local: screenshots and relevant task context can still be transmitted to the selected cloud AI service during an agent run.

### Current privacy choices

- Whisper speech recognition runs locally;
- raw microphone audio does not need to be uploaded to an STT service;
- synthetic data is used in the hackathon demonstration;
- API keys and local user data should not be committed to Git.

### Further mitigation

Before using Cognita with real sensitive data, we would add:

- screenshot cropping;
- automatic redaction of unnecessary sensitive information;
- encryption for locally stored user data;
- clearer warnings about what is sent to external APIs;
- user-controlled application permissions;
- explicit confirmation before sharing sensitive context.

---

## Accessibility risk

Voice input improves accessibility for some users but can create a new barrier if it becomes mandatory.

People with speech disabilities may not be accurately recognised by speech-recognition software.

For that reason, Cognita supports **both voice and typed input** rather than replacing one with the other.

The prototype has also not yet been formally evaluated with a representative group of people with motor disabilities.

Therefore, we describe Cognita as an **accessibility-focused hackathon prototype**, not as clinically validated assistive technology.

---

# 14. User Data and Privacy

Cognita includes a User Data interface intended to reduce repeated entry of information during form-filling tasks.

The data can be made available to the agent as context when required.

For our hackathon demonstration, we use a fictional/synthetic profile.

[ZET HIER FOTO van het User Data-scherm met uitsluitend fictieve/synthetische voorbeeldgegevens]

Real medical, financial or identity data should not be used for the demonstration.

---

# 15. Main Technologies

Cognita is built primarily with:

- **Python**
- **PyQt6** — desktop GUI
- **OpenRouter API** — live cloud AI API
- **OpenAI-compatible Python client** — API communication
- **Nex-N2.5-Pro** — multimodal computer-use reasoning
- **PyAutoGUI** — local mouse and keyboard actions
- **Pillow** — screenshot/image handling
- **Whisper / whisper.cpp**
- **pywhispercpp** — local speech-to-text
- **sounddevice** — microphone recording
- **NumPy** — audio handling
- **Deepgram Flux TTS** — speech output
- **QSettings** — application configuration
- **Requests** — HTTP functionality

---

# 16. Relevant Source Files

| File | Responsibility |
|---|---|
| `src/main.py` | Application entry point |
| `src/main_window.py` | Main Cognita GUI, agent lifecycle and voice-input integration |
| `src/worker.py` | LLM agent loop, screenshots, API requests and tool-call processing |
| `src/config.py` | AI configuration, system instructions and tool definitions |
| `src/config_panel.py` | Application settings including microphone selection |
| `src/actions.py` | Computer-control actions |
| `src/device_bridge.py` | Local / optional remote target control |
| `src/api_setup_dialog.py` | API configuration |
| `src/vault_setup_dialog.py` | User Data configuration and synthetic example data |
| `src/whisper.py` | Local microphone recording and Whisper transcription |
| `src/tts.py` | Text-to-speech output |
| `src/tts_setup_dialog.py` | TTS configuration |
| `src/target_daemon.py` | Optional remote target-device service |
| `demos/form1.html` | Local Wmo accessibility demonstration form |

---

# 17. How to Run Cognita

## Requirements

- Python 3
- Windows is the primary tested desktop environment
- internet connection for cloud AI/TTS requests
- microphone if voice input is used
- an OpenRouter API key for the final tested configuration

## 1. Clone the repository

```bash
git clone https://github.com/alex24106429/Cognita.git
cd Cognita
```

## 2. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## 4. Start Cognita

```bash
python src/main.py
```

## 5. Configure the AI API

Open Cognita's API configuration and enter an OpenRouter API key.

The computer-use configuration tested during development used:

```text
Provider: OpenRouter
Model: nex-agi/nex-n2.5-pro:free
```

Free hosted model availability can change over time. Cognita's provider/model configuration allows a compatible multimodal model with tool-calling support to be configured when necessary.

[ZET HIER FOTO van het API Setup-scherm met OpenRouter geselecteerd en het computer-use model zichtbaar]

## 6. Configure voice input

Select a microphone in Cognita's settings.

Then:

1. click the microphone button;
2. speak the task;
3. stop recording;
4. wait for local transcription;
5. review the text in the Task field;
6. press **Run Agent**.

On first use, the local Whisper model may need to be downloaded.

The model used by Cognita is:

```text
large-v3-turbo-q5_0
```

## 7. Optional TTS

Enable Text-to-Speech in Cognita to hear the final task-completion summary.

Our tested TTS configuration uses:

```text
deepgram/flux-tts:free
```

through OpenRouter.

---

# 18. Hackathon Demo

## Recommended demo

Our primary hackathon demonstration is the local Wmo practice form because it directly demonstrates the accessibility problem Cognita is intended to address.

### Demo steps

1. Start Cognita.
2. Show the configured live OpenRouter API.
3. Open the local Wmo practice form.
4. Show the synthetic User Data profile.
5. Click Cognita's microphone.
6. Say:

```text
Fill in this practice Wmo form using my saved user data.
Stop on the confirmation page and do not submit it.
```

7. Show Whisper converting the spoken instruction into text.
8. Review the transcription.
9. Press **Run Agent**.
10. Show the Agent Trace while the live LLM API analyses screenshots and requests tool actions.
11. Show Cognita clicking, typing, selecting and scrolling.
12. Show the confirmation page.
13. Show that the agent stops before submission.
14. Show the `finish_task` result.
15. If TTS is enabled, demonstrate the spoken completion summary.

This demonstrates the entire product:

```text
Voice
→ local STT
→ user verification
→ live LLM API
→ visual reasoning
→ tool calls
→ real computer actions
→ repeated verification
→ task completion
→ spoken/visual feedback
```

[ZET HIER LINK naar de demo-video / screen recording van Cognita]

[ZET HIER FOTO van het eindresultaat van de hackathon-demo]

---

# 19. Current Limitations

Cognita is complete as our **Hackathon 3 prototype**, but it is not a production-ready autonomous accessibility product.

Current limitations include:

- LLMs can still select an incorrect action or screen location;
- cloud AI requires an internet connection;
- cloud-model availability and rate limits can change;
- screenshots sent to a cloud model may contain private information;
- the local User Data vault is not intended as production-grade secure storage;
- there is no complete permission system for sensitive actions;
- high-impact actions require stronger confirmation safeguards;
- speech recognition can make transcription errors;
- speech input is not accessible to every user;
- the prototype has not yet been formally usability-tested with a representative group of people with motor impairments;
- optional remote-device mode is intended for controlled testing.

These limitations do not remove the working functionality, but they define where further development and user testing are necessary.

---

# 20. Rubric Evidence

This section maps the delivered Cognita prototype directly to the Hackathon Assessment Rubric.

## Knockout Criteria

### K1 — AI Tool

**Met.**

Cognita makes live LLM API calls from Python during the core computer-use loop.

The model receives the user's goal, current screenshot and available tools. It performs a necessary step by interpreting the graphical interface and deciding which computer-control action should happen next.

Without this AI step, Cognita would no longer function as an adaptive natural-language computer-use agent.

**Evidence in repository/demo:**

- live OpenRouter API configuration;
- `src/worker.py`;
- screenshot input;
- model tool/function calls;
- Agent Trace;
- end-to-end demo.

---

### K2 — SDG Relevance

**Met.**

Cognita addresses a concrete issue within **SDG 10 — Reduced Inequalities**, specifically Target 10.2 and disability inclusion.

The specific inequality is the additional physical interaction burden experienced by people with motor impairments when digital tasks depend on precise mouse control and repetitive keyboard input.

The intended beneficiaries are explicitly defined as people with physical/motor impairments who experience these interaction difficulties.

---

### K3 — Scope

**Met.**

Cognita goes beyond an isolated API experiment.

The delivered prototype includes:

- a complete desktop GUI;
- typed input;
- voice input;
- local speech-to-text;
- live multimodal LLM reasoning;
- screenshots;
- tool/function calling;
- real mouse and keyboard control;
- scrolling;
- repeated visual verification;
- user-data assisted form filling;
- stop/fail-safe controls;
- completion detection;
- optional TTS;
- a realistic multi-step accessibility scenario.

This provides meaningful, non-trivial functionality for the intended use case.

---

# 21. Scored Rubric Criteria

## 1. Problem Definition — Fully Met Target (2/2)

The problem is specific:

- **What goes wrong?** Digital tasks can require precise mouse control and repetitive typing.
- **For whom?** People with physical/motor impairments.
- **Where?** Graphical computer interfaces, websites and multi-step forms.
- **When?** During tasks requiring repeated clicking, typing, selecting and scrolling.
- **How significant?** WHO, W3C and WebAIM evidence is provided with concrete numbers and examples.

---

## 2. User Group — Fully Met Target (2/2)

The primary user group is specifically defined as people with physical or motor impairments who experience difficulty with precise mouse and/or repetitive keyboard interaction.

Their needs, conditions of use and relevant limitations are described.

The README also explicitly states which users and use cases are outside the current scope.

---

## 3. Solution Description — Fully Met Target (2/2)

The complete input-to-output process is documented:

```text
Typed / voice input
→ local transcription when needed
→ task
→ screenshot
→ live LLM API
→ tool call
→ Python computer action
→ new screenshot
→ verification
→ finish_task
→ visual / spoken result
```

The exact role of the required live AI API is explicitly documented.

---

## 4. Problem–Solution Fit — Fully Met Target (1/1)

Cognita directly reduces the type of physical interaction identified in the problem.

The README also explains why a simpler fixed-coordinate macro cannot provide the same adaptive behaviour across changing graphical interfaces.

---

## 5. Working Prototype — Fully Met Target (1/1)

The prototype works from intended input to intended output.

Both typed and voice task input are implemented.

Voice input is transcribed locally and inserted into the GUI. The user can then start the agent, which makes live API requests, analyses screenshots, performs computer actions, re-observes the result and finishes the task.

No manual code modification is required during the demonstrated flow.

---

## 6. Ethical Reasoning — Fully Met Target (2/2)

The ethical reflection identifies risks that are specific to Cognita:

- incorrect autonomous actions;
- increased consequences for users who may have difficulty correcting actions manually;
- privacy exposure through screenshots;
- sensitive User Data;
- speech-recognition errors;
- accessibility problems created by relying only on voice.

For each major risk, the README explains:

1. the possible consequence;
2. safeguards already implemented;
3. further safeguards required before real high-impact use.

---

# 22. Sources

## Disability and SDG evidence

1. [World Health Organization — Disability](https://www.who.int/news-room/fact-sheets/detail/disability-and-health)  
   WHO estimates that 1.3 billion people, approximately 16% of the global population, experience significant disability.

2. [United Nations — Sustainable Development Goal 10](https://sdgs.un.org/goals/goal10)  
   Official SDG 10 targets, including Target 10.2 and inclusion irrespective of disability.

3. [W3C Web Accessibility Initiative — Physical disabilities and barriers](https://www.w3.org/WAI/people-use-web/abilities-barriers/physical/)  
   Describes physical/motor disabilities, difficulties with small click targets and alternative input methods.

4. [W3C Web Accessibility Initiative — Input: typing, writing and clicking](https://www.w3.org/WAI/people-use-web/tools-techniques/input/)  
   Describes alternative input methods, reduced movement, speech recognition and other hands-free interaction.

5. [W3C Web Accessibility Initiative — Speech Recognition](https://www.w3.org/WAI/perspective-videos/voice/)  
   Explains how speech recognition can support people with physical disabilities who cannot use a conventional keyboard or mouse.

6. [WebAIM — The WebAIM Million 2026](https://webaim.org/projects/million/)  
   Accessibility analysis of one million home pages, including detected WCAG failures and form/input accessibility errors.

## Technical sources

7. [OpenRouter — API Quickstart](https://openrouter.ai/docs/quickstart)  
   Documentation for OpenRouter's OpenAI-compatible live API.

8. [OpenRouter — Nex-N2.5-Pro](https://openrouter.ai/nex-agi/nex-n2.5-pro:free)  
   Model documentation including image input and tool-calling support.

9. [whisper.cpp — Available Models](https://github.com/ggml-org/whisper.cpp/blob/master/models/README.md)  
   Documentation for Whisper models including `large-v3-turbo-q5_0`.

10. [OpenRouter — Deepgram Flux TTS](https://openrouter.ai/deepgram/flux-tts:free)  
    Model information for the TTS model used by Cognita.

11. [OpenRouter — Text-to-Speech API](https://openrouter.ai/docs/guides/overview/multimodal/tts)  
    Documentation for generating speech through the OpenRouter API.

---

# 23. Final Hackathon Deliverables

The repository contains the completed Hackathon 3 product and documentation.

Before handing in the GitHub link, the portfolio should visibly contain:

- [x] Python-native working product
- [x] Live LLM API integration
- [x] Concrete SDG 10 inequality
- [x] Clearly defined intended user group
- [x] Typed input
- [x] Integrated voice input
- [x] Local Whisper speech-to-text
- [x] Real computer-control actions
- [x] AI response/tool handling
- [x] Edge-case handling
- [x] Ethical reflection
- [x] Quantitative evidence with authoritative sources
- [x] README with setup instructions
- [x] Realistic accessibility demo scenario
- [ ] Screenshots inserted at the marked locations in this README
- [ ] Demo screen recording linked in this README

---

# 24. Summary

Cognita demonstrates how a live multimodal LLM API can be used for more than generating text.

It combines:

```text
Natural-language interaction
        +
Computer vision
        +
LLM reasoning
        +
Tool/function calling
        +
Real computer actions
        +
Local speech recognition
        +
Spoken feedback
```

to address a specific accessibility problem for people with physical or motor impairments.

The project's connection to **SDG 10.2** is therefore not based only on the topic of disability. The functionality itself is designed around reducing an interaction barrier that can contribute to unequal digital participation.

> **Cognita turns a user's intention into computer actions, reducing the amount of precise physical interaction required to complete a desktop task.**
