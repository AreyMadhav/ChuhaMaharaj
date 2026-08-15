# Chuha Maharaj

Chuha Maharaj is a Windows utility that lets you control the mouse pointer using the keyboard. It is useful for accessibility, remote desktop situations, or any workflow where keyboard-only mouse control is helpful.

## Features

- Move the mouse with the arrow keys or WASD
- Left click, right click, and double click using keyboard keys
- Smooth continuous movement while keys are held down
- Adjustable cursor speed
- Pause/resume mode without closing the app
- Optional startup with Windows
- Saves the speed setting automatically

## Supported Controls

| Action | Keys |
| --- | --- |
| Move mouse | Arrow keys / W A S D |
| Left click | Enter / Numpad 5 |
| Right click | Right Shift / Numpad 0 |
| Double click | Space |
| Increase speed | + / = |
| Decrease speed | - |
| Pause / Resume | Ctrl + Alt + M |
| Quit | Ctrl + Alt + Q |

## Requirements

- Windows
- Python 3.9+
- Administrative privileges are recommended because this tool uses global keyboard hooks

## Installation

1. Open a terminal in the project folder.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the program:

```bash
python keyboard_mouse_utility.py
```

## Usage

- Launch the app and keep it running in the background.
- Use the keyboard controls listed above to move and click the mouse.
- If you need to type normally, pause the utility with `Ctrl + Alt + M`.
- You can also increase or decrease movement speed with `+` and `-`.

## Windows Startup

The app includes buttons in the UI to:

- Start with Windows
- Disable Startup

This creates a shortcut in the Windows Startup folder.

## Notes

- Speed is stored automatically in `%APPDATA%\ChuhaMaharaj\config.txt`
- Because the program listens globally for keyboard input, it may work best when run as Administrator
- The app is designed for personal desktop use and not as a general-purpose automation framework

## Building an EXE

A PyInstaller spec file is included: `Chuha Maharaj.spec`.

You can build the executable with:

```bash
pyinstaller Chuha Maharaj.spec
```

If `pyinstaller` is not installed, install it first:

```bash
pip install pyinstaller
```

## Project Files

- `keyboard_mouse_utility.py` — main application
- `Chuha Maharaj.spec` — PyInstaller build spec
- `requirements.txt` — Python dependencies

## Disclaimer

This project is intended for keyboard accessibility and personal productivity use. Ensure you are using it in a way that complies with your system and security requirements.
