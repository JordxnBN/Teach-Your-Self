import os
import threading
import time

import webview
import uvicorn

from app.server import app

HOST = "127.0.0.1"
PORT = 8799
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 820
ICON_PATH = os.path.join(os.path.dirname(__file__), "assets", "certiv-icon.ico")

def run_server():
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")

if __name__ == "__main__":
    t = threading.Thread(target=run_server, daemon=True)
    t.start()
    time.sleep(0.8)
    window = webview.create_window(
        "Cert IV Coach (Offline)",
        f"http://{HOST}:{PORT}",
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        min_size=(900, 640),
        resizable=True,
        background_color="#030711",
        text_select=True,
    )
    # icon supported on GTK/QT; on Windows the exe icon is set via PyInstaller
    try:
        webview.start(icon=ICON_PATH)
    except (TypeError, Exception):
        webview.start()
