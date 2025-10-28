# 1. Используем официальный образ Python
FROM python:3.11

# 2. Устанавливаем рабочую директорию
WORKDIR /app

# 3. Копируем все файлы проекта внутрь контейнера
COPY . .

# 4. Устанавливаем зависимости, если есть requirements.txt
RUN pip install --no-cache-dir -r requirements.txt || true

# 5. Указываем команду для запуска бота
CMD ["python", "bot.py"]
