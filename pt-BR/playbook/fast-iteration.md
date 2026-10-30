# <a id="fast-iteration-one-in-game-fix-round-in-a-minute-or-two"></a>Iteração rápida: uma rodada de correção dentro do jogo em um ou dois minutos

Uma rodada de correção de mod cooperativo consiste em alterar o código, colocá-lo em duas cópias do jogo em execução, levar o mundo ao estado que falhou, executar o teste e entender por que falhou. Manualmente, isso leva facilmente 15 minutos. Quase nada é tempo de CPU: são inicializações, recargas de salvamentos, fechamento de janelas, esperas fixas e investigação do problema. Uma linguagem mais rápida não ajuda. Eliminar cada espera, sim.

Uma rodada típica do projeto fnv-coop e o que substitui cada parte:

| Parte da rodada | Manualmente | Com as ferramentas do projeto |
|---|---|---|
| Recompilar o mod | 1,5 min | Compilar apenas o núcleo recarregável, com cache de compilação ([buildlock](../tools/buildlock/README.md)) |
| Reiniciar ambas as cópias | 4 min | Trocar o núcleo com os jogos em execução ([hotreload](../tools/hotreload/README.md)) |
| Carregar o salvamento, fechar janelas | 1 min | Salvamento preparado com as janelas já dispensadas ([scenarios](../tools/scenarios/README.md)) |
| Esperas fixas de sincronização | 2 min | Esperas por eventos que terminam cedo quando a sincronização para de avançar ([bots](../tools/bots/README.md)) |
| Caminhar até o local e preparar | 1 min | `--from-step N`: cada etapa consegue preparar seu próprio estado do mundo |
| O teste em si | 2 min | `--timescale` pelo multiplicador de tempo do jogo |
| Descobrir por que falhou | 3+ min | Motivos de falha que identificam a causa, visualização ao vivo lado a lado ([inspect](../tools/inspect/README.md)) e reprodução da falha fora do jogo ([flight](../tools/flight/README.md)) |

O objetivo é um ou dois minutos por rodada.

## <a id="the-pieces"></a>Os componentes

1. **Uma ponte para dentro do jogo.** Pequeno servidor RPC no processo do jogo, fila de solicitações consumida na thread principal e registro de métodos (executar comando de console, avaliar, aguardar condição, capturar estado, salvar, carregar, capturar tela). Todas as outras ferramentas se comunicam com o jogo por ela. Consulte [in-game-bridge.md](in-game-bridge.md) e [tools/bridge](../tools/bridge/README.md).
2. **Separe o mod em carregador e núcleo.** O carregador permanece no jogo; o núcleo é mapeado a partir de uma cópia em cache e pode ser trocado durante a execução. Os módulos salvam e restauram estado versionado durante a troca. Uma drenagem aguarda até que nenhuma thread execute código do núcleo. Todas as threads pertencentes ao núcleo precisam ser registradas, caso contrário a drenagem recusa indefinidamente. Consulte [hot-reloading-your-mod.md](hot-reloading-your-mod.md).
3. **Várias cópias de uma instalação.** Cópias por hardlinks, um conjunto de INI e portas por cópia, pares de host e cliente com portas próprias, sem exceder o número de pares permitido pela RAM livre ([gamepool](../tools/gamepool/README.md) `--pairs N`).
4. **Bots cujas ações se explicam.** Cada ação retorna `ok`, um `reason` e dados, com pré e pós-condições: "menu aberto", "arma guardada", "preso, faltam 4,2 m", "alvo íngreme demais". Uma execução malsucedida deve indicar o que corrigir sem abrir o jogo.
5. **Roteiros retomáveis.** Cada etapa tem uma preparação idempotente; assim, `--from-step` e `--only-step` saltam diretamente para a etapa que falha. Esperas de estabilização falham rapidamente, informando o motivo.
6. **Pares em paralelo.** Um executor por par como subprocessos, logs com prefixos, uma tabela PASS/FAIL (`tools/bots/run_parallel.py`).
7. **Reprodução fora do jogo.** `tools/flight/from_failure.py` transforma uma execução malsucedida dentro do jogo em caso de regressão fora dele: reduza o caso, corrija sem o jogo e preserve o teste.
8. **Variantes para tudo.** Cada comportamento tem um teste e uma variante de mutação, um seletor em tempo de execução que reintroduz o bug; o teste precisa falhar com ele ativado ([mutants](../tools/mutants/README.md)).

## <a id="rules-that-keep-the-loop-fast"></a>Regras para manter o ciclo rápido

- Nunca reinicie uma cópia para aplicar uma alteração do núcleo. Se uma cópia não puder trocar o núcleo, a ferramenta informa o motivo e termina com código 2; corrija isso uma vez e continue trocando.
- Nunca acrescente uma pausa fixa. Aguarde um evento e desista cedo quando nada se mover.
- Uma falha sem motivo é um bug no teste. Acrescente o motivo antes de corrigir o mod.
- Nunca altere cópias usadas por outro agente ou sessão. Obtenha primeiro a reserva [gameslot](../tools/gameslot/README.md).
