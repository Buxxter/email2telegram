#!/usr/bin/python3
# -*- coding: utf-8 -*-

import random
import threading

import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import InlineQueryResultArticle, InlineQueryResultPhoto, InputTextMessageContent
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

"""
$ python3.5 skeleton_class.py <token>
An example that demonstrates the use of custom keyboard and inline keyboard, and their various buttons.
Before running this example, remember to `/setinline` and `/setinlinefeedback` to enable inline mode for your bot.
The bot works like this:
- First, you send it one of these 4 characters - `c`, `i`, `h`, `f` - and it replies accordingly:
    - `c` - a custom keyboard with various buttons
    - `i` - an inline keyboard with various buttons
    - `h` - hide custom keyboard
    - `f` - force reply
- Press various buttons to see their effects
- Within inline mode, what you get back depends on the **last character** of the query:
    - `a` - a list of articles
    - `p` - a list of photos
    - `b` - to see a button above the inline results to switch back to a private chat with the bot
- Play around with the bot for an afternoon ...
"""


class TelegramBot(telepot.Bot):

    __access_list = []

    @property
    def master(self):
        if len(self.__access_list) > 0:
            return self.__access_list[0]
        else:
            return None

    @master.setter
    def master(self, val):
        self.__access_list.append(val)

    def __init__(self, *args, **kwargs):
        super(TelegramBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self._message_with_inline_keyboard = None


    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        logger.debug('Chat: {} {} {}: {}'.format(content_type, chat_type, chat_id, msg['text']))

        if content_type != 'text':
            return

        if chat_id not in self.__access_list:
            self.sendMessage(chat_id, "Доступ запрещен")
            return
        else:
            self.sendMessage(chat_id, "Welcome")

        command = msg['text']

        if '/start' in command.lower():
            pass
        elif '/' in command:
            self.parse_command(command, chat_id)
        else:
            self.sendMessage(chat_id, "Я не знаю, что нужно сделать")

    def parse_command(self, command_text, chat_id):
        pass

    def on_callback_query(self, msg):
        pass

    def on_inline_query(self, msg):
        pass

    def on_chosen_inline_result(self, msg):
        pass
