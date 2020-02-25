from datetime import datetime
from collections import Iterable

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, INT, VARCHAR, TEXT, TIMESTAMP, BOOLEAN, ForeignKey, DATE, JSON
from sqlalchemy.orm import relationship, backref


ignore_set = {'active', 'metadata', 'to_dict', 'to_dict_plain', 'query_class', 'query'}


def to_dict(self):
    """
    将 SQLAlchemy Model 对象序列化为字典，同时也会对 backref 属性进行处理
    backref 属性内的 backref 不会被序列化，避免循环调用
    """
    data = {c: getattr(self, c, None) for c in dir(self) if
            (not c.startswith('_') and c not in ignore_set)}
    print(dir(self))
    for i in data:
        if 'model' in str(type(data[i])):
            data[i] = data[i].to_dict_plain()
        elif isinstance(data[i], list):
            data[i] = [it.to_dict_plain() for it in data[i]]
    return data


def to_dict_plain(self):
    """
    只处理数据库中存在的列，不处理 backref 属性
    """
    return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}


db = SQLAlchemy()
Base = db.Model
Base.query = db.session.query_property()
Base.to_dict = to_dict
Base.to_dict_plain = to_dict_plain
Base.__repr__ = lambda _: str(_.to_dict_plain())


class User(Base):
    __tablename__ = "user"
    id_tag = Column(VARCHAR(16), nullable=False, primary_key=True, comment="学号")
    name = Column(VARCHAR(12), nullable=False, comment="用户姓名")
    type = Column(BOOLEAN, nullable=False, comment="用户类型")


class Qnaire(Base):
    __tablename__ = "qnaire"
    id = Column(INT, primary_key=True, comment="自增主键", autoincrement=True)
    name = Column(VARCHAR(32), nullable=False, comment="问卷名称")
    description = Column(TEXT, nullable=True, comment="问卷详细信息")
    form = Column(JSON, nullable=False, comment="问卷表单样式，JSONString")
    active = Column(BOOLEAN, nullable=False, default=True, comment="FLAG值，问卷是否处于活动中")
    deadline = Column(DATE, nullable=False, comment="问卷填写截止时间")
    create_time = Column(TIMESTAMP, nullable=False, comment="此项创建时间", default=datetime.now)

    owner_id = Column(VARCHAR(16), ForeignKey("user.id_tag"), nullable=False)
    owner = relationship(
        User,
        backref=backref("my_qnaire", uselist=True)
    )


class Anaire(Base):
    __tablename__ = "anaire"
    id = Column(INT, primary_key=True, comment="自增主键", autoincrement=True)
    name = Column(VARCHAR(32), nullable=False, comment="问卷名称")
    description = Column(TEXT, nullable=True, comment="问卷详细信息")
    form = Column(JSON, nullable=False, comment="问卷表单样式，JSONString")
    active = Column(BOOLEAN, nullable=False, default=True, comment="FLAG值，问卷是否处于活动中")
    deadline = Column(DATE, nullable=False, comment="问卷填写截止时间")
    create_time = Column(TIMESTAMP, nullable=False, comment="此项创建时间", default=datetime.now)

    owner_id = Column(VARCHAR(16), ForeignKey("user.id_tag"), nullable=False)
    owner = relationship(
        User,
        backref=backref("my_anaire", uselist=True)
    )


class Answer(Base):
    __tablename__ = "answer"
    id = Column(INT, primary_key=True, comment="自增主键", autoincrement=True)
    answer = Column(JSON, nullable=False, comment="答卷，JSONString")
    qnaire_id = Column(INT, ForeignKey("qnaire.id"), nullable=False, comment="所属问卷")
    qnaire = relationship(
        Qnaire,
        backref=backref("answer", uselist=True)
    )
    owner_id = Column(VARCHAR(16), ForeignKey("user.id_tag"), nullable=False, comment="答卷者")
    owner = relationship(
        User,
        backref=backref("my_answer", uselist=True)
    )
    create_time = Column(TIMESTAMP, nullable=False, comment="此项创建时间", default=datetime.now)


class GAnswer(Base):
    __tablename__ = "ganswer"
    id = Column(INT, primary_key=True, comment="自增主键", autoincrement=True)
    answer = Column(JSON, nullable=False, comment="答卷，JSONString")
    qnaire_id = Column(INT, ForeignKey("anaire.id"), nullable=False, comment="所属问卷")
    create_time = Column(TIMESTAMP, nullable=False, comment="此项创建时间", default=datetime.now)
    qnaire = relationship(
        Anaire,
        backref=backref("answer", uselist=True)
    )
