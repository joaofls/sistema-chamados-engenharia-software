# Banco de Dados

## Visão geral

O sistema utiliza PostgreSQL local com banco `support_tickets`. O modelo relacional foi pensado para suportar cadastro de usuários, ciclo de vida dos chamados, comentários e rastreabilidade de alterações de status.

## Tabelas e campos

### `users`

- `id`: chave primária inteira.
- `name`: nome do usuário.
- `email`: e-mail único.
- `password_hash`: hash da senha.
- `role`: perfil do usuário (`requester`, `support_agent`, `admin`).
- `created_at`: data de criação.
- `updated_at`: data de atualização.

### `tickets`

- `id`: chave primária inteira.
- `title`: título do chamado.
- `description`: descrição detalhada.
- `priority`: prioridade (`baixa`, `media`, `alta`, `critica`).
- `status`: status (`aberto`, `em_andamento`, `aguardando_usuario`, `resolvido`, `fechado`).
- `requester_id`: chave estrangeira para `users`.
- `responsible_id`: chave estrangeira opcional para `users`.
- `created_at`: data de criação.
- `updated_at`: data de atualização.
- `closed_at`: data de encerramento.

### `ticket_comments`

- `id`: chave primária inteira.
- `ticket_id`: chave estrangeira para `tickets`.
- `user_id`: chave estrangeira para `users`.
- `comment`: conteúdo textual.
- `created_at`: data de criação.

### `ticket_status_history`

- `id`: chave primária inteira.
- `ticket_id`: chave estrangeira para `tickets`.
- `old_status`: status anterior.
- `new_status`: novo status.
- `changed_by`: chave estrangeira para `users`.
- `created_at`: data da alteração.

## Relacionamentos

- Um usuário pode abrir vários chamados.
- Um usuário pode ser responsável por vários chamados.
- Um chamado pode ter vários comentários.
- Um chamado pode ter várias alterações de status.

## Chaves primárias

- `users.id`
- `tickets.id`
- `ticket_comments.id`
- `ticket_status_history.id`

## Chaves estrangeiras

- `tickets.requester_id -> users.id`
- `tickets.responsible_id -> users.id`
- `ticket_comments.ticket_id -> tickets.id`
- `ticket_comments.user_id -> users.id`
- `ticket_status_history.ticket_id -> tickets.id`
- `ticket_status_history.changed_by -> users.id`

## Índices

- Índice único em `users.email`.
- Índices de busca em `tickets.priority`, `tickets.status`, `tickets.requester_id`, `tickets.responsible_id`.
- Índices em `ticket_comments.ticket_id`, `ticket_comments.user_id`.
- Índices em `ticket_status_history.ticket_id`, `ticket_status_history.changed_by`.

## Comandos SQL de criação

O script completo está disponível em [schema.sql](schema.sql).
