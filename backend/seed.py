"""Popula o banco com dados de exemplo para a demonstracao.

    docker compose exec backend python seed.py

Nunca demonstrar com banco vazio: o dashboard precisa de semanas de historico,
o estoque precisa de produto em falta e a agenda precisa de horarios marcados.

Os dados passam pelos mesmos services da API (conflito de agenda, preco
congelado, estoque so via movimentacao). O seed nao "fura" nenhuma regra: se
ele conseguiu gravar, a API tambem gravaria.

Idempotente: se o admin de exemplo ja existe, nao faz nada. Para recomecar do
zero no compose: docker compose down -v && docker compose up -d --build.
"""

import os
import random
import sys
from datetime import date, datetime, time, timedelta
from decimal import Decimal

os.environ.setdefault("APP_ENV", "dev")

from app import create_app  # noqa: E402
from app.core.exceptions import Conflito  # noqa: E402
from app.core.fuso import FUSO_BARBEARIA, agora  # noqa: E402
from app.core.security import gerar_hash  # noqa: E402
from app.extensions import db  # noqa: E402
from app.models.usuario import PAPEL_ADMIN, PAPEL_BARBEIRO, Usuario  # noqa: E402
from app.repositories.agendamento_repository import AgendamentoRepository  # noqa: E402
from app.repositories.movimentacao_estoque_repository import (  # noqa: E402
    MovimentacaoEstoqueRepository,
)
from app.repositories.produto_repository import ProdutoRepository  # noqa: E402
from app.repositories.servico_repository import ServicoRepository  # noqa: E402
from app.repositories.usuario_repository import UsuarioRepository  # noqa: E402
from app.services.agendamento_service import AgendamentoService  # noqa: E402
from app.services.cliente_service import ClienteService  # noqa: E402
from app.services.estoque_service import EstoqueService  # noqa: E402
from app.services.produto_service import ProdutoService  # noqa: E402
from app.services.servico_service import ServicoService  # noqa: E402

# Contas de demonstracao. Senha unica para facilitar a apresentacao; nao e
# credencial de producao de verdade.
SENHA_DEMO = "barbearia123"
EMAIL_ADMIN = "admin@nextbarber.com"

BARBEIROS = [
    ("Rafael Costa", "rafael@nextbarber.com", "(48) 99901-1001"),
    ("Diego Martins", "diego@nextbarber.com", "(48) 99901-1002"),
    ("Thiago Souza", "thiago@nextbarber.com", "(48) 99901-1003"),
]

CLIENTES = [
    ("Ana Beatriz Lima", "ana.lima@email.com", "(48) 98811-2001"),
    ("Bruno Henrique Alves", "bruno.alves@email.com", "(48) 98811-2002"),
    ("Carlos Eduardo Rocha", "carlos.rocha@email.com", "(48) 98811-2003"),
    ("Daniel Ferreira", "daniel.ferreira@email.com", "(48) 98811-2004"),
    ("Eduardo Pereira", "eduardo.pereira@email.com", "(48) 98811-2005"),
    ("Felipe Andrade", "felipe.andrade@email.com", "(48) 98811-2006"),
    ("Gabriel Nunes", "gabriel.nunes@email.com", "(48) 98811-2007"),
    ("Gustavo Ribeiro", "gustavo.ribeiro@email.com", "(48) 98811-2008"),
    ("Henrique Duarte", "henrique.duarte@email.com", "(48) 98811-2009"),
    ("Igor Mendes", "igor.mendes@email.com", "(48) 98811-2010"),
    ("João Pedro Silva", "joao.silva@email.com", "(48) 98811-2011"),
    ("Leonardo Barros", "leonardo.barros@email.com", "(48) 98811-2012"),
    ("Lucas Gabriel Melo", "lucas.melo@email.com", "(48) 98811-2013"),
    ("Mateus Cardoso", "mateus.cardoso@email.com", "(48) 98811-2014"),
    ("Pedro Henrique Dias", "pedro.dias@email.com", "(48) 98811-2015"),
    ("Rodrigo Teixeira", "rodrigo.teixeira@email.com", "(48) 98811-2016"),
    ("Vinícius Moreira", "vinicius.moreira@email.com", "(48) 98811-2017"),
    ("Cliente Demo", "cliente@nextbarber.com", "(48) 98811-2099"),
]

# (nome, duracao_minutos, preco, peso no sorteio)
SERVICOS = [
    ("Corte masculino", 30, "45.00", 10),
    ("Barba", 20, "30.00", 6),
    ("Corte + barba", 50, "70.00", 8),
    ("Degradê", 40, "55.00", 5),
    ("Sobrancelha", 10, "15.00", 3),
    ("Pigmentação de barba", 30, "40.00", 2),
    ("Hidratação capilar", 30, "35.00", 2),
]

# (nome, unidade, estoque_minimo, entrada inicial, saidas de uso)
# Os ultimos ficam no minimo ou abaixo dele: o alerta de estoque aparece na demo.
PRODUTOS = [
    ("Pomada modeladora", "un", "5", "24", ["3", "4", "2"]),
    ("Shampoo anticaspa 1L", "ml", "1000", "5000", ["800", "650", "900"]),
    ("Óleo para barba", "ml", "200", "1200", ["150", "200", "120"]),
    ("Lâmina descartável", "un", "50", "300", ["60", "45", "70"]),
    ("Gel fixador", "g", "500", "3000", ["400", "350"]),
    ("Pós-barba", "ml", "300", "1500", ["250", "300", "200"]),
    ("Cera matte", "un", "6", "10", ["3", "2"]),
    ("Toalha descartável", "un", "100", "200", ["60", "50"]),
    ("Talco", "g", "400", "800", ["250", "200"]),
]

DIAS_DE_HISTORICO = 56  # 8 semanas para o grafico semanal ficar cheio
DIAS_DE_AGENDA_FUTURA = 10
ABERTURA, FECHAMENTO = time(9, 0), time(19, 0)
TAXA_CANCELAMENTO = 0.12


def criar_equipe(usuarios):
    """Admin e barbeiros nao tem cadastro publico (o /auth/registrar so cria
    cliente), entao entram direto pelo repository, com a senha em hash.
    """
    admin = usuarios.create(
        Usuario(
            nome="Administrador",
            email=EMAIL_ADMIN,
            senha_hash=gerar_hash(SENHA_DEMO),
            papel=PAPEL_ADMIN,
        )
    )
    barbeiros = [
        usuarios.create(
            Usuario(
                nome=nome,
                email=email,
                telefone=telefone,
                senha_hash=gerar_hash(SENHA_DEMO),
                papel=PAPEL_BARBEIRO,
            )
        )
        for nome, email, telefone in BARBEIROS
    ]
    return admin, barbeiros


def criar_clientes(usuarios):
    service = ClienteService(usuarios)
    return [
        service.cadastrar(
            {"nome": nome, "email": email, "telefone": telefone, "senha": SENHA_DEMO}
        )
        for nome, email, telefone in CLIENTES
    ]


def criar_servicos():
    service = ServicoService(ServicoRepository())
    criados = []
    for nome, duracao, preco, peso in SERVICOS:
        servico = service.cadastrar(
            {"nome": nome, "duracao_minutos": duracao, "preco": Decimal(preco)}
        )
        criados.append((servico, peso))
    return criados


def criar_estoque(admin):
    produtos = ProdutoService(ProdutoRepository())
    estoque = EstoqueService(ProdutoRepository(), MovimentacaoEstoqueRepository())
    for nome, unidade, minimo, inicial, saidas in PRODUTOS:
        produto = produtos.cadastrar(
            {"nome": nome, "unidade": unidade, "estoque_minimo": Decimal(minimo)}
        )
        # Quantidade nunca e escrita direto: so entrada/saida pelo service,
        # que grava a movimentacao junto (RN04).
        estoque.registrar_entrada(produto.id, Decimal(inicial), admin.id, "Compra inicial")
        for quantidade in saidas:
            estoque.registrar_saida(produto.id, Decimal(quantidade), admin.id, "Uso no atendimento")


def sortear_servicos(sorteio, servicos):
    """Um servico na maioria das vezes; as vezes um combo (ex.: corte + sobrancelha)."""
    pesos = [peso for _, peso in servicos]
    escolhidos = sorteio.choices([s for s, _ in servicos], weights=pesos, k=1)
    if sorteio.random() < 0.25:
        extra = sorteio.choices([s for s, _ in servicos], weights=pesos, k=1)[0]
        if extra not in escolhidos:
            escolhidos.append(extra)
    return escolhidos


def horarios_do_dia(sorteio, dia, maximo):
    """Inicios candidatos do dia, em passos de 30 min. O fim real de cada
    agendamento depende dos servicos sorteados, entao quem garante que nao
    ha sobreposicao e o proprio service.
    """
    inicio = datetime.combine(dia, ABERTURA, tzinfo=FUSO_BARBEARIA)
    inicio += timedelta(minutes=30 * sorteio.randint(0, 2))
    fechamento = datetime.combine(dia, FECHAMENTO, tzinfo=FUSO_BARBEARIA)
    horarios = []
    while inicio < fechamento - timedelta(minutes=60) and len(horarios) < maximo:
        horarios.append(inicio)
        inicio += timedelta(minutes=60 * sorteio.randint(1, 3))
    return horarios


def criar_agenda(sorteio, admin, barbeiros, clientes, servicos):
    repositorio = AgendamentoRepository()
    servico_service = ServicoService(ServicoRepository())
    usuarios = UsuarioRepository()
    instante_real = agora()
    hoje = instante_real.astimezone(FUSO_BARBEARIA).date()

    total = {"concluido": 0, "cancelado": 0, "agendado": 0, "recusados": 0}
    primeiro_dia = hoje - timedelta(days=DIAS_DE_HISTORICO)
    dias = [primeiro_dia + timedelta(days=n) for n in range(DIAS_DE_HISTORICO + DIAS_DE_AGENDA_FUTURA + 1)]

    for dia in dias:
        if dia.weekday() == 6:  # domingo fechado
            continue
        futuro = dia > hoje
        for barbeiro in barbeiros:
            for inicio in horarios_do_dia(sorteio, dia, maximo=2 if futuro else 5):
                # O service recusa horario no passado. Para montar historico, o
                # relogio dele e "um minuto antes do horario": a regra de
                # conflito e todas as outras continuam valendo.
                relogio = (lambda i=inicio: i - timedelta(minutes=1))
                service = AgendamentoService(
                    repositorio, servico_service, usuarios, relogio=relogio
                )
                try:
                    agendamento = service.criar(
                        {
                            "cliente_id": sorteio.choice(clientes).id,
                            "barbeiro_id": barbeiro.id,
                            "inicio": inicio,
                            "servico_ids": [s.id for s in sortear_servicos(sorteio, servicos)],
                        },
                        admin.id,
                        PAPEL_ADMIN,
                    )
                except Conflito:
                    # Combo longo invadiria o proximo horario: a regra de
                    # conflito recusa, como faria na API. So pula.
                    total["recusados"] += 1
                    continue

                if agendamento.inicio < instante_real:
                    if sorteio.random() < TAXA_CANCELAMENTO:
                        service.cancelar(agendamento.id, admin.id, PAPEL_ADMIN)
                        total["cancelado"] += 1
                    else:
                        service.concluir(agendamento.id, admin.id, PAPEL_ADMIN)
                        total["concluido"] += 1
                else:
                    total["agendado"] += 1
        print(f"  agenda de {dia:%d/%m} ok", end="\r", flush=True)

    print(" " * 40, end="\r")
    return total


def main():
    app = create_app()
    with app.app_context():
        # O DevConfig liga o eco do SQL; aqui seriam milhares de linhas.
        db.engine.echo = False

        usuarios = UsuarioRepository()
        if usuarios.buscar_por_email(EMAIL_ADMIN) is not None:
            print("Banco ja tem os dados de exemplo. Nada a fazer.")
            return 0

        # Semente fixa: toda execucao gera a mesma barbearia.
        sorteio = random.Random(2026)

        print("Criando equipe e clientes...")
        admin, barbeiros = criar_equipe(usuarios)
        clientes = criar_clientes(usuarios)

        print("Criando servicos e estoque...")
        servicos = criar_servicos()
        criar_estoque(admin)

        print("Montando agenda (historico + proximos dias)...")
        total = criar_agenda(sorteio, admin, barbeiros, clientes, servicos)

        print("Pronto!")
        print(f"  {len(barbeiros)} barbeiros, {len(clientes)} clientes, "
              f"{len(servicos)} servicos, {len(PRODUTOS)} produtos")
        print(f"  agendamentos: {total['concluido']} concluidos, "
              f"{total['cancelado']} cancelados, {total['agendado']} agendados "
              f"({total['recusados']} horarios recusados por conflito)")
        print(f"  login admin: {EMAIL_ADMIN} / senha de demonstracao no topo do seed.py")
        return 0


if __name__ == "__main__":
    sys.exit(main())
