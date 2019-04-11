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
    id = Column(INT, primary_key=True, comment="自增主键")
    id_tag = Column(VARCHAR(16), nullable=False, comment="学号")
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
    creator = relationship(
        User,
        backref=backref("event_creator", uselist=True)
    )
    _active = Column(BOOLEAN, nullable=False, default=True, comment="活动当前是否可以报名")


class Participate(Base):
    __tablename__ = "participate"
    event_id = Column(INT, ForeignKey("event.id"), primary_key=True, comment="所加入的活动")
    event = relationship(
        Event,
        backref=backref("where", uselist=True)
    )
    user_id = Column(INT, ForeignKey("user.id"), primary_key=True, comment="加入活动的用户")
    user = relationship(
        User,
        backref=backref("who", uselist=True)
    )
    join_data = Column(JSON, nullable=False, comment="报名表")


class Qnaire(Base):
    __tablename__ = "qnaire"
    id = Column(INT, primary_key=True, comment="自增主键")
    name = Column(VARCHAR(32), nullable=False, comment="问卷名称")
    detail = Column(TEXT, nullable=True, comment="问卷详细信息")
    deadline = Column(TIMESTAMP, nullable=False, comment="问卷填写截止时间")
    form = Column(JSON, nullable=False, comment="问卷表单样式，JSONString")
    is_anonymous = Column(BOOLEAN, nullable=False, comment="是否为匿名问卷，匿名问卷不需要登陆即可填写，非匿名问卷填写后可以修改")
    creator_id = Column(INT, ForeignKey("user.id"), nullable=False)
    creator = relationship(
        User,
        backref=backref("qnaire_creator", uselist=True)
    )
    _active = Column(BOOLEAN, nullable=False, default=True, comment="FLAG值，问卷是否处于活动中")


class AnonymousAnswer(Base):
    __tablename__ = "anonymous_answer"
    id = Column(INT, primary_key=True, comment="自增主键")
    answer_data = Column(JSON, nullable=False, comment="答卷，JSONString")
    qnaire_id = Column(INT, nullable=False, comment="所属问卷")


class Answer(Base):
    __tablename__ = "answer"
    id = Column(INT, primary_key=True, comment="自增主键")
    answer_data = Column(JSON, nullable=False, comment="答卷，JSONString")
    qnaire_id = Column(INT, nullable=False, comment="所属问卷")
    user_id = Column(INT, ForeignKey("user.id"), comment="答卷者")
    user = relationship(
        User,
        backref=backref("user", uselist=True)
    )
