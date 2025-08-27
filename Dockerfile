FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВСЕ файлы включая папку app
COPY . .

# Правильная команда запуска - указываем полный путь
CMD ["python", "app/main.py"]