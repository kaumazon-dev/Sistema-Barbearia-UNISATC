import { useEffect, useMemo, useRef, useState } from 'react';
import { IconSearch, IconBell } from './Icons';
import { unidade, notificacoes } from '../data/mock';
import { useApp } from '../state/AppStore';
import { formatarBRL } from '../utils/formato';
import './Topbar.css';

export default function Topbar() {
  const {
    agendamentos,
    clientes,
    servicos,
    navegar,
    abrirModal,
    notificacoesLidas,
    marcarNotificacoesLidas
  } = useApp();

  const [busca, setBusca] = useState('');
  const [sinoAberto, setSinoAberto] = useState(false);
  const areaBusca = useRef(null);
  const areaSino = useRef(null);

  /* Busca global: agenda + clientes + servicos. */
  const resultados = useMemo(() => {
    const t = busca.trim().toLowerCase();
    if (t.length < 2) return null;

    const bate = (valor) => String(valor).toLowerCase().includes(t);

    return {
      agendamentos: agendamentos
        .filter((a) => bate(a.cliente) || bate(a.barbeiro) || bate(a.servico) || bate(a.horario))
        .slice(0, 4),
      clientes: clientes.filter((c) => bate(c.nome) || bate(c.telefone)).slice(0, 4),
      servicos: servicos.filter((s) => bate(s.nome) || bate(s.categoria)).slice(0, 3)
    };
  }, [busca, agendamentos, clientes, servicos]);

  const totalResultados = resultados
    ? resultados.agendamentos.length + resultados.clientes.length + resultados.servicos.length
    : 0;

  /* Fecha os dois popovers ao clicar fora ou apertar ESC. */
  useEffect(() => {
    const aoClicarFora = (e) => {
      if (!areaBusca.current?.contains(e.target)) setBusca('');
      if (!areaSino.current?.contains(e.target)) setSinoAberto(false);
    };
    const aoTeclar = (e) => {
      if (e.key !== 'Escape') return;
      setBusca('');
      setSinoAberto(false);
    };
    document.addEventListener('mousedown', aoClicarFora);
    document.addEventListener('keydown', aoTeclar);
    return () => {
      document.removeEventListener('mousedown', aoClicarFora);
      document.removeEventListener('keydown', aoTeclar);
    };
  }, []);

  const irPara = (destino) => {
    setBusca('');
    navegar(destino);
  };

  return (
    <header className="topbar">
      <div className="topbar__busca-area" ref={areaBusca}>
        <label className="topbar__search">
          <IconSearch size={17} />
          <input
            type="text"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder="Buscar agendamentos, clientes ou faturamento..."
            aria-label="Buscar"
          />
        </label>

        {resultados && (
          <div className="busca-resultados" role="listbox">
            {totalResultados === 0 && <p className="busca-vazio">Nada encontrado para “{busca}”.</p>}

            {resultados.agendamentos.length > 0 && (
              <section>
                <h4>Agendamentos</h4>
                {resultados.agendamentos.map((a) => (
                  <button key={a.id} type="button" onClick={() => irPara('agendamentos')}>
                    <strong>
                      {a.horario} · {a.cliente}
                    </strong>
                    <small>
                      {a.servico} · {a.barbeiro}
                    </small>
                  </button>
                ))}
              </section>
            )}

            {resultados.clientes.length > 0 && (
              <section>
                <h4>Clientes</h4>
                {resultados.clientes.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => {
                      setBusca('');
                      abrirModal('clienteDetalhe', c);
                    }}
                  >
                    <strong>{c.nome}</strong>
                    <small>
                      {c.telefone} · {c.visitas} visitas
                    </small>
                  </button>
                ))}
              </section>
            )}

            {resultados.servicos.length > 0 && (
              <section>
                <h4>Serviços</h4>
                {resultados.servicos.map((s) => (
                  <button key={s.id} type="button" onClick={() => irPara('servicos')}>
                    <strong>{s.nome}</strong>
                    <small>
                      {s.duracao} min · {formatarBRL(s.preco)}
                    </small>
                  </button>
                ))}
              </section>
            )}
          </div>
        )}
      </div>

      <div className="topbar__right">
        <span className="topbar__unidade dot-label">
          {unidade.nome} {unidade.aberta ? 'Aberta' : 'Fechada'}
        </span>

        <div className="topbar__sino-area" ref={areaSino}>
          <button
            type="button"
            className="topbar__bell"
            aria-label="Notificações"
            aria-expanded={sinoAberto}
            onClick={() => {
              setSinoAberto((v) => !v);
              marcarNotificacoesLidas();
            }}
          >
            <IconBell size={18} />
            {!notificacoesLidas && <span className="topbar__bell-dot" />}
          </button>

          {sinoAberto && (
            <div className="notificacoes">
              <header>
                <strong>Notificações</strong>
                <span>{notificacoes.length} recentes</span>
              </header>
              <ul>
                {notificacoes.map((n) => (
                  <li key={n.id}>
                    <strong>{n.titulo}</strong>
                    <p>{n.texto}</p>
                    <small>{n.quando}</small>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="topbar__data">
          <strong>{unidade.dataExtenso}</strong>
          <small>Expediente: {unidade.expediente}</small>
        </div>
      </div>
    </header>
  );
}
