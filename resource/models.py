from datetime import datetime
from collections import Iterable

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, INT, VARCHAR, TEXT, TIMESTAMP, BOOLEAN, create_engine, ForeignKey
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from sqlalchemy.orm.collections import InstrumentedList
from sqlalchemy.dialects.postgresql import JSON


def to_dict(self):
    data = {c: getattr(self, c, None) for c in dir(self) if
            (not c.startswith('_') or c == '_active') and c not in ['metadata', 'to_dict', 'to_dict_plain', 'query_class', 'query']}
    for i in data:
        if 'model' in str(type(data[i])):
            data[i] = data[i].to_dict_plain()
        elif isinstance(data[i], list):
            data[i] = [it.to_dict_plain() for it in data[i]]
    return data


def to_dict_plain(self):
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


db = SQLAlchemy()
Base = db.Model
Base.query = db.session.query_property()
Base.to_dict = to_dict
Base.to_dict_plain = to_dict_plain
Base.__repr__ = lambda _: str(_.to_dict_plain())


class User(Base):
    __tablename__ = "user"
    id = Column(INT, primary_key=True, comment="自增主键")
    id_tag = Column(VARCHAR(16), nullable=False, unique=True, comment="学号")
    name = Column(VARCHAR(12), nullable=False, comment="用户姓名")


class Event(Base):
    __tablename__ = "event"
    id = Column(INT, primary_key=True, comment="自增主键")
    name = Column(VARCHAR(32), nullable=False, unique=True, comment="活动名称")
    detail = Column(TEXT, nullable=True, comment="活动详细信息")
    creator_id = Column(INT, ForeignKey("user.id"), nullable=False, comment="创建者")
    form = Column(JSON, nullable=False, comment="活动报名表单")
    start_time = Column(TIMESTAMP, nullable=False, comment="活动开始时间")
    deadline = Column(TIMESTAMP, nullable=False, comment="报名截止时间")
    create_time = Column(TIMESTAMP, nullable=False, comment="此项创建时间", default=datetime.now)
    creator = relationship(
        User,
        backref=backref("my_event", uselist=True)
    )
    _active = Column(BOOLEAN, nullable=False, default=True, comment="活动当前是否可以报名")


class Participate(Base):
    __tablename__ = "participate"
    event_id = Column(INT, ForeignKey("event.id"), primary_key=True, comment="所加入的活动")
    event = relationship(
        Event,
        backref=backref("participant", uselist=True)
    )
    user_id = Column(INT, ForeignKey("user.id"), primary_key=True, comment="加入活动的用户")
    user = relationship(
        User,
        backref=backref("my_participation", uselist=True)
    )
    answer = Column(JSON, nullable=False, comment="报名表")
    create_time = Column(
        TIMESTAMP,
        nullable=False,
        comment="此项创建时间",
        default=datetime.now,
        onupdate=datetime.now
    )


class Qnaire(Base):
    __tablename__ = "qnaire"
    id = Column(INT, primary_key=True, comment="自增主键")
    name = Column(VARCHAR(32), nullable=False, comment="问卷名称")
    detail = Column(TEXT, nullable=True, comment="问卷详细信息")
    deadline = Column(TIMESTAMP, nullable=False, comment="问卷填写截止时间")
    form = Column(JSON, nullable=False, comment="问卷表单样式，JSONString")
    creator_id = Column(INT, ForeignKey("user.id"), nullable=False)
    create_time = Column(TIMESTAMP, nullable=False, comment="此项创建时间", default=datetime.now)
    creator = relationship(
        User,
        backref=backref("my_qnaire", uselist=True)
    )
    _active = Column(BOOLEAN, nullable=False, default=True, comment="FLAG值，问卷是否处于活动中")


class AnonymousQnaire(Base):
    __tablename__ = "anonymous_qnaire"
    id = Column(INT, primary_key=True, comment="自增主键")
    name = Column(VARCHAR(32), nullable=False, comment="问卷名称")
    detail = Column(TEXT, nullable=True, comment="问卷详细信息")
    deadline = Column(TIMESTAMP, nullable=False, comment="问卷填写截止时间")
    form = Column(JSON, nullable=False, comment="问卷表单样式，JSONString")
    creator_id = Column(INT, ForeignKey("user.id"), nullable=False)
    create_time = Column(TIMESTAMP, nullable=False, comment="此项创建时间", default=datetime.now)
    creator = relationship(
        User,
        backref=backref("my_anonymous_qnaire", uselist=True)
    )
    _active = Column(BOOLEAN, nullable=False, default=True, comment="FLAG值，问卷是否处于活动中")


class AnonymousAnswer(Base):
    __tablename__ = "anonymous_answer"
    id = Column(INT, primary_key=True, comment="自增主键")
    answer = Column(JSON, nullable=False, comment="答卷，JSONString")
    qnaire_id = Column(INT, ForeignKey("anonymous_qnaire.id"), nullable=False, comment="所属问卷")
    qnaire = relationship(
        AnonymousQnaire,
        backref=backref("anonymous_answer", uselist=True)
    )
    create_time = Column(TIMESTAMP, nullable=False, comment="此项创建时间", default=datetime.now)


class Answer(Base):
    __tablename__ = "answer"
    id = Column(INT, primary_key=True, comment="自增主键")
    answer = Column(JSON, nullable=False, comment="答卷，JSONString")
    qnaire_id = Column(INT, ForeignKey("qnaire.id"), nullable=False, comment="所属问卷")
    qnaire = relationship(
        Qnaire,
        backref=backref("answer", uselist=True)
    )
    user_id = Column(INT, ForeignKey("user.id"), comment="答卷者")
    user = relationship(
        User,
        backref=backref("my_answer", uselist=True)
    )
    create_time = Column(
        TIMESTAMP,
        nullable=False,
        comment="此项创建时间",
        default=datetime.now,
        onupdate=datetime.now
    )
