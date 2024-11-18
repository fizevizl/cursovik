import telebot
import sqlite3
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Инициализация бота
bot = telebot.TeleBot(os.getenv("BOTTOKEN"))

# Путь к базе данных
db_path = 'data.db'

@bot.message_handler(commands=['start'])
def start_message(message):
    """
    Стартовое сообщение с выбором роли
    """
    # Создаем клавиатуру для выбора роли
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Студент', callback_data='role_student'))
    markup.add(telebot.types.InlineKeyboardButton(text='Викладач', callback_data='role_teacher'))
    bot.send_message(message.chat.id, text="Вітаю! Хто Ви?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """
    Обработка обратных вызовов (выбор роли или факультета)
    """
    if call.data == "role_student":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Ви студент. Оберіть факультет:")
        offer_faculties(call.message)

    elif call.data == "role_teacher":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Ви викладач. Оберіть факультет:")
        offer_faculties(call.message)

    elif call.data.startswith("fc_"):
        faculty_id = call.data.split('_')[1]
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"Ви обрали факультет : {faculty_id}. Дякуємо за вибір!")


def offer_faculties(message):
    """
    Генерирует список факультетов из базы данных и отправляет их как inline-кнопки.
    """
    try:
        # Подключение к базе данных
        bot_db = sqlite3.connect(db_path)
        cur = bot_db.cursor()

        # Получение списка факультетов
        sql = '''
            SELECT id, name FROM faculties
        '''
        faculties = cur.execute(sql).fetchall()

        # Создание клавиатуры
        markup = telebot.types.InlineKeyboardMarkup()
        for faculty_id, faculty_name in faculties:
            markup.add(telebot.types.InlineKeyboardButton(
                text=faculty_name,
                callback_data=f"fc_{faculty_id}"
            ))

        # Отправка сообщения с кнопками
        bot.send_message(message.chat.id, text="Оберіть факультет:", reply_markup=markup)

    except sqlite3.Error as e:
        bot.send_message(message.chat.id, f"Помилка доступу до бази даних: {e}")
    finally:
        bot_db.close()


def offer_courses(message):
    """
    Генерирует список курсов из базы данных и отправляет их как inline-кнопки.
    Курсы показываются без зависимости от факультета.
    """
    try:
        # Подключение к базе данных
        bot_db = sqlite3.connect(db_path)
        cur = bot_db.cursor()

        # Получение списка всех курсов
        sql = '''
            SELECT id, name FROM courses
        '''
        courses = cur.execute(sql).fetchall()

        # Создание клавиатуры
        markup = telebot.types.InlineKeyboardMarkup()
        for course_id, course_name in courses:
            markup.add(telebot.types.InlineKeyboardButton(
                text=course_name,
                callback_data=f"co_{course_id}"
            ))

        # Отправка сообщения с кнопками
        bot.send_message(message.chat.id, text="Оберіть курс:", reply_markup=markup)

    except sqlite3.Error as e:
        bot.send_message(message.chat.id, f"Помилка доступу до бази даних: {e}")
    finally:
        bot_db.close()

# Запуск бота
bot.polling(none_stop=True)
