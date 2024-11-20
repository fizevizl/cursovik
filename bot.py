import telebot
import sqlite3
import os
from datetime import datetime as dt
from dotenv import load_dotenv
from constants import WEEKDAYS, LAST_WEEK_DAY

# Загружаем переменные окружения
load_dotenv()

# Инициализация бота
bot = telebot.TeleBot(os.getenv("BOTTOKEN"))

# Путь к базе данных
db_path = 'data.db'

# TODO доделать
def get_num_of_week_by_date(date):
    return 11

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

    if call.data == "role_teacher":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Ви викладач. Оберіть факультет:")
        offer_faculties(call.message)

    if call.data.startswith("fc_"):
        faculty_id = int(call.data.split('_')[1])
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"Ви обрали факультет: {faculty_id}. Оберіть курс:")
        offer_courses_by_faculty(call.message, faculty_id)

    elif call.data.startswith("course_"):
        parts = call.data.split('_')
        faculty_id = int(parts[1])  # Извлекаем faculty_id из callback_data
        course_id = int(parts[2])   # Извлекаем course_id из callback_data
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"Ви обрали курс: {course_id}. Оберіть групу:")
        offer_groups_by_course_and_faculty(call.message, faculty_id, course_id)


    elif call.data.startswith("gr_"):
        # Пользователь выбрал группу
        group_id = int(call.data.split('_')[1])
        bot.answer_callback_query(call.id)
        offer_schedule_for_group(call.message,group_id)

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


# выбор курса, Генерирует список курсов
def offer_courses_by_faculty(message, faculty_id):
    try:
        bot_db = sqlite3.connect(db_path)
        cur = bot_db.cursor()
    
        sql = '''
            SELECT id, name FROM course WHERE faculty_id = ?
        '''
        courses = cur.execute(sql, (faculty_id,)).fetchall()

        if not courses:
            bot.send_message(message.chat.id, "На жаль, немає доступних курсів для цього факультету.")
            return

        markup = telebot.types.InlineKeyboardMarkup()
        for course_id, course_name in courses:
            # Добавляем faculty_id в callback_data
            markup.add(telebot.types.InlineKeyboardButton(
                text=course_name,
                callback_data=f"course_{faculty_id}_{course_id}"
            ))

        bot.send_message(message.chat.id, text="Оберіть курс:", reply_markup=markup)

    except sqlite3.Error as e:
        bot.send_message(message.chat.id, f"Помилка доступу до бази даних: {e}")
    finally:
        bot_db.close()


# выбор групы, Генерирует список групп
def offer_groups_by_course_and_faculty(message, faculty_id, course_id):
    """
    Генерирует список групп, связанных с выбранным факультетом и курсом.
    """
    try:
        # Подключение к базе данных
        bot_db = sqlite3.connect(db_path)
        cur = bot_db.cursor()

        # SQL-запрос с двумя параметрами
        sql = '''
            SELECT id, name 
            FROM groups 
            WHERE faculty_id = ? AND course_id = ?
        '''
        groups = cur.execute(sql, (faculty_id, course_id)).fetchall()

        # Проверяем, есть ли группы
        if not groups:
            bot.send_message(message.chat.id, "На жаль, немає доступних груп для цього курсу і факультету.")
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


# Отображение расписания для выбранной группы
def offer_schedule_for_group(message, group_id):
    try:
        # Подключение к базе данных
        bot_db = sqlite3.connect(db_path)
        cur = bot_db.cursor()

        # SQL-запрос для получения расписания для группы, отсортированного по дням недели и номеру урока
        sql = '''
            SELECT day_of_week, lesson_number, subject, teacher_name, video_link
            FROM schedule
            WHERE group_id = ?
            ORDER BY day_of_week, lesson_number
        '''
        schedule = cur.execute(sql, (group_id,)).fetchall()

        if not schedule:
            bot.send_message(message.chat.id, "На жаль, для цієї групи немає доступного розкладу.")
            return

         # Создаем словарь для хранения расписания, ключи — названия дней недели
        schedule_by_day = {day: [] for day in WEEKDAYS}

        # Заполняем расписание
        for entry in schedule:
            day, lesson_number, subject, teacher, link = entry
            day_name = WEEKDAYS[day - 1]
            schedule_by_day[day_name].append((lesson_number, subject, teacher, link))

         # Формируем текст расписания
        week_num = get_num_of_week_by_date(dt.now())
        schedule_text = f"📅 *Поточний тиждень №{week_num}*\n"
        schedule_text += "  *Розклад на тиждень:*\n\n"
        for day in  WEEKDAYS[:LAST_WEEK_DAY]:  
            schedule_text += f"🔹 *{day}:*\n"
            if schedule_by_day[day]:
                for lesson_number, subject, teacher, link in sorted(schedule_by_day[day]):
                    schedule_text += f"№{lesson_number}.  {subject}\n"
                    schedule_text += f"     Викладач:  {teacher}\n"
                    schedule_text += f"     Посилання:  [Перейти до конференції]({link})\n"
            else:
                schedule_text += "  Немає занять\n"
            schedule_text += f"{'-' * 60}\n"

        # Отправляем текст пользователю
        bot.send_message(message.chat.id, schedule_text, parse_mode='Markdown', disable_web_page_preview=True)

    except sqlite3.Error as e:
        bot.send_message(message.chat.id, f"Помилка доступу до бази даних: {e}")
    finally:
        bot_db.close()

# Запуск бота
bot.polling(none_stop=True)