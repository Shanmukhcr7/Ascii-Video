from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2, os, numpy as np, tempfile, ffmpeg

app = Flask(__name__)
CORS(app, origins=["https://shanmukhcr7.github.io"])  # ✅ Allow only your GitHub Pages frontend

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ascii_chars = " .:-=+*#%@"

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

@app.route('/')
def home():
    return jsonify({"message": "ASCII Video Converter API running!"})

@app.route('/convert', methods=['OPTIONS'])
def convert_options():
    return '', 200

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

    frame_count = 0
    with open(ascii_output, "w", encoding="utf-8") as f:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            if frame_count % 10 != 0:  # skip frames to save time
                continue
            ascii_frame = convert_frame_to_color_ascii(frame, width, brightness)
            f.write(ascii_frame + "\n\n")

    cap.release()
    return send_file(ascii_output, as_attachment=True, download_name="ascii_video.txt")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
