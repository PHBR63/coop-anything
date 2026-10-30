# <a id="xcom-2-war-of-the-chosen--co-op-campaign-notes"></a>XCOM 2: War of the Chosen — notas da campanha cooperativa

Registro contínuo. Observações, fatos derivados, suposições e questões em aberto são mantidos em listas separadas.

## <a id="goal"></a>Objetivo
- Camada estratégica compartilhada (Avenger): ambos os jogadores podem escolher pesquisas/construções/melhorias de instalações e
  editar qualquer soldado.
- Seleção de esquadrão: cada jogador escolhe seu próprio esquadrão (por exemplo, 4 + 4 = 8 em campo);
  um soldado escolhido por um jogador fica bloqueado para o outro.
- Tático: cada jogador controla apenas seus próprios soldados; os jogadores se alternam.
- 2 jogadores, Steam, WotC + todos os DLCs.

## <a id="session-1--2026-10-24-triage--research"></a>Sessão 1 — 2026-10-24: triagem + pesquisa

### <a id="observed"></a>Observado
- Identidade do jogo: build Steam 8270065, changelist 699444, UE3.
- "XCOM 2: Tactical Co-Op", da Team Dragonpunk, Workshop 792693587: status "Final", criado em
  3 de novembro de 2016, última atualização em 3 de setembro de 2017, 61,8 MB. Cooperativo tático para dois jogadores em missões
  da campanha, com divisão do esquadrão; permite importar soldados do jogo do amigo; sem
  Ironman; ambos devem estar em Squad Select ao convidar. A equipe passou a outros jogos.
  Fonte: https://steamcommunity.com/sharedfiles/filedetails/?id=792693587
- Nenhum repositório público de código-fonte encontrado (busca de repositórios no GitHub por "xcom2 coop", "dragonpunk xcom": 0 resultados).
- "WOTC Multiplayer mods", de robojumper (Workshop 1571537500), descontinuado informalmente em favor de um
  recurso do X2WOTCCommunityHighlander para mods no multijogador.
  Fonte: https://steamcommunity.com/sharedfiles/filedetails/?id=1571537500
- Aplicativo Steam 602410 = "XCOM 2 War of the Chosen SDK" (nome de installdir em steamapps).

### <a id="searched-nothing-more-found"></a>Pesquisado (nada mais encontrado)
- web: "XCOM 2 co-op campaign mod", "Team Dragonpunk ... github source",
  "WOTC shared campaign multiplayer strategy layer XComGameStateNetworkManager"
- Busca de repositórios na API do GitHub: "xcom2 coop", "dragonpunk xcom"
- DIRECTORY/games/issues de coop-anything: nenhuma entrada de XCOM

### <a id="unknown"></a>Em aberto
- Se Tactical Co-Op funciona no WotC (última atualização 5 dias após o lançamento de WotC; provavelmente para o jogo base).
- Se o pacote do Workshop inclui `Src/` (muitos mods de XCOM 2 incluem).
- Como a camada multijogador original (XComGameStateNetworkManager) envia estados do jogo — ler o código-fonte do SDK.

## <a id="session-1-cont--sdk-source-reading"></a>Sessão 1 (cont.) — leitura do código-fonte do SDK

SDK: aplicativo Steam 602410 "XCOM 2 War of the Chosen SDK", buildid 3075887, 4137 arquivos .uc em
`<SDK>/Development/SrcOrig`. Community Highlander (MIT, github.com/X2CommunityCore/
X2WOTCCommunityHighlander, enviado em 2026-10-12) clonado como referência.

### <a id="observed-source-wotc-sdk-srcorigxcomgameclasses"></a>Observado (código-fonte, WotC SDK SrcOrig/XComGame/Classes)
- `XComGameStateNetworkManager` (native(MP), chamável por script): CreateServer/CreateClient(URL),
  SendHistory, SendPartialHistory, SendGameState, SendMergeGameState, SendGameStateContext,
  SendRemoteCommand(string, array<byte>) + auxiliares AddCommandParam_Int/String/Bool,
  SendLoadTacticalMap, SendPlayerReady, SendSyncPoint, relatórios de validação/dessincronização.
  Delegates para cada recebimento. `HasServerConnection/HasClientConnection`.
- `X2GameRuleset.SubmitGameStateContext`: se NetworkMgr.HasConnections() e o contexto
  veio de entrada do usuário (`bSendGameState`), ele entra na fila de envio; contextos remotos
  (`bNetworkAdded`) reutilizam a semente aleatória do remetente.
- Configuração distribuída `XComGame/Config/DefaultGame.ini:105 bPauseGameStateSending=true`:
  o multijogador usa "jogador ativo é a autoridade": o jogador ativo executa o conjunto de regras; ao fim do turno,
  `SendPartialHistory`, o remoto responde "HistoryReceived", depois "SwitchTurn"; o jogador
  inativo assiste por `XComMPReplayMgr` (X2TacticalMPGameRuleset.uc ~300-360, 1095-1275).
- Condição de remoto = `XComGameState_Player.GetGameStatePlayerNetId() != local UniqueId`
  (X2TacticalMPGameRuleset.GameStatePlayerOrGroupIsRemote).
- Transporte: `UIMPShell_Lobby.CreateServer(Port=7777, bSteam)`: IP simples, ou sockets Steam
  quando a opção de URL "steamsockets" é adicionada. NetworkDevice do motor = IpNetDriverSteamworks.
- Comandos exec de trapaça (XComCheatManager.uc 3697-4091): MPCreateServer, MPCreateClient,
  MPSendHistory, MPSetPauseGameStateSending, X2PrintNetworkDebug, MPCreateLobby, ...

### <a id="derived-design-direction-not-yet-tested"></a>Derivado (direção do projeto, ainda não testada)
- Tático: manter UM jogador XCom; dividir o turno XCom em subfases A e depois B. O
  dono da subfase é a autoridade; passagem = SendPartialHistory + reprodução (igual ao fim
  de turno multijogador). Turnos de Alien/Lost/Chosen rodam no anfitrião. Unidades têm uma marca de dono.
- Estratégia: salvamento sob autoridade do anfitrião; cliente recebe histórico completo ao entrar (SendHistory).
  Edições por um "bastão": um jogador edita por vez, a passagem envia o histórico. Depois: bloqueios
  por objeto + SendMergeGameState para edição paralela de soldados.
- Testar transporte: IP em 127.0.0.1, duas instâncias em um PC (não se sabe se o executável permite).

### <a id="unknown-1"></a>Em aberto
- Duas instâncias de XCom2.exe podem rodar simultaneamente em um PC/conta Steam?
- SendHistory funciona na camada estratégica (Avenger), e o estado
  visual do cliente (Avenger, Geoscape) é atualizado após recebê-lo?
- Onde as execuções de teste gravam configurações/logs (provavelmente %USERPROFILE%\Documents\My Games\...).

## <a id="session-1-cont--running-test-instances"></a>Sessão 1 (cont.) — execução de instâncias de teste

### <a id="observed-1"></a>Observado
- A instalação de teste tinha um `XComGame/CookedPCConsole/TacticalResources_SF.upk` corrompido
  (falha ao carregar o menu: "Texture2D AdventDeskA.Textures.AdventComputerA_MSK: Serial size
  mismatch: Got 1588, Expected 1956"). "Verificar integridade" do Steam o substituiu (6,7 MB);
  o menu então carrega. Lição: verificar a integridade ANTES de copiar uma instalação de teste.
- `-nohomedir` (string presente no executável) faz o jogo gravar Config/Logs/SaveData em
  `<install>/XComGame/...` em vez de `%USERPROFILE%\Documents\My Games\...`
  (os XCom*.ini gerados aparecem em `<install>/XComGame/Config`). Mantém os testes longe
  da pasta real do Steam Cloud.
- A segunda instância encerra com código 1 antes de gravar um log enquanto a primeira está em execução.
  Causa: mutex `\Sessions\<n>\BaseNamedObjects\UnrealEngine3_<n>` (criado por
  `CreateMutexW("UnrealEngine3_%d%s")`). Fechar esse handle dentro da instância A
  (DuplicateHandle com DUPLICATE_CLOSE_SOURCE, mesmo usuário, sem administrador) permite iniciar B;
  ambas registram "STEAMWORKS initialized 1". Fechar `CDdf212806D6EmB31yE0c` e
  `{52813408-...}_0` não ajudou (não são a proteção).
- Segunda instalação = clone da primeira por links físicos, mas com cópia própria de
  `XComGame/Config` (o jogo regrava os inis ali).
- Ferramentas: `tools/launch_pair.ps1`, `close_remote_handle.py`, `hardlink_clone.py`,
  `re_callers.py`, `re_dis.py`, `trace_start.py` (no espaço de trabalho do autor, a mover
  para o repositório do jogo).

## <a id="session-1-cont--first-network-experiments-two-instances-one-pc"></a>Sessão 1 (cont.) — primeiros experimentos de rede (duas instâncias, um PC)

Repositório do mod: `WOTCCoopCampaign` (espaço de trabalho do autor; será publicado em repositório próprio).
Bot de teste: `CoopHarness` (Actor, etapas de `XComCoopHarness.ini`, progresso mantido no
objeto padrão da classe entre carregamentos de mapas) + `CoopHarnessNet` (Object que guarda os delegates
de rede). Executor: `tools/run_pair_test.ps1` (ativa o mod pelo
`DefaultModOptions.ini` das instalações de teste; o jogo regenera `XComModOptions.ini` a partir dele).

### <a id="observed-2"></a>Observado
1. `XComGameStateNetworkManager.CreateClient` com um host em notação pontuada não envia um único
   pacote (capturador UDP na porta de destino: 0 pacotes; log de B mostra o par como
   `0.0.0.127`). Com o host como UM inteiro decimal (127.0.0.1 -> "2130706433"), o
   cliente envia imediatamente (95 pacotes em 30 s). Aplica-se ao modo IP de `IpNetDriverSteamworks`.
2. Cliente e servidor em um PC não podem compartilhar a porta: o cliente registra
   "Game client on port 7777" (porta padrão da URL). Servidor em 7778 funciona.
3. `HasConnections()` já é verdadeiro enquanto um servidor apenas escuta; usar os delegates
   `PlayerJoined` / `NotifyAcceptedConnection` para detectar um par real.
4. Delegates no gerenciador de rede não devem apontar para um Actor: o gerenciador vive além dos
   mapas, o World antigo é mantido vivo e o próximo carregamento de mapa dispara uma asserção
   ("World XPACK_Shell_Intro.TheWorld not cleaned up by garbage collection!",
   UnGame.cpp:3107, referenciador `XComGameStateNetworkManager...ReceiveHistoryDelegates`).
5. Comandos remotos bidirecionais funcionam (CoopPing/CoopPong em ambas as direções).
6. **A transferência do histórico estratégico funciona**: A inicia uma campanha (início por trapaça, 225 quadros,
   22 soldados, 4000 suprimentos), `MPSendHistory`; B no menu principal recebe
   `ReceiveHistory frames=225` com o mesmo primeiro soldado (ObjectID 411) e suprimentos,
   depois `open Avenger_Root?game=XComGame.XComHeadQuartersGame` carrega a campanha de A em B.
   A conexão sobrevive à troca de mapa (ping/pong após carregar).
7. Após carregar o Avenger, o histórico de B cresce em 7 quadros locais (225 -> 232) que A
   não tem: efeitos colaterais do carregamento criam estados do jogo localmente.

### <a id="derived"></a>Derivado
- Fluxo de entrada na campanha compartilhada: anfitrião carrega salvamento -> cliente conecta -> anfitrião envia
  histórico completo -> cliente abre o Avenger. Comprovado de ponta a ponta no aparato de testes.
- Quadros criados localmente ao carregar (item 7) devem ser suprimidos no cliente ou
  o cliente deve aceitar ser sobrescrito pelo próximo histórico parcial do anfitrião.

### <a id="unknown--next"></a>Em aberto / próximos passos
- Transporte Steam (`steamsockets`) entre duas contas Steam diferentes.
- SendPartialHistory (delta) se aplica sobre os 7 quadros extras do cliente?
- Como os visuais do Avenger/Geoscape são atualizados quando o histórico muda sob um mapa carregado.

## <a id="session-1-cont--strategy-sync-with-a-baton-merge-game-states"></a>Sessão 1 (cont.) — sincronização estratégica com um bastão (mesclagem de estados do jogo)

Alterações do mod: `CoopHeadquartersGame` (ModClassOverrides em XComHeadquartersGame) permite que o
cliente entre no Avenger pelo caminho de salvamento carregado ("mirror") em vez do
caminho de retorno do tático. `CoopSession` envia cada novo quadro local do portador do bastão
como `SendMergeGameState` + um comando de impressão digital "CoopFrame" (suprimentos, informações, ligas,
elério, tripulação, instalações, tecnologias, tamanho do esquadrão).

### <a id="observed-test-baton-both-ways-run_pair_testps1-two-instances-127001"></a>Observado (teste "baton-both-ways", run_pair_test.ps1, duas instâncias, 127.0.0.1)
1. Entrada espelhada: B carrega a campanha de A (222 quadros) e adiciona apenas UM quadro local,
   "Pre Mission End UI Sequence Hook" (`XGGeoscape.OnEnterMissionControl`, criado
   incondicionalmente, também no carregamento normal de um salvamento). O caminho simples `open Avenger_Root`
   adicionava 7.
2. A -> B: `GiveResource Supplies 123`, `GiveResource Intel 7` em A; B registra
   "in sync" para ambos (sup4123, int1007).
3. B -> A após mover o bastão (`@nobaton` em A, `@baton` em B): `GiveResource
   Supplies 50`, `GiveResource AlienAlloy 9` em B; A registra "in sync" para ambos
   (sup4173, all1009). As impressões digitais finais são iguais dos dois lados.
4. Um estado de mesclagem recebido é aplicado ao quadro atual do receptor, NÃO adiciona um
   quadro: A permanece em 225 quadros enquanto B, que fez as alterações, tem 227. Contagens de quadros
   e índices de histórico, portanto, não são comparáveis entre os jogadores.
5. O comando remoto "CoopFrame" enviado DEPOIS do estado de mesclagem é tratado ANTES dele no
   receptor (mesmo tick). A primeira execução comparava impressões digitais no tratador do comando e
   registrava DESYNCs falsos. Correção: enfileirar a impressão digital e comparar em
   OnReceiveMergeGameState.
6. Dois quadros enviados em um tick (trapaça + "Analytics Resource Changed") chegaram como dois
   comandos CoopFrame, mas UM callback de estado de mesclagem. Usa-se a impressão digital mais recente.
7. O cliente cria quadros locais a partir de ações puramente de interface enquanto não tem o bastão
   (Entered/Exited Facility, Unmark needs attention, Psi Lab Intro alert seen, Trigger
   Objective Narrative Moment). Um `MPSendHistory` completo do anfitrião os sobrescreve.

### <a id="derived-1"></a>Derivado
- A comparação de impressão digital/conteúdo funciona; a de índice de quadro não (item 4).
- Estados de mesclagem servem para "um editor por vez" (bastão) em mudanças de recursos. Ainda não coberto:
  criação de objetos (novo soldado, construção de instalação, início de pesquisa), em que novos ObjectIDs são
  alocados apenas de um lado.

### <a id="unknown--next-1"></a>Em aberto / próximos passos
- Estados de mesclagem transportam objetos recém-criados e mantêm os ObjectIDs alinhados?
- Elementos da interface do Avenger/Geoscape se atualizam após uma mesclagem (a barra de recursos não foi conferida
  visualmente; apenas o estado do jogo foi lido).
- Política para os quadros locais de B exclusivos da interface (item 7): descartar, enviar ou sobrescrever.

## <a id="session-1-cont--objects-created-through-merge-states"></a>Sessão 1 (cont.) — objetos criados por estados de mesclagem

Adições ao aparato de testes: `@crewinfo N` (últimos N tripulantes, verificação de IDs duplicados), `@objrange a b`
(classe de cada ObjectID em um intervalo). A impressão digital agora também inclui o último ObjectID
de Crew, Facilities e TechsResearched. Nenhum `MPSendHistory` completo após a entrada nestes
testes, portanto só estados de mesclagem movem dados.

### <a id="observed-tests-baton-objects-baton-objids"></a>Observado (testes "baton-objects", "baton-objids")
1. A (bastão): `GiveScientist` -> nova Unit 2316 em A; `GiveTech Psionics` (adiciona a tecnologia +
   3 quadros "Trigger Objective Narrative Moment"). B: "in sync", o cientista existe em
   B com o mesmo ObjectID e nome.
2. Bastão para B: `GiveEngineer` -> nova Unit 2318 em B; A: "in sync", mesmo ID e nome.
3. `@objrange 2280 2345` fornece a mesma classe para cada ID em A e B, antes e depois
   das duas criações. O ID 2317 está vazio nos DOIS lados (alocado, nunca armazenado; causa desconhecida).
   Nenhum ID de tripulante duplicado. Portanto, o contador de ObjectID do receptor avança além dos objetos
   recebidos; sem colisão de IDs quando o outro jogador cria objetos em seguida.
4. A entrada espelhada não aloca ObjectIDs nesse intervalo ("Pre Mission End UI Sequence Hook"
   só modifica objetos existentes).
5. A enviou 6 quadros para o cientista + tecnologia; B recebeu 2 callbacks de estado de mesclagem (um por
   tick). Estados de mesclagem se agrupam por tick.
6. run_pair_test.ps1 imprimia apenas as últimas 60 linhas de log, então despejos longos ocultavam todo o
   resto; agora são 200 linhas, com remoção das linhas vazias `obj N none`.

### <a id="derived-2"></a>Derivado
- Com um editor por vez (bastão), estados de mesclagem bastam para mudanças de recursos e
  criação de unidades e tecnologias, incluindo alinhamento de ObjectIDs.

### <a id="unknown--next-2"></a>Em aberto / próximos passos
- Instalações (GiveFacility também carrega mapas de salas no remetente; os visuais do Avenger do receptor
  não são atualizados por um estado de mesclagem).
- Atualização de interface no receptor após mesclagem (barra de recursos, listas de tripulação).
- Quadros locais do cliente exclusivos da interface enquanto ele não tem bastão (descartar / enviar / sobrescrever).
- Edições dos dois jogadores ao mesmo tempo (sem bastão): não cobertas pelos testes, espera-se conflito.
## <a id="session-1-cont--facilities-and-screen-refresh-on-the-receiver"></a>Sessão 1 (cont.) — instalações e atualização de tela no receptor

Instalações de teste: telas vermelhas desativadas (`[XComGame.RedScreenManager] bDisabled=true` no
DefaultGame.ini das cópias de teste, backup `.bak`). As capturas dessas telas eram das
janelas de teste: "FullyLoading in DynamicLoadObject: DLC_60/DLC_90_NarrativeMoments" e
"Plot_Multiplayer_Test ... Unable to find associated package": avisos de desenvolvimento do jogo original, também presentes
nos logs de execuções sem alterações, sem relação com o mod. Continuam registrados como `Warning: Redscreen:`.

Adições ao aparato de testes: `@rooms` (por sala: instalação, mapa desejado, estado de carregamento, STALE quando o
mapa carregado difere do estado), `@hud` (HQPres.ClearUIToHUD), `@lookroom N`,
`@clearroom N` (remove uma instalação: RemoveStateObject), `@buildroom N Template` (mudanças
de estado de GiveFacility, tela via RefreshAvenger). `shot` no jogo grava
`<install>/XComGame/Screenshots/PCConsole/ScreenShotNNNNN.bmp` (funciona em modo janela).
O início por trapaça preenche todas as 19 salas, então os testes esvaziam a sala 3 e constroem nela.

`CoopSession.RefreshAvenger(state)`, executado a cada estado de mesclagem recebido (e após as
edições de sala do próprio aparato de testes): para cada HeadquartersRoom no estado cujo mapa carregado difere
de `XGBase.GetMapname(room)`, enfileira uma troca de sala exatamente como o método privado
`XGBase.QueueRoomSwap` (adiciona ao `m_queuedRoomSwaps` público, `StreamInRoom(idx, true)`; o
mapa antigo é removido em `OnRoomLevelLoaded`), depois `m_kAvengerHUD.UpdateResources()` e
`m_kFacilityGrid.UpdateData()`.

### <a id="observed-3"></a>Observado
1. Remoção viaja em estados de mesclagem: `@clearroom 3` em A -> B "in sync", número de instalações
   19 -> 18 em B, sala 3 trocada por AVG_ER_A.
2. Criação: `@buildroom 3 Laboratory` em A -> ObjectID da nova instalação idêntico em B, sala
   trocada de volta por AVG_Laboratory_A em B, "in sync". `@rooms` em B: nenhuma sala STALE.
3. A barra de recursos de B acompanha: energia 42/18 -> 39/18 -> 42/18 nas capturas de B, igual a A.
4. A atualização de tela da própria trapaça GiveFacility (RemoveRoom + StreamInRoom) deixava um buraco na
   sala no REMETENTE (captura "A rebuilt", primeira execução). A troca enfileirada mostra a
   sala corretamente em A nas duas execuções posteriores.
5. A câmera de B após `@hud` + `@lookroom 3` varia entre execuções (4 execuções): visão correta
   do laboratório (2x), visão "dentro de uma parede" com salas vizinhas (1x), visão externa ao Avenger
   no deserto do local de pouso (1x). Todas as 19 salas estão carregadas e visíveis em B
   (ld/vis/want=true) quando isso ocorre. A câmera de A estava correta em todas as execuções.

### <a id="unknown--next-3"></a>Em aberto / próximos passos
- Causa do item 5: o caminho de entrada espelhada (pula a configuração normal da câmera no carregamento?), uma
  corrida entre a saída do mapa estratégico de ClearUIToHUD e CAMLookAtRoom, ou mesclagens
  chegando durante a transição. Precisa ser resolvido antes de jogadores usarem o Avenger do cliente.
- Construção real (projeto de construção + passagem de tempo) define `UpdateRoomMap`; o
  próprio SetAvengerVisibility do receptor também troca a sala e grava um quadro local (não coberto pelos testes).

## <a id="session-1-cont--client-camera"></a>Sessão 1 (cont.) — câmera do cliente

Aparato de testes: `@cam` registra estado da câmera, classe CameraState, CurrentRoom, AnimTime e o
ponto de visão do jogador (loc/rot). `unsuppress DebugHQCamera` (console) ativa o log de câmera do jogo
(suprimido em DefaultEngine.ini).

### <a id="observed-test-camera"></a>Observado (teste "camera")
1. A entrada espelhada (`CoopHeadquartersGame`) difere do caminho de carregamento distribuído
   (`XComHeadquartersGame.StartMatch`, bPerformingStandardLoad) apenas por
   `OnlineEventMgr.FinishLoadGame()` (nativo, "instantiate saved actors").
2. Após a entrada espelhada, a câmera de B está em `FreeMovementView` (o corte transversal do Avenger, como
   após `BootstrappingStrategy`); a de A, após o início por trapaça, está em `EarthView`.
3. Após `@hud` + 8 s + `@lookroom 3`: A e B em `BaseRoomView`, sala AddonCam_R1_C1,
   loc=-224,-280,1380 rot=0,16384,0; ambas as capturas mostram o laboratório corretamente.

4. O testador confirmou movimentação do mouse sobre as janelas do jogo durante as execuções anteriores.
   B é iniciado em segundo lugar e tem o foco da janela; A nunca teve foco e nunca mostrou uma visão
   errada; FreeMovementView desloca a câmera com o mouse.

### <a id="derived-3"></a>Derivado
- As visões erradas do cliente (dentro de uma parede, deserto fora do Avenger) eram entrada do mouse,
  não um erro de sincronização ou entrada espelhada. Lição para testes: ninguém toca no PC durante a execução;
  registrar `@cam` junto de cada `shot`.

## <a id="session-1-cont--local-frames-on-the-player-without-the-baton"></a>Sessão 1 (cont.) — quadros locais no jogador sem o bastão

### <a id="observed-4"></a>Observado
1. Teste "client-local-alloc": B SEM o bastão executou `GiveScientist` -> Unit 2339 local.
   Depois A (bastão) executou `GiveEngineer` -> Unit 2339 também em A. O estado de mesclagem de A substituiu
   o objeto 2339 de B pelo engenheiro; o cientista de B desapareceu. As impressões digitais indicaram
   "in sync" (comparam o estado final; a colisão é invisível para elas).
2. `CoopStrategyRuleset` (subclasse de X2StrategyGameRuleset, retornada por
   `CoopHeadquartersGame.GetGameRulesetClass()`) sobrescreve `SubmitGameStates`: enquanto
   conectado, sem o bastão e sem estar aplicando um estado remoto, um quadro que cria
   um objeto é rejeitado (`CleanupPendingGameState`, registrado como "blocked frame without
   baton"). Quadros que só modificam objetos existentes passam.
3. A primeira versão testava "novo" com `History.GetGameStateForObjectID(id) == none`: nunca
   verdadeiro, nada era bloqueado (o histórico já resolve IDs do estado pendente).
   `StateObject.GetPreviousVersion() == none` funciona.
4. Teste "client-local-alloc-blocked-2": GiveScientist de B bloqueado (ID 2319 alocado,
   nunca armazenado); o quadro "New Popup Event" posterior à trapaça ainda passou; sem
   avisos de script. O engenheiro de A chega em B como 2319, sem substituição. Após o bastão
   passar para B, o cientista de B (2321) chega a A; ambos terminam iguais, sem IDs duplicados.

### <a id="derived-4"></a>Derivado
- Regra: o jogador sem o bastão não deve criar objetos; o bloqueio em
  SubmitGameStates é a rede de segurança. Fluxos reais de interface presumem que o envio funciona, então a
  interface do não portador não deve oferecer essas ações (contratar, construir, iniciar pesquisa...).

### <a id="unknown--next-4"></a>Em aberto / próximos passos
- Passagem do bastão pela rede (comando de solicitação/concessão, ambos os lados concordam) — hoje o
  aparato de testes o define manualmente de cada lado.
- Interface do não portador: quais telas criam objetos; desativá-las ou encaminhá-las.
- Quadros que modificam objetos existentes no não portador divergem até a próxima mesclagem do
  mesmo objeto; inofensivo para sinalizadores de interface, desconhecido para qualquer outra coisa.

## <a id="session-1-cont--baton-handoff-over-the-network"></a>Sessão 1 (cont.) — passagem do bastão pela rede

Protocolo (CoopSession): o não portador envia "CoopBatonRequest"; o portador larga o
bastão e envia "CoopBatonGrant" (época, impressão digital, maior ObjectID do histórico);
o receptor pega o bastão quando sua impressão digital é igual à da concessão, seu maior
ObjectID é >= ao da concessão e nenhum quadro remoto (CoopFrame ou mesclagem) chegou por 1 s;
então envia "CoopBatonAck". A verificação é repetida em cada estado de mesclagem e por um
temporizador único de actor (CoopGrantRetry). Aparato de testes: `@batonreq`, `@grant` (concessão não solicitada,
para a corrida), `@waitbaton`.

### <a id="observed-5"></a>Observado
1. A primeira versão esperava a fila de impressões digitais CoopFrame recebidas ficar vazia.
   Teste "baton-protocol": B enviou 3 quadros, A recebeu 3 comandos CoopFrame mas menos callbacks
   de mesclagem; uma impressão digital ficou enfileirada para sempre e A nunca pegou o bastão.
   Comandos e callbacks de mesclagem não correspondem 1:1.
2. Segunda versão: `WorldInfo.SetTimer(..., inObj=session)` para o período de silêncio nunca
   disparou (teste "baton-protocol-2": B tinha fp + maxID correspondentes, esperou para sempre).
   O temporizador próprio de um Actor criado funciona.
3. Teste "baton-protocol-3": A GiveScientist (2323), depois `@grant` 0,05 s mais tarde. B recebeu
   a mesclagem primeiro, depois a concessão; coincidiu imediatamente, esperou 1 s de silêncio, pegou o bastão,
   GiveEngineer -> 2324, A recebeu "in sync". Depois A `@batonreq`: B concedeu, A pegou
   imediatamente (último quadro remoto 23 s antes), GiveEngineer -> 2325, B recebeu.
   Final: ambos com 28 tripulantes, IDs 2323/2324/2325, sem duplicados, impressões digitais iguais.
4. Um quadro criado pelo jogo logo após uma concessão no antigo portador ("New Popup Event"
   posterior à trapaça) permanece local (modifica objetos existentes; não bloqueado, não enviado).

### <a id="unknown--next-5"></a>Em aberto / próximos passos
- MaxObjectID percorre cada objeto do histórico (~2300 aqui) a cada verificação; custo em uma
  campanha avançada desconhecido.
- Quadros tardios que só modificam objetos existentes e chegam após o período de silêncio seriam
  mesclados por cima das edições do novo portador.
- Interface: quem pede o bastão e quando (botão, automaticamente ao abrir uma tela de edição).

## <a id="session-1-cont--edit-screens-take-the-baton-coopeditgate"></a>Sessão 1 (cont.) — telas de edição pegam o bastão (CoopEditGate)

Não é só a criação de objetos que precisa do bastão: uma edição pelo não portador que apenas modifica
objetos (por exemplo, um equipamento) nunca é enviada e se perde na próxima mesclagem desse objeto. Portanto,
toda tela em que o jogador muda a campanha exige o bastão.

`CoopEditGate` (UIScreenListener para todas as telas), lista `EditScreens` em
`Config/XComCoopCampaign.ini` (nomes de classes, subclasses contam: UISimpleCommodityScreen,
UIInventory, UIArmory, UIBuildFacilities, UIChooseFacility, UIFacilityUpgrade,
UIChooseUpgrade, UIRecruitSoldiers, UISquadSelect, UIBlackMarket_Sell, UICovertActions,
UIStrategyMap, UIStrategyPolicy, UIPersonnel). UIStrategyMap está na lista porque o
Geoscape faz o relógio avançar.
- Tela de edição aberta sem o bastão -> RequestBaton + `UIProgressDialog` modal
  ("Partner has control", Cancel fecha a tela de edição); fechado por SetBaton(true).
- Portador recebe solicitação com uma tela de edição aberta -> adiada (`bGrantRequested`),
  concedida em OnRemoved da última tela de edição.
- Textos em `Localization/WOTCCoopCampaign.int` e `.rus` (UTF-16).
Aparato de testes: `@open research`, `@open build`, `@close`, `@screens`.

### <a id="observed-test-edit-gate"></a>Observado (teste "edit-gate")
1. A no Geoscape após o início por trapaça (pilha: UIAlert < UIMouseGuard <
   UIStrategyMap[edit] < ...). B `@open research` -> diálogo de espera em B; A registra
   "baton request deferred: edit screen open".
2. A `@hud` (sai do Geoscape) -> "last edit screen closed, handing over the requested
   baton"; B pega após o período de silêncio de 1 s; o diálogo fecha; a captura de B mostra
   a lista de pesquisa.
3. A `@open research` enquanto B está em pesquisa -> diálogo em A, adiada em B; B `@close` ->
   concessão -> A pega, diálogo desaparece, captura de A mostra a lista de pesquisa.
4. Textos em russo aparecem no diálogo. Abrir pesquisa no não portador ainda grava um
   quadro local "Open Choose Research Event" (só modificação, passa).
5. Duas mesclagens durante uma espera por concessão agendaram dois temporizadores CoopGrantRetry; a segunda chamada
   não faz nada.

### <a id="unknown--next-6"></a>Em aberto / próximos passos
- Botão Cancel: ainda não clicado em teste (precisa de um comando do aparato de testes para pressioná-lo).
- Lista de telas é uma primeira hipótese: vagas de equipe dentro de UIFacility, menus de salas do Avenger,
  UIPersonnel usado somente para leitura (agora também pede o bastão), telas adicionadas por DLCs/mods.
- O portador que permanece no Geoscape nunca passa o bastão (por projeto, mas precisa de uma indicação
  visível para o parceiro: quem tem o controle, botão "pedir controle").

## <a id="session-1-cont--baton-indicator-on-the-avenger-hud"></a>Sessão 1 (cont.) — indicador do bastão no HUD do Avenger

`CoopBatonPanel` (UIPanel, adicionado a UIAvengerHUD por CoopEditGate.OnInit; canto superior direito sob
a barra de recursos, 600x40; consulta CoopSession a cada 0,5 s; oculto enquanto desconectado):
"Control: you" / "Partner asks for control - close the screen to hand it over" (portador
com solicitação adiada) / "Control: partner" + botão "Ask for control" (desativado,
"Asked..." após um clique até o bastão chegar) / "Control is being handed to you...".
`CoopSession.bRequestSent` impede solicitações repetidas, limpo quando o bastão chega.
Aparato de testes: `@panel`, `@ask` (chama o tratador do botão), `@cancelwait` (UIProgressDialogue.
OnCancel, o mesmo caminho de clicar em Cancel).

### <a id="observed-tests-baton-panel-panel-cancel"></a>Observado (testes "baton-panel", "panel-cancel")
1. B: "Control: partner" + botão -> `@ask` -> "Asked..." (desativado). A (no Geoscape)
   mostra "Partner asks for control..." (log), A `@hud` -> concessão -> B "Control: you",
   botão oculto; A "Control: partner" + botão. Capturas correspondem ao log.
2. O rótulo russo do botão era cortado pela borda da tela com largura 470/botão 185; em
   600/260 cabe.
3. Cancelar: B `@open research` -> diálogo -> `@cancelwait` -> "waiting for baton cancelled,
   closing UIChooseResearch", pilha volta a UIFacilityGrid. A solicitação continua enviada; quando
   A sai do Geoscape, B ainda recebe o bastão.
4. Launch.log mostra os rótulos russos como texto com codificação incorreta (codificação do log); a tela está correta.

5. O painel também fica visível no Geoscape (UIAvengerHUD continua na tela ali),
   então o portador no Geoscape vê "Partner asks for control".

## <a id="session-1-cont--request-replies-empty-frames-a-client-crash"></a>Sessão 1 (cont.) — respostas a solicitações, quadros vazios, falha do cliente

Respostas a solicitações: o portador responde a uma solicitação adiada com "CoopBatonDeferred" (o
solicitante mostra "Partner is busy - control comes once they leave their screen", sem
tempo limite); um não portador responde "CoopBatonNotMine" (botão do solicitante reativado).
Sem resposta alguma, a solicitação expira após 10 s (`CheckRequestTimeout`, executado pelo
painel). Textos longos recebem fundo de painel de duas linhas (70 px), curtos 40 px.

Quadros vazios: quadros sem objetos ("Entered Facility" do jogo, `@emptyframe` do
aparato de testes) não são mais enviados. SendMergeGameState os recusa ("Failed to send game
state for merging! GameState has 0 Objects!"), enquanto nosso comando CoopFrame ainda saía:
essa era a causa de haver mais comandos CoopFrame que estados de mesclagem, observada antes.

### <a id="observed-6"></a>Observado
1. Teste "baton-replies-2": B `@ask` -> "CoopBatonDeferred" -> texto de ocupado, sem mudança após
   16 s; A sai do Geoscape -> concessão -> B "Control: you". B `@nobaton` + `@ask` -> A
   "CoopBatonNotMine" -> botão de B reativado. Nenhuma linha "0 Objects" após a correção.
2. Teste "baton-replies" (primeira versão): um testador clicou nas duas janelas durante a execução
   (entrou em instalações, abriu o Armory, pressionou Cancel, pressionou "Ask for control"
   várias vezes): 5 passagens de ida e volta, todas com impressões digitais iguais; o bloqueio de edição
   e Cancel funcionaram com cliques reais do mouse.
3. Nessa execução, B falhou 0,2 s após um `@nobaton` do aparato de testes, dentro de uma instalação
   (cliques do testador): violação de acesso lendo 0xffffffffffffffff em tbbmalloc.dll+0x29c9.
   A inspeção da pilha (ferramentas `minidump_info.py`, `re_func_strings.py`, heurística) mostra
   UWorld::Tick e uma função de UnLinker.cpp (carregamento de pacote) acima do alocador. Nenhuma
   pilha de chamadas de script no log. RAM 32 GB, 13 GB livres.
4. Dez quadros vazios seguidos (teste "empty-frames", antes da correção) não causaram falha.

### <a id="unknown-2"></a>Em aberto
- Causa da falha do item 3. Carregamento de pacote pelo motor durante uma visita a instalação é a
  melhor pista; não reproduzida. Observar nas próximas execuções; uma execução que entra em instalações
  no cliente enquanto quadros chegam seria a próxima tentativa de reprodução.

### <a id="unknown--next-7"></a>Em aberto / próximos passos
- Uma solicitação sem resposta expira após 10 s; uma adiada nunca expira.
## <a id="session-1-cont--test-suite"></a>Sessão 1 (cont.) — suíte de testes

`tools/test_suite.ps1` no repositório do mod transforma as execuções acima em cinco cenários com
asserções nos dois logs (linhas esperadas; sem DESYNC, falha, ID duplicado de tripulante, sala desatualizada,
tempo limite do bot; impressões digitais finais iguais). Primeira execução: FAIL falso, a palavra proibida "STALE"
correspondia a "MaxStaleCacheSize" do motor (Select-String não diferencia maiúsculas de minúsculas por padrão);
agora "STALE loaded=" com diferenciação. Segunda execução em 2026-10-25: 5/5 passaram.

## <a id="session-2--2026-10-25-geoscape-clock-lost-frames-batching"></a>Sessão 2 — 2026-10-25: relógio do Geoscape, quadros perdidos, envio em lotes

Aparato de testes: `@time` (relógio no histórico / X2StrategyGameRuleset.GameTime / XGGeoscape.m_kDateTime,
datas de conclusão dos projetos de pesquisa), `@research <TechTemplate>` (XComHQ.SetNewResearchProject,
o que UIChooseResearch faz), `@geoscape`, `@scan` (XGGeoscape.FastForward), `@pause`,
`@burst N` (N quadros em um tick, +1 suprimento cada).

### <a id="observed-7"></a>Observado
1. O relógio estratégico vive na memória (`STRATEGYRULES.GameTime`, `XGGeoscape.m_kDateTime`);
   a cópia no histórico (`XComGameState_GameTime.CurrentTime`) é gravada por `XGGeoscape.Pause`
   ("Geoscape Pause") e alguns outros quadros.
2. Teste "clock": A pesquisou AlienBiotech e varreu por 20 s (3-1 -> 3-5, pesquisa concluída).
   O histórico de B recebeu 3-5, seu relógio na memória permaneceu na hora de entrada (3-1). B pegou o bastão,
   entrou no Geoscape: seu relógio avançou de 3-1; após uma varredura e pausa (3-3), o estado de mesclagem
   fez o relógio do HISTÓRICO de A voltar de 3-5 para 3-3. Impressões digitais disseram "in sync" (não incluíam tempo).
3. Correção: ao receber estado de mesclagem com objeto GameTime, copiá-lo para o relógio na memória e
   `XComEarth.SetTime` (`CoopSession.ApplyClock`); antes de uma concessão, o portador grava seu relógio na memória
   no histórico se diferir (`CommitClock`); a impressão digital começa pelo relógio do histórico
   com precisão de hora. Teste "clock-2": relógio de B na memória acompanhou até 3-5, B continuou 3-5 -> 3-7,
   A recebeu 3-7; ambos terminam com impressões digitais iguais, incluindo a hora.
4. Teste "burst-2" (um quadro por SendMergeGameState): B enviou 10 + 20 quadros em dois ticks, A recebeu
   3 callbacks de mesclagem; A terminou com 4021 suprimentos, B com 4030. Quadros se perderam na camada
   de rede (o remetente registrou todos os 30 "Wrote new game state frame to network queue"). A verificação
   de concessão recusou o bastão (impressões digitais diferentes): sem corrupção silenciosa, mas um impasse.
   (Primeira execução "burst": 6 rajadas de até 20 em cada direção chegaram atrasadas, mas completas; a perda não é
   determinística.)
5. Correção: envio em lotes. OnNewGameState só registra os ObjectIDs tocados por um quadro; 0,2 s depois
   (`CoopFlushTimer`, e imediatamente antes de uma concessão), um estado de mesclagem é construído com
   ModifyStateObject (ou RemoveStateObject) da versão mais recente de cada objeto tocado, enviado
   e descartado com CleanupPendingGameState (nunca submetido); uma impressão digital CoopFrame por
   lote, comparada em ordem no receptor (um callback de mesclagem por lote). Teste "burst-3":
   rajadas de 10/20/50 em ambas as direções -> 6 lotes, ambos os lados com 4160 suprimentos, tudo "in sync".
6. Nova falha do cliente (teste "clock", B 2 s após sair do Geoscape como portador, 3 quadros "Geoscape
   Pause" em um tick): Launch.log tem uma pilha nativa; falha em XCom2.exe+0x4ce235 lendo
   null+0xe0, em uma thread de trabalho cuja função de tarefa referencia a string
   "FWriteHistoryObjects" (serialização de objetos do histórico). Junto da falha anterior (também logo
   após uma rajada no cliente), aponta para uma corrida na serialização em segundo plano de estados
   de mesclagem na camada de rede. Rajadas de até 20 quadros sem agrupamento (teste "burst") e 50
   em lotes ("burst-3") não falharam; sem reprodução sob demanda. O envio em lotes manda muito menos estados de mesclagem, o que também deve
   tornar essa corrida mais rara; não verificado.

### <a id="unknown--next-8"></a>Em aberto / próximos passos
- Se o envio em lotes elimina a falha (observar a suíte e execuções mais longas).
- Estados de mesclagem construídos de cópias: testados para recursos do HQ, pesquisa, instalações (suíte); não para
  todos os tipos de objeto.

## <a id="session-2-cont--the-client-crash-client-sends-while-it-saves"></a>Sessão 2 (cont.) — a falha do cliente: o cliente envia enquanto salva

Aparato de testes: `@autosave` (XComAutosaveMgr.DoAutosave, o que BaseRoomView.BeginState faz quando a
câmera volta do Geoscape para o Avenger).

### <a id="observed-8"></a>Observado
1. Execução da suíte com "clock": B falhou novamente no mesmo endereço de antes (XCom2.exe+0x4ce235,
   lendo null+0xe0, thread de trabalho, tarefa "FWriteHistoryObjects"), 1,4 s após sair do
   Geoscape, sem envio de estado de mesclagem no intervalo. Sair do Geoscape faz um salvamento automático.
2. Teste "autosave": B sem bastão fez 10 salvamentos automáticos (quadros só locais): sem falha.
3. Teste "autosave-burst": B com bastão, `@autosave`, depois `@burst 5` 0,05 s mais tarde: falha no
   primeiro salvamento automático (a rajada saiu como lote enquanto o salvamento ocorria).
4. Teste "autosave-burst-2": A (anfitrião, bastão), salvamento automático + rajada + lote 6 vezes: sem falha.
   B sem bastão, salvamento automático + rajadas locais 6 vezes: sem falha.
5. Teste "client-send-then-save": B pega o bastão e faz salvamento automático: falha no primeiro salvamento (os
   quadros criados pelo próprio salvamento são agrupados e enviados 0,2 s depois, durante o salvamento).
6. Correção: `CoopAutosaveMgr` (ModClassOverrides de XComAutosaveMgr): sem salvamento automático / rápido no
   cliente cooperativo (`HasClientConnection`); FlushBatch espera enquanto `XComOnlineEventMgr.SaveInProgress()`
   e uma concessão também espera o salvamento. Teste "client-send-then-save-2": 6 salvamentos automáticos do cliente
   pulados, anfitrião salvou enquanto enviava, sem falha, estado final igual.

### <a id="derived-5"></a>Derivado
- Condição da falha: o CLIENTE envia estado de mesclagem enquanto salva. Nativa, impossível corrigir por
  script; evitada. Só o anfitrião salva a campanha compartilhada (já era o plano).

### <a id="unknown-3"></a>Em aberto
- Causa nativa exata (por que o cliente e não o anfitrião).
- Menu de salvamento no cliente (tela manual "Save game") ainda não bloqueado.

## <a id="session-2-cont--the-writer-task-and-a-host-crash"></a>Sessão 2 (cont.) — a tarefa de gravação e uma falha do anfitrião

Ferramentas (espaço de trabalho): `re_xrefs.py` (referências vtable / lea para uma função), `re_calls.py`
(chamadores diretos + suas strings). Aparato de testes: `@netwatch S` (registra as filas
OutGameData/InGameData do gerenciador de rede quando mudam), `@pendingstress N` (N estados pendentes criados
e descartados, como FlushBatch, sem rede).

### <a id="observed-9"></a>Observado
1. Suíte (8 cenários), 2026-10-25 01:58: 7/8; `clock` e o novo `client-save` passaram; em
   `baton-objects`, o ANFITRIÃO falhou pela primeira vez, mesmo endereço (XCom2.exe+0x4ce235,
   null+0xe0), 0,01 s após receber um estado de mesclagem e 2,1 s após seu último lote + concessão.
   Não estava salvando (seu último salvamento automático era do cenário anterior).
2. Desmontagem: 0x4ce230 é uma busca TMap por ObjectID; o chamador (0xcb6930) passa
   `frame + 0x9c`, onde `frame` vem do array de quadros do histórico, e esse ponteiro de quadro
   era nulo (falha em 0x9c + 0x44 = 0xe0). O processo de trabalho lê uma posição vazia de quadro do histórico.
3. A tarefa "FWriteHistoryObjects" (vtable 0x14175c440) é criada por: rotina de salvamento
   (0xbbc340, strings "Save0", "open Avenger_Root..."), salvamento pós-jogo do modo desafio e
   0xce2c60, chamado por UXComGameStateNetworkManager::SendGameState e (por
   0xce2db0) SendMergeGameState e SendValidateGameState. Receber não a cria
   (nenhum chamador nativo encontrado).
4. `@netwatch`: OutGameData/InGameData sempre estavam vazias nas amostras a cada 0,05 s.
5. Teste "pending-stress" (uma instância, sem rede): 10 salvamentos automáticos, cada um seguido de 20 estados
   pendentes criados e descartados: sem falha.
6. Teste "send-race": 30 lotes por lado, cada um seguido 0,22 s depois por 30 quadros locais enquanto
   a tarefa de envio talvez ainda rodasse: sem falha, tudo "in sync", ambos terminam com 4990 suprimentos.

### <a id="derived-6"></a>Derivado
- Falhas do cliente envolvendo salvamento estão cobertas por CoopAutosaveMgr (5 das 6 falhas até agora
  ocorreram no cliente logo após ou durante um salvamento).
- A falha do anfitrião segue sem explicação: uma ocorrência em cerca de 45 execuções de cenário. Uma tarefa de envio
  lendo uma posição de quadro do histórico enquanto está vazia é a melhor descrição; o que a esvazia é
  desconhecido (candidatos: estados de mesclagem gravados no quadro atual do receptor, o
  estado pendente descartado do lote).

### <a id="next"></a>Próximo passo
- Medir a frequência (repetir a suíte) antes de mais engenharia reversa.

## <a id="session-2-cont--manual-saves-on-the-client"></a>Sessão 2 (cont.) — salvamentos manuais no cliente

### <a id="observed-10"></a>Observado
- UIPauseMenu constrói seu item Save em InitScreen (índice `m_optSave`, -1 quando salvar não é
  permitido); OnChildClicked abre a tela de salvamento por `Movie.Pres.UISaveScreen()` sem
  verificar se o item da lista está desativado (o caso do tutorial verifica novamente à mão).
- Novo listener CoopSaveGate: no cliente cooperativo, desativa o item Save com o motivo
  "In co-op only the host saves the campaign" e fecha UISaveGame se abrir mesmo assim.
- Teste "client-save-menu": B (cliente) registra "pause menu: save disabled on co-op client", depois
  `@savescreen` (a chamada do item do menu) registra "save screen closed" e a pilha volta a
  UIPauseMenu; A (anfitrião) abre seu menu de pausa com Save intacto. PASS em 2026-10-25.

## <a id="session-2-cont--repeated-suite-runs"></a>Sessão 2 (cont.) — execuções repetidas da suíte

### <a id="observed-11"></a>Observado
- Suíte completa (9 cenários) três vezes seguidas em 2026-10-25: 7/9, 9/9, 8/9.
- Falha do anfitrião "FWriteHistoryObjects" (XCom2.exe+0x4ce235 lendo null+0xe0) mais uma vez, novamente em
  `baton-objects` (rodada 1). Ambas as falhas do anfitrião até agora ocorreram nesse cenário.
- Duas outras falhas (`clock` rodada 1, `client-save` rodada 3) eram defeito da bancada de testes: o
  Launch.log do anfitrião parou em 0,51 s ("Loading value for StaleCacheDays"), antes de qualquer código
  do mod rodar; o cliente esperou o histórico, atingiu o tempo limite e uma asserção de UnAsyncLoading.cpp
  ao ser encerrado. 2 de 27 inicializações do par.
- run_pair_test.ps1 agora reinicia as duas instâncias quando uma delas não registrou
  "CoopHarness: ready" em 60 s (até 3 tentativas); test_suite.ps1 mantém os dois logs de um
  cenário com falha em `<workspace>\suite-failures\`.

### <a id="next-1"></a>Próximo passo
- `baton-objects` dez vezes seguidas para capturar a falha do anfitrião com seus logs.

## <a id="session-2-cont--the-host-crash-explained-merged-versions-name-the-senders-frames"></a>Sessão 2 (cont.) — a falha do anfitrião explicada: versões mescladas apontam para quadros do remetente

### <a id="observed-12"></a>Observado
- `baton-objects` isolado: falha do anfitrião em 3 das primeiras 4 execuções, depois 1 de 4 (5 de 11 contando
  as rodadas da suíte). Sempre 0,01 s após o anfitrião receber o lote do cliente contendo o
  novo Engineer e o HQ.
- Os minidumps contêm o heap do processo. Com a tabela de nomes (array de FNameEntry*, encontrado por
  um ponteiro para uma entrada conhecida; entrada = 8 bytes de sinalizadores, int Index<<1, 8 bytes de elo de hash, caracteres
  ANSI) e o layout de UObject desta build (Outer +0x40, Name +0x48, Class +0x50), os
  ponteiros UFunction na pilha da thread que falhou identificam a pilha de script:
  XGGeoscape.Tick > UpdateUIVisualsOnly > XComStrategyMap.UpdateVisuals > UpdateMapItemVisuals
  > UIStrategyMapItem.UpdateVisuals > UpdateFromGeoscapeEntity (em UIStrategyMapItem_Avenger_0)
  > XComGameStateHistory.GetGameStateForObjectID. A falha era na thread principal, não em uma de trabalho.
  Ferramentas: `tools/mdmem.py`, `tools/md_uobj.py`, `tools/minidump_threads.py`, `tools/re_natives.py`
  (tabela de funções exec: pares {string "UClassexecName", função} nos dados).
- UpdateFromGeoscapeEntity busca a entidade (o Avenger = XComHQ) no estado de
  `HistoryIndexOnLastUpdate`, um quadro mais antigo, então o histórico percorre as versões para trás.
- XComGameState_BaseObject tem `private int PreviousHistoryFrameIndex` ("linked list to the
  history frame of the direct ancestor"). Registrado no recebimento: o pai de uma versão mesclada é o
  quadro atual do receptor, sua versão anterior é "none" de um lado, e chamar
  GetPreviousVersion nela fez o anfitrião falhar da mesma forma (2 de 2 execuções).
- Contagens de quadros na falha: o lote do cliente saiu em seu quadro atual 231 (o HQ
  mudou nos últimos quadros); o último quadro do anfitrião era 229. No experimento SendGameState:
  cliente atual 230, último quadro do anfitrião 228, falha de novo. O valor do campo privado
  em si não foi lido (desconhecido); que ultrapassa o último quadro do anfitrião é inferência.
- Experimento SendGameState + SubmitGameState do estado recebido no receptor: o estado
  chega com HistoryIndex -1 e fora do histórico; submetê-lo adiciona um quadro, mas as
  versões continuam sem versão anterior, o contador de ObjectID do receptor não avança
  (o cliente depois criou uma segunda unidade com o mesmo ID 2327) e o anfitrião ainda falhou.
  Abandonado.

### <a id="derived-7"></a>Derivado
- Uma versão de objeto mesclada mantém o PreviousHistoryFrameIndex do remetente. O receptor aplica
  a mesclagem ao seu quadro atual, e sua contagem de quadros difere (mesclagens não adicionam quadros; o
  jogador sem bastão produz quadros locais), então o índice aponta para um quadro sem relação
  (busca retorna none ou uma versão errada) ou além do fim (posição vazia: falha). Isso também
  explica as falhas do cliente no gravador de salvamento ("FWriteHistoryObjects"), que percorre os
  mesmos elos.

### <a id="fix"></a>Correção
- `@walkback N` do aparato de testes: busca HQ e tripulação no estado de cada um dos últimos N quadros (o que o
  item do mapa do Avenger faz).
- Primeira tentativa: antes de cada mesclagem, o remetente envia "CoopAlign <its current frame>" e o
  receptor submete quadros vazios ("Coop: align history") até que esse seja seu quadro atual, para
  a mesclagem cair no número de quadro do remetente. Sem falha em 3 execuções, mas ambas as instâncias travaram
  (log para; uma vez no `@walkback` do receptor, outra 0,02 s após uma mesclagem): uma versão tirada
  do quadro atual do remetente aponta para esse quadro como o anterior, e colocá-la no
  mesmo quadro faz com que aponte para si própria (derivado: percurso infinito).
- Agora: remetente envia seu quadro atual + 1, mesclagem cai logo após cada quadro ao qual suas
  versões podem apontar, então um quadro referenciado sempre é anterior ao quadro da própria versão e
  nunca fica além do fim. Comandos são tratados antes de uma mesclagem enviada depois deles ("CoopAlign" registrado
  antes de "received merge state" em toda execução). `baton-objects` 6 de 6 PASS em 2026-10-25,
  `@walkback 20` respondeu dos dois lados (found=529 e 543 buscas).
- Não se sabe: o que uma busca retorna quando o quadro referenciado não contém versão do objeto (uma
  observação: GetPreviousVersion deu none), e se salvamentos gravados após mesclagens carregam
  de volta a mesma campanha (a testar).
## <a id="session-3--host-saves-after-merges-and-version-chains"></a>Sessão 3 — salvamentos do anfitrião após mesclagens e cadeias de versões

Aparato de testes: `@save` (nova posição de salvamento, registra seu número), `@load N` (por ID do salvamento, como UILoadGame),
`@verchain` (segue GetPreviousVersion a partir da versão atual do HQ e de cada
tripulante e conta os quadros que contêm uma versão; "short" = a cadeia termina cedo, "bad" = um
elo que não retrocede no tempo), `@localburst N` (quadros que não são agrupados em lotes),
`@sendvar K` (quatro formas de enviar o HQ como estado de mesclagem).

### <a id="observed-13"></a>Observado
1. Execução em par: B (cliente) pegou o bastão e enviou dois lotes (Engineer + 9 ligas, depois 10
   quadros); A (anfitrião) estava "in sync" após cada um e salvou na posição 61 (`save done ok=true`).
2. Uma instância, carregar posição 61: impressão digital após carregar = a do momento do salvamento
   (sup4010, all1009, crew27#2321), tripulação igual (Scientist 2320 e Engineer
   2321 do cliente presentes, duplicateIDs=0). Quadros 242 -> 250 após carregar. Depois Geoscape, varredura
   (relógio até 2035-3-6, histórico = conjunto de regras = Geoscape), 3 quadros, salvar na posição 62: ok, sem falha.
3. `@verchain`: sem rede (nova campanha, rajadas, estados pendentes criados e descartados),
   toda cadeia está completa (176/176, 181/181). Pela rede, a cadeia do HQ foi cortada dos DOIS
   lados, também no remetente, logo após sair o lote do próprio remetente (A: 176/176 antes
   de enviar, HQ chain=1 depois, terminando em seu próprio último quadro local).
4. `@sendvar` no anfitrião (cada um seguido de um quadro local não enviado e `@verchain`):
   estado pendente descartado sem enviar: cadeia intacta; estado pendente enviado e não
   descartado: cortada; estado pendente enviado e descartado (FlushBatch): cortada; um quadro submetido
   enviado com SendMergeGameState: intacta.
5. Nesse experimento, nenhum "CoopAlign" foi enviado; B então falhou em `@verchain` no endereço
   conhecido (XCom2.exe+0x4ce235, null+0xe0): um elo além do fim de seu histórico.
6. Correção: FlushBatch submete o lote como quadro próprio ("Coop batch", não agrupado novamente) e
   envia esse quadro; "CoopAlign" transporta seu índice, então a mesclagem cai no mesmo número de
   quadro no receptor. Nova execução: cadeias do remetente completas após cada envio (A 179/179; as
   próprias versões de B encadeiam para trás através de seus lotes, 4 e depois 7 elos); a cadeia agora só termina em uma
   versão recebida do parceiro (ela aponta para um quadro de preenchimento "Coop: align history" sem
   versão do objeto). `@walkback 20` respondeu, salvamento do anfitrião após mesclagens ok (posição 63).

### <a id="derived-8"></a>Derivado
- SendMergeGameState de um estado fora do histórico limpa o elo de versão anterior
  da versão mais recente no histórico de cada objeto contido nele, no remetente. Nativo; evitado.
- A busca de versão anterior de uma versão recebida retorna none (sem falha) quando o quadro referenciado
  não contém versão; salvamentos mantêm isso e carregam de volta a mesma campanha.

### <a id="unknown-4"></a>Em aberto
- Se o código do jogo precisa da versão anterior de um objeto recebido (por exemplo, código que compara
  estado antigo e novo após uma mesclagem). Script que desreferencia none registra "Accessed None"; ainda não observado.

Suíte completa com o novo FlushBatch e `@verchain` em baton-objects (nenhum "bad=" permitido):
9/9 PASS em 2026-10-25 20:43.

Nota da bancada: executar `bash tools/build_mod.sh` de um job em segundo plano do PowerShell não compilou
(nenhum erro mostrado); compilar pelo Git Bash e conferir o horário de modificação de `.u`.

## <a id="session-3-cont--projects-finishing-on-the-partners-geoscape"></a>Sessão 3 (cont.) — projetos terminando no Geoscape do parceiro

Aparato de testes: `@construct N Template` (XComHQ.AddFacilityProject, o que UIChooseFacility faz ao
confirmar: tempo e custo de construção), `@dismiss` (fecha popups até as telas básicas do Geoscape / Avenger),
`@geoscape` agora só entra quando o mapa não está aberto; `@time` lista cada projeto do HQ
(classe, foco, data de conclusão, pontos) e as contagens de projetos / tecnologias / instalações; `@rooms`
marca uma sala em construção.

### <a id="observed-14"></a>Observado
1. Teste "projects": A (anfitrião, bastão) esvazia a sala 3, inicia um Laboratory (concluído em 20 dias) e
   pesquisa AlienBiotech (4,5 dias), depois concede o bastão. B entra no Geoscape e varre.
   - Os objetos dos projetos, o estado de construção da sala e o custo chegam a B (troca da sala 3
     AVG_ER_A -> AVG_ER_BuildState_A em B; suprimentos 4000 -> 3850 em ambos).
   - A pesquisa terminou em B durante a varredura; A recebeu (techs 21, projeto removido),
     "in sync".
2. Primeira execução: a instalação nunca terminou (tempo passou sua data em um mês, pontos
   inalterados). Causa: `@close` do teste fechou a tela Geoscape de B, depois seu HUD; o tempo ainda
   avançava pelo actor Geoscape. XComGameState_HeadquartersXCom só verifica projetos
   enquanto `Pres.StrategyMap2D != none`, fora de voo e sem UIAlert na pilha.
3. Com `@dismiss` e 12 rodadas de varredura (terceira execução): o Laboratory terminou em B entre
   2035-3-23 e 3-28 (sua data era 3-21; até então, um UIAlert ou a tela de missão de instalação
   alienígena estava aberta em quase toda verificação). A trocou a sala 3 de AVG_ER_BuildState_A para
   AVG_Laboratory_A; ambos terminam com projects=0 techs=21 facilities=19 e impressões digitais iguais,
   35 "in sync", nenhum DESYNC.
4. Popups (pesquisa concluída, instalação concluída, missão de instalação alienígena, outros alertas) aparecem só para
   o jogador que controla o Geoscape; o parceiro vê o resultado pelas mesclagens.
5. Durante uma varredura, o relógio do histórico (XComGameState_GameTime) fica atrás do relógio do conjunto de regras / Geoscape
   e se atualiza em eventos e na pausa; o relógio do parceiro acompanha a cópia do histórico.

### <a id="derived-9"></a>Derivado
- Projetos iniciados por um jogador terminam no Geoscape do outro; o resultado e a troca de
  sala chegam a quem iniciou. Nenhuma alteração do mod necessária para isso.

### <a id="unknown-5"></a>Em aberto
- Se uma instalação também termina dois dias atrasada no modo de um jogador quando popups ficam abertos
  (não comparado).
- O parceiro não recebe popup de eventos ocorridos do outro lado (questão de projeto:
  mostrar um resumo?).

## <a id="session-3-cont--a-lost-merge-one-merge-in-flight"></a>Sessão 3 (cont.) — uma mesclagem perdida, uma mesclagem em trânsito

### <a id="observed-15"></a>Observado
1. Suíte 2026-10-25 21:51: 7/10. `projects` falhou com DESYNC em A: B enviou dois lotes separados por
   0,23 s (log de B 219.49 e 219.72); A tratou os dois comandos "CoopAlign" (quadros 281 e 283),
   mas recebeu UM callback de mesclagem; o primeiro lote (1 objeto) se perdeu. A fila de impressões digitais
   "CoopFrame" de A ficou então uma posição atrasada, de modo que toda comparação posterior dizia DESYNC. As impressões
   digitais finais só coincidiam porque o objeto perdido foi sobrescrito depois.
2. `edit-gate` e `panel-replies` falharam por temporização: após carregar o mapa espelhado, B tinha um vídeo
   de carregamento (12-15 s) e travamentos da GPU ("Timed out while waiting for GPU"); sua etapa prevista para 15 s depois
   rodou 46-57 s depois, então as etapas das duas instâncias vieram na ordem errada. O mod se comportou
   corretamente para a ordem que ocorreu.

### <a id="fix-1"></a>Correção
- CoopSession: um estado de mesclagem em trânsito. O receptor responde a cada mesclagem com
  "CoopMergeAck"; quadros criados nesse intervalo esperam no lote seguinte; uma mesclagem sem confirmação após
  5 s é enviada de novo (seus objetos são readicionados). A impressão digital viaja em "CoopAlign" e é
  comparada uma vez após a próxima mesclagem ("CoopFrame" e sua fila foram removidos), então uma mesclagem perdida
  não pode deslocar as verificações posteriores.
- Aparato de testes: `@waitnobaton`, `@waitgrantreq`; `edit-gate` e `panel-replies` esperam essas
  condições (A mantém o Geoscape até a solicitação de B ser adiada) em vez de atrasos fixos.
- Suíte 2026-10-25 22:33: 10/10 PASS (com o novo cenário `projects`). Nenhum reenvio
  "not acknowledged" nos logs do último cenário (os dos demais foram sobrescritos; desconhecido).

## <a id="session-3-cont--client-drops-and-rejoins"></a>Sessão 3 (cont.) — cliente desconecta e retorna

Ferramentas: `tools/run_rejoin_test.ps1` do repositório do mod (A e B iniciam como de costume; quando B registra "done", seu
processo é encerrado à força, sem desconexão limpa; depois um novo processo B inicia sozinho com outras etapas:
A já não mantém o mutex de instância única). Aparato de testes: `@waitjoins N` (N-ésimo PlayerJoined),
`@waitclosed N` (N-ésimo ConnectionClosed). A suíte executa dessa forma um cenário com etapas `B2`.

### <a id="observed-16"></a>Observado
1. Teste "rejoin-explore" (antes da correção): A concedeu o bastão, B criou um Engineer (mesclado,
   "in sync") e foi encerrado com o bastão. A registrou ConnectionClosed cerca de 3 s depois.
   A então ficou sem bastão (painel "partner has control"); ninguém podia mudar a campanha.
2. O novo processo B conectou, A enviou o histórico novamente (`MPSendHistory`), B entrou no
   Avenger como espelho com 234 quadros: o Engineer que criou antes de morrer estava ali, tripulação
   igual, duplicateIDs=0.
3. A mudança de A após o retorno (+5 suprimentos) era "local frame without baton" e nunca foi
   enviada: A terminou com 4005 suprimentos, B com 4000.
4. Correção: CoopSession.OnConnectionClosed descarta tudo em trânsito (concessão pendente, mesclagem em
   trânsito, lote) e o anfitrião retoma o bastão. O lado que entrou na campanha como
   espelho (`bMirrorClient`, definido por CoopHeadquartersGame) é o cliente: ele só registra que
   o anfitrião saiu e não mantém bastão.
5. Teste "rejoin-1" / suíte "rejoin": A registra "connection closed: the partner left; the host
   takes the baton back (had it: no)", painel "you have control"; após o retorno de B, os +5
   suprimentos de A chegam a B ("in sync"); A concede (época 2) ao novo processo B, as +3 ligas de B
   chegam a A ("in sync"); ambos terminam com 236 quadros, impressões digitais iguais, duplicateIDs=0,
   verchain bad=0.

### <a id="unknown-6"></a>Em aberto
- O anfitrião morrer enquanto o cliente joga (só existe a linha de log no cliente).
- A entrada ainda é conduzida pelo bot de teste (anfitrião `MPSendHistory`, cliente `@mirror`); o jogo real
  precisa de um fluxo de entrada (anfitrião envia histórico quando um cliente entra, uma entrada de menu).
- Quadros criados pelo cliente após seu último lote e antes de morrer são perdidos (por projeto: o
  histórico do anfitrião é a campanha).
- Suíte completa com `rejoin` em 2026-10-25 23:35: 11/11 PASS.
