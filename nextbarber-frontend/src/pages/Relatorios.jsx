import PageHeader from '../components/PageHeader';
import StatCard from '../components/StatCard';
import { IconTrendUp, IconChartLine } from '../components/Icons';
import { faturamentoSemana, rankingServicos } from '../data/mock';
import { useApp } from '../state/AppStore';
import { formatarBRL } from '../utils/formato';
import './pages.css';

const resumo = [
  {
    id: 'receita',
    rotulo: 'Receita da semana',
    valor: 'R$ 12.190',
    icone: 'wallet',
    destaque: '+8,4%',
    tom: 'green',
    complemento: 'vs. semana anterior'
  },
  {
    id: 'atendimentos',
    rotulo: 'Atendimentos',
    valor: '164',
    icone: 'userCheck',
    destaque: '+19',
    tom: 'green',
    complemento: 'Média de 23 por dia'
  },
  {
    id: 'ticket',
    rotulo: 'Ticket médio',
    valor: 'R$ 74,30',
    icone: 'gauge',
    destaque: '-2,1%',
    tom: 'red',
    complemento: 'Meta de R$ 80,00'
  },
  {
    id: 'retorno',
    rotulo: 'Taxa de retorno',
    valor: '61%',
    icone: 'calendar',
    destaque: '+5%',
    tom: 'green',
    complemento: 'Clientes que remarcaram'
  }
];

export default function Relatorios() {
  const { indicadores, avisar } = useApp();
  const maior = Math.max(...faturamentoSemana.map((d) => d.valor));

  // O sabado do grafico e o dia corrente: acompanha o que acontece na agenda.
  const serie = faturamentoSemana.map((d) =>
    d.dia === 'Sáb' ? { ...d, valor: indicadores.faturado } : d
  );
  const teto = Math.max(maior, indicadores.faturado, 1);

  return (
    <div className="page">
      <PageHeader
        titulo="Relatórios"
        subtitulo="Visão gerencial da semana de 08 a 14 de outubro."
        acao={
          <button
            type="button"
            className="btn-ghost"
            onClick={() => avisar('Exportação de PDF não faz parte deste protótipo.')}
          >
            Exportar PDF
          </button>
        }
      />

      <div className="grid-stats" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
        {resumo.map((item) => (
          <StatCard key={item.id} {...item} />
        ))}
      </div>

      <div className="settings-grid">
        <section className="card card-pad">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <IconTrendUp size={17} />
            Faturamento por dia
          </h3>
          <div className="bars">
            {serie.map((d) => (
              <div key={d.dia} className="bars__item">
                <span className="bars__value">{(d.valor / 1000).toFixed(1)}k</span>
                <span className="bars__bar" style={{ height: `${(d.valor / teto) * 100}%` }} />
                <span className="bars__label">{d.dia}</span>
              </div>
            ))}
          </div>
        </section>

        <section className="card card-pad">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <IconChartLine size={17} />
            Serviços mais vendidos
          </h3>
          <div>
            {rankingServicos.map((s) => (
              <div key={s.nome} className="rank-row">
                <div className="rank-row__top">
                  <strong>{s.nome}</strong>
                  <span>
                    {formatarBRL(s.receita)} · {s.participacao}%
                  </span>
                </div>
                <div className="progress">
                  <div className="progress__fill" style={{ width: `${s.participacao}%` }} />
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
