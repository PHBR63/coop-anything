# <a id="the-witcher-3-wild-hunt-agent-notes"></a>The Witcher 3: Wild Hunt: notas do agente

Notas brutas, fases mais recentes no final. Caminhos usam `<game dir>`.

## <a id="session-2026-10-18-triage-and-research-phases-0-and-1"></a>Sessão de 2026-10-18: triagem e pesquisa (etapas 0 e 1)

### <a id="game-identity-tested-build"></a>Identidade do jogo (compilação testada)

| | |
|---|---|
| Loja | Steam, app 292030, buildid 25773555 |
| Edição | "The Witcher 3: Wild Hunt - Remastered" (linha do patch 5.0, lançada em 2026-09-29) |
| Executável | `<game dir>\bin\x64_dx12\witcher3.exe`, FileVersion 5.0.0.1048522, carimbo PE 2026-10-06 |
| SHA-256 do executável | `2df765398a3d1f165db418271be7200178320a4466817379f2fa0dc0001fb101` |
| Motor | REDengine 3 |
| Sistema operacional | Windows 11 (10.0.26200) |

### <a id="observations-checked-directly"></a>Observações (conferidas diretamente)

- 5.x inclui somente DX12 (`bin\x64_dx12`), sem `bin\x64`. Conteúdo de DLC incorporado em `content\content0` (63 GB, 31 pacotes), com marcadores vazios `dlc-tombstones\<dlc>\*.tombstone`.
- Scripts-fonte continuam incluídos: 1525 arquivos `.ws` em `content\content0\scripts`, agora UTF-8 (mods 4.04 usam UTF-16LE), além de `cookedfinal.redscripts`.
- Versões de formatos mudaram frente aos mods da época 4.04: cabeçalho `.w3strings` 0xA4 (164), antes 0xA2 (162); VTM de `metadata.store` versão 7, antes 6. Pacotes continuam `POTATO70`.
- Funções nativas de Gwent mudaram na 5.0: `gwintManager.ws` original declara `SDynamicCard`, `SGwintCardNameProperty`, `GetGwentCard`, `GetDeck`, `GetDynamicCards`; o executável 5.01 não contém textos `cardIndices`, `leaderIndex` ou `dynamicCardRequirements`.
- **Witcher Online** (rejuvenate7, GPL-3.0, HEAD GitHub `4755ee7`, 2026-08-29), verificações estáticas contra esta compilação:
  - 71 de 76 anotações de scripts (`@wrapMethod`/`@addMethod`/`@addField`) coincidem com classes e assinaturas originais 5.01. Das demais, 3 são falsos positivos do verificador (espaços em genéricos; dois métodos adicionados pelo mod em seu `gwintGameMenu.ws`); 2 visam dependências (`ChillOut`, `NR_PlayerManager` de Custom Player Characters), não verificadas.
  - Substituições completas de `game/gui/menus/gwintManager.ws` e `gwintGameMenu.ws` baseiam-se em 4.04. Declaram `import struct CollectionCard` e `import var cardIndices/leaderIndex/ dynamicCardRequirements` (removidos na 5.01) e descartam `GetGwentCard`, `GetDeck`, `GetDynamicCards`, `IsKingCard` e outros chamados por 8 scripts originais 5.01 (`playerWitcher.ws`, `r4Player.ws`, `quest_function.ws`, `deckBuilderMenu.ws`, ...).
  - O cliente `.asi` não tem hooks próprios; registra funções nativas por WitcherNativeBridge e só recusa API da ponte mais antiga que a sua (compilado para v1, ponte v2).
  - Inclui arquivos `.w3strings` v162 e `metadata.store` v6.
  - A wiki exige 4.04 e `-net -debugscripts`, Shared Imports, Custom Player Characters e Chill Out. Servidor Java, UDP 40000, servidor público oficial ou hospedagem própria com redirecionamento de portas.
- **WitcherNativeBridge** (rejuvenate7 e Flawkee, MIT, `415e1c1`, 2026-10-08 "update for 5.01 remastered"): reprodução off-line da lógica de associação neste executável: 279 pontos de registro, todos os 7 auxiliares resolvidos concordam 279/279, prólogo de `registerGlobal` coincide, padrão textual LogChannel de 5.01 coincide uma vez e o de 5.00 nenhuma. Feito com pequeno script Python que lê seções PE e repete a busca de padrões da ponte no arquivo (somente leitura, nada executado); ainda sem commit.
- **WitcherMMO** (eofim): um commit sobre Witcher Online (2026-10-02) que renomeia o projeto.
- **werasik2aa/Witcher3-Multiplayer** (AGPL-3.0): último commit em 2026-01-15, "DS DISCONTINUED"; README declara sincronização de posição/rotação, combate "10%", NPCs "30% buggy". Creditado por Witcher Online.
- **momo5502/w3m** (GPL-3.0, C++): hooks nativos em endereços absolutos fixos (por exemplo, `0x14027E700`), inicializador, atualizador e servidor próprios; último commit de código em 2026-01-01. Anterior à remasterização.
- **Hyjarion/Witcher3-MP** (AGPL-3.0): envio único em 2023-05-29, versão v0.0.1.

### <a id="derived-reasoned-from-the-above-not-run"></a>Deduções (raciocinadas a partir do acima, sem execução)

- Este executável é o patch 5.01 (compilado em 2026-10-06; 5.01 lançado em 2026-10-08; padrão exclusivo 5.01 da ponte coincide).
- A compilação pública de Witcher Online não consegue compilar scripts em 5.0/5.01 por causa das duas substituições de Gwent. É necessário adaptá-las à API Gwent 5.01 (nomes de cartas em vez de índices) ou substituí-las por anotações.
- WitcherNativeBridge 5.01 deve associar funções neste executável (todas as verificações anteriores aos hooks passam off-line), exceto a tabela de opcodes, preenchida em execução.

### <a id="guesses-unverified"></a>Hipóteses (não verificadas)

- O autor está adaptando Witcher Online à remasterização (ponte atualizada em 2026-10-06/08 com release "Remastered"); uma compilação 5.x talvez já exista no Nexus ou Discord.
- Scripts de mods UTF-16, `.w3strings` v162 e `metadata.store` v6 talvez precisem de recodificação ou reempacotamento para 5.x.
- Steam mantém branches beta "Patch 4.04" (Next-Gen) e "Patch 1.32" (Classic) junto da remasterização (somente resultados de busca, sem conferir no cliente Steam).

### <a id="unknowns"></a>Desconhecidos

- Se existe compilação remasterizada de Witcher Online no Nexus (consultas retornam 403; Discord não consultado).
- Estado remasterizado de Chill Out e Community Patch Shared Imports. Custom Player Characters tem correção 5.01 (Nexus 13735).
- Se `-net -debugscripts` e o canal scriptslog mantêm comportamento em 5.x.
- Se salvamentos 5.x carregam na branch Steam "Patch 4.04".
- Se duas instâncias podem executar no mesmo PC (travas de instância única, inicialização Steam).

### <a id="searched"></a>Pesquisado

Diretório coop-anything, `games/`, issues e PRs (API sem autenticação, "witcher", "redengine": 0 resultados); repositórios acima, commits, releases e issues; busca na web (notas 5.0/5.01, estado remasterizado de Witcher Online, branch Steam 4.04, Script Merger e carregador ASI em 5.x); wiki GitBook Witcher Online. Não consultados: Nexus diretamente (403), Discord, Reddit, YouTube.

### <a id="sources"></a>Fontes

- https://github.com/rejuvenate7/WitcherOnline
- https://github.com/rejuvenate7/WitcherNativeBridge
- https://rejuvenate.gitbook.io/witcheronline/guides/getting-started
- https://rejuvenate.gitbook.io/witcheronline/guides/client-setup/required-mods
- https://rejuvenate.gitbook.io/witcheronline/guides/server-setup
- https://rejuvenate.gitbook.io/witcheronline/general-information/playguide
- https://github.com/eofim/WitcherMMO
- https://github.com/werasik2aa/Witcher3-Multiplayer
- https://github.com/momo5502/w3m
- https://github.com/Hyjarion/Witcher3-MP
- https://witcher.fandom.com/wiki/Patch_5.0_(The_Witcher_3)
- https://gamerant.com/the-witcher-3-remastered-patch-50-notes/
- https://gamersuniverse.eu/en/roll-back-witcher-3-remastered-old-version
- https://www.nexusmods.com/witcher3/mods/13076 (Script Merger - Remastered: scripts 5.x são UTF-8)
- https://www.nexusmods.com/witcher3/mods/13735 (correção de Custom Player Characters para remasterização)

## <a id="session-2026-10-18-later-workspace-toolchain-first-launches"></a>Sessão de 2026-10-18 (depois): ambiente, ferramentas, primeiras inicializações

Objetivo a partir daqui: adaptar Witcher Online para 5.01 e avançar para inimigos e missões compartilhados.

### <a id="observations-runs-on-the-tested-build"></a>Observações (execuções na compilação testada)

- `witcher3.exe -verifyscriptsandexit` compila todos os scripts (originais e mods) e encerra (rc=3 com ou sem falha). Erros aparecem em janela "The Witcher 3: Wild Hunt - Script Compilation Errors", cujo controle Edit contém a lista completa (ler com WM_GETTEXT). Cerca de 10 a 40 s por execução.
- A remasterização carrega **mods Steam Workshop** de `steamapps\workshop\content\292030\<item>\mods\`. O mod antigo "Fast travel from anywhere" (3253049013), da época 4.04, substitui `game\gui\menus\mapMenu.ws` e quebra a compilação em toda inicialização (78 erros desse arquivo, incluindo um apontado no original `player.ws` porque chama `GetShownMapType` do mod). Erros de arquivos de mods aparecem sem prefixo `[content0]`.
- Scripts originais 5.01 compilam sem erros com esse mod desativado.
- `Documents\The Witcher 3\mods.settings` por mod com `[modName]` `Enabled=0` é respeitado pelo compilador. `[ContentManager/Mods] EnabledWorkshop=false` em `dx12user.settings` não é (é a opção interna "Enable Steam mods"; não impediu a compilação).
- 5.01 lê somente `dx12user.settings` (e `profile.settings`); o executável não tem texto `user.settings`.
- Scripts UTF-16LE com BOM ainda compilam em 5.01 (mod Workshop "Candle interactions").
- Opções úteis no executável: `-windowed -width -height -borderless`, `-world`, `-position`, `-noplayer`, `-net`, `-debugscripts`, `-show_script_log_channels`, `-forcescriptcompilation`, `-verifyscriptsandexit`, `-silentscripts`, `-scriptdefines=`, `-compile_nonstrict`, `-disablemods`, `-noninteractivecrash`, `-silentcrash`; também lê `commandline.txt`.
- WitcherNativeBridge 415e1c1 compilado com VS 2022 (v143) e carregado por Ultimate ASI Loader 9.7.4 como `bin\x64_dx12\dinput8.dll`. Log: `registration sites=279 consensus=279`, conversão de strings OK, hook instalado, `native registration: WNB_GetApiVersion=OK`. Versão numérica do executável: 5.0.15.65482.
- A atualização da ponte mostra que strings de scripts e CNames agora são UTF-8 (`char`), não UTF-16. O cliente Witcher Online ainda lê `WNB_String.data` como `wchar_t`; dados enviados ficariam corrompidos na 5.01.
- 5.0 trocou o enum `EAreaName` das APIs por CNames (`GetCurrentArea() : name`, `GetCurrentJournalArea(out name)`, novo `GetDeprecatedAreaName(int) : name`); `AreaTypeToName` foi removido. Witcher Online usa a API antiga em cerca de 30 locais.
- Custom Player Characters, Chill Out e Shared Imports não têm código público; Witcher Online usa `ENR_PlayerType` do CPC cerca de 500 vezes e `ChillSpot`/`CO_*` de Chill Out cerca de 20 vezes.

## <a id="session-2026-10-18-later-port-compiles-two-clients-see-each-other"></a>Sessão de 2026-10-18 (depois): adaptação compila, dois clientes se veem

### <a id="observations-game-501"></a>Observações (jogo 5.01)

- Adaptação Witcher Online (branch `remastered-5.01` de clone local, sem commit) compila em 5.01 com Gwent PvP isolado por `#ifdef WO_GWENT_PVP` e substitutos de compilação para Custom Player Characters e Chill Out. Mudanças: `map` é nova palavra-chave (renomear variáveis); `@addMethod(CInputManager) import function IgnoreGameInput(...)` em vez de addMethod sem corpo; API de áreas adaptada para nomes mantendo códigos numéricos no protocolo (`areaCompat.ws`); cliente lê strings como UTF-8 em 5.x.
- Pré-processador de scripts 5.x funciona: `#ifdef/#ifndef/#else/#endif` no nível superior e em funções (também existem textos de diretivas `define`, `-scriptdefines=`; `#define` ainda não testado).
- `@addMethod(Class) import function X(...)` é a forma 5.x de expor método nativo não declarado.
- Trava de instância única: mutex nomeado `cdprojekt_red_the_witcher_3_wild_hunt` (CreateMutexA). Renomear no processo (hook IAT em ASI de teste) permite várias instâncias; sem isso, a segunda mostra "game is already launched" e encerra com rc=1.
- Execuções autônomas precisam, somente em teste: GetForegroundWindow simulada para a janela do jogo; WM_ACTIVATE/WM_ACTIVATEAPP/WM_KILLFOCUS filtradas (sem pausa ao alternar janelas); ClipCursor, SetCursorPos, SetForegroundWindow, GetAsyncKeyState e INPUTSINK de entrada bruta neutralizados para nunca capturar mouse, foco ou digitação do usuário; áudio por processo silenciado.
- Inicialização: StartupMoviesMenu (vinhetas), RecapMoviesMenu (`gamestart/recap_wip.usm`, cerca de 3 min), StartupExperienceMenu, CommonMainMenu. Fechar os dois menus de vídeo em OnConfigUI reduz a chegada ao menu a aproximadamente 12 s.
- Carregar salvamento 4.04 na 5.01 exibe uma vez diálogo modal "Skill points reset / new skill system" (UDB_Ok). Pausa até responder; todos os diálogos passam por `CR4GuiManager.ShowProgressDialog`, permitindo ao invólucro de teste registrar e responder.
- Salvamentos 4.04 carregam na 5.01 (`LoadLastGameInit` em invólucro de CommonMainMenuBase.OnConfigUI).
- DLC 4.04 de Witcher Online (metadata.store v6, pacotes) carrega em 5.01: representantes remotos são criados de `dlc\dlc_mpmod\data\entities\geralt_npc.w2ent`.
- **Teste automatizado `see_each_other` PASS** (2 clientes + servidor local, mesmo salvamento): cada cliente criou o representante do outro na posição informada (502.48, 1715.15, 3.61). Execução `20261018-162109-see_each_other`, cerca de 2,5 min sem intervenção.
- O pacote próprio do mod contém apenas `gwint_game.redswf` (tabuleiro Gwent 4.04); não instalado em 5.x.

### <a id="derived"></a>Deduções

- Nível de QA para visibilidade de jogadores: automated (2 clientes, um PC). Todo o restante sem teste.

## <a id="session-2026-10-18-evening-unattended-multi-instance-qa"></a>Sessão de 2026-10-18 (noite): QA autônomo com várias instâncias

### <a id="observations"></a>Observações

- Cenário `movement` PASS (2 clientes): o jogador móvel teleporta 6 m para frente e para trás; o representante no observador termina a até aproximadamente 1,5 m da posição da rede após cada movimento (4 observados). Execução `20261018-171106-movement`. `see_each_other` também PASS antes.
- Instância de teste não deve usar a pasta Documents real: o menu chama `SaveUserSettings`; opções `-width/-height` acabam em `dx12user.settings` real (e `.bak`). Corrigido com hooks em `SHGetKnownFolderPath(FOLDERID_Documents)` e `SHGetFolderPathW/A(CSIDL_PERSONAL)` no ASI de teste, preparando sandbox por bot (cópias de configurações, `mods.settings`, um salvamento); o ASI recusa iniciar teste sem isso.
- Duas instâncias com ray tracing terminaram em falha de dispositivo GPU removido (DXGI 0x887A0020) e reinicialização do driver (WER LiveKernelEvent). Sandboxes agora usam o preset "low" do próprio jogo (expandido de `user_config_matrix/pc/graphics.xml`), RT desligado, `-noraytracing`, `[Engine] LimitFPS=30`, 640x360.
- Por instância nesse preset: aproximadamente 10,5 GB de RAM privada e 4 GB de VRAM. Em placa de 12 GB compartilhada com aplicativos, duas instâncias podem exceder a VRAM e cair para poucos FPS; o observador conta movimentos cumulativamente para atualizações lentas não causarem falha.
- Telas iniciais a tratar: StartupMoviesMenu, RecapMoviesMenu (cerca de 3 min), StartupExperienceMenu (vinculação de conta CDPR e consentimento de telemetria; testes fecham sem responder para não armazenar consentimento) e diálogo único de redefinição de habilidades para salvamentos 4.04.

## <a id="session-2026-10-18-night-steam-relay-and-player-package"></a>Sessão de 2026-10-18 (noite): retransmissão Steam e pacote para jogadores

### <a id="observations-1"></a>Observações

- `bin\x64_dx12\steam_api64.dll` do próprio jogo (10.87.46.89) exporta `SteamAPI_InitFlat`, despacho manual e interfaces `SteamUser_v023`, `SteamMatchmaking_v009`, `SteamFriends_v018`, `SteamNetworkingMessages_SteamAPI_v002`; processo retransmissor Spacewar (480) separado pode carregá-la, sem redistribuição.
- `w3relay` (padrão HXCoop): host dá a cada membro um socket UDP local para o servidor Witcher Online; cliente vincula 127.0.0.1 e encaminha ao dono da sala. Witcher Online não precisa mudar: o cliente só conecta a 127.0.0.1.
- Autoteste do retransmissor com `steam_api64.dll` simulada PASS, incluindo cliente que começa 25 s atrasado e não membro cujo tráfego não pode alcançar o servidor.
- Primeira versão falhou com dois clientes: host só respondia confirmações de atividade de jogadores que já tinham enviado dados; convidado ainda carregando recebia 20 s de silêncio e saía. Corrigido (host acompanha todos no canal de controle; convidado tenta entrar novamente em vez de encerrar).
- Steam real: inicialização como 480, criação de sala e encerramento limpo funcionam. `LobbyCreated` chega duas vezes (resultado da chamada e transmissão); tornado idempotente.
- `movement --relay` PASS (segundo cliente somente pelos retransmissores), também com o pacote distribuível instalado byte a byte.
- Pacote para jogadores (179 MB): mod adaptado + substitutos, DLC, carregador ASI, ponte, cliente, retransmissor, servidor jar, inicializadores Host/Join, licenças e código das partes GPL.

### <a id="unknowns-1"></a>Desconhecidos

- Entrada entre duas contas Steam reais em dois PCs (latência, convite e fluxo Join Game).
- Chat, gestos, cavalos, sincronização de grupo/diálogo na 5.01 (ainda não exercitados pelos bots).
