# Deployment to Render

## Quick Deploy

1. Push code to GitHub
2. Go to [render.com](https://render.com)
3. New → Background Worker
4. Connect GitHub repo
5. Add environment variable: `TELEGRAM_BOT_TOKEN`
6. Deploy

The bot will build the dictionary automatically during deployment (takes ~3 minutes).

## Configuration

Render will use `render.yaml` for automatic configuration.

Build command: `pip install -r requirements.txt && python scripts/download_saldo.py && python scripts/saldo_parser.py`

Start command: `python main.py`

## Notes

- Free tier sleeps after 15 min inactivity
- Bot wakes instantly when user sends message
- Dictionary rebuilds on each deploy
