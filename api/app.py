from flask import Flask, request, jsonify
from image import get_image_data
from video import get_video_data
import hashlib

app = Flask(__name__)

def verify_token(token):
    return token == hashlib.md5('bracket-ai-services'.encode()).hexdigest()

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    token = request.headers.get('Authorization')

    if not token or not verify_token(token.replace('Bearer ', '')):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    image_url = data.get('image_url')
    if not image_url:
        return jsonify({"error": "No image URL provided"}), 400

    result = get_image_data(image_url)
    if not result:
        return jsonify({"error": "No image data to show"}), 400

    return jsonify(result)

@app.route('/analyze-video', methods=['POST'])
def analyze_video():
    token = request.headers.get('Authorization')

    if not token or not verify_token(token.replace('Bearer ', '')):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    video_url = data.get('video_url')
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    result = get_video_data(video_url)
    if not result:
        return jsonify({"error": "No video data to show"}), 400

    return jsonify(result)

app = app