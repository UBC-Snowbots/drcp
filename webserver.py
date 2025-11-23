from flask import Flask, request, jsonify
import serial
import time

SERIAL_PORT = '/dev/pts/8'
BAUD_RATE = 9600
PORT = 5001

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)

app = Flask(__name__)

def wait_for_response(timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        if ser.in_waiting > 0:
            return ser.readline().decode(errors='replace').strip()
        time.sleep(0.1)
    return None

@app.route('/send', methods=['POST'])
def send_serial():
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({'status': 'error', 'message': 'Missing command'}), 400

    command = data['command']
    try:
        ser.write((command + '\n').encode())
        response = wait_for_response(timeout=60)

        if response:
            return jsonify({'status': 'ok', 'sent': command, 'feedback': response})
        else:
            return jsonify({'status': 'timeout', 'message': 'No response within 60 seconds'}), 504

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def index():
    return 'Serial Command Server. POST to /send with {"command": "your text"}'

if __name__ == '__main__':
    print(f"Listening on http://localhost:{PORT} and sending to serial port {SERIAL_PORT}")
    app.run(host='0.0.0.0', port=PORT)