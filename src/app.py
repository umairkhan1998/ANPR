from flask import Flask, request, render_template, jsonify, Response, send_from_directory
from detection import process_image, generate_frames  # Removed process_video
from database import check_plate_status
import os

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
if __name__ == "__main__":
    app.run(debug=True)
