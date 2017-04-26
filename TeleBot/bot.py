# -*- coding: utf-8 -*-
import config
import telebot

bot = telebot.TeleBot(config.token)

@bot.message_handler(content_types=['sticker'])
def send_sticker(message): # Название функции не играет никакой роли, в принципе
    user = message.date
    if message.sticker:
    	print('['+ message.from_user.username + '] : '+ message.sticker.file_id)
    	bot.send_message(message.chat.id, 'Получи назад АХАХАХАХ')
    	bot.send_sticker(message.chat.id, message.sticker.file_id)

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message): # Название функции не играет никакой роли, в принципе
    user = message.date
    if message.text:
    	print('['+ message.from_user.username + '] : '+ message.text)
    	bot.send_message(message.chat.id, 'Я знаю где ты живешь, '+ message.from_user.first_name)
    	

if __name__ == '__main__':
    bot.polling(none_stop=True)

