import json
from kafka import KafkaProducer
from app import logger


# Настройка Kafka продюсера
producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],  # Адрес Kafka сервера
    value_serializer=lambda v: json.dumps(v).encode(
        'utf-8')  # Сериализация данных в JSON
)
# Пример данных для отправки


def send_to_kafka(topic: str, message: dict):
    """
    Отправляет сообщение в указанный топик Kafka.

    :param topic: Название топика Kafka.
    :param message: Сообщение для отправки (словарь).
    """
    try:
        producer.send(topic, message)
        producer.flush()  # Убедимся, что сообщение отправлено
        logger.log_message(f"The message sent to {topic}: {message}")
    except Exception as e:
        logger.log_message(
            f"An error occurred while sending the message to Kafka: {e}")
