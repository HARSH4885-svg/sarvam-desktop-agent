import os
import json
import re
from typing import Dict, Any, List

from sarvam_client import SarvamClient
from voice_input import VoiceRecorder
from browser_controller import BrowserController
from desktop_controller import DesktopController
from safety import SafetyGuard

class DesktopAgent:
    """Push-to-wake AI Desktop Agent powered by Sarvam AI."""

    SYSTEM_PROMPT = """You are a fast, decisive Windows Desktop AI Assistant powered by Sarvam AI.
The user speaks in English, Hindi, or Hinglish (e.g., "Open Classroom and find my PNS assignment", "Mera downloads folder kholo aur latest PDF attach kar do").

You control the user's PC using the following tools:

1. open_website(url: str): Open any website in the browser.
2. search_web(query: str): Search Google or YouTube.
3. open_classroom(): Open Google Classroom and verify account status.
4. get_pending_classroom_assignments(): List pending assignments in Google Classroom.
5. prepare_classroom_submission(assignment_query: str, file_path: str): Find assignment matching query, open it, and attach the given file path.
6. submit_classroom_assignment(assignment_query: str): Submit/turn in an assignment (CRITICAL: only call after user gives explicit confirmation).
7. open_application(app_name: str, argument: str): Launch local Windows app (e.g., 'code', 'explorer', 'notepad').
8. open_downloads_folder(): Open user's Downloads folder in Explorer.
9. find_latest_file(directory: str, extension: str): Find latest file (e.g., extension='.pdf') in Downloads or project.
10. list_recent_files(directory: str, limit: int): List recent files.
11. click_element(description: str): Click button or link by text.
12. fill_input(description: str, value: str): Fill text box.

OUTPUT FORMAT:
You MUST respond ONLY with a valid JSON object matching this exact schema:
{
  "thought": "Brief explanation of your plan",
  "actions": [
    {
      "tool": "tool_name",
      "parameters": {
        "param_name": "value"
      }
    }
  ],
  "spoken_response": "Short, clear natural response to speak back to the user in English or friendly Hinglish (max 2 sentences)."
}

EXAMPLES:

User: "Open Google Classroom, find my pending Probability and Statistics assignment, and prepare it for submission with my latest PDF"
Output:
{
  "thought": "First locate the latest PDF in Downloads, open Google Classroom, and prepare the submission for Probability and Statistics.",
  "actions": [
    {"tool": "find_latest_file", "parameters": {"extension": ".pdf"}},
    {"tool": "open_classroom", "parameters": {}},
    {"tool": "prepare_classroom_submission", "parameters": {"assignment_query": "Probability", "file_path": "latest"}}
  ],
  "spoken_response": "I'm opening Google Classroom and attaching your latest Probability assignment. I will wait for your confirmation before turning it in."
}

User: "Open YouTube and search for machine learning tutorial"
Output:
{
  "thought": "Open website YouTube with search query.",
  "actions": [
    {"tool": "open_website", "parameters": {"url": "https://www.youtube.com/results?search_query=machine+learning+tutorial"}}
  ],
  "spoken_response": "Opening YouTube and searching for machine learning tutorials."
}

User: "Open my downloads folder and find the latest PDF"
Output:
{
  "thought": "Open downloads folder and search for latest PDF.",
  "actions": [
    {"tool": "open_downloads_folder", "parameters": {}},
    {"tool": "find_latest_file", "parameters": {"extension": ".pdf"}}
  ],
  "spoken_response": "I've opened your Downloads folder and located your newest PDF."
}

Do not include markdown code block formatting (like ```json), just raw JSON or json inside standard markdown.
"""

    def __init__(self, sarvam_api_key: str | None = None, enable_tts: bool = True):
        self.sarvam = SarvamClient(api_key=sarvam_api_key)
        self.browser = BrowserController()
        self.desktop = DesktopController()
        self.recorder = VoiceRecorder()
        self.safety = SafetyGuard()
        self.enable_tts = enable_tts
        self.context_memory: Dict[str, Any] = {}

    def process_voice_command(self, audio_path: str = "temp_user_command.wav") -> dict:
        """Transcribe audio command and execute actions."""
        print(f"\n[Transcribing audio with Sarvam Saaras v4]...")
        stt_result = self.sarvam.speech_to_text(audio_path)
        
        if not stt_result.get("success"):
            err = stt_result.get("error", "Speech recognition failed")
            print(f"[STT Error]: {err}")
            self.speak("Sorry, I could not recognize your voice. Please try again.")
            return {"success": False, "error": err}

        transcript = stt_result.get("transcript", "").strip()
        print(f"\n[User Said]: \"{transcript}\"")
        if not transcript:
            self.speak("I didn't catch that. Could you please repeat?")
            return {"success": False, "error": "Empty transcript"}

        return self.execute_command(transcript)

    def execute_command(self, command_text: str) -> dict:
        """Plan and execute actions for a textual command."""
        print(f"\n[Reasoning with Sarvam LLM]...")
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": command_text}
        ]

        response = self.sarvam.chat_completion(messages, temperature=0.1)
        if not response.get("success"):
            err = response.get("error", "LLM reasoning failed")
            print(f"[Reasoning Error]: {err}")
            self.speak("I had trouble understanding that command. Please check my connection.")
            return {"success": False, "error": err}

        raw_content = response.get("content", "").strip()
        plan = self._parse_json_plan(raw_content)

        thought = plan.get("thought", "")
        actions = plan.get("actions", [])
        spoken_response = plan.get("spoken_response", "Working on that now.")

        print(f"[Agent Plan]: {thought}")
        print(f"[Scheduled Actions]: {len(actions)} steps")

        execution_results = []
        for i, action in enumerate(actions, 1):
            tool = action.get("tool")
            params = action.get("parameters", {})
            print(f"  Step {i}: Running {tool}({params})...")

            # Resolve dynamic references (e.g. 'latest' file)
            params = self._resolve_dynamic_params(tool, params)

            # Safety check
            if self.safety.is_critical(tool):
                confirmed = self.safety.request_confirmation(tool, params)
                if not confirmed:
                    print(f"  [ACTION CANCELLED] User declined confirmation for {tool}.")
                    execution_results.append({"tool": tool, "status": "cancelled", "reason": "user_declined"})
                    continue

            # Execute tool
            res = self._dispatch_tool(tool, params)
            print(f"  Step {i} Result: {res.get('status', 'done')}")
            execution_results.append({"tool": tool, "result": res})

        # Provide spoken feedback via Sarvam Bulbul TTS
        print(f"\n[Speaking Response]: \"{spoken_response}\"")
        if self.enable_tts:
            self.speak(spoken_response)

        return {
            "success": True,
            "transcript": command_text,
            "plan": plan,
            "results": execution_results,
            "spoken_response": spoken_response
        }

    def _dispatch_tool(self, tool_name: str, params: dict) -> dict:
        """Route tool call to appropriate controller method."""
        try:
            if tool_name == "open_website":
                return self.browser.open_website(params.get("url", "https://google.com"))
            elif tool_name == "search_web":
                return self.browser.search_web(params.get("query", ""))
            elif tool_name == "open_classroom":
                return self.browser.open_classroom()
            elif tool_name == "get_pending_classroom_assignments":
                return self.browser.get_pending_classroom_assignments()
            elif tool_name == "prepare_classroom_submission":
                return self.browser.prepare_classroom_submission(
                    params.get("assignment_query", ""),
                    params.get("file_path", "")
                )
            elif tool_name == "submit_classroom_assignment":
                return self.browser.submit_classroom_assignment(params.get("assignment_query", ""))
            elif tool_name == "click_element":
                return self.browser.click_element(params.get("description", ""))
            elif tool_name == "fill_input":
                return self.browser.fill_input(params.get("description", ""), params.get("value", ""))
            elif tool_name == "open_application":
                return self.desktop.open_application(params.get("app_name", ""), params.get("argument"))
            elif tool_name == "open_downloads_folder":
                return self.desktop.open_downloads_folder()
            elif tool_name == "find_latest_file":
                res = self.desktop.find_latest_file(params.get("directory"), params.get("extension"))
                if res.get("status") == "success":
                    self.context_memory["latest_file"] = res.get("file_path")
                return res
            elif tool_name == "list_recent_files":
                return self.desktop.list_recent_files(params.get("directory"), params.get("limit", 5))
            else:
                return {"status": "error", "error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _resolve_dynamic_params(self, tool_name: str, params: dict) -> dict:
        """Resolve keywords like 'latest' or cached file paths."""
        resolved = dict(params)
        if tool_name == "prepare_classroom_submission":
            fp = resolved.get("file_path", "")
            if not fp or fp.lower() == "latest" or not os.path.exists(fp):
                # Attempt to use latest file from memory or auto-discover
                if "latest_file" in self.context_memory and os.path.exists(self.context_memory["latest_file"]):
                    resolved["file_path"] = self.context_memory["latest_file"]
                else:
                    latest = self.desktop.find_latest_file(extension=".pdf")
                    if latest.get("status") == "success":
                        resolved["file_path"] = latest.get("file_path")
                    else:
                        latest_any = self.desktop.find_latest_file()
                        if latest_any.get("status") == "success":
                            resolved["file_path"] = latest_any.get("file_path")
        return resolved

    def _parse_json_plan(self, text: str) -> dict:
        """Extract valid JSON from LLM output."""
        try:
            return json.loads(text)
        except Exception:
            pass

        # Try regex search for {...}
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass

        return {
            "thought": "Direct execution fallback",
            "actions": [],
            "spoken_response": text[:150]
        }

    def speak(self, text: str):
        """Synthesize text to speech using Sarvam Bulbul and play sound."""
        if not text:
            return
        tts_res = self.sarvam.text_to_speech(text)
        if tts_res.get("success"):
            self.sarvam.play_speech(tts_res.get("audio_bytes"))
        else:
            print(f"[TTS Warning]: {tts_res.get('error')}")

    def cleanup(self):
        """Close browser context and clean up resources."""
        self.browser.close()
