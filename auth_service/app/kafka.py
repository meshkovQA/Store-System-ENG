# auth_kafka.py
import json
from kafka import KafkaProducer
from app import logger  # Импортируем логгер

# Настройка Kafka продюсера
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],  # Адрес Kafka сервера
    value_serializer=lambda v: json.dumps(v).encode(
        'utf-8')  # Сериализация данных в JSON
)
# Пример данных для отправки


def create_auth_topic_kafka(access_token: str, user_email: str, user_id: str, action: str, topic: str = 'auth_topic'):
    # Формируем сообщение для отправки в Kafka
    message = {
        "token": access_token,  # Передаем токен, который был создан в роуте
        "user_id": user_id,
        "action": action,
        "description": "User action for Kafka"
    }

    # Логируем создание и отправку сообщения
    logger.log_message(f"""Sending message to Kafka: Action: {
                       action}, User: {user_email}, User ID: {user_id}""")

    # Отправляем сообщение в топик Kafka
    producer.send(topic, message)

    producer.flush()
    logger.log_message("Message sent to Kafka")
