import telebot
from telebot import types
from config import TELEGRAM_BOT_TOKEN
from Tracker import *

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
bot_users = {}


@bot.message_handler(commands=['start'])
def start(message):
    if not bot_users.get(message.from_user.id):
        bot_users[message.from_user.id] = None
    keyboard = [
        types.KeyboardButton("Add accounts"),
        types.KeyboardButton("Show accounts list"),
    ]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in keyboard:
        markup.add(i)
    bot.send_message(message.from_user.id, "Hello, choose the action", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def menu_actions_distributor(message):
    if message.text == 'Add accounts':
        bot.send_message(message.from_user.id,
                         f"<b>Insert twitter usernames, separated by commas</b>",
                         parse_mode='html')
        bot.register_next_step_handler(message, add_accounts)
    if message.text == 'Show accounts list':
        show_added_accounts(message)


def add_accounts(message):
    user_input = message.text.split(',')
    normalize_input(user_input)

    if not bot_users.get(message.from_user.id):
        bot_users[message.from_user.id] = Tracker(user_input, [])
    else:
        bot_users[message.from_user.id].get_users(user_input)
        for user in bot_users[message.from_user.id].users:
            bot_users[message.from_user.id].get_user_follows(user)

    print(bot_users[message.from_user.id].users)


def show_added_accounts(message):
    bot.send_message(message.from_user.id, text=','.join(bot_users[message.from_user.id].usernames))


def normalize_input(user_input: list):
    for i in range(len(user_input)):
        user_input[i] = user_input[i].strip()
