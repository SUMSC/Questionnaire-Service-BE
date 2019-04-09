# API Documentation

Flask / SQLAlchemy / Graphene / Postgres

## Query

- AllEvent
- AllUser
- AllParticipate

## Mutation

- CreateEvent(name, creator_id, form, start_time, deadline)
- CreateUser(id_tag, name, email=None)
- CreateParticipate(event_id, user_id, form)
- UserLogin(id)
- UpdateUser(id, name=None, email=None)
- UpdateEvent(id,)
