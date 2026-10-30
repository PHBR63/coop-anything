# <a id="fallout-tactics-working-notes"></a>Fallout Tactics: notas de trabalho

Objetivo: jogar a campanha de um jogador em cooperativo com amigos.

## <a id="identity"></a>Identidade
GOG, v1.27, BOS.exe SHA-256 C5B91FE56EF8DE118CE22CCD5E6512F217CA16C8B8758EA14C626229EB5A4E40, Windows.
Engine: proprietária (Micro Forte / 14 Degrees East). Inclui o editor oficial (FT Tools.exe, v1.26).

## <a id="observations-2026-10-20"></a>Observações (2026-10-20)
- O diretório e games/ não tinham entrada para Fallout Tactics. `gh` não instalado, portanto issues/PRs ainda não verificados.
- Modos de combate (core/locale/gui/gui_text.txt 306–313): Continuous Turn-Based (CTB, padrão; AP recarregam
  com o tempo, todos agem ao mesmo tempo), Individual turn-based, Squad turn-based.
- Multijogador integrado: Skirmish, Assault, Capture the Flag, Scavengers (readme.txt). CTB e os
  modos por turnos existem no MP (Patch Readme.txt menciona correções de "turnbased multiplayer").
- O testador joga CTB. Alvo cooperativo: CTB primeiro; Individual/Squad por turnos depois (exigem ordem de turnos entre humanos). Salvar é desativado no
  multijogador (notas 1.25 de Patch Readme.txt: "Disabled save in multiplayer").
- Mapas MP ficam como arquivos soltos em `core/missions/<mode>/*.mis`. Mapas da campanha também existem soltos em
  `core/campaigns/missions/core/` (bunker01.mis, mission01.mis ...). Outros podem estar empacotados em arquivos .bos (desconhecido).
- FTSE (Fallout Tactics Scripting Engine): https://github.com/melindil/FTSE, MIT, v0.60a (2026-03-27).
  Modifica BOS.exe para carregar uma DLL com Lua, gatilhos de eventos do jogo, edições hexadecimais configuráveis. Instala substituindo
  binkw32.dll. Suporte multijogador não mencionado. Versões de executável suportadas: desconhecidas.

## <a id="prior-co-op-attempts-none-found-with-a-download"></a>Tentativas cooperativas anteriores (nenhuma encontrada com download)
- Mod cooperativo do clã TBC, por volta de 2003: criaturas de IA controladas por um jogador "battlemaster (bughandler)". Fonte: tópico TTLG
  https://www.ttlg.com/forums/showthread.php?t=49006 (403 ao obter; visto apenas pelo resumo da busca).
- "The COOP Mod" no NMA: mapas SP originais, até 6 jogadores, autor disse 40% concluído. https://www.nma-fallout.com/threads/the-coop-mod.165469/
  (403 ao obter; apenas resumo da busca). Status: desconhecido, presumir abandonado.
- Mapa cooperativo NMA que copia uma missão de campanha: 2 jogadores contra mutantes de IA; iniciar sozinho encerra o jogo imediatamente
  porque não existe humano adversário. Fonte: resumo de busca do tópico NMA "Playing multiplayer alone?".
- Tutorial GameSAS: copiar mapas SP para a pasta MP, aliar slots de jogadores; o autor nunca terminou. Apenas resumo de busca.
- Tópicos Steam (2014, 2022): não existe cooperativo na campanha. https://steamcommunity.com/app/38420/discussions/0/45350791308582171

## <a id="setup-2026-10-20"></a>Configuração (2026-10-20)
- O autor escolheu: campanha completa em cooperativo, 3–4 jogadores.
- Cópia de teste em `local/test-install/` (robocopy, 364 arquivos, 1,572 GB; hash do BOS.exe copiado corresponde).
- FTSE 0.60a: SHA-256 do zip de lançamento 8731b3fdd962ffc53d8191c4c41950489ba932b0eef612e367a735e82613bc9d
  (corresponde ao digest do lançamento GitHub). Desde 0.60a, carrega por um wrapper binkw32.dll, então BOS.exe
  fica intacto. Seu realBinkw32.dll é idêntico byte a byte ao binkw32.dll GOG.
- Teste inicial: cópia iniciada, ainda executando após 12 s, FTSE.log criado (vazio). O texto de versão FTSE no
  menu principal ainda não foi conferido visualmente.
- Busca no repositório hub (API GitHub, "tactics"): 0 issues/PRs. Ninguém assumiu o jogo.
- Pontos de integração Lua FTSE (da documentação incluída): OnStart, OnLocaleLoad, OnLongTick, OnRadiated, OnVariableChanged
  (variáveis de missão + campanha), OnChanceToHitCalc, OnChanceToCritical1/2, OnCriticalEffect1/2, OnDamageCalc,
  On{Straight,Area,Radial,Spray,Cone,Burst,Projectile}Attack, OnInventoryAdd/Remove, OnCheckItemAllowed,
  OnCheckEquip/OnEquip/OnCheckUnequip/OnUnequip. Mais chamada/interceptação de vtable Entity, classe `world`,
  classes de entidades incluindo Actor, Inventory, Door, Switch. Sem pontos de integração multijogador ou rede.

## <a id="reverse-engineering-session-1-2026-10-20"></a>Engenharia reversa, sessão 1 (2026-10-20)
Build: GOG 1.27 BOS.exe (SHA-256 acima). Ferramentas: REA (Ghidra 12.1.4), descompilação completa headless Ghidra,
leitores PE próprios em Python stdlib. Dumps em `local/re/` (não publicados). Base da imagem 0x400000,
.text 0x401000–0x7fc000, .rdata 0x7fc000, .data 0x894000. Caminho PDB incorporado "BOS Milestone.pdb" (sem PDB incluído).

Observado (leitura estática de código descompilado, ainda não executado):
- Imports não têm Winsock/DirectPlay. A rede é DirectPlay por COM (ole32): strings
  `net_initCOM`, `net_initDPlay`, `net_initDPLobby`, `DPNetwork`.
- Classes RTTI e vtables: Network 0x8336c0, DPNetwork 0x833714, DPTCPNetwork 0x832aa4,
  NullNetwork 0x83366c, XNetwork 0x825298 (tipo de exceção), Server 0x825260, NetworkServer 0x82527c,
  Client 0x824ec0, NetworkClient 0x825230, Player 0x80942c, CampaignMission 0x82cb6c,
  WCampaignMain 0x82cde0, WMultiSetup 0x805228, WSingleMain 0x807868, WMainMenu 0x82e060, WGameMain 0x801ac8.
- 0x7570d0 = construtor NullNetwork (0x30 bytes). 0x724400 = alocar NullNetwork e registrá-la.
- 0x7288d0 = alocar DPTCPNetwork (0xac bytes).
- 0x724550 = gerenciador de rede: adicionar rede à lista (manager+8 início da lista, +0xc contagem). Lança XNetwork se nula.
  Se a sessão já começou (+0x10), chama imediatamente vtable+0x2c (iniciar) da nova rede.
- 0x7244c0 = iniciar sessão(name, int param_2, string param_3): define flag de iniciada (+0x10), armazena param_2
  em +0x19, chama vtable+0x2c em cada rede registrada.
- 0x636bd0 = **início de um jogador**: cria objeto de 0xfb bytes via 0x63eb70 (armazenado em this+0x248),
  copia para ele 0x58 bytes de configuração de 0x8bd9c0 em +0x31, registra apenas NullNetwork, inicia a
  sessão "SinglePlayer" com param_2 = 1.
- 0x4a9a20 = **host multijogador** (após diálogo retornar 4): mesmo objeto 0xfb e cópia de configuração, registra
  NullNetwork **e** DPTCPNetwork, inicia sessão com param_2 de 0x6d0630.
- 0x637cf0 = outro caminho que registra NullNetwork mais uma rede recebida (entrada/lobby?), desconhecido.
- Notas FTSE: 0x4e8280 carrega uma missão ou .sav (início da campanha, recarga de área). O fim da fase serializa
  primeiro as entidades do grupo do jogador, depois a fase.

- Versão DirectPlay: **DirectPlay 4** (o executável contém CLSID_DirectPlay, CLSID_DirectPlayLobby, IID_IDirectPlay4/4A,
  IID_IDirectPlayLobby3A, DPSPGUID_TCPIP, DPSPGUID_IPX; sem GUIDs DirectPlay 8). O PC de teste tem dplayx.dll,
  dpwsockx.dll, dpnet.dll em SysWOW64 (datadas de 2025-06-11); uso em execução ainda não testado.
- Vtable Network: 20 slots (0x00–0x4c). Slots 6–19 da Network base são `0x7a2eae` (provavelmente _purecall), então
  6–19 são a interface de transporte. DPTCPNetwork substitui apenas slots 2 (destrutor) e 9 de DPNetwork.
  Implementações NullNetwork: 6 0x757e00, 7 0x757e10, 8 0x757e20, 9 0x757140, 10 0x757560, 11 0x757150, 12 0x757270,
  13 0x7574b0, 14 0x757570, 15 0x757820, 16 0x757900, 17 0x757850, 18 0x757e50, 19 0x757b80.
  - Slot 9 (0x24) chama slot 10 e depois define flag aberta (+0x18)=1; slot 10 (0x28) chama slot 13 e a limpa.
    (Nomes de 9/10/13 ainda incertos: par iniciar/parar.)
  - Slot 17 (0x44), 0x757850 = consultar: retirar uma mensagem da fila (fila +0x20, contagem +0x24); tipo short em +8:
    0 = dados -> listener(+0x28)->vtable[0x10](buf, len, sender), caso contrário mensagem de sistema -> 0x757b40.
  - Slot 15 (0x3c), 0x757820 recebe os mesmos (name, int, string) do início de sessão (o gerenciador chama +0x2c... conferir).
  NullNetwork é uma fila de mensagens em loopback: as classes Network só movem buffers de bytes entre listeners Server
  e Client.
- Deduzido: uma subclasse Network personalizada (vtable própria, transporte moderno) poderia transportar as próprias mensagens do jogo.

### <a id="session-1b-protocol-static-reading"></a>Sessão 1b: protocolo (leitura estática)
Nota de ferramentas: a análise automática Ghidra não encontrou 3.037 funções alcançáveis apenas por vtables (incluindo todos os
métodos Server/Client/NullNetwork). Corrigido varrendo todas as vtables RTTI (662 classes, 4.685 destinos de slots)
e criando funções nos destinos ausentes com um script headless (3.027 criadas). Lição para o playbook.
Além disso: awk compara endereços hexadecimais como `0063e640` como números (notação científica); forçar comparação de strings.

- Vtable Server 0x825260 (6 slots); slot 4, 0x63dbb0 = despacho de recebimento por tipo de mensagem (dword em +0).
  Vtable Client 0x824ec0; slot 4, 0x6321a0 = despacho de recebimento. Client tem vtables extras em +9, +25.
- Server recebe: 2 = comandos do jogador (0x63dce0, valida propriedade, ver abaixo), 4 = 0x63c3b0,
  100 = registro de configuração do jogador com 0x37 bytes (0x63e120), 0xcc = nome/string, define client+10 (0x63df00),
  0xcd = define client+0xb (0x63e010), 0xcf = cliente informa dessincronização, define client+0xe (0x63e050),
  300/301/302 = retransmissão de chat (0x63e1a0; 301 e outros escolhem destinatários, flag de equipe).
- Client recebe: 1 (0x633bd0), 3 (0x633ab0, registro com id +0x10 e array: checksums?), 200 = versão errada,
  0xc9 = violento demais (configuração de gore), 0xca = expulso, 0xcb = 0x6327f0 (define +0x24c "em jogo"?),
  0xcc = lote de comandos por tick (0x632840; frames em +0x1d7..+0x1db, entradas de 16 bytes),
  0xce = 0x632c50, 0xcf = texto "out_of_sync" / "my_out_of_sync" (0x632c90), 300–302 = chat (formata `<+p>`).
- Server 0x63e640 empacota blobs de comandos enfileirados por cliente em um 0xcc e transmite via 0x724840.
- Client 0x6363b0 compara duas listas de registros por id (+0x10), elemento por elemento; na divergência chama 0x634770,
  que envia {0xcf, client id (+0x130)} ao servidor.
- **Verificação de propriedade na mensagem 2**: global World `DAT_008bc564`; tabela de entidades em World+0x743 (entradas de 8 bytes,
  short de geração em +6); entity+0x163 = índice do jogador proprietário; array Player em World+0x733, passo 0x15d;
  Player+0x2d = id do cliente de rede. Comando só aceito se Player+0x2d == remetente.

Deduzido (alta confiança, ainda estático): o código de rede é **lockstep determinístico**: o servidor retransmite
comandos de jogadores, toda máquina simula o mundo completo (IA, scripts), e checksums detectam dessincronização.
Um jogador passa pelo mesmo caminho Server/Client via NullNetwork.

Implicações para cooperativo na campanha (deduzidas):
1. Toda máquina precisa iniciar uma missão em estado idêntico (missão, variáveis de campanha, esquadrão, inventário,
   RNG). Plano natural: host envia seu save aos clientes, todos carregam e depois entram em lockstep.
2. Tudo que muda estado sem passar pelo fluxo de comandos dessincroniza. Suspeitos: diálogo,
   troca, recrutamento, intendente do bunker, viagem no mapa mundial (nada disso existe no MP). Verificar se a
   interface SP emite isso como comandos.
3. Entrada no meio da missão precisa de transferência de estado completo; entrar no início / via save é muito mais simples.
4. A detecção de dessincronização integrada é um presente para QA automatizado.
5. Controle do esquadrão = definir entity+0x163 para o registro Player do jogador que entra.

- Comando lockstep = ControllerCommandStruct do FTSE {u8 type, u16 action_entity_halfid, EntityID e1,
  Vector3 loc, EntityID e2, i32 param}, aplicado pelo slot 510 da vtable de entidade, ActOnControllerCommand.
  Actor (vtable 0x80c1d0), slot 510 = 0x5747e0, ~36 casos (0x00–0x25). Casos com strings indicativas:
  0x01 RobotScurry, 0x06 equip, 0x07 unEquip, 0x18/0x19 steal, 0x20 overwatch, 0x25 disembark/sneak.
  Controller (0x80a778), slot 510 = 0x50fe60. Significados dos demais casos: desconhecidos.
- Nenhum comando de conversar/trocar/recrutar encontrado por string. Botões de fala (notas FTSE: barter 0x4d0000,
  gamble 0x4d0090, recruit 0x4d0110) só são alcançados por ponteiro de função; 0x4d0090 define globais e
  abre janela de interface 7. Se alteram estado fora do fluxo de comandos: **desconhecido**.
- Cadeia de ferramentas no PC de teste: VS 2022 Professional/Community + Build Tools 2022 (builds x86 possíveis).

Próximo experimento (em execução): DLL na cópia de teste que registra todo envio NullNetwork (tipo de mensagem e
tipo de comando para mensagem 2) durante um jogador. Ações que mudam estado sem mensagem = risco de dessincronização.

### <a id="runtime-run-1-2026-10-20-the-tester-played-the-test-copy-first-campaign-mission"></a>Execução 1 (2026-10-20, testador jogou a cópia de teste, primeira missão da campanha)
Logger: `netlog.dll` (código próprio, local/src/ftcoop/logger), carregado pelo script de usuário FTSE core/FTSE/ftse.lua via
`package.loadlib("netlog.dll","*")`. Modifica slot 4 da vtable Server (0x825270) e slot 4 da vtable Client
(0x824ed0) após verificar bytes do prólogo do executável. Tecla de marcador = scan code 0x29 (à esquerda de "1"), funciona em qualquer
layout; MessageBeep é inaudível enquanto o jogo roda. Log bruto: local/re/netlog_run1.txt.
Nota FTSE: uma instalação nova FTSE 0.60a registra "Error loading LUA scripts ... module 'FTSE.ftse' not found"
até core/FTSE/ftse.lua existir; o erro aborta o restante de init.lua (instalações de interceptações após a linha 176).

Observado:
- **Um jogador executa a sessão lockstep completa via NullNetwork** (confirmado em execução).
  Handshake inicial: C->S 0x64 (59 bytes), S->C 0xc9 (358/413 bytes, configurações), 0xc8 (16), 0xcb (8),
  C->S 0xcc (12), S->C 0xcc (20), C->S 0xcd, S->C 0xce. Depois tick S->C tipo 1 a cada ~280 ms com
  contador de sequência (+4 por tick); um tick com comando tem 32 + 27*n bytes.
- C->S tipo 2 = `{u32 type=2, u16 count, count x 27-byte ControllerCommandStruct}`.
- Tipos de comando vistos (significado pelo momento dos marcadores do testador; "?" = não confirmado):
  0x00 mover (loc = ponto alvo; movimento de esquadrão = um registro por ator), 0x02 agir sobre/atacar alvo e1,
  0x04 usar/abrir alvo e1 (cadáver, também forma próprio+item), 0x06 equipar (e2 = item), 0x0b ? (param 8/0, postura?),
  0x0c ? (entidade e2, param 782), 0x12 ? (entidade e2, param 6), 0x14 pegar item do inventário alvo
  (e1 = contêiner/cadáver, e2 = item, param = quantidade), 0x17 conversar? (e1 NPC, param 6), 0x21 fechar
  inventário/transferir? (param 5).
- Id do remetente nesta execução: 58282272 (cliente único).
- O jogo caiu enquanto o testador mudava para uma resolução muito alta. Sem evento de crash Windows, netlog não mostra
  nada incomum antes. Provavelmente a conhecida fragilidade de resolução de FoT, não o logger: desconhecido.

Não coberto nesta execução: troca, bunker (intendente, recrutamento), viagem no mapa mundial, fim/transição de missão, salvar/carregar.


### <a id="runtime-run-2-2026-10-20-the-tester-played-raw-log-localrenetlog_run2txt"></a>Execução 2 (2026-10-20, testador jogou; log bruto local/re/netlog_run2.txt)
- Testador: marcadores 6 e 7 = **comprar e vender** (troca). O log mostra **nenhuma mensagem** nos
  marcadores 6 e 7. Observado: troca muda inventários sem mensagem de sessão nem comando.
  Deduzido: no cooperativo lockstep isso dessincroniza; troca precisa virar mensagem sincronizada.
- Marcador 4: um **segundo início completo de sessão** (0xc9, 0xcb com 0x0210, 0xcc, 0xcd, 0xce) logo após movimento
  de esquadrão no marcador 3. Ação do testador: ainda não confirmada (saída de missão / bunker / carregamento?).
- Novo comando 0x15 visto com 0x04 -> 0x15 -> 0x21 (abrir, transferir, fechar; contêiner?). Significado: desconhecido.
- Testador: marcador 9 = clicar numa nova missão do intendente (NPC do bunker). Log: exatamente um
  comando 0x17 logo após marcador 9. Com 0x17 também após marcadores 2, 5, 8: **0x17 = conversar / interagir
  com NPC** (provavelmente). Iniciar conversa é comando sincronizado.
- Testador: marcadores 10–13 = **salvar e depois sair**. Sair também não enviou mensagem (sessão SP). Sem mensagens: esperado, salvar grava arquivo e não
  muda o estado do mundo. Deduzido: em lockstep, toda máquina mantém o mesmo estado, então salvar pode ser
  exclusivo do host (ou de todos) sem trabalho de sincronização.
- Seleção de missão após conversar com intendente: nenhuma mensagem separada vista entre marcadores 9 e
  10, mas o testador não viajou nem iniciou a missão nesta execução. Sincronizado ou não: desconhecido.

### <a id="runtime-run-3-2026-10-20-the-tester-played-raw-log-localrenetlog_run3txt"></a>Execução 3 (2026-10-20, testador jogou; log bruto local/re/netlog_run3.txt)
- Marcador 1 = **carregar save**: handshake completo de início de sessão (0x64 ... 0xce), igual ao início de missão.
- Marcadores 2–3 = **recrutar** 3 personagens (esquadrão 3 -> 6) no bunker: **nenhuma mensagem**. Não sincronizado.
- Marcador 5 = **entrar no mapa mundial**: reinício completo de sessão (0xc9 aos 92 s ... 0xce aos 101 s).
- Marcador 6 = pressionar iniciar para aceitar a missão no mapa mundial: nenhuma mensagem. Marcador 7: não informado.
- Marcador 4 da execução 2 (reinício de sessão após movimento do esquadrão) corresponde a sair da missão para o bunker.

Deduzido: toda mudança de mapa (missão, bunker, mapa mundial) e todo carregamento de save inicia uma **sessão nova**.
São pontos naturais de sincronização: o host pode entregar a todos os clientes estado idêntico (seu save) antes de cada
sessão iniciar. Entre eles, as ações não sincronizadas encontradas até agora são troca e recrutamento.

Resumo. Sincronizado: mover, atacar, usar/abrir, equipar, saquear/transferir, conversar (início). Não sincronizado, precisa virar
mensagem cooperativa: troca, recrutamento, aceitar missão no mapa mundial (provavelmente funciona se exclusivo do host mais a
próxima sincronização de sessão). Sem necessidade de sincronização: salvar, sair. Ainda não visto: escolhas de diálogo além do
primeiro clique, requisição de equipamento ao intendente (pode ser semelhante a troca), veículos, modos por turnos.

### <a id="single-instance"></a>Instância única
- 0x72ee90 (caminho WinMain): `CreateMutexA(NULL, TRUE, "Fallout Tactics")`; se GetLastError() == 0xb7
  (ERROR_ALREADY_EXISTS), fecha o handle e retorna 0 (saída silenciosa). Única verificação encontrada: sem
  import FindWindow. Correção pela lição 21 do playbook: neutralizar dentro do processo antes de WinMain (wrapper binkw32
  carrega na importação, então um fork FTSE pode modificar a entrada IAT 0x7fc180 ou a comparação).

### <a id="two-copies-on-one-pc-done-2026-10-20"></a>Duas cópias em um PC (concluído em 2026-10-20)
- Patch na configuração personalizada FTSE `core/FTSE/FTSE_config.json`: deslocamento 0x72eeb4 `75` -> `eb` (jnz -> jmp após
  comparação ERROR_ALREADY_EXISTS). FTSE aplica patches em seu desvio WinMain antes da WinMain real.
  Verificado: FTSE.log "Applying patch Allow multiple instances", ambas as cópias continuam executando.
- Segunda cópia necessária de qualquer forma: ambas as instâncias compartilhariam core/user/$$current$$ (save temporário) e logs.
- Jogo apenas em tela cheia; alt-tab entre duas cópias em tela cheia é pouco confiável (o testador viu fechar).
  Correção: cnc-ddraw v7.1.0.0 (https://github.com/FunkyFr3sh/cnc-ddraw/releases/tag/v7.1.0.0, MIT),
  cnc-ddraw.zip 2.688.079 bytes, SHA-256 0B13AB89A64C9918189B1DADD449EF6ED3CB3B7B19CABD96D8ADBD95505BB908
  (GitHub não publica digest; hash registrado no download). ddraw.ini tem um perfil integrado `[BOS/2]`
  (hook_peekmessage=true). Definir windowed=true, savesettings=0, posX por cópia. Verificado: duas janelas
  lado a lado (retângulos (-7,2)–(647,520) e (649,2)–(1303,520)).

### <a id="live-experiment-1-a-second-copy-joins-a-single-player-session-2026-10-20"></a>Experimento ao vivo 1: segunda cópia entra numa sessão de um jogador (2026-10-20)
Configuração: host = cópia de teste 1 com save carregado; atalho netlog Ctrl+marcador executa na thread principal (da
interceptação de recebimento Client): Server = Client+0x248 (vtable verificada 0x825260), Server+0x19 máximo de jogadores 1 -> 5,
`net = 0x7288d0()` (fábrica DPTCPNetwork, sem argumentos, ret), `0x724550(server, net)` (AddNetwork, thiscall, ret 4).
Participante = cópia de teste 2, Multiplayer -> TCP/IP -> entrar em 127.0.0.1.
Observado:
- `host: AddNetwork returned, TCP network attached`. Participante **vê a sessão** e conecta.
- Participante envia registros de configuração de jogador 0x64 (nome "Unnamed"); servidor host responde com lista 0xc9, que cresce
  413 -> 468 bytes (+0x37 = mais um registro de jogador). Alternar Ready reenvia 0x64; servidor confirma.
- Participante fica no lobby MP: o servidor nunca lhe envia 0xcb (iniciar).
- Estático, mesma sessão: Server+0x19 é DPSESSIONDESC2.dwMaxPlayers (0x758bc0 monta a descrição, deslocamento 0x28,
  depois IDirectPlay4A::Open (+0x60) com DPOPEN_CREATE). Montador de lista 0xc9 0x63e3a0: configurações do servidor
  (0x58 bytes de Server+0x31), string de 0x103 caracteres, flag de jogo em andamento (Server+0xa5), N registros de 0x37.
- **0xcb = iniciar + semente RNG**: 0x63e5c0 semente = LCG de time(0) (0x7a2f3f), enviada como {0xcb, seed} a cada
  registro de jogador com present(+8), connected(+0xf), ready(+0xd). Chamador 0x63f0b0 = StartGame(force):
  sem force lança net_playersReady se um jogador conectado não estiver pronto (+9); define +0xa5, marca jogadores prontos
  como em jogo (+0xd), retransmite lista, envia semente. Chamadores: 0x484850 (botão Start do lobby MP),
  0x63aab0 (StartGame(1); sem chamador direto, alcançado por ponteiro; provavelmente início automático SP).
- Bug corrigido após a execução: GetAsyncKeyState é global, então o atalho disparava nas duas cópias. Agora só com foco.

Deduzido: não basta enviar 0xcb a quem chega tarde: uma semente nova (e o mundo/RNG já avançados do host)
significa dessincronização imediata. A entrada precisa ocorrer **no início de sessão**: host retém StartGame até participantes estarem
prontos, toda máquina inicia com o mesmo save e a mesma semente.

### <a id="live-experiment-2-hold-the-single-player-start-joiner-via-mp-browser-2026-10-20"></a>Experimento ao vivo 2: reter início de um jogador, participante pelo navegador MP (2026-10-20)
- Fluxo SP Load 0x637ab0(Client*, FOTString file): 0x636bd0 (sessão), Client+0x13a = file, Server+0x2d = file,
  depois modal WDummyGameSetup (vtable 0x825074; +0xfa Client, +0xfe Server); resultado 4 -> 0x638260.
  Slot 48 de WDummyGameSetup (0x825134 -> 0x63aab0) é Update por quadro (chamado pelo tick da janela 0x6c5130,
  slot 70) = `mov ecx,[ecx+0xfe]; StartGame(1)` em try/catch. Interceptado: host conecta TCP no primeiro quadro
  e retém o início até Ctrl+marcador.
- Handler Client 0xc9 0x6324d0 atribui Client+0x13a da string de lista (msg+0x5c) (`lea ecx,[ebp+0x13a]`),
  copia 0x58 configurações para Client+0x14a; handler 0xcb grava semente em Client+0x14a.
- Carregamento de fase Client 0x636de0: carregador 0x4e8280(Client+0x13a, ...), depois 0x4f4d90(Client+0x14a configurações/semente).
- Registros de jogador Server (node+8): byte0 presente, byte1 pronto (participante 0 -> 1 ao Ready), byte7 conectado,
  nome em +0xc ("Unnamed", participante "Unnamed(1)").
Observado: host retido, participante entrou e ficou pronto, Ctrl+marcador enviou semente 0xcb 0x7d16 a ambos. Cliente do host
enviou 0xcc (carregado), mas servidor não enviou 0xcc/0xcd/0xce: espera todo cliente carregar. Participante
entrou na seleção de esquadrão MP ("select operators") e caiu após escolher (sem evento de crash Windows).
Deduzido: o fluxo do cliente MP é o caminho errado para um save. Próximo: participante também usa fluxo SP Load.

API de rede Client (base NetworkClient em Client+0: +4 rede, +8 conectado): SetNetwork 0x728640
(limpa antiga via 0x7286e0: net[0x28] fechar, net[4] liberar; abre nova via net\[0x24](address)), Connect
0x728790 -> net[0x30](FOTString* password, session record*, client), GetSessions 0x728710 -> net\[0x38](vector*).
DPNetwork: EnumSessions slot 14 0x7599d0 (síncrono; vetor de registros de 0x85 bytes, guidInstance em +0x25),
Join slot 12 0x758580 -> 0x7591d0 (DPSESSIONDESC2 do GUID do registro, IDirectPlay4A::Open DPOPEN_JOIN).
SendPlayerInfo 0x6347a0 envia 0x64 de Client+0x103. FOTString(char*, codepage [0x82ea44]) 0x6c8bf0.

### <a id="live-experiment-4-both-sides-use-the-sp-load-flow-2026-10-20"></a>Experimento ao vivo 4: ambos os lados usam fluxo SP Load (2026-10-20)
Modo participante (ftcoop.ini mode=join): no primeiro quadro de WDummyGameSetup, SetNetwork(DPTCP, "127.0.0.1"),
GetSessions (0 na primeira tentativa, 1 dois segundos depois), Connect(password "", sessions[0]),
SendPlayerInfo. Nunca chama o Update original.
Observado: participante conectou, recebeu 0xcb (mesma semente 0x437f do host), **carregou o mesmo mapa**. Ambos os clientes
enviaram C->S 0xcc ({0xcc, player id, 0}: host 1, participante 2); servidor enviou S->C 0xcc com 2 entradas
{len 8: {1,0}}, {len 8: {2,0}}. Host caiu ao tratar; participante mostrou o mapa sem unidades e
não recebeu mais nada (sem 0xcd/0xce, sem ticks).
Estático: handler S->C 0xcc 0x632840 -> criação da missão 0x637050 ("mission_spawn"). Para cada registro de jogador
(lista Client+0x142, id em record+0x2d), chama World::SpawnPlayer 0x4f4fb0 (thiscall ECX=World, (rec, spawn,
a, b), ret 0x10). Chamada do passo 1 em 0x637202: dados de criação = *0x8bdd2c (campanha) + 0x5d quando 0x6a2270() é false
(SP), senão os próprios dados 0xcc do jogador. Portanto, o **esquadrão da campanha também foi criado para o jogador 2**.
Passos 2/3 (0x6373ad, 0x6373fd, ...) tentam novamente jogadores que falharam com seus próprios dados; "Player %d %s was refused
spawning" -> mission_spawnpl.
Correção: local de chamada 0x637202 redirecionado: jogadores com id diferente de 1 recebem lista de criação vazia
({flag 0, sentinela std::list (nó de 12 bytes, next=prev=self), contagem 0}, como montada em 0x63722e).

### <a id="live-experiments-5-10-into-the-same-mission-in-sync-2026-10-20"></a>Experimentos ao vivo 5–10: na mesma missão, sincronizados (2026-10-20)
- Criação vazia para jogador 2 retorna 0: World::SpawnPlayer 0x4f4fb0 atribui equipe. Byte +8 do registro == 1 e
  SP (World+0x7c9 == 0) -> equipe 1, senão 0x4f6fc0 encontra equipe (falha num save SP). Índice do slot
  World Player == equipe (World+0x733 + team*0x15d); slot já usado (+4) -> lança exceção. A ramificação SP então encontra a primeira
  entidade com +0x163 == 1, define câmera do slot, retorna 1. Portanto, dois humanos não compartilham slot 1 nativamente.
  Correção: interceptação de criação retorna 1 para jogador != 1 sem criar (participante = espectador da equipe 1).
- Participante então caiu no início: EXCEPTION c0000005 eip 0x4df6e4 (grupo "obter enésimo membro vivo",
  lê [this+0x4f], this = 0). Chamador WGameMain 0x476dc0 obteve o grupo do "jogador local" da interface 0x65af20:
  em cache em ui+0xfe, senão slot com Player+0x31 == Client(ui+0xfa)+0x130 (próprio id). Participante id 2 não tem slot.
  Correção: 0x65af20 reimplementada (jmp na entrada): sem correspondência + participante cooperativo -> slot 1.
- Participante então carregou com posições corretas, mas seu mundo nunca se moveu. Processador de ticks Client 0x635e00 executa
  ticks só enquanto a condição 0x635ce0 é verdadeira; após o frame Client+0x251, a condição exige
  GetPlayerById(próprio id) 0x50b880 (thiscall, ret 4: slot com Player+0x31 == id) != 0. Correção: apenas a chamada
  em 0x635dbe redirecionada (participante -> slot 1). Não a função: "jogador saiu" 0x4f4e10 remove o slot que
  obtém (0x4e0bc0, limpa +0x2d), então uma alternativa ali excluiria o esquadrão do host.
- **Observado (exp. 10): host e participante na mesma missão, unidades do participante acompanham movimentos do host.
  Ambos processaram os mesmos 16 ticks de comandos, 0 mensagens de dessincronização (0xcf), nenhuma exceção.**
- Comandos do participante (6, de seu id de rede) chegaram ao servidor e foram descartados (propriedade: Player[slot]+0x2d
  != remetente). Correção (exp. 11): ServerRecvHook do host repassa comandos cooperativos msg-2 com remetente = id
  de rede do proprietário do slot 1 (Player[1]+0x2d) -> esquadrão compartilhado.
- Log de crashes: handler de exceções vetorizadas em netlog registra código, EIP, registradores e endereços de retorno
  BOS.exe na pilha (antigos também; a primeira entrada é a mais confiável).

### <a id="milestone-exp-11-2026-10-20-two-player-campaign-co-op-shared-squad"></a>Marco (exp. 11, 2026-10-20): campanha cooperativa para dois, esquadrão compartilhado
Configuração: duas cópias num PC (TCP loopback, DirectPlay 4 pela própria DPTCPNetwork do jogo), ambas carregam o
mesmo save SP ("New Save Game", idêntico byte a byte em ambas); host retém início, Ctrl+marcador inicia.
Observado (testador jogou ambas as janelas): **ambos os jogadores controlam todos os membros do esquadrão de qualquer janela**.
Logs: 5 comandos de cada remetente, os do participante repassados como proprietário do esquadrão; ambas as cópias processaram os mesmos 10
ticks de comandos, última sequência de tick idêntica em ambas, 0 dessincronização (0xcf), 0 exceções.
Nível QA disso: teste manual, uma missão, poucos minutos. Ainda não automatizado.


### <a id="automated-two-copy-test-2026-10-20"></a>Teste automatizado de duas cópias (2026-10-20)
Bot em netlog.dll, ativado com ftcoop.ini [test] enabled=1; inicializador local/src/ftcoop/test/run_test.py.
- Ignorar vídeos iniciais: DAT_008bddbf ("introdução exibida nesta sessão", definido pela playlist de introdução 0x6c1890) = 1 antes do
  construtor do menu principal 0x6bff50, que de outra forma agenda temporizador de 1 ms -> 0x6c0970 -> 0x6c1890 (intro.bik + ss00.bik).
- Carregar sem menus: Ctrl+L do menu principal (WMainMenu slot 55 0x6c0ba0) define DAT_008bdda9 = 1 e chama 0x6c0970:
  caminho "user/save/" + locale mission_quickSaveFile + ".sav" -> 0x6c2540(*0x8bddb8, FOTString*, 0, 0) (cdecl).
  Chamar 0x6c2540 do Update de WMainMenu (slot 48, vtable 0x82e060, no-op compartilhado 0x401d20) **travou**: o carregamento
  executa um jogo inteiro dentro do tick da janela. O loop de mensagens do jogo 0x784920 consulta sua própria janela e passa cada mensagem
  para 0x7857f0 (thiscall(app, hwnd, msg, wp, lp, time), ret 0x14) **sem DispatchMessage** (uma subclasse WndProc
  nunca vê mensagens enviadas). Correção: interceptar essa chamada (0x7849cc), Update envia WM_APP+0x51, o carregamento roda pelo loop de mensagens.
- Passos do bot em quadros exatos: loop de frames do mundo 0x4fbf50 chama processador de ticks Client 0x635e00 em 0x4fc0db uma vez por quadro,
  depois passo do mundo 0x4fc230, depois World+0x2eb++. Chamada interceptada = passo do bot por quadro.
- Esquadrão = lista de membros World Player[1] em +0x4b (std::list {next, prev, EntityID{u16 seq, u16 id}}), tabela de entidades
  World+0x743 ({ptr, i16, i16 seq}), posição float[3] em entity+0x9a, HP de Actor em +0x281 (layouts FTSE).
- Comando de movimento enviado como mensagem 2 (33 bytes, cmd 0, id do ator, xyz alvo, param 4) via envio Client 0x728840
  (thiscall(client, msg, len, reliable), ret 0xc). Alvo = posição do membro mais distante do esquadrão.
- Janela em segundo plano: menu não avançou sem foco; noactivateapp=true de cnc-ddraw não resolveu
  (o foco do testador pode ter ajudado na execução aprovada). Questão aberta.
Resultado: host_move 16/16 PASS (logs local/re/test_runs/20261020-165823_host_move): mesmo primeiro frame 39 em ambos,
snapshots A e B do esquadrão de 6 idênticos, unidade movida 922 percorreu 2,29 em ambos, 0 dessincronização, saída limpa.
Ainda não executado: join_move, mutação (share_squad=0) para join_move.

Condições de corrida encontradas pelo bot (um início humano é mais lento e geralmente não as encontra):
1. Cache obsoleto do jogador local da interface: ambas as cópias caíram em 0x49f61b/0x49f62f (0x49f600, centralizar câmera no esquadrão) lendo
   a lista de membros de memória liberada. 0x65af20 guarda o slot em ui+0xfe; o array de jogadores World é reconstruído durante
   o carregamento da fase. Correção: a 0x65af20 reimplementada sempre varre novamente e atualiza o cache.
2. "Todos carregados" dividido: participante reenvia configuração de jogador (0x64) logo após StartGame; handler 0x63e120 copia
   o registro de 0x37 bytes sobre node+8.., zerando o byte de em jogo node+0xd. Se esse 0x64 chegar antes dos dois informes 0xcc,
   a verificação de todos carregados 0x63e090 (espera jogadores presentes+conectados+em jogo com node+10 carregado == 0)
   ignora o participante, e o servidor envia dois S->C 0xcc de uma entrada. Cada cliente então executa criação da missão duas vezes;
   na segunda, jogador 1 não tem entrada, segue o caminho sem dados (chamada 0x637256, não interceptada), e
   SpawnPlayer lança XRuntime (0x4f51ab); o jogo então cai no tratamento de erro (o título redesenha para sempre).
   Evidência: execução 20261020-170452 (0x64 em 10,360 antes de ambos 0xcc em 10,641) contra aprovada 20261020-170144 (0x64 em
   10,546 após 0xcc do host em 10,515). Correção: host mantém node+0xd num 0x64 de jogador já em jogo.
Suíte (2026-10-20, após ambas as correções, cronograma do bot reduzido para snapshot B em +200 frames, ~22 s por teste):
`python -I local/src/ftcoop/test/run_suite.py`
```
ok   host_move: expected PASS, got PASS  (host_move, 16/16 checks)
ok   join_move: expected PASS, got PASS  (join_move, 16/16 checks)
ok   join_move without shared-squad fix (mutation): expected FAIL, got FAIL  (join_move-mutated, 15/16 checks)
SUITE: PASS
```
A mutação falha apenas em "moved unit travelled > 1.0" (0,00 em ambas), então join_move testa a correção.
host_move também passou em 3/3 execuções consecutivas antes da mudança de cronograma; a correção da corrida 0x64 disparou em todas.
Escopo deste QA: um save, uma missão, duas cópias num PC via loopback, esquadrão compartilhado, CTB.
Testador: a primeira caminhada (até o colega mais distante, 3 unidades, moveu 2,29) foi invisível. Agora o alvo é um
Actor fora do esquadrão, a 10–30 unidades, mesma altura de piso (|dy| < 1); limite 8,0; snapshot B em +400 frames.
Suíte reexecutada: host_move PASS (moveu 23,86 em ambos), join_move PASS, mutação FAIL como esperado -> SUITE: PASS.
O testador acompanhou e confirmou que a unidade caminhou visivelmente.

Bot de cenários (bot_scenarios.inc, [test] scenario=move|simul|attack|soak), oráculo do mapa inteiro: posição e HP
de cada Actor a cada 50 frames, todos os frames compartilhados comparados.
- host_move PASS (8 frames, 440 estados de atores idênticos, moveu 23,81), simul PASS (unidade do host 22,40, unidade do participante
  20,85, mesmo frame), attack PASS (cmd 0x02, e1 = {seq, id}; alvo 70 hp 10 -> -5, 550 estados idênticos).
  Cópias de teste ainda executam Lua de invencibilidade/acerto garantido (idêntico nas duas).
- Soak v1 ficou quase ocioso (o testador percebeu): alvos de caminhada eram personagens vivos a 10–30 unidades; após algumas caminhadas
  nenhum se qualificava, e a maioria das rodadas registrou bot: FAIL. Frames comparados (80 até frame ~4000) todos corresponderam.
  Correção (compilada, AINDA NÃO executada): pontos de passagem = posição de cada Actor no primeiro frame, faixa 10–40 unidades, mais uma
  verificação soak de que o esquadrão andou uma distância total mínima.
- Soak v2 PASS: 1.200 frames (10 movimentos, 259,5 unidades, 1.320 estados idênticos) e 4.000 frames (34 movimentos, 921,9
  unidades caminhadas, 80 frames x 55 atores = 4.400 estados idênticos, 0 dessincronização, saídas limpas).

### <a id="save-transfer-2026-10-20"></a>Transferência de save (2026-10-20)
- Um save não é carregado por nome no início da sessão. Client+0x13a permaneceu 0x8af7e4 (FOTString vazia compartilhada do jogo)
  durante a lista 0xc9 até o carregamento da fase, o campo de arquivo da lista (msg+0x5c) está vazio, e Server+0x2d
  está vazio no lobby. Carregar save preenche user/$$current$$, e a fase carrega dali. Então a transferência
  precisa ocorrer antes de o participante carregar qualquer coisa.
- 0x6c2540 (carregamento direto) chama verificação de save 0x4c1290(file) (thiscall, ret 4; abre o arquivo 0x6d4b50 e
  verifica o cabeçalho) em 0x6c260e antes do início da sessão. Interceptado nos dois lados: host registra o arquivo.
- Host serve o save registrado na porta TCP 47701 ([coop] file_port): solicitação "GET\n", resposta
  "FTCOOP1 <size> <name>\n" + bytes. Participante busca no menu principal, grava core\user\save\ftcoop_received.sav,
  depois carrega esse arquivo pelo mesmo caminho de carregamento rápido. [coop] fetch_save=0 desativa.
- Teste fetch_save: bot do participante configurado com QuickSave (pré-condição: difere de New Save Game do host)
  e ainda precisa terminar idêntico. PASS 19/19: 700.953 bytes enviados, arquivo recebido idêntico byte a byte, participante o carregou,
  ambos primeiro frame 39, 440 estados idênticos, moveu 25,36 em ambos.
  Mutação (--mutate-fetch): FAIL como exigido: participante iniciou no frame 10117 (linha do tempo do QuickSave), 0 frames
  compartilhados, participante esgotou o tempo.
- Limites: só o caminho do menu principal do bot busca (um participante humano precisa de tecla ou botão no menu); chamadas de socket
  bloqueantes com timeout de 10 s na thread principal; sem testes NAT ou internet.
- Bug do harness encontrado: interromper o inicializador deixava arquivos de teste ftcoop.ini nas cópias, e a execução seguinte fazia
  backup deles como "originais". Inicializador agora restaura configurações normais se um backup contém [test].

Suíte após transferência: 7 testes (host_move, join_move, mutação join, simul, attack, fetch_save, mutação fetch)
-> SUITE: PASS.
Bug de desempenho encontrado: como a busca do jogador local da interface varre a cada chamada, sua linha de log "compartilhando slot 1" era gravada
em todas (28.000 linhas descarregadas em segundos, participante ficou lento). Agora registra uma vez por id.

### <a id="map-transitions-2026-10-20-in-progress"></a>Transições de mapa (2026-10-20, em andamento)
- Fim de missão é uma ação de gatilho: ActionEndMission (vtable 0x82b2e0), slot 15 = executar 0x680b60 (fastcall,
  lê sua FOTString alvo em +0xb; "World Map" define temporizador de saída WGameMain(DAT_008bc384)+0x19d/0x19e).
  ActionMissionComplete (0x82bc14), slot 15 = 0x68a460: marca a missão concluída (0x6a84e0) e chama vtable
  de entidade+0x358(1) para cada membro do esquadrão do jogador local da interface (0x65af20) **dentro da simulação**: a alternativa
  do slot 1 do participante mantém isso idêntico nas duas cópias. Slots 4/6 são descrição e nome do editor.
- Cenário de teste=transition: ambos os bots chamam 0x680b60("World Map") no mesmo frame. Observado: ambas abrem o
  mapa mundial localmente (classes de janela WCampaignWindow 0x82d2a8, WWorldWindow 0x82db04, WMissionItem, WListBox), sem
  nova sessão: mapa mundial é interface local, não sessão. (Classes registradas por tick de janela reimplementado
  0x6c5130 que anota cada classe RTTI no primeiro tick.)
- Mapa mundial: construtor WCampaignWindow 0x6b4cc0 (+0xfa client); handler de teclas slot 55 0x6b6650: Esc 0x6b5cd0, Ctrl+S
  salvar rápido 0x6b5ee0, Ctrl+L carregar rápido 0x6b6360, diálogos Alt+S/Alt+L. Carregamento rápido atribui a global
  FOTString "arquivo a carregar" DAT_008bddb4 (mov ecx,0x8bddb4; call 0x6c8e80) e fecha a janela com
  vtable+0x34(0x10). WWorldWindow slot 51 (mouse pressionado) 0x6ba2a0: sobre um local -> 0x6ba580 (missão), senão
  0x6ba410 (destino de viagem; viagem passa o tempo, encontros aleatórios -> não lockstep).
- Projeto deduzido (proposta): ressincronizar por save a cada início de missão. Host carrega sozinho a missão escolhida, então no
  primeiro frame salva e carrega rápido (caminho de primeira entrada: lobby espera, arquivo servido, participante busca e
  carrega); participante, ocioso no mapa mundial, vê nova geração de save do host, busca, define
  DAT_008bddb4 e fecha seu mapa com 0x10. O mesmo fluxo permite entrar no meio da partida e torna desnecessária a
  sincronização de troca e recrutamento (só ocorrem onde o host manda; participante é realinhado a cada início).

### <a id="re-sync-by-save-built-2026-10-20-the-author-chose-this-design"></a>Ressincronização por save (compilada em 2026-10-20; autor escolheu este projeto)
- Carregamentos terminam no loop superior 0x6bf6a0: após uma sessão, lê FOTString "arquivo a carregar" 0x8bddb4 e
  chama 0x6c2540(file), então todo carregamento rápido passa pela verificação de save e LoadCheckHook (nova geração).
- Teclas na missão (keys.cfg): Alt+S {quickSave}, Alt+L {quickLoad}, Ctrl+S/L {save}/{load}; despacho de comandos
  0x4734f0: quickSave -> 0x478340, quickLoad -> 0x478860, reload -> 0x478150 (todos métodos WGameMain; WGameMain*
  em DAT_008bc384). quickLoad atribui 0x8bddb4 e fecha a tela com vtable+0x38(0x10); não faz nada enquanto
  WGameMain+0x15c != 0, uma contagem regressiva que vale 100 logo após salvar rápido (quickSave também recusa nesse período).
- Host: lobby só é cooperativo (TCP, retenção, servir) quando há carregamento pendente; qualquer outra sessão inicia sozinha e
  ressincroniza após 0xce: salvar rápido, esperar QuickSave.sav ser gravado e +0x15c == 0, carregar rápido (nova geração).
  Canal lateral responde "GEN" com a geração; participante consulta a cada 2 s numa thread de fundo.
- Participante: slot 3 da vtable Client (sessão perdida 0x632080 -> limpar rede 0x7286e0, mostrar net_lostSession) substituído em
  modo de entrada cooperativa: só limpar a rede (o diálogo de erro parava os ticks da tela da missão, então ela nunca
  acompanhava). Pelo tick da janela, numa geração mais nova: buscar, atribuir 0x8bddb4, fechar mapa mundial
  (vtable WCampaignWindow+0x34) ou missão (vtable WGameMain+0x38) com 0x10.
- Bugs encontrados: (1) o segundo lobby do host reutilizava o endereço do primeiro Server, então "novo lobby" (ponteiro
  mudado) não era detectado: sem TCP, participante achava 0 sessões. Correção: esquecer o lobby a cada início de sessão. (2) a
  ressincronização "tentar novamente se ainda na missão 100 frames após carregar rápido" disparava em toda sessão nova: 4 ressincronizações seguidas
  (cada uma acompanhada corretamente). Correção: início de sessão encerra ressincronização.
- Teste resync: bot do host solicita ressincronização no frame 60 da sessão 1; ambos jogam 300 frames na sessão 2.
  PASS 18/18: geração 2 servida (702.246 bytes), participante acompanhou a partir da missão, 2 conexões, 7 frames de snapshot
  (1 + 6) com 385 estados de atores idênticos, saídas limpas. Mutação: [coop] follow=0 (--mutate-follow).
- QuickSave.sav do host é sobrescrito a cada ressincronização (slot de salvamento rápido do jogo). Questão aberta: slot próprio.
- Mapa mundial -> missão (mudança real de mapa) ainda não testado: precisa de bot iniciar missão de WWorldWindow
  (0x6ba580 num local) e participante acompanhar de WCampaignWindow.

Próximo (nota antiga): executar soak v2 e suíte de 5 testes, depois transferência de save (projeto: servidor de arquivos host numa porta TCP lateral serve
arquivo de Server+0x2d; participante baixa antes de conectar e regrava o nome de arquivo da lista 0xc9 para sua cópia local).

Diagnósticos adicionados: nomes de tipos de exceções C++ (ThrowInfo -> CatchableTypeArray -> TypeDescriptor), EIP da thread principal e
pilha no timeout do watchdog, texto das janelas deste processo (diálogos de erro) no timeout.
Lições do harness: encerrar também o loop do inicializador, não só os jogos (um foreach PowerShell iniciava a próxima execução e
redefinia logs); o participante afinal não precisava de foco (uma leitura inicial de log foi confundida com paralisação).


### <a id="co-op-design-that-follows-from-the-evidence-proposal-not-built"></a>Projeto cooperativo decorrente das evidências (proposta, não implementado)
1. Missões em lockstep; cada jogador possui alguns membros do esquadrão (entity+0x163 -> seu registro Player).
2. Só o host executa a camada de campanha (bunker, recrutamento, intendente, mapa mundial); outros esperam/observam.
3. A cada início de sessão (mudança de mapa, carregamento), host envia seu save para toda máquina começar idêntica.
4. Troca dentro da missão vira mensagem cooperativa (ou exclusiva do host mais ressincronização na próxima transição).
5. Transporte: subclasse Network própria num fork FTSE (transporte moderno, sem dependência DirectPlay).

Hipótese (a testar, não um fato): um jogador executa como servidor + cliente local via NullNetwork, então
cooperativo na campanha pode ser "registrar uma DPTCPNetwork na sessão SinglePlayer e deixar clientes entrarem",
mais dar aos clientes participantes controle de membros do esquadrão.

## <a id="derived"></a>Deduções
- A engine tem código de rede para esquadrões, IA e ambos os modos de combate, então replicação existe. O que falta no MP é
  a camada de campanha: bunker, esquadrão/inventário/XP persistentes entre missões, recrutas, instruções de missão, saves.

## <a id="unknown"></a>Desconhecidos
- Se scripts/gatilhos das missões de campanha executam corretamente numa sessão MP.
- Se FTSE funciona com o executável GOG 1.27 e no MP.
- Onde o estado da campanha (lista do esquadrão, inventário, progresso de missão) fica na memória/saves.

## <a id="world-map---mission-transition-2026-10-20"></a>Transição mapa mundial -> missão (2026-10-20)

Fluxo que agora funciona (teste `transition`, 19/19): ambas as cópias terminam missão 1 (ActionEndMission "World Map"), host
escolhe um local no mapa mundial, inicia essa missão sozinho, ressincroniza por salvar/carregar rápido (geração 2), e
participante, ainda no mapa mundial, busca geração 2, fecha o mapa com 0x10, carrega e entra no
lobby do host. Estados da geração 2 idênticos nas duas cópias.

Bugs encontrados e corrigidos no caminho (observados em logs de teste):

1. **Participante entrou num lobby antigo.** Uma janela de lobby antiga voltou a receber ticks quando o mapa mundial do participante abriu, e
   ele entrou no próximo lobby do host sem carregar o novo save. Correção: lobby de participante só pode entrar depois de o
   próprio participante começar a carregar o save do host (`g_join_pending`).
2. **Início solo da missão do host travou.** Mapa mundial -> missão reinicia o jogo no mesmo Server, cujos registros
   ainda listam participante como conectado. O StartGame forçado `0x63f0b0` (`__thiscall(Server*, char force)`, `ret 4`)
   então esperava para sempre o 0xcc do participante. Um início não forçado lançava `XNetwork` (net_playersReady) a cada quadro,
   porque as flags de pronto são redefinidas após missão. Correção: marcar todo outro jogador como não conectado (`node+0xf = 0`)
   e executar o início forçado original.
3. **Mundo do participante congelou na sessão seguinte.** No mapa mundial, ainda recebia mensagens de início solo
   do host para a sessão antiga (início fantasma), deixando a flag go do cliente `+0x24d = 0`. Sua condição
   de tick `0x635ce0` nunca abria (`started=1/0`, frame 0). Correção: participante ignora mensagens S->C da sessão antiga
   enquanto no mapa mundial, até acompanhar.
4. **Participante voltou ao mapa mundial cerca de 1 s após entrar na missão.** A tela da missão era fechada (resultado 16)
   por `0x47a680`, a verificação "esquadrão inteiro numa grade de saída". Percorre unidades do jogador local da interface
   (`0x65af20`) e retorna na primeira unidade fora da saída. O save do host continha registro de jogador com
   id do participante e **nenhuma unidade**, então participante era resolvido para esse slot vazio, e um esquadrão vazio contava como "todos
   na saída". Correção: participante cooperativo com esquadrão compartilhado sempre usa slot 1 em `0x65af20`.

Notas RE: `0x825074` (vtable) é a janela de carregamento (seu run, slot 11, retorna 4 ao carregar), não a
missão. A tela da missão é WGameMain (vtable `0x801ac8`, slot de fechar 14 em `0x6c6260`). Ghidra não encontrou
`0x47a2e0` e `0x47a680`; criá-las manualmente. Loop de campanha é `0x638fc0` (mapa mundial quando a string de próximo mapa
em `*(0x8bdd2c)+0x10` está vazia, caso contrário missão).

Testes executados após a última mudança: transition 19/19, join_move 15/15, resync 18/18. Suíte completa ainda não reexecutada.

## <a id="connecting-the-multiplayer-menu-and-drop-in-join-2026-10-21"></a>Conexão: menu Multiplayer e entrada em andamento (2026-10-21)

Escolha do autor: usar o próprio menu Multiplayer e ignorar lobby de mata-mata no cooperativo; jogadores podem entrar num
jogo já em andamento.

Como funciona agora:

- **Menu Multiplayer.** WMultiSetup (construtor `0x4a84a0`, vtable `0x805228`) é mostrado pelo loop multijogador
  `0x637720`, executado pelo botão Multiplayer do menu principal (`0x6c1ba0` -> `0x6c0c10(1)`: novo Client, depois
  loop superior aninhado). Com o mod, **Host** (`0x4a9a20`) e **Join** (`0x4a9820`) são
  substituídos por interceptações jmp (`[coop] mp_menu=0` mantém originais). Definem papel e fecham tela com resultado 2;
  qualquer valor diferente de 4 retorna de `0x637720` ao menu principal. Join lê campo IP da tela (FOTString,
  larga, em +0x135; nome de host resolvido para IPv4) e campo de nome (+0x139).
- **Host:** após Host, carregar save ou iniciar campanha normalmente. O host joga imediatamente; não há lobby de espera.
- **Participante:** após Join, o menu principal fica aberto até o host reter um lobby cooperativo; então busca o
  save do host e carrega.
- **Entrada em andamento.** A cada 2 s, cada participante consulta `GEN <id> <name>`. Resposta `GEN <gen> <lobby> <save>`. Um participante
  registrado após início da sessão do host o faz ressincronizar (salvar rápido, carregar rápido, nova geração,
  lobby cooperativo). Lobby inicia quando todo participante ativo (consultou nos últimos 6 s) estiver pronto, ou após 30 s.
- **Interceptações.** Todas instaladas no início e só agem após definir um papel; `[coop] mode=host|join` ainda define
  papel na inicialização para testes.

Handlers originais, para referência: Host abre WCreateServerBox (`0x4aa890`: nome, senha, máximo de clientes; OK retorna 4),
depois monta rede DirectPlay e Server (`0x63eb70`), copia configurações de `0x8bd9c0` e fecha a
tela com 4. O loop então executa lobby de mata-mata WGameSetup (`0x482540`) e jogo (`0x638260`).

Testes (ambas as cópias sem som: `core/bos.cfg` `sound.masterVolume` definido como 0 apenas nas cópias de teste):
- `menu_join`: 17/17. Ambas pressionam Multiplayer, depois Host ou Join pelos handlers reais, começando com modo cooperativo desativado.
- `dropin`: 20/20. Host joga sozinho; participante inicia 10 s depois, entra pelo menu; host ressincroniza
  como geração 2; ambos movem unidades na geração 2; todos os estados idênticos.

Ainda não verificado por teste: se o botão Join real pode ser clicado sem sessão selecionada na lista (bot
chama handler diretamente) e o que o participante vê enquanto espera (nada mostrado ainda, só log).

## <a id="drop-in-hardening-quicksave-guard-notices-2026-10-21"></a>Robustez de entrada em andamento, proteção QuickSave, avisos (2026-10-21)

Encontrado pela suíte completa (execução isolada de entrada havia passado): sob carga, servidor de arquivos do host de thread única
paralisava as consultas de 2 segundos do participante por 20 s ou mais. Host o considerava ausente, iniciava lobby sem
ele, depois o contava como recém-chegado a cada retorno e ressincronizava em loop (gerações 2, 3, 4). Participante também
caiu uma vez nessas reentradas repetidas, violação de acesso numa DLL de sistema após exceção C++. Pode ser consequência
do loop; não foi investigada mais.

Mudanças:

- Servidor de arquivos: uma thread por conexão.
- Consultas informam estado do participante, `GEN <id> <W|L|P> <gen> <name>`: W espera no menu, L carregado ou no
  lobby, P jogando. Host ressincroniza só quando participante ativo informa W numa consulta após início da sessão atual,
  ou informa L após 15 s numa sessão iniciada sem ele. No máximo uma ressincronização por participante a cada 20 s;
  participantes contam como ativos por 15 s após última consulta.
- Proteção QuickSave: antes de salvar rápido para ressincronizar, `QuickSave.sav` do host é copiado para
  `ftcoop_quicksave_backup.sav`. Save de ressincronização servido como `ftcoop_resync.sav`. No próximo início de sessão,
  original é restaurado, ou o save rápido da ressincronização é excluído se host não tinha um. Backup restante é restaurado ao
  iniciar o jogo.
- Avisos na linha de chat do jogo, via Client::ShowChat `0x6330a0` (`__thiscall(Client*, int player, FOTString*
  text, char team)`, `ret 0xc`, usado pelo handler de saída de jogador `0x6361f0`): "<name> entrou durante a sessão — salvando e
  recarregando para incluí-lo", "<name> saiu", "Co-op: N jogador(es) neste jogo" e "Co-op: no jogo do host" para
  participantes. `0x6602b0` é caixa OK modal (wmisc_gui.cpp), então não é usada para avisos no jogo.
- Botão Join: WMultiSetup habilita Join só enquanto uma sessão listada está selecionada (`0x4a9cd0`: lista em +0x125, botão
  em +0x131, `0x6d1350(widget, enabled)`, flag em widget+0x102). No cooperativo, mod o mantém habilitado, pois um
  host cooperativo não lista sessão até reter lobby.

Suíte completa antes destas mudanças: 11 de 12 como esperado (todo teste PASS passou, toda mutação falhou); dropin falhou
como descrito acima.

## <a id="four-players-2026-10-21"></a>Quatro jogadores (2026-10-21)

Existem quatro cópias de teste (`local/test-install`, `-2`, `-3`, `-4`; cópias 3 e 4 clonadas da 2), com
janelas em grade 2x2 definidas por posX/posY de `ddraw.ini`. A opção `--joiners 1..3` inicia cópias extras, e
cada participante recebe `[test] index=N`, então em `simul` o participante N dá ordens ao membro N do esquadrão.

- Execução 1 (`simul --joiners 3`): 28/29. Todos os quatro conectaram, e as quatro ordens simultâneas sincronizaram. **Uma divergência:**
  raider 101 tinha 33 HP no host e nos participantes 2 e 3 no frame 439, mas 21 no participante 1. A própria verificação
  de dessincronização (0xcf) não disparou. Se o testador tocou a janela do participante 1 durante a execução: desconhecido.
- Adicionado no modo de teste: linha `HPCHG s= f= id= old->new` para cada alteração de HP de ator, todo frame.
- Execução 2 (mesmo teste, sem entrada): 29/29. As quatro cópias registraram as mesmas 8 mudanças de HP nos mesmos frames: raiders 66,
  70 e 100 morrem, e 101 é atingido nos frames 338 e 440.

O testador confirmou depois que ninguém tocou o participante 1 na execução 1, então a divergência é não determinismo real,
não entrada.

- Execução 3 (`soak --joiners 3 --soak-frames 2000`): bots esgotaram o tempo, porque quatro cópias num PC rodam a cerca de 5 frames
  por segundo (código 3, timeout 300 s). Até o timeout, estado aleatório World (World+0x729, registrado a cada frame como
  `RNG s= f= v=`) foi idêntico nas quatro por 1477 frames, e os 29 snapshots corresponderam.
- RE: `0x505b00` retorna estado aleatório World: `&World+0x729`, ou, enquanto flag `0x8bdd8b` definida, uma semente redefinida
  para o número do frame (World+0x2eb). A semente é gravada nos saves (`0x4eaed0` / `0x4eb470`). O jogo a usa
  inline com LCG MS (`x * 0x343fd + 0x269ec3`); 88 chamadores. Uma interceptação registrando sorteios fora do processador
  de ticks do cliente encontrou cerca de 50 chamadores, mas são a própria atualização World (em torno de `0x4fc2xx`), executada ao lado
  da chamada interceptada, e não dentro dela. Não é bug; interceptação removida.
- Aberto: divergência da execução 1 não reapareceu. Linhas RNG e HPCHG por frame continuam no modo de teste, e o
  inicializador compara RNG frame a frame para todo participante, então a próxima ocorrência mostrará o primeiro frame.

## <a id="menu-flow-as-built-waiting-message-bunker-screens-2026-10-21"></a>Fluxo de menu implementado, mensagem de espera, telas do bunker (2026-10-21)

O fluxo desejado pelo autor está implementado e foi conferido pelo testador com cliques reais:

- Host: Multiplayer, depois **Start Co-op**, depois tela Load Game.
  - Start Co-op é novo botão em (280, 390) em WMultiSetup, adicionado envolvendo a chamada de construtor da tela
    (`0x637767` -> `0x4a84a0`).
  - Anatomia do botão: alocar 0x15b com `0x6c4dd0`. Criar callback com `0x4ac1d0(owner, &tmp, handler, 0)`.
    Construir com `0x65bcb0(button, parent, int pos[2], callback, FOTString* text, style)`, `ret 0x14`. Depois
    cancelar registro do callback temporário com `0x6c7d40(owner, &tmp)`.
  - **Handlers são `__thiscall(owner, int arg)` com `ret 4`.** Despachante em `0x7053ea` empilha um argumento.
    Handler que retorna com `ret` simples causa crash num clique real; bot não detectou porque chamava
    handlers diretamente. Agora chama por ponteiro `__thiscall(owner, arg)`.
  - A tela Load Game vem do handler Load de Single Player, `0x4ca7b0(parent)`.
- Participante: Multiplayer, selecionar "[Co-op] <name>" na lista normal de sessões, depois **Join**. Sessões normais seguem para
  Join original por trampolim de 5 bytes.
  - Host nomeia sessão DirectPlay "[Co-op] <name>": `Server+0x11` definido antes de `AddNetwork`.
  - Registros de sessão têm 0x85 bytes, entre `client+4 -> net+0x90` e `+0x94`: +0 vtable, +4 nome de tipo, **+8 nome**
    (FOTString), +0xc flag de senha, +0xd jogadores, +0x11 máximo de jogadores, +0x15 dwUser1.
  - DirectPlay não fornece IP do host ao participante. Este pergunta por UDP na porta 47701 ("FTCOOP?" enviado ao
    endereço do campo IP, loopback e endereço de broadcast); host responde "FTCOOP! <session>", e o endereço
    de origem da resposta é o host.
- Mensagem de espera: `0x6602b0(parent, FOTString* text)` (cdecl) mostra WBOSMessageBox modal (vtables 0x827ce0 /
  0x827ce8). O tick da própria caixa busca o save quando lobby abre e encerra a caixa (+0x34); depois o
  loop de mensagens carrega o save. Clicar OK antes para a espera.
- Telas do bunker: comprar e vender (WBarter 0x7ff758), recrutar (WRecruit 0x80884c) e gerenciar esquadrão
  (WSquadWindow 0x8081f8, WSquadSelectionWindow 0x80838c) não enviam mensagens de rede. No cooperativo são exclusivas do host. Quando
  uma fecha no host com participantes conectados, ele ressincroniza; num participante, a tela fecha imediatamente
  com aviso. WBarter é aberta por tipos de evento 6 e 7 de `0x471ad0` (com entidade de comerciante).
- Testes:
  - `menu_join`: 23/23, via Start Co-op, lista de sessões, descoberta UDP e mensagem de espera.
  - `bunker` (`bunker.sav`, criado pelo testador): 17/17. Cooperativo no bunker, um movimento, depois fechamento simulado de
    tela exclusiva do host: host ressincroniza e participante acompanha com estados idênticos.
  - Verificação de estado aleatório agora só falha numa divergência duradoura. Oscilação de um frame no frame de ressincronização
    do host (salvar rápido enquanto participante ainda executa sessão antiga) é informada, mas não causa falha.
- Ainda não verificado: detecção das janelas WBarter e WRecruit reais (precisa de comerciante; vtables vêm de RTTI)
  e fechá-las num participante.


### <a id="live-bunker-session-and-conversations-that-belong-to-one-player-2026-10-21"></a>Sessão ao vivo no bunker e conversas de um jogador só (2026-10-21)

Observado na sessão cooperativa ao vivo do testador em `bunker.sav` (host e participante num PC):
- Conversar com o NPC de recrutamento enviou um comando 0x17 do cliente do host: membro 0x03bc, NPC EntityID
  0x0051000a. **WSpeech abriu nas duas cópias**, porque conversar é comando lockstep.
- Host então recrutou. As janelas que receberam ticks foram WSingleRecruit, WPortraitWindow, WListBox, WRecruitItem e
  WBackground. **WRecruit nunca recebeu tick pelo tick compartilhado 0x6c5130**, então a verificação exclusiva do host (vtables RTTI)
  não a encontrou, e nenhuma ressincronização ocorreu. O movimento seguinte do esquadrão levou 5 membros em vez de 6. Testador: "posso confirmar que dessincroniza
  quando os membros do grupo mudam".

Implementado (deduzido do acima):
- Conversas e o que vem depois são privadas do jogador que iniciou:
  - Função de envio do cliente 0x728840 (`char __thiscall(Client*, msg, len, reliable)`, `ret 0xc`; primeiros 5 bytes
    vão para trampolim) anota os próprios comandos de conversa desta cópia.
  - Host também anota conversas dos participantes em seu recebimento do servidor.
  - No primeiro tick de WSpeech, a cópia que enviou a conversa nos últimos 10 s a mantém. Toda outra a fecha com
    vtable +0x34(0). Conversa que ninguém enviou fica no host (conversas por script).
- Telas identificadas pelo nome RTTI (WSpeech; qualquer coisa contendo Barter, Recruit, SquadWindow, SquadSelection). Quando
  nenhuma recebe tick por 1 s, contam como fechadas, e o jogo de quem conversou vira o de todos:
  - Host conversando: ressincronização normal (salvar rápido, carregar rápido, participantes acompanham).
  - Participante conversando: salva rápido (seu QuickSave.sav é separado e restaurado) e envia o arquivo ao host
    na porta lateral: `PUT <id> <size> <name>\n` + bytes, resposta `OK\n`, armazenado como
    `user/save/ftcoop_upload.sav`. Host carrega como num carregamento rápido (atribuir 0x8bddb4, fechar WGameMain
    +0x38 com 0x10), serve como próxima geração, e todos acompanham.
- Regra de exclusividade do host e aviso "só o host pode trocar" removidos.
- Toda conversa agora termina com recarga de alguns segundos, mesmo sem troca. Escolhas de diálogo podem mudar
  estado de missão, então isso é intencional.
- Dois jogadores trocando ao mesmo tempo: save posterior vence, e as trocas do outro são perdidas. Não tratado.
- Novos testes `talk_host` e `talk_join` (antigo `bunker` removido):
  - Bot envia o comando exato de conversa do testador, depois muda um HP em sua própria cópia (representando uma troca) e
    encerra a conversa.
  - Verificações: outra cópia fechou a conversa, save seguiu a direção correta, e sessão 2 leva a mudança às
    duas cópias.

Encontrado ao fazer os testes passarem (observado nos logs, salvo indicação):
- Comando de conversa não faz nada do outro lado da sala. Nenhum movimento direto ao NPC moveu alguém: nem a
  última posição do testador, nem um ponto próximo, para nenhum dos membros tentados. Seguir a própria rota do testador
  (6 trechos, decodificados de seus movimentos de esquadrão) funciona.
- Enquanto conversa está aberta, jogo não executa frames. Bot age pelo tick da própria janela de conversa.
- **Conversa é um modo da tela de missão.** `WGameMain::SetMode` 0x471ad0 (`__thiscall(WGameMain*,
  int)`, modo em +0x156) monta janelas de cada modo e fecha as anteriores. 12 = conversa (0x4cf4b0),
  6/7 = troca (0x453e00 com 0/1); janelas dos demais modos: desconhecidas. Fechar só a janela (+0x34) deixava modo 12
  definido, e quickSave 0x478340 recusa fora de 0, 1 e 10, então o save nunca era gravado. Conversas
  agora terminam com `SetMode(0)` pelo tick da própria tela de missão.
- quickSave também recusa enquanto +0x15a (salvando) ou +0x15c (contagem regressiva) definido, ou quando 0x4782a0 falha (World+0x7c9
  definido, ou nenhum membro passa vtable+0x480).
- **Toda cópia executa seu próprio Server, participante também** (o de seu lobby de um jogador, ocioso após entrar). Save armazena
  números de tick desse Server: +0x95 último enviado e +0x99 próximo, frame+1 e frame+5 durante execução.
  - Server local do participante ficava no carregamento (1954/1957, mundo no frame 2546). Host, carregando o save
    do participante, enviava ticks desde 1961, e ambos esperavam cerca de 42 s até chegarem ao frame do mundo.
  - Definir Server do host após carregar parou os ticks completamente.
  - Correção: antes de participante salvar para host, define seu Server local para frame+1 / frame+5.
- Resultados:
  - `talk_join`: **25/25** (log: `join: local Server ticks 1954/1957 -> 2547/2551`).
  - `talk_host`: **22/22**. Executado antes da mudança final exclusiva do participante, que não toca o caminho do host.
- Ambos adicionados a `run_suite.py`. Suíte completa não executada desde as mudanças de menu, popup e
  conversa.
- Ainda não verificado com cliques reais: janelas de troca e recrutamento alcançadas de uma conversa real, uma conversa real
  encerrada por suas próprias opções e telas de gerenciamento de esquadrão abertas sem conversa.

### <a id="bunker-trading-by-bot-and-inventories-in-every-test-2026-10-21"></a>Troca no bunker por bot e inventários em todo teste (2026-10-21)

A sessão ao vivo do testador ficou ociosa por 95 minutos (nenhum esquadrão moveu), então troca foi testada por bot.

Encontrado (descompilado, BOS.exe sha256 c5b91fe5...):
- Modos de `WGameMain::SetMode` 0x471ad0: 1, 4, 5 (telas de membro, montadas só para entidade válida), 2 (0x4817b0),
  3 (0x458b40), 6 troca (WBarter 0x453e00 flag 0), 7 igual com flag 1, 8 (0x4d6060), 9 (0x4b3c00),
  10 (0x4cea20), 11 (0x4b71c0), 12 conversa, 13 pausa ("paused", "pressAnyKey"), 14 (0x63fc50), 15 confirmação de saída.
  Significados além de 6, 7, 12 e 13: desconhecidos.
- Botões de conversa são métodos WSpeech (`__thiscall(WSpeech*, button)`, `ret 4`):
  - 0x4cffd0 encerra conversa (SetMode(0) se for WGameMain+0x136, depois fecha a si mesmo);
  - 0x4d0000 Barter: copia EntityIDs dos interlocutores (WSpeech +0x100..+0x106) para 0x8bc218 (comprador) e 0x8bc208
    (comerciante), depois chama vtable +0x28 de World+0x2b9; tela de troca (modo 6) está aberta ao retornar;
  - 0x4d0090 define o mesmo par e chama SetMode(7) (notas FTSE: gamble).
- Construtor WBarter aumenta contador de pausa do mundo (0x4fc800(1)), e destrutor o reduz, então nenhum frame
  do jogo executa durante troca, e janelas da tela recebem vários ticks por frame.
- Inventários (`Actor.h` / `Inventory.h` / `Collectable.h` do FTSE; comentários de deslocamento contam do início da entidade):
  Actor +0x1006 EntityID do inventário; entidade Inventory (vtable 0x818af8) +0x1a9 lista circular (nó: next, prev,
  EntityID); contagem de itens em +0x1ad. Actor +0x1055 isquartermaster, +0x1056 canbarter.

Observado nos testes de troca:
- Comerciante do bunker é NPC 96 (execução 2 do testador também conversou com entidade 0x60 antes de comprar e vender). Membro
  0 chega a ele pelos dois primeiros trechos da rota do testador mais um passo até (359,5, 32, 320,5).
- Comerciante tem 2 pilhas próprias. Com troca aberta, tem estoque da loja (30 pilhas). Após
  fechar e recarregar, volta às 2: estoque existe apenas durante troca, e um
  item vendido a ele vai junto. Ambas concordam, então é comportamento do jogo, não falha de sincronização (deduzido).
- Enquanto tela privada aberta, modo da tela de missão diferente de 0, 1 e 10 também conta como "ainda aberta"
  (janelas como WRecruit recebem ticks sozinhas, não pela interceptação compartilhada).

Novos testes de bot (`trade_host`, `trade_join`, bunker.sav):
- Antes da conversa, lado não comprador move membro 1 e comprador move membro 2. Sessão 1 precisa corresponder
  nas duas cópias até frame da conversa: posições, HP, estado aleatório e inventários.
- Membro 0 do comprador caminha ao comerciante e conversa. Bot pressiona botão Barter real da conversa
  (0x4d0000); troca abre só na cópia do comprador. Após 2 s, sai com SetMode(0).
- Depois move um item em cada direção com funções de inventário expostas a scripts (vtable Entity +0x508
  RemoveInventory, +0x504 AddToInventory, como FTSE chama). **Não coberto:** arrastar/ofertar da própria tela
  de troca e dinheiro. Quais funções chama é desconhecido.
- Verificações: sessão 2 (jogo do comprador) tem novo inventário do membro em ambas, e todo inventário
  corresponde ao do comprador no momento de atualizar os outros.
- Todo teste também registra inventário de cada Actor nos snapshots (`INV s= f= id= items=id:count,...`). Executor
  verifica todo inventário idêntico em ambas a cada frame compartilhado.
- Resultados: `trade_host` **30/30**, `trade_join` **33/33**.
- Suíte completa antes destas mudanças (build antiga, 14 testes): tudo como esperado, exceto `dropin`, 29/30. A verificação procurava
  texto de carregamento pelo loop de mensagens, mas participante agora carrega pela mensagem de espera ("loading the host's save ...").
  Agora aceita ambos.
- Suíte completa na build final (16 testes, todos com verificação de inventário): **SUITE: PASS**. Mutações falharam como
  deveriam; dropin 31/31, trade_host 30/30, trade_join 33/33.

Decisões do autor (2026-10-21):
- Controle continua compartilhado: todo jogador pode dar ordens a todo membro, e jogadores se organizam entre
  si.
- Divergência rara será perseguida com estresse de 4 jogadores: muitas ações dos quatro, verificando qualquer
  dessincronização.
- Próximo: recrutamento e mudanças de esquadrão por bot.

### <a id="recruiting-by-bot-2026-10-21"></a>Recrutamento por bot (2026-10-21)

Encontrado (observado na árvore de janelas do log, depois descompilado):
- Botão (WBOSButton / WImageButton) mantém handler em +0x112 e proprietário do handler em +0x10e. Handlers são
  `__fastcall(owner, edx, arg)`.
- Quatro botões da conversa (filhos WSpeech): Done 0x4cffd0, Gamble 0x4d0090, Barter 0x4d0000, Recruit
  0x4d0110. Corresponde a `WFTSESpeech.cpp` do FTSE.
- Recruit abre modo 8 da tela de missão: WSingleRecruit (vtable 0x808bc0), com lista de WRecruitItem e
  WPortraitWindow do esquadrão. Seus botões:
  - 0x4d4fe0 (botão de imagem): adicionar recruta selecionado (vtable +0x1a8 seleção, +0x1b4 adicionar);
  - 0x4d5010 (botão de imagem): dispensar membro cujas flags de entidade +0xb2 têm bit 0x40. Esse bit é a
    seleção: interlocutor tinha 0x52, outros 0x12;
  - 0x4d4e70: ficha de personagem (janela de 0x195e, 0x458b40);
  - 0x4d4e60: Done (observado: modo 0 depois, esquadrão mantido).
- Após dispensar, seleção da lista de recrutas é o membro recém-dispensado.

Novos testes `recruit_host`, `recruit_join` (bunker.sav):
- Membro 0 do jogador que recruta percorre rota do testador ao recrutador (NPC 81) e conversa. Bot pressiona
  botão Recruit da conversa.
- Na tela, seleciona e dispensa os dois últimos membros, adiciona um recruta e pressiona Done.
  São os próprios handlers dos botões, chamados como um clique os chama. Esquadrão observado na cópia de quem recruta:
  6 (1055, 997, 957, 969, 956, 308) -> 4 -> 5 (último dispensado, 956, recrutado de volta).
- Verificações: recrutamento abriu só na cópia de quem recruta, e esquadrão mudou. Sessão 2 tem
  esquadrão de 5 membros de quem recrutou em ambas, na mesma ordem.
- Todo teste também registra esquadrão da campanha nos snapshots (`SQUAD s= f= n= ids=`). Executor verifica mesmo
  esquadrão em ambas a cada frame compartilhado: o bug relatado pelo testador.
- Resultados: `recruit_host` **28/28**, `recruit_join` **31/31**.
- Suíte completa depois (18 testes, todos com verificações de inventário e esquadrão): **SUITE: PASS**.
### <a id="real-barter-deals-with-money-2026-10-21"></a>Negócios de troca reais, com dinheiro (2026-10-21)

Encontrado (árvore de janelas no log, bytes brutos decodificados manualmente, descompilação do negócio):
- Tela de troca (modo 6), como SetMode a mantém:
  - WGameMain+0x10e: WSquadEquip, inventário do comprador;
  - +0x11a: WBarter, estoque do comerciante;
  - +0x11e: WBarterTable, duas mesas de oferta (WInvActor em table +0x104 e +0x108, cada uma com valor total em
    +0x147). Tem dois botões:
    - Offer 0x455830 (thiscall): `if (value(+0x104) >= value(+0x108)) deal()`;
    - Done 0x455880: SetMode(0).
- **Todo Actor tem oferta de troca:** segunda entidade Inventory cujo EntityID fica em +0x100a (slot 406 da vtable, GetUnk22EntityID
  do FTSE; slot 402 GetInventoryList). Na execução bunker: oferta do comprador 1055 = 320, do comerciante 96 = 265.
- Negócio, 0x4558a0: para cada item da oferta do comprador e do comerciante, RemoveInventory (+0x508) da
  oferta e AddToInventory (+0x504) no outro lado. O par vem das globais 0x8bc208 / 0x8bc20c (comerciante)
  e 0x8bc210 / 0x8bc218 (comprador).
- Valores das mesas atualizam sozinhos quando itens entram nas ofertas: 20 e 2 após movimentos do bot.
- **Dinheiro são lacres de lata:** `sprites/items/Money/Ringpulls.spr`, valor 1 cada (comprador tinha 250). Ponteiro do nome
  do sprite da entidade em +0x105. Valor de Collectable em +0x1b6. Entidades Inventory (vtable 0x818af8) têm funções
  reais de adicionar/remover (0x5b4030 / 0x5b44e0). Container (vtable 0x817a2c) guarda EntityID do inventário em +0x1aa.

Testes de troca agora fazem negócio real:
- Bot coloca item mais barato do comerciante na oferta dele e 3x seu valor em lacres (pelo menos 20)
  na oferta do comprador, depois pressiona Offer. Observado: 20 lacres por uma munição 9 mm;
  comprador foi de 250 para 230, e ambas as ofertas esvaziaram.
- Movimento direto anterior removido. Não controlado: arrastar e soltar em si (bot preenche ofertas com as
  mesmas funções de inventário) e regras de preço do comerciante (mesa só verifica valor oferecido >= solicitado).
- Resultados: `trade_host` **32/32**, `trade_join` **35/35**.

- Planejado (autor pediu sincronização no bunker sem recarga): reproduzir cada ação de tela privada como comando cooperativo
  lockstep, para toda cópia executar a mesma função no mesmo frame (novas entidades de itens e recrutas recebem então
  mesmos ids em todos os lugares). Depois checksum de esquadrão, inventários, dinheiro e variáveis de missão em cada cópia. Correspondência significa
  nenhuma recarga; divergência, ou mudança que nada reproduz, recorre ao save e recarga. Conversa sem mudança
  pularia recarga. Ordem: função de negócio da própria tela primeiro (com dinheiro), depois
  checksum, depois reprodução de recrutamento, depois reprodução de troca.
- Ainda não coberto: tela de múltiplos recrutas (WMultiRecruit, "gui/back/recruitMulti"), custos ou limites de recrutas,
  telas de gerenciamento abertas sem conversa.


### <a id="trades-and-recruits-without-a-reload-2026-10-21"></a>Trocas e recrutamentos sem recarga (2026-10-21)

Testador: "quando estiver pronto, não quero mais salvar/recarregar ao fazer essas mudanças, é irritante"; os outros jogadores
devem continuar jogando; "se não tiver, implemente e sincronize"; "crie uma trava no comerciante para ninguém mais usá-lo
enquanto um jogador usa". Código: `local/src/ftcoop/logger/private_sync.inc`.

Encontrado (observado nos logs, salvo indicação):
- Lockstep e pausas. Enquanto host está em tela privada, toda cópia para: os ticks vêm do mundo do host.
  Enquanto um participante está, host continuava (trade_join: frames host 2277 -> 2343 enquanto participante estava em 2305).
- Entradas da tabela de entidades são `{ptr, i16 next_free, i16 seq}` (`World.h` FTSE), com início da lista livre u16 em
  World+0x74f. Abrir troca cria estoque da loja, e fechar o destrói novamente. Só isso move 61 entradas
  e início da lista (320 -> 265) apenas na cópia de quem troca.
- Jogo serializa entidade para memória como o desfazer do editor (`world_undo.cpp`, 0x42ec00):
  - streambuf de memória: 0x14 bytes, base 0x426830, vtable 0x7fde04, buffer FOTString em +0xc;
  - arquivo serializado sobre ele: 0x704060 `thiscall(archive, 1, streambuf, 1)`;
  - salvador 0x5eabd0 `cdecl(archive*, EntityID)`. Salvar entidade em arquivo 0x5ea630 chama da mesma forma.
  - Saída: `<entity>`, nome da classe, depois propriedades. Bug in the Shell tinha 6301 bytes.
- MakeEntity 0x5ea400 (CreateEntity FTSE) lê esse arquivo e cria entidade no slot do início da lista livre.
  Lê arquivo inteiro na memória, envolve em streambuf vtable 0x80948c e carrega com 0x5ea6d0, que também
  define entity +0x5d pelo contador 0x8be148.
- Item comprado pode se fundir a pilha existente: munição 9 mm foi para pilha do comprador, 135 -> 136.
- Caminho de dispensa do recrutamento (0x4d6980) remove ator da grade de mapa em World+4 (0x6e5ab0, 0x6e9bc0).
  Readicionar coloca recruta perto do esquadrão: 956 pulou para (333, 32, 339). Entidade do ator dispensado é
  destruída.
- DestructEntity (slot 10 da vtable) termina no frame seguinte, então lista livre do receptor muda mais uma vez após
  delta.
- Personagens caminhando avançam fração de unidade entre frames mesmo com mundo pausado.
- Contador de pausa do mundo: 0x4fc800 `thiscall(World*, bool)` (+1 / -1 em World+0x2db), `ret 4`.
- Handler de comandos de Actor 0x5747e0 chama vtable +0x660 do ator para todo comando antes do switch, então um
  tipo de comando personalizado não pode alcançá-lo.

Implementado:
- **Trava de NPC.** Comando de conversa (0x17) trava seu NPC em toda cópia, no frame em que executa. Trava liberada pelo
  comando cooperativo `kSyncDone` de quem conversa.
  - Cópia recusa conversa do próprio jogador com NPC travado (envio do cliente), com aviso.
  - Host também remove da mensagem a conversa de um segundo jogador com NPC ocupado (recebimento do servidor), para dois jogadores
    clicando ao mesmo tempo.
- **Retenção.** Toda cópia exceto a de quem conversa retém seu jogo (contador de pausa +1) desde o frame em que a
  conversa abre; mesmo frame em todos, e o mundo de quem conversa também para ali. Libera quando
  `kSyncDone` chega. Retenção que espera mais de 10 minutos, ou cujos jogadores saíram, é liberada.
  - **Isso difere do pedido do autor ("continuar jogando"):** primeira build sem retenção divergiu
    (recruit_join: NPC contornou membro movido só numa cópia).
- **Delta em vez de recarga.** Quando telas fecham, no primeiro frame em que o mundo de quem conversa volta a executar, ou
  após 1 s sem tick de tela, ele compara com snapshot da abertura. Envia delta como comandos
  cooperativos (tipo 0x30, 18 bytes por comando):
  - entidades destruídas;
  - novas entidades na serialização do próprio jogo, que receptor cria no mesmo slot (início da lista livre apontado
    para ele);
  - contagens de pilhas;
  - listas de inventário Actor, em ordem;
  - lista do esquadrão;
  - HP dos membros e posição quando mudou mais de 2 unidades (grade atualizada com 0x6e9bc0);
  - controle interno da tabela e contador serial.
- Outras cópias aplicam delta quando mensagem de rede chega: host no recebimento do servidor, participantes no
  tick antes de o cliente tratar. Ticks executam alguns frames adiantados, então esperar frame lockstep deixaria uma
  cópia retida atrasar.
  - Controle interno é gravado novamente dois frames depois, pois destruições terminam tarde.
  - Variáveis de missão alteradas (escolha de diálogo) ainda usam save e recarga antigos.
- Todo snapshot agora também registra hash da tabela de entidades (`ETAB`), e executor compara.

Resultados (cada teste cobre frames antes da conversa e todos após delta, em ambas as cópias: posições, HP,
estado aleatório, inventários, esquadrão, tabela de entidades):
- `browse_host` **25/25**: troca abriu, nada comprado, 61 entradas sincronizadas, sem recarga. Conversa do participante com
  comerciante ocupado recusada.
- `browse_join` 24/25 na execução, falhando só numa verificação do texto antigo de log; corrigida, mas
  ainda não reexecutada.
- `trade_host` **34/34** e `trade_join` **35/35**: negócio real com lacres, delta de 555 bytes, sem recarga,
  outra cópia retida por cerca de 2 s.
- `recruit_host` **30/30** e `recruit_join` **31/31**: dois dispensados, um recrutado de volta, delta de 632 bytes, sem
  recarga.
- Antigos `talk_host` e `talk_join` dependiam da recarga; `browse_*` os substitui. Suíte completa
  não executada com estas mudanças (autor pediu trabalho de recursos primeiro).

Sair do bunker e mapa mundial (testador: "no mapa, vamos permitir só o host mover"):
- Grade de saída do bunker: testador saiu de cerca de (370, 32, 343) na execução 3 (mesmo layout: mesmo
  id de recrutador, mesma rota). Movimento do esquadrão inteiro até (369,3, 32, 345,5) basta: o próprio gatilho de saída
  da missão ("Players at Exit Grid") a encerrou nas duas cópias.
- No participante, GoToMap 0x6b6580 (onde termina clique num local do mapa) é recusado com aviso: só host
  escolhe. Escolha do host inicia sua missão sozinho; ele ressincroniza e participante acompanha (caminho existente).
- `exit_host`: 23/24 na única execução, falhando só numa verificação que esperava incorretamente um segundo movimento do esquadrão. Agora
  flexibilizada; exit_host não reexecutado com ela. `exit_join` **24/24** com verificação flexibilizada.

Ainda não coberto:
- item comprado que vira nova pilha (caminho 'C') e recruta que é nova entidade;
- diálogo de missão (ainda recarrega);
- três ou quatro jogadores;
- telas de esquadrão abertas sem conversa.

## <a id="cheats-in-the-test-copies-remove-once-were-done"></a>Trapaças nas cópias de teste: remover ao terminar

Apenas para testes, script de usuário FTSE (`<game dir>/core/FTSE/ftse.lua`) de cada cópia tem invencibilidade do esquadrão
(`GODMODE_SQUAD`, `OnDamageCalc`) e acerto garantido (`SUREHIT_SQUAD`, `OnChanceToHitCalc`) sob o carregador
netlog.dll. Não fazem parte do mod. **TODO antes de distribuir:** removê-las para `ftse.lua` conter só o carregador.

## <a id="mod-repo-2026-10-22"></a>Repositório do mod (2026-10-22)

Código público em https://github.com/thennak3/fallout-tactics-coop (MIT; código, bot de teste e executor,
carregador FTSE sem trapaças; sem arquivos do jogo, saves ou DLLs compiladas). Lançamento v0.1.0 (pré-lançamento, 2026-10-22): SHA-256 de `netlog.dll`
383c3c2c687f418d467dcf15cb311871b6b4787c9ade4acc71b1d57ee92efa3c, compilada do código do commit cd073c1; `exit_host` 24/24 nessa
build. Verificação de versão (observada): instalação GOG do testador e quatro cópias têm mesmo `BOS.exe` (hash em
Identidade); arquivo por arquivo, cópias diferem da instalação apenas por FTSE, cnc-ddraw, arquivos do mod, saves e
`bos.cfg` (som silenciado, último save). Portanto, mod tem como alvo GOG 1.27 sem modificação mais FTSE 0.60a.
Documentação no playbook e PR em rascunho aguardam o mod ficar pronto (escolha do autor).

## <a id="four-players-in-the-bunker-new-stacks-quest-variables-the-merchant-race-2026-10-22"></a>Quatro jogadores no bunker, novas pilhas, variáveis de missão, corrida do comerciante (2026-10-22)

Observado (logs em `local/re/test_runs/`, 2026-10-22):
- `trade_host --joiners 3`: 61/62. Host comprou tipo de item que não carregava (armadilha bullhorn, `.?AVTrap@@`), então
  a própria entidade do comerciante, criada ao abrir troca só no host, permaneceu no inventário do comprador. O
  delta a levou ('C', 2208 bytes); os três participantes a criaram no mesmo slot (1057) com 0 conflitos, e as
  quatro cópias corresponderam em todo frame compartilhado (posições, HP, inventários, esquadrão, tabela, variáveis de missão). A única
  falha: bot não encontrou variável de missão contendo número.
- Variáveis do bunker (registradas): 2 de missão, `BUNKER_HAPPY="TRUE"`, `BUNKER_END="FALSE"`; 97 de campanha,
  por exemplo `CVAR_M01_COMPLETE="TRUE"`, `CVAR_M01_NPC_HAWKEYE="FALSE"`. Valores são texto, não números.
- Variáveis de missão agora vão no delta ('V': missão/campanha, índice, nome, valor) em vez de forçar recarga. O
  receptor define como gatilho: World::SetVariable FTSE, objeto de comando com vtable `0x837b24` executado por
  `0x67ee30` (Ghidra não marca `0x67ee30` como função). `trade_join --joiners 3`: cada cópia registrou
  `mission variable "BUNKER_HAPPY" = "1"` pelo delta.
- **Bug encontrado e corrigido: corrida do comerciante.** Em `trade_join --joiners 3`, harness tornou todos os participantes compradores. A
  trava do host descartou duas das três conversas, mas os três a consideraram sua: comando de conversa é igual para
  todos (membro do esquadrão compartilhado, mesmo NPC), e cada cópia só sabia "enviei conversa nos últimos
  10 s". Correção: cada jogador envia reivindicação (comando cooperativo 0x30, tipo 4, número aleatório) logo antes da conversa; host
  retransmite só primeira reivindicação e conversa de NPC livre (`HostFilterTalks`), então toda cópia aprende o vencedor pela
  reivindicação retransmitida. Reivindicação pode chegar logo antes do envio da conversa de um perdedor (visto: 16 ms), então conversa com NPC
  vencido por outro é recusada na própria cópia do remetente, e a reivindicação retransmitida, não a janela de 10 s, decide de quem
  abre a conversa. Números vinham inicialmente de `rand()`, mesma sequência em cada cópia: duas reivindicações
  diferiam em dois dígitos hexadecimais. Agora QueryPerformanceCounter e id do processo, com hash.
- `trade_race --joiners 3` (todos conversam com comerciante ao mesmo tempo), segunda execução: exatamente um vencedor, host
  descartou a outra conversa enviada, terceiro participante recusado na própria cópia; troca sincronizou para os quatro
  (66/68; duas falhas eram verificações que esperavam que todo perdedor tivesse enviado conversa).
- Correção do harness: com `actor=join` só participante 1 age; `actor=all` (corrida) faz todos agirem.

Lido dos botões de recrutamento (assembly; Ghidra não marca função em `0x4d68f0`, bytes decodificados manualmente):
- Add `0x4d4fe0`: `pick = vt+0x1a8()`, `vt+0x1b4(pick)`, `0x4d5d60(pick)`, todos `__thiscall`. `vt+0x1a8` (`0x4d68f0`)
  pede ao objeto em +0x14f (`0x65af20`) registro em World+0x733 (passo 0x15d, jogadores) e percorre lista
  de membros desse jogador (+0x4b).
- Remove `0x4d5010`: encontra membro com bit 0x40 em +0xb2 (contagem `vt+0x1b0`, membro i `vt+0x1ac`), remove
  (`vt+0x1b8(i)`), depois seleciona entrada desse membro na list box em +0xfa (`0x6cde50` fornece entradas; entrada
  +0x134 -> EntityID em +0x153/+0x155; `0x6cded0(listbox, index, 0)` seleciona). Por isso adicionar readiciona o recém-
  dispensado.

Hipótese, não verificada: pool de recrutas é um dos jogadores World. Primeira busca (jogador diferente do esquadrão
contendo dispensado, logo após dispensas) não encontrou nada; membro 308 foi destruído (52
atores -> 51 em todas), então se recrutas são entidades antes de recrutados é **desconhecido**.

- `recruit_join --joiners 3`: 54/56. Bot readicionou membro dispensado (pool não encontrado). Divergência: dois
  NPCs errantes (256, 246, 30 HP) seguiram caminhos diferentes na cópia de quem recruta (participante 1) a partir dos frames 2554–2604,
  enquanto host e participantes 2 e 3 concordaram. Os quatro pausaram em 2537 e retomaram em 2538; estado aleatório
  correspondeu nos quatro o tempo todo. Causa: desconhecida. Divergência inexplicada anterior de 4 jogadores (2026-10-21, `simul`)
  também só ocorreu no participante 1; `bos.cfg` e configurações das cópias são idênticos, exceto terminações de linha.


### <a id="recruits-deferred-destroys-big-deltas-2026-10-22-later"></a>Recrutas, destruições adiadas, deltas grandes (2026-10-22, mais tarde)

Observado (execuções de bot, logs em `local/re/test_runs/`):
- **Posicionamento no mapa.** Após recrutamento, NPCs errantes seguiam caminhos diferentes na cópia de quem recrutou. Dumps de memória de
  todo ator em três cópias (dois receptores concordam, então ponteiros diferentes entre eles são ruído) mostraram limites do membro
  movido (+0x08..+0x1c ints, cerca de posição x 4, e +0x50..+0x6c) ainda no lugar antigo nos receptores.
  Tela de recrutamento posiciona personagem com `0x4dfc60`, depois `0x6e5ab0(World+4, entity)` quando World+0x1a5 definido,
  depois `0x6e9bc0(World+4, entity)` (`0x4d6980`, todos `__thiscall`). Operação de posição só fazia última chamada; agora ambas.
- **Limite de comandos por tick.** `0x63bc10` (commands.cpp linha 22) para o jogo com "Invalid number of commands
  passed" quando tick contém mais de **1000** comandos. Delta de novo recruta (Actor serializado 12,7 KB, 23 KB com
  IA, inventário, armadura e duas armas) usou 1288. Agora: compressão LZNT1 (`RtlCompressBuffer` de ntdll, 23 KB -> 6 KB),
  22 bytes de carga por comando, e deltas acima de `[coop] lockstep_chunks` (padrão 300) vão pelo servidor de arquivos
  do host (`DPUT` / `DGET`, save_transfer.inc); lockstep leva só registro de concluído com tamanho e hash.
- **Destruições adiadas.** `DestructEntity` (slot 10 da vtable) define **+0x141 = 1**; entidade sai do slot no
  frame seguinte, mantendo next_free e seq. Comparação conta entidade marcada como removida e põe slot no controle interno;
  quem conversa também regrava seu próprio controle após aquele frame, como receptores.
- **Novos personagens não podem ser copiados slot por slot.** Criado pelos bytes serializados (`0x5ea400`), um Actor traz
  filhos junto, em ordem diferente e até como entidades diferentes (um BaseAI, dois inventários) daquelas criadas pela
  tela de recrutamento. Encadear lista livre na ordem de quem recruta não ajudou.
- Tentado: toda cópia, inclusive a de quem recruta, cria novo personagem pelos bytes após frame seguinte (quem recruta
  destrói o da tela). Personagem então correspondeu slot por slot nas duas (slot 308), e tabela de entidades
  correspondeu, mas NPC 46 depois andou por outro caminho na cópia de quem recruta. (Primeiro interpretado como flag IA em +0x117; errado:
  +0x117 difere em todo ator entre cópias mesmo antes das telas, bits baixos sempre 0 ou 8, parte de
  ponteiro. Causa mais provável é o frame extra abaixo.) Sob `[coop] recreate_recruits=1`, desativado por padrão.
- Tentado e removido: copiar todo byte alterado na memória de um Actor durante telas. Quase todos mudaram
  +0x171..+0x172 para mesmo novo valor em quem recruta: parte de ponteiro para objeto realocado. Uma estrutura
  compactada não permite distinguir esses ponteiros de dados com segurança, então cópias brutas não são usadas.
- Assim: readicionar membro dispensado e dispensar são sincronizados por delta; **recrutar alguém novo usa save e recarga**.

Deduzido: entradas da lista de recrutas contêm EntityIDs (+0x134 -> +0x153 seq / +0x155 id); `0x6cded0(listbox, index,
1)` seleciona uma, e botão adicionar a adiciona. Membros dispensados são destruídos (308: 52 atores -> 51).

- **Quem conversa executou um frame a mais.** Bits exatos de posição registrados no snapshot e na comparação: mundo de quem conversa foi
  do frame 2533 a 2534 entre eles (telas fecharam, mundo retomou, comparação ocorreu nesse primeiro frame),
  enquanto toda outra cópia ficou em 2533 e executou 2534 só após aplicar delta. NPCs caminhando nesse frame (93,
  239, 246, 256, 419, 432, 441) são os que divergiam nas execuções falhas de recrutamento. Agora quem conversa também retém seu
  mundo (contador de pausa `0x4fc800`, World+0x2db) desde abertura até produzir comparação, e
  telas contam como fechadas quando nenhuma privada recebeu tick por 300 ms. Snapshot e comparação agora ocorrem no mesmo frame
  (2533). Suíte completa antes desta mudança: 24 de 26 como esperado (simul: movimento de 5,07 em vez de 8 unidades, igual
  nas duas, depois 21/21 numa reexecução; recruit_host 3 jogadores: desvio de NPC, 42/44).

### <a id="recruiter-candidates-v020-2026-10-22"></a>Candidatos do recrutador; v0.2.0 (2026-10-22)

- Observado: após retenção de quem conversa, posições (bit a bit), estado aleatório e tabela de entidades corresponderam nas
  duas cópias logo após recrutamento, mas NPC 46 seguiu outro caminho cerca de 200 frames depois (suíte completa, execução 2: recruit_host
  31/32). Enquanto recrutamento está aberto, mundo de quem recruta contém 8 atores extras em (0, 0, 0): candidatos
  da lista (EntityIDs das entradas), criados só nessa cópia e destruídos ao fechar. Hipótese, não verificada: criá-los
  e destruí-los reordena algo percorrido pelas atualizações de NPC.
- Portanto, toda visita ao recrutador usa save e recarga por enquanto (issue #1 no repositório do mod). Correção planejada é o projeto
  do testador para loja: executar alocação da tela em toda cópia no mesmo frame lockstep, janela só numa cópia.
- Suíte completa, execução 2 (antes disso): 25 de 26 como esperado. Depois: recruit_host 26/26, recruit_join 27/27,
  recruit_host com 3 jogadores 37/37, trade_host com 4 pelo servidor de arquivos host 64/64.
- Repositório do mod: commit 0d43e0f, lançamento v0.2.0 (pré-lançamento), SHA-256 de `netlog.dll`
  1d2dfb4b46e583de7b3d555eecb6ffddeb4852a0ad725326b4e8b9c0da6d792e.

Decisões do autor (2026-10-22): compras não podem pausar outros jogadores; recrutamento pode (muda personagens que
todos jogam). Próximo: troca aberta por lockstep, estoque criado em toda cópia no mesmo frame (janela
só para comprador), personagem do comprador travado contra ordens enquanto compra, sem retenção para troca, delta
aplicado no frame lockstep; recrutador recusado com aviso enquanto alguém compra.

### <a id="the-quartermasters-shop-for-a-shop-that-pauses-nobody-2026-10-22"></a>Loja do intendente, para loja que não pausa ninguém (2026-10-22)

Observado (watchpoint de gravação no início da lista livre World+0x74f enquanto bot pressiona Barter; Ghidra):
- Toda alocação de entidade grava início em `0x4e525c`. Abrir troca do comerciante do bunker aloca só pelo
  construtor da tela de troca do intendente `0x454330` (vtable `0x7ff8ec`), chamado por SetMode (`0x4720e5`).
- `0x454330`: define globais do par (0x8bc20c comerciante, 0x8bc210 comprador, cópias de 0x8bc208 / 0x8bc218); `0x5b3a60()`
  cria nova entidade Inventory (cada chamada: watchpoint acerta 1–3); comprador e comerciante recebem uma como inventário de oferta
  (`vt+0x65c`, slot FTSE 407 ResetUnk22Entity, EntityID por valor). Se comerciante `vt+0x3f4` (253 IsQuartermaster):
  `vt+0x64c` (403 GetInventoryID) guarda ID do próprio inventário, terceira `0x5b3a60()` cria inventário de estoque e, para
  cada template da lista de estoque da campanha (`*0x8bdd2c` +0x151 início, +0x155 fim: templates FOTString*; +0x161:
  contagens) com contagem acima de 0: `MakeEntity 0x5ea400(&item, &template, -1)`, `item vt+0x1a4` (105 SetCount)(count),
  `stock vt+0x504` (321 AddToInventory)(&result (InventoryActionResult, 32 bytes), item, &id, count, 1), item
  destruído (`vt+0x28`) se adição falha. Depois `merchant vt+0x650` (404 SetInventoryID)(stock).
- Seu destrutor `0x454f40`: para intendente, todo item restante no estoque é removido (`vt+0x188`, `0x6a6550`),
  inventário de estoque é destruído, inventário próprio do comerciante restaurado; depois ambos os inventários de oferta são destruídos
  (`vt+0x658` cada, `vt+0x28`) e globais do par limpas.
- Construtor da outra tela de troca `0x453e00` aumenta contador de pausa (`0x4fc800(1)`); o do intendente
  não. Na troca do bunker, contador é 1 pela própria conversa (antes da retenção do mod), 2 com ela.

Plano (projeto do autor): pressionar Barter vira comando lockstep; no frame dele, cópia do comprador abre tela
(criando estoque), e todas as outras criam mesmo estoque pelas chamadas acima, sem janela; mundo do comprador
continua (pausa da conversa cancelada nessa cópia); ninguém retém; personagem comprador travado; ao
fechar, delta vai como comandos lockstep, e no frame do comando de fechamento outros aplicam e executam
passos do destrutor.

### <a id="the-shop-that-pauses-nobody-built-2026-10-22"></a>Loja que não pausa ninguém: implementada (2026-10-22)

`[coop] shop_no_pause` (padrão 1). Numa conversa com intendente (`vt+0x3f4`) que não é recrutador
(`vt+0x3f0`, slot 252), ninguém retém, e mundo de quem conversa continua: contador de pausa `0x4fc800` é interceptado
(trampolim de 6 bytes), e suas mudanças absorvidas na cópia de quem conversa enquanto aberta (saldo conferido
de volta a 0). Botão Barter `0x4d0000` (trampolim de 7 bytes) envia comando cooperativo kShopOpen em vez de abrir; no
frame dele, comprador chama handler real (tela abre sincronicamente, construtor cria estoque), e toda
outra cópia repete alocações do construtor (`HeadlessShopOpen`). Destrutor da tela do intendente `0x454f40`
(trampolim de 7 bytes) primeiro executa `0x4569a0` (devolve mesas de oferta), mede negócio (modo de comparação 2:
inventários do comprador e comerciante, novas pilhas, destruições, variáveis de missão, controle interno) e envia com kShopClose;
nesse frame, outros aplicam e repetem passos do destrutor (`HeadlessShopClose`, lista de estoque da campanha reconstruída
do restante). Ordens ao personagem comprador e conversas com recrutador são removidas das mensagens de outros jogadores
enquanto loja aberta, com aviso. Fechar a própria conversa envia só mudanças de variáveis (modo de comparação 1),
aplicadas no frame delas.

Encontrado no caminho (cada um é dessincronização real, corrigida e coberta por teste):
- Entidade criada de bytes serializados mantém cópia própria do EntityID (GenericItem em +0x146): com seq de quem conversa na
  tabela, mas não ali, jogo recusava destruí-la (`FixSelfId`).
- Entidade criada de bytes obtém nome de template (+0x199) do arquivo temporário (`ftcoop_entity.tmp`), e
  lista de estoque do intendente, reconstruída desses nomes, diferia; 'C' agora leva nome. Isso afetava toda
  entidade criada de bytes pelo mod, então saves feitos após essa sincronização podiam antes conter nome errado.
- Destruir inventário de estoque leva seus itens junto, mas não os apenas gravados na lista: seus itens são
  destruídos primeiro, na ordem da lista.
- Slot liberado e reutilizado num negócio (gastar últimos lacres): destruições antes de criações, criação cujo
  slot ainda é destruído espera um frame, e quando delta destrói algo, seu controle interno e fechamento da loja
  esperam próximo frame, para conclusão das destruições não mudar entradas novamente.
- Slot forçado é primeiro desvinculado da lista livre (`UnlinkFree`), para nunca ser entregue duas vezes.

Testes (bots, 2026-10-22): trade_host 46/46 (loja aberta no frame 2305 em ambas, estoque de 29 criado sem interface,
participante executou frames 2305..2337 nesse intervalo, travas recusaram com avisos), trade_join 45/45, trade_race com 4 jogadores
73/73, trade2_host 30/30 (duas visitas, venda, últimos lacres gastos; lista de estoque da campanha, inventários e
tabelas de entidades idênticos o tempo todo).

### <a id="selection-dots-2026-10-22"></a>Pontos de seleção (2026-10-22)

Um ponto colorido no retrato do membro para cada jogador que o selecionou (host vermelho, depois azul, amarelo,
verde por ordem de entrada; cor de participante desconectado é liberada). Canal lateral, não lockstep: "SEL <joiner id> <slots>" na
porta de arquivos cerca de 5 vezes por segundo, respondido com cor e seleção de todo jogador ativo.
- Retrato da barra do esquadrão: WPortrait, vtable 0x806d44. Substitui só slot 0 (destrutor 0x4bcdf0, ret 4), slot 4
  (desenhar 0x4bc7d0, __thiscall(this, renderer), ret 4) e slot 6 (0x4bcde0, retorna 1). EntityID do personagem em +0x153
  (slot na metade alta). Janela 57x75.
- Renderer vt+0x24 desenha contorno retangular {x0, y0, x1, y1} como ints nas coordenadas da janela, com ponteiro
  para cor ARGB (moldura de seleção do retrato). Floats ali não desenham nada visível.
- Retratos só desenham quando invalidados (seis desenhos numa sessão inteira): slot 3 da janela base (0x6c7260,
  __thiscall(this), ret simples) invalida janela inteira, slot 2 (0x6c7390) um retângulo.
- Seleção: bit 0x40 de character +0xb2. Selecionar todos 0x49f6b0 e desselecionar de uma tela 0x4cfc10 também carimbam
  +0x13c com world +0x2ef mais 1. 0x49f990 torna primeiro selecionado líder (0x49f8d0); não é atualização
  de interface, e chamá-la do tick do cliente causou crash. Definir bit diretamente (só teste) deixa retratos desselecionados
  pretos nessa cópia; clique real passa por 0x509bd0 / 0x50a1a0 (não seguido). Mensagens WM_LBUTTON
  enviadas não chegam à entrada do jogo.
- Capturas de teste: PrintWindow(PW_CLIENTONLY | PW_RENDERFULLCONTENT) na janela funciona (800x600).

Testado: host_move 25/25 (participante azul; seleção reduzida, 959,984, aparece nas duas; capturas
mostram vermelho nos seis retratos e azul nos dois do participante). Verificação do testador (2026-10-22, manual, nas cópias em execução): clicar em personagens como jogador atualiza pontos em toda cópia. Não testado: reutilização de cor após desconexão.


### <a id="a-merchant-freed-a-frame-early-on-the-shoppers-copy-4-players-2026-10-22"></a>Comerciante liberado um frame antes na cópia do comprador (4 jogadores, 2026-10-22)

trade_host com 3 participantes divergiu: atores a 300 frames após a loja ficaram 2 unidades separados, cópia do comprador era a
diferente. Fim de conversa leve liberava NPC quando registro cooperativo chegava, e registro do próprio comprador volta
um frame antes de outros o receberem (comerciante liberado em 2347 no host, 2348 nos participantes). Correção: registro
aplicado em seu frame (flag 4) libera NPC em CoopCommandAtFrame, em toda cópia no mesmo frame. Depois, 19 de
20 execuções do teste de 4 jogadores passaram; 8 registraram hash de posição de todo ator a cada frame (2200–2700) e
corresponderam nas quatro cópias em todos os frames. Única falha (execução 164447, logo após testador clicar nas
janelas): NPC 46 ficou parado em todas, depois por volta do frame 2600 andou a leste no host e ao norte nos
três participantes; mesmo estado aleatório. Causa desconhecida; não ligada à loja (250 frames após fechar). Possivelmente
igual à falha intermitente simul. Útil saber: byte de ator +0x117 difere entre cópias o tempo todo
(estado por cópia, talvez visibilidade), então não é estado de jogo a comparar.

### <a id="selection-dots-moved-above-the-name-tabs-2026-10-22"></a>Pontos de seleção movidos para acima das abas de nomes (2026-10-22)

Testador apontou que barra do esquadrão só mostra retratos dos selecionados, então retratos desselecionados
ficarem pretos no teste é visual normal do jogo, não artefato (corrigindo nota acima), e pontos nos
retratos desapareciam quando mais úteis. Pontos agora ficam acima das abas de nomes, sempre visíveis.
- Painel inferior: vtable 0x80299c, retângulo 0,472,800,600 (+0x10e de um retrato). Abas (vtable 0x80805c, 80x30, coordenadas
  do painel 236..721) em +0xfe, +0x102, ... +0x112; retratos na mesma ordem em +0x147 ... +0x15b (+0x143 é
  outra janela de retrato, 68x72).
- Acima das abas é a visão do jogo (vtable 0x804570, retângulo 0,0,800,472, slot 4 desenhar 0x4a0100, slot 0 destrutor
  0x4a34b0, ambos ret 4). Visão repinta só partes alteradas: pontos desenhados em toda parte só apareciam onde
  por acaso repintava (uma aba). Mudança dos pontos agora invalida visão inteira (slot 3 base) uma vez.
Testado: host_move 25/25, capturas de ambas: vermelho acima das seis abas, azul acima das duas do participante.

### <a id="drift-check-automatic-re-sync-2026-10-22"></a>Verificação de desvio: ressincronização automática (2026-10-22)

Toda cópia calcula hash da posição de cada ator a cada 25 frames no tick do cliente (mesmo ponto do frame em toda
cópia: hashes por frame corresponderam nas quatro em oito execuções de loja com 4 jogadores). Participantes enviam últimos 8 hashes com
consulta de seleção (" H<gen>:<frame>:<hash>,"); host compara. Dois frames verificados seguidos diferentes fazem host
ressincronizar (salvar e carregar rápido, como entrada em andamento), quando nenhuma conversa ou loja aberta, no máximo uma vez por
minuto, com aviso a todos. Byte de ator +0x117 fora do hash: difere entre cópias o tempo todo.
Testado: drift_host 25/25 (participante move NPC 3 unidades só na própria cópia no frame 139; host detecta em 150
e 175, ressincroniza 5 s após deslocamento, todos jogam novamente 8 s depois, sessão 2 idêntica); host_move e
trade_host de 4 jogadores sem alarme falso.

### <a id="recruiter-visits-without-a-reload-issue-1-2026-10-22"></a>Visitas ao recrutador sem recarga (issue #1, 2026-10-22)

Encontrado (interceptações exploratórias em recruit_sync.inc, Ghidra):
- SetMode cria tela de recrutamento em `0x4722eb`: `new 0x6c4dd0(0x153)`, construtor `0x4d6060 __thiscall(this, WGameMain*,
  [WGameMain+0x102])` (segundo argumento é visão do jogo, WGameWorld), armazenada em WGameMain+0x122. Destrutor
  de exclusão: vtable 0x808bc0 slot 0, `0x4d9280` (executa `0x4d6830`, ret 4).
- Construtor percorre pool de recrutas da campanha (`*0x8bdd2c +0x181`) e cria 88 entidades no bunker: candidatos
  com IA, inventários, armas e armadura. Destrói inelegíveis (`vt+0xdc` false ->
  `vt+0x28`) imediatamente (40 das 88). Também limpa seleção deste jogador. `0x505b00` fornece estado aleatório
  do mundo (World+0x729), ou cópia descartável de World+0x2eb quando 0x8bdd8b definido.
- Construtor anexa janela ao pai: criada em outra cópia, tela cobriu jogo dela
  (captura). Desvinculada da lista de filhos do pai (+0x14 pai, +0x18/+0x1c primeiro e último filho,
  +0x20/+0x24 irmão anterior e seguinte), não é desenhada nem recebe ticks.
- Na cópia de quem recruta, todos os candidatos não recrutados são marcados para destruição quando tela desaparece
  (caminho Done); tela nunca mostrada destrói só os 40 do construtor.

Sincronização: visita ao recrutador retém toda cópia (muda esquadrão de todos), então ficam no mesmo frame
enquanto tela aberta. Após construtor rodar, cópia de quem recruta tira novo snapshot (variáveis mantidas) e
envia registro cooperativo 7 (kRecruitOpen); toda outra, ao chegar, cria mesmo objeto de tela desvinculado e restaura
seleção: mesmas 88 entidades nos mesmos slots (registrado em ambas). Ao fechar, comparação de quem recruta (feita
após tela desaparecer) leva mudança do esquadrão, posições e 'D' para todo candidato; outros destroem
tela oculta primeiro, depois aplicam ('D' termina os 48 deixados pela tela oculta). Novo recruta já existe em
toda cópia, então nada mais é criado de bytes.
Testes (nenhum com recarga): recruit_host 28/28, recruitnew_host 28/28, recruit_join 28/28, recruitnew_join 28/28,
recruit_host com 4 jogadores 56/56, recruitnew_host com 4 jogadores 56/56.

### <a id="quest-givers-level-ups-a-scrip-deal-questbartersav-2026-10-22"></a>NPCs de missão, evolução de nível, negócio com vales (QuestBarter.sav, 2026-10-22)

Testador criou QuestBarter.sav: membro 0 (1055) junto do General Barnaky (NPC 266, B01_GenBarnaky.ent), membro
1 (997) junto do intendente Octavius (NPC 96, B01_QMOctavius.ent). Teste "survey" lista NPCs próximos dos
dois primeiros membros de qualquer save.

Encontrado (observado nos logs; descompilado onde indicado):
- **NPC de missão abre Pipboy** (WPipboy, modo 11 da tela de missão), não conversa, em toda cópia (comando
  de conversar executa em todas). Pipboy aberto na janela da reivindicação de conversa conta como tal: mantido na
  cópia de quem conversa, fechado nas outras com aviso (testador: só quem conversa vê).
- **Barra do esquadrão, um selecionado:** mostra um retrato grande e oculta seis pequenos, cujo
  campo de personagem (+0x153) então é 0. Pontos agora usam aba k = membro k (barra preenche abas na ordem
  do esquadrão; aba WSquadMember só contém nome +0x10e e HP mostrado) e encontram painel inferior (WGameBar, vtable
  0x80299c) entre filhos da tela de missão. Visão repinta pontos quando nova e a cada 2 s.
- **Evolução de nível.** Botão de efeito Level (WEffectButton, handler 0x479e60: pelo nome de efeito, "objectiveComplete" abre
  Pipboy, senão SetMode(3)) abre tela de personagem WCharacter (vtable 0x7ffa84, modo 3; EntityID
  em +0x123). Com perk para escolher, configuração (0x45ab80) cria WPickPerk (construtor 0x4b5d60, vtable 0x8063a8)
  e executa loop modal, slot 11 da vtable (+0x2c, 0x6c6190 da janela base): ticks de janela, interceptação do loop de mensagens,
  slots de atualização e desenho do próprio diálogo não são alcançados por ele. Done de perk 0x4b64b0 (perk destacado para
  vt+0x188, EndModal(4)); Cancel 0x6c62c0 (EndModal(0x10)). Done da ficha é 0x4678b0 (Cancel
  0x467e10); mudanças só chegam ao personagem em Done (alteração direta de habilidade foi sobrescrita).
- **Números de um personagem:** quatro tabelas de atributos (Stats, Traits, Skills, OTraits, Perks, vtables 0x809434,
  0x824be4, 0x824bc4, 0x824bf4, 0x824c04) desde Actor +0x2a7, separadas por 0x339; byte em +0xf8a não pertence a elas
  (diferiu entre cópias após subir nível). Operação delta 'A' leva trechos de bytes alterados das tabelas dos membros;
  testes comparam hash das tabelas de cada membro (ATTR) em toda cópia.
- **Destruições adiadas, completo:** World::DestroyEntity 0x4e4a30 põe entidade em lista pendente (World+0x759,
  contagem +0x75d), define +0x141 e seq do slot + 1; 0x4e4bb0, uma vez por frame, libera todas em ordem (0x4e5270: slot
  na lista livre, seq + 1 novamente).
- **Negócio com vales (pilha inteira gasta):** pilhas separadas pela tela para mesas de oferta existem só na
  cópia do comprador; devolvê-las as marca; medido antes de liberar, negócio entregava aos outros slots não
  liberados, e quatro slots ficaram separados por um seq. Comprador agora os libera (0x4e4bb0) antes de medir,
  quando nada mais estava pendente.
- **Mais duas dessincronizações corrigidas:** delta de conversa levava início da lista livre de snapshot coletado
  enquanto estoque de outro jogador existia (agora: sem início ou serial em delta sem mudança de entradas); criação
  esperando seu slot era destruída de novo pela proteção "destruir o que ainda está lá" (agora retirada dela).

Regras adicionadas (do testador):
- Enquanto alguém compra, outros não iniciam conversa (reteria comprador; fechamento da loja então executava
  destruições noutra ordem). Aviso: "um jogador está trocando — converse quando terminar".
- Enquanto alguém sobe nível de personagem, outros não abrem ficha desse personagem nem usam recrutador
  (registros 8/9, kLevelOpen/kLevelClose com reivindicação). Duas aberturas simultâneas: primeira pela retransmissão
  do host vence em todas; Done espera cópia saber que venceu (com host subindo nível, nenhum
  registro flui até terminar, então participante só descobria que perdeu após seu próprio Done).
- Subir nível retém só jogo de quem evolui: mudanças chegam aos outros até um segundo depois.

Testes (2026-10-22): quest_host 25/25, quest_join 25/25, levelup_host 23/23, levelup_join 25/25, levelrace 23/23,
shoptalk 25/25; no mesmo código: trade_host 48/48, trade_join 49/49, trade2_host 31/31, browse_host 29/29,
recruitnew_host 29/29, recruit_join 29/29, talk_host 30/30 (estes sete antes da trava de evolução de nível).

### <a id="what-the-games-multiplayer-layer-already-syncs-and-what-it-doesnt-2026-10-22"></a>O que a camada multijogador já sincroniza e o que não sincroniza (2026-10-22)

Método: handler de comandos lockstep (slot 510 da vtable Actor, `0x5747e0`) seleciona pelo primeiro byte do comando de 27 bytes;
chamadas de cada caso nomeadas pelos nomes de vtable Entity FTSE (`docs/vtable functions/Entity_Vtable.html`, 536 slots)
e strings dos auxiliares. Classes de janela (259 `W*`), ações de gatilhos (61) e condições (20) vêm do
RTTI do executável. "Observado" = visto em teste; "deduzido" = de nomes e descompilações, não executado.

**Comandos transportados por lockstep** (toda cópia executa no mesmo frame; deduzidos salvo indicação):
| tipo | o quê (nomes FTSE do que o caso chama) |
|---|---|
| 0x00 | mover (verificações de postura e AP; observado: movimentos do bot) |
| 0x01 | escavar / ativar torre de arma / dirigir (unidades especiais) |
| 0x02 | atacar entidade (BeginAttackAnEntity; observado: teste attack) |
| 0x03 | agir sobre entidade ao alcance |
| 0x04 | usar / ativar objeto ou item num alvo (CanBeActivated, CanUseItem) |
| 0x05 | largar item (RemoveItemFromEquippedThenInventory) |
| 0x06 | equipar, tiro localizado, munição |
| 0x07 | desequipar ("unEquip") |
| 0x08, 0x09 | mudar postura / conjunto de animações |
| 0x0a | parar |
| 0x0b | definir mão da arma ativa |
| 0x0c, 0x1d | comando de controlador de veículo |
| 0x0d, 0x22 | esquivar (SetBonusACForHTHEvade) |
| 0x0e-0x10 | modo sentinela, gatilho de precisão, local |
| 0x11 | atacar local (granadas, rajadas no chão) |
| 0x12 | recarregar |
| 0x13, 0x14 | pegar / dar item ao alcance (coletar, de contêineres) |
| 0x15 | combinar itens de inventário |
| 0x16 | agir sobre alvo ao alcance (habilidades, provavelmente) |
| 0x17 | conversar (observado) |
| 0x18, 0x19 | roubar ("steal") |
| 0x1a, 0x1b | armadilhas: ativar, definir frequência |
| 0x1e | encerrar combate (som "combatEnd") |
| 0x1f | relacionado a veículo |
| 0x20 | vigilância |
| 0x21 | definir id de alvo / líder |
| 0x23 | desconhecido |
| 0x25 | desembarcar, usar entidade, furtividade |

Portanto, movimento, combate (tempo real; por turnos também tem comandos), equipamento, pegar e largar, roubar,
armadilhas, habilidades em alvos, veículos, furtividade e vigilância já passam por lockstep.

**Telas de um jogador: quem sincroniza**
| tela (classe de janela) | estado alterado | status |
|---|---|---|
| conversa (WSpeech) | variáveis, itens, HP | mod: delta ao fechar; todos retidos (observado: talk_*) |
| instruções de NPC de missão (WPipboy a partir de conversa) | variáveis de missão | mod: só quem conversa, delta (observado: quest_*) |
| troca com intendente (WBarter, WBarterTable) | inventários, lista de estoque | mod: sem pausa, estoque em toda cópia (observado: trade_*) |
| recrutamento (WSingleRecruit) | esquadrão, novos personagens | mod: candidatos em toda cópia (observado: recruit*) |
| ficha de personagem, perks (WCharacter, WPickPerk) | atributos, habilidades, perks | mod: operação 'A', trava, corrida (observado: levelup*) |
| telas de esquadrão (WSquadWindow, WSquadSelectionWindow) | esquadrão | contadas como privadas (comparação completa); sem teste |
| **múltiplos recrutas (WMultiRecruit)** | esquadrão | não tratado: no máximo recai na comparação de tela privada; sem teste |
| **botão Gamble numa conversa (0x4d0090)** | dinheiro, itens | sem tratamento específico; sem teste |
| **troca com comerciante não intendente** | inventários | segue caminho antigo com retenção (não leve); sem teste |
| inventário (WInventory, WSquadEquip, WMemberEquip) | itens entre membros, equipar | comandos lockstep (5 largar, 6 equipar, 7 desequipar, 0x0b mão, 0x13 dar); retidos durante loja (observado: chaos com equipamentos, trade_* --inv-chaos, 2026-10-28) |
| saquear contêiner (WLoot) | inventários do contêiner e esquadrão | lockstep 0x14/0x15; entradas mortas da lista removidas em toda cópia (observado: loot, 2026-10-27); cadáveres: sem teste; WMultiEquipLoot muda inventários diretamente (nunca visto jogando) |
| **dividir pilha (WMoveStackInput, WQuantityTypeDialog)** | contagens de pilha | não verificado |
| habilidades (WSkillDex) | nenhum por si; uso é comando | provavelmente funciona |
| Pipboy pelo botão (WPipboy) | nenhum (leitura) | funciona |
| mapa mundial, viagem (WCampaign*, WWorldWindow) | destino do esquadrão | mod: só host; grupo do host mostrado em todo mapa (observado: exit_*, worldmap, 2026-10-28) |
| encontros aleatórios no mapa (WCampaignRandomWindow, WRandomDialog) | qual missão carrega | cópia do host sorteia, outras seguem save (observado: encounter, v0.8.0) |
| **salvar e carregar (WSaveLoad)** | tudo | carregamento do host ressincroniza (observado: resync); **participante carregar próprio save** não tratado |
| instruções e relatório da missão (WLoadMissionScreen, WEndScreen), cenas (WMovieWindow, ActionPlayBink) | nenhum, mas pausam | executam em toda cópia pelo mesmo gatilho; cada jogador fecha a sua |

**Riscos de scripts de gatilho** (executam em lockstep em toda cópia, então maioria das ações funciona; estes leem estado local):
- `ConditionGUIOpen`: gatilho que testa tela aberta vê telas da própria cópia.
- `ConditionRightClickOnTab`: entrada local de mouse como condição (gatilhos de tutorial).
- `ActionForceSpeech`: script abre conversa em toda cópia; regra do mod "conversa de ninguém: do host"
  a mantém no host; não testado.
- `ActionStartCombatMode`: muda para turnos; jogo por turnos não coberto por testes.

**Próximos, por risco** (atualizado em 2026-10-28; movimentos de inventário, saquear contêineres, encontros aleatórios e turnos
concluídos, ver seção de 2026-10-23 a 10-28): (1) saquear cadáveres, (2) carregamento próprio de participante, (3) fala forçada,
(4) apostas e outros comerciantes, (5) múltiplos recrutas, (6) personagem de história entrar no esquadrão (ainda recarrega).


## <a id="2026-10-23-to-2026-10-28-desync-root-cause-turn-based-two-pcs-v070-to-v093"></a>2026-10-23 a 2026-10-28: causa da dessincronização, turnos, dois PCs, v0.7.0 a v0.9.3

Repositório do mod: thennak3/fallout-tactics-coop (pré-lançamentos v0.7.0 ... v0.9.3). Todo "observado" abaixo é execução de bot
com `test/run_test.py <name>` num PC (2 a 4 cópias), ou log da sessão de dois PCs do testador onde indicado.

### <a id="observations"></a>Observações
- **Dessincronização de rajadas, causa.** `OnBurstAttack` Lua do FTSE sorteava com `math.random`, semeado por `os.time`, então rajadas
  dos NPCs de cada cópia acertavam diferente. Substituição Park-Miller determinística em `core/FTSE/ftse.lua` corrigiu (v0.7.0):
  execuções chaos com toda cópia agindo ao mesmo tempo pararam de divergir (chaos 3p 38/38).
- **Encontros aleatórios** (v0.8.0): WWorldWindow 0x6bad60 sorteia num LCG privado em ww+0x112; fila em
  campaign+4/+8/+0xc contém nomes FOTString (precisa enfileirar cópia com contagem de referências, ponteiros brutos de entradas caíam em 0x6bc980);
  despachante 0x6bcaa0(ww, 0). Teste `encounter` 26/26.
- **Por turnos** (v0.9.0): modo World+0x427 (0 tempo real, 1 Individual, 2 Squad), grupos em World+0x430, índice
  atual World+0x43c; 0x507bc0 = de quem é a vez; End Turn 0x477a80 verifica 0x6368a0 (client+0x130 contra player+0x31), interceptada
  para participante possuir slot 1. Cópia das configurações do host (World+0x749, campos como bos.cfg) vai a toda cópia como registro
  cooperativo (tipo 11) e é regravada a cada frame. Testes `turnbased` 2–4 jogadores (69/69 com 4), `tbauto` 29/29.
- **Dois PCs** (testador): descoberta em UDP 47701 falhou com WSAECONNRESET após ICMP de porta inacessível; corrigido
  desativando SIO_UDP_CONNRESET (v0.9.1). Sessão do testador então jogou de PC a PC.
- **Saque** (v0.9.2): pegar de contêiner deixava entradas mortas de lista (seq do nó em +8, slot em +10, válido só se
  seq da entrada da tabela em +6 corresponder) na cópia de quem não saqueia: desvio infinito de inventário. Removidas em toda cópia 2 frames
  após 0x14/0x15. Teste `loot` 24/24.
- **Conversas** (v0.9.2): trava de NPC deixada por conversa perdida bloqueava toda ressincronização posterior. Travas agora contêm quem conversa
  e são liberadas ao abrir conversa / comando que não é conversa. Testes `talk2` 28/28, `talk2same` 27/27.
- **Crash ao sair da sessão ao menu principal** (testador, 3 vezes; WER 0xc0000409 em netlog.dll, `__report_gsfailure`).
  Dump: slot de proteção de PumpHandlerHook continha endereço de retorno um slot acima. 0x4ca7b0 (Single Player > Load)
  é `__thiscall(menu, int unused)`, `ret 4`; era chamada como `__fastcall(menu)`. Teste `menu_join --menu-cancel`:
  chamada antiga termina com 0xC0000409, corrigido 36/36. Agente Sonnet verificou ~85 outras chamadas diretas ao jogo: todas correspondem.
- **Verificação de desvio silenciosa após uma correção** (log do testador): frame de correção era mantido entre carregamentos, que
  reiniciam contagem de frames, então nada era comparado no resto da noite. Agora por geração, com linha
  "matches ours" uma vez por minuto.
- **Loja + movimentos de inventário separavam cópias** (noite de bunker do testador; reproduzido duas vezes por `trade_host --inv-chaos`).
  Loja não pausa ninguém; cópia do comprador cria e destrói entidades em cada oferta (visto: criou 702, destruiu 702
  e 1095 no frame 2310 só no host), então uma transferência no frame 2313 pegou slots livres diferentes em cada cópia.
  Comandos 04/05/06/07/13/14/15 agora esperam desde frame de abertura até o frame após fechamento em todas.
  `trade_host --inv-chaos` 48/48, `trade_join --inv-chaos` 49/49.
- **Equipamento**: Actor+0x100e contém três handles {seq, slot} (mãos 0 e 1, armadura 2; getter vfunc +0x54c, 0x5581a0),
  byte de mão ativa +0x1029. Equipar pela interface são comandos lockstep (WSquadEquip 0x46f940 / 0x46f520 / 0x470290 -> wrappers
  0x631320 cmd 6, 0x631300 cmd 7, 0x631a80 cmd 0x0b). Agora nos snapshots, hash de desvio e correção ('G').
  Teste `drift_equip` 25/25 (corrigido, sem recarga).
- **Crescimento da tabela de entidades** (0x4e50c0): com lista livre vazia, tabela cresce para max(1000, 2n) via 0x4e7ed0, novos
  slots encadeados N..2N-1 -> 0. Durante tela privada, isso forçava recarga (testador viu 2000 -> 4000 durante
  ficha de personagem); agora delta informa ('T'), e toda cópia cresce igual. `talk_host --grow-table` 30/30,
  `talk_join --grow-table` 31/31.
- **Demoras para entrar**: consultas fixas de 1–2 s (geração, nova tentativa de sessão, mensagem de espera) agora 250 ms. Release DirectPlay
  da tela Multiplayer (0x759976 em 0x759960) bloqueia cerca de 3 s (dpwsockx+0x7eca WaitForSingleObject INFINITE na
  própria thread); movido a uma thread. Entrada em andamento 7,9 s -> 3,5 s; ressincronização do carregamento do host até jogar
  2,7 s -> 0,9 s.
- **Mapa mundial**: grupo move em 0x6ba780 (tempo real, dt limitado a 0,1 s) rumo a ww+0x10a/+0x10e enquanto ww+0x101
  definido, posição em campaign+0xa5/+0xa9; cliques vão a 0x6ba410 (thiscall(ww, float dest[2]), ret 4). Grupo do
  host agora acompanha consulta de geração dos participantes; viagem e sorteio de encontro do participante desativados. Teste `worldmap` 31/31.
- **Marcações no mapa mundial** (v0.9.4): mouse pressionado WWorldWindow é slot 51 da vtable (0x82dbd0 -> 0x6ba2a0, thiscall(ww, int pt[2]
  local da janela, int button, int), ret 0xc; botão 1 viaja, outros nada fazem); desenho é slot 4 (0x82db14 -> 0x6bbb00);
  ponto do mundo = pt + campaign+0x9d/+0xa1 (rolagem). Retângulo do renderizador (+0x24) desenha contorno de 1 px, não preenchimento.
  Janelas de teste em segundo plano não recebem entrada de mouse enviada e rolam pelas bordas se cursor fica num canto. Teste
  `worldmap` 33/33 (marcações no mesmo ponto nas duas, vistas em captura); direito = botão 2 não verificado.

### <a id="derived-1"></a>Deduções
- Multijogador do jogo nunca teve combate NPC contra esquadrão nem telas privadas de um jogador; toda dessincronização encontrada
  veio de algo executado só numa cópia (RNG Lua, mudanças de entidades de tela privada, trava perdida), não do
  núcleo lockstep.
- Tudo que tela privada faz à tabela de entidades precisa chegar aos outros como controle interno, e comandos lockstep que
  alocam não podem intercalar com isso.

### <a id="guesses"></a>Hipóteses
- Tabela do testador cresceu 2000 -> 16000 numa noite; crescer exige lista livre vazia, então slots livres podem estar sendo perdidos
  em algum lugar (talvez nossas próprias gravações de controle interno).

### <a id="unknown-1"></a>Desconhecidos
- Por que cópia do participante enviou seu save aos 1031 s em 2026-10-27 (sem log dele); provavelmente verificação de crescimento da tabela.
- Saquear cadáveres, participante carregar próprio save, fala forçada, apostas, outros comerciantes, múltiplos recrutas.
- (Depois, 2026-10-28) Névoa de guerra estava listada aqui como não compartilhada; é: campaign +0x1ad a contém (colunas de células
  de 0x38 bytes, primeiro int de 0 não visto a 2 visto), participantes carregam com save do host e grupo segue o dele,
  então ambos revelam mesmas células (`worldmap`: 45 -> 46 células, mesmo hash em ambas, 35/35).
- (Depois, 2026-10-28) Hipótese do crescimento estava certa: controle interno de delta, regravado após destruições
  adiadas, cortava slots liberados da lista livre (94 por visita ao recrutador, 3 por evolução, igual em toda cópia).
  Corrigido recolocando todo slot não usado inalcançado nela em ordem de slot (`recruit_host` perdeu 94 -> 0).

