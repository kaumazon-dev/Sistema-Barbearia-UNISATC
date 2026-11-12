import StatCard from '../components/StatCard';
import AppointmentsTable from '../components/AppointmentsTable';
import BarbersPanel from '../components/BarbersPanel';
import ScheduleDonut from '../components/ScheduleDonut';
import { IconPlus } from '../components/Icons';
import { usuario } from '../data/mock';
import { useApp } from '../state/AppStore';
import { formatarBRL } from '../utils/formato';
import './Dashboard.css';

export default function Dashboard() {
  const { agendamentos, barbeiros, indicadores, navegar, abrirModal } = useApp();

  // Os indicadores saem da agenda: criar ou concluir um atendimento move os numeros.
  const cartoes = [
    {
      id: 'agendamentos',
      rotulo: 'Agendamentos hoje',
      valor: String(indicadores.totalAtivos),
      icone: 'calendar',
      destaque: `${indicadores.emFila} na fila`,
      tom: 'green',
      complemento: `${indicadores.atendidos} já atendidos`
    },
    {
      id: 'faturamento',
      rotulo: 'Faturamento do dia',
      valor: formatarBRL(indicadores.faturado),
      icone: 'wallet',
      destaque: `${indicadores.percentualMeta}% da meta`,
      tom: indicadores.percentualMeta >= 80 ? 'green' : 'red',
      complemento: `Meta diária de ${formatarBRL(indicadores.metaDiaria)}`
    },
    {
      id: 'clientes',
      rotulo: 'Clientes atendidos',
      valor: String(indicadores.atendidos),
      icone: 'userCheck',
      destaque: `${indicadores.emFila} aguardando`,
      tom: 'green',
      complemento: `Ticket médio ${formatarBRL(indicadores.ticket)}`
    },
    {
      id: 'ocupacao',
      rotulo: 'Taxa de ocupação',
      valor: `${indicadores.ocupacao}%`,
      icone: 'gauge',
      destaque: `${indicadores.barbeirosAtivos} de ${indicadores.totalBarbeiros} barbeiros`,
      tom: indicadores.ocupacao >= 70 ? 'green' : 'red',
      complemento: `${indicadores.totalAtivos} de 23 horários do dia`
    }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard__topo">
        <h1 className="dashboard__hello">Olá, {usuario.nome}. Seja bem-vindo de volta!</h1>
        <button type="button" className="btn-primary" onClick={() => abrirModal('agendamento')}>
          <IconPlus size={16} />
          Novo agendamento
        </button>
      </div>

      <div className="dashboard__stats">
        {cartoes.map((item) => (
          <StatCard key={item.id} {...item} />
        ))}
      </div>

      <div className="dashboard__grid">
        <AppointmentsTable
          dados={agendamentos.slice(0, 6)}
          onVerAgenda={() => navegar('agendamentos')}
        />

        <div className="dashboard__aside">
          <BarbersPanel dados={barbeiros} />
          <ScheduleDonut
            ativos={indicadores.barbeirosAtivos}
            total={indicadores.totalBarbeiros}
            percentual={indicadores.percentualEscala}
          />
        </div>
      </div>
    </div>
  );
}
