import bcrypt

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
