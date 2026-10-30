# <a id="little-inferno-2012"></a>Little Inferno (2012)

| | |
|---|---|
| Motor | Motor C++ próprio da Tomorrow Corporation, Direct3D 11 (D3D9 como alternativa), Box2D; dados em arquivos pak dentro do executável |
| Versões testadas | Steam build 10124709, versão 2.0.3 (atualização Ho Ho Holiday, 2022), SHA-256 de `Little Inferno.exe`: `B61315CC90C508D7403C2DF1E12D1A4082A78C42CF56C337EAD458EC417FDCE4`, 32 bits |
| Projetos | [Little Inferno co-op](https://github.com/dobrodeetel/little-inferno-coop) (proxy winmm.dll, modo cooperativo local, versão v1.0.0), entrada no diretório "Little Inferno co-op" |
| Nível de QA | community-reports (o usuário jogou com mouse + DualSense; verificações de dois ponteiros por scripts com capturas de tela; sem suíte automatizada) |
| Última atualização | 2026-10-22 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores podem usar uma lareira em um PC: jogador 1 com mouse, jogador 2 com controle, ambos pegando, arremessando e queimando objetos ao mesmo tempo, com moedas e salvamento compartilhados. Verificado no tutorial e nas primeiras cartas; o restante do jogo não foi testado.

## <a id="existing-work"></a>Trabalhos existentes

- Nenhum mod cooperativo para PC encontrado (busca na web em 2026-10-22; `DIRECTORY.md` não tinha entrada).
- A edição Nintendo Switch (2017) tem modo cooperativo local oficial para dois jogadores: o segundo faz tudo que o primeiro pode fazer (menus, catálogo, fogo), com um ponteiro por Joy-Con ([Tomorrow Corporation](https://tomorrowcorporation.com/posts/grab-a-friend-switch-editions-will-have-local-multiplayer), [Nintendo Life](https://nintendolife.com/reviews/switch-eshop/little_inferno)).
- Ferramentas pak: [liTools](https://github.com/meh2481/liTools) (desempacotar/empacotar, não modo cooperativo).

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- Um executável de 32 bits; os dados (`resource.pak`, `embed.pak`, `frontend.pak`) ficam em sua seção `.rsrc`. As importações estáticas incluem WINMM (usado pelo mod como ponto de entrada); `d3d11.dll` é carregada pelo nome. Salvamentos em `%APPDATA%\Little Inferno\` (`profiles.bin`, `settings.txt`, Steam Cloud).
- A entrada é uma tabela de 22 canais float preenchida uma vez por atualização. O mouse é consultado (`GetCursorPos`, `GetAsyncKeyState`), não lido pelas mensagens da janela.
- **O motor já trata dois ponteiros.** O estado de ponteiro usado pela lareira, bandeja de itens, cartas e botões tem espaços para os ponteiros 0 e 1 (resquício do suporte a toque / Joy-Con). O ponteiro 1 lê os canais 0xe..0x11, sem nenhuma associação no PC. Escrever neles logo após a consulta permite um segundo jogador funcional sem mudar a lógica do jogo.
- Sem código de rede. Mapa completo das funções e endereços: [NOTES.md](NOTES.md).

## <a id="what-we-changed"></a>O que alteramos

Tudo fica em um proxy `winmm.dll`; nenhum arquivo do jogo é editado. Ele se recusa a aplicar patches em executáveis diferentes da compilação acima (verificação de carimbo de data/hora e tamanho da imagem).

- **Jogador 2:** lê um DualSense ou DualShock 4 por HID direto (XInput para outros controles) e escreve nos canais do ponteiro 1 (ativo, botão, x, y) após cada consulta de entrada.
- **Cursor:** o anel do jogador 2 é desenhado com Direct3D 11 imediatamente antes do comando Present do jogo (`FUN_004a4630`, comando 0x17). Aplicar patch à vtable da cadeia de troca causava falha dentro da sobreposição Steam, que também insere hook em Present.
- **Menus:** a tela de aviso e a interface inicial (título, modo, espaços de salvamento) ficam restritas ao jogador 1, a pedido do usuário; o jogador 2 é desativado durante a atualização dessas cenas.
- **Configurações:** `licoop.ini`, relido a cada segundo: ativação, velocidade do cursor, zona morta, tamanho, cor e `saves_dir` para dar perfil próprio a uma cópia de teste.

## <a id="qa"></a>QA

- Sem suíte automatizada. O jogador 2 pode ser controlado por arquivo de comandos ao lado do executável (`licoop_cmd.txt`, `x y button`); auxiliares PowerShell do repositório do mod iniciam uma cópia de teste com perfil novo, clicam pelos menus, arrastam com o mouse real e fazem capturas de tela.
- 2026-10-22, perfil novo, resultados conferidos por capturas: o jogador 2 queimou a placa do tutorial, abriu e folheou a primeira carta, pegou um item da bandeja; segurou um item enquanto o jogador 1 pegava outro; ambos fizeram fogo ao mesmo tempo; moedas da queima do jogador 2 entraram no contador compartilhado; a interface inicial ignorou o jogador 2.
- Um DualSense real por USB (repasse do VMware) é detectado; em seguida, o usuário jogou na instalação principal com mouse + DualSense e relatou funcionamento.
- `install.bat` / `uninstall.bat` verificados em uma cópia da pasta do jogo.

## <a id="how-to-play"></a>Como jogar

1. Baixe `LittleInferno-Coop.zip` da [versão v1.0.0](https://github.com/dobrodeetel/little-inferno-coop/releases/tag/v1.0.0), feche o jogo e execute `install.bat` (ou `install.bat "<game folder>"`; a pasta do Steam é `Little Inferno Beta`).
2. Inicie o jogo e conecte o controle. Jogador 2: analógico esquerdo move o cursor; Cross/A ou R2 mantém pressionado (segura um item ou faz fogo em espaço vazio).
3. Configurações: `licoop.ini` ao lado de `Little Inferno.exe`. Desinstalação: `uninstall.bat` ou "Verify integrity of game files" no Steam.

## <a id="known-issues"></a>Problemas conhecidos

- Somente o começo foi verificado. Catálogos posteriores, final e modo Ho Ho Holiday não foram testados; o jogador 2 ainda não abriu o catálogo.
- Menus fora da lareira ficam restritos ao jogador 1 (por escolha).
- Não testado com Steam Input ativado para o controle nem com controle Xbox.

## <a id="next-steps"></a>Próximos passos

- Jogar até o fim e confirmar catálogo, combinações e final com dois jogadores.
- Criar suíte automatizada sobre o arquivo de comandos (o jogador de IA `autoplay` e os comandos `coins`/`stamps` existem no console, mas o atalho do console é desconhecido na compilação comercial).
- Jogo on-line: controlar o ponteiro 1 pela rede em vez de pelo controle.
