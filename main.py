import random
from fastapi import FastAPI, Request, Response
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
)
from config import TOKEN, APP_URL, OWNER_NAME, OWNER_ID

app = FastAPI()
application = Application.builder().token(TOKEN).build()
votes = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🤖 *ChatBot Online!*\n\n"
        "💬 Send any message, I'll reply like a chatbot.\n"
        "👍 React using Like/Dislike buttons.\n"
        f"👑 Owner: {OWNER_NAME}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = f"👑 Bot Owner: {OWNER_NAME}"
    if OWNER_ID:
        msg += f"\n🆔 Owner ID: `{OWNER_ID}`"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg or msg.from_user.is_bot:
        return

    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("👍", callback_data=f"like_{msg.message_id}"),
        InlineKeyboardButton("👎", callback_data=f"dislike_{msg.message_id}")
    ]])
    votes[msg.message_id] = {"like": 0, "dislike": 0}
    await msg.reply_text("React to this message:", reply_markup=keyboard)

    text = msg.text.lower()
    replies = {
        "hi": ["Hey!", "Hi there!", "Hello 👋"],
        "hello": ["Hey 👋", "What's up?", "Yo!"],
        "how are you": ["I'm great, thanks! You?", "All good 😎", "Doing awesome!"],
        "love you": ["Love you too ❤️", "Awww 😳", "Same here 💖"],
        "bye": ["Goodbye 👋", "See you later!", "Take care!"],
        "thanks": ["You're welcome!", "No problem!", "Anytime 😊"]
    }
    reply = None
    for key, opts in replies.items():
        if key in text:
            reply = random.choice(opts)
            break
    if not reply:
        reply = random.choice(["Interesting 😄", "Okay 👍", "Nice!", "Hmm 🤔", "Haha good one 😂"])
    await msg.reply_text(reply)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    msg_id = int(query.data.split("_")[1])
    action = query.data.split("_")[0]
    votes.setdefault(msg_id, {"like": 0, "dislike": 0})
    votes[msg_id][action] += 1

    like_count = votes[msg_id]["like"]
    dislike_count = votes[msg_id]["dislike"]
    new_keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(f"👍 {like_count}", callback_data=f"like_{msg_id}"),
        InlineKeyboardButton(f"👎 {dislike_count}", callback_data=f"dislike_{msg_id}")
    ]])
    await query.edit_message_reply_markup(reply_markup=new_keyboard)

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("owner", owner))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
application.add_handler(CallbackQueryHandler(button_click))

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.update_queue.put(update)
    return Response(status_code=200)

@app.on_event("startup")
async def on_startup():
    await application.initialize()
    await application.start()
    await application.bot.set_webhook(f"{APP_URL}/webhook")
    print("🚀 Webhook set to:", f"{APP_URL}/webhook")

@app.on_event("shutdown")
async def on_shutdown():
    await application.bot.delete_webhook()
    await application.stop()
    await application.shutdown()
