# 1. Используем официальный образ Python
FROM python:3.11

# 2. Устанавливаем рабочую директорию
WORKDIR /app

# 3. Копируем все файлы проекта
COPY . .

# 4. Устанавливаем зависимости (если файл есть)
RUN pip install --no-cache-dir -r requirements.txt || true

# 5. Запускаем бота
CMD ["python", "bot.py"]
