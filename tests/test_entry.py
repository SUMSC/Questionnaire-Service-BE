def test_create_user(app):
    with app.test_client() as client:
        res = client.post('/', json={
            'query': 'mutation test {createUser(idTag: "1627406048", name: "WZH") {user {name}ok}}',
            'variables': {}
        })
        res = res.get_json()
        assert res['createUser']['ok']


# TODO: Other 16 Unit Test Cases
