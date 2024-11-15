import telebot
import sqlite3
import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

bot = telebot.TeleBot(os.getenv("BOTTOKEN"))

@bot.message_handler(commands=['start'])
def start_message(message, callback_data=None):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Студент', callback_data='s'))
    markup.add(telebot.types.InlineKeyboardButton(text='Викладач', callback_data='v'))
    bot.send_message(message.chat.id, text="Bітаю! Хто Ви?", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "s":
        bot.send_message(call.message.chat.id, "Ви студент")
    elif call.data == "v":
        bot.send_message(call.message.chat.id, "Ви викладач")
    # Уведомление Telegram о завершении обработки callback
    bot.answer_callback_query(call.id)


@bot.message_handler(commands=['start'])
def start_message(message, callback_data=None):
    bot_db = sqlite3.connect('data.db')
    markup = telebot.types.InlineKeyboardMarkup()

    cur = bot_db.cursor()
    sql = '''
            select id, name from faculties
        '''
    faculties = cur.execute(sql)
    for id, nm in faculties:
        markup.add(telebot.types.InlineKeyboardButton(text=nm, callback_data=f"fc_{id}"))
    
    bot.send_message(message.chat.id, text="Bітаю! Ви студент, або викладач?", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def lalala(message):
    bot.send_message(message.chat.id, message.text) 
    
bot.polling(none_stop=True)