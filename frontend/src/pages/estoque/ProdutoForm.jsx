import { useState } from 'react';
import Campo from '../../js/components/Campo';
import Modal from '../../js/components/Modal';
import { useApp } from '../../js/store/AppStore';
import { errosDosCampos } from '../../js/utils/erros';

const mensagens = {
  nome: 'Use de 2 a 120 caracteres.',
  unidade: 'Escolha un, ml ou g.',
  estoque_minimo: 'Valor de 0 a 99.999.999,99, com até 2 casas.'
};

const unidades = [
  { valor: 'un', rotulo: 'Unidade (un)' },
  { valor: 'ml', rotulo: 'Mililitro (ml)' },
  { valor: 'g', rotulo: 'Grama (g)' }
];

export default function ProdutoForm({ dados }) {
  const { salvarProduto, fecharModal } = useApp();
  const editando = Boolean(dados?.id);
  const [form, setForm] = useState({
    nome: dados?.nome || '',
    unidade: dados?.unidade || 'un',
    minimo: dados?.estoque_minimo ?? '0'
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
    const minimo = String(form.minimo).trim().replace(',', '.');
    const novos = {};
    if (form.nome.trim().length < 2) novos.nome = mensagens.nome;
    if (!/^\d+(\.\d{1,2})?$/.test(minimo)) novos.minimo = mensagens.estoque_minimo;
    setErros(novos);
    if (Object.keys(novos).length) return;

    setEnviando(true);
    try {
      // quantidade_atual nunca vai no corpo: so muda por movimentacao (RN04).
      await salvarProduto(dados?.id, { nome: form.nome.trim(), unidade: form.unidade, estoque_minimo: minimo });
      fecharModal();
    } catch (erro) {
      const porCampo = errosDosCampos(erro, mensagens);
      setErros({ nome: porCampo.nome, unidade: porCampo.unidade, minimo: porCampo.estoque_minimo });
      if (erro.codigo !== 'DADOS_INVALIDOS') setErroGeral(erro.message);
      setEnviando(false);
    }
  };

  return (
    <Modal
      titulo={editando ? 'Editar produto' : 'Novo produto'}
      descricao={editando ? 'Para mudar a quantidade, registre uma entrada ou saída.' : 'O produto nasce com quantidade 0. O estoque inicial entra por uma entrada.'}
      onFechar={fecharModal}
      rodape={
        <>
          <button type="button" className="btn-ghost" onClick={fecharModal}>
            Cancelar
          </button>
          <button type="submit" form="form-produto" className="btn-primary" disabled={enviando}>
            {enviando ? 'Salvando…' : editando ? 'Salvar alterações' : 'Cadastrar produto'}
          </button>
        </>
      }
    >
      {erroGeral && <p className="erro-form">{erroGeral}</p>}
      <form id="form-produto" onSubmit={enviar} noValidate>
        <Campo id="pr-nome" rotulo="Nome" erro={erros.nome}>
          <input id="pr-nome" type="text" value={form.nome} onChange={mudar('nome')} placeholder="Ex.: Pomada modeladora" />
        </Campo>
        <div className="form-linha">
          <Campo id="pr-unidade" rotulo="Unidade" erro={erros.unidade}>
            <select id="pr-unidade" value={form.unidade} onChange={mudar('unidade')}>
              {unidades.map((u) => (
                <option key={u.valor} value={u.valor}>
                  {u.rotulo}
                </option>
              ))}
            </select>
          </Campo>
          <Campo id="pr-minimo" rotulo="Estoque mínimo" erro={erros.minimo} dica="Abaixo ou igual a isto, o produto entra em falta.">
            <input id="pr-minimo" type="text" inputMode="decimal" value={form.minimo} onChange={mudar('minimo')} />
          </Campo>
        </div>
      </form>
    </Modal>
  );
}
