# <a id="god-of-war-2018"></a>God of War (2018)

| | |
|---|---|
| Motor | Motor proprietário da Santa Monica Studio (nome interno **Kinetica**, branch `//int8-code/main81`), 64 bits, DirectX 11, scripts de jogabilidade Lua 5.2 |
| Versões testadas | Steam AppID `1593500`, build `11168363`, `GoW.exe` `1.0.475.7534` (`20,083,552` bytes, carimbo PE `0x628e8031` / `2022-05-25`, SHA-256 `caebcb027980d7eac9203d190f9ee649eebc549f8defce138e2114dc91f40452`) no Windows 11 x64 |
| Projetos | Protótipo funcional de modo cooperativo assimétrico em rede Kratos + Atreus (`version.dll` + `mods\lua\gameart\scripts\libraries\creature\locomotion.lua`). Bases de referência para mods: [Nukem9/godofwar-gameplay-tweaks](https://github.com/Nukem9/godofwar-gameplay-tweaks), [adore11s/God-of-War-VR-Mod](https://github.com/adore11s/God-of-War-VR-Mod) (MIT), [kainotoa/GOWTool](https://github.com/kainotoa/GOWTool) |
| Nível de QA | `automated` (suíte independente de sincronização + variantes de mutação `5/5`, teste UDP com host `GoW.exe` real + retransmissor `tools/chaos` `bad_wifi` e teste simultâneo de sincronização de host + cliente em duas instâncias `GoW.exe` em 1 PC) |
| Última atualização | 2026-10-28 |

## <a id="where-things-stand"></a>Situação atual

Não existia mod cooperativo público para *God of War (2018)* no PC antes deste trabalho. Usando engenharia reversa estática e em execução na compilação Steam `11168363` (`GoW.exe` `1.0.475.7534`), construímos e verificamos um **mod cooperativo assimétrico em rede para 2 jogadores, Kratos + Atreus**:
- **Jogador 1 (host)** controla **Kratos** (`heroa00`) e executa o estado autoritativo do mundo, combate e história.
- **Jogador 2 (cliente)** controla **Atreus** (`son00`) por UDP não bloqueante (`socket.core` + `cmsgpack` embutidos em `GoW.exe`), comandando locomoção (`SetActuator` + `Warp`), corrida/movimento lateral, disparos de flechas (`Regular` / `Charged`), troca do tipo de flecha (`SwitchArrow`) e invocações rúnicas (`Tap`).

## <a id="existing-work"></a>Trabalhos existentes

Pesquisados em 2026-10-28: diretório, issues e PRs deste repositório, busca de repositórios GitHub (incluindo forks) e busca na web cobrindo Nexus Mods, ModDB, Reddit e notícias. Notas brutas: [NOTES.md](NOTES.md).

- **Mods cooperativos / multiplayer anteriores:** nenhum encontrado para *God of War (2018)* ou *God of War Ragnarök*. Speclizer mostrou um vídeo de Atreus jogável para um jogador em 2022, não um mod cooperativo.
- **[Nukem9/godofwar-gameplay-tweaks](https://github.com/Nukem9/godofwar-gameplay-tweaks)** (último commit `2024-02-01`): proxy C++ `version.dll` com hooks em `IFFProcessLuaScriptChunk` (`0x140466de0`) e `LoadLuaScriptChunk` (`0x140466260`) para extrair bytecode Lua 5.2 de `.wad` e compilar/injetar substituições-fonte `.lua` de `<game dir>\mods\lua\` em execução.
- **[adore11s/God-of-War-VR-Mod](https://github.com/adore11s/God-of-War-VR-Mod)** (licença MIT, último push `2026-10-26`): proxy C++ `version.dll` com código completo, compilado para este executável Steam exato (`PE timestamp 0x628e8031`).
- **[kainotoa/GOWTool](https://github.com/kainotoa/GOWTool)** e **[JeanxPereira/GoWToolkit](https://github.com/JeanxPereira/GoWToolkit)**: navegadores e extratores de recursos para arquivos `.wad`, `.toc`, `.lodpack` e `.texpack`.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

Observado estaticamente e verificado em execução na compilação Steam `11168363` (`GoW.exe` `1.0.475.7534`, base da imagem `0x140000000`; desmontagem completa e detalhes dos hooks em [NOTES.md](NOTES.md)):

- **Binário sem criptografia e cabeçalho SteamStub v3.1:**
  - `.text` (`13.3 MB`), `.rdata` (`3.1 MB`) e `.data` não são criptografados em disco (indicadores `SteamStub` em `0x14519f230` = `0x06`, sem criptografia de seções).
  - O ponto de entrada PE é `0x14519f310` (`.bind`); o verdadeiro `mainCRTStartup` MSVC (`OriginalEntryPoint`) está em `0x1403ec680` (`RVA 0x3ec680`).
  - Para executar uma segunda instância cliente `GoW.exe` simultaneamente em um PC, um patch em `0x14519f310` com salto relativo de 5 bytes (`E9 6B D3 24 FB`) para `0x1403ec680` e um hook na IAT `steam_api64.dll!SteamAPI_RestartAppIfNecessary` (`0x140d49328`) retornando `false` permitem instâncias lado a lado com `steam_appid.txt` (`1593500`).
- **Scripts Lua 5.2 em arquivos `.wad` e isolamento das máquinas virtuais:**
  - A varredura dos 597 `.wad` em `<game dir>\exec\wad\pc_le\` encontrou **6.627 blocos `IFFLuaScriptChunkHeader` sem compressão** (`IFFHeader` tipo `0x24`, `0x60` bytes + cabeçalho de caminho/contexto de `0x204` bytes), representando **1.423 scripts Lua únicos** (`%PROJ_PATH%/gameart/scripts/...`). Observação: `IFFHeader.m_Length` (offset `+4` do `IFFHeader` de `0x60` bytes) é medido desde o início de `IFFLuaScriptChunkHeader`; portanto, a fatia de bytecode Lua é `[chunk_start + 0x204 : chunk_start + m_Length]`.
  - Cada personagem (`heroa00` para Kratos, `son00` para Atreus) executa em sua **própria máquina virtual `lua_State*` separada**. Na VM de `son00`, `game.AI.FindSon()` retorna Atreus (`son`), `game.Player.FindPlayer()` retorna Kratos (`player`, incluindo `player:GetWorldPosition()`, `player:GetWorldForward()` e `player.Pad`), e `_G.OnCommandSonStart(son, cmd)` + `locomotion.SetActuator` executam nativamente na mesma VM.
  - As VMs Lua do jogo **não** carregam as bibliotecas padrão `io` ou `os` (`io == nil`); qualquer erro Lua não tratado chama o tratador de `GoW.exe` (`0x14063d4d0`), que formata o rastreamento em `0x14063d610` e executa `__debugbreak()` (`int 3`, `0xCC`) em `0x14063d629` (`STATUS_BREAKPOINT` / `0x80000003`). Injetar a configuração diretamente no buffer-fonte Lua em `hk_IFFProcessLuaScriptChunk` e aplicar patch em `0x14063d629` (`0xCC -> 0x90`) evita que erros Lua derrubem o processo.
- **Rede e serialização embutidas (`socket.core` + `cmsgpack`):**
  - Toda VM Lua do jogo pré-carrega `socket.core` (`0x140a05bd0`, LuaSocket TCP/UDP) e abre `cmsgpack` (`0x1409fa370`, MessagePack com float de 32 bits).

## <a id="what-we-built"></a>O que construímos

1. **Proxy `version.dll` + carregador Lua 5.2 em execução + múltiplas instâncias e isolamento de salvamentos:**
   - Encaminha as 17 exportações de `C:\Windows\System32\version.dll`.
   - Hooks em `IFFProcessLuaScriptChunk` (`0x140466de0`) e `LuaScriptChunkMemoryAllocatorHookLoc` (`0x1404662f2` -> trecho de 14 bytes em `0x140466dee`) compilam fontes `.lua` de `<game dir>\mods\lua\...` com as próprias funções `luaL_newstate` (`0x1409e4c60`), `lua_load` (`0x1409e3720`) e `str_dump` (`0x140a03650`) de `GoW.exe`, acrescentando as configurações `[Coop]` de `coop_config.ini` no início em `_G.__COOP_CFG`.
   - Hooks em `LuaScriptAllocatorHookLoc` (`0x1405a6a1f` -> trecho de 14 bytes na área `0xCC` em `0x1405a0fae`), `LuaGoldPrint` (`0x1405aacb0`), `LuaPrint` (`0x1405aacc0`) e tratador de erro Lua (`0x14063d610` -> `0x14063d4ad`, além de `nop` em `0x14063d629`) registram toda saída Lua e rastreamentos em `coop_lua.log`.
   - Hook na IAT `SHELL32.dll!SHGetKnownFolderPath` (`0x140d485c0`) isola salvamentos em `<instance dir>\saves\God of War\`; hook na IAT `USER32.dll!GetForegroundWindow` (`0x140d487a8`) retorna `Renderer::WindowHandle` (`0x14504c390`) para as instâncias em segundo plano continuarem renderizando e processando entrada.
   - Hooks em `GameModule::ShowHideSLI` (`0x140850160`) e `StartTimerSLI` (`SLIFunctionTable[360]` em `0x1411cc4c8`) pulam os logotipos iniciais (`BootSiePresentsLogo`, `Boot_SMS_Logo`), reduzindo a entrada no mundo para aproximadamente 12-14 segundos.
2. **Módulo de sincronização cooperativa `mods\lua\gameart\scripts\libraries\creature\locomotion.lua`:**
   - Executa na VM de `son00` (`crt == game.AI.FindSon()`).
   - Abre socket UDP não bloqueante (`socket.core.udp()`) e troca pacotes binários de estado `cmsgpack` (`t="H"` do host, `t="C"` do cliente).
   - Suprime chamadas autônomas de `SetActuator` pela IA de Atreus (`_G.__coop_override_until`) enquanto aplica o movimento-alvo do jogador 2 (`son:SetActuator` + `son:Warp` interpolado) a cada quadro, limitado a 35 m de Kratos e pausado quando `son:IsDoingSyncMove()` está ativo (cenas, animações em dupla, pose da tela de título).
   - Entrega comandos discretos de combate de Atreus (`Regular`, `Charged`, `SwitchArrow`, `Tap`) repetidos em 6-8 pacotes com eliminação de duplicatas por sequência (`cs > coop.last_applied_cmd_seq`), para `_G.OnCommandSonStart(son, cmd)`.

## <a id="qa"></a>QA

Verificação automatizada (`qa: automated`):

1. **Suíte independente de sincronização e variantes de mutação (`test_sync.py`):**
   - `5 checks, 5 twins, 0 failed — ALL OK`:
     - `check_stale_rejected` (detecta `accept_stale_seq`)
     - `check_cmd_loss_and_dedup` com perda determinística de 40% dos pacotes (detecta `no_cmd_repeat` e `double_apply_cmd`)
     - `check_sync_move_guard` durante `IsDoingSyncMove()` (detecta `ignore_sync_move`)
     - `check_leash_clamp` além de 35 m de Kratos (detecta `no_leash`)
     - `check_position_convergence` durante 30 atualizações
2. **Host `GoW.exe` real + `tools/chaos` (perfil `bad_wifi`) + teste simultâneo de host e cliente em duas instâncias `GoW.exe` (`run_live_qa.py`):**
   - Duas instâncias isoladas por hardlinks (`156,589` hardlinks cada) provisionadas com `tools/gamepool/gamepool.py --config local/gow_gamepool.json provision --pairs 1`.
   - Verificado que `Host` (`instance 0`) chegou a `[COOP] READY` em `12.0s`, redirecionou salvamentos a `<instance 0>\saves` e trocou `97` pacotes do cliente / `704` do host por `tools/chaos` (`bad_wifi`: latência de 35±25 ms, perda-base de 2% + rajadas de 60%, reordenação de 2%, duplicação de 0,5%), com `94` pacotes únicos em ordem aceitos e os `3/3` comandos de combate (`Regular`, `SwitchArrow`, `Charged`) aplicados exatamente uma vez (`ack=3`).
   - Verificado que a segunda instância `GoW.exe` simultânea (`Client`, `instance 1` com `BypassSteamStub=1`, `BotMode=1`) iniciou ao lado de `Host`, chegou a `[COOP] READY role=client` e recebeu `108` pacotes reais de estado do host (`rx_seq=3944`, `kratos=(-399.59,38.00,-800.85)`, `son=(-400.71,38.09,-808.64)`).
   - Hashes SHA-256 de `%USERPROFILE%\Saved Games\God of War` conferidos antes e após todas as execuções (`100%` inalterados).

## <a id="how-to-play"></a>Como jogar

1. Extraia `version.dll`, `mods\lua\gameart\scripts\libraries\creature\locomotion.lua` e `coop_config.ini` na pasta do jogo de cada jogador (ou cópia de teste isolada).
2. Conecte os PCs na mesma LAN ou LAN virtual (Tailscale / ZeroTier).
3. No **jogador 1 (host - Kratos)**, defina `Role=host` e `Port=27960` em `coop_config.ini`.
4. No **jogador 2 (cliente - Atreus)**, defina `Role=client`, `HostIP=<Host_IP>`, `Port=27960` e `ClientPort=27961` em `coop_config.ini`.
5. Inicie nos dois PCs e carregue o mesmo salvamento. O jogador 2 controla Atreus pelo controle (analógico esquerdo para mover, Cross para correr, L2 para mover lateralmente/mirar, Square para flecha Regular, Triangle para Charged, direcional para cima para alternar flechas Light/Shock, R1 para Runic Summon).

## <a id="known-issues"></a>Problemas conhecidos

- **Câmera assimétrica no cliente:** o cliente executa seu próprio mundo no mesmo ponto de salvamento, espelha as coordenadas de Kratos e Atreus do host e envia a entrada e os comandos de combate do jogador 2 ao host. Sincronização completa de inimigos no cliente ainda não implementada; para melhor experiência visual, o jogador 2 pode assistir à transmissão de baixa latência do host (Parsec / Steam Remote Play) enquanto o cliente local ou emissor UDP de controle envia comandos, ou jogar no mundo local sincronizado ao lado do host.
- **Movimentos sincronizados e cenas:** durante sequências `IsDoingSyncMove()` (cenas, entrada no barco, finalizações em dupla e pose de repouso da tela de título antes de Continue), a IA autônoma assume Atreus temporariamente, evitando bloqueios de progresso nas sequências programadas.

## <a id="sources"></a>Fontes

- https://github.com/Nukem9/godofwar-gameplay-tweaks
- https://github.com/adore11s/God-of-War-VR-Mod
- https://github.com/kainotoa/GOWTool
- https://github.com/JeanxPereira/GoWToolkit
