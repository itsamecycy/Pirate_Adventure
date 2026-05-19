import json
import os
from datetime import datetime


class SaveData:

    def __init__(self, filepath="save_data.json", slots=5):
        self.filepath = filepath
        self.slots = slots
        self.data = self._load_file()

    def _load_file(self):
        if not os.path.exists(self.filepath):
            return {"slots": [None] * self.slots}

        try:
            with open(self.filepath, "r", encoding="utf-8") as save_file:
                raw = json.load(save_file)
        except (json.JSONDecodeError, IOError):
            return {"slots": [None] * self.slots}

        if isinstance(raw, dict) and isinstance(raw.get("slots"), list):
            slots = raw["slots"]
        else:
            slots = [raw]

        if len(slots) < self.slots:
            slots += [None] * (self.slots - len(slots))
        return {"slots": slots[: self.slots]}

    def _save_file(self):
        os.makedirs(os.path.dirname(self.filepath) or ".", exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as save_file:
            json.dump(self.data, save_file, indent=4)

    def get_slot(self, index):
        if index < 0 or index >= self.slots:
            return None
        return self.data["slots"][index]

    def get_slot_list(self):
        return self.data["slots"][:]

    def save_slot(self, index, save_state):
        if index < 0 or index >= self.slots:
            return False
        slot = dict(save_state)
        slot["saved_at"] = datetime.utcnow().isoformat() + "Z"
        self.data["slots"][index] = slot
        self._save_file()
        return True

    def load_slot(self, index):
        return self.get_slot(index)

    def clear_slot(self, index):
        if index < 0 or index >= self.slots:
            return False
        self.data["slots"][index] = None
        self._save_file()
        return True

    def has_slot(self, index):
        return self.get_slot(index) is not None
