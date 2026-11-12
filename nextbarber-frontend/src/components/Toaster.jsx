import { useApp } from '../state/AppStore';
import './Toaster.css';

/** Avisos temporarios no canto da tela. */
export default function Toaster() {
  const { avisos, fecharAviso } = useApp();

  return (
    <div className="toaster" role="status" aria-live="polite">
      {avisos.map((aviso) => (
        <div key={aviso.id} className={`toast toast--${aviso.tom}`}>
          <span>{aviso.texto}</span>
          <button type="button" onClick={() => fecharAviso(aviso.id)} aria-label="Fechar aviso">
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}
