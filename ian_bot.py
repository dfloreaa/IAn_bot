from telegram.ext import Updater, CommandHandler
from flask import Flask, request
import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'config.json')
reminder_path = os.path.join(dir_path, 'reminders.json')

with open(config_path, 'r') as f:
    config = json.load(f)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if 'issue' in data:
        # Send issue content to Telegram group using Telegram API
        send_issue_to_telegram(data['issue'])
    return '', 200

Updater(token = config["TELEGRAM_BOT_TOKEN"], use_context = True)

def send_issue_to_telegram(issue):
    # Initialize the Telegram bot using the API token generated by BotFather
    bot = Updater(token = config["TELEGRAM_BOT_TOKEN"], use_context = True)

    # Set the chat ID of the Telegram group where you want to post the issue content
    chat_id = config["CHAT_ID"]

    # Construct the message to send to the Telegram group
    message = f"[Issue #{issue['number']} - {issue['title']}]({issue['html_url']}) \n\n{issue['body']}"

    # Use the bot to send the message to the Telegram group
    bot.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

def check_json_data():
    with open(reminder_path, 'r') as f:
        data = json.load(f)

    # Get the current date
    today = datetime.date.today()

    # Check if today is featured in the JSON file
    if str(today) in data:
        message = f"Today's reminder: {data[str(today)]}"
    else:
        message = "No reminder for today."

    # Use the bot to send the message to the Telegram group
    chat_id = config["CHAT_ID"]
    send_message(chat_id = chat_id, message = message)

def send_message(chat_id, message):
    # Initialize the Telegram bot using the API token generated by BotFather
    bot = Updater(token = config["TELEGRAM_BOT_TOKEN"], use_context = True)

    # Use the bot to send the message to the Telegram group
    bot.bot.send_message(chat_id = chat_id, text = message, parse_mode='Markdown')

# Create a BackgroundScheduler instance
scheduler = BackgroundScheduler({'apscheduler.timezone': 'Chile/Continental'})

# Schedule the check_json_data function to run every day at 10 AM
scheduler.add_job(check_json_data, 'interval', days=1, start_date='2023-03-15 17:15:00')

if __name__ == '__main__':
    # Start the scheduler
    scheduler.start()

    # Run the Flask app
    app.run(debug=True)
