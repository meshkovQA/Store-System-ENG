# Используем базовый образ Python 3.10-bullseye
FROM python:3.10-bullseye

# Указываем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем requirements.txt и устанавливаем зависимости
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код в контейнер
COPY . .

# Открываем порт для доступа
EXPOSE 8000

# Команда для запуска приложения (FastAPI в этом примере)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]