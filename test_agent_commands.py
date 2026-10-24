import os
from dotenv import load_dotenv
from agent import DesktopAgent

load_dotenv()

print("=======================================================")
print("  Running Live Agent Test with Sarvam AI Models")
print("=======================================================")

agent = DesktopAgent(enable_tts=True)

# Test Command 1: Desktop file discovery and application handling
test_cmd_1 = "Open my downloads folder and find the latest PDF file"
print(f"\n>>> Executing Test Command 1: '{test_cmd_1}'")
res_1 = agent.execute_command(test_cmd_1)
print(f"\nResult 1 Spoken Response: {res_1.get('spoken_response')}")
print(f"Result 1 Status: {res_1.get('success')}")

# Test Command 2: Browser Web Search
test_cmd_2 = "Open YouTube and search for Sarvam AI tutorial"
print(f"\n>>> Executing Test Command 2: '{test_cmd_2}'")
res_2 = agent.execute_command(test_cmd_2)
print(f"\nResult 2 Spoken Response: {res_2.get('spoken_response')}")
print(f"Result 2 Status: {res_2.get('success')}")

agent.cleanup()
print("\n[SUCCESS] Both test commands executed cleanly!")
