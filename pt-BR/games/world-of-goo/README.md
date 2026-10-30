# <a id="world-of-goo-2008"></a>World of Goo (2008)

| | |
|---|---|
| Motor | Estrutura C++ própria da 2D Boy ("Boy"), SDL2 + OpenGL, física própria (`PhysBoy`) |
| Versões testadas | Steam 1.5 (atualização de 2019), identificador de compilação 20824155, SHA-256 de `WorldOfGoo.exe` `C99A90A5EE66CC82B3CAF4AC60EB49BAB4937CFADFDB26677B065089A9FBB379` |
| Projetos | [World of Goo co-op](https://github.com/dobrodeetel/world-of-goo-coop) (proxy SDL2, tela dividida, versão v1.0.0), entrada "World of Goo co-op" no diretório |
| Nível de QA | community-reports (teste pelo usuário, mouse + DualSense, fase 1; verificações de bot por script; sem suíte automatizada) |
| Última atualização | 2026-10-21 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores podem jogar as fases juntos em um PC: jogador 1 com mouse, jogador 2 com controle, tela dividida com uma câmera por jogador e um mundo compartilhado. Testado somente na primeira fase do capítulo 1; o restante do jogo não foi testado.

## <a id="existing-work"></a>Trabalhos existentes

- Nenhum mod cooperativo de PC encontrado (GitHub, busca na web, 2026-10-21; issues/PRs deste repositório não foram consultadas porque `gh` não estava instalado).
- A versão Wii (2008) tinha modo cooperativo local para 1-4 jogadores, um cursor por Wii Remote, com entrada durante a partida ([Co-Optimus](https://www.co-optimus.com/game/514/wiiware/world-of-goo.html), [Nintendo Life](https://www.nintendolife.com/reviews/2008/10/world_of_goo)).
- Instalador de mods para PC 1.5: [goofans/globin](https://github.com/goofans/globin) (fases, não modo cooperativo).

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- Binário C++ fechado, sem scripts; os dados são XML simples desde a versão 1.5 (`.level`, `.scene`, `.resrc`). Salvamentos em `%LOCALAPPDATA%\2DBoy\WorldOfGoo\` (Steam Cloud).
- **O código multiplayer do Wii continua na compilação para PC.** A camada de plataforma cria quatro objetos `Boy::Mouse`, e o jogo cria quatro `GooCursor`s; existem bola segurada, detecção de objeto sob o cursor e cores de cursor por jogador (`cursor1color`.`cursor4color` nas fases). Somente o mouse 0 recebe entradas do SDL. Alimentar o mouse 1 produz um segundo jogador funcional sem alterações na lógica do jogo.
- Sem código de rede (somente estatísticas da World of Goo Corporation por HTTP).
- Uma câmera em perspectiva por cena de fase; renderizador baseado em shaders, com uma projeção por quadro. Mapa completo de funções, offsets e fórmulas: [NOTES.md](NOTES.md).

## <a id="what-we-changed"></a>O que alteramos

Tudo em um proxy `SDL2.dll` (a biblioteca real é renomeada para `SDL2_real.dll`); nenhum arquivo do jogo foi editado. Ele recusa aplicar patches a qualquer executável diferente da compilação acima.

- **Jogador 2:** habilita o mouse 1 e o controla por um controle de jogo SDL. A SDL 2.0.9 do jogo é anterior ao suporte ao DualSense, então o mod acrescenta um mapeamento para ele.
- **Tela dividida:** nas fases, o getter de largura gráfica informa metade da largura (exceto na cópia de imagem ao fim do quadro); o desenho do mundo ocorre duas vezes, nas duas metades, com duas câmeras. O mouse do jogador 1 fica limitado à sua metade. O cursor do jogador 2 é mapeado da sua metade, pela câmera 2, para o mundo e de volta para a câmera 1, de modo que a detecção sob o cursor, o ato de agarrar e os filamentos continuem usando um só mundo. A câmera 2 acompanha a câmera 1 até o jogador 2 movê-la, mantém o zoom da câmera 1 e permanece nos limites da cena.
- **Configurações:** `wogcoop.ini`, relido com o jogo em execução: divisão ligada/desligada, host à esquerda/direita, cores dos cursores, zona morta e velocidades dos analógicos, botões de agarrar e salvamentos separados.

## <a id="qa"></a>QA

- Ainda não há suíte automatizada. Um arquivo de comandos junto ao executável (`wogcoop_cmd.txt`, `x y button`) controla o jogador 2 para verificações por script; os resultados foram conferidos por capturas de tela.
- 2026-10-21, fase 1 "Going Up": jogador 2 agarrou uma bola e ela se juntou à torre (tela compartilhada e dividida); metades com proporção correta; câmera 2 desvinculada, movida e parada na borda da cena; troca de lado do host e cor do cursor aplicadas ao vivo; usuário jogou com mouse + DualSense (redirecionamento USB no VMware), sem falhas.
- Scripts de instalação/desinstalação conferidos em uma cópia da pasta do jogo.

## <a id="how-to-play"></a>Como jogar

1. Baixe `WorldOfGoo-Coop.zip` na [versão v1.0.0](https://github.com/dobrodeetel/world-of-goo-coop/releases/tag/v1.0.0), feche o jogo e execute `install.bat` (ou `install.bat "<game folder>"`).
2. Inicie o jogo e conecte o controle. Jogador 2: analógico esquerdo move o cursor, Cross/A ou R2 seguram uma bola, analógico direito move a câmera.
3. Configurações: `wogcoop.ini` junto a `WorldOfGoo.exe`. Desinstalação: `uninstall.bat` ou "Verify integrity of game files" no Steam.

## <a id="known-issues"></a>Problemas conhecidos

- Somente a fase 1 foi testada. Time bug, saída de fase, menu de pausa, OCD e outros capítulos não foram conferidos.
- O botão de tentar novamente é desenhado nas duas metades; o contador de bolas e o botão de menu aparecem apenas na metade do jogador 1.
- O cursor de cada jogador aparece somente em sua própria metade.
- Menus e mapa do mundo continuam em tela cheia, controlados pelo jogador 1.
- Uma vez, tocar o analógico direito colocou a janela do jogo atrás da área de trabalho (não reproduzido; o mod agora mantém a janela à frente quando perde o foco).
- Não testado ao iniciar o jogo pelo Steam com Steam Input habilitado.

## <a id="next-steps"></a>Próximos passos

- Jogar todos os capítulos e corrigir o que falhar (time bug, saídas, fases especiais com barras horizontais ou câmeras controladas por scripts).
- Criar uma suíte automatizada para dois jogadores sobre o arquivo de comandos.
- Jogo on-line: alimentar o mouse 1 pela rede em vez de um controle (autoridade do host; o convidado renderiza snapshots).
