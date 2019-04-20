from resource.models import db
import pytest


# TODO: 添加注释
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_create_user(client):
    res = client.post('/', json=dict(
        query="""
    mutation testUser {
      createUser(
        idTag: "123456",
        name: "测试用户"
      ) {
        user {
          name
        }
        ok
        message
      }
    }""",
        variables={}))
    res = res.get_json()
    assert res['data']['createUser']['ok']


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_create_event(client):
    res = client.post('/', json=dict(
        query="""
    mutation testEvent {
      createEvent(
        name: "测试活动",
        detail: "测试数据",
        deadline: "2004-05-03T17:30:08+08:00",
        creatorId: 1,
        form: "{}",
        startTime: "2004-05-03T17:30:08+08:00"
      ) {
        ok
        event {
          name
          detail
          creator {
            name
          }
        }
        message
      }
    }
    """,
        variables={}))
    res = res.get_json()
    assert res['data']['createEvent']['ok']
    assert res['data']['createEvent']['event']['creator']['name'] == '测试用户'


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_join_event(client):
    res = client.post('/', json=dict(
        query="""
    mutation joinEvent{
      joinEvent(
        eventId: 1,
        userId: 1,
        joinData: "{}"
      ) {
        ok
        message
        participate {
          joinData
          user {
            name
          }
          event {
            name
          }
        }
      }
    }
    """,
        variables={}
    ))
    res = res.get_json()
    assert res['data']
    assert res['data']['joinEvent']['ok']
    assert res['data']['joinEvent']['participate']['user']['name'] == '测试用户'
    assert res['data']['joinEvent']['participate']['event']['name'] == '测试活动'


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_create_qnaire(client):
    res = client.post('/', json=dict(
        query="""
    mutation createQnaire {
      createQnaire(
        name: "测试问卷",
        isAnonymous: false,
        form: "{}",
        detail: "测试数据",
        deadline: "2004-05-03T17:30:08+08:00",
        creatorId: 1
      ) {
        ok
        message
        qnaire {
          id
          name
          creator {
            name
          }
        }
      }
    }
    """,
        variables={}
    ))
    res = res.get_json()
    assert res['data']
    assert res['data']['createQnaire']['ok']
    assert res['data']['createQnaire']['qnaire']['id'] == '1'


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_create_anonymous_qnaire(client):
    res = client.post('/', json=dict(
        query="""
    mutation createAnonymousQnaire {
      createQnaire(
        name: "测试问卷 - 匿名",
        isAnonymous: true,
        form: "{}",
        detail: "测试数据",
        deadline: "2004-05-03T17:30:08+08:00",
        creatorId: 1
      ) {
        ok
        message
        qnaire {
          id
          name
          creator {
            name
          }
        }
      }
    }
    """,
        variables={}
    ))
    res = res.get_json()
    print(res)
    assert res['data']
    assert res['data']['createQnaire']['ok']
    assert res['data']['createQnaire']['qnaire']['id'] == '2'


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_anonymous_answer(client):
    res = client.post('/', json=dict(
        query="""
    mutation anonymousAnswer {
      anonymousAnswerQnaire(
        answer: "{}",
        qnaireId: 2
      ) {
        ok
        message
        answer {
          qnaire {
            name
          }
        }
      }
    }
    """,
        variables={}
    ))
    res = res.get_json()
    assert res['data']
    assert res['data']['anonymousAnswerQnaire']['ok']
    assert res['data']['anonymousAnswerQnaire']['answer']['qnaire']['name'] == "测试问卷 - 匿名"


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_answer(client):
    query = """
    mutation answer {
      answerQnaire(
        answer: "{}",
        qnaireId: 1,
        userId: 1
      ) {
        ok
        message
        answer {
          qnaire {
            name
          }
          user {
            name
          }
        }
      }
    }
        """
    # 创建实名问卷
    res = client.post('/', json=dict(
        query=query,
        variables={}
    )).get_json()
    assert not res.get('errors')
    assert res['data']['answerQnaire']['ok']
    assert res['data']['answerQnaire']['answer']['qnaire']['name'] == "测试问卷"
    # 再次创建问卷，应当失败
    res = client.post('/', json=dict(
        query=query,
        variables={}
    )).get_json()
    assert not res.get('errors')
    assert not res['data']['answerQnaire']['ok']


# TODO: User Update Test Case
@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_update_user(client):
    pass


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_update_event(client):
    # 更新活动数据
    res = client.post("/", json=dict(
        query="""
    mutation updateEvent {
      updateEvent(
        id: 1,
        name: "测试活动",
        detail: "测试数据",
        deadline: "2004-05-03T17:30:08+08:00",
        form: "{}",
        startTime: "2004-05-03T17:30:08+08:00"
      ) {
        ok
        event {
          name
          detail
        }
        message
      }
    }
        """,
        variables={}
    ))
    res = res.get_json()
    assert not res.get('errors')
    assert res['data']['updateEvent']['ok']
    # 更新不存在的活动，应当失败，返回 cannot found
    res = client.post("/", json=dict(
        query="""
        mutation updateEvent {
          updateEvent(
            id: 2,
            name: "测试活动",
            detail: "测试数据",
            deadline: "2004-05-03T17:30:08+08:00",
            form: "{}",
            startTime: "2004-05-03T17:30:08+08:00"
          ) {
            ok
            event {
              name
              detail
            }
            message
          }
        }
            """,
        variables={}
    ))
    res = res.get_json()
    assert not res.get('errors')
    assert not res['data']['updateEvent']['ok']
    assert res['data']['updateEvent']['message'] == 'cannot found'


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_update_qnaire(client):
    res = client.post("/", json=dict(
        query="""
    mutation updateQnaire {
      updateQnaire(
        id: 1,
        name: "测试问卷",
        detail: "测试数据",
        deadline: "2004-05-03T17:30:08+08:00",
        form: "{}"
      ) {
        ok
        qnaire {
          name
          detail
        }
        message
      }
    }
            """,
        variables={}
    ))
    res = res.get_json()
    assert not res.get('errors')
    assert res['data']['updateQnaire']['ok']


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_update_participate(client):
    res = client.post('/', json=dict(
        query="""
        mutation updateParticipate{
          updateParticipate(
                eventId: 1,
            userId: 1,
            joinData: "{}"
          ) {
            ok
            message
            participate {
              event {
                name
              }
              user {
                name
              }
            }
          }
        }
        """,
        variables={}
    )).get_json()
    assert not res.get('errors')
    assert res['data']['updateParticipate']['ok']
    assert res['data']['updateParticipate']['participate']['event']['name'] == '测试活动'
    assert res['data']['updateParticipate']['participate']['user']['name'] == '测试用户'


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_update_answer(client):
    res = client.post('/', json=dict(
        query="""
        mutation updateAnswer{
          updateAnswer(
            userId: 1,
            qnaireId: 1,
            answer: "{}"
          ) {
            ok
            message
            answer {
              answer
              qnaire {
                name
              }
              user {
                name
              }
            }
          }
        }
        """,
        variables={}
    )).get_json()
    assert not res.get('errors')
    assert res['data']['updateAnswer']['ok']
    assert res['data']['updateAnswer']['answer']['qnaire']['name'] == '测试问卷'
    assert res['data']['updateAnswer']['answer']['user']['name'] == '测试用户'


# @pytest.mark.filterwarnings("ignore::DeprecationWarning")
# def test_clear(app):
#     db.init_app(app)
#     with app.app_context():
#         db.drop_all()
#         db.create_all()
