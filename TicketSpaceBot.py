import telebot
import os
import psycopg2
from telebot import types

bot = telebot.TeleBot(api_token)

# Храним данные о пользователях в словаре
user_data = {}


@bot.message_handler(commands=['start'])
def beginning(message):
    mark = types.ReplyKeyboardMarkup(resize_keyboard=True)
    mark.add(types.KeyboardButton("Реклама"), types.KeyboardButton("Поддержка"))
    bot.send_photo(message.chat.id, 'https://www.meme-arsenal.com/memes/836c42c0863f5e87ac9ebde78cfb437e.jpg',
                   reply_markup=mark)


@bot.message_handler(func=lambda message: message.text == "Реклама")
def advert(message):
    inline_mark = types.InlineKeyboardMarkup()
    inline_mark.add(
        types.InlineKeyboardButton("Добавить баннер на сайт", callback_data='order_advert'),
        types.InlineKeyboardButton("Другое", callback_data='connect_with')
    )
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=inline_mark)


@bot.message_handler(func=lambda message: message.text == "Поддержка")
def connect_with(message):
    inline_mark = types.InlineKeyboardMarkup()
    inline_mark.add(
        types.InlineKeyboardButton("Тех.отделом", callback_data='connect_tech'),
        types.InlineKeyboardButton("Отделом маркетинга", callback_data='connect_marketing'))
    bot.send_message(message.chat.id, "Связаться с:", reply_markup=inline_mark)


@bot.callback_query_handler(func=lambda call: call.data == 'order_advert')
def order_advert(call):
    bot.send_message(call.message.chat.id, "Отправьте название мероприятия (как на сайте)")
    user_data[call.from_user.id] = {'step': 'waiting_for_event_name'}


@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id].get(
    'step') == 'waiting_for_event_name')
def get_event_name(message):
    event_name = message.text
    bot.send_message(message.chat.id,
                     f"Название мероприятия '{event_name}' получено! Теперь отправьте постер в формате PNG/JPG")

    # Сохраняем название мероприятия в данных пользователя
    user_data[message.chat.id]['event_name'] = event_name
    user_data[message.chat.id]['step'] = 'waiting_for_poster'


@bot.message_handler(content_types=['photo'],
                     func=lambda message: message.chat.id in user_data and user_data[message.chat.id].get('step') == 'waiting_for_poster')
def handle_banner_upload(message):
    event_name = user_data[message.chat.id].get('event_name')
    event_name_c = event_name.replace(" ", "_").replace(":", "")
    # Получаем информацию о фотографии
    file_info = bot.get_file(message.photo[-1].file_id)  # Используем последнее фото, это самое большое качество

    # Скачиваем файл
    downloaded_file = bot.download_file(file_info.file_path)

    # Указываем папку для сохранения
    folder_path = 'proizvod/mainpage/static/mainpage/img/'
    poster_path = f"{folder_path}{event_name_c}_poster.png"
    path = f"/static/mainpage/img/{event_name_c}_poster.png"
    with open(poster_path, 'wb') as new_file:
        new_file.write(downloaded_file)
    try:
        conn = psycopg2.connect(
            dbname="project", user="postgres", password="1234567", host="localhost", port='5432')
        cursor = conn.cursor()
        cursor.execute("UPDATE Events SET poster = %s WHERE event_name = %s", (path, event_name))
        conn.commit()
        cursor.close()
        conn.close()
        bot.send_message(message.chat.id, f"Постер для мероприятия '{event_name}' успешно загружен и сохранен!")
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при сохранении данных!")
        print(f"Ошибка при сохранении в базе данных: {e}")
    # Очищаем данные пользователя
    del user_data[message.chat.id]


@bot.callback_query_handler(func=lambda call: call.data in ['connect_tech', 'connect_marketing', 'connect_with'])
def handle_department_selection(call):
    if call.data in ['connect_marketing', 'connect_with']:
        bot.send_message(call.message.chat.id, "Введите текст сообщения для отдела маркетинга:")
        user_data[call.from_user.id] = {'step': 'waiting_for_marketing_message'}
    elif call.data == 'connect_tech':
        bot.send_message(call.message.chat.id, "Введите текст сообщения для технического отдела:")
        user_data[call.from_user.id] = {'step': 'waiting_for_tech_message'}


@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id].get(
    'step') == 'waiting_for_marketing_message')
def handle_sales_message(message):
    username = message.from_user.username or "неизвестный пользователь"
    try:
        # Отправляем сообщение в отдел маркетинга
        bot.send_message(SALES_CHAT_ID, f"Сообщение от @{username}:\n{message.text}")
        bot.send_message(message.chat.id, "Ваше сообщение отправлено в отдел маркетинга")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при отправке сообщения! Попробуйте позже")
        print(f"Ошибка при отправке сообщения в отдел  маркетинга: {e}")
    del user_data[message.chat.id]


@bot.message_handler(func=lambda message: message.chat.id in user_data and user_data[message.chat.id].get(
    'step') == 'waiting_for_tech_message')
def handle_tech_message(message):
    username = message.from_user.username or "неизвестный пользователь"
    try:
        # Отправляем сообщение в технический отдел
        bot.send_message(TECH_CHAT_ID, f"Сообщение от @{username}:\n{message.text}")
        bot.send_message(message.chat.id, "Ваше сообщение отправлено в технический отдел")
    except Exception as e:
        bot.send_message(message.chat.id, "Произошла ошибка при отправке сообщения! Попробуйте позже")
        print(f"Ошибка при отправке сообщения в тех. отдел: {e}")
    del user_data[message.chat.id]

bot.infinity_polling()
