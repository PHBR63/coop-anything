# <a id="mdk2-hd-working-notes"></a>MDK2 HD: notas de trabalho

## <a id="game-identity"></a>Identidade do jogo
- Loja: Steam, app 213350, build id 3902
- Executável: `mdk2hd.exe`, PE32 (x86 de 32 bits), SHA-256 `bf5faa81b18837b4c07f35941b107e5c23caa8b105536ccd9c8e5a8e37357f43`
- Arquivos: `mdk2hd.exe`, `steam_api.dll`, `mdk2.tar` (1.6 GB)
- Renderizador: OpenGL 3.0 (string do executável "MDK2 HD requires OpenGL 3.0."); entrada: importa `DINPUT8.dll`
- SO testado: Windows 11

## <a id="observations-checked"></a>Observações (verificadas)
- `mdk2.tar` é um tar GNU/ustar simples, plano (sem diretórios), 5842 entradas:
  2210 .mod, 1808 .dds, 998 .wav, 692 .bsp, 101 .lua, 27 .mus, mais mdk2.str, stars.sta, shading.shd e uma fonte.
- Os 101 arquivos .lua são fonte Lua em texto simples (CRLF), não bytecode. O executável incorpora Lua 3.1 ("Lua 3.1 Copyright (C) 1994-1998 TeCGraf") com bindings tolua.
- O script de inicialização é `mdk2.lua`; ele usa dofile() em strings, menuinit, script, effects, debug. Fases são `levelN.lua` + `lN.lua` + `lightsN.lua`.
- Personagens do jogador são criados por Lua: `CreateKurt()`, `CreateMax()`, `CreateDoctor()`, `CreateHyde()` (mdk2.lua ~linhas 800–860). `start.lua` é apenas `CreateKurt()`.
- `debug.lua` vem no arquivo ("Do not ship this file") com atalhos de depuração (F9 menu de depuração, cheat de jato, câmera livre).
- Prefixos da API Lua da engine: `om*` (objetos/gobs/animações/comandos), `ch*` (núcleo: som, vídeo, entrada, `chRecordInput`), `mdk*`, `vv*` (visualizador de variáveis), `do*`. Cerca de 460 nomes assim nas strings do executável.
- Sem biblioteca io de Lua (`writeto`/`readfrom` ausentes); `dofile`/`dostring` presentes.
- Strings do executável referenciam `override\`, `override\<language>\`, `scripts\`, `script\lights%d.lua`, `save\auto.sav`, `save\Auto%d.sav`, `settings.lua`.
- O jogo cria `%LOCALAPPDATA%\MDK2HD\` (vazia após várias execuções).

## <a id="tried"></a>Tentativas
- Cópia de teste iniciada diretamente (com `steam_appid.txt` = 213350) via Start-Process do PowerShell.
  Processo permanece vivo por mais de 30 s, mas capturas entre 8–32 s mostram todas o logotipo da Interplay; Escape via SendKeys não avançou visivelmente.
- `menuinit.lua` solto contendo um erro Lua deliberado colocado em `override\`, `scripts\`, `script\`, `override\english\`: nenhum efeito observável,
  mas INCONCLUSIVO porque o jogo nunca passou visivelmente do logotipo da Interplay nas execuções automatizadas.

## <a id="session-1-results-2026-10-20"></a>Resultados da sessão 1 (2026-10-20)
Automação: jogo em modo de janela (800x600). Teclas devem ser enviadas como scancodes via SendInput (KEYEVENTF_SCANCODE)
para DirectInput enxergá-las; .NET SendKeys não funciona. A captura da janela deve reconhecer DPI (SetProcessDPIAware)
ou captura a área errada da tela. Escape pula introduções; dois Escapes chegam ao menu de título.
O problema anterior de “preso no logotipo da Interplay” era a combinação desses dois problemas, não um travamento.

- `override\`, `scripts\`: um `menuinit.lua` solto contendo apenas um erro foi IGNORADO (menu carregou normalmente).
  Substituição por arquivo solto não se aplica a scripts Lua (talvez se aplique a outros assets: não testado).
- `%LOCALAPPDATA%\MDK2HD\settings.lua` é escrito pelo jogo (opções de vídeo/áudio/teclas como chamadas Lua) e
  executado na inicialização DEPOIS de mdk2.lua: acrescentar `chSetVideoMode(...1024,768...)` mudou o tamanho da janela, e
  `if CreateKurt then ... end` seguiu o ramo definido. Portanto é um ponto funcional de injeção que pode redefinir
  qualquer função Lua do jogo.
- `dofile()` só lê de mdk2.tar: `dofile('C:\\coop\\mod\\coop.lua')` não fez nada silenciosamente.
  `dofile('debug')` (nome no arquivo) funciona.
- `mdk2.lua` protege `dofile('debug')` com o pré-processador `$if features` do Lua 3.1. Acrescentar `dofile('debug')`
  a settings.lua ativa o menu de depuração de desenvolvedor da BioWare: F9 durante o jogo mostra God Mode, Spawn Object,
  Spawn Doctor Item, Warp To Point, Play Movie, Toggle Bars/Status, Varview, Lights, Ambient,
  Switch Player Character, Spawn Character, Show Scene Graph, Record Demo, Play Demo, Load Game.
  F9 não faz nada na tela de título (vinculado apenas aos esquemas de controle de jogo/menu).
- O chefe final (boss.lua ~linhas 548–640) cria os dois heróis não controlados pelo jogador com IA na mesma cena que o jogador:
  `mdkCreateObjectLua("kurt", OBJ_KURT, ...)`, `mdkKurtInitAI`, `mdkKurtAIHeadToGob`, `mdkKurtAISetPosition`,
  o mesmo para Max/Doc (`mdkMaxAIGiveGun`). A engine, portanto, suporta vários gobs de herói ao mesmo tempo.
- Existe API de posição: `mdkGobSetPosition`, `mdkGobSetPositionXYZ`, `mdkGobSetOrientation`, `mdkGobSyncSetPosition`,
  `mdkGetPlayerGob`, `mdkGobDistancePoint`. Existe gravação/reprodução de entrada: `chRecordInput`, `mdkPlayDemo` (útil para QA com bots).

## <a id="unknown"></a>Desconhecido
- Se existe um getter Lua para posição do gob (necessário para sincronização); nenhum visto por nome ainda.
- Se Lua pode fazer rede ou E/S de arquivos (sem biblioteca io), portanto o transporte provavelmente precisa de DLL nativa (proxy dinput8).
- Se a substituição por arquivo solto funciona para assets que não sejam scripts.
- Qualquer tentativa existente de multijogador/cooperativo para MDK2 (nenhuma encontrada em DIRECTORY.md, issues/PRs do repositório e uma busca na web).

## <a id="session-1b-second-player-puppet-2026-10-20"></a>Sessão 1b: fantoche de segundo jogador (2026-10-20)
Código do mod: repositório separado `mdk2-coop` (local por enquanto), `lua/coop_dev.lua` injetado via `tools/inject.sh`.
Verificado (capturas de tela):
- Tratadores `comfuncs.fkey[...]` disparam em qualquer esquema de controle, incluindo a tela de título.
  Revincular comandos de depuração não usados funciona: `omMakeCommand(COM_TOGL1, "F6", CON_BUTTON_FALL, 0, 0)`.
- `mdkNewGame(1, 2)` da tela de título carrega diretamente fase 1 checkpoint 2 (Kurt a pé).
- Campos do gob são legíveis por Lua: `gob.position.x/y/z`, `gob.orientation.yaw` (debug.lua COM_PRINTINFO).
- `mdkCreateObjectLua("coop_p2", OBJ_KURT, mdkGetScene(), nil, nil, 0,0,0, 1,0,0,0, nil,0,0,0,0)` cria um
  segundo Kurt ao lado do Kurt jogador. Com `mdkSetLuaEvent(p2, "OnUpdate", fn)` chamando
  `mdkGobSetPositionXYZ` a cada quadro, ele acompanha o jogador (pose congelada no meio da animação: sem sincronização de animação).
- `mdkKurtInitAI(p2)` + `mdkKurtAIHeadToGob(p2, player)` o faz andar até o jogador com a animação correta.
Derivado: um jogador remoto pode ser mostrado como fantoche teletransportado (precisa de sincronização de animação) ou direcionando a
IA de herói do jogo para a posição remota (animação gratuita, precisão desconhecida).
Desconhecido: semântica do setter de orientação, se o Kurt de IA pode disparar/receber dano de forma sensata, como um segundo
gob de herói interage com checkpoints, transições de fase, salvamentos e cenas.

## <a id="session-1c-native-bridge-2026-10-20"></a>Sessão 1c: ponte nativa (2026-10-20)
Verificado:
- mdk2hd.exe é envolvido por SteamStub: ponto de entrada em `.bind`, entropia de `.text` 8.0 no disco. Não desembrulhado.
  Em vez disso, um proxy dinput8.dll (o jogo importa DINPUT8.dll) extraiu a imagem na memória na primeira
  chamada de DirectInput8Create; a entropia de `.text` ali é 6.63 (descriptografada). A análise usa apenas esse dump, mantido em local/.
- DllMain do proxy executa antes de o jogo inicializar Lua, e `.data` é gravável nesse momento.
- Tabela de funções internas do Lua 3.1 {nome, função} em 0x5064f8..0x5065d0 (setfallback .. type). Entrada `copytagmethods` em 0x506520
  (string de nome 0x4d7d34); nenhum script do jogo a usa. Redirecioná-la para uma função C antes de Lua iniciar dá a Lua uma
  global que chama a DLL. Funciona.
- Endereços da API C de Lua (build 3902, cdecl), encontrados desmontando as funções internas dostring/tonumber/setglobal e o
  código de registro da engine:
  | endereço | função |
  |---|---|
  | 0x476690 | lua_getparam(int) |
  | 0x476a20 | lua_isnumber(obj) |
  | 0x476a60 | lua_getnumber(obj) -> double |
  | 0x476bb0 | lua_pushnumber(double) |
  | 0x476c40 | lua_pushstring (derivado, não testado) |
  | 0x476c70 | lua_pushcclosure(fn, n) (derivado) |
  | 0x476930 | lua_setglobal(name) (derivado) |
  | 0x478100 | luaL_check_lstr(narg, &len) |
  | 0x478de0 | lua_dobuffer(buf, len, name) (derivado) |
  | 0x4776b0 | tolua_function(module, name, fn): a engine registra funções mdk* com ela (por exemplo, 0x442893) |
- A ponte registra `coop_send(x,y,z,yaw)` / `coop_recv()` via tolua_function(NULL, ...) e envia UDP.
- Duas instâncias executam ao mesmo tempo a partir de duas pastas (a segunda pasta usa hardlink de mdk2.tar). Ambas compartilham
  %LOCALAPPDATA%\MDK2HD (configurações e provavelmente salvamentos).
- Teste com duas instâncias, fase 1 cp 2: A registrou `send #2700 (85.25, 186.00, -30.00)`, B registrou
  `recv #2700 (85.25, 186.00, -30.00)`; B registrou `send #2400 (83.52, ...)`, A `recv #2400 (83.52, ...)`.
  Captura de B mostra o Kurt fantoche no lugar de A.
- `gob.orientation` é nil em Lua (indexá-lo gera erro "indexed expression not a table" a cada quadro).
  Erros Lua são impressos na tela dentro do jogo, o que é útil para depuração.
Desconhecido: como ler/definir a orientação por Lua; se instâncias sem foco continuam executando na taxa completa.

## <a id="session-1d-orientation-and-animation-2026-10-20"></a>Sessão 1d: orientação e animação (2026-10-20)
Verificado:
- Funções de acesso dos campos OMGOB registradas com tolua_tablevar (0x4774f0) na classe "OMGOB" (0x4c3058):
  getter de position 0x437af0 / setter 0x437b30 -> gob+0x18 (3 floats);
  getter de orientation 0x437ba0 / setter 0x437be0 -> gob+0x24 (4 floats, setter copia dados brutos).
  `gob.orientation` em Lua é um userdata de quaternion sem campos, portanto `.yaw` gera erro.
- Layout do quaternion é (w, x, y, z): identidade aparece no log como (1,0,0,0); girar com X deu (0.913, 0, 0, -0.408).
  z é para cima (chão em z = -30), Kurt com quat (0,0,0,1) anda para -y.
- Sistema de animação: gob+0x60 = controlador; controller+0x24 = array de blocos de estado de 40 bytes,
  controller+0x28 / +0x2c = bloco atual / anterior. `0x44c640(gob, anim_id)` retorna o bloco
  (model+0x68 é um mapa de bytes id -> slot). omAnimPlay nativo = 0x44ca90(gob, id, flags),
  omAnimIsPlaying = 0x44cc20(gob, id).
- Conteúdos de bloco vistos: [0] reproduzindo, [1] modo (1 normal, 0xa sobreposição), [3]/[4] tempo, [5] taxa,
  [6] peso, [7] 4.0, [9] 1. Sem ponteiros. Kurt ocioso = animação 107 (também animação 1), caminhada = 22, sobreposição de salto = 77.
- Copiar os blocos ativos mais ids atuais/anteriores de um Kurt para outro a cada quadro faz os
  estados do fantoche corresponderem (dump: fantoche animação 107 tempo 0x3f313b87 versus jogador 0x3f3113b5). Teste de loopback
  com o fantoche desenhado 3 unidades acima do jogador: mesma pose ociosa, pernas do fantoche em ciclo de caminhada ao andar.
- Teste de duas instâncias: quaternion de A (0.913,0,0,-0.408) recebido por B; fantoche em B reorientado visivelmente.
- debug.lua vincula D (câmera livre), I (imprime orientation.yaw -> erro recorrente "indexed expression not a
  table"), 0/9 (velocidade do jogo) e mais; limpá-los com omMakeCommand(COM_x, "") corrige conflitos de entrada.
- Espaço não é salto nos atalhos padrão (salto é botão do mouse 1001); alternava o modo sniper.
Desconhecido:
- Um fantoche colocado a 2 ou 6 unidades ao longo de -y do jogador não era visível da câmera padrão, embora
  sua posição no log estivesse certa; 3 unidades acima era visível. Não explicado (direção da câmera versus descarte de salas).
- Se um fantoche que sai da sala onde surgiu continua renderizado (salas: mdkAddRoom, mdkRoomSetBB, mdkRoomAddVisible).
- F7 às vezes cria em x=80 (área aberta) e às vezes em x=105 (junto a uma parede): RESOLVIDO na sessão 2, o fantoche
  sólido sobrepondo o jogador no ponto de surgimento compartilhado empurrava o jogador para dentro da parede.

## <a id="session-1e-rooms-2026-10-20"></a>Sessão 1e: salas (2026-10-20)
Verificado:
- Salas da fase 1 são entradas do grafo de cena (l1_r2, l1_tun05crv, ...) com listas `visible`; poucas têm
  caixas delimitadoras (bmin/bmax), por exemplo l1_r2sky. `mdkGetCurrentRoom()` retorna o gob da sala (userdata).
- `mdkGobSetPositionXYZ(player, 133, 46, -40)` (lugar da fase 1 cp3) move o jogador para outra sala
  sem recarregar; mdkGetCurrentRoom() muda.
- Loopback: fantoche desenhado 3 unidades acima do jogador permanece visível após esse teletransporte.
- Duas instâncias: A teletransporta para a sala de cp3, depois B também; B desenha o fantoche de A no lugar de A na nova
  sala. Portanto um fantoche movido por mdkGobSetPositionXYZ é reclassificado na sala certa; nenhum código de sala é necessário
  para este caso.
- F12 é a tecla de captura da Steam; teclas de desenvolvimento a evitam.
Desconhecido: se um fantoche em uma sala para a qual o observador pode enxergar (não a própria sala do observador) é desenhado;
o caso anterior de “fantoche 2–6 unidades à frente não visível” continua sem explicação.

## <a id="session-1f-smoothing-2026-10-20"></a>Sessão 1f: suavização (2026-10-20)
Verificado (duas instâncias, A anda 7 s, B recebe com latência simulada de 120 ms, jitter de 40 ms, perda de 5%, envios a 30 Hz):
- Sem interpolação (pacote mais recente): janela de caminhada constante ficou parada em 83% dos quadros, passo máximo 0.97, cv 2.45.
- Com buffer de interpolação de 100 ms: paradas 0%, passo máximo 0.096, cv 0.18 (cv = desvio padrão/média do passo por quadro).
- Uma instância sem foco continua executando na taxa completa (330 quadros por janela de 2 s a ~165 fps).
Derivado: campos de animação [3]/[4] se comportam como posição de reprodução de 0..1 (todos os valores observados < 1); interpolados com retorno cíclico.
Desconhecido: se interpolar a posição de reprodução da animação parece certo na tela (apenas a suavidade da posição foi medida).

## <a id="session-1g-damage-2026-10-20"></a>Sessão 1g: dano (2026-10-20)
Verificado:
- Nomes de eventos Lua são uma tabela char[16] em 0x4f6370 indexada pelo id de evento (OnUpdate 0, OnCollision 1,
  OnDestroy 2, OnDamage 3, OnHear 4, ..., OnDie 9, OnEnterRoom 10, ...). 0x40cf60(gob, id) = tem tratador Lua.
- Função central de dano 0x40d590(from, target, damage, damagetype, part), cdecl, 31 locais de chamada. Chama o
  OnDamage Lua do gob se definido, senão um tratador C por classe (tabela de classes 0x4f64a8[gob+0xb4 & 0x3f] + 0x14).
  Pontos de vida: *(short *)(*(gob+0x84) + 0x12). Prólogo 55 8b 6c 24 0c, permite hook com jmp de 5 bytes após
  SteamStub descriptografar .text (hook instalado de coop_init).
- Nome do gob: char[] inline em gob+0x4 (encontrado buscando “bob” no gob do jogador).
- Observado pelo hook: arma de Kurt = 2 de dano, tipo 0x1, parte -1 (ou 2 em alguns cenários); Doganboy atinge
  Kurt por 2–8, tipo 0x2. Disparos que erram danificam gobs de geometria da fase (l1_r2plate, l1_r2pillars, l1r3_wall, l1_r2).
- settings.lua é lido em um buffer de pilha de 8 KB (função em torno de 0x42c4b0, sub esp 0x2004): um settings.lua
  com mais de 8192 bytes derruba o jogo na inicialização com 0xc0000409 (cookie de pilha). O Lua do mod agora executa de
  coop\coop.lua via lua_dobuffer (0x478de0, status 0 em sucesso); lua_pushstring 0x476c40 confirmado funcionando.
- Duas instâncias, anfitrião + cliente, ambas criam “coop_dog1”: o cliente disparou nele 50 vezes; log do anfitrião
  "event 1 on coop_dog1 ... hp 98 ... hp 0" e log do cliente "event 2 on coop_dog1 ... hp 98 ... hp 0" correspondem em
  cada golpe; morreu nos dois jogos.
- O Doganboy do anfitrião não atacou o fantoche do cliente neste teste (sem eventos HURT), e a IA do próprio
  Doganboy do cliente ainda atacou o cliente (cada jogo executa sua própria IA inimiga; inimigos controlados pelo anfitrião são o próximo passo).
Desconhecido: se a IA inimiga alguma vez mira em um OBJ_KURT não jogador; gobs sem nome (de geradores) ainda não têm id de rede.

## <a id="session-1h-enemies-2026-10-20"></a>Sessão 1h: inimigos (2026-10-20)
Verificado:
- Tipo de gob: *(short *)(*(gob+0x84)) (mdkGetGobType nativo = 0x40cf20). O índice de classe usado pelo código de
  dano é *(game object + 0xb4) & 0x3f onde game object = *(gob+0x84) (NÃO gob+0xb4: ler isso
  fornecia índices inválidos e causava falha). Descritores de classe: 0x4f64a8[class] -> 14 ponteiros de função.
- Tabela de gobs da engine em 0x524e10: 0x800 entradas {gob *, u16 generation, u16}; handle = gen<<16 | slot
  (0x449560 = mdkGetGob(handle)). Fase 1 cp2: 425 gobs com objetos de jogo.
- Números de tipo OBJ (registrados das globais Lua): 200–254 criaturas (200 BIF, 202 GRUNT, 207 DOGANBOY,
  217 POOPSY, 230 TURRET, 240 SPHEREOFDOOM, 250–254 CONEHEADCIV), faixa 300 itens/armas/coletáveis,
  faixa 400 disparos (403 DOGANBOYSHOT, 455–459 TURSHOT), faixa 500 dispositivos de fase (540 SPAWNER), faixa 600 explosões,
  faixa 700 portas, 800 SCENERY, 802 STATICLIGHT, 803 ROOM, 1101 AMBIENTSOUND.
- omGobEnterStasis oculta completamente o gob (não desenhado, sem IA, não pode ser atingido): não serve para fantoches.
- Perfil da classe 4 (família Doganboy), envolvendo slots do descritor em thunks de contagem: slots +0x4 e +0x1c
  executam uma vez por quadro. Substituir +0x4 por "xor eax,eax; ret" para a IA (sem ataques); o gob continua
  desenhado e atingível. O mesmo slot existe nas classes 13 (sphere of doom) e 19 (turret).
- Nativos: definir posição 0x40dda0(gob, float x, y, z) (por trás de mdkGobSetPositionXYZ);
  excluir 0x449710(gob) (por trás de omGobDelete); lua_pushusertag 0x476ce0(ptr, tolua_tag("OMGOB")) empilha um gob.
- Teste com duas instâncias (anfitrião + cliente, fase 1 cp2): anfitrião anunciou 24 atores posicionados; o cliente vinculou todos os
  24 pelo nome (mesmos handles dos dois lados). Um Doganboy criado pelo anfitrião apareceu no cliente no mesmo
  lugar. A IA do Doganboy do anfitrião ataca o fantoche do cliente (OBJ_KURT não jogador), além do
  jogador anfitrião. O Doganboy espelhado no cliente ainda causa dano por sua animação de ataque copiada;
  o cliente agora ignora dano ao seu jogador vindo de atores/projéteis e aceita apenas HURT do anfitrião
  (hp do cliente 91 após um HURT de 9 pontos). Disparos do cliente mataram o Doganboy do anfitrião, hp correspondeu em cada golpe,
  e seu DESPAWN removeu a cópia do cliente.
Desconhecido / próximo:
- Projéteis não são espelhados (o cliente não vê disparos inimigos do anfitrião); armas do cliente cujo
  dano vem de um gob de projétil (granadas, tiros de sniper) não são encaminhadas porque `from` é o disparo.
- Itens coletáveis (faixa 300), portas (faixa 700), scripts/gatilhos de fase, checkpoints e mudanças de fase executam independentemente.

## <a id="session-1i-shots-2026-10-20"></a>Sessão 1i: disparos (2026-10-20)
Verificado:
- Atualização por gob (em torno de 0x42b3f0) chama o think da classe como think(gob): slot +0x4 normalmente, slot +0x0 quando
  o gob é o controlado pelo jogador (comparado com [0x5494c8]).
- Criar um disparo com mdkCreateObjectLua("", OBJ_DOGANBOYSHOT, ...) no cliente fez o jogo encerrar
  silenciosamente (sem evento WER): o caminho Lua "exit(1). Unable to recover".
- Disparo de Doganboy: 0x434e5c verifica tipo 0xcf (207), 0x44db50(gob, "slot name") escolhe a boca da arma,
  0x42e030(shooter, slot, shot type) calcula posição/direção da boca da arma (0x44e580) e o alvo
  (handle em shooter+0x88 -> 0x449560) e chama create_object.
- create_object = 0x42d360(name, type, scene, parent, slot, &pos, &quat, model, a8, a9, a10, a11), cdecl,
  31 locais de chamada; prólogo 8b 44 24 04 83 ec 0c (7 bytes, sem endereçamento relativo). Para disparos parent = alvo,
  a8 = handle de gob do atirador (dano creditado a ele). Ponteiro da cena principal em [0x549500].
  Tiros de sniper de Kurt (406) são criados com parent NULL e a8 = 0.
- Acertos de sniper são creditados a Kurt (bob, 25 de dano, tipo 0x9), não ao projétil.
- Reproduzir FIRE por create_object original funciona nos dois sentidos: bolas de fogo de Doganboy do anfitrião (403) aparecem
  no cliente, tiros de sniper do cliente (406) aparecem no anfitrião; dano contado uma vez (caminho HIT).

## <a id="session-1j-pickups-2026-10-20"></a>Sessão 1j: itens coletáveis (2026-10-20)
Verificado:
- Índices de eventos Lua: tabela em 0x4f6370, 16 bytes cada: 0 OnUpdate, 1 OnCollision, 2 OnDestroy, 3 OnDamage,
  4 OnHear, 5 OnAnimLoop, 6 OnCustomKey, 7 OnTimer, 8 OnCreate, 9 OnSpawn, 10 OnDie, 11 OnEnterRoom,
  12 OnShotLanded, 13 OnShotExploded, 14 OnOutOfAmmo, 15 OnPickedUp, 16 OnItemUsed, 17 OnModeSwitch,
  18 OnItemEquiped.
- has_lua_event(gob, 15) é consultado apenas nos caminhos de coleta: 0x408d70 (Kurt, após adição ao inventário 0x414e50 em
  +0x6c), 0x419071/0x4190ca (Max, +0x94), 0x4222ef (Doc, +0x64), 0x4157c4 (item usado no local, após
  excluí-lo com 0x449710). Prólogo 53 56 8b 74 24 0c. Um caminho também passa o gob do jogador (“bob”).
- Itens da fase 1 (tipo 300–399, classe 6) têm nomes: l1_r3health01-03 (313 maçã), r3_ham01 (314), l1_r3grenade
  (317), l1_r3dummy (319 isca) em (140, 46, -42), ...
- Duas instâncias: cliente ficou sobre l1_r3dummy -> PICKUP -> anfitrião excluiu sua cópia; o anfitrião, ficando ali depois,
  não coletou nada.
Desconhecido: itens deixados em tempo de execução (sem nome) não são sincronizados; ambos os jogadores podem coletar o mesmo item se
o tocarem dentro de um tempo de ida e volta.

## <a id="session-1k-doors-and-rooms-2026-10-20"></a>Sessão 1k: portas e salas (2026-10-20)
Verificado:
- Porta de proximidade (OBJ_PROXDOOR1 700, classe 17) think 0x4251a0: player = gob_by_handle([0x5494c8]); state =
  *(game object + 0x40) -> { open, hold, ?, radius (float), locked }; abre (animação 0x42) dentro do raio quando não
  bloqueada, fecha (animação 0x43) caso contrário. Apenas o jogador local conta. dr1_01 raio 20, dr1_03 raio 15.
  dr1_02 é bloqueada em Level.Init e desbloqueada por r2_dog01.OnDie (level1.lua).
- Palavra de flags de gob em gob+0xa6: 0x8 = estase (0x449470 define, 0x4494a0 limpa); a atualização da cena
  (0x457xxx -> 0x44b620 por gob, recursiva nos filhos) pula gobs em estase e suas subárvores;
  0x2 = foi atualizado uma vez. Um gob com OnUpdate Lua recebe isso em vez do think de sua classe (0x42b390).
- Gerenciador de salas 0x4302a0 (chamado de 0x40262a): marca cada sala inativa (+0x24 = 1), encontra o gob da câmera
  (handle [0x5494b4], 0x42ae90) e chama mark_rooms(arg, camera, 1) = 0x430020, que ativa a sala cuja
  caixa (+0x2c / +0x38, point_in_box 0x453fc0) o contém mais suas salas visíveis (+0x4 contagem, +0xc array), dispara
  OnEnterRoom (evento 11), música (0x42f0b0), ambiente sonoro (0x42bc90), define sala atual [0x524de0]; depois salas
  inativas entram em estase, ativas saem. Lista de salas: array [0x524380] de [0x524378] structs de sala, [0] = gob da sala.
- Observado: salas do anfitrião perto do fantoche do cliente tinham flag 0x8 e a porta ali tinha flags 0000 (nunca atualizada).
  Após também ativar as salas do fantoche, l1_r4 mostra 0002 e dr1_03 abre para o fantoche.
- Chamar mark_rooms com o gob do fantoche derrubou ambos os jogos (lê campos exclusivos de câmera).

## <a id="session-1l-levels-and-going-down-2026-10-20"></a>Sessão 1l: fases e queda (2026-10-20)
Verificado:
- Laço principal em torno de 0x4025ff..0x402638: trocar modo de jogo (0x42af80, escreve o handle do jogador 0x5494c8),
  0x42fa40, depois gerenciador de salas (0x4302a0), a menos que 0x40e860() == 4, depois update_scene(scene) 0x457520
  (incondicional). Executar Lua com lua_dobuffer logo após update_scene funciona a cada quadro, incluindo título.
- Cada carregamento de fase termina na função Lua level(l, cp, sec) (mdk2.lua); envolvê-la em coop.lua captura
  carregamentos de menu, script (mdkNewGame em level1.lua: 2,12 / 2,1 / 1,10 / 1,12), depuração e salvamento. O gob do jogador
  ainda não existe quando level() retorna (CreateKurt executa, mas mdkGetPlayerGob() é nil); existe um tick depois.
  A tela de título é fase 0.
- Acionadores de scripts da fase 1: OnDamage/OnDie 41 tratadores (sincronizados por dano), OnAnimLoop 25, OnUpdate 11,
  OnTimer 9, OnEnterRoom 4 (l1_con2a02 bloqueia l1_con2adr01; temporizador de dica de l1_r7; l1_r1 vazio; l1_tun13swt apenas na
  build de demonstração para PC).
- Duas instâncias: anfitrião F7 -> LEVEL(1, 2) -> cliente seguiu (log "peer started level 1 checkpoint 2:
  following"), 24 inimigos vinculados. F3 (200 de dano, 100 hp) reviveu cada lado junto ao parceiro com 100 hp.
Desconhecido: gatilhos de proximidade OnUpdate (mdkGobDistancePoint(mdkGetPlayerGob(), ...)) só veem o jogador local;
OnEnterRoom dispara por jogo; mortes que não passam pela função de dano (abismos, mortes por script).

## <a id="qa-2026-10-20"></a>QA (2026-10-20)
`tools/qa.sh` em mdk2-coop: 17 verificações com duas instâncias reais controladas por entrada de teclado/mouse, verificando ambos os
bridge.logs. Resultados: 17/17 localhost; 17/17 com latência de 120 ms / jitter de 40 ms / perda de 5% nos dois lados
(verificações de ataque e disparo de Doganboy foram 0/0 na execução com perdas: o inimigo não agiu na janela).
Nível de QA do relato: automatizado (escopo parcial: apenas área inicial da fase 1, sem partida completa).

## <a id="first-manual-session-2026-10-20"></a>Primeira sessão manual (2026-10-20)
- Jogando na janela do anfitrião, o cliente falhou. O jogo escreve seu próprio minidump
  (<game dir>\mdk2hd_crash_<date>.mdmp, sem evento WER). Exceção 0xc0000005 em 0x40cf66 (has_lua_event,
  lendo gob+0x84 com gob NULL), pilha: tick cooperativo -> Lua -> coop_apply -> 0x42d9fc -> 0x4169da -> 0x403b67.
  Causa: dano APPLY aplicado com atacante NULL; o caminho de dano de Poopsy consulta eventos Lua do atacante.
- Geradores nomeiam todas as criações como "<spawner>_spawn"; r3dogangen da fase 1 cria Poopsies (217) na sala l1_r3.
- New Game: level0.lua mdkNewGame(1,9) (introdução), depois scripts de level1 mdkNewGame(1,12) (queda livre),
  Level.IntroMovieBDone -> mdkNewGame(1,1). Executa nos dois jogos.
- Pressionar Esc na tela de título abre “quit?” com Yes selecionado; a automação não deve pressionar Enter depois disso.

## <a id="second-manual-session-2026-10-20"></a>Segunda sessão manual (2026-10-20)
- Observado: após o trecho de queda livre, o jogador é empurrado até a parede esquerda.
  Medido sem entrada: Kurt anfitrião 80 -> 105.41 com parceiro, permanece em 80 sozinho. Causa: ambos os jogadores surgem
  no mesmo ponto; o fantoche é sólido e recolocado na posição do parceiro a cada quadro, sobrepondo o
  jogador. omGobGMSetSolid(puppet, slot, 0) em cada slot não ajudou (colisão de personagem fica em outro lugar).
  Correção: nunca colocar o fantoche a menos de 3 unidades (horizontais) do jogador local. Ambos permanecem em 80.
- OBJ_DOGANBOYGRENADE (417) é criado por create_object com pos/quat NULL e uma cena não principal: posicionado
  e lançado depois, portanto ainda não é replicado.

## <a id="third-manual-session-2026-10-20"></a>Terceira sessão manual (2026-10-20)
- Subindo o grande poço do ventilador (área l1_r7), o jogador morreu na lava (r7_lava -> bob 500, tipo de dano 0x40). A
  revivificação então aplicou hp-1 do golpe; o dano de lava ainda acionou a sequência de morte, e o anfitrião recarregou com
  level(1, -1) (carregamento instantâneo de save\auto.sav). O cliente seguiu mdkNewGame(1, -1) e falhou:
  0xc0000005 em 0x45b942 sob mdkGobCreateInstant (wrapper Lua 0x42a6a0). Correção: não aplicar nada de um golpe letal;
  traduzir cp -1 para mdkGetCurrentCheckPoint(); cliente ignora checkpoints negativos.
- Marca 1: textura visível apenas de um lado e atravessável, em (263, -77, -169) em
  l1_r5 logo após coletar l1_r5_cloak (OBJ 320). Causa desconhecida (efeito de invisibilidade, geometria original de um lado só
  ou salas extras ativas); F2 agora salva uma captura.
- Tipo de dano de Poopsy visto: 0x422.

## <a id="fourth-manual-session-2026-10-20"></a>Quarta sessão manual (2026-10-20)
- Saltando do topo da fase 1 (área das cúpulas), o jogador caiu para sempre e nunca morreu (anfitrião por último em z -764).
  Verificado: anfitrião sozinho (ponte carregada, sem parceiro, lógica cooperativa ociosa), Kurt caiu 400 unidades abaixo da fase em
  1–6 e continuou caindo por mais de 30 s com 83 hp. Derivado: não há plano de morte ali no jogo (não verificado sem a
  ponte). Correção: com parceiro, z < menor bmin.z de sala - 30 (fase 1: -236.8) move o jogador para o parceiro.
- mdk2.str: contagem u32, entradas de {u32 id, u32 byte offset, i32} a partir de 0x18, texto UTF-16LE a partir de 0x20c4.
  605 "Use the Sniper Mortar" (dica de l1_r7 a cada 75 s), 712–717 dicas de tutorial (teclas padrão: botão direito do mouse
  salta, espaço entra no modo sniper, roda do mouse seleciona munição de sniper, e lança granadas).
- l1_r7 (topo do poço do ventilador): três plataformas com cúpula (platportal1-3, Level.InitPlatform), cada uma com guardas,
  um ventilador (blower, desativado no início), duas com geradores de Doganboy; munição de morteiro sniper é criada na
  plataforma do jogador (l1_r7.SpawnMeSomeMortars) até todas as cúpulas estarem mortas.
- Revivificações vistas nesta sessão: golpes inimigos (tipo 0x2) x3, lava (0x40) x1; nenhum recarregamento depois.

## <a id="fifth-manual-session-2026-10-20"></a>Quinta sessão manual (2026-10-20)
- Usando teclas de checkpoint, depois F8 para fase 2, ambos os jogos encerraram (sem dumps dessa vez).
- Reproduzido com MDK2_START="2 1": um jogo morreu em ~16 s em 2 de 3 execuções. Minidumps (anfitrião e cliente
  idênticos): 0xc0000005 em 0x449715 (gob_delete, gob NULL), chamador 0x4219a0 = tratador de loop de animação da classe Max,
  despachado de 0x42b532 (slot de classe +0x2c, chamado quando uma animação repete, após a verificação Lua OnAnimLoop,
  evento 5). Exclui o gob que um braço de Max segura (estado do braço em game object+0x40, 36 bytes por braço, handle em +0x88).
  O Max fantoche não segura nada; animações copiadas do parceiro o fazem repetir. Correção: gobs espelhados e o
  fantoche também pulam o slot +0x2c. 4/4 execuções sobreviveram depois.
- O jogo vincula salvamento rápido a F6 e carregamento rápido a F7 (mdk2.lua COM_SAVEINSTANT / COM_LOADINSTANT; carregamento instantâneo
  aparece como level(l, -1) com mdkLoadLevelIsInstant() 1). As teclas de checkpoint do mod conflitavam; salvamento e
  carregamento rápidos agora ficam sem atalho no cooperativo.
- mdkNewGame(level, cp[, x]) -> 0x42c2a0(level, cp, x): x (padrão 1) só condiciona a parada de música/som
  (0x470e20/0x470e30); o próprio carregamento é 0x42ea50(level, cp).

## <a id="session-2a-background-testing-and-state-checks-2026-10-20"></a>Sessão 2a: testes em segundo plano e verificações de estado (2026-10-20)
Verificado:
- Modo de teste em segundo plano (`[test] background=1` em coop.ini): a ponte fornece pressionamentos DirectInput programados
  (Lua `coop_press(code, ms)`, escrito pelo harness em `<game dir>\coop\command.lua`) em vez do teclado
  e mouse reais, mantém a janela sem foco atrás de outras, silencia e limita a 60 fps.
  Outros programas permaneceram utilizáveis no mesmo PC durante as varreduras completas.
- `chScreenShot` chamado de um script gera quadro preto e ignora seu nome de arquivo (escreve screenNNNN.tga em
  `%LOCALAPPDATA%\MDK2HD`). As capturas são obtidas do back buffer no hook de SwapBuffers em seu lugar.
- `coop_state(tag)` extrai o mundo de cada jogo (jogadores, fantoche, inimigos sincronizados com hp, atores, itens, portas);
  `tools/statecheck.py` compara anfitrião e cliente. Encontrou dessincronizações que as verificações por recurso nunca viram.
- O cliente termina um carregamento de fase cerca de 1 s após o anfitrião: dumps obtidos logo após carregar mostram itens
  transitoriamente exclusivos do anfitrião. Apenas dumps alguns segundos após carregar são confiáveis.
- `tail | grep -q` sob `set -o pipefail` fornece falso “no match” (SIGPIPE) quando os logs crescem.

## <a id="session-2b-checkpoint-sweep-and-the-bugs-it-found-2026-10-20--21"></a>Sessão 2b: varredura de checkpoints e os erros que encontrou (2026-10-20 / 21)
`tools/sweep.sh` visita todos os 96 checkpoints da lista do menu de depuração com anfitrião e cliente, anda, dispara e
acerta um golpe de cliente em cada um, e verifica: cliente seguiu, ambos vivos, fantoches, todos os inimigos anunciados vinculados,
órfãos, erros Lua, hp inimigo igual, diferenças de estado. Cerca de 55 min, em segundo plano.
Erros encontrados e corrigidos (cada um confirmado repetindo os checkpoints que falhavam):
- Fantoche desatualizado após carregar fase ou checkpoint: o anfitrião desenhava o parceiro na posição da fase antiga por
  cerca de um segundo; o gerenciador de salas mantém as salas do fantoche executando, portanto esse ponto da fase nova despertava e seu
  OnCreate criava itens apenas no anfitrião (armas de Max em 2–3, paraquedas 1–5, invisibilidade 4–2). Pacotes de jogador agora contêm
  fase e contagem de carregamentos do remetente; estados anteriores ao carregamento do parceiro são ignorados.
- Geradores de itens (tipos OBJ 300–399 feitos por geradores 511/540) eram desativados no cliente com os geradores de
  inimigos; reaparecimentos de vida e munição existiam apenas no anfitrião.
- A lista de checkpoints de depuração tem 3–16 (“3–6.5”) entre 3–6 e 3–7; uma correspondência por prefixo enviava F6 de 3–6 para 4-x.
- 9–7: um script exclui `ch1`/`ch2` e cria novos gobs com os mesmos nomes. O anfitrião anunciava a nova criação
  antes da remoção antiga, e `gob_delete` (0x449710) apenas marca um gob: ele permanece na tabela e sua global
  Lua continua válida até a limpeza da cena, portanto a busca por nome do cliente vinculava o novo id ao gob
  moribundo. Correção: remoções primeiro, e gobs que excluímos contam como ausentes pelo resto do quadro.
- 8–5: um soldado criado (`l8r5_sod01_spawn`, tipo 240) tem dois gobs sem informação de objeto (GOB_INFO NULL)
  com seu nome. A verificação de unicidade de nome os contava, o anfitrião recorria a um nome numérico de rede, e o cliente
  criava uma cópia básica de tipo 240, com 0 hp. Gobs sem informação não contam mais.
- 12–6: o cliente despertava salas na posição do corpo do anfitrião, e o anfitrião pela câmera. Um passo à esquerda no
  início colocava o corpo do anfitrião dentro da caixa delimitadora da próxima sala, mas não sua câmera, portanto o OnCreate dessa sala executava
  apenas no cliente (7 itens). Cada jogo agora também desperta as salas no seu próprio jogador.
Derivado: “caiu” em 1–7, 3–9, 4–3, 6–2 e outros eram mortes reais (lava `r7_lava` 500 de dano, disparos inimigos)
capturadas pela revivificação cooperativa, não erros.
Resultado: 96/96 checkpoints limpos no commit 129b7e3 (um dump isolado de item na origem em 10–4 não se repetiu em duas
reexecuções). Essa varredura ocorreu antes da mudança para N jogadores abaixo e não foi repetida desde então.

## <a id="session-2c-n-players-co-op-saves-reconnect-2026-10-21"></a>Sessão 2c: N jogadores, salvamentos cooperativos, reconexão (2026-10-21)
Dos commits 5e48dd6 e ba9cc77 do mod (desenvolvidos em paralelo):
- Jogadores 1..16: o anfitrião é jogador 1 e fornece um slot aos clientes a partir do primeiro pacote deles; clientes falam apenas com
  o anfitrião, que retransmite estados, disparos, coletas e marcadores. Jogadores trafegam como `@p<n>` nos eventos, fantoches são
  `coop_p<n>`; salas, portas e revivificações usam o jogador mais próximo. Épocas de fase substituem a estimativa de contagem de carregamentos.
- Jogadores silenciosos saem após 10 s; um cliente que entra ou reinicia recebe fase, inimigos vivos com hp e
  itens obtidos.
- Salvamentos cooperativos: o anfitrião os solicita (10 s após entrar na fase, após cada checkpoint, a cada 2 min), e cada jogo faz
  um salvamento instantâneo completo de seu próprio mundo sob o mesmo número. Um cliente que falhou retorna em sua cópia do
  salvamento mais recente; um anfitrião que falhou retoma por Load Game > “Resume co-op”.
- Testes: `qa.sh` 30/30 (2 jogadores), `qa_n.sh` 38/38 (3) e 53/53 (8), `qa_save.sh` 31/31 (3) e 41/41 (8),
  conforme relatado nesses commits.
- Várias cópias de teste em um PC: cada cópia recebe sua própria pasta e portas; todas compartilham
  `%LOCALAPPDATA%\MDK2HD` (settings.lua e save\, onde Auto0-3.sav são escritos por todas).
Descobertas das execuções dessa sessão:
- Caminhos de salvamento são cortados em 16 caracteres (`save\coop_t_c.sav` tornou-se ".sa"); salvamentos cooperativos usam `save\c<4 hex id><a|b>.sav`.
- `mdkStartInstantSave(file, desc)` / `mdkStartInstantLoad(file)` são salvamentos de estado completo e funcionam durante o cooperativo com
  fantoches e gobs espelhados presentes. Cuidados: o salvamento traz de volta fantoches antigos (`coop_p*` duplicados), portanto eliminá-los
  após qualquer carregamento instantâneo; `mdkGetCurrentCheckPoint()` retorna -1 após carregamento instantâneo, portanto rastrear o checkpoint por conta própria.
- Carregamentos de fase terminam alguns quadros após `mdkNewGame` retornar. Eventos SPAWN lidos nesse intervalo eram descartados e o
  cliente depois excluía esses inimigos como órfãos; clientes retêm eventos até o carregamento terminar.
- Um cliente que segue um evento LEVEL durante os vídeos de introdução falha (o carregamento de título da própria introdução ocorre sobre
  a fase); LEVEL é retido até o jogo alcançar o título.
- UDP no Windows: sem desativar `SIO_UDP_CONNRESET`, um ICMP de porta inalcançável de um par morto faz a próxima recepção falhar
  com WSAECONNRESET; com vários clientes, isso interrompia precocemente a leitura de cada quadro.
- Os conjuntos de ponteiros de gobs espelhados / estrangeiros devem ser limpos a cada início de fase: o endereço de um fantoche liberado reutilizado por
  um novo inimigo fazia esse inimigo pular sua IA.
- Cerca de 370 MB de memória por jogo. 8 jogadores foram tão suaves quanto 3. Upload do anfitrião é de aproximadamente mais de 20 Mbit/s com 8 jogadores
  em uma fase movimentada, principalmente snapshots completos de animação inimiga para cada cliente (adequado para LAN, precisa reduzir para internet).
- Lua: `bob.orientation` é userdata cujos campos não podem ser lidos; `mdkGobSetOrientation(gob, yaw, 0, 0)` funciona,
  yaw 0 olha para +y.
- O tutorial de Max no início da fase 2 bloqueia salvamento (`Save.intutorial = 1`; o próprio salvamento rápido do jogo também é
  bloqueado). O anfitrião, portanto, também registra seu progresso a cada início de fase e checkpoint, e Resume escolhe esse
  checkpoint quando é mais novo que o último salvamento cooperativo (commit 9ba18c7 do mod; `qa_save.sh` 38/38 com 3 jogadores).

## <a id="parallel-work-on-one-mod-2026-10-21"></a>Trabalho paralelo em um mod (2026-10-21)
- Duas frentes de trabalho editaram a mesma árvore de trabalho ao mesmo tempo; uma alteração de cabeçalho incompleta em uma quebrou a
  compilação da outra. Corrigido dando a cada uma seu próprio worktree e branch Git, suas próprias cópias do jogo e portas, e
  fazendo a etapa de encerramento dos testes fechar apenas processos cujo caminho de executável esteja nas suas próprias cópias (usava
  `taskkill /IM`, o que teria matado os jogos da outra frente).

## <a id="session-2d-player-installer-and-release-2026-10-21"></a>Sessão 2d: instalador para jogadores e lançamento (2026-10-21)
Verificado:
- Steam instala o jogo em `steamapps\common\MDK 2 HD` (appmanifest_213350.acf `installdir`, `buildid` 3902);
  bibliotecas são listadas em `<Steam>\steamapps\libraryfolders.vdf` (entradas `"path"`). O valor HKCU `SteamPath` fica em
  minúsculas; HKLM `WOW6432Node\Valve\Steam\InstallPath` mantém maiúsculas/minúsculas.
- O jogo reescreve `%LOCALAPPDATA%\MDK2HD\settings.lua` do zero quando opções são salvas
  (`mdkSaveControlSettings`, chamado pelo menu de controles): a linha de carregador do mod desaparecia e a próxima execução ficava
  sem cooperativo. Também escrevia as mudanças de teclas do mod nas configurações do jogador. Correção: a ponte (carregada com o executável,
  antes de o jogo ler o arquivo) reinsere a linha na inicialização; verificado salvando opções, reiniciando e
  vendo coop_init executar.
- O jogo inicia normalmente até o título com um settings.lua contendo apenas a linha de carregador (valores padrão para o
  restante), portanto a ponte cria um quando não existe.
- Instalador: script PowerShell 5.1 + wrappers .cmd, sem ferramentas de desenvolvimento. Encontra o jogo, verifica SHA-256 do executável,
  escreve apenas as chaves `[net]` de coop.ini por WritePrivateProfileString (mantém outras chaves), faz backup de
  settings.lua uma vez. Testado em cópias de teste: entrar, mudar para anfitrião, executável incorreto recusado sem alterar nada,
  desinstalação e anfitrião e cliente criados pelo instalador conectando via UDP.
- Lançado como zip de pré-lançamento no GitHub (v0.1.0-alpha). Lacuna conhecida: o Lua distribuído ainda tem os atalhos de
  teclas F de desenvolvimento.
- Varredura com 3 jogos (`MDK2_N=3`): 1–1 .. 1–3 e 8–4 .. 8–5 limpos.

## <a id="session-2e-options--co-op-menu-2026-10-21"></a>Sessão 2e: menu Options > Co-op (2026-10-21)
Verificado:
- Os menus do jogo são Lua (`menu.lua`, `options.lua`): `mdkCreateMenu`, `mdkCreateMenuItem` (texto bruto) /
  `mdkCreateMenuItemW` (id de string), `mdkMenuItemAddCheckBox` (Select(item, n)), `mdkMenuItemAddComboBox` +
  `mdkMenuItemAddComboString` (lido com `mdkMenuItemGetWidgitValue` em Inc/Dec), `mdkMenuItemEnable`. A entrada de texto
  segue o modo do menu de salvamento: `mdkMessageBoxCreate` + `mdkEditString`, depois consultar `mdkGetEditResult()` (1 aceitar,
  2 cancelar) e `mdkGetEditString()` do `Update` do menu, com `conscheme = "poo"` durante a edição.
- Redefinir `BuildOptionsMenu` (de coop.lua) adiciona um item a Options na tela de título e no menu de
  pausa. Itens desativados são desenhados claros demais para ler em um fundo carregado; uma caixa de combinação em um menu JUSTIFY_CENTER é
  desenhada sobre seu próprio rótulo; rótulos longos em um menu JUSTIFY_RIGHT saem pela borda esquerda.
- Teclas de menu de um script: o menu de pausa aparece gradualmente por cerca de um segundo, e pressionamentos antes disso são perdidos.
  Seta para baixo (DirectInput 208) e Enter (28) navegam.
- Fogo amigo: um personagem jogador atingindo o jogador não faz nada, independentemente de quem aplica: a engine ignora um
  atacante de classe jogador contra o jogador, e o filtro de dano do jogador (game object +0x10) descarta o tipo
  de dano 0x1 da arma de jogador. Passado sem atacante e como tipo 0x2 (arma inimiga), acerta (anfitrião 100 -> 93,
  cliente 100 -> 94).
- `mdkGobGetHealth` retornou -2147483648 para o jogador a partir de um comando; game object +0x12 é o hp real.
- Um cliente que aceita datagramas de qualquer endereço continua jogando com o anfitrião antigo após ser direcionado a um novo
  (o antigo ainda envia para ele). Clientes agora recebem pacotes apenas do endereço para o qual estão configurados.
Derivado:
- Configurações decididas pelo anfitrião (fogo amigo, resistência inimiga) são lidas apenas no anfitrião: clientes informam cada
  golpe em outro jogador, o anfitrião o descarta ou aplica.
Evidência: commits 1c7c6af, 3c15d21 do mod; `tools/qa_menu.sh` 26/26 com 3 jogadores (menu alcançado com teclas,
nomes retransmitidos, ping, fogo amigo nos dois sentidos, hp inimigo 100 -> 200 em +50% x 2 jogadores extras, troca de anfitrião ao vivo,
controles, teclas de desenvolvimento, configurações mantidas após reiniciar); qa.sh 30/30, qa_n.sh 38/38, qa_save.sh 38/38.

## <a id="session-2f-players-on-screen-2026-10-21"></a>Sessão 2f: jogadores na tela (2026-10-21)
Verificado:
- O jogo cria seu contexto GL com `wglCreateContext` simples (o executável não importa `wglCreateContextAttribsARB`), portanto
  é um contexto de compatibilidade: em uma GPU NVIDIA (GL 4.6), as chamadas de função fixa funcionam
  ao lado dos shaders e objetos de framebuffer do jogo. Desenho no hook de SwapBuffers: salvar o programa atual,
  framebuffer e unidade de textura ativa, `glPushAttrib(GL_ALL_ATTRIB_BITS)`, empilhar as três pilhas de matrizes, vincular
  framebuffer 0, desenhar, restaurar tudo. Nenhuma mudança visível no próprio quadro ou menus do jogo depois.
- Texto: `wglUseFontBitmapsA` (consultado em opengl32.dll em tempo de execução) de uma fonte Windows. Depois que o jogo mudou
  para 1920x1080, falhava a cada quadro; chamado duas vezes seguidas funciona (nenhuma falha registrada desde então).
- A câmera do jogo é um gob (`mdkGetCameraGob()`, chamado “camera”): posição + quaternion, olhando ao longo de seu
  +y local com +z para cima e +x à direita. No início de 1–2: (80, 190, -28.5), quaternion (0, 0, 0, 1). Seu campo vertical de
  visão é de cerca de 64 graus: Kurts colocados a 3.4 unidades para o lado em profundidades de 8.5 e 12.5 apareceram a 180 e 120 px do
  centro em uma visão de 561 px de altura.
- Kurt tem cerca de 1.45 unidades de altura (pés na posição do gob, cabeça 1.45 acima, da mesma imagem).
Evidência: commit d68742b do mod; `tools/qa_hud.sh` 11/11 (linhas do painel a partir do próprio log da ponte do que desenhou, o
painel alterando pixels do quadro, oculto quando desligado e sob menu, Max na fase 2); qa.sh 30/30,
qa_n.sh 38/38, qa_menu.sh 26/26, qa_save.sh 38/38; uma captura de 8 jogadores com os sete marcadores e linhas.

## <a id="session-2e-network-traffic-and-a-faster-sweep-2026-10-21"></a>Sessão 2e: tráfego de rede e varredura mais rápida (2026-10-21)
Medido (upload do anfitrião, 8 jogos em 2–1 com 71 inimigos, todos se movendo; netstats.c conta cabeçalhos UDP/IP):
- Antes: 27.0 Mbit/s: snapshots de inimigos 21.7, estados de jogadores retransmitidos 4.6. Cada snapshot era uma struct fixa de ~390 bytes,
  quase toda formada por 8 slots de animação; 1 de 24 inimigos em 1–2 tinha alguma animação executando (o restante está em
  salas em estase), e cada inimigo ia para cada cliente 15 vezes por segundo.
- Um bloco de estado de animação tem 10 DWORDs: [0] flags 1, [1] modo 1, [3]/[4] posição normalizada de reprodução (iguais),
  [5] constante por animação (0.405, 0.3125), [6] peso 1.0, [7] 4.0, [9] 1. Apenas [3]/[4] mudam enquanto reproduz.
- Depois: codificação compacta (apenas valores não zero, rotação como int16, posições de reprodução como u16), inimigos enviados apenas
  quando mudam (mais dois envios, depois keepalives de 1 s), estados retransmitidos agrupados por cliente e tick:
  1.3 Mbit/s (inimigos 0.1, retransmissões 0.9, próprio estado 0.3); um cliente envia ~38 kbit/s.
- Todas as suítes passam depois, também com latência de 80 ms / jitter de 30 ms / perda de 3%; varredura completa 96/96.
Derivado: para uma engine que executa a maior parte do mundo em estase, “enviar ao mudar” vale muito mais que melhorar a
codificação; a codificação importou para os próprios estados dos jogadores, que mudam a cada quadro.

A varredura de checkpoints caiu de 35 min para 4 min (236 s) com as mesmas linhas: gastava ~18 de 20.5 s por checkpoint
em esperas fixas e em jogos agindo um após o outro. Agora espera condições (cada cliente vinculou cada
inimigo anunciado; golpes e revivificações pararam), todos os jogos agem ao mesmo tempo, capturas apenas em falhas, e quatro conjuntos
de jogos executam lado a lado em cópias e portas separadas. Uma diferença que desaparece 1.5 s depois é relatada como
transitória (um teletransporte de revivificação capturado no meio), não como falha.

## <a id="session-2g-ai-upscaled-textures-2026-10-21"></a>Sessão 2g: texturas ampliadas por IA (2026-10-21)
Verificado:
- `mdk2.tar` contém 1808 DDS: 770 texturas difusas de 32 bits não comprimidas (BGRA), 511 mapas de normais `ATI2`/BC5 (`_n`), 511
  mapas especulares `ATI1`/BC4 (`_s`), alguns DXT3/DXT5. Apenas 17 têm uma nova difusa HD (`_d`, personagens principais,
  2048); as texturas de fase com `_n`/`_s` mantêm a difusa original, principalmente de 64–512 pixels.
- No modo HD, o jogo desenha Kurt com `kurt_d.dds` (tingido de vermelho em um arquivo modificado: Kurt vermelho), não `kurt.dds`.
- Texturas soltas são ignoradas: um `kurt_d.dds` tingido em `<game>\`, `<game>\override\`, `<game>\data\`,
  `<game>\textures\`, `%LOCALAPPDATA%\MDK2HD\override\` e `\data\` não mudou nada. As strings de caminhos de busca do executável
  (`data\`, `override\`, `override\<language>\`, `scripts\`, `save\`) ficam junto de `\MDK2HD\`.
- O jogo carrega DXT5 (BC3) no lugar de texturas difusas não comprimidas, com um arquivo reconstruído (membros na mesma
  ordem, novos tamanhos); nenhuma outra mudança necessária.
- Memória: um jogo, primeiro checkpoint de cada fase, antes / depois de ampliar 441 texturas para no máximo 1024 BC3:
  pico virtual 1166 / 1183 MB dos 2 GB que um executável de 32 bits sem suporte a endereços grandes recebe; início da fase 1 770 / 984 MB.
- Real-ESRGAN `realesrgan-x4plus` (ncnn/Vulkan): cerca de 0.5 s por textura de 512 em uma GPU de desktop. De perto adiciona
  detalhes plausíveis (rachadura e granulação nítidas onde o original tem manchas); da distância padrão da câmera,
  mipmapping oculta a maior parte, e o ruído fino vira superfícies mais suaves, com aparência pintada. texconv converte
  entrada PNG como sRGB, a menos que se use `--ignore-srgb` (caso contrário, todas as texturas mudam de brilho).
Derivado:
- BC3 em 1024 com mipmaps tem aproximadamente o tamanho dos originais não comprimidos de 512, portanto 4x custa pouca memória.
Evidência: commit bec16c6 do mod; varredura 96/96 com o arquivo ampliado em cada jogo; `-Restore` idêntico byte a byte.

## <a id="session-2f-going-down-reviving-spectating-2026-10-21"></a>Sessão 2f: cair, reviver, observar (2026-10-21)
Verificado:
- A morte do jogador é ANIM_DIE (17): reproduzir uma vez (estilo 3), cerca de 0.93 s, depois a pose permanece. Bloco de estado
  {1, 1, 3, phase, phase, 1.0714, 1.0, 4.0, 0, 1}.
- `mdkDeathCancel()` não apenas para a sequência de morte: carrega instantaneamente o salvamento (“checkpoint -1”).
  Durante a sequência de morte, `mdkGobGetHealth` do jogador retorna NaN/INF; `mdkGobGetHealth` de um jogador
  vivo também lê INF, portanto ler o hp do objeto de jogo em seu lugar.
- `omAnimPlay(player, ANIM_DIE, 0)` em um jogador vivo não faz nada visível: o próprio código de controle do jogador
  restaura sua animação a cada quadro. `mdkDisablePlayerControl()` para o movimento (W não faz nada) e
  `mdkEnablePlayerControl()` o devolve.
- O que funciona para uma pose caída: marcar o jogador como gob espelhado (slots de think de classe e loop de animação
  pulados) e aplicar o bloco de estado de ANIM_DIE a cada quadro, após a atualização da engine e antes de obter o
  snapshot de rede (senão os outros jogos recebem a animação ociosa).
- A câmera padrão (OBJ_DEFAULTCAMERA 110) é classe 0 sem think próprio, portanto não pode ser
  redirecionada envolvendo um think de classe como nas portas de proximidade. Para observar: o corpo oculto
  (`omGobGMSetVisible(gob, 0)`), inalvejável e sem think do jogador morto acompanha a 3 unidades atrás do
  companheiro observado, e a câmera normal o segue. Pular seu think também o impede de coletar itens.
- Tipos de dano (constantes Lua): GOODGUY 1, BADGUY 2, LAVA 4, SNIPER 8, FALLING 16, AREA 32, LAVAFALL 64,
  LAVAFLOAT 128, BLACKHOLE 256, LAVAELECTRIC 512, KNOCKDOWN 1024, LAVADEATH 2048, PUNCH 4096.
- `mdkShowToolTipMessage` recebe um id de string de mdk2.str, não texto; texto próprio precisa da sobreposição (hud.c).
- Um carregamento do checkpoint onde um cliente já está era tratado como “já está aqui” (para evitar carregamentos duplos
  dos próprios scripts do cliente); um recarregamento por derrota de toda a equipe precisa de uma flag de força no evento LEVEL.
Design: caído por 30 s (um companheiro segura R ao seu lado por 3 s; o relógio para enquanto isso),
depois morto e observando até não haver inimigos nas salas em torno do seu corpo (verificado pelo anfitrião) ou um
checkpoint; lava, buracos negros e o vazio levam direto à morte; todos caídos recarrega o checkpoint.
Testes: tools/qa_revive.sh 33/33 (3 jogos); todas as outras suítes e a varredura completa passam.


## <a id="recorded-route-progression-bot-2026-10-21"></a>Bot de progressão com rota gravada (2026-10-21)
Observações:
- Adicionadas gravação de teclado/mouse na ponte e reprodução temporizada, usando o caminho normal de entrada do jogo.
  Rotas contêm transformações observadas e transições de checkpoints como asserções; sem teletransporte na reprodução
  nem avanço de checkpoint. Gravações completas e versionadas são validadas antes da reprodução.
- Adicionados executor anfitrião/cliente em segundo plano, comparações dos mundos nos limites de progressão e no ponto final,
  verificações estritas de participantes/vidas, esperas limitadas e artefatos de falha. Nenhuma rota de campanha incluída.
- Ponte compila com mingw-w64. Testes portáteis do parser/player, verificações ASan/UBSan, testes Windows dos
  wrappers DirectInput reais (eixos/botões, leituras em buffer, peek, liberação de teclas e gravação em primeiro
  plano), quatro testes do avaliador de participantes com mutações de falha e rejeição CLI de versão inválida
  passaram todos. Evidência: worktree do mod `local/replay-validation.txt`.
- Testes ao vivo em cópias descartáveis separadas não conseguiram iniciar a ponte: tanto a nova ponte quanto
  uma build de referência inalterada foram ignoradas, e a DINPUT8.dll do sistema foi carregada em seu lugar.
  ImageLoad PreferSystem32 do processo foi observado ATIVADO. Uma substituição na criação de processo e um marcador .local
  não mudaram o resultado. Paradas apenas as cópias de teste do jogo; nenhuma configuração persistente
  de mitigação alterada.
Derivado:
- Um teste bem-sucedido de parser/entrada estabelece a maquinaria de reprodução, não a progressão de campanha.
  Marcos intermediários ausentes devem falhar mesmo quando o checkpoint final é igual a um já
  visitado antes na gravação; um teste de regressão cobre esse caso.
Desconhecido:
- Causa do comportamento de carregamento da DLL e se é transitório ou específico do ambiente.
- Progressão real com rota gravada em dois clientes, tolerâncias de tempo em combate e cobertura de
  rotas da campanha continuam sem validação. As alegações existentes da varredura de checkpoints não foram ampliadas.


## <a id="projectile-launch-capture-2026-10-21"></a>Captura de lançamento de projéteis (2026-10-21)
Observações:
- Executável de teste verificado como Steam build 3902, SHA-256 bf5faa81b18837b4c07f35941b107e5c23caa8b105536ccd9c8e5a8e37357f43.
- Na desmontagem existente da imagem descriptografada, 0x4305f7 cria a granada de Doganboy (417)
  anexada ao atirador/slot de modelo, com posição e quaternion NULL. O callback de animação
  a desanexa em 0x434d6d e a lança em 0x434d78 por 0x403b00(shot, shooter, target, direction).
- O construtor da classe 5 (0x403830) configura modelo e física sem necessariamente lançar.
  Seu estado em info+0x40 tem ativo em +4, tempo de vida em +0x10, handles de atirador/alvo em +0x18/+0x1c.
  O lançador calcula dispersão de mira/arco balístico e escreve a velocidade em gob->physics(+0x68)+4.
- Adicionadas captura/reprodução de lançamento no worktree do mod: FIRE transporta a transformação concluída, velocidade,
  tempo de vida e dono traduzido; lançamentos do construtor são capturados uma vez após a criação retornar;
  lançamentos adiados são capturados pelo hook do lançador. Disparos reproduzidos permanecem estrangeiros. Lançamentos
  de atores/fantoches espelhados são descartados para evitar disparos duplicados de chaves de animação copiadas.
- Compilação e testes de captura/reprodução com engine falsa passaram. O qa.sh existente com dois jogos concluiu
  34 passed, 0 failed (evidência: local/qa/20261021-183817 do mod).
- Os processos filhos Windows tinham flags de política de carregamento de imagem 4 (PreferSystem32Images),
  carregando DirectInput do sistema em vez do proxy. Um inicializador local Win32_Process.Create produziu
  flags 0 e carregou o proxy adjacente do jogo não modificado. Nenhuma configuração do sistema foi alterada.
Derivado:
- Um hook de projétil apenas na criação perde disparos anexados à mão e pode reproduzir uma trajetória diferente
  quando o lançador real executa depois ou adiciona dispersão aleatória de mira. Capture o estado final do lançamento.
Desconhecido:
- Verificações determinísticas de voo/dano do tipo 417 com três jogos ainda estão executando; resultados a seguir.

Acompanhamento da validação de projéteis (2026-10-21):
Observações:
- O primeiro teste determinístico com três jogos falhou corretamente: viu reproduções de tipo 417 criadas, mas
  suas posições amostradas eram estacionárias. O remetente se movia. Causa raiz: flag 0x8 do descritor
  seleciona um corpo rígido que quica; 0x403e0c escreve sua velocidade em gob->body(+0x80)+0xb4, enquanto
  disparos que não quicam usam gob->physics(+0x68)+4. Atualizadas captura/reprodução e a fixture de engine falsa
  para cobrir ambos os layouts.
- Após a correção, tools/qa_shots.sh passou com três jogos reais: anfitrião e cliente lançaram cada um
  uma granada de tipo 417; as seis combinações origem/par tiveram exatamente um callback OnSpawn
  e mudaram de posição entre amostras, e as quatro cópias estrangeiras suprimiram dano injetado.
  Evidência: local/qa-shots/20261021-184551/game1.log .. game3.log do mod.
- A velocidade de lançamento de tipo 417 da origem foi (0, -14.14, 14.14), correspondendo à velocidade de 20 unidades;
  amostras de posição dos pares seguiram o mesmo arco. A captura anterior à correção lia um vetor de gravidade em seu lugar.
Derivado:
- Um log de reprodução criada não é teste de voo de projétil. Capture o gob reproduzido e amostre seu
  movimento real; uma engine falsa deve modelar cada backend de física em vez de pressupor um layout.
Desconhecido:
- Cobertura de projéteis na campanha completa e jogo pela internet continuam não testados por esta verificação focada.


## <a id="projectile-launch-replication-2026-10-21"></a>Replicação de lançamento de projéteis (2026-10-21)
Observações:
- Steam build 3902, SHA-256 do executável bf5faa81b18837b4c07f35941b107e5c23caa8b105536ccd9c8e5a8e37357f43.
- O caminho da granada de Doganboy em 0x4305a0 cria tipo 417 anexado ao atirador e slot da mão,
  sem argumentos de posição ou orientação. A liberação por animação em 0x434d6d muda seu pai para a
  cena principal, depois chama launch_shot em 0x403b00. Criação não é lançamento.
- O ramo do construtor da classe 5 em 0x42da26 inicializa 406 (tiro de sniper) e 417 sem lançar.
  Outros ramos da classe 5 chamam 0x403b00 dentro de create_object. Capturar os dois hooks os duplicaria.
- 0x403b00 calcula orientação e velocidade finais, registra handles de dono/alvo e ativa
  o projétil. Velocidade fica em gob->physics (+0x68) +4, ou gob->movement (+0x80) +0xb4 quando o
  +0x54 da definição do disparo tem flag 0x8. Estado do disparo é gob->info (+0x84) -> +0x40; +4..+0x14 são
  cinco valores sem ponteiros (ativo, idade, flags, temporizadores); +0x18/+0x1c são handles de dono/alvo.
- A ponte agora envia FIRE de classe 5 pelo hook de lançamento, captura esse resultado e o restaura na
  reprodução. Lançamentos automáticos de construtor são suprimidos durante a reprodução: o lançamento nativo chama
  OnSpawn do atirador e usa mira/aleatoriedade locais. Outras classes de projétil mantêm reprodução da criação.
- FIRE usa uma union sobre seus bytes não usados do nome do atacante para o estado de lançamento, mantendo eventos de 128 bytes.
  A assinatura de jogador é MDKC para uma ponte antiga não criar silenciosamente reproduções inertes. Reproduções permanecem estrangeiras;
  handles de dono e alvo são traduzidos, e atiradores espelhados/estrangeiros não podem anunciar outro disparo.
- tools/test_shots.sh passa com o shots.c real e um dublê de engine. Remover a flag de lançado
  faz suas asserções falharem. Cobre lançamento adiado e imediato, ausência de FIRE duplicado, dono ausente,
  tradução de alvo/jogador, armazenamento alternativo de velocidade, supressão de estrangeiros/espelhados, falha de criação,
  limpeza e o ponto de entrada de QA nativo de sniper exclusivo do segundo plano.
- Três jogos reais, latência de 80 ms / jitter de 30 ms / perda de 3%: tools/qa_shots.sh 26 passed, 0 failed.
  Ambos os clientes mostraram granadas de Doganboy ativas, estrangeiras e em movimento; cada posição/velocidade de lançamento correspondeu,
  todas as granadas expiraram e o lançamento nativo de sniper de um cliente foi retransmitido exatamente uma vez a cada par.
  Evidência: local/qa-shots/20261021-184701 do mod (logs e duas amostras de voo por cliente).
Derivado:
- Reproduzir apenas argumentos de criação não pode replicar um projétil cujo construtor o deixa inativo
  ou cujo lançamento posterior sobrescreve a transformação. Capture o resultado final do lançamento em seu lugar.
Desconhecido / limites da validação:
- Os novos processos de teste desta máquina selecionaram a DLL DirectInput do sistema; um inicializador de teste isolado
  carregou a ponte explicitamente. A entrada programada não alcançou esses processos. A suíte de projéteis usa
  ações nativas da engine, e a varredura de checkpoints usa callbacks e ações nativas de checkpoint em vez
  de entrada. Nenhuma inferência sobre controles de entrada ou inicialização normal da versão publicada decorre dessas execuções.
- Uma partida completa da campanha e cada variante incomum de projétil continuam sem verificação.

Validação final de checkpoints para a mudança de projéteis:
- 96/96 verificações de carregamento/estado com ações nativas, 168 s, dois jogos em cada um dos quatro conjuntos isolados;
  todos seguiram e sobreviveram, zero erros Lua, divergências de hp inimigo ou falhas persistentes de
  estado do mundo. Criações exclusivas do cliente foram eliminadas normalmente; avisos de verificação de estado são mantidos no relatório.
  Evidência: local/sweeps/20261021-184731-x4/results.md do mod. Usa o carregador explícito e a substituição por ações
  nativas descritos acima; as suítes originais controladas por entrada continuam sem verificação.


## <a id="steam-transport-merge-into-master-2026-10-21"></a>Merge do transporte Steam no master (2026-10-21)
Observações:
- Transporte Steam, menus de lobby, atualizações do instalador e fixtures offline registrados no commit 032274a.
- Merge no master como cfe06c2, preservando o commit 27cfc6f de reprodução de entrada gravada.
- Resolvido o conflito do Makefile da ponte mantendo steam.c, route.c e bot.c,
  com dependências de steam_abi.h e route.h.
- A DLL Win32 combinada compilou com sucesso. tools/test_network.sh passou 234 verificações;
  tools/test_replay.sh passou verificações de reprodução/progressão de rotas, verificações Windows de entrada
  e quatro testes Python. Verificações de sintaxe shell e de git diff passaram.
Desconhecido / limites da validação:
- Este merge não executou clientes do jogo nem testes ao vivo de conta Steam; convites com duas contas,
  conectividade de relay e jogabilidade continuam sem validação. Nenhum commit foi enviado por push.


## <a id="consolidated-projectile-change-2026-10-21"></a>Mudança consolidada de projéteis (2026-10-21)
Observações:
- Consolidadas duas implementações sobrepostas em uma. A mantida permanece como base, incluindo a solução alternativa opcional de inicializador
  MDK2_PROCESS_SERVICE=1; a proteção de protocolo, salvaguardas de reprodução e testes adicionais da outra estão incluídos.
- Layout canônico de FIRE: evento existente de 128 bytes, part = 1, extra[0] = atirador traduzido;
  a union não usada de nome do atacante transporta velocity[3], depois cinco DWORDs de estado sem ponteiros.
  A assinatura de jogador é MDKC, impedindo pontes antigas de apenas criação de aceitar o novo payload.
- A reprodução suprime lançamentos do construtor e restaura o estado gravado diretamente, sem chamar
  scripts OnSpawn do atirador nem precisar de atirador vivo. Traduz handles de dono/alvo e restaura
  a exclusão nativa de colisão com dono quando ele está disponível. Atiradores espelhados/estrangeiros não podem
  anunciar filhos autoritativos. Endereços de alocação reutilizados têm flags antigas de disparos removidas primeiro.
- Testes consolidados com engine falsa passaram, incluindo ambos os layouts de velocidade, atiradores ausentes,
  scripts de construtor suprimidos, tradução de dono/alvo, reutilização de geração de handle no mesmo quadro,
  automação de sniper exclusiva do segundo plano e limpeza de propriedade. Tamanho e offsets do payload são verificados por asserções.
- Compilação final passou com mingw-w64. O tools/qa.sh combinado com entrada normal passou 34/34 verificações,
  incluindo diferenças de mundo e transições de fase (local/qa/20261021-190351 do mod).
- Três jogos com latência simulada de 120 ms, jitter de 40 ms e perda de 5%: tools/qa_shots.sh passou
  todos os seis casos de voo origem/par e quatro verificações de dano de reprodução, sem callbacks de atirador nos pares
  (local/qa-shots/20261021-190105 do mod). O tools/qa_shots_native.sh importado passou 26/26 verificações:
  liberação real de granada segurada de Doganboy, transformações de lançamento correspondentes, voo estrangeiro ativo, expiração,
  exatamente uma reprodução de sniper de cliente em cada par, processos sobreviventes e nenhum erro Lua
  (local/qa-shots/20261021-190148 do mod). Os inicializadores usaram executáveis não modificados Steam build 3902.
Derivado:
- A restauração final de lançamento deve ignorar scripts do atirador e manter sua exclusão de colisão;
  chamar o lançador novamente apenas para ativar uma reprodução introduz efeitos extras e exige dono vivo.
Desconhecido:
- A campanha completa e todas as variantes incomuns de projéteis não foram percorridas por essas verificações.

## <a id="2026-10-21-merged-parallel-branches-shots-qa-on-the-merged-tree"></a>2026-10-21: branches paralelas mescladas, QA de disparos na árvore combinada

Observado:
- Duas branches implementaram independentemente replicação de projéteis lançados (mesma extensão do evento
  FIRE, mesma mudança de assinatura de pacote). Ambas não podem ser mescladas; a que tinha um dublê de teste unitário,
  supressão de ataque copiado e script de QA nativo foi mantida; a outra foi arquivada como patch e descartada.
- No master combinado: teste unitário passa; `qa_shots.sh` 6/6 e `qa_shots_native.sh` 26/26 com 3 jogos.
- `qa_shots*.sh` com `MDK2_N=3` encerra silenciosamente sem diretório de saída quando `mdk2-test3` não existe
  (saída da instalação enviada a /dev/null). Correção: definir `MDK2_DIR_BASE` como prefixo com cópias numeradas.
Derivado:
- Frentes paralelas na mesma tarefa duplicarão trabalho; verificar `git worktree list` em busca de assuntos
  sobrepostos antes de começar.

## <a id="2026-10-21-ai-texture-upscaler-removed"></a>2026-10-21: ampliador de texturas por IA removido

Observado:
- Lado a lado em 1440p, mesmo lugar (um jogo com o arquivo ampliado, um com o original): o
  ampliado era muito mais escuro e plano; a iluminação quente da parede e a geladeira iluminada desapareceram. Detalhes
  difusos (veios da madeira, pontilhado do teto) estavam um pouco mais nítidos.
- Tela cheia em um monitor escolhido funciona apenas por `chVideoChangeMode(<index into the resolution list>)`
  (entradas da lista são por driver de exibição); `chSetVideoMode` fornece janela com moldura. `chScreenShot` de um
  comando gerou quadros pretos em tela cheia; capturar o monitor pelo Windows funcionou.
Hipóteses (não testadas):
- Alfa dos originais contendo iluminação/brilho perdido no Real-ESRGAN, ou mudança de espaço de cor na etapa BC3.
Decisão: o resultado foi julgado pior que o original; a ferramenta, seus dois inicializadores e a documentação foram removidos do mod
(a sessão 2g acima descreve o recurso removido).

## <a id="2026-10-21-couch-split-screen-co-op-by-multi-instance"></a>2026-10-21: cooperativo local (tela dividida) por múltiplas instâncias

Observado:
- Duas cópias iniciadas com `[couch]` (janelas sem bordas 1280x720 empilhadas em uma tela,
  `chSetVideoMode('', 0, 0, w, h, 165, 0)` de Lua no início) renderizaram nesse tamanho e se conectaram por
  localhost; HUD e marcadores de nome funcionaram em cada janela.
- Estado XInput simulado (analógico esquerdo para frente por 3 s) moveu o jogador ~30 unidades no mundo do anfitrião; o analógico
  direito girou a câmera.
Derivado:
- A engine tem um gob de jogador, uma câmera e um passe de renderização, portanto tela dividida no processo não foi tentada;
  N processos em mosaico em uma tela reutilizam toda a sincronização cooperativa. Custo é N vezes CPU/GPU/RAM.
- Gamepad -> teclado/mouse sintéticos que o modo de teste em segundo plano já fornece a DirectInput funciona sem
  foco da janela.
Desconhecido: controles reais, 3–4 janelas, se as opções salvas de um jogo (settings.lua compartilhado) fazem configurações locais
(volume 0, 1280x720) vazarem para o jogo normal.

## <a id="2026-10-21-pre-launch-launcher-inside-the-proxy-dll"></a>2026-10-21: inicializador antes da execução dentro da DLL proxy

Observado:
- Ordem de inicialização em bridge.log: DllMain (ponte anexada) -> primeiro `CreateWindowExA` do executável -> settings.lua
  -> `coop_init`. Portanto uma interface modal executada dentro do primeiro `CreateWindowExA` (hook IAT, thread do jogo, lock do carregador
  liberado há muito tempo) vem antes de o jogo ler settings.lua ou o mod ler coop.ini.
- `mdk2hd.exe` importa estaticamente `DINPUT8.dll` e `CreateWindowExA` / `RegisterClassA` de user32.
- `Titlescreen_PC.dds` (1024x1024) e `font.dds` (512x512) em mdk2.tar são DDS não comprimidos de 32 bits (flags de
  formato de pixel 0x41, máscaras R 0xff0000 G 0xff00 B 0xff A 0xff000000) com linhas armazenadas de baixo para cima.
  `font.lua` contém `dim`, 16 linhas de 16 larguras de avanço em unidades de célula, indexadas `dim[col][row]` para
  o caractere `row * 16 + col`; células 32x32, glifos alinhados à esquerda, layout ASCII simples.
- A linha de vídeo de settings.lua é `chSetVideoMode('<s>', a, b, width, height, hz, fullscreen)`; o padrão
  do jogo (defaultconfig.lua) é `( "", 2147483648, -1, 640, 480, -1, 1 )`. O inicializador reescreve largura,
  altura e o último argumento ali antes de o jogo ler o arquivo; o jogo então iniciou e executou
  (tamanho da janela não medido).
- `tools/qa_launcher.sh` (mdk2-coop, inicializador oculto e controlado por arquivo de comandos): 23/23, cobrindo entrada UDP
  em endereço digitado (anfitrião registrou "player 2 joined from 127.0.0.1"), solo deixando coop_init inerte
  com o jogo ainda executando, Esc encerrando antes da janela do jogo, `[launcher] show=0` e
  `+connect_lobby` pulando-o.
Derivado:
- Uma tela antes da execução não precisa de executável separado nem opção de inicialização Steam: a DLL proxy já carrega primeiro.
- Configurações que só se aplicam na inicialização (transporte, papel, portas) podem ser mudadas ali e entram em vigor imediatamente.
Desconhecido:
- O caminho de janela visível (não teste), tratamento real de mouse e escala DPI não foram exercitados pelo
  QA em segundo plano (nunca mostra janelas); deixados para teste manual.
- Argumentos a e b de chSetVideoMode; se a resolução / flag de tela cheia reescrita é respeitada
  nesse início (esperado, pois o arquivo é lido após o hook, mas não medido).

## <a id="2026-10-21-players-through-walls-hud-outline"></a>2026-10-21: jogadores através das paredes (contorno no HUD)

Observações:
- Marcadores de nome já eram desenhados em 2D com teste de profundidade desligado, portanto já aparecem através de paredes.
- Adicionado contorno de cápsula colorido por slot (horizontal quando caído), desenhado do mesmo modo; `[hud] outline`, ativado por padrão.
- Captura de uma execução com 2 instâncias de `tools/qa_hud.sh` mostra o contorno em torno de um parceiro na borda da tela.

Fatos derivados:
- `MAX_PLAYERS` é 16; uma tabela de cores com tamanho 8 indexada por slot lia além do fim e desenhava preto para o slot 8.
- O contorno é uma cápsula de tamanho fixo dos pontos projetados de pés e cabeça, não a silhueta da malha.

Desconhecido:
- Uma silhueta real da malha (redesenhar o fantoche com teste de profundidade desligado) não foi tentada; exige hook no renderizador do jogo.
- Tamanhos de contorno para Max e Doc (mais alto/baixo que Kurt) não foram medidos.

## <a id="2026-10-21-controls-presets-and-a-drawn-keyboard-view"></a>2026-10-21: predefinições de controles e uma visualização desenhada do teclado

Observado:
- Os menus do jogo ficam na região 4:3 central da janela (menu x 0..1 = essa parte, rótulos terminam em x, widgets
  de valores seguem à direita dele); em uma janela 16:9 há uma faixa livre de cada lado, portanto uma sobreposição desenhada pela ponte
  pode ficar ao lado do menu do jogo. A sobreposição é desenhada após o menu, portanto deve deixar sua coluna
  livre; uma caixa de escurecimento em tela cheia ocultava o menu.
- Revincular reutiliza a captura do próprio jogo: `conscheme = "poo"`, `mdkShowMouse(0,0)`, depois `omGetKeyPress()` a cada quadro
  (-1 nada, 1 Esc cancela). Uma tecla entra nos dois slots de uma ação e a mais antiga sai.
- Códigos do mouse (nomes do próprio jogo): 1000 / 1001 botões, 1002 "Mouse B3", 1003 "Mouse B4", 1008 / 1009 roda.
- Vários processos editando settings.lua compartilhado ao mesmo tempo: `sed -i` falha ("cannot rename ... Permission
  denied") enquanto algum jogo o mantém aberto. Um arquivo de trabalho por `MDK2_SETTINGS` funciona quando a linha de carregador já está ali.
- `tools/qa_controls.sh` 30/30, `tools/qa_menu.sh` 26/26 com a mudança.
Derivado:
- Original e Modern são tabelas sobre uma lista de ações com os comandos do jogo aos quais as teclas de cada uma estão vinculadas;
  uma lista “set” diz quais ações são usadas juntas, para tirar uma tecla de quem a tinha.

## <a id="2026-10-21-difficulty-presets-and-rules-sync"></a>2026-10-21: predefinições de dificuldade e sincronização de regras

Observado:
- Um golpe por script no próprio jogador do anfitrião (`mdkDealDamage(enemy, player, ...)`) não é uma verificação limpa de HP em um
  teste: um Doganboy criado está vivo e atira no anfitrião enquanto o script executa, portanto diferenças de HP são ruído. O
  hook agora registra `difficulty: <from> -> <to> damage a -> b` sempre que reescala um golpe, e o teste busca um tamanho
  de golpe que o inimigo nunca causa.
- O Lua do jogo é 3.1: sem laços `for` (usar `while`), sem `getn`. Reconstruir uma página de menu dentro de um de seus próprios
  tratadores de item é evitado; em vez disso, as linhas são atualizadas no próprio local.
- `tools/qa_menu.sh` 38/38 e `tools/qa_revive.sh` 33/33 com a mudança.
Derivado:
- Toda dificuldade passa por um único hook de dano do lado anfitrião (golpes do mundo nos jogadores, golpes dos jogadores no mundo),
  pelo hook de criação de inimigos (hp) e por duas constantes em revive.c; o anfitrião envia seus valores aos clientes como evento
  confiável ao entrar e a cada mudança de `[game]`, para os temporizadores de queda e revivificação concordarem em todos os lados.
- Uma predefinição é apenas um conjunto de valores `[game]`; “Custom” é o que não corresponde a nenhuma, portanto não há chave de predefinição para sincronizar.
Desconhecido:
- Dano de projéteis lançados por um cliente (granadas) pode contar como do mundo em vez de jogador para
  `dmg_dealt`; não testado.

## <a id="2026-10-21-controls-page-merged-keys-of-other-features-folded-in"></a>2026-10-21: página de controles mesclada; teclas de outros recursos integradas

Observado:
- As teclas de chat / ping (T, V, botão do meio do mouse) e revivificação (R) eram fixas na ponte, e
  o inventário de Doc em Modern usava R: um conflito encontrado apenas pela leitura do merge. Agora são definidas de Lua
  (`coop_game_keys`), mostradas na aba Co-op da página Controls, revinculáveis e nos conjuntos de conflitos.
- `tools/qa_chat.sh` falhava no master antes do merge: sua regex de mensagem do anfitrião terminava em `$` e a
  linha do log Windows termina em retorno de carro (corrigido com `[[:space:]]*$`).
- Suítes na árvore combinada: qa_controls 36/36, qa_menu 26/26, qa_chat 8/8, qa_revive 33/33.
Derivado:
- Qualquer recurso que lê teclas por conta própria deve obtê-las da tabela de controles, ou dois recursos
  compartilharão silenciosamente uma tecla; a verificação de conflitos só conhece as ações em `coop.actions`.

## <a id="2026-10-22-merging-voice-emotes-outlines-difficulty-couch-and-the-launcher-master-43a34c4"></a>2026-10-22: merge de voz, emotes, contornos, dificuldade, cooperativo local e inicializador (master 43a34c4)

Observado (da mensagem de commit do mod; o resultado combinado não foi executado novamente por suíte aqui):
- Pressionar para falar era uma tecla fixa que conflitava com chat e ping; agora é uma ação na aba Co-op da página
  Controls (B nas duas predefinições) e tem conflitos verificados como as outras. As teclas que a própria ponte lê
  (chat, ping, reviver, pressionar para falar) são ignoradas enquanto uma linha de chat está aberta, portanto digitar “r” ou “b” não
  revive nem fala mais.
- Emotes terminavam em teclas fixas de movimento; agora terminam nas teclas vinculadas a mover, saltar, disparar e modo sniper
  na predefinição ativa, e não enquanto se digita.
- Jogos locais usam a predefinição Modern (as teclas que o gamepad pressiona), pulam o inicializador e não têm chat de voz
  (uma sala, um microfone).
- As entradas de dificuldade e controles do inicializador escreviam chaves que a página Gameplay havia substituído (vida inimiga Hard ou
  Custom de 75% virava 50% a cada Play). Agora oferece as mesmas predefinições e escreve `[game]` apenas
  quando algo muda.
- HUD: o indicador MIC foi movido para o canto inferior direito (chat no inferior esquerdo); um balão de chat fica acima do ícone de
  alto-falante de um jogador que está falando.
Derivado:
- Cada recurso construído em sua própria branch funcionava sozinho; os conflitos eram todos estado compartilhado (teclas, chaves `[game]` /
  `[controls]`, cantos da tela). O merge precisou de uma revisão de cada tabela compartilhada pelos recursos.
Desconhecido:
- A varredura de 96 checkpoints e as suítes anteriores não foram executadas novamente nesta árvore combinada.

## <a id="2026-10-22-six-parallel-feature-branches-merged-outlines-emotes-difficulty-voice-couch-launcher"></a>2026-10-22: seis branches paralelas de recursos mescladas (contornos, emotes, dificuldade, voz, cooperativo local, inicializador)

Observado:
- As seis branches começaram antes de a página Controls e o chat estarem no master. Cada uma mesclou com apenas pequenos
  conflitos textuais (lista de fontes do Makefile, tabelas de menu, enum de eventos), mas três quebras entraram silenciosamente:
  - Dificuldade definia `coop.SetPreset(i)` / `coop.presets` / `coop.PresetName`, e a página Controls já tinha
    `coop.SetPreset(name)` para predefinições de teclas. Globais Lua: a última carregada prevalecia, sem erro. Renomeadas para
    `coop.SetDiffPreset` etc.
  - O inicializador retornava antecipadamente do hook de `CreateWindowExA` quando `!test_background`. O cooperativo local havia substituído
    esse teste por `synth` em todos os outros lugares, portanto as janelas locais teriam mantido borda e tamanho.
  - A linha “Tougher enemies” do inicializador reescrevia `enemy_scale` a partir de seus quatro valores em cada Play (75% de uma predefinição
    Hard virava 50%), e sua linha “Modern controls” escrevia a chave substituída `[controls] modern`.
- Conflitos de teclas: pressionar para falar de voz usava V por padrão (Ping) e oferecia T (Chat). Agora é uma ação da página Controls
  (B, `coop_game_keys` 3). Emotes terminavam em WASD e setas fixas, e agora nas teclas vinculadas a mover, saltar, disparar e
  sniper (`coop_emote_keys`). Teclas cooperativas são ignoradas enquanto uma linha de chat está aberta.
- Jogos locais: jogam com a predefinição Modern (as teclas que o gamepad pressiona), pulam o inicializador e não têm voz.
- Ambiente de teste: jogos iniciados com `Start-Process` deste shell WSL carregavam `dinput8.dll` do sistema. Nenhum código do
  mod executou em qualquer cópia ou commit, incluindo cópias que funcionavam uma hora antes. `mdk_cmd` informava
  "did not pick up" para cada comando, e `bridge.log` mantinha a data antiga. `MDK2_PROCESS_SERVICE=1`
  (`Win32_Process.Create`) carrega o proxy. O próprio início por `+connect_lobby` de qa_launcher agora também o respeita.
- Com isso, no master 606132e: qa_controls 37/37, qa_voice 14/14, qa_menu 38/38, qa_chat 8/8, qa_launcher 23/23,
  qa_hud 11/11, qa_revive 33/33 e varredura completa em 96/96 checkpoints sem erros Lua, divergências de HP ou falhas de
  estado (`MDK2_SHARDS=4`, 236 s).
Derivado:
- Um merge limpo não diz nada sobre entradas compartilhadas (teclas), chaves de configuração, espaço na tela e nomes globais
  de dois recursos. Cada par precisa ser lido em busca disso.
Desconhecido:
- Por que o caminho de inicialização passou a preferir DLLs do sistema entre 23:46 e 23:58 em 2026-10-21.
- Cooperativo local com gamepads reais e voz com microfone real continuam sem teste manual.

## <a id="2026-10-22-automated-regression-ladder-and-oracle-checks"></a>2026-10-22: sequência automatizada de regressão e verificações de oráculos

Observações:
- Adicionado executor sequencial de regressão no worktree do mod: perfis offline, smoke, features,
  campaign e full; tempos limite por etapa, reserva/limpeza do laboratório, validação de resultados
  terminais, resumos JSON/Markdown e rotas opcionais de progressão gravadas.
- Testes existentes de entrada e rede tinham dependências desatualizadas e falhavam na vinculação. A fixture de
  entrada também selecionava a antiga flag de segundo plano em vez do novo modo de entrada sintética.
  Atualizadas dependências da fixture e seleção de modo; testes de entrada passam.
- A recepção do anfitrião agora enfileira EV_RULES antes de eventos de jogo. Atualizadas as asserções de
  sequência/confirmação de eventos confiáveis do teste de rede e verificada a recepção após reinício do nonce.
- Perfil offline passa as cinco etapas: build da DLL, verificações de rota/entrada/oráculo,
  núcleo de projéteis, mapeamento de controles e testes de rede com Steam falsa/loopback.
- A varredura de dois clientes de 1–1 a 1–3 produziu mundos correspondentes (zero avisos de estado
  em cada checkpoint), contagens e HP de inimigos correspondentes e nenhum erro Lua. O primeiro
  avaliador estrito rejeitou incorretamente três mensagens de exclusão de órfãos do cliente em 1–3.
  A inspeção do fonte confirmou que registram remoção bem-sucedida de duplicatas de geradores
  locais; atores removidos são contados como evidência, não divergências sobreviventes do mundo.
- O inicializador de processos padrão não carregou o proxy neste ambiente do agente;
  MDK2_PROCESS_SERVICE=1 o carregou. Ambas as tentativas foram paradas e as reservas liberadas.

Fatos derivados:
- Sucesso do processo da varredura antes não estabelecia sucesso da suíte: o script
  retornava zero mesmo com falhas de estado e linhas de partições ausentes. O novo avaliador
  verifica explicitamente as linhas solicitadas de checkpoints e falha com evidências ausentes/incompletas.
- Coordenadas NaN podem escapar de comparações com limites. A análise de estado deve validar
  posições finitas antes de calcular distâncias; dumps vazios/sem cabeçalho falham.

Desconhecido:
- Validação do perfil de recursos está em andamento. Campanha completa de 96 checkpoints e rotas reais de
  progressão gravada ainda não foram executadas novamente nesta sessão.

Observações adicionais:
- Sequência de recursos: qa_n com três jogadores passou 38/38. qa.sh com dois jogadores passou 30 e
  falhou em quatro verificações de tempo de morte/revivificação; mantidas como falhas, sem relaxar asserções.
- Adicionada etapa de instalador descartável preparando apenas código do mod e lendo um executável
  da reserva. A primeira tentativa de fixture sob UNC WSL falhou na API INI Win32;
  fixtures agora usam a pasta de trabalho NTFS da reserva, com seu local registrado
  no diretório de evidências ignorado. Nenhuma instalação original ou salvamento do dono é usado.
- A suíte Python de oráculos agora tem 20 testes, incluindo falha na coleta de artefatos com
  liberação garantida da reserva. Mutantes cobrem os avaliadores de produção de estado/varredura/executor.

Atualização da validação:
- qa_save passou 38/38; qa_revive passou 33/33; fixtures de instalador passaram 22/22
  após movê-las para NTFS. As reexecuções restantes de recursos de menu/interface foram interrompidas
  para priorizar o novo amostrador de fases; o relatório do perfil de recursos é FAIL com
  uma linha INTERRUPTED do executor, não uma alegação de aprovação completa.
- Teste básico de checkpoints 1–1 a 1–3 passou do início ao fim pelo executor de regressão
  com todos os logs/configurações dos jogos capturados antes da próxima etapa.
- Adicionado --levels à varredura: primeiro checkpoint de cada uma das doze fases,
  usando F8 entre fixtures, com as mesmas ações de jogo e comparações de estado.
  Sua primeira execução chegou às doze com estado correspondente, mas falhou ao escrever
  o resumo porque o fonte shell foi editado durante a execução. Avaliar diretamente as
  linhas salvas passou 12/12. Uma reexecução limpa do início ao fim está em andamento.
- A varredura agora rejeita pontos finais inválidos, contagens inválidas de instâncias/partições e reservas
  pequenas demais para as partições solicitadas. Portas de partições seguem os slots realmente reservados,
  incluindo conjuntos não contíguos, em vez de offsets fixos sobrepostos.
- Perfil offline final passou as cinco etapas, incluindo 235 asserções de rede;
  testes Python agora somam 21. O teste de manifesto exige que toda suíte de jogo qa*.sh
  esteja registrada no perfil full.

Lição:
- Não reescreva um harness shell em execução. Bash pode ler o próximo comando de nível superior
  do arquivo modificado no offset antigo de byte. Termine ou pare a execução primeiro, ou
  execute uma cópia imutável. A falha observada aqui foi sintaxe do executor, não uma
  divergência de estado do jogo; mantenha essa distinção nas evidências e repita a etapa.

Resultado do amostrador limpo:
- A reexecução não modificada de --levels passou os doze checkpoints do início ao fim em
  143.4 segundos, com ambos os processos sobreviventes e nenhuma falha de mundo avaliada.
  Evidência: local/regression/20261022-144137-501292 e
  local/sweeps/20261022-144139 no worktree do mod. A reserva foi liberada.
- Os 96 checkpoints completos e as suítes restantes de recursos/menus não foram repetidos;
  nenhuma travessia completa da campanha ou rota gravada é alegada.

Validação particionada:
- Duas partições (dois clientes reais por partição) passaram fixtures de checkpoints 1–1 e 1–2
  em 39 segundos usando slots reservados não contíguos 0,1,4,5. Isso exercitou resumos
  dos filhos, verificações de saída de todos os filhos, avaliação combinada e atribuição de portas atravessando uma
  lacuna de slots. Evidência: local/sweeps/20261022-144447-x2. Os quatro slots liberados;
  a reserva de dois clientes do outro jogo permaneceu executando.

Validação final de etapa:
- Instalador também passou do início ao fim pelo novo executor (22 verificações, 7.4 segundos),
  incluindo coleta de diagnósticos, limpeza de processos e liberação de reserva. Evidência:
  local/regression/20261022-144550-480965 no worktree do mod.
- Links da documentação, verificações de sintaxe shell e git diff --check passaram. Mudanças
  permanecem no worktree; esta sessão não as publicou nem enviou por push.

Continuação: confiabilidade de revivificação e validação ampliada

Observações:
- O QA inalterado de dois jogadores executou novamente com sucesso, 34/34; as quatro falhas anteriores
  são intermitentes, não um defeito de revivificação reproduzido consistentemente. Evidência:
  local/regression/20261022-145655-357320 no worktree do mod.
- Adicionada fixture sem jogo em torno da implementação real bridge/revive.c:
  69 asserções cobrindo dano/lava/vazio, sangramento até a morte e limitação de pausa, companheiro
  segurando revivificação, verificações de alcance, restauração de vida, observação/alternância, autoridade
  de checkpoint, atraso de zona limpa, derrota/recarregamento uma única vez e alternativa solo.
- Dez variantes de fonte deliberadamente quebradas foram rejeitadas por essas asserções de estado:
  dano inalcançável, observação ausente, alcance excessivo de revivificação, derrota ausente,
  sangramento enquanto revivido, reaparecimento com vida cheia, autoridade incorreta de checkpoint,
  revivificação repetida com tecla mantida, sangramento até a morte causado por pausa e interceptação de morte solo.
- Reformulada a fase de morte para dois jogadores para carregar um checkpoint novo após combate; agora
  verifica estado de vida nativo local/recebido, precondições de sobrevivente e replicação
  antes de solicitar reaparecimentos. Essa mudança está em validação com jogo real.

Fatos derivados:
- As suposições da fixture antiga não eram verificadas: o sobrevivente ainda podia estar
  lutando com inimigos criados antes, e uma espera fixa podia terminar antes de receber
  o estado morto/vivo do par. A nova fixture expõe isso como condições explícitas,
  em vez de tratar uma linha antiga de log como estado de vida atual.

Desconhecido:
- A causa exata das quatro falhas anteriores é desconhecida: os logs completos da ponte
  daquela execução inicial foram sobrescritos antes de adicionar a coleta de diagnósticos.

Regressão de época descoberta ao reforçar a fixture de morte:

Observações:
- Um reinício do anfitrião no mesmo checkpoint gerou uma nova época, mas o cliente registrou
  "already here", manteve IDs antigos de atores e deixou ausente o item já coletado.
  Isso é um defeito de reinício do mundo, além de um problema de precondição da fixture de teste.
- Adicionado qa_epoch.sh: modificar ambos os mundos com uma criação no anfitrião e coleta no cliente,
  reiniciar o anfitrião exatamente no mesmo checkpoint, exigir que os dois jogos realmente carreguem
  e restaurem a fixture, depois cortar a rede do cliente por 12 segundos e exigir
  continuação na mesma época sem outro recarregamento.
- Contra a build antiga, falhou em 5 de 20 verificações: recarregamento do cliente, correspondência do mundo reiniciado,
  restauração da fixture e mundo/fixture após reconexão. Evidência:
  local/regression/20261022-150740-647152 e local/qa-epoch/20261022-150745.
- Uma nova asserção de rede falhou contra o código antigo porque net_level_event
  adotava a época pendente antes de terminar o carregamento. Após a correção, todas as 243
  asserções de rede passam, incluindo adiamento de criações e retorno cíclico da época de 16 bits.
- Corrigido net_level_event para adiar adoção da época para net_level_reset e removido
  o caminho de reutilização de FollowLevel baseado apenas no número do checkpoint. A reutilização na mesma época permanece
  como caso explícito same==2. A validação da correção com clientes reais está em andamento.
- A fixture revisada de QA para dois jogadores passa por 1–1 antes de voltar a 1–2,
  verifica explicitamente carregamentos reais e lê estado de vida local/recebido. Passou
  50/50 antes da correção de época; evidência local/regression/20261022-150457-829600.

Fatos derivados:
- Números iguais de checkpoint não estabelecem mundos iguais. A época deve corresponder
  antes de uma reconexão poder manter com segurança atores/itens e aplicar novos eventos recebidos.

Validação da correção de época:
- O mesmo qa_epoch.sh imutável passou 20/20 contra a build corrigida, incluindo
  recarregamentos reais do mesmo checkpoint, estado restaurado de coletas/criações e nenhum recarregamento em uma
  reconexão na mesma época. Evidência local/regression/20261022-150907-236075.
- A validação completa de recursos agora executa com a build nativa/Lua corrigida. Adicionadas uma
  etapa de época com perdas e uma configuração opcional --campaign-shards no executor, para as fixtures
  completas de checkpoints executarem em conjuntos paralelos limitados com reservas adequadas.

Ampliação de cobertura sem jogo e de movimento:
- A regressão de rede agora inclui quatro variantes quebradas compiladas, todas rejeitadas por
  asserções: adoção antecipada de época, aplicar criações durante carregamento, bloquear uma
  reconexão na mesma época e ignorar época zero. A referência passa 243 verificações.
- Adicionadas telemetria Lua de movimento por quadro exclusiva de teste e qa_motion.sh para caminhada real,
  deslocamento lateral e comportamento de salto/jato em Kurt, Max e Doc nos dois jogos. Nunca escreve
  transformações de jogadores, exige controle ocioso estável, direções de movimento opostas,
  quadros suficientes, jogadores vivos, movimento/subida reais e mundos correspondentes.
  Validação da fixture com jogo real aguarda a reserva de recursos em andamento.
- Avaliação de movimento tem testes de mutação para sondas ausentes/duplicadas, personagem errado,
  zero amostras, estado inválido de vida/menu/carregamento, ociosidade instável, direção errada,
  controles estacionários, subida de salto ausente, NaN/Inf e números malformados. Total de
  testes Python: 26, incluindo verificações de recursos/diagnósticos para etapas particionadas do executor.

## <a id="2026-10-22-mdk-save-lab-trial"></a>2026-10-22 mdk-save: teste do laboratório
- Slots 2,3,4 via `lab acquire --slots 3` (sem espera), `eval "$(lab env mdk2)"`, portas a partir de 27932.
- tools/qa_revive.sh: 33 passed, 0 failed. tools/qa_save.sh: 38 passed, 0 failed.
- Ambos os scripts já reconhecem o laboratório (MDK2_DIR*, MDK2_PORT, MDK2_PIDS do ambiente); sem mudanças.
- Nenhuma colisão vista; os jogos de Witness dos outros agentes executaram simultaneamente, mdk_kill é limitado por caminho.

## <a id="2026-10-22-mdk-sweep-lab-trial-toolsqash"></a>2026-10-22 mdk-sweep: teste do laboratório, tools/qa.sh
- Observado: `lab acquire --slots 2` do worktree forneceu slots 0,1 (dono mdk-sweep); uma reserva executada de outro cwd assume o nome dessa pasta como dono (liberada). Porta 27900, diretórios C:\coop\lab\mdk2\s0/s1, pids em run\mdk-sweep.
- Observado: `tools/qa.sh` com ambiente da reserva: 34 passed, 0 failed (cerca de 4 min), enquanto mdk-save mantinha slots 2–4. Nenhuma colisão vista.
- Observado: verificação “client hurt only via host” passou de forma vazia (0 HURT, 0 golpes do anfitrião).
- Não executados: qa_n.sh, sweep.sh. Nenhum código alterado.

## <a id="2026-10-23-cutscenes-together-shared-go-skip-vote-end-barrier-skydive-ghosts-host-triggered-movies"></a>2026-10-23: cenas juntos (início compartilhado, voto para pular, barreira final, fantasmas de queda livre, vídeos acionados pelo anfitrião)
Observações:
- Cada jogo executa por conta própria os vídeos de uma fase: `StartMovie(gob, { tasks..., Done = fn })` (script.lua) coloca uma lista de tarefas em um gob e
  `ScriptUpdate` a avança; um vídeo do carregamento de fase começa dentro do Init do script da fase, ou seja, dentro da chamada de `level()`
  (a linha de log do primeiro vídeo vem antes de "level N checkpoint M started"). O Done de um vídeo geralmente carrega a próxima fase
  (`mdkNewGame`) ou inicia o próximo vídeo (cena da sala de estar de 1–9 -> vídeo do corredor -> queda livre 1–12 -> 1–1).
- A tecla de interrupção é COM_ABORTMOVIE (Backspace, `comfuncs.game`); `StopScript` executa Done ou, com um minijogo depois na
  lista (fases 1, 2, 5, 9), pula para o minijogo; `Save.inminigame` bloqueia a tecla durante ele.
- Com teclas de desenvolvimento ativas, o navegador de emotes vinculava Backspace ao comando de parar; a engine dá uma tecla ao último comando vinculado e o
  jogo salvava isso em settings.lua, portanto interromper vídeo depois lia -1 (tecla morta) em cada início posterior, incluindo cópias de teste
  (settings.lua é compartilhado por todas as cópias). Revincular o comando no início (omBindCommandI) corrigiu isso.
- Lua 3.1 não tem `true` (uma global indefinida, nil): um mutante "if (true) then" nunca executava.
- Eventos enviados por um cliente enquanto sua fase ainda carrega contêm a época antiga e são descartados pelo anfitrião: enviar do tick do
  próximo quadro, depois de a chamada de carregamento retornar.
- Execução de tools/qa_cutscene.sh com 2 jogadores: 34 de 34 (cena da sala de estar e vídeo do corredor pulados por voto, queda livre pulada até o
  minijogo, minijogo não pulável, anfitrião espera na retenção final até o cliente aterrissar, ambos carregam 1–1, um vídeo substituto
  acionado pelo anfitrião reproduzido pelo cliente, fantasma do outro jogador no céu, captura mostra ambos em queda livre);
  mutantes “no end barrier” e “one-player vote” são capturados pelas verificações que os protegem.
Derivado:
- Vídeos precisam ser mantidos juntos, não copiados: os mesmos scripts executam em todo lugar, portanto o anfitrião só precisa dizer quando começar, se o
  voto passou e quando todos chegaram ao fim. Um script pausado (`stack.paused`) é uma barreira limpa de início; envolver `sc.Done`
  é uma barreira limpa de fim (Done executa do tick do anfitrião quando cada jogo tiver informado).
- Vídeos acionados (entrada de chefe, cena do ventilador) só reproduzem no jogo cujo jogador os acionou; as funções que os iniciam
  (`Level.PlayBossMovie`, `l1_r6.StartCutScene`, ...) podem ser envolvidas para o anfitrião anunciá-las e os outros chamarem sua própria cópia.
Desconhecido:
- Vídeos acionados em fases além do substituto na fase 1 (envolvidos por nome a partir dos scripts, não executados): as cópias dos clientes
  da função podem depender de estado que o jogo do anfitrião tem (gobs de chefe, itens); são chamadas de forma protegida.
- Com três ou mais jogadores reais: contagens seguem regra de maioria, apenas dois foram executados.

## <a id="2026-10-23-later-ghosts-in-the-other-three-minigames"></a>2026-10-23 (mais tarde): fantasmas nos outros três minijogos
Observações:
- Fases 2 (checkpoint 13), 5 (11) e 9 (13) têm cada uma um minijogo estilo torpedo: uma nave (`torpgob`, `podgob`, `jdgob`) controlada em um ou dois eixos
  (apenas z; x e z; x e z) em profundidade fixa, desviando de meteoros; um golpe define `.dead`, o script do vídeo tenta novamente com resultado negativo.
- Fantasmas dos outros jogadores (seu próprio modelo de nave, posicionado pelos dois números que enviam) aparecem em capturas das fases 2 e 9
  (qa_minigames 15/15 por linhas de log). Na captura da fase 5, a própria cápsula do anfitrião havia acabado de explodir, portanto nenhum fantasma é visível ali.
Desconhecido: aparência dos fantasmas em movimento com vários jogadores; fantasma da fase 5 visualmente.

## <a id="2026-10-23-controls-page-in-the-games-colours-gamepad-tab-pad-in-normal-games"></a>2026-10-23: página Controls nas cores do jogo, aba de gamepad, controle em jogos normais
Observações:
- A imagem de Controls agora usa preto e âmbar com painéis recortados (painéis de cabeçalho, abas e mouse compartilham um auxiliar
  `panel()` em ctrlview.c); qa_controls 40/40 com uma nova página Gamepad e uma verificação de que o controle segue cada predefinição.
Derivado:
- As teclas de ação do controle vêm da predefinição por `coop_pad_keys`; as setas permanecem pressionadas ao lado delas para os menus funcionarem.
- Em um jogo normal, o controle é combinado às leituras reais de teclado/mouse (estado e em buffer), apenas enquanto a janela tem foco.
Desconhecido:
- O caminho de controle fora do cooperativo local com controle real: apenas mapeamento (pad_test) e página Controls executados. Controles reais, manualmente, não testados.

## <a id="2026-10-23-character-wheel-switch-hero-at-any-time"></a>2026-10-23 roda de personagens (trocar herói a qualquer momento)
Observações:
- Cada script de fase chama exatamente uma de CreateKurt / CreateMax / CreateDoctor (fases 6 e 12: CreateDoctor + CreateHyde).
- “Switch Player Character” do menu de depuração (debug.lua) exclui a câmera, chama CreateX(), move `bob` para a posição
  antiga e exclui o gob do jogador antigo. Fazer o mesmo de Lua em uma fase em andamento funcionou para Kurt <-> Max <-> Doc na
  fase 1 (checkpoint 2), embora essa fase normalmente só tenha Kurt: tipo de jogador relido como 100 / 101 / 102.
Derivado: o fantoche deve seguir player_type do par (já trafega em cada pacote); a ponte o substitui em uma mudança.
Desconhecido: troca em fases de Hyde (deixadas de fora), vida transferida (não feito: novo herói começa do zero), fases além de 1–2.
Evidência: tools/qa_char.sh 9/9, tools/qa_char2.sh 7/7 (2 jogos), qa.sh 50/50, qa_emote 19/19, qa_controls 37/37.

## <a id="2026-10-23-softer-player-outlines-hud-text-in-the-games-menu-font"></a>2026-10-23: contornos de jogador mais suaves, texto do HUD na fonte de menu do jogo
Observações:
- Contornos agora são uma curva em forma de pessoa (Catmull-Rom por ~35 pontos: cabeça, ombros, braços, pernas), 1.5 px com uma linha
  escura tênue por baixo, alfa de no máximo 0.6, desaparecendo gradualmente entre 11 e 3 unidades de jogo da câmera; deitado quando caído;
  mais largos para Max e Doc. Visto em captura de qa_hud com 3 jogos: fino, legível, aproximadamente do tamanho do fantoche.
- `font.dds` do jogo tem maiúsculas e minúsculas; o HUD (marcadores, painel, chat, títulos) o desenha como quads com textura (célula de 32 px,
  tingida), compartilhando o carregador do inicializador. Texto pequeno da página de controles permanece na fonte Windows (a folha é suave demais em ~10 px).
Desconhecido:
- Verificações de linhas do painel de qa_hud (3 de 11) falham nos números de slot do texto da linha (linhas mostram 5 e 6, o script espera 2 e o
  slot do cliente); não investigado, não causado pelo desenho.
- Não é silhueta de malha: a forma é genérica, a pose do fantoche não é seguida.

## <a id="2026-10-23-save-browser-sessions-and-level-picker"></a>2026-10-23: navegador de salvamentos (sessões) e seletor de fases
Observações:
- O jogo corta o caminho inteiro do salvamento em 15 caracteres (`save\` + 6 + `.sav`), portanto um nome de arquivo de salvamento cooperativo é `c` + 2 dígitos de base 36 do
  id de jogador da cópia + 2 da sessão + a/b. Minha primeira tentativa (`c` + 4 hex + 4 hex + a/b) nunca foi escrita: "co-op save N: ... was not written".
- Lua 3.1 não tem upvalues: uma função `Select` de item de menu que usava uma variável local da função construtora gerava erro de carregamento
  (`running coop.lua ...: 1`, nada mais em bridge.log). Mantenha o que uma closure precisa no item ou consulte novamente.
- Sessões: cada novo jogo da tela de título (ou Start at level) cria um id de sessão (1..1295); o evento de salvamento o transporta, para cada cliente
  arquivar seu próprio salvamento na mesma sessão. saves.ini mantém quem jogou (nomes), maior número simultâneo de jogadores, última partida e progresso, por
  sessão, na cópia de cada jogo. A aba Saves do inicializador os lista (cartões: fase-checkpoint, indicador CO-OP n PLAYERS, nomes, anfitrião, idade, barra de progresso),
  escolhe “Continue” para uma sessão que esta cópia hospedou e tem um seletor de fase/checkpoint para novo jogo (a lista de 96 checkpoints do menu de depuração).
  A escolha vai para coop.ini `[start] action=new|resume` e coop_dev.lua a usa uma vez da tela de título.
Derivado: um cliente só pode continuar uma sessão por seu anfitrião (o anfitrião retoma, clientes seguem), portanto sessões de amigos são mostradas, não selecionáveis.
Evidência: tools/qa_launcher.sh 29/29 (página de salvamentos com sessões pré-preenchidas, Continue, novo jogo em 2–3 iniciado sozinho); tools/qa_save.sh com as
verificações de sessão (mesma sessão em cada jogo, todos os jogadores registrados, retomar mantém uma sessão, Start at level cria uma segunda) — veja a execução final no
resumo da sessão. Nomes de fases: desconhecidos (a página mostra apenas números).
Desconhecido: se os arquivos antigos de uma sessão sobrevivem à limpeza de slots de salvamento do próprio jogo (não vi nada no jogo que os exclua); o menu
“Start at level...” dentro do jogo foi apenas construído e controlado de Lua (`coop.BuildStart()`, `coop.StartAt`), não clicado manualmente.

## <a id="2026-10-23-level-captions-and-numbering"></a>2026-10-23: legendas e numeração de fases
Observações:
- `mdk2.str` (em mdk2.tar) contém as legendas da tela de carregamento como texto UTF-16, "<place>, <town>: 9:05AM". Scripts de fase as mostram com
  `HideNextLoadingScreen(strings.l<N>chk1)` (ids 207–209 para fases 1–3, 509–515 para 4–10); não há para 11 e 12, e há uma segunda
  para fase 1 (`l1chk2`, vídeo de introdução). As primeiras dez strings com horário na ordem do arquivo são fases 1–10 em ordem.
- Personagens por fase vêm da única chamada de `CreateKurt/CreateMax/CreateDoctor` em cada script de fase (6 e 12 também CreateHyde):
  Kurt 1,4,7,10; Max 2,5,8,11; Doc 3,6,9,12.
- O inicializador lê as legendas em tempo de execução (nenhum texto é mantido no repositório) e numera checkpoints na ordem de jogo.
Desconhecido: formato do índice .str (não decodificado; strings encontradas por varredura); nomes das fases 11 e 12.
Evidência: tools/qa_launcher.sh 30/30, tools/qa_save.sh 52/52, captura da página de salvamentos na pasta de saída do QA.

## <a id="2026-10-23-skydive-ghosts-face-the-right-way-homing-missile-ghost-cutscene-countdown"></a>2026-10-23: fantasmas de queda livre na direção certa, fantasma de míssil teleguiado, contagem regressiva de cenas
Observações (de um teste manual com duas janelas, depois scripts):
- O fantasma de queda livre estava de cabeça para baixo nos dois jogos. O jogo registra `ktgame_kurt` com orientação inclinada
  (quaternion 0.5228, 0.1249, -0.0978, -0.8376); o fantasma era criado com orientação identidade. Agora copia
  a orientação do próprio Kurt do jogador, lida do gob (nova chamada da ponte `coop_pose(gob)` -> posição + quaternion,
  OMGOB +0x18 / +0x24).
- Cada jogo executa sua própria queda livre: lasers (`ktgame_laser0`, mirando pontos aleatórios) e, a cada quinto disparo, um projétil
  teleguiado (`OBJ_TURSHOT07`, `mdkShootBullet` no seu Kurt, mantido em `kurtgame.lastmis`). A engine move esse projétil, portanto
  seus campos Lua não contêm posição; `coop_pose` a lê. É enviado 8 vezes por segundo (`MV_FALLMIS`) e os outros desenham
  um fantasma inofensivo `ktgame_missl0`, extrapolado pela última direção (no máximo 0.5 s à frente).
- O Lua deste jogo é 3.1: `getn` não existe ("call expression not a function" no início do vídeo, o anfitrião repetia
  o início automático em laço e o cliente permanecia na tela de título).
- Faixa de cena: o voto para pular não tem mais limite de tempo (dura até o vídeo terminar, Backspace o retira);
  a faixa faz contagem regressiva do tempo restante do vídeo. A duração de um vídeo não está em seu script (segue durações
  de animações e temporizadores de diálogo), portanto é aprendida: tempo de reprodução (excluindo esperas e minijogo) quando um vídeo termina
  sem ser pulado, mantido em `coop.ini [movies]` sob level_gobname_stepcount.
Derivado: uma duração aprendida só é tão boa quanto a reprodução completa; um vídeo pulado nunca registra uma.
Desconhecido: durações de todos os vídeos do jogo (a tabela inicial `coop.mvlen` é vazia; uma instalação nova não mostra contagem regressiva
até um vídeo ser assistido até o fim uma vez); se `ktgame_missl0` é o modelo do projétil teleguiado real (é o
modelo de míssil não usado da fase; parece plausível, não comparado lado a lado).
Evidência: tools/qa_cutscene.sh 40/41, depois corrigido o padrão da verificação que falhava (o log tinha a linha, o padrão exigia
fim de linha antes de `\r`), verificado contra o log da execução; MUTANT=upright capturado por “client's ghost Kurt faces like its
own” (produto escalar de orientação 1.000 com a correção); tools/qa_minigames.sh 15/15; captura de queda livre mostra ambos os Kurts na mesma pose.

## <a id="2026-10-23-two-client-crashes-in-movies-level-8-intro-end-of-the-torpedo-minigame-measuring-movie-lengths"></a>2026-10-23: duas falhas de cliente em vídeos (introdução da fase 8, fim do minijogo de torpedo), medição de durações
Observações:
- A introdução da fase 8 (8–8) derrubava o cliente alguns segundos após iniciar, todas as vezes (duas de duas), anfitrião normal. Falha
  em gob_delete (0x449715, escrita em 0xa6 = gob nulo + palavra de flags). O vídeo exclui os coneheads da fase
  pelo nome (`Level.ForAllConeheads(omGobDelete)`, level8.lua); um cliente já removeu suas cópias dos
  inimigos do anfitrião. Correção: coop.lua envolve omGobDelete para pular um gob que coop_alive diz estar ausente (coop.lua carrega antes
  dos scripts de fase, portanto as tabelas de vídeo capturam o wrapper).
- Fim do minijogo de torpedo da fase 2 (vencido pelo próprio tpgame_timer.OnCustomKey do jogo): o cliente falhava
  3 s depois (quando torpgob.OnTimer troca as cenas de volta) em cada execução cooperativa sem proteção (mais de seis); uma vez o anfitrião
  também. Um jogo sozinho não falhava. Não causado pelo fantasma do minijogo (fallspec desativado), fantoche (removido) nem
  chamadas de estase em gobs ausentes (protegidas, nenhuma registrada).
- Local da falha 0x48b00d: memcpy SSE (0x483cb0) além do fim de um bloco de heap, chamado de 0x447bf2 na atualização de
  uma parte de gob de tipo 1 (gob +0x70 -> parte, dword 0 = tipo; despachante 0x448930, tipo 1 -> 0x447ab0). Essa parte é
  um emissor de partículas: realloc (0x473550) de um array de entradas de 32 bytes em +0x7c, máximo +0x0c (limitado a 256), e um
  memmove de [+0x34] * 32 bytes. No cliente, `ml2b_cameragob` (câmera de vídeo da fase 2) tem um emissor cujo
  +0x34 é -15 desde o carregamento da fase (o do anfitrião é 0), portanto o tamanho da movimentação é cerca de 4 GB.
- O jogo escreve -15 novamente a cada quadro enquanto essa câmera é mantida. A ponte agora redefine um +0x34 negativo antes de
  cada atualização de cena (frame.c, fix_emitters; `coop_emitter_guard(0)` o desativa): o cliente sobrevive (duas de duas).
- Código lido da memória de um jogo em execução (ReadProcessMemory, 0x400000..0x4e0000): o executável no disco é empacotado.
- tools/qa_launcher.sh deixou `player.ini` com id 0a0b0c0d nas cópias de laboratório que usou; um cliente compartilhando id com
  um jogador anterior recebeu jogador 3 em vez de 2, e o teste de cenas falhou por isso. Agora restaura os arquivos.
Derivado: +0x34 é um índice no anel de partículas desse emissor (outros escritores em 0x447802 / 0x44845c o definem
a partir de um índice corrente), não uma contagem simples.
Desconhecido: por que o emissor da câmera do cliente recebe -15 (apenas no cliente, já no carregamento); se as fases 5 e 9
encontram a mesma falha (qa_minigames agora verifica as três).
Medição de vídeos: tools/measure_movies.sh inicia dois jogos em cada checkpoint de vídeo (os ramos cp == N do
Level.Init dos scripts de fase) e vence minijogos pelos mesmos hooks; durações se repetem dentro de 0.2 s entre execuções.
Nomes de vídeos: nome do gob em reprodução, contagem de etapas e soma de seus ids de animação e esperas; a fase não está incluída
(um vídeo de carregamento de fase começa antes de coop.level ser definido, portanto continha a fase anterior).
Resultados (mais tarde no mesmo dia):
- 31 vídeos medidos (cada checkpoint de vídeo de Level.Init e tudo a que suas cadeias de Done levaram, créditos 329 s); a tabela é
  coop.mvlen em lua/coop_dev.lua (a maior medição de cada). O mesmo vídeo medido duas vezes difere em 0.2 s ou menos,
  exceto o vídeo de chefe compartilhado boss.lua (75.5 / 77.0 / 77.5 s nas fases 10, 11, 12).
- Vídeos de gatilho (coop.moviehooks: cenas de sala, vídeos de morte, ponte, KillZizzy): chamar a função em cada checkpoint de
  jogo não reproduziu nenhum em 45 minutos (l1_r6 iniciou em 1–1 e não terminou em 10 minutos; l3_bathroom03 em nenhum).
  Recebem contagem regressiva quando um jogo assiste um até o fim (aprendida, coop.ini [movies]).
- Proteção de falha do minijogo de torpedo: tools/qa_minigames.sh 24/24 (os três minijogos vencidos, ambos os jogos continuam vivos);
  MUTANT=noguard (coop.ini [test] emitter_guard=0 desde o início) falha apenas na fase 2. Desativar a proteção após
  carregar a fase não causa falha: o índice incorreto aparece durante o carregamento e já foi reparado nesse momento.
- Introdução da fase 8: tools/qa_level8_intro.sh 6/6; MUTANT=gonegob derruba o cliente. Excluir um gob novo duas vezes não
  causa falha, portanto não era um teste disso.
- O anfitrião mantém o slot de cada id de jogador ([slots] em player.ini) e dá a um novo id um slot que ninguém teve: cópias de laboratório que
  hospedaram execuções anteriores faziam seu cliente jogador 3, 4, ... e testes que esperavam jogador 2 falhavam. tools/install.sh agora
  remove [slots] / [steam_slots] das cópias que prepara.
- Duas instalações ao mesmo tempo podem colidir em settings.lua compartilhado (`sed: cannot rename ... Permission denied`).
Evidência: tools/qa_cutscene.sh 42/42 com a tabela (faixa "Cutscene 1:27 | Skip cutscene: 1 of 2 (Backspace)" na
primeira exibição do vídeo da sala de estar); saída da medição em local/movies/.

## <a id="2026-10-23-every-option-in-the-launcher-an-interface-page-the-skip-key-as-an-action-the-missile-ghosts-nose"></a>2026-10-23: todas as opções no inicializador, página Interface, tecla de pular como ação, nariz do fantasma de míssil
Observações:
- mdkGobPointToXYZ(g, dx, dy, dz) recebe uma direção (não um ponto) e vira o +y do modelo nessa direção: para
  (0, 0, 10), forneceu quaternion (0.707, 0.707, 0, 0). O modelo do míssil da queda livre (ktgame_missl0) tem seu
  nariz em +z, portanto um fantasma virado assim voava de lado. Três mísseis de teste parados (sem rotação; +x; +y,
  captura) mostraram isso: o não girado é um ponto visto de cima, nariz para cima. O fantasma agora recebe a rotação
  de +z para sua direção, escrita com uma nova chamada da ponte (coop_set_quat; o setter da engine copia o
  quaternion em gob +0x24 do mesmo modo).
- O jogo não tem volume geral: três níveis em settings.lua (chSndSetEffectsVolume, chSndMusicVolume,
  chSndSetVoiceVolume, 0..1, padrão 0.25), e o jogo os salva do próprio estado, portanto escalá-los em
  Lua acumularia o efeito em cada salvamento. O inicializador edita essas três linhas (passos de 10%).
- "sed: cannot rename ... Permission denied" quando instalações executavam junto a jogos iniciando: o lock de inject.sh só
  serializa instalações; um jogo iniciando mantém settings.lua aberto e Windows recusa renomear. Uma cópia
  que falhou ali manteve seu coop.lua antigo e falhou em testes de código que não tinha. inject.sh agora tenta novamente.
- O anfitrião do teste de cenas morreu uma vez na queda livre (um laser), o que inicia a câmera de morte como novos vídeos e
  quebrou as verificações de fim da queda; o teste agora substitui a atualização de mísseis do jogo por uma que nunca acerta.
Derivado: uma opção [features] que retira as teclas de uma ação (coop.BindAction) não precisa de mudança na ponte.
Evidência: qa_launcher 32/32 (opção Interface e nível de música escritos), qa_menu 38/38 (captura da página
Interface), qa_emote 21/21 (MUTANT=nofeat capturado), qa_cutscene 48/48 (opções de caixa de cena, temporizador e fantasma,
nariz do míssil; MUTANT=sideways capturado), qa_controls 40/40 (Skip cutscene na página Co-op).

## <a id="2026-10-23-esc-skipped-a-co-op-cutscene-for-one-player-character-collision-distance"></a>2026-10-23: Esc pulava uma cena cooperativa para um jogador; distância de colisão de personagens
Observações:
- Em uma sessão manual, o quadrinho de abertura de 112 s terminou após 3 a 10 s sem voto de pular registrado. Uma varredura de teclas
  (W, E, F, Tab, Enter, Espaço, 0, 0 numérico, ambos os botões do mouse, Esc, Backspace, uma por vez no cliente,
  StopScript envolvido para registrar) mostrou Esc: a engine trata COM_PAUSE por conta própria (sem entrada comfuncs) e durante um
  vídeo chama StopScript(Save.movietocancel). O executor de scripts também chama StopScript quando um script passa de
  sua última etapa, portanto o wrapper só transforma uma parada no meio do vídeo cooperativo, a até 1 s de um pressionamento de tecla,
  em voto de pular.
- Colisão de personagens: com o fantoche do parceiro mantido a d unidades do anfitrião parado em 1–1 (movendo o anfitrião
  para lá a cada vez), d >= 1 não moveu nada; d <= 0.75 moveu o anfitrião até ficar a 0.88 de distância, suavemente. O fantoche era
  mantido a 3, o que os jogadores viam como o parceiro deslizando para longe. Agora 1. Um anfitrião apenas parado junto a um fantoche mantido
  a 0.5 não era movido, portanto apenas entrar em uma sobreposição aciona o empurrão.
- A queda livre termina sozinha quando a animação de ktgame_timer chega à chave personalizada: um teste que espera deve
  reter isso.
Evidência: qa_cutscene 49/49 (MUTANT=escskip capturado), qa.sh 52/52 (MUTANT=overlap e magnet capturados pelas
verificações “partner right beside”).

## <a id="2026-10-23-a-hero-stuck-in-a-wall-after-a-switch-emote-wheels-per-hero"></a>2026-10-23: herói preso em parede após troca; rodas de emotes por herói
Observações:
- Doc andou até a parede à esquerda do início de 1–1 (x -39), depois a troca para Kurt colocou Kurt no lugar de Doc: Kurt não conseguia
  se mover em direção alguma. Colocado a 0.2 ou mais da parede, movia-se. Kurt (e Max) são mais largos que Doc.
- Tentativas como teste de um lugar: mdkAILineOfSight entre jogador e personagem de sondagem (informava livre mesmo 2 unidades
  dentro da parede, e diferia por direção: orientação, não paredes); soltar o herói de 0.4 acima do lugar (um herói preso
  ainda cai). Nenhum identifica um lugar preso. Voltar 0.5 pelo caminho recente não ajudou quando Doc havia deslizado
  ao longo da parede (a 0.17). O que funciona: após trocar, enquanto uma tecla de movimento está pressionada e o herói não se moveu, tentar
  os lugares ao redor em sequência (8 direções, 0.3 depois 0.6); o primeiro funcionou aqui.
- Animações que cada herói tem (om_anim_state no jogador, ids 0–159): Kurt 61, Max 61, Doc 70. Max não tem THROW (57),
  Doc não tem ACTION05 (82): os slots da roda compartilhada registravam "does not exist for this character".
Evidência: qa_char 12/12 (MUTANT=nounstick capturado), qa_emote 25/25.

## <a id="2026-10-23-regression-takeover-private-configuration-and-bounded-qa-lanes"></a>2026-10-23: retomada da regressão, configuração privada e vias limitadas de QA

Observações:
- A sequência full herdada e sequencial concluiu 31 etapas: 28 passaram. Controls falhou em
  22 verificações, a etapa de projéteis com perdas falhou em uma verificação de movimento, e fixtures de
  campanha 3–10 e 3–11 informaram erros aritméticos Lua do cliente. Evidência:
  `local/regression/20261023-163734-876744`, varredura `local/sweeps/20261023-171411-x4`.
- A captura de controles mostra Interface onde o teste esperava Controls: adicionar
  Interface deslocou a navegação em um item. A escrita de PID do reinício também ficou
  acidentalmente dentro de um comentário shell. Ambos os defeitos de teste foram corrigidos.
- O primeiro snapshot do cliente 3 de projétil com perdas continha uma granada ativa com
  velocidade; o segundo não continha granada. O teste falhou porque
  exige duas posições, não porque as posições capturadas eram idênticas.
- Cinco testes de executor baseados em subprocessos verificam sobreposição real de suítes, barreiras de
  etapas exclusivas, reversão de alocação ocupada, limpeza de alocação malformada, rejeição de recursos
  conflitantes e cancelamento. Os 31 testes Python passaram após integração.
- Instruções da estação de trabalho e comandos de alocação foram movidos para configuração
  privada ignorada. Ferramentas públicas usam variáveis de ambiente documentadas e uma interface
  opcional de recursos por comando/JSON; nenhum alocador local específico é exigido.

Fatos derivados:
- Um caminho antecipado de GO de vídeo define o estado como reprodução sem inicializar tick_at, enquanto
  MovieTick subtrai tick_at do relógio. Os logs de campanha afetados mostram a
  mensagem de GO antecipado imediatamente antes dos erros aritméticos. É um forte candidato
  para as falhas da campanha; um reprodutor/correção direcionado ainda está pendente.

Desconhecido:
- Se a verificação de movimento de projétil com perdas está amostrando consistentemente tarde demais.
- Paridade e duração completas da nova sequência de três vias; validação está executando.

Observações de acompanhamento:
- A sequência full de três vias passou 30/31 etapas, incluindo os 96 checkpoints, em
  cerca de 21 minutos. A única falha foi character-motion: sondas de fases posteriores tinham
  apenas 11–17 quadros em uma amostra de um segundo (o oráculo exige 20), e um salto
  foi perdido. A evidência sequencial de referência havia passado. Character-motion agora é uma
  etapa exclusiva; nenhuma asserção de movimento foi reduzida.
- Uma seleção posterior de três vias passou character-motion (44 verificações, 74 s),
  HUD, projéteis nativos e projéteis nativos com perdas. Movimento executou sozinho antes
  de as outras três se sobreporem. As duas variantes de projéteis começaram no mesmo
  segundo e produziram diretórios distintos de evidências após adicionar sufixos de PID.
- Snapshots de projéteis nativos agora são capturados como um par próximo por cliente, com
  clientes amostrados simultaneamente, para as idas e voltas de shell de outro cliente não
  consumirem a vida da granada antes do segundo snapshot. As mesmas asserções de projétil
  ativo, estrangeiro e mudança de posição permanecem.
Evidência: `local/regression/20261023-171852-379664` (full),
`local/regression/20261023-174024-204153` (movimento exclusivo mais variantes simultâneas
de projéteis).

Validação determinística da condição de corrida de vídeo:
- Receber MV_GO antes de MovieStarted antes entrava em reprodução com tick_at nil,
  produzindo os mesmos erros aritméticos das fixtures anteriores de campanha. O
  ramo agora chama o inicializador comum MovieGo. A verificação focada com dois jogos
  observa relógio decorrido positivo, conclusão normal e nenhum erro Lua.
- O mutante earlygo restaura o ramo original e é capturado pela asserção de
  relógio, com os erros aritméticos também observados. Uma asserção inicial de teste
  acidentalmente correspondia ao fonte do comando ecoado; ancorá-la no prefixo real de
  log `lua:` corrigiu o falso positivo antes de aceitar o resultado do mutante.
Evidência: `local/regression/movie-clock-20261023-174546` (positivo 4/4; o mutante
deve falhar nas verificações de relógio e ausência de erros, e o harness negativo informa captura).

Observação de varredura com recursos novos:
- Uma execução apenas de campanha com pasta auxiliar recém-criada encontrou erros concorrentes de criação
  de arquivos NTFS enquanto partições copiavam scripts PowerShell. A falha de instalação foi então
  ignorada e a varredura iniciou configuração antiga. A execução inválida foi cancelada;
  todos os oito jogos próprios e a reserva foram liberados.
- A cópia de auxiliares agora usa um lock curto, e uma instalação malsucedida para uma partição antes
  de iniciar. Um reprodutor de concorrência com shell real falha antes do lock e passa depois;
  outro teste shell verifica que uma instalação malsucedida nunca inicia um jogo. Os 33
  testes Python passam. Um novo reteste de campanha com pasta nova está executando.
Evidência da execução inválida: `local/regression/20261023-174743-655439`.

Validação final com pasta nova:
- O perfil campaign passou as sete etapas, incluindo os 96 checkpoints após
  as correções de relógio de vídeo e instalação de auxiliares. Os 16 slots de recursos ficaram livres após
  a limpeza. A execução final de 33 testes Python, sintaxe shell, verificações de destinos Markdown e
  auditoria de estação de trabalho nos arquivos rastreados passam.
Evidência: `local/regression/20261023-175357-180407`,
`local/sweeps/20261023-175423-761414-x4`.

## <a id="2026-10-23-separate-private-workstation-configuration-from-public-requirements"></a>2026-10-23: separar configuração privada da estação de trabalho de requisitos públicos

Observações:
- Instruções da estação de trabalho, integração de ambiente, adaptador de alocação e histórico privado
  de passagem de trabalho agora ficam em um espaço de trabalho privado separado. Links ignorados mantêm os
  pontos de entrada genéricos de configuração do checkout existente funcionando. Um auxiliar de configuração que só opera no sistema de arquivos
  conecta novos worktrees e recusa sobrescrever configuração diferente.
- Os guias públicos mantêm configuração genérica, protocolo de alocador e dependências de
  executáveis. Prosa desnecessária de configuração específica da estação de trabalho foi removida.
- Validação: os 33 testes Python do repositório e três testes privados de configuração passam;
  mapeamento de ambiente, permissões de adaptador, links simbólicos, sintaxe shell, destinos Markdown
  e verificações de espaços em branco passam. Nenhum teste de jogo foi executado para essa mudança de configuração.

## <a id="2026-10-23-full-ladder-before-the-public-alpha-a-hero-stuck-when-the-player-waits"></a>2026-10-23: sequência full antes do alpha público, herói preso quando o jogador espera

Observações:
- Sequência full com três vias e quatro partições de campanha na candidata a lançamento: 30 de 31 etapas passaram, a
  campanha (96 checkpoints) em 240 s. Controls e character-motion, que falharam em execuções anteriores, passaram.
- character-wheel falhou em uma verificação: após trocar de Doc para Kurt na parede em 1–1, Kurt não se moveu
  (-39.09 124.64 antes e depois de W, S e D). Nas duas execuções full anteriores, moveu cerca de 10 unidades, e o jogo
  registrou `character: unstuck at spot 1`; desta vez essa linha está ausente.
- O tempo limite para destravar (4 s) começava na troca. O teste trocava, esperava 3 s, lia a posição por uma
  ida e volta de comando, depois pressionava teclas; com as outras vias executando, as teclas chegavam após o limite.

Fatos derivados:
- Um jogador que troca de herói em uma parede e espera mais de 4 s antes de andar permanece preso. Correção: o limite começa
  na primeira tecla de movimento mantida. O teste agora espera 6 s após trocar, além do limite antigo.

Evidência:
- Código corrigido: etapa character-wheel 12/12, Kurt -39.09 124.64 -> -29.42 126.11. `MUTANT=nounstick`: capturado. O
  código anterior com o novo teste: a verificação de parede falha. Commit 75998a7 do mod, lançado como v0.2.0-alpha.
