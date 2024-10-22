import json
from kafka import KafkaProducer
from auth import create_access_token
from auth import logger  # Импортируем логгер

# Настройка Kafka продюсера
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],  # Адрес Kafka сервера
    value_serializer=lambda v: json.dumps(v).encode(
        'utf-8')  # Сериализация данных в JSON
)
# Пример данных для отправки


def send_message_to_kafka(user_email: str, action: str):
    # Генерируем токен с данными пользователя
    token_data = {
        "user_id": "123e4567-e89b-12d3-a456-426614174000",  # Пример ID пользователя
        "email": user_email,
        "sub": user_email  # subject (субъект токена)
    }

    # Создаем access_token
    token = create_access_token(token_data)

    # Формируем сообщение для отправки в Kafka
    message = {
        "token": token,
        # Пример действия (создание продукта, удаление и т.д.)
        "action": action,
        "description": "Sample message for Kafka"
    }

    # Логируем создание и отправку сообщения
    logger.log_message(f"""Sending message to Kafka: Action: {
                       action}, User: {user_email}""")

    # Отправляем сообщение в топик Kafka
    producer.send('products_topic', message)
    producer.flush()


# Пример использования отправки сообщения
send_message_to_kafka("admin@example.com", "create_product")
