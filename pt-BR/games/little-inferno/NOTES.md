# <a id="little-inferno--working-notes"></a>Little Inferno - notas de trabalho

Registro contínuo. Observações, deduções e hipóteses são mantidas separadas.

## <a id="2026-10-22-triage"></a>Triagem de 2026-10-22

Jogo: aplicativo Steam 221260, identificador de compilação 10124709, recurso de versão 2.0.3.0, `Little Inferno.exe` SHA-256 `B61315CC90C508D7403C2DF1E12D1A4082A78C42CF56C337EAD458EC417FDCE4`, PE32 x86, Windows 10.

### <a id="observed"></a>Observado
- A pasta de instalação é `steamapps\common\Little Inferno Beta` (não `Little Inferno`).
- Um executável de 328 MB; os dados ficam em `.rsrc` (paks, consulte [liTools](https://github.com/meh2481/liTools)).
- Importações estáticas: WINHTTP, WINMM, steam_api, KERNEL32, USER32, GDI32, SHELL32, IPHLPAPI, WS2_32. Sem importações de d3d, dxgi, xinput, dinput ou hid. `d3d11.dll` e `d3d9.dll` aparecem como strings largas (carregadas pelo nome; a opção `-d3d9` seleciona D3D9).
- Entrada no PC: mensagens da janela mais `GetCursorPos`; arrastar itens usa uma junta Box2D `b2MouseJoint`. Nomes de ajustes: `MISC_mouseDragForce`, `MISC_pointerFireRadius`, `UI_CATALOG_itemBtnMaxPointerDist`.
- Existe um console de desenvolvimento (strings de ajuda: `bind`, `coins`, `stamps`, `toggle ai player`, `toggleui`, passo de tempo fixo, ...). Como abri-lo na versão comercial: desconhecido.
- "Another instance of Little Inferno is already running ... Clicking Yes could cause your save data to be lost." - várias instâncias são permitidas após uma confirmação.
- Salvamentos: `%APPDATA%\Little Inferno\` (`profiles.bin`, `settings.txt`, `imagecache.bin`).

### <a id="prior-work"></a>Trabalhos anteriores
- `DIRECTORY.md` / `data/directory.yaml`: nenhuma entrada de Little Inferno.
- Nenhum mod cooperativo para PC encontrado (busca na web em 2026-10-22).
- A edição Switch (2017) tem modo cooperativo local oficial para 2 jogadores: o segundo faz tudo que o primeiro pode fazer (menus, catálogo, fogo), com um ponteiro por Joy-Con ([Tomorrow Corporation](https://tomorrowcorporation.com/posts/grab-a-friend-switch-editions-will-have-local-multiplayer), [Nintendo Life](https://nintendolife.com/reviews/switch-eshop/little_inferno)).
- Nenhuma string de jogador 2 ou múltiplos ponteiros encontrada no executável de PC (diferentemente de World of Goo, que manteve o código dos quatro cursores de Wii).

### <a id="plan-agreed-with-owner"></a>Plano (combinado com o usuário)
Um PC, uma tela. P1 usa mouse; P2 usa cursor de controle (analógico esquerdo, Cross/A ou R2 para agarrar/clicar, R2 em espaço vazio para fogo). P2 pode fazer tudo. Moedas, selos e salvamento compartilhados. Hook: proxy `d3d11.dll` junto ao executável (alterado para `winmm.dll`, veja a implementação abaixo: carrega na inicialização, permitindo redirecionar o caminho de salvamento nas cópias de teste). Durante a implementação, o usuário permitiu que os menus fora do jogo continuassem exclusivos do jogador 1.

## <a id="2026-10-22-reverse-engineering-ghidra-1214-headless-code-only-copy-of-the-exe"></a>Engenharia reversa de 2026-10-22 (Ghidra 12.1.4 sem interface, cópia apenas do código do executável)

Os endereços são VAs do Ghidra com base de imagem 0x400000; o executável usa ASLR (rebase em tempo de execução).

### <a id="observed-1"></a>Observado
- Procedimento de janela `FUN_0049e7e0`; o mouse é consultado, não obtido por mensagens: `FUN_0049c830` lê `GetAsyncKeyState(VK_LBUTTON/VK_RBUTTON)` e `GetCursorPos`.
- A entrada é uma tabela de 22 canais float (`DAT_0083ae30`, 0x14 bytes por canal, dois quadros em buffer duplo). Os vínculos são definidos em `FUN_0049c700` (tipo 2 = tecla, 3 = eixo/botão de mouse, 4 = outro). `FUN_00473e70` consulta esses canais uma vez por tick em um vetor local em `[ebp-0x5c]` (chamada a `FUN_0049c830` em 0x473ec1) e o copia para a tabela.
- Canal "on" significa |valor| >= 0.5 (`DAT_0061968c` = -0.5, `DAT_0061967c` = 0.5).
- **Dois ponteiros já existem no motor** (resquício de multitoque / Joy-Con do Switch). `FUN_00461100` monta o estado do ponteiro (máscaras de bits `buttons pressed`, `down`, `active`, depois pares x/y) para o ponteiro 0 a partir dos canais 8 (ativo), 9 (botão), 0xb/0xc (x/y entre 0 e 1) e para o ponteiro 1 a partir de 0xe, 0xf, 0x10, 0x11. No PC, os canais 0xe..0x11 não estão vinculados.
- Auxiliares de ponteiro: `FUN_00460f60` pressionado, `FUN_00460fb0` mantido pressionado, `FUN_00461070` ativo, `FUN_00461090` posição, `FUN_004610b0` pixels, `FUN_00460fd0` por uma matriz, `FUN_00460ec0/0f00/0f30` limpeza.
- Atualização da cena da lareira `FUN_00482070`, bandeja de itens `FUN_00479ee0` (percorre ambos os ponteiros), botão genérico `FUN_00408980` (ambos), interface inicial `FUN_00467330` (título/modo/slots; apenas ponteiro 0 em alguns pontos), tela de aviso `FUN_00419470`.
- Comandos de renderização passam por `FUN_004a4630` (`switch (*(short*)cmd)`); o comando 0x17 chama `IDXGISwapChain::Present` na swap chain em `*(void**)0x7134dc + 0x10`.
- Caminho dos salvamentos: `FUN_0049ed30`, `SHGetFolderPathW(CSIDL_APPDATA)` + `\Little Inferno`.
- A sobreposição Steam também insere hook em Present; aplicar um patch à vtable da swap chain causou falha em `gameoverlayrenderer.dll` (chamada nula), então o mod usa hook no comando de renderização.

### <a id="derived"></a>Deduzido
- Alimentar os canais 0xe..0x11 logo após a consulta produz um segundo ponteiro totalmente funcional, sem mudanças na lógica: agarrar, arremessar, fogo, bandeja, cartas e botões.

## <a id="2026-10-22-build"></a>Implementação de 2026-10-22

Proxy `winmm.dll` (o jogo importa WINMM estaticamente, então ele carrega antes do código do jogo). Todas as 193 exportações winmm saltam para a DLL do sistema. Hooks: resultado da consulta (0x473ec6), comando de renderização (0x4a4630), interface inicial e aviso (0x467330, 0x419470), IAT `SHGetFolderPathW` (cópias de teste mantêm perfil próprio por `saves_dir=`). Controle: HID bruto para DualSense / DualShock 4, XInput para os demais. Anel do P2 desenhado com D3D11 antes de Present.

### <a id="checks-that-ran-scripted-player-2-through-licoop_cmdtxt-results-by-screenshot"></a>Verificações executadas (por script, jogador 2 via `licoop_cmd.txt`, resultados por captura de tela)
- P2 acende fogo, queima a placa do tutorial, abre e avança as páginas da primeira carta.
- P2 arrasta um item da bandeja para a lareira.
- P2 segura um item enquanto P1 pega outro da bandeja (ambos seguram ao mesmo tempo).
- P1 e P2 acendem dois fogos ao mesmo tempo; moedas do que P2 queimou vão para o contador compartilhado.
- A interface inicial ignora P2 (escolha do usuário); P1 navega pelos menus normalmente.
- DualSense real (USB por VMware) abre por HID; cursor aparece e fica imóvel em repouso. Analógico e botões ainda não foram experimentados por uma pessoa.
- install.bat / uninstall.bat em uma cópia da pasta do jogo.

### <a id="not-checked"></a>Não verificado
- Catálogo pelo P2 (também bloqueado para P1 naquele ponto do tutorial), capítulos posteriores, final, modo Ho Ho Holiday, tela cheia, Steam Input habilitado, controles XInput.
