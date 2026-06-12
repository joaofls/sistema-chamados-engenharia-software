# Requisitos do Sistema

## Requisitos funcionais

- RF01: O sistema deve permitir cadastrar usuários.
- RF02: O sistema deve permitir abrir chamados.
- RF03: O sistema deve permitir definir prioridade do chamado.
- RF04: O sistema deve permitir atribuir responsável.
- RF05: O sistema deve permitir alterar status do chamado.
- RF06: O sistema deve permitir comentar em chamados.
- RF07: O sistema deve permitir consultar histórico do chamado.
- RF08: O sistema deve permitir filtrar chamados por status, prioridade e responsável.
- RF09: O sistema deve permitir listar chamados por solicitante.
- RF10: O sistema deve permitir gerar relatórios simples.

## Requisitos não funcionais

- RNF01: O sistema deve utilizar PostgreSQL.
- RNF02: O sistema deve possuir API REST.
- RNF03: O sistema deve seguir Clean Code.
- RNF04: O sistema deve ter testes automatizados.
- RNF05: O sistema deve ser executável localmente, sem Docker.
- RNF06: O sistema deve possuir documentação de instalação e uso.
- RNF07: O sistema deve usar variáveis de ambiente para configuração.
- RNF08: O sistema deve seguir princípios SOLID quando aplicável.

## Histórias de usuário

- Como colaborador, quero abrir um chamado para solicitar suporte interno.
- Como analista de suporte, quero visualizar chamados atribuídos a mim.
- Como administrador, quero acompanhar todos os chamados da empresa.
- Como usuário, quero comentar em um chamado para complementar informações.
- Como suporte, quero alterar o status do chamado para manter o solicitante informado.
- Como administrador, quero visualizar relatórios simples por status, prioridade e responsável.

## Regras de negócio

- RN01: Um ticket deve possuir título, descrição, prioridade e solicitante.
- RN02: Todo ticket inicia com status `aberto`.
- RN03: Apenas usuários com papel `support_agent` ou `admin` podem ser responsáveis por chamados.
- RN04: Toda alteração de status deve gerar um registro em `ticket_status_history`.
- RN05: Tickets fechados não aceitam comentários, a menos que sejam reabertos.
- RN06: Tickets de prioridade crítica devem aparecer primeiro nas listagens.
- RN07: A listagem de tickets deve permitir filtros por status, prioridade, responsável e solicitante.
