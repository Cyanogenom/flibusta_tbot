#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot, requests
from lxml import html

token = '512170663:AAGwbVnjIoEfqkyUr0AQKvYVyLWCt7tWeeI'
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=["text"])
def recieve_messages(message):
    page = requests.get('http://flibusta.is/').content
    print(page)
    page = html.document_fromstring(page)
    title = page.cssselect('title')[0].text_content()

    bot.send_message(message.chat.id, title)
    print(message.chat.id, message.text, title)


if __name__ == '__main__':
    bot.polling(none_stop=True)