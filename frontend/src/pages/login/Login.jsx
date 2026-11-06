import { useState } from 'react';
import Campo from '../../js/components/Campo';
import { IconScissors } from '../../js/components/Icons';
import { authApi } from '../../js/api/auth.api';
import { useApp } from '../../js/store/AppStore';
import { errosDosCampos } from '../../js/utils/erros';
import '../../assets/css/components/PageHeader.css';
import '../../assets/css/pages/pages.css';
import '../../assets/css/pages/login.css';

const mensagensCadastro = {
  nome: 'Use de 3 a 120 caracteres.',
  email: 'Informe um e-mail válido.',
  senha: 'A senha precisa ter pelo menos 8 caracteres.',
  telefone: 'Até 20 caracteres.'
};

const vazio = { nome: '', email: '', senha: '', confirmacao: '', telefone: '' };

// Textos de cada modo da tela. Um objeto so evita um ternario por linha no JSX.
const textos = {
  login: { titulo: 'Entrar', sub: 'Acesse a agenda e a gestão da barbearia.', botao: 'Entrar' },
  cadastro: { titulo: 'Criar conta', sub: 'Cadastre-se para marcar seus horários.', botao: 'Criar conta' },
  esqueci: {
    titulo: 'Esqueci minha senha',
    sub: 'Informe seu e-mail e enviaremos um link para criar uma senha nova.',
    botao: 'Enviar link'
  },
  redefinir: { titulo: 'Nova senha', sub: 'Escolha uma senha nova para a sua conta.', botao: 'Salvar senha' }
};

/** O link do e-mail chega como ?redefinir=<token>. */
function lerTokenDaUrl() {
  return new URLSearchParams(window.location.search).get('redefinir');
}

/** Tira o token da barra de endereco: ele nao deve ficar no historico. */
function limparTokenDaUrl() {
  const url = new URL(window.location.href);
  url.searchParams.delete('redefinir');
  window.history.replaceState(null, '', url.pathname + url.search + url.hash);
}

export default function Login() {
  const { entrar, cadastrar } = useApp();
  const [token] = useState(lerTokenDaUrl);
  const [modo, setModo] = useState(token ? 'redefinir' : 'login');
  const [form, setForm] = useState(vazio);
  const [erros, setErros] = useState({});
  const [erroGeral, setErroGeral] = useState('');
  const [sucesso, setSucesso] = useState('');
  const [enviando, setEnviando] = useState(false);

  const cadastrando = modo === 'cadastro';
  const pedeEmail = modo !== 'redefinir';
  const pedeSenha = modo !== 'esqueci';
  const senhaNova = cadastrando || modo === 'redefinir';

  const mudar = (campo) => (e) => {
    setForm((atual) => ({ ...atual, [campo]: e.target.value }));
    setErros((atuais) => ({ ...atuais, [campo]: undefined }));
    setErroGeral('');
  };

  const irPara = (novoModo) => {
    if (modo === 'redefinir') limparTokenDaUrl();
    setModo(novoModo);
    setForm((atual) => ({ ...vazio, email: atual.email }));
    setErros({});
    setErroGeral('');
    setSucesso('');
  };

  const validar = () => {
    const novos = {};
    if (cadastrando && form.nome.trim().length < 3) novos.nome = mensagensCadastro.nome;
    if (pedeEmail && !form.email.includes('@')) novos.email = mensagensCadastro.email;
    if (pedeSenha) {
      if (!form.senha) novos.senha = 'Informe a senha.';
      else if (senhaNova && form.senha.length < 8) novos.senha = mensagensCadastro.senha;
    }
    if (modo === 'redefinir' && form.confirmacao !== form.senha) {
      novos.confirmacao = 'As senhas não conferem.';
    }
    setErros(novos);
    return Object.keys(novos).length === 0;
  };

  const executar = async () => {
    if (modo === 'cadastro') {
      await cadastrar({
        nome: form.nome.trim(),
        email: form.email.trim(),
        senha: form.senha,
        ...(form.telefone.trim() ? { telefone: form.telefone.trim() } : {})
      });
    } else if (modo === 'login') {
      await entrar(form.email.trim(), form.senha);
    } else if (modo === 'esqueci') {
      const { mensagem } = await authApi.esqueciSenha(form.email.trim());
      setSucesso(mensagem);
    } else {
      const { mensagem } = await authApi.redefinirSenha(token, form.senha);
      limparTokenDaUrl();
      setModo('login');
      setForm(vazio);
      setSucesso(mensagem);
    }
  };

  const enviar = async (e) => {
    e.preventDefault();
    if (!validar()) return;
    setEnviando(true);
    setSucesso('');
    try {
      await executar();
    } catch (erro) {
      const doCampo = errosDosCampos(erro, mensagensCadastro);
      setErros(doCampo);
      // CONFLITO = e-mail ja cadastrado; NAO_AUTENTICADO = credenciais erradas;
      // REGRA_VIOLADA = link de redefinicao invalido ou expirado.
      if (erro.codigo !== 'DADOS_INVALIDOS') setErroGeral(erro.message);
      // O token nao tem campo na tela: link cortado vira mensagem geral.
      else if (doCampo.token) setErroGeral('Link de redefinição inválido. Solicite um novo.');
    }
    // Login e cadastro que deram certo desmontam esta tela; nos outros modos
    // ela continua aberta e o botao precisa voltar.
    setEnviando(false);
  };

  const texto = textos[modo];

  return (
    <div className="login">
      <section className="login__caixa card">
        <div className="login__marca">
          <span className="login__logo">
            <IconScissors size={20} />
          </span>
          <div>
            <strong>NextBarber</strong>
            <small>PREMIUM HUB</small>
          </div>
        </div>

        <h1 className="login__titulo">{texto.titulo}</h1>
        <p className="login__sub">{texto.sub}</p>

        <form onSubmit={enviar} noValidate>
          {cadastrando && (
            <Campo id="lg-nome" rotulo="Nome completo" erro={erros.nome}>
              <input id="lg-nome" type="text" value={form.nome} onChange={mudar('nome')} autoComplete="name" />
            </Campo>
          )}

          {pedeEmail && (
            <Campo id="lg-email" rotulo="E-mail" erro={erros.email}>
              <input
                id="lg-email"
                type="email"
                value={form.email}
                onChange={mudar('email')}
                autoComplete="email"
                placeholder="voce@exemplo.com"
              />
            </Campo>
          )}

          {pedeSenha && (
            <Campo id="lg-senha" rotulo={modo === 'redefinir' ? 'Nova senha' : 'Senha'} erro={erros.senha}>
              <input
                id="lg-senha"
                type="password"
                value={form.senha}
                onChange={mudar('senha')}
                autoComplete={senhaNova ? 'new-password' : 'current-password'}
              />
            </Campo>
          )}

          {modo === 'login' && (
            <button type="button" className="link-acao login__esqueci" onClick={() => irPara('esqueci')}>
              Esqueci minha senha
            </button>
          )}

          {modo === 'redefinir' && (
            <Campo id="lg-confirmacao" rotulo="Confirme a nova senha" erro={erros.confirmacao}>
              <input
                id="lg-confirmacao"
                type="password"
                value={form.confirmacao}
                onChange={mudar('confirmacao')}
                autoComplete="new-password"
              />
            </Campo>
          )}

          {cadastrando && (
            <Campo id="lg-tel" rotulo="Telefone" erro={erros.telefone} dica="Opcional.">
              <input id="lg-tel" type="tel" value={form.telefone} onChange={mudar('telefone')} autoComplete="tel" />
            </Campo>
          )}

          {erroGeral && (
            <p className="login__erro" role="alert">
              {erroGeral}
            </p>
          )}

          {sucesso && (
            <p className="login__ok" role="status">
              {sucesso}
            </p>
          )}

          <button type="submit" className="btn-primary login__botao" disabled={enviando}>
            {enviando ? 'Aguarde…' : texto.botao}
          </button>
        </form>

        <p className="login__troca">
          {modo === 'login' && (
            <>
              Ainda não tem conta?{' '}
              <button type="button" className="link-acao" onClick={() => irPara('cadastro')}>
                Cadastre-se
              </button>
            </>
          )}
          {modo === 'cadastro' && (
            <>
              Já tem conta?{' '}
              <button type="button" className="link-acao" onClick={() => irPara('login')}>
                Entrar
              </button>
            </>
          )}
          {(modo === 'esqueci' || modo === 'redefinir') && (
            <button type="button" className="link-acao" onClick={() => irPara('login')}>
              Voltar para o login
            </button>
          )}
        </p>
      </section>
    </div>
  );
}
