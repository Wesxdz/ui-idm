from pynput import keyboard, mouse
from datetime import datetime
import obsws_python as obs
from multiprocessing import Event
import subprocess
import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

recorded_video_file = None

class MyHandler(FileSystemEventHandler):
    def on_created(self, event):
        global recorded_video_file
        filename, file_extension = os.path.splitext(event.src_path)
        if file_extension.lower() in ['.mkv', '.mp4', '.flv', '.mov']:  # add or remove video file types
            print(f'New video file {event.src_path} has been created.')
            # Here we call the postprocess.py script with the path of the newly created video file
            recorded_video_file = event.src_path
            observer.stop()  # Stop the observer

observer = Observer()
event_handler = MyHandler()

LOGFILE = "log.txt"

# pass conn info if not in config.toml
cl = obs.ReqClient(host='localhost', port=4455, password='mystrongpass')

stop_listener = Event()

def on_move(x, y):
    with open(LOGFILE, "a") as f:
        f.write(f'{datetime.now()} - Mouse moved to {(x, y)}\n')

def on_click(x, y, button, pressed):
    with open(LOGFILE, "a") as f:
        f.write(f'{datetime.now()} - Mouse {"Pressed" if pressed else "Released"} {button} at {(x, y)}\n')
    if not pressed:
        # Stop listener
        stop_listener.set()

def on_press(key):
    with open(LOGFILE, "a") as f:
        f.write(f'{datetime.now()} - Key pressed: {key}\n')

def on_release(key):
    with open(LOGFILE, "a") as f:
        f.write(f'{datetime.now()} - Key released: {key}\n')


stop_listener = Event()
observers = []  # List to store the observer subprocesses

def main_loop():
    if os.path.isfile(LOGFILE):
        os.remove(LOGFILE)
    try:
        while not stop_listener.is_set():
            # End all previous observer processes
            for proc in observers:
                proc.terminate()
            observers.clear()

            record_dir = cl.get_record_directory().record_directory
            # Observer detects first file created in OBS output directory (hopefully the video)
            observer.schedule(event_handler, path=record_dir, recursive=False)
            observer.start()

            cl.start_record()
            with open(LOGFILE, "a") as f:
                f.write(f'{datetime.now()} - Start Recording\n')
            # Collect events until released
            with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
                with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                    listener.join()
    except KeyboardInterrupt:
        observer.join()
        cl.stop_record()
        # Call the postprocess function with the recorded video file path
        print(recorded_video_file)
        if recorded_video_file:
            subprocess.call(["python", "postprocess.py", recorded_video_file])


main_loop()
