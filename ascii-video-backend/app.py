import cv2
import os
import sys
import time
import numpy as np
import tempfile
import ffmpeg
from flask import Flask, request, jsonify, send_file

# ---------- FLASK SETUP ----------
app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------- ASCII CHAR SET ----------
ascii_chars = " .:-=+*#%@"

# ---------- FRAME TO ASCII CONVERSION ----------
def convert_frame_to_color_ascii(frame, width=80, brightness=1.0):
    height = int(frame.shape[0] * width / frame.shape[1] / 2)
    if height <= 0:
        height = 1

    resized = cv2.resize(frame, (width, height))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    gray = np.clip(gray * brightness, 0, 255).astype(np.uint8)
    normalized = gray / 255.0

    lines = []
    for y in range(height):
        row = []
        for x in range(width):
            pixel_brightness = normalized[y][x]
            b, g, r = resized[y, x]
            index = int(pixel_brightness * (len(ascii_chars) - 1))
            char = ascii_chars[index]
            color_char = f"\033[38;2;{r};{g};{b}m{char}\033[0m"
            row.append(color_char)
        lines.append("".join(row))
    return "\n".join(lines)

# ---------- API ROUTES ----------
@app.route('/')
def home():
    return jsonify({
        "message": "🎞️ ASCII Video Converter API is running!",
        "usage": "POST a video file to /convert with form-data { video, width(optional), brightness(optional) }"
    })

@app.route('/convert', methods=['POST'])
def convert_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video = request.files['video']
    width = int(request.form.get('width', 80))
    brightness = float(request.form.get('brightness', 1.0))

    video_path = os.path.join(UPLOAD_FOLDER, video.filename)
    video.save(video_path)

    cap = cv2.VideoCapture(video_path)
    ascii_output = tempfile.NamedTemporaryFile(delete=False, suffix=".txt").name

    with open(ascii_output, "w", encoding="utf-8") as f:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            ascii_frame = convert_frame_to_color_ascii(frame, width, brightness)
            f.write(ascii_frame + "\n\n")

    cap.release()

    return send_file(ascii_output, as_attachment=True, download_name="ascii_video.txt")

# ---------- RUN LOCALLY ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
