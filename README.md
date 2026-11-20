# Deriv Trading Backend — Fundação

Fundação assíncrona para backend de robôs de trading na Deriv (conta demo inicial), desenvolvida com FastAPI, Python 3.14 e PostgreSQL.

---

## Estrutura do Projeto

```text
C:\Projetos\Deriv\
├── app/
│   ├── __init__.py
│   ├── main.py                    # Ponto de entrada FastAPI e ciclo de vida (lifespan)
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── health.py          # Endpoints /health e /ready
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # Pydantic Settings e configurações
│   └── db/
│       ├── __init__.py
│       └── connection.py          # Gerenciamento assíncrono do pool PostgreSQL (asyncpg)
├── tests/
│   ├── __init__.py
│   └── test_health.py             # Testes automatizados das sondas de saúde e prontidão
├── .env.example                   # Modelo de variáveis de ambiente com dados fictícios
├── .gitignore                     # Regras de exclusão do Git
├── .dockerignore                  # Regras de exclusão do contexto Docker
├── Dockerfile                     # Imagem de container baseada em python:3.14-slim (não-root)
├── compose.yaml                   # Orquestração de serviços (API + PostgreSQL 16)
├── pyproject.toml                 # Definição e fixação de dependências
└── README.md
```

---

## Tecnologias e Versões

- **Runtime**: Python `3.14-slim`
- **Framework Web**: FastAPI `0.162.0`
- **Servidor ASGI**: Uvicorn `0.54.0`
- **Validação e Configurações**: Pydantic `2.14.1` / Pydantic Settings `2.16.2`
- **Driver de Banco Assíncrono**: asyncpg `0.32.0`
- **Banco de Dados**: PostgreSQL `16-alpine`
- **Testes**: Pytest `9.2.0`, Pytest-Asyncio `1.4.1`, HTTPX `0.28.1`

---

## Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` se desejar customizar valores locais:

```bash
cp .env.example .env
```

| Variável | Padrão | Descrição |
|---|---|---|
| `APP_NAME` | `Deriv Trading Backend` | Nome da aplicação |
| `APP_ENV` | `development` | Ambiente (`development`, `staging`, `production`) |
| `DEBUG` | `true` | Habilita modo debug |
| `PORT` | `8000` | Porta HTTP da API |
| `POSTGRES_HOST` | `db` | Host do banco (nome do serviço no Compose) |
| `POSTGRES_PORT` | `5432` | Porta do PostgreSQL |
| `POSTGRES_DB` | `deriv_db` | Nome do banco de dados |
| `POSTGRES_USER` | `deriv_user` | Usuário do banco de dados |
| `POSTGRES_PASSWORD` | `deriv_pass` | Senha do banco (alterar em produção) |
| `POSTGRES_MIN_POOL_SIZE`| `2` | Mínimo de conexões no pool assíncrono |
| `POSTGRES_MAX_POOL_SIZE`| `10` | Máximo de conexões no pool assíncrono |

---

## Como Executar

### 1. Iniciar os Serviços (API + Banco de Dados)

```bash
docker compose up -d --build
```

A API aguarda a condição de saúde (`service_healthy`) do PostgreSQL antes de inicializar. O código local em `./app` e `./tests` é montado como volume, permitindo recarregamento a quente (*hot-reload*) em desenvolvimento sem reconstrução contínua da imagem.

### 2. Verificar Status dos Serviços

```bash
docker compose ps
```

### 3. Visualizar Logs

```bash
# Todos os logs:
docker compose logs -f

# Apenas API:
docker compose logs -f api

# Apenas Banco:
docker compose logs -f db
```

### 4. Executar Testes Automatizados no Container

```bash
docker compose exec api pytest -v
```

### 5. Parar os Serviços

```bash
# Para os containers preservando os dados persistentes:
docker compose down

# Para os containers e remove os volumes de dados (se desejado resetar o banco):
docker compose down -v
```

---

## Endpoints Disponíveis

| Endpoint | Método | Descrição | Resposta de Sucesso | Resposta de Falha |
|---|---|---|---|---|
| `/health` | `GET` | Sonda de vida da API (*liveness*) | `200 OK` | `500` se a API cair |
| `/ready` | `GET` | Sonda de prontidão (*readiness* / banco) | `200 OK` | `503 Service Unavailable` |
| `/docs` | `GET` | Documentação interativa Swagger UI | `200 OK` | - |
| `/redoc` | `GET` | Documentação ReDoc | `200 OK` | - |
| `/openapi.json` | `GET` | Esquema OpenAPI estruturado | `200 OK` | - |

---

## Estratégia de Banco de Dados e Evolução Futura

### 1. Persistência e Isolamento
- Os dados do PostgreSQL são persistidos através do volume nomeado `postgres_data`.
- O banco de dados **não** possui portas mapeadas diretamente para o host no `compose.yaml` de produção, garantindo isolamento de rede e impedindo exposição indevida à internet. A comunicação ocorre exclusivamente através da rede interna do Docker Compose (`deriv_network`).

### 2. Evolução para TimescaleDB
- O sistema receberá fluxos de alta frequência de ticks e métricas financeiras de séries temporais.
- A versão principal do banco está fixada em `PostgreSQL 16` (`postgres:16-alpine`), base que possui compatibilidade direta e estável com a extensão **TimescaleDB** (`timescale/timescaledb:latest-pg16` ou imagem customizada com extensão `timescaledb`).
- Na etapa de persistência de séries temporais, as tabelas de ticks serão convertidas em *Hypertables* particionadas por tempo (`create_hypertable`), permitindo compressão colunar e retenção eficiente de dados históricos.

### 3. Migrações de Esquema
- A evolução do esquema de dados utilizará **Alembic** com SQLAlchemy/asyncpg.
- As migrações serão declarativas e versionadas sob controle de versão (`alembic/versions`), executadas de forma determinística antes da subida da API em ambientes de staging/produção via container init ou step de deploy.
