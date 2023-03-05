import os
import subprocess
import requests
import json
import time
import cv2
from config import DIR
from config import WEBHOOK_URL

webhook_url = WEBHOOK_URL

# Replace this with the path to the directory you want to monitor
dir_path = DIR

debounce_delay = 10

last_access_times = {}

process1 = subprocess.Popen(["inotifywait", "-m", "-r", "-e", "access", dir_path], stdout=subprocess.PIPE)


for line in process1.stdout:
    parts = line.decode("utf-8").strip().split(" ")
    file_path = os.path.join(parts[0], parts[1])

    # Get the current time
    current_time = time.time()

    last_access_time = last_access_times.get(file_path, 0)
    if current_time - last_access_time >= debounce_delay:
        # Initialize the camera
        camera = cv2.VideoCapture(0)

        ret, frame = camera.read()
        if not ret:
            print("Failed to capture image from camera")
            camera.release()
            continue

        image_file = "/tmp/accessed.jpg"
        cv2.imwrite(image_file, frame)

        with open(image_file, "rb") as f:
            payload = {"content": "The file {} was accessed by someone!".format(file_path)}
            files = {"file": f}
            response = requests.post(webhook_url, data=payload, files=files)
            if response.status_code != 200:
                print("Failed to send message to Discord webhook: {}".format(response.text))

        camera.release()

        last_access_times[file_path] = current_time


