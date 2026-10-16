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
agendamento novo (RF12). A regra já está em
`ServicoService.buscar_ativos_para_agendamento`, que o agendamento da Fase 4 deve
usar.

Resposta `204` sem corpo.

| Status | `codigo` | Quando |
|---|---|---|
| 404 | `NAO_ENCONTRADO` | Id não existe |

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
