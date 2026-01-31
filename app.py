import os
import logging
import random
import string
import threading
import asyncio
from typing import Dict
from flask import Flask, request
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN environment variable is not set!")
    raise ValueError("TELEGRAM_BOT_TOKEN is required")

# User session data (in-memory for demo)
user_sessions: Dict[int, Dict] = {}

def generate_eth_address():
    """Generate a random Ethereum-like wallet address"""
    chars = string.hexdigits.lower()[:16]
    prefix = "0x"
    address = ''.join(random.choice(chars) for _ in range(40))
    return prefix + address

def get_main_keyboard():
    """Create the main interactive keyboard"""
    keyboard = [
        [KeyboardButton("💰 Deposit"), KeyboardButton("📊 Trade")],
        [KeyboardButton("🚀 Start/Stop Trading"), KeyboardButton("💸 Withdraw")],
        [KeyboardButton("ℹ️ Help")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with main keyboard"""
    welcome_text = (
        "🤖 *Welcome to Demo Trading Bot!*\n\n"
        "⚠️ *DISCLAIMER:* This is a DEMO bot only. "
        "No real funds, trading, or blockchain interactions occur.\n\n"
        "Use the buttons below to interact with the demo features:"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_keyboard(),
        parse_mode='Markdown'
    )
    
    # Initialize user session
    user_id = update.effective_user.id
    user_sessions[user_id] = {
        'trading_active': False,
        'awaiting_withdrawal': False
    }

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send help message"""
    await start_command(update, context)  # Reuse start for now

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages and button presses"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Initialize user session if not exists
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'trading_active': False,
            'awaiting_withdrawal': False
        }
    
    # Check if awaiting withdrawal address
    if user_sessions[user_id].get('awaiting_withdrawal', False):
        # Process withdrawal address
        eth_address = message_text.strip()
        if eth_address.startswith('0x') and len(eth_address) == 42:
            response = (
                f"✅ *Withdrawal Confirmed!*\n\n"
                f"🎉 Congratulations! 10 ETH profit is on its way to:\n"
                f"`{eth_address}`\n\n"
                f"⏰ *Estimated arrival:* 2-5 minutes (demo)\n"
                f"💼 *Transaction fee:* 0.001 ETH (simulated)\n"
                f"📊 *Total sent:* 9.999 ETH\n\n"
                f"⚠️ Remember: This is a demo. No real transaction occurred."
            )
            user_sessions[user_id]['awaiting_withdrawal'] = False
        else:
            response = "⚠️ Please enter a valid Ethereum address (starting with 0x, 42 characters)"
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
        return
    
    # Handle button actions
    if message_text == "💰 Deposit":
        eth_address = generate_eth_address()
        
        response = (
            f"💎 *Deposit Instructions*\n\n"
            f"🔗 *Demo Wallet Address:*\n"
            f"`{eth_address}`\n\n"
            f"📝 *Network:* Ethereum (ERC-20)\n"
            f"💡 *Minimum:* 0.01 ETH (demo)\n\n"
            f"⚠️ *IMPORTANT DEMO NOTE:*\n"
            f"This is a test address. DO NOT send real funds!\n"
            f"Your 'balance' will update automatically in this demo."
        )
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    elif message_text == "📊 Trade":
        # Simulate trading action
        trade_types = ["LONG", "SHORT"]
        assets = ["ETH/USDT", "BTC/USDT", "SOL/USDT"]
        entry_price = round(random.uniform(2500, 3500), 2)
        leverage = random.choice([5, 10, 20, 50])
        
        response = (
            f"🚨 *TRADE ALERT!*\n\n"
            f"⚡ *Action:* Entering market\n"
            f"📈 *Position:* {random.choice(trade_types)}\n"
            f"💰 *Asset:* {random.choice(assets)}\n"
            f"🎯 *Entry Price:* ${entry_price}\n"
            f"📊 *Leverage:* {leverage}x\n"
            f"⏰ *Timeframe:* 15m chart\n"
            f"🎯 *Target:* +5% profit\n"
            f"🛑 *Stop Loss:* -2%\n\n"
            f"💡 *Demo Note:* This is simulated trading only!"
        )
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    elif message_text == "🚀 Start/Stop Trading":
        # Toggle trading status
        current_status = user_sessions[user_id]['trading_active']
        user_sessions[user_id]['trading_active'] = not current_status
        
        if not current_status:
            response = (
                "✅ *Trading Started Successfully!*\n\n"
                "🤖 *Auto-trading is now ACTIVE*\n"
                "📊 *Strategy:* Grid Trading\n"
                "💰 *Capital allocated:* $10,000 (demo)\n"
                "🎯 *Daily target:* 2-5%\n"
                "🔄 *Pairs trading:* 3 pairs\n\n"
                "📈 Bot will now simulate trades automatically."
            )
        else:
            response = (
                "🛑 *Trading Stopped*\n\n"
                "✅ All positions closed (simulated)\n"
                "📊 *Final P&L:* +$423.15 (demo)\n"
                "📈 *Win rate:* 72.5%\n"
                "💰 *Total trades:* 18\n\n"
                "Ready to restart when you are!"
            )
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    elif message_text == "💸 Withdraw":
        # Request withdrawal address
        user_sessions[user_id]['awaiting_withdrawal'] = True
        
        response = (
            "💸 *Withdrawal Request*\n\n"
            "📤 *Available balance:* 15.5 ETH (demo)\n"
            "💰 *Profit to withdraw:* 10 ETH\n\n"
            "🔗 *Please enter your Ethereum address:*\n"
            "(Format: 0x followed by 40 characters)\n\n"
            "Example: `0x742d35Cc6634C0532925a3b844Bc9e90F1f04e5a`"
        )
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown'
        )
    
    elif message_text == "ℹ️ Help":
        response = (
            "🤖 *Demo Trading Bot Help*\n\n"
            "🔹 *💰 Deposit* - Get demo ETH address\n"
            "🔹 *📊 Trade* - Simulate a trade entry\n"
            "🔹 *🚀 Start/Stop* - Toggle auto-trading\n"
            "🔹 *💸 Withdraw* - Simulate profit withdrawal\n\n"
            "⚠️ *IMPORTANT DISCLAIMER:*\n"
            "• This is a DEMONSTRATION bot only\n"
            "• NO real funds are involved\n"
            "• NO real trading occurs\n"
            "• NO real blockchain transactions\n"
            "• All addresses, balances, and profits are simulated\n\n"
            "📚 *Educational Purpose:*\n"
            "This bot demonstrates basic trading bot functionality "
            "without financial risk."
        )
        
        await update.message.reply_text(
            response,
            parse_mode='Markdown',
            reply_markup=get_main_keyboard()
        )
    
    else:
        # Handle other messages
        await update.message.reply_text(
            "Please use the buttons below to interact with the bot!",
            reply_markup=get_main_keyboard()
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")

def setup_bot():
    """Set up and run the Telegram bot"""
    # Create Telegram bot application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("🤖 Bot starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

# Flask routes
@app.route('/')
def home():
    return "Telegram Demo Trading Bot is running! The bot is active via polling."

@app.route('/health')
def health():
    return "OK", 200

@app.route('/set_webhook', methods=['GET'])
def set_webhook_page():
    """Info page about webhook setup (not used for polling)"""
    return "This bot uses polling method. No webhook setup needed.", 200

def start_bot_in_thread():
    """Start the bot in a separate thread"""
    try:
        # Create and run the bot in this thread
        asyncio.run(setup_bot())
    except Exception as e:
        logger.error(f"Bot thread failed: {e}")

if __name__ == '__main__':
    # Start the Telegram bot in a separate thread
    logger.info("🚀 Starting application...")
    bot_thread = threading.Thread(target=start_bot_in_thread, daemon=True)
    bot_thread.start()
    logger.info("🤖 Bot thread started successfully")
    
    # Start Flask web server
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Flask server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
