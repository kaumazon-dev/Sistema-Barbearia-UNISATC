import { useState } from 'react';
import PageHeader from '../components/PageHeader';
import { unidade, usuario } from '../data/mock';
import { useApp } from '../state/AppStore';
import './pages.css';

const preferenciasIniciais = [
  {
    id: 'sms',
    titulo: 'Lembrete por SMS',
    descricao: 'Enviar aviso 2 horas antes do horário marcado.',
    ligado: true
  },
  {
    id: 'encaixe',
    titulo: 'Permitir encaixe',
    descricao: 'Aceitar agendamento fora da grade quando houver vaga.',
    ligado: true
  },
  {
    id: 'bloqueio',
    titulo: 'Bloquear horário vencido',
    descricao: 'Impedir marcação em horários que já passaram.',
    ligado: true
  },
  {
    id: 'comissao',
    titulo: 'Fechamento automático de comissão',
    descricao: 'Consolidar comissões todo dia 30, às 23h.',
    ligado: false
  }
];

export default function Configuracoes() {
  const { avisar } = useApp();
  const [preferencias, setPreferencias] = useState(preferenciasIniciais);

  const alternar = (id) => {
    const alvo = preferencias.find((p) => p.id === id);
    setPreferencias((atual) =>
      atual.map((p) => (p.id === id ? { ...p, ligado: !p.ligado } : p))
    );
    avisar(`${alvo.titulo}: ${alvo.ligado ? 'desligado' : 'ligado'}.`);
  };

  return (
    <div className="page">
      <PageHeader
        titulo="Configurações"
        subtitulo="Dados da unidade e preferências de operação."
      />

      <div className="settings-grid">
        <section className="card card-pad">
          <h3>Dados da unidade</h3>

          <div className="field">
            <label htmlFor="cfg-nome">Nome da unidade</label>
            <input id="cfg-nome" type="text" defaultValue={unidade.nome} />
          </div>

          <div className="field">
            <label htmlFor="cfg-exp">Expediente</label>
            <input id="cfg-exp" type="text" defaultValue={unidade.expediente} />
          </div>

          <div className="field">
            <label htmlFor="cfg-intervalo">Intervalo entre atendimentos</label>
            <select id="cfg-intervalo" defaultValue="15">
              <option value="0">Sem intervalo</option>
              <option value="10">10 minutos</option>
              <option value="15">15 minutos</option>
              <option value="30">30 minutos</option>
            </select>
          </div>

          <div className="field">
            <label htmlFor="cfg-resp">Responsável</label>
            <input id="cfg-resp" type="text" defaultValue={usuario.nomeCompleto} />
          </div>

          <button
            type="button"
            className="btn-primary"
            style={{ marginTop: 6 }}
            onClick={() => avisar('Configurações salvas (apenas nesta sessão).')}
          >
            Salvar alterações
          </button>
        </section>

        <section className="card card-pad">
          <h3>Preferências de operação</h3>
          {preferencias.map((p) => (
            <div key={p.id} className="switch-row">
              <div>
                <strong>{p.titulo}</strong>
                <small>{p.descricao}</small>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={p.ligado}
                aria-label={p.titulo}
                className={`switch ${p.ligado ? 'is-on' : ''}`}
                onClick={() => alternar(p.id)}
              />
            </div>
          ))}
        </section>
      </div>
    </div>
  );
}
