# <a id="god-of-war-2018--co-op-research--reverse-engineering-notes"></a>God of War (2018) - notas de pesquisa cooperativa e engenharia reversa

Data: 2026-10-28
Estado: Etapa 0 (Triagem), Etapa 1 (Pesquisa) e Etapa 3 (Engenharia reversa estática da compilação Steam instalada `11168363`). Nenhum processo de jogo iniciado; nenhum arquivo da instalação ou dos salvamentos reais alterado.

## <a id="1-game-identity-observed-on-owners-install"></a>1. Identidade do jogo (observada na instalação do usuário)

- **Título:** God of War (2018; lançamento PC em 2022)
- **Loja:** Steam (AppID `1593500`), manifesto `appmanifest_1593500.acf`
- **ID da compilação Steam:** `11168363`
- **Executável principal:** `<game dir>\GoW.exe`
  - **Tamanho:** `20,083,552` bytes
  - **SHA-256:** `caebcb027980d7eac9203d190f9ee649eebc549f8defce138e2114dc91f40452`
  - **Arquitetura:** x64 (`PE32+`), base de imagem `0x140000000`
  - **Timestamp PE:** `1653506097` (`0x628e8031`, `2022-05-25 19:14:57 UTC`)
  - **Versão de arquivo / produto:** `1.0.475.7534` / `GoW-4757534-Wed May 25 11:52:20 2022`
  - **Opções de inicialização (`<game dir>\exec\boot-options.json`):** `content-id: PC0000-GOWA08000_00-00000000PLATINUM`, `app-version: 01.35`, `build-id: 79291`, `wad-pack-id: 379064`, `code-changelist: 4757534`, `data-changelist: 5336418`, `code-branch: //int8-code/main81`, `data-branch: //int8-data/main81`
  - **Seções PE:**
    - `.text`: RVA `0x00001000`, VSize `0x00d4649e`, RawPtr `0x00000400`, RawSize `0x00d46600` (~13.3 MB)
    - `.rdata`: RVA `0x00d48000`, VSize `0x0031139e`, RawPtr `0x00d46a00`, RawSize `0x00311400` (~3.1 MB)
    - `.data`: RVA `0x0105a000`, VSize `0x04064bd8`, RawPtr `0x01057e00`, RawSize `0x001b3a00`
    - `.pdata`: RVA `0x050bf000`, VSize `0x00097f5c`, RawPtr `0x0120b800`, RawSize `0x00098000`
    - `_RDATA`: RVA `0x05157000`, VSize `0x000030c0`, RawPtr `0x012a3800`, RawSize `0x00003200`
    - `.rsrc`: RVA `0x0515b000`, VSize `0x00013a58`, RawPtr `0x012a6a00`, RawSize `0x00013c00`
    - `.reloc`: RVA `0x0516f000`, VSize `0x0002fbbc`, RawPtr `0x012ba600`, RawSize `0x0002fc00`
    - `.bind`: RVA `0x0519f000`, VSize `0x0003d160`, RawPtr `0x012ea200`, RawSize `0x0003d160`
- **Motor:** motor proprietário Santa Monica Studio (namespace C++ interno `Kinetica`, branch `int8`, portado para PC por Jetpack Interactive).
- **DLLs distribuídas em `<game dir>`:** `bink2w64.dll`, `libSceGnm.dll`, `libSceGpuAddress.dll`, `libSceJobManager.dll`, `libScePad.dll`, `nvngx_dlss.dll`, `steam_api64.dll`, `exec\crs-client.dll`.

## <a id="2-search-log"></a>2. Registro de buscas

- **Este repositório (`DIRECTORY.md`, `data/directory.yaml`, `games/`, issues e PRs GitHub):**
  - `data/directory.yaml` tinha lacuna para `God of War (2018)` (`checked: 2026-10-16`).
  - Não havia relato em `games/god-of-war-2018`.
  - Busca de issues/PRs em `cranebeaker/coop-anything` por `"god of war"` retornou 0 abertas ou fechadas.
- **Buscas de repositórios pela API GitHub:**
  - Consultas: `god of war coop OR multiplayer`, `godofwar mod OR lua OR wad`, `"GoW.exe" OR "Kinetica" god of war`, `GOWTool OR godofwar-gameplay-tweaks OR gow-gameplay-tweaks`, além de forks de `Nukem9/godofwar-gameplay-tweaks`.
- **Buscas na web:**
  - Consultas: `"God of War" 2018 "co-op" OR "multiplayer" mod PC`, `"God of War" PC modding tools wad dcb lua unpacker github`, `"God of War" "Atreus" playable mod OR "Speclizer" OR "multiplayer" OR "co-op"`, `"God of War Ragnarok" "co-op" OR "multiplayer" mod PC`.
- **Não pesquisados diretamente:** servidores Discord, fóruns em outros idiomas.

## <a id="3-observations-verified-facts"></a>3. Observações (fatos verificados)

### <a id="31-existing-mods-and-tooling-public-sources"></a>3.1 Mods e ferramentas existentes (fontes públicas)

- **Não existe mod cooperativo ou multiplayer** de *God of War (2018)* no PC (nem de *God of War Ragnarök*).
- **[Nukem9/godofwar-gameplay-tweaks](https://github.com/Nukem9/godofwar-gameplay-tweaks)** (último push `2024-02-01`, licença não informada / "No license provided. TBD", 3 forks sem commits mais novos):
  - Carrega em `GoW.exe` como proxy `version.dll`.
  - Hooks em `IFFProcessLuaScriptChunk` (RVA `0x466de0`, deslocamento de arquivo `0x4661e0`) e `LoadLuaScriptChunk` (RVA `0x466260`, deslocamento `0x465660`) extraem blocos de bytecode Lua 5.2 (`.lua.bin`) dos carregamentos `.wad` e compilam/injetam fontes `.lua` substitutas de `mods\lua\` em execução por `luaL_newstate`, `lua_load` e `str_dump` do jogo.
  - Contorna o conjunto fixo de blocos Lua WAD do motor alterando chamadas de alocação (`LuaScriptChunkMemoryAllocatorHookLoc` e `LuaScriptAllocatorHookLoc`) para `_aligned_malloc` e `realloc`/`free`.
  - Mapeia tabelas RTTI internas (`Kinetica::RTTI::TypeDeclTable`, `EnumDeclTable`, `TypeAttributeTable`, `ArrayAttributeTable`, `HashMapAttributeTable`), `GameModule::SLIFunctionTable`, `GameModule::SLIPropertyTable`, `gCameraBlender` e `gLocalPlayerGO`.
  - Aviso em `CameraHooks.cpp` (`hk_CameraObjectGetFov`): `GoW.exe` usa otimização do programa inteiro e espera que certas funções preservem o registrador volátil `R9` entre chamadas (mesmo risco de *Middle-earth: Shadow of War*, item 67 de `playbook/methods.md`).
- **[adore11s/God-of-War-VR-Mod](https://github.com/adore11s/God-of-War-VR-Mod)** (MIT, ativo, último push `2026-10-26`):
  - Proxy `version.dll` C++ com fonte completa para *God of War (2018)*, suporta Steam, Epic e GOG.
  - Compilação de referência registrada (`PE timestamp 0x628e8031 = 1653506097`) é exatamente a Steam (`11168363`) instalada aqui (`source/src/core/addrsigs.inc` lista 166 VAs estáticos e assinaturas).
  - Mapeia tabela de personagens/entidades (`*(0x1422a98c0)`, vetor em `+0x20`, contagem em `+0x30`), ponteiro do herói (`*(0x1422c6950)` e `*(*(*(0x1422e7d50) + 8) + 8)`), esqueleto (`*(obj + 0x238)`, número de juntas `*(int16_t*)(skel + 0x38)`, vetor de hashes `*(uint64_t**)(skel + 0x30)`, matrizes mundiais `*(uint8_t**)(skel + 0x58) + (count + i) * 0x40`), avaliação de esqueleto local para mundo (`0x140591550`), indicador cinematográfico (`*(uint8_t*)0x1422e9d2f`), controle XInput virtual (hook IAT `XInputGetState`) e PlayStation `libScePad`, substituição de foco (hook `GetForegroundWindow` para instâncias em segundo plano aceitarem entrada), canal de comandos ativo (`gowvr_logs\cmd.txt`).
- **[kainotoa/GOWTool](https://github.com/kainotoa/GOWTool)** (último push `2024-10-31`, sem arquivo de licença) e **[JeanxPereira/GoWToolkit](https://github.com/JeanxPereira/GoWToolkit)**:
  - Navegadores e extratores de recursos `.wad`, `.toc`, `.texpack`, `.lodpack`.
- **Vídeo de Atreus jogável (Speclizer, 2022):**
  - Demonstra troca de controle/personagem para Atreus no modo de um jogador; nunca lançado como mod cooperativo.

### <a id="32-static-analysis-of-installed-gowexe-and-wad-archives-verified-by-local-scripts"></a>3.2 Análise estática de `GoW.exe` instalado e arquivos `.wad` (verificada por scripts locais)

1. **Seções de código e dados sem criptografia em disco:**
   - Apesar de `GoW.exe` ter seção `.bind` (SteamStub), `.text`, `.rdata` e `.data` **não são criptografadas** em disco. Todas as assinaturas testadas de `Nukem9/godofwar-gameplay-tweaks` corresponderam a `GoW.exe` em disco com `1 match(es)` cada:
     - `wadLoader::OpenFile`: deslocamento de arquivo `0x41cba0` (RVA `0x41d7a0`, VA `0x14041d7a0`)
     - `dc::LookupSymByHash`: deslocamento de arquivo `0x430f90` (RVA `0x431b90`, VA `0x140431b90`)
     - `IFFProcessLuaScriptChunk`: deslocamento de arquivo `0x4661e0` (RVA `0x466de0`, VA `0x140466de0`)
     - `LoadLuaScriptChunk`: deslocamento de arquivo `0x465660` (RVA `0x466260`, VA `0x140466260`)
     - `lua_newstate`: deslocamento de arquivo `0x9e8110` (RVA `0x9e8d10`, VA `0x1409e8d10`)
     - `lua_load`: deslocamento de arquivo `0x9e2b20` (RVA `0x9e3720`, VA `0x1409e3720`)
     - `UpdatePlayerPositionJob`: deslocamento de arquivo `0x7924b0` (RVA `0x7930b0`, VA `0x1407930b0`)
     - `gLocalPlayerGO`: RVA `0x022e7d50` (VA `0x1422e7d50`)
     - `gCameraBlender`: RVA `0x022a93d0` (VA `0x1422a93d0`)
2. **Bytecode Lua 5.2 não comprimido com símbolos completos de depuração nos `.wad`:**
   - Varredura dos 597 arquivos `.wad` em `<game dir>\exec\wad\pc_le\` encontrou **6.627 blocos `IFFLuaScriptChunkHeader`** (tipo `IFFHeader` `0x24`, `0x60` bytes e cabeçalho de script de `0x204` bytes), cobrindo **1.423 caminhos Lua únicos** (`%PROJ_PATH%/gameart/scripts/...`).
   - Cada bloco começa por `1b 4c 75 61 52 00 01 04 08 04 04 00 19 93 0d 0a 1a 0a`: bytecode Lua 5.2 little-endian padrão com `int` de 4 bytes, `size_t` de 8, `Instruction` de 4 e **`lua_Number` `float` de 4 bytes**.
   - Depuração **não removida**: caminhos originais (`@Z:\int8\gameart\scripts\...`), nomes de funções, variáveis locais e upvalues preservados.
   - WADs e scripts principais:
     - `r_perm.wad` (198 scripts): `libraries/core/thunk.lua` (`__hook_thunks`, `InstallHook`), `libraries/creature/locomotion.lua` (`SetActuator`, `SetFocus`, `FollowNavCurve`, `motionWarp.SetWarp`), `libraries/design/puppeteerlibrary.lua` (`game.Puppeteer.NewForce`, `SyncAndPlayBranch`, `GoToLocation`), `libraries/design/questlibrary.lua` (`game.QuestManager.GetQuestState`, `StartQuest`, `ProposeQuestState`, `IncrementQuestProgress`), `libraries/socket.lua`, `libraries/mobdebug.lua`.
     - `r_heroa00.wad` (4 scripts): `characters/heroa00/main.lua` (405,218 B de bytecode), `perks.lua`, `audio_luahooks.lua`, `libraries/ui/util.lua`. Contém hooks como `SendInputDataToSon`, `OnSonRevive`, `OnSonCoopJumpAttack`, `LuaHookDecision_CanSonPerformSpecial`, `LuaHook_SpawnGameObject`.
     - `r_son00.wad` (22 scripts): `characters/son00/main.lua` (181,180 B), `son_brain.lua` (224,654 B), `son_awarenessbrain.lua` (107,105 B), `son_motionbrain.lua` (72,605 B), `son_helper.lua` (34,656 B), `son_poiframework.lua` (28,727 B), `son_gamestate.lua` (15,598 B), `son_input.lua` (12,099 B), `son_targetbrain.lua` (8,544 B), `son_interaction.lua` (5,432 B).
3. **`socket.core` (LuaSocket TCP/UDP) e `cmsgpack` (MessagePack) embutidos em `GoW.exe`:**
   - Inspeção de `luaL_openlibs` (`loadedlibs[]` e `preloadedlibs[]` no deslocamento de arquivo `0xd9cff0`..`0xd9d090`, RVA `0xd9e5f0`..`0xd9e690`) em `GoW.exe` revelou que cada estado Lua registra:
     - `_G` (`0x1409fdb80`), `package` (`0x1409fff80`), `coroutine` (`0x140a08860`), `table` (`0x1409fb720`), `string` (`0x140a048d0`), `bit32` (`0x140a09260`), `math` (`0x140a057d0`), `debug` (`0x140a080d0`), **`cmsgpack`** (`0x1409fa370`), e pré-carrega **`socket.core`** (`0x140a05bd0`, com `udp`, `sendto`, `receivefrom`, `settimeout`, `setsockname`, `setpeername`).
4. **Vínculos nativos C para Lua e reflexão do motor em `GoW.exe`:**
   - **2.057 entradas `(name_va, func_va)`** em `.rdata`/`.data` (passo de 24 bytes `0x18` em `.data`, de RVA `0x011bc500` a `0x011c9000`), expondo:
     - Entidade / Transformação / Criação: `GetWorldPosition` (`0x14018f800`), `SetWorldPosition` (`0x1405fc0f0`), `SetLocalPosition` (`0x1405fbf20`), `SetWorldFacing` (`0x1405fbd00`), `SetWorldOrientation` (`0x1405fbb20`), `SetWorldTransform` (`0x1405fb7d0`), `SpawnGameObject` (`0x1405ffc20`), `SpawnProp` (`0x1405ff930`), `SpawnWildlife` (`0x1405f9850`), `ClonePose` (`0x1405feec0`), `AnimSync` (`0x140607b80`).
     - Jogador / Companheiro / IA / Movimentos: `GetPlayer` (`0x140222030`), `GetAI` (`0x140221e30`), `IsCreature` (`0x14018f420`), `GetCreature` (`0x1405fa4f0`), `TriggerMoveEvent` (`0x1407dc860`), `IsPlayingMove` (`0x1407dd1a0`), `IsInNavigationMove` (`0x1407dd130`), `GetActiveMovePercent` (`0x1407dcff0`), `IsDoingSyncMove` (`0x140223470`), `IsSyncMaster` (`0x140223550`), `IsSyncSlave` (`0x140223630`), `GetSyncInfo` (`0x1407da010`), `RequestInteract` (`0x1407d3150`), `HasInteractAvailable` (`0x1407d2f30`).
     - História / Variáveis / Salvamentos / Cenas: `GetVariable` (`0x140787c60`), `SetVariable` (`0x1407878d0`), `OnVariableChange` (`0x1407804c0`), `CreateEntityVariableMonitor` (`0x1407806e0`), `GetHeroPersistentLevel` (`0x14020afe0`), `GetSonPersistentLevel` (`0x14020b080`), `GetPermLevel` (`0x14020b130`), `MarkForSave` (`0x140781120`), `SetSaveRequired` (`0x1405fb470`), `SetInhibitSave` (`0x1405fb3c0`), `EnableCinematicMode` (`0x1407a1830`), `DisableCinematicMode` (`0x1407a17e0`), `IsInCinematicMode` (`0x1407a17b0`).
   - **395 entradas `SLIFunctionHandler`** em RVA `0x011ca300` e **86 `SLIPropertyHandler`** em RVA `0x011cc9a0`.
   - **482 entradas `EnumDecl`** inicializadas estaticamente em RVA `0x01184e70` (incluindo `eTeams`, `ePad`, `ePadMask`, `ePlayerControls`, `eSynchFlags`, `eCombatMoveType`, `eSaveOption`) e **1.198 posições `TypeDecl`** em RVA `0x011daa70` (entradas `2..1197` preenchidas dinamicamente em execução).
   - **1.263 classes/estruturas RTTI MSVC** em `.data`, revelando arquitetura de filas (`ScopedLuaRequestQueue`, `DMARequestAllocator`) onde vínculos Lua enfileiram solicitações tipadas (`SetPositionRequest`, `SetFacingRequest`, `SetTransformRequest`, `WarpCreatureRequest`, `SpawnGameObjectRequest`, `ClonePoseRequest`, `MimicRequest`, `ModifyCreatureMotionRequest`, `ModifyMoveSystemRequest`, `LevelSetVariableRequest`).
5. **Salvamentos, configurações e instância única:**
   - `GoW.exe` lê `settings.ini` do diretório de trabalho/jogo (`./settings.ini`).
   - Salvamentos usam `SHGetKnownFolderPath` (`FOLDERID_SavedGames` -> `%USERPROFILE%\Saved Games\God of War\<steam_id>\`). `GoW.exe` tem **0 importações/strings de `ISteamRemoteStorage`** (Steam Cloud usa Auto-Cloud na pasta `Saved Games`, não a API `ISteamRemoteStorage`).
   - **0 ocorrências `OpenMutex` e 0 `FindWindow`** em `GoW.exe` (só 1 importação `CreateMutexA` no runtime de falhas/fibras).

## <a id="4-derived-from-static-analysis--existing-mods"></a>4. Deduções (da análise estática e mods existentes)

- **Por que modo assimétrico Kratos + Atreus é o caminho mais curto:**
  - *God of War (2018)* mantém Kratos (`r_heroa00.wad`, `game.Player.FindPlayer()`) e Atreus (`r_son00.wad`, `game.AI.FindSon()`) carregados, animados e aptos a combater por praticamente toda a campanha.
  - Criar um segundo Kratos (`goPlayer`) num motor de câmera e movimentos sincronizados para um jogador enfrentaria cada agarrão, transição de barco e `PlaySingleSynchMove_KratosSonObject`. **Jogador 1 como Kratos (host)** e **jogador 2 como Atreus (convidado)** reutiliza a entidade `son00` sem inventar outra classe de jogador.
- **Como jogador 2 controla Atreus (`son00`) em Lua + C++:**
  - Cérebro de IA (`son00/main.lua`, `son_brain.lua`, `son_motionbrain.lua`, `son_input.lua`) já expõe `gVFSDisableSonCommands`, `gVFSDebugNoBrainLogic`, `creature.locomotion` (`SetActuator`, `SetFocus`, `motionWarp.SetWarp`), `TriggerMoveEvent` e `game.Puppeteer`.
  - Melhor: `GoW.exe` tem `socket.core` (UDP) e `cmsgpack` estão em cada VM, então hook Lua carregado por `IFFProcessLuaScriptChunk` (método `Nukem9`) abre socket UDP não bloqueante (`require("socket").udp()`) diretamente em Lua!
- **Duas arquiteturas a avaliar nas etapas 1-2:**
  1. **Sincronização em duas instâncias (Kratos host, Atreus cliente):**
     - Ambas no mesmo nível/salvamento. Host executa Kratos e substitui IA/locomoção de Atreus (`SetActuator` / `TriggerMoveEvent` / `SetWorldPosition` / `SetWorldFacing`) por entrada de controle ou pacotes do cliente; cliente executa Atreus (câmera ligada a ele por hook `gCameraBlender` de `Nukem9`/`God-of-War-VR-Mod`) e espelha Kratos, inimigos e estado `SetVariable`/`QuestManager` do host.
  2. **Uma instância / Parsec / Steam Remote Play Together (ou dois controles locais):**
     - Ambos já estão no mesmo mundo e tela (ou segunda câmera/área de visualização separada); segundo controle XInput/PlayStation no host (ou Parsec/Remote Play) dirige locomoção (`SetActuator`), mira, arco (`TriggerMoveEvent`) e invocações rúnicas de Atreus, suprimindo IA autônoma (`gVFSDebugNoBrainLogic`), sem dessincronização de inimigos, missões ou cenas!

## <a id="5-runtime-verified-findings-2026-10-28"></a>5. Descobertas verificadas em execução (2026-10-28)

- **Cabeçalho de entrada SteamStub v3.1 e múltiplas instâncias:**
  - Cabeçalho `.bind` em `0x14519f220..0x14519f310` tem assinatura `0xC0DEC0DF`, `OriginalEntryPoint = RVA 0x3ec680` (`0x1403ec680`) e indicadores `0x06` (sem criptografia de seções).
  - Alterar entrada `.bind` `0x14519f310` com salto relativo de 5 bytes (`E9 6B D3 24 FB`) para `0x1403ec680` e inserir hook IAT `steam_api64.dll!SteamAPI_RestartAppIfNecessary` (`0x140d49328`) retornando `false` permite outra instância simultânea de `GoW.exe` (`BypassSteamStub=1`) ao lado do host `GoW.exe`, sem conflitos de travas nos hardlinks `.wad` / `.lodpack`.
- **Desmontagem Lua 5.2 e estrutura da VM:**
  - Todos os scripts de `r_son00.wad`, `r_perm.wad`, `r_heroa00.wad` desmontados por ferramenta própria Lua 5.2 float de 4 bytes (`IFFHeader.m_Length` em `h - 0x60 + 4` medido desde `IFFLuaScriptChunkHeader` em `h`; bytecode `data[h + 0x204 : h + m_Length]`).
  - VMs (`LuaScriptAllocatorHookLoc` em `0x1405a6a1f`) **não** carregam `io` ou `os` (`io == nil`); erro Lua não tratado entra em `0x14063d4d0`, formata rastreamento (`printf` em `0x14063d610`) e executa `__debugbreak()` (`int 3`, `0xCC`) em `0x14063d629` (`STATUS_BREAKPOINT` / `0x80000003`).
  - Injetar `_G.__COOP_CFG` no buffer Lua em `hk_IFFProcessLuaScriptChunk` (`0x140466de0`), hook em `0x14063d610` pela área livre de 19 bytes `0xCC` em `0x14063d4ad`, e patch em `0x14063d629` (`0xCC -> 0x90`) dá log completo de erros Lua sem derrubar o processo.
- **Hook cooperativo em VM única de `son00` (`gameart/scripts/libraries/creature/locomotion.lua`):**
  - `locomotion.lua` recebe `require` e `.Install()` em `heroa00/main.lua` e `son00/main.lua`.
  - Filtrar `OnCreatureUpdate(crt)` por `crt == game.AI.FindSon()` executa o loop na VM `lua_State*` própria de `son00`, onde `son` (`Atreus`), `player = game.Player.FindPlayer()` (`Kratos` + `player.Pad`), `_G.__coop_override_until`, `son:SetActuator`, `son:Warp` e `_G.OnCommandSonStart(son, cmd)` (`"Regular"`, `"Charged"`, `"SwitchArrow"`, `"Tap"`) residem juntos.

## <a id="6-guesses--remaining-unknowns"></a>6. Hipóteses e desconhecidos restantes

- **Hipóteses:** sincronizar vida/transformações dos inimigos ou transmitir a visão do host eliminaria divergências dos inimigos na tela cliente durante combates longos.
- **Desconhecidos:** comportamento das transições de carregamento entre reinos (saltos de `CompletedCineNumber`) em sessões de várias horas.

## <a id="7-test-log"></a>7. Registro de testes

- Executados `coop_mcp.game_identity` e `coop_mcp.detect_engine` contra `<game dir>\GoW.exe` (somente leitura).
- Executado `local/decompile_lua52.py` para desmontar todos os scripts Lua 5.2 de `r_son00.wad`, `r_perm.wad`, `r_heroa00.wad`.
- Executado `local/coop_mod/test_sync.py`: `5 checks, 5 twins, 0 failed — ALL OK` (`accept_stale_seq`, `no_cmd_repeat`, `double_apply_cmd`, `ignore_sync_move`, `no_leash`).
- Compilada `version.dll` (`cl.exe` 14.44.35207 x64), provisionadas 2 instâncias isoladas por hardlinks com `tools/gamepool/gamepool.py --config local/gow_gamepool.json provision --pairs 1`.
- Executado `local/coop_mod/run_live_qa.py`:
  - Verificado redirecionamento por `SHGetKnownFolderPath` para `<instance>\saves` e hashes SHA-256 100% inalterados de `%USERPROFILE%\Saved Games\God of War`.
  - Verificado host `GoW.exe` ativo (`PID 27392`) + `tools/chaos` (perfil `bad_wifi`: latência 35±25ms, perda base 2% + rajada 60%, reordenação 2%, duplicação 0,5%): `97` pacotes cliente enviados, `94` únicos ordenados aceitos (`rx_seq=96`), `704` pacotes host recebidos, `3/3` comandos confiáveis (`Regular`, `SwitchArrow`, `Charged`) aplicados exatamente uma vez (`ack=3`).
  - Verificada inicialização simultânea de 2 instâncias `GoW.exe` (`Host PID 27392` + `Client PID 16076` com `BypassSteamStub=1`, `BotMode=1`): ambas chegaram a `[COOP] READY` simultaneamente e trocaram pacotes de estado `cmsgpack` ativos (`Client rx=108, rx_seq=3944`).
