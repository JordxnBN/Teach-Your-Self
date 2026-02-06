import threading
import time
import webview
import uvicorn

from app.server import app

HOST = "127.0.0.1"
PORT = 8799

def run_server():
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(0.8)
    webview.create_window("Cert IV Coach (Offline)", f"http://{HOST}:{PORT}")
    webview.start()
