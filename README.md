# Telegram ChatBot + Like/Dislike + Owner Info

A Telegram bot that reacts to messages and chats smartly.

## 🚀 Deploy on Render
1. Fork repo to GitHub.
2. Create new *Web Service* on Render.
3. Add Environment Variables:
   - TOKEN = your_bot_token
   - APP_URL = https://your-app.onrender.com
   - OWNER_NAME = your_name
   - OWNER_ID = your_telegram_numeric_id
4. Start Command:
   ```
   gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
   ```
