#!/usr/bin/env python3
import random
import threading
import time
from pynput.keyboard import Controller, KeyCode, Listener

# Tune these for how "super quick" you want it.
# Hold each key for 14-42 ms, then wait between presses.
BASE_TAP_MIN_DOWN = 0.014
BASE_TAP_MAX_DOWN = 0.042
# Slow key frequency by ~50% (double the gap range).
BASE_TAP_MIN_GAP = 0.0042 * 1.587
BASE_TAP_MAX_GAP = 0.021 * 1.587

# Increase speed by an additional 30% by shortening all delays.
SPEED_MULTIPLIER = 1.3 * 1.3
TAP_MIN_DOWN = BASE_TAP_MIN_DOWN / SPEED_MULTIPLIER
TAP_MAX_DOWN = BASE_TAP_MAX_DOWN / SPEED_MULTIPLIER
TAP_MIN_GAP = BASE_TAP_MIN_GAP / SPEED_MULTIPLIER
TAP_MAX_GAP = BASE_TAP_MAX_GAP / SPEED_MULTIPLIER

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
    time.sleep(random.uniform(TAP_MIN_DOWN, TAP_MAX_DOWN))
    keyboard.release(key)


def rapid_random_taps(duration_seconds: float) -> None:
    end_time = time.perf_counter() + duration_seconds
    while time.perf_counter() < end_time and not stop_event.is_set():
        tap_key(random.choice((F_KEY, J_KEY)))
        time.sleep(random.uniform(TAP_MIN_GAP, TAP_MAX_GAP))


def hold_tilde(seconds: float) -> None:
    if stop_event.is_set():
        return
    keyboard.press(TILDE_KEY)
    try:
        end_time = time.perf_counter() + seconds
        while time.perf_counter() < end_time and not stop_event.is_set():
            time.sleep(0.01)
    finally:
        keyboard.release(TILDE_KEY)


def on_press(key: KeyCode) -> None:
    if key == Q_KEY:
        pause_event.set()
    elif key == E_KEY:
        pause_event.clear()


def main() -> None:
    print('Starting in 5 seconds. Focus the target window now...')
    time.sleep(5)
    print('Running. Press q to pause, e to resume.')

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
