# CLAUDE.md — Sistema de Gerenciamento de Barbearias

Projeto Integrador WEB — SATC
Equipe: Kauã Guollo Mazon, Lucas Fernandes Rovaris, Vitor Fernandes de Almeida

---

## 1. COMO VOCÊ DEVE TRABALHAR NESTE PROJETO

**Leia esta seção antes de qualquer coisa. Ela tem precedência sobre o resto do arquivo.**

Este é um trabalho acadêmico. O objetivo é que a equipe aprenda escrevendo o código.
Você é um **consultor técnico e revisor**, não um gerador de código.

### Não faça, a menos que seja pedido explicitamente

- Não escreva implementações completas de arquivos.
- Não crie arquivos no projeto por conta própria.
- Não "adiante" o próximo passo porque pareceu útil.
- Não reescreva um arquivo inteiro quando a pergunta era sobre uma parte dele.
- Não entregue a solução pronta quando a pergunta foi conceitual.

### Faça por padrão

- Explique conceitos e o **porquê** das decisões.
- Aponte onde a arquitetura está sendo violada e explique qual regra foi quebrada.
- Revise código que a equipe enviar: erros, riscos, acoplamento, casos de borda não tratados.
- Sugira a **direção** da solução em texto, não em código pronto.
- Faça perguntas quando o requisito estiver ambíguo.
- Quando houver mais de um caminho válido, apresente os trade-offs e deixe a decisão com a equipe.

### Quando código é permitido

Só nestes casos:

1. A equipe pedir explicitamente ("escreve para mim", "me mostra o código", "implementa isso").
2. A equipe enviar um código e pedir correção ou melhoria — aí você pode devolver o trecho corrigido.
3. Trechos mínimos de ilustração de um conceito isolado (2 a 5 linhas), quando for mais claro que um parágrafo — nunca a solução do módulo em questão.

### Formato preferido de resposta

Quando a equipe estiver travada, prefira nesta ordem:

1. Explicar o conceito por trás do problema.
2. Indicar onde no projeto a solução deve morar (qual camada, qual arquivo).
3. Descrever os passos em texto.
4. Só então, se pedirem, mostrar código.

Se você não tiver certeza se deve escrever código, **pergunte antes**.

---

## 2. STACK

| Camada | Tecnologia |
|---|---|
| Front-end | HTML, CSS e JavaScript puro (sem framework) |
| Back-end | Python + Flask (API REST) |
| Banco de dados | PostgreSQL |
| Containerização | Docker + Docker Compose |

Bibliotecas do backend:

- **Flask-SQLAlchemy** — ORM
- **Flask-Migrate** (Alembic) — versionamento de schema
- **Marshmallow** — validação de entrada e serialização de saída
- **Flask-JWT-Extended** — autenticação stateless
- **Flask-CORS** — liberação de origem para o front
- **psycopg2-binary** — driver do PostgreSQL
- **passlib/bcrypt** — hash de senha
- **gunicorn** — servidor WSGI de produção
- **pytest** — testes

---

## 3. ARQUITETURA

Arquitetura em **camadas**, com fluxo unidirecional:

```
Requisição HTTP
   ↓
api/       (rotas, blueprints)      → valida entrada, chama service, devolve resposta
   ↓
services/  (regras de negócio)      → decide, calcula, lança exceções de negócio
   ↓
repositories/ (acesso a dados)      → só CRUD, sem regra
   ↓
models/    (entidades ORM)          → mapeamento das tabelas
   ↓
PostgreSQL
```

### As 5 regras invioláveis

Se alguma dessas for quebrada em código que a equipe enviar, **aponte imediatamente**.

1. **A rota não sabe o que é banco de dados.**
   Nada de `db.session` ou `Model.query` dentro de `api/`.

2. **O service não sabe o que é HTTP.**
   Não recebe `Request`, não devolve `status_code`, não chama `jsonify`.
   Ele lança exceções de negócio; a camada de erro traduz para HTTP.

3. **O repository não decide nada.**
   Só busca, insere, atualiza e remove. Nenhum `if` de regra de negócio.

4. **Model nunca sai da API.**
   O que trafega é sempre um schema Marshmallow. Isso impede vazar `senha_hash`.

5. **Nada fora de `app/api/` importa `request`, `g`, `session` ou `current_app`.**
   Esta é a regra mais frágil no Flask, porque esses objetos são globais e acessíveis
   de qualquer lugar. Se um service precisa do usuário logado, ele recebe `usuario_id`
   como argumento.

**Teste rápido da regra 5:** se um service não pode ser chamado de um script de linha de
comando sem simular uma requisição HTTP, ele está errado.

### Estrutura de pastas

```
barbearia/
├── docker-compose.yml
├── docker-compose.override.yml   # ajustes de dev (hot reload, volumes)
├── .env.example
├── README.md
│
├── docs/
│   ├── der.dbml                  # fonte do diagrama (dbdiagram.io) — edite AQUI
│   ├── der.png                   # exportado do .dbml, nunca editado à mão
│   ├── requisitos.md             # RF, RNF, fora de escopo e regras de negócio
│   └── api.md                    # contrato dos endpoints, mantido à mão
│
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── wsgi.py
│   ├── migrations/
│   ├── tests/
│   │   ├── unit/                 # services isolados, sem banco
│   │   └── integration/          # rotas + banco
│   └── app/
│       ├── __init__.py           # create_app() — application factory
│       ├── extensions.py         # db, migrate, jwt, cors instanciados sem app
│       ├── config.py             # DevConfig / ProdConfig / TestConfig
│       ├── core/
│       │   ├── security.py
│       │   ├── exceptions.py     # exceções de negócio
│       │   └── error_handlers.py # exceção → resposta HTTP
│       ├── api/v1/
│       │   ├── __init__.py       # blueprint pai, url_prefix="/api/v1"
│       │   ├── auth.py
│       │   ├── clientes.py
│       │   ├── servicos.py
│       │   ├── agendamentos.py
│       │   ├── estoque.py
│       │   └── dashboard.py
│       ├── schemas/
│       ├── services/
│       ├── repositories/
│       └── models/
│
└── frontend/
    ├── Dockerfile
    ├── nginx.conf                # serve estáticos + proxy para /api
    ├── index.html
    └── src/
        ├── pages/
        │   ├── login/
        │   ├── agenda/
        │   ├── clientes/
        │   ├── estoque/
        │   └── dashboard/
        ├── assets/
        │   ├── css/
        │   │   ├── base.css      # reset, variáveis CSS, tipografia
        │   │   ├── components/
        │   │   └── pages/
        │   └── img/
        └── js/
            ├── api/
            │   ├── http.js       # fetch centralizado, injeta o token
            │   └── *.api.js
            ├── components/
            ├── utils/
            └── store/            # estado da sessão
```

### Regras do front-end

- Nenhuma tela chama `fetch` direto. Tudo passa por `js/api/`.
- `http.js` é o único lugar que conhece a URL base e o cabeçalho de autorização.
- CSS de componente é separado de CSS de página.

**Sem build, sem Node.** Decisão tomada: nada de Vite, npm ou `package.json`. O ganho
(HMR, variável de ambiente para a URL da API) não paga o custo de trazer uma stack de
build para três iniciantes com 11 semanas — e a estrutura é multi-página, o que exigiria
configuração extra no Vite. A URL base por ambiente se resolve em três linhas dentro do
`http.js`. Se for reavaliar, reavalie **no começo** da Fase 7, nunca no meio.

### Por que `extensions.py` existe

As extensões são importadas por models, repositories e pela factory. Instanciá-las dentro
de `__init__.py` gera import circular assim que um model importar `db`. Instanciar num
módulo separado, sem app, e chamar `init_app()` na factory resolve.

---

## 4. ORDEM DE EXECUÇÃO — POR ONDE COMEÇAR

### Princípio central: fatias verticais, não camadas horizontais

**Não** faça "todos os models → todos os repositories → todos os services".
Escolha **um módulo** e leve-o de ponta a ponta, do banco até a tela.

Motivo: erros de arquitetura aparecem cedo, quando ainda são baratos de corrigir, e nunca
se chega na entrega com três camadas prontas e nada rodando.

### Calendário real

Entrega final: **27/11/2026**. Apresentação parcial: **25/09/2026**.
Feature freeze: **15/11/2026**. São 11 semanas, sem folga.

| Prazo | Entrega |
|---|---|
| 18/09 | Fase 0 fechada + migrations criando as 6 tabelas |
| 20/09 | `base_repository`, error handlers, CORS |
| 24/09 | Auth completa + tela de login |
| **25/09** | **Apresentação parcial** |
| 11/10 | CRUD de clientes (4 camadas + tela) |
| 18/10 | CRUD de serviços (4 camadas + tela) |
| 01/11 | Agenda completa com regra de conflito |
| 08/11 | Estoque |
| 15/11 | Dashboard + **feature freeze** |
| 22/11 | Testes, responsividade, deploy |
| **27/11** | **Entrega final** |

As datas e os critérios de pronto de cada item estão no Trello, quadro
"Sistema Barbearia — PI WEB".

**Ordem de corte**, decidida com antecedência para não virar discussão em cima da hora:
RF31 (taxa de cancelamento) → RF30 (ranking de serviços) → RF09 (histórico do cliente)
→ RF08 (busca de cliente). Auth, agenda e estoque **não** entram na lista de corte.

Depois de 15/11 nada novo entra. Funcionalidade que faltar é cortada, não adiada.
Sistema incompleto que roda vale mais que completo que quebra na apresentação.

### Ordem recomendada

**Fase 0 — Fundação (semana 1)**
Repositório com branches (`main`, `develop`, `feature/*`). Esqueleto de pastas.
`docker-compose` subindo Postgres + backend com uma rota `/health` respondendo.
DER e requisitos fechados em `docs/`. Divisão de responsabilidades entre os três.

> Docker vem **agora**, não antes do deploy. O ganho principal é os três rodarem o
> mesmo Postgres, mesma versão, sem instalar nada na máquina.

**Fase 1 — Base técnica (semana 2)**
Conexão com o banco. Flask-Migrate configurado e primeira migration aplicada.
`base_repository` com CRUD genérico. Tratamento global de erros. CORS liberado.

**Fase 2 — Autenticação (semana 3)**
Cadastro e login, hash de senha, geração e validação de JWT, decorador que protege rotas.
É a **primeira fatia vertical completa** e vira o template de todas as outras.

> Esta fase é feita por **uma pessoa só**. Se três inventarem o padrão em paralelo,
> saem três padrões e as fases seguintes herdam a bagunça. Os outros dois copiam o
> template depois. Se alguém precisar inventar algo novo na Fase 3, o template ficou
> incompleto — corrija na auth, não no módulo novo.

**Fase 3 — Cadastros básicos (semanas 4–5)**
CRUD de clientes e de serviços, cada um passando pelas quatro camadas.
O padrão já está estabelecido; o ritmo acelera aqui.

**Fase 4 — Agenda (semanas 6–7) — parte mais difícil**
Criar, listar por dia e por barbeiro, remarcar, cancelar.
Regra crítica: nenhum agendamento pode se sobrepor a outro do mesmo barbeiro.
Testar casos de borda: agendamento que começa exatamente quando o outro termina,
agendamento que engloba outro por inteiro.
**Reservar tempo extra para esta fase.**

**Fase 5 — Estoque (semana 8)**
Produtos, entradas e saídas, alerta de estoque abaixo do mínimo.
Toda alteração de quantidade passa pelo service e grava movimentação.

**Fase 6 — Dashboard (semana 9)**
Atendimentos e faturamento por semana e por mês, serviços mais vendidos,
taxa de cancelamento, produtos em falta.
Usar agregação em SQL (`GROUP BY`, `SUM`, `COUNT`), nunca percorrer listas em Python.

**Fase 7 — Front-end (em paralelo, a partir da fase 2)**
Começar assim que o login existir e acompanhar cada módulo do backend.
Deixar todo o front para o fim é o erro clássico que estoura o prazo.
Chart.js para os gráficos.

**Fase 8 — Refino e deploy (semanas 10–11)**
Testes nos services críticos (conflito de agenda, cálculo de estoque).
Responsividade, tratamento de erro visível, README com instruções.
Deploy decidido: **front no Vercel, backend e banco no Render** (planos gratuitos).

Consequências dessa escolha, que afetam o código desde a Fase 7:

- Front e back ficam em **origens diferentes**. CORS deixa de ser enfeite: whitelist da
  origem do Vercel, nunca `*`.
- A URL base da API muda entre local e produção. Só `http.js` pode saber disso.
  Se alguma tela chamar `fetch` direto, o dia do deploy vira caçada a URLs.
- O Render entrega `DATABASE_URL` com prefixo `postgres://`; SQLAlchemy 2.x exige
  `postgresql://`. Normalize no `config.py`.
- O backend gratuito hiberna. Acordar alguns minutos antes de qualquer apresentação.
- O banco gratuito do Render tem prazo de validade — confirmar os termos atuais.
  O `seed.py` da Fase 9 é o plano de recuperação se ele expirar.
- Senha do banco em produção: forte e diferente da usada no Docker local.

**Fase 9 — Apresentação (semana 12)**
Roteiro de demonstração, script `seed.py` com dados de exemplo, slides.
**Nunca demonstrar com banco vazio.**

---

## 5. BANCO DE DADOS

### Tabelas mínimas

| Tabela | Observação |
|---|---|
| `usuario` | admin, barbeiro **e cliente**, diferenciados por `papel` |
| `servico` | nome, **duracao_minutos**, preço, ativo |
| `agendamento` | `cliente_id` e `barbeiro_id` (ambos → `usuario`), início, fim, status |
| `agendamento_servico` | N:N — um agendamento pode ter corte + barba; guarda `preco_cobrado` |
| `produto` | nome, unidade, quantidade atual, estoque mínimo |
| `movimentacao_estoque` | entrada/saída, quantidade, motivo, data, responsável |

Status do agendamento: `agendado`, `concluido`, `cancelado`.
Papéis do usuário: `admin`, `barbeiro`, `cliente`.

**Não existe tabela `cliente`.** O cliente faz login, então é um `usuario` com
`papel = 'cliente'`. Consequência: `agendamento` referencia `usuario` duas vezes, uma
como cliente e outra como barbeiro. Ao desenhar o DER, rotule as duas setas.

Quatro pontos que costumam ser esquecidos:

- `duracao_minutos` no serviço é o que permite calcular o fim do agendamento e detectar conflito.
- `agendamento.fim` é **gravado**, não calculado na leitura. Isso mantém a consulta de
  conflito simples e impede que mudar a duração de um serviço deforme agendamentos passados.
- `agendamento_servico.preco_cobrado` guarda o preço vigente na marcação. O dashboard soma
  essa coluna, nunca `servico.preco` — senão um reajuste reescreve o faturamento de meses
  já fechados.
- Nunca alterar `produto.quantidade` sem gravar a movimentação correspondente.
  O dashboard depende dessas tabelas de histórico.

Valores monetários em `numeric`, nunca `float`. O requisito completo está em
`docs/requisitos.md`.

### Schema vem de migration, não de pgAdmin

O schema tem **uma única fonte de verdade**: os models Python + migrations versionadas.

Motivos:
- Três pessoas com três bancos locais divergem em uma semana se alguém criar tabela clicando.
- O Alembic controla o estado do schema numa tabela própria; tabelas criadas fora dele
  causam autogenerate errado.
- O deploy precisa aplicar o schema sozinho, sem interface gráfica.
- As migrations no Git são prova de processo para a avaliação acadêmica.

**pgAdmin serve para ler, não para escrever schema:** conferir o resultado da migration,
inspecionar dados, testar as consultas do dashboard antes de levá-las ao repository,
gerar o ERD para a documentação.

Modelar visualmente antes de escrever os models é válido — mas como rascunho descartável.

### Cuidados com Alembic

- `autogenerate` produz **rascunho**. Sempre ler a migration antes de aplicar.
- Ele **não detecta renomeação**: vê "coluna sumiu + coluna nova" e gera DROP + ADD,
  o que apaga os dados daquela coluna.

---

## 6. DOCKER

Serviços: `db` (Postgres 18), `backend`, `frontend` (nginx).

**Volume do Postgres 18:** monte em **`/var/lib/postgresql`**, sem o `/data` no final.
A imagem 18 mudou o `PGDATA` para `/var/lib/postgresql/18/docker`. O caminho antigo
`/var/lib/postgresql/data` vale até o Postgres 17 e não persiste nada no 18.

Pontos de atenção:

- Dentro da rede do Compose, o host do banco é **`db`**, não `localhost`.
  `DATABASE_URL = postgresql://user:senha@db:5432/barbearia`
- A porta exposta ao host é **`5433:5432`**, não `5432:5432`. Na máquina do Kauã existe
  um PostgreSQL 18 instalado no Windows ocupando a 5432. Do pgAdmin, portanto:
  `localhost:5433` é o container do projeto, `localhost:5432` é a instalação local.
  Nomeie a conexão com a porta junto — rodar migration no container e conferir no banco
  errado custa uma tarde.
- As variáveis `POSTGRES_*` são lidas **apenas no primeiro boot**, quando o volume está
  vazio. Trocar a senha no `.env` depois não tem efeito; exige `docker compose down -v`,
  que destrói o banco.
- O `db` precisa de **healthcheck** (`pg_isready`). Sem isso, o backend tenta conectar
  antes do Postgres aceitar conexões e quebra no start.
- `entrypoint.sh` no backend roda `flask db upgrade` antes do CMD.
- **Dev:** código montado como volume, `flask run --host=0.0.0.0 --debug`.
  **Produção:** código copiado para a imagem, `gunicorn`.
- `.env` no `.gitignore`; `.env.example` versionado com valores fake.
- Dockerfile: usuário não-root, `pip install` antes de copiar o código (cache de camadas).

---

## 7. CONVENÇÕES

- Código, variáveis e nomes de tabela em **português** (o domínio é em português).
- Commits: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`.
- Branches: `feature/nome-da-funcionalidade`, PR para `develop`.
  Sempre `git pull` na `develop` antes de criar branch nova.
  `main` só recebe merge de `develop` em versão estável.
- **Revisão cruzada obrigatória** nos PRs — sem isso as regras da seção 3 se dissolvem
  em duas semanas.
- `docs/api.md` atualizado sempre que um endpoint mudar: quem trabalha no front precisa
  do contrato antes do endpoint existir.
- Senha nunca em texto puro. Hash sempre por biblioteca, nunca implementado à mão.
- Valores monetários em `numeric`/`Decimal`, nunca `float`.

### Divisão de trabalho

Os três fazem front, back e banco. Kauã acumula DevOps.

Para isso não virar conflito de merge, **divida por módulo, não por camada**. Cada um
leva uma fatia vertical inteira — model, repository, service, schema, rota e tela do
mesmo domínio. Nunca "um faz todos os models, outro faz todos os services": isso põe
três pessoas no mesmo arquivo e dilui a responsabilidade por cada regra.

Exceção: a Fase 2 (auth) é feita por uma pessoa só, porque define o template.

---

## 8. LEMBRETE FINAL PARA O ASSISTENTE

Ao responder qualquer pergunta deste projeto, verifique:

- [ ] A equipe pediu código explicitamente? Se não, **não escreva**.
- [ ] A resposta explica o **porquê**, não só o **como**?
- [ ] A solução respeita as 5 regras de camada?
- [ ] Estou criando arquivos sem ter sido solicitado? Se sim, **pare**.

Na dúvida entre explicar e implementar, **explique e pergunte**.
