#!/usr/bin/env python3
"""
chat_gui.py — v1.5.1 — ENCRYPTED instant messenger with a desktop GUI.

Changes in 1.5.1:
- Appearance (new): a 🎨 button in the chat, an "Appearance" link on the main menu, or Ctrl+Shift+T. Pick a theme
  (Midnight, Graphite, Ocean, Forest, Plum, Mocha, Rose) or make your own from a background and an accent colour;
  choose any font installed on your computer and a text size; put a picture behind the main menu. The window
  can be resized and scrolls, so it fits short screens. It changes instantly, applies only on your computer, and is remembered after you close the app.
- Bans, reworked: they are now saved on the host's computer, so they survive restarting the chat. A ban covers the
  person's address AND their device, so getting a new IP no longer gets them back in. /ban and /ipban accept a
  name (even of someone who has just left) or an IP. New: /bans lists who is banned; /unban takes the number from
  that list, a name or an IP. The banned person still gets their ban screen, appeal and "you've been unbanned"
  notice exactly as before.
- Banning from the whole app (publisher only): /globalban <name or device id> [time|perm] [reason], /unglobalban and
  /globalbans. They go through the report server (no more uploading a file by hand), for a set time or until lifted.
  Every running copy checks every ~20 seconds; a banned device is removed from any chat at once and shown who
  banned it for what, and until when. Needs the signing key file and the admin password.
- Windows look: text is sharp on scaled displays (it used to be stretched, which looked pixelated), the bright
  borders round the text boxes and the bright grey scrollbars are gone, title bars are dark, and the chat has
  a little more breathing room. macOS keeps its native look.
- Another secret gradient name colour (ocean blue to sea green).

Changes in 1.5.0f:
- Announcements: the publisher opens a menu with Ctrl+Shift+A and the admin password, types a message, and
  every running copy of the app shows it as a banner across the top of the window — in a chat or on the main
  menu. Copies refresh every 20 minutes, or on demand from "Announcements" on the main menu (once every 20
  seconds). Mark it urgent and the banner flashes red and white, the window jumps to the front (even on
  Do Not Disturb) and it arrives within about 2 minutes instead of waiting for the next refresh. Optionally
  it expires after 1 hour / 1 day / 7 days. Announcements are signed with your update signing key, so
  nobody who only learns the password can publish one. It needs the internet (it uses the report server).
- Restore a previous version: a link on the main menu (admin password) lists the earlier versions kept on
  this computer, or restores the last one in one click. The version you were running is kept too, so you
  can go forward again. Backups kept: the newest 5 (was 1).
- Old entries at the top of this file are trimmed with each release; the in-app changelog is untouched.
- The report server's address is now filled in.

Changes in 1.5.0e:
- The "your report was completed" window now says when it was completed ("3 minutes ago" plus the date
  and time, in your own time zone).
- The home-screen link is now "Report a bug, suggest a feature, or view your previous reports". It opens
  a small menu: send a new report, or open "My previous reports" — a list of everything this computer
  has sent, with whether each is still open or completed (and when), and a Refresh button that asks the
  report server right now instead of waiting for the 10-minute check. Refresh can be used once every
  30 seconds.
- Report server: it now records when a report was marked completed. If you set up an earlier version, it
  adds the new column to your database by itself — just re-paste report_worker.js and Deploy.

Changes in 1.5.0d:
- Updates are checked for when the app starts, and an available update shows on the main menu as a
  banner ("✨ Update available: v1.5.0e — Update now · What's new") instead of a pop-up. The
  "Check for Updates" link uses the same banner. (Version letters already worked from a to z — only a
  comment said a-d.)
- Old update backups (chat_gui.py.bak-…) are cleaned up automatically: the newest one is kept as a
  safety net, the rest are deleted — at launch and right after each update.
- When a bug report or suggestion you sent is marked completed, a window tells you so and that it will
  be released in the next update. (Your app checks quietly, at launch and every 10 minutes.)
- Report inbox owner: tick "Tell me when a new report arrives" in the inbox and a slim bar at the top of
  the window — in a chat or not — flashes green and white for 5 seconds for each new report. Bursts are
  collapsed into one notice (more than 5 at once), and no more than 5 notices show per minute.
- Report server (Worker) anti-abuse: at most 5 reports per minute and 10 per 10 minutes from one sender,
  and 30 per minute from everyone; extras are refused. Re-deploy the updated report_worker.js.

Changes in 1.5.0c:
- Game leaderboards show how many people are playing right now ("● 2 playing") instead of a
  "playing — score" tag on every row.
- Joining by Room Code is more forgiving and clearer: spaces, dashes, line breaks and full-width
  digits are ignored, and the error says what's actually wrong ("you've entered 5 digits", or
  "each half has to be 000–255") instead of always saying "must be 6 digits".
- Hosts now prefer a fixed port, so a joiner whose Wi-Fi blocks the UDP lookup can still find the
  room with plain TCP, and connection failures explain themselves ("no answer — Wi-Fi may be
  blocking devices from talking to each other" vs "nothing is listening there").
- New: "Report a bug or suggest a feature" on the home screen — pick bug or suggestion, say what it
  is, add detail if you like. The date, version and OS are added automatically. Reports are saved
  on the computer they were written on and, if REPORT_WORKER_URL points at your report server (the
  free Cloudflare Worker in report_worker.js), sent there too. Ctrl+Shift+B opens the report inbox
  (password protected) — with a report server set, it shows everyone's reports.

Changes in 1.5.0b:
- Durations in /mute, /ban and /ipban now take units: 30 (minutes, as before), 90m, 2h, 7d, 2w,
  3mo, 1y. Months and years are calendar ones — "1y" ends at the same date and time next year.
  (A year typed as a number of minutes is easy to get slightly wrong: 365 days is 525,600 minutes,
  and 8,765 hours' worth lands 5 hours late.)
- /unwarn no longer guesses: with more than one active warning it lists them and asks which to
  remove (/unwarn <name> <#>, or /unwarn <name> all). With just one, it removes that one.
- Several warnings at once: the ⚠ button now shows all your active warnings ("⚠ Warnings #1, #3").
  With more than one, clicking it opens a menu of them; pick one to see who warned you, why, its
  appeal status, and to appeal it. Warnings (and their appeal status) are remembered by the host,
  so they're still there if you leave and rejoin the chat.

Changes in 1.5.0a:
- Toast notifications for moderation outcomes: a warning appeal accepted or rejected, being banned,
  a ban appeal rejected, and being unbanned (including by an accepted appeal). Not shown while
  Do Not Disturb is on.
- Warnings, mutes, kicks and bans now jump to the front of everything (even if the app was
  minimised) with a notice window — unless you were on Do Not Disturb, in which case they wait
  quietly until you next open the window, as before.
- Fixed: times in mute / ban messages (and the admin log, /history and /appeals) were written in the
  HOST's time zone, so they could be hours out for everyone else. They're now sent as a duration and
  turned into your own local time on your own computer.
- The ban message names the host ("…the chat hosted by Richy…") instead of their IP address.
- The ⚠ button shows "appeal rejected" for 3 seconds after its flash, then goes back to
  "⚠ Warning #N".
- /warning is now /warnings: it lists your warnings — current and previous, with what happened to
  each. Admins can add a name (/warnings Bob). The host can't be warned, so /warnings tells them so.
- Recent chats keeps one entry per room you've joined (two different rooms show as two); joining the
  same room again just refreshes its entry.
- Fixed: the Changelog window could show the notes typed when signing a release instead of the
  built-in changelog. The built-in changelog now always wins.
"""

import sys
import os
import io
import itertools
import socket
import threading
import queue
import select
import time
import re
import random
import math
import datetime
import calendar
import colorsys
import unicodedata
import base64
import hashlib
import importlib
import subprocess
import json
import shutil
import tempfile
import platform
import uuid
import urllib.request
import urllib.error
import traceback
import tkinter as tk
import tkinter.font as tkfont
from contextlib import contextmanager
from tkinter import colorchooser, filedialog, messagebox, scrolledtext, simpledialog

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
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey, Ed25519PrivateKey
from cryptography.exceptions import InvalidSignature

ensure_installed("plyer", required=False)
try:
    from plyer import notification as _plyer_notification
except ImportError:
    _plyer_notification = None

ensure_installed("PIL", pip_name="Pillow", required=False)
try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageGrab
except ImportError:
    Image = ImageTk = ImageDraw = ImageFont = ImageGrab = None

if sys.platform == "darwin":
    ensure_installed("pyobjus", required=False)

VERSION = "1.5.1"

APP_DIR = os.path.dirname(os.path.abspath(__file__))

def app_path(filename: str) -> str:
    return os.path.join(APP_DIR, filename)

def load_json(path: str, expected_type: type):
    """Reads a small JSON file; returns an empty `expected_type()` if it's
    missing, unreadable, or holds the wrong kind of value."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):  # JSONDecodeError/UnicodeDecodeError are ValueErrors
        return expected_type()
    return data if isinstance(data, expected_type) else expected_type()

def save_json(path: str, data, **dump_kwargs) -> bool:
    """Writes via a temp file + atomic replace so a crash mid-write can't
    leave a half-written (and so unreadable) file behind."""
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, **dump_kwargs)
        os.replace(tmp, path)
        return True
    except OSError:
        return False
MSG_LEN_BYTES = 4
MAX_GUESTS = 15
MAX_MESSAGE_CHARS = 4000  # one chat message / whisper / edit — a multi-megabyte paste would otherwise freeze everyone's window
MAX_FILE_BYTES = 1024 * 1024 * 1024   # 1 GB — files are streamed in chunks, so this really is the limit
FILE_CHUNK_BYTES = 512 * 1024          # raw bytes per chunk (each chunk is its own encrypted frame)
INLINE_FILE_BYTES = 16 * 1024 * 1024   # received files up to this size are held in memory (instant preview/save); bigger ones live in a temp file
TRANSFER_WINDOW_BYTES = 16 * 1024 * 1024  # a sender pauses while this much is already queued for a recipient
TRANSFER_STALL_SECONDS = 120           # a recipient that can't drain their queue for this long is skipped for that one file (they stay connected)
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
ENABLE_INVITE_CODES = False   # Invite Codes (a longer code holding a room's full address) are built but switched off: Room Codes only, for now
DEFAULT_TCP_PORT = 47615   # hosts try this port first, so a joiner can reach them with TCP alone if the UDP lookup is blocked

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

# ---- Platform polish: sharp text on Windows, dark title bars, and the text-size helper ----
DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE = CHAT_FONT[0], CHAT_FONT[1]
FONT_DELTA = 0      # points the chosen text size is above the platform default (Appearance window)
UI_SCALE = 1.0      # Windows display scaling (1.0 = 96 dpi). Pixel sizes are multiplied by it; text (points) scales by itself.

def px(n) -> int:
    return int(round(n * UI_SCALE))

def fnt(size: int, *styles) -> tuple:
    """A font in the current family, `size` points at the default text size (so it follows the chosen size)."""
    return (CHAT_FONT[0], max(6, size + FONT_DELTA), *styles)

def enable_hidpi():
    """Windows only, and before the first window exists: tell Windows this app draws its own pixels. Without
    this Windows renders the whole window small and stretches it up on a scaled display (125%/150%), which is
    exactly what makes text look soft and pixelated."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        try:
            ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))   # per-monitor v2 (Windows 10 1703+)
        except Exception:
            try: ctypes.windll.shcore.SetProcessDpiAwareness(2)                       # per-monitor (8.1+)
            except Exception: ctypes.windll.user32.SetProcessDPIAware()               # system-wide (older)
    except Exception:
        pass

def init_ui_scale(root):
    global UI_SCALE
    if sys.platform == "win32":
        try: UI_SCALE = max(1.0, min(3.0, root.winfo_fpixels("1i") / 96.0))
        except tk.TclError: UI_SCALE = 1.0

def _colorref(hex_color: str) -> int:
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return r | (g << 8) | (b << 16)

def style_titlebar(win):
    """Windows 10/11: a dark title bar (and on Windows 11 one in the theme's own colours) instead of the bright
    system one. Does nothing anywhere else, and never raises."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        win.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(win.winfo_id()) or win.winfo_id()
        dwm = ctypes.windll.dwmapi
        def set_attr(attr, value):
            v = ctypes.c_uint(value)
            return dwm.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(v), ctypes.sizeof(v))
        if set_attr(20, 1) != 0:   # DWMWA_USE_IMMERSIVE_DARK_MODE (the id was 19 before Windows 10 20H1)
            set_attr(19, 1)
        set_attr(35, _colorref(BG_PANEL))   # caption colour  (Windows 11 only; ignored elsewhere)
        set_attr(36, _colorref(FG_TEXT))    # caption text
        set_attr(34, _colorref(BG_PANEL))   # window border
    except Exception:
        pass

class Toplevel(tk.Toplevel):
    """tk.Toplevel that gets the same dark title bar as the main window on Windows."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if sys.platform == "win32":
            self.after_idle(self._style)
    def _style(self):
        try: style_titlebar(self)
        except tk.TclError: pass

class FlatScrollbar(tk.Canvas):
    """A slim, flat scrollbar in the theme's colours. (Windows' native one is a bright grey bar that clashes with a
    dark window.) Same interface as tk.Scrollbar for what the app uses: set() and a `command`."""
    def __init__(self, master, command=None, bg=None, **kw):
        super().__init__(master, width=px(11), height=1, highlightthickness=0, bd=0, bg=bg or BG_DARK, cursor="arrow", **kw)
        self.command = command
        self._first, self._last = 0.0, 1.0
        self._drag = None
        self._hover = False
        self._thumb = self.create_polygon(0, 0, 0, 0, smooth=True, fill=BTN_NEUTRAL, outline="", state="hidden")
        self.bind("<Configure>", lambda e: self._draw())
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<B1-Motion>", self._motion)
        self.bind("<ButtonRelease-1>", self._release)

    def set(self, first, last):
        self._first, self._last = float(first), float(last)
        self._draw()

    def retheme(self):
        self._paint()

    def _paint(self):
        self.itemconfigure(self._thumb, fill=BTN_NEUTRAL_HOVER if (self._hover or self._drag) else BTN_NEUTRAL)

    def _set_hover(self, on):
        self._hover = on
        self._paint()

    def _geometry(self):
        h, pad = max(1, self.winfo_height()), px(2)
        span = self._last - self._first
        avail = max(1, h - 2 * pad)
        tlen = min(avail, max(px(28), span * avail))
        top = pad + ((self._first / (1.0 - span)) * (avail - tlen) if span < 0.999 else 0)
        return top, tlen, avail, span

    def _draw(self):
        top, tlen, avail, span = self._geometry()
        if span >= 0.999:
            self.itemconfigure(self._thumb, state="hidden")
            return
        w, inset = max(1, self.winfo_width()), px(2)
        x1, x2, y1, y2, r = inset, w - inset, top, top + tlen, max(2, (w - 2 * inset) // 2)
        pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
        self.coords(self._thumb, *pts)
        self.itemconfigure(self._thumb, state="normal")
        self._paint()

    def _press(self, event):
        top, tlen, avail, span = self._geometry()
        if span >= 0.999 or not self.command:
            return
        if top <= event.y <= top + tlen:
            self._drag = (event.y, self._first)
            self._paint()
        else:
            self.command("scroll", -1 if event.y < top else 1, "pages")

    def _motion(self, event):
        if not self._drag or not self.command:
            return
        top, tlen, avail, span = self._geometry()
        room = max(1, avail - tlen)
        start_y, start_first = self._drag
        self.command("moveto", max(0.0, min(1.0 - span, start_first + (event.y - start_y) / room * (1.0 - span))))

    def _release(self, event):
        self._drag = None
        self._paint()

class DarkScrolledText(tk.Text):
    """tk.Text with a FlatScrollbar beside it — the same recipe (and the same methods) as the standard
    ScrolledText, which is where the bright native scrollbar comes from."""
    def __init__(self, master=None, **kw):
        self.frame = tk.Frame(master, bg=kw.get("bg") or BG_DARK)
        self.vbar = FlatScrollbar(self.frame, bg=kw.get("bg"))
        self.vbar.pack(side="right", fill="y")
        kw["yscrollcommand"] = self.vbar.set
        super().__init__(self.frame, **kw)
        self.pack(side="left", fill="both", expand=True)
        self.vbar.command = self.yview
        text_meths = vars(tk.Text).keys()
        methods = vars(tk.Pack).keys() | vars(tk.Grid).keys() | vars(tk.Place).keys()
        for m in methods.difference(text_meths):
            if m[0] != "_" and m not in ("config", "configure"):
                setattr(self, m, getattr(self.frame, m))
    def __str__(self):
        return str(self.frame)

# macOS keeps its own scrollbar (it overlays and fades, and already looks right); Windows and Linux get the flat one.
ScrolledText = scrolledtext.ScrolledText if sys.platform == "darwin" else DarkScrolledText

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
FILE_PREFIX = "__FILE__:"            # start of a transfer: "sender|msg_id|to|filename|size"
FILECHUNK_PREFIX = "__FCHUNK__:"     # "msg_id|index|base64 bytes"
FILEEND_PREFIX = "__FEND__:"         # "msg_id"
FILEABORT_PREFIX = "__FABORT__:"     # "msg_id|reason" — the transfer is dead, discard what you have
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
RAINBOW_UNLOCK_PREFIX = "__RAINBOW_UNLOCK__:"
BLUE_UNLOCK_PREFIX = "__BLUE_UNLOCK__:"
EMBER_UNLOCK_PREFIX = "__EMBER_UNLOCK__:"
AURORA_UNLOCK_PREFIX = "__AURORA_UNLOCK__:"
VOLCANIC_UNLOCK_PREFIX = "__VOLCANIC_UNLOCK__:"
FINGERPRINT_PREFIX = "__FINGERPRINT__:"
EDIT_PREFIX = "__EDIT__:"          # guest -> host: "msg_id|new text"; host -> clients: "msg_id|editor|new text"
DELETE_PREFIX = "__DELETE__:"      # guest -> host: "msg_id";          host -> clients: "msg_id|deleter"
REPORT_PREFIX = "__REPORT__:"        # guest -> host: "msg_id|reason"
REPLYTO_PREFIX = "__REPLYTO__:"      # guest -> host: "msg_id|target_msg_id" (sent right after the reply itself)
REPLY_PREFIX = "__REPLY__:"          # host -> clients: "msg_id|target_msg_id|author|snippet"
BANCHECK_PREFIX = "__BANCHECK__:"    # a banned person's app -> host (first frame of a fresh connection): "are we still banned?"
BANSTATUS_PREFIX = "__BANSTATUS__:"  # host -> that app: JSON {"state": banned|unbanned|free, "by", "reason", "appeal"}
BAN_POLL_SECONDS = 6                 # how often a banned person's screen asks the host
APPEAL_PREFIX = "__APPEAL__:"        # a JSON appeal for a ban (first frame of a fresh connection) or a warning (when connected)
NICK_PREFIX = "__NICK__:"            # guest -> host: "new nickname"
RENAME_PREFIX = "__RENAME__:"        # host -> everyone: "old|new|renamed_by"
WARN_PREFIX = "__WARN__:"            # host -> the warned person: "by|warning_number|reason"
SNAKE_PREFIX = "__SNAKE__:"        # guest -> host: "score|playing"; host -> clients: "name|best|score|playing"
FLAPPY_PREFIX = "__FLAPPY__:"      # same shape as SNAKE_PREFIX, for the Flappy Bird leaderboard (1.4.11+)
GAME_PREFIXES = {"snake": SNAKE_PREFIX, "flappy": FLAPPY_PREFIX}
WARNSYNC_PREFIX = "__WARNSYNC__:"    # host -> a (re)joining person: JSON list of their active warnings (1.5.0b+)
WARNSTATE_PREFIX = "__WARNSTATE__:"  # host -> the warned person: "warning_number|removed" or "warning_number|rejected" (1.4.11+)
APPEAL_SENT_TEXT = "Your appeal was sent to the host and admins."
APPEAL_MISSING_TEXT = "There's no such warning to appeal, or you've already appealed it."
APPEAL_UNREADABLE_TEXT = "That appeal couldn't be read."
APPEAL_REPLY_TEXTS = (APPEAL_SENT_TEXT, APPEAL_MISSING_TEXT, APPEAL_UNREADABLE_TEXT)
WHISPER_PREFIX = "__WHISPER__:"    # guest -> host: "msg_id|target|text"; host -> both parties: "msg_id|from|to|text"
FEATURES_PREFIX = "__FEATURES__:"  # each side announces optional features it understands
FEATURE_EDIT = "edit"              # edit/delete of messages (added in 1.4.9b)
FEATURE_FILES = "files"            # chunked file transfers (1.4.10b+) — older clients would show every chunk as a chat line
FEATURE_REPLY = "reply"            # reply-to-message quotes (1.4.10b+)
FEATURE_FLAPPY = "flappy"          # Flappy Bird leaderboard frames (1.4.11+) — older clients would show them as chat lines
FEATURE_WARNSYNC = "warnsync"      # warning removed/rejected notices that drive the ⚠ button (1.4.11+)
HOST_FEATURES = frozenset({FEATURE_EDIT, FEATURE_FILES, FEATURE_REPLY, FEATURE_FLAPPY, FEATURE_WARNSYNC})
GAME_FEATURES = {"snake": None, "flappy": FEATURE_FLAPPY}  # which feature a client needs to hear a game's leaderboard

# ---- Secret gradient unlocks ----
# Typed into the "Host IP" field on the join screen instead of an actual
# address. Letters + symbols only (no digits) so they can never collide
# with a real IP:port and misfire the discovery/parsing logic below.
# Deliberately kept out of the changelog text (see EMBEDDED_CHANGELOG) —
# describe the feature there, never the literal codes.
RAINBOW_SECRET_CODE = ":prism:"
BLUE_SECRET_CODE = ":glacier:"
EMBER_SECRET_CODE = ":ember:"
AURORA_SECRET_CODE = ":aurora:"
VOLCANIC_SECRET_CODE = ":volcanic:"
# Stored in place of a hex color for an unlocked user — every place
# that renders a name checks GRADIENT_PALETTES for its color_value and
# draws the matching gradient instead of a flat color.
RAINBOW_SENTINEL = "RAINBOW"
BLUE_SENTINEL = "BLUE_GRADIENT"
EMBER_SENTINEL = "EMBER_GRADIENT"
AURORA_SENTINEL = "AURORA_GRADIENT"
VOLCANIC_SENTINEL = "VOLCANIC_GRADIENT"
RAINBOW_PALETTE = ["#FF5555", "#FFA347", "#FFE066", "#57F287", "#00C8C8", "#5B8CFF", "#C77DFF"]
BLUE_PALETTE = ["#0B2545", "#13315C", "#134074", "#1B5299", "#3E7CB1", "#6D9DC5", "#8FC0E9"]
EMBER_PALETTE = ["#7A1F1F", "#B3261E", "#E8472A", "#FF7A33", "#FFA94D", "#FFD166", "#FFE9A8"]    # deep red -> gold
VOLCANIC_PALETTE = ["#2F6FE0", "#2F8BE0", "#2AA5D6", "#26BDC0", "#2ED3A0", "#4BE38A", "#86F09A"]    # ocean blue -> teal -> sea green
AURORA_PALETTE = ["#2EE59D", "#1FD1B4", "#22B8D6", "#4C8DF0", "#7C6CF2", "#A855F7", "#D946EF"]    # green -> teal -> blue -> violet
GRADIENT_PALETTES = {
    RAINBOW_SENTINEL: RAINBOW_PALETTE, BLUE_SENTINEL: BLUE_PALETTE,
    EMBER_SENTINEL: EMBER_PALETTE, AURORA_SENTINEL: AURORA_PALETTE,
    VOLCANIC_SENTINEL: VOLCANIC_PALETTE,
}
# code -> (sentinel, unlock prefix to send once connected)
GRADIENT_UNLOCK_CODES = {
    RAINBOW_SECRET_CODE: (RAINBOW_SENTINEL, RAINBOW_UNLOCK_PREFIX),
    BLUE_SECRET_CODE: (BLUE_SENTINEL, BLUE_UNLOCK_PREFIX),
    EMBER_SECRET_CODE: (EMBER_SENTINEL, EMBER_UNLOCK_PREFIX),
    AURORA_SECRET_CODE: (AURORA_SENTINEL, AURORA_UNLOCK_PREFIX),
    VOLCANIC_SECRET_CODE: (VOLCANIC_SENTINEL, VOLCANIC_UNLOCK_PREFIX),
}

# ---- Minigames: Snake and Flappy Bird (each person plays their own game; the leaderboards are shared live) ----
GAMES_KEYBIND = "<Control-Shift-KeyPress-S>"   # opens the game picker — in a chat or on the home screen
SNAKE_COLS = 24
SNAKE_ROWS = 18
SNAKE_CELL_PX = 20
SNAKE_TICK_MS = 130
FLAPPY_TICK_MS = 20
SETTINGS_FILE = app_path("chat_gui_settings.json")
BANS_FILE = app_path("chat_gui_bans.json")   # the host's ban list — kept between sessions (1.5.1)

class SnakeGame:
    """Pure game logic — no Tk, no I/O, fully deterministic given a
    fixed random seed. head is body[0]."""

    def __init__(self, cols=SNAKE_COLS, rows=SNAKE_ROWS, rng=None):
        self.cols, self.rows = cols, rows
        self.rng = rng or random
        self.reset()

    def reset(self):
        cx, cy = self.cols // 2, self.rows // 2
        self.body = [(cx, cy), (cx - 1, cy), (cx - 2, cy)]
        self.direction = (1, 0)
        self.pending_direction = (1, 0)
        self.alive = True
        self.score = 0
        self.food = self._random_free_cell()

    def _random_free_cell(self):
        occupied = set(self.body)
        free = [(x, y) for x in range(self.cols) for y in range(self.rows) if (x, y) not in occupied]
        return self.rng.choice(free) if free else None

    def set_direction(self, dx: int, dy: int):
        cur_dx, cur_dy = self.direction
        if (dx, dy) == (-cur_dx, -cur_dy):
            return  # ignore instant 180-degree reversal
        self.pending_direction = (dx, dy)

    def tick(self):
        if not self.alive:
            return
        self.direction = self.pending_direction
        hx, hy = self.body[0]
        dx, dy = self.direction
        nx, ny = hx + dx, hy + dy

        if not (0 <= nx < self.cols and 0 <= ny < self.rows):
            self.alive = False
            return

        new_head = (nx, ny)
        grew = new_head == self.food
        # The tail cell vacates this tick unless we're growing, so it's a
        # legal move even though it's currently occupied.
        collision_zone = self.body if grew else self.body[:-1]
        if new_head in collision_zone:
            self.alive = False
            return

        self.body.insert(0, new_head)
        if grew:
            self.score += 1
            self.food = self._random_free_cell()
        else:
            self.body.pop()


class FlappyGame:
    """Flappy Bird logic — no Tk, no I/O, deterministic given a seeded rng. One tick is one
    frame (FLAPPY_TICK_MS). The bird waits in place until the first flap."""

    WIDTH, HEIGHT, GROUND = 320, 440, 40
    BIRD_X, BIRD_R = 80, 10
    GRAVITY, FLAP_V, MAX_FALL = 0.42, -6.6, 9.0
    PIPE_W, GAP, SPEED, SPACING = 54, 124, 2.5, 175
    EDGE_MARGIN = 45     # a gap's centre never gets closer than this (plus half a gap) to the ceiling or ground
    MAX_SHIFT = 130      # ...and never jumps further than this from the previous gap, so every pipe is reachable

    def __init__(self, rng=None):
        self.rng = rng or random
        self.reset()

    def reset(self):
        self.bird_y = (self.HEIGHT - self.GROUND) / 2
        self.vy = 0.0
        self.pipes = []          # [{"x": left edge, "gap_y": centre of the gap, "scored": bool}]
        self.score = 0
        self.started = False
        self.alive = True
        self.frame = 0

    @property
    def playing(self) -> bool:
        return self.alive and self.started

    def flap(self):
        if not self.alive:
            return
        self.started = True
        self.vy = self.FLAP_V

    def _spawn_pipe(self):
        low = self.EDGE_MARGIN + self.GAP / 2
        high = self.HEIGHT - self.GROUND - self.EDGE_MARGIN - self.GAP / 2
        if self.pipes:
            prev = self.pipes[-1]["gap_y"]
            low, high = max(low, prev - self.MAX_SHIFT), min(high, prev + self.MAX_SHIFT)
        self.pipes.append({"x": float(self.WIDTH), "gap_y": self.rng.uniform(low, high), "scored": False})

    def tick(self):
        if not self.alive:
            return
        self.frame += 1
        if not self.started:
            return
        self.vy = min(self.vy + self.GRAVITY, self.MAX_FALL)
        self.bird_y += self.vy
        for pipe in self.pipes:
            pipe["x"] -= self.SPEED
        if not self.pipes or self.pipes[-1]["x"] <= self.WIDTH - self.SPACING:
            self._spawn_pipe()
        self.pipes = [p for p in self.pipes if p["x"] + self.PIPE_W > 0]

        for pipe in self.pipes:
            if not pipe["scored"] and pipe["x"] + self.PIPE_W < self.BIRD_X - self.BIRD_R:
                pipe["scored"] = True
                self.score += 1

        top, bottom = self.bird_y - self.BIRD_R, self.bird_y + self.BIRD_R
        if top < 0 or bottom > self.HEIGHT - self.GROUND:
            self.alive = False
            return
        for pipe in self.pipes:
            if self.BIRD_X + self.BIRD_R > pipe["x"] and self.BIRD_X - self.BIRD_R < pipe["x"] + self.PIPE_W:
                if top < pipe["gap_y"] - self.GAP / 2 or bottom > pipe["gap_y"] + self.GAP / 2:
                    self.alive = False
                    return


class GameWindowBase(Toplevel):
    """What every minigame window shares: the live leaderboard, the player's colour, reporting the
    score to the room (when there is one) and cleaning up. A subclass builds its canvas, calls
    _build_footer(), and implements _state() -> (score, playing)."""

    GAME_KEY = ""
    GAME_TITLE = ""
    HELP_TEXT = ""
    LEADERBOARD_ROWS = 8

    def __init__(self, app, color_value: str):
        super().__init__(app)
        self.app = app
        self.color_value = color_value  # a hex color, or a gradient sentinel
        self._tick_job = None
        self._reported = None           # (score, playing) last sent to the room
        self._board_layout = None       # what the leaderboard's widgets were built for (see refresh_leaderboard)
        self._board_rows, self._best_label, self._playing_label = [], None, None
        self.title(self.GAME_TITLE)
        self.configure(bg=BG_DARK, padx=12, pady=12)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Escape>", lambda e: self._on_close())

    def _build_footer(self, wrap_px: int):
        # Fixed two-line labels: text that changes length (a score going 9 -> 10, "Game over…") must never
        # change the window's size, or macOS redraws the whole window — which looked like a screen flash.
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, bg=BG_DARK, fg=FG_TEXT, font=CHAT_FONT, height=2, wraplength=wrap_px, justify="center").pack(pady=(6, 0))
        tk.Label(self, text=self.HELP_TEXT, bg=BG_DARK, fg=FG_MUTED, font=(CHAT_FONT[0], 9), height=2, wraplength=wrap_px, justify="center").pack()
        self.leaderboard_frame = tk.Frame(self, bg=BG_DARK)
        self.leaderboard_frame.pack(fill="x", pady=(8, 0))

    def _state(self):
        raise NotImplementedError

    def set_color(self, color_value: str):
        self.color_value = color_value

    def _gradient_or_flat(self, index: int = 0) -> str:
        palette = GRADIENT_PALETTES.get(self.color_value)
        return palette[index % len(palette)] if palette else self.color_value

    def _report(self):
        """Tell the room our score / whether we're mid-game — only when it changed."""
        state = self._state()
        if state != self._reported:
            self._reported = state
            self.app.game_report(self.GAME_KEY, *state)

    def rejoin(self):
        """The room changed (we joined one, or left): say where we are now and redraw the board."""
        self._reported = None
        self._report()
        self.refresh_leaderboard()

    def refresh_leaderboard(self):
        """Brings the leaderboard up to date (called whenever anyone's score changes — for the person
        playing, on every point). Widgets are only rebuilt when the board's *shape* changes (who's listed,
        in what order, in a chat or not); a score changing just rewrites a label's text in place, so the
        window never relays out mid-game."""
        try:
            frame = self.leaderboard_frame
            in_room = self.app.in_room()
            me = self.app.game_player_name().lower()
            # Our own row is always listed (even at 0), so it doesn't pop in — and resize the window — at our first flap.
            board = self.app.game_boards[self.GAME_KEY]
            playing_now = sum(1 for e in board.values() if e["playing"])
            rows = [e for e in board.values() if e["best"] > 0 or e["playing"] or e["name"].lower() == me]
            rows.sort(key=lambda e: (-e["best"], e["name"].lower()))
            rows = rows[:self.LEADERBOARD_ROWS]
            my_best = self.app.game_best(self.GAME_KEY)
            layout = (in_room, tuple((e["name"], self.app.game_name_color(e["name"])) for e in rows))
            if layout != self._board_layout:
                self._board_layout = layout
                self._rebuild_leaderboard(frame, in_room, rows, my_best)
            for best_label, entry in zip(self._board_rows, rows):
                self._set_label(best_label, f"  best {entry['best']}")
            if self._playing_label is not None:
                self._set_label(self._playing_label, f"● {playing_now} playing" if in_room and playing_now else "")
            if self._best_label is not None:
                self._set_label(self._best_label, f"Your best on this computer: {my_best}" if my_best else "\u00a0")
        except tk.TclError:
            pass  # the window is going away

    @staticmethod
    def _set_label(label, text: str):
        if label.cget("text") != text:
            label.configure(text=text)

    def _rebuild_leaderboard(self, frame, in_room: bool, rows: list, my_best: int = 0):
        for w in frame.winfo_children(): w.destroy()
        self._board_rows, self._best_label = [], None
        title = "Leaderboard — this chat" if in_room else "Leaderboard — not in a chat"
        header = tk.Frame(frame, bg=BG_DARK)
        header.pack(fill="x")
        tk.Label(header, text=title, bg=BG_DARK, fg=FG_MUTED, font=BOLD_FONT).pack(side="left")
        self._playing_label = tk.Label(header, text="", bg=BG_DARK, fg=COLOR_PALETTE["green"], font=CHAT_FONT)  # "● 2 playing", filled in place
        self._playing_label.pack(side="right")
        if not rows:
            tk.Label(frame, text="No scores yet — be the first!" if in_room else "No scores yet — go on, give it a go!",
                     bg=BG_DARK, fg=FG_MUTED, font=CHAT_FONT).pack(anchor="w")
        for rank, entry in enumerate(rows, 1):
            row = tk.Frame(frame, bg=BG_DARK)
            row.pack(fill="x")
            tk.Label(row, text=f"{rank}.", bg=BG_DARK, fg=FG_MUTED, font=CHAT_FONT, width=3, anchor="e").pack(side="left")
            tk.Label(row, text=entry["name"], bg=BG_DARK, fg=self.app.game_name_color(entry["name"]), font=BOLD_FONT).pack(side="left", padx=(4, 0))
            best_label = tk.Label(row, text="", bg=BG_DARK, fg=FG_TEXT, font=CHAT_FONT)
            best_label.pack(side="left")
            self._board_rows.append(best_label)
        self._best_label = tk.Label(frame, text="\u00a0", bg=BG_DARK, fg=FG_MUTED, font=(CHAT_FONT[0], 9))  # always there: it fills in later
        self._best_label.pack(anchor="w", pady=(4, 0))
        note = "Resets when the chat is restarted." if in_room else "Join a chat and your scores show up for everyone in it."
        tk.Label(frame, text=note, bg=BG_DARK, fg=FG_MUTED, font=(CHAT_FONT[0], 8)).pack(anchor="w", pady=(2, 0))

    def _on_close(self):
        if self._tick_job:
            try: self.after_cancel(self._tick_job)
            except Exception: pass
            self._tick_job = None
        score, playing = self._state()
        if playing:
            self.app.game_report(self.GAME_KEY, score, False)  # no longer "playing" once the window is gone
        if self.app._game_wins.get(self.GAME_KEY) is self:
            del self.app._game_wins[self.GAME_KEY]
        self.destroy()


class SnakeWindow(GameWindowBase):
    """Snake. Everyone plays their own local game, but scores are shared live with the room: the
    leaderboard shows everyone in the chat who has played (and who's playing right now). It lives
    only as long as the room — it starts empty whenever the chat is restarted."""

    GAME_KEY, GAME_TITLE = "snake", "Snake"
    HELP_TEXT = "Arrows or WASD to move — Space to restart after a game over"
    ARROW_DIRECTIONS = {
        "Up": (0, -1), "w": (0, -1), "W": (0, -1),
        "Down": (0, 1), "s": (0, 1), "S": (0, 1),
        "Left": (-1, 0), "a": (-1, 0), "A": (-1, 0),
        "Right": (1, 0), "d": (1, 0), "D": (1, 0),
    }

    def __init__(self, app, color_value: str):
        super().__init__(app, color_value)
        self.game = SnakeGame()
        self._rainbow_offset = 0

        canvas_w, canvas_h = SNAKE_COLS * SNAKE_CELL_PX, SNAKE_ROWS * SNAKE_CELL_PX
        self.canvas = tk.Canvas(self, width=canvas_w, height=canvas_h, bg=BG_PANEL, highlightthickness=0)
        self.canvas.pack()
        self._build_footer(canvas_w)

        for keysym, vec in self.ARROW_DIRECTIONS.items():
            self.bind(f"<KeyPress-{keysym}>", lambda e, v=vec: self.game.set_direction(*v))
        self.bind("<space>", lambda e: self._restart_if_dead())

        self._report()
        self.refresh_leaderboard()
        self._set_status()
        self.focus_set()
        self._loop()

    def _state(self):
        return (self.game.score, self.game.alive)

    def _restart_if_dead(self):
        if not self.game.alive:
            self.game.reset()
            self._rainbow_offset = 0
            self._report()
            self._set_status()

    def _set_status(self):
        if self.game.alive:
            self.status_var.set(f"Score: {self.game.score}")
        else:
            self.status_var.set(f"Game over — score {self.game.score}. Press Space to try again.")

    def _loop(self):
        if self.game.alive:
            self.game.tick()
            self._report()
            self._set_status()
        self._draw()
        self._tick_job = self.after(SNAKE_TICK_MS, self._loop)

    def _segment_color(self, index: int) -> str:
        return self._gradient_or_flat(index + self._rainbow_offset)

    def _draw(self):
        self.canvas.delete("all")
        cs = SNAKE_CELL_PX

        if self.game.food:
            fx, fy = self.game.food
            self.canvas.create_oval(fx * cs + 3, fy * cs + 3, fx * cs + cs - 3, fy * cs + cs - 3, fill=BTN_RED, outline="")

        for i, (x, y) in enumerate(self.game.body):
            self.canvas.create_rectangle(x * cs + 1, y * cs + 1, x * cs + cs - 1, y * cs + cs - 1, fill=self._segment_color(i), outline="")

        palette = GRADIENT_PALETTES.get(self.color_value)
        if palette and self.game.alive:
            self._rainbow_offset = (self._rainbow_offset + 1) % len(palette)

        if not self.game.alive:
            self.canvas.create_rectangle(0, 0, self.canvas.winfo_reqwidth(), self.canvas.winfo_reqheight(), fill=BG_PANEL, stipple="gray50", outline="")


class FlappyWindow(GameWindowBase):
    """Flappy Bird: Space, ↑, W or a click flaps. The bird wears your name colour, like the snake."""

    GAME_KEY, GAME_TITLE = "flappy", "Flappy Bird"
    HELP_TEXT = "Space, ↑, W or click to flap — Space to restart after a game over"
    SKY, PIPE, PIPE_EDGE, GROUND_TOP, GROUND_FILL = "#6FC3E8", "#3CB043", "#2A7A31", "#73BF2E", "#DED895"
    RESTART_DELAY_TICKS = 18   # after dying, ignore flaps for a moment so a frantic last tap doesn't restart at once

    def __init__(self, app, color_value: str):
        super().__init__(app, color_value)
        self.game = FlappyGame()
        self._dead_ticks = 0
        self._status = ""
        self.canvas = tk.Canvas(self, width=FlappyGame.WIDTH, height=FlappyGame.HEIGHT, bg=self.SKY, highlightthickness=0)
        self.canvas.pack()
        self._build_footer(FlappyGame.WIDTH)

        for keysym in ("space", "Up", "w", "W"):
            self.bind(f"<KeyPress-{keysym}>", self._flap)
        self.canvas.bind("<Button-1>", self._flap)

        self._report()
        self.refresh_leaderboard()
        self._set_status()
        self.focus_set()
        self._loop()

    def _state(self):
        return (self.game.score, self.game.playing)

    def _flap(self, event=None):
        game = self.game
        if game.alive:
            game.flap()
            self._report()
        elif self._dead_ticks >= self.RESTART_DELAY_TICKS:
            game.reset()
            self._dead_ticks = 0
            self._report()
        self._set_status()
        return "break"

    def _set_status(self):
        game = self.game
        if not game.alive:
            text = f"Game over — score {game.score}. Press Space to try again."
        elif not game.started:
            text = "Press Space or click to start"
        else:
            text = f"Score: {game.score}"
        if text != self._status:
            self._status = text
            self.status_var.set(text)

    def _loop(self):
        if self.game.alive:
            self.game.tick()
            self._report()
        else:
            self._dead_ticks += 1
        self._set_status()
        self._draw()
        self._tick_job = self.after(FLAPPY_TICK_MS, self._loop)

    def _draw(self):
        c, g = self.canvas, self.game
        c.delete("all")
        w, h, ground_top = FlappyGame.WIDTH, FlappyGame.HEIGHT, FlappyGame.HEIGHT - FlappyGame.GROUND

        for pipe in g.pipes:
            x0, x1 = pipe["x"], pipe["x"] + g.PIPE_W
            gap_top, gap_bottom = pipe["gap_y"] - g.GAP / 2, pipe["gap_y"] + g.GAP / 2
            c.create_rectangle(x0, 0, x1, gap_top, fill=self.PIPE, outline=self.PIPE_EDGE, width=2)
            c.create_rectangle(x0 - 3, gap_top - 16, x1 + 3, gap_top, fill=self.PIPE, outline=self.PIPE_EDGE, width=2)
            c.create_rectangle(x0, gap_bottom, x1, ground_top, fill=self.PIPE, outline=self.PIPE_EDGE, width=2)
            c.create_rectangle(x0 - 3, gap_bottom, x1 + 3, gap_bottom + 16, fill=self.PIPE, outline=self.PIPE_EDGE, width=2)

        c.create_rectangle(0, ground_top, w, h, fill=self.GROUND_FILL, outline="")
        c.create_rectangle(0, ground_top, w, ground_top + 8, fill=self.GROUND_TOP, outline="")

        bob = 0 if g.started else math.sin(g.frame * 0.12) * 5  # idles up and down until the first flap
        by, bx, r = g.bird_y + bob, g.BIRD_X, g.BIRD_R
        body = self._gradient_or_flat(g.frame // 4)
        c.create_oval(bx - r - 2, by - r + 1, bx + r + 2, by + r - 1, fill=body, outline="#222222")
        wing_up = (g.frame // 6) % 2 == 0 and g.alive
        wing_y = by - 2 if wing_up else by + 2
        c.create_oval(bx - 9, wing_y - 3, bx + 1, wing_y + 4, fill="white", outline="#222222")
        c.create_oval(bx + 3, by - 7, bx + 9, by - 1, fill="white", outline="#222222")
        c.create_oval(bx + 6, by - 5, bx + 8, by - 3, fill="black", outline="")
        c.create_polygon(bx + r, by - 1, bx + r + 9, by + 2, bx + r, by + 5, fill="#FF9A1F", outline="#222222")

        score_text = str(g.score)
        c.create_text(w / 2 + 2, 52, text=score_text, font=(CHAT_FONT[0], 32, "bold"), fill="#222222")
        c.create_text(w / 2, 50, text=score_text, font=(CHAT_FONT[0], 32, "bold"), fill="white")
        if not g.alive:
            c.create_rectangle(0, 0, w, h, fill="#000000", stipple="gray25", outline="")
            c.create_text(w / 2, h / 2 - 10, text="Game over", font=(CHAT_FONT[0], 24, "bold"), fill="white")
            c.create_text(w / 2, h / 2 + 24, text=f"Score {g.score}", font=(CHAT_FONT[0], 14), fill="white")
        elif not g.started:
            c.create_text(w / 2, h / 2 + 70, text="Press Space to flap", font=(CHAT_FONT[0], 13, "bold"), fill="white")


class GamePicker(Toplevel):
    """Ctrl+Shift+S opens this: pick which minigame to play. Works in a chat or on the home screen."""

    CHOICES = (("snake", "🐍  Snake", "1"), ("flappy", "🐦  Flappy Bird", "2"))

    def __init__(self, app):
        super().__init__(app)
        self.app = app
        self.title("Games")
        self.configure(bg=BG_PANEL, padx=24, pady=20)
        self.resizable(False, False)
        self.transient(app)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind("<Escape>", lambda e: self._close())
        tk.Label(self, text="🎮  Pick a game", bg=BG_PANEL, fg=FG_TEXT, font=TITLE_FONT).pack(anchor="w")
        where = "Scores are shared with everyone in this chat." if app.in_room() else "Not in a chat — scores stay on this computer."
        tk.Label(self, text=where, bg=BG_PANEL, fg=FG_MUTED, font=fnt(9)).pack(anchor="w", pady=(4, 12))
        for key, label, shortcut in self.CHOICES:
            row = tk.Frame(self, bg=BG_PANEL)
            row.pack(fill="x", pady=4)
            make_button(row, label, lambda k=key: self._pick(k), bg=BTN_GREEN, hover_bg=BTN_GREEN_HOVER, padx=16, pady=8).pack(side="left")
            best = app.game_best(key)
            tk.Label(row, text=f"  your best: {best}" if best else "", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(side="left")
            self.bind(shortcut, lambda e, k=key: self._pick(k))
        tk.Label(self, text="Press 1 or 2, or click. Esc closes this.", bg=BG_PANEL, fg=FG_MUTED, font=fnt(8)).pack(anchor="w", pady=(10, 0))
        self.focus_set()

    def _pick(self, key):
        self._close()
        self.app.open_game(key)

    def _close(self):
        if self.app._game_picker is self:
            self.app._game_picker = None
        self.destroy()

GAME_WINDOWS = {"snake": SnakeWindow, "flappy": FlappyWindow}
GAME_KEYS = tuple(GAME_WINDOWS)

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

ACCENT = "#5B8CFF"           # the UI accent (buttons, selections, banners) — separate from the blue a person can pick as a name colour
ACCENT_HOVER = BTN_BLUE_HOVER

# ---- Appearance: themes and fonts (per computer — saved in the settings file, never sent to anyone) ----
THEME_ROLES = ("bg", "panel", "input", "text", "muted", "neutral", "neutral_hover", "accent", "accent_hover")
_THEME_GLOBALS = {"bg": "BG_DARK", "panel": "BG_PANEL", "input": "BG_INPUT", "text": "FG_TEXT", "muted": "FG_MUTED",
                  "neutral": "BTN_NEUTRAL", "neutral_hover": "BTN_NEUTRAL_HOVER", "accent": "ACCENT", "accent_hover": "ACCENT_HOVER"}

def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

def _hex(rgb):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c * 255))) for c in rgb)

def _luminance(h):
    lin = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(c) for c in _rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def _contrast(a, b):
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)

def _shade(h, dl):
    hue, light, sat = colorsys.rgb_to_hls(*_rgb(h))
    return _hex(colorsys.hls_to_rgb(hue, max(0.0, min(1.0, light + dl)), sat))

def _mix(a, b, t):
    return _hex(tuple(x + (y - x) * t for x, y in zip(_rgb(a), _rgb(b))))

def _valid_hex(v) -> bool:
    return isinstance(v, str) and re.fullmatch(r"#[0-9A-Fa-f]{6}", v) is not None

def make_theme(bg: str, accent: str) -> dict:
    """A whole palette from just a background and an accent colour. The background is kept dark (the text, status
    colours and name colours are all tuned for a dark window) and the accent dark enough for white button text."""
    hue, light, sat = colorsys.rgb_to_hls(*_rgb(bg))
    bg = _hex(colorsys.hls_to_rgb(hue, max(0.09, min(0.30, light)), min(sat, 0.45)))
    text = "#DBDEE1"
    acc = accent.upper()
    while _contrast(acc, "#FFFFFF") < 3.6 and _luminance(acc) > 0.02:
        acc = _shade(acc, -0.03)
    return {"bg": bg, "panel": _shade(bg, -0.035), "input": _shade(bg, 0.035), "text": text,
            "muted": _mix(text, bg, 0.42), "neutral": _shade(bg, 0.10), "neutral_hover": _shade(bg, 0.19),
            "accent": acc, "accent_hover": _shade(acc, -0.09)}

THEME_PRESETS = {   # key -> (label, palette)
    "midnight": ("Midnight", {"bg": "#313338", "panel": "#2B2D31", "input": "#383A40", "text": "#DBDEE1", "muted": "#949BA4",
                              "neutral": "#4E5058", "neutral_hover": "#6D6F78", "accent": "#5B8CFF", "accent_hover": "#4752C4"}),
    "graphite": ("Graphite", make_theme("#2C2C2E", "#6C8EEF")),
    "ocean":    ("Ocean",    make_theme("#1E2D3D", "#2E9FD8")),
    "forest":   ("Forest",   make_theme("#24302A", "#3FA86B")),
    "plum":     ("Plum",     make_theme("#2D2535", "#B565E6")),
    "mocha":    ("Mocha",    make_theme("#302822", "#D68A4A")),
    "rose":     ("Rose",     make_theme("#33262B", "#E0607E")),
}
FONT_SIZE_RANGE = (DEFAULT_FONT_SIZE - 2, DEFAULT_FONT_SIZE + 8)
DEFAULT_APPEARANCE = {"theme": "midnight", "custom_bg": "#313338", "custom_accent": "#5B8CFF",
                      "font_family": "", "font_size": 0, "home_image": False}   # font "" / size 0 = the platform default
HOME_IMAGE_FILE = app_path("chat_gui_background.jpg")
CURRENT_THEME = dict(THEME_PRESETS["midnight"][1])

def sanitize_appearance(raw) -> dict:
    """Whatever the settings file holds -> a complete, valid appearance (a hand-edited or damaged file can't break startup)."""
    cfg = dict(DEFAULT_APPEARANCE)
    if not isinstance(raw, dict):
        return cfg
    if raw.get("theme") in THEME_PRESETS or raw.get("theme") == "custom":
        cfg["theme"] = raw["theme"]
    for key in ("custom_bg", "custom_accent"):
        if _valid_hex(raw.get(key)):
            cfg[key] = raw[key].upper()
    if isinstance(raw.get("font_family"), str):
        cfg["font_family"] = raw["font_family"][:80]
    size = raw.get("font_size")
    if isinstance(size, int) and not isinstance(size, bool) and FONT_SIZE_RANGE[0] <= size <= FONT_SIZE_RANGE[1] and size != DEFAULT_FONT_SIZE:
        cfg["font_size"] = size
    cfg["home_image"] = bool(raw.get("home_image")) and os.path.exists(HOME_IMAGE_FILE)
    return cfg

def theme_for(cfg: dict) -> dict:
    if cfg["theme"] == "custom":
        return make_theme(cfg["custom_bg"], cfg["custom_accent"])
    return dict(THEME_PRESETS[cfg["theme"]][1])

def apply_theme_globals(theme: dict):
    """Points the module's colour constants at `theme`. Widgets built afterwards pick it up; ones already on screen
    are recoloured by ChatApp._retheme_tree."""
    global CURRENT_THEME
    CURRENT_THEME = dict(theme)
    g = globals()
    for role, name in _THEME_GLOBALS.items():
        g[name] = theme[role]

def apply_font_globals(family: str, size: int):
    global CHAT_FONT, BOLD_FONT, TITLE_FONT, FONT_DELTA
    family, size = family or DEFAULT_FONT_FAMILY, size or DEFAULT_FONT_SIZE
    FONT_DELTA = size - DEFAULT_FONT_SIZE
    CHAT_FONT, BOLD_FONT, TITLE_FONT = (family, size), (family, size, "bold"), (family, size + 1, "bold")
    # EMOJI_FONT is left alone: emoji come from the system's emoji font whatever text font is chosen.

def system_font_families(root) -> list:
    """Only fonts this computer actually has."""
    try: names = set(tkfont.families(root))
    except tk.TclError: names = set()
    names.add(DEFAULT_FONT_FAMILY)
    return sorted((n for n in names if n and not n.startswith("@")), key=str.lower)

def derive_key(passphrase: str) -> bytes:
    digest = hashlib.sha256(passphrase.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)

# ---- Invite Codes: the room's whole address (IPv4 + port, 48 bits) as 10 characters + 1 check character ----
# A Room Code is only the last two numbers of the host's IP, so the joiner has to go looking for the rest — which
# fails on networks that block broadcasts or span several subnets. An Invite Code holds the entire address, so
# joining is just one direct connection. (Crockford's alphabet: no I, L, O or U, so a misread still decodes.)
_INVITE_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_INVITE_LOOKALIKES = str.maketrans({"O": "0", "I": "1", "L": "1", "U": "V"})

def _invite_check(chars: str) -> str:
    return _INVITE_ALPHABET[sum((2 * i + 1) * _INVITE_ALPHABET.index(c) for i, c in enumerate(chars)) % 32]  # odd weights: any single wrong character changes the sum

def make_invite_code(ip: str, port: int) -> str:
    a, b, c, d = (int(part) for part in ip.split("."))
    value = (((a << 24) | (b << 16) | (c << 8) | d) << 16) | (int(port) & 0xFFFF)
    chars = ""
    for _ in range(10):
        chars = _INVITE_ALPHABET[value & 31] + chars
        value >>= 5
    chars += _invite_check(chars)
    return f"{chars[:4]}-{chars[4:8]}-{chars[8:]}"

def parse_invite_code(cleaned: str):
    """-> (ip, port). `cleaned` is already upper-case with the dashes and spaces gone. Raises ValueError (with a
    message fit to show the user) if it isn't a valid Invite Code."""
    cleaned = cleaned.translate(_INVITE_LOOKALIKES)
    if len(cleaned) != 11 or any(ch not in _INVITE_ALPHABET for ch in cleaned):
        raise ValueError("That doesn't look like a Room Code (6 digits) or an Invite Code (11 letters and numbers, like 7K2M-9QXA-R5B).")
    if _invite_check(cleaned[:10]) != cleaned[10]:
        raise ValueError("That Invite Code has a typo in it — check it against the host's screen (or have them send it again).")
    value = 0
    for ch in cleaned[:10]:
        value = (value << 5) | _INVITE_ALPHABET.index(ch)
    port, ip_int = value & 0xFFFF, value >> 16
    if ip_int >> 32 or not 1 <= port <= 65535:
        raise ValueError("That Invite Code isn't valid.")
    return ".".join(str((ip_int >> shift) & 255) for shift in (24, 16, 8, 0)), port

def normalize_room_input(text: str) -> str:
    """What's in the Room Code box, with the noise taken out: spaces, dashes, dots, line breaks and invisible
    characters are dropped, full-width / other-script digits become 0-9, letters are upper-cased."""
    out = []
    for ch in unicodedata.normalize("NFKC", text):
        if ch.isdecimal(): out.append(str(unicodedata.decimal(ch)))
        elif ch.isalpha(): out.append(ch.upper())
    return "".join(out)

def interpret_room_input(text: str):
    """-> ("room", "123456") | ("invite", (ip, port)) | ("error", message-for-the-user)."""
    cleaned = normalize_room_input(text)
    if not cleaned:
        return "error", "Enter the Room Code (or Invite Code) from the host." if ENABLE_INVITE_CODES else "Enter the Room Code from the host."
    if ENABLE_INVITE_CODES and len(cleaned) == 11:
        try: return "invite", parse_invite_code(cleaned)
        except ValueError as e: return "error", str(e)
    if cleaned.isdigit():
        if len(cleaned) != 6:
            return "error", f"A Room Code is 6 digits — you've entered {len(cleaned)}. (Check it against the host's screen.)"
        if int(cleaned[:3]) > 255 or int(cleaned[3:]) > 255:
            return "error", f"{cleaned[:3]} {cleaned[3:]} can't be a Room Code: each half has to be between 000 and 255. Check it against the host's screen."
        return "room", cleaned
    if not ENABLE_INVITE_CODES:
        return "error", "A Room Code is 6 digits — numbers only. (Check it against the host's screen.)"
    try: return "invite", parse_invite_code(cleaned)
    except ValueError as e: return "error", str(e)

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

MAX_FRAME_BYTES = 8 * 1024 * 1024  # sanity cap on one encrypted frame — real frames are far smaller (a file chunk is ~0.9MB)

def encode_frame(fernet: Fernet, plaintext: str) -> bytes:
    token = fernet.encrypt(plaintext.encode("utf-8", errors="surrogatepass"))
    return len(token).to_bytes(MSG_LEN_BYTES, "big") + token

def send_encrypted(sock: socket.socket, fernet: Fernet, plaintext: str):
    """Blocking send — only for the handshake, before a connection has an Outbox."""
    sock.sendall(encode_frame(fernet, plaintext))

def recv_exact(sock: socket.socket, n: int) -> bytes:
    # recv_into a preallocated buffer: appending to a bytes object chunk by chunk is
    # quadratic, which made receiving large files stall the receive thread for seconds.
    buf = bytearray(n)
    view = memoryview(buf)
    got = 0
    while got < n:
        received = sock.recv_into(view[got:], min(n - got, 1 << 20))
        if not received:
            raise ConnectionError("peer closed connection")
        got += received
    return bytes(buf)

def recv_message(sock: socket.socket, fernet: Fernet) -> str:
    length = int.from_bytes(recv_exact(sock, MSG_LEN_BYTES), "big")
    if length > MAX_FRAME_BYTES:
        raise ConnectionError("corrupt or oversized frame")  # the stream is out of step — don't wait for 4GB that will never come
    token = recv_exact(sock, length)
    return fernet.decrypt(token).decode("utf-8", errors="surrogatepass")

def enable_keepalive(sock: socket.socket, idle: int = 30, interval: int = 10, count: int = 3):
    """Have the OS probe idle connections so a peer that vanished (Wi-Fi drop, laptop
    sleep) is noticed in about a minute instead of lingering as a ghost session."""
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        if hasattr(socket, "SIO_KEEPALIVE_VALS"):  # Windows
            sock.ioctl(socket.SIO_KEEPALIVE_VALS, (1, idle * 1000, interval * 1000))
            return
        if hasattr(socket, "TCP_KEEPIDLE"): sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, idle)
        elif hasattr(socket, "TCP_KEEPALIVE"): sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPALIVE, idle)  # macOS
        if hasattr(socket, "TCP_KEEPINTVL"): sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval)
        if hasattr(socket, "TCP_KEEPCNT"): sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, count)
    except (OSError, ValueError, AttributeError):
        pass  # keepalive is a nicety — never fail a connection over it


class Outbox:
    """Ordered, non-blocking sender for one socket. Callers just enqueue a frame; a
    dedicated thread does the (possibly slow) sendall. That means:
      * a stalled peer can never block anyone else's messages (or the UI);
      * frames from different threads can never interleave on the wire (which
        would permanently desync the peer's stream — it'd stop seeing messages);
      * small control frames (chat) overtake queued bulk frames (file chunks) —
        while bulk frames always stay in order among themselves.
    `on_sent(ok)` is called once the frame has been written (or dropped)."""

    HARD, CONTROL, AFTER_CONTROL, BULK = -1, 0, 1, 2
    BULK_THRESHOLD = 64 * 1024
    MAX_QUEUED_BYTES = 256 * 1024 * 1024  # backstop only: transfers are paced by wait_below(), so normally a few MB

    def __init__(self, sock: socket.socket, on_failed=None):
        self.sock = sock
        self.on_failed = on_failed
        self._queue = queue.PriorityQueue()
        self._seq = itertools.count()
        self._lock = threading.Condition()
        self._queued = 0
        self._closed = False
        self._dead = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def put(self, frame: bytes, on_sent=None, bulk: bool = False) -> bool:
        with self._lock:
            if self._closed:
                return False
            overflow = self._queued + len(frame) > self.MAX_QUEUED_BYTES
            if not overflow:
                self._queued += len(frame)
        if overflow:
            self._fail()
            return False
        priority = self.BULK if (bulk or len(frame) > self.BULK_THRESHOLD) else self.CONTROL
        self._queue.put((priority, next(self._seq), frame, on_sent))
        return True

    @property
    def closed(self) -> bool:
        return self._closed

    def wait_below(self, limit: int, timeout: float) -> bool:
        """Back-pressure for senders: block until at most `limit` bytes are queued.
        False if it's still above after `timeout` seconds, or the connection is gone."""
        deadline = time.monotonic() + timeout
        with self._lock:
            while self._queued > limit and not self._closed:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                self._lock.wait(remaining)
            return not self._closed

    def close(self, after_control: bool = False):
        """Stop accepting frames. after_control=True still sends queued small frames
        first (e.g. a kick notice); otherwise everything pending is dropped."""
        with self._lock:
            self._closed = True
            self._lock.notify_all()
        self._queue.put((self.AFTER_CONTROL if after_control else self.HARD, next(self._seq), None, None))

    def join(self, timeout: float):
        self._thread.join(timeout)

    def _run(self):
        while True:
            _, _, frame, on_sent = self._queue.get()
            if frame is None:  # close sentinel
                self._shutdown_socket()
                self._drain()
                return
            try:
                self.sock.sendall(frame)
            except OSError:
                self._fail()
                return
            with self._lock:
                self._queued -= len(frame)
                self._lock.notify_all()
            self._notify(on_sent, True)

    def _fail(self):
        with self._lock:
            if self._dead:
                return
            self._dead = self._closed = True
            self._lock.notify_all()
        self._shutdown_socket()
        self._drain()
        if self.on_failed:
            try: self.on_failed()
            except Exception: traceback.print_exc()
        self._queue.put((self.HARD, next(self._seq), None, None))  # wake the writer if it's idle

    def _shutdown_socket(self):
        try: self.sock.shutdown(socket.SHUT_RDWR)
        except OSError: pass

    def _drain(self):
        while True:
            try: _, _, frame, on_sent = self._queue.get_nowait()
            except queue.Empty: return
            if frame is not None:
                self._notify(on_sent, False)

    @staticmethod
    def _notify(callback, ok: bool):
        if callback is not None:
            try: callback(ok)
            except Exception: traceback.print_exc()


def extract_ping_targets(text: str, known_names):
    """All distinct @mentions in `text` -> (names that exist, mentions that don't)."""
    lower_names = {n.lower(): n for n in known_names}
    found, unknown, seen = [], [], set()
    for mention in re.findall(r"@(\w+)", text):
        key = mention.lower()
        if key in seen:
            continue
        seen.add(key)
        if key in lower_names: found.append(lower_names[key])
        else: unknown.append(mention)
    return found, unknown

BAN_APPEAL_QUESTIONS = (
    ("text", "Why do you think you were banned?"),
    ("text", "What happened, from your side of the story?"),
    ("choice", "Which of these best describes the situation?",
     ("I made an honest mistake", "I got carried away", "It wasn't me — my cat walked on the keyboard",
      "Someone else started it", "It was all a big misunderstanding")),
    ("scale", "How sorry are you? (1 = barely, 10 = I'll bring cookies)"),
    ("text", "What will you do differently next time?"),
    ("text", "Anything else the admins should know? (Jokes optional, but appreciated.)"),
)
WARN_APPEAL_QUESTIONS = (
    ("text", "Why do you think this warning was unfair — or was it fair?"),
    ("text", "What happened, from your side of the story?"),
    ("choice", "Which of these best describes the situation?",
     ("I made an honest mistake", "I got carried away", "It wasn't me — my cat walked on the keyboard",
      "Someone else started it", "It was all a big misunderstanding")),
    ("text", "What will you do differently next time?"),
    ("text", "Anything else the admins should know?"),
)

def parse_appeal(payload: str):
    """Reads an appeal off the wire (JSON), keeping only sane, size-limited text. None if unusable."""
    try:
        data = json.loads(payload)
        answers = [[str(q)[:200], str(a)[:600]] for q, a in data["answers"][:8]]
    except (ValueError, TypeError, KeyError):
        return None
    return {"kind": str(data.get("kind", "")), "number": data.get("number"), "answers": answers}

def format_appeal(heading: str, who: str, details: str, answers: list) -> str:
    lines = [f"📨 [{heading}] {who} {details}"]
    lines += [f"     • {q}  —  {a or '(no answer)'}" for q, a in answers]
    return "\n".join(lines)

def send_ban_appeal(host_ip: str, port: int, fernet, payload: dict) -> str:
    """A banned person can't join, so the appeal goes over a fresh connection that opens with the
    appeal instead of a hello. Returns the host's reply; raises ConnectionError if it's unreachable."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(8)
    try:
        sock.connect((host_ip, port))
        send_encrypted(sock, fernet, APPEAL_PREFIX + json.dumps(dict(payload, fp=get_machine_fingerprint())))
        reply = recv_message(sock, fernet)
    except (OSError, ConnectionError, InvalidToken):
        raise ConnectionError("Couldn't reach the host right now — they may be offline. Try again once they're back.")
    finally:
        sock.close()
    return reply[len(NOTICE_PREFIX):] if reply.startswith(NOTICE_PREFIX) else reply

def check_ban_status(host_ip: str, port: int, fernet) -> dict:
    """Asks the host whether our address is still banned (a banned person can't join, so this
    is a fresh connection that opens with the question). Returns the host's answer as a dict;
    raises ConnectionError if the host can't be reached or is too old to answer."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(6)
    try:
        sock.connect((host_ip, port))
        send_encrypted(sock, fernet, BANCHECK_PREFIX + "?|" + get_machine_fingerprint())   # an older host ignores everything after BANCHECK
        reply = recv_message(sock, fernet)
    except (OSError, ConnectionError, InvalidToken):
        raise ConnectionError("host unreachable")
    finally:
        sock.close()
    if reply.startswith(BANSTATUS_PREFIX):
        try: return json.loads(reply[len(BANSTATUS_PREFIX):])
        except ValueError: pass
    if reply.startswith(BAN_NOTICE_PREFIX):  # an older host: all it can say is "still banned"
        return {"state": "banned"}
    raise ConnectionError("unreadable reply")

def nickname_error(name: str):
    """Why `name` can't be a nickname, or None if it's fine. (The wire format uses '|' as a
    separator, so it can't appear in a name.)"""
    if not name: return "A nickname can't be empty."
    if len(name) > 30: return "A nickname can be at most 30 characters."
    if any(ch.isspace() for ch in name): return "A nickname can't contain spaces."
    if "|" in name or any(ord(ch) < 32 for ch in name): return "A nickname can't contain that character."
    return None

def _name_list(names) -> str:
    names = list(names)
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]

def route_pings(hub, sender: str, text: str, reply, on_host_ping):
    """Pings everyone @mentioned in `text` (not just the first), then tells the sender
    about anyone who couldn't be pinged — all the DND users in one message."""
    targets, unknown = extract_ping_targets(text, hub.names() + [hub.host_name])
    dnd = []
    for name in targets:
        if name.lower() == sender.lower():
            continue
        if hub.is_dnd(name):
            dnd.append(name)
        elif hub.is_host(name):
            on_host_ping(sender)
        elif (target_sock := hub.find_socket_by_name(name)) is not None:
            hub.send_private(target_sock, PING_PREFIX + sender)
    if dnd:
        plural = len(dnd) > 1
        reply(f"{_name_list(dnd)} {'are' if plural else 'is'} on Do Not Disturb — they won't be notified.")
    if unknown:
        reply("No one named " + _name_list([f"'{u}'" for u in unknown]) + " is here to ping.")

def route_reply_ping(hub, sender: str, payload: dict, reply, on_host_ping):
    """Replying to someone pings them, too — unless they're on Do Not Disturb (then the sender is
    told, like with an @mention), or the reply already @mentioned them (route_pings handled that)."""
    author = payload.get("author", "")
    if not author or author.lower() == sender.lower():
        return
    with hub.lock:
        mine = hub.messages.get(payload.get("msg_id"))
    targets, _ = extract_ping_targets(mine["text"] if mine else "", hub.names() + [hub.host_name])
    if any(t.lower() == author.lower() for t in targets):
        return
    if hub.is_dnd(author):
        reply(f"{author} is on Do Not Disturb — they won't be notified.")
    elif hub.is_host(author):
        on_host_ping(sender)
    elif (target_sock := hub.find_socket_by_name(author)) is not None:
        hub.send_private(target_sock, PING_PREFIX + sender)

def format_time(ts: float) -> str:
    """A moment in local time. Today it's just the clock; any other day includes the date
    (and the year if it isn't this year) — a bare clock time made a one-year mute look like
    it ended the moment it began."""
    if ts == float('inf'):
        return "permanently"
    when, now = time.localtime(ts), time.localtime()
    if (when.tm_year, when.tm_yday) == (now.tm_year, now.tm_yday):
        return time.strftime("%H:%M:%S", when)
    fmt = "%a %d %b %Y, %H:%M" if when.tm_year != now.tm_year else "%a %d %b, %H:%M"
    return time.strftime(fmt, when)

def format_duration(seconds: float) -> str:
    seconds = max(0, seconds)
    if seconds < 30: return "under a minute"
    minutes = max(1, int(round(seconds / 60)))  # nearest minute, so a 60-minute ban doesn't read "59 min" a second later
    if minutes < 60: return f"{minutes} min"
    hours, mins = divmod(minutes, 60)
    if hours < 24: return f"{hours} h {mins} min" if mins else f"{hours} h"
    days, hrs = divmod(hours, 24)
    if days < 7: return f"{days} day{'s' if days != 1 else ''}" + (f" {hrs} h" if hrs else "")
    if days < 60: return f"{days} days"
    if days < 365: return f"about {round(days / 30.44)} months"
    years = days / 365.25
    return "1 year" if abs(years - 1) < 0.02 else f"{years:.1f} years"

def format_until(ts: float) -> str:
    """'Fri 23 Oct 2027, 14:05 (1 year)' — when something ends, and how long that is from now."""
    if ts == float('inf'):
        return "permanently"
    return f"{format_time(ts)} ({format_duration(ts - time.time())})"

# ---- Times that have to read correctly on EVERY computer ----
# The host used to write "until 23:22" into messages in ITS time zone, so a guest in another zone (or whose
# clock disagreed) saw the wrong hour. Now the host sends a token holding a duration — "{{until:3600}}" is
# "an hour from now", "{{ago:60}}" is "a minute ago" — and each app turns it into its OWN local time as the
# message is shown. A duration (not a clock time) also can't be thrown off by the two computers' clocks.
_TIME_TOKEN = re.compile(r"\{\{(until|ago):(inf|\d+)\}\}")

def until_token(ts: float) -> str:
    if ts == float('inf'): return "{{until:inf}}"
    return "{{until:%d}}" % max(0, int(ts - time.time()))

def ago_token(ts: float) -> str:
    return "{{ago:%d}}" % max(0, int(time.time() - ts))

def localize_times(text: str) -> str:
    """Turns until/ago tokens in a message into this computer's local time."""
    if "{{" not in text: return text
    def repl(m):
        kind, value = m.groups()
        if kind == "until":
            return "permanently" if value == "inf" else format_until(time.time() + int(value))
        return format_time(time.time() - int(value))
    return _TIME_TOKEN.sub(repl, text)

def make_ban_notice(until_ts: float, reason: str, host_name: str) -> str:
    """What a banned person is told: 'until|reason', then the host's nickname after a \\x1f separator."""
    reason = reason.replace("\x1f", " ")
    return f"{until_token(until_ts)}|{reason}\x1f{host_name.replace(chr(0x1f), ' ')}"

def parse_ban_notice(rest: str):
    """-> (until text in OUR local time, reason, the host's nickname — '' from an older host)."""
    body, _, host = rest.partition("\x1f")
    until_str, _, reason = body.partition("|")
    return localize_times(until_str), reason, host.strip()

def notify_toast(title: str, message: str, root=None, timeout: int = 6):
    """A desktop notification (falls back to a beep where notifications aren't available)."""
    if _plyer_notification is not None:
        try:
            _plyer_notification.notify(title=title[:64], message=message[:240], timeout=timeout)
            return
        except Exception:
            pass
    if root is not None:
        try: root.bell()
        except Exception: pass

def notify_ping(pinger_name: str, root=None):
    notify_toast("Ping Received", f"{pinger_name} mentioned you!", root, timeout=5)

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

def get_local_ips() -> list:
    """Every usable (non-loopback, non-link-local) IPv4 address this machine has,
    with the default-route address first. A machine on Wi-Fi + Ethernet, or with a VPN
    or virtual adapters, has several, and the Room Code only matches one of them."""
    ips = []
    def add(ip):
        if ip and not ip.startswith(("127.", "169.254.", "0.")) and ip not in ips:
            ips.append(ip)
    add(get_local_ip())
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
            add(info[4][0])
    except OSError:
        pass
    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            add(ip)
    except OSError:
        pass
    return ips

def _guess_broadcast_addresses() -> set:
    addrs = {"255.255.255.255"}
    for local_ip in get_local_ips():
        parts = local_ip.split(".")
        if len(parts) == 4:
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

def discover_host(room_code: str, target_ip=None, timeout: float = 4.0) -> tuple[str, int]:
    """target_ip may be one address, or a collection of addresses to try at once."""
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_sock.settimeout(0.5)

    msg = f"DISCOVER:{room_code}".encode('utf-8')
    if target_ip:
        targets = {target_ip} if isinstance(target_ip, str) else set(target_ip)
    else:
        targets = _guess_broadcast_addresses()
        for ip in get_local_ips()[:3]:
            targets |= set(_local_subnet_hosts(ip))
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

# ---- Recent chats: remembers hosts a Join succeeded against, so returning
# to a chat is a click instead of retyping the Room Code / Host IP. Entries
# older than a day are dropped on load, since a host's IP (and so its Room
# Code) typically changes by the next day anyway. ----
RECENT_HOSTS_FILE = app_path("chat_gui_recent_hosts.json")
RECENT_HOSTS_MAX_AGE = 24 * 60 * 60
RECENT_HOSTS_MAX_ENTRIES = 6

def load_recent_hosts() -> list:
    entries = load_json(RECENT_HOSTS_FILE, list)
    cutoff = time.time() - RECENT_HOSTS_MAX_AGE
    fresh = [e for e in entries if isinstance(e, dict) and e.get("last_connected", 0) >= cutoff]
    fresh.sort(key=lambda e: e.get("last_connected", 0), reverse=True)
    seen, unique = set(), []
    for e in fresh:  # one entry per room — the newest sighting (the port is different every session)
        room = (e.get("room_code"), e.get("host_ip"))
        if room not in seen:
            seen.add(room)
            unique.append(e)
    if len(unique) != len(entries):
        save_recent_hosts(unique)
    return unique

def save_recent_hosts(entries: list):
    save_json(RECENT_HOSTS_FILE, entries[:RECENT_HOSTS_MAX_ENTRIES])

def remember_recent_host(room_code: str, host_ip: str, port: int):
    # A room is its code plus the host's address (the same code can exist on two networks). Joining a room you already
    # have just refreshes that entry — the port differs every session — while a different room is added alongside it.
    entries = [e for e in load_recent_hosts() if not (e.get("room_code") == room_code and e.get("host_ip") == host_ip)]
    entries.insert(0, {"room_code": room_code, "host_ip": host_ip, "port": port, "last_connected": time.time()})
    save_recent_hosts(entries[:RECENT_HOSTS_MAX_ENTRIES])

# ---- Bug reports and feature suggestions ----
REPORTS_FILE = app_path("chat_gui_reports.json")
REPORTS_KEYBIND = "<Control-Shift-KeyPress-B>"   # opens the report inbox (asks for the password)
# The inbox "password" is deliberately light — this is a friends' app and the file is readable anyway. It's stored as a
# SHA-256 of salt + password; to change it: python3 -c "import hashlib; print(hashlib.sha256(b'chat_gui-reports|YOURPASSWORD').hexdigest())"
REPORTS_PASSWORD_SHA256 = "b7f6b0c151a099ce850f1da345e9e97db90b5f6cc960f5a895e17f337025c07a"
# Optional: where reports go so you receive everyone's. Reports are always saved on the computer they were written on; with this
# set they're also sent to YOUR report server — a free Cloudflare Worker (the code is in report_worker.js, with setup steps) — and
# the inbox (Ctrl+Shift+B) then shows reports from everyone's computers. Paste the Worker's address between the quotes,
# e.g. "https://chat-gui-reports.yourname.workers.dev". Leave it empty to keep reports on each computer only. The same
# server also carries announcements (Ctrl+Shift+A).
REPORT_WORKER_URL = "https://chat-gui-reports.richardfeng023.workers.dev"
REPORT_COOLDOWN_SECONDS = 20

def _os_label() -> str:
    system = platform.system()
    if system == "Darwin": return f"macOS {platform.mac_ver()[0]}".strip()
    return f"{system} {platform.release()}".strip()

def new_report(kind: str, summary: str, description: str) -> dict:
    """A report with its date, version and OS filled in automatically (no name, address or messages)."""
    return {"id": time.time_ns(), "kind": "feature" if kind == "feature" else "bug", "summary": " ".join(summary.split())[:120],
            "description": description.strip()[:2000], "version": VERSION, "date": time.strftime("%Y-%m-%d %H:%M"),
            "os": _os_label(), "status": "open", "delivered": False}

def load_reports() -> list:
    return [r for r in load_json(REPORTS_FILE, list) if isinstance(r, dict)]

def save_report(report: dict):
    save_json(REPORTS_FILE, ([report] + load_reports())[:500])

def update_report(report_id, **changes):
    reports = load_reports()
    for r in reports:
        if r.get("id") == report_id: r.update(changes)
    save_json(REPORTS_FILE, reports)

def delete_report(report_id):
    save_json(REPORTS_FILE, [r for r in load_reports() if r.get("id") != report_id])

def format_report_text(r: dict) -> str:
    kind = "Feature suggestion" if r.get("kind") == "feature" else "Bug report"
    lines = [f"{kind}: {r.get('summary', '')}", f"Reported {r.get('date', '?')} · chat_gui v{r.get('version', '?')} · {r.get('os', '?')}"]
    if r.get("description"): lines += ["", r["description"]]
    return "\n".join(lines)

def check_reports_password(attempt: str) -> bool:
    import hmac
    digest = hashlib.sha256(("chat_gui-reports|" + attempt).encode("utf-8")).hexdigest()
    return hmac.compare_digest(digest, REPORTS_PASSWORD_SHA256)

def report_server():
    """The report server's address from REPORT_WORKER_URL, or None if it isn't set."""
    url = REPORT_WORKER_URL.strip().rstrip("/")
    return url if re.match(r"^https?://[^/\s]+", url) else None

def worker_call(path: str, body: dict = None, password: str = None, timeout: float = 8):
    """Talks to the report server. -> (HTTP status, decoded JSON or None); (None, None) if it can't be reached.
    A `body` makes it a POST; `password` is sent as the admin key (only the inbox needs that)."""
    base = report_server()
    if base is None:
        return None, None
    headers = {"User-Agent": "chat_gui-reporter/1.0"}
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if password:
        headers["Authorization"] = "Bearer " + password
    request = urllib.request.Request(base + path, data=data, headers=headers, method="POST" if body is not None else "GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status, raw = response.status, response.read()
    except urllib.error.HTTPError as e:   # the server answered, with an error status
        status, raw = e.code, e.read()
    except Exception:                     # offline, wrong address, blocked…
        return None, None
    try: return status, json.loads(raw.decode("utf-8"))
    except ValueError: return status, None

def deliver_report(report: dict) -> bool:
    """Sends a report to the report server, if one is set. True only if the server stored it."""
    status, data = worker_call("/report", body={
        "id": str(report.get("id", "")), "kind": report.get("kind", "bug"), "summary": report.get("summary", ""),
        "description": report.get("description", ""), "version": report.get("version", ""), "os": report.get("os", ""), "date": report.get("date", "")})
    return status == 200 and isinstance(data, dict) and bool(data.get("ok"))

APPEARANCE_KEYBIND = "<Control-Shift-KeyPress-T>"   # opens the Appearance window (themes, fonts)
ANNOUNCEMENTS_KEYBIND = "<Control-Shift-KeyPress-A>"   # the publisher's announcement menu (asks for the password)
ANNOUNCE_REFRESH_SECONDS = 20 * 60        # how often every copy re-reads the announcement
ANNOUNCE_URGENT_CHECK_SECONDS = 120       # …and how often it asks "is there an URGENT one?" (a tiny request) so those arrive fast
ANNOUNCE_MANUAL_COOLDOWN_SECONDS = 20     # "Refresh" in the Announcements window
ANNOUNCE_MAX_CHARS = 500

def _announcement_signing_bytes(text: str, urgent: bool, issued: int, hours: int) -> bytes:
    return json.dumps({"text": text, "urgent": bool(urgent), "issued": int(issued), "hours": int(hours)}, sort_keys=True, separators=(",", ":")).encode("utf-8")

def sign_announcement(text: str, urgent: bool, issued: int, hours: int, privkey) -> str:
    """Signs an announcement with the publisher's update signing key (the same key that signs releases)."""
    return base64.b64encode(privkey.sign(_announcement_signing_bytes(text, urgent, issued, hours))).decode("ascii")

def verify_announcement(data: dict):
    """The report server's announcement, checked. -> {seq, text, urgent, issued, hours} (text is "" if there's none, or it has
    run out), or None if its signature is bad — a forged or damaged announcement is simply ignored."""
    seq = int(data.get("seq") or 0)
    text = data.get("text") or ""
    if not text:
        return {"seq": seq, "text": "", "urgent": False, "issued": 0, "hours": 0}
    try:
        issued, hours, urgent = int(data["issued"]), int(data["hours"]), bool(data.get("urgent"))
        pubkey = Ed25519PublicKey.from_public_bytes(base64.b64decode(UPDATE_PUBLIC_KEY_B64))
        pubkey.verify(base64.b64decode(data["signature"]), _announcement_signing_bytes(text, urgent, issued, hours))
    except Exception:
        return None
    if hours and time.time() * 1000 > issued + hours * 3600 * 1000:
        text = ""
    return {"seq": seq, "text": text, "urgent": urgent and bool(text), "issued": issued, "hours": hours}

REPORT_REFRESH_COOLDOWN_SECONDS = 30   # how often "Refresh" in My previous reports may ask the server

def friendly_ago(seconds: float) -> str:
    """'just now', '3 minutes ago', '2 hours ago', '5 days ago'."""
    seconds = max(0, int(seconds))
    if seconds < 60: return "just now"
    for size, unit in ((86400, "day"), (3600, "hour"), (60, "minute")):
        if seconds >= size:
            n = seconds // size
            return f"{n} {unit}{'s' if n != 1 else ''} ago"
    return "just now"

def apply_report_statuses(data: dict) -> list:
    """Records what the report server says about this computer's reports (done / reopened, and when). Returns the reports
    that have JUST turned out to be completed and haven't been announced yet."""
    statuses = data.get("statuses") or {}
    completed = data.get("completed") or {}
    server_now = data.get("now")
    newly = []
    for r in load_reports():
        status = statuses.get(str(r.get("id")))
        if status is None:
            continue  # the server doesn't know it (deleted, or never arrived)
        if status == "done":
            changes = {"status": "done"}
            when_ms = completed.get(str(r.get("id")))
            if when_ms and server_now:  # work out WHEN on this computer's clock, from how long ago the server says it was
                changes["completed_at"] = time.time() - max(0, (server_now - when_ms) / 1000)
            if any(r.get(k) != v for k, v in changes.items()):
                update_report(r["id"], **changes)
            if not r.get("notified"):
                newly.append(dict(r, **changes))
        elif r.get("status") == "done":  # the developer reopened it
            update_report(r["id"], status="open", notified=False, completed_at=None)
    return newly

def relative_time_str(timestamp: float) -> str:
    delta = max(0, time.time() - timestamp)
    if delta < 60: return "just now"
    if delta < 3600: return f"{int(delta // 60)}m ago"
    return f"{int(delta // 3600)}h ago"


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
    letter (any a-z) for a small QOL patch that doesn't
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

BACKUPS_TO_KEEP = 5   # earlier versions kept next to the script (so "Restore a previous version" has something to offer)

def prune_old_backups(keep: int = None, target_path: str = None) -> int:
    """Deletes the backups earlier updates left next to the script (chat_gui.py.bak-<timestamp>), keeping only the
    newest `keep` of them (default BACKUPS_TO_KEEP; keep=0 keeps none). Only files with exactly that name are touched.
    Also clears a half-finished update's temp file. Returns how many files were deleted."""
    keep = BACKUPS_TO_KEEP if keep is None else keep
    target_path = os.path.abspath(target_path or __file__)
    folder, base = os.path.split(target_path)
    pattern = re.compile(r"^" + re.escape(base) + r"\.bak-(\d+)$")
    try:
        backups = sorted(((int(m.group(1)), name) for name in os.listdir(folder) if (m := pattern.match(name))), reverse=True)
    except OSError:
        return 0
    removed = 0
    for _, name in backups[max(0, keep):]:
        try:
            os.remove(os.path.join(folder, name))
            removed += 1
        except OSError:
            pass
    leftover = target_path + ".update_tmp"
    try:
        if os.path.exists(leftover) and time.time() - os.path.getmtime(leftover) > 3600:
            os.remove(leftover)
            removed += 1
    except OSError:
        pass
    return removed

def apply_update(payload: bytes) -> str:
    """Only ever called after verify_update_payload() has already
    succeeded. Backs up the running script before overwriting it, and
    writes via a temp file + atomic replace so a crash mid-write can't
    leave a half-written, unrunnable script behind."""
    target_path = os.path.abspath(__file__)
    stamp = int(time.time())
    while os.path.exists(f"{target_path}.bak-{stamp}"):  # two updates in the same second must not overwrite each other's backup
        stamp += 1
    backup_path = f"{target_path}.bak-{stamp}"
    shutil.copy2(target_path, backup_path)
    tmp_path = f"{target_path}.update_tmp"
    with open(tmp_path, "wb") as f:
        f.write(payload)
    os.replace(tmp_path, target_path)
    prune_old_backups(target_path=target_path)  # the backup just made stays; the oldest ones beyond BACKUPS_TO_KEEP go
    return backup_path

def list_backups(target_path: str = None) -> list:
    """The earlier versions kept next to the script, newest first: [{path, stamp, version, size}]."""
    target_path = os.path.abspath(target_path or __file__)
    folder, base = os.path.split(target_path)
    pattern = re.compile(r"^" + re.escape(base) + r"\.bak-(\d+)$")
    found = []
    try: names = os.listdir(folder)
    except OSError: return []
    for name in names:
        m = pattern.match(name)
        if not m: continue
        path = os.path.join(folder, name)
        try:
            with open(path, encoding="utf-8") as f: version = re.search(r'^VERSION = "([^"]+)"', f.read(), re.M)
            size = os.path.getsize(path)
        except (OSError, UnicodeDecodeError):
            continue
        if version: found.append({"path": path, "stamp": int(m.group(1)), "version": version.group(1), "size": size})
    return sorted(found, key=lambda b: b["stamp"], reverse=True)

def restore_from_backup(path: str) -> str:
    """Puts a kept earlier version back as the running script (the version being replaced is backed up first, so you can
    go forward again). Refuses anything that isn't a working copy of this app. Returns the new backup's path."""
    try:
        with open(path, "rb") as f: source = f.read()
        text = source.decode("utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise ValueError(f"Couldn't read that backup: {e}")
    try:
        compile(text, "chat_gui.py", "exec")
    except SyntaxError as e:
        raise ValueError(f"That backup isn't a working copy of the app ({e.msg}, line {e.lineno}).")
    if not re.search(r'^VERSION = "', text, re.M) or not re.search(r"^class ChatApp\(", text, re.M):
        raise ValueError("That file doesn't look like chat_gui.")
    return apply_update(source)


# ---- Global machine ban list ----
# A separate mechanism from the in-room /ipban above: that one only
# affects a single host's session, keyed by IP, and lives only in that
# host's runtime memory. This one is meant to follow a machine
# everywhere, forever, enforced by every copy of the app.
#
# Important limitation, stated plainly rather than oversold: this is a
# CLIENT-SIDE check. Anyone with the technical skill to read Python
# source can bypass it — delete the check, edit the file, spoof the
# fingerprint. It cannot be a true unbypassable lock, the same way no
# purely client-side mechanism can be. What it realistically provides:
# a real deterrent against casual reconnection, backed by a list that
# every client trusts because it's signed with the same private key
# used for OTA releases — nobody else can add or remove an entry from
# the version every client actually honors.
#
# Left empty, this feature is completely inert — no network call, no
# possibility of a false ban — until GLOBAL_BANLIST_URL is set.
GLOBAL_BANLIST_URL = "https://raw.githubusercontent.com/Richy023/chat-gui-releases/main/global_banlist_signed.json"
GLOBAL_BANLIST_SIGNING_KEY_FILE = app_path("update_signing_key.b64")

def get_machine_fingerprint() -> str:
    """A best-effort, stable-ish per-machine identifier — not the IP
    (which changes), and not anything personally identifying beyond
    'this is probably the same computer as last time'. Shown to hosts
    when someone connects (same as their IP already is) so a
    fingerprint can actually be captured before it's ever needed."""
    raw = f"{uuid.getnode()}|{platform.node()}|{platform.system()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]

GLOBAL_BAN_BEACON_SECONDS = 20       # how often every running copy asks the report server "has the ban list changed?" (a tiny request)
GLOBAL_BANS_CACHE_FILE = app_path("chat_gui_globalbans_cache.json")
GLOBAL_BAN_REASON_PREFIX = "Banned from chat_gui: "   # what a room's ban notice says when the publisher bans someone from the whole app

def fetch_global_banlist_github() -> dict:
    """The older list on GitHub — only used until the first ban is published through the report server, so bans made
    before that aren't lost."""
    raw = _https_get(GLOBAL_BANLIST_URL, timeout=8.0)
    data = json.loads(raw.decode("utf-8"))
    if "entries" not in data or "signature" not in data:
        raise ValueError("Ban list is missing required fields.")
    return data

def verify_global_banlist(data: dict) -> list:
    """Returns the verified entry list, or raises ValueError. The signature covers the exact JSON-serialized entries
    list, so a tampered or appended entry fails verification rather than being silently trusted."""
    if not UPDATE_PUBLIC_KEY_B64:
        raise ValueError("No signing key configured — refusing to trust an unverifiable ban list.")
    entries = data["entries"]
    if not isinstance(entries, list):
        raise ValueError("Ban list is malformed.")
    payload = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    try:
        pubkey = Ed25519PublicKey.from_public_bytes(base64.b64decode(UPDATE_PUBLIC_KEY_B64))
        pubkey.verify(base64.b64decode(data["signature"]), payload)
    except InvalidSignature:
        raise ValueError("Ban list signature is INVALID — ignoring it.")
    except Exception as e:
        raise ValueError(f"Could not verify the ban list: {e}")
    return entries

def fetch_global_bans() -> dict:
    """The verified global ban list -> {"entries", "signature", "seq", "skew", "source"}. `skew` is how far the report
    server's clock is ahead of this computer's, so a ban's end time means the same on every computer.
    Raises if nothing could be read or the signature is bad."""
    if report_server() is not None:
        code, data = worker_call("/bans", timeout=8)
        if code != 200 or not isinstance(data, dict):
            raise ConnectionError("couldn't reach the report server")
        now_ms = data.get("now")
        skew = (now_ms / 1000.0 - time.time()) if isinstance(now_ms, (int, float)) else 0.0
        if data.get("published"):
            return {"entries": verify_global_banlist(data), "signature": data["signature"], "seq": int(data.get("seq", 0)), "skew": skew, "source": "worker"}
        if not GLOBAL_BANLIST_URL:
            return {"entries": [], "signature": "", "seq": int(data.get("seq", 0)), "skew": skew, "source": "worker"}
        legacy = fetch_global_banlist_github()   # nothing published here yet: the old list still applies
        return {"entries": verify_global_banlist(legacy), "signature": legacy["signature"], "seq": int(data.get("seq", 0)), "skew": skew, "source": "github"}
    if not GLOBAL_BANLIST_URL:
        raise ConnectionError("no ban list is configured")
    legacy = fetch_global_banlist_github()
    return {"entries": verify_global_banlist(legacy), "signature": legacy["signature"], "seq": 0, "skew": 0.0, "source": "github"}

def save_global_bans_cache(info: dict):
    save_json(GLOBAL_BANS_CACHE_FILE, {"entries": info["entries"], "signature": info.get("signature", ""), "skew": info.get("skew", 0.0)})

def load_global_bans_cache():
    """The last list this computer verified, so a ban still holds with no internet. Re-verified every time it's read."""
    data = load_json(GLOBAL_BANS_CACHE_FILE, dict)
    try:
        return {"entries": verify_global_banlist({"entries": data.get("entries"), "signature": data.get("signature", "")}),
                "skew": float(data.get("skew", 0.0)), "seq": None, "source": "cache"}
    except Exception:
        return None

def _ban_entry_expired(entry: dict, now: float) -> bool:
    until = entry.get("until")
    return isinstance(until, (int, float)) and not isinstance(until, bool) and until <= now

def global_ban_match(entries, fingerprint: str, now: float):
    """The entry banning this device right now, or None. An entry with no end time (all the older ones) is permanent."""
    for entry in entries or []:
        if isinstance(entry, dict) and entry.get("fingerprint") == fingerprint and not _ban_entry_expired(entry, now):
            return entry
    return None

def global_ban_until_text(entry: dict, skew: float = 0.0) -> str:
    until = entry.get("until")
    if not isinstance(until, (int, float)) or isinstance(until, bool):
        return "permanently — until the publisher lifts it"
    return format_until(until - skew)

def global_ban_message(entry: dict, skew: float = 0.0) -> str:
    return (f"This device has been banned from chat_gui. Reason: {entry.get('reason') or 'no reason given'}. "
            f"Banned until: {global_ban_until_text(entry, skew)}.")

def check_global_ban():
    """-> (matching ban entry or None, clock skew). Fails OPEN: if the list can't be read (no internet, server down) we use the last
    verified copy, and with none of that we treat the device as not banned — this is a deterrent, not a hard security gate."""
    try:
        info = fetch_global_bans()
        save_global_bans_cache(info)
    except Exception:
        info = load_global_bans_cache()
    if not info:
        return None, 0.0
    return global_ban_match(info["entries"], get_machine_fingerprint(), time.time() + info.get("skew", 0.0)), info.get("skew", 0.0)

def _load_local_signing_key():
    """Loads the Ed25519 PRIVATE key from a local file that is never distributed with the app (see sign_release.py's own
    warnings about this same file). Returns None if it isn't present — which is the normal, expected case for literally
    everyone except the person who holds it, and is exactly what makes /globalban only usable by them."""
    try:
        with open(GLOBAL_BANLIST_SIGNING_KEY_FILE) as f:
            key_bytes = base64.b64decode(f.read().strip())
        return Ed25519PrivateKey.from_private_bytes(key_bytes)
    except Exception:
        return None

def sign_global_banlist(entries: list, privkey: Ed25519PrivateKey) -> dict:
    payload = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    signature = base64.b64encode(privkey.sign(payload)).decode("ascii")
    return {"entries": entries, "signature": signature}

def run_global_ban_command(cmd: str, arg: str, lookup, password):
    """The publisher's /globalban, /unglobalban and /globalbans. Runs on a background thread (it talks to the network).
    `lookup(name)` -> (ip, fingerprint, name) for someone this room knows, or None. Gated purely by local possession of
    the signing key, so it must run on the computer of whoever typed it (never on a host for a guest).
    -> (text to show, details of a ban to carry out in the room right now or None, True if the password was wrong)"""
    privkey = _load_local_signing_key()
    if privkey is None:
        return "This command requires the signing key file, which only the app's publisher has.", None, False
    try:
        info = fetch_global_bans()
    except Exception as e:
        return f"Couldn't read the current global ban list, so I stopped rather than risk dropping bans. ({e})", None, False
    skew = info.get("skew", 0.0)
    now = time.time() + skew
    entries = [e for e in info["entries"] if isinstance(e, dict) and not _ban_entry_expired(e, now)]

    def listing():
        if not entries:
            return "No one is banned from the whole app."
        lines = [f"Banned from the whole app ({len(entries)}):"]
        for n, e in enumerate(entries, 1):
            who = e.get("name") or "(unnamed)"
            lines.append(f"  #{n}  {who}  (device {str(e.get('fingerprint', ''))[:8]}) — {global_ban_until_text(e, skew)}: {e.get('reason') or 'no reason given'}")
        lines.append("Lift one with /unglobalban <#, name or device id>.")
        return "\n".join(lines)

    def publish(new_entries):
        code, data = worker_call("/bans/publish", body=sign_global_banlist(new_entries, privkey), password=password, timeout=15)
        if code == 200 and isinstance(data, dict) and data.get("ok"):
            return None
        if code == 401:
            return "Wrong password."
        return "The report server didn't accept the new list." if code else "Couldn't reach the report server."

    if cmd == "/globalbans":
        return listing(), None, False

    if cmd == "/globalban":
        parts = arg.split(maxsplit=2)
        if not parts:
            return "Usage: /globalban <name or device id> [time|perm] [reason]   (time: 30, 2h, 7d, 1y …)", None, False
        token = parts[0].strip()
        if re.fullmatch(r"[0-9a-fA-F]{16}", token):
            fp, name = token.lower(), ""
            known = lookup(token) if lookup else None
        else:
            found = lookup(token) if lookup else None
            if found is None:
                return (f"I don't know '{token}'. Use a name from this room (as host), or paste their device id — the 16 characters "
                        f"in '…device fingerprint: …' when they joined."), None, False
            fp, name = found[1], found[2] or token
            if not fp:
                return f"I know {name} but don't have their device id (they may be on an older version). Ask them for it, or ban them in the room with /ban.", None, False
        if fp == get_machine_fingerprint():
            return "That's this computer — I won't ban you from your own app.", None, False
        until, reason = parse_ban_args(parts)
        entry = {"id": os.urandom(3).hex(), "fingerprint": fp, "name": name, "reason": reason, "date": time.strftime("%Y-%m-%d"),
                 "until": None if until == float("inf") else int(until + skew)}
        error = publish([e for e in entries if e.get("fingerprint") != fp] + [entry])
        if error:
            return error, None, error == "Wrong password."
        who = name or f"device {fp[:8]}"
        text = (f"{who} is now banned from the whole app — {global_ban_until_text(entry, skew)}. Reason: {reason}. "
                f"Every running copy acts on it within about {GLOBAL_BAN_BEACON_SECONDS} seconds: anyone in a chat is removed and shown the reason.")
        return text, {"fp": fp, "name": name or who, "until": until, "reason": reason}, False

    if cmd == "/unglobalban":
        token = arg.strip().split(maxsplit=1)[0] if arg.strip() else ""
        if not token:
            return "Usage: /unglobalban <# from /globalbans, name or device id>", None, False
        index = int(token.lstrip("#")) - 1 if token.lstrip("#").isdigit() else None
        target = None
        if index is not None and 0 <= index < len(entries):
            target = entries[index]
        else:
            low = token.lower()
            target = next((e for e in entries if (e.get("name") or "").lower() == low or e.get("id") == low
                           or (len(low) >= 6 and str(e.get("fingerprint", "")).startswith(low))), None)
        if target is None:
            return f"'{token}' isn't banned from the whole app. /globalbans shows who is.", None, False
        error = publish([e for e in entries if e is not target])
        if error:
            return error, None, error == "Wrong password."
        return (f"{target.get('name') or 'device ' + str(target.get('fingerprint', ''))[:8]} can use the app again. "
                f"Running copies notice within about {GLOBAL_BAN_BEACON_SECONDS} seconds."), None, False
    return "Unknown command.", None, False


# ---- Changelog ----
# EMBEDDED_CHANGELOG is the static release history baked into this
# build — add one entry per release when you bump VERSION. Anything
# installed via OTA *after* this build additionally gets appended to
# CHANGELOG_FILE (a small local JSON file next to the script) at
# install time, so the in-app viewer stays complete going forward
# without needing the whole history re-embedded on every release.
EMBEDDED_CHANGELOG = [
    {   "version": "1.5.1",
        "date": "2026-11-18",
        "notes": (
            "New: Appearance. Themes (or your own colours), any font installed on your computer, text size, and a "
            "picture behind the main menu - from the 🎨 button, the main menu, or Ctrl+Shift+T. Saved on your computer "
            "only. Reworked bans: saved between sessions, they cover the person's device as well as their address, "
            "/ban takes a name or an IP, and there is now /bans (list) and /unban <number, name or IP>. "
            "Publisher only: /globalban, /unglobalban and /globalbans ban a device from the whole app, for a set time "
            "or until lifted, through the report server. Windows: sharp text on scaled displays, no more bright borders and scrollbars, dark "
            "title bars. Plus one more secret gradient name colour."
        ),
    },
    {   "version": "1.5.0f",
        "date": "2026-11-16",
        "notes": (
            "New: announcements. The publisher can post a message that shows as a banner across the top of every "
            "running copy of the app (in a chat or not), refreshing every 20 minutes or on demand from "
            "'Announcements' on the main menu. Urgent ones flash red and white, jump to the front and arrive "
            "within about 2 minutes. They're signed, so only the publisher can post one. New: 'Restore a "
            "previous version' on the main menu (admin password) puts back the last version, or any of the "
            "newest 5 kept on this computer."
        ),
    },
    {   "version": "1.5.0e",
        "date": "2026-11-15",
        "notes": (
            "The 'your report was completed' window now says when it was completed ('3 minutes ago', plus the date "
            "and time). The home-screen link is now 'Report a bug, suggest a feature, or view your previous reports': "
            "it opens a menu with a new-report form and a 'My previous reports' list showing whether each report is "
            "open or completed (and when), with a Refresh button (once every 30 seconds) that checks the report "
            "server right away instead of waiting for the 10-minute check."
        ),
    },
    {   "version": "1.5.0d",
        "date": "2026-11-14",
        "notes": (
            "The app now checks for updates when it starts, and shows an available update as a banner on the main "
            "menu (Update now / What's new) instead of a pop-up; the 'Check for Updates' link does the same. Old "
            "update backups are deleted automatically, keeping only the newest. When a bug report or suggestion you "
            "sent is marked completed, you get a window saying it will be released in the next update. For the "
            "report inbox owner: a slim bar at the top of the window flashes green and white for 5 seconds when a "
            "new report arrives (in a chat or not), with bursts collapsed. The report server also refuses floods: "
            "5 reports a minute per sender, 30 a minute overall."
        ),
    },
    {   "version": "1.5.0c",
        "date": "2026-11-11",
        "notes": (
            "Game leaderboards now show how many people are playing ('● 2 playing') instead of a tag on every "
            "row. Joining is clearer and more forgiving: spaces and dashes in a Room Code are ignored, and the "
            "error says what's actually wrong. Hosts now prefer a fixed port so joiners whose Wi-Fi blocks the "
            "lookup can still find them, and connection failures explain themselves. New: 'Report a bug or "
            "suggest a feature' on the home screen (date, version and OS added automatically), with a "
            "password-protected report inbox on Ctrl+Shift+B that can show everyone's reports."
        ),
    },
    {   "version": "1.5.0b",
        "date": "2026-11-10",
        "notes": (
            "Durations in /mute, /ban and /ipban now take units — 30 (minutes, as before), 90m, 2h, 7d, 2w, "
            "3mo, 1y — and months/years are calendar ones, so '1y' ends at the same date and time next year. "
            "/unwarn now asks which warning to remove when someone has more than one active (/unwarn <name> "
            "<#> or /unwarn <name> all) instead of silently removing the newest. The ⚠ button now shows all "
            "your active warnings; with more than one it opens a menu where you can pick a warning to see who "
            "gave it, why, its appeal status, and appeal it. Your warnings are remembered by the host, so they "
            "survive leaving and rejoining the chat."
        ),
    },
    {   "version": "1.5.0a",
        "date": "2026-11-09",
        "notes": (
            "Toast notifications for moderation outcomes: a warning appeal accepted or rejected, being "
            "banned, a ban appeal rejected, and being unbanned (not shown on Do Not Disturb). Warnings, "
            "mutes, kicks and bans now jump to the front of everything with a notice window — unless you "
            "were on Do Not Disturb, when they wait until you next open the window. Fixed: times in mute "
            "and ban messages were written in the host's time zone and could be hours out; they now show "
            "in your own local time. The ban message names the host instead of their IP address. The ⚠ "
            "button shows 'appeal rejected' for 3 seconds after its flash, then goes back to the warning "
            "number. /warning is now /warnings and lists your current and previous warnings (admins can "
            "add a name; the host is told they're invincible). Recent chats keeps one entry per room "
            "instead of replacing. Fixed: the Changelog window could show release-signing notes instead "
            "of the built-in changelog."
        ),
    },
    {   "version": "1.5.0",
        "date": "2026-11-08",
        "notes": (
            "The 'New messages' button is back to a small button (bottom right, in its own strip under "
            "the chat so it still can't smear on macOS) instead of a full-width bar, with no leftover gap "
            "once it hides. Fixed: the Recent "
            "list showed the same room several times if you'd joined it more than once — a room code "
            "now appears once, with its latest address."
        ),
    },
    {   "version": "1.4.11b",
        "date": "2026-11-08",
        "notes": (
            "Fixed: the 'New messages' button smeared up the screen as you scrolled (macOS). It is now a "
            "bar in its own strip under the chat instead of floating over it. The ⚠ Warning button's "
            "rejected-appeal flash is now six quick flashes between red and white, then back to yellow."
        ),
    },
    {   "version": "1.4.11a",
        "date": "2026-11-08",
        "notes": (
            "Fixed: clicking a recent chat no longer fills in the Host IP box. It used to paste the IP "
            "along with the port from that earlier session, and that port is usually out of date (the "
            "host picks a new one each time), which caused 'machine actively refused the connection'. "
            "Only the Room Code is filled in now; it finds the host's current address and port itself. "
            "The ⚠ Warning button now reacts to what the admins do: it flashes red and settles back to "
            "yellow when an appeal is rejected, and turns green ('Appeal accepted' / 'Warning removed') "
            "for about 5 seconds before disappearing when the warning is deleted."
        ),
    },
    {   "version": "1.4.11",
        "date": "2026-11-08",
        "notes": (
            "New: Flappy Bird! Ctrl+Shift+S now opens a game picker (Snake or Flappy Bird — press 1 or 2, "
            "or click). Flappy Bird has its own live leaderboard shared with the chat, just like Snake's; "
            "Space, Up, W or a click flaps, and the bird wears your name colour. The games now work from "
            "the home screen too, not just inside a chat — your best score per game is remembered on this "
            "computer, and open game windows stay open as you join or leave a chat. Warnings: a '⚠ Warning' "
            "button now stays in the chat's top bar while you have a warning you haven't dealt with, so "
            "closing the pop-up no longer loses the Appeal button (click it, or type /warning). Sending a "
            "warning appeal now edits 'Sending your appeal…' into 'Appeal sent ✔' instead of adding a new "
            "line. A banned person's screen now checks for unbans every 6 seconds (was 10). Also fixed: "
            "the 'New messages' button no longer smears as you scroll (macOS), counts how many messages "
            "are waiting, and goes away whenever you scroll back to the bottom; and the game windows no "
            "longer flash when your score goes up."
        ),
    },
    {   "version": "1.4.10d",
        "date": "2026-11-06",
        "notes": (
            "Replying to a message now pings its author (not if they're on Do Not Disturb — you're "
            "told, like an @mention). Unbans now reach the person: a banned person's screen checks in "
            "with the host every few seconds and shows 'You have been unbanned' with who did it and "
            "why; /unban <ip or name> [reason] takes a reason. Appeals can now be decided: each appeal "
            "has a number, /appeals lists the open ones, and /accept <#> [reason] or /reject <#> "
            "[reason] closes them — accepting a ban appeal lifts the ban, accepting a warning appeal "
            "deletes the warning, and the person is told the outcome and your reason. New: "
            "/unwarn <name> [warning # | all] [reason] to delete a warning, and /history [name] to see "
            "moderation history (warnings, mutes, kicks, bans, unbans, appeal decisions) for this "
            "session. Fixed: the 'You have been warned' pop-up now closes when you send an appeal."
        ),
    },
    {   "version": "1.4.10c",
        "date": "2026-11-04",
        "notes": (
            "Bug fix: joining a host by Room Code could fail with 'Could not find Room' even though "
            "entering the host's IP worked. The Room Code is built from the host's IP address, and a "
            "VPN (or any extra network adapter) can make a computer report a different address from "
            "the one guests actually reach it on. The code was also only worked out once, when the "
            "host screen opened, so a later IP change (Wi-Fi reconnect, sleep/wake, DHCP renewal) left "
            "it stale. The code is now re-checked the moment you press Host, and every few seconds "
            "while hosting; if it changes, the chat shows the new code and the title bar updates. "
            "The host answers for every address it has, guests try the Room Code against every "
            "network they're on, and the host's welcome line lists any extra addresses it found, to "
            "make odd networks easier to diagnose."
        ),
    },
    {   "version": "1.4.10b",
        "date": "2026-10-23",
        "notes": (
            "Appeals: if you're banned, the home screen now shows an APPEAL BAN button with a short, "
            "light-hearted questionnaire; the host and admins see it in the admin channel (one appeal "
            "per ban, and only if the host is online). Warnings got an Appeal button in the warning "
            "pop-up too, which works the same way. "
            "Reports: right-click a message or attachment and choose Report — the admin channel gets "
            "the message, who wrote it, who reported it and why. Reports on a whisper go to the host "
            "only, so a private message is never shown to admins. "
            "Reply: right-click a message and choose Reply — your message shows a small quote of what "
            "it answers, and clicking the quote jumps back to the original. "
            "Uploads: there's now a ✕ Cancel button on the 'Uploading and Sending…' line, which stops "
            "a send straight away (recipients are told it was cancelled and nothing is left behind). "
            "Large files: fixed people being kicked while receiving a big file — a recipient on a slow "
            "connection is no longer disconnected; they're skipped for that one file and told why, and "
            "stay in the chat. Anyone on an older version that can't receive files now just gets a "
            "one-line notice instead of being flooded with unreadable data (the likely cause of the "
            "freezes/kicks with a 350 MB file). "
            "Dates: mutes and temporary bans now show the full date and how long that is — "
            "e.g. 'Fri 23 Oct 2027, 14:05 (1 year)' — instead of only a clock time. "
            "File sizes now use the same units as your computer's file manager, so a file reads the same "
            "in the chat as it does on disk (Finder counts in thousands, Windows Explorer in 1024s — "
            "that was the mismatch). "
            "Layout: fixed the message box and its buttons being squashed very thin when status lines "
            "such as 'Uploading and Sending…', a mute notice or 'someone is typing' appeared above it. "
            "Bug fixes: the host now stamps the real sender on every message, typing indicator, Do Not "
            "Disturb change and reaction (a modified app could previously post as someone else, "
            "including the host); whispers can't be reacted to; a person who left (or renamed) while "
            "typing no longer keeps haunting everyone's 'is typing…' line; messages are limited to "
            "4,000 characters so one giant paste can't freeze everybody's window; connections that "
            "never say hello now time out instead of piling up; a half-received file whose id was "
            "reused no longer leaks a file handle; warning reasons are tidied and length-limited; "
            "and leftover upload messages from a chat you left no longer pop up in the next one."
        ),
    },
    {   "version": "1.4.10a",
        "date": "2026-10-22",
        "notes": (
            "Rooms now hold up to 15 guests (it was 4). "
            "New: paste images. Press Ctrl+V (Cmd+V on a Mac) with an image on your clipboard — "
            "a screenshot, or an image copied from a browser or editor — and a small preview "
            "asks whether to send it. It goes out like any attachment, so it can be deleted "
            "afterwards, and if the message box starts with /whisper and a name it's sent "
            "privately to that person. Files copied in Explorer or Finder can be pasted and "
            "sent the same way. Normal text pasting is unchanged. "
            "Nicknames: /nick now tells you how many changes you have left (everyone, admins "
            "included, gets two per chat; only the host can use /rename for inappropriate names). "
            "The 1 GB file limit stays — a real 1 GiB file was sent end to end and arrived intact."
        ),
    },
    {   "version": "1.4.10",
        "date": "2026-10-21",
        "notes": (
            "Large files: fixed sending a big file disconnecting everyone. Files used to go "
            "out as one giant message that overflowed everyone's send queue (anything over "
            "roughly 300 MB), and the old limit could never really work. Files now stream in "
            "small pieces, paced to the slowest person, and are written to disk as they "
            "arrive — so the limit is a genuine 1 GB, memory use stays low, chat stays "
            "instant while a file is going, someone on a bad connection is only dropped "
            "themselves (never the whole room), and if the sender disappears halfway nothing "
            "is left behind on anyone's computer. You'll see 'Uploading and Sending… 40%' "
            "and 'Receiving…' progress, and downloading a big file now copies in the "
            "background instead of freezing the window. "
            "Nicknames: type /nick <new name> to change your own name — up to twice per chat, "
            "no need to disconnect. The host has /rename <current name> <new name> for "
            "inappropriate names; that doesn't use up the person's own changes, but they can't "
            "change it back. Admin status, colours, mutes, whispers, the right to edit your own "
            "messages and your Snake score all follow you to the new name. Names can't contain "
            "spaces or the | character. "
            "New: /warn <name> [reason] for the host and admins. The person gets a warning "
            "pop-up with a running warning count, everyone else sees '<name> has been warned', "
            "and the admin log records who warned whom and why. "
            "Version numbers like 1.4.10 are compared numerically, so 1.4.10 is correctly newer "
            "than 1.4.9d and 1.4.1. "
            "1.4.10 isn't compatible with 1.4.9d for file transfers, so update everyone together."
        ),
    },
    {   "version": "1.4.9d",
        "date": "2026-10-15",
        "notes": (
            "Joining: fixed rejoining after leaving while muted (it failed with an "
            "'invalid handshake'), and fixed joins occasionally failing if someone else "
            "sent a message or left at the same instant. If the same device reconnects it "
            "now simply replaces its old session instead of being refused with 'Nickname "
            "already in use'; a muted user's name stays reserved for other devices until "
            "the mute ends. "
            "Delivery: messages sometimes not reaching certain people is fixed at the root "
            "— every connection now has its own ordered send queue, so one slow or stalled "
            "person can no longer hold up or scramble messages for others, and big files "
            "can no longer interleave with chat on the wire. Receiving large files is much "
            "faster, which also removes the lag when deleting an attachment. If a receive "
            "error ever does happen you're now disconnected cleanly instead of silently "
            "stopping seeing messages. "
            "Uploads: files, images and stickers send in the background and show "
            "'Uploading and Sending…' instead of freezing the chat. "
            "Whispers: now proper messages you can edit or delete (right-click), private "
            "to you and the recipient — admins never see them, and only the host is told "
            "(in a separate Host Log, with the old and new text) when one is edited or deleted — and "
            "they can carry files, images and stickers: type /whisper and their name, then "
            "click the attach or sticker button. Muted users can't whisper and slowmode "
            "applies to whispers. "
            "Pings: @mentioning several people pings all of them, and if some are on Do Not "
            "Disturb you get a single message listing everyone who is (plus any unknown names). "
            "Menus: the emoji, sticker and suggestion pop-ups now open inside the window, "
            "which fixes the chat box seizing up until the window was minimised and reopened. "
            "Snake: the leaderboard is now live across the whole chat — everyone's best "
            "score and who's playing right now — and starts empty whenever the chat is "
            "restarted; the snake now always matches your name colour. "
            "New: two more secret gradient name colours. "
            "1.4.9d isn't compatible with 1.4.9c for whispers and attachments, so update "
            "everyone together."
        ),
    },
    {   "version": "1.4.9c",
        "date": "2026-10-14",
        "notes": (
            "New: delete attachments. Right-click a file, image or sticker and choose "
            "Delete attachment — it disappears for everyone: the image preview or "
            "download button is removed and the line just says '[attachment deleted]' "
            "(or '[attachment deleted by Name]' if an admin removed it). You can delete "
            "your own; admins and the host can delete anyone's, except the host's own "
            "attachments, which only the host can delete. The admin log records these "
            "too, showing who deleted what. Right-click an attachment also gives you "
            "'Save As...' (replacing the old image-only menu). Deleted and scrolled-off "
            "attachments now free their memory. Because attachments now carry an id, "
            "1.4.9c and 1.4.9b can't exchange files — update everyone together."
        ),
    },
    {   "version": "1.4.9b",
        "date": "2026-10-13",
        "notes": (
            "New: edit and delete your own messages. Right-click a message you sent "
            "and choose Edit or Delete — everyone's chat updates, edited messages show "
            "'(edited)' and deleted ones show '[message deleted]'. Admins (and the host) "
            "can also delete other people's messages from the same right-click menu; "
            "the host's own messages can only be deleted by the host. The admin log "
            "(what the host and admins see) now records every edit — showing the old "
            "and new text — and every delete, with the username of whoever did it. "
            "Editing/deleting needs the host and the person to be on 1.4.9b; anyone on "
            "an older version simply keeps seeing the original message (no garbled "
            "text), and if the host is older you'll be told it isn't supported."
        ),
    },
    {   "version": "1.4.9a",
        "date": "2026-10-12",
        "notes": (
            "Fixed the '↓ New messages' button sometimes staying on screen even "
            "though you were already at the bottom of the chat — most noticeable "
            "right after starting a room (seen on macOS). The button now re-checks "
            "once the window has finished laying out, and also when the window is "
            "resized. No other changes, and no protocol changes."
        ),
    },
    {   "version": "1.4.9",
        "date": "2026-10-09",
        "notes": (
            "Tidy-up and efficiency pass, mostly UI/UX. Connecting no longer "
            "freezes the window (the ban-list check now runs in the background), "
            "Connect shows a 'Connecting...' state and can't be double-clicked, "
            "pressing Enter on any connect-screen field connects, and your display "
            "name and DND keybind are remembered between launches. In chat: the "
            "log only auto-scrolls when you're already at the bottom (a 'New "
            "messages' button appears if you've scrolled up, and your own messages "
            "always jump to the bottom); very old lines are trimmed so long "
            "sessions stay fast; Up/Down recall your previous messages; Esc closes "
            "suggestion/emoji/sticker pop-ups; the window title shows an unread "
            "count while the app is in the background; the online list only "
            "redraws when something changed; typing notices are only sent when "
            "the text really changes; image thumbnails are prepared off the UI "
            "thread so big pictures don't stall the chat; emoji/sticker pickers "
            "open right above their buttons and stickers have larger, centered "
            "labels; the changelog window is resizable. Fixes: one bad event can "
            "no longer stop the whole UI event loop; leaving a chat yourself no "
            "longer shows a bogus 'Disconnected from host' error; late events "
            "from a closed session can't leak into the next one; host /color "
            "now refreshes your own view immediately; bare /ban, /mute, etc. show "
            "usage instead of being posted as a chat message. Under the hood: "
            "shared JSON helpers with atomic saves, table-driven moderation "
            "commands and event handling, and de-duplicated slowmode, file-send "
            "and unlock code. No protocol changes, so 1.4.9 works alongside 1.4.8x."
        ),
    },
    {   "version": "1.4.8d",
        "date": "2026-09-07",
        "notes": (
            "The auto-discovered chat list from 1.4.8c is reverted — it relied "
            "on LAN broadcast, which routed/segmented networks (common on bigger "
            "home or institutional setups) filter out, so it silently never "
            "found anything for some people. Joining is back to typing a Room "
            "Code (plus Host IP if that fails), like before 1.4.8c. New: 'Join a "
            "chat' now shows a Recent list of hosts you've successfully "
            "connected to before — click one to fill in its Room Code and Host "
            "IP automatically, then just enter the password. Entries older than "
            "a day are dropped automatically, since a host's IP (and so its Room "
            "Code) usually isn't the same the next day."
        ),
    },
    {   "version": "1.4.8b",
        "date": "2026-08-28",
        "notes": (
            "Added global banlist."
        ),
    },
    {   "version": "1.4.8a",
        "date": "2026-08-23",
        "notes": (
            "Added a device-level global ban system, separate from the existing "
            "in-room /ipban: a device fingerprint (shown to hosts when someone "
            "connects, same as their IP already is) can be added to a signed ban "
            "list that every copy of the app checks before hosting or joining. "
            "Adding to that list is gated by possession of a private key that's "
            "never distributed with the app — not a password, since anything "
            "baked into the public source can't actually stay secret. Worth "
            "knowing honestly: like any client-side check, a technical user could "
            "still bypass it by editing their own copy — this is a real deterrent, "
            "not an unbreakable lock. Inert by default (zero network calls) unless "
            "explicitly configured."
        ),
    },
    {   "version": "1.4.8",
        "date": "2026-08-22",
        "notes": (
            "Snake leaderboard shows every player ranked, not just a top few. "
            "Fixed a real bug where an unexpected error while handling a message "
            "mid-session could silently skip cleanup, leaving a 'ghost' user stuck "
            "in the room — blocking that name from reconnecting and never actually "
            "leaving the member list, until the app was restarted. Added a second "
            "secret gradient unlock (blue-toned this time) alongside the existing "
            "one — as always, the actual codes are intentionally not written here. "
            "Host can now IP-ban someone directly by address (even if they're not "
            "currently connected) with a new host-only command, instead of only "
            "being able to ban someone already in the room."
        ),
    },
    {   "version": "1.4.7",
        "date": "2026-08-22",
        "notes": (
            "Rainbow name hover animation now works in the chat log too, not just "
            "the sidebar (each message instance animates independently — hovering "
            "one doesn't animate every other message from the same person). Fixed "
            "the sidebar rendering rainbow names with abnormally spaced-out letters. "
            "Added Snake: press Ctrl+Shift+S to open it (single-player for now). "
            "Host plays a plain white snake, rainbow-unlocked plays a moving "
            "rainbow snake, everyone else gets a random color. High scores are "
            "saved locally and shown as a small leaderboard in the game window."
        ),
    },
    {   "version": "1.4.6",
        "date": "2026-08-21",
        "notes": (
            "Added a secret rainbow unlock: entering a specific hidden phrase in "
            "the 'Host IP' field (instead of an address) gives your name an animated "
            "rainbow treatment — a static color gradient in chat, and in the member "
            "list it actually shifts/moves while you hover over it. Host color stays "
            "plain white as always. Snake multiplayer minigame is scoped as a "
            "separate follow-up — didn't want to rush a real-time networked game "
            "engine into the same pass as everything else."
        ),
    },
    {   "version": "1.4.5c",
        "date": "2026-08-21",
        "notes": (
            "Fixed 'View Changelog' clipping into 'Check for Updates' on the "
            "connect screen (Mac only) — the gap between them was a hardcoded "
            "pixel offset that didn't account for macOS rendering text taller "
            "than other platforms at the same font size. Now sized from the "
            "actual rendered text height instead of a fixed guess."
        ),
    },
    {   "version": "1.4.5b",
        "date": "2026-08-21",
        "notes": (
            "Host can now change their own color as many times as they want, "
            "overriding the usual once-per-session limit that still applies to guests."
        ),
    },
    {   "version": "1.4.5a",
        "date": "2026-08-21",
        "notes": (
            "Fixed a major bug where the connection handshake kept failing."
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

CHANGELOG_FILE = app_path("chat_gui_changelog.json")

def _load_local_changelog() -> list:
    return load_json(CHANGELOG_FILE, list)

def _save_local_changelog(entries: list):
    save_json(CHANGELOG_FILE, entries, indent=2)

def record_changelog_entry(version: str, notes: str):
    """Called after an OTA update is successfully applied, so the
    changelog viewer picks up releases beyond what's embedded here."""
    entries = [e for e in _load_local_changelog() if e.get("version") != version]
    entries.append({"version": version, "date": time.strftime("%Y-%m-%d"), "notes": notes})
    _save_local_changelog(entries)

def full_changelog() -> list:
    """Embedded history plus anything recorded locally since, deduped
    by version and sorted newest-first (letter-suffix aware)."""
    # The built-in text is authoritative. The local file only fills in versions this build doesn't know
    # about — it holds whatever notes came with an update's manifest (e.g. what was typed when signing the
    # release), which must never replace the real changelog entry for the same version.
    by_version = {e["version"]: e for e in _load_local_changelog()}
    by_version.update({e["version"]: e for e in EMBEDDED_CHANGELOG})
    return sorted(by_version.values(), key=lambda e: _version_tuple(e["version"]), reverse=True)


# ---- Custom stickers ----
# Uploaded stickers are stored locally (as base64 JPEG bytes in a small
# JSON file next to the script) so they persist across sessions instead
# of needing to be re-uploaded every time. They're sent over the wire
# exactly like the built-in stickers — as a regular JPEG file transfer.
STICKERS_FILE = app_path("chat_gui_stickers.json")
MAX_CUSTOM_STICKERS = 24

def _load_custom_stickers() -> dict:
    return load_json(STICKERS_FILE, dict)

def _save_custom_stickers(stickers: dict):
    save_json(STICKERS_FILE, stickers)


class Hub:
    def __init__(self, fernet: Fernet, host_name: str, on_typing_change, on_admin_log, on_message_event=None):
        self.fernet = fernet
        self.host_name = host_name
        self.on_typing_change = on_typing_change
        self.on_admin_log = on_admin_log
        self.on_message_event = on_message_event  # (kind, payload) for the host's own UI
        self.lock = threading.Lock()
        self.closed = False  # set when the host shuts the room down; handler threads then stay quiet
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
        self.gradient_users = {}  # name.lower() -> sentinel (RAINBOW_SENTINEL, BLUE_SENTINEL, ...)
        self.messages = {}        # msg_id -> {"author", "text"}; oldest dropped past MAX_TRACKED_MESSAGES
        self.outboxes = {}        # sock -> Outbox (one writer thread per connected guest)
        self.transfers = {}       # msg_id -> in-flight file transfer (see _handle_guest_file)
        self.warnings = {}        # name.lower() -> how many times they've been warned this session
        self.reports = set()      # (reporter.lower(), msg_id) — one report per person per message
        self.warn_log = {}        # (name.lower(), warning number) -> {"by", "reason", "appealed"}
        self.report_times = {}    # reporter.lower() -> recent report timestamps (rate limit)
        self.host_nick = {"nick_changes": 0, "nick_locked": False}  # same bookkeeping the guests keep in their client info
        self.local_files = None   # the host's own FileAssembler (set by HostConnection)
        self.snake = {}           # name.lower() -> {"name", "best", "score", "playing"}; lives and dies with the room
        self.boards = {"snake": self.snake, "flappy": {}}  # one live leaderboard per minigame
        self.unbans = {}          # ip -> {"by", "reason", "time"}: who lifted a ban and why (so the banned person can be told)
        self.appeals = {}         # id -> {"id", "kind", "who", "ip", "number", "status", ...}
        self.appeal_seq = 0
        self.mod_log = []         # moderation history for /history (this session only)
        self.ip_names = {}        # ip -> names seen joining from that address
        self.known_devices = {}   # name.lower() -> {"name", "ip", "fp"}: who joined from where this session (so /ban works on someone who just left)
        self._load_bans()

    # ---- identity helpers ----

    def is_host(self, name: str) -> bool:
        return name.lower() == self.host_name.lower()

    def set_gradient(self, name: str, sentinel: str):
        with self.lock:
            self.gradient_users[name.lower()] = sentinel

    def set_color(self, name: str, color_hex: str, once: bool = False):
        with self.lock:
            self.colors[name.lower()] = color_hex
            if once:
                self.color_changed_once.add(name.lower())

    def assign_color(self, name):
        with self.lock:
            used = set(self.colors.values())
            available = [c for c in COLOR_PALETTE.values() if c not in used]
            color = random.choice(available or list(COLOR_PALETTE.values()))
            self.colors[name.lower()] = color
            return color

    def free_color(self, name):
        with self.lock:
            # A same-name session may already have replaced this one (a reconnect) —
            # don't strip the colour out from under it.
            if any(info["name"].lower() == name.lower() for info in self.clients.values()):
                return
            self.colors.pop(name.lower(), None)

    def colormap_snapshot(self):
        with self.lock:
            return {n: self.gradient_users.get(n, c) for n, c in self.colors.items()}

    def colormap_string(self):
        return ",".join(f"{n}={c}" for n, c in self.colormap_snapshot().items())

    def broadcast_colormap(self):
        self.broadcast(COLORMAP_PREFIX + self.colormap_string())

    # ---- admin log ----

    def log_admin_action(self, admin_name: str, text: str):
        log_text = f"🛡️ [Admin Log] {admin_name} {text}"

        if not self.is_host(admin_name):
            self.on_admin_log(log_text)

        msg_proto = ADMIN_LOG_PREFIX + log_text
        with self.lock:
            targets = [
                s for s, info in self.clients.items()
                if info["name"].lower() in self.admins
                and info["name"].lower() != admin_name.lower()
            ]
        for s in targets:
            self.send_private(s, msg_proto)

    # ---- message ownership: edit / delete ----

    MAX_TRACKED_MESSAGES = 1000

    def record_message(self, msg_id: str, author: str, text: str, kind: str = "text", to: str = None) -> bool:
        """Remembers who sent a message (kind "text") or attachment (kind "file", `text`
        = its filename) so later edits/deletes can be authorised and logged. Returns
        `to` marks a private (whisper) message, which only its two parties may edit,
        delete or see. Returns False — and the caller should drop the message — if the id is unusable or already
        known: an id is never reassigned, otherwise someone could re-send a victim's id
        to take over their message."""
        if not msg_id or len(msg_id) > 32:
            return False
        with self.lock:
            if msg_id in self.messages:
                return False
            self.messages[msg_id] = {"author": author, "text": text, "kind": kind, "to": to}
            while len(self.messages) > self.MAX_TRACKED_MESSAGES:
                self.messages.pop(next(iter(self.messages)))
        return True

    def _emit(self, kind: str, payload: dict):
        if self.on_message_event:
            self.on_message_event(kind, payload)

    def _deliver_update(self, to, author: str, wire_text: str, event_kind: str, event_payload: dict):
        """Edit/delete notices go to everyone for public messages, but only to the two
        people involved for a whisper."""
        if to is None:
            self.broadcast_feature(FEATURE_EDIT, wire_text)
            self._emit(event_kind, event_payload)
            return
        for name in {author.lower(): author, to.lower(): to}.values():
            if self.is_host(name):
                self._emit(event_kind, event_payload)
            elif (sock := self.find_socket_by_name(name)) is not None:
                self.send_private(sock, wire_text)

    def edit_message(self, msg_id: str, editor: str, new_text: str):
        """Authors only. Returns an error message for the requester, or None on
        success (or when nothing changed)."""
        new_text = new_text.strip()
        if not new_text:
            return "An edited message can't be empty — delete it instead."
        if len(new_text) > MAX_MESSAGE_CHARS:
            return f"That message is too long (the limit is {MAX_MESSAGE_CHARS:,} characters)."
        with self.lock:
            record = self.messages.get(msg_id)
            if record is None:
                return "That message can't be edited any more."
            if record.get("kind") == "file":
                return "Attachments can't be edited — delete it instead."
            if record["author"].lower() != editor.lower():
                return "You can only edit your own messages."
            old_text, to = record["text"], record.get("to")
            if old_text == new_text:
                return None
            record["text"] = new_text
        self._deliver_update(to, editor, f"{EDIT_PREFIX}{msg_id}|{editor}|{new_text}",
                             "msg_edit", {"msg_id": msg_id, "text": new_text, "editor": editor})
        if to is None:
            self.log_admin_action(editor, f'edited their message: "{_clip(old_text)}" → "{_clip(new_text)}"')
        elif not self.is_host(editor):  # whispers: the host (only) is told what changed — admins never see them
            self.log_host_only(editor, f'edited a whisper to {to}: "{_clip(old_text)}" → "{_clip(new_text)}"')
        return None

    def delete_message(self, msg_id: str, deleter: str, deleter_is_admin: bool):
        """Authors may delete their own; admins (and the host) may delete anyone's
        public messages except the host's. Whispers: only their sender. Returns an
        error message, or None on success."""
        with self.lock:
            record = self.messages.get(msg_id)
            if record is None:
                return "That message can't be deleted any more."
            author, text, to = record["author"], record["text"], record.get("to")
            noun = "attachment" if record.get("kind") == "file" else ("whisper" if to else "message")
            own = author.lower() == deleter.lower()
            if to is not None and not own:
                return f"You can only delete your own {noun}s."
            if not own and not deleter_is_admin:
                return f"You can only delete your own {noun}s."
            if not own and self.is_host(author):
                return f"You cannot delete the host's {noun}s."
            del self.messages[msg_id]  # gone for good — it can't be edited or deleted again
        self._deliver_update(to, author, f"{DELETE_PREFIX}{msg_id}|{deleter}",
                             "msg_delete", {"msg_id": msg_id, "deleter": deleter})
        if to is None:
            if own:
                self.log_admin_action(deleter, f'deleted their own {noun}: "{_clip(text)}"')
            else:
                self.log_admin_action(deleter, f'deleted {author}\'s {noun}: "{_clip(text)}"')
        elif not self.is_host(deleter):  # whispers: host-only log (the sender is the only one who can delete them)
            what = "an attachment whispered to" if noun == "attachment" else "a whisper to"
            self.log_host_only(deleter, f'deleted {what} {to}: "{_clip(text)}"')
        return None

    # ---- appeals ----

    def mark_ban_appealed(self, ip: str) -> bool:
        """One appeal per ban. False if that address isn't banned or already appealed."""
        with self.lock:
            self._purge_expired()
            ban = self.banned_ips.get(ip)
            if ban is None or ban.get("appealed"):
                return False
            ban["appealed"] = True
            self._save_bans()
            return True

    def mark_warning_appealed(self, name: str, number) -> dict:
        """Returns the warning's record the first time it's appealed, else None."""
        with self.lock:
            record = self.warn_log.get((name.lower(), number))
            if record is None or record["appealed"] or record.get("deleted"):
                return None
            record["appealed"] = True
            return dict(record)

    def register_appeal(self, kind: str, who: str, ip: str = None, number=None) -> int:
        """Gives an appeal a number so the admins can /accept or /reject it."""
        with self.lock:
            self.appeal_seq += 1
            self.appeals[self.appeal_seq] = {"id": self.appeal_seq, "kind": kind, "who": who, "ip": ip, "number": number,
                                             "status": "pending", "time": time.time()}
            appeal_id = self.appeal_seq
        self.record_mod("appeal filed", who, who, "", ip=ip, detail=f"({kind} #{appeal_id})")
        return appeal_id

    def pending_appeals(self) -> list:
        with self.lock:
            return [dict(a) for a in self.appeals.values() if a["status"] == "pending"]

    def _notice_to(self, name: str, text: str):
        sock = self.find_socket_by_name(name)
        if sock is not None:
            self.send_private(sock, NOTICE_PREFIX + text)

    def _warn_state_to(self, name: str, number, state: str):
        """Tells a warned person's app how their warning ended up (their ⚠ button follows) — only if
        their app understands it; an older one would show the raw protocol text."""
        sock = self.find_socket_by_name(name)
        if sock is not None and FEATURE_WARNSYNC in self.get_info(sock).get("features", ()):
            self.send_private(sock, f"{WARNSTATE_PREFIX}{number}|{state}")

    def decide_appeal(self, appeal_id: int, accept: bool, by: str, reason: str):
        """Accepts or rejects an appeal. -> (error or None, reply text, admin-log text).
        Accepting a ban appeal lifts the ban; accepting a warning appeal deletes the warning."""
        reason = " ".join(reason.split())[:300] or "no reason given"
        with self.lock:
            a = self.appeals.get(appeal_id)
            if a is None:
                return f"There's no appeal #{appeal_id}. /appeals lists the open ones.", None, None
            if a["status"] != "pending":
                return f"Appeal #{appeal_id} was already {a['status']} by {a['decided_by']}.", None, None
            a.update(status="accepted" if accept else "rejected", decided_by=by, decision_reason=reason, decided_at=time.time())
            a = dict(a)
        verb = "accepted" if accept else "rejected"
        kind_text = "ban" if a["kind"] == "ban" else f"warning #{a['number']}"
        what = f"{a['who']}'s {kind_text} appeal"
        self.record_mod(f"appeal {verb}", a["who"], by, reason, ip=a.get("ip"), detail=f"({a['kind']} #{appeal_id})")
        extra = ""
        if a["kind"] == "ban":
            if accept:
                if self.unban_ip(a["ip"], by, f"your appeal was accepted — {reason}", log=False):
                    extra = " The ban has been lifted."
                    self.broadcast(f"* {a['who']}'s ban appeal was accepted *")
                else:
                    extra = " (That ban had already been lifted.)"
            else:
                with self.lock:
                    ban = self.banned_ips.get(a["ip"])
                    if ban is not None:
                        ban["appeal_result"] = {"status": "rejected", "by": by, "reason": reason}
                        self._save_bans()
                extra = " The ban stays; they'll see your reason on their ban screen."
        else:
            if accept:
                error, _, _ = self.delete_warning(a["who"], a["number"], by,
                                                  f"appeal accepted — {reason}", log=False, state="accepted")
                extra = " The warning has been deleted." if error is None else " (That warning had already been removed.)"
            else:
                self._notice_to(a["who"], f"Your appeal for warning #{a['number']} was rejected by {by}. Reason: {reason}")
                self._warn_state_to(a["who"], a["number"], "rejected")
                extra = " The warning stands; they've been told."
        text = f"Appeal #{appeal_id} ({what}) {verb}. Reason: {reason}.{extra}"
        return None, text, f"{verb} appeal #{appeal_id} from {a['who']}. Reason: {reason}"

    def delete_warning(self, name: str, number, by: str, reason: str, log: bool = True, state: str = "removed"):
        """Deletes a warning (the latest active one if `number` is None); the warned person is told if
        they're here. Warning numbers are never reused. -> (error or None, canonical name, number)."""
        reason = " ".join(reason.split())[:300] or "no reason given"
        with self.lock:
            if number is None:
                active = [n for (who, n), rec in self.warn_log.items() if who == name.lower() and not rec.get("deleted")]
                if not active:
                    return f"{name} has no active warnings.", name, None
                number = max(active)
            rec = self.warn_log.get((name.lower(), number))
            if rec is None:
                return f"{name} has no warning #{number}.", name, number
            if rec.get("deleted"):
                return f"{rec.get('name', name)}'s warning #{number} was already removed.", name, number
            rec.update(deleted=True, deleted_by=by, deleted_reason=reason, deleted_at=time.time())
            canonical = rec.get("name", name)
        if log:
            self.record_mod("warning removed", canonical, by, reason, detail=f"#{number}")
        self._notice_to(canonical, f"Warning #{number} was removed by {by}. Reason: {reason}")
        self._warn_state_to(canonical, number, state)  # "accepted" when it's the result of an appeal
        return None, canonical, number

    def active_warnings(self, name: str) -> list:
        """[(number, record)] of `name`'s warnings that haven't been removed, oldest first."""
        key = name.lower()
        with self.lock:
            return sorted(((n, dict(r)) for (who, n), r in self.warn_log.items() if who == key and not r.get("deleted")), key=lambda item: item[0])

    def warning_sync_payload(self, name: str) -> list:
        """What a (re)joining person's ⚠ button needs: each active warning, and where its appeal stands."""
        with self.lock:
            appeals = {a["number"]: a["status"] for a in self.appeals.values() if a["kind"] == "warn" and a["who"].lower() == name.lower()}
        payload = []
        for number, r in self.active_warnings(name):
            status = appeals.get(number)
            appeal = status if status in ("pending", "rejected") else ("pending" if r.get("appealed") else "none")
            payload.append({"n": number, "by": r["by"], "reason": r["reason"], "appeal": appeal})
        return payload

    def warnings_text(self, name: str, own: bool) -> str:
        """Every warning `name` has had this session — current and previous — and what became of each."""
        key = name.lower()
        with self.lock:
            records = sorted(((n, dict(r)) for (who, n), r in self.warn_log.items() if who == key), key=lambda item: -item[0])
            appeals = {a["number"]: dict(a) for a in self.appeals.values() if a["kind"] == "warn" and a["who"].lower() == key}
        if not records:
            return "You have no warnings this session." if own else f"{name} has no warnings this session."
        shown = records[0][1].get("name", name)
        active = sum(1 for _, r in records if not r.get("deleted"))
        lines = [f"{'Your warnings' if own else f'Warnings for {shown}'} (this session): {len(records)} issued, {active} active"]
        for number, r in records:
            if r.get("deleted"):
                status = f"removed by {r.get('deleted_by', '?')}: {r.get('deleted_reason', 'no reason given')}"
            else:
                status = "ACTIVE"
                appeal = appeals.get(number)
                if appeal and appeal["status"] == "pending": status += " · appeal pending"
                elif appeal and appeal["status"] == "rejected": status += " · appeal rejected"
                elif r.get("appealed"): status += " · appealed"
            when = f", {ago_token(r['time'])}" if r.get("time") else ""
            lines.append(f"  #{number}  {status} — from {r['by']}{when}: \"{r['reason']}\"")
        return "\n".join(lines)

    def ban_status(self, ip: str, fp=None) -> dict:
        """What a banned person's app is told when it checks in."""
        with self.lock:
            self._purge_expired()
            key = self._find_ban_key(ip, fp)
            ban = self.banned_ips.get(key) if key is not None else None
            unban = next((u for u in self.unbans.values() if u.get("ip") == ip or (fp and u.get("fp") == fp)), None)
            if ban is not None:
                return {"state": "banned", "until": until_token(ban["until"]), "by": ban.get("banned_by", ""),
                        "reason": ban.get("reason", ""), "appeal": ban.get("appeal_result")}
            if unban is not None:
                return {"state": "unbanned", "by": unban["by"], "reason": unban["reason"]}
            return {"state": "free"}  # the ban ran out (or was cleared some other way)

    def resolve_ban_target(self, token: str):
        """What someone typed -> the key of a current ban. Accepts the number from /bans (#2 or 2), an address, the name
        of the banned person (as they were called, or as we saw them join), or the start of a device fingerprint."""
        token = token.strip()
        entries = self.bans_list()
        with self.lock:
            if token in self.banned_ips:
                return token
            if token.lstrip("#").isdigit() and 1 <= int(token.lstrip("#")) <= len(entries):
                return entries[int(token.lstrip("#")) - 1][0]
            lowered = token.lower()
            for key, ban in self.banned_ips.items():
                names = ([ban["name"]] if ban.get("name") else []) + list(self.ip_names.get(key, []))
                if any(n.lower() == lowered for n in names):
                    return key
                if len(lowered) >= 6 and (ban.get("fp") or "").startswith(lowered):
                    return key
        return None

    def find_device(self, token: str):
        """A name (connected now, or seen joining this session) or an address -> (ip, fingerprint, name), else None."""
        lowered = token.lower()
        sock = self.find_socket_by_name(token)
        if sock is not None:
            info = self.get_info(sock)
            return info.get("ip"), info.get("fingerprint"), info.get("name", token)
        with self.lock:
            seen = self.known_devices.get(lowered)
            if seen:
                return seen["ip"], seen.get("fp"), seen["name"]
            if token in self.ip_names:
                names = self.ip_names[token]
                return token, next((d["fp"] for d in self.known_devices.values() if d["ip"] == token and d.get("fp")), None), (names[-1] if names else None)
        if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", token):
            return token, None, None
        return None

    # ---- moderation history ----

    def record_mod(self, kind: str, target: str, by: str, reason: str = "", ip: str = None, detail: str = "", until: float = None):
        with self.lock:
            self.mod_log.append({"time": time.time(), "kind": kind, "target": target, "by": by,
                                 "reason": reason, "ip": ip, "detail": detail, "until": until})
            del self.mod_log[:-500]

    def history_text(self, who: str = None, limit: int = 25) -> str:
        with self.lock:
            entries = list(self.mod_log)
            ip_names = {ip: list(names) for ip, names in self.ip_names.items()}
            warn_log = dict(self.warn_log)
        header = "Moderation history (this session)"
        if who:
            w = who.lower()
            ips = {ip for ip, names in ip_names.items() if any(n.lower() == w for n in names)} | {who}
            entries = [e for e in entries if e["target"].lower() == w or (e["ip"] and e["ip"] in ips)]
            issued = [r for (n, _), r in warn_log.items() if n == w]
            header = f"Moderation history for {who} (this session)"
            if issued:
                active = sum(1 for r in issued if not r.get("deleted"))
                header += f" — {len(issued)} warning{'s' if len(issued) != 1 else ''} issued, {active} active"
        if not entries:
            return f"{header}: nothing recorded."
        lines = [header + ":"]
        if len(entries) > limit:
            lines.append(f"  (showing the latest {limit} of {len(entries)})")
            entries = entries[-limit:]
        for e in entries:
            who_part = "" if who else f"{e['target']}  "
            detail = f" {e['detail']}" if e["detail"] else ""
            if e.get("until") is not None:
                detail += f" until {until_token(e['until'])}"
            reason = f": {e['reason']}" if e["reason"] else ""
            lines.append(f"  {ago_token(e['time'])}  {who_part}{e['kind'].upper()}{detail}  (by {e['by']}){reason}")
        return "\n".join(lines)

    # ---- replies ----

    def make_reply(self, msg_id: str, replier: str, target_id: str):
        """Checks that `replier` wrote `msg_id` and that `target_id` is a public message, and
        returns what clients need to draw the quote (or None). The text quoted is the host's own
        record, never what the replier's app claims it was."""
        with self.lock:
            mine, target = self.messages.get(msg_id), self.messages.get(target_id)
        if mine is None or mine["author"].lower() != replier.lower() or mine.get("to"):
            return None
        if target is None or target.get("to"):
            return None  # whispers can't be quoted, and the message may have been deleted
        snippet = f"[attachment] {target['text']}" if target.get("kind") == "file" else target["text"]
        return {"msg_id": msg_id, "to": target_id, "author": target["author"], "snippet": " ".join(snippet.split())[:80]}

    def broadcast_reply(self, payload: dict, exclude_sock=None):
        self.broadcast_feature(FEATURE_REPLY, f"{REPLY_PREFIX}{payload['msg_id']}|{payload['to']}|{payload['author']}|{payload['snippet']}", exclude_sock)

    # ---- reports ----

    def admin_broadcast(self, text: str):
        """A line for the whole admin channel: the host's screen plus every admin."""
        self.on_admin_log(text)
        frame = encode_frame(self.fernet, ADMIN_LOG_PREFIX + text)
        with self.lock:
            targets = [s for s, info in self.clients.items() if info["ready"] and info["name"].lower() in self.admins]
        for s in targets:
            self._send_frame(s, frame)

    def report_message(self, msg_id: str, reporter: str, reason: str):
        """-> (error or None, confirmation text). Public messages and attachments go to the whole
        admin channel; a whisper (which only its recipient may report) goes to the host alone."""
        reason = " ".join(reason.split())[:200] or "no reason given"
        now = time.time()
        with self.lock:
            record = self.messages.get(msg_id)
            if record is None:
                return "That message can't be reported any more.", ""
            if record["author"].lower() == reporter.lower():
                return "You can't report your own message.", ""
            to = record.get("to")
            if to is not None and to.lower() != reporter.lower():
                return "You can only report whispers that were sent to you.", ""
            if (reporter.lower(), msg_id) in self.reports:
                return "You've already reported that.", ""
            recent = [t for t in self.report_times.get(reporter.lower(), []) if now - t < 60]
            if len(recent) >= 5:
                return "You're sending a lot of reports — please wait a minute.", ""
            self.report_times[reporter.lower()] = recent + [now]
            self.reports.add((reporter.lower(), msg_id))
            author, text, kind = record["author"], record["text"], record.get("kind")
        what = f'attachment "{_clip(text)}"' if kind == "file" else f'message "{_clip(text)}"'
        if to is None:
            self.admin_broadcast(f"🚩 [Report] {reporter} reported {author}'s {what} — reason: {reason}")
            return None, "Thanks — your report was sent to the admins."
        self.on_admin_log(f"🚩 [Whisper Report — host only] {reporter} reported a whisper from {author}: {what} — reason: {reason}")
        return None, "Thanks — your report was sent to the host."

    # ---- nicknames ----

    MAX_SELF_RENAMES = 2

    def rename(self, old: str, new: str, by: str):
        """Changes `old`'s nickname to `new`; `by` is whoever asked. Anyone may rename
        themselves up to MAX_SELF_RENAMES times per chat; the host may rename anyone (that
        doesn't use up their changes, but locks them out of changing it back). Returns an
        error message, or None on success."""
        error = nickname_error(new)
        if error:
            return error
        old_key, new_key = old.lower(), new.lower()
        self_rename = by.lower() == old_key
        with self.lock:
            self._purge_expired()
            if new_key != old_key and (new_key == self.host_name.lower() or new_key in self.ghost_mutes
                                       or any(i["name"].lower() == new_key for i in self.clients.values())):
                return "That nickname is already taken."
            is_host = self.is_host(old)
            if is_host:
                state, canonical_old = self.host_nick, self.host_name
            else:
                sock = next((s for s, i in self.clients.items() if i["name"].lower() == old_key), None)
                if sock is None:
                    return f"No one named '{old}' is connected."
                state, canonical_old = self.clients[sock], self.clients[sock]["name"]
            if self_rename:
                if state["nick_locked"]:
                    return "Your nickname was changed by the host, so it can't be changed again."
                if state["nick_changes"] >= self.MAX_SELF_RENAMES:
                    return f"You've already changed your nickname {self.MAX_SELF_RENAMES} times in this chat."
                state["nick_changes"] += 1
            else:
                state["nick_locked"] = True  # a host rename sticks
            if is_host: self.host_name = new
            else: state["name"] = new

            # Everything keyed by name follows the person.
            for table in (self.colors, self.gradient_users, self.last_dnd_announce, self.last_msg_time, self.warnings):
                if old_key in table:
                    table[new_key] = table.pop(old_key)
            for group in (self.admins, self.color_changed_once, self.dnd):
                if old_key in group:
                    group.discard(old_key)
                    group.add(new_key)
            self.typing.pop(canonical_old, None)
            for board in self.boards.values():
                entry = board.pop(old_key, None)
                if entry is not None:
                    entry["name"] = new
                    board[new_key] = entry
            for key in [k for k in self.warn_log if k[0] == old_key]:
                self.warn_log[(new_key, key[1])] = self.warn_log.pop(key)
            for record in self.messages.values():  # so they can still edit/delete what they wrote
                if record["author"].lower() == old_key: record["author"] = new
                if record.get("to") and record["to"].lower() == old_key: record["to"] = new
            for transfer in self.transfers.values():
                if transfer["to"] and transfer["to"].lower() == old_key: transfer["to"] = new

        self.broadcast(f"{RENAME_PREFIX}{canonical_old}|{new}|{by}")
        self.broadcast_colormap()
        self._emit("rename", {"old": canonical_old, "new": new, "by": by})
        if self_rename:
            left = self.MAX_SELF_RENAMES - state["nick_changes"]
            note = (f"You have {left} nickname change{'s' if left != 1 else ''} left in this chat."
                    if left > 0 else "That was your last nickname change in this chat.")
            if is_host: self._emit("system", note)
            else: self.send_private(sock, NOTICE_PREFIX + note)
        return None

    def warn(self, name: str, by: str, reason: str):
        """Sends `name` a formal warning (with a running count). Returns an error or None."""
        if self.is_host(name):
            return "You cannot warn the host."
        sock = self.find_socket_by_name(name)
        if sock is None:
            return f"No one named '{name}' is connected."
        canonical = self.get_info(sock).get("name", name)
        reason = " ".join(reason.split())[:300] or "no reason given"
        with self.lock:
            count = self.warnings[canonical.lower()] = self.warnings.get(canonical.lower(), 0) + 1
            self.warn_log[(canonical.lower(), count)] = {"name": canonical, "by": by, "reason": reason, "appealed": False, "deleted": False, "time": time.time()}
        self.record_mod("warn", canonical, by, reason, detail=f"#{count}")
        self.send_private(sock, f"{WARN_PREFIX}{by}|{count}|{reason}")
        self.broadcast(f"* {canonical} has been warned *", exclude_sock=sock)
        self.log_admin_action(by, f"warned {canonical} (warning #{count}). Reason: {reason}")
        return None

    # ---- minigame leaderboards (Snake, Flappy Bird) ----

    @staticmethod
    def _game_wire(game: str, entry: dict) -> str:
        return f"{GAME_PREFIXES[game]}{entry['name']}|{entry['best']}|{entry['score']}|{1 if entry['playing'] else 0}"

    def update_game(self, game: str, name: str, score, playing: bool, exclude_sock=None, emit: bool = False):
        """Records a player's current score (their best is the max seen this session) and tells
        everyone else — for Flappy Bird, only the clients that understand its frames."""
        board = self.boards.get(game)
        if board is None: return None
        try: score = max(0, min(int(score), 100_000))
        except (TypeError, ValueError): return None
        with self.lock:
            entry = board.setdefault(name.lower(), {"name": name, "best": 0, "score": 0, "playing": False})
            entry.update(name=name, score=score, playing=bool(playing))
            entry["best"] = max(entry["best"], score)
            snapshot = dict(entry)
        wire = self._game_wire(game, snapshot)
        if feature := GAME_FEATURES.get(game):
            self.broadcast_feature(feature, wire, exclude_sock)
        else:
            self.broadcast(wire, exclude_sock=exclude_sock)
        if emit:
            self._emit("game", {"game": game, "entry": snapshot})
        return snapshot

    def game_entries(self, game: str) -> list:
        with self.lock:
            return [dict(e) for e in self.boards.get(game, {}).values()]

    def game_player_left(self, name: str):
        for game, board in self.boards.items():
            with self.lock:
                entry = board.get(name.lower())
                still_playing = bool(entry and entry["playing"])
                score = entry["score"] if entry else 0
            if still_playing:
                self.update_game(game, name, score, False, emit=True)

    # ---- whispers ----

    def resolve_whisper_target(self, sender: str, target_name: str):
        """-> (canonical name, None) or (None, error message for the sender)."""
        if target_name.lower() == sender.lower():
            return None, "You cannot whisper to yourself!"
        if self.is_host(target_name):
            return self.host_name, None
        sock = self.find_socket_by_name(target_name)
        if sock is None:
            return None, f"No one named '{target_name}' is connected."
        return self.get_info(sock).get("name", target_name), None

    def whisper(self, msg_id: str, sender: str, target_name: str, text: str):
        """Delivers a private message to `target_name` and echoes it to the sender (so
        the sender sees exactly what was delivered). Returns an error or None."""
        text = text.strip()
        if not text:
            return "Usage: /whisper <name> <message>"
        if len(text) > MAX_MESSAGE_CHARS:
            return f"That whisper is too long (the limit is {MAX_MESSAGE_CHARS:,} characters)."
        target, error = self.resolve_whisper_target(sender, target_name)
        if error:
            return error
        if not self.record_message(msg_id, sender, text, kind="whisper", to=target):
            return "Couldn't send that whisper."
        payload = {"msg_id": msg_id, "from": sender, "to": target, "text": text}
        wire = f"{WHISPER_PREFIX}{msg_id}|{sender}|{target}|{text}"
        for name in (target, sender):  # recipient first, then the sender's own copy
            if self.is_host(name):
                self._emit("whisper", payload)
            elif (sock := self.find_socket_by_name(name)) is not None:
                self.send_private(sock, wire)
        return None

    def set_features(self, sock, features):
        with self.lock:
            if sock in self.clients:
                self.clients[sock]["features"] = set(features)

    def broadcast_feature(self, feature: str, text: str, exclude_sock=None):
        """Like broadcast(), but only to clients that announced `feature` — so older
        versions never receive protocol text they'd display as a chat line."""
        frame = encode_frame(self.fernet, text)
        with self.lock:
            targets = [s for s, info in self.clients.items() if info["ready"] and s is not exclude_sock and feature in info.get("features", ())]
        for s in targets:
            self._send_frame(s, frame)

    def log_host_only(self, actor: str, text: str):
        """A log line only the host sees — deliberately NOT sent to admins, unlike
        log_admin_action. Used for changes to whispers."""
        self.on_admin_log(f"🛡️ [Host Log] {actor} {text}")

    # ---- do-not-disturb ----

    def set_dnd(self, name, active):
        """Returns True if the change should be announced (rate-limited)."""
        now = time.time()
        key = name.lower()
        with self.lock:
            if active: self.dnd.add(key)
            else: self.dnd.discard(key)
            if (now - self.last_dnd_announce.get(key, 0)) < DND_ANNOUNCE_COOLDOWN:
                return False
            self.last_dnd_announce[key] = now
            return True

    def is_dnd(self, name):
        with self.lock:
            return name.lower() in self.dnd

    # ---- client table ----

    def add_client(self, sock, name, ip):
        outbox = Outbox(sock, on_failed=lambda: self.disconnect(sock))  # a peer we can't write to is dropped
        with self.lock:
            self.outboxes[sock] = outbox
            names = self.ip_names.setdefault(ip, [])
            if name not in names: names.append(name)
            self.known_devices[name.lower()] = {"name": name, "ip": ip, "fp": None}
            self.clients[sock] = {
                "name": name, "ip": ip, "muted_until": 0.0,
                "muted_by": None, "mute_reason": None, "kicked": False,
                "features": set(),
                "ready": False,  # becomes True once the roster has gone out — see mark_ready()
                "nick_changes": 0, "nick_locked": False,
            }

    def mark_ready(self, sock):
        """A joining client must receive the roster before anything else (its handshake
        rejects any other first reply), so broadcasts skip it until this is called."""
        with self.lock:
            if sock in self.clients:
                self.clients[sock]["ready"] = True

    def remove_client(self, sock):
        with self.lock:
            outbox = self.outboxes.pop(sock, None)
            info = self.clients.pop(sock, None)
            if info and time.time() < info["muted_until"]:
                self.ghost_mutes[info["name"].lower()] = {
                    "name": info["name"], "ip": info.get("ip"),
                    "muted_until": info["muted_until"],
                    "muted_by": info["muted_by"], "mute_reason": info["mute_reason"],
                }
        if outbox is not None:
            outbox.close()
        return info

    def names(self):
        with self.lock:
            return [info["name"] for info in self.clients.values()]

    def get_info(self, sock):
        with self.lock:
            return dict(self.clients.get(sock, {}))

    def set_fingerprint(self, sock, fingerprint: str):
        with self.lock:
            if sock in self.clients:
                self.clients[sock]["fingerprint"] = fingerprint
                seen = self.known_devices.get(self.clients[sock]["name"].lower())
                if seen: seen["fp"] = fingerprint

    def _find_socket(self, predicate):
        with self.lock:
            return next((s for s, info in self.clients.items() if predicate(info)), None)

    def find_socket_by_name(self, name):
        lowered = name.lower()
        return self._find_socket(lambda info: info["name"].lower() == lowered)

    def find_socket_by_ip(self, ip):
        return self._find_socket(lambda info: info.get("ip") == ip)

    def claim_name(self, name: str, ip: str):
        """Decides whether `ip` may join as `name`. Returns an error message, or None.

        The same device reconnecting under its own name replaces its old session
        (which is often a dead connection the host hasn't noticed yet — that's what
        used to make rejoining fail with "Nickname already in use"). A name held by a
        different address stays taken, and so does the name of a muted user who left
        (so a mute can't be shed by switching to someone else's name)."""
        lowered = name.lower()
        with self.lock:
            self._purge_expired()
            stale = next((s for s, info in self.clients.items() if info["name"].lower() == lowered), None)
            if stale is None:
                ghost = self.ghost_mutes.get(lowered)
                if ghost and ghost.get("ip") != ip:
                    return "That nickname is reserved while its mute is active."
                return None
            if self.clients[stale].get("ip") != ip:
                return "Nickname already in use."
            self.clients[stale]["kicked"] = True  # its handler then exits quietly

        self.send_private(stale, KICK_NOTICE_PREFIX + "the server|you signed in again from this device")
        box = self.outboxes.get(stale)
        if box is not None:
            box.close(after_control=True)
        for attempt in range(2):
            deadline = time.time() + (0.5 if attempt == 0 else 1.5)
            while time.time() < deadline and self.find_socket_by_name(name):
                time.sleep(0.02)
            if not self.find_socket_by_name(name):
                return None
            self.disconnect(stale)  # didn't leave politely (dead connection) — cut it
        return "Nickname already in use."

    def _purge_expired(self):
        """Caller must hold self.lock."""
        now = time.time()
        for k in [k for k, v in self.ghost_mutes.items() if now >= v["muted_until"]]:
            del self.ghost_mutes[k]
        expired = [ip for ip, info in self.banned_ips.items() if now >= info["until"]]
        for ip in expired:
            del self.banned_ips[ip]
        if expired:
            self._save_bans()

    # ---- bans ----

    def is_ip_banned(self, ip, fp=None):
        return self.get_ban_info(ip, fp) is not None

    def _find_ban_key(self, ip, fp=None):
        """Caller holds the lock (and has purged). A ban applies to a device if it's at the banned address OR has the
        banned device fingerprint. Address alone isn't enough on networks that hand out new addresses, and the
        fingerprint alone isn't enough when it can't be read (older versions) — so either one counts."""
        if ip in self.banned_ips:
            return ip
        if fp:
            for key, ban in self.banned_ips.items():
                if ban.get("fp") and ban["fp"] == fp:
                    return key
        return None

    def get_ban_info(self, ip, fp=None):
        with self.lock:
            self._purge_expired()
            key = self._find_ban_key(ip, fp)
            return dict(self.banned_ips[key], key=key) if key is not None else None

    def ban_ip(self, ip, until, by, reason, fp=None, name=None):
        """Bans an address (and, when known, the device fingerprint and name seen with it). Kept on disk."""
        with self.lock:
            old = self.banned_ips.get(ip, {})
            self.banned_ips[ip] = {"until": until, "banned_by": by, "reason": reason, "fp": fp or old.get("fp"),
                                   "name": name or old.get("name"), "created": time.time()}
            self.unbans = {k: v for k, v in self.unbans.items() if k != ip and not (fp and v.get("fp") == fp)}  # a fresh ban cancels any earlier "you were unbanned" note
            self._save_bans()

    def unban_ip(self, ip, by: str = "", reason: str = "", log: bool = True):
        """Lifts a ban and remembers who and why, so the banned person's app can be told."""
        reason = " ".join(reason.split())[:300] or "no reason given"
        with self.lock:
            ban = self.banned_ips.pop(ip, None)
            if ban is None:
                return False
            self.unbans[ip] = {"by": by or "the host", "reason": reason, "time": time.time(), "ip": ip, "fp": ban.get("fp")}
            names = [ban["name"]] if ban.get("name") else list(self.ip_names.get(ip, []))
            self._save_bans()
        if log:
            self.record_mod("unban", names[-1] if names else f"IP {ip}", by or "the host", reason, ip=ip)
        return True

    def ban_label(self, key) -> str:
        """Who a ban is for, in words: the name we know them by, else the address."""
        with self.lock:
            ban = self.banned_ips.get(key, {})
            names = [ban["name"]] if ban.get("name") else list(self.ip_names.get(key, []))
        return names[-1] if names else f"IP {key}"

    def bans_list(self) -> list:
        """Active bans, oldest first, as (key, record) — the numbering /bans shows and /unban # accepts."""
        with self.lock:
            self._purge_expired()
            return sorted(((k, dict(v)) for k, v in self.banned_ips.items()), key=lambda kv: kv[1].get("created", 0))

    def bans_text(self) -> str:
        entries = self.bans_list()
        if not entries:
            return "No one is banned."
        lines = [f"Active bans ({len(entries)}):"]
        for n, (key, ban) in enumerate(entries, 1):
            who = ban.get("name") or next(iter(self.ip_names.get(key, [])), None)
            device = f" · device {ban['fp'][:8]}" if ban.get("fp") else ""
            when = f", {ago_token(ban['created'])}" if ban.get("created") else ""
            lines.append(f"  #{n}  {who + '  ' if who else ''}({key}{device}) — until {until_token(ban['until'])}"
                         f"  (by {ban.get('banned_by', '?')}{when}): {ban.get('reason') or 'no reason given'}")
        lines.append("Lift one with /unban <#, name or IP> [reason].")
        return "\n".join(lines)

    # ---- the ban list on disk ----

    def _load_bans(self):
        for rec in load_json(BANS_FILE, dict).get("bans", []):
            try:
                ip = str(rec["ip"])
                until = float("inf") if rec.get("until") is None else float(rec["until"])
                if time.time() >= until:
                    continue
                self.banned_ips[ip] = {"until": until, "banned_by": str(rec.get("banned_by", "the host")), "reason": str(rec.get("reason", "")),
                                       "fp": rec.get("fp") or None, "name": rec.get("name") or None, "created": float(rec.get("created", 0)),
                                       **({"appealed": True} if rec.get("appealed") else {})}
            except (KeyError, TypeError, ValueError):
                continue

    def _save_bans(self):
        """Caller holds the lock. Written every time the list changes, so a crash or a restart never loses a ban."""
        bans = []
        for ip, ban in self.banned_ips.items():
            rec = {"ip": ip, "until": None if ban["until"] == float("inf") else ban["until"], "banned_by": ban.get("banned_by"),
                   "reason": ban.get("reason"), "fp": ban.get("fp"), "name": ban.get("name"), "created": ban.get("created", 0)}
            if ban.get("appealed"): rec["appealed"] = True
            bans.append(rec)
        save_json(BANS_FILE, {"version": 1, "bans": bans}, indent=1)

    # ---- mutes / slowmode ----

    def apply_ghost_ip_mute(self, sock, ip):
        """Re-applies a still-running mute if the same IP reconnects under a new name."""
        with self.lock:
            self._purge_expired()
            now = time.time()
            for g_info in self.ghost_mutes.values():
                if g_info.get("ip") == ip and now < g_info["muted_until"]:
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
            if sock not in self.clients: return False
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
            self._purge_expired()
            if self.ghost_mutes.pop(name.lower(), None) is not None:
                found = True
        return found

    def check_slowmode(self, name, is_admin) -> float:
        """Seconds the sender still has to wait (0.0 = free to send, and the
        send is stamped). Admins and slowmode-off always return 0.0."""
        if self.slowmode_delay <= 0 or is_admin:
            return 0.0
        now, key = time.time(), name.lower()
        with self.lock:
            remaining = self.slowmode_delay - (now - self.last_msg_time.get(key, 0.0))
            if remaining > 0:
                return remaining
            self.last_msg_time[key] = now
        return 0.0

    # ---- typing ----

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

    # ---- sending / removing ----

    def mark_kicked(self, sock):
        with self.lock:
            if sock in self.clients:
                self.clients[sock]["kicked"] = True

    def broadcast(self, text, exclude_sock=None):
        frame = encode_frame(self.fernet, text)  # encrypted once, shared by every recipient
        with self.lock: targets = [s for s, info in self.clients.items() if s is not exclude_sock and info["ready"]]
        for s in targets:
            self._send_frame(s, frame)

    def send_private(self, sock, text, on_sent=None) -> bool:
        return self._send_frame(sock, encode_frame(self.fernet, text), on_sent)

    def _send_frame(self, sock, frame: bytes, on_sent=None, bulk: bool = False) -> bool:
        outbox = self.outboxes.get(sock)
        if outbox is not None:
            return outbox.put(frame, on_sent, bulk)
        try:  # not a registered client (yet) — e.g. replying during the handshake
            sock.sendall(frame)
            ok = True
        except OSError:
            ok = False
        if on_sent is not None:
            on_sent(ok)
        return ok

    # ---- file transfers ----

    def transfer_targets(self, to, exclude_sock=None, skipped=None) -> list:
        """Sockets a transfer's frames go to: everyone (to=None) or one person — only those whose
        app understands chunked files, and not anyone already skipped for this transfer. The host's
        own copy is handled separately via local_files."""
        skipped = skipped or ()
        with self.lock:
            if to is None:
                pool = [(s, info) for s, info in self.clients.items() if info["ready"]]
            elif self.is_host(to):
                return []
            else:
                pool = [(s, info) for s, info in self.clients.items() if info["name"].lower() == to.lower()]
            return [s for s, info in pool if s is not exclude_sock and s not in skipped and FEATURE_FILES in info["features"]]

    def legacy_targets(self, to, exclude_sock=None) -> list:
        """Recipients whose app is too old for chunked files (they get a one-line notice instead)."""
        with self.lock:
            if to is None:
                pool = [(s, info) for s, info in self.clients.items() if info["ready"]]
            elif self.is_host(to):
                return []
            else:
                pool = [(s, info) for s, info in self.clients.items() if info["name"].lower() == to.lower()]
            return [s for s, info in pool if s is not exclude_sock and FEATURE_FILES not in info["features"]]

    def announce_unreceivable(self, sender: str, filename: str, size: int, to=None, exclude_sock=None):
        for s in self.legacy_targets(to, exclude_sock):
            self.send_private(s, NOTICE_PREFIX + f"{sender} shared {filename} ({format_size(size)}), but your version can't receive files — please update chat_gui.")

    def relay_frame(self, frame: bytes, targets: list, cancel=None, skipped=None, abort_frame: bytes = None):
        """Queue a transfer frame for each target, then wait for their queues to drain below
        the window. That paces the sender to the slowest recipient without ever buffering a
        whole file. A recipient who can't keep up for TRANSFER_STALL_SECONDS is skipped for
        the rest of *this file* (they're sent `abort_frame`, and stay connected) — a slow
        connection must never get someone kicked from the room."""
        for s in targets:
            self._send_frame(s, frame, bulk=True)
        for s in targets:
            box = self.outboxes.get(s)
            if box is None:
                continue
            waited = 0.0
            while not box.wait_below(TRANSFER_WINDOW_BYTES, 0.5):
                if box.closed:
                    break
                if cancel is not None and cancel.is_set():
                    return
                waited += 0.5
                if waited >= TRANSFER_STALL_SECONDS:
                    if skipped is not None:
                        skipped.add(s)
                    if abort_frame is not None:
                        self._send_frame(s, abort_frame, bulk=True)
                    break

    def abort_transfer(self, msg_id: str, reason: str = "", notify_author: bool = True):
        with self.lock:
            tr = self.transfers.pop(msg_id, None)
            self.messages.pop(msg_id, None)
        if tr is None:
            return
        frame = encode_frame(self.fernet, f"{FILEABORT_PREFIX}{msg_id}|{reason}")
        self.relay_frame(frame, self.transfer_targets(tr["to"], exclude_sock=tr["sock"], skipped=tr["skipped"]))
        if tr["local"] and self.local_files is not None:
            info = self.local_files.abort(msg_id)
            if info is not None and reason:
                self._emit("system", abort_message(info, reason))
        if reason and notify_author:
            self.send_private(tr["sock"], NOTICE_PREFIX + f"Sending {tr['filename']} failed: {reason}")

    def abort_transfers_of(self, sock):
        """The sender went away mid-transfer: tell everyone to discard the partial file."""
        for msg_id in [m for m, tr in list(self.transfers.items()) if tr["sock"] is sock]:
            self.abort_transfer(msg_id, "the sender disconnected", notify_author=False)

    def disconnect(self, sock):
        # shutdown() first: closing a socket from another thread does not wake a
        # thread blocked in recv() on it, which would leave a ghost session behind.
        try: sock.shutdown(socket.SHUT_RDWR)
        except OSError: pass
        try: sock.close()
        except OSError: pass

    def eject(self, sock, notice: str, announcement: str):
        """Tell `sock` why it's leaving, flag it so its handler skips the usual
        'disconnected' chatter, announce to everyone else, then close it."""
        self.send_private(sock, notice)
        self.mark_kicked(sock)
        self.broadcast(announcement, exclude_sock=sock)
        outbox = self.outboxes.get(sock)
        if outbox is not None:
            outbox.close(after_control=True)  # lets the notice out first, then hangs up
        else:
            self.disconnect(sock)

    def shutdown_all(self, timeout: float = 0.5):
        """Room closing: let each client's pending small frames (the host-disconnect
        notice) go out, then hang up on everyone."""
        with self.lock:
            sockets, outboxes = list(self.clients), list(self.outboxes.values())
        for box in outboxes:
            box.close(after_control=True)
        deadline = time.time() + timeout
        for box in outboxes:
            box.join(max(0.0, deadline - time.time()))
        for s in sockets:
            self.disconnect(s)


def _clip(text: str, limit: int = 200) -> str:
    return text if len(text) <= limit else text[:limit - 1] + "…"


# ---- Files ----

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
THUMB_SIZE = (260, 260)

# Sizes are shown in the units this computer's file manager uses, so a file reads the same in
# the chat as it does on disk: Windows Explorer counts in 1024s, macOS Finder (and most Linux
# file managers) in 1000s. (A 350 MB file in Finder is 333 "MB" by Explorer's maths.)
SIZE_BASE = 1024 if sys.platform == "win32" else 1000
FILE_LIMIT_TEXT = "1 GB"

def format_size(n: int) -> str:
    for unit, power in (("GB", 3), ("MB", 2), ("KB", 1)):
        factor = SIZE_BASE ** power
        if n >= factor:
            return f"{n / factor:.1f} {unit}"
    return f"{n} B"

def check_file_size(filepath: str):
    size = os.path.getsize(filepath)
    if size > MAX_FILE_BYTES:
        raise ValueError(f"File is {format_size(size)} — the limit is {FILE_LIMIT_TEXT}.")

def make_thumbnail(filename: str, data: bytes):
    """Decodes + shrinks an image in whatever thread calls this (the network
    thread, normally) so the UI thread only has to wrap the small result."""
    if Image is None or not filename.lower().endswith(IMAGE_EXTENSIONS):
        return None
    try:
        img = Image.open(io.BytesIO(data))
        img.thumbnail(THUMB_SIZE)
        img.load()
        return img
    except Exception:
        return None

def encode_file_start(sender: str, msg_id: str, to: str, filename: str, size: int) -> str:
    """`to` is the whisper recipient, or "" to send to everyone."""
    return FILE_PREFIX + "|".join((sender, msg_id, to, filename.replace("|", "_"), str(size)))

def parse_file_start(text: str):
    """-> {"sender", "msg_id", "to", "filename", "size"}, or None if it's malformed."""
    try:
        sender, msg_id, to, filename, size = text[len(FILE_PREFIX):].split("|", 4)
        size = int(size)
    except ValueError:
        return None
    if size < 0 or not msg_id:
        return None
    return {"sender": sender, "msg_id": msg_id, "to": to, "filename": os.path.basename(filename) or "unnamed_file", "size": size}

def iter_file_texts(sender: str, msg_id: str, to: str, filename: str, size: int, chunks):
    """The wire messages for one file: START, one per chunk, END."""
    yield encode_file_start(sender, msg_id, to, filename, size)
    for index, chunk in enumerate(chunks):
        yield f"{FILECHUNK_PREFIX}{msg_id}|{index}|{base64.b64encode(chunk).decode('ascii')}"
    yield FILEEND_PREFIX + msg_id

def chunks_from_bytes(data: bytes):
    view = memoryview(data)
    for offset in range(0, len(data), FILE_CHUNK_BYTES):
        yield view[offset:offset + FILE_CHUNK_BYTES]

def chunks_from_path(path: str):
    with open(path, "rb") as f:
        while chunk := f.read(FILE_CHUNK_BYTES):
            yield chunk

def with_progress(chunks, size: int, on_progress):
    sent = 0
    for chunk in chunks:
        sent += len(chunk)
        if on_progress is not None:
            on_progress(sent, size)
        yield chunk

def local_file_event(sender, msg_id, to, filename, size, data=None, path=None) -> dict:
    """The event for showing a file we sent ourselves (the host never echoes it back)."""
    return {"sender": sender, "msg_id": msg_id, "to": to, "filename": filename, "size": size,
            "data": data, "path": path, "temp": False,
            "thumb": make_thumbnail(filename, data) if data is not None else None}


class BannedError(PermissionError):
    """The host refused us because we're banned (carries what the appeal form needs to show)."""
    def __init__(self, message: str, until_str: str, reason: str):
        super().__init__(message)
        self.until_str, self.reason = until_str, reason


class UploadCancelled(Exception):
    """Raised inside a send loop when the user presses Cancel."""


def abort_message(info: dict, reason: str) -> str:
    """What to tell the user when a transfer they were receiving ends early."""
    if reason.startswith("cancelled"):
        return f"{info['sender']} cancelled sending {info['filename']}."
    return f"{info['filename']} from {info['sender']} didn't finish: {reason or 'the transfer was interrupted'}."


class FileAssembler:
    """Receives file transfers (START / CHUNK / END frames) for one client and turns them
    into "file" events. Files up to INLINE_FILE_BYTES are assembled in memory; bigger ones
    are written to a temp file as they arrive, so a 1 GB file never has to fit in RAM."""

    PROGRESS_MIN_BYTES = 2 * 1024 * 1024  # don't bother reporting progress for small files
    PROGRESS_STEP = 0.02

    def __init__(self, event_queue: queue.Queue):
        self.event_queue = event_queue
        self._lock = threading.Lock()
        self._transfers = {}
        self._dir = None

    def _say(self, text: str):
        self.event_queue.put(("system", text))

    def start(self, info: dict) -> bool:
        size, name = info["size"], info["filename"]
        if not 0 <= size <= MAX_FILE_BYTES:
            self._say(f"Ignored {name}: it's larger than the {FILE_LIMIT_TEXT} limit.")
            return False
        with self._lock:
            previous = self._transfers.pop(info["msg_id"], None)
        if previous is not None:  # same id again: drop the old half-received copy rather than leak its file
            self._discard(previous)
        state = {"info": info, "size": size, "got": 0, "next": 0, "buf": None, "fh": None, "path": None, "last_pct": -1.0}
        if size <= INLINE_FILE_BYTES:
            state["buf"] = bytearray()
        else:
            try:
                if self._dir is None:
                    self._dir = tempfile.mkdtemp(prefix="chat_gui_files_")
                if shutil.disk_usage(self._dir).free < size + 64 * 1024 * 1024:
                    raise OSError("not enough free disk space")
                safe_id = re.sub(r"[^0-9A-Za-z_-]", "_", info["msg_id"])[:32]
                state["path"] = os.path.join(self._dir, safe_id + ".part")
                state["fh"] = open(state["path"], "wb")
            except OSError as e:
                self._say(f"Can't receive {name}: {e}")
                return False
        with self._lock:
            self._transfers[info["msg_id"]] = state
        self._progress(state, force=True)
        return True

    def chunk(self, msg_id: str, index: int, b64: str):
        with self._lock:
            state = self._transfers.get(msg_id)
        if state is None:
            return
        try:
            if index != state["next"]:
                raise ValueError("chunks arrived out of order")
            raw = base64.b64decode(b64)
            state["got"] += len(raw)
            if state["got"] > state["size"]:
                raise ValueError("more data than announced")
            if state["buf"] is not None: state["buf"] += raw
            else: state["fh"].write(raw)
            state["next"] += 1
        except (ValueError, OSError) as e:
            self.abort(msg_id)
            self._say(f"Receiving {state['info']['filename']} failed: {e}")
            return
        self._progress(state)

    def finish(self, msg_id: str):
        with self._lock:
            state = self._transfers.pop(msg_id, None)
        if state is None:
            return
        info = state["info"]
        if state["got"] != state["size"]:
            self._discard(state)
            self._say(f"Receiving {info['filename']} failed: the file arrived incomplete.")
            return
        event = dict(info, data=None, path=None, temp=False, thumb=None)
        if state["buf"] is not None:
            event["data"] = bytes(state["buf"])
            event["thumb"] = make_thumbnail(info["filename"], event["data"])
        else:
            state["fh"].close()
            event["path"], event["temp"] = state["path"], True
        self._done(info)
        self.event_queue.put(("file", event))

    def abort(self, msg_id: str):
        """Discards a half-received file. Returns its info (None if we weren't receiving it)."""
        with self._lock:
            state = self._transfers.pop(msg_id, None)
        if state is None:
            return None
        self._discard(state)
        self._done(state["info"])
        return state["info"]

    def _discard(self, state: dict):
        if state["fh"] is not None:
            try: state["fh"].close()
            except OSError: pass
        if state["path"]:
            try: os.remove(state["path"])
            except OSError: pass

    def _progress(self, state: dict, force: bool = False):
        if state["size"] < self.PROGRESS_MIN_BYTES:
            return
        pct = state["got"] / state["size"]
        if force or pct - state["last_pct"] >= self.PROGRESS_STEP:
            state["last_pct"] = pct
            info = state["info"]
            self.event_queue.put(("transfer_progress", {"msg_id": info["msg_id"], "filename": info["filename"], "sender": info["sender"], "pct": pct, "done": False}))

    def _done(self, info: dict):
        if info["size"] >= self.PROGRESS_MIN_BYTES:
            self.event_queue.put(("transfer_progress", {"msg_id": info["msg_id"], "done": True}))

    def close(self):
        with self._lock:
            states, self._transfers = list(self._transfers.values()), {}
        for state in states:
            self._discard(state)
        if self._dir is not None:
            shutil.rmtree(self._dir, ignore_errors=True)
            self._dir = None


# ---- Guest handling (runs on the host, one thread per guest) ----

UNLOCK_PREFIX_TO_SENTINEL = {prefix: sentinel for sentinel, prefix in GRADIENT_UNLOCK_CODES.values()}

def _guest_notice(hub: Hub, sock, text: str):
    hub.send_private(sock, NOTICE_PREFIX + text)

def _handle_guest_command(text, sock, guest_name, is_admin, hub: Hub, host_name, event_queue):
    cmd_name, _, arg = text[len(CMD_PREFIX):].partition("|")

    if cmd_name == "color":
        color = arg.lower()
        if guest_name.lower() in hub.color_changed_once:
            _guest_notice(hub, sock, "You can only change your color once during a chat session.")
        elif color in COLOR_PALETTE:
            hub.set_color(guest_name, COLOR_PALETTE[color], once=True)
            _guest_notice(hub, sock, f"Color changed successfully to {color}.")
            hub.broadcast_colormap()
            snapshot = hub.colormap_snapshot()
            event_queue.put(("colormap", snapshot))
            event_queue.put(("chat", {"raw": f"* {guest_name} changed their color to {color} *", "colors": snapshot}))
        else:
            _guest_notice(hub, sock, f"Invalid color. Available: {', '.join(COLOR_PALETTE)}")

    elif cmd_name == "warnings":  # anyone may ask for their own; admins can name someone else
        _guest_notice(hub, sock, warnings_report(hub, guest_name, arg, is_admin))

    elif cmd_name == "mod":
        if is_admin:
            if arg.split(" ", 1)[0].lower() in MOD_COMMAND_NAMES:  # only genuine moderation commands
                run_mod_command(arg, hub, guest_name, lambda t: _guest_notice(hub, sock, t))
        else:
            _guest_notice(hub, sock, "You do not have permission to use moderation commands.")

def _ping_from_guest(hub: Hub, sock, guest_name, host_name, raw_text, event_queue):
    route_pings(hub, guest_name, raw_text, lambda t: _guest_notice(hub, sock, t),
                on_host_ping=lambda who: event_queue.put(("ping", who)))

def _handle_guest_file(text, sock, guest_name, hub: Hub, event_queue):
    """START of a file/image/sticker from a guest: vet it, record it, and open the relay."""
    info = parse_file_start(text)
    if info is None:
        event_queue.put(("system", "[received a corrupted file, ignored]"))
        return
    if info["size"] > MAX_FILE_BYTES:
        _guest_notice(hub, sock, f"{info['filename']} is {format_size(info['size'])} — the limit is {FILE_LIMIT_TEXT}.")
        return
    target = None
    if info["to"]:
        target, error = hub.resolve_whisper_target(guest_name, info["to"])
        if error:
            _guest_notice(hub, sock, error)
            return
        if not hub.is_host(target) and hub.legacy_targets(target):
            _guest_notice(hub, sock, f"{target}'s version of chat_gui is too old to receive files — ask them to update.")
            return
    if not hub.record_message(info["msg_id"], guest_name, info["filename"], kind="file", to=target):
        return  # unusable or already-used id — never relay it
    local = target is None or hub.is_host(target)
    info.update(sender=guest_name, to=target or "")  # never trust the sender's claims about who they are
    abort_frame = encode_frame(hub.fernet, f"{FILEABORT_PREFIX}{info['msg_id']}|your connection couldn't keep up with this file")
    hub.transfers[info["msg_id"]] = {"sock": sock, "to": target, "local": local, "filename": info["filename"],
                                     "expected": info["size"], "got": 0, "next": 0, "skipped": set(), "abort_frame": abort_frame}
    if local and hub.local_files is not None:
        hub.local_files.start(info)
    hub.announce_unreceivable(guest_name, info["filename"], info["size"], target, exclude_sock=sock)
    start = encode_file_start(guest_name, info["msg_id"], target or "", info["filename"], info["size"])
    tr = hub.transfers[info["msg_id"]]
    hub.relay_frame(encode_frame(hub.fernet, start), hub.transfer_targets(target, exclude_sock=sock), skipped=tr["skipped"], abort_frame=abort_frame)

def _handle_guest_chunk(text, sock, hub: Hub):
    try:
        msg_id, index, b64 = text[len(FILECHUNK_PREFIX):].split("|", 2)
        index = int(index)
    except ValueError:
        return
    tr = hub.transfers.get(msg_id)
    if tr is None or tr["sock"] is not sock:
        return  # unknown transfer, or someone else's
    if index != tr["next"]:
        return hub.abort_transfer(msg_id, "the file's pieces arrived out of order")
    tr["next"] += 1
    tr["got"] += len(b64) // 4 * 3 - b64[-2:].count("=")
    if tr["got"] > tr["expected"]:
        return hub.abort_transfer(msg_id, "more data arrived than the file announced")
    if tr["local"] and hub.local_files is not None:
        hub.local_files.chunk(msg_id, index, b64)
    hub.relay_frame(encode_frame(hub.fernet, text), hub.transfer_targets(tr["to"], exclude_sock=sock, skipped=tr["skipped"]),
                    skipped=tr["skipped"], abort_frame=tr["abort_frame"])

def _handle_guest_file_end(text, sock, hub: Hub):
    msg_id = text[len(FILEEND_PREFIX):].strip()
    tr = hub.transfers.get(msg_id)
    if tr is None or tr["sock"] is not sock:
        return
    if tr["got"] != tr["expected"]:
        return hub.abort_transfer(msg_id, "the file arrived incomplete")
    with hub.lock:
        hub.transfers.pop(msg_id, None)
    if tr["local"] and hub.local_files is not None:
        hub.local_files.finish(msg_id)
    hub.relay_frame(encode_frame(hub.fernet, FILEEND_PREFIX + msg_id), hub.transfer_targets(tr["to"], exclude_sock=sock, skipped=tr["skipped"]),
                    skipped=tr["skipped"], abort_frame=tr["abort_frame"])

def _process_guest_message(text, sock, guest_name, hub: Hub, host_name, event_queue):
    is_admin = guest_name.lower() in hub.admins

    # Pieces of a transfer that's already underway (vetted at its START) — these keep flowing even
    # if the sender is muted mid-upload.
    if text.startswith(FILECHUNK_PREFIX):
        return _handle_guest_chunk(text, sock, hub)
    if text.startswith(FILEEND_PREFIX):
        return _handle_guest_file_end(text, sock, hub)
    if text.startswith(FILEABORT_PREFIX):
        msg_id = text[len(FILEABORT_PREFIX):].partition("|")[0]
        reason = text[len(FILEABORT_PREFIX):].partition("|")[2][:100] or "cancelled by the sender"
        tr = hub.transfers.get(msg_id)
        if tr is not None and tr["sock"] is sock:
            hub.abort_transfer(msg_id, reason if reason.startswith("cancelled") else "cancelled by the sender", notify_author=False)
        return

    if text.startswith(TYPING_START_PREFIX):
        if not hub.is_muted(sock):
            hub.mark_typing(guest_name)  # never the name the client claims — anyone could show "X is typing"
            hub.broadcast(TYPING_START_PREFIX + guest_name, exclude_sock=sock)
            event_queue.put(("typing", hub.typing_names()))
        return

    if text.startswith(TYPING_STOP_PREFIX):
        hub.mark_stopped_typing(guest_name)
        hub.broadcast(TYPING_STOP_PREFIX + guest_name, exclude_sock=sock)
        event_queue.put(("typing", hub.typing_names()))
        return

    if text.startswith(APPEAL_PREFIX):  # a warning appeal — allowed even while muted
        _handle_warning_appeal(text[len(APPEAL_PREFIX):], sock, guest_name, hub)
        return

    if text.startswith(REPORT_PREFIX):  # allowed even while muted — it's a safety tool
        msg_id, _, reason = text[len(REPORT_PREFIX):].partition("|")
        error, note = hub.report_message(msg_id, guest_name, reason)
        _guest_notice(hub, sock, error or note)
        return

    if text.startswith(REPLYTO_PREFIX):
        msg_id, _, target_id = text[len(REPLYTO_PREFIX):].partition("|")
        if payload := hub.make_reply(msg_id, guest_name, target_id):
            hub.broadcast_reply(payload, exclude_sock=sock)
            event_queue.put(("reply", payload))
            route_reply_ping(hub, guest_name, payload, lambda t: _guest_notice(hub, sock, t),
                             on_host_ping=lambda who: event_queue.put(("ping", who)))
        return

    if text.startswith(NICK_PREFIX):
        if error := hub.rename(guest_name, text[len(NICK_PREFIX):].strip(), by=guest_name):
            _guest_notice(hub, sock, error)
        return

    if any(text.startswith(prefix) for prefix in GAME_PREFIXES.values()):
        game, prefix = next((g, p) for g, p in GAME_PREFIXES.items() if text.startswith(p))
        score, _, playing = text[len(prefix):].partition("|")
        hub.update_game(game, guest_name, score, playing == "1", exclude_sock=sock, emit=True)
        return

    if text.startswith(DND_PREFIX):
        _, _, state = text[len(DND_PREFIX):].partition("|")
        dname = guest_name  # a guest can only change their own Do Not Disturb
        active = state == "on"
        if hub.set_dnd(dname, active):
            verb = "turned on" if active else "turned off"
            hub.broadcast(f"* {dname} {verb} Do Not Disturb *", exclude_sock=sock)
            event_queue.put(("system", f"{dname} {verb} Do Not Disturb"))
        return

    for prefix, sentinel in UNLOCK_PREFIX_TO_SENTINEL.items():
        if text.startswith(prefix):
            hub.set_gradient(guest_name, sentinel)
            hub.broadcast_colormap()
            event_queue.put(("colormap", hub.colormap_snapshot()))
            return

    if text.startswith(FEATURES_PREFIX):
        hub.set_features(sock, [f for f in text[len(FEATURES_PREFIX):].split(",") if f])
        if FEATURE_FLAPPY in hub.get_info(sock).get("features", ()):  # catch them up on the Flappy Bird board
            for entry in hub.game_entries("flappy"):
                hub.send_private(sock, Hub._game_wire("flappy", entry))
        if FEATURE_WARNSYNC in hub.get_info(sock).get("features", ()):  # …and on any warnings they still have
            if payload := hub.warning_sync_payload(guest_name):
                hub.send_private(sock, WARNSYNC_PREFIX + json.dumps(payload))
        # Only a client that announced itself gets our reply — an older one never
        # does, so it never sees protocol text it can't parse.
        hub.send_private(sock, FEATURES_PREFIX + ",".join(sorted(HOST_FEATURES)))
        return

    if text.startswith(FINGERPRINT_PREFIX):
        fp = text[len(FINGERPRINT_PREFIX):].strip()
        hub.set_fingerprint(sock, fp)
        event_queue.put(("system", f"{guest_name}'s device fingerprint: {fp}"))
        return

    if text.startswith(CMD_PREFIX):
        _handle_guest_command(text, sock, guest_name, is_admin, hub, host_name, event_queue)
        return

    if hub.is_muted(sock):
        info = hub.get_info(sock)
        hub.send_private(sock, MUTE_NOTICE_PREFIX + f"You are muted by {info['muted_by']} until {until_token(info['muted_until'])}. Reason: {info['mute_reason']}")
        return

    if text.startswith(EDIT_PREFIX):
        msg_id, _, new_text = text[len(EDIT_PREFIX):].partition("|")
        if error := hub.edit_message(msg_id, guest_name, new_text):
            _guest_notice(hub, sock, error)
        return

    if text.startswith(DELETE_PREFIX):
        msg_id = text[len(DELETE_PREFIX):].partition("|")[0]
        if error := hub.delete_message(msg_id, guest_name, is_admin):
            _guest_notice(hub, sock, error)
        return

    if text.startswith(REACT_PREFIX):
        msg_id, _, rest = text[len(REACT_PREFIX):].partition("|")
        emoji = rest.partition("|")[0]
        record = hub.messages.get(msg_id)
        if record is not None and record.get("to"):
            return  # whispers can't be reacted to — and a reaction would tell the whole room about one
        hub.broadcast(f"{REACT_PREFIX}{msg_id}|{emoji}|{guest_name}", exclude_sock=sock)  # reactions are always from the real sender
        event_queue.put(("react", {"msg_id": msg_id, "emoji": emoji, "sender": guest_name}))
        return

    if text.startswith(WHISPER_PREFIX):
        wait = hub.check_slowmode(guest_name, is_admin)
        if wait > 0:
            _guest_notice(hub, sock, f"Slowmode is active! Please wait {wait:.1f} seconds.")
            return
        msg_id, _, rest = text[len(WHISPER_PREFIX):].partition("|")
        target, _, body = rest.partition("|")
        if error := hub.whisper(msg_id, guest_name, target, body):
            _guest_notice(hub, sock, error)
        return

    is_file = text.startswith(FILE_PREFIX)
    if not (is_file or text.startswith(MSG_PREFIX)):
        return  # e.g. the "[name left the chat]" courtesy line — nothing to relay

    wait = hub.check_slowmode(guest_name, is_admin)
    if wait > 0:
        _guest_notice(hub, sock, f"Slowmode is active! Please wait {wait:.1f} seconds.")
        return

    if is_file:
        _handle_guest_file(text, sock, guest_name, hub, event_queue)
        return

    msg_id, _, raw_text = text[len(MSG_PREFIX):].partition("|")
    body = raw_text.partition(": ")[2] if ": " in raw_text else raw_text
    if len(body) > MAX_MESSAGE_CHARS:
        return _guest_notice(hub, sock, f"That message is too long (the limit is {MAX_MESSAGE_CHARS:,} characters).")
    # The sender's name is stamped on by the host, never taken from the message: a modified
    # client could otherwise post as anyone — including the host.
    raw_text = f"{guest_name}: {body}"
    text = f"{MSG_PREFIX}{msg_id}|{raw_text}"
    if not hub.record_message(msg_id, guest_name, body):
        return  # unusable or already-used id: never relay it (it could shadow someone's message)
    _ping_from_guest(hub, sock, guest_name, host_name, raw_text, event_queue)
    event_queue.put(("chat", {"raw": raw_text, "colors": hub.colormap_snapshot(), "msg_id": msg_id}))
    hub.broadcast(text, exclude_sock=sock)

def _handle_ban_appeal(sock, addr, hub: Hub, payload: str):
    """Someone who's banned (they can't join, so they dial in just to appeal)."""
    def finish(text: str):
        hub.send_private(sock, NOTICE_PREFIX + text)
        sock.close()

    try: appeal_fp = str(json.loads(payload).get("fp") or "").strip()[:64] or None
    except (ValueError, AttributeError): appeal_fp = None
    ban = hub.get_ban_info(addr[0], appeal_fp)
    if ban is None:
        return finish("You aren't banned any more — just try joining again.")
    appeal = parse_appeal(payload)
    if appeal is None or appeal["kind"] != "ban":
        return finish("That appeal couldn't be read.")
    key = ban["key"]   # the ban's own record (it may have been made from a different address than this one)
    if not hub.mark_ban_appealed(key):
        return finish("You've already appealed this ban — the admins have it. Hang tight!")
    name = str(json.loads(payload).get("name", "Someone"))[:30]
    reason = ban.get("reason") or "no reason given"
    appeal_id = hub.register_appeal("ban", name, ip=key)
    hub.admin_broadcast(format_appeal(
        f"Ban Appeal #{appeal_id}", f"{name} ({addr[0]})",
        f"is appealing their ban (by {ban.get('banned_by', '?')}, until {until_token(ban['until'])}; reason: \"{reason}\"). "
        f"To decide: /accept {appeal_id} [reason]  or  /reject {appeal_id} [reason]", appeal["answers"]))
    finish("Your appeal was sent to the host and admins. If they unban you, you can rejoin straight away.")

def _handle_warning_appeal(payload: str, sock, guest_name: str, hub: Hub):
    appeal = parse_appeal(payload)
    if appeal is None or appeal["kind"] != "warn":
        return _guest_notice(hub, sock, APPEAL_UNREADABLE_TEXT)
    record = hub.mark_warning_appealed(guest_name, appeal["number"])
    if record is None:
        return _guest_notice(hub, sock, APPEAL_MISSING_TEXT)
    appeal_id = hub.register_appeal("warn", record.get("name", guest_name), number=appeal["number"])
    hub.admin_broadcast(format_appeal(
        f"Warning Appeal #{appeal_id}", guest_name,
        f"is appealing warning #{appeal['number']} (from {record['by']}: \"{record['reason']}\"). "
        f"To decide: /accept {appeal_id} [reason]  or  /reject {appeal_id} [reason]", appeal["answers"]))
    _guest_notice(hub, sock, APPEAL_SENT_TEXT)

def _peek_fingerprint(sock, hub: Hub, wait: float = 0.6):
    """A 1.5.1+ client sends its device fingerprint right behind its hello. Reading it first lets the host check the
    ban list by device as well as by address. Older clients send nothing yet, so this just times out for them."""
    try:
        if not select.select([sock], [], [], wait)[0]:
            return None
        sock.settimeout(5)
        frame = recv_message(sock, hub.fernet)
        sock.settimeout(None)
    except (OSError, ConnectionError, InvalidToken):
        return None
    if frame.startswith(FINGERPRINT_PREFIX):
        return frame[len(FINGERPRINT_PREFIX):].strip()[:64] or None
    return None

def handle_guest_connection(sock, addr, hub: Hub, host_name: str, event_queue: queue.Queue):
    try:
        sock.settimeout(10)  # a real client speaks immediately; don't let silent connections pile up
        first = recv_message(sock, hub.fernet)
        sock.settimeout(None)
    except InvalidToken:
        try: sock.sendall((0xFFFFFFFF).to_bytes(MSG_LEN_BYTES, 'big'))
        except OSError: pass
        sock.close()
        return
    except (OSError, ConnectionError):
        sock.close()
        return

    if first.startswith(APPEAL_PREFIX):
        _handle_ban_appeal(sock, addr, hub, first[len(APPEAL_PREFIX):])
        return

    if first.startswith(BANCHECK_PREFIX):  # a banned person's screen asking whether the ban is still on
        check_fp = first[len(BANCHECK_PREFIX):].partition("|")[2].strip()[:64] or None
        hub.send_private(sock, BANSTATUS_PREFIX + json.dumps(hub.ban_status(addr[0], check_fp)))
        sock.close()
        return

    fingerprint = _peek_fingerprint(sock, hub) if first.startswith(HELLO_PREFIX) else None
    ban_info = hub.get_ban_info(addr[0], fingerprint)
    if ban_info:
        reason = ban_info.get("reason") or "no reason given"
        hub.send_private(sock, BAN_NOTICE_PREFIX + make_ban_notice(ban_info["until"], reason, hub.host_name))
        sock.close()
        return

    if not first.startswith(HELLO_PREFIX):
        sock.close()
        return

    guest_name = first[len(HELLO_PREFIX):].strip()[:30] or f"Guest@{addr[0]}"

    if error := nickname_error(guest_name):
        hub.send_private(sock, NOTICE_PREFIX + error)
        sock.close()
        return
    if hub.is_host(guest_name):
        hub.send_private(sock, NOTICE_PREFIX + "Nickname already in use.")
        sock.close()
        return
    if error := hub.claim_name(guest_name, addr[0]):
        hub.send_private(sock, NOTICE_PREFIX + error)
        sock.close()
        return

    with hub.lock:
        room_full = len(hub.clients) >= MAX_GUESTS
    if room_full:
        hub.send_private(sock, NOTICE_PREFIX + "[room is full — try again later]")
        sock.close()
        return

    hub.add_client(sock, guest_name, addr[0])
    if fingerprint:
        hub.set_fingerprint(sock, fingerprint)
        event_queue.put(("system", f"{guest_name}'s device fingerprint: {fingerprint}"))

    # Everything from here on is inside try/finally so that *any* failure still
    # removes the guest — otherwise a "ghost" would block the name until restart.
    try:
        hub.apply_ghost_ip_mute(sock, addr[0])
        hub.assign_color(guest_name)

        event_queue.put(("system", f"{guest_name} joined from {addr[0]}"))
        hub.broadcast(f"* {guest_name} joined the chat *", exclude_sock=sock)
        # The roster MUST be the first thing a joining client receives — its handshake
        # treats anything else as an invalid reply and gives up. (A rejoining muted user
        # used to be sent their mute status first, so they could never get back in.)
        hub.send_private(sock, ROSTER_PREFIX + ",".join([hub.host_name] + hub.names()))
        hub.send_private(sock, SLOWMODE_PREFIX + str(hub.slowmode_delay))
        if hub.is_muted(sock):
            info = hub.get_info(sock)
            hub.send_private(sock, MUTE_STATUS_PREFIX + f"1:{info['muted_until']}")
        hub.mark_ready(sock)  # from here on the client receives broadcasts normally
        for entry in hub.game_entries("snake"):  # catch the joiner up on the live Snake leaderboard
            hub.send_private(sock, Hub._game_wire("snake", entry))
        hub.broadcast_colormap()
        event_queue.put(("colormap", hub.colormap_snapshot()))
        event_queue.put(("roster", hub.names()))

        while True:
            try: text = recv_message(sock, hub.fernet)
            except InvalidToken: continue
            except (OSError, ConnectionError): break
            except Exception:
                traceback.print_exc()  # anything else means the stream is unusable
                break

            try:
                # Use their *current* nickname — they may have renamed since joining.
                current_name = hub.get_info(sock).get("name", guest_name)
                _process_guest_message(text, sock, current_name, hub, host_name, event_queue)
            except Exception:
                traceback.print_exc()  # one bad message must never end the guest's session
    finally:
        hub.abort_transfers_of(sock)  # a half-sent file must not linger on anyone's screen
        info = hub.remove_client(sock)
        guest_name = info["name"] if info else guest_name  # as they were last known (they may have renamed)
        hub.free_color(guest_name)
        try: sock.close()
        except OSError: pass
        if not hub.closed:
            hub.game_player_left(guest_name)
            name = info["name"] if info else guest_name
            if not (info and info.get("kicked")):
                event_queue.put(("system", f"{name} disconnected"))
                hub.broadcast(f"* {name} left the chat *", exclude_sock=sock)
                hub.broadcast_colormap()
                event_queue.put(("colormap", hub.colormap_snapshot()))
            event_queue.put(("roster", hub.names()))


def host_accept_loop(server: socket.socket, hub: Hub, host_name: str, event_queue: queue.Queue):
    while True:
        try: conn, addr = server.accept()
        except OSError: break
        enable_keepalive(conn)
        threading.Thread(target=handle_guest_connection, args=(conn, addr, hub, host_name, event_queue), daemon=True).start()


# ---- Slash commands ----

HELP_TEXT = (
    "Commands: /mute <name> <time> [reason], /unmute <name>, /kick <name> [reason], "
    "/ban <name or ip> [time|perm] [reason], /unban <#, name or ip> [reason], /bans (who is banned), /slowmode [sec], /admin <name>, /unadmin <name>, "
    "/warn <name> [reason], /unwarn <name> [warning #] [reason], /history [name], /appeals, "
    "/accept <appeal #> [reason], /reject <appeal #> [reason], /color <name>, /colors, /list, /clear [lines], /warnings (your warnings — admins: /warnings <name>), /whisper <name> <msg>, "
    "/nick <new name> (you can change yours twice per chat), /help — "
    "Times: 30 (minutes), 90m, 2h, 7d, 2w, 3mo, 1y. "
    "host only: /rename <current name> <new name>. "
    "Ctrl+Shift+S opens the games (Snake, Flappy Bird) — in a chat or on the home screen. "
    "Paste an image with Ctrl+V (Cmd+V on Mac) to send it. "
    "Right-click a message to reply to it, or report it to the admins. "
    "Right-click a message or attachment to edit/delete it (admins can delete anyone's, but never whispers). "
    "To whisper a file or sticker, type /whisper <name> then click the 📎 or 🌠 button."
)

PERMANENT_WORDS = ("perm", "indefinite", "0", "infinite")

_DURATION_RE = re.compile(r"^(\d+(?:\.\d+)?)\s*([a-z]*)$")
_DURATION_UNITS = {
    "": 60, "m": 60, "min": 60, "mins": 60, "minute": 60, "minutes": 60,     # a bare number means minutes, as it always has
    "s": 1, "sec": 1, "secs": 1, "second": 1, "seconds": 1,
    "h": 3600, "hr": 3600, "hrs": 3600, "hour": 3600, "hours": 3600,
    "d": 86400, "day": 86400, "days": 86400, "w": 604800, "wk": 604800, "wks": 604800, "week": 604800, "weeks": 604800,
}
_CALENDAR_UNITS = {"mo": 1, "mon": 1, "month": 1, "months": 1, "y": 12, "yr": 12, "yrs": 12, "year": 12, "years": 12}

def parse_until(token: str, now: float = None):
    """'30' (minutes) | '90m' | '2h' | '7d' | '2w' | '3mo' | '1y' -> the moment it ends, or None if `token` isn't a
    duration. Months and years are calendar ones: '1y' ends at the same date and clock time next year (not
    365 days — or 365.25 — from now, which drifts by hours)."""
    m = _DURATION_RE.match(token.strip().lower())
    if not m: return None
    amount, unit = float(m.group(1)), m.group(2)
    now = time.time() if now is None else now
    if unit in _CALENDAR_UNITS:
        if amount != int(amount): return None
        months = int(amount) * _CALENDAR_UNITS[unit]
        if months > 1200: return None
        start = datetime.datetime.fromtimestamp(now)
        year, month0 = divmod(start.year * 12 + (start.month - 1) + months, 12)
        day = min(start.day, calendar.monthrange(year, month0 + 1)[1])
        try: return time.mktime(start.replace(year=year, month=month0 + 1, day=day).timetuple())
        except (OverflowError, ValueError): return None
    if unit not in _DURATION_UNITS: return None
    seconds = amount * _DURATION_UNITS[unit]
    return now + seconds if 0 < seconds <= 100 * 365 * 86400 else None

def parse_ban_args(parts: list) -> tuple:
    """`parts` = [target, duration?, reason?] -> (until_timestamp, reason).
    A duration that isn't a number or a 'permanent' word is treated as the
    start of the reason, with the ban permanent."""
    dur = parts[1].lower() if len(parts) > 1 else "perm"
    reason = parts[2] if len(parts) > 2 else ""
    if dur in PERMANENT_WORDS:
        until = float("inf")
    else:
        until = parse_until(dur)
        if until is None:
            until = float("inf")
            reason = f"{dur} {reason}".strip()
    return until, reason or "no reason given"

def _cmd_help(arg, hub, me, reply):
    reply(HELP_TEXT)

def _cmd_list(arg, hub, me, reply):
    names = hub.names()
    reply("Connected: " + (", ".join(names) if names else "(no one yet)"))

def _cmd_colors(arg, hub, me, reply):
    reply("Available colors: " + ", ".join(COLOR_PALETTE))

def _cmd_color(arg, hub, me, reply):
    color = arg.lower()
    is_host = hub.is_host(me)
    if not color:
        reply("Usage: /color <name> — see /colors")
    elif not is_host and me.lower() in hub.color_changed_once:
        reply("You can only change your color once in one chat session.")
    elif color in COLOR_PALETTE:
        hub.set_color(me, COLOR_PALETTE[color], once=not is_host)
        hub.broadcast_colormap()
        reply(f"Color changed successfully to {color}.")
    else:
        reply(f"Invalid color. Available: {', '.join(COLOR_PALETTE)}")

def _cmd_whisper(arg, hub, me, reply):
    parts = arg.split(maxsplit=1)
    if len(parts) < 2:
        return reply("Usage: /whisper <name> <message>")
    if error := hub.whisper(os.urandom(4).hex(), me, parts[0], parts[1]):
        reply(error)

def _cmd_nick(arg, hub, me, reply):
    if not arg:
        return reply("Usage: /nick <new name>")
    if error := hub.rename(me, arg, by=me):
        reply(error)

def _cmd_rename(arg, hub, me, reply):
    if not hub.is_host(me):
        return reply("Only the host can use /rename.")
    parts = arg.split()
    if len(parts) != 2:
        return reply("Usage: /rename <current name> <new name>")
    old, new = parts
    if hub.is_host(old):
        return reply("Use /nick to change your own name.")
    sock = hub.find_socket_by_name(old)
    if sock is None:
        return reply(f"No one named '{old}' is connected.")
    canonical = hub.get_info(sock)["name"]
    if error := hub.rename(canonical, new, by=me):
        return reply(error)
    hub.log_admin_action(me, f"renamed {canonical} to {new}.")
    reply(f"Renamed {canonical} to {new}.")

def _cmd_warn(arg, hub, me, reply):
    parts = arg.split(maxsplit=1)
    if not parts:
        return reply("Usage: /warn <name> [reason]")
    if error := hub.warn(parts[0], me, parts[1] if len(parts) > 1 else ""):
        return reply(error)
    reply(f"Warned {parts[0]}.")

def _cmd_admin(arg, hub, me, reply):
    if not arg: return reply("Usage: /admin <name>")
    if hub.is_host(arg): return reply("You cannot admin the host.")
    target_sock = hub.find_socket_by_name(arg)
    if not target_sock:
        return reply(f"No one named '{arg}' is connected.")
    hub.admins.add(arg.lower())
    hub.send_private(target_sock, ADMIN_NOTICE_PREFIX + "1")
    hub.broadcast(f"* {arg} is now an admin *")
    hub.log_admin_action(me, f"granted admin privileges to {arg}.")
    reply(f"Granted admin privileges to {arg}.")

def _cmd_unadmin(arg, hub, me, reply):
    if not arg: return reply("Usage: /unadmin <name>")
    if hub.is_host(arg): return reply("You cannot unadmin the host.")
    if arg.lower() not in hub.admins:
        return reply(f"'{arg}' is not an admin.")
    hub.admins.discard(arg.lower())
    target_sock = hub.find_socket_by_name(arg)
    if target_sock:
        hub.send_private(target_sock, ADMIN_NOTICE_PREFIX + "0")
    hub.broadcast(f"* {arg} is no longer an admin *")
    hub.log_admin_action(me, f"revoked admin privileges from {arg}.")
    reply(f"Revoked admin privileges from {arg}.")

def _cmd_slowmode(arg, hub, me, reply):
    if not arg:
        hub.slowmode_delay = 0.0 if hub.slowmode_delay > 0 else 2.0
    else:
        try: hub.slowmode_delay = max(0.0, float(arg))
        except ValueError:
            return reply("Usage: /slowmode [seconds]")
    status = f"set to {hub.slowmode_delay:g}s" if hub.slowmode_delay > 0 else "disabled"
    hub.broadcast(f"* Slowmode has been {status} *")
    hub.broadcast(SLOWMODE_PREFIX + str(hub.slowmode_delay))
    hub.log_admin_action(me, f"set slowmode to {hub.slowmode_delay:g}s.")
    reply(f"Slowmode has been {status}.")

def _do_ban(arg, hub, me, reply, usage, address_only=False):
    parts = arg.split(maxsplit=2)
    if not parts: return reply(usage)
    token = parts[0].strip()
    if hub.is_host(token): return reply("You cannot ban the host.")
    device = hub.find_device(token)
    if device is None or not device[0]:
        return reply(f"I don't know '{token}' — they aren't connected and haven't joined this session. "
                     f"Use their IP address (/ipban <ip>) if you have it.")
    ip, fp, name = device
    until, reason = parse_ban_args(parts)
    hub.ban_ip(ip, until, me, reason, fp=fp, name=name)
    until_str = until_token(until)
    who = name or f"IP {ip}"
    hub.record_mod("ban", who, me, reason, ip=ip, until=until)
    # Everyone connected from that address or that device goes too (a second window, a new nickname).
    removed = set()
    for _ in range(5):
        target = hub.find_socket_by_ip(ip) or (hub._find_socket(lambda info: fp and info.get("fingerprint") == fp) if fp else None)
        if target is None or target in removed: break
        removed.add(target)
        tname = hub.get_info(target).get("name", "someone")
        hub.eject(target, BAN_NOTICE_PREFIX + make_ban_notice(until, reason, hub.host_name), f"* {tname} has been banned *")
    hub.log_admin_action(me, f"banned {who} ({ip}) until {until_str}. Reason: {reason}")
    reply(f"Banned {who} ({ip}{' · device ' + fp[:8] if fp else ''}) until {until_str}. Reason: {reason}. It's saved, so it survives a restart. /bans lists bans; /unban lifts one.")

def _cmd_ban(arg, hub, me, reply):
    _do_ban(arg, hub, me, reply, "Usage: /ban <name or ip> [time|perm] [reason]   (time: 30, 2h, 7d, 1y …)")

def _cmd_ipban(arg, hub, me, reply):
    if not hub.is_host(me): return reply("Only the host can use /ipban.")
    _do_ban(arg, hub, me, reply, "Usage: /ipban <ip or name> [time|perm] [reason]   (time: 30, 2h, 7d, 1y …)", address_only=True)

def _cmd_unban(arg, hub, me, reply):
    parts = arg.split(maxsplit=1)
    if not parts: return reply("Usage: /unban <# from /bans, name or ip> [reason]")
    reason = parts[1] if len(parts) > 1 else ""
    key = hub.resolve_ban_target(parts[0])
    label = hub.ban_label(key) if key is not None else None
    if key is None or not hub.unban_ip(key, me, reason):
        return reply(f"'{parts[0]}' isn't banned. /bans shows who is.")
    hub.broadcast(f"* {label} has been unbanned *")
    hub.log_admin_action(me, f"unbanned {label} ({key}). Reason: {' '.join(reason.split()) or 'no reason given'}")
    reply(f"Unbanned {label} ({key}). If they're on their ban screen, they'll be told.")

def _cmd_bans(arg, hub, me, reply):
    reply(hub.bans_text())

def _cmd_unwarn(arg, hub, me, reply):
    usage = "Usage: /unwarn <name> [warning # | all] [reason]"
    parts = arg.split(maxsplit=2)
    if not parts: return reply(usage)
    name, rest = parts[0], parts[1:]
    selector, reason = None, " ".join(rest)
    if rest and (rest[0].lstrip("#").isdigit() or rest[0].lower() == "all"):
        selector, reason = rest[0].lstrip("#").lower(), (rest[1] if len(rest) > 1 else "")
    active = hub.active_warnings(name)
    if not active:
        return reply(f"{name} has no active warnings.")
    shown = active[0][1].get("name", name)
    if selector is None:
        if len(active) > 1:  # don't guess which one they meant
            lines = [f"{shown} has {len(active)} active warnings — which one?"]
            lines += [f"  #{n}  from {r['by']}: \"{r['reason']}\"" for n, r in active]
            lines.append(f"/unwarn {shown} <#> [reason]    or    /unwarn {shown} all [reason]")
            return reply("\n".join(lines))
        selector = str(active[0][0])
    numbers = [n for n, _ in active] if selector == "all" else [int(selector)]
    removed = []
    for number in numbers:
        error, _, _ = hub.delete_warning(name, number, me, reason)
        if error:
            if len(numbers) == 1: return reply(error)
        else:
            removed.append(number)
    if not removed: return reply(f"{shown} has no active warnings.")
    listed = ", ".join(f"#{n}" for n in removed)
    plural = "warnings" if len(removed) > 1 else "warning"
    hub.log_admin_action(me, f"removed {plural} {listed} from {shown}. Reason: {' '.join(reason.split()) or 'no reason given'}")
    reply(f"Removed {plural} {listed} from {shown}.")

def warnings_report(hub, requester: str, arg: str, is_admin: bool) -> str:
    """The reply to /warnings [name]: your own warnings, or (for admins and the host) someone else's."""
    target = arg.strip()
    if not target:
        if hub.is_host(requester): return "You're the host, so you're invincible!"
        return hub.warnings_text(requester, own=True)
    if target.lower() != requester.lower() and not (is_admin or hub.is_host(requester)):
        return "Only admins can look up other people's warnings — /warnings on its own shows yours."
    if hub.is_host(target):
        return "You're the host, so you're invincible!" if target.lower() == requester.lower() else f"{target} is the host, so they can't be warned."
    return hub.warnings_text(target, own=target.lower() == requester.lower())

def _cmd_warnings(arg, hub, me, reply):
    reply(warnings_report(hub, me, arg, is_admin=True))  # only the host (and admins, via a guest's own path) get here

def _cmd_history(arg, hub, me, reply):
    reply(hub.history_text(arg.strip() or None))

def _cmd_appeals(arg, hub, me, reply):
    pending = hub.pending_appeals()
    if not pending: return reply("No appeals are waiting.")
    lines = ["Open appeals:"]
    for a in pending:
        what = "ban" if a["kind"] == "ban" else f"warning #{a['number']}"
        lines.append(f"  #{a['id']}  {a['who']} — {what} ({ago_token(a['time'])})")
    lines.append("Decide with /accept <#> [reason] or /reject <#> [reason].")
    reply("\n".join(lines))

def _decide_appeal_cmd(arg, hub, me, reply, accept: bool):
    word = "accept" if accept else "reject"
    parts = arg.split(maxsplit=1)
    try: appeal_id = int(parts[0].lstrip("#")) if parts else None
    except ValueError: appeal_id = None
    if appeal_id is None: return reply(f"Usage: /{word} <appeal #> [reason]   (/appeals lists the open ones)")
    error, text, log_text = hub.decide_appeal(appeal_id, accept, me, parts[1] if len(parts) > 1 else "")
    if error: return reply(error)
    hub.log_admin_action(me, log_text)
    reply(text)

def _cmd_accept(arg, hub, me, reply): _decide_appeal_cmd(arg, hub, me, reply, True)
def _cmd_reject(arg, hub, me, reply): _decide_appeal_cmd(arg, hub, me, reply, False)

def _cmd_mute(arg, hub, me, reply):
    usage = "Usage: /mute <name> <time> [reason]   (time: 30 minutes, 2h, 7d, 1y …)"
    parts = arg.split(maxsplit=2)
    if len(parts) < 2: return reply(usage)
    name = parts[0]
    if hub.is_host(name): return reply("You cannot mute the host.")
    until = parse_until(parts[1])
    if until is None: return reply(usage)
    length = format_duration(until - time.time())
    reason = parts[2] if len(parts) > 2 else "no reason given"
    if not hub.mute(name, until, me, reason):
        return reply(f"No one named '{name}' is connected.")

    hub.broadcast(f"* {name} has been muted *")
    target_sock = hub.find_socket_by_name(name)
    hub.record_mod("mute", hub.get_info(target_sock).get("name", name) if target_sock else name, me, reason,
                   detail=f"for {length}")
    if target_sock:
        hub.send_private(target_sock, MUTE_NOTICE_PREFIX + f"You were muted by {me} for {length}. Reason: {reason}")
        hub.send_private(target_sock, MUTE_STATUS_PREFIX + f"1:{until}")
    hub.log_admin_action(me, f"muted {name} until {until_token(until)}. Reason: {reason}")
    reply(f"Muted {name} for {length}, until {until_token(until)}. Reason: {reason}")

def _cmd_unmute(arg, hub, me, reply):
    if not arg: return reply("Usage: /unmute <name>")
    if hub.is_host(arg): return reply("You cannot unmute the host.")
    target_sock = hub.find_socket_by_name(arg)
    if not hub.unmute(arg):
        return reply(f"No one named '{arg}' is connected or muted.")
    hub.broadcast(f"* {arg} has been unmuted *")
    hub.record_mod("unmute", hub.get_info(target_sock).get("name", arg) if target_sock else arg, me)
    if target_sock:
        hub.send_private(target_sock, MUTE_STATUS_PREFIX + "0")
    hub.log_admin_action(me, f"unmuted {arg}.")
    reply(f"Unmuted {arg}.")

def _cmd_kick(arg, hub, me, reply):
    parts = arg.split(maxsplit=1)
    if not parts: return reply("Usage: /kick <name> [reason]")
    name = parts[0]
    if hub.is_host(name): return reply("You cannot kick the host.")
    reason = parts[1] if len(parts) > 1 else "no reason given"
    target = hub.find_socket_by_name(name)
    if not target:
        return reply(f"No one named '{name}' is connected.")
    hub.record_mod("kick", hub.get_info(target).get("name", name), me, reason)
    hub.eject(target, KICK_NOTICE_PREFIX + f"{me}|{reason}", f"* {name} has been kicked *")
    hub.log_admin_action(me, f"kicked {name}. Reason: {reason}")
    reply(f"Kicked {name}. Reason: {reason}")

COMMAND_HANDLERS = {
    "/help": _cmd_help, "/list": _cmd_list, "/colors": _cmd_colors, "/color": _cmd_color,
    "/whisper": _cmd_whisper, "/admin": _cmd_admin, "/unadmin": _cmd_unadmin,
    "/slowmode": _cmd_slowmode, "/ban": _cmd_ban, "/ipban": _cmd_ipban, "/unban": _cmd_unban, "/unipban": _cmd_unban, "/bans": _cmd_bans,
    "/mute": _cmd_mute, "/unmute": _cmd_unmute, "/kick": _cmd_kick,
    "/nick": _cmd_nick, "/rename": _cmd_rename, "/warn": _cmd_warn,
    "/unwarn": _cmd_unwarn, "/history": _cmd_history, "/appeals": _cmd_appeals,
    "/accept": _cmd_accept, "/reject": _cmd_reject, "/warnings": _cmd_warnings,
}
# Commands a guest may only send if the host has made them an admin.
MOD_COMMAND_NAMES = frozenset({"/mute", "/unmute", "/kick", "/ban", "/unban", "/unipban", "/bans", "/ipban", "/slowmode", "/admin", "/unadmin", "/warn", "/rename",
                           "/unwarn", "/history", "/appeals", "/accept", "/reject"})

def run_mod_command(msg: str, hub: Hub, my_name: str, reply_func) -> bool:
    """Runs a slash command against the hub. Returns False if `msg` isn't one
    of ours (so the caller should treat it as ordinary chat)."""
    name, _, arg = msg.strip().partition(" ")
    handler = COMMAND_HANDLERS.get(name.lower())
    if handler is None:
        return False
    handler(arg.strip(), hub, my_name, reply_func)
    return True


# ---- Guest-side receive loop ----

# prefix -> UI event kind, for messages that need no processing beyond stripping the prefix
GUEST_SIMPLE_EVENTS = (
    (PING_PREFIX, "ping"),
    (ADMIN_NOTICE_PREFIX, "admin_status"),
    (ADMIN_LOG_PREFIX, "system"),
    (MUTE_STATUS_PREFIX, "mute_status"),
    (MUTE_NOTICE_PREFIX, "mute_notice"),
    (NOTICE_PREFIX, "private"),
)
LEAVE_PATTERN = re.compile(r"^\* (.+?) (?:left the chat|has been kicked|has been IP banned) \*$")
JOIN_PATTERN = re.compile(r"^\* (.+?) joined the chat \*$")

def guest_recv_loop(sock, fernet, event_queue, local_colors, colors_lock, known_names, host_ip, closing, host_features, assembler):
    typing_names = set()
    put = event_queue.put

    def handle(text) -> bool:
        """Returns False when the session is over."""
        if text.startswith(TYPING_START_PREFIX):
            typing_names.add(text[len(TYPING_START_PREFIX):])
            put(("typing", list(typing_names)))
            return True
        if text.startswith(TYPING_STOP_PREFIX):
            typing_names.discard(text[len(TYPING_STOP_PREFIX):])
            put(("typing", list(typing_names)))
            return True

        for prefix, kind in GUEST_SIMPLE_EVENTS:
            if text.startswith(prefix):
                put((kind, text[len(prefix):]))
                return True

        if text.startswith(SLOWMODE_PREFIX):
            try: put(("slowmode", float(text[len(SLOWMODE_PREFIX):])))
            except ValueError: pass
            return True
        if text.startswith(BAN_NOTICE_PREFIX):
            until_str, reason, host_name = parse_ban_notice(text[len(BAN_NOTICE_PREFIX):])
            put(("banned_live", {"message": f"You were banned from the chat hosted by {host_name or host_ip} until {until_str}. Reason: {reason}",
                                 "until": until_str, "reason": reason, "host_name": host_name}))
            return False
        if text.startswith(KICK_NOTICE_PREFIX):
            by, _, reason = text[len(KICK_NOTICE_PREFIX):].partition("|")
            put(("kicked", f"You were kicked by {by}. Reason: {reason}"))
            return False
        if text.startswith(HOST_DISCONNECT_PREFIX):
            put(("disconnected", "Host disconnected."))
            return False
        if text.startswith(ROSTER_PREFIX):
            known_names.update(n.strip() for n in text[len(ROSTER_PREFIX):].split(",") if n.strip())
            put(("roster", sorted(known_names)))
            return True
        if text.startswith(COLORMAP_PREFIX):
            new_map = dict(pair.split("=", 1) for pair in text[len(COLORMAP_PREFIX):].split(",") if "=" in pair)
            with colors_lock:
                local_colors.clear()
                local_colors.update(new_map)
            put(("colormap", dict(new_map)))
            return True
        if text.startswith(FILE_PREFIX):
            info = parse_file_start(text)
            if info is None: put(("system", "[received a corrupted file, ignored]"))
            else: assembler.start(info)
            return True
        if text.startswith(FILECHUNK_PREFIX):
            try:
                msg_id, index, b64 = text[len(FILECHUNK_PREFIX):].split("|", 2)
                assembler.chunk(msg_id, int(index), b64)
            except ValueError:
                pass
            return True
        if text.startswith(FILEEND_PREFIX):
            assembler.finish(text[len(FILEEND_PREFIX):].strip())
            return True
        if text.startswith(FILEABORT_PREFIX):
            msg_id, _, reason = text[len(FILEABORT_PREFIX):].partition("|")
            info = assembler.abort(msg_id)
            if info is not None:
                put(("system", abort_message(info, reason)))
            return True
        if text.startswith(FEATURES_PREFIX):
            host_features.update(f for f in text[len(FEATURES_PREFIX):].split(",") if f)
            put(("features", None))  # now we know what the host understands (an open game can announce itself)
            return True
        if text.startswith(WARNSYNC_PREFIX):
            try: put(("warn_sync", json.loads(text[len(WARNSYNC_PREFIX):])))
            except ValueError: pass
            return True
        if text.startswith(WARNSTATE_PREFIX):
            number, _, state = text[len(WARNSTATE_PREFIX):].partition("|")
            if number.isdigit():
                put(("warn_state", {"number": int(number), "state": state}))
            return True
        if text.startswith(REPLY_PREFIX):
            try:
                msg_id, to, author, snippet = text[len(REPLY_PREFIX):].split("|", 3)
                put(("reply", {"msg_id": msg_id, "to": to, "author": author, "snippet": snippet}))
            except ValueError:
                pass
            return True
        if text.startswith(RENAME_PREFIX):
            try:
                old, new, by = text[len(RENAME_PREFIX):].split("|", 2)
            except ValueError:
                return True
            known_names.discard(old)
            known_names.add(new)
            if old in typing_names:
                typing_names.discard(old)
                put(("typing", list(typing_names)))
            put(("rename", {"old": old, "new": new, "by": by}))
            return True
        if text.startswith(WARN_PREFIX):
            try:
                by, count, reason = text[len(WARN_PREFIX):].split("|", 2)
                put(("warned", {"by": by, "count": int(count), "reason": reason}))
            except ValueError:
                pass
            return True
        for game, prefix in GAME_PREFIXES.items():
            if text.startswith(prefix):
                try:
                    name, best, score, playing = text[len(prefix):].rsplit("|", 3)
                    put(("game", {"game": game, "entry": {"name": name, "best": int(best), "score": int(score), "playing": playing == "1"}}))
                except ValueError:
                    pass
                return True
        if text.startswith(WHISPER_PREFIX):
            msg_id, _, rest = text[len(WHISPER_PREFIX):].partition("|")
            sender, _, rest = rest.partition("|")
            to, _, body = rest.partition("|")
            put(("whisper", {"msg_id": msg_id, "from": sender, "to": to, "text": body}))
            return True
        if text.startswith(EDIT_PREFIX):
            msg_id, _, rest = text[len(EDIT_PREFIX):].partition("|")
            editor, _, new_text = rest.partition("|")
            put(("msg_edit", {"msg_id": msg_id, "text": new_text, "editor": editor}))
            return True
        if text.startswith(DELETE_PREFIX):
            msg_id, _, deleter = text[len(DELETE_PREFIX):].partition("|")
            put(("msg_delete", {"msg_id": msg_id, "deleter": deleter}))
            return True
        if text.startswith(REACT_PREFIX):
            msg_id, _, rest = text[len(REACT_PREFIX):].partition("|")
            emoji, _, sender = rest.partition("|")
            put(("react", {"msg_id": msg_id, "emoji": emoji, "sender": sender}))
            return True

        msg_id = None
        if text.startswith(MSG_PREFIX):
            msg_id, _, text = text[len(MSG_PREFIX):].partition("|")

        if m := JOIN_PATTERN.match(text):
            known_names.add(m.group(1))
            put(("roster", sorted(known_names)))
        elif m := LEAVE_PATTERN.match(text):
            known_names.discard(m.group(1))
            if m.group(1) in typing_names:  # they left mid-sentence — don't keep showing "X is typing…"
                typing_names.discard(m.group(1))
                put(("typing", list(typing_names)))
            put(("roster", sorted(known_names)))
        elif m := re.match(r"^(.+?): ", text):
            known_names.add(m.group(1))

        with colors_lock:
            colors_copy = dict(local_colors)
        put(("chat", {"raw": text, "colors": colors_copy, "msg_id": msg_id}))
        return True

    while True:
        try: text = recv_message(sock, fernet)
        except InvalidToken:
            put(("system", "[received a message that failed to decrypt — key mismatch?]"))
            continue
        except (OSError, ConnectionError):
            if not closing.is_set():  # a deliberate Disconnect isn't an error worth reporting
                put(("disconnected", "Disconnected from host."))
            break
        except Exception:
            # Anything unexpected here used to end this thread silently — leaving you
            # connected but unable to see any more messages. Say so instead.
            traceback.print_exc()
            if not closing.is_set():
                put(("disconnected", "Connection error — please reconnect."))
            break

        try:
            if not handle(text):
                break
        except Exception:
            traceback.print_exc()  # a malformed message must not kill the receive thread


# ---- Connections ----

def bind_host_socket() -> socket.socket:
    """The room's listening socket. It prefers the well-known port (so a joiner on a network that blocks the UDP
    lookup can still find the room with a plain TCP connection); if that's taken, any free port."""
    for port in (DEFAULT_TCP_PORT, 0):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if os.name == "nt" and port and hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
                server.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)  # (SO_REUSEADDR would let a second copy share the port on Windows)
            else:
                server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(("0.0.0.0", port))
            return server
        except OSError:
            server.close()
            if port == 0: raise

class HostConnection:
    def __init__(self, name, room_code, fernet, event_queue):
        self.name = name
        self.fernet = fernet
        self.event_queue = event_queue

        self.hub = Hub(
            fernet, name,
            on_typing_change=lambda: event_queue.put(("typing", self.hub.typing_names())),
            on_admin_log=lambda msg: event_queue.put(("system", msg)),
            on_message_event=lambda kind, payload: event_queue.put((kind, payload)),
        )
        self.local_files = FileAssembler(event_queue)  # the host's own copy of files addressed to it
        self.hub.local_files = self.local_files

        self.server = bind_host_socket()
        self.tcp_port = self.server.getsockname()[1]
        self.server.listen(MAX_GUESTS)

        self.stop_event = threading.Event()

        threading.Thread(target=self._udp_discovery_loop, args=(room_code,), daemon=True).start()
        threading.Thread(target=host_accept_loop, args=(self.server, self.hub, self.name, self.event_queue), daemon=True).start()

    def _udp_discovery_loop(self, room_code):
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_sock.bind(("", DISCOVERY_PORT))
        except OSError as e:
            udp_sock.close()
            self.event_queue.put(("system", f"Room Code lookup is unavailable ({e}) — guests will need to enter your IP:port instead."))
            return
        udp_sock.settimeout(1.0)
        # The code we advertised, plus a code for every address we currently have. These are
        # refreshed while hosting, because the host's IP can change (Wi-Fi reconnect, sleep/wake,
        # DHCP renewal) and the Room Code is built from it.
        accepted = {f"DISCOVER:{room_code}"}
        shown_code = room_code
        last_primary = get_local_ip()
        last_refresh = time.time()
        offer = f"OFFER:{self.tcp_port}".encode("utf-8")

        while not self.stop_event.is_set():
            if time.time() - last_refresh >= 5.0:
                last_refresh = time.time()
                for ip in get_local_ips():
                    accepted.add(f"DISCOVER:{generate_room_code(ip)}")
                primary = get_local_ip()
                if primary != last_primary and not primary.startswith("127."):
                    last_primary = primary
                    new_code = generate_room_code(primary)
                    if new_code != shown_code:
                        shown_code = new_code
                        accepted.add(f"DISCOVER:{new_code}")
                        self.event_queue.put(("room_code_changed", {"room_code": new_code, "ip": primary}))
            try:
                data, addr = udp_sock.recvfrom(1024)
                if data.decode("utf-8", errors="replace") in accepted:
                    udp_sock.sendto(offer, addr)
            except (socket.timeout, OSError):
                continue
        udp_sock.close()

    def send_chat(self, text: str, reply_to: dict = None):
        if run_mod_command(text, self.hub, self.name, lambda t: self.event_queue.put(("system", t))):
            self.name = self.hub.host_name  # /nick may have renamed us
            # Commands like /color change shared state; refresh our own view now.
            self.event_queue.put(("colormap", self.hub.colormap_snapshot()))
            return
        if len(text) > MAX_MESSAGE_CHARS:
            return self.event_queue.put(("system", f"That message is too long (the limit is {MAX_MESSAGE_CHARS:,} characters)."))

        route_pings(self.hub, self.name, text, lambda t: self.event_queue.put(("system", t)), on_host_ping=lambda who: None)

        msg_id = os.urandom(4).hex()
        full_msg = f"{self.name}: {text}"
        self.hub.record_message(msg_id, self.name, text)
        self.event_queue.put(("chat", {"raw": full_msg, "colors": self.hub.colormap_snapshot(), "msg_id": msg_id}))
        self.hub.broadcast(f"{MSG_PREFIX}{msg_id}|{full_msg}")
        if reply_to and (payload := self.hub.make_reply(msg_id, self.name, reply_to["id"])):
            self.hub.broadcast_reply(payload)
            self.event_queue.put(("reply", payload))
            route_reply_ping(self.hub, self.name, payload, lambda t: self.event_queue.put(("system", t)),
                             on_host_ping=lambda who: None)

    def send_game(self, game: str, score: int, playing: bool):
        self.hub.update_game(game, self.name, score, playing)

    def send_dnd(self, active: bool):
        if self.hub.set_dnd(self.name, active):
            verb = "turned on" if active else "turned off"
            self.hub.broadcast(f"* {self.name} {verb} Do Not Disturb *")
            self.event_queue.put(("system", f"You {verb} Do Not Disturb."))

    def send_typing(self, started: bool):
        self.hub.broadcast((TYPING_START_PREFIX if started else TYPING_STOP_PREFIX) + self.name)

    def send_edit(self, msg_id: str, new_text: str):
        if error := self.hub.edit_message(msg_id, self.name, new_text):
            self.event_queue.put(("system", error))

    def send_delete(self, msg_id: str):
        # The host may delete anyone's message (including its own).
        if error := self.hub.delete_message(msg_id, self.name, deleter_is_admin=True):
            self.event_queue.put(("system", error))

    def send_react(self, msg_id: str, emoji: str):
        self.hub.broadcast(f"{REACT_PREFIX}{msg_id}|{emoji}|{self.name}")
        self.event_queue.put(("react", {"msg_id": msg_id, "emoji": emoji, "sender": self.name}))

    def send_file(self, filepath: str, on_done=None, to: str = None, on_progress=None, cancel=None):
        """Sends a file to everyone, or privately to `to`. Streams big files from disk;
        blocks until done (paced by recipients), so run it off the UI thread. Set the `cancel`
        Event to stop it part-way."""
        check_file_size(filepath)
        size, name = os.path.getsize(filepath), os.path.basename(filepath)
        if size <= INLINE_FILE_BYTES:
            with open(filepath, "rb") as f:
                return self.send_file_bytes(name, f.read(), on_done, to, on_progress, cancel)
        self._send_file(name, size, chunks_from_path(filepath), None, filepath, to, on_done, on_progress, cancel)

    def send_file_bytes(self, filename: str, data: bytes, on_done=None, to: str = None, on_progress=None, cancel=None):
        self._send_file(os.path.basename(filename), len(data), chunks_from_bytes(data), data, None, to, on_done, on_progress, cancel)

    def _send_file(self, filename, size, chunks, data, path, to, on_done, on_progress, cancel=None):
        done = on_done or (lambda ok: None)
        if self.hub.closed:
            return done(False)
        if size > MAX_FILE_BYTES:
            self.event_queue.put(("system", f"{filename} is {format_size(size)} — the limit is {FILE_LIMIT_TEXT}."))
            return done(False)
        target = ""
        if to:
            target, error = self.hub.resolve_whisper_target(self.name, to)
            if error:
                self.event_queue.put(("system", error))
                return done(False)
            if self.hub.legacy_targets(target):
                self.event_queue.put(("system", f"{target}'s version of chat_gui is too old to receive files — ask them to update."))
                return done(False)
        msg_id = os.urandom(4).hex()
        self.hub.record_message(msg_id, self.name, filename, kind="file", to=target or None)
        skipped = set()
        abort_frame = encode_frame(self.hub.fernet, f"{FILEABORT_PREFIX}{msg_id}|your connection couldn't keep up with this file")
        self.hub.announce_unreceivable(self.name, filename, size, target or None)
        try:
            for text in iter_file_texts(self.name, msg_id, target, filename, size, with_progress(chunks, size, on_progress)):
                if cancel is not None and cancel.is_set():
                    raise UploadCancelled()
                self.hub.relay_frame(encode_frame(self.hub.fernet, text), self.hub.transfer_targets(target or None, skipped=skipped),
                                     cancel=cancel, skipped=skipped, abort_frame=abort_frame)
        except Exception as e:
            self.hub.messages.pop(msg_id, None)
            reason = "cancelled by the sender" if isinstance(e, UploadCancelled) else "the sender hit an error"
            self.hub.relay_frame(encode_frame(self.hub.fernet, f"{FILEABORT_PREFIX}{msg_id}|{reason}"), self.hub.transfer_targets(target or None, skipped=skipped))
            if not isinstance(e, UploadCancelled) and not self.hub.closed:
                self.event_queue.put(("system", f"Couldn't send {filename}: {e}"))
            return done(False)
        self.event_queue.put(("file", local_file_event(self.name, msg_id, target, filename, size, data, path)))
        done(True)

    def close(self):
        self.hub.closed = True
        self.stop_event.set()
        self.hub.broadcast(HOST_DISCONNECT_PREFIX)
        self.hub.shutdown_all()
        self.local_files.close()
        try: self.server.shutdown(socket.SHUT_RDWR)  # wakes the blocked accept() thread
        except OSError: pass
        try: self.server.close()
        except OSError: pass


class GuestConnection:
    """Connect + handshake happen in __init__ (raising PermissionError or
    ConnectionError on failure). The receive thread only starts once the UI
    calls start(), so no events can arrive before the UI is ready for them."""

    def __init__(self, name, host, port, fernet, event_queue):
        self.name = name
        self.host = host
        self.port = port
        self.fernet = fernet
        self.event_queue = event_queue
        self.local_colors = {}
        self.colors_lock = threading.Lock()
        self.closing = threading.Event()
        self.is_admin = False
        self.host_features = set()  # filled in when the host answers our FEATURES announcement
        self.outbox = None          # created by start(); until then sends are direct (handshake)
        self.assembler = FileAssembler(event_queue)  # receives files sent to us

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.settimeout(5)
            self.sock.connect((host, port))
            self.sock.settimeout(None)
            enable_keepalive(self.sock)
            self._handshake()
        except BaseException:
            self.sock.close()
            raise

    def _handshake(self):
        send_encrypted(self.sock, self.fernet, HELLO_PREFIX + self.name)
        # Right behind the hello, so a host can check this device against its ban list before letting us in. (An older
        # host just reads it as the first message after joining, as it always did.)
        send_encrypted(self.sock, self.fernet, FINGERPRINT_PREFIX + get_machine_fingerprint())
        try:
            length = int.from_bytes(recv_exact(self.sock, MSG_LEN_BYTES), "big")
            if length == 0xFFFFFFFF: raise PermissionError("Password is incorrect.")
            response = self.fernet.decrypt(recv_exact(self.sock, length)).decode("utf-8", errors="surrogatepass")
        except InvalidToken: raise PermissionError("Password is incorrect.")
        except PermissionError: raise
        except Exception: raise ConnectionError("Host disconnected unexpectedly.")

        if response.startswith(BAN_NOTICE_PREFIX):
            until_str, reason, host_name = parse_ban_notice(response[len(BAN_NOTICE_PREFIX):])
            where = f"the chat hosted by {host_name}" if host_name else "this room"
            raise BannedError(f"You are banned from {where} until {until_str}. Reason: {reason}", until_str, reason)
        if response.startswith(NOTICE_PREFIX): raise PermissionError(response[len(NOTICE_PREFIX):])
        if not response.startswith(ROSTER_PREFIX): raise ConnectionError("Invalid handshake from host.")

        self.known_names = {n.strip() for n in response[len(ROSTER_PREFIX):].split(",") if n.strip()}
        self.initial_roster = sorted(self.known_names)

    def _on_outbox_failed(self):
        if not self.closing.is_set():
            self.event_queue.put(("disconnected", "Connection lost."))

    def start(self, unlock_prefix: str = None):
        self.outbox = Outbox(self.sock, on_failed=self._on_outbox_failed)
        threading.Thread(
            target=guest_recv_loop,
            args=(self.sock, self.fernet, self.event_queue, self.local_colors, self.colors_lock, self.known_names, self.host, self.closing, self.host_features, self.assembler),
            daemon=True,
        ).start()
        self._send(FEATURES_PREFIX + ",".join(sorted(HOST_FEATURES)), report=False)
        if unlock_prefix:
            self._send(unlock_prefix + "1", report=False)

    def _send(self, payload: str, report: bool = True, on_sent=None) -> bool:
        """Queues `payload` for the writer thread (returns immediately). `on_sent(ok)`
        fires once it has actually gone out, or been dropped."""
        frame = encode_frame(self.fernet, payload)
        if self.outbox is None:  # handshake phase
            try:
                self.sock.sendall(frame)
                ok = True
            except OSError:
                ok = False
        else:
            ok = self.outbox.put(frame, on_sent)
            if ok:
                return True  # on_sent will be called by the writer
        if not ok and report and not self.closing.is_set():
            self.event_queue.put(("disconnected", "Connection lost."))
        if on_sent is not None:
            on_sent(ok)
        return ok

    def _colors_copy(self) -> dict:
        with self.colors_lock:
            return dict(self.local_colors)

    def _host_supports_edit(self) -> bool:
        if FEATURE_EDIT in self.host_features:
            return True
        self.event_queue.put(("system", "Editing and deleting messages isn't available — the host is running an older version."))
        return False

    def send_edit(self, msg_id: str, new_text: str):
        # No optimistic local update: the host checks permission and echoes the
        # edit to everyone (including us), so what we show always matches the room.
        if self._host_supports_edit():
            self._send(f"{EDIT_PREFIX}{msg_id}|{new_text}")

    def send_delete(self, msg_id: str):
        if self._host_supports_edit():
            self._send(f"{DELETE_PREFIX}{msg_id}")

    def send_react(self, msg_id: str, emoji: str):
        self._send(f"{REACT_PREFIX}{msg_id}|{emoji}|{self.name}", report=False)
        # Optimistic local update — the host's broadcast excludes the original
        # sender (avoids an echo), so without this the reacting guest would
        # never see their own reaction applied.
        self.event_queue.put(("react", {"msg_id": msg_id, "emoji": emoji, "sender": self.name}))

    def send_appeal(self, payload: dict):
        self._send(APPEAL_PREFIX + json.dumps(payload), report=False)

    def send_report(self, msg_id: str, reason: str):
        self._send(f"{REPORT_PREFIX}{msg_id}|{reason}", report=False)

    def send_chat(self, text: str, reply_to: dict = None):
        stripped = text.strip()
        put = self.event_queue.put
        cmd, _, arg = stripped.partition(" ")
        cmd = cmd.lower()

        if cmd == "/help": return put(("system", HELP_TEXT))
        if cmd == "/colors": return put(("system", "Available colors: " + ", ".join(COLOR_PALETTE)))
        if cmd == "/list": return put(("system", "Connected: " + ", ".join(sorted(self.known_names, key=str.lower))))

        if cmd == "/color":
            if not arg.strip(): return put(("system", "Usage: /color <name> — see /colors"))
            self._send(CMD_PREFIX + f"color|{arg.strip()}")
            return

        if cmd == "/nick":
            if not arg.strip(): return put(("system", "Usage: /nick <new name>"))
            self._send(NICK_PREFIX + arg.strip())
            return

        if cmd == "/warnings":
            self._send(CMD_PREFIX + f"warnings|{arg.strip()}")
            return

        if cmd == "/whisper":
            parts = arg.split(maxsplit=1)
            if len(parts) < 2: return put(("system", "Usage: /whisper <name> <message>"))
            if parts[0].lower() == self.name.lower(): return put(("system", "You cannot whisper to yourself!"))
            self._send(f"{WHISPER_PREFIX}{os.urandom(4).hex()}|{parts[0]}|{parts[1]}")
            return

        if cmd in MOD_COMMAND_NAMES:
            if self.is_admin: self._send(CMD_PREFIX + f"mod|{stripped}")
            else: put(("system", "Only admins can use moderation commands."))
            return

        if len(text) > MAX_MESSAGE_CHARS:
            return put(("system", f"That message is too long (the limit is {MAX_MESSAGE_CHARS:,} characters)."))
        msg_id = os.urandom(4).hex()
        full_msg = f"{self.name}: {text}"
        if self._send(f"{MSG_PREFIX}{msg_id}|{full_msg}"):
            put(("chat", {"raw": full_msg, "colors": self._colors_copy(), "msg_id": msg_id}))
            if reply_to:
                put(("reply", {"msg_id": msg_id, "to": reply_to["id"], "author": reply_to["author"], "snippet": reply_to["snippet"]}))
                self._send(f"{REPLYTO_PREFIX}{msg_id}|{reply_to['id']}", report=False)

    def send_typing(self, started: bool):
        self._send((TYPING_START_PREFIX if started else TYPING_STOP_PREFIX) + self.name, report=False)

    def send_game(self, game: str, score: int, playing: bool):
        feature = GAME_FEATURES.get(game)
        if feature and feature not in self.host_features:
            return  # an older host would show the frame as a chat line
        self._send(f"{GAME_PREFIXES[game]}{score}|{1 if playing else 0}", report=False)

    def send_dnd(self, active: bool):
        verb = "turned on" if active else "turned off"
        self.event_queue.put(("system", f"You {verb} Do Not Disturb."))
        self._send(DND_PREFIX + f"{self.name}|{'on' if active else 'off'}", report=False)

    def send_file(self, filepath: str, on_done=None, to: str = None, on_progress=None, cancel=None):
        """Sends a file to everyone, or privately to `to`. Streams big files from disk;
        blocks until the last piece is queued (paced by the connection), so run it off
        the UI thread. `on_done(ok)` fires once the final piece has actually gone out;
        set the `cancel` Event to stop part-way."""
        check_file_size(filepath)
        size, name = os.path.getsize(filepath), os.path.basename(filepath)
        if size <= INLINE_FILE_BYTES:
            with open(filepath, "rb") as f:
                return self.send_file_bytes(name, f.read(), on_done, to, on_progress, cancel)
        self._send_file(name, size, chunks_from_path(filepath), None, filepath, to, on_done, on_progress, cancel)

    def send_file_bytes(self, filename: str, data: bytes, on_done=None, to: str = None, on_progress=None, cancel=None):
        self._send_file(os.path.basename(filename), len(data), chunks_from_bytes(data), data, None, to, on_done, on_progress, cancel)

    def _send_file(self, filename, size, chunks, data, path, to, on_done, on_progress, cancel=None):
        done = on_done or (lambda ok: None)
        if size > MAX_FILE_BYTES:
            self.event_queue.put(("system", f"{filename} is {format_size(size)} — the limit is {FILE_LIMIT_TEXT}."))
            return done(False)
        outbox = self.outbox
        if outbox is None or self.closing.is_set():
            return done(False)
        msg_id = os.urandom(4).hex()
        try:
            for text in iter_file_texts(self.name, msg_id, to or "", filename, size, with_progress(chunks, size, on_progress)):
                # Wait until the writer has drained (so memory stays bounded and the chat stays
                # responsive), then queue the next piece. Waiting in half-second slices means
                # Cancel takes effect promptly even on a slow connection.
                waited = 0.0
                while not outbox.wait_below(TRANSFER_WINDOW_BYTES, 0.5):
                    if outbox.closed or self.closing.is_set():
                        raise ConnectionError("the connection was lost")
                    if cancel is not None and cancel.is_set():
                        raise UploadCancelled()
                    waited += 0.5
                    if waited >= TRANSFER_STALL_SECONDS:
                        raise ConnectionError("the connection stalled")
                if cancel is not None and cancel.is_set() and not text.startswith(FILEEND_PREFIX):
                    raise UploadCancelled()
                last = text.startswith(FILEEND_PREFIX)
                if not outbox.put(encode_frame(self.fernet, text), on_sent=done if last else None, bulk=True):
                    raise ConnectionError("the connection was lost")
        except Exception as e:
            reason = "cancelled by the sender" if isinstance(e, UploadCancelled) else "the sender hit an error"
            outbox.put(encode_frame(self.fernet, f"{FILEABORT_PREFIX}{msg_id}|{reason}"), bulk=True)
            if not isinstance(e, UploadCancelled) and not self.closing.is_set():
                self.event_queue.put(("system", f"Couldn't send {filename}: {e}"))
            return done(False)
        # Show our own copy straight away (the host doesn't echo files back to their sender).
        self.event_queue.put(("file", local_file_event(self.name, msg_id, to or "", filename, size, data, path)))

    def close(self):
        self.closing.set()
        self._send(f"[{self.name} left the chat]", report=False)
        if self.outbox is not None:
            self.outbox.close(after_control=True)  # sends the leave notice, then shuts the socket
            self.outbox.join(0.3)
        # shutdown() so the receive thread (blocked in recv) wakes up and the host
        # actually sees us leave — a bare close() from another thread doesn't.
        try: self.sock.shutdown(socket.SHUT_RDWR)
        except OSError: pass
        try: self.sock.close()
        except OSError: pass
        self.assembler.close()


def make_button(parent, text, command, bg, fg="white", font=None, padx=14, pady=6, hover_bg=None):
    """A flat, label-based button (native Tk buttons ignore bg colors on macOS).
    The returned frame has: .label, .base_bg, .disabled, .paint(color), .set_enabled(bool)."""
    frame = tk.Frame(parent, bg=bg, cursor="hand2")
    label = tk.Label(frame, text=text, bg=bg, fg=fg, font=font or BOLD_FONT, padx=padx, pady=pady)
    label.pack(fill="both", expand=True)

    frame.label = label
    frame.base_bg = bg
    frame.hover_bg = hover_bg   # change both (and .paint) to recolour the button for good
    frame.disabled = False

    def paint(color):
        frame.configure(bg=color)
        label.configure(bg=color)

    def set_enabled(enabled: bool):
        frame.disabled = not enabled
        paint(frame.base_bg if enabled else BG_INPUT)
        label.configure(fg=fg if enabled else FG_MUTED)

    def on_click(event=None):
        if not frame.disabled: command()

    def on_enter(event=None):
        if not frame.disabled: paint(frame.hover_bg)

    def on_leave(event=None):
        if not frame.disabled: paint(frame.base_bg)

    for w in (frame, label):
        w.bind("<Button-1>", on_click)
        if hover_bg:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

    frame.paint, frame.set_enabled = paint, set_enabled
    return frame


def probe_tcp_hosts(ips, port: int = DEFAULT_TCP_PORT, timeout: float = 1.5):
    """TCP-only fallback for when the UDP lookup gets no answer: is a chat host listening on the well-known
    port at any of these addresses? Returns the first (in the order given) that accepts a connection, else None."""
    answered = {}
    def probe(ip):
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                answered[ip] = True
        except OSError:
            pass
    threads = [threading.Thread(target=probe, args=(ip,), daemon=True) for ip in ips]
    for t in threads: t.start()
    for t in threads: t.join(timeout + 0.5)
    return next((ip for ip in ips if answered.get(ip)), None)

def friendly_connect_error(e: Exception, host_ip: str, port: int) -> str:
    text = str(e).lower()
    if isinstance(e, ConnectionRefusedError):
        return (f"{host_ip}:{port} answered, but nothing is listening there — the room may have closed, or its port changed. "
                + ("Ask the host for a fresh Invite Code (/invite)." if ENABLE_INVITE_CODES else "Check the host is still running, then try again."))
    if isinstance(e, (socket.timeout, TimeoutError)) or "timed out" in text:
        return (f"No answer from {host_ip}:{port}. On school or public Wi-Fi, devices are often blocked from talking to each other — "
                "try a phone hotspot, or check you're on the same network as the host.")
    return f"Connection failed: {e}"

def resolve_join_target(room_code, manual_target: str = None):
    """Works out where to connect for a Join. `room_code` is the 6-digit code, or the (ip, port) an Invite Code
    carries. Returns (host_ip, port, unlock_prefix, error_message) — error_message is None on success."""
    unlock_prefix = None
    if manual_target:
        match = GRADIENT_UNLOCK_CODES.get(manual_target.strip().lower())
        if match:
            # Not a real address — a secret code. Join as if the field were empty.
            unlock_prefix, manual_target = match[1], None

    if isinstance(room_code, tuple):  # an Invite Code: the whole address is in it, so there's nothing to look up
        return room_code[0], room_code[1], unlock_prefix, None

    host_ip = port = None
    if manual_target:
        ip_str, sep, port_str = manual_target.partition(":")
        host_ip = ip_str.strip()
        if sep:
            try: port = int(port_str.strip())
            except ValueError:
                return None, None, unlock_prefix, f"'{manual_target}' isn't a valid address. Use an IP like 192.168.1.42, or IP:port if you have both."

    if not ENABLE_WAN_RELAY and not (host_ip and port):
        if host_ip:
            typed_ip = host_ip
            host_ip, port = discover_host(room_code, target_ip=typed_ip)
            if not host_ip and probe_tcp_hosts([typed_ip]):
                host_ip, port = typed_ip, DEFAULT_TCP_PORT
        else:
            # Fast path first: Room Code = last two octets, so try the likely address directly.
            # Try the prefix of every network we're on, not just the default-route one.
            prefixes = []
            for ip in get_local_ips():
                prefix = ".".join(ip.split(".")[:2])
                if prefix not in prefixes: prefixes.append(prefix)
            guesses = [f"{p}.{int(room_code[:3])}.{int(room_code[3:])}" for p in prefixes]
            if guesses:
                host_ip, port = discover_host(room_code, target_ip=set(guesses), timeout=1.5)
            if not host_ip:
                host_ip, port = discover_host(room_code)
            if not host_ip and guesses:  # the UDP lookup got nowhere — try a plain TCP connection to the well-known port
                if found := probe_tcp_hosts(guesses):
                    host_ip, port = found, DEFAULT_TCP_PORT

    if not host_ip:
        return None, None, unlock_prefix, (
            f"Could not find Room {room_code}. Check the host is running and you're on the same network. "
            + ("Still stuck? Ask the host to type /invite in their chat and paste the Invite Code here instead of the Room Code. " if ENABLE_INVITE_CODES
               else "Still stuck? Type the host's IP address in the 'Host IP' box. ") +
            "(School and public Wi-Fi often block devices from finding each other — a phone hotspot gets around that.)")
    return host_ip, port, unlock_prefix, None


class ChatApp(tk.Tk):
    BUILTIN_STICKERS = {"GG": "#57F287", "RIP": "#ED4245", "HELLO": "#5B8CFF", "WOW": "#FEE75C", "BRUH": "#FFA347"}
    REACTION_CHOICES = ("😀", "😂", "❤️", "👍", "🔥", "😢", "😡")
    WARN_YELLOW = ("#B8860B", "#D4A017")   # the ⚠ button's resting colour: warned, no appeal answered yet
    WARN_GREEN = (BTN_GREEN, BTN_GREEN_HOVER)
    WARN_RED = (BTN_RED, BTN_RED_HOVER)
    WARN_WHITE = ("#FFFFFF", "#EEEEEE")
    BASE_COMMANDS = ("/color", "/colors", "/list", "/clear", "/whisper", "/nick", "/warnings") + (("/invite",) if ENABLE_INVITE_CODES else ()) + ("/help",)
    ADMIN_COMMANDS = ("/mute", "/unmute", "/kick", "/ban", "/unban", "/bans", "/warn", "/unwarn", "/history", "/appeals",
                      "/accept", "/reject", "/slowmode", "/admin", "/unadmin")
    PLAYER_ARG_COMMANDS = frozenset({"/mute", "/unmute", "/kick", "/ban", "/warn", "/unwarn", "/warnings", "/history", "/rename", "/whisper", "/admin", "/unadmin"})
    ACTIVITY_RANKED_COMMANDS = frozenset({"/mute", "/kick", "/ban", "/warn"})
    # Keys that never change the text, so they shouldn't refresh suggestions or typing state.
    NON_EDIT_KEYSYMS = frozenset({
        "Tab", "ISO_Left_Tab", "Up", "Down", "Return", "KP_Enter", "Escape", "Caps_Lock",
        "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Meta_L", "Meta_R",
        "Super_L", "Super_R", "Command", "Option_L", "Option_R",
    })
    STATUS_COLORS = {"error": COLOR_PALETTE["red"], "info": COLOR_PALETTE["yellow"], "ok": COLOR_PALETTE["green"]}
    DEFAULT_DND_KEYBIND = "<Control-d>"

    MAX_LOG_LINES = 3000      # older lines are trimmed once the log grows past this
    TRIM_EVERY = 40           # ...checked every N appended lines
    HISTORY_MAX = 50          # sent messages recalled with Up/Down
    MAX_EVENTS_PER_POLL = 200

    def __init__(self):
        super().__init__()
        init_ui_scale(self)
        self.settings = load_json(SETTINGS_FILE, dict)
        self._home_src = None            # the home-screen picture, opened once (see _apply_home_picture)
        self._home_photo = None
        self._appearance_built = False   # True once every widget exists, so a theme change knows to recolour them
        self._gban_entries = None        # the verified global ban list (see _global_ban_tick)
        self._gban_skew = 0.0            # how far the report server's clock is ahead of ours
        self._gban_seq_seen = None       # the list number we last read; None = not read yet this run
        self._gban_entry = None          # the entry banning THIS device right now, or None
        self._gban_overlay = None
        self._gban_pw = None             # the publisher's admin password, for this run only
        self._load_appearance()          # themes and fonts first: every widget below is built in them
        if sys.platform == "win32":
            self.after_idle(lambda: style_titlebar(self))
        self.geometry(f"{px(900)}x{px(600)}")
        self.minsize(px(640), px(420))
        self.configure(bg=BG_DARK)

        # connection
        self.connection = None
        self.my_name = ""
        self.is_admin = False
        self._connecting = False
        self.event_queue = queue.Queue()
        self._host_local_ip = None

        # shared UI plumbing
        self._timers = {}              # key -> pending after() id (see _set_timer)
        self._popups = {}              # key -> open Toplevel (see _open_dialog / _toggle_picker)
        self._picker_anchors = {}      # picker name -> the button that opens it
        self.photo_cache = []          # keeps PhotoImages alive — Tk drops them otherwise
        self.suggest_popup = None
        self._game_wins = {}           # game key -> its open window (they outlive chats: you can play on the home screen)
        self._game_picker = None
        self._last_report_time = 0.0
        self._report_login_failures = 0
        self._pending_manifest = None     # the update the banner on the main menu is offering
        self._reports_last_checked = 0.0  # when this computer last heard from the report server about its reports
        self._announce = None             # the live announcement {seq, text, urgent, issued, hours}, or None
        self._announce_seq_seen = -1      # the newest announcement number the server has told us about
        self._announce_shown_seq = None   # which announcement the banner is showing right now
        self._announce_checked = 0.0
        self._last_announce_manual = 0.0
        self._last_force_refresh = 0.0    # when "Refresh" in My previous reports was last pressed (it's rate limited)
        self._notice_queue, self._notice_active, self._notice_times = [], False, []
        self._rainbow_instance_seq = 0
        self._job_seq = 0
        self._session_id = 0
        self._jump_visible = False
        self._unseen = 0               # messages that arrived out of view since the "New messages" button appeared
        self._jump_sync_pending = False
        self.sent_history, self._history_pos, self._history_draft = [], None, ""
        self._active_dnd_bind = None
        saved_bind = self.settings.get("dnd_keybind")
        self.dnd_keybind = saved_bind if isinstance(saved_bind, str) and saved_bind else self.DEFAULT_DND_KEYBIND
        self._init_session_state()

        self._event_handlers = {
            "connect_success": self._on_connect_success,
            "connect_fail": self._on_connect_fail,
            "room_code_changed": self._on_room_code_changed,
            "chat": self._on_chat_event,
            "react": lambda p: self.add_reaction(p["msg_id"], p["emoji"], p.get("sender", "")),
            "whisper": self.append_whisper_line,
            "rename": self._on_rename,
            "reply": self._on_reply,
            "banned": self._on_banned,
            "banned_live": self._on_banned_live,
            "appeal_result": self._on_appeal_result,
            "ban_status": self._on_ban_status,
            "warned": self._on_warned,
            "game": self._on_game_event,
            "features": lambda _: self._games_context_changed(),
            "warn_state": self._on_warn_state,
            "warn_sync": self._on_warn_sync,
            "report_result": self._on_report_result,
            "bg_done": self._on_bg_done,
            "upload_done": self._on_upload_done,
            "upload_progress": self._on_upload_progress,
            "transfer_progress": self._on_transfer_progress,
            "msg_edit": self._on_msg_edit,
            "msg_delete": self._on_msg_delete,
            "system": self.append_system_line,
            "private": self._on_private_text,
            "roster": self.update_roster,
            "colormap": self._on_colormap_event,
            "typing": self.update_typing,
            "ping": lambda p: notify_ping(p, root=self),
            "file": self.render_incoming_file,
            "disconnected": self._handle_disconnected,
            "kicked": self._on_kicked,
            "mute_notice": self._on_mute_notice,
            "slowmode": self._on_slowmode_event,
            "admin_status": self._on_admin_status,
            "mute_status": self._on_mute_status,
            "update_check_result": self._handle_update_check_result,
            "update_apply_result": self._handle_update_apply_result,
        }

        self._build_connect_frame()
        self._build_chat_frame()
        self._apply_dnd_keybind()
        self._update_window_title()
        self.connect_frame.pack(fill="both", expand=True)
        self._focus_first_empty()

        # The slim notice bar across the very top of the window (new-report alerts) — packed only while it has something to show.
        self.notice_bar = tk.Label(self, text="", bg=BG_PANEL, fg=FG_TEXT, font=fnt(10, "bold"), pady=5)
        # The announcement banner: above everything, on the main menu and in a chat alike, until it's dismissed.
        self.announce_bar = tk.Frame(self, bg=ACCENT)
        self.announce_label = tk.Label(self.announce_bar, text="", bg=ACCENT, fg="white", font=fnt(10, "bold"), justify="left", anchor="w", padx=12, pady=7)
        self.announce_label.pack(side="left", fill="x", expand=True)
        self.announce_close = tk.Label(self.announce_bar, text="✕", bg=ACCENT, fg="white", font=fnt(11, "bold"), cursor="hand2", padx=12)
        self.announce_close.pack(side="right")
        self.announce_close.bind("<Button-1>", lambda e: self._dismiss_announcement())
        self.announce_bar.bind("<Configure>", lambda e: self.announce_label.configure(wraplength=max(200, e.width - 70)))

        self.bind_all(GAMES_KEYBIND, self.on_open_games)
        self.bind_all(APPEARANCE_KEYBIND, lambda e: self._open_appearance())
        self.bind_all(REPORTS_KEYBIND, self.on_open_reports)
        self.bind_all(ANNOUNCEMENTS_KEYBIND, self.on_open_announcements_admin)
        # Quiet background jobs shortly after launch, once the window is up.
        self.after(1500, lambda: self._start_update_check(manual=False))
        self.after(4000, self._check_my_reports)
        self.after(6000, self._start_report_watch)
        self.after(8000, self._start_announcements)
        threading.Thread(target=prune_old_backups, daemon=True).start()
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind_all("<Button-1>", self._on_global_click, add="+")  # click-away closes the in-window pickers
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._appearance_built = True
        self._apply_home_picture()
        cached = load_global_bans_cache()   # a ban holds even with no internet
        if cached:
            self._gban_entries, self._gban_skew = cached["entries"], cached["skew"]
            self.after(200, self._evaluate_global_ban)
        self.after(1200, self._global_ban_tick)
        self.after(50, self.poll_queue)

    def _init_session_state(self):
        """Everything that belongs to one chat session (reset on every join/host)."""
        self.current_roster = []
        self._roster_sig = None
        self.known_colors = {}
        self.known_tags = set()
        self.message_reactions = {}
        self._msg_authors = {}         # msg_id -> author name, for "deleted by ..." wording
        self._my_messages = {}         # msg_id -> current text of messages *I* sent (editable)
        self._attachments = {}         # msg_id -> {"data", "filename", "photo", "mine", "whisper"} for files/images in the log
        self._whisper_ids = set()      # msg_ids of whisper lines (private: no reactions, no admin delete)
        self._session_id += 1          # lets late events from a previous chat be recognised and ignored
        self._reply_to = None          # {"id", "author", "snippet"} while composing a reply
        self._appealed_warnings = set()  # warning numbers we've already appealed
        self._warn_fx = None             # "hold" / "flash" while the ⚠ button plays an effect (see _on_warn_state)
        self._warnings = {}              # warning number -> {"by", "reason", "state"}: every ACTIVE warning we hold (see the ⚠ button)
        self._warn_view = None           # the warning number the warning dialog is showing
        self._appeal_pending = None      # {"number", "key"} while a warning appeal's "Sending…" line awaits the host's answer
        self._room_code = ""
        self._upload_jobs = {}         # job id -> {"name", "to", "pct"} for files we're sending
        self._incoming = {}            # msg_id -> {"filename", "sender", "pct"} for big files arriving
        self.game_boards = {key: {} for key in GAME_KEYS}  # game -> name.lower() -> {"name", "best", "score", "playing"}: the room's live scores
        self.typing_last_seen = {}
        self.user_msg_times = {}       # name.lower() -> recent message timestamps (spam ranking)
        self.user_last_msg_time = {}   # name.lower() -> timestamp of their last message (idle ranking)
        self.typing_active = False
        self.last_typing_sent = 0.0
        self._last_entry_text = ""
        self.dnd_active = False
        self._dnd_cd = 0.0
        self.slowmode_delay = 0.0
        self._slowmode_cd_end = 0.0
        self.current_suggestions = []
        self._unread = 0
        self._appended = 0

    # ------------------------------------------------------------------
    # Small shared helpers
    # ------------------------------------------------------------------

    def _set_timer(self, key, ms, fn):
        """Schedules fn, replacing any pending timer with the same key."""
        self._cancel_timer(key)
        def run():
            self._timers.pop(key, None)
            fn()
        self._timers[key] = self.after(ms, run)

    def _cancel_timer(self, key):
        job = self._timers.pop(key, None)
        if job is not None:
            try: self.after_cancel(job)
            except Exception: pass

    def _close_popup(self, name):
        self._picker_anchors.pop(name, None)
        popup = self._popups.pop(name, None)
        if popup is not None:
            try: popup.destroy()
            except tk.TclError: pass

    def _open_dialog(self, name, title, padx=20, pady=16, resizable=False):
        """A single-instance dialog (Esc / the window's X close it). Returns the
        new Toplevel, or None if one is already open (which is raised instead)."""
        existing = self._popups.get(name)
        if existing is not None:
            try:
                existing.lift()
                existing.focus_force()
            except tk.TclError:
                pass
            return None
        popup = Toplevel(self)
        popup.title(title)
        popup.configure(bg=BG_PANEL, padx=padx, pady=pady)
        popup.resizable(resizable, resizable)
        popup.transient(self)
        popup.protocol("WM_DELETE_WINDOW", lambda: self._close_popup(name))
        popup.bind("<Escape>", lambda e: self._close_popup(name))
        self._popups[name] = popup
        popup.focus_set()
        return popup

    def _toggle_picker(self, name, anchor, build):
        """A panel that opens just above `anchor`, inside the main window. (A separate
        borderless window steals keyboard focus on some platforms and can leave the
        chat box dead until the app is minimised and restored — here the entry never
        loses focus.) Closes on Esc, on a click anywhere else, or on its button again."""
        if name in self._popups:
            return self._close_popup(name)
        for other in ("emoji", "stickers"):
            self._close_popup(other)
        popup = tk.Frame(self.chat_frame, bg=BG_PANEL, bd=1, relief="solid", padx=6, pady=6)
        self._popups[name] = popup
        self._picker_anchors[name] = anchor
        build(popup)
        popup.update_idletasks()
        frame = self.chat_frame
        x = anchor.winfo_rootx() - frame.winfo_rootx()
        x = max(0, min(x, frame.winfo_width() - popup.winfo_reqwidth()))
        y = max(0, anchor.winfo_rooty() - frame.winfo_rooty() - popup.winfo_reqheight() - 6)
        popup.place(x=x, y=y)
        popup.lift()

    @staticmethod
    def _within(widget_path: str, container) -> bool:
        path = str(container)
        return widget_path == path or widget_path.startswith(path + ".")

    def _on_global_click(self, event):
        clicked = str(event.widget)
        for name in ("emoji", "stickers"):
            popup = self._popups.get(name)
            if popup is None:
                continue
            anchor = self._picker_anchors.get(name)
            if not (self._within(clicked, popup) or (anchor is not None and self._within(clicked, anchor))):
                self._close_popup(name)
        if self.suggest_popup is not None and not (self._within(clicked, self.suggest_popup) or clicked == str(self.msg_entry)):
            self.destroy_suggestions()

    @contextmanager
    def _log_edit(self):
        self.log.configure(state="normal")
        try: yield
        finally: self.log.configure(state="disabled")

    @contextmanager
    def _log_append(self, force_scroll=False):
        """Edit the log, then scroll to the end only if the reader was already
        at the bottom (or force_scroll) — so reading history isn't interrupted."""
        follow = force_scroll or self._at_bottom()
        with self._log_edit():
            yield
        if follow:
            self.log.see("end")
            self._hide_jump()
        else:
            self._show_jump()
            # Layout may not have caught up with the insert (common right after a
            # room starts) — re-check once it has, so a stale reading can't leave
            # the button stuck on while you're actually at the bottom.
            self.after(80, self._sync_jump_btn)
        self._appended += 1
        if follow and self._appended % self.TRIM_EVERY == 0:
            self._trim_log()

    def _at_bottom(self, precise: bool = False) -> bool:
        """Is the reader looking at the end of the log? `precise` first lets Tk finish pending layout —
        slower, so it's used only for the delayed re-checks, not on every appended line.
        The last line counts as in view when it's fully on screen (or the view fraction reaches 1)."""
        if not self.log.winfo_ismapped():
            return True  # not on screen yet (e.g. the room is still starting) — nothing to be "behind" on
        if precise:
            self.log.update_idletasks()
            info = self.log.dlineinfo("end-1c")
            if info is not None and info[1] + info[3] <= self.log.winfo_height() + 1:
                return True
        return self.log.yview()[1] >= 0.999

    def _on_log_yscroll(self, first, last):
        """Tk calls this whenever the log's visible range changes, however it changed."""
        self.log.vbar.set(first, last)
        if self._jump_visible and not self._jump_sync_pending:
            self._jump_sync_pending = True
            self.after_idle(self._sync_jump_btn)

    def _wheel_over_jump_btn(self, event):
        if event.num == 4: units = -3
        elif event.num == 5: units = 3
        elif sys.platform == "darwin": units = -event.delta  # macOS reports small per-notch deltas
        else: units = -int(event.delta / 120) * 3
        if units:
            self.log.yview_scroll(units, "units")
        return "break"

    def _show_jump(self):
        """Something new arrived out of view: show the button, with how many (called once per arrival)."""
        if not self.log.winfo_ismapped():
            return
        self._unseen += 1
        self.jump_btn.configure(text="↓ 1 new message" if self._unseen == 1 else f"↓ {self._unseen} new messages")
        if not self._jump_visible:
            self.jump_btn.pack(side="right", padx=14, pady=(3, 5))
            self._jump_visible = True

    def _hide_jump(self):
        self._unseen = 0
        if self._jump_visible:
            self.jump_btn.pack_forget()
            self.jump_bar.configure(height=1)  # an emptied frame would otherwise keep the button's height as dead space
            self._jump_visible = False

    def _scroll_to_bottom(self):
        self.log.see("end")
        self._hide_jump()

    def _sync_jump_btn(self):
        """Hides the button once the reader has got back to the end of the log, by any route."""
        self._jump_sync_pending = False
        if self._jump_visible and self._at_bottom(precise=True):
            self._hide_jump()

    def _trim_log(self):
        excess = int(self.log.index("end-1c").split(".")[0]) - self.MAX_LOG_LINES
        if excess <= 0:
            return
        with self._log_edit():
            self.log.delete("1.0", f"{excess + 1}.0")
        # Marks inside a deleted range collapse to its start — drop the stranded
        # reaction anchors so late reactions to trimmed messages are ignored.
        for mark in self.log.mark_names():
            if mark.startswith("react_mark_") and self.log.compare(mark, "==", "1.0"):
                self.log.mark_unset(mark)
        self._prune_attachments()

    def _prune_attachments(self):
        """Forget attachments whose lines are no longer in the log (trimmed or cleared)
        so their bytes and previews can be freed."""
        for msg_id in [m for m in self._attachments if not self.log.tag_ranges(f"attach_{m}")]:
            self._release_attachment(self._attachments.pop(msg_id))

    def _release_attachment(self, attachment):
        photo = attachment.get("photo")
        if photo is not None and photo in self.photo_cache:
            self.photo_cache.remove(photo)
        if attachment.get("temp") and attachment.get("path"):  # big files received to disk — free the space
            try: os.remove(attachment["path"])
            except OSError: pass
            attachment["path"] = None

    def _set_status(self, text, kind="error"):
        self.status_label.configure(text=text, fg=self.STATUS_COLORS[kind])

    def _update_window_title(self):
        prefix = f"({self._unread}) " if self._unread else ""
        self.title(f"{prefix}chat_gui.py v{VERSION}")

    def _note_unread(self):
        try: unfocused = self.focus_displayof() is None
        except Exception: unfocused = False
        if unfocused:
            self._unread += 1
            self._update_window_title()

    def _on_focus_in(self, event=None):
        if self._unread:
            self._unread = 0
            self._update_window_title()

    def _save_settings(self):
        self.settings.update(
            name=self.my_name or self.name_entry.get().strip(),
            mode=self.mode_var.get(),
            dnd_keybind=self.dnd_keybind,
        )
        save_json(SETTINGS_FILE, self.settings)


    # ------------------------------------------------------------------
    # Appearance: themes, fonts, home picture  (this computer only)
    # ------------------------------------------------------------------

    _COLOR_OPTIONS = ("background", "foreground", "activebackground", "activeforeground", "highlightbackground", "highlightcolor",
                      "selectbackground", "selectforeground", "selectcolor", "troughcolor", "readonlybackground",
                      "disabledbackground", "disabledforeground", "insertbackground")
    # The accent only ever appears as a *background* (buttons, banners, selections, the focus ring). A name or status colour
    # can be exactly the same blue as text, so text colours never follow the accent.
    _ACCENT_OPTIONS = frozenset({"background", "activebackground", "selectbackground", "highlightcolor"})
    _TAG_COLOR_OPTIONS = ("foreground", "background", "selectforeground", "selectbackground", "underlinefg", "overstrikefg")

    def _load_appearance(self):
        """Runs before any widget exists: puts the saved theme and font into the module's constants."""
        self.appearance = sanitize_appearance(self.settings.get("appearance"))
        apply_theme_globals(theme_for(self.appearance))
        apply_font_globals(self.appearance["font_family"], self.appearance["font_size"])
        self._setup_option_db()

    def _setup_option_db(self):
        """Defaults for widgets created from now on: a thin border that matches the field (so the bright system border
        around every text box is gone) and turns into an accent ring when the field has focus. (macOS already looks right.)"""
        if sys.platform == "darwin":
            return
        add = lambda pattern, value: self.option_add(pattern, value, 60)
        for kind in ("Entry", "Text", "Listbox", "Spinbox"):
            add(f"*{kind}.highlightThickness", 1)
            add(f"*{kind}.highlightBackground", BG_INPUT)
            add(f"*{kind}.highlightColor", ACCENT)
        for kind in ("Radiobutton", "Checkbutton"):
            add(f"*{kind}.highlightThickness", 0)
            add(f"*{kind}.borderWidth", 0)

    def _apply_appearance(self, new_cfg, save=True):
        """Switches theme/font/picture right now, on screen, and remembers the choice."""
        cfg = sanitize_appearance(new_cfg)
        old_theme, old_family, old_delta = dict(CURRENT_THEME), CHAT_FONT[0], FONT_DELTA
        new_theme = theme_for(cfg)
        apply_theme_globals(new_theme)
        apply_font_globals(cfg["font_family"], cfg["font_size"])
        self.appearance = cfg
        self._setup_option_db()
        if self._appearance_built:
            full = {old_theme[r].lower(): new_theme[r] for r in THEME_ROLES if old_theme[r].lower() != new_theme[r].lower()}
            plain = {k: v for k, v in full.items() if k not in (old_theme["accent"].lower(), old_theme["accent_hover"].lower())}
            remap = None
            if CHAT_FONT[0] != old_family or FONT_DELTA != old_delta:
                remap = self._font_remapper(old_family, CHAT_FONT[0], FONT_DELTA - old_delta)
            if full or remap:
                self._retheme_tree(self, full, plain, remap)
            self._apply_home_picture()
            self._restyle_titlebars()
        if save:
            self.settings["appearance"] = cfg
            save_json(SETTINGS_FILE, self.settings)

    def _restyle_titlebars(self):
        if sys.platform != "win32":
            return
        for win in [self] + [w for w in self.winfo_children() if isinstance(w, tk.Toplevel)]:
            try: style_titlebar(win)
            except tk.TclError: pass

    def _font_remapper(self, old_family, new_family, delta):
        """-> a function mapping any Tk font spec to (new family, resized, same bold/italic), or None when the spec isn't
        in the old text font (emoji and other special fonts are left alone)."""
        cache = {}
        try: actual_old = str(self.tk.call("font", "actual", (old_family, 10), "-family"))
        except tk.TclError: actual_old = old_family
        def remap(spec):
            spec = str(spec)
            if not spec:
                return None
            if spec in cache:
                return cache[spec]
            result = None
            try:
                parts = self.tk.splitlist(self.tk.call("font", "actual", spec))
                info = dict(zip(parts[0::2], parts[1::2]))
            except (tk.TclError, ValueError):
                info = {}
            if str(info.get("-family")) == actual_old:
                try: size = int(info.get("-size", 0))
                except ValueError: size = 0
                if size > 0:
                    styles = []
                    if str(info.get("-weight")) == "bold": styles.append("bold")
                    if str(info.get("-slant")) == "italic": styles.append("italic")
                    if str(info.get("-underline")) == "1": styles.append("underline")
                    if str(info.get("-overstrike")) == "1": styles.append("overstrike")
                    result = (new_family, max(6, size + delta), *styles)
            cache[spec] = result
            return result
        return remap

    def _retheme_tree(self, widget, full, plain, remap_font):
        if getattr(widget, "_no_retheme", False):   # e.g. the theme swatches, which show other themes' colours on purpose
            return
        self._retheme_widget(widget, full, plain, remap_font)
        for child in widget.winfo_children():
            self._retheme_tree(child, full, plain, remap_font)

    def _retheme_widget(self, widget, full, plain, remap_font):
        try: keys = set(widget.keys())
        except (tk.TclError, AttributeError): keys = set()
        if full:
            for opt in self._COLOR_OPTIONS:
                if opt not in keys:
                    continue
                try: current = str(widget.cget(opt)).lower()
                except tk.TclError: continue
                new = (full if opt in self._ACCENT_OPTIONS else plain).get(current)
                if new:
                    try: widget.configure(**{opt: new})
                    except tk.TclError: pass
            for attr in ("base_bg", "hover_bg"):   # make_button's remembered colours
                value = getattr(widget, attr, None)
                if isinstance(value, str) and value.lower() in full:
                    setattr(widget, attr, full[value.lower()])
        if remap_font and "font" in keys:
            try: new_font = remap_font(widget.cget("font"))
            except tk.TclError: new_font = None
            if new_font:
                try: widget.configure(font=new_font)
                except tk.TclError: pass
        if isinstance(widget, tk.Text):
            try: tags = widget.tag_names()
            except tk.TclError: tags = ()
            for tag in tags:
                if full:
                    for opt in self._TAG_COLOR_OPTIONS:
                        try: current = str(widget.tag_cget(tag, opt)).lower()
                        except tk.TclError: continue
                        new = (full if opt == "background" else plain).get(current) if current else None
                        if new:
                            try: widget.tag_configure(tag, **{opt: new})
                            except tk.TclError: pass
                if remap_font:
                    try: new_font = remap_font(widget.tag_cget(tag, "font"))
                    except tk.TclError: new_font = None
                    if new_font:
                        try: widget.tag_configure(tag, font=new_font)
                        except tk.TclError: pass
        retheme = getattr(widget, "retheme", None)
        if callable(retheme):
            try: retheme()
            except tk.TclError: pass

    # ---- the picture behind the main menu ----

    def _style_corner_links(self, over_picture: bool):
        """The links in the bottom-right corner sit on the plain background as before; over a picture they get a small panel
        behind them so they stay readable."""
        widgets = getattr(self, "_corner_widgets", None)
        if not widgets:
            return
        frame, *labels = widgets
        bg = BG_PANEL if over_picture else BG_DARK
        frame.configure(bg=bg, padx=px(10) if over_picture else 0, pady=px(5) if over_picture else 0)
        for label in labels:
            label.configure(bg=bg)

    def _apply_home_picture(self):
        label = getattr(self, "home_pic_label", None)
        if label is None:
            return
        self._style_corner_links(False)
        if not (self.appearance.get("home_image") and Image is not None and os.path.exists(HOME_IMAGE_FILE)):
            label.place_forget()
            label.configure(image="")
            self._home_photo = self._home_src = None
            return
        w, h = self.connect_frame.winfo_width(), self.connect_frame.winfo_height()
        if w < 60 or h < 60:
            w, h = px(900), px(600)
        try:
            from PIL import ImageOps
            if self._home_src is None:
                self._home_src = Image.open(HOME_IMAGE_FILE).convert("RGB")
            self._home_photo = ImageTk.PhotoImage(ImageOps.fit(self._home_src, (w, h), Image.LANCZOS))
        except Exception:
            label.place_forget()
            return
        label.configure(image=self._home_photo)
        label.place(x=0, y=0, relwidth=1, relheight=1)
        label.lower()
        self._style_corner_links(True)

    def _set_home_picture(self, path):
        """Copies the chosen picture next to the app (shrunk to screen size) so it still works if the original is moved."""
        if Image is None:
            raise ValueError("Pictures need the Pillow library, which isn't installed.")
        from PIL import ImageOps
        try:
            img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
        except Exception:
            raise ValueError("That file couldn't be opened as a picture.")
        img.thumbnail((2560, 1600))
        try:
            img.save(HOME_IMAGE_FILE, "JPEG", quality=88)
        except OSError as e:
            raise ValueError(f"Couldn't save the picture: {e}")
        self._home_src = None
        new = dict(self.appearance, home_image=True)
        self._apply_appearance(new)

    # ---- the Appearance window ----

    def _open_appearance(self):
        popup = self._open_dialog("appearance", "Appearance", padx=0, pady=0, resizable=True)
        if popup is None:
            return
        popup.minsize(px(420), px(300))
        # Everything sits in a scrolling area, so on a short screen (or with the Dock in the way) the bottom is still reachable,
        # and the window can be dragged bigger or smaller.
        shell = tk.Frame(popup, bg=BG_PANEL)
        shell.pack(fill="both", expand=True)
        canvas = tk.Canvas(shell, bg=BG_PANEL, highlightthickness=0, bd=0, width=px(470), height=px(300))
        if sys.platform == "darwin":
            scroll = tk.Scrollbar(shell, command=canvas.yview)
        else:
            scroll = FlatScrollbar(shell, bg=BG_PANEL)
            scroll.command = canvas.yview
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        body = tk.Frame(canvas, bg=BG_PANEL, padx=px(22), pady=px(18))
        body_id = canvas.create_window(0, 0, window=body, anchor="nw")
        body.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(body_id, width=e.width))
        def wheel(event):
            if str(event.widget).startswith(str(box)):   # the font list scrolls itself
                return
            step = -1 if (getattr(event, "delta", 0) > 0 or event.num == 4) else 1
            canvas.yview_scroll(step * (1 if sys.platform == "darwin" else 2), "units")
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            popup.bind(sequence, wheel)
        tk.Label(body, text="🎨  Appearance", bg=BG_PANEL, fg=FG_TEXT, font=fnt(14, "bold")).pack(anchor="w")
        tk.Label(body, text="Just for this computer — nobody else sees your choices, and they're remembered next time.",
                 bg=BG_PANEL, fg=FG_MUTED, font=fnt(9), wraplength=px(440), justify="left").pack(anchor="w", pady=(4, 10))

        def change(**fields):
            self._apply_appearance(dict(self.appearance, **fields))
            refresh()

        def heading(text, top=10):
            tk.Label(body, text=text, bg=BG_PANEL, fg=FG_MUTED, font=fnt(8, "bold")).pack(anchor="w", pady=(top, 2))

        # -- theme swatches --
        heading("THEME", top=0)
        grid = tk.Frame(body, bg=BG_PANEL)
        grid.pack(anchor="w")
        swatches = {}
        entries = [(key, label, pal) for key, (label, pal) in THEME_PRESETS.items()] + [("custom", "Custom", None)]
        for i, (key, label, pal) in enumerate(entries):
            sw = tk.Frame(grid, highlightthickness=2, cursor="hand2", width=px(104), height=px(56))
            sw._no_retheme = True
            sw.grid(row=i // 4, column=i % 4, padx=3, pady=3)
            sw.pack_propagate(False)
            name = tk.Label(sw, text=label, font=fnt(9, "bold"), anchor="w", padx=6)
            name.pack(anchor="w", pady=(6, 0), fill="x")
            chips = tk.Frame(sw)
            chips.pack(anchor="w", padx=6, pady=(4, 0))
            chip_widgets = [tk.Frame(chips, width=px(20), height=px(9)) for _ in range(3)]
            for chip in chip_widgets:
                chip.pack(side="left", padx=(0, 3))
            for w in (sw, name, chips, *chip_widgets):
                w._no_retheme = True
                w.bind("<Button-1>", lambda e, key=key: change(theme=key))
            swatches[key] = (sw, name, chips, chip_widgets, pal)

        custom_row = tk.Frame(body, bg=BG_PANEL)
        custom_chips = {}
        def pick(which, title):
            current = theme_for(self.appearance)["bg" if which == "custom_bg" else "accent"]
            _rgb_value, chosen = colorchooser.askcolor(color=current, title=title, parent=popup)
            if chosen:
                change(theme="custom", **{which: chosen.upper()})
        for col, (which, label) in enumerate((("custom_bg", "Background"), ("custom_accent", "Accent"))):
            tk.Label(custom_row, text=label, bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).grid(row=0, column=col * 3, padx=(0 if col == 0 else 18, 6))
            chip = tk.Frame(custom_row, width=px(34), height=px(20), highlightthickness=1, cursor="hand2")
            chip._no_retheme = True
            chip.grid(row=0, column=col * 3 + 1)
            chip.bind("<Button-1>", lambda e, which=which, label=label: pick(which, f"{label} colour"))
            make_button(custom_row, "Pick…", lambda which=which, label=label: pick(which, f"{label} colour"),
                        bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=10, pady=2, font=fnt(9)).grid(row=0, column=col * 3 + 2, padx=(6, 0))
            custom_chips[which] = chip
        tk.Label(custom_row, text="Backgrounds stay fairly dark and light accents get a little darker, so text stays readable.",
                 bg=BG_PANEL, fg=FG_MUTED, font=fnt(8), wraplength=px(440), justify="left").grid(row=1, column=0, columnspan=6, sticky="w", pady=(4, 0))

        # -- font --
        heading("TEXT", top=12)
        tk.Label(body, text="Only fonts installed on this computer are listed.", bg=BG_PANEL, fg=FG_MUTED, font=fnt(8)).pack(anchor="w")
        search_var = tk.StringVar()
        search = tk.Entry(body, textvariable=search_var, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", font=CHAT_FONT)
        search.pack(fill="x", pady=(4, 4), ipady=(0 if sys.platform == "darwin" else px(3)))
        list_frame = tk.Frame(body, bg=BG_INPUT)
        list_frame.pack(fill="x")
        box = tk.Listbox(list_frame, height=6, width=38, bg=BG_INPUT, fg=FG_TEXT, selectbackground=ACCENT, selectforeground="white",
                         relief="flat", font=CHAT_FONT, activestyle="none", exportselection=False, highlightthickness=0)
        if sys.platform == "darwin":
            bar = tk.Scrollbar(list_frame, command=box.yview)
        else:
            bar = FlatScrollbar(list_frame, bg=BG_INPUT)
            bar.command = box.yview
        box.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        box.pack(side="left", fill="x", expand=True)
        families = system_font_families(self)
        shown = []   # (list row text, family value) for what's in the box right now
        def fill_fonts(*_):
            needle = search_var.get().strip().lower()
            shown.clear()
            if not needle or needle in "default":
                shown.append((f"Default  ({DEFAULT_FONT_FAMILY})", ""))
            shown.extend((f, f) for f in families if needle in f.lower())
            box.delete(0, "end")
            for text, _value in shown:
                box.insert("end", text)
            chosen = self.appearance["font_family"]
            for i, (_text, value) in enumerate(shown):
                if value == chosen:
                    box.selection_set(i)
                    box.see(i)
                    break
        def on_font_pick(_event=None):
            sel = box.curselection()
            if sel and shown[sel[0]][1] != self.appearance["font_family"]:
                change(font_family=shown[sel[0]][1])
        box.bind("<<ListboxSelect>>", on_font_pick)
        search_var.trace_add("write", fill_fonts)
        fill_fonts()

        size_row = tk.Frame(body, bg=BG_PANEL)
        size_row.pack(anchor="w", pady=(8, 0))
        tk.Label(size_row, text="Size", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(side="left", padx=(0, 10))
        def nudge(step):
            size = (self.appearance["font_size"] or DEFAULT_FONT_SIZE) + step
            size = max(FONT_SIZE_RANGE[0], min(FONT_SIZE_RANGE[1], size))
            change(font_size=0 if size == DEFAULT_FONT_SIZE else size)
        make_button(size_row, "−", lambda: nudge(-1), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=12, pady=2).pack(side="left")
        size_label = tk.Label(size_row, text="", bg=BG_PANEL, fg=FG_TEXT, font=BOLD_FONT, width=7)
        size_label.pack(side="left")
        make_button(size_row, "+", lambda: nudge(1), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=12, pady=2).pack(side="left")
        make_button(size_row, "Reset text", lambda: change(font_family="", font_size=0), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER,
                    padx=10, pady=2, font=fnt(9)).pack(side="left", padx=(14, 0))

        preview = tk.Frame(body, bg=BG_DARK, padx=10, pady=8)
        preview.pack(fill="x", pady=(10, 0))
        line = tk.Frame(preview, bg=BG_DARK)
        line.pack(anchor="w")
        tk.Label(line, text="[12:30]", bg=BG_DARK, fg=FG_MUTED, font=fnt(8)).pack(side="left")
        tk.Label(line, text=" Richy:", bg=BG_DARK, fg=COLOR_PALETTE["green"], font=BOLD_FONT).pack(side="left")
        tk.Label(line, text=" The quick brown fox jumps over the lazy dog", bg=BG_DARK, fg=FG_TEXT, font=CHAT_FONT).pack(side="left")
        tk.Label(preview, text="* A system message looks like this *", bg=BG_DARK, fg=FG_MUTED, font=fnt(9, "italic")).pack(anchor="w")

        # -- home picture --
        heading("MAIN MENU PICTURE", top=12)
        pic_row = tk.Frame(body, bg=BG_PANEL)
        pic_row.pack(anchor="w")
        pic_status = tk.Label(body, text="", bg=BG_PANEL, fg=FG_MUTED, font=fnt(9), wraplength=px(440), justify="left")
        def choose_picture():
            path = filedialog.askopenfilename(parent=popup, title="Choose a picture",
                                              filetypes=[("Pictures", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("All files", "*.*")])
            if not path:
                return
            try: self._set_home_picture(path)
            except ValueError as e:
                pic_status.configure(text=str(e), fg=COLOR_PALETTE["red"])
                return
            refresh()
        make_button(pic_row, "Choose picture…", choose_picture, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=12, pady=4).pack(side="left")
        remove_btn = make_button(pic_row, "Remove", lambda: change(home_image=False), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=12, pady=4)
        remove_btn.pack(side="left", padx=(8, 0))
        pic_status.pack(anchor="w", pady=(4, 0))
        tk.Label(body, text="It's shown behind the main menu. The chat itself keeps a plain background so messages stay readable.",
                 bg=BG_PANEL, fg=FG_MUTED, font=fnt(8), wraplength=px(440), justify="left").pack(anchor="w")

        buttons = tk.Frame(body, bg=BG_PANEL)
        buttons.pack(fill="x", pady=(14, 0))
        make_button(buttons, "Done", lambda: self._close_popup("appearance"), bg=ACCENT, hover_bg=ACCENT_HOVER, padx=22, pady=5).pack(side="right")
        make_button(buttons, "Reset everything", lambda: (self._set_default_appearance(), refresh()), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER,
                    padx=14, pady=5).pack(side="right", padx=(0, 8))

        def refresh():
            cfg = self.appearance
            effective = theme_for(cfg)
            for key, (sw, name, chips, chip_widgets, pal) in swatches.items():
                pal = pal or make_theme(cfg["custom_bg"], cfg["custom_accent"])
                sw.configure(bg=pal["bg"], highlightbackground=ACCENT if cfg["theme"] == key else BG_PANEL, highlightcolor=ACCENT)
                name.configure(bg=pal["bg"], fg=pal["text"])
                chips.configure(bg=pal["bg"])
                for chip, color in zip(chip_widgets, (pal["panel"], pal["input"], pal["accent"])):
                    chip.configure(bg=color)
            if cfg["theme"] == "custom":
                custom_row.pack(anchor="w", pady=(6, 0), after=grid)
            else:
                custom_row.pack_forget()
            custom_chips["custom_bg"].configure(bg=effective["bg"], highlightbackground=FG_MUTED)
            custom_chips["custom_accent"].configure(bg=effective["accent"], highlightbackground=FG_MUTED)
            size_label.configure(text=f"{cfg['font_size'] or DEFAULT_FONT_SIZE} pt")
            if cfg["home_image"]: remove_btn.pack(side="left", padx=(8, 0))
            else: remove_btn.pack_forget()
            if not pic_status.cget("fg") == COLOR_PALETTE["red"]:
                pic_status.configure(text="")
            popup.update_idletasks()
        refresh()
        # open at the natural size, but never taller than the screen leaves room for (menu bar and Dock)
        popup.update_idletasks()
        room = popup.winfo_screenheight() - px(190)
        canvas.configure(width=body.winfo_reqwidth(), height=min(body.winfo_reqheight(), room))
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _set_default_appearance(self):
        try: os.remove(HOME_IMAGE_FILE)
        except OSError: pass
        self._home_src = None
        self._apply_appearance(dict(DEFAULT_APPEARANCE))

    # ------------------------------------------------------------------
    # Connect screen
    # ------------------------------------------------------------------

    def _build_connect_frame(self):
        f = tk.Frame(self, bg=BG_DARK)
        self.connect_frame = f
        # Optional picture behind the card (Appearance). Created first, so everything else sits on top of it.
        self.home_pic_label = tk.Label(f, bd=0, highlightthickness=0, bg=BG_DARK)
        f.bind("<Configure>", lambda e: self._set_timer("home_pic", 150, self._apply_home_picture) if self.appearance.get("home_image") else None)

        card = tk.Frame(f, bg=BG_PANEL, padx=px(32), pady=px(28))
        card.place(relx=0.5, rely=0.5, anchor="center")

        corner_frame = tk.Frame(f, bg=BG_DARK)
        corner_frame.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-8)
        link_font = fnt(8, "underline")
        changelog_label = tk.Label(corner_frame, text="View Changelog", bg=BG_DARK, fg=FG_MUTED, font=link_font, cursor="hand2")
        changelog_label.pack(anchor="e", pady=(0, 2))
        changelog_label.bind("<Button-1>", lambda e: self.on_show_changelog())
        version_label = tk.Label(corner_frame, text=f"v{VERSION} — Check for Updates", bg=BG_DARK, fg=FG_MUTED, font=link_font, cursor="hand2")
        version_label.pack(anchor="e")
        version_label.bind("<Button-1>", lambda e: self.on_check_updates())
        self._corner_widgets = (corner_frame, changelog_label, version_label)

        # Sits across the top of the main menu whenever there's something to say about updates (see _set_update_banner).
        self.update_banner = tk.Frame(f, bg=BG_PANEL, padx=14, pady=8)
        self.update_banner_label = tk.Label(self.update_banner, text="", bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT, anchor="w", justify="left", wraplength=px(560))
        self.update_banner_label.pack(side="left")
        self.update_banner_buttons = tk.Frame(self.update_banner, bg=BG_PANEL)
        self.update_banner_buttons.pack(side="right")

        tk.Label(card, text="chat_gui", font=fnt(20, "bold"), bg=BG_PANEL, fg=FG_TEXT).grid(row=0, column=0, columnspan=3, pady=(0, 16))

        saved_mode = self.settings.get("mode")
        self.mode_var = tk.StringVar(value=saved_mode if saved_mode in ("host", "join") else "host")
        mode_row = tk.Frame(card, bg=BG_PANEL)
        mode_row.grid(row=1, column=0, columnspan=3, pady=(0, 12))
        for text, val in (("Host a chat", "host"), ("Join a chat", "join")):
            tk.Radiobutton(
                mode_row, text=text, variable=self.mode_var, value=val, bg=BG_PANEL, fg=FG_TEXT,
                selectcolor=BG_INPUT, activebackground=BG_PANEL, activeforeground=FG_TEXT, font=CHAT_FONT, cursor="hand2",
            ).pack(side="left", padx=8)

        def field(row, label, validate_cmd=None, entry_width=28, show=None):
            label_widget = tk.Label(card, text=label, bg=BG_PANEL, fg=FG_MUTED, anchor="w", font=CHAT_FONT)
            label_widget.grid(row=row, column=0, sticky="w", pady=(6, 0))
            kwargs = {"validate": "key", "validatecommand": validate_cmd} if validate_cmd else {}
            if show: kwargs["show"] = show
            entry = tk.Entry(
                card, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", width=entry_width, font=CHAT_FONT,
                # Tk uses a separate bg for state="readonly"; left unset it's a
                # near-white system color that makes light text unreadable.
                readonlybackground=BG_INPUT, **kwargs,
            )
            entry.grid(row=row, column=1, sticky="ew", pady=(6, 0), padx=(10, 0), ipady=(0 if sys.platform == "darwin" else px(3)))
            entry.bind("<Return>", lambda e: self.on_connect_clicked())
            entry.label = label_widget
            return entry

        card.grid_columnconfigure(1, weight=1)

        self.name_entry = field(2, "Display name", validate_cmd=(self.register(lambda p: " " not in p and "|" not in p and len(p) <= 30), "%P"))
        saved_name = self.settings.get("name")
        if isinstance(saved_name, str) and saved_name:
            self.name_entry.insert(0, saved_name[:30])

        # Recent chats (Join mode only): quick-fill from past successful
        # connections. Hidden entirely when there's nothing to show.
        self.recent_frame = tk.Frame(card, bg=BG_PANEL)
        self.recent_frame.grid(row=3, column=0, columnspan=3, sticky="ew")
        tk.Label(self.recent_frame, text="Recent", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(anchor="w", pady=(6, 2))
        self.recent_list_frame = tk.Frame(self.recent_frame, bg=BG_PANEL)
        self.recent_list_frame.pack(fill="x")

        # Room Code (6 digits) or Invite Code (11 letters/numbers, usually written with dashes). Spaces and dashes are
        # allowed so a pasted "123 456" or "7K2M-9QXA-R5B" isn't rejected on the spot; it's tidied up when you connect.
        room_chars = (self.register(lambda p: len(p) <= 20 and all((ch.isalnum() if ENABLE_INVITE_CODES else ch.isdecimal()) or ch in " -." for ch in p)), "%P")
        self.room_entry = field(4, "Room Code", validate_cmd=room_chars, entry_width=20)
        self.regen_room_btn = make_button(card, "Refresh", self._regenerate_room_code, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=8, pady=4, font=CHAT_FONT)
        self.regen_room_btn.grid(row=4, column=2, sticky="w", padx=(8, 0), pady=(6, 0))

        self.host_ip_entry = field(5, "Host IP (only if Room Code fails)")
        self.key_entry = field(6, "Shared key", show="*")

        self.status_label = tk.Label(card, text="", bg=BG_PANEL, fg=self.STATUS_COLORS["error"], wraplength=px(300), justify="left", font=CHAT_FONT)
        self.status_label.grid(row=7, column=0, columnspan=3, sticky="w", pady=(10, 0))

        self.connect_btn = make_button(card, "Connect", self.on_connect_clicked, bg=BTN_GREEN, hover_bg=BTN_GREEN_HOVER)
        self.connect_btn.grid(row=8, column=0, columnspan=3, pady=(16, 0), sticky="ew")
        self._ban_ctx = None  # what the appeal needs, while we're showing a ban message
        self.appeal_btn = make_button(card, "APPEAL BAN", self._open_ban_appeal, bg=BTN_RED, hover_bg=BTN_RED_HOVER)
        self.appeal_btn.grid(row=9, column=0, columnspan=3, pady=(8, 0), sticky="ew")
        self.appeal_btn.grid_remove()
        report_link = tk.Label(card, text="💡 Report a bug, suggest a feature, or view your previous reports", bg=BG_PANEL, fg=FG_MUTED, font=link_font, cursor="hand2")
        report_link.grid(row=10, column=0, columnspan=3, pady=(14, 0))
        report_link.bind("<Button-1>", lambda e: self._open_reports_menu())
        more_links = tk.Frame(card, bg=BG_PANEL)
        more_links.grid(row=11, column=0, columnspan=3, pady=(6, 0))
        for text, action in (("🎨 Appearance", self._open_appearance), ("📢 Announcements", self._open_announcements_window), ("🛠 Restore a previous version", self._open_restore_flow)):
            link = tk.Label(more_links, text=text, bg=BG_PANEL, fg=FG_MUTED, font=link_font, cursor="hand2")
            link.pack(side="left", padx=10)
            link.bind("<Button-1>", lambda e, action=action: action())

        self.mode_var.trace_add("write", lambda *_args: self._on_mode_change())
        self._on_mode_change()

    def _focus_first_empty(self):
        """Puts the cursor where the user will most likely type next."""
        for entry in (self.name_entry, self.room_entry, self.key_entry):
            if str(entry["state"]) == "normal" and not entry.get():
                entry.focus_set()
                return
        self.key_entry.focus_set()

    def _on_mode_change(self):
        if self.mode_var.get() == "host":
            self.recent_frame.grid_remove()
            self.room_entry.label.configure(text="Room Code (= last 2 numbers of your IP)")
            self.regen_room_btn.grid()
            self._regenerate_room_code()
            self.host_ip_entry.grid_remove()
            self.host_ip_entry.label.grid_remove()
        else:
            self.room_entry.label.configure(text="Room Code or Invite Code (from host)" if ENABLE_INVITE_CODES else "Room Code (from host)")
            self.regen_room_btn.grid_remove()
            self.room_entry.configure(state="normal")
            self.room_entry.delete(0, "end")
            self.host_ip_entry.grid()
            self.host_ip_entry.label.grid()
            self._render_recent_list()
        self.after_idle(self._focus_first_empty)

    def _regenerate_room_code(self):
        if self.mode_var.get() != "host": return
        self._host_local_ip = get_local_ip()
        self.room_entry.configure(state="normal")
        self.room_entry.delete(0, "end")
        self.room_entry.insert(0, generate_room_code(self._host_local_ip))
        self.room_entry.configure(state="readonly")

    # ---- Recent chats (Join mode) ----

    def _render_recent_list(self):
        for child in self.recent_list_frame.winfo_children(): child.destroy()
        entries = load_recent_hosts()
        if not entries:
            self.recent_frame.grid_remove()
            return
        self.recent_frame.grid()
        for entry in entries:
            self._build_recent_row(self.recent_list_frame, entry).pack(fill="x", pady=(0, 6))

    def _build_recent_row(self, parent, entry):
        row = tk.Frame(parent, bg=BG_INPUT, cursor="hand2")
        title = tk.Label(row, text=f"Room {entry['room_code']}", bg=BG_INPUT, fg=FG_TEXT, font=BOLD_FONT, anchor="w")
        title.pack(fill="x", padx=10, pady=(6, 0))
        subtitle = tk.Label(row, text=f"{entry['host_ip']} · {relative_time_str(entry['last_connected'])}", bg=BG_INPUT, fg=FG_MUTED, font=CHAT_FONT, anchor="w")
        subtitle.pack(fill="x", padx=10, pady=(0, 6))

        def paint(color):
            for w in (row, title, subtitle): w.configure(bg=color)

        for w in (row, title, subtitle):
            w.bind("<Button-1>", lambda e: self._on_recent_row_clicked(entry))
            w.bind("<Enter>", lambda e: paint(BTN_NEUTRAL_HOVER))
            w.bind("<Leave>", lambda e: paint(BG_INPUT))
        return row

    def _on_recent_row_clicked(self, entry):
        # Just prefills the Room Code from last time — the user still enters the shared key and hits
        # Connect as usual. The Host IP box is deliberately NOT filled in: the port saved from that session
        # is usually stale, and a typed IP:port skips the Room Code lookup that would find the current one.
        # (It is cleared, so an older manual IP can't silently override the code we just filled in.)
        self.room_entry.configure(state="normal")
        self.room_entry.delete(0, "end")
        self.room_entry.insert(0, entry["room_code"])
        self.host_ip_entry.delete(0, "end")
        self._set_status("Filled in from a recent connection — enter the shared key and press Connect.", "info")
        self.key_entry.focus_set()

    # ---- Connecting ----

    def _set_connecting(self, connecting: bool):
        self._connecting = connecting
        self.connect_btn.set_enabled(not connecting)
        self.connect_btn.label.configure(text="Connecting..." if connecting else "Connect")

    def _validate_connect_inputs(self, name, room_code, key):
        if not name: return "Enter a display name."
        if error := nickname_error(name): return error
        kind, value = interpret_room_input(room_code)
        if kind == "error": return value
        if not key: return "Enter the shared key password."
        return None

    def on_connect_clicked(self):
        if self._connecting or self.connection or self._gban_entry: return
        if self._ban_ctx and self._ban_ctx.get("name") != self.name_entry.get().strip():
            self._set_ban_context(None)  # a different name: it's a new attempt, not a follow-up to that ban
        name, key = self.name_entry.get().strip(), self.key_entry.get()
        room_code, mode = self.room_entry.get().strip(), self.mode_var.get()

        error = self._validate_connect_inputs(name, room_code, key)
        if error:
            return self._set_status(error, "error")

        self._set_connecting(True)
        self._set_status("Connecting, please wait..." if mode == "join" else "Starting your room...", "info")
        manual_target = (self.host_ip_entry.get().strip() or None) if mode == "join" else None
        threading.Thread(
            target=self._async_connect,
            args=(mode, name, room_code, Fernet(derive_key(key)), manual_target),
            daemon=True,
        ).start()

    def _async_connect(self, mode, name, room_code, fernet, manual_target):
        """Runs on a worker thread so the window never freezes while we do
        network work (ban-list lookup, room discovery, the handshake)."""
        put = self.event_queue.put
        ban, ban_skew = check_global_ban()
        if ban:
            return put(("connect_fail", global_ban_message(ban, ban_skew)))

        if mode == "host":
            # The code on screen was worked out when this screen opened; the IP may have changed
            # since, which would leave guests knocking on an address we no longer have.
            self._host_local_ip = get_local_ip()
            self._host_all_ips = get_local_ips()  # looked up here, off the UI thread (hostname lookups can stall)
            room_code = generate_room_code(self._host_local_ip)
            try:
                conn = HostConnection(name, room_code, fernet, self.event_queue)
            except OSError as e:
                return put(("connect_fail", f"Couldn't start: {e}"))
            return put(("connect_success", {"connection": conn, "mode": "host", "name": name, "room_code": room_code}))

        kind, value = interpret_room_input(room_code)  # already checked in _validate_connect_inputs
        host_ip, port, unlock_prefix, error = resolve_join_target(value, manual_target)
        if error:
            return put(("connect_fail", error))
        if kind == "invite":
            room_code = generate_room_code(host_ip)  # the usual 6 digits, for the title bar and the Recent list
        else:
            room_code = value
        try:
            conn = GuestConnection(name, host_ip, port, fernet, self.event_queue)
        except BannedError as e:
            return put(("banned", {"message": str(e), "host_ip": host_ip, "port": port, "fernet": fernet, "name": name,
                                   "until": e.until_str, "reason": e.reason, "room_code": room_code}))
        except PermissionError as e:
            return put(("connect_fail", str(e)))
        except (OSError, ConnectionError) as e:
            return put(("connect_fail", friendly_connect_error(e, host_ip, port)))
        remember_recent_host(room_code, host_ip, port)
        put(("connect_success", {"connection": conn, "mode": "join", "name": name, "room_code": room_code, "unlock_prefix": unlock_prefix}))

    def _on_connect_success(self, payload):
        self._set_ban_context(None)
        self._set_connecting(False)
        self.connection = payload["connection"]
        self.my_name = payload["name"]
        self.is_admin = payload["mode"] == "host"
        self._transition_to_chat(payload["mode"], payload["name"], payload["room_code"])
        if payload["mode"] == "join":
            self.update_roster(self.connection.initial_roster)
            self.connection.start(payload.get("unlock_prefix"))
        self._save_settings()

    # ---- appeals ----

    def _set_ban_context(self, ctx):
        self._ban_ctx = ctx
        self._cancel_timer("ban_poll")
        if ctx:
            ctx.setdefault("can_appeal", True)
            self._set_timer("ban_poll", BAN_POLL_SECONDS * 1000, self._poll_ban_status)
        self._refresh_ban_button()

    def _refresh_ban_button(self):
        if self._ban_ctx and self._ban_ctx.get("can_appeal", True): self.appeal_btn.grid()
        else: self.appeal_btn.grid_remove()

    def _poll_ban_status(self):
        """While we're on the ban screen, ask the host every few seconds whether we're still banned."""
        ctx = self._ban_ctx
        if not ctx: return
        def work():
            try: status = check_ban_status(ctx["host_ip"], ctx["port"], ctx["fernet"])
            except ConnectionError: status = None  # host offline for now — try again later
            self.event_queue.put(("ban_status", {"ctx": ctx, "status": status}))
        threading.Thread(target=work, daemon=True).start()

    def _on_ban_status(self, payload):
        ctx, status = payload["ctx"], payload["status"]
        if ctx is not self._ban_ctx:  # we've moved on (joined somewhere, or a newer ban screen)
            return
        state = (status or {}).get("state")
        if state in ("unbanned", "free"):
            if state == "unbanned":
                by, reason = status.get("by") or "the host", status.get("reason") or "no reason given"
                message = f"✅ You have been unbanned by {by}. Reason: {reason}. You can rejoin now."
                body = f"You have been unbanned.\n\nBy: {by}\nReason: {reason}\n\nYou can rejoin the room now."
            else:
                message = "✅ Your ban has ended. You can rejoin now."
                body = "Your ban has ended.\n\nYou can rejoin the room now."
            self._set_ban_context(None)
            self._set_status(message, "ok")
            self.bell()
            appeal_accepted = state == "unbanned" and (status.get("reason") or "").startswith("your appeal was accepted")
            self._toast("Appeal accepted" if appeal_accepted else ("Unbanned" if state == "unbanned" else "Ban ended"), message.lstrip("✅ "))
            popup = self._open_dialog("unbanned", "Unbanned", padx=24, pady=20)
            if popup is not None:
                tk.Label(popup, text="✅  You have been unbanned", bg=BG_PANEL, fg=COLOR_PALETTE["green"], font=fnt(14, "bold")).pack(anchor="w")
                tk.Label(popup, text=body.split("\n\n", 1)[1], bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT, wraplength=px(380), justify="left").pack(anchor="w", pady=(10, 0))
                make_button(popup, "OK", lambda: self._close_popup("unbanned"), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=18, pady=5).pack(anchor="e", pady=(16, 0))
                popup.lift()
                self._raise_for_attention(popup)
            return
        appeal = (status or {}).get("appeal")
        if appeal and appeal.get("status") == "rejected" and not ctx.get("appeal_result_shown"):
            ctx["appeal_result_shown"], ctx["can_appeal"] = True, False
            self._refresh_ban_button()
            self._set_status(f"Your ban appeal was rejected by {appeal.get('by', 'the host')}. Reason: {appeal.get('reason', 'no reason given')}", "error")
            self.bell()
            self._toast("Ban appeal rejected", f"Rejected by {appeal.get('by', 'the host')}. Reason: {appeal.get('reason', 'no reason given')}")
        self._set_timer("ban_poll", BAN_POLL_SECONDS * 1000, self._poll_ban_status)

    # ---- bug reports / feature suggestions ----

    def _open_report_dialog(self):
        popup = self._open_dialog("report", "Report a bug or suggest a feature", padx=24, pady=20)
        if popup is None:
            return
        tk.Label(popup, text="💡  Report a bug or suggest a feature", bg=BG_PANEL, fg=FG_TEXT, font=fnt(14, "bold")).pack(anchor="w")
        kind_var = tk.StringVar(value="bug")
        kinds = tk.Frame(popup, bg=BG_PANEL)
        kinds.pack(anchor="w", pady=(10, 4))
        for text, value in (("🐞 Bug report", "bug"), ("💡 Feature suggestion", "feature")):
            tk.Radiobutton(kinds, text=text, variable=kind_var, value=value, bg=BG_PANEL, fg=FG_TEXT, selectcolor=BG_INPUT,
                           activebackground=BG_PANEL, activeforeground=FG_TEXT, font=CHAT_FONT, cursor="hand2").pack(side="left", padx=(0, 14))
        tk.Label(popup, text="What is it, in a sentence?", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(anchor="w", pady=(8, 2))
        summary = tk.Entry(popup, width=54, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", font=CHAT_FONT,
                           validate="key", validatecommand=(self.register(lambda p: len(p) <= 120), "%P"))
        summary.pack(anchor="w", ipady=3)
        tk.Label(popup, text="More detail (optional) — what happened, what you expected, how to make it happen again…", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(anchor="w", pady=(10, 2))
        detail = tk.Text(popup, width=54, height=7, wrap="word", bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", font=CHAT_FONT, padx=6, pady=4)
        detail.pack(anchor="w")
        where = "It's saved on this computer and sent to the developer." if report_server() else "It's saved on this computer."
        tk.Label(popup, text=f"Added automatically: the date, v{VERSION} and your operating system — no name, address or messages. {where}",
                 bg=BG_PANEL, fg=FG_MUTED, font=fnt(8), wraplength=px(420), justify="left").pack(anchor="w", pady=(8, 0))
        status = tk.Label(popup, text="", bg=BG_PANEL, fg=self.STATUS_COLORS["error"], font=CHAT_FONT)
        status.pack(anchor="w", pady=(6, 0))
        buttons = tk.Frame(popup, bg=BG_PANEL)
        buttons.pack(anchor="e", pady=(8, 0))

        def send():
            if not summary.get().strip():
                return status.configure(text="Say what it is in a sentence first.")
            wait = REPORT_COOLDOWN_SECONDS - (time.time() - self._last_report_time)
            if wait > 0:
                return status.configure(text=f"One moment — you can send another in {int(wait) + 1}s.")
            self._last_report_time = time.time()
            report = new_report(kind_var.get(), summary.get(), detail.get("1.0", "end"))
            save_report(report)
            self._close_popup("report")
            if report_server() is None:
                return self._show_report_result(report, delivered=False, attempted=False)
            def deliver():
                ok = deliver_report(report)
                if ok: update_report(report["id"], delivered=True)
                self.event_queue.put(("report_result", {"report": report, "delivered": ok}))
            threading.Thread(target=deliver, daemon=True).start()
        make_button(buttons, "Send", send, bg=ACCENT, hover_bg=ACCENT_HOVER, padx=18, pady=5).pack(side="left", padx=(0, 8))
        make_button(buttons, "Cancel", lambda: self._close_popup("report"), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=18, pady=5).pack(side="left")
        summary.focus_set()

    def _check_my_reports(self):
        """Asks the report server whether any report THIS computer sent has been marked completed. Runs at launch and every
        10 minutes, and only does anything if there are sent reports it hasn't told you about yet."""
        self._set_timer("report_status", 10 * 60 * 1000, self._check_my_reports)
        if report_server() is None:
            return
        ids = [str(r["id"]) for r in load_reports() if r.get("delivered") and not r.get("notified")][:50]
        if ids:
            self._run_bg(lambda: worker_call("/status", body={"ids": ids}), self._on_my_reports_checked)

    def _on_my_reports_checked(self, result):
        code, data = result if isinstance(result, tuple) else (None, None)
        if code != 200 or not isinstance(data, dict):
            return
        self._reports_last_checked = time.time()
        self._announce_completed(apply_report_statuses(data))

    def _announce_completed(self, finished: list):
        """The window saying one or more of this computer's reports were completed (and when)."""
        if not finished:
            return
        for r in finished:
            update_report(r["id"], notified=True)
        popup_name = f"report_completed_{time.time_ns()}"
        popup = self._open_dialog(popup_name, "Report completed", padx=24, pady=20)
        if popup is None:
            return
        many = len(finished) > 1
        tk.Label(popup, text="✔  Your report was completed" if not many else "✔  Your reports were completed", bg=BG_PANEL, fg=COLOR_PALETTE["green"], font=fnt(14, "bold")).pack(anchor="w")
        for r in finished[:6]:
            icon = "💡" if r.get("kind") == "feature" else "🐞"
            tk.Label(popup, text=f"{icon}  {r.get('summary', '')}", bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT, wraplength=px(400), justify="left").pack(anchor="w", pady=(8, 0))
            if r.get("completed_at"):
                tk.Label(popup, text=f"Completed {friendly_ago(time.time() - r['completed_at'])} — {format_time(r['completed_at'])}", bg=BG_PANEL, fg=FG_MUTED, font=fnt(9)).pack(anchor="w")
        if len(finished) > 6:
            tk.Label(popup, text=f"…and {len(finished) - 6} more", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(anchor="w", pady=(4, 0))
        tk.Label(popup, text=("They've been marked as completed and will be released in the next update. " if many else
                              "It's been marked as completed and will be released in the next update. ") + "Thanks for helping make chat_gui better!",
                 bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT, wraplength=px(400), justify="left").pack(anchor="w", pady=(12, 0))
        make_button(popup, "OK", lambda: self._close_popup(popup_name), bg=ACCENT, hover_bg=ACCENT_HOVER, padx=18, pady=5).pack(anchor="e", pady=(14, 0))
        popup.lift()

    # ---- a password prompt shared by the admin tools ----

    def _ask_admin_password(self, name: str, heading: str, verify, on_ok):
        """Asks for the admin password. `verify(password)` runs in the background and returns (True, result) or (False, message);
        `on_ok(password, result)` then runs on the UI thread. Five wrong tries lock the admin tools until the app restarts."""
        if name in self._popups:
            self._popups[name].lift()
            return
        popup = self._open_dialog(name, heading, padx=24, pady=20)
        if popup is None:
            return
        tk.Label(popup, text=f"🔒  {heading}", bg=BG_PANEL, fg=FG_TEXT, font=fnt(14, "bold")).pack(anchor="w")
        tk.Label(popup, text="Admin password", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(anchor="w", pady=(10, 2))
        entry = tk.Entry(popup, show="•", width=30, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", font=CHAT_FONT)
        entry.pack(anchor="w", ipady=3)
        status = tk.Label(popup, text="", bg=BG_PANEL, fg=self.STATUS_COLORS["error"], font=CHAT_FONT)
        status.pack(anchor="w", pady=(6, 0))
        busy = {"on": False}

        def answered(password, result):
            busy["on"] = False
            ok, value = result if isinstance(result, tuple) else (False, "Something went wrong.")
            if ok:
                self._report_login_failures = 0
                self._close_popup(name)
                on_ok(password, value)
            else:
                if value == "Wrong password.":
                    self._report_login_failures += 1
                    entry.delete(0, "end")
                status.configure(text=str(value), fg=self.STATUS_COLORS["error"])

        def submit(event=None):
            if self._report_login_failures >= 5:
                return status.configure(text="Too many wrong tries — restart the app to try again.")
            if busy["on"]:
                return
            busy["on"] = True
            password = entry.get()
            status.configure(text="Checking…", fg=FG_MUTED)
            self._run_bg(lambda: verify(password), lambda result: answered(password, result))
        entry.bind("<Return>", submit)
        make_button(popup, "Open", submit, bg=ACCENT, hover_bg=ACCENT_HOVER, padx=18, pady=5).pack(anchor="e", pady=(8, 0))
        entry.focus_set()

    # ---- restore a previous version ----

    def _open_restore_flow(self):
        self._ask_admin_password("restore_login", "Restore a previous version",
                                 lambda pw: (True, None) if check_reports_password(pw) else (False, "Wrong password."),
                                 lambda pw, _: self._open_restore_window())

    def _open_restore_window(self):
        win = self._open_dialog("restore", "Restore a previous version", padx=20, pady=16)
        if win is None:
            return
        tk.Label(win, text="🛠  Restore a previous version", bg=BG_PANEL, fg=FG_TEXT, font=fnt(14, "bold")).pack(anchor="w")
        tk.Label(win, text=f"You're running v{VERSION}.", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(anchor="w", pady=(4, 8))
        backups = list_backups()
        if not backups:
            tk.Label(win, text="There's no earlier version on this computer yet — one is saved each time the app updates itself.", bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT, wraplength=px(420), justify="left").pack(anchor="w")
            make_button(win, "OK", lambda: self._close_popup("restore"), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=18, pady=5).pack(anchor="e", pady=(14, 0))
            return
        box = tk.Listbox(win, width=64, height=min(8, len(backups)), bg=BG_INPUT, fg=FG_TEXT, selectbackground=ACCENT, relief="flat", font=CHAT_FONT, activestyle="none", exportselection=False)
        box.pack(fill="x")
        for i, b in enumerate(backups):
            box.insert("end", f"{'★ last version  ' if i == 0 else ''}v{b['version']}   ·   replaced {format_time(b['stamp'])}   ·   {b['size'] // 1024} KB")
        box.selection_set(0)
        status = tk.Label(win, text="", bg=BG_PANEL, fg=FG_MUTED, font=fnt(9), wraplength=px(420), justify="left")
        status.pack(anchor="w", pady=(8, 0))
        buttons = tk.Frame(win, bg=BG_PANEL)
        buttons.pack(fill="x", pady=(10, 0))

        def restore(index):
            b = backups[index]
            if not messagebox.askyesno("Restore", f"Restore v{b['version']}?\n\nv{VERSION} (what you're running now) is kept as a backup, and the app will need a restart.", parent=win):
                return
            try:
                restore_from_backup(b["path"])
            except Exception as e:
                return status.configure(text=f"Couldn't restore it: {e}", fg=self.STATUS_COLORS["error"])
            for w in buttons.winfo_children(): w.destroy()
            status.configure(text=f"✔ v{b['version']} is back in place. Restart to use it. (The update banner may offer the newer version again — you can ignore it.)", fg=COLOR_PALETTE["green"])
            make_button(buttons, "Restart now", self._restart_app, bg=BTN_GREEN, hover_bg=BTN_GREEN_HOVER, padx=14, pady=5).pack(side="left", padx=(0, 8))
            make_button(buttons, "Later", lambda: self._close_popup("restore"), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=14, pady=5).pack(side="left")

        make_button(buttons, "Restore the last version", lambda: restore(0), bg=BTN_GREEN, hover_bg=BTN_GREEN_HOVER, padx=14, pady=5).pack(side="left", padx=(0, 8))
        make_button(buttons, "Restore the selected one", lambda: restore(box.curselection()[0] if box.curselection() else 0), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=14, pady=5).pack(side="left", padx=(0, 8))
        make_button(buttons, "Cancel", lambda: self._close_popup("restore"), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=14, pady=5).pack(side="left")

    # ---- announcements: every copy of the app ----

    def _start_announcements(self):
        """Runs shortly after launch: read the announcement now, then every 20 minutes — plus a tiny check every 2 minutes
        for an URGENT one, so those reach running copies quickly. (Needs the internet; works in a chat or not.)"""
        self._refresh_announcement()
        self._set_timer("announce_beacon", ANNOUNCE_URGENT_CHECK_SECONDS * 1000, self._check_urgent_beacon)

    def _refresh_announcement(self, manual: bool = False, done=None):
        self._set_timer("announce_full", ANNOUNCE_REFRESH_SECONDS * 1000, self._refresh_announcement)
        if report_server() is None:
            if done: done(False, "There's no server set up for announcements.")
            return
        self._run_bg(lambda: worker_call("/announcement"), lambda result: self._on_announcement(result, done))

    def _check_urgent_beacon(self):
        self._set_timer("announce_beacon", ANNOUNCE_URGENT_CHECK_SECONDS * 1000, self._check_urgent_beacon)
        if report_server() is None:
            return
        def got(result):
            code, data = result if isinstance(result, tuple) else (None, None)
            if code == 200 and isinstance(data, dict) and data.get("urgent") and data.get("seq") != self._announce_seq_seen:
                self._refresh_announcement()  # a new urgent announcement: fetch it now rather than at the next regular refresh
        self._run_bg(lambda: worker_call("/announcement/beacon"), got)

    def _on_announcement(self, result, done=None):
        code, data = result if isinstance(result, tuple) else (None, None)
        if code != 200 or not isinstance(data, dict):
            if done: done(False, "Couldn't reach the server.")
            return
        self._announce_checked = time.time()
        info = verify_announcement(data)
        if info is None:  # not signed by the publisher: ignore it entirely
            self._announce = None
            self._hide_announcement_bar()
            if done: done(False, "The announcement's signature didn't check out, so it was ignored.")
            return
        self._announce_seq_seen = info["seq"]
        self._announce = info if info["text"] else None
        if not info["text"]:
            self._hide_announcement_bar()
        elif info["seq"] != self.settings.get("announce_dismissed") and info["seq"] != self._announce_shown_seq:
            self._show_announcement_bar(info["seq"], info["text"], info["urgent"])
            if info["urgent"]:  # urgent overrides Do Not Disturb: it's the point of it
                notify_toast("🚨 Urgent announcement", info["text"], root=self)
                self._raise_for_attention(force=True)
        if done: done(True, "")

    def _paint_announce(self, bg: str, fg: str):
        for w in (self.announce_bar, self.announce_label, self.announce_close):
            w.configure(bg=bg)
        self.announce_label.configure(fg=fg)
        self.announce_close.configure(fg=fg)

    def _show_announcement_bar(self, seq: int, text: str, urgent: bool):
        self._announce_shown_seq = seq
        self._cancel_timer("announce_flash")
        self.announce_label.configure(text=("🚨 " if urgent else "📢 ") + text)
        self._paint_announce(BTN_RED if urgent else ACCENT, "white")
        anchor = self.notice_bar if self.notice_bar.winfo_ismapped() else (self.chat_frame if self.chat_frame.winfo_ismapped() else self.connect_frame)
        try: self.announce_bar.pack(side="top", fill="x", before=anchor)
        except tk.TclError: self.announce_bar.pack(side="top", fill="x")
        if urgent:  # flash red / white like the ⚠ button, then settle on red until it's dismissed
            phases = [("white", BTN_RED), (BTN_RED, "white")] * 6
            def flash():
                if not phases:
                    return self._paint_announce(BTN_RED, "white")
                bg, fg = phases.pop(0)
                self._paint_announce(bg, fg)
                self._set_timer("announce_flash", 350, flash)
            flash()

    def _hide_announcement_bar(self):
        self._cancel_timer("announce_flash")
        self._announce_shown_seq = None
        self.announce_bar.pack_forget()

    def _dismiss_announcement(self):
        if self._announce:
            self.settings["announce_dismissed"] = self._announce["seq"]
            self._save_settings()
        self._hide_announcement_bar()

    def _open_announcements_window(self):
        """The main-menu 'Announcements' window: the current announcement, and a Refresh button (once every 20 seconds)."""
        win = self._open_dialog("announcements", "Announcements", padx=24, pady=20)
        if win is None:
            return
        tk.Label(win, text="📢  Announcements", bg=BG_PANEL, fg=FG_TEXT, font=fnt(14, "bold")).pack(anchor="w")
        body = tk.Label(win, text="", bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT, wraplength=px(420), justify="left")
        body.pack(anchor="w", pady=(10, 0))
        meta = tk.Label(win, text="", bg=BG_PANEL, fg=FG_MUTED, font=fnt(9), justify="left")
        meta.pack(anchor="w", pady=(8, 0))
        message = tk.Label(win, text="", bg=BG_PANEL, fg=FG_MUTED, font=fnt(9))
        message.pack(anchor="w", pady=(4, 0))

        def render():
            a = self._announce
            body.configure(text=(("🚨 URGENT\n\n" if a["urgent"] else "") + a["text"]) if a else "No announcement right now.", fg=BTN_RED if a and a["urgent"] else FG_TEXT)
            checked = self._announce_checked
            meta.configure(text=(f"Published {friendly_ago(time.time() - a['issued'] / 1000)}. " if a else "") +
                           (f"Last checked {friendly_ago(time.time() - checked)}. " if checked else "Not checked yet. ") + "It also refreshes by itself every 20 minutes.")

        def refresh():
            wait = ANNOUNCE_MANUAL_COOLDOWN_SECONDS - (time.time() - self._last_announce_manual)
            if wait > 0:
                return message.configure(text=f"Easy — you can refresh again in {int(wait) + 1}s.")
            self._last_announce_manual = time.time()
            message.configure(text="Checking…")
            def finished(ok, why):
                message.configure(text="Up to date." if ok else why, fg=COLOR_PALETTE["green"] if ok else self.STATUS_COLORS["error"])
                render()
            self._refresh_announcement(manual=True, done=finished)

        buttons = tk.Frame(win, bg=BG_PANEL)
        buttons.pack(anchor="e", pady=(14, 0))
        make_button(buttons, "🔄 Refresh", refresh, bg=ACCENT, hover_bg=ACCENT_HOVER, padx=14, pady=5).pack(side="left", padx=(0, 8))
        make_button(buttons, "Close", lambda: self._close_popup("announcements"), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=14, pady=5).pack(side="left")
        render()

    # ---- announcements: the publisher (Ctrl+Shift+A) ----

    def on_open_announcements_admin(self, event=None):
        if report_server() is None:
            messagebox.showinfo("Announcements", "No server is set up (REPORT_WORKER_URL), so there's nowhere to publish to.", parent=self)
            return "break"
        def verify(password):
            code, data = worker_call("/announcement/admin", password=password)
            if code == 200 and isinstance(data, dict): return True, data
            return False, "Wrong password." if code == 401 else "Couldn't reach the server."
        self._ask_admin_password("announce_login", "Announcements", verify, self._open_announcement_editor)
        return "break"

    def _open_announcement_editor(self, password: str, current: dict):
        win = self._open_dialog("announce_editor", "Publish an announcement", padx=24, pady=20)
        if win is None:
            return
        tk.Label(win, text="📢  Publish an announcement", bg=BG_PANEL, fg=FG_TEXT, font=fnt(14, "bold")).pack(anchor="w")
        live = tk.Label(win, text="", bg=BG_PANEL, fg=FG_MUTED, font=fnt(9), wraplength=px(440), justify="left")
        live.pack(anchor="w", pady=(4, 8))
        box = tk.Text(win, width=58, height=5, wrap="word", bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", font=CHAT_FONT, padx=6, pady=4)
        box.pack(anchor="w")
        counter = tk.Label(win, text="", bg=BG_PANEL, fg=FG_MUTED, font=fnt(8))
        counter.pack(anchor="e")
        urgent_var = tk.BooleanVar(value=False)
        tk.Checkbutton(win, text="🚨 Urgent — flashes red, jumps to the front (even on Do Not Disturb) and arrives within about 2 minutes",
                       variable=urgent_var, bg=BG_PANEL, fg=FG_TEXT, selectcolor=BG_INPUT, activebackground=BG_PANEL, activeforeground=FG_TEXT,
                       font=CHAT_FONT, wraplength=px(440), justify="left", cursor="hand2").pack(anchor="w", pady=(6, 4))
        hours_var = tk.IntVar(value=0)
        row = tk.Frame(win, bg=BG_PANEL)
        row.pack(anchor="w")
        tk.Label(row, text="Show it for:", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(side="left", padx=(0, 8))
        for text, value in (("1 hour", 1), ("1 day", 24), ("7 days", 168), ("until I clear it", 0)):
            tk.Radiobutton(row, text=text, variable=hours_var, value=value, bg=BG_PANEL, fg=FG_TEXT, selectcolor=BG_INPUT, activebackground=BG_PANEL,
                           activeforeground=FG_TEXT, font=CHAT_FONT, cursor="hand2").pack(side="left", padx=(0, 8))
        status = tk.Label(win, text="", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT, wraplength=px(440), justify="left")
        status.pack(anchor="w", pady=(10, 0))
        buttons = tk.Frame(win, bg=BG_PANEL)
        buttons.pack(anchor="e", pady=(8, 0))

        def show_current(a):
            live.configure(text=(f"Live now: “{a['text'][:90]}{'…' if len(a['text']) > 90 else ''}”" + ("  (urgent)" if a.get("urgent") else "")) if a and a.get("text") else "Nothing is live right now.")
        show_current(current)
        if current.get("text"):
            box.insert("1.0", current["text"])
            urgent_var.set(bool(current.get("urgent")))
        def update_counter(event=None):
            n = len(box.get("1.0", "end").strip())
            counter.configure(text=f"{n} / {ANNOUNCE_MAX_CHARS}", fg=self.STATUS_COLORS["error"] if n > ANNOUNCE_MAX_CHARS else FG_MUTED)
        box.bind("<KeyRelease>", update_counter)
        update_counter()

        def show_result(result, success_text):
            code, data = result if isinstance(result, tuple) else (None, None)
            if code == 200 and isinstance(data, dict):
                status.configure(text=success_text, fg=COLOR_PALETTE["green"])
                show_current(data)
                self._refresh_announcement(manual=True)  # show it on this computer straight away, too
            elif code == 401:
                status.configure(text="The server says the password is wrong now.", fg=self.STATUS_COLORS["error"])
            else:
                status.configure(text="Couldn't reach the server — nothing was changed.", fg=self.STATUS_COLORS["error"])

        def publish():
            text = box.get("1.0", "end").replace("\r\n", "\n").strip()
            if not text:
                return status.configure(text="Type the announcement first.", fg=self.STATUS_COLORS["error"])
            if len(text) > ANNOUNCE_MAX_CHARS:
                return status.configure(text=f"That's {len(text)} characters — the limit is {ANNOUNCE_MAX_CHARS}.", fg=self.STATUS_COLORS["error"])
            key = _load_local_signing_key()
            if key is None:
                return status.configure(text="Publishing needs your update signing key file (update_signing_key.b64) next to the app — the same one you sign releases with. "
                                             "That's what stops anyone else posting announcements.", fg=self.STATUS_COLORS["error"])
            issued, hours, urgent = int(time.time() * 1000), hours_var.get(), bool(urgent_var.get())
            body = {"text": text, "urgent": urgent, "issued": issued, "hours": hours, "signature": sign_announcement(text, urgent, issued, hours, key)}
            status.configure(text="Publishing…", fg=FG_MUTED)
            self._run_bg(lambda: worker_call("/announcement/publish", body=body, password=password),
                         lambda result: show_result(result, "Published ✔ — urgent ones reach running copies within about 2 minutes, others at their next refresh (within 20)." if urgent
                                                    else "Published ✔ — running copies pick it up at their next refresh (within 20 minutes)."))

        def clear():
            if not messagebox.askyesno("Clear announcement", "Take the announcement down for everyone?", parent=win):
                return
            status.configure(text="Clearing…", fg=FG_MUTED)
            self._run_bg(lambda: worker_call("/announcement/clear", body={}, password=password), lambda result: show_result(result, "Cleared ✔"))

        make_button(buttons, "Publish", publish, bg=ACCENT, hover_bg=ACCENT_HOVER, padx=16, pady=5).pack(side="left", padx=(0, 8))
        make_button(buttons, "Clear announcement", clear, bg=BTN_RED, hover_bg=BTN_RED_HOVER, padx=14, pady=5).pack(side="left", padx=(0, 8))
        make_button(buttons, "Close", lambda: self._close_popup("announce_editor"), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=14, pady=5).pack(side="left")
        box.focus_set()

    # ---- the reports menu and "My previous reports" ----

    def _open_reports_menu(self):
        popup = self._open_dialog("reports_menu", "Reports", padx=24, pady=20)
        if popup is None:
            return
        tk.Label(popup, text="💡  Reports", bg=BG_PANEL, fg=FG_TEXT, font=fnt(14, "bold")).pack(anchor="w")
        tk.Label(popup, text="Found a bug, or have an idea? Or see how the ones you sent are getting on.", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT, wraplength=px(340), justify="left").pack(anchor="w", pady=(6, 14))
        def choose(action):
            self._close_popup("reports_menu")
            action()
        make_button(popup, "📝  Send a bug report or suggestion", lambda: choose(self._open_report_dialog), bg=ACCENT, hover_bg=ACCENT_HOVER, padx=16, pady=8).pack(fill="x")
        make_button(popup, "📂  My previous reports", lambda: choose(self._open_my_reports_window), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=16, pady=8).pack(fill="x", pady=(8, 0))
        make_button(popup, "Close", lambda: self._close_popup("reports_menu"), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=16, pady=5).pack(anchor="e", pady=(14, 0))

    def _open_my_reports_window(self):
        """Everything this computer has sent: still open or completed (and when), with a rate-limited Refresh."""
        win = self._open_dialog("my_reports", "My previous reports", padx=16, pady=14, resizable=True)
        if win is None:
            return
        top = tk.Frame(win, bg=BG_PANEL)
        top.pack(fill="x")
        tk.Label(top, text="📂  My previous reports", bg=BG_PANEL, fg=FG_TEXT, font=fnt(13, "bold")).pack(side="left")
        info = tk.Label(win, text="", bg=BG_PANEL, fg=FG_MUTED, font=fnt(9), anchor="w", justify="left", wraplength=px(600))
        info.pack(fill="x", pady=(4, 6))
        listbox = tk.Listbox(win, width=86, height=9, bg=BG_INPUT, fg=FG_TEXT, selectbackground=ACCENT, relief="flat", font=CHAT_FONT, activestyle="none", exportselection=False)
        listbox.pack(fill="x")
        detail = tk.Text(win, width=86, height=9, wrap="word", bg=BG_INPUT, fg=FG_TEXT, relief="flat", font=CHAT_FONT, padx=8, pady=6, state="disabled")
        detail.pack(fill="both", expand=True, pady=(8, 0))
        message = tk.Label(win, text="", bg=BG_PANEL, fg=FG_MUTED, font=fnt(9), anchor="w")
        message.pack(fill="x", pady=(6, 0))
        buttons = tk.Frame(win, bg=BG_PANEL)
        buttons.pack(fill="x", pady=(6, 0))
        shown = []

        def status_text(r):
            if r.get("status") == "done":
                if r.get("completed_at"):
                    return f"✔ Completed {friendly_ago(time.time() - r['completed_at'])} — {format_time(r['completed_at'])}. It will be released in the next update."
                return "✔ Completed — it will be released in the next update."
            if r.get("delivered"):
                return "⏳ Sent to the developer — not completed yet."
            if report_server() is None:
                return "📝 Saved on this computer only — this copy of the app doesn't send reports anywhere."
            return "📝 Saved on this computer only — it hasn't reached the developer (it was sent while offline, or the server was unreachable)."

        def refresh_list(keep_id=None):
            nonlocal shown
            shown = load_reports()
            listbox.delete(0, "end")
            for r in shown:
                mark = "✔" if r.get("status") == "done" else ("⏳" if r.get("delivered") else "📝")
                icon = "💡" if r.get("kind") == "feature" else "🐞"
                listbox.insert("end", f"{mark} {icon}  {r.get('date', '?')}  ·  v{r.get('version', '?')}  ·  {r.get('summary', '')}")
            index = next((i for i, r in enumerate(shown) if r.get("id") == keep_id), 0 if shown else None)
            if index is not None:
                listbox.selection_set(index)
            show_selected()
            checked = self._reports_last_checked
            info.configure(text=("Last checked with the report server: " + (friendly_ago(time.time() - checked) if checked else "not yet this session") + ". It also checks by itself every 10 minutes.")
                           if report_server() else "Reports aren't being sent anywhere from this copy of the app.")

        def show_selected(event=None):
            picked = listbox.curselection()
            r = shown[picked[0]] if picked else None
            detail.configure(state="normal")
            detail.delete("1.0", "end")
            detail.insert("1.0", f"{format_report_text(r)}\n\n{status_text(r)}" if r else "You haven't sent any reports from this computer yet.")
            detail.configure(state="disabled")

        def refresh_clicked():
            wait = REPORT_REFRESH_COOLDOWN_SECONDS - (time.time() - self._last_force_refresh)
            if wait > 0:
                return message.configure(text=f"Easy — you can refresh again in {int(wait) + 1}s.", fg=FG_MUTED)
            if report_server() is None:
                return message.configure(text="There's no report server set up, so there's nothing to check.", fg=FG_MUTED)
            self._last_force_refresh = time.time()
            message.configure(text="Checking…", fg=FG_MUTED)
            ids = [str(r["id"]) for r in load_reports() if r.get("delivered")][:50]
            if not ids:
                return message.configure(text="None of your reports have reached the server yet, so there's nothing to check.", fg=FG_MUTED)
            def finished(result):
                code, data = result if isinstance(result, tuple) else (None, None)
                if code != 200 or not isinstance(data, dict):
                    message.configure(text="Couldn't reach the report server — try again in a bit.", fg=self.STATUS_COLORS["error"])
                    return
                self._reports_last_checked = time.time()
                newly = apply_report_statuses(data)
                keep = shown[listbox.curselection()[0]].get("id") if listbox.curselection() else None
                refresh_list(keep_id=keep)
                message.configure(text="Up to date." if not newly else f"{len(newly)} newly completed!", fg=COLOR_PALETTE["green"])
                self._announce_completed(newly)
            self._run_bg(lambda: worker_call("/status", body={"ids": ids}), finished)

        def copy():
            picked = listbox.curselection()
            if picked:
                self.clipboard_clear()
                self.clipboard_append(format_report_text(shown[picked[0]]))
                message.configure(text="Copied.", fg=FG_MUTED)

        listbox.bind("<<ListboxSelect>>", show_selected)
        make_button(buttons, "🔄 Refresh", refresh_clicked, bg=ACCENT, hover_bg=ACCENT_HOVER, padx=14, pady=5).pack(side="left", padx=(0, 8))
        make_button(buttons, "Copy", copy, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=14, pady=5).pack(side="left", padx=(0, 8))
        make_button(buttons, "New report", lambda: (self._close_popup("my_reports"), self._open_report_dialog()), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=14, pady=5).pack(side="left", padx=(0, 8))
        make_button(buttons, "Close", lambda: self._close_popup("my_reports"), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=14, pady=5).pack(side="left")
        refresh_list()

    # ---- the inbox owner's "a new report arrived" alerts ----

    def _start_report_watch(self):
        """If this computer was told to watch for new reports (inbox → "Tell me when a new report arrives"), checks with the
        report server once a minute. Nothing runs unless that's switched on."""
        self._cancel_timer("report_watch")
        if report_server() and self.settings.get("report_admin_key"):
            self._poll_new_reports()

    def _poll_new_reports(self):
        key = self.settings.get("report_admin_key")
        if not key or report_server() is None:
            return
        since = int(self.settings.get("report_last_seen") or 0)
        self._set_timer("report_watch", 60 * 1000, self._poll_new_reports)
        self._run_bg(lambda: worker_call(f"/reports/since?t={since}", password=key), lambda result: self._on_new_reports_polled(result, since))

    def _on_new_reports_polled(self, result, since):
        code, data = result if isinstance(result, tuple) else (None, None)
        if code == 401:  # the inbox password was changed on the server: stop quietly, say so once
            self._set_report_alerts(False)
            self._queue_notice("📬 New-report alerts turned off — the inbox password has changed. Turn them on again in the inbox.")
            return
        if code != 200 or not isinstance(data, dict):
            return
        latest = int(data.get("latest") or 0)
        if latest > int(self.settings.get("report_last_seen") or 0):
            self.settings["report_last_seen"] = latest
            self._save_settings()
        if since <= 0:
            return  # that was just finding out where "now" is
        reports = data.get("reports") or []
        count = int(data.get("count") or len(reports))
        if count > 5:  # anti-abuse: a flood is one notice, not a stream of them
            self._queue_notice(f"📬 {count} new reports arrived at once — that's unusual. Open the inbox (Ctrl+Shift+B) to look.")
            return
        for r in reports:
            what = "suggestion" if r.get("kind") == "feature" else "bug report"
            summary = str(r.get("summary", ""))
            self._queue_notice(f"📬 New {what}: {summary[:70]}{'…' if len(summary) > 70 else ''}")

    def _set_report_alerts(self, on: bool, password: str = None, baseline: int = 0):
        """Turns the new-report alerts on (remembering the inbox password on this computer) or off."""
        if on and password:
            self.settings["report_admin_key"] = password
            self.settings["report_last_seen"] = baseline
        else:
            self.settings.pop("report_admin_key", None)
            self.settings.pop("report_last_seen", None)
            self._cancel_timer("report_watch")
        self._save_settings()
        if on and password:
            self._start_report_watch()

    def _queue_notice(self, text: str):
        """Shows `text` in the slim bar across the top of the window for 5 seconds, flashing green and white. At most 5
        notices a minute; the rest are dropped (the inbox still has everything)."""
        now = time.time()
        self._notice_times = [t for t in self._notice_times if now - t < 60]
        if len(self._notice_times) >= 5:
            return
        self._notice_times.append(now)
        self._notice_queue.append(text)
        if not self._notice_active:
            self._next_notice()

    def _next_notice(self):
        if not self._notice_queue:
            self._notice_active = False
            self._cancel_timer("notice_flash")
            self.notice_bar.pack_forget()
            return
        self._notice_active = True
        self.notice_bar.configure(text=self._notice_queue.pop(0), fg=COLOR_PALETTE["green"])
        frame = self.chat_frame if self.chat_frame.winfo_ismapped() else self.connect_frame  # sits above whichever screen is showing
        try: self.notice_bar.pack(side="top", fill="x", before=frame)
        except tk.TclError: self.notice_bar.pack(side="top", fill="x")
        ticks = {"n": 0}
        def flash():
            ticks["n"] += 1
            if ticks["n"] >= 14:  # 14 × 350 ms ≈ 5 seconds
                return self._next_notice()
            self.notice_bar.configure(fg="white" if ticks["n"] % 2 else COLOR_PALETTE["green"])
            self._set_timer("notice_flash", 350, flash)
        self._set_timer("notice_flash", 350, flash)

    def _on_report_result(self, payload):
        self._show_report_result(payload["report"], payload["delivered"], attempted=True)

    def _show_report_result(self, report: dict, delivered: bool, attempted: bool):
        popup = self._open_dialog("report_done", "Thanks!", padx=24, pady=20)
        if popup is None:
            return
        word = "suggestion" if report["kind"] == "feature" else "bug report"
        tk.Label(popup, text=f"✔  Thanks — your {word} is saved", bg=BG_PANEL, fg=COLOR_PALETTE["green"], font=fnt(14, "bold")).pack(anchor="w")
        if delivered:
            note = "It's been sent to the developer."
        elif attempted:
            note = "It's saved on this computer, but couldn't be sent to the developer just now (offline, or the network is blocking it)."
        else:
            note = "It's saved on this computer."
        tk.Label(popup, text=note, bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT, wraplength=px(380), justify="left").pack(anchor="w", pady=(8, 0))
        buttons = tk.Frame(popup, bg=BG_PANEL)
        buttons.pack(anchor="e", pady=(14, 0))
        def copy():
            self.clipboard_clear()
            self.clipboard_append(format_report_text(report))
            copy_btn.label.configure(text="Copied ✔")
        copy_btn = make_button(buttons, "Copy report", copy, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=14, pady=5)
        copy_btn.pack(side="left", padx=(0, 8))
        make_button(buttons, "Close", lambda: self._close_popup("report_done"), bg=ACCENT, hover_bg=ACCENT_HOVER, padx=18, pady=5).pack(side="left")
        popup.lift()

    def _run_bg(self, work, done):
        """Runs `work()` on a background thread (so the window never freezes on the network), then calls `done(result)` on the UI thread."""
        def runner():
            try: result = work()
            except Exception as e: result = e
            self.event_queue.put(("bg_done", {"done": done, "result": result}))
        threading.Thread(target=runner, daemon=True).start()

    def _on_bg_done(self, payload):
        try: payload["done"](payload["result"])
        except tk.TclError: pass  # the window it was for has gone

    def on_open_reports(self, event=None):
        """Ctrl+Shift+B — the report inbox, behind a password. With a report server set, the server checks the password
        (it's the Worker's ADMIN_KEY) and the inbox shows everyone's reports; otherwise it's this computer's reports and
        the password is checked here."""
        if "reports" in self._popups:
            self._popups["reports"].lift()
            return "break"
        popup = self._open_dialog("reports_login", "Report inbox", padx=24, pady=20)
        if popup is None:
            return "break"
        tk.Label(popup, text="🔒  Report inbox", bg=BG_PANEL, fg=FG_TEXT, font=fnt(14, "bold")).pack(anchor="w")
        tk.Label(popup, text="Password", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(anchor="w", pady=(10, 2))
        entry = tk.Entry(popup, show="•", width=30, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", font=CHAT_FONT)
        entry.pack(anchor="w", ipady=3)
        status = tk.Label(popup, text="", bg=BG_PANEL, fg=self.STATUS_COLORS["error"], font=CHAT_FONT)
        status.pack(anchor="w", pady=(6, 0))
        busy = {"on": False}

        def fail(message):
            self._report_login_failures += 1
            status.configure(text=message, fg=self.STATUS_COLORS["error"])
            entry.delete(0, "end")

        def opened(password, remote, note=""):
            self._report_login_failures = 0
            self._close_popup("reports_login")
            self._open_reports_window(remote=remote, password=password, note=note)

        def server_answered(password, result):
            busy["on"] = False
            code, data = result if isinstance(result, tuple) else (None, None)
            if code == 200 and isinstance(data, dict):
                opened(password, data.get("reports") or [])
            elif code == 401:
                fail("Wrong password.")
            elif code is None:  # can't reach the server: fall back to this computer's own reports
                if check_reports_password(password):
                    opened(None, None, "Couldn't reach the report server — showing only the reports saved on this computer.")
                else:
                    status.configure(text="Couldn't reach the report server (offline? or the address is wrong).", fg=self.STATUS_COLORS["error"])
            else:
                status.configure(text=f"The report server answered with an error ({code}).", fg=self.STATUS_COLORS["error"])

        def submit(event=None):
            if self._report_login_failures >= 5:
                return status.configure(text="Too many wrong tries — restart the app to try again.")
            if busy["on"]:
                return
            password = entry.get()
            if report_server():
                busy["on"] = True
                status.configure(text="Checking…", fg=FG_MUTED)
                self._run_bg(lambda: worker_call("/reports", password=password), lambda result: server_answered(password, result))
            elif check_reports_password(password):
                opened(None, None)
            else:
                fail("Wrong password.")
        entry.bind("<Return>", submit)
        make_button(popup, "Open", submit, bg=ACCENT, hover_bg=ACCENT_HOVER, padx=18, pady=5).pack(anchor="e", pady=(8, 0))
        entry.focus_set()
        return "break"

    def _open_reports_window(self, remote=None, password=None, note=""):
        """The inbox. `remote` is the report server's list (None = no server: just this computer's reports); `password` is
        the admin key, kept only for this window's server calls."""
        win = self._open_dialog("reports", "Report inbox", padx=16, pady=14, resizable=True)
        if win is None:
            return
        state = {"remote": remote}
        show_var = tk.StringVar(value="all")
        top = tk.Frame(win, bg=BG_PANEL)
        top.pack(fill="x")
        count_label = tk.Label(top, text="", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT)
        count_label.pack(side="right")
        for text, value in (("All", "all"), ("Open", "open"), ("🐞 Bugs", "bug"), ("💡 Ideas", "feature")):
            tk.Radiobutton(top, text=text, variable=show_var, value=value, bg=BG_PANEL, fg=FG_TEXT, selectcolor=BG_INPUT, activebackground=BG_PANEL,
                           activeforeground=FG_TEXT, font=CHAT_FONT, cursor="hand2", command=lambda: refresh()).pack(side="left", padx=(0, 10))
        if note:
            tk.Label(win, text=note, bg=BG_PANEL, fg=self.STATUS_COLORS["error"], font=fnt(9), wraplength=px(620), justify="left").pack(anchor="w", pady=(6, 0))
        listbox = tk.Listbox(win, width=86, height=10, bg=BG_INPUT, fg=FG_TEXT, selectbackground=ACCENT, relief="flat", font=CHAT_FONT, activestyle="none", exportselection=False)
        listbox.pack(fill="x", pady=(8, 8))
        detail = tk.Text(win, width=86, height=12, wrap="word", bg=BG_INPUT, fg=FG_TEXT, relief="flat", font=CHAT_FONT, padx=8, pady=6, state="disabled")
        detail.pack(fill="both", expand=True)
        buttons = tk.Frame(win, bg=BG_PANEL)
        buttons.pack(fill="x", pady=(10, 0))
        if password:
            alerts_var = tk.BooleanVar(value=bool(self.settings.get("report_admin_key")))
            def alerts_toggled():
                newest = max([int(r.get("created") or 0) for r in state["remote"] or []] or [0])
                self._set_report_alerts(alerts_var.get(), password=password, baseline=newest)
            tk.Checkbutton(win, text="Tell me when a new report arrives (saves the inbox password on this computer)", variable=alerts_var, command=alerts_toggled,
                           bg=BG_PANEL, fg=FG_MUTED, selectcolor=BG_INPUT, activebackground=BG_PANEL, activeforeground=FG_TEXT,
                           font=fnt(9), cursor="hand2").pack(anchor="w", pady=(8, 0))
        shown = []

        def all_items():
            """The server's reports, plus any of this computer's that never reached the server (newest first)."""
            items, seen = [], set()
            for r in state["remote"] or []:
                items.append(dict(r, _source="server", _stamp=(r.get("created") or 0) / 1000))
                seen.add(str(r.get("id")))
            for r in load_reports():
                if state["remote"] is not None and (r.get("delivered") or str(r.get("id")) in seen):
                    continue  # the server's copy is the one shown
                items.append(dict(r, _source="local", _stamp=(r.get("id") or 0) / 1e9 if isinstance(r.get("id"), int) else 0))
            return sorted(items, key=lambda r: r["_stamp"], reverse=True)

        def refresh(keep_id=None):
            nonlocal shown
            mode = show_var.get()
            everything = all_items()
            shown = [r for r in everything if mode == "all" or (mode == "open" and r.get("status") != "done") or r.get("kind") == mode]
            listbox.delete(0, "end")
            for r in shown:
                icon = "💡" if r.get("kind") == "feature" else "🐞"
                done = "✔ " if r.get("status") == "done" else ""
                listbox.insert("end", f"{icon} {done}{r.get('date', '?')}  ·  v{r.get('version', '?')}  ·  {r.get('summary', '')}")
            count_label.configure(text=f"{len(shown)} of {len(everything)}")
            index = next((i for i, r in enumerate(shown) if str(r.get("id")) == str(keep_id)), 0 if shown else None)
            if index is not None:
                listbox.selection_set(index)
            show_selected()

        def selected():
            picked = listbox.curselection()
            return shown[picked[0]] if picked else None

        def show_selected(event=None):
            r = selected()
            where = "stored on the report server" if r and r["_source"] == "server" else "saved on this computer only"
            if r and r["_source"] == "server" and r.get("status") == "done" and r.get("completed"):
                where = f"completed {friendly_ago(time.time() - r['completed'] / 1000)}, {format_time(r['completed'] / 1000)} · " + where
            detail.configure(state="normal")
            detail.delete("1.0", "end")
            detail.insert("1.0", f"{format_report_text(r)}\n\n[{r.get('status', 'open')} · {where}]" if r else "No reports here yet.")
            detail.configure(state="disabled")

        def server_failed():
            messagebox.showerror("Report inbox", "Couldn't reach the report server — nothing was changed.", parent=win)

        def toggle_done():
            r = selected()
            if not r:
                return
            new_status = "open" if r.get("status") == "done" else "done"
            if r["_source"] == "server":
                def finished(result):
                    if isinstance(result, tuple) and result[0] == 200:
                        for item in state["remote"]:
                            if str(item.get("id")) == str(r["id"]): item["status"] = new_status
                        refresh(keep_id=r["id"])
                    else:
                        server_failed()
                self._run_bg(lambda: worker_call("/reports/status", body={"id": str(r["id"]), "status": new_status}, password=password), finished)
            else:
                update_report(r["id"], status=new_status)
                refresh(keep_id=r["id"])

        def remove():
            r = selected()
            if not r or not messagebox.askyesno("Delete report", "Delete this report for good?", parent=win):
                return
            if r["_source"] == "server":
                def finished(result):
                    if isinstance(result, tuple) and result[0] == 200:
                        state["remote"] = [item for item in state["remote"] if str(item.get("id")) != str(r["id"])]
                        refresh()
                    else:
                        server_failed()
                self._run_bg(lambda: worker_call("/reports/delete", body={"id": str(r["id"])}, password=password), finished)
            else:
                delete_report(r["id"])
                refresh()

        def reload_from_server():
            def finished(result):
                if isinstance(result, tuple) and result[0] == 200 and isinstance(result[1], dict):
                    state["remote"] = result[1].get("reports") or []
                    refresh()
                else:
                    server_failed()
            self._run_bg(lambda: worker_call("/reports", password=password), finished)

        def copy():
            if r := selected():
                self.clipboard_clear()
                self.clipboard_append(format_report_text(r))

        listbox.bind("<<ListboxSelect>>", show_selected)
        actions = [("Mark done / reopen", toggle_done, (BTN_GREEN, BTN_GREEN_HOVER)), ("Copy", copy, (BTN_NEUTRAL, BTN_NEUTRAL_HOVER)),
                   ("Delete", remove, (BTN_RED, BTN_RED_HOVER)), ("Close", lambda: self._close_popup("reports"), (BTN_NEUTRAL, BTN_NEUTRAL_HOVER))]
        if password:
            actions.insert(0, ("Refresh", reload_from_server, (BTN_NEUTRAL, BTN_NEUTRAL_HOVER)))
        for text, command, colors in actions:
            make_button(buttons, text, command, bg=colors[0], hover_bg=colors[1], padx=14, pady=5).pack(side="left", padx=(0, 8))
        refresh()

    def _invite_code(self):
        """This room's Invite Code — its host's address and port — or None if we're not in one."""
        conn = self.connection
        if isinstance(conn, HostConnection):
            return make_invite_code(self._host_local_ip or get_local_ip(), conn.tcp_port)
        if isinstance(conn, GuestConnection):
            return make_invite_code(conn.host, conn.port)
        return None

    def _toast(self, title: str, message: str):
        """A desktop notification for a moderation outcome. Not shown under Do Not Disturb."""
        if not self.dnd_active:
            notify_toast(title, message, root=self)

    def _raise_for_attention(self, popup=None, force: bool = False):
        """Warnings, mutes, kicks and bans jump in front of everything — even other apps, and even if this window
        was minimised. Under Do Not Disturb they don't: they wait quietly and are there when the window is next opened."""
        if self.dnd_active and not force:
            return
        try:
            if self.state() == "iconic": self.deiconify()
            self.lift()
            self.attributes("-topmost", True)
            if popup is not None:
                popup.lift()
                popup.attributes("-topmost", True)
            self.focus_force()
            def settle():  # float on top just long enough to be seen, then behave like a normal window again
                for w in (self, popup):
                    try:
                        if w is not None: w.attributes("-topmost", False)
                    except tk.TclError:
                        pass
            self.after(1500, settle)
        except tk.TclError:
            pass

    def _show_moderation_notice(self, name: str, heading: str, message: str, color: str, appeal_button: bool = False):
        """A small notice window for being muted, kicked or banned (the warning has its own dialog)."""
        popup = self._open_dialog(name, heading, padx=24, pady=20)
        if popup is None:
            return
        tk.Label(popup, text=heading, bg=BG_PANEL, fg=color, font=fnt(14, "bold")).pack(anchor="w")
        tk.Label(popup, text=localize_times(message), bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT, wraplength=px(400), justify="left").pack(anchor="w", pady=(10, 0))
        buttons = tk.Frame(popup, bg=BG_PANEL)
        buttons.pack(anchor="e", pady=(16, 0))
        if appeal_button and self._ban_ctx:
            make_button(buttons, "Appeal", lambda: (self._close_popup(name), self._open_ban_appeal()), bg=ACCENT, hover_bg=ACCENT_HOVER, padx=16, pady=5).pack(side="left", padx=(0, 8))
        make_button(buttons, "OK", lambda: self._close_popup(name), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=18, pady=5).pack(side="left")
        self._raise_for_attention(popup)

    def _on_kicked(self, message: str):
        was_in_chat = self.connection is not None
        self._handle_disconnected(message)
        if was_in_chat:
            self._show_moderation_notice("mod_kick", "You were kicked", message, COLOR_PALETTE["red"])

    def _on_mute_notice(self, text: str):
        self.append_private_line(text)
        self._show_moderation_notice("mod_mute", "🔇  You were muted", text, COLOR_PALETTE["yellow"])

    def _on_banned(self, ctx):
        """Joining was refused because we're banned: say so, and offer to appeal."""
        self._set_connecting(False)
        self._set_status(ctx["message"], "error")
        self._set_ban_context(ctx)
        self._teardown_connection()

    # ---- banned from the whole app (the publisher's /globalban) ----

    def _global_ban_tick(self):
        """Every 20 seconds: ask the report server one tiny question (\"has the ban list changed?\") and only read the whole
        list when it has. Also lifts a ban that has run out, without asking anyone."""
        self._set_timer("gban_tick", GLOBAL_BAN_BEACON_SECONDS * 1000, self._global_ban_tick)
        self._evaluate_global_ban()
        if self._gban_seq_seen is None or report_server() is None:
            return self._fetch_global_bans()
        def got(result):
            code, data = result if isinstance(result, tuple) else (None, None)
            if code == 200 and isinstance(data, dict) and data.get("seq") != self._gban_seq_seen:
                self._fetch_global_bans()
        self._run_bg(lambda: worker_call("/bans/beacon", timeout=6), got)

    def _fetch_global_bans(self):
        def done(result):
            if not isinstance(result, dict):
                return   # couldn't read it (offline, server down): carry on with what we had — and ask again next time
            self._gban_seq_seen = result["seq"]
            self._gban_entries, self._gban_skew = result["entries"], result["skew"]
            save_global_bans_cache(result)
            self._evaluate_global_ban()
        self._run_bg(fetch_global_bans, done)

    def _evaluate_global_ban(self):
        entry = global_ban_match(self._gban_entries, get_machine_fingerprint(), time.time() + self._gban_skew) if self._gban_entries else None
        if entry is not None and entry != self._gban_entry:
            self._show_global_ban(entry)
        elif entry is None and self._gban_entry is not None:
            self._hide_global_ban()

    def _show_global_ban(self, entry):
        """Takes this device out of the app at once: leaves any chat (a host's room closes), closes every window, and covers the
        screen with who banned it for what, and until when."""
        self._gban_entry = entry
        if self.connection is not None:
            self._return_to_connect_screen("This device has been banned from chat_gui.", "error")
        self._set_connecting(False)
        for name in list(self._popups):
            self._close_popup(name)
        for win in list(self._game_wins.values()):
            try: win.destroy()
            except tk.TclError: pass
        if self._gban_overlay is not None:
            try: self._gban_overlay.destroy()
            except tk.TclError: pass
        overlay = tk.Frame(self, bg=BG_DARK)
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        card = tk.Frame(overlay, bg=BG_PANEL, padx=px(40), pady=px(32))
        card.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(card, text="🚫  You've been banned from chat_gui", bg=BG_PANEL, fg=COLOR_PALETTE["red"], font=fnt(16, "bold")).pack()
        tk.Label(card, text="This device can't use the app while the ban is in place.", bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT).pack(pady=(10, 14))
        for label, value in (("Reason", entry.get("reason") or "no reason given"), ("Banned until", global_ban_until_text(entry, self._gban_skew))):
            row = tk.Frame(card, bg=BG_PANEL)
            row.pack(anchor="w", pady=2)
            tk.Label(row, text=f"{label}:", bg=BG_PANEL, fg=FG_MUTED, font=BOLD_FONT).pack(side="left")
            tk.Label(row, text=f" {value}", bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT, wraplength=px(380), justify="left").pack(side="left")
        tk.Label(card, text=f"Device ID: {entry.get('fingerprint', '')}", bg=BG_PANEL, fg=FG_MUTED, font=fnt(8)).pack(pady=(14, 0))
        make_button(card, "Close app", self.on_close, bg=BTN_RED, hover_bg=BTN_RED_HOVER, padx=22, pady=6).pack(pady=(14, 0))
        overlay.lift()
        self._gban_overlay = overlay
        self.bell()
        notify_toast("Banned from chat_gui", f"Reason: {entry.get('reason') or 'no reason given'}", root=self)
        self._raise_for_attention(force=True)

    def _hide_global_ban(self):
        self._gban_entry = None
        if self._gban_overlay is not None:
            try: self._gban_overlay.destroy()
            except tk.TclError: pass
            self._gban_overlay = None
        notify_toast("chat_gui", "Your ban has ended — you can use the app again.", root=self)
        self._focus_first_empty()

    def _handle_global_ban_command(self, cmd: str, arg: str):
        """/globalban, /unglobalban, /globalbans — the publisher only (it needs the signing key file, and the admin password to publish)."""
        if _load_local_signing_key() is None:
            return self.append_system_line("This command requires the signing key file, which only the app's publisher has.")
        if report_server() is None:
            return self.append_system_line("No report server is set (REPORT_WORKER_URL), so there's nowhere to publish the ban list.")
        hub = self.connection.hub if isinstance(self.connection, HostConnection) else None
        lookup = (lambda token: hub.find_device(token)) if hub is not None else None

        def run(password):
            def done(result):
                if isinstance(result, Exception):
                    return self.append_system_line(f"Something went wrong: {result}")
                text, kick, bad_password = result
                if bad_password:
                    self._gban_pw = None
                self.append_system_line(text)
                if kick:
                    self._fetch_global_bans()   # this computer too, straight away
                    if hub is not None:  # carry it out in this room right now; their own app does the rest the moment it hears
                        sock = hub._find_socket(lambda info: info.get("fingerprint") == kick["fp"])
                        if sock is not None:
                            hub.eject(sock, BAN_NOTICE_PREFIX + make_ban_notice(kick["until"], GLOBAL_BAN_REASON_PREFIX + kick["reason"], hub.host_name),
                                      f"* {kick['name']} has been banned from chat_gui *")
                elif cmd == "/unglobalban":
                    self._fetch_global_bans()
            self._run_bg(lambda: run_global_ban_command(cmd, arg, lookup, password), done)

        if cmd == "/globalbans":
            return run(None)
        password = self.settings.get("report_admin_key") or self._gban_pw
        if password:
            return run(password)
        def verify(pw):
            code, data = worker_call("/bans/admin", password=pw)
            if code == 200 and isinstance(data, dict): return True, data
            return False, "Wrong password." if code == 401 else "Couldn't reach the server."
        def accepted(pw, _data):
            self._gban_pw = pw
            run(pw)
        self._ask_admin_password("gban_login", "Global ban", verify, accepted)

    def _on_banned_live(self, payload):
        """We were banned while in the chat. Remember how to reach the host so the appeal works."""
        if GLOBAL_BAN_REASON_PREFIX in str(payload.get("message", "")):
            self._fetch_global_bans()   # the publisher banned this device from the whole app: read the list now
        conn = self.connection
        ctx = None
        if isinstance(conn, GuestConnection):
            ctx = {**payload, "host_ip": conn.host, "port": conn.port, "fernet": conn.fernet, "name": self.my_name, "room_code": self._room_code}
        self._return_to_connect_screen(payload["message"], "error")
        self._set_ban_context(ctx)
        self._toast("You were banned", payload["message"])
        self._show_moderation_notice("mod_ban", "You were banned", payload["message"], COLOR_PALETTE["red"], appeal_button=True)

    def _open_ban_appeal(self):
        ctx = self._ban_ctx
        if not ctx:
            return
        intro = (f"You were banned until {ctx['until']}.\nReason given: {ctx['reason']}\n\n"
                 "Answer a few questions and the host and admins will see them. If they're feeling kind, you'll be unbanned.")
        self._open_appeal_form("appeal_ban", "Appeal your ban", intro, BAN_APPEAL_QUESTIONS, self._submit_ban_appeal)

    def _submit_ban_appeal(self, answers):
        ctx = self._ban_ctx
        if not ctx:
            return
        self._set_status("Sending your appeal…", "info")
        payload = {"kind": "ban", "name": ctx["name"], "answers": answers}

        def work():
            try:
                reply = send_ban_appeal(ctx["host_ip"], ctx["port"], ctx["fernet"], payload)
                ok = reply.startswith("Your appeal was sent")
                self.event_queue.put(("appeal_result", {"ok": ok, "message": reply}))
            except ConnectionError as e:
                self.event_queue.put(("appeal_result", {"ok": False, "message": str(e)}))

        threading.Thread(target=work, daemon=True).start()

    def _on_appeal_result(self, payload):
        self._set_status(payload["message"], "ok" if payload["ok"] else "error")
        if payload["ok"] and self._ban_ctx:
            self._ban_ctx["can_appeal"] = False  # one appeal per ban — nothing more to press (but keep listening for the answer)
            self._refresh_ban_button()

    def _open_warning_appeal(self, number: int, by: str, reason: str):
        if number in self._appealed_warnings:
            return messagebox.showinfo("Appeal", "You've already appealed that warning.", parent=self)
        intro = f"Warning #{number} from {by}:\n“{reason}”\n\nAnswer a few questions and the host and admins will see them."

        def submit(answers):
            self._appealed_warnings.add(number)
            if self.connection is not None:
                self.connection.send_appeal({"kind": "warn", "number": number, "answers": answers})
                key = f"appeal_{number}"
                self._status_line_new(key, f"Sending your appeal for warning #{number}…")
                self._appeal_pending = {"number": number, "key": key}
                self._set_timer("appeal_wait", 12000, lambda: self._status_line_update(
                    key, f"Still waiting for the host to confirm your appeal for warning #{number}…"))
            self._close_popup("warning_view")  # the warning pop-up has done its job
            self._refresh_warn_button()

        self._open_appeal_form(f"appeal_warn_{number}", f"Appeal warning #{number}", intro, WARN_APPEAL_QUESTIONS, submit)

    def _open_appeal_form(self, dialog_name, title, intro, questions, on_submit):
        """A questionnaire dialog; on_submit([[question, answer], ...]) is called when they hit Send."""
        popup = self._open_dialog(dialog_name, title, padx=20, pady=16)
        if popup is None:
            return
        tk.Label(popup, text=title, bg=BG_PANEL, fg=FG_TEXT, font=fnt(14, "bold")).pack(anchor="w")
        tk.Label(popup, text=intro, bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT, wraplength=px(470), justify="left").pack(anchor="w", pady=(4, 6))
        getters = []
        for item in questions:
            kind, question = item[0], item[1]
            tk.Label(popup, text=question, bg=BG_PANEL, fg=FG_TEXT, font=BOLD_FONT, wraplength=px(470), justify="left", anchor="w").pack(fill="x", pady=(8, 2))
            if kind == "text":
                box = tk.Text(popup, height=2, width=58, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", font=CHAT_FONT, wrap="word")
                box.pack(fill="x")
                getters.append((question, lambda b=box: b.get("1.0", "end").strip()))
            elif kind == "choice":
                var = tk.StringVar(value=item[2][0])
                option = tk.OptionMenu(popup, var, *item[2])
                option.configure(bg=BG_INPUT, fg=FG_TEXT, activebackground=BTN_NEUTRAL, activeforeground="white", relief="flat", highlightthickness=0, font=CHAT_FONT)
                option["menu"].configure(bg=BG_PANEL, fg=FG_TEXT)
                option.pack(anchor="w")
                getters.append((question, var.get))
            elif kind == "scale":
                scale = tk.Scale(popup, from_=1, to=10, orient="horizontal", length=280, bg=BG_PANEL, fg=FG_TEXT, highlightthickness=0, troughcolor=BG_INPUT)
                scale.set(5)
                scale.pack(anchor="w")
                getters.append((question, lambda sc=scale: str(sc.get())))
        hint = tk.Label(popup, text="", bg=BG_PANEL, fg=COLOR_PALETTE["red"], font=CHAT_FONT)
        hint.pack(anchor="w", pady=(8, 0))

        def send():
            answers = [[q, g()] for q, g in getters]
            if not answers[0][1]:
                hint.configure(text="Please answer the first question at least.")
                return
            self._close_popup(dialog_name)
            on_submit(answers)

        row = tk.Frame(popup, bg=BG_PANEL)
        row.pack(anchor="e", pady=(6, 0))
        make_button(row, "Cancel", lambda: self._close_popup(dialog_name), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=14, pady=5).pack(side="left", padx=(0, 8))
        make_button(row, "Send appeal", send, bg=BTN_GREEN, hover_bg=BTN_GREEN_HOVER, padx=16, pady=5).pack(side="left")
        popup.lift()

    def _on_connect_fail(self, message):
        self._set_connecting(False)
        self._set_status(message, "error")
        self._teardown_connection()
        self._focus_first_empty()

    def _reset_session_state(self):
        self._teardown_popups()
        for key in ("slowmode", "mute", "dnd", "typing", "typing_prune"):
            self._cancel_timer(key)
        self._init_session_state()
        self.photo_cache = []
        self._history_pos = None

        with self._log_edit():
            self.log.delete("1.0", "end")
        self._hide_jump()
        self.typing_var.set("")
        self._refresh_upload_label()
        self._clear_reply()
        self.dnd_btn.disabled = False
        self._set_dnd_button_style(False)
        self._apply_mute_state(False)
        self._close_popup("warning_view")
        self._cancel_timer("appeal_wait")
        self._cancel_timer("warn_fx")
        self._warn_fx = None
        self._refresh_warn_button()
        for child in self.member_list_frame.winfo_children(): child.destroy()
        self._update_window_title()

    def _transition_to_chat(self, mode, name, room_code):
        self._set_ban_context(None)
        self._reset_session_state()
        self.known_colors = {name.lower(): HOST_COLOR if mode == "host" else FG_TEXT}
        self.update_roster([name])
        self._room_code = room_code
        self._update_room_label()
        self.connect_frame.pack_forget()
        self.chat_frame.pack(fill="both", expand=True)
        self.msg_entry.focus_set()

        if mode == "host":
            local_ip = self._host_local_ip or get_local_ip()
            others = [ip for ip in getattr(self, "_host_all_ips", []) if ip != local_ip]
            extra = f" (this device also has: {', '.join(others)})" if others else ""
            self.append_system_line(
                f"Hosting Room {room_code} on {local_ip}{extra}. Guests on your same network can join with just the Room Code. "
                + (f"If that doesn't work for someone, send them your Invite Code — {make_invite_code(local_ip, self.connection.tcp_port)} — "
                   f"to paste into the Room Code box (/invite shows it again). Type /help for commands." if ENABLE_INVITE_CODES else
                   f"If that doesn't work, have them enter {local_ip}:{self.connection.tcp_port} in the 'Host IP' field. Type /help for commands.")
            )
        else:
            self.append_system_line(f"You joined Room {room_code} as {name}. Type /help for commands.")
        # Open game windows carry on. A host's can say where it stands at once; a guest's does so once the
        # host has answered our feature announcement (see the "features" event) — until then, just redraw.
        if mode == "host": self._games_context_changed()
        else: self._refresh_games()

    def _on_room_code_changed(self, payload):
        """Our IP changed while hosting, so the Room Code did too."""
        if not isinstance(self.connection, HostConnection): return
        self._room_code = payload["room_code"]
        self._host_local_ip = payload["ip"]
        self._update_room_label()
        self.append_system_line(
            f"Your IP changed to {payload['ip']}, so the Room Code is now {payload['room_code']}. "
            f"Guests already in the chat aren't affected; new guests should use the new code."
        )

    def _update_room_label(self):
        verb = "Hosting as" if isinstance(self.connection, HostConnection) else "Connected as"
        self.title_label.configure(text=f"{verb} {self.my_name} — Room {self._room_code}")

    def _on_rename(self, payload):
        """Somebody's nickname changed (their own choice, or the host's). Everything on screen
        that's keyed by name follows."""
        old, new, by = payload["old"], payload["new"], payload["by"]
        old_key, new_key = old.lower(), new.lower()
        if old_key == self.my_name.lower():
            self.my_name = new
            if self.connection is not None:
                self.connection.name = new
            self._update_room_label()
            self._save_settings()
        if old_key in self.known_colors:
            self.known_colors[new_key] = self.known_colors.pop(old_key)
        for key, author in list(self._msg_authors.items()):
            if author.lower() == old_key:
                self._msg_authors[key] = new
        for key, board in self.game_boards.items():
            entry = board.pop(old_key, None)
            if entry is not None:
                entry["name"] = new
                board[new_key] = entry
                self._refresh_games(key)
        self.typing_last_seen.pop(old, None)
        self.update_roster([new if n.lower() == old_key else n for n in self.current_roster])
        if by.lower() == old_key:
            self.append_system_line(f"{old} is now known as {new}")
        else:
            self.append_system_line(f"{old} was renamed to {new} by {by}")

    def _on_warned(self, payload):
        by, count, reason = payload["by"], payload["count"], payload["reason"]
        self._warnings[count] = {"by": by, "reason": reason, "state": "active"}
        self.append_private_line(f"⚠ Warning #{count} from {by}: {reason}")
        self.bell()
        self._close_popup("warning_view")  # the new warning is what we show now
        self._cancel_timer("warn_fx")
        self._warn_fx = None
        self._refresh_warn_button()
        self._show_warning_dialog(count)
        self._raise_for_attention(self._popups.get("warning_view"))

    def _on_warn_sync(self, entries):
        """On joining, the host tells us every warning we still have (and where each appeal stands), so
        the ⚠ button is there even if we left and came back. Quiet: no pop-up, no sound."""
        if not isinstance(entries, list): return
        self._warnings = {}
        for e in entries:
            try: number, by, reason, appeal = int(e["n"]), str(e["by"]), str(e["reason"]), e.get("appeal", "none")
            except (KeyError, TypeError, ValueError): continue
            self._warnings[number] = {"by": by, "reason": reason, "state": "rejected" if appeal == "rejected" else "active", "note_done": True}
            if appeal in ("pending", "rejected"):
                self._appealed_warnings.add(number)
        self._refresh_warn_button()

    def _warn_note(self, number: int) -> str:
        warning = self._warnings[number]
        if warning["state"] == "rejected":
            return "" if warning.get("note_done") else " · appeal rejected"  # shown for 3 s after the flash (see _warn_btn_rejected)
        return " · appeal sent" if number in self._appealed_warnings else ""

    def _refresh_warn_button(self):
        """The ⚠ button in the top bar: there for as long as we hold a warning, so closing the pop-up
        never costs us the Appeal button. One warning: "⚠ Warning #2"; several: "⚠ Warnings #1, #3"."""
        if self._warn_fx:
            return  # an effect is playing — it repaints the button itself when it finishes
        if not self._warnings:
            self.warn_btn.pack_forget()
            return
        self._paint_warn_btn(self.WARN_YELLOW)
        numbers = sorted(self._warnings)
        if len(numbers) == 1:
            text = f"⚠ Warning #{numbers[0]}{self._warn_note(numbers[0])}"
        elif len(numbers) <= 4:
            text = "⚠ Warnings " + ", ".join(f"#{n}" for n in numbers)
        else:
            text = f"⚠ {len(numbers)} warnings"
        self.warn_btn.label.configure(text=text)
        self.warn_btn.pack(side="right", padx=(12, 0), pady=6, after=self.dnd_btn)

    def _on_warn_btn_clicked(self):
        """One warning: open it. Several: a menu of them, to pick which to look at."""
        numbers = sorted(self._warnings)
        if not numbers:
            return messagebox.showinfo("Warning", "You don't have any warnings right now.", parent=self)
        if len(numbers) == 1:
            return self._show_warning_dialog(numbers[0])
        menu = tk.Menu(self, tearoff=0, bg=BG_PANEL, fg=FG_TEXT)
        for number in numbers:
            warning = self._warnings[number]
            reason = warning["reason"] if len(warning["reason"]) <= 40 else warning["reason"][:39] + "…"
            status = "appeal rejected" if warning["state"] == "rejected" else ("appeal sent" if number in self._appealed_warnings else "no appeal yet")
            menu.add_command(label=f"#{number} — {reason}   ({status})", command=lambda n=number: self._show_warning_dialog(n))
        try:
            menu.tk_popup(self.warn_btn.winfo_rootx(), self.warn_btn.winfo_rooty() + self.warn_btn.winfo_height())
        finally:
            menu.grab_release()

    def _paint_warn_btn(self, colors):
        self.warn_btn.base_bg, self.warn_btn.hover_bg = colors
        self.warn_btn.paint(colors[0])
        # white text vanishes on the white flash, so the text goes red there (red-on-white / white-on-red)
        self.warn_btn.label.configure(fg=BTN_RED if colors is self.WARN_WHITE else "white")

    def _end_warn_fx(self):
        """Stops any ⚠ button effect and puts the button back to how things really stand."""
        self._cancel_timer("warn_fx")
        self._warn_fx = None
        self._refresh_warn_button()

    def _warn_btn_removed(self, text: str):
        """A warning is gone (an admin deleted it, or our appeal was accepted): the button goes green, says so for
        a few seconds, then shows whatever warnings are left (or disappears if there are none)."""
        self._cancel_timer("warn_fx")
        self._warn_fx = "hold"
        self.warn_btn.label.configure(text=text)
        self._paint_warn_btn(self.WARN_GREEN)
        self.warn_btn.pack(side="right", padx=(12, 0), pady=6, after=self.dnd_btn)
        self._set_timer("warn_fx", 5000, self._end_warn_fx)

    def _warn_btn_rejected(self, number: int):
        """Our appeal was rejected: the button flashes red and white six times, quickly, then settles back to yellow."""
        self._cancel_timer("warn_fx")
        self._warn_fx = "flash"
        self.warn_btn.label.configure(text=f"⚠ Warning #{number} · appeal rejected")
        self.warn_btn.pack(side="right", padx=(12, 0), pady=6, after=self.dnd_btn)
        sequence = [self.WARN_RED, self.WARN_WHITE] * 6
        def step():
            if self._warn_fx != "flash":
                return
            if not sequence:
                # Flashing done: back to yellow, "appeal rejected" stays up for 3 more seconds, then the warning number(s).
                self._paint_warn_btn(self.WARN_YELLOW)
                def show_number():
                    if number in self._warnings:
                        self._warnings[number]["note_done"] = True
                    self._end_warn_fx()
                return self._set_timer("warn_fx", 3000, show_number)
            self._paint_warn_btn(sequence.pop(0))
            self._set_timer("warn_fx", 120, step)
        step()

    def _show_warning_dialog(self, number: int = None):
        """Shows one of our warnings (the newest unless told which), with the Appeal button while there's still an appeal to make."""
        if number is None and self._warnings:
            number = max(self._warnings)
        warning = self._warnings.get(number)
        if warning is None:
            return messagebox.showinfo("Warning", "You don't have any warnings right now.", parent=self)
        if self._warn_view != number:
            self._close_popup("warning_view")  # showing a different warning than the open dialog
        by, count, reason = warning["by"], number, warning["reason"]
        popup = self._open_dialog("warning_view", "⚠ Warning", padx=24, pady=20)
        if popup is None:
            return
        self._warn_view = number
        tk.Label(popup, text="⚠  You have been warned", bg=BG_PANEL, fg=COLOR_PALETTE["red"], font=fnt(14, "bold")).pack(anchor="w")
        tk.Label(popup, text=f"By {by}   ·   warning #{count}", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(anchor="w", pady=(6, 10))
        tk.Label(popup, text=reason, bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT, wraplength=px(380), justify="left").pack(anchor="w")
        buttons = tk.Frame(popup, bg=BG_PANEL)
        buttons.pack(anchor="e", pady=(16, 0))
        if warning["state"] == "rejected":
            tk.Label(popup, text="Your appeal was rejected — the warning stands.", bg=BG_PANEL, fg=COLOR_PALETTE["red"], font=CHAT_FONT).pack(anchor="w", pady=(10, 0))
        elif count in self._appealed_warnings:
            tk.Label(popup, text="Appeal sent ✔ — the host and admins have it.", bg=BG_PANEL, fg=COLOR_PALETTE["green"], font=CHAT_FONT).pack(anchor="w", pady=(10, 0))
        else:
            make_button(buttons, "Appeal", lambda: self._open_warning_appeal(count, by, reason), bg=ACCENT, hover_bg=ACCENT_HOVER, padx=16, pady=5).pack(side="left", padx=(0, 8))
        make_button(buttons, "Close", lambda: self._close_popup("warning_view"), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=18, pady=5).pack(side="left")
        others = [n for n in sorted(self._warnings) if n != count]
        if others:
            tk.Label(popup, text="You also have: " + ", ".join(f"#{n}" for n in others) + " — click the ⚠ button to look at them.", bg=BG_PANEL, fg=FG_MUTED, font=fnt(9)).pack(anchor="w", pady=(10, 0))
        tk.Label(popup, text="Closing this is fine — the ⚠ button at the top of the chat brings it back, and /warnings lists them all.", bg=BG_PANEL, fg=FG_MUTED, font=fnt(8)).pack(anchor="w", pady=(6, 0))
        popup.lift()

    def _on_warn_state(self, payload):
        """The host tells us how one of our warnings ended up: removed, or its appeal rejected."""
        number, state = payload["number"], payload["state"]
        if state == "accepted":
            self._toast("Appeal accepted", f"Your appeal for warning #{number} was accepted — the warning was removed.")
        elif state == "rejected":
            self._toast("Appeal rejected", f"Your appeal for warning #{number} was rejected — the warning stands.")
        warning = self._warnings.get(number)
        if warning is None:
            return  # not a warning we're holding
        viewing = "warning_view" in self._popups and self._warn_view == number
        if viewing:
            self._close_popup("warning_view")
        if state in ("removed", "accepted"):
            del self._warnings[number]
            self._appealed_warnings.discard(number)
            self._warn_btn_removed("✔ Appeal accepted" if state == "accepted" else "✔ Warning removed")
            return
        if state == "rejected":
            warning["state"] = "rejected"
            self._appealed_warnings.add(number)
            self._warn_btn_rejected(number)
        else:
            self._refresh_warn_button()
        if viewing:
            self._show_warning_dialog(number)

    # ---- the "Sending your appeal…" line that becomes "Appeal sent ✔" ----

    def _status_line_new(self, key: str, text: str):
        """A system line we can rewrite later with _status_line_update (it's tagged with `key`)."""
        with self._log_append():
            self.log.insert("end", f"* {text}", ("system", f"status_{key}"))
            self.log.insert("end", "\n", ("system",))

    def _status_line_update(self, key: str, text: str):
        tag = f"status_{key}"
        ranges = self.log.tag_ranges(tag)
        if not ranges:  # the line is gone (the log was cleared) — say it again as a new line
            return self.append_system_line(text)
        with self._log_edit():
            start, end = ranges[0], ranges[1]
            self.log.delete(start, end)
            self.log.insert(start, f"* {text}", ("system", tag))

    def _on_private_text(self, text: str):
        """A private line from the host. If it's the answer to a warning appeal we just sent, it rewrites
        the "Sending…" line; anything else is shown as usual."""
        pending = self._appeal_pending
        if pending is not None and text in APPEAL_REPLY_TEXTS:
            self._appeal_pending = None
            self._cancel_timer("appeal_wait")
            number = pending["number"]
            if text == APPEAL_SENT_TEXT:
                self._status_line_update(pending["key"], f"Appeal sent for warning #{number} ✔ — the host and admins have it.")
            else:
                self._status_line_update(pending["key"], f"Couldn't send your appeal for warning #{number}: {text}")
            return
        self.append_private_line(text)

    def _return_to_connect_screen(self, message, kind):
        self._teardown_connection()
        self._set_connecting(False)
        self.chat_frame.pack_forget()
        self.connect_frame.pack(fill="both", expand=True)
        self._set_status(message, kind)
        self._regenerate_room_code()
        if self.mode_var.get() == "join": self._render_recent_list()
        self._unread = 0
        self._update_window_title()
        self._focus_first_empty()

    def on_disconnect_clicked(self):
        self._return_to_connect_screen("Disconnected.", "ok")

    def _handle_disconnected(self, reason: str):
        if self.connection is None:
            return  # already left; a late event from the old session
        self._return_to_connect_screen(reason, "error")

    def _teardown_popups(self):
        self.destroy_suggestions()
        self._close_popup("emoji")
        self._close_popup("stickers")

    def _teardown_connection(self):
        self._teardown_popups()
        self._close_popup("warning_view")
        self._stop_typing_signal()
        if self.connection:
            try: self.connection.close()
            except Exception: pass
            self.connection = None
            # The room is gone, and so are its leaderboards — but open games stay open (home screen play).
            self.game_boards = {key: {} for key in GAME_KEYS}
            self._games_context_changed()

    # ------------------------------------------------------------------
    # Chat screen
    # ------------------------------------------------------------------

    def _build_chat_frame(self):
        self.chat_frame = tk.Frame(self, bg=BG_DARK)
        top = tk.Frame(self.chat_frame, bg=BG_PANEL, height=40)
        top.pack(side="top", fill="x")

        self.title_label = tk.Label(top, text="", bg=BG_PANEL, fg=FG_TEXT, font=TITLE_FONT)
        self.title_label.pack(side="left", padx=12, pady=8)

        make_button(top, "Disconnect", self.on_disconnect_clicked, bg=BTN_RED, hover_bg=BTN_RED_HOVER, padx=12, pady=5).pack(side="right", padx=12, pady=6)

        self.dnd_btn = make_button(top, "🔕 DND: OFF", self.on_dnd_toggle, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=12, pady=5)
        self.dnd_btn.pack(side="right", padx=(12, 0), pady=6)
        for bind in ("<Button-2>", "<Button-3>"):
            self.dnd_btn.bind(bind, lambda e: self.on_dnd_keybind_picker())
            self.dnd_btn.label.bind(bind, lambda e: self.on_dnd_keybind_picker())

        self.appearance_btn = make_button(top, "🎨", self._open_appearance, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=10, pady=5)
        self.appearance_btn.pack(side="right", padx=(12, 0), pady=6)

        self.warn_btn = make_button(top, "⚠ Warning", self._on_warn_btn_clicked, bg=self.WARN_YELLOW[0], hover_bg=self.WARN_YELLOW[1], padx=12, pady=5)  # shown by _refresh_warn_button

        body = tk.Frame(self.chat_frame, bg=BG_DARK)  # packed last — see the end of this method

        log_col = tk.Frame(body, bg=BG_DARK)
        log_col.pack(side="left", fill="both", expand=True)
        # The "New messages" button lives in its own strip UNDER the log. It used to float over the log, but on
        # macOS Tk scrolls a Text by copying pixels inside the window's one shared surface, and that copies
        # anything drawn over the Text too — smearing the button up the screen. Nothing overlaps the log now.
        self.jump_bar = tk.Frame(log_col, bg=BG_DARK)
        self.jump_bar.pack(side="bottom", fill="x")
        self.log = ScrolledText(log_col, bg=BG_DARK, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", state="disabled", wrap="word", padx=px(12), pady=px(8), font=CHAT_FONT, highlightthickness=0, bd=0, width=10, height=5,
                              spacing1=(0 if sys.platform == "darwin" else 2), spacing3=(0 if sys.platform == "darwin" else 2))
        self.log.pack(side="top", fill="both", expand=True)
        self.log.tag_configure("system", foreground=FG_MUTED, font=fnt(9, "italic"))
        self.log.tag_configure("private", foreground=COLOR_PALETTE["yellow"])
        self.log.tag_configure("timestamp", foreground=FG_MUTED, font=fnt(8))
        self.log.tag_configure("reaction_style", foreground=COLOR_PALETTE["yellow"], font=fnt(9))
        self.log.tag_configure("edited_mark", foreground=FG_MUTED, font=fnt(8, "italic"))
        self.log.tag_configure("deleted_mark", foreground=FG_MUTED, font=fnt(9, "italic"))
        self.log.tag_configure("quote", foreground=FG_MUTED, font=fnt(9, "italic"))
        self.log.tag_configure("flash", background=BTN_NEUTRAL)
        self.log.tag_configure("align_right", justify="right")
        self.log.tag_configure("align_left", justify="left")

        # One right-click handler for the whole log (finds the message under the
        # cursor) instead of two Tcl bindings per message.
        for bind in ("<Button-2>", "<Button-3>"):
            self.log.bind(bind, self._on_log_right_click)
        # Hide the "new messages" button once the reader scrolls back to the end
        # (also when the window is resized, which can put the end back in view).
        self.log.bind("<Configure>", lambda e: self.after_idle(self._sync_jump_btn), add="+")

        self.jump_btn = tk.Label(self.jump_bar, text="↓ New messages", bg=ACCENT, fg="white", font=fnt(9, "bold"), padx=8, pady=2, cursor="hand2")
        self.jump_btn.bind("<Button-1>", lambda e: self._scroll_to_bottom())
        # The wheel over the button would otherwise do nothing — pass it on to the log.
        for bind in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.jump_btn.bind(bind, self._wheel_over_jump_btn)
        # Every change of the view — wheel, trackpad, dragging the scrollbar, keys, a resize — reaches us
        # through the scrollbar callback, so the button can't miss the reader getting back to the bottom.
        self.log.configure(yscrollcommand=self._on_log_yscroll)

        member_panel = tk.Frame(body, bg=BG_PANEL, width=px(160))
        member_panel.pack(side="right", fill="y")
        member_panel.pack_propagate(False)
        tk.Label(member_panel, text="ONLINE", bg=BG_PANEL, fg=FG_MUTED, font=fnt(8, "bold")).pack(anchor="w", padx=10, pady=(10, 4))
        self.member_list_frame = tk.Frame(member_panel, bg=BG_PANEL)
        self.member_list_frame.pack(fill="both", expand=True, padx=10)

        self.typing_var = tk.StringVar(value="")
        self.typing_label = tk.Label(self.chat_frame, textvariable=self.typing_var, bg=BG_DARK, fg=FG_MUTED, font=fnt(9, "italic"), anchor="w")

        self.upload_var = tk.StringVar(value="")
        self.upload_row = tk.Frame(self.chat_frame, bg=BG_DARK)  # packed only while a transfer is in progress
        self.upload_label = tk.Label(self.upload_row, textvariable=self.upload_var, bg=BG_DARK, fg=COLOR_PALETTE["yellow"], font=fnt(9, "bold"), anchor="w")
        self.upload_label.pack(side="left", fill="x", expand=True)
        self.cancel_upload_btn = make_button(self.upload_row, "✕ Cancel", self._cancel_uploads, bg=BTN_RED, hover_bg=BTN_RED_HOVER, padx=8, pady=1, font=fnt(9, "bold"))

        self.mute_status_var = tk.StringVar(value="")
        self.mute_label = tk.Label(self.chat_frame, textvariable=self.mute_status_var, bg=BG_DARK, fg=COLOR_PALETTE["red"], font=fnt(9, "bold"), anchor="w")

        self.reply_bar = tk.Frame(self.chat_frame, bg=BG_PANEL)  # packed only while replying
        self.reply_label = tk.Label(self.reply_bar, text="", bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT, anchor="w")
        self.reply_label.pack(side="left", fill="x", expand=True, padx=(10, 4), pady=4)
        reply_close = tk.Label(self.reply_bar, text="✕", bg=BG_PANEL, fg=FG_MUTED, font=BOLD_FONT, cursor="hand2", padx=10)
        reply_close.pack(side="right")
        reply_close.bind("<Button-1>", lambda e: self._clear_reply())

        self.bottom_bar = tk.Frame(self.chat_frame, bg=BG_DARK)

        def tool_button(text, command):
            btn = make_button(self.bottom_bar, text, command, bg=BG_INPUT, hover_bg=BTN_NEUTRAL_HOVER, padx=10, pady=6)
            btn.pack(side="left", padx=(0, 6))
            return btn

        self.attach_btn = tool_button("📎", self.on_attach_file)
        self.sticker_btn = tool_button("🌠", self.on_sticker_picker)
        self.emoji_btn = tool_button("😀", self.on_emoji_picker)

        self.msg_entry = tk.Entry(self.bottom_bar, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", font=CHAT_FONT)
        self.msg_entry.pack(side="left", fill="x", expand=True, ipady=px(6))
        self.msg_entry.bind("<Return>", self.on_send)
        self.msg_entry.bind("<KeyRelease>", self.on_entry_key)
        self.msg_entry.bind("<Tab>", self.on_tab_autocomplete)
        self.msg_entry.bind("<Up>", self._on_up_arrow)
        self.msg_entry.bind("<Down>", self._on_down_arrow)
        self.msg_entry.bind("<Escape>", self._on_escape)
        self.msg_entry.bind("<<Paste>>", self._on_paste)  # Ctrl+V, Cmd+V and the right-click Paste all arrive as this
        self.msg_entry.bind("<FocusOut>", lambda e: self.after(150, self.destroy_suggestions))

        self.send_btn = make_button(self.bottom_bar, "Send", self.on_send, bg=ACCENT, hover_bg=ACCENT_HOVER, padx=16, pady=6)
        self.send_btn.pack(side="left", padx=(6, 0))

        # Pack order is how Tk shares out a short window: widgets packed first are satisfied first
        # and the last one packed is what gets squeezed. The log used to be packed first, so every
        # status line above the message box (uploading, muted, someone typing) shrank the chat bar —
        # sometimes to a sliver. Reserve the bottom strip first; the log gives way instead.
        self.bottom_bar.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        self.mute_label.pack(side="bottom", fill="x", padx=10)
        self.typing_label.pack(side="bottom", fill="x", padx=10)
        body.pack(fill="both", expand=True)

    def _set_input_state(self, enabled: bool):
        self.msg_entry.configure(state="normal" if enabled else "disabled")
        for btn in (self.send_btn, self.attach_btn, self.sticker_btn, self.emoji_btn):
            btn.set_enabled(enabled)

    # ---- mute / slowmode ----

    def _apply_mute_state(self, muted: bool, until: float = 0.0):
        self._cancel_timer("mute")
        self._set_input_state(not muted)
        until_text = f" until {format_until(until)}" if until else ""
        self.mute_status_var.set(f"🔇 You are muted{until_text} — messages won't send." if muted else "")

        if muted and until:
            # The host only tells us "you're muted until X" once; nothing pushes
            # an unmute when the timer simply runs out, so re-check locally.
            remaining_ms = max(0, int((until - time.time()) * 1000)) + 250
            self._set_timer("mute", remaining_ms, self._on_mute_expired)

    def _on_mute_expired(self):
        self._apply_mute_state(False)
        self.append_system_line("🔇 Your mute has expired — you can send messages again.")

    def _on_mute_status(self, payload):
        if payload == "0":
            return self._apply_mute_state(False)
        try: until = float(payload.partition(":")[2])
        except ValueError: until = 0.0
        self._apply_mute_state(True, until)

    def _on_slowmode_event(self, delay):
        self.slowmode_delay = delay
        if delay == 0.0: self._end_slowmode_cooldown()

    def _on_admin_status(self, payload):
        self.is_admin = payload == "1"
        if self.connection: self.connection.is_admin = self.is_admin
        self.append_system_line(f"Your admin privileges have been {'granted' if self.is_admin else 'revoked'}.")

    def _maybe_start_slowmode_cooldown(self):
        if self.slowmode_delay > 0 and not self.is_admin:
            self._set_input_state(False)
            self._slowmode_cd_end = time.time() + self.slowmode_delay
            self._tick_slowmode_cooldown()

    def _tick_slowmode_cooldown(self):
        remaining = self._slowmode_cd_end - time.time()
        if remaining <= 0:
            return self._end_slowmode_cooldown()
        if not self.mute_status_var.get().startswith("🔇"):
            self.mute_status_var.set(f"⏳ Slowmode is active, you cannot send messages for {remaining:.1f}s")
        self._set_timer("slowmode", 100, self._tick_slowmode_cooldown)

    def _end_slowmode_cooldown(self):
        self._cancel_timer("slowmode")
        if self.mute_status_var.get().startswith("🔇"):
            return  # still muted for a separate reason — leave that message/lock alone
        self.mute_status_var.set("")
        self._set_input_state(True)

    # ---- activity ranking for suggestions ----

    def _record_user_message_time(self, sender_name: str):
        key, now = sender_name.lower(), time.time()
        self.user_last_msg_time[key] = now
        times = [t for t in self.user_msg_times.get(key, []) if now - t <= SPAM_SUGGESTION_WINDOW]
        times.append(now)
        self.user_msg_times[key] = times

    def _rank_by_recent_activity(self, names: list) -> list:
        """Most messages within SPAM_SUGGESTION_WINDOW first — a shortcut for /mute /kick /ban."""
        now = time.time()
        def score(name):
            return sum(1 for t in self.user_msg_times.get(name.lower(), ()) if now - t <= SPAM_SUGGESTION_WINDOW)
        return sorted(names, key=lambda n: (-score(n), n.lower()))

    def _rank_by_idle_time(self, names: list) -> list:
        """Longest since their last message first (never-sent = most idle) — a shortcut for @ pings."""
        now = time.time()
        def idle_for(name):
            last = self.user_last_msg_time.get(name.lower())
            return float("inf") if last is None else now - last
        return sorted(names, key=lambda n: (-idle_for(n), n.lower()))

    # ---- live suggestions ----

    def evaluate_live_suggestions(self):
        text, cursor_pos = self.msg_entry.get(), self.msg_entry.index("insert")
        left_text = text[:cursor_pos]
        words = left_text.split(" ")
        suggestions = []

        if left_text.startswith("/"):
            base_cmd = words[0].lower()
            if len(words) == 1:
                is_host = isinstance(self.connection, HostConnection)
                commands = list(self.BASE_COMMANDS)
                if self.is_admin: commands.extend(self.ADMIN_COMMANDS)
                if is_host: commands.append("/rename")
                suggestions = [c for c in commands if c.startswith(base_cmd)]
            elif len(words) == 2:
                arg = words[1].lower()
                if base_cmd in self.PLAYER_ARG_COMMANDS:
                    suggestions = [n for n in self.current_roster if n.lower() != self.my_name.lower() and n.lower().startswith(arg)]
                    # Punitive actions: surface whoever's been most active
                    # recently first — usually who you're about to target.
                    if base_cmd in self.ACTIVITY_RANKED_COMMANDS:
                        suggestions = self._rank_by_recent_activity(suggestions)
                elif base_cmd == "/color":
                    suggestions = [c for c in COLOR_PALETTE if c.startswith(arg)]

        if words[-1].startswith("@"):
            query = words[-1][1:].lower()
            candidates = [n for n in self.current_roster if n.lower() != self.my_name.lower() and n.lower().startswith(query)]
            suggestions.extend(f"@{n}" for n in self._rank_by_idle_time(candidates) if f"@{n}" not in suggestions)

        self.current_suggestions = suggestions
        if suggestions: self.render_suggestion_popup()
        else: self.destroy_suggestions()

    def render_suggestion_popup(self):
        if not self.suggest_popup:
            self.suggest_popup = tk.Frame(self.chat_frame, bg=BG_PANEL, bd=1, relief="solid")
            self.suggest_listbox = tk.Listbox(
                self.suggest_popup, bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT,
                selectbackground=BTN_NEUTRAL, selectforeground="white",
                relief="flat", highlightthickness=0, activestyle="none",
            )
            self.suggest_listbox.pack(fill="both", expand=True, padx=4, pady=4)
            self.suggest_listbox.bind("<Button-1>", self._on_suggestion_clicked)

        self.suggest_listbox.delete(0, "end")
        self.suggest_listbox.insert("end", *(f"  {item}  " for item in self.current_suggestions))
        self.suggest_listbox.selection_set(0)
        self.suggest_listbox.configure(height=min(6, len(self.current_suggestions)))
        self.suggest_popup.update_idletasks()

        frame = self.chat_frame
        height = self.suggest_popup.winfo_reqheight()
        x = self.msg_entry.winfo_rootx() - frame.winfo_rootx()
        y = self.msg_entry.winfo_rooty() - frame.winfo_rooty() - height - 5
        self.suggest_popup.place(x=x, y=max(0, y), width=max(self.msg_entry.winfo_width() // 2, 220), height=height)
        self.suggest_popup.lift()

    def destroy_suggestions(self):
        if self.suggest_popup:
            try: self.suggest_popup.destroy()
            except Exception: pass
            self.suggest_popup = None
        self.current_suggestions = []

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
        left_text, right_text = text[:cursor_pos], text[cursor_pos:]
        words = left_text.split(" ")

        if len(words) == 1: new_left = chosen + " "
        elif left_text.endswith(" "): new_left = left_text + chosen + " "
        else:
            words[-1] = chosen
            new_left = " ".join(words) + " "

        self._set_entry_text(new_left + right_text, cursor=len(new_left))
        self.msg_entry.focus_set()

    def _move_suggestion(self, delta: int):
        count = len(self.current_suggestions)
        selection = self.suggest_listbox.curselection()
        current = selection[0] if selection else (count if delta < 0 else -1)
        new_idx = min(max(current + delta, 0), count - 1)
        self.suggest_listbox.selection_clear(0, "end")
        self.suggest_listbox.selection_set(new_idx)
        self.suggest_listbox.see(new_idx)

    def on_tab_autocomplete(self, event):
        if self.suggest_popup and self.current_suggestions:
            selection = self.suggest_listbox.curselection()
            self._apply_chosen_suggestion(self.current_suggestions[selection[0] if selection else 0])
        return "break"

    # ---- entry helpers: history, escape ----

    def _set_entry_text(self, text: str, cursor: int = None):
        self.msg_entry.delete(0, "end")
        self.msg_entry.insert(0, text)
        self.msg_entry.icursor("end" if cursor is None else cursor)
        self._last_entry_text = text
        self.destroy_suggestions()

    def _history_step(self, delta: int):
        if not self.sent_history: return "break"
        if delta < 0:
            if self._history_pos is None:
                self._history_draft = self.msg_entry.get()
                self._history_pos = len(self.sent_history) - 1
            else:
                self._history_pos = max(0, self._history_pos - 1)
        else:
            if self._history_pos is None: return "break"
            self._history_pos += 1
            if self._history_pos >= len(self.sent_history):
                self._history_pos = None
                self._set_entry_text(self._history_draft)
                return "break"
        self._set_entry_text(self.sent_history[self._history_pos])
        return "break"

    def _on_up_arrow(self, event):
        if self.suggest_popup and self.current_suggestions:
            self._move_suggestion(-1)
            return "break"
        return self._history_step(-1)

    def _on_down_arrow(self, event):
        if self.suggest_popup and self.current_suggestions:
            self._move_suggestion(1)
            return "break"
        return self._history_step(1)

    def _on_escape(self, event):
        open_pickers = [name for name in ("emoji", "stickers") if name in self._popups]
        for name in open_pickers:
            self._close_popup(name)
        if open_pickers:
            return "break"
        if self._reply_to is not None and not self.suggest_popup:
            self._clear_reply()
            return "break"
        if self.suggest_popup:
            self.destroy_suggestions()
        elif self._history_pos is not None:
            self._history_pos = None
            self._set_entry_text(self._history_draft)
        return "break"

    def _remember_sent(self, text: str):
        if not self.sent_history or self.sent_history[-1] != text:
            self.sent_history.append(text)
            del self.sent_history[:-self.HISTORY_MAX]

    # ---- sending ----

    def on_send(self, event=None):
        if not self.connection or str(self.msg_entry["state"]) == "disabled": return "break"
        text = self.msg_entry.get().strip()
        if not text: return "break"
        if len(text) > MAX_MESSAGE_CHARS:  # keep what they typed so they can trim it
            self.append_system_line(f"That message is {len(text):,} characters — the limit is {MAX_MESSAGE_CHARS:,}. Shorten it, or send it as a file.")
            return "break"
        self._set_entry_text("")
        self._history_pos = None

        first_word = text.split()[0].lower()
        if ENABLE_INVITE_CODES and first_word == "/invite":
            code = self._invite_code()
            if code:
                self.clipboard_clear()
                self.clipboard_append(code)
                self.append_system_line(f"Invite Code: {code} (copied). Paste it into the Room Code box to join this chat directly — no searching needed.")
            else:
                self.append_system_line("There's no Invite Code to show — you're not in a chat.")
            return "break"

        if first_word == "/clear":
            self._handle_clear_command(text.split())
            return "break"

        if first_word in ("/globalban", "/unglobalban", "/globalbans"):
            self._handle_global_ban_command(first_word, text.partition(" ")[2].strip())
            return "break"

        self._remember_sent(text)
        self._stop_typing_signal()
        reply, self._reply_to = (None if text.startswith("/") else self._reply_to), None  # replies only apply to ordinary messages
        self._clear_reply()
        self.connection.send_chat(text, reply)
        self._maybe_start_slowmode_cooldown()
        return "break"

    def _handle_clear_command(self, parts):
        if len(parts) > 1 and parts[1].isdigit():
            with self._log_edit():
                self.log.delete(self.log.index(f'end-1c - {int(parts[1])} lines'), "end")
            self._prune_attachments()
        elif messagebox.askyesno("Confirm Clear", "Are you sure you want to completely clear the chat log?"):
            with self._log_edit():
                self.log.delete("1.0", "end")
            self.photo_cache = []
            self._attachments.clear()
            self._hide_jump()

    def on_entry_key(self, event=None):
        if event and event.keysym in self.NON_EDIT_KEYSYMS: return
        text = self.msg_entry.get()
        changed = text != self._last_entry_text
        self._last_entry_text = text
        self.evaluate_live_suggestions()

        if not self.connection or not changed: return
        if text.strip():
            now = time.time()
            if not self.typing_active or (now - self.last_typing_sent > 1.0):
                self.connection.send_typing(True)
                self.typing_active, self.last_typing_sent = True, now
            self._set_timer("typing", int(TYPING_IDLE_TIMEOUT * 1000), self._stop_typing_signal)
        else:
            self._stop_typing_signal()

    def _stop_typing_signal(self):
        self._cancel_timer("typing")
        if self.typing_active and self.connection:
            self.connection.send_typing(False)
        self.typing_active, self.last_typing_sent = False, 0.0

    def _on_paste(self, event=None):
        """Text pastes exactly as before. If the clipboard holds an image (or copied files)
        instead, offer to send it as an attachment."""
        if str(self.msg_entry["state"]) == "disabled":
            return "break"
        try:
            self.clipboard_get()
            return None  # there's text on the clipboard — let the normal paste happen
        except tk.TclError:
            pass
        if ImageGrab is None or not self.connection:
            return None
        try:
            clip = ImageGrab.grabclipboard()
        except Exception:
            return None  # not supported on this system (e.g. Linux without xclip / wl-paste)
        if clip is None:
            return None
        ok, target = self._attachment_target()
        if not ok:
            return "break"
        if isinstance(clip, (list, tuple)):
            self._offer_pasted_files(clip, target)
        else:
            self._offer_pasted_image(clip, target)
        return "break"

    def _offer_pasted_image(self, image, target):
        popup = self._open_dialog("paste", "Send pasted image?", padx=18, pady=16)
        if popup is None:
            return
        try:
            if image.mode not in ("RGB", "RGBA", "L", "LA", "P"):
                image = image.convert("RGBA")
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            png = buf.getvalue()
            preview = image.copy()
            preview.thumbnail((380, 280))
            popup.photo = ImageTk.PhotoImage(preview)  # keep a reference alive
        except Exception as e:
            self._close_popup("paste")
            return messagebox.showerror("Paste", f"Couldn't read that image: {e}", parent=self)
        name = time.strftime("pasted_image_%H%M%S.png")

        def send():
            self._close_popup("paste")
            self._start_upload(name, lambda: (name, png), target)
            self.msg_entry.focus_set()

        tk.Label(popup, image=popup.photo, bg=BG_PANEL).pack()
        where = f"Whisper to {target}" if target else "Send to everyone"
        tk.Label(popup, text=f"{where}   ·   {format_size(len(png))}", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(pady=(8, 10))
        row = tk.Frame(popup, bg=BG_PANEL)
        row.pack(anchor="e")
        make_button(row, "Cancel", lambda: (self._close_popup("paste"), self.msg_entry.focus_set()), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=14, pady=5).pack(side="left", padx=(0, 8))
        make_button(row, "Send", send, bg=BTN_GREEN, hover_bg=BTN_GREEN_HOVER, padx=18, pady=5).pack(side="left")
        popup.bind("<Return>", lambda e: send())
        popup.focus_set()

    def _offer_pasted_files(self, paths, target):
        files = [p for p in paths if isinstance(p, str) and os.path.isfile(p)][:5]
        if not files:
            return
        listing = "\n".join(f"  •  {os.path.basename(p)}  ({format_size(os.path.getsize(p))})" for p in files)
        where = f"Whisper to {target}" if target else "Send to everyone"
        if not messagebox.askyesno("Send pasted files?", f"{where}:\n\n{listing}", parent=self):
            return
        for path in files:
            try:
                check_file_size(path)
            except (ValueError, OSError) as e:
                messagebox.showerror("Couldn't send", f"{os.path.basename(path)}: {e}", parent=self)
                continue
            self._start_upload(os.path.basename(path), to=target, path=path)

    def _attachment_target(self):
        """-> (ok, whisper_target). If the message box starts with "/whisper <name>", an
        attachment goes privately to that person; otherwise to everyone."""
        parts = self.msg_entry.get().split(None, 2)
        if not parts or parts[0].lower() != "/whisper":
            return True, None
        wanted = parts[1].lower() if len(parts) > 1 else ""
        for name in self.current_roster:
            if name.lower() == wanted and name.lower() != self.my_name.lower():
                return True, name
        messagebox.showinfo("Whisper a file", "To whisper a file, first type /whisper and someone's full name (e.g. /whisper Sam), then use the button again.", parent=self)
        return False, None

    def _refresh_upload_label(self):
        """One status line above the message box for files going out and coming in."""
        parts = []
        jobs = list(self._upload_jobs.values())
        if jobs:
            job = jobs[0]
            text = f"✖ Cancelling… {job['name']}" if job.get("cancelling") else f"⏳ Uploading and Sending… {job['name']}"
            if job.get("to"): text += f" (whisper to {job['to']})"
            if job.get("pct") is not None: text += f" {job['pct']:.0f}%"
            if len(jobs) > 1: text += f"  [{len(jobs)} in progress]"
            parts.append(text)
        if self._incoming:
            item = next(iter(self._incoming.values()))
            text = f"⬇ Receiving {item['filename']} from {item['sender']}… {item['pct']:.0f}%"
            if len(self._incoming) > 1: text += f"  [{len(self._incoming)} incoming]"
            parts.append(text)
        if not parts:
            self.upload_var.set("")
            self.upload_row.pack_forget()
            return
        self.upload_var.set("   ".join(parts))
        if not self.upload_row.winfo_manager():
            self.upload_row.pack(side="bottom", fill="x", padx=10, before=self.typing_label)
        if jobs and not self.cancel_upload_btn.winfo_manager():
            self.cancel_upload_btn.pack(side="right", padx=(8, 0))
        elif not jobs and self.cancel_upload_btn.winfo_manager():
            self.cancel_upload_btn.pack_forget()

    def _start_upload(self, filename: str, loader=None, to: str = None, path: str = None):
        """Sending a file — reading it, encrypting it, and pacing it to the connection — runs
        on a worker thread, so the window stays live and the label above the message box
        shows progress. Pass `path` to stream a file from disk (any size up to the limit),
        or `loader` returning (filename, bytes) for something already in memory."""
        conn = self.connection
        if conn is None:
            return
        self._job_seq += 1
        job, session, cancel = self._job_seq, self._session_id, threading.Event()
        self._upload_jobs[job] = {"name": filename, "to": to, "pct": None, "cancel": cancel}
        self._refresh_upload_label()
        last_pct = [-100.0]

        def report(ok, name=filename, error=None):
            self.event_queue.put(("upload_done", {"job": job, "session": session, "ok": ok, "filename": name, "error": error,
                                                  "cancelled": cancel.is_set() and not ok}))

        def progress(sent, size):
            pct = sent * 100.0 / size if size else 100.0
            if pct - last_pct[0] >= 2 or sent >= size:
                last_pct[0] = pct
                self.event_queue.put(("upload_progress", {"job": job, "session": session, "pct": pct}))

        def work():
            try:
                if path is not None:
                    conn.send_file(path, on_done=lambda ok: report(ok), to=to, on_progress=progress, cancel=cancel)
                else:
                    name, data = loader()
                    conn.send_file_bytes(name, data, on_done=lambda ok: report(ok, name), to=to, on_progress=progress, cancel=cancel)
            except Exception as e:
                report(False, filename, str(e))

        threading.Thread(target=work, daemon=True).start()

    def _cancel_uploads(self):
        """The ✕ Cancel button: stop everything we're currently sending."""
        for job in self._upload_jobs.values():
            job["cancel"].set()
            job["cancelling"] = True
        self._refresh_upload_label()

    def _on_upload_progress(self, payload):
        if payload.get("session") != self._session_id:
            return  # from a chat we've since left
        job = self._upload_jobs.get(payload["job"])
        if job is not None:
            job["pct"] = payload["pct"]
            self._refresh_upload_label()

    def _on_transfer_progress(self, payload):
        if payload.get("done"):
            self._incoming.pop(payload["msg_id"], None)
        else:
            self._incoming[payload["msg_id"]] = {"filename": payload["filename"], "sender": payload["sender"], "pct": payload["pct"] * 100}
        self._refresh_upload_label()

    def _on_upload_done(self, payload):
        if payload.get("session") != self._session_id:
            return  # a leftover from a chat we've since left — don't leak it into this one
        self._upload_jobs.pop(payload.get("job"), None)
        self._refresh_upload_label()
        if payload.get("cancelled"):
            self.append_system_line(f"Cancelled sending {payload['filename']}.")
        elif payload.get("error"):
            self.append_system_line(f"Couldn't send {payload['filename']}: {payload['error']}")
        elif not payload["ok"]:
            self.append_system_line(f"Couldn't send {payload['filename']}.")
        else:
            self._maybe_start_slowmode_cooldown()

    def on_attach_file(self):
        if not self.connection: return
        ok, target = self._attachment_target()
        if not ok: return
        path = filedialog.askopenfilename(title="Choose a file to send")
        if not path: return
        try:
            check_file_size(path)
        except ValueError as e: return messagebox.showerror("File too large", str(e))
        except OSError as e: return messagebox.showerror("Couldn't read file", str(e))
        self._start_upload(os.path.basename(path), to=target, path=path)

    # ---- Do Not Disturb ----

    def on_dnd_toggle(self):
        if not self.connection or (time.time() - self._dnd_cd < DND_ANNOUNCE_COOLDOWN): return
        self._dnd_cd, self.dnd_active = time.time(), not self.dnd_active
        self._set_dnd_button_style(self.dnd_active)

        self.dnd_btn.disabled = True
        self.dnd_btn.label.configure(text="🔕 Cooldown...")
        self._set_timer("dnd", int(DND_ANNOUNCE_COOLDOWN * 1000), self._restore_dnd_btn)
        self.connection.send_dnd(self.dnd_active)

    def _restore_dnd_btn(self):
        self.dnd_btn.disabled = False
        self._set_dnd_button_style(self.dnd_active)

    def _set_dnd_button_style(self, active: bool):
        bg, text = (BTN_RED, "🔕 DND: ON") if active else (BTN_NEUTRAL, "🔕 DND: OFF")
        self.dnd_btn.base_bg = bg
        self.dnd_btn.paint(bg)
        self.dnd_btn.label.configure(text=text)

    def _apply_dnd_keybind(self):
        """(Re)binds the DND shortcut, removing whichever one was active before."""
        old = self._active_dnd_bind
        if old:
            for unbind in (self.unbind_all, self.msg_entry.unbind):
                try: unbind(old)
                except tk.TclError: pass
            self._active_dnd_bind = None

        handler = lambda e: self._trigger_dnd_toggle()
        for attempt in (self.dnd_keybind, self.DEFAULT_DND_KEYBIND):
            try:
                self.bind_all(attempt, handler)
                # Bound on the entry too: instance bindings fire before the
                # Entry class binding (which types the character), so "break"
                # stops a letter-key bind from also typing that letter.
                self.msg_entry.bind(attempt, handler)
            except tk.TclError:
                continue
            self.dnd_keybind = self._active_dnd_bind = attempt
            return

    def _trigger_dnd_toggle(self):
        self.on_dnd_toggle()
        return "break"

    def on_dnd_keybind_picker(self):
        popup = self._open_dialog("dnd_bind", "DND Keybind", padx=16, pady=14)
        if popup is None: return
        tk.Label(popup, text="Press any key combination to bind Do Not Disturb...", bg=BG_PANEL, fg=FG_TEXT, font=BOLD_FONT).pack(anchor="w", pady=(0, 10))
        tk.Label(popup, text=f"Current bind: {self.dnd_keybind}   (Esc to cancel)", bg=BG_INPUT, fg=FG_TEXT, font=CHAT_FONT).pack(fill="x", pady=5)

        def capture(e):
            if e.keysym.endswith(("_L", "_R")): return  # a bare modifier press
            is_mac = sys.platform == "darwin"
            parts = []
            if e.state & 4: parts.append("Control")
            if e.state & 1: parts.append("Shift")
            if is_mac:
                # Tk's Aqua port reports Command under the bit X11 calls "Mod1",
                # and Command/Option are its native modifier names on macOS —
                # "<Alt-x>" would never fire on a real Command press there.
                if e.state & 8: parts.append("Command")
                if e.state & 16: parts.append("Option")
            elif e.state & 131072 or e.state & 8:
                parts.append("Alt")

            keyname = e.keysym
            if is_mac and (e.state & 16):
                # Option composes accents (Option+e -> dead key); recover the physical key.
                keyname = MAC_VIRTUAL_KEYCODE_TO_KEY.get(e.keycode, keyname)
            parts.append(keyname)

            self.dnd_keybind = "<" + "-".join(parts) + ">"
            self._apply_dnd_keybind()
            self._save_settings()
            self._close_popup("dnd_bind")

        popup.bind("<KeyPress>", capture)

    # ---- changelog ----

    def on_show_changelog(self):
        popup = self._open_dialog("changelog", "Changelog", padx=16, pady=14, resizable=True)
        if popup is None: return
        # Buttons first (packed at the bottom) so shrinking the window never hides Close.
        make_button(popup, "Close", lambda: self._close_popup("changelog"), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=12, pady=5).pack(side="bottom", pady=(10, 0))

        text = ScrolledText(popup, width=64, height=20, bg=BG_INPUT, fg=FG_TEXT, font=CHAT_FONT, wrap="word", relief="flat", padx=8, pady=8)
        text.pack(fill="both", expand=True)
        text.tag_configure("ver", font=(CHAT_FONT[0], CHAT_FONT[1], "bold"), foreground=ACCENT)

        entries = full_changelog()
        if not entries:
            text.insert("1.0", "No changelog entries yet.")
        for i, e in enumerate(entries):
            if i: text.insert("end", "\n\n")
            text.insert("end", f"v{e.get('version', '?')} — {e.get('date', 'unknown date')}\n", ("ver",))
            text.insert("end", e.get("notes") or "(no notes)")
        text.configure(state="disabled")

    # ---- updates ----

    def on_check_updates(self):
        """The "Check for Updates" link: the same check as at launch, but it always says what it found, in the banner on the main menu."""
        self._start_update_check(manual=True)

    def _start_update_check(self, manual: bool):
        if not UPDATE_MANIFEST_URL:
            if manual:
                self._set_update_banner("No update server is configured yet (UPDATE_MANIFEST_URL, near the top of chat_gui.py).", kind="error", hide_after=6)
            return
        if manual:
            self._set_update_banner(f"Checking for updates (you have v{VERSION})…")
        threading.Thread(target=self._async_check_updates, args=(manual,), daemon=True).start()

    def _set_update_banner(self, text, buttons=(), kind="info", hide_after=None):
        """Shows `text` (and buttons: (label, command, 'green'|'neutral')) in the banner across the top of the main menu."""
        self._cancel_timer("update_banner")
        self.update_banner_label.configure(text=text, fg={"info": FG_TEXT, "ok": COLOR_PALETTE["green"], "error": COLOR_PALETTE["red"]}[kind])
        for w in self.update_banner_buttons.winfo_children(): w.destroy()
        palette = {"green": (BTN_GREEN, BTN_GREEN_HOVER), "neutral": (BTN_NEUTRAL, BTN_NEUTRAL_HOVER)}
        for label, command, style in buttons:
            bg, hover = palette[style]
            make_button(self.update_banner_buttons, label, command, bg=bg, hover_bg=hover, padx=10, pady=3).pack(side="left", padx=(8, 0))
        self.update_banner.place(relx=0, rely=0, relwidth=1.0)
        self.update_banner.lift()
        if hide_after:
            self._set_timer("update_banner", int(hide_after * 1000), self._hide_update_banner)

    def _hide_update_banner(self):
        self._cancel_timer("update_banner")
        self.update_banner.place_forget()

    def _async_check_updates(self, manual: bool = True):
        try:
            manifest = fetch_update_manifest(UPDATE_MANIFEST_URL)
        except Exception as e:
            self.event_queue.put(("update_check_result", {"ok": False, "error": str(e), "manual": manual}))
            return
        self.event_queue.put(("update_check_result", {"ok": True, "manifest": manifest, "manual": manual}))

    def _handle_update_check_result(self, result):
        manual = result.get("manual", True)
        dismiss = ("✕", self._hide_update_banner, "neutral")
        if not result["ok"]:
            if manual:  # a failed check at launch stays quiet (offline, GitHub down…)
                self._set_update_banner(f"Couldn't check for updates: {result['error']}", (dismiss,), kind="error")
            return
        manifest = result["manifest"]
        remote_version = manifest.get("version", "?")
        if not is_newer_version(remote_version, VERSION):
            self._pending_manifest = None
            if manual:
                self._set_update_banner(f"✔ You're up to date (v{VERSION}).", kind="ok", hide_after=5)
            return
        self._pending_manifest = manifest
        self._set_update_banner(
            f"✨ Update available: v{remote_version} (you have v{VERSION})",
            (("Update now", self._start_update_install, "green"), ("What's new", self._show_update_notes, "neutral"), dismiss),
        )

    def _show_update_notes(self):
        manifest = self._pending_manifest
        if not manifest: return
        popup = self._open_dialog("update_notes", "What's new", padx=24, pady=20)
        if popup is None: return
        tk.Label(popup, text=f"What's new in v{manifest.get('version', '?')}", bg=BG_PANEL, fg=FG_TEXT, font=fnt(14, "bold")).pack(anchor="w")
        tk.Label(popup, text=manifest.get("notes") or "(no notes for this release)", bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT, wraplength=px(420), justify="left").pack(anchor="w", pady=(10, 0))
        tk.Label(popup, text="It's signature-verified before anything is installed.", bg=BG_PANEL, fg=FG_MUTED, font=fnt(9)).pack(anchor="w", pady=(10, 0))
        make_button(popup, "Close", lambda: self._close_popup("update_notes"), bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=18, pady=5).pack(anchor="e", pady=(14, 0))

    def _start_update_install(self):
        if not self._pending_manifest: return
        self._set_update_banner("Downloading and verifying the update…")
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
        if not result["ok"]:
            self._set_update_banner(f"Update failed and was NOT installed: {result['error']}", (("✕", self._hide_update_banner, "neutral"),), kind="error")
            return
        self._pending_manifest = None
        self._set_update_banner(
            f"✔ Update installed and verified (your previous version is kept as {os.path.basename(result['backup'])}). Restart to use it.",
            (("Restart now", self._restart_app, "green"), ("Later", self._hide_update_banner, "neutral")), kind="ok",
        )

    def _restart_app(self):
        self._save_settings()
        self._teardown_connection()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def on_close(self):
        self._save_settings()
        self._teardown_connection()
        self.destroy()

    # ---- minigames (Snake, Flappy Bird) ----

    def in_room(self) -> bool:
        return self.connection is not None

    def game_player_name(self) -> str:
        """Who a game's score belongs to: our chat name in a room, otherwise whatever is in the name box."""
        if self.connection is not None and self.my_name:
            return self.my_name
        return self.name_entry.get().strip() or self.my_name or "Player"

    def on_open_games(self, event=None):
        """Ctrl+Shift+S — works anywhere in the app, in a chat or not."""
        if self._game_picker is not None:
            try:
                self._game_picker.lift()
                self._game_picker.focus_force()
                return "break"
            except tk.TclError:
                self._game_picker = None
        self._game_picker = GamePicker(self)
        return "break"

    def open_game(self, key: str):
        win = self._game_wins.get(key)
        if win is not None:
            try:
                win.deiconify()
                win.lift()
                win.focus_force()
                return
            except tk.TclError:
                self._game_wins.pop(key, None)
        self._game_wins[key] = GAME_WINDOWS[key](self, self._game_color())

    def _game_color(self) -> str:
        """The snake / bird wears your name's colour — a flat colour or one of the gradients."""
        fallback = HOST_COLOR if isinstance(self.connection, HostConnection) else FG_TEXT
        return self.known_colors.get(self.game_player_name().lower()) or fallback

    def game_name_color(self, name: str) -> str:
        color = self.known_colors.get(name.lower(), FG_TEXT)
        palette = GRADIENT_PALETTES.get(color)
        if not palette:
            return color
        # A flat label can't show a gradient — use its brightest shade so it stays readable on the dark background.
        luminance = lambda c: 0.299 * int(c[1:3], 16) + 0.587 * int(c[3:5], 16) + 0.114 * int(c[5:7], 16)
        return max(palette, key=luminance)

    def game_best(self, key: str) -> int:
        bests = self.settings.get("game_bests")
        value = bests.get(key, 0) if isinstance(bests, dict) else 0
        return value if isinstance(value, int) and value > 0 else 0

    def game_report(self, key: str, score: int, playing: bool):
        """Called by a game window: update our row on its board, remember a new personal best, and tell the room."""
        name = self.game_player_name()
        entry = self.game_boards[key].setdefault(name.lower(), {"name": name, "best": 0, "score": 0, "playing": False})
        entry.update(name=name, score=score, playing=playing)
        entry["best"] = max(entry["best"], score)
        if score > self.game_best(key):
            bests = self.settings.get("game_bests")
            if not isinstance(bests, dict):
                bests = self.settings["game_bests"] = {}
            bests[key] = score
            self._game_best_unsaved = True
        if not playing and getattr(self, "_game_best_unsaved", False):  # a game just ended: write the new best down
            self._game_best_unsaved = False
            self._save_settings()
        if self.connection is not None:
            self.connection.send_game(key, score, playing)
        self._refresh_games(key)

    def _on_game_event(self, payload):
        board = self.game_boards.get(payload["game"])
        if board is not None:
            board[payload["entry"]["name"].lower()] = payload["entry"]
            self._refresh_games(payload["game"])

    def _refresh_games(self, key: str = None):
        for game, win in list(self._game_wins.items()):
            if key is None or game == key:
                win.refresh_leaderboard()

    def _games_context_changed(self):
        """We joined or left a chat: every open game redraws its board and says where it stands (to the
        room, if we're in one — otherwise just to the home-screen board)."""
        for win in list(self._game_wins.values()):
            try: win.rejoin()
            except tk.TclError: pass

    # ------------------------------------------------------------------
    # Stickers + emoji
    # ------------------------------------------------------------------

    def on_sticker_picker(self):
        if Image is None or ImageDraw is None:
            return messagebox.showerror("Error", "Pillow (PIL) is required to use stickers.")
        self._toggle_picker("stickers", self.sticker_btn, self._build_sticker_picker)

    def _picker_cell(self, parent, row, col, command, text=None, image=None, on_right=None, muted=False):
        cell = tk.Label(
            parent, text=text, image=image, font=fnt(9) if muted else BOLD_FONT, bg=BG_INPUT,
            fg=FG_MUTED if muted else FG_TEXT, padx=10, pady=10, cursor="hand2", bd=1, relief="solid",
        )
        cell.grid(row=row, column=col, padx=4, pady=4)
        cell.bind("<Button-1>", lambda e: command())
        if on_right:
            for bind in ("<Button-2>", "<Button-3>"):
                cell.bind(bind, lambda e: on_right())
        cell.bind("<Enter>", lambda e: cell.configure(bg=BTN_NEUTRAL))
        cell.bind("<Leave>", lambda e: cell.configure(bg=BG_INPUT))
        return cell

    def _build_sticker_picker(self, popup):
        popup.thumbs = {}  # PhotoImage refs live as long as the popup does
        grid = tk.Frame(popup, bg=BG_PANEL)
        grid.pack()

        for col, name in enumerate(self.BUILTIN_STICKERS):
            self._picker_cell(grid, 0, col, lambda n=name: self.send_sticker(n), text=name)

        custom = _load_custom_stickers()
        row, col = 1, 0
        for name, b64data in custom.items():
            try:
                thumb = Image.open(io.BytesIO(base64.b64decode(b64data))).resize((64, 64), Image.LANCZOS)
                popup.thumbs[name] = ImageTk.PhotoImage(thumb)
            except Exception:
                continue
            self._picker_cell(grid, row, col, lambda n=name: self.send_sticker(n), image=popup.thumbs[name], on_right=lambda n=name: self._delete_custom_sticker(n))
            col += 1
            if col >= 5:
                col, row = 0, row + 1

        self._picker_cell(grid, row, col, self.on_upload_sticker, text="➕\nUpload", muted=True)
        if custom:
            tk.Label(popup, text="Right-click a custom sticker to delete it", bg=BG_PANEL, fg=FG_MUTED, font=fnt(8)).pack(pady=(4, 0))

    def _reopen_sticker_picker(self):
        self._close_popup("stickers")
        self.on_sticker_picker()

    def on_upload_sticker(self):
        path = filedialog.askopenfilename(
            title="Choose a sticker image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"), ("All files", "*.*")],
        )
        if not path:
            return

        custom = _load_custom_stickers()
        if len(custom) >= MAX_CUSTOM_STICKERS:
            self._close_popup("stickers")
            return messagebox.showerror("Too many stickers", f"You can have at most {MAX_CUSTOM_STICKERS} custom stickers. Delete one first (right-click it).")

        name = simpledialog.askstring("Name this sticker", "Short name (shown as the filename when sent):", parent=self)
        if not name or not name.strip():
            return
        name = re.sub(r"[^A-Za-z0-9_\- ]", "", name.strip())[:20] or "sticker"

        try:
            img = Image.open(path).convert("RGB")
        except Exception as e:
            self._close_popup("stickers")
            return messagebox.showerror("Couldn't load image", str(e))

        img.thumbnail((240, 240), Image.LANCZOS)
        square = Image.new("RGB", (240, 240), color=BG_PANEL)
        square.paste(img, ((240 - img.width) // 2, (240 - img.height) // 2))
        bio = io.BytesIO()
        square.save(bio, format="JPEG", quality=88)

        custom[name] = base64.b64encode(bio.getvalue()).decode("ascii")
        _save_custom_stickers(custom)
        self._reopen_sticker_picker()  # now showing the new sticker

    def _delete_custom_sticker(self, name):
        custom = _load_custom_stickers()
        if custom.pop(name, None) is not None:
            _save_custom_stickers(custom)
        self._reopen_sticker_picker()

    def _render_builtin_sticker(self, name: str) -> bytes:
        size = 240
        img = Image.new("RGB", (size, size), color=BG_PANEL)
        d = ImageDraw.Draw(img)
        d.rectangle([10, 10, size - 10, size - 10], fill=self.BUILTIN_STICKERS[name], outline="white", width=6)

        font = None
        if ImageFont is not None:
            for font_size in (64, 52, 40, 32):
                try: font = ImageFont.load_default(size=font_size)
                except Exception: font = None  # older Pillow: no sized default font
                if font is None or d.textbbox((0, 0), name, font=font)[2] <= size - 50:
                    break
        if font is not None:
            left, top, right, bottom = d.textbbox((0, 0), name, font=font)
            d.text(((size - (right - left)) // 2 - left, (size - (bottom - top)) // 2 - top), name, fill="black", font=font)
        else:
            d.text((size // 2 - 4 * len(name), size // 2 - 6), name, fill="black")

        bio = io.BytesIO()
        img.save(bio, format="JPEG", quality=90)
        return bio.getvalue()

    def send_sticker(self, name):
        self._close_popup("stickers")
        if not self.connection: return
        ok, target = self._attachment_target()
        if not ok: return

        if name in self.BUILTIN_STICKERS:
            img_bytes = self._render_builtin_sticker(name)
        else:
            b64data = _load_custom_stickers().get(name)
            if not b64data: return
            img_bytes = base64.b64decode(b64data)

        filename = f"Sticker_{name}.jpg"
        self._start_upload(filename, lambda: (filename, img_bytes), target)

    def on_emoji_picker(self):
        self._toggle_picker("emoji", self.emoji_btn, self._build_emoji_picker)

    def _build_emoji_picker(self, popup):
        grid = tk.Frame(popup, bg=BG_PANEL)
        grid.pack()
        for i, emoji_char in enumerate(EMOJI_PICKER_SET):
            btn = tk.Label(grid, text=emoji_char, font=EMOJI_FONT, bg=BG_PANEL, fg=FG_TEXT, padx=4, pady=4, cursor="hand2")
            btn.grid(row=i // 10, column=i % 10)
            btn.bind("<Button-1>", lambda e, ch=emoji_char: self._insert_emoji(ch))
            btn.bind("<Enter>", lambda e, w=btn: w.configure(bg=BTN_NEUTRAL))
            btn.bind("<Leave>", lambda e, w=btn: w.configure(bg=BG_PANEL))

    def _insert_emoji(self, emoji_char: str):
        self.msg_entry.insert("insert", emoji_char)
        self._close_popup("emoji")
        self.on_entry_key()  # so the typing indicator reflects the inserted emoji

    # ------------------------------------------------------------------
    # Event loop
    # ------------------------------------------------------------------

    def poll_queue(self):
        for _ in range(self.MAX_EVENTS_PER_POLL):
            try: kind, payload = self.event_queue.get_nowait()
            except queue.Empty: break
            handler = self._event_handlers.get(kind)
            if handler is None: continue
            try:
                handler(payload)
            except Exception:
                traceback.print_exc()  # one bad event must never stop the UI loop
        # Poll quickly while busy, lazily when idle.
        self.after(30 if not self.event_queue.empty() else 70, self.poll_queue)

    def _remember_author(self, msg_id: str, author: str):
        self._msg_authors[msg_id] = author
        if len(self._msg_authors) > 3000:
            self._msg_authors.pop(next(iter(self._msg_authors)))

    def _on_chat_event(self, payload):
        self.known_colors.update(payload.get("colors") or {})
        self.append_chat_line(payload["raw"], payload.get("msg_id"))

    def _on_colormap_event(self, colors):
        self.known_colors.update(colors)
        self.update_roster(self.current_roster)
        for win in list(self._game_wins.values()):
            win.set_color(self._game_color())  # keep the snake / bird matching our name colour
            win.refresh_leaderboard()          # …and the names on the leaderboard

    # ------------------------------------------------------------------
    # Chat log rendering
    # ------------------------------------------------------------------

    def _color_tag(self, color_hex: str) -> str:
        tag = f"c_{color_hex.lstrip('#')}"
        if tag not in self.known_tags:
            self.log.tag_configure(tag, foreground=color_hex)
            self.known_tags.add(tag)
        return tag

    def _insert_name(self, name: str, color_value: str):
        """Insert a name into the chat log. A gradient-unlocked sender's name
        gets its own uniquely-tagged instance (so hovering one occurrence in
        the history doesn't animate every other), with the same
        static-gradient/hover-animation the roster uses."""
        palette = GRADIENT_PALETTES.get(color_value)
        if palette is None:
            self.log.insert("end", name, (self._color_tag(color_value),))
            return

        self._rainbow_instance_seq += 1
        group_tag = f"rbname_{self._rainbow_instance_seq}"
        char_tags = []
        for i, ch in enumerate(name):
            tag = f"{group_tag}_{i}"
            self.log.tag_configure(tag, foreground=palette[i % len(palette)])
            self.log.insert("end", ch, (tag, group_tag))
            char_tags.append(tag)

        def apply_colors(offset):
            for i, tag in enumerate(char_tags):
                self.log.tag_configure(tag, foreground=palette[(i + offset) % len(palette)])

        on_enter, on_leave = self._wire_rainbow_hover(apply_colors, len(palette))
        self.log.tag_bind(group_tag, "<Enter>", on_enter)
        self.log.tag_bind(group_tag, "<Leave>", on_leave)

    def append_chat_line(self, raw: str, msg_id: str = None):
        prefix, sep, rest = raw.partition(": ")
        is_chat = bool(sep)
        mine = is_chat and prefix.lower() == self.my_name.lower()

        with self._log_append(force_scroll=mine):
            start_index = self.log.index("end-1c")
            self.log.insert("end", f"[{time.strftime('%H:%M')}] ", ("timestamp",))

            if is_chat:
                self._record_user_message_time(prefix)
                self._insert_name(prefix, self.known_colors.get(prefix.lower(), FG_TEXT))
                self.log.insert("end", ": ")
                body_start = self.log.index("end-1c")
                self.log.insert("end", rest)

                end_index = self.log.index("end-1c")
                self.log.tag_add("align_right" if mine else "align_left", start_index, end_index)
                if msg_id:
                    self.log.tag_add(f"msg_{msg_id}", start_index, end_index)
                    self.log.tag_add(f"body_{msg_id}", body_start, end_index)  # just the text — what edit/delete replace
                    self._remember_author(msg_id, prefix)
                    if mine:
                        self._my_messages[msg_id] = rest
                    self.log.mark_set(f"react_mark_{msg_id}", end_index)
                    self.log.mark_gravity(f"react_mark_{msg_id}", "left")
            else:
                self.log.insert("end", raw)

            self.log.insert("end", "\n")

        if not mine:
            self._note_unread()

    def append_whisper_line(self, payload):
        sender, to, msg_id, body = payload["from"], payload["to"], payload["msg_id"], payload["text"]
        mine = sender.lower() == self.my_name.lower()
        label = f"[whisper to {to}] " if mine else f"[whisper from {sender}] "
        with self._log_append(force_scroll=mine):
            start_index = self.log.index("end-1c")
            self.log.insert("end", f"[{time.strftime('%H:%M')}] ", ("timestamp",))
            self.log.insert("end", label, ("private",))
            body_start = self.log.index("end-1c")
            self.log.insert("end", body, ("private",))
            end_index = self.log.index("end-1c")
            self.log.tag_add("align_right" if mine else "align_left", start_index, end_index)
            if msg_id:
                self.log.tag_add(f"msg_{msg_id}", start_index, end_index)
                self.log.tag_add(f"body_{msg_id}", body_start, end_index)
                self._remember_author(msg_id, sender)
                self._whisper_ids.add(msg_id)
                if mine:
                    self._my_messages[msg_id] = body
                self.log.mark_set(f"react_mark_{msg_id}", end_index)
                self.log.mark_gravity(f"react_mark_{msg_id}", "left")
            self.log.insert("end", "\n")
        if not mine:
            self._note_unread()

    def append_system_line(self, text: str):
        with self._log_append():
            self.log.insert("end", f"* {localize_times(text)}\n", ("system",))

    def append_private_line(self, text: str):
        with self._log_append():
            self.log.insert("end", f"[private] {localize_times(text)}\n", ("private",))

    # ---- reactions ----

    def _on_log_right_click(self, event):
        index = self.log.index(f"@{event.x},{event.y}")
        for tag in self.log.tag_names(index):
            if tag.startswith("msg_"):
                self.show_reaction_menu(event, tag[len("msg_"):])
                return "break"

    def _build_message_menu(self, msg_id):
        """The right-click menu for a message/attachment, or None if there's nothing to offer."""
        menu = tk.Menu(self, tearoff=0, bg=BG_PANEL, fg=FG_TEXT)
        attachment = self._attachments.get(msg_id)
        private = msg_id in self._whisper_ids or (attachment is not None and attachment["whisper"])
        entries = 0
        if attachment is not None:
            menu.add_command(label="Save As...", command=lambda: self._save_attachment(attachment))
            entries += 1
            mine, noun = attachment["mine"], "attachment"
        elif private:
            mine, noun = msg_id in self._my_messages, "message"  # whispers can't be reacted to
        else:
            for emoji in self.REACTION_CHOICES:
                menu.add_command(label=emoji, command=lambda e=emoji: self.send_reaction(msg_id, e))
                entries += 1
            mine, noun = msg_id in self._my_messages, "message"

        known = msg_id in self._msg_authors
        am_host = isinstance(self.connection, HostConnection)
        actions = []  # (label, command) — the things you can do with this message, below the emoji row
        if known and not private:
            actions.append(("Reply", lambda: self.start_reply(msg_id)))
        if known and not mine and not am_host:
            actions.append((f"Report {noun}", lambda: self.start_report(msg_id)))
        if mine:
            if attachment is None:
                actions.append(("Edit message", lambda: self.start_edit(msg_id)))
            actions.append((f"Delete {noun}", lambda: self.start_delete(msg_id)))
        elif self.is_admin and not private:  # is_admin is also True for the host; admins never see (or delete) whispers
            actions.append((f"Delete {noun} (admin)", lambda: self.start_delete(msg_id)))
        if actions:
            if entries:
                menu.add_separator()
            for label, command in actions:
                menu.add_command(label=label, command=command)
            entries += len(actions)
        return menu if entries else None

    def show_reaction_menu(self, event, msg_id):
        menu = self._build_message_menu(msg_id)
        if menu is None:
            return
        try: menu.tk_popup(event.x_root, event.y_root)
        finally: menu.grab_release()

    # ---- editing / deleting messages ----

    # ---- replying to and reporting messages ----

    def start_reply(self, msg_id):
        author = self._msg_authors.get(msg_id)
        if author is None or not self.connection:
            return
        attachment = self._attachments.get(msg_id)
        if attachment is not None:
            snippet = f"[attachment] {attachment['filename']}"
        else:
            ranges = self.log.tag_ranges(f"body_{msg_id}")
            snippet = self.log.get(ranges[0], ranges[1]) if ranges else ""
        snippet = " ".join(snippet.split())[:80]
        self._reply_to = {"id": msg_id, "author": author, "snippet": snippet}
        self.reply_label.configure(text=f"↪ Replying to {author}: {snippet}")
        if not self.reply_bar.winfo_manager():
            self.reply_bar.pack(side="bottom", fill="x", padx=10, pady=(0, 4), before=self.mute_label)
        self.msg_entry.focus_set()

    def _clear_reply(self):
        self._reply_to = None
        if self.reply_bar.winfo_manager():
            self.reply_bar.pack_forget()

    def _on_reply(self, payload):
        """Draw the little quote line above a message that replies to another."""
        ranges = self.log.tag_ranges(f"msg_{payload['msg_id']}")
        if not ranges:
            return
        follow = self._at_bottom()
        mine = self._msg_authors.get(payload["msg_id"], "").lower() == self.my_name.lower()
        quote_tag = f"quote_{payload['msg_id']}"
        with self._log_edit():
            self.log.insert(str(ranges[0]), f"   ↪ {payload['author']}: {payload['snippet']}\n", ("quote", quote_tag, "align_right" if mine else "align_left"))
        self.log.tag_bind(quote_tag, "<Button-1>", lambda e, target=payload["to"]: self._jump_to(target))
        if follow:
            self.log.see("end")

    def _jump_to(self, msg_id):
        ranges = self.log.tag_ranges(f"msg_{msg_id}")
        if not ranges:
            return self.append_system_line("That message is no longer in the chat log.")
        self.log.see(ranges[0])
        self.log.tag_add("flash", ranges[0], ranges[1])
        self.after(1200, lambda: self.log.tag_remove("flash", "1.0", "end"))

    def start_report(self, msg_id):
        if not self.connection or msg_id not in self._msg_authors:
            return
        noun = "attachment" if msg_id in self._attachments else "message"
        reason = simpledialog.askstring(f"Report {noun}", f"Report this {noun} to the admins.\nWhy? (optional — a few words is plenty)", parent=self)
        if reason is None:
            return  # cancelled
        self.connection.send_report(msg_id, reason.strip())

    def start_edit(self, msg_id):
        current = self._my_messages.get(msg_id)
        if not self.connection or current is None:
            return
        new_text = simpledialog.askstring("Edit message", "Edit your message:", initialvalue=current, parent=self)
        if new_text is None:
            return
        new_text = new_text.strip()
        if not new_text:
            return messagebox.showinfo("Edit message", "An edited message can't be empty — use Delete instead.", parent=self)
        if new_text != current:
            self.connection.send_edit(msg_id, new_text)

    def start_delete(self, msg_id):
        if not self.connection:
            return
        attachment = self._attachments.get(msg_id)
        noun = "attachment" if attachment is not None else ("whisper" if msg_id in self._whisper_ids else "message")
        mine = attachment["mine"] if attachment is not None else msg_id in self._my_messages
        prompt = f"Delete your {noun} for everyone?" if mine else f"Delete this {noun} for everyone?"
        if messagebox.askyesno(f"Delete {noun}", prompt, parent=self):
            self.connection.send_delete(msg_id)

    def _on_msg_edit(self, payload):
        msg_id, new_text = payload["msg_id"], payload["text"]
        if msg_id in self._my_messages:
            self._my_messages[msg_id] = new_text
        ranges = self.log.tag_ranges(f"body_{msg_id}")
        if not ranges:
            return  # not in our log (we joined after it, or it was trimmed away)

        start, end = str(ranges[0]), str(ranges[1])
        msg_tag, edited_tag = f"msg_{msg_id}", f"edited_{msg_id}"
        align = "align_right" if msg_id in self._my_messages else "align_left"
        with self._log_edit():
            self.log.delete(start, end)
            colour = ("private",) if msg_id in self._whisper_ids else ()
            self.log.insert(start, new_text, (f"body_{msg_id}", msg_tag, align) + colour)
            body_end = f"{start}+{len(new_text)}c"
            marker = self.log.tag_ranges(edited_tag)
            if marker:
                anchor = str(marker[1])  # already marked "(edited)" by an earlier edit
            else:
                label = " (edited)"
                self.log.insert(body_end, label, ("edited_mark", edited_tag, msg_tag, align))
                anchor = f"{body_end}+{len(label)}c"
            # Deleting the old text collapsed the reactions anchor; put it back at the end of the line.
            self.log.mark_set(f"react_mark_{msg_id}", anchor)
            self.log.mark_gravity(f"react_mark_{msg_id}", "left")

    def _delete_attachment_line(self, msg_id, author, deleter, attachment):
        ranges = self.log.tag_ranges(f"attach_{msg_id}")
        if ranges:
            start, end = str(ranges[0]), str(ranges[1])
            own = author is None or author.lower() == deleter.lower()
            note = ": [attachment deleted]\n" if own else f": [attachment deleted by {deleter}]\n"
            align = "align_right" if (author or "").lower() == self.my_name.lower() else "align_left"
            with self._log_edit():
                # The range runs from " sent an attachment (...):" to the end of the preview /
                # download card, so deleting it also destroys the embedded widget.
                self.log.delete(start, end)
                self.log.insert(start, note, ("deleted_mark", align))
                self.log.tag_remove(f"msg_{msg_id}", "1.0", "end")  # no more menu on this line
        if attachment is not None:
            self._release_attachment(attachment)

    def _on_msg_delete(self, payload):
        msg_id, deleter = payload["msg_id"], payload["deleter"]
        author = self._msg_authors.get(msg_id)
        attachment = self._attachments.pop(msg_id, None)
        if attachment is not None or self.log.tag_ranges(f"attach_{msg_id}"):
            return self._delete_attachment_line(msg_id, author, deleter, attachment)
        self._my_messages.pop(msg_id, None)
        self.message_reactions.pop(msg_id, None)
        ranges = self.log.tag_ranges(f"body_{msg_id}")
        if not ranges:
            return

        start, end = str(ranges[0]), str(ranges[1])
        msg_tag = f"msg_{msg_id}"
        own = author is None or author.lower() == deleter.lower()
        note = "[message deleted]" if own else f"[message deleted by {deleter}]"
        align = "align_right" if (author or "").lower() == self.my_name.lower() else "align_left"
        with self._log_edit():
            # Later text first, so `start`/`end` stay valid: reactions, then the "(edited)" label, then the body.
            for tag in (f"react_text_{msg_id}", f"edited_{msg_id}"):
                r = self.log.tag_ranges(tag)
                if r:
                    self.log.delete(r[0], r[1])
            self.log.delete(start, end)
            self.log.insert(start, note, ("deleted_mark", align))
            self.log.tag_remove(msg_tag, "1.0", "end")  # no more reactions / edit / delete on this line
            try: self.log.mark_unset(f"react_mark_{msg_id}")
            except tk.TclError: pass

    def send_reaction(self, msg_id, emoji):
        if self.connection:
            self.connection.send_react(msg_id, emoji)

    def add_reaction(self, msg_id, emoji, sender_name):
        if not sender_name:
            return
        per_message = self.message_reactions.setdefault(msg_id, {})
        reactors = per_message.setdefault(emoji, set())
        key = sender_name.lower()
        if key in reactors:
            reactors.discard(key)  # toggle off — clicking your own reaction again removes it
            if not reactors:
                del per_message[emoji]
                if not per_message:
                    del self.message_reactions[msg_id]
        else:
            reactors.add(key)  # a set, so a stray duplicate is naturally idempotent
        self.render_reactions(msg_id)

    def render_reactions(self, msg_id):
        mark_name = f"react_mark_{msg_id}"
        try: self.log.index(mark_name)
        except tk.TclError: return  # that message was trimmed away (or never had an id)

        react_tag = f"react_text_{msg_id}"
        with self._log_edit():
            ranges = self.log.tag_ranges(react_tag)
            if ranges: self.log.delete(ranges[0], ranges[1])
            if reactions := self.message_reactions.get(msg_id):
                summary = "  [" + " ".join(f"{e} {len(reactors)}" for e, reactors in reactions.items()) + "]"
                self.log.insert(mark_name, summary, (react_tag, "reaction_style"))

    # ---- attachments ----

    def render_incoming_file(self, payload):
        sender, filename, thumb = payload["sender"], payload["filename"], payload.get("thumb")
        data, path = payload.get("data"), payload.get("path")
        size = payload.get("size") or (len(data) if data is not None else 0)
        msg_id = payload.get("msg_id")
        mine = sender.lower() == self.my_name.lower()
        # `data` is held in memory for files up to INLINE_FILE_BYTES; larger ones live in a file at `path`.
        attachment = {"data": data, "path": path, "temp": bool(payload.get("temp")), "filename": filename, "size": size,
                      "photo": None, "mine": mine, "whisper": bool(payload.get("to"))}

        with self._log_append(force_scroll=mine):
            start_index = self.log.index("end-1c")
            self.log.insert("end", f"[{time.strftime('%H:%M')}] ", ("timestamp",))
            self._insert_name(sender, self.known_colors.get(sender.lower(), FG_TEXT))
            attach_start = self.log.index("end-1c")
            to = payload.get("to") or ""
            if to:
                header = f" whispered an attachment to {to} ({filename}):\n" if mine else f" whispered you an attachment ({filename}):\n"
            else:
                header = f" sent an attachment ({filename}):\n"
            self.log.insert("end", header, ("private",) if to else ())

            photo = None
            if thumb is not None and ImageTk is not None:
                try: photo = ImageTk.PhotoImage(thumb)
                except Exception: photo = None
            attachment["photo"] = photo

            if photo is not None:
                self.photo_cache.append(photo)
                self.log.image_create("end", image=photo)
            else:
                embed = tk.Frame(self.log, bg=BG_PANEL, bd=1, relief="solid", padx=12, pady=8)
                tk.Label(embed, text=f"📁  {filename}", bg=BG_PANEL, fg=FG_TEXT, font=BOLD_FONT).pack(side="left", padx=(0, 14))
                tk.Label(embed, text=f"({format_size(size)})", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(side="left", padx=(0, 14))
                make_button(embed, "Download", lambda: self._save_attachment(attachment), bg=BTN_GREEN, hover_bg=BTN_GREEN_HOVER, padx=10, pady=4).pack(side="right")
                if msg_id:  # widgets inside the log don't pass clicks on to it — wire the menu to the card itself
                    self._bind_menu_recursive(embed, msg_id)
                self.log.window_create("end", window=embed)

            self.log.insert("end", "\n\n")
            end_index = self.log.index("end-1c")
            self.log.tag_add("align_right" if mine else "align_left", start_index, end_index)
            if msg_id:
                self.log.tag_add(f"msg_{msg_id}", start_index, end_index)
                self.log.tag_add(f"attach_{msg_id}", attach_start, end_index)  # what a delete replaces
                self._remember_author(msg_id, sender)
                self._attachments[msg_id] = attachment

        if not mine:
            self._note_unread()

    def _save_attachment(self, attachment):
        if attachment["data"] is not None:
            return self._save_file_to_disk(attachment["data"], attachment["filename"])
        source = attachment.get("path")
        if not source or not os.path.exists(source):
            return messagebox.showerror("Error", "That file is no longer available.")
        dest = filedialog.asksaveasfilename(initialfile=attachment["filename"], title="Save file as")
        if not dest:
            return
        self.append_system_line(f"Saving {attachment['filename']} ({format_size(attachment['size'])})…")
        threading.Thread(target=self._copy_file_worker, args=(source, dest), daemon=True).start()

    def _copy_file_worker(self, source: str, dest: str):
        """Copying a multi-hundred-MB file takes a while — never on the UI thread."""
        try:
            shutil.copyfile(source, dest)
            self.event_queue.put(("system", f"Saved to {dest}"))
        except OSError as e:
            self.event_queue.put(("system", f"Couldn't save the file: {e}"))

    def _bind_menu_recursive(self, widget, msg_id):
        for bind in ("<Button-2>", "<Button-3>"):
            widget.bind(bind, lambda e, m=msg_id: self.show_reaction_menu(e, m))
        for child in widget.winfo_children():
            self._bind_menu_recursive(child, msg_id)

    def _save_file_to_disk(self, data: bytes, filename: str):
        if path := filedialog.asksaveasfilename(initialfile=filename, title="Save file as"):
            try:
                with open(path, "wb") as f: f.write(data)
                messagebox.showinfo("Saved", f"File saved to:\n{path}")
            except OSError as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")

    # ------------------------------------------------------------------
    # Member list + typing indicator
    # ------------------------------------------------------------------

    def update_roster(self, names):
        me = self.my_name
        roster = [me] + sorted((n for n in names if n.lower() != me.lower()), key=str.lower)
        signature = tuple((n, self.known_colors.get(n.lower(), FG_TEXT)) for n in roster)
        self.current_roster = roster
        if signature == self._roster_sig:
            return  # nothing visible changed — keep the existing widgets (and any hover animation)
        self._roster_sig = signature

        for child in self.member_list_frame.winfo_children(): child.destroy()
        for n, color in signature:
            palette = GRADIENT_PALETTES.get(color)
            if palette:
                self._build_rainbow_name_widget(self.member_list_frame, n, palette).pack(fill="x", pady=2, anchor="w")
            else:
                tk.Label(self.member_list_frame, text=n, bg=BG_PANEL, fg=color, anchor="w", font=CHAT_FONT).pack(fill="x", pady=2)

    def _wire_rainbow_hover(self, apply_colors, palette_len: int = None):
        """Shared 'static gradient by default, colors shift while hovering'
        driver. `apply_colors(offset)` recolors whatever is being animated; it
        may raise tk.TclError if the widget/tag is gone (a roster refresh or
        trimmed chat line can destroy it mid-animation) — that's a normal stop
        condition. Returns (on_enter, on_leave) to bind."""
        palette_len = palette_len or len(RAINBOW_PALETTE)
        anim = {"offset": 0, "active": False}

        def safe_apply(offset):
            try:
                apply_colors(offset)
                return True
            except tk.TclError:
                anim["active"] = False
                return False

        def tick():
            if not anim["active"]:
                return
            anim["offset"] = (anim["offset"] + 1) % palette_len
            if safe_apply(anim["offset"]) and anim["active"]:
                self.after(150, tick)

        def on_enter(e):
            if not anim["active"]:
                anim["active"] = True
                tick()

        def on_leave(e):
            anim["active"] = False
            safe_apply(0)

        return on_enter, on_leave

    def _build_rainbow_name_widget(self, parent, name: str, palette: list = None):
        """A name in a small single-line Text widget with one color tag per
        character — the same technique as the chat log (separate Labels carry
        per-widget padding that visibly spaces the letters apart)."""
        palette = palette or RAINBOW_PALETTE
        txt = tk.Text(
            parent, height=1, width=max(len(name), 1), bg=BG_PANEL, fg=FG_TEXT,
            bd=0, highlightthickness=0, font=CHAT_FONT, wrap="none",
            cursor="arrow", padx=0, pady=0, takefocus=0,
        )
        txt.insert("1.0", name)
        txt.configure(state="disabled")

        char_tags = []
        for i in range(len(name)):
            tag = f"c{i}"
            txt.tag_add(tag, f"1.{i}", f"1.{i + 1}")
            txt.tag_configure(tag, foreground=palette[i % len(palette)])
            char_tags.append(tag)

        def apply_colors(offset):
            for i, tag in enumerate(char_tags):
                txt.tag_configure(tag, foreground=palette[(i + offset) % len(palette)])

        on_enter, on_leave = self._wire_rainbow_hover(apply_colors, len(palette))
        txt.bind("<Enter>", on_enter)
        txt.bind("<Leave>", on_leave)
        return txt

    def update_typing(self, names):
        """`names` is the authoritative list of who's typing right now."""
        now, me = time.time(), self.my_name.lower()
        self.typing_last_seen = {n: now for n in names if n.lower() != me}
        self._render_typing_var()
        if self.typing_last_seen: self._ensure_typing_prune()

    def _render_typing_var(self):
        now = time.time()
        active = [n for n, seen in self.typing_last_seen.items() if now - seen <= TYPING_DISPLAY_TIMEOUT]
        if not active: self.typing_var.set("")
        elif len(active) == 1: self.typing_var.set(f"{active[0]} is typing...")
        else: self.typing_var.set(f"{', '.join(active)} are typing...")

    def _ensure_typing_prune(self):
        if "typing_prune" not in self._timers:
            self._set_timer("typing_prune", 500, self._typing_prune)

    def _typing_prune(self):
        """Expires 'is typing' entries whose START was never followed by a STOP.
        Only runs while someone is actually showing as typing."""
        now = time.time()
        stale = [n for n, seen in self.typing_last_seen.items() if now - seen > TYPING_DISPLAY_TIMEOUT]
        for n in stale: del self.typing_last_seen[n]
        if stale: self._render_typing_var()
        if self.typing_last_seen: self._ensure_typing_prune()


def main():
    enable_hidpi()   # before the first window exists
    app = ChatApp()
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        try: input("\nSomething crashed (see above). Press Enter to close this window...")
        except Exception: pass
        sys.exit(1)
