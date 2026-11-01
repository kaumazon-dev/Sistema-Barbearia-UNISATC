import StatCard from '../components/StatCard';
import AppointmentsTable from '../components/AppointmentsTable';
import BarbersPanel from '../components/BarbersPanel';
import ScheduleDonut from '../components/ScheduleDonut';
import { IconPlus, IconAlert } from '../components/Icons';
import { useApp } from '../state/AppStore';
import { agendamentosApi } from '../api/agendamentos.api';
import { authApi } from '../api/auth.api';
import { dashboardApi } from '../api/dashboard.api';
import { produtosApi } from '../api/produtos.api';
import { useCarregar } from '../utils/useCarregar';
import { situacaoDosBarbeiros } from '../utils/agenda';
import { formatarBRL, formatarQuantidade, somarDinheiro } from '../utils/formato';
import { hojeISO } from '../utils/datas';
import './Dashboard.css';

export default function Dashboard() {
  const { usuario, navegar, abrirModal } = useApp();
  const hoje = hojeISO();

  // Agenda do dia: base dos cartoes do dia e do painel de barbeiros.
  const agenda = useCarregar(
    async () => {
      const [dia, barbeiros] = await Promise.all([
        agendamentosApi.listar({ dia: hoje, porPagina: 100 }),
        authApi.listarBarbeiros()
      ]);
      return { itens: dia.itens, barbeiros };
    },
    [hoje]
  );

  // Metricas do mes: agregadas no SQL pela API (sem periodo = mes atual).
  const mes = useCarregar(async () => {
    const [faturamento, atendimentos, cancelamento, emFalta] = await Promise.all([
      dashboardApi.faturamento({ granularidade: 'mes' }),
      dashboardApi.atendimentos({ granularidade: 'mes' }),
      dashboardApi.cancelamento(),
      produtosApi.emFalta()
    ]);
    return { faturamento, atendimentos, cancelamento, emFalta };
  }, []);

  const itens = agenda.dados?.itens || [];
  const ativosHoje = itens.filter((a) => a.status !== 'cancelado');
  const naFila = itens.filter((a) => a.status === 'agendado');
  const concluidosHoje = itens.filter((a) => a.status === 'concluido');
  const faturadoHoje = somarDinheiro(concluidosHoje.map((a) => a.total));
  const equipe = situacaoDosBarbeiros(agenda.dados?.barbeiros || [], itens);
  const comHorario = equipe.filter((b) => b.atendimentosHoje > 0).length;

  const m = mes.dados;
  const faturadoMes = m ? somarDinheiro(m.faturamento.valores) : 0;
  const atendidosMes = m ? m.atendimentos.valores.reduce((a, b) => a + b, 0) : 0;
  const taxa = m?.cancelamento.taxa;
  const carregandoMes = mes.carregando && !m;

  const cartoes = [
    {
      id: 'agendamentos',
      rotulo: 'Agendamentos hoje',
      valor: agenda.dados ? String(ativosHoje.length) : '—',
      icone: 'calendar',
      destaque: `${naFila.length} na fila`,
      tom: 'green',
      complemento: `${concluidosHoje.length} já atendidos`
    },
    {
      id: 'faturamento-dia',
      rotulo: 'Faturamento do dia',
      valor: agenda.dados ? formatarBRL(faturadoHoje) : '—',
      icone: 'wallet',
      destaque: `${concluidosHoje.length} concluídos`,
      tom: 'green',
      complemento: 'Soma do preço cobrado'
    },
    {
      id: 'faturamento-mes',
      rotulo: 'Faturamento do mês',
      valor: carregandoMes ? '—' : formatarBRL(faturadoMes),
      icone: 'userCheck',
      destaque: `${atendidosMes} atendimentos`,
      tom: 'green',
      complemento: `Ticket médio ${formatarBRL(atendidosMes ? faturadoMes / atendidosMes : 0)}`
    },
    {
      id: 'cancelamento',
      rotulo: 'Taxa de cancelamento',
      valor: carregandoMes ? '—' : taxa === null || taxa === undefined ? 'Sem dados' : `${Number(taxa).toLocaleString('pt-BR')}%`,
      icone: 'gauge',
      destaque: m ? `${m.cancelamento.cancelados} cancelados` : '',
      tom: Number(taxa) > 15 ? 'red' : 'green',
      complemento: m ? `de ${m.cancelamento.total} no mês` : ''
    }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard__topo">
        <h1 className="dashboard__hello">Olá, {usuario.nome.split(' ')[0]}. Seja bem-vindo de volta!</h1>
        <button type="button" className="btn-primary" onClick={() => abrirModal('agendamento')}>
          <IconPlus size={16} />
          Novo agendamento
        </button>
      </div>

      {mes.erro && (
        <p className="erro-form">
          Não foi possível carregar as métricas do mês: {mes.erro.message}
        </p>
      )}

      <div className="dashboard__stats">
        {cartoes.map((item) => (
          <StatCard key={item.id} {...item} />
        ))}
      </div>

      <div className="dashboard__grid">
        <AppointmentsTable
          titulo="Agenda de hoje"
          dados={itens}
          estado={agenda}
          onVerAgenda={() => navegar('agendamentos')}
        />

        <div className="dashboard__aside">
          <BarbersPanel dados={equipe} />
          <ScheduleDonut
            titulo="Ocupação da equipe"
            rotulo="Barbeiros com horário hoje"
            texto={`${equipe.length ? Math.round((comHorario / equipe.length) * 100) : 0}% da equipe com agenda no dia`}
            ativos={comHorario}
            total={equipe.length}
            percentual={equipe.length ? Math.round((comHorario / equipe.length) * 100) : 0}
          />

          <section className="card barbers">
            <header className="barbers__head">
              <h2 className="section-title">
                <IconAlert size={18} />
                Produtos em falta
              </h2>
              <p className="barbers__subtitle">Quantidade no mínimo ou abaixo dele.</p>
            </header>
            <ul className="barbers__list">
              {(m?.emFalta || []).map((p) => (
                <li key={p.id} className="barber">
                  <div className="barber__info">
                    <strong>{p.nome}</strong>
                    <small>
                      {formatarQuantidade(p.quantidade_atual)} {p.unidade} · mínimo {formatarQuantidade(p.estoque_minimo)}
                    </small>
                  </div>
                  <span className="dot-label barber__status barber__status--amber">Repor</span>
                </li>
              ))}
              {m && m.emFalta.length === 0 && <li className="vazio">Estoque em dia.</li>}
            </ul>
          </section>
        </div>
      </div>
    </div>
  );
}
