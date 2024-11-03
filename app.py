from flask import Flask, jsonify, request
from flask_cors import CORS
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
