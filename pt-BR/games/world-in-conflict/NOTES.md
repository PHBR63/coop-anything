# <a id="world-in-conflict--soviet-assault-co-op-campaign-notes"></a>World in Conflict (+ Soviet Assault): notas de campanha cooperativa

Sessão 1, 2026-10-17. Objetivo: jogar campanhas WiC / Soviet Assault em cooperativo, idealmente com forças próprias por jogador; compartilhar o controle do jogador 1 é a alternativa.

## <a id="identity-rule-5"></a>Identidade (regra 5)

| | |
|---|---|
| Loja | Steam: app 21760 (WiC, buildid 11300) + app 21910 (Soviet Assault, buildid 15036), mesma pasta |
| Versão | 1.0.1.1 (b35), informações PE dos três executáveis |
| Motor | Masstech (Massive Entertainment), Python 2.5 incorporado estaticamente (assinatura pyc `6d f2 0d 0a`) |
| Sistema / arquitetura | Windows, x86 (PE32) |
| SHA-256 wic.exe | `7e15107e5cec5d66ca2f0a90da94a19a8a893308f5377adee97db1467ff0f5e9` |
| SHA-256 wic_online.exe | `433b406ecc3b92def045c3a8af6cd873b86592ad0937fdbbf33bb5b8de74823b` |
| SHA-256 wic_ds.exe | `c150494dcd3b59c4afe3cf7580619b4864cd0238a892f350f1efcedfe6ac10cf` |
| DRM | wic.exe e wic_online.exe: SteamStub (seção `.bind`, entrada nela, entropia `.text` 8,00). wic_ds.exe: sem empacotamento (entropia `.text` 6,61) |

## <a id="prior-work-phase-1"></a>Trabalhos anteriores (etapa 1)

- Diretório coop-anything e `games/`: sem entrada (2026-10-17).
- Buscas web ("World in Conflict campaign co-op mod", "... coop campaign mod moddb", "... play campaign with friend"): nenhum mod de campanha cooperativa. Não encontrado, não comprovadamente inexistente. Ainda não pesquisados: fóruns Massgate.org, Discords WiC, expressões russas/alemãs/polonesas, archive.org.
- BriscoeMod lista escaramuças com bots e servidores não dedicados (página ModDB retornou 403, só trecho da busca).
- Ubisoft publicou backend Massgate em GPL-2.0 (https://github.com/ubisoft/massgate, último envio 2018-10-30). Contém `src/MNetwork` (MN_*, incluindo `MN_LoopbackConnection.h`) e `src/MCommon2` (MC_*), bibliotecas também vinculadas ao jogo. Útil para nomear estruturas no binário.
- Existiu Mod Kit / WicEd (Sierra, 2007): https://worthplaying.com/article/2007/12/18/news/47533-world-in-conflict-v1005-level-editormod-sdk-available-now/ . Wiki Fandom diz que Server.py controla lógica SP do mapa e Client.py, câmeras dos objetivos (https://worldinconflict.fandom.com/wiki/Map_and_Mod_Wiki/Before_we_start, apenas trecho da busca; coleta bloqueada).

## <a id="observations-things-seen-in-files--decompiler"></a>Observações (arquivos / descompilador)

1. Arquivos `.sdf` começam com `RYS\n` e contêm fluxos zlib brutos; procurar fluxos `78 da` recupera arquivos. Índice ainda não decodificado (fim do arquivo, nomes não recuperados).
2. Extraídos 480 pyc de wic1/2/3/30/40/45/60/65.sdf (Python 2.5). Pastas de missão: `maps/europe1`, `europe5`, `ustown1`, `usdesert1`, além de MP. Cada mapa SP possui `server.py`, `server_autogen.py`, `client.py`, `mapvars.py`, `allunits.py`.
3. `serverimports.py` encaminha eventos (`OnUnitDestroyed`, `OnZoneTaken`, `OnPlayerConnected`, `OnPlayerLeave`, `OnPlayerAction`, ...) ao sistema de reações; cada manipulador verifica primeiro `wicg.IsSinglePlayer()`.
4. Scripts usam um único `PLAYER_HUMAN` (107 arquivos, como `thePlayers[PLAYER_HUMAN]`, `GetCameraPosition(PLAYER_HUMAN)`, `APLimitTest`, `NrOfPlayerUnitsTest`).
5. 19 `server.py` SP têm ramos `'OnGameStarted:: Singel'` e `'OnGameStarted:: Multi'`, chamando `AddDeploymentZoneToTeam`. Docstring `EnableAutoMoods` de `wicg` informa padrão ligado em multiplayer e desligado no modo individual.
6. Strings da API em wic.exe: `SendPlayerEvent` / `SendPlayerAction`, enviam dados do jogador ao servidor; `IsSinglePlayer`, verifica modo individual; módulo separado `wicp` disponível aos scripts cliente.
7. Classes/arquivos em wic.exe: `EX_SinglePlayerMode`, `EX_MultiPlayerHostMode`, `EX_MultiPlayerJoinMode`, `EXR_Server`, `EXR_Client`, `WICR_ServerFactory`, `WICR_ClientFactory`, `EX_AIPlayer(Container)`, `EX_LANCreateBots_*Handler`, `WICP_SaveGameHandler`, `EXCO_Persistent*`. Ambos têm RTTI `MN_LoopbackConnection` e `MN_FakeUdpStream`.
8. wic_ds.exe contém suporte a missões SP: `mySinglePlayerData`, `myGameModeSinglePlayer`, `myIsSinglePlayerGameFlag`, `SINGLEPLAYER_ROLE`, `SINGLEPLAYER_ROLE_USSR`, `myCommanderAIData->myIsSinglePlayerGame==true`.
9. `FUN_004aefd0` de wic_ds.exe (Ghidra por REA) trata seleção de papel. Recusa papel SP em multiplayer e papel não SP em partidas individuais, salvo indicador global em `+4` do objeto de `FUN_0045c3b0`. Limites por equipe vêm do servidor (`NumAllowedPlayersPerRole` em wic_ds.ini, padrão 4).
10. Host LAN suporta bots IA (`MultiplayerLANCreateBots_{None,Even,PvsB,Advanced}`, `[BotMode_*]` no wic_ds).

## <a id="derived-reasoning-from-observations-not-yet-tested"></a>Deduções (das observações, ainda não testadas)

- Modo individual provavelmente executa servidor/cliente normais num processo por loopback (itens 3, 6, 7, 8, 9). Assim, campanha já seria um jogo em rede de um cliente; cooperativo exigiria principalmente aceitar outro cliente remoto.
- Missão usa Python servidor; câmeras/cenas, Python cliente acionado por `ClientCommand`. Scripts podem ser substituídos por reempacotamento `.sdf` ou pastas de mods; corrigir missões (vários `PLAYER_HUMAN`, objetivos, AP) seria principalmente Python, não nativo.
- Ramos `Multi` indicam que Massive executou mapas de campanha em MP durante desenvolvimento.

## <a id="unknowns"></a>Desconhecidos

- Se SP cliente realmente usa `EXR_Server` + loopback (executável criptografado por DRM; verificar em execução por DLL/logs, não desempacotar).
- Se wic_ds.exe (ou host de jogador) carrega mapa SP, com qual modo/papel.
- Se `ClientCommand` visa um ou todos os clientes (cenas, mensagens, câmeras).
- Salvamentos no meio da missão cooperativa (`WICP_SaveGameHandler` só cliente; provável ausência inicial).
- Se a simulação é determinística ou estado com autoridade do servidor (modelo DS indica autoridade; não confirmado no código).
- Progresso entre missões (`EXCO_Campaign`, desbloqueios, vídeos) do convidado.

## <a id="session-2-2026-10-17-first-experiments"></a>Sessão 2 (2026-10-17): primeiros experimentos

Ambiente: `<workspace>/coop-anything` (branch `game/world-in-conflict`, privados em `local/`), cópia em `<workspace>/testinstall` (hashes dos executáveis iguais aos originais). Só `wic_ds.ini` da cópia (5 valores: GameName, MapCycleFile, RandomMapCycle, MinPlayers=1, MaxPlayers=4; original em `wic_ds.ini.orig`) e novo `coop_cycle.txt` alterados. Executor: `local/tools/run_ds.ps1` (inicia wic_ds.exe copiado minimizado, encerra após N segundos, move logs a `local/<tag>/`).

Efeito colateral: wic_ds.exe escreve em `%USERPROFILE%\Documents\World in Conflict\debug\`, criando a pasta, antes inexistente. O executor remove dela os novos logs.

### <a id="observed"></a>Observado

- E1, ciclo `europe2`: servidor iniciou, TCP 48000 + 52999 (VOIP), UDP 48000; listou 31 mapas (`LoadMissions()`), ignorou `europe2`, carregou primeiro `maps/usdesert2/usdesert2.ice`, executou InitMission, criou IAs e zonas de implantação.
- E2, ciclo `do_Riviera`: carregou `maps/europe4/europe4.ice`.
- E3, ciclo `maps/europe2/europe2.ice` + `Europe2`: ignorado, carregou `usdesert2` novamente.
- Campanhas (tabela textual `myCampaigns.<cmp>.myItems.MissionN-<Map>` em `wicloc61.sdf`): WiC `cmp1`: Seattle2, Seattle3, Ustown4, Usfarmland3, Ustown3, Europe4, Europe2, Russia2, Russia4, Newyork1, Usfarmland2, Ustown1, Seattle4, Seattle1. Soviet Assault `WIC_SA`: Berlin1, Seattle2, Seattle3, UsFarmland1, Ustown4, Usfarmland3, UsFarmland5, Ustown3, Europe4, Europe2, Norway1, Russia2, Russia4, Russia3, Newyork1, Usfarmland2, Ustown1, UsFarmland4, Seattle4, Seattle1.
- `FUN_004a7f30` de wic_ds verifica `myIsSinglePlayerGameFlag` (EXG_Game.cpp, linha 0xda2) no byte `EXG_Game+4`; `FUN_004aefd0` lê o mesmo. Classe compartilhada SP/MP, modo é um indicador nela.

- E4, execução de 12 s por nome original de ciclo (`local/mp_map_folders.tsv`), nome MP -> pasta:

  | Nome MP | Pasta | Missão(ões) de campanha |
  |---|---|---|
  | do_Hometown | ustown1 | WiC 12, SA 17 |
  | do_Xmas | ustown3 | WiC 5, SA 8 |
  | do_Seaside | ustown4 | WiC 3, SA 5 |
  | do_SpaceNeedle | seattle1 | WiC 14, SA 20 |
  | as_Dome | seattle2 | WiC 1, SA 2 |
  | as_Bridge | seattle3 | WiC 2, SA 3 |
  | do_Island | seattle4 | WiC 13, SA 19 |
  | do_Liberty | newyork1 | WiC 10, SA 15 |
  | do_Farmland | usfarmland1 | SA 4 |
  | tw_Wasteland | usfarmland2 | WiC 11, SA 16 |
  | do_Riverbed | usfarmland3 | WiC 4, SA 6 |
  | tw_Highway | usfarmland4 | SA 18 |
  | do_Silo | usdesert1 | - |
  | as_AirBase | usdesert2 | - |
  | do_Ruins | europe1 | - |
  | as_Hillside | europe2 | WiC 7, SA 10 |
  | do_Riviera | europe4 | WiC 6, SA 9 |
  | tw_Radar | russia1 | - |
  | do_Powerplant | russia2 | WiC 8, SA 12 |
  | do_Quarry | russia3 | SA 14 |
  | as_Typhoon | russia4 | WiC 9, SA 13 |
  | do_Apocalypse / do_Tequila / do_Studio | próprias | - |

  Sem equivalente MP: usfarmland5 (SA 7), berlin1 (SA 1), norway1 (SA 11). Pastas ainda aparecem em `LoadMissions()`.

### <a id="derived"></a>Deduções

- Missões e mapas MP compartilham pastas: `do_Riviera` é `europe4`, missão 6 da campanha. Um `.ice` contém modos MP e `mySinglePlayerData`, explicando ramos `OnGameStarted:: Singel` e `:: Multi`.
- Ciclo DS usa nomes de exibição MP, não pastas. Não seleciona modo SP por configuração; precisa definir indicador SP em `EXG_Game` (hook nativo) ou usar modo host do cliente.

- E5, usuário na missão 1 de WiC (Steam, iniciada pelo Steam), sockets de `wic.exe` lidos externamente por `Get-NetTCPConnection` / `Get-NetUDPEndpoint`: nenhum TCP, um UDP em `0.0.0.0:<ephemeral>`. Servidor dedicado escuta TCP/UDP 48000.

### <a id="derived-1"></a>Deduções

- Modo individual não coloca servidor atrás de socket real. Com RTTI `MN_LoopbackConnection`, o provável é servidor/cliente num processo por conexão em memória. Cooperativo exige trabalho nativo: host SP aceitar cliente real como `EX_MultiPlayerHostMode`, ou missão SP dentro do host MP com indicador SP. Só configuração não basta.
- Finalidade do único UDP desconhecida (busca LAN ou VOIP são hipóteses).

### <a id="still-open"></a>Ainda em aberto

- Índice SDF (nomes de todos os fluxos) não decodificado; busca por varredura.
- Compatibilidade GOG/Steam desconhecida. Conferir versão/hash GOG e tentar LAN original por VPN.

## <a id="networking-plan-owner-preference"></a>Plano de rede (preferência do usuário)

O usuário usou Steam "Spacewar" (AppID 480) antes (`playbook/networking-steam-spacewar.md`). Para WiC, retransmissor separado como `HXCoop.exe` é melhor que carregar `steam_api.dll`: `wic.exe` já é aplicativo Steam (21760) com SteamStub; outro AppID no mesmo processo é arriscado. Um retransmissor pode ser Spacewar e encaminhar UDP/TCP a localhost. Também funciona sem alterações com um jogador GOG.

## <a id="sources"></a>Fontes

- https://github.com/cranebeaker/coop-anything (guias)
- https://github.com/ubisoft/massgate
- https://en.wikipedia.org/wiki/World_in_Conflict
- https://worldinconflict.fandom.com/wiki/Map_and_Mod_Wiki/Before_we_start

## <a id="session-3-2026-10-17-gog-complete-edition-vs-steam"></a>Sessão 3 (2026-10-17): GOG Complete Edition versus Steam

Instalação GOG Galaxy de "World in Conflict: Complete Edition" (ID 1438332414, versão informada 2.0.0.3).

| Arquivo | SHA-256 |
|---|---|
| GOG wic.exe | `41017f352cabd5fb3dc2b4457727c6e32678fdbdd89e881b11a8868edba18ebc` |
| GOG wic_online.exe | `7bb41478f3070641b7639707d72a976a2ae5c8f9ad9356ff5733610979c0b7d0` |
| GOG wic_ds.exe | `c150494dcd3b59c4afe3cf7580619b4864cd0238a892f350f1efcedfe6ac10cf` (igual ao Steam) |

### <a id="observed-1"></a>Observado

- `wic.exe` / `wic_online.exe` GOG sem `.bind` / `.extra`, `.text` não criptografada (entropia 6,6). Endereços/tamanhos de seções iguais aos do Steam.
- Comparação por seção de `wic.exe`: mesmo timestamp PE (`0x4a2f7509`); `.rdata`, `.data`, `.tls`, `CONST`, `.rsrc` idênticos; só `.text` difere (Steam criptografada), além de seções extras `.extra` / `.bind` e ponto de entrada Steam.
- Todas DLLs comuns e `.sdf` têm hashes iguais, salvo `wicloc46.sdf` e `wicloc61.sdf` (localização/interface). `wic_ds.ini` difere só nos padrões.
- RTTI no GOG `wic.exe` (`local/tools/rtti.py`):
  - `EX_MultiPlayerHostMode` deriva de `EX_SinglePlayerMode` (bases EX_SinglePlayerMode, EX_IPlayMode, EXCO_Persistent<EX_SinglePlayerMode>). `EX_DemoReplayMode` também.
  - `EX_MultiPlayerJoinMode` separado: EX_IPlayMode, `EXR_Server::IClient`.
  - Bases de `EXG_Game`: WICO_IGameInfo, EXCO_IGame (subobjeto em +8), EXCO_Persistent<EXG_Game>.
- `0xb405d0` (rótulo `EX_SinglePlayerMode::InitGame`) recebe bool; com 1 aplica configuração individual (`singleplayer_craters`). Único chamador direto: `EX_MultiPlayerHostMode::InitGame` (`0xb3f2e0`), em `0xb3f386`: `6a 00 / 8b cb / e8 ..` (`push 0; mov ecx,ebx; call 0xb405d0`).
- `0xb405d0` cria jogo por `0x756990`, alocando `0x1320b8` bytes e executando construtor `EXG_Game` `0x754f40`. Ele armazena argumento de registrador (Ghidra: `in_AL`) em `+0xC`, byte lido pelo servidor pelo subobjeto `EXCO_IGame` (`this+8`, campo `+4`). Outro chamador de `0x756990`: `WICR_GameController::InitGame` (`0x768a10`), controlador de `WICR_GameController::MapCycle` (`0x768e50`).

### <a id="derived-2"></a>Deduções

- Executável Steam é GOG com SteamStub. Endereços GOG devem coincidir em memória após o stub (inferência de dados/seções idênticos, ainda sem verificação em memória). Hook por assinatura pode servir a ambos.
- Mesmo código/dados sugere compatibilidade LAN (inferência, não teste).
- Hospedar multiplayer é modo individual mais servidor de rede. Protótipo mais simples: host MP chamar `InitGame(1)` (byte `0xb3f387`, `00` -> `01`) num mapa com equivalente de campanha e entrar com outro cliente. Obstáculos esperados: papel (`"joining singleplayer match with non-SP role"`), mapa/papel da sala, scripts para um `PLAYER_HUMAN`.

### <a id="recommendation"></a>Recomendação

Desenvolver na versão GOG: análise estática direta, sem DRM atrapalhando hooks, versão comprável por novos jogadores. Manter Steam como segundo alvo por hooks em execução com assinatura conferida, sem desempacotar.

## <a id="session-4-2026-10-17-host-mode-prototype-set-up"></a>Sessão 4 (2026-10-17): protótipo do modo host preparado

- Opções encontradas listando strings do verificador `0x9fa4c0`: `window`, `debug`, `pythondebug`, `nointro`, `multi`, `forceteam1`, `forceteam2`, `noai`, `dev`, `startingap`. `-multi` pula mutex `WorldInConflict_Duplicate_App_Detection` em WinMain (`0xb2ef40`), permitindo duas cópias no PC.
- Cliente comercial não registra depuração por padrão; espera-se que `-debug` habilite `Documents\World in Conflict\Debug\wic_<id>_debug.txt` (a confirmar).
- Protótipo GOG: offset de arquivo `0x73f387` de `wic.exe`, `00` -> `01` (`push 0` -> `push 1` antes de `call 0xb405d0` em `EX_MultiPlayerHostMode::InitGame`). Resultado aguarda teste do usuário.

### <a id="test-1-owner-v1-one-byte-patch-gog-test-copy-lan-host-on-as_dome"></a>Teste 1 (usuário, v1 com patch de um byte, cópia GOG, host LAN em as_Dome)

Observado (log com `-debug`):
- Sala mostra descrição de campanha de as_Dome (soviéticos invadindo Seattle). Não se sabe se a original mostra igual.
- Em Create: `EX_PlayState::Init(): MULTI_PLAYER_HOST mode`, servidor em 48000, missão `maps/seattle2/seattle2.ice` carregada com `units/unittypes_wic_singleplayer.ice`, `ex_singleplayermode.cpp InitGame(): creating game...`, depois `ex_multiplayerhostmode.cpp(788): InitGame(): Error Could not init Python`, retorno ao menu.

Código (GOG):
- Inicialização Python `0xb41200(this, spScriptName, flag)` (`ret 0xc`, caminho em EAX). Host MP empilha `0, 0`, calcula caminho por `0x985dd0` (lê `myPythonServerScript` de mission-info `+0x29dc`), chama função.
- `EX_SinglePlayerMode::PlayerLoadingThread` (`0xb40c90`) chama virtual `InitGame(1)`, empilha `0`, obtém nome do script por `0x984310` (lê `mySinglePlayerData.mySinglePlayer...` em `+0x29c0`), empilha como segundo argumento, chama `0x985dd0` e `0xb41200`.

Patch v2 (sobre v1): `0xb3f393`–`0xb3f3d7` reescritos como modo individual (`push 0; push ecx; mov eax,esi; call 0x984310; add esp,4; push eax; call 0x985dd0; push ebx; call 0xb41200; test al,al; jnz 0xb3f3e3; jmp 0xb3f3d8`). Sobrescreve registro de falha Python. Sem relocações no executável. SHA-256 alterado `18765094...`.

### <a id="test-2-owner-v2"></a>Teste 2 (usuário, v2)

Mesmo sintoma (menu após cerca de 1 s). Log sem falha de inicialização Python; inicialização passou. Depois `EX_PlayState::Update() returning EVENT_GAME_EXIT`, e no encerramento `wico_pythonc.cpp CheckPyError(): exceptions.ImportError: No module named client`.

Código: thread de carregamento MP `0xb3f840` chama `InitGame` (`0xb3f2e0`) e `0xb3f640`, que cria local por `EX_IPlayMode::InitPlayer` (`0xb41e20`). Recebe papel em EAX e `(slot, a2, a3, isMultiplayer)` na pilha. Recusa incompatibilidades com mensagens num nível não gravado por `-debug` ("Player joining singleplayer match with non-SP role!", "...multiplayer match with SP role!", variantes FPM). Modo individual usa `EAX=[0xe9ff6c]` (papel SP), `(0,0,1,0)`; host usa `EAX = 0 or [0xe9ff74]`, `(0,1,0,1)`.

Patch v3 (sobre v2): `0xb3f7cc`–`0xb3f7e3` -> `mov eax,[0xe9ff6c]; push 0; push 1; push 0; push 0; nop×11`, criando jogador local como individual. SHA-256 `63e7976f...`. Script passa também `-debugspam` (esperado mostrar mensagens de baixo nível, a confirmar). Próximo obstáculo esperado: remotos ainda entram com papel MP.

### <a id="test-3-owner-v3-and-switch-to-runtime-tracing"></a>Teste 3 (usuário, v3) e mudança para rastreamento em execução

Mesmo sintoma. `-debugspam` não acrescentou nada. Logger (`0xa02800`) sempre escreve níveis 0/2, nível 1 só com `[0xdffe06]`; ausência de "creating player on slot %d" (nível 0, `EX_IPlayMode::InitPlayer`) significa que não chegou à criação. Dedução: falha ainda dentro ou após Python; v2 sobrescreveu seu log de erro.

Ferramenta própria (`wic-coop/trace/`): `tracehook.dll` redireciona 12 locais `call` do carregamento para funções de registro (argumentos/retorno) em `coop_trace.log`; `coop_launch.exe` inicia wic.exe suspenso e carrega DLL com CreateRemoteThread + LoadLibraryA. Compilado MSVC x86 (VS 2022). Teste básico na cópia GOG: 12 locais interceptados.

### <a id="trace-1-owner-v3--tracer"></a>Rastreamento 1 (usuário, v3 + rastreador)

Observado em `coop_trace.log`: InitGame host -> `SP::InitGame(1)` retorna 1 -> InitPython (área auxiliar) -> configuração de caminhos Python (`0x972500`) retorna 1 -> execução de script servidor (`0x925a80`) retorna 0 -> InitPython 0 -> InitGame 0. `0x925a80` cria `WICP_Python`; seu init (`0x925760`, `wicp_python.cpp`) executa `import client`, correspondendo a `ImportError: No module named client`. Python cliente não encontra `client.py` do mapa no host.

Código lido: `0x984310` retorna `mySinglePlayerData.mySinglePlayerScriptFiles`; `0x985dd0` monta `<map dir>/<myWicedMap.myPythonServerScript>` (mission-info `+0x29dc` é `myWicedMap`, não modo). `0x972500` define busca Python a partir deles por `0x4aab10`. `EXCO_MissionInfo::Init` (`0x987540`) carrega dados individuais (`0x987290`) em todos os modos.

Próximo: rastreador v2 (21 locais, argumentos/resultados string) comparando tentativa host e início real individual na mesma sessão.

### <a id="trace-2-owner-host-attempt-then-resume-campaign-in-the-same-session"></a>Rastreamento 2 (usuário): tentativa host e Resume Campaign na mesma sessão

Resume Campaign (berlin1) também falhou na cópia com `import client`, pelo caminho individual intacto (`ex_singleplayermode.cpp(163): PlayerLoadingThread(): Error Could not init Python`). Strings: scripts individuais `cutscenes/maps/<map>/python/serverplay.py`, servidor `maps/<map>/python/server.py`, busca `cutscenes/maps/<map>/python;maps/<map>/python`; host monta iguais para seattle2.

Dedução: patches não causam a falha. Todos os scripts passavam `-pythondebug`. Em `0x972500`, sem `pythondebug`, o jogo incrementa `[0xe0f418]` antes do Python. Hipótese não confirmada: é `Py_OptimizeFlag`, execuções normais importam `.pyo` otimizados, e `-pythondebug` procura `.py`/`.pyc`, ausentes dos arquivos. `-pythondebug` foi removido de todos os scripts. Lição: comprovar referência individual no ambiente exato antes do patch (lição 3 dos guias).

### <a id="test-6-owner-v3-host-without--pythondebug--campaign-runs-from-the-lan-lobby"></a>Teste 6 (usuário): host v3 sem `-pythondebug`, campanha roda pela sala LAN

Observado (usuário + rastreamento): LAN Create Game em as_Dome com v3 carrega missão seattle2. Por segundos só os APCs iniciais aparecem; cena completa reproduz (som/animação), missão normal inicia e usuário relata funcionamento normal. Rastreamento: MPHost::InitGame = 1, get player slot = 1, voip connect = 1, `EX_IPlayMode::InitPlayer(SP role, 0,0,1,0)` = 1, etapa 3 = 1.

Dedução: mínimo de três edições no GOG para missão como host de rede: `InitGame(1)` (0xb3f387), caminho individual do script Python (0xb3f393..), papel individual do local (0xb3f7cc..). Servidor continua em 48000 durante missão (linha `enabled reliable listening on port 48000` dos logs anteriores; não conferido durante partida).

`coop_join.cmd` só abre outra cópia no menu; entrada ainda não tentada.

### <a id="test-7-owner-second-copy-joins-the-v3-host-over-lan"></a>Teste 7 (usuário): segunda cópia entra no host v3 por LAN

Jogador 2 vê a partida, entra, recebe seleção MP de facção/papel, escolhe e volta ao menu com perda de conexão. Log host: `Client ('Player') accepted on slot '1'`, `SendPlayerStartingData(): Player connected`, `PlayerJoinedTeam(): Player 1 joined team 1`, depois `exg_game.cpp(4974): PlayerSetRole(): Player 1 joining singleplayer match with non-SP role!`, `exr_client.cpp(661): ParsePlayerSetRole() failed`, `RemovePlayer(): removed player 1`.

Código GOG, `EXG_Game::PlayerSetRole` `0x752880`: `cmp byte [game+4],0` em `0x7529c7` escolhe ramo SP; `0x7529d8 jnz 0x752b92` aceita com campo global de permitir qualquer papel; `0x7529e4 je 0x752b92` aceita SP; senão registra e falha.

Patch v4 (sobre v3): `0x7529d8` `0f 85 b4 01 00 00` -> `e9 b5 01 00 00 90` (sempre aceitar em SP). SHA-256 `91e1f854...`. Convidado mantém papel MP escolhido.

### <a id="test-8-owner-v4-player-2-joins-the-running-campaign-mission"></a>Teste 8 (usuário): v4, jogador 2 entra na campanha em execução

Observado pelo usuário: jogador 2 entra, ainda seleciona facção/papel MP, não recebe unidades, mas vê mapa e todas as unidades sem névoa; acompanha unidades de Parker movendo em tempo real às ordens do jogador 1. Host: `Player 1 joined team 1`, `PlayerSetRole(): Player 1 has got role INFANTRY (234881739)`, sem recusa.

Dedução: segundo cliente real conectado ao servidor de campanha recebe simulação sincronizada. Falta preparar cada jogador: AP/reforços, zonas de chegada, névoa (equipe/visão) e tudo que scripts fazem para `PLAYER_HUMAN`.

## <a id="status-after-session-4-2026-10-17"></a>Estado após sessão 4 (2026-10-17)

Funciona numa cópia de teste GOG com quatro patches de bytes (v1–v4) em wic.exe:
1. Partida LAN em mapa de campanha executa missão real (cenas, scripts, IA).
2. Segundo cliente entra e vê a missão ao vivo.

Pendências, aproximadamente em ordem:
- Controle do jogador 2: (a) compartilhado, servidor aceita suas ordens para unidades do 1 e seleção alterada no cliente; (b) forças próprias, fornecer AP/zona de chegada, definir equipe/visão e ensinar scripts sobre outro humano.
- Telas MP de facção/papel do convidado.
- Segundos iniciais só com APCs antes da cena no host.
- Migrar alterações de executável para DLL proxy em execução compatível com GOG/Steam.
- Rede pela internet (só LAN testada; Spacewar planejado).
