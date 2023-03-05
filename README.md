# dirmon-discord-notifier
## (linux only - only tested on Manjaro)

This is a simple script that monitors a directory. When the directory is being accessed, it will take a picture using the webcam and send it to a Discord channel using a webhook.

## Requirements

- Python 3
- inotify (Linux only)

## Usage

1. Create a webhook in your Discord channel
2. Make sure the directory you want to monitor is inside the config.py file
3. Run the script using `python3 dirmon.py`

