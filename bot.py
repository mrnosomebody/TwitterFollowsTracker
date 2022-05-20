import math
import time

import telebot
from telebot import types
from config import TELEGRAM_BOT_TOKEN
from Tracker import *
from time import sleep

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
bot_users = {}
twitter_link = 'https://twitter.com/'


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
                         f"<b>Insert twitter username you want to stop tracking (only 1)</b>",
                         parse_mode='html')
        bot.register_next_step_handler(message, remove_accounts)
    if message.text == 'Show difference':
        compare_follows(message)
    if message.text == 'Show accounts list':
        show_added_accounts(message)


def add_accounts(message):
    user_input = message.text.split(',')
    normalize_input(user_input)
    acc_amount = len(user_input)
    loops_required = math.ceil(acc_amount / 15)
    for i in range(loops_required):
        index_start = i * 15
        index_end = (i + 1) * 15
        if index_end > acc_amount:
            index_end = acc_amount
        if not bot_users.get(message.from_user.id):
            bot_users[message.from_user.id] = Tracker(user_input[index_start: index_end], [])
        else:
            bot_users[message.from_user.id].get_users(user_input[index_start: index_end])
            for user in bot_users[message.from_user.id].users[index_start: index_end]:
                bot_users[message.from_user.id].get_user_follows(user)
        bot.send_message(message.from_user.id,
                         f"Accounts {', '.join(user_input[index_start: index_end])} were added, check the list to "
                         f"make sure")
        if index_end != acc_amount:
            bot.send_message(message.from_user.id,
                             f"Wait for 15 minutes until all users will be added")
        else:
            bot.send_message(message.from_user.id,
                             f"Wait for 15 minutes before using 'Show difference'")
        time.sleep(910)


def remove_accounts(message):
    user_input = message.text.split(',')
    normalize_input(user_input)
    for user in bot_users[message.from_user.id].users:
        if user_input[0] == user.username:
            bot_users[message.from_user.id].delete_user(user)
    bot.send_message(message.from_user.id, "Accounts were deleted, check the list to make sure")


def compare_follows(message):
    acc_amount = len(bot_users[message.from_user.id].usernames)
    loops_required = math.ceil(acc_amount / 15)
    for i in range(loops_required):
        index_start = i * 15
        index_end = (i + 1) * 15
        if index_end > acc_amount:
            index_end = acc_amount
        for user in bot_users[message.from_user.id].users[index_start: index_end]:
            old_follows = set(user.follows_usernames)
            bot_users[message.from_user.id].get_user_follows(user)
            new_follows = set(user.follows_usernames)
            followed = new_follows.difference(old_follows)
            unfollowed = old_follows.difference(new_follows)
            if len(followed) > 0 or len(unfollowed) > 0:
                li_s_followed = []
                li_s_unfollowed = []
                for j in followed:
                    li_s_followed.append(f'{twitter_link + j}\n')
                for j in unfollowed:
                    li_s_unfollowed.append(f'{twitter_link + j}\n')
                bot.send_message(message.from_user.id,
                                 text=f"{user.username} \n followed: \n {''.join(li_s_followed)}\n "
                                      f"unfollowed: \n {''.join(li_s_unfollowed)}")
            else:
                bot.send_message(message.from_user.id,
                                 text=f'Nothing has changed for {user.username}')
        time.sleep(910)


def show_added_accounts(message):
    bot.send_message(message.from_user.id, text=','.join(bot_users[message.from_user.id].usernames))


def normalize_input(user_input: list):
    for i in range(len(user_input)):
        user_input[i] = user_input[i].strip()
