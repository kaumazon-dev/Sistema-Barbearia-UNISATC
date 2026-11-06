# NextBarber — Sistema de Gerenciamento de Barbearias

Projeto Integrador WEB — SATC
Equipe: Kauã Guollo Mazon, Lucas Fernandes Rovaris e Vitor Fernandes de Almeida

Sistema web para gestão de uma barbearia: agenda dos barbeiros sem horário em
duplicidade, cadastro de clientes e serviços, controle de estoque com histórico
e dashboard com faturamento, atendimentos e taxa de cancelamento.

**No ar:** <https://nextbarber-blush.vercel.app>
(API: <https://barbearia-api-voje.onrender.com/health>)

> O plano gratuito do Render dorme a API depois de 15 min sem uso. O primeiro
> acesso pode levar uns 50 s; depois fica normal.

---

## Funcionalidades

| Módulo | O que faz |
|---|---|
| **Autenticação** | Cadastro, login com JWT, senha em hash (bcrypt), permissão por papel (admin, barbeiro e cliente) e "esqueci minha senha" com link por e-mail assinado, de uso único e com validade de 30 min. |
| **Clientes e serviços** | CRUD com paginação e busca. Nada é apagado de verdade, só desativado, para não perder histórico. |
| **Agenda** | Criar, listar por dia e barbeiro, remarcar, concluir e cancelar. O fim é calculado pela soma das durações dos serviços e **nenhum agendamento se sobrepõe a outro do mesmo barbeiro** (checado no service e garantido no banco por uma `EXCLUDE constraint`, que segura até duas requisições simultâneas). |
| **Estoque** | Produtos, entradas e saídas. A quantidade só muda junto com a movimentação, na mesma transação, e o histórico é imutável (um trigger no Postgres recusa `UPDATE` e `DELETE`). Alerta de produto no mínimo ou abaixo dele. |
| **Dashboard** | Atendimentos e faturamento por semana e mês, ranking de serviços, taxa de cancelamento e produtos em falta. Toda agregação roda em SQL (`GROUP BY`, `SUM`, `COUNT`). |

Os requisitos completos estão em [`docs/requisitos.md`](docs/requisitos.md), o
DER em [`docs/der.png`](docs/der.png) e o contrato da API em [`docs/api.md`](docs/api.md).

---

## Stack

| Camada | Tecnologia |
|---|---|
| Front-end | React 18 + Vite, Chart.js, CSS puro |
| Back-end | Python 3.12 + Flask (API REST), Flask-SQLAlchemy, Flask-Migrate, Marshmallow, Flask-JWT-Extended, Flask-CORS, gunicorn |
| Banco | PostgreSQL 18 |
| Infra | Docker + Docker Compose, GitHub Actions (CI), Render (API + banco), Vercel (front) |
| Testes | pytest (backend) e Vitest (front) |

### Arquitetura do backend

Camadas com fluxo de mão única: a rota valida a entrada e chama o service; o
service decide as regras de negócio e lança exceções de negócio; o repository
só lê e grava; o model mapeia a tabela.

```
api/  →  services/  →  repositories/  →  models/  →  PostgreSQL
```

- A rota não acessa o banco. O service não conhece HTTP.
- O que sai da API é sempre um schema Marshmallow, nunca o model (ex.: a `senha_hash` nunca vaza).
- Um handler global traduz as exceções de negócio para o formato de erro da API.
- O schema do banco vem só das migrations do Alembic, aplicadas sozinhas no start do container.

---

## Como rodar localmente

Pré-requisito: [Docker Desktop](https://www.docker.com/products/docker-desktop/).

**1. Variáveis de ambiente**

```bash
cp .env.example .env
```

Edite o `.env` com usuário e senha do Postgres. Use os mesmos valores em
`POSTGRES_*` e em `DATABASE_URL`, com host `db`.

**2. Subir tudo**

```bash
docker compose up -d --build
```

| Serviço | Endereço |
|---|---|
| Front (nginx) | <http://localhost:8080> |
| API | <http://localhost:5000/health> |
| Postgres | `localhost:5433` (para o pgAdmin) |

As migrations rodam sozinhas no start do backend.

**3. Popular com dados de exemplo**

```bash
docker compose exec backend python seed.py
```

O seed cria 1 admin, 3 barbeiros, 18 clientes, 7 serviços, 9 produtos (3 em
falta) e 8 semanas de agenda, mais os próximos 10 dias. Tudo passa pelos
mesmos services da API, então os dados respeitam as mesmas regras. Se o banco
já foi populado, ele não faz nada.

**Contas de demonstração:** `admin@nextbarber.com`, `rafael@nextbarber.com`
(barbeiro) e `cliente@nextbarber.com`. A senha de todas é a `SENHA_DEMO` do
topo do [`backend/seed.py`](backend/seed.py).

Para recomeçar do zero: `docker compose down -v` e suba de novo.

### Front em modo desenvolvimento (hot reload)

```bash
cd frontend
npm install
npm run dev
```

Abra <http://localhost:5173>. O Vite repassa `/api` para a API em `localhost:5000`.
Mais detalhes em [`frontend/README.md`](frontend/README.md).

---

## Testes

**Backend:** são mais de 280 testes. Os unitários testam os services sem banco;
os de integração testam rota e banco.

```bash
docker compose exec db createdb -U <POSTGRES_USER> barbearia_test
docker compose exec backend python -m pytest
```

Os testes de integração usam o `DATABASE_URL_TEST`, um banco separado, nunca o
de desenvolvimento. Sem ele, só os unitários rodam:
`docker compose exec backend python -m pytest tests/unit`.

Os services críticos têm cobertura de casos de borda:

- **Conflito de agenda:** começar exatamente quando o outro termina (pode),
  englobar outro por inteiro (não pode), remarcar sobre o próprio horário,
  agendamento cancelado liberando o horário, duas requisições simultâneas no
  mesmo horário, comparação de horário com fuso.
- **Estoque:** saída maior que o saldo, saldo sempre batendo com o histórico,
  falha no meio desfazendo tudo, histórico que nem o SQL direto consegue editar.

**Front:**

```bash
cd frontend
npm test
```

**CI:** o GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml))
roda a suíte do backend contra um Postgres 18 de verdade, mais os testes e o
build do front, a cada push e PR na `develop` e na `main`.

---

## Deploy

```
navegador → Vercel (front estático) ──/api──→ Render (gunicorn + Flask) → Render Postgres
```

### API e banco no Render

O [`render.yaml`](render.yaml) é um Blueprint que cria o Postgres e a API de uma vez:

1. No Render: **New → Blueprint**, aponte para este repositório.
2. Preencha `CORS_ORIGINS` com a URL do front, sem barra no final.
3. Clique em **Apply**.

O Render gera `SECRET_KEY` e `JWT_SECRET_KEY`, liga a `DATABASE_URL` ao banco e
roda as migrations a cada deploy. Com `RODAR_SEED=1`, o seed roda no primeiro
deploy. O `ProdConfig` se recusa a subir sem essas variáveis ou com `*` no CORS.

### Front no Vercel

Importe o repositório com **Root Directory = `frontend`**. O preset Vite vem do
[`frontend/vercel.json`](frontend/vercel.json).

Esse arquivo também tem um *rewrite* que repassa `/api/*` para a API no Render.
O navegador só fala com o domínio do Vercel, o mesmo papel que o nginx faz no
compose. Se a URL da API mudar, é só atualizar o `destination` do rewrite.

---

## Estrutura

```
├── .github/workflows/ci.yml   # CI: pytest (com Postgres) + Vitest + build
├── docker-compose.yml         # db + backend + frontend
├── docker-compose.override.yml# dev: flask --debug com o código montado
├── render.yaml                # deploy da API + Postgres
├── docs/                      # requisitos, DER e contrato da API
├── backend/
│   ├── Dockerfile / entrypoint.sh   # migrations no start, gunicorn
│   ├── seed.py                # dados de exemplo
│   ├── migrations/            # Alembic
│   ├── tests/unit|integration/
│   └── app/
│       ├── api/v1/            # rotas
│       ├── services/          # regras de negócio
│       ├── repositories/      # acesso a dados
│       ├── models/            # ORM
│       ├── schemas/           # Marshmallow (entrada e saída)
│       └── core/              # exceções, handlers de erro, segurança, fuso
└── frontend/                  # React + Vite (ver frontend/README.md)
```
