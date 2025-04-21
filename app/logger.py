# logger.py
import logging
import os
import json
from datetime import datetime
import socket


os.makedirs('logs', exist_ok=True)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


handler = logging.FileHandler('logs/app.log')
handler.setLevel(logging.INFO)


def get_ip_address():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        return str(e)

# Создаем форматтер и добавляем его в обработчик


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "name": record.name,
            "class": record.levelname,
            "state": record.levelno,
            "timestamp": int(datetime.utcnow().timestamp() * 1000),
            "message": record.getMessage(),
            "ip_address": get_ip_address()
        }
        return json.dumps(log_entry)


formatter = JsonFormatter()
handler.setFormatter(formatter)

logger.addHandler(handler)


def log_message(message: str):
    logger.info(message)
