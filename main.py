from __future__ import print_function
import time
import telebot
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SAMPLE_SPREADSHEET_ID = '1LVfy_bz1iexDJ_GJHFYlX75DazkwVQtiazChoy4au5g'
TimerSet = False


def creatmaterial(SAMPLE_RANGE_NAME):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return
        spisok = []
        for row in values:
            spisok.append('%s' % (row[0]))
        return spisok
    except HttpError as err:
        print(err)


bot = telebot.TeleBot('5760972567:AAEKvEEkrxQryxDsccHKg9wNatwKCduScOU')


@bot.message_handler(commands=['start'])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    videomaterial = telebot.types.KeyboardButton('Видеоматериалы')
    dopmaterial = telebot.types.KeyboardButton('Дополнительные материалы')
    markup.add(videomaterial, dopmaterial)
    bot.send_message(message.chat.id,
                     f'Привет, {message.from_user.first_name}!\nЭто чат-бот по курсу "python для чайников"',
                     reply_markup=markup)
    bot.send_message(message.chat.id, 'Задайте промежуток времени через который будет отправлено напоминание об учебе в формате: часы минуты')


@bot.message_handler(content_types=['text'])
def material(message):
    global TimerSet
    if (message.text == 'Видеоматериалы'):
        videomaterial(message)
    elif (message.text == 'Дополнительные материалы'):
        dopmaterial(message)
    elif (TimerSet == False):
        chislo = message.text
        if (chislo.replace(' ','')).isdigit():
            sek = 60*60*int(chislo[:chislo.find(' ')]) + 60 * int(chislo[chislo.find(' '):])
            TimerSet = True
            bot.send_message(message.chat.id, 'Таймер успешно установлен! Спасибо!')
            pushnotification(sek, message)
    else:
        bot.send_message(message.chat.id, 'Введите коректную команду')


def videomaterial(message):
    spisok = creatmaterial('firstlist!A2:A')
    stroka = 'Список ссылок курса:\n'
    for i in range(len(spisok)):
        ssilka = spisok[i]
        stroka += f'<a href=\'{ssilka}\'> Урок {i + 1} </a> \n'
    bot.send_message(message.chat.id, stroka, parse_mode='html')


def dopmaterial(message):
    name = creatmaterial('firstlist!C2:C')
    ssilka = creatmaterial('firstlist!D2:D')
    stroka = 'Дополнительные материалы:\n'
    for i in range(len(name)):
        stroka += f'<a href=\'{ssilka[i]}\'> {name[i]} </a> \n'
    bot.send_message(message.chat.id, stroka, parse_mode='html')

def pushnotification(sek, message):
    time.sleep(sek)
    bot.send_message(message.chat.id, 'Пора учиться!!!')
    pushnotification(sek, message)


bot.polling(none_stop=True)
