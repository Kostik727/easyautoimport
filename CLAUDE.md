# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Описание проекта

Telegram-бот для мониторинга автоаукциона Copart.com. Находит подходящие лоты (по маркам, году, состоянию), скачивает фото и публикует в Telegram-канал @easyautoimport. Пользователи могут сохранять понравившиеся лоты через инлайн-кнопки. Также есть маркетинговый лендинг (index.html).

## Команды

```bash
# Запуск скрапера (разовый прогон — ищет лоты и публикует в канал)
python copart_bot.py

# Запуск polling-бота (непрерывный сервис — обрабатывает команды пользователей + скрапер каждые 3 часа в фоне)
python polling_bot.py

# Установка зависимостей
pip install -r requirements.txt
# Важно: beautifulsoup4 нужен, но не указан в requirements.txt (ставится отдельно в CI)
```

## Архитектура

- **copart_bot.py** — скрапер Copart. Ищет лоты через API, фильтрует по маркам (`PRIORITY_MAKES`), году (≥2018), состоянию ("run and drive"). Скачивает фото, формирует сообщение с деталями (цена, повреждения, пробег, двигатель, VIN) и публикует в Telegram-канал. Отслеживает уже опубликованные лоты в `seen_lots.json`.
- **polling_bot.py** — Telegram-бот (long polling). Обрабатывает команды `/start`, `/saved`, `/help` и callback "❤️ Save". Запускает скрапер в фоновом потоке. Хранит сохранённые лоты пользователей в `saved_lots.json`.
- **index.html + script.js + style.css** — маркетинговый лендинг (статика, на русском языке).

## Деплой

- **Heroku**: `Procfile` запускает `polling_bot.py` как worker
- **GitHub Actions**: `.github/workflows/bot.yml` — запуск `copart_bot.py` ежедневно в 6:00 UTC

## Переменные окружения

- `BOT_TOKEN` — токен Telegram-бота (секрет в GitHub Actions, есть hardcoded fallback в коде)

## Хранилище данных (runtime, JSON-файлы)

- `seen_lots.json` — множество ID уже опубликованных лотов (создаётся автоматически)
- `saved_lots.json` — словарь {user_id: [lot_ids]} сохранённых лотов

## Git Workflow

- Always develop and commit directly on the `master` branch
- Never create feature branches
- Always push to `master`
