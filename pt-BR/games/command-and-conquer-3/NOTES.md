# <a id="command--conquer-3-tiberium-wars--kanes-wrath-working-notes"></a>Command & Conquer 3: Tiberium Wars / Kane's Wrath: notas de trabalho

Iniciado em 2026-10-17. Objetivo: jogar as campanhas de um jogador de ambos em cooperativo (dois humanos). Preferência: facção e dinheiro próprios por jogador. Alternativa: compartilhar o controle da facção humana da campanha.

## <a id="0-identity-observed"></a>0. Identidade (observada)

| | Tiberium Wars | Kane's Wrath |
|---|---|---|
| Loja | Steam app 24790, buildid 17447444 | Steam app 24810, buildid 17447564 |
| Inicializador | `CNC3.exe` (lê `CNC3_english_1.10.SkuDef`) | `CNC3EP1.exe` (lê `CNC3EP1_english_1.3.SkuDef`) |
| Executável real | `RetailExe\1.10\cnc3game.dat` (PE32 x86, não empacotado, timestamp PE 2025-02-19) | `RetailExe\1.3\cnc3ep1.dat` (PE32 x86, não empacotado, timestamp PE 2025-02-19) |
| SHA-256 do executável | `af568a89b6d0d4f69ec690cf1d443539cb15afe197b96ac3fc5bf0ec0a56d141` | `1716c954ab80cf05752f4a4a467d34313a95a55a408718270f96382e330572f3` |
| Seções | `.text .rdata .data rts.ver .tls .rsrc` (sem `.bind` SteamStub, sem SecuROM) | iguais |
| Motor | SAGE (linhagem Generals), seção 3 | igual |
| Sistema operacional | Windows 11 | |

Executáveis antigos vêm junto (`RetailExe\1.0`..`1.9`); o `.bak` comercial da 1.9 tem seções `.securom`, mas Steam 1.10 / KW 1.3 não. Só as compilações Steam de 2025 importam aqui.

## <a id="1-existing-work-searched-2026-10-17"></a>1. Trabalhos existentes (pesquisados em 2026-10-17)

Pesquisados: este repositório (diretório, games/, issues, PRs por "Command and Conquer", "Tiberium", "Kane", "SAGE", "RTS"), busca web (várias formulações), repositórios GitHub ("cnc3 coop", "tiberium wars coop", "kanes wrath coop", "cnc3 campaign multiplayer", "sage engine coop"). ModDB bloqueou a coleta automática (verificação Cloudflare); só texto dos resultados usado. Não verificados: Discords CNCNet / C&C Online, fóruns Revora em profundidade, archive.org.

Observado:
- Sem campanha cooperativa oficial de PC para ambos. Fonte: resposta Revora, https://forums.revora.net/topic/100755-how-to-play-c-c-3-campaign-co-op-please-help/
- Xbox 360 tinha cooperativo contra IA, não história. Fonte: https://www.co-optimus.com/game/181/xbox-360/command-and-conquer-3-tiberium-wars.html
- Existem missões comunitárias cooperativas *personalizadas* como mapas multiplayer (não são a campanha oficial): COOP Evacuation (exige bot IA em uma posição), https://www.moddb.com/games/cc-tiberium-wars/addons/coop-evacuation-co-operative-mission ; pacote Boyle's Legacy e outros, https://forums.cncnz.com/topic/16232-boyles-legacy-co-op-mission-pack-re-released/ ; Co-Op Tiberian Sun Map Pack (exige Tiberium Essence), https://www.moddb.com/mods/co-op-tiberian-sun-map-pack
- Um trecho de busca cita membro do ModDB convertendo missões TW oficiais para ter um "Co-Commander"; página de distribuição não encontrada. Estado desconhecido.
- Kane's Wrath já possui proxy comunitário `dsound.dll` ("Tacitus", melhorias de conveniência, encontrado na instalação do usuário). Mostra que DLL proxy carrega normalmente na versão Steam.

Não encontrado nessas buscas: cooperativo de campanha no nível do motor para C&C3 ou KW.

## <a id="2-data-formats-observed"></a>2. Formatos de dados (observados)

- Mapas de campanha: `SP\1.0\SPMaps.big` (TW, 39 mapas), `Kane\1.0\KaneMaps.big` na pasta TW e instalação KW. Cada pasta contém `*.map` bruto e `map.bin/.imp/.manifest/.relo` compilados.
- `.big` é BIGF/BIG4 usual (tools/bigtool.py no ambiente).
- `.map` = fluxo RefPack contendo `EAR\0` + tamanho u32 + RefPack contendo arquivo de blocos `CkMp` (tools/sagemap.py decodifica; organização portada de OpenSAGE, https://github.com/OpenSAGE/OpenSAGE src/OpenSage.Game/Logic/Map/SidesList.cs, Data/Map/Player.cs).
- Facções de campanha (exemplo GDI 1-1 Pentagon): uma com `playerIsHuman=true` (`Plyr_GDI_a`), várias IAs nomeadas com aliados/inimigos e indicadores próprios (`Plyr_Nod_a..d`, aliada `Plyr_GDI_b` "Pentagon Defense Force"), além de civil e neutra. Nod 3-1 Slovenia: humana `PlyrNOD_A`, oito outras. Nomes variam por mapa.

## <a id="3-engine-seams-observed-in-the-tw-110-exe-with-reaghidra-1214"></a>3. Pontos de integração do motor (observados no executável TW 1.10 com REA/Ghidra 12.1.4)

- Referência: versão GPL de Generals Zero Hour da EA, https://github.com/electronicarts/CnC_Generals_Zero_Hour (`GameLogic::startNewGame`, `SidesList::prepareForMP_or_Skirmish`). Em Generals, todo jogo em rede ou escaramuça chama `prepareForMP_or_Skirmish`, removendo facções salvo civil e criando jogadores `player0..N` pelas posições da sala.
- `FUN_0068a498` em TW 1.10 é a versão C&C3: percorre facções, mantém só `PlyrCivilian` e `PlyrCreeps`, acrescenta modelos `SkirmishHuman`, `FactionCivilian`, `Multiplayer_Human`.
- Multiplayer Steam de 2025 usa Steamworks: strings de interface `SteamMatchMaking009`, `SteamNetworkingMessages002`, `SteamNetworkingSockets012` em ambos.
- Sala LAN ainda presente (`AptLanLobby::*`, `LANAPI`), incluindo `AptLanLobby::OnLoadGameBttn` (salvar/carregar multiplayer).
- Opções existentes: `-file`, `-xres`, `-yres`, `-noaudio`, `-noshellmap`.
- KW 1.3 tem as mesmas strings (`PlyrCreeps`, `Multiplayer_Human`, `SkirmishHuman`, `SteamNetworkingMessages002`, `LanLobby.apt`) em outros endereços.

## <a id="4-derived-reasoning-not-tested"></a>4. Deduções (raciocínio, não testado)

- Ambos usam um motor; uma DLL com tabelas de endereços por executável (assinaturas de bytes) deve servir aos dois. Começar por TW.
- Motor lockstep (linhagem Generals). Se ambos carregam o mapa com suas facções, scripts e IA rodam identicamente; não precisa sincronizar estado, só preparar jogadores e encaminhar comandos corretamente.
- Plano: iniciar sala LAN/Steam em mapa de campanha e substituir `prepareForMP_or_Skirmish` por DLL proxy para preservar facções. Depois:
  - controle compartilhado: vincular ambos à facção humana (comandos da posição 1 executam como jogador da campanha); ou
  - facção própria: acrescentar uma humana clonada da original, aliada. Scripts que nomeiam o jogador (reforços, derrota, objetivos) só afetam o primeiro, exigindo regras por missão.
- Sistemas exclusivos da campanha: instruções/vídeos, interface de objetivos, sequência (próximo mapa após vitória), salvamentos. Ficam fora do lockstep.

## <a id="5-unknowns"></a>5. Desconhecidos

- Se carrega `.map` bruto ou `map.bin` compilado para facções/scripts.
- Como C&C3 vincula posições a jogadores e marca comandos com índice de jogador.
- Se um mapa de campanha é selecionável na sala ou filtrado da lista.
- Como calcula/registra checksum lockstep (necessário como oráculo de teste).
- Se duas cópias rodam em um PC (verificações de instância), para testes automatizados.

## <a id="6-workspace-and-harness-2026-10-17-observed"></a>6. Ambiente e estrutura de testes (2026-10-17, observado)

- Instalações por hardlinks em `<workspace>\testinstall\tw|kw` (arquivos grandes vinculados, configurações/executáveis copiados). Verificado por `fsutil hardlink list`.
- `.dat` associado a editor hexadecimal no PC; `Start-Process` abriu o editor. Iniciar com CreateProcess (`UseShellExecute=false`).
- Inicializador executa `cnc3game.dat -config "<install>\CNC3_english_1.10.SkuDef"` (strings `-config "`, `-modConfig "` em CNC3.exe). Janela: `-win` (próxima a `-fullscreen`), `-xres/-yres`.
- Proxy `dinput8.dll` (só importa `DirectInput8Create`) carrega. Redireciona `SHGetSpecialFolderPathA/W`, dando AppData própria (escreve `AppData\Command and Conquer 3 Tiberium Wars\Profiles`); perfis do usuário intactos.
- Segundo plano: só renderiza enquanto acredita estar à frente. Hooks em `GetForegroundWindow` (retorna janela do jogo), `IsIconic` (FALSE), `ShowWindow` (SW_SHOWMINNOACTIVE) e operações nulas de `SetForegroundWindow/SetFocus` mantêm minimizado e ativo.
- PrintWindow gera preto (D3D9). Capturas internas: hook inline em `IDirect3DDevice9::Present`/`EndScene` + `D3DXSaveSurfaceToFileA` de `d3dx9_29.dll`. `Present` já tem hook de outro módulo neste PC (começa com `E9`, provável sobreposição Steam); o hook encadeia pelo salto, pois alteração de vtable era contornada.
- Nome do comandante preenchido previamente em `Profiles\directory.ini` (cada caractere como `<c>_00`, não alfanuméricos `_<hex>_00`; codificador conferido byte a byte em arquivo real), com `Options.ini` (800x600, detalhe baixo, volume 0).
- `WM_MOUSEMOVE/WM_LBUTTONDOWN/UP` postados à janela minimizada clicam botões APT (menu em 1024x768: Skirmish = (311,303)).

## <a id="7-startnewgame-tw-110-observed-in-ghidra-dump"></a>7. startNewGame (TW 1.10, observado em dump Ghidra)

- `FUN_004e0fd3` = metade de carregamento de mapa de GameLogic::startNewGame. `DAT_00bf92c4` = TheGameInfo (nulo em campanha). Com GameInfo remove equipes, chama `FUN_0068a498` (prepareForMP_or_Skirmish) quando `TheGameEngine->isMultiplayer()` ou há IA e chama `FUN_004c1674(hasAI, ...)`, que cria facções `Player_%d` / `Observer_%d`. `DAT_00bf34a0 + 0x18` = nome do mapa TheGlobalData (passado ao carregador).
- `FUN_0068ccee(i)` = GameInfo::getSlot(i); 8 posições.
- Classes de comandos correspondem a Generals (`NetGameCommandMsg`, `ConnectionManager`), mas sem busca `Player_%d` na rede; como o comando escolhe jogador continua desconhecido.

## <a id="8-shared-control-prototype-single-client-2026-10-17"></a>8. Protótipo de controle compartilhado, cliente único (2026-10-17)

Hooks DLL (só TW 1.10, conferidos pelos bytes de prólogo esperados):
- `0x4e0fd3` trecho de mapa startNewGame: trocar mapa por `CNC3COOP_MAP`; só nesta chamada, mudar `JZ` em `0x4e11a5` para `JMP`, preservando equipes da missão no ciclo de exclusão.
- `0x68a498` prepareForMP_or_Skirmish: ignorado. `0x4c1674` facções das posições: ignorado.
- `0x4bc5aa` (adiciona ReplayObserver): depois, definir `multiplayerIsLocal` na facção com `playerIsHuman` (não em ReplayObserver, também humano; marcá-lo tornava o jogador observador, com mapa revelado e interface de fim).
- `0x50fff4` VictoryConditions::update: ignorado (verifica jogadores Player_N).
- Tentado e rejeitado: zerar TheGameInfo no carregamento para forçar campanha. Tela de escaramuça o acessa (violação de acesso em `0x68cd12` via `0x4e1076`).

Resultados observados (capturas internas, execuções controladas por tests/t_skirmish.py):
- Escaramuça + hooks + `MAP_SP_GDI_0_1_Prologue`: esquadrões iniciais, câmera e estado parado iguais à campanha real (referência tests/t_campaign.py), sem derrota por cerca de 2 min. Barra lateral mostra botões de escaramuça, não objetivos/inteligência da campanha.
- Escaramuça + hooks + `map_sp_gdi_1_1_pentagon` (missão 2, sem contexto): introdução, objetivos e IA funcionam, mas ação de script encerra com DEFEAT após cerca de 70 a 120 s (ScriptActions `0x5365b7` -> `0x516bfb` -> interface `0x50fea6`). Ainda não comparado com campanha real dessa missão. Pendente.
- Referência real: Campaign -> GDI Campaign -> confirmação "Autosave Overwrite" (até com pasta vazia, causa desconhecida) -> vídeo (Esc pula) -> briefing espera PLAY.
- `-file <map>` não é atalho confiável: com caminho `.map`, acrescenta nome da pasta novamente e falha após carregar; com pasta, não inicia.

Ainda não testados: dois clientes, ordens do segundo, salvar/carregar, transições de missão.

## <a id="9-two-clients-on-one-pc-lan-co-op-start-2026-10-17"></a>9. Dois clientes em um PC, início cooperativo LAN (2026-10-17)

Observado:
- Sala mostra primeiro "Firewall Detected" e recusa continuar em NO. Para testes, DLL faz `CoCreateInstance` de NetFwPolicy2/NetFwMgr falhar (só indicador de ambiente de teste); nenhuma configuração do firewall alterada. Jogador real clica YES uma vez (adiciona exceção).
- Protocolo LAN só por broadcast: todas as mensagens a 255.255.255.255 nas portas 8086-8093.
- Mesmo IP em duas instâncias: sala funciona e convidado entra, mas no início fica em "Starting the game...", e host vence por expiração. Corresponde a Generals, que identifica por IP (`LANAPI::handleRequestJoin` verifica `msg->GameToJoin.gameIP != m_localIP`).
- Correção (adaptação de rede só de teste, `CNC3COOP_LOCALIP`/`CNC3COOP_PEERS`): cada instância informa 127.0.0.N por `gethostbyname`, vincula sockets a ele, broadcasts reenviados como unicast às demais; `GameSpyIPAddress = 127.0.0.N` e `FirewallPortOverride` distinto preparados em Options.ini; `SIO_UDP_CONNRESET` desligado. Sem este, ICMP de porta inacessível das cópias unicast atrasava receptor cerca de um minuto e expirava entradas.
- Com adaptação, LAN original de dois clientes inicia em ambos (teste `t_lan_coop.py mode=`).
- Modo compartilhado LAN no prólogo GDI: ambos carregam mapa e facções da campanha, marcam `GDI_a` local, quadros lógicos avançam nos dois (cerca de 15/s), capturas coincidem.
- Mapeamento posição -> jogador: nome em `GameSlot+0x34` (definido como `Player_%d` por `0x4c1674`, chamada `0x4c1743`), usado na resolução. O mod define o nome de toda posição humana ocupada como a facção humana da campanha. Efeito nas ordens não verificado.

Descobertas sobre entradas da estrutura:
- Mensagens postadas funcionam em menus APT, seleção e dicas, mas não acionam botões laterais (usina não construída); clique esquerdo no chão com infantaria selecionada não moveu (prólogo; talvez bloqueio de entrada da missão, desconhecido).
- Vista tática lê cursor por `GetCursorPos`; a DLL agora responde (e ScreenToClient/ClientToScreen/GetAsyncKeyState) com cursor virtual e bloqueia `SetCursorPos`/`ClipCursor` em segundo plano. Só cria teclado DirectInput, zerado em segundo plano para teclas do usuário nunca chegarem aos testes.

Em aberto:
- Comprovar execução de ordens do convidado pela facção compartilhada. Plano: bot interno acrescentando GameMessages (mover, construir) diretamente, sem cliques; tabela `MSG_*` tem 227 nomes para deduzir IDs.
- Derrota roteirizada em Pentagon; transições; salvamentos; facções separadas; Kane's Wrath.

## <a id="10-first-human-test-and-follow-up-2026-10-17"></a>10. Primeiro teste humano e acompanhamento (2026-10-17)

Relato do usuário (C&C Online, dois PCs, 0.0.1): hospedagem normal, ambos entram, conversa funciona, mesmas unidades, área e cenas. Jogador 2 não controla unidades do 1. Sair da partida fecha para a área de trabalho.

Observado depois (LAN, duas instâncias, TW 1.10):
- Despachante lógico = `0x4e995b` (thiscall, ret 8). GameMessage +0x0c tipo, +0x10 índice; executa para `ThePlayerList(*0xbee110)->getNthPlayer(idx)` (`0x49714c`). Player +0x44 chave do nome; PlayerList +0x1c local, +0x20 contagem, +0x24 Player*[]. NameKeyGenerator `*0xc28ccc`, nameToKey `0x9ddec0`.
- IDs de tipo no switch de nomes `0x54f2d6`, tabela de bytes `0x54ffc1` (dump/msgtypes_tw110.txt): MSG_CREATE_SELECTED_GROUP 0x1f5, MSG_DESTROY_SELECTED_GROUP 0x1f8, MSG_DO_MOVETO 0x23c, MSG_DO_STOP 0x242, MSG_LOGIC_CRC 0x257.
- Ambos: facção GDI_a = jogador 1 = LOCAL.
- Seleção por clique postado não gera mensagem lógica (seleção é local até comando), e cliques não geram ordens; estrutura ainda não testa controle.
- Saída LAN (Esc por tecla DirectInput injetada > Exit > Yes > Skip > Continue): host/convidado voltam à sala Network, sem falha. Falha do usuário provavelmente no caminho pós-jogo exclusivo on-line (relatório espera Player_N; estatísticas `MISSING: 'TimeLine:PlayerName:1'`). Não confirmado.
- 0.0.2 = versão com registro (CNC3COOP_MSGLOG=1 padrão) para teste de controle/saída pelo usuário.

## <a id="11-owner-test-of-002-cc-online-2026-10-18"></a>11. Teste de 0.0.2 pelo usuário (C&C Online, 2026-10-18)

- Log host: comandos como jogador 1 (campanha): `MSG_CREATE_SELECTED_GROUP`(0x1f5), depois `MSG_DO_MOVETO`(0x23c), quadros 248/256 e 523/531. Não se sabe qual par era do convidado.
- Log convidado inutilizável: processo antigo (PID 3092), parado após hooks; o jogo real era PID 21976 e não abriu log bloqueado. 0.0.3 usa alternativa `cnc3coop_<pid>.log`.
- Falha de saída idêntica em ambos: violação de acesso no heap ntdll (+0x4e6e2), thread de trabalho 0x6ac197 -> 0x69d58e -> 0x6944b0 (relatório on-line: `FUN_007ba0ea(...,5,players, teams)` e registros por jogador) -> 0x7c654c. LAN não executa isso. 0.0.3 faz 0x6944b0 retornar falso no cooperativo (caminho próprio de impossibilidade de criar relatório). Ainda não confirmado on-line.
- tools/minidump.py lê minidumps WER (exceção, módulos, pilha da thread da falha).
- 0.0.3 acrescenta Setup.bat (WinForms): detecção Steam por registro + libraryfolders.vdf + appmanifest_24790.acf, lembra pastas em %LOCALAPPDATA%\cnc3coop\settings.json, atualizações só substituem arquivos quando a cópia de instalação é mais nova.

## <a id="12-guest-orders-fixed-2026-10-18"></a>12. Ordens do convidado corrigidas (2026-10-18)

Teste do usuário em 0.0.3 (C&C Online): falha de saída eliminada nos dois. Convidado seleciona e ouve falas, mas unidades não movem. Logs mostram mesmo fluxo, tudo como jogador 1.

Observado (LAN, dois clientes em um PC, registro em ambos):
- Seleção do convidado criada pela interface (TheMessageStream `*0xbf34b0`, vtable+0x48 appendMessage), passada à etapa de envio `0x69fa54`, mas nunca acrescentada a quadro algum (construtor de cópia `0x554928` chamado por `0x6a7329`) em nenhum cliente. Comandos do host passam nos dois.
- Causa: receptor `0x6a35e3` mantém por posição (+0xe0 no registro de 0xd0 bytes) o ID `cmd+0x24` do primeiro comando; se outro tem mesmo ID, marca posição como -2 e descarta todos os comandos. Ambos agem pela facção da campanha, tornando o convidado duplicado. Correção: em modo compartilhado, `JNC` em `0x6a37b0` (`0f 83 04 01 00 00`) -> `90 e9 04 01 00 00`. Depois, ordens do convidado executam nos dois clientes.
- Seleção lógica compartilhada (Player+0x208, só definida por mensagens de seleção) agora por cliente: cada um clona suas seleções (construtor de cópia, alocação `0x402997`) e, se a seleção de outro executou no intervalo, reenvia pela sequência própria (`0x690691` ctor(frame, msg) -> `0x69e3b9` fila em `[net+0x1c]` -> `0x68d841` liberar) antes da próxima ordem. Teste: host seleciona, convidado seleciona, host pressiona S: host reenvia seleção no quadro 642 e DO_STOP no 642, mesma ordem em ambos.
- Cliques postados ainda não geram deslocamento; ordens por teclado (S) geram, pois teclas postadas agora alimentam DirectInput em segundo plano.

## <a id="13-mission-end-and-mission-flow-2026-10-18"></a>13. Fim e fluxo de missão (2026-10-18)

Observado (TW 1.10):
- Scripts encerram missões por objetivos e eliminação de facções; só GDI 3-3 usa `VICTORY`/`DEFEAT` e GDI 3-4 `QUICKVICTORY` (levantamento mission-survey.md). Ações: VICTORY = tipo 3 -> `[0xbf0440]` (TheVictoryConditions) vtable +0x7c; DEFEAT = 4 -> +0x80; PLAYER_KILL = 78 -> `0x518311` -> Player::kill `0x4a67c5`; MARK_MISSION_OBJECTIVE_COMPLETED = 536 -> `0x4f79b8` -> setStatus(2) do objetivo `0x4c900c` (só EVA, sem verificar vitória). TheMissionObjectiveTracker é `*0xb81560`.
- Vtable VictoryConditions `0xa6456c`: +0x38 hasWon `0x4f671f`, +0x3c hasLost `0x4f67b6`, +0x40 isDefeated `0x4f67f5` (+0x74 morto, +0x88 regra de eliminação), +0x7c victory `0x516b29` (grava progresso por `0x4e0766`/`0x4e0614`), +0x80 defeat `0x516bfb`. Último bloco chama hasWon(local) -> victory, senão hasLost(local) -> defeat. hasWon verifica última facção restante.
- Com atualização ativa no cooperativo, a facção da campanha falhava na regra multiplayer inicial (EndGameUI DEFEAT de `0x510279`). Correção: hook em isDefeated para a facção local nunca ser eliminada por essa regra; atualização permanece ativa.
- Teste (LAN, dois clientes, prólogo): gatilho exclusivo de teste elimina todas as outras facções no quadro 600 (despacho lockstep, mesmo quadro em ambos); ambos recebem EndGameUI(VICTORY) por `0x51049e` no 611.
- Fluxo: missão atual é nome de pasta em `<home>\coop_mission.txt`, lido a cada início; na vitória ambos avançam à próxima de missions.txt (mesmo grupo de campanha).
- Vídeos: `Movies\1.0\Movies*.big` têm VP6 (`g01a`, `g02ba`, ...); ligação missão -> vídeo está em dados de campanha compilados. Reprodução pela DLL ainda não feita.

## <a id="14-gdi-2-pentagon-defeat-traced-2026-10-18"></a>14. Derrota de GDI 2 (Pentagon) rastreada (2026-10-18)

Observado (dois clientes LAN, Pentagon iniciado diretamente, ninguém jogando):
- 0.0.5 inicial: DEFEAT após cerca de 15 s, mesmo quadro em ambos. Rastreamento: hook DLL no executor `0x532d6f` (thiscall, `ret 8`; argumento Script, vtable `0xa646f4`; +0x30 lista OrCondition, +0x34 ações, +0x38 ações falsas, +0x44 nome) e verificação individual `0x528c13` (thiscall, `ret 4`; condição +4 tipo, +0xc primeiro parâmetro, AsciiString em parâmetro+0x10). Tipos vêm da tabela `0x5082ec` (passo 0x80; 4 TIMER_EXPIRED, 8 TEAM_DESTROYED, 15 NAMED_DESTROYED, 53 UNIT_HEALTH, 56 PLAYER_HAS_OBJECT_COMPARISON). Dentro de OrCondition, condições usam AND; OrConditions usam OR.
- Cadeia: scripts de derrota do mapa só definem `Mission Lost`; script externo ao mapa (nome vazio, `TIMER_EXPIRED t_ShowDefeated` -> `DEFEAT`) mostra derrota segundos depois. No quadro 75, regra multiplayer julgou três IAs derrotadas (Plyr_GDI_b, Plyr_Nod_d, Plyr_GDI_d), e a atualização as matou (`0x4a67c5`), destruindo objetos. Plyr_GDI_b tem o edifício `_G_B_Penta-building`; scripts de saúde simbiótica zeram o Pentágono -> NAMED_DESTROYED -> Mission Lost.
- Correção: em cooperativo, uma facção só é derrotada após Player::kill (indicador `Player+0x20c`, definido por PLAYER_KILL dos scripts), nunca pela regra de não restar nada. Depois, nenhuma é eliminada.
- Sem ninguém jogar, ainda acontece: usina aliada 1 (inicia com 50%) destruída por Nod em cerca de 40 s; script perde a missão (`G_A_POwer Plant 1 lose`). Esperado para jogador inativo; não comparado ao modo individual. Pentagon não tem scripts específicos de dificuldade.
- Usina do prólogo (relato: bombardeiros danificaram, mas não destruíram): nenhum script a destrói; equipe Nod `Act1_TEAM_PowerPlantAttack` a ataca e depois ao MCV. Se for abatida antes de chegar, a usina sobrevive. Scripts de dificuldade só mudam dinheiro e forças de ataque Nod.
- Problema só na primeira 0.0.5 (0.0.4 mantinha atualização de vitória desligada). Antes da correção, qualquer IA que falhasse na primeira verificação seria morta em qualquer missão (não conferido missão por missão).
