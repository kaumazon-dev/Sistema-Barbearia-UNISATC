from sqlalchemy.exc import IntegrityError

from app.core.exceptions import Conflito, NaoAutorizada, NaoEncontrado
from app.core.security import (
    gastar_tempo_de_verificacao,
    gerar_hash,
    verificar_senha,
)
from app.models.usuario import PAPEL_CLIENTE, Usuario

# E-mail inexistente, senha errada e usuario desativado devolvem esta mesma
# mensagem: diferenciar informaria quais e-mails existem.
MENSAGEM_CREDENCIAIS_INVALIDAS = "E-mail ou senha inválidos."


class AuthService:
    def __init__(self, repositorio):
        self.repositorio = repositorio

    def cadastrar(self, dados):
        email = dados["email"]
        if self.repositorio.buscar_por_email(email) is not None:
            raise Conflito(f"Já existe um usuário cadastrado com o e-mail {email}.")

        usuario = Usuario(
            nome=dados["nome"],
            email=email,
            senha_hash=gerar_hash(dados["senha"]),
            telefone=dados.get("telefone"),
            papel=PAPEL_CLIENTE,
        )

        try:
            return self.repositorio.create(usuario)
        except IntegrityError:
            # Duas requisicoes simultaneas passam as duas pela verificacao acima;
            # quem segura o caso e o UNIQUE do banco.
            self.repositorio.desfazer()
            raise Conflito(f"Já existe um usuário cadastrado com o e-mail {email}.")

    def autenticar(self, email, senha):
        usuario = self.repositorio.buscar_por_email(email)
        if usuario is None or not usuario.ativo:
            # Gasta o mesmo tempo de um bcrypt real: sem isso a resposta sai em
            # 2ms contra 200ms do caminho normal, e o tempo revela quais
            # e-mails existem.
            gastar_tempo_de_verificacao()
            raise NaoAutorizada(MENSAGEM_CREDENCIAIS_INVALIDAS)
        if not verificar_senha(senha, usuario.senha_hash):
            raise NaoAutorizada(MENSAGEM_CREDENCIAIS_INVALIDAS)
        return usuario

    def buscar_perfil(self, usuario_id):
        usuario = self.repositorio.get_by_id(usuario_id)
        if usuario is None or not usuario.ativo:
            raise NaoEncontrado(f"Usuário {usuario_id} não existe.")
        return usuario

    def listar_usuarios(self, papel=None):
        if papel is None:
            return self.repositorio.get_all()
        return self.repositorio.listar_por_papel(papel)
