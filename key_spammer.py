#!/usr/bin/env python3
import json
import random
import threading
import time
from pathlib import Path
from pynput.keyboard import Controller, KeyCode, Listener

# Tune these for how "super quick" you want it.
# Hold each key for 14-42 ms, then wait between presses.
BASE_TAP_MIN_DOWN = 0.014
BASE_TAP_MAX_DOWN = 0.042
# Slow key frequency by ~50% (double the gap range).
BASE_TAP_MIN_GAP = 0.0042 * 1.587
BASE_TAP_MAX_GAP = 0.021 * 1.587

SPEED_FACTOR_MIN = 0.2
SPEED_FACTOR_MAX = 5.0
SPEED_FACTOR_STEP = 1.01
CONFIG_PATH = Path(__file__).with_name("key_spammer_config.json")

speed_factor = 1.0
speed_lock = threading.Lock()
TAP_MIN_DOWN = BASE_TAP_MIN_DOWN
TAP_MAX_DOWN = BASE_TAP_MAX_DOWN
TAP_MIN_GAP = BASE_TAP_MIN_GAP
TAP_MAX_GAP = BASE_TAP_MAX_GAP

BURST_SECONDS = 35
TILDE_HOLD_SECONDS = 1
TILDE_AFTER_SECONDS = 10 * 60

keyboard = Controller()
F_KEY = KeyCode.from_char('f')
J_KEY = KeyCode.from_char('j')
Q_KEY = KeyCode.from_char('q')
E_KEY = KeyCode.from_char('e')
# This is the grave/tilde key. Holding this key physically is usually equivalent.
TILDE_KEY = KeyCode.from_char('`')
stop_event = threading.Event()
pause_event = threading.Event()


def tap_key(key: KeyCode) -> None:
    keyboard.press(key)
    with speed_lock:
        min_down = TAP_MIN_DOWN
        max_down = TAP_MAX_DOWN
    time.sleep(random.uniform(min_down, max_down))
    keyboard.release(key)


def wait_while_paused() -> None:
    while pause_event.is_set() and not stop_event.is_set():
        time.sleep(0.05)


def rapid_random_taps(duration_seconds: float) -> None:
    end_time = time.perf_counter() + duration_seconds
    while time.perf_counter() < end_time and not stop_event.is_set():
        if pause_event.is_set():
            wait_while_paused()
            continue
        tap_key(random.choice((F_KEY, J_KEY)))
        with speed_lock:
            min_gap = TAP_MIN_GAP
            max_gap = TAP_MAX_GAP
        time.sleep(random.uniform(min_gap, max_gap))


def hold_tilde(seconds: float) -> None:
    if stop_event.is_set():
        return
    if pause_event.is_set():
        wait_while_paused()
        if stop_event.is_set():
            return
    keyboard.press(TILDE_KEY)
    try:
        end_time = time.perf_counter() + seconds
        while time.perf_counter() < end_time and not stop_event.is_set():
            time.sleep(0.01)
    finally:
        keyboard.release(TILDE_KEY)


def recompute_timing() -> None:
    global TAP_MIN_DOWN, TAP_MAX_DOWN, TAP_MIN_GAP, TAP_MAX_GAP
    with speed_lock:
        factor = speed_factor
    TAP_MIN_DOWN = BASE_TAP_MIN_DOWN / factor
    TAP_MAX_DOWN = BASE_TAP_MAX_DOWN / factor
    TAP_MIN_GAP = BASE_TAP_MIN_GAP / factor
    TAP_MAX_GAP = BASE_TAP_MAX_GAP / factor


def load_speed_factor() -> None:
    global speed_factor
    if not CONFIG_PATH.exists():
        recompute_timing()
        return
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        value = float(data.get("speed_factor", 1.0))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        recompute_timing()
        return
    with speed_lock:
        speed_factor = max(SPEED_FACTOR_MIN, min(SPEED_FACTOR_MAX, value))
    recompute_timing()


def save_speed_factor() -> None:
    with speed_lock:
        value = speed_factor
    try:
        CONFIG_PATH.write_text(
            json.dumps({"speed_factor": value}, indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass


def adjust_speed(factor: float) -> None:
    global speed_factor
    with speed_lock:
        speed_factor = max(
            SPEED_FACTOR_MIN,
            min(SPEED_FACTOR_MAX, speed_factor * factor),
        )
    recompute_timing()
    save_speed_factor()


def on_press(key) -> None:
    if isinstance(key, KeyCode) and key.char:
        ch = key.char.lower()
        if ch == 'q':
            pause_event.set()
        elif ch == 'e':
            pause_event.clear()
        elif ch == ']':
            adjust_speed(SPEED_FACTOR_STEP)
        elif ch == '[':
            adjust_speed(1.0 / SPEED_FACTOR_STEP)


def main() -> None:
    print('Starting in 5 seconds. Focus the target window now...')
    time.sleep(5)
    load_speed_factor()
    print('Running. Press q to pause, e to resume, ] to speed up, [ to slow down.')

    with Listener(on_press=on_press):
        try:
            last_tilde_time = time.perf_counter()
            while not stop_event.is_set():
                if pause_event.is_set():
                    time.sleep(0.1)
                    continue
                rapid_random_taps(BURST_SECONDS)
                if (time.perf_counter() - last_tilde_time) >= TILDE_AFTER_SECONDS:
                    hold_tilde(TILDE_HOLD_SECONDS)
                    last_tilde_time = time.perf_counter()
        except KeyboardInterrupt:
            stop_event.set()

    print('\nStopped.')


if __name__ == '__main__':
    main()
