import aiohttp
import asyncio
import json
import os
import hmac
import hashlib
import telegram
from aiohttp import web


dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'config.json')

with open(config_path, 'r') as f:
    config = json.load(f)

TELEGRAM_TOKEN = config["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = config["CHAT_ID"]
GITHUB_SECRET = config["GITHUB_SECRET"]

app = web.Application()

async def handle_webhook(request):
    body = await request.json()
    signature = request.headers.get('X-Hub-Signature')
    if not verify_signature(signature, body):
        return web.Response(status=401)

    event_type = request.headers.get('X-GitHub-Event')
    if event_type == 'issues':
        issue = body['issue']
        message = f'New issue posted on {issue["repository"]["name"]}: {issue["title"]} ({issue["html_url"]})'
        await send_telegram_notification(message)
    return web.Response(status=200)

def verify_signature(signature, body):
    digest = hmac.new(GITHUB_SECRET.encode(), body, hashlib.sha1).hexdigest()
    return hmac.compare_digest(f'sha1={digest}', signature)

async def send_telegram_notification(message):
    bot = telegram.Bot(token = TELEGRAM_TOKEN)
    bot.send_message(chat_id = TELEGRAM_CHAT_ID, text = message)

if __name__ == '__main__':
    app = web.Application()
    app.router.add_post('/webhook', handle_webhook)
    web.run_app(app)