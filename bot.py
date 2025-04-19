import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.request import HTTPXRequest
from telegram.error import BadRequest
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token
TOKEN = os.getenv('BOT_TOKEN')

# Admin IDs (convert string to int)
ADMIN_IDS = [int(id_str) for id_str in os.getenv('ADMIN_ID', '').split(',') if id_str]

# Web App URL
WEB_APP_URL = "https://your-domain.com"  # Замініть на ваш URL

def get_main_keyboard():
    """Get main keyboard with web app button."""
    keyboard = [
        [KeyboardButton("🌐 Веб версія", web_app=WebAppInfo(url=WEB_APP_URL))],
        [KeyboardButton("🎨 Дизайн"), KeyboardButton("💻 Програмування")],
        [KeyboardButton("💰 Прайс")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text(
        "Вітаю! Я бот студії STKRMND.\nОберіть опцію:",
        reply_markup=get_main_keyboard()
    )

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle data received from web app."""
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        msg_type = data.get('type')
        user_message = data.get('message')
        user = update.effective_user
        
        # Format message for admin
        admin_message = f"""
📩 *НОВЕ ПОВІДОМЛЕННЯ*

👤 *Від:* {user.full_name}
🔍 *Username:* @{user.username if user.username else 'немає'}
📋 *Тип:* {msg_type}
💭 *Повідомлення:* {user_message}
"""
        
        # Send to all admins
        for admin_id in ADMIN_IDS:
            try:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=admin_message,
                    parse_mode='Markdown'
                )
            except Exception as e:
                logger.error(f"Failed to send message to admin {admin_id}: {e}")
        
        # Send confirmation to user
        await update.message.reply_text(
            "✅ *Дякуємо за ваше повідомлення!*\nМи зв'яжемося з вами найближчим часом.",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error processing web app data: {e}")
        await update.message.reply_text(
            "❌ Виникла помилка при обробці вашого запиту. Спробуйте пізніше."
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular messages."""
    text = update.message.text
    
    if text == "💰 Прайс":
        price_text = """
*💰 STKRMND | STUDIO — Прайс лист*

*🎨 Створення емодзі та стікер паків:*
• [ 🌟 ] (емодзі такого типу) — *0,72$*
• Міні пакунок (10 емодзі) — *7,2$*
• Повний пакунок (40 емодзі) — *28$*

*💡 Про послугу:*
Емодзі, які додають унікальності вашому контенту.
Ідеально підходять для каналів, чатів та особистих проектів.

*💻 Ціна розробки програмування та дизайну залежить від ваших вимог!*
"""
        await update.message.reply_text(price_text, parse_mode='Markdown')
    elif text in ["🎨 Дизайн", "💻 Програмування"]:
        await update.message.reply_text(
            f"Для замовлення {text}, будь ласка, натисніть кнопку '🌐 Веб версія' та заповніть форму."
        )

def main() -> None:
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the Bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 