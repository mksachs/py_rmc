import sqlalchemy
import sqlalchemy.orm
import flask

from py_rmc import rmc


@rmc.before_request
def before_request():
    """Creates database connections for each request.

    """
    engine = sqlalchemy.create_engine('sqlite:///database.sqlite3', echo=True)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)

    flask.g.database = Session()


@rmc.teardown_request
def teardown_request(exception):
    """Closes database connections when a request ends.

    :param exception: exception
    """
    database = flask.g.get('database')
    if database is not None:
        if not database.connection().closed:
            database.close()