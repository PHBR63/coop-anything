# <a id="world-of-goo-working-notes"></a>World of Goo: notas de trabalho

Objetivo: cooperação local em tela dividida para 2 jogadores numa cópia em execução. Jogador 1 usa mouse, jogador 2 controle. Cada um tem metade da tela e câmera própria. Conjunto de bolas compartilhado; qualquer um captura o inseto do tempo (desfaz último movimento, independentemente de quem fez); jogador 1 controla menus e mapa. Jogo on-line pelo Steam pode vir depois no mesmo mod (jogador 2 alimentado pela rede em vez do controle).

## <a id="game-identity"></a>Identidade do jogo

| Campo | Valor |
|---|---|
| Loja | Steam, aplicativo 22000, depósito 22001 |
| Identificador da compilação | 20824155 |
| Versão | Linha 1.5 (atualização de 2019: 64 bits, SDL2, recursos em dobro, dados sem criptografia). Inferida da estrutura; executável sem recurso de versão |
| Executável principal | `Win64\WorldOfGoo.exe`, 3.653.120 bytes |
| SHA-256 | `C99A90A5EE66CC82B3CAF4AC60EB49BAB4937CFADFDB26677B065089A9FBB379` |
| Motor | Estrutura C++ própria da 2D Boy (namespace "Boy"), SDL2 + OpenGL, steam_api64 |
| Sistema operacional | Windows 10 Pro 22H1 (10.0.19042), VMware SVGA 3D |

## <a id="observations-checked"></a>Observações (verificadas)

- Dados XML simples: `game\res\levels\<id>\<id>.level / .scene / .resrc`, `game\properties\*.xml`.
- 7 arquivos `.level` têm atributos `cursor1color` a `cursor4color`, e o executável tem string de formato `cursor%dcolor` junto dos outros atributos `<level>`. Vestígios do modo de 1 a 4 jogadores do Wii.
- Classes RTTI: `GooCursor`, `ControllerBuddy`, `GooController`, `LevelController`, `WorldController`, `IslandController`, `Boy::NetworkInterface`, `Boy::NullNetworkInterface`.
- Único uso de rede encontrado: estatísticas da torre World of Goo Corporation (`/wogbuddy2.php`).
- Executável não importa funções SDL de joystick/controle, mas `SDL2.dll` incluída as exporta (`SDL_GameControllerOpen` etc.); mod pode ler controle pela mesma SDL.
- OpenGL carregado em tempo de execução (sem importação `opengl32.dll`). Quadros terminam em `SDL_GL_SwapWindow`.
- Salvamentos/configuração: `%LOCALAPPDATA%\2DBoy\WorldOfGoo\` (`pers3.dat`, `config.ini`), obtidos por `SHGetFolderPathW(CSIDL_LOCAL_APPDATA)`. Steam Cloud sincroniza a pasta (`steam_autocloud.vdf`).
- Executa no VMware (SVGA 3D) a cerca de 60 fps.

## <a id="mod-loading-works"></a>Carregamento do mod (funciona)

Proxy `SDL2.dll`: original renomeada para `SDL2_real.dll`; encaminha todas as 656 exportações por `#pragma comment(linker, "/EXPORT:x=SDL2_real.x")` (arquivo `.def` com linhas `x=SDL2_real.x` não gerou encaminhadores com MSVC 14.51: todos os nomes falharam com LNK2001), implementando `SDL_GetPrefPath`, `SDL_GL_SwapWindow`, `SDL_PollEvent` próprios. Também aplica patch IAT a `SHELL32!SHGetFolderPathW` no executável.

Teste 2026-10-21: cópia iniciou no menu com proxy, log mostrou `SHGetFolderPathW(0x1c)` redirecionado ao perfil de teste, novo `config.ini` gravado ali e pasta real manteve timestamps antigos.

Testar fora da pasta Steam exige `steam_appid.txt` (`22000`) junto ao executável, com Steam em execução.

## <a id="engine-map-ghidra-1214-headless-exe-pe-timestamp-0x691acf5c-sizeofimage-0x398000"></a>Mapa do motor (Ghidra 12.1.4 sem interface, timestamp PE 0x691ACF5C, SizeOfImage 0x398000)

Endereços são RVAs (base 0x140000000). Nomes são os `FUN_` do Ghidra.

| O que | Onde | Notas |
|---|---|---|
| Singleton de aplicativo/plataforma | global `0x3507e8` (retornada por `0x972a0`) | vtable `+0x70` gráficos (null na abertura), `+0x88` getMouse(i) |
| Vetor de mouses | aplicativo `+0x78`, `Boy::Mouse*[4]` | criado em `0xaaf00` (inicialização SDL2); todos recebem vfunc `+0x18(false)`, depois mouse 0 `+0x18(true)` |
| `Boy::Mouse` (tamanho 0x88, base `Boy::Controller`) | construtor `0x9c000(this, index)` | `+0x50/+0x54` x/y (float), `+0x5c` índice, `+0x60` ativado, `+0x61` tem posição, `+0x62+b` botão b pressionado |
| Movimento do mouse | `0x9c470(Mouse*, float x, float y)` | verifica limites pelo tamanho dos gráficos, notifica ouvintes |
| Pressionar / soltar botão | `0x9c200(Mouse*, int button, int clicks)` / `0x9c630(Mouse*, int button)` | botão 0 = esquerdo |
| Eventos SDL do mouse para mouse 0 | `0xaa9b0` | plataforma só alimenta mouse 0 |
| `GooCursor` ×4 | objeto do jogo `+0x2e0`, criado em `0x58400`, construtor `0x25e10(this, index)` | índice em `+0x18`; desenho `0x261a0` |
| Cores de cursor por fase | fase `+0x2ec + i*4`, definidas no carregador `0x39b00` | padrões: 0 branco `0xffffffff`, 1 laranja `0xffff7e00`, 2 verde `0xff06ff00`; `cursorNcolor` substitui |
| Bola segurada por jogador | fase `+0x1a8 + i*8` | pegar `0x411c0(level, player, ball, flag)`: bola de outro jogador é solta primeiro por ele |

## <a id="second-player-works-in-the-engine-checked-2026-10-21"></a>Segundo jogador funciona no motor (verificado 2026-10-21)

O código de múltiplos cursores Wii está ativo na versão PC. Ativar `Mouse[1]` (vfuncs `+0x18` e `+0x08` com `true`) e fornecer `move` / `down` / `up` a cada quadro pelo hook `SDL_GL_SwapWindow` basta:

- Segundo cursor laranja com rastro é desenhado em menus e fases.
- Bola sob ele destacada em laranja (primeiro permanece branco).
- Jogador 2 pegou bola na fase 1 (Going Up), prévias de ligações à torre apareceram e, ao soltar, bola integrou a torre (capturas, execução 18:52 a 18:55).

Coordenadas de mouse são do jogo (cerca de 1600×900 para janela de tela inteira 1405×803). Mover durante abertura falha em `WorldOfGoo.exe+0x9c4a6` (gráficos ainda null); mod espera vfunc `+0x70` retornar não null.

Canal de teste: `wogcoop_cmd.txt` junto ao executável com `x y button` controla jogador 2 (usado pelos bots).

## <a id="player-2-gamepad-checked-2026-10-21-dualsense-over-usb-passthrough-in-vmware"></a>Controle do jogador 2 (verificado 2026-10-21, DualSense por USB no VMware)

- Jogo não lê controles, mas `SDL_Init(0x221)` inclui subsistema joystick; mod adiciona `SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER)` e lê primeiro controle a cada quadro.
- SDL distribuída é **2.0.9**, anterior ao suporte DualSense (2.0.14): aparece como joystick DirectInput, GUID `030000004c050000e60c000000000000`, sem mapeamento. Mod adiciona mapeamento estilo gamecontrollerdb (também DualSense Edge, PID 0DF2; Edge não testado).
- Controles: analógico esquerdo move cursor 2 (zona morta 0,22, curva quadrática, 1,1 larguras de tela por segundo no máximo); Cross (A) ou R2 segura bola.
- Teste do usuário: cursor seguiu analógico, bola arrastada com Cross integrou torre (log `hold=1`/`hold=0` e captura), simultaneamente ao mouse do primeiro.
- Uma vez, tocar analógico direito levou janela atrás da área de trabalho (jogo continuou, sem evento de falha). Não reproduzido em gravação de 2 minutos da janela ativa. Mod agora define `SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS=0`. Causa desconhecida; suspeitos Steam Input ou VMware.
- Não verificado: controle com jogo iniciado pelo Steam (Steam Input pode encapsulá-lo).

## <a id="split-screen-works-checked-2026-10-21-with-bot-input-on-level-1"></a>Tela dividida (funciona, verificada 2026-10-21 com bot na fase 1)

Caminho de renderização: laço principal `0xae960` chama `beginFrame 0xbd150`, depois `Wog::draw` (posição 0x40 na vtable, `0x89860`), `WogRenderer::draw 0x933c0` e `endFrame 0xbdfc0` (copia FBO para janela e chama `SDL_GL_SwapWindow`). Numa fase (estado `Wog+0x10`, modo `+0x18` == 3), `WogRenderer::draw` chama desenho do mundo `0x91580(renderer, gfx, ?, level, ...)` de `0x93618`; executa `Scene::draw 0x99420` por camada de profundidade com câmera `level+0x178 → scene+0x28`. Interface e cursores vêm depois. Gráficos (`Boy::SDL2Graphics`, vtable `0x2b8768`): posição 0x138 largura, 0x140 altura; posição 0x130 (retângulo de recorte) é `ret` vazio no PC. Funções GL vêm de `SDL_GL_GetProcAddress` (global glViewport `0x368538`). Renderizador usa shaders: beginFrame monta projeção pelos valores de largura/altura e a envia uma vez.

`Boy::Camera` (0x110 bytes, perspectiva): posição `+0x18/+0x1c`, distância (zoom) `+0x78`, fov `+0xb8`, tan(fov/2) `+0xbc`. Tela para mundo em z=0 (`0x9b990`): `world = cam + z * (screen − size/2) / k`, y invertido, `k = H / (2·tan(fov/2))`. Limites da cena em `.scene`: `scene+0xe8` minx, `+0xec` maxx, `+0xf0` miny, `+0xf4` maxy.

Como o mod divide a tela (tudo na proxy SDL2):

1. Função de largura (vtable 0x138) retorna metade durante fase, exceto em endFrame, que a usa para ajustar FBO à janela. Projeção, mapeamento do mouse, movimento nas bordas e interface passam a funcionar com meia largura.
2. As `call`s de beginFrame/endFrame no laço (`0xaea62`, `0xaea93`) e desenho do mundo (`0x93618`) são redirecionadas a hooks. Após beginFrame, viewport GL é metade esquerda. Mundo desenhado duas vezes: esquerda com câmera da fase, direita com câmera 2 (posição/zoom trocados no objeto só nessa chamada).
3. Eventos SDL do mouse 1 limitados à metade esquerda e esticados.
4. Cursor 2 fica à direita; mod converte metade direita para mundo (câmera 2), depois tela da câmera 1 e alimenta mouse 1; destaque, coleta, ligações e soltura usam um mundo. Quatro verificações de limites do movimento (`jb` em `0x9c4d5/0x9c4ed/0x9c506/0x9c51e`) substituídas por NOP, pois ponto pode ficar longe da tela 1.
5. Cursor 2 desenha de histórico de 24 pontos em coordenadas de mouse 1 (`cursor+0x28 + i*0x10`); hook do cursor (`GooCursor` vtable `0x2b0d60`, posição 0x18) reprojeta para metade direita.
6. Câmera 2 segue primeira até jogador 2 deslocar (analógico direito ou cursor a até 6% da borda direita); zoom sempre segue primeira; câmera 2 limitada à cena.

Conferido por capturas: duas metades com proporção correta; câmeras vinculadas mostram mesma imagem e destaque do segundo na mesma bola em ambas; após desvincular, câmera 2 moveu à direita até maxx; segundo pegou bola na própria metade, aparecendo em ambas no mesmo ponto do mundo; mouse 1 permanece à esquerda e bordas ainda movem câmera 1.

Problemas conhecidos: botão de tentar novamente desenhado nas duas metades (parte do mundo); interface (contador, menu) só à esquerda; cursor de cada um só na própria metade; menus e mapa permanecem em tela inteira.

## <a id="prior-work"></a>Trabalhos anteriores

- Nada de World of Goo em `DIRECTORY.md` / `data/directory.yaml` (2026-10-21).
- Issues e PRs GitHub: não verificadas (sem `gh` nesta máquina).
- Nenhum mod PC encontrado na web. Wii tinha cooperação local para 1 a 4 com cursor por Wii Remote e entrada durante partida ([Co-Optimus](https://www.co-optimus.com/game/514/wiiware/world-of-goo.html), [Nintendo Life](https://www.nintendolife.com/reviews/2008/10/world_of_goo)). Só primeiro movia câmera (uma análise de usuário, não verificada).
- Instalador de mods para 1.5: [goofans/globin](https://github.com/goofans/globin).

## <a id="unknown"></a>Desconhecidos

- Se aceita Steam Remote Play Together (página Steam não carregou).
- Física: namespace próprio `PhysBoy` (RTTI `PhysBoy::Body`); detalhes internos não lidos.
- Caminho de câmera e renderização da fase: ainda não mapeado.
- Se inseto do tempo, menus e saída da fase respondem aos cliques do segundo.

## <a id="settings-and-packaging-2026-10-21"></a>Configurações e empacotamento (2026-10-21)

- Teste humano de tela dividida com mouse + DualSense: funciona, sem falhas.
- `wogcoop.ini` junto ao executável (padrão gravado no primeiro início), relido a cada 60 quadros: `[screen] split, host_side`, `[cursors] p1_color, p2_color` (gravados na tabela de cores do controlador `+0x2ec`), `[gamepad] pad_index, deadzone, cursor_speed, camera_speed, edge_margin, swap_sticks, invert_camera_y, grab`, `[saves] separate` (só no início), `[debug] log`. Conferido ao vivo: host_side right (mouse à direita, segundo à esquerda), p2_color 00C0FF (cursor e destaque), split 0 para 1.
- Salvamentos separados agora opcionais (`[saves] separate = 1`); cópia de teste usa.
- Pacote: `SDL2.dll`, `install.bat`, `uninstall.bat`, `README.txt`. Arquivos batch precisam de ASCII com CRLF (LF e UTF-8 quebraram `cmd`).

## <a id="next"></a>A seguir

1. Inseto do tempo, saída, menu de pausa e indicadores OCD com dois jogadores.
2. Mostrar cursor de cada um na outra metade; posição da interface.
