import telebot
import config0

bot = telebot.TeleBot(config0.token)

bot.message_handler(commands=['start'])
def start_message(message, callback_data=None):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='Студент', callback_data='s'))
    markup.add(telebot.types.InlineKeyboardButton(text='Викладач', callback_data='v'))
    bot.send_message(message.chat.id, text="Bітаю! Хто Ви?", reply_markup=markup)

@bot.message_handler(content_types=['text'])
def lalala(message):
    bot.send_message(message.chat.id, message.text) 
    
bot.polling(none_stop=True)