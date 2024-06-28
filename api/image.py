import requests
from openai import OpenAI
import os
import re

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
model = os.getenv('OPENAI_MODEL_NAME')

def get_image_data(image_url):
    try:
        image_url = image_url.replace('\\/', '/')
        response = requests.get(image_url)
        if response.status_code != 200:
            return {"error": "Could not download the image"}
        
        prompt = (
            f"You are an expert SEO analyst, we need to generate metadata for this image, following google's criteria for best performance please generate:\n"
            f"Caption: Provide a caption for the image.\n"
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
        caption = re.search(r'Caption: (.+)', output).group(1) if re.search(r'Caption: (.+)', output) else ''
        description = re.search(r'Description: (.+)', output).group(1) if re.search(r'Description: (.+)', output) else ''
        alt_text = re.search(r'Alt Text: (.+)', output).group(1) if re.search(r'Alt Text: (.+)', output) else ''

        result = {
            "caption": caption,
            "description": description,
            "alt_text": alt_text
        }
    except Exception as e:
        result = {"error": str(e)}

    return result