import { useState } from 'react';
import Campo from '../components/Campo';
import Modal from '../components/Modal';
import { unidade } from '../data/mock';
import { useApp } from '../state/AppStore';

const vazio = {
  apelido: '',
  nome: '',
  especialidade: '',
  comissao: 40,
  situacao: 'Disponível'
};

export default function BarbeiroForm({ dados }) {
  const { salvarBarbeiro, fecharModal } = useApp();
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
    if (!form.apelido.trim()) novos.apelido = 'Informe como ele aparece na agenda.';
    if (!form.nome.trim()) novos.nome = 'Informe o nome completo.';
    setErros(novos);
    if (Object.keys(novos).length) return;

    salvarBarbeiro({
      ...form,
      apelido: form.apelido.trim(),
      nomeAgenda: form.apelido.trim(),
      nome: form.nome.trim(),
      comissao: Number(form.comissao) || 0
    });
    fecharModal();
  };

  return (
    <Modal
      titulo={editando ? 'Editar barbeiro' : 'Novo barbeiro'}
      descricao={`Membro da equipe da ${unidade.nome}.`}
      onFechar={fecharModal}
      rodape={
        <>
          <button type="button" className="btn-ghost" onClick={fecharModal}>
            Cancelar
          </button>
          <button type="submit" form="form-barbeiro" className="btn-primary">
            {editando ? 'Salvar alterações' : 'Cadastrar barbeiro'}
          </button>
        </>
      }
    >
      <form id="form-barbeiro" onSubmit={enviar} noValidate>
        <Campo
          id="ba-apelido"
          rotulo="Nome na agenda"
          erro={erros.apelido}
          dica="É o que aparece na tabela de agendamentos."
        >
          <input
            id="ba-apelido"
            type="text"
            value={form.apelido}
            onChange={mudar('apelido')}
            placeholder='Ex.: Rafa "Tesoura"'
          />
        </Campo>

        <Campo id="ba-nome" rotulo="Nome completo" erro={erros.nome}>
          <input
            id="ba-nome"
            type="text"
            value={form.nome}
            onChange={mudar('nome')}
            placeholder="Ex.: Rafael Souza Lima"
          />
        </Campo>

        <Campo id="ba-esp" rotulo="Especialidade">
          <input
            id="ba-esp"
            type="text"
            value={form.especialidade}
            onChange={mudar('especialidade')}
            placeholder="Ex.: Degradê e navalhado"
          />
        </Campo>

        <div className="form-linha">
          <Campo id="ba-com" rotulo="Comissão (%)">
            <input
              id="ba-com"
              type="number"
              min="0"
              max="100"
              step="5"
              value={form.comissao}
              onChange={mudar('comissao')}
            />
          </Campo>

          <Campo id="ba-sit" rotulo="Situação">
            <select id="ba-sit" value={form.situacao} onChange={mudar('situacao')}>
              <option value="Disponível">Disponível</option>
              <option value="Ocupado">Ocupado</option>
              <option value="Intervalo">Intervalo</option>
            </select>
          </Campo>
        </div>
      </form>
    </Modal>
  );
}
