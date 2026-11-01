import { useState } from 'react';
import Campo from '../../js/components/Campo';
import Modal from '../../js/components/Modal';
import { useApp } from '../../js/store/AppStore';
import { errosDosCampos } from '../../js/utils/erros';

const mensagens = {
  nome: 'Use de 2 a 120 caracteres.',
  duracao_minutos: 'Duração inteira de 1 a 480 minutos.',
  preco: 'Preço de 0 a 99.999.999,99, com até 2 casas.'
};

/** "35,9" ou "35.90" -> "35.90"; o preco viaja como string (RNF09). */
const normalizarPreco = (texto) => String(texto).trim().replace(',', '.');

export default function ServicoForm({ dados }) {
  const { salvarServico, fecharModal } = useApp();
  const editando = Boolean(dados?.id);
  const [form, setForm] = useState({
    nome: dados?.nome || '',
    duracao: dados?.duracao_minutos ?? 30,
    preco: dados?.preco ?? ''
  });
  const [erros, setErros] = useState({});
  const [erroGeral, setErroGeral] = useState('');
  const [enviando, setEnviando] = useState(false);

  const mudar = (campo) => (e) => {
    setForm((atual) => ({ ...atual, [campo]: e.target.value }));
    setErros((atuais) => ({ ...atuais, [campo]: undefined }));
  };

  const enviar = async (e) => {
    e.preventDefault();
    const preco = normalizarPreco(form.preco);
    const duracao = Number(form.duracao);
    const novos = {};
    if (form.nome.trim().length < 2) novos.nome = mensagens.nome;
    if (!Number.isInteger(duracao) || duracao < 1 || duracao > 480) novos.duracao = mensagens.duracao_minutos;
    if (!/^\d+(\.\d{1,2})?$/.test(preco)) novos.preco = mensagens.preco;
    setErros(novos);
    if (Object.keys(novos).length) return;

    setEnviando(true);
    try {
      await salvarServico(dados?.id, { nome: form.nome.trim(), duracao_minutos: duracao, preco });
      fecharModal();
    } catch (erro) {
      const porCampo = errosDosCampos(erro, mensagens);
      setErros({ nome: porCampo.nome, duracao: porCampo.duracao_minutos, preco: porCampo.preco });
      if (erro.codigo !== 'DADOS_INVALIDOS') setErroGeral(erro.message);
      setEnviando(false);
    }
  };

  return (
    <Modal
      titulo={editando ? 'Editar serviço' : 'Novo serviço'}
      descricao="Mudar preço ou duração não altera agendamentos já marcados."
      onFechar={fecharModal}
      rodape={
        <>
          <button type="button" className="btn-ghost" onClick={fecharModal}>
            Cancelar
          </button>
          <button type="submit" form="form-servico" className="btn-primary" disabled={enviando}>
            {enviando ? 'Salvando…' : editando ? 'Salvar alterações' : 'Cadastrar serviço'}
          </button>
        </>
      }
    >
      {erroGeral && <p className="erro-form">{erroGeral}</p>}
      <form id="form-servico" onSubmit={enviar} noValidate>
        <Campo id="se-nome" rotulo="Nome do serviço" erro={erros.nome}>
          <input id="se-nome" type="text" value={form.nome} onChange={mudar('nome')} placeholder="Ex.: Corte + Barba" />
        </Campo>

        <div className="form-linha">
          <Campo id="se-dur" rotulo="Duração (min)" erro={erros.duracao}>
            <input id="se-dur" type="number" min="1" max="480" step="5" value={form.duracao} onChange={mudar('duracao')} />
          </Campo>

          <Campo id="se-preco" rotulo="Preço (R$)" erro={erros.preco}>
            <input id="se-preco" type="text" inputMode="decimal" value={form.preco} onChange={mudar('preco')} placeholder="35,90" />
          </Campo>
        </div>
      </form>
    </Modal>
  );
}
