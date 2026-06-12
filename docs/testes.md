# Plano de Testes

## Ferramenta utilizada

- Pytest

## Estratégia

Os testes automatizados validam os principais fluxos do MVP usando `TestClient` do FastAPI e banco SQLite em memória, garantindo execução rápida e isolamento dos cenários.

## Casos de teste

### Criar usuário com sucesso

- Entrada: dados válidos de nome, e-mail, senha e papel.
- Resultado esperado: resposta `201` e persistência do usuário.

### Criar ticket com sucesso

- Entrada: título, descrição, prioridade e solicitante existentes.
- Resultado esperado: resposta `201` com status inicial `aberto`.

### Impedir criação de ticket sem título

- Entrada: título vazio.
- Resultado esperado: falha de validação `422`.

### Alterar status de ticket

- Entrada: ticket existente, novo status e usuário responsável pela alteração.
- Resultado esperado: resposta `200` com novo status persistido.

### Registrar histórico ao alterar status

- Entrada: alteração de `aberto` para `em_andamento`.
- Resultado esperado: criação de registro em `ticket_status_history`.

### Adicionar comentário em ticket aberto

- Entrada: ticket aberto e comentário válido.
- Resultado esperado: comentário salvo com resposta `201`.

### Impedir comentário em ticket fechado

- Entrada: ticket fechado e tentativa de comentário.
- Resultado esperado: resposta `400`.

### Filtrar tickets por prioridade

- Entrada: consulta `GET /tickets?priority=critica`.
- Resultado esperado: retorno apenas dos tickets críticos.

### Filtrar tickets por responsável

- Entrada: consulta `GET /tickets?responsible_id=<id>`.
- Resultado esperado: retorno apenas dos tickets atribuídos ao responsável informado.
