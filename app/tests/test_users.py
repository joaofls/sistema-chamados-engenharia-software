def test_create_user_success(client):
    response = client.post(
        "/users",
        json={
            "name": "Maria Silva",
            "email": "maria@empresa.local",
            "password": "segredo123",
            "role": "requester",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["data"]["email"] == "maria@empresa.local"
    assert payload["data"]["role"] == "requester"


def test_list_users_returns_created_users(client):
    client.post(
        "/users",
        json={
            "name": "Joao Lima",
            "email": "joao@empresa.local",
            "password": "segredo123",
            "role": "support_agent",
        },
    )

    response = client.get("/users")
    assert response.status_code == 200
    assert len(response.json()["data"]) == 1
