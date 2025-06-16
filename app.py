from gevent import monkey
monkey.patch_all()  # Must be at the top

from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

# --- App Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'SecretKeyForSocketIO'
socketio = SocketIO(app, async_mode='gevent')

# --- Constants ---
GRID_SIZE = 30
GAME_AREA_DIM = 300
CHAR_DIM = 30
MAX_POS = GAME_AREA_DIM - CHAR_DIM

# --- Global State ---
character_x = 135
character_y = 135
camera_active = False
authenticated_for_camera = False

# --- Credentials ---
AUTH_USERNAME = "admin"
AUTH_PASSWORD = "password123"

# --- Routes ---

@app.route('/')
def control_panel():
    return send_from_directory('.', 'controller_panel.html')

@app.route('/mobile')
def mobile_device():
    return send_from_directory('.', 'mobile_device.html')

@app.route('/<path:filename>')
def serve_static_files(filename):
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
        print(f"[LOGIN] Success: {username}")
        return jsonify({'success': True})
    else:
        authenticated_for_camera = False
        print(f"[LOGIN] Failed: {username}")
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/toggle_camera', methods=['POST'])
def toggle_camera():
    global camera_active, authenticated_for_camera
    action = request.json.get('action')

    if action == 'start':
        if authenticated_for_camera:
            camera_active = True
            socketio.emit('start_camera_stream')
            print("[CAMERA] Start requested.")
            return jsonify({'status': 'camera_expected_from_mobile', 'active': True})
        else:
            return jsonify({'status': 'unauthorized', 'error': 'Not authenticated'}), 401

    elif action == 'stop':
        camera_active = False
        authenticated_for_camera = False
        socketio.emit('stop_camera_stream')
        print("[CAMERA] Stop requested.")
        return jsonify({'status': 'camera_stopped', 'active': False})

    return jsonify({'error': 'Invalid action'}), 400

# --- Socket.IO Events ---

@socketio.on('connect')
def on_connect():
    print(f"[SOCKET] Client connected: {request.sid}")
    emit('character_position_update', {'x': character_x, 'y': character_y})
    if camera_active and authenticated_for_camera:
        emit('start_camera_stream')

@socketio.on('disconnect')
def on_disconnect():
    print(f"[SOCKET] Client disconnected: {request.sid}")

@socketio.on('move_command')
def on_move_command(data):
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
        print(f"[MOVE] Invalid direction: {direction}")
        return

    print(f"[MOVE] X:{character_x}, Y:{character_y} via '{direction}'")
    emit('character_position_update', {'x': character_x, 'y': character_y}, broadcast=True)

@socketio.on('mobile_camera_frame')
def on_mobile_camera_frame(data):
    if camera_active and authenticated_for_camera:
        emit('camera_frame', {'frame': data['frame']}, broadcast=True, include_self=False)

# --- Main Entrypoint ---
if __name__ == '__main__':
    print("[SERVER] Starting Flask-SocketIO app...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
