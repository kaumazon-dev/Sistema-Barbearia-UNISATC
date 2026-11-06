class ErroNegocio(Exception):
    """base de todas as exeções; nao lançar direto"""
    codigo = "ERRO"

    def __init__(self, mensagem):
        self.mensagem = mensagem
        super().__init__(mensagem)


class NaoEncontrado(ErroNegocio):
    """USAR QUANDO NÃO FOR ENCONTRADO ALGUM DADO POIS NAO EXISTE"""
    codigo = "NAO_ENCONTRADO"


class RegraDeNegocioViolada(ErroNegocio):
    """USAR QUANDO REGRA VIOLADA, ESTOQUE INSUFICIENTE OU TENTATIVA DE CANCELAR AGENDA CONCLUIDA"""
    codigo = "REGRA_VIOLADA"


class NaoAutorizada(ErroNegocio):
    """USAR QUANDO NAO AUTENTICADO"""
    codigo = "NAO_AUTENTICADO"


class AcessoNegado(ErroNegocio):
    """USAR QUANDO NAO TIVER PERMISSAO"""
    codigo = "ACESSO_NEGADO"


class Conflito(ErroNegocio):
    """USAR QUANDO EMAIL DUPLICADO OU  HORARIO DUPLICADO OU HORARIO SOBREPOSTO"""
    codigo = "CONFLITO"
