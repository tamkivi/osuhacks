# osuhacks

Small Python scripts that send rapid keyboard input to the currently focused application window using `pynput`.

This repository is provided for learning, automation testing, and accessibility experiments. Do not use it to violate a game's terms of service or any platform rules.

## Programs

### `key_spammer.py`

Randomly taps `f` and `j` at a high rate.

Controls while running:

- `q`: pause
- `e`: resume
- `]`: speed up
- `[`: slow down

Persists speed in `key_spammer_config.json` (created next to the script).

### `mania_spammer.py`

Repeatedly presses a 5-key chord simultaneously: `d`, `f`, `g`, `h`, `j` (press all down, hold briefly, release all, repeat).

Controls while running:

- `q`: pause
- `e`: resume
- `]`: speed up
- `[`: slow down

Persists speed in `mania_spammer_config.json` (created next to the script).

## Setup

Python: 3.10+

Install dependency:

```sh
python3 -m pip install -r requirements.txt
```

macOS note: if keystrokes are not being sent, you likely need to grant Accessibility permissions to your terminal app (System Settings -> Privacy & Security -> Accessibility).

## Run

Focus the target window, then run one of:

```sh
python3 key_spammer.py
python3 mania_spammer.py
```

Stop with `Ctrl+C`.

