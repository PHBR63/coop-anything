# <a id="the-lord-of-the-rings-the-two-towers-2002-xbox-co-op-notes"></a>The Lord of the Rings: The Two Towers (2002, Xbox): notas sobre cooperativo

As descobertas e evidências por trás do cooperativo local em The Two Towers Recompiled (código:
[Volverine-Dude/TooTawersRecomp-coop](https://github.com/Volverine-Dude/TooTawersRecomp-coop), consulte seu `COOP.md`). Dois
jogadores em um PC, uma câmera compartilhada, um processo do jogo: sem rede, portanto sem dessincronização.

- Cada endereço é um endereço virtual de Xbox no `Default.xbe` comercial dos EUA (identidade abaixo).
- **Observado**: visto em tempo de execução (logs, dumps de quadros, execuções de bots). **Derivado**: lido do código, não verificado em tempo de
  execução. **Desconhecido**: não encontrado.
- As execuções de bots controlam os heróis com controles programados, bots de teste com direcionamento ou o P2 Bot, e montam situações com
  as opções de teste `TT_COOP_*`. A suíte que repete as verificações principais está em `tools/coop-bot/` do fork.

## <a id="1-identity"></a>1. Identidade

| | |
|---|---|
| Jogo | The Lord of the Rings: The Two Towers, Xbox original, 2002 (EA / Stormfront Studios) |
| Mídia | Disco dos EUA, extraído (`<game dir>\game_files`) |
| Certificado XBE | title ID `0x45410010`, "The Two Towers(tm)", região `0x1` (América do Norte), versão 1 |
| `Default.xbe` | SHA-256 `ae2d1b5304b3e9572339b693a6a45ad0869bdaeec89aae374b5c14feebbb8d30`, 2.224.128 bytes (o hash exigido pelo `generate.py` do port) |
| Port para PC | The Two Towers Recompiled 1.9.4 (xboxrecomp 0.12.0); trabalho iniciado em 1.9.2 |
| Renderizador testado | Direct3D 11, 16:9 (Vulkan e 4:3 não testados) |
| Sistema anfitrião | Windows |

Engine (observada nas strings do XBE): “Fusion” da Stormfront (`C:\Fusion\xbox\Game\Burn\FusionXbox.exe`), XDK
4928, Bink, XACT. Lua 4.0 está vinculado (`$Lua: Lua 4.0 ...`), mas nenhuma fase inclui Lua: 0 assinaturas de bytecode Lua 4.0
(`1B 4C 75 61 40`) e nenhum fonte Lua nos 4.3 GB de arquivos do jogo, cujos arquivos compactadores não usam compressão
(entropia 5.4–5.6 bits/byte). As fases usam scripts na linguagem de comandos própria da Stormfront (4.1).

## <a id="2-prior-work"></a>2. Trabalhos anteriores

- Nenhum mod, patch ou hack cooperativo para este jogo: diretório Co-op Anything e buscas na web ("Two Towers 2002 co-op
  mod two player PC port", "Two Towers Xbox 2 player coop hack/mod/player 2"), 2026-10-17. ModDB, Nexus, Reddit e
  os Discords dos ports: não verificados.
- O jogo não tem multijogador nem código de rede. Return of the King tem cooperativo para 2 jogadores, em outra engine (a própria
  `EAThirdPerson` da EA, segundo `docs/ROTK-ENGINE-NOTES.md` do Athelas): apenas uma referência de design.
- Dois ports para PC, nenhum com cooperativo:
  - [The Two Towers Recompiled](https://github.com/Gumpolas/TooTawersRecomp): recompilação estática com
    [xboxrecomp](https://github.com/sp00nznet/xboxrecomp). MIT para seu próprio código; xboxrecomp MIT mais partes LGPL-2.1
    do xemu. O repositório não tem código do jogo: `generate.py` traduz o `Default.xbe` do próprio jogador.
  - [Athelas](https://github.com/Shagg88/Athelas): outro recompilador (XboxXBE-Recomp), MIT. Seu harness de testes Linux sem interface
    (renderizador por CPU, controles programados) é um bom modelo para testes com bots.
- Construído sobre The Two Towers Recompiled: seu C escrito à mão fica sobre o código gerado, já filtra cada leitura de
  controle (`xbox_pad_filter`), e seu `heroes.c` (o mod Extra Heroes) já reconstrói uma fase com modelo,
  animações e textura de outro herói.

## <a id="3-building-the-port"></a>3. Compilação do port

- `generate.py` precisa de **capstone**, embora o README do port diga “no extra packages” (observado:
  `ModuleNotFoundError: No module named 'capstone'` em `tools.disasm`). Um venv com `capstone==5.0.9` (instalado com
  `--require-hashes --only-binary=:all:`) funciona. Vale relatar ao upstream.
- Ferramentas usadas: clang 22.1.8 (estilo llvm-mingw, `x86_64-w64-windows-gnu`), CMake 3.31, Ninja 1.13, Python 3.15.
  `generate.py`: 8.6 minutos, "8718/8724 functions (0 failed)", 27 destinos de chamada não resolvidos substituídos por stubs. Compilação: 52 s.
- Nossa build difere da versão publicada no hash (publicada: clang 23.1.2 com msvcrt; nossa: clang 22.1.8 com UCRT),
  com as mesmas seções, importações, strings e comportamento em uma execução de teste básico.
- Hooks: um `sub_X` escrito à mão substitui uma função gerada, que é renomeada para `sub_X_gen` e pode ser chamada. Um novo
  `sub_X` exige executar `generate.py` novamente (cerca de 9 minutos). O `manual_scan.py` do xboxrecomp só aceita declarações em
  sua própria linha (`^extern void sub_X_gen(void);`): uma que vem após um `}` na mesma linha não é vista, e a compilação falha
  com símbolos duplicados.
- De 1.9.2 para 1.9.4: o upstream mudou 26 arquivos; o cooperativo altera 9 deles (`e3hud.c`, `heroes.c`, `menus.c`,
  `options.c`, `twotowers_manual.c`, `kernel_bridge.c`, `nv2a_d3d11.inc`, `nv2a_gl.inc`, `nv2a_pb_exec.c`). Um merge de três vias
  foi limpo em 7, com conflitos de um trecho em 2 (“Options just opened” de options.c agora conta quadros;
  includes de twotowers_manual.c, onde `tt_env.h` de 1.9.4 armazena `getenv` em cache por nome).

## <a id="4-how-the-game-works"></a>4. Como o jogo funciona

### <a id="41-level-scripts"></a>4.1 Scripts de fase

- Uma tabela de 500 comandos, registros de 40 bytes `{char name[36]; u32 handler}` a partir de `@TEST_SCREEN` (0x173EE3).
- Tratadores são cdecl `(vm)`: 0xB4520 verifica a contagem de argumentos, 0xB4590 o tipo de um argumento (2 número, 3 objeto),
  0x9F2A0 lê um número, 0x9F2E0 um id de objeto, **0xB4690 transforma um id em ator**, 0x9F350 / 0x9F380 empilham um
  resultado. A busca de objetos de cada tratador passa por 0xB4690, o que o torna o local para responder a um script com os objetos do jogador
  2.
- 31 comandos são `return 0` na versão comercial (0xD3BA0), entre eles `@CameraGoto`, `@CameraSetMode`, `@CameraSetTarget`,
  `@CameraSnapTo` e `@InitHealth`: a câmera existe apenas em código nativo.
- **Scripts endereçam atores pelo nome.** O handle de script de um ator `+0x18` é seu registro de posicionamento + 8, o nome.
  - O herói é configurado pelo nome no início da fase (observado com um hook em 0xB4690): `@SetAnimMachine`,
    `@SetBrainMachine`, `@AttachToBone` x3, `@SetEnemyID`, `@PassBrain`, `@StartPlayerWeaponPfx`, `@UnlockHeading`,
    `@OnComboBreak`, `@PlayerLargeMass`, `@ObjectCollisionOn`, `@SetAlpha`.
  - Cada arma tem seu próprio script de configuração: `@Activate`, `@SetRenderable`, `@SetWeaponID`, `@Deactivate`,
    `@ObjectCollisionOff`.
  - A verificação de morte (`@ObjectDie`) e os scripts de cérebro dos inimigos (`@IsPlayer`, `@ObjGetPosition`, `@Probe`) nomeiam o
    herói. Uma execução com quatro Ringwraiths mirando no jogador 2: `@IsPlayer` 1174 buscas, `@ObjGetPosition` 623 (12 no
    jogador 2), `@Probe` 553, todas no jogador 1.

| Comando | Tratador | Notas |
|---|---|---|
| `@GetPlayer` | 0xAF610 | `[0x43B15C]+0x18` |
| `@IsPlayer` | 0xA6850 | actor == `[0x43B15C]` |
| `@SetPlayerControl(b)` | 0xA6B50 | o byte 0x43B1C0 (um só, não por jogador) |
| `@EndMission(n)` | 0xA6370 | `[0x8D2484]->0xF1230(code)`; n 0–4 gera código 0, 1, 2, 5, 6 |
| `@NoDie(actor, b)` | 0xAE5D0 | bit 0x4 de `+0x110` (derivado) |
| `@AllowHeroCam` / `@AllowDeathCam` | 0xA3D90 / 0xA3DE0 | câmera `+0x18A` / `+0x18B` |
| `@PassBrain(actor, n)` | 0xA50F0 | 0xC6150 do gerenciador de atores (4.6) |
| `@ObjectDie` | 0xAB200 | método de morrer do herói (4.8) |
| `@SetRespawnId` | 0xB0FB0 | o checkpoint (4.10) |
| `@KilledByPlayer` | (chama 0x99D40) | a recompensa por abate (4.9) |
| `@ChangeTarget` | 0xA1CA0 | pede uma nova escolha: componente `+0x23C` = 1, `+0x128` = -1.0 |
| `@FollowPlayer` | 0xA5A20 | fornece à IA de um companheiro seu líder (0x54C00 com `[0x43B15C]`) |
| `@PlaySound` / `@SetSfxVolume` | 0xB3760 / 0xB3450 | 4.15 |
| `@TeleportToStartPoint`, `@TeleportPlayerTo` | 0xAC710, 0xAF840 | sem hooks |

### <a id="42-the-player-and-the-characters"></a>4.2 O jogador e os personagens

**“O jogador” é um conjunto de globais** (observado):

| Endereço | Significado |
|---|---|
| `[0x43B15C]` | o personagem do jogador (mais de 270 usos no código gerado comparam com ele) |
| `[0x43B160]` | seu componente (`+0x494`) |
| `[0x43B164]` | o objeto de câmera |
| `0x43B1C0` | byte “controle tomado”: 1 enquanto a fase imobiliza o jogador (aproximadamente os primeiros 4 s de Weathertop) |
| `[0x1CB8B4]` | a porta do controle que o jogo lê como a do jogador |
| `0x8D2484` | o gerenciador de missão; 0xF1230(code) armazena o estado de término pendente em `+0x4808` |
| `[0x4AB69D]` | o byte do herói atual (1 Aragorn, 2 Legolas, 3 Gimli, 4 Isildur) |

O estado por jogador escrito pela etapa de controle e por suas funções chamadas (trocado para o jogador 2): `0x43B114` (0x48 bytes),
`0x43B168` (0x58), `0x43B1C1` (0x5F), `0x43B298` (0xF8), `0x43B3A4` (0x10), `0x1B0C40` (0x20), `0x1B1080` (0x24),
mais o registro do herói atual (0x348 bytes, 4.9).

**Personagens** são uma classe, vtable 0x1741C0: heróis, companheiros, inimigos, o Watcher e seus tentáculos. Construídos
com `0xE6B50(0x540)` e o construtor 0x82C10.

| Campo | Significado |
|---|---|
| `+0x18` | handle de script (registro de posicionamento + 8: o nome) |
| `+0xF0..+0xF8` | posição (`+0x90` e `+0x130`, `+0x140` contêm mais cópias) |
| `+0x110` | flags: 0x4 não morrer, 0x2000 ativo, 0x20 (limpo durante a morte) |
| `+0x114` | papel: 1 jogador, 2 companheiro, 3 inimigo |
| `+0x2EC` | seu índice no mapa de caminhos (-1: nenhum) |
| `+0x2F0` | tipo de personagem: define vida, munição e seu máximo (0x8C850). Aragorn 0 (30 flechas), Legolas 7 (60), Gimli 8 (25 machados) |
| `+0x2FC`, `+0x300` | vida (int32), vida máxima |
| `+0x304`, `+0x306` | munição (16 bits), seu máximo |
| `+0x3D8` | sua máquina de estados: `+0x408` o estado, `+0x420` o tempo do estado em segundos |
| `+0x3D0` | lista de ouvintes de sua fonte de eventos (as armas de um herói estão nela) |
| `+0x464`, `+0x465` | flags de bloqueio que a fase define no jogador |
| `+0x466` | em uma janela de acerto (definida por um evento de animação de tipo 4) |
| `+0x494` | componente: `+0` flags (0x8000 controlado por jogador, 0x10000), `+0x20` cérebro, `+0x50` objeto da máquina de cérebro, `+0x98` alvo, `+0xA0..+0xB0` detalhes de mira, `+0x148` ponderação de alvo |
| `+0x49C` | flags: 0x100 caminho de acerto do jogador, 0x40 definido durante a morte (nenhum golpe o alcança), 0x400 (um tentáculo) atacando |
| `+0x4BC` | seu último atacante |

Métodos (slots da vtable): 1 = 0x843F0, **o que move um personagem** (sua locomoção; a etapa de controle apenas prepara as
coisas); 21 = 0x85340, tratador de mensagens; 36 = 0x838E0, morrer; 42 = 0x84220, receber um golpe; 43 = 0x86B30, aplicar os
atributos do personagem (vida máxima).

**Armas** são objetos posicionados, classe 0x174980: dono `+0x11C`, id da arma `+0x2F4` (seleciona os dados da arma e
o alcance da sua caixa de ataque). Ids (observados): espada de Aragorn 0x01 e adaga 0x1D, facas de Legolas 0x1F e adaga 0x1D,
machado de Gimli 0x17, modelo de arco 0834F2D4 0x27; os de Isildur desconhecidos. `@AttachToBone(parent, bone, child)` chama a
vtable do pai `+0xC4(child, slot)`.

| Herói | Slot 0 | Slot 1 | Slot 2 | Slot 3 |
|---|---|---|---|---|
| Aragorn | espada 13F82514 / 29636120 | - | - | adaga 69DAC4B8 / BD9E230B |
| Legolas | faca EF8EBCEC / 9126E92A | faca EF8EBCEC / 9126E92A | adaga 69DAC4B8 / BD9E230B | - |
| Gimli | machado 2B9252D0 / AB926BE7 | - | - | - |
| Isildur | espada 13F82514 / 29636120 | - | - | adaga 69DAC4B8 / BD9E230B |

(chaves de modelo / textura, observadas com `TT_COOP_WLOG` em Balin's Tomb.) A arma de longo alcance é outro objeto, obtido
ao mirar (4.13).

### <a id="43-how-a-level-makes-the-player"></a>4.3 Como uma fase cria o jogador

- **O jogador é um ator posicionado.** O carregador de fase 0xF5E50 percorre os atores posicionados; o primeiro com papel 1 se torna
  o jogador: `+0x49C = (+0x49C & ~6) | 1`, slot 0 da vtable, depois **SetPlayer 0x99000** (`[0x43B15C]`, `[0x43B160]`,
  bit 0x8000 no componente, a câmera anexada com 0x68750, o estado do jogador reiniciado). Cada ator é então
  registrado no gerenciador em 0x43C5E8 (0xC5E20).
- Objetos são feitos de **registros de posicionamento** por 0xF5BC0 (um switch no tipo do registro; depois 0x19880(obj, type)
  o vincula). Personagens por 0xF3430 (thiscall world 0x4B0EF0, record, key; `ret 8`).
- Um registro (observado): `+0` tipo (1 herói, 0x16 arma, 0xB ...), `+4` tamanho do nome, `+8` nome, `+0x28` chave (o
  hash do nome), `+0x2C` posição; registros ficam a 0x64 bytes de distância. Um registro de herói tem suas chaves de malha, conjunto de animações e textura
  em `+0x44`, `+0x48`, `+0x4C`; modelo e textura de uma arma em `+0x40`, `+0x50`.
- **O heap de atores (0xE6B50) só fornece memória durante o carregamento da fase.** Durante o jogo, retorna 0 (observado), portanto nada
  pode ser construído durante o jogo: nenhum segundo herói, nenhuma cópia de arma, nenhum inimigo extra.
- O índice da fase é `[0x1BB2A4]` (0xD1C00 o define, 0xD1BF0 o lê; tabela em 0x17B7A4): 0 00ISUL1 (o prólogo),
  1 01WEAT1, 2 02GATE2, 3 04BALIN1, 4 13AMON1, 5 14FANG2, 6 16ROHAN2, 7 16ROHAN1, 8 16ROHAN3, 9 17TOP1, 10 18HOLE1,
  11 20YARD1, 12 21ORTH1, 13 21ORTH2.
- Arquivos de fase por herói: `.bfa` Aragorn, `.bfl` Legolas, `.bfg` Gimli, `.bfi` Isildur. Cada um contém os registros de armas de
  todos os heróis. Chaves de heróis (iguais em todas as fases):

| Herói | Malha | Animações | Textura |
|---|---|---|---|
| Aragorn | E9B808FE | DE94124A | 66829AC2 |
| Legolas | 9EDC669E | EE4A9EBA | 58C546AD |
| Gimli | 71EB3C66 | AAE0DF66 | F35ADE70 |
| Isildur | 37EA8A4E | 53DFD442 | CD25E3B2 |

- O que é carregado é nomeado por listas de recursos (pares `{index, key}`) em recursos de tipo 500 (pacotes). Weathertop tem 6
  pacotes, Balin's Tomb 2; **0E01E39C é o pacote do jogador**, os outros são os das cenas da fase.

### <a id="44-input"></a>4.4 Entrada

- **O jogo vê um controle.** O USB emulado do xboxrecomp (`src/usb/ohci.c`) tem um dispositivo de gamepad, e
  `usb_gamepad_report()` lê apenas a porta 0 do anfitrião. Um segundo controle do PC nunca chega ao jogo.
- O jogo consulta os controles em **`0x6B2758 + 0x14C * port`** (0xE7DB0; nada fora do módulo de entrada
  0xE7D30–0xE8B70 o lê, exceto 0xD12C0), e cada consulta o indexa com `[0x1CB8B4]`:

| Offset | Conteúdo |
|---|---|
| `+0x00..+0x11` | XINPUT_GAMEPAD bruto: botões (u16), 8 botões analógicos, LX LY RX RY (s16) |
| `+0x14..+0x20` | analógicos como floats, com zona morta aplicada |
| `+0x34` | máscara de pressionados (botões digitais, botões analógicos acima de um limite no bit 8+i, direções dos analógicos) |
| `+0x24` / `+0x28` | máscara do quadro anterior / liberados neste quadro |
| `+0x2C`, `+0x30` | latches |
| `+0x144` | handle de dispositivo (um registro com 0 é pulado); `+0x148`, `+0x149` flags de inserção / remoção |
| `+0xE4` | solicitação de vibração |

- XInputGetState é 0x1697D9 (stdcall handle, XINPUT_STATE*; `ret 8`).
- Em um PC com um controle, seu handle estava no registro da porta 2, e com a rota de teste (início de fase `TT_TWEAKS`)
  `[0x1CB8B4]` não está definido ("primary 4294967295"), portanto o jogo lê todos os controles para o jogador 1.
- Controles (observados): **X sozinho nunca cria uma caixa de ataque, nem para o jogador 1**; Y cria. Para disparar, segure LT e pressione
  A (ou Y); LT sozinho apenas prepara a arma. White bloqueia.

### <a id="45-a-frame"></a>4.5 Um quadro

- 0xF2FF0, a atualização do mundo (de 0x7C340), executa ... 0x9E1D0, **0x9C380 a etapa de controle do jogador**, depois **a
  atualização da câmera 0x68DC0** (thiscall camera), 0x89220, 0xD43E0, as atualizações dos atores, depois `[0x43B160]->0x54E70` (o
  componente do jogador).
- **0x9C380** (cdecl; seu argumento é o tempo do quadro, 0.013–0.057 s; o jogo mantém uma cópia em 0x1B0C54) lê
  `0x43B1C0`, `[0x43B15C]`, a câmera (analógicos relativos à câmera) e o controle, e escreve os blocos de estado acima. Também
  chama a atualização da câmera duas vezes (0x9C8BF, 0x9CA35).
- 0x5A450 (uma vez por quadro, centrado no jogador) organiza os personagens em listas de engajamento, e 0x5A920 (de 0x5AAC0) executa
  a arbitragem de alvos (4.7).

### <a id="46-messages-brains-the-state-machine"></a>4.6 Mensagens, cérebros e máquina de estados

- Cada mensagem passa pelo enfileiramento 0xC6F60; o despachante é 0xC73E0. O tratador de um cérebro é sua vtable `+0x54`
  = **0x922A0** (depois 0x9E9D0, a máquina de estados e a VM): os scripts de ataque do herói executam a partir de mensagens para seu
  cérebro.
- `@PassBrain` armazena um id de cérebro pelo componente `+0x20` (0x55C70): o herói recebe 22 na configuração, trocado para 2 a
  cada golpe recebido e depois de volta.
- Máquinas de cérebro e animação são definições por tipo: os cinco Ringwraiths compartilham um componente `+0x50` e um
  `+0x3F8`. Dois heróis do mesmo tipo compartilhá-los é normal.
- **Entradas da máquina de estados** (0x53090, thiscall machine = actor + 0x3D8, input; uma máscara pendente de 64 bits em `+8`, uma máscara
  de bloqueio em `+0x50`). Seus nomes estão no XBE (`INP_*`; id = ordem inversa no arquivo menos 64): 1 `INP_DIE`,
  2 `INP_KNOCKDOWN`, 3 `INP_KNOCKBACK`, 5 `INP_TAKEDAMAGE`, 13 `INP_ATTACKGROUND`, 16 `INP_BLOCK`, 28 `INP_RESSURECT`
  (sic), 35 `INP_JUMP`, 37 `INP_ARROWS`, 38 `INP_SHOOT`, 50 `INP_DRAWBOW`, 51 `INP_BOWCHARGE`, 52 `INP_LONG_BLOCK`,
  57 `INP_SLAM`, 58 `INP_DEEP_WATER`, 63 `INP_NULL`.
- Estados vistos: 2 ocioso; ataque 30 / 34 (X), 11 / 13 / 42 (Y); 27 preparando o arco, depois 28, 30, 26 e o disparo;
  41 depois 47 morte do jogador por script; 44 / 45 depois 50 morte por golpe (deitado; terminal); 48 / 51 levantando;
  55 andando na água. **O estado é comportamento, não animação**: acionar entradas de derrubada ou repulsão mudou o estado
  enquanto o modelo permanecia de pé.

### <a id="47-combat"></a>4.7 Combate

- **Caixas de ataque:** `@WeaponCollisionOn` termina em 0xC6750, depois 0xBA020 no gerenciador de contatos `[0x49E8DC]`: uma caixa
  com o atacante (`+8`), a arma (`+0x14`), valores de dano e uma máscara escolhida pelo papel (`+0x4C`).
- **O teste da caixa** é 0xBE0D0 (uma mensagem atrasada de um pool, tipo 0x19, executada na atualização do mundo). Um atacante com
  `+0x49C & 0x100` segue o caminho do jogador: precisa de `+0x466`, varre a lâmina (0x6DD70 no id da arma fornece o
  alcance; 0x257B0) e consulta o mundo de colisão (0x6A160). Seu desvio de acerto em 0xBE7D2 testa attacker ==
  `[0x43B15C]`, mas os golpes do jogador 2 acertam sem uma troca ali (3 execuções com, 2 sem: todas causaram dano). Outros
  atacantes seguem um caminho de NPC que só pode atingir seu próprio alvo. Um contato posta **mensagem 3 da arma para a
  vítima**; mensagens de acerto são `{0x103, weapon or projectile, victim}`.
- Um herói atualiza suas armas pela lista de ouvintes (`+0x3D0`: 0x86500 chama `vt+0xC` de cada ouvinte, o
  slot 3 da arma, 0x905D0). Eventos de acerto do jogador 1 passam pelo despachante 0x265D0 (ouvintes em `src+0x74`, contagem
  `src+0x174`).
- **Receber um golpe:** slot 42 (0x84220). O tratamento de acerto 0x849F0 (do tratador de mensagens 0x85340, na vítima)
  alimenta o medidor de avaliação do atacante apenas se o último atacante da vítima `+0x4BC` for `[0x43B15C]` (em 0x84DF8).
- **Alvos:** componente `+0x98`. Setters 0x539F0 (alvo e detalhes), 0x53AE0 (`+0x98`, `+0x9C`), 0x54410; 0x53B30
  limpa. Arbitragem: 0x5A450 preenche as listas 0x4110C0 (contagem 0x411394), 0x411250 (0x4114A4), 0x411140
  (0x4114AC), 0x411398 (0x4110BC); 0x5A920 obtém os candidatos (`[0x43B15C]` primeiro, depois 0x4110C0 e 0x411250) e
  os atacantes (0x411140, 0x411398); 0x57A70 limpa o alvo de cada atacante e 0x5A330 escolhe novamente. A escolha da mira do próprio herói
  é 0x5A150 (orientação da câmera ou do herói, `[0x43B110] ? [0x43B10C] : camera+0x60`, mais o ângulo do analógico
  `[0x43B18C]`). Em Weathertop, os dois heróis obtiveram seus alvos no passe de correspondência 0x57350 (chamada 0x5741E): o jogo
  também escolhe o alvo do jogador 2 (201 escolhas contra 199 do jogador 1 em 100 s, observado).
- **A recompensa por abate** 0x99D40(enemy) é chamada pelo tratador de mensagens do inimigo na morte dele (0x85706 / 0x85711, cdecl).
  É condicionada por `+0x526` e `+0x538` do inimigo, não por quem o matou, e executa no contexto que estiver atual:
  avaliação do medidor do registro (0x9DE10), popup (0xCB9D0), experiência = base do tipo de inimigo (`+0xA4` dos
  dados de seu tipo; 80 para os goblins de Balin's Tomb) x medidor x fatores (0x99CA0), adicionada por 0x9D3E0, contadores de abates.
  Recompensas repetidas para um objeto de inimigo também ocorrem no modo solo (Balin's Tomb reutiliza objetos de inimigos, derivado).

### <a id="48-death"></a>4.8 Morte

- Morte do jogador 1 (observada): vida 0 coloca o herói no estado de acerto 41; cerca de 4 s depois o `@ObjectDie` do script da fase
  (0xAB272) chama o método de morrer 0x838E0 (estado morto 47). Seu ramo de jogador inicia a câmera de morte 0x69130 (câmera lenta,
  o Olho de Sauron), e cerca de 10 s depois o código da câmera de morte encerra a missão com código 5 (de 0x64EE6). **Código 5 =
  missão fracassada após a morte do jogador.**
- O método de morrer se ramifica: papel 3, morte do inimigo (0x8CAD0); this == `[0x43B15C]`, câmera de morte; qualquer outro, apenas uma
  parte comum. Ele desmonta muita coisa (evento 46 em component+0x20, mensagens enfileiradas descartadas, alvos limpos): um herói em que
  executou não pôde ser revivido corretamente.
- A verificação de morte do script nomeia o jogador 1, portanto **o jogo nunca mata um segundo herói**: com 0 de vida ele continua.
- Um golpe fatal (dentro do slot 42) inicia a morte, como `INP_DIE`: 44 / 45, depois deitado em 50, terminal (nenhuma entrada o
  move). A partir de 50:
  estado definido como 47 com seu tempo em 0, depois `INP_RESSURECT` (28) levanta o herói (51, depois ocioso em até 0.7 s).
- A sequência de morte define o bit 0x40 de `+0x49C` (e às vezes limpa o bit 0x20 de `+0x110`), e nada os limpa: um
  herói revivido não recebia golpes até que fossem restaurados (observado: 0 golpes após reaparecimento sem a correção, 2–3 com ela).

### <a id="49-hero-records-experience-upgrades"></a>4.9 Registros de heróis, experiência e melhorias

- **Registros:** `0x4AB598 + index * 0x348` (0xD26F0; 0xD2310 mapeia o byte do herói para o índice). A partir de `+0x64`, é
  o bloco do salvamento para esse herói.

| Offset | Significado |
|---|---|
| `+4` | medidor de avaliação de combate |
| `+0x5C`, `+0x60` | tempo restante de Perfect, duração de Perfect (10 s) |
| `+0x68` | limite do próximo nível (recalculado, não salvo) |
| `+0x6C` | experiência consolidada |
| `+0x74`, `+0x78` | campos de nível (0x75430 imprime `+0x74` + 1; o indicador lê `+0x78`): não desvendados |
| `+0x7C` | brilho de subida de nível |
| `+0x90` | experiência acumulada na fase (float) |
| `+0x94..+0xB3` | estatísticas por fase, incluindo contadores de abates (`+0x98`, `+0xA0`; também `+0x128`) |
| `+0x204` | um valor de trabalho por fase (0, 0x10000 ou 0x20000 ao fechar uma loja) |

- **O medidor de avaliação:** 0x9D9D0 o aumenta (de 0 para 30 em um golpe do tipo abate; de 0x99AB0, 0x99E00, o tratamento de
  acerto 0x849F0), 0x9DF70 (a cada quadro, de 0x9E080) o reduz, mais rápido nas faixas inferiores, e dano recebido o drena
  (0x9DEC0, 0x98EF0). Faixas (0x9DE10): acima de 98 Perfect, 58 Excellent, 25 Good, senão Fair. Em 98 inicia o modo Perfect
  (`+0x5C` = `+0x60`), e quando termina o medidor vai para 0. Um nível equivale a 5000 de experiência.
- **Melhorias:** 80 bytes por herói em `0x4AC5B0 + hero * 0x50` (Aragorn 0x4AC600, Legolas 0x4AC650, Gimli 0x4AC6A0,
  Isildur 0x4AC6F0). 0xD2710 fornece o bloco de um herói, 0xD25B0(upgrade, hero) consulta uma melhoria, 0xD2570 define uma (a compra da loja).
  Comprar War Rush de Legolas definiu a melhoria 31 de Legolas, tirou 5000 de `0x4AB67C` (pontos restantes) e colocou em `0x4AB270`
  (pontos gastos da loja).
- **Escolhas de golpes:** 0x99A90 e as 20 funções em 0x9A1F0–0x9C37E consultam o getter de herói 0xD2310 para saber as melhorias de qual herói
  ler e qual ramo seguir (0x9B950: melhoria 15 comprada fornece golpe 0xE9, senão 0xE7).
- **Após uma fase:** a tela de estatísticas move a experiência da fase para os pontos futuros `[0x4AB67C]` (0xD2630:
  registro `+0x64` mais `+0x90`; flags `[0x4AB678]`, `[0x4AB270]`) e sobe o nível do registro; a loja trabalha a partir deles.

### <a id="410-checkpoints"></a>4.10 Checkpoints

- `@SetRespawnId` (0xB0FB0) preenche o registro de checkpoint em 0x1BB354 (0xD24E0, armazenado por 0xD24F0): id de reaparecimento,
  vida do herói (virtual `+0xA4`), munição (`+0x304`), depois `+0x90` de seu registro (como int) até `+0xB3`.
- Replay após um fim de jogo recarrega a fase a partir dele e restaura a experiência da fase e as estatísticas por fase do jogador 1 (800
  para 500 em um teste; com checkpoint zerado, 500 para 0). Para um mod cooperativo, o recarregamento parece uma nova fase.
- Em Gates of Moria, o id de reaparecimento 1 começa na luta do Watcher; ids 2–4 carregaram para uma tela preta.

### <a id="411-front-end"></a>4.11 Front-end

- O objeto de tela é 0x4AD050: `+4` é a próxima tela. Telas: 1 mapa, 3 salvamentos, 4 menu principal, 5 Options,
  6 jogo, 7 salvamento, 9 estatísticas da missão (`+0x9474`, vtable 0x173C40), 10 loja de melhorias (`+0x9A78`, vtable
  0x173BCC). O laço principal é 0xD1850 (entrada = vtable `+8`, saída `+0xC`).
- Após `EndMission(1)`, o tick do jogo (0x7C340) define a fase + 1 e vai para a tela 9. O nome e
  o retrato da tela de estatísticas vêm de 0x71970, que sua entrada (0x71F60) executa apenas enquanto `ui\endlvl.bff` ainda precisa carregar.
- A loja: estado de diálogo `+0x3A0` (4 = "Do you want to save your game?"; Yes define `+4` = 7). Foco: `0x4AD050 +
  0xA008` = 1 lista de melhorias; `+0xA00C` 1 Continue, 2 Replay; ambos 0 abas de fases, `+0xA004` página. Esquerda a partir
  da lista ou de Continue vai para Replay. Elemento e palavra de Replay: loja 0x425520 / 0x4256D8, estatísticas 0x426CD0 /
  0x426E88.
- 0xC35E0 reduz música e som até o silêncio para a tela de salvamento (`[0x43BD21]` = 1), 0xC3610 limpa isso.
- Seleção de herói: objeto 0x4AD058; `+0x18` cursor, `+0x20` modo (2 girando, 3 escolhido, com `+0x220` = 1).
  0x75430 define o texto do rótulo de nível a cada quadro logo antes de desenhá-lo (desenho do elemento: 0xC8940).
- Tratador da tela inicial 0x7F000: sem salvamento, define fase 0 e inicia um novo jogo (0xD1C10): a primeira execução
  vai direto para o prólogo.
- Imagens `UI\*.BFF` (tipo 350, cabeçalho de 0x80): imagens estáticas 640x448 lineares de 32 bits; fundos de menu 512x256 DXT1
  (chave 0 de `options.BFF` é a da tela Options).

### <a id="412-hud-and-renderer"></a>4.12 HUD e renderizador

- 21 listas de elementos em 0x1BAAE4 (`{elements, count, -}`), desenhadas por 0xCF450, bytes de ativação em 0x4A559C. Um elemento tem
  0xDC bytes: `+8` x, `+0xC` y, `+0x10` w, `+0x14` h (espaço do HUD, 640x480), `+0x20` cor AABBGGRR, `+0x24` exibido,
  `+0x2C` fonte, `+0x34` ponteiro de texto (ou UTF-16 em `+0x38`). **Uma largura negativa desenha um elemento com textura
  espelhado.**
- Lista 0 (0x4A0398), espada de vida: 0 faixa da lâmina, 7 barra vermelha, 8 preenchimento verde, 16 arte; 24 aljava, 25 seu brilho,
  26 contagem. Lista 1 (0x4A3D80), indicador: 0–6 (tubo, preenchimento, brilho, tampa, medalhão, marcador, ícone de golpe), 7–9 brilho
  de Perfect, 10 / 14 popup de avaliação, 11–13 brilho de subida de nível, 15 linha de mensagem. Lista 2: retrato
  do companheiro.
- O indicador (0xCF9A0) mostra `(int)+0x90 + +0x6C` menos o limite (0x9D6D0), de um total de (0x9D6A0 - 0x9D6D0). A contagem
  de flechas `[0x4A82BC]` vem de `[0x4ACBB0]`, preenchida por 0xD3530 a partir de `+0x304`.
- O objeto de textura da aljava é `{0x1709C4, 0, 0, 0, data}`: um cabeçalho de 0x80 (a textura D3D em `+0x2C`), depois
  pixels ARGB reorganizados (swizzled). O arquivo de fase tem dois desses ícones (tipo 350, chaves 6 e 0xD), por variante de herói.
- Memória livre do convidado: de 0x4BA600 em diante estava zerado em todas as execuções (0x4BA1C0 e 0x4BA400 são o item Exit do menu principal).
- O renderizador do port prende partes do HUD às bordas da tela em widescreen: partes a até 10 unidades formam um grupo, e um
  grupo em uma metade vai para essa borda (`hud_frame_end`, `hud_wide_x`). Quads de sobreposição (`xbox_overlay_cb`, até 8 quads BGRA
  no espaço 640x480) seguem o grupo em que seu centro se encontra. A sobreposição do cursor do mouse do port adota o que estiver
  instalado como seu “anterior”, portanto encadear outro callback externamente gera um laço (estouro de pilha); menus.c agora tem um
  slot para outro adicional.
- Xbox D3D: SetTransform 0x117230; o dispositivo `[0x124180]` mantém o estado n em `+0x810 + n * 64`. A projeção (estado 1,
  `+0x850`) é real; a visão (estado 0) é identidade.
- **O frustum da câmera:** SetPerspective 0x4E890(fov, aspect, near, far) (fov em radianos) mantém um objeto (0x4B2F80
  durante o jogo): planos próximo e distante (`+0`, `+4`), quadro (`+0xC`, `+0x10` = 640, 480), cantos no espaço de visão (`+0x18`..), limites
  no mundo (`+0xA8`, `+0xB8`), os quatro cantos próximos no mundo (`+0xC8..+0xF8`), os quatro distantes
  (`+0x108..+0x138`), planos (`+0x158`..). Executa apenas quando começa uma tomada de câmera (10 chamadas em 40 s), cada tomada
  com seu próprio fov (0.436, 0.663, 0.785 vistos).

### <a id="413-ranged-weapons-and-projectiles"></a>4.13 Armas de longo alcance e projéteis

- Um herói mirando pega um objeto de arma de longo alcance com 0x85FB0 (thiscall character, weapon, 0xA; `ret 8`), o que o torna
  dono da arma (`+0x11C`). Os scripts de ataque do herói disparam a partir dela pelo nome.
- O lançamento é 0xD9460: `[esp+4]` objeto do arco, `[esp+16]` id do projétil, `[esp+0x18]` atirador. Ids
  (observados, jogador 1 disparando): Aragorn 13, Legolas 19, Gimli 16 (machado de arremesso), Isildur 15; pedra de Frodo 10. A
  tabela de projéteis é igual em todas as variantes e não nomeia modelo algum: **um projétil é desenhado com o modelo de arma
  da mão do arco do atirador.**
- Modelos de armas de longo alcance (modelo / textura): arco de Legolas 0834F2D4 / 4167DADC, machado de arremesso de Gimli E7EEC090 / AB926BE7,
  arco de Aragorn 36AC3F58 / D82C5CAB. Isildur não pega nenhum.

### <a id="414-the-world"></a>4.14 O mundo

- **Mapas de caminhos** (grades caminháveis da IA): gerenciador em 0x41F428; o mapa de caminhos de um ator é
  `[0x41F428 + 0x1088 + 4 * actor+0x2EC]` (0x5CC70). Um mapa de caminhos: origem `+0x48`, `+0x4C`; tamanho da célula `+0x68` (int);
  células `+0x6C` (um byte cada); colunas `+0x70`; linhas `+0x74`. O estado de uma célula é `(byte >> 2) & 3`, ou a tabela de
  substituição em 0x418C00 onde ela é diferente de zero: 0 caminhável, 2 também caminhável (heróis ficam nela), 3 bloqueada. Gates of Moria:
  mapa de caminhos 11, 40 x 20 células de 2 unidades. A opção de depuração “AI/Draw Pathmaps” (0x8D24DD) não desenhou nada nos quadros.
- **Geradores** (vtable de classe 0x174B60): cada um executa um script que adiciona os personagens pré-construídos da fase ao seu pool
  (`@AddToSpawnPool` 0xA6480 depois 0x93250: colocado no gerador, `+0x3B8` = 1, oculto pelo bit 0x200000 de `+0x110`).
  Um pool comporta até 9 (fases usam 2–5): listas de prontos (`+0x3D0`) e gerados (`+0x3DC`). Gerar é vtable `+0xC4` =
  0x930F0 (`@SpawnAnObject` 0xAB520). Um personagem morto de pool recebe `+0x3B8` novamente no fim de sua morte e volta
  para a lista de prontos. Por fase (levantamento de 60 s): Weathertop nenhum (seus inimigos são posicionados), Gates of Moria 25
  geradores, Rohan 4, Deeping Wall cerca de 50, Courtyard 35.
- **Itens coletáveis:** classe 0x1748B0, tipo `+0x3D0` (7 flechas, 1 vida), tratador de mensagens 0x8FC60. Um toque (mensagem 13, quem
  tocou como origem) executa 0x8F960, que repõe `[0x43B15C]` (0x9D400 vida, 0x9D460 flechas). Itens deixados seguem o que o
  jogador precisa: com jogador 1 cheio, nenhum foi deixado.

### <a id="415-sound"></a>4.15 Som

- `@PlaySound` (0xB3760) vai para 0xC3BF0 e 0xED4E0, condicionado por `[0x43BD69]`; apenas scripts o usam. Os sons de combate dos heróis
  seguem outro caminho (desconhecido). `@SetSfxVolume` (0xB3450) passa por 0xC3060 para a biblioteca de som (0xEA550).

### <a id="416-the-watcher-gates-of-morias-boss"></a>4.16 O Watcher (chefe de Gates of Moria)

- `WatcherObj`, `TentacleObj`, `TentacleObj3`, `TentacleObj4`: personagens comuns (vtable 0x1741C0, papel 3). Seus
  corpos ficam no lago (tentáculos em x 33–40, y 389–410; o Watcher em 53.9, 393.8). Os objetos de script da fase
  incluem `activateWatcher`, `introduceWatcherCine`, `makeTentaclesNotTAble`, `bossMissionStart`,
  `setRespawnBossId`.
- Ciclo de um tentáculo (observado): ergue-se (estado 5, cerca de 2.6 s); ataca (2, 3 ou 4, com bit 0x400 de `+0x49C`; mensagem
  28 para o herói que persegue quando o ataque começa, no ponto em que ele estava; os heróis respondem com tipo 40);
  fica estendido até esse ponto (9, 3–5 s); ataca de novo ou recua (14, cerca de 5 s) e afunda (1). Ataques
  derrubam heróis nos estados 33 / 37 / 49 / 52 (mensagem 51).
- Em execuções de bots, o Watcher permaneceu no estado 0 com 225 de vida, e a arma de nenhum herói enviou contato (mensagem 3) a um
  tentáculo, mesmo com o alvo do herói definido nele e golpeando seu meio: os únicos contatos eram das armas dos próprios
  tentáculos atingindo os heróis.

## <a id="5-how-player-2-is-made"></a>5. Como o jogador 2 é criado

O que funciona, em ordem (`twotowers_manual.c`). Cada etapa foi descoberta por uma falha sem ela.

1. **Um segundo controle.** O registro de controle da porta 1 recebe um handle virtual (0xFEED0001), reconectado no hook de consulta (0xE7DB0)
   sempre que é 0. O hook de XInputGetState responde com o controle 2 do anfitrião (ou um script de teste); a vibração para ele retorna
   imediatamente. A consulta, a detecção de bordas e as zonas mortas do próprio jogo então funcionam para ele.
2. **O gêmeo.** Durante o carregamento, logo após construir o registro de posicionamento do jogador 1 (0xF5BC0), o original executa
   de novo no mesmo registro: um segundo personagem (o gêmeo), com papel definido como 2 para o carregador manter o original
   como jogador 1. Compartilha o registro e o handle de script do jogador 1. (Sua própria cópia renomeada de registro causava falha no primeiro
   golpe de inimigo no jogador 1: um evento de script alcançava o gêmeo sem objeto de script por trás do nome.)
3. **A configuração da fase para ele.** Os comandos de configuração do herói do script executam uma segunda vez com 0xB4690 respondendo com o
   gêmeo (apenas na fase de configuração: `@OnComboBreak`, `@PlayerLargeMass`, `@UnlockHeading` continuam disparando durante o jogo), mais
   `@PassBrain` (0xC6150). O slot 43 da vtable fornece vida máxima e atributos. Sem a configuração o gêmeo tinha 1 de vida e
   travava o jogo: seu componente postava mensagens para um alvo nulo (sem `component+0x50`).
4. **A tomada de controle**, 3 s após começar o jogo: bloco de estado do jogador 2 configurado como SetPlayer faz, bits de `+0x49C` iguais aos do jogador 1,
   colocado ao lado do jogador 1.
5. **A cada quadro, o contexto do jogador 2:** a etapa de controle executa uma segunda vez com as globais do jogador 2 trocadas para dentro
   (`[0x43B15C]`, `[0x43B160]`, `[0x1CB8B4]` = 1, os blocos de estado, o byte de herói e seu registro), e a mesma troca
   ocorre em torno de seus métodos de vtable, de sua atualização de componente e de 0x5A450. O ponteiro de câmera e a flag de controle permanecem
   os do jogador 1. O tempo do quadro é o do jogador 1 (de 0x1B0C54; uma palavra perdida da pilha deixou o tempo Perfect do jogador 2 congelado).
6. **As flags de bloqueio:** `+0x464`, `+0x465` e `component+0 & 0x18000` do jogador 1 espelhados no gêmeo a cada quadro.
   A fase os muda apenas no jogador 1 (pelo nome); sem o espelhamento o slot 1 do gêmeo pulava a locomoção e
   ele nunca se movia. Com ele, um analógico programado no controle 2 moveu o gêmeo 6.6 / 52.9 / 0.7 unidades em três janelas, e 0.00
   sem entrada (duas execuções).
7. **As mensagens do seu cérebro:** enquanto 0x922A0 trata uma mensagem cuja origem é o gêmeo, buscas de objetos do jogador 1 ou
   de uma das armas do jogador 1 respondem com o gêmeo ou sua cópia, no contexto do jogador 2. Sem isso, `@FlagAttacking`,
   `@WeaponCollisionOn/Off` e `@LockHeadingToTarget` recaíam todos no jogador 1 quando o jogador 2 golpeava.
8. **Suas próprias armas:** cópias dos registros de armas (renomeadas, chaves próprias) são construídas durante o `@AttachToBone`
   repetido (o heap ainda está aberto); depois o script de configuração das armas é repetido para elas. Por slot, do próprio herói do jogador
   2 (um slot que não existe no herói do jogador 1 recebe uma cópia extra); então cada cópia recebe o id de arma do herói do jogador 2
   (com os ids do jogador 1, Gimli golpeava com o alcance da faca de Legolas: 2 contatos em 278 testes de caixa, contra 209 em 704
   depois). O gêmeo mantém sua própria lista de ouvintes (copiar a do jogador 1 deixava suas armas onde estavam).
9. **Apenas suas próprias armas:** jogador 2 pega apenas armas construídas para ele (um hook em 0x85FB0). Antes, pegava o arco do jogador
   1 e se tornava seu dono, portanto sua mira girava o arco e a faca do jogador 1.
10. **Sua própria arma de longo alcance:** no primeiro attach repetido, cópias de cada objeto de arma de longo alcance da fase com
    o modelo de longo alcance do herói do jogador 2 (importado de sua própria variante de fase por heroes.c), fornecidas a ele no lugar das do jogador
    1.
11. **Um destino para o restante:** dentro dos eventos do jogador 2, uma busca de uma arma do jogador 1 da qual ele não tem cópia responde com
    uma cópia de longo alcance não usada, nunca desenhada. Sem isso, os eventos de Legolas (o gêmeo de um jogador 1 Legolas é um clone de Legolas)
    definiam a pose da faca esquerda do jogador 1 sempre que o jogador 2 Gimli mirava.
12. **Seu próprio tipo de personagem** (vida, munição): definido novamente após `@SetEnemyID`, a tomada de controle e o início do jogo,
    que todos lhe davam o do jogador 1.
13. **Sua própria aparência:** heroes.c constrói a fase com modelo, animações e textura do jogador 2 sob suas próprias chaves,
    entrega essas chaves ao registro do gêmeo apenas para sua construção e as nomeia apenas no pacote do jogador (0E01E39C), para que
    cenas mantenham o herói do jogador 1. Um herói convidado (Extra Heroes) joga com seu próprio esqueleto e animações compostas.
14. **Seu próprio registro:** uma cópia do registro de seu herói do salvamento, trocada com seu contexto; gravada de volta apenas
    por suas próprias telas após a fase (6.6).

O gêmeo é da mesma classe que todos os personagens, portanto a maior parte do jogo funciona para ele sem mudanças em seu contexto. O que
precisou de tratamento é tudo que pergunta “é o jogador?” (`this == [0x43B15C]` ou o nome do herói em um script):
6.3 a 6.10.

## <a id="6-what-co-op-does-and-the-evidence"></a>6. O que o cooperativo faz e as evidências

### <a id="61-the-shared-camera"></a>6.1 A câmera compartilhada

- **Ponto médio:** durante a atualização da câmera 0x68DC0 (e a câmera de morte 0x69130 e os modos de câmera 0x69070,
  0x69310, 0x695F0, 0x69760), a posição do jogador 1 contém o ponto médio dos dois heróis; é restaurada depois. Deslocá-la
  em 10 unidades moveu o ponto de foco 8–9 unidades (observado). As chamadas de dentro da etapa de controle são puladas na
  etapa do jogador 2. Bot: o ponto de foco permaneceu a 4.4–11.6 unidades do ponto médio com os heróis separados por até 46; com
  apenas jogador 1, permaneceu junto ao jogador 1 enquanto o jogador 2 se afastava 80.

- **Zoom:** o campo de visão, reaplicando SetPerspective da tomada com fov' = 2 atan(tan(fov/2) x zoom). O zoom é
  1 até 4 unidades de separação, +1 a cada 20 unidades adicionais, suavizado; limitado a 1.3 (Normal) ou 1.5 (Wide). Com 20 unidades de separação: zoom
  1.30, fov de 0.785 para 0.984. (Afastar o olho da câmera, por outro lado, realimentava sua suavização e esbarrava nas
  paredes; 2.0, visão de 79 graus, era amplo demais.)
- Enquanto um herói está caído, a câmera enquadra quem está de pé.
- Em Gates of Moria, a fase move o jogador 1 para o ponto inicial após o vídeo de abertura (47 unidades), e o ponto médio
  enquadrava uma rocha: jogador 2 agora é colocado ao lado do jogador 1 quando o jogo começa (6.2).

### <a id="62-keeping-player-2-near"></a>6.2 Manter o jogador 2 perto

- **Posicionamento no mapa de caminhos:** uma busca em inundação a partir da célula do jogador 1 pelas células caminháveis (até 5 células), escolhendo a célula
  cujos oito vizinhos também sejam caminháveis, mais próxima de 3 unidades do jogador 1; sem uma célula assim, o próprio lugar do jogador 1 (eles se
  empurram e se separam). Nunca cegamente para o lado: 3 unidades ao longo de +x colocaram o jogador 2 fora de uma borda, no vazio.
- **Quando:** no início do jogo e após cada cena (mais de 8 unidades separados); no quadro em que a fase desloca o
  jogador 1 mais de 6 unidades; a uma distância fixa enquanto uma cena faz o jogador 1 andar (em células caminháveis); recuperação (P2
  Teleport) quando longe demais por 0.5 s; queda (mais de 12 unidades abaixo do jogador 1 por 1 s).
- **O limite de distância** (desativado enquanto o P2 Bot controla): um passo para fora além de R a partir do jogador 1 é desfeito logo após o
  slot 1 do gêmeo. Bot: separação máxima de 28.1 unidades com R = 20 (o extra vem da repulsão sofrida pelo jogador 1), 48.2 sem.
  (Puxar o jogador 2 de volta no início do quadro deixava escapar: seu movimento e colisão executam depois.)

### <a id="63-combat-for-two"></a>6.3 Combate para dois

- **Dano do jogador 2** (5 de 5 execuções de bot com direcionamento, 170–1686 de vida inimiga por 25 s), com etapas 7 e 8 da seção 5
  e seu alvo definido. Ambos os heróis lutando ao mesmo tempo: 3 de 3 execuções, ambos fazendo contatos, nenhuma falha.
- **Seu alvo:** a escolha do próprio jogo (4.7). Um preenchimento inicial que substituía qualquer alvo a mais de 10 unidades pelo
  inimigo mais próximo a sobrescrevia; agora só preenche quando não há alvo vivo a até 35 unidades.
- **Sua escolha de mira** (0x5A150) executa no contexto do jogador 2 para o gêmeo.
- **Crédito de acerto:** uma mensagem de acerto é do jogador 2 quando sua origem é o jogador 2 ou algo possuído por ele (`+0x11C`), e seu tratamento
  de acerto então executa no contexto dele (medidor de avaliação, último atacante). Ler `+0x4BC` primeiro identificava o atacante anterior:
  os golpes de machado do jogador 2 apareciam como se não fossem dele, e o próximo golpe de aliado no mesmo inimigo como se fosse.
- **Abates:** a recompensa por abate (0x99D40, de 0x85711) executa no contexto do jogador 2 quando o último atacante do inimigo é
  jogador 2. Antes, cada abate seu adicionava um abate ao registro do jogador 1 ("Fair 8" para um jogador 1 ocioso).
  Bot (Balin's Tomb, jogador 1 ocioso): 7 recompensas, todas no contexto do jogador 2, 167 de experiência; estatísticas do jogador 1 0 / 0 / 0 /
  0. Suíte: kills_post.
- **Ameaça:** cada inimigo vivo mantém uma pontuação de ameaça por jogador (vida perdida para a arma desse jogador, reduzida à metade a cada
  6 s); após cada arbitragem, um inimigo com ameaça é direcionado ao jogador de maior ameaça (0x53AE0), trocando apenas quando
  o outro supera por 25 % e 60 de vida. Bot: um inimigo atingido pelo jogador 2 se voltou para ele em 2–3 s e voltou ao jogador
  1 quando a ameaça diminuiu. Uma troca direta por causar mais dano nunca foi exercitada.
- **Inimigos atacando o jogador 2:** apenas um campo de alvo não basta (seus scripts trabalham com “o jogador”): com dois
  Ringwraiths mirando no jogador 2 por 27 s ele não recebeu dano. Portanto uma mensagem de cérebro de um inimigo mirando no jogador 2 executa
  no contexto do jogador 2, e jogador 2 é acrescentado à lista de candidatos da arbitragem. Golpes no jogador 2 por execução: 0 e
  0 sem nenhum dos dois, 1–4 com eles (cerca de metade da taxa do jogador 1 por inimigo-segundo).

### <a id="64-down-respawn-game-over"></a>6.4 Queda, reaparecimento e fim de jogo

- Regras: um herói que cai reaparece ao lado do outro após uma espera (15 / 30 / 45 s conforme a dificuldade); fim de jogo apenas
  quando ambos estão caídos.
- **Proteção de vida:** cada golpe em um herói executa com sua vida aumentada em 100000, portanto o tratador de acerto nunca vê 0; o
  dano real é aplicado depois, e com 0 ou menos o herói cai com 1 de vida. O último herói de pé recebe o golpe do próprio
  jogo, portanto seu golpe fatal é a morte do jogo.
- **Caído:** `INP_DIE` (animação de morte, deitado em 50), nenhum golpe (flags de morte mantidas), vida mantida em 1, entrada do
  controle retida (mas não no fim de jogo, ou o menu “Replay mission / Exit to menu” não recebia nada). **De pé:** estado 47,
  `INP_RESSURECT`, flags de acerto restauradas.
- **Fim de jogo:** quando o golpe fatal do jogador 2 encerra o jogo, executa no contexto dele, onde o método de morrer do jogador 1
  segue o ramo simples (sem câmera de morte). A morte do jogador 1 agora é enfileirada e executada no próximo quadro no próprio contexto do jogador 1:
  câmera de morte e Olho de Sauron, depois o estado de término 5 do próprio jogo.
- Bot (Weathertop e Balin's Tomb): jogador 2 caído e depois de pé, lutando novamente (46 novos contatos nos últimos 15 s);
  jogador 1 caído sem câmera de morte nem fim de missão, depois de pé (124 / 87 novos contatos); ambos caindo em qualquer ordem: fim de
  jogo. Suíte: down_respawn, down_gameover.

### <a id="65-hud"></a>6.5 HUD

- **Espada de vida do jogador 2:** elementos da espada do jogador 1 copiados para memória livre do convidado a cada quadro e desenhados espelhados
  (larguras negativas) no canto superior direito, por um slot de lista de HUD desativado; retrato do companheiro movido 72 unidades
  para baixo durante o desenho.
- **O contador de reaparecimento** ("P1 RESPAWN n" / "P2 RESPAWN n") sob as espadas, na fonte do jogo. O renderizador agora tem
  caixas de exclusão (`xbox_hud_excl`, `xbox_hud_excl_more` em `nv2a_pb_exec.c`): peças cujo centro está em uma ficam fora
  dos grupos de borda (em y 110–160 o contador havia unido toda a faixa superior em um grupo centralizado).
- **Indicador, popup, flechas:** indicador do jogador 2 (peças da lista 1 espelhadas, preenchidas de seu registro), seu popup de avaliação no
  seu lado por 2.6 s após seu abate (oculto no do jogador 1), sua aljava e contagem de seu próprio `+0x304`, com o ícone de
  munição de seu próprio herói (de sua variante de fase).
- **Anéis Perfect** (novo): um anel em torno do medalhão de cada jogador, preenchendo com o medidor na cor da faixa, depois com o
  tempo Perfect restante. Quads de sobreposição com bits 31 / 30 de sua versão prendendo-os à borda esquerda / direita
  (`ovl_wide_x`).
- **Marcadores de cabeça** (“P1” azul, “P2” âmbar, cinza enquanto caído), a partir das Co-op Options:
  - Projetados pelo objeto de frustum (4.12): olho a partir de um canto próximo e um distante, raio até a cabeça pelo
    retângulo próximo. Correspondeu exatamente à projeção anterior de olho/alvo onde aquela está certa, e segue
    câmeras programadas e transições (`TT_COOP_OLDPROJECT` é o modo antigo).
  - No topo da cabeça do herói (Aragorn, Legolas, Isildur 5.6 unidades; Gimli 3.6; hobbits convidados 3.4, uma estimativa), depois
    14 unidades de quadro acima. Um valor fixo de 6.8 acima dos pés flutuava muito acima de um herói perto da câmera.
  - **Atenuados atrás de paredes:** a cada quadro o jogo solicita a profundidade nas duas cabeças; na troca de buffers, um pequeno shader lê
    a profundidade do quadro ali para um alvo 4x1, copiado para um anel de staging e lido duas trocas depois. Com os
    termos z da projeção isso se torna uma distância de visão. 3 unidades ou mais à frente por 8 resultados consecutivos atenuam o marcador
    para um terço (orcs passando à frente acionavam isso tanto quanto paredes, por isso ele não é ocultado). Autoteste: um ponto 4 unidades sob
    os pés do jogador 1 é lido como atrás do chão (25 de 26). Apenas Direct3D 11; 58–60 fps com isso.
- Nas cenas, o HUD cooperativo é oculto (`tt_in_scene()`).

### <a id="66-progress-for-two"></a>6.6 Progresso para dois

- **Seu próprio registro** (5.14). Após Replay de um fim de jogo, sua experiência da fase e suas estatísticas por fase voltam aos
  valores do checkpoint, como o jogo faz para o jogador 1: ambos são mantidos quando se registra um checkpoint. Suíte:
  checkpoint (500 / 300 mantidos no checkpoint, 800 / 700 depois, fim de jogo, Replay: 500 / 300 restaurados; suas palavras de estatística
  `+0x98`, `+0x9C` 7 / 3 restauradas após 20 / 20).
- **Telas após a fase:** estatísticas do jogador 1, estatísticas do jogador 2, loja do jogador 1, loja do jogador 2, salvamento. O registro do jogador 2
  vai para o slot de seu herói, e o byte de herói passa a ser o dele durante suas telas. O registro de cada jogador e as três
  globais após a fase são mantidos quando terminam as estatísticas desse jogador e restaurados antes de sua loja (as estatísticas do jogador 2
  haviam sobrescrito a subida de nível do jogador 1). A pergunta de salvamento do jogador 1 é respondida automaticamente; a loja do jogador 2 a faz (sem
  executar 0xC35E0, que deixava essa loja sem som). Sem Replay nas telas que se seguem.
- **Salvo e carregado:** compras e experiência do jogador 2 ficam no registro de seu herói no salvamento. Suíte: save_buy,
  save_reload (seu registro inteiro retorna: um checksum de `+0x64..+0x348` sem os valores de trabalho `+0x68`,
  `+0x90`, `+0x204`).
- **Golpes comprados:** no contexto do jogador 2, o getter de herói das escolhas de golpes vê o byte de herói do jogador 2, portanto seus golpes seguem
  as melhorias de seu próprio herói. Suíte: weapons, kills_post (melhorias compradas em memória para Gimli liberam seus golpes; as de Aragorn
  nunca fazem isso). Mantidas como estão: exibições de melhorias do HUD e do front-end (0x6E350–0x6F220, 0xCCA50, 0xCCB30).
- Suíte: levelup_shops (cada loja recebe a subida de nível e os pontos de seu próprio jogador), shop_left (esquerda pagina as abas de fases,
  e é retida onde alcançaria o Replay oculto).

### <a id="67-menus"></a>6.7 Menus

- **Co-op no menu principal**, sob Credits. Abre uma página da tela Options (options.c): New Game, Load Game
  e as configurações cooperativas. New Game e Load Game voltam ao menu principal sob uma cobertura preta e pressionam seu próprio item,
  para seguir o fluxo do próprio jogo (salvamentos, mapa, seleção de herói). Trocar de tela diretamente de Options
  causava falha no renderizador ao sair do mapa, e a entrada do jogo não carrega nada quando a tela anterior é 5 (esse é o
  caminho de volta do menu de pausa).
- **Seleção de herói, duas vezes:** jogador 1 escolhe, a escolha é desfeita, jogador 2 gira o anel (seu controle dirige o
  menu), a escolha do jogador 1 é feita novamente. Jogador 2 não pode escolher o herói do jogador 1 (seu rótulo mostra “Unavailable”). Duas
  linhas de estado, uma por jogador. Suíte: menus.
- **Co-op Options** (ini `[Coop]`): Difficulty, Player Icons, Camera Zoom, P2 Teleport, P2 Bot.
- **Fundo do menu Co-op:** uma imagem dos próprios arquivos do jogo do jogador (`stills3.BFF` chave 2), reamostrada,
  escurecida e reorganizada (swizzled) em tempo de execução. Suíte: menus.
- A primeira execução sem salvamento vai para a tela de título em vez de diretamente ao prólogo (objeto `+0x3F8` do tratador
  de inicialização definido primeiro).

### <a id="68-difficulty"></a>6.8 Dificuldade

| | Easy | Normal | Expert |
|---|---|---|---|
| Dano inimigo | x0.75 | x1 | x1.5 |
| Vida máxima dos heróis | x1.5 | x1 | x0.75 |
| Espera de um herói caído | 15 s | 30 s | 45 s |
| Inimigos dos geradores | como solo | cada geração traz mais 1 | mais 2 |

- Dano é escalado na proteção de vida; vida máxima sempre que o jogo a define (início de fase, melhorias).
- Os inimigos extras vêm da lista de prontos do gerador (0x930F0), reciclados conforme o jogo recicla os seus; nada pode
  ser construído durante o jogo. Deeping Wall, 150 s: 0 extras em 1x, 31 em 3x, até 18 inimigos de pools em jogo ao mesmo tempo (8 em 1x).
  Os inimigos posicionados de Weathertop não são multiplicados.

### <a id="69-pickups"></a>6.9 Itens coletáveis

- Um item coletável tocado pelo jogador 2 executa no contexto dele, portanto repõe jogador 2. Bot: "touched by (P2), in his context |
  ammo P1 30 -> 30, P2 2 -> 42". Suíte: pickups.

### <a id="610-ranged-attacks-for-player-2"></a>6.10 Ataques de longo alcance para o jogador 2

- Seu projétil é o do seu próprio herói (machado de Gimli 16, flecha de Legolas 19, ...); com seus próprios golpes (6.6), o jogo
  já o escolhe. Seus arremessos saem de sua própria cópia de longo alcance (modelo de machado de arremesso de Gimli E7EEC090): antes, saíam
  do arco do jogador 1, sem modelo de machado, portanto voavam invisíveis. Isildur, que não tem arma de longo alcance, recebe uma cópia do
  arco de Aragorn. Sua munição diminui, a do jogador 1 permanece. Suíte: weapons, weapons_bow.
- Feixe de Gandalf e Sauron (Extra Heroes) para o jogador 2: iniciado na altura de sua própria mão. As partículas do feixe de um
  disparo feito dentro do contexto do jogador 2 permaneciam para sempre, assim como as do próprio Gandalf do jogador 1: sua geração (0x8E470) recebia
  vida de -1.0; agora 0.6 s (também no solo).

### <a id="611-the-p2-bot-a-stopgap"></a>6.11 O P2 Bot (uma solução provisória)

Uma opção que joga como jogador 2 até haver configurações de controle adequadas para um segundo jogador. Qualquer entrada real no controle
2 devolve o controle ao jogador por 3 s.

- **O grupo:** jogador 1 e os companheiros (papel 2) a até 20 unidades do jogador 1. Centro = média deles; raio = membro
  mais distante + 4, mantido entre 10–18 unidades; sem companheiro perto, 8 unidades em torno do jogador 1. Ele permanece dentro (voltando a
  75 % do raio) e se afasta quando está a menos de 3 unidades do jogador 1 sem nada para combater.

- **Corpo a corpo:** inimigo mais próximo a até 6 unidades dele, ou o mais próximo dentro do círculo a até 12. Anda até
  ele (até 1.2 unidades) e golpeia apenas a até 2 unidades, com o analógico virado em sua direção. Um inimigo do qual nunca conseguiu chegar a até 2
  unidades pode ser golpeado a até 3.5 após 1 s sem se aproximar (corpos grandes; não testado). Sem se aproximar em 2.5 s: ignorado
  por 5 s. Seus ataques são combos aleatórios (XXX, XXY, XYY, YY, XY, XXXY, Y, XX, YX), com um bloqueio ocasional (1 em
  15 a cada 1.5 s quando um inimigo a até 4 unidades o persegue).
- **Longo alcance:** dentro do círculo, nada perto, munição restante: um disparo de onde está em um inimigo a até 35 unidades
  (primeiro os que perseguem um herói), assim que a fixação de alvo está no inimigo (ou após 1.2 s de LT). Fora do círculo: voltar primeiro.
  Nunca durante a luta do Watcher.
- **Jogador 1 caído:** vaga, atrás do inimigo mais próximo a até 30 unidades (senão anda até um ponto a 10 unidades), com
  combos e aparadas ocasionais; volta às regras do grupo quando o jogador 1 se levanta.
- **O Watcher:** perto do ponto de ataque do tentáculo mais próximo, toca White; um ataque contra ele que não custa vida conta
  como aparado, depois 3.5 s atacando o tentáculo estendido mais próximo no meio do corpo com o alvo nele.
- **Movimento:** o analógico segue a câmera compartilhada (analógico para cima = frente da câmera no chão). Traça rotas sobre seu
  mapa de caminhos (busca em largura por células caminháveis, 8 direções sem cortar cantos, em uma caixa 64 x 64; direcionamento para a mais distante das
  próximas 6 células em uma linha reta caminhável, a cada 250 ms), mantendo metade da direção do último quadro (ele
  ziguezagueava). Preso (menos de 1 unidade em 1.5 s): passo lateral; mais de 22 unidades atrás por 3 s: colocado ao lado do jogador 1.
- Execuções de bots (Balin's Tomb, Gimli, jogador 1 ocioso, 130 s): todas as 31 verificações de golpe a até 2 unidades do inimigo; 2–11 abates
  pelo jogador 2 por execução (varia conforme quando o jogador 1 cai). Suíte: checkpoint (no Watcher ele apara junto a um
  tentáculo e nunca dispara).

## <a id="7-wrong-leads-for-the-next-one"></a>7. Pistas erradas (para o próximo)

- Um gêmeo cujos campos são copiados do jogador 1 para completá-lo: adivinhação. A configuração do próprio jogo, repetida (5.3), é
  o que funcionou.
- `@IsPlayerWeapon` (0xABD00) não está no caminho de acerto: 0 chamadas enquanto os golpes do jogador 1 causavam dano.
- O “alvo” das armas `+0x420` (definido pelo callback de ouvinte 0x8FF50) é um evento de HUD, um resultado dos golpes.
- Executar 0x5A450 uma segunda vez para o jogador 2 o moveu em 0: a etapa de controle, atualização de componente e esse passe apenas
  preparam as coisas; o slot 1 move um personagem.
- “15 = machado de Gimli” para ids de projéteis: os ids vêm do próprio arremesso de cada herói (4.13).
- Os estados da máquina de estados não controlam a animação do modelo (4.6): acionar entradas para fazer um herói caído se deitar
  só funcionou com `INP_DIE`.
- Os vetores da câmera `+0x40` / `+0x50` não são ponto de foco e olho em todos os modos de câmera (a 1 unidade de distância em Balin's Tomb).
- A faca de Legolas balançando entre 44–46 s em algumas execuções era sua animação ociosa (também ocorreu com jogador 2 ocioso).

## <a id="8-open"></a>8. Em aberto

- **Os tentáculos do Watcher não recebem golpes** de nenhum herói em execuções de bots (4.16), portanto como vencer a luta e o que o
  bot deve fazer ali é desconhecido. Próximos itens a ler: volumes de acerto e máscaras de contato dos tentáculos, e o objeto de script
  `makeTentaclesNotTAble`.
- **O lago antes do Watcher:** jogador 2 já ficou retido ali andando na água (estado 55, sem movimento) com as mesmas flags do
  jogador 1; causa desconhecida. O checkpoint do chefe começa depois dele, portanto nenhum bot o alcança.
- **Marcadores de cabeça se afastando para fora** a partir do centro da tela foi relatado uma vez, com zoom afastado e os heróis separados, e
  não reproduzido; a projeção de frustum pode corrigir (não confirmado).
- **Sons de combate** estavam ausentes em algumas execuções de bots (vozes e golpes de todos os personagens; música normal), retornando na
  cena do troll da caverna. Solo e cooperativo tinham o mesmo volume segundo a segundo nos dumps de áudio; visto apenas com
  `TT_SKIPMOVIES`, portanto considerado um efeito exclusivo de teste.
- Weathertop: nenhum abate pelo jogador 2 em execuções de bots (motivo desconhecido); com `TT_SKIPMOVIES` a fase fica preta (espera por
  `wea1_2.bik`).
- Não cobertos: segundo controle físico (testes de bots controlam o controle 2 por script), Vulkan, 4:3, herói derrubado
  no ar ou agarrado, inimigos grandes para o P2 Bot, efeito do multiplicador nos finais de ondas e objetivos.
- Port upstream: “no extra packages” do README para `generate.py` (precisa de capstone).

## <a id="9-test-switches-and-tools"></a>9. Opções de teste e ferramentas

- O código cooperativo lê suas opções de teste com `getenv` onde são usadas; cada uma é descrita ali. Grupos:
  - preparações: `TT_COOP_TESTEND="ms:code"` (EndMission), `TT_COOP_TESTDOWN="ms1,ms2"` (herói caído),
    `TT_COOP_TESTEXP` / `TT_COOP_TESTEXP1` / `TT_COOP_TESTXP12[B]` (experiência da fase), `TT_COOP_TESTCKPT=ms` (um
    checkpoint), `TT_COOP_RESPAWNID=n`, `TT_COOP_TESTAMMO`, `TT_COOP_TESTUPG="hero:upgrade,..."`, `TT_COOP_TESTHP1/2`;
  - controles: `TT_COOP_PAD2SCRIPT`, `TT_P1SCRIPT` (com `TT_P1SCRIPT_INPLAY`), `TT_COOP_P1PORT=0` (jogador 1 em seu próprio controle
    ocioso), bots de teste com direcionamento `TT_COOP_PAD2SEEK`, `TT_COOP_P1SEEK`;
  - opções de desativação de cada correção (`TT_COOP_NO...`) e registradores de pesquisa (`TT_COOP_*LOG`).
- `TT_SKIPMOVIES` (kernel_bridge.c): aberturas de vídeos falham como ausentes, portanto o jogo os pula (mas Weathertop espera pelo
  primeiro). `TT_SHOTS="ms:file,..."`: dumps de quadros com tempo contado desde a execução, incluindo menus.
- Suíte de bots: 14 cenários, 73 verificações, em `tools/coop-bot/` do fork. Última execução completa na build publicada:
  "73 passed, 0 failed of 73 checks in 14 scenarios" (2026-10-21, 24 min).

## <a id="10-playbook-gaps-found"></a>10. Lacunas encontradas no playbook

- `playbook/split-screen.md` cobre apenas tela dividida com múltiplas instâncias; **cooperativo local em tela compartilhada, com um único processo, em
  um port a partir do fonte ou por recompilação** (este projeto) não é coberto em lugar algum.
- `playbook/decomp-and-recomp.md` lista ferramentas de recompilação do Xbox original como “not researched”: há pelo menos
  xboxrecomp (sp00nznet) e XboxXBE-Recomp (TGP482).

