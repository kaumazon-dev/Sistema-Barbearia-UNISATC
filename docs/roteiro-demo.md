# Roteiro de demonstração — NextBarber

Apresentação de cerca de 15 min: 4 de slides, 8 de sistema no ar e 3 de
código e testes. Cada bloco tem um responsável; o nome fica a critério da equipe.

**Sistema:** <https://nextbarber-blush.vercel.app>
**Contas:** `admin@nextbarber.com` · `rafael@nextbarber.com` (barbeiro) · `cliente@nextbarber.com`
**Senha:** a `SENHA_DEMO` do topo de `backend/seed.py`

---

## Antes de começar (5 min antes)

- [ ] Abrir <https://barbearia-api-voje.onrender.com/health> e esperar o `{"status":"ok"}`.
      A API gratuita dorme depois de 15 min parada e leva uns 50 s para acordar.
- [ ] Abrir o sistema numa aba e já fazer o login como **admin**.
- [ ] Deixar abertas, em outras abas: a página **Actions** do GitHub (CI verde),
      o `docs/der.png` e o VS Code com `agendamento_service.py` aberto.
- [ ] Zoom do navegador em 110–125% para o projetor.
- [ ] **Plano B:** se o Render cair, rodar local com `docker compose up -d` e
      `docker compose exec backend python seed.py`, depois abrir <http://localhost:8080>.

---

## 1. Slides: problema, solução e arquitetura (4 min)

1. **Problema:** agenda no papel ou no WhatsApp gera horário em duplicidade e nenhuma visão de faturamento ou consumo de produto.
2. **Solução e papéis:** admin, barbeiro e cliente, cada um vendo só o que lhe cabe.
3. **Arquitetura:** rota → service → repository → model. Dizer as regras em uma frase cada: a rota não acessa o banco; o service não conhece HTTP; o model nunca sai da API.
4. **Stack e deploy:** React no Vercel, Flask + Postgres no Render, Docker local, CI no GitHub Actions.

## 2. Dashboard (1 min) — logado como admin

- Mostrar os cards e os gráficos de atendimentos e faturamento por semana e mês, o ranking de serviços, a taxa de cancelamento e os produtos em falta.
- **Frase-chave:** "toda essa agregação roda no banco, com `GROUP BY` e `SUM`; nenhuma lista é percorrida em Python. O faturamento soma o preço *cobrado* no dia, então um reajuste não reescreve meses já fechados."

## 3. Agenda: a regra mais importante (3 min)

1. **Agendamentos → Novo agendamento:** cliente qualquer, barbeiro **Rafael Costa**, *amanhã às 15:00*, serviços **Corte + barba** (50 min). Salvar.
   Mostrar que o fim (15:50) foi calculado sozinho pela soma das durações.
2. **Novo agendamento de novo:** outro cliente, mesmo barbeiro, *amanhã às 15:30*.
   → **Erro de conflito:** "Rafael Costa já tem agendamento… das 15:00 às 15:50".
3. Mesmo horário (15:30) com **outro barbeiro** → salva normalmente.
4. **Caso de borda:** Rafael *amanhã às 15:50*, exatamente quando o outro termina → **pode**.
   "O intervalo é fechado no início e aberto no fim: encostar não é sobrepor."
5. **Remarcar** o das 15:00 e depois **Cancelar horário**: o registro continua lá como cancelado (alimenta a taxa de cancelamento) e o horário fica livre.
6. **Frase-chave:** "a checagem está no service, e o banco tem uma `EXCLUDE constraint` como segunda barreira. Se duas pessoas clicarem ao mesmo tempo, o banco só aceita a primeira."

## 4. Estoque (2 min)

1. **Estoque:** mostrar o alerta de produtos em falta (Cera matte, Talco, Toalha descartável).
2. **Registrar saída** de 10 un de **Cera matte**, que só tem 5 → erro: estoque não fica negativo.
3. **Registrar entrada** de 20 un com motivo "Compra fornecedor" → sai do alerta.
4. Abrir o **histórico** do produto: cada mudança tem tipo, quantidade, motivo e responsável.
5. **Frase-chave:** "a quantidade nunca é editada direto: só muda junto com a movimentação, na mesma transação. E o histórico é imutável: um trigger no Postgres recusa `UPDATE` e `DELETE`, mesmo vindo do pgAdmin."

## 5. Visão por papel (1 min)

- Sair e entrar como **cliente** (`cliente@nextbarber.com`): o menu só mostra Agendamentos, Serviços e Minha conta, e a agenda só tem os agendamentos dele.
- "O que esconde a tela é o front; quem garante a permissão é o backend. Mesmo chamando a API direto, o cliente não enxerga o agendamento de outra pessoa."

## 6. Código e qualidade (3 min)

1. **VS Code:** abrir `agendamento_service.py` e mostrar `_garantir_horario_livre` (service decide) e o repository, que só busca.
2. **Testes:** mostrar `tests/unit/test_agendamento_service.py`. Os nomes contam as regras: `test_permite_comecar_exatamente_quando_o_outro_termina`, `test_recusa_englobar_um_existente_por_inteiro`, `test_corrida_no_mesmo_horario_vira_conflito`.
3. **GitHub Actions:** mais de 280 testes rodando contra um Postgres de verdade a cada PR. Mostrar o check verde.
4. **Processo:** branches `feature/*`, PR para a `develop`, migrations versionadas no Git e deploy a partir delas.

## 7. Fechamento (30 s)

Resumo em uma frase por módulo e abrir para perguntas.

---

## Perguntas prováveis

| Pergunta | Resposta curta |
|---|---|
| Por que separar service e repository? | O service tem a regra e dá para testar sem banco (repositório falso). O repository só lê e grava. Trocar o banco não mexe na regra. |
| Como evita dois agendamentos no mesmo horário ao mesmo tempo? | Checagem no service e `EXCLUDE constraint` (`tstzrange` + `btree_gist`) no Postgres. O segundo commit falha com `23P01` e vira um erro 409 amigável. |
| Por que `Numeric` e não `float` no dinheiro? | O `float` erra centavos (0,1 + 0,2 ≠ 0,3). |
| Onde fica a senha? | Só o hash bcrypt, e ele nunca sai da API: o que trafega é o schema Marshmallow, não o model. |
| E se mudar o preço de um serviço? | Agendamentos antigos guardam o `preco_cobrado` do dia. O faturamento passado não muda. |
| Por que não pgAdmin para criar tabela? | O schema vem só das migrations. Assim o banco de cada um, o do CI e o de produção são iguais, e o deploy aplica sozinho. |
| Por que o dado de exemplo é confiável? | O `seed.py` passa pelos mesmos services da API: se a regra recusaria, o seed também recusa. |
