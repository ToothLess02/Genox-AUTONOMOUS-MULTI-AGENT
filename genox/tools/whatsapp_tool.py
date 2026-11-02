"""
Genox WhatsApp & Messaging Integration Tool
Specialized tool to automate opening WhatsApp, finding chats, sending messages,
and extracting emails/details from messages with native macOS CoreGraphics precision.
"""

import subprocess
import re
import urllib.parse
import time
import ctypes
import ctypes.util
from genox.tools.base import registry

EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")

# Load macOS CoreGraphics for pixel-perfect event dispatch
try:
    cg = ctypes.cdll.LoadLibrary(ctypes.util.find_library("CoreGraphics"))

    class CGPoint(ctypes.Structure):
        _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]

    cg.CGEventCreateMouseEvent.restype = ctypes.c_void_p
    cg.CGEventCreateMouseEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint32, CGPoint, ctypes.c_uint32]
    cg.CGEventPost.restype = None
    cg.CGEventPost.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
    _CG_AVAILABLE = True
except Exception:
    _CG_AVAILABLE = False


def _robust_mouse_click(x: float, y: float):
    """Dispatch a smooth mouse move followed by left down and up events."""
    if not _CG_AVAILABLE:
        return
    pt = CGPoint(float(x), float(y))
    # 1. Mouse moved (kCGEventMouseMoved = 5)
    move = cg.CGEventCreateMouseEvent(None, 5, pt, 0)
    cg.CGEventPost(0, move)
    time.sleep(0.04)
    # 2. Mouse down (kCGEventLeftMouseDown = 1)
    down = cg.CGEventCreateMouseEvent(None, 1, pt, 0)
    cg.CGEventPost(0, down)
    time.sleep(0.05)
    # 3. Mouse up (kCGEventLeftMouseUp = 2)
    up = cg.CGEventCreateMouseEvent(None, 2, pt, 0)
    cg.CGEventPost(0, up)
    time.sleep(0.04)


def _navigate_to_whatsapp_chat(contact_name_or_number: str) -> tuple[bool, str, dict]:
    """Helper to bring WhatsApp forward, search for contact/number, and select the chat thread."""
    target = contact_name_or_number.strip()
    if not target:
        return False, "Error: Contact name or phone number is required.", {}

    # Check if target is a phone number (>= 7 digits)
    digits_only = re.sub(r"[^\d+]", "", target)
    if len(digits_only) >= 7:
        clean_num = digits_only.replace("+", "")
        url = f"whatsapp://send?phone={clean_num}"
        subprocess.run(["open", url], capture_output=True)
        time.sleep(1.0)
        return True, f"Navigated to phone number {target}", {"is_phone": True}

    # For contact names: atomic AppleScript to reopen, activate, grab geometry, and search
    atomic_script = f"""
    tell application "WhatsApp" to reopen
    tell application "WhatsApp" to activate
    delay 0.5
    tell application "System Events"
        tell process "WhatsApp"
            set frontmost to true
            delay 0.2
            key code 53 -- Esc
            delay 0.1
            key code 53 -- Esc
            delay 0.1
            set w to first window
            set pos to (get position of w)
            set sz to (get size of w)
            -- Focus search field via Cmd+F
            keystroke "f" using {{command down}}
            delay 0.3
            -- Clear previous search query
            keystroke "a" using {{command down}}
            delay 0.1
            key code 51 -- backspace
            delay 0.2
            -- Type target contact name
            keystroke "{target}"
            delay 0.8
            return {{pos, sz}}
        end tell
    end tell
    """
    res = subprocess.run(["osascript", "-e", atomic_script], capture_output=True, text=True)
    nums = [int(x.strip()) for x in res.stdout.strip().split(",") if x.strip().isdigit()]
    wx, wy = (nums[0], nums[1]) if len(nums) >= 2 else (0, 70)
    w_w, w_h = (nums[2], nums[3]) if len(nums) >= 4 else (1280, 762)

    # Click first search result (Chats -> Result 1) located at wx + 250, wy + 180
    _robust_mouse_click(wx + 250, wy + 180)
    time.sleep(0.5)

    # Click inside message composer (bottom right of the window)
    comp_x = wx + min(700, int(w_w * 0.55))
    comp_y = wy + w_h - 35
    _robust_mouse_click(comp_x, comp_y)
    time.sleep(0.3)

    return True, f"Navigated to '{target}' and focused composer.", {
        "is_phone": False,
        "wx": wx,
        "wy": wy,
        "w_w": w_w,
        "w_h": w_h,
        "comp_x": comp_x,
        "comp_y": comp_y
    }


@registry.register
def open_whatsapp_chat(contact_name_or_number: str) -> str:
    """Open WhatsApp on macOS and navigate directly to a specific person's chat.
    
    Args:
        contact_name_or_number: The contact name (e.g. 'cutie', 'Alex', 'John') or phone number with country code.
    
    Returns:
        Status report of the action taken.
    """
    target = contact_name_or_number.strip()
    success, msg, _ = _navigate_to_whatsapp_chat(target)
    if success:
        return f"Successfully opened WhatsApp chat with '{target}'. Chat window and message composer are now active."
    else:
        return f"Failed to open WhatsApp chat with '{target}': {msg}"


@registry.register
def send_whatsapp_message(contact_name_or_number: str, message: str) -> str:
    """Open a specific person's chat on WhatsApp and send them a text message.
    
    Args:
        contact_name_or_number: The contact name (e.g. 'cutie', 'Alex') or phone number with country code.
        message: The text message to send.
        
    Returns:
        Confirmation status of the message sent.
    """
    target = contact_name_or_number.strip()
    msg = message.strip()
    
    if not msg:
        return "Error: Message text cannot be empty."

    digits_only = re.sub(r"[^\d+]", "", target)
    if len(digits_only) >= 7:
        clean_num = digits_only.replace("+", "")
        encoded_msg = urllib.parse.quote(msg)
        url = f"whatsapp://send?phone={clean_num}&text={encoded_msg}"
        subprocess.run(["open", url], capture_output=True)
        time.sleep(1.0)
        # Press Return to send prefilled message
        subprocess.run(["osascript", "-e", 'tell application "System Events" to key code 36'], capture_output=True)
        return f"Successfully sent WhatsApp message to {target}: '{msg}'"

    # 1. Copy message to macOS clipboard first
    proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
    proc.communicate(msg.encode("utf-8"))

    # 2. Navigate to contact chat and focus composer
    success, err_msg, info = _navigate_to_whatsapp_chat(target)
    if not success:
        return f"Could not navigate to WhatsApp contact '{target}': {err_msg}"

    # 3. Paste message via Cmd+V into the focused AXTextArea and press Return to send!
    send_script = """
    tell application "WhatsApp" to activate
    delay 0.2
    tell application "System Events"
        tell process "WhatsApp"
            set frontmost to true
            delay 0.2
            keystroke "v" using {command down}
            delay 0.3
            key code 36
        end tell
    end tell
    """
    res = subprocess.run(["osascript", "-e", send_script], capture_output=True, text=True)
    if res.returncode == 0:
        return f"Successfully sent WhatsApp message to '{target}': '{msg}'"
    else:
        return f"WhatsApp sending noticed an error: {res.stderr.strip()}"


@registry.register
def extract_emails_from_text(text: str = "") -> str:
    """Extract email addresses from a block of text or from the current clipboard.
    
    Args:
        text: Text to scan. If omitted or empty, reads directly from current clipboard.
    
    Returns:
        Found email addresses and formatted report.
    """
    scan_text = text.strip()
    if not scan_text:
        # Read from clipboard
        try:
            res = subprocess.run(["pbpaste"], capture_output=True, text=True, timeout=5)
            scan_text = res.stdout.strip()
        except Exception:
            scan_text = ""
            
    if not scan_text:
        return "No text provided and clipboard is empty. Please provide message text or copy text from WhatsApp first."
        
    emails = EMAIL_REGEX.findall(scan_text)
    unique_emails = list(dict.fromkeys(emails))
    
    if unique_emails:
        return (
            f"Found {len(unique_emails)} email address(es):\n" +
            "\n".join([f"- {e}" for e in unique_emails]) +
            f"\n\nTop candidate email: '{unique_emails[0]}'. "
            "Please call ask_user_confirmation to verify this email address with the user before drafting or sending."
        )
    else:
        return (
            f"No standard email addresses found in the provided content ({len(scan_text)} characters scanned). "
            f"Snippet: '{scan_text[:200]}...'"
        )
