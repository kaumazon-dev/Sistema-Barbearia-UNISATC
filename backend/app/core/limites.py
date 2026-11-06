"""Limite de tentativas (rate limit) das rotas publicas de autenticacao.

Cada limite e contado por uma "chave". Duas chaves sao usadas:

- IP de quem chama (get_remote_address): segura um robo martelando a API.
- E-mail do corpo da requisicao: segura ataque a UMA conta, mesmo vindo de
  varios IPs (forca bruta de senha, ou lotar a caixa de alguem com
  "esqueci minha senha").

Os limites por e-mail sao os mais rigidos de proposito: eles nao dependem de
acertar a configuracao de proxy (PROXIES_CONFIAVEIS) para funcionar.
"""

from flask import request
from flask_limiter.util import get_remote_address

# Strings no formato da biblioteca "limits": "<quantidade> per <periodo>".
# Varios limites separados por ";" valem juntos.
LIMITE_LOGIN_IP = "30 per minute"
LIMITE_LOGIN_EMAIL = "10 per 15 minutes"
LIMITE_CADASTRO_IP = "10 per hour"
LIMITE_ESQUECI_IP = "10 per hour"
LIMITE_ESQUECI_EMAIL = "3 per hour"
LIMITE_REDEFINIR_IP = "10 per 15 minutes"

MENSAGEM_LIMITE = "Muitas tentativas em pouco tempo. Aguarde um pouco e tente novamente."


def chave_por_email():
    """E-mail normalizado do corpo JSON; sem e-mail valido, cai no IP.

    Normaliza igual ao schema (strip + lower): sem isso "Ana@x.com" e
    "ana@x.com" contariam separado e o limite dobraria.
    """
    dados = request.get_json(silent=True)
    email = dados.get("email") if isinstance(dados, dict) else None
    if isinstance(email, str) and email.strip():
        return "email:" + email.strip().lower()
    return "ip:" + get_remote_address()
