import os

UPLOAD_FOLDER = 'uploads'
EXCEL_FOLDER = 'excel_reports'
DB_PATH = 'my_database.db'
MODEL_PATH = 'best (1).pt'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXCEL_FOLDER, exist_ok=True)
EXCEL_PATH = os.path.join(EXCEL_FOLDER, 'license_plates.xlsx')