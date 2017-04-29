# -*- coding: utf-8 -*-
import config
import telebot
import tensorflow as tf
import sys, os  
import random
sys.path.append("../tf_chatbot")
import execute

'''
Init seq2seq model
    1. Call main from execute.py
    2. Create decode_line function that takes message as input
'''

sess = tf.Session()
sess, model, enc_vocab, rev_dec_vocab = execute.init_session(sess, conf='../tf_chatbot/seq2seq.ini')

'''
Init Telegram Bot with token from @BotFather
'''

bot = telebot.TeleBot(config.token)

dissatisfacted_stickers = ['CAADAgADegcAAlOx9wPdYZQdsjeJ1QI', 'CAADAgADfAcAAlOx9wPFib3kWlKcTgI', 'CAADAgADZAcAAlOx9wMOPOsobSvsAwI',
                            'CAADAgADcAcAAlOx9wPvD5GVsIF2awI', 'CAADAgADZgcAAlOx9wP_l3UsB3QgqgI', 'CAADAgADawADCcWmA1VTC_qsRfCDAg', 'CAADAgADcwADCcWmAyzf617bF45OAg',
                            'CAADAgADZAADCcWmAzEQWoj97GwoAg', 'CAADAgADVgADCcWmA3t13Jtwo52vAg', 'CAADAgADdAADCcWmA7q-xty48LXYAg', 'CAADAgADUwADCcWmA2mcT2RpHaCuAg']

replaces = {"n\'t": " not", "\'ll": " will", "\'re": " are", " he\'s": " he is", " she\'s": " she is", " it\'s": " it is", " there\'s": " there is", 
            "\'em": " them", "i\'m": "i am", " who\'s": " who is", " what\'s": " what is", " that\'s": " that is"}

@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    print('['+ message.from_user.username + '] : '+ message.text)
    mess = ('Hello, it\'s Adventure Time Chatbot, if you\'re sad, please write me and I make your life better \n \n Authors: \n Ruslan Aminev, \n Alina Belyaeva, \n Violetta Mishechkina, \n Vitaliy Reut,  \n code: https://github.com/rus8/infoemhack-chatbot')
    bot.send_message(message.chat.id, mess)
    if message.text == '/start':
        bot.send_sticker(message.chat.id, 'CAADAgADWgcAAlOx9wOIad-ZBUtESwI')

@bot.message_handler(content_types=['sticker'])
def repeat_sticker(message): # Название функции не играет никакой роли, в принципе
    if message.sticker:
    	print('['+ message.from_user.username + '] : '+ message.sticker.file_id)
    	bot.send_message(message.chat.id, 'Получи назад АХАХАХАХ')
    	bot.send_sticker(message.chat.id, message.sticker.file_id)

'''@bot.message_handler(content_types=["text"])
def say_I_know_your_location(message): # Название функции не играет никакой роли, в принципе
    if message.text:
    	print('['+ message.from_user.username + '] : '+ message.text)
    	bot.send_message(message.chat.id, 'Я знаю где ты живешь, '+ message.from_user.first_name)'''

def preprocessing(strr):
    strr = strr.lower()
    for key, value in replaces.items():
        #print(key)
        if key in strr:
            strr = strr.replace(key, value)
        elif key[0]==' ' and strr.find(key[1:])==0:
            strr = strr.replace(key[1:], value[1:])
    return strr

# answer message with Adventure Time 
@bot.message_handler(content_types=["text"])
def answer_adventure_time(message): # Название функции не играет никакой роли, в принципе
    if message.text:
        print('['+ message.from_user.username + '] : '+ message.text)
        mess = 'hello, dear user_name, i like you user_name'
        question = preprocessing(message.text)      
        mess = execute.decode_line(sess, model, enc_vocab, rev_dec_vocab, question)
        if '_UNK' in mess:
            mess = 'I don\'t understand you'
            bot.send_sticker(message.chat.id, dissatisfacted_stickers[random.randint(0, 10)])        
        if 'user_name' in mess:
            mess = mess.replace('user_name', message.from_user.first_name)
        mess = mess[0].upper()+mess[1:]
        mess = mess.replace(' i ', ' I ')
        bot.send_message(message.chat.id, mess)


if __name__ == '__main__':
    bot.polling(none_stop=True)

