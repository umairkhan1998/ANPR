
import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR
from utils import save_detection_to_json
from database import check_plate_status
from flask import jsonify
import os
import re 
os.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'
from config import MODEL_PATH, UPLOAD_FOLDER


model = YOLO(MODEL_PATH)
ocr = PaddleOCR(use_angle_cls=True, use_gpu=True)#det_db_box_thresh=0.5

def paddle_ocr(frame, x1, y1, x2, y2):
    cropped_frame = frame[y1:y2, x1:x2]
    result = ocr.ocr(cropped_frame, det=False, rec=True, cls=True)
    raw_text = " ".join(r[0][0] for r in result if r and r[0][1] > 0.6)
    
    # Words to ignore in OCR results (case insensitive)
    ignore_words = ["ISLAMABAD", "PESHAWAR", "ICT", "SWAT", "KPK","NWFP"]
    for word in ignore_words:
        raw_text = re.sub(re.escape(word), "", raw_text, flags=re.IGNORECASE)
    cleaned_text = re.sub(r"[^A-Za-z0-9 ]", "", raw_text)
    cleaned_text = cleaned_text.replace("O", "0").replace("粤", "").replace("8B","BB")
    return cleaned_text.strip()

def process_image(request):
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    image = cv2.imread(file_path)
    results = model.predict(image, conf=0.7, iou=0.5)

    detected_plates = []
    for result in results: #Detected plate in the image  
        for box in result.boxes: # Bounding box
            x1, y1, x2, y2 = map(int, box.xyxy[0])# Get the coordinates of bounding box(top left and bottem right)
            plate_text = paddle_ocr(image, x1, y1, x2, y2)
            if plate_text:
                status = check_plate_status(plate_text)
                detected_plates.append({
                    "plate": plate_text, 
                    "status": status,
                    "coords": (x1, y1, x2, y2)
                })
                
                # Draw rectangle and text with status
                color = (0, 255, 0) if status == "Paid" else (0, 0, 255)
                cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
                cv2.putText(image, f"{plate_text} - {status}", (x1, y1 - 5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    save_detection_to_json(detected_plates)

    output_path = os.path.join(UPLOAD_FOLDER, "output.jpg")
    cv2.imwrite(output_path, image)

    return jsonify({
        "plates": detected_plates, 
        "output_image": f"/uploads/output.jpg"
    })

def generate_frames():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        results = model.predict(frame, conf=0.70)
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

                    # Visual feedback based on status
                    color = (0, 255, 0) if status == "Paid" else (0, 0, 255)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    cv2.putText(frame, f"{plate_text} - {status}", (x1, y1 - 10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        save_detection_to_json(detected_plates)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')