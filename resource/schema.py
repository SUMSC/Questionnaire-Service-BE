import graphene
import logging

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
    def mutate(root, info, name, detail, creator_id, form, start_time, deadline):
        event_data = {
            name: name,
            detail: detail,
            creator_id: creator_id,
            form: form,
            start_time: start_time,
            deadline: deadline
        }
        logging.info("[Mutation - CreateEvent] {}".format(str(event_data)))
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
    def mutate(root, info, id_tag, name, email=None):
        user_data = {
            id_tag: id_tag,
            name: name,
            email: email
        }
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
    def mutate(root, info, event_id, user_id, form):
        participate_data = {
            event_id: event_id,
            user_id: user_id,
            form: form
        }
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
