import json
from kafka import KafkaConsumer
from app import logger
from app.approval_queue import add_product_to_pending

consumer = KafkaConsumer(
    'product_topic',
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)


def listen_for_product_approval_requests():
    """
    Listen for product approval requests from Kafka and add them to the pending queue.
    """
    logger.log_message("Starting to listen for product approval requests...")
    for message in consumer:
        logger.log_message(f"New message received from Kafka topic: {message}")
        product_id = message.value.get('product_id')
        logger.log_message(f"Product ID got from kafka: {product_id}")
        if product_id:
            add_product_to_pending(product_id)
            logger.log_message(
                f"Received product approval request for ID: {product_id}")
        else:
            logger.log_message("Received message without product ID.")
