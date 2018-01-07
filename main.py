#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot, requests
from lxml import html

token = '512170663:AAGwbVnjIoEfqkyUr0AQKvYVyLWCt7tWeeI'
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=["text"])
def recieve_messages(message):

    params = {
        'ask': 'сталкер'
    }
    page = html.document_fromstring(requests.get('http://flibusta.is/booksearch?ask=', params=params).content)
    data = page.cssselect('div#main ul')
    ans = []
    for elem in data:
        if 'Найденные книги' in elem.cssselect('h3')[0].text_content():
            ans = elem.cssselect('li')[0].text_content()


    bot.send_message(message.chat.id, ans)
    print(message.chat.id, message.text, ans)


if __name__ == '__main__':
    bot.polling(none_stop=True)