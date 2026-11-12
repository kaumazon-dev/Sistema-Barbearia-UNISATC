import Avatar from './Avatar';
import { IconUserCheck, IconScissors } from './Icons';
import './BarbersPanel.css';

const tomDaSituacao = {
  Disponível: 'green',
  Ocupado: 'amber',
  Intervalo: 'neutral'
};

export default function BarbersPanel({ dados }) {
  return (
    <section className="card barbers">
      <header className="barbers__head">
        <h2 className="section-title">
          <IconUserCheck size={18} />
          Barbeiros Disponíveis
        </h2>
        <p className="barbers__subtitle">Status atualizado em tempo real da equipe.</p>
      </header>

      <ul className="barbers__list">
        {dados.map((b) => (
          <li key={b.id} className="barber">
            <Avatar iniciais={b.iniciais} size={38} />
            <div className="barber__info">
              <strong>{b.apelido}</strong>
              <small>{b.nome}</small>
              {b.atendendo && (
                <span className="barber__now">
                  <IconScissors size={12} />
                  Atendendo: {b.atendendo}
                </span>
              )}
            </div>
            <span className={`dot-label barber__status barber__status--${tomDaSituacao[b.situacao]}`}>
              {b.situacao}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}
