# Use an official Python runtime as a parent image
FROM python:3.10-bullseye

# Put the application code in /app
WORKDIR /app

# Copy requirements.txt first to leverage Docker cache
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Open port 8000 for the application
EXPOSE 8000

# CMD to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]