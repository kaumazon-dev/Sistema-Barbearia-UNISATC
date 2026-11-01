import { useState } from 'react';
import Campo from '../components/Campo';
import Modal from '../components/Modal';
import { useApp } from '../state/AppStore';
import { errosDosCampos } from '../utils/erros';

const mensagens = {
  nome: 'Use de 3 a 120 caracteres.',
  email: 'Informe um e-mail válido.',
  senha: 'A senha precisa ter de 8 caracteres a 72 bytes.',
  telefone: 'Até 20 caracteres.'
};

export default function ClienteForm({ dados }) {
  const { salvarCliente, fecharModal } = useApp();
  const editando = Boolean(dados?.id);
  const [form, setForm] = useState({
    nome: dados?.nome || '',
    email: dados?.email || '',
    telefone: dados?.telefone || '',
    senha: ''
  });
  const [erros, setErros] = useState({});
  const [erroGeral, setErroGeral] = useState('');
  const [enviando, setEnviando] = useState(false);

  const mudar = (campo) => (e) => {
    setForm((atual) => ({ ...atual, [campo]: e.target.value }));
    setErros((atuais) => ({ ...atuais, [campo]: undefined }));
    setErroGeral('');
  };

  const validar = () => {
    const novos = {};
    if (form.nome.trim().length < 3) novos.nome = mensagens.nome;
    if (!form.email.includes('@')) novos.email = mensagens.email;
    if (!editando && form.senha.length < 8) novos.senha = mensagens.senha;
    setErros(novos);
    return Object.keys(novos).length === 0;
  };

  const enviar = async (e) => {
    e.preventDefault();
    if (!validar()) return;
    setEnviando(true);

    const corpo = { nome: form.nome.trim(), email: form.email.trim() };
    if (editando) {
      // PUT aceita null para apagar o telefone; senha nao e alterada por aqui.
      corpo.telefone = form.telefone.trim() || null;
    } else {
      corpo.senha = form.senha;
      if (form.telefone.trim()) corpo.telefone = form.telefone.trim();
    }

    try {
      await salvarCliente(dados?.id, corpo);
      fecharModal();
    } catch (erro) {
      setErros(errosDosCampos(erro, mensagens));
      if (erro.codigo !== 'DADOS_INVALIDOS') setErroGeral(erro.message);
      setEnviando(false);
    }
  };

  return (
    <Modal
      titulo={editando ? 'Editar cliente' : 'Novo cliente'}
      descricao={editando ? 'A senha só pode ser trocada pelo próprio cliente.' : 'O cliente usa este e-mail e senha para entrar e marcar horários.'}
      onFechar={fecharModal}
      rodape={
        <>
          <button type="button" className="btn-ghost" onClick={fecharModal}>
            Cancelar
          </button>
          <button type="submit" form="form-cliente" className="btn-primary" disabled={enviando}>
            {enviando ? 'Salvando…' : editando ? 'Salvar alterações' : 'Cadastrar cliente'}
          </button>
        </>
      }
    >
      {erroGeral && (
        <p className="erro-form" role="alert">
          {erroGeral}
        </p>
      )}
      <form id="form-cliente" onSubmit={enviar} noValidate>
        <Campo id="cl-nome" rotulo="Nome completo" erro={erros.nome}>
          <input id="cl-nome" type="text" value={form.nome} onChange={mudar('nome')} placeholder="Ex.: João Pedro Ramos" />
        </Campo>

        <div className="form-linha">
          <Campo id="cl-email" rotulo="E-mail" erro={erros.email}>
            <input id="cl-email" type="email" value={form.email} onChange={mudar('email')} />
          </Campo>

          <Campo id="cl-tel" rotulo="Telefone" erro={erros.telefone} dica="Opcional.">
            <input id="cl-tel" type="tel" value={form.telefone} onChange={mudar('telefone')} placeholder="48999990000" />
          </Campo>
        </div>

        {!editando && (
          <Campo id="cl-senha" rotulo="Senha inicial" erro={erros.senha} dica="Mínimo de 8 caracteres.">
            <input id="cl-senha" type="password" value={form.senha} onChange={mudar('senha')} autoComplete="new-password" />
          </Campo>
        )}
      </form>
    </Modal>
  );
}
