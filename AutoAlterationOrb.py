import tkinter as tk
from tkinter import scrolledtext
import keyboard
import pyautogui
import pyperclip
import time
import re
import threading

pyautogui.PAUSE = 0

COPY_DELAY = 0.015
CLICK_DELAY = 0.005
ITERATION_DELAY = 0.02

running = False


def extract_item_name(text):
    lines = text.splitlines()
    capture = False
    extracted = []

    for line in lines:
        if line.startswith("Rarity:") or line.startswith("稀有度:"):
            capture = True
            continue

        if line.strip() == "--------" and capture:
            break

        if capture:
            extracted.append(line)

    return "".join(line.lstrip() for line in extracted)


def log(message):
    output_box.insert(tk.END, message + "\n")
    output_box.see(tk.END)


def stop_script():
    global running
    running = False
    pyautogui.keyUp("shift")
    pyautogui.keyUp("ctrl")
    log("Stopped. Ready again.")


def run_script():
    global running

    if running:
        return

    user_regex = regex_entry.get().strip()

    if not user_regex:
        log("Please enter a regex first.")
        return

    try:
        compiled_regex = re.compile(user_regex, re.IGNORECASE)
    except re.error as e:
        log(f"Invalid regex: {e}")
        return

    try:
        safety_limit = int(limit_entry.get())
    except ValueError:
        safety_limit = 40

    ctrl_click_enabled = ctrl_click_var.get()

    running = True
    attempts = 0
    attempt_width = len(str(safety_limit))

    log("Started. Shift is being held automatically.")

    pyautogui.keyDown("shift")

    try:
        while running and attempts < safety_limit:
            pyautogui.hotkey("ctrl", "c")
            time.sleep(COPY_DELAY)

            raw_text = pyperclip.paste()
            item_name = extract_item_name(raw_text)

            matched = compiled_regex.search(raw_text)

            if matched:
                log(f"Match found: {item_name}")
                break

            log(
                f"Attempt {str(attempts + 1).rjust(attempt_width)} | "
                f"Item: {item_name}"
            )

            pyautogui.click()
            time.sleep(CLICK_DELAY)

            if ctrl_click_enabled:
                    time.sleep(0.02)  # 👈 slight delay before augment

                    try:
                        pyautogui.keyDown("ctrl")
                        time.sleep(0.005)
                        pyautogui.click()
                    finally:
                        pyautogui.keyUp("ctrl")

            attempts += 1
            time.sleep(ITERATION_DELAY)

        if attempts >= safety_limit:
            log(f"Reached safety limit: {safety_limit}")

    finally:
        running = False
        pyautogui.keyUp("shift")
        pyautogui.keyUp("ctrl")
        log("Ready again. Press Shift+= to start.")


def start_thread():
    threading.Thread(target=run_script, daemon=True).start()


root = tk.Tk()
root.title("PoE Regex Roller")
root.geometry("700x470")

tk.Label(root, text="Regex to match full copied item text:").pack(anchor="w", padx=10, pady=(10, 0))

regex_entry = tk.Entry(root, width=85)
regex_entry.pack(padx=10, pady=5)

tk.Label(root, text="Safety limit:").pack(anchor="w", padx=10)

limit_entry = tk.Entry(root, width=20)
limit_entry.insert(0, "40")
limit_entry.pack(anchor="w", padx=10, pady=5)

ctrl_click_var = tk.BooleanVar()

tk.Checkbutton(
    root,
    text="Enable extra Ctrl + Left Click after normal click",
    variable=ctrl_click_var
).pack(anchor="w", padx=10, pady=5)

tk.Label(
    root,
    text="Hotkeys: Shift+= Start | Shift+- Stop | Esc Emergency Stop"
).pack(pady=5)

output_box = scrolledtext.ScrolledText(root, width=85, height=20)
output_box.pack(padx=10, pady=10)

log("Ready. Enter regex, set mode, then use Shift+= in game.")

keyboard.add_hotkey("shift+=", start_thread)
keyboard.add_hotkey("shift+-", stop_script)
keyboard.add_hotkey("esc", stop_script, suppress=False)
keyboard.add_hotkey("shift+esc", stop_script, suppress=False)

root.mainloop()