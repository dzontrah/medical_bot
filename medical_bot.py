import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, ConversationHandler, filters
)

# Environment variable for bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Conversation states
BOOK_NAME, BOOK_DATETIME, BOOK_PHONE, CONTACT_MESSAGE = range(4)

# In-memory storage
appointments = []
contact_messages = []

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

# /faq command
async def faq(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Frequently Asked Questions\n\n"
        "⏰ Opening hours: Mon–Fri 08:00–18:00\n"
        "💉 Services: General practice, pediatrics, dermatology, lab tests\n"
        "💳 Insurance: We accept all major insurance providers.\n\n"
        "Need something else? Use /contact to send us a message."
    )

# ---- BOOKING ----

async def book_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👤 Please provide your full name.")
    return BOOK_NAME

async def book_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("📅 Please provide the desired date and time (e.g., 2025-05-10 14:00).")
    return BOOK_DATETIME

async def book_datetime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["datetime"] = update.message.text
    await update.message.reply_text("📞 Please provide your phone number (we'll use it to confirm the booking).")
    return BOOK_PHONE

async def book_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = context.user_data["name"]
    datetime = context.user_data["datetime"]
    phone = update.message.text
    appointments.append({"name": name, "datetime": datetime, "phone": phone})
    await update.message.reply_text(
        f"✅ Thank you, {name}! Your appointment is booked for {datetime}.\n"
        f"📞 We will contact you at: {phone}."
    )
    return ConversationHandler.END

async def book_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Booking process canceled.")
    return ConversationHandler.END

# ---- CONTACT ----

async def contact_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✉️ Please type your message for the clinic.")
    return CONTACT_MESSAGE

async def contact_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    message = update.message.text
    contact_messages.append({"user": user.username or user.first_name, "message": message})
    await update.message.reply_text("✅ Your message has been sent to the clinic. We'll get back to you soon!")
    return ConversationHandler.END

async def contact_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Contact process canceled.")
    return ConversationHandler.END

# ---- MAIN ----

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("faq", faq))

# Booking conversation
book_conv = ConversationHandler(
    entry_points=[CommandHandler("book", book_start)],
    states={
        BOOK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, book_name)],
        BOOK_DATETIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, book_datetime)],
        BOOK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, book_phone)],
    },
    fallbacks=[CommandHandler("cancel", book_cancel)],
)
app.add_handler(book_conv)

# Contact conversation
contact_conv = ConversationHandler(
    entry_points=[CommandHandler("contact", contact_start)],
    states={
        CONTACT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact_message)],
    },
    fallbacks=[CommandHandler("cancel", contact_cancel)],
)
app.add_handler(contact_conv)

# Run the bot
app.run_polling()
