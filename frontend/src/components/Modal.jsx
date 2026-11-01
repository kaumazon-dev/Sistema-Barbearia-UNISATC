import { useEffect, useRef } from 'react';
import './Modal.css';

/** Modal acessivel: fecha no ESC, no clique fora e devolve o foco. */
export default function Modal({ titulo, descricao, largura = 520, onFechar, children, rodape }) {
  const caixa = useRef(null);
  const focoAnterior = useRef(null);

  useEffect(() => {
    focoAnterior.current = document.activeElement;
    const aoTeclar = (e) => {
      if (e.key === 'Escape') onFechar();
    };
    document.addEventListener('keydown', aoTeclar);
    document.body.style.overflow = 'hidden';

    // foca o primeiro campo do formulario
    const alvo = caixa.current?.querySelector('input, select, textarea, button');
    alvo?.focus();

    return () => {
      document.removeEventListener('keydown', aoTeclar);
      document.body.style.overflow = '';
      focoAnterior.current?.focus?.();
    };
  }, [onFechar]);

  return (
    <div className="modal" onMouseDown={(e) => e.target === e.currentTarget && onFechar()}>
      <div
        className="modal__caixa"
        style={{ maxWidth: largura }}
        role="dialog"
        aria-modal="true"
        aria-label={titulo}
        ref={caixa}
      >
        <header className="modal__head">
          <div>
            <h2 className="modal__title">{titulo}</h2>
            {descricao && <p className="modal__desc">{descricao}</p>}
          </div>
          <button type="button" className="modal__x" onClick={onFechar} aria-label="Fechar">
            ✕
          </button>
        </header>

        <div className="modal__body">{children}</div>

        {rodape && <footer className="modal__foot">{rodape}</footer>}
      </div>
    </div>
  );
}
