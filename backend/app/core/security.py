import hashlib
import hmac

import bcrypt
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

# Limite do bcrypt, contado em bytes e nao em caracteres.
LIMITE_BYTES_SENHA = 72

# Hash descartavel, usado so para gastar o mesmo tempo de verificacao quando o
# usuario nao existe. Sem isso o tempo de resposta do login revela quais
# e-mails estao cadastrados, mesmo com a mensagem de erro sendo igual.
_HASH_DESCARTAVEL = "$2b$12$Cne5zFvxoEKTW21ZKqVSl.i4Gd16/kvwq/UUsZ3lsIOcH9iP4Axa6"


def gerar_hash(senha):
    senha_bytes = senha.encode("utf-8")
    if len(senha_bytes) > LIMITE_BYTES_SENHA:
        raise ValueError(
            f"Senha excede o limite de {LIMITE_BYTES_SENHA} bytes aceito pelo bcrypt."
        )
    return bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha, senha_hash):
    senha_bytes = senha.encode("utf-8")
    if len(senha_bytes) > LIMITE_BYTES_SENHA:
        return False
    return bcrypt.checkpw(senha_bytes, senha_hash.encode("utf-8"))


def gastar_tempo_de_verificacao():
    verificar_senha("senha-que-nunca-confere", _HASH_DESCARTAVEL)


# ---------------------------------------------------------------------------
# Token de redefinicao de senha ("esqueci minha senha")
# ---------------------------------------------------------------------------
#
# O token e assinado (HMAC com a SECRET_KEY), nao guardado no banco: quem o
# recebe nao consegue forjar nem alterar o conteudo sem a chave, e o banco nao
# precisa de tabela nova.
#
# Ele carrega o id do usuario e uma "impressao" do hash da senha atual. Quando
# a senha muda, o hash muda e a impressao deixa de conferir: o link vira uso
# unico sem precisar guardar estado nenhum.

_SALT_REDEFINICAO = "redefinir-senha"


def impressao_da_senha(senha_hash):
    """Resumo curto do hash da senha. Nao revela o hash, so detecta mudanca."""
    return hashlib.sha256(senha_hash.encode("utf-8")).hexdigest()[:32]


class TokenRedefinicaoSenha:
    def __init__(self, segredo, validade_segundos):
        if not segredo:
            raise RuntimeError("SECRET_KEY e obrigatoria para gerar tokens de senha.")
        self._serializador = URLSafeTimedSerializer(segredo, salt=_SALT_REDEFINICAO)
        self.validade_segundos = validade_segundos

    def gerar(self, usuario):
        return self._serializador.dumps(
            {"id": usuario.id, "impressao": impressao_da_senha(usuario.senha_hash)}
        )

    def ler(self, token):
        """Devolve o conteudo do token, ou None se for invalido ou expirado."""
        try:
            conteudo = self._serializador.loads(token, max_age=self.validade_segundos)
        except (BadSignature, SignatureExpired):
            # SignatureExpired e filha de BadSignature; as duas ficam explicitas
            # para deixar claro que "expirado" tambem cai aqui.
            return None
        if not isinstance(conteudo, dict) or "id" not in conteudo:
            return None
        return conteudo


def impressao_confere(conteudo_token, senha_hash):
    # compare_digest gasta o mesmo tempo acerte ou erre: nao vaza, pelo tempo
    # de resposta, quantos caracteres batem.
    return hmac.compare_digest(
        str(conteudo_token.get("impressao", "")), impressao_da_senha(senha_hash)
    )
