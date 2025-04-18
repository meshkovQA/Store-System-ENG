# logger.py
import logging
import os
import json
from datetime import datetime
import socket

# Create directory for logs if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Создаем логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler
handler = logging.FileHandler('logs/app.log')
handler.setLevel(logging.INFO)

# Get IP address


def get_ip_address():
    try:
        hostname = socket.gethostname()  # Get the hostname
        ip_address = socket.gethostbyname(hostname)  # Get the IP address
        return ip_address
    except Exception as e:
        return str(e)

# Create a custom formatter


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "name": record.name,
            "class": record.levelname,  # use level name as class
            # use level number as state
            "state": record.levelno,
            # timestamp in milliseconds
            "timestamp": int(datetime.utcnow().timestamp() * 1000),
            "message": record.getMessage(),  # add message
            "ip_address": get_ip_address()  # add IP address
        }
        return json.dumps(log_entry)


formatter = JsonFormatter()
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)


def log_message(message: str):
    logger.info(message)
