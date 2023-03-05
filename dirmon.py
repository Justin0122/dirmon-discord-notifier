import os
import subprocess
import json
import time
import cv2
from config import DIR
from config import WEBHOOK_URL

if subprocess.call(["which", "inotifywait"], stdout=subprocess.PIPE) != 0:
    print("Installing inotify-tools...")
    subprocess.call(["sudo", "pacman", "-S", "inotify-tools"])

try:
    import requests
except ImportError:
    print("Installing requests...")
    subprocess.call(["pip3", "install", "requests"])


webhook_url = WEBHOOK_URL

dir_path = DIR

debounce_delay = 10

last_access_times = {}

process1 = subprocess.Popen(["inotifywait", "-m", "-r", "-e", "access", dir_path], stdout=subprocess.PIPE)


for line in process1.stdout:
    parts = line.decode("utf-8").strip().split(" ")
    file_path = os.path.join(parts[0], parts[1])

    if "SSH_CLIENT" in os.environ:
        ip_address = os.environ["SSH_CLIENT"].split()[0]
        message = "The file {} was accessed by someone over SSH from IP address {}!".format(file_path, ip_address)
    else:
        message = "The file {} was accessed by someone locally!".format(file_path)

    current_time = time.time()

    last_access_time = last_access_times.get(file_path, 0)
    if current_time - last_access_time >= debounce_delay:
        camera = cv2.VideoCapture(0)

        ret, frame = camera.read()
        if not ret:
            print("Failed to capture image from camera")
            camera.release()
            continue

        image_file = "/tmp/accessed.jpg"
        cv2.imwrite(image_file, frame)

        with open(image_file, "rb") as f:
            payload = {"content": message}
            files = {"file": f}
            response = requests.post(webhook_url, data=payload, files=files)
            if response.status_code != 200:
                print("Failed to send message to Discord webhook: {}".format(response.text))

        camera.release()

        last_access_times[file_path] = current_time
