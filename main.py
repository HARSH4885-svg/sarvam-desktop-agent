import os
import sys
import time
import argparse
import keyboard
from dotenv import load_dotenv

from agent import DesktopAgent
from sarvam_client import SarvamClient

# Force line-buffered stdout for real-time output
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

# Load environment configuration
load_dotenv()

def print_banner():
    banner = """
===================================================================
    Push-to-Wake AI Desktop Agent Powered by Sarvam AI
===================================================================
[*] STT Model:      Sarvam Saaras v4
[*] Reasoning:      Sarvam Chat Completions (sarvam-105b)
[*] TTS Model:      Sarvam Bulbul (v4-flash / v3)
[*] Automation:     Playwright Browser + Windows Desktop Controller
[*] Safety Guard:   Active (confirmation required for submission)
===================================================================
"""
    print(banner)

def run_smoke_test(agent: DesktopAgent):
    """Run an end-to-end smoke test of API credentials, browser, and desktop."""
    print("\n--- Running Milestone A: API & Environment Smoke Test ---")
    
    # 1. Test Sarvam AI API
    print("[1/3] Testing Sarvam AI Chat API...")
    auth_check = agent.sarvam.verify_credentials()
    if auth_check.get("success"):
        print(f"  [+] API Connection Successful! Reply: '{auth_check.get('sample_reply')}'")
    else:
        print(f"  [-] API Connection Failed: {auth_check.get('error')}")
        print("      Please ensure your SARVAM_API_KEY in .env is valid.")
        return False

    # 2. Test Browser Controller
    print("\n[2/3] Testing Playwright Browser Context...")
    try:
        page_res = agent.browser.open_website("https://example.com")
        print(f"  [+] Browser opened successfully: {page_res.get('title')} ({page_res.get('url')})")
    except Exception as e:
        print(f"  [-] Browser test failed: {e}")
        return False

    # 3. Test Desktop Controller
    print("\n[3/3] Testing Desktop Controller...")
    latest_file = agent.desktop.find_latest_file()
    print(f"  [+] Discovered latest file in Downloads: {latest_file.get('file_name', 'None')}")

    print("\n[SUCCESS] Smoke test completed successfully! Ready for voice interaction.")
    return True

from hotkey_manager import NativeHotkeyManager

def start_push_to_wake(agent: DesktopAgent, hotkey: str = "ctrl+space"):
    """Register system-wide global hotkeys using native Windows API."""
    is_processing = False

    def on_hotkey_pressed(hotkey_id: int):
        nonlocal is_processing
        if is_processing:
            print("\n[Busy] Currently processing previous command, please wait...")
            return

        is_processing = True
        key_name = "Ctrl+Space" if hotkey_id == 1 else ("Ctrl+Shift+Space" if hotkey_id == 2 else "F8")
        print(f"\n=======================================================")
        print(f"[*] Push-to-wake triggered via [{key_name}]! RECORDING AUDIO...")
        print(f"[*] Speak in English or Hinglish now (auto-stops on silence)...")
        print(f"=======================================================")

        try:
            # Record audio with auto-silence detection
            recorded = agent.recorder.record_to_file("temp_voice_command.wav", max_duration=12.0, silence_timeout=1.6)
            if not recorded:
                print("[!] No speech detected.")
            else:
                agent.process_voice_command("temp_voice_command.wav")
        except Exception as e:
            print(f"[!] Error during voice processing: {e}")
        finally:
            is_processing = False
            print(f"\n[*] Listening... Press [Ctrl+Space], [Ctrl+Shift+Space], or [F8] anytime.")

    listener = NativeHotkeyManager(on_hotkey_pressed)
    listener.start()

    print("[*] Push-to-Wake Listener is active in foreground.")
    print("[*] Press Ctrl+C in this console window to quit.\n")

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[*] Exiting Push-to-Wake agent...")
    finally:
        listener.stop()
        agent.cleanup()

def start_interactive_cli(agent: DesktopAgent):
    """Interactive loop allowing typed commands and instant execution."""
    print("\n[*] Interactive Console Mode Active.")
    print("[*] Type your command (or 'voice' to speak, 'exit' to quit):\n")

    while True:
        try:
            user_input = input("Agent > ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                break

            if user_input.lower() == "voice":
                print("\n[*] Recording microphone for up to 10 seconds (speak now)...")
                agent.recorder.record_to_file("temp_voice_command.wav", max_duration=10.0, silence_timeout=1.6)
                agent.process_voice_command("temp_voice_command.wav")
            else:
                agent.execute_command(user_input)

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"[!] Error: {e}")

    agent.cleanup()
    print("\n[*] Goodbye!")

def main():
    parser = argparse.ArgumentParser(description="Push-to-Wake AI Desktop Agent Powered by Sarvam AI")
    parser.add_argument("--test", action="store_true", help="Run initial smoke tests")
    parser.add_argument("--cli", action="store_true", help="Run in interactive text CLI mode")
    parser.add_argument("--no-tts", action="store_true", help="Disable spoken audio response")
    parser.add_argument("--hotkey", type=str, default=os.getenv("PUSH_TO_WAKE_HOTKEY", "ctrl+space"), help="Global hotkey")
    args = parser.parse_args()

    print_banner()

    api_key = os.getenv("SARVAM_API_KEY")
    if not api_key or api_key == "your_sarvam_api_key_here":
        print("\n[!] Warning: SARVAM_API_KEY is not configured in .env.")
        prompt_key = input("Please enter your Sarvam AI API Key: ").strip()
        if prompt_key:
            api_key = prompt_key
            # Save to .env for convenience
            try:
                with open(".env", "a") as f:
                    f.write(f"\nSARVAM_API_KEY={api_key}\n")
                print("[+] Saved SARVAM_API_KEY to .env file.")
            except Exception:
                pass
        else:
            print("[-] API key is required to run the agent. Exiting.")
            sys.exit(1)

    agent = DesktopAgent(sarvam_api_key=api_key, enable_tts=not args.no_tts)

    if args.test:
        run_smoke_test(agent)
        return

    if args.cli:
        start_interactive_cli(agent)
    else:
        start_push_to_wake(agent, hotkey=args.hotkey)

if __name__ == "__main__":
    main()
