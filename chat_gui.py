#!/usr/bin/env python3
"""
chat_gui.py — v1.4.9b — ENCRYPTED instant messenger with a desktop GUI.

Changes in 1.4.9b:
- Everyone can edit or delete their own messages (right-click a message).
  Admins (and the host) can also delete other people's messages. The host
  can't have its messages deleted by an admin. Edited messages show
  "(edited)"; deleted ones become "[message deleted]".
- The admin log (host + admins) records every edit (old -> new text) and
  delete (the text that was removed), with who did it.
- Backwards compatible: edit/delete updates are only sent to clients that
  announced support, so 1.4.9a/1.4.8x members just keep seeing the original
  message instead of stray protocol text.

Changes in 1.4.9a:
- Fixed the "New messages" button sometimes staying on screen while you were
  already at the bottom of the chat (most often right after starting a room,
  seen on macOS). The button now re-checks once the window has finished laying
  out, and also when the window is resized.

Changes in 1.4.9 (tidy-up + UI/UX efficiency pass — no protocol changes,
so 1.4.9 interoperates with 1.4.8x):
- Connecting no longer freezes the window (ban-list check moved off the UI
  thread); Connect shows a "Connecting..." state; Enter connects from any
  field; display name + DND keybind are remembered between launches.
- Chat log only auto-scrolls when you're already at the bottom (with a
  "New messages" jump button otherwise); trimmed past MAX_LOG_LINES.
- Up/Down recall sent messages, Esc closes pop-ups, unread count in the
  window title, member list only redraws when something changed, typing
  notices only sent when the text actually changes, image thumbnails are
  prepared off the UI thread, pickers anchor to their buttons.
- Robustness: a bad event can't stop the UI event loop; stale events from
  a closed session can't leak into the next one; bare "/ban" etc. show
  usage instead of being posted as chat; host /color refreshes instantly.
- Code: shared JSON helpers (atomic saves), table-driven moderation
  commands and event dispatch, de-duplicated slowmode/file/unlock code.

Fixes/features in 1.4.8d (and the earlier 1.4.8 patches):
- Added a device-level global ban system, separate from the in-room
  /ipban: a device fingerprint (shown to hosts on connect, alongside
  their IP) can go on a signed ban list every client checks before
  hosting/joining. Gated by possession of a private key that's never
  distributed with the app (not a password — nothing in public source
  can stay secret). Like any client-side check, a technical user could
  still bypass it — a real deterrent, not an unbreakable lock. Inert
  (zero network calls) unless explicitly configured.

Fixes in 1.4.8:
- Snake leaderboard shows every player ranked, not just a top few.
- Fixed a real bug where an unexpected error while handling a message
  mid-session could silently skip cleanup, leaving a "ghost" user stuck
  in the room until the app restarted (blocked that name from
  reconnecting the whole time).
- Added a second secret gradient unlock (blue-toned) alongside the
  existing one — codes intentionally not written here, same as before.
- Host can now IP-ban someone directly by address, even if they're not
  currently connected, via a new host-only command.

Fixes in 1.4.7:
- Rainbow name hover animation now works in the chat log too, not just
  the sidebar — each message instance animates independently. Fixed the
  sidebar rendering rainbow names with abnormally spaced-out letters.
- Added Snake: press Ctrl+Shift+S to open it (single-player for now).
  Host plays plain white, rainbow-unlocked plays a moving rainbow
  snake, everyone else gets a random color. High scores save locally
  and show as a small leaderboard in the game window.

Fixes in 1.4.6:
- Added a secret rainbow unlock: entering a specific hidden phrase in
  the "Host IP" field (instead of an address) gives your name an
  animated rainbow treatment — a static gradient in chat, and in the
  member list it actually shifts/moves while you hover over it. Host
  color stays plain white as always.

Fixes in 1.4.5c:
- Fixed "View Changelog" clipping into "Check for Updates" on the connect
  screen (Mac only) — the gap was a hardcoded pixel offset that didn't
  account for macOS rendering text taller at the same font size. Now
  sized from actual rendered text height instead of a fixed guess.

Fixes in 1.4.5b:
- Host can now change their own color as many times as they want,
  overriding the usual once-per-session limit that still applies to guests.

Fixes in 1.4.5a:
- Fixed a major bug where the connection handshake kept failing.

Fixes/features in 1.4.5:
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
import platform
import uuid
import urllib.request
import urllib.error
import traceback
import tkinter as tk
from contextlib import contextmanager
from tkinter import filedialog, messagebox, scrolledtext, simpledialog

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
    from PIL import Image, ImageTk, ImageDraw, ImageFont
except ImportError:
    Image = ImageTk = ImageDraw = ImageFont = None

if sys.platform == "darwin":
    ensure_installed("pyobjus", required=False)

VERSION = "1.4.9b"

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
RAINBOW_UNLOCK_PREFIX = "__RAINBOW_UNLOCK__:"
BLUE_UNLOCK_PREFIX = "__BLUE_UNLOCK__:"
FINGERPRINT_PREFIX = "__FINGERPRINT__:"
EDIT_PREFIX = "__EDIT__:"          # guest -> host: "msg_id|new text"; host -> clients: "msg_id|editor|new text"
DELETE_PREFIX = "__DELETE__:"      # guest -> host: "msg_id";          host -> clients: "msg_id|deleter"
FEATURES_PREFIX = "__FEATURES__:"  # each side announces optional features it understands
FEATURE_EDIT = "edit"              # edit/delete of messages (added in 1.4.9b)
HOST_FEATURES = frozenset({FEATURE_EDIT})

# ---- Secret gradient unlocks ----
# Typed into the "Host IP" field on the join screen instead of an actual
# address. Letters + symbols only (no digits) so they can never collide
# with a real IP:port and misfire the discovery/parsing logic below.
# Deliberately kept out of the changelog text (see EMBEDDED_CHANGELOG) —
# describe the feature there, never the literal codes.
RAINBOW_SECRET_CODE = ":prism:"
BLUE_SECRET_CODE = ":glacier:"
# Stored in place of a hex color for an unlocked user — every place
# that renders a name checks GRADIENT_PALETTES for its color_value and
# draws the matching gradient instead of a flat color.
RAINBOW_SENTINEL = "RAINBOW"
BLUE_SENTINEL = "BLUE_GRADIENT"
RAINBOW_PALETTE = ["#FF5555", "#FFA347", "#FFE066", "#57F287", "#00C8C8", "#5B8CFF", "#C77DFF"]
BLUE_PALETTE = ["#0B2545", "#13315C", "#134074", "#1B5299", "#3E7CB1", "#6D9DC5", "#8FC0E9"]
GRADIENT_PALETTES = {RAINBOW_SENTINEL: RAINBOW_PALETTE, BLUE_SENTINEL: BLUE_PALETTE}
# code -> (sentinel, unlock prefix to send once connected)
GRADIENT_UNLOCK_CODES = {
    RAINBOW_SECRET_CODE: (RAINBOW_SENTINEL, RAINBOW_UNLOCK_PREFIX),
    BLUE_SECRET_CODE: (BLUE_SENTINEL, BLUE_UNLOCK_PREFIX),
}

# ---- Snake minigame (single-player for now) ----
SNAKE_KEYBIND = "<Control-Shift-KeyPress-S>"
SNAKE_COLS = 24
SNAKE_ROWS = 18
SNAKE_CELL_PX = 20
SNAKE_TICK_MS = 130
SNAKE_HIGHSCORES_FILE = app_path("chat_gui_snake_highscores.json")
SETTINGS_FILE = app_path("chat_gui_settings.json")

def _load_snake_highscores() -> dict:
    return load_json(SNAKE_HIGHSCORES_FILE, dict)

def _save_snake_highscore(name: str, score: int):
    scores = _load_snake_highscores()
    key = name.lower()
    if score > scores.get(key, 0):
        scores[key] = score
        save_json(SNAKE_HIGHSCORES_FILE, scores)

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


class SnakeWindow(tk.Toplevel):
    """Single-player Snake. Opened via the secret SNAKE_KEYBIND. Not
    networked — each person plays their own local game — but everyone
    who plays on this machine ends up on the same local high-score
    list, so it still works like a shared leaderboard over time."""

    ARROW_DIRECTIONS = {
        "Up": (0, -1), "w": (0, -1), "W": (0, -1),
        "Down": (0, 1), "s": (0, 1), "S": (0, 1),
        "Left": (-1, 0), "a": (-1, 0), "A": (-1, 0),
        "Right": (1, 0), "d": (1, 0), "D": (1, 0),
    }

    def __init__(self, app, player_name: str, color_value: str):
        super().__init__(app)
        self.app = app
        self.player_name = player_name
        self.color_value = color_value  # a hex color, or RAINBOW_SENTINEL

        self.title("Snake")
        self.configure(bg=BG_DARK, padx=12, pady=12)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.game = SnakeGame()
        self._tick_job = None
        self._rainbow_offset = 0

        canvas_w, canvas_h = SNAKE_COLS * SNAKE_CELL_PX, SNAKE_ROWS * SNAKE_CELL_PX
        self.canvas = tk.Canvas(self, width=canvas_w, height=canvas_h, bg=BG_PANEL, highlightthickness=0)
        self.canvas.pack()

        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, bg=BG_DARK, fg=FG_TEXT, font=CHAT_FONT).pack(pady=(8, 0))
        tk.Label(self, text="Arrows or WASD to move — Space to restart after a game over", bg=BG_DARK, fg=FG_MUTED, font=(CHAT_FONT[0], 9)).pack()

        self.leaderboard_frame = tk.Frame(self, bg=BG_DARK)
        self.leaderboard_frame.pack(fill="x", pady=(10, 0))
        self._render_leaderboard()

        for keysym, vec in self.ARROW_DIRECTIONS.items():
            self.bind(f"<KeyPress-{keysym}>", lambda e, v=vec: self.game.set_direction(*v))
        self.bind("<space>", lambda e: self._restart_if_dead())
        self.bind("<Escape>", lambda e: self._on_close())

        self._set_status()
        self.focus_set()
        self._loop()

    def _restart_if_dead(self):
        if not self.game.alive:
            self.game.reset()
            self._rainbow_offset = 0
            self._set_status()

    def _set_status(self):
        if self.game.alive:
            self.status_var.set(f"Score: {self.game.score}")
        else:
            self.status_var.set(f"Game over — score {self.game.score}. Press Space to try again.")

    def _loop(self):
        if self.game.alive:
            self.game.tick()
            if not self.game.alive:
                _save_snake_highscore(self.player_name, self.game.score)
                self._render_leaderboard()
            self._set_status()
        self._draw()
        self._tick_job = self.after(SNAKE_TICK_MS, self._loop)

    def _segment_color(self, index: int) -> str:
        palette = GRADIENT_PALETTES.get(self.color_value)
        if palette:
            return palette[(index + self._rainbow_offset) % len(palette)]
        return self.color_value

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

    def _render_leaderboard(self):
        for w in self.leaderboard_frame.winfo_children(): w.destroy()
        tk.Label(self.leaderboard_frame, text="High Scores", bg=BG_DARK, fg=FG_MUTED, font=BOLD_FONT).pack(anchor="w")
        scores = _load_snake_highscores()
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        if not ranked:
            tk.Label(self.leaderboard_frame, text="No scores yet — be the first!", bg=BG_DARK, fg=FG_MUTED, font=CHAT_FONT).pack(anchor="w")
            return
        for i, (name, score) in enumerate(ranked, 1):
            tk.Label(self.leaderboard_frame, text=f"{i}. {name} — {score}", bg=BG_DARK, fg=FG_TEXT, font=CHAT_FONT).pack(anchor="w")

    def _on_close(self):
        if self._tick_job:
            try: self.after_cancel(self._tick_job)
            except Exception: pass
            self._tick_job = None
        if getattr(self.app, "_snake_win", None) is self:
            self.app._snake_win = None
        self.destroy()

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
    if len(fresh) != len(entries):
        save_recent_hosts(fresh)
    return fresh

def save_recent_hosts(entries: list):
    save_json(RECENT_HOSTS_FILE, entries[:RECENT_HOSTS_MAX_ENTRIES])

def remember_recent_host(room_code: str, host_ip: str, port: int):
    entries = [e for e in load_recent_hosts() if not (e.get("room_code") == room_code and e.get("host_ip") == host_ip and e.get("port") == port)]
    entries.insert(0, {"room_code": room_code, "host_ip": host_ip, "port": port, "last_connected": time.time()})
    save_recent_hosts(entries[:RECENT_HOSTS_MAX_ENTRIES])

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

def fetch_global_banlist() -> dict:
    raw = _https_get(GLOBAL_BANLIST_URL, timeout=8.0)
    data = json.loads(raw.decode("utf-8"))
    if "entries" not in data or "signature" not in data:
        raise ValueError("Ban list is missing required fields.")
    return data

def verify_global_banlist(data: dict) -> list:
    """Returns the verified entry list, or raises ValueError. The
    signature covers the exact JSON-serialized entries list, so a
    tampered or appended entry fails verification rather than being
    silently trusted."""
    if not UPDATE_PUBLIC_KEY_B64:
        raise ValueError("No signing key configured — refusing to trust an unverifiable ban list.")
    entries = data["entries"]
    payload = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    try:
        pubkey = Ed25519PublicKey.from_public_bytes(base64.b64decode(UPDATE_PUBLIC_KEY_B64))
        pubkey.verify(base64.b64decode(data["signature"]), payload)
    except InvalidSignature:
        raise ValueError("Ban list signature is INVALID — ignoring it.")
    except Exception as e:
        raise ValueError(f"Could not verify the ban list: {e}")
    return entries

def check_global_ban() -> dict:
    """Returns a matching ban entry {fingerprint, reason, date} if this
    machine is banned, or None. Fails OPEN: any network/parse/
    verification problem is treated as 'not banned' rather than
    locking out an innocent person over a network hiccup — this was
    never meant to be a hard security gate, just a real deterrent."""
    if not GLOBAL_BANLIST_URL:
        return None
    try:
        entries = verify_global_banlist(fetch_global_banlist())
    except Exception:
        return None
    my_fp = get_machine_fingerprint()
    for entry in entries:
        if entry.get("fingerprint") == my_fp:
            return entry
    return None

def _load_local_signing_key():
    """Loads the Ed25519 PRIVATE key from a local file that is never
    distributed with the app (see sign_release.py's own warnings about
    this same file). Returns None if it isn't present — which is the
    normal, expected case for literally everyone except the person who
    holds it, and is exactly what makes /globalban only usable by them."""
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

def perform_globalban(fingerprint: str, reason: str) -> str:
    """Composes and signs an updated global ban list, gated purely by
    local possession of the private signing key. MUST be invoked
    directly by the local UI layer (never routed over the network to
    run on someone else's machine) — the key check is only meaningful
    against the filesystem of whoever actually typed the command, and
    a guest's mod commands normally execute on the HOST's machine, not
    their own, which would silently check the wrong computer."""
    privkey = _load_local_signing_key()
    if privkey is None:
        return "This command requires the signing key file, which only the app's publisher has."

    if not fingerprint:
        return "Usage: /globalban <fingerprint> [reason]"

    entries = []
    if GLOBAL_BANLIST_URL:
        try:
            entries = verify_global_banlist(fetch_global_banlist())
        except Exception as e:
            return f"Could not fetch/verify the current ban list — aborting rather than risk silently dropping existing entries. ({e})"

    entries = [e for e in entries if e.get("fingerprint") != fingerprint]
    entries.append({"fingerprint": fingerprint, "reason": reason, "date": time.strftime("%Y-%m-%d")})

    signed = sign_global_banlist(entries, privkey)
    out_path = app_path("global_banlist_signed.json")
    if not save_json(out_path, signed, indent=2):
        return "Signed the ban list but couldn't write it to disk."

    return f"Signed a global ban for fingerprint {fingerprint}. Upload {os.path.basename(out_path)} to wherever GLOBAL_BANLIST_URL points to make it live ({len(entries)} total entries)."


# ---- Changelog ----
# EMBEDDED_CHANGELOG is the static release history baked into this
# build — add one entry per release when you bump VERSION. Anything
# installed via OTA *after* this build additionally gets appended to
# CHANGELOG_FILE (a small local JSON file next to the script) at
# install time, so the in-app viewer stays complete going forward
# without needing the whole history re-embedded on every release.
EMBEDDED_CHANGELOG = [
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
    by_version = {e["version"]: e for e in EMBEDDED_CHANGELOG}
    for e in _load_local_changelog():
        by_version[e["version"]] = e
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

    def record_message(self, msg_id: str, author: str, text: str):
        """Remembers who sent a message so later edits/deletes can be authorised and
        logged. An id we already know is never reassigned — otherwise someone could
        re-send a victim's id and take over their message."""
        if not msg_id or len(msg_id) > 32:
            return
        with self.lock:
            if msg_id in self.messages:
                return
            self.messages[msg_id] = {"author": author, "text": text}
            while len(self.messages) > self.MAX_TRACKED_MESSAGES:
                self.messages.pop(next(iter(self.messages)))

    def _emit(self, kind: str, payload: dict):
        if self.on_message_event:
            self.on_message_event(kind, payload)

    def edit_message(self, msg_id: str, editor: str, new_text: str):
        """Authors only. Returns an error message for the requester, or None on
        success (or when nothing changed)."""
        new_text = new_text.strip()
        if not new_text:
            return "An edited message can't be empty — delete it instead."
        with self.lock:
            record = self.messages.get(msg_id)
            if record is None:
                return "That message can't be edited any more."
            if record["author"].lower() != editor.lower():
                return "You can only edit your own messages."
            old_text = record["text"]
            if old_text == new_text:
                return None
            record["text"] = new_text
        self.broadcast_feature(FEATURE_EDIT, f"{EDIT_PREFIX}{msg_id}|{editor}|{new_text}")
        self._emit("msg_edit", {"msg_id": msg_id, "text": new_text, "editor": editor})
        self.log_admin_action(editor, f'edited their message: "{_clip(old_text)}" → "{_clip(new_text)}"')
        return None

    def delete_message(self, msg_id: str, deleter: str, deleter_is_admin: bool):
        """Authors may delete their own; admins (and the host) may delete anyone's
        except the host's. Returns an error message, or None on success."""
        with self.lock:
            record = self.messages.get(msg_id)
            if record is None:
                return "That message can't be deleted any more."
            author, text = record["author"], record["text"]
            own = author.lower() == deleter.lower()
            if not own and not deleter_is_admin:
                return "You can only delete your own messages."
            if not own and self.is_host(author):
                return "You cannot delete the host's messages."
            del self.messages[msg_id]  # gone for good — it can't be edited or deleted again
        self.broadcast_feature(FEATURE_EDIT, f"{DELETE_PREFIX}{msg_id}|{deleter}")
        self._emit("msg_delete", {"msg_id": msg_id, "deleter": deleter})
        if own:
            self.log_admin_action(deleter, f'deleted their own message: "{_clip(text)}"')
        else:
            self.log_admin_action(deleter, f'deleted {author}\'s message: "{_clip(text)}"')
        return None

    def set_features(self, sock, features):
        with self.lock:
            if sock in self.clients:
                self.clients[sock]["features"] = set(features)

    def broadcast_feature(self, feature: str, text: str):
        """Like broadcast(), but only to clients that announced `feature` — so older
        versions never receive protocol text they'd display as a chat line."""
        with self.lock:
            targets = [s for s, info in self.clients.items() if feature in info.get("features", ())]
        for s in targets:
            self.send_private(s, text)

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
        with self.lock:
            self.clients[sock] = {
                "name": name, "ip": ip, "muted_until": 0.0,
                "muted_by": None, "mute_reason": None, "kicked": False,
                "features": set(),
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

    def set_fingerprint(self, sock, fingerprint: str):
        with self.lock:
            if sock in self.clients:
                self.clients[sock]["fingerprint"] = fingerprint

    def _find_socket(self, predicate):
        with self.lock:
            return next((s for s, info in self.clients.items() if predicate(info)), None)

    def find_socket_by_name(self, name):
        lowered = name.lower()
        return self._find_socket(lambda info: info["name"].lower() == lowered)

    def find_socket_by_ip(self, ip):
        return self._find_socket(lambda info: info.get("ip") == ip)

    def is_name_occupied(self, name):
        lowered = name.lower()
        with self.lock:
            self._purge_expired()
            if any(info["name"].lower() == lowered for info in self.clients.values()):
                return True
            return lowered in self.ghost_mutes

    def _purge_expired(self):
        """Caller must hold self.lock."""
        now = time.time()
        for k in [k for k, v in self.ghost_mutes.items() if now >= v["muted_until"]]:
            del self.ghost_mutes[k]
        for ip in [ip for ip, info in self.banned_ips.items() if now >= info["until"]]:
            del self.banned_ips[ip]

    # ---- bans ----

    def is_ip_banned(self, ip):
        return self.get_ban_info(ip) is not None

    def get_ban_info(self, ip):
        with self.lock:
            self._purge_expired()
            info = self.banned_ips.get(ip)
            return dict(info) if info else None

    def ban_ip(self, ip, until, by, reason):
        with self.lock:
            self.banned_ips[ip] = {"until": until, "banned_by": by, "reason": reason}

    def unban_ip(self, ip):
        with self.lock:
            return self.banned_ips.pop(ip, None) is not None

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
        with self.lock: targets = [s for s in self.clients if s is not exclude_sock]
        for s in targets:
            self.send_private(s, text)

    def send_private(self, sock, text):
        try: send_encrypted(sock, self.fernet, text)
        except OSError: pass

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
        self.disconnect(sock)


def _clip(text: str, limit: int = 200) -> str:
    return text if len(text) <= limit else text[:limit - 1] + "…"


# ---- Files ----

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")
THUMB_SIZE = (260, 260)

def encode_file_message(sender: str, filename: str, data: bytes) -> str:
    safe_name = filename.replace("|", "_")
    return FILE_PREFIX + sender + "|" + safe_name + "|" + base64.b64encode(data).decode("ascii")

def build_file_message(sender: str, filepath: str) -> str:
    size = os.path.getsize(filepath)
    if size > MAX_FILE_BYTES:
        raise ValueError(f"File is {size / 1024 / 1024:.1f} MB — the limit is {MAX_FILE_BYTES // 1024 // 1024} MB.")
    with open(filepath, "rb") as f:
        data = f.read()
    return encode_file_message(sender, os.path.basename(filepath), data)

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

def handle_incoming_file(text: str, event_queue: queue.Queue):
    try:
        sender, filename, b64data = text[len(FILE_PREFIX):].split("|", 2)
        raw = base64.b64decode(b64data)
    except Exception:
        event_queue.put(("system", "[received a corrupted file, ignored]"))
        return
    safe_name = os.path.basename(filename) or "unnamed_file"
    event_queue.put(("file", {"sender": sender, "filename": safe_name, "data": raw, "thumb": make_thumbnail(safe_name, raw)}))


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

    elif cmd_name == "whisper":
        target_name, _, msg = arg.partition("|")
        if target_name.lower() == host_name.lower():
            event_queue.put(("private", f"[Whisper from {guest_name}]: {msg}"))
            _guest_notice(hub, sock, f"[Whisper to {host_name}]: {msg}")
            return
        target_sock = hub.find_socket_by_name(target_name)
        if target_sock:
            _guest_notice(hub, target_sock, f"[Whisper from {guest_name}]: {msg}")
            _guest_notice(hub, sock, f"[Whisper to {target_name}]: {msg}")
        else:
            _guest_notice(hub, sock, f"No one named '{target_name}' is connected.")

    elif cmd_name == "mod":
        if is_admin:
            run_mod_command(arg, hub, guest_name, lambda t: _guest_notice(hub, sock, t))
        else:
            _guest_notice(hub, sock, "You do not have permission to use moderation commands.")

def _ping_from_guest(hub: Hub, sock, guest_name, host_name, raw_text, event_queue):
    target_name, raw_mention = extract_ping_target(raw_text, hub.names() + [host_name])
    if not target_name:
        if raw_mention:
            _guest_notice(hub, sock, f"No one named '{raw_mention}' is here to ping.")
        return

    if hub.is_dnd(target_name):
        _guest_notice(hub, sock, f"{target_name} is on Do Not Disturb — they won't be notified.")
    elif target_name.lower() == host_name.lower():
        event_queue.put(("ping", guest_name))
    else:
        target_sock = hub.find_socket_by_name(target_name)
        if target_sock:
            hub.send_private(target_sock, PING_PREFIX + guest_name)

def _process_guest_message(text, sock, guest_name, hub: Hub, host_name, event_queue):
    is_admin = guest_name.lower() in hub.admins

    if text.startswith(TYPING_START_PREFIX):
        if not hub.is_muted(sock):
            hub.mark_typing(text[len(TYPING_START_PREFIX):])
            hub.broadcast(text, exclude_sock=sock)
            event_queue.put(("typing", hub.typing_names()))
        return

    if text.startswith(TYPING_STOP_PREFIX):
        hub.mark_stopped_typing(text[len(TYPING_STOP_PREFIX):])
        hub.broadcast(text, exclude_sock=sock)
        event_queue.put(("typing", hub.typing_names()))
        return

    if text.startswith(DND_PREFIX):
        dname, _, state = text[len(DND_PREFIX):].partition("|")
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
        hub.send_private(sock, MUTE_NOTICE_PREFIX + f"You are muted by {info['muted_by']} until {format_time(info['muted_until'])}. Reason: {info['mute_reason']}")
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
        hub.broadcast(text, exclude_sock=sock)
        msg_id, _, rest = text[len(REACT_PREFIX):].partition("|")
        emoji, _, sender = rest.partition("|")
        event_queue.put(("react", {"msg_id": msg_id, "emoji": emoji, "sender": sender or guest_name}))
        return

    is_file = text.startswith(FILE_PREFIX)
    if not (is_file or text.startswith(MSG_PREFIX)):
        return  # e.g. the "[name left the chat]" courtesy line — nothing to relay

    wait = hub.check_slowmode(guest_name, is_admin)
    if wait > 0:
        _guest_notice(hub, sock, f"Slowmode is active! Please wait {wait:.1f} seconds.")
        return

    if is_file:
        handle_incoming_file(text, event_queue)
        hub.broadcast(text, exclude_sock=sock)
        return

    msg_id, _, raw_text = text[len(MSG_PREFIX):].partition("|")
    _, has_name, body = raw_text.partition(": ")
    hub.record_message(msg_id, guest_name, body if has_name else raw_text)
    _ping_from_guest(hub, sock, guest_name, host_name, raw_text, event_queue)
    event_queue.put(("chat", {"raw": raw_text, "colors": hub.colormap_snapshot(), "msg_id": msg_id}))
    hub.broadcast(text, exclude_sock=sock)

def handle_guest_connection(sock, addr, hub: Hub, host_name: str, event_queue: queue.Queue):
    ban_info = hub.get_ban_info(addr[0])
    if ban_info:
        reason = ban_info.get("reason") or "no reason given"
        hub.send_private(sock, BAN_NOTICE_PREFIX + f"{format_time(ban_info['until'])}|{reason}")
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

    if hub.is_name_occupied(guest_name) or hub.is_host(guest_name):
        hub.send_private(sock, NOTICE_PREFIX + "Nickname already in use.")
        sock.close()
        return

    with hub.lock:
        room_full = len(hub.clients) >= MAX_GUESTS
    if room_full:
        hub.send_private(sock, NOTICE_PREFIX + "[room is full — try again later]")
        sock.close()
        return

    hub.add_client(sock, guest_name, addr[0])

    # Everything from here on is inside try/finally so that *any* failure still
    # removes the guest — otherwise a "ghost" would block the name until restart.
    try:
        hub.apply_ghost_ip_mute(sock, addr[0])
        hub.assign_color(guest_name)

        if hub.is_muted(sock):
            info = hub.get_info(sock)
            hub.send_private(sock, MUTE_STATUS_PREFIX + f"1:{info['muted_until']}")

        event_queue.put(("system", f"{guest_name} joined from {addr[0]}"))
        hub.broadcast(f"* {guest_name} joined the chat *", exclude_sock=sock)
        hub.send_private(sock, ROSTER_PREFIX + ",".join([host_name] + hub.names()))
        hub.send_private(sock, SLOWMODE_PREFIX + str(hub.slowmode_delay))
        hub.broadcast_colormap()
        event_queue.put(("colormap", hub.colormap_snapshot()))
        event_queue.put(("roster", hub.names()))

        while True:
            try: text = recv_message(sock, hub.fernet)
            except InvalidToken: continue
            except (OSError, ConnectionError): break

            try:
                _process_guest_message(text, sock, guest_name, hub, host_name, event_queue)
            except Exception:
                traceback.print_exc()  # one bad message must never end the guest's session
    finally:
        info = hub.remove_client(sock)
        hub.free_color(guest_name)
        try: sock.close()
        except OSError: pass
        if not hub.closed:
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
        threading.Thread(target=handle_guest_connection, args=(conn, addr, hub, host_name, event_queue), daemon=True).start()


# ---- Slash commands ----

HELP_TEXT = (
    "Commands: /mute <name> <min> [reason], /unmute <name>, /kick <name> [reason], "
    "/ban <name> [min|perm] [reason], /unban <ip>, /slowmode [sec], /admin <name>, /unadmin <name>, "
    "/color <name>, /colors, /list, /clear [lines], /whisper <name> <msg>, /help — "
    "host only: /ipban <ip> [min|perm] [reason]. "
    "Right-click a message to edit/delete it (admins can delete anyone's)."
)

PERMANENT_WORDS = ("perm", "indefinite", "0", "infinite")

def parse_ban_args(parts: list) -> tuple:
    """`parts` = [target, duration?, reason?] -> (until_timestamp, reason).
    A duration that isn't a number or a 'permanent' word is treated as the
    start of the reason, with the ban permanent."""
    dur = parts[1].lower() if len(parts) > 1 else "perm"
    reason = parts[2] if len(parts) > 2 else ""
    if dur in PERMANENT_WORDS:
        until = float("inf")
    else:
        try:
            until = time.time() + float(dur) * 60
        except ValueError:
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
    target_name, wmsg = parts
    if target_name.lower() == me.lower():
        return reply("You cannot whisper to yourself!")
    target_sock = hub.find_socket_by_name(target_name)
    if not target_sock:
        return reply(f"No one named '{target_name}' is connected.")
    _guest_notice(hub, target_sock, f"[Whisper from {me}]: {wmsg}")
    reply(f"[Whisper to {target_name}]: {wmsg}")

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

def _cmd_ban(arg, hub, me, reply):
    parts = arg.split(maxsplit=2)
    if not parts: return reply("Usage: /ban <name> [minutes|perm] [reason]")
    name = parts[0]
    if hub.is_host(name): return reply("You cannot ban the host.")
    target = hub.find_socket_by_name(name)
    if not target:
        return reply(f"No one named '{name}' is connected.")

    until, reason = parse_ban_args(parts)
    ip = hub.get_info(target).get("ip")
    if ip: hub.ban_ip(ip, until, me, reason)
    until_str = format_time(until)
    hub.eject(target, BAN_NOTICE_PREFIX + f"{until_str}|{reason}", f"* {name} has been IP banned *")
    hub.log_admin_action(me, f"banned {name} ({ip}) until {until_str}. Reason: {reason}")
    reply(f"Banned {name} ({ip}) until {until_str}. Reason: {reason}")

def _cmd_ipban(arg, hub, me, reply):
    if not hub.is_host(me): return reply("Only the host can use /ipban.")
    parts = arg.split(maxsplit=2)
    if not parts: return reply("Usage: /ipban <ip> [minutes|perm] [reason]")
    ip = parts[0].strip()
    until, reason = parse_ban_args(parts)
    hub.ban_ip(ip, until, me, reason)
    until_str = format_time(until)

    # If someone is connected from that IP right now (under any name), kick
    # them too — otherwise the ban only bites on their next connection attempt.
    target = hub.find_socket_by_ip(ip)
    if target:
        target_name = hub.get_info(target).get("name", "someone")
        hub.eject(target, BAN_NOTICE_PREFIX + f"{until_str}|{reason}", f"* {target_name} has been IP banned *")

    hub.log_admin_action(me, f"IP-banned {ip} directly until {until_str}. Reason: {reason}")
    reply(f"IP {ip} banned until {until_str}. Reason: {reason}")

def _cmd_unban(arg, hub, me, reply):
    if not arg: return reply("Usage: /unban <ip>")
    if not hub.unban_ip(arg):
        return reply(f"IP '{arg}' is not currently banned.")
    hub.broadcast(f"* IP {arg} has been unbanned *")
    hub.log_admin_action(me, f"unbanned IP: {arg}")
    reply(f"Unbanned IP: {arg}")

def _cmd_mute(arg, hub, me, reply):
    parts = arg.split(maxsplit=2)
    if len(parts) < 2: return reply("Usage: /mute <name> <minutes> [reason]")
    name = parts[0]
    if hub.is_host(name): return reply("You cannot mute the host.")
    try: minutes = float(parts[1])
    except ValueError:
        return reply("Usage: /mute <name> <minutes> [reason]")
    reason = parts[2] if len(parts) > 2 else "no reason given"
    until = time.time() + minutes * 60
    if not hub.mute(name, until, me, reason):
        return reply(f"No one named '{name}' is connected.")

    hub.broadcast(f"* {name} has been muted *")
    target_sock = hub.find_socket_by_name(name)
    if target_sock:
        hub.send_private(target_sock, MUTE_NOTICE_PREFIX + f"You were muted by {me} for {minutes:g} minute(s). Reason: {reason}")
        hub.send_private(target_sock, MUTE_STATUS_PREFIX + f"1:{until}")
    hub.log_admin_action(me, f"muted {name} for {minutes:g} min. Reason: {reason}")
    reply(f"Muted {name} for {minutes:g} min until {format_time(until)}. Reason: {reason}")

def _cmd_unmute(arg, hub, me, reply):
    if not arg: return reply("Usage: /unmute <name>")
    if hub.is_host(arg): return reply("You cannot unmute the host.")
    target_sock = hub.find_socket_by_name(arg)
    if not hub.unmute(arg):
        return reply(f"No one named '{arg}' is connected or muted.")
    hub.broadcast(f"* {arg} has been unmuted *")
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
    hub.eject(target, KICK_NOTICE_PREFIX + f"{me}|{reason}", f"* {name} has been kicked *")
    hub.log_admin_action(me, f"kicked {name}. Reason: {reason}")
    reply(f"Kicked {name}. Reason: {reason}")

COMMAND_HANDLERS = {
    "/help": _cmd_help, "/list": _cmd_list, "/colors": _cmd_colors, "/color": _cmd_color,
    "/whisper": _cmd_whisper, "/admin": _cmd_admin, "/unadmin": _cmd_unadmin,
    "/slowmode": _cmd_slowmode, "/ban": _cmd_ban, "/ipban": _cmd_ipban, "/unban": _cmd_unban,
    "/mute": _cmd_mute, "/unmute": _cmd_unmute, "/kick": _cmd_kick,
}
# Commands a guest may only send if the host has made them an admin.
MOD_COMMAND_NAMES = frozenset({"/mute", "/unmute", "/kick", "/ban", "/unban", "/ipban", "/slowmode", "/admin", "/unadmin"})

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
    (MUTE_NOTICE_PREFIX, "private"),
    (NOTICE_PREFIX, "private"),
)
LEAVE_PATTERN = re.compile(r"^\* (.+?) (?:left the chat|has been kicked|has been IP banned) \*$")
JOIN_PATTERN = re.compile(r"^\* (.+?) joined the chat \*$")

def guest_recv_loop(sock, fernet, event_queue, local_colors, colors_lock, known_names, host_ip, closing, host_features):
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
            until_str, _, reason = text[len(BAN_NOTICE_PREFIX):].partition("|")
            put(("disconnected", f"You were banned from the chat hosted by {host_ip} until {until_str}. Reason: {reason}"))
            return False
        if text.startswith(KICK_NOTICE_PREFIX):
            by, _, reason = text[len(KICK_NOTICE_PREFIX):].partition("|")
            put(("disconnected", f"You were kicked by {by}. Reason: {reason}"))
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
            handle_incoming_file(text, event_queue)
            return True
        if text.startswith(FEATURES_PREFIX):
            host_features.update(f for f in text[len(FEATURES_PREFIX):].split(",") if f)
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

        try:
            if not handle(text):
                break
        except Exception:
            traceback.print_exc()  # a malformed message must not kill the receive thread


# ---- Connections ----

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
        try:
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_sock.bind(("", DISCOVERY_PORT))
        except OSError as e:
            udp_sock.close()
            self.event_queue.put(("system", f"Room Code lookup is unavailable ({e}) — guests will need to enter your IP:port instead."))
            return
        udp_sock.settimeout(1.0)
        expected = f"DISCOVER:{room_code}"
        offer = f"OFFER:{self.tcp_port}".encode("utf-8")

        while not self.stop_event.is_set():
            try:
                data, addr = udp_sock.recvfrom(1024)
                if data.decode("utf-8", errors="replace") == expected:
                    udp_sock.sendto(offer, addr)
            except (socket.timeout, OSError):
                continue
        udp_sock.close()

    def send_chat(self, text: str):
        if run_mod_command(text, self.hub, self.name, lambda t: self.event_queue.put(("system", t))):
            # Commands like /color change shared state; refresh our own view now.
            self.event_queue.put(("colormap", self.hub.colormap_snapshot()))
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
        self.hub.record_message(msg_id, self.name, text)
        self.event_queue.put(("chat", {"raw": full_msg, "colors": self.hub.colormap_snapshot(), "msg_id": msg_id}))
        self.hub.broadcast(f"{MSG_PREFIX}{msg_id}|{full_msg}")

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

    def _share_file(self, msg: str):
        handle_incoming_file(msg, self.event_queue)
        self.hub.broadcast(msg)

    def send_file(self, filepath: str):
        self._share_file(build_file_message(self.name, filepath))

    def send_file_bytes(self, filename: str, data: bytes):
        self._share_file(encode_file_message(self.name, filename, data))

    def close(self):
        self.hub.closed = True
        self.stop_event.set()
        self.hub.broadcast(HOST_DISCONNECT_PREFIX)
        with self.hub.lock:
            sockets = list(self.hub.clients)
        for s in sockets:
            self.hub.disconnect(s)
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
        self.fernet = fernet
        self.event_queue = event_queue
        self.local_colors = {}
        self.colors_lock = threading.Lock()
        self.closing = threading.Event()
        self.is_admin = False
        self.host_features = set()  # filled in when the host answers our FEATURES announcement

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.settimeout(5)
            self.sock.connect((host, port))
            self.sock.settimeout(None)
            self._handshake()
        except BaseException:
            self.sock.close()
            raise

    def _handshake(self):
        send_encrypted(self.sock, self.fernet, HELLO_PREFIX + self.name)
        try:
            length = int.from_bytes(recv_exact(self.sock, MSG_LEN_BYTES), "big")
            if length == 0xFFFFFFFF: raise PermissionError("Password is incorrect.")
            response = self.fernet.decrypt(recv_exact(self.sock, length)).decode("utf-8", errors="surrogatepass")
        except InvalidToken: raise PermissionError("Password is incorrect.")
        except PermissionError: raise
        except Exception: raise ConnectionError("Host disconnected unexpectedly.")

        if response.startswith(BAN_NOTICE_PREFIX):
            until_str, _, reason = response[len(BAN_NOTICE_PREFIX):].partition("|")
            raise PermissionError(f"You are banned from this room until {until_str}. Reason: {reason}")
        if response.startswith(NOTICE_PREFIX): raise PermissionError(response[len(NOTICE_PREFIX):])
        if not response.startswith(ROSTER_PREFIX): raise ConnectionError("Invalid handshake from host.")

        self.known_names = {n.strip() for n in response[len(ROSTER_PREFIX):].split(",") if n.strip()}
        self.initial_roster = sorted(self.known_names)

    def start(self, unlock_prefix: str = None):
        threading.Thread(
            target=guest_recv_loop,
            args=(self.sock, self.fernet, self.event_queue, self.local_colors, self.colors_lock, self.known_names, self.host, self.closing, self.host_features),
            daemon=True,
        ).start()
        self._send(FINGERPRINT_PREFIX + get_machine_fingerprint(), report=False)
        self._send(FEATURES_PREFIX + ",".join(sorted(HOST_FEATURES)), report=False)
        if unlock_prefix:
            self._send(unlock_prefix + "1", report=False)

    def _send(self, payload: str, report: bool = True) -> bool:
        try:
            send_encrypted(self.sock, self.fernet, payload)
            return True
        except OSError:
            if report and not self.closing.is_set():
                self.event_queue.put(("disconnected", "Connection lost."))
            return False

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

    def send_chat(self, text: str):
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

        if cmd == "/whisper":
            parts = arg.split(maxsplit=1)
            if len(parts) < 2: return put(("system", "Usage: /whisper <name> <message>"))
            if parts[0].lower() == self.name.lower(): return put(("system", "You cannot whisper to yourself!"))
            self._send(CMD_PREFIX + f"whisper|{parts[0]}|{parts[1]}")
            return

        if cmd in MOD_COMMAND_NAMES:
            if self.is_admin: self._send(CMD_PREFIX + f"mod|{stripped}")
            else: put(("system", "Only admins can use moderation commands."))
            return

        msg_id = os.urandom(4).hex()
        full_msg = f"{self.name}: {text}"
        if self._send(f"{MSG_PREFIX}{msg_id}|{full_msg}"):
            put(("chat", {"raw": full_msg, "colors": self._colors_copy(), "msg_id": msg_id}))

    def send_typing(self, started: bool):
        self._send((TYPING_START_PREFIX if started else TYPING_STOP_PREFIX) + self.name, report=False)

    def send_dnd(self, active: bool):
        verb = "turned on" if active else "turned off"
        self.event_queue.put(("system", f"You {verb} Do Not Disturb."))
        self._send(DND_PREFIX + f"{self.name}|{'on' if active else 'off'}", report=False)

    def _share_file(self, msg: str):
        if self._send(msg):
            handle_incoming_file(msg, self.event_queue)

    def send_file(self, filepath: str):
        self._share_file(build_file_message(self.name, filepath))

    def send_file_bytes(self, filename: str, data: bytes):
        self._share_file(encode_file_message(self.name, filename, data))

    def close(self):
        self.closing.set()
        self._send(f"[{self.name} left the chat]", report=False)
        # shutdown() so the receive thread (blocked in recv) wakes up and the host
        # actually sees us leave — a bare close() from another thread doesn't.
        try: self.sock.shutdown(socket.SHUT_RDWR)
        except OSError: pass
        try: self.sock.close()
        except OSError: pass


def make_button(parent, text, command, bg, fg="white", font=BOLD_FONT, padx=14, pady=6, hover_bg=None):
    """A flat, label-based button (native Tk buttons ignore bg colors on macOS).
    The returned frame has: .label, .base_bg, .disabled, .paint(color), .set_enabled(bool)."""
    frame = tk.Frame(parent, bg=bg, cursor="hand2")
    label = tk.Label(frame, text=text, bg=bg, fg=fg, font=font, padx=padx, pady=pady)
    label.pack(fill="both", expand=True)

    frame.label = label
    frame.base_bg = bg
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
        if not frame.disabled: paint(hover_bg)

    def on_leave(event=None):
        if not frame.disabled: paint(frame.base_bg)

    for w in (frame, label):
        w.bind("<Button-1>", on_click)
        if hover_bg:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

    frame.paint, frame.set_enabled = paint, set_enabled
    return frame


def resolve_join_target(room_code: str, manual_target: str = None):
    """Works out where to connect for a Join. Returns
    (host_ip, port, unlock_prefix, error_message) — error_message is None on success."""
    unlock_prefix = None
    if manual_target:
        match = GRADIENT_UNLOCK_CODES.get(manual_target.strip().lower())
        if match:
            # Not a real address — a secret code. Join as if the field were empty.
            unlock_prefix, manual_target = match[1], None

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
            host_ip, port = discover_host(room_code, target_ip=host_ip)
        else:
            # Fast path first: Room Code = last two octets, so try the likely address directly.
            prefix = ".".join(get_local_ip().split(".")[:2])
            if prefix and not prefix.startswith("127."):
                guess = f"{prefix}.{int(room_code[:3])}.{int(room_code[3:])}"
                host_ip, port = discover_host(room_code, target_ip=guess, timeout=1.5)
            if not host_ip:
                host_ip, port = discover_host(room_code)

    if not host_ip:
        return None, None, unlock_prefix, f"Could not find Room {room_code}. Ensure the host is running and you are on the same Wi-Fi/network."
    return host_ip, port, unlock_prefix, None


class ChatApp(tk.Tk):
    BUILTIN_STICKERS = {"GG": "#57F287", "RIP": "#ED4245", "HELLO": "#5B8CFF", "WOW": "#FEE75C", "BRUH": "#FFA347"}
    REACTION_CHOICES = ("😀", "😂", "❤️", "👍", "🔥", "😢", "😡")
    BASE_COMMANDS = ("/color", "/colors", "/list", "/clear", "/whisper", "/help")
    ADMIN_COMMANDS = ("/mute", "/unmute", "/kick", "/ban", "/unban", "/slowmode", "/admin", "/unadmin")
    PLAYER_ARG_COMMANDS = frozenset({"/mute", "/unmute", "/kick", "/ban", "/whisper", "/admin", "/unadmin"})
    ACTIVITY_RANKED_COMMANDS = frozenset({"/mute", "/kick", "/ban"})
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
        self.settings = load_json(SETTINGS_FILE, dict)
        self.geometry("900x600")
        self.minsize(640, 420)
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
        self._picker_closed_at = {}    # key -> when a picker last closed by losing focus
        self.photo_cache = []          # keeps PhotoImages alive — Tk drops them otherwise
        self.suggest_popup = None
        self._snake_win = None
        self._rainbow_instance_seq = 0
        self._jump_visible = False
        self.sent_history, self._history_pos, self._history_draft = [], None, ""
        self._active_dnd_bind = None
        saved_bind = self.settings.get("dnd_keybind")
        self.dnd_keybind = saved_bind if isinstance(saved_bind, str) and saved_bind else self.DEFAULT_DND_KEYBIND
        self._init_session_state()

        self._event_handlers = {
            "connect_success": self._on_connect_success,
            "connect_fail": self._on_connect_fail,
            "chat": self._on_chat_event,
            "react": lambda p: self.add_reaction(p["msg_id"], p["emoji"], p.get("sender", "")),
            "msg_edit": self._on_msg_edit,
            "msg_delete": self._on_msg_delete,
            "system": self.append_system_line,
            "private": self.append_private_line,
            "roster": self.update_roster,
            "colormap": self._on_colormap_event,
            "typing": self.update_typing,
            "ping": lambda p: notify_ping(p, root=self),
            "file": self.render_incoming_file,
            "disconnected": self._handle_disconnected,
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

        self.bind_all(SNAKE_KEYBIND, self.on_open_snake)
        self.bind("<FocusIn>", self._on_focus_in)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
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
        popup = tk.Toplevel(self)
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
        """A borderless picker that opens just above `anchor`, and closes on
        Esc, on losing focus, or when its button is clicked again."""
        if name in self._popups:
            return self._close_popup(name)
        # Clicking the anchor button while the picker is open first makes the
        # picker lose focus (closing it) — don't instantly reopen it.
        if time.time() - self._picker_closed_at.get(name, 0.0) < 0.25:
            return
        popup = tk.Toplevel(self)
        popup.overrideredirect(True)
        popup.configure(bg=BG_PANEL, padx=6, pady=6)
        self._popups[name] = popup
        build(popup)
        popup.update_idletasks()
        x = anchor.winfo_rootx()
        y = max(0, anchor.winfo_rooty() - popup.winfo_reqheight() - 6)
        popup.geometry(f"+{x}+{y}")
        popup.bind("<FocusOut>", lambda e: self._picker_lost_focus(name))
        popup.bind("<Escape>", lambda e: self._close_popup(name))
        popup.focus_set()

    def _picker_lost_focus(self, name):
        self._picker_closed_at[name] = time.time()
        self._close_popup(name)

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
        """Is the reader looking at the end of the log? `precise` first lets Tk finish
        pending layout and also accepts "last line is visible" — slower, so it's used
        only for the delayed re-check, not on every appended line."""
        if not self.log.winfo_ismapped():
            return True  # not on screen yet (e.g. the room is still starting) — nothing to be "behind" on
        if precise:
            self.log.update_idletasks()
            if self.log.dlineinfo("end-1c") is not None:
                return True
        return self.log.yview()[1] >= 0.999

    def _show_jump(self):
        if not self._jump_visible and self.log.winfo_ismapped():
            self.jump_btn.place(relx=1.0, rely=1.0, anchor="se", x=-12, y=-8)
            self._jump_visible = True

    def _hide_jump(self):
        if self._jump_visible:
            self.jump_btn.place_forget()
            self._jump_visible = False

    def _scroll_to_bottom(self):
        self.log.see("end")
        self._hide_jump()

    def _sync_jump_btn(self):
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
    # Connect screen
    # ------------------------------------------------------------------

    def _build_connect_frame(self):
        f = tk.Frame(self, bg=BG_DARK)
        self.connect_frame = f

        card = tk.Frame(f, bg=BG_PANEL, padx=32, pady=28)
        card.place(relx=0.5, rely=0.5, anchor="center")

        corner_frame = tk.Frame(f, bg=BG_DARK)
        corner_frame.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-8)
        link_font = (CHAT_FONT[0], 8, "underline")
        changelog_label = tk.Label(corner_frame, text="View Changelog", bg=BG_DARK, fg=FG_MUTED, font=link_font, cursor="hand2")
        changelog_label.pack(anchor="e", pady=(0, 2))
        changelog_label.bind("<Button-1>", lambda e: self.on_show_changelog())
        version_label = tk.Label(corner_frame, text=f"v{VERSION} — Check for Updates", bg=BG_DARK, fg=FG_MUTED, font=link_font, cursor="hand2")
        version_label.pack(anchor="e")
        version_label.bind("<Button-1>", lambda e: self.on_check_updates())

        tk.Label(card, text="chat_gui", font=(CHAT_FONT[0], 20, "bold"), bg=BG_PANEL, fg=FG_TEXT).grid(row=0, column=0, columnspan=3, pady=(0, 16))

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
            entry.grid(row=row, column=1, sticky="ew", pady=(6, 0), padx=(10, 0))
            entry.bind("<Return>", lambda e: self.on_connect_clicked())
            entry.label = label_widget
            return entry

        card.grid_columnconfigure(1, weight=1)

        self.name_entry = field(2, "Display name", validate_cmd=(self.register(lambda p: " " not in p and len(p) <= 30), "%P"))
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

        digits_only = (self.register(lambda p: p == "" or (p.isdigit() and len(p) <= 6)), "%P")
        self.room_entry = field(4, "Room Code", validate_cmd=digits_only, entry_width=20)
        self.regen_room_btn = make_button(card, "Refresh", self._regenerate_room_code, bg=BTN_NEUTRAL, hover_bg=BTN_NEUTRAL_HOVER, padx=8, pady=4, font=CHAT_FONT)
        self.regen_room_btn.grid(row=4, column=2, sticky="w", padx=(8, 0), pady=(6, 0))

        self.host_ip_entry = field(5, "Host IP (only if Room Code fails)")
        self.key_entry = field(6, "Shared key", show="*")

        self.status_label = tk.Label(card, text="", bg=BG_PANEL, fg=self.STATUS_COLORS["error"], wraplength=300, justify="left", font=CHAT_FONT)
        self.status_label.grid(row=7, column=0, columnspan=3, sticky="w", pady=(10, 0))

        self.connect_btn = make_button(card, "Connect", self.on_connect_clicked, bg=BTN_GREEN, hover_bg=BTN_GREEN_HOVER)
        self.connect_btn.grid(row=8, column=0, columnspan=3, pady=(16, 0), sticky="ew")

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
            self.room_entry.label.configure(text="Room Code (from host)")
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
        # Just prefills the normal fields with what worked last time — the user
        # still enters the shared key and hits Connect as usual.
        self.room_entry.configure(state="normal")
        self.room_entry.delete(0, "end")
        self.room_entry.insert(0, entry["room_code"])
        self.host_ip_entry.delete(0, "end")
        self.host_ip_entry.insert(0, f"{entry['host_ip']}:{entry['port']}")
        self._set_status("Filled in from a recent connection — enter the shared key and press Connect.", "info")
        self.key_entry.focus_set()

    # ---- Connecting ----

    def _set_connecting(self, connecting: bool):
        self._connecting = connecting
        self.connect_btn.set_enabled(not connecting)
        self.connect_btn.label.configure(text="Connecting..." if connecting else "Connect")

    def _validate_connect_inputs(self, name, room_code, key):
        if not name: return "Enter a display name."
        if " " in name: return "Display name cannot contain spaces."
        if not (len(room_code) == 6 and room_code.isdigit() and 0 <= int(room_code[:3]) <= 255 and 0 <= int(room_code[3:]) <= 255):
            return "Room Code must be 6 digits (from the host's screen)."
        if not key: return "Enter the shared key password."
        return None

    def on_connect_clicked(self):
        if self._connecting or self.connection: return
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
        ban = check_global_ban()
        if ban:
            return put(("connect_fail", f"This device isn't able to use chat_gui. ({ban.get('reason', 'no reason given')})"))

        if mode == "host":
            try:
                conn = HostConnection(name, room_code, fernet, self.event_queue)
            except OSError as e:
                return put(("connect_fail", f"Couldn't start: {e}"))
            return put(("connect_success", {"connection": conn, "mode": "host", "name": name, "room_code": room_code}))

        host_ip, port, unlock_prefix, error = resolve_join_target(room_code, manual_target)
        if error:
            return put(("connect_fail", error))
        try:
            conn = GuestConnection(name, host_ip, port, fernet, self.event_queue)
        except PermissionError as e:
            return put(("connect_fail", str(e)))
        except (OSError, ConnectionError) as e:
            return put(("connect_fail", f"Connection failed: {e}"))
        remember_recent_host(room_code, host_ip, port)
        put(("connect_success", {"connection": conn, "mode": "join", "name": name, "room_code": room_code, "unlock_prefix": unlock_prefix}))

    def _on_connect_success(self, payload):
        self._set_connecting(False)
        self.connection = payload["connection"]
        self.my_name = payload["name"]
        self.is_admin = payload["mode"] == "host"
        self._transition_to_chat(payload["mode"], payload["name"], payload["room_code"])
        if payload["mode"] == "join":
            self.update_roster(self.connection.initial_roster)
            self.connection.start(payload.get("unlock_prefix"))
        self._save_settings()

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
        self.dnd_btn.disabled = False
        self._set_dnd_button_style(False)
        self._apply_mute_state(False)
        if self._snake_win is not None:
            try: self._snake_win._on_close()
            except Exception: pass
            self._snake_win = None
        for child in self.member_list_frame.winfo_children(): child.destroy()
        self._update_window_title()

    def _transition_to_chat(self, mode, name, room_code):
        self._reset_session_state()
        self.known_colors = {name.lower(): HOST_COLOR if mode == "host" else FG_TEXT}
        self.update_roster([name])
        self.title_label.configure(text=f"{'Hosting as' if mode == 'host' else 'Connected as'} {name} — Room {room_code}")
        self.connect_frame.pack_forget()
        self.chat_frame.pack(fill="both", expand=True)
        self.msg_entry.focus_set()

        if mode == "host":
            local_ip = self._host_local_ip or get_local_ip()
            self.append_system_line(
                f"Hosting Room {room_code} on {local_ip}. Guests on your same network segment can join with just the Room Code. "
                f"If that doesn't work, have them enter {local_ip}:{self.connection.tcp_port} in the 'Host IP' field. Type /help for commands."
            )
        else:
            self.append_system_line(f"You joined Room {room_code} as {name}. Type /help for commands.")

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
        self._stop_typing_signal()
        if self.connection:
            try: self.connection.close()
            except Exception: pass
            self.connection = None

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

        body = tk.Frame(self.chat_frame, bg=BG_DARK)
        body.pack(fill="both", expand=True)

        self.log = scrolledtext.ScrolledText(body, bg=BG_DARK, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", state="disabled", wrap="word", padx=10, pady=8, font=CHAT_FONT, highlightthickness=0, bd=0)
        self.log.pack(side="left", fill="both", expand=True)
        self.log.tag_configure("system", foreground=FG_MUTED, font=(CHAT_FONT[0], 9, "italic"))
        self.log.tag_configure("private", foreground=COLOR_PALETTE["yellow"])
        self.log.tag_configure("timestamp", foreground=FG_MUTED, font=(CHAT_FONT[0], 8))
        self.log.tag_configure("reaction_style", foreground=COLOR_PALETTE["yellow"], font=(CHAT_FONT[0], 9))
        self.log.tag_configure("edited_mark", foreground=FG_MUTED, font=(CHAT_FONT[0], 8, "italic"))
        self.log.tag_configure("deleted_mark", foreground=FG_MUTED, font=(CHAT_FONT[0], 9, "italic"))
        self.log.tag_configure("align_right", justify="right")
        self.log.tag_configure("align_left", justify="left")

        # One right-click handler for the whole log (finds the message under the
        # cursor) instead of two Tcl bindings per message.
        for bind in ("<Button-2>", "<Button-3>"):
            self.log.bind(bind, self._on_log_right_click)
        # Hide the "new messages" button once the reader scrolls back to the end
        # (also when the window is resized, which can put the end back in view).
        self.log.bind("<Configure>", lambda e: self.after_idle(self._sync_jump_btn), add="+")
        for widget in (self.log, self.log.vbar):
            for bind in ("<MouseWheel>", "<Button-4>", "<Button-5>", "<ButtonRelease-1>", "<KeyRelease>"):
                widget.bind(bind, lambda e: self.after_idle(self._sync_jump_btn), add="+")

        self.jump_btn = tk.Label(self.log, text="↓ New messages", bg=COLOR_PALETTE["blue"], fg="white", font=BOLD_FONT, padx=10, pady=4, cursor="hand2")
        self.jump_btn.bind("<Button-1>", lambda e: self._scroll_to_bottom())

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

        def tool_button(text, command):
            btn = make_button(self.bottom_bar, text, command, bg=BG_INPUT, hover_bg=BTN_NEUTRAL_HOVER, padx=10, pady=6)
            btn.pack(side="left", padx=(0, 6))
            return btn

        self.attach_btn = tool_button("📎", self.on_attach_file)
        self.sticker_btn = tool_button("🌠", self.on_sticker_picker)
        self.emoji_btn = tool_button("😀", self.on_emoji_picker)

        self.msg_entry = tk.Entry(self.bottom_bar, bg=BG_INPUT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat", font=CHAT_FONT)
        self.msg_entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.msg_entry.bind("<Return>", self.on_send)
        self.msg_entry.bind("<KeyRelease>", self.on_entry_key)
        self.msg_entry.bind("<Tab>", self.on_tab_autocomplete)
        self.msg_entry.bind("<Up>", self._on_up_arrow)
        self.msg_entry.bind("<Down>", self._on_down_arrow)
        self.msg_entry.bind("<Escape>", self._on_escape)
        self.msg_entry.bind("<FocusOut>", lambda e: self.after(150, self.destroy_suggestions))

        self.send_btn = make_button(self.bottom_bar, "Send", self.on_send, bg=COLOR_PALETTE["blue"], hover_bg=BTN_BLUE_HOVER, padx=16, pady=6)
        self.send_btn.pack(side="left", padx=(6, 0))

    def _set_input_state(self, enabled: bool):
        self.msg_entry.configure(state="normal" if enabled else "disabled")
        for btn in (self.send_btn, self.attach_btn, self.sticker_btn, self.emoji_btn):
            btn.set_enabled(enabled)

    # ---- mute / slowmode ----

    def _apply_mute_state(self, muted: bool, until: float = 0.0):
        self._cancel_timer("mute")
        self._set_input_state(not muted)
        until_text = f" until {format_time(until)}" if until else ""
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
                if is_host: commands.append("/ipban")
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
            self.suggest_popup = tk.Toplevel(self)
            self.suggest_popup.wm_overrideredirect(True)
            self.suggest_popup.configure(bg=BG_PANEL, bd=1, relief="solid")
            self.suggest_popup.attributes("-topmost", True)
            # Clicking the popup's own padding should dismiss it and hand focus
            # straight back to the entry — otherwise losing focus to a
            # borderless window can leave the entry unresponsive on macOS.
            self.suggest_popup.bind("<Button-1>", self._on_suggestion_popup_clicked)

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

        height = self.suggest_popup.winfo_reqheight()
        x, y = self.msg_entry.winfo_rootx(), self.msg_entry.winfo_rooty() - height - 5
        self.suggest_popup.wm_geometry(f"{max(self.msg_entry.winfo_width() // 2, 220)}x{height}+{x}+{y}")

    def destroy_suggestions(self):
        if self.suggest_popup:
            try: self.suggest_popup.destroy()
            except Exception: pass
            self.suggest_popup = None
        self.current_suggestions = []

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
        self._set_entry_text("")
        self._history_pos = None

        first_word = text.split()[0].lower()
        if first_word == "/clear":
            self._handle_clear_command(text.split())
            return "break"

        if first_word == "/globalban":
            parts = text.split(maxsplit=2)
            fingerprint = parts[1] if len(parts) > 1 else ""
            reason = parts[2] if len(parts) > 2 else "no reason given"
            self.append_system_line(perform_globalban(fingerprint, reason))
            return "break"

        self._remember_sent(text)
        self._stop_typing_signal()
        self.connection.send_chat(text)
        self._maybe_start_slowmode_cooldown()
        return "break"

    def _handle_clear_command(self, parts):
        if len(parts) > 1 and parts[1].isdigit():
            with self._log_edit():
                self.log.delete(self.log.index(f'end-1c - {int(parts[1])} lines'), "end")
        elif messagebox.askyesno("Confirm Clear", "Are you sure you want to completely clear the chat log?"):
            self.photo_cache = []
            with self._log_edit():
                self.log.delete("1.0", "end")
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

    def on_attach_file(self):
        if not self.connection: return
        path = filedialog.askopenfilename(title="Choose a file to send")
        if not path: return
        try:
            self.connection.send_file(path)
            self._maybe_start_slowmode_cooldown()
        except ValueError as e: messagebox.showerror("File too large", str(e))
        except OSError as e: messagebox.showerror("Couldn't read file", str(e))

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

        text = scrolledtext.ScrolledText(popup, width=64, height=20, bg=BG_INPUT, fg=FG_TEXT, font=CHAT_FONT, wrap="word", relief="flat", padx=8, pady=8)
        text.pack(fill="both", expand=True)
        text.tag_configure("ver", font=(CHAT_FONT[0], CHAT_FONT[1], "bold"), foreground=COLOR_PALETTE["blue"])

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
        if not UPDATE_MANIFEST_URL:
            messagebox.showinfo(
                "Check for Updates",
                "No update server is configured yet. Set UPDATE_MANIFEST_URL near the top of chat_gui.py to enable this.",
            )
            return
        popup = self._open_dialog("update", "Check for Updates")
        if popup is None: return
        self._pending_manifest = None
        self._update_status_var = tk.StringVar(value=f"Checking for updates (current: v{VERSION})...")
        tk.Label(popup, textvariable=self._update_status_var, bg=BG_PANEL, fg=FG_TEXT, font=CHAT_FONT, wraplength=320, justify="left").pack(pady=(0, 12))
        self._update_btn_row = tk.Frame(popup, bg=BG_PANEL)
        self._update_btn_row.pack()
        threading.Thread(target=self._async_check_updates, daemon=True).start()

    def _show_update_state(self, text, *buttons) -> bool:
        """Sets the update dialog's message and buttons ((label, command, 'green'|'neutral'), ...).
        Returns False if the dialog was closed in the meantime."""
        if "update" not in self._popups:
            return False
        self._update_status_var.set(text)
        for w in self._update_btn_row.winfo_children(): w.destroy()
        colors = {"green": (BTN_GREEN, BTN_GREEN_HOVER), "neutral": (BTN_NEUTRAL, BTN_NEUTRAL_HOVER)}
        for i, (label, command, kind) in enumerate(buttons):
            bg, hover = colors[kind]
            make_button(self._update_btn_row, label, command, bg=bg, hover_bg=hover, padx=12, pady=5).pack(side="left", padx=(0, 8) if i < len(buttons) - 1 else 0)
        return True

    def _close_update_dialog(self):
        self._close_popup("update")

    def _async_check_updates(self):
        try:
            manifest = fetch_update_manifest(UPDATE_MANIFEST_URL)
        except Exception as e:
            self.event_queue.put(("update_check_result", {"ok": False, "error": str(e)}))
            return
        self.event_queue.put(("update_check_result", {"ok": True, "manifest": manifest}))

    def _handle_update_check_result(self, result):
        close = ("Close", self._close_update_dialog, "neutral")
        if not result["ok"]:
            self._show_update_state(f"Couldn't check for updates:\n{result['error']}", close)
            return

        manifest = result["manifest"]
        remote_version = manifest.get("version", "?")
        if not is_newer_version(remote_version, VERSION):
            self._show_update_state(f"You're up to date (v{VERSION}).", close)
            return

        notes = manifest.get("notes", "")
        notes_line = f"\n\n{notes}" if notes else ""
        self._pending_manifest = manifest
        self._show_update_state(
            f"Update available: v{remote_version} (you have v{VERSION}).{notes_line}\n\n"
            "This will be signature-verified before anything is installed.",
            ("Install & Restart", self._start_update_install, "green"),
            ("Not now", self._close_update_dialog, "neutral"),
        )

    def _start_update_install(self):
        if not self._pending_manifest: return
        if self._show_update_state("Downloading and verifying update..."):
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
            self._show_update_state(f"Update failed and was NOT installed:\n{result['error']}", ("Close", self._close_update_dialog, "neutral"))
            return
        self._show_update_state(
            f"Update installed and verified. Your previous version was backed up as:\n"
            f"{os.path.basename(result['backup'])}\n\nRestart to apply it.",
            ("Restart Now", self._restart_app, "green"),
            ("Later", self._close_update_dialog, "neutral"),
        )

    def _restart_app(self):
        self._save_settings()
        self._teardown_connection()
        os.execv(sys.executable, [sys.executable] + sys.argv)

    def on_close(self):
        self._save_settings()
        self._teardown_connection()
        self.destroy()

    # ---- snake ----

    def on_open_snake(self, event=None):
        if not self.connection:
            return  # only makes sense once you're actually in a chat session
        if self._snake_win is not None:
            try:
                self._snake_win.lift()
                self._snake_win.focus_force()
            except Exception:
                pass
            return "break"
        self._snake_win = SnakeWindow(self, self.my_name, self._snake_color())
        return "break"

    def _snake_color(self) -> str:
        if isinstance(self.connection, HostConnection):
            return HOST_COLOR
        my_color = self.known_colors.get(self.my_name.lower())
        if my_color in GRADIENT_PALETTES:
            return my_color
        return random.choice(list(COLOR_PALETTE.values()))

    # ------------------------------------------------------------------
    # Stickers + emoji
    # ------------------------------------------------------------------

    def on_sticker_picker(self):
        if Image is None or ImageDraw is None:
            return messagebox.showerror("Error", "Pillow (PIL) is required to use stickers.")
        self._toggle_picker("stickers", self.sticker_btn, self._build_sticker_picker)

    def _picker_cell(self, parent, row, col, command, text=None, image=None, on_right=None, muted=False):
        cell = tk.Label(
            parent, text=text, image=image, font=(CHAT_FONT[0], 9) if muted else BOLD_FONT, bg=BG_INPUT,
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
            tk.Label(popup, text="Right-click a custom sticker to delete it", bg=BG_PANEL, fg=FG_MUTED, font=(CHAT_FONT[0], 8)).pack(pady=(4, 0))

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

        if name in self.BUILTIN_STICKERS:
            img_bytes = self._render_builtin_sticker(name)
        else:
            b64data = _load_custom_stickers().get(name)
            if not b64data: return
            img_bytes = base64.b64decode(b64data)

        self.connection.send_file_bytes(f"Sticker_{name}.jpg", img_bytes)
        self._maybe_start_slowmode_cooldown()

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
        self.msg_entry.focus_set()
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

    def _on_chat_event(self, payload):
        self.known_colors.update(payload.get("colors") or {})
        self.append_chat_line(payload["raw"], payload.get("msg_id"))

    def _on_colormap_event(self, colors):
        self.known_colors.update(colors)
        self.update_roster(self.current_roster)

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
                    self._msg_authors[msg_id] = prefix
                    if len(self._msg_authors) > 3000:
                        self._msg_authors.pop(next(iter(self._msg_authors)))
                    if mine:
                        self._my_messages[msg_id] = rest
                    self.log.mark_set(f"react_mark_{msg_id}", end_index)
                    self.log.mark_gravity(f"react_mark_{msg_id}", "left")
            else:
                self.log.insert("end", raw)

            self.log.insert("end", "\n")

        if not mine:
            self._note_unread()

    def append_system_line(self, text: str):
        with self._log_append():
            self.log.insert("end", f"* {text}\n", ("system",))

    def append_private_line(self, text: str):
        with self._log_append():
            self.log.insert("end", f"[private] {text}\n", ("private",))

    # ---- reactions ----

    def _on_log_right_click(self, event):
        index = self.log.index(f"@{event.x},{event.y}")
        for tag in self.log.tag_names(index):
            if tag.startswith("msg_"):
                self.show_reaction_menu(event, tag[len("msg_"):])
                return "break"

    def _build_message_menu(self, msg_id):
        menu = tk.Menu(self, tearoff=0, bg=BG_PANEL, fg=FG_TEXT)
        for emoji in self.REACTION_CHOICES:
            menu.add_command(label=emoji, command=lambda e=emoji: self.send_reaction(msg_id, e))
        mine = msg_id in self._my_messages
        if mine or self.is_admin:  # is_admin is also True for the host
            menu.add_separator()
            if mine:
                menu.add_command(label="Edit message", command=lambda: self.start_edit(msg_id))
                menu.add_command(label="Delete message", command=lambda: self.start_delete(msg_id))
            else:
                menu.add_command(label="Delete message (admin)", command=lambda: self.start_delete(msg_id))
        return menu

    def show_reaction_menu(self, event, msg_id):
        menu = self._build_message_menu(msg_id)
        try: menu.tk_popup(event.x_root, event.y_root)
        finally: menu.grab_release()

    # ---- editing / deleting messages ----

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
        mine = msg_id in self._my_messages
        prompt = "Delete your message for everyone?" if mine else "Delete this message for everyone?"
        if messagebox.askyesno("Delete message", prompt, parent=self):
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
            self.log.insert(start, new_text, (f"body_{msg_id}", msg_tag, align))
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

    def _on_msg_delete(self, payload):
        msg_id, deleter = payload["msg_id"], payload["deleter"]
        author = self._msg_authors.get(msg_id)
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
        sender, filename, data, thumb = payload["sender"], payload["filename"], payload["data"], payload.get("thumb")
        mine = sender.lower() == self.my_name.lower()

        with self._log_append(force_scroll=mine):
            start_index = self.log.index("end-1c")
            self.log.insert("end", f"[{time.strftime('%H:%M')}] ", ("timestamp",))
            self._insert_name(sender, self.known_colors.get(sender.lower(), FG_TEXT))
            self.log.insert("end", f" sent an attachment ({filename}):\n")

            photo = None
            if thumb is not None and ImageTk is not None:
                try: photo = ImageTk.PhotoImage(thumb)
                except Exception: photo = None

            if photo is not None:
                self.photo_cache.append(photo)
                self.log.image_create("end", image=photo)
                img_tag = f"img_{len(self.photo_cache)}"
                self.log.tag_add(img_tag, self.log.index("end-2c"), self.log.index("end-1c"))
                for bind in ("<Button-2>", "<Button-3>"):
                    self.log.tag_bind(img_tag, bind, lambda e, d=data, fn=filename: self._show_image_context_menu(e, d, fn))
            else:
                embed = tk.Frame(self.log, bg=BG_PANEL, bd=1, relief="solid", padx=12, pady=8)
                tk.Label(embed, text=f"📁  {filename}", bg=BG_PANEL, fg=FG_TEXT, font=BOLD_FONT).pack(side="left", padx=(0, 14))
                tk.Label(embed, text=f"({len(data) / 1024:.1f} KB)", bg=BG_PANEL, fg=FG_MUTED, font=CHAT_FONT).pack(side="left", padx=(0, 14))
                make_button(embed, "Download", lambda d=data, fn=filename: self._save_file_to_disk(d, fn), bg=BTN_GREEN, hover_bg=BTN_GREEN_HOVER, padx=10, pady=4).pack(side="right")
                self.log.window_create("end", window=embed)

            self.log.insert("end", "\n\n")
            self.log.tag_add("align_right" if mine else "align_left", start_index, self.log.index("end-1c"))

        if not mine:
            self._note_unread()

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
