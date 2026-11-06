from functools import wraps

from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

from app.core.exceptions import AcessoNegado


def rota_protegida(*papeis_permitidos):
    """Sem argumento exige apenas token valido; com argumento exige um dos papeis."""

    def decorador(funcao):
        @wraps(funcao)
        @jwt_required()
        def envelope(*args, **kwargs):
            if papeis_permitidos:
                if get_jwt().get("papel") not in papeis_permitidos:
                    raise AcessoNegado(
                        "Seu papel não tem permissão para acessar este recurso."
                    )
            return funcao(*args, **kwargs)

        return envelope

    return decorador


def usuario_logado_id():
    # A claim "sub" e gravada como string por exigencia do padrao JWT.
    return int(get_jwt_identity())
