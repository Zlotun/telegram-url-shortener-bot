# Деплой бота на Render.com (бесплатно)

## Шаг 1: Создать аккаунт на Render
1. Перейди на https://render.com
2. Зарегистрируйся через GitHub или email

## Шаг 2: Залить код на GitHub
1. Создай новый репозиторий на https://github.com/new
2. Загрузи файлы бота:
```bash
git init
git add .
git commit -m "initial"
git branch -M main
git remote add origin https://github.com/ТВОЙ_НИК/telegram-url-shortener.git
git push -u origin main
```

## Шаг 3: Деплой на Render
1. В Render нажми "New +" → "Web Service"
2. Подключи свой GitHub репозиторий
3. Настройки:
   - **Name**: telegram-url-shortener
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Plan**: Free
4. Добавь Environment Variable:
   - Key: `BOT_TOKEN`
   - Value: `8741430813:AAHf5_VdaU6rjFYnQYK4sq_my8rWtk4ZaOI`
5. Нажми "Create Web Service"

## Готово!
Бот будет работать 24/7. Через несколько минут он будет онлайн.

## Проверка
Напиши боту: https://t.me/ТВОЙ_БОТ
