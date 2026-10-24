# Contrato da API

Base: `/api/v1`

## Formato de erro

Toda resposta de erro da API segue o mesmo formato JSON:

```json
{
  "erro": {
    "codigo": "NAO_ENCONTRADO",
    "mensagem": "Cliente 5 não existe."
  }
}
```

- `codigo`: identificador fixo do tipo de erro. O front deve decidir o comportamento por ele, nunca pelo texto da mensagem.
- `mensagem`: texto legível, pode ser exibido ao usuário.

Erros de validação de entrada incluem também o campo `campos`, com a lista de erros por campo:

```json
{
  "erro": {
    "codigo": "DADOS_INVALIDOS",
    "mensagem": "Dados de entrada inválidos.",
    "campos": {
      "email": ["Not a valid email address."]
    }
  }
}
```

## Códigos de erro

| Status | `codigo` | Quando acontece |
|---|---|---|
| 400 | (código da exceção) | Erro de negócio sem status mapeado |
| 401 | `NAO_AUTENTICADO` | Usuário não autenticado |
| 403 | `ACESSO_NEGADO` | Usuário autenticado, mas sem permissão |
| 404 | `NAO_ENCONTRADO` | Registro não existe |
| 404 | `NOT_FOUND` | Rota não existe |
| 405 | `METHOD_NOT_ALLOWED` | Método HTTP não aceito pela rota |
| 409 | `CONFLITO` | E-mail duplicado, horário duplicado ou sobreposto |
| 422 | `REGRA_VIOLADA` | Regra de negócio violada (ex.: estoque insuficiente, cancelar agendamento concluído) |
| 422 | `DADOS_INVALIDOS` | Corpo da requisição não passou na validação do schema |
| 500 | `ERRO_INTERNO` | Erro inesperado no servidor. Detalhes ficam só no log |

Erros do Werkzeug (rota inexistente, método não permitido etc.) usam como `codigo` o nome do erro HTTP em maiúsculas, com `_` no lugar de espaço.

Erros de token JWT (ausente, inválido, expirado, revogado) seguem o mesmo formato, com `codigo` igual a `NAO_AUTENTICADO` e status 401.

As mensagens de erro de validação do Marshmallow vêm em inglês (texto padrão da biblioteca). O front deve decidir o comportamento pelo `codigo` e pela chave do campo em `campos`, nunca pelo texto.

## Endpoints

Documentar aqui cada endpoint antes de implementá-lo: método, rota, corpo de entrada, resposta de sucesso e erros possíveis.

---

# Autenticação (Fase 2)

## Como autenticar

`POST /api/v1/auth/login` devolve um token JWT. As rotas protegidas exigem o
cabeçalho:

```
Authorization: Bearer <token>
```

O token carrega o id do usuário na claim `sub` (como string, exigência do padrão
JWT) e o papel na claim `papel`. Validade padrão de 60 minutos, configurável pela
variável de ambiente `JWT_EXPIRA_MINUTOS`.

Consequência de guardar o papel no token: promover, rebaixar ou desativar um
usuário **não** invalida o token que ele já tem em mãos. O papel novo passa a
valer no próximo login. É uma troca aceita de propósito — evita uma consulta ao
banco por requisição.

## POST /auth/register

Cadastro público. Cria sempre com `papel = "cliente"`.

Para criar admin ou barbeiro use o `seed.py` (Fase 9) ou um endpoint restrito a
admin. O campo `papel` **não** é aceito no corpo: se fosse, qualquer pessoa se
cadastraria como admin.

Corpo:

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `nome` | string | sim | 3 a 120 caracteres, medidos após remover espaços das pontas |
| `email` | string | sim | formato de e-mail, até 160 caracteres, único |
| `senha` | string | sim | mínimo 8 caracteres e máximo 72 **bytes** |
| `telefone` | string | não | até 20 caracteres |

O e-mail é normalizado para minúsculas antes de gravar, então `Joao@X.com` e
`joao@x.com` são o mesmo cadastro.

O limite da senha é em bytes, não em caracteres, porque é um limite do bcrypt.
Em UTF-8 um caractere acentuado ocupa 2 bytes, então uma senha de 40 caracteres
acentuados já passa de 72 bytes e é recusada.

```json
{
  "nome": "João da Silva",
  "email": "joao@exemplo.com",
  "senha": "senha-boa-123",
  "telefone": "48999990000"
}
```

Resposta `201`:

```json
{
  "id": 1,
  "nome": "João da Silva",
  "email": "joao@exemplo.com",
  "telefone": "48999990000",
  "papel": "cliente",
  "ativo": true,
  "criado_em": "2026-10-11T21:07:23.614521+00:00"
}
```

`senha_hash` nunca aparece na resposta.

| Status | `codigo` | Quando |
|---|---|---|
| 409 | `CONFLITO` | E-mail já cadastrado |
| 422 | `DADOS_INVALIDOS` | Campo faltando, e-mail inválido, senha curta ou longa demais, ou campo desconhecido (inclusive `papel`) |

## POST /auth/login

Corpo:

```json
{ "email": "joao@exemplo.com", "senha": "senha-boa-123" }
```

Resposta `200`:

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "usuario": {
    "id": 1,
    "nome": "João da Silva",
    "email": "joao@exemplo.com",
    "telefone": "48999990000",
    "papel": "cliente",
    "ativo": true,
    "criado_em": "2026-10-11T21:07:23.614521+00:00"
  }
}
```

| Status | `codigo` | Quando |
|---|---|---|
| 401 | `NAO_AUTENTICADO` | E-mail inexistente, senha errada **ou** usuário desativado |
| 422 | `DADOS_INVALIDOS` | E-mail ou senha ausentes |

Os três casos de 401 devolvem a mesma mensagem, `"E-mail ou senha inválidos."`,
de propósito. Mensagens diferentes contariam a quem está tentando invadir quais
e-mails existem no sistema.

O login também gasta o mesmo tempo nos três casos, por volta de 200 ms. Quando o
e-mail não existe, o service roda uma verificação de senha descartável antes de
recusar. Sem isso a resposta sairia em 2 ms contra 200 ms do caminho normal, e o
tempo entregaria quais e-mails estão cadastrados mesmo com a mensagem igual.

## GET /auth/me

Perfil do usuário autenticado. Exige token, qualquer papel.

Resposta `200`: o mesmo objeto de usuário do cadastro.

| Status | `codigo` | Quando |
|---|---|---|
| 401 | `NAO_AUTENTICADO` | Token ausente, inválido ou expirado |
| 404 | `NAO_ENCONTRADO` | Usuário do token não existe mais ou foi desativado |

## GET /auth/usuarios

Lista usuários. **Exige papel `admin`.**

Parâmetro de consulta opcional `papel` (`admin`, `barbeiro` ou `cliente`) para
filtrar: `GET /api/v1/auth/usuarios?papel=barbeiro`.

`papel` vazio (`?papel=`) é tratado como ausente e devolve a lista completa, o
que permite ao front mandar o valor de um `select` sem opção escolhida.
Parâmetros desconhecidos são ignorados.

Resposta `200`: lista de objetos de usuário.

| Status | `codigo` | Quando |
|---|---|---|
| 401 | `NAO_AUTENTICADO` | Token ausente, inválido ou expirado |
| 403 | `ACESSO_NEGADO` | Autenticado, mas o papel no token não é `admin` |
| 422 | `DADOS_INVALIDOS` | `papel` fora de `admin`, `barbeiro` e `cliente` |

Sem paginação: é uma rota administrativa de poucos registros. A listagem que
cresce, a de clientes, é paginada (ver `GET /clientes`).

---

# Clientes (Fase 3)

Cliente **não tem tabela própria**: é um registro de `usuario` com
`papel = "cliente"` (ver DER). Por estas rotas, admin e barbeiro simplesmente não
existem: `GET /clientes/<id>` de um barbeiro devolve 404.

Cliente nunca é apagado de fato. `DELETE` só desativa (`ativo = false`), porque o
histórico de agendamentos e o dashboard dependem do registro (RF06). Cliente
desativado não consegue fazer login.

| Rota | Papel exigido |
|---|---|
| `GET /clientes` | `admin` ou `barbeiro` |
| `GET /clientes/<id>` | `admin` ou `barbeiro` |
| `POST /clientes` | `admin` |
| `PUT /clientes/<id>` | `admin` |
| `DELETE /clientes/<id>` | `admin` |

Barbeiro só lê: precisa escolher o cliente ao marcar horário (Fase 4).

Todas as rotas respondem `401 NAO_AUTENTICADO` sem token e `403 ACESSO_NEGADO`
com papel errado.

O objeto de cliente é o mesmo objeto de usuário da autenticação.

## Paginação

Listagens paginadas aceitam os parâmetros de consulta:

| Parâmetro | Padrão | Regra |
|---|---|---|
| `pagina` | `1` | inteiro ≥ 1 |
| `por_pagina` | `20` | inteiro de 1 a 100 |

E respondem sempre no envelope:

```json
{
  "itens": [ ... ],
  "pagina": 1,
  "por_pagina": 20,
  "total": 41,
  "paginas": 3
}
```

Página além da última devolve `itens` vazio, não erro. Parâmetro vazio
(`?busca=`) é tratado como ausente e parâmetros desconhecidos são ignorados.

## GET /clientes

Lista paginada, ordenada por nome.

| Parâmetro | Regra |
|---|---|
| `busca` | opcional. Procura no nome **ou** no telefone, sem diferenciar maiúsculas (RF08). `%` e `_` são tratados como texto |
| `ativo` | opcional, `true` ou `false`. Ausente traz ativos e inativos |
| `pagina`, `por_pagina` | ver Paginação |

Exemplo: `GET /api/v1/clientes?busca=joão&ativo=true&pagina=1`

Resposta `200`: envelope de paginação com objetos de cliente em `itens`.

| Status | `codigo` | Quando |
|---|---|---|
| 422 | `DADOS_INVALIDOS` | `pagina` ou `por_pagina` fora da faixa, `ativo` não booleano |

## GET /clientes/&lt;id&gt;

Resposta `200`: objeto de cliente.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Id não existe ou não é de um cliente |

## POST /clientes

Cadastro feito pelo admin. Mesmo corpo e mesmas regras de `POST /auth/register`
(`nome`, `email`, `senha`, `telefone`); o papel é sempre `cliente`.

Resposta `201`: objeto de cliente.

| Status | `codigo` | Quando |
|---|---|---|
| 409 | `CONFLITO` | E-mail já cadastrado |
| 422 | `DADOS_INVALIDOS` | Mesmas regras do cadastro público |

## PUT /clientes/&lt;id&gt;

Atualização parcial: só os campos enviados mudam.

| Campo | Tipo | Regra |
|---|---|---|
| `nome` | string | 3 a 120 caracteres |
| `email` | string | formato de e-mail, até 160, único |
| `telefone` | string ou `null` | até 20 caracteres |
| `ativo` | boolean | `true` reativa um cliente desativado |

`senha` e `papel` **não** são aceitos: viram 422.

```json
{ "telefone": "48988887777" }
```

Resposta `200`: objeto de cliente atualizado.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Id não existe ou não é de um cliente |
| 409 | `CONFLITO` | E-mail já usado por outro usuário |
| 422 | `DADOS_INVALIDOS` | Campo inválido ou desconhecido |

## DELETE /clientes/&lt;id&gt;

Desativa o cliente (exclusão lógica). Repetir em cliente já desativado não é erro.

Resposta `204` sem corpo.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Id não existe ou não é de um cliente |

O histórico de agendamentos do cliente (RF09) entra na Fase 4, junto com a
tabela `agendamento`.

---

# Serviços (Fase 3)

| Rota | Papel exigido |
|---|---|
| `GET /servicos` | qualquer usuário autenticado |
| `GET /servicos/<id>` | qualquer usuário autenticado |
| `POST /servicos` | `admin` |
| `PUT /servicos/<id>` | `admin` |
| `DELETE /servicos/<id>` | `admin` |

Leitura é aberta a todos os papéis porque o cliente escolhe os serviços ao marcar
horário. **Quem não é admin só enxerga serviço ativo**: o filtro `ativo` é
ignorado e um serviço inativo responde 404.

Objeto de serviço:

```json
{
  "id": 1,
  "nome": "Corte",
  "duracao_minutos": 30,
  "preco": "35.90",
  "ativo": true
}
```

**`preco` sai como string**, sempre com duas casas. Número em JSON vira `float`
no JavaScript e erra centavos (RNF09). O front deve exibir a string como está ou
converter só para formatar, nunca para somar.

Serviço nunca é apagado de fato: agendamentos antigos apontam para ele. Mudar
preço ou duração não altera agendamentos já marcados, porque o preço cobrado e o
horário de fim ficam gravados no agendamento (RN02, RN03).

## GET /servicos

Lista sem paginação (poucos registros), ordenada por nome.

| Parâmetro | Regra |
|---|---|
| `ativo` | opcional, `true` ou `false`. Só vale para admin |

Resposta `200`: lista de objetos de serviço.

## GET /servicos/&lt;id&gt;

Resposta `200`: objeto de serviço.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Id não existe, ou serviço inativo e quem pede não é admin |

## POST /servicos

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `nome` | string | sim | 2 a 120 caracteres, após remover espaços das pontas |
| `duracao_minutos` | inteiro | sim | 1 a 480. `30.5` ou `"30"` são recusados |
| `preco` | string ou número | sim | 0 a 99999999.99, no máximo 2 casas decimais. Prefira string: `"35.90"` |

`35.999` é recusado em vez de arredondado: mais de duas casas quase sempre é erro
de digitação.

```json
{ "nome": "Corte", "duracao_minutos": 30, "preco": "35.90" }
```

Resposta `201`: objeto de serviço, criado ativo.

| Status | `codigo` | Quando |
|---|---|---|
| 422 | `DADOS_INVALIDOS` | Campo faltando, fora da faixa ou desconhecido |

## PUT /servicos/&lt;id&gt;

Atualização parcial com os mesmos campos do POST, mais `ativo` (boolean) para
reativar.

```json
{ "preco": "40.00" }
```

Resposta `200`: objeto de serviço atualizado.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Id não existe |
| 422 | `DADOS_INVALIDOS` | Campo inválido ou desconhecido |

## DELETE /servicos/&lt;id&gt;

Desativa o serviço (exclusão lógica). Serviço desativado não pode entrar em
agendamento novo (RF12). A regra fica em
`ServicoService.buscar_ativos_para_agendamento`, usada pelo agendamento.

Resposta `204` sem corpo.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Id não existe |

---

# Agendamentos (Fase 4)

| Rota | Papel exigido |
|---|---|
| `GET /agendamentos` | qualquer usuário autenticado |
| `GET /agendamentos/<id>` | qualquer usuário autenticado |
| `POST /agendamentos` | qualquer usuário autenticado |
| `PATCH /agendamentos/<id>` | qualquer usuário autenticado |
| `POST /agendamentos/<id>/cancelar` | qualquer usuário autenticado |
| `POST /agendamentos/<id>/concluir` | `admin` ou `barbeiro` |

Admin e barbeiro enxergam e gerenciam a agenda inteira. **Cliente só enxerga e
mexe nos próprios agendamentos (RF21)**: o de outra pessoa responde 404, como se
não existisse, e ao marcar o cliente é sempre ele mesmo (o `cliente_id` do corpo
é ignorado).

## Data, hora e fuso

- **Entrada:** ISO 8601 **com fuso obrigatório**, sem segundos.
  `"2026-10-20T14:30:00-03:00"` ou `"2026-10-20T17:30:00Z"`. Sem fuso
  (`"2026-10-20T14:30:00"`) dá 422: não dá para saber se é Brasília ou UTC.
  No JavaScript, `new Date(...).toISOString()` já manda em UTC com `Z`.
- **Saída:** sempre no fuso da barbearia (`America/Sao_Paulo`), com o offset:
  `"2026-10-20T14:30:00-03:00"`.
- **Banco:** `timestamptz`. Nenhum horário sem fuso circula no backend.
- O filtro `dia` é o dia de Brasília (00:00 até 24:00 de Brasília).

## Status

| Status | Pode ir para |
|---|---|
| `agendado` | `concluido`, `cancelado` |
| `concluido` | — (final) |
| `cancelado` | — (final) |

Só agendamento `agendado` pode ser remarcado. Cancelar **não apaga** o registro:
o dashboard precisa dele para a taxa de cancelamento (RF19).

## Regra de conflito (RN01)

Nenhum agendamento do mesmo barbeiro pode se sobrepor a outro. O intervalo é
`[inicio, fim)`: um agendamento que começa exatamente quando outro termina é
válido. Agendamento `cancelado` não bloqueia horário; `concluido` bloqueia.

A regra é checada no service (que monta a mensagem de erro) e garantida também
no banco por uma `EXCLUDE` constraint, para o caso de duas pessoas marcarem o
mesmo horário ao mesmo tempo.

Conflito responde `409 CONFLITO` com mensagem pronta para exibir:

```json
{
  "erro": {
    "codigo": "CONFLITO",
    "mensagem": "João já tem agendamento em 20/10/2026 das 13:30 às 14:30. Escolha outro horário."
  }
}
```

Objeto de agendamento:

```json
{
  "id": 7,
  "cliente": { "id": 4, "nome": "Ana" },
  "barbeiro": { "id": 2, "nome": "João" },
  "inicio": "2026-10-20T13:30:00-03:00",
  "fim": "2026-10-20T14:30:00-03:00",
  "status": "agendado",
  "observacao": null,
  "servicos": [
    { "servico_id": 1, "nome": "Corte", "preco_cobrado": "35.00" },
    { "servico_id": 2, "nome": "Barba", "preco_cobrado": "25.50" }
  ],
  "total": "60.50",
  "criado_em": "2026-10-18T10:02:11.481203-03:00"
}
```

- `fim` = `inicio` + soma das durações dos serviços, **gravado** na marcação
  (RF14). Mudar a duração de um serviço depois não desloca a agenda (RN03).
- `preco_cobrado` é cópia do preço do serviço na marcação (RN02). `total` é a
  soma deles. Ambos saem como string, igual ao preço do serviço.

## GET /agendamentos

Lista paginada, em ordem de horário (RF17).

| Parâmetro | Regra |
|---|---|
| `dia` | opcional, `AAAA-MM-DD`. Agendamentos que começam nesse dia (Brasília) |
| `barbeiro_id` | opcional |
| `cliente_id` | opcional. Para cliente logado é sempre ele mesmo |
| `status` | opcional, `agendado`, `concluido` ou `cancelado` |
| `pagina`, `por_pagina` | ver Paginação |

Exemplo: `GET /api/v1/agendamentos?dia=2026-10-20&barbeiro_id=2`

Resposta `200`: envelope de paginação com objetos de agendamento em `itens`.

| Status | `codigo` | Quando |
|---|---|---|
| 422 | `DADOS_INVALIDOS` | `dia` fora do formato, `status` desconhecido, paginação fora da faixa |

## GET /agendamentos/&lt;id&gt;

Resposta `200`: objeto de agendamento.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Id não existe, ou é de outro cliente |

## POST /agendamentos

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `cliente_id` | inteiro | admin e barbeiro | Usuário com papel `cliente`, ativo. Ignorado quando quem marca é cliente |
| `barbeiro_id` | inteiro | sim | Usuário com papel `barbeiro`, ativo |
| `inicio` | string | sim | Ver "Data, hora e fuso". Não pode estar no passado |
| `servico_ids` | lista de inteiros | sim | 1 a 10 serviços ativos. Repetidos contam uma vez |
| `observacao` | string | não | até 500 caracteres |

```json
{
  "cliente_id": 4,
  "barbeiro_id": 2,
  "inicio": "2026-10-20T13:30:00-03:00",
  "servico_ids": [1, 2]
}
```

Resposta `201`: objeto de agendamento, com status `agendado`.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Cliente, barbeiro ou serviço não existe (ou tem outro papel) |
| 409 | `CONFLITO` | Horário sobrepõe outro agendamento do barbeiro |
| 422 | `REGRA_VIOLADA` | Horário no passado, serviço, cliente ou barbeiro desativado |
| 422 | `DADOS_INVALIDOS` | Campo faltando, horário sem fuso ou com segundos, campo desconhecido |

## PATCH /agendamentos/&lt;id&gt;

Remarca: novo início e, opcionalmente, outro barbeiro. **A duração é mantida**
(a do próprio agendamento, não a atual dos serviços) e a regra de conflito é
aplicada de novo, ignorando o próprio agendamento (RF18). Serviços não mudam por
aqui: para trocar serviços, cancele e marque de novo.

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `inicio` | string | sim | Ver "Data, hora e fuso". Não pode estar no passado |
| `barbeiro_id` | inteiro | não | Barbeiro ativo |

```json
{ "inicio": "2026-10-20T15:00:00-03:00" }
```

Resposta `200`: objeto de agendamento atualizado.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Agendamento ou barbeiro não existe, ou agendamento de outro cliente |
| 409 | `CONFLITO` | Novo horário sobrepõe outro agendamento |
| 422 | `REGRA_VIOLADA` | Agendamento não está `agendado`, horário no passado, barbeiro desativado |
| 422 | `DADOS_INVALIDOS` | Campo inválido ou desconhecido |

## POST /agendamentos/&lt;id&gt;/cancelar

Sem corpo. Muda o status para `cancelado` e libera o horário. Resposta `200`:
objeto de agendamento.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Id não existe, ou é de outro cliente |
| 422 | `REGRA_VIOLADA` | Agendamento já concluído ou cancelado |

## POST /agendamentos/&lt;id&gt;/concluir

Sem corpo. Só admin e barbeiro (RF20). Resposta `200`: objeto de agendamento.

| Status | `codigo` | Quando |
|---|---|---|
| 403 | `ACESSO_NEGADO` | Quem pede é cliente |
| 404 | `NAO_ENCONTRADO` | Id não existe |
| 422 | `REGRA_VIOLADA` | Agendamento já concluído ou cancelado |

---

# Estoque (Fase 5)

| Rota | Papel exigido |
|---|---|
| `GET /produtos` | `admin` |
| `GET /produtos/em-falta` | `admin` |
| `GET /produtos/<id>` | `admin` |
| `POST /produtos` | `admin` |
| `PUT /produtos/<id>` | `admin` |
| `DELETE /produtos/<id>` | `admin` |
| `POST /produtos/<id>/entradas` | `admin` |
| `POST /produtos/<id>/saidas` | `admin` |
| `GET /produtos/<id>/movimentacoes` | `admin` |

Estoque é área do admin (RF22). Barbeiro e cliente recebem `403` em todas as rotas.

Objeto de produto:

```json
{
  "id": 1,
  "nome": "Pomada",
  "unidade": "g",
  "quantidade_atual": "10.50",
  "estoque_minimo": "5.00",
  "em_falta": false,
  "ativo": true
}
```

- `quantidade_atual` e `estoque_minimo` saem como **string** com duas casas, pelo
  mesmo motivo do `preco` do serviço (RNF09). Aceitam fração porque `ml` e `g`
  podem ser fracionados.
- `em_falta` é `true` quando `quantidade_atual <= estoque_minimo` (RF27). Estar
  exatamente no mínimo já conta como em falta.

**A quantidade nunca é alterada direto (RN04).** Não existe campo
`quantidade_atual` no cadastro nem na edição: mandar esse campo dá `422`. O
produto nasce com quantidade `0` e o estoque inicial entra por
`POST /produtos/<id>/entradas`. Toda mudança de quantidade grava uma
movimentação, na mesma transação.

## GET /produtos

Lista sem paginação, ordenada por nome.

| Parâmetro | Regra |
|---|---|
| `ativo` | opcional, `true` ou `false` |

Resposta `200`: lista de objetos de produto.

## GET /produtos/em-falta

Produtos **ativos** com `quantidade_atual <= estoque_minimo`, ordenados por nome
(RF27). É a mesma consulta do card "produtos em falta" do dashboard (RF32).

Resposta `200`: lista de objetos de produto.

## GET /produtos/&lt;id&gt;

Resposta `200`: objeto de produto.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Id não existe |

## POST /produtos

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `nome` | string | sim | 2 a 120 caracteres, após remover espaços das pontas |
| `unidade` | string | sim | `un`, `ml` ou `g` |
| `estoque_minimo` | string ou número | não | padrão `0`. De 0 a 99999999.99, no máximo 2 casas |

```json
{ "nome": "Pomada", "unidade": "g", "estoque_minimo": "5" }
```

Resposta `201`: objeto de produto, ativo e com `quantidade_atual` `"0.00"`.

| Status | `codigo` | Quando |
|---|---|---|
| 422 | `DADOS_INVALIDOS` | Campo faltando, fora da faixa ou desconhecido (inclusive `quantidade_atual`) |

## PUT /produtos/&lt;id&gt;

Atualização parcial com os mesmos campos do POST, mais `ativo` (boolean) para
reativar. `quantidade_atual` continua proibido.

```json
{ "estoque_minimo": "8" }
```

Resposta `200`: objeto de produto atualizado.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Id não existe |
| 422 | `DADOS_INVALIDOS` | Campo inválido ou desconhecido |

## DELETE /produtos/&lt;id&gt;

Desativa o produto (exclusão lógica): o histórico de movimentações continua
apontando para ele. Produto desativado não aceita entrada nem saída e não aparece
em `/em-falta`.

Resposta `204` sem corpo.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Id não existe |

## POST /produtos/&lt;id&gt;/entradas e POST /produtos/&lt;id&gt;/saidas

Registra uma movimentação e atualiza a quantidade do produto, numa transação só
(RF24, RF25). O tipo vem da rota; o responsável vem do token.

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `quantidade` | string ou número | sim | maior que 0, até 99999999.99, no máximo 2 casas. Sempre positiva: o sinal vem da rota |
| `motivo` | string | não | até 160 caracteres. Texto vazio vira `null` |

```json
{ "quantidade": "2", "motivo": "uso no atendimento" }
```

Resposta `201`: objeto de movimentação, com o produto já atualizado em
`produto`:

```json
{
  "id": 12,
  "tipo": "saida",
  "quantidade": "2.00",
  "motivo": "uso no atendimento",
  "usuario": { "id": 1, "nome": "Admin" },
  "criado_em": "2026-10-20T18:45:00-03:00",
  "produto": { "id": 1, "nome": "Pomada", "unidade": "g", "quantidade_atual": "8.50", "estoque_minimo": "5.00", "em_falta": false, "ativo": true }
}
```

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Produto não existe |
| 422 | `REGRA_VIOLADA` | Saída maior que a quantidade disponível (RF26), ou produto desativado |
| 422 | `DADOS_INVALIDOS` | Quantidade zero, negativa, com mais de 2 casas, ou campo desconhecido |

Exemplo de saída recusada:

```json
{
  "erro": {
    "codigo": "REGRA_VIOLADA",
    "mensagem": "Estoque insuficiente de Pomada: disponível 2.00 g, pedido 3 g."
  }
}
```

## GET /produtos/&lt;id&gt;/movimentacoes

Histórico paginado do produto, da movimentação mais recente para a mais antiga.

| Parâmetro | Regra |
|---|---|
| `tipo` | opcional, `entrada` ou `saida` |
| `pagina`, `por_pagina` | ver Paginação |

Resposta `200`: envelope de paginação com objetos de movimentação em `itens`,
**sem** o campo `produto` (ali seria o saldo de hoje, não o da época).

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Produto não existe |
| 422 | `DADOS_INVALIDOS` | `tipo` desconhecido, paginação fora da faixa |

---

# Dashboard (Fase 6)

| Rota | Papel exigido |
|---|---|
| `GET /dashboard/atendimentos` | `admin` |
| `GET /dashboard/faturamento` | `admin` |
| `GET /dashboard/servicos-ranking` | `admin` |
| `GET /dashboard/cancelamento` | `admin` |

Dashboard é área do admin. Barbeiro e cliente recebem `403` em todas as rotas.

Produtos em falta (RF32) não têm rota própria aqui: o card do dashboard usa
`GET /produtos/em-falta`, da Fase 5.

As respostas já vêm no formato do Chart.js: `labels` e `valores` alinhados por
posição, prontos para `data.labels` e `data.datasets[0].data`.

As regras de cada métrica estão na RN05 de `docs/requisitos.md`.

## Período

Parâmetros de consulta aceitos por todas as rotas:

| Parâmetro | Regra |
|---|---|
| `de` | opcional, data `AAAA-MM-DD` |
| `ate` | opcional, data `AAAA-MM-DD`, **inclusivo** |

- As datas são dias no fuso da barbearia (`America/Sao_Paulo`).
  `de=2026-10-01&ate=2026-10-31` é o mês de outubro inteiro.
- Informe os dois ou nenhum. Sem nenhum, vale o mês atual, do dia 1 até hoje.
- `ate` não pode ser anterior a `de`, e o intervalo máximo é de 366 dias.
- Toda resposta devolve `de` e `ate` com o período efetivamente usado. Assim o front
  descobre quais datas o padrão aplicou.

Erros comuns às quatro rotas:

| Status | `codigo` | Quando |
|---|---|---|
| 401 | `NAO_AUTENTICADO` | Sem token |
| 403 | `ACESSO_NEGADO` | Papel diferente de `admin` |
| 422 | `DADOS_INVALIDOS` | Data inválida, só uma das datas, `ate` antes de `de`, intervalo acima de 366 dias, parâmetro fora da faixa |

## GET /dashboard/atendimentos

Quantidade de atendimentos **concluídos** por semana ou por mês (RF28). Um
agendamento com mais de um serviço conta como um atendimento.

| Parâmetro | Regra |
|---|---|
| `granularidade` | opcional, `semana` (padrão) ou `mes` |

Resposta `200`:

```json
{
  "granularidade": "semana",
  "de": "2026-10-01",
  "ate": "2026-10-31",
  "labels": ["2026-09-28", "2026-10-05", "2026-10-12", "2026-10-19", "2026-10-26"],
  "valores": [19, 34, 34, 37, 0]
}
```

- **Semana:** o rótulo é a data da segunda-feira que abre a semana. A primeira
  e a última semana podem começar antes de `de` ou terminar depois de `ate`, mas só
  contam os dias dentro do período.
- **Mês:** o rótulo é `AAAA-MM`.
- Períodos sem nenhum atendimento aparecem com `0`, para o gráfico não pular datas.

## GET /dashboard/faturamento

Soma do preço cobrado dos atendimentos **concluídos**, por semana ou por mês
(RF29). Usa `preco_cobrado`, então um reajuste no serviço não altera meses já
fechados.

Parâmetros e rótulos iguais aos de `/dashboard/atendimentos`.

Resposta `200`:

```json
{
  "granularidade": "mes",
  "de": "2026-08-01",
  "ate": "2026-10-31",
  "labels": ["2026-08", "2026-09", "2026-10"],
  "valores": ["7560.00", "8150.00", "6880.00"]
}
```

`valores` sai como **string** com duas casas, como todo valor monetário da API
(RNF09). O Chart.js aceita string numérica; para somar no JavaScript, converta com
`Number()` só na hora de exibir.

## GET /dashboard/servicos-ranking

Serviços mais vendidos em atendimentos **concluídos** (RF30), do mais vendido para
o menos. Em caso de empate, a ordem é pelo nome.

| Parâmetro | Regra |
|---|---|
| `limite` | opcional, de 1 a 20, padrão 5 |

Resposta `200`:

```json
{
  "de": "2026-10-01",
  "ate": "2026-10-31",
  "labels": ["Corte", "Barba", "Pigmentação"],
  "valores": [80, 45, 30],
  "receitas": ["3200.00", "1125.00", "1800.00"]
}
```

`valores` é a quantidade de vezes que o serviço foi realizado. `receitas` é a soma
do preço cobrado daquele serviço, alinhada pela mesma posição.

## GET /dashboard/cancelamento

Taxa de cancelamento no período (RF31): cancelados ÷ (concluídos + cancelados).
Agendamentos com status `agendado` ficam fora.

Resposta `200`:

```json
{
  "de": "2026-08-01",
  "ate": "2026-10-31",
  "concluidos": 417,
  "cancelados": 64,
  "total": 481,
  "taxa": "13.31",
  "labels": ["Concluídos", "Cancelados"],
  "valores": [417, 64]
}
```

- `taxa` é um percentual com duas casas, arredondado meio para cima
  (3,125% vira `"3.13"`).
- `taxa` é `null` quando não há nenhum concluído nem cancelado no período: sem
  desfecho, a taxa não existe, e `0` daria a impressão errada.
- `labels` e `valores` servem direto para um gráfico de rosca.

---

# Testes

```
docker compose exec backend python -m pytest
```

Os testes de integração (`tests/integration`) usam um banco separado, definido
em `DATABASE_URL_TEST`. Ele precisa existir antes da primeira execução:

```
docker compose exec db createdb -U barbearia barbearia_test
```

As tabelas são criadas e apagadas pelos próprios testes. Nunca aponte
`DATABASE_URL_TEST` para o banco de desenvolvimento.
