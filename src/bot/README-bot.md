# Telegram Bot для V2Ray Auto Scanner

Опциональный модуль для автоматического получения конфигов через Telegram.

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install python-telegram-bot python-dotenv
```

### 2. Настройка

1. Скопируй `.env.example` в `.env`:
```bash
cp src/bot/.env.example src/bot/.env
```

2. Отредактируй `.env`:
- `BOT_TOKEN` — токен бота от @BotFather
- `CHAT_ID` — твой ID в Telegram (можно получить через @userinfobot)

### 3. Запуск

```bash
python src/bot/bot.py
```

## Команды бота

- `/start` — приветственное сообщение
- `/scan` — запустить сканер и получить новые конфиги
- `/last` — получить последние сохранённые конфиги

## Требования

- Python 3.10+
- Telegram бот с токеном
- Скомпилированный `v2ray_auto_scanner.exe` в корне проекта
