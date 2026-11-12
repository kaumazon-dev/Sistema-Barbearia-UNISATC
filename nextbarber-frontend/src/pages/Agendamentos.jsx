import { useMemo, useState } from 'react';
import PageHeader from '../components/PageHeader';
import StatusBadge from '../components/StatusBadge';
import MenuAcoes from '../components/MenuAcoes';
import { IconPlus, IconFilter } from '../components/Icons';
import { STATUS } from '../data/mock';
import { useApp } from '../state/AppStore';
import { acoesDoAgendamento } from '../utils/acoesAgendamento';
import { formatarBRL } from '../utils/formato';
import './pages.css';

const filtros = ['Todos', ...Object.values(STATUS)];

export default function Agendamentos() {
  const app = useApp();
  const { agendamentos, abrirModal } = app;
  const [filtro, setFiltro] = useState('Todos');

  const lista = useMemo(
    () => (filtro === 'Todos' ? agendamentos : agendamentos.filter((a) => a.status === filtro)),
    [filtro, agendamentos]
  );

  const contar = (status) =>
    status === 'Todos'
      ? agendamentos.length
      : agendamentos.filter((a) => a.status === status).length;

  return (
    <div className="page">
      <PageHeader
        titulo="Agendamentos"
        subtitulo={`${agendamentos.length} horários na agenda de 14 de outubro.`}
        acao={
          <button type="button" className="btn-primary" onClick={() => abrirModal('agendamento')}>
            <IconPlus size={16} />
            Novo agendamento
          </button>
        }
      />

      <div className="toolbar">
        <span className="btn-ghost toolbar__rotulo">
          <IconFilter size={15} />
          Status
        </span>
        {filtros.map((f) => (
          <button
            key={f}
            type="button"
            className={`chip ${filtro === f ? 'is-active' : ''}`}
            onClick={() => setFiltro(f)}
          >
            {f} <span className="chip__contador">{contar(f)}</span>
          </button>
        ))}
      </div>

      <section className="card panel">
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Horário</th>
                <th>Cliente</th>
                <th>Barbeiro</th>
                <th>Serviço</th>
                <th>Valor</th>
                <th>Status</th>
                <th aria-label="Ações" />
              </tr>
            </thead>
            <tbody>
              {lista.map((item) => (
                <tr key={item.id}>
                  <td className="col-time">{item.horario}</td>
                  <td className="col-strong">{item.cliente}</td>
                  <td className="col-nowrap">{item.barbeiro}</td>
                  <td>{item.servico}</td>
                  <td className="col-money">{formatarBRL(item.valor)}</td>
                  <td>
                    <StatusBadge status={item.status} />
                  </td>
                  <td className="col-acoes">
                    <MenuAcoes itens={acoesDoAgendamento(item, app)} />
                  </td>
                </tr>
              ))}
              {lista.length === 0 && (
                <tr>
                  <td colSpan={7} className="vazio">
                    Nenhum agendamento com esse status.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
