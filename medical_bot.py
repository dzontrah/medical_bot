import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

# In-memory storage (for testing)
appointments = {}
messages = []

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏥 Welcome to MediCare Clinic Bot!\n\n"
        "I can help you:\n"
        "✅ Book appointments (/book)\n"
        "✅ Answer FAQs (/faq)\n"
        "✅ Send messages to the clinic (/contact)\n\n"
        "Type a command to get started!"
    )

# /book command
async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "🗓 Usage: /book <YourName> <DateTime>\nExample: /book JohnDoe 2025-05-10 14:00"
        )
        return

    name = context.args[0]
    datetime = " ".join(context.args[1:])
    user_id = update.message.from_user.id

    appointments[user_id] = {"name": name, "datetime": datetime}
    await update.message.reply_text(
        f"✅ Appointment booked for {name} at {datetime}.\nWe’ll contact you if anything changes!"
    )

# /faq command
async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ *Frequently Asked Questions*\n\n"
        "⏰ *Opening hours:* Mon-Fri 08:00–18:00\n"
        "💉 *Services:* General practice, pediatrics, dermatology, lab tests\n"
        "💳 *Insurance:* We accept all major insurance providers.\n\n"
        "Need something else? Use /contact to send us a message.",
        parse_mode="Markdown"
    )

# /contact command
async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("✉️ Usage: /contact <Your message>")
        return

    user = update.message.from_user.username or update.message.from_user.id
    message_text = " ".join(context.args)
    messages.append({"user": user, "message": message_text})

    await update.message.reply_text(
        "✅ Your message has been sent! Our staff will reach out to you soon."
    )

# Set up the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("book", book))
app.add_handler(CommandHandler("faq", faq))
app.add_handler(CommandHandler("contact", contact))

# Run the bot
app.run_polling()
