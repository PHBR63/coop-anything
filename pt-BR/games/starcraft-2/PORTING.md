# <a id="making-a-starcraft-ii-campaign-co-op-ready"></a>Preparando uma campanha de StarCraft II para modo cooperativo

O que o inicializador SC2Coop faz sozinho numa campanha, o que você (autor do mapa) ainda precisa decidir ou editar e como verificar uma campanha nova. Baseado na adaptação de campanhas WoL@Kit (2026-10). Execute primeiro o verificador:

```
SC2Coop-console.exe campaign-check "<campaign folder>" report.md
```

Ele lista, por mapa, todas as chamadas de script dirigidas ao jogador 1 que o inicializador **ainda não** trata.

## <a id="how-co-op-works-one-paragraph"></a>Como funciona o modo cooperativo (em um parágrafo)

O host é o jogador 1, como de costume. O parceiro entra como jogador adicional (vaga livre, por exemplo 6 a 14), compartilhando controle, visão e gastos do exército do jogador 1 (modo "shared army"). Cada um explora sua própria cópia do centro (mapa de história); selecionar missão a inicia para ambos pela API multiplayer de StarCraft II. O progresso fica nos bancos do host; o inicializador os copia para o parceiro e de volta em torno de cada missão.

## <a id="done-automatically-by-the-launcher-no-map-edits"></a>Feito automaticamente pelo inicializador (sem editar mapas)

| Área | O que faz | Por quê |
|---|---|---|
| Vaga do convidado | Copia registro MapInfo do jogador 1 para vaga livre | Mapa precisa de segundo humano |
| Exército compartilhado | Aliança com controle, visão e gastos compartilhados; reaplicada a cada segundo | Missões alteram alianças durante a execução |
| Entrada do convidado | Ponte de cliques (seleção, ordens, mira, colocação de construções) e teclas de câmera | API descarta cliques no mundo de quem entra |
| Objetivos | `ObjectiveSetState` / `libWCMI_gf_ZS_SetMissionObjectiveState` do Kit: conclusão/falha mostradas como sufixo do nome; estado do motor permanece ativo | Objetivo concluído ou falho faz API encerrar para ambos |
| Câmera de cenas | 13 funções de câmera dirigidas ao jogador 1 também executam para convidado | Ambos veem mesmos enquadramentos e bloqueios de entrada |
| Marcações | Marcações para jogador 1 também vão ao convidado | Antes só host recebia as de objetivos |
| Pular | Cenas puláveis exigem Esc de um jogador, não de todos | Quantidade exigida 0 significa todos |
| Fim da missão | Vitória/derrota pela biblioteca encerra ambos; bancos sincronizados; centros reabertos | |
| Próximo mapa | `GameSetNextMap` limpo | Inicializador decide o carregamento |
| Centro | Lançamentos (`libWoLC_gf_LaunchMission`) registrados para inicializador; janela de depuração mantida fechada | |
| Dificuldade, cores, nomes | Definidos por missão a partir da escolha no centro e configurações | |
| Comandos de teste | `-cooplaunch <mission>` (centro), `-coopwin`, `-coopwinnow`, `-cooplose`, `-coopobj <objective> [fail]` (missões) | Avançar durante testes |

Também automáticos: conferência de configuração (mesmo inicializador, mapas e mods nos dois PCs), recuperação de falhas (salvamento automático dos bancos antes de cada missão) e cortina de carregamento entre partidas.

## <a id="needs-a-decision-or-an-edit-by-you"></a>Exige decisão ou edição sua

### <a id="shared-army-mode-current-nothing-required-but-know-these"></a>Exército compartilhado (atual): nada obrigatório, mas saiba disto

- **Eventos de entrada só do host.** Gatilhos de entrada do jogador 1 (`TriggerAddEventButtonPressed(t, 1, ...)`, teclas, conversa, seleção de unidades) só respondem ao host. Tutoriais como "selecione os marines" esperam por ele. Botões de escolha de missão (diálogo para escolher lado, por exemplo) cabem ao host. Para o parceiro usá-los, acrescente o convidado aos eventos (ou use `c_playerAny` e confira `EventPlayer()`).
- **Seleção forçada** (`UnitSelect(u, 1, ...)`) só altera a seleção do host.
- **Dificuldade.** Dois jogadores com um exército facilitam missões. Considere aumentar dificuldade inimiga ou tamanho das ondas.
- **Gatilhos de saída.** A maioria das missões tem gatilhos de trapaça de vitória/derrota em `TriggerAddEventPlayerLeft(..., c_playerAny, ...)`. O inicializador encerra ambos quando alguém sai; hoje não importam. Confira os novos.

### <a id="separate-armies-planned-mode-real-map-work"></a>Exércitos separados (modo planejado): trabalho real no mapa

A seção "Matters for separate armies" do verificador é a lista de tarefas:

- **Unidades do jogador 1** (quantidades, posse, criação). Objetivos como treinar 10 marines ou levar unidades a X contam só jogador 1. Decida por objetivo: contar ambos ou manter responsabilidade do host.
- **Recursos e suprimento do jogador 1** (minerais iniciais, recompensas).
- **Tecnologia do jogador 1** (desbloqueios, melhorias, pesquisas do centro). Convidado precisa das mesmas chamadas para sua vaga, ou tecnologia de seus próprios bancos (modo de melhorias separadas).
- **Conteúdo espacial** a construir no editor: segundo ponto inicial, espaço de base e unidades iniciais do convidado. Não pode ser gerado.

**Projeto (decidido em 2026-10-21).** A missão adere tendo **dois jogadores humanos (user)** no mapa. Só assim o inicializador mostra opção "separate armies" e configurações. Mapa normal (um humano) sempre usa exército e melhorias compartilhados. Num mapa de dois humanos:

| Responsável | O que faz |
|---|---|
| Autor do mapa | Vaga do segundo, ponto inicial, espaço de base, forças iniciais, dificuldade/equilíbrio para dois exércitos |
| Inicializador (automático) | Convidado usa segunda vaga criada pelo autor (sem clonagem). Verificações de objetivos e posse do jogador 1 também contam o segundo; desbloqueios tecnológicos do primeiro espelhados |
| Configuração: unidades dadas pela missão (resgates, reforços) | Descobridor (padrão; jogador cujas unidades acionaram), divididas/alternadas ou duplicadas |
| Configuração: dinheiro dado pela missão | Duplicado (padrão) ou dividido |
| Configuração: créditos, pesquisa, melhorias (ligada à sincronização do centro) | Compartilhados (ambos usam progresso do host) ou separados (progresso e compras individuais) |

**Implementado (2026-10-21, `SeparateArmies.cs`).** O mapa precisa de:

- Segundo jogador com controle **User** nas configurações (qualquer vaga; primeira User após jogador 1 será do convidado), raça e unidades/estruturas posicionadas. Ponto inicial opcional: após abertura, câmera vai para unidades próprias. Nomeie no script se quiser (`gv_pLAYER01_USER2 = 14;`); inicializador não precisa.
- Nada mais. Mapa com dois humanos só é jogado cooperativamente, sem precisar alternativa solo; mapas com um humano continuam com exército compartilhado.

O que o inicializador faz nesse mapa:

- Convidado entra naquela vaga com sua raça (sem clonagem).
- Alianças: todas as relações do jogador 1 com os demais (hostilidade, visão, ajuda, conversa, derrota, deslocamento) copiadas ao convidado a cada segundo; primeiro e convidado são aliados com visão compartilhada (sem controle ou gastos compartilhados).
- Contagem: grupos e verificações de posse do jogador 1 contam ambos; levar unidades a X, resgates e "todas as suas unidades morreram" (derrota só quando ambos perdem o exército) funcionam para qualquer um. Se o script já conta unidades do convidado (qualquer `UnitGroup(..., <guest>, ...)`), isso é ignorado no mapa inteiro.
- Dinheiro e tecnologia: todo definidor `PlayerModifyProperty*` e `TechTree*` para o primeiro também se aplica ao convidado (minerais iniciais, desbloqueios, pesquisas); melhorias do arsenal da campanha aplicadas ao convidado no início. Configuração "Mission money": ambos recebem (padrão) ou dividem (só renda durante a missão: metade para cada).
- Recursos coletáveis: paletes Liberty (dados: habilidade `PickupMinerals100`/`PickupGas100` paga a quem passa), outros coletáveis nos dados de habilidades/efeitos do mapa ou mods e depósitos de script `libCamp_gf_DestroyCacheAndGivePlayerResources` do Kit: outro recebe mesma quantia, ou metade para cada com divisão.
- Unidades dadas ao jogador 1 durante a missão (`UnitSetOwner`, `libNtve_gf_RescueUnit`, `UnitCreate`, `libNtve_gf_CreateUnitsAtPoint2`, `libNtve_gf_CreateUnitsWithDefaultFacing`): configuração "Units the mission gives": quem encontrou (padrão; unidades mais próximas), alternância ou ambos. Heróis e tudo dado antes do começo efetivo ou durante cena continuam do jogador 1. Visão de unidade compartilhada com ele também é compartilhada com convidado.
- Ainda não: créditos/pesquisa/melhorias separados de cada centro (ambos usam progresso do host).

**Planejado: compras e progresso do centro (decidido em 2026-10-22, não implementado).** Uma configuração para campanhas de duas facções (exércitos separados), cobrindo dinheiro, melhorias do arsenal Hyperion e pesquisas: "vale o banco do jogador 1" (progresso do host para ambos) ou "dinheiro, melhorias e pesquisas individuais em bancos próprios". Um exército (Archon) sempre usa banco do host. Em aberto: o que o centro do parceiro permite em Archon. Bloquear compras ou deixá-lo gastar créditos compartilhados com aviso claro. WoL original não tem reembolso; compra acidental não pode ser desfeita. Campanhas Kit reembolsam gratuitamente. Hoje as compras do parceiro só contam se ele iniciar a missão.

A linha de configurações só aparece se a pasta tiver ao menos um mapa assim. `SC2_COOP_SEPARATE=1` ainda tenta o mesmo num mapa normal de um humano (vaga clonada e cópias das unidades iniciais do primeiro).

### <a id="other-campaigns"></a>Outras campanhas

- **Campanhas estilo WoL@Kit** (mapa TStory01 + `libWoLC_gf_LaunchMission`): devem funcionar diretamente; execute verificador e teste básico abaixo.
- **Campanhas Blizzard e outros mods:** hook de lançamento no centro e lista de bancos dependem da biblioteca da campanha. Progresso também em bancos, mas com nomes diferentes e possivelmente assinados. Espere adicionar adaptador para essa biblioteca.
- **Mods WoL baseados no original: compatíveis** (2026-10-21, testado em UED 3.0.3). Inicializador distingue bibliotecas pelas chamadas do centro e da missão; nada a configurar. Centro: `libCamp_gf_LaunchMission` substituída por cópia do inicializador (escolha A/B, apresentação, PrepareForMission, fim de jogo) que registra seleção final; `-cooplaunch TRaynor01` funciona após apresentação da missão. Missões: `-coopwin/-coopwinnow/-cooplose` usam nomes libCamp; `-coopobj <objective id> [fail]` recebe identificador do objetivo do motor. Ainda não: repetições Mission Archives da Blizzard e tecnologia do convidado em exércitos separados (tabela).
- Avaliação (2026-10-21: UED 3.0.3, WoL Nod 1.1, 3-Race Nightmare de RaptorX, WoL+ CCM): todos mantêm centro e biblioteca Blizzard (`libCamp`, Liberty/LibertyStory), com as mesmas cinco chamadas `libCamp_gf_LaunchMission(mapID, simulation, difficulty)` no script do centro; um adaptador "vanilla" cobre todos. Bibliotecas Kit são cópia renomeada de libCamp; a maioria dos hooks tem correspondência direta:

  | Hook do inicializador (Kit) | Original | Notas |
  |---|---|---|
  | `libWoLC_gf_LaunchMission(name, ...)` | `libCamp_gf_LaunchMission(mapID, ...)` | Identificador é enum; nome de arquivo de `libCamp_gv_tS_MapFile[id]`. Missões A/B (THanson03, TTosh03, TValerian02) escolhem dentro da biblioteca. |
  | `libWCMI_gf_EndCampaignMission` | `libCamp_gf_EndCampaignMission` | Igual: vitória mostra pontuação, derrota encerra jogo. |
  | `libWCMI_gf_ZS_SetMissionObjectiveState` | nenhum necessário | Missões originais chamam `ObjectiveSetState` diretamente (já redirecionado); libCamp só guarda número. |
  | `libWCMI_gf_GameOver/GameIsOver`, `libWCMI_gt_WM_VictoryContinue` (comandos de teste) | `libCamp_gf_RunMissionVictorySequence`, continuar na pontuação | Precisa de indicador próprio de fim. |
  | Bancos (BankList.xml) | TCampaign, CampaignPS, TStory01, um por missão | Bancos simples, sem assinatura, do jogador 1; sincronização existente funciona diretamente. |
  | `libWoLC_gf_WC_ApplyTech(player)` (exércitos separados) | `libCamp_gf_TS_UpdateTechStates()` | Só jogador 1; tecnologia do convidado precisa de outro caminho (em aberto). |
  | Mission Archives (biblioteca Kit) | Arquivos da Blizzard | Ainda não examinados. |

  Em execução (2026-10-18): TStory01 Blizzard reempacotado funciona como jogo API (introdução, seleção e lançamento); `RequestGameInfo` nele derrubou SC2.

  Missões iniciadas pelo inicializador não são mapas de transição (`GameIsTransitionMap()` é false), interpretado por ambas as bibliotecas como "iniciado do editor ou reinício" (2026-10-22, créditos variando entre missões):
  - `libCamp_gf_PurchaseStorymodeTech()` de libCamp (chamada por toda missão) executa então a compra de tecnologia média de depuração: créditos recalculados pelas recompensas esperadas menos compras, progresso ajustado ao caminho esperado, missão salva como última bem-sucedida (até derrota pagava recompensa no centro). Inicializador remove a chamada (do centro não faz nada). TRaynor01-03 ainda recebem compra de depuração dentro de `libCamp_gf_LoadCampaignData`; diálogo de derrota salva derrota (`libCamp_gf_PrepareForStoryMode(defeat)`), para centro não pagar.
  - Ambas carregam captura de reinício da missão quando existe (original: banco próprio; Kit: seções `<mission>|...` do banco da campanha, `MissionSectionExist`), desfazendo compras desde tentativa anterior. Começo pelo centro descarta captura primeiro (original: inicializador apaga banco; Kit: centro limpa indicador); Retry a mantém.
  - Centro paga recompensa da última missão a cada abertura até salvamento marcar como paga; centro do host salva após 10 s e novamente antes de fechar sem iniciar missão.

## <a id="testing-a-ported-campaign"></a>Testando campanha adaptada

1. Execute `campaign-check` e leia a lista por mapa.
2. Teste básico de toda missão num PC (modo local): `SC2_COOP_TEST_LAUNCH=<mission,mission,...>` inicia cada uma do centro; `SC2_COOP_TEST_WIN=45` vence após 45 s. Procure missões que não encerram, erros ou estado API do convidado saindo de 3.
3. Objetivos: `-coopobj <objective>` na missão; ambos devem permanecer no jogo.
4. Jogue algumas missões de verdade em dois PCs.
