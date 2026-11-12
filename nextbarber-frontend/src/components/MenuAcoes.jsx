import { useEffect, useRef, useState } from 'react';
import './MenuAcoes.css';

/** Menu suspenso de acoes de uma linha da tabela. */
export default function MenuAcoes({ itens }) {
  const [aberto, setAberto] = useState(false);
  const raiz = useRef(null);

  useEffect(() => {
    if (!aberto) return undefined;
    const aoClicarFora = (e) => {
      if (!raiz.current?.contains(e.target)) setAberto(false);
    };
    const aoTeclar = (e) => e.key === 'Escape' && setAberto(false);
    document.addEventListener('mousedown', aoClicarFora);
    document.addEventListener('keydown', aoTeclar);
    return () => {
      document.removeEventListener('mousedown', aoClicarFora);
      document.removeEventListener('keydown', aoTeclar);
    };
  }, [aberto]);

  return (
    <div className="menu-acoes" ref={raiz}>
      <button
        type="button"
        className="menu-acoes__botao"
        onClick={() => setAberto((v) => !v)}
        aria-haspopup="menu"
        aria-expanded={aberto}
        aria-label="Ações"
      >
        •••
      </button>

      {aberto && (
        <div className="menu-acoes__lista" role="menu">
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
                  setAberto(false);
                  item.aoClicar();
                }}
              >
                {item.rotulo}
              </button>
            )
          )}
        </div>
      )}
    </div>
  );
}
