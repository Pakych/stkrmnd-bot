# STKRMND | STUDIO Feedback Bot

Telegram bot for handling feedback and inquiries about programming and design services.

## Features

- Interactive menu with buttons
- Price list display
- Feedback collection for Design and Programming categories
- Automatic message forwarding to administrators

## Setup

1. Install Python 3.7 or higher
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the bot:
   ```
   python bot.py
   ```

## Usage

1. Start the bot with `/start` command
2. Use the menu buttons to:
   - Write to us (choose Design or Programming)
   - View price list
3. Follow the prompts to send your message

## Admin Configuration

The bot is configured to forward messages to the following admin IDs:
- 6053516349
- 1991195848

To change admin IDs, modify the `ADMIN_IDS` list in `bot.py`. 