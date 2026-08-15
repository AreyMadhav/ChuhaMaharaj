import ctypes
import os
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

import keyboard
import pyautogui

# ============================================================
# Chuha Maharaj
# Windows
#
# Controls:
#   Arrow keys / WASD     Move cursor
#   Enter                 Left click
#   Right Shift           Right click
#   Space                 Double click
#   Numpad 5              Left click
#   Numpad 0              Right click
#   + / -                 Increase/decrease speed
#   Ctrl+Alt+M            Toggle keyboard-mouse mode
#   Ctrl+Alt+Q            Quit
#
# The program uses global keyboard hooks, so it works even when
# another application has focus.
# ============================================================

APP_NAME = "Chuha Maharaj"
CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "ChuhaMaharaj")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.txt")

DEFAULT_SPEED = 18
MIN_SPEED = 2
MAX_SPEED = 100

speed = DEFAULT_SPEED
enabled = True
running = True

# Prevent repeated click actions while a key is held.
click_lock = threading.Lock()
last_click_time = 0.0


def load_speed():
    global speed
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            value = int(f.read().strip())
            speed = max(MIN_SPEED, min(MAX_SPEED, value))
    except Exception:
        speed = DEFAULT_SPEED


def save_speed():
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(str(speed))
    except Exception:
        pass


def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def request_admin():
    """Restart this program elevated. Some Windows apps require elevation
    before global keyboard hooks/cursor control work reliably."""
    if is_admin():
        return

    params = " ".join(f'"{arg}"' for arg in sys.argv)
    ctypes.windll.shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        params,
        None,
        1
    )
    sys.exit(0)


def move(dx, dy):
    if not enabled:
        return
    pyautogui.moveRel(dx, dy, duration=0)


def safe_click(button="left", clicks=1):
    global last_click_time

    # Avoid accidental click storms from a held key.
    with click_lock:
        now = time.monotonic()
        if now - last_click_time < 0.12:
            return
        last_click_time = now
        pyautogui.click(button=button, clicks=clicks, interval=0.05)


def movement_loop():
    """Continuous movement while arrow/WASD keys are held."""
    global running

    tick = 0.008

    while running:
        if enabled:
            dx = 0
            dy = 0

            if keyboard.is_pressed("left") or keyboard.is_pressed("a"):
                dx -= speed

            if keyboard.is_pressed("right") or keyboard.is_pressed("d"):
                dx += speed

            if keyboard.is_pressed("up") or keyboard.is_pressed("w"):
                dy -= speed

            if keyboard.is_pressed("down") or keyboard.is_pressed("s"):
                dy += speed

            if dx or dy:
                # Normalize diagonal movement so it isn't faster.
                if dx and dy:
                    dx = int(dx * 0.7071)
                    dy = int(dy * 0.7071)

                move(dx, dy)

        time.sleep(tick)


def toggle_enabled():
    global enabled
    enabled = not enabled
    update_status()


def increase_speed():
    global speed
    speed = min(MAX_SPEED, speed + 2)
    save_speed()
    update_status()


def decrease_speed():
    global speed
    speed = max(MIN_SPEED, speed - 2)
    save_speed()
    update_status()


def quit_program():
    global running
    running = False

    try:
        keyboard.unhook_all()
    except Exception:
        pass

    try:
        root.after(0, root.destroy)
    except Exception:
        pass


def update_status():
    try:
        status_var.set(
            f"Mode: {'ON' if enabled else 'PAUSED'}    |    Speed: {speed}"
        )
        toggle_btn.config(
            text="Pause Keyboard Mouse" if enabled else "Resume Keyboard Mouse"
        )
    except Exception:
        pass


def register_hotkeys():
    # Toggle mode.
    keyboard.add_hotkey("ctrl+alt+m", toggle_enabled, suppress=False)

    # Quit.
    keyboard.add_hotkey("ctrl+alt+q", quit_program, suppress=False)

    # Speed controls.
    keyboard.add_hotkey("=", increase_speed, suppress=False)
    keyboard.add_hotkey("+", increase_speed, suppress=False)
    keyboard.add_hotkey("-", decrease_speed, suppress=False)

    # Click controls.
    #
    # on_release is used so a held key does not generate hundreds
    # of clicks.
    keyboard.on_release_key("enter", lambda _: safe_click("left"))
    keyboard.on_release_key("right shift", lambda _: safe_click("right"))
    keyboard.on_release_key("space", lambda _: safe_click("left", clicks=2))

    # Numpad alternatives.
    keyboard.on_release_key("num 5", lambda _: safe_click("left"))
    keyboard.on_release_key("num 0", lambda _: safe_click("right"))


def enable_startup():
    """Create a Windows Startup shortcut using PowerShell."""
    startup = os.path.join(
        os.environ["APPDATA"],
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )
    shortcut = os.path.join(startup, "Chuha Maharaj.lnk")

    target = os.path.abspath(sys.argv[0])

    # If running from a .py file, use the current Python executable.
    # If packaged as .exe, use the executable itself.
    if target.lower().endswith(".py"):
        target_path = sys.executable
        arguments = f'"{target}"'
    else:
        target_path = target
        arguments = ""

    ps = f"""
$ws = New-Object -ComObject WScript.Shell
$s = $ws.CreateShortcut('{shortcut}')
$s.TargetPath = '{target_path}'
$s.Arguments = '{arguments}'
$s.WorkingDirectory = '{os.path.dirname(target)}'
$s.Save()
"""
    try:
        import subprocess
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
            creationflags=subprocess.CREATE_NO_WINDOW,
            check=False
        )
        messagebox.showinfo(APP_NAME, "Chuha Maharaj will start with Windows.")
    except Exception as e:
        messagebox.showerror(APP_NAME, f"Could not enable startup:\n{e}")


def disable_startup():
    startup = os.path.join(
        os.environ["APPDATA"],
        r"Microsoft\Windows\Start Menu\Programs\Startup"
    )
    shortcut = os.path.join(startup, "Chuha Maharaj.lnk")

    try:
        if os.path.exists(shortcut):
            os.remove(shortcut)
        messagebox.showinfo(APP_NAME, "Windows startup has been disabled.")
    except Exception as e:
        messagebox.showerror(APP_NAME, f"Could not disable startup:\n{e}")


def show_help():
    messagebox.showinfo(
        APP_NAME,
        """KEYBOARD MOUSE CONTROLS

Movement
  Arrow keys / W A S D  = move mouse

Clicks
  Enter                = left click
  Right Shift          = right click
  Space                = double left click
  Numpad 5             = left click
  Numpad 0             = right click

Utility
  + / =                = increase speed
  -                    = decrease speed
  Ctrl + Alt + M       = pause/resume
  Ctrl + Alt + Q       = quit

Speed is saved automatically.

Tip:
If you need to type normally, pause the utility with
Ctrl+Alt+M first."""
    )


# ------------------------- UI -------------------------

load_speed()

root = tk.Tk()
root.title(APP_NAME)
root.geometry("560x520")
root.resizable(False, False)

try:
    root.iconname(APP_NAME)
except Exception:
    pass

style = ttk.Style()
try:
    style.theme_use("vista")
except Exception:
    pass

main = ttk.Frame(root, padding=20)
main.pack(fill="both", expand=True)

title = ttk.Label(
    main,
    text="Chuha Maharaj",
    font=("Segoe UI", 20, "bold")
)
title.pack(pady=(0, 6))

subtitle = ttk.Label(
    main,
    text="Use your keyboard as a full mouse replacement.",
    font=("Segoe UI", 10)
)
subtitle.pack(pady=(0, 18))

status_var = tk.StringVar()
status = ttk.Label(
    main,
    textvariable=status_var,
    font=("Segoe UI", 11, "bold")
)
status.pack(pady=(0, 15))

controls = ttk.LabelFrame(main, text="Controls", padding=15)
controls.pack(fill="x", pady=5)

rows = [
    ("Move", "Arrow keys / W A S D"),
    ("Left click", "Enter / Numpad 5"),
    ("Right click", "Right Shift / Numpad 0"),
    ("Double click", "Space"),
    ("Speed up", "+ / ="),
    ("Speed down", "-"),
    ("Pause / Resume", "Ctrl + Alt + M"),
    ("Quit", "Ctrl + Alt + Q"),
]

for action, keys in rows:
    row = ttk.Frame(controls)
    row.pack(fill="x", pady=3)

    ttk.Label(
        row,
        text=action,
        width=20,
        font=("Segoe UI", 10, "bold")
    ).pack(side="left")

    ttk.Label(
        row,
        text=keys
    ).pack(side="left")

button_frame = ttk.Frame(main)
button_frame.pack(fill="x", pady=18)

toggle_btn = ttk.Button(
    button_frame,
    text="Pause Keyboard Mouse",
    command=toggle_enabled
)
toggle_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))

help_btn = ttk.Button(
    button_frame,
    text="Help",
    command=show_help
)
help_btn.pack(side="left", expand=True, fill="x", padx=5)

quit_btn = ttk.Button(
    button_frame,
    text="Quit",
    command=quit_program
)
quit_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))

startup_frame = ttk.LabelFrame(main, text="Windows Startup", padding=12)
startup_frame.pack(fill="x", pady=5)

startup_buttons = ttk.Frame(startup_frame)
startup_buttons.pack(fill="x")

ttk.Button(
    startup_buttons,
    text="Start with Windows",
    command=enable_startup
).pack(side="left", expand=True, fill="x", padx=(0, 5))

ttk.Button(
    startup_buttons,
    text="Disable Startup",
    command=disable_startup
).pack(side="left", expand=True, fill="x", padx=(5, 0))

footer = ttk.Label(
    main,
    text="Tip: Ctrl+Alt+M pauses the utility when you need normal keyboard input.",
    font=("Segoe UI", 9)
)
footer.pack(pady=(15, 0))

update_status()

# Register global keyboard hooks.
try:
    register_hotkeys()
except Exception as e:
    messagebox.showerror(
        APP_NAME,
        "Could not register keyboard controls.\n\n"
        f"{e}\n\n"
        "Try running the program as Administrator."
    )

# Movement runs separately so holding a key gives smooth movement.
threading.Thread(target=movement_loop, daemon=True).start()

root.protocol("WM_DELETE_WINDOW", quit_program)

try:
    root.mainloop()
finally:
    running = False
    try:
        keyboard.unhook_all()
    except Exception:
        pass
