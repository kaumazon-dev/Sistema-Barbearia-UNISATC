import { useState } from 'react';
import Campo from '../components/Campo';
import { IconScissors } from '../components/Icons';
import { useApp } from '../state/AppStore';
import { errosDosCampos } from '../utils/erros';
import '../components/PageHeader.css';
import './pages.css';
import './Login.css';

const mensagensCadastro = {
  nome: 'Use de 3 a 120 caracteres.',
  email: 'Informe um e-mail válido.',
  senha: 'A senha precisa ter pelo menos 8 caracteres.',
  telefone: 'Até 20 caracteres.'
};

const vazio = { nome: '', email: '', senha: '', telefone: '' };

export default function Login() {
  const { entrar, cadastrar } = useApp();
  const [modo, setModo] = useState('login');
  const [form, setForm] = useState(vazio);
  const [erros, setErros] = useState({});
  const [erroGeral, setErroGeral] = useState('');
  const [enviando, setEnviando] = useState(false);
  const cadastrando = modo === 'cadastro';

  const mudar = (campo) => (e) => {
    setForm((atual) => ({ ...atual, [campo]: e.target.value }));
    setErros((atuais) => ({ ...atuais, [campo]: undefined }));
    setErroGeral('');
  };

  const trocarModo = () => {
    setModo(cadastrando ? 'login' : 'cadastro');
    setErros({});
    setErroGeral('');
  };

  const validar = () => {
    const novos = {};
    if (cadastrando && form.nome.trim().length < 3) novos.nome = mensagensCadastro.nome;
    if (!form.email.includes('@')) novos.email = mensagensCadastro.email;
    if (!form.senha) novos.senha = 'Informe a senha.';
    else if (cadastrando && form.senha.length < 8) novos.senha = mensagensCadastro.senha;
    setErros(novos);
    return Object.keys(novos).length === 0;
  };

  const enviar = async (e) => {
    e.preventDefault();
    if (!validar()) return;
    setEnviando(true);
    try {
      if (cadastrando) {
        await cadastrar({
          nome: form.nome.trim(),
          email: form.email.trim(),
          senha: form.senha,
          ...(form.telefone.trim() ? { telefone: form.telefone.trim() } : {})
        });
      } else {
        await entrar(form.email.trim(), form.senha);
      }
    } catch (erro) {
      setErros(errosDosCampos(erro, mensagensCadastro));
      // CONFLITO = e-mail ja cadastrado; NAO_AUTENTICADO = credenciais erradas.
      if (erro.codigo !== 'DADOS_INVALIDOS') setErroGeral(erro.message);
      setEnviando(false);
    }
  };

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

        <h1 className="login__titulo">{cadastrando ? 'Criar conta' : 'Entrar'}</h1>
        <p className="login__sub">
          {cadastrando
            ? 'Cadastre-se para marcar seus horários.'
            : 'Acesse a agenda e a gestão da barbearia.'}
        </p>

        <form onSubmit={enviar} noValidate>
          {cadastrando && (
            <Campo id="lg-nome" rotulo="Nome completo" erro={erros.nome}>
              <input id="lg-nome" type="text" value={form.nome} onChange={mudar('nome')} autoComplete="name" />
            </Campo>
          )}

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

          <Campo id="lg-senha" rotulo="Senha" erro={erros.senha}>
            <input
              id="lg-senha"
              type="password"
              value={form.senha}
              onChange={mudar('senha')}
              autoComplete={cadastrando ? 'new-password' : 'current-password'}
            />
          </Campo>

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

          <button type="submit" className="btn-primary login__botao" disabled={enviando}>
            {enviando ? 'Aguarde…' : cadastrando ? 'Criar conta' : 'Entrar'}
          </button>
        </form>

        <p className="login__troca">
          {cadastrando ? 'Já tem conta?' : 'Ainda não tem conta?'}{' '}
          <button type="button" className="link-acao" onClick={trocarModo}>
            {cadastrando ? 'Entrar' : 'Cadastre-se'}
          </button>
        </p>
      </section>
    </div>
  );
}
