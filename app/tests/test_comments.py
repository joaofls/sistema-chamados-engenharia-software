def create_user(client, name, email, role):
    response = client.post(
        "/users",
        json={"name": name, "email": email, "password": "segredo123", "role": role},
    )
    return response.json()["data"]["id"]


def create_ticket(client, requester_id):
    response = client.post(
        "/tickets",
        json={
            "title": "Notebook sem audio",
            "description": "Dispositivo nao emite som.",
            "priority": "media",
            "requester_id": requester_id,
        },
    )
    return response.json()["data"]["id"]


def test_add_comment_to_open_ticket(client):
    requester_id = create_user(client, "Solicitante", "solicitante5@empresa.local", "requester")
    ticket_id = create_ticket(client, requester_id)

    response = client.post(
        f"/tickets/{ticket_id}/comments",
        json={"user_id": requester_id, "comment": "Informacao adicional do problema."},
    )

    assert response.status_code == 201
    comments = client.get(f"/tickets/{ticket_id}/comments")
    assert len(comments.json()["data"]) == 1


def test_prevent_comment_on_closed_ticket(client):
    requester_id = create_user(client, "Solicitante", "solicitante6@empresa.local", "requester")
    admin_id = create_user(client, "Admin", "admin@empresa.local", "admin")
    ticket_id = create_ticket(client, requester_id)

    client.put(f"/tickets/{ticket_id}/status", json={"status": "fechado", "changed_by": admin_id})
    response = client.post(
        f"/tickets/{ticket_id}/comments",
        json={"user_id": requester_id, "comment": "Ainda preciso de ajuda."},
    )

    assert response.status_code == 400
    assert "Closed tickets" in response.json()["detail"]
