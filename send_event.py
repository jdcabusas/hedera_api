import sys
import json
from hedera import Client, AccountId, PrivateKey, TopicMessageSubmitTransaction, TopicId

# Initialize client for testnet
client = Client.forTestnet()
client.setOperator(
    AccountId.fromString("0.0.5036759"),
    PrivateKey.fromString("3030020100300706052b8104000a04220420403e1538d2e1e108c59a923c79dd62c784037c521e5884e4da4f0de2a5e34685")
)

# Ensure a topic ID is passed as a command-line argument
if len(sys.argv) < 3:
    print(json.dumps({"success": False, "message": "Usage: python send_event.py <topic_id_str> <event_message>"}))
    sys.exit(1)

# Convert the first argument to topic_id_str and the second to event_message
topic_id_str = sys.argv[1]
event_message = sys.argv[2]

# Convert string back to TopicId type
topic_id_obj = TopicId.fromString(topic_id_str)

def push_event_to_topic():
    try:
        # Create and submit the message to the topic
        submit_txn = TopicMessageSubmitTransaction().setTopicId(topic_id_obj).setMessage(event_message)
        response = submit_txn.execute(client)
        receipt = response.getReceipt(client)

        # Confirm the message was successfully submitted
        result = {
            "success": receipt.status.toString() == "SUCCESS",  # Check if the transaction was successful
            "topic_id": topic_id_str,
            "message": event_message,
            "status": receipt.status.toString()  # Include the transaction status
        }

        print(json.dumps(result))  # Print the result as a JSON string

    except Exception as e:
        print(json.dumps({"success": False, "message": "An error occurred while submitting the message to the topic.", "error": str(e)}))

# Run the function
if __name__ == "__main__":
    push_event_to_topic()
