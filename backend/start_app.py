import threading
import time
import subprocess
import uvicorn
import sys
import os

# Essential for PyInstaller
if getattr(sys, 'frozen', False):
    # Change working directory so relative file lookups work inside bundle
    os.chdir(sys._MEIPASS)

def run_backend():
    # Pass reload=False (which is default) since Pyinstaller doesn't support hot reload well
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="warning")

def open_app_window():
    # Attempt to open as a chromeless desktop app using Edge (built-into Windows)
    try:
        subprocess.Popen('start msedge --app="http://127.0.0.1:8000"', shell=True)
    except Exception:
        # Fallback to default browser
        import webbrowser
        webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # Start backend in separate thread
    threading.Thread(target=run_backend, daemon=True).start()

    # Wait for server to boot up
    time.sleep(3)

    # Open UI in desktop app mode
    open_app_window()

    # Keep app alive and running silently in the background
    while True:
        time.sleep(1)
