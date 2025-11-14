"""WeatherBot на Python Головний файл"""
import os
import datetime
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
WEATHER_TOKEN = os.getenv('WEATHER_TOKEN')

GREETINGS = ['Привіт', 'привіт', 'hi', 'hello', 'вітаю', 'доброго дня']


def get_weather_info(city):
    """Функція створення запиту до openweathermap та обробки відповіді"""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_TOKEN}&units=metric&lang=uk"
    response = requests.get(url)

    if response.status_code != 200:
        return "Місто не знайдено! Перевірте правильність назви."

    weather_data = response.json()
    print(weather_data)

    city_name = weather_data['name']

    current_temperature = weather_data['main']['temp']
    feels_like = weather_data['main']['feels_like']

    current_humidity = weather_data['main']['humidity']
    current_pressure = weather_data['main']['pressure']

    wind_speed = weather_data['wind']['speed']

    timezone_offset = weather_data['timezone']
    tz = datetime.timezone(datetime.timedelta(seconds=timezone_offset))

    sunrise = weather_data['sys']['sunrise']
    sunset = weather_data['sys']['sunset']

    sunrise_local = datetime.datetime.fromtimestamp(sunrise, tz)
    sunset_local = datetime.datetime.fromtimestamp(sunset, tz)

    hours_offset = timezone_offset // 3600
    minutes_offset = abs(timezone_offset % 3600) // 60
    tz_label = f"UTC {hours_offset:+03d}:{minutes_offset:02d}"

    weather_main = weather_data['weather'][0]['main']

    icons = {
        'Clear': '☀️', 'Clouds': '☁️', 'Rain': '🌧️', 'Drizzle': '🌦️',
        'Thunderstorm': '⛈️', 'Snow': '❄️', 'Mist': '🌫️', 'Fog': '🌫️',
        'Haze': '🌤️', 'Smoke': '💨', 'Dust': '🌪️'
    }
    icon = icons.get(weather_main, '🌍')

    return (f'Погода в населенному пункті {city.capitalize()} / {city_name}:\n'
            f'- Часовий пояс: {tz_label}\n'
            f'- Погода: {weather_data["weather"][0]['description'].capitalize()} {icon}\n'
            f'- Температура: {current_temperature:.1f} °C / Відчувається як: {feels_like:.1f} °C\n'
            f'- Вологість: {current_humidity} %\n'
            f'- Атмосферний тиск: {current_pressure} hPa\n'
            f'- Швидкість вітру: {wind_speed} м/с\n'
            f'- Схід Сонця: {sunrise_local.strftime("%H:%M")}\n'
            f'- Захід Сонця: {sunset_local.strftime("%H:%M")}\n')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функція старту чат-бота"""
    await update.message.reply_text(
        "👋 Привіт! Я WeatherBot. Напиши назву міста, і я дам тобі погоду!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функція відображення погоди та вітання"""
    text = update.message.text.strip().lower()

    if any(greet in text for greet in GREETINGS):
        await update.message.reply_text("👋 Привіт! Напиши назву міста, щоб дізнатися погоду.")
        return

    weather_msg = get_weather_info(text)
    await update.message.reply_text(weather_msg)


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Функція зупинки чату"""
    await update.message.reply_text(
        "👋 Дякую за спілкування! Бот зупиняється."
    )
    await context.application.stop()
    await context.application.shutdown()


def main():
    """Функція запуску коду"""
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 WeatherBot запущено!")
    app.run_polling()


if __name__ == "__main__":
    main()
