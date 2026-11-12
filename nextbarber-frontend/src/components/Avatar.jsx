import './Avatar.css';

/**
 * Avatar por iniciais — evita depender de imagens externas no mockup.
 */
export default function Avatar({ iniciais, size = 40, tone = 'gold' }) {
  return (
    <span
      className={`avatar avatar--${tone}`}
      style={{ width: size, height: size, fontSize: Math.round(size * 0.36) }}
      aria-hidden="true"
    >
      {iniciais}
    </span>
  );
}
