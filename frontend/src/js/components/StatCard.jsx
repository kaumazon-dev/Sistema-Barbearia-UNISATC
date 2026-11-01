import { IconCalendar, IconWallet, IconUserCheck, IconGauge } from './Icons';
import '../../assets/css/components/StatCard.css';

const icones = {
  calendar: IconCalendar,
  wallet: IconWallet,
  userCheck: IconUserCheck,
  gauge: IconGauge
};

export default function StatCard({ rotulo, valor, icone, destaque, tom, complemento }) {
  const Icone = icones[icone] || IconCalendar;

  return (
    <article className="stat card">
      <header className="stat__head">
        <span className="stat__label">{rotulo}</span>
        <span className="stat__icon">
          <Icone size={17} />
        </span>
      </header>

      <strong className="stat__value">{valor}</strong>

      <p className="stat__foot">
        <span className={`stat__delta stat__delta--${tom}`}>{destaque}</span>
        <span className="stat__hint">{complemento}</span>
      </p>
    </article>
  );
}
