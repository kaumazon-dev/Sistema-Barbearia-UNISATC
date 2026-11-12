import { useState } from 'react';
import Campo from '../components/Campo';
import Modal from '../components/Modal';
import { useApp } from '../state/AppStore';

const vazio = { nome: '', categoria: 'Cabelo', duracao: 30, preco: 50, ativo: true };

export default function ServicoForm({ dados }) {
  const { salvarServico, fecharModal } = useApp();
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
    if (!form.nome.trim()) novos.nome = 'Informe o nome do serviço.';
    if (Number(form.duracao) <= 0) novos.duracao = 'Duração deve ser maior que zero.';
    if (Number(form.preco) < 0) novos.preco = 'Preço não pode ser negativo.';
    setErros(novos);
    if (Object.keys(novos).length) return;

    salvarServico({
      ...form,
      nome: form.nome.trim(),
      duracao: Number(form.duracao),
      preco: Number(form.preco)
    });
    fecharModal();
  };

  return (
    <Modal
      titulo={editando ? 'Editar serviço' : 'Novo serviço'}
      descricao="Catálogo usado ao montar um agendamento."
      onFechar={fecharModal}
      rodape={
        <>
          <button type="button" className="btn-ghost" onClick={fecharModal}>
            Cancelar
          </button>
          <button type="submit" form="form-servico" className="btn-primary">
            {editando ? 'Salvar alterações' : 'Cadastrar serviço'}
          </button>
        </>
      }
    >
      <form id="form-servico" onSubmit={enviar} noValidate>
        <Campo id="se-nome" rotulo="Nome do serviço" erro={erros.nome}>
          <input
            id="se-nome"
            type="text"
            value={form.nome}
            onChange={mudar('nome')}
            placeholder="Ex.: Corte + Hidratação"
          />
        </Campo>

        <Campo id="se-cat" rotulo="Categoria">
          <select id="se-cat" value={form.categoria} onChange={mudar('categoria')}>
            {['Cabelo', 'Barba', 'Combo', 'Química', 'Tratamento'].map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </Campo>

        <div className="form-linha">
          <Campo id="se-dur" rotulo="Duração (min)" erro={erros.duracao}>
            <input
              id="se-dur"
              type="number"
              min="5"
              step="5"
              value={form.duracao}
              onChange={mudar('duracao')}
            />
          </Campo>

          <Campo id="se-preco" rotulo="Preço (R$)" erro={erros.preco}>
            <input
              id="se-preco"
              type="number"
              min="0"
              step="5"
              value={form.preco}
              onChange={mudar('preco')}
            />
          </Campo>
        </div>
      </form>
    </Modal>
  );
}
