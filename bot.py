import request_list
from config import *
import telebot
from image_gen import *
from io import BytesIO
from pathlib import Path
import json
from apscheduler.schedulers.background import BackgroundScheduler

bot = telebot.TeleBot(token=bot_token)
scheduler = BackgroundScheduler()
scheduler.start()

SUB_FILE = Path("subscriptions.json")
user_context = {}


def load_subscribers() -> dict:
    try:
        if not SUB_FILE.exists():
            return {}
        with open(SUB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return json.loads(content) if content else {}
    except json.JSONDecodeError:
        return {}


def save_subscribers(data: dict):
    with open(SUB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def send_forecast(chat_id: int, lang: str, lat: float, lon: float):
    req_list_obj = request_list.Requests(api_key)
    curr = req_list_obj.current_weather(lon, lat, lang)
    forecast = req_list_obj.five_days_forecast(lon, lat, lang)[:10]
    gen = ImageGenerator(curr, lang=lang)
    img = gen.daily_forecast_img(forecast)
    bio = BytesIO()
    img.save(bio, format="PNG")
    bio.seek(0)
    bot.send_photo(chat_id, bio)


def scheduled_forecast_job():
    subs = load_subscribers()
    for chat_id, info in subs.items():
        send_forecast(int(chat_id), info["lang"], info["lat"], info["lon"])


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("RU🇷🇺", "EN🇬🇧")
    bot.send_message(message.chat.id, 'Chose your language', reply_markup=markup)


@bot.message_handler(content_types='text')
def message_handler(message):
    chat_id = message.chat.id
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    text = message.text
    user = user_context.get(chat_id, {})
    lang = user.get("lang", "ru")

    subs = load_subscribers()

    if text == "RU🇷🇺":
        user_context[chat_id] = {"lang": "ru"}
        markup.add(telebot.types.KeyboardButton("Поделиться локацией🌐", request_location=True))
        bot.send_message(chat_id, "Привет!👋\nГде ты находишься?🗺️", reply_markup=markup)
        return

    if text == "EN🇬🇧":
        user_context[chat_id] = {"lang": "en"}
        markup.add(telebot.types.KeyboardButton("Send my location🌐", request_location=True))
        bot.send_message(chat_id, "Hi!👋\nWhere are you now?🗺️", reply_markup=markup)
        return

    user = user_context.get(chat_id)
    if not user or "lat" not in user or "lon" not in user:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("RU🇷🇺", "EN🇬🇧")
        bot.send_message(message.chat.id, 'Chose your language', reply_markup=markup)
        return

    req_list_obj = request_list.Requests(api_key)
    lang = user["lang"]
    lat, lon = user["lat"], user["lon"]

    if text in ["Погода сейчас☀️", "Weather now☀️"]:
        curr_weather = req_list_obj.current_weather(lon, lat, lang)
        img = ImageGenerator(curr_weather, lang=lang).curr_weather_img()
        bio = BytesIO()
        img.save(bio, "PNG")
        bio.seek(0)
        bot.send_photo(chat_id, bio, caption="Погода сейчас☀️" if lang == 'ru' else 'Forecast for now☀️')

    elif text in ["Прогноз на сутки⏳", "Today forecast⏳"]:
        curr_weather = req_list_obj.current_weather(lon, lat, lang)
        forecast = req_list_obj.five_days_forecast(lon, lat, lang)[:10]
        img = ImageGenerator(curr_weather, lang=lang).daily_forecast_img(forecast)
        bio = BytesIO()
        img.save(bio, "PNG")
        bio.seek(0)
        bot.send_photo(chat_id, bio, caption="Прогноз на сутки⏳" if lang == 'ru' else 'Today forecast⏳')

    elif text in ["Прогноз на 5 дней🗓️️", "5 days forecast🗓️️"]:
        curr_weather = req_list_obj.current_weather(lon, lat, lang)
        forecast = req_list_obj.five_days_forecast(lon, lat, lang)[:40]
        img = ImageGenerator(curr_weather, lang=lang).five_days_img(forecast)
        bio = BytesIO()
        img.save(bio, "PNG")
        bio.seek(0)
        bot.send_photo(chat_id, bio, caption="Прогноз на 5 дней🗓️️" if lang == 'ru' else '5 days forecast🗓️')

    elif text in ["Уведомления🔔", "Notifications🔔"]:
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Подписаться ✅", "Отписаться ❌") if lang == "ru" else markup.add("Follow ✅", "Unfollow ❌")
        bot.send_message(chat_id,
                         "Вы можете включить или выключить уведомления:" if lang == "ru"
                         else "You can follow/unfollow daily messages:",
                         reply_markup=markup)

    elif message.text in ["Подписаться ✅", "Follow ✅"]:
        if "lat" in user and "lon" in user:
            subs[str(chat_id)] = {"lang": lang, "lat": user["lat"], "lon": user["lon"]}
            save_subscribers(subs)
            bot.send_message(chat_id, "✅ Подписка оформлена!" if lang == "ru" else "✅ Subscribed!")
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            if lang == "ru":
                markup.add("Погода сейчас☀️", "Прогноз на сутки⏳", "Прогноз на 5 дней🗓️️",
                           "Уведомления🔔", "Обо мнеℹ️")
            else:
                markup.add("Weather now☀️", "Today forecast⏳", "5 days forecast🗓️️",
                           "Notifications🔔", "Aboutℹ️")
            bot.send_message(chat_id, "Вы в главном меню." if lang == "ru" else "Back to main menu.",
                             reply_markup=markup)

        else:
            bot.send_message(chat_id,
                             "Сначала отправьте геолокацию." if lang == "ru" else "Please send your location first.")

    elif message.text in ["Отписаться ❌", "Unfollow ❌"]:
        if str(chat_id) in subs:
            del subs[str(chat_id)]
            save_subscribers(subs)
        bot.send_message(chat_id, "❌ Подписка отменена!" if lang == "ru" else "❌ Unsubscribed!")
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        if lang == "ru":
            markup.add("Погода сейчас☀️", "Прогноз на сутки⏳", "Прогноз на 5 дней🗓️️",
                       "Уведомления🔔", "Обо мнеℹ️")
        else:
            markup.add("Weather now☀️", "Today forecast⏳", "5 days forecast🗓️️",
                       "Notifications🔔", "Aboutℹ️")
        bot.send_message(chat_id, "Вы в главном меню." if lang == "ru" else "Back to main menu.", reply_markup=markup)
    elif message.text in ["Обо мнеℹ️", "Aboutℹ️"]:
        about_text = (
            "Я — бот прогноза погоды ☀️\n\n"
            "📍 Определю ваш город по геолокации\n"
            "📷 Отправлю картинку с текущей погодой\n"
            "📆 Покажу прогноз на сегодня и на 5 дней\n"
            "🔔 Могу присылать прогноз на день каждое утро\n\n"
            "🧑‍💻 По всем вопросам и предложениям: @ad_astraa1\n"
            "🤖 Мой репозиторий на Github: https://github.com/grigoscope/weatherly"
            if lang == "ru" else
            "I’m a weather forecast bot ☀️\n\n"
            "📍 I’ll detect your city by location\n"
            "📷 I’ll send you an image with current weather\n"
            "📆 I can show you today’s and 5-day forecast\n"
            "🔔 I can send you forecast every morning\n\n"
            "‍💻 Feedback: @ad_astraa1\n"
            "🤖 My Github repo: https://github.com/grigoscope/weatherly"
        )
        bot.send_message(chat_id, about_text)


@bot.message_handler(content_types=['location'])
def location_handler(message):
    chat_id = message.chat.id
    longitude = message.location.longitude
    latitude = message.location.latitude

    if chat_id not in user_context:
        user_context[chat_id] = {}

    user_context[chat_id].update({"lat": latitude, "lon": longitude})
    lang = user_context[chat_id].get("lang", "ru")

    req_list_obj = request_list.Requests(api_key)
    if req_list_obj.find_city(longitude, latitude, lang):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        if lang == "ru":
            markup.add("Погода сейчас☀️", "Прогноз на сутки⏳", "Прогноз на 5 дней🗓️️",
                       "Уведомления🔔", "Обо мнеℹ️")
            bot.send_message(chat_id, "Отлично! Ожидайте прогноза!☂️", reply_markup=markup)
        else:
            markup.add("Weather now☀️", "Today forecast⏳", "5 days forecast🗓️️",
                       "Notifications🔔", "Aboutℹ️")
            bot.send_message(chat_id, "Awesome! Look forward to the forecast!☂️", reply_markup=markup)
    else:
        bot.send_message(chat_id, "Мы вас не нашли😢" if lang == "ru" else "We can't find you😢")
