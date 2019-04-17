from graphene import Schema
import graphene

from flask import current_app
from sqlalchemy.exc import IntegrityError
from graphene import Mutation, ObjectType
from graphene_sqlalchemy import SQLAlchemyObjectType
from .models import db, Event as EventModel, User as UserModel, \
    Participate as ParticipateModel, Qnaire as QnaireModel, AnonymousAnswer as AnonymousAnswerModel, \
    Answer as AnswerModel


class Event(SQLAlchemyObjectType):
    class Meta:
        model = EventModel


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel


class Participate(SQLAlchemyObjectType):
    class Meta:
        model = ParticipateModel


class Qnaire(SQLAlchemyObjectType):
    class Meta:
        model = QnaireModel


class AnonymousAnswer(SQLAlchemyObjectType):
    class Meta:
        model = AnonymousAnswerModel


class Answer(SQLAlchemyObjectType):
    class Meta:
        model = AnswerModel


class Query(ObjectType):
    event = graphene.List(
        Event,
        id=graphene.Int(),
        name=graphene.String(),
        creator_id=graphene.Int(),
        _active=graphene.Boolean()
    )
    user = graphene.List(
        User,
        id=graphene.Int(),
        id_tag=graphene.String()
    )
    participate = graphene.List(
        Participate,
        event_id=graphene.Int(),
        user_id=graphene.Int()
    )
    qnaire = graphene.List(
        Qnaire,
        id=graphene.Int(),
        name=graphene.String(),
        is_anonymous=graphene.String(),
        creator_id=graphene.Int()
    )
    anonymous_answer = graphene.List(
        AnonymousAnswer,
        id=graphene.Int(),
        qnaire_id=graphene.Int()
    )
    answer = graphene.List(
        Answer,
        id=graphene.Int(),
        qnaire_id=graphene.Int(),
        user_id=graphene.Int()
    )

    @staticmethod
    def resolve_user(root, info, **kwargs):
        return db.session.query(UserModel).filter_by(**kwargs).all()

    @staticmethod
    def resolve_event(root, info, **kwargs):
        return db.session.query(EventModel).filter_by(**kwargs).all()

    @staticmethod
    def resolve_participate(root, info, **kwargs):
        return db.session.query(ParticipateModel).filter_by(**kwargs).all()

    @staticmethod
    def resolve_qnaire(root, info, **kwargs):
        return db.session.query(QnaireModel).filter_by(**kwargs).all()

    @staticmethod
    def resolve_anonymous_answer(root, info, **kwargs):
        return db.session.query(AnonymousAnswerModel).filter_by(**kwargs).all()

    @staticmethod
    def resolve_answer(root, info, **kwargs):
        return db.session.query(AnswerModel).filter_by(**kwargs).all()


def createData(model, data):
    new_field = model(**data)
    current_app.logger.debug("Create {}: ".format(str(model)) + str(data))
    db.session.add(new_field)
    try:
        db.session.commit()
    except IntegrityError as e:
        detail = str(e).split('\n')[1][9:]
        return new_field, detail, False
    else:
        return new_field, "success", True


# TODO: Create Mutation Log
#       INFO：Create Data
#       WARNING：Data Existed
#       ERROR：Create Error
class CreateEvent(Mutation):
    ok = graphene.Boolean()
    event = graphene.Field(lambda: Event)
    message = graphene.String()

    class Arguments:
        name = graphene.String(required=True)
        detail = graphene.String(required=True)
        creator_id = graphene.Int(required=True)
        form = graphene.JSONString(required=True)
        start_time = graphene.DateTime(required=True)
        deadline = graphene.DateTime(required=True)

    @staticmethod
    def mutate(root, info, **event_data):
        event, message, ok = createData(EventModel, event_data)
        return CreateEvent(event=event, ok=ok, message=message)


class CreateUser(Mutation):
    ok = graphene.Boolean()
    user = graphene.Field(lambda: User)
    message = graphene.String()

    class Arguments:
        id_tag = graphene.ID(required=True)
        name = graphene.String(required=True)

    @staticmethod
    def mutate(root, info, **user_data):
        user, message, ok = createData(UserModel, user_data)
        return CreateUser(user=user, ok=ok, message=message)


class CreateQnaire(Mutation):
    class Arguments:
        name = graphene.String(required=True)
        detail = graphene.String()
        deadline = graphene.String(required=True)
        form = graphene.JSONString(required=True)
        is_anonymous = graphene.Boolean(required=True)
        creator_id = graphene.Int(required=True)

    ok = graphene.Boolean()
    qnaire = graphene.Field(lambda: Qnaire)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, **qnaire_data):
        qnaire, message, ok = createData(QnaireModel, qnaire_data)
        return CreateQnaire(qnaire=qnaire, ok=ok, message=message)


class JoinEvent(Mutation):
    class Arguments:
        event_id = graphene.Int(required=True)
        user_id = graphene.Int(required=True)
        join_data = graphene.JSONString(required=True)

    ok = graphene.Boolean()
    participate = graphene.Field(lambda: Participate)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, **participate_data):
        """
        用户加入活动
        :param root:
        :param info:
        :param participate_data: event_id, user_id, form
        :return:
        """
        participate, message, ok = createData(ParticipateModel, participate_data)
        return JoinEvent(participate=participate, ok=ok, message=message)


class AnonymousAnswerQnaire(Mutation):
    class Arguments:
        qnaire_id = graphene.Int(required=True)
        answer = graphene.JSONString(required=True)

    ok = graphene.Boolean()
    answer = graphene.Field(lambda: AnonymousAnswer)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, **answer_data):
        answer, message, ok = createData(AnonymousAnswerModel, answer_data)
        return AnonymousAnswerQnaire(ok=ok, answer=answer, message=message)


class AnswerQnaire(Mutation):
    class Arguments:
        qnaire_id = graphene.Int(required=True)
        answer = graphene.JSONString(required=True)
        user_id = graphene.Int(required=True)

    ok = graphene.Boolean()
    answer = graphene.Field(lambda: Answer)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, **answer_data):
        res = db.session.query(AnswerModel).filter(
            AnswerModel.qnaire_id == answer_data['qnaire_id'] and AnswerModel.user_id == answer_data['user_id']
        ).first()
        if res is not None:
            return AnswerQnaire(ok=False, answer=res, message="existed")
        answer, message, ok = createData(AnswerModel, answer_data)
        return AnswerQnaire(ok=ok, answer=answer, message=message)


def updateDataById(model, id, data):
    """
    Update sth
    :param curr:
    :param data:
    :return:
    """
    curr = db.session.query(model).filter_by(id=id).first()
    if curr is None:
        return curr, "cannot found", False
    if len(list(filter(lambda x: x[1] is not None, data.items()))) == 0:
        return curr, "nothing to update", False
    for i in data:
        setattr(curr, i, data[i])
    try:
        db.session.commit()
    except IntegrityError as e:
        return curr, e.detail, False
    else:
        return curr, "success", True


# TODO: Update Mutation
#       INFO: Update Data
#       Warning: Nothing to update
#       Error: Update Failed
class UpdateUser(Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()
    user = graphene.Field(lambda: User)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, id, **data):
        curr_user, message, ok = updateDataById(UserModel, id, data)
        return UpdateUser(ok=ok, user=curr_user, message=message)


class UpdateEvent(Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        form = graphene.JSONString()
        start_time = graphene.DateTime()
        deadline = graphene.DateTime()
        detail = graphene.String()

    ok = graphene.Boolean()
    event = graphene.Field(lambda: Event)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, id, **data):
        curr_event, message, ok = updateDataById(EventModel, id, data)
        return UpdateEvent(ok=ok, event=curr_event, message=message)


class UpdateQnaire(Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        name = graphene.String()
        detail = graphene.String()
        form = graphene.JSONString()
        deadline = graphene.DateTime()

    ok = graphene.Boolean()
    qnaire = graphene.Field(lambda: Qnaire)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, id, **data):
        curr_qnaire, message, ok = updateDataById(QnaireModel, id, data)
        return UpdateQnaire(qnaire=curr_qnaire, ok=ok, message=message)


class UpdateParticipate(Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        event_id = graphene.Int(required=True)
        join_data = graphene.JSONString(required=True)

    ok = graphene.Boolean()
    participate = graphene.Field(lambda: Participate)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, user_id, event_id, join_data):
        curr = db.session.query(ParticipateModel).filter(
            ParticipateModel.event_id == event_id and ParticipateModel.user_id == user_id
        ).first()
        if curr is None:
            return UpdateParticipate(ok=False, participate=None, message="cannot found")
        curr.join_data = join_data
        try:
            db.session.commit()
        except IntegrityError as e:
            message, ok = e.detail, False
        else:
            message, ok = "success", True
        return UpdateParticipate(ok=ok, message=message, participate=curr)


class UpdateAnswer(Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        qnaire_id = graphene.Int(required=True)
        answer = graphene.JSONString(required=True)

    ok = graphene.Boolean()
    answer = graphene.Field(lambda: Answer)
    message = graphene.String()

    @staticmethod
    def mutate(root, info, user_id, qnaire_id, answer):
        curr = db.session.query(AnswerModel).filter(
            AnswerModel.user_id == user_id and AnswerModel.qnaire_id == qnaire_id
        ).first()
        if curr is None:
            return UpdateAnswer(ok=False, answer=None, message="cannot found")
        curr.answer = answer
        try:
            db.session.commit()
        except IntegrityError as e:
            message, ok = e.detail, False
        else:
            message, ok = "success", True
        return UpdateAnswer(ok=ok, message=message, answer=curr)


class DBMutation(ObjectType):
    create_event = CreateEvent.Field()
    create_user = CreateUser.Field()
    create_qnaire = CreateQnaire.Field()
    join_event = JoinEvent.Field()
    anonymous_answer_qnaire = AnonymousAnswerQnaire.Field()
    answer_qnaire = AnswerQnaire.Field()
    update_user = UpdateUser.Field()
    update_event = UpdateEvent.Field()
    update_qnaire = UpdateQnaire.Field()
    update_participate = UpdateParticipate.Field()
    update_answer = UpdateAnswer.Field()


schema = Schema(query=Query, mutation=DBMutation)
