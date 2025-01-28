from datetime import datetime
import io
import os
import signal
import threading
import time

from flask import Flask, jsonify, request, send_file, send_from_directory
from PIL import Image


PID = os.getpid()
app = Flask(__name__)

# Thread-safe screenshot storage
class ScreenshotStore:
    def __init__(self):
        self.lock = threading.Lock()
        self.latest_screenshot = None
        self.latest_timestamp = None
    
    def store_screenshot(self, image_data):
        with self.lock:
            self.latest_screenshot = image_data
            self.latest_timestamp = datetime.now()
    
    def get_screenshot(self):
        with self.lock:
            return {
                'image': self.latest_screenshot,
                'timestamp': self.latest_timestamp
            }
    
    def clear_screenshot(self):
        with self.lock:
            self.latest_screenshot = None
            self.latest_timestamp = None
        
screenshot_store = ScreenshotStore()

@app.route('/')
def health_check():
    return {'status': 'healthy', 'path': os.path.dirname(os.path.realpath(__file__)), 'timestamp': time.time()}

@app.route('/getConfig')
def get_config():
    return send_from_directory('./', 'config.json')

@app.route('/screenshot', methods=['POST'])
def receive_screenshot():
    """Endpoint to receive screenshots in WEBP format"""
    if 'image/webp' not in request.content_type:
        return jsonify({'error': 'Invalid content type, expected image/webp'}), 400
    
    try:
        # Read the image data
        image_data = request.get_data()
        
        # Verify it's a valid WebP image
        img = Image.open(io.BytesIO(image_data))
        if img.format != 'WEBP':
            return jsonify({'error': 'Invalid image format, expected WebP'}), 400
        
        # Store the screenshot
        screenshot_store.store_screenshot(image_data)
        
        return jsonify({
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/getLatestScreenshot', methods=['GET'])
def get_latest_screenshot():
    """Endpoint to retrieve the latest screenshot"""
    screenshot_data = screenshot_store.get_screenshot()
    
    if screenshot_data['image'] is None:
        return jsonify({'error': 'No screenshot available'}), 404

    # Create an in-memory file-like object
    image_io = io.BytesIO(screenshot_data['image'])
    image_io.seek(0)
    
    # Send the file with proper mimetype
    return send_file(
        image_io,
        mimetype='image/webp',
        as_attachment=False,
        download_name=f'screenshot_{screenshot_data["timestamp"].strftime("%Y%m%d_%H%M%S")}.webp'
    )
    
    # return {
    #     'image': screenshot_data['image'],
    #     'timestamp': screenshot_data['timestamp'].isoformat()
    # }

@app.route('/clearScreenshot')
def clear_screenshot():
    screenshot_store.clear_screenshot()
    return "OK"

@app.route('/viewer')
def viewer():
    return send_from_directory('./', 'index.html')

@app.route('/shutdown')
def shutdown():
    # this mimics a CTRL+C hit by sending SIGINT
    # it ends the app run, but not the main thread
    pid = os.getpid()
    assert pid == PID
    os.kill(pid, signal.SIGINT)
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
