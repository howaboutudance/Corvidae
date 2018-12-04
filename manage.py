import os
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from corvidae import app, db

# Migration stuff

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
