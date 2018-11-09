from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

import os

engine = create_engine('sqlite:///./../instance/restaurantmenu.db')
db_session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()


def init_db():

    from models import Restaurant, MenuItem
    Base.metadata.create_all(engine)
