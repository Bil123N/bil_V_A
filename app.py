from flask import Flask, render_template, jsonify, request
import threading
from speech_loop import speech_loop, stop_speech_loop, start_speech_loop
from speech_loop2 import stop_speech_loop, start_speech_loop
import sys
from io import StringIO

app = Flask(__name__)

# Flag to indicate if the assistant is active
assistant_active = False

class Assistant:
    def __init__(self):
        self.speech_thread = None

    def send_response(self, message):
        return jsonify({"response": message})

    def activate_assistant(self):
        global assistant_active
        if not assistant_active:
            start_speech_loop()  # Start the speech loop
            self.speech_thread = threading.Thread(target=speech_loop)
            self.speech_thread.start()
            assistant_active = True
            print("Assistant Power On.")
            return self.send_response("Assistant Power On.")
        else:
            print("Assistant is already On")
            return self.send_response("Assistant is already On")

    def deactivate_assistant(self):
        global assistant_active
        if assistant_active:
            stop_speech_loop()
            assistant_active = False
            print("Assistant Power is Off.")
            return self.send_response("Assistant Off")
        else:
            print("Assistant is not Off")
            return self.send_response("Assistant is not Off")
  
class StdoutCapture:
    def __init__(self):
        self.buffer = StringIO()

    def write(self, text):
        self.buffer.write(text)

    def flush(self):
        pass

    def clear_output(self):
        self.buffer.truncate(0)  # Clear the buffer
        self.buffer.seek(0)  # Reset the cursor to the beginning

    def get_output(self):
        return self.buffer.getvalue()

# Create an instance of the capture class
stdout_capture = StdoutCapture()

# Redirect stdout to the custom capture object
sys.stdout = stdout_capture

@app.route('/get_output')
def get_output():
    return stdout_capture.get_output().replace('\n', '<br>')

@app.route('/clear_output', methods=['POST'])
def clear_output():
    stdout_capture.clear_output()
    return jsonify({"message": "Output cleared"})

@app.route('/')
def index():
    return render_template('index.html', assistant_active=assistant_active)

@app.route('/activate_assistant', methods=['POST'])
def activate_assistant_route():
    assistant = Assistant()  # Create a new instance for each request
    return assistant.activate_assistant()

@app.route('/deactivate_assistant', methods=['POST'])
def deactivate_assistant_route():
    assistant = Assistant()  # Create a new instance for each request
    return assistant.deactivate_assistant()
