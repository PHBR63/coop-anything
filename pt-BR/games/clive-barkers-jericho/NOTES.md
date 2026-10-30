# <a id="clive-barkers-jericho-working-notes"></a>Clive Barker's Jericho: notas de trabalho

## <a id="identity-of-the-tested-build"></a>Identidade da compilação testada
- Loja: disco comercial (disco antigo do usuário, reinstalado)
- `bin/Jericho.exe` FileVersion 1.0.0.1, marca de tempo PE 2007-09-21, SHA-256 `7fb5b759823283a83b685adc4848289a149f520ddbab6dbc7f9e6131b15d2a62`
- 32 bits, D3D9 (d3dx9_31), PhysX (PhysXLoader, NxCooking), FMOD Ex, Bink, XInput 1.3, DInput8
- SecuROM: executável contém seção `.securom` e strings de ativação.

## <a id="session-2026-10-18-triage-phase-0-and-first-research-phase-1"></a>Sessão 2026-10-18: triagem (etapa 0) e pesquisa inicial (etapa 1)

### <a id="observations-checked"></a>Observações (conferidas)
- Núcleo: nenhuma entrada Jericho em `DIRECTORY.md`, `data/directory.yaml`, `games/` ou guias. Busca de issues e PRs GitHub por "jericho": 0 resultados.
- Web: nenhum mod cooperativo ou multiplayer encontrado. Pedidos de jogadores:
  - https://www.moddb.com/forum/thread/clive-barkers-jericho-multiplayer
  - https://steamcommunity.com/app/11420/discussions/0/846963710897727939/
  - https://gamefaqs.gamespot.com/boards/934444-clive-barkers-jericho/41226885
- Ferramentas de mod existentes: SMOD (https://www.nexusmods.com/clivebarkersjericho/mods/2, página respondeu 403 ao WebFetch; conhecido só por trechos de busca).
- Motor é ScrapEngine da MercurySteam, usado em Scrapland: strings `.\ScrapEngMain.cpp`, `ScrapEngWorld.cpp`, vínculos Lua de teclas para conjunto de ações "Racer" (Laser, Vulcan, Devastator, Swarm) em `scripts/quickconsole.lua`.
- **O executável contém camada completa de rede cliente/servidor** (multiplayer de Scrapland):
  - caminhos `Net\GameServer.cpp`, `Net\ManServer.cpp`, `Net\ManClient.cpp`, `Net\msgman.cpp`, `Net\NetData.cpp`; classes `cServerNetManager`, `cClientNetManager`
  - importa UDP WSOCK32 (`socket`, `bind`, `sendto`, `recvfrom`, `select`)
  - variáveis: `DefaultServerPort`, `DefaultServerAddress`, `DefaultMaxPlayersOnServer`, `JoinServerOnStartup`, `ServerType`, `ServerMapList`, `ServerName`, `ServerPassword`, `ClientPPS`, `NetTimeOut`, `LogNetData`, `MasterServerAddress/Port`
  - strings de linha de comando: `server`, `dedicated`, `Init Server at %s`, `Using default server map` com `Levels/FZ` (mapa Scrapland ausente dos dados Jericho)
  - callbacks de script: `OnClientJoin(...)`, `OnClientExit(...)`, `OnClientModify(...)`, `OnChatString`, `OnUsrString`; assinaturas descrevem naves Scrapland (`PilotName, Motor0..3, WeaponBay`)
  - biblioteca Lua `Net`: `InitServer, CloseServer, IsServer, ServerChangeLevel, AddResource,
    ModifyUsrData, GetServerData, GetBotName, GetObjName, InitClient, CloseClient,
    IsClient, GetClientData, GetMyClientShip, InitBrowser, DoneBrowser, SendUsrString,
    SendChatString, SendCtrlString, SendMasterString, IsMaster, PingInetSvrs, GetPing`
- Scripts quase não a usam: somente `scripts/quickconsole.lua` (`QuickConsole.reload`) chama `Net.IsServer/IsClient/CloseServer/CloseClient`.
- Lua 5.1.1 (`$Lua: Lua 5.1.1 ...` no executável). Vínculos: `LuaInterface\*.cpp` (bibliotecas Game, Act, AI, AIBehav, AITeam, FX, Input, Physics).
- Arquivos `*.packed` são BFPK: `"BFPK"`, versão u32 (1 para Data0x, 0 para Voices), contagem u32, entradas `u32 name_len, name, u32 size, u32 abs_offset`. Ferramenta: `tools/bfpk.py` no repositório do mod.
- Scripts são `*.lc`: cabeçalho u32 (não é tamanho bruto; significado desconhecido) e fluxo zlib de bytecode Lua 5.1 padrão (`\x1bLuaQ`, int 4, size_t 4, instrução 4, número 8), com informações de depuração. 1533 arquivos; todos descompilam com unluac 2025-12-23 em Lua legível com nomes locais.
- Configuração: GVars gravadas em `game.cfg` sob `%APPDATA%\Codemasters\Clive Barker's Jericho` (formato `name = value ### comment`); existem `ModFileName`, `ModPathName` (nome/caminho de modificação); carregador também reconhece extensão `.2BPACK`.
- Camada de entrada aceita controles 0..3 (`pad>=0 && pad<4`) e tem `ResetToSplit`.
- 34 fases em `levels/` (alk_*, cru_*, rom_*, sum_*, wwii_*, menu), cada qual com pasta `scripts/` (mapa, gatilhos, inimigos, cenas, física).

### <a id="derived"></a>Deduzido
- Modo cooperativo não exige criar rede do zero: cliente/servidor UDP com criação de entidades, descritores de usuário, ping, chat e troca de fase provavelmente ainda funciona no executável. O trabalho é colocar personagens, IA, gatilhos e cenas de Jericho nessa camada e corrigir partes removidas. Corresponde à triagem "motor com multiplayer e fonte de scripts".
- Jericho é um jogo de esquadrão com troca de personagem; desenho cooperativo natural: cada jogador controla um integrante, IA controla os demais.

### <a id="guesses-unverified"></a>Hipóteses (não verificadas)
- Camada de rede pode estar parcialmente desativada em Jericho; replicação talvez só conheça entidades Scrapland (naves).
- `server` / `dedicated` na linha de comando podem iniciar host diretamente.
- `ModPathName` pode carregar arquivos avulsos ou pacotes extras (mods sem reempacotar Data0x).

### <a id="unknowns"></a>Desconhecidos
- Loja; necessidade de ativação on-line SecuROM nesta compilação.
- Se o jogo roda no Windows 11 pela cópia de teste.
- Se a rede inicia e conecta, e o que replica.
- Significado do cabeçalho u32 de `.lc`; se o motor carrega fonte `.lua` simples.

## <a id="session-2026-10-18-first-launch-test-copy-windows-11"></a>Sessão 2026-10-18: primeira inicialização (cópia de teste, Windows 11)

### <a id="observations-checked-1"></a>Observações (conferidas)
- Primeira inicialização falhou no início; log.html: `FATAL ERROR: Check failed! physicsSDK && "Wrong PhysX
  SDK DLL version?"` (`World\WorldPhysics.cpp`, linha 1587). Inclui `NxCooking.dll` 2.7.0.3, exigindo núcleo PhysX 2.7.0. Naquele momento só havia 2.7.1 a 2.8.4.
- Usuário instalou NVIDIA PhysX System Software 9.12.0613 do disco. Depois passou a existir `%ProgramFiles(x86)%\NVIDIA Corporation\PhysX\Engine\v2.7.0\PhysXCore.dll` (2.7.0.9).
- Segunda inicialização: janela "Clive Barker's Jericho" ainda ativa após 40 s; usuário confirma início. log.html fica vazio enquanto roda (descarrega ao sair?).
- Correção comunitária para a mesma falha: PhysX legacy 9.13.0604 ou 9.12.x (https://steamcommunity.com/app/11420/discussions/0/846945955298387706/).

## <a id="session-2026-10-18-first-network-experiments-test-copy"></a>Sessão 2026-10-18: primeiros experimentos de rede (cópia de teste)

### <a id="observations-checked-2"></a>Observações (conferidas)
- Sintaxe (tokenizador desmontado em 0x402ae0): tokens `-Name:value`, separados por espaços, valores entre `"` ou `'`. Cada par vai ao tratador 0x402ce0: se `Name` é GVar, define-a (qualquer variável de `game.cfg` pode ser substituída ao iniciar); senão trata `build`, `dedicated`, `server`. `-server` / `-dedicated` chamam InitServer durante a análise dos argumentos e falham com `Check failed: LangTabl` (`Global\Language.cpp:29`): cedo demais, tabela de idiomas não carregada.
- GVars úteis: `FullScreen` (0 = janela), `VideoWidth/Height`, `SelectedLanguage`, `debug` (0..3, detalhe de logs), `OutDebugFile` (log de console em texto), `InitLuaLine` (Lua após init.lua, depois limpa), `iMap` (mapa inicial, padrão `Levels/Menu`), `LogNetData`, `ShowNetStatus`, `SoundMainVolume/MusicMainVolume/VoiceMainVolume`.
- `-InitLuaLine:"print('COOP_INIT_OK '..tostring(Net.IsServer()))"` exibiu `COOP_INIT_OK 0`: Lua arbitrário roda ao iniciar sem alterar arquivos.
- Carregador também tenta `<ModFileName>.packed`, `English.packed`, `Voices.packed`, `Pack1.packed` (log `Pack: X not found`): pacotes extras podem ficar junto aos originais.
- `SelectedLanguage` gravado pelo jogo neste PC é `Русский` (cp1251), mas só há texto em inglês/francês/alemão/italiano/espanhol; por isso aparece seleção de idioma. Testes passam `-SelectedLanguage:English`.
- `Video/*.bik` ausentes são ignorados com `ERROR: video file not found` (movidos a `Video.disabled` só na cópia). Sem isso, vídeo Prologue bloqueia a janela.
- Vínculos Lua `Net` (tabela luaL_Reg perto de VA 0x72e4f8), argumentos por strings de formato:
  - `Net.InitServer(map:string, maxPlayers:int, port:int) -> 1/0` (0x53b3e0, formato `"sii"`, chama 0x482030; primeiro teste com `(map, 28086, 4)` abriu UDP 4)
  - `Net.InitClient(address:string, port:int) -> 1/0` (0x53b790, formato `"si"`, chama 0x481a30)
- `Net.InitServer('Levels/Alk_Desert',4,28086)` por InitLuaLine: log `Starting server at ...`, UDP 0.0.0.0:28086 aberto; depois Alk_Desert carrega, e seus scripts/cena inicial rodam como servidor.
- Segunda instância mostra "Session detected / Clive Barker's Jericho is already running." Verificação é `FindWindowA("MercuryGameClass", NULL)` em código ofuscado SecuROM (0x5820b0).
  - Área de trabalho oculta separada (CreateDesktop) evita verificação, mas D3D falha: `Could not find any compatible Direct3D devices.`
  - Funciona: proxy `dinput8.dll` só para teste em `bin/` (`native/` no repositório) que, apenas com variável `JERICHO_MULTI=1`, faz FindWindowA retornar NULL para essa classe. Executável intacto.
- Cliente `Net.InitClient('127.0.0.1',28086)` pelo menu: `Try to server`, `COOP_CLI 1`, `'Ready to build' message send to server`.
  - Execução 1 (cliente 45 s após servidor): servidor nunca registrou cliente.
  - Execução 2 (cliente após 80 s, LogNetData=1): servidor registrou `Creating new client!` e falhou com `Check failed: newpos<=size` (`FileSys\FileMem.cpp:46`). Cliente ficou no menu.

### <a id="derived-1"></a>Deduzido
- Transporte e negociação ainda funcionam no executável comercial. Primeiro impedimento: construir estado inicial do cliente; arquivo de memória de tamanho fixo transborda, provavelmente dimensionado para Scrapland (`NetMaxResourcesSend`, `NetMaxPlayersInitSend` e `Global/StaticBuffer.h` são candidatos).

### <a id="unknowns-1"></a>Desconhecidos
- O que o servidor serializa e tamanho do buffer.
- Se `NetMaxResourcesSend` / `NetMaxPlayersInitSend` alteram esse tamanho.

## <a id="session-2026-10-18-evening-own-transport-lua-bridge-puppets"></a>Sessão 2026-10-18 (fim da tarde): transporte próprio, ponte Lua, representantes

### <a id="observations-checked-3"></a>Observações (conferidas)
- Rede do motor abandonada: `newpos<=size` (FileSys\FileMem.cpp:46) ocorre ao analisar pacote de entrada do cliente (Net\ManServer.cpp perto de 0x4839ac): espera NET_GAME_ID 0xCEBA, NET_GAME_VERSION 0x101 e descritor de nave Scrapland (strings em +0x8c..+0x40c, u16 +0x490, u32 +0x48c). Construtor cliente fica na seção SecuROM. Encontrado por dump de pilha em hook GetLastError (tratador Check failed em 0x404f00 chama GetLastError primeiro).
- API C Lua 5.1 no Jericho.exe (cdecl, assinaturas padrão): lua_pushnil 0x662770, lua_pushnumber 0x662790, lua_pushlstring 0x6627d0, lua_pushstring 0x662810, lua_pushboolean 0x662940, lua_tolstring 0x663e90, lua_tonumber 0x663f30, lua_toboolean 0x663f80, lua_tointeger 0x663ff0; topo lua_State em +8, base em +0xc; global lua_State* em 0x7cd390; equivalente luaL_dostring em 0x663cb0. Auxiliares de argumentos: getargs 0x661fe0 (formato b d f i s v |), pushret 0x52df90 (b d f i s v).
- Tabela luaL_Reg `Net` em 0x72e4f8 (24 entradas). dinput8.dll do mod reescreve 8 não usadas para Net.CoopHost/CoopJoin/CoopSend/CoopRecv/CoopStatus/CoopClose/CoopTime/CoopLog (ENet 1.3.18 em thread de fundo). Duas instâncias trocaram ping/pong, ida e volta de 2-5 ms.
- InitLuaLine roda uma vez por inicialização Lua via 0x663cb0 e é limpa em seguida (seção realocada perto de 0x481548c). Rearmá-la por função Lua agendada executa mod em toda fase. `dofile` aceita caminhos absolutos de avulsos; `io`/`os` ausentes; `debug`, `coroutine`, `loadstring` existem; Game.AddScheduledFunc produz tick de 20 Hz.
- Personagens: `UsrControl` 0 = entrada do usuário 0, -1 = IA; `oAI.bEnable` liga/desliga IA. Sem IA e UsrControl -1, escrever `InCtrl_Walk`/`InCtrl_Str` (e `Ang`) faz corpo correr com animação própria (Action=Run). `UsrControl=1` é aceito (`Game.UsrEntity(1)` retornou corpo), mas entrada do dispositivo sobrescreve InCtrl. No corpo local, `IgnoreUsrControl=1` permite ao bot dirigir por InCtrl.
- Convenção: Ang.y = giro horizontal (graus); frente = (-sin yaw, -cos yaw) em x/z (Black em 113 correu por (-0,92, +0,39)).
- Teste com duas instâncias em rom_tepidarium (host Rawlings, cliente Black): cliente seguiu a fase, trocou para Black, bot correu em círculos; representante Black no host teve erro de 23-140 unidades e correções periódicas; representantes do esquadrão do host no cliente ficaram em 0-45 unidades.
- INCIDENTE: execução posterior congelou a área de trabalho (logs param em `Engine 3D initializing` do cliente, nenhum TDR nos eventos, kernel vivo); reinício forçado. Nova regra: uma instância e bot sem interface (tools/bot/coop_bot.py) por padrão; duas só com autorização. Usuário depois habilitou GPU integrada e ligou segundo monitor nela.

### <a id="unknowns-2"></a>Desconhecidos
- Se D3D9 pode renderizar no adaptador 1 (existem `AdapterInfo`, `Render Last Device name`) ou se preferência GPU do Windows se aplica. → Respondido abaixo: hook IAT em Direct3DCreate9 e vtable em CreateDevice resolvem.

## <a id="session-2026-10-18-night-safe-two-instance-testing-background-mode"></a>Sessão 2026-10-18 (noite): duas instâncias seguras, segundo plano

### <a id="observations-checked-4"></a>Observações (conferidas)
- GVar `OnRenderDebug` nomeia função Lua chamada a cada quadro renderizado, mesmo com tempo reduzido (10 s reais: 297 chamadas na velocidade normal, 301 com SetTimeSpeed(0.05)); `Game.AddScheduledFunc` segue tempo do jogo (150 contra 9 ticks). Mod roda por OnRenderDebug.
- Hooks de exibição da DLL proxy (tabela de importação e vtables COM, por ambiente): `JERICHO_WINPOS=x,y` cria janela ali (log `window 0,0 -> 1940,20`); `JERICHO_ADAPTER=window` cria dispositivo D3D9 na GPU do monitor (log `CreateDevice asked=0 used=1 (<integrated GPU> ) hr=0`), funciona corretamente.
- Jogo pausa com janela inativa (usuário viu janelas congeladas; Lua do host parou quando cliente recebeu foco). `JERICHO_BACKGROUND=1` substitui procedimento para ignorar desativação e simula GetForegroundWindow/GetActiveWindow. Como consulta GetAsyncKeyState e move cursor por SetCursorPos, modo de fundo também zera GetAsyncKeyState, ignora SetCursorPos/SetForegroundWindow/SetFocus/BringWindowToTop e esvazia DirectInput GetDeviceState/GetDeviceData quando janela não está realmente à frente.
- Bot sem interface repetindo percurso gravado (bot de desenvolvimento 'wander', respeita colisões): erro médio do representante no host 11-24 unidades, 1 correção em 70 s (contra 31, média ~55, com bot atravessando paredes).
- Duas instâncias reais (host GPU dedicada, cliente integrada, janelas no monitor secundário, segundo plano, BelowNormal, R_LimitFPS 30): 60 s sem problemas. Representante Black do cliente no host: média 13-23, máximo 55-127, 0 correções. Representantes do esquadrão do host no cliente: erro 0-10.

### <a id="derived-2"></a>Deduzido
- Etapa 2 da implementação (tornar segundo jogador visível) passa em rom_tepidarium. Inimigos ainda simulados independentemente (próximo: autoridade do host).

## <a id="cutscene-pov-camera-2026-10-18"></a>Câmera de ponto de vista em cenas (2026-10-18)
- `FCam.Ang` usa RADIANOS, enquanto `camAng` (resultado só de leitura de qualquer câmera) usa graus (créditos sum_end: `cam.Ang = V3D(-0.3, 3.4, 0)`, `Fov = 1.35`). Usar graus gira descontroladamente; era o "ponto de vista caótico" das gravações anteriores.
- Oculte modelo com `e.bObjectVisible = false`; há `bShowNode_<node>` por nó. `bRender` não existe em entidades (somente nos dados do modelo). Câmera tem clipNear.
- Nomes de propriedades do motor aparecem como strings junto a `TimeSpeed`, `EntityLink`.
- Resultado: outros jogadores veem cenas em primeira pessoa pela cabeça do próprio ator (corpo oculto), mirando o ponto atingido pelo raio da câmera da cena, suavizado. Conferido em TheTrap por vídeo.
- Testes com vídeo: native/capture.c (hook Present, resolução MSAA), tools/record.ps1, sheet.ps1.
- Outros downloads: ffmpeg (BtbN master-latest win64 gpl), SHA-256 `4c967363c4f369172cfec1336d8364814c181c749cb34f654d522af1542fd29e`.

## <a id="session-2026-10-22-first-human-session-022"></a>Sessão 2026-10-22: primeira sessão humana, 0.2.2

- `Game.UsrEntity(n)` lê tabela de usuários locais sem verificar limites (0x427470). Scripts chamam `Game.UsrEntity(fp.id)` em modelos de primeira pessoa; id fora dos usuários (-1 ou 3 usado para ocultar modelo em uma visão dividida) lia ponteiro inválido e falhava (0x427489; tratador chama ExitProcess com 0xC0000005). Invólucro Lua retornando nil para usuários ausentes resolveu; scripts aceitam nil sem erro. Tratador vetorizado no proxy (só testes) revelou endereço da falha; tratador original mostra só caminho de saída.
- Corpo posicionado pela rede, com colisão desligada, não é mantido no chão pelo motor: delegar altura abaixo de um limiar deixava remotos até 40 unidades dentro/acima do piso em rampas e escadas. Siga a altura do responsável a cada quadro.
- `InCtrl_Crouch` agacha corpo sem IA parado, mas não um movido por `Pos` a cada quadro: execute a ação `Duck*` do responsável (`ForceAction`) e `Relax` ao terminar.
- Paredes invisíveis só para quem entrava: fases desligam entidades `InvisibleBlocker` (`bMapCollision`) no fim de conversa da equipe ou caminhada de IA "do jogador"; esse fim pode nunca ocorrer no cliente. Sincronize bloqueios do host.
- Motor recusa iniciar sem mouse (`Input\PcMouse.cpp`, linha 176), mesmo com controle: PC de teste funciona sem monitor e teclado, mas não sem mouse.

## <a id="session-2026-10-23-023-squad-leaders-objects-splits-updates"></a>Sessão 2026-10-23: 0.2.3 (líderes, objetos, divisões, atualizações)

### <a id="observations-checked-5"></a>Observações (conferidas)
- `AreaManager` e "siga-me" do esquadrão usam só usuário local 0; áreas amplas demais para saber de quem um integrante está próximo. Comportamento próprio `CHASE_WITHOUT_ACTION_CHAR` segue qualquer entidade nomeada, atendendo líder não host.
- Objetos quebráveis são nomeados pela fase, não por prefixo: lista `MapPhysicObjects` e nomes `DM_Physic_`/`OB_` cobrem-nos; partes `BoE_` pertencem a scripts de personagens e não devem mudar.
- `OnDamage` de legionário (`chars/legionary.lua`) devolve dano se o golpe anterior atingiu escudo. Definir `Life = 0` por script nesse caso não persiste (vida lida inalterada); teste que "mata a onda" precisa evitar callback. Jogador acertando além do escudo não é afetado.
- Windows PowerShell 5.1 iniciado do PowerShell 7 herda `PSModulePath` e não consegue carregar módulos próprios (`Get-FileHash` ausente). Inicializador por atalho deve limpar variável ou evitar cmdlets de módulos (.NET `SHA256`, `ZipFile`).

## <a id="session-2026-10-23-024-player-souls-display-settings"></a>Sessão 2026-10-23: 0.2.4 (almas dos jogadores, exibição)

### <a id="observations-checked-6"></a>Observações (conferidas)
- Muitos campos de menu (por exemplo, `<id>OnSelect` de uma entrada do esquadrão) aceitam escrita Lua, mas não leitura: registra "BaseType ... can't read" em game.log e retorna nil. Invólucro que lia o campo para desabilitar entrada nunca desabilitava, enquanto simulação que aceitava leituras passava; agora a simulação erra nas leituras. Recalcule a condição (teste original `Team.IsPlayerAvaliable(name)`).
- Espírito de fogo do chefe final (EvilAbabanili) dirige em `0x4fc9b0`: objeto +0x68 é responsável, +0x64 é presa; sem presa, escolhe nova e lê sem conferir (`mov eax,[edx]` em `0x4fcd47`). Com todos próximos caídos ou presos pela runa, EDX = 0 e falha (teste de separação da história; solo nunca chega ali). O caminho "sem alvo" em `0x4fcd2a` tem a mesma pilha e pilha x87 vazia; tratador vetorizado pode retomar ali para essa leitura.
- D3D9 `Reset` com `FullScreen_RefreshRateInHz = 0` mantém taxa atual, não padrão do monitor; voltar a "Auto" em execução exige a taxa recebida em `CreateDevice`.
- Dicas de mensagem (`Scorer.SetMsgText`) não são desenhadas nos menus; caixa própria é `Menu.AcceptMenuMultiline(text, nextFunc)`. Salvar configuração reconstrói menu principal por callback depois; caixa exibida imediatamente é substituída.

## <a id="session-2026-10-23-025-024-completed"></a>Sessão 2026-10-23: 0.2.5 (0.2.4 concluída)

### <a id="observations-checked-7"></a>Observações (conferidas)
- "Mouse not found" (PcMouse.cpp) vem de verificação original em código SecuROM ofuscado: dispara quando DirectInput `CreateDevice(GUID_SysMouse)` falha, não por `GetSystemMetrics(SM_MOUSEPRESENT)` ou enumeração (DLL diagnóstica falhou cada um; só `CreateDevice` reproduziu). Implementação substituta `IDirectInputDevice8A` (32 métodos, `GetCapabilities` como mouse de 3 eixos/3 botões, `GetDeviceState` zerado) basta para iniciar e jogar com controle.
- `dofile` Lua abre caminhos pela página ANSI. `GetShortPathNameW` só fornece caminho útil em volumes com nomes 8.3 (D: do PC de teste não tem); caminho relativo à pasta de trabalho funciona em qualquer volume quando jogo é iniciado da própria pasta.
- Runa final (`EvilFirstBorn` agendada a cada 0,1 s) define `Team.UnavaliablePlayers`, mas tutoriais (`wwii_biggates`, casamatas) também, mantendo IA do personagem bloqueado; só agendamento da runa indica corpo realmente preso.
- Animação de agonia desliga IA do caído (evento `bAI_bEnable=0`); reanimação religa, tanto em integrante de IA como em corpo abandonado pelo jogador.
- Tela "Press [ENTER] or START" (`MainMenu.PressStartMsg`, chamada de `MainMenu.Init2` no PC) é `Menu.VerticalMenu` de um item posicionado em Y 380 de 480, abaixo; SMOD a pula.
- Iniciar menu principal recarrega brevemente `PhysicalAspectRatio` da configuração; organizar algo nesse momento por `Game.Get("PhysicalAspectRatio")` usa proporção do monitor, não da janela. Use a proporção imposta pelo mod.
- `PrintWindow(PW_RENDERFULLCONTENT)` da janela D3D9 às vezes retorna quadro vazio; tente algumas vezes. Nunca recorra a copiar a tela: janelas sobrepostas apareceriam.
- `@(f)` em torno de função PowerShell que retorna `, @($list)` cria array de um elemento contendo a lista: itens são unidos por espaços ao virar string; lista vazia vira uma string vazia.

## <a id="session-2026-10-24-026-027-clean-exit-any-version-updated-split-screen"></a>Sessão 2026-10-24: 0.2.6-0.2.7 (saída limpa, atualização de qualquer versão, tela dividida)

### <a id="observations-checked-8"></a>Observações (conferidas)
- Aviso D3D9 ao sair é verificação de depuração no último `Release` do dispositivo: superfície estática em memória de sistema no proxy (clipe F11, captura) mantinha referência. Ler contagem com `AddRef`+`Release` em hook `Release` e liberar objetos do proxy com 16 referências ou menos permite ao último `Release` chegar a zero.
- Instaladores até 0.2.2 recusam enquanto qualquer `Jericho.exe` roda no PC (0.2.3+ só na própria pasta): teste de versão antiga junto a teste ativo não instala nada.
- Instalador 0.2.4 publicado para sobre registro 0.2.3 com linha `shortcut=` vazia; 0.2.5+ consegue ler.
- No teste de almas, IA Rawlings no host às vezes não chega ao representante caído em 12 s (1 de 3 com DLL 0.2.5, 2 de 6 com 0.2.6): reanimação não é enviada. A escolha de IA fica no motor; cura original (`WeaponsRawlings.Cure(me, tgt)`: `Team.RevivePlayer`, luz/som, custo de vida Rawlings) pode ser chamada por ele.
- `Team.TravelCam` / `Team.EndTravelCam`: voo de alma na troca depende de `SetTimeSpeed(0.005)`; sem isso, percurso termina no mesmo quadro, e `EndTravelCam` exclui câmera (`cam:Del()` antes de `SetCam(0, MainCam)`) já usada pelo motor naquele quadro: "Check failed: GetActiveCamera() != this" (`ScrapEngCamera.cpp`, linha 48).
- `Scorer.SetMsgText` é linha única para todos; widget "Msg" de cada um a mostra. `Visible` dos itens Scorer aceita 1/0; booleano é ignorado silenciosamente.
- Padrão `R_LimitFPS` é 0 (sem limite); `VSync` é a opção do menu.
- Agrupador 2D desenha quando textura muda, não quando viewport muda: na tela dividida cujo HUD pulava a regra de agrupamento, mensagem de cada jogador era desenhada na outra metade em quadros alternados (parecia piscar em dois estilos).
- Mensagens de estado não confiáveis enviadas antes de trocar fase chegam após carregar a próxima (host descartava uma do cliente em quase todo início). Host retransmite estados a todos, inclusive ao remetente.
- Eventos de aparecer/desaparecer de `PsichicCommander`, `EvilFirstBorn`, `SummerianNANNA` e `SummerianUTU` chamam `oAI:OnAfterAppear/OnAfterDisappear`; chamada define modo da IA (vtable +0x3a4 → `005035f0` com 3) e lê estado que IA desativada não mantém.

## <a id="tools-and-downloads"></a>Ferramentas e downloads
- unluac 2025-12-23, https://sourceforge.net/projects/unluac/files/Unstable/unluac_2025_12_23.jar/download
  SHA-256 `98be0fa84ac73ca66dce2842a2e4512226f4c611b6500dc96415571fc5538fcc`
- pefile (pip) para inspeção PE.
- Zig 0.16.0 (compilador C da DLL proxy de 32 bits), https://ziglang.org/download/0.16.0/zig-x86_64-windows-0.16.0.zip
  SHA-256 `68659eb5f1e4eb1437a722f1dd889c5a322c9954607f5edcf337bc3684a75a7e` (corresponde a index.json de ziglang.org).
- capstone 5.0.3 (pip) para desmontagem.
- Código ENet 1.3.18, https://github.com/lsalzman/enet/archive/refs/tags/v1.3.18.tar.gz
  SHA-256 `28603c895f9ed24a846478180ee72c7376b39b4bb1287b73877e5eae7d96b0dd` (MIT).
- Ghidra 12.1.4 (SHA-256 ddac49f9...d4db, corresponde às notas), Temurin JDK 21.0.12.1+1 (SHA-256 f9d6e191...8b4e, corresponde à API Adoptium).
