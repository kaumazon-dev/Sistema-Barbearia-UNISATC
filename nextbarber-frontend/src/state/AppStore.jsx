import { createContext, useCallback, useContext, useMemo, useState } from 'react';
import * as base from '../data/mock';
import { STATUS } from '../data/mock';
import { horarioEmMinutos, iniciaisDe } from '../utils/formato';

/**
 * Estado da aplicacao inteira — em memoria.
 *
 * Nao existe backend nem persistencia: recarregar a pagina (F5) devolve
 * os dados originais de src/data/mock.js. E de proposito, para a
 * apresentacao sempre comecar do mesmo ponto.
 */

const AppContext = createContext(null);

let proximoId = 1000;
const novoId = () => ++proximoId;

export function AppProvider({ children }) {
  const [agendamentos, setAgendamentos] = useState(base.agendamentos);
  const [clientes, setClientes] = useState(base.clientes);
  const [barbeiros, setBarbeiros] = useState(base.barbeiros);
  const [servicos, setServicos] = useState(base.servicos);

  const [pagina, setPagina] = useState('dashboard');
  const [modal, setModal] = useState(null); // { tipo, dados }
  const [avisos, setAvisos] = useState([]); // toasts
  const [notificacoesLidas, setNotificacoesLidas] = useState(false);

  /* ---------------------------------------------------------------- avisos */

  const avisar = useCallback((texto, tom = 'ok') => {
    const id = novoId();
    setAvisos((atuais) => [...atuais, { id, texto, tom }]);
    setTimeout(() => setAvisos((atuais) => atuais.filter((a) => a.id !== id)), 3200);
  }, []);

  const fecharAviso = useCallback(
    (id) => setAvisos((atuais) => atuais.filter((a) => a.id !== id)),
    []
  );

  /* ---------------------------------------------------------- navegacao/UI */

  const navegar = useCallback((destino) => {
    setPagina(destino);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const abrirModal = useCallback((tipo, dados = null) => setModal({ tipo, dados }), []);
  const fecharModal = useCallback(() => setModal(null), []);

  /* ------------------------------------------------------------ agendamentos */

  const salvarAgendamento = useCallback(
    (dados) => {
      const ordenar = (lista) =>
        [...lista].sort((a, b) => horarioEmMinutos(a.horario) - horarioEmMinutos(b.horario));

      // o formulario envia clienteId; o aviso precisa do nome
      const nomeCliente =
        clientes.find((c) => c.id === Number(dados.clienteId))?.nome || 'cliente';

      if (dados.id) {
        setAgendamentos((lista) =>
          ordenar(lista.map((a) => (a.id === dados.id ? { ...a, ...dados } : a)))
        );
        avisar(`Agendamento de ${nomeCliente} atualizado.`);
      } else {
        setAgendamentos((lista) => ordenar([...lista, { ...dados, id: novoId() }]));
        avisar(`Agendamento de ${nomeCliente} criado para ${dados.horario}.`);
      }
    },
    [avisar, clientes]
  );

  const mudarStatus = useCallback(
    (id, status) => {
      setAgendamentos((lista) => lista.map((a) => (a.id === id ? { ...a, status } : a)));
      avisar(`Status alterado para "${status}".`);
    },
    [avisar]
  );

  const removerAgendamento = useCallback(
    (id) => {
      setAgendamentos((lista) => lista.filter((a) => a.id !== id));
      avisar('Agendamento excluído.', 'alerta');
    },
    [avisar]
  );

  /* ----------------------------------------------------------------- clientes */

  const salvarCliente = useCallback(
    (dados) => {
      const comIniciais = { ...dados, iniciais: iniciaisDe(dados.nome) };
      if (dados.id) {
        setClientes((lista) => lista.map((c) => (c.id === dados.id ? { ...c, ...comIniciais } : c)));
        avisar('Cliente atualizado.');
      } else {
        setClientes((lista) => [
          { ...comIniciais, id: novoId(), visitas: 0, ultimaVisita: '—' },
          ...lista
        ]);
        avisar(`Cliente ${dados.nome} cadastrado.`);
      }
    },
    [avisar]
  );

  const removerCliente = useCallback(
    (id) => {
      setClientes((lista) => lista.filter((c) => c.id !== id));
      avisar('Cliente removido.', 'alerta');
    },
    [avisar]
  );

  /* ---------------------------------------------------------------- barbeiros */

  const salvarBarbeiro = useCallback(
    (dados) => {
      const comIniciais = { ...dados, iniciais: iniciaisDe(dados.nome || dados.apelido) };
      if (dados.id) {
        setBarbeiros((lista) => lista.map((b) => (b.id === dados.id ? { ...b, ...comIniciais } : b)));
        avisar('Barbeiro atualizado.');
      } else {
        setBarbeiros((lista) => [...lista, { ...comIniciais, id: novoId(), avaliacao: 0 }]);
        avisar(`Barbeiro ${dados.apelido} cadastrado.`);
      }
    },
    [avisar]
  );

  const mudarSituacaoBarbeiro = useCallback(
    (id, situacao) => {
      setBarbeiros((lista) => lista.map((b) => (b.id === id ? { ...b, situacao } : b)));
      avisar(`Situação alterada para "${situacao}".`);
    },
    [avisar]
  );

  /* ----------------------------------------------------------------- servicos */

  const salvarServico = useCallback(
    (dados) => {
      if (dados.id) {
        setServicos((lista) => lista.map((s) => (s.id === dados.id ? { ...s, ...dados } : s)));
        avisar('Serviço atualizado.');
      } else {
        setServicos((lista) => [...lista, { ...dados, id: novoId(), realizados: 0 }]);
        avisar(`Serviço ${dados.nome} cadastrado.`);
      }
    },
    [avisar]
  );

  const alternarServico = useCallback(
    (id) => {
      let ativo = false;
      setServicos((lista) =>
        lista.map((s) => {
          if (s.id !== id) return s;
          ativo = !s.ativo;
          return { ...s, ativo };
        })
      );
      avisar(ativo ? 'Serviço reativado.' : 'Serviço desativado.');
    },
    [avisar]
  );

  /* -------------------------------------------------------------- derivados */

  /**
   * A agenda guarda ids (clienteId/barbeiroId/servicoId), como seria com o
   * banco. Aqui os ids viram os nomes que as telas exibem, para nenhum
   * componente precisar fazer lookup.
   */
  const agenda = useMemo(() => {
    const porId = (lista) => new Map(lista.map((item) => [item.id, item]));
    const mapaClientes = porId(clientes);
    const mapaBarbeiros = porId(barbeiros);
    const mapaServicos = porId(servicos);

    return agendamentos
      .map((a) => ({
        ...a,
        cliente: mapaClientes.get(a.clienteId)?.nome || 'Cliente removido',
        barbeiro:
          mapaBarbeiros.get(a.barbeiroId)?.nomeAgenda ||
          mapaBarbeiros.get(a.barbeiroId)?.apelido ||
          'Sem barbeiro',
        servico: mapaServicos.get(a.servicoId)?.nome || 'Serviço removido'
      }))
      .sort((a, b) => horarioEmMinutos(a.horario) - horarioEmMinutos(b.horario));
  }, [agendamentos, clientes, barbeiros, servicos]);

  const indicadores = useMemo(() => {
    const ativos = agendamentos.filter((a) => a.status !== STATUS.CANCELADO);
    const concluidos = agendamentos.filter((a) => a.status === STATUS.CONCLUIDO);
    const emFila = agendamentos.filter(
      (a) => a.status === STATUS.AGUARDANDO || a.status === STATUS.CONFIRMADO
    );

    const { baseDoDia, capacidadeDiaria, metaDiaria } = base.unidade;

    // base do dia + o que esta na tabela agora
    const totalAtivos = baseDoDia.agendamentos + ativos.length;
    const atendidos = baseDoDia.atendidos + concluidos.length;
    const faturado =
      baseDoDia.faturamento + concluidos.reduce((soma, a) => soma + Number(a.valor || 0), 0);
    const ticket = atendidos ? faturado / atendidos : 0;

    const barbeirosAtivos = barbeiros.filter((b) => b.situacao !== 'Intervalo').length;

    return {
      totalAtivos,
      emFila: emFila.length,
      faturado,
      metaDiaria,
      percentualMeta: Math.round((faturado / metaDiaria) * 100),
      atendidos,
      ticket,
      ocupacao: Math.min(100, Math.round((totalAtivos / capacidadeDiaria) * 100)),
      barbeirosAtivos,
      totalBarbeiros: barbeiros.length,
      percentualEscala: Math.round((barbeirosAtivos / Math.max(1, barbeiros.length)) * 100)
    };
  }, [agendamentos, barbeiros]);

  /** Quem cada barbeiro atende agora sai da propria agenda. */
  const equipe = useMemo(
    () =>
      barbeiros.map((b) => {
        const atual = agenda.find(
          (a) => a.barbeiroId === b.id && a.status === STATUS.EM_ATENDIMENTO
        );
        return {
          ...b,
          atendendo: atual?.cliente || null,
          atendimentosHoje: agenda.filter(
            (a) => a.barbeiroId === b.id && a.status !== STATUS.CANCELADO
          ).length
        };
      }),
    [barbeiros, agenda]
  );

  const valor = {
    // dados
    agendamentos: agenda,
    agendamentosBrutos: agendamentos,
    clientes,
    barbeiros: equipe,
    servicos,
    indicadores,
    // navegacao e UI
    pagina,
    navegar,
    modal,
    abrirModal,
    fecharModal,
    avisos,
    avisar,
    fecharAviso,
    notificacoesLidas,
    marcarNotificacoesLidas: () => setNotificacoesLidas(true),
    // acoes
    salvarAgendamento,
    mudarStatus,
    removerAgendamento,
    salvarCliente,
    removerCliente,
    salvarBarbeiro,
    mudarSituacaoBarbeiro,
    salvarServico,
    alternarServico
  };

  return <AppContext.Provider value={valor}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp precisa estar dentro de <AppProvider>.');
  return ctx;
}
