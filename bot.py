import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from telegram.request import HTTPXRequest
from telegram.error import BadRequest
import os
import json
from dotenv import load_dotenv
from datetime import datetime

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

# Admin IDs
ADMIN_IDS = [6053516349, 1991195848]  # Replace with actual admin IDs

# Web App URL
WEB_APP_URL = os.getenv("WEB_APP_URL", "https://pakych.github.io/stkrmnd-bot/?v=1.0.2")

# Категорії для кнопок
CATEGORIES = {
    "programming": "Програмування 💻",
    "design": "Дизайн 🎨",
    "video": "Відеомонтаж 🎬",
    "editing": "Редагування фото 📸",
    "other": "Інше 📝"
}

def get_main_keyboard():
    """Get main keyboard with web app button."""
    keyboard = [
        [KeyboardButton("🌐 Веб версія", web_app=WebAppInfo(url=WEB_APP_URL))],
        [KeyboardButton("🎨 Дизайн"), KeyboardButton("💻 Програмування")],
        [KeyboardButton("🎬 Відеомонтаж"), KeyboardButton("📸 Редагування фото")],
        [KeyboardButton("💰 Прайс")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    
    # Initialize messages list in bot_data if not exists
    if 'messages' not in context.bot_data:
        context.bot_data['messages'] = []
    
    # Check if user is admin
    if user.id in ADMIN_IDS:
        keyboard = [
            [KeyboardButton("🌐 Веб версія", web_app=WebAppInfo(url=WEB_APP_URL))],
            [KeyboardButton("📬 Повідомлення"), KeyboardButton("📊 Статистика")],
            [KeyboardButton("💰 Прайс")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"👋 Вітаю, {user.full_name}!\n\n"
            "🔑 *Ви увійшли як адміністратор*\n\n"
            "Доступні команди:\n"
            "/messages - переглянути всі повідомлення\n"
            "/stats - переглянути статистику\n\n"
            "Використовуйте кнопки нижче для навігації:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return

    keyboard = [
        [KeyboardButton("🌐 Веб версія", web_app=WebAppInfo(url=WEB_APP_URL))],
        [KeyboardButton("🎨 Дизайн"), KeyboardButton("💻 Програмування")],
        [KeyboardButton("🎬 Відеомонтаж"), KeyboardButton("📸 Редагування фото")],
        [KeyboardButton("💰 Прайс")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        f"👋 Вітаю, {user.full_name}!\n\n"
        "🎨 *STKRMND Studio* - ваш надійний партнер у створенні:\n"
        "• Веб-сайтів та додатків\n"
        "• Дизайну будь-якої складності\n"
        "• Відеомонтажу та анімації\n"
        "• Обробки фотографій\n\n"
        "Використовуйте кнопки нижче для навігації:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle data received from web app."""
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        msg_type = data.get('type')
        user = update.effective_user
        
        # Handle admin actions
        if msg_type == 'admin_action':
            if user.id not in ADMIN_IDS:
                await update.message.reply_text("❌ У вас немає прав для виконання цієї дії.")
                return
                
            action = data.get('action')
            message_id = data.get('messageId')
            
            if action == 'reply':
                reply_text = data.get('reply')
                try:
                    # Get the original message details from context.bot_data
                    original_message = next(
                        (msg for msg in context.bot_data.get('messages', []) if str(msg.get('id')) == str(message_id)),
                        None
                    )
                    if original_message:
                        user_id = original_message.get('user_id')
                        try:
                            await context.bot.send_message(
                                chat_id=user_id,
                                text=f"*Відповідь від STKRMND:*\n\n{reply_text}",
                                parse_mode='Markdown'
                            )
                            await update.message.reply_text("✅ Відповідь надіслано успішно!")
                        except Exception as e:
                            logger.error(f"Error sending reply to user: {e}")
                            await update.message.reply_text("❌ Не вдалося надіслати відповідь користувачу.")
                    else:
                        await update.message.reply_text("❌ Повідомлення не знайдено.")
                except Exception as e:
                    logger.error(f"Error processing reply: {e}")
                    await update.message.reply_text("❌ Помилка при обробці відповіді.")
                return
                
            elif action == 'mark_completed':
                try:
                    # Mark message as completed in context.bot_data
                    message = next(
                        (msg for msg in context.bot_data['messages'] if str(msg['id']) == str(message_id)),
                        None
                    )
                    if message:
                        message['completed'] = True
                        await update.message.reply_text("✅ Позначено як виконане!")
                    else:
                        await update.message.reply_text("❌ Повідомлення не знайдено.")
                except Exception as e:
                    logger.error(f"Error marking as completed: {e}")
                    await update.message.reply_text("❌ Помилка при позначенні як виконане.")
                return
        
        # Handle regular messages
        user_message = data.get('message')
        
        # Store message in context.bot_data
        message_id = len(context.bot_data['messages']) + 1
        message_data = {
            'id': message_id,
            'user_id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'type': msg_type,
            'message': user_message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'completed': False
        }
        context.bot_data['messages'].append(message_data)
        
        # Format message for admin
        admin_message = f"""
📩 *НОВЕ ПОВІДОМЛЕННЯ*

👤 *Від:* {user.full_name}
🔍 *Username:* @{user.username if user.username else 'немає'}
📋 *Тип:* {msg_type}
💭 *Повідомлення:* {user_message}

🆔 Message ID: `{message_id}`
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
    user = update.effective_user
    
    # Якщо це відповідь від адміна на повідомлення
    if user.id in ADMIN_IDS and update.message.reply_to_message:
        replied_msg = update.message.reply_to_message
        
        try:
            # Знаходимо ID повідомлення в тексті
            msg_id = None
            for line in replied_msg.text.split('\n'):
                if 'Message ID:' in line:
                    try:
                        # Видаляємо всі символи крім цифр
                        msg_id_str = ''.join(filter(str.isdigit, line))
                        if msg_id_str:
                            msg_id = int(msg_id_str)
                            break
                    except ValueError:
                        continue
            
            if msg_id is not None:
                # Безпечно отримуємо список повідомлень
                messages = context.bot_data.get('messages', [])
                original_msg = next(
                    (msg for msg in messages if msg.get('id') == msg_id),
                    None
                )
                
                if original_msg:
                    user_id = original_msg.get('user_id')
                    if user_id:
                        try:
                            await context.bot.send_message(
                                chat_id=user_id,
                                text=f"*Відповідь від STKRMND:*\n\n{text}",
                                parse_mode='Markdown'
                            )
                            await update.message.reply_text("✅ Відповідь надіслано успішно!")
                        except Exception as e:
                            logger.error(f"Error sending reply to user: {e}")
                            await update.message.reply_text("❌ Не вдалося надіслати відповідь користувачу.")
                    else:
                        await update.message.reply_text("❌ Не знайдено ID користувача.")
                else:
                    await update.message.reply_text("❌ Повідомлення не знайдено.")
            else:
                await update.message.reply_text("❌ Не знайдено ID повідомлення.")
        except Exception as e:
            logger.error(f"Error processing reply: {e}")
            await update.message.reply_text("❌ Помилка при обробці відповіді.")
        return

    # Handle regular messages
    if text == "📬 Повідомлення" and user.id in ADMIN_IDS:
        await admin_messages(update, context)
        return
    elif text == "📊 Статистика" and user.id in ADMIN_IDS:
        await admin_stats(update, context)
        return
    elif text == "💰 Прайс":
        price_text = """
*💰 STKRMND | STUDIO — Прайс лист*

*🎨 Створення емодзі та стікер паків:*
• [Емодзі такого типу](https://t.me/addemoji/zahidsticker_by_fStikBot) — *0,72$*
• Міні пакунок (10 емодзі) — *7,2$*
• Повний пакунок (40 емодзі) — *28$*

*🎬 Відеомонтаж:*
• Базове редагування — від *15$*
• Едіт — від *15$*
• Повний монтаж — від *30$*

*📸 Редагування фото:*
• Аватар проекту — від *5$*
• Обкладинка проекту — від *10$*
• Прев'ю — від *20$*

*💻 Розробка:*
• Telegram боти — від *50$*
• Веб-сайти — від *200$*
• Десктопні програми — від *300$*

*💡 Про послуги:*
• Індивідуальний підхід до кожного проекту
• Безкоштовні правки
• Підтримка після виконання

*📞 Для детального обговорення використовуйте веб-форму або оберіть категорію в меню.*
"""
        await update.message.reply_text(price_text, parse_mode='Markdown')
    elif text in ["🎨 Дизайн", "💻 Програмування", "🎬 Відеомонтаж", "📸 Редагування фото"]:
        await update.message.reply_text(
            f"Опишіть ваш проект для категорії {text}.\nЯ передам ваше повідомлення адміністраторам.",
            reply_markup=get_main_keyboard()
        )
    else:
        # Store regular message in context.bot_data
        if 'messages' not in context.bot_data:
            context.bot_data['messages'] = []
            
        message_id = len(context.bot_data['messages']) + 1
        message_type = 'other'  # Default type for regular messages
        
        # Try to determine message type based on content
        if "програм" in text.lower():
            message_type = 'programming'
        elif "дизайн" in text.lower():
            message_type = 'design'
        elif "відео" in text.lower() or "монтаж" in text.lower():
            message_type = 'video'
        elif "фото" in text.lower() or "редагування" in text.lower():
            message_type = 'editing'
        
        message_data = {
            'id': message_id,
            'user_id': user.id,
            'username': user.username,
            'full_name': user.full_name if user.full_name else "Користувач",
            'type': message_type,
            'message': text,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'completed': False
        }
        context.bot_data['messages'].append(message_data)
        
        # Format message for admin
        admin_message = f"""
📩 *НОВЕ ПОВІДОМЛЕННЯ*

👤 *Від:* {message_data['full_name']}
🔍 *Username:* @{message_data['username'] if message_data['username'] else 'немає'}
📋 *Тип:* {message_type}
💭 *Повідомлення:* {text}

🆔 Message ID: `{message_id}`
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
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )

async def admin_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show messages to admin."""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ У вас немає прав для виконання цієї команди.")
        return

    if 'messages' not in context.bot_data:
        context.bot_data['messages'] = []
    
    messages = context.bot_data['messages']
    
    if not messages:
        await update.message.reply_text("📭 Наразі немає повідомлень.")
        return
        
    # Format messages
    message_text = "📬 *Останні повідомлення:*\n\n"
    for msg in messages[-10:]:  # Show last 10 messages
        status = "✅ Виконано" if msg.get('completed', False) else "⏳ В обробці"
        message_text += f"👤 *Від:* {msg['full_name']}\n"
        message_text += f"📱 *Telegram:* @{msg['username'] if msg['username'] else 'немає'}\n"
        message_text += f"📋 *Категорія:* {msg['type']}\n"
        message_text += f"💬 *Повідомлення:* {msg['message']}\n"
        message_text += f"⏰ *Час:* {msg['timestamp']}\n"
        message_text += f"📊 *Статус:* {status}\n"
        message_text += f"🆔 Message ID: `{msg['id']}`\n\n"
        message_text += "➖➖➖➖➖➖➖➖➖➖\n\n"
    
    await update.message.reply_text(message_text, parse_mode='Markdown')

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show statistics to admin."""
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ У вас немає прав для виконання цієї команди.")
        return

    if 'messages' not in context.bot_data:
        context.bot_data['messages'] = []
    
    messages = context.bot_data['messages']
    
    # Calculate statistics
    total_messages = len(messages)
    completed_messages = sum(1 for msg in messages if msg.get('completed', False))
    pending_messages = total_messages - completed_messages
    
    # Count messages by type
    type_counts = {}
    for msg in messages:
        msg_type = msg.get('type', 'other')
        type_counts[msg_type] = type_counts.get(msg_type, 0) + 1
    
    # Format statistics message
    stats_text = "📊 *Статистика повідомлень:*\n\n"
    stats_text += f"📨 *Всього повідомлень:* {total_messages}\n\n"
    
    if type_counts:
        stats_text += "*По категоріях:*\n"
        for msg_type, count in type_counts.items():
            category_name = CATEGORIES.get(msg_type, msg_type.capitalize())
            stats_text += f"• {category_name}: {count}\n"
        stats_text += "\n"
    
    stats_text += "*Статус повідомлень:*\n"
    stats_text += f"✅ Виконано: {completed_messages}\n"
    stats_text += f"⏳ В обробці: {pending_messages}\n"
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'messages':
        if query.from_user.id not in ADMIN_IDS:
            await query.message.reply_text("❌ У вас немає прав для виконання цієї команди.")
            return
        await admin_messages(update, context)
    elif query.data == 'stats':
        if query.from_user.id not in ADMIN_IDS:
            await query.message.reply_text("❌ У вас немає прав для виконання цієї команди.")
            return
        await admin_stats(update, context)

def main() -> None:
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("messages", admin_messages))
    application.add_handler(CommandHandler("stats", admin_stats))
    
    # Callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Web app data handler
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    
    # Regular message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main() 