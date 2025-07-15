import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR
from database import check_plate_status
from flask import jsonify
import os
import re 
import pandas as pd
from datetime import datetime
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
from config import MODEL_PATH, UPLOAD_FOLDER, EXCEL_PATH

model = YOLO(MODEL_PATH)
ocr = PaddleOCR(use_angle_cls=True, use_gpu=True)

def initialize_excel():
    if not os.path.exists(EXCEL_PATH):
        df = pd.DataFrame(columns=['License Plate', 'Status', 'Timestamp'])
        df.to_excel(EXCEL_PATH, index=False)

def save_to_excel(plate_data):
    initialize_excel()
    
    # Read existing data
    df = pd.read_excel(EXCEL_PATH)
    
    # Check if plate already exists
    existing_plates = df['License Plate'].tolist()
    
    new_entries = []
    for plate in plate_data:
        if plate['plate'] not in existing_plates:
            new_entries.append({
                'License Plate': plate['plate'],
                'Status': plate['status'],
                'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
    
    if new_entries:
        # Append new entries
        new_df = pd.DataFrame(new_entries)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_excel(EXCEL_PATH, index=False)

def paddle_ocr(frame, x1, y1, x2, y2):
    cropped_frame = frame[y1:y2, x1:x2]
    result = ocr.ocr(cropped_frame, det=False, rec=True, cls=True)
   
    raw_text = " ".join(
        r[0][0] for r in result if r and r[0][1] > 0.6
    )
    ignore_words = ["ISLAMABAD", "PESHAWAR", "ICT", "SWAT", "KPK", "NWFP"]
    for word in ignore_words:
        raw_text = re.sub(re.escape(word), "", raw_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r"[^A-Za-z0-9 ]", "", raw_text)

    def clean_text(text):
        cleaned = re.sub(r'^88(?=[A-Z])', 'BB', text)
        cleaned = re.sub(r'^8(?=[A-Z])', 'B', cleaned)
        return cleaned

    cleaned_text = re.sub(r'(?<=[A-Z])8B(?=[A-Z])', 'BB', cleaned_text)
    cleaned_text = re.sub(r'(?<=[A-Z])88(?=[A-Z])', 'BB', cleaned_text)
    cleaned_text = re.sub(r'([A-Z]+)\s+([0-9]+)', r'\1\2', cleaned_text)
    return cleaned_text.strip()

def process_image(request):
    if "image" not in request.files:
        return jsonify({"error": "No image"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    image = cv2.imread(file_path)
    results = model.predict(image, conf=0.643, iou=0.5)

    detected_plates = []
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            plate_text = paddle_ocr(image, x1, y1, x2, y2)
            if plate_text:
                status = check_plate_status(plate_text)
                detected_plates.append({
                    "plate": plate_text, 
                    "status": status,
                    "coords": (x1, y1, x2, y2)
                })
                
                color = (0, 255, 0) if status == "Paid" else (0, 0, 255)
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                cv2.putText(image, f"{plate_text} - {status}", (x1, y1 - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Save only paid/unpaid plates to Excel (no duplicates)
    plates_to_save = [p for p in detected_plates if p['status'] in ['Paid', 'Unpaid']]
    save_to_excel(plates_to_save)

    output_path = os.path.join(UPLOAD_FOLDER, "output.jpg")
    cv2.imwrite(output_path, image)

    return jsonify({"plates": detected_plates})

def generate_frames():
    cap = cv2.VideoCapture(0)
    initialize_excel()  # Ensure Excel file exists
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        results = model.predict(frame, conf=0.643)
        detected_plates = []

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                plate_text = paddle_ocr(frame, x1, y1, x2, y2)
                if plate_text:
                    status = check_plate_status(plate_text)
                    detected_plates.append({
                        "plate": plate_text, 
                        "status": status,
                        "coords": (x1, y1, x2, y2)
                    })

                    color = (0, 255, 0) if status == "Paid" else (0, 0, 255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{plate_text} - {status}", (x1, y1 - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Save only paid/unpaid plates to Excel (no duplicates)
        plates_to_save = [p for p in detected_plates if p['status'] in ['Paid', 'Unpaid']]
        save_to_excel(plates_to_save)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')






























































# import cv2
# import numpy as np
# from ultralytics import YOLO
# from paddleocr import PaddleOCR
# from utils import save_detection_to_json
# from database import check_plate_status
# from flask import jsonify
# import os
# import re 
# os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
# from config import MODEL_PATH, UPLOAD_FOLDER


# model = YOLO(MODEL_PATH)
# ocr = PaddleOCR(use_angle_cls=True, use_gpu=True)


# def paddle_ocr(frame, x1, y1, x2, y2):
#     cropped_frame = frame[y1:y2, x1:x2]
#     # Run recognition only (det=False), use classification
#     result = ocr.ocr(cropped_frame, det=False, rec=True, cls=True)
   
#     raw_text = " ".join(
#         r[0][0] for r in result if r and r[0][1] > 0.6  # Only keep text with > 60% confidence
#     )
#     # Step 2: Remove known extra words (case-insensitive)
#     ignore_words = ["ISLAMABAD", "PESHAWAR", "ICT", "SWAT", "KPK", "NWFP"]
#     for word in ignore_words:
#         raw_text = re.sub(re.escape(word), "", raw_text, flags=re.IGNORECASE)
#     # Step 3: Clean out special characters
#     cleaned_text = re.sub(r"[^A-Za-z0-9 ]", "", raw_text)

#     def clean_text(text):
#         # Replace only if the string starts with 8 or 88 followed by an uppercase letter
#         cleaned = re.sub(r'^88(?=[A-Z])', 'BB', text)
#         cleaned = re.sub(r'^8(?=[A-Z])', 'B', cleaned)
#         return cleaned

#     # Step 4b: Context-aware replacements
#     cleaned_text = re.sub(r'(?<=[A-Z])8B(?=[A-Z])', 'BB', cleaned_text)
#     cleaned_text = re.sub(r'(?<=[A-Z])88(?=[A-Z])', 'BB', cleaned_text)
#     # Step 5: Post-processing logic to fix `Letter + 0 + Digits` (logo misread as 0)
#    # cleaned_text = re.sub(r'([A-Z])0([0-9]{3,})', r'\1 \2', cleaned_text)
#     # Step 6: Final fix — remove space between letters and numbers (e.g., "ABC 123" → "ABC123")
#     cleaned_text = re.sub(r'([A-Z]+)\s+([0-9]+)', r'\1\2', cleaned_text)
#     return cleaned_text.strip()


# def process_image(request):
#     if "image" not in request.files:
#         return jsonify({"error": "No image "}), 400

#     file = request.files["image"]
#     if file.filename == "":
#         return jsonify({"error": "No selected file"}), 400

#     file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#     file.save(file_path)

#     image = cv2.imread(file_path)
#     results = model.predict(image, conf=0.643, iou=0.5)

#     detected_plates = []
#     for result in results: #Detected plate in the image  
#         for box in result.boxes: # Bounding box
#             x1, y1, x2, y2 = map(int, box.xyxy[0])# Get the coordinates of bounding box(top left and bottem right)
#             plate_text = paddle_ocr(image, x1, y1, x2, y2)
#             if plate_text:
#                 status = check_plate_status(plate_text)
#                 detected_plates.append({
#                     "plate": plate_text, 
#                     "status": status,
#                     "coords": (x1, y1, x2, y2)
#                 })
                
#                 # Draw rectangle and text with status
#                 color = (0, 255, 0) if status == "Paid" else (0, 0, 255)
#                 cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
#                 cv2.putText(image, f"{plate_text} - {status}", (x1, y1 - 5), 
#                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

#     save_detection_to_json(detected_plates)

#     output_path = os.path.join(UPLOAD_FOLDER, "output.jpg")
#     cv2.imwrite(output_path, image)

#     return jsonify({
#         "plates": detected_plates, 
#        # "output_image": f"/uploads/output.jpg"
#     })

# def generate_frames():
#     cap = cv2.VideoCapture(0)
#     while cap.isOpened():
#         success, frame = cap.read()
#         if not success:
#             break

#         results = model.predict(frame, conf=0.643)
#         detected_plates = []

#         for result in results:
#             for box in result.boxes:
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#                 plate_text = paddle_ocr(frame, x1, y1, x2, y2)
#                 if plate_text:
#                     status = check_plate_status(plate_text)
#                     detected_plates.append({
#                         "plate": plate_text, 
#                         "status": status,
#                         "coords": (x1, y1, x2, y2)
#                     })

#                     # Visual feedback based on status
#                     color = (0, 255, 0) if status == "Paid" else (0, 0, 255)
#                     cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
#                     cv2.putText(frame, f"{plate_text} - {status}", (x1, y1 - 10), 
#                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0, 255), 2)

#         save_detection_to_json(detected_plates)

#         _, buffer = cv2.imencode('.jpg', frame)
#         frame_bytes = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')