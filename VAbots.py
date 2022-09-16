import cv2
from cv2 import*
import telebot
from telebot import *
import pafy
import os
import qrcode
import mysql.connector
from pyzbar.pyzbar import *


db = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="vabot"
)

cursor = db.cursor()
cursor.execute(
    """
     CREATE TABLE IF NOT EXISTS Images(
          id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          id_tele INT NOT NULL,
          Photo LONGBLOB
     )
     """
)

api = "5582599374:AAHreQoNCtyAPjwhCpe_xUR2fqS8tAQj3Os"
bot = telebot.TeleBot(api, parse_mode=None)


@bot.message_handler(commands=['start'])
def welcome(message):
    nama = message.from_user.first_name
    nama_akhir = message.from_user.last_name
    bot.send_message(message.chat.id, 'Hallo {} {} selamat datang :)'.format(
        nama, nama_akhir))
    menuHome(message)


def menuHome(message):
    # Membalas Pesan
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    item1 = types.KeyboardButton('Donwloader YT')
    item2 = types.KeyboardButton('Code QR')
    item3 = types.KeyboardButton('Lainnya')
    itemH = types.KeyboardButton('Help')
    markup.row(item1, item2)
    markup.row(item3)
    markup.row(itemH)
    bot.send_message(message.chat.id, "Silahkan masukkan pilihan anda : ",
                     reply_markup=markup)
    bot.register_next_step_handler(message, opsiStart)


def opsiStart(message):
    opsi = message.text
    if opsi == 'Donwloader YT':
        DownloaderYT(message)
    elif opsi == 'Code QR':
        menuCodeQr(message)
    elif opsi == 'Lainnya':
        cek(message)
    elif opsi == 'Help':
        send_welcome(message)
    else:
        bot.send_message(
            message.chat.id, "Mohon masukkan pilihan dengan benar")
        menuHome(message)


@bot.message_handler(commands=['lainnya'])
def cek(message):
    bot.send_message(message.chat.id, "Silahkan kirim Code QR : ")
    bot.register_next_step_handler(message, tester)


def tester(message):
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)

    with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)


@bot.message_handler(commands=['help'])
def send_welcome(message):
    nama = message.from_user.first_name

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    homeButton = types.KeyboardButton('Kembali')
    markup.row(homeButton)
    bot.reply_to(message, f''' 
    Help

Hi {nama}, my name is VA Bot. I am a bot that has various features that you may need, here I will help you to use my features.
    
Helpful commands:
- /start : To start the bot
- /help : I'll tell you more about myself
- /mp4 : A feature that has a function to download videos on YouTube in Mp4 format
- /mp3 : A feature that has a function to download videos on YouTube which will be converted to Mp3
- /createQR : Feature to create QR code
    ''', reply_markup=markup)
    bot.register_next_step_handler(message, backHome)


def backHome(message):
    opsi = message.text
    print(message.text)
    if opsi == 'Kembali':
        menuHome(message)


@bot.message_handler(commands=['id'])
def action(message):
    no_id = message.from_user.id
    username = message.from_user.username
    bot.reply_to(message, '''
id = {}
username = {}
    '''.format(no_id, username))


@bot.message_handler(commands=['DownloaderYT'])
def DownloaderYT(message):
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    item1 = types.KeyboardButton('mp4')
    item2 = types.KeyboardButton('mp3')
    item3 = types.KeyboardButton('back')
    markup.row(item1, item2)
    markup.row(item3)
    bot.reply_to(
        message, "Silahkan masukkan pilihan anda : ", reply_markup=markup)
    bot.register_next_step_handler(message, opsiDownloadYT)


def opsiDownloadYT(message):
    opsi = message.text
    if opsi == 'mp4':
        receive_mp4(message)
    elif opsi == 'mp3':
        receive_mp3(message)
    elif opsi == 'back':
        menuHome(message)
    else:
        bot.send_message(
            message.chat.id, "Mohon masukkan pilihan dengan benar")
        DownloaderYT(message)


@bot.message_handler(commands=['mp4'])
def receive_mp4(message):
    bot.reply_to(message, "Masukkan URL youtube yang akan di download : ")
    bot.register_next_step_handler(message, send)


def send(message):
    try:
        bot.send_message(message.chat.id, "Bot sedang mencari file...")
        url = pafy.new(message.text.replace('/mp4 ', ''))
        bot.send_message(message.chat.id, url.title)
        bot.send_message(
            message.chat.id, "Silahkan tunggu beberapa saat bot sedang memprosesnya...")
        hasil = url.getbest()
        hasil.download()

        for i in os.listdir():
            if i.endswith('.mp4'):
                print(i)
                bot.send_video(message.chat.id, open(i, 'rb'))
                os.remove(i)
        menuHome(message)
    except:
        bot.send_message(message.chat.id, "Mohon masukkan url dengan benar!")
        DownloaderYT(message)


@bot.message_handler(commands=['mp3'])
def receive_mp3(message):
    bot.reply_to(
        message, "Masukkan URL youtube yang akan di convert menjadi mp3 : ")
    bot.register_next_step_handler(message, send_mp3)


def send_mp3(message):
    try:
        bot.send_message(message.chat.id, "Bot sedang mencari file...")
        url = pafy.new(message.text.replace('/mp3 ', ''))
        bot.send_message(message.chat.id, url.title)
        bot.send_message(
            message.chat.id, "Silahkan tunggu beberapa saat bot sedang memprosesnya...")
        hasil = url.getbestaudio()
        hasil.download(f'{url.title}.mp3')

        for i in os.listdir():
            if i.endswith('.mp3'):
                print(i)
                bot.send_audio(message.chat.id, open(i, 'rb'))
                os.remove(i)
        menuHome(message)
    except:
        bot.send_message(message.chat.id, "Mohon masukkan url dengan benar!")
        DownloaderYT(message)


@bot.message_handler(commands=['CodeQr'])
def menuCodeQr(message):
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    item1 = types.KeyboardButton('Create QR Code')
    item2 = types.KeyboardButton('Read QR Code')
    item3 = types.KeyboardButton('Back')
    markup.row(item1, item2)
    markup.row(item3)
    bot.reply_to(
        message, "Silahkan masukkan pilihan anda : ", reply_markup=markup)
    bot.register_next_step_handler(message, opsiQR)


def opsiQR(message):
    opsi = message.text
    if opsi == 'Create QR Code':
        createQR(message)
    elif opsi == 'Read QR Code':
        readQR(message)
    elif opsi == 'Back':
        menuHome(message)
    else:
        print("error")


@bot.message_handler(commands=['createQR'])
def createQR(message):
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True)
    item1 = types.KeyboardButton('back')
    markup.row(item1)
    bot.reply_to(message, "Silahkan masukkan link atau text :",
                 reply_markup=markup)
    bot.register_next_step_handler(message, processQR)


def processQR(message):
    data = message.text
    if data == 'back':
        menuCodeQr(message)
    else:
        id_ = message.from_user.id
        qr_code = qrcode.make(data)
        qr_code.save(f'{id_}.png')

        for i in os.listdir():
            if i == (f'{id_}.png'):
                print(i)
                bot.send_document(message.chat.id, open(i, 'rb'))
                os.remove(i)
        menuHome(message)


@bot.message_handler(commands=['readQR'])
def readQR(message):
    bot.send_message(message.chat.id, "Silahkan kirim Code QR : ")
    bot.register_next_step_handler(message, processRead)


def processRead(message):
    try:
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        id = message.from_user.id
        file_name = f'{id}.png'
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        detector = cv2.QRCodeDetector()

        reval, point, s_qr = detector.detectAndDecode(cv2.imread(file_name))
        bot.reply_to(message, reval)
        menuHome(message)
    except:
        print('error')
        menuCodeQr(message)


while True:
    try:
        print("Bot Telah Dijalankan")
        bot.polling()
    except:
        print('error')
        pass


# def youtube(message):
    # bot.reply_to(message, "Masukkan URL youtube")
    # yt[message.chat.id] = {}
    # bot.register_next_step_handler(message, link)


# def link(message):
    # yt[message.chat.id]['link'] = message.text
    # bot.reply_to(message, "link {}".format(yt[message.chat.id]['link']))

    # link = yt[message.chat.id]['link']

    # url = pafy.new(message.text.replace('/mp4 ', ''))
    # bot.send_message(message.chat.id, url.title)
    # bot.send_message(message.chat.id, "Harap tunggu beberapa saat")
    # hasil = url.getbest()
    # hasil.download()
    # video = YouTube(link)
    # video = YouTube('https://www.youtube.com/watch?v=taYxyE34jjY')
    # stream = video.streams.get_highest_resolution()
