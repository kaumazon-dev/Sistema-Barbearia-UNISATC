import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { quandoPerderSessao } from '../api/http';
import { authApi } from '../api/auth.api';
import { agendamentosApi } from '../api/agendamentos.api';
import { clientesApi } from '../api/clientes.api';
import { servicosApi } from '../api/servicos.api';
import { produtosApi } from '../api/produtos.api';
import {
  lerSessao,
  salvarSessao,
  limparSessao,
  podeAcessar,
  telaInicial
} from '../store/sessao';

/**
 * Estado da interface: sessao, tela atual, modal aberto e avisos.
 *
 * Os DADOS nao moram aqui: cada tela busca o que precisa na API (useCarregar).
 * As acoes que alteram dados ficam aqui para todas as telas avisarem e
 * recarregarem do mesmo jeito: depois de salvar, `versao` sobe e toda tela
 * aberta busca de novo.
 */

const AppContext = createContext(null);

let proximoAviso = 0;

const telaDoHash = () => window.location.hash.replace(/^#\/?/, '') || '';

export function AppProvider({ children }) {
  const [sessao, setSessao] = useState(lerSessao);
  const [hash, setHash] = useState(telaDoHash);
  const [modal, setModal] = useState(null); // { tipo, dados }
  const [avisos, setAvisos] = useState([]);
  const [versao, setVersao] = useState(0);

  const usuario = sessao?.usuario || null;

  /* ---------------------------------------------------------------- avisos */

  const avisar = useCallback((texto, tom = 'ok') => {
    const id = ++proximoAviso;
    setAvisos((atuais) => [...atuais, { id, texto, tom }]);
    setTimeout(() => setAvisos((atuais) => atuais.filter((a) => a.id !== id)), 4000);
  }, []);

  const fecharAviso = useCallback(
    (id) => setAvisos((atuais) => atuais.filter((a) => a.id !== id)),
    []
  );

  /* ---------------------------------------------------------------- sessao */

  const sair = useCallback(() => {
    limparSessao();
    setSessao(null);
    setModal(null);
    window.location.hash = '';
  }, []);

  useEffect(() => {
    quandoPerderSessao(() => {
      sair();
      avisar('Sua sessão expirou. Entre novamente.', 'alerta');
    });
  }, [sair, avisar]);

  const entrar = useCallback(async (email, senha) => {
    const { token, usuario: logado } = await authApi.login(email, senha);
    salvarSessao(token, logado);
    setSessao({ token, usuario: logado });
    window.location.hash = `/${telaInicial(logado.papel)}`;
  }, []);

  const cadastrar = useCallback(
    async (dados) => {
      await authApi.cadastrar(dados);
      await entrar(dados.email, dados.senha);
    },
    [entrar]
  );

  /* ------------------------------------------------------- navegacao e UI */

  useEffect(() => {
    const aoMudar = () => setHash(telaDoHash());
    window.addEventListener('hashchange', aoMudar);
    return () => window.removeEventListener('hashchange', aoMudar);
  }, []);

  // Guarda de rota: tela que o papel nao acessa cai na tela inicial dele.
  const pagina = usuario && podeAcessar(usuario.papel, hash) ? hash : usuario ? telaInicial(usuario.papel) : null;

  const navegar = useCallback((destino) => {
    window.location.hash = `/${destino}`;
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const abrirModal = useCallback((tipo, dados = null) => setModal({ tipo, dados }), []);
  const fecharModal = useCallback(() => setModal(null), []);

  /* --------------------------------------------------------------- acoes */

  /** Executa, recarrega as telas e avisa. Erro sobe para o formulario tratar. */
  const alterar = useCallback(
    async (executar, mensagem) => {
      const resultado = await executar();
      setVersao((v) => v + 1);
      if (mensagem) avisar(typeof mensagem === 'function' ? mensagem(resultado) : mensagem);
      return resultado;
    },
    [avisar]
  );

  /** Igual a alterar, mas para menus: o erro vira aviso na tela. */
  const tentar = useCallback(
    (executar, mensagem) => alterar(executar, mensagem).catch((erro) => avisar(erro.message, 'alerta')),
    [alterar, avisar]
  );

  const acoes = useMemo(
    () => ({
      // agendamentos
      criarAgendamento: (dados) =>
        alterar(() => agendamentosApi.criar(dados), (a) => `Horário de ${a.cliente.nome} marcado.`),
      remarcarAgendamento: (id, dados) =>
        alterar(() => agendamentosApi.remarcar(id, dados), 'Agendamento remarcado.'),
      concluirAgendamento: (item) =>
        tentar(() => agendamentosApi.concluir(item.id), `Atendimento de ${item.cliente.nome} concluído.`),
      cancelarAgendamento: (item) =>
        tentar(() => agendamentosApi.cancelar(item.id), 'Horário cancelado.'),

      // clientes
      salvarCliente: (id, dados) =>
        id
          ? alterar(() => clientesApi.atualizar(id, dados), 'Cliente atualizado.')
          : alterar(() => clientesApi.criar(dados), (c) => `Cliente ${c.nome} cadastrado.`),
      alternarCliente: (cliente) =>
        cliente.ativo
          ? tentar(() => clientesApi.desativar(cliente.id), `${cliente.nome} desativado.`)
          : tentar(() => clientesApi.atualizar(cliente.id, { ativo: true }), `${cliente.nome} reativado.`),

      // servicos
      salvarServico: (id, dados) =>
        id
          ? alterar(() => servicosApi.atualizar(id, dados), 'Serviço atualizado.')
          : alterar(() => servicosApi.criar(dados), (s) => `Serviço ${s.nome} cadastrado.`),
      alternarServico: (servico) =>
        servico.ativo
          ? tentar(() => servicosApi.desativar(servico.id), 'Serviço desativado.')
          : tentar(() => servicosApi.atualizar(servico.id, { ativo: true }), 'Serviço reativado.'),

      // estoque
      salvarProduto: (id, dados) =>
        id
          ? alterar(() => produtosApi.atualizar(id, dados), 'Produto atualizado.')
          : alterar(() => produtosApi.criar(dados), (p) => `Produto ${p.nome} cadastrado.`),
      alternarProduto: (produto) =>
        produto.ativo
          ? tentar(() => produtosApi.desativar(produto.id), 'Produto desativado.')
          : tentar(() => produtosApi.atualizar(produto.id, { ativo: true }), 'Produto reativado.'),
      movimentarEstoque: (produto, tipo, dados) =>
        alterar(
          () => (tipo === 'entrada' ? produtosApi.entrada(produto.id, dados) : produtosApi.saida(produto.id, dados)),
          tipo === 'entrada' ? `Entrada registrada em ${produto.nome}.` : `Saída registrada em ${produto.nome}.`
        )
    }),
    [alterar, tentar]
  );

  const valor = {
    // sessao
    usuario,
    entrar,
    cadastrar,
    sair,
    // navegacao e UI
    pagina,
    navegar,
    modal,
    abrirModal,
    fecharModal,
    avisos,
    avisar,
    fecharAviso,
    versao,
    // acoes
    ...acoes
  };

  return <AppContext.Provider value={valor}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp precisa estar dentro de <AppProvider>.');
  return ctx;
}
