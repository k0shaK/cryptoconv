import requests
import config
from bs4 import BeautifulSoup
from telegram import Bot
from telegram import Update
from telegram import InlineQueryResultArticle
from telegram import InputTextMessageContent
from telegram import ReplyKeyboardRemove
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import Filters
from telegram.ext import InlineQueryHandler
from telegram.ext import MessageHandler
from telegram.ext import Updater
# i do not know how to use GIT :D

class Parser:

    def get_crypto_course(self, first_coin, second_coin):
        html = requests.get(
            url=f'https://yobit.net/ru/trade/'
                f'{first_coin.upper()}/{second_coin.upper()}',
                timeout=5
        )
        soup = BeautifulSoup(html.text, 'lxml')
        self.course_crypto = soup.find('span', {'id': 'label_last'})

        return self.course_crypto


class Inline:

    def set_inline(self, id, title, message_text):
        self.inline = InlineQueryResultArticle(
            id=1,
            title=title,
            input_message_content=InputTextMessageContent(
                message_text=message_text,
            ),
        )

        return self.inline


curr = [
        'PLN', 'UAH', 'EUR', 'BYN',
        'AZN', 'BYR', 'AMD', 'KZT',
        'LEU', 'TJS', 'KGS'
]
pars_c = Parser()
inline = Inline()


def echo_handler(update: Update, context: CallbackContext):
    bname = update.message.bot.username
    if not update.message:
        return False
    update.message.reply_text(
        text=f'Перейдите в любой другой диалог и начните печатать: @{bname}',
    )


def inline_handler(update: Update, context: CallbackContext):
    users = []
    r = str(update.inline_query).split()[-3].replace("'", '').replace(',', '')
    if r not in users:
        users.append(r)
    query = update.inline_query.query.strip().upper()
    results = []
    if len(query.split()) == 4:
        print(f'Inline request: {query} \n\tfrom {r}')
        try:
            if (query.split()[3] and query.split()[1]) not in curr and len(
                    query.split()[1]) > 2 and len(query.split()[3]) > 2:
                if query.split()[3].lower() == 'rub':
                    answer = pars_c.get_crypto_course(query.split()[1], 'RUR')
                elif query.split()[1].lower() == 'rub':
                    answer = pars_c.get_crypto_course('RUR', query.split()[3])
                elif query.split() is not None:
                    answer = pars_c.get_crypto_course(
                        query.split()[1], query.split()[3]
                    )
                conv = f'{" ".join(query.split()[:2])} стоит '\
                    f'{float(answer.text)*float(query.split()[0])} '\
                    f'{query.split()[3]} сейчас!'
                title = f'{" ".join(query.split()[:2])} convert'
                results.append(inline.set_inline(1, title, conv))
            else:
                results.append(inline.set_inline(
                    1, 'Ошибка!', 'Бот переводит только криптовалюту!'
                    )
                )
        except Exception as err:
            results.append(inline.set_inline(
                1, 'Ошибка!', f'Ошибка - {err}'
                )
            )

    # Ничего не нашлось
    if query and not results:
        results.append(inline.set_inline(
            999, 'Ничего не нашлось', 'Ничего не нашлось по запросу "{query}"'
            )
        )

    update.inline_query.answer(
        results=results,
        cache_time=10,
    )


def main():
    bot = Bot(
        token=config.token,
    )
    updater = Updater(
        bot=bot,
        use_context=True,
    )

    updater.dispatcher.add_handler(MessageHandler(
        filters=Filters.text,
        callback=echo_handler
        )
    )
    updater.dispatcher.add_handler(InlineQueryHandler(inline_handler))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
