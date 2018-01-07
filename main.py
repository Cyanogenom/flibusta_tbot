import telebot, requests
from lxml import html

token = '512170663:AAGwbVnjIoEfqkyUr0AQKvYVyLWCt7tWeeI'
bot = telebot.TeleBot(token)

@bot.message_handler(content_types=["text"])
def recieve_messages(message):
    try:
        page = html.document_fromstring(requests.get('http://flibusta.is/').content)
        title = page.cssselect('title')[0].text_content()
    except:
        title = 'None'

    bot.send_message(message.chat.id, title)
    print(message.chat.id, message.text, title)


if __name__ == '__main__':
    bot.polling(none_stop=True)