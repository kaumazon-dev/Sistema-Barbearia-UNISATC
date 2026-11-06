import { useState } from 'react';
import Campo from '../../js/components/Campo';
import Modal from '../../js/components/Modal';
import { useApp } from '../../js/store/AppStore';
import { authApi } from '../../js/api/auth.api';
import { useCarregar } from '../../js/utils/useCarregar';
import { hojeISO, montarInicio, separarInicio, hora, data } from '../../js/utils/datas';
import { errosDosCampos } from '../../js/utils/erros';

/**
 * Remarcar muda so o inicio e, se quiser, o barbeiro. A duracao e os
 * servicos ficam os mesmos (RF18): para trocar servico, cancele e marque de novo.
 */
export default function RemarcarForm({ dados }) {
  const { remarcarAgendamento, fecharModal } = useApp();
  const atual = separarInicio(dados.inicio);

  const [form, setForm] = useState({
    dia: atual.dia < hojeISO() ? hojeISO() : atual.dia,
    horario: atual.horario,
    barbeiroId: String(dados.barbeiro.id)
  });
  const [erros, setErros] = useState({});
  const [erroGeral, setErroGeral] = useState('');
  const [enviando, setEnviando] = useState(false);

  const { dados: barbeiros } = useCarregar(() => authApi.listarBarbeiros(), []);

  const mudar = (campo) => (e) => {
    setForm((f) => ({ ...f, [campo]: e.target.value }));
    setErros((atuais) => ({ ...atuais, [campo]: undefined }));
    setErroGeral('');
  };

  const enviar = async (e) => {
    e.preventDefault();
    if (!form.dia || !form.horario) {
      setErros({ horario: 'Informe a data e o horário.' });
      return;
    }
    setEnviando(true);
    try {
      const corpo = { inicio: montarInicio(form.dia, form.horario) };
      if (Number(form.barbeiroId) !== dados.barbeiro.id) corpo.barbeiro_id = Number(form.barbeiroId);
      await remarcarAgendamento(dados.id, corpo);
      fecharModal();
    } catch (erro) {
      const porCampo = errosDosCampos(erro, { inicio: 'Data ou horário inválido.', barbeiro_id: 'Barbeiro inválido.' });
      setErros({ horario: porCampo.inicio, barbeiroId: porCampo.barbeiro_id });
      if (erro.codigo !== 'DADOS_INVALIDOS') setErroGeral(erro.message);
      setEnviando(false);
    }
  };

  return (
    <Modal
      titulo="Remarcar horário"
      descricao={`${dados.cliente.nome} · hoje marcado para ${data(dados.inicio)}, das ${hora(dados.inicio)} às ${hora(dados.fim)}`}
      onFechar={fecharModal}
      rodape={
        <>
          <button type="button" className="btn-ghost" onClick={fecharModal}>
            Cancelar
          </button>
          <button type="submit" form="form-remarcar" className="btn-primary" disabled={enviando}>
            {enviando ? 'Salvando…' : 'Remarcar'}
          </button>
        </>
      }
    >
      {erroGeral && (
        <p className="erro-form" role="alert">
          {erroGeral}
        </p>
      )}
      <form id="form-remarcar" onSubmit={enviar} noValidate>
        <div className="form-linha">
          <Campo id="re-dia" rotulo="Nova data">
            <input id="re-dia" type="date" min={hojeISO()} value={form.dia} onChange={mudar('dia')} />
          </Campo>
          <Campo id="re-horario" rotulo="Novo horário" erro={erros.horario}>
            <input id="re-horario" type="time" value={form.horario} onChange={mudar('horario')} />
          </Campo>
        </div>

        <Campo
          id="re-barbeiro"
          rotulo="Barbeiro"
          erro={erros.barbeiroId}
          dica={`Serviços mantidos: ${dados.servicos.map((s) => s.nome).join(' + ')}`}
        >
          <select id="re-barbeiro" value={form.barbeiroId} onChange={mudar('barbeiroId')}>
            {(barbeiros || [dados.barbeiro]).map((b) => (
              <option key={b.id} value={b.id}>
                {b.nome}
              </option>
            ))}
          </select>
        </Campo>
      </form>
    </Modal>
  );
}
