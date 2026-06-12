# Support Ticket System

Sistema de Chamados para Suporte Interno desenvolvido em Python com FastAPI, PostgreSQL e SQLAlchemy para atender ao trabalho final da disciplina de Engenharia de Software. O projeto implementa um MVP funcional para cadastro de usuários, abertura e acompanhamento de chamados, comentários, histórico de status, relatórios e documentação acadêmica.

## Objetivo do sistema

O objetivo do sistema é organizar o fluxo de suporte interno de uma empresa, permitindo que colaboradores registrem problemas, acompanhem o andamento do atendimento e que a equipe de suporte distribua, priorize e resolva chamados de forma estruturada.

## Tecnologias utilizadas

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- Pytest
- Jinja2 preparado para futuras telas simples

## Funcionalidades do MVP

- Cadastro e consulta de usuários.
- Abertura de chamados com prioridade.
- Atribuição de responsável.
- Alteração de status com histórico automático.
- Comentários por ticket.
- Filtros por status, prioridade, responsável e solicitante.
- Relatórios simples por status, prioridade e responsável.
- Seed inicial para demonstração.
- Interface web simples para operação e apresentação do sistema.

## Estrutura de pastas

```text
support-ticket-system/
|-- app/
|   |-- main.py
|   |-- dependencies.py
|   |-- seed.py
|   |-- core/
|   |   |-- config.py
|   |   |-- database.py
|   |   `-- security.py
|   |-- models/
|   |-- schemas/
|   |-- repositories/
|   |-- services/
|   |-- controllers/
|   `-- tests/
|-- alembic/
|   |-- env.py
|   `-- versions/
|-- docs/
|   |-- arquitetura.md
|   |-- banco_de_dados.md
|   |-- casos_de_uso.md
|   |-- diagramas.md
|   |-- requisitos.md
|   |-- schema.sql
|   |-- testes.md
|   `-- trabalho_final.md
|-- .env.example
|-- alembic.ini
|-- requirements.txt
`-- README.md
```

## Arquitetura

O projeto segue arquitetura em camadas para manter responsabilidades bem definidas.

- `controllers`: recebem e devolvem requisições HTTP.
- `services`: concentram regras de negócio.
- `repositories`: executam acesso ao banco de dados.
- `models`: representam as tabelas no SQLAlchemy.
- `schemas`: validam entradas e padronizam saídas.
- `core`: centraliza configuração, conexão e utilitários de infraestrutura.

Essa separação favorece Clean Code, reutilização, manutenção e aderência aos princípios SOLID.

## Como instalar o PostgreSQL localmente

1. Baixe o PostgreSQL pelo site oficial: [PostgreSQL Downloads](https://www.postgresql.org/download/).
2. Instale o servidor localmente.
3. Durante a instalação, defina usuário, senha e porta.
4. Confirme que o serviço está em execução.
5. Acesse o `psql` ou o pgAdmin para criar o banco.

## Como criar o banco `support_tickets`

Execute:

```sql
CREATE DATABASE support_tickets;
```

Depois ajuste o `DATABASE_URL` conforme seu usuário e senha locais do PostgreSQL.

## Como configurar o `.env`

1. Crie um arquivo `.env` na raiz do projeto.
2. Use o `.env.example` como base.
3. Exemplo:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/support_tickets
APP_NAME=Support Ticket System
APP_ENV=development
```

## Como criar e ativar o ambiente virtual

No caminho final do projeto:

```bash
cd /d E:\support-ticket-system
python -m venv venv
venv\Scripts\activate
```

## Como instalar as dependências

```bash
pip install -r requirements.txt
```

## Como rodar as migrations com Alembic

```bash
alembic upgrade head
```

## Como executar o projeto com Uvicorn

```bash
uvicorn app.main:app --reload
```

Documentação interativa:

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Como carregar os dados iniciais

```bash
python -m app.seed
```

Dados criados:

- 1 usuário administrador
- 1 usuário solicitante
- 1 analista de suporte
- tickets e interações de exemplo

## Como rodar os testes com Pytest

```bash
pytest
```

Os testes usam SQLite em memória para validar as regras de negócio da API sem depender do PostgreSQL local.

## Endpoints disponíveis

### Usuários

- `POST /users`
- `GET /users`
- `GET /users/{id}`

### Tickets

- `POST /tickets`
- `GET /tickets`
- `GET /tickets/{id}`
- `PUT /tickets/{id}/assign`
- `PUT /tickets/{id}/status`
- `PUT /tickets/{id}/priority`
- `DELETE /tickets/{id}`

### Comentários

- `POST /tickets/{id}/comments`
- `GET /tickets/{id}/comments`

### Relatórios

- `GET /reports/tickets-by-status`
- `GET /reports/tickets-by-priority`
- `GET /reports/tickets-by-responsible`

## Exemplos de uso da API

### Criar usuário

```http
POST /users
Content-Type: application/json

{
  "name": "Maria Silva",
  "email": "maria@empresa.local",
  "password": "segredo123",
  "role": "requester"
}
```

### Abrir chamado

```http
POST /tickets
Content-Type: application/json

{
  "title": "Erro no e-mail corporativo",
  "description": "Nao consigo enviar mensagens externas.",
  "priority": "alta",
  "requester_id": 1
}
```

### Atribuir responsável

```http
PUT /tickets/1/assign
Content-Type: application/json

{
  "responsible_id": 2
}
```

### Alterar status

```http
PUT /tickets/1/status
Content-Type: application/json

{
  "status": "em_andamento",
  "changed_by": 2
}
```

### Adicionar comentário

```http
POST /tickets/1/comments
Content-Type: application/json

{
  "user_id": 1,
  "comment": "Enviei prints adicionais do erro."
}
```

## Explicação do banco de dados

O banco possui quatro tabelas principais:

- `users`
- `tickets`
- `ticket_comments`
- `ticket_status_history`

Os relacionamentos e o schema SQL completo estão documentados em [docs/banco_de_dados.md](docs/banco_de_dados.md) e [docs/schema.sql](docs/schema.sql).

## Frontend e telas

O foco do MVP é a API REST. O projeto está preparado para futura adição de telas simples em Jinja2, mas a entrega atual prioriza simplicidade, clareza e funcionamento no backend.

## Como apresentar o projeto ao professor

Ao apresentar o trabalho, destaque os seguintes pontos:

1. Objetivo do sistema: organizar o atendimento de suporte interno.
2. Processo SCRUM: mostrar backlog, sprints e entregas incrementais descritas em `docs/trabalho_final.md`.
3. Requisitos: explicar requisitos funcionais, não funcionais e regras de negócio em `docs/requisitos.md`.
4. Arquitetura: mostrar a separação entre controllers, services e repositories.
5. Banco PostgreSQL: apresentar o modelo relacional e o schema SQL.
6. MVP: demonstrar cadastro de usuários, abertura de tickets, comentários, atribuição e alteração de status.
7. Testes: executar `pytest` e comentar os cenários validados.
8. Melhorias futuras: autenticação, anexos, notificações e dashboard.

## Possíveis melhorias futuras

- Autenticação e autorização com JWT.
- Painel web para usuários e equipe de suporte.
- Upload de anexos.
- Notificações por e-mail.
- SLA por prioridade.
- Métricas e dashboards gerenciais.
