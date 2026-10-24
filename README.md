# Push-to-Wake AI Desktop Agent Powered by Sarvam AI

An intelligent, voice-controlled Windows desktop agent powered by Sarvam AI. Activate it with a global hotkey (**Ctrl + Space**), speak naturally in **English, Hindi, or Hinglish**, and watch the agent navigate your browser, automate Google Classroom, control desktop apps, and speak back in real time.

---

## Key Features

- **Push-to-Wake Global Hotkey**: Press `Ctrl + Space` anywhere on Windows to activate listening.
- **Full Sarvam AI Stack**:
  - **Speech-to-Text**: Sarvam **Saaras v4** (`saaras:v4`) for accurate multi-lingual Indian speech recognition.
  - **Reasoning & Planning**: Sarvam **105B** Chat Completions (`sarvam-105b`) structured JSON tool-call planner.
  - **Text-to-Speech**: Sarvam **Bulbul** (`bulbul:v4-flash` / `bulbul:v3`) for natural spoken audio responses played directly through Windows speakers.
- **Browser Automation (Playwright)**:
  - Persistent Chromium session saved in `./browser_data` (log in once to Google/Classroom and keep your session).
  - Automated Google Classroom navigation: checks pending assignments, finds specific classes/assignments (e.g., Probability & Statistics), and attaches homework files.
  - Web search on Google / YouTube, link navigation, button clicking, form filling.
- **Desktop Automation**:
  - Launch applications (VS Code, Explorer, Notepad, Calculator).
  - Search and locate the latest downloaded assignment files or PDFs.
- **Safety Gate**:
  - Enforces explicit user confirmation before irreversible actions (such as final submission / "Turn in" on Google Classroom).

---

## Project Structure

```
├── agent.py               # Core orchestrator: connects STT -> Planner -> Tools -> TTS
├── sarvam_client.py       # Sarvam AI API client (STT, LLM chat, TTS, playback)
├── browser_controller.py  # Playwright browser controller with Classroom workflows
├── desktop_controller.py  # Windows desktop application & file manager
├── voice_input.py         # Push-to-wake audio recorder with silence detection
├── safety.py              # Safety gate requiring confirmation on critical actions
├── main.py                # Main entrypoint (Push-to-Wake hotkey & CLI modes)
├── verify_setup.py        # System diagnostic script
├── requirements.txt       # Python dependencies
├── .env.example           # Environment template
└── browser_data/          # Persistent Playwright browser profile directory
```

---

## Windows Setup & Installation

### 1. Prerequisites
- **Windows 10 / 11**
- **Python 3.10+** (Python 3.11 recommended)
- Working Microphone & Speakers

### 2. Environment Setup
Open PowerShell in the project directory:

```powershell
# Activate the existing virtual environment (or create one if needed)
.\venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

### 3. Configure Your Sarvam API Key
Create a `.env` file in the root folder (or copy from `.env.example`):

```powershell
Copy-Item .env.example .env
```

Open `.env` and fill in your Sarvam AI subscription key:
```ini
SARVAM_API_KEY=your_sarvam_api_key_here
PUSH_TO_WAKE_HOTKEY=ctrl+space
SARVAM_TTS_LANGUAGE=en-IN
SARVAM_TTS_SPEAKER=shubh_enhi_ads
SARVAM_CHAT_MODEL=sarvam-105b
SARVAM_STT_MODEL=saaras:v4
```
> Obtain your key from: [Sarvam AI Indus Key Management](https://indus.sarvam.ai/key-management)

### 4. Run System Diagnostics
Verify your microphone, speakers, and dependencies:

```powershell
.\venv\Scripts\python.exe verify_setup.py
```

---

## How to Run

### Mode 1: Push-to-Wake (Default)
Runs in the background waiting for the global shortcut:

```powershell
.\venv\Scripts\python.exe main.py
```
- Press **Ctrl + Space** anywhere in Windows.
- Speak your command (e.g. *"Open Google Classroom and find my pending Probability assignment"*).
- The agent records, transcribes with Saaras v4, plans the steps with Sarvam 105B, executes them visibly on your PC, and speaks the confirmation with Bulbul TTS!

### Mode 2: Interactive CLI / Demo Mode
Ideal for testing without pressing hotkeys or in environments without audio:

```powershell
# Interactive text prompt (type 'voice' anytime to speak)
.\venv\Scripts\python.exe main.py --cli

# Test without speech playback (text-only responses)
.\venv\Scripts\python.exe main.py --cli --no-tts
```

### Mode 3: Smoke Test Mode
Verifies live API credentials, Playwright browser opening, and desktop controllers:

```powershell
.\venv\Scripts\python.exe main.py --test
```

---

## Implemented Tool Capabilities

| Tool | Category | Description |
|---|---|---|
| `open_classroom()` | Browser | Opens Google Classroom and checks login state |
| `get_pending_classroom_assignments()` | Browser | Scrapes pending assignments from To-Do / Classwork |
| `prepare_classroom_submission()` | Browser | Finds assignment, attaches specified or latest PDF file |
| `submit_classroom_assignment()` | Browser (Safety) | Submits/Turns in assignment (**requires confirmation**) |
| `open_website(url)` | Browser | Navigates to any target URL |
| `search_web(query)` | Browser | Performs query on Google or YouTube |
| `find_latest_file(extension)` | Desktop | Locates latest file (e.g., `.pdf`) in Downloads |
| `open_application(app_name)` | Desktop | Launches Windows software (VS Code, Explorer, Notepad) |
| `open_downloads_folder()` | Desktop | Opens Downloads folder in Windows Explorer |

---

## 3-Minute Hackathon Demo Script

Use this exact script when presenting to hackathon judges:

### 1. The Hook (30 seconds)
> *"Hello judges! We all use voice assistants on our phones, but on desktop PCs, assistants still can't do real multi-step work across native applications and web browsers. Today, we built the **Push-to-Wake AI Desktop Agent**, powered completely by **Sarvam AI**'s speech and language models."*

### 2. Live Demo Part 1: Push-to-Wake & Desktop Control (45 seconds)
1. Run `python main.py` in PowerShell.
2. Press **Ctrl + Space**.
3. Speak into microphone:
   > *"Open my downloads folder and find my latest PDF file."*
4. **Judge observation**: The agent immediately detects the speech with **Saaras v4**, launches Windows Explorer, identifies the latest downloaded file, and speaks back via **Bulbul TTS**.

### 3. Live Demo Part 2: Google Classroom End-to-End Automation (60 seconds)
1. Press **Ctrl + Space**.
2. Speak:
   > *"Open Google Classroom, find my Probability and Statistics assignment, and prepare it for submission."*
3. **Judge observation**:
   - The browser opens Google Classroom using the persistent profile.
   - It navigates to the assignment and clicks "Add or create" -> "File".
   - It attaches the latest PDF automatically.
   - The agent halts at the **Safety Gate** and asks: *"Attached your assignment. Would you like me to submit it?"*
   - Type or speak **Yes** to perform the final turn-in.

### 4. Why Sarvam AI (30 seconds)
> *"Sarvam AI is the powerhouse behind this: Saaras v4 accurately handles Indian accents and mixed Hinglish commands, Sarvam 105B structures complex desktop plans reliably, and Bulbul TTS provides low-latency, natural sounding vocal feedback right on Windows."*
