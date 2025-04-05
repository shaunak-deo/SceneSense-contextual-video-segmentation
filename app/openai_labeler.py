import os
import base64
import time
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def label_frames(image_paths):
    captions = []
    for path in image_paths:
        base64_img = encode_image(path)
        max_retries = 5
        retry_delay = 1  # seconds
        
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": [
                        {"type": "text", "text": "List 3-5 key ad-related tags for this scene. Focus on: product categories, brand types, or commercial elements. Keep each tag short (1-3 words). Format as comma-separated tags."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]}
                ],
                max_tokens=50)
                captions.append(response.choices[0].message.content)
                break  # Success, exit retry loop
            except Exception as e:
                if "rate_limit" in str(e).lower() and attempt < max_retries - 1:
                    print(f"Rate limit reached. Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    print(f"Error processing image: {e}")
                    captions.append("Error: Could not process image")
                    break
    return captions