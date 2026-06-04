import telebot
from telebot import apihelper
import json
import time

# Настройка прокси для обхода ограничений PythonAnywhere
apihelper.proxy = {'https': 'https://tproxy.dev:443'}

# Вставьте сюда ВАШ токен (внимательно!)
TOKEN = '8992964135:AAE2DK5G8GtwS9BQPgVEky4eQFH2PVPD2F0'
bot = telebot.TeleBot(TOKEN)

# Глобальная переменная для хранения состояния компании
company_data = {}

def keyboard(message):
    username = message.from_user.username
    chat_id = message.chat.id
    try:
        with open('data.json', encoding='utf-8') as json_file:
            data = json.load(json_file)
    except:
        bot.send_message(chat_id, "Ошибка: файл data.json не найден или поврежден.")
        return

    markup = telebot.types.InlineKeyboardMarkup()
    for item in data:
        checkuser(item, username, chat_id, data)
        markup.add(telebot.types.InlineKeyboardButton(text=item["company"], callback_data=item["company"]))
    
    bot.send_message(chat_id, "Выберите компанию:", reply_markup=markup)

def checkuser(company_data, username, chat_id, data):
    for contact in company_data["contacts"]:
        if contact["username"] == username:
            if "chat_id" in contact and contact["chat_id"] == '':
                contact["chat_id"] = chat_id
                with open('data.json', 'w', encoding='utf-8') as json_file:
                    json.dump(data, json_file, sort_keys=True, indent=4)
            break

def send_message_to_contacts(message_text, contacts_list):
    for contact in contacts_list:
        if "chat_id" in contact and contact["chat_id"] != '':
            try:
                bot.send_message(contact["chat_id"], message_text)
            except Exception as e:
                print(f"Ошибка отправки: {e}")

@bot.message_handler(commands=['start', 'select'])
def handle_start_command(message):
    keyboard(message)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    global company_data
    if call.data == "/start":
        keyboard(call.message)
        return

    with open('data.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
        for item in data:
            if item["company"] == call.data:
                company_data = item
                break
    
    cancelbutton = telebot.types.InlineKeyboardMarkup()
    cancelbutton.add(telebot.types.InlineKeyboardButton(text="Отмена", callback_data="/start"))
    bot.send_message(call.message.chat.id, f"Вы выбрали: {call.data}\nВведите сообщение:", reply_markup=cancelbutton)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    global company_data
    if not company_data:
        keyboard(message)
        return

    with open('data.json', encoding='utf-8') as json_file:
        data = json.load(json_file)
    
    checkuser(company_data, message.from_user.username, message.chat.id, data)
    sendetxt = f"{company_data['company']}: {message.text}"
    send_message_to_contacts(sendetxt, company_data["contacts"])
    
    bot.send_message(message.chat.id, f"Сообщение отправлено в {company_data['company']}")
    company_data = {} # Сбрасываем выбор

# Запуск
print("Бот запущен...")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")
        time.sleep(5)