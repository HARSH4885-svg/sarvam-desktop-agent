"""Safety Guard Module for Push-to-Wake AI Desktop Agent.

Ensures critical and irreversible actions (e.g. submitting assignments, deleting files,
making payments, modifying system files) require explicit user confirmation.
"""

from typing import Callable, Any

class SafetyGuard:
    """Interceptors and confirmation gates for critical desktop and browser actions."""

    CRITICAL_ACTIONS = {
        "submit_classroom_assignment": "Submit Google Classroom assignment",
        "delete_file": "Delete file from filesystem",
        "turn_in_assignment": "Final assignment turn-in",
        "execute_system_command": "Run system shell command",
    }

    def __init__(self, require_confirmation: bool = True):
        self.require_confirmation = require_confirmation

    def is_critical(self, tool_name: str) -> bool:
        """Check if an action requires explicit confirmation."""
        return tool_name in self.CRITICAL_ACTIONS

    def get_action_description(self, tool_name: str) -> str:
        return self.CRITICAL_ACTIONS.get(tool_name, tool_name)

    def request_confirmation(self, tool_name: str, params: dict, confirm_callback: Callable[[str], bool] | None = None) -> bool:
        """
        Request user confirmation for a critical action.
        If confirm_callback is provided (e.g., voice or console prompt), use it.
        Otherwise prompt via standard input.
        """
        action_desc = self.get_action_description(tool_name)
        prompt_text = (
            f"\n[SAFETY GATE] Critical Action Requested: {action_desc}\n"
            f"Details: {params}\n"
            f"Do you want to proceed? (yes/no): "
        )

        if confirm_callback:
            return confirm_callback(prompt_text)

        # Default console prompt fallback
        print(prompt_text, end="", flush=True)
        try:
            choice = input().strip().lower()
            return choice in ["y", "yes", "confirm", "proceed", "haan", "kar do"]
        except Exception:
            return False
