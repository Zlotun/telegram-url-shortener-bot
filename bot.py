import os
import re
import logging
import aiohttp
import asyncio
from urllib.parse import quote
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN", "8741430813:AAHf5_VdaU6rjFYnQYK4sq_my8rWtk4ZaOI")
WEBHOOK_URL = os.getenv("RENDER_EXTERNAL_URL", "")
PORT = int(os.getenv("PORT", 10000))

URL_REGEX = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)

app = Flask(__name__)


async def shorten_clckru(url: str):
    try:
        encoded_url = quote(url, safe='')
        api_url = f"https://clck.ru/--?url={encoded_url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    result = await response.text()
                    if result and result.startswith('http'):
                        return (result.strip(), "Яндекс")
        return None
    except Exception as e:
        logger.error(f"clck.ru error: {e}")
        return None


async def shorten_goosu(url: str):
    try:
        api_url = "https://goo.su/api/shorten"
        payload = {"url": url}
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and data.get('short_url'):
                        return (data['short_url'], "goo.su")
        return None
    except Exception as e:
        logger.error(f"goo.su error: {e}")
        return None


async def shorten_isgd(url: str):
    try:
        encoded_url = quote(url, safe='')
        api_url = f"https://is.gd/create.php?format=simple&url={encoded_url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    result = await response.text()
                    if result and result.startswith('http'):
                        return (result.strip(), "is.gd")
        return None
    except Exception as e:
        logger.error(f"is.gd error: {e}")
        return None


async def shorten_tinyurl(url: str):
    try:
        encoded_url = quote(url, safe='')
        api_url = f"https://tinyurl.com/api-create.php?url={encoded_url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    result = await response.text()
                    if result and result.startswith('http'):
                        return (result.strip(), "TinyURL")
        return None
    except Exception as e:
        logger.error(f"tinyurl error: {e}")
        return None


async def shorten_all(url: str):
    shorteners = [shorten_clckru, shorten_goosu, shorten_isgd, shorten_tinyurl]
    results = []
    
    for shortener in shorteners:
        try:
            result = await shortener(url)
            if result and result[0] not in [r[0] for r in results]:
                results.append(result)
        except Exception as e:
            logger.error(f"Shortener error: {e}")
            continue
    
    return results


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Отправь мне ссылку, и я сокращу её через несколько сервисов.\n\n"
        "📋 Поддерживаемые сокращалки:\n"
        "• clck.ru (Яндекс)\n"
        "• goo.s
