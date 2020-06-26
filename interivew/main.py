import os
import logging

from config import Config
from interivew.bot.bot import InterviewMeBot

basedir = os.path.abspath(os.path.dirname(__file__))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler()]
                        )
    try:
        token = os.environ['TELEGRAM_TOKEN']
    except KeyError:
        print('Missing token. You did not provide the TELEGRAM_TOKEN environment variable.')
        exit()


    port = int(os.environ.get('PORT', 8443))

    bot = InterviewMeBot(token, Config.SQLALCHEMY_DATABASE_URI)
    #bot.start_webhook('https://app.com/', port)
    bot.start_local()
