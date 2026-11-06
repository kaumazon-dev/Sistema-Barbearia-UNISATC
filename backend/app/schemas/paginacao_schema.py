from marshmallow import EXCLUDE, Schema, fields, pre_load, validate

POR_PAGINA_PADRAO = 20
POR_PAGINA_MAXIMO = 100


def descartar_vazios(dados):
    """Parametro de consulta vazio (?busca=) e tratado como ausente.

    Permite ao front mandar o valor de um input ou select sem nada escolhido.
    """
    if not isinstance(dados, dict):
        return dados
    return {chave: valor for chave, valor in dados.items() if valor != ""}


class PaginacaoSchema(Schema):
    """Base dos filtros de listagens paginadas."""

    class Meta:
        unknown = EXCLUDE

    pagina = fields.Integer(load_default=1, validate=validate.Range(min=1))
    por_pagina = fields.Integer(
        load_default=POR_PAGINA_PADRAO,
        validate=validate.Range(min=1, max=POR_PAGINA_MAXIMO),
    )

    @pre_load
    def ignorar_vazios(self, dados, **kwargs):
        return descartar_vazios(dados)


def montar_pagina(itens_serializados, total, pagina, por_pagina):
    """Envelope padrao de resposta paginada."""
    return {
        "itens": itens_serializados,
        "pagina": pagina,
        "por_pagina": por_pagina,
        "total": total,
        "paginas": (total + por_pagina - 1) // por_pagina,
    }
