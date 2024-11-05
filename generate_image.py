import requests
import sys
import os

API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-dev"
#API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3-medium-diffusers"
#API_URL = "https://api-inference.huggingface.co/models/stabilityai/sdxl-turbo"
hugging_face_token = os.environ.get("HUGGING_FACE_TOKEN")
headers = {"Authorization": f"Bearer {hugging_face_token}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

# Check if the user provided an input string
if len(sys.argv) != 2:
    print("Usage: python generate_image.py <STRING TO ENTER>")
    sys.exit(1)

input_string = sys.argv[1]

image_bytes = query({
    "inputs": input_string,
})

# Save the image bytes directly to a file
with open("output_image.png", "wb") as f:
    f.write(image_bytes)

print("Image generated")
