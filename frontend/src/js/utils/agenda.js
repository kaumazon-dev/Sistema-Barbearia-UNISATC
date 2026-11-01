/**
 * Calculos sobre a agenda de UM dia que ja veio da API.
 *
 * Nao e agregacao de negocio (essa fica no SQL do dashboard): e so a
 * situacao do momento, para o painel de barbeiros.
 */

/** Barbeiros com situacao (Ocupado/Disponivel) e quem atendem agora. */
export function situacaoDosBarbeiros(barbeiros, agendaDoDia, agora = new Date()) {
  return barbeiros.map((b) => {
    const doBarbeiro = agendaDoDia.filter((a) => a.barbeiro.id === b.id && a.status !== 'cancelado');
    const atual = doBarbeiro.find(
      (a) => a.status === 'agendado' && new Date(a.inicio) <= agora && agora < new Date(a.fim)
    );
    const proximo = doBarbeiro.find((a) => a.status === 'agendado' && new Date(a.inicio) > agora);
    return {
      ...b,
      situacao: atual ? 'Ocupado' : 'Disponível',
      atendendo: atual?.cliente.nome || null,
      proximo: proximo || null,
      atendimentosHoje: doBarbeiro.length,
      concluidosHoje: doBarbeiro.filter((a) => a.status === 'concluido').length
    };
  });
}
