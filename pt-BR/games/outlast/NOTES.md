# <a id="outlast-2013-working-notes"></a>Outlast (2013): notas de trabalho

> Onde estão scripts e patches: as pastas `harness/`, `patches/` e `play/` citadas abaixo agora ficam em [`tools/outlast-coop/` do próprio fork https://github.com/G3RKA/OpenOL](https://github.com/G3RKA/OpenOL/tree/main/tools/outlast-coop) (como `harness/`, `relay-patches/`, `exe-patch/`, `play/`), não neste repositório.

Termos: “proprietário” sempre significa o cliente que possui (simula) um inimigo, `OwnerID` do OpenOL; os demais clientes apenas exibem uma marionete dele. Os scripts mencionados (`harness/...`) estão em [harness/](https://github.com/G3RKA/OpenOL/tree/main/tools/outlast-coop/harness/). Capturas e logs brutos das execuções são mantidos privados (capturas da área de trabalho; as regras do repositório proíbem publicá-las); as descobertas estão escritas aqui.

## <a id="phase-0-triage-2026-10-20"></a>Fase 0: triagem (2026-10-20)

### <a id="game-identity-observed-via-mcp-game_identity--detect_engine"></a>Identidade do jogo (observada pelo MCP `game_identity` / `detect_engine`)

| | |
|---|---|
| Loja | Steam, appid 238320 |
| Id de compilação | 576074 |
| Executável principal | `Binaries\Win32\OLGame.exe`, PE32 x86, 26000896 bytes |
| SHA-256 | `fc06a9d562ea41757fa7c95abae67c89fb4f56a9c970122fdef2f15758f2bb0d` |
| Versão do arquivo | 1.0.12046.0 (tabela de strings diz 1, 0, 8767, 0) |
| Timestamp PE | 1398795250 (2014-04-29) |
| Motor | Unreal Engine 3 (evidência: `CookedPCConsole`) |
| DLC | Whistleblower instalado (`OLGame\CookedPCConsoleDLC`) |
| SO | Windows 11 |

- Não estava em DIRECTORY.md nem `games/` no momento deste clone. Busca de issues “outlast” neste repositório: 0 resultados.
  Busca de PRs: não feita (`gh` não instalado).

## <a id="phase-1-research-2026-10-20"></a>Fase 1: pesquisa (2026-10-20)

### <a id="observations"></a>Observações

1. **OpenOL** https://github.com/ShyKiss/OpenOL (autor ShyKiss)
   - Cliente UE3 modificado (`OLGame.exe` reconstruído + `.upk`), instalado sobre uma instalação Steam licenciada.
   - Licença: nenhuma declarada (API GitHub `license: null`).
   - Último push 2026-08-29. Última versão 2.1.0 (2026-08-29): `OpenOL.7z` sha256
     `f15d724124a07cad8a58b0465795d66610ba431608ee65bdf4844667e682dc62`, `OpenOL.zip` sha256
     `b301b267d4c2e26815b6b7f11267ecae493c65db2ad523ab2d23512d9db2d67d` (digests de assets GitHub).
   - Multiplayer beta desde 2.0.1 (2026-08-07). README declara sincronização de portas, gatilhos, inimigos,
     cenas. Notas 2.1.0: pacotes por canais; canais de portas, inimigos, empurrões, mundo, CSA.
   - Hospedagem: Multiplayer -> Start Server (relay embutido, Steam P2P, sala `DEFAULT`), ou
     `OpenOL_Relay` separado UDP 7777, sala `PUBLIC` (repositório ShyKiss/OpenOL-Relay).
   - Autor (issue #6): cliente exige DLC Whistleblower (`CookedPCConsoleDLC/DLC_Intro_Persistent.upk`).
   - Relatos abertos: #7 “Connect does nothing” (2026-09-14), #8 “Invite in Steam and Start
     Server do nothing; F6 relay enables invite but still doesn't join” (2026-09-21). Sem resposta do autor.
2. **Outlast-Together** https://github.com/LucianLandIsBack/Outlast-Together
   - MIT, 5 commits, sem versões; projeto escolar, README diz que não haverá novas atualizações.
   - Pastas `Outlast Networking DLL`, `OutlastNetworkingClient`; o que sincroniza: desconhecido.
3. Steam Workshop “Outlast multiplayer” (316004291) é um mapa Garry's Mod, removido. Não é mod do jogo.
4. Mods Outlast no ModDB / Nexus: apenas modo individual nos resultados da pesquisa.

### <a id="not-yet-searched"></a>Ainda não pesquisado
Reddit, Discord, archive.org, guias Steam, forks/branches OpenOL, repositório OpenOL-Relay.

### <a id="unknowns"></a>Desconhecidos
- (Respondido pelas execuções abaixo: OpenOL MP funciona na compilação 576074 com relay separado; itens sincronizados listados no README.)
- Salvamentos e inventário/baterias: não conferidos.
- Número máximo de jogadores.

## <a id="phase-23-workspace-and-source-reading-2026-10-20"></a>Fase 2-3: workspace e leitura de código (2026-10-20)

- Cópia de teste da instalação Steam feita com robocopy (1345 arquivos, 5,868 GB, 0 falhas).
- `OpenOL.zip` 2.1.0 baixado, SHA-256 correspondeu ao digest do asset GitHub, instalado
  apenas sobre a cópia de teste. Sobrescreve 15 arquivos originais (incluindo `Binaries\Win64\OLGame.exe`,
  `DefaultEngine.ini`, `DefaultGame.ini`, `DefaultUI.ini`, `OLFrontEnd.upk`, localização).
  SHA-256 do `OLGame.exe` modificado (Win64): `2e58afbb1203d04476581f34216428d1dfc96228e5f3df8c6881323c56c93346`.
- Fonte: https://github.com/ShyKiss/OpenOL commit `2ab9ecaa17325c32260aba039e5398d5720f0acc` (2026-08-29).
- UE3 grava configuração em `%USERPROFILE%\Documents\My Games\Outlast\OLGame\Config` mesmo numa instalação
  copiada; o arquivo MP é `OLMultiplayer.ini` ali (`FMpConnection::LoadConfig`).

### <a id="observations-source"></a>Observações (código fonte)
- Botão de host (`OLUIFrontEnd_Multiplayer.uc` `Press_CreateServer`): `NativeStartRelay(port)` e depois
  `NativeConnectLocal(port)`, que fixa a sala `DEFAULT` (`MultiplayerLink.cpp` `GMpConn_ConnectLocal`).
  Depois `open DLC_Intro_Persistent?game=Multiplayer.MultiplayerGame` (mapa Whistleblower, portanto exige DLC).
- Relay embutido cria apenas sala `DEFAULT` (`openol_relay/src/relay_api.c`).
- “Connect” do cliente lê sala de `OLMultiplayer.ini`; `DefaultMultiplayer.ini` da versão traz `RoomCode=PUBLIC`.
- Relay responde `SRV_HELLO_FAIL "unknown room"` a sala desconhecida (`server.c` `handle_hello`).
- Cliente ignora HELLO_FAIL: `MultiplayerController.cpp` `case SRV_HELLO_FAIL: break;`. Nenhuma mensagem ao jogador.
- `DefaultEngine.ini` acrescenta `+SeekFreePackage=OpenOLResources`, mas esse pacote não existe no arquivo da versão. Efeito: desconhecido.

### <a id="test-run-relay-protocol-without-the-game-2026-10-20"></a>Execução de teste: protocolo do relay sem jogo (2026-10-20)
- Fontes do relay embutido compiladas sem alterações com MinGW gcc e um `main` de 15 linhas (`relay_host.c`),
  sondadas por `hello_probe.py` enviando a linha HELLO exata do cliente.
- Resultado: `DEFAULT` -> `READY player_id=1000`; `PUBLIC` -> `HELLO_FAIL unknown room`. 2/2 conforme esperado.

### <a id="derived"></a>Deduzido
- Entrada por IP direto num jogador hospedando com “Start Server” falha silenciosamente a menos que quem entra
  mude o código de sala de `PUBLIC` para `DEFAULT`. Corresponde à issue #7 do OpenOL (“Connect does nothing”). Ainda não
  confirmado no jogo.

### <a id="test-run-modded-game-as-client-launched-from-the-command-line-2026-10-20"></a>Execução de teste: jogo modificado como cliente, iniciado pela linha de comando (2026-10-20)

Inicialização: `Binaries\Win64\OLGame.exe DLC_Intro_Persistent?game=Multiplayer.MultiplayerGame -nostartupmovies -log=mp_a.log`
(log fica em `<game dir>\OLGame\Logs`).

Observado:
1. Com configuração da versão (sala `PUBLIC`, porta 7777, nenhum relay rodando), cliente carrega mapa MP,
   registra `MpConn: Resolving '127.0.0.1':7777 room='PUBLIC'` e `HELLO #1..#46` a cada 2 s para sempre.
   Nada é mostrado ao jogador. (Uma instância, Steam ligado, com foco.)
2. A compilação modificada grava configuração em `<game dir>\OLGame\Config\` (OLEngine.ini, OLMultiplayer.ini, ...),
   NÃO em Documents. `OLMultiplayer.ini` é gerado ali a partir de `DefaultMultiplayer.ini`.
3. Salvamentos e perfil ficam no Steam Cloud: `<steam>\userdata\<id>\238320\remote\` (`*.sav`, `profile.bin`).
   Com Steam ligado, o mod lê esse perfil (`Profile version mismatch (19 != 17)`, depois
   `Setting to defaults`). Risco: pode gravar um `profile.bin` v19 sobre o do jogador. Não observado
   (nenhum arquivo mudou após várias execuções encerradas à força), mas não testado numa saída normal.
4. `-nosteam` funciona: `Steam Client API Disabled!`, `UOLProfileSettings::SetToDefaults()`, nome de usuário `Player`.
   Perfil da nuvem não é usado. Conexão ao relay UDP dispensa Steam.
5. Resolução e tela cheia vêm do perfil (`OLEngine.cpp` por volta da linha 1883 `### Applying resolution`),
   então `-windowed -ResX -ResY` e `Fullscreen=False` em OLSystemSettings.ini são sobrepostos. Perfil padrão é tela cheia.
6. `<game dir>\OLGame\Config\OLEngine.ini` tem `bPauseOnLossOfFocus=TRUE`.
7. **Bloqueio para teste com bot:** com porta 17777 / sala `DEFAULT` apontando ao relay de teste ativo, toda inicialização
   que não obtinha primeiro plano (2 instâncias ou 1 iniciada por shell em segundo plano, com ou sem
   `-nosteam`, com `bPauseOnLossOfFocus=FALSE`) para de registrar logo após `Resizing to WxH (fullscreen)`:
   processo responde, CPU ocupada, nenhum `HELLO` enviado, relay não viu nada.
8. `-EXEC=<file>` resolve para `<game dir>\Binaries\<file>` (`..\..\Binaries\` a partir de Win64). Executa em ~14,1 s,
   ANTES do redimensionamento do perfil em ~14,9 s; portanto `setres 960x540w` nele é sobreposto. Última execução terminou aqui.

Hipóteses (não verificadas):
- Item 7 é D3D9 em tela cheia exclusiva sendo minimizado sem foco, então
  o tick de rede nunca executa. Se verdadeiro, host que usa alt-tab também para de sincronizar.
- Correção para bots: obter modo janela antes de aplicar o perfil, com perfil de tela cheia desligada
  num perfil local `-nosteam`, ou `setres` atrasado (ImGui F6 do OpenOL ou console após carregar).

### <a id="test-run-2-one-client--nosteam-gamma-screen-protocol-2026-10-20-later"></a>Execução de teste 2: um cliente, -nosteam, tela de gama, protocolo (2026-10-20, mais tarde)

Inicialização como antes, com `-nosteam`, sala `DEFAULT`, porta 17777, `harness\relay_host.exe` (fonte do relay embutido).
Entrada por `harness\olwin.py` (foca janela + teclado real por SendInput; jogo ignora
eventos de tecla PostMessage).

Observado:
1. **Item 7 acima foi diagnóstico incorreto.** O log é escrito em blocos grandes atrasados e `relay_host` não imprime
   por pacote, portanto “nenhum HELLO, relay não viu nada” estava errado. Quando o log descarregou: `HELLO #1` em 16,65 s,
   `Connected! PlayerID=1000` em 16,88 s, com janela em tela cheia mostrando calibração de gama.
2. Perfil novo (padrões `-nosteam`) abre a **tela de calibração de gama** sobre o menu principal
   (`OLUIFrontEnd.uc` ~341, `PSI_GammaInitialized`). Teclado: Baixo, Enter aceita.
3. O mapa MP da linha de comando chega ao **menu principal** (`DLC_Intro_Persistent` carrega `dlc_mainmenugame`), HUD MP
   “OpenOL: 1 player” no canto.
4. Options -> Graphics -> FullScreen desligado, Resolution 800x600, Apply: log `Applying resolution 800 x 600
   (Fullscreen: no)`, janela 816x639 e perfil salvo em `<game>\OLGame\SaveData\Player1.olprofile`
   (379 bytes, `[OnlineSubsystemPC] ProfileDataDirectory=../../OLGame/SaveData`). Próximas inicializações `-nosteam` devem
   abrir em janela (ainda não repetido).
5. Console (Til) não abriu no menu principal.
6. **Laço de reconexão:** `Connected!` e depois novo `HELLO` a cada ~30-35 s, PlayerID 1000, 1001, ... 1009.
7. Causa (leitura das duas fontes):
   - Formato do cliente 2.1.0 (`MultiplayerLink.cpp` `FMpConnection::SendBinary`): `[channel][type][player_id LE4][payload]`;
     PING = `[0x00][0x02][id][ms]`. Cliente encerra enlace se nada chega por 30 s (`Tick`, heartbeat).
   - Relay embutido no repositório OpenOL (`Development/External/openol_relay/src/server.c` `handle_packet`) interpreta
     formato ANTIGO `[type][player_id LE4]`: lê id de jogador dos bytes errados, não encontra jogador, descarta todos
     os pacotes binários (sem eco PING, `last_seen` nunca atualizado) e expira o jogador após 30 s (`TIMEOUT_SEC`).
   - Relay separado https://github.com/ShyKiss/OpenOL-Relay em `b9def512` (“Update to 2.1.0”) já tem
     cabeçalho de canal (`/* Client->server 2-byte header: [channel][type][player_id LE4] */`).
   - Nota: mesmo ali, `ENEMY_LOC` é 0x08 no relay mas 0x04 no `PacketChannels.h` do cliente
     (e ENEMY_DOOR_* diferem). Não investigado mais.
8. Ainda desconhecido: se o relay compilado DENTRO do `OLGame.exe` distribuído (Start Server) é a fonte antiga
   (verificação de strings inconclusiva). Se for, hospedar por “Start Server” não sincroniza nada, explicando
   possivelmente a issue #8 OpenOL. Teste: duas instâncias, uma hospedando pelo menu “Start Server”.

Observação adicional: `FMpConnectionTicker::IsTickableWhenPaused()` retorna FALSE (`Multiplayer.h` ~172), então jogo
pausado (menu de pausa, `bPauseOnLossOfFocus`) interrompe HELLO/PING/heartbeat. Ainda não observado como problema.

### <a id="test-run-3-two-clients-on-the-standalone-openol-relay-210-2026-10-20-2330-2347"></a>Execução de teste 3: dois clientes no OpenOL-Relay separado 2.1.0 (2026-10-20, 23:30-23:47)

Preparação: OpenOL-Relay `b9def512` (https://github.com/ShyKiss/OpenOL-Relay), `src/{main.cpp,server.c,cli.c,db.c}`
compilados com MinGW (`gcc -c` nos arquivos C, `g++` main.cpp, `-lws2_32`), executado como
`OpenOL_Relay.exe --port 17777 --name CoopTest`. Cria só sala `PUBLIC` (main.cpp, quando banco não tem
salas); o `OLMultiplayer.ini` de teste recebeu `RoomCode=PUBLIC`. `hello_probe.py`: PUBLIC -> READY,
DEFAULT -> HELLO_FAIL (2/2).
Duas instâncias `-nosteam` da mesma cópia (perfil em janela compartilhado do teste 2), controladas por `olwin.py`.

Observado:
1. **Novo bloqueio de inicialização e correção:** iniciada por shell em segundo plano, janela aparece minimizada e inicialização
   do motor para após `Wwise(R) SDK Version ...` (CPU estável, log vazio, espera >2 min). Minimizar + restaurar janela
   (`olwin.py wake <pid>`) libera imediatamente (lacuna no log 13,5 s -> 88,1 s = tempo até despertar).
2. Relay: `ID=1001 joined room 'PUBLIC' (1 players)`, `ID=1002 joined ... (2 players)`, ambos `identified as 'Player'`;
   nenhum `timed out` no restante da execução (~13 min). Logs clientes: exatamente 1 `HELLO` e 1 `Connected!` cada.
   **Laço de reconexão do teste 2 desapareceu.**
3. Ambos os HUDs: `CoopTest: 2 players`, ping 15-17 ms, lista `Player (You)`, `Player`.
4. Ambos: New Game -> Main -> Normal -> Continue -> carta inicial -> portão do asilo (início da campanha principal). Ambos os logs:
   `KISMET: Remote event Car_Ride activated for 2 recipients`.
5. **Sincronização do herói funciona:** B segurou W por 3 s; janela A mostra modelo de B andando à frente no portão
   (captura mantida localmente).
6. Peculiaridades de menu para bots: na tela de introdução textual, Continue às vezes não tem foco; mover/clicar
   nele dá foco e Enter funciona.

Ainda não testado: portas, inimigos, objetos empurráveis, sincronização de cenas, progresso da história, salvamentos, morte/ressurgimento, dois PCs pela
internet, “Start Server” pelo menu (relay embutido).

### <a id="test-run-4-door-and-enemy-sync-with-bots-2026-10-21-0004-0014"></a>Execução de teste 4: sincronização de portas e inimigos com bots (2026-10-21 00:04-00:14)

Preparação como teste 3, mais proxy de registro entre clientes e relay (`harness/udp_tap.py`, clientes UDP 17778,
relay 17777). Proxy decodifica formato 2.1.0 e grava `state.json` (x/y/z/yaw dos heróis por cliente, portas
por posição, inimigos por nome). Bots: `goto.py` (anda até x,y: mira com movimentos relativos do mouse calibrados pelo
yaw de `state.json`; anda em intervalos <=0,6 s; se moveu <25 unidades, recua e desvia lateralmente alternando lados;
desiste com `BLOCKED` após 5 tentativas; aborta com `STALE` se estado tem >3 s), `turn.py` (giro em malha fechada),
`click.py`, `look.py`, `hold.py`. Ambos carregaram checkpoint `Admin_MainHall` pela sobreposição F6 do OpenOL
(aba Checkpoints).

Observado:
1. **Carregamentos de checkpoints não são sincronizados.** Carregar `Admin_MainHall` em A deixou B nos portões; B também precisou carregar.
2. Ao carregar nível, cada cliente envia `DOOR INIT` de cada porta (47-52 aqui, com x/y/z e ângulo). Relay responde
   com snapshots `DOOR ANGLE`.
3. **Porta A->B funciona:** A fechou a porta aberta em (-8748,-788,0) (jogo pediu “Press LEFT MOUSE BUTTON to close”).
   Proxy: `C>R A DOOR CLOSE` -> `R>C B DOOR CLOSE`. Visão de B: malha da porta fechou o vão, A atrás
   (capturas antes/depois mantidas localmente).
4. **Porta B->A funciona:** B fechou novamente mais tarde; na tela A, a porta estava fechada e o aviso mudou para “open”.
5. Após cada CLOSE/OPEN recebido, receptor envia o mesmo pacote de volta uma vez (eco). Nenhum laço visto (1 eco cada).
6. Porta abriu uma vez sem clique. Cliente A enviou `OPEN` enquanto B passava (00:09:36). Hipótese: modelo
   remoto de B no cliente A empurrou a porta. Não confirmado.
7. **Inimigo A->B funciona para criação e posição:** Soldier criado em A (sobreposição Spawns -> Enemies -> + -> Spawn,
   “Should Attack” desligado, clique esquerdo no jogo para colocar, direito para sair do modo). Proxy: 1 `ENEMY SPAWN
   OLEnemySoldier_0` A->B, depois `ENEMY LOC` 5263 enviados por A / 5263 entregues a B em ~1,5 min. Ambas as telas mostram
   o mesmo inimigo no mesmo lugar perto de A (escuro, captura local).
8. Reiniciar proxy muda endereço do cliente no relay: expira o endereço antigo e os clientes
   repetem HELLO com IDs novos (1001/1002 -> 1003/1004 -> 1005/1006). Voltaram sozinhos em <30 s.
9. Problemas do aparato encontrados e corrigidos: proxy falhava quando bot lia `state.json` durante `os.replace`
   (Windows PermissionError), e bot andava sobre dados antigos. Bot andando reto prendia em móveis e
   no outro jogador.

Ainda não testado: inimigo perseguindo/atacando jogador, IA de inimigo pertencente a B, inimigo morto/removido, trancar/destrancar porta,
objetos empurráveis, cenas, gatilhos de história, morte/ressurgimento, dois PCs.

### <a id="test-run-5-attacking-enemy-damage-death-respawn-2026-10-21-0017-0035"></a>Execução de teste 5: inimigo atacando, dano, morte, ressurgimento (2026-10-21 00:17-00:35)

Preparação como teste 4. Proxy agora decodifica vida do herói (i16 @38) e movimento especial (u8 @30) de `HERO_STATE`,
e modo de inimigo (u8 após yaw/velocidade) de `ENEMY LOC`, registrando cada mudança. `harness/watch.py` grava linha do tempo de 1 s
(hp, movimento especial, posições, distâncias inimigo->herói, indicadores STALE) e uma captura a cada 2 s.
A = proprietário do inimigo (criou Soldier na sobreposição F6, “Should Attack” ligado, sem arma), B = outro cliente.
Ambos no checkpoint `Admin_MainHall`. Para causar mortes, Max Health definido como 40 na sobreposição (aba Player).

Observado:
1. **Inimigo do proprietário ataca os dois jogadores.** IA executa só no cliente A; em B é cópia.
   - B atacado (00:23:15): modo inimigo 0->2, `ENEMY SMT` A->B, `HERO 0x07` (evento de jogador) A->B, hp B 100->49 e
     B empurrado ~250 unidades. Movimento especial próprio de B ficou 0 (sem animação de agarrar nesse golpe).
   - A atacado (00:28:05, novamente 00:28:56): movimento especial A 0->62 (agarrar) -> 67 (arremessar, z=41) -> pousou, hp 100->49.
   - Após a morte de A, o inimigo restante deixou B morto/ressurgido e andou até A
     ((-8649,166) -> (-8732,132)), agarrou A, hp 100->49. Portanto persegue.
   - Um golpe Soldier = 51 de dano. Regeneração cerca de 2 hp/s. Após golpe, inimigo volta ao modo 0 em ~4-12 s.
2. **O que o outro vê:** cópia do inimigo move e reproduz animações de ataque/agarrão/morte na outra
   tela; nome da vítima fica vermelho no HUD do outro enquanto ferida; tela própria da vítima fica vermelha.
   B viu Soldier levantar A na execução; A viu Soldier sobre o corpo de B.
3. **Morte do proprietário (A, 40 hp máximo):** 00:32:03 agarrão 62 -> execução 68 -> hp 40->5->0 (00:32:07).
   00:32:15 A envia `ENEMY DEL` dos próprios inimigos (ambos Soldiers removidos em B também), `LIFECYCLE DIED` e
   `LIFECYCLE RESPAWNED`, ambos entregues a B. A ressurgiu com 100 hp (configuração máxima 40 foi redefinida).
4. **Morte do não proprietário (B, 40 hp máximo):** 00:34:31 dois `HERO 0x07` A->B, movimento especial B 62 -> 68, hp 40->5->0
   (00:34:35). 00:34:43 B envia `DIED` + `RESPAWNED`, entregues a A. B ressurgiu no início do checkpoint
   (-9272,2) com 100 hp. Inimigo de A NÃO foi removido e continuou lutando (atacou A em seguida).
5. Assimetria: morte do proprietário remove seus inimigos para todos; morte de não proprietário não os afeta.

Mudanças do aparato (bots agora conferem estado mais frequentemente e tratam obstáculos):
- `goto.py` decide “preso” pelo progresso até alvo (sem nova melhor distância por 2 intervalos), não distância percorrida.
  Rebater entre dois móveis antes reiniciava o contador para sempre. Desvios crescem (recuar, andar lateralmente
  direita/esquerda 0,4 s * n, avançar); após 6 desvios informa `BLOCKED` com posição e melhor distância.
  Rotas longas usam pontos intermediários.
- `goto.py` para com `HIT` quando hp do herói cai ou movimento especial começa. Antes tratava agarrão e arremesso
  como obstáculo e saía andando.
- `setslider.py` define valores de sliders ImGui (ctrl+clique, digitar).

Ainda não testado: inimigo pertencente a B, dois inimigos com proprietários distintos, armas (Soldier armado, outros tipos),
esconderijos (armários/camas), gatilhos/cenas da história, progresso de checkpoint após morte, dois PCs.

### <a id="test-run-6-enemy-owned-by-b-enemies-of-two-owners-at-once-2026-10-21-0036-0045"></a>Execução de teste 6: inimigo pertencente a B, inimigos de dois proprietários simultâneos (2026-10-21 00:36-00:45)

Preparação como teste 5 (relay, proxy, `watch.py`). Ambos em `Admin_MainHall`. Soldiers criados pela sobreposição F6
com “Should Attack” ligado.

Observado:
1. **Inimigo de B funciona como o de A.** B criou `OLEnemySoldier_0` perto de A: `SPAWN` B->A, atacou A
   imediatamente (hp A 100->49), aparecendo na tela A. Depois atingiu também o proprietário B (hp 100->49).
2. **Dois proprietários ao mesmo tempo:** A criou `OLEnemySoldier_1` com `_0` de B vivo; B depois criou `_2`.
   Proxy recebeu posições dos três dos respectivos proprietários. Os quatro casos funcionaram com inimigos de ambos
   vivos: inimigo de B atingiu A (00:42:27) e B; inimigo de A atingiu B (00:43:3x) e depois A.
3. Inimigos recém-criados atacam imediatamente se jogador está perto do ponto. Caso contrário, ficam no modo 0
   até um jogador chegar a ~100 unidades (não ajustado/medido além disso).
4. **B (não proprietário de `_1`) morto por inimigo de A:** morte de B enviou `DEL` apenas dos próprios `_0` e `_2`.
   `_1` de A ficou, foi até A e também o matou. Morte de A enviou só `DEL _1`. Assim, morte do proprietário remove exatamente
   seus inimigos para todos. Confirma teste 5 e explica sua “assimetria”.
5. **Nomes nunca colidiram.** Cada cliente numera inimigos pelo contador do motor por classe, e a cópia remota
   (“dummy”) do inimigo do outro consome um número no mundo receptor. Assim, próxima criação local recebe
   número novo: A recebeu `_1` após `_0` de B, B recebeu `_2`. Mesmo confirmando ambas as criações com 0,27 s de diferença,
   A recebeu `_3` e B `_5`.
6. Leitura de código: cliente busca inimigos remotos por (nome, id do proprietário) (`EnemyChannel.cpp` `ApplySpawn`,
   `ApplyDel`, `ApplySmt`), então nomes iguais com proprietários distintos seriam seguros nos clientes. Tabela de snapshots
   do relay para entradas tardias usa só (sala, nome) (`server.c` `enemy_find/enemy_alloc/enemy_remove`). Dois proprietários
   com o mesmo nome se sobrescreveriam ali. Não observado (veja 5). Relay também nunca armazena snapshots
   `ENEMY_LOC` porque seu `ENEMY_LOC` é 0x08 e cliente envia 0x04 (teste 2 item 7); quem entrasse tarde receberia
   criação + SMT, mas não posição atual.

Não testado: entrada tardia com inimigos vivos (caminho de snapshots do relay), inimigos da história/nível (criados pelo mapa
nos dois clientes ao mesmo tempo), armas, outros tipos, dois PCs.

### <a id="test-run-7-story-sync-with-a-scripted-fake-peer-2026-10-21-0047-0103"></a>Execução de teste 7: sincronização da história com par simulado por script (2026-10-21 00:47-01:03)

Mudança de método (andar com bot para encontrar gatilhos era lento demais):
`harness/fake_peer.py` entra na sala como terceiro jogador (HELLO textual, apelido binário `SRV_HELLO`, `SRV_PING`
a cada 5 s) e injeta pacotes `WORLD_TRIGGER_ACT`. Seu modo `sweep` envia
`<level>.TheWorld:PersistentLevel.Main_Sequence.SeqEvent_Touch_N` para N num intervalo, um a cada 3 s, e relaciona
o log do receptor (tempo do jogo + hora de “Log file open”) a cada envio. Os dois clientes reais são receptores.
Receptor registra `[TA] ForceActivateTouchEvent: <name> ... MaxTriggerCount=..` (OLPlayerController.cpp ~1773),
`KISMET: Remote event <name>`, `--- SAVING CHECKPOINT "<name>" ---`, `GS - Applying checkpoint <name>`.
Nomes de níveis vêm de caminhos de gatilhos vistos pelo proxy e nomes de arquivos `CookedPCConsole` (em minúsculas).
Proxy agora decodifica pacotes WORLD (caminho de gatilho, caminho/posição/taxa de matinee).

**Exigiu `-FORCELOGFLUSH`:** sem isso, log cliente chegava ao disco ~3+ min atrasado e a primeira varredura não
correspondeu a nada.

Observado:
1. Ao iniciar, cada cliente toca `asylum_exterior-ld...SeqEvent_Touch_4`; envia `TRIGGER_ACT` e o
   outro recebe. Estado matinee (`SeqAct_Interp_0`, taxa 1,0) enviado nos dois sentidos.
2. **Carregamentos de checkpoint não sincronizam e gatilhos são aplicados fora de contexto.** Ao carregar `Admin_Explosion`
   em A (sobreposição F6), seus toques de gatilhos `center_block_explosionroom-art`/`floors_snd` chegaram a B, ainda nos
   portões. Log B: `[TA] ForceActivateTouchEvent: SeqEvent_Touch_0/3/7 ...`. Objetos existem em B (mesmo
   mapa persistente `adminblock_persistent`), então B executou eventos de história de outra sala.
3. **Varredura de Touch_0..30 de `center_block_sript` com ambos em `Admin_Explosion`:** 13 gatilhos existiam e foram
   forçados em AMBOS, na mesma ordem. Eventos vistos nos dois: `Patient_Running_After_AirVent`
   (Touch_2), `SOLDIER_MEZZANINE_GRAB` (Touch_8, mais aviso “SeqAct_Interp_10 has no groups that reference
   connected Actor 'MultiplayerController_0'”), `SwapWindowsEntrance` (Touch_9), depois `WheelchairReady`,
   `PriestDone` e **`SAVING CHECKPOINT "Admin_MainHall"` nos dois** (perto de Touch_23..25).
   Assim, gatilho de um jogador avança história e checkpoint de AMBOS. Ficaram onde estavam
   (sem teleporte), ou seja, história avançou sem eles. Salvamentos ficaram em
   `OLGame\SaveData\OL_<date>.sav` da cópia de teste (-nosteam); Steam Cloud inalterado.
4. Varredura Touch_0..30 de `center_block_basement-ld` em `Admin_Electricity`: 8 gatilhos ativados no receptor,
   nenhum evento remoto Kismet, nenhum inimigo.
5. **Inimigos do mapa são duplicados.** Ambos carregaram `Prison_IsolationCells02_Soldier`. A primeiro, enviando
   `SPAWN OLEnemyGenericPatient_0`. B carregou 14 s depois, enviando `SPAWN OLEnemyGenericPatient_1` (sua própria cópia IA
   do mesmo paciente; número mudou porque dummy de A ocupou `_0` no mundo B). Ambos enviavam LOC do
   mesmo ponto (2734,1166,1351), modo 0. Deduzido do código (`EnemyChannel.cpp` TickSend envia cada
   `AOLEnemyPawn` local; `ApplySpawn` cria dummy por (nome, proprietário)): cada cliente tem seu paciente IA e
   um dummy do outro no mesmo lugar. Não conferido na tela (paciente a ~3000 unidades).
   Relay também reenviou `SPAWN _0` de A a B no carregamento do nível de B (snapshot do relay).
6. Nenhum Soldier (apesar do nome do checkpoint) existia no mundo ao carregar; deve aparecer depois por script.

Não testado: sincronização de início/parada de cena (matinee) com ambos assistindo, mesmo gatilho tocado pelos dois simultaneamente,
tratamento MaxTriggerCount (contagem enviada como 0 pelo par simulado), matar/remover inimigo duplicado do mapa, dois PCs.

### <a id="test-run-8-duplicated-map-enemy-on-screen-who-it-attacks-2026-10-21-0106-0126"></a>Execução de teste 8: inimigo duplicado na tela, quem ataca (2026-10-21 01:06-01:26)

Para reduzir caminhada e menus manuais, novo driver de comando único `harness/ol.py` (detalhes na docstring):
`up` (relay + proxy, desacoplados, sonda HELLO), `launch N <map>` (clientes diretamente no mapa por URL, sem menus;
espera linha Wwise do log, desperta janela, repete; organiza janelas; relaciona cliente à sua porta do proxy),
`cp <idx> <name>` / `cpall <name>` (carrega checkpoint pela sobreposição F6: aba Checkpoints, busca, Ctrl+A+Delete,
digita nome completo, clica resultado único), `survey <idx> <cp...>` (posição inicial do herói e inimigos por checkpoint),
`status`, `down`. URL de mapa sozinha não escolhe checkpoint (`prison_persistent#<cp>` carrega mapa na posição
inicial padrão; fonte não tem opção URL para checkpoints).

Observado:
1. Levantamento dos 13 checkpoints Prison (`survey_prison_checkpoints.log`): posições iniciais fixas por checkpoint. Só
   `Prison_OldCells_PreStruggle2` inicia no piso do paciente, perto dele: herói (2902,225,1348), paciente
   `OLEnemyGenericPatient` em (2734,1166,1351), a 956 unidades. Ambos surgem exatamente no mesmo ponto.
2. Início novo, ambos `cpall Prison_OldCells_PreStruggle2`: proxy mostra DOIS pacientes no mesmo ponto,
   `_0` de A e `_1` de B, ambos modo 0.
3. A andou até paciente (`goto.py`, sem menu). Na tela (quadro clareado 01:24:14, mantido em `evidence`): **A vê dois
   pacientes sobre ele simultaneamente; B, ainda na posição inicial, vê duas silhuetas lado a lado no corredor.**
4. **Quem ataca quem:** cada paciente ataca o jogador próximo; ambas as cópias atacam a mesma vítima.
   A recebeu golpes de `_1` (cópia B: `HERO 0x07` enviado por B a A, 01:24:18 e :22) e de `_0` (sua própria
   cópia, 01:24:20 e :23): hp 100->70->...->10, depois agarrão (movimento especial 69) e morte 01:24:28. Assim, dano
   foi cerca do dobro de um inimigo.
5. Após morte de A, cópia de B andou até B (2903,233), matando-o em 01:24:47 do mesmo modo.
6. Na morte de A: `ENEMY DEL _0` (própria cópia removida), `DIED`+`RESPAWNED`; relay reproduziu `SPAWN _1` de B a A duas vezes e
   o checkpoint recarregado de A criou novo `_2`. Após ressurgir, mapa tem novamente uma cópia local e a do outro
   jogador.
7. Alvo de acompanhamento da cabeça em `ENEMY LOC` difere entre cópias (cada uma olha ao jogador considerado
   mais próximo), consistente com duas IAs escolhendo alvos independentemente.

Não testado: o que ocorre quando só um cliente carregou o inimigo, se matar uma cópia remove a outra,
outros tipos de inimigo, dois PCs.

### <a id="test-run-9-first-assert-based-suite-2026-10-21-1640-1710"></a>Execução de teste 9: primeira suíte com asserções (2026-10-21 16:40-17:10)

`harness/suite.py` (tabela README). Primeiras execuções encontraram: (1) erro do avaliador: log relay mostra primeiro id (sonda HELLO de `ol.py up`)
expirando após 30 s porque nunca envia ping; contado como expiração real, corrigido e coberto por autoteste do avaliador (S0).
(2) **Falha:** iniciar cliente em `adminblock_persistent` e depois carregar `Admin_Explosion` terminou em caixa de erro Windows
`Assertion failed: Sequence != RootSequence [UnWorld.cpp:1693] SubLevel is streaming in its parent`; log silencia. Execuções manuais anteriores
chegaram ao bloco administrativo só por outros mapas. Suíte agora inicia em `prison_persistent` e salta por checkpoint; toda
asserção verifica diálogos de falha. Duas execuções completas: 7 PASS, 2 XFAIL (A4 inimigo do mapa enviado pelos dois, B3 gatilho de outro
nível dispara nos dois), 365 s cada, estáveis.

### <a id="test-run-10-suite-extended-to-doors-and-player-spawned-enemies-2026-10-21-1700-1810"></a>Execução de teste 10: suíte ampliada para portas e inimigos criados pelo jogador (2026-10-21 17:00-18:10)

Incluídos: injeção de porta (`fake_peer.py door`), testes A6/A7, grupo C (C0..C6), `ol.py maxhp/spawn/nudge/level`, pitch do herói no estado do proxy.
O que primeiras execuções C mostraram (tudo tratado na suíte, nenhum erro OpenOL salvo indicação):
1. Console da sobreposição não tem linha de entrada visível em janela 800x600 e digitar às cegas nada fez; `KillPlayer` não pôde ser usado. Morte
   vem do inimigo e Max Health 40 nos dois jogadores (golpe de 51 mata).
2. Posicionamento de criação segue mira: visão nivelada põe fantasma a 1100 unidades atrás de parede; olhar totalmente para baixo o põe
   nos pés. Restaurar visão ultrapassa o ponto; câmera é nivelada em malha fechada pelo pitch decodificado do proxy (bytes 18-19 HERO_STATE).
3. Soldier criado dentro da cela acolchoada inicial `Prison_Start` nunca atacou (sem caminho?); em `Admin_MainHall`, sim.
4. Inimigo parado a 70-270 unidades de jogador imóvel não ataca; breve passo muda para modo 2 (cerca de 77-190 unidades).
   Após ataque volta ao modo 0 em segundos e exige novo movimento dos jogadores.
5. Morte do proprietário exclui seu inimigo (DEL, retransmitido); morte de não proprietário o mantém até proprietário morrer (C5, C6 observados).
Duas execuções completas: 16 PASS, 2 XFAIL, 562 s e 601 s.

### <a id="build-check-of-openol-2026-10-21"></a>Verificação de compilação OpenOL (2026-10-21)

Lidos `docs/BUILD.md`, workflow CI, receita de contêiner OpenOL (commit 2ab9ecaa) e toolchain local.
1. Repositório tem só arquivos alterados pelo OpenOL: `Development` 25 MB, `OLGame` 8 MB, `Binaries` 3,6 MB. Compilação documentada exige árvore fonte Outlast
   completa (cerca de 36 GB: `Binaries` 5 GB, `Development/External` 30 GB, `Development/Src` 8,6 GB, `Engine`, `OLGame` 22,6 GB), que
   os documentos dizem não fornecer (“We won't be providing any links to the Outlast source here”), mais Visual Studio 2012 e DirectX SDK June 2010
   (Windows, `DXSDK_DIR`), ou Wine 11 e os mesmos em Linux. Nada disso no PC de teste (sem VS 2012, DXSDK, `cl`/`msbuild`).
2. Consequência: código nativo causador dos XFAILs abertos (`EnemyChannel.cpp`, `WorldChannel.cpp`) não pode ser reconstruído aqui, e não procuraremos a
   fonte proprietária. Pode ser compilado sem ela: relay separado (feito, MinGW) e ferramentas sem UnrealScript.
3. Opções em `OLMultiplayer.ini` dispensam reconstrução: `SyncEnemies`, `SyncMatinees`, `SyncInteractable`, `SyncPickups` (todas `True`
   por padrão; lidas em `FMpConnection::LoadConfig`). `SyncMatinees=False` impede cliente de enviar gatilhos; `SyncEnemies=False` impede envio e
   recebimento de pacotes inimigos. São liga/desliga, não propriedade; não corrigem duplicação ou gatilhos fora de contexto; não testadas.
4. Caminho para A4 (um proprietário por inimigo de mapa) e B3 (contexto de área para gatilhos): alteração fonte por alguém com fonte completa; patch do executável distribuído (feito depois, teste 21);
   ou filtro no relay (limitado: relay não distingue inimigo de mapa de criado na sobreposição, só vê nomes e posições).

### <a id="test-run-11-relay-side-trigger-filter-2026-10-21-1920-2015"></a>Execução de teste 11: filtro de gatilhos no relay (2026-10-21 19:20-20:15)

Como correções nativas não podem ser compiladas (veja verificação), problema de gatilhos abordado no relay aberto. Patch
`patches/0001-openol-relay-trigger-radius.patch` (contra OpenOL-Relay `b9def512`, aplicação simulada em fontes intactas): `--trigger-radius <units>`; relay
mantém último `HERO_STATE` de cada jogador e encaminha `WORLD_TRIGGER_ACT`/`WORLD_TRIGGER_FIRE` só a jogadores no raio do remetente (posição desconhecida: encaminhar).
1. `relay_filter_test.py` (sem jogo): T1 pares próximos e de posição desconhecida recebem gatilho, distante não; T2 desligado = todos; T3 pacotes de porta não são
   filtrados; T4 relay upstream viola T1 (variante); T5 remetente sem posição alcança todos. 5 de 5.
2. No jogo (`suite.py B`, raio 3000, um par por script): gatilho enviado por par a 50000 unidades ignorado por ambos os reais (B3 PASS); mesmo gatilho de par
   na posição dos jogadores dispara nos dois (B4 PASS). No relay upstream, B3 dispara nos dois (XFAIL), portanto teste pode falhar.
3. **Erro de teste encontrado pela variante:** primeira versão B3 usava gatilho de uso único (`MaxTriggerCount=1`) depois de B4 esgotá-lo, então “passava” também no upstream. Agora B3 usa
   gatilho repetível (`center_block_sript` Touch_3), executa primeiro e espera cadeia Kismet anterior.
4. Suíte completa: 18 PASS, 1 XFAIL (A4), 618 s.
Limites: distância é heurística de “mesma área” (pisos verticais, salas grandes), jogador distante perde gatilhos até reencontrar, checkpoints continuam sem sincronização, inimigos sem filtro.

### <a id="test-run-12-relay-side-enemy-dedupe-rejected-syncenemiesfalse-measured-2026-10-21-2000-2040"></a>Execução de teste 12: deduplicação de inimigos no relay rejeitada, SyncEnemies=False medido (2026-10-21 20:00-20:40)

1. **Filtro de inimigos de mapa duplicados no relay pioraria tudo.** Dano de uma cópia vem do cliente que a executa: no teste de paciente duplicado
   (teste 8), `HERO 0x07` de B segue imediatamente mudança de modo 0->2 da própria cópia B (`HeroChannel.cpp` `SendPlayerHit`). Esconder a cópia do
   outro jogador no relay deixaria atacante invisível que ainda o fere, pois IA continua executando no cliente.
2. **`SyncEnemies=False` (configuração, sem recompilar) nos dois, grupo D:** nenhum pacote `ENEMY` cruza relay (D1), Soldier criado num cliente não é espelhado (D3),
   outro não sofre dano dele (D4), inimigo ataca no próprio cliente (D5: `SMT_AttackGrab`/`SMT_KillHero` no log).
3. Surpresas: com `SyncEnemies=False`, ataque local não mudou estado do herói de A (sem mudança de hp/movimento especial no proxy, sem morte), embora
   log mostre agarrão e execução; provavelmente mira dummy de jogador remoto B no mesmo lugar; eventos `HERO 0x07` (visuais de agarrão/execução)
   ainda enviados por A e retransmitidos a B (4 em 90 s), mas B os ignorou (hp igual). `SendPlayerHit` depende de `SyncEnemies`, outros eventos de jogador não.
   Não conferido: alvo com jogadores separados.
4. Notas: D3 a D5 executam em `Admin_MainHall`, pois Soldier não ataca nos corredores da prisão (como `Prison_Start`); D5 impede aprovações vazias de D3/D4.
   A, B, C completos: 18 PASS, 1 XFAIL (A4); D: 7 PASS.

### <a id="test-run-13-relay-enemy-packet-ids-2026-10-21-2045-2110"></a>Execução de teste 13: ids de pacotes inimigos no relay (2026-10-21 20:45-21:10)

Teste sem jogo com pares simulados (`relay_filter_test.py` T6/T7): proprietário envia `ENEMY SPAWN` (1) e `LOC` (4, como cliente 2.1.0); entrada tardia envia
`WORLD_REQUEST_ENEMIES` (0x0A). Relay upstream: recebe só `SPAWN` (T7 mostra `LOC` ausente), porque relay armazena `ENEMY_LOC` = 0x08. Com patch
(`0002`): `SPAWN` e `LOC` (T6). Relay não usa `ENEMY_LOC` em outro lugar, nem ids de portas deslocados; mudança local. Patches divididos em
`0001` (raio de gatilho) e `0002` (ids); aplicados na ordem às fontes intactas `b9def512`, reproduzem árvore corrigida byte a byte.
No jogo o efeito é pequeno: proprietário envia `ENEMY_LOC` continuamente, portanto entrada tardia recebe posições num instante; nenhum teste de jogo incluído.
Nota de ferramentas: em Windows, escrita Python em modo texto tornou `server.c` CRLF e primeiro patch tinha 2900 linhas; agora gerados de arquivos LF.

### <a id="test-run-14-relay-shared-state-tests-without-the-game-2026-10-22"></a>Execução de teste 14: estado compartilhado do relay sem jogo (2026-10-22)

`relay_state_test.py` (pares simulados): S1 segundo `DOOR_LOCK` numa porta trancada recebe pacote servidor `SRV_DOOR_DENY` (0xE4), trava não retransmitida (primeira versão do
teste procurava tipo 8 no canal de portas e falhou: erro do teste, não relay); S2 trava permitida após proprietário destrancar; S3 primeira escrita `DOOR_INIT` vence, nunca retransmitida, reproduzida
a entrada tardia como `DOOR_ANGLE` com primeiro ângulo; S4 `DOOR_OPEN` ao vivo e no snapshot tardio; S5 segundo empurrador recebe `PUSH_DENIED`, proprietário não perturbado; S6 empurrão permitido após liberar; S7 `PUSH_INIT`
nunca retransmitido, snapshot mantém primeira posição com `bPushing` limpo; S8 variante: relay espelho cego falha S1. 8 de 8 no corrigido e upstream (comportamento upstream). Incluído na suíte como grupo P com T1-T7
(64 s, 15 verificações + autoteste). No jogo, caminhos de objetos empurráveis e trancas ainda não testados (nenhum objeto movido por cliente nas execuções).

### <a id="test-run-15-pushable-objects-in-game-2026-10-22"></a>Execução de teste 15: objetos empurráveis no jogo (2026-10-22)

`pushsurvey.py` (um cliente, carregar cada checkpoint, contar `PUSH_INIT` enviados) em 25 checkpoints: objetos só anunciados no grupo male ward (`Male_Start`: 2 em
(-3626,-7763,1000) e (-3799,-11516,1000), posteriores 3 a 4, `Male_Cafeteria` 1); nenhum em Admin, Prison, Courtyard, Sewer_start, Revisit, Lab. Nomes com `_Doc_`/`_RM_` são notas/gravações, não checkpoints
(`cp` expira em 90 s); nomes reais vêm da aba Checkpoints (`Male_Start`, `Male_Chase`, `Male_Torture`, `Male_Elevator`, `Male_Priest`, `Male_Cafeteria`, `Sewer_ToMaleWard`, `Courtyard_FemaleWard`...).
Proxy agora decodifica `PUSH` (chave, deslocamento, empurrando). Par por script (`fake_peer.py push`) enviou `PUSH_STATE` crescente e pacote de parada ao objeto a 764 unidades dos heróis: relay encaminhou aos dois reais
(`R>C` às duas portas), mas nenhum deslocamento visível na janela voltada a ele (quadros antes/depois iguais salvo oscilação de luz), portanto aplicação do empurrão remoto é **não verificada** (código receptor limita
ou ignora? desconhecido; sem log). Segunda falha da mesma asserção do motor (`UnWorld.cpp:1693`, “Sublevel is streaming in its parent”) ao saltar por checkpoint de `Lab_Soldierdead` a `Prison_Start`.
Objetos só anunciados após alguns carregamentos dentro do mapa male, não na primeira carga de outro mapa (não entendido).

### <a id="test-run-16-the-embedded-relay-of-the-shipped-olgameexe-start-server-2026-10-22"></a>Execução de teste 16: relay embutido no OLGame.exe distribuído (“Start Server”) (2026-10-22)

Aba Relay da sobreposição (F6) inicia o mesmo relay do menu Multiplayer (`GRelayThread.StartRelay`): campos porta (padrão 7777), nome, caminho DB, botão Start Relay; log mostrado ali.
Preparação: apenas proxy de registro (UDP 17778 -> 17780), cliente A em `prison_persistent` com `RoomCode=DEFAULT` (relay embutido só tem `DEFAULT`), Start Relay na porta 17780, depois B.
1. **Relay embutido distribuído fala formato 2.1.0.** A entrou (`ID=1000`, identificado), conectado por mais de 70 s com um `Connected!`, sem timeout; B entrou, ambos transmitiram estado
   recente por mais 40 s, sem reconexões. Laço do teste 2 é propriedade da *cópia fonte do relay embutido no repositório*, não do relay do executável distribuído (compilado
   de cópia mais nova). Problema 1 do README restrito à cópia fonte.
2. **Relay embutido distribuído também tem problema de id `ENEMY_LOC`** (pares simulados sem jogo, porta 17780, sala `DEFAULT`): snapshot tardio tem `SPAWN` (1), mas não `LOC` (4).
   Patch relay 0002 importa para hosts “Start Server”, mas não podem aplicá-lo sem reconstruir; relay separado pode.
3. Início na sobreposição dispensou Steam. Botão Multiplayer (`Press_CreateServer` = StartRelay + ConnectLocal + open map) e convite Steam não clicados; issues upstream #7/#8 podem tratar disso ou Steam.
   Preparação deixou arquivos estilo `relay_db.json` só na cópia de teste.

Grupo E automatiza teste 16: `suite.py E` (196 s): E1 a E4 PASS, E5 (posição inimiga no snapshot tardio do relay distribuído) XFAIL. Nota de menu: principal ignora cliques e seu
foco de teclado é ambíguo após diálogos (Baixo+Enter chegou a Options, depois New Game, depois Difficulty), então testes por menu não tentados; sobreposição é confiável para iniciar.

Repetição da falha (2026-10-22): carregar `Lab_Soldierdead` e depois `Prison_Start` pela sobreposição num cliente falhou com `Assertion failed: Sequence != RootSequence [UnWorld.cpp:1693]` (“Sublevel is streaming in its parent”) na primeira
tentativa, novamente na segunda sessão: determinístico para esse salto (outros saltos entre mapas tentados, Prison <-> Admin <-> Male, sem falha). Mapa inicial `adminblock_persistent` falha igual. É asserção do motor original
no carregamento de subníveis, alcançada pelos saltos de checkpoint da sobreposição (`StartNewGameAtCheckpoint`); não demonstrada relação com multiplayer (todos rodam `MultiplayerGame`; modo individual não tentado).

Grupo F (entrada tardia real, `suite.py F`, 169 s): A carrega `Admin_MainHall`, cria Soldier calmo (Should Attack desligado; caso contrário mata proprietário e
se exclui), depois B iniciado e carrega mesmo checkpoint: recebe `SPAWN` (F1), posição (F2, fluxo `LOC` contínuo do proprietário, ocultando problema de id `ENEMY_LOC`), transmite estado (F3), A mantém conexão inicial (F4). Todos PASS.

Sincronização de cenas, tentada e descartada (2026-10-22): verificação “gatilho injetado inicia cena nos dois” falhou (0 de 2 relataram novo matinee), pois premissa errada.
Pacotes `MATINEE_STATE` listam matinees com posição e taxa, enviados por cliente ao carregar conteúdo de nível (primeiro relato do proxy para cada caminho coincide com
carregamentos de checkpoint/nível: `asylum_exterior-art Interp_0`, `center_block_explosionroom-art Interp_1`, `prison_01-ld Interp_27`...), não quando gatilho inicia um; `Touch_4` disparou (`ForceActivateTouchEvent`), mas
nada visível iniciou nesse contexto. Receptores aplicam posição informada só se matinee não está rodando localmente (`WorldChannel.cpp`). Testar sincronização exige cena real
e oráculo visual ou de estado; não feito. Verificação falha removida de `suite.py` em vez de mantida como XFAIL vazio.

Verificação README de compilação (2026-10-22): cópia nova de `OpenOL-Relay` `b9def512/src`, ambos patches na ordem (`patch -p1 -d src`), compilada exatamente como README
(`gcc -O2 -c server.c cli.c db.c`, `g++ ... -lws2_32`), reproduz árvore corrigida byte a byte; `relay_filter_test.py` 7/7 e `relay_state_test.py` 8/8 nesse binário.

### <a id="open-hypothesis-2026-10-22-unverified"></a>Hipótese aberta (2026-10-22, não verificada)

Inimigos de mapa duplicados (A4, teste 8) talvez ocorram só após carregar checkpoint pela sobreposição F6 (`StartNewGameAtCheckpoint`: `ClearAllProgress`,
`SaveCheckpoint`, `RestartPlayer` em cada cliente), não no progresso normal. Toda evidência de duplicação até agora vem da sobreposição. Não
refutado: gatilhos sincronizam, ambos executariam mesmo Kismet e criariam cópia própria; tampouco confirmado. Varredura do teste 7 não criou inimigo,
portanto não decide. Raciocínio (deduzido, não testado): início simples de mapa (`prison_persistent` por URL) não criou paciente até aplicar checkpoint; inimigos vêm de subníveis
carregados por cliente; jogadores juntos carregariam mesmo subnível nos dois e receberiam uma cópia cada, enquanto jogador distante talvez nunca carregue (sem duplicata). Hipótese só plausível para
jogadores separados. Teste: jogar ambos de New Game até primeiro inimigo do mapa sem sobreposição, procurando dois `ENEMY SPAWN` da mesma classe no mesmo ponto.

### <a id="derived-1"></a>Deduzido
- Sincronização da história OpenOL 2.1.0 = “qualquer gatilho tocado por qualquer pessoa dispara para todos, onde estiverem”. Serve quando
  ficam juntos; falha com um em outra área ou checkpoint. Inimigos do mapa não
  têm um proprietário único; cada cliente simula e transmite sua cópia.
- Relay separado 2.1.0 é servidor funcional para clientes OpenOL 2.1.0; fontes do relay embutido no repositório
  OpenOL não são (protocolo incompatível, teste 2).

### <a id="next-steps"></a>Próximos passos
1. Testar “Start Server” do menu (relay no executável distribuído) igual. Se houver laço, corrigir reconstruindo
   relay embutido de `server.c` OpenOL-Relay ou hospedar separado.
2. Verificações de bots abertas: gatilhos/cenas, sincronização de checkpoint/nível, inimigo pertencente a B,
   esconder de inimigo, estado do nível (portas, inimigos) após recarregar por morte.
3. Teste com duas pessoas em dois PCs só após bots: host roda OpenOL_Relay com UDP 7777 redirecionado,
   outro configura IP/porta/sala `PUBLIC` em Multiplayer.
4. Relato upstream cobriria (nenhum enviado): sala `PUBLIC` vs `DEFAULT`, HELLO_FAIL silencioso, protocolo do relay embutido
   incompatível, ids ENEMY_* incompatíveis, parada de inicialização com janela minimizada.
5. Não feito neste ponto: `gh` (não instalado), issue de reivindicação, fork/PR (feito depois: issue #133, fork, PR deste texto).

### <a id="tentative-path"></a>Caminho provisório
Retomar/ampliar OpenOL (playbook/reviving-abandoned-mods.md): recente, tem camada de rede
funcional e versão publicada; testar primeiro com duas instâncias locais, sem pessoas.

### <a id="test-run-17-2026-10-22-guide-dry-run-over-the-lan-address"></a>Execução de teste 17 (2026-10-22): ensaio do guia pelo endereço LAN
Relay iniciado conforme guia (`OpenOL_Relay.exe --port 7777`, vínculo padrão `0.0.0.0:7777`, sala `PUBLIC`); um cliente com `IP=<this PC's LAN address>` e `UdpPort=7777` (ini restaurado depois) registrou `Connected!` e relay `joined room 'PUBLIC'`. Script: `harness/lan_dryrun.py`. Nenhum aviso de firewall neste PC. Não é teste de dois PCs ou internet: tráfego não saiu da máquina.

### <a id="test-run-18-2026-10-22-late-join-snapshots-of-the-standalone-relay"></a>Execução de teste 18 (2026-10-22): snapshots tardios do relay separado
Novos testes sem jogo `relay_state_test.py` S9 a S13 (estado de itens coletáveis e caminho Kismet, matinee e herói, jogador que saiu, variante espelho cego). No upstream e no compilado com patches 0001/0002, entrada tardia só recebeu contagem online. Compilação de depuração (`fprintf` em `send_snapshots_to_newcomer` e `server_drain_snaps`) mostrou snapshot enfileirado sem drenagem: laço CLI de `main.cpp` não chama `server_drain_snaps`. Patch 0003 acrescenta chamada; testes passam (15 de 15) e falham no upstream (3 falhas esperadas, XFAIL). Não verificado no jogo: efeito em itens coletados. Relay dentro do executável distribuído envia fila (E6: entrada tardia recebe estado do item sem pedir); erro só no relay CLI separado.

### <a id="observation-2026-10-22-the-f6-overlay-cannot-spawn-items"></a>Observação (2026-10-22): sobreposição F6 não cria itens
Aba Spawns lista uma categoria, Enemies. Não há como criar item coletável pela sobreposição, então sincronização no jogo segue coberta só pelos testes de protocolo (`relay_state_test.py` S9 a S13, E6).
Aba Actions tem só formulário de ajuste DummyHead; Scene é navegador UObject (88144 objetos, busca), sem controle visto para conceder item.

### <a id="play-kit-2026-10-22"></a>Kit para jogar (2026-10-22)
`play/host.ps1` e `play/join.ps1` (veja `play/README.md`) automatizam etapas de hospedar e entrar do guia. Testados num PC numa pasta descartável: reescrita de ini com backup (ini existente e ausente), guarda `steamapps` e `host.ps1` iniciando relay corrigido (porta UDP vinculada, lista de endereços impressa). Dois PCs não testados.

### <a id="test-run-19-2026-10-22-the-real-player-path-no-overlay-and-no-map-url"></a>Execução de teste 19 (2026-10-22): caminho real do jogador, sem sobreposição nem URL de mapa
Preparação: relay (patches 0001 a 0003, `--trigger-radius 3000`) e proxy de registro; ini escrito por `play/join.ps1`; dois clientes iniciados no menu principal (`harness/ol_menu.py`).
Observações:
1. `join.ps1` encontrou `OLGame.exe` igual ao hash conhecido OpenOL 2.1.0 (sem aviso). Diálogo Multiplayer exibiu exatamente valores gravados (nome, IP, porta, sala, quatro indicadores Sync).
2. Menu > Multiplayer > Connect conectou ambos (`MpConn: Connected! ... room='PUBLIC'`; HUD mostra `CoopTest: 2 players` e ping). Lista do menu aceita teclado no principal e diálogos, mas botões do diálogo Multiplayer exigem cursor (virtual): só movimentos relativos do mouse.
3. New Game > Main > Normal nos dois: ambos iniciaram em `StartGame` no carro. Matinee do trajeto (`SeqAct_Interp_3`) cruzou relay nos dois sentidos (proxy), log mostra `KISMET: Remote event Car_Ride activated for 2 recipients`, depois `CarRideDone` e checkpoint `Admin_Gates` salvo sozinho; ambos ganharam controle no mesmo lugar. Uma nota de e-mail aparece primeiro; Enter fecha.
4. Parceiro visível no mundo (modelo Miles do outro cliente, visto na tela do primeiro).
5. Movimento com entrada real funciona (cerca de 130 unidades/s andando; yaw do proxy permite script girar até orientação absoluta).
Não alcançado: qualquer inimigo do mapa. Caminho do portão ao edifício exige etapas encontradas olhando a tela; script às cegas não encontrou em cerca de vinte tentativas, portanto verificação de progresso natural para inimigos duplicados (hipótese acima) permanece aberta.

### <a id="test-run-20-2026-10-22-f6-overlay-as-a-test-aid-and-the-vpn-adapter-dry-run"></a>Execução de teste 20 (2026-10-22): sobreposição F6 como auxílio de teste e ensaio do adaptador VPN
Abas vistas na tela (imagens só da janela): Player tem Fully Ghost (sem colisão, herói voa na direção da visão), Bunny Hop, Unlimited Batteries, Free Camera, God e Max Health;
Visuals tem indicadores de exibição e FreeCam Inspector; Checkpoints lista grupos da história (StartGame, Admin, Prison, Sewer, Male, Courtyard, Female, Revisit, Lab) e DLC; faixa Console no rodapé de Player/Visuals só
visível com janela maior que 800x600 (redimensionável pelo mouse ou script, viewport acompanha): `ToggleUnlit` digitado ali mudou visão para sem iluminação.
Fully Ghost levou cliente pelo portão em segundos; voar às cegas dentro da casca do edifício deu quadros pretos (faces traseiras), portanto nenhuma rota natural até inimigo registrada. Não é resultado sobre história.
Ensaio no adaptador VPN: `lan_dryrun.py` com endereço de adaptador VPN (Radmin VPN, categoria de rede Public no Windows) conectou (`Connected!`, relay viu cliente daquele endereço). Executáveis de relay já iniciados antes tinham regras de entrada permitida para redes Public (consulta somente leitura das regras); amigo alcançando host pela VPN não veria novo aviso para esses executáveis; outra cópia do relay noutro caminho perguntará novamente.

### <a id="test-run-21-2026-10-22-native-patch-for-the-duplicated-map-enemies"></a>Execução de teste 21 (2026-10-22): patch nativo para inimigos de mapa duplicados
Decisão: aplicar patch direto ao executável (Ghidra 12.1.4 da versão oficial NSA no GitHub, SHA-256 conferiu com notas; JDK 21 já instalado; tudo no workspace).
Observações (Ghidra no executável OpenOL 2.1.0, ancorado em strings de `EnemyChannel.cpp` público):
- `ApplySpawn` = `FUN_14171eb00` (único chamador direto em `0x14172b0b4` de `OnBinaryPacket`); corpo confere linha a linha com fonte: `RemoteEnemies` no controlador `+0xeb8` (contagem `+0xec0`, elemento `0x44`: nome, `DummyEnemy +0x10`, `OwnerID +0x18`), `SpawnActor`, `Tag = MultiplayerDummyEnemy` em `+0x130`, `DestroyActor(controller)` = `FUN_1408d7550`.
- `TickSend` = `FUN_141736ae0`: `IndexEnemies` pela vtable do controlador `+0xbb0`, `CachedEnemies` em `+0xe78`, vida `+0x37c`, `SendSpawn` pela vtable do canal `+0x268` em `0x141736cab`.
- `GMpConn.LocalPlayerID` em `0x1436b9a70` (função compara id com ele para retornar herói local), `SyncEnemies` em `0x1436b9aec`, `GWorld` em `0x1430d1e58`; `UObject::Index +0x38`, `Name +0x48` (de `GetName()`), portanto `Class +0x50`.
Patch: `patches/native-one-owner` (fonte C compilada por MinGW em 1104 bytes de código independente de posição, acrescentado como seção `.olfix`, dois locais de chamada redirecionados). Regra: menor id de jogador mantém inimigo real.
Resultados na cópia de teste, grupo A:
- executável corrigido: 10 de 10 PASS, incluindo A4 (um proprietário), novo A4b (maior id carrega primeiro) e A4c (ambos processos vivos depois). Sem falha.
- variante, executável original na mesma preparação: A4 e A4b XFAIL (um ponto com pacientes enviados pelos dois), como em todas as execuções anteriores.
Ainda não conferido: script de história que espera cópia destruída, dois inimigos da mesma classe a até 150 unidades, três jogadores, dois PCs.

### <a id="test-run-22-2026-10-22-full-suite-on-the-patched-exe"></a>Execução de teste 22 (2026-10-22): suíte completa no executável corrigido
Um comando, grupos P, A, B, C, D, E, F, N, H, 1822 s: `{'PASS': 67, 'XFAIL': 4}`. Quatro XFAIL são erros conhecidos do relay (S9 a S11 no separado, E5 no embutido distribuído). A4 e A4b passam; novo N (inimigo real de mapa continua jogável, história avança ao checkpoint seguinte nos dois, processos vivos) 4 de 4.
Execução completa anterior no mesmo dia teve um FAIL, H3 (rajada de portas por script com perfil bad-wifi, ecos [0,0] de 10). Parecia regressão do patch: mesmo grupo passava no original ([9,9]). Log proxy mostrou causa: `fake_peer.py` contava pacotes recebidos em vez de tempo nas repetições de handshake; ONLINE_COUNT reordenado antes de READY fazia desistir em um segundo sem enviar portas. Corrigido, H3 passa também no corrigido ([10,10] e [9,9]). Não era erro do patch; teste da variante enganaria sem ler pacotes.
Ainda não verificado: inimigo roteirizado esperado pela história (cópia destruída no maior id), dois inimigos da mesma classe a menos de 150 unidades, caminho real do menu com patch, dois PCs.

### <a id="test-run-23-2026-10-22-the-real-player-path-with-the-native-patch-group-g"></a>Execução de teste 23 (2026-10-22): caminho real do jogador com patch nativo (grupo G)
`suite.py G`, 312 s, 6 de 6 PASS no executável corrigido: ambos iniciaram no principal, conectaram por Multiplayer > Connect (valores do ini), New Game > Main > Normal; registraram `StartGame`, depois história salvou `Admin_Gates` nos dois; matinee do carro cruzou relay nos dois sentidos para ambas as portas; ambos heróis transmitiam no mesmo local; um cliente encerrado, reiniciado no menu e reconectado, ambos transmitindo. Usa mouse e teclado reais (`harness/ol_menu.py`), executado separado, fora da execução padrão.

### <a id="test-run-24-2026-10-22-near-enemies-and-story-scenes-with-the-native-patch-read-from-the-games-memory"></a>Execução de teste 24 (2026-10-22): inimigos próximos e cenas com patch nativo, lidos da memória do jogo
Nova ferramenta somente leitura `harness/census.py`: lê da memória os inimigos próprios (`CachedEnemies`) e marionetes dos inimigos alheios (`RemoteEnemies`) pelos offsets do patch. Primeiro conferida num paciente: original, cada cliente tem 1 próprio + 1 marionete no mesmo local (2 inimigos); corrigido, cliente 0 tem 1 próprio, cliente 1 tem 1 marionete (1 inimigo), conforme projeto.
1. Dois inimigos da mesma classe a menos de 150 unidades (`fake_peer.py enemy-near`, par por script anuncia segundo paciente junto de real): a 86 unidades, menor id destruiu marionete do par (fusão falsa: cliente 0 viu 1 inimigo, cliente 1 viu 2); a 151 unidades, ambos concordaram (cliente 0: 1 próprio + 1 marionete, cliente 1: 2 marionetes). Dentro do raio, regra não distingue duplicata de outro inimigo. Raio menor perderia fusões de inimigos movidos entre anúncio e carregamento do outro (uma posição de criação reproduzida ficava a 172 unidades do inimigo após checkpoint); não alterado.
2. Cenas com inimigo, original vs corrigido, 25 s após carregar e um passo: Prison_OldCells_PreStruggle2 (um paciente): original 1 próprio + 1 marionete por cliente; corrigido 1 próprio no 0 e 1 marionete no 1, avisos iguais. Admin_MainHall: sem inimigos nas duas variantes. **Prison_PrisonFloor02_SecurityRoom2 (cena roteirizada Soldier): original 2 próprios + 2 marionetes por cliente (dois distintos e cópias); corrigido só 1 inimigo total por cliente (0 com 1 próprio, 1 com 1 marionete), e um evento remoto Kismet a menos no 0 (4 contra 5). Um dos dois inimigos falta nos dois no corrigido.** Ainda sem explicação: falsa fusão de inimigos próximos da mesma classe, um morto na cena ou cópia destruída parando script. Próximo: imprimir classe, posição e vida por inimigo na cena com ambos executáveis.
Avisos de script `Accessed None` também existem no original (ruído de referência), sem aumento nas execuções corrigidas.
Seguimento do teste 24 só por logs salvos (sem nova execução): inimigo ausente em `Prison_PrisonFloor02_SecurityRoom2` era artefato de tempo do teste. Passo que desperta inimigos iniciou luta roteirizada: nas duas variantes Soldier agarrou e matou herói, nível recarregou, e censo capturou fases diferentes. Logs mostram mesmos eventos Kismet na mesma ordem nos dois (`SoldierSAS`, `SoldierEnteredCloseSasDoors`, `AirlockParticlesFire`, depois segundo `SoldierSAS` após ressurgir; original só é mais longo). Nomes no cliente 0: original `Patient_0`, `Patient_2`, `Soldier_0`, `Soldier_1`, `Soldier_2` (reais e cópias), corrigido só `Patient_0` e `Soldier_0`. Original também registra `Accessed None 'Bot'` de Soldier marionete causando dano ao herói local; corrigido não, Soldier real mata herói com próprio bot (`SMT_KillHero`, `SMT_HeroDecapitate`). Portanto não há evidência de patch quebrando cena. Falta confirmação limpa: censo em tempo fixo após carregar sem despertar inimigos.
