def test_create_user(client):
    res = client.post('/', json=dict(query="""mutation test($idTag: ID!, $name: String!) {createUser(idTag: $idTag, name: $name) {user {name}ok}}""", variables={
        "idTag": "1627406048",
        "name": "WZH"
    }))
    res = res.get_json()
    assert res['createUser']['ok']


def test_create_event(client):
    res = client.post('/', json=dict(
        query="""mutation test {
  createEvent(name: "测试", detail: "测试数据", deadline: "2004-05-03T17:30:08+08:00", creatorId: 1, form: "{\"test\": \"1\"}", startTime: "2004-05-03T17:30:08+08:00") {
    ok
    event {
      name
      detail
    }
  }
}
""",variables={}))
    res = res.get_json()
    assert res['createEvent']['ok']