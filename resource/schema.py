from graphene import Schema
import graphene

from graphql.error import located_error
from graphene import Mutation, ObjectType
from graphene.relay import Node, Connection
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from .models import db, Event as EventModel, User as UserModel, \
    Participate as ParticipateModel, Qnaire as QnaireModel, AnonymousAnswer as AnonymousAnswerModel, \
    Answer as AnswerModel


class Event(SQLAlchemyObjectType):
    class Meta:
        model = EventModel
        interfaces = (Node,)


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (Node,)


class Participate(SQLAlchemyObjectType):
    class Meta:
        model = ParticipateModel
        interfaces = (Node,)


class Qnaire(SQLAlchemyObjectType):
    class Meta:
        model = QnaireModel
        interfaces = (Node,)


class AnonymousAnswer(SQLAlchemyObjectType):
    class Meta:
        model = AnonymousAnswerModel
        interfaces = (Node,)


class Answer(SQLAlchemyObjectType):
    class Meta:
        model = AnswerModel
        interfaces = (Node,)


class EConnection(Connection):
    class Meta:
        node = Event


class UConnection(Connection):
    class Meta:
        node = User


class PConnection(Connection):
    class Meta:
        node = Participate


class QConnection(Connection):
    class Meta:
        node = Qnaire


class AnonyAConnection(Connection):
    class Meta:
        node = AnonymousAnswer


class AConnection(Connection):
    class Meta:
        node = Answer


class Query(ObjectType):
    node = Node.Field()
    all_event = SQLAlchemyConnectionField(EConnection)
    all_user = SQLAlchemyConnectionField(UConnection)
    all_participate = SQLAlchemyConnectionField(PConnection)
    all_qnaire = SQLAlchemyConnectionField(QConnection)
    all_anonymous_answer = SQLAlchemyConnectionField(AnonyAConnection)
    all_answer = SQLAlchemyConnectionField(AConnection)


# TODO: Create Mutation Log
#       INFO：Create Data
#       WARNING：Data Existed
#       ERROR：Create Error
class CreateEvent(Mutation):
    class Arguments:
        name = graphene.String(required=True)
        detail = graphene.String(required=True)
        creator_id = graphene.Int(required=True)
        form = graphene.JSONString(required=True)
        start_time = graphene.DateTime(required=True)
        deadline = graphene.DateTime(required=True)

    ok = graphene.Boolean()
    event = graphene.Field(lambda: Event)

    @staticmethod
    def mutate(root, info, **event_data):
        """
        创建活动
        :param root:
        :param info:
        :param event_data: name, detail, creator_id, form, start_time, deadline
        :return:
        """
        event = EventModel(**event_data)
        db.session.add(event)
        db.session.commit()
        ok = True
        event = Event(**event_data)
        return CreateEvent(event=event, ok=ok)


class CreateUser(Mutation):
    class Arguments:
        id_tag = graphene.ID(required=True)
        name = graphene.String(required=True)

    ok = graphene.Boolean()
    user = graphene.Field(lambda: User)

    @staticmethod
    def mutate(root, info, **user_data):
        """
        创建用户
        :param root:
        :param info:
        :param user_data: id_tag, name, email
        :return:
        """
        user = UserModel(**user_data)
        db.session.add(user)
        db.session.commit()
        user = User(**user_data)
        ok = True
        return CreateUser(user=user, ok=ok)


class CreateNaire(Mutation):
    class Arguments:
        name = graphene.String(required=True)
        detail = graphene.String()
        deadline = graphene.String(required=True)
        form = graphene.JSONString(required=True)
        is_anonymous = graphene.Boolean(required=True)
        creator_id = graphene.Int(required=True)

    ok = graphene.Boolean()
    qnaire = graphene.Field(lambda: Qnaire)

    @staticmethod
    def mutate(root, info, **qnaire_data):
        """
        创建问卷
        :param root:
        :param info:
        :param qnaire_data: name, detail, deadline, form, is_anonymous, creator_id
        :return:
        """
        qnaire = QnaireModel(**qnaire_data)
        db.session.add(qnaire)
        db.session.commit()
        qnaire = Qnaire(**qnaire_data)
        ok = True
        return CreateNaire(qnaire=qnaire, ok=ok)


class JoinEvent(Mutation):
    class Arguments:
        event_id = graphene.Int(required=True)
        user_id = graphene.Int(required=True)
        form = graphene.JSONString(required=True)

    ok = graphene.Boolean()
    participate = graphene.Field(lambda: Participate)

    @staticmethod
    def mutate(root, info, **participate_data):
        """
        用户加入活动
        :param root:
        :param info:
        :param participate_data: event_id, user_id, form
        :return:
        """
        participate = ParticipateModel(**participate_data)
        db.session.add(participate)
        db.session.commit()
        participate = Participate(**participate_data)
        return JoinEvent(participate=participate, ok=True)


class AnonymousAnswerNaire(Mutation):
    class Arguments:
        naire_id = graphene.Int(required=True)
        answer = graphene.JSONString(required=True)

    ok = graphene.Boolean()
    answer = graphene.Field(lambda: AnonymousAnswer)

    @staticmethod
    def mutate(root, info, **answer_data):
        answer = AnonymousAnswerModel(**answer_data)
        db.session.add(answer)
        db.session.commit()
        answer = AnonymousAnswer(**answer_data)
        return AnonymousAnswerNaire(ok=True, answer=answer)


class AnswerNaire(Mutation):
    class Arguments:
        naire_id = graphene.Int(required=True)
        answer = graphene.JSONString(required=True)
        user_id = graphene.Int(required=True)

    ok = graphene.Boolean()
    answer = graphene.Field(lambda: Answer)

    @staticmethod
    def mutate(root, info, **answer_data):
        answer = AnswerModel(**answer_data)
        db.session.add(answer)
        db.session.commit()
        answer = Answer(**answer_data)
        return AnswerNaire(ok=True, answer=answer)


def updateData(curr, data: dict):
    """
    Update sth
    :param curr:
    :param data:
    :return:
    """
    if curr is None:
        return False, curr
    if len(list(filter(lambda x: x[1] is not None, data.items()))) == 0:
        return True, curr
    for i in data:
        setattr(curr, i, data[i])
    db.session.commit()
    return True


# TODO: Update Mutation
#       INFO: Update Data
#       Warning: Nothing to update
#       Error: Update Failed
class UpdateUser(Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    user = graphene.Field(lambda: User)

    @staticmethod
    def mutate(root, info, id, **data):
        curr_user = db.session.query(UserModel).filter_by(id=id).first_or_404()
        res = updateData(curr_user, data)
        curr_user = User(**data)
        return UpdateUser(ok=res, user=curr_user)


class UpdateEvent(Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        detail = graphene.String()
        form = graphene.JSONString()
        start_time = graphene.DateTime()
        deadline = graphene.DateTime()

    ok = graphene.Boolean()
    event = graphene.Field(lambda: Event)

    @staticmethod
    def mutate(root, info, id, **data):
        curr_event = db.session.query(EventModel).filter_by(id=id).first_or_404()
        res = updateData(curr_event, data)
        curr_event = Event(**data)
        return UpdateEvent(ok=res, event=curr_event)


class UpdateNaire(Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        detail = graphene.String()
        form = graphene.JSONString()
        start_time = graphene.DateTime()
        deadline = graphene.DateTime()

    ok = graphene.Boolean()
    event = graphene.Field(lambda: Event)

    @staticmethod
    def mutate(root, info, id, **data):
        curr_naire = db.session.query(EventModel).filter_by(id=id).first_or_404()
        res = updateData(curr_naire, data)
        curr_naire = Qnaire(**data)
        return UpdateNaire(ok=res, event=curr_naire)


class UpdateParticipate(Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        event_id = graphene.Int(required=True)
        join_data = graphene.JSONString(required=True)

    ok = graphene.Boolean()
    participate = graphene.Field(lambda: Participate)

    @staticmethod
    def mutate(root, info, user_id, event_id, join_data):
        curr = db.session.query(ParticipateModel).filter(
            ParticipateModel.event_id == event_id and ParticipateModel.user_id == user_id).first_or_404()
        if curr is None:
            return UpdateParticipate(ok=False, curr=None)
        curr.join_data = join_data
        db.session.commit()
        curr = Participate(user_id=user_id, event_id=event_id, join_data=join_data)
        return UpdateParticipate(ok=True, participate=curr)


class UpdateAnswer(Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        qnaire_id = graphene.Int(required=True)
        answer_data = graphene.JSONString(required=True)

    ok = graphene.Boolean()
    answer = graphene.Field(lambda: Answer)

    @staticmethod
    def mutate(root, info, user_id, qnaire_id, answer_data):
        curr = db.session.query(AnswerModel).filter(
            AnswerModel.user_id == user_id and AnswerModel.qnaire_id == qnaire_id).first_or_404()
        if curr is None:
            return UpdateAnswer(ok=False, curr=None)
        curr.answer_data = answer_data
        db.session.commit()
        curr = Answer(user_id=user_id, qnaire_id=qnaire_id, answer_data=answer_data)
        return UpdateAnswer(ok=True, answer=curr)


class DBMutation(ObjectType):
    create_event = CreateEvent.Field()
    create_user = CreateUser.Field()
    create_naire = CreateNaire.Field()
    join_event = JoinEvent.Field()


schema = Schema(query=Query, mutation=DBMutation)
