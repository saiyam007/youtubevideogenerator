import os
import requests
from dotenv import load_dotenv

load_dotenv()
EURON_API_KEY = os.getenv("EURON_API_KEY")
IMAGE_URL = "https://api.euron.one/api/v1/euri/images/generations"
IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {EURON_API_KEY}"
}

payload = {
    "model": IMAGE_MODEL,
    "prompt": "A simple illustration of a cat sitting on a mat",
    "size": "1024x1024"
}

r = requests.post(IMAGE_URL, headers=headers, json=payload)
print(r.status_code)
print(r.text)
