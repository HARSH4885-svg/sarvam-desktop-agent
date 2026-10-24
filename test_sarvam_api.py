import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("SARVAM_API_KEY")
print(f"API Key present: {bool(api_key)}")

# Test 1: Chat Completion
print("\n--- [1] Testing Chat Completion ---")
url = "https://api.sarvam.ai/v1/chat/completions"
headers = {
    "api-subscription-key": api_key,
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}
payload = {
    "messages": [
        {"role": "user", "content": "Reply with one word: 'READY'"}
    ],
    "model": "sarvam-105b",
    "max_tokens": 500,
    "temperature": 0.1
}
res = requests.post(url, json=payload, headers=headers, timeout=20)
print(f"Status: {res.status_code}")
try:
    data = res.json()
    print("Response JSON:", json.dumps(data, indent=2))
except Exception:
    print("Response Text:", res.text)

# Test 2: Text-to-Speech
print("\n--- [2] Testing Text-to-Speech ---")
tts_url = "https://api.sarvam.ai/text-to-speech"
tts_payload = {
    "text": "System initialized and ready.",
    "language_code": "en-IN",
    "speaker": "shubh_enhi_ads",
    "model": "bulbul:v4-flash",
    "output_audio_codec": "wav"
}
tts_headers = {
    "api-subscription-key": api_key,
    "Content-Type": "application/json"
}
tts_res = requests.post(tts_url, json=tts_payload, headers=tts_headers, timeout=20)
print(f"TTS Status: {tts_res.status_code}")
try:
    tts_data = tts_res.json()
    audios = tts_data.get("audios", [])
    print(f"Audio received: {bool(audios)}, count: {len(audios)}, length of audio string: {len(audios[0]) if audios else 0}")
except Exception:
    print("TTS Response Text:", tts_res.text)
