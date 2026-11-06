import { useState } from 'react';
import Campo from '../../js/components/Campo';
import Modal from '../../js/components/Modal';
import { useApp } from '../../js/store/AppStore';
import { errosDosCampos } from '../../js/utils/erros';
import { formatarQuantidade } from '../../js/utils/formato';

const mensagens = {
  quantidade: 'Quantidade maior que 0, com até 2 casas.',
  motivo: 'Até 160 caracteres.'
};

/** dados: o produto, com tipo 'entrada' ou 'saida'. */
export default function MovimentacaoForm({ dados }) {
  const { movimentarEstoque, fecharModal } = useApp();
  const entrada = dados.tipo === 'entrada';
  const [form, setForm] = useState({ quantidade: '', motivo: '' });
  const [erros, setErros] = useState({});
  const [erroGeral, setErroGeral] = useState('');
  const [enviando, setEnviando] = useState(false);

  const mudar = (campo) => (e) => {
    setForm((atual) => ({ ...atual, [campo]: e.target.value }));
    setErros((atuais) => ({ ...atuais, [campo]: undefined }));
    setErroGeral('');
  };

  const enviar = async (e) => {
    e.preventDefault();
    const quantidade = form.quantidade.trim().replace(',', '.');
    if (!/^\d+(\.\d{1,2})?$/.test(quantidade) || Number(quantidade) <= 0) {
      setErros({ quantidade: mensagens.quantidade });
      return;
    }
    setEnviando(true);
    try {
      await movimentarEstoque(dados, dados.tipo, {
        quantidade,
        ...(form.motivo.trim() ? { motivo: form.motivo.trim() } : {})
      });
      fecharModal();
    } catch (erro) {
      setErros(errosDosCampos(erro, mensagens));
      // REGRA_VIOLADA: saida maior que o disponivel (RF26), com mensagem pronta.
      if (erro.codigo !== 'DADOS_INVALIDOS') setErroGeral(erro.message);
      setEnviando(false);
    }
  };

  return (
    <Modal
      titulo={entrada ? `Entrada · ${dados.nome}` : `Saída · ${dados.nome}`}
      descricao={`Disponível agora: ${formatarQuantidade(dados.quantidade_atual)} ${dados.unidade}`}
      largura={440}
      onFechar={fecharModal}
      rodape={
        <>
          <button type="button" className="btn-ghost" onClick={fecharModal}>
            Cancelar
          </button>
          <button type="submit" form="form-movimentacao" className="btn-primary" disabled={enviando}>
            {enviando ? 'Salvando…' : entrada ? 'Registrar entrada' : 'Registrar saída'}
          </button>
        </>
      }
    >
      {erroGeral && (
        <p className="erro-form" role="alert">
          {erroGeral}
        </p>
      )}
      <form id="form-movimentacao" onSubmit={enviar} noValidate>
        <Campo id="mv-qtd" rotulo={`Quantidade (${dados.unidade})`} erro={erros.quantidade}>
          <input id="mv-qtd" type="text" inputMode="decimal" value={form.quantidade} onChange={mudar('quantidade')} />
        </Campo>
        <Campo id="mv-motivo" rotulo="Motivo" erro={erros.motivo} dica="Opcional. Ex.: compra do fornecedor, uso no atendimento.">
          <input id="mv-motivo" type="text" maxLength={160} value={form.motivo} onChange={mudar('motivo')} />
        </Campo>
      </form>
    </Modal>
  );
}
