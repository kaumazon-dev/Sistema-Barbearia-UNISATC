import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import Avatar from '../components/Avatar';
import MenuAcoes from '../components/MenuAcoes';
import { BlocoEstado } from '../components/Estado';
import { useApp } from '../state/AppStore';
import { agendamentosApi } from '../api/agendamentos.api';
import { authApi } from '../api/auth.api';
import { useCarregar } from '../utils/useCarregar';
import { situacaoDosBarbeiros } from '../utils/agenda';
import { iniciaisDe } from '../utils/formato';
import { hojeISO, hora } from '../utils/datas';
import './pages.css';

export default function Barbeiros() {
  const { abrirModal } = useApp();
  const hoje = hojeISO();

  const consulta = useCarregar(async () => {
    const [barbeiros, agenda] = await Promise.all([
      authApi.listarBarbeiros(),
      agendamentosApi.listar({ dia: hoje, porPagina: 100 })
    ]);
    return situacaoDosBarbeiros(barbeiros, agenda.itens);
  }, [hoje]);

  const equipe = consulta.dados || [];

  return (
    <div className="page">
      <PageHeader titulo="Barbeiros" subtitulo="Equipe ativa e situação de cada um na agenda de hoje." />

      <BlocoEstado {...consulta} carregando={consulta.carregando && !consulta.dados} />

      <div className="grid-cards">
        {equipe.map((b) => (
          <article key={b.id} className="card mini-card">
            <div className="mini-card__top">
              <Avatar iniciais={iniciaisDe(b.nome)} size={44} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <strong>{b.nome}</strong>
                <small>Barbeiro</small>
              </div>
              <StatusBadge status={b.situacao} />
              <MenuAcoes
                itens={[
                  {
                    chave: 'agendar',
                    rotulo: 'Agendar com ele',
                    aoClicar: () => abrirModal('agendamento', { barbeiroId: b.id })
                  }
                ]}
              />
            </div>

            <div className="mini-card__rows">
              <div className="mini-card__row">
                <span>Horários hoje</span>
                <b>{b.atendimentosHoje}</b>
              </div>
              <div className="mini-card__row">
                <span>Concluídos hoje</span>
                <b>{b.concluidosHoje}</b>
              </div>
              <div className="mini-card__row">
                <span>Atendendo agora</span>
                <b>{b.atendendo || '—'}</b>
              </div>
              <div className="mini-card__row">
                <span>Próximo horário</span>
                <b>{b.proximo ? `${hora(b.proximo.inicio)} · ${b.proximo.cliente.nome}` : '—'}</b>
              </div>
            </div>
          </article>
        ))}
      </div>

      {consulta.dados && equipe.length === 0 && <p className="vazio">Nenhum barbeiro ativo cadastrado.</p>}
    </div>
  );
}
