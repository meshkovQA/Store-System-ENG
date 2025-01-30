# kafka.py
from kafka import KafkaProducer, KafkaConsumer
import json
import time
import threading
import app.logger as logger

CHAT_TOPIC = "chat_notifications"
KAFKA_BROKER = "kafka:9092"


# Настройка продюсера Kafka
def create_kafka_producer():
    """Создает Kafka Producer с обработкой ошибок"""
    while True:
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            logger.log_message("✅ Kafka Producer connected")
            return producer
        except Exception as e:
            logger.log_message(f"Error connecting to Kafka: {e}")
            time.sleep(5)


producer = create_kafka_producer()


def send_chat_notification(chat_id, sender_id, message_content):
    """Отправляет сообщение в Kafka-топик"""
    event = {
        "chat_id": str(chat_id),
        "sender_id": str(sender_id),
        "message": message_content
    }
    try:
        producer.send(CHAT_TOPIC, value=event)
        producer.flush()
    except Exception as e:
        logger.log_message(f"Error sending Kafka notification: {e}")


# Настройка консюмера Kafka
def consume_chat_notifications():
    """Консьюмер для обработки сообщений из Kafka"""
    while True:
        try:
            consumer = KafkaConsumer(
                CHAT_TOPIC,
                bootstrap_servers=[KAFKA_BROKER],
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="chat_service_group",
                value_deserializer=lambda v: json.loads(v.decode("utf-8"))
            )
            logger.log_message("✅ Kafka Consumer connected")

            for message in consumer:
                event = message.value
                chat_id = event["chat_id"]
                sender_id = event["sender_id"]
                content = event["message"]
                logger.log_message(
                    f"Received message in chat {chat_id} from user {sender_id}: {content}")

        except Exception as e:
            logger.log_message(f"Error connecting to Kafka: {e}")
            time.sleep(5)

# Функция для старта Kafka Consumer в отдельном потоке


def start_kafka_consumer():
    consumer_thread = threading.Thread(
        target=consume_chat_notifications, daemon=True)
    consumer_thread.start()
