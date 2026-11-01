import StatusBadge from './StatusBadge';
import MenuAcoes from './MenuAcoes';
import { IconListOrdered, IconArrowRight } from './Icons';
import { LinhaEstado } from './Estado';
import { useApp } from '../state/AppStore';
import { acoesDoAgendamento } from '../utils/acoesAgendamento';
import { formatarBRL, STATUS } from '../utils/formato';
import { hora } from '../utils/datas';
import './AppointmentsTable.css';

export default function AppointmentsTable({ titulo, dados, estado, onVerAgenda }) {
  const app = useApp();

  return (
    <section className="card appointments">
      <header className="appointments__head">
        <h2 className="section-title">
          <IconListOrdered size={18} />
          {titulo}
        </h2>
        <button type="button" className="appointments__link" onClick={onVerAgenda}>
          Ver agenda completa
          <IconArrowRight size={15} />
        </button>
      </header>

      <div className="table-wrap">
        <table className="table">
          <thead>
            <tr>
              <th>Horário</th>
              <th>Cliente</th>
              <th>Barbeiro</th>
              <th>Serviços</th>
              <th>Valor</th>
              <th>Status</th>
              <th aria-label="Ações" />
            </tr>
          </thead>
          <tbody>
            {dados.map((item) => (
              <tr key={item.id}>
                <td className="col-time">
                  {hora(item.inicio)}
                  <span className="col-sub">até {hora(item.fim)}</span>
                </td>
                <td className="col-strong">{item.cliente.nome}</td>
                <td className="col-nowrap">{item.barbeiro.nome}</td>
                <td>{item.servicos.map((s) => s.nome).join(' + ')}</td>
                <td className="col-money">{formatarBRL(item.total)}</td>
                <td>
                  <StatusBadge status={STATUS[item.status]} />
                </td>
                <td className="col-acoes">
                  {item.status === 'agendado' && <MenuAcoes itens={acoesDoAgendamento(item, app)} />}
                </td>
              </tr>
            ))}
            <LinhaEstado
              colunas={7}
              {...estado}
              vazio={dados.length === 0}
              textoVazio="Nenhum agendamento para hoje."
            />
          </tbody>
        </table>
      </div>
    </section>
  );
}
