import { useState } from 'react';
import Campo from '../components/Campo';
import Modal from '../components/Modal';
import { useApp } from '../state/AppStore';
import { authApi } from '../api/auth.api';
import { clientesApi } from '../api/clientes.api';
import { servicosApi } from '../api/servicos.api';
import { useCarregar } from '../utils/useCarregar';
import { formatarBRL, somarDinheiro } from '../utils/formato';
import { hojeISO, montarInicio } from '../utils/datas';
import { errosDosCampos } from '../utils/erros';

const mensagens = {
  cliente_id: 'Escolha o cliente.',
  barbeiro_id: 'Escolha o barbeiro.',
  inicio: 'Data ou horário inválido.',
  servico_ids: 'Escolha de 1 a 10 serviços.',
  observacao: 'Até 500 caracteres.'
};

/** dados opcionais: { dia, barbeiroId, clienteId } para abrir ja preenchido. */
export default function AgendamentoForm({ dados }) {
  const { usuario, criarAgendamento, fecharModal } = useApp();
  const ehCliente = usuario.papel === 'cliente';

  const [form, setForm] = useState({
    dia: dados?.dia && dados.dia >= hojeISO() ? dados.dia : hojeISO(),
    horario: '',
    clienteId: dados?.clienteId ? String(dados.clienteId) : '',
    barbeiroId: dados?.barbeiroId ? String(dados.barbeiroId) : '',
    servicoIds: [],
    observacao: ''
  });
  const [erros, setErros] = useState({});
  const [erroGeral, setErroGeral] = useState('');
  const [enviando, setEnviando] = useState(false);

  const opcoes = useCarregar(async () => {
    const [barbeiros, servicos, clientes] = await Promise.all([
      authApi.listarBarbeiros(),
      servicosApi.listar({ ativo: true }),
      // cliente marca sempre para si mesmo: a API ignora cliente_id
      ehCliente ? null : clientesApi.listar({ ativo: true, porPagina: 100 })
    ]);
    // Servico inativo nao entra em agendamento novo (RF12).
    return { barbeiros, servicos: servicos.filter((s) => s.ativo), clientes: clientes?.itens || [] };
  }, []);

  const { barbeiros = [], servicos = [], clientes = [] } = opcoes.dados || {};
  const escolhidos = servicos.filter((s) => form.servicoIds.includes(s.id));
  const duracao = escolhidos.reduce((soma, s) => soma + s.duracao_minutos, 0);
  const total = somarDinheiro(escolhidos.map((s) => s.preco));

  const mudar = (campo) => (e) => {
    setForm((atual) => ({ ...atual, [campo]: e.target.value }));
    setErros((atuais) => ({ ...atuais, [campo]: undefined }));
    setErroGeral('');
  };

  const alternarServico = (id) => {
    setForm((atual) => ({
      ...atual,
      servicoIds: atual.servicoIds.includes(id)
        ? atual.servicoIds.filter((s) => s !== id)
        : [...atual.servicoIds, id]
    }));
    setErros((atuais) => ({ ...atuais, servicoIds: undefined }));
  };

  const validar = () => {
    const novos = {};
    if (!form.dia) novos.dia = 'Informe a data.';
    if (!form.horario) novos.horario = 'Informe o horário.';
    if (!ehCliente && !form.clienteId) novos.clienteId = mensagens.cliente_id;
    if (!form.barbeiroId) novos.barbeiroId = mensagens.barbeiro_id;
    if (form.servicoIds.length === 0) novos.servicoIds = 'Escolha pelo menos um serviço.';
    setErros(novos);
    return Object.keys(novos).length === 0;
  };

  const enviar = async (e) => {
    e.preventDefault();
    if (!validar()) return;
    setEnviando(true);
    try {
      await criarAgendamento({
        ...(ehCliente ? {} : { cliente_id: Number(form.clienteId) }),
        barbeiro_id: Number(form.barbeiroId),
        inicio: montarInicio(form.dia, form.horario),
        servico_ids: form.servicoIds,
        ...(form.observacao.trim() ? { observacao: form.observacao.trim() } : {})
      });
      fecharModal();
    } catch (erro) {
      const porCampo = errosDosCampos(erro, mensagens);
      setErros({
        clienteId: porCampo.cliente_id,
        barbeiroId: porCampo.barbeiro_id,
        horario: porCampo.inicio,
        servicoIds: porCampo.servico_ids,
        observacao: porCampo.observacao
      });
      // CONFLITO (horario ocupado) e REGRA_VIOLADA (horario no passado...) ja
      // vem com mensagem pronta para exibir.
      if (erro.codigo !== 'DADOS_INVALIDOS') setErroGeral(erro.message);
      setEnviando(false);
    }
  };

  return (
    <Modal
      titulo={ehCliente ? 'Marcar horário' : 'Novo agendamento'}
      descricao="O horário de término é calculado pela duração dos serviços."
      onFechar={fecharModal}
      rodape={
        <>
          <button type="button" className="btn-ghost" onClick={fecharModal}>
            Cancelar
          </button>
          <button type="submit" form="form-agendamento" className="btn-primary" disabled={enviando || !opcoes.dados}>
            {enviando ? 'Salvando…' : 'Criar agendamento'}
          </button>
        </>
      }
    >
      {opcoes.erro && <p className="erro-form">{opcoes.erro.message}</p>}
      {erroGeral && (
        <p className="erro-form" role="alert">
          {erroGeral}
        </p>
      )}

      <form id="form-agendamento" onSubmit={enviar} noValidate>
        <div className="form-linha">
          <Campo id="ag-dia" rotulo="Data" erro={erros.dia}>
            <input id="ag-dia" type="date" min={hojeISO()} value={form.dia} onChange={mudar('dia')} />
          </Campo>

          <Campo id="ag-horario" rotulo="Horário" erro={erros.horario}>
            <input id="ag-horario" type="time" value={form.horario} onChange={mudar('horario')} />
          </Campo>
        </div>

        {!ehCliente && (
          <Campo id="ag-cliente" rotulo="Cliente" erro={erros.clienteId}>
            <select id="ag-cliente" value={form.clienteId} onChange={mudar('clienteId')}>
              <option value="">Selecione…</option>
              {clientes.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.nome}
                  {c.telefone ? ` — ${c.telefone}` : ''}
                </option>
              ))}
            </select>
          </Campo>
        )}

        <Campo id="ag-barbeiro" rotulo="Barbeiro" erro={erros.barbeiroId}>
          <select id="ag-barbeiro" value={form.barbeiroId} onChange={mudar('barbeiroId')}>
            <option value="">Selecione…</option>
            {barbeiros.map((b) => (
              <option key={b.id} value={b.id}>
                {b.nome}
              </option>
            ))}
          </select>
        </Campo>

        <Campo
          id="ag-servicos"
          rotulo="Serviços"
          erro={erros.servicoIds}
          dica={escolhidos.length ? `${duracao} min · ${formatarBRL(total)}` : 'Escolha um ou mais serviços.'}
        >
          <div id="ag-servicos" className="servicos-escolha">
            {servicos.map((s) => {
              const marcado = form.servicoIds.includes(s.id);
              return (
                <label key={s.id} className={marcado ? 'is-marcado' : ''}>
                  <input type="checkbox" checked={marcado} onChange={() => alternarServico(s.id)} />
                  {s.nome}
                  <span>
                    {s.duracao_minutos} min · {formatarBRL(s.preco)}
                  </span>
                </label>
              );
            })}
            {opcoes.dados && servicos.length === 0 && <p className="vazio">Nenhum serviço ativo.</p>}
          </div>
        </Campo>

        <Campo id="ag-obs" rotulo="Observação" erro={erros.observacao} dica="Opcional.">
          <textarea id="ag-obs" maxLength={500} value={form.observacao} onChange={mudar('observacao')} />
        </Campo>
      </form>
    </Modal>
  );
}
