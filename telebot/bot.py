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
    print(strr)
    return strr

def postprocessing(strr, message):
    print('came to post:'+strr)
    #if 'user_name' in strr:
    #    strr = strr.replace('user_name', message.from_user.first_name) # замена собственных имен на твое имя
    symbols = ['.', '?', '!',',']
    adventure_heroes = [' finn ', ' jake ', ' bubblegum ', ' bmo ', ' rainicorn ', ' fionna ',  ' princess ', ' king ', ' marceline ', ' lady ', ' gunther ']
    b = []
    a = strr.strip().split()
    '''if len(a) == 1:
        b = a
    else:'''
    for i in range(0, len(a)):
        if (not (' '+a[i] in b) and not (a[i] in symbols)):
            if ' '+a[i]+' ' in adventure_heroes:
                b.append(' '+ message.from_user.first_name)
            else:
                b.append(' ' + a[i])
        elif (len(b)>0 and a[i] in symbols and  not b[len(b)-1] in symbols):
            b.append(a[i])

    strr = ''.join(b)
    strr = strr[1].upper() + strr[2:]
    strr = strr.replace(' i ', ' I ')
    for i in range(0, len(strr)):
        if strr[i] in symbols[:3]:
            if i+2 < len(strr)-1:
                strr = strr[:i+2] + strr[i+2].upper() + strr[i+3:]

    return strr

# answer message with Adventure Time 
@bot.message_handler(content_types=["text"])
def answer_adventure_time(message): # Название функции не играет никакой роли, в принципе
    if message.text:
        print('['+ message.from_user.username + '] : '+ message.text)
        question = preprocessing(message.text)
        answ = execute.decode_line(sess, model, enc_vocab, rev_dec_vocab, question)
        if '_UNK' in answ:
            answ = "I don't understand you"
            bot.send_sticker(message.chat.id, dissatisfacted_stickers[random.randint(0, 10)])
        else:
            answ = postprocessing(answ, message)
        bot.send_message(message.chat.id, answ)


if __name__ == '__main__':
    bot.polling(none_stop=True)

