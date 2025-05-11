import json
import os

MEMORY_DIR = "memory"

def load_memory(name):
    path = os.path.join(MEMORY_DIR, f"{name}.json")
    with open(path, "r") as f:
        return json.load(f)

def save_memory(name, data):
    path = os.path.join(MEMORY_DIR, f"{name}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
