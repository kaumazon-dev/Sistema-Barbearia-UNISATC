import { useMemo, useState } from 'react';
import PageHeader from '../../js/components/PageHeader';
import StatCard from '../../js/components/StatCard';
import Grafico from '../../js/components/Grafico';
import { BlocoEstado } from '../../js/components/Estado';
import { IconTrendUp, IconChartLine, IconCalendar, IconXCircle } from '../../js/components/Icons';
import { dashboardApi } from '../../js/api/dashboard.api';
import { useCarregar } from '../../js/utils/useCarregar';
import { formatarBRL, somarDinheiro } from '../../js/utils/formato';
import { hojeISO, inicioDoMes, dataDoDia, rotuloPeriodo } from '../../js/utils/datas';
import '../../assets/css/pages/pages.css';

const OURO = '#e9a23b';
const VERDE = '#4ade80';
const VERMELHO = '#f87171';

/**
 * Graficos do dashboard gerencial (RF28 a RF31) com Chart.js.
 * Toda agregacao vem pronta do SQL; aqui so se desenha.
 */
export default function Relatorios() {
  const hoje = hojeISO();
  const [de, setDe] = useState(inicioDoMes(hoje));
  const [ate, setAte] = useState(hoje);
  const [granularidade, setGranularidade] = useState('semana');

  const consulta = useCarregar(async () => {
    const periodo = { de, ate };
    const [faturamento, atendimentos, ranking, cancelamento] = await Promise.all([
      dashboardApi.faturamento({ ...periodo, granularidade }),
      dashboardApi.atendimentos({ ...periodo, granularidade }),
      dashboardApi.ranking({ ...periodo, limite: 5 }),
      dashboardApi.cancelamento(periodo)
    ]);
    return { faturamento, atendimentos, ranking, cancelamento };
  }, [de, ate, granularidade]);

  const r = consulta.dados;

  const graficos = useMemo(() => {
    if (!r) return null;
    const rotulos = (serie) => serie.labels.map((l) => rotuloPeriodo(l, granularidade));
    const moeda = { callbacks: { label: (ctx) => formatarBRL(ctx.raw) } };
    return {
      faturamento: {
        dados: {
          labels: rotulos(r.faturamento),
          // a API manda string ("120.00"); o Chart.js aceita string numerica
          datasets: [{ label: 'Faturamento', data: r.faturamento.valores, backgroundColor: OURO, borderRadius: 6 }]
        },
        opcoes: { plugins: { legend: { display: false }, tooltip: moeda } }
      },
      atendimentos: {
        dados: {
          labels: rotulos(r.atendimentos),
          datasets: [
            {
              label: 'Atendimentos',
              data: r.atendimentos.valores,
              borderColor: OURO,
              backgroundColor: 'rgba(233, 162, 59, 0.15)',
              fill: true,
              tension: 0.3
            }
          ]
        },
        opcoes: { plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
      },
      ranking: {
        dados: {
          labels: r.ranking.labels,
          datasets: [{ label: 'Vezes realizado', data: r.ranking.valores, backgroundColor: OURO, borderRadius: 6 }]
        },
        opcoes: {
          indexAxis: 'y',
          plugins: {
            legend: { display: false },
            tooltip: {
              callbacks: {
                afterLabel: (ctx) => `Receita: ${formatarBRL(r.ranking.receitas[ctx.dataIndex])}`
              }
            }
          },
          scales: { x: { beginAtZero: true, ticks: { precision: 0 } } }
        }
      },
      cancelamento: {
        dados: {
          labels: r.cancelamento.labels,
          datasets: [{ data: r.cancelamento.valores, backgroundColor: [VERDE, VERMELHO], borderWidth: 0 }]
        },
        opcoes: { cutout: '68%', plugins: { legend: { position: 'bottom' } } }
      }
    };
  }, [r, granularidade]);

  const faturado = r ? somarDinheiro(r.faturamento.valores) : 0;
  const atendidos = r ? r.atendimentos.valores.reduce((a, b) => a + b, 0) : 0;
  const taxa = r?.cancelamento.taxa;

  const resumo = [
    {
      id: 'receita',
      rotulo: 'Faturamento no período',
      valor: r ? formatarBRL(faturado) : '—',
      icone: 'wallet',
      destaque: 'preço cobrado',
      tom: 'green',
      complemento: 'só atendimentos concluídos'
    },
    {
      id: 'atendimentos',
      rotulo: 'Atendimentos',
      valor: r ? String(atendidos) : '—',
      icone: 'userCheck',
      destaque: r ? `${r.ranking.valores.reduce((a, b) => a + b, 0)} serviços` : '',
      tom: 'green',
      complemento: 'nos 5 mais vendidos'
    },
    {
      id: 'ticket',
      rotulo: 'Ticket médio',
      valor: r ? formatarBRL(atendidos ? faturado / atendidos : 0) : '—',
      icone: 'gauge',
      destaque: 'por atendimento',
      tom: 'green',
      complemento: ''
    },
    {
      id: 'cancelamento',
      rotulo: 'Taxa de cancelamento',
      valor: !r ? '—' : taxa === null ? 'Sem dados' : `${Number(taxa).toLocaleString('pt-BR')}%`,
      icone: 'calendar',
      destaque: r ? `${r.cancelamento.cancelados} cancelados` : '',
      tom: Number(taxa) > 15 ? 'red' : 'green',
      complemento: r ? `de ${r.cancelamento.total} com desfecho` : ''
    }
  ];

  return (
    <div className="page">
      <PageHeader
        titulo="Relatórios"
        subtitulo={r ? `Período de ${dataDoDia(r.faturamento.de)} a ${dataDoDia(r.faturamento.ate)}.` : 'Visão gerencial do período.'}
      />

      <div className="filtros">
        <div className="field">
          <label htmlFor="rel-de">De</label>
          <input id="rel-de" type="date" value={de} max={ate} onChange={(e) => e.target.value && setDe(e.target.value)} />
        </div>
        <div className="field">
          <label htmlFor="rel-ate">Até</label>
          <input id="rel-ate" type="date" value={ate} min={de} onChange={(e) => e.target.value && setAte(e.target.value)} />
        </div>
        <div className="toolbar">
          {[
            ['semana', 'Por semana'],
            ['mes', 'Por mês']
          ].map(([valor, rotulo]) => (
            <button
              key={valor}
              type="button"
              className={`chip ${granularidade === valor ? 'is-active' : ''}`}
              onClick={() => setGranularidade(valor)}
            >
              {rotulo}
            </button>
          ))}
        </div>
      </div>

      {/* 422 aqui = periodo invalido (ate antes de de, mais de 366 dias) */}
      <BlocoEstado {...consulta} carregando={consulta.carregando && !r} />

      <div className="grid-stats" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
        {resumo.map((item) => (
          <StatCard key={item.id} {...item} />
        ))}
      </div>

      {graficos && (
        <div className="graficos-grid">
          <section className="card card-pad">
            <h3>
              <IconTrendUp size={17} />
              Faturamento por {granularidade === 'mes' ? 'mês' : 'semana'}
            </h3>
            <Grafico tipo="bar" {...graficos.faturamento} descricao="Faturamento por período" />
          </section>

          <section className="card card-pad">
            <h3>
              <IconCalendar size={17} />
              Atendimentos por {granularidade === 'mes' ? 'mês' : 'semana'}
            </h3>
            <Grafico tipo="line" {...graficos.atendimentos} descricao="Atendimentos concluídos por período" />
          </section>

          <section className="card card-pad">
            <h3>
              <IconChartLine size={17} />
              Serviços mais vendidos
            </h3>
            {r.ranking.labels.length ? (
              <Grafico tipo="bar" {...graficos.ranking} descricao="Ranking de serviços" />
            ) : (
              <p className="vazio">Nenhum serviço concluído no período.</p>
            )}
          </section>

          <section className="card card-pad">
            <h3>
              <IconXCircle size={17} />
              Concluídos x cancelados
            </h3>
            {r.cancelamento.total ? (
              <Grafico tipo="doughnut" {...graficos.cancelamento} descricao="Taxa de cancelamento" />
            ) : (
              <p className="vazio">Nenhum agendamento com desfecho no período.</p>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
