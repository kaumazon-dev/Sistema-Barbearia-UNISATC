import './PageHeader.css';

export default function PageHeader({ titulo, subtitulo, acao }) {
  return (
    <div className="page-header">
      <div>
        <h1 className="page-header__title">{titulo}</h1>
        {subtitulo && <p className="page-header__subtitle">{subtitulo}</p>}
      </div>
      {acao}
    </div>
  );
}
