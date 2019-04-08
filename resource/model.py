from datetime import datetime

from sqlalchemy import Column, INT, VARCHAR, TEXT, TIMESTAMP, BOOLEAN, create_engine, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import JSON

engine = create_engine('postgresql+psycopg2://sumsc:sumsc666@wzhzzmzzy.xyz:55432/eform', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()
# We will need this for querying
Base.query = db_session.query_property()


class Event(Base):
    __tablename__ = "event"
    id = Column(INT, primary_key=True)
    name = Column(VARCHAR(32), nullable=False, unique=True)
    detail = Column(TEXT, nullable=True)
    creator = Column(INT, nullable=False)
    form = Column(JSON, nullable=False)
    active = Column(BOOLEAN, nullable=False, default=True)
    start_time = Column(TIMESTAMP, nullable=False)
    deadline = Column(TIMESTAMP, nullable=False)


class User(Base):
    __tablename__ = "user"
    id = Column(INT, primary_key=True)
    id_tag = Column(VARCHAR(16), nullable=False)
    name = Column(VARCHAR(12), nullable=False)
    email = Column(VARCHAR(128), nullable=True)
    last_login = Column(TIMESTAMP, nullable=False, default=datetime.now())


class Participate(Base):
    __tablename__ = "participate"
    event_id = Column(INT, ForeignKey("event.id"), primary_key=True, )
    event = relationship(
        Event,
        backref=backref("where", uselist=True)
    )
    user_id = Column(INT, ForeignKey("user.id"), primary_key=True)
    user = relationship(
        User,
        backref=backref("who", uselist=True)
    )
    form = Column(JSON, nullable=False)
