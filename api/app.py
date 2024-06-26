from flask import Flask, request, jsonify
import requests
from openai import OpenAI
import os
import hashlib
import re

app = Flask(__name__)
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model = os.getenv('OPENAI_MODEL_NAME')

def verify_token(token):
    return token == hashlib.md5('bracket-ai-services'.encode()).hexdigest()

def get_image_data(image_url):
    response = requests.get(image_url)
    if response.status_code != 200:
        return {"error": "Could not download the image"}

    try:
        prompt = (
            f"You are an expert SEO analyst, we need to generate metadata for this image, following google's criteria for best performance please generate:\n"
            f"Caption: Provide a caption for the image.\n"
            f"Tags: Provide relevant tags for the image.\n"
            f"Description: Provide a detailed description of the image.\n"
            f"Alt Text: Provide alternative text for accessibility for the image.\n"
            f"Ff you are not able to interpret this images just fill the fields with \"blank\"\n"
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text", 
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )

        output = response.choices[0].message.content.strip()

        caption = re.search(r'Caption: (.+)', output).group(1)
        tags = re.search(r'Tags: (.+)', output).group(1).split(", ")
        description = re.search(r'Description: (.+)', output).group(1)
        alt_text = re.search(r'Alt Text: (.+)', output).group(1)

        result = {
            "caption": caption,
            "tags": tags,
            "description": description,
            "alt_text": alt_text
        }
    except Exception as e:
        result = {"error": str(e)}

    return result

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

app = app