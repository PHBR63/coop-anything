# <a id="modern-warfare-2-2009--session-notes"></a>Modern Warfare 2 (2009) — notas de sessão

Data da sessão: 2026-10-19. Objetivo: **campanha completa, com suas cenas**, em cooperativo com
amigos (Spec Ops não é o objetivo). Mod cooperativo de campanha existente (COD-MOD, abaixo) foi testado
em 2026-07-04 e funciona mal.

## <a id="game-identity-agentsmd-rule-5"></a>Identidade do jogo (regra 5 de AGENTS.md)

- Título: Call of Duty: Modern Warfare 2 (2009), Steam appid 10180 (SP: campanha + Spec Ops)
- Steam buildid **25374375** (idioma russo; depots 10181, 10182, 10189)
- `iw4sp.exe`: **x64** (PE machine 0x8664), data de link PE 2026-09-16, 4.480.056 B,
  SHA-256 `2F8C9CFDA1B8C0FB308FD9719577154E8222FC7654F5E8F1BF54579BCA69D805`
- Inclui `steam_api64.dll`, `bink2w64.dll`, `SteamAPIUpdater.dll`, `UpdateDLLWrapper.dll`,
  `CoDCleaner.exe`; conteúdo em `main\iw_00..iw_09.iwd`, `zone\<language>\*.ff` (96 zonas)
- Motor: IW 4.0 (binário fechado). SO: Windows 11
- Caminhos locais exatos e logs do proprietário: `local/` (privado)

## <a id="observations-checked-this-session"></a>Observações (conferidas nesta sessão)

- Repositório não cobria MW2 (2009): `directory.yaml` e `games/` só mencionam MW3 (2011);
  `engine-families.md` não tem linha IW-engine (grep `IW ?4|IW5|Call of Duty|id Tech 3` → 0).
  `gh` não instalado neste PC; issues/PRs abertos não conferidos.
- **Atualização de 64 bits de 2026 também atingiu MW2.** `iw4sp.exe` é x64, linkado em 2026-09-16. README
  da correção ultrawide confirma “the September 2026 64-bit MW2 update”
  (https://github.com/ISASTO/mw2-ultrawide-fix).
- **Zonas novas são de 64 bits.** Todos `.ff` mantêm magic `IWffu100` e versão `0x114`, mas
  após descomprimir primeiro bloco, XAssetList tem ponteiros de 8 bytes:
  `common.ff` → `…0000020c 00000000 ffffffff ffffffff 00002448 00000000 ffffffff ffffffff`
  (contagem de strings, ponteiro de 64 bits, contagem de assets, ponteiro de 64 bits). `x_coop.ff` do mod antigo tem ponteiros de 4 bytes
  (`00000139 ffffffff 00000025 ffffffff`). Mesma mudança de MW3, veja
  `games/modern-warfare-3/NOTES.md` “STOP: the owner's install is the 64-bit build”.
- **COD-MOD** é o único mod cooperativo de campanha encontrado. Partes na instalação do proprietário:
  - `iw4sp.hk`: DLL x86, versão `COD-MOD: 3.223`, FileDescription “Call of Duty -
    Singleplayer Modification”, compilada em 2020-09-16; créditos NTAuthority, kiwidog, archony.
  - `iw4sp_codmod.exe`: executável x86, data de link PE 2009-11-07 (log imprime
    `Build 159 … Fri Nov 06 2009`, ou seja, versão 1.0.159).
  - `zone/custom/x_coop.ff`, `a_coop_models.ff`, `z_customanim.ff` (zonas 32 bits, 2020) e
    `spdata/x_core.iwd` (menus incluindo `ui/coop_lobby.menu`, `maps/{trainer,boneyard,ending}.d3dbsp.ents`,
    ~20 arquivos `weapons/sp/*`), todos datados de setembro-outubro 2020.
- **Fonte da DLL:** https://github.com/FreeTheTech101/cod-mod (momo5502, 223 commits =
  “3.223”, último commit 2014-12-13 `db305c19`). Sem arquivo LICENSE. `code/PatchMW2_Coop.cpp`
  só reativa o **código de rede cooperativo Spec Ops** embutido do motor por IP direto para o
  executável 32 bits 1.0.159: pula conexão IWNet, força porta 28960, ignora incompatibilidade de protocolo/XUID,
  inclui `connect` → `connect_coop`, mais busca de grupo no servidor mestre. Não contém
  **lógica de campanha**. Conteúdo cooperativo fica em `x_coop.ff` + `x_core.iwd`, de autor
  2020 desconhecido. Repositório também inclui binários originais `iw4sp_159.exe` e
  `iw4sp_184.exe`.
- Distribuição: guia Steam “Tutorial - Modern Warfare 2 Coop Campaign Mod” (2021-10-11,
  pacote mega.nz, Hamachi, host + 1 cliente, início por `iw4sp_codmod.exe`); comentário 2023 diz
  “Mission big brother” congela ao carregar
  (https://steamcommunity.com/app/10180/discussions/0/3087772148451672664).
- **Execução do proprietário (2026-07-04, logs em `local/`):** com amigo pelo mod; mapas
  trainer, roadkill, favela, invasion, favela_escape, arcadia. Nos logs:
  - falha `Fatal error (0xc0000005) at 0x00401772` ao carregar favela_escape (minidump);
  - membro do lobby expirou; desconexões repetidas “host ended the game”;
  - fim/falha de missão passa por telas Spec Ops ausentes
    (`coop_eog_summary.menu`, `sp_eog_summary.menu`, `hud_show_timer`,
    soundaliases `so_defeat_ranger`, `so_defeat_woodland`);
  - avisos do criador favela_escape “dospawn called twice in frame”;
  - muitos reinícios de nível inteiro (cada um imprime novo `network coop random seed`).
  - Dvars cooperativas observadas: `coop`, `coop_mapName`, `coop_maxFramesPerPacket 20`,
    `coop_minFramesClientCanBeBehind 2`, `coop_maxPacketUserCmds 32`, `coop_validateData`.
- **iw4x-sp** (AlterWare): cliente individual que exige executável rebaixado 1.0.159 do
  CDN AlterWare; sem menção a cooperativo (https://forum.alterware.dev/t/iw4x-singleplayer-install-guide/383).
  PCGamingWiki supostamente diz (trecho de busca, página 403 ao buscar) que IW4x-SP não funciona
  com a versão mais recente.
- **IW4x** (https://github.com/iw4x/iw4x-client): cliente MP aberto, não campanha.

## <a id="derived-reasoning-not-tested"></a>Deduções (raciocínio, não testado)

- COD-MOD **não pode rodar na instalação atual do proprietário**: executável 32 bits não carrega
  zonas 64 bits e `x_coop.ff` 32 bits não carrega no executável 64 bits. Trabalhar no
  mod existente exige **cópia de teste 32 bits** separada (manifestos antigos dos depots).
- Campanha cooperativa MW2 dispensa novo código de rede: executável SP já traz cliente/servidor de 2 jogadores
  (Spec Ops). Trabalho é (a) fazer scripts de cada nível de campanha tratarem
  segundo jogador (`level.player` → jogadores, cenas, veículos, checkpoints, falha/reinício),
  (b) fluxo cooperativo de checkpoint/reinício no lugar de telas finais Spec Ops.
- Reclamações do proprietário correspondem a (b) e lacunas por missão: reinícios inteiros em vez de
  checkpoints, telas finais ausentes, avisos de criação, falha ao carregar.
- Cenas Bink entre missões rodam localmente em cada PC; cenas no motor são roteirizadas
  para um jogador e exigem adaptação por missão para o segundo.

## <a id="guesses-unverified"></a>Hipóteses (não verificadas)

- Limite: caminho Spec Ops do motor provavelmente tem limite fixo de 2 jogadores.
- Compilação 64 bits talvez ainda tenha o mesmo código de rede, mas não há ferramentas de 64 bits.

## <a id="unknowns"></a>Desconhecidos

- Autor, licença e fonte de `x_coop.ff` / `x_core.iwd`; quantas missões cobrem.
- Ids antigos (32 bits) dos manifestos dos depots 10181/10182/10189 e tamanhos.
- Se mais de 2 jogadores são possíveis no motor SP.
- Se Spec Ops online oficial ainda funciona na compilação 64 bits.
- O que é 0x00401772 do minidump (exige executável 1.0.159 no Ghidra).

## <a id="decisions-2026-10-19"></a>Decisões (2026-10-19)

- **2 jogadores**, **mirar compilação Steam atual de 64 bits** (amigos não devem precisar
  rebaixar versão). Sem download de depot 32 bits por enquanto. Caminho 2 (construir do zero) na compilação 64 bits;
  COD-MOD apenas como referência.

## <a id="phase-3-recon-of-the-64-bit-build-static-on-a-copy-of-the-exe-in-local"></a>Reconhecimento da fase 3 da compilação 64 bits (estático, numa cópia do executável em `local/`)

Observações:
- `iw4sp.exe` PE32+, base 0x140000000, 8 seções. Ponto de entrada numa seção `.bind`
  (raw 0x39248 B, entropia 7,96): wrapper DRM SteamStub. Entropia `.text` 6,55, então
  código não parece criptografado. Caminho PDB do diretório de depuração termina em
  `iw4-pc\game\pc\iw4sp_steam.pdb` (pasta interna `outrun`).
- Importações de DLLs substituíveis por proxy: `d3d9.dll` (Direct3DCreate9), `WINMM.dll`
  (timeGetTime, timeBeginPeriod, timeEndPeriod), `X3DAudio1_7.dll`, `bink2w64.dll`.
  Rede: sockets `WSOCK32`/`WS2_32`, `steam_api64.dll` incluindo SteamNetworking,
  SteamMatchmaking, SteamFriends. `SteamAPIUpdater.dll` e `UpdateDLLWrapper.dll` na
  pasta são sobras 32 bits que executável x64 não pode carregar.
- **Todo o código de rede Spec Ops continua presente** (strings): `coop`, `coop_mapName`
  (“The name of the map to load in co-op mode”, padrão `so_killspree_trainer`),
  `coop_autoLaunch`, `coopLaunch`, `coopConnect`/`coopAccept`/`coopReject COOP_FULL`,
  `coopLoaded`, `coopRestart`, `coop_maxFramesClientCanBeBehind`,
  `coop_fastForwardThreshold`, `coop_maxPacketUserCmds`, `connect %u.%u.%u.%u %u`,
  `connect_lobby`, `joinParty`, callbacks de lobby Steam (`LobbyCreated_t`, `LobbyEnter_t`,
  `GameLobbyJoinRequested_t`), “Invalid co-op packet - references invalid clientNum %i”.
- Console e hooks de mod no executável: `monkeytoy`, `cmdlist`, `devmap`, `spdevmap`,
  `sv_cheats`, `fs_game` (“Game data directory. Must be \"\" or a sub directory of
  'mods/'."), `fs_basegame`, `devraw`, `raw_shared`. Ausentes: `useFastFile`, `mod.ff`,
  string “Waited %d msec for asset”.
- `players/config.cfg` do proprietário associa `` ` `` e `~` a `toggleconsole`.
- Instalação agora também contém zonas MP (`mp_*.ff`, `common_mp.ff`, `patch_mp.ff`) junto
  às SP; 96 zonas em `zone/russian`.
- **Scripts podem ser lidos de zonas 64 bits**: rawfiles inline `name\0` + fluxo zlib;
  pequeno scanner (sem parser de assets) descomprime a zona e extrai. Resultados:
  `common.ff` 455 rawfiles, `favela.ff` 89, `so_killspree_favela.ff` 2 (mantidos em `local/`,
  dados do jogo, nunca num PR). Scanner tem ~50 linhas Python; vale incluir em `tools/`.
- Nível Spec Ops é mapa de campanha com script diferente:
  `maps/so_killspree_favela.gsc` inclui `maps\favela_code`, chama
  `maps\favela_precache::main()`, `favela_fx`, `favela_art`, `maps\_load::main()` e
  executa seus objetivos em `level.players`.
- Scripts comuns já conhecem segundo jogador: `maps/_utility.gsc` `is_coop()` é
  `IsSplitScreen() || GetDvar("coop") == "1"` e verifica existência de `level.player2`;
  chamadas `is_coop()`/`is_specialop()` em `_loadout`, `_load`, `_gameskill`, `_ac130`,
  `_specialops*`, `_snowmobile_drive`, `_spawner`, `_endmission`, `_autosave`, `_coop` e
  outros. Contagens: `common` 1624 `level.player` vs 270 `level.players`; scripts de nível
  `favela` 80 `level.player`, 0 `level.players`.
- Relatado, não verificado (trecho de busca; Nexus 403): mod de controle Nexus diz que a
  compilação 64 bits exige carregador x64 `winmm.dll` (https://www.nexusmods.com/codmw2/mods/83).

Deduzido:
- Campanha cooperativa 64 bits = iniciar mapa de campanha com `coop 1` pelo
  lançamento cooperativo existente, então corrigir scripts do nível (e alguns comuns)
  para `level.player2`: criação, cenas, veículos, checkpoints, falha,
  reinício, fim de missão. Novo código de rede dispensável.
- Entregar GSC alterado exige carregamento de arquivos soltos por `fs_game`/`mods/`
  (não testado) ou DLL proxy (`winmm.dll` ou `d3d9.dll`) interceptando busca de rawfile.

Desconhecidos (próximos experimentos, todos exigem cópia de teste):
- `monkeytoy 0` abre console nesta compilação?
- Definir `coop_mapName` para mapa de campanha e iniciar cooperativo carrega o mapa? `_load`
  então dá aos dois uma criação funcional?
- `mods/<x>/maps/*.gsc` solto sobrepõe a cópia da zona?
- Duas instâncias podem rodar num PC e conectar por `connect 127.0.0.1 <port>`, para
  QA com bots sem segunda conta Steam?

## <a id="phase-23-experiments-on-a-test-copy-2026-10-19"></a>Experimentos das fases 2/3 numa cópia de teste (2026-10-19)

Preparação: cópia completa (183 arquivos, 11,3 GB, sem arquivos antigos COD-MOD) numa
pasta de teste separada; backup de `players\` do proprietário em `local/backup` antes. Script inicializador
monitora todo `iw4sp.exe` a cada 200 ms e encerra os que não forem da cópia de teste.

Observações:
- **Incidente:** execução 1 funcionou com `steam_appid.txt` presente, mas jogo **excluiu
  `steam_appid.txt`**. Execução 2 (sem arquivo/variáveis): stub saiu com código
  53 e **Steam reiniciou a instalação real** com mesmos argumentos. Regravou
  `players\config.cfg` do proprietário em ~6 s antes de ser encerrado. Restaurado do
  backup, SHA-256 igual ao original; nenhum outro arquivo real mudou.
  **Correção funcional:** iniciar cópia com variáveis `SteamAppId=10180` e
  `SteamGameId=10180` (6 execuções depois, todas da cópia; instalação real
  intocada). Lição: backup da configuração antes da primeira execução e guarda
  contra Steam reiniciar instalação real.
- Jogo rodou da cópia e chegou ao principal (menu SP agora oferece também
  “Multiplayer”). Nada escrito fora da pasta (conferidos LocalAppData,
  AppData, Documents, Saved Games, ProgramData).
- **`+set`/`+exec` da linha de comando ignorados** (janela continuou tela cheia 1920x1080, `quit`
  nunca executou, sem log).
- **Linhas `config.cfg`:** `seta …`, `set …` e `bind …` fazem efeito (`set r_mode
  "1024x768"` redimensionou; `seta cooptest_marker` foi salvo de volta). `quit`,
  `cmdlist`, `wait`, `exec` e `set logfile 2` de `config.cfg` sem efeito visível: jogo
  nunca saiu e nenhum `console.log` apareceu.
- Console: enviar `` ` `` (WM_KEYDOWN/WM_CHAR) à janela, mesmo após trazê-la
  ao primeiro plano, não abriu console (com `seta monkeytoy "0"`). F10 associado a
  `exec` também nada fez. Não se sabe se console removido ou mensagens
  ignoradas; entrada global sintética (SendInput) não tentada, poderia digitar em outros apps.
- Capturas: PrintWindow retorna preto para D3D9; tornar janela TOPMOST
  brevemente e copiar só retângulo cliente funciona. (Primeira cópia simples pegou
  janela sobreposta de outro app; excluída. Nunca copiar tela sem TOPMOST.)
  Sobreposição Discord desenha sobre jogo; guarde capturas em `local/`.
- **Segunda instância:** iniciar teste duas vezes fez segundo processo sair imediatamente;
  só uma roda (causa desconhecida: mutex ou Steam).

Deduzido:
- Sem DLL nativa não há como controlar esta compilação por scripts: sem linha de comando,
  comandos iniciais, console ou log. DLL proxy (`winmm.dll`, importada pelo executável
  e não KnownDLL) é próximo passo: log em arquivo, comandos pelo código,
  depois interceptar carregamento rawfile para nosso GSC.
- QA com dois clientes num PC também exige DLL (instância única), ou outro PC/VM.

## <a id="phase-35-native-dll-on-the-64-bit-build-2026-10-19"></a>Fases 3–5: DLL nativa na compilação 64 bits (2026-10-19)

Ferramentas (versões fixadas, SHA-256 conferido, portáteis em `local/tools`): llvm-mingw 20261006 (ucrt x86_64,
`317492c4…d17a`), Ghidra 12.1.4 (`ddac49f9…d4db`), Temurin JDK 21.0.12.1+1 (`f9d6e191…8b4e`).
Fonte do mod em `local/mw2coop` por enquanto (terá próprio repositório).

Observações (cada uma verificada executando cópias; RVAs relativos à base, compilação
PE timestamp `0x6aaaa257`, dvar `version` “IW4 2.0 build 14 . 2025 win64”):
- **Carregador:** proxy `winmm.dll` (180 exportações encaminhadas a System32) ao lado
  de `iw4sp.exe` carrega; base aleatória (ASLR), portanto endereços são RVAs.
- **Comandos:** `Cbuf_AddText(int, const char*)` @ `0x1ee890` (trava seção crítica 0x24,
  segura em outra thread). Comandos enfileirados executam, incluindo `map trainer` (campanha
  carrega), `quit`, `set`. Cabeça da lista do console @ `0x1315308` (`cmd_function_t` {next,
  name, dir, ext, fn}); 139 comandos, incluindo `listen`, `connect`, `coopLaunch`,
  `stopListening`, `connect_lobby`, `devmap`, `loadgame`. Novos comandos entram
  ligando nó à lista (feito para `mw2coop_party_join`).
- **Dvars:** `Dvar_FindVar(name)` @ `0x26bdf0` (trava de leitura). Layout: name +0, flags +8,
  type +0xC, current +0x10, latched +0x20, reset +0x30, hash next +0x58.
- **Logs:** `Com_Printf` e log em arquivo parecem removidos na compilação (sem string `console.log`, maioria
  das strings de impressão ausente). Dvar `logfile` ainda registrada. Estado lido de dvars/memória.
- **Scripts:** GSC solto não lido (testados `main/`, `raw/`; `fs_game` da configuração
  ignorado). `Scr_AddSourceBuffer` @ `0x217950` chama `DB_FindXAssetHeader(0x24 = rawfile)`
  @ `0xef5d0`, `DB_IsXAssetDefault` @ `0xefff0`, `DB_GetRawFileLen` @ `0xefdc0`,
  `Hunk_AllocateTempMemoryHigh` @ `0x2693f0`, `DB_GetRawBuffer` @ `0xefc70`. Substituir
  função (jmp absoluto de 14 bytes, mesma lógica + busca de sobreposição) faz
  `<game>\mw2coop\scripts\maps\trainer.gsc` vencer cópia da zona: dvar marcadora
  apareceu no jogo ativo.
- **Instância única:** jogo escreve PID em `<game dir>\__iw4sp` (oculto) e sai
  silenciosamente se PID é `iw4sp.exe` ativo (@ `0x2900a0`). Também exclui
  `steam_appid.txt` ao iniciar Steam (@ `0x240c30`). Segunda pasta (dados com hardlinks, executável próprio
  e `players/`) executa outra instância normalmente; vincula automaticamente UDP 28961.
- **Condição online:** `listen`/`connect` exigem Steam conectado e estado DemonWare
  (@ `0x115c07c`) == 4, alcançado ~7 s após início. Informado por `@PLATFORM_POPUP_CONNECTION`.
- **Handshake cooperativo por IP direto funciona nativamente.** `connect <ip> <port>` guarda porta sem converter
  em campo de ordem de rede; passe `htons(port)`: `connect 127.0.0.1 8305` mira 28960.
  Pacotes (registrados com wrappers WSOCK32 `sendto` #20 / `recvfrom` #17 na IAT):
  `coopConnect` (protocolo 0x1d, XUID, nome Steam) → `coopAccept` (leva `coop_mapName`) →
  `coopAcceptAck` → teste de banda `bw` → `bwres` → `coopLaunch <map>` → `coopLoaded`.
  Handler host @ `0x22d830` ignora `coopConnect` do próprio XUID; QA com duas cópias numa
  conta exige XUIDs distintos (tabela @ `0x1bbaad8`; só QA `!xuid_add`).
- **Grupo:** `coopLaunch` (@ `0xd25d0`) só define indicador (@ `0x5dd953`); quadro do grupo
  (@ `0xd74a0`) inicia quando grupo ativo (@ `0x5dd951`, objeto lobby @ `0x5dd958`
  +0x10), 2 membros (+0x70, +0xa8), teste de banda concluído (@ `0x5dd820` == 0). Membro
  sem contato por `coop_lobbyTimeout` (12 s) removido. Cliente normal ativa seu
  grupo entrando no **lobby Steam** do host (@ `0x28f1b0` → `0x22dda0` →
  `PartyClient_Join` @ `0xd7cb0`); `connect` simples pula isso, cliente não envia
  keepalives, ignora `coopLaunch` e cai. `mw2coop_party_join` repete
  `PartyClient_Join` sem busca de lobby Steam.
- **Resultado (m14):** host `set coop_mapName trainer; listen; coopLaunch`, cliente
  `mw2coop_party_join; connect 127.0.0.1 8305` → ambos carregam `trainer` com `coop 1`;
  script informa `level.players.size == 2` e `level.player2` definido nos dois;
  cliente vê modelo do host e nome; ~110 s cooperativos sem queda
  até interromper teste. Host reproduz cena inicial no motor, **cliente não**
  (visto ao vivo): cena roteirizada só para `level.player`.
- **Lockstep:** cliente também informa `sv_running 1` e compila scripts
  por conta própria; dvars `coop_maxFramesClientCanBeBehind`, `coop_fastForwardThreshold` e
  “network coop random seed” do log antigo apontam o mesmo. Ambos simulam; cada
  script substituído deve ser idêntico byte a byte (senão dessincroniza).

Deduzido:
- Rede necessária à campanha cooperativa existe e roda nesta compilação. Falta
  trabalho de scripts por missão (cenas, veículos, checkpoints, falha/reinício, fim e
  próximo nível), mais entrada para hospedar/entrar.
- Duas contas Steam reais devem seguir caminho nativo (convite Steam → lobby → grupo),
  sem `mw2coop_party_join` ou `!xuid_add`. Não testado: exige duas pessoas com suas contas.

Instalação do proprietário, seguimento do incidente: jogo real reiniciado também deixou arquivo oculto
`__iw4sp` (PID 24472 = reinício encerrado). Movido para `local/backup` para próxima
inicialização real não pedir “improper quit / safe mode”. Guarda agora lista também
arquivos ocultos.

## <a id="co-op-campaign-framework-ssdd-2026-10-19-in-progress"></a>Estrutura de campanha cooperativa, S.S.D.D. (2026-10-19, em andamento)

Construído (fonte `local/mw2coop`, conteúdo em `content/`):
- **Patches de scripts em vez de código do jogo distribuído:** `<game>\mw2coop\patches\<script>.patch`
  (`@@@ replace / with / end`, `@@@ append`) aplicados pela DLL ao texto da zona ao carregar;
  `tools/check_patches.py` aplica offline aos scripts extraídos (11 trechos OK).
  Scripts próprios em `<game>\mw2coop\scripts\` (`maps/_mw2coop.gsc`, `maps/_mw2coop_qa.gsc`).
  Log imprime hash por script alterado; hashes host/cliente iguais.
- **Modo:** campanha cooperativa = `coop 1` e mapa não chamado `so_*`; `is_specialop()` corrigido
  para false então (lobby define `specialops 1`, mandando `trainer` ao ramo Spec
  Ops: sem remoção de armas, sem IA ambiente, equipamento Spec Ops ao jogador 2).
- **Estrutura (`_mw2coop.gsc`):** reagrupar jogador 2 junto do 1 após ponto inicial e
  em cada teleporte do 1; sincronizar armas (ganhos/perdas do 1 ao 2, modo `both`
  em trainer); checkpoints = pontos iniciais do nível (indicador mais avançado define
  dvar `start`); sem salvamentos cooperativos; ambos caídos (sistema de reanimação `maps\_coop`) ou
  `missionFailedWrapper` → escurecer, host executa `fast_restart` (SV_MapRestart @0x22c970
  envia `coopRestart` ao cliente); `nextmission()` → pedido “nextmap <next level>”
  (transição por fazer). Pedidos script→DLL pela dvar `mw2coop_cmd`, só host age.
- **Patch trainer:** checkpoints timed_ads, bullet_penetration, frag, pit, course, end;
  munição infinita no estande para ambos; fim aplica invulnerabilidade, sem corrida, caminhada lenta e
  escurecimento também ao 2.

Encontrado no caminho (observado nas execuções):
- **Scripts cooperativos não podem ler maioria das dvars.** GSC `getdvar` numa sessão passa por
  `SV_GetDvarCoop` (@0x230fc0): só dvars com indicador em `0x20c4` retornam valor, demais
  retornam padrão, e nome+valor entram no checksum de validação. Assim,
  dvars do console e até `start` eram lidas como "" (pontos iniciais nunca aplicariam).
  DLL faz OR `0x80` em `start`, `mw2coop_qa`, `mw2coop_qa_phase` nas duas máquinas; depois
  cenário QA ficou visível aos scripts.
- **Erros de script silenciosos na versão comercial:** `Scr_Error` (@0x2226a0) só faz longjmp.
  Substituído por logger + longjmp do jogo (@0x2e485c). Cliente registra ~60
  longjmps desde carregar nível, host nenhum, com texto `va()` antigo (“Event EV_PLAY_FX”).
  Não causados pelo mod; desconhecido se cooperativo original faz igual (conferir).
- **Execução QA intro:** PASS dois jogadores, modo campanha, 2 junto do 1 (distância 0:
  trace de espaço livre não achou nada, alternativa usa mesmo ponto), mesmas armas (vazias). Então
  `GiveWeapon("m4_grunt")` da própria QA no 1 encerrou sessão: erro “no
  viewmodel set for player 0 for 'm4_grunt' in 'right' hand” (enviado como `coopDis`).
  `_loadout` de `trainer` define viewmodel só em `level.player` e no ramo
  campanha; próximo: mesmas mãos em ambos no cooperativo.

Próximo passo (2026-10-19): embarque de ambos onde campanha precisar.
Scripts de todos os mapas extraídos em `local/mw2-64/gsc/<map>` para
levantamento (ainda não feito).

## <a id="session-2026-10-20-intro-passes-restart-in-progress"></a>Sessão 2026-10-20: introdução aprovada, reinício em andamento

Observado (QA com duas cópias):
- **Erros só no cliente** vinham de `GetPlayerIntelIsFound` (builtin @0x18dea0): em
  cooperativo exige jogador local (estado do slot cliente == 2), então jogador do
  host falha no cliente. `maps\_intelligence` o executava ao carregar → sua thread morria
  só no cliente (deriva lockstep). Patch `_intelligence.gsc`: remover intel na sessão de campanha
  antes de `initialize_intel()`. Depois: 0 erros nos dois.
- **“no viewmodel set for player 0”** vem de cgame (@0xc5b70) para jogador *local*
  da máquina que desenha: jogador próprio do cliente (2). `maps\_loadout` define mãos só em
  `level.player`. Estrutura agora copia `GetViewModel()` do 1 ao 2 no início
  e a cada 0,25 s.
- Reagrupamento usava `PlayerPhysicsTrace` dentro do volume do parceiro, sempre caindo
  no mesmo ponto; agora `BulletTracePassed` (ignora parceiro) + trace do piso: 48 unidades.
- **QA `intro`: 6/6 PASS no host e cliente**, sem erros de script ou desconexão (04:53).
- QA `restart`: checkpoint `timed_ads` definiu dvar `start` nos dois; 2 caído (não
  morto); ambos caídos → `coop_alldowned`. Depois nada: (a) `watch_failure` chamou
  `mission_failed()` na própria thread, cujo `level notify("mw2coop_level_end")` a encerrou
  (corrigido: `level thread mission_failed()`), e (b) `maps\_coop`
  `level.revive_ent linkTo( self, "tag_origin" )` gera erro de script nos dois
  (builtin link @0x18ff30 → pai tem índice de modelo mas não DObj, @0x19004d): jogadores de campanha
  não têm modelo corporal (Spec Ops define por SetModelFunc). Patch `_coop.gsc`: vincular
  sem tag na sessão de campanha. Ambos aplicados, **ainda não testados**.
- DLL: erros registrados por local de chamada (RVA de retorno), permitindo buscar nome builtin
  na tabela de métodos.

## <a id="session-2026-10-20-later-restart-mission-end-progress-saving"></a>Sessão 2026-10-20 (mais tarde): reinício, fim de missão, progresso salvo

Observado (QA com duas cópias, `tools/qa_pair.sh`):
- **Pilhas de script no log DLL.** VM guarda posição ativa do código no rva
  0x1900b78 e posições salvas dos chamadores em `function_frame_start[]` (rva 0x18f44c0,
  0x28 bytes/quadro, posição primeiro; `function_count` em 0x18f44a0). Posições apontam ao
  buffer do programa (ponteiro rva 0x15a03e0). `Scr_GetFunctionHandle` (rva 0x216920)
  retorna offset da função no buffer, mas só enquanto tabela de scripts carregados existe:
  `Scr_EndLoadScripts` (rva 0x2166d0) a libera. DLL intercepta, mapeia todos os
  nomes encontrados nos textos fonte compilados (5414 em S.S.D.D.) e imprime
  `file::function +offset` da posição com falha e de cada chamador.
- Erros comerciais nem sempre encerram thread: um local registrou 100 ocorrências em 2,4 s.
- Com pilhas, erros restantes ao cair estavam em `maps\_coop` (corrigido):
  - `flag( "special_op_terminated" )` num indicador criado só por `maps\_specialops` (também lido por
    `kill_wrapper()` em qualquer sessão). `_mw2coop` agora o cria em campanha
    e define na falha/fim do nível como Spec Ops, parando HUD de reanimação
    e threads de jogador caído.
  - `player_coop_kill()` → `kill()` num jogador já invulnerável. Em campanha agora
    falha missão (reinicia checkpoint) em vez de matar; sangramento faz
    igual.
  - `player_coop_downed()` continuava após `player_coop_kill()` (em Spec Ops jogador morre
    ali), iniciando HUD de sangramento após sua limpeza; agora retorna ao encerrar
    nível.
- Erro no parser de patches (DLL e `check_patches.py`): bloco logo após `@@@ end` sem
  linha vazia era engolido. Corrigido nos dois; `_coop` agora informa 4/4.
- **QA `restart`: todas PASS no host/cliente, 0 erros** (05:18): checkpoint,
  2 caído, ambos caídos, `coopRestart` enviado/confirmado, nível volta ao checkpoint
  `timed_ads`, jogadores de pé.
- **QA `end` (ponto `end`): PASS nos dois, 0 erros**: fim atingido, próxima
  missão `roadkill` encontrada. DLL ainda não troca mapa.
- No PC, S.S.D.D. pula treino ADS cronometrado (`AA_timed_ADS_init`: `!level.console`) e
  define indicador imediatamente; checkpoint `bullet_penetration` segue `timed_ads` em
  um segundo. Esperado, não erro.

Progresso salvo (conferido):
- Antes: nada persistia após jogo. Checkpoint é dvar `start` na memória; sessão
  não gravava salvamento (`players/save` intocado, só `config.cfg`), e
  `mission_complete()` substitui `_nextmission()`, então registros do perfil (`highestMission`,
  `missionHighestDifficulty`, `UpdateGamerProfile`) tampouco escritos.
- Agora: DLL host grava `<game dir>\mw2coop\progress.txt` (`map`, `start`) em cada
  checkpoint e fim (próxima missão, sem ponto inicial). `mw2coop_continue` no
  host define `coop_mapName` e `start` dele. Em cada `coopLaunch`, host também envia
  pacote fora de banda `mw2coop_start <start>`; cliente define próprio `start`
  dele e descarta pacote, para ambos escolherem mesmo ponto em lockstep.
- Pedidos de script à DLL enfileirados com 0,3 s de intervalo (DLL lê dvar a cada 250 ms).
- Primeira continuação detectou dessincronia: pacote host tinha ponto vazio porque
  string dvar entre aspas falhou na validação do nome; host iniciou `bullet_penetration`, cliente
  `default`. QA passou no cliente porque, sem ponto, nível
  escreve lista de pontos em `start`. Ambos corrigidos (valor bruto; verificação agora
  lê `level.start_point`).
- **QA `resume @continue`: PASS nos dois, ambos em `bullet_penetration`, 0 erros** (05:32).
  Após QA `end`, `progress.txt` contém `map roadkill`.
- Não feito: registros de perfil (lista de missões no menu); próxima missão.

## <a id="next-mission-transition-2026-10-20"></a>Transição para próxima missão (2026-10-20)

- “Jogar novamente” Spec Ops chama `ChangeLevel( level.script )`; primeira tentativa chamou
  `ChangeLevel( next, keepWeapons )` nas duas máquinas. Observado: ambas ficaram em `trainer`,
  sem erro de script.
- Entrada da tabela builtin rva 0x3c2dc0: `changelevel` → 0x1937e0, `missionsuccess` →
  0x1938d0. Ambos só agem se `g_reloading` (ponteiro dvar rva 0xd9c020) é 0 e int
  rva 0xd9e1d4 é acima de 0; guardam mapa (buffer rva 0xd96e30) e definem indicador de saída
  rva 0xd97b80. Handler de saída (rva 0x170e60) escurece e executa `spmap <map>`, mas
  **retorna imediatamente quando `gameMode` (ponteiro dvar rva 0x192da20; valores none/sp/so/mp) é
  2 (“so”)**, usado numa sessão cooperativa (observado: `gameMode` 0 → 2 ao formar lobby).
- Lançamento do lobby: `coopLaunch` define indicador (rva 0x5dd953); quadro do grupo
  (rva 0xd74a0) exige grupo ativo (rva 0x5dd951), lobby com dois membros
  (lobby +0x70 e +0xa8), rva 0x1905300 == 0 e rva 0x5dd820 <= 0; host envia
  `coopLaunch` (rva 0x22e610) e ambos executam rva 0x22e1a0: estado do slot cooperativo
  (rva 0x533cb8, por cliente local, passo 16) = 3, dvars de taxa de rede, `map <coop_mapName>`.
- Observado (monitoramentos): grupo fica inativo (0x5dd951 → 0) nos dois ao iniciar
  nível; `coopLaunch` dado nele só define indicador; handler `coopLaunch` do cliente
  (rva 0x22d2e0, tabela de mensagens rva 0x350ce0) ignora
  mensagem salvo slot em estado 0 (está 4, depois 6 após `coopLoaded`).
- Correção: ao pedir fim do nível, ambas DLLs definem `coop_mapName` e chamam rva 0x22e1a0
  (comando `mw2coop_launch_map`). **QA `end`: ambas carregam `roadkill`,
  trocam `coopLoaded`, dois jogadores, modo campanha, PASS nos dois** (06:01). Em `roadkill`,
  jogador 2 inicia a 4668 unidades do 1 (1 num veículo do comboio) e
  `roadkill_code::player_shepherd_fov` falha nos dois (`LerpViewAngleClamp` em
  `level.player`): trabalho de nível dessa missão.

## <a id="test-god-mode-2026-10-20"></a>Modo deus de teste (2026-10-20)

- `_mw2coop::god_mode()`: em cada quadro, cada jogador vivo recebe `EnableInvulnerability()` e
  vida cheia. Ligado salvo host definir `mw2coop_god 0`. Deve coincidir nas duas máquinas
  lockstep (dano só numa dessincronizaria); pacote host agora leva
  `start=… mw2coop_god=…`, cliente define ambos; `mw2coop_god` também recebe indicador
  legível cooperativo. Comando `god` agiria só numa máquina.
- QA `god`: dano pesado nos dois → ambos vivos, nenhum caído, vida 100/100,
  PASS nos dois. QA `restart` com `mw2coop_god 0` só no host: cliente recebeu `0` do
  pacote; todas PASS, 0 erros.

## <a id="vehicles-for-two-players-2026-10-20-in-progress"></a>Veículos para dois jogadores (2026-10-20, em andamento)

Requisitos: num veículo, ambos em assentos distintos; na torre só um jogador,
quem entrar primeiro, e podem trocar. Locais: Team Player
(`roadkill`, única torre veicular), Wolverines! (`invasion`: Humvee inicial, embarque
num estacionado no final após defender Burger Town).

Levantamento (grep dos scripts próprios de cada missão por `UseBy( level.player`, `level.player
PlayerLinkTo` e nomes de veículos; lista inicial, não auditoria completa):

| Missão | Jogador e veículos | Estado |
|---|---|---|
| roadkill (Team Player) | Humvee: entrar por assento utilizável, depois torre calibre 50 (`player_ride_vehicle`, `player_gets_on_turret`); viagem termina em derrapagem de acidente | feito, QA `rkintro`, `board`, `rideend` passam |
| invasion (Wolverines!) | início: passageiro por `_utility::player_rides_shotgun_in_humvee`; fim: assento `tag_guy1` no Humvee estacionado | feito, QA `ride` passa; 2 no assento traseiro esquerdo |
| cliffhanger | jogador dirige snowmobile (380 menções). Próximo: segundo snowmobile ao 2; gatilho final só quando 2 também chegar | não examinado |
| af_chase (Endgame, perseguição a Shepherd) | jogador dirige barco (`friendly_boat UseBy( level.player )`) | não examinado |
| oilrig (início submerso) | SDV / sequência subaquática (`PlayerLinkTo`) | não examinado |
| gulag, oilrig, af_caves, dcemp, estate, boneyard, favela_escape, airport, contingency | cenas `PlayerLinkTo` (helicópteros, barcos, sequências) | não examinado |
| dcburning | helicópteros / Humvees, nenhum vínculo do jogador encontrado pelo grep | não examinado |

Assentos: `level.vehicle_aianims[ vehicletype ][ pos ].sittag` (Humvee: 0 tag_driver,
1 tag_passenger, 2 tag_guy0, 3 tag_guy1; `humvee50cal` acrescenta 4 tag_guy_turret); `usedPositions[ pos ]`
marca assentos de passageiros IA. `_mw2coop::seat_partner_in_vehicle()` põe
2 num assento livre sem ser motorista/torre (marca ocupado), vinculado como 1
(`PlayerLinkTo` com arcos visuais, armas desligadas); senão em `tag_body` offset (-50, 0, 10).

- Corrigidos `_utility::player_rides_shotgun_in_humvee` / `player_leaves_humvee` (2 acompanha
  embarque e saída do 1) e `invasion::player_enters_convoy_humvee` (assento ao 2).
- QA `ride` em invasion: 1 sentado, 2 a 72 unidades, juntos durante
  viagem, ambos fora, 2 junto ao 1: PASS nos dois, 0 erros (06:18 e 06:22).
- Observado: no Humvee inicial todos os traseiros têm IA (`humvee: 0=tag_driver* 1=tag_passenger
  2=tag_guy0* 3=tag_guy1*`); 2 vai no ponto alternativo: captura cliente mostra
  escotilha do teto (anel da torre adiante).
- Escolhido assento real em vez da escotilha: Worm (`script_noteworthy` “worm”, companheiro
  que a missão deixa morrer após pátios; usos posteriores verificam `isalive( level.worm )`) cede
  traseiro esquerdo. `invasion` define `level.mw2coop_spare_rider = "worm"`;
  `seat_partner_in_vehicle()` remove passageiro (`evict_rider()`) sem lugar livre. Ao
  sentar, função de criação ainda não rodou; correspondência por animname ou
  script_noteworthy. Três usos iniciais de `level.worm` sem verificação receberam `isalive()`.
  QA `ride`: `player 2 seated on tag_guy0 spare worm: removed`, tudo PASS nos dois, 0 erros
  (06:37); captura cliente mostra assento traseiro atrás do motorista.
- `follow_leader_teleports` agora não mexe no 2 vinculado.
- Visto em roadkill: 1 é interpolado (1 s) para cena Shepherd, lento demais para
  verificação de teleporte 512 unidades/quadro; 2 fica a 4668 unidades; exige vínculo
  por distância.

Projeto Roadkill (ainda não construído): assento utilizável (e gatilho automático de 80 unidades) responde a qualquer
jogador; primeiro é artilheiro (`level.mw2coop_gunner`), recebe animação de entrada e
torre; comboio (`player_gets_in`) espera segundo embarcar em assento recriado (ou
timeout o senta); passageiro segura Usar para trocar; fim desvincula ambos. Desconhecido: como
tirar jogador de torre por script (`UseBy` de novo?).

## <a id="team-player-for-two-players-2026-10-20"></a>Team Player para dois jogadores (2026-10-20)

Método: antes de resolver missão, ver como COD-MOD fez (referência, não
base). Scripts `x_coop.ff` COD-MOD (`local/`, só leitura, sem licença, nada
copiado): roadkill vincula ambos ao
mesmo rig na cena Shepherd, vincula 2 deitado em `tag_seat_rb_attach` quando 1
está na torre, desvincula ambos ao fim e vincula ambos à derrapagem. Sem escolha
de artilheiro, troca ou tratamento de pontos iniciais.

mw2_coop (`_mw2coop_roadkill.gsc`, patches `roadkill_code`, `roadkill`,
`_minigun_viewmodel`; fora de cooperativo, cada local mantém comportamento):
- Assento brilhante (e gatilho de 80 unidades) responde a qualquer um; primeiro é
  artilheiro (`level.mw2coop_gunner`, `_mw2coop::vehicle_gunner()`), recebe animação de entrada e
  torre; mãos da torre seguem botões dele.
- Indicador de comboio `player_gets_in` espera segundo alcançar assento novamente (ou 30
  s); ocupa lugar livre com armas (`tag_passenger` livre nesse Humvee).
- Troca: passageiro segura Usar por 1 s. Retirada da torre: `EnableTurretDismount()`
  depois segundo `turret UseBy( player )` (também desvincula; QA `turret`).
- Observado: troca num quadro de servidor causou falha nos dois na segunda troca
  (violação de acesso escrevendo 0x1c no rva 0x15f515, `TeleportPlayer` com `ent->client` NULL,
  pilha 0x175ca5 / 0x15b73f / 0x234331). Distribuir em três quadros resolveu (QA `board`:
  troca e volta passam).
- Fim e acidente: ambos saem onde estão; 2 pousa junto ao 1.
- Pontos `ride`, `ambush`, `ride_later`: 1 vinculado no primeiro quadro,
  deixado para trás quando ponto inicial moveu Humvee ao trajeto (a 13375 unidades da
  torre em uso) e desvinculado ~2,25 s depois; remonta após 1 s.
- Cena Shepherd: 2 vinculado ao mesmo rig visual (ideia COD-MOD), colocado junto ao
  1 depois.
- **Dvars definidas por script:** rastreamento de método (DLL `!trace <rva of a method table entry>`, unlink
  rva 0x342c88 → 0x187e20) mostrou `_introscreen::flying_intro` desvinculando 1 em 2,25 s.
  Introdução com zoom rápido só roda se `getdvarint( "newintro" )` é 0; roadkill.gsc define 1,
  mas getdvar cooperativo lê "" para qualquer dvar sem indicadores 0x20c4, então introdução só SP
  rodava e quebrava cena (erro LerpViewAngleClamp `player_shepherd_fov`). DLL agora envolve
  builtin GSC `setdvar` (entrada rva 0x3c1568 → 0x185500; nome por
  `Scr_GetString` rva 0x223440) e dá 0x80 à dvar após definir: ambas definem
  mesmo valor, leitura segura em lockstep. Depois: sem zoom, 1 permanece
  na cena, 0 erros.
- Logger de falhas DLL (handler de exceções vetorizado): RVA da falha, registradores, retornos.
- QA (duas cópias, 0 erros nos dois): `rkintro` (ambos na cena, a 48 unidades
  depois), `board` de `convoy` (2 primeiro → artilheiro, comboio espera, 1 sentado, troca
  e volta, ambos em Humvee móvel a 47 unidades), `rideend` de `ride_later` (1
  na torre a 51 unidades, acidente em 21,5 s, ambos fora, a 48 unidades), `turret`.

## <a id="cliffhanger-spawn-audit-gulag-and-takedown-seats-2026-10-20-later"></a>Cliffhanger, auditoria de criação, assentos Gulag e Takedown (2026-10-20, mais tarde)

Snowmobiles Cliffhanger (COD-MOD não tem script cliffhanger para comparar):
- `maps\_snowmobile_drive::drive_vehicle()` já trata segundo jogador (Spec Ops). 2
  recebe snowmobile do `playermobile_spawner` (criador do jogador cria
  uma vez); qualquer jogador pode montar qualquer um; montado pelo 1 vira
  `level.player_snowmobile`; ponto `snowmobile` monta ambos; após `end_begins`,
  final do helicóptero espera 2 fora do snowmobile a até 400 unidades do 1.
- `_blizzard::blizzard_start_proc` reproduz nevasca cooperativa na `tag_origin`;
  jogadores de campanha sem modelo corporal (`coop_body_*` só nas zonas so_*:
  grep das zonas descomprimidas), chamada falhava; agora usa modelo tag_origin ligado ao
  jogador.
- QA `snow` (início snowmobile → favela nos dois), `snowpick` (início icepick, 2 pega
  primeiro snowmobile do 1): PASS, 0 erros.
- No Russian sempre jogada (esta `_nextmission()` pula airport após
  cliffhanger incondicionalmente, comentário “RUSSIAN PC BUILD”).

Escalada de gelo (andamento; objetivo: completa para dois, sem paliativos, qualidade como se
Activision a tivesse lançado): `cave_main` já executa `_climb::climb_wall` para cada um no
seu início `player_climb` (existem dois: errado, há um, veja seção abaixo), mas `_climb.gsc` usa `level.player` 158 vezes em 35
funções, indicadores globais (`player_in_position_to_climb`, `finished_climbing`, `final_climb`,
`climb_pullup`, `climb_big_jump`, ...), `level.arm_ent_globals`, `level.stabs_completed`, e
lê golpes por `ButtonPressed( "mouse1"/"mouse2"/"j"/"k" )` — teclas locais que
dessincronizam jogador remoto. Plano: `@@@ subst` level.player -> escalador
por função, ent_flags por jogador alimentados pelos mesmos volumes de gatilho, botões usercmd
(`AttackButtonPressed`/`AdsButtonPressed`), globais dos braços por jogador, salto com ambos
escorregando e Soap MacTavish (`level.price`) puxando ambos, injeção de entrada DLL
para QA. Fuga de snowmobile pronta.

Auditoria de criação (QA `spawn`, início padrão de cada missão, 12 s): 2 junto do 1 no
chão em trainer, roadkill, cliffhanger, favela_escape, arcadia, dcburning, contingency,
dc_whitehouse, estate, boneyard, af_caves, af_chase; sentado em invasion. Problemas onde 1
inicia vinculado: gulag (2 caiu 67000 unidades do ponto inicial), favela (carro),
oilrig (SDV: 2 no fundo, 3530 abaixo), airport (elevador: mesmo
ponto), dcemp (acidente), ending (créditos: 8 erros `_credits::playcredits`).
- Teleportes agora recusam enquanto 1 vinculado ou no ar, repetindo até ficar de pé
  (`is_standing`: `IsOnGround()` lê 0 para 2 em cooperativo, portanto trace do chão).
- Gulag: 2 recebe próprio `get_player_view_controller` num assento livre do helicóptero
  de chegada (COD-MOD também tinha segundo controlador), olha mesmo alvo, sai com
  1. Takedown: 2 viaja no carro inicial (aianims `luxurysedan` só têm assento de
  motorista; ponto alternativo por enquanto), sai com 1. Auditoria PASS
  nos dois (53 e 66 unidades, vinculados), 0 erros.
- Operação `@@@ subst <function>` (DLL + check_patches.py): substituição de palavra inteira numa
  função, para reformulações não colocarem código do jogo nos patches.

## <a id="cliffhanger-ice-climb-for-two-players-2026-10-20"></a>Escalada de gelo Cliffhanger para dois jogadores (2026-10-20)

Ambos escalam parede, correm e fazem salto grande, Soap MacTavish (`level.price` nos
scripts) pega cada um, ambos sobem última parede; nível segue após ambos
subirem. Arquivos: `scripts/maps/_mw2coop_climb.gsc` (lógica), `_mw2coop_climb_qa.gsc` (bot QA),
`patches/maps/_climb.gsc.patch` (110 trechos), `_climb_anim.gsc.patch` (8), `cliffhanger.gsc.patch`
(2), gerados por `tools/gen_climb_patches.py` dos scripts extraídos.

Observações (logs QA, capturas das duas cópias):
- Mapa tem **um** início `player_climb`, não dois (correção acima):
  `cave_main` indexava `climb_starts[ 1 ]` para 2 → dois erros, sem início
  para ele. Faixa do 2 calculada: ao lado do início na parede, oposto ao
  nó de Soap (`cliffhanger_cliff`), conferida por 12 bullet traces na parede para
  superfície compatível com picaretas (gelo/rocha/neve/reboco). Aqui: 72 unidades, offset
  (-18,6, -69,5, 0).
- `climb_startdir` lê "" nesta compilação ao iniciar (`create_dvar` =
  `SetDvarIfUninitialized` não pegou), então `get_anims_for_climbing_direction` retornava
  indefinido e braços sem animações até primeiro golpe: erros em
  `player_finishes_climbing`/`player_relinks_to_tag` (rva 0x21f1b6: índice em não vetor;
  0x21ee98/0x2263d6: comparar com indefinido), sem animação de subir à parede. Cooperativo usa
  “up” para valor desconhecido (individual mantido).
- Do outro lado, offset da faixa aponta quase na direção do salto; lado distante
  (nó de salto, `climb_catch`, estrutura de levantar) usa offset próprio à direita de `climb_catch`,
  lado escolhido pelo mesmo teste (aqui 70 unidades, pontuação 6 vs 3).
- `if ( !flag( "can_save" ) ) return;` ao fim de `player_big_jump` impedia ambos
  de chegar ao topo: `can_save` lê 0 então (limpo em algum lugar, escritor não
  encontrado). Cooperativo verifica queda própria do jogador (`fade_to_death`).
- Geometria dos gatilhos (origens): `climb_jump_prep` (455, -29245, 855), `climb_big_jump`
  (497, -29084, 948, tocando), `climb_icepick_slide` (531, -28878, 682, tocando),
  gatilhos de definir `ramp_block_notsolid` (447, -29132, 810) e **limpar** (461, -29264, 860);
  monitor por jogador trata `*_flag_clear` como limpeza.
- Carregamento: script de todos mapas não deve nomear `maps\_climb` (só na zona
  Cliffhanger): primeira versão tinha QA em `_mw2coop_qa.gsc` e todo outro mapa falhava
  com “Could not find script 'maps/_climb_anim'” (detectado por `snow` e `leash`).
  QA fica em `_mw2coop_climb_qa.gsc`, alcançado por `level.mw2coop_qa_climb`.

Projeto (implementado):
- `level.player` → escalador em cada função (`self`, `ent.player`,
  `self.player`, `self.mw2coop_player`); individual inalterado (escalador é
  level.player ali).
- 20 indicadores por jogador (8 de gatilho alimentados por monitor `IsTouching` nos mesmos volumes,
  12 de estado). Definição individual também define compartilhado; `reached_top` quando
  ambos têm.
- Golpes: usercmd (`AttackButtonPressed` esquerdo, `AdsButtonPressed` direito, conforme comentários
  dos desenvolvedores junto das chamadas mouse1/mouse2) no lugar de `ButtonPressed` local.
- Salto: Soap salta uma vez; captura enfileirada (notetrack `start_gaz`): enquanto pega
  um, rig do outro segura (taxa 0) onde se agarra; depois Soap o pega.
- `level.mw2coop_no_follow` durante escalada: sem teleporte de acompanhamento ou vínculo por distância,
  ninguém movido parede acima.
- Conhecido, não feito: `cg_fov` 78 ao escalar e profundidade de campo são globais /
  só level.player; câmera lenta de captura (0,2 s) global.

QA `climb` (início padrão, bot: golpes por `mw2coop_qa_hold`, andar/correr por impulsos
de velocidade; não acha caminho na borda da caverna, então define `price_begins_climbing` após
6 s), 2026-10-20 nas duas cópias, hashes iguais, 0 erros:
```
PASS two players (2)
PASS player 1 reached the top
PASS player 2 reached the top
PASS Soap caught player 1
PASS Soap caught player 2
PASS the level goes on (reached_top)
PASS both players together at the top (60 units)
```
Ordem do log: Soap pega 1 → “player 2 hangs on, Soap is catching the other player” →
1 no topo, esperando → Soap pega 2 → ambos no topo. Regressão no mesmo
dia: `leash` (trainer), `snow` (agora para airport), `snowpick` PASS. Entrada real dos golpes pelo
mouse (caminho usercmd) não exercitada pelo bot: não testada.

## <a id="takedown-opening-car-for-two-players-2026-10-20"></a>Carro inicial de Takedown para dois jogadores (2026-10-20)

COD-MOD só punha 2 num ponto fixo na rua (`level.players[1] SetOrigin` em
favela.gsc), fora do carro. Observações: traseiro do sedã vazio durante trajeto
(Soap criado fora quando sai correndo: `anim_teleport_solo` em `soap_start_node`); nível
leva level.player num rig ligado a `tag_passenger`, abaixa por `notifyOnCommand`
(só comandos do 1; Spec Ops usa `player NotifyOnPlayerCommand`), e tiros
10-15 de Makarov matam level.player salvo global `player_is_ducking` definida.

Construído (`scripts/maps/_mw2coop_favela.gsc`, `patches/maps/favela.gsc.patch` 17 trechos por
`tools/gen_favela_patches.py`; geradores compartilham `tools/gsc_patch.py`):
- `player_rides_vehicle` e `player_exits_vehicle` executam para todos (`level.player` →
  self); rig do 2 no traseiro, 40 unidades atrás de `tag_passenger`, mesmas animações de abaixar
  e morrer e seus próprios comandos de agachar.
- `player_is_ducking` = “um jogador abaixa” (portas do hotel); cada tiro fatal atinge todos
  que não abaixam (`kill_player( player )`); golpe falha missão 1,5 s depois, como
  individual (sem ficar caído no carro).
- Saída: 2 espera 1, desliza ao banco dianteiro e sai pela
  mesma porta aberta para ponto no chão junto da saída.

QA 2026-10-20, cópias iguais, 0 erros: `takedown` (ambos no carro, olhos a 39
unidades, ambos abaixam, ninguém baleado, ambos fora a 47 unidades, vivos), `takedown2` (2
fica erguido: “Makarov hits player 2”, missão falha e reinicia nos dois 1,5 s depois), `spawn`
em favela PASS. Capturas: 2 vê encosto dianteiro e van à frente; sai
pela porta dianteira aberta. Abaixar enviado como notificação `go_crouch`: tecla real
por `NotifyOnPlayerCommand` não testada.

## <a id="the-only-easy-day-oilrig-opening-for-two-players-2026-10-20"></a>Início de The Only Easy Day... (oilrig) para dois jogadores (2026-10-20)

COD-MOD vinculava ambos ao rig do 1 no SDV A, ocultando-os (duas câmeras num rig),
também na execução da grade: não usado. Observações: SDV A leva piloto, copiloto, swimmer1 e
jogador (`oilrig_sub_A_disembark_player` = lugar 3); SDV B (do segundo submarino, ~16900
unidades longe no início) leva quatro SEALs, lugar 3 = `sdv02_swimmer1`. Cena da grade é
execução sincronizada: jogador mata guarda 2 em primeira pessoa e SEAL `sdv02_pilot`
mata guarda 1 (sem animação em primeira pessoa para 1); dois SEALs
(`water_helper_01/02`, `surface_helpout`) puxam jogador, no tempo da notetrack “help” de
sua animação de execução. `killtrigger_ocean` ligado após jogador sair e
mata qualquer um tocando água.

Construído (`scripts/maps/_mw2coop_oilrig.gsc`, `patches/maps/oilrig.gsc.patch` 24 trechos por
`tools/gen_oilrig_patches.py`):
- 2 vai no SDV B no lugar de sdv02_swimmer1 (SEAL omitido em cooperativo), com
  animação de viagem/nado do jogador; só rig do 1 controla indicadores de nado (mesma duração).
- Cada jogador boia e nada junto da grade (`water_bob` por jogador); nado do 2 termina 35
  unidades mais alto (acima da passarela), boiando na altura do 1.
- Execução furtiva: primeiro a golpear (no gatilho, olhando guarda, corpo a corpo) executa;
  dica aparece quando qualquer um olha. Outro nada até executor sair;
  seu próprio rig roda execução invisível (taxa 8) até “help” e ele é puxado
  pelos dois SEALs (animação de ajuda repetida), junto ao executor.
- Gatilho fatal do oceano poupa quem ainda espera ser puxado.
- Conhecido: visão da água (acima/abaixo) e HUD seguem executor nas duas telas.

QA 2026-10-20 (`oilrig`: 1 executa; `oilrig2`: 2 executa), duas cópias, resultados
iguais, 0 erros após correção oceano: ambos num SDV, ambos à superfície (235 unidades
de distância, mesma altura), executor fora, outro puxado 5,75 s depois, ambos na plataforma a 24
unidades, vivos. Golpe forçado pelo bot (`mw2coop_qa_melee`): olhar ao
guarda e tecla de ataque não testados. Capturas: 2 no tubo de saída do sub B, atrás das
nadadeiras de SEAL sob água, sob grade durante execução, na plataforma depois.

## <a id="no-russian-elevator-crash-site-and-second-sun-opening-for-two-players-2026-10-20"></a>Elevador No Russian, acidente e início Second Sun para dois jogadores (2026-10-20)

No Russian (`airport`): nível segura visão do 1 num script_origin ao fundo do
elevador por ~20 s (zoom, máscara de gás, `airport_vision_elevator`); 2 compartilhava
ponto. Agora fica junto à parede traseira, ao lado do 1 (ponto livre: chão, linha livre, nenhum
membro a até 30 unidades; aqui 36 à direita), preso igual e liberado junto
(`_mw2coop_airport.gsc`, `airport_code.gsc.patch` 2 trechos). QA `spawn`: d 36, ambos vinculados;
captura: 2 no canto traseiro direito, Makarov diz “Remember, no Russian”.

Acidente (`dc_crashsite.gsc`, idêntico nas zonas dcburning e dcemp, um patch
serve ao fim de Of Their Own Accord e início Second Sun): 2 recebe rig próprio
com animação de despertar junto ao 1 (lado escolhido por 5 traces visuais para fora: casco
bloqueia um), movimento próprio na grade da cabine (`player_crash_movement` por
jogador), rifle e carregador de Foley (`player_crash_gun_behavior` por jogador; autosave
só para 1: duas vezes simultâneas geravam erros `_autosave_game_now`). Lógica
em `_mw2coop_crashsite.gsc`, sem nomear script dcemp/dcburning (carregado nas duas
zonas). Second Sun (`_mw2coop_dcemp.gsc`): na ISS, 2 flutua 64 unidades junto ao 1
num tag_origin ligado à câmera animada do 1; visão e postura guardadas para após
EMP; `emp_empaftermath` e `emp_free_player` por jogador (2 sai 0,6 s depois,
40 unidades ao lado).
QA `dcemp` (2026-10-20, duas cópias, 0 erros): ambos nos destroços (olhos a 35 unidades),
ambos com rifle, ambos na ISS (64), de volta aos destroços (35), fora (40),
vivos. QA `crashsite` (dcburning, início crash): ambos nos destroços, rifles, ainda dentro ao
fim; nível segue a contingency.
Aberto: `dcemp_code::street_heli_player_kill` (helicóptero mata quem fica
exposto) gerou erro com bot parado após QA e só trata level.player:
2 ainda não ameaçado.

## <a id="second-sun-street-and-the-ending-map-2026-10-20"></a>Rua Second Sun e mapa final (2026-10-20)

Rua (`dcemp_code::street_heli_player_kill`, `street_hide_moment`): little bird caindo
persegue level.player até equipe e “street_player_hide” (qualquer um no
esconderijo) definirem `street_safe`. Cooperativo: um helicóptero por jogador (`street_helis`), cada um para
quando seu jogador se esconde (retenção individual do mesmo gatilho) ou rua segura;
`street_safe` espera todos vivos; “street_insta_death” individual. QA `street`
(início street, bot teleporta 1 ao esconderijo, acompanhamento desligado): rua não
segura com 2 fora (helicóptero o alcançou: `kill()` gera erro sob
modo deus), segura após ambos esconderem, vivos.

Mapa final (`ending`): `ending.gsc` define `level.level_mode` por `ui_char_museum_mode`, que
fim de af_chase define “credits_1” (ambos executam script, portanto ambos têm).
“credits_1” é luta de faca com Shepherd (`af_chase_knife_fight`, pontos wakeup ...
walkoff), depois créditos do museu. Iniciado direto na auditoria, lista só
tinha pontos do museu (“ ** no_game arcadia ... af_caves ”), iniciou em
“af_caves”, `_credits::playcredits` falhou em `level.linelist.size` (8 erros), com
1 na câmera do museu, 2 de pé a 1500 unidades. Desconhecido: se pontos da
luta são registrados ao chegar por af_chase; exige executar a partir do
fim de af_chase. Ainda não alterado.

## <a id="ending-map-mode-no-russian-ending-qa-runner-2026-10-20"></a>Modo do mapa final, fim No Russian, executor QA (2026-10-20)

- Mapa final: em cooperativo `ending.gsc` leu `ui_char_museum_mode` vazia (monitoramento
  mostrou “credits_1”; causa desconhecida), indo ao museu livre com créditos
  quebrados. Agora trata valor vazio/desconhecido como “credits_1” (`_mw2coop_ending.gsc`,
  `ending.gsc.patch`): luta inicia (ponto “wakeup”; pontos wakeup ... walkoff).
  2 ainda a 43000 unidades do 1: próxima é luta para dois.
- Projeto (2026-10-20): luta = ambos feridos, por vez (primeiro a chegar em
  Shepherd faz golpe/monólogo/revólver, outro rasteja e observa; ambos tiram
  faca, primeiro arremessa); fim No Russian = Makarov mata ambos.
- Fim No Russian (`airport.gsc.patch` 8, `airport_code.gsc.patch` 11 trechos): qualquer um
  pode estar na van; Makarov atira nele primeiro (fim próximo) ou no mais perto
  (fim distante), depois desvincula, gira (ForceTeleport para encarar) e atira no outro com
  animação de tiro do fim distante; outro cai onde está com animação do jogador
  do fim distante. Cada clarão branco na tela da vítima; visão de morte no segundo tiro.
  QA `nrend` (distante: 2 primeiro, depois 1), `nrend2` (1 na porta da van: fim
  próximo, depois 2): ambos baleados/caídos. Capturas: 2 caído na ambulância com
  Makarov sobre ele, 1 junto à roda, ambos em branco. Aberto: `nrend` (fim
  distante) um erro em `_anim::anim_loop_packet` de `escape_end_sequence` (laço do
  companheiro da van) após segundo tiro; não em `nrend2`. Desconhecido se individual tem.
- Executor QA: `run_test.ps1 -DoneLogs` fecha cópias após todo log ter “qa: N: done”
  (janelas ficavam até timeout). `leash` fechou em 71 s em vez
  de 170.

## <a id="endgame-knife-fight-for-two-players-mod-localized-strings-2026-10-20"></a>Luta de faca Endgame para dois, strings localizadas do mod (2026-10-20)

COD-MOD vinculava ambos ao rig do 1 e teleportava a ponto fixo; também
forçava `level_mode = "credits_1"` (mesmo problema da dvar vazia).

Observações: `af_chase_knife_fight.gsc` e `_code.gsc` idênticos nas zonas af_chase e
ending (192 usos `level.player`). Cena tem braços em primeira pessoa só para
jogador; animação de terceira pessoa `player_body` só para Price despertando. Jogadores sem
corpo em campanha, motor sem visibilidade de entidade por jogador (só
`target_showtoplayer`/`target_hidefromplayer` para alvos HUD); quem olha protagonista
vê braços flutuantes (visto no cliente: só braços). Rastejar lê
`ButtonPressed("mouse1"/"mouse2")` (teclas locais); dicas dizem +attack (direito), +speed_throw
(esquerdo). `getdvar` leu `ui_char_museum_mode` vazia (dvars de script de outro mapa).
Jogador vinculado com `AllowStand(false)` e `AllowCrouch(false)` derruba sessão
(“All stances (standing & crouching) disallowed for linked player”). Strings localizadas desta compilação
são Windows-1251 (`!loc COOP_WAITINGFORPLAYER`: ce e6 e8 e4 ...); string simples de script
com cirílico, UTF-8 ou 1251 aparece como pontos.

Construído (projeto: ambos feridos, primeiro a golpear faz cena; depois,
ao ver braços flutuantes: outro oscila entre consciência e inconsciência):
- `tools/gen_knife_patches.py`: cada `level.player` dos dois arquivos -> `level.mw2coop_lead`
  (definido como level.player em `_mw2coop::main()` também individual); mais próximo candidato
  a protagonista; golpe de qualquer um conta; botões de rastejar do usercmd protagonista.
- 2 desperta 64 unidades junto do 1 com rig próprio; caminhada ferida depois.
- Outro (`_mw2coop_knife.gsc`): sobreposição preta própria com respiração/batimentos e
  texto `MW2COOP_STUNNED` desde golpe; desperta quando faca sai
  (`knife_pulled_out`), vê arremesso, morte Shepherd e Price da câmera no chão
  a 120-240 unidades, virada para protagonista ficar a pelo menos 60-81 graus fora da visão (arcos
  25/25/15/10); apaga imediatamente se Shepherd/Price saltam (>80 unidades/quadro:
  cortes da cena) e ao caminhar ao helicóptero (braços flutuantes novamente).
- `src/localize.c`: trampoline `DB_FindXAssetHeader` (15 bytes de prólogo) responde
  entradas localize `MW2COOP_*` em russo (1251) quando `MENU_YES` lê “??”, senão inglês.
- `tools/gsc_patch.py` encontra funções pelo pareamento de chaves (função terminando em “}\t\t” fazia
  busca antiga `
}
` invadir função seguinte).

QA `knife` (2026-10-20, ending, início wakeup; bot: executor teleportado à frente de Shepherd,
botões de rastejo alternados, toques Usar, mira e “arremesso”): ambos despertam a 64 unidades; 1
golpeia e faz cena toda (rastejo 84 s, faca 23 s, arremesso 6 s); outro apagado até
faca sair, acordado a 114 unidades de Shepherd com linha livre enquanto morre, 3 s e 30 s
depois; 0 erros. `knife2` (2 golpeia): 2 faz cena, 1
testemunha, acordado a 121 unidades de Shepherd ao morrer; 0 erros. Capturas: texto russo
de atordoamento; Shepherd com faca no
olho; corpo visto do chão. Sincronia labial: voz/lábios vistos fora de sincronia nas duas
telas; `timescale` ficou 1 na cena toda salvo câmera lenta do arremesso (volta a 1), então
não é causa; aberto.

## <a id="qa-bots-press-real-buttons-2026-10-21"></a>Bots QA pressionam botões reais (2026-10-21)

`+activate` do console nada fez, pois compilação 64 bits não tem esse comando (`!cmds`:
168 comandos; dos `+`, só `+moveup`, `+speed`, `+melee_breath`, `+throw`,
`+nightvision`, `+incAnimWeight`, `+decAnimWeight`, registrados nos rvas 0xcf5d0 e 0xd3240).
Como tecla funciona (Ghidra, iw4sp.exe compilação 25374375):
- Tabela de associações rva 0x3be770, 0x4c entradas `char *`: índice 0 vazio, `+attack` 1, `-attack`
  2, `+melee` 3, ... `+forward` 0x1b, `+back` 0x1d, `+gostand` 0x19, `+activate` 0x31,
  `-activate` 0x32, `+reload` 0x33, ... depois `togglemenu`, `weapnext`, ... `leaveads` 0x4b.
- rva 0xd1810: nome -> índice (0 ausente). Índice por tecla em 0x5300f0 (passo 0x18,
  256 teclas); rva 0xd17f0 lê; `bind` (rva 0xd13d0) escreve.
- rva 0xce450 `(localClient, index, key)`: switch do índice. Ímpar: kbutton pressionado
  (rva 0xd0620), par: solto (rva 0xd06f0); alguns executam ações (actionslots, postura). Retorna
  cedo salvo cliente num nível (bytes 0x5dac53 e 0x40cac8). kbutton (0x14 bytes):
  `int down[2]; int downtime; int msec; char active; char wasPressed`; vetor em
  0x52fbc0 (`+left` 0x52fbc0, `+forward` 0x52fbe8, `+attack` 0x52fcd8, `+activate` 0x52fd3c).
- rva 0xd03a0 monta usercmd: key catcher 0x10 (0x533cb0) definido, só faz postura;
  senão botões (rva 0xce200: attack 0x1, melee 0x4, Use 0x8, reload 0x10, usereload 0x20,
  prone 0x100, ...), movimento (rva 0xcf900, frente/trás/lateral de kbutton, rva
  0xcfbc0) e mouse. Movimento pulado com indicador de estado 0x800 (0x535d44,
  controles congelados).
- mw2_coop: comando `mw2coop_bind +activate` chama 0xce450 com tecla 0x1ff (nenhum teclado
  envia); scripts QA definem `mw2coop_qa_press "<player> <button> <ms> <n>"` e só DLL
  da máquina daquele jogador (host = 1) pressiona e solta após ms.

Resultados: `buttons` (S.S.D.D., Whiskey Hotel) e `pickups` (rifle, pistola, caixa de granadas) todos PASS
nos dois com pressões reais. Encontrado com entrada real:
- S.S.D.D.: posição do 1 no estande (48 unidades à esquerda de `player_start_range`) ficava 10
  atrás da do 2 e dentro da parede traseira: traces bloqueados aos
  lados/trás, Frente moveu 0 unidades em cinco tentativas. Agora ambos onde COD-MOD
  põe jogadores: 1 em -2515.2 5190.2 (67 à esquerda
  do início, 36 adiante: sacos 20 à frente, parede 23 atrás), 2 no início (sacos 42
  à frente). Baia (traces de jogador): 101 à esquerda até 28 à direita do início; parede traseira
  inclinada, 7-25 atrás da linha inicial. QA `bay` verifica ambos dentro, não presos.
- `maps\_introscreen` congelava só `level.player` (S.S.D.D.: 12 s): 2 podia andar e pegar
  pistola enquanto 1 não. Corrigido (tools/gen_intro_patches.py): FreezeControls,
  DisableWeapons e EnableWeapons em `level.player` nas 12 funções passam a todos.
  Cada uma desfaz próprio congelamento (sem retorno antecipado). QA `introfreeze`.

## <a id="loose-ends-shepherds-betrayal-for-two-players-2026-10-22"></a>Loose Ends: traição de Shepherd para dois jogadores (2026-10-22)

Cena (estate.gsc `ending_moments()`): na zona de pouso, morteiro derruba Roach (`birchfield_knockout`,
indicador `play_ending_sequence`); Ghost o arrasta no rig `playerview` (anim `estate_ending_drag`,
arcos `PlayerLinkToDelta` 30) enquanto luta de costas com AK; apagão; no Pave Low
(`estate_ending_part1`), Ghost o ergue, Shepherd saca (`pistol_pullout`), atira nele
(`shepherd_fire2`: `DoDamage(99 / damagemultiplier)` com escudo de morte ligado) e em Ghost
(`shepherd_fire1`); apagão; `estate_ending_part2`: dois homens jogam corpo de Roach
(`body_ending`), depois Ghost, numa vala; gasolina, fogo, `end_the_mission`. Tudo em
`level.player`. Antes: 2 ficava onde estava (a 12.000 unidades no início `ending`) e
nada via. COD-MOD: só congelamento e escudo nos dois ao cair; tentativas de vincular
ambos ao rig comentadas.
Projeto: como COD-MOD, 2 invisível nas
cenas e jogado com Roach no mesmo lançamento; tiro de Shepherd também o atinge (vê
pelos olhos de Roach, arma aponta a ele), depois preto sem texto.
Feito (tools/gen_estate_patches.py, `maps\_mw2coop_estate`): cada instrução `level.player` de
`ending_moments`, `ending_gasoline_sequence`, `ending_passing_out`, `ending_slowmo`,
`ending_mortarhit_ghost_sequence`, `startEnding`, `birchfield_knockout` executa por jogador,
salvo tiro Shepherd e vibrações, monitor de dano, respiração e cadência
do ciclo de desfoque; ambos perdem função de modelo (`SetModelFunc( undefined )`: Hide não oculta jogador
cooperativo) e nomes; 2 sofre mesmo golpe após Roach, depois sobreposição preta cliente
(ordem -1, sob legendas) entra em 0,3 s e sai com `restoreVision` do lançamento.
QA `betrayal`: com modo deus, golpe nada faz (vida continua 100, também no 1):
executar com `MW2COOP_GOD=0`. Escudo do final não envia notificação `damage`; teste lê
menor vida.

## <a id="upnp-on-a-pc-with-several-network-adapters-2026-10-22"></a>UPnP num PC com vários adaptadores de rede (2026-10-22)

Num PC com vários adaptadores, busca sem resposta (“no router answered”). SSDP
M-SEARCH simples (Python, sem interface escolhida) também sem resposta, até `ssdp:all`; mesma
busca enviada do endereço LAN (vinculada, `IP_MULTICAST_IF`) ou direto ao gateway obteve
resposta imediata. Windows enviava multicast por outro adaptador. Correção em
`src/upnp.c`: endereço da rota à internet (`connect` UDP a endereço público,
`getsockname`; não envia nada) e gateway dessa rota (`GetBestRoute`); busca sai
desse endereço e também vai ao gateway. Roteador respondeu e aceitou redirecionamento
(UDP 28960). Iniciar nível também removia estado “hosting” por instante, removendo e
refazendo regra; remoção agora espera parada de 10 s.

## <a id="no-russian-makarovs-crew-look-on-the-spec-ops-body-2026-10-22"></a>No Russian: aparência da equipe de Makarov no corpo Spec Ops (2026-10-22)

Corpos devem ser cooperativos Spec Ops (`coop_body_*`): corpo IA como
`body_airport_com_c` num jogador dá postura quebrada (animações precisam do esqueleto
cooperativo). Para vestir ambos como equipe de Makarov, DLL (`src/transplant.c`) põe malha da
equipe em `coop_body_us_army` na memória: alvo mantém ossos, locais de impacto, colisão e
limites, recebe LODs (cópias de superfícies) e lista de materiais. Ossos de cada vértice
renumerados por nome; osso doador ausente no alvo usa ancestral mais próximo. Cabeças
continuam modelos separados (cabeças da equipe se ligam ao corpo como cabeças cooperativas).

Observações (dumps do novo comando QA `!surfs <xmodel>`, depois quadros):
- Layouts 64 bits. XModel: boneNames +0x28 (índices de strings de script internadas), parentList +0x30
  (byte por osso não raiz: índice menos índice do pai), materialHandles +0x58, lodInfo[4]
  +0x60, passo 0x38 (dist +0, numsurfs +4, surfIndex +6, modelSurfs +8, partBits[6] +0x10, surfs
  +0x28). XModelSurfs: name +0, surfs +8, numsurfs +0x10, partBits +0x14. XSurface, 0x58 bytes:
  deformed +1, vertCount +2, vertInfo.vertCount[4] +0x18, vertsBlend +0x20, vertListCount +0x30,
  vertList +0x38 (0x10 cada: boneOffset, vertCount, triOffset, triCount, árvore de colisão +8),
  partBits[6] +0x40. Conferido em todas superfícies de três modelos: grupos de vértices somam
  vertCount.
- vertsBlend: vertCount[0] vértices com 1 osso (1 valor), [1] com 2 (osso, osso, peso), [2]
  com 3 (5 valores), [3] com 4 (7 valores); osso guardado como índice * 64.
- partBits: um bit por osso usado, osso 0 = bit mais alto da palavra 0, sem ancestrais (17 de 17
  superfícies da equipe conferem, nenhuma com “com ancestrais”).
- Equipe (com_c) 81 ossos, 17 superfícies em 4 LODs; ranger 90 ossos, 33 superfícies. Seis ossos
  sem ranger do mesmo nome (mapeados a ancestrais).
- Troca na thread principal (comando enfileirado pela thread de controle), só enquanto
  mapa pedido executa: buscas de assets por outra thread ou ao carregar zona do próximo nível
  travavam jogo em trabalhos anteriores. Reinício encontra pronto (lista de materiais alvo é
  do doador); carregar zona seguinte restaura original.
- Quadros (QA `bodyview`, airport início `stairs`): ambos com jaqueta e calças da equipe,
  de pé, andando de lado e recuando com animações de jogador; sem estiramento visível
  nos quadris, onde poses de referência dos esqueletos diferem até 5 unidades.

Desconhecido: aparência de outros LODs à distância (não vista). Ambos compartilham corpo
com_c com cabeças diferentes; não conferido se zonas carregadas contêm segundo corpo cooperativo
para com_d.

## <a id="no-russian-level-tour-and-the-squads-line-of-fire-2026-10-22"></a>Percurso No Russian e linha de tiro da equipe (2026-10-22)

QA `tour` em airport (9 pontos, quadros das duas telas): 109 PASS, 0 FAIL. Erros
vieram do ponto de desenvolvimento `grigs` e um `Kill()` sob modo deus.
Essa morte é linha de tiro: no saguão (`intro_civilians`) e massacre
(`massacre_killers_shotgun`), nível espera gatilho final com `add_wait(
::trigger_wait_targetname )`, abortado pelo indicador de avanço da equipe, e chama `level.player
add_call( ::Kill )`; antes, `player_line_of_fire` dispara MagicBullets de aviso aos
pés de `level.player` no raio da linha. Gatilho dispara para qualquer um;
2 entrando matava 1, e 2 não recebia avisos. Correção (gerada por
`tools/gen_airport_patches.py`): aviso ao jogador na linha, quem
entra no gatilho final morre (1 fora de cooperativo). QA `lineoffire` (início `intro`,
`MW2COOP_GOD=0`): 2 entra e morre, 1 vive, missão falha nos dois.

Quadros: início `intro` é elevador com tela inicial da missão, preta pelos primeiros
10 s, como individual.

## <a id="god-mode-downs-and-difficulty-for-two-2026-10-22-v040-beta"></a>Modo deus, quedas e dificuldade para dois (2026-10-22, v0.4.0-beta)

- Modo deus: `god_mode_on()` era `GetDvar("mw2coop_god") != "0"`, e só inicializadores `.bat`
  removidos definiam “0”: toda sessão de lobby v0.3.0-alpha e v0.3.1-alpha tinha ambos
  invulneráveis. Agora só com “1” (`tools/qa_pair.sh` define). QA `god` dos dois modos.
- Recruit: `maps\_gameskill` só tem `player_downed_buffer_time` para normal, hardened e veteran.
  Em Recruit (`easy`), `maps\_coop::downed_player_manager()` multiplicava indefinido na
  primeira queda (erro), encerrava thread: ninguém caía depois e ambos caídos nunca
  falhavam missão. Corrigido para 2 s de Regular. QA `downs` (força Recruit por
  `level.forcedgameskill`): antes 4 FAIL e erro nos dois, depois todas PASS.
- `resetSkill()` executa em cada queda/reanimação (bônus Spec Ops para quem segue em pé) e
  restaurava `threatbias` e `attackeraccuracy` dos dois aos valores de dificuldade, desfazendo
  ajustes da cena. Ambos preservados em torno da chamada. QA `sceneskill`: antes 150 e 1, não 777 e
  0,123; depois todas PASS.
- Dificuldade: botões do popup executam `profile_difficultySave <n>` e `setdvar` em
  `g_gameskill` e `g_gameskill_player_1/2`. Todas latched (indicador 2; `g_gameskill` também tem
  0x2000; `set`, `setdvar`, `seta` nada mudam): `devmap` aplica valor pendente,
  cooperativo começa por `coopLaunch`, escolha nunca aplicada. Início (rva
  `0x22e1a0`) define `g_gameskill_player_<n>` pela dificuldade do membro n (rva `0x5dd988` +
  n * 0x38, perfil próprio); `GetPlayerSetting("gameskill")` lê dvar (rva
  `0x18de0a`), `updateGameSkill()` usa maior dos dois. Host jogava
  com perfil carregado ao iniciar, cliente com seu próprio. Correção: DLL intercepta
  `profile_difficultySave` para escolha host (senão dificuldade jogada), envia como
  `mw2coop_skill` em `coopLaunch`, e `updateGameSkill()` obtém a de cada um dali em
  campanha cooperativa. QA `skill` (host escolhe por `profile_difficultySave`, cliente no
  Regular): escolhas 3, 0, 2 dão nível e ambos jogadores 3, 0, 2 nos dois; DLL de
  distribuição conferida com 3.

## <a id="level-tour-results-2026-10-22"></a>Resultados do percurso dos níveis (2026-10-22)

QA `tour` em duas cópias (host/cliente), modo deus ligado, main do mod daquele dia (cada nível
uma vez entre 07:22 e 13:20; correções anteriores no dia presentes, posteriores não). Por nível:
pontos iniciais (seções), verificações aprovadas/reprovadas no host, erros de script host/cliente,
quadros host/cliente. dc_whitehouse (Whiskey Hotel) e ending (Museum) percorridos mais tarde
(16:55 e 16:58).

| Nível | Seções | PASS | FAIL | Erros de script | Quadros | Notas |
|---|---|---|---|---|---|---|
| trainer | 7 | 91 | 0 | 0/0 | 28/28 | |
| roadkill | 9 | 88 | 1 | 0/0 | 30/30 | teste de caminhada em `dismount`: 26 de 100 unidades (caminhada lenta do nível) |
| cliffhanger | 15 | 162 | 21 | 4/4 | 56/56 | caminhada saiu da borda da caverna, 2 caiu para sempre: corrigido (morte na borda por jogador, andar só com chão); duas primeiras seções repetidas PASS; erros do ponto de desenvolvimento `jump` |
| airport | 9 | 109 | 0 | 6/6 | 34/34 | erros em `grigs_test` / `_anim::get_anim_position` (não investigados) |
| favela | 12 | 123 | 0 | 0/0 | 37/37 | |
| invasion | 17 | 201 | 0 | 0/0 | 62/62 | execução após corrigir ponto Burger Town |
| favela_escape | 13 | 169 | 0 | 0/0 | 52/52 | |
| arcadia | 5 | 65 | 0 | 0/0 | 20/20 | |
| oilrig | 9 | 93 | 0 | 0/0 | 30/30 | início de emergir corrigido depois |
| gulag | 13 | 139 | 4 | 1/1 | 46/46 | 1 enviado a gatilhos em paredes (artefato de teste); erro: morte roteirizada `player_dies_to_cavein` sob modo deus |
| dcburning | 10 | 116 | 0 | 0/0 | 36/36 | viagem Blackhawk corrigida depois |
| contingency | 8 | 104 | 0 | 0/0 | 32/32 | |
| dcemp | 12 | 126 | 0 | 7/7 | 40/40 | erros em `emp_empaftermath` / código inicial ambiente; rigs do parceiro corrigidos depois |
| estate | 10 | 121 | 1 | 4/4 | 38/38 | caminhada em `forest_fight` (shellshock inicial); erros no código de início |
| boneyard | 7 | 83 | 2 | 5/5 | 26/26 | `ride_end`: 2 deixado, corrigido (traseiro UAZ); erros no início de veículos |
| af_caves | 10 | 108 | 1 | 0/0 | 33/33 | caminhada no início padrão: 25 de 99 unidades (não investigado) |
| af_chase | 13 | 39 | 0 | 0/0 | 14/14 | pontos de desenvolvimento da faca pulados |
| dc_whitehouse | 4 | 52 | 0 | 0/0 | 16/16 | |
| ending | 9 | 45 | 9 | 361714/2562846 | 16/16 | 2 não anda (0 de 100 unidades) ou a 1500-1800 do 1 nos pontos de exposição: não corrigido; tempestade de erros `_anim::anim_weight` dos civis também ocorre individual |

## <a id="playtest-2026-10-23-two-pcs-cliffhanger-and-no-russian"></a>Teste jogado 2026-10-23 (dois PCs, Cliffhanger e No Russian)

Duas pessoas pela internet, cada uma em seu PC/conta Steam, com gravador
de sessão nos scripts (`maps\_mw2coop_rec.gsc`: posições a cada segundo, botões,
armas, vínculos, dano, quedas, aliados, escritos em `mw2coop.log` por `setdvar`
interceptada pela DLL). Logs de ambos iguais linha a linha (sem dessincronia). Compilações enviadas
durante sessão (v0.4.6-beta-rec1 a rec10), correções vindas do último log:

| Visto nos logs | Causa | Correção |
|---|---|---|
| 2 perdeu picaretas e caiu quando 1 chegou ao topo | sincronização tirou junto com as do 1 e devolveu no meio da escalada | picaretas próprias de cada um (`level.mw2coop_own_weapons`) |
| 2 ficou dentro da rocha após salto; depois Soap pegou quem já caíra | ponto distante do 2 sob borda estava na rocha; rig oculto ainda atingia `start_gaz` | 2 usa pontos do 1 após vão; sem captura sem `player_hangs_on` |
| queda pôs 2 fora do chão na encosta, depois 40 unidades sob piso | `player_recover` deslocado à faixa, depois início da faixa | ambos recuperam em `player_recover`; movidos ao lado do outro se sobre ele |
| quedas acima do ponto seguro matavam | regra original | qualquer queda da primeira parede volta à base; escalada usa regras fáceis |
| dois MacTavishes no topo | `friendly_init_cliffhanger` cria Soap por captura | segunda reutiliza |
| reinício em `c4` pôs ambos na caverna | `start_c4()` não posiciona ninguém (teleporte comentado) | checkpoints guardam posição onde atingidos; restauram no início |
| final do helicóptero nunca iniciou, missão falhou depois | esperava 2 sair do snowmobile | final começa quando qualquer um chega (como original) |
| No Russian nunca terminou após reinício em `tarmac` | `escape_main()` chama `nextmission()` só do início padrão | `maps\_mw2coop::ending_goes_on()` em cinco finais |

Cliffhanger concluída; correção final No Russian ainda não jogada. Queda de lobby em 12 s vista
antes na QA era artefato de duas cópias num PC (entrar em `127.0.0.1` põe membros em
loopback, heartbeat não alcança socket); dois PCs não afetados.

## <a id="v050-beta-2026-10-25"></a>v0.5.0-beta (2026-10-25)

Versão `v0.5.0-beta` de mw2_coop (tag main 8e4f31c, docs 83c6cbd): zip SHA-256
`661359ebba9e8ee4a9f4d62f2a9a533a00afa341178a72dca848d1897051c4e6`, `winmm.dll` distribuída SHA-256
`12176eeea7bf517c1901812e2f996a3dbc4175ac794c1806bc918a671d4c13fd`, compilada de clone novo do `main` GitHub.
DLL conferida em duas cópias: `spawn` no estande e corda Gulag (`rappel`): PASS nos dois, fontes carregam. Arquivo experimental
32 bits `mw2coop-v0.5.0-beta-x86.zip` (SHA-256 `146d14513c1944b21a4ac3e4c473de0801c191d87d50f6209ad37e4a69b073bf`, DLL
`836f09112cf33694...`): `spawn` PASS em duas cópias 32 bits.

Observações (o que executou; tudo por bots em duas cópias num PC, ninguém jogou com duas pessoas):
- Cenas para ambos: QA `rappel` (corda Gulag: ambos na corda, ambos 479 unidades abaixo, soltos, armas
  nas mãos), `rappel` em af_caves, `gulagevac`, `chopperjump`, `bigjump`, `oilbird`, `invconvoy`: PASS.
- Cliffhanger: `snow`, `snowview` (quadros do condutor e visão do parceiro do snowmobile), `climbview` (quadros
  do escalador e picaretas), `climb` (ambos ao topo; Soap pega ambos; quatro execuções falharam na
  corrida do bot para salto, uma passou com novas picaretas: etapa QA instável, não comprovada).
- S.S.D.D. `course` (portões fecham após ambos passarem), Team Player `seatview` (passageiro olha à frente, sem
  fogo amigo na viagem): PASS.

Aprendizados (úteis noutros jogos deste motor):
- `GetEntArray( value, "script_flag" )` retorna indefinido nesta compilação: escolha gatilhos por classe e compare campo.
- Corpo de jogador (esqueleto multiplayer) não reproduz animações IA da campanha (condutor snowmobile torce sobre
  assento): crie modelo com esqueleto IA vestindo malha do jogador. DLL copia modelo IA ao pool XModel
  e põe superfícies do corpo cooperativo nele (mesmo transplante da equipe No Russian), responde à busca
  de nome inventado; `DB_IsXAssetDefault` deve dizer “não padrão” para esse nome, senão contador de leitores vaza e
  próximo `playsound` trava.
- Attach não aceita ângulos: picareta erguida no punho exige modelo com osso girado na memória.
- Depurar travamento: thread DLL que escreve retornos de todas as outras em arquivo sob pedido
  (arquivo `dumpstacks` na pasta gera `stacks.txt`), sem obter travas que jogo possa segurar.

Não verificados: correção de clique na escalada (hipótese; commit próprio, reverter com `git revert`), furtividade do segundo
jogador em Cliffhanger (sem quadro), slide_sync em Escape from Favela, visão do outro em cada
cena de corda.

## <a id="status"></a>Estado

Feito em v0.5.0-beta: cenas de corda e rapel para dois, portões S.S.D.D., troca Team Player, visões
de snowmobile/escalada Cliffhanger, fontes russas, arquivo experimental 32 bits. Próximo: jogar novas
cenas com duas pessoas, sincronia labial (fora nos dois), erro nrend anim_loop, Museum para 2, tela dividida.
