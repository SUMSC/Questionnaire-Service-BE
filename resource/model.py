from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, INT, VARCHAR, TEXT, TIMESTAMP, BOOLEAN, create_engine, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.dialects.postgresql import JSON


db = SQLAlchemy()
Base = db.Model
Base.query = db.session.query_property()


class User(Base):
    __tablename__ = "user"
    id = Column(INT, primary_key=True)
    id_tag = Column(VARCHAR(16), nullable=False)
    name = Column(VARCHAR(12), nullable=False)
    email = Column(VARCHAR(128), nullable=True)
    last_login = Column(TIMESTAMP, nullable=False, default=datetime.now())


class Event(Base):
    __tablename__ = "event"
    id = Column(INT, primary_key=True)
    name = Column(VARCHAR(32), nullable=False, unique=True)
    detail = Column(TEXT, nullable=True)
    creator_id = Column(INT, ForeignKey("user.id"), nullable=False)
    form = Column(TEXT, nullable=False)
    active = Column(BOOLEAN, nullable=False, default=True)
    start_time = Column(TIMESTAMP, nullable=False)
    deadline = Column(TIMESTAMP, nullable=False)
    creator = relationship(
        User,
        backref=backref("creator", uselist=True)
    )


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
    form = Column(TEXT, nullable=False)
