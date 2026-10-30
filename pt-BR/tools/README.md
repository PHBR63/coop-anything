# <a id="tools"></a>Ferramentas

Há dois tipos de ferramentas aqui:

- **Ferramentas centrais:** `build_directory.py` (valida `data/directory.yaml` e gera `DIRECTORY.md`) e `mcp/` (o [servidor MCP](../playbook/mcp.md)).
- **Ferramentas de teste de sincronização:** ferramentas independentes de jogo para criar e testar sincronização cooperativa, listadas abaixo. Vêm do projeto [fnv-coop](https://github.com/cranebeaker/fnv-coop), com as particularidades do jogo movidas para arquivos de configuração, adaptadores e pastas `examples/fnv/`.

## <a id="sync-test-tools"></a>Ferramentas de teste de sincronização

| Ferramenta | O que faz | Linguagem | Guia |
|---|---|---|---|
| [chaos](chaos/README.md) | Retransmissor UDP entre host e clientes de qualquer jogo: atraso, variação de latência, perda, rajadas, reordenação, duplicação, limites de banda e interrupções em um sentido. Perfis de `lan` a `hell`, alterados ao vivo. Uma implementação equivalente C++ somente em cabeçalho toma as mesmas decisões em testes dentro do processo. | Python, cabeçalho C++ | [network-chaos-testing](../playbook/network-chaos-testing.md) |
| [flight](flight/README.md) | Gravador de eventos para o mod (registros `.cofr` de mensagens, transações, responsabilidade e digests de estado), com analisador que alinha 2 a 4 máquinas, encontra a primeira divergência até o agrupamento, chave e valor, reduz a execução e escreve um teste de regressão e relatório HTML. | C++, Python | [desync-hunting](../playbook/desync-hunting.md) |
| [fuzz](fuzz/README.md) | Sessões de 2 a 4 jogadores com sementes reproduzíveis em um enlace com perdas, verificadas por oráculos de invariantes (convergência, nenhuma aplicação dupla, um responsável por época, nenhuma duplicata ou estado obsoleto, reparos cessam). Reduz sementes que falham. Adapte seu núcleo de sincronização à interface de alvo. | C++, CLI Python | [fuzzing-coop-sync](../playbook/fuzzing-coop-sync.md) |
| [ownership](ownership/README.md) | Qual máquina simula cada ator: épocas, concessão, transferência, liberação, histerese, exceção de seguidor, rejeição de estados obsoletos e ecos. Sem dependências. | Biblioteca C++ | [actor-ownership](../playbook/actor-ownership.md) |
| [fakeworld](fakeworld/README.md) | Mundo de exemplo em memória (atores, células, contêineres, portas, criação de entidades, combate, etapas de missões) com relógio virtual, para testar sincronização sem o jogo. | C++ | [fake-world-testing](../playbook/fake-world-testing.md) |
| [gameslot](gameslot/README.md) | Trava com prazo de concessão para permitir somente uma frente de execução de cópias do jogo por vez, com proteção de RAM e encerramentos limitados aos processos iniciados por você. | Python | [multi-instance-testing](../playbook/multi-instance-testing.md) |
| [gamepool](gamepool/README.md) | Instalações isoladas com hardlinks, conjunto de cópias já inicializadas e reutilizáveis, inicializações minimizadas de baixo custo, sondas de prontidão e leitura de logs de falha, a partir de uma configuração JSON por jogo. | Python | [multi-instance-testing](../playbook/multi-instance-testing.md) |
| [scenarios](scenarios/README.md) | Estados iniciais JSON com verificações; reinicializa sem encerrar e só recarrega um salvamento quando necessário. | Python | [bots-and-playbooks](../playbook/bots-and-playbooks.md) |
| [bots](bots/README.md) | Roteiros cooperativos com vários bots (luta, disputa por itens, contêiner, porta, diálogo, voto de consentimento, sincronização de missão, viagem rápida, transferência de responsabilidade, salvar e reconectar após carregar), com comparação de estado após cada etapa, usando um adaptador de ações escrito para seu jogo. | Python | [bots-and-playbooks](../playbook/bots-and-playbooks.md) |
| [bridge](bridge/README.md) | Um servidor RPC no processo do jogo: modelo C++ somente em cabeçalho, com fila de solicitações na thread principal e registro de métodos (exec, eval, waitFor, state, save, load, screenshot, events), além de cliente Python por pipe nomeado ou TCP. | Cabeçalho C++, Python | [in-game-bridge](../playbook/in-game-bridge.md) |
| [inspect](inspect/README.md) | Tabela ao vivo somente de leitura de todas as cópias lado a lado (menu, arma, saúde, posição, responsáveis, contadores de sincronização, dessincronizações recentes), com colunas definidas por uma lista de campos por jogo. | Python | [in-game-bridge](../playbook/in-game-bridge.md) |
| [hotreload](hotreload/README.md) | DLL carregadora permanente e núcleo recarregável: estado versionado durante a troca, drenagem que aguarda threads do núcleo, identificadores de compilação e recusa limpa com código de saída 2. | C++, Python | [hot-reloading-your-mod](../playbook/hot-reloading-your-mod.md) |
| [mutants](mutants/README.md) | Estrutura de variantes de mutação: chave em tempo de execução sem custo (`COOP_MUT`) para C++ e Python e executor que informa variantes não detectadas, que acionam o teste errado ou quebram a compilação. | Cabeçalho C++, Python | [fast-iteration](../playbook/fast-iteration.md) |
| [buildlock](buildlock/README.md) | Trava com prazo de concessão para árvore de compilação compartilhada (recuperação de trava obsoleta pelo pid) e controlador CMake com sccache opcional. | Python | [fast-iteration](../playbook/fast-iteration.md) |
| [animcheck](animcheck/README.md) | Compara animação, pose, arma e orientação entre máquinas e detecta deslizamento, pose em T, flutuação, afundamento, tremor, correções bruscas de posição, travamentos e falhas de pose de morte. Lê um fluxo de sondagem JSON. | Python | [animation-sync-checks](../playbook/animation-sync-checks.md) |

O projeto de sincronização da história (capturar efeitos no host em vez de reexecutar scripts) está em [effect-capture-story-sync](../playbook/effect-capture-story-sync.md).

## <a id="running-the-tests"></a>Execução dos testes

Cada ferramenta tem um comando que executa seus testes e variantes de mutação (versões propositalmente defeituosas que os testes precisam detectar) e exibe `ALL OK`:

```
python -I tools/chaos/run_tests.py
python -I tools/test_all.py            # every tool
python -I tools/test_all.py fuzz bots  # some of them
```

O segundo comando executa todas as ferramentas; o terceiro seleciona apenas algumas.

As ferramentas C++ usam CMake e exigem um compilador C++17 (foram compiladas com Visual Studio 2022 no Windows). As ferramentas Python usam somente a biblioteca padrão. Nenhum teste inicia um jogo real: usam simulações e processos substitutos.

Use a skill `coop-sync-testing` para o agente escolher a ferramenta adequada.
