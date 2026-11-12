import { useState } from 'react';
import Campo from '../components/Campo';
import Modal from '../components/Modal';
import { useApp } from '../state/AppStore';
import { STATUS, unidade } from '../data/mock';
import { formatarBRL } from '../utils/formato';

const vazio = {
  horario: '',
  clienteId: '',
  barbeiroId: '',
  servicoId: '',
  status: STATUS.AGUARDANDO
};

export default function AgendamentoForm({ dados }) {
  const { clientes, barbeiros, servicos, salvarAgendamento, fecharModal } = useApp();
  const [form, setForm] = useState(dados ? { ...dados } : vazio);
  const [erros, setErros] = useState({});

  const servicoEscolhido = servicos.find((s) => s.id === Number(form.servicoId));
  const editando = Boolean(dados?.id);

  const mudar = (campo) => (e) => {
    setForm((atual) => ({ ...atual, [campo]: e.target.value }));
    setErros((atuais) => ({ ...atuais, [campo]: undefined }));
  };

  const validar = () => {
    const novos = {};
    if (!form.horario) novos.horario = 'Informe o horário.';
    if (!form.clienteId) novos.clienteId = 'Escolha o cliente.';
    if (!form.barbeiroId) novos.barbeiroId = 'Escolha o barbeiro.';
    if (!form.servicoId) novos.servicoId = 'Escolha o serviço.';
    setErros(novos);
    return Object.keys(novos).length === 0;
  };

  const enviar = (e) => {
    e.preventDefault();
    if (!validar()) return;

    salvarAgendamento({
      ...(editando ? { id: dados.id } : {}),
      horario: form.horario,
      clienteId: Number(form.clienteId),
      barbeiroId: Number(form.barbeiroId),
      servicoId: Number(form.servicoId),
      valor: servicoEscolhido?.preco ?? 0,
      status: form.status
    });
    fecharModal();
  };

  return (
    <Modal
      titulo={editando ? 'Editar agendamento' : 'Novo agendamento'}
      descricao={`${unidade.dataExtenso} — ${unidade.nome}`}
      onFechar={fecharModal}
      rodape={
        <>
          <button type="button" className="btn-ghost" onClick={fecharModal}>
            Cancelar
          </button>
          <button type="submit" form="form-agendamento" className="btn-primary">
            {editando ? 'Salvar alterações' : 'Criar agendamento'}
          </button>
        </>
      }
    >
      <form id="form-agendamento" onSubmit={enviar} noValidate>
        <div className="form-linha">
          <Campo id="ag-horario" rotulo="Horário" erro={erros.horario}>
            <input id="ag-horario" type="time" value={form.horario} onChange={mudar('horario')} />
          </Campo>

          <Campo id="ag-status" rotulo="Status">
            <select id="ag-status" value={form.status} onChange={mudar('status')}>
              {Object.values(STATUS).map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </Campo>
        </div>

        <Campo id="ag-cliente" rotulo="Cliente" erro={erros.clienteId}>
          <select id="ag-cliente" value={form.clienteId} onChange={mudar('clienteId')}>
            <option value="">Selecione…</option>
            {clientes.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nome} — {c.telefone}
              </option>
            ))}
          </select>
        </Campo>

        <Campo id="ag-barbeiro" rotulo="Barbeiro" erro={erros.barbeiroId}>
          <select id="ag-barbeiro" value={form.barbeiroId} onChange={mudar('barbeiroId')}>
            <option value="">Selecione…</option>
            {barbeiros.map((b) => (
              <option key={b.id} value={b.id}>
                {b.apelido} — {b.situacao}
              </option>
            ))}
          </select>
        </Campo>

        <Campo
          id="ag-servico"
          rotulo="Serviço"
          erro={erros.servicoId}
          dica={
            servicoEscolhido
              ? `${servicoEscolhido.duracao} min · ${formatarBRL(servicoEscolhido.preco)}`
              : 'O valor é preenchido pelo serviço escolhido.'
          }
        >
          <select id="ag-servico" value={form.servicoId} onChange={mudar('servicoId')}>
            <option value="">Selecione…</option>
            {servicos
              .filter((s) => s.ativo)
              .map((s) => (
                <option key={s.id} value={s.id}>
                  {s.nome} — {formatarBRL(s.preco)}
                </option>
              ))}
          </select>
        </Campo>
      </form>
    </Modal>
  );
}
