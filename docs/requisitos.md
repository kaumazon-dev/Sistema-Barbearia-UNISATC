# Requisitos — Sistema de Gerenciamento de Barbearias

Projeto Integrador WEB — SATC
Equipe: Kauã Guollo Mazon, Lucas Fernandes Rovaris, Vitor Fernandes de Almeida

---

## 1. Objetivo

Sistema web para gestão de uma barbearia. Centraliza a agenda dos barbeiros, o cadastro
de clientes e serviços, o controle de estoque de produtos e a visão gerencial do negócio.

O problema que resolve: agenda em papel ou WhatsApp gera horário marcado em duplicidade,
cliente esquecido e nenhuma informação sobre faturamento ou consumo de produto.

---

## 2. Atores

| Ator | Descrição |
|---|---|
| **Admin** | Dono ou gerente. Acesso total, incluindo estoque e dashboard. |
| **Barbeiro** | Atende clientes. Vê e gerencia a própria agenda. |
| **Cliente** | Faz login, marca e acompanha os próprios agendamentos. |

Todos os três são registros da tabela `usuario`, diferenciados pelo campo `papel`.

---

## 3. Requisitos funcionais

### 3.1 Autenticação e acesso

| ID | Requisito |
|---|---|
| RF01 | O sistema deve permitir cadastro de usuário com nome, e-mail, telefone e senha. |
| RF02 | O sistema deve rejeitar cadastro com e-mail já existente. |
| RF03 | O sistema deve armazenar a senha apenas como hash, nunca em texto puro. |
| RF04 | O sistema deve autenticar o usuário por e-mail e senha e devolver um token JWT. |
| RF05 | O sistema deve restringir o acesso a cada funcionalidade conforme o papel do usuário. |
| RF06 | O sistema deve permitir desativar um usuário sem apagar seu histórico. |

### 3.2 Clientes

| ID | Requisito |
|---|---|
| RF07 | O admin deve poder cadastrar, listar, editar e desativar clientes. |
| RF08 | O sistema deve permitir buscar cliente por nome ou telefone. |
| RF09 | O sistema deve exibir o histórico de agendamentos de um cliente. |

### 3.3 Serviços

| ID | Requisito |
|---|---|
| RF10 | O admin deve poder cadastrar, listar, editar e desativar serviços. |
| RF11 | Cada serviço deve ter nome, duração em minutos e preço. |
| RF12 | O sistema deve impedir que um serviço desativado seja usado em novo agendamento. |

### 3.4 Agenda

| ID | Requisito |
|---|---|
| RF13 | O sistema deve permitir criar agendamento informando cliente, barbeiro, data/hora de início e um ou mais serviços. |
| RF14 | O sistema deve calcular a hora de término somando a duração dos serviços selecionados. |
| RF15 | **O sistema deve impedir que um agendamento se sobreponha a outro do mesmo barbeiro.** |
| RF16 | O sistema deve registrar o preço cobrado de cada serviço no momento da marcação. |
| RF17 | O sistema deve permitir listar agendamentos por dia e por barbeiro. |
| RF18 | O sistema deve permitir remarcar um agendamento, aplicando novamente a regra do RF15. |
| RF19 | O sistema deve permitir cancelar um agendamento, mantendo o registro. |
| RF20 | O sistema deve permitir marcar um agendamento como concluído. |
| RF21 | O cliente deve poder visualizar apenas os próprios agendamentos. |

Status possíveis do agendamento: `agendado`, `concluido`, `cancelado`.

### 3.5 Estoque

| ID | Requisito |
|---|---|
| RF22 | O admin deve poder cadastrar, listar, editar e desativar produtos. |
| RF23 | Cada produto deve ter nome, unidade, quantidade atual e estoque mínimo. |
| RF24 | O sistema deve registrar entradas e saídas de produto com quantidade, motivo, data e responsável. |
| RF25 | O sistema deve atualizar a quantidade do produto somente por meio de uma movimentação. |
| RF26 | O sistema deve impedir saída que deixe a quantidade negativa. |
| RF27 | O sistema deve sinalizar os produtos com quantidade abaixo do estoque mínimo. |

### 3.6 Dashboard

| ID | Requisito |
|---|---|
| RF28 | O sistema deve exibir a quantidade de atendimentos concluídos por semana e por mês. |
| RF29 | O sistema deve exibir o faturamento por semana e por mês, somando o preço cobrado dos serviços. |
| RF30 | O sistema deve exibir o ranking dos serviços mais vendidos. |
| RF31 | O sistema deve exibir a taxa de cancelamento no período. |
| RF32 | O sistema deve exibir a lista de produtos abaixo do estoque mínimo. |

---

## 4. Requisitos não funcionais

| ID | Requisito |
|---|---|
| RNF01 | O back-end deve ser uma API REST em Python com Flask. |
| RNF02 | O front-end deve usar HTML, CSS e JavaScript puro, sem framework. |
| RNF03 | O banco de dados deve ser PostgreSQL 18. |
| RNF04 | O ambiente de desenvolvimento deve subir por Docker Compose. |
| RNF05 | O schema do banco deve ser versionado por migrations. |
| RNF06 | As senhas devem ser protegidas por algoritmo de hash de biblioteca consolidada. |
| RNF07 | A interface deve ser responsiva e funcionar em telas de celular. |
| RNF08 | Os erros da API devem retornar mensagem legível e código HTTP adequado. |
| RNF09 | Os valores monetários devem usar tipo decimal, nunca ponto flutuante. |

---

## 5. Fora de escopo

Itens deliberadamente não implementados nesta versão:

- Pagamento online e emissão de nota fiscal.
- Notificação automática por e-mail, SMS ou WhatsApp.
- Programa de fidelidade, cupons ou descontos.
- Comissão de barbeiro sobre serviços.
- Múltiplas unidades ou filiais da barbearia.
- Aplicativo mobile nativo.
- Relatórios exportáveis em PDF ou Excel.

---

## 6. Regras de negócio relevantes

**RN01 — Conflito de agenda.**
Dois agendamentos do mesmo barbeiro não podem ocupar o mesmo intervalo de tempo.
Agendamento cancelado não bloqueia horário. Um agendamento que começa exatamente no
minuto em que outro termina é válido.

**RN02 — Preço congelado.**
O preço de cada serviço é copiado para o agendamento no momento da marcação. Alterar o
preço na tabela de serviços não altera agendamentos já existentes.

**RN03 — Duração congelada.**
A hora de término é gravada no agendamento. Alterar a duração de um serviço não desloca
agendamentos já marcados.

**RN04 — Estoque sempre com histórico.**
A quantidade de um produto nunca é alterada diretamente. Toda mudança passa por um
registro em `movimentacao_estoque`.
