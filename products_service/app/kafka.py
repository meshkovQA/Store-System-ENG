import json
from kafka import KafkaConsumer
from app import logger
from uuid import UUID
from fastapi import HTTPException
from kafka.errors import KafkaError


# Настройка Kafka консьюмера
logger.log_message("Attempting to connect to Kafka")
consumer = KafkaConsumer(
    'auth_topic',  # Топик для чтения сообщений об аутентификации
    bootstrap_servers=['kafka:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True
)
logger.log_message("Kafka consumer successfully created")


async def get_token_and_user_from_kafka():
    try:
        # Устанавливаем таймаут ожидания сообщений
        timeout_ms = 5000  # 5 секунд

        # Ожидаем одно сообщение
        msg_pack = consumer.poll(timeout_ms=timeout_ms)

        # Если сообщения не пришли, закрываем запрос
        if not msg_pack:
            logger.log_message(
                "No messages received from Kafka within timeout.")
            raise HTTPException(
                status_code=404, detail="No messages in Kafka topic.")

        # Обрабатываем только одно сообщение
        for tp, messages in msg_pack.items():
            if messages:
                message = messages[0]
                # Логируем сообщение для отладки
                logger.log_message(f"Received message: {message.value}")

                data = message.value

                # Извлекаем token и user_id
                token = data.get('token')
                user_id = data.get('user_id')

                # Логируем полученные значения
                logger.log_message(f"Extracted token from Kafka: {token}")
                logger.log_message(f"Extracted user_id from Kafka: {user_id}")

                # Проверяем, что token и user_id являются строками
                if not isinstance(token, str):
                    token = str(token)

                if not isinstance(user_id, str):
                    user_id = str(user_id)

                # Возвращаем полученное сообщение
                return token, user_id

        # Если не было сообщений
        raise HTTPException(status_code=404, detail="No valid messages found.")

    except KafkaError as e:
        logger.log_message(f"Error consuming message from Kafka: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to consume message from Kafka.")
