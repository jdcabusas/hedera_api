import requests
import sys
import json  # Import json for formatting output

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": "Bearer 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"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

def summarize_text(text):
    output = query({
        "inputs": text,
    })
    return output

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No text provided for summarization."}))  # Change to JSON format
        sys.exit(1)

    input_text = ' '.join(sys.argv[1:])
    output = summarize_text(input_text)

    # Extract the summary text for a clearer output
    summary_text = output[0]['summary_text'] if isinstance(output, list) and len(output) > 0 else "No summary available."
    print(json.dumps({"summary_text": summary_text}))  # Return as JSON

