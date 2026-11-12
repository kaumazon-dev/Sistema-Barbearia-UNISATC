import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import Avatar from '../components/Avatar';
import MenuAcoes from '../components/MenuAcoes';
import { IconPlus, IconStar } from '../components/Icons';
import { useApp } from '../state/AppStore';
import './pages.css';

const situacoes = ['Disponível', 'Ocupado', 'Intervalo'];

export default function Barbeiros() {
  const { barbeiros, abrirModal, mudarSituacaoBarbeiro } = useApp();

  const acoes = (b) => [
    { chave: 'editar', rotulo: 'Editar barbeiro', aoClicar: () => abrirModal('barbeiro', b) },
    {
      chave: 'agendar',
      rotulo: 'Agendar com ele',
      aoClicar: () => abrirModal('agendamento', { barbeiroId: b.id })
    },
    { chave: 'sep', separador: true },
    ...situacoes
      .filter((s) => s !== b.situacao)
      .map((s) => ({
        chave: `sit-${s}`,
        rotulo: `Marcar como ${s}`,
        aoClicar: () => mudarSituacaoBarbeiro(b.id, s)
      }))
  ];

  return (
    <div className="page">
      <PageHeader
        titulo="Barbeiros"
        subtitulo="Equipe da unidade, disponibilidade e desempenho do dia."
        acao={
          <button type="button" className="btn-primary" onClick={() => abrirModal('barbeiro')}>
            <IconPlus size={16} />
            Novo barbeiro
          </button>
        }
      />

      <div className="grid-cards">
        {barbeiros.map((b) => (
          <article key={b.id} className="card mini-card">
            <div className="mini-card__top">
              <Avatar iniciais={b.iniciais} size={44} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <strong>{b.apelido}</strong>
                <small>{b.nome}</small>
              </div>
              <StatusBadge status={b.situacao} />
              <MenuAcoes itens={acoes(b)} />
            </div>

            <div className="mini-card__rows">
              <div className="mini-card__row">
                <span>Especialidade</span>
                <b>{b.especialidade || '—'}</b>
              </div>
              <div className="mini-card__row">
                <span>Atendimentos hoje</span>
                <b>{b.atendimentosHoje}</b>
              </div>
              <div className="mini-card__row">
                <span>Atendendo agora</span>
                <b>{b.atendendo || '—'}</b>
              </div>
              <div className="mini-card__row">
                <span>Comissão</span>
                <b>{b.comissao}%</b>
              </div>
              <div className="mini-card__row">
                <span>Avaliação</span>
                <b style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
                  <IconStar size={13} />
                  {b.avaliacao ? b.avaliacao.toFixed(1) : '—'}
                </b>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
