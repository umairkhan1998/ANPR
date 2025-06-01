import json
from config import JSON_PATH

def save_detection_to_json(detected_plates):
    try:
        with open(JSON_PATH, 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    data.extend(detected_plates)
    with open(JSON_PATH, 'w') as file:
        json.dump(data, file, indent=4)
