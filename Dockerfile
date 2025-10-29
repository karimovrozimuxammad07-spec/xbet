# 1. Используем официальный образ Python
FROM python:3.11

# 2. Устанавливаем рабочую директорию
WORKDIR /app

# 3. Копируем все файлы проекта
COPY . .

# 4. Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# 5. Запускаем бота
CMD ["python", "bot.py"]
