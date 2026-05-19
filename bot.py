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


async def shorten_clckru(url):
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


async def shorten_goosu(url):
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


async def shorten_isgd(url):
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


async def shorten_tinyurl(url):
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


async def shorten_all(url):
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


async def start(update, context):
    await update.message.reply_text(
        "Привет! Отправь мне ссылку, и я сокращу ее через несколько сервисов.\n\n"
        "Поддерживаемые сокращалки:\n"
        "- clck.ru (Яндекс)\n"
        "- goo.su\n"
        "- is.gd\n"
        "- TinyURL\n\n"
        "Просто отправь URL в сообщении."
    )


async def handle_message(update, context):
    text = update.message.text or update.message.caption or ""
    
    urls = URL_REGEX.findall(text)
    
    if not urls:
        await update.message.reply_text(
            "В сообщении не найдено ссылок. Отправьте URL для сокращения."
        )
        return
    
    all_results = []
    
    for url in urls:
        shortened_list = await shorten_all(url)
        
        if shortened_list:
            url_results = [f"{short_url} ({service})" for short_url, service in shortened_list]
            all_results.append(
                f"Оригинал: {url[:60]}{'...' if len(url) > 60 else ''}\n"
                + "\n".join(url_results)
            )
        else:
            all_results.append(f"Не удалось сократить: {url[:50]}{'...' if len(url) > 50 else ''}")
    
    result_text = "\n\n".join(all_results)
    
    if result_text:
        await update.message.reply_text(
            f"Результаты сокращения:\n\n{result_text}",
            disable_web_page_preview=True
        )


@app.route('/')
def health():
    return 'Bot is running!'


@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    asyncio.run(process_update(update))
    return 'OK'


async def process_update(update):
    await application.process_update(update)


def main():
    global application, bot
    
    application = Application.builder().token(TOKEN).build()
    bot = Bot(token=TOKEN)
    
    # Инициализация
    asyncio.run(application.initialize())
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Starting bot with webhook...")
    
    webhook_url = f"{WEBHOOK_URL}/webhook"
    asyncio.run(bot.set_webhook(url=webhook_url))
    
    app.run(host='0.0.0.0', port=PORT)


if __name__ == "__main__":
    main()
