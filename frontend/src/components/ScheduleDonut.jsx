import './ScheduleDonut.css';

export default function ScheduleDonut({ titulo, rotulo, texto, ativos, total, percentual }) {
  const raio = 22;
  const circunferencia = 2 * Math.PI * raio;
  const preenchido = (percentual / 100) * circunferencia;

  return (
    <section className="card schedule">
      <h3 className="schedule__title">{titulo}</h3>

      <div className="schedule__body">
        <svg className="schedule__donut" viewBox="0 0 56 56" role="img" aria-label={`${percentual}% da capacidade`}>
          <circle cx="28" cy="28" r={raio} className="schedule__track" />
          <circle
            cx="28"
            cy="28"
            r={raio}
            className="schedule__fill"
            strokeDasharray={`${preenchido} ${circunferencia}`}
          />
          <text x="28" y="28" className="schedule__ratio">
            {ativos}/{total}
          </text>
        </svg>

        <div className="schedule__info">
          <strong>{rotulo}</strong>
          <small>{texto}</small>
        </div>
      </div>
    </section>
  );
}
