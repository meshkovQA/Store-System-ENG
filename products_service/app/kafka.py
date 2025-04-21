import json
from kafka import KafkaProducer
from app import logger


producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode(
        'utf-8')
)


def send_to_kafka(topic: str, message: dict):
    """
    Sends a message to a specified Kafka topic.
    Args:
        topic (str): The Kafka topic to send the message to.
        message (dict): The message to send, which will be serialized to JSON.
    """
    try:
        producer.send(topic, message)
        producer.flush()
        logger.log_message(f"The message sent to {topic}: {message}")
    except Exception as e:
        logger.log_message(
            f"An error occurred while sending the message to Kafka: {e}")
