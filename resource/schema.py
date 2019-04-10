import graphene
import logging

from datetime import datetime
from graphene import Mutation, ObjectType, Schema, InputObjectType
from graphene.relay import Node, Connection
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from .model import db, Event as EventModel, User as UserModel, Participate as ParticipateModel


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


class EConnection(Connection):
    class Meta:
        node = Event


class UConnection(Connection):
    class Meta:
        node = User


class PConnection(Connection):
    class Meta:
        node = Participate


class CreateEvent(Mutation):
    class Arguments:
        name = graphene.String(required=True)
        detail = graphene.String(required=True)
        creator_id = graphene.String(required=True)
        form = graphene.JSONString(required=True)
        start_time = graphene.DateTime()
        deadline = graphene.DateTime(required=True)

    ok = graphene.Boolean()
    event = graphene.Field(lambda: Event)

    @staticmethod
    def mutate(root, info, **event_data):
        """

        :param root:
        :param info:
        :param event_data: name, detail, creator_id, form, start_time, deadline
        :return:
        """
        event = EventModel(**event_data)
        db.session.add(event)
        db.session.commit()
        event = Event(**event_data)
        ok = True
        return CreateEvent(event=event, ok=ok)


class CreateUser(Mutation):
    class Arguments:
        id_tag = graphene.ID(required=True)
        name = graphene.String(required=True)
        email = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(lambda : User)

    @staticmethod
    def mutate(root, info, **user_data):
        """

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


class CreateParticipate(Mutation):
    class Arguments:
        event_id = graphene.ID(required=True)
        user_id = graphene.ID(required=True)
        form = graphene.JSONString(required=True)

    ok = graphene.Boolean()
    event = graphene.Field(lambda: Participate)

    @staticmethod
    def mutate(root, info, **participate_data):
        """

        :param root:
        :param info:
        :param participate_data: event_id, user_id, form
        :return:
        """
        participate = ParticipateModel(**participate_data)
        db.session.add(participate)
        try:
            db.session.commit()
        except Exception as e:
            ok = False
            participate = None
        else:
            participate = Participate(**participate_data)
            ok = True
        return CreateParticipate(participate=participate, ok=ok)


class UserLogin(Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    ok = graphene.Boolean()
    user = graphene.Field(lambda: User)

    @staticmethod
    def mutate(root, info, id):
        curr_user = db.session.query(UserModel).filter_by(id=id).first_or_404()
        if curr_user is None:
            return UserLogin(ok=False, user=curr_user)
        curr_user.last_login = datetime.now()
        db.session.commit()
        return UserLogin(user=curr_user, ok=True)


class UpdateUserData(Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        email = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(lambda: User)

    @staticmethod
    def mutate(root, info, id, **user_data):
        curr_user = db.session.query(UserModel).filter_by(id=id).first_or_404()
        if curr_user is None:
            return UpdateUserData(ok=False, user=None)
        if len(list(filter(lambda x: x[1] is not None, user_data.items()))) == 0:
            return UpdateUserData(ok=True, user=curr_user)
        for i in user_data:
            setattr(curr_user, i, user_data[i])
        db.session.commit()
        return UpdateUserData(user=curr_user, ok=True)


class UpdateEventData(Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        name = graphene.String()
        detail = graphene.String()
        form = graphene.JSONString()
        start_time = graphene.DateTime()
        deadline = graphene.DateTime()

    ok = graphene.Boolean()
    event = graphene.Field(lambda : Event)

    @staticmethod
    def mutate(root, info, id, **event_data):
        curr_event = db.session.query(EventModel).filter_by(id=id).first_or_404()
        if curr_event is None:
            UpdateEventData(ok=False, event=None)
        if len(list(filter(lambda x: x[1] is not None, event_data.items()))) == 0:
            return UpdateEventData(ok=True, user=curr_event)
        for i in event_data:
            setattr(curr_event, i, event_data[i])
        db.session.commit()
        return UpdateEventData(user=curr_event, ok=True)


# TODO: JOIN Event(Update Participate)
class JoinEvent(Mutation):
    pass


# TODO: Leave Event (Update Participate)
class LeaveEvent(Mutation):
    pass

# TODO: Add Other Resource Mutation


class Query(ObjectType):
    node = Node.Field()
    all_event = SQLAlchemyConnectionField(EConnection)
    all_user = SQLAlchemyConnectionField(UConnection)
    all_participate = SQLAlchemyConnectionField(PConnection)


class DBMutation(ObjectType):
    create_event = CreateEvent.Field()
    create_user = CreateUser.Field()
    create_participate = CreateParticipate.Field()


schema = Schema(query=Query, mutation=DBMutation)
