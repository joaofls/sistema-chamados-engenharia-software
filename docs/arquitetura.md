# Arquitetura do Projeto

## Arquitetura em camadas

O sistema foi organizado em camadas para manter baixo acoplamento e alta coesão. Cada parte da aplicação possui responsabilidade clara, facilitando evolução, testes e manutenção.

## Responsabilidade de cada camada

- `controllers`: expõem os endpoints FastAPI, recebem parâmetros HTTP e devolvem respostas padronizadas.
- `services`: concentram validações e regras de negócio, como criação de histórico de status e restrição de comentários em tickets fechados.
- `repositories`: encapsulam consultas e operações de persistência com SQLAlchemy.
- `models`: representam as entidades do banco de dados.
- `schemas`: validam payloads de entrada e estruturam respostas da API.
- `core`: centraliza configuração da aplicação, conexão com banco e utilitários compartilhados.

## Fluxo de uma requisição

1. O cliente envia uma requisição HTTP para a API.
2. O controller recebe os dados, valida o formato via schema e chama a service apropriada.
3. A service aplica regras de negócio.
4. Quando necessário, a service usa um repository para ler ou gravar dados no PostgreSQL.
5. O repository executa as operações com SQLAlchemy.
6. A resposta retorna ao controller, que devolve o resultado ao cliente.

## Justificativa da separação entre controllers, services e repositories

A separação entre essas camadas evita a concentração excessiva de responsabilidades em um único ponto da aplicação.

- Controllers ficam leves e focados no contrato HTTP.
- Services preservam a lógica de negócio fora da camada web.
- Repositories isolam a persistência, facilitando manutenção e testes.

Esse desenho melhora legibilidade, promove reutilização de código e aproxima a solução dos princípios SOLID, em especial responsabilidade única e inversão de dependência em nível arquitetural.
