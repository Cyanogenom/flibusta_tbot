#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot, requests
from lxml import html
import re
import os

users = {}
start_finding_message = 'Сейчас найдём всё что нужно!'
formats = 'doc.prc, epub, fb2, htm, isilo3, java, lit, lrf, mobi.prc, pdf, rb, rtf, txt'
token = '512170663:AAGwbVnjIoEfqkyUr0AQKvYVyLWCt7tWeeI'
bot = telebot.TeleBot(token)
lpage = re.compile(r'page=([0-9]+)&')
rform = re.compile(r'\(([\w ]+)\)')
page_size = 50
book_url = 'http://flibusta.is'


@bot.message_handler(commands=['start'])
def command_help(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который поможет тебе с поиском книг на сайте flibusta.is. "
                                      "Для началы работы просто напиши название книги, которую хочешь найти.")


def get_books(data):
    ans = []
    urls = []
    for i_id, i in enumerate(data):
        urls.append(book_url + i.cssselect('a')[0].attrib['href'])
        ans.append(i.text_content())
    return ans, urls


def get_last_page(page):
    pager = page.cssselect('ul.pager')
    if pager:
        last_page = pager[0].cssselect('li.pager-last a')[0].attrib['href']
        return int(lpage.findall(last_page)[0])
    return 0


def get_books_data(page):
    data_cont = page.cssselect('div#main > ul')
    data_name = page.cssselect('div#main > h3')
    return data_cont, data_name


def find_books(message, page_num, last_page):
    params = {
        'ask': message,
        'page': page_num
    }

    ans = []
    url = []
    error = None
    try:
        page = html.document_fromstring(requests.get('http://flibusta.is/booksearch?ask=', params=params).content)

        if not last_page:
            last_page = get_last_page(page)

        data_cont, data_name = get_books_data(page)
        for el_id, elem in enumerate(data_cont):
            if 'Найденные книги' in data_name[el_id].text_content():
                ans, url = get_books(elem.cssselect('li'))
    except:
        error = 'error'

    if last_page and page_num < last_page:
        more_button_data = 'more_||_' + message + '_||_' + str(page_num+1) + '_||_' + str(last_page)
    else:
        more_button_data = None

    return ans, url, more_button_data, error


@bot.message_handler(content_types=["text"])
def recieve_messages(message):
    bot.send_message(message.chat.id, start_finding_message)
    answ, urls, more_button_data, error = find_books(message.text, 0, None)
    if not error:
        if answ:
            bot.send_message(message.chat.id, 'Вот что удалось найти:')

            for idx, i in enumerate(answ):
                keyboard = telebot.types.InlineKeyboardMarkup()
                button = telebot.types.InlineKeyboardButton(text='Выбрать', callback_data=urls[idx])
                keyboard.add(button)
                bot.send_message(message.chat.id, i, reply_markup=keyboard)

            if more_button_data:
                keyboard = telebot.types.InlineKeyboardMarkup()
                button = telebot.types.InlineKeyboardButton(text='Ещё', callback_data=more_button_data)
                keyboard.add(button)
                text = 'Страница ' + more_button_data.split('_||_')[2] + ' из ' + \
                       str(int(more_button_data.split('_||_')[3])+1)
                bot.send_message(message.chat.id, text, reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Ничего не нашлось :/')
    else:
        bot.send_message(message.chat.id, 'Произошла какая-то ужасная ошибка :/. Попробуйте снова. (code=0)')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.data.split('_||_')[0] == 'download':
        try:
            page = requests.get(book_url + call.data.split('_||_')[1])
            extension = page.headers['Content-Disposition'].split('.')[-1].split('"')[0]
            open('file.' + extension, 'wb').write(page.content)
            file = open('file.' + extension, 'rb')
            bot.send_document(call.from_user.id, file)
            file.close()
            os.remove('file.' + extension)
        except:
            bot.send_message(call.from_user.id, 'Произошла какая-то ужасная ошибка :/. Попробуйте снова. (code=1)')

    elif call.data.split('_||_')[0] == 'more':
        data = call.data.split('_||_')
        answ, urls, more_button_data, error = find_books(data[1], int(data[2]), int(data[3]))

        if not error:
            for idx, i in enumerate(answ):
                keyboard = telebot.types.InlineKeyboardMarkup()
                button = telebot.types.InlineKeyboardButton(text='Выбрать', callback_data=urls[idx])
                keyboard.add(button)
                bot.send_message(call.from_user.id, i, reply_markup=keyboard)

            if more_button_data:
                keyboard = telebot.types.InlineKeyboardMarkup()
                button = telebot.types.InlineKeyboardButton(text='Ещё', callback_data=more_button_data)
                keyboard.add(button)
                text = 'Страница ' + more_button_data.split('_||_')[2] + ' из ' + \
                       str(int(more_button_data.split('_||_')[3])+1)
                bot.send_message(call.from_user.id, text, reply_markup=keyboard)
        else:
            bot.send_message(call.from_user.id, 'Произошла какая-то ужасная ошибка :/. Попробуйте снова. (code=2)')

    else:
        try:
            page = html.document_fromstring(requests.get(call.data).content)
            data = page.cssselect('a')
            bot.send_message(call.from_user.id, page.cssselect('h1.title')[0].text_content())
            img = page.cssselect('img[title="Cover image"]')
            if img:
                img = book_url + img[0].attrib['src']
                bot.send_photo(call.from_user.id, photo=img)
            bot.send_message(call.from_user.id, page.cssselect('h2 + p')[0].text_content())
            keyboard = telebot.types.InlineKeyboardMarkup()
            for elem in data:
                text = rform.findall(elem.text_content())
                if text:
                    text = text[0]
                    if len(text.split(' ')) > 1:
                        text = text.split(' ')[-1]
                    if text in formats:
                        button = telebot.types.InlineKeyboardButton(text=text, callback_data='download_||_' +
                                                                                             elem.attrib['href'])
                        keyboard.add(button)
            bot.send_message(call.from_user.id, 'Выберите формат:', reply_markup=keyboard)
        except:
            bot.send_message(call.from_user.id, 'Произошла какая-то ужасная ошибка :/. Попробуйте снова. (code=3)')

if __name__ == '__main__':
    bot.polling(none_stop=True)