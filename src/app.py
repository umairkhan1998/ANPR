from flask import Flask, request, render_template, jsonify, Response, send_from_directory
from detection import process_image, generate_frames 
from database import check_plate_status
import os
import pandas as pd
from config import EXCEL_PATH

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/detect", methods=["POST"])
def detect():
    return process_image(request)

@app.route("/upload_image", methods=["POST"])
def upload_image():
    return process_image(request)

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@app.route("/live_detect")
def live_detect():
    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")



@app.route("/view_report")
def view_report():
    try:
        df = pd.read_excel(EXCEL_PATH)
        return jsonify({
            "success": True,
            "data": df.to_dict(orient='records')
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

if __name__ == "__main__":
    app.run(debug=True)





















































