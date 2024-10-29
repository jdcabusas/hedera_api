import json
import os
import sys
from hedera import Client, AccountId, PrivateKey, TopicCreateTransaction

# Initialize client for testnet
client = Client.forTestnet()
client.setOperator(
    AccountId.fromString("0.0.5036759"),
    PrivateKey.fromString("3030020100300706052b8104000a04220420403e1538d2e1e108c59a923c79dd62c784037c521e5884e4da4f0de2a5e34685")
)

# Define topics file
topics_file = "topics_list.json"

def create_and_save_topic(memo):
    try:
        # Create a new topic with the provided memo
        topic_create_txn = TopicCreateTransaction().setTopicMemo(memo).freezeWith(client)

        # Execute the transaction to create the topic
        topic_response = topic_create_txn.execute(client)

        # Get the receipt of the transaction to confirm the topic ID
        receipt = topic_response.getReceipt(client)

        # Ensure topicId is correctly fetched as a string
        topic_id = str(receipt.topicId.toString())

        # Prepare topic data to save
        topic_data = {
            "topic_id": topic_id,
            "memo": memo  # Use the provided memo
        }

        # Load existing topics from the file, if it exists
        if os.path.exists(topics_file):
            with open(topics_file, "r") as file:
                topics = json.load(file)
        else:
            topics = []

        # Append the new topic
        topics.append(topic_data)

        # Save the updated topics list back to the file
        with open(topics_file, "w") as file:
            json.dump(topics, file, indent=4)

        # Prepare success response
        response = {
            "success": True,
            "topic_id": topic_id,
            "memo": memo,
            "message": f"Topic {topic_id} created successfully and saved to {topics_file}."
        }

        print(json.dumps(response))  # Print the result as a JSON string

    except Exception as e:
        print(json.dumps({"success": False, "message": "An error occurred while creating the topic.", "error": str(e)}))

# Run the function with command line argument
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"success": False, "message": "Usage: python create_topic.py <topic_memo>"}))
    else:
        memo = sys.argv[1]
        create_and_save_topic(memo)
