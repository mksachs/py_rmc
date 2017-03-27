import sys
import os
import os.path

import sqlalchemy

sys.path.append('./')

import py_rmc.data.models


def create_database():
    engine = sqlalchemy.create_engine('sqlite:///database.sqlite3', echo=True)
    py_rmc.data.models.RMCBase.metadata.create_all(engine)


def reset_database():
    if os.path.isfile('database.sqlite3'):
        os.remove('database.sqlite3')
    create_database()


if __name__ == "__main__":

    reset_database()
