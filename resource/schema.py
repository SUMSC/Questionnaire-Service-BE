import graphene
from graphene.relay import Node, Connection
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from .model import db_session, Event as EventModel, User as UserModel, Participate as ParticipateModel


class Event(SQLAlchemyObjectType):
    class Meta:
        model = EventModel
        interfaces = (Node, )


class EventConnection(Connection):
    class Meta:
        node = Event


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (Node, )


class UserConnection(Connection):
    class Meta:
        node = User


class Participate(SQLAlchemyObjectType):
    class Meta:
        model = ParticipateModel
        interfaces = (Node, )


class PConnection(Connection):
    class Meta:
        node = Participate


class Query(graphene.ObjectType):
    node = Node.Field()
    all_event = SQLAlchemyConnectionField(EventConnection)
    all_user = SQLAlchemyConnectionField(UserConnection)
    all_participate = SQLAlchemyConnectionField(PConnection)


schema = graphene.Schema(query=Query)
