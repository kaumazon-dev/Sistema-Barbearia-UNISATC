import StatusBadge from './StatusBadge';
import MenuAcoes from './MenuAcoes';
import { IconListOrdered, IconArrowRight } from './Icons';
import { useApp } from '../state/AppStore';
import { acoesDoAgendamento } from '../utils/acoesAgendamento';
import { formatarBRL } from '../utils/formato';
import './AppointmentsTable.css';

export default function AppointmentsTable({ dados, onVerAgenda }) {
  const app = useApp();

  return (
    <section className="card appointments">
      <header className="appointments__head">
        <h2 className="section-title">
          <IconListOrdered size={18} />
          Próximos Agendamentos
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
              <th>Serviço</th>
              <th>Valor</th>
              <th>Status</th>
              <th aria-label="Ações" />
            </tr>
          </thead>
          <tbody>
            {dados.map((item) => (
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
          </tbody>
        </table>
      </div>
    </section>
  );
}
