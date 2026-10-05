"""Flask bridge: browser UI  <->  USB serial  <->  your board.

Run:  pip install -r requirements.txt
      python app.py
Open: http://localhost:5000
"""
import os
import threading

import serial
import serial.tools.list_ports
from flask import Flask, jsonify, request, send_file

BAUD = 38400
app = Flask(__name__)

board = None                 # the open serial.Serial, or None
lock = threading.Lock()      # one command at a time on the wire


def send(cmd: str) -> str:
    """Send one line to the board and return its one-line reply."""
    if board is None or not board.is_open:
        raise RuntimeError("Board not connected")
    with lock:
        board.reset_input_buffer()
        board.write((cmd + "\n").encode())
        return board.readline().decode(errors="ignore").strip()


BASE = os.path.dirname(os.path.abspath(__file__))


@app.get("/")
def index():
    # Works whether index.html is in a "templates" folder or next to app.py
    for folder in (os.path.join(BASE, "templates"), BASE):
        path = os.path.join(folder, "index.html")
        if os.path.exists(path):
            return send_file(path, max_age=0)
    return "index.html not found. Put it next to app.py.", 500


@app.get("/api/ports")
def ports():
    return jsonify([{"device": p.device, "label": p.description}
                    for p in serial.tools.list_ports.comports()])


@app.post("/api/connect")
def connect():
    global board
    port = request.json.get("port")
    try:
        if board and board.is_open:
            board.close()
        board = serial.Serial(port, BAUD, timeout=1)
        board.reset_input_buffer()
        return jsonify(ok=True, port=port)
    except Exception as e:
        board = None
        return jsonify(ok=False, error=str(e)), 400


@app.post("/api/disconnect")
def disconnect():
    global board
    if board and board.is_open:
        board.close()
    board = None
    return jsonify(ok=True)


@app.get("/api/status")
def status():
    return jsonify(connected=bool(board and board.is_open),
                   port=board.port if board else None)


@app.post("/api/command")
def command():
    """Body: {"cmd": "LED 1"} -> {"ok": true, "reply": "OK"}"""
    cmd = (request.json.get("cmd") or "").strip()
    if not cmd:
        return jsonify(ok=False, error="Empty command"), 400
    try:
        return jsonify(ok=True, reply=send(cmd))
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 400


if __name__ == "__main__":
    found = [p.device for p in serial.tools.list_ports.comports()]
    print("Serial ports found:", found or "none")
    app.run(host="0.0.0.0", port=5000, debug=False)