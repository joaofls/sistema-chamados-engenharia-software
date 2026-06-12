def create_user(client, name, email, role):
    response = client.post(
        "/users",
        json={"name": name, "email": email, "password": "segredo123", "role": role},
    )
    return response.json()["data"]["id"]


def test_create_ticket_success(client):
    requester_id = create_user(client, "Solicitante", "solicitante@empresa.local", "requester")

    response = client.post(
        "/tickets",
        json={
            "title": "Erro no e-mail",
            "description": "Nao consigo enviar mensagens externas.",
            "priority": "alta",
            "requester_id": requester_id,
        },
    )

    assert response.status_code == 201
    payload = response.json()["data"]
    assert payload["status"] == "aberto"
    assert payload["priority"] == "alta"


def test_prevent_ticket_without_title(client):
    requester_id = create_user(client, "Solicitante", "solicitante2@empresa.local", "requester")

    response = client.post(
        "/tickets",
        json={
            "title": "",
            "description": "Descricao valida",
            "priority": "media",
            "requester_id": requester_id,
        },
    )

    assert response.status_code == 422


def test_update_status_registers_history(client):
    requester_id = create_user(client, "Solicitante", "solicitante3@empresa.local", "requester")
    agent_id = create_user(client, "Agente", "agente@empresa.local", "support_agent")
    ticket_id = client.post(
        "/tickets",
        json={
            "title": "VPN indisponivel",
            "description": "A VPN nao conecta.",
            "priority": "critica",
            "requester_id": requester_id,
        },
    ).json()["data"]["id"]

    response = client.put(
        f"/tickets/{ticket_id}/status",
        json={"status": "em_andamento", "changed_by": agent_id},
    )

    assert response.status_code == 200
    detail = client.get(f"/tickets/{ticket_id}").json()["data"]
    assert detail["status"] == "em_andamento"
    assert len(detail["status_history"]) == 1
    assert detail["status_history"][0]["old_status"] == "aberto"
    assert detail["status_history"][0]["new_status"] == "em_andamento"


def test_filter_tickets_by_priority_and_responsible(client):
    requester_id = create_user(client, "Solicitante", "solicitante4@empresa.local", "requester")
    agent_id = create_user(client, "Agente", "agente2@empresa.local", "support_agent")

    critical_ticket_id = client.post(
        "/tickets",
        json={
            "title": "Servidor parado",
            "description": "Aplicacao principal indisponivel.",
            "priority": "critica",
            "requester_id": requester_id,
        },
    ).json()["data"]["id"]
    client.post(
        "/tickets",
        json={
            "title": "Mouse com defeito",
            "description": "Equipamento falhando.",
            "priority": "baixa",
            "requester_id": requester_id,
        },
    )

    client.put(f"/tickets/{critical_ticket_id}/assign", json={"responsible_id": agent_id})

    priority_response = client.get("/tickets", params={"priority": "critica"})
    responsible_response = client.get("/tickets", params={"responsible_id": agent_id})

    assert priority_response.status_code == 200
    assert len(priority_response.json()["data"]) == 1
    assert priority_response.json()["data"][0]["title"] == "Servidor parado"
    assert len(responsible_response.json()["data"]) == 1
