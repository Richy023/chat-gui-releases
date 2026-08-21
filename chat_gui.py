#!/usr/bin/env python3
"""
chat_gui.py — v1.4.5a — ENCRYPTED instant messenger with a desktop GUI.

Fixes/features in this version:
- Custom sticker upload: pick an image, name it, it's converted to JPEG
  and saved locally (chat_gui_stickers.json) so it persists across
  sessions — no re-uploading every time. Shown as thumbnails in the
  picker alongside the built-ins; right-click a custom one to delete it.
- Guests now see "You joined Room ... as ..." immediately on connecting,
  instead of a blank chat box until someone else sends a message.
- /mute, /kick, /ban suggestions now rank whoever's sent the most
  messages recently (last 60s) first — usually who you're about to
  target. @ ping suggestions rank whoever's gone longest without
  sending a message first (never-spoken users rank highest of all).
- Fixed macOS DND keybinds: Command was being detected/labeled as Alt
  (so a Command-based bind never actually matched a real Command press
  on Mac — not just a display bug), and Option was corrupting the
  captured key through its own accent/dead-key composition. Both fixed
  via correct Mac modifier names and a stable keycode-based fallback —
  not verified on a real Mac, worth double-checking on your end.

Fixes in 1.4.4d:
- DND keybind picker can now be reopened after already setting a
  non-default bind once, instead of requiring an app restart.
- A letter-key DND bind no longer also types that letter into the chat box.
- Clicking a slash-command suggestion now actually inserts it, instead of
  just making the suggestion box vanish — and no longer leaves the chat
  box stuck/unresponsive on Mac afterward.
- Fixed the room code on the host setup screen showing unreadable
  white-on-white text (Tk's readonly-state background wasn't set).

Fixes in 1.4.4a:
- Added an in-app Changelog viewer (see the "View Changelog" link on the
  connect screen) — shows version, install date, and release notes for
  every version, including anything installed later via OTA.
- Slowmode now shows a live countdown above the chat box while the input
  is locked ("Slowmode is active, you cannot send messages for X.Xs"),
  instead of just silently disabling it with no explanation.

Fixes in 1.4.4:
- Version strings can now carry an optional trailing letter (e.g. 1.4.2c)
  for small QOL patches that don't warrant a full numeric bump; the
  updater sorts these correctly (1.4.2 < 1.4.2a < ... < 1.4.2d < 1.4.3).
- Mute now actually lifts on its own when the timer runs out, instead of
  leaving the input box stuck disabled until an explicit /unmute.
- Moderating the host (/mute, /unmute, /kick, /ban, /admin, /unadmin) now
  replies "You cannot <action> the host." instead of the misleading
  "No one named '<host>' is connected." (the host was never in the
  guest-socket table those commands were checking).

Fixes in 1.4.2:
- Added an in-app, signature-verified update checker (see UPDATE_MANIFEST_URL below).
- Minor UI/UX polish and cleanup pass.

Fixes in 1.4.1:
- Added 🛡️ [Admin Log] broadcasting so admins can see each other's moderation actions in real-time.
- Optimized live suggestion evaluating with sets and comprehensions.
- Refactored UI toggle states to DRY up Slowmode & Mute logic.
- Optimized ping targeting string searches.
"""

import sys
import os
import io
import socket
import threading
import queue
import time
import re
import random
import base64
import hashlib
import importlib
import subprocess
import json
import shutil
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog

# FEATURE TOGGLE: WAN (Wide Area Network) / Global Room Support
ENABLE_WAN_RELAY = False

def ensure_installed(import_name, pip_name=None, required=True):
    pip_name = pip_name or import_name
    try:
        module = importlib.import_module(import_name)
        return module
    except ImportError:
        pass

    print(f"[deps] {pip_name}: not found — installing automatically...")
    attempts = [
        [sys.executable, "-m", "pip", "install", "-q", pip_name],
        [sys.executable, "-m", "pip", "install", "-q", "--user", pip_name],
        [sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", pip_name],
    ]
    for cmd in attempts:
        try:
            subprocess.check_call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            return importlib.import_module(import_name)
        except Exception:
            continue
    if required:
        sys.exit(1)
    return None

ensure_installed("cryptography")
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

ensure_installed("plyer", required=False)
try:
    from plyer import notification as _plyer_notification
except ImportError:
    _plyer_notification = None

ensure_installed("PIL", pip_name="Pillow", required=False)
try:
    from PIL import Image, ImageTk, ImageDraw
except ImportError:
    Image = None
    ImageTk = None
    ImageDraw = None

if sys.platform == "darwin":
    ensure_installed("pyobjus", required=False)

VERSION = "1.4.5a"
MSG_LEN_BYTES = 4
MAX_GUESTS = 4
MAX_FILE_BYTES = 500 * 1024 * 1024 # 500MB Limit
DND_ANNOUNCE_COOLDOWN = 2.0
SPAM_SUGGESTION_WINDOW = 60.0  # seconds — how far back "recent" message activity counts for /mute /kick /ban suggestion ranking

# macOS reports physical key presses via event.keycode using Apple's
# stable "virtual keycode" numbering (same across all Mac hardware,
# unaffected by keyboard layout or which modifiers are held) — unlike
# event.keysym, which the Option key can corrupt into an entirely
# different character via Unicode composition (e.g. Option+e can dead-key
# into an accented letter instead of reporting a clean "e"). Used only
# as a fallback when Option is held, to recover the actual key pressed.
MAC_VIRTUAL_KEYCODE_TO_KEY = {
    0x00: "a", 0x0B: "b", 0x08: "c", 0x02: "d", 0x0E: "e", 0x03: "f",
    0x05: "g", 0x04: "h", 0x22: "i", 0x26: "j", 0x28: "k", 0x25: "l",
    0x2E: "m", 0x2D: "n", 0x1F: "o", 0x23: "p", 0x0C: "q", 0x0F: "r",
    0x01: "s", 0x11: "t", 0x20: "u", 0x09: "v", 0x0D: "w", 0x07: "x",
    0x10: "y", 0x06: "z",
    0x1D: "0", 0x12: "1", 0x13: "2", 0x14: "3", 0x15: "4", 0x17: "5",
    0x16: "6", 0x1A: "7", 0x1C: "8", 0x19: "9",
}
DISCOVERY_PORT = 5005

# ---- OTA updates ----
# Point this at a JSON manifest you host over HTTPS (e.g. a raw GitHub
# URL). Left empty, the in-app "Check for Updates" link just tells the
# user it isn't configured yet — it never fails silently or phones
# home on its own. See sign_release.py / generate_signing_key.py for
# how to produce a manifest and keep the signing key itself OFFLINE —
# only the public key belongs in this file.
UPDATE_MANIFEST_URL = "https://raw.githubusercontent.com/Richy023/chat-gui-releases/main/update_manifest.json"
UPDATE_PUBLIC_KEY_B64 = "buYuGiOKh5LYltgmbUH9S63A10/DGcuyGWz9PzZp85A="

TYPING_IDLE_TIMEOUT = 2
TYPING_DISPLAY_TIMEOUT = 2.0  

if sys.platform == "win32":
    CHAT_FONT = ("Segoe UI", 10)
    BOLD_FONT = ("Segoe UI", 10, "bold")
    TITLE_FONT = ("Segoe UI", 11, "bold")
    EMOJI_FONT = ("Segoe UI Emoji", 14)
elif sys.platform == "darwin":
    CHAT_FONT = ("Helvetica Neue", 12)
    BOLD_FONT = ("Helvetica Neue", 12, "bold")
    TITLE_FONT = ("Helvetica Neue", 13, "bold")
    EMOJI_FONT = ("Apple Color Emoji", 16)
else:
    CHAT_FONT = ("DejaVu Sans", 10)
    BOLD_FONT = ("DejaVu Sans", 10, "bold")
    TITLE_FONT = ("DejaVu Sans", 11, "bold")
    EMOJI_FONT = ("Noto Color Emoji", 14)

# Network Prefixes
HELLO_PREFIX = "__HELLO__:"
TYPING_START_PREFIX = "__TYPING_START__:"
TYPING_STOP_PREFIX = "__TYPING_STOP__:"
PING_PREFIX = "__PING__:"
MUTE_NOTICE_PREFIX = "__MUTE_NOTICE__:"
MUTE_STATUS_PREFIX = "__MUTE_STATUS__:"
NOTICE_PREFIX = "__NOTICE__:"
ROSTER_PREFIX = "__ROSTER__:"
COLORMAP_PREFIX = "__COLORMAP__:"
FILE_PREFIX = "__FILE__:"
DND_PREFIX = "__DND__:"
CMD_PREFIX = "__CMD__:"
HOST_DISCONNECT_PREFIX = "__HOST_DISCONNECT__"
BAN_NOTICE_PREFIX = "__BANNED__:"
KICK_NOTICE_PREFIX = "__KICKED__:"
ADMIN_NOTICE_PREFIX = "__ADMIN_UPDATE__:"
ADMIN_LOG_PREFIX = "__ADMIN_LOG__:"
SLOWMODE_PREFIX = "__SLOWMODE__:"
MSG_PREFIX = "__MSG__:"
REACT_PREFIX = "__REACT__:"

EMOJI_PICKER_SET = [
    "😀", "😂", "😅", "😊", "😉", "😍", "😘", "😜", "🤔", "😎",
    "😢", "😭", "😡", "😱", "🥳", "😴", "🤢", "🤯", "🥶", "🤗",
    "👍", "👎", "👏", "🙏", "💪", "🤝", "👋", "✌️", "🤞", "👀",
    "❤️", "💔", "🔥", "✨", "🎉", "🎂", "⭐", "☀️", "🌙", "⚡",
    "🐶", "🐱", "🍕", "🍔", "☕", "🍺", "⚽", "🎮", "📚", "💻",
]

HOST_COLOR = "#FFFFFF"
COLOR_PALETTE = {
    "red": "#ED4245",
    "green": "#57F287",
    "yellow": "#FEE75C",
    "blue": "#5B8CFF",
    "magenta": "#EB459E",
    "cyan": "#00C8C8",
    "orange": "#FFA347",
}

BG_DARK = "#313338"
BG_PANEL = "#2B2D31"
BG_INPUT = "#383A40"
FG_TEXT = "#DBDEE1"
FG_MUTED = "#949BA4"
BTN_GREEN = "#248046"
BTN_GREEN_HOVER = "#1B6338"
BTN_BLUE_HOVER = "#4752C4"
BTN_RED = "#DA373C"
BTN_RED_HOVER = "#A12D2F"
BTN_NEUTRAL = "#4E5058"
BTN_NEUTRAL_HOVER = "#6D6F78"

def clean_non_bmp(s: str) -> str:
    return s

def derive_key(passphrase: str) -> bytes:
    digest = hashlib.sha256(passphrase.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)

def generate_room_code(local_ip: str = None) -> str:
    ip = local_ip or get_local_ip()
    parts = ip.split(".")
    try:
        octet3, octet4 = int(parts[2]), int(parts[3])
        if 0 <= octet3 <= 255 and 0 <= octet4 <= 255:
            return f"{octet3:03d}{octet4:03d}"
    except (ValueError, IndexError):
        pass
    rng = random.SystemRandom()
    return f"{rng.randint(0, 255):03d}{rng.randint(1, 254):03d}"

def send_encrypted(sock: socket.socket, fernet: Fernet, plaintext: str):
    token = fernet.encrypt(plaintext.encode("utf-8", errors="surrogatepass"))
    length = len(token).to_bytes(MSG_LEN_BYTES, "big")
    sock.sendall(length + token)

def recv_exact(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("peer closed connection")
        buf += chunk
    return buf

def recv_message(sock: socket.socket, fernet: Fernet) -> str:
    length = int.from_bytes(recv_exact(sock, MSG_LEN_BYTES), "big")
    token = recv_exact(sock, length)
    return fernet.decrypt(token).decode("utf-8", errors="surrogatepass")

def extract_ping_target(text: str, known_names):
    mentions = re.findall(r"@(\w+)", text)
    if not mentions:
        return None, None
    lower_names = {n.lower(): n for n in known_names}
    for candidate in mentions:
        if candidate.lower() in lower_names:
            return lower_names[candidate.lower()], candidate
    return None, mentions[0]

def format_time(ts: float) -> str:
    if ts == float('inf'):
        return "permanently"
    return time.strftime("%H:%M:%S", time.localtime(ts))

def notify_ping(pinger_name: str, root=None):
    if _plyer_notification is not None:
        try:
            _plyer_notification.notify(title="Ping Received", message=f"{pinger_name} mentioned you!", timeout=5)
            return
        except Exception:
            pass
    if root is not None:
        try: root.bell()
        except Exception: pass

def get_local_ip() -> str:
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.settimeout(0.2)
        probe.connect(("8.8.8.8", 80))
        ip = probe.getsockname()[0]
        probe.close()
        return ip
    except OSError:
        return "127.0.0.1"

def _guess_broadcast_addresses() -> set:
    addrs = {"255.255.255.255"}
    local_ip = get_local_ip()
    parts = local_ip.split(".")
    if len(parts) == 4 and local_ip != "127.0.0.1":
        addrs.add(".".join(parts[:3]) + ".255")
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
            ip = info[4][0]
            if ip.startswith("127.") or ip in addrs:
                continue
            ip_parts = ip.split(".")
            if len(ip_parts) == 4:
                addrs.add(".".join(ip_parts[:3]) + ".255")
    except OSError:
        pass
    return addrs

def _local_subnet_hosts(local_ip: str) -> list:
    parts = local_ip.split(".")
    if len(parts) != 4 or local_ip == "127.0.0.1":
        return []
    try: network = [int(p) for p in parts[:3]]
    except ValueError: return []
    return [".".join(str(o) for o in network) + f".{h}" for h in range(1, 255)]

def discover_host(room_code: str, target_ip: str = None, timeout: float = 4.0) -> tuple[str, int]:
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_sock.settimeout(0.5)

    msg = f"DISCOVER:{room_code}".encode('utf-8')
    targets = {target_ip} if target_ip else (_guess_broadcast_addresses() | set(_local_subnet_hosts(get_local_ip())))
    deadline = time.time() + timeout
    
    try:
        while time.time() < deadline:
            for addr in targets:
                try: udp_sock.sendto(msg, (addr, DISCOVERY_PORT))
                except OSError: pass
            try:
                data, addr = udp_sock.recvfrom(1024)
                resp = data.decode('utf-8')
                if resp.startswith("OFFER:"):
                    return addr[0], int(resp.split(":")[1])
            except (socket.timeout, OSError):
                continue
    except ValueError:
        pass
    finally:
        udp_sock.close()
    return None, None


# ---- OTA update helpers ----
# Design notes: the ONLY thing that makes an update trustworthy is the
# Ed25519 signature check in verify_update_payload — the sha256 check
# is just an early, cheap integrity check (catches truncated/corrupted
# downloads), not a security boundary, since an attacker controlling
# the download could recompute a matching hash for their own payload.
# HTTPS is required on every URL to stop a network-level swap of the
# manifest or the payload in transit. Nothing here executes anything —
# apply_update() only ever writes bytes that already passed signature
# verification, and the caller (ChatApp) always requires an explicit
# user click before either downloading or restarting.

def _https_get(url: str, timeout: float) -> bytes:
    if not url.lower().startswith("https://"):
        raise ValueError("Refusing to fetch an update over a non-HTTPS URL.")
    req = urllib.request.Request(url, headers={"User-Agent": f"chat_gui/{VERSION}"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

def fetch_update_manifest(manifest_url: str) -> dict:
    raw = _https_get(manifest_url, timeout=10.0)
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"Update manifest wasn't valid JSON: {e}")
    missing = [k for k in ("version", "url", "sha256", "signature") if k not in manifest]
    if missing:
        raise ValueError(f"Update manifest is missing required field(s): {', '.join(missing)}")
    return manifest

def _parse_version_segment(seg: str) -> tuple:
    """'2' -> (2, ''), '2c' -> (2, 'c'). Lets a release use a trailing
    letter (recommended: a-d) for a small QOL patch that doesn't
    deserve a full numeric bump, while still sorting correctly against
    plain numeric versions: 1.4.2 < 1.4.2a < 1.4.2b < ... < 1.4.3."""
    seg = seg.strip()
    m = re.match(r"^(\d+)([a-zA-Z]?)$", seg)
    if not m:
        digits = "".join(ch for ch in seg if ch.isdigit())
        return (int(digits) if digits else 0, "")
    return (int(m.group(1)), m.group(2).lower())

def _version_tuple(v: str) -> tuple:
    return tuple(_parse_version_segment(p) for p in str(v).strip().split("."))

def is_newer_version(remote: str, local: str) -> bool:
    return _version_tuple(remote) > _version_tuple(local)

def verify_update_payload(payload: bytes, manifest: dict):
    """Raises ValueError on any failure. No partial/soft-pass outcome —
    either this returns cleanly or the update must not be installed."""
    expected_hash = str(manifest["sha256"]).strip().lower()
    actual_hash = hashlib.sha256(payload).hexdigest()
    if actual_hash != expected_hash:
        raise ValueError("The downloaded update failed its checksum check (corrupted or tampered download).")

    if not UPDATE_PUBLIC_KEY_B64:
        raise ValueError("No update signing key is configured — refusing to install an unverifiable update.")

    try:
        pubkey = Ed25519PublicKey.from_public_bytes(base64.b64decode(UPDATE_PUBLIC_KEY_B64))
        signature = base64.b64decode(manifest["signature"])
        pubkey.verify(signature, payload)
    except InvalidSignature:
        raise ValueError("Update signature is INVALID — refusing to install. This update may not be authentic.")
    except Exception as e:
        raise ValueError(f"Could not verify the update signature: {e}")

def download_and_verify_update(manifest: dict) -> bytes:
    payload = _https_get(manifest["url"], timeout=30.0)
    verify_update_payload(payload, manifest)
    return payload

def apply_update(payload: bytes) -> str:
    """Only ever called after verify_update_payload() has already
    succeeded. Backs up the running script before overwriting it, and
    writes via a temp file + atomic replace so a crash mid-write can't
    leave a half-written, unrunnable script behind."""
    target_path = os.path.abspath(__file__)
    backup_path = f"{target_path}.bak-{int(time.time())}"
    shutil.copy2(target_path, backup_path)
    tmp_path = f"{target_path}.update_tmp"
    with open(tmp_path, "wb") as f:
        f.write(payload)
    os.replace(tmp_path, target_path)
    return backup_path


# ---- Changelog ----
# EMBEDDED_CHANGELOG is the static release history baked into this
# build — add one entry per release when you bump VERSION. Anything
# installed via OTA *after* this build additionally gets appended to
# CHANGELOG_FILE (a small local JSON file next to the script) at
# install time, so the in-app viewer stays complete going forward
# without needing the whole history re-embedded on every release.
EMBEDDED_CHANGELOG = [
    {   "version": "1.4.5a",
        "date": "2026-08-21",
        "notes": (
            "Fixed major bug fixes in 1.4.5"
        ),
    },
    {   "version": "1.4.5",
        "date": "2026-08-21",
        "notes": (
            "Stickers can now be uploaded (image -> JPEG, with a name you pick) and "
            "are saved locally so you don't need to re-upload them every session — "
            "the sticker picker shows your saved ones as thumbnails alongside the "
            "built-ins, and right-click deletes one. Guests now see a 'You joined "
            "Room...' message immediately instead of an empty chat box. /mute, "
            "/kick, and /ban suggestions now put whoever's been most active "
            "recently first; @ ping suggestions put whoever's been quiet the "
            "longest first. Fixed macOS DND keybinds: Command was being detected "
            "as Alt (so Command-based binds never actually fired), and Option was "
            "corrupting the captured key via its accent/dead-key composition — "
            "both fixed, though not verified on an actual Mac, so worth checking."
        ),
    },
    {   "version": "1.4.4d",
        "date": "2026-08-20",
        "notes": (
            "Fixed the DND keybind picker not being able to reopen after already "
            "setting a non-default bind once (had to restart the app). Letter-key "
            "DND binds no longer also type that letter into the chat box. Clicking "
            "a slash-command suggestion now actually inserts it instead of just "
            "making the suggestion box vanish (and no longer causes the chat box "
            "to get stuck/unresponsive on Mac afterward). Fixed the room code on "
            "the host setup screen showing unreadable white-on-white text."
        ),
    },
    {   "version": "1.4.4c",
        "date": "2026-08-19",
        "notes": (
            "literally nothing just had to fix version number"
        ),
    },
    {   "version": "1.4.4b",
        "date": "2026-08-19",
        "notes": (
            "Fixed manifest_url."
        ),
    },
    {
        "version": "1.4.4a",
        "date": "2026-08-19",
        "notes": (
            "Added an in-app Changelog viewer. Slowmode now shows a live countdown "
            "above the chat box while the input is locked, instead of just silently "
            "disabling it with no explanation."
        ),
    },
    {
        "version": "1.4.4",
        "date": "2026-08-19",
        "notes": (
            "Fixed issue where mute doesn't automatically lift after time expires. "
            "Versions now also correctly update with letters as well. When an admin "
            "user attempts to moderate the host, it will now say \"you can't <action> "
            "the host\" instead of a generic user does not exist error."
        ),
    },
]

CHANGELOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_gui_changelog.json")

def _load_local_changelog() -> list:
    try:
        with open(CHANGELOG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []

def _save_local_changelog(entries: list):
    try:
        with open(CHANGELOG_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
    except OSError:
        pass

def record_changelog_entry(version: str, notes: str):
    """Called after an OTA update is successfully applied, so the
    changelog viewer picks up releases beyond what's embedded here."""
    entries = [e for e in _load_local_changelog() if e.get("version") != version]
    entries.append({"version": version, "date": time.strftime("%Y-%m-%d"), "notes": notes})
    _save_local_changelog(entries)

def full_changelog() -> list:
    """Embedded history plus anything recorded locally since, deduped
    by version and sorted newest-first (letter-suffix aware)."""
    by_version = {e["version"]: e for e in EMBEDDED_CHANGELOG}
    for e in _load_local_changelog():
        by_version[e["version"]] = e
    return sorted(by_version.values(), key=lambda e: _version_tuple(e["version"]), reverse=True)


# ---- Custom stickers ----
# Uploaded stickers are stored locally (as base64 JPEG bytes in a small
# JSON file next to the script) so they persist across sessions instead
# of needing to be re-uploaded every time. They're sent over the wire
# exactly like the built-in stickers — as a regular JPEG file transfer.
STICKERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_gui_stickers.json")
MAX_CUSTOM_STICKERS = 24

def _load_custom_stickers() -> dict:
    try:
        with open(STICKERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}

def _save_custom_stickers(stickers: dict):
    try:
        with open(STICKERS_FILE, "w", encoding="utf-8") as f:
            json.dump(stickers, f)
    except OSError:
        pass

class Hub:
    def __init__(self, fernet: Fernet, host_name: str, on_typing_change, on_admin_log):
        self.fernet = fernet
        self.host_name = host_name
        self.on_typing_change = on_typing_change
        self.on_admin_log = on_admin_log
        self.lock = threading.Lock()
        self.clients = {}
        self.admins = set()
        self.ghost_mutes = {}
        self.banned_ips = {}
        self.colors = {host_name.lower(): HOST_COLOR}
        self.typing = {}
        self.dnd = set()
        self.last_dnd_announce = {} 
        self.color_changed_once = set()
        self.slowmode_delay = 0.0
        self.last_msg_time = {}

    def log_admin_action(self, admin_name: str, text: str):
        log_text = f"🛡️ [Admin Log] {admin_name} {text}"
        
        if admin_name.lower() != self.host_name.lower():
            self.on_admin_log(log_text)
            
        msg_proto = ADMIN_LOG_PREFIX + log_text
        with self.lock:
            targets = [
                s for s, info in self.clients.items() 
                if info["name"].lower() in self.admins 
                and info["name"].lower() != admin_name.lower()
            ]
        for s in targets:
            try: send_encrypted(s, self.fernet, msg_proto)
            except OSError: pass

    def set_dnd(self, name, active):
        now = time.time()
        with self.lock:
            if active: self.dnd.add(name.lower())
            else: self.dnd.discard(name.lower())
            last = self.last_dnd_announce.get(name.lower(), 0)
            if (now - last) < DND_ANNOUNCE_COOLDOWN:
                return False
            self.last_dnd_announce[name.lower()] = now
            return True

    def is_dnd(self, name):
        with self.lock:
            return name.lower() in self.dnd

    def add_client(self, sock, name, ip):
        with self.lock:
            self.clients[sock] = {
                "name": name, "ip": ip, "muted_until": 0.0,
                "muted_by": None, "mute_reason": None, "kicked": False,
            }

    def remove_client(self, sock):
        with self.lock:
            info = self.clients.pop(sock, None)
            if info and time.time() < info["muted_until"]:
                self.ghost_mutes[info["name"].lower()] = {
                    "name": info["name"], "ip": info.get("ip"),
                    "muted_until": info["muted_until"],
                    "muted_by": info["muted_by"], "mute_reason": info["mute_reason"],
                }
            return info

    def names(self):
        with self.lock:
            return [info["name"] for info in self.clients.values()]

    def get_info(self, sock):
        with self.lock:
            return dict(self.clients.get(sock, {}))

    def find_socket_by_name(self, name):
        with self.lock:
            for s, info in self.clients.items():
                if info["name"].lower() == name.lower():
                    return s
        return None

    def assign_color(self, name):
        with self.lock:
            used = set(self.colors.values())
            available = [c for c in COLOR_PALETTE.values() if c not in used]
            color = random.choice(available) if available else random.choice(list(COLOR_PALETTE.values()))
            self.colors[name.lower()] = color
            return color

    def free_color(self, name):
        with self.lock:
            self.colors.pop(name.lower(), None)

    def colormap_string(self):
        with self.lock:
            return ",".join(f"{n}={c}" for n, c in self.colors.items())

    def colormap_snapshot(self):
        with self.lock:
            return dict(self.colors)

    def is_name_occupied(self, name):
        with self.lock:
            self._purge_expired_ghosts()
            if any(info["name"].lower() == name.lower() for info in self.clients.values()):
                return True
            return name.lower() in self.ghost_mutes

    def _purge_expired_ghosts(self):
        now = time.time()
        expired_mutes = [k for k, v in self.ghost_mutes.items() if now >= v["muted_until"]]
        expired_bans = [ip for ip, info in self.banned_ips.items() if now >= info["until"]]
        for k in expired_mutes: del self.ghost_mutes[k]
        for ip in expired_bans: del self.banned_ips[ip]

    def is_ip_banned(self, ip):
        with self.lock:
            self._purge_expired_ghosts()
            return ip in self.banned_ips and time.time() < self.banned_ips[ip]["until"]

    def get_ban_info(self, ip):
        with self.lock:
            self._purge_expired_ghosts()
            info = self.banned_ips.get(ip)
            return dict(info) if info else None

    def apply_ghost_ip_mute(self, sock, ip):
        with self.lock:
            self._purge_expired_ghosts()
            for g_info in self.ghost_mutes.values():
                if g_info.get("ip") == ip and time.time() < g_info["muted_until"]:
                    if sock in self.clients:
                        self.clients[sock].update(
                            muted_until=g_info["muted_until"],
                            muted_by=g_info["muted_by"],
                            mute_reason=g_info["mute_reason"],
                        )
                    return True
        return False

    def is_muted(self, sock):
        with self.lock:
            info = self.clients.get(sock)
            return bool(info and time.time() < info["muted_until"])

    def mute(self, name, until, by, reason):
        sock = self.find_socket_by_name(name)
        if not sock: return False
        with self.lock:
            self.clients[sock].update(muted_until=until, muted_by=by, mute_reason=reason)
        self.mark_stopped_typing(name)
        return True

    def unmute(self, name):
        sock = self.find_socket_by_name(name)
        found = False
        with self.lock:
            if sock and sock in self.clients:
                self.clients[sock].update(muted_until=0.0, muted_by=None, mute_reason=None)
                found = True
            self._purge_expired_ghosts()
            if name.lower() in self.ghost_mutes:
                del self.ghost_mutes[name.lower()]
                found = True
        return found

    def ban_ip(self, ip, until, by, reason):
        with self.lock:
            self.banned_ips[ip] = {"until": until, "banned_by": by, "reason": reason}

    def unban_ip(self, ip):
        with self.lock:
            if ip in self.banned_ips:
                del self.banned_ips[ip]
                return True
            return False

    def mark_kicked(self, sock):
        with self.lock:
            if sock in self.clients:
                self.clients[sock]["kicked"] = True

    def mark_typing(self, name):
        with self.lock: self.typing[name] = time.time()
        self.on_typing_change()

    def mark_stopped_typing(self, name):
        with self.lock: self.typing.pop(name, None)
        self.on_typing_change()

    def typing_names(self):
        now = time.time()
        with self.lock:
            return [n for n, t in self.typing.items() if now - t <= TYPING_IDLE_TIMEOUT]

    def broadcast(self, text, exclude_sock=None):
        with self.lock: targets = [s for s in self.clients if s is not exclude_sock]
        for s in targets:
            try: send_encrypted(s, self.fernet, text)
            except OSError: pass

    def send_private(self, sock, text):
        try: send_encrypted(sock, self.fernet, text)
        except OSError: pass

    def disconnect(self, sock):
        try: sock.close()
        except OSError: pass

def build_file_message(sender: str, filepath: str):
    size = os.path.getsize(filepath)
    if size > MAX_FILE_BYTES:
        raise ValueError(f"File is {size / 1024 / 1024:.1f} MB — the limit is {MAX_FILE_BYTES // 1024 // 1024} MB.")
    with open(filepath, "rb") as f:
        raw = f.read()
    filename = os.path.basename(filepath).replace("|", "_")
    b64data = base64.b64encode(raw).decode("ascii")
    return FILE_PREFIX + sender + "|" + filename + "|" + b64data

def handle_incoming_file(text: str, event_queue: queue.Queue):
    try:
        sender, filename, b64data = text[len(FILE_PREFIX):].split("|", 2)
        raw = base64.b64decode(b64data)
    except Exception:
        event_queue.put(("system", "[received a corrupted file, ignored]"))
        return
    safe_name = os.path.basename(filename) or "unnamed_file"
    event_queue.put(("file", {"sender": sender, "filename": safe_name, "data": raw}))

def handle_guest_connection(sock, addr, hub: Hub, host_name: str, event_queue: queue.Queue):
    ban_info = hub.get_ban_info(addr[0])
    if ban_info:
        until_str = format_time(ban_info["until"])
        reason = ban_info.get("reason") or "no reason given"
        try: send_encrypted(sock, hub.fernet, BAN_NOTICE_PREFIX + f"{until_str}|{reason}")
        except Exception: pass
        sock.close()
        return

    try:
        first = recv_message(sock, hub.fernet)
    except InvalidToken:
        try: sock.sendall((0xFFFFFFFF).to_bytes(MSG_LEN_BYTES, 'big'))
        except OSError: pass
        sock.close()
        return
    except (OSError, ConnectionError):
        sock.close()
        return
        
    if not first.startswith(HELLO_PREFIX):
        sock.close()
        return
    
    guest_name = first[len(HELLO_PREFIX):].strip()[:30] or f"Guest@{addr[0]}"

    if hub.is_name_occupied(guest_name) or guest_name.lower() == host_name.lower():
        hub.send_private(sock, NOTICE_PREFIX + "Nickname already in use.")
        sock.close()
        return

    with hub.lock:
        if len(hub.clients) >= MAX_GUESTS:
            hub.send_private(sock, NOTICE_PREFIX + "[room is full — try again later]")
            sock.close()
            return

    hub.add_client(sock, guest_name, addr[0])
    hub.apply_ghost_ip_mute(sock, addr[0])
    hub.assign_color(guest_name)
    
    if hub.is_muted(sock):
        info = hub.get_info(sock)
        hub.send_private(sock, MUTE_STATUS_PREFIX + f"1:{info['muted_until']}")
    
    event_queue.put(("system", f"{guest_name} joined from {addr[0]}"))
    hub.broadcast(f"* {guest_name} joined the chat *", exclude_sock=sock)
    hub.send_private(sock, ROSTER_PREFIX + ",".join([host_name] + hub.names()))
    hub.send_private(sock, SLOWMODE_PREFIX + str(hub.slowmode_delay))
    hub.broadcast(COLORMAP_PREFIX + hub.colormap_string())
    event_queue.put(("colormap", hub.colormap_snapshot()))
    event_queue.put(("roster", hub.names()))

    while True:
        try: text = recv_message(sock, hub.fernet)
        except InvalidToken: continue
        except (OSError, ConnectionError): break

        is_admin = guest_name.lower() in hub.admins

        if text.startswith(TYPING_START_PREFIX):
            if hub.is_muted(sock): continue
            hub.mark_typing(text[len(TYPING_START_PREFIX):])
            hub.broadcast(text, exclude_sock=sock)
            event_queue.put(("typing", hub.typing_names()))
            continue
            
        elif text.startswith(TYPING_STOP_PREFIX):
            hub.mark_stopped_typing(text[len(TYPING_STOP_PREFIX):])
            hub.broadcast(text, exclude_sock=sock)
            event_queue.put(("typing", hub.typing_names()))
            continue

        elif text.startswith(DND_PREFIX):
            dname, _, state = text[len(DND_PREFIX):].partition("|")
            active = state == "on"
            if hub.set_dnd(dname, active):
                verb = "turned on" if active else "turned off"
                hub.broadcast(f"* {dname} {verb} Do Not Disturb *", exclude_sock=sock)
                event_queue.put(("system", f"{dname} {verb} Do Not Disturb"))
            continue

        elif text.startswith(CMD_PREFIX):
            cmd_name, _, arg = text[len(CMD_PREFIX):].partition("|")
            if cmd_name == "color":
                if guest_name.lower() in hub.color_changed_once:
                    hub.send_private(sock, NOTICE_PREFIX + "You can only change you color once during a chat session.")
                elif arg.lower() in COLOR_PALETTE:
                    hub.colors[guest_name.lower()] = COLOR_PALETTE[arg.lower()]
                    hub.color_changed_once.add(guest_name.lower())
                    hub.send_private(sock, NOTICE_PREFIX + f"Color changed successfully to {arg.lower()}.")
                    hub.broadcast(COLORMAP_PREFIX + hub.colormap_string())
                    event_queue.put(("colormap", hub.colormap_snapshot()))
                    event_queue.put(("chat", {"raw": f"* {guest_name} changed their color to {arg.lower()} *", "colors": hub.colormap_snapshot()}))
                else:
                    hub.send_private(sock, NOTICE_PREFIX + f"Invalid color. Available: {', '.join(COLOR_PALETTE.keys())}")
            elif cmd_name == "whisper":
                target_name, _, msg = arg.partition("|")
                if target_name.lower() == host_name.lower():
                    event_queue.put(("private", f"[Whisper from {guest_name}]: {msg}"))
                    hub.send_private(sock, NOTICE_PREFIX + f"[Whisper to {host_name}]: {msg}")
                else:
                    target_sock = hub.find_socket_by_name(target_name)
                    if target_sock:
                        hub.send_private(target_sock, NOTICE_PREFIX + f"[Whisper from {guest_name}]: {msg}")
                        hub.send_private(sock, NOTICE_PREFIX + f"[Whisper to {target_name}]: {msg}")
                    else:
                        hub.send_private(sock, NOTICE_PREFIX + f"No one named '{target_name}' is connected.")
            elif cmd_name == "mod":
                if is_admin:
                    run_mod_command(arg, hub, guest_name, lambda t: hub.send_private(sock, NOTICE_PREFIX + t))
                else:
                    hub.send_private(sock, NOTICE_PREFIX + "You do not have permission to use moderation commands.")
            continue

        if hub.is_muted(sock):
            info = hub.get_info(sock)
            hub.send_private(sock, MUTE_NOTICE_PREFIX + f"You are muted by {info['muted_by']} until {format_time(info['muted_until'])}. Reason: {info['mute_reason']}")
            continue

        if text.startswith(FILE_PREFIX):
            if hub.slowmode_delay > 0 and not is_admin:
                now = time.time()
                last_t = hub.last_msg_time.get(guest_name.lower(), 0.0)
                if now - last_t < hub.slowmode_delay:
                    rem = hub.slowmode_delay - (now - last_t)
                    hub.send_private(sock, NOTICE_PREFIX + f"Slowmode is active! Please wait {rem:.1f} seconds.")
                    continue
                hub.last_msg_time[guest_name.lower()] = now

            handle_incoming_file(text, event_queue)
            hub.broadcast(text, exclude_sock=sock)
            continue
            
        elif text.startswith(REACT_PREFIX):
            hub.broadcast(text, exclude_sock=sock)
            msg_id, _, emoji = text[len(REACT_PREFIX):].partition("|")
            event_queue.put(("react", {"msg_id": msg_id, "emoji": emoji}))
            continue

        elif text.startswith(MSG_PREFIX):
            if hub.slowmode_delay > 0 and not is_admin:
                now = time.time()
                last_t = hub.last_msg_time.get(guest_name.lower(), 0.0)
                if now - last_t < hub.slowmode_delay:
                    rem = hub.slowmode_delay - (now - last_t)
                    hub.send_private(sock, NOTICE_PREFIX + f"Slowmode is active! Please wait {rem:.1f} seconds.")
                    continue
                hub.last_msg_time[guest_name.lower()] = now
                
            msg_id, _, raw_text = text[len(MSG_PREFIX):].partition("|")

            target_name, raw_mention = extract_ping_target(raw_text, hub.names() + [host_name])
            if target_name:
                if target_name.lower() == host_name.lower():
                    if hub.is_dnd(host_name): hub.send_private(sock, NOTICE_PREFIX + f"{host_name} is on Do Not Disturb — they won't be notified.")
                    else: event_queue.put(("ping", guest_name))
                else:
                    target_sock = hub.find_socket_by_name(target_name)
                    if target_sock:
                        if hub.is_dnd(target_name): hub.send_private(sock, NOTICE_PREFIX + f"{target_name} is on Do Not Disturb — they won't be notified.")
                        else: hub.send_private(target_sock, PING_PREFIX + guest_name)
            elif raw_mention:
                hub.send_private(sock, NOTICE_PREFIX + f"No one named '{raw_mention}' is here to ping.")

            event_queue.put(("chat", {"raw": raw_text, "colors": hub.colormap_snapshot(), "msg_id": msg_id}))
            hub.broadcast(text, exclude_sock=sock)

    info = hub.remove_client(sock)
    hub.free_color(guest_name)
    sock.close()
    name = info["name"] if info else guest_name
    if not (info and info.get("kicked")):
        event_queue.put(("system", f"{name} disconnected"))
        hub.broadcast(f"* {name} left the chat *", exclude_sock=sock)
        hub.broadcast(COLORMAP_PREFIX + hub.colormap_string())
        event_queue.put(("colormap", hub.colormap_snapshot()))
    event_queue.put(("roster", hub.names()))


def host_accept_loop(server: socket.socket, hub: Hub, host_name: str, event_queue: queue.Queue):
    while True:
        try: conn, addr = server.accept()
        except OSError: break
        threading.Thread(target=handle_guest_connection, args=(conn, addr, hub, host_name, event_queue), daemon=True).start()


HELP_TEXT = (
    "Commands: /mute <name> <min> [reason], /unmute <name>, /kick <name> [reason], "
    "/ban <name> [min|perm] [reason], /unban <ip>, /slowmode [sec], /admin <name>, /unadmin <name>, "
    "/color <name>, /colors, /list, /clear [lines], /whisper <name> <msg>, /help"
)


def run_mod_command(msg: str, hub: Hub, my_name: str, reply_func) -> bool:
    stripped = msg.strip()

    if stripped == "/help":
        reply_func(HELP_TEXT)
        return True

    if stripped == "/list":
        names = hub.names()
        reply_func("Connected: " + (", ".join(names) if names else "(no one yet)"))
        return True

    if stripped == "/colors":
        reply_func("Available colors: " + ", ".join(COLOR_PALETTE.keys()))
        return True

    if stripped.startswith("/color "):
        color = stripped[len("/color "):].strip().lower()
        if my_name.lower() in hub.color_changed_once:
            reply_func("You can only change your color once in one chat session.")
        elif color in COLOR_PALETTE:
            hub.colors[my_name.lower()] = COLOR_PALETTE[color]
            hub.color_changed_once.add(my_name.lower())
            hub.broadcast(COLORMAP_PREFIX + hub.colormap_string())
            reply_func(f"Color changed successfully to {color}.")
        else:
            reply_func(f"Invalid color. Available: {', '.join(COLOR_PALETTE.keys())}")
        return True

    if stripped.startswith("/whisper "):
        parts = stripped[len("/whisper "):].split(maxsplit=1)
        if len(parts) < 2:
            reply_func("Usage: /whisper <name> <message>")
            return True
        target_name, wmsg = parts[0], parts[1]
        if target_name.lower() == my_name.lower():
            reply_func("You cannot whisper to yourself!")
            return True
        target_sock = hub.find_socket_by_name(target_name)
        if not target_sock:
            reply_func(f"No one named '{target_name}' is connected.")
            return True
        hub.send_private(target_sock, NOTICE_PREFIX + f"[Whisper from {my_name}]: {wmsg}")
        reply_func(f"[Whisper to {target_name}]: {wmsg}")
        return True

    if stripped.startswith("/admin "):
        target = stripped[len("/admin "):].strip()
        if target.lower() == hub.host_name.lower():
            reply_func("You cannot admin the host.")
            return True
        target_sock = hub.find_socket_by_name(target)
        if target_sock:
            hub.admins.add(target.lower())
            hub.send_private(target_sock, ADMIN_NOTICE_PREFIX + "1")
            hub.broadcast(f"* {target} is now an admin *")
            hub.log_admin_action(my_name, f"granted admin privileges to {target}.")
            reply_func(f"Granted admin privileges to {target}.")
        else:
            reply_func(f"No one named '{target}' is connected.")
        return True

    if stripped.startswith("/unadmin "):
        target = stripped[len("/unadmin "):].strip()
        if target.lower() == hub.host_name.lower():
            reply_func("You cannot unadmin the host.")
            return True
        if target.lower() in hub.admins:
            hub.admins.remove(target.lower())
            target_sock = hub.find_socket_by_name(target)
            if target_sock:
                hub.send_private(target_sock, ADMIN_NOTICE_PREFIX + "0")
            hub.broadcast(f"* {target} is no longer an admin *")
            hub.log_admin_action(my_name, f"revoked admin privileges from {target}.")
            reply_func(f"Revoked admin privileges from {target}.")
        else:
            reply_func(f"'{target}' is not an admin.")
        return True

    if stripped.startswith("/slowmode"):
        arg = stripped[len("/slowmode"):].strip()
        if not arg:
            hub.slowmode_delay = 0.0 if hub.slowmode_delay > 0 else 2.0
        else:
            try: hub.slowmode_delay = max(0.0, float(arg))
            except ValueError:
                reply_func("Usage: /slowmode [seconds]")
                return True
        status = f"set to {hub.slowmode_delay:g}s" if hub.slowmode_delay > 0 else "disabled"
        hub.broadcast(f"* Slowmode has been {status} *")
        hub.broadcast(SLOWMODE_PREFIX + str(hub.slowmode_delay))
        hub.log_admin_action(my_name, f"set slowmode to {hub.slowmode_delay:g}s.")
        reply_func(f"Slowmode has been {status}.")
        return True

    if stripped.startswith("/ban "):
        parts = stripped[len("/ban "):].split(maxsplit=2)
        if not parts:
            reply_func("Usage: /ban <name> [minutes|perm] [reason]")
            return True
        name = parts[0]
        if name.lower() == hub.host_name.lower():
            reply_func("You cannot ban the host.")
            return True
        dur_str = parts[1].lower() if len(parts) > 1 else "perm"
        reason = parts[2] if len(parts) > 2 else "no reason given"
        
        if dur_str in ("perm", "indefinite", "0", "infinite"): until = float('inf')
        else:
            try: until = time.time() + float(dur_str) * 60
            except ValueError:
                until = float('inf')
                reason = f"{dur_str} {reason}".strip()

        target_sock = hub.find_socket_by_name(name)
        if not target_sock:
            reply_func(f"No one named '{name}' is connected.")
            return True
        
        info = hub.get_info(target_sock)
        ip = info.get("ip")
        if ip: hub.ban_ip(ip, until, my_name, reason)

        until_str = format_time(until)
        hub.send_private(target_sock, BAN_NOTICE_PREFIX + f"{until_str}|{reason}")
        hub.mark_kicked(target_sock)
        hub.broadcast(f"* {name} has been IP banned *", exclude_sock=target_sock)
        hub.disconnect(target_sock)
        
        hub.log_admin_action(my_name, f"banned {name} ({ip}) until {until_str}. Reason: {reason}")
        reply_func(f"Banned {name} ({ip}) until {until_str}. Reason: {reason}")
        return True

    if stripped.startswith("/unban "):
        ip = stripped[len("/unban "):].strip()
        if not ip:
            reply_func("Usage: /unban <ip>")
            return True
        if hub.unban_ip(ip):
            hub.broadcast(f"* IP {ip} has been unbanned *")
            hub.log_admin_action(my_name, f"unbanned IP: {ip}")
            reply_func(f"Unbanned IP: {ip}")
        else:
            reply_func(f"IP '{ip}' is not currently banned.")
        return True

    if stripped.startswith("/mute "):
        parts = stripped[len("/mute "):].split(maxsplit=2)
        if len(parts) < 2:
            reply_func("Usage: /mute <name> <minutes> [reason]")
            return True
        name, minutes_str = parts[0], parts[1]
        if name.lower() == hub.host_name.lower():
            reply_func("You cannot mute the host.")
            return True
        reason = parts[2] if len(parts) > 2 else "no reason given"
        try: minutes = float(minutes_str)
        except ValueError:
            reply_func("Usage: /mute <name> <minutes> [reason]")
            return True
        until = time.time() + minutes * 60
        if not hub.mute(name, until, my_name, reason):
            reply_func(f"No one named '{name}' is connected.")
            return True
            
        hub.broadcast(f"* {name} has been muted *")
        target_sock = hub.find_socket_by_name(name)
        if target_sock:
            hub.send_private(target_sock, MUTE_NOTICE_PREFIX + f"You were muted by {my_name} for {minutes:g} minute(s). Reason: {reason}")
            hub.send_private(target_sock, MUTE_STATUS_PREFIX + f"1:{until}")
            
        hub.log_admin_action(my_name, f"muted {name} for {minutes:g} min. Reason: {reason}")
        reply_func(f"Muted {name} for {minutes:g} min until {format_time(until)}. Reason: {reason}")
        return True

    if stripped.startswith("/unmute "):
        name = stripped[len("/unmute "):].strip()
        if name.lower() == hub.host_name.lower():
            reply_func("You cannot unmute the host.")
            return True
        target_sock = hub.find_socket_by_name(name)
        if not hub.unmute(name):
            reply_func(f"No one named '{name}' is connected or muted.")
            return True
        hub.broadcast(f"* {name} has been unmuted *")
        if target_sock:
            hub.send_private(target_sock, MUTE_STATUS_PREFIX + "0")
        
        hub.log_admin_action(my_name, f"unmuted {name}.")
        reply_func(f"Unmuted {name}.")
        return True

    if stripped.startswith("/kick "):
        parts = stripped[len("/kick "):].split(maxsplit=1)
        name = parts[0] if parts else ""
        if name.lower() == hub.host_name.lower():
            reply_func("You cannot kick the host.")
            return True
        reason = parts[1] if len(parts) > 1 else "no reason given"
        target = hub.find_socket_by_name(name)
        if not target:
            reply_func(f"No one named '{name}' is connected.")
            return True
            
        hub.send_private(target, KICK_NOTICE_PREFIX + f"{my_name}|{reason}")
        hub.mark_kicked(target)
        hub.broadcast(f"* {name} has been kicked *", exclude_sock=target)
        hub.disconnect(target)
        
        hub.log_admin_action(my_name, f"kicked {name}. Reason: {reason}")
        reply_func(f"Kicked {name}. Reason: {reason}")
        return True

    return False

def guest_recv_loop(sock: socket.socket, fernet: Fernet, event_queue: queue.Queue, local_colors: dict, colors_lock: threading.Lock, known_names: set, host_ip: str = ""):
    typing_names = set()

    while True:
        try: text = recv_message(sock, fernet)
        except InvalidToken:
            event_queue.put(("system", "[received a message that failed to decrypt — key mismatch?]"))
            continue
        except (OSError, ConnectionError):
            event_queue.put(("disconnected", "Disconnected from host."))
            break

        if text.startswith(TYPING_START_PREFIX):
            typing_names.add(text[len(TYPING_START_PREFIX):])
            event_queue.put(("typing", list(typing_names)))
            continue
        elif text.startswith(TYPING_STOP_PREFIX):
            typing_names.discard(text[len(TYPING_STOP_PREFIX):])
            event_queue.put(("typing", list(typing_names)))
            continue
        elif text.startswith(PING_PREFIX):
            event_queue.put(("ping", text[len(PING_PREFIX):]))
            continue
        elif text.startswith(ADMIN_NOTICE_PREFIX):
            event_queue.put(("admin_status", text[len(ADMIN_NOTICE_PREFIX):]))
            continue
        elif text.startswith(ADMIN_LOG_PREFIX):
            event_queue.put(("system", text[len(ADMIN_LOG_PREFIX):]))
            continue
        elif text.startswith(SLOWMODE_PREFIX):
            event_queue.put(("slowmode", float(text[len(SLOWMODE_PREFIX):])))
            continue
        elif text.startswith(BAN_NOTICE_PREFIX):
            until_str, _, reason = text[len(BAN_NOTICE_PREFIX):].partition("|")
            event_queue.put(("disconnected", f"You were banned from the chat hosted by {host_ip} until {until_str}. Reason: {reason}"))
            break
        elif text.startswith(KICK_NOTICE_PREFIX):
            by, _, reason = text[len(KICK_NOTICE_PREFIX):].partition("|")
            event_queue.put(("disconnected", f"You were kicked by {by}. Reason: {reason}"))
            break
        elif text.startswith(MUTE_STATUS_PREFIX):
            event_queue.put(("mute_status", text[len(MUTE_STATUS_PREFIX):]))
            continue
        elif text.startswith(MUTE_NOTICE_PREFIX):
            event_queue.put(("private", text[len(MUTE_NOTICE_PREFIX):]))
            continue
        elif text.startswith(NOTICE_PREFIX):
            event_queue.put(("private", text[len(NOTICE_PREFIX):]))
            continue
        elif text.startswith(ROSTER_PREFIX):
            for n in text[len(ROSTER_PREFIX):].split(","):
                if n.strip(): known_names.add(n.strip())
            event_queue.put(("roster", sorted(known_names)))
            continue
        elif text.startswith(COLORMAP_PREFIX):
            new_map = {}
            for pair in text[len(COLORMAP_PREFIX):].split(","):
                if "=" in pair:
                    n, c = pair.split("=", 1)
                    new_map[n] = c
            with colors_lock:
                local_colors.clear()
                local_colors.update(new_map)
            event_queue.put(("colormap", dict(new_map)))
            continue
        elif text.startswith(HOST_DISCONNECT_PREFIX):
            event_queue.put(("disconnected", "Host disconnected."))
            break
        elif text.startswith(FILE_PREFIX):
            handle_incoming_file(text, event_queue)
            continue
        elif text.startswith(REACT_PREFIX):
            msg_id, _, emoji = text[len(REACT_PREFIX):].partition("|")
            event_queue.put(("react", {"msg_id": msg_id, "emoji": emoji}))
            continue

        if text.startswith(MSG_PREFIX):
            msg_id, _, text = text[len(MSG_PREFIX):].partition("|")
        else:
            msg_id = None

        m = re.match(r"^\* (.+?) joined the chat \*$", text)
        if m:
            known_names.add(m.group(1))
            event_queue.put(("roster", sorted(known_names)))
        else:
            m = re.match(r"^(.+?): ", text)
            if m: known_names.add(m.group(1))

        with colors_lock:
            colors_copy = dict(local_colors)
        event_queue.put(("chat", {"raw": text, "colors": colors_copy, "msg_id": msg_id}))


class HostConnection:
    def __init__(self, name, room_code, fernet, event_queue):
        self.name = name
        self.fernet = fernet
        self.event_queue = event_queue
        
        self.hub = Hub(
            fernet, name, 
            on_typing_change=lambda: event_queue.put(("typing", self.hub.typing_names())),
            on_admin_log=lambda msg: event_queue.put(("system", msg))
        )
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind(("0.0.0.0", 0)) 
        self.tcp_port = self.server.getsockname()[1]
        self.server.listen(MAX_GUESTS)
        
        self.stop_event = threading.Event()

        threading.Thread(target=self._udp_discovery_loop, args=(room_code,), daemon=True).start()
        threading.Thread(target=host_accept_loop, args=(self.server, self.hub, self.name, self.event_queue), daemon=True).start()

    def _udp_discovery_loop(self, room_code):
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_sock.bind(("", DISCOVERY_PORT))
        udp_sock.settimeout(1.0)
        
        while not self.stop_event.is_set():
            try:
                data, addr = udp_sock.recvfrom(1024)
                if data.decode('utf-8') == f"DISCOVER:{room_code}":
                    udp_sock.sendto(f"OFFER:{self.tcp_port}".encode('utf-8'), addr)
            except (socket.timeout, OSError):
                if self.stop_event.is_set(): break
        udp_sock.close()

    def send_chat(self, text: str):
        if run_mod_command(text, self.hub, self.name, lambda t: self.event_queue.put(("system", t))):
            return
            
        target_name, raw_mention = extract_ping_target(text, self.hub.names())
        if target_name:
            target_sock = self.hub.find_socket_by_name(target_name)
            if target_sock:
                if self.hub.is_dnd(target_name): self.event_queue.put(("system", f"{target_name} is on Do Not Disturb — they won't be notified."))
                else: self.hub.send_private(target_sock, PING_PREFIX + self.name)
        elif raw_mention:
            self.event_queue.put(("system", f"No one named '{raw_mention}' is here to ping."))
        
        msg_id = os.urandom(4).hex()
        full_msg = f"{self.name}: {text}"
        full_proto = f"{MSG_PREFIX}{msg_id}|{full_msg}"
        
        self.event_queue.put(("chat", {"raw": full_msg, "colors": self.hub.colormap_snapshot(), "msg_id": msg_id}))
        self.hub.broadcast(full_proto)

    def send_dnd(self, active: bool):
        if self.hub.set_dnd(self.name, active):
            verb = "turned on" if active else "turned off"
            self.hub.broadcast(f"* {self.name} {verb} Do Not Disturb *")
            self.event_queue.put(("system", f"You {verb} Do Not Disturb."))

    def send_typing(self, started: bool):
        self.hub.broadcast((TYPING_START_PREFIX if started else TYPING_STOP_PREFIX) + self.name)

    def send_react(self, msg_id: str, emoji: str):
        self.hub.broadcast(f"{REACT_PREFIX}{msg_id}|{emoji}")
        self.event_queue.put(("react", {"msg_id": msg_id, "emoji": emoji}))

    def send_file(self, filepath: str):
        msg = build_file_message(self.name, filepath)
        handle_incoming_file(msg, self.event_queue)
        self.hub.broadcast(msg)

    def send_file_bytes(self, filename: str, data: bytes):
        msg = FILE_PREFIX + self.name + "|" + filename + "|" + base64.b64encode(data).decode("ascii")
        handle_incoming_file(msg, self.event_queue)
        self.hub.broadcast(msg)

    def close(self):
        self.stop_event.set()
        self.hub.broadcast(HOST_DISCONNECT_PREFIX)
        with self.hub.lock:
            for s in list(self.hub.clients.keys()):
                try: s.close()
                except OSError: pass
        try: self.server.close()
        except OSError: pass


class GuestConnection:
    def __init__(self, name, host, port, fernet, event_queue):
        self.name = name
        self.fernet = fernet
        self.event_queue = event_queue
        self.local_colors = {}
        self.colors_lock = threading.Lock()
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        self.sock.connect((host, port))
        self.sock.settimeout(None)

        send_encrypted(self.sock, fernet, HELLO_PREFIX + name)
        
        try:
            length = int.from_bytes(recv_exact(self.sock, MSG_LEN_BYTES), "big")
            if length == 0xFFFFFFFF: raise PermissionError("Password is incorrect.")
            response = fernet.decrypt(recv_exact(self.sock, length)).decode("utf-8", errors="surrogatepass")
        except InvalidToken: raise PermissionError("Password is incorrect.")
        except Exception as e: raise e if isinstance(e, PermissionError) else ConnectionError("Host disconnected unexpectedly.")

        if response.startswith(BAN_NOTICE_PREFIX):
            until_str, _, reason = response[len(BAN_NOTICE_PREFIX):].partition("|")
            raise PermissionError(f"You are banned from this room until {until_str}. Reason: {reason}")
            
        if response.startswith(NOTICE_PREFIX): raise PermissionError(response[len(NOTICE_PREFIX):])
        if not response.startswith(ROSTER_PREFIX): raise ConnectionError("Invalid handshake from host.")

        self.event_queue.put(("connect_success", {"name": name, "host": host, "port": port}))

        known_names = set(n.strip() for n in response[len(ROSTER_PREFIX):].split(",") if n.strip())
        self.event_queue.put(("roster", sorted(known_names)))

        threading.Thread(
            target=guest_recv_loop, 
            args=(self.sock, fernet, event_queue, self.local_colors, self.colors_lock, known_names, host),
            daemon=True,
        ).start()

    def send_chat(self, text: str):
        stripped = text.strip()
        if stripped in ("/help", "/list", "/colors"):
            if stripped == "/help": self.event_queue.put(("system", HELP_TEXT))
            elif stripped == "/colors": self.event_queue.put(("system", "Available colors: " + ", ".join(COLOR_PALETTE.keys())))
            return
            
        if stripped.startswith("/color "):
            color = stripped[len("/color "):].strip()
            try: send_encrypted(self.sock, self.fernet, CMD_PREFIX + f"color|{color}")
            except OSError: self.event_queue.put(("disconnected", "Connection lost."))
            return
            
        if stripped.startswith("/whisper "):
            parts = stripped[len("/whisper "):].split(maxsplit=1)
            if len(parts) < 2:
                self.event_queue.put(("system", "Usage: /whisper <name> <message>"))
                return
            if parts[0].lower() == self.name.lower():
                self.event_queue.put(("system", "You cannot whisper to yourself!"))
                return
            try: send_encrypted(self.sock, self.fernet, CMD_PREFIX + f"whisper|{parts[0]}|{parts[1]}")
            except OSError: self.event_queue.put(("disconnected", "Connection lost."))
            return
            
        if stripped.startswith(("/mute ", "/unmute ", "/kick ", "/ban ", "/unban ", "/slowmode", "/admin ", "/unadmin ")):
            if getattr(self, "is_admin", False):
                try: send_encrypted(self.sock, self.fernet, CMD_PREFIX + f"mod|{stripped}")
                except OSError: self.event_queue.put(("disconnected", "Connection lost."))
            else:
                self.event_queue.put(("system", "Only admins can use moderation commands."))
            return

        msg_id = os.urandom(4).hex()
        full_msg = f"{self.name}: {text}"
        try: send_encrypted(self.sock, self.fernet, f"{MSG_PREFIX}{msg_id}|{full_msg}")
        except OSError:
            self.event_queue.put(("disconnected", "Connection lost."))
            return
            
        with self.colors_lock: colors_copy = dict(self.local_colors)
        self.event_queue.put(("chat", {"raw": full_msg, "colors": colors_copy, "msg_id": msg_id}))

    def send_typing(self, started: bool):
        try: send_encrypted(self.sock, self.fernet, (TYPING_START_PREFIX if started else TYPING_STOP_PREFIX) + self.name)
        except OSError: pass

    def send_dnd(self, active: bool):
        verb = "turned on" if active else "turned off"
        self.event_queue.put(("system", f"You {verb} Do Not Disturb."))
        try: send_encrypted(self.sock, self.fernet, DND_PREFIX + f"{self.name}|{'on' if active else 'off'}")
        except OSError: pass

    def send_file(self, filepath: str):
        try:
            msg = build_file_message(self.name, filepath)
            send_encrypted(self.sock, self.fernet, msg)
            handle_incoming_file(msg, self.event_queue)
        except OSError:
            self.event_queue.put(("disconnected", "Connection lost."))

    def send_file_bytes(self, filename: str, data: bytes):
        msg = FILE_PREFIX + self.name + "|" + filename + "|" + base64.b64encode(data).decode("ascii")
        try:
            send_encrypted(self.sock, self.fernet, msg)
            handle_incoming_file(msg, self.event_queue)
        except OSError:
            self.event_queue.put(("disconnected", "Connection lost."))

    def close(self):
        try: send_encrypted(self.sock, self.fernet, f"[{self.name} left the chat]")
        except OSError: pass
        try: self.sock.close()
        except OSError: pass


def make_button(parent, text, command, bg, fg="white", font=BOLD_FONT, padx=14, pady=6, hover_bg=None):
    frame = tk.Frame(parent, bg=bg, cursor="hand2")
    label = tk.Label(frame, text=text, bg=bg, fg=fg, font=font, padx=padx, pady=pady)
    label.pack(fill="both", expand=True)
    
    frame.base_bg = bg
    frame.disabled = False

    def on_click(event=None):
        if not getattr(frame, "disabled", False): command()

    frame.bind("<Button-1>", on_click)
    label.bind("<Button-1>", on_click)

    if hover_bg:
        def on_enter(event=None):
            if not getattr(frame, "disabled", False):
                frame.configure(bg=hover_bg)
                label.configure(bg=hover_bg)

        def on_leave(event=None):
            if not getattr(frame, "disabled", False):
                frame.configure(bg=frame.base_bg)
                label.configure(bg=frame.base_bg)

        for w in (frame, label):
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

    frame.label = label
    return frame


class ChatApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"chat_gui.py v{VERSION}")
        self.geometry("900x600")
        self.minsize(640, 420)
        self.configure(bg=BG_DARK)

        self.connection = None
        self.my_name = ""
        self.is_admin = False 
        self._mute_expiry_timer = None
        self.current_roster = []
        self.event_queue = queue.Queue()
        self.known_colors = {}
        self.known_tags = set()
        self.typing_active = False
        self.last_typing_sent = 0.0
        self.photo_cache = [] 
        self._typing_timer = None
        self.typing_last_seen = {}
        self.message_reactions = {}
        self.slowmode_delay = 0.0
        self._slowmode_cd_timer = None
        self._slowmode_cd_end = 0.0
        self.user_msg_times = {}       # name.lower() -> recent message timestamps (spam ranking)
        self.user_last_msg_time = {}   # name.lower() -> timestamp of their last message (idle ranking)
        
        self.suggest_popup = None
        self.current_suggestions = []
        self._emoji_popup = None
        self._sticker_popup = None
        self.dnd_keybind = "<Control-d>"
        self._dnd_keybind_popup = None
        self._dnd_cd = 0.0

        self._build_connect_frame()
        self._build_chat_frame()
        self.connect_frame.pack(fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(50, self.poll_queue)
        self.after(500, self._typing_prune_loop)

    def _build_connect_frame(self):
        f = tk.Frame(self, bg=BG_DARK)
        self.connect_frame = f

        card = tk.Frame(f, bg=BG_PANEL, padx=32, pady=28)
        card.place(relx=0.5, rely=0.5, anchor="center")

        self._update_popup = None
        changelog_label = tk.Label(
            f, text="View Changelog", bg=BG_DARK, fg=FG_MUTED,
            font=(CHAT_FONT[0], 8, "underline"), cursor="hand2"
        )
        changelog_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-24)
        changelog_label.bind("<Button-1>", lambda e: self.on_show_changelog())

        version_label = tk.Label(
            f, text=f"v{VERSION} — Check for Updates", bg=BG_DARK, fg=FG_MUTED,
            font=(CHAT_FONT[0], 8, "underline"), cursor="hand2"
        )
        version_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-8)
        version_label.bind("<Button-1>", lambda e: self.on_check_updates())

        tk.Label(card, text="chat_gui", font=(CHAT_FONT[0], 20, "bold"), bg=BG_PANEL, fg=FG_TEXT).grid(
            row=0, column=0, columnspan=2, pady=(0, 16)
        )

        self.mode_var = tk.StringVar(value="host")
        mode_row = tk.Frame(card, bg=BG_PANEL)
        mode_row.grid(row=1, column=0, columnspan=2, pady=(0, 12))
        for text, val in [("Host a chat", "host"), ("Join a chat", "join")]:
            tk.Radiobutton(
                mode_row, text=text, variable=self.mode_var, value=val, bg=BG_PANEL, fg=FG_TEXT, 
                selectcolor=BG_INPUT, activebackground=BG_PANEL, activeforeground=FG_TEXT, font=CHAT_FONT
            ).pack(side="left", padx=8)

        def field(row, label, validate_cmd=None, entry_width=28):
            label_widget = tk.Label(card, text=label, bg=BG_PANEL, fg=FG_MUTED, anchor="w", font=CHAT_FONT)
            label_widget.grid(row=row, column=0, sticky="w", pady=(6, 0))
            kwargs = {"validate": "key", "validatecommand": validate_cmd} if validate_cmd else {}
            entry = tk.Entry(
                card, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat",
                width=entry_width, font=CHAT_FONT,
                readonlybackground=BG_INPUT,  # Tk uses a separate bg for state="readonly";
                                               # left unset it defaults to a near-white system
                                               # color, making light text unreadable on it.
                **kwargs
            )
            entry.grid(row=row, column=1, sticky="ew", pady=(6, 0), padx=(10, 0))
            entry.label = label_widget
            return entry

        card.grid_columnconfigure(1, weight=1)

        self.name_entry = field(2, "Display name", validate_cmd=(self.register(lambda p: " " not in p and len(p) <= 30), "%P"))
        self.room_entry = field(3, "Room Code", entry_width=20)
        self.regen_room_btn = make_button(card, "Refresh", self._regenerate_room_code, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=8, pady=4, font=CHAT_FONT)
        self.regen_room_btn.grid(row=3, column=2, sticky="w", padx=(8, 0), pady=(6, 0))

        self.host_ip_entry = field(4, "Host IP (only if Room Code fails)")

        tk.Label(card, text="Shared key", bg=BG_PANEL, fg=FG_MUTED, anchor="w", font=CHAT_FONT).grid(row=5, column=0, sticky="w", pady=(6, 0))
        self.key_entry = tk.Entry(card, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", width=28, show="*", font=CHAT_FONT)
        self.key_entry.grid(row=5, column=1, sticky="ew", pady=(6, 0), padx=(10, 0))

        self.status_label = tk.Label(card, text="", bg=BG_PANEL, fg=COLOR_PALETTE["red"], wraplength=280, justify="left", font=CHAT_FONT)
        self.status_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))

        self.connect_btn = make_button(card, "Connect", self.on_connect_clicked, bg=BTN_GREEN, hover_bg=BTN_GREEN_HOVER)
        self.connect_btn.grid(row=7, column=0, columnspan=2, pady=(16, 0), sticky="ew")

        self._host_local_ip = None
        self.mode_var.trace_add("write", lambda *_args: self._on_mode_change())
        self._on_mode_change()

    def _on_mode_change(self):
        if self.mode_var.get() == "host":
            self.room_entry.label.configure(text="Room Code (= last 2 numbers of your IP)")
            self.regen_room_btn.grid()
            self._regenerate_room_code()
            self.host_ip_entry.grid_remove()
            self.host_ip_entry.label.grid_remove()
        else:
            self.room_entry.label.configure(text="Room Code (from host)")
            self.regen_room_btn.grid_remove()
            self.room_entry.configure(state="normal")
            self.room_entry.delete(0, "end")
            self.host_ip_entry.grid()
            self.host_ip_entry.label.grid()

    def _regenerate_room_code(self):
        if self.mode_var.get() != "host": return
        self._host_local_ip = get_local_ip()
        self.room_entry.configure(state="normal")
        self.room_entry.delete(0, "end")
        self.room_entry.insert(0, generate_room_code(self._host_local_ip))
        self.room_entry.configure(state="readonly")

    def _build_chat_frame(self):
        self.chat_frame = tk.Frame(self, bg=BG_DARK)
        top = tk.Frame(self.chat_frame, bg=BG_PANEL, height=40)
        top.pack(side="top", fill="x")
        
        self.title_label = tk.Label(top, text="", bg=BG_PANEL, fg=FG_TEXT, font=TITLE_FONT)
        self.title_label.pack(side="left", padx=12, pady=8)

        make_button(top, "Disconnect", self.on_disconnect_clicked, bg=BTN_RED, hover_bg=BTN_RED_HOVER, padx=12, pady=5).pack(side="right", padx=12, pady=6)

        self.dnd_active = False
        self.dnd_btn = make_button(top, "🔕 DND", self.on_dnd_toggle, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=12, pady=5)
        self.dnd_btn.pack(side="right", padx=(12, 0), pady=6)
        
        for bind in ["<Button-2>", "<Button-3>"]:
            self.dnd_btn.bind(bind, lambda e: self.on_dnd_keybind_picker())
            self.dnd_btn.label.bind(bind, lambda e: self.on_dnd_keybind_picker())
        self._apply_dnd_keybind()

        body = tk.Frame(self.chat_frame, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        self.log = scrolledtext.ScrolledText(body, bg=BG_DARK, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", state="disabled", wrap="word", padx=10, pady=8, font=CHAT_FONT)
        self.log.pack(side="left", fill="both", expand=True)
        self.log.tag_configure("system", foreground=FG_MUTED, font=(CHAT_FONT[0], 9, "italic"))
        self.log.tag_configure("private", foreground=COLOR_PALETTE["yellow"])
        self.log.tag_configure("timestamp", foreground=FG_MUTED, font=(CHAT_FONT[0], 8))
        self.log.tag_configure("reaction_style", foreground=COLOR_PALETTE["yellow"], font=(CHAT_FONT[0], 9))

        member_panel = tk.Frame(body, bg=BG_PANEL, width=160)
        member_panel.pack(side="right", fill="y")
        member_panel.pack_propagate(False)
        tk.Label(member_panel, text="ONLINE", bg=BG_PANEL, fg=FG_MUTED, font=(CHAT_FONT[0], 8, "bold")).pack(anchor="w", padx=10, pady=(10, 4))
        self.member_list_frame = tk.Frame(member_panel, bg=BG_PANEL)
        self.member_list_frame.pack(fill="both", expand=True, padx=10)

        self.typing_var = tk.StringVar(value="")
        tk.Label(self.chat_frame, textvariable=self.typing_var, bg=BG_DARK, fg=FG_MUTED, font=(CHAT_FONT[0], 9, "italic"), anchor="w").pack(fill="x", padx=10)

        self.mute_status_var = tk.StringVar(value="")
        tk.Label(self.chat_frame, textvariable=self.mute_status_var, bg=BG_DARK, fg=COLOR_PALETTE["red"], font=(CHAT_FONT[0], 9, "bold"), anchor="w").pack(fill="x", padx=10)

        self.bottom_bar = tk.Frame(self.chat_frame, bg=BG_DARK)
        self.bottom_bar.pack(fill="x", padx=10, pady=(0, 10))

        self.attach_btn = make_button(self.bottom_bar, "📎", self.on_attach_file, bg=BG_INPUT, hover_bg=BTN_NEUTRAL_HOVER, padx=10, pady=6)
        self.attach_btn.pack(side="left", padx=(0, 6))

        self.sticker_btn = make_button(self.bottom_bar, "🌠", self.on_sticker_picker, bg=BG_INPUT, hover_bg=BTN_NEUTRAL_HOVER, padx=10, pady=6)
        self.sticker_btn.pack(side="left", padx=(0, 6))

        self.emoji_btn = make_button(self.bottom_bar, "😀", self.on_emoji_picker, bg=BG_INPUT, hover_bg=BTN_NEUTRAL_HOVER, padx=10, pady=6)
        self.emoji_btn.pack(side="left", padx=(0, 6))

        self.msg_entry = tk.Entry(self.bottom_bar, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", font=CHAT_FONT)
        self.msg_entry.pack(side="left", fill="x", expand=True, ipady=6)

        self.msg_entry.bind("<Return>", self.on_send)
        self.msg_entry.bind("<KeyRelease>", self.on_entry_key)
        self.msg_entry.bind("<Tab>", self.on_tab_autocomplete)
        self.msg_entry.bind("<Up>", self._on_up_arrow)
        self.msg_entry.bind("<Down>", self._on_down_arrow)
        self.msg_entry.bind("<FocusOut>", lambda e: self.after(150, self.destroy_suggestions))

        self._apply_dnd_keybind()  # re-apply now that msg_entry exists (see _apply_dnd_keybind)

        self.send_btn = make_button(self.bottom_bar, "Send", self.on_send, bg=COLOR_PALETTE["blue"], hover_bg=BTN_BLUE_HOVER, padx=16, pady=6)
        self.send_btn.pack(side="left", padx=(6, 0))

    def _set_button_enabled(self, btn, enabled: bool):
        btn.disabled = not enabled
        bg = btn.base_bg if enabled else BG_INPUT
        btn.configure(bg=bg)
        btn.label.configure(bg=bg, fg="white" if enabled else FG_MUTED)

    def _set_input_state(self, enabled: bool):
        self.msg_entry.configure(state="normal" if enabled else "disabled")
        for btn in (self.send_btn, self.attach_btn, self.sticker_btn, self.emoji_btn):
            self._set_button_enabled(btn, enabled)

    def _apply_mute_state(self, muted: bool, until: float = 0.0):
        if getattr(self, "_mute_expiry_timer", None):
            try:
                self.after_cancel(self._mute_expiry_timer)
            except Exception:
                pass
            self._mute_expiry_timer = None

        self._set_input_state(not muted)
        self.mute_status_var.set(f"🔇 You are muted{f' until {format_time(until)}' if until else ''} — messages won't send." if muted else "")

        if muted and until:
            # The server only tells us "you're muted until X" once, up
            # front — nothing proactively pushes an unmute when the
            # timer simply runs out (as opposed to an explicit
            # /unmute). Schedule our own local re-check so the input
            # box doesn't stay stuck disabled after the mute has
            # actually expired.
            remaining_ms = max(0, int((until - time.time()) * 1000)) + 250
            self._mute_expiry_timer = self.after(remaining_ms, self._on_mute_expired)

    def _on_mute_expired(self):
        self._mute_expiry_timer = None
        self._apply_mute_state(False)
        self.append_system_line("🔇 Your mute has expired — you can send messages again.")

    def _record_user_message_time(self, sender_name: str):
        key = sender_name.lower()
        now = time.time()
        self.user_last_msg_time[key] = now
        times = [t for t in self.user_msg_times.get(key, []) if now - t <= SPAM_SUGGESTION_WINDOW]
        times.append(now)
        self.user_msg_times[key] = times

    def _rank_by_recent_activity(self, names: list) -> list:
        """Most messages within SPAM_SUGGESTION_WINDOW first — surfaces
        whoever's currently sending the most messages in the shortest
        time, as a shortcut for /mute /kick /ban."""
        now = time.time()
        def score(name):
            times = self.user_msg_times.get(name.lower(), [])
            return len([t for t in times if now - t <= SPAM_SUGGESTION_WINDOW])
        return sorted(names, key=lambda n: (-score(n), n.lower()))

    def _rank_by_idle_time(self, names: list) -> list:
        """Longest since their last message first (never-sent = most
        idle of all) — surfaces who's most likely away, as a shortcut
        for @ pings."""
        now = time.time()
        def idle_for(name):
            last = self.user_last_msg_time.get(name.lower())
            return float("inf") if last is None else now - last
        return sorted(names, key=lambda n: (-idle_for(n), n.lower()))

    def evaluate_live_suggestions(self):
        text, cursor_pos = self.msg_entry.get(), self.msg_entry.index("insert")
        left_text = text[:cursor_pos]
        words = left_text.split(" ")
        self.current_suggestions = []

        if left_text.startswith("/"):
            base_cmd = words[0].lower()
            if len(words) == 1:
                all_cmds = ["/color", "/colors", "/list", "/clear", "/whisper", "/help"]
                if self.mode_var.get() == "host" or getattr(self, 'is_admin', False):
                    all_cmds.extend(["/mute", "/unmute", "/kick", "/ban", "/unban", "/slowmode", "/admin", "/unadmin"])
                self.current_suggestions = [c for c in all_cmds if c.startswith(base_cmd)]
            elif len(words) >= 2:
                current_arg = words[-1].lower() if left_text[-1] != " " else ""
                if base_cmd in {"/mute", "/unmute", "/kick", "/ban", "/whisper", "/admin", "/unadmin"} and len(words) == 2:
                    matches = [n for n in self.current_roster if n.lower() != self.my_name.lower() and n.lower().startswith(current_arg)]
                    # Punitive/moderation actions: surface whoever's been
                    # most active recently first — usually who you're
                    # actually about to target.
                    if base_cmd in {"/mute", "/kick", "/ban"}:
                        matches = self._rank_by_recent_activity(matches)
                    self.current_suggestions = matches
                elif base_cmd == "/color" and len(words) == 2:
                    self.current_suggestions = [col for col in COLOR_PALETTE if col.startswith(current_arg)]

        if words and words[-1].startswith("@") and len(words[-1]) >= 1:
            query = words[-1][1:].lower()
            ping_matches = self._rank_by_idle_time([
                n for n in self.current_roster
                if n.lower() != self.my_name.lower() and n.lower().startswith(query)
            ])
            self.current_suggestions.extend(
                f"@{n}" for n in ping_matches if f"@{n}" not in self.current_suggestions
            )

        if self.current_suggestions: self.render_suggestion_popup()
        else: self.destroy_suggestions()

    def render_suggestion_popup(self):
        if not self.suggest_popup:
            self.suggest_popup = tk.Toplevel(self)
            self.suggest_popup.wm_overrideredirect(True)
            self.suggest_popup.configure(bg=BG_PANEL, bd=1, relief="solid")
            self.suggest_popup.attributes("-topmost", True)
            # Clicking the popup's own background (e.g. the padding around
            # the listbox) should dismiss it and hand focus straight back
            # to the entry — without this, losing focus to a borderless
            # overrideredirect window can leave the entry in a stuck,
            # unresponsive state on macOS until the user clicks elsewhere
            # and back.
            self.suggest_popup.bind("<Button-1>", self._on_suggestion_popup_clicked)

            self.suggest_listbox = tk.Listbox(
                self.suggest_popup, bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT,
                selectbackground=BTN_NEUTRAL, selectforeground="white",
                relief="flat", highlightthickness=0
            )
            self.suggest_listbox.pack(fill="both", expand=True, padx=4, pady=4)
            self.suggest_listbox.bind("<Button-1>", self._on_suggestion_clicked)
        
        self.suggest_listbox.delete(0, "end")
        for item in self.current_suggestions: self.suggest_listbox.insert("end", f"  {item}  ")
        self.suggest_listbox.selection_set(0)
        self.suggest_listbox.configure(height=min(6, len(self.current_suggestions)))
        
        x, y = self.msg_entry.winfo_rootx(), self.msg_entry.winfo_rooty() - self.suggest_popup.winfo_reqheight() - 5
        self.suggest_popup.wm_geometry(f"{max(self.msg_entry.winfo_width() // 2, 220)}x{self.suggest_popup.winfo_reqheight()}+{x}+{y}")

    def destroy_suggestions(self):
        if self.suggest_popup:
            try: self.suggest_popup.destroy()
            except Exception: pass
            self.suggest_popup, self.current_suggestions = None, []

    def _on_suggestion_popup_clicked(self, event):
        self.destroy_suggestions()
        self.msg_entry.focus_set()
        return "break"

    def _on_suggestion_clicked(self, event):
        if not self.current_suggestions:
            return "break"
        index = self.suggest_listbox.nearest(event.y)
        if 0 <= index < len(self.current_suggestions):
            self._apply_chosen_suggestion(self.current_suggestions[index])
        else:
            self.destroy_suggestions()
            self.msg_entry.focus_set()
        return "break"

    def _apply_chosen_suggestion(self, chosen):
        text, cursor_pos = self.msg_entry.get(), self.msg_entry.index("insert")
        left_text, right_text, words = text[:cursor_pos], text[cursor_pos:], text[:cursor_pos].split(" ")

        if len(words) == 1: new_left = chosen + " "
        elif left_text[-1] == " ": new_left = left_text + chosen + " "
        else:
            words[-1] = chosen
            new_left = " ".join(words) + " "

        self.msg_entry.delete(0, "end")
        self.msg_entry.insert(0, new_left + right_text)
        self.msg_entry.icursor(len(new_left))

        self.destroy_suggestions()
        self.msg_entry.focus_set()

    def _on_up_arrow(self, event):
        if self.suggest_popup and self.current_suggestions:
            idx = self.suggest_listbox.curselection()
            new_idx = max(0, (idx[0] if idx else len(self.current_suggestions)) - 1)
            self.suggest_listbox.selection_clear(0, "end")
            self.suggest_listbox.selection_set(new_idx)
            self.suggest_listbox.see(new_idx)
            return "break"

    def _on_down_arrow(self, event):
        if self.suggest_popup and self.current_suggestions:
            idx = self.suggest_listbox.curselection()
            new_idx = min(len(self.current_suggestions)-1, (idx[0] if idx else -1) + 1)
            self.suggest_listbox.selection_clear(0, "end")
            self.suggest_listbox.selection_set(new_idx)
            self.suggest_listbox.see(new_idx)
            return "break"

    def on_tab_autocomplete(self, event):
        if not self.suggest_popup or not self.current_suggestions: return "break"
        chosen = self.current_suggestions[self.suggest_listbox.curselection()[0]] if self.suggest_listbox.curselection() else self.current_suggestions[0]
        self._apply_chosen_suggestion(chosen)
        return "break"

    def on_connect_clicked(self):
        name, key, room_code, mode = self.name_entry.get().strip(), self.key_entry.get(), self.room_entry.get().strip(), self.mode_var.get()
        if not name: return self.status_label.configure(text="Enter a display name.", fg=COLOR_PALETTE["red"])
        if " " in name: return self.status_label.configure(text="Display name cannot contain spaces.", fg=COLOR_PALETTE["red"])
        if not (len(room_code) == 6 and room_code.isdigit() and 0 <= int(room_code[:3]) <= 255 and 0 <= int(room_code[3:]) <= 255):
            return self.status_label.configure(text="Room Code must be 6 digits (from the host's screen).", fg=COLOR_PALETTE["red"])
        if not key: return self.status_label.configure(text="Enter the shared key password.", fg=COLOR_PALETTE["red"])

        self.status_label.configure(text="Connecting, please wait...", fg=COLOR_PALETTE["yellow"])
        self.update_idletasks()

        fernet, self.my_name = Fernet(derive_key(key)), name
        
        if mode == "host":
            try:
                self.connection = HostConnection(name, room_code, fernet, self.event_queue)
                self.is_admin = True
                self.title_label.configure(text=f"Hosting as {name} — Room {room_code}")
                self._transition_to_chat(mode, name, room_code)
            except OSError as e:
                self.status_label.configure(text=f"Couldn't start: {e}", fg=COLOR_PALETTE["red"])
        else:
            self.is_admin = False
            threading.Thread(target=self._async_guest_connect, args=(name, room_code, fernet, self.host_ip_entry.get().strip() or None), daemon=True).start()

    def _async_guest_connect(self, name, room_code, fernet, manual_target=None):
        host_ip, port = None, None
        
        if manual_target:
            if ":" in manual_target:
                ip_str, _, port_str = manual_target.partition(":")
                try: host_ip, port = ip_str.strip(), int(port_str.strip())
                except ValueError:
                    return self.event_queue.put(("connect_fail", f"'{manual_target}' isn't a valid address. Use an IP like 192.168.1.42, or IP:port if you have both."))
            else: host_ip = manual_target

        if not ENABLE_WAN_RELAY:
            if host_ip and port: pass 
            elif host_ip: host_ip, port = discover_host(room_code, target_ip=host_ip)
            else:
                if len(room_code) == 6 and room_code.isdigit():
                    prefix = ".".join(get_local_ip().split(".")[:2])
                    if prefix and not prefix.startswith("127."):
                        host_ip, port = discover_host(room_code, target_ip=f"{prefix}.{int(room_code[:3])}.{int(room_code[3:])}", timeout=1.5)
                if not host_ip: host_ip, port = discover_host(room_code)

        if not host_ip:
            return self.event_queue.put(("connect_fail", f"Could not find Room {room_code}. Ensure the host is running and you are on the same Wi-Fi/network."))

        try: self.connection = GuestConnection(name, host_ip, port, fernet, self.event_queue)
        except PermissionError as e: self.event_queue.put(("connect_fail", str(e)))
        except (OSError, ConnectionError) as e: self.event_queue.put(("connect_fail", f"Connection failed: {e}"))

    def _reset_session_state(self):
        self._close_emoji_popup()
        self._close_sticker_popup()
        self._stop_typing_signal()
        self.photo_cache = []
        
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        
        self.known_colors, self.known_tags, self.current_roster, self.message_reactions, self.typing_last_seen = {}, set(), [], {}, {}
        self.user_msg_times, self.user_last_msg_time = {}, {}
        self.typing_var.set("")
        self.dnd_active, self._dnd_cd, self.dnd_btn.disabled, self.slowmode_delay = False, 0.0, False, 0.0
        self._set_dnd_button_style(False)
        if getattr(self, "_slowmode_cd_timer", None):
            try: self.after_cancel(self._slowmode_cd_timer)
            except Exception: pass
            self._slowmode_cd_timer = None
        self._apply_mute_state(False)
        
        for child in self.member_list_frame.winfo_children(): child.destroy()

    def _transition_to_chat(self, mode, name, room_code):
        self._reset_session_state()
        self.known_colors = {name.lower(): HOST_COLOR if mode == "host" else FG_TEXT}
        self.update_roster([name])
        self.connect_frame.pack_forget()
        self.chat_frame.pack(fill="both", expand=True)
        self.msg_entry.focus_set()
        
        if mode == "host":
            local_ip = self._host_local_ip or get_local_ip()
            self.append_system_line(f"Hosting Room {room_code} on {local_ip}. Guests on your same network segment can join with just the Room Code. If that doesn't work, have them enter {local_ip}:{self.connection.tcp_port} in the 'Host IP' field. Type /help for commands.")
        else:
            self.append_system_line(f"You joined Room {room_code} as {name}. Type /help for commands.")

    def on_disconnect_clicked(self):
        self._teardown_connection()
        self.chat_frame.pack_forget()
        self.connect_frame.pack(fill="both", expand=True)
        self.status_label.configure(text="Disconnected.", fg=COLOR_PALETTE["green"])
        self._regenerate_room_code()

    def _handle_disconnected(self, reason: str):
        self._teardown_connection()
        self.chat_frame.pack_forget()
        self.connect_frame.pack(fill="both", expand=True)
        self.status_label.configure(text=reason, fg=COLOR_PALETTE["red"])
        self._regenerate_room_code()

    def _teardown_connection(self):
        self.destroy_suggestions()
        self._stop_typing_signal()
        if self.connection:
            try: self.connection.close()
            except Exception: pass
            self.connection = None

    def on_dnd_toggle(self):
        if not self.connection or (time.time() - self._dnd_cd < DND_ANNOUNCE_COOLDOWN): return
            
        self._dnd_cd, self.dnd_active = time.time(), not self.dnd_active
        self._set_dnd_button_style(self.dnd_active)
        
        self.dnd_btn.disabled = True
        self.dnd_btn.label.configure(text="🔕 Cooldown...")
        self.after(int(DND_ANNOUNCE_COOLDOWN * 1000), self._restore_dnd_btn)
        self.connection.send_dnd(self.dnd_active)

    def _restore_dnd_btn(self):
        self.dnd_btn.disabled = False
        self._set_dnd_button_style(self.dnd_active)

    def _apply_dnd_keybind(self):
        try: self.unbind_all(self.dnd_keybind)
        except Exception: pass
        if hasattr(self, "msg_entry"):
            try: self.msg_entry.unbind(self.dnd_keybind)
            except Exception: pass
        if self.dnd_keybind:
            self.bind_all(self.dnd_keybind, lambda e: self._trigger_dnd_toggle())
            if hasattr(self, "msg_entry"):
                # Bound directly on the entry too: instance-level bindings
                # fire before the Entry widget's own class binding (which
                # is what types the character in), so returning "break"
                # here actually stops a letter-key DND bind from also
                # typing that letter into the chat box. bind_all alone
                # can't do this — "all" bindings are checked last.
                self.msg_entry.bind(self.dnd_keybind, lambda e: self._trigger_dnd_toggle())

    def _trigger_dnd_toggle(self):
        self.on_dnd_toggle()
        return "break"

    def on_dnd_keybind_picker(self):
        if self._dnd_keybind_popup is not None: return
        popup = tk.Toplevel(self)
        popup.title("DND Keybind")
        popup.configure(bg=BG_PANEL, padx=16, pady=14)
        popup.resizable(False, False)
        popup.transient(self)
        self._dnd_keybind_popup = popup

        tk.Label(popup, text="Press any key combination to bind Do Not Disturb...", bg=BG_PANEL, fg=FG_TEXT, font=BOLD_FONT).pack(anchor="w", pady=(0, 10))
        tk.Label(popup, text=f"Current bind: {self.dnd_keybind}", bg=BG_INPUT, fg=FG_TEXT, font=CHAT_FONT).pack(fill="x", pady=5)

        def capture(e):
            if e.keysym.endswith("_L") or e.keysym.endswith("_R"): return
            is_mac = sys.platform == "darwin"
            parts = []
            if e.state & 4: parts.append("Control")
            if e.state & 1: parts.append("Shift")
            if is_mac:
                # Tk's Aqua port reports Command under the same bit X11
                # calls "Mod1" (historically mislabeled "Alt" below) —
                # and Command/Option are Tk's own native modifier names
                # on macOS, not "Alt". Binding "<Alt-x>" here would never
                # actually fire on a real Command press, since Tk doesn't
                # report Command presses under that name on this platform.
                if e.state & 8: parts.append("Command")
                if e.state & 16: parts.append("Option")
            else:
                if e.state & 131072 or e.state & 8: parts.append("Alt")

            keyname = e.keysym
            if is_mac and (e.state & 16):
                keyname = MAC_VIRTUAL_KEYCODE_TO_KEY.get(e.keycode, keyname)
            parts.append(keyname)
            
            try: self.unbind_all(self.dnd_keybind)
            except Exception: pass
            if hasattr(self, "msg_entry"):
                try: self.msg_entry.unbind(self.dnd_keybind)
                except Exception: pass
                
            self.dnd_keybind = "<" + "-".join(parts) + ">"
            self._apply_dnd_keybind()
            self._dnd_keybind_popup = None
            popup.destroy()

        popup.bind("<KeyPress>", capture)
        popup.focus_set()
        popup.protocol("WM_DELETE_WINDOW", lambda: (setattr(self, '_dnd_keybind_popup', None), popup.destroy()))

    def _set_dnd_button_style(self, active: bool):
        bg, text = (BTN_RED, "🔕 DND: ON") if active else (BTN_NEUTRAL, "🔕 DND: OFF")
        self.dnd_btn.configure(bg=bg)
        self.dnd_btn.base_bg = bg
        self.dnd_btn.label.configure(text=text, bg=bg)

    def on_show_changelog(self):
        entries = full_changelog()
        popup = tk.Toplevel(self)
        popup.title("Changelog")
        popup.configure(bg=BG_PANEL, padx=16, pady=14)
        popup.resizable(False, False)
        popup.transient(self)

        text = scrolledtext.ScrolledText(
            popup, width=56, height=16, bg=BG_INPUT, fg=FG_TEXT, font=CHAT_FONT,
            wrap="word", relief="flat", padx=8, pady=8
        )
        text.pack()
        text.tag_configure("ver", font=(CHAT_FONT[0], CHAT_FONT[1], "bold"), foreground=COLOR_PALETTE["blue"])

        if not entries:
            text.insert("1.0", "No changelog entries yet.")
        else:
            for i, e in enumerate(entries):
                if i:
                    text.insert("end", "\n\n")
                text.insert("end", f"v{e.get('version', '?')} — {e.get('date', 'unknown date')}\n", ("ver",))
                text.insert("end", e.get("notes") or "(no notes)")
        text.configure(state="disabled")

        make_button(popup, "Close", popup.destroy, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=12, pady=5).pack(pady=(10, 0))

    def on_check_updates(self):
        if not UPDATE_MANIFEST_URL:
            messagebox.showinfo(
                "Check for Updates",
                "No update server is configured yet. Set UPDATE_MANIFEST_URL near the "
                "top of chat_gui.py to enable this."
            )
            return
        if self._update_popup is not None:
            return
        self._open_update_popup(f"Checking for updates (current: v{VERSION})...")
        threading.Thread(target=self._async_check_updates, daemon=True).start()

    def _open_update_popup(self, status_text: str):
        popup = tk.Toplevel(self)
        popup.title("Check for Updates")
        popup.configure(bg=BG_PANEL, padx=20, pady=16)
        popup.resizable(False, False)
        popup.transient(self)
        popup.protocol("WM_DELETE_WINDOW", self._close_update_popup)
        self._update_popup = popup
        self._pending_manifest = None

        self._update_status_var = tk.StringVar(value=status_text)
        tk.Label(
            popup, textvariable=self._update_status_var, bg=BG_PANEL, fg=FG_TEXT,
            font=CHAT_FONT, wraplength=320, justify="left"
        ).pack(pady=(0, 12))

        self._update_btn_row = tk.Frame(popup, bg=BG_PANEL)
        self._update_btn_row.pack()

    def _close_update_popup(self):
        if self._update_popup is not None:
            try:
                self._update_popup.destroy()
            except Exception:
                pass
            self._update_popup = None

    def _clear_update_buttons(self):
        for w in self._update_btn_row.winfo_children():
            w.destroy()

    def _async_check_updates(self):
        try:
            manifest = fetch_update_manifest(UPDATE_MANIFEST_URL)
        except Exception as e:
            self.event_queue.put(("update_check_result", {"ok": False, "error": str(e)}))
            return
        self.event_queue.put(("update_check_result", {"ok": True, "manifest": manifest}))

    def _handle_update_check_result(self, result):
        if self._update_popup is None:
            return
        self._clear_update_buttons()
        if not result["ok"]:
            self._update_status_var.set(f"Couldn't check for updates:\n{result['error']}")
            make_button(self._update_btn_row, "Close", self._close_update_popup, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=12, pady=5).pack()
            return

        manifest = result["manifest"]
        remote_version = manifest.get("version", "?")
        if not is_newer_version(remote_version, VERSION):
            self._update_status_var.set(f"You're up to date (v{VERSION}).")
            make_button(self._update_btn_row, "Close", self._close_update_popup, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=12, pady=5).pack()
            return

        notes = manifest.get("notes", "")
        notes_line = f"\n\n{notes}" if notes else ""
        self._update_status_var.set(
            f"Update available: v{remote_version} (you have v{VERSION}).{notes_line}\n\n"
            "This will be signature-verified before anything is installed."
        )
        self._pending_manifest = manifest
        make_button(self._update_btn_row, "Install & Restart", self._start_update_install, bg=BTN_GREEN, hover_bg=BTN_GREEN_HOVER, padx=12, pady=5).pack(side="left", padx=(0, 8))
        make_button(self._update_btn_row, "Not now", self._close_update_popup, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=12, pady=5).pack(side="left")

    def _start_update_install(self):
        if not self._pending_manifest:
            return
        self._clear_update_buttons()
        self._update_status_var.set("Downloading and verifying update...")
        threading.Thread(target=self._async_install_update, args=(self._pending_manifest,), daemon=True).start()

    def _async_install_update(self, manifest):
        try:
            payload = download_and_verify_update(manifest)
            backup_path = apply_update(payload)
            record_changelog_entry(manifest.get("version", "?"), manifest.get("notes", ""))
        except Exception as e:
            self.event_queue.put(("update_apply_result", {"ok": False, "error": str(e)}))
            return
        self.event_queue.put(("update_apply_result", {"ok": True, "backup": backup_path}))

    def _handle_update_apply_result(self, result):
        if self._update_popup is None:
            return
        self._clear_update_buttons()
        if not result["ok"]:
            self._update_status_var.set(f"Update failed and was NOT installed:\n{result['error']}")
            make_button(self._update_btn_row, "Close", self._close_update_popup, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=12, pady=5).pack()
            return
        self._update_status_var.set(
            f"Update installed and verified. Your previous version was backed up as:\n"
            f"{os.path.basename(result['backup'])}\n\nRestart to apply it."
        )
        make_button(self._update_btn_row, "Restart Now", self._restart_app, bg=BTN_GREEN, hover_bg=BTN_GREEN_HOVER, padx=12, pady=5).pack(side="left", padx=(0, 8))
        make_button(self._update_btn_row, "Later", self._close_update_popup, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=12, pady=5).pack(side="left")

    def _restart_app(self):
        self._teardown_connection()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def on_close(self):
        self._teardown_connection()
        self.destroy()

    def _stop_typing_signal(self):
        if getattr(self, "_typing_timer", None):
            try: self.after_cancel(self._typing_timer)
            except Exception: pass
            self._typing_timer = None
        if self.typing_active and self.connection:
            self.connection.send_typing(False)
            self.typing_active, self.last_typing_sent = False, 0.0

    def _start_slowmode_cooldown(self):
        self._set_input_state(False)
        self.msg_entry.update()
        self._slowmode_cd_end = time.time() + self.slowmode_delay
        if getattr(self, "_slowmode_cd_timer", None):
            try: self.after_cancel(self._slowmode_cd_timer)
            except Exception: pass
        self._tick_slowmode_cooldown()

    def _tick_slowmode_cooldown(self):
        remaining = self._slowmode_cd_end - time.time()
        if remaining <= 0:
            self._end_slowmode_cooldown()
            return
        if not self.mute_status_var.get().startswith("🔇"):
            self.mute_status_var.set(f"⏳ Slowmode is active, you cannot send messages for {remaining:.1f}s")
        self._slowmode_cd_timer = self.after(100, self._tick_slowmode_cooldown)

    def _end_slowmode_cooldown(self):
        if getattr(self, "_slowmode_cd_timer", None):
            try: self.after_cancel(self._slowmode_cd_timer)
            except Exception: pass
            self._slowmode_cd_timer = None
        if self.mute_status_var.get().startswith("🔇"):
            return  # still muted for a separate reason — leave that message/lock alone
        self.mute_status_var.set("")
        self._set_input_state(True)

    def _maybe_start_slowmode_cooldown(self):
        if getattr(self, "slowmode_delay", 0) > 0 and not self.is_admin:
            self._start_slowmode_cooldown()

    def on_send(self, event=None):
        if not self.connection or str(self.msg_entry["state"]) == "disabled": return
        text = self.msg_entry.get().strip()
        if not text: return
        
        if text.lower().startswith("/clear"):
            parts = text.split()
            if len(parts) > 1 and parts[1].isdigit():
                self.log.configure(state="normal")
                self.log.delete(self.log.index(f'{self.log.index("end-1c")} - {int(parts[1])} lines'), "end")
                self.log.configure(state="disabled")
            elif messagebox.askyesno("Confirm Clear", "Are you sure you want to completely clear the chat log?"):
                self.photo_cache = []
                self.log.configure(state="normal")
                self.log.delete("1.0", "end")
                self.log.configure(state="disabled")
            
            self.msg_entry.delete(0, "end")
            self.destroy_suggestions()
            return

        self.msg_entry.delete(0, "end")
        self.destroy_suggestions()
        self._stop_typing_signal()
        self.connection.send_chat(clean_non_bmp(text))
        self._maybe_start_slowmode_cooldown()

    def on_entry_key(self, event=None):
        if event and event.keysym in ("Tab", "ISO_Left_Tab", "Up", "Down"): return "break"
        self.evaluate_live_suggestions()
        
        if not self.connection: return
        if self.msg_entry.get().strip():
            now = time.time()
            if not self.typing_active or (now - self.last_typing_sent > 1.0):
                self.connection.send_typing(True)
                self.typing_active, self.last_typing_sent = True, now

            if getattr(self, "_typing_timer", None):
                try: self.after_cancel(self._typing_timer)
                except Exception: pass
            self._typing_timer = self.after(2000, self._stop_typing_signal)
        else:
            self._stop_typing_signal()

    def on_attach_file(self):
        if not self.connection: return
        path = filedialog.askopenfilename(title="Choose a file to send")
        if not path: return
        try:
            self.connection.send_file(path)
            self._maybe_start_slowmode_cooldown()
        except ValueError as e: messagebox.showerror("File too large", str(e))
        except OSError as e: messagebox.showerror("Couldn't read file", str(e))

    BUILTIN_STICKERS = ["GG", "RIP", "HELLO", "WOW", "BRUH"]

    def on_sticker_picker(self):
        if Image is None or ImageDraw is None:
            return messagebox.showerror("Error", "Pillow (PIL) is required to use stickers.")

        if getattr(self, "_sticker_popup", None) is not None:
            try: self._sticker_popup.destroy()
            except: pass
            self._sticker_popup = None
            return

        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.configure(bg=BG_PANEL, padx=6, pady=6)
        self._sticker_popup = popup
        self._sticker_thumb_cache = {}  # keeps PhotoImage refs alive — Tk GCs them otherwise

        x, y = self.winfo_rootx() + self.bottom_bar.winfo_x() + 40, self.winfo_rooty() + self.bottom_bar.winfo_y() - 4
        popup.geometry(f"+{x}+{y-140}")

        grid = tk.Frame(popup, bg=BG_PANEL)
        grid.pack()

        col = 0
        for s in self.BUILTIN_STICKERS:
            btn = tk.Label(grid, text=s, font=BOLD_FONT, bg=BG_INPUT, fg=FG_TEXT, padx=10, pady=10, cursor="hand2", bd=1, relief="solid")
            btn.grid(row=0, column=col, padx=4, pady=4)
            btn.bind("<Button-1>", lambda e, name=s: self.send_sticker(name))
            btn.bind("<Enter>", lambda e, w=btn: w.configure(bg=BTN_NEUTRAL))
            btn.bind("<Leave>", lambda e, w=btn: w.configure(bg=BG_INPUT))
            col += 1

        custom = _load_custom_stickers()
        row, col = 1, 0
        for name, b64data in custom.items():
            try:
                img_bytes = base64.b64decode(b64data)
                thumb = Image.open(io.BytesIO(img_bytes)).resize((64, 64), Image.LANCZOS)
                photo = ImageTk.PhotoImage(thumb)
            except Exception:
                continue
            self._sticker_thumb_cache[name] = photo

            btn = tk.Label(grid, image=photo, bg=BG_INPUT, cursor="hand2", bd=1, relief="solid")
            btn.grid(row=row, column=col, padx=4, pady=4)
            btn.bind("<Button-1>", lambda e, name=name: self.send_sticker(name))
            btn.bind("<Button-3>", lambda e, name=name: self._delete_custom_sticker(name))
            btn.bind("<Enter>", lambda e, w=btn: w.configure(bg=BTN_NEUTRAL))
            btn.bind("<Leave>", lambda e, w=btn: w.configure(bg=BG_INPUT))
            col += 1
            if col >= 5:
                col, row = 0, row + 1

        upload_btn = tk.Label(grid, text="➕\nUpload", font=(CHAT_FONT[0], 9), bg=BG_INPUT, fg=FG_MUTED, padx=8, pady=8, cursor="hand2", bd=1, relief="solid")
        upload_btn.grid(row=row, column=col, padx=4, pady=4)
        upload_btn.bind("<Button-1>", lambda e: self.on_upload_sticker())
        upload_btn.bind("<Enter>", lambda e: upload_btn.configure(bg=BTN_NEUTRAL))
        upload_btn.bind("<Leave>", lambda e: upload_btn.configure(bg=BG_INPUT))

        if custom:
            tk.Label(popup, text="Right-click a custom sticker to delete it", bg=BG_PANEL, fg=FG_MUTED, font=(CHAT_FONT[0], 8)).pack(pady=(4, 0))

        popup.bind("<FocusOut>", lambda e: self._close_sticker_popup())
        popup.focus_set()

    def _close_sticker_popup(self):
        if getattr(self, "_sticker_popup", None):
            try: self._sticker_popup.destroy()
            except: pass
            self._sticker_popup = None

    def on_upload_sticker(self):
        path = filedialog.askopenfilename(
            title="Choose a sticker image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("All files", "*.*")]
        )
        if not path:
            return

        custom = _load_custom_stickers()
        if len(custom) >= MAX_CUSTOM_STICKERS:
            self._close_sticker_popup()
            return messagebox.showerror("Too many stickers", f"You can have at most {MAX_CUSTOM_STICKERS} custom stickers. Delete one first (right-click it).")

        name = simpledialog.askstring("Name this sticker", "Short name (shown as the filename when sent):", parent=self)
        if not name or not name.strip():
            return
        name = re.sub(r"[^A-Za-z0-9_\- ]", "", name.strip())[:20] or "sticker"

        try:
            img = Image.open(path).convert("RGB")
        except Exception as e:
            self._close_sticker_popup()
            return messagebox.showerror("Couldn't load image", str(e))

        img.thumbnail((240, 240), Image.LANCZOS)
        square = Image.new("RGB", (240, 240), color=BG_PANEL)
        square.paste(img, ((240 - img.width) // 2, (240 - img.height) // 2))
        bio = io.BytesIO()
        square.save(bio, format="JPEG", quality=88)

        custom[name] = base64.b64encode(bio.getvalue()).decode("ascii")
        _save_custom_stickers(custom)

        self._close_sticker_popup()
        self.on_sticker_picker()  # reopen, now showing the new sticker

    def _delete_custom_sticker(self, name):
        custom = _load_custom_stickers()
        if name in custom:
            del custom[name]
            _save_custom_stickers(custom)
        self._close_sticker_popup()
        self.on_sticker_picker()

    def send_sticker(self, name):
        self._close_sticker_popup()
        if not self.connection: return

        if name in self.BUILTIN_STICKERS:
            img = Image.new('RGB', (120, 120), color=BG_PANEL)
            d = ImageDraw.Draw(img)
            d.rectangle([5, 5, 115, 115], fill={"GG": "#57F287", "RIP": "#ED4245", "HELLO": "#5B8CFF", "WOW": "#FEE75C", "BRUH": "#FFA347"}.get(name, "#FFFFFF"), outline="white", width=3)
            d.text((10, 50), name, fill="black")
            bio = io.BytesIO()
            img.resize((240, 240), Image.NEAREST).save(bio, format="JPEG")
            img_bytes = bio.getvalue()
        else:
            custom = _load_custom_stickers()
            b64data = custom.get(name)
            if not b64data:
                return
            img_bytes = base64.b64decode(b64data)

        self.connection.send_file_bytes(f"Sticker_{name}.jpg", img_bytes)
        self._maybe_start_slowmode_cooldown()

    def on_emoji_picker(self):
        if getattr(self, "_emoji_popup", None) is not None:
            try: self._emoji_popup.destroy()
            except Exception: pass
            self._emoji_popup = None
            return

        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.configure(bg=BG_PANEL, padx=6, pady=6)
        self._emoji_popup = popup

        x, y = self.winfo_rootx() + self.bottom_bar.winfo_x() + 40, self.winfo_rooty() + self.bottom_bar.winfo_y() - 4
        popup.geometry(f"+{x}+{y-220}")

        grid = tk.Frame(popup, bg=BG_PANEL)
        grid.pack()
        
        for i, emoji_char in enumerate(EMOJI_PICKER_SET):
            btn = tk.Label(grid, text=emoji_char, font=EMOJI_FONT, bg=BG_PANEL, fg=FG_TEXT, padx=4, pady=4, cursor="hand2")
            btn.grid(row=i // 10, column=i % 10)
            btn.bind("<Button-1>", lambda e, ch=emoji_char: self._insert_emoji(ch))
            btn.bind("<Enter>", lambda e, w=btn: w.configure(bg=BTN_NEUTRAL))
            btn.bind("<Leave>", lambda e, w=btn: w.configure(bg=BG_PANEL))

        popup.bind("<FocusOut>", lambda e: self._close_emoji_popup())
        popup.focus_set()

    def _insert_emoji(self, emoji_char: str):
        self.msg_entry.insert("insert", emoji_char)
        self.msg_entry.focus_set()
        self._close_emoji_popup()

    def _close_emoji_popup(self):
        if getattr(self, "_emoji_popup", None) is not None:
            try: self._emoji_popup.destroy()
            except Exception: pass
            self._emoji_popup = None

    def poll_queue(self):
        try:
            while True:
                kind, payload = self.event_queue.get_nowait()
                if kind == "connect_success":
                    self.title_label.configure(text=f"Connected as {payload['name']} — Room {self.room_entry.get().strip()}")
                    self._transition_to_chat("join", payload['name'], self.room_entry.get().strip())
                elif kind == "connect_fail":
                    self.status_label.configure(text=payload, fg=COLOR_PALETTE["red"])
                    self._teardown_connection()
                elif kind == "chat":
                    self.known_colors.update(payload.get("colors") or {})
                    self.append_chat_line(payload["raw"], payload.get("msg_id"))
                elif kind == "react":
                    self.add_reaction(payload["msg_id"], payload["emoji"])
                elif kind == "system": self.append_system_line(payload)
                elif kind == "private": self.append_private_line(payload)
                elif kind == "roster": self.update_roster(payload)
                elif kind == "colormap":
                    self.known_colors.update(payload)
                    self.update_roster(self.current_roster)
                elif kind == "typing": self.update_typing(payload)
                elif kind == "ping": notify_ping(payload, root=self)
                elif kind == "file": self.render_incoming_file(payload["sender"], payload["filename"], payload["data"])
                elif kind == "disconnected": self._handle_disconnected(payload)
                elif kind == "slowmode":
                    self.slowmode_delay = payload
                    if payload == 0.0: self._end_slowmode_cooldown()
                elif kind == "admin_status":
                    self.is_admin = (payload == "1")
                    if self.connection: self.connection.is_admin = self.is_admin 
                    self.append_system_line(f"Your admin privileges have been {'granted' if self.is_admin else 'revoked'}.")
                elif kind == "mute_status":
                    if payload == "0": self._apply_mute_state(False)
                    else:
                        try: until = float(payload.partition(":")[2])
                        except ValueError: until = 0.0
                        self._apply_mute_state(True, until)
                elif kind == "update_check_result": self._handle_update_check_result(payload)
                elif kind == "update_apply_result": self._handle_update_apply_result(payload)
        except queue.Empty: pass
        self.after(50, self.poll_queue)

    def _color_tag(self, color_hex: str) -> str:
        tag = f"c_{color_hex.lstrip('#')}"
        if tag not in self.known_tags:
            self.log.tag_configure(tag, foreground=color_hex)
            self.known_tags.add(tag)
        return tag

    def append_chat_line(self, raw: str, msg_id: str = None):
        self.log.configure(state="normal")
        start_index = self.log.index("end-1c")
        
        raw_safe = clean_non_bmp(raw)
        self.log.insert("end", f"[{time.strftime('%H:%M')}] ", ("timestamp",))
        
        if ": " in raw_safe:
            prefix, rest = raw_safe.split(": ", 1)
            self._record_user_message_time(prefix)
            self.log.insert("end", prefix, (self._color_tag(self.known_colors.get(prefix.lower(), FG_TEXT)),))
            self.log.insert("end", ": " + rest)
            
            align_tag = "align_right" if prefix.lower() == self.my_name.lower() else "align_left"
            if align_tag not in self.known_tags:
                self.log.tag_configure(align_tag, justify="right" if align_tag == "align_right" else "left")
                self.known_tags.add(align_tag)
            
            end_index = self.log.index("end-1c")
            self.log.tag_add(align_tag, start_index, end_index)
            
            if msg_id:
                tag_name = f"msg_{msg_id}"
                self.log.tag_add(tag_name, start_index, end_index)
                self.log.tag_bind(tag_name, "<Button-3>", lambda e, mid=msg_id: self.show_reaction_menu(e, mid))
                self.log.tag_bind(tag_name, "<Button-2>", lambda e, mid=msg_id: self.show_reaction_menu(e, mid))
                
                self.log.mark_set(f"react_mark_{msg_id}", end_index)
                self.log.mark_gravity(f"react_mark_{msg_id}", "left")
        else:
            self.log.insert("end", raw_safe)

        self.log.insert("end", "\n")
        self.log.configure(state="disabled")
        self.log.see("end")

    def show_reaction_menu(self, event, msg_id):
        menu = tk.Menu(self, tearoff=0, bg=BG_PANEL, fg=FG_TEXT)
        for emoji in ["😀", "😂", "❤️", "👍", "🔥", "😢", "😡"]:
            menu.add_command(label=emoji, command=lambda e=emoji: self.send_reaction(msg_id, e))
        try: menu.tk_popup(event.x_root, event.y_root)
        finally: menu.grab_release()

    def send_reaction(self, msg_id, emoji):
        if not self.connection: return
        if hasattr(self.connection, "send_react"): self.connection.send_react(msg_id, emoji)
        else:
            try: send_encrypted(self.connection.sock, self.connection.fernet, f"{REACT_PREFIX}{msg_id}|{emoji}")
            except OSError: pass

    def add_reaction(self, msg_id, emoji):
        counts = self.message_reactions.setdefault(msg_id, {})
        counts[emoji] = counts.get(emoji, 0) + 1
        self.render_reactions(msg_id)

    def render_reactions(self, msg_id):
        mark_name = f"react_mark_{msg_id}"
        try: self.log.index(mark_name)
        except tk.TclError: return 
        
        react_tag = f"react_text_{msg_id}"
        self.log.configure(state="normal")
        
        ranges = self.log.tag_ranges(react_tag)
        if ranges: self.log.delete(ranges[0], ranges[1])
        
        if counts := self.message_reactions[msg_id]:
            self.log.insert(mark_name, "  [" + " ".join(f"{e} {c}" for e, c in counts.items()) + "]", (react_tag, "reaction_style"))
        
        self.log.configure(state="disabled")

    def append_system_line(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", f"* {clean_non_bmp(text)}\n", ("system",))
        self.log.configure(state="disabled")
        self.log.see("end")

    def append_private_line(self, text: str):
        self.log.configure(state="normal")
        self.log.insert("end", f"[private] {clean_non_bmp(text)}\n", ("private",))
        self.log.configure(state="disabled")
        self.log.see("end")

    def render_incoming_file(self, sender: str, filename: str, data: bytes):
        self.log.configure(state="normal")
        
        align_tag = "align_right" if sender.lower() == self.my_name.lower() else "align_left"
        if align_tag not in self.known_tags:
            self.log.tag_configure(align_tag, justify="right" if align_tag == "align_right" else "left")
            self.known_tags.add(align_tag)

        start_index = self.log.index("end-1c")
        self.log.insert("end", f"[{time.strftime('%H:%M')}] ", ("timestamp",))
        self.log.insert("end", sender, (self._color_tag(self.known_colors.get(sender.lower(), FG_TEXT)),))
        self.log.insert("end", f" sent an attachment ({clean_non_bmp(filename)}):\n")

        if Image is not None and filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")):
            try:
                img = Image.open(io.BytesIO(data))
                img.thumbnail((260, 260))
                photo = ImageTk.PhotoImage(img)
                self.photo_cache.append(photo)
                self.log.image_create("end", image=photo)
                
                img_tag = f"img_{len(self.photo_cache)}"
                self.log.tag_add(img_tag, self.log.index("end-2c"), self.log.index("end-1c"))
                for bind in ["<Button-2>", "<Button-3>"]:
                    self.log.tag_bind(img_tag, bind, lambda e, d=data, fn=filename: self._show_image_context_menu(e, d, fn))
                
                self.log.insert("end", "\n\n")
                self.log.tag_add(align_tag, start_index, self.log.index("end-1c"))
                self.log.configure(state="disabled")
                self.log.see("end")
                return
            except Exception: pass

        embed = tk.Frame(self.log, bg=BG_PANEL, bd=1, relief="solid", padx=12, pady=8)
        tk.Label(embed, text=f"📁  {clean_non_bmp(filename)}", bg=BG_PANEL, fg=FG_TEXT, font=BOLD_FONT).pack(side="left", padx=(0, 14))
        tk.Label(embed, text=f"({len(data) / 1024:.1f} KB)", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(side="left", padx=(0, 14))
        make_button(embed, "Download", lambda d=data, fn=filename: self._save_file_to_disk(d, fn), bg=BTN_GREEN, hover_bg=BTN_GREEN_HOVER, padx=10, pady=4).pack(side="right")

        self.log.window_create("end", window=embed)
        self.log.insert("end", "\n\n")
        self.log.tag_add(align_tag, start_index, self.log.index("end-1c"))
        
        self.log.configure(state="disabled")
        self.log.see("end")

    def _save_file_to_disk(self, data: bytes, filename: str):
        if path := filedialog.asksaveasfilename(initialfile=filename, title="Save file as"):
            try:
                with open(path, "wb") as f: f.write(data)
                messagebox.showinfo("Saved", f"File saved to:\n{path}")
            except OSError as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")

    def _show_image_context_menu(self, event, data: bytes, filename: str):
        menu = tk.Menu(self, tearoff=0, bg=BG_PANEL, fg=FG_TEXT, activebackground=BTN_NEUTRAL, activeforeground=FG_TEXT)
        menu.add_command(label="Save Image As...", command=lambda: self._save_file_to_disk(data, filename))
        try: menu.tk_popup(event.x_root, event.y_root)
        finally: menu.grab_release()

    def update_roster(self, names):
        self.current_roster = [self.my_name] + sorted(n for n in names if n.lower() != self.my_name.lower())
        for child in self.member_list_frame.winfo_children(): child.destroy()
        for n in self.current_roster:
            tk.Label(self.member_list_frame, text=clean_non_bmp(n), bg=BG_PANEL, fg=self.known_colors.get(n.lower(), FG_TEXT), anchor="w", font=CHAT_FONT).pack(fill="x", pady=2)

    def update_typing(self, names):
        now = time.time()
        for n in names:
            if n.lower() != self.my_name.lower(): self.typing_last_seen[n] = now
        self._render_typing_var()

    def _render_typing_var(self):
        active = [n for n, seen in self.typing_last_seen.items() if time.time() - seen <= TYPING_DISPLAY_TIMEOUT]
        if not active: self.typing_var.set("")
        elif len(active) == 1: self.typing_var.set(f"{clean_non_bmp(active[0])} is typing...")
        else: self.typing_var.set(f"{', '.join(clean_non_bmp(n) for n in active)} are typing...")

    def _typing_prune_loop(self):
        stale = [n for n, seen in self.typing_last_seen.items() if time.time() - seen > TYPING_DISPLAY_TIMEOUT]
        for n in stale: del self.typing_last_seen[n]
        if stale: self._render_typing_var()
        self.after(500, self._typing_prune_loop)


def main():
    app = ChatApp()
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback
        traceback.print_exc()
        try: input("\nSomething crashed (see above). Press Enter to close this window...")
        except Exception: pass
        sys.exit(1)
