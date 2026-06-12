CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('requester', 'support_agent', 'admin')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_users_email ON users (email);

CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('baixa', 'media', 'alta', 'critica')),
    status VARCHAR(30) NOT NULL CHECK (status IN ('aberto', 'em_andamento', 'aguardando_usuario', 'resolvido', 'fechado')),
    requester_id INTEGER NOT NULL REFERENCES users (id),
    responsible_id INTEGER NULL REFERENCES users (id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMPTZ NULL
);

CREATE INDEX ix_tickets_title ON tickets (title);
CREATE INDEX ix_tickets_priority ON tickets (priority);
CREATE INDEX ix_tickets_status ON tickets (status);
CREATE INDEX ix_tickets_requester_id ON tickets (requester_id);
CREATE INDEX ix_tickets_responsible_id ON tickets (responsible_id);

CREATE TABLE ticket_comments (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES tickets (id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users (id),
    comment TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_ticket_comments_ticket_id ON ticket_comments (ticket_id);
CREATE INDEX ix_ticket_comments_user_id ON ticket_comments (user_id);

CREATE TABLE ticket_status_history (
    id SERIAL PRIMARY KEY,
    ticket_id INTEGER NOT NULL REFERENCES tickets (id) ON DELETE CASCADE,
    old_status VARCHAR(30) NOT NULL CHECK (old_status IN ('aberto', 'em_andamento', 'aguardando_usuario', 'resolvido', 'fechado')),
    new_status VARCHAR(30) NOT NULL CHECK (new_status IN ('aberto', 'em_andamento', 'aguardando_usuario', 'resolvido', 'fechado')),
    changed_by INTEGER NOT NULL REFERENCES users (id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX ix_ticket_status_history_ticket_id ON ticket_status_history (ticket_id);
CREATE INDEX ix_ticket_status_history_changed_by ON ticket_status_history (changed_by);
