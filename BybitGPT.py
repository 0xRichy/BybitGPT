import ccxt
import openai
import logging
import requests
import time
import telegram
import threading
from telegram.ext import CommandHandler, Updater

# Vous devez créer vos propres clés API sur Bybit et les remplacer ici
apiKey = 'YOUR_BYBIT_API_KEY'
secret = 'YOUR_BYBIT_SECRET'

openai.api_key = 'YOUR_OPENAI_API_KEY'

exchange = ccxt.bybit({
    'apiKey': apiKey,
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

# Set up logging
logging.basicConfig(filename='bot.log', level=logging.INFO)

# Initialise la connexion avec Telegram
bot_token = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telegram.Bot(token=bot_token)

# ID du chat sur lequel vous souhaitez recevoir les notifications
chat_id = 'YOUR_TELEGRAM_CHAT_ID'

# Variable pour contrôler l'état du trading
trading_active = True

def log_and_notify(message):
    logging.info(message)
    bot.send_message(chat_id=chat_id, text=message)

def set_leverage(leverage: int):
    message = f"Setting leverage to {leverage}"
    log_and_notify(message)

def get_balance():
    message = "Getting balance"
    log_and_notify(message)
    balance = 0
    return balance

def get_price():
    message = "Getting price"
    log_and_notify(message)
    price = 0
    return price

def place_order(side, amount):
    message = f"Placing {side} order for {amount}"
    log_and_notify(message)

def get_openai_decision(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=50
    )
    
    # Extraction de la réponse de ChatGPT
    decision = response.choices[0].text.strip()

    return decision

# Nouvelle fonction pour l'interaction automatique avec ChatGPT et envoi de notifications Telegram
def automatic_chat_with_chatgpt():
    global trading_active

    message = "ChatGPT: Hello! I'm here to assist you with trading decisions."
    log_and_notify(message)

    while True:
        if trading_active:
            # Demande à ChatGPT quelle action prendre en fonction des conditions actuelles du marché
            market_conditions_prompt = "Given the current market conditions, should we buy or sell BTC?"
            decision = get_openai_decision(market_conditions_prompt)

            if decision == 'buy':
                balance = get_balance()
                if balance >= 10:
                    set_leverage(25)  # Set leverage to 25x
                    place_order('BUY', 10)
                    message = "Bot: Placed a BUY order for 10 BTC."
                    log_and_notify(message)
                else:
                    message = "Bot: Not enough USDT balance to execute a BUY order."
                    log_and_notify(message)
            elif decision == 'sell':
                btc_balance = exchange.fetch_balance()['BTC']
                if btc_balance['free'] > 0:
                    set_leverage(25)  # Set leverage to 25x
                    place_order('SELL', btc_balance['free'])
                    message = f"Bot: Placed a SELL order for {btc_balance['free']} BTC."
                    log_and_notify(message)
                else:
                    message = "Bot: No BTC balance to execute a SELL order."
                    log_and_notify(message)
        
        # Attendre 10 minutes avant de demander une autre action à ChatGPT
        time.sleep(600)

# Initialisez l'Updater avec votre token de bot
updater = Updater(token=bot_token, use_context=True)

# Obtenez le gestionnaire de mise à jour
dp = updater.dispatcher

# Fonction pour obtenir la balance du compte
def get_balance_command(update, context):
    balance = get_balance()
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your balance is {balance} USDT")

# Fonction pour obtenir les trades en cours
def get_trades_command(update, context):
    trades = "You have 2 trades open"
    context.bot.send_message(chat_id=update.effective_chat.id, text=trades)

# Fonction pour la commande /restart
def restart_command(update, context):
    restart_text = "Bot needs to be restarted. Please restart the bot manually."
    context.bot.send_message(chat_id=update.effective_chat.id, text=restart_text)

# Fonction pour la commande /set_leverage
def set_leverage_command(update, context):
    if context.args:
        try:
            leverage = int(context.args[0])
            set_leverage(leverage)
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Leverage set to {leverage}.")
        except ValueError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid leverage. Please provide a number.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No leverage provided. Please provide a number after the command. Example: /set_leverage 10")

# Fonction pour la commande /help
def help_command(update, context):
    help_text = """
Here are the available commands:

/balance - Get your current balance
/trades - Get your current trades
/restart - Restart the bot
/set_leverage - Set the leverage (Example: /set_leverage 10)
/status - Get the current status of the bot
/start_trading - Start the trading bot
/stop_trading - Stop the trading bot
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

# Fonction pour la commande /status
def status_command(update, context):
    if trading_active:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The bot is currently trading.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="The bot is currently not trading.")

# Fonctions pour les commandes /start_trading et /stop_trading
def start_trading_command(update, context):
    global trading_active
    trading_active = True
    context.bot.send_message(chat_id=update.effective_chat.id, text="Trading has been started.")

def stop_trading_command(update, context):
    global trading_active
    trading_active = False
    context.bot.send_message(chat_id=update.effective_chat.id, text="Trading has been stopped.")

# Ajoutez les gestionnaires de commandes à votre bot
dp.add_handler(CommandHandler('balance', get_balance_command))
dp.add_handler(CommandHandler('trades', get_trades_command))
dp.add_handler(CommandHandler('restart', restart_command))
dp.add_handler(CommandHandler('set_leverage', set_leverage_command, pass_args=True))
dp.add_handler(CommandHandler('help', help_command))
dp.add_handler(CommandHandler('status', status_command))
dp.add_handler(CommandHandler('start_trading', start_trading_command))
dp.add_handler(CommandHandler('stop_trading', stop_trading_command))

def main():
    # Créez un thread pour l'interaction automatique avec ChatGPT
    chat_thread = threading.Thread(target=automatic_chat_with_chatgpt)

    # Créez un thread pour le bot Telegram
    telegram_thread = threading.Thread(target=updater.start_polling)

    # Démarrez les threads
    chat_thread.start()
    telegram_thread.start()

# Appelez la fonction main pour démarrer les threads
if __name__ == "__main__":
    main()
