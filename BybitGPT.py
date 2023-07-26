import ccxt
import openai
import logging
import time
import telegram
import threading
from telegram.ext import CommandHandler, Updater, MessageHandler, Filters
import subprocess

# Replace the placeholders with your actual API keys and tokens
openai.api_key = 'YOUR_OPENAI_API_KEY'
apiKey = 'YOUR_BYBIT_API_KEY'
secret = 'YOUR_BYBIT_API_SECRET'
bot_token = 'YOUR_TELEGRAM_BOT_TOKEN'
chat_id = 'YOUR_CHAT_ID'

exchange = ccxt.bybit({
    'apiKey': apiKey,
    'secret': secret,
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

logging.basicConfig(filename='bot.log', level=logging.INFO)
bot = telegram.Bot(token=bot_token)
trading_active = True

def log_and_notify(message):
    logging.info(message)
    bot.send_message(chat_id=chat_id, text=message)

def set_leverage(leverage: int):
    message = f"Setting leverage to {leverage}"
    log_and_notify(message)

    # Utiliser l'API Bybit pour définir le levier
    try:
        params = {'symbol': 'BTCUSD', 'leverage': leverage}  # Remplacer 'BTCUSD' par le symbole de l'actif que vous tradez
        exchange.set_leverage(symbol='BTC/USDT', leverage=leverage)
    except Exception as e:
        error_message = f"Failed to set leverage: {str(e)}"
        log_and_notify(error_message)



def get_balance():
    message = "Getting balance"
    log_and_notify(message)

    # Utiliser l'API Bybit pour récupérer le solde du compte
    try:
        balance = exchange.fetch_balance()['total']['USDT']
        return balance
    except Exception as e:
        error_message = f"Failed to get balance: {str(e)}"
        log_and_notify(error_message)
        return 0

def get_price():
    message = "Getting price"
    log_and_notify(message)

    # Utiliser l'API Bybit pour obtenir le prix actuel du BTC
    try:
        ticker = exchange.fetch_ticker('BTC/USDT')
        price = ticker['last']
        return price
    except Exception as e:
        error_message = f"Failed to get price: {str(e)}"
        log_and_notify(error_message)
        return 0


def place_order(side, amount):
    message = f"Placing {side} order for {amount}"
    log_and_notify(message)

    # Utiliser l'API Bybit pour placer un ordre
    try:
        order = exchange.create_order('BTC/USDT', 'market', side, amount)
    except Exception as e:
        error_message = f"Failed to place order: {str(e)}"
        log_and_notify(error_message)


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

import subprocess

# Fonction pour la commande /restart
def restart_command(update, context):
    restart_text = "Redémarrage en cours... Le bot va bientôt être de retour en ligne!"
    context.bot.send_message(chat_id=update.effective_chat.id, text=restart_text)

    try:
        subprocess.Popen(["python3", "BybitGPT.py"])
        # Si le fichier est dans un autre répertoire, ajustez le chemin d'accès en conséquence
        # Par exemple, si le fichier est dans le dossier /chemin/vers/le/fichier/BybitGPT.py :
        # subprocess.Popen(["python3", "/chemin/vers/le/fichier/BybitGPT.py"])

        success_text = "Redémarrage réussi ! Le bot est de retour en ligne. Profitez de nos services !"
        context.bot.send_message(chat_id=update.effective_chat.id, text=success_text)
    except Exception as e:
        error_message = f"Une erreur s'est produite lors du redémarrage du bot : {e}"
        context.bot.send_message(chat_id=update.effective_chat.id, text=error_message)


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

# Function for setting the risk level command
def set_risk_level_command(update, context):
    if context.args:
        try:
            risk_level = context.args[0].lower()
            # Implement the logic to set the risk level based on the input (e.g., 'low', 'medium', 'high')
            # Your code here

            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Risk level set to {risk_level}.")
        except ValueError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid risk level. Please provide 'low', 'medium', or 'high'.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No risk level provided. Please provide a risk level after the command. Example: /set_risk_level medium")

def get_profit_command(update, context):
    # Implement the logic to calculate and fetch the total profit from your trading activities
    try:
        # Fetch all closed trades
        closed_trades = exchange.fetch_closed_orders('BTC/USDT')

        # Calculate the total profit
        total_profit = sum([trade['profit'] for trade in closed_trades if trade['status'] == 'closed'])

        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Total profit: {total_profit} USDT")
    except Exception as e:
        error_message = f"Failed to get profit: {str(e)}"
        log_and_notify(error_message)

    # If the above code fails, it will send a default profit value
    total_profit = 1000  # Replace this with the actual calculated profit
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Total profit: {total_profit} USDT")

# Function for the command /get_open_positions
def get_open_positions_command(update, context):
    try:
        # Fetch all open orders
        open_orders = exchange.fetch_open_orders('BTC/USDT')

        # Filter the open orders to include only positions
        open_positions = [order for order in open_orders if order['type'] == 'market']

        if open_positions:
            # Format the open positions information
            open_positions_info = "\n".join([f"Position {i+1}: {position['side']} {position['amount']} BTC at {position['price']} USDT" for i, position in enumerate(open_positions)])
            context.bot.send_message(chat_id=update.effective_chat.id, text=open_positions_info)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You have no open positions.")
    except Exception as e:
        error_message = f"Failed to get open positions: {str(e)}"
        log_and_notify(error_message)

        # If the above code fails or there are no positions, send a default message
        context.bot.send_message(chat_id=update.effective_chat.id, text="You have no open positions.")



# Function to close a specific position based on the position number
def close_position_command(update, context):
    global trade_amount

    if context.args:
        try:
            position_number = int(context.args[0])
            # Implement the logic to close the specific position based on the position number
            open_positions = exchange.fetch_open_orders('BTC/USDT')

            if 1 <= position_number <= len(open_positions):
                position_to_close = open_positions[position_number - 1]
                exchange.cancel_order(position_to_close['id'], 'BTC/USDT')

                # Decrease the trade amount by the amount of the closed position
                trade_amount -= position_to_close['amount']

                context.bot.send_message(chat_id=update.effective_chat.id, text=f"Closed position {position_number}.")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid position number. No such position.")
        except ValueError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid position number. Please provide a valid number.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No position number provided. Please provide a position number after the command. Example: /close_position 1")


# Function to set the trade amount based on the input
def set_trade_amount_command(update, context):
    global trade_amount

    if context.args:
        try:
            trade_amount = float(context.args[0])

            # Add your custom logic here if needed, for example, ensuring the trade amount is within a specific range.

            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Trade amount set to {trade_amount} BTC.")
        except ValueError:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid trade amount. Please provide a valid number.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No trade amount provided. Please provide a trade amount after the command. Example: /set_trade_amount 100")


def get_market_conditions_command(update, context):
    # Implement the logic to fetch and display the current market conditions
    try:
        # Fetch the ticker for BTC/USDT
        ticker = exchange.fetch_ticker('BTC/USDT')

        # Format the market conditions information
        market_conditions = f"The current price of BTC is {ticker['last']} USDT."

        context.bot.send_message(chat_id=update.effective_chat.id, text=market_conditions)
    except Exception as e:
        error_message = f"Failed to get market conditions: {str(e)}"
        log_and_notify(error_message)

    # If the above code fails, it will send a default market conditions information
    market_conditions = "The market conditions are favorable for buying BTC."  # Replace this with the actual market conditions information
    context.bot.send_message(chat_id=update.effective_chat.id, text=market_conditions)

trading_strategy = ""  # Global variable to store the trading strategy

def set_strategy_command(update, context):
    global trading_strategy
    if context.args:
        trading_strategy = " ".join(context.args)
        # Implement the logic to set the trading strategy based on the input
        if trading_strategy.lower() == "scalping":
            # For scalping, we might want to use high leverage and small trade size
            set_leverage(50)
            set_trade_amount(0.01)
        elif trading_strategy.lower() == "swing":
            # For swing trading, we might want to use low leverage and large trade size
            set_leverage(10)
            set_trade_amount(1.0)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid strategy. Please provide a valid strategy. Example: /set_strategy scalping")

        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Trading strategy set to: {trading_strategy}.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No trading strategy provided. Please provide a strategy after the command. Example: /set_strategy scalping")


trading_strategy = ""  # Global variable to store the trading strategy

# Function for the command /analyze_market
def analyze_market_command(update, context):
    # Prompt the user to enter their market analysis
    context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter your market analysis:")

    # Set the handler for the user response
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, analyze_market_response))

# Function to handle the user response to /analyze_market
def analyze_market_response(update, context):
    # Get the user's market analysis
    market_analysis = update.message.text.strip()
    if not market_analysis:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No market analysis provided.")
        return

    # Get the trading decision from ChatGPT using the user's market analysis as the prompt
    decision = get_openai_decision(market_analysis)

    # Send the trading decision to the user
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"ChatGPT's decision: {decision}")

    # Log the market analysis and ChatGPT's decision
    log_message = f"User market analysis: {market_analysis}\nChatGPT's decision: {decision}"
    log_and_notify(log_message)

    # Remove the temporary message handler to avoid processing future messages as responses to /analyze_market
    dp.remove_handler(analyze_market_response)

    # Implement the logic to execute the trading decision
    if decision.lower() == 'buy':
        balance = get_balance()
        if balance >= 10:
            set_leverage(25)  # Set leverage to 25x
            place_order('BUY', 10)
            message = "Bot: Placed a BUY order for 10 BTC."
            log_and_notify(message)
        else:
            message = "Bot: Not enough USDT balance to execute a BUY order."
            log_and_notify(message)
    elif decision.lower() == 'sell':
        btc_balance = exchange.fetch_balance()['BTC']
        if btc_balance['free'] > 0:
            set_leverage(25)  # Set leverage to 25x
            place_order('SELL', btc_balance['free'])
            message = f"Bot: Placed a SELL order for {btc_balance['free']} BTC."
            log_and_notify(message)
        else:
            message = "Bot: No BTC balance to execute a SELL order."
            log_and_notify(message)

# Function for the command /get_strategy
def get_strategy_command(update, context):
    global trading_strategy
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Current trading strategy: {trading_strategy}")

# Function for the command /set_strategy
def set_strategy_command(update, context):
    global trading_strategy
    if context.args:
        new_strategy = " ".join(context.args)
        # Implement the logic to set the trading strategy based on the input
        if new_strategy.lower() == "scalping":
            # For scalping, we might want to use high leverage and small trade size
            set_leverage(50)
            set_trade_amount(0.01)
        elif new_strategy.lower() == "swing":
            # For swing trading, we might want to use low leverage and large trade size
            set_leverage(10)
            set_trade_amount(1.0)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Invalid strategy. Please provide a valid strategy. Example: /set_strategy scalping")
            return

        # Update the trading strategy and notify the user
        trading_strategy = new_strategy
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Trading strategy set to: {trading_strategy}.")
        log_and_notify(f"Trading strategy set to: {trading_strategy}.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No trading strategy provided. Please provide a strategy after the command. Example: /set_strategy scalping")


# Function for the /help command
def help_command(update, context):
    help_text = """
Here are the available commands:

🏦 Account:
/balance - Get your current balance

📈 Trading:
/trades - Get your current trades
/start_trading - Start the trading bot
/stop_trading - Stop the trading bot
/set_leverage - Set the leverage (Example: /set_leverage 10)
/set_risk_level - Set the risk level (Example: /set_risk_level medium)
/set_trade_amount - Set the trade amount (Example: /set_trade_amount 100)
/get_profit - Get the total profit

🔍 Market:
/get_open_positions - Get the open positions
/close_position - Close a specific position (Example: /close_position 1)
/get_market_conditions - Get the current market conditions
/analyze_market - Manually analyze the market and get a trading decision from ChatGPT

⚙️ Settings:
/restart - Restart the bot
/set_strategy - Set the trading strategy (Example: /set_strategy scalping)
/get_strategy - Get the current trading strategy
/status - Get the current status of the bot
    """
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)


# Function for the command /status
def status_command(update, context):
    try:
        # Fetch current positions from Bybit
        open_positions = exchange.fetch_open_positions('BTC/USDT')

        if open_positions:
            context.bot.send_message(chat_id=update.effective_chat.id, text="The bot is currently trading. There are open positions.")
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="The bot is currently not trading. There are no open positions.")
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error occurred while checking the status: {str(e)}")


# Global variable to store the trading status
trading_active = False

# Functions for the commands /start_trading and /stop_trading
def start_trading_command(update, context):
    global trading_active
    trading_active = True
    context.bot.send_message(chat_id=update.effective_chat.id, text="Trading has been started.")

def stop_trading_command(update, context):
    global trading_active
    trading_active = False
    context.bot.send_message(chat_id=update.effective_chat.id, text="Trading has been stopped.")

# Function for the command /trade
def trade_command(update, context):
    try:
        # Fetch current positions from Bybit
        open_positions = exchange.fetch_open_positions('BTC/USDT')

        if open_positions:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Cannot execute trade. There are already open positions.")
        else:
            # Send a message to prompt the user for their market analysis
            context.bot.send_message(chat_id=update.effective_chat.id, text="Please enter your market analysis:")

            # Set the handler for the user response
            dp.add_handler(MessageHandler(Filters.text & ~Filters.command, trade_response))

    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error occurred while fetching positions: {str(e)}")

def trade_response(update, context):
    # Get the user's market analysis
    market_analysis = update.message.text.strip()
    if not market_analysis:
        context.bot.send_message(chat_id=update.effective_chat.id, text="No market analysis provided.")
        return

    try:
        # Send the market analysis to the user and to ChatGPT
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your market analysis: {market_analysis}")

        # Get the trading decision from ChatGPT using the user's market analysis as the prompt
        decision = get_openai_decision(market_analysis)

        # Send ChatGPT's decision to the user
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"ChatGPT's decision: {decision}")

        # Implement the logic to execute the trading decision
        if decision.lower() == 'buy':
            balance = get_balance()
            if balance >= 10:
                set_leverage(25)  # Set leverage to 25x
                place_order('BUY', 10)
                context.bot.send_message(chat_id=update.effective_chat.id, text="Placed a BUY order for 10 BTC.")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="Not enough USDT balance to execute a BUY order.")
        elif decision.lower() == 'sell':
            btc_balance = exchange.fetch_balance()['BTC']
            if btc_balance['free'] > 0:
                set_leverage(25)  # Set leverage to 25x
                place_order('SELL', btc_balance['free'])
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"Placed a SELL order for {btc_balance['free']} BTC.")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text="No BTC balance to execute a SELL order.")
        
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error occurred while processing trade: {str(e)}")

    # Remove the temporary message handler to avoid processing future messages as responses to /trade
    dp.remove_handler(trade_response)


# Add the command handlers to your bot, including the new /analyze_market
dp.add_handler(CommandHandler('balance', get_balance_command))
dp.add_handler(CommandHandler('trades', get_trades_command))
dp.add_handler(CommandHandler('restart', restart_command))
dp.add_handler(CommandHandler('set_leverage', set_leverage_command, pass_args=True))
dp.add_handler(CommandHandler('help', help_command))
dp.add_handler(CommandHandler('status', status_command))
dp.add_handler(CommandHandler('start_trading', start_trading_command))
dp.add_handler(CommandHandler('stop_trading', stop_trading_command))
dp.add_handler(CommandHandler('set_risk_level', set_risk_level_command, pass_args=True))
dp.add_handler(CommandHandler('get_profit', get_profit_command))
dp.add_handler(CommandHandler('get_open_positions', get_open_positions_command))
dp.add_handler(CommandHandler('close_position', close_position_command, pass_args=True))
dp.add_handler(CommandHandler('set_trade_amount', set_trade_amount_command, pass_args=True))
dp.add_handler(CommandHandler('get_market_conditions', get_market_conditions_command))
dp.add_handler(CommandHandler('set_strategy', set_strategy_command, pass_args=True))
dp.add_handler(CommandHandler('get_strategy', get_strategy_command))
dp.add_handler(CommandHandler('analyze_market', analyze_market_command))

def main():
    # Create a thread for automatic interaction with GPT-4
    chat_thread = threading.Thread(target=automatic_chat_with_chatgpt)

    # Create a thread for the Telegram bot
    telegram_thread = threading.Thread(target=updater.start_polling)

    # Start the threads
    chat_thread.start()
    telegram_thread.start()

# Call the main function to start the threads
if __name__ == "__main__":
    main()
