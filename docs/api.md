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

Ainda não há endpoints de negócio. Documentar aqui cada endpoint antes de implementá-lo: método, rota, corpo de entrada, resposta de sucesso e erros possíveis.

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

Ainda sem paginação. A Fase 3 precisa decidir isso antes de a base de clientes
crescer.
