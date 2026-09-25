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

Erros de token JWT (ausente, expirado, inválido) ainda não seguem este formato. Serão ajustados na Fase 2.

## Endpoints

Ainda não há endpoints de negócio. Documentar aqui cada endpoint antes de implementá-lo: método, rota, corpo de entrada, resposta de sucesso e erros possíveis.
