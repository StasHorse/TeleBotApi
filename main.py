import telebot
from telebot import types

API_TOKEN = '7840559273:AAHOs-wR1Mh3lKhv9cp1-_5cIgKXdmYnoKk'
bot = telebot.TeleBot(API_TOKEN)

admin_id = '768762870'

#Адмін
admin_ids = [768762870]

#Каталог
catalog = [
    {"id": 1, "name": "Товар 1", "price": "100 грн", "description": "Опис товару 1"},
    {"id": 2, "name": "Товар 2", "price": "200 грн", "description": "Опис товару 2"},
]

orders = []

# ---------------------- Команди бота ----------------------

#/start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Вітаємо у нашому боті! Використовуйте /help для перегляду доступних команд.")

#/help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
    Ось список доступних команд:
    /start - Почати роботу з ботом
    /help - Отримати список команд
    /info - Інформація про бота
    /catalog - Перегляд каталогу товарів
    /feedback - Залишити відгук
    """
    bot.reply_to(message, help_text)

#/info
@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message, "Це бот для інтерактивного інтернет-магазину. Ви можете переглянути товари, зробити замовлення та багато іншого.")


# ---------------------- Функціонал ----------------------

# /catalog з інлайн кнопками
@bot.message_handler(commands=['catalog'])
def send_catalog(message):
    markup = telebot.types.InlineKeyboardMarkup()
    for item in catalog:
        markup.add(telebot.types.InlineKeyboardButton(text=f"{item['name']} - {item['price']}",
                                                      callback_data=f"item_{item['id']}"))
    bot.send_message(message.chat.id, "Ось наш каталог товарів:", reply_markup=markup)

# Обработка каталога
@bot.callback_query_handler(func=lambda call: call.data.startswith("item_"))
def handle_item(call):
    item_id = int(call.data.split("_")[1])
    item = next((i for i in catalog if i['id'] == item_id), None)
    if item:
        bot.send_message(call.message.chat.id, f"{item['name']} - {item['price']}\nОпис: {item['description']}")
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text="Замовити", callback_data=f"order_{item['id']}"))
        bot.send_message(call.message.chat.id, "Натисніть 'Замовити', щоб оформити замовлення:", reply_markup=markup)

#Обробка замовлення
@bot.callback_query_handler(func=lambda call: call.data.startswith("order_"))
def handle_order(call):
    item_id = int(call.data.split("_")[1])
    item = next((i for i in catalog if i['id'] == item_id), None)
    if item:
        bot.send_message(call.message.chat.id, f"Ви підтверджуєте замовлення на {item['name']} за {item['price']}?",
                         reply_markup=telebot.types.InlineKeyboardMarkup().add(
                             telebot.types.InlineKeyboardButton(text="Підтвердити", callback_data=f"confirm_{item['id']}"),
                             telebot.types.InlineKeyboardButton(text="Скасувати", callback_data=f"cancel_{item['id']}")
                         ))

#Підтвердження замовлення
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_order(call):
    item_id = int(call.data.split("_")[1])
    item = next((i for i in catalog if i['id'] == item_id), None)
    if item:
        bot.send_message(call.message.chat.id, f"Ваше замовлення на {item['name']} підтверджено.")
        orders.append({"username": call.message.chat.username, "item_name": item['name']})
        bot.send_message(admin_id, f"Замовлення: {item['name']}\nКористувач: {call.message.chat.username}")

#Скасування замовлення
@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_"))
def cancel_order(call):
    bot.send_message(call.message.chat.id, "Ваше замовлення було скасовано.")


# ---------------------- Адмін панель ----------------------

#/admin з доступом до панелі
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id in admin_ids:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("/add_item")
        btn2 = types.KeyboardButton("/remove_item")
        btn3 = types.KeyboardButton("/orders")
        markup.add(btn1, btn2, btn3)
        bot.send_message(message.chat.id, "Ласкаво просимо в адмін-панель. Виберіть дію:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "У вас немає прав адміністратора.")

# ---------------------- Додавання товарів ----------------------

@bot.message_handler(commands=['add_item'])
def add_item(message):
    if message.from_user.id in admin_ids:
        bot.send_message(message.chat.id, "Введіть інформацію про товар у форматі: Назва, Ціна, Опис.")
        bot.register_next_step_handler(message, save_item)
    else:
        bot.send_message(message.chat.id, "У вас немає прав адміністратора.")

def save_item(message):
    try:
        name, price, description = message.text.split(", ")
        if not price.isdigit():
            bot.send_message(message.chat.id, "Помилка! Ціна повинна бути числом.")
            return
        item_id = len(catalog) + 1
        catalog.append({"id": item_id, "name": name, "price": f"{price} грн", "description": description})
        bot.send_message(message.chat.id, f"Товар {name} додано до каталогу.")
    except Exception as e:
        bot.send_message(message.chat.id, "Помилка! Перевірте формат введених даних.")

# ---------------------- Видалення товарів ----------------------

@bot.message_handler(commands=['remove_item'])
def remove_item(message):
    if message.from_user.id in admin_ids:
        bot.send_message(message.chat.id, "Введіть ID товару для видалення.")
        bot.register_next_step_handler(message, delete_item)
    else:
        bot.send_message(message.chat.id, "У вас немає прав адміністратора.")

def delete_item(message):
    try:
        item_id = int(message.text)
        global catalog
        catalog = [i for i in catalog if i['id'] != item_id]
        bot.send_message(message.chat.id, f"Товар з ID {item_id} видалено.")
    except Exception as e:
        bot.send_message(message.chat.id, "Помилка! Перевірте введені дані.")

# ---------------------- Перегляд замовлень ----------------------

@bot.message_handler(commands=['orders'])
def view_orders(message):
    if message.from_user.id in admin_ids:
        if orders:
            for order in orders:
                bot.send_message(message.chat.id, f"Замовлення: {order['item_name']}\nКористувач: {order['username']}")
        else:
            bot.send_message(message.chat.id, "Немає замовлень.")
    else:
        bot.send_message(message.chat.id, "У вас немає прав адміністратора.")


# ---------------------- Відгукт ----------------------

#/feedback
@bot.message_handler(commands=['feedback'])
def get_feedback(message):
    bot.send_message(message.chat.id, "Напишіть свій відгук, і він буде переданий адміністраторам.")
    bot.register_next_step_handler(message, save_feedback)

def save_feedback(message):
    feedback = message.text
    bot.send_message(admin_id, f"Відгук від користувача {message.chat.username}: {feedback}")
    bot.send_message(message.chat.id, "Дякуємо за ваш відгук!")

bot.polling()
