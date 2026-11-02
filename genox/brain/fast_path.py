"""
Genox Fast-Path Intent Engine
Executes common user commands (opening websites, launching apps, system controls)
in <50ms without invoking heavy LLM function calling loops.
"""

import os
import re
import sys
import subprocess
import datetime
from typing import Optional, Dict, Any

URL_SHORTCUTS = {
    "youtube": "https://www.youtube.com",
    "spotify": "https://open.spotify.com",
    "google": "https://www.google.com",
    "github": "https://github.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "chatgpt": "https://chatgpt.com",
    "netflix": "https://www.netflix.com",
    "reddit": "https://www.reddit.com",
    "gmail": "https://mail.google.com",
    "amazon": "https://www.amazon.com",
    "whatsapp": "https://web.whatsapp.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "wikipedia": "https://www.wikipedia.org",
    "facebook": "https://www.facebook.com",
}

APP_SHORTCUTS = {
    "terminal": "Terminal",
    "calculator": "Calculator",
    "notes": "Notes",
    "finder": None,  # handled via open ~
    "safari": "Safari",
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "calendar": "Calendar",
    "music": "Music",
    "apple music": "Music",
    "settings": "System Settings",
    "system settings": "System Settings",
    "mail": "Mail",
    "vscode": "Visual Studio Code",
    "vs code": "Visual Studio Code",
    "code": "Visual Studio Code",
    "messages": "Messages",
    "maps": "Maps",
    "photos": "Photos",
    "preview": "Preview",
    "activity monitor": "Activity Monitor",
    "whatsapp": "WhatsApp",
    "telegram": "Telegram",
    "discord": "Discord",
    "spotify": "Spotify",
}

SEARCH_PLATFORMS = {
    "youtube": {
        "name": "YouTube",
        "url_template": "https://www.youtube.com/results?search_query={query}",
        "aliases": ["youtube", "you tube", "yt"]
    },
    "amazon": {
        "name": "Amazon",
        "url_template": "https://www.amazon.com/s?k={query}",
        "aliases": ["amazon", "amazon.com", "amazon store"]
    },
    "google": {
        "name": "Google",
        "url_template": "https://www.google.com/search?q={query}",
        "aliases": ["google", "google.com"]
    },
    "spotify": {
        "name": "Spotify",
        "url_template": "https://open.spotify.com/search/{query}",
        "aliases": ["spotify"]
    },
    "github": {
        "name": "GitHub",
        "url_template": "https://github.com/search?q={query}",
        "aliases": ["github", "git hub"]
    },
    "reddit": {
        "name": "Reddit",
        "url_template": "https://www.reddit.com/search/?q={query}",
        "aliases": ["reddit"]
    },
    "twitter": {
        "name": "Twitter / X",
        "url_template": "https://x.com/search?q={query}",
        "aliases": ["twitter", "x"]
    },
    "wikipedia": {
        "name": "Wikipedia",
        "url_template": "https://en.wikipedia.org/wiki/Special:Search?search={query}",
        "aliases": ["wikipedia", "wiki"]
    },
    "netflix": {
        "name": "Netflix",
        "url_template": "https://www.netflix.com/search?q={query}",
        "aliases": ["netflix"]
    }
}

ALIAS_TO_PLATFORM = {}
for p_key, p_info in SEARCH_PLATFORMS.items():
    for alias in p_info["aliases"]:
        ALIAS_TO_PLATFORM[alias] = p_key

import urllib.parse

GENERIC_MUSIC_REGEX = re.compile(
    r"^(?:(?:some|any|a|the|top|good|cool|trending|chill|relaxing|background|popular)\s+)?(?:music|songs?|tracks?|tunes?|hits?|playlist|something|anything)(?:\s+(?:for\s+me|please|now))?$",
    re.IGNORECASE
)

def find_installed_macos_app(name: str) -> Optional[str]:
    """Check if an app is installed on macOS in standard app directories."""
    candidates = [
        f"/Applications/{name}.app",
        f"/System/Applications/{name}.app",
        f"/System/Applications/Utilities/{name}.app",
        os.path.expanduser(f"~/Applications/{name}.app")
    ]
    for c in candidates:
        if os.path.exists(c):
            return name
    return None

WAKE_WORD_FINDER_REGEX = re.compile(
    r"\b(?:hey\s+|hi\s+|ok\s+|hello\s+|yo\s+)?(?:genox|geox|xenox|jenox|janox|zenox|ginox|gnox|kenox|knox|jarvis|genius)\b",
    re.IGNORECASE
)

def extract_clean_intent(prompt: str) -> str:
    """Extract clean intent, prioritizing text following the last wake word if multiple exist."""
    raw = prompt.strip()
    matches = list(WAKE_WORD_FINDER_REGEX.finditer(raw))
    if len(matches) > 1:
        # User restarted or re-called wake word, take the final segment
        last_match = matches[-1]
        raw = raw[last_match.end():].strip()
    elif matches:
        raw = raw[matches[0].end():].strip()
    
    clean = raw.lower()
    clean = WAKE_WORD_FINDER_REGEX.sub("", clean)
    # Deduplicate repeated consecutive phrases (e.g. "open youtube open youtube" -> "open youtube")
    clean = re.sub(r"\b([a-z0-9\s]{3,})\s+\1\b", r"\1", clean)
    return clean.strip().rstrip(".!?")

def try_fast_path(prompt: str) -> Optional[Dict[str, Any]]:
    """Check if prompt matches an instant local intent.
    Returns a dict with tool, args, output, and final_response if matched, else None.
    """
    clean = extract_clean_intent(prompt)

    # =========================================================================
    # WhatsApp Direct Messaging & Chat Opening Intents
    # =========================================================================
    # 1. "open <contact> (chat) in/on whatsapp and send/type/say <msg>"
    m_wa1 = re.match(r"^(?:open|launch)\s+([a-z0-9\s\.\-_]+?)\s+(?:chat\s+)?(?:in|on)\s+whatsapp\s+(?:and\s+)?(?:send|type|say|text|message)\s+(.+)$", clean)
    if m_wa1:
        contact = m_wa1.group(1).strip()
        msg = m_wa1.group(2).strip()
        from genox.tools.whatsapp_tool import send_whatsapp_message
        res = send_whatsapp_message(contact, msg)
        return {
            "fast_path": True,
            "tool": "whatsapp_sender",
            "args": {"contact": contact, "message": msg},
            "output": res,
            "final_response": f"Opened chat with **{contact}** on WhatsApp and sent: *\"{msg}\"*"
        }

    # 1b. "in/on whatsapp open <contact> (chat) and send/type/say <msg>"
    m_wa1b = re.match(r"^(?:in|on)\s+whatsapp\s+(?:open|launch)\s+([a-z0-9\s\.\-_]+?)\s+(?:chat\s+)?(?:and\s+)?(?:send|type|say|text|message)\s+(.+)$", clean)
    if m_wa1b:
        contact = m_wa1b.group(1).strip()
        msg = m_wa1b.group(2).strip()
        from genox.tools.whatsapp_tool import send_whatsapp_message
        res = send_whatsapp_message(contact, msg)
        return {
            "fast_path": True,
            "tool": "whatsapp_sender",
            "args": {"contact": contact, "message": msg},
            "output": res,
            "final_response": f"Opened chat with **{contact}** on WhatsApp and sent: *\"{msg}\"*"
        }

    # 2. "send <msg> to <contact> in/on whatsapp"
    m_wa2 = re.match(r"^(?:send|text|message)\s+(.+?)\s+to\s+([a-z0-9\s\.\-_]+?)\s+(?:in|on)\s+whatsapp$", clean)
    if m_wa2:
        msg = m_wa2.group(1).strip()
        contact = m_wa2.group(2).strip()
        from genox.tools.whatsapp_tool import send_whatsapp_message
        res = send_whatsapp_message(contact, msg)
        return {
            "fast_path": True,
            "tool": "whatsapp_sender",
            "args": {"contact": contact, "message": msg},
            "output": res,
            "final_response": f"Opened chat with **{contact}** on WhatsApp and sent: *\"{msg}\"*"
        }

    # 2b. "in/on whatsapp send <msg> to <contact>"
    m_wa2b = re.match(r"^(?:in|on)\s+whatsapp\s+(?:send|text|message)\s+(.+?)\s+to\s+([a-z0-9\s\.\-_]+)$", clean)
    if m_wa2b:
        msg = m_wa2b.group(1).strip()
        contact = m_wa2b.group(2).strip()
        from genox.tools.whatsapp_tool import send_whatsapp_message
        res = send_whatsapp_message(contact, msg)
        return {
            "fast_path": True,
            "tool": "whatsapp_sender",
            "args": {"contact": contact, "message": msg},
            "output": res,
            "final_response": f"Opened chat with **{contact}** on WhatsApp and sent: *\"{msg}\"*"
        }

    # 2c. "send <contact> a message in/on whatsapp saying/with/that <msg>"
    m_wa2c = re.match(r"^(?:send|text)\s+([a-z0-9\s\.\-_]+?)\s+(?:a\s+)?(?:message|text)?\s*(?:in|on)\s+whatsapp\s+(?:saying|with|that)\s+(.+)$", clean)
    if m_wa2c:
        contact = m_wa2c.group(1).strip()
        msg = m_wa2c.group(2).strip()
        from genox.tools.whatsapp_tool import send_whatsapp_message
        res = send_whatsapp_message(contact, msg)
        return {
            "fast_path": True,
            "tool": "whatsapp_sender",
            "args": {"contact": contact, "message": msg},
            "output": res,
            "final_response": f"Opened chat with **{contact}** on WhatsApp and sent: *\"{msg}\"*"
        }

    # 3. "open whatsapp and send/text/message <msg> to <contact>"
    m_wa3 = re.match(r"^(?:open|launch)\s+whatsapp\s+(?:and\s+)?(?:send|text|message)\s+(.+?)\s+to\s+([a-z0-9\s\.\-_]+)$", clean)
    if m_wa3:
        msg = m_wa3.group(1).strip()
        contact = m_wa3.group(2).strip()
        from genox.tools.whatsapp_tool import send_whatsapp_message
        res = send_whatsapp_message(contact, msg)
        return {
            "fast_path": True,
            "tool": "whatsapp_sender",
            "args": {"contact": contact, "message": msg},
            "output": res,
            "final_response": f"Opened chat with **{contact}** on WhatsApp and sent: *\"{msg}\"*"
        }

    # 4. "open <contact> (chat) in/on whatsapp" (open chat only)
    m_wa4 = re.match(r"^(?:open|launch|go\s+to)\s+([a-z0-9\s\.\-_]+?)\s+(?:chat\s+)?(?:in|on)\s+whatsapp$", clean)
    if m_wa4 and m_wa4.group(1).strip() not in ("the", "a", "my"):
        contact = m_wa4.group(1).strip()
        from genox.tools.whatsapp_tool import open_whatsapp_chat
        res = open_whatsapp_chat(contact)
        return {
            "fast_path": True,
            "tool": "whatsapp_chat_opener",
            "args": {"contact": contact},
            "output": res,
            "final_response": f"Opened WhatsApp chat with **{contact}** for you."
        }

    # 4b. "in/on whatsapp open <contact> (chat)"
    m_wa4b = re.match(r"^(?:in|on)\s+whatsapp\s+(?:open|launch|go\s+to)\s+([a-z0-9\s\.\-_]+?)(?:\s+chat)?$", clean)
    if m_wa4b and m_wa4b.group(1).strip() not in ("the", "a", "my"):
        contact = m_wa4b.group(1).strip()
        from genox.tools.whatsapp_tool import open_whatsapp_chat
        res = open_whatsapp_chat(contact)
        return {
            "fast_path": True,
            "tool": "whatsapp_chat_opener",
            "args": {"contact": contact},
            "output": res,
            "final_response": f"Opened WhatsApp chat with **{contact}** for you."
        }

    # 0. Match Direct Multi-Platform Search Intents (e.g. "open youtube and search valorant", "search shoes on amazon")
    search_target = None

    # Pattern 1: "open <platform> and search/find/play (for) <query>" or "open <platform> search <query>"
    m1 = re.match(r"^(?:open|launch|go\s+to|visit)\s+([a-z0-9\.\s]+?)\s+(?:and\s+)?(?:search(?:\s+for)?|find|look\s+up|play)\s+(.+)$", clean)
    if m1:
        plat_raw = m1.group(1).replace("the ", "").strip()
        query = m1.group(2).strip()
        if plat_raw in ALIAS_TO_PLATFORM:
            search_target = (ALIAS_TO_PLATFORM[plat_raw], query)

    # Pattern 2: "search/look up/find (for) <query> on/in <platform>"
    if not search_target:
        m2 = re.match(r"^(?:search(?:\s+for)?|look\s+up|find)\s+(.+?)\s+(?:on|in)\s+([a-z0-9\.\s]+)$", clean)
        if m2:
            query = m2.group(1).strip()
            plat_raw = m2.group(2).replace("the ", "").strip()
            if plat_raw in ALIAS_TO_PLATFORM:
                search_target = (ALIAS_TO_PLATFORM[plat_raw], query)

    # Pattern 3: "play <query> on/in <platform>"
    if not search_target:
        m3 = re.match(r"^play\s+(.+?)\s+(?:on|in)\s+([a-z0-9\.\s]+)$", clean)
        if m3:
            query = m3.group(1).strip()
            plat_raw = m3.group(2).replace("the ", "").strip()
            if plat_raw in ALIAS_TO_PLATFORM:
                search_target = (ALIAS_TO_PLATFORM[plat_raw], query)

    # Pattern 4: "<platform> search (for) <query>"
    if not search_target:
        m4 = re.match(r"^([a-z0-9\.\s]+?)\s+search(?:\s+for)?\s+(.+)$", clean)
        if m4:
            plat_raw = m4.group(1).replace("the ", "").strip()
            query = m4.group(2).strip()
            if plat_raw in ALIAS_TO_PLATFORM:
                search_target = (ALIAS_TO_PLATFORM[plat_raw], query)

    # Pattern 5: "play <query>" (default to YouTube)
    if not search_target:
        m5 = re.match(r"^play\s+(.+)$", clean)
        if m5:
            query = m5.group(1).strip()
            search_target = ("youtube", query)

    # Pattern 6: "search (for) <query>" or "google <query>" (default to Google)
    if not search_target:
        m6 = re.match(r"^(?:search(?:\s+for)?|google)\s+(.+)$", clean)
        if m6:
            query = m6.group(1).strip()
            search_target = ("google", query)

    if search_target:
        plat_key, query = search_target
        plat_info = SEARCH_PLATFORMS[plat_key]
        clean_q = query.strip()
        is_generic_music = bool(GENERIC_MUSIC_REGEX.match(clean_q))

        # Specialized handling for Spotify
        if plat_key == "spotify":
            spotify_app = find_installed_macos_app("Spotify")
            if is_generic_music:
                if spotify_app:
                    cmd = 'open -a "Spotify" && osascript -e "tell application \\"Spotify\\" to play"'
                    subprocess.run(["open", "-a", "Spotify"], capture_output=True)
                    subprocess.run(["osascript", "-e", 'tell application "Spotify" to play'], capture_output=True)
                    return {
                        "fast_path": True,
                        "tool": "bash_executor",
                        "args": {"command": cmd},
                        "output": "Opened Spotify desktop application and started playback.",
                        "final_response": "Opened **Spotify** and started playing music for you."
                    }
                else:
                    search_url = "https://open.spotify.com"
                    cmd = f'open "{search_url}"'
                    subprocess.run(["open", search_url], capture_output=True, text=True)
                    return {
                        "fast_path": True,
                        "tool": "bash_executor",
                        "args": {"command": cmd},
                        "output": f"Opened {search_url} in your default browser.",
                        "url": search_url,
                        "final_response": "Opened **Spotify** in your browser ready to play music. (Spotify desktop app is not installed, so launched Spotify Web Player)."
                    }
            else:
                if spotify_app:
                    cmd = f'open "spotify:search:{urllib.parse.quote(clean_q)}"'
                    subprocess.run(["open", f"spotify:search:{urllib.parse.quote(clean_q)}"], capture_output=True)
                    return {
                        "fast_path": True,
                        "tool": "bash_executor",
                        "args": {"command": cmd},
                        "output": f"Opened Spotify desktop app and searching for {clean_q}.",
                        "final_response": f"Opened **Spotify** and searching for **{clean_q}**."
                    }
                else:
                    encoded = urllib.parse.quote_plus(clean_q)
                    search_url = f"https://open.spotify.com/search/{encoded}"
                    cmd = f'open "{search_url}"'
                    subprocess.run(["open", search_url], capture_output=True, text=True)
                    return {
                        "fast_path": True,
                        "tool": "bash_executor",
                        "args": {"command": cmd},
                        "output": f"Opened {search_url} in your default browser.",
                        "url": search_url,
                        "final_response": f"Searching for **{clean_q}** on **Spotify** in your browser right now."
                    }

        # Specialized handling for YouTube generic music
        if plat_key == "youtube" and is_generic_music:
            search_url = "https://www.youtube.com/results?search_query=trending+music"
            cmd = f'open "{search_url}"'
            subprocess.run(["open", search_url], capture_output=True, text=True)
            return {
                "fast_path": True,
                "tool": "bash_executor",
                "args": {"command": cmd},
                "output": f"Opened {search_url} in your default browser.",
                "url": search_url,
                "final_response": "Playing trending music on **YouTube** in your browser right now."
            }

        # General platform search
        encoded = urllib.parse.quote_plus(clean_q)
        search_url = plat_info["url_template"].format(query=encoded)
        cmd = f'open "{search_url}"'
        subprocess.run(["open", search_url], capture_output=True, text=True)
        return {
            "fast_path": True,
            "tool": "bash_executor",
            "args": {"command": cmd},
            "output": f"Opened {search_url} in your default browser.",
            "url": search_url,
            "final_response": f"Searching for **{clean_q}** on **{plat_info['name']}** in your browser right now."
        }

    # 1. Match "open <target>" / "launch <target>" / "go to <target>"
    open_match = re.match(r"^(?:open|launch|start|go\s+to|visit)\s+(.+)$", clean)
    if open_match:
        target = open_match.group(1).strip()
        target_norm = target.replace("the ", "").strip()

        # Check if desktop application exists locally first (e.g. WhatsApp, Discord, Spotify)
        if target_norm in APP_SHORTCUTS:
            app_name = APP_SHORTCUTS[target_norm]
            if app_name is None and target_norm == "finder":
                cmd = 'open ~'
                subprocess.run(["open", os.path.expanduser("~")], capture_output=True, text=True)
                return {
                    "fast_path": True,
                    "tool": "bash_executor",
                    "args": {"command": cmd},
                    "output": "Opened Finder in home directory.",
                    "final_response": "Opened **Finder** for you."
                }
            elif app_name:
                installed = find_installed_macos_app(app_name)
                if installed:
                    cmd = f'open -a "{app_name}"'
                    subprocess.run(["open", "-a", app_name], capture_output=True, text=True)
                    return {
                        "fast_path": True,
                        "tool": "bash_executor",
                        "args": {"command": cmd},
                        "output": f"Launched {app_name}.",
                        "final_response": f"Launched **{app_name}** on your Mac."
                    }
                # If app not installed locally, fall through to website shortcut below

        # Check website shortcut
        if target_norm in URL_SHORTCUTS:
            url = URL_SHORTCUTS[target_norm]
            cmd = f'open "{url}"'
            subprocess.run(["open", url], capture_output=True, text=True)
            return {
                "fast_path": True,
                "tool": "bash_executor",
                "args": {"command": cmd},
                "output": f"Opened {url} in your default browser.",
                "url": url,
                "final_response": f"Opening **{target_norm.capitalize()}** in your browser right now."
            }

        # Check full URL
        if target.startswith("http://") or target.startswith("https://") or (target.endswith(".com") or target.endswith(".org") or target.endswith(".net") or target.endswith(".io")):
            url = target if target.startswith("http") else f"https://{target}"
            cmd = f'open "{url}"'
            subprocess.run(["open", url], capture_output=True, text=True)
            return {
                "fast_path": True,
                "tool": "bash_executor",
                "args": {"command": cmd},
                "output": f"Opened {url} in your default browser.",
                "url": url,
                "final_response": f"Opening **{url}** for you."
            }

        # Check macOS App shortcut fallback if not in URL shortcuts
        if target_norm in APP_SHORTCUTS:
            app_name = APP_SHORTCUTS[target_norm]
            if app_name:
                cmd = f'open -a "{app_name}"'
                subprocess.run(["open", "-a", app_name], capture_output=True, text=True)
                return {
                    "fast_path": True,
                    "tool": "bash_executor",
                    "args": {"command": cmd},
                    "output": f"Launched {app_name}.",
                    "final_response": f"Launched **{app_name}** on your Mac."
                }
            if app_name is None and target_norm == "finder":
                cmd = 'open ~'
                subprocess.run(["open", os.path.expanduser("~")], capture_output=True, text=True)
                return {
                    "fast_path": True,
                    "tool": "bash_executor",
                    "args": {"command": cmd},
                    "output": "Opened Finder in home directory.",
                    "final_response": "Opened **Finder** for you."
                }
            elif app_name:
                cmd = f'open -a "{app_name}"'
                subprocess.run(["open", "-a", app_name], capture_output=True, text=True)
                return {
                    "fast_path": True,
                    "tool": "bash_executor",
                    "args": {"command": cmd},
                    "output": f"Launched {app_name}.",
                    "final_response": f"Launched **{app_name}** on your Mac."
                }

    # 2. Match Time and Date Queries
    if clean in ("what time is it", "what's the time", "current time", "tell me the time", "time"):
        now_str = datetime.datetime.now().strftime("%I:%M:%S %p")
        return {
            "fast_path": True,
            "tool": "bash_executor",
            "args": {"command": "date +%r"},
            "output": now_str,
            "final_response": f"The current time is **{now_str}**."
        }

    if clean in ("what date is it", "what's the date", "today's date", "what is today's date", "date"):
        date_str = datetime.datetime.now().strftime("%A, %B %d, %Y")
        return {
            "fast_path": True,
            "tool": "bash_executor",
            "args": {"command": "date '+%A, %B %d, %Y'"},
            "output": date_str,
            "final_response": f"Today is **{date_str}**."
        }

    # 3. Match Battery Query
    if clean in ("battery", "battery percentage", "battery level", "check battery", "what is my battery", "how much battery"):
        res = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True)
        out = res.stdout.strip()
        pct_match = re.search(r"(\d+%)", out)
        pct = pct_match.group(1) if pct_match else "Status available"
        state = "Charging" if "charging" in out.lower() else "On Battery"
        return {
            "fast_path": True,
            "tool": "bash_executor",
            "args": {"command": "pmset -g batt"},
            "output": out,
            "final_response": f"Battery is at **{pct}** ({state}).\n\n```\n{out}\n```"
        }

    # 4. Match System Volume controls
    if clean in ("mute", "mute volume", "mute mac", "turn off sound"):
        subprocess.run(["osascript", "-e", "set volume output muted true"], capture_output=True)
        return {
            "fast_path": True,
            "tool": "bash_executor",
            "args": {"command": 'osascript -e "set volume output muted true"'},
            "output": "System muted.",
            "final_response": "macOS volume is now **muted**."
        }
    if clean in ("unmute", "unmute volume", "unmute sound"):
        subprocess.run(["osascript", "-e", "set volume output muted false"], capture_output=True)
        return {
            "fast_path": True,
            "tool": "bash_executor",
            "args": {"command": 'osascript -e "set volume output muted false"'},
            "output": "System unmuted.",
            "final_response": "macOS volume is now **unmuted**."
        }

    return None
