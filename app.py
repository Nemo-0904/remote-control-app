
from gevent import monkey
monkey.patch_all() # This should be at the very top, before other imports that might be patched

from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import base64
import time
import os

# Initialize Flask app
# When app.py is inside the folder containing the HTML/CSS/JS,
# Flask's root_path will automatically be set to that folder.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SecretKeyForSocketIO'

# Explicitly set async_mode to 'gevent' as we are using gevent for monkey patching
socketio = SocketIO(app, async_mode='gevent')

# --- Character State ---
character_x = 135
character_y = 135
GRID_SIZE = 30
GAME_AREA_DIM = 300
CHAR_DIM = 30
MAX_POS = GAME_AREA_DIM - CHAR_DIM

# --- Camera State ---
camera_active = False
authenticated_for_camera = False

# --- Authentication Credentials (for camera) ---
AUTH_USERNAME = "admin"
AUTH_PASSWORD = "password123"

# --- Routes ---

# Route for the control panel HTML file
@app.route('/')
def control_panel():
    # 'controller_panel.html' is in the same directory as app.py
    return send_from_directory('.', '# --- IMPORTANT: Using gevent instead of eventlet due to previous issues ---
from gevent import monkey
monkey.patch_all() # This should be at the very top, before other imports that might be patched

from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import base64
import time
import os

# Initialize Flask app
# When app.py is inside the folder containing the HTML/CSS/JS,
# Flask's root_path will automatically be set to that folder.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SecretKeyForSocketIO'

# Explicitly set async_mode to 'gevent' as we are using gevent for monkey patching
socketio = SocketIO(app, async_mode='gevent')

# --- Character State ---
character_x = 135
character_y = 135
GRID_SIZE = 30
GAME_AREA_DIM = 300
CHAR_DIM = 30
MAX_POS = GAME_AREA_DIM - CHAR_DIM

# --- Camera State ---
camera_active = False
authenticated_for_camera = False

# --- Authentication Credentials (for camera) ---
AUTH_USERNAME = "admin"
AUTH_PASSWORD = "password123"

# --- Routes ---

# Route for the control panel HTML file
@app.route('/')
def control_panel():
    # 'controller_panel.html' is in the same directory as app.py
    return send_from_directory('.', 'controller_panel.html')

# Route for the mobile device HTML file
@app.route('/mobile')
def mobile_device():
    # 'mobile_device.html' is in the same directory as app.py
    return send_from_directory('.', 'mobile_device.html')

# Route for serving CSS and other files from the same directory
@app.route('/<path:filename>')
def serve_public_files(filename):
    # This will catch requests for 'controller.css', 'device.css', etc.
    # as they are now directly in the current directory.
    if filename.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico')):
        return send_from_directory('.', filename)
    return "File not found", 404

@app.route('/login', methods=['POST'])
def login():
    global authenticated_for_camera
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == AUTH_USERNAME and password == AUTH_PASSWORD:
        authenticated_for_camera = True
        print(f"User '{username}' successfully authenticated for camera access.")
        return jsonify({'success': True})
    authenticated_for_camera = False
    print(f"Login failed for user '{username}'.")
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/toggle_camera', methods=['POST'])
def toggle_camera_route():
    global camera_active, authenticated_for_camera
    action = request.json.get('action')

    if action == 'start':
        if authenticated_for_camera:
            camera_active = True
            socketio.emit('start_camera_stream')
            print("Server requested mobile to start camera stream.")
            return jsonify({'status': 'camera_expected_from_mobile', 'active': True})
        else:
            return jsonify({'status': 'unauthorized', 'error': 'Not authenticated for camera access'}), 401
    elif action == 'stop':
        camera_active = False
        authenticated_for_camera = False
        socketio.emit('stop_camera_stream')
        print("Server requested mobile to stop camera stream.")
        return jsonify({'status': 'camera_stopped', 'active': False})
    return jsonify({'error': 'Invalid action'}), 400

# --- Socket.IO Event Handlers ---
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('character_position_update', {'x': character_x, 'y': character_y})
    if camera_active and authenticated_for_camera:
        emit('start_camera_stream')

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('move_command')
def handle_move_command(data):
    global character_x, character_y
    direction = data.get('direction')

    if direction == 'up':
        character_y = max(0, character_y - GRID_SIZE)
    elif direction == 'down':
        character_y = min(MAX_POS, character_y + GRID_SIZE)
    elif direction == 'left':
        character_x = max(0, character_x - GRID_SIZE)
    elif direction == 'right':
        character_x = min(MAX_POS, character_x + GRID_SIZE)
    else:
        print(f"Unknown direction received: {direction}")
        return

    emit('character_position_update', {'x': character_x, 'y': character_y}, broadcast=True)
    print(f"Character moved to X:{character_x}, Y:{character_y} via '{direction}' command.")

@socketio.on('mobile_camera_frame')
def handle_mobile_camera_frame(data):
    if camera_active and authenticated_for_camera:
        emit('camera_frame', {'frame': data['frame']}, broadcast=True, include_self=False)

if __name__ == '__main__':
    print("Attempting to run SocketIO server...")
    # Using port 5000 as that was the last port we tried.
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    print("SocketIO server run command finished.")')

# Route for the mobile device HTML file
@app.route('/mobile')
def mobile_device():
    # 'mobile_device.html' is in the same directory as app.py
    return send_from_directory('.', 'mobile_device.html')

# Route for serving CSS and other files from the same directory
@app.route('/<path:filename>')
def serve_public_files(filename):
    # This will catch requests for 'controller.css', 'device.css', etc.
    # as they are now directly in the current directory.
    if filename.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico')):
        return send_from_directory('.', filename)
    return "File not found", 404

@app.route('/login', methods=['POST'])
def login():
    global authenticated_for_camera
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == AUTH_USERNAME and password == AUTH_PASSWORD:
        authenticated_for_camera = True
        print(f"User '{username}' successfully authenticated for camera access.")
        return jsonify({'success': True})
    authenticated_for_camera = False
    print(f"Login failed for user '{username}'.")
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/toggle_camera', methods=['POST'])
def toggle_camera_route():
    global camera_active, authenticated_for_camera
    action = request.json.get('action')

    if action == 'start':
        if authenticated_for_camera:
            camera_active = True
            socketio.emit('start_camera_stream')
            print("Server requested mobile to start camera stream.")
            return jsonify({'status': 'camera_expected_from_mobile', 'active': True})
        else:
            return jsonify({'status': 'unauthorized', 'error': 'Not authenticated for camera access'}), 401
    elif action == 'stop':
        camera_active = False
        authenticated_for_camera = False
        socketio.emit('stop_camera_stream')
        print("Server requested mobile to stop camera stream.")
        return jsonify({'status': 'camera_stopped', 'active': False})
    return jsonify({'error': 'Invalid action'}), 400

# --- Socket.IO Event Handlers ---
@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")
    emit('character_position_update', {'x': character_x, 'y': character_y})
    if camera_active and authenticated_for_camera:
        emit('start_camera_stream')

@socketio.on('disconnect')
def handle_disconnect():
    print(f"Client disconnected: {request.sid}")

@socketio.on('move_command')
def handle_move_command(data):
    global character_x, character_y
    direction = data.get('direction')

    if direction == 'up':
        character_y = max(0, character_y - GRID_SIZE)
    elif direction == 'down':
        character_y = min(MAX_POS, character_y + GRID_SIZE)
    elif direction == 'left':
        character_x = max(0, character_x - GRID_SIZE)
    elif direction == 'right':
        character_x = min(MAX_POS, character_x + GRID_SIZE)
    else:
        print(f"Unknown direction received: {direction}")
        return

    emit('character_position_update', {'x': character_x, 'y': character_y}, broadcast=True)
    print(f"Character moved to X:{character_x}, Y:{character_y} via '{direction}' command.")

@socketio.on('mobile_camera_frame')
def handle_mobile_camera_frame(data):
    if camera_active and authenticated_for_camera:
        emit('camera_frame', {'frame': data['frame']}, broadcast=True, include_self=False)

if __name__ == '__main__':
    print("Attempting to run SocketIO server...")
    # Using port 5000 as that was the last port we tried.
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    print("SocketIO server run command finished.")
