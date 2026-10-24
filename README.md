# Saarthi AI — Your Voice. Your Computer. Your Agent.

**A multilingual, voice-controlled AI desktop agent powered by Sarvam AI.**

> Speak naturally. Watch your computer take action. Stay in control.

Saarthi AI transforms natural-language commands into real desktop and browser actions. Activate it with a global hotkey, speak in English, Hindi, or Hinglish, and let the agent interpret your intent, plan a workflow, operate applications, and report the result.

Unlike traditional voice assistants that primarily answer questions, Saarthi is designed to **execute multi-step tasks on your computer**, with visible actions and explicit approval for consequential operations.

Built for the Sarvam AI hackathon.

---

## The Problem

Everyday computer tasks require constant manual interaction: opening applications, finding files, switching browser tabs, navigating portals, and filling out forms.

Traditional voice assistants can answer questions, but completing a real workflow often still requires the user to perform every step.

**What if you could tell your computer what you need instead of explaining how to do it?**

Saarthi bridges the gap between conversational AI and desktop automation.

## What Makes Saarthi Different?

<details>
<summary><strong>01. Voice-to-Action, Not Just Voice-to-Text</strong></summary>

Press `Ctrl + Space`, speak naturally, and turn your intent into a sequence of desktop and browser actions. The goal is task completion, not another conversational response.

</details>

<details>
<summary><strong>02. Built Around Sarvam AI</strong></summary>

The system uses Sarvam's speech recognition, language-model reasoning, and speech generation capabilities to create a multilingual voice interaction loop.

- **Saaras:** Speech-to-text.
- **Sarvam 105B:** Intent understanding and structured task planning.
- **Bulbul:** Text-to-speech responses.

</details>

<details>
<summary><strong>03. Real Browser Automation</strong></summary>

Using Playwright, Saarthi can navigate websites, interact with page elements, and automate supported Google Classroom workflows, including locating assignments and preparing file attachments.

A persistent Chromium profile allows users to maintain their own authenticated browser session.

</details>

<details>
<summary><strong>04. Native Desktop Control</strong></summary>

Open supported Windows applications, access Downloads, and locate relevant files without manually navigating through folders.

</details>

<details>
<summary><strong>05. Plan → Act → Verify</strong></summary>

Saarthi is designed to go beyond issuing clicks. Important actions should be verified against the resulting application state, helping distinguish successful execution from an attempted action.

</details>

<details>
<summary><strong>06. Human-in-the-Loop Safety</strong></summary>

Consequential operations, such as final assignment submission, require explicit approval. The user remains in control of actions that can have lasting effects.

</details>

---

## Powered by Sarvam AI

| Component | Role |
|---|---|
| Saaras | Recognizes spoken commands |
| Sarvam 105B | Interprets intent and plans tool-based actions |
| Bulbul | Converts responses into spoken feedback |

Saarthi combines these capabilities into one workflow:

**Listen → Understand → Plan → Act → Verify → Respond**

The application also uses Python for orchestration, Playwright for browser automation, and controlled Windows utilities for desktop operations.

> Model availability, identifiers, and API configurations depend on the current Sarvam API documentation and account access.

## The Judge Demo: From Voice to Real Action

The recommended demonstration follows one coherent workflow rather than showcasing disconnected features.

### Demo 1 — Control the Desktop

Start Saarthi and press `Ctrl + Space`.

Say:

> "Open my Downloads folder and find my latest PDF."

**What to observe:**
- Voice input is captured.
- Saaras transcribes the command.
- The agent identifies the requested operation.
- Windows Explorer opens.
- The relevant file is located and its path is reported.
- Bulbul speaks the result when TTS is enabled.

### Demo 2 — Automate Google Classroom

Press `Ctrl + Space` again.

Say:

> "Open Google Classroom, find my Probability and Statistics assignment, and prepare it using the correct PDF."

**What to observe:**

1. The persistent browser opens Google Classroom.
2. The agent checks the login state.
3. The requested assignment is located.
4. The relevant local file is identified.
5. The browser navigates to the assignment.
6. The file is attached.
7. The attachment is verified.
8. The agent pauses before final submission and requests approval.

Approve the final action only when the assignment and attachment are correct. For judging, use a dedicated test assignment whenever possible.

If multiple assignments match, the agent should ask the user to select the correct one rather than guessing.

### Demo 3 — Interactive Text Mode

For a demonstration without microphone input, run:

```powershell
.\venv\Scripts\python.exe main.py --cli
```

Enter a command in the terminal to exercise the supported agent workflow.

For text-only responses without speech playback:

```powershell
.\venv\Scripts\python.exe main.py --cli --no-tts
```

These modes are useful fallbacks if the microphone or audio environment causes problems.

---

## Getting Started on Windows

### Prerequisites

- Windows 10 or Windows 11.
- Python 3.11 recommended.
- A working microphone and speakers for voice mode.
- A valid Sarvam AI API key.
- Internet access.
- A Google account with access to the relevant Classroom course for Classroom automation.

### 1. Open the project

Open PowerShell in the repository directory.

Create a virtual environment if one does not already exist:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the virtual environment's Python executable directly in the following steps.

### 2. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
playwright install chromium
```

### 3. Configure Sarvam AI

Create your local environment file:

```powershell
Copy-Item .env.example .env
```

Open `.env` and configure your API key and preferences:

```ini
SARVAM_API_KEY=your_sarvam_api_key_here
PUSH_TO_WAKE_HOTKEY=ctrl+space
SARVAM_TTS_LANGUAGE=en-IN
SARVAM_TTS_SPEAKER=shubh_enhi_ads
SARVAM_CHAT_MODEL=sarvam-105b
SARVAM_STT_MODEL=saaras:v4
```

Use only model IDs, language codes, and speaker names supported by your current Sarvam account and API version.

Get your API key from [Sarvam AI Indus — Key Management](https://indus.sarvam.ai/key-management).

**Important:** Never commit your `.env` file or expose your API key in screenshots, logs, or demonstrations.

### 4. Run diagnostics

```powershell
.\venv\Scripts\python.exe verify_setup.py
```

Resolve any reported dependency, API configuration, microphone, or speaker issues before the live demonstration.

### 5. Launch Saarthi

**Voice mode — recommended for judging**

```powershell
.\venv\Scripts\python.exe main.py
```

Press `Ctrl + Space` and speak your command.

**Interactive CLI**

```powershell
.\venv\Scripts\python.exe main.py --cli
```

**CLI without TTS**

```powershell
.\venv\Scripts\python.exe main.py --cli --no-tts
```

**Smoke test**

```powershell
.\venv\Scripts\python.exe main.py --test
```

The smoke test should report actual results for the integrations it checks. Live API calls and authenticated Classroom workflows require their respective credentials and sessions.

---

## Available Tools

| Tool | Purpose |
|---|---|
| `open_classroom()` | Opens Google Classroom and checks login state |
| `get_pending_classroom_assignments()` | Retrieves supported pending-assignment information |
| `prepare_classroom_submission()` | Locates an assignment and prepares a file attachment |
| `submit_classroom_assignment()` | Performs final submission after valid approval |
| `open_website(url)` | Navigates to a validated website |
| `search_web(query)` | Searches Google or YouTube |
| `find_latest_file(extension)` | Locates a matching file in Downloads |
| `open_application(app_name)` | Opens a supported Windows application |
| `open_downloads_folder()` | Opens the Downloads folder |

Tool availability depends on the current implementation and environment. These tools should validate inputs and report errors instead of silently claiming success.

## Project Structure

```text
├── agent.py                # Core agent orchestration
├── sarvam_client.py        # Sarvam STT, LLM and TTS integration
├── browser_controller.py   # Playwright and Classroom automation
├── desktop_controller.py   # Windows applications and file handling
├── voice_input.py          # Push-to-wake recording and silence detection
├── safety.py               # Confirmation and safety controls
├── main.py                 # Application entry point and CLI modes
├── verify_setup.py         # Setup diagnostics
├── requirements.txt        # Python dependencies
├── .env.example            # Environment configuration template
└── browser_data/           # Persistent browser profile
```

The `browser_data` directory may contain authenticated session data. Keep it private and never upload it to a public repository.

## Reliability and Safety

Saarthi is designed around controlled execution.

- Only registered tools should be executable by the planner.
- Application names, file paths, URLs, and tool arguments should be validated.
- Ambiguous assignment matches should trigger clarification.
- Consequential operations should require explicit, action-specific approval.
- Failed operations should be reported honestly.
- Important actions should be verified using observable application state.
- Credentials and private session data should not be included in logs or committed to source control.

A click is not proof of success. A successful result should be based on what the application actually shows.

## Troubleshooting

| Problem | What to check |
|---|---|
| API authentication failure | Check the API key, account access, and current API requirements |
| Hotkey not responding | Check the configured shortcut and whether another application intercepts it |
| Microphone unavailable | Check Windows microphone permissions and the selected input device |
| No spoken response | Check the TTS configuration, speaker settings, output device, and API response |
| Chromium fails to launch | Run `playwright install chromium` |
| Classroom asks for login | Complete login manually in the persistent browser session |
| Assignment cannot be found | Check course access, assignment naming, and the current Classroom interface |
| Attachment cannot be verified | Inspect the assignment page and confirm the selected file |
| Smoke test fails | Read the individual diagnostic results and verify external-service availability |

## Limitations

Saarthi depends on external APIs, network connectivity, supported application interfaces, and user permissions.

- Speech recognition quality can vary with noise, accents, and mixed-language speech.
- Google Classroom interface changes can affect browser selectors.
- Authentication and security challenges may require manual intervention.
- Some desktop actions may be unavailable on particular Windows configurations.
- End-to-end success depends on the integrations being configured and tested in the actual environment.

The intended feature set should not be confused with verified capabilities. Demonstrate only workflows that have been tested successfully.

## Our Vision

We believe the next generation of desktop interfaces should let people communicate goals rather than manually operate every application.

Saarthi explores that future through multilingual speech, structured planning, real computer interactions, and user-controlled automation.

**Saarthi AI — Speak naturally. See the action. Stay in control.**
