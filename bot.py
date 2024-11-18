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

# функция для начала и выбора роли
@bot.message_handler(commands=['start'])
def start_message(message, callback_data=None):

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Студент', callback_data='role_student'))
    markup.add(telebot.types.InlineKeyboardButton(text='Викладач', callback_data='role_teacher'))
    bot.send_message(message.chat.id, text="Вітаю! Хто Ви?", reply_markup=markup)


# обработка обратных вызовов
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):

    print('***\t', call.data)
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
        offer_courses(call.message)

    elif call.data.startswith("co_"):
        # Пользователь выбрал курс
        course_id = call.data.split('_')[1]
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"Ви обрали курс: {course_id}. Дякуємо за вибір!")
        offer_groups(call.message)

# выбор факультета, Генерирует список факультетов из базы данных и отправляет их как inline-кнопки.
def offer_faculties(message):
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


# выбор курса, Генерирует список всех курсов из базы данных и отправляет их как inline-кнопки. 
def offer_courses(message):
    try:
        # Подключение к базе данных
        bot_db = sqlite3.connect(db_path)
        cur = bot_db.cursor()

        # Получение списка всех курсов
        sql = '''
            SELECT id, name FROM course
        '''
        courses = cur.execute(sql).fetchall()

        # Проверяем, есть ли курсы
        if not courses:
            bot.send_message(message.chat.id, "На жаль, немає доступних курсів.")
            return

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


# выбор групы, Генерирует список всех групп из базы данных и отправляет их как inline-кнопки.
def offer_groups(message):
    try:
        # Подключение к базе данных
        bot_db = sqlite3.connect(db_path)
        cur = bot_db.cursor()

        # Получение списка всех групп
        sql = '''
            SELECT id, name FROM groups
        '''
        groups = cur.execute(sql).fetchall()

        # Проверяем, есть ли группы
        if not groups:
            bot.send_message(message.chat.id, "На жаль, немає доступних груп.")
            return

        # Создание клавиатуры
        markup = telebot.types.InlineKeyboardMarkup()
        for group_id, group_name in groups:
            markup.add(telebot.types.InlineKeyboardButton(
                text=group_name,
                callback_data=f"gr_{group_id}"
            ))

        # Отправка сообщения с кнопками
        bot.send_message(message.chat.id, text="Оберіть групу:", reply_markup=markup)

    except sqlite3.Error as e:
        bot.send_message(message.chat.id, f"Помилка доступу до бази даних: {e}")
    finally:
        bot_db.close()


# Запуск бота
bot.polling(none_stop=True)
