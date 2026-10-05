# SMMTestBot

Telegram SMM-бот на aiogram 3.

## Запуск в Docker

```bash
cp .env.example .env   # заполнить TOKEN и остальное
docker compose up -d --build
docker compose logs -f
```

База SQLite хранится в `./data/database.db` (volume). Чтобы перенести старую базу: `mkdir -p data && cp database.db data/`.

- `BOT_URL` пустой — бот работает через polling.
- `BOT_URL=https://домен` — вебхуки (`/webhook/main`, `/webhook/bot/{token}`), порт `8001`; нужен reverse-proxy с HTTPS (nginx/caddy).
- Админ — `ADMIN_ID` (по умолчанию `8270329416`), при первом запуске ему создаётся баланс `ADMIN_DEFAULT_BALANCE` (5 000 000 руб.).

## Локально

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r req.txt
python main.py
```
