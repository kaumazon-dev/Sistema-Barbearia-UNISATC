import { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import '../../assets/css/components/MenuAcoes.css';

const ALTURA_ITEM = 36;
const FOLGA = 8;

/**
 * Menu suspenso de acoes de uma linha da tabela.
 *
 * A lista e desenhada no <body> (portal) com position: fixed, na posicao do
 * botao. Dentro da tabela ela seria cortada pelo overflow do .table-wrap: na
 * ultima linha, ou numa tabela de uma linha so, o menu abria escondido.
 * Sem espaco embaixo, abre para cima.
 */
export default function MenuAcoes({ itens }) {
  const [posicao, setPosicao] = useState(null);
  const raiz = useRef(null);
  const lista = useRef(null);
  const aberto = posicao !== null;

  const fechar = () => setPosicao(null);

  const alternar = () => {
    if (aberto) return fechar();
    const botao = raiz.current.getBoundingClientRect();
    const altura = itens.length * ALTURA_ITEM + 2 * FOLGA;
    const espacoAbaixo = window.innerHeight - botao.bottom;
    const paraCima = espacoAbaixo < altura + FOLGA && botao.top > espacoAbaixo;
    const direita = window.innerWidth - botao.right;
    setPosicao(
      paraCima
        ? { right: direita, bottom: window.innerHeight - botao.top + 6 }
        : { right: direita, top: botao.bottom + 6 }
    );
    return undefined;
  };

  useEffect(() => {
    if (!aberto) return undefined;
    const aoClicarFora = (e) => {
      if (!raiz.current?.contains(e.target) && !lista.current?.contains(e.target)) fechar();
    };
    const aoTeclar = (e) => e.key === 'Escape' && fechar();
    // Posicao fixa nao acompanha a rolagem: rolou, fecha.
    const aoRolar = (e) => {
      if (!lista.current?.contains(e.target)) fechar();
    };
    document.addEventListener('mousedown', aoClicarFora);
    document.addEventListener('keydown', aoTeclar);
    window.addEventListener('scroll', aoRolar, true);
    window.addEventListener('resize', fechar);
    return () => {
      document.removeEventListener('mousedown', aoClicarFora);
      document.removeEventListener('keydown', aoTeclar);
      window.removeEventListener('scroll', aoRolar, true);
      window.removeEventListener('resize', fechar);
    };
  }, [aberto]);

  return (
    <div className="menu-acoes" ref={raiz}>
      <button
        type="button"
        className="menu-acoes__botao"
        onClick={alternar}
        aria-haspopup="menu"
        aria-expanded={aberto}
        aria-label="Ações"
      >
        •••
      </button>

      {aberto &&
        createPortal(
          <div className="menu-acoes__lista" role="menu" ref={lista} style={posicao}>
            {itens.map((item) =>
              item.separador ? (
                <hr key={item.chave} className="menu-acoes__hr" />
              ) : (
                <button
                  key={item.chave}
                  type="button"
                  role="menuitem"
                  className={`menu-acoes__item ${item.perigo ? 'is-perigo' : ''}`}
                  onClick={() => {
                    fechar();
                    item.aoClicar();
                  }}
                >
                  {item.rotulo}
                </button>
              )
            )}
          </div>,
          document.body
        )}
    </div>
  );
}
