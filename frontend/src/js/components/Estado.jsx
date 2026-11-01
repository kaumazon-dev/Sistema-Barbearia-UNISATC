/**
 * Carregando, erro com "tentar de novo" ou lista vazia, dentro de uma tabela
 * ou de um card. Toda tela que busca dados mostra o erro em vez de ficar em
 * branco.
 */
export function LinhaEstado({ colunas, carregando, erro, vazio, textoVazio, recarregar }) {
  // Recarga com linhas na tela (depois de salvar) nao pisca "Carregando".
  if (carregando && vazio) return <LinhaMensagem colunas={colunas}>Carregando…</LinhaMensagem>;
  if (erro) {
    return (
      <LinhaMensagem colunas={colunas}>
        {erro.message}{' '}
        <button type="button" className="link-acao" onClick={recarregar}>
          Tentar de novo
        </button>
      </LinhaMensagem>
    );
  }
  if (vazio && !carregando) return <LinhaMensagem colunas={colunas}>{textoVazio}</LinhaMensagem>;
  return null;
}

function LinhaMensagem({ colunas, children }) {
  return (
    <tr>
      <td colSpan={colunas} className="vazio">
        {children}
      </td>
    </tr>
  );
}

export function BlocoEstado({ carregando, erro, recarregar }) {
  if (carregando) return <p className="vazio">Carregando…</p>;
  if (erro) {
    return (
      <p className="vazio">
        {erro.message}{' '}
        <button type="button" className="link-acao" onClick={recarregar}>
          Tentar de novo
        </button>
      </p>
    );
  }
  return null;
}
