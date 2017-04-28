# -*- coding: utf-8 -*-
import config
import telebot
import tensorflow as tf
import sys, os  
sys.path.append("../tensorflow_chatbot")
import execute

'''
Init seq2seq model
    1. Call main from execute.py
    2. Create decode_line function that takes message as input
'''

#sess = tf.Session()
#sess, model, enc_vocab, rev_dec_vocab = execute.init_session(sess, conf='seq2seq_serve.ini')

'''
Init Telegram Bot with token from @BotFather
'''

bot = telebot.TeleBot(config.token)

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    print('['+ message.from_user.username + '] : '+ message.text)
    mess = ('Hello, it\'s Adventure Time Chatbot, if you\'re sad, please write me and I make your life better \n \n Authors: \n Ruslan Aminev, \n Alina Belyaeva, \n Violetta Mishechkina, \n Vitaliy Reut,  \n code: https://github.com/rus8/infoemhack-chatbot')
    bot.send_message(message.chat.id, mess)
    if message.text == '/start':
        bot.send_sticker(message.chat.id, 'CAADAgADWgcAAlOx9wOIad-ZBUtESwI')

@bot.message_handler(content_types=['sticker'])
def repeat_sticker(message): # Название функции не играет никакой роли, в принципе
    user = message.date
    if message.sticker:
    	print('['+ message.from_user.username + '] : '+ message.sticker.file_id)
    	bot.send_message(message.chat.id, 'Получи назад АХАХАХАХ')
    	bot.send_sticker(message.chat.id, message.sticker.file_id)

@bot.message_handler(content_types=["text"])
def say_I_know_your_location(message): # Название функции не играет никакой роли, в принципе
    user = message.date
    if message.text:
    	print('['+ message.from_user.username + '] : '+ message.text)
    	bot.send_message(message.chat.id, 'Я знаю где ты живешь, '+ message.from_user.first_name)

# answer message with Adventure Time 
@bot.message_handler(content_types=["text"])
def answer_adventure_time(message): # Название функции не играет никакой роли, в принципе
    user = message.date
    if message.text:
        print('['+ message.from_user.username + '] : '+ message.text)
        mess = ''
        #mess = execute.decode_line(sess, model, enc_vocab, rev_dec_vocab, message.text)
        if 'user_name' in mess:
            print('need to replace name')
        bot.send_message(message.chat.id, 'Я знаю где ты живешь, '+ mess)


if __name__ == '__main__':
    bot.polling(none_stop=True)

