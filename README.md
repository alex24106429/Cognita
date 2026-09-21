# Cognita

**AI for Good — Hackathon 3: Equal Access**

Cognita is a Python desktop assistant that uses a live LLM API, screenshots and computer-control tools to reduce the amount of precise mouse movement and repetitive keyboard input needed to complete desktop tasks.

| | |
|---|---|
| **Assigned SDG** | SDG 10 — Reduced Inequalities |
| **Relevant target** | SDG 10.2 — promote social, economic and political inclusion irrespective of disability |
| **Language** | Python |
| **Team** | Arbër & Alex |
| **Status** | Working prototype — typed-input computer-use flow implemented; voice input is still experimental |

> **Hackathon assessment configuration:** Cognita supports several LLM providers, but for the final Hackathon 3 demo we should use the **direct Anthropic Claude API**. Claude is explicitly listed in the assignment and is called live from our own Python code. Other providers are optional extensions and are not needed as evidence for the knockout criterion.

---

## 1. Problem Definition

Many computer tasks still require accurate mouse movement, clicking small interface elements and repeated typing. This can create a practical barrier for people with **physical or motor impairments**, including users with tremors, reduced fine-motor control, limited hand or arm movement, paralysis, or fatigue that makes prolonged mouse and keyboard use difficult.

This is not a small accessibility issue:

- The **World Health Organization (WHO)** estimates that more than **1.3 billion people**, around **16% of the global population**, live with significant disability.
- The **W3C Web Accessibility Initiative (WAI)** explains that people with physical disabilities may have difficulty clicking small targets, may make more typing or clicking errors, and may rely on alternative input methods such as speech recognition, switches or other hands-free interaction.
- The **WebAIM Million 2026** study detected WCAG 2 failures on **95.9% of one million tested home pages**. It also found missing form input labels on **51%** of the tested home pages. Automated testing cannot detect every accessibility problem, but these results show that accessibility barriers remain common in digital interfaces.

Cognita focuses on one specific part of this broader problem:

> **A person may understand exactly what they want to do on a computer, but precise mouse navigation and repetitive form entry can still be physically difficult.**

Instead of asking the user to manually perform every click and keystroke, Cognita lets the user describe the goal in natural language and lets the AI perform the interaction step by step.

### Context and example

A multi-step online form may require a user to click many small fields, enter the same personal information repeatedly, scroll through the page and select several options. For a user with hand tremors or severely limited fine-motor control, this can require substantially more effort than understanding the form itself.

For our hackathon demo, the repository contains a **local Wmo practice application form** (`demos/form1.html`) and a synthetic example user profile. This gives us a realistic but safe environment for demonstrating how Cognita can fill a complex form without using a real government service or real personal data.

---

## 2. Intended User Group

### Primary user

The current prototype is designed for:

> **People with physical or motor impairments who can provide a short typed natural-language instruction, but who have difficulty with precise mouse navigation and/or repetitive keyboard input.**

Examples include users who experience:

- hand tremors;
- reduced fine-motor control;
- limited hand or arm movement;
- muscle weakness;
- difficulty clicking small interface elements;
- fatigue from repetitive mouse and keyboard use.

The current workflow is especially relevant when the user can type a short instruction such as:

```text
Fill in this practice Wmo form using my saved user data. Stop before final submission.
```

Cognita can then perform the more repetitive interaction itself.

### Conditions of use

The current prototype assumes that:

- the user can understand and describe the task they want completed;
- the computer has a graphical desktop environment;
- an internet connection is available when a cloud LLM is used;
- the user supervises the agent and can stop it if necessary;
- real sensitive or safety-critical tasks are not performed without additional safeguards.

### Who is currently outside the main scope?

Cognita does **not** currently claim to fully support:

- users who cannot provide typed input at all, because speech-to-text is not yet integrated into the main application;
- blind or low-vision users who require a properly tested screen-reader-first workflow;
- users who need medical diagnosis or treatment advice;
- safety-critical computer systems;
- unsupervised high-impact actions such as financial transactions, legal submissions or deletion of important files.

A standalone Whisper experiment exists in `src/whisper.py`, but it is **not part of the end-to-end working prototype yet**. Future speech input could extend Cognita to users who cannot comfortably type even short commands.

---

## 3. SDG 10 — Reduced Inequalities

Cognita addresses **SDG 10: Reduced Inequalities**, especially **Target 10.2**.

The United Nations describes Target 10.2 as promoting the social, economic and political inclusion of all, irrespective of characteristics including **disability**.

Cognita connects to this target through digital participation. Access to a computer or website does not automatically mean equal ability to operate it. If a service depends on repeated clicking and typing, users with motor impairments can face an additional interaction barrier.

Cognita attempts to reduce that barrier by moving part of the physical interaction from the user to an AI-controlled agent:

```text
User goal
   ↓
Live LLM API
   ↓
Screen understanding
   ↓
Mouse / keyboard / scroll actions
   ↓
New screenshot
   ↓
Result verification
```

The goal is **not** to solve disability or replace professional assistive technology. The goal is narrower: reduce the amount of precise physical desktop interaction required for selected computer tasks.

---

## 4. What We Built

Cognita is a **PyQt6 desktop application** with an autonomous observe → reason → act → verify loop.

The current application includes:

- a graphical desktop interface;
- live LLM API configuration;
- screenshot capture;
- vision-capable LLM input;
- LLM function/tool calling;
- mouse clicking;
- combined click-and-type actions;
- keyboard typing;
- keyboard shortcuts;
- mouse scrolling;
- wait actions for loading interfaces;
- repeated screen inspection after actions;
- a visible execution log;
- a screenshot preview;
- a Stop button;
- the PyAutoGUI emergency fail-safe;
- a user-data vault for form-filling tasks;
- optional text-to-speech feedback after successful completion;
- optional local or remote target-device control.

### Main application flow

```text
1. User enters a natural-language goal
                    ↓
2. Cognita captures the current screen
                    ↓
3. Python sends the goal + screenshot + tool definitions to the LLM API
                    ↓
4. The LLM interprets the screen and selects a tool call
                    ↓
5. Cognita executes the requested mouse / keyboard / scroll action
                    ↓
6. Cognita captures a new screenshot
                    ↓
7. The LLM checks the new screen and decides what to do next
                    ↓
8. The loop repeats until the model calls finish_task or the run is stopped
                    ↓
9. Cognita shows the result and can optionally speak the completion summary
```

---

## 5. Where the Required AI API Is Used

The LLM API is a necessary part of Cognita's core functionality.

Each iteration sends the model:

- the user's task;
- the current screenshot;
- the system instructions;
- the available computer-control tool definitions;
- previous actions and results.

The model then decides which tool should be used next and supplies the arguments for that action.

Examples of available tools are:

```text
mouse_click
click_and_type
mouse_scroll
type_text
press_hotkey
wait
finish_task
```

The tool execution itself is performed by Python/PyAutoGUI. The LLM is responsible for **interpreting the changing screen, deciding what action is appropriate and determining when the requested task is complete**.

### Why Cognita would not work the same way without the LLM

A fixed automation could contain instructions such as:

```python
click(300, 450)
type("Marloes")
press("tab")
```

That approach only works if the interface always appears in exactly the same location and order.

Cognita instead re-observes the screen after actions. The LLM can adapt its next action to what is currently visible. Removing the LLM would remove the screen interpretation and adaptive decision-making that make Cognita a general computer-use assistant rather than a hard-coded macro.

---

## 6. Meaningful User Scenario: Accessible Form Filling

To connect the technical prototype to a realistic accessibility problem, we built a local multi-step **Wmo practice application form** in:

```text
demos/form1.html
```

The form contains multiple stages, including:

1. personal details;
2. disability and functional-limitation information;
3. requested support/provisions;
4. a confirmation screen.

Cognita also includes a **User Data** interface. The data entered there is stored locally in:

```text
data/vault.json
```

When an agent run begins, the saved user data is added to the agent context. This allows the agent to use the information while interacting with a form.

The repository includes a **synthetic example profile** for testing. It contains fictional identity, living-situation, medical and Wmo-related information so that the workflow can be demonstrated without using a real person's data.

### Recommended demo task

1. Open the local Wmo practice form in a browser.
2. In Cognita, load the synthetic example profile through **User Data**.
3. Enter:

```text
Fill in this practice Wmo form using my saved user data. Stop on the confirmation page and do not submit it.
```

4. Run the agent.
5. Show that Cognita reads the current screen, fills fields, selects options, scrolls when needed and re-checks the screen after actions.
6. Stop before the final submission action.

This scenario is more representative of Cognita's intended purpose than a generic application-launch test because it demonstrates a task where repeated mouse and keyboard interaction is directly relevant to the target user's accessibility needs.

---

## 7. Problem–Solution Fit

The problem is not that the intended user does not understand what a computer task means. The barrier we focus on is the **physical interaction required to carry it out**.

Cognita therefore lets the user express the goal at a higher level:

```text
"Fill in this practice form using my saved information."
```

instead of requiring the user to manually perform every individual action.

A simpler fixed macro is not enough for this use case because desktop interfaces can change due to:

- window position;
- screen resolution;
- different page content;
- loading delays;
- scrolling;
- changed button or field positions;
- unexpected dialogs.

Cognita observes the current state after each action and lets the LLM choose the next step from the new screenshot. This adaptive loop is the reason an LLM-based computer-use approach is relevant to the problem.

---

## 8. Working Prototype

### Implemented in the current application

| Feature | Status |
|---|---|
| Python desktop application | ✅ Working |
| PyQt6 graphical interface | ✅ Working |
| Live LLM API calls | ✅ Working |
| Typed natural-language tasks | ✅ Working |
| Screenshot capture | ✅ Working |
| Screenshot/vision input to the LLM | ✅ Working |
| LLM tool/function calling | ✅ Working |
| Mouse click | ✅ Working |
| Click + type | ✅ Working |
| Keyboard typing and hotkeys | ✅ Working |
| Mouse scrolling | ✅ Working |
| Re-observation after actions | ✅ Working |
| Completion through `finish_task` | ✅ Working |
| Visible logs and screenshot preview | ✅ Working |
| Stop button | ✅ Working |
| PyAutoGUI emergency fail-safe | ✅ Working |
| User-data vault | ✅ Working |
| Optional TTS after successful completion | ✅ Implemented |
| Remote target-device bridge | 🧪 Implemented / optional |
| Whisper speech-to-text | 🧪 Standalone experiment only |
| Voice input integrated into the GUI | ❌ Not yet |
| Per-action confirmation for sensitive actions | ❌ Not yet |

### End-to-end core

The working core can be demonstrated from input to output:

```text
Typed task
   ↓
Live LLM request with screenshot
   ↓
Tool call
   ↓
Real desktop action
   ↓
New screenshot
   ↓
Further tool calls if required
   ↓
finish_task
   ↓
Completion summary (+ optional TTS)
```

No manual code changes are required during this flow.

---

## 9. User Safety and Edge Cases

Cognita interacts with a real computer, so a bad model decision can have real consequences.

The current prototype handles several failure situations explicitly:

| Situation | Current behaviour |
|---|---|
| No task entered | GUI blocks the run and asks for a task |
| API not configured | GUI opens the API setup flow |
| User starts an agent run | Cognita asks for confirmation before taking control |
| Screen capture fails | Run stops and reports the error |
| Tool execution fails | Error is logged and returned to the agent loop |
| Interface is still loading | Agent can use the `wait` tool and inspect the screen again |
| Agent needs lower/higher page content | Agent can use `mouse_scroll` |
| User wants to stop | Stop button requests an abort |
| Emergency stop | PyAutoGUI fail-safe can abort local mouse control |
| Model returns no tool call | Run ends instead of inventing a local action |

Cognita currently has **no hard maximum-step limit**. This is a limitation of the current version and should be reconsidered before the system is used outside controlled demonstrations.

---

## 10. Ethical Reflection

The biggest risk is that Cognita can **misinterpret the user's intention or the screen and perform the wrong computer action**.

For the intended user, that risk can be especially important. A person who relies on Cognita because precise mouse or keyboard interaction is difficult may also find it harder to quickly correct an unintended click. On a real website, a wrong action could enter incorrect information, close work, send a message, submit a form or trigger another action the user did not intend.

Several safeguards are already present in the prototype:

- Cognita asks for confirmation before an agent run takes control of the computer;
- each action is followed by another screenshot so the model can reassess the result;
- the interface shows the action log and current screenshot;
- the user can press **STOP**;
- local control uses the PyAutoGUI corner fail-safe;
- our accessibility demo uses a **local practice form and synthetic data**, not a real government submission.

A second major risk is **privacy**. Screenshots sent to a cloud LLM may contain personal information, and the optional user-data vault can contain highly sensitive identity or medical information. The repository therefore excludes `.env` and `data/*.json` from Git, but that does **not** prevent information from being sent to the selected cloud model during an agent run.

Before Cognita should be used with real sensitive data, we would add:

- explicit confirmation immediately before sensitive actions such as submitting a form, sending a message, deleting a file or making a payment;
- screenshot cropping/redaction so irrelevant private information is not sent to the model;
- stronger protection or encryption for locally stored user data;
- a hard action/step limit to prevent runaway loops;
- clearer permissions describing which applications or actions the agent may use;
- testing with people from the intended user group instead of assuming that our interface is accessible to them.

Cognita is therefore presented as an accessibility-focused prototype, **not** as a replacement for professional assistive technology and not as a safe autonomous agent for high-impact tasks.

---

## 11. Technology and Repository Structure

### Main technologies

- Python
- PyQt6
- live LLM APIs
- OpenAI-compatible Python client
- direct Anthropic Messages API support
- PyAutoGUI
- Pillow
- Requests
- QSettings
- optional text-to-speech engines

### Relevant files

| File | Purpose |
|---|---|
| `src/main.py` | Application entry point |
| `src/main_window.py` | Main GUI, start/stop controls and agent lifecycle |
| `src/worker.py` | LLM loop, screenshots, API calls and tool-call handling |
| `src/config.py` | Provider definitions, system prompt and tool schemas |
| `src/actions.py` | Mouse, keyboard, scroll, wait and finish actions |
| `src/device_bridge.py` | Local and optional remote device control |
| `src/api_setup_dialog.py` | LLM provider/API setup and connection verification |
| `src/vault_setup_dialog.py` | User-data form and synthetic example profile |
| `src/tts.py` | Optional text-to-speech output |
| `src/tts_setup_dialog.py` | TTS configuration and testing |
| `src/whisper.py` | Experimental standalone Whisper transcription script |
| `src/target_daemon.py` | Optional HTTP service for controlling a remote target device |
| `demos/form1.html` | Local Wmo accessibility demo form |

### Supported LLM providers in the code

The current code contains provider configurations for:

- Anthropic;
- OpenAI;
- Gemini;
- OpenRouter;
- DeepSeek;
- a local OpenAI-compatible endpoint.

For **Hackathon 3 assessment evidence**, use the direct **Anthropic Claude API** so the required AI tool is clear and demonstrable.

---

## 12. Optional Text-to-Speech

After a successful `finish_task`, Cognita can speak the completion summary if TTS is enabled.

The current code supports:

- **Supertonic-3** locally;
- **Deepgram Flux** through OpenRouter;
- **OpenAI TTS**;
- **ElevenLabs**.

TTS is an additional feedback channel. It is **not required for the core computer-use loop** and should not be confused with speech input.

---

## 13. Experimental Speech-to-Text

`src/whisper.py` currently contains an experiment using `pywhispercpp` and the `large-v3-turbo-q5_0` model to transcribe an `audio.wav` file.

This is **not yet connected** to the Cognita GUI or agent flow. Therefore voice input is not used as evidence for the current working-prototype criterion.

The future flow would be:

```text
Microphone
   ↓
Local Whisper
   ↓
Transcribed task
   ↓
Existing Cognita computer-use loop
```

Running Whisper locally could reduce the need to upload raw microphone audio to an external speech-to-text service, although the resulting task text and screenshots may still be sent to the selected LLM provider.

---

## 14. How to Run

### 1. Clone the repository

```bash
git clone https://github.com/alex24106429/Cognita.git
cd Cognita
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install the core dependencies

```bash
pip install -r requirements.txt
```

### 4. Start Cognita

```bash
python src/main.py
```

### 5. Configure the LLM API

On first launch, Cognita opens the API setup dialog.

For the final hackathon assessment:

1. select **Anthropic**;
2. enter a valid Claude API key;
3. verify the connection;
4. select the Claude model used for the demo;
5. save the configuration.

The main agent credentials are configured through the application UI.

### 6. Run a task

Enter a task such as:

```text
Open Notepad and type: Cognita accessibility demo.
```

or use the Wmo practice-form demo described above.

Cognita asks for confirmation before taking control of the mouse and keyboard.

---

## 15. Optional Remote Target Mode

The code also contains a `RemoteDeviceBridge` and `src/target_daemon.py` so the Cognita UI can request screenshots and tool execution from another device over HTTP.

This is an optional extension, not required for the hackathon demo.

To use it, the target device also needs the FastAPI/ASGI dependencies used by `target_daemon.py`, for example:

```bash
pip install fastapi uvicorn pydantic
```

Then start the target daemon, preferably with an authentication token:

```bash
python src/target_daemon.py --host 0.0.0.0 --port 8765 --token YOUR_TOKEN
```

> The current remote bridge uses plain HTTP. It should only be used on a trusted test network. Encryption and stronger authentication would be required before real-world deployment.

---

## 16. Current Limitations

- speech-to-text is not integrated into the main GUI;
- the current user must still be able to enter a short typed task;
- LLMs can choose an incorrect screen location or action;
- there is currently no hard maximum-step limit;
- there is no per-action confirmation system for sensitive actions yet;
- screenshots sent to a cloud model may contain private information;
- user-vault data can be sensitive and is not encrypted at rest;
- the prototype has not yet been validated with real users from the intended target group;
- remote target mode uses HTTP and is intended only for controlled testing;
- behaviour can vary between LLM providers and models.

---

## 17. Evidence Against the Hackathon Rubric

### Knockout criteria

| Criterion | Evidence in Cognita |
|---|---|
| **K1 — AI tool** | The Python application makes live LLM API calls. The model receives screenshots and tool definitions and must choose the next computer action. For the final assessment we use the direct Anthropic Claude API. Without the LLM, the adaptive screen-understanding and action-selection loop would not work. |
| **K2 — SDG relevance** | Cognita addresses a specific digital-interaction inequality for people with physical or motor impairments under SDG 10.2. It reduces the need for precise mouse navigation and repetitive typing. |
| **K3 — Scope** | Cognita is not only an API test. It has a GUI, real mouse/keyboard/scroll control, repeated visual verification, a user-data vault, safety controls, optional TTS and a realistic multi-step Wmo practice-form scenario. |

### Scored criteria — target: full score

| Criterion | Evidence for the fully-met description |
|---|---|
| **1. Problem definition — 2/2** | The README defines what goes wrong, who experiences the barrier, the computer/form context in which it occurs, and supports significance with WHO, W3C and WebAIM evidence. |
| **2. User group — 2/2** | The current target group is narrowly defined as people with motor impairments who can give a short typed instruction but struggle with precise or repetitive desktop input. Conditions of use and excluded users are stated explicitly. |
| **3. Solution description — 2/2** | The README documents the input → screenshot → live LLM API → tool call → desktop action → new screenshot → verification → output flow, and maps the important source files. |
| **4. Problem–solution fit — 1/1** | The solution directly transfers repetitive physical interaction from the user to an adaptive agent. The README also explains why fixed coordinate macros do not provide the same adaptability. |
| **5. Working prototype — 1/1** | The typed-input core works end to end: task input, live API reasoning, screenshot analysis, real tool execution, repeated verification and `finish_task` completion. Experimental voice input is not presented as working evidence. |
| **6. Ethical reasoning — 2/2** | The reflection identifies project-specific risks, explains consequences for motor-impaired users, documents safeguards already implemented, and lists concrete next mitigations for sensitive actions and privacy. |

---

## 18. Sources

1. **World Health Organization — Disability and Health**  
   https://www.who.int/news-room/fact-sheets/detail/disability-and-health

2. **W3C Web Accessibility Initiative — Physical disabilities and barriers**  
   https://www.w3.org/WAI/people-use-web/abilities-barriers/physical/

3. **W3C Web Accessibility Initiative — Input: typing, writing and clicking**  
   https://www.w3.org/WAI/people-use-web/tools-techniques/input/

4. **WebAIM — The WebAIM Million 2026**  
   https://webaim.org/projects/million/

5. **United Nations — Sustainable Development Goal 10**  
   https://sdgs.un.org/goals/goal10

---

## 19. Before Final Submission

Before submitting the repository, we still need to make sure that what is documented is also demonstrated:

- [ ] run the final demo with the direct Anthropic Claude API;
- [ ] record a short screen capture of the working input → action → output flow;
- [ ] include or link that recording in the GitHub submission;
- [ ] use the Wmo practice form rather than a gaming example as the main accessibility demo;
- [ ] use only synthetic/non-sensitive data in the recording;
- [ ] stop before any real high-impact submission;
- [ ] make sure both team members can explain the observe → reason → act → verify loop and the ethical risks.

