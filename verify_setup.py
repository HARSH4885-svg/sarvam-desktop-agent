import os
import sys

print("[*] Testing imports...")
try:
    import requests
    import sounddevice as sd
    import scipy
    import playwright
    import keyboard
    import dotenv
    print("  [+] Core third-party libraries imported successfully.")
except ImportError as e:
    print(f"  [-] Import error: {e}")
    sys.exit(1)

try:
    from sarvam_client import SarvamClient
    from voice_input import VoiceRecorder
    from browser_controller import BrowserController
    from desktop_controller import DesktopController
    from safety import SafetyGuard
    from agent import DesktopAgent
    print("  [+] Project modules imported successfully.")
except ImportError as e:
    print(f"  [-] Project module error: {e}")
    sys.exit(1)

# Check audio devices
print("\n[*] Inspecting audio input/output devices...")
try:
    devices = sd.query_devices()
    default_input = sd.default.device[0]
    default_output = sd.default.device[1]
    input_info = sd.query_devices(default_input) if default_input is not None else None
    output_info = sd.query_devices(default_output) if default_output is not None else None
    print(f"  [+] Default Audio Input:  {input_info['name'] if input_info else 'Not detected'}")
    print(f"  [+] Default Audio Output: {output_info['name'] if output_info else 'Not detected'}")
except Exception as e:
    print(f"  [-] Audio device check: {e}")

# Check Desktop Controller
print("\n[*] Testing Desktop Controller...")
desktop = DesktopController()
latest = desktop.find_latest_file()
print(f"  [+] Latest file search status: {latest.get('status')} -> {latest.get('file_name', 'None')}")

# Check API Key
print("\n[*] Checking Sarvam AI API Configuration...")
api_key = os.getenv("SARVAM_API_KEY")
if not api_key or api_key == "your_sarvam_api_key_here":
    print("  [!] SARVAM_API_KEY is not set yet in .env.")
    print("      To test live speech-to-text and reasoning, add your key to .env:")
    print("      SARVAM_API_KEY=your_key_from_indus_sarvam_ai")
else:
    print("  [+] SARVAM_API_KEY is configured!")
    client = SarvamClient(api_key=api_key)
    res = client.verify_credentials()
    print(f"  [+] API verification result: {res}")

print("\n[COMPLETE] System verification finished.")
