# <a id="dead-cells-2018"></a>Dead Cells (2018)

| | |
|---|---|
| Motor | Haxe sobre HashLink (bytecode embutido no executável), Heaps, SDL2 |
| Versões testadas | Steam, versão 35 do jogo ("The End is Near"), compilação 2023-10-01, `deadcells.exe` SHA-256 `6778a6cf685a0f5962dd880af7e7ab6dbd848b5cd32daab6a8a8a6078534a7a1`; Windows x64; DCCM 35.14.1 |
| Projetos | [Dead Cells Local Co-op](https://github.com/Osman-Mujic/DeadCellsLocalCoop) (este relato, modo cooperativo local no sofá); [DeadCellsMultiplayerMod](https://github.com/vaiserYT/DeadCellsMultiplayerMod) (on-line, projeto separado) |
| Nível de QA | none (sessões manuais de teste pelo usuário, ainda sem estrutura automatizada) |
| Última atualização | 2026-10-27 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores em um PC com dois controles conseguem jogar uma partida juntos: dois heróis reais, cada um com vida, frascos, equipamentos, mutações, pergaminhos e HUD próprios, câmera compartilhada, incapacitação/reanimação e itens duplicados para o segundo jogador. O usuário jogou a versão 0.6.0 do início de uma partida até o Banco e a descreveu como totalmente jogável do começo ao fim, com pequenos problemas. As versões 0.7.x e 0.8.0 corrigem os bugs dessa sessão, mas ainda não foram jogadas.

## <a id="existing-work"></a>Trabalhos existentes

- **DeadCellsMultiplayerMod** (vaiserYT, MIT, github.com/vaiserYT/DeadCellsMultiplayerMod, último commit observado em 2026-10-19): host/cliente on-line por TCP ou Steam P2P sobre DCCM. O jogador remoto é uma entidade "fantasma" (`GhostKing : KingSkin`), não um herói real; sem modo local. Seu item no Steam Workshop mostra "removed ... violates Steam Community & Content Guidelines" (verificado em 2026-10-23, motivo desconhecido), assim como o próprio item do DCCM no Workshop.
- **Dead Cells Core Modding (DCCM)** (github.com/dead-cells-core-modding/core, MIT): estrutura usada pelos dois mods. C# sobre .NET 10, hooks em qualquer função HashLink (`Hook_<Class>.<method> += (orig, self, ...) => ...`), proxies gerados para todas as classes do jogo.
- As ferramentas oficiais ModTools (paks de dados, CastleDB, scripts de salas/fases) não conseguem adicionar um jogador.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para modo cooperativo)

- **Um herói em todos os lugares.** `Game.ME.hero` é lido por menus, NPCs, itens coletáveis, armadilhas, portas, HUD e muitos itens. O mod cria um segundo `en.hero.Beheaded` e, ao redor do código que conhece apenas "o herói", aponta temporariamente `Game.hero` para o jogador 2 ("vez do P2"). `Game.hud` / `HUD.ME` nunca são trocados globalmente: o jogo acessa o único minimapa por eles (a troca causou falhas em v0.2.0 e v0.3.x).
- **Entrada**: `tool.Controller` lê um `GamePad` quando `gc` está definido; caso contrário, combina todos os controles. O jogador 1 mantém o controlador de inicialização fixado no controle 1; o jogador 2 recebe um novo `Controller` fixado no controle 2. Menus obtêm um `ControllerAccess` *exclusivo* sobre o controlador de inicialização: ao entregar um menu ao jogador 2, é necessário liberar esse acesso, ou o jogador 1 permanece congelado.
- **Instâncias únicas de enums Haxe**: valores de enum sem argumentos são comparados por ponteiro no jogo (`Controller.updateMainMode`, `ControlIcon.setAction`). Criar `new MainMode.MM_Gamepad()` em C# gera um terceiro valor sem correspondência, congelando os indicadores de botões. Obtenha os valores reais do jogo. (O `==` de C# do DCCM compara enums por índice, ocultando isso.)
- **Fases**: `Hero.clean()` antes de sair de uma fase, `Game.initHero` depois; hooks limpam e reposicionam o jogador 2.
- **Câmera**: `Viewport.update` mira em `tracked.spr`; durante a chamada, o sprite do jogador 1 fica no ponto médio entre os jogadores.
- **HUD**: um segundo `ui.HUD`, construído durante a vez do P2 e espelhado para a direita. 39 funções de herói/habilidade/arma escrevem em `HUD.ME` (encontradas por varredura de bytecode); cada uma roda com `HUD.ME` apontando para o HUD de seu dono. A névoa de guerra do minimapa é revelada durante o desenho; portanto, ele pode ser movido, mas não ocultado.
- **Estado de todo o perfil**: roupa e cabeça ficam em `User.heroSkin` / `User.heroHeadSkin`, de onde todos os heróis são desenhados; alguns contadores (carga de "Watcher" do Diverse Deck, contagem de eliminações) ficam em `game.data`. Exigem tratamento por jogador.
- **Chaves**: portas, teleportadores, túmulos e zonas de gatilho contam chaves apenas em `game.hero.inventory`. O mod trata as chaves como um chaveiro compartilhado (`Inventory.countItemKind/hasItem/removeOne` também veem as chaves do parceiro).
- **Ferramentas**: crashlink (incluído no DCCM) desmonta `hlboot.dat`; um dump completo em texto de todas as funções, com destinos de chamadas nomeados (cerca de 100 MB), transformou cada bug em uma busca textual, em vez de uma descompilação. Os índices de funções (`f@NNNN`) são da v35.

Detalhes, com os índices de todas as funções do jogo que receberam hooks, estão em [NOTES.md](NOTES.md).

## <a id="what-we-changed"></a>O que alteramos

O mod: https://github.com/Osman-Mujic/DeadCellsLocalCoop (MIT). Componentes principais e os bugs corrigidos:

| Área | Bug observado nas sessões de teste | Causa raiz | Correção |
|---|---|---|---|
| Menus do P2 | P1 congelado depois que P2 trocava um item | ControllerAccess exclusivo nunca liberado | liberar e dar ao menu acesso exclusivo do P2 |
| HUD | dano do P2 na barra do P1, ícones de recarga piscando, som em loop | código do herói escreve em `HUD.ME` | encaminhar ao HUD de cada dono |
| Mortes | partida encerrada com P2 vivo | morte por `Hero.onDie` sem `kill` | incapacitação/reanimação nos dois caminhos |
| Itens | itens trocados/recusados duplicados, itens de loja copiados sem fim | cópia feita antes de decidir a coleta | copiar somente depois da coleta concluída; nunca em compras ou itens descartados |
| Salas de recompensa | uma escolha para dois jogadores | `ItemAltar.disable` desativa a fileira inteira | manter os outros altares para o parceiro |
| Chaves | cartão de acesso do P2 não abria nada | verificações leem `game.hero.inventory` | chaveiro compartilhado |
| Portas/chefes | jogadores separados por portas e arenas | portas fecham atrás "do herói" | trazer o parceiro junto; L3 para reagrupar |
| Indicadores | ícones de botões presos no teclado | valor de enum criado em C# sem correspondência | usar as instâncias únicas de enums do jogo |
| Minimapa | áreas exploradas nunca exibidas | névoa desenhada somente enquanto visível | continuar desenhando e movê-lo |
| Diverse Deck, foice | habilidade do P2 sem efeito, fantasmas seguindo P1 | leituras de `game.hero` | executar como o dono |
| Eliminações | contadas duas vezes | todos os heróis vivos são notificados de cada morte | contar cada inimigo uma vez |
| Roupas | (descoberto ao ler o código) escolha do P2 alteraria a roupa do P1 | uma roupa para todo o perfil | roupa/cabeça por jogador salvas na configuração do mod |

## <a id="qa"></a>QA

Ainda não há teste automatizado: `CoopTestBot.cs` é um esqueleto vazio. Tudo acima foi verificado pelo usuário em nove sessões manuais (dois jogadores, dois controles), lendo o log DCCM após cada uma. Isso viola a regra deste guia de testar com bots, não com o usuário; o bot interno ao jogo é o primeiro próximo passo.

## <a id="how-to-play"></a>Como jogar

Instale DCCM 35.14.1 e descompacte a versão do mod em `<game dir>\coremod\mods\`. Passos e controles completos no README do mod. Não está no Steam Workshop (mods de código DCCM são instalados manualmente; os itens DCCM do Workshop foram removidos).

## <a id="known-issues"></a>Problemas conhecidos

- O jogador 2 não tem cabeça visível.
- O jogador 2 às vezes flutua após um salto duplo até executar um golpe descendente (gatilho não encontrado).
- Habilidades e itens ainda não verificados podem agir no jogador 1 quando usados pelo jogador 2.
- Desafios de sequência de eliminações e sem sofrer dano são compartilhados.

## <a id="next-steps"></a>Próximos passos

- Criar o bot interno (o hook `LOCALCOOP_SELFTEST=1` já existe): criar os dois heróis, atravessar portas e teleportadores, abrir cada menu como P2 e verificar que P1 nunca congele e ambos permaneçam na mesma fase.
- Varrer o bytecode em busca de toda habilidade/poder que leia `game.hero` (como Diverse Deck) e executá-los como seu dono.
- Câmera v2 (ideia do usuário): centralizar no ponto médio e deslocar conforme o afastamento de cada jogador, em vez de usar um limite rígido de tela.
- Encontrar a causa da flutuação após salto duplo.
