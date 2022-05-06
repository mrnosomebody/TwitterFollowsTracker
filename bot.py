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
        types.KeyboardButton("Remove accounts"),
        types.KeyboardButton("Show difference"),
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
    if message.text == 'Remove accounts':
        bot.send_message(message.from_user.id,
                         f"<b>Insert twitter usernames you want to stop tracking</b>",
                         parse_mode='html')
        bot.register_next_step_handler(message, remove_accounts)
    if message.text == 'Show difference':
        compare_follows(message)
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
    bot.send_message(message.from_user.id, "Accounts were added, check the list to make sure")


def remove_accounts(message):
    user_input = message.text.split(',')
    normalize_input(user_input)
    for user in bot_users[message.from_user.id].users:
        if user.username in user_input:
            bot_users[message.from_user.id].delete_user(user)
    bot.send_message(message.from_user.id, "Accounts were deleted, check the list to make sure")


def compare_follows(message):
    for user in bot_users[message.from_user.id].users:
        old_follows = set(user.follows_usernames)
        bot_users[message.from_user.id].get_user_follows(user)
        new_follows = set(user.follows_usernames)
        followed = new_follows.difference(old_follows)
        unfollowed = old_follows.difference(new_follows)
        bot.send_message(message.from_user.id,
                         text=f"{user.username} followed: {followed or None}, unfollowed: {unfollowed or None}")


def show_added_accounts(message):
    bot.send_message(message.from_user.id, text=','.join(bot_users[message.from_user.id].usernames))


def normalize_input(user_input: list):
    for i in range(len(user_input)):
        user_input[i] = user_input[i].strip()
