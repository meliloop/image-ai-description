from IPython.display import display, Image, Audio
import cv2
import base64
from openai import OpenAI
import os
import re

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model = os.getenv('OPENAI_MODEL_NAME')

def get_video_data(video_url):
    try:
        video_url = video_url.replace('\\/', '/')
        video = cv2.VideoCapture(video_url)

        base64_frames = []
        while video.isOpened():
            success, frame = video.read()
            if not success:
                break
            _, buffer = cv2.imencode(".jpg", frame)
            base64_frames.append(base64.b64encode(buffer).decode("utf-8"))

        video.release()

        # Take a sample of frames for prompt (e.g., every 50th frame)
        sample_frames = base64_frames[0::50]

        prompt = [
            "These are frames from a video that I want to upload. Please generate:\n",
            "Caption: Provide a caption for the video.\n",
            "Description: Provide a detailed description of the video.\n",
            "Alt Text: Provide alternative text for accessibility for the video.\n",
            "If you are not able to interpret these frames, just fill the fields with 'blank'.\n",
            *map(lambda x: {"image": x, "resize": 768}, sample_frames)
        ]
            
        response = client.chat_completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=200,
        )

        output = response.choices[0].message.content.strip()
        caption = re.search(r'Caption: (.+)', output).group(1) if re.search(r'Caption: (.+)', output) else 'blank'
        description = re.search(r'Description: (.+)', output).group(1) if re.search(r'Description: (.+)', output) else 'blank'
        alt_text = re.search(r'Alt Text: (.+)', output).group(1) if re.search(r'Alt Text: (.+)', output) else 'blank'

        result = {
            "caption": caption,
            "description": description,
            "alt_text": alt_text
        }
    except Exception as e:
        result = {"error": str(e)}

    return result