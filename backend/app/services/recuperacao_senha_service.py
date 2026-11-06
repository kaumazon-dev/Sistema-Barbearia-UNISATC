"""Fluxo de "esqueci minha senha", em dois passos:

1. solicitar(email): se a conta existe e esta ativa, manda um link por e-mail.
2. redefinir(token, nova_senha): confere o token do link e grava a senha nova.

Sem Flask aqui dentro: token, enviador de e-mail e URL do front chegam prontos
pelo construtor, e os testes passam dubles no lugar deles.
"""

from app.core.exceptions import RegraDeNegocioViolada
from app.core.security import gerar_hash, impressao_confere

MENSAGEM_SOLICITACAO = (
    "Se o e-mail estiver cadastrado, você receberá um link para redefinir a senha."
)
MENSAGEM_LINK_INVALIDO = (
    "Link de redefinição inválido ou expirado. Solicite um novo."
)

ASSUNTO_EMAIL = "NextBarber - redefinição de senha"


class RecuperacaoSenhaService:
    def __init__(self, repositorio, tokens, enviador_email, url_frontend):
        self.repositorio = repositorio
        self.tokens = tokens
        self.enviador_email = enviador_email
        self.url_frontend = url_frontend.rstrip("/")

    def solicitar(self, email):
        usuario = self.repositorio.buscar_por_email(email)
        # E-mail inexistente ou conta desativada: nao faz nada, mas a rota
        # responde igual. Responder "e-mail nao encontrado" contaria a qualquer
        # um quais e-mails tem conta (a mesma regra do login).
        if usuario is None or not usuario.ativo:
            return

        token = self.tokens.gerar(usuario)
        link = f"{self.url_frontend}/?redefinir={token}"
        minutos = self.tokens.validade_segundos // 60
        corpo = (
            f"Olá, {usuario.nome}!\n\n"
            "Recebemos um pedido para redefinir a senha da sua conta no NextBarber.\n"
            f"Para criar uma senha nova, acesse o link abaixo (vale por {minutos} minutos):\n\n"
            f"{link}\n\n"
            "Se não foi você, ignore este e-mail: sua senha continua a mesma."
        )
        self.enviador_email.enviar(usuario.email, ASSUNTO_EMAIL, corpo)

    def redefinir(self, token, nova_senha):
        conteudo = self.tokens.ler(token)
        if conteudo is None:
            raise RegraDeNegocioViolada(MENSAGEM_LINK_INVALIDO)

        usuario = self.repositorio.get_by_id(conteudo["id"])
        # A impressao nao confere quando a senha ja foi trocada depois de o
        # link ser gerado: e isso que faz o link valer uma vez so.
        if (
            usuario is None
            or not usuario.ativo
            or not impressao_confere(conteudo, usuario.senha_hash)
        ):
            raise RegraDeNegocioViolada(MENSAGEM_LINK_INVALIDO)

        usuario.senha_hash = gerar_hash(nova_senha)
        return self.repositorio.update(usuario)
