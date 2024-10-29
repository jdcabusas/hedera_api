import requests
import base64
import sys
import json

# Hedera mirror node URL for the testnet
MIRROR_NODE_URL = "https://testnet.mirrornode.hedera.com/api/v1"

def fetch_past_events(topic_id):
    # Construct the URL for the topic messages endpoint
    url = f"{MIRROR_NODE_URL}/topics/{topic_id}/messages"
    
    try:
        # Make a GET request to the mirror node API
        response = requests.get(url)
        response.raise_for_status()

        # Parse the response JSON
        messages = response.json().get("messages", [])
        result = []

        # Process the messages
        if messages:
            for message in messages:
                content = message.get("message")
                
                # Decode the content from base64
                decoded_message = base64.b64decode(content).decode("utf-8")
                
                # Append the result as a dictionary
                result.append({
                    "timestamp": message.get("consensus_timestamp"),
                    "decoded_message": decoded_message,
                })
        else:
            result.append({"error": "No messages found for this topic."})

        # Return the result as a JSON string
        return json.dumps(result)
    
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"An error occurred while fetching messages: {str(e)}"})

# Run the function with the topic_id from command line argument
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: python get_topic_events.py <topic_id>"}))
    else:
        topic_id = sys.argv[1]
        output = fetch_past_events(topic_id)
        print(output)
