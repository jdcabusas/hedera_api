from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime, timedelta
import subprocess
import json
import os

app = Flask(__name__)
CORS(app)

@app.route('/create_topic', methods=['GET'])
def create_topic():
    memo = request.args.get('memo')  # Get the memo parameter from the request
    if not memo:
        return jsonify({'success': False, 'message': 'Missing memo parameter'}), 400
    
    try:
        # Run the script and capture its print output
        result = subprocess.run(['python', 'create_topic.py', memo], capture_output=True, text=True)
        
        # Capture any print output directly from the script
        print_output = result.stdout.strip()
        
        return jsonify({
            'success': result.returncode == 0,
            'data': json.loads(print_output) if result.returncode == 0 else None,
            'error': result.stderr.strip() if result.returncode != 0 else None  # Only include stderr if there's an error
        }), 200 if result.returncode == 0 else 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred.', 'error': str(e)}), 500

@app.route('/send_event', methods=['GET'])
def send_event():
    topic_id = request.args.get('topic_id')
    event_message = request.args.get('event_message')

    if not topic_id or not event_message:
        return jsonify({'success': False, 'message': 'Missing topic_id or event_message'}), 400

    try:
        result = subprocess.run(['python', 'send_event.py', topic_id, event_message], capture_output=True, text=True)
        print_output = result.stdout.strip()
        
        return jsonify({
            'success': result.returncode == 0,
            'data': json.loads(print_output) if result.returncode == 0 else None,
            'error': result.stderr.strip() if result.returncode != 0 else None  # Only include stderr if there's an error
        }), 200 if result.returncode == 0 else 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred.', 'error': str(e)}), 500

@app.route('/get_topic_events', methods=['GET'])
def get_topic_events():
    topic_id = request.args.get('topic_id')
    if not topic_id:
        return jsonify({'success': False, 'message': 'Missing topic_id'}), 400

    try:
        result = subprocess.run(['python', 'get_topic_events.py', topic_id], capture_output=True, text=True)
        print_output = result.stdout.strip()
        
        return jsonify({
            'success': result.returncode == 0,
            'data': json.loads(print_output) if result.returncode == 0 else None,
            'error': result.stderr.strip() if result.returncode != 0 else None  # Only include stderr if there's an error
        }), 200 if result.returncode == 0 else 500
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred.', 'error': str(e)}), 500

@app.route('/get_topic_ids', methods=['GET'])
def get_topic_ids():
    try:
        with open('topics_list.json', 'r') as file:
            topics = json.load(file)
        return jsonify({
            'success': True,
            'data': topics
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'An error occurred.', 'error': str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    # Get the JSON data from the request
    data = request.get_json()

    # Check if 'text' is provided in the request data
    if 'text' not in data:
        return jsonify({'error': 'No text provided for summarization.'}), 400

    input_text = data['text']

    # Call the summarization script and pass the input text as a parameter
    try:
        result = subprocess.run(['python', 'summarization_ai.py', input_text],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)

        # Check for errors in the script execution
        if result.returncode != 0:
            return jsonify({'error': 'Error in summarization script: ' + result.stderr}), 500

        # Parse the output as JSON
        output_json = json.loads(result.stdout)  # Load the JSON output from the script

        # Return the output from the script as JSON
        return jsonify(output_json), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request."}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400

    # Save the uploaded file to a temporary location
    temp_file_path = os.path.join('temp', file.filename)
    os.makedirs('temp', exist_ok=True)  # Create temp directory if it doesn't exist
    file.save(temp_file_path)

    # Execute the auto_speech_recog.py script with the file as a parameter
    try:
        result = subprocess.run(
            ["python", "auto_speech_recog.py", temp_file_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Assuming the output of your script is in JSON format
        output = json.loads(result.stdout)

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Error processing the file", "details": e.stderr}), 500

    # Remove the temporary file after processing
    os.remove(temp_file_path)

    # Return the response
    return jsonify({
        "full_text": output.get('text', 'No text returned'),
        "chunks": output.get('chunks', [])
    })

# File to store IP request logs
IP_LOG_FILE = "ip_list.json"

def load_ip_logs():
    """Load IP logs from the text file into a dictionary."""
    if not os.path.exists(IP_LOG_FILE):
        return {}
    
    try:
        with open(IP_LOG_FILE, 'r') as file:
            ip_logs = json.load(file)
            # Convert timestamps from strings back to datetime objects
            for ip, timestamps in ip_logs.items():
                ip_logs[ip] = [datetime.fromisoformat(ts) for ts in timestamps]
            return ip_logs
    except (json.JSONDecodeError, ValueError):
        # If the file is empty or invalid, return an empty dictionary
        return {}

def save_ip_logs(ip_logs):
    """Save IP logs to the text file."""
    with open(IP_LOG_FILE, 'w') as file:
        # Convert datetime objects to strings for JSON serialization
        json.dump({ip: [ts.isoformat() for ts in timestamps] for ip, timestamps in ip_logs.items()}, file)

@app.route('/generate-image', methods=['POST'])
def generate_image():
    # Load IP logs from file
    ip_request_log = load_ip_logs()
    
    # Get the IP address of the requester
    ip_address = request.remote_addr
    current_time = datetime.now()
    
    # Check or initialize IP entry in ip_request_log
    if ip_address not in ip_request_log:
        ip_request_log[ip_address] = []
    
    # Filter out requests that are older than 24 hours
    ip_request_log[ip_address] = [
        timestamp for timestamp in ip_request_log[ip_address]
        if timestamp > current_time - timedelta(hours=24)
    ]
    
    # Check if the IP has reached the limit of 3 requests in the past 24 hours
    if len(ip_request_log[ip_address]) >= 3:
        return jsonify({"message": "Users can only generate three images in a 24 hour period."}), 200
    
    # Record the new request timestamp
    ip_request_log[ip_address].append(current_time)
    
    # Save updated IP logs back to file
    save_ip_logs(ip_request_log)
    
    # Get the input string from the request
    data = request.json
    input_string = data.get('input_string')

    if not input_string:
        return jsonify({"error": "No input string provided"}), 400

    # Prepare the command to run the generate_image.py script
    command = ['python', 'generate_image.py', input_string]

    # Run the script and wait for it to finish
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": str(e)}), 500

    # Send the generated image file back to the frontend
    output_image_path = "output_image.png"
    if os.path.exists(output_image_path):
        return send_file(output_image_path, mimetype='image/png')
    else:
        return jsonify({"error": "Image generation failed."}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
