from pynput import keyboard, mouse
import time
import threading
import json
from datetime import datetime
import sys

import os

recording = False
playing = False
paused = False
events = []
start_time = None

RECORDING_FILE = 'recording.json'
LOG_FILE = 'replay_log.txt'

keyboard_listener = None
mouse_listener = None

def log_to_file(text):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {text}\n")

def save_recording():
    with open(RECORDING_FILE, 'w') as f:
        json.dump(events, f)
    print(f"💾 Înregistrare salvată în {RECORDING_FILE}")
 

def load_recording():
    global events
    with open(RECORDING_FILE, 'r') as f:
        events.clear()
        events.extend(json.load(f))
    print(f"📂 Înregistrare încărcată din {RECORDING_FILE}")

def log_event(event_type, event_data):
    if paused:
        return
    global start_time
    if start_time is None:
        start_time = time.time()
    timestamp = time.time() - start_time

    if event_type in ['key_press', 'key_release']:
        key = event_data
        if hasattr(key, 'char') and key.char is not None:
            event_data = repr(key.char)
        else:
            event_data = f'keyboard.{key}'
    elif event_type == 'mouse_click':
        x, y, button, pressed = event_data
        event_data = (x, y, str(button), pressed)
    elif event_type == 'mouse_scroll':
        x, y, dx, dy = event_data
        event_data = (x, y, dx, dy)
    elif event_type == 'mouse_move':
        x, y = event_data
        event_data = (x, y)

    events.append((event_type, event_data, timestamp))

def on_key_press(key):
    if recording:
        log_event('key_press', key)

def on_key_release(key):
    global recording
    if recording:
        log_event('key_release', key)
    if key == keyboard.Key.f2:
        if not recording:
            start_recording()
        else:
            stop_recording()
    elif key == keyboard.Key.f1:
        toggle_playback()
    elif key == keyboard.Key.f3:
        toggle_pause()
    elif key == keyboard.Key.f12:
        kill_program()

def on_click(x, y, button, pressed):
    if recording:
        log_event('mouse_click', (x, y, button, pressed))

def on_move(x, y):
    if recording:
        log_event('mouse_move', (x, y))

def on_scroll(x, y, dx, dy):
    if recording:
        log_event('mouse_scroll', (x, y, dx, dy))

def start_recording():
    global recording, events, start_time
    if playing:
        print("❌ Opriți redarea (F1) înainte de a porni o nouă înregistrare.")
        return
    print("✅ Înregistrare pornită (F2 pentru a opri)")
    recording = True
    events.clear()
    start_time = time.time()

def stop_recording():
    global recording
    print("🛑 Înregistrare oprită.")
    recording = False
    save_recording()

def toggle_pause():
    global paused
    paused = not paused
    if paused:
        print("⏸️ Înregistrare în pauză.")
    else:
        print("▶️ Înregistrare reluată.")

def toggle_playback():
    global playing
    if not playing:
        if recording:
            print("❌ Opriți înregistrarea (F2) înainte de a porni redarea.")
            return
        try:
            load_recording()
        except FileNotFoundError:
            print("❌ Fișier de înregistrare inexistent.")
            return
        
        if not events:
            print("⚠️ Înregistrarea este goală. Nimic de redat.")
            return

        print("▶️ Redare pornită (F1 pentru a opri)")
        playing = True
        playback_events = list(events)  # Create a copy for the thread
        threading.Thread(target=playback, args=(playback_events,)).start()
    else:
        print("⏹️ Redare oprită.")
        playing = False

def playback(events_to_play):
    global playing
    kb = keyboard.Controller()
    ms = mouse.Controller()

    while playing:
        start = time.time()
        for event_type, event_data, timestamp in events_to_play:
            if not playing:
                break
            time.sleep(max(0, (start + timestamp) - time.time()))
            try:
                if event_type == 'key_press':
                    kb.press(eval(event_data))
                elif event_type == 'key_release':
                    kb.release(eval(event_data))
                elif event_type == 'mouse_click':
                    x, y, button_str, pressed = event_data
                    ms.position = (x, y)
                    button = getattr(mouse.Button, button_str.split('.')[-1])
                    if pressed:
                        ms.press(button)
                    else:
                        ms.release(button)
                elif event_type == 'mouse_move':
                    x, y = event_data
                    ms.position = (x, y)
                elif event_type == 'mouse_scroll':
                    x, y, dx, dy = event_data
                    ms.position = (x, y)
                    ms.scroll(dx, dy)
            except Exception as e:
                print(f"Eroare la redare: {e}")

        if playing:
            delay = 1
            print(f"⏳ Aștept {delay} secunde înainte de redarea următoare...")
            log_to_file(f"Redare completă – pauză {delay} sec")
            time.sleep(delay)

def kill_program():
    global playing, recording, keyboard_listener, mouse_listener
    print("🛑 Program oprit forțat (F12 apăsat)")
    playing = False
    recording = False
    if keyboard_listener:
        keyboard_listener.stop()
    if mouse_listener:
        mouse_listener.stop()
    sys.exit(0)

def main():
    global keyboard_listener, mouse_listener

    if os.path.exists(RECORDING_FILE):
        choice = input("Am găsit un fișier de înregistrare. Doriți să îl încărcați? (y/n): ")
        if choice.lower() == 'y':
            load_recording()
        elif choice.lower() != 'n':
            print("Alegere invalidă. Programul se va opri.")
            sys.exit(0)

    keyboard_listener = keyboard.Listener(on_press=on_key_press, on_release=on_key_release)
    mouse_listener = mouse.Listener(on_click=on_click, on_move=on_move, on_scroll=on_scroll)

    keyboard_listener.start()
    mouse_listener.start()

    print("🎬 F2 = Înregistrare | F1 = Redare | F3 = Pauză/Reluare | F12 = Oprire completă")
    keyboard_listener.join()
    mouse_listener.join()

if __name__ == '__main__':
    main()
