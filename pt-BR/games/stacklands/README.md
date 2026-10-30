# <a id="stacklands-2022"></a>Stacklands (2022)

| | |
|---|---|
| Motor | Unity 2022.3.4f1, Mono (carregador oficial de mods com Harmony) |
| Versões testadas | Steam, compilação Windows no Proton Experimental, buildid 16550853 |
| Projetos | Stacklands Co-op ([stacklands-coop](https://github.com/Dudiebug/stacklands-coop)) |
| Nível de QA | automated |
| Última atualização | 2026-10-17 |

## <a id="where-things-stand"></a>Situação atual

Stacklands Co-op permite que 2 ou mais jogadores compartilhem um tabuleiro on-line: mesmas cartas, luas e missões. Todos os ciclos principais funcionam e são cobertos por teste automatizado com duas instâncias: abrir pacotes, empilhar aldeões em recursos, temporizadores de colheita, vender, comprar pacotes, alterar velocidade e avançar cenas por cliques. As salas Steam estão implementadas, mas não foram testadas (exigem duas contas Steam).

## <a id="existing-work"></a>Trabalhos existentes

Nenhum mod cooperativo ou multiplayer para Stacklands foi encontrado nas buscas do Steam Workshop, GitHub, Nexus ou web em geral (2026-10-17). O jogo oficial é exclusivamente para um jogador.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Mods:** Stacklands inclui um carregador oficial. Um mod é uma pasta em `LocalLow/sokpop/Stacklands/Mods/<id>/` contendo `manifest.json` e `<id>.dll`. A DLL tem uma classe derivada de `Mod : MonoBehaviour`, com hook `Ready()` e instância `Harmony` pronta. `Ready()` é chamado **três vezes** por inicialização; proteja contra repetição.
- **Logs desativados** nas compilações de distribuição (`Debug.Log` não imprime nada após iniciar o carregador); escreva seu próprio arquivo de log.
- **Nenhum código de rede.** Todo o estado fica em `WorldManager.instance`: `AllCards`, `AllBoosters`, `MonthTimer`, `BoardMonths`, `SpeedUp` e `CurrentBoard`. Cada carta é um `GameCard` (`Draggable`) com `CardData`, identificada por `CardData.UniqueId`.
- **Salvamentos:** `JsonUtility` em toda parte. `GameCard.ToSavedCard()` fornece estado compacto e completo da carta (posição, pai da pilha, suportes de equipamento e trabalhadores, temporizador, efeitos de estado, dados extras). É, portanto, um formato de rede natural. `WorldManager.GetSaveRound()` / `LoadSaveRound()` lidam com capturas completas da partida.
- **Simulação:** temporizadores de cartas (`GameCard.StartTimer` / `UpdateTimer`), atualizações das luas e fim de mês escalam por `WorldManager.TimeScale`. Alterar `TimeScale` para 0 e bloquear `CreateCard`, `DestroyCard`, `ChangeToCard`, `CreateBoosterpack` e os métodos de temporizador congela completamente um cliente.
- **Entrada:** `WorldManager.Update` inicia arraste em `DraggingDraggable`. O método privado `DropCard()` chama `NearbyCardTarget.CardDropped` ou `CheckIfCanAddOnStack`. Um clique é um arraste solto abaixo do limite, encaminhado por `Draggable.StopDragging` a `Clicked()`.
- **Cenas** são corrotinas que aguardam `WorldManager.ContinueClicked`. Respostas de múltipla escolha definem `ContinueButtonIndex` (consulte `CutsceneScreen.CreateMultipleOptions`).

## <a id="what-we-changed"></a>O que alteramos

A arquitetura é um espelhamento com autoridade do host:

- **Host:** executa o jogo real. A 15 Hz envia um delta comprimido com gzip contendo cada carta cujo JSON de `ToSavedCard()` mudou, além dos globais (temporizador lunar, velocidade, tabuleiro, missões e ideias descobertas, pacotes, texto e botões de cenas). A cada segundo envia um quadro completo com todas as cartas. Um novo participante recebe uma captura completa: o salvamento do host com a rodada atual inserida como `LastPlayedRound`.
- **Participantes:** carregam a captura pelo próprio `LoadPreviousRound()` do jogo, sob identificador temporário de salvamento que nunca é gravado em disco. Sua simulação fica congelada por patches Harmony. Cartas recebidas são criadas com `IsLoadingSaveRound` definido, evitando acionar missões ou ímãs, e depois associadas por `UniqueId`. Arrastes, solturas (com chave para a caixa alvo de venda/compra), cliques, vendas, mudanças de velocidade e botões de cenas são encaminhados ao host, que os reproduz pelos métodos do próprio jogo.
- **Transportes:** TCP para LAN/IP e salas Steam com `SteamNetworkingMessages`, usando "Join game" nos convites de jogo Steam (`+connect_lobby`).

Problemas encontrados durante o trabalho:

1. **`JsonUtility` descarta classes aninhadas de um assembly de mod.** Uma classe `[Serializable]` definida no mod e aninhada em outra voltava como `null`, enquanto tipos do jogo, como `SavedCard`, eram aninhados normalmente. Correção: serializar classes do mod como strings JSON separadas e manter dados aninhados em listas simples.
2. **Janela Unity sem foco rodava a 2 fps no Proton/XWayland.** Correções: `Application.runInBackground = true` e desativar vsync quando a janela perde foco durante a sessão. Na máquina de teste, os 2 fps persistiram, mas ela estava sobrecarregada com outras tarefas.
3. **A mudança de velocidade do cliente era sobrescrita antes de ser percebida.** O estado recebido do host era aplicado no mesmo quadro. Correção: verificar mudanças locais de velocidade antes de consultar a rede.
4. **Uma cena no host bloqueava toda a entrada.** Por exemplo, "New Pack Unlocked!" espera Continue. Correção: enviar texto e botões da cena aos participantes e permitir que qualquer jogador os pressione.

## <a id="qa"></a>QA

- `test/run.sh` compila o mod, copia-o para dois prefixos Proton separados (salvamentos separados) e inicia duas cópias. Os bots começam com `COOP_TEST=host` e `COOP_TEST=client`. O bot host inicia uma partida, cria cartas de teste e hospeda por TCP. O cliente entra e controla o jogo pelos caminhos reais de entrada: `DropCard` e `Clicked` com patches.
- Asserções: captura carrega; quantidade de cartas corresponde; pacote inicial espelhado; clicar no pacote gera cartas; aldeão empilhado no arbusto de frutas; temporizador de colheita roda no espelho; fruta aparece; venda dá uma moeda; compra de pacote com moedas funciona; movimento de carta no host é visto; mudança de velocidade chega ao host; cliente pressiona Continue de uma cena.
- Último resultado (2026-10-17): **13/13 aprovados.**

## <a id="how-to-play"></a>Como jogar

Consulte o README do mod. Resumo: copie a pasta `stacklands_coop` para a pasta Mods em todos os PCs. O host inicia uma partida e pressiona F8 → Host. Participantes ficam no menu principal e aceitam o convite Steam ou pressionam F8 → Join IP.

## <a id="known-issues"></a>Problemas conhecidos

- O transporte Steam não foi testado. Exige duas contas; LAN/IP foi testado.
- Animações de combate e alguns efeitos (tremor da tela, oscilação, partículas) aparecem apenas no host. Os participantes veem os resultados.
- Conectores de energia e esgoto do DLC Cities não são sincronizados.
- Apenas o host pode viajar entre tabuleiros; os participantes o acompanham.
- Todos devem executar os mesmos mods.

## <a id="next-steps"></a>Próximos passos

- Testar salas Steam com duas contas.
- Sincronizar conectores de Cities (`CardConnector`) e eventos de animação de combate/ataque.
- Jogar uma partida completa (continente → ilha → floresta) em modo cooperativo para alcançar `verified-playthrough`.
