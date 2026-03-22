import json
import os

SAVE_FILE = "save.json"

def load_progress():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                return data.get("unlocked_levels", 1)
        except:
            return 1
    return 1

def save_progress(unlocked_levels):
    # Only save if the new unlocked level is greater than the current one
    current = load_progress()
    if unlocked_levels > current:
        with open(SAVE_FILE, "w") as f:
            json.dump({"unlocked_levels": unlocked_levels}, f)
