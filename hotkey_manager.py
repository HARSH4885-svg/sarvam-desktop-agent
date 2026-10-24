import sys
import ctypes
from ctypes import wintypes
import threading
import time
import winsound

user32 = ctypes.windll.user32

# Modifiers
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

# Virtual Keys
VK_SPACE = 0x20
VK_F8 = 0x77
VK_F9 = 0x78

class NativeHotkeyManager:
    """
    Robust system-wide Windows Hotkey Listener using native Win32 RegisterHotKey.
    Unlike hook-based libraries, RegisterHotKey is natively supported by Windows kernel,
    works across all applications, and does not require administrative elevation.
    """

    HOTKEY_CTRL_SPACE = 1
    HOTKEY_CTRL_SHIFT_SPACE = 2
    HOTKEY_F8 = 3

    def __init__(self, callback):
        self.callback = callback
        self.running = False
        self.thread = None
        self._lock = threading.Lock()

    def start(self):
        """Start the message loop in a dedicated background thread."""
        self.running = True
        self.thread = threading.Thread(target=self._message_loop, daemon=True)
        self.thread.start()

    def _message_loop(self):
        # Register primary and backup hotkeys to ensure zero conflicts
        reg_ctrl_space = user32.RegisterHotKey(None, self.HOTKEY_CTRL_SPACE, MOD_CONTROL | MOD_NOREPEAT, VK_SPACE)
        reg_ctrl_shift_space = user32.RegisterHotKey(None, self.HOTKEY_CTRL_SHIFT_SPACE, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_SPACE)
        reg_f8 = user32.RegisterHotKey(None, self.HOTKEY_F8, MOD_NOREPEAT, VK_F8)

        print("\n[*] Hotkey Activation Status:")
        print(f"    [1] Ctrl + Space:         {'ACTIVE' if reg_ctrl_space else 'BLOCKED (In use by another application)'}")
        print(f"    [2] Ctrl + Shift + Space: {'ACTIVE' if reg_ctrl_shift_space else 'FAILED'}")
        print(f"    [3] F8 (Single Key Wake): {'ACTIVE' if reg_f8 else 'FAILED'}")
        print("[*] Press any active hotkey to wake the agent.\n")

        msg = wintypes.MSG()
        while self.running:
            # GetMessageW blocks until a message is sent to this thread
            res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if res <= 0:
                break

            if msg.message == 0x0312:  # WM_HOTKEY
                hotkey_id = msg.wParam
                # Play brief chime so user knows recording started
                try:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                except Exception:
                    pass

                # Dispatch callback
                if self.callback:
                    try:
                        self.callback(hotkey_id)
                    except Exception as e:
                        print(f"[!] Error in hotkey callback: {e}")

            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        # Cleanup
        user32.UnregisterHotKey(None, self.HOTKEY_CTRL_SPACE)
        user32.UnregisterHotKey(None, self.HOTKEY_CTRL_SHIFT_SPACE)
        user32.UnregisterHotKey(None, self.HOTKEY_F8)

    def stop(self):
        """Stop listening and unregister hotkeys."""
        self.running = False
        user32.PostQuitMessage(0)
