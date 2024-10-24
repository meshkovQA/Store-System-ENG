import json
from kafka import KafkaConsumer
from app import logger
from uuid import UUID
from fastapi import HTTPException


# Настройка Kafka консьюмера
logger.log_message("Attempting to connect to Kafka")
consumer = KafkaConsumer(
    'auth_topic',  # Топик для чтения сообщений об аутентификации
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)
logger.log_message("Kafka consumer successfully created")


def get_token_and_user_from_kafka():
    try:
        while True:
            # Ожидаем 1 секунду для получения сообщений
            msg_pack = consumer.poll(timeout_ms=1000)
            if not msg_pack:
                logger.log_message("No messages received from Kafka.")
                continue

            for tp, messages in msg_pack.items():
                for message in messages:
                    data = message.value
                    token = data.get('token')
                    user_id_str = data.get('user_id')

                    if token and user_id_str:
                        user_id = UUID(user_id_str)
                        logger.log_message(f"""Token and user_id found in Kafka: {
                                           token}, {user_id}""")
                        return token, user_id
                    else:
                        logger.log_message(
                            "Token or user_id not found in Kafka message.")
                        raise HTTPException(
                            status_code=401, detail="No autorization data in Kafka message")
    except Exception as e:
        logger.log_message(f"Error while getting token from Kafka: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to get token from Kafka"
        )
