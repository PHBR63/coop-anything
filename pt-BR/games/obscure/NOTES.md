# <a id="obscure-2004-research-notes"></a>Obscure (2004): notas de pesquisa

Registro técnico do mod cooperativo on-line em [obscure-coop](https://github.com/Gyurooo/obscure-coop) (MIT). Resumo, tabela QA e problemas conhecidos em [README.md](README.md). Aqui ficam evidências: endereços, resultado de cada teste e tentativas descartadas.

Rótulos: **observado** (visto no executável, log, memória ou captura), **deduzido** (inferido de observações), **desconhecido** (não encontrado). Endereços virtuais de `Obscure.exe` (base `0x400000`, sem ASLR), válidos só para compilação 215286.

## <a id="1-game-identity"></a>1. Identidade do jogo

- Obscure (Hydravision Entertainment, 2004), Steam app 254460, build id 215286. Obscure II (254480) é outro jogo, não coberto.
- `Obscure.exe` SHA-256 `7107439eb6ee1b20cad32e87f7a10a3a95b71c0b5ee26b1ec9139b263577a0f2`, 3.662.336 bytes, PE32 x86, timestamp PE 2014-03-18, FileVersion 1.0.1.0, CompanyName "Mighty Rocket Studio".
- `steam_api.dll` SHA-256 `6756b377865f55e1c8c8a21526f87559741f204036ce33e5be594d3e13b53bce`, `binkw32.dll` `3627edef5383ad43ffc14ab14f8d81171b6c08fdcb9f52a657f24301d3fd7b00`.
- Instalação: `Obscure.exe`, `steam_api.dll`, `binkw32.dll`, `cachpack.hvp`, `datapack.hvp`, `kinepack.hvp`, `strmpack.hvp`, `mrs.bik`, `logoload.bmp`, `video_cfg.dat`, `Deluxe Content/`.
- Executável com SteamStub (seção `.bind`), mas `.text` não criptografada (entropia 6,57), analisável diretamente; nunca foi desempacotado.
- Motor: **próprio da Hydravision, não RenderWare** (a ficha Wikipedia diz RenderWare). Sem strings RenderWare nem `.txd`/`.dff`; 722 nomes RTTI mostram camadas: `CZoe*` (renderização, cena, DX9), `CNoe*` (física, entidades), `CToe*`/`CHoe*` (comportamento, IA), `CHV*` (entrada, som, fluxos), `CZPackage*` (contêineres), `CZMemoryCardSteam` (salvamentos), `Cslh_L*` (linguagem de scripts) e cerca de 300 funções nativas `CTM_*`.
- Importações: VERSION, WINMM, AVIFIL32, MSVFW32, d3d9 (`Direct3DCreate9`), DINPUT8, DSOUND, SHLWAPI, binkw32, XINPUT1_3 (ordinal), KERNEL32, USER32, GDI32, COMDLG32, ADVAPI32, SHELL32, ole32, steam_api (UserStats, Utils, Friends, User, Apps, RemoteStorage, callbacks). **Sem código de rede**: nenhuma importação winsock, dplay, rede ou matchmaking Steam.

## <a id="2-prior-art"></a>2. Trabalhos anteriores

- Nenhum mod cooperativo on-line encontrado. Pesquisados diretório, jogos e issues do núcleo; web em inglês, francês e russo; repositórios e código GitHub; ModDB e Nexus (só resultados, Nexus retorna 403 a automação); discussões Steam do app 254460.
- Jogo tem cooperativo **local** para dois na mesma tela: segundo aperta START no outro controle após segundo personagem aparecer (cerca de 10 min).
- Relatos de Steam Remote Play Together na campanha completa (transmite tela host, exige controle para ao menos um jogador, pois ambos PCs parecem um teclado) e Parsec: [discussão 1](https://steamcommunity.com/app/254460/discussions/0/540735426727130309), [discussão 2](https://steamcommunity.com/app/254460/discussions/0/142261027580957991).
- Ferramentas: complemento Blender para `.zwo` ([ObscureZWOimporter](https://github.com/studiosleafmore-maker/ObscureZWOimporter), alfa, sem licença informada) e extratores/empacotadores HVP de Obscure II no Nexus (não testados aqui).
- Outras páginas: [loja Steam](https://store.steampowered.com/app/254460/), [Wikipedia](https://en.wikipedia.org/wiki/Obscure_(video_game)). Página Co-Optimus de `Obscure__The_Aftermath` trata de Obscure II.

## <a id="3-files-and-engine-facts"></a>3. Arquivos e fatos do motor

**Contêineres HVP** (observado, leitor verificado nos quatro): big-endian. Cabeçalho de `0x28` bytes: assinatura `HV PackFile\0`, u16 3, u16 1, u32 de entradas raiz, total, arquivos, tamanho TOC e 8 bytes desconhecidos. Entradas TOC em profundidade começam com u32 de tamanho e u8 de tipo: 0 diretório (u32 0, u32 quantidade de filhos, u32 tamanho do nome, nome); 1 arquivo (u32 comprimido, tamanho armazenado, tamanho, crc, deslocamento absoluto, tamanho do nome, nome). Dados zlib (`78 da`); todos os 847 verificados expandem ao tamanho listado. `crc` não é CRC-32 padrão (desconhecido; relevante só para reempacotar). Contagens: cachpack 732, datapack 1708, kinepack 40 (cenas `.bik`), strmpack 6447 (`.ogg`). Conteúdo: 202 scripts `.hoe` compilados (globais como `gPlayerDetected`, 179 referenciam nativas `TM_*`), 150 binários `.tm` por fase (significado desconhecido), `.noe`, `.dip`, `.coa`, `gdatas*.ini` (tabelas textuais de armas/dificuldade), `default.ipt` e `default_pad.ipt` (entradas), `chapters/chaptr0..9.sav` e `default*.sav` (modelos de salvamento).

**Nativas de script** (observado): 255, cada uma classe cujo construtor chama `FUN_005b8860(name, flag, nargs)`; posição 3 da vtable é o corpo; fábrica por nome `FUN_004a3140`.

**Verificações de início** (observado): `CreateMutexA(NULL, 0, "obscure_lock")` (segunda instância sai); principal `FUN_00547290` só roda se `IsDebuggerPresent()` falso; falha de `SteamAPI_Init` mostra "Steam must be running" e sai.

**Armadilhas das ferramentas** (observado): Ghidra 12.2 exige Java 25 (defina `JAVA_HOME` e PATH para `analyzeHeadless`); análise automática não nomeia vtables MSVC, deixando ausentes funções só acessíveis por elas até criá-las pelo endereço `*this = &PTR_...` do construtor; RTTI (descritor de tipo, localizador completo de objeto, vtable) as encontra pelo nome de classe.

## <a id="4-game-state-and-addresses"></a>4. Estado e endereços

**Objeto global do jogo** `*(0x6ab8e4)`:

| Campo | Significado |
|---|---|
| `+4` | estado, 2 = jogando |
| `+8` | solicitação da máquina de estados: 5 = mudar fase (nome `+0x590`, entrada `+0x5d0`), 3 = carregar salvamento (posição `+0x838`) |
| `+0x4fc`, `+0x500` | duas posições de jogador real (`CRealPlayer*`); nativas rejeitam índice 2 ou maior |
| `+0x510` | gerenciador de fases (humanos `+0x1c`, itens `+0x30`, inimigos `+0x58`; byte de ID em `+8`) |
| `+0xa20` | gerenciador de salvamento (tabela de dispositivos por jogador `+0x2c0`) |
| `+0xa24` | 161 bytes de indicadores de história, escritos por `TM_SetGameEventState` (`0x4d8c70`) |
| `+0x7bc` | bolsa compartilhada (categorias 8..17 em `+0x14 * category`) |

**Jogador real** (`CRealPlayer`): `+4` função (100 ou 200), `+0xc` personagem controlado, `+0x10` menu `CInventory`, `+0x84` controle (`+4` tipo: 1 teclado, 3..6 usuários XInput 0..3). `FUN_0044b7e0` troca personagem; `FUN_0044c2b0` executa por quadro nas duas posições.

**Personagem** (`CPlayerHuman`, vtable `0x6449e4`): `+0x20..+0x28` posição, `+0x2c..+0x34` direção, `+0x54` vida, `+0x58`/`+0x5c` morte, `+0x60` estado (10 ocioso, 20 andar, 30 correr, 101 mirar, 103 golpear, 50/52 porta), `+0x68` corpo físico, `+0x78` ID, `+0x88` jogador real controlador, `+0x128` `CPlayerInventory` embutido, `+0x224` porta usada, `+0x230` estado solicitado, `+0x238..+0x254` bloco de movimento. Posição 1 da vtable é `Update` (`FUN_0043f6e0`), que executa máquina de estados `FUN_0043bf60`; ociosa, muda pelo estado solicitado escrito pelo controle antes no quadro. Alterar `+0x60` não persiste; solicitação conduz animação. Valores solicitados duram um quadro (golpe `103` por um quadro).

**Inimigos** (`CPlayerPNJ*`, como `CPlayerPNJMord`, vtable `0x64cafc`): lista `+0x58` do gerenciador, nós `{item, next}`. Posição/direção vêm do corpo físico por quadro. `TM_SetLife` usa posição 6 (`AddLife`); `TM_KillPlayer` define `+0x54 = 0`, `+0x58 = 1`, `+0x5c = 1`.

**Itens e portas** (lista `+0x30`, chave por tipo `+4` e ID `+8`, posição `+0xc..+0x14`): `CItDoor` tipo 1 (`+0x88` abertura, `+0xfc` tempo até 2000), `CItPlayerPos` tipo 2 (pontos de criação), coletáveis com `+0xfc` = coletado. Coletar é `FUN_00448a00` (AddItem). IDs únicos apenas por tipo. Registro de coletáveis em `+0x648` do jogo, pesquisado por `FUN_004ebdd0`. Armas no inventário não estão na lista da fase.

**Inventário:** `CPlayerInventory` tem 8 listas `{head, tail, iter, count, flag}` desde `+0x10` (passo `0x14`, categoria 1 mãos, 2..7 armas), arma em uso `+0xd8`, item ativo `+0xdc`. Item: `+4` tipo, `+8` ID, `+0x3c` quantidade, `+0xfc` coletado, `+0x12c` energia de arma (só armas). Menu `CInventory` tem seção de itens (`CInventorySectionItems`, `0x1a8` bytes, construtor `FUN_00512890`) criada por `FUN_0041f6a0` só uma vez (global `DAT_006a6868`), fazendo P2 compartilhar menu P1. **Dar** é ação 6 em `FUN_005111a0`: `FUN_00449410(item, count)` no doador, depois `FUN_00448a00(item, 0, 0)` no receptor.

**Fases:** 111 nomes em tabela (`FUN_0042c150`: IDs byte em `0x695df8`, nomes em `0x695e68`), por exemplo A000 = 1, B000 = 17, C000 = 49, D000 = 65, M000 = 193. IDs 225..234 (`WLOCK`...`WHOMM`) são fases de desenvolvimento ausentes; solicitar retorna ao menu (`FUN_00416a70`). `TM_LoadLevel` (`0x4ddb80`) e `TM_EventChangeLevel` (`0x4d92a0`) escrevem os três campos de transição.

**Câmera:** cada uma segue jogador real (`camera+0x180`); gerenciador de duas câmeras em `game+0x1c` (`+8` posição seguida; alternada por `FUN_0040bf10`). Quando personagem morre sem outro livre vivo, `FUN_0044c2b0` **troca jogadores reais**: sobrevivente vira P1 (`+0x4fc`, função 100), morto P2. Só dispositivo P1 abre pausa.

**Entrada:** consulta `FUN_005868e0`. Tipo 1 teclado, 3..6 XInput 0..3 (`XInputGetState`, cerca de 3.000 consultas/s, quatro usuários por quadro). Ordem: 01 A, 02 B, 03 X, 04 Y, 05 BACK, 06 START, 07 LB, 08 RB, 09/10 cliques nos analógicos, 11 direcional cima, 12 esquerda, 13 direita, 14 baixo, 15 LT, 16 RT. P1 move W/A/S/D, ação RETURN; **segurar Q** (LB) abre inventário; **LT** mira, **LT+A** golpeia. START no segundo controle mostra "Player 2 joins the game", confirmado por Enter/A do P1. Dispositivos por jogador em `tm_input.ipt` (imagem bruta das tabelas, preenchimento `0xcd`/`0xcc`; mudar tabela em memória não refaz vínculos). XInput lido sem depender do foco.

**Salvamentos:** armazenamento remoto Steam (`game0..9.sav`, `recover.sav`, `options.sav`, `tm_input.ipt`). 22.528 bytes, byte de versão 6 para `options.sav`, CRC-32 padrão de `[4:]` guardado little-endian em `[0:4]`. Modelos de capítulos têm 30.720 bytes e são rejeitados como "Damaged game" (carregador confere tamanho). Escritor `FUN_00416640`, chamado diretamente só por menu `FUN_0053fa60`. Menu de carregar chama `FUN_004524d0(slot)` no gerenciador, define `game+0x838 = slot` e `game+8 = 3`; único local de escrita de `+8 = 3`. `video_cfg.dat` lido/escrito por `ISteamApps::GetAppInstallDir` (app `0x3e1fc`), portanto cópia ainda usa arquivo da instalação da loja.

## <a id="5-co-op-design"></a>5. Projeto cooperativo

- **Entrada remota:** proxy `xinput1_3.dll` junto a `Obscure.exe` relata controle virtual num índice XInput alimentado pelo remoto, tratado como P2 local. Controles reais ocultáveis nos testes (`HIDE_REAL_PADS`). Teclado DirectInput virtual (`GetDeviceState` posição 9, cada dispositivo teclado criado) controla menus; jogo não consulta mouse.
- **Autoridade:** host é jogo real, convidado espelha. Mod altera `CPlayerHuman::Update` no convidado: antes da máquina de estados, recebe estado solicitado e bloco de movimento do host; depois, posição/direção do host.
- **Hook por quadro:** `steam_api!SteamAPI_RunCallbacks`, uma vez por ciclo principal.
- **Transporte:** P2P Steam pela própria `steam_api.dll` de 2014, vtables C++ (`SteamUser017`, `SteamFriends013`, `SteamNetworking005`); só amigos, um convidado. Convidado se apresenta ao ID configurado ou a todo amigo jogando app 254460. Pacotes não confiáveis, menores que 1200 bytes; protocolo trata perda. Modo UDP para testes num PC.
- **Espelhado:** personagens (posição, direção, vida, estado, eventos solicitados), inimigos, 161 indicadores a cada 15 quadros, fases, itens coletados, portas (com porta usada), armas e bolsa, inventário (segurar botões, rolar, ações), visualizador de imagens, mensagens, transferência/carregamento. Não espelhado: escadas, estantes e fechaduras (resultado sim, animação não), texto das páginas de documentos (não testado), objetos dirigidos por cenas.
- **Eventos de um quadro:** host intercepta `Update`, registra mudanças de estado solicitado antes do consumo (sequência e quatro últimos valores por personagem); convidado reproduz faltantes em ordem. Só estados seguros (10, 11, 20, 30, 31, 100, 101, 103, 50/52 com porta); estado de porta sem contexto travou thread principal em `FUN_005907d0`.
- **Suavização:** pacotes levam tempo host. Envio fixo 60 Hz (por quadro gerava cerca de 600 pacotes/s a 275 fps). Convidado mantém 32 capturas, mostra tempo host menos atraso adaptativo (percentil 90 do atraso de 128 pacotes + intervalo de envio, entre 20..200 ms), interpola posição/direção, extrapola até 50 ms e reposiciona em saltos acima de 150 unidades. Inimigos usam mesmo buffer.
- **Inventário por jogador:** host cria seção ausente de P2 a cada quadro (alocador `0x5e3fda`, construtor `FUN_00512890`) e altera devolução ao fechar (`75 19` para `EB 19` em `0x41fb1f`).
- **Referencial de movimento do convidado:** `FUN_0044c2b0` transforma analógico em direção mundial relativa a vetor frontal: referência travada (`+0xa8/+0xac/+0xb0` do jogador real, válida com `+0xa0` = 1 e analógico próximo da direção capturada, `+0xb4/+0xb8`) ou câmera atual (`*(*(game+0x514)+0x54)`, eixo `+0x40/+0x44/+0x48`). Referências copiadas por `FUN_0040bf10` e `FUN_0040c9f0` (zonas, vistas). No host são suas câmeras, movendo convidado no referencial host enquanto sua tela mostrava outro ângulo (relato). Convidado envia eixo da própria câmera (pacote 19, cerca de 20/s); hook host em `FUN_0044c2b0` (entrada `55 8b ec 8b 45 08`, trampolim) troca eixo na câmera e referência travada só durante atualização remota e restaura depois. Medido: enviando eixo escolhido, P2 andou a 81.6, 8.6, -81.5, -179.5 graus para +y, +x, -y, -x (`tests/moveref_test.py`, 4/4). Yaw da matriz mostrou ângulos fixos 0/90 no corredor C000 e único 90 no pátio. Sem teste de duas zonas reais simultâneas.
- **Objetos móveis (1.10):** cadeiras, rodados (suportes TV) e bolas são entidades Noe (`CNoeChair` vtable `0x6539a4`, `CNoeCasterObject` `0x65354c`, `CNoeBasketBall` `0x652f14`, `CNoeMobileRack` `0x653dc4`) envolvidas por Toe (`CToeEntityChair` `0x64732c`, `...CasterObject` `0x647318`, `...BasketBall` `0x647354`, `...MobileRack` `0x6472d4`) em `CToeWorld` (`*(game+0x588)`), lista `+0xc`, nós `{item, next}`; Toe aponta a Noe em `+4`. Lista também contém ossos de personagens; escolha por classe. Noe guarda posição em `+0xb0` (3 floats), quaternion em `+0xbc`; posições vtable `0x4c`/`0x50` leem e `0x54`/`0x58` escrevem, atualizando matriz/corpo; `0x30(1)` congela velocidade. Motor tem serialização de 9 bytes (posição 3, tag, hash de identidade e x/y/direção em 4 bytes dentro de limites; posição 4 lê), não usada pela quantização grosseira. Contagens por fase: cadeiras na maioria da escola (D000 1, fase 19 5, 21 9, 25 13, 53 15, 71 19), rodados em 52 (1), 54 (4), 68 (1), 79 (3), bola em 177; pátio 193, C000 e B000 sem eles (têm portas de armário, quebráveis e `CNoeEntityObject`). Host envia poses alteradas a 30 Hz e cada objeto cerca de uma vez/s (pacote 20); listas na mesma ordem, identidade por classe e índice nela; convidado usa definidores próprios de posição/rotação. Teste (fase 54, 10 objetos, `tests/props_test.py`, 6/6): listas iguais, objeto movido pelo definidor host acompanha; rodado empurrado de 225 para 324 unidades por personagem em contato (teleportado junto) fica a até 2 unidades no convidado. Não testado empurrar andando (teclado não moveu P1 logo após transição naquela configuração). Não sincronizados: portas `CNoeClosetDoor`, itens `CItPushable`/`CItMobile*` (nenhum encontrado nas fases varridas).
- **Quebráveis (1.11):** dois tipos, ambos sincronizados pelo estado quebrado; fragmentos voadores não.
  - Itens da lista `+0x30`: `CItBreakable` (vtable `0x64dc14`), `...DoorWindow` (`0x64dcf4`), `...Wall` (`0x64dde4`), `...Wall2` (`0x64de54`), `...Window` (`0x64e02c`). `+0x2c` vira 1; `+0x30` conta animação até 1000; posição vtable `0x60` quebra com som/efeitos (usada por `TM_EventBreakIt`), `0x64` imediatamente. No pacote de itens (tipo 3); convidado chama `0x60`, ou `0x64` se animação host acabou. `tests/break_test.py` (fase 71, 5 janelas): 4/4.
  - Objetos de cena (janelas, máquinas de bebida `distrib_PT`, liberam item `0xab`): `CNoeBreakableGroup` (vtable `0x65307c`) mantém membros com tags `+0x30` (`0xe` intacto, `0xf` quebrado, `0x11` efeitos, `0x10` inquebrável); indicador em `+0x7c`, definido por `FUN_0052a820` (this = grupo), que troca membros. Membro intacto (`CNoeBreakableUnbroken`, `0x653114`) guarda grupo em `+0x2f4`; lista Toe (`+0x588`, `+0xc`) aponta a ele em `+4`. Serializador nativo (posições 3/4 desse membro) envia mesmo indicador no byte 6 e hash do nome. Host envia índices dos intactos (pacote 21, cerca de 2 s e ao mudar); convidado chama `FUN_0052a820`. `tests/sbreak_test.py`: fase 17 (8 membros, dois quebrados inicialmente, três sem grupo) e 49 (10): estados iguais, um quebrado no host quebra no convidado, demais intactos; 3/3 em cada. Bebida é item comum; sincronização deve transportá-la (não verificado). Quebras por comando de teste, não tiros.
- **Mortes:** host acompanha objeto que entrou como P2 (mantém controle na troca), não a posição; convidado nunca troca para morto (senão violação em `0x44ba63`, corpo nulo). Host morto vira P2, START pergunta "Player 2 quits the party"; então abre pausa sozinho (3 s após morte ou F1: `game+0x60c = 1`, `FUN_005353d0` em `game+0x628`, nó 400).
- **Carregar:** host envia pacote quando `game+8 == 3`, nomeando transferência; convidado aguarda arquivo no slot cooperativo e executa mesmos dois passos para slot 0. Ao entrar, carrega sozinho o salvamento host.
- **Isolamento do mod:** convidado salva em `coop_profile` (ou pasta por usuário se instalado em Program Files, onde virtualização Windows redireciona escritas), nunca na nuvem; escritas remotas bloqueadas ou intermediadas; título mostra estado; vigia registra endereço da thread principal se ciclo parar 5 s.

## <a id="6-test-evidence"></a>6. Evidências de teste

Bots controlam duas cópias reais num PC (host/convidado UDP), por pipe nomeado na DLL (controles/teclas virtuais, comandos `level`, `teleport`, `hurt`, `give`, `loadslot`), verificando memória de ambos. Estão em `tests/` do mod.

| Área | Teste | Resultado | Primeira aprovação |
|---|---|---|---|
| Controle remoto entra como P2 | `net_join_test` | 3/3 | 0.1 |
| Ambos os personagens espelhados | `mirror_test` | 7/7 (8/8 após reescrita Steam) | 0.1 |
| Animação por estado solicitado | log de execução | 47 de 48 amostras iguais | 0.1 |
| Fase e história | `level_test` (ID 194) | 7/7 | 0.1 |
| Inimigos e vida | `enemy_test` | 6/6 | 0.1 |
| Coleta | `item_test` | 5/5 | 0.1 |
| Morte de inimigo | `combat_test` | 6/6 | 0.1 |
| Entrada recebe salvamento host | `join_test` | 5/5 | 0.2 |
| Inventário individual | `items_split_test` | 3/3 | 0.3 |
| Eventos de ataque | `attack_test` | host 3 golpes, convidado 3 | 0.3 |
| Dar arma | `give_test` | 7/7 | 0.4 |
| Bolsa compartilhada | `bag_test` | 9/9 | 0.5 |
| Porta e P2 atravessando | `door_test`, `p2door_test` | 7/7, 9/9 | 0.7 |
| Vigia | `stall_test` | 4/4 | 0.5 |
| Inventário no convidado | `ui_test` | 7/7 | 0.6 |
| Imagens e mensagens | `view_test`, `msg_test` | 7/7, 2/2 | 0.6 |
| Troca na morte | `death_test` | 7/7 (9/9 na primeira widescreen 1.8) | 0.8 |
| Manter câmera | `camera_test` | 3/3 | 0.9 |
| Carregar após morte, pausa host | `load_test --menu`, `load_test` | 21/21, 19/19 | 1.0 |

**Sem teste bot:** versões 1.1 a 1.8. Suavização (1.1, 1.7), superamostragem/texto (1.2 a 1.4), filtragem/ReShade (1.3 a 1.5), troca e reversão de fontes (1.5, 1.6), widescreen (1.8) verificados por capturas, medições e partidas Steam em dois PCs, não suíte cooperativa. Teste de latência/perda (`chaos_run.sh`) preparado, não executado.

Testes Steam (dois PCs, 0.2 a 1.7) relataram: sem conexão inicial (log convidado ausente; versões posteriores mostram estado no título), problema de câmera não reproduzido, congelamento em porta (corrigido), falha ao morrer (corrigida), controle individual do inventário (corrigido), barra/imagens/mensagens ausentes no convidado (corrigidas), microengasgos pela internet (suavização 1.1 e 1.7).

## <a id="7-graphics"></a>7. Gráficos

- **Direct3D 9, função fixa:** contagem original na fase em janela mostrou cerca de 520 desenhos/quadro sem shader de vértice/pixel (`SetVertexShader(NULL)` sempre), um conjunto UV e FVF `0x144`/`0x152`. Nenhuma luz Direct3D (0 `SetLight`); iluminação por cores de vértice pré-calculadas e ambiente.
- **Superamostragem (`SSAA`, 1.2):** buffer traseiro com largura/altura 2x ou 4x; cada `Present` reduz para swap chain extra do tamanho da janela com `StretchRect` LINEAR (2:1 exato é filtro de caixa). `GetClientRect` retorna tamanho maior para layout acompanhar; tela cheia vira janela sem borda com caminho em janela (`renderer+0x124 = 0`). Primeira tentativa desenhava no quarto superior esquerdo.
- **Texto (`TEXT_SCALE`, 1.4):** fontes bitmap 1:1 por `FUN_0045ba60`, posições vtable `+0xb8`/`+0xc0` do renderizador. Ao desenhar string, quadriláteros ampliados em torno de sua âncora.
- **Filtragem (`ANISO`, 1.3):** `MINFILTER` LINEAR, `MIPFILTER` NONE. Viés LOD não mudou nada; anisotrópico 16x trouxe cerca de 4% de detalhe em chão distante inclinado (gradiente médio, A/B).
- **Fontes mais nítidas (1.5), revertidas em 1.6:** troca por endereço Direct3D desenhou letras no chão quando textura de fonte foi liberada e endereço reutilizado.
- **ReShade 6.8.0:** funciona em D3D9; com `SSAA`, vê swap chain extra como segundo runtime e exige `ReShade2.ini`; `DepthCopyBeforeClears=1` habilita profundidade MXAO. Predefinições: MXAO, SMAA, Deband, CAS, Vibrance; segunda com ajuste de cores, granulação e vinheta.
- **Widescreen 16:9 (1.8):**
  - Em 2560x1440 cheio, viewport 1920x1440 em x = 320 (4:3 com faixas laterais), câmera baseada nisso. `FUN_005ab420` cria retângulo e faixas só com `renderer+0x298` não zero; construtor `FUN_005ac170` define por `mov dword [esi+0x298], 1` em `0x5ac1db`. Alterar `1` para `0` dá retângulo completo. Janela e superamostragem já usavam área toda.
  - Campo horizontal fixo (projeção `_11` = 2.4142, tangente de 67,5 graus), vertical pelo aspecto (`_22` 3.219 em 4:3, 4.292 em 16:9); só mudar para 16:9 cortava topo/base. Função `FUN_00590230` (floats `+0xc` horizontal, `+0x10` vertical; chamadores usam 4:3) substituída por hook que mantém vertical 4:3 e calcula horizontal do aspecto real. Escalar projeção gerava aparições bruscas nas bordas, pois jogo descarta geometria com valores próprios; hook resolve.
  - Hook precisa ser idempotente. Vistas usam ângulos da fase (horizontal base, vertical pelo aspecto); mudanças também realimentam ângulo atual (vertical recalculado; só horizontal coincide com armazenado). Ampliar novamente fazia vista crescer 0,75 x aspecto a cada câmera (base 0.6 virou 0.7824 e depois 1.0056). Hook lembra horizontais produzidos e repassa os coincidentes; base sempre gera igual (0.6 -> 0.7824, 0.7854 -> 1.0092, 1.1427 -> 1.4173).
  - Verificado por dumps de buffer em 2560x1440 cheio (pátio, escada, corredor, menu). Aberto: logo/fundo do menu esticados; vídeos e inventários não verificados em 16:9.

## <a id="8-rtx-remix-experiment-parked"></a>8. Experimento RTX Remix (suspenso)

RTX Remix NVIDIA visa D3D9 de função fixa, caso de Obscure. Remix 1.6.1 x86 executado numa cópia de teste.

- **Falha inicial (causa identificada, alternativa escrita):** `FUN_005ac610` percorre tabela de tipos de dispositivo e chama `GetDeviceCaps`/`CheckDeviceType`; entrada inválida (`0x658d2c`: posição sobrescrita pela quantidade de adaptadores). D3D9 nativo rejeita; Remix aceita qualquer tipo, jogo formata nome inválido e falha num loop. Rejeitar tipos fora de 1..3, como Windows, corrige início.
- **Luzes:** objetos próprios, não Direct3D: `CLightingElementLightOmni` (vtable `0x64472c`, tipo 10), `...LightSpot` (`0x644708`, tipo 11, `0x104` bytes), `...DarkOmni`, `...Ambient`, `...AmbientBox`. Omni: `+0x10` ativa, `+0x20..+0x28` posição (igual ao mundo Direct3D), `+0x2c..+0x34` direção, `+0x38` cor ARGB, `+0x3c` alcance. Interiores têm luzes (B000 8, C000 6, D000 até 4; alcance 160 a 1566), pátio não. Entregar como luzes legadas a Remix funcionou (sombras reais). Um spot desativado com alcance padrão 100000 existe em C004, provavelmente lanterna; não verificado.
- **Aberto:** no corredor C000, paredes, chão e armários mostravam uma textura espiralada em Remix, mas portas, objetos e personagens corretos. Descartados: iluminação, formato (pátio usa mesmas R5G6B5), UVs, mistura, opções Remix `recomputeTextureHashOnWrite`, `alwaysWaitForAsyncTextures`, `ignoreLastTextureStage`, ponte `sendAllServerResponses`, manter texturas liberadas vivas. Captura Remix mostraria as texturas retidas. Código arquivado, ausente nas versões distribuídas.

## <a id="9-open-items"></a>9. Pendências

- Escadas, estantes e fechaduras não animam no convidado (solicitantes de 85..87, 122..142 mapeados; enviar tipo/ID do objeto no evento).
- Executar teste de latência/perda e suíte bot completa na versão atual.
- Widescreen: logo principal, vídeos, inventário em 16:9.
- Significado de `.tm`, formato de bytecode `.hoe`, crc HVP, organização de `tm_input.ipt`.
- Obscure II (254480) é outro alvo; nada verificado.
