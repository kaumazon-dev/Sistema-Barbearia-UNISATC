from app.core.exceptions import NaoEncontrado, RegraDeNegocioViolada
from app.core.fuso import agora
from app.models.agendamento import STATUS_AGENDADO
from app.models.usuario import PAPEIS, PAPEL_ADMIN, PAPEL_BARBEIRO, PAPEL_CLIENTE

ROTULO_PAPEL = {
    PAPEL_ADMIN: "administrador",
    PAPEL_BARBEIRO: "barbeiro",
    PAPEL_CLIENTE: "cliente",
}


class UsuarioService:
    """Gestao de acesso feita pelo admin (dono da barbearia).

    O cadastro publico sempre cria cliente (AuthService). Quem vira barbeiro ou
    admin e decisao do admin, por aqui. Quem esta logado chega por argumento.
    """

    def __init__(self, repositorio, agendamento_repositorio, relogio=agora):
        self.repositorio = repositorio
        self.agendamento_repositorio = agendamento_repositorio
        self.relogio = relogio

    def alterar_papel(self, usuario_id, novo_papel, admin_id):
        if novo_papel not in PAPEIS:
            raise RegraDeNegocioViolada(f"Papel inválido: {novo_papel}.")
        # Sem esta regra o ultimo admin poderia se rebaixar e a barbearia
        # ficaria sem ninguem para promover outra pessoa.
        if usuario_id == admin_id:
            raise RegraDeNegocioViolada(
                "Você não pode alterar o próprio papel. Peça a outro administrador."
            )

        usuario = self.repositorio.get_by_id(usuario_id)
        if usuario is None:
            raise NaoEncontrado(f"Usuário {usuario_id} não existe.")
        if usuario.papel == novo_papel:
            return usuario

        if usuario.papel == PAPEL_BARBEIRO:
            self._garantir_agenda_livre(usuario)

        usuario.papel = novo_papel
        return self.repositorio.update(usuario)

    def _garantir_agenda_livre(self, barbeiro):
        """Barbeiro com horario marcado daqui para frente continua barbeiro:
        senao a agenda teria atendimentos de alguem que nao atende mais.
        """
        pendentes = self.agendamento_repositorio.contar_do_barbeiro_a_partir_de(
            barbeiro.id, self.relogio(), STATUS_AGENDADO
        )
        if pendentes:
            plural = "horário marcado" if pendentes == 1 else "horários marcados"
            raise RegraDeNegocioViolada(
                f"{barbeiro.nome} ainda tem {pendentes} {plural}. "
                "Remarque com outro barbeiro ou cancele antes de mudar o papel."
            )
