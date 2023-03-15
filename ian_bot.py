import asyncio
import json
import os

from aiohttp import ClientSession
from flask import Flask, request
from github import Github
import telegram

dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'config.json')

with open(config_path, 'r') as f:
    config = json.load(f)

app = Flask(__name__)
telegram_bot = telegram.Bot(token=config['TELEGRAM_BOT_TOKEN'])
github = Github(config['GITHUB_TOKEN'])
repo = github.get_repo(config['GITHUB_REPO'])

async def handle_issue_event(event_data):
    issue = repo.get_issue(event_data['issue']['number'])
    group_id = get_group_for_today()

    issue_repo = ''.join(issue.url.split("https://api.github.com/repos")[1:])
    issue_url = "https://github.com/" + issue_repo

    message = f"<a href={issue_url}> <b>Issue #{issue.number} - {issue.title}</b></a> \n\n<b>Descripción:</b>\n{issue.body}\n\n<b>Link:</b>"
    
    await telegram_bot.send_message(chat_id=group_id, text=message, parse_mode='HTML', pool_timeout = 15)


def get_group_for_today():
    return config['CHAT_ID']


@app.route('/', methods=['POST'])
async def handle_webhook():
    event_type = request.headers.get('X-GitHub-Event')
    if event_type == 'issues':
        await handle_issue_event(request.json)
    return '', 204


if __name__ == '__main__':
    asyncio.run(app.run(port=5000, debug=True))
