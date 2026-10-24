import os
import json
import base64
import tempfile
import requests
from dotenv import load_dotenv

# Ensure .env is loaded
load_dotenv()

class SarvamClient:
    """Client for interacting with Sarvam AI Speech-to-Text, Chat Completion, and Text-to-Speech APIs."""
    
    BASE_URL = "https://api.sarvam.ai"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("SARVAM_API_KEY")
        if not self.api_key:
            raise ValueError("Sarvam API key not found. Please set SARVAM_API_KEY in .env.")
        
        self.headers = {
            "api-subscription-key": self.api_key,
        }

    def verify_credentials(self) -> dict:
        """Smoke test authentication with a minimal chat completion request."""
        url = f"{self.BASE_URL}/v1/chat/completions"
        payload = {
            "messages": [
                {"role": "user", "content": "Hello"}
            ],
            "model": os.getenv("SARVAM_CHAT_MODEL", "sarvam-105b"),
            "max_tokens": 300,
            "temperature": 0.1
        }
        headers = {
            "api-subscription-key": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=25)
            if response.status_code == 200:
                data = response.json()
                msg = data["choices"][0]["message"]
                reply = msg.get("content") or msg.get("reasoning_content") or "Ready"
                return {"success": True, "message": "Authentication successful", "sample_reply": reply.strip()}
            
            error_msg = f"HTTP {response.status_code}: {response.text}"
            try:
                err_json = response.json()
                if "error" in err_json:
                    err_details = err_json["error"]
                    error_msg = f"Code: {err_details.get('code')}, Message: {err_details.get('message')}"
            except Exception:
                pass
            return {"success": False, "error": error_msg, "status_code": response.status_code}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}

    def speech_to_text(self, audio_file_path: str, model: str | None = None, language_code: str | None = None) -> dict:
        """Transcribe audio using Sarvam Saaras v4."""
        url = f"{self.BASE_URL}/speech-to-text"
        model_name = model or os.getenv("SARVAM_STT_MODEL", "saaras:v4")
        lang = language_code or "unknown"
        
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
            
        with open(audio_file_path, "rb") as f:
            files = {
                "file": (os.path.basename(audio_file_path), f, "audio/wav")
            }
            data = {
                "model": model_name,
                "language_code": lang
            }
            response = requests.post(url, files=files, data=data, headers=self.headers, timeout=30)
            
        if response.status_code == 200:
            res_data = response.json()
            return {
                "success": True,
                "transcript": res_data.get("transcript", ""),
                "language_code": res_data.get("language_code"),
                "request_id": res_data.get("request_id")
            }
        
        return {
            "success": False,
            "error": f"HTTP {response.status_code}: {response.text}",
            "status_code": response.status_code
        }

    def chat_completion(self, messages: list[dict], model: str | None = None, temperature: float = 0.2, response_format: dict | None = None) -> dict:
        """Send chat completion request to Sarvam model (default: sarvam-105b)."""
        url = f"{self.BASE_URL}/v1/chat/completions"
        model_name = model or os.getenv("SARVAM_CHAT_MODEL", "sarvam-105b")
        
        payload = {
            "messages": messages,
            "model": model_name,
            "temperature": temperature,
            "max_tokens": 2500
        }
        if response_format:
            payload["response_format"] = response_format
            
        headers = {
            "api-subscription-key": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code == 200:
            data = response.json()
            msg = data["choices"][0]["message"]
            content = msg.get("content") or msg.get("reasoning_content") or ""
            return {"success": True, "content": content, "raw": data}
            
        return {
            "success": False,
            "error": f"HTTP {response.status_code}: {response.text}",
            "status_code": response.status_code
        }

    def text_to_speech(self, text: str, language_code: str | None = None, speaker: str | None = None, model: str | None = None) -> dict:
        """Synthesize text to speech using Sarvam Bulbul TTS and return WAV bytes."""
        url = f"{self.BASE_URL}/text-to-speech"
        lang = language_code or os.getenv("SARVAM_TTS_LANGUAGE", "en-IN")
        spk = speaker or os.getenv("SARVAM_TTS_SPEAKER", "shubh_enhi_ads")
        mdl = model or "bulbul:v4-flash"
        
        # Clean / truncate text if exceeds limit
        cleaned_text = text.strip()[:2000]
        if not cleaned_text:
            cleaned_text = "Task completed."
            
        payload = {
            "text": cleaned_text,
            "language_code": lang,
            "speaker": spk,
            "model": mdl,
            "output_audio_codec": "wav"
        }
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                audios = data.get("audios", [])
                if audios:
                    audio_bytes = base64.b64decode(audios[0])
                    return {"success": True, "audio_bytes": audio_bytes}
            
            # Fallback to bulbul:v3 with default voice if v4-flash fails
            if mdl == "bulbul:v4-flash":
                payload["model"] = "bulbul:v3"
                payload["speaker"] = "shubh"
                fallback_res = requests.post(url, json=payload, headers=headers, timeout=30)
                if fallback_res.status_code == 200:
                    data = fallback_res.json()
                    audios = data.get("audios", [])
                    if audios:
                        audio_bytes = base64.b64decode(audios[0])
                        return {"success": True, "audio_bytes": audio_bytes}
            
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def play_speech(self, audio_bytes: bytes, temp_path: str = "temp_response.wav"):
        """Save WAV bytes to a file and play through Windows speakers using winsound."""
        try:
            with open(temp_path, "wb") as f:
                f.write(audio_bytes)
            import winsound
            winsound.PlaySound(temp_path, winsound.SND_FILENAME)
            return True
        except Exception as e:
            print(f"[Audio Playback Warning] Could not play sound via winsound: {e}")
            return False
