import requests
import base64
import json
import argparse
import os

API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
hugging_face_token = os.environ.get("HUGGING_FACE_TOKEN")
headers = {"Authorization": f"Bearer {hugging_face_token}"}

def query(filename):
    with open(filename, "rb") as f:
        data = f.read()
        # Encode audio data as base64
        encoded_audio = base64.b64encode(data).decode("utf-8")

    # Set the parameters with return_timestamps
    payload = {
        "inputs": encoded_audio,
        "parameters": {
            "return_timestamps": True
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        print(json.dumps({"error": "Request to the API failed", "details": response.text}))
        return {"error": "Request to the API failed"}

    response_json = response.json()  # Parse JSON response directly

    # Format output to be valid JSON
    output = {
        "text": response_json.get('text', 'No text returned'),
        "chunks": []
    }
    
    for chunk in response_json.get('chunks', []):
        start, end = chunk['timestamp']
        output["chunks"].append({
            "timestamp": [start, end],
            "text": chunk['text']
        })

    # Print the output as JSON
    print(json.dumps(output))  # Output the result as a JSON string

    return output  # Return the original response if needed

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process a FLAC audio file for transcription.")
    parser.add_argument("filename", type=str, help="The path to the FLAC audio file.")

    args = parser.parse_args()
    query(args.filename)

