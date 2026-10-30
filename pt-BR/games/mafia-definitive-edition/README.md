# <a id="mafia-definitive-edition-2020"></a>Mafia: Definitive Edition (2020)

| | |
|---|---|
| Motor | Illusion Engine (Hangar 13); compartilha código com Mafia III (abaixo) |
| Versões testadas | Steam app 1030840, compilação 16502642, `mafiadefinitiveedition.exe` FileVersion 1.0.0.1, SHA-256 `34B06C6C11326E51001EF2FD82933C7F200ACAD27EDBFCC0C159A7051978675E`, Windows 10 x64. Análise estática e inicializações por bots de cópia de teste isolada e offline com DLL de sondagem e registro |
| Projetos | MafiaMP <https://github.com/MafiaHub/MafiaMP> (exploração livre); MafiaCoop (JustAddMP) <https://github.com/JustAddMP/MafiaDE> (história cooperativa, pré-lançamento); ambos em [DIRECTORY.md](../../DIRECTORY.md). Trabalho próprio deste relato: história cooperativa do zero, reivindicação [#173](https://github.com/cranebeaker/coop-anything/issues/173) |
| Nível de QA | none |
| Última atualização | 2026-10-24 |

## <a id="where-things-stand"></a>Situação atual

Existem dois projetos. MafiaMP oferece exploração livre em servidor dedicado, sem história. MafiaCoop (JustAddMP) afirma acompanhar a história do host, mas é pré-lançamento testado pelo autor só em um PC e poucos capítulos. Este relato cobre uma terceira tentativa, criada do zero. Já ultrapassou a análise estática: uma DLL na cópia de teste registra chamadas dos scripts de história enquanto um bot joga, identificando início de missão, definição de checkpoint e mudanças de objetivos. Ainda não existe código cooperativo.

Registro de pesquisa com fontes, separando observações, deduções e desconhecidos: [NOTES.md](NOTES.md).

## <a id="existing-work"></a>Trabalhos existentes

- **MafiaMP** (<https://github.com/MafiaHub/MafiaMP>, MafiaHub; último commit 2026-10-15, pré-lançamento noturno v2.5.1 de 2025-12-21): multiplayer de exploração livre sobre MafiaHub Framework, com servidor dedicado, API de scripts de servidor e 34 issues e pull requests abertas. Missões e história não sincronizadas. O cliente aplica hooks com MinHook e padrões de bytes no estilo IDA. **Os 394 padrões do cliente ocorrem na compilação 16502642, 382 exatamente uma vez** (varredura do executável em 2026-10-24), tornando muito provável que o SDK de engenharia reversa (`code/client/src/sdk`: humanos, veículos, tráfego, câmera, carregamento dinâmico, diretor do jogo) corresponda a ela. Licença MafiaHub OSS, cuja cláusula 5 só permite derivados para devolver contribuições a MafiaMP e exige autorização escrita para uso pessoal. Use como referência, não base.
- **MafiaCoop (JustAddMP)** (<https://github.com/JustAddMP/MafiaDE>, parte independente do jogo <https://github.com/JustAddMP/core>; repositório criado em 2026-10-08, último pré-lançamento v0.17.1 em 2026-10-21): uma DLL e um inicializador para a compilação 16502642. O README informa que capítulo, checkpoint, objetivos e cenas seguem o host, que desde 0.17.0 executa tráfego, polícia, pedestres e inimigos. O autor testou história cooperativa em Omerta, Taxi e Bon Appetit, em um PC com duas cópias; dois PCs não testados. Transporte UDP ou Steam (`--transport udp|steam`), entrada por convite Steam ou IP. Nenhum repositório possui licença, portanto não concede direitos de reutilização. Não executado aqui.
- **Nomad Group ScriptHook (+Trainer):** executa Lua personalizado no jogo. A listagem é de 2020-12; compatibilidade atual desconhecida (<https://www.gamepressure.com/download/mafia-definitive-edition-mafia-definitive-edition-scripthook-tra/ze12c26>). O Script Hook anterior de MartinJK foi descontinuado (<https://www.gamepressure.com/download/mafia-definitive-edition-script-hook-v10-mod/z812a13>).
- **Mafia Toolkit** (<https://github.com/Greavesy1899/MafiaToolkit>, versão 2.36 de 2026-07-09): lê arquivos SDS de Mafia DE. O toolkit é PolyForm Strict 1.0.0 (código disponível, só uso não comercial, sem distribuição de alterações), mas seu código de arquivos (`Gibbed.Mafia2.FileFormats`, `Gibbed.Illusion.*`, (c) 2017 Rick "gibbed") usa licença zlib.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Executável:** x64 MSVC, 111 MB, cerca de 76 MB de código. Sem empacotamento SteamStub: não há seção `.bind`, permitindo descompilação direta. Possui seção incomum `.interpr`, finalidade desconhecida. O PDB (`MafiaDefinitiveEdition.pdb`) não é distribuído. A maioria dos nomes de tipo RTTI MSVC está ausente, mas nomes de classes sobrevivem em strings de reflexão e serialização. API Steam vinculada estaticamente (o jogo nunca carrega `steam_api64.dll`).
- **Compartilhado com Mafia III:** o executável contém caminhos de scripts de Mafia III, como `/scripts/entities/interactions/int_kill_olivia_game_room_guard_l_hold.vi` e `int_kill_the_judge_*`, tornando amplamente reutilizável a pesquisa desse jogo.
- **Scripts:** o motor incorpora HavokScript (namespace `hks`), VM compatível com Lua 5.1. **As missões, porém, não são arquivos Lua.** Os 150 arquivos em `sds_retail/script` contêm 9.249 recursos Generic: `.ires.compiled` 4.326, `.vi.compiled` 4.210, `.entity.compiled` 358, `.iprofai` 189, `.iproftime` 150 e `.gxml` 15 (extensões da tabela de hashes de Mafia Toolkit). Há também 15.528 animações, 8.261 texturas, 14 cenas e **exatamente um script Lua**, `/scripts/missions/statistic_tracking/statistic_tracking.lua` (bytecode Lua 5.1). O formato `.vi.compiled` não é documentado. Os scripts compilados ainda controlam a história pela API C Lua do jogo, onde mudanças podem ser observadas e reproduzidas (abaixo).
- **Missões** têm um conjunto de arquivos cada: `mm_<n>_<name>_p` e subáreas `mm_<n>_<name>_s_*`. Exemplos: `mm_20_taxi_p`, `mm_110_omerta_p` com `mm_110_omerta_s_bank`, `mm_200_bank_p`. Mundo aberto inclui `lh_trap_manager_*`, `lh_garage_quest_loc_*`, `game_manager` e `game_over_manager`. No jogo, capítulo 1 é missão `mm_10_chase` e capítulo 2, `mm_20_taxi`.
- **Organização SDS v20** (deduzida do código Gibbed sob zlib e conferida nos arquivos): cabeçalho de 12 bytes (`SDS\0`, versão 20, `PC\0\0`), checksum de 4 bytes. Depois, cabeçalho de arquivo de 52 bytes (offsets de tabela de tipos, tabela de blocos, XML, tamanhos RAM/VRAM, indicadores, 16 bytes desconhecidos, quantidade de recursos), com checksum próprio. Segue a tabela de tipos (id, nome com comprimento u32, pai). Dados em fluxo de blocos `zlEU`: alinhamento 0x10000 com indicador 0x1000000 para Oodle; blocos comprimidos têm cabeçalho de 128 bytes, e a descompressão usa `oo2core_8_win64.dll` do jogo. Cada recurso tem cabeçalho de 34 bytes (tipo, tamanho, versão, hash de nome u64, 4×u32 de memória), checksum de 4 bytes e `size - 38` bytes de dados. Recursos Generic começam com hash de tipo u32 e contêm marca `GENR`.
- **API de scripts:** 436 tabelas no estilo `luaL_Reg` (`{const char *name, lua_CFunction fn}`) em `.rdata`/`.data`, total de 5.800 funções. As relacionadas à história nesta compilação:

  | Tabela | Funções (endereço) |
  |---|---|
  | Missões `0x145ad0780` (72) | `QuestSetActive` `0x142245e30`, `QuestSetFinished` `0x142246010`, `QuestSetCustomState` `0x142246e60`, `ObjectiveActivate` `0x142242cc0`, `SetCurrentAct` `0x142244210`, `SetCurrentSubAct` `0x142244470`, `GameOver` `0x142245970`, `CityTransfer` `0x142245af0` |
  | Salvamentos `0x145af5810` | `EnableSaveLogic` `0x142e56940`, `RequestCheckpointSave` `0x142e56ef0`, `RequestMissionSave` `0x142e56f40`, `Retry` `0x142e570b0` |
  | HUD `0x145af7b50` (237) | `AddQuestChapter` `0x142f51880`, `AddQuestObjective` `0x142f54590`, `ShowMissionComplete` `0x142f4db40`, `ShowMissionRestart` `0x142f4d830`, `AcceptMissionRestart` `0x142f5bec0` |
  | `0x145ae3450` (finalidade incerta) | `SetMissionState` `0x142677270` |
  | Jogo `0x145ae3b20` | `SetCurrentStoryId` `0x142683340`, `GetMissionTime` |

  A maioria são métodos (argumento 1 é o userdata do invólucro). Os prólogos de ligação Lua se repetem, portanto assinaturas de bytes não são únicas. Resolva pelo nome nas tabelas de registro em execução. Funções de missão chamam um gerenciador global em `0x14635a740` por sua vtable (por exemplo, `QuestSetActive` -> vt+0x70); ser `C_GameDirector` é hipótese.
- **Valores HavokScript** (confirmados em execução): `lua_State` +0x48 topo, +0x50 base; valores da pilha têm 16 bytes, marca u32 em +0 e valor em +8. Marcas: 1 booleano, 3 número (float), 4 string, 7 userdata (invólucros `self`). Objeto de string tem comprimento u64 em +0x08, hash u32 em +0x10 e texto em +0x14.
- **Chamadas da história no capítulo 1**, registradas em execução com bot (consultas e leituras por quadro omitidas; tempo em segundos após iniciar):

  | Tempo | Chamadas | No jogo |
  |---|---|---|
  | 96.6 | `EnableSaveLogic("main")`, `RequestMissionSave("mm_10_chase")`, `SetMissionState("mm_10_chase", true)`, `UpdateRolloverDateAndImage("$mm_10_chase_date", "mission01")` | missão começa a carregar |
  | 108.5 | `CreateScriptActorAction` ×4, `RegisterVehicleDirect("enemy")` | preparação de atores |
  | 108-318 | nenhuma | cena inicial |
  | 318.7 | `ShowTitleCard("$title_card_mm_010_…", …)`, depois `HideTitleCard` | título do capítulo |
  | 384.8 | `SetRespawnPosDir`, `QuestSetCustomState("mm_10_chase", "cp_020")`, `UpdateSimpleObjective("$mm_10_chase_cp_020", …)`, `AddSecondaryObjective("$mm_10_chase_cp_030_…", false, 1)`, `OpenScotchTutorial("tutorial_accelerate", …)` | jogabilidade começa em checkpoint |
  | 396.8 | `RegisterIconEntityDirect("traps")`, `AddEntityIndicator("vehicle_trap")` | marcador no carro dos gângsteres |
  | 400.8 | `ZombieShotAtEntityStart`/`Stop`, `ModifyGameTime(0.3, 1000)` | tiros por script, câmera lenta |
  | 411.7 | `ShowMissionRestart("mm_10_chase", "mm_000_go_death")` | tela de morte (bot não dirige) |

  A cada quadro de jogabilidade, os scripts chamam `GetActivePlayer` cerca de 60 vezes e `GetMissionTime` de 120 a 240 vezes por segundo. Canal de sincronização deduzido: início `SetMissionState(<mission>, true)`, checkpoint `QuestSetCustomState(<mission>, "cp_NNN")`, objetivos `UpdateSimpleObjective`/`AddSecondaryObjective` com IDs de texto `$`, morte `ShowMissionRestart(<mission>, <reason>)`.
- **Todos os 20 capítulos**, carregados um a um por Chapter Replay com bot e registrados até pouco depois do primeiro checkpoint jogável (uma inicialização por capítulo; o bot não joga, então checkpoints posteriores não cobertos):

  | Capítulo (posição na lista) | Missão | Título | Checkpoints observados | ID do texto do primeiro objetivo |
  |---|---|---|---|---|
  | 1 | `mm_10_chase` | `$title_card_mm_010_…` | `cp_015`, `cp_020` | `$mm_10_chase_cp_020` |
  | 2 | `mm_20_taxi` | `$title_card_mm_020_title` | `cp_020` | `$mm_20_taxi_cp_010` |
  | 3 | `mm_30_molotov` | `$title_card_mm_030_title` | `cp_020` | `$mm_30_molotov_cp_020_look_around` |
  | 4 | `mm_40_motel` | `$title_card_mm_040_title` | `cp_010`, `cp_020` | `$mm_40_motel_cp_005` |
  | 5 | `mm_50_race` | `$title_card_mm_050_title` | `cp_020`, `cp_030`, `cp_040`, `cp_050` | `$mm_50_race_cp_030` |
  | 6 | `mm_60_sarah` | `$title_card_mm_060_title` | `cp_020` | `$mm_60_sarah_cp_020` |
  | 7 | `mm_70_hoodlums` | `$title_card_mm_070_title` | `cp_020` | `$mm_70_hoodlums_cp_020` |
  | 8 | `mm_80_brothel` | `$title_card_mm_080_title` | `cp_015`, `cp_020` | `$mm_80_brothel_cp_015` |
  | 9 | `mm_100_farm` | `$title_card_mm_100_title` | `cp_015`, `cp_020`, `cp_030` | `$mm_100_farm_cp_015` |
  | 10 | `mm_110_omerta` | `$title_card_mm_110_title` | `cp_020`, `cp_030` | `$mm_110_omerta_cp_020` |
  | 11 | `mm_120_mansion` | `$title_card_mm_120_title` | `cp_020` | `$mm_120_mansion_cp_010` |
  | 12 | `mm_130_parking` | `$title_card_mm_130_title` | `cp_020`, `cp_030` | `$mm_130_parking_cp_010` |
  | 13 | `mm_140_salieri` | `$title_card_mm_140_title` | `cp_020` | `$mm_140_salieri_cp_020` |
  | 14 | `mm_150_boat` | `$title_card_mm_150_title` | `cp_020`, `cp_030` | `$mm_150_boat_cp_010` |
  | 15 | `mm_160_harbor` | `$title_card_mm_160_title` | `cp_015`, `cp_020` | `$mm_160_harbor_cp_020` |
  | 16 | `mm_170_plane` | `$title_card_mm_170_title` | `cp_020` | `$mm_170_plane_cp_020_1` |
  | 17 | `mm_180_sniper` | `$title_card_mm_180_title` | `cp_020` | `$mm_180_sniper_cp_010` |
  | 18 | `mm_190_cigars` | `$title_card_mm_190_title` | `cp_020`, `cp_030`, `cp_040` | `$mm_190_cigars_cp_020` |
  | 19 | `mm_200_bank` | `$title_card_mm_200_title` | `cp_050`, `cp_060` | `$mm_200_bank_cp_010` |
  | 20 | `mm_210_gallery` | `$title_card_mm_210_title` | `cp_020` | `$mm_210_gallery_cp_020` |

  Cada capítulo é uma missão, iniciada com `SetMissionState("<mission>", true)` e um título `$title_card_mm_<NNN>_…`. Checkpoints são sempre `QuestSetCustomState("<mission>", "cp_NNN")`, e IDs de objetivo seguem `$<mission>_cp_NNN…`; o cliente precisa só do nome da missão e ID do checkpoint para seguir o host. O primeiro objetivo pode pertencer a checkpoint anterior ao primeiro `QuestSetCustomState` (como `cp_010` antes de `cp_020`), então iniciar a missão funciona como checkpoint inicial implícito. Capítulo 19 começa em `cp_050`. Os arquivos `sds_retail` incluem `mm_90_funeral`, não carregado por nenhuma entrada de Chapter Replay, e `mm_03_morello`, `mm_010_bridge`, `mm_020_prologue`, `mm_040_chase`, `mm_070_acetylene`, `mm_180_prison`; suas finalidades não foram verificadas.
- **Salvamentos:** o sistema grava blocos nomeados, entre eles `S_QuestsManagerSaveData`, `S_PlotlinesManagerSaveData`, `S_DialogStateManagerSaveData`, `S_JournalSaveData`, `S_StreamingWorldStateSaveData`, `C_PoliceForceSaveBlock`, `S_GameActivitiesSpawnSystemSaveData`. Tudo fica sob `<Documents>\My Games\Mafia Definitive Edition\` (Documents por `SHGetFolderPathA(CSIDL_PERSONAL)`, visto em disco na instância redirecionada): `Saves\launcconfig.cfg`, `Saves\videoconfig.cfg`, perfil em `Data\<SteamID64>\profiles\temporaryprofile\*.pf`, salvamentos em `Data\<SteamID64>\gamesaves\default\aslot\save<n>.sav` (binário, cabeçalho `GENR`). Independe da instalação, portanto todas as cópias compartilham a pasta; se Documents é redirecionado ao OneDrive, os salvamentos também.
- **Perfis** (`*.pf`): XML (`C_SaveDataUnwrapped` com blocos) e sufixo de 4 bytes, CRC32 do XML (little endian). Armazenamento de scripts mapeia `C_HashName` (FNV-1 de 64 bits do nome, multiplicar e depois xor; nomes só de dígitos interpretados como números) para `S_Variable*`; `m_Type` é 2 para `S_VariableNumber` e 3 para `S_VariableString`. Chapter Replay (`0x142fe01b0`) mostra capítulo *i* jogável se *i* for menor que `MissionReplayUnlocked` no bloco `PersistentDataStorage` de `profile_data_storage_persistantdata.pf`. Defini-lo num perfil de teste desbloqueia os 20; cada um carregou diretamente, sem confirmação, terminando na tela que espera "Continue". Assim, ambos devem poder carregar o mesmo capítulo sem chegar até ele jogando (dedução, não testada em duas instâncias).
- **Entradas:** teclado/mouse por DirectInput 8, controles por XInput (importado e localizado por `GetProcAddress` em execução). Mensagens postadas à janela não têm efeito. A interface segue o cursor real (muda os avisos para mouse quando ele se move) e chama `ClipCursor`. Cenas pausam com janela inativa; o jogo reage a `WM_ACTIVATE`/`WM_ACTIVATEAPP`. Tocar ou segurar A, ou pressionar B, não pula cenas; tecla de pular desconhecida. Para bots: botão mantido por 0,4 s passa à tela seguinte (A fecha aviso de falha de conexão 2K e também aciona Continue no menu); em Chapter Replay, um DOWN às vezes move duas linhas, mesmo com pulsos de 0,15 s. Confira o destaque antes de selecionar. O aviso de conexão 2K não aparece em toda inicialização offline.
- **Serviços on-line:** ao iniciar, contata `*.my.2k.com` e `*.api.2kcoretech.online` (login único, telemetria, promoções). A biblioteca HTTP escreve logs detalhados, **incluindo token bearer**, na saída padrão. Quando as consultas falham, mostra aviso de conexão 2K e funciona normalmente offline.
- **Instância única e rede:** importa `CreateMutexA`/`OpenMutexA`; recusa a segunda instância não testada. O jogo é individual; desconhece-se se resta código de rede do motor.

## <a id="what-we-changed"></a>O que alteramos

Nenhum arquivo do jogo. Ferramentas escritas até agora (ainda não publicadas):

- Extrator de scripts SDS v20 somente leitura e scanner de padrões de bytes.
- Scripts Ghidra sem interface: referências cruzadas de strings com descompilação e localização de tabelas `luaL_Reg`.
- DLL de sondagem como proxy `version.dll`, só na cópia de teste. Redireciona `SHGetFolderPathA` para pasta por instância (encerra se falhar), bloqueia consultas/conexões fora de loopback, fornece controle XInput virtual alimentado por arquivo de texto, fixa cursor, mantém janela ativa e envolve 579 funções C Lua de 8 tabelas. Cada invólucro troca o ponteiro da tabela só se nome e endereço coincidirem com a compilação. Registra chamadas com argumentos decodificados, limitadas por função.
- Estrutura de inicialização: registra instalação real, hash do executável, `Documents\My Games`, Saved Games, Steam `userdata` e chaves de registro 2K/Hangar 13 antes/depois, relatando mudanças. Um monitor encerra jogos iniciados na instalação real. Bots navegam até qualquer capítulo, conferindo a tela antes de cada comando (título do menu, linha destacada), por capturas da janela.
- Editor `.pf` que define variável numérica e corrige CRC (recusa arquivos cujo CRC já esteja errado).

## <a id="qa"></a>QA

Nenhum cooperativo: não existe código cooperativo. Sondagens e estrutura até aqui (36 inicializações protegidas da cópia, todas offline exceto a primeira): todas preservaram instalação real, hash do executável e salvamentos. Só registros internos do cliente Steam mudaram (`localconfig.vdf`, `librarycache\*.json`, `gamerecording.pb` e cache Steam Notes `userdata\<id>\2371090\remotecache.vdf`, com data renovada e conteúdo idêntico). Uma execução também detectou arquivos Steam de outro jogo iniciado no PC durante o teste.

## <a id="how-to-play"></a>Como jogar

Este trabalho ainda não é jogável. Para jogar hoje, consulte os dois projetos em Trabalhos existentes.

## <a id="known-issues"></a>Problemas conhecidos

Nenhum, pois nada é distribuído ainda.

## <a id="next-steps"></a>Próximos passos

1. Registrar cada capítulo após os primeiros checkpoints: listar todos os `cp_NNN` por missão e chamadas de término (`ShowMissionComplete`, início da próxima). Exige bot que dirija/caminhe ou forma de saltar a checkpoints.
2. Aplicar hooks abaixo da ligação Lua: gerenciador das funções de missão (`0x14635a740`), `SetMissionState` -> `0x142438730` e pedidos de salvamento. Confirmar que código nativo só altera a história por eles.
3. Dar ao host autoridade sobre a história. Enviar início de missão, checkpoint, objetivos e reinício ao cliente e reproduzir com proteção contra reentrada. Suprimir as chamadas próprias do cliente para essas funções.
4. Na entrada tardia, carregar no cliente o capítulo do host por Chapter Replay e aplicar seu checkpoint. Para ressincronizar, usar blocos do host (missões, tramas, diário, diálogos, mundo carregado) como snapshot.
5. Testar duas instâncias em um PC (cada uma com Documents redirecionado) usando bots, antes de dois PCs.
