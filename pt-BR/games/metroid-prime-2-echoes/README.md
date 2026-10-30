# <a id="metroid-prime-2-echoes-2004-in-metroid-prime-trilogy-2009"></a>Metroid Prime 2: Echoes (2004), em Metroid Prime Trilogy (2009)

| | |
|---|---|
| Motor | Próprio da Retro Studios, Wii (PowerPC), executado no Dolphin; inimigos de Echoes são módulos RSO carregados em tempo de execução |
| Versões testadas | Metroid Prime Trilogy NTSC-U `R3ME01` rev 0 (disco extraído); `rs5mp2_p.dol` SHA-256 `5b68271fd75ff1bd48986874d6f9112fc8299a1c93c6ce459fa1a83b8ebeb2b2` (SHA-1 `2375606f4e9429a699cfa02728b0bb1176421226`); Dolphin 2609a, Windows 10 |
| Projetos | [Echoes co-op](https://github.com/FarrenB939/metroid-prime-2-echoes-coop) (códigos Gecko + patches Dolphin, tela dividida, 2 a 4 jogadores), entrada "Echoes co-op" |
| Nível de QA | community-reports (testes com dois controles Xbox, horas iniciais até a perda de itens; verificações por scripts no jogo em execução para cada recurso; sem suíte automatizada) |
| Última atualização | 2026-10-30 |

## <a id="where-things-stand"></a>Situação atual

De dois a quatro jogadores podem jogar a campanha de Echoes juntos em um PC, com tela dividida, a partir do próprio modo versus. Portas, elevadores, portais, salvamentos, escaneamento, cenas, mapa, itens coletáveis, alterações de itens da história e chefes funcionaram para todos nos testes. Pessoas só jogaram as horas iniciais. Nas áreas posteriores, a estrutura de teste teletransportou para 282 das 284 salas dos cinco mundos principais para listar inimigos e verificou se os chefes presentes num jogo novo também perseguem o jogador 2. Somente Trilogy NTSC-U é compatível; Echoes de GameCube não.

## <a id="existing-work"></a>Trabalhos existentes

- Nenhuma entrada Metroid Prime neste diretório e nenhuma issue ou PR aqui (2026-10-21 e 2026-10-24).
- SubsonicBeatz154, "Metroid Prime 2 (Trilogy) Co-op Mod", 2019-04 a 2019-07, mesma compilação Trilogy NTSC-U, só alterações de recursos (PAKs do Prime World Editor), abandonado, sem download público encontrado ([tópico do fórum](https://forum.metroidconstruction.com/index.php?topic=4942.0), lido por captura archive.org). Listava obstáculos que exigem código: morte encerra a partida, estações de salvamento desativadas, salas seguem jogador 1, teletransportes sobrescrevem inventários, Scan Visor não funciona, inventários separados, fogo amigo, inimigos miram jogador 1 e câmeras de cenas quebram para jogador 2. Este projeto corrige todos por código.
- xjonx, Echoes GameCube e demonstração E3, por volta de 2018, cancelado: atingiu limite de memória do multiplayer GameCube ([vídeo](https://youtu.be/PXVwoBMD6k0)).
- Multiworld de [Randovania](https://github.com/randovania/randovania) envia itens entre jogos separados (discos GameCube, não Trilogy); não é mundo compartilhado.
- PrimeHack só se comunica com jogador 1; Wii Remotes 2 a 4 não funcionam nele no multiplayer de Echoes ([PrimeHack issue #113](https://github.com/shiiion/dolphin/issues/113)). Use Dolphin principal.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- A interface inicial de Trilogy (`main.dol`) carrega `rs5mp2_p.dol` ao iniciar Echoes; cada patch depende de três palavras desse executável estarem residentes. Inimigos ficam em módulos RSO.
- O modo versus já executa 2 a 4 atores Samus, câmeras e HUDs em tela dividida num mundo (`CStateManager` 0x804e72e8: quantidade de jogadores +0x14f0, jogadores +0x14f4, estados dos jogadores +0x1504, gerenciadores de câmera +0x1514). Carregar um mundo de campanha nesse modo funciona; o restante são correções de código.
- A sala atual segue somente `players[0]` (atualização da porta), e muito código lê `players[0]`: mira inimiga, remetentes de mensagens de script, identificadores de alvo dos chefes, buffer de alvos do Scan Visor.
- Alterações de equipamentos da história são mensagens de script para pontos de criação (RSET aplica equipamentos a todos). Reaparecer após morrer no multiplayer reconstrói do zero o estado do jogador.
- Dificuldade: `FUN_800bc668` retorna a dificuldade salva só no modo de um jogador ('SNGL'); versus ('DTHM') sempre recebia Veteran. 0 Normal, 1 Veteran, 2 Hypermode.
- Mapa completo de endereços, hooks, tentativas e testes ao vivo: [NOTES.md](NOTES.md).

## <a id="what-we-changed"></a>O que alteramos

Um código Gecko (condição de ativação, patches de uma palavra e stub por hook) e um patch Dolphin `[OnFrame]` que grava os corpos dos hooks em MEM2 livre (0x93700000), mantendo a lista abaixo do limite Dolphin. A palavra original de cada hook é conferida no executável antes de gerar os códigos. A parte Gecko depende de 23 palavras de `rs5mp2_p.dol`, uma a cada 256 KB de código: com apenas três, sair de Echoes permitia que o manipulador aplicasse patches à interface inicial entrando durante um quadro, que então falhava num corpo de hook ("Invalid read from 0x000014f0").
Códigos, conforme nomeados no ini:

- **A, manter inventário:** reaparecimentos multiplayer preservam itens; itens iniciais do ponto de criação são dados só na primeira aparição da sessão.
- **B, sessão de campanha:** sem temporizador ou limite de abates; escolher Sidehopper Station inicia a campanha (ou continua o salvamento cooperativo) com todos os participantes; jogador reaparecido surge junto de colega, com a tela voltando do escurecimento.
- **C, salas compartilhadas:** qualquer jogador cruzando porta muda a sala. Os outros podem atravessar enquanto ela abre; quando fecha, quem ficou na sala anterior é posicionado ao lado do líder (direita, senão esquerda, senão atrás; cada ponto verificado por raio de colisão; câmera morph ball reinicializada).
- **D, cenas:** executam em tela inteira pela câmera do jogador 1; todos ficam retidos como no modo solo; mensagens e Data Network também ocupam a tela inteira.
- **E, Scan Visor e sem fogo amigo:** escaneamento funciona para todos (seletor alternativo de alvos para jogadores 2 a 4), texto aparece e qualquer um pode avançá-lo; jogadores não se ferem mutuamente.
- **F, inimigos e chefes:** atualização e mensagens de cada inimigo veem o jogador mais próximo como jogador 1; chefes que armazenam identificador de alvo (9 classes) são direcionados ao mais próximo.
- **G, estações de salvamento** sob regras multiplayer. **H, itens coletados** vão para todos. **I, progresso de escaneamento** compartilhado. **J, melhorias por script** vão para todos. **K, mapa** para qualquer controle, e o botão de pausa (Wii 2) abre Data Network de um jogador (percentuais de escaneamento e itens, Inventory, Logbook) em tela inteira para qualquer controle (quem abriu o controla), em vez do menu multiplayer individual "Quit Game?". **L, vidas compartilhadas:** reserva definida por Deathmatch Kill Limit, recarregada ao salvar; derrubados observam um colega.
- **Dificuldade:** três códigos pequenos (Normal / Veteran / Hypermode, Hypermode ativado por padrão).
- RSET da história voltou ao original (2026-10-24): alteração anterior de "somente aumentar" bloqueava a perda de itens.

## <a id="qa"></a>QA

- Sem suíte automatizada. Cada recurso foi verificado no jogo por scripts Python que leem/escrevem memória Dolphin, chamam funções por pequeno hook e pressionam teclas (scripts não publicados; repositório tem gerador de códigos); resultados por sessão em [NOTES.md](NOTES.md).
- 2026-10-24, segunda rodada (inicializações novas com códigos distribuídos):
  - Falha de saída reproduzida (sair do multiplayer para menu), depois eliminada com mudança na condição: menu principal sem aviso e código da interface nos locais antigos de hooks inalterado.
  - Data Network: Menu do jogador 2 abre em tela inteira; ele navega e fecha. Teste humano encontrou jogador 1 sem controle (entrada ociosa do jogador 2 substituía a dele a cada quadro); agora aceita só quem abriu, e teste posterior confirmou Menu para ambos.
- Verificações anteriores, 2026-10-24, inicializações novas com códigos distribuídos:
  - Hypermode: função retorna 2; acerto inimigo de 10 de dano levou jogador 1 de 99 para 83,7 (x1,53); ataque de 10 do jogador 1 contra inimigo virou 5,0.
  - Perda de itens (Hive Chamber B): ambos perderam Missiles, Space Jump, Bombs, Boost e Spider Ball.
  - Seguidor em morph ball atravessando porta de Landing Site: moveu 57,5 unidades, câmera da bola a 6,4 unidades na amostra seguinte, sem lançamento.
- Anteriormente (2026-10-23): teste básico do arquivo distribuído numa execução: portas, escaneamentos, caixa de texto, mapa para ambos, vidas com salvar Yes/No, mira de chefes em cada jogador, taxa 89 a 91 (chamadas da estrutura por segundo) numa sala de 16 inimigos.
- Levantamento de inimigos: teletransporte para 282 das 284 salas dos cinco mundos e registro de cada classe; chefes que guardam alvo (Blogg, Space Pirate e outros) verificados com jogador 2 perto e jogador 1 longe, antes e depois da correção.

## <a id="how-to-play"></a>Como jogar

Consulte o README: copie `echoes-coop-R3ME01.ini` para `GameSettings\R3ME01.ini` do Dolphin, ative cheats, opcionalmente use `WiimoteNew.ini` para dois controles Xbox, depois Echoes > Multiplayer > 2-4 players > Deathmatch (Kill Limit define vidas) > Sidehopper Station. O modo cooperativo usa o terceiro salvamento Echoes de Trilogy.

## <a id="known-issues"></a>Problemas conhecidos

- Pessoas só jogaram as horas iniciais; áreas posteriores não testadas em partidas reais.
- Somente Trilogy NTSC-U (`R3ME01` rev 0). Versões PAL, japonesa e GameCube não funcionam.
- Apenas tela dividida local. Dolphin NetPlay não testado.
- Cenas e mensagens usam a visão do jogador 1.
- Menu abre Data Network em vez de "Quit Game?" multiplayer; saia pelas Options de Data Network.
- Jogadores precisam pular para fora das estações para elas pararem de perguntar se querem salvar.
- Em controles Xbox, Wii A (confirmar, disparar) é RT; botão Xbox A é Wii B.

## <a id="next-steps"></a>Próximos passos

- Campanha cooperativa completa, listando pontos da história que ainda presumem um jogador.
- Inimigos e dispositivos condicionados à história após o início (não havia salvamento posterior).
- Verificação NetPlay; compatibilidade PAL (endereços diferentes).
