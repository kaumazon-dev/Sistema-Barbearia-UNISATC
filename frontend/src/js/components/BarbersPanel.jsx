import Avatar from './Avatar';
import { IconUserCheck, IconScissors } from './Icons';
import { iniciaisDe } from '../utils/formato';
import '../../assets/css/components/BarbersPanel.css';

const tomDaSituacao = {
  Disponível: 'green',
  Ocupado: 'amber'
};

/** dados: barbeiros com { situacao, atendendo, atendimentosHoje } calculados da agenda. */
export default function BarbersPanel({ dados }) {
  return (
    <section className="card barbers">
      <header className="barbers__head">
        <h2 className="section-title">
          <IconUserCheck size={18} />
          Barbeiros
        </h2>
        <p className="barbers__subtitle">Situação calculada pela agenda de hoje.</p>
      </header>

      <ul className="barbers__list">
        {dados.map((b) => (
          <li key={b.id} className="barber">
            <Avatar iniciais={iniciaisDe(b.nome)} size={38} />
            <div className="barber__info">
              <strong>{b.nome}</strong>
              <small>{b.atendimentosHoje} horários hoje</small>
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
        {dados.length === 0 && <li className="vazio">Nenhum barbeiro ativo.</li>}
      </ul>
    </section>
  );
}
