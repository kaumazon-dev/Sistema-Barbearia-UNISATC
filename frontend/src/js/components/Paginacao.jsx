/** Navegacao do envelope paginado da API ({ pagina, paginas, total }). */
export default function Paginacao({ dados, onMudar }) {
  if (!dados || dados.paginas <= 1) return null;
  const { pagina, paginas, total } = dados;

  return (
    <div className="paginacao">
      <span>
        Página {pagina} de {paginas} · {total} registros
      </span>
      <div>
        <button type="button" className="btn-ghost" disabled={pagina <= 1} onClick={() => onMudar(pagina - 1)}>
          Anterior
        </button>
        <button
          type="button"
          className="btn-ghost"
          disabled={pagina >= paginas}
          onClick={() => onMudar(pagina + 1)}
        >
          Próxima
        </button>
      </div>
    </div>
  );
}
