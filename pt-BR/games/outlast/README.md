# <a id="outlast-2013"></a>Outlast (2013)

| | |
|---|---|
| Motor | Unreal Engine 3 (`CookedPCConsole`) |
| Versões testadas | Steam 576074, `Binaries\Win32\OLGame.exe` SHA-256 `fc06a9d562ea41757fa7c95abae67c89fb4f56a9c970122fdef2f15758f2bb0d`, DLC Whistleblower instalado, Windows 11 |
| Projetos | [Fork OpenOL com nossos patches, kit e testes](https://github.com/G3RKA/OpenOL) (desenvolvimento próprio, `tools/outlast-coop/`), [OpenOL](https://github.com/ShyKiss/OpenOL) com [OpenOL-Relay](https://github.com/ShyKiss/OpenOL-Relay) (diretório: alpha), [Outlast-Together](https://github.com/LucianLandIsBack/Outlast-Together) (abandonado) |
| Nível de QA | automated (67 PASS, 4 XFAIL de bugs conhecidos na última execução completa; consulte [QA](#qa)) |
| Última atualização | 2026-10-22 |

## <a id="where-things-stand"></a>Situação atual

OpenOL 2.1.0 tem beta multiplayer funcional usando OpenOL-Relay 2.1.0 independente e sala `PUBLIC`. Dois clientes num PC ficaram conectados de 5 a 13 minutos, viram-se, compartilharam portas e inimigos criados por jogadores, com dano, morte e reaparecimento. História rudimentar: gatilho tocado por um dispara para todos onde estiverem, checkpoints não sincronizam e inimigos do mapa duplicam (cada cliente simula sua cópia, ambas atacam o mesmo jogador). A *cópia-fonte* do retransmissor embutido no repositório usa formato antigo (o integrado ao executável distribuído funciona). Nada testado entre dois PCs.

## <a id="existing-work"></a>Trabalhos existentes

| Projeto | O que é | Última atividade | Notas |
|---|---|---|---|
| [OpenOL](https://github.com/ShyKiss/OpenOL) | Cliente UE3 modificado (`OLGame.exe` recompilado e pacotes), instalado sobre Steam licenciado; beta desde 2.0.1, versão 2.1.0 em 2026-08-29 | 2026-08 | Fontes públicas sem licença declarada (API `license: null`). Exige Whistleblower (mapa `DLC_Intro_Persistent`). Issues #6 (mapa ausente), #7 (conectar não faz nada), #8 (Start Server/Invite não fazem nada). |
| [OpenOL-Relay](https://github.com/ShyKiss/OpenOL-Relay) | Retransmissor UDP independente (CLI e interface) | 2026-08 | Cria sala `PUBLIC` quando banco vazio. Usado em todos os testes no commit `b9def512` ("Update to 2.1.0"). |
| [Outlast-Together](https://github.com/LucianLandIsBack/Outlast-Together) | Projeto escolar MIT com DLL de rede e pasta cliente | 2025-02 | Sem versões distribuídas. README diz que não haverá atualizações após entrega escolar. Sincronização não verificada. |

Também vistos: item Workshop "Outlast multiplayer" (mapa Garry's Mod removido), mods ModDB/Nexus (só solo nos resultados). Não pesquisados: Reddit, Discord, archive.org, guias Steam.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- UE3 com módulo nativo `OLGame`. OpenOL distribui `OLGame.exe` recompilado e `.upk`; árvore tem código (`Development/Src/OLGame`), multiplayer (`Development/Src/Multiplayer`) e retransmissor (`Development/External/openol_relay`).
- Formato transmitido (2.1.0, `FMpConnection::SendBinary`): `[channel][type][player_id LE4][payload]`. Canais SRV 0, HERO 1, DOOR 2, ENEMY 3, PUSH 4, WORLD 5; avisos ao cliente começam em 0xE0 (`READY`, `ONLINE_COUNT`, `HELLO_FAIL`). Conecta por texto `HELLO,<room>,<password>`, recebe `READY` e identificador, envia `SRV_HELLO` binário com apelido e `SRV_PING` a cada ~5 s. Silêncio de 30 s desconecta nos dois lados.
- Retransmissor encaminha dentro da sala e guarda capturas para entradas tardias (portas, inimigos, objetos empurráveis, último estado do herói e matinee).
- `HERO_STATE` leva posição, rotação, vida e movimento especial; inimigos enviados como `SPAWN`, `LOC` (modo e alvo do olhar), `SMT` (movimentos) e `DEL`; eventos globais: `TRIGGER_ACT` (toques Kismet por caminho), `MATINEE_STATE`, coletas, `RemoteEvent`s.
- Cada inimigo criado ou possuído por cliente é simulado localmente e espelhado nos demais por representante identificado por nome e responsável.
- Com Steam, lê perfil Steam Cloud; com `-nosteam`, usa `OLGame\SaveData\*.olprofile` e `OLGame\SaveData\OL_<date>.sav` na pasta do jogo. Configuração UE3 vai para `<game dir>\OLGame\Config\` (inclui `OLMultiplayer.ini`).
- Cliente inicia direto em mapa por comando (nem todos: `adminblock_persistent` falha com `Assertion failed: Sequence != RootSequence [UnWorld.cpp:1693]` e janela Windows; iniciar `prison_persistent` e carregar checkpoint) (`OLGame.exe prison_persistent?game=Multiplayer.MultiplayerGame -nosteam`). Checkpoint específico só pela sobreposição F6 ou console; URL `#name` carrega criação padrão do mapa.
- Sobreposição F6 (Dear ImGui): abas Checkpoints (busca), Spawns, Player, Scene.

## <a id="what-we-changed"></a>O que alteramos

**Patches do retransmissor (OpenOL-Relay, opcionais, sem fontes do jogo).** `0001` [relay-patches/0001-openol-relay-trigger-radius.patch](https://github.com/G3RKA/OpenOL/tree/main/tools/outlast-coop/relay-patches/0001-openol-relay-trigger-radius.patch) acrescenta `--trigger-radius <units>`. Só encaminha gatilho a quem tem última posição conhecida dentro da distância ao remetente; posições desconhecidas permitem envio; 0 (padrão) mantém original. `0002` [relay-patches/0002-openol-relay-enemy-packet-ids.patch](https://github.com/G3RKA/OpenOL/tree/main/tools/outlast-coop/relay-patches/0002-openol-relay-enemy-packet-ids.patch) usa identificadores `ENEMY_*` do cliente 2.1.0 (`LOC` 0x04, portas 0x05 a 0x08), dando posição na captura ao entrar com inimigo vivo (responsável já transmite posições, então efeito no jogo pequeno). `0003` [relay-patches/0003-openol-relay-drain-snapshots.patch](https://github.com/G3RKA/OpenOL/tree/main/tools/outlast-coop/relay-patches/0003-openol-relay-drain-snapshots.patch), correção de uma linha: CLI preenche fila de capturas tardias, mas nunca chama `server_drain_snaps`; participante não recebe itens coletados, últimos estados matinee/herói nem repetição automática de portas/inimigos/empurráveis (jogo solicita os três últimos, por isso funcionavam). Todos aplicam a `OpenOL-Relay` em `b9def512` nessa ordem (0003 também isolado). Consequência: jogador distante perde gatilho e história pode divergir até reencontro; escolha raio que cubra área conjunta (suíte usa 3000). Nada no próprio OpenOL alterado.

**Patch nativo de inimigos duplicados (executável, opcional):** [exe-patch](https://github.com/G3RKA/OpenOL/tree/main/tools/outlast-coop/exe-patch/README.md) adiciona ~1 KB a `OLGame.exe` 2.1.0 e redireciona duas chamadas (`ApplySpawn`, `SendSpawn` em `TickSend`): encontrando duas cópias do inimigo de mapa, menor identificador mantém real, outro destrói cópia local e fica com representante. Descoberto no Ghidra pelas fontes públicas multiplayer, sem fontes Outlast. A4/A4b passam com patch e falham no original (variante).

**Alternativa sem fontes para inimigos duplicados (sem patch nativo):** `SyncEnemies=False` em `OLMultiplayer.ini` em todos. Nenhum pacote inimigo enviado/aplicado; cada um fica com cópia independente (sem fantasma/dano duplo, mas parceiros não veem inimigos uns dos outros). Filtro no retransmissor considerado e rejeitado (NOTES.md, execução 12).
Problemas e evidências em [NOTES.md](NOTES.md) (execuções 1 a 11):

| # | Problema | Causa raiz (leitura de fontes) | Teste que demonstra |
|---|---|---|---|
| 1 | Cliente reconecta a cada ~30 s com novo identificador usando *cópia-fonte* integrada ao repositório (integrado ao `OLGame.exe` distribuído não faz: dois clientes, execução 16) | `server.c` integrado interpreta `[type][player_id]`; cliente envia `[channel][type][player_id]`; todo binário descartado, expira | Execução 2; mesmos clientes estáveis em OpenOL-Relay `b9def512` (3 a 8) |
| 2 | Conexão direta a host "Start Server" não mostra nada | Padrão `PUBLIC`, integrado só `DEFAULT`; cliente ignora `HELLO_FAIL` | Sonda (`hello_probe.py`): `DEFAULT` retorna `READY`, `PUBLIC` retorna `HELLO_FAIL`; sem host real |
| 3 | Identificadores `ENEMY_*` diferentes (`LOC` 0x08/0x04, portas deslocadas em um) | Constantes copiadas manualmente | T6/T7: captura tardia original tem `SPAWN`, sem `LOC`; patch 0002 corrige |
| 4 | Checkpoints não sincronizam; gatilhos para todos sem contexto | Toques enviados por caminho e forçados em todo cliente | Execução 7: par roteirizado enviou `SeqEvent_Touch_0..30`; 13 dispararam nos dois, história e salvamento avançaram. Gatilhos mitigados pelo patch (B3/B4, `relay_filter_test.py`); checkpoints ainda não |
| 5 | Inimigos duplicados atacam mesmo jogador (após carregar por F6; **não verificado no progresso normal**, hipótese aberta em NOTES.md) | Cada cliente envia todos os locais; sem responsável único | Execução 8: dois pacientes, `HERO 0x07` de ambos, dano duplo. **Corrigido no patch nativo** (A4/A4b PASS; execução 21) |
| 6 | Menores: atraso iniciando minimizado, pausa interrompe pings, pacote `OpenOLResources` desconhecido, aviso de perfil Steam | Consulte NOTES | Execuções 3/7 e fontes |
| 7 | Independente nunca envia fila tardia (coletas, matinee e herói alheios perdidos) | `server_drain_snaps` declarada/documentada a cada atualização, mas laço CLI `main.cpp` não chama (laço `server_run` chama) | S9 a S11 (XFAIL original, PASS patch 0003); encontrado com depuração registrando fila |

Não relatados aos autores OpenOL; fork desenvolvido independentemente.

## <a id="licence"></a>Licença

Conferido em 2026-10-25 pela API: [OpenOL](https://github.com/ShyKiss/OpenOL) e [OpenOL-Relay](https://github.com/ShyKiss/OpenOL-Relay) sem licença (`license: null`, arquivo ausente); direitos permanecem com autor por padrão. README diz arquivos só para conveniência de modificação, executável `OLGame.exe` substitui arquivos da cópia Steam licenciada; nada sobre forks/patches. Autor não consultado. Como trabalho respeita isso:

- Nenhum binário OpenOL/Outlast redistribuído: sem `OLGame.exe`, `.upk`, arquivo de lançamento ou recursos. Patch distribuído como C próprio, bytes compilados próprios e aplicador executado no `OLGame.exe` 2.1.0 baixado pelo jogador. Confere SHA-256 e bytes originais em sete locais (5 a 8 bytes cada), recusa outros arquivos. É a rota de distribuir patch para própria cópia da regra 7.
- Patches são diffs unificados sobre OpenOL-Relay `b9def512` (linhas alteradas e três de contexto); jogador aplica ao próprio clone e compila.
- [G3RKA/OpenOL](https://github.com/G3RKA/OpenOL) é fork GitHub, permitido pelos termos para repositório público; arquivos originais seguem termos originais. Trabalho próprio em `tools/outlast-coop/` sob MIT (só pasta). Um original alterado: `Development/Src/Multiplayer/Src/EnemyChannel.cpp` (+66 linhas), regra de responsável único como referência; não compilado/distribuído em binário.
- Quem quiser distribuir executável pré-compilado com patch ou mais código OpenOL deve pedir autorização ao autor.

## <a id="qa"></a>QA

Comando (Windows, duas janelas por cerca de 10 minutos; definir `OL_GAME_DIR`, `OL_LOG_DIR`, `OL_RELAY_EXE`; [harness/README.md](https://github.com/G3RKA/OpenOL/tree/main/tools/outlast-coop/harness/README.md)):
```
python -I tools/outlast-coop/harness/suite.py       # in the fork https://github.com/G3RKA/OpenOL        # everything (P, A, B, C, D, E, F; about 25 minutes); or: suite.py P | A | B | C | D | E | F
```

Inicia retransmissor e proxy de logs, dois clientes reais na cópia (`-nosteam`), carrega checkpoints, injeta pacotes por par roteirizado, cria inimigos por F6, verifica estado decodificado e logs; exibe `RESULT: PASS|FAIL|XFAIL|XPASS|SKIP|ERROR <test>` por teste e `SUMMARY`. Saída 0 só sem FAIL/ERROR/XPASS. Janela de falha vira ERROR.

| Teste | Asserções | Último resultado |
|---|---|---|
| P (26 resultados, sem jogo, `relay_filter_test.py` T1-T7 e `relay_state_test.py` S1-S13) | raio de gatilho (perto, longe, posição desconhecida, desligado, portas sem filtro), captura tardia com posição inimiga, exclusividade de trancas e primeira escrita prevalece, responsabilidade/liberação de empurráveis, `PUSH_INIT`, repetição de coletas/matinee/herói; variantes no original (T4/T7) e espelhos cegos (S8/S13) | 23 PASS; S9 a S11 originais XFAIL (drenagem ausente, patch 0003 corrige) |
| S0 autoteste do avaliador | avaliador de expiração vê entradas boas/ruins (ignora sonda HELLO deixada por `ol.py up`) | PASS |
| A1 | ambos enviam estado atualizado | PASS |
| A2 | sem reconexão em 45 s (um `Connected!` por cliente) | PASS |
| A3 | retransmissor nunca expira cliente real | PASS |
| A6 | `DOOR_OPEN` de porta real enviado pelo par é aplicado por ambos (cada um ecoa uma vez) | PASS |
| A7 | variante A6: posição sem porta não aplicada por ninguém | PASS |
| A4 | inimigo de mapa enviado por só um | PASS com patch nativo; XFAIL original (ambos enviam cópia) |
| A4b | igual, com identificador maior carregando primeiro | PASS nativo; XFAIL original |
| A4c | ambos vivos após transferência inimiga | PASS |
| N1 | paciente real (checkpoint nos dois) tem um remetente | PASS nativo (ignorado no original) |
| N2 | ambos vivos após transferência | PASS |
| N3 | história avança: segundo checkpoint do grupo carrega nos dois, heróis chegam juntos e transmitem | PASS |
| N4 | ambos vivos após segunda carga | PASS |
| G1 | ambos conectam pelo menu real (Multiplayer > Connect, valores ini) | PASS |
| G2 | New Game em ambos: `StartGame`, depois `Admin_Gates` salvo pela história nos dois | PASS |
| G3 | cena do carro (matinee) cruza retransmissor nos dois sentidos para ambos | PASS |
| G4 | heróis transmitem e compartilham início após introdução | PASS |
| G5 | cliente encerrado retorna pelo menu; ambos transmitem novamente | PASS (G exige mouse/teclado reais, 312 s, executado isoladamente) |
| A5 | ambos criados no mesmo ponto após checkpoint | PASS |
| B1 | `WORLD_TRIGGER_ACT` injetado dispara nos dois | PASS |
| B2 | variante B1: caminho falso não dispara | PASS |
| B3 | gatilho de par distante (50000 unidades) não aplicado | PASS com patch; original dispara em ambos (mesmo teste com `OL_PATCHED_RELAY_EXE` apontando a lugar inexistente relata XFAIL) |
| B4 | controle: mesmo gatilho de par próximo aplicado | PASS |
| F1 | segundo entrando/carregando mesmo checkpoint com inimigo vivo e calmo no primeiro recebe inimigo retransmitido | PASS |
| F2 | e sua posição | PASS |
| F3 | participante tardio transmite estado | PASS |
| F4 | primeiro não perturbado (sem reconectar) | PASS |
| E1 | dois conectam ao integrado no `OLGame.exe` distribuído, iniciado F6 > Relay > Start Relay (sala `DEFAULT`; suíte troca/restaura ini) | PASS |
| E2 | sem reconexão em 65 s (um `Connected!` cada) | PASS |
| E3 | ambos transmitem por ele | PASS |
| E4 | captura tardia tem `SPAWN` | PASS |
| E6 | participante tardio recebe coletas guardadas sem pedir (fila enviada; adicionado após última completa, E isolado PASS) | PASS |
| E5 | e posição (`LOC`) | XFAIL (integrado com `ENEMY_LOC` 0x08/0x04 divergente; patch 0002 corrige fonte, não executável) |
| D1 | `SyncEnemies=False` em `OLMultiplayer.ini` nos dois: nenhum pacote inimigo cruza (suíte edita/restaura) | PASS |
| D2 | cada um mantém inimigo próprio (checkpoint do paciente aplicado) | PASS |
| D3 | inimigo criado num cliente não espelhado | PASS |
| D5 | pré-condição D3/D4: inimigo em A realmente atacou (`SMT_AttackGrab` no log) | PASS |
| D4 | outro jogador não recebe dano dele | PASS |
| H1 | dois com conexão prejudicada (`tools/chaos` perfil `bad_wifi`: ~35 ms +/- 25, perda em rajadas 2%, reordenação) conectados por 90 s | PASS |
| H2 | ambos ainda transmitem | PASS |
| H3 | rajada de 10 pacotes abrir/fechar porta aplicada por ambos (mínimo 7 ecos de 10) | PASS (9 de 10) |
| H4 | interrupção 10 s não reconecta; fluxos retomam | PASS |
| H5 | interrupção 40 s recuperada: cada um reconecta uma vez e transmite | PASS |
| C0 | controle: sem inimigo, sem perder vida em 8 s | PASS |
| C1 | inimigo de um jogador retransmitido ao outro | PASS |
| C2 | inimigo causa dano | PASS |
| C3 | morte anunciada ao outro | PASS |
| C4 | morto reaparece com vida | PASS |
| C5 | morte do responsável remove seu inimigo | PASS (SKIP se não morrer) |
| C6 | morte de outro não remove inimigo do responsável | PASS (SKIP se outro não morrer) |

Última completa em 2026-10-22, um comando (`suite.py`, P/A/B/C/D/E/F/N/H), executável com patch nativo, 1822 s: `{'PASS': 67, 'XFAIL': 4}`, sem FAIL (S0 conta uma vez). Anterior no mesmo dia tinha FAIL H3: par de teste desistia do handshake em um segundo na conexão ruim (bug da estrutura, corrigido esperando READY por tempo, não por pacotes; patch nativo não envolvido, execuções de variantes). XFAIL: E5 (posição ausente na captura integrada) e S9-S11 original (fila não enviada; só independente, integrado envia, teste E6). Execuções anteriores por grupo iguais; primeiras encontraram problemas acima.
Teste de protocolo sem jogo, [harness/relay_filter_test.py](https://github.com/G3RKA/OpenOL/tree/main/tools/outlast-coop/harness/relay_filter_test.py) (7/7, variantes no original). Primeiras execuções acharam avaliador contando expiração HELLO, mapa inicial errado (`adminblock_persistent` derruba motor, seção de funcionamento), posição de criação fora do alcance de ataque e inimigo ocioso só atacando quem se move (100 a 190 unidades); todos tratados na suíte.

Limites: cobre estabilidade, criação, portas/gatilhos injetados, responsabilidade de inimigos de mapa, inimigos criados por jogadores com dano/morte/reaparecimento. Não cobertos no jogo: empurráveis (efeito remoto não observável), cenas, coletas, progresso da história, outros tipos de inimigos, dois PCs. Bots usam entrada de área de trabalho e F6 (carregar, criar inimigos, vida), não bot interno preferido pelo repositório. Variantes de portas/gatilhos (A7/B2) e controle C0; demais ainda sem correção para desligar. XFAIL A4 codifica bug atual; correção produz XPASS e exige inverter expectativa. B3 só passa com patch (seção de alterações).

## <a id="how-to-play"></a>Como jogar

Internet não verificada. Configuração funcional num PC:

1. Copie instalação (exige Whistleblower), aplique OpenOL 2.1.0 na cópia, preserve original.
2. Host: retransmissor com UDP 7777 acessível. Versão `OpenOL_Relay` (sala `PUBLIC`), integrado (F6 > Relay > Start Relay, `DEFAULT`) ou compilado:
   ```
   git clone https://github.com/ShyKiss/OpenOL-Relay && cd OpenOL-Relay && git checkout b9def512
   patch -p1 -d src < <OpenOL fork>/tools/outlast-coop/relay-patches/0001-openol-relay-trigger-radius.patch    # optional
   patch -p1 -d src < <OpenOL fork>/tools/outlast-coop/relay-patches/0002-openol-relay-enemy-packet-ids.patch   # optional
   patch -p1 -d src < <OpenOL fork>/tools/outlast-coop/relay-patches/0003-openol-relay-drain-snapshots.patch     # optional, recommended
   cd src && gcc -O2 -c server.c cli.c db.c && g++ -O2 main.cpp server.o cli.o db.o -o OpenOL_Relay.exe -lws2_32   # MinGW
   OpenOL_Relay.exe --port 7777 --trigger-radius 3000
   ```
   Auxiliar: `play\host.ps1 -Relay <OpenOL_Relay.exe>` inicia e exibe endereços ([play/README.md](https://github.com/G3RKA/OpenOL/tree/main/tools/outlast-coop/play/README.md)).
3. Todos: em `OLGame\Config\OLMultiplayer.ini`, definir `IP`, `UdpPort`, `RoomCode` (`PUBLIC`, ou `DEFAULT` integrado), usar Multiplayer > Connect ou iniciar mapa multiplayer por comando. `play\join.ps1 -GameDir <copy> -HostIp <host>` escreve ini com backup. Acrescente `-nosteam` para excluir perfil Steam Cloud.
4. Carreguem mesmo checkpoint manualmente (sem sincronização) e fiquem juntos (gatilhos para todos, salvo filtro).
5. Para duplicatas: aplicar patch nativo em `OLGame.exe` de todos ([exe-patch](https://github.com/G3RKA/OpenOL/tree/main/tools/outlast-coop/exe-patch/README.md)) ou `SyncEnemies=False` em todos (inimigos próprios, não compartilhados).

## <a id="known-issues"></a>Problemas conhecidos

Perceptíveis: conectar silenciosamente sem efeito com sala errada; história disparando longe do jogador; inimigo duplicado perto do primeiro, dando mais dano; checkpoint sem levar parceiro; janela de erro (asserção `UnWorld.cpp`) ao carregar checkpoint de outro grupo pelo F6, também vista num só cliente. Com Start Server integrado, participante tardio não recebe posição de inimigo já presente (E5); independente não tem problema.

## <a id="next-steps"></a>Próximos passos

- OpenOL não recompila sem fontes completas privadas Outlast (NOTES.md, conferência); novas correções nativas vão ao patch como regra de responsável único. Abertos: contexto de gatilho (só próximos) e posição E5 no integrado.
- Só testes de protocolo, não no jogo: coletas, estado de cena matinee, efeito de empurrão remoto. F6 não cria itens (Spawns só Enemies); precisa passagem real na história.
- Verificar duplicatas no progresso normal, não só checkpoints por F6 (precisa New Game).
- Testar Start Server/convites Steam manualmente e dois PCs na internet (`lan_dryrun.py` cobre um PC pelo endereço LAN).
