# Deriv Trading Platform
## Documento de Arquitetura e Especificação Funcional

**Versão:** 1.0  
**Data:** 20/11/2026  
**Status:** Em elaboração  
**Escopo:** Backend, integração Deriv e futura plataforma de gestão.

---

# 1. Visão geral do projeto

## 1.1. Objetivo

Desenvolver uma plataforma própria para disponibilizar e gerenciar robôs de negociação conectados à API oficial da Deriv.

A plataforma deverá permitir que diversos clientes utilizem robôs simultaneamente, cada um operando em sua própria conta Deriv, com possibilidade de utilização de contas demo e reais.

O backend será responsável pela infraestrutura de dados, indicadores, estratégias, gerenciamento dos robôs, integração com a Deriv e execução das operações.

Futuramente, será desenvolvido um frontend para permitir a gestão administrativa e a gestão individual dos clientes.

## 1.2. Modelo de funcionamento

A plataforma deverá funcionar da seguinte maneira:

1. O usuário acessa a plataforma.
2. Caso ainda não possua conta Deriv, poderá criá-la por meio do link de indicação do proprietário da plataforma.
3. O usuário autoriza a conexão entre sua conta Deriv e a plataforma.
4. Escolhe a conta demo ou real.
5. Configura e ativa os robôs disponíveis.
6. Utiliza a plataforma durante um período inicial de avaliação de sete dias.
7. Ao final da avaliação, poderá continuar utilizando a plataforma ou encerrar seu acesso.

Cada cliente deverá operar exclusivamente com suas próprias contas e autorizações.

## 1.3. Modelo de remuneração

A plataforma deverá contemplar duas fontes independentes de remuneração:

**A. Markup da aplicação Deriv**
- Utilização do programa de Markup Commission.
- Remuneração vinculada às operações elegíveis realizadas por meio da aplicação.
- Respeito às regras, limites e condições estabelecidos pela Deriv.

**B. Programa de parceiros Deriv**
- Disponibilização de link de indicação.
- Aquisição de novos clientes.
- Identificação das indicações.
- Acompanhamento das comissões e resultados conforme as regras do programa.

As duas modalidades deverão ser tratadas separadamente no backend.

## 1.4. Princípios fundamentais

- Cada cliente mantém sua própria conta Deriv.
- A plataforma não deverá custodiar os recursos financeiros dos clientes.
- A autorização de acesso deverá ser individual.
- Contas demo e reais deverão ser suportadas.
- Os dados dos clientes deverão ser isolados.
- Os robôs deverão funcionar independentemente uns dos outros.
- A execução deverá ser rastreável e auditável.
- A integração será própria, baseada na documentação e nos schemas oficiais da Deriv.
- A plataforma deverá permitir a revogação de acesso sem comprometer a conta Deriv do cliente.

## 1.5. Ciclo de vida do cliente

O ciclo deverá contemplar:

1. Cadastro.
2. Vinculação da conta Deriv.
3. Autorização da aplicação.
4. Configuração dos robôs.
5. Período de avaliação de sete dias.
6. Continuidade ou encerramento.
7. Desvinculação, quando solicitada.

Quando o cliente encerrar seu vínculo com a plataforma, perderá o acesso aos robôs e aos serviços oferecidos, mas continuará tendo acesso normal à sua conta diretamente na Deriv.

---

# 2. Arquitetura geral

## 2.1. Tecnologias atuais

| Tecnologia | Finalidade | Situação |
|---|---|---|
| Python 3.14 | Linguagem principal | Implementado |
| FastAPI | API do backend | Implementado |
| PostgreSQL 16 | Banco de dados | Implementado |
| TimescaleDB | Armazenamento de séries temporais | Extensão configurada |
| asyncpg | Comunicação assíncrona com PostgreSQL | Implementado |
| Alembic | Migrações do banco | Estrutura criada |
| Docker | Ambiente de execução | Implementado |
| Docker Compose | Orquestração dos serviços | Implementado |
| Pytest | Testes automatizados | Implementado |
| WebSocket Deriv | Recepção de dados de mercado | Implementado |

## 2.2. Arquitetura lógica

A arquitetura deverá ser organizada em módulos independentes, com responsabilidades bem definidas.

Os principais módulos previstos são:

- API e gerenciamento de requisições.
- Usuários e autenticação.
- Integração com a Deriv.
- Contas e autorizações Deriv.
- Dados de mercado.
- Banco de dados.
- Indicadores e estratégias.
- Gestão dos robôs.
- Execução de operações.
- Planos e período de avaliação.
- Programa de parceiros e Markup.
- Auditoria e monitoramento.

A implementação será incremental. A definição de um módulo nesta documentação não significa que ele já esteja desenvolvido.

## 2.3. Arquitetura de dados de mercado existente

O sistema já possui uma estrutura de coleta e armazenamento de dados.

O fluxo atual é:

1. Conexão com o WebSocket público da Deriv.
2. Recepção dos ticks dos ativos configurados.
3. Construção de candles de um minuto (M1).
4. Recuperação de histórico de candles pela API.
5. Persistência dos candles no PostgreSQL.
6. Disponibilização dos dados armazenados para processamento posterior.

Decisões já estabelecidas:

- Armazenar candles M1.
- Utilizar UTC como referência temporal.
- Persistir candles somente após seu fechamento.
- Manter o candle em formação em memória.
- Não criar candles artificiais para minutos sem dados.
- Utilizar o histórico oficial da Deriv para recuperação.
- Preservar os dados existentes durante migrações.

## 2.4. Banco de dados existente

O projeto já possui PostgreSQL configurado e migrações gerenciadas pelo Alembic.

A estrutura inclui:

- Infraestrutura de TimescaleDB.
- Schema inicial.
- Deduplicação de ticks.
- Tabela `price_candles`.

A tabela `price_candles` armazena os candles por ativo e horário, com valores OHLC e restrições de integridade.

O histórico já existente deverá ser preservado durante a evolução do banco.

## 2.5. Integração com a Deriv

A integração será desenvolvida e mantida pelo próprio projeto.

Não utilizaremos como dependência principal o SDK Python arquivado ou sem manutenção.

As referências oficiais serão:

- https://developers.deriv.com/docs/
- https://github.com/deriv-com/deriv-api-schemas

A integração deverá contemplar os recursos públicos e privados necessários à operação da plataforma.

O endpoint público atualmente configurado é:

`wss://api.derivws.com/trading/v1/options/ws/public`

A compatibilidade de cada operação será validada com a documentação vigente antes de sua implementação.

## 2.6. Requisitos arquiteturais

A arquitetura deverá atender aos seguintes requisitos:

- Processamento assíncrono.
- Baixa latência.
- Suporte a múltiplos usuários.
- Suporte a múltiplos robôs simultâneos.
- Suporte a diferentes ativos.
- Isolamento entre clientes.
- Resiliência a desconexões.
- Recuperação de dados.
- Controle de concorrência.
- Segurança das credenciais.
- Rastreabilidade das operações.
- Escalabilidade horizontal quando necessário.

## 2.7. Estado atual e próximos desenvolvimentos

**Já implementado ou estruturado:**
- Ambiente Docker.
- API FastAPI.
- Banco PostgreSQL.
- Migrações Alembic.
- Coleta de dados de mercado.
- Construção de candles M1.
- Recuperação de histórico.
- Persistência de candles.
- Monitoramento básico da coleta.

**Próximas etapas arquiteturais:**
- Auditoria da integração atual.
- Gerenciamento centralizado das conexões Deriv.
- Autenticação multiusuário.
- Vinculação de contas individuais.
- Gerenciamento de autorizações.
- Catálogo dinâmico de ativos.
- Indicadores e estratégias.
- Gerenciamento e execução dos robôs.
- Gestão de planos e avaliação.

---

# 3. Estrutura do Backend e Responsabilidades dos Módulos

**Status:** Em especificação  
**Objetivo:** Definir a organização lógica do backend, as responsabilidades de cada módulo e as regras de comunicação entre eles.

## 3.1. Princípios de organização

O backend será organizado de forma modular, com separação entre:

- Camada de API: comunicação com o frontend e consumidores externos.
- Camada de serviços: execução das regras de negócio.
- Camada de integração: comunicação com a Deriv e outros serviços externos.
- Camada de dados: persistência e consulta ao banco.
- Camada de processamento: indicadores, estratégias e execução dos robôs.
- Camada de infraestrutura: configurações, conexões, monitoramento e tarefas operacionais.

Cada módulo deverá possuir uma responsabilidade principal e interfaces bem definidas.

Um módulo não deverá acessar diretamente a implementação interna de outro módulo quando existir uma interface de serviço apropriada.

## 3.2. Estrutura atual do projeto

A estrutura conhecida atualmente inclui:

```text
Deriv/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── health.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   └── connection.py
│   ├── services/
│   │   └── deriv_market_data.py
│   └── main.py
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
├── .env.example
├── Dockerfile
├── compose.yaml
├── pyproject.toml
└── README.md
```

Esta representação registra os diretórios e arquivos identificados durante o desenvolvimento. Não deve ser considerada uma listagem exaustiva de todos os arquivos existentes.

## 3.3. Módulos existentes

### 3.3.1. Core

**Localização atual:** `app/core/`

Responsabilidade:
- Centralizar configurações da aplicação.
- Carregar variáveis de ambiente.
- Disponibilizar configurações tipadas.
- Manter parâmetros de conexão e funcionamento.

Arquivo identificado:
- `config.py`

Estado: Implementado.

### 3.3.2. Database

**Localização atual:** `app/db/`

Responsabilidade:
- Gerenciar a conexão com PostgreSQL.
- Criar e disponibilizar o pool assíncrono.
- Controlar o ciclo de vida das conexões.
- Disponibilizar acesso ao banco para os serviços.

Arquivo identificado:
- `connection.py`

Estado: Implementado.

### 3.3.3. API

**Localização atual:** `app/api/`

Responsabilidade:
- Expor endpoints HTTP.
- Receber requisições.
- Validar entradas.
- Encaminhar solicitações aos serviços responsáveis.
- Retornar respostas padronizadas.

Arquivo identificado:
- `routes/health.py`

Estado: Implementado parcialmente. A rota de saúde existe; as APIs funcionais da plataforma ainda serão desenvolvidas.

### 3.3.4. Services

**Localização atual:** `app/services/`

Responsabilidade:
- Implementar serviços operacionais da aplicação.
- Coordenar processos que envolvem banco de dados e integrações.
- Executar tarefas de negócio sem depender diretamente das rotas HTTP.

Arquivo identificado:
- `deriv_market_data.py`

Estado: Implementado parcialmente. O serviço de coleta, recuperação e persistência de dados de mercado já existe e possui testes.

## 3.4. Módulos planejados

Os módulos abaixo representam a organização funcional desejada. A localização definitiva dos arquivos será decidida durante a evolução do projeto.

### 3.4.1. Integração Deriv

**Responsabilidade:** Centralizar a comunicação com a API oficial da Deriv.

Funções:
- Gerenciar conexões WebSocket.
- Gerenciar requisições e respostas.
- Correlacionar identificadores de requisição.
- Implementar autenticação.
- Gerenciar conexões públicas e privadas.
- Tratar erros e reconexões.
- Validar mensagens conforme os schemas oficiais.

Limite de responsabilidade:
- Não deverá implementar estratégias de negociação.
- Não deverá decidir quando um robô deve operar.
- Não deverá controlar planos ou permissões comerciais da plataforma.

### 3.4.2. Usuários e autenticação

**Responsabilidade:** Gerenciar a identidade e o acesso dos clientes à plataforma.

Funções:
- Cadastro de usuários.
- Autenticação.
- Recuperação de acesso.
- Perfis e permissões.
- Controle de sessões.
- Isolamento dos dados por usuário.

### 3.4.3. Contas Deriv

**Responsabilidade:** Gerenciar as contas Deriv vinculadas pelos clientes.

Funções:
- Vinculação de contas.
- Autorização via mecanismo oficial.
- Identificação de contas demo e reais.
- Gerenciamento de tokens e credenciais.
- Consulta de informações da conta.
- Controle de permissões concedidas.
- Desvinculação e revogação.

Uma conta Deriv pertence ao respectivo cliente. O backend deverá garantir que um usuário não consiga acessar ou operar contas de outro usuário sem autorização.

### 3.4.4. Market Data

**Responsabilidade:** Receber, organizar, recuperar e disponibilizar dados de mercado.

Funções:
- Gerenciar assinaturas de ativos.
- Receber ticks.
- Construir candles.
- Recuperar histórico.
- Persistir dados.
- Detectar lacunas.
- Recuperar dados após desconexões.
- Disponibilizar candles para indicadores e estratégias.

Decisão estabelecida:
- A coleta será centralizada por ativo sempre que possível.
- Os dados serão armazenados uma única vez, independentemente da quantidade de robôs que os utilizem.
- Os consumidores utilizarão os dados armazenados, evitando consultas repetidas e processamento desnecessário.

### 3.4.5. Indicators

**Responsabilidade:** Calcular indicadores técnicos a partir dos dados de mercado.

Funções:
- Consultar candles armazenados.
- Calcular indicadores.
- Manter parâmetros configuráveis.
- Disponibilizar resultados para as estratégias.
- Controlar períodos mínimos de dados necessários.

Regra:
Os indicadores deverão utilizar prioritariamente os candles persistidos. O candle em formação poderá ser utilizado quando necessário, respeitando as regras de consistência.

### 3.4.6. Strategies

**Responsabilidade:** Transformar informações de mercado e indicadores em sinais de negociação.

Funções:
- Avaliar condições de entrada.
- Avaliar condições de saída.
- Aplicar regras configuradas.
- Gerar sinais.
- Registrar justificativas e parâmetros utilizados.

Limite:
Uma estratégia não deverá enviar diretamente ordens à Deriv. Ela deverá produzir sinais para o módulo responsável pela execução.

### 3.4.7. Bots

**Responsabilidade:** Gerenciar o ciclo de vida e a configuração dos robôs.

Funções:
- Criar e configurar robôs.
- Associar robôs a usuários.
- Associar robôs a contas Deriv.
- Definir ativos e estratégias.
- Ativar e desativar robôs.
- Controlar estados operacionais.
- Coordenar a execução das estratégias.

Cada instância de robô deverá possuir identificação própria e contexto isolado.

### 3.4.8. Execution

**Responsabilidade:** Executar operações autorizadas na Deriv.

Funções:
- Receber sinais ou comandos manuais.
- Validar condições de execução.
- Verificar conta e autorização.
- Preparar contratos.
- Enviar operações à Deriv.
- Acompanhar contratos abertos.
- Registrar resultados.
- Tratar falhas e respostas inesperadas.

Regra:
Nenhuma operação poderá ser enviada sem validação de usuário, conta, robô, autorização e condições de execução.

### 3.4.9. Risk Management

**Responsabilidade:** Aplicar controles de risco antes e durante as operações.

Funções:
- Validar limites de operação.
- Controlar exposição.
- Aplicar limites de perdas.
- Respeitar parâmetros definidos pelo usuário.
- Bloquear operações quando as condições de segurança não forem atendidas.

O gerenciamento de risco deverá funcionar como uma camada independente das estratégias.

### 3.4.10. Plans and Access

**Responsabilidade:** Controlar o direito de utilização da plataforma.

Funções:
- Gerenciar planos.
- Registrar início da avaliação.
- Controlar o período de sete dias.
- Verificar validade do acesso.
- Autorizar ou bloquear o uso dos robôs.
- Gerenciar cancelamentos e encerramentos.

A expiração do acesso à plataforma não deverá cancelar ou modificar a conta Deriv do cliente.

### 3.4.11. Partners and Markup

**Responsabilidade:** Organizar as informações relacionadas às fontes de remuneração.

Funções:
- Registrar referências de indicação.
- Associar clientes às indicações, conforme os dados oficiais disponíveis.
- Integrar informações do programa de parceiros.
- Acompanhar dados de Markup Commission.
- Disponibilizar relatórios administrativos.

As duas fontes de remuneração deverão permanecer separadas, respeitando as regras e os recursos disponibilizados pela Deriv.

### 3.4.12. Audit and Monitoring

**Responsabilidade:** Registrar eventos relevantes e acompanhar a saúde da plataforma.

Funções:
- Registrar autenticações.
- Registrar alterações de configuração.
- Registrar autorizações e revogações.
- Registrar decisões de execução.
- Monitorar conexões.
- Monitorar serviços.
- Registrar falhas e eventos operacionais.

Os registros deverão permitir reconstruir o histórico de uma operação e identificar qual usuário, conta e robô estavam envolvidos.

## 3.5. Regras de comunicação entre módulos

As seguintes regras deverão orientar a implementação:

1. A API recebe requisições e encaminha as ações aos serviços.
2. Usuários e permissões determinam quem pode solicitar cada ação.
3. Contas Deriv fornecem o contexto de autorização necessário.
4. Market Data disponibiliza dados para indicadores e estratégias.
5. Indicators fornecem resultados para Strategies.
6. Strategies geram sinais, mas não executam operações.
7. Bots coordenam as instâncias e suas configurações.
8. Execution valida e encaminha as operações à integração Deriv.
9. Risk Management pode bloquear uma operação antes do envio.
10. Audit registra os eventos relevantes de todos os módulos.

## 3.6. Fluxo lógico de uma operação

```text
Market Data
    |
    v
Indicators
    |
    v
Strategies
    |
    v
Bots
    |
    v
Risk Management
    |
    v
Execution
    |
    v
Deriv Integration
    |
    v
Deriv API
    |
    v
Resultado da operação
    |
    v
Audit / Database
```

O fluxo manual deverá utilizar os mesmos mecanismos de validação, risco e execução. A diferença será a origem da solicitação, que poderá ser uma ação do cliente em vez de um sinal automático.

## 3.7. Isolamento entre usuários e robôs

O sistema deverá garantir:

- Separação dos dados por usuário.
- Separação das contas vinculadas.
- Identificação individual de cada robô.
- Controle de acesso em todas as operações.
- Impossibilidade de utilizar autorização de outro cliente.
- Monitoramento independente das instâncias.
- Capacidade de interromper um

# 4. Integração com a Deriv

**Status:** Em especificação  
**Objetivo:** Definir a arquitetura, as responsabilidades e os mecanismos de comunicação entre o backend da plataforma e os serviços oficiais da Deriv.

## 4.1. Diretriz arquitetural

A plataforma terá uma integração própria com a Deriv.

Não adotaremos o SDK Python arquivado ou sem manutenção como dependência principal.

A implementação será baseada em:

- Documentação oficial da Deriv.
- Schemas oficiais da API.
- Protocolos e endpoints oficialmente disponibilizados.
- Testes automatizados de compatibilidade.

Referências oficiais:

- https://developers.deriv.com/docs/
- https://github.com/deriv-com/deriv-api-schemas

A integração deverá ser independente das regras de negócio dos robôs. Sua função será fornecer uma camada confiável de comunicação com a Deriv.

## 4.2. Responsabilidades da integração

O módulo de integração deverá ser responsável por:

1. Estabelecer conexões com os serviços da Deriv.
2. Gerenciar conexões WebSocket.
3. Gerenciar requisições HTTP.
4. Enviar mensagens conforme os contratos oficiais da API.
5. Receber e interpretar respostas.
6. Correlacionar requisições e respostas.
7. Controlar assinaturas de dados.
8. Gerenciar autenticação e autorização.
9. Tratar erros e desconexões.
10. Implementar reconexões.
11. Validar mensagens e estruturas de dados.
12. Registrar eventos técnicos relevantes.

Não será responsável por definir estratégias, indicadores, regras comerciais ou decisões de negociação.

## 4.3. Tipos de conexão

A integração deverá separar as conexões conforme sua finalidade.

### 4.3.1. Conexão pública

Utilizada para informações que não dependem da autorização de uma conta individual.

Exemplos:

- Recepção de ticks.
- Histórico de preços.
- Catálogo de ativos.
- Dados públicos de mercado.

Endpoint público atualmente configurado:

`wss://api.derivws.com/trading/v1/options/ws/public`

Estado: Implementado parcialmente. A coleta de ticks e a recuperação de histórico já estão implementadas.

### 4.3.2. Conexão privada

Utilizada para operações e informações que exigem autorização de uma conta Deriv.

Exemplos:

- Consulta de informações da conta.
- Consulta de saldo.
- Consulta de contratos.
- Compra de contratos.
- Acompanhamento de operações.
- Consulta de transações, quando disponível.

A conexão privada deverá ser estabelecida com autorização individual de cada cliente, seguindo o fluxo oficial de autenticação da Deriv.

Estado: Planejado.

## 4.4. Autenticação e autorização

A plataforma deverá permitir que cada cliente autorize sua própria conta Deriv.

O modelo deverá contemplar OAuth2, respeitando os mecanismos oficiais de autorização e os escopos necessários.

Responsabilidades:

- Iniciar o processo de autorização.
- Receber o retorno da autorização.
- Validar a identidade e a conta autorizada.
- Registrar os escopos concedidos.
- Proteger tokens e credenciais.
- Renovar ou solicitar nova autorização quando necessário.
- Detectar autorizações expiradas ou revogadas.
- Encerrar o acesso quando o cliente desvincular sua conta.

### 4.4.1. Princípios de segurança

- Nunca solicitar a senha da conta Deriv do cliente.
- Nunca compartilhar tokens entre usuários.
- Não armazenar credenciais em texto puro.
- Restringir os escopos ao mínimo necessário.
- Não registrar tokens em logs.
- Proteger os fluxos de autorização contra falsificação e interceptação.
- Respeitar a revogação de acesso.

### 4.4.2. Separação de ambientes

O sistema deverá distinguir:

- Conta demo.
- Conta real.

A identificação deverá ser obtida por informações oficiais da conta, e não apenas por uma configuração informada pelo usuário.

Operações em contas reais deverão exigir controles adicionais de autorização e risco.

## 4.5. Gerenciamento de conexões

O módulo deverá controlar as conexões de forma centralizada.

Responsabilidades:

- Abrir e encerrar conexões.
- Controlar o estado de cada conexão.
- Detectar perda de comunicação.
- Implementar reconexão automática.
- Evitar conexões duplicadas desnecessárias.
- Controlar timeouts.
- Monitorar latência.
- Gerenciar o ciclo de vida das assinaturas.

As conexões públicas e privadas terão ciclos de vida independentes.

Uma falha na conexão privada de um cliente não deverá interromper a coleta pública de dados de mercado.

## 4.6. Gerenciamento de requisições

Toda requisição deverá possuir controle de identificação e resposta.

O mecanismo deverá contemplar:

- Identificador único de requisição.
- Associação entre requisição e resposta.
- Controle de timeout.
- Tratamento de respostas de erro.
- Cancelamento quando aplicável.
- Proteção contra respostas duplicadas.
- Tratamento de respostas recebidas fora de ordem.

Requisições simultâneas deverão ser processadas sem bloquear desnecessariamente as demais operações.

## 4.7. Gerenciamento de assinaturas

A integração deverá controlar as assinaturas de dados disponibilizadas pela Deriv.

Exemplos:

- Assinatura de ticks.
- Assinatura de informações de conta.
- Acompanhamento de contratos, quando suportado.

Cada assinatura deverá possuir identificação, estado e mecanismo de cancelamento.

As assinaturas de mercado deverão ser compartilhadas entre os consumidores internos sempre que possível.

Assinaturas privadas deverão respeitar o contexto de autorização de cada cliente.

## 4.8. Tratamento de falhas

A integração deverá prever:

- Perda de conexão.

# 5. Gestão de Usuários, Contas Deriv e Autorizações

**Status:** Em especificação  
**Objetivo:** Definir o gerenciamento da identidade dos clientes, o vínculo com suas contas Deriv e o controle de acesso da plataforma às contas autorizadas.

## 5.1. Princípios fundamentais

O gerenciamento de usuários deverá respeitar os seguintes princípios:

- Cada cliente terá uma identidade própria na plataforma.
- Cada cliente poderá vincular sua própria conta Deriv.
- A plataforma não será proprietária das contas Deriv.
- A senha da Deriv nunca será solicitada ou armazenada.
- Cada autorização deverá estar associada ao respectivo usuário.
- O acesso às contas deverá respeitar os escopos concedidos.
- O cliente poderá solicitar a desvinculação a qualquer momento.
- A suspensão da plataforma não deverá bloquear o acesso direto à Deriv.

## 5.2. Cadastro de usuários

**Responsabilidade:** Registrar e gerenciar os clientes da plataforma.

Informações previstas:

- Identificador interno único.
- Nome.
- E-mail.
- Data de cadastro.
- Situação cadastral.
- Data de início da avaliação.
- Data de término da avaliação.
- Plano contratado, quando aplicável.
- Data de encerramento, quando aplicável.

O cadastro da plataforma será independente do cadastro realizado na Deriv.

Um usuário poderá possuir cadastro na plataforma mesmo antes de vincular uma conta Deriv.

## 5.3. Autenticação dos usuários

**Responsabilidade:** Garantir que somente usuários autenticados acessem os recursos permitidos.

Funções:

- Login.
- Logout.
- Recuperação de acesso.
- Gerenciamento de sessões.
- Expiração de sessões.
- Proteção contra tentativas indevidas.
- Controle de permissões.

A autenticação da plataforma será independente da autenticação da Deriv.

O cliente terá uma credencial para acessar a plataforma e utilizará o fluxo oficial da Deriv para autorizar sua conta.

## 5.4. Perfis e permissões

A plataforma deverá possuir, inicialmente, dois perfis principais:

### 5.4.1. Administrador

Responsabilidades:

- Gerenciar usuários.
- Consultar contas vinculadas.
- Gerenciar robôs e configurações.
- Monitorar operações.
- Gerenciar planos e avaliações.
- Consultar indicadores operacionais.
- Acompanhar informações de parceiros e Markup.
- Administrar permissões.

### 5.4.2. Cliente

Responsabilidades e permissões:

- Gerenciar seu próprio cadastro.
- Vincular suas contas Deriv.
- Consultar informações das contas autorizadas.
- Configurar seus robôs.
- Ativar e desativar robôs.
- Consultar operações e resultados.
- Gerenciar seu acesso à plataforma.
- Solicitar desvinculação.

O controle de permissões deverá ser aplicado no backend, não apenas na interface do frontend.

## 5.5. Vinculação de contas Deriv

**Responsabilidade:** Permitir que o cliente autorize a plataforma a acessar sua conta Deriv.

O processo deverá seguir o mecanismo oficial de autorização da Deriv.

Fluxo previsto:

1. Cliente acessa a opção de vincular conta.
2. Backend inicia o processo oficial de autorização.
3. Cliente é direcionado ao ambiente da Deriv.
4. Cliente autentica-se diretamente na Deriv.
5. Cliente concede as permissões solicitadas.
6. Deriv retorna os dados de autorização.
7. Backend valida o retorno.
8. Backend identifica a conta autorizada.
9. Backend registra o vínculo.
10. Conta fica disponível para utilização conforme as permissões concedidas.

A plataforma não deverá solicitar a senha da Deriv em nenhuma etapa.

## 5.6. Gerenciamento das contas vinculadas

Cada conta vinculada deverá possuir um registro independente.

Informações previstas:

- Identificador interno da conta.
- Usuário proprietário.
- Identificador da conta na Deriv.
- Tipo de conta: demo ou real.
- Moeda da conta, quando disponível.
- Escopos autorizados.
- Estado da autorização.
- Data de vinculação.
- Data da última validação.
- Estado operacional da conexão.

A identificação do tipo de conta deverá ser obtida por dados oficiais da Deriv.

### 5.6.1. Múltiplas contas

A arquitetura deverá permitir a associação de mais de uma conta Deriv a um usuário, caso os mecanismos e as regras da Deriv permitam.

Cada conta deverá manter autorização, identificação e estado operacional independentes.

O limite de contas vinculadas será definido posteriormente.

### 5.6.2. Contas demo e reais

A plataforma deverá suportar os dois ambientes.

Contas demo:
- Desenvolvimento.
- Testes.
- Validação de estratégias.
- Avaliação dos robôs.

Contas reais:
- Operações com recursos financeiros do cliente.
- Controles adicionais de segurança.
- Validação de permissões.
- Monitoramento de operações.

A plataforma deverá identificar claramente o ambiente antes de permitir qualquer operação.

Não deverá ser possível executar uma operação real por engano devido a uma configuração incorreta.

## 5.7. Gerenciamento de autorizações

**Responsabilidade:** Controlar as permissões concedidas pelo cliente à aplicação.

Funções:

- Registrar autorizações.
- Identificar os escopos concedidos.
- Armazenar tokens de forma protegida.
- Controlar validade.
- Detectar falhas de autenticação.
- Detectar revogações.
- Solicitar nova autorização quando necessário.
- Encerrar conexões privadas quando o acesso deixar de ser válido.

### 5.7.1. Proteção de tokens

Os tokens deverão:

- Ser armazenados criptografados.
- Nunca aparecer em respostas públicas da API.
- Nunca ser registrados em logs.
- Ser acessíveis somente aos componentes autorizados.
- Ser protegidos por controles de acesso.
- Ser excluídos ou inutilizados quando não forem mais necessários.

A criptografia deverá utilizar gerenciamento seguro de chaves, separado dos dados criptografados.

### 5.7.2. Escopos mínimos

A plataforma deverá solicitar somente as permissões necessárias para as funcionalidades habilitadas.

Os escopos deverão ser definidos por recurso, considerando as operações necessárias para:

- Consultar informações da conta.
- Consultar saldo.
- Consultar contratos.
- Comprar contratos.
- Acompanhar operações.

A lista definitiva dependerá dos escopos efetivamente disponibilizados pela Deriv e dos requisitos de cada funcionalidade.

## 5.8. Associação entre usuário, conta e robô

A associação deverá seguir esta estrutura lógica:

```text
Usuário
   |
   ├── Conta Deriv Demo
   |      |
   |      ├── Robô A
   |      └── Robô B
   |
   └── Conta Deriv Real
          |
          ├── Robô C
          └── Robô D
```

Cada robô deverá estar associado a:

- Um usuário proprietário.
- Uma conta Deriv autorizada.
- Uma configuração operacional.
- Uma estratégia.
- Um ou mais ativos, conforme sua configuração.

O backend deverá validar essa associação antes de qualquer execução.

Nenhum robô poderá utilizar automaticamente uma conta pertencente a outro usuário.

## 5.9. Desvinculação de contas

**Responsabilidade:** Permitir que o cliente interrompa a conexão entre sua conta Deriv e a plataforma.

O processo deverá contemplar:

1. Receber a solicitação de desvinculação.
2. Bloquear novas operações.
3. Desativar os robôs associados à conta.
4. Tratar operações que ainda estejam abertas.
5. Encerrar conexões privadas.
6. Invalidar ou excluir os tokens armazenados, conforme o mecanismo aplicável.
7. Registrar o evento de desvinculação.
8. Atualizar o estado da conta.

### 5.9.1. Operações abertas

A desvinculação não deverá simplesmente abandonar contratos que já foram comprados.

Antes de encerrar a conexão, o sistema deverá verificar se existem operações abertas e garantir que seu acompanhamento não seja perdido.

A plataforma deverá distinguir:

- Bloqueio de novas operações.
- Acompanhamento de contratos existentes.
- Encerramento da autorização.
- Desvinculação definitiva.

O comportamento para contratos ainda abertos deverá respeitar as possibilidades e regras da Deriv.

### 5.9.2. Consequências da desvinculação

Após a desvinculação:

- O cliente perde o acesso aos robôs associados à conta.
- A plataforma não poderá iniciar novas operações nessa conta.
- Os tokens de acesso deixam de ser utilizáveis pela plataforma.
- O cliente mantém sua conta Deriv.
- O cliente mantém acesso direto ao site e aplicativo oficial da Deriv.
- O histórico da conta na Deriv permanece sob controle da Deriv.

A desvinculação da plataforma não deverá ser confundida com o encerramento da conta Deriv.

## 5.10. Isolamento e segurança dos dados

O backend deverá garantir isolamento entre usuários.

Regras:

- Um cliente não poderá consultar contas de outro cliente.
- Um cliente não poderá acessar robôs de outro cliente.
- Um cliente não poderá consultar operações de outro cliente.
- Um cliente não poderá utilizar tokens de outro cliente.
- Toda solicitação deverá validar o proprietário do recurso.
- Operações administrativas deverão ser registradas.

O isolamento deverá existir na camada de serviços e no acesso aos dados, não somente nas rotas da API.

## 5.11. Estrutura de dados prevista

As entidades lógicas iniciais serão:

| Entidade | Finalidade |
|---|---|
| users | Cadastro dos clientes |
| user_sessions | Sessões de autenticação |
| deriv_accounts | Contas Deriv vinculadas |
| deriv_authorizations | Autorizações e permissões |
| access_events | Histórico de acessos e alterações |
| account_events | Eventos relacionados às contas |

A estrutura física das tabelas, relacionamentos, índices e restrições será definida na especificação do banco de dados.

Os nomes são propostas e não indicam que as tabelas já existem.

## 5.12. Testes e critérios de aceitação

O módulo deverá possuir testes para:

- Cadastro de usuários.
- Autenticação.
- Controle de permissões.
- Vinculação de contas.
- Identificação de contas demo e reais.
- Proteção de tokens.
- Isolamento entre usuários.
- Associação de contas e robôs.
- Expiração de autorização.
- Revogação de autorização.
- Desvinculação.
- Tratamento de operações abertas durante a desvinculação.

Os testes de integração deverão utilizar contas demo sempre que possível.

## 5.13. Estado de implementação

| Funcionalidade | Situação |
|---|---|
| Cadastro de usuários | Planejado |
| Autenticação própria | Planejado |
| Perfis e permissões | Planejado |
| Vinculação OAuth2 | Planejado |
| Identificação de contas Deriv | Planejado |
| Contas demo e reais | Planejado |
| Armazenamento protegido de tokens | Planejado |
| Gestão de autorizações | Planejado |
| Associação de contas e robôs | Planejado |
| Desvinculação | Planejado |
| Isolamento multiusuário | Planejado |

## 5.14. Critério de conclusão deste capítulo

Este capítulo será considerado validado quando:

- O modelo de usuários estiver definido.
- O processo de vinculação estiver documentado.
- As responsabilidades sobre contas estiverem claras.
- O modelo de autorização estiver especificado.
- As regras de segurança estiverem estabelecidas.
- O processo de desvinculação estiver definido.
- O isolamento entre clientes estiver documentado.

# 6. Dados de Mercado (Market Data)

**Status:** Parcialmente implementado e em evolução  
**Objetivo:** Definir como a plataforma coleta, recupera, armazena, organiza e disponibiliza dados de mercado da Deriv para os indicadores, estratégias e robôs.

## 6.1. Responsabilidade do módulo

O módulo Market Data será responsável por toda a infraestrutura de dados de mercado.

Suas responsabilidades incluem:

- Receber dados da Deriv.
- Gerenciar assinaturas de ativos.
- Processar ticks recebidos.
- Construir candles.
- Recuperar histórico.
- Persistir dados no banco.
- Detectar lacunas no histórico.
- Recuperar dados após desconexões.
- Disponibilizar dados aos consumidores internos.
- Monitorar a integridade e a disponibilidade dos dados.

O módulo não deverá executar operações financeiras nem tomar decisões de negociação.

## 6.2. Arquitetura de coleta

A coleta será centralizada por ativo.

Isso significa que, se dez robôs utilizarem o mesmo ativo, a plataforma deverá aproveitar a mesma fonte de dados, em vez de abrir dez conexões independentes para receber os mesmos ticks.

Fluxo:

```text
             Deriv API
                 |
                 v
          WebSocket Público
                 |
                 v
          Recepção de Ticks
                 |
                 v
           CandleBuilder
                 |
                 v
          Fila de Persistência
                 |
                 v
             PostgreSQL
                 |
          +------+------+
          |      |      |
          v      v      v
       Robô A  Robô B  Robô C
```

A distribuição interna deverá permitir que vários consumidores utilizem os mesmos dados sem duplicar a coleta.

## 6.3. Recepção de ticks

O backend utilizará WebSocket para receber atualizações de preços.

Responsabilidades:

- Conectar ao endpoint público da Deriv.
- Solicitar assinatura dos ativos configurados.
- Receber mensagens de ticks.
- Identificar o ativo correspondente.
- Validar os dados recebidos.
- Encaminhar os ticks ao componente responsável pela construção dos candles.

A recepção deverá ser assíncrona, evitando bloqueios no processamento de outros ativos.

## 6.4. Construção de candles

A plataforma utilizará inicialmente candles de um minuto (M1).

O componente CandleBuilder será responsável por transformar os ticks recebidos em candles OHLC.

Cada candle deverá conter:

- `asset_symbol`: identificação do ativo.
- `candle_start`: início do intervalo.
- `open`: primeiro preço observado.
- `high`: maior preço observado.
- `low`: menor preço observado.
- `close`: último preço observado.

### 6.4.1. Regras de construção

- O intervalo será de 60 segundos.
- O horário será armazenado em UTC.
- O primeiro tick observado no intervalo define a abertura.
- O maior preço observado define a máxima.
- O menor preço observado define a mínima.
- O último preço observado define o fechamento.
- O candle somente será persistido após seu fechamento.
- O candle em formação permanecerá em memória.

### 6.4.2. Primeiro intervalo após conexão

Quando uma assinatura for iniciada ou reiniciada, o primeiro intervalo observado poderá estar incompleto.

Esse candle não deverá ser considerado completo e não deverá ser emitido como candle fechado.

A partir da transição para o próximo intervalo, o sistema poderá emitir os candles completos observados.

### 6.4.3. Minutos sem dados

A plataforma não deverá criar candles artificiais para intervalos sem ticks.

A ausência de dados deverá permanecer identificável, sem inventar preços ou movimentos.

## 6.5. Recuperação de histórico

O backend utilizará o recurso oficial `ticks_history` da Deriv para recuperar candles históricos.

Parâmetros atualmente adotados:

| Parâmetro | Valor |
|---|---|
| Método | ticks_history |
| Estilo | candles |
| Granularidade | 60 segundos |
| Período inicial | 14 dias |
| Quantidade por requisição | Até 5.000 registros |

A recuperação deverá respeitar os limites e as respostas efetivamente disponibilizados pela API.

### 6.5.1. Recuperação inicial

Na primeira inicialização de um ativo:

1. Identificar a ausência de histórico local.
2. Solicitar histórico à Deriv.
3. Processar os candles retornados.
4. Validar os registros.
5. Persistir os dados.
6. Iniciar ou manter a atualização em tempo real.

### 6.5.2. Recuperação incremental

Quando já houver histórico armazenado:

1. Consultar o último candle persistido.
2. Solicitar dados a partir de um intervalo anterior ao último registro.
3. Recuperar os candles posteriores.
4. Reconciliar registros existentes.
5. Persistir os novos registros.

A recuperação deverá permitir corrigir eventuais diferenças entre os dados locais e o histórico oficial.

### 6.5.3. Separação entre histórico e tempo real

A coleta em tempo real e a recuperação histórica utilizarão conexões independentes.

A assinatura em tempo real deverá ser estabelecida antes da recuperação histórica, reduzindo a possibilidade de perder atualizações durante o processo.

## 6.6. Persistência no banco de dados

Os candles serão armazenados no PostgreSQL, utilizando a extensão TimescaleDB para dados temporais.

Tabela existente:

`price_candles`

Campos:

| Campo | Finalidade |
|---|---|
| asset_symbol | Identificação do ativo |
| candle_start | Início do candle |
| open | Preço de abertura |
| high | Preço máximo |
| low | Preço mínimo |
| close | Preço de fechamento |
| received_at | Momento de recebimento/persistência |

### 6.6.1. Integridade dos dados

A chave primária será composta por:

- `candle_start`
- `asset_symbol`

Isso impede duplicidade de candles para o mesmo ativo e intervalo.

Também existem restrições para garantir a consistência dos valores OHLC.

### 6.6.2. Estratégia de gravação

O sistema utilizará operações em lote para reduzir o número de transações.

Existem dois comportamentos distintos:

**Histórico:**
- Permite atualizar um candle existente.
- Utiliza `ON CONFLICT DO UPDATE`.
- Permite reconciliar dados históricos.

**Tempo real:**
- Utiliza `ON CONFLICT DO NOTHING`.
- Não permite que uma atualização ao vivo sobrescreva um registro já persistido.

Essa separação protege a integridade do histórico.

## 6.7. Recuperação após desconexões

O serviço deverá detectar interrupções e restabelecer a comunicação.

O processo deverá contemplar:

- Detecção de desconexão.
- Reconexão automática.
- Backoff progressivo.
- Nova assinatura dos ativos.
- Recuperação do histórico perdido.
- Atualização do estado operacional.

A recuperação deverá evitar duplicações e preservar a continuidade dos dados.

O sistema não deverá presumir que uma reconexão significa que todos os intervalos foram recebidos.

## 6.8. Distribuição interna dos dados

Os dados de mercado serão disponibilizados aos módulos internos.

Consumidores previstos:

- Indicators.
- Strategies.
- Bots.
- Monitoramento.
- Futuras interfaces de gráficos.

A arquitetura deverá permitir consultas históricas e acesso aos dados recentes sem exigir que cada consumidor estabeleça sua própria conexão com a Deriv.

### 6.8.1. Fonte de verdade

O PostgreSQL será a fonte persistente de verdade dos candles fechados.

O candle em formação poderá ser disponibilizado em memória, mas deverá ser identificado como provisório.

Os consumidores deverão saber distinguir:

- Candle fechado e persistido.
- Candle atual em formação.
- Intervalo sem dados.
- Dados históricos em recuperação.

## 6.9. Gerenciamento de ativos

O sistema deverá evoluir para suportar um catálogo dinâmico de ativos.

Funções previstas:

- Consultar ativos disponíveis.
- Identificar símbolos.
- Registrar informações dos ativos.
- Identificar disponibilidade.
- Controlar assinaturas ativas.
- Compartilhar dados entre robôs.
- Evitar assinaturas duplicadas.

O catálogo deverá utilizar informações oficiais da Deriv, em vez de depender exclusivamente de uma lista fixa no arquivo de configuração.

## 6.10. Desempenho e escalabilidade

O módulo deverá ser desenvolvido considerando:

- Grande volume de atualizações.
- Múltiplos ativos simultâneos.
- Múltiplos robôs consumidores.
- Processamento assíncrono.
- Escrita em lote.
- Consultas indexadas.
- Controle de memória.
- Backpressure nas filas.
- Monitoramento de latência.

O sistema deverá evitar que a lentidão do banco bloqueie a recepção de dados de mercado.

A política de filas deverá prever limites, monitoramento e tratamento de sobrecarga para evitar perda silenciosa de dados.

## 6.11. Monitoramento

O módulo deverá disponibilizar métricas como:

- Estado da conexão WebSocket.
- Ativos assinados.
- Último tick recebido por ativo.
- Último candle persistido.
- Tamanho da fila de gravação.
- Quantidade de candles processados.
- Quantidade de erros.
- Tempo de recuperação.
- Tempo de persistência.
- Lacunas identificadas.

Essas informações serão utilizadas pelo monitoramento administrativo e pela futura interface.

## 6.12. Estado de implementação

| Funcionalidade | Situação |
|---|---|
| Conexão WebSocket pública | Implementado |
| Recepção de ticks | Implementado |
| CandleBuilder M1 | Implementado e testado |
| Recuperação histórica | Implementado e testado |
| Recuperação incremental | Implementado e testado |
| Persistência em PostgreSQL | Implementado e testado |
| Gravação em lote | Implementado |
| Reconexão automática | Implementado parcialmente |
| Monitoramento básico | Implementado |
| Catálogo dinâmico de ativos | Planejado |
| Distribuição interna otimizada | Em evolução |
| Gráficos e consultas para frontend | Planejado |

## 6.13. Testes e critérios de aceitação

O módulo deverá possuir testes para:

- Construção correta de candles.
- Cálculo de OHLC.
- Transição entre intervalos.
- Primeiro intervalo incompleto.
- Ausência de candles artificiais.
- Persistência.
- Deduplicação.
- Recuperação histórica.
- Recuperação incremental.
- Reconexão.
- Recuperação de lacunas.
- Múltiplos ativos.
- Concorrência.
- Sobrecarga da fila de persistência.

A implementação atual possui testes específicos para CandleBuilder, recuperação de histórico, integração com PostgreSQL e monitoramento.

O conjunto completo de testes anteriormente executado apresentou 27 testes aprovados. Essa quantidade deverá ser novamente verificada em cada etapa de evolução.

## 6.14. Critério de conclusão deste capítulo

Este capítulo será considerado validado quando:

- O fluxo de coleta estiver documentado.
- As regras de construção dos candles estiverem definidas.
- A recuperação histórica estiver especificada.
- A persistência estiver documentada.
- A estratégia de reconexão estiver definida.
- A distribuição dos dados estiver especificada.
- Os requisitos de desempenho estiverem estabelecidos.
- A implementação existente estiver diferenciada das evoluções planejadas.

# 7. Indicadores e Estratégias

**Status:** Planejado  
**Objetivo:** Definir como os dados de mercado serão processados, como os indicadores técnicos serão calculados e como as estratégias utilizarão esses resultados para gerar sinais de negociação.

## 7.1. Visão geral

Os módulos de indicadores e estratégias serão responsáveis pelo processamento lógico das informações de mercado.

O fluxo será:

```text
PostgreSQL
    |
    v
Candles M1
    |
    v
Indicators
    |
    v
Resultados dos indicadores
    |
    v
Strategies
    |
    v
Sinais de negociação
    |
    v
Bots
```

Os módulos deverão funcionar independentemente da comunicação direta com a Deriv.

## 7.2. Módulo de indicadores (Indicators)

### 7.2.1. Responsabilidade

Calcular indicadores técnicos utilizando os dados de mercado disponíveis na plataforma.

O módulo deverá:

- Consultar candles armazenados.
- Calcular indicadores técnicos.
- Gerenciar parâmetros de cálculo.
- Disponibilizar resultados às estratégias.
- Identificar dados insuficientes.
- Controlar a atualização dos cálculos.
- Evitar cálculos desnecessários e duplicados.

### 7.2.2. Fonte dos dados

A fonte principal será a tabela `price_candles`.

Os indicadores deverão trabalhar prioritariamente com candles fechados e persistidos.

O candle atual, ainda em formação, poderá ser utilizado quando a estratégia permitir, mas deverá ser identificado como provisório.

Cada cálculo deverá considerar:

- Ativo.
- Período gráfico.
- Intervalo temporal.
- Tipo de indicador.
- Parâmetros.
- Estado dos candles utilizados.

### 7.2.3. Indicadores previstos

A arquitetura deverá permitir implementar diferentes famílias de indicadores.

**Tendência:**
- SMA.
- EMA.
- MACD.
- ADX.

**Momentum:**
- RSI.
- Stochastic.
- CCI.
- Williams %R.

**Volatilidade:**
- Bollinger Bands.
- ATR.
- Keltner Channels.

**Volume e outros dados:**
- Indicadores de volume, quando aplicáveis aos dados efetivamente disponibilizados pela Deriv.
- Indicadores personalizados.

A lista não representa uma obrigação de implementar todos imediatamente.

### 7.2.4. Parâmetros configuráveis

Cada indicador deverá possuir parâmetros próprios.

Exemplo:

| Indicador | Parâmetro |
|---|---|
| RSI | Período |
| EMA | Período |
| SMA | Período |
| MACD | Períodos rápido e lento; sinal |
| Bollinger Bands | Período e desvio |
| ATR | Período |

Os parâmetros deverão ser configuráveis sem necessidade de modificar o código-fonte.

### 7.2.5. Histórico necessário

Cada indicador deverá declarar a quantidade mínima de candles necessária para produzir um resultado válido.

Exemplo:

Um RSI de 14 períodos precisa de histórico suficiente para seu cálculo e inicialização.

O sistema não deverá gerar sinais com indicadores ainda não inicializados ou com dados insuficientes.

## 7.3. Processamento e atualização

O processamento deverá ocorrer conforme a disponibilidade de novos dados.

Eventos que poderão iniciar uma atualização:

- Fechamento de um candle.
- Disponibilização de dados históricos.
- Alteração de parâmetros.
- Inicialização de uma estratégia.
- Recuperação de dados após desconexão.

O sistema deverá evitar recalcular desnecessariamente todo o histórico a cada novo candle.

### 7.3.1. Cálculo incremental

Sempre que tecnicamente adequado, os indicadores deverão utilizar processamento incremental.

Isso permite atualizar os resultados utilizando apenas os novos dados e o estado anterior do cálculo.

O resultado incremental deverá ser validado contra o cálculo completo para garantir equivalência.

### 7.3.2. Compartilhamento de cálculos

Se diferentes robôs utilizarem o mesmo indicador, ativo, período e parâmetros, a plataforma deverá permitir compartilhar os resultados calculados.

A identificação de um cálculo deverá considerar:

- Ativo.
- Timeframe.
- Indicador.
- Parâmetros.
- Candle de referência.
- Versão do algoritmo.

Dessa forma, evitamos repetir cálculos idênticos.

## 7.4. Módulo de estratégias (Strategies)

### 7.4.1. Responsabilidade

Interpretar os dados de mercado e os resultados dos indicadores para identificar oportunidades de negociação.

O módulo deverá:

- Avaliar condições de entrada.
- Avaliar condições de saída.
- Combinar indicadores.
- Aplicar regras lógicas.
- Considerar filtros.
- Gerar sinais.
- Registrar os motivos que originaram cada sinal.

A estratégia não deverá enviar ordens diretamente à Deriv.

### 7.4.2. Estrutura de uma estratégia

Cada estratégia deverá possuir:

- Identificador.
- Nome.
- Versão.
- Descrição.
- Indicadores utilizados.
- Parâmetros.
- Condições de entrada.
- Condições de saída.
- Filtros.
- Regras de invalidação.
- Timeframe.
- Ativos compatíveis.

### 7.4.3. Condições de negociação

Uma estratégia poderá avaliar:

**Entrada:**
- Cruzamento de médias.
- RSI acima ou abaixo de determinado limite.
- MACD indicando mudança de momentum.
- Rompimento de bandas.
- Combinação de indicadores.

**Saída:**
- Condição técnica contrária.
- Alvo atingido.
- Stop configurado.
- Tempo máximo de operação.
- Regra específica da estratégia.

As condições concretas dependerão de cada estratégia implementada.

### 7.4.4. Filtros

As estratégias poderão utilizar filtros para evitar sinais em condições inadequadas.

Exemplos:

- Filtro de tendência.
- Filtro de volatilidade.
- Filtro de horário.
- Filtro de qualidade dos dados.
- Filtro de frequência de sinais.

## 7.5. Geração de sinais

Quando as condições de uma estratégia forem atendidas, será gerado um sinal.

Cada sinal deverá conter:

| Informação | Finalidade |
|---|---|
| signal_id | Identificação única |
| user_id | Cliente proprietário |
| bot_id | Robô responsável |
| strategy_id | Estratégia utilizada |
| asset_symbol | Ativo |
| timeframe | Período gráfico |
| signal_type | Tipo de sinal |
| reference_time | Momento de referência |
| reference_price | Preço de referência |
| indicator_snapshot | Valores dos indicadores |
| strategy_version | Versão da estratégia |
| status | Estado do sinal |

Tipos de sinal previstos:

- Compra.
- Venda.
- Saída.
- Cancelamento.
- Nenhuma operação.

A interpretação de compra e venda deverá respeitar o tipo de contrato suportado pela Deriv.

## 7.6. Controle de sinais duplicados

A plataforma deverá impedir que o mesmo evento gere múltiplas operações indevidas.

Para isso, cada sinal deverá possuir uma identificação lógica baseada em:

- Robô.
- Estratégia.
- Ativo.
- Candle de referência.
- Tipo de sinal.

O controle deverá considerar também sinais simultâneos e concorrência entre processos.

A geração de um sinal não significa que uma operação foi executada.

## 7.7. Separação entre estratégia e execução

A arquitetura deverá manter responsabilidades independentes:

| Módulo | Responsabilidade |
|---|---|
| Indicators | Calcular indicadores |
| Strategies | Interpretar condições |
| Bots | Coordenar a execução lógica |
| Risk Management | Validar riscos |
| Execution | Executar operações |

Uma estratégia não poderá acessar diretamente tokens, conexões privadas ou métodos de compra da Deriv.

## 7.8. Isolamento e reutilização

Os indicadores e estratégias poderão ser compartilhados tecnicamente, mas suas configurações serão independentes.

Exemplo:

Dois clientes poderão utilizar a mesma estratégia, mas com parâmetros diferentes.

```text
Estratégia RSI
    |
    +-- Cliente A
    |      RSI: 14
    |      Limite inferior: 30
    |
    +-- Cliente B
           RSI: 21
           Limite inferior: 25
```

A plataforma deverá manter a separação entre:

- Código da estratégia.
- Versão da estratégia.
- Configuração do robô.
- Parâmetros do cliente.
- Resultados dos cálculos.

## 7.9. Versionamento

Cada estratégia deverá possuir versão identificável.

Uma alteração nas regras deverá produzir uma nova versão, permitindo:

- Rastrear sinais antigos.
- Reproduzir decisões.
- Comparar resultados.
- Evitar mudanças silenciosas em robôs ativos.
- Identificar qual lógica gerou determinada operação.

Os indicadores também deverão possuir versão de implementação quando uma mudança puder alterar seus resultados.

## 7.10. Backtesting e validação

A arquitetura deverá permitir testar estratégias utilizando dados históricos.

Funções futuras:

- Reprocessar candles históricos.
- Simular condições de entrada e saída.
- Calcular resultados.
- Comparar parâmetros.
- Avaliar desempenho.
- Identificar limitações da estratégia.

O backtesting deverá considerar custos, payout, regras contratuais e limitações do produto Deriv utilizado, quando aplicáveis.

Resultados históricos não deverão ser apresentados como garantia de desempenho futuro.

## 7.11. Armazenamento

Estruturas de dados previstas:

| Entidade | Finalidade |
|---|---|
| indicators | Cadastro de indicadores |
| indicator_configs | Parâmetros dos indicadores |
| indicator_values | Resultados calculados, quando persistidos |
| strategies | Cadastro e versões das estratégias |
| strategy_configs | Configurações das estratégias |
| trading_signals | Histórico de sinais |

A necessidade de persistir todos os valores de indicadores será avaliada considerando desempenho, volume de dados e necessidade de auditoria.

Não devemos duplicar dados que possam ser calculados de forma eficiente sem necessidade operacional.

## 7.12. Monitoramento

O módulo deverá acompanhar:

- Tempo de cálculo.
- Quantidade de cálculos.
- Indicadores com dados insuficientes.
- Erros de processamento.
- Estratégias ativas.
- Sinais gerados.
- Sinais duplicados bloqueados.
- Atraso entre fechamento do candle e geração do sinal.

## 7.13. Testes e critérios de aceitação

Os testes deverão contemplar:

- Precisão matemática dos indicadores.
- Inicialização com histórico suficiente.
- Dados insuficientes.
- Cálculo incremental.
- Equivalência entre cálculo incremental e completo.
- Condições de entrada.
- Condições de saída.
- Combinação de indicadores.
- Geração de sinais.
- Prevenção de duplicidade.
- Isolamento entre clientes.
- Versionamento de estratégias.
- Reprodução histórica de decisões.

## 7.14. Estado de implementação

| Funcionalidade | Situação |
|---|---|
| Consulta de candles | Infraestrutura existente |
| Motor de indicadores | Planejado |
| Indicadores técnicos | Planejado |
| Cálculo incremental | Planejado |
| Compartilhamento de cálculos | Planejado |
| Motor de estratégias | Planejado |
| Configuração de estratégias | Planejado |
| Geração de sinais | Planejado |
| Controle de duplicidade | Planejado |
| Backtesting | Planejado |
| Versionamento | Planejado |

## 7.15. Critério de conclusão deste capítulo

Este capítulo será considerado validado quando:

- As responsabilidades dos indicadores estiverem definidas.
- As responsabilidades das estratégias estiverem definidas.
- A fonte de dados estiver estabelecida.
- O processamento incremental estiver especificado.
- A geração de sinais estiver documentada.
- A prevenção de duplicidade estiver definida.
- O versionamento estiver estabelecido.
- A separação entre sinais e execução estiver clara.

# Capítulo 8 — Gestão dos Robôs (Bots)

## 8.1. Objetivo do módulo

O módulo de Bots será responsável por gerenciar o ciclo de vida dos robôs de trading da plataforma.

Cada bot representa uma instância operacional vinculada a um cliente, a uma conta Deriv e a uma estratégia configurada.

Suas responsabilidades incluem:

- Criar e configurar robôs.
- Associar robôs a estratégias.
- Definir ativos e períodos gráficos.
- Controlar início, pausa, retomada e encerramento.
- Monitorar o estado operacional.
- Garantir isolamento entre clientes.
- Coordenar o processamento de sinais.
- Impedir execuções duplicadas.
- Registrar o histórico de funcionamento.

O módulo não deverá calcular indicadores, implementar estratégias ou enviar ordens diretamente à Deriv. Essas responsabilidades pertencem aos respectivos módulos.

## 8.2. Conceito de Bot

Um bot é uma instância de execução de uma estratégia com parâmetros próprios.

Cada bot deverá possuir, no mínimo:

- Identificador único.
- Cliente proprietário.
- Conta Deriv vinculada.
- Ambiente da conta: demo ou real.
- Estratégia utilizada.
- Versão da estratégia.
- Ativos monitorados.
- Timeframes utilizados.
- Parâmetros operacionais.
- Perfil de risco.
- Configuração de execução.
- Estado atual.
- Data de criação e última atualização.

Um cliente poderá possuir vários bots, inclusive utilizando a mesma estratégia com configurações diferentes.

A utilização simultânea de uma conta por vários bots deverá respeitar as regras da Deriv e os controles de risco da plataforma.

## 8.3. Ciclo de vida do Bot

O bot deverá possuir estados operacionais explícitos.

| Estado | Descrição |
|---|---|
| Draft | Bot em elaboração ou configuração inicial. |
| Stopped | Bot configurado, mas sem execução ativa. |
| Starting | Processo de inicialização. |
| Running | Bot em funcionamento. |
| Pausing | Processo de pausa. |
| Paused | Bot temporariamente pausado. |
| Stopping | Processo de encerramento. |
| Error | Erro que impede a operação normal. |
| Suspended | Bot bloqueado por uma condição administrativa ou de acesso. |

As transições deverão ser controladas pelo módulo, impedindo mudanças inválidas de estado.

Condições específicas também deverão ser registradas, sem confundir o estado operacional com a causa do bloqueio:

- Autorização Deriv revogada.
- Conta desconectada.
- Plano expirado.
- Período de teste encerrado.
- Limite de risco atingido.
- Falha de comunicação.
- Bloqueio administrativo.

## 8.4. Inicialização

Ao receber uma solicitação de início, o módulo deverá validar:

1. Existência e propriedade do bot.
2. Configuração válida.
3. Estratégia disponível e versão compatível.
4. Conta Deriv vinculada e autorizada.
5. Ambiente correto: demo ou real.
6. Plano ou período de teste válido.
7. Limites operacionais e de risco.
8. Disponibilidade dos ativos e dados necessários.

Após as validações, o módulo deverá criar uma sessão de execução e iniciar o processamento.

O bot deverá consumir sinais produzidos pelo módulo de Estratégias, sem executar diretamente chamadas de negociação à API da Deriv.

## 8.5. Separação entre demo e real

A plataforma deverá tratar os ambientes demo e real como contextos operacionais distintos.

Regras obrigatórias:

- O ambiente deverá estar explicitamente definido na configuração do bot.
- Um bot demo não poderá operar em uma conta real.
- Um bot real não poderá operar em uma conta demo.
- A conta utilizada deverá ser validada antes de cada sessão.
- A interface deverá identificar claramente o ambiente.
- Alterar o ambiente exigirá validação e confirmação explícitas.

Nenhuma configuração poderá provocar uma mudança automática de demo para real.

## 8.6. Pausa e encerramento

### Pausa

Ao pausar um bot, o sistema deverá:

- Impedir a geração de novas operações pelo bot.
- Suspender o processamento de novos sinais para execução.
- Preservar a configuração e o histórico.
- Registrar o evento e seu motivo.
- Manter o controle de operações que já foram abertas.

### Encerramento

Ao encerrar um bot, o sistema deverá:

- Bloquear novas operações.
- Finalizar a sessão de execução.
- Registrar o estado final.
- Preservar o histórico operacional.
- Encaminhar o tratamento de contratos abertos ao módulo de Execução.

O encerramento do bot não deverá presumir que contratos abertos possam ser cancelados ou fechados imediatamente. Isso dependerá dos recursos efetivamente disponíveis na Deriv e das regras de negociação aplicáveis.

## 8.7. Configuração e versionamento

As configurações deverão ser versionadas.

Cada sessão de execução deverá registrar um snapshot imutável das configurações utilizadas, incluindo:

- Versão da estratégia.
- Parâmetros da estratégia.
- Ativos.
- Timeframes.
- Perfil de risco.
- Conta e ambiente.
- Configurações operacionais.

Alterações posteriores não deverão modificar retroativamente uma sessão já iniciada.

Uma mudança relevante na configuração deverá gerar uma nova versão ou um novo snapshot operacional.

## 8.8. Concorrência e idempotência

O módulo deverá impedir:

- Inicialização simultânea duplicada do mesmo bot.
- Duas sessões ativas incompatíveis para o mesmo bot.
- Processamento duplicado de um mesmo sinal.
- Execução de comandos fora de ordem.
- Alterações concorrentes que comprometam o estado operacional.

Comandos de início, pausa e encerramento deverão possuir controle de concorrência e idempotência.

A garantia de não duplicação de operações financeiras deverá ser complementada pelo módulo de Execução, que será responsável pelo controle das solicitações enviadas à Deriv.

## 8.9. Integração com outros módulos

O módulo de Bots deverá se comunicar com:

| Módulo | Responsabilidade na integração |
|---|---|
| Usuários e Contas | Identificar proprietário e conta autorizada. |
| Planos e Acesso | Validar permissões e período de utilização. |
| Market Data | Consumir dados de mercado por distribuição interna. |
| Indicadores | Consultar os indicadores necessários à estratégia. |
| Estratégias | Receber sinais e resultados de avaliação. |
| Gestão de Risco | Validar limites antes de solicitar uma operação. |
| Execução | Encaminhar operações autorizadas e acompanhar seu estado. |
| Auditoria e Monitoramento | Registrar eventos, falhas e alterações. |

A coleta de dados de mercado deverá ser compartilhada entre os bots que utilizarem o mesmo ativo. Não deverá existir uma conexão independente com a Deriv para cada robô sem necessidade técnica justificada.

## 8.10. Estrutura de dados proposta

Entidades principais:

**bots**
- id
- user_id
- deriv_account_id
- strategy_id
- name
- environment
- status
- created_at
- updated_at

**bot_configs**
- id
- bot_id
- version
- configuration
- created_at

**bot_runs**
- id
- bot_id
- config_version
- strategy_version
- status
- started_at
- finished_at
- termination_reason

**bot_events**
- id
- bot_id
- run_id
- event_type
- previous_state
- new_state
- details
- created_at

Os campos e relacionamentos definitivos serão estabelecidos durante o projeto do banco de dados e das migrações.

## 8.11. Segurança e isolamento

O módulo deverá garantir:

- Um cliente não poderá consultar ou controlar bots de outro cliente.
- Toda operação deverá validar a propriedade do bot.
- Credenciais Deriv não deverão ser armazenadas na configuração do bot.
- Tokens deverão permanecer sob responsabilidade do módulo de autorização.
- Comandos administrativos deverão possuir controle de permissão.
- Alterações relevantes deverão gerar registros de auditoria.

## 8.12. Testes e critérios de aceitação

O módulo será considerado apto quando os seguintes cenários forem validados:

1. Criar bots com configurações diferentes.
2. Associar bots às contas e estratégias corretas.
3. Iniciar, pausar, retomar e encerrar bots.
4. Impedir transições de estado inválidas.
5. Impedir inicializações duplicadas.
6. Garantir isolamento entre clientes.
7. Impedir operação quando a autorização estiver revogada.
8. Impedir operação quando o plano ou período de teste não permitir acesso.
9. Diferenciar corretamente ambientes demo e real.
10. Preservar snapshots de configuração e versões.
11. Tratar corretamente bots com contratos ainda abertos.
12. Registrar eventos e falhas operacionais.

## 8.13. Situação atual

| Recurso | Situação |
|---|---|
| Estrutura de gerenciamento de bots | Planejado |
| Cadastro e configuração | Planejado |
| Ciclo de vida | Planejado |
| Sessões de execução | Planejado |
| Integração com estratégias | Planejado |
| Integração com gestão de risco | Planejado |
| Controle de concorrência | Planejado |
| Histórico e auditoria | Planejado |

O módulo de Bots ainda não está implementado. Este capítulo define sua arquitetura funcional, sem exigir alterações na estrutura atual do projeto.

## 8.14. Decisão arquitetural

Os bots serão instâncias independentes de execução, mas compartilharão serviços centrais da plataforma, especialmente Market Data e cálculos de indicadores compatíveis.

Cada bot manterá seu próprio contexto de estratégia, configuração, risco e execução.

A responsabilidade de enviar operações à Deriv permanecerá exclusivamente no módulo de Execução, mediante validação do módulo de Gestão de Risco.

# Capítulo 9 — Gestão de Risco (Risk Management)

## 9.1. Objetivo do módulo

O módulo de Gestão de Risco será responsável por aplicar os limites financeiros e operacionais da plataforma antes que qualquer operação seja enviada à Deriv.

Sua função é proteger o capital do cliente, controlar a exposição dos robôs e impedir operações que não respeitem as regras configuradas.

Nenhum sinal de estratégia ou comando manual poderá ignorar as validações deste módulo.

O módulo deverá atuar como uma camada independente de autorização de operações, sem executar diretamente ordens na Deriv.

## 9.2. Princípios fundamentais

A arquitetura deverá seguir estes princípios:

- Cada cliente terá seu próprio contexto de risco.
- Cada conta Deriv terá limites próprios.
- Cada bot poderá possuir limites individuais.
- Os limites da plataforma poderão restringir os limites configurados pelo cliente.
- Uma operação somente será autorizada após todas as validações.
- Falhas na validação deverão resultar em bloqueio, nunca em autorização automática.
- Operações manuais e automáticas deverão seguir as mesmas regras.
- Todas as decisões deverão ser registradas.

## 9.3. Hierarquia dos limites

A gestão de risco deverá considerar diferentes níveis:

| Nível | Escopo |
|---|---|
| Plataforma | Limites globais e regras obrigatórias. |
| Cliente | Limites gerais de utilização. |
| Conta Deriv | Exposição e limites financeiros da conta. |
| Bot | Limites individuais de cada robô. |
| Operação | Validação específica da ordem solicitada. |

Um limite de nível inferior não poderá ampliar um limite obrigatório de nível superior.

Exemplo: se a plataforma estabelecer uma exposição máxima de 5% para determinada conta, o cliente não poderá configurar um bot para ultrapassar esse limite.

## 9.4. Parâmetros de risco

O módulo deverá permitir configurar e validar parâmetros como:

### Limites financeiros

- Valor máximo por operação.
- Exposição máxima simultânea.
- Perda máxima por dia.
- Perda máxima por sessão.
- Limite de perda acumulada.
- Saldo mínimo operacional.
- Percentual máximo do saldo comprometido.

### Limites operacionais

- Número máximo de operações simultâneas.
- Número máximo de operações por período.
- Intervalo mínimo entre operações.
- Número máximo de perdas consecutivas.
- Pausa automática após sequência de perdas.
- Limite de operações por ativo.
- Limite de exposição por estratégia.

Nem todos os parâmetros serão aplicáveis a todos os tipos de contrato. A validação deverá considerar as características do contrato oferecido pela Deriv.

## 9.5. Validação antes da operação

Toda solicitação deverá passar por uma sequência de verificações:

1. Identificar cliente, conta e bot.
2. Confirmar autorização da conta Deriv.
3. Confirmar que o ambiente é o esperado: demo ou real.
4. Verificar plano e permissões de acesso.
5. Consultar os limites da plataforma.
6. Consultar os limites do cliente e da conta.
7. Consultar os limites do bot.
8. Verificar saldo e exposição disponíveis.
9. Verificar limites de operações simultâneas.
10. Verificar perdas acumuladas e bloqueios ativos.
11. Validar os parâmetros específicos do contrato.
12. Autorizar ou rejeitar a solicitação.

O resultado deverá ser explícito e identificável.

Exemplo de resultado:

- Autorizado.
- Rejeitado por limite financeiro.
- Rejeitado por exposição máxima.
- Rejeitado por conta não autorizada.
- Rejeitado por limite de perdas.
- Rejeitado por bloqueio operacional.

## 9.6. Controle de perdas

O sistema deverá acompanhar os resultados das operações e atualizar os indicadores de risco.

Deverão ser considerados:

- Resultado realizado.
- Resultado de contratos ainda abertos, quando disponível.
- Perdas acumuladas no período.
- Sequência de operações negativas.
- Exposição financeira atual.
- Limites de perda configurados.

A definição de lucro, prejuízo e exposição deverá respeitar os dados financeiros efetivamente retornados pela Deriv, incluindo taxas e demais componentes aplicáveis.

O sistema deverá distinguir claramente:

- Resultado realizado: operações encerradas.
- Resultado não realizado: exposição ou resultado de contratos ainda abertos.
- Resultado líquido: resultado após os custos aplicáveis.

## 9.7. Bloqueios e pausa automática

O módulo deverá ser capaz de bloquear novas operações quando um limite for atingido.

Exemplos:

- Limite diário de perda atingido.
- Exposição máxima alcançada.
- Quantidade máxima de operações simultâneas atingida.
- Sequência máxima de perdas alcançada.
- Conta sem autorização válida.
- Dados financeiros indisponíveis ou inconsistentes.

O bloqueio poderá afetar um bot, uma conta ou um cliente, dependendo do escopo do limite violado.

O sistema deverá registrar:

- Motivo do bloqueio.
- Nível afetado.
- Valor observado.
- Limite configurado.
- Data e hora.
- Origem da decisão.
- Condição necessária para desbloqueio.

O desbloqueio automático somente será permitido quando a regra correspondente estiver explicitamente configurada. Bloqueios de segurança e administrativos poderão exigir intervenção autorizada.

## 9.8. Operações simultâneas e concorrência

O controle de risco deverá considerar solicitações concorrentes.

Duas operações autorizadas individualmente não poderão ultrapassar, em conjunto, o limite de exposição.

Para isso, o módulo deverá implementar mecanismos de reserva ou contabilização de exposição antes da execução.

A reserva deverá possuir:

- Identificador único.
- Conta e bot relacionados.
- Valor reservado.
- Data de criação.
- Estado da reserva.
- Referência à solicitação de operação.

A reserva deverá ser confirmada, ajustada ou liberada conforme o resultado da execução.

Em caso de timeout ou resposta incerta da Deriv, o sistema não deverá liberar a exposição automaticamente sem verificar o estado real da operação.

## 9.9. Integração com o módulo de Execução

A Gestão de Risco e a Execução deverão manter responsabilidades separadas.

**Gestão de Risco:**
- Receber solicitações de validação.
- Verificar limites.
- Reservar exposição.
- Autorizar ou rejeitar operações.
- Registrar decisões de risco.

**Execução:**
- Receber solicitações autorizadas.
- Enviar operações à Deriv.
- Controlar requisições e respostas.
- Acompanhar contratos.
- Informar o resultado ao módulo de risco.

O módulo de Execução não deverá aceitar solicitações sem uma autorização válida de risco.

A autorização deverá estar vinculada à solicitação específica, evitando seu reaproveitamento em outra operação.

## 9.10. Operações manuais

Operações iniciadas manualmente pelo cliente deverão seguir exatamente as mesmas validações aplicadas aos robôs.

A origem da solicitação poderá ser identificada como:

- Bot automático.
- Comando manual do cliente.
- Ação administrativa autorizada.

A origem deverá ser registrada para auditoria, mas não poderá permitir que uma operação manual ignore os limites.

## 9.11. Estrutura de dados proposta

Entidades principais:

**risk_profiles**
- id
- owner_type
- owner_id
- name
- configuration
- active
- created_at
- updated_at

**risk_limits**
- id
- profile_id
- limit_type
- limit_value
- period
- scope
- created_at

**risk_exposures**
- id
- deriv_account_id
- bot_id
- exposure_value
- updated_at

**risk_reservations**
- id
- request_id
- deriv_account_id
- bot_id
- reserved_value
- status
- created_at
- expires_at

**risk_events**
- id
- user_id
- deriv_account_id
- bot_id
- event_type
- reason
- observed_value
- configured_limit
- created_at

Os valores monetários deverão utilizar tipos numéricos apropriados, evitando cálculos financeiros com ponto flutuante binário.

A estrutura definitiva será estabelecida durante o projeto do banco de dados.

## 9.12. Segurança e integridade

O módulo deverá garantir:

- Isolamento dos limites por cliente.
- Proteção contra alterações não autorizadas.
- Validação de todas as solicitações.
- Controle de concorrência nas reservas.
- Rastreabilidade das decisões.
- Integridade entre autorização, reserva e execução.
- Bloqueio seguro quando informações essenciais estiverem indisponíveis.

Alterações nos limites deverão gerar eventos de auditoria, identificando o responsável e os valores anteriores e novos.

## 9.13. Testes e critérios de aceitação

O módulo será considerado apto quando os seguintes cenários forem validados:

1. Autorizar operações dentro dos limites.
2. Rejeitar operações que ultrapassem limites.
3. Aplicar corretamente a hierarquia de limites.
4. Calcular perdas e exposição.
5. Bloquear operações ao atingir limites configurados.
6. Impedir que operações manuais ignorem as regras.
7. Controlar operações simultâneas.
8. Evitar reservas duplicadas.
9. Tratar corretamente timeouts e respostas incertas.
10. Liberar ou confirmar reservas conforme o resultado da execução.
11. Garantir isolamento entre clientes e contas.
12. Registrar todas as decisões de risco.
13. Impedir execução sem autorização válida.

## 9.14. Situação atual

| Recurso | Situação |
|---|---|
| Estrutura de gestão de risco | Planejado |
| Perfis e limites | Planejado |
| Validação pré-operação | Planejado |
| Controle de exposição | Planejado |
| Reservas de risco | Planejado |
| Bloqueios automáticos | Planejado |
| Integração com Execução | Planejado |
| Auditoria de risco | Planejado |

O módulo de Gestão de Risco ainda não está implementado.

## 9.15. Decisão arquitetural

A Gestão de Risco será uma etapa obrigatória entre a geração de sinais ou solicitações manuais e o envio de operações à Deriv.

A autorização deverá ser específica para cada solicitação, com controle de exposição e concorrência.

A plataforma deverá adotar comportamento conservador: quando não for possível confirmar que uma operação respeita os limites, ela não deverá ser autorizada.

# Capítulo 10 — Execução de Operações (Execution)

## 10.1. Objetivo do módulo

O módulo de Execução será responsável por transformar solicitações autorizadas em operações efetivamente enviadas à Deriv.

Será o único módulo de negócio responsável por solicitar a abertura de contratos e acompanhar seu ciclo de vida na plataforma Deriv.

Suas responsabilidades incluem:

- Receber solicitações de operações.
- Validar a autorização da Gestão de Risco.
- Consultar propostas de contratos.
- Comprar contratos aprovados.
- Acompanhar contratos abertos.
- Identificar encerramentos e resultados.
- Tratar erros, timeouts e respostas incertas.
- Manter a consistência entre o estado local e o estado informado pela Deriv.
- Registrar todas as operações.

O módulo não deverá decidir quando operar. Essa decisão pertence às Estratégias e aos Bots, enquanto a autorização financeira pertence à Gestão de Risco.

## 10.2. Princípios fundamentais

A implementação deverá seguir estas regras:

- Nenhuma operação será enviada sem autorização válida da Gestão de Risco.
- Operações automáticas e manuais utilizarão o mesmo fluxo.
- Toda solicitação deverá possuir identificador único.
- Toda comunicação deverá ser rastreável.
- Respostas incertas não poderão ser tratadas como falhas definitivas.
- Uma operação não poderá ser enviada novamente sem verificar o estado da solicitação anterior.
- O resultado financeiro deverá ser confirmado com dados da Deriv.
- A execução deverá respeitar o ambiente demo ou real da conta.

## 10.3. Fluxo de execução

O fluxo operacional será:

1. Bot ou interface manual solicita uma operação.
2. O módulo de Execução recebe a solicitação.
3. A Gestão de Risco valida a operação.
4. A Gestão de Risco autoriza e registra a reserva de exposição.
5. O módulo de Execução solicita uma proposta à Deriv.
6. A proposta é validada conforme os parâmetros solicitados.
7. O módulo solicita a compra do contrato.
8. A Deriv retorna a confirmação ou o resultado da solicitação.
9. O módulo registra o contrato e acompanha sua evolução.
10. O encerramento e o resultado financeiro são registrados.
11. A Gestão de Risco recebe a atualização da exposição e do resultado.
12. O Bot recebe o resultado da operação.

O fluxo deverá ser idempotente e rastreável em todas as etapas.

## 10.4. Solicitação de operação

Toda solicitação deverá conter, no mínimo:

- Identificador único da solicitação.
- Cliente.
- Conta Deriv.
- Bot ou origem manual.
- Estratégia relacionada, quando aplicável.
- Ativo.
- Tipo de contrato.
- Direção da operação, quando aplicável.
- Valor ou parâmetros de compra.
- Moeda.
- Duração e unidade de duração, quando aplicáveis.
- Ambiente demo ou real.
- Identificador da autorização de risco.
- Data e hora da solicitação.

Os campos definitivos dependerão dos tipos de contratos efetivamente suportados pela plataforma.

O módulo deverá validar a consistência dos parâmetros antes de enviar qualquer solicitação à Deriv.

## 10.5. Integração com a API Deriv

A integração deverá utilizar os métodos oficiais documentados pela Deriv e os schemas oficiais da API como referência.

Para o fluxo de contratos de opções, os principais comandos incluem:

| Comando | Finalidade |
|---|---|
| `proposal` | Solicitar uma proposta de contrato. |
| `buy` | Comprar um contrato utilizando uma proposta válida. |
| `proposal_open_contract` | Consultar ou acompanhar um contrato aberto. |
| `sell` | Solicitar a venda antecipada, quando permitida. |
| `portfolio` | Consultar contratos e posições da conta. |
| `statement` | Consultar o histórico financeiro da conta. |
| `transaction` | Receber notificações de transações, conforme suporte da API. |

A disponibilidade, os parâmetros e os requisitos de autorização deverão ser verificados para cada tipo de contrato.

Não será implementado um fluxo genérico presumindo que todos os contratos aceitam os mesmos parâmetros ou operações de encerramento.

## 10.6. Controle de propostas

Antes de comprar um contrato, o sistema deverá solicitar uma proposta à Deriv.

A proposta deverá ser analisada para confirmar:

- Ativo.
- Tipo de contrato.
- Direção.
- Valor de compra.
- Preço ou pagamento esperado.
- Prazo de validade.
- Condições e parâmetros solicitados.

A compra deverá utilizar o identificador da proposta retornada pela Deriv.

O sistema não deverá assumir que uma proposta continua válida indefinidamente. Caso esteja expirada ou não corresponda à solicitação original, deverá solicitar uma nova proposta.

## 10.7. Compra de contratos

A compra será realizada somente após:

1. Autorização de risco válida.
2. Confirmação da conta e do ambiente.
3. Validação da proposta.
4. Verificação da validade da solicitação.
5. Verificação de que a operação ainda não foi executada.

Após o envio, o sistema deverá registrar a resposta da Deriv e associar o identificador do contrato à solicitação original.

O identificador retornado pela Deriv será a referência principal para acompanhamento posterior.

## 10.8. Máquina de estados da operação

Cada operação deverá possuir um estado explícito.

| Estado | Descrição |
|---|---|
| Received | Solicitação recebida. |
| RiskPending | Aguardando validação de risco. |
| Rejected | Rejeitada pela Gestão de Risco. |
| ProposalPending | Proposta solicitada. |
| ProposalReceived | Proposta recebida e aguardando validação. |
| BuyPending | Compra enviada, aguardando confirmação. |
| Open | Contrato confirmado e aberto. |
| SellPending | Venda antecipada solicitada. |
| Won | Contrato encerrado com resultado positivo. |
| Lost | Contrato encerrado com resultado negativo. |
| Sold | Contrato vendido antecipadamente. |
| Expired | Contrato encerrado por expiração. |
| Failed | Falha confirmada antes da execução do contrato. |
| Unknown | Estado ainda não confirmado. |

Os estados finais e suas transições deverão considerar os eventos efetivamente retornados pela Deriv.

`Unknown` não deverá ser tratado como `Failed`. Uma solicitação com resultado incerto exigirá reconciliação antes de qualquer tentativa de repetição.

## 10.9. Tratamento de timeout e falhas

Uma das principais responsabilidades do módulo será tratar situações em que a comunicação não permita confirmar se a operação foi executada.

Exemplo:

1. O sistema envia uma solicitação de compra.
2. A Deriv processa a solicitação.
3. A conexão é interrompida antes da resposta chegar.
4. O sistema não sabe se o contrato foi comprado.

Nesse caso, o sistema deverá:

- Marcar a solicitação como `Unknown`.
- Impedir uma nova compra automática da mesma solicitação.
- Consultar o estado da conta e os contratos disponíveis.
- Utilizar os identificadores disponíveis para reconciliar a operação.
- Confirmar se o contrato foi aberto.
- Somente permitir uma nova tentativa após resolver a incerteza.

Não deverá existir repetição automática indiscriminada de comandos financeiros.

## 10.10. Acompanhamento de contratos

Após a confirmação da compra, o módulo deverá acompanhar o contrato até seu encerramento.

O acompanhamento deverá considerar:

- Identificador do contrato.
- Estado atual.
- Ativo.
- Tipo de contrato.
- Preço de compra.
- Valor de pagamento.
- Resultado informado.
- Horário de abertura.
- Horário de encerramento.
- Possibilidade de venda antecipada.
- Eventos recebidos da Deriv.

Sempre que possível, o acompanhamento deverá utilizar assinaturas de atualização da API, evitando consultas repetitivas desnecessárias.

O estado local deverá ser reconciliado periodicamente com os dados da Deriv.

## 10.11. Venda antecipada e encerramento

A venda antecipada somente poderá ser solicitada quando:

- O contrato permitir essa operação.
- A Deriv informar que a venda está disponível.
- A solicitação estiver autorizada.
- O contrato ainda estiver aberto.
- Não existir outra solicitação de venda pendente.

A plataforma não deverá presumir que todos os contratos podem ser vendidos antecipadamente.

Caso a venda não esteja disponível, o contrato deverá continuar sendo acompanhado até seu encerramento natural, quando aplicável.

## 10.12. Reconciliação financeira

O módulo deverá manter os registros locais consistentes com as informações retornadas pela Deriv.

Deverão ser conciliados:

- Contratos comprados.
- Contratos ainda abertos.
- Contratos encerrados.
- Vendas antecipadas.
- Valores de compra.
- Pagamentos.
- Lucros e perdas.
- Transações relacionadas.

Os dados locais serão utilizados para histórico, relatórios e monitoramento, mas o resultado financeiro confirmado pela Deriv será a referência para a conciliação.

O sistema deverá identificar divergências e gerar eventos para investigação.

## 10.13. Integração com outros módulos

| Módulo | Integração |
|---|---|
| Bots | Receber solicitações automáticas e devolver resultados. |
| Estratégias | Receber a referência do sinal que originou a operação. |
| Gestão de Risco | Solicitar autorização e atualizar exposição e resultados. |
| Deriv Integration | Enviar comandos e receber respostas da API. |
| Usuários e Contas | Identificar conta, proprietário e autorização. |
| Market Data | Consultar dados de referência, quando necessários. |
| Auditoria e Monitoramento | Registrar solicitações, respostas, erros e transições. |

O módulo de Execução deverá utilizar a camada central de integração com a Deriv, sem criar conexões independentes e descontroladas para cada operação.

## 10.14. Estrutura de dados proposta

Entidades principais:

**trade_requests**
- id
- user_id
- deriv_account_id
- bot_id
- source
- asset_symbol
- contract_type
- direction
- requested_amount
- currency
- risk_authorization_id
- status
- created_at
- updated_at

**trade_proposals**
- id
- trade_request_id
- deriv_proposal_id
- proposal_data
- expires_at
- status
- created_at

**contracts**
- id
- trade_request_id
- deriv_contract_id
- deriv_account_id
- asset_symbol
- contract_type
- buy_price
- payout
- profit_loss
- status
- opened_at
- closed_at

**execution_events**
- id
- trade_request_id
- contract_id
- event_type
- request_data
- response_data
- created_at

**execution_reconciliation**
- id
- deriv_account_id
- reconciliation_type
- status
- details
- started_at
- completed_at

Os valores financeiros deverão utilizar tipos numéricos apropriados. Tokens, senhas e credenciais não deverão ser armazenados nessas entidades.

A estrutura definitiva será definida durante o projeto do banco de dados.

## 10.15. Segurança e integridade

O módulo deverá garantir:

- Autorização válida antes de qualquer compra.
- Isolamento entre clientes e contas.
- Separação rigorosa entre demo e real.
- Proteção contra operações duplicadas.
- Registro das solicitações e respostas.
- Proteção de dados sensíveis.
- Controle de acesso às operações manuais.
- Rastreabilidade pelo identificador local e pelo identificador Deriv.
- Reconciliação de operações com estado incerto.

O sistema deverá considerar que uma falha de conexão não significa necessariamente que uma operação financeira falhou.

## 10.16. Testes e critérios de aceitação

O módulo será considerado apto quando os seguintes cenários forem validados:

1. Receber solicitações de bots e comandos manuais.
2. Impedir operações sem autorização de risco.
3. Solicitar e validar propostas.
4. Comprar contratos utilizando propostas válidas.
5. Registrar corretamente os identificadores Deriv.
6. Acompanhar contratos até o encerramento.
7. Tratar vendas antecipadas quando permitidas.
8. Impedir compras duplicadas.
9. Tratar timeouts e respostas incertas.
10. Reconciliar contratos com os dados da Deriv.
11. Atualizar corretamente a Gestão de Risco.
12. Isolar operações entre clientes.
13. Garantir separação entre contas demo e reais.
14. Registrar todos os eventos relevantes.

Os testes deverão utilizar mocks e ambiente demo sempre que possível, sem depender de operações reais para validar os fluxos comuns.

## 10.17. Situação atual

| Recurso | Situação |
|---|---|
| Recebimento de solicitações | Planejado |
| Validação de risco | Planejado |
| Consulta de propostas | Planejado |
| Compra de contratos | Planejado |
| Acompanhamento de contratos | Planejado |
| Venda antecipada | Planejado |
| Tratamento de timeout | Planejado |
| Reconciliação financeira | Planejado |
| Histórico de operações | Planejado |

O módulo de Execução ainda não está implementado.

## 10.18. Decisão arquitetural

O módulo de Execução será o único responsável pelo ciclo operacional dos contratos negociados pela plataforma.

Toda operação deverá possuir um identificador local, autorização de risco e rastreabilidade até o contrato correspondente na Deriv.

O sistema deverá priorizar a integridade financeira em vez de tentar manter disponibilidade a qualquer custo. Em caso de incerteza, deverá reconciliar o estado antes de repetir uma operação.

# Capítulo 11 — Planos, Assinaturas e Controle de Acesso

## 11.1. Objetivo do módulo

O módulo será responsável por controlar o direito de cada cliente de utilizar a plataforma e seus robôs.

Deverá administrar:

- Períodos de teste.
- Planos disponíveis.
- Assinaturas.
- Vigência e vencimento.
- Permissões de utilização.
- Limites de uso.
- Bloqueios e reativações.
- Histórico de alterações comerciais.
- Controle de acesso aos recursos da plataforma.

A autorização da plataforma será independente da autorização concedida pelo cliente à Deriv.

Um cliente poderá continuar acessando sua conta diretamente na Deriv mesmo quando perder o acesso aos serviços da plataforma.

## 11.2. Princípios fundamentais

1. A conta Deriv pertence ao cliente e permanece sob seu controle.
2. A plataforma não deverá custodiar fundos dos clientes.
3. O acesso aos robôs dependerá de uma autorização válida da plataforma.
4. A autorização Deriv será verificada separadamente.
5. O período de teste será uma regra comercial da plataforma.
6. O encerramento da assinatura não deverá excluir a conta Deriv do cliente.
7. O histórico financeiro e operacional deverá ser preservado conforme as políticas de retenção.
8. Nenhuma cobrança deverá ser presumida sem integração e confirmação do meio de pagamento.

## 11.3. Período de teste de 7 dias

Cada novo cliente elegível poderá receber um período inicial de avaliação de 7 dias.

Durante esse período, o cliente poderá utilizar os recursos definidos para o plano de teste.

O sistema deverá registrar:

- Cliente.
- Data e hora de início.
- Data e hora de encerramento.
- Plano de avaliação.
- Estado do período de teste.
- Recursos disponíveis.
- Data de eventual conversão para plano pago.

O início do teste deverá seguir uma regra comercial única e documentada. A recomendação é iniciar a contagem quando o cliente ativar efetivamente o período de avaliação, e não simplesmente quando criar uma conta na plataforma.

O sistema deverá utilizar datas e horários consistentes, preferencialmente armazenados em UTC.

## 11.4. Estados de acesso

O acesso do cliente deverá possuir estados próprios.

| Estado | Descrição |
|---|---|
| Trial | Cliente em período de avaliação. |
| Active | Plano válido e acesso liberado. |
| PastDue | Pagamento vencido ou pendente, conforme regra comercial. |
| Expired | Período de teste ou assinatura encerrado. |
| Suspended | Acesso suspenso administrativamente ou por regra de segurança. |
| Cancelled | Assinatura cancelada. |
| Pending | Aguardando ativação ou confirmação. |

O estado comercial não deverá ser confundido com o estado de conexão ou autorização da conta Deriv.

## 11.5. Planos e recursos

A plataforma deverá permitir a criação de diferentes planos comerciais.

Cada plano poderá definir:

- Nome.
- Descrição.
- Preço.
- Moeda.
- Periodicidade.
- Quantidade máxima de bots.
- Quantidade máxima de contas Deriv.
- Ativos permitidos.
- Estratégias disponíveis.
- Recursos habilitados.
- Limites operacionais.
- Condições do período de teste.

Os limites comerciais não poderão substituir nem ampliar os limites de segurança da Gestão de Risco.

A estrutura deverá permitir alterar os planos sem modificar a lógica central dos robôs.

## 11.6. Controle de permissões

O sistema deverá validar o acesso aos recursos antes de permitir sua utilização.

Exemplos:

- Criar bot.
- Iniciar bot.
- Utilizar determinada estratégia.
- Conectar conta Deriv.
- Operar em ambiente real.
- Acessar relatórios.
- Utilizar funcionalidades avançadas.

As permissões deverão ser avaliadas no backend. Ocultar funcionalidades na interface não será considerado mecanismo suficiente de segurança.

## 11.7. Encerramento do período de teste

Ao terminar os 7 dias, o sistema deverá verificar se o cliente possui uma assinatura válida.

Caso não possua:

1. Bloquear a inicialização de novos bots.
2. Impedir novas operações pela plataforma.
3. Interromper a geração de novas solicitações de execução.
4. Registrar o encerramento do período de teste.
5. Informar o cliente sobre a necessidade de contratar um plano.
6. Preservar os dados e o histórico do cliente.

Bots em execução deverão ser tratados de forma controlada.

O sistema deverá bloquear novas operações e encerrar as sessões dos bots. Contratos já abertos deverão continuar sendo monitorados até seu encerramento ou até que exista um procedimento autorizado de tratamento.

O encerramento do acesso não deverá provocar perda de controle sobre operações financeiras que já tenham sido enviadas à Deriv.

## 11.8. Cancelamento e suspensão

O cliente poderá cancelar sua assinatura conforme as condições comerciais estabelecidas.

O sistema deverá distinguir:

- Cancelamento imediato.
- Cancelamento ao final do período já pago.
- Suspensão temporária.
- Expiração por falta de renovação.

O comportamento deverá respeitar as condições informadas ao cliente e as regras do meio de pagamento utilizado.

Uma suspensão administrativa também deverá registrar seu motivo e o responsável pela decisão.

## 11.9. Separação entre plataforma e Deriv

A autorização para utilizar a plataforma e a autorização para acessar a conta Deriv serão independentes.

| Situação | Consequência |
|---|---|
| Plano ativo e autorização Deriv válida | Recursos permitidos poderão ser utilizados. |
| Plano expirado e autorização Deriv válida | Cliente mantém acesso direto à Deriv, mas perde acesso aos robôs da plataforma. |
| Plano ativo e autorização Deriv revogada | Robôs não poderão operar na conta afetada. |
| Plano expirado e autorização Deriv revogada | Acesso aos robôs bloqueado; conta Deriv continua sob controle do cliente. |
| Plano suspenso | Recursos da plataforma bloqueados conforme a política de suspensão. |

O módulo não deverá revogar, alterar ou interferir na propriedade da conta Deriv do cliente.

## 11.10. Integração com pagamentos

A integração com um provedor de pagamentos poderá ser implementada para:

- Criar cobranças.
- Confirmar pagamentos.
- Processar renovações.
- Identificar pagamentos recusados.
- Processar reembolsos.
- Receber notificações de eventos.
- Atualizar o estado da assinatura.

As notificações deverão ser autenticadas e processadas de maneira idempotente.

O estado da assinatura não deverá ser alterado apenas porque uma solicitação de pagamento foi enviada. A confirmação deverá depender do retorno confiável do provedor.

O provedor de pagamentos ainda deverá ser definido.

## 11.11. Estrutura de dados proposta

Entidades principais:

**plans**
- id
- name
- description
- price
- currency
- billing_period
- active
- created_at
- updated_at

**plan_features**
- id
- plan_id
- feature_key
- feature_value

**subscriptions**
- id
- user_id
- plan_id
- status
- started_at
- current_period_start
- current_period_end
- cancelled_at
- created_at
- updated_at

**trials**
- id
- user_id
- started_at
- expires_at
- status
- converted_at

**payment_records**
- id
- user_id
- subscription_id
- provider
- external_payment_id
- amount
- currency
- status
- created_at
- updated_at

**access_events**
- id
- user_id
- event_type
- previous_status
- new_status
- reason
- created_at

A estrutura deverá permitir consultar o histórico de assinaturas sem perder informações de períodos anteriores.

## 11.12. Segurança e integridade

O módulo deverá garantir:

- Validação de permissões no backend.
- Isolamento entre clientes.
- Proteção contra ativação indevida de planos.
- Processamento idempotente de eventos de pagamento.
- Registro de alterações comerciais.
- Controle de acesso administrativo.
- Preservação dos dados após expiração.
- Separação entre autorização da plataforma e autorização Deriv.

Nenhuma informação de pagamento ou assinatura deverá ser considerada válida apenas com base em dados enviados pelo navegador do cliente.

## 11.13. Testes e critérios de aceitação

O módulo será considerado apto quando os seguintes cenários forem validados:

1. Criar e ativar um período de teste de 7 dias.
2. Calcular corretamente o vencimento.
3. Liberar recursos permitidos durante o teste.
4. Bloquear recursos não incluídos no plano.
5. Converter um cliente de teste para assinatura paga.
6. Tratar expiração e cancelamento.
7. Processar notificações de pagamento sem duplicidade.
8. Impedir acesso aos robôs quando o plano não estiver válido.
9. Preservar o histórico do cliente.
10. Encerrar bots de forma controlada.
11. Garantir que contratos abertos continuem sob acompanhamento.
12. Preservar o acesso direto do cliente à sua conta Deriv.
13. Garantir isolamento entre clientes.

## 11.14. Situação atual

| Recurso | Situação |
|---|---|
| Cadastro de planos | Planejado |
| Período de teste de 7 dias | Planejado |
| Assinaturas | Planejado |
| Controle de permissões | Planejado |
| Expiração e cancelamento | Planejado |
| Integração com pagamentos | Planejado |
| Bloqueio controlado de bots | Planejado |
| Histórico comercial | Planejado |

O módulo de Planos, Assinaturas e Controle de Acesso ainda não está implementado.

## 11.15. Decisão arquitetural

O controle de acesso comercial será independente da integração com a Deriv.

O período de teste terá duração de 7 dias, e a continuidade dependerá de uma assinatura válida ou de outra condição comercial autorizada.

A expiração deverá bloquear o uso da plataforma, sem interferir na conta Deriv ou nos fundos do cliente.

A interrupção dos bots deverá ser coordenada com os módulos de Bots e Execução, preservando o acompanhamento de contratos já abertos.

# Capítulo 12 — Parceiros, Afiliados e Markup da Deriv

## 12.1. Objetivo do módulo

O módulo será responsável por administrar e acompanhar as receitas da plataforma provenientes dos programas comerciais da Deriv.

O modelo de negócio utilizará duas fontes de receita:

1. **Programa de Parceiros/Afiliados:** comissões provenientes de clientes indicados à Deriv e aprovados no programa.
2. **Markup da aplicação:** comissão gerada em contratos elegíveis executados pelos clientes através da aplicação integrada à Deriv API.

Essas receitas deverão ser controladas separadamente, pois possuem mecanismos de atribuição, cálculo e apuração diferentes.

O módulo também deverá manter informações que permitam acompanhar o desempenho comercial da plataforma e conciliar os valores informados pela Deriv.

## 12.2. Princípios fundamentais

- Utilizar os mecanismos oficiais disponibilizados pela Deriv.
- Não presumir que todos os clientes ou contratos geram comissão.
- Não contabilizar receitas estimadas como receitas confirmadas.
- Manter a atribuição de clientes corretamente identificada.
- Separar receitas de afiliados e receitas de markup.
- Preservar o histórico de apuração.
- Não custodiar fundos dos clientes.
- Não incentivar operações com o objetivo de aumentar comissões.
- Não prometer rentabilidade ou resultados financeiros aos clientes.
- Respeitar os termos comerciais vigentes da Deriv.

## 12.3. Programa de Parceiros e Afiliados

A primeira fonte de receita será a participação no programa de parceiros da Deriv.

O objetivo será atrair novos clientes por meio dos links e mecanismos oficiais de indicação disponibilizados pela Deriv.

### Fluxo de indicação

1. A plataforma disponibiliza o link oficial de indicação.
2. O visitante acessa o link.
3. O visitante realiza seu cadastro na Deriv.
4. A Deriv identifica a origem da indicação.
5. A Deriv avalia e aprova a atribuição do cliente.
6. O cliente passa a utilizar sua própria conta Deriv.
7. As transações elegíveis poderão gerar comissões conforme as regras do programa.
8. A plataforma acompanha os resultados pelos mecanismos oficiais disponibilizados.

A plataforma deverá armazenar informações suficientes para relacionar o cliente cadastrado internamente à identificação correspondente na Deriv, quando permitido.

### Regras de atribuição

A atribuição de clientes dependerá dos mecanismos oficiais da Deriv.

O simples cadastro de um usuário na plataforma não garantirá que ele será reconhecido como cliente indicado.

O sistema deverá permitir identificar:

- Cliente da plataforma.
- Identificador de cliente na Deriv.
- Data de indicação.
- Origem da indicação.
- Estado da atribuição.
- Data de confirmação.
- Eventuais divergências.

A plataforma deverá oferecer orientação clara ao usuário para realizar o cadastro pelo canal correto.

Não deverá tentar modificar artificialmente a atribuição de clientes já existentes.

## 12.4. Regras comerciais do programa de afiliados

As comissões dependerão das condições comerciais vigentes e da elegibilidade das operações.

O módulo deverá considerar:

- Clientes efetivamente aprovados como indicações.
- Produtos e plataformas elegíveis.
- Operações concluídas.
- Estrutura de comissão aplicável.
- Ajustes e estornos.
- Contestação de pagamentos.
- Alterações de elegibilidade.
- Períodos de apuração.

As taxas de comissão não deverão ser fixadas permanentemente no código.

A Deriv poderá alterar as condições, percentuais, critérios e programas de parceria.

A plataforma deverá tratar os valores apresentados pela Deriv como referência para sua apuração, preservando os registros históricos.

## 12.5. Markup da aplicação Deriv API

A segunda fonte de receita será o markup da aplicação.

O markup é uma margem comercial aplicada aos contratos elegíveis executados pelos usuários através da aplicação.

A documentação oficial da Deriv informa a possibilidade de obter até 3% de comissão de markup por contrato, conforme as condições aplicáveis.

### Funcionamento

1. O cliente utiliza a plataforma para solicitar uma operação.
2. O módulo de Execução solicita uma proposta à Deriv.
3. O fluxo utiliza o mecanismo de markup autorizado para a aplicação.
4. A Deriv apresenta as condições do contrato considerando o markup.
5. O cliente decide se deseja executar a operação.
6. A Deriv processa o contrato.
7. A comissão de markup é apurada conforme as regras da Deriv.

### Impacto para o cliente

O markup influencia o pagamento potencial do contrato.

Quanto maior o markup, menor poderá ser o pagamento potencial recebido pelo cliente em uma operação vencedora.

Por isso:

- O percentual deverá ser transparente.
- O cliente deverá ter acesso às informações aplicáveis.
- A plataforma não deverá ocultar o impacto do markup.
- A configuração deverá respeitar os limites e condições autorizados pela Deriv.
- A aplicação deverá evitar alterações não autorizadas no percentual.

A taxa máxima de 3% não deverá ser interpretada como garantia de comissão em qualquer contrato.

A elegibilidade dependerá do tipo de contrato, da aplicação registrada e das regras vigentes da Deriv.

## 12.6. Configuração do markup

A plataforma deverá possuir uma configuração centralizada de markup.

Parâmetros previstos:

- Percentual configurado.
- Aplicação Deriv relacionada.
- Estado de ativação.
- Data de início.
- Data de alteração.
- Condições de aplicação.
- Histórico de versões.

O percentual não deverá ser definido individualmente por cada bot.

A configuração deverá ser administrada centralmente, respeitando as permissões e condições comerciais concedidas pela Deriv.

Qualquer alteração deverá gerar um evento de auditoria.

A implementação deverá ocorrer somente após confirmação de que a aplicação e a conta possuem autorização para utilizar o mecanismo de markup.

## 12.7. Integração com a API de Parceiros

A documentação da Deriv disponibiliza uma API REST para consulta de informações do parceiro.

Entre os recursos documentados estão:

| Recurso | Finalidade |
|---|---|
| Analytics Overview | Consultar resumo de desempenho e comissões. |
| Client Tags Check | Verificar a associação de clientes ao parceiro. |
| Markup Statistics | Consultar estatísticas de markup das aplicações. |

A documentação informa que esses recursos utilizam autenticação OAuth2 com o escopo `application_read`.

Alguns endpoints são identificados como Beta e poderão sofrer alterações.

A integração deverá:

- Consultar os dados de forma periódica.
- Armazenar os resultados históricos.
- Controlar erros e indisponibilidade.
- Evitar consultas desnecessárias.
- Registrar a data da última sincronização.
- Permitir conciliação com os relatórios oficiais.

A implementação deverá utilizar a documentação vigente e os mecanismos oficiais de autenticação.

## 12.8. Separação das fontes de receita

As receitas deverão possuir registros e relatórios independentes.

| Característica | Parceiros/Afiliados | Markup |
|---|---|---|
| Origem | Indicação de clientes | Contratos executados pela aplicação |
| Atribuição | Identificação do cliente indicado | Aplicação registrada |
| Base de cálculo | Regras do programa de parceiros | Markup aplicado ao contrato elegível |
| Apuração | Relatórios de parceiros | Estatísticas de markup |
| Autorização | Participação no programa | Aplicação habilitada para markup |

A plataforma poderá apresentar uma visão consolidada, mas deverá permitir consultar cada fonte individualmente.

## 12.9. Conciliação de receitas

O sistema deverá distinguir três situações:

**Receita estimada:** valor calculado internamente, ainda não confirmado pela Deriv.

**Receita reportada:** valor informado pelos sistemas oficiais da Deriv.

**Receita recebida:** valor efetivamente creditado ou pago.

A conciliação deverá identificar:

- Período de referência.
- Fonte da receita.
- Aplicação ou parceiro relacionado.
- Valor informado.
- Moeda.
- Estado da apuração.
- Data de atualização.
- Ajustes.
- Divergências.

O sistema não deverá somar receitas estimadas e confirmadas como se fossem valores independentes.

Correções e ajustes deverão preservar o histórico, sem sobrescrever registros anteriores.

## 12.10. Estrutura de dados proposta

Entidades principais:

**partner_profiles**
- id
- deriv_partner_id
- partner_type
- status
- created_at
- updated_at

**partner_referrals**
- id
- user_id
- deriv_client_id
- referral_source
- attribution_status
- referred_at
- confirmed_at

**markup_configs**
- id
- deriv_app_id
- markup_percentage
- active
- valid_from
- valid_until
- created_at

**partner_commissions**
- id
- deriv_client_id
- period
- commission_type
- amount
- currency
- status
- reported_at

**markup_commissions**
- id
- deriv_app_id
- deriv_contract_id
- period
- amount
- currency
- status
- reported_at

**revenue_reconciliations**
- id
- revenue_source
- reference_period
- reported_amount
- received_amount
- currency
- status
- reconciled_at

**partner_events**
- id
- event_type
- reference_id
- details
- created_at

Os campos definitivos deverão ser ajustados conforme os dados efetivamente disponibilizados pelas APIs e relatórios da Deriv.

## 12.11. Segurança e conformidade

O módulo deverá garantir:

- Proteção dos dados de clientes e parceiros.
- Acesso restrito às informações comerciais.
- Uso seguro das credenciais OAuth2.
- Não exposição de tokens em logs.
- Controle de alterações no markup.
- Rastreabilidade das receitas.
- Respeito aos termos do programa de parceiros.
- Transparência sobre o impacto do markup.
- Separação entre recursos comerciais e execução operacional.

A plataforma não deverá:

- Receber ou custodiar fundos dos clientes.
- Operar contas em nome dos clientes fora das autorizações concedidas.
- Incentivar depósitos ou operações para aumentar comissões.
- Garantir lucros ou limitar perdas.
- Manipular indicações ou atribuições.
- Prometer comissões ainda não confirmadas.

A participação nos programas dependerá da aprovação e manutenção da elegibilidade pela Deriv.

## 12.12. Testes e critérios de aceitação

O módulo será considerado apto quando os seguintes cenários forem validados:

1. Registrar corretamente a identificação de clientes indicados.
2. Consultar a atribuição de clientes pela API de parceiros.
3. Identificar clientes sem atribuição confirmada.
4. Consultar estatísticas de markup.
5. Aplicar somente configurações de markup autorizadas.
6. Manter histórico das alterações de percentual.
7. Separar receitas de afiliados e markup.
8. Registrar receitas estimadas, reportadas e recebidas.
9. Conciliar períodos e valores.
10. Tratar ajustes e estornos.
11. Impedir duplicação de registros durante sincronizações.
12. Proteger credenciais e dados comerciais.
13. Gerar relatórios consolidados e separados.

## 12.13. Situação atual

| Recurso | Situação |
|---|---|
| Participação no programa de parceiros | Planejado / elegibilidade a confirmar |
| Links de indicação | Planejado |
| Atribuição de clientes | Planejado |
| Integração com Partners API | Planejado |
| Aplicação de markup | Planejado / habilitação a confirmar |
| Configuração central de markup | Planejado |
| Consulta de estatísticas | Planejado |
| Conciliação de receitas | Planejado |
| Relatórios comerciais | Planejado |

A integração comercial ainda não está implementada.

A elegibilidade da conta, da aplicação e dos produtos deverá ser confirmada com a Deriv antes da implementação definitiva.

## 12.14. Decisões arquiteturais

A plataforma utilizará duas fontes independentes de receita:

1. Programa de parceiros e afiliados.
2. Markup da aplicação Deriv API.

O módulo comercial será independente dos módulos de Bots, Gestão de Risco e Execução.

A aplicação do markup ocorrerá no fluxo de negociação, mas sua configuração e apuração serão responsabilidades deste módulo e da integração Deriv correspondente.

A receita de afiliados será apurada com base nos clientes efetivamente atribuídos e nas transações elegíveis reconhecidas pela Deriv.

Nenhuma receita deverá ser considerada garantida antes da confirmação oficial.

## 12.15. Pendências antes da implementação

Antes de desenvolver este módulo, será necessário:

1. Confirmar a aprovação e as condições da conta no programa de parceiros.
2. Confirmar o processo de registro da aplicação para markup.
3. Verificar quais contratos e produtos são elegíveis.
4. Confirmar o fluxo técnico de aplicação do markup.
5. Validar os escopos OAuth2 necessários.
6. Confirmar os mecanismos de atribuição de clientes.
7. Verificar os relatórios e a frequência de atualização das comissões.
8. Definir a política de conciliação financeira e contábil.

# Capítulo 13 — Auditoria, Logs e Monitoramento

## 13.1. Objetivo do módulo

O módulo será responsável por registrar, monitorar e disponibilizar informações sobre o funcionamento da plataforma.

Deverá permitir identificar:

- Quem realizou determinada ação.
- Quando a ação aconteceu.
- Qual recurso foi afetado.
- Qual era o estado anterior.
- Qual foi o resultado.
- Se ocorreu algum erro.
- Qual foi a origem da solicitação.

A auditoria deverá permitir reconstruir o histórico de uma operação desde a geração do sinal até sua confirmação ou encerramento na Deriv.

O monitoramento deverá permitir identificar falhas técnicas, degradação de desempenho e situações que possam comprometer a operação dos robôs.

## 13.2. Princípios fundamentais

- Registrar eventos importantes de forma estruturada.
- Separar auditoria de logs técnicos.
- Preservar a integridade dos registros.
- Utilizar identificadores para correlacionar eventos.
- Não registrar senhas, tokens ou credenciais.
- Garantir isolamento das informações entre clientes.
- Monitorar os serviços de forma contínua.
- Gerar alertas para condições críticas.
- Evitar que falhas de monitoramento interrompam indevidamente o processamento principal.

## 13.3. Tipos de registros

A plataforma deverá trabalhar com três categorias principais.

### 13.3.1. Auditoria

Registros permanentes de ações relevantes para segurança, controle e rastreabilidade.

Exemplos:

- Cadastro e alteração de usuários.
- Vinculação e desvinculação de contas Deriv.
- Alterações de autorização.
- Criação e alteração de bots.
- Início, pausa e encerramento de bots.
- Alterações de estratégias e parâmetros.
- Alterações de limites de risco.
- Autorizações e rejeições de operações.
- Solicitações de compra e venda.
- Alterações de planos e assinaturas.
- Alterações no markup.
- Ações administrativas.

### 13.3.2. Logs técnicos

Registros destinados à investigação de problemas de software e infraestrutura.

Exemplos:

- Inicialização de serviços.
- Conexões e desconexões WebSocket.
- Reconexões.
- Erros de comunicação.
- Exceções.
- Falhas de banco de dados.
- Processamento de filas.
- Tempo de execução de tarefas.
- Falhas em integrações externas.

### 13.3.3. Métricas e monitoramento

Informações quantitativas sobre o funcionamento da plataforma.

Exemplos:

- Número de bots ativos.
- Quantidade de contas conectadas.
- Quantidade de operações.
- Latência das solicitações.
- Taxa de erros.
- Tamanho das filas.
- Tempo de persistência dos dados.
- Consumo de recursos.
- Estado das conexões com a Deriv.

## 13.4. Identificação e correlação de eventos

Todo fluxo operacional deverá utilizar identificadores que permitam relacionar os eventos.

Identificadores previstos:

- `request_id`: solicitação recebida pela API.
- `correlation_id`: identificador comum entre serviços envolvidos.
- `user_id`: cliente responsável.
- `deriv_account_id`: conta relacionada.
- `bot_id`: robô relacionado.
- `bot_run_id`: sessão de execução.
- `signal_id`: sinal que originou a operação.
- `trade_request_id`: solicitação de operação.
- `deriv_contract_id`: contrato correspondente na Deriv.

Exemplo de rastreamento:

1. Estratégia gera um sinal.
2. Bot recebe o sinal.
3. Gestão de Risco valida a operação.
4. Execução solicita uma proposta.
5. Deriv retorna a proposta.
6. Execução solicita a compra.
7. Deriv confirma o contrato.
8. Contrato é acompanhado.
9. Resultado é registrado.
10. Gestão de Risco atualiza a exposição.

Todos esses eventos deverão possuir referências suficientes para reconstruir o fluxo.

## 13.5. Estrutura dos logs

Os logs deverão ser estruturados, preferencialmente em formato JSON.

Campos previstos:

- timestamp
- level
- service
- environment
- event_type
- message
- request_id
- correlation_id
- user_id, quando aplicável
- bot_id, quando aplicável
- duration_ms, quando aplicável
- error_code, quando aplicável
- details

Os níveis de severidade serão:

| Nível | Utilização |
|---|---|
| DEBUG | Informações detalhadas para desenvolvimento. |
| INFO | Eventos normais de funcionamento. |
| WARNING | Situações inesperadas que não interrompem o serviço. |
| ERROR | Falhas que impedem uma operação ou tarefa. |
| CRITICAL | Falhas que comprometem serviços essenciais ou a segurança operacional. |

Em produção, o nível de log deverá ser configurável.

## 13.6. Eventos de auditoria

Os registros de auditoria deverão conter:

- Identificador do evento.
- Tipo de evento.
- Usuário ou serviço responsável.
- Recurso afetado.
- Identificador do recurso.
- Data e hora.
- Origem da ação.
- Estado anterior, quando aplicável.
- Estado posterior, quando aplicável.
- Motivo ou justificativa.
- Identificador de correlação.

Os registros deverão ser protegidos contra alterações não autorizadas.

Uma correção de informação deverá gerar um novo evento, preservando o histórico original.

## 13.7. Monitoramento da integração Deriv

A conexão com a Deriv será um dos componentes mais importantes a monitorar.

O sistema deverá acompanhar:

- Estado da conexão WebSocket.
- Tempo de conexão.
- Frequência de desconexões.
- Quantidade de reconexões.
- Tempo de resposta.
- Erros retornados pela API.
- Solicitações pendentes.
- Assinaturas ativas.
- Falhas de autenticação.
- Estado das conexões públicas e privadas.

Deverá existir distinção entre indisponibilidade da Deriv, falha de rede local e falha interna da plataforma, sempre que possível.

## 13.8. Monitoramento de Market Data

O módulo deverá acompanhar:

- Último dado recebido por ativo.
- Atraso entre recebimento e persistência.
- Quantidade de candles processados.
- Quantidade de candles persistidos.
- Falhas de recuperação histórica.
- Tamanho da fila de persistência.
- Tempo de processamento em lote.
- Estado de cada assinatura.
- Intervalos sem dados.

A ausência de dados não deverá ser interpretada automaticamente como preço zero ou como candle válido.

Quando houver atraso ou interrupção relevante, o sistema deverá registrar o evento e executar os procedimentos de recuperação definidos pelo módulo de Market Data.

## 13.9. Monitoramento dos bots e operações

O sistema deverá acompanhar:

- Bots em execução.
- Bots pausados.
- Bots bloqueados.
- Bots com erro.
- Sessões de execução.
- Sinais recebidos.
- Operações solicitadas.
- Operações rejeitadas.
- Contratos abertos.
- Contratos encerrados.
- Operações com estado desconhecido.
- Tempo entre sinal e solicitação de operação.
- Tempo entre solicitação e confirmação da Deriv.

Operações com estado desconhecido deverão gerar alerta e permanecer sob acompanhamento até a reconciliação.

## 13.10. Alertas

O sistema deverá possuir mecanismos de alerta para eventos relevantes.

Exemplos:

| Evento | Severidade |
|---|---|
| Deriv desconectada | WARNING ou CRITICAL, conforme impacto |
| Falha de autenticação | WARNING |
| Falha persistente de reconexão | CRITICAL |
| Atraso elevado em Market Data | WARNING |
| Falha de persistência de candles | CRITICAL |
| Bot interrompido inesperadamente | WARNING |
| Limite de risco atingido | WARNING |
| Operação com estado desconhecido | CRITICAL |
| Falha de reconciliação financeira | CRITICAL |
| Banco de dados indisponível | CRITICAL |

Os alertas deverão conter informações suficientes para investigação, sem expor credenciais ou dados sensíveis.

Os canais de notificação poderão incluir:

- Painel administrativo.
- Notificações internas.
- E-mail.
- Integrações externas de monitoramento.

A escolha dos canais será definida posteriormente.

## 13.11. Métricas de desempenho

A plataforma deverá acompanhar indicadores técnicos e operacionais.

### Infraestrutura

- CPU.
- Memória.
- Disco.
- Conexões com PostgreSQL.
- Latência de consultas.
- Estado dos containers.

### Aplicação

- Requisições por segundo.
- Tempo de resposta da API.
- Taxa de erros.
- Exceções.
- Tarefas pendentes.
- Consumo de recursos por serviço.

### Operação

- Quantidade de bots ativos.
- Operações por período.
- Taxa de rejeição por risco.
- Tempo de execução.
- Quantidade de contratos abertos.
- Divergências de reconciliação.

As métricas deverão permitir identificar gargalos antes que provoquem falhas operacionais.

## 13.12. Persistência e retenção

Os registros deverão possuir políticas de retenção diferentes conforme sua finalidade.

| Informação | Política |
|---|---|
| Auditoria | Retenção prolongada, conforme requisitos legais e comerciais. |
| Logs técnicos | Retenção configurável e rotação periódica. |
| Métricas | Retenção conforme necessidade de análise histórica. |
| Eventos de operação | Preservação conforme política de histórico financeiro e operacional. |
| Alertas | Retenção suficiente para investigação e acompanhamento. |

O volume de logs deverá ser controlado para evitar crescimento desnecessário do banco de dados.

Logs técnicos de alta frequência não deverão competir com a persistência de dados financeiros e de mercado.

A estratégia poderá utilizar armazenamento especializado para logs e métricas quando o volume justificar.

## 13.13. Segurança e privacidade

O módulo deverá garantir:

- Nenhum token de autorização em logs.
- Nenhuma senha em logs.
- Proteção de dados pessoais.
- Acesso administrativo controlado.
- Isolamento dos registros por cliente.
- Proteção contra alterações não autorizadas.
- Registro das consultas administrativas relevantes.
- Mascaramento de dados sensíveis.
- Controle de acesso aos relatórios.

Os logs não deverão ser utilizados como substitutos do controle de permissões dos módulos de negócio.

## 13.14. Estrutura de dados proposta

Entidades principais:

**audit_events**
- id
- actor_type
- actor_id
- user_id
- event_type
- resource_type
- resource_id
- previous_state
- new_state
- reason
- correlation_id
- created_at

**system_events**
- id
- service
- event_type
- severity
- message
- details
- correlation_id
- created_at

**system_alerts**
- id
- alert_type
- severity
- status
- resource_type
- resource_id
- message
- created_at
- acknowledged_at
- resolved_at

**service_health**
- id
- service_name
- status
- last_check_at
- details

**metric_snapshots**
- id
- metric_name
- metric_value
- labels
- recorded_at

Os logs técnicos de alto volume poderão utilizar armazenamento separado. As entidades acima representam o modelo lógico inicial, não uma exigência de armazenar todos os registros no PostgreSQL.

## 13.15. Integração com outros módulos

| Módulo | Eventos monitorados |
|---|---|
| Usuários e Contas | Cadastro, acesso, autorização e desvinculação. |
| Deriv Integration | Conexões, solicitações e respostas da API. |
| Market Data | Recebimento, recuperação e persistência de dados. |
| Indicadores | Cálculos, atrasos e falhas. |
| Estratégias | Geração e rejeição de sinais. |
| Bots | Estados e sessões de execução. |
| Gestão de Risco | Autorizações, bloqueios e reservas. |
| Execução | Propostas, compras, contratos e reconciliações. |
| Planos e Acesso | Ativações, expirações e bloqueios. |
| Parceiros e Markup | Sincronizações e conciliação de receitas. |

Cada módulo deverá emitir eventos estruturados. O módulo de Auditoria e Monitoramento será responsável por recebê-los, registrá-los e disponibilizá-los.

## 13.16. Testes e critérios de aceitação

O módulo será considerado apto quando:

1. Registrar eventos relevantes de todos os módulos.
2. Correlacionar eventos de uma mesma operação.
3. Diferenciar auditoria, logs técnicos e métricas.
4. Registrar erros e exceções.
5. Monitorar conexões com a Deriv.
6. Detectar interrupções de Market Data.
7. Monitorar o estado dos bots.
8. Alertar sobre operações com estado desconhecido.
9. Proteger dados sensíveis.
10. Garantir isolamento entre clientes.
11. Aplicar políticas de retenção.
12. Preservar a integridade dos registros de auditoria.
13. Permitir investigação de falhas operacionais.

## 13.17. Situação atual

| Recurso | Situação |
|---|---|
| Logs técnicos básicos | Parcialmente implementado, a confirmar por auditoria do código atual. |
| Auditoria de ações | Planejado |
| Correlação de eventos | Planejado |
| Métricas operacionais | Planejado |
| Monitoramento de bots | Planejado |
| Alertas | Planejado |
| Monitoramento centralizado | Planejado |
| Histórico de incidentes | Planejado |

A existência de logs básicos em algum serviço não significa que a auditoria e o monitoramento centralizados estejam implementados.

O estado real deverá ser confirmado durante a análise do código.

## 13.18. Decisão arquitetural

Auditoria, logs técnicos e monitoramento serão responsabilidades distintas, embora integradas.

A auditoria deverá preservar a rastreabilidade das ações relevantes. Os logs técnicos deverão facilitar a investigação de falhas. As métricas e os alertas deverão permitir acompanhar a saúde da plataforma.

O fluxo de operações deverá ser rastreável desde o sinal até o resultado confirmado pela Deriv.

A infraestrutura de monitoramento não deverá comprometer o desempenho dos serviços críticos nem bloquear operações por falhas secundárias de registro, exceto quando a integridade ou a segurança operacional exigir bloqueio.

# Capítulo 14 — API Interna e Comunicação entre Módulos

## 14.1. Objetivo do módulo

Este capítulo define os padrões de comunicação entre os módulos internos do backend e a interface externa da plataforma.

A arquitetura deverá permitir que os módulos trabalhem de forma independente, mantendo contratos de comunicação claros e controlados.

Os objetivos são:

- Reduzir o acoplamento entre módulos.
- Padronizar entradas e saídas.
- Garantir rastreabilidade das solicitações.
- Evitar processamento duplicado.
- Preservar a consistência dos dados.
- Permitir processamento assíncrono.
- Manter baixa latência nos fluxos críticos.
- Facilitar testes e evolução da arquitetura.

## 14.2. Princípios arquiteturais

A comunicação deverá seguir estes princípios:

1. Cada módulo será responsável pelos próprios dados e regras de negócio.
2. Um módulo não deverá modificar diretamente as tabelas internas de outro módulo.
3. As interfaces deverão possuir contratos explícitos.
4. A comunicação deverá ser assíncrona sempre que isso trouxer benefícios.
5. Operações críticas deverão possuir rastreabilidade.
6. Eventos deverão ser processados de forma idempotente.
7. Falhas deverão ser tratadas sem comprometer a integridade dos demais módulos.
8. A comunicação interna deverá evitar chamadas externas desnecessárias.
9. A arquitetura deverá priorizar simplicidade e desempenho.

## 14.3. Tipos de comunicação

A plataforma utilizará três formas principais de comunicação.

### 14.3.1. Chamadas diretas entre serviços internos

Utilizadas quando um módulo precisa de uma resposta imediata.

Exemplos:

- Bots solicitando validação à Gestão de Risco.
- Execução solicitando autorização de risco.
- API consultando dados de um serviço.
- Planos e Acesso validando permissões.

Essas chamadas deverão utilizar interfaces internas definidas, sem acessar diretamente a implementação de outro módulo.

### 14.3.2. Eventos internos

Utilizados para comunicar acontecimentos sem exigir uma resposta imediata.

Exemplos:

- Novo candle persistido.
- Novo sinal gerado.
- Bot iniciado.
- Bot pausado.
- Operação autorizada.
- Contrato comprado.
- Contrato encerrado.
- Assinatura expirada.
- Conta Deriv desvinculada.

Os eventos permitirão que vários módulos reajam ao mesmo acontecimento sem criar dependências diretas entre todos eles.

### 14.3.3. API externa

Será a interface de comunicação entre o backend e os clientes da plataforma.

Será disponibilizada inicialmente por meio de HTTP/REST, utilizando FastAPI.

Posteriormente, poderá existir comunicação em tempo real por WebSocket para atualizações de bots, operações, alertas e indicadores.

## 14.4. API HTTP/REST

A API externa deverá utilizar padrões consistentes.

### Convenções

- Prefixo versionado: `/api/v1`.
- Formato de dados: JSON.
- Métodos HTTP conforme a finalidade.
- Códigos de status HTTP apropriados.
- Validação de entradas.
- Autenticação e autorização.
- Documentação OpenAPI.
- Identificadores únicos para recursos.

### Exemplos de endpoints futuros

| Método | Endpoint | Finalidade |
|---|---|---|
| POST | `/api/v1/auth/register` | Cadastro de usuário. |
| GET | `/api/v1/users/me` | Consultar usuário autenticado. |
| GET | `/api/v1/deriv/accounts` | Listar contas vinculadas. |
| POST | `/api/v1/deriv/accounts/link` | Iniciar vinculação de conta. |
| DELETE | `/api/v1/deriv/accounts/{id}` | Desvincular conta. |
| GET | `/api/v1/bots` | Listar bots do cliente. |
| POST | `/api/v1/bots` | Criar bot. |
| POST | `/api/v1/bots/{id}/start` | Iniciar bot. |
| POST | `/api/v1/bots/{id}/pause` | Pausar bot. |
| POST | `/api/v1/bots/{id}/stop` | Encerrar bot. |
| GET | `/api/v1/trades` | Consultar operações. |
| GET | `/api/v1/indicators` | Consultar indicadores disponíveis. |
| GET | `/api/v1/subscription` | Consultar plano e acesso. |

Esses endpoints são propostas de interface. Não representam rotas já implementadas.

## 14.5. Padrão de resposta

As respostas deverão seguir uma estrutura uniforme.

Exemplo de sucesso:

```json
{
  "data": {
    "id": "resource-id",
    "status": "active"
  },
  "meta": {
    "request_id": "request-id"
  }
}
```

Exemplo de erro:

```json
{
  "error": {
    "code": "BOT_NOT_FOUND",
    "message": "Bot não encontrado"
  },
  "meta": {
    "request_id": "request-id"
  }
}
```

As mensagens destinadas ao cliente não deverão expor detalhes internos, credenciais ou informações de outros usuários.

## 14.6. Comunicação síncrona e assíncrona

A comunicação deverá considerar a criticidade e a latência de cada fluxo.

| Fluxo | Comunicação recomendada |
|---|---|
| Autenticação | Síncrona |
| Consulta de configurações | Síncrona |
| Validação de risco | Síncrona |
| Solicitação de execução | Síncrona para validações e aceitação; processamento controlado para etapas posteriores |
| Recebimento de ticks | Assíncrona |
| Distribuição de candles | Assíncrona |
| Geração de indicadores | Assíncrona ou processamento interno |
| Geração de sinais | Orientada a eventos |
| Atualização de contratos | Assíncrona |
| Alertas | Assíncrona |
| Sincronização de comissões | Assíncrona |

A escolha deverá evitar bloquear fluxos críticos com tarefas que podem ser executadas em segundo plano.

## 14.7. Eventos internos

Os eventos deverão representar acontecimentos já ocorridos.

Exemplos de eventos:

| Evento | Produtor | Consumidores possíveis |
|---|---|---|
| `market.candle.closed` | Market Data | Indicadores |
| `indicator.updated` | Indicadores | Estratégias |
| `strategy.signal.generated` | Estratégias | Bots |
| `bot.started` | Bots | Monitoramento |
| `bot.stopped` | Bots | Monitoramento |
| `risk.approved` | Gestão de Risco | Execução |
| `risk.rejected` | Gestão de Risco | Bots e Auditoria |
| `trade.opened` | Execução | Bots, Risco e Auditoria |
| `trade.closed` | Execução | Risco, Bots e Auditoria |
| `subscription.expired` | Planos e Acesso | Bots e Auditoria |
| `deriv.authorization.revoked` | Deriv Integration | Contas, Bots e Execução |

Os nomes são convenções propostas e poderão ser ajustados durante a implementação.

## 14.8. Estrutura dos eventos

Todo evento deverá possuir um envelope padronizado.

Campos previstos:

- event_id
- event_type
- event_version
- occurred_at
- producer
- correlation_id
- causation_id
- user_id, quando aplicável
- aggregate_id, quando aplicável
- payload

O `event_id` permitirá identificar duplicidades.

O `correlation_id` permitirá acompanhar um fluxo completo.

O `causation_id` permitirá identificar qual evento ou solicitação originou o evento atual.

A versão do evento permitirá evoluir os contratos sem quebrar consumidores existentes.

## 14.9. Idempotência e duplicidade

A comunicação deverá considerar que mensagens podem ser entregues mais de uma vez.

Os consumidores deverão ser capazes de identificar eventos já processados.

Regras:

- Cada evento terá identificador único.
- Cada consumidor deverá controlar seu processamento.
- Solicitações financeiras deverão possuir chave de idempotência.
- Repetições não poderão gerar operações duplicadas.
- Eventos fora de ordem deverão ser tratados conforme o estado do recurso.

A idempotência deverá ser aplicada especialmente nos módulos de Bots, Gestão de Risco e Execução.

A proteção contra duplicidade no backend deverá ser complementada pelo controle de estado e reconciliação com a Deriv.

## 14.10. Filas e processamento em segundo plano

A arquitetura deverá permitir processamento assíncrono por filas.

Usos previstos:

- Distribuição de eventos.
- Atualização de indicadores.
- Processamento de sinais.
- Notificações.
- Sincronização de parceiros.
- Reconciliação financeira.
- Tarefas administrativas.

A escolha da tecnologia de mensageria será realizada conforme o volume e a necessidade operacional.

Na primeira etapa, poderão ser utilizados mecanismos internos simples, desde que não comprometam a confiabilidade e a evolução futura.

A adoção de um broker externo deverá ser justificada por requisitos reais de escala, persistência, distribuição ou isolamento.

## 14.11. Consistência e transações

Operações que envolvam múltiplas etapas deverão possuir controle explícito de consistência.

Exemplo: autorização de risco e execução.

1. Registrar a solicitação.
2. Validar os limites.
3. Criar a reserva de exposição.
4. Registrar a autorização.
5. Encaminhar a operação à Execução.
6. Atualizar o estado conforme a resposta da Deriv.

A comunicação entre módulos não deverá depender de uma única transação de banco de dados envolvendo todo o fluxo.

Quando eventos precisarem ser publicados junto com alterações persistidas, deverá ser avaliado o uso do padrão Transactional Outbox.

Esse padrão evita que uma alteração seja salva sem que o evento correspondente seja publicado, ou que um evento seja publicado sem que a alteração tenha sido confirmada.

Para processos com várias etapas e resultados externos, deverá ser avaliado o padrão Saga, com compensações adequadas a cada situação.

Uma operação financeira já confirmada pela Deriv não poderá ser tratada como se fosse simplesmente desfeita por uma transação local.

## 14.12. Segurança da comunicação

A comunicação deverá garantir:

- Autenticação nas rotas externas.
- Autorização por recurso e proprietário.
- Validação de todos os dados recebidos.
- Proteção contra acesso cruzado entre clientes.
- TLS nas comunicações externas.
- Proteção contra abuso de requisições.
- Controle de acesso administrativo.
- Segredos fora do código-fonte.
- Tokens Deriv fora de logs e eventos.
- Validação de origem e integridade dos eventos externos.

Os módulos internos deverão confiar apenas em chamadas originadas por componentes autorizados.

## 14.13. Desempenho e escalabilidade

A comunicação deverá ser projetada para suportar múltiplos bots e clientes simultâneos.

Requisitos:

- Operações assíncronas de I/O.
- Conexões de banco reutilizadas.
- Consultas eficientes.
- Evitar chamadas HTTP internas desnecessárias.
- Evitar processamento repetido.
- Distribuir tarefas demoradas.
- Aplicar backpressure quando necessário.
- Controlar tamanho das filas.
- Monitorar latência por módulo.

O processamento de Market Data deverá permanecer separado do processamento de operações financeiras.

A distribuição de candles e sinais não deverá bloquear o recebimento de dados da Deriv.

## 14.14. Estrutura de dados proposta

Entidades principais, quando houver persistência de mensageria interna:

**event_outbox**
- id
- event_id
- event_type
- payload
- status
- created_at
- published_at

**event_inbox**
- id
- consumer_name
- event_id
- status
- processed_at

**idempotency_keys**
- id
- scope
- idempotency_key
- request_hash
- status
- response_reference
- created_at
- expires_at

Essas estruturas são propostas. A necessidade de cada uma deverá ser avaliada conforme a implementação da comunicação e dos mecanismos de mensageria.

## 14.15. Testes e critérios de aceitação

A arquitetura será considerada apta quando:

1. As interfaces dos módulos estiverem documentadas.
2. Os contratos de entrada e saída forem validados.
3. A API apresentar respostas padronizadas.
4. As permissões forem verificadas no backend.
5. Os eventos possuírem identificadores únicos.
6. Consumidores tratarem mensagens duplicadas.
7. Falhas de comunicação forem tratadas.
8. A publicação de eventos críticos for confiável.
9. Fluxos financeiros preservarem sua consistência.
10. A comunicação não permitir acesso entre clientes.
11. A latência dos fluxos críticos for monitorada.
12. A documentação OpenAPI estiver atualizada.

## 14.16. Situação atual

| Recurso | Situação |
|---|---|
| FastAPI | Implementado |
| Rotas básicas de saúde | Implementado |
| API versionada | Planejado |
| Padrão de resposta | Planejado |
| Interfaces formais entre módulos | Planejado |
| Eventos internos padronizados | Planejado |
| Mensageria persistente | Planejado |
| Idempotência centralizada | Planejado |
| Transactional Outbox | Planejado |
| WebSocket para frontend | Planejado |

A API básica já existe, mas a arquitetura completa de comunicação ainda não está implementada.

## 14.17. Decisão arquitetural

A plataforma utilizará comunicação direta para operações que exigem resposta imediata e eventos assíncronos para distribuição de acontecimentos e processamento desacoplado.

Os módulos manterão suas responsabilidades e dados independentes.

A arquitetura começará simples, utilizando os recursos existentes do projeto. Novas tecnologias de mensageria e infraestrutura somente serão introduzidas quando houver necessidade técnica comprovada.

A prioridade será manter consistência financeira, isolamento entre clientes, baixa latência e facilidade de manutenção.

# Capítulo 15 — Banco de Dados e Persistência

## 15.1. Objetivo

Definir a arquitetura de armazenamento da plataforma, estabelecendo como os dados serão organizados, persistidos, consultados, protegidos e recuperados.

O banco de dados será um componente central do backend, responsável por preservar dados operacionais, financeiros, comerciais e históricos.

Os objetivos principais são:

- Garantir integridade e consistência.
- Suportar múltiplos clientes e robôs.
- Armazenar histórico de preços e candles.
- Permitir consultas eficientes para indicadores.
- Preservar o histórico de operações.
- Evitar perda e duplicidade de dados.
- Suportar crescimento do volume de informações.
- Permitir backup e recuperação.

## 15.2. Tecnologias

A arquitetura atual utiliza:

| Tecnologia | Responsabilidade |
|---|---|
| PostgreSQL 16 | Banco de dados relacional principal. |
| TimescaleDB | Extensão para armazenamento e consulta de séries temporais. |
| asyncpg | Comunicação assíncrona com PostgreSQL. |
| Alembic | Controle de migrações do banco. |
| Docker | Isolamento e execução dos serviços. |

A escolha por PostgreSQL permite manter dados relacionais e financeiros no mesmo mecanismo utilizado para o histórico de mercado.

O TimescaleDB complementa essa estrutura com recursos especializados para séries temporais.

## 15.3. Organização lógica dos dados

O banco deverá ser organizado por domínios funcionais.

| Domínio | Principais informações |
|---|---|
| Usuários | Clientes, administradores e sessões. |
| Contas Deriv | Contas vinculadas e autorizações. |
| Market Data | Ativos, candles e histórico de preços. |
| Indicadores | Configurações e valores calculados. |
| Estratégias | Definições, parâmetros e sinais. |
| Bots | Configurações, sessões e eventos. |
| Gestão de Risco | Perfis, limites, exposições e reservas. |
| Execução | Solicitações, propostas e contratos. |
| Planos e Acesso | Planos, testes e assinaturas. |
| Parceiros e Markup | Indicações, comissões e conciliações. |
| Auditoria | Eventos, registros e rastreabilidade. |

Cada domínio deverá possuir responsabilidade definida sobre seus dados.

O acesso a dados de outro domínio deverá ocorrer por interfaces internas, evitando dependências diretas entre estruturas de tabelas.

## 15.4. Separação entre dados de mercado e dados operacionais

A plataforma deverá distinguir duas categorias principais.

### Dados de mercado

Incluem:

- Ativos.
- Candles históricos.
- Preços.
- Indicadores derivados.
- Metadados de mercado.

Esses dados poderão ser compartilhados entre todos os clientes e bots, respeitando as condições de utilização da Deriv.

### Dados operacionais

Incluem:

- Usuários.
- Contas Deriv.
- Configurações de bots.
- Estratégias personalizadas.
- Operações.
- Contratos.
- Limites de risco.
- Assinaturas.
- Eventos de auditoria.

Esses dados deverão possuir isolamento por cliente e controle de acesso.

## 15.5. Market Data e TimescaleDB

O histórico de mercado será armazenado principalmente em candles M1.

Cada registro deverá representar um candle de um ativo em determinado intervalo de um minuto.

Estrutura atual da tabela `price_candles`:

| Campo | Tipo | Descrição |
|---|---|---|
| asset_symbol | VARCHAR | Identificador do ativo. |
| candle_start | TIMESTAMPTZ | Início do candle em UTC. |
| open | NUMERIC(30,12) | Preço de abertura. |
| high | NUMERIC(30,12) | Preço máximo. |
| low | NUMERIC(30,12) | Preço mínimo. |
| close | NUMERIC(30,12) | Preço de fechamento. |
| received_at | TIMESTAMPTZ | Momento de persistência. |

A chave primária será composta por:

- `candle_start`
- `asset_symbol`

A tabela possui validações de integridade para os valores OHLC e índice para consultas por ativo e período.

A tabela foi projetada para utilização como hypertable do TimescaleDB.

### Regras de persistência

- Apenas candles fechados serão persistidos pelo fluxo ao vivo.
- O candle atual poderá permanecer em memória como provisório.
- O horário será armazenado em UTC.
- Não serão criados candles artificiais para intervalos sem dados.
- A recuperação histórica poderá atualizar registros existentes.
- A ingestão ao vivo não deverá sobrescrever candles históricos já existentes.

O banco será a fonte oficial dos candles fechados utilizados pelos indicadores.

## 15.6. Estratégia de consultas

As consultas de mercado deverão priorizar:

- Filtro por ativo.
- Intervalo temporal.
- Ordenação cronológica.
- Limite explícito de registros.
- Utilização de índices adequados.

Exemplo conceitual:

```sql
SELECT
    candle_start,
    open,
    high,
    low,
    close
FROM price_candles
WHERE asset_symbol = $1
  AND candle_start >= $2
  AND candle_start < $3
ORDER BY candle_start ASC;
```

Os indicadores deverão consumir os dados persistidos, evitando depender diretamente de novas consultas à API da Deriv para cada cálculo.

O candle em formação poderá ser utilizado como dado provisório, desde que identificado como tal e sem ser confundido com um candle fechado.

## 15.7. Dados financeiros

Valores financeiros deverão utilizar tipos numéricos apropriados, como `NUMERIC`, evitando `FLOAT` e `DOUBLE PRECISION` para cálculos monetários.

O banco deverá preservar:

- Valor solicitado.
- Valor efetivamente comprado.
- Moeda.
- Pagamento informado.
- Resultado financeiro.
- Taxas e custos aplicáveis.
- Estado da operação.

A precisão e a escala deverão respeitar as características dos produtos e moedas utilizados.

Os valores recebidos da Deriv deverão ser preservados com precisão suficiente para permitir conciliação.

## 15.8. Relacionamentos e isolamento entre clientes

As tabelas operacionais deverão manter relacionamentos claros com seus proprietários.

Exemplo lógico:

```text
users
  └── deriv_accounts
        └── bots
              ├── bot_configs
              ├── bot_runs
              └── trade_requests
                    └── contracts
```

As operações de consulta e alteração deverão validar o proprietário dos recursos.

O sistema deverá impedir que um cliente consulte ou modifique dados de outro cliente por meio da API ou de chamadas internas.

Poderá ser avaliado o uso de PostgreSQL Row-Level Security (RLS) como camada adicional de proteção.

A RLS não substituirá as validações de autorização da aplicação.

## 15.9. Integridade e transações

O banco deverá utilizar os mecanismos nativos do PostgreSQL para preservar a consistência.

Recursos previstos:

- Primary Keys.
- Foreign Keys.
- Unique Constraints.
- Check Constraints.
- Índices.
- Transações.
- Controle de concorrência.
- Restrições de nulidade.

Operações financeiras e alterações críticas deverão utilizar transações apropriadas.

A integração com serviços externos, especialmente a Deriv, não poderá depender de uma transação SQL aberta durante toda a comunicação de rede.

O sistema deverá registrar estados intermediários e reconciliar operações quando houver falhas ou respostas incertas.

## 15.10. Índices e desempenho

Os índices deverão ser definidos conforme os padrões reais de consulta.

Índices prioritários:

- Identificador do cliente.
- Identificador da conta Deriv.
- Identificador do bot.
- Estado operacional.
- Identificador do contrato.
- Data e hora.
- Identificadores de correlação.
- Combinações utilizadas em filtros frequentes.

Para Market Data, deverá ser priorizado o acesso por ativo e intervalo temporal.

Índices adicionais deverão ser criados com base em consultas observadas, evitando sobrecarregar a escrita com índices desnecessários.

O desempenho deverá ser avaliado com `EXPLAIN ANALYZE` e métricas reais.

## 15.11. Migrações com Alembic

Toda alteração estrutural deverá ser controlada por migrações.

Regras:

- Não alterar manualmente o schema de produção.
- Cada mudança deverá possuir uma migração.
- Migrações deverão ser revisadas antes da aplicação.
- Alterações destrutivas exigirão avaliação de impacto.
- A versão do banco deverá ser identificável.
- O histórico de migrações deverá permanecer no Git.

As migrações deverão ser testadas em ambiente controlado antes da aplicação em produção.

A estrutura de Alembic já foi criada no projeto, mas cada migração e seu estado de aplicação deverão ser verificados no ambiente.

## 15.12. Backups e recuperação

A plataforma deverá possuir estratégia de backup.

Requisitos:

- Backup periódico do PostgreSQL.
- Armazenamento protegido.
- Retenção definida.
- Verificação de integridade.
- Testes de restauração.
- Proteção contra exclusão acidental.
- Procedimento documentado de recuperação.

Em ambiente de produção, deverá ser avaliada a utilização de arquivamento contínuo de WAL e recuperação point-in-time (PITR).

Os objetivos de recuperação deverão ser definidos:

- **RPO:** quantidade máxima aceitável de dados perdidos.
- **RTO:** tempo máximo aceitável para restaurar o serviço.

Backups não serão considerados confiáveis até que a restauração tenha sido testada.

## 15.13. Retenção e arquivamento

A retenção deverá considerar o tipo e a importância dos dados.

| Categoria | Política |
|---|---|
| Candles | Histórico necessário para indicadores e análises. |
| Operações e contratos | Retenção prolongada para histórico e conciliação. |
| Auditoria | Retenção conforme requisitos legais e comerciais. |
| Logs técnicos | Rotação e retenção configuráveis. |
| Sessões e dados temporários | Expiração controlada. |
| Dados de assinatura | Preservação do histórico comercial. |

A remoção de dados deverá considerar obrigações legais, contratos, privacidade e necessidades de auditoria.

O uso de políticas de retenção e compressão do TimescaleDB deverá ser avaliado conforme o volume real e os requisitos de consulta.

## 15.14. Segurança do banco

O banco deverá possuir:

- Usuário exclusivo para a aplicação.
- Privilégios mínimos necessários.
- Credenciais fora do código-fonte.
- Conexões protegidas em produção.
- Controle de acesso administrativo.
- Backups protegidos.
- Monitoramento de conexões.
- Proteção de dados sensíveis.
- Procedimentos de rotação de credenciais.

Tokens de autorização Deriv deverão ser criptografados pela aplicação antes de serem armazenados.

O banco não deverá registrar credenciais em texto aberto.

## 15.15. Estrutura de dados proposta

Os principais grupos de tabelas serão:

**Market Data**
- `price_candles`
- `market_assets`
- `market_data_events`

**Usuários e Contas**
- `users`
- `user_sessions`
- `deriv_accounts`
- `deriv_authorizations`

**Indicadores e Estratégias**
- `indicator_configs`
- `indicator_values`
- `strategies`
- `strategy_configs`
- `trading_signals`

**Bots**
- `bots`
- `bot_configs`
- `bot_runs`
- `bot_events`

**Gestão de Risco**
- `risk_profiles`
- `risk_limits`
- `risk_exposures`
- `risk_reservations`
- `risk_events`

**Execução**
- `trade_requests`
- `trade_proposals`
- `contracts`
- `execution_events`
- `execution_reconciliation`

**Planos e Comercial**
- `plans`
- `subscriptions`
- `trials`
- `partner_referrals`
- `markup_configs`
- `partner_commissions`
- `markup_commissions`

**Auditoria**
- `audit_events`
- `system_events`
- `system_alerts`

A lista representa o modelo lógico planejado. Não significa que todas essas tabelas já existam no banco atual.

## 15.16. Testes e critérios de aceitação

O banco será considerado apto quando:

1. As migrações forem reproduzíveis.
2. As restrições de integridade forem validadas.
3. Os relacionamentos forem consistentes.
4. O isolamento entre clientes for comprovado.
5. As consultas de candles utilizarem índices adequados.
6. Os dados financeiros preservarem precisão.
7. As operações críticas possuírem transações apropriadas.
8. O sistema suportar concorrência.
9. Os backups forem realizados e restaurados com sucesso.
10. As políticas de retenção forem documentadas.
11. A reconciliação financeira puder ser realizada.
12. O desempenho for medido com volume representativo de dados.

## 15.17. Situação atual

| Recurso | Situação |
|---|---|
| PostgreSQL 16 | Implementado |
| TimescaleDB | Implementado na estrutura de migrações; aplicação no ambiente a verificar |
| asyncpg | Implementado |
| Alembic | Estrutura criada; migrações existentes precisam ser verificadas no ambiente |
| Tabela `price_candles` | Implementada por migração |
| Índice de candles | Implementado por migração |
| Modelo completo dos domínios | Planejado |
| Isolamento completo entre clientes | Planejado |
| Backups automatizados | A verificar |
| Recuperação point-in-time | Planejado |
| Políticas completas de retenção | Planejado |

## 15.18. Decisão arquitetural

PostgreSQL será o banco principal da plataforma, com TimescaleDB para séries temporais de mercado.

Os candles fechados persistidos serão a referência para os cálculos de indicadores e análises históricas.

Dados financeiros e operacionais deverão preservar integridade, precisão e rastreabilidade.

A estrutura será ampliada por migrações controladas, sem reorganizações desnecessárias do projeto existente.

A evolução do banco deverá priorizar consistência, isolamento entre clientes e desempenho, evitando introduzir complexidade antes que exista necessidade comprovada.

# Capítulo 16 — Segurança, Autenticação e Proteção de Dados

## 16.1. Objetivo

Estabelecer os requisitos de segurança da plataforma em todas as camadas:

- Autenticação de usuários.
- Autorização e controle de acesso.
- Integração segura com a Deriv.
- Proteção de tokens e credenciais.
- Isolamento entre clientes.
- Proteção das operações financeiras.
- Segurança da infraestrutura.
- Auditoria e resposta a incidentes.

A segurança deverá ser considerada desde a arquitetura inicial, e não adicionada apenas quando a plataforma estiver pronta.

## 16.2. Princípios de segurança

A plataforma deverá seguir os seguintes princípios:

1. **Privilégio mínimo:** cada usuário, serviço e componente terá somente as permissões necessárias.
2. **Defesa em profundidade:** diferentes camadas de proteção deverão atuar em conjunto.
3. **Isolamento entre clientes:** nenhum cliente poderá acessar dados ou operações de outro.
4. **Segregação de credenciais:** autenticação da plataforma e autorização Deriv serão independentes.
5. **Rastreabilidade:** ações críticas deverão gerar registros de auditoria.
6. **Proteção por padrão:** funcionalidades críticas deverão permanecer bloqueadas até que as condições de segurança sejam satisfeitas.
7. **Falha segura:** falhas de autorização ou validação não poderão liberar operações.
8. **Minimização de dados:** armazenar somente informações necessárias ao funcionamento da plataforma.

## 16.3. Autenticação da plataforma

A plataforma deverá possuir seu próprio sistema de autenticação.

O cadastro e o login na plataforma não deverão depender da autenticação da Deriv.

Requisitos:

- Cadastro de clientes.
- Login e logout.
- Recuperação de senha.
- Verificação de endereço de e-mail.
- Expiração de sessões.
- Revogação de sessões.
- Proteção contra tentativas repetidas de login.
- Registro de eventos de autenticação.

As senhas deverão ser armazenadas utilizando algoritmos próprios para hashing de senhas, como Argon2id.

Senhas nunca deverão ser armazenadas em texto aberto ou por meio de hashing rápido convencional, como SHA-256 isoladamente.

## 16.4. Sessões e tokens internos

A autenticação deverá utilizar um mecanismo seguro de sessão.

A arquitetura poderá utilizar:

- Access tokens de curta duração.
- Refresh tokens com rotação.
- Revogação de sessões.
- Identificação de dispositivos ou sessões.
- Expiração por inatividade, quando aplicável.

Se forem utilizados JWTs, deverão existir validações rigorosas de assinatura, emissor, audiência e expiração.

Tokens de atualização deverão ser protegidos e sua reutilização indevida deverá ser detectada.

A implementação deverá evitar sessões permanentes ou tokens sem expiração.

## 16.5. Autorização e permissões

A plataforma deverá implementar controle de acesso baseado em papéis e permissões (RBAC), complementado por validações de propriedade dos recursos.

Papéis iniciais:

| Papel | Responsabilidade |
|---|---|
| Administrador | Gerenciar clientes, planos, bots e configurações administrativas. |
| Cliente | Gerenciar sua própria conta, contas Deriv e bots autorizados. |
| Serviço interno | Executar tarefas específicas entre módulos. |

As permissões deverão ser verificadas no backend.

Ocultar funcionalidades no frontend não será considerado controle de segurança.

Toda solicitação deverá validar:

- Identidade do usuário.
- Permissão para executar a ação.
- Propriedade do recurso.
- Estado da conta.
- Estado da assinatura.
- Autorização Deriv, quando necessária.
- Limites e regras de risco, quando envolver operações.

## 16.6. Autorização de contas Deriv

A autorização Deriv deverá ser independente da autenticação interna.

O cliente deverá conectar sua conta utilizando o mecanismo oficial de autorização disponibilizado pela Deriv.

A plataforma não deverá solicitar nem armazenar a senha da conta Deriv.

O fluxo deverá contemplar:

1. Solicitação de autorização.
2. Redirecionamento ou mecanismo oficial de consentimento.
3. Recebimento da autorização.
4. Validação da resposta.
5. Identificação da conta Deriv.
6. Identificação das permissões concedidas.
7. Armazenamento seguro das credenciais necessárias.
8. Ativação da conta vinculada após validações.

O protocolo, os endpoints, os parâmetros e os escopos deverão seguir a documentação oficial vigente da Deriv.

A implementação deverá ser validada antes de assumir que OAuth2 é o mecanismo aplicável a todos os fluxos necessários.

## 16.7. Proteção dos tokens Deriv

Tokens de autorização Deriv são informações sensíveis.

Requisitos:

- Criptografia antes do armazenamento.
- Chaves de criptografia fora do banco de dados.
- Controle de acesso restrito.
- Rotação de chaves quando aplicável.
- Revogação quando o cliente desvincular a conta.
- Nunca registrar tokens em logs.
- Nunca retornar tokens ao frontend sem necessidade técnica e autorização expressa.
- Nunca incluir tokens em mensagens de erro.

A arquitetura deverá permitir criptografia e descriptografia exclusivamente nos componentes que realmente precisam utilizar as credenciais.

Em produção, deverá ser avaliada a utilização de um gerenciador de segredos ou serviço de gerenciamento de chaves.

## 16.8. Isolamento entre clientes

O isolamento entre clientes é um requisito crítico.

Um cliente não poderá:

- Consultar contas Deriv de outro cliente.
- Iniciar ou interromper bots de outro cliente.
- Consultar operações de terceiros.
- Modificar configurações alheias.
- Acessar tokens de terceiros.
- Alterar limites de risco de outros usuários.

Todas as consultas e alterações deverão verificar a propriedade dos recursos.

O isolamento deverá ser testado também em chamadas internas, tarefas assíncronas e processamento de eventos.

A utilização de identificadores não previsíveis não substitui a validação de autorização.

## 16.9. Segurança das operações financeiras

Operações financeiras deverão possuir controles adicionais.

Antes de qualquer operação, o sistema deverá verificar:

- Conta Deriv correta.
- Ambiente correto: demo ou real.
- Autorização válida.
- Bot autorizado e ativo.
- Assinatura e plano válidos.
- Limites de risco.
- Parâmetros da operação.
- Ausência de bloqueios operacionais.

O ambiente real deverá possuir proteção contra execução acidental.

Requisitos adicionais:

- Identificação explícita do modo real.
- Confirmação das configurações de operação.
- Limites de exposição.
- Controle de concorrência.
- Idempotência.
- Registro de solicitações.
- Reconciliação de resultados.

Nenhuma operação deverá ser repetida automaticamente quando o resultado da primeira solicitação for desconhecido, sem antes verificar seu estado na Deriv.

## 16.10. Proteção das APIs

As APIs internas e externas deverão implementar:

- HTTPS em produção.
- Validação de entradas.
- Limites de tamanho de requisição.
- Rate limiting.
- Controle de autenticação e autorização.
- Tratamento seguro de erros.
- Proteção contra injeção SQL.
- Política adequada de CORS.
- Validação de parâmetros.
- Proteção contra abuso de endpoints.

As consultas ao banco deverão utilizar parâmetros, evitando montar comandos SQL por concatenação de entradas externas.

Mensagens de erro não deverão revelar informações internas, credenciais, estruturas sensíveis ou detalhes desnecessários da infraestrutura.

## 16.11. Proteção contra ataques

A plataforma deverá considerar, entre outros, os seguintes riscos:

| Risco | Proteção |
|---|---|
| Brute force | Rate limiting e bloqueio progressivo. |
| Roubo de sessão | Expiração, rotação e revogação. |
| Acesso indevido a recursos | Validação de propriedade e permissões. |
| SQL Injection | Consultas parametrizadas. |
| CSRF | Proteções específicas quando houver autenticação baseada em cookies. |
| XSS | Validação e codificação adequada de conteúdo. |
| Replay de solicitações | Idempotência e validação de estado. |
| Vazamento de tokens | Criptografia e mascaramento de logs. |
| Abuso de API | Limites de frequência e monitoramento. |
| Elevação de privilégios | RBAC e validação de permissões no servidor. |

## 16.12. Segurança dos serviços internos

Os serviços internos deverão possuir responsabilidades e permissões específicas.

Um módulo não deverá ter acesso irrestrito a todos os recursos apenas por executar dentro do backend.

Requisitos:

- Separação de responsabilidades.
- Validação de origem dos eventos.
- Identificação de chamadas internas.
- Proteção de endpoints administrativos.
- Controle de acesso a tarefas críticas.
- Validação de dados recebidos entre módulos.

Credenciais de serviços deverão ser separadas das credenciais dos usuários.

## 16.13. Segurança da infraestrutura

A infraestrutura deverá observar:

- Variáveis sensíveis fora do código-fonte.
- Arquivos `.env` fora do Git.
- Usuários de sistema com privilégios mínimos.
- Imagens Docker confiáveis e atualizadas.
- Serviços internos não expostos desnecessariamente.
- Banco de dados sem acesso público direto.
- Firewall e regras de rede.
- Atualizações de segurança.
- Monitoramento de vulnerabilidades.

Em produção, deverá existir separação entre ambientes de desenvolvimento, homologação e produção.

## 16.14. Logs e auditoria de segurança

Eventos relevantes deverão ser registrados.

Exemplos:

- Login bem-sucedido.
- Tentativa de login inválida.
- Recuperação de senha.
- Alteração de permissões.
- Vinculação de conta Deriv.
- Revogação de autorização.
- Início de bot.
- Alteração de configuração.
- Solicitação de operação.
- Bloqueio por risco.
- Alteração de plano.
- Ação administrativa.

Os registros deverão permitir identificar usuário, horário, ação, resultado e contexto.

Dados sensíveis deverão ser mascarados ou omitidos.

Os registros de auditoria não deverão permitir alteração comum por usuários ou módulos operacionais.

## 16.15. Revogação e desvinculação da Deriv

O cliente deverá poder retirar a autorização concedida à plataforma.

O procedimento deverá:

1. Bloquear novas operações.
2. Impedir novas solicitações de negociação.
3. Suspender os bots vinculados.
4. Verificar contratos ainda abertos.
5. Tratar contratos e operações pendentes conforme as regras da Deriv.
6. Encerrar conexões privadas quando aplicável.
7. Revogar a autorização pelo mecanismo oficial, quando disponível.
8. Invalidar ou eliminar os tokens armazenados conforme a política de segurança.
9. Registrar o evento de auditoria.

A desvinculação não deverá excluir a conta Deriv do cliente nem impedir seu acesso direto à Deriv.

A plataforma deverá preservar os registros necessários para auditoria e conciliação, respeitando as regras de retenção e proteção de dados.

## 16.16. Proteção de dados e LGPD

A plataforma deverá observar a Lei Geral de Proteção de Dados Pessoais (LGPD), considerando sua atuação e os dados tratados.

Deverão ser definidos:

- Finalidades do tratamento.
- Bases legais aplicáveis.
- Categorias de dados coletados.
- Política de privacidade.
- Política de retenção.
- Procedimentos de atendimento aos titulares.
- Controle de acesso aos dados.
- Processo de correção e exclusão quando aplicável.
- Procedimentos de resposta a incidentes.

A coleta deverá se limitar aos dados necessários para cadastro, autenticação, operação e obrigações legais ou contratuais.

A plataforma deverá avaliar suas responsabilidades como controladora ou operadora em cada atividade de tratamento.

## 16.17. Gestão de incidentes

Deverá existir um procedimento para incidentes de segurança.

Etapas:

1. Identificação.
2. Classificação da gravidade.
3. Contenção.
4. Investigação.
5. Recuperação.
6. Comunicação quando necessária.
7. Registro.
8. Revisão e prevenção de recorrência.

Incidentes envolvendo tokens Deriv, dados financeiros ou acesso indevido deverão receber prioridade elevada.

## 16.18. Testes de segurança

O sistema deverá possuir testes para:

- Autenticação.
- Expiração de sessões.
- Revogação de tokens.
- Controle de permissões.
- Isolamento entre clientes.
- Proteção de endpoints administrativos.
- Validação de entradas.
- Proteção de credenciais.
- Bloqueio de operações não autorizadas.
- Separação entre demo e real.
- Rate limiting.
- Tratamento de falhas de autorização.

Também deverão ser realizadas análises de dependências e verificações de vulnerabilidades antes da publicação de versões relevantes.

## 16.19. Situação atual

| Recurso | Situação |
|---|---|
| Separação de configurações sensíveis | Parcial, a auditar |
| Autenticação própria de usuários | Planejada |
| Controle RBAC | Planejado |
| OAuth2 / autorização Deriv | Planejado e sujeito à validação do fluxo oficial |
| Criptografia de tokens | Planejada |
| Isolamento completo entre clientes | Planejado |
| Proteção das operações reais | Planejada |
| Rate limiting | Planejado |
| Auditoria de segurança | Planejada |
| Procedimentos LGPD | Planejados |
| Gestão de incidentes | Planejada |

## 16.20. Decisão arquitetural

A plataforma deverá manter separadas a autenticação interna e a autorização Deriv.

Credenciais Deriv nunca serão solicitadas diretamente ao cliente nem armazenadas em texto aberto.

Todas as operações deverão respeitar autorização, propriedade dos recursos, plano, estado do bot e limites de risco.

O ambiente real deverá possuir controles adicionais contra execução acidental.

A segurança deverá ser aplicada de forma transversal a todos os módulos, APIs, tarefas assíncronas, conexões externas e operações financeiras.

# Capítulo 17 — Infraestrutura, Deploy, Ambientes e CI/CD

## 17.1. Objetivo

Definir a infraestrutura necessária para executar a plataforma Deriv de maneira estável, segura, escalável e previsível.

O capítulo estabelece:

- Organização dos ambientes.
- Infraestrutura de execução.
- Containerização.
- Deploy e atualização.
- Integração e entrega contínuas (CI/CD).
- Monitoramento da infraestrutura.
- Escalabilidade.
- Recuperação de falhas.
- Estratégia de publicação de versões.

A infraestrutura deverá suportar múltiplos clientes, múltiplos robôs e conexões contínuas com a Deriv.

## 17.2. Arquitetura atual

O projeto utiliza Docker e Docker Compose para executar os serviços.

Estrutura lógica atual:

```text
Deriv Backend
│
├── API
│   └── FastAPI / Python 3.14
│
├── Database
│   └── PostgreSQL 16
│       └── TimescaleDB
│
└── Configuração
    ├── Dockerfile
    ├── compose.yaml
    ├── .env.example
    └── .dockerignore
```

O serviço `api` executa o backend.

O serviço `db` executa o PostgreSQL com suporte ao TimescaleDB.

O Docker Compose gerencia a execução e a comunicação entre esses serviços.

Essa estrutura é adequada para desenvolvimento e para a etapa inicial de validação da arquitetura.

## 17.3. Separação de ambientes

A plataforma deverá possuir três ambientes distintos.

| Ambiente | Finalidade |
|---|---|
| Desenvolvimento | Construção e testes locais. |
| Homologação | Validação integrada antes da publicação. |
| Produção | Atendimento aos clientes e execução real da plataforma. |

### Desenvolvimento

Características:

- Execução local.
- Docker Compose.
- Banco de dados isolado.
- Dados de teste.
- Conta Deriv demo.
- Logs detalhados.
- Testes automatizados.

### Homologação

Características:

- Configuração próxima à produção.
- Banco de dados independente.
- Credenciais próprias.
- Testes de integração.
- Validação de migrações.
- Testes de autorização.
- Validação de operações em ambiente demo.

### Produção

Características:

- Infraestrutura dedicada.
- Banco de dados protegido.
- Credenciais reais.
- HTTPS obrigatório.
- Backups automatizados.
- Monitoramento contínuo.
- Controle de acesso administrativo.
- Política de atualização e recuperação.

Credenciais, bancos e dados dos ambientes não deverão ser compartilhados indevidamente.

## 17.4. Containerização

O Docker será utilizado para padronizar a execução dos serviços.

Cada serviço deverá possuir dependências e responsabilidades bem definidas.

Serviços previstos:

| Serviço | Responsabilidade |
|---|---|
| API | Expor endpoints e coordenar solicitações. |
| Database | Armazenar dados operacionais e históricos. |
| Market Data Worker | Coletar e persistir dados de mercado. |
| Bot Worker | Processar estratégias e eventos dos robôs. |
| Execution Worker | Processar solicitações de execução. |
| Scheduler | Executar tarefas periódicas. |

A separação entre processos deverá ocorrer conforme a necessidade real de escalabilidade e isolamento.

Não será obrigatório criar um container independente para cada módulo lógico.

## 17.5. Inicialização e dependências

A inicialização deverá respeitar a disponibilidade dos serviços.

Ordem lógica:

1. Banco de dados disponível.
2. Verificação da conectividade.
3. Aplicação das migrações pendentes.
4. Inicialização dos serviços da aplicação.
5. Inicialização dos workers.
6. Verificação de saúde dos componentes.

A aplicação deverá possuir mecanismos de health check.

Deverão ser diferenciados:

- **Liveness:** indica se o processo está funcionando.
- **Readiness:** indica se o serviço está pronto para receber solicitações.
- **Dependency health:** indica se as dependências necessárias estão disponíveis.

Uma falha temporária na Deriv não deverá necessariamente impedir a inicialização da API, mas deverá impedir operações que dependam da integração indisponível.

## 17.6. Configurações e variáveis de ambiente

As configurações deverão ser externas ao código-fonte.

Exemplos:

```env
APP_ENV=development
APP_DEBUG=true

DATABASE_HOST=db
DATABASE_PORT=5432
DATABASE_NAME=deriv_db
DATABASE_USER=deriv_user
DATABASE_PASSWORD=

DERIV_WS_URL=
DERIV_SYMBOLS=1HZ100V
DERIV_RECONNECT_DELAY_SECONDS=2.0

LOG_LEVEL=INFO
```

Os valores acima são ilustrativos e deverão respeitar os nomes efetivamente definidos no projeto.

Regras:

- Não armazenar segredos no Git.
- Utilizar `.env.example` apenas como modelo.
- Separar configurações por ambiente.
- Validar variáveis obrigatórias na inicialização.
- Não utilizar credenciais de produção em desenvolvimento.
- Não registrar senhas ou tokens nos logs.

Em produção, deverá ser avaliada a utilização de um gerenciador de segredos.

## 17.7. Deploy

O processo de publicação deverá ser controlado e reproduzível.

Fluxo proposto:

```text
Código no Git
     |
     v
Verificação automática
     |
     v
Testes automatizados
     |
     v
Build das imagens
     |
     v
Publicação em homologação
     |
     v
Validação
     |
     v
Aprovação para produção
     |
     v
Deploy em produção
     |
     v
Health checks e monitoramento
```

Cada versão publicada deverá possuir identificação clara.

O deploy deverá permitir identificar:

- Versão do código.
- Data da publicação.
- Migrações aplicadas.
- Imagem utilizada.
- Ambiente de destino.
- Resultado da implantação.

## 17.8. Integração e entrega contínuas (CI/CD)

A plataforma deverá implementar um pipeline automatizado.

Etapas previstas:

1. Verificação de sintaxe.
2. Verificação de formatação.
3. Análise estática.
4. Testes unitários.
5. Testes de integração.
6. Validação das migrações.
7. Build Docker.
8. Verificação de vulnerabilidades.
9. Publicação do artefato.
10. Deploy controlado.

O GitHub poderá ser utilizado como plataforma de repositório e automação.

GitHub Actions é uma opção para implementar os pipelines.

A adoção deverá considerar o custo, os limites de execução e a complexidade operacional.

## 17.9. Estratégia de testes antes do deploy

Nenhuma versão deverá ser publicada em produção sem passar pelas verificações obrigatórias.

Requisitos:

- Todos os testes críticos aprovados.
- Migrações validadas.
- Configurações obrigatórias presentes.
- Imagem construída com sucesso.
- Verificação de segurança.
- Health checks aprovados.
- Compatibilidade com o schema do banco.

A suíte existente de testes deverá ser preservada como referência de regressão.

O resultado histórico de 27 testes aprovados deverá ser tratado como baseline anterior, não como garantia de que a versão atual continua aprovada.

## 17.10. Atualização e rollback

O processo de atualização deverá considerar a compatibilidade entre código e banco de dados.

Migrações deverão seguir, sempre que possível, uma estratégia compatível com versões anteriores:

1. Adicionar estruturas novas.
2. Publicar código compatível com estruturas antigas e novas.
3. Migrar dados, quando necessário.
4. Remover estruturas antigas somente em uma versão posterior.

O rollback da aplicação não deverá presumir que uma migração destrutiva pode ser revertida automaticamente.

Antes de atualizações críticas:

- Criar backup.
- Validar a migração.
- Definir procedimento de recuperação.
- Registrar a versão anterior.
- Planejar a interrupção, se necessária.

## 17.11. Disponibilidade e recuperação de falhas

A plataforma deverá ser preparada para falhas de:

- API.
- Banco de dados.
- Conexão com a Deriv.
- Workers.
- Rede.
- Infraestrutura.
- Armazenamento.

Cada componente deverá possuir estratégia de recuperação.

A reconexão com a Deriv deverá respeitar backoff e limites de tentativas.

O reinício de um worker não poderá gerar operações duplicadas.

Estados de execução deverão ser recuperáveis a partir do banco e reconciliados com a Deriv quando necessário.

O reinício da aplicação não poderá ser tratado como cancelamento automático de operações financeiras.

## 17.12. Escalabilidade

A infraestrutura deverá permitir crescimento gradual.

A arquitetura inicial deverá priorizar simplicidade operacional.

Possibilidades futuras:

- Múltiplas instâncias da API.
- Workers independentes.
- Pool de conexões do PostgreSQL.
- Distribuição de tarefas.
- Filas de eventos.
- Balanceamento de carga.
- Banco de dados gerenciado.
- Separação de cargas de leitura e escrita, se necessário.

Market Data deverá evitar conexões duplicadas desnecessárias para o mesmo ativo.

A coleta de preços deverá ser compartilhada entre robôs que utilizam o mesmo ativo.

A execução de cada robô deverá permanecer isolada.

## 17.13. Monitoramento da infraestrutura

Deverão ser monitorados:

- CPU.
- Memória.
- Armazenamento.
- Uso de rede.
- Conexões com PostgreSQL.
- Tempo de resposta da API.
- Erros por serviço.
- Reinicializações de containers.
- Estado dos workers.
- Disponibilidade da Deriv.
- Atraso na ingestão de candles.

O monitoramento deverá permitir identificar problemas antes que provoquem perda de operações ou indisponibilidade prolongada.

Alertas deverão possuir níveis de prioridade e responsáveis definidos.

## 17.14. Segurança do deploy

O processo de publicação deverá proteger o ambiente de produção.

Requisitos:

- Credenciais de deploy protegidas.
- Permissões mínimas.
- Segredos separados por ambiente.
- Imagens provenientes de fontes confiáveis.
- Controle de versões.
- Registro das publicações.
- Acesso administrativo restrito.
- Verificação de vulnerabilidades.
- Proibição de credenciais reais em pipelines de desenvolvimento.

As credenciais de produção não deverão estar disponíveis para todos os colaboradores ou processos de CI.

## 17.15. Banco de dados em produção

O PostgreSQL de produção deverá possuir:

- Armazenamento persistente.
- Backups automatizados.
- Monitoramento.
- Controle de conexões.
- Política de atualização.
- Proteção de rede.
- Procedimentos de restauração.

O banco não deverá depender do ciclo de vida do container da aplicação.

Os dados deverão permanecer preservados mesmo quando containers forem removidos ou recriados.

A estratégia de armazenamento deverá considerar o crescimento contínuo dos candles e dos registros operacionais.

## 17.16. Estratégia de publicação

A publicação deverá ocorrer inicialmente de maneira controlada.

Recomendação:

- Desenvolvimento local com Docker Compose.
- Homologação em infraestrutura separada.
- Produção em servidor ou serviço gerenciado.
- Deploy automatizado após aprovação.
- Monitoramento após publicação.

Estratégias mais avançadas, como blue-green deployment ou canary deployment, poderão ser adotadas quando houver necessidade de alta disponibilidade e capacidade operacional para mantê-las.

## 17.17. Testes e critérios de aceitação

A infraestrutura será considerada adequada quando:

1. Os serviços iniciarem de maneira reproduzível.
2. Os ambientes estiverem isolados.
3. Os dados persistirem após reinicialização dos containers.
4. Os health checks identificarem falhas.
5. Os testes forem executados automaticamente.
6. As migrações forem validadas antes do deploy.
7. A publicação possuir identificação de versão.
8. O rollback da aplicação estiver documentado.
9. Os backups puderem ser restaurados.
10. Workers puderem reiniciar sem duplicar operações.
11. A infraestrutura possuir monitoramento.
12. Segredos estiverem protegidos.

## 17.18. Situação atual

| Recurso | Situação |
|---|---|
| Docker | Implementado |
| Docker Compose | Implementado |
| Container da API | Implementado |
| Container PostgreSQL | Implementado |
| Persistência do banco | Configurada, a validar continuamente |
| Health check básico | Implementado |
| Ambientes separados | Planejado |
| CI/CD | Planejado |
| Deploy em produção | Planejado |
| Monitoramento centralizado | Planejado |
| Backup automatizado | A verificar |
| Rollback documentado | Planejado |
| Escalabilidade horizontal | Planejada |

## 17.19. Decisão arquitetural

Docker e Docker Compose continuarão sendo utilizados no desenvolvimento e na etapa inicial de validação.

A infraestrutura de produção deverá ser independente do ambiente de desenvolvimento.

A plataforma deverá começar com uma infraestrutura simples, mas preparada para separar API, coleta de mercado, processamento dos bots e execução de operações quando a carga justificar.

A publicação deverá ser automatizada, testada, rastreável e reversível no nível da aplicação.

A estabilidade das operações financeiras terá prioridade sobre a velocidade de publicação.

# Capítulo 18 — Testes, Qualidade de Software e Validação Operacional

## 18.1. Objetivo

Estabelecer uma estratégia de qualidade para todo o backend da plataforma Deriv.

A estratégia deverá garantir:

- Correção das funcionalidades.
- Integridade dos dados.
- Isolamento entre clientes.
- Segurança das operações.
- Confiabilidade da integração com a Deriv.
- Desempenho sob carga.
- Recuperação após falhas.
- Ausência de regressões.
- Comportamento previsível em produção.

A qualidade não deverá ser avaliada apenas pela quantidade de testes aprovados. Também deverá considerar cobertura dos requisitos, cenários de falha e comportamento operacional.

## 18.2. Tecnologias de testes

O projeto já utiliza:

| Tecnologia | Responsabilidade |
|---|---|
| Pytest | Execução dos testes. |
| pytest-asyncio | Testes assíncronos. |
| HTTPX | Testes de endpoints HTTP. |
| Docker Compose | Ambiente integrado de testes. |
| PostgreSQL | Validação de persistência e consultas. |

Ferramentas adicionais poderão ser incorporadas conforme a necessidade.

Possibilidades:

- Ruff: análise estática e formatação.
- Coverage.py: cobertura dos testes.
- Mypy ou Pyright: verificação de tipos.
- Bandit: análise de segurança do código Python.
- Locust ou k6: testes de carga.

A inclusão dessas ferramentas deverá ser gradual e justificada.

## 18.3. Níveis de testes

A estratégia deverá possuir diferentes níveis.

### Testes unitários

Validam componentes isolados.

Exemplos:

- Cálculo de indicadores.
- Formação de candles.
- Regras de estratégias.
- Validação de parâmetros.
- Cálculos de risco.
- Transições de estado dos bots.
- Regras de assinatura.

Deverão ser rápidos e independentes de serviços externos sempre que possível.

### Testes de integração

Validam a comunicação entre componentes.

Exemplos:

- FastAPI com PostgreSQL.
- asyncpg com o banco.
- Alembic com o schema.
- Market Data com persistência.
- Indicadores com candles.
- Bots com estratégias.
- Risk Management com Execution.
- Integração com serviços da Deriv em ambiente controlado.

### Testes de ponta a ponta (E2E)

Validam fluxos completos.

Exemplo:

```text
Cliente autenticado
       |
       v
Conta Deriv autorizada
       |
       v
Bot configurado
       |
       v
Estratégia avaliada
       |
       v
Sinal gerado
       |
       v
Risco validado
       |
       v
Operação solicitada
       |
       v
Resultado reconciliado
```

Os testes E2E deverão validar também os caminhos de falha.

## 18.4. Testes de regressão

Toda alteração deverá preservar funcionalidades anteriormente aprovadas.

A suíte de regressão deverá ser executada antes de integrar mudanças relevantes.

O resultado histórico de referência é de 27 testes aprovados em uma execução anterior.

Esse número representa um baseline histórico, não o estado garantido da suíte atual.

Regras:

- Não remover testes apenas para fazer uma alteração passar.
- Não reduzir a cobertura sem justificativa.
- Corrigir a causa dos problemas.
- Adicionar testes para novos comportamentos.
- Registrar falhas conhecidas.
- Comparar resultados antes e depois das mudanças.

## 18.5. Testes de Market Data

O módulo de Market Data deverá possuir testes específicos.

### CandleBuilder

Validar:

- Abertura como primeiro preço recebido.
- Máxima como maior preço.
- Mínima como menor preço.
- Fechamento como último preço.
- Mudança de minuto.
- Encerramento do candle anterior.
- Candle em formação.
- Reinicialização do coletor.
- Ausência de ticks.
- Mudança de ativo.
- Ordenação temporal.

### Persistência

Validar:

- Inserção de candles.
- Ausência de duplicidade.
- Atualização por recuperação histórica.
- Não sobrescrita por ingestão ao vivo.
- Integridade dos valores OHLC.
- Persistência em UTC.
- Consultas por ativo e período.

### Recuperação

Validar:

- Reconexão.
- Recuperação de histórico.
- Falha na conexão histórica.
- Falha na conexão ao vivo.
- Recuperação incremental.
- Sobreposição de dados históricos e ao vivo.

Não deverá ser criado candle artificial para preencher períodos sem dados.

## 18.6. Testes de indicadores e estratégias

Os indicadores deverão ser testados matematicamente.

Para cada indicador:

- Fórmula.
- Parâmetros.
- Período mínimo de histórico.
- Tratamento de valores ausentes.
- Precisão numérica.
- Comportamento inicial.
- Atualização incremental.

O cálculo incremental deverá produzir resultados compatíveis com o recálculo completo, respeitando a precisão definida.

As estratégias deverão ser testadas quanto a:

- Condições de entrada.
- Condições de saída.
- Filtros.
- Parâmetros.
- Geração de sinais.
- Deduplicação.
- Versionamento.
- Alterações de configuração.

Os testes deverão utilizar séries históricas controladas, com resultados esperados conhecidos.

## 18.7. Testes de bots

O módulo de bots deverá validar:

- Criação.
- Configuração.
- Inicialização.
- Pausa.
- Retomada.
- Encerramento.
- Suspensão.
- Recuperação após reinicialização.
- Concorrência.
- Duplicidade de execução.
- Associação correta com cliente e conta Deriv.

Deverão ser testadas todas as transições de estado permitidas.

Transições inválidas deverão ser rejeitadas.

## 18.8. Testes de gestão de risco

O módulo de risco deverá possuir testes de prioridade elevada.

Validar:

- Limite por operação.
- Exposição máxima.
- Perda diária.
- Perda acumulada.
- Saldo mínimo.
- Número máximo de operações.
- Limites por bot.
- Limites por conta.
- Limites por cliente.
- Bloqueios automáticos.
- Reservas simultâneas.
- Liberação de reservas.
- Operações com resultado desconhecido.

Nenhuma operação deverá chegar ao módulo de execução sem autorização válida do Risk Management.

Solicitações manuais deverão passar pelas mesmas regras aplicadas aos sinais automáticos.

## 18.9. Testes de execução

O módulo de execução deverá testar todos os estados relevantes.

Exemplos:

- Solicitação criada.
- Proposta recebida.
- Proposta rejeitada.
- Compra confirmada.
- Compra rejeitada.
- Timeout.
- Resposta desconhecida.
- Contrato aberto.
- Contrato encerrado.
- Venda antecipada.
- Falha na consulta do contrato.
- Reconciliação.

Um cenário especialmente importante é o timeout após uma solicitação de compra.

O sistema deverá verificar o estado real na Deriv antes de tentar executar novamente.

Testes deverão comprovar que uma falha de comunicação não provoca duplicidade de operações financeiras.

## 18.10. Testes da integração Deriv

A integração deverá possuir testes separados por funcionalidade.

Validar:

- Estabelecimento de conexão.
- Autenticação.
- Envio de solicitações.
- Correlação de respostas.
- Identificação de erros.
- Subscrições.
- Cancelamento de subscrições.
- Reconexão.
- Timeout.
- Limites de frequência.
- Mudanças de protocolo ou schema.

Os testes unitários deverão utilizar respostas simuladas.

Testes de integração poderão utilizar a conta demo e os recursos oficiais disponíveis.

A conta real não deverá ser utilizada em testes automatizados comuns.

## 18.11. Testes de segurança

Deverão existir testes para:

- Login inválido.
- Expiração de sessão.
- Revogação de sessão.
- Controle de permissões.
- Isolamento entre clientes.
- Acesso indevido a recursos.
- Proteção de tokens.
- Endpoints administrativos.
- Rate limiting.
- Separação entre demo e real.
- Bloqueio por assinatura expirada.
- Revogação de autorização Deriv.

A tentativa de acessar dados de outro cliente deverá resultar em negação de acesso.

## 18.12. Testes de banco de dados

Validar:

- Aplicação de migrações.
- Integridade referencial.
- Restrições.
- Índices.
- Consultas críticas.
- Transações.
- Concorrência.
- Persistência após reinicialização.
- Recuperação de backup.

Os testes deverão utilizar banco isolado, sem comprometer dados de desenvolvimento ou produção.

## 18.13. Testes de desempenho

A plataforma deverá ser avaliada em diferentes condições.

### Market Data

Métricas:

- Ticks recebidos por segundo.
- Candles processados.
- Tempo entre recebimento e persistência.
- Tamanho da fila.
- Tempo de gravação em lote.
- Atraso de ingestão.

### Indicadores e estratégias

Métricas:

- Tempo de cálculo.
- Quantidade de ativos processados.
- Quantidade de estratégias avaliadas.
- Tempo de geração de sinais.
- Consumo de CPU e memória.

### Bots e execução

Métricas:

- Bots ativos simultaneamente.
- Tempo de processamento de eventos.
- Latência de solicitação.
- Operações simultâneas.
- Tempo de reconciliação.

### Banco de dados

Métricas:

- Latência de consultas.
- Tempo de escrita.
- Conexões ativas.
- Locks.
- Uso de armazenamento.
- Crescimento das tabelas.

Os limites de desempenho deverão ser definidos com base em testes representativos, e não em estimativas sem medição.

## 18.14. Testes de carga e resistência

Além dos testes convencionais, deverão ser executados:

- Testes de carga.
- Testes de estresse.
- Testes de longa duração.
- Testes de concorrência.
- Testes de recuperação.
- Testes de interrupção de serviços.

O objetivo é verificar se o sistema mantém comportamento previsível sob pressão.

Deverá ser observado se filas crescem continuamente, se conexões ficam presas e se operações são duplicadas após reinicializações.

## 18.15. Simulação de falhas

A plataforma deverá ser testada em cenários de falha controlada.

Exemplos:

- PostgreSQL indisponível.
- Deriv WebSocket desconectado.
- Timeout de rede.
- Worker encerrado inesperadamente.
- API reiniciada.
- Falha durante persistência.
- Resposta incompleta.
- Evento duplicado.
- Evento fora de ordem.
- Disco próximo da capacidade máxima.

A recuperação deverá preservar a integridade dos dados e impedir execução duplicada de operações.

## 18.16. Testes com conta demo

A conta demo será o ambiente inicial para validar os fluxos de integração e operação.

Deverão ser testados:

1. Autorização.
2. Identificação da conta.
3. Consulta de informações permitidas.
4. Proposta de contrato.
5. Compra.
6. Monitoramento.
7. Encerramento.
8. Histórico.
9. Reconciliação.

Os testes deverão utilizar valores controlados e limites conservadores.

A conta demo será utilizada para validar o comportamento técnico, mas não será considerada garantia de que todos os comportamentos serão idênticos em produção.

## 18.17. Critérios para liberar operações reais

A liberação do ambiente real dependerá de aprovação formal.

Requisitos mínimos:

- Integração Deriv validada.
- Autorização e revogação testadas.
- Isolamento entre clientes comprovado.
- Gestão de risco implementada.
- Idempotência nas operações críticas.
- Reconciliação implementada.
- Auditoria funcional.
- Backups testados.
- Monitoramento ativo.
- Testes de segurança realizados.
- Testes com conta demo aprovados.
- Procedimento de emergência documentado.

A liberação deverá ocorrer inicialmente de forma controlada, com limites reduzidos e monitoramento reforçado.

## 18.18. Pipeline de qualidade

O pipeline deverá executar as verificações automaticamente.

```text
Alteração no código
       |
       v
Análise estática
       |
       v
Testes unitários
       |
       v
Testes de integração
       |
       v
Testes de regressão
       |
       v
Verificação de segurança
       |
       v
Build
       |
       v
Aprovação
       |
       v
Publicação
```

Falhas em verificações obrigatórias deverão bloquear a publicação.

## 18.19. Critérios de aceitação

A estratégia de qualidade será considerada implementada quando:

1. Cada módulo possuir testes próprios.
2. Os fluxos críticos possuírem testes de integração.
3. Os principais fluxos possuírem testes E2E.
4. A suíte de regressão estiver automatizada.
5. As operações financeiras possuírem testes de falha.
6. O isolamento entre clientes estiver comprovado.
7. Os testes de desempenho possuírem métricas documentadas.
8. A recuperação após falhas tiver sido validada.
9. A conta demo tiver sido utilizada para testes operacionais.
10. Existir um processo formal de aprovação para produção.

## 18.20. Situação atual

| Recurso | Situação |
|---|---|
| Pytest | Implementado |
| pytest-asyncio | Implementado |
| HTTPX | Implementado |
| Testes de health check | Implementados |
| Testes de Market Data | Parcialmente implementados, a auditar |
| Testes de integração com PostgreSQL | A auditar |
| Testes de indicadores | Planejados |
| Testes de bots | Planejados |
| Testes de risco | Planejados |
| Testes de execução | Planejados |
| Testes de segurança | Planejados |
| Testes de carga | Planejados |
| Pipeline CI/CD | Planejado |
| Validação operacional completa em demo | Pendente |

## 18.21. Decisão arquitetural

A qualidade será tratada como requisito obrigatório em todas as etapas de desenvolvimento.

Nenhum módulo crítico deverá ser considerado concluído apenas porque seu código foi implementado.

A aprovação deverá depender de testes funcionais, de integração, de segurança e de comportamento sob falhas.

A conta demo será o ambiente inicial de validação operacional.

A utilização de contas reais somente será liberada após o cumprimento dos critérios de segurança, risco, execução e confiabilidade definidos nesta documentação.

# Capítulo 19 — Desempenho, Concorrência e Escalabilidade dos Robôs

## 19.1. Objetivo

Estabelecer a arquitetura de desempenho e concorrência da plataforma Deriv.

O backend deverá ser capaz de:

- Operar múltiplos robôs simultaneamente.
- Atender vários clientes sem interferência entre eles.
- Monitorar diferentes ativos.
- Compartilhar dados de mercado entre robôs.
- Calcular indicadores sem processamento redundante.
- Processar sinais e operações com baixa latência.
- Evitar bloqueios e duplicidade de execução.
- Crescer horizontalmente quando necessário.
- Preservar a integridade das operações financeiras sob concorrência.

O desempenho deverá ser tratado como requisito arquitetural, não apenas como otimização posterior.

## 19.2. Princípios de desempenho

A arquitetura deverá seguir estes princípios:

1. **Compartilhamento de recursos:** evitar conexões e cálculos duplicados.
2. **Processamento assíncrono:** utilizar operações assíncronas para I/O.
3. **Isolamento:** um robô lento ou com falha não deverá bloquear os demais.
4. **Concorrência controlada:** limitar tarefas simultâneas conforme a capacidade disponível.
5. **Baixa latência:** reduzir etapas desnecessárias no caminho entre sinal e execução.
6. **Persistência eficiente:** utilizar escrita em lote quando apropriado.
7. **Idempotência:** impedir processamento duplicado de eventos e solicitações.
8. **Escalabilidade gradual:** aumentar a infraestrutura conforme métricas reais.
9. **Previsibilidade:** evitar crescimento ilimitado de filas, conexões e tarefas.

## 19.3. Arquitetura de processamento compartilhado

Os dados de mercado deverão ser coletados uma única vez por ativo e distribuídos internamente aos consumidores interessados.

Exemplo:

```text
                 DERIV
                   |
                   v
             Market Data
                   |
             CandleBuilder
                   |
          Candle fechado (M1)
                   |
          +--------+--------+
          |                 |
          v                 v
      Indicadores       Persistência
          |
          v
       Estratégias
          |
     +----+----+
     |    |    |
     v    v    v
    Bot 1 Bot 2 Bot 3
     |    |    |
     v    v    v
    Risk Management
          |
          v
       Execution
          |
          v
         DERIV
```

A coleta de mercado será compartilhada entre os robôs que utilizarem o mesmo ativo.

Cada robô manterá suas próprias configurações, estratégias, limites de risco e estado operacional.

**Decisão:** compartilhar infraestrutura e dados de mercado, mas manter a execução e o contexto operacional independentes por robô.

## 19.4. Gerenciamento de conexões Deriv

Não deverá existir uma conexão WebSocket independente para cada robô por padrão.

A arquitetura deverá reutilizar conexões sempre que o protocolo e o contexto de autorização permitirem.

Responsabilidades:

- Gerenciar conexões.
- Controlar solicitações e respostas.
- Correlacionar mensagens.
- Gerenciar subscrições.
- Detectar desconexões.
- Reconectar.
- Distribuir eventos.
- Respeitar limites da API.

Conexões públicas de Market Data poderão atender diversos robôs.

Conexões privadas deverão respeitar o contexto de autorização e a conta Deriv correspondente.

Não se deverá misturar informações privadas de clientes diferentes em um mesmo contexto de autorização.

A quantidade de conexões deverá ser definida pelas necessidades técnicas e pelas regras atuais da Deriv.

## 19.5. Processamento assíncrono

O backend utiliza Python e FastAPI. O processamento de I/O deverá priorizar recursos assíncronos.

Exemplos:

- Comunicação WebSocket.
- Consultas ao PostgreSQL.
- Comunicação HTTP.
- Recebimento de eventos.
- Persistência de dados.
- Monitoramento de contratos.

Operações de I/O não deverão bloquear desnecessariamente o event loop.

Cálculos intensivos de CPU deverão ser tratados separadamente, quando o volume justificar.

Possibilidades:

- Processamento em processos independentes.
- Workers especializados.
- Bibliotecas otimizadas.
- Cálculos incrementais.
- Distribuição de tarefas.

Não se deverá executar trabalho pesado de forma síncrona dentro do fluxo principal de recebimento de mensagens.

## 19.6. Filas e controle de fluxo

A comunicação entre componentes deverá utilizar filas com capacidade controlada.

Exemplo:

```text
WebSocket
    |
    v
Fila de entrada
    |
    v
Processamento de mercado
    |
    v
Fila de persistência
    |
    v
PostgreSQL
```

As filas deverão possuir:

- Capacidade máxima.
- Monitoramento de tamanho.
- Política de backpressure.
- Tratamento de falhas.
- Política de repetição quando apropriada.
- Identificação de eventos.
- Proteção contra crescimento ilimitado.

Quando uma fila atingir sua capacidade, o sistema deverá aplicar uma política explícita.

Não será permitido descartar silenciosamente eventos necessários para preservar a integridade do histórico ou das operações.

Para eventos financeiros e solicitações de execução, a persistência e a recuperação deverão ser prioritárias.

## 19.7. Persistência eficiente

A gravação dos candles deverá utilizar o mecanismo de persistência em lote já previsto no Market Data.

Parâmetros como tamanho do lote e intervalo de flush deverão ser configuráveis.

A arquitetura deverá equilibrar:

- Latência de persistência.
- Quantidade de operações SQL.
- Consumo de memória.
- Capacidade do PostgreSQL.
- Risco de perda de dados em falhas.

O lote não deverá crescer indefinidamente.

As operações financeiras deverão utilizar persistência adequada à criticidade de cada etapa, sem depender exclusivamente de lotes periódicos.

## 19.8. Cálculo compartilhado de indicadores

Quando diferentes robôs utilizarem o mesmo indicador, ativo, timeframe e parâmetros, o sistema deverá evitar cálculos idênticos repetidos.

Exemplo:

```text
Ativo: 1HZ100V
Timeframe: M1
Indicador: EMA
Período: 20

       |
       v
Cálculo compartilhado
       |
   +---+---+
   |       |
   v       v
 Bot A   Bot B
```

A reutilização somente será permitida quando todos os parâmetros relevantes forem equivalentes.

A chave lógica de identificação deverá considerar:

- Ativo.
- Timeframe.
- Indicador.
- Parâmetros.
- Versão do algoritmo.
- Tipo de dado utilizado.

O resultado de um indicador baseado em candle provisório deverá ser distinguido daquele baseado em candle fechado.

## 19.9. Processamento independente dos robôs

Cada robô deverá possuir contexto operacional próprio.

Esse contexto deverá conter:

- Identificador do robô.
- Cliente proprietário.
- Conta Deriv.
- Ambiente demo ou real.
- Estratégia e versão.
- Ativos monitorados.
- Timeframes.
- Configurações.
- Perfil de risco.
- Estado operacional.
- Execuções em andamento.

A falha de um robô não deverá interromper o processamento dos demais.

O sistema deverá evitar que uma estratégia lenta ou um cliente com grande quantidade de robôs monopolize os recursos.

Deverão existir limites configuráveis por cliente e por robô.

## 19.10. Concorrência e prevenção de duplicidade

A plataforma deverá impedir que o mesmo sinal gere múltiplas operações indevidas.

A proteção deverá existir em diferentes níveis:

- Deduplicação de sinais.
- Controle de execução por robô.
- Chaves de idempotência.
- Restrições únicas no banco.
- Controle de concorrência.
- Identificação de solicitações.
- Reconciliação com a Deriv.

Um sinal deverá possuir identidade estável, considerando o robô, a estratégia, o ativo, o timeframe, o candle de referência e o tipo de sinal.

Antes de executar uma operação, o sistema deverá verificar se já existe uma solicitação correspondente em processamento ou concluída.

A proteção não deverá depender apenas de verificações em memória.

## 19.11. Controle de propriedade e execução de bots

Quando houver múltiplas instâncias de workers, deverá existir um mecanismo para garantir que apenas um executor seja responsável por determinado contexto operacional.

Possibilidades:

- Locks no PostgreSQL.
- Leases com prazo de validade.
- Controle de propriedade por worker.
- Heartbeats.
- Identificação de instância.
- Recuperação após expiração de lease.

O mecanismo escolhido deverá permitir que outro worker assuma o processamento quando a instância responsável falhar.

A troca de responsável não poderá provocar execução duplicada.

Locks distribuídos deverão possuir timeout e estratégia de recuperação. Um lock permanente não poderá bloquear indefinidamente um robô.

## 19.12. Ordem dos eventos

A plataforma deverá preservar a ordem dos eventos quando ela for necessária para a lógica operacional.

Exemplos:

- Atualização de candles de um mesmo ativo.
- Transições de estado de um bot.
- Eventos de um contrato.
- Solicitações de execução.
- Reconciliação financeira.

Não será necessário impor ordenação global a todos os eventos.

A ordenação deverá ser definida por contexto, como ativo, robô, conta ou contrato.

Eventos duplicados ou fora de ordem deverão ser detectados e tratados de maneira segura.

## 19.13. Agendamento e distribuição de tarefas

O processamento dos robôs deverá ser organizado para evitar sobrecarga.

O sistema deverá considerar:

- Quantidade de robôs ativos.
- Quantidade de ativos por robô.
- Timeframes utilizados.
- Frequência de avaliação.
- Custo computacional das estratégias.
- Limites de execução.
- Disponibilidade de recursos.

A avaliação deverá priorizar eventos relevantes, evitando ciclos de consulta desnecessários.

Quando vários robôs dependerem do mesmo candle fechado, o evento poderá ser distribuído a todos os consumidores interessados.

O agendamento não deverá gerar tarefas repetitivas sem necessidade.

## 19.14. Pool de conexões PostgreSQL

O backend deverá utilizar pool de conexões para evitar a abertura indiscriminada de conexões com o banco.

O pool deverá possuir:

- Limite mínimo e máximo.
- Timeout para aquisição.
- Timeout de conexão.
- Controle de conexões inativas.
- Monitoramento de utilização.
- Tratamento de indisponibilidade.

O tamanho do pool deverá considerar todas as instâncias da aplicação.

A soma das conexões máximas de todas as instâncias não poderá exceder a capacidade operacional do PostgreSQL.

## 19.15. Escalabilidade horizontal

A arquitetura deverá permitir adicionar instâncias de processamento sem alterar as regras de negócio.

Possível evolução:

```text
                 API
                  |
          Distribuição de tarefas
                  |
       +----------+----------+
       |          |          |
       v          v          v
    Worker 1   Worker 2   Worker 3
       |          |          |
       +----------+----------+
                  |
             PostgreSQL
```

A distribuição deverá considerar o tipo de tarefa e a propriedade do contexto operacional.

Não se deverá iniciar várias instâncias independentes de um mesmo coletor ou executor sem mecanismo de coordenação.

A escalabilidade horizontal deverá ser introduzida quando as métricas demonstrarem necessidade.

## 19.16. Limites de recursos

A plataforma deverá possuir limites configuráveis para evitar consumo descontrolado.

Exemplos:

- Máximo de robôs ativos por cliente.
- Máximo de ativos monitorados.
- Máximo de estratégias simultâneas.
- Máximo de operações concorrentes.
- Máximo de tarefas por worker.
- Máximo de conexões com o banco.
- Capacidade máxima das filas.
- Tempo máximo de processamento de tarefas.

Os limites comerciais poderão depender do plano contratado.

Os limites técnicos deverão considerar a capacidade real da infraestrutura.

O plano do cliente não deverá permitir ultrapassar limites de segurança ou estabilidade da plataforma.

## 19.17. Métricas de desempenho

O sistema deverá monitorar:

| Métrica | Finalidade |
|---|---|
| Ticks recebidos por segundo | Medir ingestão de mercado. |
| Atraso dos candles | Detectar atraso na coleta. |
| Tamanho das filas | Detectar acúmulo de tarefas. |
| Tempo de persistência | Medir gravação no banco. |
| Tempo de cálculo dos indicadores | Medir processamento. |
| Tempo de avaliação das estratégias | Medir geração de sinais. |
| Latência de execução | Medir o caminho até a Deriv. |
| Bots ativos | Medir carga operacional. |
| CPU e memória | Medir utilização dos recursos. |
| Conexões PostgreSQL | Detectar saturação do banco. |
| Eventos duplicados | Identificar problemas de concorrência. |
| Operações desconhecidas | Identificar necessidade de reconciliação. |

As métricas deverão ser segmentadas por serviço e, quando necessário, por cliente e robô, sem expor informações sensíveis.

## 19.18. Definição de metas de desempenho

A plataforma deverá estabelecer metas mensuráveis antes da produção.

Exemplos de indicadores:

- Latência de ingestão.
- Tempo entre fechamento do candle e avaliação da estratégia.
- Tempo de resposta da API.
- Tempo de persistência.
- Quantidade de bots simultâneos.
- Taxa de erros.
- Tempo de recuperação de workers.

Os limites deverão ser definidos por testes de carga e condições reais de operação.

Não deverá ser estabelecida uma promessa de latência inferior ao tempo de resposta da própria Deriv.

A latência externa deverá ser medida separadamente da latência interna da plataforma.

## 19.19. Recuperação e continuidade operacional

Após reinicialização de um serviço, o sistema deverá recuperar seu estado a partir de informações persistidas.

Requisitos:

- Recuperar bots ativos.
- Identificar operações em andamento.
- Reconciliar contratos.
- Reestabelecer subscrições.
- Recuperar histórico de mercado.
- Reprocessar eventos pendentes.
- Reconhecer solicitações já concluídas.
- Evitar duplicidade.

A memória de um processo não poderá ser a única fonte de verdade para estados críticos.

O reinício de um worker não poderá ser interpretado como autorização para repetir operações.

## 19.20. Estratégia de evolução

A evolução deverá ocorrer em etapas.

### Etapa 1 — Arquitetura inicial

- Um backend.
- PostgreSQL.
- Market Data compartilhado.
- Workers assíncronos.
- Filas limitadas em memória para fluxos apropriados.
- Controle de concorrência no banco.
- Métricas básicas.

### Etapa 2 — Separação de processamento

- API independente.
- Worker de Market Data.
- Worker de bots.
- Worker de execução.
- Controle de propriedade dos workers.
- Monitoramento ampliado.

### Etapa 3 — Escalabilidade horizontal

- Múltiplas instâncias.
- Distribuição de tarefas.
- Mecanismo de filas duráveis quando necessário.
- Coordenação distribuída.
- Recuperação automática.
- Controle avançado de capacidade.

A adoção de Redis, RabbitMQ, Kafka ou outras tecnologias não será automática. Deverá ocorrer somente quando houver necessidade comprovada.

## 19.21. Testes e critérios de aceitação

A arquitetura será considerada adequada quando:

1. Vários robôs puderem operar simultaneamente.
2. A coleta de um mesmo ativo for compartilhada.
3. Indicadores equivalentes não forem calculados repetidamente sem necessidade.
4. Um robô não bloquear os demais.
5. Eventos duplicados não gerarem operações duplicadas.
6. Workers puderem assumir tarefas com segurança.
7. Filas possuírem limites e backpressure.
8. O pool do banco respeitar a capacidade configurada.
9. A reinicialização não duplicar execuções.
10. Operações desconhecidas forem reconciliadas.
11. Métricas de desempenho estiverem disponíveis.
12. A capacidade máxima suportada for documentada por testes.

## 19.22. Situação atual

| Recurso | Situação |
|---|---|
| FastAPI assíncrono | Implementado |
| Comunicação assíncrona com PostgreSQL | Implementada |
| Coleta compartilhada de Market Data | Parcial, conforme implementação atual |
| Persistência em lote | Implementada no serviço de Market Data |
| Cálculo compartilhado de indicadores | Planejado |
| Processamento independente dos bots | Planejado |
| Controle distribuído de execução | Planejado |
| Deduplicação completa de operações | Planejada |
| Filas duráveis | Planejadas, se necessárias |
| Escalabilidade horizontal | Planejada |
| Métricas de desempenho completas | Planejadas |
| Testes de carga | Pendentes |

## 19.23. Decisão arquitetural

A plataforma deverá compartilhar dados de mercado e cálculos equivalentes, mantendo independência operacional entre robôs e clientes.

O processamento deverá ser assíncrono, limitado e monitorado.

A concorrência deverá ser controlada por mecanismos persistentes e idempotentes, não apenas por variáveis em memória.

A escalabilidade será gradual, começando com uma arquitetura simples e evoluindo para múltiplos workers e instâncias quando os testes e as métricas justificarem.

A prioridade será preservar a integridade das operações financeiras, mesmo sob alta concorrência ou falhas de infraestrutura.

# Capítulo 20 — Fluxos Operacionais Completos e Ciclo de Vida de uma Operação

## 20.1. Objetivo

Documentar os fluxos operacionais da plataforma, estabelecendo a sequência de processamento, as responsabilidades dos módulos e as condições necessárias para cada etapa.

O objetivo é garantir que todos os componentes trabalhem de maneira coordenada, segura e rastreável.

Este capítulo contempla:

- Entrada de clientes na plataforma.
- Vinculação de contas Deriv.
- Ativação de planos e período de avaliação.
- Inicialização dos robôs.
- Coleta e processamento de dados de mercado.
- Cálculo de indicadores.
- Avaliação de estratégias.
- Geração de sinais.
- Validação de risco.
- Execução de operações.
- Acompanhamento de contratos.
- Encerramento.
- Conciliação.
- Tratamento de falhas.

## 20.2. Visão geral da arquitetura operacional

O fluxo principal da plataforma será:

```text
CLIENTE
   |
   v
Autenticação
   |
   v
Conta Deriv vinculada
   |
   v
Plano e autorização validados
   |
   v
Bot configurado e iniciado
   |
   v
MARKET DATA
   |
   v
Candles
   |
   v
INDICADORES
   |
   v
ESTRATÉGIAS
   |
   v
SINAIS
   |
   v
BOTS
   |
   v
GESTÃO DE RISCO
   |
   v
EXECUTION
   |
   v
DERIV API
   |
   v
Acompanhamento do contrato
   |
   v
Encerramento e resultado
   |
   v
CONCILIAÇÃO E AUDITORIA
```

Cada módulo deverá cumprir sua responsabilidade sem assumir funções pertencentes aos demais.

## 20.3. Fluxo de cadastro do cliente

O cadastro deverá ocorrer independentemente da conta Deriv.

Sequência:

1. Cliente acessa a plataforma.
2. Informa os dados necessários.
3. O backend valida as informações.
4. O usuário é criado.
5. O sistema inicia o processo de verificação de e-mail.
6. O cliente realiza a autenticação.
7. O sistema cria sua sessão.
8. O cliente acessa sua área de gerenciamento.

O cadastro não deverá iniciar automaticamente operações de negociação.

A conta Deriv será vinculada em um fluxo separado.

## 20.4. Fluxo de vinculação da conta Deriv

O cliente deverá autorizar a plataforma por meio do mecanismo oficial disponibilizado pela Deriv.

Sequência:

1. Cliente solicita vinculação.
2. Backend inicia o fluxo oficial de autorização.
3. Cliente concede as permissões solicitadas.
4. Backend recebe a resposta de autorização.
5. A autorização é validada.
6. A conta Deriv é identificada.
7. O ambiente demo ou real é identificado.
8. Os escopos concedidos são verificados.
9. As credenciais necessárias são armazenadas de maneira segura.
10. A conta passa a constar como vinculada.

Regras:

- Nunca solicitar a senha Deriv.
- Não armazenar tokens em texto aberto.
- Solicitar somente permissões necessárias.
- Não permitir operações sem autorização válida.
- Manter demo e real claramente identificados.

O protocolo e os detalhes do fluxo deverão seguir a documentação oficial vigente da Deriv.

## 20.5. Fluxo de ativação do plano

O período inicial de avaliação será uma regra comercial da plataforma.

Recomendação: iniciar os sete dias de avaliação quando o cliente ativar explicitamente o teste, e não simplesmente quando criar seu cadastro.

Sequência:

1. Cliente solicita início do período de avaliação.
2. Backend verifica sua elegibilidade.
3. A avaliação é registrada.
4. A data de início é persistida.
5. A data de expiração é calculada.
6. O acesso aos recursos permitidos é liberado.

Ao término do período:

- O sistema deverá verificar o estado da assinatura.
- Novas operações deverão ser bloqueadas quando não houver acesso válido.
- Bots deverão entrar em encerramento controlado.
- Contratos já abertos deverão continuar sendo acompanhados.
- O histórico deverá ser preservado.

## 20.6. Fluxo de configuração de um bot

Antes de iniciar um bot, o cliente deverá configurar:

- Nome.
- Conta Deriv.
- Ambiente demo ou real.
- Estratégia.
- Versão da estratégia.
- Ativos.
- Timeframes.
- Parâmetros dos indicadores.
- Regras de entrada e saída.
- Perfil de risco.
- Limites operacionais.

O backend deverá validar os parâmetros.

A configuração aprovada deverá possuir versão ou snapshot para preservar o contexto operacional.

Alterações posteriores não deverão modificar silenciosamente a configuração de uma execução já iniciada.

## 20.7. Fluxo de inicialização do bot

O início do bot deverá ocorrer por uma solicitação controlada.

Sequência:

1. Cliente solicita inicialização.
2. API autentica o usuário.
3. Sistema verifica a propriedade do bot.
4. Valida a assinatura.
5. Valida a conta Deriv vinculada.
6. Confirma a autorização necessária.
7. Confirma o ambiente demo ou real.
8. Valida a configuração.
9. Verifica os limites de risco.
10. Confirma a disponibilidade dos ativos.
11. Registra a execução do bot.
12. Altera o estado para Running.
13. Registra o evento de inicialização.

Se alguma validação obrigatória falhar, o bot não deverá iniciar.

## 20.8. Fluxo de coleta de dados de mercado

O Market Data deverá manter a coleta dos ativos utilizados pelos robôs.

Sequência:

1. Identificar os ativos necessários.
2. Verificar se já existe coleta ativa.
3. Criar subscrição quando necessário.
4. Receber ticks da Deriv.
5. Atualizar o CandleBuilder.
6. Detectar mudança de minuto.
7. Finalizar o candle anterior.
8. Persistir o candle fechado.
9. Distribuir o evento internamente.
10. Atualizar o estado de saúde da coleta.

A coleta deverá ser compartilhada entre os robôs interessados no mesmo ativo.

A desconexão deverá acionar o mecanismo de reconexão e recuperação histórica.

## 20.9. Fluxo de cálculo dos indicadores

Quando um candle fechado for recebido:

1. O sistema identifica o ativo e timeframe.
2. Verifica os indicadores necessários.
3. Consulta o histórico persistido.
4. Atualiza os cálculos.
5. Armazena os valores quando necessário.
6. Publica os resultados.
7. Disponibiliza os dados às estratégias interessadas.

O processamento deverá evitar cálculos duplicados para combinações equivalentes de ativo, timeframe, indicador e parâmetros.

Resultados baseados em candles provisórios deverão ser identificados separadamente.

## 20.10. Fluxo de avaliação das estratégias

Cada estratégia deverá avaliar os dados disponíveis conforme sua configuração.

Sequência:

1. Receber atualização de mercado ou indicador.
2. Identificar os bots interessados.
3. Verificar se a estratégia está habilitada.
4. Consultar os indicadores necessários.
5. Avaliar condições de entrada.
6. Avaliar condições de saída.
7. Aplicar filtros.
8. Gerar sinal quando houver condição válida.
9. Registrar o sinal.
10. Publicar o evento para o bot correspondente.

A estratégia não deverá enviar ordens diretamente à Deriv.

Sua responsabilidade será produzir sinais e justificativas estruturadas.

## 20.11. Fluxo de geração e validação do sinal

O sinal deverá conter contexto suficiente para rastrear sua origem.

Informações mínimas:

- Identificador do sinal.
- Cliente.
- Bot.
- Estratégia.
- Versão da estratégia.
- Ativo.
- Timeframe.
- Tipo de sinal.
- Candle de referência.
- Preço de referência.
- Indicadores utilizados.
- Parâmetros relevantes.
- Horário de geração.

Antes de encaminhar o sinal à execução, o bot deverá verificar:

- Estado Running.
- Configuração válida.
- Ausência de bloqueio.
- Ausência de execução duplicada.
- Disponibilidade do contexto operacional.

## 20.12. Fluxo de gestão de risco

Todo sinal deverá passar pelo Risk Management.

Sequência:

1. Receber solicitação de operação.
2. Identificar cliente, conta e bot.
3. Validar limites globais.
4. Validar limites do cliente.
5. Validar limites da conta.
6. Validar limites do bot.
7. Verificar exposição atual.
8. Verificar reservas existentes.
9. Calcular exposição potencial.
10. Aprovar ou rejeitar.
11. Registrar a decisão.

Uma aprovação deverá gerar uma autorização identificável e vinculada aos parâmetros específicos da operação.

A autorização deverá possuir validade limitada e não poderá ser reutilizada livremente.

Solicitações manuais deverão passar pelo mesmo fluxo.

## 20.13. Fluxo de execução na Deriv

O módulo Execution será o único responsável pelo ciclo de vida das operações.

Sequência:

1. Receber solicitação aprovada pelo Risk Management.
2. Validar a autorização de risco.
3. Validar a conta e o contexto.
4. Consultar ou solicitar proposta à Deriv.
5. Validar os parâmetros e valores retornados.
6. Registrar a proposta.
7. Enviar a solicitação de compra.
8. Interpretar a resposta.
9. Registrar o contrato quando confirmado.
10. Atualizar o estado da operação.
11. Iniciar o acompanhamento.

Métodos da API que poderão participar desse fluxo incluem:

- `proposal`
- `buy`
- `proposal_open_contract`
- `sell`
- `portfolio`
- `statement`
- `transaction`

A disponibilidade, os parâmetros e os requisitos de autorização deverão ser confirmados na documentação oficial e nos schemas vigentes da Deriv antes da implementação.

## 20.14. Ciclo de vida da operação

Uma operação deverá possuir estados explícitos.

Modelo lógico:

```text
CREATED
   |
   v
RISK_PENDING
   |
   v
RISK_APPROVED
   |
   v
PROPOSAL_PENDING
   |
   v
PROPOSAL_RECEIVED
   |
   v
BUY_PENDING
   |
   v
OPEN
   |
   v
MONITORING
   |
   +-------> CLOSED
   |
   +-------> SOLD
   |
   +-------> EXPIRED
   |
   +-------> UNKNOWN
```

Estados adicionais poderão representar rejeição, cancelamento, falha ou necessidade de reconciliação.

O estado `UNKNOWN` deverá ser utilizado quando não for possível determinar com segurança se uma solicitação foi concluída.

Esse estado não poderá ser interpretado como falha definitiva.

## 20.15. Fluxo de acompanhamento do contrato

Após a confirmação da compra, o sistema deverá acompanhar o contrato.

Responsabilidades:

- Identificar o contrato.
- Monitorar seu estado.
- Receber atualizações.
- Registrar mudanças relevantes.
- Atualizar exposição.
- Calcular resultados conforme dados disponíveis.
- Detectar encerramento.
- Tratar desconexões.
- Reconciliar informações.

A plataforma deverá manter acompanhamento dos contratos mesmo quando o bot for pausado ou suspenso.

O encerramento do bot não deverá significar abandono de contratos abertos.

## 20.16. Fluxo de encerramento da operação

O contrato poderá terminar por diferentes motivos, conforme o produto utilizado.

Exemplos:

- Expiração natural.
- Venda antecipada, quando permitida.
- Encerramento confirmado pela Deriv.
- Outros estados previstos pelo contrato.

Quando houver encerramento:

1. Receber ou consultar a confirmação.
2. Validar o identificador do contrato.
3. Registrar o resultado.
4. Atualizar o estado da operação.
5. Atualizar exposição e reservas.
6. Registrar o evento.
7. Disponibilizar o resultado ao bot e ao cliente.

O resultado financeiro definitivo deverá ser baseado nas informações confirmadas pela Deriv.

## 20.17. Fluxo de reconciliação

A reconciliação deverá identificar divergências entre os registros internos e as informações da Deriv.

Deverá ocorrer:

- Após respostas incertas.
- Após reconexões.
- Após reinicializações.
- Em verificações periódicas.
- Após encerramentos.
- Durante o fechamento de períodos financeiros.

O sistema deverá comparar:

- Identificadores de contratos.
- Estados.
- Valores de compra.
- Pagamentos.
- Resultados.
- Horários.
- Transações relacionadas.

A Deriv será a fonte de verdade para os resultados efetivamente registrados na conta.

Divergências deverão gerar eventos de auditoria e, quando necessário, alertas.

## 20.18. Fluxo de pausa e parada do bot

### Pausa

Ao pausar:

1. Bloquear novos sinais para execução.
2. Impedir novas operações.
3. Preservar a configuração.
4. Manter acompanhamento de contratos abertos.
5. Registrar o motivo.
6. Atualizar o estado para Paused.

### Parada

Ao parar:

1. Impedir novos sinais.
2. Bloquear novas solicitações.
3. Encerrar o processamento operacional do bot.
4. Manter acompanhamento de contratos ainda abertos.
5. Liberar recursos que não sejam mais necessários.
6. Registrar o encerramento.

O tratamento de contratos abertos deverá permanecer sob responsabilidade do módulo Execution.

## 20.19. Fluxo de falha e recuperação

Quando ocorrer uma falha, o sistema deverá identificar seu impacto.

Exemplos:

| Falha | Comportamento esperado |
|---|---|
| Deriv desconectada | Suspender novas operações dependentes e reconectar. |
| PostgreSQL indisponível | Bloquear operações que dependam de persistência segura. |
| Worker encerrado | Recuperar tarefas pendentes e reconciliar estados. |
| Token revogado | Bloquear novas operações da conta. |
| Assinatura expirada | Bloquear novas operações e encerrar bots controladamente. |
| Limite de risco atingido | Bloquear novas operações conforme a política. |
| Timeout de compra | Consultar o estado na Deriv antes de qualquer repetição. |
| Evento duplicado | Deduplicar sem repetir efeitos financeiros. |

A recuperação deverá preservar o histórico e a rastreabilidade.

## 20.20. Fluxo de desvinculação da conta Deriv

Quando o cliente retirar a autorização:

1. Registrar a solicitação.
2. Bloquear novas operações.
3. Suspender bots associados.
4. Identificar contratos abertos.
5. Manter o acompanhamento permitido dos contratos existentes.
6. Encerrar conexões privadas quando apropriado.
7. Revogar a autorização conforme o mecanismo oficial disponível.
8. Invalidar ou eliminar os tokens armazenados.
9. Registrar a conclusão.

A desvinculação não deverá excluir a conta Deriv do cliente nem afetar seu acesso direto à plataforma oficial da Deriv.

## 20.21. Fluxo de operação manual

Uma operação iniciada manualmente deverá respeitar a mesma arquitetura.

Fluxo:

```text
Cliente
   |
   v
API
   |
   v
Autorização
   |
   v
Validação da conta
   |
   v
Gestão de risco
   |
   v
Execution
   |
   v
Deriv
   |
   v
Acompanhamento
   |
   v
Conciliação
```

Não deverá existir caminho alternativo que permita contornar:

- Permissões.
- Limites de risco.
- Validação da conta.
- Idempotência.
- Auditoria.
- Regras de execução.

A diferença entre operação manual e automática estará na origem da solicitação, não nos controles de segurança.

## 20.22. Rastreabilidade ponta a ponta

Cada operação deverá possuir identificadores que permitam reconstruir todo o fluxo.

Identificadores relevantes:

- `user_id`
- `deriv_account_id`
- `bot_id`
- `bot_run_id`
- `strategy_id`
- `signal_id`
- `risk_reservation_id`
- `trade_request_id`
- `correlation_id`
- `deriv_contract_id`

Os identificadores deverão ser propagados entre os módulos e eventos.

Será possível responder:

- Qual cliente originou a operação?
- Qual bot solicitou?
- Qual estratégia gerou o sinal?
- Quais indicadores foram utilizados?
- Qual regra de risco aprovou?
- Qual proposta foi recebida?
- Qual contrato foi aberto?
- Qual foi o resultado?
- Quando ocorreu cada etapa?

## 20.23. Fluxos de teste e validação

Os fluxos completos deverão ser validados em ambiente controlado.

Cenários mínimos:

1. Cadastro e autenticação.
2. Vinculação de conta demo.
3. Ativação do período de avaliação.
4. Configuração e inicialização do bot.
5. Recebimento de candles.
6. Cálculo de indicadores.
7. Geração de sinal.
8. Aprovação de risco.
9. Solicitação de proposta.
10. Compra e confirmação.
11. Acompanhamento do contrato.
12. Encerramento.
13. Atualização financeira.
14. Reconciliação.
15. Pausa e parada do bot.
16. Revogação da autorização.
17. Recuperação após falhas.
18. Operação manual.

Cada fluxo deverá validar tanto o caminho de sucesso quanto as falhas possíveis.

## 20.24. Situação atual

| Fluxo | Situação |
|---|---|
| Coleta pública de Market Data | Parcialmente implementada |
| Persistência de candles | Implementada na estrutura atual |
| Cadastro e autenticação | Planejados |
| Vinculação de contas Deriv | Planejada |
| Planos e avaliação | Planejados |
| Gestão de bots | Planejada |
| Indicadores | Planejados |
| Estratégias | Planejadas |
| Gestão de risco | Planejada |
| Execução de contratos | Planejada |
| Acompanhamento de contratos | Planejado |
| Reconciliação financeira | Planejada |
| Operações manuais | Planejadas |
| Auditoria completa | Planejada |
| Fluxos E2E completos | Pendentes |

## 20.25. Decisão arquitetural

Todos os fluxos operacionais deverão respeitar a separação de responsabilidades definida nos capítulos anteriores.

O Market Data fornecerá os dados; indicadores e estratégias produzirão sinais; bots coordenarão sua execução; Risk Management autorizará ou rejeitará; Execution será responsável pelas operações na Deriv.

Toda operação, automática ou manual, deverá seguir o mesmo caminho de validação, execução, acompanhamento e reconciliação.

A integridade financeira terá prioridade sobre a continuidade automática de uma operação quando houver incerteza.

Nenhuma falha de comunicação deverá provocar repetição cega de uma solicitação financeira.

A plataforma deverá manter rastreabilidade completa desde a origem do sinal até o resultado confirmado pela Deriv.

# Capítulo 21 — Requisitos Não Funcionais, Disponibilidade e Confiabilidade

## 1. Objetivo

Este capítulo define os requisitos não funcionais da plataforma Deriv.

Enquanto os capítulos anteriores descrevem o que cada módulo deve fazer, este capítulo estabelece como o sistema deve se comportar em termos de desempenho, disponibilidade, confiabilidade, integridade dos dados, segurança e capacidade de evolução.

Os requisitos aqui definidos deverão orientar a implementação, os testes e a operação em produção.

**Importante:** metas descritas neste documento são requisitos de projeto, não resultados de desempenho já comprovados. Nenhuma garantia de disponibilidade ou latência deve ser anunciada antes de medições em ambiente representativo.

## 2. Disponibilidade e níveis de serviço

A plataforma deverá buscar alta disponibilidade, considerando que os robôs podem operar continuamente e dependem de conexões externas com a Deriv.

Devem ser diferenciados:

- **SLI (Service Level Indicator):** indicador efetivamente medido, como percentual de disponibilidade ou latência.
- **SLO (Service Level Objective):** objetivo interno definido para determinado indicador.
- **SLA (Service Level Agreement):** compromisso formal de serviço assumido perante clientes.

Não será estabelecido um SLA comercial antes de existir histórico operacional suficiente para definir metas realistas.

Indicadores a acompanhar:

- Disponibilidade da API.
- Disponibilidade do banco de dados.
- Disponibilidade da coleta de Market Data.
- Percentual de candles recebidos e persistidos corretamente.
- Tempo de recuperação após desconexões.
- Disponibilidade dos serviços de execução e monitoramento.
- Quantidade de operações em estado desconhecido aguardando reconciliação.

## 3. Desempenho e latência

O backend deverá ser otimizado para processar sinais e operações com baixa latência, sem comprometer a integridade financeira.

Devem ser medidos separadamente:

1. Recebimento de dados da Deriv.
2. Processamento e atualização do candle.
3. Persistência no PostgreSQL.
4. Cálculo dos indicadores.
5. Avaliação da estratégia.
6. Geração do sinal.
7. Validação de risco.
8. Solicitação e resposta da Deriv.
9. Atualização do estado da operação.

### 3.1 Métricas de latência

As medições deverão incluir:

- P50: mediana.
- P95: percentil 95.
- P99: percentil 99.
- Máximo observado.
- Taxa de erros e timeouts.

A latência interna deverá ser separada da latência externa da Deriv e da rede. O backend não poderá garantir o tempo de resposta de serviços externos.

### 3.2 Metas de desempenho

As metas numéricas serão definidas após testes de carga e medições do ambiente.

Não se deve otimizar apenas a média: os percentis superiores também precisam ser avaliados, pois atrasos ocasionais podem prejudicar a operação dos robôs.

## 4. Integridade e consistência dos dados

A integridade dos dados é requisito crítico.

Regras fundamentais:

- Candles fechados e persistidos devem ser recuperáveis sem perda silenciosa.
- Cada ativo deve possuir, no máximo, um candle por intervalo temporal.
- Os valores OHLC devem respeitar as regras de consistência definidas no Capítulo 6.
- Operações financeiras devem possuir identificadores e histórico de eventos.
- Comandos financeiros não podem ser repetidos indiscriminadamente após timeout.
- Dados recebidos da Deriv devem ser validados antes de sua utilização.

### 4.1 Fontes de verdade

Cada domínio terá sua referência principal:

| Informação | Fonte de verdade |
|---|---|
| Candles fechados armazenados | PostgreSQL |
| Resultado financeiro confirmado | Deriv |
| Estado operacional dos robôs | Backend |
| Autorizações e permissões | Backend e estado confirmado da autorização Deriv |
| Assinatura e período de avaliação | Backend |
| Comissões e estatísticas de parceiros | Dados oficiais disponibilizados pela Deriv |

Em caso de divergência financeira, a plataforma deverá consultar e reconciliar os dados da Deriv, sem substituir resultados confirmados por estimativas internas.

## 5. Confiabilidade e tolerância a falhas

O sistema deverá continuar funcionando de forma controlada diante de falhas parciais.

Falhas previstas:

- Desconexão do WebSocket da Deriv.
- Indisponibilidade temporária da API externa.
- Reinicialização do backend.
- Indisponibilidade do PostgreSQL.
- Atraso na persistência de candles.
- Falha de processamento de indicadores.
- Erros em estratégias ou robôs.
- Timeout durante solicitação de operação.
- Revogação de autorização.
- Expiração de assinatura ou período de avaliação.

### 5.1 Comportamento esperado

- Reconectar automaticamente quando aplicável.
- Utilizar backoff progressivo para evitar excesso de tentativas.
- Não iniciar operações quando os dados necessários estiverem desatualizados ou indisponíveis.
- Não perder silenciosamente eventos importantes.
- Preservar o estado das operações durante reinicializações.
- Reconciliar operações cujo resultado seja desconhecido.
- Impedir duplicidade de ordens.
- Isolar falhas de um robô para que não comprometam os demais.
- Bloquear novas operações quando não for possível garantir as condições mínimas de segurança.

### 5.2 Degradação controlada

A indisponibilidade de um componente não deverá provocar comportamento financeiro imprevisível.

Exemplos:

- Se o Market Data estiver desatualizado, os robôs dependentes desse ativo devem suspender novas decisões.
- Se o módulo de risco estiver indisponível, novas operações devem ser bloqueadas.
- Se o banco de dados estiver indisponível, não devem ser iniciadas operações que dependam de persistência confiável.
- Se a Deriv estiver indisponível, as solicitações devem aguardar recuperação ou entrar em estado apropriado, sem repetição financeira cega.

## 6. Recuperação e continuidade operacional

A plataforma deverá possuir mecanismos de recuperação após falhas.

### 6.1 RPO e RTO

- **RPO (Recovery Point Objective):** quantidade máxima de dados que se admite perder após um incidente.
- **RTO (Recovery Time Objective):** tempo máximo desejado para restabelecer o serviço.

Os valores numéricos de RPO e RTO ainda precisam ser definidos conforme a criticidade e os custos da infraestrutura.

### 6.2 Backups

O PostgreSQL deverá possuir:

- Backups periódicos.
- Proteção dos arquivos de backup.
- Retenção definida.
- Testes periódicos de restauração.
- Procedimento documentado de recuperação.

A existência de um backup não será considerada suficiente sem testes de restauração.

### 6.3 Recuperação de Market Data

Após uma interrupção:

1. Restabelecer a conexão de coleta.
2. Identificar o último candle persistido.
3. Consultar o histórico necessário na Deriv.
4. Reconciliar os candles recuperados com o banco.
5. Retomar a distribuição dos dados atualizados.

A recuperação não deverá gerar candles artificiais para períodos sem dados.

### 6.4 Recuperação de operações

Após reinicialização ou falha:

1. Carregar operações que não estejam em estado terminal.
2. Identificar operações com estado desconhecido.
3. Consultar o estado correspondente na Deriv.
4. Atualizar o estado local.
5. Retomar o monitoramento quando possível.

## 7. Escalabilidade e capacidade

A arquitetura deverá permitir crescimento gradual em:

- Quantidade de usuários.
- Quantidade de contas Deriv conectadas.
- Quantidade de robôs ativos.
- Quantidade de ativos monitorados.
- Frequência de eventos.
- Volume histórico de candles.
- Quantidade de operações simultâneas.

A escalabilidade deverá priorizar:

- Coleta compartilhada de Market Data.
- Reutilização de cálculos de indicadores equivalentes.
- Isolamento dos contextos de cada robô.
- Processamento assíncrono.
- Filas com limites e controle de pressão.
- Separação de workers quando a carga justificar.
- Consultas eficientes ao PostgreSQL.

Não serão adicionadas tecnologias de infraestrutura apenas por antecipação. Redis, RabbitMQ, Kafka ou outros componentes deverão ser introduzidos quando houver necessidade técnica demonstrada.

## 8. Sincronização temporal

A plataforma deverá utilizar UTC como referência interna de tempo.

Requisitos:

- Armazenar timestamps com fuso horário.
- Utilizar relógios sincronizados no servidor.
- Não depender do horário local do computador do usuário.
- Diferenciar horário de ocorrência, recebimento e persistência de eventos.
- Preservar a ordem temporal necessária à reconstrução de operações.

Os horários apresentados na interface poderão ser convertidos para o fuso do usuário, sem alterar os registros internos.

## 9. Observabilidade

A plataforma deverá permitir identificar rapidamente problemas operacionais.

A observabilidade deverá combinar:

- Logs estruturados.
- Métricas.
- Rastreamento de requisições e operações.
- Indicadores de saúde dos serviços.
- Alertas operacionais.

Cada operação deverá ser rastreável por identificadores de correlação, conforme definido no Capítulo 13.

Indicadores importantes:

- Conexões Deriv ativas.
- Tempo desde o último dado recebido por ativo.
- Candles pendentes de persistência.
- Tamanho e idade das filas.
- Latência de cada etapa.
- Robôs ativos, pausados e com erro.
- Operações abertas e desconhecidas.
- Erros de banco de dados.
- Taxa de reconexão.
- Uso de CPU, memória e conexões.

Os limites de alerta deverão ser definidos a partir de medições e testes, evitando alarmes excessivos ou ausência de alertas relevantes.

## 10. Segurança e isolamento

Segurança e isolamento são requisitos permanentes, não funcionalidades opcionais.

A plataforma deverá:

- Isolar os dados de cada cliente.
- Impedir acesso a contas Deriv de outros usuários.
- Proteger tokens e credenciais.
- Registrar eventos relevantes de autorização.
- Aplicar permissões no backend.
- Não expor informações financeiras ou dados sensíveis em logs.
- Separar ambientes demo e real.
- Bloquear operações quando a autorização necessária não estiver válida.

Os detalhes estão definidos no Capítulo 16.

## 11. Manutenibilidade e evolução

A arquitetura deverá permitir evolução sem comprometer funcionalidades já testadas.

Requisitos:

- Módulos com responsabilidades claras.
- Interfaces internas documentadas.
- Testes automatizados.
- Migrações de banco controladas.
- Compatibilidade entre versões quando necessária.
- Logs e erros que permitam diagnóstico.
- Documentação atualizada junto às mudanças.
- Alterações incrementais e reversíveis sempre que possível.

A implementação deverá preservar o comportamento já validado, salvo quando uma mudança for explicitamente aprovada e acompanhada de testes de regressão.

## 12. Compatibilidade e interoperabilidade

A integração deverá acompanhar as interfaces oficiais da Deriv.

Requisitos:

- Utilizar documentação e schemas oficiais como referência.
- Validar mensagens recebidas e enviadas.
- Tratar mudanças de protocolo de maneira controlada.
- Manter separação entre a lógica interna e os detalhes do protocolo externo.
- Evitar dependência de bibliotecas descontinuadas ou sem manutenção adequada.

Mudanças na API da Deriv deverão ser avaliadas antes de serem incorporadas.

## 13. Testabilidade

Os requisitos não funcionais deverão ser verificáveis por testes.

Serão necessários:

- Testes de carga.
- Testes de concorrência.
- Testes de reconexão.
- Testes de recuperação após reinicialização.
- Testes de persistência sob carga.
- Testes de indisponibilidade do banco.
- Testes de timeout da Deriv.
- Testes de duplicidade e idempotência.
- Testes de isolamento entre usuários.
- Testes de restauração de backup.

Os testes de desempenho deverão utilizar cenários representativos do número esperado de usuários, robôs, ativos e operações.

## 14. Operação e resposta a incidentes

A plataforma deverá possuir procedimentos operacionais documentados.

Cada incidente relevante deverá permitir identificar:

- O que aconteceu.
- Quando começou.
- Quais serviços foram afetados.
- Quais usuários, contas ou robôs foram impactados.
- Se houve impacto financeiro.
- Como o serviço foi recuperado.
- Se existem operações pendentes de reconciliação.
- Quais medidas evitam recorrência.

Incidentes financeiros terão prioridade elevada e deverão ser tratados com reconciliação antes de qualquer tentativa de repetir comandos.

## 15. Critérios de aceitação

Os requisitos deste capítulo serão considerados atendidos quando:

1. Existirem indicadores de disponibilidade e desempenho dos serviços.
2. A latência interna e externa puder ser analisada separadamente.
3. O sistema suportar reconexão e recuperação de Market Data.
4. Falhas críticas bloquearem novas operações de forma segura.
5. Operações com resultado desconhecido puderem ser reconciliadas.
6. Não houver repetição financeira cega após timeout.
7. O banco possuir backups e testes documentados de restauração.
8. Os serviços puderem ser monitorados por métricas e logs.
9. Os testes de carga e concorrência tiverem resultados documentados.
10. O isolamento entre usuários e contas estiver validado.
11. Os objetivos de RPO, RTO e SLO estiverem definidos antes da operação comercial.
12. Existirem procedimentos documentados para incidentes e recuperação.

## 16. Situação atual

| Recurso | Situação |
|---|---|
| API FastAPI e endpoint de saúde | Implementado parcialmente |
| PostgreSQL e persistência de candles | Implementado parcialmente |
| Reconexão da coleta Deriv | Implementado no serviço existente; validar por testes |
| Métricas operacionais centralizadas | Planejado |
| Monitoramento e alertas | Planejado |
| Testes de carga e capacidade | Planejado |
| RPO e RTO definidos | Pendente |
| SLO de disponibilidade definido | Pendente |
| Backup e restauração testados | A verificar |
| Recuperação completa de operações | Planejado |
| Procedimentos de incidentes | Planejado |
| Validação de escalabilidade multiusuário | Planejado |

**Regra final:** nenhum requisito não funcional será considerado concluído apenas porque existe código relacionado. Sua conclusão exige teste, evidência e documentação do resultado.

# Capítulo 22 — Requisitos de Produto, Limites e Roadmap de Implementação

## 1. Objetivo

Este capítulo consolida os requisitos do produto Deriv e estabelece uma sequência de implementação para transformar a arquitetura documentada nos capítulos anteriores em uma plataforma operacional.

O objetivo é evitar desenvolvimento desordenado, funcionalidades duplicadas e alterações prematuras na estrutura existente.

O roadmap deverá respeitar três princípios:

1. Preservar o que já foi implementado e testado.
2. Priorizar funcionalidades necessárias para uma operação segura.
3. Adiar funcionalidades que não sejam essenciais para a primeira versão comercial.

Este documento representa o planejamento de implementação. Não significa que os módulos descritos já estejam desenvolvidos.

## 2. Definição do produto

A plataforma será um backend multiusuário para gerenciamento e execução de robôs de negociação conectados à Deriv.

Cada cliente deverá poder:

- Criar uma conta na plataforma.
- Vincular sua própria conta Deriv.
- Utilizar contas demo e reais, respeitando as permissões aplicáveis.
- Ativar um período inicial de avaliação de sete dias.
- Configurar e operar robôs.
- Acompanhar operações e resultados.
- Interromper ou desvincular sua autorização.
- Continuar acessando diretamente sua conta Deriv, independentemente da utilização da plataforma.

O administrador deverá poder gerenciar usuários, autorizações, robôs, planos e informações operacionais.

A plataforma não deverá custodiar o dinheiro dos clientes nem solicitar suas senhas da Deriv.

## 3. Escopo da primeira versão comercial

A primeira versão deverá concentrar-se no conjunto mínimo necessário para oferecer uma operação real, segura e administrável.

### 3.1 Funcionalidades obrigatórias

| Área | Requisito |
|---|---|
| Usuários | Cadastro, autenticação e gerenciamento de sessões |
| Autorização Deriv | Vinculação, validação, revogação e isolamento por cliente |
| Contas | Identificação de contas demo e reais |
| Market Data | Coleta, recuperação e persistência de candles |
| Indicadores | Cálculo a partir dos candles armazenados |
| Estratégias | Avaliação de condições e geração de sinais |
| Robôs | Configuração, inicialização, pausa e parada |
| Gestão de risco | Limites e validações antes de cada operação |
| Execução | Solicitação, acompanhamento e reconciliação de contratos |
| Assinaturas | Avaliação de sete dias e controle de acesso |
| Segurança | Proteção de tokens e isolamento multiusuário |
| Auditoria | Registro de eventos e operações |
| Monitoramento | Saúde dos serviços e falhas operacionais |
| Administração | Consulta e gerenciamento operacional dos clientes |

### 3.2 Funcionalidades desejáveis, mas não bloqueantes

- Painéis analíticos avançados.
- Relatórios financeiros detalhados.
- Exportação de histórico.
- Notificações por e-mail ou outros canais.
- Configurações avançadas de estratégias.
- Backtesting integrado.
- Estatísticas avançadas de desempenho dos robôs.
- Automação de suporte ao cliente.

Essas funcionalidades poderão ser incorporadas após a estabilização do núcleo operacional.

## 4. Limites do produto

É importante definir o que a plataforma não deverá fazer.

### 4.1 Limites financeiros

- Não custodiar fundos dos clientes.
- Não solicitar senhas da Deriv.
- Não prometer rentabilidade.
- Não garantir ausência de perdas.
- Não executar operações sem autorização válida.
- Não ultrapassar os limites de risco configurados.
- Não repetir comandos financeiros sem verificar o resultado anterior.

### 4.2 Limites de integração

- A plataforma dependerá da disponibilidade e das permissões oferecidas pela Deriv.
- Nem todos os contratos ou produtos necessariamente serão elegíveis para Markup.
- A utilização de APIs de parceiros e de Markup dependerá dos requisitos e aprovações aplicáveis.
- Mudanças nos protocolos oficiais poderão exigir atualizações.
- Não será utilizado um SDK arquivado como dependência central da integração.

### 4.3 Limites operacionais

- Uma falha de Market Data deverá impedir decisões que dependam de dados confiáveis.
- A ausência do módulo de risco deverá bloquear novas operações.
- A revogação de autorização deverá impedir novas operações na conta vinculada.
- Robôs interrompidos não poderão abandonar contratos já abertos sem acompanhamento.
- Uma assinatura expirada deverá bloquear novas operações, sem apagar histórico ou desvincular automaticamente a conta Deriv.

## 5. Prioridades de implementação

As prioridades serão classificadas em quatro níveis:

- **P0 — Crítico:** necessário para segurança, integridade ou funcionamento básico.
- **P1 — Essencial:** necessário para a primeira versão comercial.
- **P2 — Importante:** melhora a operação, administração ou experiência.
- **P3 — Futuro:** evolução que pode ser adiada.

| Módulo | Prioridade |
|---|---|
| Auditoria da estrutura atual | P0 |
| Estabilização do Market Data | P0 |
| Integração Deriv centralizada | P0 |
| Persistência e migrações | P0 |
| Segurança e isolamento multiusuário | P0 |
| Autenticação e usuários | P1 |
| Autorização de contas Deriv | P1 |
| Indicadores | P1 |
| Estratégias | P1 |
| Gestão dos robôs | P1 |
| Gestão de risco | P0 |
| Execução e reconciliação | P0 |
| Planos e período de avaliação | P1 |
| Auditoria e monitoramento | P1 |
| Administração | P1 |
| Integração comercial de Markup e parceiros | P1, condicionada às aprovações |
| Backtesting | P2 |
| Relatórios avançados | P2 |
| Notificações | P2 |
| Escalabilidade horizontal avançada | P2 |
| Aplicativo ou interface mobile | P3 |

A prioridade P0 não significa necessariamente que o módulo será implementado primeiro de forma isolada. Dependências técnicas poderão determinar a ordem real.

## 6. Roadmap de implementação

A sequência abaixo é uma proposta de execução. Cada fase deverá ser encerrada com critérios de aceitação e testes antes de avançar.

### Fase 0 — Auditoria e preservação da base existente

**Objetivo:** estabelecer exatamente o estado atual do projeto.

Atividades:

1. Inventariar os arquivos e módulos existentes.
2. Verificar a configuração do Docker Compose.
3. Verificar a conexão com PostgreSQL.
4. Verificar o estado real das migrações Alembic.
5. Revisar o serviço atual de Market Data.
6. Identificar os testes existentes.
7. Executar a suíte completa de testes.
8. Registrar os resultados como referência.
9. Identificar problemas e divergências em relação à documentação.

Critério de conclusão:

- Estrutura atual documentada.
- Testes executados e resultados registrados.
- Problemas conhecidos identificados.
- Nenhuma alteração desnecessária nos módulos existentes.

### Fase 1 — Fundação da integração Deriv

**Objetivo:** criar uma camada de integração confiável e reutilizável.

Atividades:

1. Auditar a conexão WebSocket existente.
2. Comparar mensagens utilizadas com a documentação e os schemas oficiais atuais.
3. Definir o cliente central de comunicação.
4. Implementar correlação de requisições e respostas.
5. Padronizar tratamento de erros.
6. Definir gerenciamento de conexões e reconexões.
7. Separar comunicação pública e autenticada.
8. Implementar gerenciamento de assinaturas.
9. Definir tratamento seguro de credenciais e autorizações.

O serviço atual de Market Data deverá ser preservado durante a auditoria. A refatoração somente deverá ocorrer quando houver justificativa e testes de equivalência.

Critério de conclusão:

- Integração validada contra a documentação oficial.
- Requisições correlacionadas corretamente.
- Reconexões testadas.
- Erros externos tratados.
- Testes automatizados aprovados.

### Fase 2 — Usuários, contas e autorização Deriv

**Objetivo:** preparar a plataforma para múltiplos clientes.

Atividades:

1. Criar cadastro de usuários.
2. Implementar autenticação da plataforma.
3. Implementar controle de permissões.
4. Definir modelo de contas Deriv.
5. Implementar o fluxo oficial de autorização.
6. Proteger tokens e dados sensíveis.
7. Implementar revogação e desvinculação.
8. Validar isolamento entre clientes.
9. Registrar eventos de autorização.

Critério de conclusão:

- Usuários conseguem autenticar-se.
- Cada conta Deriv está associada ao proprietário correto.
- Nenhum cliente acessa dados de outro.
- Tokens não aparecem em logs.
- Revogação bloqueia novas operações.

### Fase 3 — Market Data confiável

**Objetivo:** garantir uma fonte consistente de dados para todos os robôs.

Atividades:

1. Validar coleta em tempo real.
2. Validar formação de candles M1.
3. Validar persistência de candles fechados.
4. Implementar recuperação histórica.
5. Implementar recuperação incremental.
6. Implementar catálogo de ativos.
7. Implementar controle de qualidade e atualização dos dados.
8. Implementar distribuição interna dos candles.
9. Testar interrupções e recuperação.

Critério de conclusão:

- Candles consistentes.
- Persistência sem duplicidade.
- Recuperação histórica validada.
- Falhas de conexão tratadas.
- Dados compartilhados entre robôs sem duplicar desnecessariamente a coleta.

### Fase 4 — Indicadores e estratégias

**Objetivo:** transformar os dados de mercado em sinais de negociação.

Atividades:

1. Implementar estrutura de indicadores.
2. Implementar cálculos iniciais prioritários.
3. Garantir cálculo sobre candles persistidos.
4. Definir tratamento de candle provisório.
5. Implementar configuração de parâmetros.
6. Criar estrutura de estratégias.
7. Implementar avaliação de condições.
8. Criar geração e deduplicação de sinais.
9. Implementar versionamento.

Critério de conclusão:

- Cálculos matemáticos validados.
- Resultados incrementais equivalentes aos cálculos completos.
- Sinais reproduzíveis.
- Duplicidade controlada.
- Estratégias não executam operações diretamente.

### Fase 5 — Robôs e gestão de risco

**Objetivo:** permitir a execução independente e controlada de múltiplos robôs.

Atividades:

1. Criar entidades e serviços de robôs.
2. Implementar ciclo de vida.
3. Implementar configurações e versões.
4. Implementar inicialização, pausa e parada.
5. Implementar isolamento por cliente e conta.
6. Criar perfis e limites de risco.
7. Implementar validação obrigatória antes de cada operação.
8. Implementar reservas para operações concorrentes.
9. Implementar bloqueios automáticos.
10. Testar concorrência e idempotência.

Critério de conclusão:

- Múltiplos robôs podem operar independentemente.
- Cada robô respeita sua configuração.
- Limites de risco são aplicados.
- Operações simultâneas não provocam duplicidade ou ultrapassagem de limites.

### Fase 6 — Execução de operações

**Objetivo:** implementar o ciclo financeiro completo.

Atividades:

1. Implementar solicitação de propostas.
2. Validar propostas recebidas.
3. Implementar compra de contratos.
4. Registrar identificadores e respostas.
5. Monitorar contratos abertos.
6. Implementar encerramento antecipado quando permitido.
7. Implementar acompanhamento de expiração.
8. Implementar reconciliação.
9. Implementar tratamento de estado desconhecido.
10. Testar falhas durante cada etapa.

Critério de conclusão:

- Operações possuem histórico completo.
- Nenhuma repetição financeira cega.
- Resultados são reconciliados com a Deriv.
- Operações abertas continuam sendo monitoradas após parada de robôs.

### Fase 7 — Assinaturas e controle de acesso

**Objetivo:** habilitar o modelo comercial da plataforma.

Atividades:

1. Implementar período de avaliação de sete dias.
2. Definir início explícito do período de avaliação.
3. Implementar estados de assinatura.
4. Implementar planos e limites.
5. Implementar bloqueio de novas operações por expiração.
6. Definir integração com provedor de pagamentos.
7. Implementar confirmação segura de pagamentos.
8. Criar histórico de alterações de assinatura.

Critério de conclusão:

- Avaliação de sete dias controlada pelo backend.
- Expiração bloqueia novas operações.
- Contratos abertos continuam sendo acompanhados.
- Alterações de assinatura são auditáveis.

### Fase 8 — Administração, monitoramento e auditoria

**Objetivo:** permitir operação e suporte da plataforma.

Atividades:

1. Implementar consultas administrativas.
2. Implementar gerenciamento de clientes.
3. Implementar consulta de contas vinculadas.
4. Implementar gerenciamento de robôs.
5. Implementar auditoria centralizada.
6. Implementar métricas e alertas.
7. Criar procedimentos de incidentes.
8. Implementar ferramentas de diagnóstico.

Critério de conclusão:

- Administrador consegue acompanhar o estado operacional.
- Eventos críticos são rastreáveis.
- Falhas importantes geram alertas.
- Ações administrativas possuem controle de acesso e auditoria.

### Fase 9 — Markup, parceiros e monetização

**Objetivo:** integrar os mecanismos comerciais disponibilizados pela Deriv.

Atividades:

1. Confirmar requisitos atuais do programa de parceiros.
2. Confirmar elegibilidade e aprovação para Markup.
3. Validar mecanismos oficiais de atribuição de clientes.
4. Validar permissões OAuth necessárias.
5. Implementar consultas de estatísticas disponíveis.
6. Separar receitas estimadas, confirmadas e recebidas.
7. Implementar conciliação de dados comerciais.
8. Criar relatórios administrativos.

Critério de conclusão:

- Mecanismos comerciais aprovados e habilitados.
- Atribuição de clientes validada.
- Dados de receita rastreáveis.
- Nenhuma comissão presumida sem confirmação da fonte oficial.

### Fase 10 — Homologação e lançamento

**Objetivo:** validar a plataforma em condições próximas da produção.

Atividades:

1. Executar testes de integração completos.
2. Executar testes de carga.
3. Executar testes de segurança.
4. Testar recuperação de falhas.
5. Testar operações em conta demo.
6. Validar fluxos de autorização e revogação.
7. Validar assinatura e expiração.
8. Validar backups e restauração.
9. Configurar monitoramento de produção.
10. Documentar procedimentos de operação.
11. Definir critérios de liberação para contas reais.
12. Realizar lançamento controlado.

Critério de conclusão:

- Testes críticos aprovados.
- Incidentes conhecidos documentados.
- Procedimentos de recuperação testados.
- Operações demo validadas.
- Aprovações externas necessárias obtidas.
- Liberação para operações reais formalmente autorizada.

## 7. Dependências entre módulos

A implementação deverá respeitar as dependências abaixo:

| Módulo | Depende principalmente de |
|---|---|
| Usuários | Banco de dados e segurança |
| Contas Deriv | Usuários e integração Deriv |
| Market Data | Integração Deriv e banco de dados |
| Indicadores | Market Data |
| Estratégias | Indicadores e Market Data |
| Bots | Usuários, contas, estratégias e Market Data |
| Gestão de risco | Bots, contas e dados financeiros |
| Execution | Integração Deriv, risco e contas |
| Assinaturas | Usuários e controle de acesso |
| Auditoria | Infraestrutura e módulos operacionais |
| Administração | Usuários, permissões e módulos de negócio |
| Monetização | Integração Deriv e aprovação comercial |

As dependências são lógicas. Alguns trabalhos poderão ocorrer em paralelo, desde que suas interfaces estejam definidas.

## 8. Estratégia de implementação incremental

Cada módulo deverá seguir um ciclo controlado:

1. Revisar o capítulo de documentação correspondente.
2. Auditar o código existente e suas dependências.
3. Identificar o menor escopo funcional necessário.
4. Definir interfaces e estruturas de dados.
5. Implementar em alterações pequenas.
6. Criar testes unitários e de integração.
7. Executar a suíte completa de regressão.
8. Revisar segurança e impacto sobre outros módulos.
9. Atualizar a documentação.
10. Registrar o estado real de implementação.

Nenhum módulo deverá ser considerado concluído apenas porque seus arquivos foram criados.

## 9. Controle de mudanças e preservação da base

A base atual do projeto deverá ser preservada.

Regras:

- Não apagar funcionalidades existentes sem justificativa.
- Não substituir código funcional apenas por preferência estrutural.
- Não alterar migrações já aplicadas.
- Criar novas migrações para mudanças de banco.
- Executar testes antes e depois de alterações relevantes.
- Utilizar commits pequenos e descritivos.
- Manter possibilidade de identificar e reverter mudanças.
- Não realizar refatorações amplas sem necessidade comprovada.

A documentação orienta o desenvolvimento, mas não autoriza automaticamente mudanças no código.

## 10. Critérios gerais de conclusão do produto

A primeira versão comercial somente poderá ser considerada pronta quando:

1. Suportar múltiplos usuários com isolamento validado.
2. Permitir vinculação segura de contas Deriv.
3. Operar com contas demo e reais conforme permissões e aprovações aplicáveis.
4. Possuir coleta e persistência confiáveis de Market Data.
5. Calcular indicadores e avaliar estratégias.
6. Gerenciar múltiplos robôs.
7. Aplicar gestão de risco antes de cada operação.
8. Executar e reconciliar contratos.
9. Controlar avaliação e assinaturas.
10. Permitir revogação de autorização.
11. Monitorar operações abertas.
12. Possuir auditoria e monitoramento.
13. Possuir backup e recuperação testados.
14. Passar pelos testes de segurança, integração, regressão e carga definidos.
15. Ter as aprovações externas necessárias para os recursos comerciais e operacionais.

## 11. Estado atual e próximos passos

O projeto já possui uma base técnica criada, incluindo infraestrutura Docker, API FastAPI, PostgreSQL, estrutura de migrações Alembic e implementação parcial de Market Data.

Também existe um histórico de testes aprovado anteriormente, com 27 testes passando. Esse resultado é uma referência histórica e deverá ser confirmado novamente antes de novas alterações.

A próxima etapa não deve ser iniciar imediatamente todos os módulos do roadmap.

A sequência recomendada é:

1. Consolidar os capítulos de documentação.
2. Auditar o estado real dos arquivos e testes.
3. Criar uma matriz de rastreabilidade entre requisitos, código e testes.
4. Identificar lacunas e divergências.
5. Iniciar a implementação incremental pela fundação da integração Deriv e pela estabilização do Market Data.

**Regra final:** o roadmap é uma sequência de trabalho sujeita a validação técnica. Nenhuma fase será considerada concluída sem implementação verificável, testes aprovados e documentação atualizada.

# Capítulo 23 — Matriz de Requisitos, Rastreabilidade e Critérios de Aceitação

## 1. Objetivo

Este capítulo estabelece como os requisitos da plataforma Deriv serão relacionados à implementação, aos testes e às evidências de funcionamento.

O objetivo é garantir que nenhuma funcionalidade seja considerada concluída apenas porque foi documentada ou porque existe código relacionado.

Cada requisito deverá possuir uma identificação única, prioridade, módulo responsável, dependências, critérios de aceitação e evidências de validação.

A matriz será utilizada como referência durante todo o desenvolvimento.

## 2. Princípios de rastreabilidade

A rastreabilidade deverá permitir responder às seguintes perguntas:

- O que a plataforma precisa fazer?
- Qual módulo é responsável?
- Onde está implementado?
- Quais outros módulos são necessários?
- Como o comportamento será testado?
- Qual evidência comprova que funciona?
- O requisito está concluído, parcial ou pendente?

Cada requisito deverá ser rastreável nos dois sentidos:

**Requisito → Implementação → Teste → Evidência**

E também:

**Código → Requisito → Teste**

Isso evita funcionalidades sem justificativa documentada e requisitos esquecidos durante o desenvolvimento.

## 3. Identificação dos requisitos

Cada requisito deverá possuir um identificador estável.

Padrão sugerido:

| Prefixo | Domínio |
|---|---|
| REQ-CORE | Requisitos gerais |
| REQ-DERIV | Integração Deriv |
| REQ-USER | Usuários |
| REQ-ACCOUNT | Contas Deriv |
| REQ-MD | Market Data |
| REQ-IND | Indicadores |
| REQ-STR | Estratégias |
| REQ-BOT | Robôs |
| REQ-RISK | Gestão de risco |
| REQ-EXEC | Execução |
| REQ-PLAN | Planos e assinaturas |
| REQ-PARTNER | Parceiros e Markup |
| REQ-SEC | Segurança |
| REQ-AUDIT | Auditoria |
| REQ-OPS | Infraestrutura e operação |
| REQ-API | API interna |

Exemplo:

`REQ-MD-001`

Representa o primeiro requisito identificado no domínio de Market Data.

Os identificadores não deverão mudar quando arquivos ou módulos forem reorganizados.

## 4. Classificação dos requisitos

Cada requisito deverá ser classificado por prioridade e natureza.

### 4.1 Prioridade

- **P0 — Crítico:** segurança, integridade financeira ou funcionamento essencial.
- **P1 — Essencial:** necessário para a primeira versão comercial.
- **P2 — Importante:** necessário para evolução operacional.
- **P3 — Futuro:** pode ser adiado.

### 4.2 Natureza

- **Funcional:** descreve um comportamento que o sistema deve executar.
- **Não funcional:** descreve desempenho, segurança, disponibilidade ou qualidade.
- **Regulatório/comercial:** depende de regras, contratos ou aprovações externas.
- **Operacional:** descreve procedimentos necessários à operação e manutenção.

## 5. Estados de implementação

Todos os requisitos deverão utilizar estados padronizados.

| Estado | Significado |
|---|---|
| Não iniciado | Não existe implementação identificada |
| Planejado | Existe definição e planejamento |
| Em desenvolvimento | Implementação em andamento |
| Implementado | Existe código, mas ainda não há validação completa |
| Validado | Implementação e testes foram aprovados |
| Parcial | Apenas parte do requisito foi atendida |
| Bloqueado | Depende de decisão ou recurso externo |
| Descontinuado | Requisito retirado mediante decisão documentada |

**Regra:** somente o estado Validado representa requisito concluído.

A existência de arquivos, classes, endpoints ou tabelas não é suficiente para comprovar conclusão.

## 6. Estrutura da matriz de rastreabilidade

A matriz principal deverá possuir as seguintes colunas:

| Campo | Descrição |
|---|---|
| ID | Identificador único |
| Requisito | Descrição objetiva |
| Prioridade | P0, P1, P2 ou P3 |
| Natureza | Funcional, não funcional, comercial ou operacional |
| Capítulo | Documento de origem |
| Módulo | Responsável pela implementação |
| Dependências | Outros requisitos necessários |
| Implementação | Arquivo, classe, função ou endpoint |
| Teste | Teste que comprova o comportamento |
| Estado | Situação atual |
| Evidência | Resultado verificável |
| Observações | Restrições ou pendências |

Os caminhos dos arquivos deverão ser atualizados conforme a estrutura real do projeto. Não devem ser inventados antes da auditoria.

## 7. Matriz inicial de requisitos

A tabela abaixo é a matriz inicial de referência. Os estados representam o conhecimento atual do projeto e deverão ser confirmados na auditoria técnica.

| ID | Requisito | Prioridade | Módulo | Estado inicial |
|---|---|---|---|---|
| REQ-CORE-001 | Suportar múltiplos usuários | P0 | Core | Planejado |
| REQ-CORE-002 | Isolar dados e operações por cliente | P0 | Segurança | Planejado |
| REQ-DERIV-001 | Manter integração própria com a Deriv | P0 | Integração Deriv | Parcial |
| REQ-DERIV-002 | Correlacionar requisições e respostas | P0 | Integração Deriv | A verificar |
| REQ-DERIV-003 | Reconectar após falhas de comunicação | P0 | Integração Deriv | Parcial |
| REQ-USER-001 | Registrar usuários da plataforma | P1 | Usuários | Planejado |
| REQ-USER-002 | Autenticar usuários | P0 | Segurança | Planejado |
| REQ-ACCOUNT-001 | Vincular conta Deriv ao proprietário | P0 | Contas | Planejado |
| REQ-ACCOUNT-002 | Identificar contas demo e reais | P1 | Contas | Planejado |
| REQ-ACCOUNT-003 | Permitir revogação de autorização | P0 | Contas | Planejado |
| REQ-MD-001 | Receber dados de mercado em tempo real | P0 | Market Data | Parcial |
| REQ-MD-002 | Formar candles M1 | P0 | Market Data | Parcial |
| REQ-MD-003 | Persistir candles fechados | P0 | Banco de dados | Parcial |
| REQ-MD-004 | Recuperar histórico de candles | P0 | Market Data | Parcial |
| REQ-MD-005 | Evitar candles duplicados | P0 | Market Data | Parcial |
| REQ-MD-006 | Compartilhar coleta entre robôs | P1 | Market Data | Planejado |
| REQ-IND-001 | Calcular indicadores sobre candles armazenados | P1 | Indicadores | Planejado |
| REQ-IND-002 | Suportar configuração de parâmetros | P1 | Indicadores | Planejado |
| REQ-STR-001 | Avaliar regras de estratégias | P1 | Estratégias | Planejado |
| REQ-STR-002 | Gerar sinais identificáveis e deduplicados | P1 | Estratégias | Planejado |
| REQ-BOT-001 | Criar e configurar robôs | P1 | Bots | Planejado |
| REQ-BOT-002 | Controlar ciclo de vida dos robôs | P1 | Bots | Planejado |
| REQ-RISK-001 | Validar risco antes de cada operação | P0 | Risco | Planejado |
| REQ-RISK-002 | Controlar operações concorrentes | P0 | Risco | Planejado |
| REQ-EXEC-001 | Solicitar propostas à Deriv | P0 | Execução | Planejado |
| REQ-EXEC-002 | Comprar contratos autorizados | P0 | Execução | Planejado |
| REQ-EXEC-003 | Monitorar contratos abertos | P0 | Execução | Planejado |
| REQ-EXEC-004 | Reconciliar operações desconhecidas | P0 | Execução | Planejado |
| REQ-PLAN-001 | Controlar avaliação de sete dias | P1 | Assinaturas | Planejado |
| REQ-PLAN-002 | Bloquear novas operações após expiração | P1 | Assinaturas | Planejado |
| REQ-PARTNER-001 | Integrar programa de parceiros | P1 | Monetização | Bloqueado por validação externa |
| REQ-PARTNER-002 | Integrar Markup elegível | P1 | Monetização | Bloqueado por validação externa |
| REQ-SEC-001 | Proteger tokens Deriv | P0 | Segurança | A verificar |
| REQ-SEC-002 | Impedir acesso cruzado entre clientes | P0 | Segurança | Planejado |
| REQ-AUDIT-001 | Registrar eventos financeiros e administrativos | P0 | Auditoria | Parcial |
| REQ-OPS-001 | Monitorar saúde dos serviços | P1 | Operação | Parcial |
| REQ-OPS-002 | Realizar backup e testar restauração | P0 | Operação | A verificar |
| REQ-API-001 | Padronizar interfaces internas | P1 | API interna | Parcial |

Essa matriz não é um inventário definitivo. Novos requisitos poderão ser adicionados conforme a auditoria e a implementação avançarem.

## 8. Critérios de aceitação

Cada requisito deverá possuir critérios objetivos.

Exemplo:

### REQ-MD-002 — Formação de candles M1

**Descrição:** o sistema deverá formar candles de um minuto a partir dos ticks recebidos da Deriv.

**Critérios de aceitação:**

1. O candle deverá representar um intervalo de um minuto.
2. O primeiro preço observado será o Open.
3. O maior preço será o High.
4. O menor preço será o Low.
5. O último preço observado será o Close.
6. O horário deverá utilizar UTC.
7. Apenas candles fechados serão persistidos pelo fluxo de coleta em tempo real.
8. O primeiro intervalo incompleto após início ou reinicialização não deverá ser tratado como candle completo.
9. Não deverão ser criados candles artificiais para intervalos sem dados.
10. Os testes deverão comprovar os cálculos e as transições de intervalo.

**Evidência esperada:**

- Testes automatizados aprovados.
- Registros persistidos no PostgreSQL.
- Verificação de consistência dos valores OHLC.
- Teste de reinicialização e recuperação.

### REQ-EXEC-004 — Reconciliação de operações desconhecidas

**Descrição:** o sistema deverá identificar o resultado de uma operação cujo comando tenha sido enviado, mas cuja resposta não tenha sido recebida de forma conclusiva.

**Critérios de aceitação:**

1. A operação deverá ser marcada como desconhecida.
2. O sistema não poderá repetir imediatamente o comando financeiro.
3. Deverá consultar os mecanismos disponíveis na Deriv para identificar o resultado.
4. O resultado confirmado deverá atualizar o registro local.
5. A operação deverá possuir histórico de reconciliação.
6. O robô não poderá considerar a operação inexistente apenas porque ocorreu um timeout.

**Evidência esperada:**

- Teste de timeout simulado.
- Teste de reconciliação bem-sucedida.
- Teste de prevenção de duplicidade.
- Histórico de eventos persistido.

## 9. Rastreabilidade entre documentação e código

A documentação será a referência dos requisitos, mas a implementação deverá apontar para arquivos concretos.

Exemplo de registro:

| Campo | Exemplo |
|---|---|
| Requisito | REQ-MD-003 |
| Capítulo | 6 — Market Data |
| Módulo | Market Data |
| Arquivo | `app/services/deriv_market_data.py` |
| Responsabilidade | Persistência dos candles |
| Testes | Testes de persistência e duplicidade |
| Estado | A confirmar |
| Evidência | Resultado da suíte de testes e consulta ao banco |

O caminho acima é uma referência conhecida da estrutura atual, não uma confirmação de que todo o requisito esteja implementado nesse arquivo.

A implementação poderá envolver mais de um arquivo e mais de um módulo.

## 10. Rastreabilidade dos testes

Os testes também deverão possuir identificadores.

Padrão sugerido:

- `TEST-MD-001`
- `TEST-EXEC-001`
- `TEST-SEC-001`
- `TEST-BOT-001`

Cada teste deverá indicar:

- Requisito validado.
- Cenário de execução.
- Dados de entrada.
- Resultado esperado.
- Resultado obtido.
- Estado de aprovação.
- Data da última execução.

Um requisito poderá depender de vários testes. Um teste também poderá validar mais de um requisito, desde que essa relação esteja explícita.

## 11. Gestão de pendências e bloqueios

Nem todo requisito poderá ser implementado imediatamente.

As pendências deverão ser classificadas:

**Pendência técnica**
- Falta de código.
- Falta de teste.
- Problema de arquitetura.
- Incompatibilidade com a API.

**Pendência de decisão**
- Regra de negócio ainda não definida.
- Parâmetros de risco não aprovados.
- Comportamento operacional indefinido.

**Pendência externa**
- Aprovação da Deriv.
- Permissão OAuth.
- Elegibilidade de Markup.
- Regras comerciais do programa de parceiros.
- Disponibilidade de serviço externo.

Cada pendência deverá possuir responsável, impacto, dependência e condição para resolução.

## 12. Processo de atualização da matriz

A matriz deverá ser atualizada sempre que:

- Um requisito for criado ou alterado.
- Um módulo for implementado.
- Um teste for criado ou modificado.
- Um requisito passar para Validado.
- Uma dependência externa mudar.
- Uma decisão arquitetural alterar o escopo.
- Uma funcionalidade for descontinuada.

A atualização deverá acompanhar o commit correspondente, evitando divergência entre código e documentação.

## 13. Critérios de conclusão deste capítulo

Este capítulo será considerado operacionalmente aplicado quando:

1. Todos os requisitos prioritários possuírem identificadores.
2. Cada requisito possuir módulo responsável.
3. Os critérios de aceitação estiverem definidos.
4. Os testes estiverem relacionados aos requisitos.
5. Os arquivos de implementação estiverem identificados após auditoria.
6. Os estados refletirem evidências reais.
7. As pendências externas estiverem documentadas.
8. A matriz for mantida atualizada durante o desenvolvimento.

## 14. Regra final

A matriz de rastreabilidade será o instrumento de controle técnico do projeto.

A documentação define o que deve existir. O código demonstra o que foi construído. Os testes demonstram se funciona. As evidências permitem confirmar a conclusão.

Nenhuma funcionalidade crítica será considerada pronta para produção sem atender aos quatro elementos.

# Capítulo 24 — Auditoria Técnica da Implementação Atual e Plano de Ajustes

## 24.X — Auditoria do módulo Market Data

### 24.X.1 — Escopo da auditoria

Foi realizada uma revisão da implementação existente do módulo Market Data, incluindo:

- `app/services/deriv_market_data.py`
- `app/services/candle_builder.py`
- Estrutura de persistência PostgreSQL/TimescaleDB.
- Recuperação de candles históricos.
- Processamento de ticks em tempo real.
- Reconexão e recuperação após interrupções.
- Monitoramento de saúde e persistência.
- Testes unitários e de integração existentes.

A auditoria teve caráter de conformidade e validação. Não houve reconstrução do módulo nem alteração de código.

### 24.X.2 — Construção de candles

O `CandleBuilder` implementa a agregação de ticks em candles de um minuto (M1).

Regras identificadas:

- Open: primeiro preço recebido no minuto.
- High: maior preço observado.
- Low: menor preço observado.
- Close: último preço válido recebido.
- Separação independente por ativo.
- Descarte de ticks duplicados ou fora de ordem.
- Descarte de candles incompletos após reinicialização ou reconexão.
- Não criação de candles artificiais em intervalos sem ticks.

O candle é emitido quando chega um tick de um minuto posterior. Portanto, não existe fechamento baseado exclusivamente no relógio do sistema.

**Situação: implementado e coberto por testes.**

### 24.X.3 — Integração com a Deriv

O serviço utiliza WebSocket para receber ticks em tempo real e solicita dados históricos por meio de `ticks_history`, com:

- `style="candles"`
- `granularity=60`

A recuperação histórica utiliza uma conexão WebSocket separada da conexão de mercado em tempo real.

O serviço também:

- Mantém os ativos configurados.
- Registra o estado da conexão.
- Processa mensagens de ticks.
- Detecta eventos de lacuna temporal.
- Reinicia a conexão após falhas.
- Reinicia o processo de recuperação histórica após reconexões.

**Situação: implementado. A compatibilidade operacional completa com a API vigente ainda requer validação externa.**

### 24.X.4 — Recuperação histórica

A recuperação considera o último candle persistido para cada ativo.

Comportamento identificado:

- Sem cursor persistido, inicia a recuperação considerando os últimos 14 dias.
- Com cursor, retrocede um candle para permitir reconciliação.
- Solicita candles históricos M1.
- Ignora candles anteriores ao início solicitado.
- Não persiste o candle do minuto ainda em formação.
- Utiliza paginação para percorrer o histórico.
- Encaminha os registros recuperados para a fila de persistência.
- Executa novas tentativas quando ocorrem falhas.

A implementação possui testes de recuperação e retentativa.

**Situação: implementado, com cobertura parcial.**

Ainda precisam ser validados:

1. Paginação com múltiplas páginas.
2. Recuperação inicial sem registros anteriores.
3. Respostas vazias ou incompletas.
4. Validação de candles históricos inválidos.
5. Comportamento diante de lacunas extensas.
6. Compatibilidade real da paginação com as respostas da Deriv.

### 24.X.5 — Persistência

A persistência é executada por um worker assíncrono que agrupa registros em lotes.

Foram identificadas duas políticas:

**Candles históricos**
- Utilizam `INSERT ... ON CONFLICT DO UPDATE`.
- Permitem reconciliar e atualizar registros existentes.

**Candles em tempo real**
- Utilizam `INSERT ... ON CONFLICT DO NOTHING`.
- Evitam que um candle live sobrescreva um registro já existente.

O worker também possui retentativa após falhas de banco de dados.

A fila é mantida em memória. Portanto, uma interrupção abrupta do processo pode perder itens ainda não persistidos. A recuperação histórica é o mecanismo previsto para reconciliar esses dados posteriormente.

**Situação: implementado e testado parcialmente.**

Pendente: testar diretamente a atualização de um candle histórico já existente e validar a recuperação após perda de itens ainda presentes apenas na fila.

### 24.X.6 — Monitoramento

O serviço disponibiliza informações sobre:

- Estado da conexão.
- Tempo desde o último tick recebido.
- Ativos sem atualização recente.
- Ocupação da fila.
- Quantidade de ticks recebidos.
- Candles históricos recuperados.
- Lotes e registros persistidos.
- Erros de banco de dados.
- Erros de conexão.
- Eventos de lacuna.
- Tempo desde a última persistência bem-sucedida.

Os estados identificados são:

- `healthy`
- `degraded`
- `unhealthy`

A implementação possui testes para desconexão, ativos sem atualização, fila com ocupação elevada e persistência parada.

**Situação: implementado e testado.**

### 24.X.7 — Testes existentes

Foram identificados seis arquivos na suíte:

| Arquivo | Cobertura |
|---|---|
| `test_candle_builder.py` | Formação OHLC, ativos independentes, ticks atrasados, lacunas e reset |
| `test_market_data_recovery.py` | Recuperação, retentativas, persistência, reconexão e ciclo de vida |
| `test_market_data_health.py` | Estados de saúde, fila, persistência e métricas |
| `test_market_data_postgres_integration.py` | Integração real com PostgreSQL e proteção contra duplicidade |
| `test_health.py` | Health check geral da API |
| `__init__.py` | Inicialização do pacote de testes |

A suíte já havia apresentado resultado de 27 testes aprovados na execução geral registrada anteriormente.

A revisão dos arquivos identificou oportunidades de ampliar a cobertura, não uma justificativa para substituir a implementação existente.

### 24.X.8 — Ajustes de cobertura recomendados

Os seguintes testes devem ser acrescentados, preferencialmente sem modificar o comportamento atual do sistema:

| Prioridade | Teste adicional |
|---|---|
| Alta | Paginação histórica com múltiplas páginas |
| Alta | Atualização de candle histórico existente |
| Alta | Recuperação inicial sem cursor |
| Alta | Recuperação de lacunas após interrupção |
| Média | Exclusão de candle ainda em formação |
| Média | Respostas históricas vazias |
| Média | Rejeição de candles históricos inválidos |
| Média | Estado `degraded` com fila a partir de 70% |
| Média | Emissão normal de candles após reconexão |

Também foram observadas duplicações de `@pytest.mark.asyncio` em alguns testes. É uma redundância de organização, não uma falha funcional identificada.

O teste de integração PostgreSQL utiliza um horário fixo. Recomenda-se garantir isolamento desse registro de teste para que uma execução anterior ou um registro preexistente não produza um falso resultado positivo.

### 24.X.9 — Validação operacional pendente

Os testes automatizados não substituem uma validação operacional com a API real.

Antes de considerar o módulo definitivamente validado, será necessário:

1. Observar a recepção de ticks em tempo real.
2. Confirmar a persistência dos candles M1.
3. Interromper e reiniciar o serviço.
4. Confirmar a recuperação dos candles ausentes.
5. Comparar os candles recuperados com o histórico fornecido pela Deriv.
6. Verificar que não existam duplicidades ou candles artificiais.
7. Confirmar que os indicadores possam consumir os dados persistidos.

A validação deve utilizar inicialmente a conta demo já disponível.

### 24.X.10 — Classificação final do módulo

| Componente | Classificação |
|---|---|
| CandleBuilder | Implementado e testado |
| Recepção de ticks | Implementada; validação operacional necessária |
| Agregação M1 | Implementada e testada |
| Persistência de candles | Implementada e testada parcialmente |
| Recuperação histórica | Implementada; cobertura parcial |
| Reconexão automática | Implementada e testada |
| Monitoramento | Implementado e testado |
| Integração PostgreSQL | Testada |
| Recuperação após interrupção real | Pendente de validação operacional |

**Conclusão:** o módulo Market Data possui uma base funcional construída e testada. A estratégia recomendada é preservar a implementação, complementar os testes identificados e realizar validação operacional com a Deriv. Não há justificativa, neste momento, para reescrever o módulo.

---

## 24.X+1 — Diretriz de preservação da implementação

As funcionalidades já construídas e aprovadas nos testes devem ser preservadas.

Toda alteração futura deverá:

- Ter uma justificativa técnica identificada.
- Ser limitada ao componente que necessita de ajuste.
- Preservar os contratos existentes entre módulos.
- Possuir testes correspondentes.
- Ser validada antes de integrar a versão principal.

A auditoria dos demais módulos deverá seguir o mesmo critério: identificar o estado real da implementação, verificar a cobertura existente e separar correções necessárias de funcionalidades ainda planejadas.