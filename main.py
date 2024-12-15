from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import logging
from logging.handlers import RotatingFileHandler
import socket
import json

# Logging-Konfiguration
log_file_path = '/var/log/mappedplayer/server.log'
logging.basicConfig(handlers=[RotatingFileHandler(log_file_path, maxBytes=10000, backupCount=5)],
                    level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Flask-App erstellen
app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/media')
def media():
    return render_template('media.html')

@app.route('/setup')
def setup():
    return render_template('setup.html')

# Path to the config.json file
CONFIG_FILE = 'config.json'
config_content = -1

def load_config():
    global config_content
    """Load the configuration from the config.json file."""
    try:
        if config_content == -1:
            with open(CONFIG_FILE, 'r') as file:
                config_content = json.load(file)
                return config_content
        else:
            return config_content
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_config(config):
    global config_content
    """Save the configuration to the config.json file."""
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config, file, indent=4)
    config_content = config
    notify_display(config)

@app.route('/setup/config', methods=['GET'])
def get_config():
    """Provide the configuration as a JSON response."""
    config = load_config()
    return jsonify(config)

@app.route('/setup/config', methods=['POST'])
def update_config():
    """Update the configuration and save it to config.json."""
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    # Load the current configuration
    config = load_config()

    # Update the configuration with the new data
    config.update(data)

    # Save the updated configuration
    save_config(config)

    return jsonify({'status': 'success', 'message': 'Configuration updated successfully'})

@app.route('/setup/displays', methods=['POST'])
def update_displays():
    """Update display configurations including positions and polygons."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        # Load the current configuration
        config = load_config()

        # Ensure displays key exists
        if 'displays' not in config:
            config['displays'] = []

        # Update displays configuration
        config['displays'] = data.get('displays', [])

        # Save the updated configuration
        save_config(config)

        return jsonify({'status': 'success', 'message': 'Displays updated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def notify_display(config):
    display_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('localhost', 6000))  # Die Adresse und Portnummer muss mit display.py übereinstimmen
        client_socket.send(json.dumps(config).encode())
    finally:
        client_socket.close()

def read_log():
    log_entries = []
    with open(log_file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(' ', 1)
            if len(parts) == 2:
                log_entries.append({'timestamp': parts[0], 'message': parts[1]})
    return log_entries

@socketio.on('request_log')
def handle_request_log():
    log_contents = read_log()
    socketio.emit('update_log', log_contents)

@socketio.on('mouse_move')
def handle_mouse_move(data):
    config = load_config()
    config["mouse_x"] = data['x']
    config["mouse_y"] = data['y']
    notify_display(config)

if __name__ == '__main__':
    logging.info("mappedplayer server started.")
    # Flask-SocketIO Server starten
    socketio.run(app, host='0.0.0.0', port=5000)
