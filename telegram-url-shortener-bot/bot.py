import os
import re
import logging
import aiohttp
from urllib.parse import quote
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN", "8741430813:AAHf5_VdaU6rjFYnQYK4sq_my8rWtk4ZaOI")

URL_REGEX = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)


async def shorten_clckru(url: str) -> str | None:
    """Shorten URL using clck.ru"""
    try:
        encoded_url = quote(url, safe='')
        api_url = f"https://clck.ru/--?url={encoded_url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=10) as response:
                if response.status == 200:
                    result = await response.text()
                    if result and result.startswith('http'):
                        return result.strip()
        return None
    except Exception as e:
        logger.error(f"clck.ru error: {e}")
        return None


async def shorten_goosu(url: str) -> str | None:
    """Shorten URL using goo.su"""
    try:
        api_url = "https://goo.su/api/shorten"
        payload = {"url": url}
        async with aiohttp.ClientSession() as session:
            async with session.post(api_url, json=payload, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if data and data.get('short_url'):
                        return data['short_url']
        return None
    except Exception as e:
        logger.error(f"goo.su error: {e}")
        return None


async def shorten_url(url: str) -> str | None:
    """Try multiple shorteners, return first successful"""
    shorteners = [shorten_clckru, shorten_goosu]
    
    for shortener in shorteners:
        try:
            result = await shortener(url)
            if result:
                return result
        except Exception as e:
            logger.error(f"Shortener error: {e}")
            continue
    
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message"""
    await update.message.reply_text(
        "👋 Привет! Отправь мне ссылку, и я сокращу её.\n\n"
        "Поддерживаемые сокращалки:\n"
        "• clck.ru\n"
        "• goo.su\n\n"
        "Просто отправь URL в сообщении."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages with URLs"""
    text = update.message.text or update.message.caption or ""
    
    urls = URL_REGEX.findall(text)
    
    if not urls:
        await update.message.reply_text(
            "❌ В сообщении не найдено ссылок. Отправьте URL для сокращения."
        )
        return
    
    processing_msg = await update.message.reply_text("⏳ Сокращаю ссылки...")
    
    results = []
    for url in urls:
        shortened = await shorten_url(url)
        if shortened:
            results.append(f"🔗 [{url[:50]}{'...' if len(url) > 50 else ''}]({shortened})")
        else:
            results.append(f"❌ Не удалось сократить: {url[:50]}{'...' if len(url) > 50 else ''}")
    
    result_text = "\n\n".join(results)
    
    await processing_msg.delete()
    
    if results:
        await update.message.reply_text(
            f"✅ Результат:\n\n{result_text}",
            parse_mode='Markdown',
            disable_web_page_preview=True
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    logger.error(f"Update {update} caused error {context.error}")


def main():
    """Start the bot"""
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.add_error_handler(error_handler)
    
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
