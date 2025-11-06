from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2, os, numpy as np, tempfile, ffmpeg, traceback

app = Flask(__name__)

# ✅ FIX: Apply CORS globally (including send_file responses)
CORS(app, resources={r"/*": {"origins": ["https://shanmukhcr7.github.io"]}})

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ascii_chars = " .:-=+*#%@"

def frame_to_ascii_image(frame, width=120, brightness=1.0, font_scale=0.4, color=False):
    """
    Convert a single frame to an image of ASCII characters.
    """
    height = int(frame.shape[0] * width / frame.shape[1] / 2)
    if height < 1:
        height = 1
    resized = cv2.resize(frame, (width, height))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    gray = np.clip(gray * brightness, 0, 255).astype(np.uint8)
    normalized = gray / 255.0

    char_w, char_h = 10, 18
    canvas = np.ones((height * char_h, width * char_w, 3), dtype=np.uint8) * 0  # black background

    for y in range(height):
        for x in range(width):
            index = int(normalized[y][x] * (len(ascii_chars) - 1))
            char = ascii_chars[index]
            color_val = resized[y, x] if color else (255, 255, 255)
            cv2.putText(canvas, char, (x * char_w, y * char_h + char_h),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, color_val, 1, cv2.LINE_AA)
    return canvas


@app.route('/')
def home():
    return jsonify({"message": "🎞️ ASCII Video Converter API running!"})


@app.route('/convert', methods=['POST'])
def convert_video():
    try:
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400

        video = request.files['video']
        width = int(request.form.get('width', 120))
        brightness = float(request.form.get('brightness', 1.0))
        color = request.form.get('color', 'false').lower() == 'true'

        video_path = os.path.join(UPLOAD_FOLDER, video.filename)
        video.save(video_path)

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        if not fps or fps == 0:
            fps = 24.0  # fallback to default
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Output path for converted video
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

        ret, test_frame = cap.read()
        if not ret:
            return jsonify({"error": "Could not read video"}), 400

        h, w, _ = frame_to_ascii_image(test_frame, width).shape
        out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (w, h))

        frame_no = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_no += 1

            # Convert frame
            ascii_frame = frame_to_ascii_image(frame, width, brightness, color=color)
            out.write(ascii_frame)

            # Skip frames to reduce CPU usage (Render free plans time out at ~90s)
            if frame_no % 2 == 0:
                continue

        cap.release()
        out.release()

        return send_file(output_path, as_attachment=True, download_name="ascii_video.mp4")

    except Exception as e:
        print("🔥 ERROR during /convert:", str(e))
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
