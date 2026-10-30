# <a id="far-cry-2-working-notes"></a>Far Cry 2: notas de trabalho

Iniciado em 2026-10-19. Fase: 0 triagem, iniciando 1 pesquisa e 2 espaço de trabalho.

## <a id="identity"></a>Identidade

- Título: Far Cry 2 (2008), Ubisoft Montreal. Loja: Steam, app id 19900.
- Versão: 1.03 (do `PatchNotes.txt` incluído). Steam build id: 52164.
- Engine: Dunia (derivada da CryEngine 1). Arquitetura: x86, 32 bits.
- Arquivos principais (SHA-256):
  - `bin\FarCry2.exe`, 28296 bytes (stub de inicializador): `7d018d049974972fe71ec38ec446a141e9011a846b71dad6fe4242bf9353fd1d`
  - `bin\Dunia.dll`, 20183176 bytes (engine): `6353936a54aa841350bb30ff005727859cdef1aa10c209209b220b399e862765`
  - `bin\FC2.dll`, 389768 bytes (código do jogo): `94486f716554c23f9673409b0a4b36121a1ad64d11029fed1aebb1fe71494a7b`
- SO: Windows 10 Pro 10.0.19045.

## <a id="observations-checked-on-the-install-or-a-source"></a>Observações (verificadas na instalação ou em uma fonte)

- `detect_engine` não encontrou correspondência para a pasta de instalação (187 arquivos examinados).
- A instalação inclui `FC2ServerLauncher.exe` (servidor dedicado) e um readme dele, portanto
  a engine tem código de rede multijogador. Fonte: `bin\FC2ServerLauncher_ReadMe.txt`.
- Um instalador do PunkBuster está incluído em `installers\PunkBuster`.
- Os dados ficam nos arquivos `Data_Win32\*.dat/.fat` (common, patch, shadersobj, sound).
- O diretório não tem entrada para Far Cry 2. Tem dois mods cooperativos de Far Cry 1 (CryEngine 1).
- Uma discussão de 2013 na Steam diz que o jogo é apenas individual, sem cooperativo fora do
  multijogador: https://steamcommunity.com/app/19900/discussions/0/864973123475897875
  (resposta de usuário, não uma fonte oficial).
- FCSE (Far Cry 2 Engine Extension) existe no Nexus Mods e aplica patches ao comportamento de `Dunia.dll`:
  https://www.nexusmods.com/farcry2/mods/368 . A página retornou HTTP 403 ao
  WebFetch, portanto os detalhes vêm apenas de um resumo de busca.

- FC2MPPatcher (GPL-2.0, 463 commits, sem datas vistas) aplica patches aos arquivos do jogo para restaurar o
  multijogador online após a Ubisoft encerrar seus serviços em 2021-06-01. Exige versão 1.03 do jogo;
  Retail, Steam, Uplay e GOG testados. As contas passam por longweep.net. Nenhuma menção a cooperativo ou
  campanha. https://github.com/halvors/FC2MPPatcher (README apenas via WebFetch).
- FCSE segundo o resumo de busca: um inicializador do autor “bajuh” do Nexus que carrega plugins DLL de
  `bin\plugins\` na inicialização; uma extensão do Vortex trata essas DLLs como plugins de “Far Cry Script Extender”.
  Nenhum repositório de fontes encontrado por busca.
- Buscas que não encontraram projeto de campanha cooperativa de Far Cry 2: "Far Cry 2 campaign co-op mod",
  "... Dunia ... moddb", uma consulta ampliada de cooperativo/Nexus/Reddit, uma consulta em russo e uma
  consulta de servidor dedicado. ModDB lista mods de reformulação (New Dunia, Realism+Redux, True
  Misery Redux) e um mapa de deathmatch para 16 jogadores, nenhum cooperativo.

### <a id="from-strings-and-ghidra-auto-analysis-on-the-test-copy-nothing-run-yet"></a>Das strings e da análise automática do Ghidra (na cópia de teste, nada executado ainda)

A análise sem interface do Ghidra 12.1.4 de `FC2.dll` e `Dunia.dll` foi bem-sucedida. Varredura de palavras-chave nas
strings imprimíveis (script: rascunho local, saída: `local/dumps/strings-*.txt`):

- `Dunia.dll` contém o código de rede. Nomes de classes: `NetworkEngine`, `CNetObject*`,
  `CNetDescriptor`, `CNetworkComponent` com variantes Pawn, Vehicle, MountedWeapon, Projectile,
  Pickup, Weapon, Camera, Gadget, Ladder. Tipos NetObject têm papéis
  `Host` / `Controller` / `ThirdParty` (por exemplo, `NetObject.PawnHost`,
  `NetObject.PawnController`, `NetObject.PawnThirdParty`).
- Sessões e lobby: `CSessionInfo_Agora`, `CLobbyService`, `CFCXLobbyService`, strings de
  erros de rendezvous / matchmaking da Ubisoft, `MULTI_ERROR_NETWORK_BIND_MAIN_SOCKET`. Existe uma
  string de lobby de deathmatch (`Deathmatch Lobby (%d)`).
- Estrutura do modo individual: `CFCXMissionManager`, `CGameMissionMgr`, `CBaseMission`,
  `MissionManager`, comando de console `get_mission_manager_status`, `SCRIPTS\MissionTools.lua`,
  `CLuaResource` e uma string de runtime `Lua 4.1 (alpha)` (Lua é a linguagem de script, a
  confirmar nos arquivos).
- Sistema de companheiros nas strings: `get_current_primary_buddy`, `set_current_primary_buddy`,
  `CSpawnPointBuddy`, `BuddyRescueEnable`, `Selects a buddy to use as main avatar.`
- Salvamentos: `SaveGame`, `CSavePointSaveGamePage`, `IsSaveGame`. Apenas uma string com
  “coop”: uma chamada DirectSound `SetCooperativeLevel` (não um modo de jogo).
- `FC2.dll` é pequena (1097 strings) e não tem nada disso: a rede fica na DLL da engine.
- PunkBuster é referenciado por 15 strings em `Dunia.dll`.

### <a id="archive-unpacking-data_win32-on-the-test-copy"></a>Extração dos arquivos (Data_Win32, na cópia de teste)

- Formato dos arquivos: cabeçalho `FAT2`, versão de arquivo 5, plataforma Windows, versão de compressão 3
  (lida dos primeiros bytes de `patch.fat`). As entradas usam o layout v5: id de compressão
  de 2 bits (0 nenhuma, 1 LZO1x).
- Ferramenta: Gibbed.Dunia (licença zlib) https://github.com/gibbed/Gibbed.Dunia no commit
  `a43405cab3ea206ed0e9fcc6222fc2e36d545eea`, projeto `Gibbed.FarCry2.Unpack`, com o
  submódulo `FarCry2-File-Lists` em `22f9499e837f9f524ac7a857d3e0af9e3f8ee72c`. Não existem builds
  publicadas, portanto é compilada com `dotnet build` (SDK 9). Precisou de duas correções locais
  neste commit (marcadas no fonte como modificadas localmente):
  1. `BigFileV2.ToCompressionScheme` só mapeava versões de arquivo 10 e 11; adicionada v5
     (0 = nenhuma, 1 = LZO1x, como em commits antigos do upstream, por exemplo `da6fb1d`).
  2. `EntryDecompression.DecompressLZO1x` ignorava `maxSize`, portanto o buffer de 64 bytes de
     detecção de tipo estourava (`MemoryStream not expandable`); agora escreve no máximo `maxSize`.
  A pasta `configs` deve ficar ao lado da pasta da ferramenta.
  Essa descoberta merece entrar no playbook (uma build padrão da ferramenta não extrai Far Cry 2).
- Resultado: `patch.fat` fornece 216 arquivos; `common.fat` fornece 3428 arquivos, 102 MB
  (`ui` 1977, `domino` 1071, `scripts` 218, `config` 26, `languages` 20, `engine` 27,
  `soundbinary` 24, `databases` 10, `graphics` 8, `ingameeditor` 14, `__UNKNOWN` 29).
- Scripts são Lua. `scripts\missiontools.lua` define uma tabela `Mission` com eventos como
  `Event__MissionSetState`, `Event__SaveGame`, `Event__Game_PlaySequence`
  (chama `Game:MissionSetState`, `Game:SaveGame`).
- `domino\` contém 1071 arquivos Lua, cada um um nó de um sistema de grafos de scripts visuais
  (“Domino”): um comentário de cabeçalho declara `ControlIn`, `ControlOut`, `DataIn`, `DataOut`
  (por exemplo, `domino\system\assignbuddy.lua` chama `GetBuddiesManager():AssignBuddy(...)` e
  `GetFCXMissionManager():ActivateBuddyMission(...)`). `domino\system`: 233 nós,
  `domino\user`: 838 nós.
- Os próprios grafos de missão não estão em `common`; `missions\missions.xml` está vazio (0
  bytes) ali. `worlds\worlds.dat` tem 2.58 GB e provavelmente contém mapas e dados de missão.
  A extração foi iniciada pulando arquivos de tipo desconhecido; resultado ainda não lido.
- Existem mapas de ações de entrada separados para modo individual e multijogador
  (`config\inputactionmapsingle.xml`, `inputactionmapmulti.xml`).

- `worlds.fat` (v5, 142369 entradas): 77776 arquivos com nomes conhecidos extraídos (2.0 GB):
  `levels\` (60219 arquivos), `graphics` (13055), `domino` (821 nós Lua específicos de missões),
  `scripts` (126), `worlds\` (224). Principais extensões: `.fcb` 26015 (formato binário de
  objetos), `.xbt` 14127 (texturas), `.sdat`/`.zsr`/`.srl` mais de 6000, `.nvm` 4275 (malha de navegação),
  `.hkx` 2546 (Havok), `.lua` 821.
- Fases: `mp_*` (15 mapas multijogador, por exemplo `mp_02_s_shanty`, `mp_25_prison`), `w1_*` e
  `w2_*` (campanha, duas regiões, setores a a e, etapas 1 a 5, por exemplo `w1_b_2`), `tmpla`,
  `ige_map` (editor dentro do jogo). `scripts\engine\objects\pawn\statemachine\*.gosm.xml`
  (`main_avatar`, `vehicles`, `weapons`) são máquinas de estados em XML simples.
- Arquivos chamados `*.game.xml` nas fases MP são binários, não XML. Pastas de fases da campanha
  contêm arquivos `.fcb` por setor e nenhum `generated\*.managers.fcb` entre os arquivos com nomes; as
  64593 entradas restantes não têm nome conhecido e foram extraídas separadamente (ainda não lidas).

- As 64593 entradas sem nome foram extraídas separadamente (0.59 GB): 43403 sem extensão,
  12973 `.fcb`, 7282 `.xbt`, 862 `.hMvN`, 51 `.xml`, 22 `.xbg`.
- FCB para XML funciona com `Gibbed.FarCry2.ConvertBinaryObject` (mesmo repositório e commit,
  compilado sem modificações). `binary_classes.xml` na configuração FC2 nomeia muitas classes
  (`CBaseMission`, `CConvoyMission`, `CBrainBuddyBase`, `CEnableBuddyDown`, ...), mas muitos
  campos ainda aparecem como hashes brutos. Exemplo: a fase multijogador
  `mp_02_s_shanty.managers.fcb` é convertida para XML (5.7 MB) com uma entidade legível
  `DominoManager` da classe `CDominoManager` no início, portanto o executor de grafos Domino é uma
  entidade de gerenciador por fase.

### <a id="game-modes-and-network-config-data-files-read-from-the-unpacked-archives"></a>Modos de jogo e configuração de rede (arquivos de dados, lidos dos arquivos extraídos)

- `engine\gamemodes\gamemodesconfig.xml` (common e uma cópia com patch um pouco maior em
  `patch.fat`, 491463 bytes) define cada modo de jogo como um `<GameMode>` com um
  `<Desc Name=... GameModeEntityArchetype=...>` e uma lista de `<Service ClassName=...>`.
  Modos vistos: `FCXConsole`, `FCXMainMenu`, `Single`, `Editor`, `FCXEditor` (editor dentro do
  jogo, um modo com rede), `FCXBenchmark`, `FCXSingle`, além dos modos multijogador.
- Os serviços da campanha (`FCXSingle`) não têm atributo `NetPresence`: `CSpawnPointService`,
  `CFCXPlayerService`, `CFCXMissionManager`, `CBuddiesManager`, `CFCXGameplayManager`,
  `CRescueManager`, `CFCXWeaponsService`, `CFCXAIBehaviorService`, `CFCXHudService`,
  `CPersistenceMgr`, `CDominoService`, e outros. O modo com rede `FCXEditor` lista
  `CFCXPlayerService`, `CFCXMissionManager`, `CFCXWeaponsService`, `CFCXHudService` com
  `NetPresence="AllPeer"`, e `CFCXDMSpawnPointService` com `NetPresence="HostOnly"`.
  Portanto, um serviço pode ser marcado como replicado para todos os pares ou exclusivo do anfitrião neste arquivo.
- `engine\settings\defaultnetworkconfig.xml`: `UseAgora="0"`, `ConnectionSpeed="lan"`,
  portas 9000 a 9004 (engine online, serviço online, anfitrião e cliente de transferência de arquivos, difusão
  LAN). Tipos de objetos de rede são definidos em
  `engine\online\onlineengine\{engine,fcx,session,onlineengine}.netobject.xml`, grupos e
  canais em `default.netgroup.xml` e `default.netchannel.xml`.
- Strings de `Dunia.dll`: `CFCXGameModeSingle`, `CFCXGameModeDeathMatch`, `...VIP`, `...CTF`,
  `...TeamDeathMatch`, `CFCXGameModeInitNetworkOperation`,
  `CFCXGameModeShutdownNetworkOperation`, `GameModeOnNetReady`, `-dedicated`,
  `IsDedicated`, `net_GetCurrentGameMode`.
- Ghidra (descompilado, `Dunia.dll`): `FUN_10750140` registra `CFCXMissionManager` como classe
  Lua (`gettable_event`), confirmando a vinculação Lua. `FUN_104ebf90` é
  `RegisterNetworkComponents`; ramifica-se por uma flag global em `DAT_11645a74 + 4`.
  `FUN_10218010` constrói uma tabela de categorias de log de rede (General, Transmission,
  MainSocket, NetworkEngine), não a inicialização da engine. `MULTI_ERROR_NETWORK_BIND_MAIN_SOCKET`
  não tem referência direta de código (provavelmente consultado por tabela). Os nomes de funções são nomes
  automáticos do Ghidra. Scripts: `local/scripts/XrefStrings.java`, `strs.py`, `grepstr.py`.

### <a id="command-line-and-first-run-test-copy"></a>Linha de comando e primeira execução (cópia de teste)

- Opções de linha de comando encontradas como strings em `Dunia.dll` (ainda não testadas, exceto
  `-dedicated` pelo inicializador): `-host`, `-join`, `-client`, `-dedicated`, `-noagora`,
  `-world`, `-load`, `-spawn`, `-spawnpos`, `-spawnangle`, `-cmdfile`, `-exec`, `-logFile`,
  `-norender`, `-nosound`, `-borderless`, `-online`, `-ranked`, `-login`, `-nobf`,
  `-noarchivecache`, `-usearchivecache`, `-benchmark*`.
- Nomes de arquivos na lista de arquivos da engine (strings): `common.dat`, `patch.dat` (listado por último),
  `shadersobj.dat`, `sound.dat`, `sound_%lang%.dat`, `worlds/<name>/<name>.dat`. Ainda é desconhecido se a
  engine também lê arquivos soltos do disco em vez dos arquivos de dados.
- 2026-10-19, execução 1: `FC2ServerLauncher.exe` da cópia de teste, opções padrão, 40 s, depois
  parado pelo PID. Resultado: iniciou sem nenhum serviço Ubisoft. Log
  (`bin\dedicated_log.txt` na cópia): login `EAccountFlags_Offline`, sessão
  `E_SESSION_TYPE_OFFLINE` em `<LAN address>:9001`, 16 slots públicos,
  `match_pb_enabled = 0`, `network_type = 1`, examinando portas 9000 a 9999, porta de difusão
  LAN 9004. Definir `gamemode` falha com "can only do it in the game lobby". Nenhuma falha. Isso
  apenas mostra que o servidor inicia e abre uma sessão LAN offline; nenhum cliente entrou e nenhum mapa
  foi carregado.
- Efeito colateral fora do espaço de trabalho: a execução criou
  `Documents\My Games\Far Cry 2\Server\dedicated_server.cfg` (3217 bytes). Essa pasta
  não existia antes; não há arquivos de salvamento ali. Salvamentos reais não foram tocados (ainda não localizados).

### <a id="start-up-code-paths-ghidra-duniadll-auto-names"></a>Caminhos de código da inicialização (Ghidra, `Dunia.dll`, nomes automáticos)

- `FUN_10663d40` é o despachante de linha de comando (`-exec` primeiro; depois `-editorpc`,
  `-benchmark`, `-host`/`-join`, `-load`, `-wait`, senão o início normal `FUN_106622f0`).
- `-world <name>` e `-map <name>` são usados apenas pelo inicializador de benchmark `FUN_10662f90`
  (seu texto de erro: `-benchmark {playback|record|sectors|spawnpoints|path} -world worldname
  -map mapname`, com `-spawn`, `-spawnpos`, `-spawnangle`). Sem `-benchmark`, não fazem nada.
- `-load <savegame>` (`FUN_10661f50`) carrega um arquivo de salvamento e lê `PlayerPos`. Salvamentos são
  `*.sav` em `Documents\My Games\Far Cry 2\` (string `My Games\Far Cry 2\`). Não existe salvamento
  neste PC, portanto esse caminho não pode ser testado sem criar um primeiro.
- `-host` (`FUN_10662440`): exige `-login <name>` ("Invalid parameters for -host, missing
  (-login)"); opcionais `-password`, `-keyonline`, `-bfname`, `-dedicated`, `-sessionuid`,
  `-ranked`; opções de modo `-team`, `-ctf`, `-vip` (padrão é deathmatch); tipo de rede `-online`
  ou `-lan`; `-online` com `-noagora` é recusado ("Cannot launch an online game (-online)
  without using Agora").
- `-join` / `-client` (`FUN_10662b40`) e `-wait` passam por `FUN_10663af0`.

### <a id="client-runs-on-the-test-copy-2026-10-19"></a>Execuções do cliente na cópia de teste (2026-10-19)

Todas as execuções: `bin\FarCry2.exe` da cópia de teste, diretório de trabalho `bin`, parado pelo PID.

| Argumentos | Resultado |
|---|---|
| `-noagora -nosound -logFile <absolute path>` | encerrou imediatamente com código 0 (não reproduzido; talvez uma etapa da primeira execução) |
| `-nobf`, `-borderless -logFile fc2.log`, `-noagora`, `-nosound`, `-logFile fc2b.log` (cada um sozinho) | janela com título "Far Cry 2", processo vivo durante todos os 15 a 20 s |
| `-noagora -world w1_b_2 -logFile fc2c.log` | conjunto de trabalho de cerca de 40 MB, encerrou com código 0 em cerca de 30 s |
| `-host -login coopbot1 -lan -noagora` | conjunto de trabalho de 38 a 69 MB, nenhuma porta UDP ou TCP aberta, encerrou com código 0 em cerca de 30 s |

- `-logFile` não produziu arquivo de log na cópia nem em `Documents`.
- Nada foi escrito em `Documents` pelas execuções do cliente, e a instalação original não mostra
  arquivo alterado.
- Desconhecido: por que o cliente nunca passa de cerca de 70 MB e encerra sozinho após cerca de 30 s.
  Candidatos (não verificados): falha na inicialização gráfica neste PC, introdução ou menu esperando
  entrada, verificação Steam. O servidor dedicado, por sua vez, iniciou e abriu uma sessão.

### <a id="why-the-client-stalls-diagnosis-in-progress-2026-10-19"></a>Por que o cliente para (diagnóstico em andamento, 2026-10-19)

- Capturas apenas da janela (`local/scripts/shot-window.ps1`, `PrintWindow`, não captura da área de trabalho):
  `FarCry2.exe` sem argumentos mostra a arte da tela inicial de Far Cry 2 em uma janela de 572x380 e
  não muda entre 10 s e 22 s.
- Estado do processo em cerca de 14 s (`local/scripts/list-modules.ps1`, PowerShell de 32 bits necessário para ler
  módulos de um jogo de 32 bits): cerca de 2 s de CPU em uma janela de 6 s (ocupado, não congelado), 15 threads, todas
  esperando. Carregados: `Dunia.dll`, `systemdetection.dll`, `dxdiagn.dll`, WMI (`wbem*`, `fastprox`),
  `d3d9`, `d3d10`, `d3d11`, `d3d12`, `dxgi`, drivers AMD em modo de usuário, `binkw32`, `dsound`, `EAX`,
  `ws2_32`, `AcLayers.DLL`. `FC2.dll` **não** está carregada ainda, portanto a biblioteca do jogo nunca começa.
- `FC2Launcher.exe` da cópia não mostra janela, vive alguns segundos e encerra com código 0.
- `-norender -nosound` sozinho: encerra com código 0 após 23 s (pico de 74 MB); com
  `-host -login coopbot1 -lan -noagora`: após 7 s (41 MB); com `-dedicated`: após 3 s (65 MB).
- Strings de `systemdetection.dll`: consultas DxDiag e WMI (`Win32_VideoController`,
  `Win32_PhysicalMemory`, `Win32_ComputerSystem`, `Win32_NetworkAdapter`) e textos de erro como
  `Could not detect information for adapter %i`, `Could not retreive current resolution width`.
- Este PC informa dois controladores de vídeo: `AMD Radeon(TM) Graphics` e um `Virtual Display Device`
  sem resolução e sem valor de RAM. WMI responde a todas as consultas acima em menos de 0.4 s.
- ~~Hipótese: a etapa de detecção do sistema falha no adaptador virtual.~~ **Refutada para as verificações de
  exibição** (veja abaixo). Não testados: execução pela Steam da instalação original, `FC2Launcher.exe` com um
  perfil.

Leitura estática da inicialização (Ghidra, `Dunia.dll`, nomes automáticos; scripts `local/scripts/DecompAt.java`,
`display-check.ps1`):

- Exportação `RunGame(HINSTANCE, const char*)` (`10006510`): se a linha de comando tem `-openautomate`,
  chama `FUN_10005fa0` e retorna verdadeiro. Senão executa em laço: `FUN_10006130` (cria a janela da tela
  inicial), `InitDuniaEngine` (`10004900`), `DestroyWindow(splash)`; se `InitDuniaEngine` retorna 0,
  retorna falso (o stub encerra com código 0). Senão executa o jogo (`DAT_10fd42c8`).
- `InitDuniaEngine` retorna 0 nestes caminhos vistos na descompilação: o mutex nomeado
  `FarCry2Instance` já existe (`OpenMutexA`); nenhum dispositivo de exibição com as flags
  ATTACHED_TO_DESKTOP e PRIMARY_DEVICE (laço de `EnumDisplayDevicesA`); `EnumDisplaySettingsA` do
  modo atual falha; o modo atual não é de 32 bits por pixel (a menos que uma flag esteja definida);
  outros ramos ainda não lidos. Um `MessageBoxA(..., "Error", 0)` é exibido se o despachante de linha de
  comando `FUN_10663d40` retorna 0.
- As mesmas chamadas de exibição feitas apenas para leitura neste PC (`display-check.ps1`, C# P/Invoke, 32 e 64
  bits): `\\.\DISPLAY1` AMD Radeon, flags `0x80005` (conectado, primário), 32 bpp, 1920x1080@60;
  `DISPLAY2/3` não conectados; `DISPLAY4` "Virtual Display Device" flags 0 (não conectado). Portanto essas
  verificações passariam. (Uma primeira versão em PowerShell informou “no device” por um erro meu de
  marshalling, erro 87; a versão C# é a confiável.)
- Ainda não se sabe qual ramo encerra. Um depurador (breakpoints em `ExitProcess`, `MessageBoxA`,
  resultados de `OpenMutexA`) ou um rastreamento do Process Monitor responderia; nenhum está instalado.

- Conversão em massa dos 12973 arquivos `.fcb` sem nome para XML terminou: 12973 convertidos, 0 falhas
  (`local/dumps/xml-unknown`, ainda não analisado).

### <a id="world-sectors-and-mission-layers-converted-xml-nothing-run"></a>Setores do mundo e camadas de missão (XML convertido, nada executado)

- Os dados do mundo são divididos em objetos `WorldSector` (campos de cabeçalho `Id`, `X`, `Y`), cada um uma lista de
  objetos `Entity` com componentes. 2023 dos 12973 arquivos `.fcb` sem nome são setores; uma
  pasta de fase da campanha (`levels\w1_b_2`) foi convertida em 1105 arquivos XML de 1246 (141 falhas, não
  investigadas), 605 deles setores.
- Cada entidade contém um `CMissionComponent` (campo de string hash `7AF1FD74` mais
  `hidMissionLayerPath`). String vazia e caminho `FFFFFFFF` significam “sempre carregado”.
  Script: `local/scripts/mission_layers.py`, resultados `local/dumps/mission-layers*.txt`.
- Setores sem nome (mapas multijogador): apenas quatro camadas não vazias, nomeadas segundo os modos de jogo:
  `fcxdeathmatch`, `fcxteamdeathmatch`, `fcxvip`, `fcxctf`. Portanto os modos multijogador selecionam seu
  conteúdo por camadas, como o nome do modo de jogo.
- Setores da campanha de `w1_b_2`: 61 camadas distintas, principalmente caminhos de missão como
  `missions\librarymissions\a1lm02\wager_trainwreck` (290 entidades), `...\wager_enemies`,
  `missions\convoymissions\convoy_01_disable`, `missions\grinmissions\mission_01\operative`,
  `missions\carvertapemissions\carvertapes`, `missions\safehouse\weaponcrates\magiccrate_01`,
  `missions\safehouse\upgrades\w1\level_01` a `level_06`, `missions\_disableformission\...`,
  além de `benchmark`. 528 entidades não têm camada.
- Interpretação: o mundo da campanha é um mundo aberto persistente por região cujo conteúdo de missão é
  ativado e desativado por camada, portanto o conjunto de camadas ativas é o estado da missão que um segundo jogador
  precisaria compartilhar. Isso é derivado dos dados, não testado no jogo.

### <a id="client-starts-baseline-profile-and-the--noagora-finding-2026-10-19-later"></a>O cliente inicia: linha de base, perfil e a descoberta sobre `-noagora` (2026-10-19, mais tarde)

- O dono executou a instalação original pela Steam: funciona e chega ao menu principal (relato do dono,
  não verificado por mim). Essa execução criou `Documents\My Games\Far Cry 2\GamerProfile.xml` (2205
  bytes; `Platform="d3d9"`, 1760x990, `Fullscreen="1"`, portas de rede 9000 a 9004, sem conta).
  Antes desse arquivo existir, o cliente da cópia de teste nunca passava da inicialização.
- Com o perfil presente, a cópia de teste executa: sem argumentos, viva por 90 s, conjunto de trabalho de 177 a 189
  MB (os primeiros 20 a 25 s são uma fase silenciosa de inicialização em cerca de 40 MB). As capturas da janela
  Direct3D em tela cheia são todas pretas (`PrintWindow` não consegue lê-la), portanto não provam
  nada sobre o que aparece na tela.
- Resultados de argumentos na cópia de teste, 45 s cada: `-host -login coopbot1` vivo, 97 MB;
  `-host -login coopbot1 -lan` vivo, 97 MB; `-nobf` encerrou com código 0 após 22 s; `-noagora`
  encerrou com código 0 após 22 s; anteriormente `-host -login coopbot1 -lan -noagora` encerrou após 31 s.
  Portanto **`-noagora` faz o cliente encerrar** aqui (causa não lida no código). `-nobf` sozinho também
  encerrou desta vez, embora uma execução anterior de 20 s tivesse permanecido viva: não explicado.
- `-host -login coopbot1 -lan` (execução de 75 s): UDP 9000 e 9001 abertas após cerca de 26 s, 34 a 40
  threads, 96 MB, nenhum listener TCP e nenhuma conexão TCP de saída vistos. Isso é uma sessão de anfitrião LAN
  dos arquivos não modificados do jogo da cópia. Ninguém entrou, nenhum mapa foi visto.
- O jogo toma a tela (tela cheia) enquanto dura uma execução. `GamerProfile.xml` é o arquivo do
  dono e não foi alterado.
- Dois clientes em um PC colidirão no mutex nomeado `FarCry2Instance` (`OpenMutexA` em
  `InitDuniaEngine`): a segunda instância encerra. Ainda não testado.

### <a id="two-copies-a-dedicated-lan-server-and-a-join-attempt-2026-10-19-evening"></a>Duas cópias, servidor LAN dedicado e tentativa de entrada (2026-10-19, noite)

- Segunda cópia de teste `local/test-installs/FarCry2-B` (copiada da primeira cópia de teste, nunca da
  instalação real; hashes da `Dunia.dll` real e da cópia A verificados novamente, sem mudanças). Patches apenas em sua
  `Dunia.dll` (`local/scripts/patch_mutex.py`, `patch_bytes.py`, backups mantidos ao lado):
  1. offset de arquivo `0xe08950`: nome de mutex `FarCry2Instance` para `FarCry2Instanc2` (1 byte diferente),
     para duas instâncias do jogo executarem ao mesmo tempo. Verificado: o cliente da cópia B executou ao lado do
     servidor da cópia A e sem mais nada; dois clientes ao mesmo tempo ainda não testados.
  2. offset de arquivo `0x662032` (endereço `10662c32`, o imediato de `PUSH 0x2` antes de
     `CALL 10aa1580` no tratador de `-join` `FUN_10662b40`): `02` para `03`, tentando LAN em vez de
     online como tipo de rede. O tratador de anfitrião usa 3 para `-lan` e 2 para `-online`.
- `-join` recebe um endereço IPv4 (`inet_addr`); mensagens: "Trying to launch an online client, but ip
  is missing (-join xxx.xx.xx.xx)" e "...with an invalid ip".
- A configuração padrão do servidor dedicado (`Documents\My Games\Far Cry 2\Server\dedicated_server.cfg`,
  feita pelo jogo, pasta do dono, não editada) tem `network_type 1` ("1 = Online, 2 = LAN"). Com ela,
  o servidor tenta entrar no serviço online encerrado e registra
  `E_SESSION_ERROR_CORE_TASK_TIMEOUT` e "The Far Cry 2 server is not available at this time".
- Com uma configuração própria (`local/test-installs/server-lan.cfg`, passada como
  `FC2ServerLauncher.exe -dedicated "<path>"`, `network_type 2`, `match_pb_enabled 0`): o servidor
  registra um login com `EAccountFlags_LAN`, depois cria uma sessão `E_SESSION_TYPE_LAN` e imprime
  `Game message: Entering lobby!`. Seus sockets: UDP 9000 em todos os endereços, 9001 e 9002 no endereço
  LAN, 9004 (difusão LAN) em todos. O registro de sessão anuncia o endereço de um adaptador VPN
  deste PC em vez do endereço LAN (não escrito aqui).
- O arquivo de log do próprio servidor `dedicated_log.txt` é cumulativo e não foi atualizado pelas execuções
  encerradas à força; a saída do console (stdout redirecionado a um arquivo) é ao vivo e completa.
- Tentativas de entrada, cliente da cópia B com `-join <ip>`, três endereços (loopback, endereço LAN, endereço
  anunciado): em todos os casos o cliente chegou a cerca de 100 MB após 25 s, abriu UDP 9003 e
  9004 e **encerrou sozinho com código 0 após cerca de 46 s**; o servidor nunca registrou um segundo par
  (apenas sua própria entrada de anfitrião com `PeerId: 0`). Portanto nenhuma entrada foi obtida. O encerramento parece uma
  falha ao entrar (não confirmado). O mesmo encerramento ocorreu antes e depois do patch de `02` para `03`.
- Não testados: telas LAN ou de conexão direta dentro do jogo (strings `SearchSessionByJoinIp`, `JoinMatch`,
  "Try to join using direct connect but no ip was set."), `-wait`, um cliente anfitrião (`-host -login x
  -lan`) com entrada da segunda cópia, e leitura do que acontece após `FUN_10aa1580` no Ghidra.

### <a id="host-client-plus-join-and-the-static-join-trace-2026-10-19-night"></a>Cliente anfitrião mais entrada, e rastreamento estático da entrada (2026-10-19, noite)

- Teste: cliente completo da cópia A `-host -login coopbot1 -lan` (UDP 9000, 9001 após cerca de 30 s), depois
  cliente da cópia B `-join <LAN address>` (`local/scripts/host-join-test.ps1`, 75 s). Resultados: o
  cliente permaneceu vivo durante todos os 75 s (encerrava após 46 s quando o anfitrião era o servidor
  dedicado); abriu UDP 9002, 9003, 9004; os contadores de sistema `UDPv4 Datagrams Sent/Received` mostraram
  uma única rajada curta (3 enviados, 2 recebidos por segundo) no momento em que a rede do cliente iniciou, e
  0 depois. Não existe log em nenhum cliente, e capturas de janela são pretas, portanto se o cliente
  realmente entrou é **desconhecido**. A rajada é o único indício de uma tentativa de handshake.
- Rastreamento estático da entrada: `SearchSessionByJoinIp`, `SearchSessionId`, `JoinSessionId` são nomes de
  campos registrados em uma tabela de reflexão da classe de parâmetros de busca de sessão (`FUN_100f2980`),
  não a lógica de entrada. A mensagem "Try to join using direct connect but no ip was set." é
  referenciada por um auxiliar de hash de string inicializado sob demanda em `106cb980` (não dentro de uma função
  reconhecida), também não pela lógica. Nada nesta análise explica por que o cliente encerra.
- Observabilidade é o bloqueio real: clientes não têm log (`-logFile` não escreve nada), a janela em
  tela cheia não pode ser capturada e a pasta de perfil é compartilhada com o dono. Ideias, em
  ordem de esforço: (1) pasta de perfil por cópia aplicando patch à string `My Games\Far Cry 2\`
  (offset `0xe089a0` de `Dunia.dll`, 19 bytes), para cada cópia de teste ter seu próprio `GamerProfile.xml` com
  `Fullscreen="0"` (exige novas pastas em `Documents`, aprovação do dono); (2) uma DLL dentro do processo
  (proxy ou carregador de plugins, como FCSE faz) que registre chamadas da engine e depois hospede o código cooperativo.

## <a id="derived"></a>Derivado

- Nada a reviver: nenhum projeto cooperativo de Far Cry 2 apareceu nas três primeiras buscas.
  O caminho é “construir do zero” (playbook/how-coop-mods-work.md).

- Derivado das strings, não da execução do jogo: a engine já replica pawns,
  veículos, projéteis e itens coletáveis com papéis host/controller/third-party, portanto um segundo
  jogador na campanha pode plausivelmente ser uma questão de executar o código de missão individual
  nesse código de rede, como em outras engines que incluem modo deathmatch (consulte
  playbook/triage.md, etapa 5). A lógica de missões provavelmente é Lua.

- Derivado dos arquivos de configuração (não executado): modos de jogo são orientados a dados, e a engine tem
  uma configuração de replicação por serviço. Um modo cooperativo talvez possa ser expresso como um novo `<GameMode>`
  que usa a lista de serviços `FCXSingle` e adiciona `NetPresence` aos serviços que precisam
  ser compartilhados, com o pawn do jogador criado como `PawnHost` / `PawnThirdParty` com rede.
  Se os dados de fase do modo individual (setores, grafos Domino) carregam sob um modo com
  rede não foi testado.

## <a id="guesses"></a>Hipóteses

- FCSE poderia ser o ponto de hook para um plugin nativo. Não verificado.
- O código de rede multijogador em `Dunia.dll` talvez possa ser reutilizado para campanha cooperativa. Não verificado.
- A build individual talvez nem instancie NetworkEngine, portanto uma sessão de campanha
  talvez precise ser iniciada pelo caminho de modo de jogo multijogador. Não verificado.

## <a id="unknown"></a>Desconhecido

- Se existe um projeto cooperativo de Far Cry 2 em Discord, forks/branches do GitHub ou Archive.org
  (ainda não pesquisados; “não encontrado por busca na web” é tudo que pode ser dito até agora).
- Licença do FCSE, versões compatíveis, disponibilidade do fonte (página do Nexus bloqueia WebFetch).
- Como os scripts da campanha e o estado das missões são armazenados.
- (respondido em 2026-10-19) Buscas de `gh issue list` / `gh pr list --state all` por "Far Cry 2",
  "farcry", "Dunia": nenhuma issue e nenhum PR sobre este jogo (PR #2 correspondeu por acaso; é
  sobre Celeste). Issue de reserva aberta: https://github.com/cranebeaker/coop-anything/issues/29
  (o rótulo `in-progress` do modelo não existe no repositório, portanto está sem rótulo).

## <a id="log"></a>Registro

- 2026-10-19: identidade registrada em `local/identity.md` (privado). Instalação copiada para
  `local/test-installs/FarCry2` (187 arquivos, 3.44 GB). Ghidra 12.1.4 baixado da
  versão oficial do GitHub, SHA-256 `ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db`
  correspondeu às notas da versão. Iniciadas importação e análise sem interface de `FC2.dll` e
  `Dunia.dll`.

## <a id="per-copy-profile-folders-and-window-capture-2026-10-19-morning"></a>Pastas de perfil por cópia e captura de janela (2026-10-19, manhã)

O dono aprovou criar pastas de perfil de teste em `%USERPROFILE%\Documents\My Games\`.

Observações (todas executadas):
- `Dunia.dll` tem exatamente uma ocorrência ASCII de `My Games\Far Cry 2\` no offset de arquivo 0xe089a0 (19 bytes). As ocorrências UTF-16 estão em outros 12 lugares, não tocados.
- Cópia A agora usa `My Games\FC2test_A\`, cópia B `My Games\FC2test_B\` (patch de mesmo tamanho; backups `Dunia.dll.before-profile`). Cada pasta contém uma cópia do `GamerProfile.xml` do dono com `ResolutionX=800 ResolutionY=600 Fullscreen=0`. O hash do próprio perfil do dono permaneceu inalterado depois.
- O jogo não escreveu nada nas novas pastas (nenhum arquivo alterado, nenhum arquivo novo).
- Iniciar B normalmente permanece vivo por 45 s com e sem seu arquivo de perfil. Portanto esse teste não mostra se a nova pasta é lida.
- O tamanho da janela no início é 1408x792 (80 % dos 1760x990 do dono), não 800x600. Isso sugere que a engine ainda obtém o tamanho de outro lugar ou o sobrescreve. Desconhecido qual.
- Captura: `PrintWindow` e uma cópia da região da tela (`shot-screen.ps1`, janela trazida à frente) produzem imagem preta da janela D3D, também com `-host`.

Derivado: captura de janela é um caminho sem saída neste ambiente, independentemente do perfil.

Desconhecido: se o novo caminho de perfil é lido; por que a captura é preta (sessão sem área de trabalho real ou swap chain D3D).

Próximo: uma DLL de registro dentro do processo nas cópias de teste (exige um compilador de 32 bits; perguntar ao dono antes de instalar qualquer coisa).

## <a id="in-process-probe-dinput8dll-proxy-first-results-2026-10-19"></a>Sonda dentro do processo (proxy dinput8.dll), primeiros resultados (2026-10-19)

Ferramenta: proxy `dinput8.dll` compilado com o MinGW de 32 bits instalado (gcc 9.2), colocado na pasta bin das duas cópias de teste. Encaminha `DirectInput8Create` à DLL do sistema, espera por `Dunia.dll`, aplica patches à tabela de importações e escreve `coop_probe.log` ao seu lado. Hooks em: `bind`, `connect`, `sendto`, `recvfrom` (ws2_32), `PostQuitMessage` (user32). `ExitProcess` não é importado por `Dunia.dll` (nenhum hook instalado). O fonte da sonda não está neste repositório (o código do jogo fica no próprio repositório do jogo; consulte seu estado no README).

Observações (anfitrião A `-host -login coopbot1 -lan`, cliente B `-join <LAN IP>`, executado uma vez, 60 s):
- O proxy carrega e os 5 hooks são aplicados em ambos os processos. O registro funciona sem captura da área de trabalho.
- Anfitrião A: vincula UDP 9000 e 9001 no endereço LAN (9000 repetido com resultado de já usado, depois ok). Também tenta `connect` a um endereço público na porta TCP 80, que falha (-1).
- Cliente B: vincula 9000, 9001 (falha, porta ocupada por A), depois 9002 e 9003, 9004. Depois `connect` a um endereço público em TCP 80 (falha) e TCP 3074 (falha), sendo 3074 a porta usada pelos antigos serviços online.
- Nenhum processo registrou `sendto` ou `recvfrom` em direção ao outro par. Contadores UDP do sistema mostraram alguns datagramas, portanto existe outro caminho de envio (provavelmente `WSASendTo` ou outro módulo). Desconhecido.
- `PostQuitMessage` não foi chamado durante os 60 s; o cliente permaneceu vivo.

Derivado (não provado): `-join` passa primeiro pelos serviços online encerrados (TCP 80 e 3074); o par LAN nunca é contatado pelas chamadas com hooks. Isso explicaria por que entrar não mostra nada.

Próximo: hooks em `WSASendTo`/`WSARecvFrom`/`WSASend`/`getaddrinfo`/`gethostbyname` e nos caminhos de exceções de primeira chance e de saída; registrar qual módulo chama `connect` (endereço do chamador); depois tentar fazer a engine usar um caminho apenas LAN.

## <a id="probe-round-2-name-resolution-and-callers-2026-10-19"></a>Segunda rodada da sonda: resolução de nomes e chamadores (2026-10-19)

A sonda agora também tem hooks em `WSASendTo`, `WSARecvFrom`, `getaddrinfo`, `gethostbyname` (9 entradas de importação com patches) e imprime módulo+offset do chamador. Mesma configuração (anfitrião A `-host -login coopbot1 -lan`, cliente B `-join <LAN IP>`).

Observações (executado uma vez, 50 s):
- Ambos os processos resolvem o próprio nome do PC muitas vezes no início (`Dunia.dll+0x14200`).
- Anfitrião A: resolve `onlineconfigservice.ubi.com` (`Dunia.dll+0xd928b4`), `connect` ao endereço resultante em TCP 80 falha (`+0xd921d7`). Depois `getaddrinfo("locate.madserver.net")` falha com 11001 (host não encontrado; `+0xc86a27`).
- Cliente B: o mesmo, mais resolve `gconnect.ubi.com` (`+0xc16339`) e tenta `connect` a TCP 3074, que falha.
- Ainda nenhuma chamada de `sendto`, `WSASendTo`, `recvfrom` ou `WSARecvFrom` em nenhum processo, portanto a engine envia seu UDP de outro jeito (desconhecido; talvez uma importação diferente ou sockets em outro módulo).
- Nenhum processo encerrou em 50 s.

Derivado: o caminho `-join` do cliente quer o antigo serviço de conexão Ubisoft (`gconnect.ubi.com:3074`) antes de fazer qualquer coisa na LAN. Esses servidores não existem mais. Portanto a entrada original não pode funcionar como está, e o patch de tipo de rede de `02` para `03` não basta.

Opções (não decididas): (a) fazer a engine pular essa etapa de serviço por patch, (b) emular o serviço localmente (protocolo desconhecido, grande), (c) deixar o código de rede multijogador original como está e executar nosso próprio transporte cooperativo dentro de uma DLL carregada, como outros mods cooperativos fizeram. Recomendação: (c), usando a DLL da sonda como base.

## <a id="lua-channel-into-the-running-game-2026-10-19"></a>Canal Lua para o jogo em execução (2026-10-19)

O fonte da sonda (`probe.c`, `probe.def`; compilação: `gcc -O1 -shared -o dinput8.dll probe.c probe.def -lws2_32 -static-libgcc`, MinGW de 32 bits) não está neste repositório (o código do jogo fica no próprio repositório do jogo; consulte seu estado no README). É um proxy `dinput8.dll` apenas para as cópias de teste. Os RVAs abaixo são para `Dunia.dll` Steam v1.03 (SHA-256 no registro privado de identidade) e precisam ser verificados novamente para qualquer outra build.

Observações (executadas, cópia A no menu principal):
- A linguagem de script é **Lua 4.0** (vinculada estaticamente, sem símbolos): biblioteca base tem métodos `getglobal`, `tag`, `foreach`, `globals`, `copytagmethods`, `_ALERT`. Encontrada na tabela de registro de `dostring` no VA 0x10e3b150 (pares nome, função).
- Endereços da API Lua (cdecl, VA = 0x10000000 + RVA): `lua_gettop` 0x102aa9c0, `lua_settop` 0x102aa9e0, `lua_getglobal(L, name)` 0x102aaf90, `lua_dobuffer(L, buf, size, name)` 0x102ab600, `luaL_check_lstr(L, narg, &len)` 0x102d24b0. Valores Lua ocupam 5 bytes na pilha.
- O ponteiro do estado Lua principal é armazenado em `*(void **)0x11606728` (o auxiliar `FUN_102aa850(0, name, cfunc)` em 0x102aa850 o lê e registra uma função C como global; é assim que a engine registra sua API Lua em `FUN_109fc830` e `FUN_1070f5e0`).
- Executar Lua externamente funciona: a sonda coloca um arquivo `coop_cmd.lua` na pasta do jogo, um hook de `PeekMessage` na thread principal o executa com `lua_dobuffer`, depois lê a global Lua `__out` e a registra. Teste: `__out = "alive " .. (1+2)` retornou `alive 3`. `_ALERT`/`print`/`writeto` não produzem saída visível nesta build (o hook de `_ALERT` nunca disparou), portanto `__out` é o canal de saída.
- 573 globais; 21 são tabelas (`Game`, `System`, `Script`, `Sound`, `CGameMissionMgr`, `CBuddiesManager`, `CFCXRegionManager`, `CDominoConsoleCommandManager`, ...); 246 funções. `Game` tem 98 métodos, entre eles `GetLocalPlayerId`, `IsServer`, `IsLocalPlayer`, `GetEntityTeam`, `SetPlayerId`, `SaveGame`, `LoadNextMap`, `LoadScript`, `Exec`, `MissionSetState`, `SetHealth`, `SelectMainAvatar`, `GetCurrentGameType`, `SendGlobalChatMessage`.
- Globais relacionadas a entidades: `TeleportEntity(entity, destEntity)`, `SpawnEntityFromArchetype`, `RemoveEntity`, `IsEntityValid`, `IsEntityLoaded`, `GetEntityName`, `GetInvalidEntityId`, `KillPawnAgent`, `SetVisibility`, `GameChangeWorld`. Nenhuma função de script retorna a posição de uma entidade.
- `net_log_enable` / `net_log_disable` e `debug_envNetwork` existem como variáveis de console, possivelmente um log de rede interno (não testado).
- O nativo por trás de `TeleportEntity` (`FUN_109fb530`) não move nada por si só: constrói um evento de rede com campos `entityId` e `destId` e o envia pelo sistema de eventos. Muitas operações de script parecem ser eventos de rede (consulte também `CFCXTeleportEntityOperation`).

Derivado (não provado): cooperativo poderia ser construído sobre esse sistema de eventos (operações de script são eventos com papel host/controller), em vez de replicação bruta de objetos; um getter de posição precisa de código nativo (busca de entidade por id), porque a API de script não tem um.

Desconhecido: a tabela nativa de entidades e como um id mapeia para um objeto de entidade; onde a posição de um pawn é armazenada; quais eventos já são replicados em um modo de jogo com rede.

Próximo: (1) descompilar a busca de entidade por id e a posição de pawn (começar pelos nativos de `IsEntityValid` e `GetLocalPlayerId`); (2) testar `net_log_enable` para ver se a engine registra seus próprios eventos de rede; (3) testar se um mundo de campanha carrega quando o tipo de jogo é trocado via `Game:LoadLevel`/`GameChangeWorld` enquanto a sonda executa.

## <a id="entity-lookup-and-why-a-loaded-world-is-needed-2026-10-19"></a>Busca de entidades e por que é necessário um mundo carregado (2026-10-19)

Observações (estáticas, Ghidra em `Dunia.dll` Steam v1.03; VA = 0x10000000 + RVA):
- Ids de entidades são de **64 bits**. Lua os recebe como strings decimais (interpretadas com `sscanf "%llu"` no wrapper compartilhado `FUN_1058f250`). O id inválido é 0xFFFFFFFFFFFFFFFF; no menu principal `GetLocalPlayerId()` retorna `18446744073709551615` e `IsEntityValid` é falso (executado).
- A busca de entidade por id é `FUN_10055820` (thiscall; `ECX = *(void **)0x11644e80`, gerenciador de entidades; argumentos na pilha: ponteiro de saída, parte baixa do id, parte alta do id). Retorna um holder com contagem de referências; `holder+8` é a contagem e `holder+0xC` o objeto de entidade (0 se não encontrado). `IsEntityValid` então testa o bit 4 do dword de flags do objeto em `+0x70` (inválido quando definido).
- O nativo de `GetLocalPlayerId` é `FUN_1058fa00` (chama `FUN_1058f8c0`, que lê uma lista de `DAT_11645578`).
- Nativos Lua são registrados por `FUN_102aa850(0, name, cfunc)`, em lotes em `FUN_10591120` (entidades), `FUN_109fc830` (jogabilidade) e `FUN_1070f5e0` (console).

Ferramentas: a sonda recebeu comandos nativos (`coop_native.txt`: `peek <hexaddr> <len>`, `ent <id> <len>` com uma coluna float). Compilados e implantados, ainda não executados contra uma entidade real.

Tentativas de carregar um mundo de campanha sem o menu (todas executadas, nenhuma carregou um mundo; memória permaneceu estável, id de jogador local permaneceu inválido):
- `Game:LoadLevel("w1_b_2")` de Lua: erro de execução (status 1); `LoadLevel` é um modelo de console, não um método da tabela `Game`.
- `GameChangeWorldDefaultSpawnPoint("w1_a_1")`: executa sem erro, nada carrega no menu.
- `-benchmark -world w1_a_1`: nada visível carregou após 75 s (nome do mundo pode estar errado).

Bloqueio: não existe salvamento de campanha no perfil do dono, portanto `-load` não tem o que carregar, e o menu não pode ser clicado sem janela visível.

## <a id="getting-a-world-loaded--load-and-menu-keys-2026-10-19-later"></a>Carregar um mundo: `-load` e teclas de menu (2026-10-19, mais tarde)

O dono jogou até o primeiro salvamento; o salvamento é `Saved Games\<number>.sav` (1.1 MB) no perfil. Uma cópia somente leitura está no espaço de trabalho privado e nas duas pastas de perfil de teste (subpasta `Saved Games`). O arquivo de perfil do dono mudou (sua partida); perfis de teste foram atualizados a partir dele com `Fullscreen=0`, 800x600.

Observações (executadas):
- A sonda agora tem hooks em `CreateFileA/W` (caminhos contendo `av`, `Saved`, `Documents`, `Profile`). `-load <arg>` abre `<profile>\Saved Games\<arg>` literalmente, sem adicionar extensão: `-load 1624175031227` falha ao abrir, `-load 1624175031227.sav` abre corretamente.
- Após uma abertura bem-sucedida, o processo ainda encerra em ~3 s com código 0, sem `PostQuitMessage`, sem erro. Portanto `-load` não inicia a campanha a partir de um `.sav` normal nesta build (talvez seja um caminho de desenvolvedor para outro tipo de salvamento; o tratador lê uma chave `PlayerPos`). Motivo desconhecido.
- Enviar teclas Enter para a janela do jogo com `SendKeys` moveu o conjunto de trabalho de 144 MB (tela inicial) para cerca de 180 MB (menu), mas nunca produziu um id válido de jogador local. Essa abordagem é cega e pode digitar na janela que estiver em foco, portanto foi abandonada e o script excluído.
- Uma captura de toda a área de trabalho funciona nesta sessão (mostrou a área de trabalho real do dono, portanto foi excluída imediatamente e não deve ser usada novamente). A própria janela do jogo continua não podendo ser capturada.

Desconhecido: como Continue do menu inicia uma campanha; se um ponto de entrada Lua ou nativo faz isso diretamente.

## <a id="first-live-entity-dump-the-player-2026-10-19"></a>Primeiro dump de entidade em execução: o jogador (2026-10-19)

Preparação: o dono iniciou manualmente a cópia de teste A (perfil próprio `FC2test_A`, em janela), pressionou Continue e ficou no mundo. O canal Lua e o comando `ent` da sonda executaram nesse processo.

Observações (executado uma vez, um dump, jogador parado):
- `GetLocalPlayerId()` = `13072524568650856960`, `IsEntityValid` = verdadeiro, `GetEntityName` = `player.MainCharacter.PawnPlayer.<character name>`, `Game:IsServer()` = verdadeiro e `Game:GetCurrentGameType()` = 0 na campanha individual.
- O objeto de entidade (id de 64 bits -> holder -> objeto em `holder+0xC`) começa com o ponteiro de vtable em `+0x00`. Em `+0x30` há uma matriz float 4x4, por linhas, 16 bytes por linha: linhas 0–2 parecem uma rotação (linha 0 `-0.664 0.748 0 0`, linha 1 `-0.748 -0.664 0 0`, linha 2 `0 0 1 0`), linha 3 em `+0x60` é `(2801.552, 2884.597, 17.0, 1.0)`.
- O dword de flags da entidade em `+0x70` não foi isolado neste dump; a leitura estática anterior de `IsEntityValid` usou as flags no objeto retornado pela busca (bit 4).

Derivado (ainda não provado): `obj+0x60..0x68` é a posição no mundo (x, y, z com z para cima) e linhas 0–1 fornecem a orientação horizontal. Precisa de um segundo dump após mover o jogador para confirmar.

Próximo: segundo dump após mover; depois escrever um leitor e um setter de posição (um setter talvez precise passar pelo evento de teletransporte da engine em vez de escrever a matriz, pois a física e a camada de rede rastreiam a entidade).

## <a id="second-dump-position-confirmed-2026-10-19"></a>Segundo dump: posição confirmada (2026-10-19)

Observação (executada): após o dono andar para frente e girar a câmera, a mesma entidade (mesmo id, mesmo endereço de objeto, `refs` 76 -> 77) mostrou a linha 3 da matriz em `+0x30` mudar de `(2801.552, 2884.597, 17.000)` para `(2781.723, 2869.039, 17.002)` (cerca de 25 m), e linhas 0–1 mudaram de `(-0.664, 0.748)/(-0.748, -0.664)` para `(0.763, 0.646)/(-0.646, 0.763)`; as linhas permanecem ortonormais.

Derivado (sustentado pelos dois dumps): a transformação do jogador no mundo é uma matriz float 4x4 por linhas em `entity+0x30`; posição = `+0x60`, `+0x64`, `+0x68` (z para cima), orientação horizontal de `atan2(row0.y, row0.x)`. O endereço da entidade permanece igual enquanto ela vive.

Atualização da sonda: novos comandos nativos `pos <id>` (registra posição e direção), `setpos <id> x y z` (escreve os três floats; efeito na física desconhecido, talvez volte à posição anterior) e `poke <hexaddr> <hex32>`. Ainda não executados.

## <a id="setpos-test-writing-the-matrix-does-not-stick-2026-10-19"></a>Teste de setpos: escrever a matriz não persiste (2026-10-19)

Observação (executada, dono no mundo, jogador parado): `pos` retornou `(2806.237, 2886.508, 17.262)`. `setpos` escreveu `(2814.0, 2886.5, 17.3)` em `entity+0x60..0x68`. Quatro leituras nos ~3 s seguintes retornaram os valores originais todas as vezes; a primeira leitura veio ~2.7 s após a escrita por causa do intervalo de processamento de comandos, portanto a engine restaurou o valor dentro desse tempo (ou antes do próximo quadro).

Derivado (não provado): a matriz da entidade é recalculada a cada quadro de outra origem (corpo físico ou controlador de pawn), portanto escrevê-la diretamente não move o pawn. Desconhecido: o que o dono viu na tela.

Próximas opções: (a) encontrar o objeto de origem (um ponteiro de física ou controlador dentro da entidade, por exemplo os campos perto de `+0x9c` e `+0x1c0`) e escrever ali, (b) usar o evento de teletransporte da engine (`TeleportEntity(entity, destEntity)`), que precisa de uma entidade de destino posicionada onde queremos, (c) escrever a cada quadro de um hook logo após a atualização da engine.

## <a id="per-frame-hold-test-2026-10-19"></a>Teste de manutenção por quadro (2026-10-19)

Observação (executada, dono no mundo, parado): `hold` escreveu a posição da matriz (+8 m em x) em cada chamada de `PeekMessage` da thread principal por 8 s (1168 ticks, cerca de 146 chamadas por segundo). No início de cada tick a sonda registrou o que a engine havia deixado: em 5 dos primeiros 8 ticks, o valor original tinha voltado; o valor escrito sobreviveu apenas nos ticks em que `PeekMessage` executou várias vezes entre duas atualizações da engine (ticks 9, 10, 840, 960). `pos` após `unhold` era o original novamente.

Derivado: a engine recalcula a matriz da entidade de outra origem em cada atualização, e uma escrita do laço principal não persiste. A observação do dono sobre o que a tela mostrou está pendente.

Próximo: procurar a origem (corpo físico ou objeto de controlador referenciado pela entidade, como os ponteiros perto de `+0x9c`, `+0x1c0` e `+0x1d4`; os 3–4 ponteiros vistos no dump) e escrever ali; ou enviar o próprio evento de teletransporte da engine.

## <a id="where-the-player-position-really-lives-2026-10-19"></a>Onde a posição do jogador realmente fica (2026-10-19)

Método (executado): varreduras de memória pelo par float (x, y) do jogador em duas posições paradas diferentes, separadas por cerca de 14 m, janelas de 4 e 16 bytes, tolerância 0.01; os endereços presentes nas duas varreduras (valor mudou do antigo para o novo no mesmo endereço) são os candidatos em uso. Depois cada candidato recebeu uma escrita de `x + 6`, um por vez, e a posição da entidade (`pos`) foi lida após 1.2 s.

Observações:
- Varredura 1: 66 ocorrências; varredura 2: 54; 45 endereços em ambas. 17 deles acompanham o z do jogador. Os outros 28 têm z de 11–13 ou -1000005 (valores iniciais típicos de caixa delimitadora) e não foram testados.
- 16 dos 17 endereços que acompanham z são cópias passivas: escrever neles deixa `pos` inalterado, incluindo a cópia dentro da entidade em `entity+0x140`.
- Escrever `x + 6` no endereço de heap `3C22A050` (primeiro float de uma struct: x, y, z, depois um float pequeno; os próximos grupos de 12 bytes contêm outras posições) moveu a posição da entidade em exatamente +6, o valor permaneceu e escrever o x antigo de volta o restaurou. Portanto essa struct é a origem da qual deriva a matriz da entidade em `+0x60`. Um segundo teste (+8 m por 6 s e volta) também teve efeito em `pos`. O que o dono viu na tela está pendente.
- O endereço é de heap e muda entre sessões; não é um offset fixo.

Derivado: o jogador pode ser movido escrevendo x, y, z nessa struct de origem uma vez (sem necessidade de manutenção por quadro). Para usá-la em um mod, a struct deve ser encontrada a partir da entidade por uma cadeia de ponteiros, não por varredura.

Próximo: encontrar quem aponta para `3C22A050` ou para o início de sua struct (varredura de ponteiros por dwords em `3C22A000..3C22A050`), depois encontrar a cadeia a partir do objeto de entidade.

## <a id="pointer-chain-from-the-entity-to-the-position-matrix-2026-10-19"></a>Cadeia de ponteiros da entidade à matriz de posição (2026-10-19)

Método (executado, no processo em execução, apenas leitura): varredura reversa por ponteiros para `3C22A000..3C22A050`, depois busca em largura por dwords que parecem ponteiros (alinhados, faixa de heap, fora da imagem de `Dunia.dll`) a partir do objeto de entidade do jogador. Ferramentas (privadas): `local/scripts/memscan.ps1`, `local/scripts/ptrchain.ps1`.

Observações:
- A struct em `3C22A020` é uma matriz de transformação 4x4: rotação identidade nas primeiras três linhas e posição na linha 3 (`+0x30` a partir do início da matriz). Suas vizinhas em `3C22A060/70` contêm outras posições (provavelmente valores anteriores e de destino).
- Outro objeto contém a mesma posição como três pontos (posição, +0.45 m, +1.35 m) e um ponteiro para a matriz; isso parece a cápsula do controlador de personagem.
- A BFS encontrou cadeias na profundidade 5–6. A mais curta: `entity+0x9C -> A; A+0x140 -> B; B+0x140 -> C; C+0x34 -> D; D+0x18 -> matrix`. Outras cadeias alcançam a mesma matriz, portanto ela é compartilhada por vários donos.
- O dono confirmou que o personagem realmente se moveu na tela ao escrever a posição ali (como teletransporte, não caminhada).

Derivado (ainda não verificado em uma segunda sessão): os offsets `9C, 140, 140, 34, 18` talvez sejam estáveis entre sessões, pois vêm do layout de objetos, não de endereços.

Atualização da sonda: `follow <id> <hex offsets...>` segue a cadeia e registra a posição da matriz ao lado da posição da entidade; `tp <id> x y z <hex offsets...>` escreve a posição no fim da cadeia. Compilado e implantado, ainda não executado.

## <a id="the-pointer-chain-was-not-stable-the-physics-body-is-2026-10-19"></a>A cadeia de ponteiros não era estável; o corpo físico é (2026-10-19)

Observações (executadas, segunda e terceira sessões, mesmo salvamento):
- `entity+0x9C` aponta para um array de ponteiros, não um componente. Seguir ligações `+0x140` levou a tipos diferentes de objetos na nova sessão (uma etapa caiu em um registro que contém uma string de nome de tabela), portanto a cadeia `9C,140,140,34,18` da sessão anterior **não** é estável. `follow` informou "chain broken at step 3".
- `Dunia.dll` contém nomes RTTI e classes de física Havok (`hkpRigidBody`, `hkpCharacterRigidBody`, `hkpCharacterProxy`, `hkpCapsuleShape`). O objeto encontrado anteriormente (`3C229F80` na sessão 2) tinha vtable `10E67658` (RVA `0xE67658`, estática). Seu layout corresponde a `hkpRigidBody`: `+0` vtable, `+4` contagem de referências/tamanho, `+8` ponteiro de mundo, `+0xC` dados do usuário, `+0x10` forma, `+0x18` ponteiro do colidível para a transformação de movimento.
- Na terceira sessão, uma varredura de memória por dwords iguais a `10E67658` encontrou exatamente **uma** instância (`3B183DC0`). Seu `+0x18` aponta para `3B183E60`, uma rotação identidade seguida (em `+0x30`) pela posição `(2806.967, 2886.745, 17.258)`, igual à posição da entidade lida por `pos`. A próxima linha contém outra posição (valor anterior ou destino).
- Portanto a regra “encontrar a instância da classe com vtable RVA `0xE67658` cuja matriz de movimento está perto da posição da entidade” funcionou em duas sessões.

Derivado: o corpo rígido do jogador pode ser encontrado por classe e posição; escrever a translação de sua matriz de movimento move o jogador (confirmado anteriormente no endereço de heap; o dono viu teletransportes).

Desconhecido: se NPCs usam a mesma classe (aqui existia apenas uma instância, portanto provavelmente não); como dar a um segundo pawn seu próprio corpo físico; o que o ponteiro de mundo em body+8 oferece (iterar todos os corpos).

Sonda: `findbody <id>` varre pela classe e armazena o corpo correspondente em cache, `posb` o lê, `tpb x y z` escreve nele. Compilado, ainda não executado em uma sessão.

## <a id="findbody--tpb-verified-in-a-fresh-session-2026-10-19"></a>findbody / tpb verificados em uma nova sessão (2026-10-19)

Observação (executada, dono no mundo): `findbody` encontrou exatamente um corpo (`3A115AC0`, matriz `3A115B60`) perto da posição da entidade; `tpb` para +5 m em x moveu a entidade para essa posição (`pos` e `posb` concordaram, z se acomodou de 17.3 para 17.27), e `tpb` de volta a restaurou (z 17.259). Esta é a terceira sessão seguida em que a classe `RVA 0xE67658` identificou o corpo do jogador; os endereços de heap eram diferentes a cada vez.

## <a id="own-udp-transport-between-two-copies-position-exchange-works-2026-10-19"></a>Transporte UDP próprio entre duas cópias: troca de posições funciona (2026-10-19)

Preparação: a sonda abre seu próprio socket UDP não bloqueante (loopback, portas 9101 e 9102, não as portas da engine 9000–9004; as importações da engine têm hooks, mas as chamadas da própria sonda não). Cada cópia envia um pacote de 28 bytes (assinatura, sequência, posição x/y/z da matriz do corpo rígido do jogador, direção da linha 0 da matriz da entidade) a cada cerca de 50 ms quando seu laço principal executa (foram observados cerca de 16 pacotes/s) e consulta o socket no mesmo hook do laço principal. Comando: `netstart <localport> <peerip> <peerport> <entity id>`; o id de entidade do personagem principal é igual em ambas as cópias porque carregam o mesmo salvamento.

Observações (executadas, dono com ambas as cópias no mundo, em janela, executando ao mesmo tempo):
- Após `netstart` em ambas, `rx` cresceu nos dois logs (cerca de 16 pacotes/s em cada direção, idades de 0–63 ms) e `remote` de cada cópia era igual a `local` da outra (A viu `2806.26 2886.47`, posição da própria B, e vice-versa).
- Um teletransporte `tpb` do jogador na cópia A por +6 m em x apareceu no `remote` da cópia B até a próxima linha de log (`2812.10 2886.62`), e teletransportar de volta mostrou `2806.11` novamente.
- Duas cópias executam no mundo ao mesmo tempo sem falha durante todo o teste (cerca de 2 minutos).

Derivado: para um protótipo apenas de posição, transporte e lado de leitura estão prontos. Falta o avatar remoto na cópia receptora: um segundo pawn que possa ser movido sem a IA ou física da engine movê-lo de volta, mais animação, armas e vida.

## <a id="a-second-pawn-can-be-spawned-and-moved-without-the-ai-interfering-2026-10-19"></a>Um segundo pawn pode ser criado e movido sem interferência da IA (2026-10-19)

Observações (executadas, apenas cópia A, dono no mundo, parado):
- `SpawnEntityFromArchetype(name, x, y, z, rx, ry, rz)` (sete argumentos: uma string e seis números; encontrado lendo as verificações de argumentos do nativo, `FUN_10590da0`) retorna o novo id de entidade; um nome desconhecido retorna `18446744073709551615` e `IsEntityValid` é falso.
- Passar o nome da própria entidade do jogador (`GetEntityName(GetLocalPlayerId())`, aqui `player.MainCharacter.PawnPlayer.<character>`) como nome de arquétipo criou uma segunda entidade válida na posição dada (`2810, 2886`, z 17.275 após acomodar). `GetLocalPlayerId()` permaneceu igual.
- O novo pawn tem um corpo rígido da mesma classe que o do jogador (vtable RVA `0xE67658`); `findbody` encontrou exatamente uma correspondência perto dele.
- O pawn ficou parado por 4 s (sem deriva de IA) e `tpb` o moveu para quatro cantos de um quadrado de 4 m (posições relidas corresponderam dentro de 0.4 m, z dentro de 0.3 m). Se o dono o viu se mover na tela está pendente.
- O sistema de companheiros (`GetBuddiesManager():SpawnBuddy`) não era utilizável neste ponto da campanha: `GetBuddyList()` tem duas entradas vazias e nenhum companheiro está desbloqueado.

Atualização da sonda (compilada, ainda não executada): `findbody` usa a correspondência mais próxima em vez da primeira; `lua_eval` executa Lua de C e retorna `__out`; assim que chega o primeiro pacote do par, a cópia receptora cria um avatar na posição do par, vincula seu corpo e o move a cada quadro em direção à posição recebida (suavização exponencial de 25 % por quadro, ajuste imediato acima de 6 m); `netstop` remove o avatar com `RemoveEntity`.

## <a id="owners-view-of-the-spawned-avatar-2026-10-19"></a>Visão do dono sobre o avatar criado (2026-10-19)

Observação (dono, na tela, cópia A, avatar movido por `tpb` cerca de 4 vezes por segundo ao longo de um círculo de raio 2–2.5 m): o segundo personagem era visível, movia-se pelo círculo em saltos (teletransportes), e a cada vez aparecia um pouco acima do chão e depois caía, repetidamente.

Derivado: o avatar é um pawn real e renderizado. Os saltos vêm da baixa taxa de atualização (o teste escreveu quatro posições por segundo) e a queda do mundo físico aplicando gravidade entre duas escritas (eu havia colocado o avatar 5 cm acima do z do jogador). Escrever a posição em cada quadro do laço principal (cerca de 140 por segundo) deve ocultar ambos; a verificar com a suavização por quadro incorporada à sonda.

## <a id="avatar-over-the-network-first-look-2026-10-19"></a>Avatar pela rede: primeira visão (2026-10-19)

Observação (executada, ambas as cópias no mundo ao mesmo tempo, dono olhando apenas a cópia B; jogador da cópia A movido por `tpb` ao longo de um círculo de 4 m, cerca de 4 passos por segundo):
- Ambas as cópias criaram por conta própria um avatar do par após o primeiro pacote e então vincularam seu corpo após algumas tentativas (o corpo aparece alguns segundos após a criação): `avatar spawned`, `findbody` 0 correspondências várias vezes, depois 1 correspondência, `avatar body bound`.
- Dono: o avatar era visível em B e seguia o círculo de A; movia-se por teletransportes, não caía nem quicava como antes e permanecia em pose ociosa (sem animação de caminhada).

Derivado: a escrita por quadro corrigiu a queda. A aparência de teletransporte pode vir do próprio teste (o jogador de origem só mudava de posição 4 vezes por segundo), não do receptor. A pose ociosa é esperada, pois apenas a posição é escrita; a animação de locomoção precisa de outra entrada (velocidade ou controlador).

Atualização da sonda (compilada, ainda não executada): `walk <radius> <seconds> <speed>` move o corpo local em um círculo a cada quadro (para testar suavidade com origem contínua); `avvel x y z <hex offset>` e `bodyvel x y z <hex offset>` escrevem três floats no avatar ou no corpo em cache em um offset (para testar se um campo de velocidade controla movimento e animação).

## <a id="copy-b-crashed-after-the-avatar-spawn-2026-10-19"></a>Cópia B falhou após criar o avatar (2026-10-19)

Observação (executada): em uma das execuções com duas cópias, a cópia B encerrou logo após `avatar spawned` (o log desse processo termina ali; sem `avatar body bound`, sem mais linhas `net:`). O dono confirmou que o jogo falhou e o reiniciou. O log de aplicativos do Windows não tinha entrada. A execução anterior com a mesma versão da sonda (o caminho de criação do avatar) não falhou em nenhuma cópia.

Derivado (hipótese, não provada): `findbody` percorria cada região de leitura/escrita comprometida com leituras diretas. Se outra thread da engine libera ou descompromete uma página entre `VirtualQuery` e a leitura, essa leitura causa falha e mata o processo; o corpo do avatar só aparece alguns segundos após a criação, portanto a varredura executa várias vezes justamente quando a engine está ocupada criando-o.

Atualização da sonda: `findbody` agora copia memória em blocos de 64 KiB com `ReadProcessMemory` (uma leitura malsucedida pula o bloco em vez de falhar), e um registrador de exceções escreve qualquer violação de acesso (código, módulo e offset, endereço) e um registro final de falha em `coop_probe.log`. Compilado, ainda não executado nas duas cópias.

## <a id="game-over-after-the-continuous-walk-2026-10-19"></a>“Game over” após a caminhada contínua (2026-10-19)

Observação (executada, ambas as cópias no mundo com seus avatares, sem falha desta vez): a troca funcionou (cerca de 16 pacotes/s em ambos os sentidos) e ambos os avatares foram criados e vinculados. Depois `walk 4 40 2.5` fez o jogador da cópia A se mover em um círculo de 4 m por escritas por quadro da matriz de seu corpo rígido com z fixo. O dono então viu a tela “Game over” em **ambas** as cópias. As verificações de validade de entidade (`IsEntityValid`, `IsEntityLoaded`) ainda eram verdadeiras para ambos os jogadores e avatares, portanto as entidades não foram removidas.

Derivado (hipóteses, não provadas): o z fixo não acompanha o terreno, portanto o corpo fixado é empurrado para dentro ou mantido acima do chão e recebe dano de queda ou penetração; em A é o jogador local, em B é o avatar de A (que recebe o mesmo z). O jogo parece tratar o avatar, criado do arquétipo do personagem principal, como personagem principal, portanto sua morte encerra a missão para ambos.

Atualização da sonda (compilada, ainda não executada): após criar o avatar, a sonda envia `CFCXCountersComponent_SetInvincible` para ele (o evento usado pelos scripts para `PawnInvincibleState`, via `CDominoManager_GetInstance():SendRegisteredEventToEntity`).

## <a id="smooth-avatar-no-game-over-with-invincibility-2026-10-19"></a>Avatar suave, sem Game over com invencibilidade (2026-10-19)

Observação (executada, ambas as cópias no mundo; jogador local da cópia A tornado invencível manualmente, ambos os avatares definidos como invencíveis pela sonda logo após a criação; jogador da cópia A movido por escritas por quadro em um círculo de 3 m a 2 m/s por 30 s): o dono observou a cópia B: o avatar de A percorreu o círculo suavemente, sem cair ou quicar, e sem Game over em nenhuma cópia.

Derivado: o Game over anterior foi morte (dano) de um pawn fixado, não efeito do avatar ou da camada de rede. Movimento suave precisa de escritas por quadro mais suavização (cerca de 140 atualizações/s do hook do laço principal, 16 pacotes/s do par).

## <a id="layout-of-the-pinned-avatars-body-2026-10-19"></a>Layout do corpo do avatar fixado (2026-10-19)

Observação (executada, cópia B, avatar de A movendo em círculo por escritas por quadro; 400 bytes de body+0x80): o corpo rígido em `3911C5C0` tem a transformação de movimento (linhas de rotação, depois posição) em `body+0xA0`; as duas linhas de 16 bytes logo depois (`+0xE0`, `+0xF0`; valor em `+0xD0` é a posição atual) ainda contêm a posição onde o avatar foi **criado** (`2799.274 2877.071 17.031`), enquanto a transformação contém a atual, portanto a cópia de movimento “swept” do mundo físico está desatualizada. Os bytes após `body+0x180` parecem dados empacotados ou codificados, não floats; nenhum vetor óbvio de velocidade foi encontrado neste bloco.

Desconhecido: onde ficam velocidade do personagem, entrada de animação e entrada do controlador; o caminho de jogador remoto da própria engine (`NetObject.PawnThirdParty`, `PawnHost`, `PawnController`) provavelmente os alimenta. O avatar atualmente fica em pose ociosa enquanto desliza.

## <a id="walking-through-a-tree-other-archetypes-and-where-heading-and-animation-might-come-from-2026-10-19"></a>Atravessar uma árvore, outros arquétipos e possíveis origens de orientação e animação (2026-10-19)

Observações:
- Dono: durante o teste `walk`, o personagem em movimento atravessou uma árvore. Esperado e intencional no teste: a posição é escrita no corpo rígido a cada quadro, portanto a colisão é ignorada. No jogo normal, a posição real do par já inclui suas colisões, portanto um avatar fantoche não precisa delas.
- `gamemodesconfig.xml` (`PlayerService`) lista treze arquétipos de pawn jogáveis: `player.MainCharacter.PawnPlayer` e `player.MainCharacter.PawnPlayer.<Andre_Hyppolite|Flora_Guillen|Frank_Bilders|Hakim_Echebbi|Josip_Idromeno|Marty_Alencar|Michele_Dachss|Nasreen_Davar|Paul_Ferenc|Quarbani_Singh|Warren_Clyde|Xianyong_Bai>`, e os multijogador (`player.MainCharacter.PawnPlayerNetworkKit...`).
- Criar `player.MainCharacter.PawnPlayerNetworkKit` no jogo individual retornou id inválido (não disponível neste modo de jogo). Criar `...PawnPlayer.Frank_Bilders` funcionou (id válido) e, segundo o dono, parecia o mesmo personagem que Marty ("stands next to me and looks the same").
- `fcx.netobject.xml` / `engine.netobject.xml` definem a própria replicação de pawns da engine: `NetObject.PawnController` (snapshot de estado `CPawnControllerMemento`, mais mensagens: reload, shoot, fire_bullet, enter vehicle, use equipment, process landing ...), `NetObject.PawnHost` (`CPawnHostMemento`, mementos de munição do inventário e equipamento) e `NetObject.PawnThirdParty` (`CPawnThirdPartyMemento`), controlados por `CPawnNetworkComponent`.
- Orientação: a direção da entidade (linha 0 da matriz em entity+0x30) mudou apenas de `(0.986, -0.164)` para `(0.967, -0.253)` quando o dono girou a câmera cerca de 90 graus parado, portanto a orientação do corpo do pawn não acompanha a câmera quando parado. Uma busca em duas varreduras pelo par de orientação deu 53 endereços comuns às duas; um teste de escrita por força bruta neles foi executado com um erro de script (uma função com nome igual ao alias `Dir`), portanto não mediu nada e, para 244 candidatos, deixou o valor de teste (0, 1) na memória até a engine sobrescrevê-lo; a cópia A continuou executando normalmente.

Derivado: posição pode ser imposta externamente (feito), mas orientação e estado de animação ficam nos próprios componentes do pawn, e a fonte de verdade mais limpa é o layout de `CPawnControllerMemento` e `CPawnThirdPartyMemento`. Ler seu código de serialização no Ghidra é a próxima etapa concreta. A colisão do fantoche não é necessária.

## <a id="pawn-memento-classes-in-ghidra-2026-10-19"></a>Classes de memento de pawn no Ghidra (2026-10-19)

Método (estático, Ghidra em `Dunia.dll` Steam v1.03): referências cruzadas dos nomes de classes `CPawnControllerMemento`, `CPawnThirdPartyMemento`, `CPawnNetworkComponent`, depois a função de registro de classes `FUN_10044de0` (pares nome + fábrica), as fábricas e a vtable do memento de controlador.

Observações:
- Os nomes são registrados com fábricas: `CPawnControllerMemento` -> `FUN_10040090` (aloca `0x130` bytes, construtor `FUN_100b1fe0`, vtable `10E176C8`); `CPawnThirdPartyMemento` -> `FUN_10040110` (aloca `0x278` bytes, construtor `FUN_100b3ef0`). Getters de descritores de classe são `FUN_100b2080` e `FUN_100b3a70`.
- O memento de controlador é construído de cerca de onze subobjetos tipados nos offsets `0x70, 0x84, 0x98, 0xac, 0xc0, 0xd4, 0xe8, 0xfc, 0x108, 0x114, 0x120`; seu método de serialização (`vtable[2]`, `100b2000`) chama a mesma função virtual (slot 1) em cada um deles. Os tipos dos subobjetos decidem quais são os campos (ainda não decodificados).

Derivado: o estado sincronizado do pawn (orientação, locomoção, postura) é armazenado nesses campos tipados de rede e alimentado por `CPawnNetworkComponent`; usá-lo externamente significa executar a própria camada de rede da engine no modo individual (o caminho de sessão de `NetworkEngine`, que também precisa dos serviços Ubisoft encerrados ou de um substituto local), ou encontrar quais campos nos componentes do pawn contêm orientação e velocidade e escrevê-los a cada quadro. Ambos são esforços maiores que o fantoche de posição; nenhum atalho barato foi encontrado.

Estado ao fim desta etapa: o fantoche de posição funciona (suave, invencível, criado automaticamente, nos dois sentidos), mas não tem animação de caminhada, orientação nem armas.

## <a id="walking-animation-where-the-locomotion-data-lives-2026-10-19"></a>Animação de caminhada: onde ficam os dados de locomoção (2026-10-19)

Método (executado, apenas leitura, na cópia de teste em execução): snapshots do grafo de ponteiros do pawn (busca em largura a partir do objeto de entidade do jogador, profundidade 4, primeiros 0x200 bytes de cada objeto, cerca de 35.000 a 39.000 objetos, 18 a 20 MB cada) obtidos duas vezes parado e duas enquanto o dono segurava W; depois os campos iguais nos dois snapshots parados, iguais nos dois andando e diferentes entre os dois estados. Ferramenta (privada): `local/scripts/snapgraph.ps1`.

Observações:
- 113.098 campos atenderam à regra (o heap muda continuamente); os legíveis se agrupam em poucos objetos. O alcançado pela cadeia mais curta é `entity+0x9C` (profundidade 1). Em seu `+0x110..0x118` há um vetor de 3 floats que lê cerca de `(0.003, -0.032, 0.066)` parado e `(2.72, 0.59, 1.76)` andando; em `+0x120..0x134`, uma caixa que lê `(99999, 99999, 99999, -99999, -99999, -99999)` parado (caixa vazia) e números reais andando; em `+0x1E0..`, um bloco que muda de tipo entre os estados (parece texto parado, floats `-0.11, -0.01, 1.40, -0.18` andando). Outros objetos (alcançados na profundidade 3 a 5) mostram conjuntos de flags 0/1 que alternam entre os estados.
- A mesma cadeia em um avatar criado por script leva a outro tipo de objeto (valores e layout diferentes; coordenadas de outras coisas). Portanto `entity+0x9C` não é um slot fixo de “componente de movimento” para todo pawn; o avatar feito do arquétipo do jogador não tem nenhum dos dados do lado controlador que o jogador real tem.
- Todos os arquétipos de pawn multijogador encontrados na configuração (`player.MainCharacter.PawnPlayerNetwork.RedVIP`, `...PawnPlayerNetworkKit`, `.Agent`, `.Assault.Level1`, `.CQB.Level1`) retornaram id inválido ao serem criados na campanha. Apenas os arquétipos `PawnPlayer.*` são criados. Nenhum nome de arquétipo de pawn de IA aparece no texto da configuração ou Lua extraídos (entidades de fase são chamadas `Pawn.Enemy.C` e similares, que são nomes de instância, não arquétipos).
- Escrever o vetor de caminhada no avatar não foi tentado: seu objeto não tem esse layout.

Derivado: dados de locomoção pertencem ao lado controlador de um pawn controlado por jogador, que um pawn `PawnPlayer.*` criado por script não recebe. Opções restantes: (a) encontrar um arquétipo de pawn de IA e deixar o próprio comando `MoveTo` da engine fazê-lo andar para um alvo móvel (animação e colisão naturais, mas atraso e comportamento de IA); (b) decodificar `CPawnControllerMemento` e alimentar o caminho de terceiro da engine; (c) aceitar um fantoche em pose ociosa. Nenhuma foi tentada.

## <a id="second-pc-profile-patch-correction-two-copies-avatar-body-fix-2026-10-24"></a>Segundo PC: correção do patch de perfil, duas cópias, correção do corpo do avatar (2026-10-24)

Identidade (segundo PC): Steam, app 19900, build id 52164, `PatchNotes.txt` "v1.03"; `Dunia.dll`
SHA-256 `6353936a...2765`, 20.183.176 bytes (idêntica ao arquivo acima); Windows 11 23H2, 64 bits.
Duas cópias de teste da instalação; a instalação e o perfil do dono foram apenas lidos. Sonda compilada de
fc2-coop-probe `583772f` com winlibs i686 gcc 9.5.0 (nenhuma build 9.2 com hash disponível; o arquivo da versão 9.5.0
correspondeu a seus SHA-256 e SHA-512 publicados). Antes de cada execução, um snapshot dos arquivos da
pasta de perfil do dono e das duas pastas de perfis de teste foi obtido, e um interruptor de emergência monitorou o
log da sonda em busca do caminho de perfil do dono.

Observações (todas executadas):
- Apenas com os patches documentados (0xE08950 mutex, 0xE089A0 `My Games\Far Cry 2\` para
  `My Games\FC2test_A\`), o log da sonda mostrou `CreateFileW <Documents>\My Games\Far Cry 2\GamerProfile.xml`
  (leitura, abrir existente): o jogo abriu o perfil real do dono. Cópia encerrada à força após ~45 s; nenhum arquivo em qualquer
  pasta de perfil mudou.
- `Dunia.dll` tem strings separadas junto a `CGamerProfileNative`: 0xE0E080 `\GamerProfile.xml`,
  0xE0E094 `\Far Cry 2` (10 bytes + NUL), 0xE0E0A0 `\My Games`. O ASCII `My Games\Far Cry 2\` em
  0xE089A0 é a única outra ocorrência ASCII; as 12 UTF-16 estão em `.rsrc`, dentro de XML com
  `KnownFolderID=... path="My Games\Far Cry 2\Saved Games"` (aparentemente metadados do Game Explorer).
- Após também aplicar patch em 0xE0E094 para `\FC2test_A` / `\FC2test_B` (17 bytes diferentes do original por
  cópia): cópia A abriu `FC2test_A\GamerProfile.xml`, depois em Continue `FC2test_A\saved games\<save>.sav`;
  cópia B, os de `FC2test_B`. Janela 800x600 conforme definido nos perfis de teste. Ambas as cópias executaram ao mesmo tempo.
- Isso explica as observações de 2026-10-19 acima (janela 1408x792 em vez de 800x600; “se o
  novo caminho de perfil é lido” desconhecido): o patch de 0xE089A0 nunca moveu o perfil.
- `GetLocalPlayerId()` retornou o mesmo id em ambas as cópias após carregar o mesmo salvamento.
- `netstart` em ambas: cerca de 16 pacotes/s em cada direção (log a cada segundo, por exemplo `tx=694 rx=697` após ~44 s),
  `remote` de cada cópia igual ao `local` da outra.
- Erro de vinculação do avatar: ambas as cópias registraram `avatar body bound` com corpo do avatar igual ao corpo do
  jogador local (A `3bd8e940` ambos, B `3bd48a40` ambos). Ambos os jogadores ficaram no mesmo lugar após
  carregar, portanto o corpo mais próximo do avatar recém-criado era o do jogador local. Parado ali
  (sem teste de movimento com o erro).
- Com a correção (busca do avatar pula o corpo local, espera até ele ser conhecido; `av_valid` rejeita
  igualdade): avatar A `3babb100` versus local `3bb54580`, avatar B `3ba96980` versus local `3bd22900`. A primeira
  busca do avatar encontrou 0 correspondências e teve sucesso cerca de 1 s depois. `walk 3 20 2` em A: `pos <avatar id>` de B
  a cada 2 s seguiu o círculo de A 0.5–1 m atrás (por exemplo, remoto `2589.02 2456.56` -> avatar `2589.62 2456.96`);
  `pos <player id>` de B permaneceu dentro de 0.1 m (a mesma deriva existia antes da caminhada).
- Após a caminhada, o corpo de A subiu de z 18.49 para 19.29 e se acomodou.
- `dir` do avatar permaneceu `(1,0)` o tempo todo.
- Nenhuma linha CRASH ou ACCESS VIOLATION em qualquer execução; após cada execução todas as pastas de perfil corresponderam
  ao snapshot obtido antes.
- O primeiro início da segunda cópia abriu uma solicitação do Firewall do Windows para seu `FarCry2.exe`
  (a engine vincula UDP 9000/9001); o dono respondeu.
- Leitura do código: o comando `scan` ainda desreferencia memória diretamente (apenas `findbody` usa
  `ReadProcessMemory` em blocos); `setpos` existe, mas não está no README da sonda; `ent`, `pos`, `setpos` nunca decrementam
  a contagem de referências do holder de entidade.

Derivado:
- A pasta de perfil e a pasta de salvamento vêm ambas de 0xE0E094.
- O erro do avatar só aparece quando ambos os jogadores começam a até 1 m um do outro; as execuções de 2026-10-19 haviam
  movido um jogador primeiro (teletransportes, `tpb`) e não o encontraram.

Desconhecido:
- Para que é usada a string de 0xE089A0.
- Se novos salvamentos (salvamento automático) também vão para a pasta de teste: nenhum salvamento foi escrito nessas execuções.
- Por que o corpo que caminhou subiu 0.8 m após `walk` terminar.
## <a id="automated-two-copy-walk-test-2026-10-24"></a>Teste automatizado de caminhada com duas cópias (2026-10-24)

Script `tests/two_copy_walk.ps1`, adicionado à sonda em https://github.com/MortyRei/fc2-coop-probe/pull/1.
O que ele verifica está listado na seção QA do README.

Observações (executadas, mesmo PC e cópias da seção acima):
- Sonda com a correção do corpo do avatar (`dinput8.dll` SHA-256 `87cb733b...431c`): 16 verificações, 0 falhas, cerca de 2 minutos
  do início ao encerramento. Cópia A precisou de 8 pressionamentos de Enter para chegar ao salvamento, cópia B 3. Corpos dos avatares diferentes dos locais
  nas duas cópias; 16.0 pacotes/s em cada direção; 17 amostras do avatar durante a caminhada de 20 s, todas pareadas com uma posição
  `remote`; amplitude de movimento do avatar 5.92 m; distância até A média de 0.43 m, máxima de 1.07 m; deriva do próprio jogador de B 0.12 m; sem linhas de falha;
  pastas de perfil real e de teste inalteradas.
- Controle negativo com a sonda anterior à correção (`22ac2fea...8001`), mesmo script: 3 verificações falharam. `B player stays
  put`: deriva máxima 16.46 m. `avatar body A/B`: a linha antiga de log não tem ponteiros, portanto não pode ser comparada.
  `avatar moved` (amplitude 16.01 m) e `avatar follows A` (média 0.19 m) passaram.

Derivado: com o erro, ambos os jogadores recebem escritas da posição um do outro, portanto movem-se juntos (daí a deriva
de 16 m e um “avatar” que parece seguir); apenas a verificação de que o próprio jogador da cópia receptora permanece parado diferencia os
dois casos.
## <a id="heading-network-mode-steam-relay-2026-10-24-later"></a>Orientação, modo de rede, relay Steam (2026-10-24, mais tarde)

Observações (executadas; um PC, salvo indicação):
- A matriz do corpo físico do jogador é sempre identidade (cápsula vertical), enquanto a direção da entidade muda; olhar com mouse
  (`mouse_event` relativo) girou o jogador: dir da entidade (-0.640, 0.768) -> (-0.913, -0.409), corpo inalterado.
  Linhas da entidade do jogador: (d0, d1, 0), (-d1, d0, 0), (0, 0, 1).
- Em um pawn criado por script: escrever a rotação de seu corpo persiste no corpo, mas dir da entidade permanece (1,0);
  `TeleportEntity(id, x, y, z, a, b, c)` retorna e não muda nada (nem rotação nem posição);
  `SpawnEntityFromArchetype(..., 0, 0, 90)` fornece dir (0,1) (último argumento = orientação horizontal em graus; radianos ou outros eixos
  não fazem nada); escrever as linhas de rotação da entidade do pawn persiste (ainda (0,1) 3 s depois).
- Mudança na sonda: as linhas de rotação da entidade do avatar recebem a direção recebida a cada tick (suavização de 25 %).
  Teste com duas cópias e fase de giro por mouse: 18/18, avatar de A e B em 128.1/128.1, -145.4/-145.4, 149.8/149.8 graus;
  sem a mudança: avatar permaneceu em 0 graus (1 verificação falhou).
- Visão do dono (ambas as cópias lado a lado): avatar de B girou com A, também quando o dono girou A manualmente.
  Minhas próprias capturas nunca pegaram o avatar: a câmera de diálogo do salvamento inicial se move sozinha; um pawn criado
  ao ar livre com um salvamento posterior também não foi visível, e um pawn não fixado movido por `tpb` atravessou o
  terreno (z 108.9 -> 63.0).
- Modo de rede: par diferente de 127.x -> vincular 0.0.0.0, apenas pacotes do IP do par contam (contador `drop`). Teste com
  o próprio endereço LAN do PC: 19/19; 30 pacotes forjados de 127.0.0.1 descartados.
- Relay (`relay/fc2_relay.py`): substituto UDP e Steam (Spacewar, ctypes de 64 bits sobre a API plana de
  `steam_api64.dll` de Steamworks.NET Standalone 2025.164.1, SHA-256 eb17909a...fb75). Teste por dois relays
  UDP: 22/22. Lado anfitrião Steam em uma conta: inicialização, lobby apenas para amigos criado e deixado.

## <a id="two-pcs-over-steam-2026-10-25"></a>Dois PCs pela Steam (2026-10-25)

Preparação: o primeiro PC (anfitrião) e um segundo PC em outra rede (Wi-Fi versus Ethernet, sem ping entre eles), cada um
com sua própria conta Steam, contas amigas; o segundo PC nunca havia executado o jogo. Mesma `Dunia.dll`
(6353936a...2765) em ambos. O segundo PC foi preparado de um kit (build da sonda, relay, scripts), mais o salvamento
compartilhado e um perfil de teste passados manualmente.

Observações (executadas):
- Primeira tentativa: a cópia do segundo PC tinha patches apenas em 0xE08950 e 0xE0E094. Leu seu próprio
  `FC2test_B\GamerProfile.xml`, mas Story Mode ofereceu apenas New Story; a execução com Enter automático nunca abriu salvamento.
  As cópias do primeiro PC também tinham patch em 0xE089A0 (`My Games\FC2test_A\`). Após aplicar patch em 0xE089A0 no segundo
  PC, sua `Dunia.dll` correspondeu à cópia do primeiro PC com os mesmos três patches (SHA-256 e0fef7c2...) e o salvamento
  foi listado e carregado (`CreateFileW ...\FC2test_B\saved games\222368278550.sav`).
- Segunda tentativa: anfitrião no mundo e lobby criado às 13:05:54; o relay de entrada não encontrou lobby na primeira tentativa,
  encontrou o amigo em um lobby Spacewar na segunda (13:05:56), entrou, a sessão foi aceita e a
  primeira mensagem foi decodificada com a identidade do remetente no offset 16. Avatares criados nos dois lados (corpos vinculados diferentes
  dos locais).
- Pacotes: cerca de 16/s em cada direção por ~7 minutos, dropped=0 em cada linha de estatística de relay nos dois lados, par nunca
  indisponível enquanto ambos executavam (lado de entrada, final tx 6711 / rx 6624).
- `walk 3 20 2` no anfitrião em cerca de 13:06:40. Lado de entrada, `pos <avatar>` a cada 2 s: cerca de dois círculos entre
  ~13:06:58 e ~13:07:19, centro em cerca de (2587.3, 2459.2), raio de cerca de 3 m; o centro da caminhada é o ponto inicial
  menos o raio em x, (2587.36, 2459.24), e 2 m/s x 20 s = 40 m = 2.1 círculos de 18.85 m. O próprio jogador do PC de entrada
  permaneceu dentro de cerca de 0.1 m. Dir do avatar permaneceu (-0.989, 0.151), igual à do jogador anfitrião: `walk`
  não gira o jogador.
- Dono (visualmente): o avatar se moveu na tela do primeiro PC, e no segundo PC deu voltas em círculo.
- Após o lado de entrada parar (13:13:00), o relay do anfitrião mostrou peer=down após seu tempo limite de 20 s.
- Sem linhas CRASH / ACCESS VIOLATION em nenhum lado; nenhum log da sonda nomeou uma pasta de perfil real; os perfis de
  teste permaneceram inalterados (o jogo não salvou nada).

Derivado:
- 0xE0E094 decide o perfil e o arquivo de salvamento aberto; 0xE089A0 decide a pasta da qual a lista de salvamentos é
  construída. A afirmação de 2026-10-24 de que 0xE089A0 não é necessário estava errada.
- O relay Steam transporta o tráfego da sonda entre dois PCs sem endereços IP ou encaminhamento de portas.

Desconhecido: orientação entre PCs (não exercitada), convites e Join Game, comportamento em uma sessão mais longa ou com perda.
## <a id="two-pcs-heading-steam-invite-join-game-2026-10-25-afternoon"></a>Dois PCs: orientação, convite Steam, Join Game (2026-10-25, tarde)

Mesmos dois PCs e cópias de teste acima; anfitrião com `scripts/start-coop.ps1 -Role host`, lado de entrada com o mesmo
script (seu relay com patch de `--join wait`, idêntico byte a byte ao do repositório da sonda).

Observações (executadas):
- Orientação: o anfitrião girou seu jogador com entrada relativa de mouse, mantendo cada direção por ~8 s: 171.3 (início), 81.3,
  -171.3, 77.6 graus (relógios dos dois PCs concordavam dentro de ~1 s: "peer is talking" às 14:38:05 em ambos). O avatar do PC
  de entrada, amostrado a cada 2 s: 171.3 até 14:38:29, 95.7 às 14:38:31 (durante o giro), 81.3 a partir de 14:38:33, -171.3 a partir de
  14:38:42, 77.6 a partir de 14:38:52; posição estável dentro de poucos mm.
- Convite Steam: o relay anfitrião registrou "invite to <name> sent: True" quando seu lobby foi criado; o relay de entrada
  esperou ("waiting for a Steam invite or Join Game ..."); após o dono aceitar o convite no segundo PC
  (cerca de 3 minutos depois), o relay registrou callback 333 ("invite or Join Game accepted (lobby)"), entrou no lobby,
  e os primeiros pacotes e o avatar vieram em até 3 s.
- Join Game: uma nova execução de anfitrião sem convite criou um novo lobby; o relay de entrada esperou; após o dono escolher
  Join Game no anfitrião na lista de amigos da Steam, entrou nesse novo lobby, novamente pelo callback 333; nenhum 337 foi
  registrado. O convite anterior apontava para o lobby anterior (fechado), portanto essa entrada veio de Join Game.
- Todas as execuções: dropped=0 em cada linha de estatística de relay, sem linhas CRASH / ACCESS VIOLATION, nenhuma pasta de perfil real em
  nenhum log da sonda; após um anfitrião parar, o relay de entrada registrou "peer silent for 20 s, dropped".
- Nenhuma linha “accepted session” nessas execuções: ambos os lados enviaram sua primeira mensagem aproximadamente ao mesmo tempo, portanto o
  próprio envio de cada lado abriu a sessão.

Derivado: para um amigo em um lobby que permite entrada, a Steam entrega Join Game como GameLobbyJoinRequested (333), o mesmo
callback de um convite aceito; GameRichPresenceJoinRequested (337) precisaria de uma string de conexão sem lobby.
