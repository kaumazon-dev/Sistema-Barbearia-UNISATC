import { useCallback, useEffect, useState } from 'react';
import { useApp } from '../state/AppStore';

/**
 * Busca dados de uma tela e recarrega quando:
 * - as dependencias mudam (filtro, pagina...);
 * - alguma acao do AppStore altera dados (versao).
 *
 * Devolve { dados, carregando, erro, recarregar }.
 */
export function useCarregar(buscar, dependencias, { ativo = true } = {}) {
  const { versao } = useApp();
  const [estado, setEstado] = useState({ dados: null, carregando: ativo, erro: null });
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    if (!ativo) return undefined;
    let cancelado = false;
    setEstado((atual) => ({ ...atual, carregando: true, erro: null }));
    buscar()
      .then((dados) => !cancelado && setEstado({ dados, carregando: false, erro: null }))
      .catch((erro) => !cancelado && setEstado((atual) => ({ ...atual, carregando: false, erro })));
    return () => {
      cancelado = true;
    };
    // buscar muda a cada render; as dependencias reais vem de quem chama
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [...dependencias, versao, tentativa, ativo]);

  const recarregar = useCallback(() => setTentativa((n) => n + 1), []);
  return { ...estado, recarregar };
}
