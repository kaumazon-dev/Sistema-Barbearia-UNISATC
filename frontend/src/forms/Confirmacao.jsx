import Modal from '../components/Modal';
import { useApp } from '../state/AppStore';

/** Confirmacao usada antes de excluir algo. */
export default function Confirmacao({ dados }) {
  const { fecharModal } = useApp();

  return (
    <Modal titulo={dados.titulo} largura={420} onFechar={fecharModal}>
      <p className="confirma__texto">{dados.texto}</p>

      <div className="confirma__acoes">
        <button type="button" className="btn-ghost" onClick={fecharModal}>
          Cancelar
        </button>
        <button
          type="button"
          className="btn-perigo"
          onClick={() => {
            dados.aoConfirmar();
            fecharModal();
          }}
        >
          {dados.rotuloConfirmar || 'Excluir'}
        </button>
      </div>
    </Modal>
  );
}
