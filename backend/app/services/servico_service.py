from app.core.exceptions import NaoEncontrado, RegraDeNegocioViolada
from app.models.servico import Servico


class ServicoService:
    """Servico nunca e apagado de fato, so desativado: agendamentos antigos
    apontam para ele.
    """

    def __init__(self, repositorio):
        self.repositorio = repositorio

    def listar(self, ativo=None):
        return self.repositorio.listar(ativo)

    def buscar(self, servico_id):
        servico = self.repositorio.get_by_id(servico_id)
        if servico is None:
            raise NaoEncontrado(f"Serviço {servico_id} não existe.")
        return servico

    def cadastrar(self, dados):
        servico = Servico(
            nome=dados["nome"],
            duracao_minutos=dados["duracao_minutos"],
            preco=dados["preco"],
        )
        return self.repositorio.create(servico)

    def atualizar(self, servico_id, dados):
        # Mudar preco ou duracao nao mexe em agendamento ja marcado: o preco
        # cobrado e o horario de fim ficam gravados no agendamento (RN02, RN03).
        servico = self.buscar(servico_id)
        for campo in ("nome", "duracao_minutos", "preco", "ativo"):
            if campo in dados:
                setattr(servico, campo, dados[campo])
        return self.repositorio.update(servico)

    def desativar(self, servico_id):
        servico = self.buscar(servico_id)
        servico.ativo = False
        return self.repositorio.update(servico)

    def buscar_ativos_para_agendamento(self, ids):
        """Servicos de um agendamento novo, na ordem pedida (RF12).

        Ponto de entrada da Fase 4: o service de agendamento chama este metodo
        em vez de consultar o repositorio direto, para a regra ficar num lugar so.
        """
        ids_unicos = list(dict.fromkeys(ids))
        encontrados = {s.id: s for s in self.repositorio.buscar_por_ids(ids_unicos)}

        faltando = [i for i in ids_unicos if i not in encontrados]
        if faltando:
            raise NaoEncontrado(
                "Serviço(s) inexistente(s): " + ", ".join(map(str, faltando)) + "."
            )

        inativos = [encontrados[i].nome for i in ids_unicos if not encontrados[i].ativo]
        if inativos:
            raise RegraDeNegocioViolada(
                "Serviço desativado não pode ser usado em novo agendamento: "
                + ", ".join(inativos)
                + "."
            )

        return [encontrados[i] for i in ids_unicos]
