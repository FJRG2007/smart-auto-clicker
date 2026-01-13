"""
Native Input System - Low-level input injection for maximum compatibility.

Este modulo implementa multiples metodos de input para maximizar
la compatibilidad con juegos y aplicaciones que bloquean autoclickers.

Metodos disponibles (de mas compatible a menos):
1. Interception Driver - Eventos a nivel de kernel, indistinguibles de hardware real
2. SendInput con flags optimizados - API de Windows de bajo nivel
3. mouse_event legacy - API antigua, algunos juegos la aceptan mejor
4. Default (mouse library) - Fallback estandar

El sistema detecta automaticamente cual metodo funciona mejor.
"""

import ctypes
from ctypes import wintypes
from typing import Tuple, Optional, Callable
from enum import Enum
import time
import sys

# Windows API constants
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_VIRTUALDESK = 0x4000

# Keyboard constants
KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008

# Input type constants
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1


class InputMethod(Enum):
    """Available input methods."""
    AUTO = "auto"                    # Auto-detect best method
    INTERCEPTION = "interception"   # Kernel-level driver (best)
    SENDINPUT = "sendinput"         # Windows SendInput API
    MOUSE_EVENT = "mouse_event"     # Legacy mouse_event API
    DEFAULT = "default"              # Standard mouse library


class MOUSEINPUT(ctypes.Structure):
    """Windows MOUSEINPUT structure."""
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]


class KEYBDINPUT(ctypes.Structure):
    """Windows KEYBDINPUT structure."""
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG)),
    ]


class HARDWAREINPUT(ctypes.Structure):
    """Windows HARDWAREINPUT structure."""
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    """Union for INPUT structure."""
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    """Windows INPUT structure for SendInput."""
    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION),
    ]


class NativeInput:
    """
    Native input system with multiple injection methods.

    Provides low-level input injection that works with most games
    and applications, including those with anti-cheat protection.
    """

    # Virtual key codes
    VK_CODES = {
        'a': 0x41, 'b': 0x42, 'c': 0x43, 'd': 0x44, 'e': 0x45,
        'f': 0x46, 'g': 0x47, 'h': 0x48, 'i': 0x49, 'j': 0x4A,
        'k': 0x4B, 'l': 0x4C, 'm': 0x4D, 'n': 0x4E, 'o': 0x4F,
        'p': 0x50, 'q': 0x51, 'r': 0x52, 's': 0x53, 't': 0x54,
        'u': 0x55, 'v': 0x56, 'w': 0x57, 'x': 0x58, 'y': 0x59,
        'z': 0x5A, '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33,
        '4': 0x34, '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38,
        '9': 0x39, 'space': 0x20, 'enter': 0x0D, 'tab': 0x09,
        'escape': 0x1B, 'backspace': 0x08, 'shift': 0x10,
        'ctrl': 0x11, 'alt': 0x12, 'capslock': 0x14,
        'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
        'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
        'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
    }

    # Scan codes for hardware-level input
    SCAN_CODES = {
        'a': 0x1E, 'b': 0x30, 'c': 0x2E, 'd': 0x20, 'e': 0x12,
        'f': 0x21, 'g': 0x22, 'h': 0x23, 'i': 0x17, 'j': 0x24,
        'k': 0x25, 'l': 0x26, 'm': 0x32, 'n': 0x31, 'o': 0x18,
        'p': 0x19, 'q': 0x10, 'r': 0x13, 's': 0x1F, 't': 0x14,
        'u': 0x16, 'v': 0x2F, 'w': 0x11, 'x': 0x2D, 'y': 0x15,
        'z': 0x2C, '0': 0x0B, '1': 0x02, '2': 0x03, '3': 0x04,
        '4': 0x05, '5': 0x06, '6': 0x07, '7': 0x08, '8': 0x09,
        '9': 0x0A, 'space': 0x39, 'enter': 0x1C, 'tab': 0x0F,
        'escape': 0x01, 'backspace': 0x0E, 'shift': 0x2A,
        'ctrl': 0x1D, 'alt': 0x38, 'capslock': 0x3A,
        'f1': 0x3B, 'f2': 0x3C, 'f3': 0x3D, 'f4': 0x3E,
        'f5': 0x3F, 'f6': 0x40, 'f7': 0x41, 'f8': 0x42,
        'f9': 0x43, 'f10': 0x44, 'f11': 0x57, 'f12': 0x58,
    }

    def __init__(self, method: InputMethod = InputMethod.AUTO):
        self.method = method
        self.interception_available = False
        self.interception_context = None
        self.interception_device = None

        # Load Windows APIs
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32

        # Setup SendInput
        self.user32.SendInput.argtypes = [
            wintypes.UINT,
            ctypes.POINTER(INPUT),
            ctypes.c_int
        ]
        self.user32.SendInput.restype = wintypes.UINT

        # Setup mouse_event (legacy)
        self.user32.mouse_event.argtypes = [
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.DWORD,
            wintypes.DWORD,
            ctypes.POINTER(wintypes.ULONG)
        ]

        # Setup GetCursorPos
        self.user32.GetCursorPos.argtypes = [ctypes.POINTER(wintypes.POINT)]
        self.user32.GetCursorPos.restype = wintypes.BOOL

        # Setup SetCursorPos
        self.user32.SetCursorPos.argtypes = [ctypes.c_int, ctypes.c_int]
        self.user32.SetCursorPos.restype = wintypes.BOOL

        # Get screen metrics for absolute positioning
        self.screen_width = self.user32.GetSystemMetrics(0)
        self.screen_height = self.user32.GetSystemMetrics(1)

        # Try to initialize Interception driver
        if method in [InputMethod.AUTO, InputMethod.INTERCEPTION]:
            self._init_interception()

        # Select best available method
        if method == InputMethod.AUTO:
            self.active_method = self._detect_best_method()
        else:
            self.active_method = method

    def _init_interception(self) -> bool:
        """
        Initialize Interception driver if available.
        Interception provides kernel-level input that's indistinguishable from real hardware.
        """
        try:
            # Try to load interception library
            if sys.platform == 'win32':
                try:
                    self.interception_dll = ctypes.CDLL("interception.dll")
                    self.interception_available = True

                    # Setup interception functions
                    self.interception_dll.interception_create_context.restype = ctypes.c_void_p
                    self.interception_context = self.interception_dll.interception_create_context()

                    if self.interception_context:
                        # Find first mouse device
                        for i in range(10, 20):  # Mouse devices are 10-19
                            if self.interception_dll.interception_is_mouse(i):
                                self.interception_device = i
                                break
                        return True
                except OSError:
                    pass
        except Exception:
            pass

        self.interception_available = False
        return False

    def _detect_best_method(self) -> InputMethod:
        """Detect the best available input method."""
        if self.interception_available:
            return InputMethod.INTERCEPTION
        return InputMethod.SENDINPUT

    def get_cursor_pos(self) -> Tuple[int, int]:
        """Get current cursor position."""
        point = wintypes.POINT()
        self.user32.GetCursorPos(ctypes.byref(point))
        return point.x, point.y

    def set_cursor_pos(self, x: int, y: int):
        """Set cursor position."""
        self.user32.SetCursorPos(x, y)

    def _to_absolute(self, x: int, y: int) -> Tuple[int, int]:
        """Convert screen coordinates to absolute coordinates (0-65535)."""
        abs_x = int(x * 65535 / self.screen_width)
        abs_y = int(y * 65535 / self.screen_height)
        return abs_x, abs_y

    def _send_mouse_input(self, flags: int, dx: int = 0, dy: int = 0, data: int = 0):
        """Send mouse input using SendInput API."""
        extra = ctypes.pointer(wintypes.ULONG(0))
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp.union.mi.dx = dx
        inp.union.mi.dy = dy
        inp.union.mi.mouseData = data
        inp.union.mi.dwFlags = flags
        inp.union.mi.time = 0
        inp.union.mi.dwExtraInfo = extra

        self.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

    def _send_mouse_event_legacy(self, flags: int, dx: int = 0, dy: int = 0, data: int = 0):
        """Send mouse input using legacy mouse_event API."""
        extra = ctypes.pointer(wintypes.ULONG(0))
        self.user32.mouse_event(flags, dx, dy, data, extra)

    def _send_interception_click(self, button: str, down: bool):
        """Send mouse click through Interception driver."""
        if not self.interception_available or not self.interception_device:
            return False

        try:
            # Interception mouse stroke structure
            class InterceptionMouseStroke(ctypes.Structure):
                _fields_ = [
                    ("state", ctypes.c_ushort),
                    ("flags", ctypes.c_ushort),
                    ("rolling", ctypes.c_short),
                    ("x", ctypes.c_int),
                    ("y", ctypes.c_int),
                    ("information", ctypes.c_uint),
                ]

            stroke = InterceptionMouseStroke()
            stroke.flags = 0
            stroke.rolling = 0
            stroke.x = 0
            stroke.y = 0
            stroke.information = 0

            # Set button state
            if button == "left":
                stroke.state = 0x001 if down else 0x002  # LEFT_DOWN / LEFT_UP
            elif button == "right":
                stroke.state = 0x004 if down else 0x008  # RIGHT_DOWN / RIGHT_UP
            elif button == "middle":
                stroke.state = 0x010 if down else 0x020  # MIDDLE_DOWN / MIDDLE_UP

            self.interception_dll.interception_send(
                self.interception_context,
                self.interception_device,
                ctypes.byref(stroke),
                1
            )
            return True
        except Exception:
            return False

    def mouse_down(self, button: str = "left"):
        """Press mouse button down."""
        if self.active_method == InputMethod.INTERCEPTION and self.interception_available:
            if self._send_interception_click(button, True):
                return

        flags_map = {
            "left": MOUSEEVENTF_LEFTDOWN,
            "right": MOUSEEVENTF_RIGHTDOWN,
            "middle": MOUSEEVENTF_MIDDLEDOWN,
        }
        flags = flags_map.get(button, MOUSEEVENTF_LEFTDOWN)

        if self.active_method == InputMethod.MOUSE_EVENT:
            self._send_mouse_event_legacy(flags)
        else:
            self._send_mouse_input(flags)

    def mouse_up(self, button: str = "left"):
        """Release mouse button."""
        if self.active_method == InputMethod.INTERCEPTION and self.interception_available:
            if self._send_interception_click(button, False):
                return

        flags_map = {
            "left": MOUSEEVENTF_LEFTUP,
            "right": MOUSEEVENTF_RIGHTUP,
            "middle": MOUSEEVENTF_MIDDLEUP,
        }
        flags = flags_map.get(button, MOUSEEVENTF_LEFTUP)

        if self.active_method == InputMethod.MOUSE_EVENT:
            self._send_mouse_event_legacy(flags)
        else:
            self._send_mouse_input(flags)

    def click(self, button: str = "left"):
        """Perform a mouse click (down + up)."""
        self.mouse_down(button)
        # Small delay between down and up for realism
        time.sleep(0.01 + (time.time() % 0.02))  # 10-30ms random
        self.mouse_up(button)

    def move_to(self, x: int, y: int, absolute: bool = True):
        """Move mouse to position."""
        if absolute:
            abs_x, abs_y = self._to_absolute(x, y)
            flags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
            if self.active_method == InputMethod.MOUSE_EVENT:
                self._send_mouse_event_legacy(flags, abs_x, abs_y)
            else:
                self._send_mouse_input(flags, abs_x, abs_y)
        else:
            # Relative movement
            flags = MOUSEEVENTF_MOVE
            if self.active_method == InputMethod.MOUSE_EVENT:
                self._send_mouse_event_legacy(flags, x, y)
            else:
                self._send_mouse_input(flags, x, y)

    def _send_key_input(self, vk: int, scan: int, down: bool):
        """Send keyboard input using SendInput with scan codes."""
        extra = ctypes.pointer(wintypes.ULONG(0))
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.union.ki.wVk = 0  # Use scan code only for better compatibility
        inp.union.ki.wScan = scan
        inp.union.ki.dwFlags = KEYEVENTF_SCANCODE | (0 if down else KEYEVENTF_KEYUP)
        inp.union.ki.time = 0
        inp.union.ki.dwExtraInfo = extra

        self.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

    def key_down(self, key: str):
        """Press a key down."""
        key_lower = key.lower()
        vk = self.VK_CODES.get(key_lower, 0)
        scan = self.SCAN_CODES.get(key_lower, 0)

        if scan:
            self._send_key_input(vk, scan, True)
        elif vk:
            # Fallback to VK code if no scan code available
            extra = ctypes.pointer(wintypes.ULONG(0))
            inp = INPUT()
            inp.type = INPUT_KEYBOARD
            inp.union.ki.wVk = vk
            inp.union.ki.wScan = 0
            inp.union.ki.dwFlags = 0
            inp.union.ki.time = 0
            inp.union.ki.dwExtraInfo = extra
            self.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

    def key_up(self, key: str):
        """Release a key."""
        key_lower = key.lower()
        vk = self.VK_CODES.get(key_lower, 0)
        scan = self.SCAN_CODES.get(key_lower, 0)

        if scan:
            self._send_key_input(vk, scan, False)
        elif vk:
            extra = ctypes.pointer(wintypes.ULONG(0))
            inp = INPUT()
            inp.type = INPUT_KEYBOARD
            inp.union.ki.wVk = vk
            inp.union.ki.wScan = 0
            inp.union.ki.dwFlags = KEYEVENTF_KEYUP
            inp.union.ki.time = 0
            inp.union.ki.dwExtraInfo = extra
            self.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

    def key_press(self, key: str):
        """Press and release a key."""
        self.key_down(key)
        time.sleep(0.01 + (time.time() % 0.02))
        self.key_up(key)

    def get_method_name(self) -> str:
        """Get the name of the active input method."""
        return self.active_method.value

    def set_method(self, method: InputMethod):
        """Change the input method."""
        if method == InputMethod.INTERCEPTION and not self.interception_available:
            return False
        self.active_method = method
        return True

    def is_interception_available(self) -> bool:
        """Check if Interception driver is available."""
        return self.interception_available

    def cleanup(self):
        """Cleanup resources."""
        if self.interception_context and self.interception_available:
            try:
                self.interception_dll.interception_destroy_context(self.interception_context)
            except Exception:
                pass


# Singleton instance for easy access
_native_input: Optional[NativeInput] = None


def get_native_input() -> NativeInput:
    """Get or create the native input singleton."""
    global _native_input
    if _native_input is None:
        _native_input = NativeInput(InputMethod.AUTO)
    return _native_input
