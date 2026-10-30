# <a id="metroid-prime-2-echoes-trilogy-co-op-notes"></a>Cooperativo de Metroid Prime 2: Echoes (Trilogy): notas

Referência técnica por trás do [README.md](README.md). Todos os endereços são de `rs5mp2_p.dol`, SHA-1
`2375606f4e9429a699cfa02728b0bb1176421226`, de Metroid Prime Trilogy NTSC-U `R3ME01` rev 0. Os nomes das funções
são os `FUN_xxxxxxxx` do Ghidra, a menos que se conheça um nome melhor. “Em execução” significa lido ou escrito no jogo em execução
com o efeito observado; “estático” significa apenas desmontagem.

## <a id="game-engine-executables"></a>Jogo, engine e executáveis

- Metroid Prime Trilogy (Wii, 2009), disco extraído. Engine da Retro Studios, PowerPC big-endian, binário fechado.
- O front-end `rs5fe_p.dol` (= `main.dol`, SHA-1 `d55b890c4e7c2cc6f2e120ec4ef988c186780308`) carrega
  `rs5mp2_p.dol` quando Echoes começa e é recarregado ao sair de Echoes, portanto cada patch depende de rs5mp2
  estar residente (consulte Empacotamento).
- Inimigos e muitas classes de scripts são módulos RSO carregados em tempo de execução (`MP2/RSO/Production`); seus `bl`s
  não têm relocação aplicada no disco (0x48000001), portanto só é possível encontrar os chamadores em execução. Bases SDA: r13 0x805d1660, r2 0x805d4280.
- A tabela PRIME_2 NTSC do PrimeHack corresponde a este DOL, mas o PrimeHack controla apenas o jogador 1; use o Dolphin oficial,
  com um núcleo (dois núcleos causaram uma dessincronização do FIFO da GPU na introdução de Echoes).
- O modo versus de Echoes já executa de 2 a 4 atores Samus, câmeras e HUDs em um mundo; o mod carrega o mundo
  da campanha nesse modo e corrige o que pressupõe um jogador.

## <a id="existing-work"></a>Trabalhos existentes

O mod cooperativo de Trilogy de 2019 de SubsonicBeatz154, feito apenas com assets (abandonado), listava os obstáculos que exigem código: a morte encerra
a partida, estações de salvamento desativadas, salas seguem o jogador 1, teletransportes entre mundos sobrescrevem inventários, Scan Visor inoperante,
inventários separados, fogo amigo, inimigos miram no jogador 1, câmeras de cenas quebram para o jogador 2. A tentativa de xjonx
no GameCube atingiu o limite de memória do multijogador. O multiworld do Randovania conecta jogos separados de GameCube.

## <a id="memory-map"></a>Mapa de memória

### <a id="globals"></a>Globais

| Endereço | Descrição |
|---|---|
| 0x804e72e8 | `CStateManager` (objeto estático em .bss) |
| 0x805cb314 | `CGameState*` (= r13-0x634c); +0 mundo MLVL atual; +0x148 objeto de regras (ponteiro possuído em +0x144) |
| 0x805cb220 | opções/dados do sistema (r13-0x6440): +0x29 flag de carregamento, +0x2c índice do arquivo de salvamento, +0x80 dificuldade |
| 0x805cb310 | objeto da aplicação; +0x70 -> +0x114 possui o estado do jogo |
| 0x805cb338 | flag do caminho de inicialização (1 = caminho InitialWorld/FrontEnd) |
| 0x804a4f20 | tabela de capacidade máxima dos power-ups [109] |

### <a id="cstatemanager-0x804e72e8"></a>CStateManager (0x804e72e8)

| Offset | Descrição |
|---|---|
| +0x810 | lista de objetos |
| +0x8e4 | fila de mensagens (processada por FUN_80244c08) |
| +0x14f0 | contagem de jogadores u32 (1 no modo individual, 2–4 no versus) |
| +0x14f4 | `CPlayer*[4]`, indexado pelo número do jogador (cerca de 30 funções leem `sm + idx*4 + 0x14f4`) |
| +0x1504 | `CPlayerState*[4]` (igual a players[i]->+0x12ec) |
| +0x1514 | gerenciadores de câmeras, 4 bytes por viewport; gerenciador +0x12 = uid da câmera cinematográfica atual (0xffff nenhuma), +0x14 câmera em primeira pessoa |
| +0x153c | estado de carregamento |
| +0x1da0 / +0x1da4 / +0x1da8 | jogador / estado / gerenciador de câmeras usado para o viewport sendo desenhado (definido por FUN_8024b72c) |
| +0x1dac | `CWorld*`: +0x24 contagem de áreas, +0x2c array de áreas (8 bytes, +4 = `CGameArea*`), +0x54 lista de áreas carregadas (próximo em +0xd4) |
| +0x1e28 | dados de mapa/automapa (existem no cooperativo) |
| +0x1e44 / +0x1e48 | índice da área atual / anterior |
| +0x1e98 | passes de filtro de câmera: 0x2c cada, 11 por viewport, 0x1e8 por viewport; passe 1 em +0x1ec4 (P1), +0x20ac (P2) |
| +0x2bd0 / +0x2bf0 | id STRG / tempo da caixa de mensagem |
| +0x2c0c | estado de pausa: 0 nenhum, 1 mapa, 2 (função especial 37), 3 menu de pausa MP, 4 Data Network, 5 solicitação de salvamento, 6 caixa de mensagem |
| +0x2c78 | índice do viewport sendo desenhado |

Escritores de +0x1e44: SetCurrentArea FUN_8023eb60(mgr, &idx), FUN_8023f6c0 (surgimento), FUN_8023be44 (carregamento).

### <a id="cplayer"></a>CPlayer

| Offset | Descrição |
|---|---|
| +0x8 | uid da entidade (u16; CEntity), +0xc id do editor |
| +0x20 | transformação (3x4, translação em +0x2c/+0x3c/+0x4c); escrevê-la não move o jogador |
| +0x50 | posição usada por docks, gatilhos e IA |
| +0x1a0 | velocidade |
| +0x2c4 / +0x374 / +0x378 / +0x390 | estado de movimento / câmera / transformação / órbita (órbita 1 = alvo fixado) |
| +0x39c | uid do alvo da órbita (fixação de alvo); +0x3c8 candidato à fixação de alvo |
| +0x5a4 | estado de escaneamento (0 nenhum, 1 escaneando, 2 concluído); +0x5a8/+0x5ac tempo de escaneamento, +0x5b0 uid do alvo, +0x5b4 id do asset de escaneamento |
| +0x5f0 | inclinação vertical em primeira pessoa |
| +0xec0 / +0x138c | ativação do buffer de ids / buffer 64x32 por jogador dos ids dos objetos na tela (Scan Visor) |
| +0x12ec | `CPlayerState*` |
| +0x12f0 | gerenciador de câmeras (o código do jogador consulta nele se está “em uma cena”); +0x18 câmera da Morph Ball |
| +0x1388 | índice do jogador |

Teletransporte de jogador: FUN_80160cc4(CPlayer*, CTransform4f*, mgr, bool). O último argumento reinicia a câmera da Morph Ball
(via +0x12f0 -> +0x18, vt+0x84); SpawnPlayer e chegadas passam 1, pontos de surgimento passam 0.

### <a id="cplayerstate-ctor-fun_8016d008this-playerindex-persistent-size--0x5b0"></a>CPlayerState (ctor FUN_8016d008(this, playerIndex, persistent); tamanho >= 0x5b0)

| Offset | Descrição |
|---|---|
| +0x00 | índice do jogador |
| +0x04 | flags; bit 0x80 = vivo (regras de deathmatch), bit 0x40 limpo = imune (verificado por FUN_8014baa4) |
| +0x10 | 99.0 ao surgir, não é a vida em tempo real |
| +0x14 | vida atual (f32) |
| +0x34 | visor atual (0 Combat, 2 Scan; setter FUN_8016e000) |
| +0x38..+0x40 | vector<u16> {tamanho, capacidade 0x20, data*} |
| +0x50 | traje atual (0 Varia, 1 Dark, 2 Light), recalculado quando os ids 12–14 mudam |
| +0x54 | contagem de power-ups = 0x6d (109) |
| +0x58 + id*0xc | powerups[109]: {s32 quantidade; s32 capacidade; u32 extra} |
| +0x588 | índice do controle (definido por FUN_8016d76c) |
| +0x594 / +0x59c | mapa de escaneamentos: contagem / entradas de 8 bytes {u32 id do escaneamento, u8 progresso (0xff = concluído), preenchimento}; todos os 821 ids pré-listados |

Funções de acesso (ps, id, n; todos verificam os limites id < 0x6d): FUN_8016d998 InitializePowerUp (capacity += n, limitado a
0x804a4f20[id]; amount = min(amount, capacity)); FUN_8016d984 capacity = 0 e depois o anterior; FUN_8016db60 IncrPickup
(amount += n, limitado; ids 41/42 repõem vida); FUN_8016daec amount = 0 e depois IncrPickup; FUN_8016dc10
DecrPickup; FUN_8016de44 define a quantidade; FUN_8016de70 / FUN_8016debc capacidade; FUN_8016de90 HasPowerUp (chamado
a cada quadro pelo HUD); FUN_8016db00(ps, f) health += f; FUN_8016e39c(ps, id, f1) SetScanTime (byte quantizado
em entry+4) / FUN_8016e29c GetScanTime.

Ids dos power-ups (correspondem ao cabeçalho `prime2` do Randovania): raios 0 Power, 1 Dark, 2 Light, 3 Annihilator, 22 Charge;
combos 4 Super Missile, 5 Darkburst, 6 Sunburst, 7 Sonic Boom; visores 8 Combat, 9 Scan, 10 Dark, 11 Echo;
trajes 12 Varia, 13 Dark, 14 Light; 15 Morph Ball, 16 Boost, 17 Spider, 18 Bombs; 23 Grapple, 24 Space Jump,
25 Gravity Boost, 26 Seeker, 27 Screw Attack; chaves 29–31 e 101–106 Sky Temple, 32–40 Dark Temple;
41 reposição de vida, 42 Energy Tank, 43 Power Bomb, 44 Missile, 45 Dark Ammo, 46 Light Ammo, 47 % de itens,
0x2f contador de itens coletados, 0x40 abates, 0x41 mortes (salvos com o estado), 0x61 usado por uma condição posterior de bloqueio,
97–100 tradutores. Desconhecidos: 19–21 (capacidade 1 no versus), 80 (capacidade 9999 no versus).

### <a id="game-state-and-rules"></a>Estado do jogo e regras

- CGameState (0x640 bytes, ctor FUN_800b9178): +0 mundo atual; +0x8/+0x10 estados de mundos (0x24 cada: +0 MLVL,
  +4 índice da área, +0x18 MREA desejada); +0x14 contagem de estados de jogadores (4), +0x18 rc_ptrs dos estados de jogadores (8 bytes cada);
  +0x74 + 8i entradas MP por jogador; +0x14c configurações MP ('FRND', 0x64 bytes); +0x638 bit 0x40 força equipamentos iniciais.
- Novo jogo: FUN_800ba8ac fixa o mundo 0x3bfa3eff (Temple Grounds) e a área 0x62b0d67d (Landing Site) em
  0x800ba8e0–0x800ba900 (`lis r31` em 0x800ba8e0, `addi r4,r31` em 0x800ba8e8/0x800ba8f4). Reescrevê-los
  inicia um novo jogo no ponto de surgimento padrão de outra área (um auxílio útil aos testes).
- Objeto de regras = `*(*(0x805cb314)+0x148)`; tag do modo de jogo de vt+0x44: 'SNGL' individual, 'FRND' front-end,
  'DTHM' (0x4454484d) deathmatch, o modo em que o cooperativo roda. IsMultiplayer FUN_8024b4fc = não SNGL/FRND.
  - Regras do modo individual vt 0x804b9648 (SpawnPlayer = `blr`).
  - Regras de deathmatch vt 0x804b4838 (construídas por FUN_800760d8). vt+0x1c SpawnPlayer FUN_8010cd94, vt+0x20
    0x8010d580 (`li r3,1; blr`, “aplicar equipamento de surgimento”), vt+0x38 IsGameOver FUN_80076644.
  - Campos: +0x04 limite de tempo (600.0), +0x08 decorrido (avançado por `stfs f0,0x8(r31)` em 0x8010d560 no tick
    FUN_8010d528), +0x38 contagem de jogadores, +0x3c limite de abates, +0x40 flags (0x80 fim de jogo, 0x40 limite de abates ativado,
    0x08 limite atingido), +0x4c + 0x14i por jogador {f32 temporizador de reaparecimento, u8 morto}.
- Atualização de deathmatch FUN_800762e8: por jogador, a morte é detectada em 0x80076400 (`rlwinm.` no bit 0x80 de state+4),
  marca como morto, define o temporizador e incrementa o item 0x41; a cada quadro o temporizador diminui (`lfs f0,0(r23)` em
  0x80076414), depois FUN_80140cec(player, mgr) e SpawnPlayer (chamada em 0x80076450). Verificação do limite de abates:
  `blt +0x40` em 0x800764bc; prosseguir sem o desvio define +0x40 |= 8 e chama vt+0x40, vt+0x3c (fim da partida, 0x800764c0).
- SpawnPlayer FUN_8010cd94 reconstrói CPlayerState do zero (novo estado via FUN_8016d008 copiado sobre o
  estado em execução, blocos persistentes mantidos via FUN_8016e770/FUN_8016e88c), aplica o equipamento do ponto de reaparecimento a todos os
  109 slots, teletransporta e então notifica `SPWN` (`bl 0x8010ca50` em 0x8010d478). É o caminho de reaparecimento após morte.
- Surgimento de chegada FUN_8023f45c(mgr, spawn point, player index), chamadores 0x8023fe68, 0x8023fed0 (padrão do modo
  individual), 0x80240090 (laço MP por jogador): teletransporta e só então aumenta para o equipamento do ponto de surgimento se as regras
  vt+0x20 != 0 (único local de chamada 0x8023f578) ou o bit 0x40 de game state +0x638 estiver definido. Usado no início da sessão e em cada
  mudança de mundo por WorldTeleporter.
- Início de partida MP FUN_800ba388 (máquina de estados FUN_800eacec(..., 8), regras do front-end 'FRND'): constrói as regras
  DTHM, reconstrói o estado do jogo por um ciclo de salvar/carregar (FUN_802a9174; o mundo passa a ser o da arena), instala
  as regras (FUN_800bc414 em 0x800ba6a0), escreve as configurações MP e as entradas por jogador (state+0x588), termina com
  FUN_800ba230, FUN_800bb364(gs), FUN_8017e00c(gs+0x94); epílogo 0x800ba7d0.

### <a id="spawn-points-world-teleporters-special-functions"></a>Pontos de surgimento, teletransportadores de mundos e funções especiais

- CScriptSpawnPoint (vt 0x804b8950, AcceptScriptMsg FUN_8020c5f4): +0x04 área, +0x1c flags (bit 31 primeiro
  surgimento), +0x20 transformação, +0x54 + 4*id quantidade do equipamento, +0x20c + 4*id substituição da capacidade (getters FUN_8020c594,
  FUN_8020c5bc).
  - `RSET`: para cada jogador e cada id, FUN_8016d984 (0x8020c65c) e FUN_8016daec (0x8020c67c), ou seja,
    todo o inventário é substituído pelo equipamento; depois teletransporta cada jogador se o bit 31 estiver definido. RSET vem apenas
    de scripts de fase (mudanças de equipamento da história: a introdução em Landing Site, a perda de itens).
  - `ZERO`: carrega a área de destino se necessário, SetCurrentArea, teletransporta cada jogador (sem mudança no inventário).
- CScriptWorldTeleporter vt 0x804b95a8, AcceptScriptMsg FUN_8022da4c; +0x1c ativo, +0x20 MLVL, +0x24 MREA,
  +0x2c bit 0x40 pula a transição. O mundo do front-end MP 0xdaea74a3 tem um para cada arena; o de Sidehopper Station
  aponta para MLVL 0xa50a80cc / MREA 0x02690de1. Ele recebe XCRT/XALD/XWLD, ACTV no início da partida, XDEL; nunca ZERO.
  Uma mudança de mundo por ele gera o surgimento via FUN_8023f45c (apenas aumenta), não SpawnPlayer nem RSET.
- CScriptSpecialFunction vt 0x804b8cb8, tipo em +0x150, AcceptScriptMsg FUN_802107f4 despachando por uma
  tabela de funções-membro em 0x804b8958 (12 bytes por tipo). Tipo 5 estação de mapa FUN_8020e598, tipo 7 estação
  de salvamento FUN_8020e800, tipos 31–34 concessão de power-ups FUN_8020f780/f838/f8d4/f9ac (item +0x208, quantidade +0x174, seletor
  de jogador +0x170 resolvido por FUN_802147ec, concessão FUN_80241a98), tipo 37 FUN_8020fbe4 (estado de pausa 2).
- A entidade vt 0x804b8678 (FUN_802031e4) em ZERO concede o item +0x20 (capacidade +0x28, quantidade +0x24) apenas ao estado 0.
- Conexões de scripts são {estado, mensagem, u32 id do editor}; o id do editor do destino fica em +0xc.

### <a id="areas-docks-doors"></a>Áreas, docks e portas

- CGameArea: +0x3c xyz mínimo, +0x48 xyz máximo, +0x8c contagem de docks, +0x94 docks (0x48 bytes cada; pontos do plano em
  +0x14/+0x20/+0x2c), +0xd0 == 0x10 quando carregada (o teste da própria rotina think do dock, FUN_8009af64/FUN_8009af7c).
- CScriptDock (tipo 55, vt 0x804b8088, think vt+0x14 FUN_801e6a84): +0x2c8 índice do dock, +0x2cc índice da área,
  +0x2d0 estado (1 -> 2 armado, 3 = em uma área que não é a atual), +0x2d4 flags. No estado 2, testa
  `bl FUN_801e6cec(dock, mgr, players[0]+0x50)` em 0x801e6bf8 (r30 dock, r31 mgr); se cruzado e o outro
  lado estiver carregado, chama SetCurrentArea. É por isso que apenas o jogador 1 conseguia mudar a sala.
- CScriptDoor (tipo 56, vt 0x804b8128): seu gatilho (tipo 92) envia ENTR->INCR / EXIT->DECR; a porta envia ao seu
  dock OPEN->INCR e CLOS->DECR, portanto uma porta fica aberta enquanto alguém estiver no gatilho. O tratador de mensagens do dock
  FUN_801e64bc trata INCR/DECR e termina em `bl 0x801e6398(opened, other side's CGameArea*, CWorld*)` em
  0x801e6a5c. O descarregamento de salas (ULOD) vem do streaming, não da porta.
- Somente docks, pontos de surgimento e o gerador de chegada chamam SetCurrentArea; portais usam esses caminhos. Plano a partir de
  três pontos: FUN_8033b77c(out {n, d}, a, b, c), normal em direção ao lado cruzado.

- Raio de colisão estática: FUN_800a2ac8(mgr, &start, &unit dir, &filter, f1 length) -> 1 se o caminho estiver livre. Filtro conforme
  construído pelo teste de linha de visão da IA: {u64 include = 1 << *(r13-0x78d8) (bit solid), u64 exclude 0, u32 type 1};
  FUN_802b8834 é o deslocamento de 64 bits.

### <a id="cameras-hud-pause-messages"></a>Câmeras, HUD, pausa e mensagens

- Tratador de mensagens de câmera FUN_801dafbc: uma câmera iniciada/parada por um jogador vai para o gerenciador desse jogador
  (índice FUN_8024ba90), outros remetentes vão para o do jogador 1. FUN_8005c1d0(manager) = cena ativa; FUN_8005c1ec =
  ativa com a flag de multijogador da câmera (+0x2c -> +0x208 bit 1); FUN_8005c024 a encerra. O desenho de nível superior
  FUN_800e885c e o layout dos viewports FUN_8024b554 se reduzem a uma visão quando FUN_8005c1ec(do gerenciador de players[0]) é verdadeiro.
- Quadro: passe do mundo FUN_800e84d4 para todos os viewports (seleção de viewport FUN_8024b72c), depois passe do HUD FUN_800e864c
  (`cmpwi r4,0` em 0x800e8654 o pula na visão única; limite do laço em 0x800e870c), desenho do HUD FUN_800dd98c ->
  FUN_801577fc (janela de mensagem em 0x80157d20).
- HUDs: objeto de quadro +0x18 -> contêiner de HUDs, HUD k em +0x60 + 8k. O ctor do HUD FUN_80156d7c constrói o objeto de quadro
  de mapa/pausa de 0x3ac bytes (+0x30) somente quando HUD+4 (flag de modo individual) está definido. HUD_SET_MODE 0x80159854 (1/2 mapa,
  3/4 pausa, 6 mensagem, 7 menu MP “Quit Game?”).
- Passe de filtro de câmera: CCameraFilterPass::DisableFilter 0x80056bf8(this, f1 fade time). Uma morte escurece o passe 1 até
  preto em cada viewport; arenas versus o limpam com seus próprios objetos de script, salas da campanha não.
- SetPauseState FUN_8024ab94(mgr, state) ignora toda solicitação sob regras MP (`bl IsMultiplayer; cmpwi; bne`
  em 0x8024abb0–0x8024abb8). Mostrar mensagem FUN_8024ac68(mgr, STRG, f1) define +0x2bd0/+0x2bf0 e estado 6; a
  tela de mensagens FUN_800e8d50 -> FUN_801599b0 desenha uma caixa paginada no HUD 0.
- Entrada do controle: FUN_800ddc04(huds, mgr, input) fornece cada CFinalInput apenas ao HUD cujo state +0x588
  é igual a input +4 (`cmpw r7,r0` em 0x800ddc28, dentro de um laço `bdnz`); FUN_80158a40 -> FUN_800f82f0 (mensagem).
- Botão de pausa = ação de jogo 0x43 (Wii 2), tratada em FUN_800e8xxx; tratador do estado 4 FUN_800e8ccc. Botão de mapa =
  ação 0x44 (Wii 1) em FUN_80241530; mapa aberto por FUN_800e8bcc; posicionamento HUD+0x1e4 recalculado a cada quadro por
  FUN_80157320; atualização do automapa FUN_8002b824, desenho FUN_8002a3b0. Locais: consulte o código K.

### <a id="scanning"></a>Escaneamento

- Can-scan FUN_80149f3c exige manter a ação 0x42 pressionada (FUN_8014ed30) e órbita fixada; depois retorna falso sob MP
  para alvos que não sejam jogadores. SetScanningState FUN_80149d30 abre o painel de escaneamento (ScanPause FUN_8024b1d4) apenas no modo
  individual; a conclusão envia ao alvo sua mensagem de escaneamento concluído (0x8014a430). Ator vt+0x78 -> informações de escaneamento
  {+0 SCAN id, +4 STRG id}; CastToActor FUN_8029fd70.
- Atualização de candidatos à fixação de alvo FUN_80166a38: no Scan Visor, o modo individual usa a busca de alvos de escaneamento
  FUN_8016a8fc (lê o buffer de ids); o MP recorre à busca de combate, que nunca oferece pontos apenas escaneáveis
  (travas de portões, estações de mapa). Atualização da mira de escaneamento FUN_8016a410. SetOrbitTarget FUN_80168598, SetOrbitState
  FUN_80168670. Os buffers de ids são cópias da GPU (FUN_8024bf80 -> gráficos vt+0x138) de cada região de viewport.

### <a id="damage"></a>Dano

- ApplyDamage FUN_80242338(mgr, &damager, &damagee, &radiusSender, info, filter, knockback); caminho de dano em área
  FUN_80243a70. Ambos chamam FUN_802429ec(out, mgr, &damager, &radiusSender, &damagee, info) (chamadas em 0x802423b0
  e 0x80243ad4) para construir o CDamageInfo final (+4 dano, +8 dano em área, +0x10 repulsão).
- ObjectById FUN_8023e9fc(mgr, &uid); CastToWeapon FUN_8029ede0, uid da entidade que disparou a arma em +0x2c8.

### <a id="enemies-and-ai"></a>Inimigos e IA

- Laço think por entidade FUN_80240720: `bl 0x80240994(mgr, entity, f1)` em 0x80240be8 chama vt+0x14 Think.
  Laço PreThink FUN_80240c40 (vt+0x10 via `bctrl` em 0x80240d50). Passe Touch 0x80240888–0x80240944.
- Mensagens: imediatas FUN_8024b388 (`bctrl` 0x8024b3d0) e processamento da fila FUN_80244c08 (`bctrl` 0x80244c70);
  tudo enviado com FUN_8024b3ec, inclusive dano, é enfileirado. Mensagem: +2 remetente, +4 alvo, +8 tipo.
- IsA: FUN_8029da94(entity, type id); cada função IsA no DOL compara `cmpwi r4,N` (id de tipo lido da
  palavra 0 de vt+0xc). CPatterned é o tipo 4.
- CPatterned: InDetectionRange FUN_80130864 percorre todos os jogadores; InRange FUN_8013071c, InMinRange FUN_80130794
  (+0x3c4), InMaxRange FUN_801307fc (+0x3c8) e o temporizador “jogador longe demais” em Think FUN_8012b93c (0x8012c2ac:
  +0x3e0 conta enquanto players[0] está além de +0x3d8 = 25; desiste em +0x3dc = 5 s) leem apenas players[0].
  Linha de visão FUN_80130bbc.
- Uid armazenado do jogador-alvo, definido uma vez a partir de players[0] (id de tipo: classe +campo): 117 Boost Guardian +0x1098,
  149 Alpha Blogg +0x9b0, 132 Space Pirate +0x31c, 118 Jump Guardian +0x9f0, 113 Quadraxis (DigitalGuardian)
  +0x1052, 116 Ing +0xd7c, 134 / 135 Splitter +0xcd8 / +0xf0e, 127 Rezbit +0xca2. Uma varredura estática de todos os RSO
  por “players[0] -> lhz 8 -> sth OFF(obj)” também encontrou ChozoGhost +0x31c, CommandoPirate +0xbe2, DarkCommando
  +0xca4, DarkSamus +0x700 (111; redefine o alvo sozinho), FlyingPirate +0xacc, IngSnatchingSwarm +0x3f6, MediumIng
  +0x700, ScriptCannonBall +0x122. Também vistos em um jogo novo: Quadraxis 112, Grenchler 115, Elite Pirate 114,
  Sandworm 130. `lwz rX,0x14f4(rY)` por RSO: Dark Samus 46, Sandworm 38, Grenchler 36, Digital Guardian 34,
  Sand Boss 29, Splinter 28, Emperor Ing 3 23.
- CScriptPickup vt 0x804b8498: Think FUN_801f7d04 (jogador mais próximo em +0x1b8), Touch vt+0x50 FUN_801f8b2c(pickup,
  other, mgr); item +0x150, quantidade +0x154, capacidade +0x158, +0x15c somado a 0x2f, +0x1c8 bit 0x10 = variantes “set”.
- Zonas seguras (classe RSO, subclasse de gatilho) e plataformas de salvamento/elevador são gatilhos: rastreiam todos os atores.

### <a id="saves"></a>Salvamentos

- Dados salvos por arquivo = um blob de estado do jogo de 2000 bytes (um registro 'GMST' por arquivo usado; o terceiro arquivo em 0x5d84).
  FUN_801b2414(slot) -> FUN_802a9e88(app, memstream) substitui o estado do jogo. Tarefa de carregamento: FUN_801ad590(mem, 0)
  (0x5c bytes, de operator new 0x80315990), FUN_801ad764(task, 1), FUN_801adfcc(task, file). Estações de salvamento
  salvam no arquivo `*(0x805cb220)+0x2c` (FUN_801ade7c). Um salvamento contém os estados dos 4 jogadores.
- Respostas à solicitação de salvamento exibem uma mensagem: estação Yes 0x1dffe3e7 / No 0x50b34a43, nave Yes 0x47816a80 /
  No 0x0acdc324.

## <a id="packaging"></a>Empacotamento

- Um código Gecko combinado: a condição de proteção, escritas `04` de uma palavra e, por hook, um stub C2
  `lis r12; ori r12; mtctr r12; bctr` para um corpo em MEM2. Cada corpo termina com o mesmo salto distante para site+4.
  r12 e CTR devem estar livres em cada local (substituem uma chamada, ficam na entrada ou no epílogo de uma função, ou r12 está
  morto). Exceções com CTR em uso permanecem como corpos C2 inline: 0x800ddc28 (um laço `bdnz`; um salto distante ali derrubou
  o menu MP do front-end em 0x800ddc24), 0x80157c14, 0x80157c84.
- Os corpos são escritos por um patch `[OnFrame]` do Dolphin em 0x93700000–0x93800000: acima da arena MEM2 do jogo
  (limite superior 0x935e0000) e do heap do IOS (0x935e0000–0x93600000); tudo zerado sob o HLE IOS do Dolphin. MEM1 não tem espaço livre
  (limite superior da arena = início da FST 0x817fa320). OnFrame se aplica a cada quadro, portanto os corpos não ficam desatualizados, mas alterações em execução
  feitas neles externamente não persistem. Dados MEM2 usados pelos códigos: 0x937f0000 reserva de vidas, +4 vidas por jogador,
  0x937f0010 flag de HUD por cima, 0x937f0014 controle que abriu a Data Network.
- A lista de códigos do Dolphin começa em 0x80002338 e deve terminar abaixo de 0x80003000 (0x80001800–0x80003000 pertence
  ao tratador de códigos). Códigos além do limite são descartados silenciosamente; antes da mudança para MEM2 a lista chegava a
  0x80002ff0. Escrever code caves nessa faixa com códigos `06` só funciona enquanto a lista é curta.
- Proteção: 23 palavras `20` (se igual): 0x8014bacc = 0x4082000c, 0x8023fe68 = 0x4bfff5f5, 0x804b4854 = 0x8010cd94
  (palavras em que nenhum patch toca), mais uma palavra a cada 256 KB do texto de rs5mp2 (0x80006508 a 0x8049ff00, cada uma distante
  dos locais dos patches; listadas como `GATE` em `coop_patches.py` do projeto). Com apenas as três primeiras, sair de
  Echoes permitia ao tratador de códigos aplicar patches ao front-end que estava entrando durante um quadro (0x80076414 continha o desvio do stub C2,
  0x800bc6a0 a palavra de dificuldade), o que então causava uma falha em um corpo de hook ("Invalid read from 0x000014f0,
  PC = 0x93702078"). Com 23, sair do multijogador para o menu principal deixa o front-end intacto.
- Cada palavra original é verificada contra o DOL antes de construir os códigos (uma palavra deslocada incorreta uma vez
  causou uma falha na inicialização). O Dolphin invalida blocos JIT para código escrito por Gecko; escritas externas em código já
  compilado exigem limpar o JIT (salvar e carregar um estado).
- Estados salvos contêm a lista de códigos do Dolphin (ela reside na RAM do jogo): um estado criado com códigos antigos executa os
  códigos antigos, e stubs antigos com um novo layout de corpos MEM2 causam falhas. Inicialize do zero após mudar os códigos.

## <a id="codes"></a>Códigos

As tabelas de hooks listam local, palavra original e o que a substituição faz. “nop” = 0x60000000.

### <a id="a-keep-inventory"></a>A. Manter o inventário

Problema: um reaparecimento após morte (SpawnPlayer) deixa apenas o equipamento do ponto de reaparecimento (original: todos os itens marcadores,
Gravity Boost e Grapple perdidos, traje 0). Cada chegada também aumentava os itens dos jogadores para o equipamento do ponto de surgimento
de chegada, pois DTHM vt+0x20 sempre responde sim (Great Temple Transport B fornece Dark/Echo Visor, Gravity Boost,
Seekers, munição, 3 Energy Tanks). Em um jogo novo cada jogador chega a um ponto de surgimento diferente com outros itens.

| Local | Original | Com patch |
|---|---|---|
| 0x8010d01c | 0x901d0050 `stw r0,0x50(r29)` | nop: manter o campo de traje |
| 0x8010d020 | 0x41820058 `beq 0x8010d078` | `b 0x8010d078`: manter o bloco de power-ups |
| 0x8010d2b0 | 0x7f83e378 `mr r3,r28` | `b 0x8010d364`: pular o laço de equipamento de 109 slots |
| 0x8010d580 (hook) | 0x38600001 `li r3,1` | 1 apenas enquanto a capacidade de Power Beam no estado (+0x5c) for 0, ou seja, o primeiro surgimento da sessão, e apenas para o jogador 1; jogadores 2–4 recebem uma cópia da vida, do traje e dos itens do jogador 1 |

Verificado: uma morte real no versus (jogador 1 com 1 HP atingido pelo jogador 2) resultou em reaparecimento com 99 HP mantendo traje 1, Dark/Light
Beam, Dark Suit e Missile 30/50. Um salto por WorldTeleporter para Great Temple Transport B e uma viagem real de elevador
Temple Grounds <-> Great Temple não mudaram nenhum inventário. Novo jogo: ambos os jogadores idênticos. Morrer
não repõe munição. O RSET da história permanece original e alcança todos os jogadores: na perda de itens (Hive Chamber B, MREA
0x1d7bd3ae, área 17; gatilho 0811005a -> 0011001c -> ponto de surgimento da perda 08110021), ambos perderam Missiles,
Space Jump, Bombs, Boost e Spider Ball.

### <a id="b-campaign-session"></a>B. Sessão de campanha

Problema: versus termina por tempo (600 s) ou limite de abates, carrega apenas arenas e, após uma morte, ambas as visões ficam
pretas e o ponto de reaparecimento costuma ficar em outra sala.

| Local | Original | Com patch |
|---|---|---|
| 0x8010d560 | 0xd01f0008 `stfs f0,0x8(r31)` | nop: o tempo decorrido nunca avança (relógio do HUD fica em 10:00) |
| 0x800764bc | 0x41800040 `blt +0x40` | `b 0x800764fc`: limite de abates nunca atingido |
| 0x8022da4c (hook) | 0x9421ffe0 `stwu r1,-0x20(r1)` | WorldTeleporter direcionado a Sidehopper Station (a50a80cc / 02690de1) é redirecionado para Temple Grounds / Landing Site (3bfa3eff / 62b0d67d) |
| 0x800ba7d0 (hook) | 0x396100e0 `addi r11,r1,0xe0` | carregar o salvamento cooperativo (abaixo) |
| 0x8010d478 (hook) | 0x4bfff5d9 `bl 0x8010ca50` | após a notificação: DisableFilter(0.5 s) no passe 1 de cada viewport; teletransportar o jogador que reapareceu (r27) para a transformação do primeiro outro jogador, com reinício da câmera da Morph Ball |

Carregamento do salvamento cooperativo, quando o mundo atual é Temple Grounds (a arena redirecionada): manter o objeto de regras (limpar
gs+0x144 para o destrutor do estado antigo não o excluir), as configurações MP (+0x14c, 0x64 bytes), as
entradas por jogador (+0x74, 0x20) e o +0x588 de cada estado; carregar o índice de arquivo de salvamento 2 (o terceiro arquivo) como
o Continue do modo individual faz (operator new 0x5c -> FUN_801ad590(t, 0); FUN_801ad764(0, 1); FUN_801adfcc(t, 2);
FUN_801ad764(t, 1)); definir `*(0x805cb220)+0x2c` = 2 novamente (o carregador o redefine); restaurar tudo; copiar
+0x10/+0x14 e +0x50..+0x574 do jogador 1 para os estados 1–3 (não +0x0 índice nem +0x40 ponteiro possuído); preencher a
reserva de vidas (código L); executar novamente FUN_800ba230 / FUN_800bb364 / FUN_8017e00c. Um arquivo vazio gera um jogo novo.

Verificado: Sidehopper Station inicia Temple Grounds com 2 jogadores, relógio congelado (decorrido 0.00 após 2.5 min);
abates em 9 mais um abate real: nenhuma tela de resultados. Salvo com o jogador 1 marcado (Dark Beam, Missile 33/40), inicialização
do zero: ambos retomam na sala de salvamento com Dark Beam e 33/40. Um arquivo do modo individual copiado para o terceiro
arquivo no menu de Trilogy produz um registro GMST idêntico byte a byte e retoma no cooperativo. Morte: tela permanece iluminada,
reaparecimento ao lado do parceiro. Posicionar o jogador 2.5 unidades atrás do parceiro, por outro lado, fez com que atravessasse o chão
(orientação de 135 e 180 graus em uma porta de Landing Site: z -56.5 versus -38.2); no lugar do parceiro, o jogador sempre
termina na altura dele, a cerca de 1.1 unidades de distância. Ambos morrendo ao mesmo tempo: ambos reaparecem onde morreram.

### <a id="c-shared-rooms"></a>C. Salas compartilhadas

Problema: o think do dock testa apenas players[0] (0x801e6bf8). Se o jogador 2 atravessa sozinho, a área atual
permanece inalterada, o dock é desarmado e o jogador 2 cai em uma sala não renderizada.

| Local | Original | Com patch |
|---|---|---|
| 0x801e6bf8 (hook) | 0x480000f5 `bl FUN_801e6cec` | qualquer jogador que atravesse muda a sala |
| 0x801e6a5c (hook) | 0x4bfff93d `bl 0x801e6398` | ao fechar a porta, trazer os jogadores ainda atrás dela |
| 0x801db1f8 (hook) | 0x807f1514 `lwz r3,0x1514(r31)` | “stop” da câmera vindo de um remetente que não é jogador verifica o gerenciador de cada jogador, depois continua em 0x801db25c |

- Travessia: o teste original FUN_801e6cec por jogador, além de estar a até 6 unidades do centro da porta (média dos
  pontos do plano do dock). O dock testa uma vez, quando a porta informa que alguém está passando; um jogador esperando na
  sala antiga também está além do plano, e usar apenas o plano fazia a sala alternar repetidamente. Jogadores na sala antiga ou nova
  são deixados como estão; jogadores que não estão em nenhuma das duas (duas ou mais salas atrás) são colocados ao lado de quem atravessa imediatamente.
  Teste de presença na sala: posição a até 1 unidade dos limites da área.
- Fechamento da porta: em DECR (r3 == 0) com 2+ jogadores, obter o plano deste dock da lista da sua própria área (a sala
  atrás fica além dele quando a área do dock é a atual). Líder = primeiro jogador que não está desse lado; cada jogador
  desse lado e dentro dessa sala é colocado ao lado do líder. r3–r5 são salvos (sobrescrever r5 causava falha).
- Posicionamento: 2.25 unidades à direita do líder (coluna 0 da transformação), senão à esquerda, senão atrás (-coluna 1), cada
  ponto verificado por raio a partir do peito do líder (+1 z) até 0.5 além dele; todos bloqueados: o lugar do líder. Elevar 1 unidade,
  orientação do líder, FUN_80160cc4 com reinício da câmera da Morph Ball.
- Parada da câmera: a câmera de chegada de uma sala de salvamento é iniciada com o jogador 2 como remetente e parada por um temporizador, então apenas
  o gerenciador do jogador 1 era limpo e o jogador 2 mantinha o uid cinematográfico 0x44f (visão congelada, sem controle).

Verificado: o jogador 2 abre uma porta de Hive Access Tunnel e atravessa; o jogador 1 espera 14 unidades atrás: sala
2 -> 0 uma vez em 1.1 s; em 2.2 s (porta fechada), jogador 1 colocado à direita +2.72, à frente -0.47, acima +1 do jogador 2.
Jogador 1 esperando 3 unidades atrás (no gatilho da porta): nenhum teletransporte por 5 s, depois atravessa, sala permanece 0.
Com o teletransporte anterior no momento da travessia: um seguidor em Morph Ball moveu 57.5 unidades, câmera da bola a 6.4 unidades no
próximo registro, sem lançamento; os quatro jogadores seguiram. A versão ao fechar a porta foi testada com dois jogadores.

### <a id="d-cutscenes-and-full-screen-message-boxes"></a>D. Cenas e caixas de mensagem em tela cheia

Problema: uma cena era reproduzida apenas na metade do jogador 1 (câmeras da campanha não têm a flag de multijogador); uma câmera
acionada pelo jogador 2 ia para o gerenciador dele; apenas o jogador 1 ficava imobilizado durante cenas; caixas de mensagem eram
desenhadas na metade do jogador 1 e textos longos não cabiam.

| Local | Original | Com patch |
|---|---|---|
| 0x801db154, 0x801db22c, 0x801db2b8, 0x801db310 | 0x5460103a `rlwinm r0,r3,2` | `li r0,0`: toda câmera vai para o gerenciador do jogador 1 |
| 0x8005c1d0 (hook) | 0xa0830012 `lhz r4,0x12(r3)` | para chamadores em 0x80140000–0x80164000 (código de jogador/HUD) com 2+ jogadores, testar o gerenciador do jogador 1 para imobilizar todos |
| 0x800e88a4 (hook) | 0x4bf73949 `bl 0x8005c1ec` | cena ativa (FUN_8005c1d0) ou modo de mensagem: visão única |
| 0x8024b584 (hook) | 0x4be10c69 `bl 0x8005c1ec` | o mesmo, layout em tela cheia |
| 0x800e8654 (hook) | 0x2c040000 `cmpwi r4,0` | executar o passe de HUD no modo de mensagem |
| 0x800e870c (hook) | 0x800314f0 `lwz r0,0x14f0(r3)` | apenas HUD 0 no modo de mensagem |

Modo de mensagem = estado de pausa 4 ou 6, 2+ jogadores, mundo diferente do front-end (0xdaea74a3). 0x800e8654 vem após
`mfspr r0,LR`, portanto seu corpo só pode usar r11/r12 (uma versão usando r0 corrompeu o LR salvo e travou toda
inicialização em Arena Select).

Verificado: cena de abertura em tela cheia, tela dividida retorna depois; jogador 2 sozinho em uma plataforma de salvamento gera câmera
0x454 apenas no gerenciador 0 e uma solicitação em tela cheia; uma cena acionada apenas pelo jogador 2 (Temple Grounds área
2, gatilho 046f) foi reproduzida em tela cheia e moveu os dois jogadores. O laço de salvamento da nave (ZERO do ponto de surgimento da nave recolocava
um jogador que se afastava sobre o gatilho de salvamento, indefinidamente) desapareceu com todos imobilizados: apenas uma solicitação.

### <a id="e-scan-visor-and-no-friendly-fire"></a>E. Scan Visor e ausência de fogo amigo

| Local | Original | Com patch |
|---|---|---|
| 0x8014a0e8 | 0x4182000c `beq +0xc` | `b 0x8014a0f4`: permitir escaneamento sob MP |
| 0x80166a88 | 0x40820030 `bne` | nop: usar a busca de alvos de escaneamento |
| 0x80148578 | 0x40820008 `bne` | nop: atualizar a mira de escaneamento para cada jogador |
| 0x80166aac (hook) | 0x5460843e `rlwinm r0,r3,16,16,31` | busca não encontrou nada: ator ativo mais próximo com informações de escaneamento (+0xbc -> +8) a até 40 unidades e cos^2 >= 0.96 da mira da câmera em primeira pessoa (gerenciador +0x14: olho = coluna 3, mira = coluna 1), excluindo jogadores; senão a busca de combate em 0x80166ab8 |
| 0x80149ee8 (hook) | 0x48101615 `bl IsMultiplayer` | sob MP: alvo (+0x39c) -> CastToActor -> vt+0x78 -> mostrar sua STRG com FUN_8024ac68; retorna 1 |
| 0x8024abb4 (hook) | 0x2c030000 `cmpwi r3,0` | permitir estados de pausa 0, 1, 3, 4, 5, 6 sob MP |
| 0x800ddc28 (inline) | 0x7c070000 `cmpw r7,r0` | nos estados de pausa 1 e 6 todo controle vai para o HUD 0; no estado 4 apenas o controle que abriu a Data Network |
| 0x802429ec (hook) | 0x9421ffa0 `stwu r1,-0x60(r1)` | entrada do construtor de dano: executá-lo, depois zerar +4/+8/+0x10 quando quem recebe o dano for um jogador e quem causa o dano ou o remetente da área for um jogador ou a arma de um jogador |

O hook de dano define LR para seu próprio código posterior, executa o `stwu` deslocado e prossegue na função, de modo que um
corpo atende aos dois chamadores. Ordem dos argumentos: r5 quem causa o dano, r6 remetente da área, r7 quem recebe o dano.

Verificado: escaneamento concluído em 1.5 s; texto da estátua pagina e fecha (A apenas do jogador 2 funciona), mundo pausado para
ambos durante isso. Jogador 2 escaneou o mecanismo do portão da sala 6 de Temple Grounds (ambas as travas ativas); jogador 1, a Map
Station. ApplyDamage de uma porta 99 -> 89, do jogador 2 79 -> 79; jogador 2 disparando no jogador 1 (1 HP) por 12 s:
ileso (sem o código, matava). Bloqueado entre todos os pares com 4 jogadores.

### <a id="f-enemies-and-bosses"></a>F. Inimigos e chefes

| Local | Original | Com patch |
|---|---|---|
| 0x80240be8 (hook) | 0x4bfffdad `bl 0x80240994` | para um CPatterned com 2+ jogadores: trocar o jogador mais próximo (distância ao quadrado de +0x50) para players[0] e states[0], atualizar o campo de alvo armazenado, executar Think, desfazer a troca |
| 0x80240d50 (hook) | 0x4e800421 `bctrl` | o mesmo em torno de PreThink (a chamada de vtable é refeita porque o salto distante usa CTR) |
| 0x8024b3d0, 0x80244c70 (hooks) | 0x4e800421 `bctrl` | entrega de mensagem a um CPatterned: trocar para o remetente se for um jogador, senão para o jogador que disparou a arma remetente (+0x2c8), senão para o jogador mais próximo |

Os campos de alvo armazenados (consulte Inimigos e IA) são reescritos apenas enquanto contêm o uid de um jogador. O próprio id de tipo é lido
do imediato `cmpwi` da função IsA e comparado inline apenas em Think (9 chamadas CAST_ENTITY por inimigo em
Think e PreThink haviam custado até 25 chamadas do harness por segundo em salas com 16 inimigos).

Verificado: Splinters junto ao jogador 2 com jogador 1 longe: temporizadores de desistência 15.1 / 9.3 s sem, 0.00 com.
Dano do Boost Guardian em 60 s (jogador 1 / jogador 2): nenhum 263 / 10, Think 713 / 90, Think + PreThink 345 / 110.
Seu +0x1098 permanecia 0x400 (jogador 1) com apenas o jogador 2 na arena; reescrito: apenas jogador 1 370/330/185 versus
apenas jogador 2 257/370/160. Campo do Blogg -> 0x401 com jogador 2 perto; dano de Space Pirate A/B com jogador 2 perto
195/190, jogador 1 perto 110/95. Salas com 16 inimigos de volta a 89–91 chamadas por segundo.

### <a id="g-save-stations"></a>G. Estações de salvamento

0x8020e83c: 0x408200a4 `bne` -> nop (FUN_8020e800 retornava sob MP antes da reposição e de SetPauseState(5)).
Exige a condição de pausa do código E. Verificado: “Do you want to save?” em tela cheia, salvamento escrito, um A fecha a
mensagem “saved” (estado 6), inventários inalterados; qualquer jogador pode salvar. Os jogadores precisam sair da plataforma;
ficar em uma plataforma armada reabre a solicitação.

### <a id="h-pickups"></a>H. Itens coletáveis

0x801f8d78 (hook, original 0x1c19000c `mulli r0,r25,12`, logo após a concessão; r23 item coletável, r24 mgr, r25 item,
r30 índice de quem tocou): repetir a mesma concessão para o estado de cada outro jogador (variantes set quando +0x1c8 bit 0x10).
Verificado: Missile Expansion obtida pelo jogador 1: ambos 33/40 -> 38/45, contador 0x2f 1/1 cada; Energy Tank alcançado
pelo jogador 2: ambos 1/1. Itens coletados permanecem coletados (estado de camada do mundo, salvo).

### <a id="i-shared-scan-progress"></a>I. Progresso de escaneamento compartilhado

Hooks em 0x8014a474 (original 0x48023f29), 0x80149e8c (0x48024511) e 0x8014a2d4 (0x480240c9), todos
`bl SetScanTime`: chamá-lo para o estado de cada jogador com o mesmo id e a mesma fração. Verificado no próprio caminho de
atualização do jogo: o jogador 2 escaneando a estátua definiu a entrada dos dois jogadores como 0xff.

### <a id="j-script-upgrades"></a>J. Melhorias por script

Hooks nas entradas de FUN_8020f780, FUN_8020f838, FUN_8020f8d4, FUN_8020f9ac (original 0x9421ffe0 em cada): executar
o tratador uma vez por jogador com +0x170 = i (`stwu` deslocado, depois salto distante para entry+4), restaurar +0x170.
0x8020322c (original 0x807e1504): percorrer o estado de cada jogador, continuar em 0x8020324c. FUN_80065290 (controle das regras
MP) percorre os jogadores por conta própria. Verificado apenas com objetos substitutos: mísseis tipo 33 +5 enviados pelo jogador 2
-> ambos 50 -> 55; concessão ZERO Light Beam -> ambos 0 -> 1.

### <a id="k-map-screen-and-data-network"></a>K. Tela de mapa e Data Network

| Local | Original | Com patch |
|---|---|---|
| 0x80156e88 | 0x41820034 | nop: ctor do HUD sempre constrói o objeto de quadro do mapa |
| 0x80241854 | 0x40820058 | nop: botão de mapa com 2+ jogadores |
| 0x8024188c | 0x40820020 | nop: botão de mapa de qualquer controle |
| 0x80159598 | 0x418202a8 | nop: carregar a lista de texturas do HUD individual (ícones do mapa) |
| 0x800e7f50 | 0x41820068 | `b 0x800e7fb8`: sem menu MP por jogador |
| 0x800e7fc0 | 0x4082032c | nop: qualquer controle abre a Data Network |
| 0x80157b84 (hook) | 0x2c050000 | com 2+ jogadores, desenhar o bloco do mapa apenas no estado de pausa 1 (sem sobreposição de minimapa no canto) |
| 0x80157c14 (inline) | 0x4e800421 | pular o widget de fundo (um painel claro no quadro de HUD MP) |
| 0x80157c84 (inline) | 0x38800006 | comparação z 7 (ALWAYS) em vez de 6: o mundo em execução preenche o buffer de profundidade |
| 0x80157cbc (hook) | 0x48210579 | concatenar com (40, 1, 40, profundidade -17.479) em vez de HUD+0x1e4 (âncoras MP davam escala 0.35) |
| 0x801577fc (hook) | 0x9421fe80 | entrada do desenho do HUD: definir 0x937f0010 quando estado de pausa != 0 com 2+ jogadores |
| 0x803ec8d0 (hook) | 0x8122cf08 | GXSetZMode: comparar ALWAYS enquanto a flag estiver definida |
| 0x80245504 (hook) | 0x9421fea0 | entrada do desenho do mundo: limpar a flag, invalidar o byte de cache 0x8050d272 |
| 0x800e82d8 (hook) | 0x38800003 `li r4,3` | estado 4 (Data Network); armazenar o controle que pressionou (r1+0x5c) em 0x937f0014 |
| 0x800e8cf4 (hook) | 0x4bff4e11 `bl 0x800ddb04` | HUD_SET_MODE(4) apenas no HUD 0 |

Os três hooks de profundidade corrigem outros jogadores e geometria próxima desenhados sobre as telas de HUD pausadas (caixa de texto, mapa):
quadros pausados ainda desenham primeiro o passe do mundo em execução.

Verificado: o mapa da fase mostra salas visitadas, portas e Samus; A alterna para World Map; B fecha; o botão 1 do jogador 2
o abre, e A/B do jogador 2 o controlam. Caixa de texto limpa com o jogador 2 visível. Data Network: o botão de pausa do jogador 2
a abre em tela cheia, e o jogador 2 navega e a fecha. Um teste encontrou que o jogador 1 não conseguia controlá-la
quando o jogador 2 estava ocioso (a última entrada a chegar prevalecia); com o controle de abertura registrado, o botão de pausa funciona para
ambos. O menu MP “Quit Game?” já não está em um botão; sair é feito pelas Options da Data Network.

### <a id="l-shared-lives"></a>L. Vidas compartilhadas

Reserva (s32) em 0x937f0000, vidas por jogador em +4 = Deathmatch Kill Limit / 5 (valores de menu 0, 5, 10, ...;
regras +0x3c, +0x40 bit 0x40). 0 = desativado (reserva -1). Preenchida no início da sessão e ao salvar como vidas por jogador x contagem
de jogadores (regras +0x38). Exibida como quantidade/capacidade do item 0x40 para cada jogador (os contadores centrais do HUD).

| Local | Original | Com patch |
|---|---|---|
| 0x80076428 (hook) | 0x7fa4eb78 `mr r4,r29` | temporizador do jogador morto esgotado: reserva != 0 -> SpawnPlayer; reserva 0 e alguém vivo -> 0x80076498 (permanecer caído); ninguém vivo -> zerar item 0x40, 0x800764c0 (fim da partida, “DRAW GAME”) |
| 0x80076454 (hook) | 0x9b370004 `stb r25,0x4(r23)` | após SpawnPlayer: reserva - 1 (se > 0), atualizar exibição |
| 0x8024ac68 (hook) | 0x9421ffd0 `stwu r1,-0x30(r1)` | entrada de mostrar mensagem: repor a reserva apenas para as duas mensagens “saved” |
| 0x80076414 (hook) | 0xc0170000 `lfs f0,0(r23)` | a cada quadro para um jogador morto: DisableFilter(0.5 s) no passe 1 do viewport de cada jogador vivo (pass+4 != 0); com reserva 0, também no do jogador caído |
| 0x8024b844 (hook) | 0x57e0103a | reserva 0, jogador do viewport caído: definir mgr+0x1da0/+0x1da4/+0x1da8 a partir do primeiro jogador de pé (espectar) |
| 0x800dd9cc (hook) | 0x57e01838 | o mesmo, desenhar o HUD desse jogador no viewport |

A metade preta de um jogador caído é o objeto HUD cobrindo o viewport, não um filtro de câmera.

Verificado: reserva 4 com 2 jogadores conta 4 -> 0; em 0, jogador 2 permanece caído e a visão do jogador 1 permanece iluminada; estação de
salvamento No: reserva 0, nada salvo; Yes: salvo, reserva 4, jogador 2 revivido (-> 3); todos caídos -> tela de resultados
-> menu multijogador; Sidehopper novamente retoma com reserva 4. Kill Limit 15 -> 3 por jogador (reserva 6); 0 -> três
mortes com reaparecimento em todas. Com jogador 2 caído: portas e mudanças de mundo levam o corpo junto, cenas e salvamento
funcionam, e um salvamento retomado tem ambos os jogadores de pé.

### <a id="difficulty"></a>Dificuldade

O getter FUN_800bc668(gs) retorna `*(0x805cb220)+0x80` apenas para 'SNGL', senão `li r3,1` em 0x800bc6a0, portanto
versus e cooperativo sempre eram Veteran. 0 Normal, 1 Veteran, 2 Hypermode. Escalas: FUN_800bc334 0.5 / 1.0 /
tweak+0x48 (1.53) para dano a Samus; FUN_800bc39c 1.3 / 1.0 / tweak+0x4c (0.5) para dano de Samus aos
inimigos (FUN_80292110 de FUN_802429ec). Objeto tweak `**(r13-0x6420)`.

Três códigos, cada um escrevendo `li r3,N` sobre 0x800bc6a0 (original 0x38600001): Normal 0, Veteran 1, Hypermode 2.
Verificado com Hypermode: getter 2; o 10 do jogador 1 contra um inimigo se tornou 5.0 (dano, raio, repulsão); o
10 de um inimigo levou o jogador 1 de 99 a 83.7 (x1.53, aplicado no caminho completo de ApplyDamage, não em FUN_802429ec).

## <a id="dead-ends-and-pitfalls"></a>Caminhos sem saída e armadilhas

- Aplicar NOP às duas chamadas RSET removeu a sobrescrita da introdução, mas também pula mudanças de equipamento da história; a versão que apenas aumenta
  bloqueou a perda de itens. O RSET original é o correto para o cooperativo.
- Uma mudança de mundo por WorldTeleporter não apaga o inventário nesta build (apenas aumenta, ambas as regras). O relato de 2019
  sobre elevadores redefinirem itens é RSET na chegada ou as alterações de equipamento do próprio mod.
- Escrever em CPlayerState +0x10 não muda a vida; escrever vida 0 não mata (a morte exige um evento de
  dano); bombas próprias não ferem; escrever a transformação de CPlayer não move o jogador (use FUN_80160cc4).
- IsGameOver (vt+0x38) -> `li r3,0`: impede o fim por tempo (relógio ficou negativo), mas não o fim por limite de abates, e
  bloquearia a saída.
- Teletransportar todos os seguidores 2.5 unidades à frente ao longo da normal da porta no momento da travessia continuava colocando-os
  no caminho e podia fazê-los cair dentro da geometria; substituído pelo posicionamento ao fechar a porta.
- Texto de escaneamento por ScanPause sob MP congelou ambos os jogadores atrás de um painel vazio (o HUD MP não tem um); a
  caixa de mensagem é usada em seu lugar.
- Scan Visor: o nop de 0x80166a88 sozinho não deu candidato ao jogador 2 (+0x3c8 = 0xffff); uma leitura extra do buffer de ids
  após todos os viewports, ou copiar apenas o viewport atual, não preencheu o buffer do jogador 2 e
  esvaziou o do jogador 1. O momento da cópia da GPU continua sem solução; a alternativa baseada em mira cobre isso.
- Mapa: forçar o estado de pausa 1 sem o objeto de quadro causou falha (escrita inválida em 0x208 em 0x800e8bfc). Construir
  o objeto gerou um quadro com painel claro e sem mapa até as três correções de desenho (encontradas por bisseção de chamadas com NOP
  entre 0x80157a08 e 0x80157c14). Forçar a visão em tela cheia não ajudou.
- Silhueta sobre HUDs pausados: desativar o teste de profundidade da janela de texto (0x80157d20), retornar antecipadamente do
  vt+0x2c do jogador e 0x8015762c/0x80157618 não mudaram nada; desenhos de materiais chamam GXSetZMode diretamente.
- Atenção dos chefes: trocar apenas em Think deixava o jogador 2 muito atrás; trocar apenas nas mensagens não mudou o A/B.
  Os campos de alvo armazenados eram a causa real.
- `lis 0x804f; addi -0x8d18` não é 0x804e72e8 (imediato com sinal de 16 bits): use `lis 0x804e; addi 0x72e8`.
- RSET não pode ser testado iniciando um novo jogo em outra área: um início no surgimento padrão usa FUN_8023f45c e
  nunca envia RSET. Os elevadores Temple Transport B/C nesse tipo de início são bloqueados por teias Ing e camadas da história.

## <a id="test-harness-not-published"></a>Harness de testes (não publicado)

- Python lê e escreve a memória emulada do Dolphin (o método Dolphin Memory Engine) para extrair jogadores,
  inventários, mapas de escaneamento, objetos de script e conexões.
- Funções do jogo são chamadas na thread do jogo por um hook em HasPowerUp (0x8016de90, executado a cada quadro):
  ele verifica uma flag e chama um endereço com até 7 argumentos inteiros e f1, retornando r3. Usado para o
  teletransporte de jogador, ApplyDamage, SetScanningState, mensagens de script para objetos reais ou substitutos, o teletransportador
  de mundos com objeto falso, o raio de colisão e SpawnPlayer. Sua RAM deve ficar fora da lista de códigos
  (de 0x80003a00 para cima). Ele pode executar durante Think de inimigos enquanto o código F trocou players[0], portanto testes de portas andam
  em vez de teletransportar. Chamadas com tempo esgotado devem ser canceladas, ou executam depois em objetos já liberados.
- Pressionamentos de teclas no Dolphin (janela em foco) controlam os dois Wii Remotes; Wii Remotes desconectam quando ociosos, portanto cada
  rodada começa com um pressionamento. IR absoluto fornece giros repetíveis no jogo; menus precisam de IR relativo. Em Trilogy,
  mirar e disparar dependem do ponteiro, portanto um ponteiro travado parece um botão de disparo inoperante.
- Stubs de contagem em torno de locais de chamada candidatos (repassando ao destino original) mostraram quais caminhos de surgimento executam.
- Um scanner de mundos teletransportou para 282 das 284 salas dos cinco mundos principais (duas travam em um salto direto) e
  registrou cada classe de inimigo; salas criam objetos 6–9 s após a chegada.
- Aproximação da taxa de quadros: chamadas do harness por segundo (máximo de cerca de 90). Comparações A/B constroem os códigos omitindo
  um recurso e inicializam do zero (alterações em execução nos corpos MEM2 são sobrescritas por OnFrame).

## <a id="known-issues-and-untested"></a>Problemas conhecidos e itens não testados

- Apenas as horas iniciais foram jogadas por pessoas; áreas posteriores foram verificadas apenas pelo harness. Inimigos,
  dispositivos e chefes condicionados pela história após o início (Chykka, Spider Guardian, fases de Emperor Ing, piratas Dark/Commando)
  não foram testados, e os campos de alvo armazenados de Jump Guardian, Quadraxis, Ing, Splitter e Rezbit
  não foram verificados em combate.
- Chefes ainda dão um pouco menos de atenção ao jogador 2 do que ao jogador 1 em alguns pontos (código de chefe fora de Think).
- O buffer de ids do Scan Visor não é preenchido para os jogadores 2–4; eles dependem da alternativa por mira.
- Cenas e caixas de mensagem usam a visão do jogador 1. Jogadores 2–4 podem cair durante uma cena de chegada de elevador
  (invisíveis; o script então coloca ambos na saída). O mapa abre na metade do jogador 1, com salas um pouco fora do centro.
- Código J testado apenas com objetos substitutos; uma estação de mapa abrindo o mapa (tipo 5 com código K) não foi testada
  separadamente; a função especial 37 (estado de pausa 2) permanece bloqueada.
- Apenas Trilogy NTSC-U. Builds PAL, japonesa e de GameCube têm outros endereços; a proteção mantém os códigos inertes
  nelas. Dolphin NetPlay não testado.

