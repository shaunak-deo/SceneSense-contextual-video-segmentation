import os
import json

# Get the base directory path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def format_time(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def save_labels(data, path):
    """Save labeled segments data to a JSON file"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)