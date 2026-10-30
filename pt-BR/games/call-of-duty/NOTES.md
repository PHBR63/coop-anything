# <a id="call-of-duty-2003--united-offensive-co-op-notes"></a>Call of Duty (2003) + United Offensive: notas do modo cooperativo

## <a id="game-identity"></a>Identidade do jogo

| | Valor |
|---|---|
| Versão CoD | 1.5 (`version.inf` ExtVersion=1.5, IntVersion=5.3) |
| Versão UO | 1.51 (`version.inf` ExtVersion=1.51, IntVersion=12.4) |
| Motor | IW engine 1 (derivado de id Tech 3); `detect_engine`: "id Tech 3 (or derived)" |
| Idioma | Paks localizados em francês (`localized_french_pak*.pk3`) |

| Arquivo | Carimbo PE |
|---|---|
| CoDSP.exe | 1078214618 (2004-03-02) |
| CoDUOSP.exe | 1093030896 (2004-08-20) |
| gamex86.dll (jogo de um jogador) | 1078214576 |
| uo_gamex86.dll (jogo UO de um jogador) | 1093030666 |

Todos PE32 de 32 bits. Um módulo nativo ainda deve conferir a compilação-alvo antes de aplicar patches; derive essa verificação da cópia do próprio jogador na compilação, em vez de distribuir hashes de uma redistribuição.

### <a id="observations"></a>Observações
- `CoDUOSP.exe` contém seções `stxt774`, `stxt371` (nomes SafeDisc). `CoDSP.exe` não. Desconhecido se o código ainda é criptografado.
- A lógica de um jogador é DLL separada (`gamex86.dll`, `uo_gamex86.dll`), como qagame de Quake 3. Cliente de jogo `cgamex86.dll`, interface `uix86.dll`.
- Arquivos PunkBuster em `pb/` (somente multiplayer). Mantenha distância.

## <a id="design-goals-for-the-mod"></a>Objetivos de projeto do mod
- Primeiro campanha CoD1, depois adaptação a UO. Começar com 2 jogadores, projetar para 4.
- Rede: retransmissão Steam Spacewar (480) por padrão, IP direto + UPnP como alternativa.
- Morte: caído + reviver (como WaW), se possível; alternativa: reaparecer no parceiro após 5 s.
- Progresso: host conduz, próxima missão automática, menu de seleção de fase no host. Sem necessidade de salvar/retomar.
- Escalonar dificuldade: adicional opcional, baixa prioridade.
- Idioma: francês primeiro; aceitar quaisquer paks localizados ou informar o motivo da incompatibilidade.
- Missões de veículos: tentar papéis compartilhados (motorista/artilheiro, escolhidos por menu), espectador como alternativa; decidir por missão.
- Início: idealmente menu interno, executável inicializador como alternativa; diagnóstico claro das falhas.

## <a id="log"></a>Registro

### <a id="2026-10-23-phase-0-2-triage-workspace"></a>2026-10-23 Etapas 0-2: triagem e ambiente
- Coop-anything clonado em 5b86e5b, branch `game/call-of-duty`. Testes MCP: 13 OK (`python -m unittest tools/mcp/test_coop_mcp.py`; com `-I` a importação falha, questão cosmética).
- Instalação de teste = cópia por hardlinks da instalação do jogador (configurações copiadas de verdade).
- Nenhuma issue ou PR CoD1/UO em coop-anything (`gh issue list --search "call of duty"`: apenas indicações de trabalho em MW 2019, MW3, MW2CR).

### <a id="2026-10-23-phase-1-research"></a>2026-10-23 Etapa 1: pesquisa

#### <a id="found-with-sources"></a>Encontrado (com fontes)
| Descoberta | O que realmente é | Licença | Última atividade | Utilidade aqui |
|---|---|---|---|---|
| "CoD 1 Cooperative Mod" | Só um nome em resposta Steam de 2025, sem link ou autor. Não encontrado em ModDB, GitHub ou web russa. | unknown | unknown | Nenhuma até encontrar compilação ([discussão](https://steamcommunity.com/discussions/forum/0/2284960483102477437/)) |
| CoD1 Splitscreen PC v1.1 (ModDB) | ZIP de 318 bytes, inicializador multiplayer em tela dividida, não campanha | Não declarada | 2024-05 | Nenhuma ([página](https://www.moddb.com/downloads/call-of-duty-1-splitscreen-pc-v11)) |
| Workshop 2327804851 | Mod "Call of Duty 2 - Deluxe Edition" para **Men of War: Assault Squad 2**, não CoD | n/a | 2025 | Nenhuma ([página](https://steamcommunity.com/sharedfiles/filedetails/?id=2327804851)) |
| [Clippy95/CoDUO-YAP](https://github.com/Clippy95/CoDUO-YAP) | Plugin UO para um jogador e multiplayer (proxy ddraw.dll ou ASI), SafetyHook/MinHook, cvars, widescreen, hooks no jogo de um jogador. FAQ: NÃO aceita CoD1 (2003). | GPL-3.0 | 2026-10-21 | UO: carregador, estrutura de hooks e endereços conhecidos. Referência de estilo para CoD1. |
| [opencoduo/coduomp](https://github.com/opencoduo/coduomp) | Código reconstruído do cliente **multiplayer** UO, motor servidor, jogo servidor, cgame, ui. 2485 arquivos, sem IA/atores. | **Não declarada** (sem LICENSE) | 2026-10-18 | Referência somente de leitura das estruturas (netchan, snapshot, servidor). Não fazer fork sem autorização do autor. |
| [cod1raph/iw1x-client-r](https://github.com/cod1raph/iw1x-client-r), [xtnded/codextended-client](https://github.com/xtnded/codextended-client), [xtnded/iw1x-server](https://github.com/xtnded/iw1x-server), [Wolf-Pack-Clan/t1x-client](https://github.com/Wolf-Pack-Clan/t1x-client) | Extensões cliente/servidor multiplayer de CoD1 **1.1**. Nossa instalação é 1.5. | iw1x: não declarada; codextended: GPL-3.0 | 2026 | Só multiplayer 1.1; referência de hooks, não de endereços |
| [kungfooman/libcod](https://github.com/kungfooman/libcod) | Extensão de servidor multiplayer CoD1/2/4 | Veja o repositório | 2026-07 | Somente multiplayer |
| [United Fronts](https://www.moddb.com/mods/call-of-duty-united-fronts), Singleplayer Improved | Mods de campanha só para um jogador | | | Nenhuma para rede |
| [games/modern-warfare-2](../modern-warfare-2/README.md) | Mesma família de motor (IW4): cooperativo = código de rede de um jogador + trabalho em scripts | | | Referência de projeto: patches em `level.player` |

#### <a id="observations-binaries-this-install"></a>Observações (binários desta instalação)
- `CoDSP.exe` / `CoDUOSP.exe` não importam WSOCK32/WS2_32; `CoDMP.exe` importa `WSOCK32.dll`. A camada de rede de um jogador ainda contém textos `loopback`, `net_qport`, `NET_CompareAdr`: divisão cliente/servidor Q3, com netchan só por loopback. (Varredura de strings Python, script provisório.)
- DLL `gamex86.dll` contém `G_LoadGame: clientnum out of range`, `getentarray`, funções nativas de scripts.
- Scripts de fases são GSC em texto dentro de pk3 (ZIP): CoD1 tem 809 `.gsc`, 1210 referências `level.player` (maiores: `_loadout` 160, `stalingrad` 119, `dawnville` 106); UO tem 315 `.gsc`, 1916 referências.

#### <a id="derived-not-verified"></a>Deduções (não verificadas)
- Herança Q3: o executável de um jogador provavelmente ainda executa servidor + cliente no mesmo processo por loopback. Adicionar transporte real (UDP / Steam P2P) sob NET por DLL injetada poderia permitir a um segundo CoDSP.exe entrar como cliente puro. O servidor precisa então de mais de uma vaga de cliente no motor e em `gamex86.dll`.
- Scripts cooperativos: pk3 de substituição (`zzz_coop.pk3`) pode substituir `maps/*.gsc`; regra 7 proíbe distribuir scripts do jogo, então distribuir patches aplicados ao pk3 do jogador na instalação.

#### <a id="unknown"></a>Desconhecidos
- Se o código de servidor SP (SV_*, array de clientes) preserva mais de uma vaga ou foi reduzido a uma.
- Se `gamex86.dll` trata cliente 1 (criação, estado, IA mirando alguém diferente de `level.player`).
- Se `CoDUOSP.exe` ainda tem criptografia SafeDisc (seções `stxt774`, `stxt371` presentes).
- Se "CoD 1 Cooperative Mod" existe como compilação em algum lugar.

### <a id="2026-10-23-phase-3-reverse-engineering-ghidra-1212-headless"></a>2026-10-23 Etapa 3: engenharia reversa (Ghidra 12.1.2 sem interface)

Ambiente: projeto `<workspace>/ghidra/CoD.gpr` (CoDSP.exe, gamex86.dll, CoDMP.exe; análise automática padrão, aproximadamente 2 min cada). Scripts de consulta em `<workspace>/ghidra/scripts/` (StrXrefDecomp, DecompAt, RefCount). Chamar `analyzeHeadless` do PowerShell por junção sem espaços: cmd separa argumentos em `,` e `|`. Todos os endereços abaixo correspondem aos hashes de "Identidade do jogo". Os nomes de funções foram atribuídos pelo autor com base em strings e na organização do código Quake 3.

#### <a id="observations-codspexe-image-base-0x400000"></a>Observações: CoDSP.exe (base da imagem 0x400000)
- `SV_Startup` 0x44be90: aloca `svs.clients` = `0x2e1f0` bytes = **4 x client_t (0xb87c)**. Ponteiro em `0x152e8e8`.
- `SV_GetUsercmd` 0x449a10: erro se clientNum < 0 ou > 3.
- `SV_ReadPackets` 0x44ccb0: percorre 4 clientes e compara endereço + qport (`NET_CompareBaseAdr` 0x43efb0), depois `Netchan_Process` 0x43eea0 e `SV_ExecuteClientMessage` 0x4491b0. Pacotes sem conexão (seq -1) vão a 0x44cc00.
- `SV_ConnectionlessPacket` 0x44cc00: reconhece só um comando (comparação textual); caso contrário, exibe "bad connectionless packet".
- `SVC_DirectConnect` 0x448d70: **zera as 4 vagas** e configura somente a 0: estado, netchan com netadr do remetente, buffers `Z_Malloc(0x18000)`, `0x400` x2.
- `NET_SendPacket` 0x43f290: reduzido a copiar por loopback no buffer do outro socket (`0x14f07a0 + (sock^1)*0x200c`). Ignora tipo de endereço, tem **uma vaga de pacote por sentido**, sem sendto. Não importa WSOCK32.
- `NET_AdrToString` 0x43f030: ainda formata `NA_LOOPBACK` (2), `NA_IP` (4) `%i.%i.%i.%i:%i` e IPX. `ntohs` chamado por ponteiro (`0x8cc71c`).
- `Netchan_Transmit` 0x43ed50: máximo 0x4000 bytes, MAX_PACKETLEN 0x1f9b.
- Cliente intacto: `CL_ParseServerMessage`, `svc_gamestate`/`svc_snapshot`/`svc_serverCommand` e "%s:sequenced packet without connection" em `CL_PacketEvent` 0x40dec0.
- `CoDUOSP.exe`: entrada em `.text`, entropia `.text` 6,75 (CoDSP: 6,71). Código não criptografado; `stxt774`/`stxt371` são sobras inertes de SafeDisc nesta compilação.

#### <a id="observations-gamex86dll-image-base-0x20000000-exports-dllentry-vmmain"></a>Observações: gamex86.dll (base 0x20000000, exporta `dllEntry`, `vmMain`)
- `vmMain` 0x2001cd70, ordem Q3: 2 = ClientConnect(n) 0x20014800; 3 = ClientBegin 0x200148d0 (clientNum em EAX, perdido pelo descompilador); 4 = ClientDisconnect 0x20014ca0; 5 = ClientCommand 0x20017ff0; 6 = ClientThink 0x200129c0; 7 = inicialização de mapa/criações 0x2001ed30.
- `ClientConnect` é por cliente: `gclient_t` (0x74e8) em `level.clients` (`0x202db220`) + n*0x74e8, gentity n (0x2c8 cada, `g_entities` por volta de 0x2012fa80) e **um sentient por jogador** (percepção da IA, "No sentient for player").
- `G_LoadGame` 0x2002d980 serializa lista de clientes, limite `clientnum > 4`.
- ~~Singleton do jogador `0x202db224`~~ **Corrigido na segunda passagem:** `0x202db224` é ponteiro `g_entities` (acesso `idx*0x2c8 + base`), não `level.player`.

#### <a id="derived-not-verified-at-runtime"></a>Deduções (não verificadas em execução)
- O motor SP mantém servidor Quake 3 de 4 vagas. Falta: (1) transporte real sob `NET_SendPacket` / recebimento loopback; (2) conexão para vagas 1-3 (`SVC_DirectConnect` fixa vaga 0 e apaga demais); (3) correções das suposições de jogador único: poucas no código nativo (segunda passagem), maioria nos scripts.
- Portanto: cooperativo nativo no código de rede cliente/servidor existente (autoridade do host, capturas Q3), não lockstep. Jogador 2 roda CoDSP.exe normal como cliente puro.
- Esboço: DLL com hooks (proxy ddraw/winmm como CoDUO-YAP) que (a) substitui `NET_SendPacket` e recebimento por fila indexada por netadr: loopback para par local, UDP/Steam P2P remoto; (b) adiciona variante `SVC_DirectConnect` que preenche vaga 1..3 livre sem zerar outras; (c) no cliente, caminho `connect <host>` envia conexão OOB para netadr remoto.

#### <a id="unknown-next-to-check"></a>Desconhecidos (próximas verificações)
- Se `SV_SendClientMessages`, criação de capturas e `SV_Frame` percorrem os 4 clientes ou só vaga 0.
- Se cgame/cliente aceita clientNum != 0 (`cg.clientNum`, índice de playerstate).
- Funções de IA por trás das 32 referências `level.player`: alvos, fogo amigo, gatilhos de jogador visto.
- Mesmas verificações para CoDUOSP.exe / uo_gamex86.dll.

### <a id="2026-10-24-phase-3-pass-2"></a>2026-10-24 Etapa 3, segunda passagem

#### <a id="observations-codspexe-server-send-path"></a>Observações: caminho de envio do servidor CoDSP.exe
- 19 funções usam `svs.clients` (`0x152e8e8`). Maioria percorre as 4 vagas (`while (off < 0x2e1f0)` passo 0xb87c ou `+0x2e1f` dwords): transmissão de configstrings 0x44b900, comandos `SV_SendServerCommand` 0x44caf0, 0x44b710, 0x44c0b0, criação do mapa 0x44c1b0.
- **`SV_SendClientMessages` 0x44da50 envia só ao cliente 0**: `MOV ECX,[0x152e8e8]` depois `CALL 0x44d960`, sem ciclo.
- `SV_SendClientSnapshot` 0x44d960 (cliente em ECX) e `SV_BuildClientSnapshot` 0x44d800 (cliente em EAX) são genéricas. Índice = `(cl - svs.clients)/0xb87c`, playerstate = `gameClients + idx*gameClientSize` (`0x152bc64`, `0x152bc68`), `ps.clientNum` em ps+0x9c conferido `< 0x800`.
- `SV_Frame` 0x44cf10 executa o jogo a 20 Hz (50 ms), depois `SV_SendClientMessages` uma vez por quadro.

#### <a id="observations-cgamex86dll-base-0x30000000-exports-dllentryvmmain"></a>Observações: cgamex86.dll (base 0x30000000, exporta dllEntry/vmMain)
- `CG_Init` 0x3001af80 não recebe clientNum (Q3 multiplayer passa um); confere nome "cod-sp". Cgame lê capturas do motor (`CG_ReadNextSnapshot` 0x30022380, `CG_ProcessSnapshots` 0x30022460). O playerstate de cada captura pertence ao destinatário (lado servidor, acima).
- Não encontrado estaticamente: se cgame trata entidade 0 como "eu" (oculta corpo, usa entidade para visão). Buscar offsets de ps.clientNum gerou ruído demais.

#### <a id="observations-gamex86dll-player-assumptions"></a>Observações: suposições sobre jogadores em gamex86.dll
- Array estático `g_entities` em `0x2012fa80` (0x2c8 cada), `ent->client` em +0x104; `level.num_entities` em `0x202db22c`.
- `G_FreeEntity` 0x20046200 recusa entidades 0..3: **MAX_CLIENTS = 4** também na DLL.
- As 4 funções de "IA" da primeira passagem (0x2006b020, 0x2006dbb0, 0x2006f320, 0x2006fad0) percorrem todas as entidades. Sem supor jogador único.
- Acessos diretos não indexados à entidade 0 (`[0x2012fb84]` = `g_entities[0].client`, ou `MOV reg,0x2012fa80`): **10 funções, 13 instruções** (0x2001df70, 0x2001e110, 0x2001e940, 0x2001f0c0, 0x2002c1b0, 0x2002d980, 0x2002ede0, 0x20045c70, 0x20046090, 0x2004d8b0). Vários são inícios de ciclos. 0x20070f40 também lê origem de `g_entities[0].client` para teste de raio (provável distância de criação ou descarte ao redor do jogador).
- Scripts definem jogador por `getent("player", "classname")`: `maps/_load.gsc:49-50` (`level.player = player`), `animscripts/utility.gsc:570` (`anim.player`) e cópias por mapa (stalingrad, chateau, us_intro...). `getent` dá erro com várias correspondências ("getent used with more than one entity" em gamex86.dll).

#### <a id="derived"></a>Deduções
- Correção do servidor: trocar `SV_SendClientMessages` por ciclo das vagas ativas. Capturas já são por cliente.
- Código nativo é majoritariamente compatível com vários clientes. A suposição de jogador único fica principalmente em GSC.
- Primeiro passo de baixo risco: clientes 1..3 com outro classname (por exemplo, `player_coop`), mantendo `getent("player","classname")` retornando o host. Scripts rodam sem mudanças, com host em `level.player` (World at War faz isso). Depois incorporar jogador 2 script por script (gatilhos, verificações `activator`, objetivos). IA usa sentients (um por cliente), então inimigos já deveriam mirar jogador 2. Exige verificar em execução.

#### <a id="unknown-needs-the-prototype"></a>Desconhecidos (exigem protótipo)
- Cgame com cliente remoto: jogador 2 vê o próprio corpo ou o corpo oculto do host?
- O que 0x20070f40 descarta ao redor do jogador 0 (distância de criação da IA? som?).
- Onde a DLL define classname "player" (ClientSpawn), para inserir hook por cliente.

### <a id="2026-10-24-script-gsc-analysis-cod1-campaign"></a>2026-10-24 Análise de scripts (GSC), campanha CoD1

Método: varredura Python dos `.gsc` dentro de `main/*.pk3` do jogador (ZIP, somente leitura), contando padrões por mapa (todos os `maps/<map>*.gsc`). Somente contagens; nenhum texto de scripts do jogo copiado aqui. Sequências de veículos não foram revisadas linha por linha; a classificação abaixo é aproximada.

#### <a id="campaign-order-observed-missionsuccess--changelevel-targets-in-each-maps-scripts"></a>Ordem da campanha (observada: destinos `missionsuccess` / `changelevel` nos scripts de cada mapa)
training → us_intro (briefing) → pathfinder → burnville → dawnville → carride → brecourt → us_mid (briefing) → chateau →
powcamp → uk_6ab (briefing) → pegasusnight → pegasusday → uk_sas (briefing) → dam → truckride → airfield → ship →
ru_stalingrad (briefing) → stalingrad → redsquare → trainstation → sewer → pavlov → factory → railyard →
tankdrivecountry → tankdrivetown → allied_start (briefing) → hurtgen → rocket → berlin. `credits` é separado.
Mapas de briefing têm 0 referências `level.player` e chamam `getent("player","classname")` uma vez.

#### <a id="per-map-counts-observed"></a>Contagens por mapa (observadas)
| Mapa | Linhas de scripts | `level.player` | Esperas de gatilho | Comparações de jogador | Chamadas de armas | Chamadas de postura | Vida/dano | Seguir jogador | Termos de veículos | Termos de torres | Chamadas de objetivos |
|---|---|---|---|---|---|---|---|---|---|---|---|
| training | 2117 | 19 | 28 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 34 |
| pathfinder | 2969 | 33 | 25 | 0 | 5 | 8 | 1 | 6 | 32 | 1 | 15 |
| burnville | 2773 | 65 | 30 | 2 | 0 | 0 | 6 | 6 | 7 | 25 | 11 |
| dawnville | 4582 | 106 | 38 | 3 | 3 | 4 | 11 | 26 | 22 | 28 | 45 |
| carride | 2457 | 61 | 26 | 0 | 3 | 12 | 6 | 2 | 76 | 13 | 13 |
| brecourt | 2224 | 32 | 19 | 2 | 0 | 0 | 2 | 13 | 0 | 3 | 24 |
| chateau | 1982 | 19 | 20 | 0 | 0 | 0 | 1 | 11 | 9 | 0 | 17 |
| powcamp | 876 | 7 | 9 | 0 | 0 | 2 | 0 | 1 | 9 | 0 | 10 |
| pegasusnight | 3444 | 76 | 8 | 2 | 8 | 12 | 12 | 2 | 19 | 29 | 23 |
| pegasusday | 3574 | 43 | 1 | 3 | 0 | 7 | 8 | 2 | 34 | 20 | 27 |
| dam | 986 | 9 | 21 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 5 |
| truckride | 1381 | 28 | 21 | 0 | 10 | 0 | 0 | 0 | 41 | 0 | 8 |
| airfield | 1101 | 26 | 8 | 0 | 7 | 0 | 2 | 0 | 77 | 4 | 7 |
| ship | 1240 | 5 | 14 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 29 |
| stalingrad | 15532 | 119 | 40 | 3 | 3 | 4 | 13 | 0 | 70 | 74 | 12 |
| redsquare | 3140 | 54 | 16 | 0 | 0 | 5 | 2 | 3 | 4 | 16 | 17 |
| trainstation | 132 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| sewer | 335 | 4 | 7 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 3 |
| pavlov | 4035 | 72 | 6 | 0 | 0 | 0 | 13 | 11 | 102 | 22 | 44 |
| factory | 950 | 7 | 12 | 0 | 0 | 0 | 0 | 3 | 6 | 0 | 3 |
| railyard | 467 | 10 | 7 | 1 | 2 | 0 | 0 | 1 | 4 | 0 | 5 |
| tankdrivecountry | 343 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 3 |
| tankdrivetown | 372 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 15 |
| hurtgen | 1008 | 17 | 7 | 0 | 0 | 0 | 2 | 3 | 6 | 19 | 5 |
| rocket | 588 | 12 | 11 | 0 | 0 | 0 | 0 | 2 | 13 | 0 | 10 |
| berlin | 1090 | 23 | 13 | 0 | 0 | 0 | 0 | 3 | 12 | 12 | 9 |

Termos são contados por regexes simples ("termos de veículos" corresponde a qualquer linha com funções nativas relacionadas ou a palavra "vehicle"); trate como indicador de tamanho, não uso exato.

Bibliotecas compartilhadas com mais referências ao jogador: `_loadout` 160, `_load` 53, `_spawner` 24, `_mg42` 21, `_truckridewaters` 18, `_shellshock` 15, `_mortar` 9, `_tankdrive` 7, `_utility` 7, `_tankmg42` 5, `_vehiclechase` 5, `_autosave` 4. `animscripts/utility.gsc` mantém seu próprio `anim.player`.

#### <a id="mission-types-derived-from-the-vehicle-libraries-each-map-calls-coarse"></a>Tipos de missão (deduzidos das bibliotecas de veículos chamadas; aproximados)
- **Jogador dirige tanque:** tankdrivecountry, tankdrivetown (`_tankdrive`); railyard também chama `_tankdrive`.
- **Perseguição / transporte em veículo:** carride, truckride, airfield (`_vehiclechase`, `_truckridewaters`); dam (`_truckridewaters`).
- **Barco:** ship; travessia de stalingrad (também o script mais longo, 15,5 mil linhas).
- **Artilharia antiaérea:** pegasusnight, pegasusday, brecourt, hurtgen, tankdrivecountry, tankdrivetown (`_flak`).
- **Infantaria, metralhadoras fixas (`_mg42`, `_scripted`):** burnville, brecourt, stalingrad.
- **Principalmente infantaria simples:** chateau, powcamp, trainstation, sewer, factory, rocket, berlin, hurtgen, redsquare, pavlov, dawnville (os três últimos ainda têm tanques e torres de IA perto do jogador).

#### <a id="plan-for-player-2-derived-nothing-implemented-or-tested"></a>Plano para jogador 2 (deduzido; nada implementado ou testado)
1. **Manter host em `level.player`.** Scripts compartilhados (`_load`, `_loadout`, `animscripts/utility`) e chamadas `getent("player","classname")` por mapa esperam exatamente uma correspondência. Outros jogadores precisam de outro classname. Scripts rodam como em um jogador, com host como jogador da missão, igual ao modo cooperativo de World at War.
2. **Primeiro a camada de bibliotecas** (uma mudança cobre todos os mapas): `_loadout` (mesmas armas e munição para jogador 2), `_load` (criar ao lado do host, salvamento automático e checkpoints), `_spawner`/`_mg42` (alvos da IA e torres ao redor de "o" jogador), `_shellshock` (efeitos só no atingido), `_autosave` (host decide).
3. **Gatilhos:** mais de 400 esperas `"trigger"` na campanha. Onde se espera `level.player` tocando um gatilho, qualquer jogador deve contar. Ordem: dawnville (38 esperas, 16 verificações `istouching`), stalingrad (40), burnville (30), training (28), carride (26), pathfinder (25).
4. **IA amigável seguindo jogador** (`setgoalentity(level.player)`, cadeias amigáveis): dawnville 26, brecourt 13, chateau 11, pavlov 11. Host como líder primeiro; depois seguir o mais próximo.
5. **Morte e reviver:** estado caído com reviver como meta; reaparecer perto do parceiro após 5 s como alternativa (escolha de projeto). Ambos caídos = recarregar último checkpoint. Exige mudanças `_load`/`_autosave` e hook de vida por jogador.
6. **Missões de veículos:** primeiro jogador 2 espectador (alternativa). Depois tentar papéis compartilhados onde houver segundo assento ou arma. Decidir por missão: tankdrivecountry, tankdrivetown, railyard, carride, truckride, airfield, dam, ship, travessia de stalingrad.
7. **Ordem de esforço (menor primeiro) para primeira execução jogável:** trainstation, sewer, factory, powcamp, rocket, chateau; depois grandes (dawnville, pavlov, stalingrad, pegasusnight).

#### <a id="unknown-1"></a>Desconhecidos
- Como cada sequência de veículo prende o jogador: revisão linha a linha não feita.
- Se scripts ou motor recusam ou se comportam mal com segundo cliente: exige parte nativa ainda não concluída.
- UO (`uo/*.pk3`, 315 scripts, 1916 referências `level.player`): ainda sem análise por mapa.
