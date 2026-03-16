# Advanced Macro Recorder & Player

A sophisticated Python-based tool for recording and replaying keyboard and mouse activities. This script captures user actions with precise timing and allows for infinite playback, making it ideal for automating repetitive tasks.

## 🚀 Features

- **Comprehensive Event Recording**: Captures a wide range of actions, including key presses, key releases, mouse clicks, mouse movement, and mouse scrolling.
- **Persistent Recordings**: Save your recorded sessions to a `recording.json` file for later use.
- **Load & Play**: Load any previously saved recording and play it back.
- **Infinite Loop Playback**: Plays the recorded sequence repeatedly until stopped.
- **Hotkey Controls**: Easy-to-use hotkeys to manage recording and playback without a GUI.
  - `F1`: Start/Stop Playback
  - `F2`: Start/Stop Recording
  - `F3`: Pause/Resume Recording
  - `F12`: Force kill the entire program.
- **Thread-Safe Operations**: Recording and playback run in separate threads with safety checks to prevent conflicts.
- **Action Logging**: Key playback cycle events are logged in `replay_log.txt`.

## 🛠️ Technology Stack

- **Language**: **Python 3**
- **Core Library**: **`pynput`** - A powerful library for monitoring and controlling input devices like the keyboard and mouse.

## ⚙️ How It Works

The application is built around a few core concepts:

### 1. Event Listening
Two listener threads from the `pynput` library run in the background:
- `pynput.keyboard.Listener`: Monitors all key presses and releases.
- `pynput.mouse.Listener`: Monitors mouse clicks, movement, and scrolling.

Each time an event is detected, a callback function (`on_key_press`, `on_click`, etc.) is invoked.

### 2. Event Capturing and Timestamping
When recording is active, each event captured by the listeners is passed to the `log_event` function. This function calculates a relative timestamp based on the time elapsed since the recording started. It then formats the event data and the timestamp into a tuple: `(event_type, event_data, timestamp)`.

- **Keyboard Events**: To ensure they can be re-evaluated during playback, keys are stored as either their character representation (e.g., `'a'`) or their full object path (e.g., `'keyboard.Key.space'`).
- **Mouse Events**: Mouse actions are stored with their coordinates and button/scroll information.

This list of event tuples is stored in a global `events` list.

### 3. Saving and Loading
- **Saving**: When recording stops, the `save_recording` function is called. It uses Python's `json` module to serialize the `events` list and write it to `recording.json`.
- **Loading**: Before playback, the `load_recording` function reads the `recording.json` file, deserializes its content, and populates the global `events` list.

### 4. Playback Mechanism
Playback is handled in a separate thread to keep the main application responsive.
- A **safe copy** of the events is passed to the playback thread to prevent conflicts.
- The function uses `pynput.keyboard.Controller` and `pynput.mouse.Controller` to simulate the input events.
- It iterates through the event list, using `time.sleep()` to wait for the correct relative timestamp of each event. This ensures the playback speed matches the original recording speed.
- Python's `eval()` function is used to interpret the stored keyboard event strings back into pressable key objects.

## 📦 Installation & Usage

### Prerequisites
- Python 3.x
- pip (Python package installer)

### Installation
1. Clone or download the project files.
2. Open a terminal in the project directory.
3. Install the required library:
   ```sh
   pip install pynput
   ```

### Running the Script
Execute the main script from your terminal:
```sh
python keylogger_plus.py
```
The application will start, and you can use the hotkeys to control it.

### Hotkey Guide

| Key | Action                                       |
|:---:|:---------------------------------------------|
|`F1` | Toggles playback of the `recording.json` file. |
|`F2` | Toggles recording. Starts a new recording or stops the current one. |
|`F3` | Pauses or resumes the current recording.       |
|`F12`| Immediately terminates the application.      |


## 📂 File Structure

```
.
├── keylogger_plus.py   # The main application script
├── recording.json      # Default file for saving/loading recordings
└── replay_log.txt      # Log file for playback cycle information
```

## 📄 License

This project can be considered under the **MIT License**. You are free to use, modify, and distribute it.
