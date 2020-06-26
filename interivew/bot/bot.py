import logging
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from telegram import KeyboardButton, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters

from bot.exceptions import APIConnectionError
from bot.models import User
from bot.questions_api import get_random_question

logger = logging.getLogger(__name__)

emojis = {'computer': '💻'}

QUESTION_RECEIVED, CANCEL = 0, 1


class InterviewMeBot:
    def __init__(self, token, database_url):
        """

        :rtype: object
        """
        self.token = token
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher

        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        self.session = Session()

        start_handler = CommandHandler('start', self.menu)
        menu_handler = CommandHandler('menu', self.menu)
        cancel_handler = CommandHandler('cancel', self.cancel_conversation)

        usage_handler = CommandHandler('usage', self.usage)
        about_handler = CommandHandler('about', self.about)
        random_question_handler = ConversationHandler(
            entry_points=[CommandHandler('random_question', self.random_question)],
            states={
                QUESTION_RECEIVED: [MessageHandler(Filters.text, self.answer_received)],
                CANCEL: [cancel_handler]
            },
            fallbacks=[cancel_handler]
        )

        handlers = [start_handler,
                    menu_handler,
                    usage_handler,
                    about_handler,
                    random_question_handler,
                    random_question_handler
                    ]

        for handler in handlers:
            self.dispatcher.add_handler(handler)

    def answer_received(self, bot, update):
        answer_name = update.message.text
        try:
            # TODO: check answer
            bot.send_message(chat_id=update.message.chat_id, text=f'Amazing',
                             parse_mode=ParseMode.MARKDOWN)
        except APIConnectionError:
            bot.send_message(chat_id=update.message.chat_id, text=f'Answer failed to check.',
                             parse_mode=ParseMode.MARKDOWN)

    def usage(self, bot, update):
        u = """*/random_question* - random question
        
*/about* - information about the bot and the author

*/usage* - show this message."""

        self.display_menu_keyboard(bot, update, u)

    def about(self, bot, update):
        about_message = """    
*About the bot*
The bot is written in programming language called *python*.
It uses internal questions database to show messages.
If you're familiar with programming and want to use the code as an inspiration or a guide when writing your own bots, or you're just curious about how does a code for a chatbot look like, you can find it [here](https://github.com/).
"""

        self.display_menu_keyboard(bot, update, about_message)

    def update_user_in_database(self, user_id):
        user = self.session.query(User).filter(User.id == user_id).first()
        time = datetime.now()
        if user is None:
            user = User(id=user_id, date_started=time, date_last_used=time)
        else:
            user.update_time(time)

        self.session.add(user)
        self.session.commit()

    def cancel_conversation(self, bot, update):
        self.display_menu_keyboard(bot, update, emojis['computer'])
        return ConversationHandler.END

    def random_question(self, bot, update):
        user_id = update.message.chat.id
        self.update_user_in_database(user_id)

        question = get_random_question()
        self.send_question(bot, update, question)
        return QUESTION_RECEIVED

    def send_question(self, bot, update, question):
        bot.send_message(chat_id=update.message.chat_id, text=f'*{question["name"]}*', parse_mode=ParseMode.MARKDOWN)
        bot.send_message(chat_id=update.message.chat_id, text=f'_{question["question"]}_',
                         parse_mode=ParseMode.MARKDOWN)

    def menu(self, bot, update):
        user_id = update.message.chat.id
        self.update_user_in_database(user_id)

        self.display_menu_keyboard(bot, update, emojis['computer'])

    def display_menu_keyboard(self, bot, update, text):
        menu_options = [
            [KeyboardButton('/random_question')],
            [KeyboardButton('/about')],
            [KeyboardButton('/usage')],
        ]

        keyboard = ReplyKeyboardMarkup(menu_options)
        bot.send_message(chat_id=update.message.chat_id,
                         text=text,
                         parse_mode=ParseMode.MARKDOWN,
                         reply_markup=keyboard,
                         disable_web_page_preview=True)

    def start_webhook(self, url, port):
        self.updater.start_webhook(listen="0.0.0.0",
                                   port=port,
                                   url_path=self.token)
        self.updater.bot.set_webhook(url + self.token)
        self.updater.idle()

    def start_local(self):
        self.updater.start_polling()
        self.updater.idle()
