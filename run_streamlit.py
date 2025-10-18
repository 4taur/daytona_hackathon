import subprocess
import time
from browser_use import Browser

def run_streamlit_app():
    # Start the Streamlit app
    process = subprocess.Popen(["streamlit", "run", "app.py"])
    print("Starting Streamlit app...")
    time.sleep(5)  # Give it a few seconds to start
    return process

def main():
    process = run_streamlit_app()
    
    # Launch browser automation with Browser Use
    with Browser() as browser:
        browser.goto("http://localhost:8501")
        print("Streamlit app opened in browser using Browser Use.")
        browser.screenshot("streamlit_home.png")  # Optional

    # Keep running until manually stopped
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        process.terminate()
        print("Streamlit app closed.")

if __name__ == "__main__":
    main()
