import telebot
from telebot import types
import requests
import random
import os
from dotenv import load_dotenv

# ================== НАСТРОЙКИ ==================
load_dotenv()


TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not TOKEN or not WEATHER_API_KEY:
    raise ValueError("Токены не найдены")

bot = telebot.TeleBot(TOKEN)

# ================== ДАННЫЕ ГОРОДОВ ==================

cities = {
    "Париж": {
        "country": "Франция",
        "lat": 48.8566,
        "lon": 2.3522,
        "area": "105 км²",
        "population": "2.1 млн",
        "photos": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/La_Tour_Eiffel_vue_de_la_Tour_Saint-Jacques%2C_Paris_ao%C3%BBt_2014_%282%29.jpg/800px-La_Tour_Eiffel_vue_de_la_Tour_Saint-Jacques%2C_Paris_ao%C3%BBt_2014_%282%29.jpg"
        ]
    },
    "Лондон": {
        "country": "Великобритания",
        "lat": 51.5074,
        "lon": -0.1278,
        "area": "1572 км²",
        "population": "9 млн",
        "photos": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/London_Skyline_%28125508655%29.jpeg/800px-London_Skyline_%28125508655%29.jpeg"
        ]
    },
    "Токио": {
        "country": "Япония",
        "lat": 35.6895,
        "lon": 139.6917,
        "area": "2194 км²",
        "population": "14 млн",
        "photos": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Skyscrapers_of_Shinjuku_2009_January.jpg/800px-Skyscrapers_of_Shinjuku_2009_January.jpg"
        ]
    },
    "Рим": {
        "country": "Италия",
        "lat": 41.9028,
        "lon": 12.4964,
        "area": "1285 км²",
        "population": "2.8 млн",
        "photos": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Colosseum_in_Rome%2C_Italy_-_April_2007.jpg/800px-Colosseum_in_Rome%2C_Italy_-_April_2007.jpg"
        ]
    },
    "Нью-Йорк": {
        "country": "США",
        "lat": 40.7128,
        "lon": -74.0060,
        "area": "783 км²",
        "population": "8.4 млн",
        "photos": [
            "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/View_of_Empire_State_Building_from_Rockefeller_Center_New_York_City_dllu_%28cropped%29.jpg/800px-View_of_Empire_State_Building_from_Rockefeller_Center_New_York_City_dllu_%28cropped%29.jpg"
        ]
    }
}

photo_replies = [
    "Классное фото 📸",
    "Красиво!",
    "Интересный кадр 😎",
    "Отличное фото!",
    "Мне нравится!"
]

# хранит выбранный пользователем город
user_city = {}


# ================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==================

def get_city_from_user(chat_id):
    """
    Возвращает выбранный пользователем город.
    Если город не выбран — возвращает None.
    """
    return user_city.get(chat_id)


def normalize_city_name(text):
    """
    Нормализует название города (приводит к правильному регистру).
    Возвращает название города если найдено, иначе None.
    """
    text_lower = text.strip().lower()
    for city_name in cities.keys():
        if city_name.lower() == text_lower:
            return city_name
    return None


def create_city_menu():
    """
    Создаёт клавиатуру с действиями для города.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Справка", "Фото", "Погода")
    markup.add("Выбрать другой город")
    return markup



def create_cities_keyboard():
    """
    Создаёт клавиатуру со списком городов.
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for city in cities.keys():
        markup.add(city)
    return markup


def send_error_message(chat_id, text):
    """
    Универсальная функция отправки сообщения об ошибке.
    """
    bot.send_message(chat_id, text)


# ================== КОМАНДЫ ==================

@bot.message_handler(commands=["start"])
def start(message):
    """
    Обработчик команды /start.
    """
    bot.send_message(
        message.chat.id,
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я — Информер путешественника 🌍\n"
        "Напиши /help чтобы увидеть список городов",
        reply_markup=create_cities_keyboard()
    )


@bot.message_handler(commands=["help"])
def help_cmd(message):
    """
    Выводит список доступных городов.
    """
    city_list = "\n".join(cities.keys())
    bot.send_message(
        message.chat.id,
        f"Доступные города:\n{city_list}\n\n"
        "Выберите город из меню ниже или введите название:",
        reply_markup=create_cities_keyboard()
    )


@bot.message_handler(commands=["bye"])
def bye(message):
    """
    Команда прощания.
    """
    bot.send_message(message.chat.id, "До свидания! ✈️")


# ================== ВЫБОР ГОРОДА ==================

@bot.message_handler(func=lambda m: m.text == "Выбрать другой город")
def change_city(message):
    """
    Позволяет выбрать другой город.
    """
    bot.send_message(
        message.chat.id,
        "Выберите город:",
        reply_markup=create_cities_keyboard()
    )


@bot.message_handler(func=lambda m: m.text in cities or normalize_city_name(m.text) is not None)
def city_menu(message):
    """
    Сохраняет выбранный город и показывает меню действий.
    """
    city = message.text if message.text in cities else normalize_city_name(message.text)

    user_city[message.chat.id] = city
    bot.send_message(
        message.chat.id,
        f"✅ Выбран город: {city}\n\n"
        "Выберите действие:",
        reply_markup=create_city_menu()
    )


# ================== СПРАВКА ==================

@bot.message_handler(func=lambda m: m.text == "Справка")
def info(message):
    """
    Выводит справочную информацию о городе.
    """
    city = get_city_from_user(message.chat.id)
    if not city:
        send_error_message(message.chat.id, "⚠️ Сначала выберите город из списка:")
        help_cmd(message)
        return

    c = cities[city]
    text = (
        f"🏙 {city}\n"
        f"🌍 Страна: {c['country']}\n"
        f"📍 Широта: {c['lat']}\n"
        f"📍 Долгота: {c['lon']}\n"
        f"📐 Площадь: {c['area']}\n"
        f"👥 Население: {c['population']}"
    )
    bot.send_message(message.chat.id, text)


# ================== ФОТО ==================

@bot.message_handler(func=lambda m: m.text == "Фото")
def send_photos(message):
    """
    Отправляет фотографии выбранного города с указанием URL.
    """
    city = get_city_from_user(message.chat.id)
    if not city:
        send_error_message(message.chat.id, "⚠️ Сначала выберите город из списка:")
        help_cmd(message)
        return

    bot.send_message(message.chat.id, "📸 Загружаю фотографии...")

    success_count = 0
    for url in cities[city]["photos"]:
        try:
            bot.send_photo(
                message.chat.id,
                url,
                caption=f"🌆 {city}\n🔗 {url}"
            )
            success_count += 1
        except Exception:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    bot.send_photo(
                        message.chat.id,
                        response.content,
                        caption=f"🌆 {city}\n🔗 {url}"
                    )
                    success_count += 1
            except Exception:
                pass

    if success_count == 0:
        send_error_message(message.chat.id, "⚠️ Не удалось загрузить фотографии. Попробуйте позже.")


# ================== ПОГОДА ==================

@bot.message_handler(func=lambda m: m.text == "Погода")
def weather(message):
    """
    Получает и выводит текущую погоду для выбранного города.
    """
    city = get_city_from_user(message.chat.id)
    if not city:
        send_error_message(message.chat.id, "⚠️ Сначала выберите город из списка:")
        help_cmd(message)
        return

    url = (
        "https://api.weatherapi.com/v1/current.json"
        f"?key={WEATHER_API_KEY}&q={city}&lang=ru"
    )

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if "error" in data:
            raise ValueError("Ошибка API")

        temp_c = data["current"]["temp_c"]
        temp_f = data["current"]["temp_f"]
        time = data["location"]["localtime"]
        condition = data["current"]["condition"]["text"]

        bot.send_message(
            message.chat.id,
            f"🌤 Погода в {city}\n"
            f"🕒 {time}\n"
            f"🌡 {temp_c}°C / {temp_f}°F\n"
            f"☁️ {condition}"
        )

    except requests.exceptions.RequestException:
        send_error_message(message.chat.id, "⚠️ Нет соединения с сервисом погоды.")
    except ValueError:
        send_error_message(message.chat.id, "⚠️ Ошибка получения данных о погоде.")
    except Exception:
        send_error_message(message.chat.id, "⚠️ Неизвестная ошибка.")


# ================== ФОТО ОТ ПОЛЬЗОВАТЕЛЯ ==================

@bot.message_handler(content_types=["photo"])
def reply_photo(message):
    """
    Реакция на фото пользователя случайной фразой.
    """
    replies = random.sample(photo_replies, k=3)
    text = "\n".join(replies)
    bot.send_message(message.chat.id, text)


# ================== ОБРАБОТКА НЕИЗВЕСТНЫХ СООБЩЕНИЙ ==================

@bot.message_handler(func=lambda m: True)
def handle_unknown(message):
    """
    Обрабатывает все неизвестные сообщения.
    """
    city = normalize_city_name(message.text)

    if city:
        city_menu(message)
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Город '{message.text}' не найден в базе.\n\n"
            "Пожалуйста, выберите город из списка ниже или введите название правильно:",
            reply_markup=create_cities_keyboard()
        )


# ================== ЗАПУСК ==================

if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(non_stop=True)
