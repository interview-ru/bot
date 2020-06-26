from flask_migrate import MigrateCommand
from flask_script import Manager

from bot.app import app

if __name__ == '__main__':
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)
    manager.run()
