# <a id="the-doors-of-trithius-notes-for-the-next-agent"></a>The Doors of Trithius: notas para o próximo agente

Jogo 0.6.3b (compilação Steam 25513945). Cada fato abaixo foi verificado com `javap` no `DOT.jar` do próprio jogo ou medido ao vivo com o host realizando sozinho a mesma ação. Os nomes das classes são os do jogo. Fatos válidos apenas para um mod de dois jogadores estão marcados como (cooperativo).

## <a id="turns-and-the-world-map"></a>Turnos e mapa do mundo

- Um passo no mapa do mundo corresponde a N unidades de finalização mais um início de turno. `OverworldMovementService.turnCleanup` executa todos os procedimentos de início de turno uma vez por unidade de custo do terreno (40, 50, 80, 100 ou 120). `RefreshPlayerAbilities` avança `updateCooldowns` e depois `updateToggles` a cada unidade. Medição: um tempo de recarga de 300 cai para 259 após um passo de 40 unidades na planície.
- `OverworldData.movementDetails` é um único espaço para o único jogador. `turnCleanup` grava nele os detalhes do terreno do jogador ativo, e `OverworldGameState.load` o calcula. (Cooperativo) Mantenha uma cópia por jogador e redefina-a quando um jogador se mover sem ter seu próprio turno.
- Passar o turno (Espaço no mapa do mundo) não dispara `PlayerTurnCompleteEvent` e também nunca reduz o cansaço no jogo original.
- `PlayerHungryCheckCommand` não subtrai nada após um turno de movimentação no mapa do mundo.

## <a id="interaction-and-doors"></a>Interação e portas

- E (`PlayerInteractsWithNearbyObject`) mantém entidades que possuem tanto um componente de recurso quanto um de interação do jogador a uma distância em linha de até 1. Uma correspondência dispara `PlayerInputUseFeatureEvent`; várias abrem um seletor. O componente de porta nunca é lido.
- Nenhuma porta distribuída com o jogo possui componente de interação do jogador (`modules/map_features.dat`: quatro recursos de porta, todos com `interaction=null`). As portas abrem por C (`PlayerOpenClosesAdjacentDoors`), por colisão ou por clique; todos os caminhos terminam em `PlayerUsesDoor`. E ao lado de uma porta não faz nada.
- O jogo original recalcula a caminhada em direção a uma criatura a cada passo (`HandlePathContinue`).

## <a id="shops-and-reputation"></a>Lojas e reputação

- `ShopInventory.isTradeable` oculta pilhas desgastadas (condição de 0,5 ou menos), envenenadas, amaldiçoadas, não identificadas ou sem preço. `ShopPane.isTradeable` também oculta favoritos e pilhas em estudo, e a janela lista apenas pilhas não equipadas e não alternativas.
- `ShopItem(ItemStack)` copia o item, a quantidade, o encantamento, a condição, o estudo e o nome, sem manter referência à pilha na bolsa. Não é possível distinguir qual de duas pilhas iguais um jogador moveu.
- `PlayerInventory.findItem` compara o encantamento por referência. Substituí-lo por um novo objeto igual enquanto a janela está aberta faz a venda falhar com "One of the items you are selling is no longer available".
- `PlayerAcceptTradeEvent` não transporta dados. As pilhas movimentadas ficam em `ShopPane.shopkeeper` (vendidas) e `ShopPane.playerItems` (compradas), e o painel ainda está aberto quando o evento é executado.
- Modificadores de reputação ficam em um estado oculto único, `reputation`, definido no jogador a cada carregamento de local (etapa `LoadReputation` de `PrepareZone` -> `refreshReputationEffects` -> `givePassiveReputationGain`, que pode acrescentar um ganho sorteado e uma ação "passage of time"). O estado é salvo junto ao jogador e substituído no carregamento.
- Comerciantes itinerantes não são lojas ativas.

## <a id="stats"></a>Atributos

- `RefreshStatsService.recalculateTotalHealth` define a vida total como o total do atributo `MaximumHealth` a cada `refreshStats`. Um total sem respaldo em um atributo é perdido. `LifeComponent.setTotalLife` ajusta a vida atual pela variação do total; portanto, restaure primeiro o total.
- Uma simples atualização dos efeitos passivos cancela inscrições de gatilhos feitas por outros trechos de código. (Cooperativo) Reivindique novamente os efeitos passivos do jogador ativo após qualquer atualização.

## <a id="engine-traps"></a>Armadilhas do motor

- O salvamento automático renomeia o arquivo da zona. Se outro processo o mantiver aberto (varredura de antivírus, segundo leitor), a renomeação falha e a cidade carrega pela metade.
- Abrir o painel Location duas vezes cria duas threads de carregamento para o mesmo local, o que causou falha do jogo em uma cidade. (Cooperativo) Proteja o painel para recusar uma segunda abertura.
- Muitos sistemas leem `context.player` diretamente (linhas de mensagens, notas de tutorial, névoa de guerra, barra de atalhos). (Cooperativo) Conte essas leituras por tipo antes de confiar em uma janela de personificação.

## <a id="harness-notes"></a>Notas sobre a estrutura de testes

- Mensagens de teclado postadas pelo Windows alcançam a janela AWT sem foco apenas para algumas teclas. Injete as teclas dentro da JVM (fila de eventos AWT) e poste cliques em coordenadas da tela.
- Uma janela de testes que solicita foco faz um jogo em tela cheia no mesmo PC voltar à área de trabalho. Abra janelas de teste sem solicitar foco, no monitor em que ninguém joga.
- O host de testes roda com heap de 2 a 6 GB (`-Xms2G -Xmx6G`), e dois jogadores rodam no mesmo PC. Mantenha a pasta temporária da JVM em uma unidade com espaço: quando a unidade do sistema ficou cheia, as verificações expiraram em vez de falharem.
