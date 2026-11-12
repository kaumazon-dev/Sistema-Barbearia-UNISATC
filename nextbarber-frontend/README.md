# NextBarber — Front-end (modelo de apresentação)

Interface do Sistema de Gerenciamento de Barbearias, construída a partir do
modelo do Figma.

> **Este projeto é apenas um mockup navegável.**
> Não tem tela de login, não faz chamada de API e não depende do backend.
> Todo o conteúdo exibido vem de `src/data/mock.js`.

## Stack

- React 18 (JavaScript, sem TypeScript)
- Vite (servidor de desenvolvimento e build)
- CSS puro, sem framework de UI e sem biblioteca de ícones
  (os ícones são SVG inline em `src/components/Icons.jsx`)

## Como rodar

### 1. Só apresentar (sem instalar nada)

Abra **`NextBarber-apresentacao.html`** com duplo clique. É um arquivo único,
com todo o React, o CSS e os dados embutidos. Funciona offline, sem `npm`, sem
servidor e sem internet (sem internet só troca a fonte Inter pela do sistema).

> A pasta `dist/` **não** serve para duplo clique: ela usa
> `<script type="module">`, e o navegador bloqueia módulos abertos via
> `file://`. Ela é para ser servida por HTTP — veja a opção 2.

### 2. Apresentar em localhost (também sem instalar nada)

Três formas, todas equivalentes — escolha a que preferir:

```bash
npm start           # atalho configurado no package.json
node servidor.js    # o mesmo, direto
node .              # o mesmo, via "main" do package.json
```

No Windows dá para **dar duplo clique em `iniciar.bat`**, sem abrir terminal.

Qualquer uma sobe em <http://localhost:3000> e abre o navegador sozinho. O
`servidor.js` usa só os módulos que já vêm no Node (`http`, `fs`, `path`) —
**não precisa de `npm install`**, não usa esbuild e não baixa nada. É o caminho
para apresentar com uma URL de verdade.

Porta ocupada? Passe outra (funciona nas três formas e no `.bat`):

```bash
npm start -- 8080
node servidor.js 8080
```

O servidor atende só em `127.0.0.1` (acessível apenas nesta máquina); para
mostrar em outro aparelho da rede, troque `'127.0.0.1'` por `'0.0.0.0'` no final
do `servidor.js`.

### 3. Desenvolver

```bash
npm install
npm run dev
```

O Vite sobe em <http://localhost:5173>.

Para gerar a versão de produção:

```bash
npm run build      # regera a pasta dist/ (servida por node servidor.js)
npm run preview    # servidor do proprio Vite em cima da dist/
npm run build:html # regera o NextBarber-apresentacao.html (arquivo único)
```

## Se o `npm install` falhar no Windows

Erro típico em máquina corporativa:

```
npm error code 1
npm error path ...\node_modules\esbuild
npm error Error: spawnSync ...\@esbuild\win32-x64\esbuild.exe UNKNOWN
npm warn cleanup Error: EPERM: operation not permitted, rmdir ...
```

Isso **não é erro do projeto**. O antivírus / proteção de endpoint está
impedindo a execução do `esbuild.exe`, que o Vite usa para compilar.

O que resolve, em ordem:

1. **Não precisa resolver para apresentar** — use `node servidor.js` ou o
   `NextBarber-apresentacao.html`. Nenhum dos dois depende do `npm install`.
2. **Tire o projeto da pasta `Downloads`.** Arquivos vindos da internet ficam
   marcados como bloqueados e o Windows barra os `.exe` de dentro deles. Mova
   para algo como `C:\dev\nextbarber`, apague `node_modules` e
   `package-lock.json`, e rode `npm install` de novo.
3. **Desbloqueie o .zip antes de extrair**: botão direito no arquivo →
   Propriedades → marque **Desbloquear** → OK → extraia de novo.
4. Se ainda falhar, peça para o antivírus liberar a pasta do projeto, ou rode
   em outra máquina.

## Telas

| Menu | Arquivo | O que mostra |
|---|---|---|
| Dashboard | `src/pages/Dashboard.jsx` | Tela do Figma: 4 indicadores, próximos agendamentos, barbeiros disponíveis e otimização de escala |
| Agendamentos | `src/pages/Agendamentos.jsx` | Agenda do dia com filtro por status |
| Clientes | `src/pages/Clientes.jsx` | Listagem com busca por nome ou telefone |
| Barbeiros | `src/pages/Barbeiros.jsx` | Cards da equipe com desempenho do dia |
| Serviços | `src/pages/Servicos.jsx` | Catálogo com duração e preço |
| Relatórios | `src/pages/Relatorios.jsx` | Faturamento da semana e ranking de serviços |
| Configurações | `src/pages/Configuracoes.jsx` | Dados da unidade e preferências |

A navegação é feita por estado no `App.jsx` (`useState`), sem `react-router`.

## Funções mapeadas

Tudo abaixo já funciona na interface, **em memória**. Nenhuma chamada de rede:
apertar F5 devolve os dados originais de `src/data/mock.js`.

### Agendamentos
- **Novo agendamento** — botão no Dashboard e na tela de Agendamentos. Modal com
  horário, cliente, barbeiro, serviço e status. Campos obrigatórios acusam erro,
  e o valor é preenchido pelo preço do serviço escolhido.
- **Editar agendamento** — mesmo modal, já preenchido.
- **Avançar o atendimento** pelo menu `•••` da linha: Confirmar → Iniciar
  atendimento → Concluir. Cancelados e concluídos podem ser reabertos.
- **Cancelar horário** e **Excluir** (com confirmação).
- **Filtro por status** com a contagem de cada um.

### Clientes
- **Novo cliente** e **Editar cadastro** (nome, telefone, plano, ticket).
- **Ver ficha**: clicar no nome abre o histórico daquele cliente, montado a
  partir da própria agenda.
- **Agendar horário** já com o cliente selecionado.
- **Excluir** com confirmação.
- **Busca** por nome ou telefone.

### Barbeiros
- **Novo barbeiro** e **Editar**.
- **Mudar situação** (Disponível / Ocupado / Intervalo) pelo menu do card.
- **Agendar com ele** já com o barbeiro selecionado.
- "Atendendo agora" e "Atendimentos hoje" saem da agenda, não são texto fixo.

### Serviços
- **Novo serviço** e **Editar** (nome, categoria, duração, preço).
- **Desativar / Reativar**: serviço desativado some do formulário de
  agendamento, como pede o RF12 do documento de requisitos.

### Topo da tela
- **Busca global**: procura em agendamentos, clientes e serviços ao mesmo tempo;
  clicar em um resultado leva à tela certa ou abre a ficha.
- **Sino de notificações** com o painel de avisos recentes.

### Indicadores que reagem
Os quatro cartões do Dashboard são calculados a partir da agenda. Criar um
agendamento muda "Agendamentos hoje" e a "Taxa de ocupação"; concluir um
atendimento muda "Faturamento do dia" e "Clientes atendidos"; pôr um barbeiro
em intervalo muda a "Otimização de escala".

Para a tela abrir com os mesmos números do Figma (18 · R$ 2.450 · 12 · 78%),
`unidade.baseDoDia` em `src/data/mock.js` representa o que já aconteceu antes do
trecho de agenda que a tabela mostra. Os cartões somam essa base ao que está na
tela.

## Estrutura

```
NextBarber-apresentacao.html # arquivo unico, abre com duplo clique
servidor.js                  # servidor local sem dependencias (npm start)
iniciar.bat                  # duplo clique no Windows: sobe o servidor
dist/                        # build de producao, servida pelo servidor.js
src/
├── App.jsx                 # layout e troca de telas
├── main.jsx                # ponto de entrada
├── components/             # Sidebar, Topbar, cards, tabela, modal, ícones
├── forms/                  # modais de cadastro, ficha e confirmação
├── pages/                  # uma tela por item do menu
├── state/AppStore.jsx      # estado da aplicação e todas as ações
├── utils/                  # formatação e menu de ações do agendamento
├── data/mock.js            # TODOS os dados fictícios ficam aqui
├── styles/
│   ├── global.css          # tokens de cor, tipografia, badges
│   └── table.css           # tabela padrão
└── scripts/inline.mjs      # gera o HTML único (npm run build:html)
```

## Design

Os tokens do modelo estão centralizados em `:root`, dentro de
`src/styles/global.css`:

| Token | Valor | Uso |
|---|---|---|
| `--bg-app` | `#0b0b0c` | Fundo da aplicação |
| `--bg-sidebar` | `#0f0f11` | Menu lateral |
| `--bg-surface` | `#141416` | Cards e tabelas |
| `--border` | `#232327` | Contorno dos cards |
| `--gold` | `#e9a23b` | Cor de marca (item ativo, destaques, botões) |
| `--green` / `--blue` / `--red` | — | Status dos agendamentos |

A fonte é a **Inter**, carregada do Google Fonts no `index.html`, com fallback
para a fonte do sistema caso não haja internet.

Os avatares são gerados por iniciais (`src/components/Avatar.jsx`) para que o
projeto não dependa de imagens externas. Se quiser usar as fotos do Figma,
troque o `<Avatar />` por um `<img />` apontando para arquivos em `public/`.

## Como plugar no backend depois

Os agendamentos guardam `clienteId`, `barbeiroId` e `servicoId` — as mesmas
chaves estrangeiras do banco. O `src/state/AppStore.jsx` resolve esses ids em
nomes antes de entregar para as telas.

Para integrar, o ponto de troca é só esse arquivo: cada função (`salvarCliente`,
`mudarStatus`, `removerAgendamento`…) vira uma chamada HTTP, e o estado inicial
sai de um `fetch` no lugar do `src/data/mock.js`. Nenhum componente de tela
precisa ser reescrito.
