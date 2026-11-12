import { useState } from 'react';
import Campo from '../components/Campo';
import Modal from '../components/Modal';
import { useApp } from '../state/AppStore';

const vazio = { nome: '', telefone: '', plano: 'Novo', ticket: 0 };

export default function ClienteForm({ dados }) {
  const { salvarCliente, fecharModal } = useApp();
  const [form, setForm] = useState(dados ? { ...dados } : vazio);
  const [erros, setErros] = useState({});
  const editando = Boolean(dados?.id);

  const mudar = (campo) => (e) => {
    setForm((atual) => ({ ...atual, [campo]: e.target.value }));
    setErros((atuais) => ({ ...atuais, [campo]: undefined }));
  };

  const enviar = (e) => {
    e.preventDefault();
    const novos = {};
    if (!form.nome.trim()) novos.nome = 'Informe o nome.';
    if (!form.telefone.trim()) novos.telefone = 'Informe o telefone.';
    setErros(novos);
    if (Object.keys(novos).length) return;

    salvarCliente({ ...form, nome: form.nome.trim(), ticket: Number(form.ticket) || 0 });
    fecharModal();
  };

  return (
    <Modal
      titulo={editando ? 'Editar cliente' : 'Novo cliente'}
      descricao="Cadastro básico do cliente da unidade."
      onFechar={fecharModal}
      rodape={
        <>
          <button type="button" className="btn-ghost" onClick={fecharModal}>
            Cancelar
          </button>
          <button type="submit" form="form-cliente" className="btn-primary">
            {editando ? 'Salvar alterações' : 'Cadastrar cliente'}
          </button>
        </>
      }
    >
      <form id="form-cliente" onSubmit={enviar} noValidate>
        <Campo id="cl-nome" rotulo="Nome completo" erro={erros.nome}>
          <input
            id="cl-nome"
            type="text"
            value={form.nome}
            onChange={mudar('nome')}
            placeholder="Ex.: João Pedro Ramos"
          />
        </Campo>

        <div className="form-linha">
          <Campo id="cl-tel" rotulo="Telefone" erro={erros.telefone}>
            <input
              id="cl-tel"
              type="text"
              value={form.telefone}
              onChange={mudar('telefone')}
              placeholder="(48) 99999-0000"
            />
          </Campo>

          <Campo id="cl-plano" rotulo="Plano">
            <select id="cl-plano" value={form.plano} onChange={mudar('plano')}>
              <option value="Novo">Novo</option>
              <option value="Recorrente">Recorrente</option>
              <option value="VIP">VIP</option>
            </select>
          </Campo>
        </div>

        <Campo id="cl-ticket" rotulo="Ticket médio (R$)" dica="Opcional — só para o relatório.">
          <input
            id="cl-ticket"
            type="number"
            min="0"
            step="5"
            value={form.ticket}
            onChange={mudar('ticket')}
          />
        </Campo>
      </form>
    </Modal>
  );
}
