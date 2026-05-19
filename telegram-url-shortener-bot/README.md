# Telegram URL Shortener Bot

Бот для сокращения ссылок через Telegram.

## Возможности

- Получает URL от пользователя
- Сокращает через clck.ru или goo.su
- Возвращает скрытую ссылку в формате Markdown: `[оригинал](сокращенная)`

## Установка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите бота:
```bash
python bot.py
```

## Использование

Отправьте боту любую ссылку, например:
```
https://example.com/some-very-long-url
```

Бот ответит сокращенной ссылкой:
```
🔗 [https://example.com/some-very-lo...](https://clck.ru/xxxxx)
```
