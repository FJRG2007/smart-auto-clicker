import os, pickle
from src.utils.basics import get_config_path

class MemoryManagerClass:
    def __init__(self):
        self.file_name = os.path.join(get_config_path(), "memory.pkl")
        self.memory = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.file_name):
            try:
                with open(self.file_name, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                print(f"Error loading memory: {e}")
                return {}
        return {}

    def save_memory(self):
        try:
            with open(self.file_name, "wb") as f:
                pickle.dump(self.memory, f)
        except Exception as e: print(f"Error saving memory: {e}")

    def set(self, key, value):
        self.memory[key] = value

    def get(self, key, default=None):
        return self.memory.get(key, default)

    def delete(self, key):
        if key in self.memory: del self.memory[key]

    def clear(self):
        self.memory.clear()
        self.save_memory()

MemoryManager = MemoryManagerClass()