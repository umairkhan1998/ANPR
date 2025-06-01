import os

UPLOAD_FOLDER = 'uploads'
JSON_FOLDER = 'json'
DB_PATH = 'free.db'
MODEL_PATH = 'TRF_8.pt'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(JSON_FOLDER, exist_ok=True)
JSON_PATH = os.path.join(JSON_FOLDER, 'json.json')
