# <a id="fake-world-test-your-sync-without-the-game"></a>Mundo simulado: teste a sincronização sem o jogo

Um exemplo de padrão, não uma biblioteca pronta para encaixar: **modele as partes do mundo do jogo que são sincronizadas como dados simples em memória, execute várias cópias com relógio virtual em uma rede simulada com perdas e verifique se permanecem iguais.** Sem jogo, janela ou rede real. A execução completa dos 63 testes abaixo leva cerca de um segundo após a compilação.

Esta pasta é um exemplo completo. Modela atores, células, contêineres, itens, portas, pontos de criação, combate simples e etapas de missões; usa a [biblioteca de responsabilidade](../ownership/README.md) para decidir quem simula cada coisa e tem teste para cada bug cooperativo clássico. Copie, renomeie os tipos e adapte o mundo ao jogo. Leia a [página dos guias](../../playbook/fake-world-testing.md) para o método.

Adaptado do commit f57aa78 de fnv-coop (repositório público [github.com/cranebeaker/fnv-coop](https://github.com/cranebeaker/fnv-coop)), onde serve de ambiente de teste da camada de sincronização cooperativa de Fallout: New Vegas. Esta cópia foi tornada independente: serializador, transporte, RNG e código de sessão originais foram substituídos por implementações locais pequenas.

## <a id="what-is-in-it"></a>Conteúdo

| Arquivo | O que é |
|---|---|
| `include/fakeworld/types.h`, `world.h`, `src/world.cpp` | Mundo mantido por uma máquina: atores, contêineres, itens, portas, pontos de criação, jogadores, missões. Construção determinística por semente, efeitos, resumos por categoria e chave, salvar/carregar, importar/exportar reparos, auxiliares de duplicação e conservação |
| `effect.h`, `src/effect.cpp` | `Ref` (nome em um pacote de conteúdo) e pequeno conjunto de efeitos de história (etapa de missão, matar, mover, ativar, estado de porta, trancar, criar, responsável por companheiro) |
| `messages.h`, `src/messages.cpp` | Mensagens transmitidas pela camada ativa e codec do envelope |
| `machine.h`, `src/machine_*.cpp` | Um par simulado: réplica do mundo, visão de responsabilidade (host também executa o serviço), conexão confiável sobre transporte de datagramas com perdas, IA dos NPCs sob sua responsabilidade, combate, saque, contêineres, arbitragem de criação, resumos e reparos, estado completo para participantes, salvar/carregar no host |
| `cluster.h`, `src/cluster.cpp` | N máquinas em uma rede simulada com relógio virtual, entrada/saída, salvar/carregar no host, oráculos de invariantes e reprodução de execução gravada |
| `net.h`, `rng.h`, `wire.h` | Pequeno simulador de conexão com perdas (latência, variação, perda, duplicatas, inversão de um bit), RNG com semente e serializador com verificação de limites. Substitua pelos seus |
| `faults.h` | Seletores exclusivos de teste que recriam bugs clássicos (usados pelas variantes de mutação) |
| `tests/` | Testes de cenários, mundo, codec e variantes |

## <a id="embed-it"></a>Incorporação

Foi feito para ser lido e copiado. Para compilar como está:

```cmake
add_subdirectory(path/to/tools/fakeworld)            # also pulls in ../ownership
target_link_libraries(my_tests PRIVATE coop_fakeworld)
```

Menor execução útil:

```cpp
#include "fakeworld/cluster.h"
using namespace coop::fakeworld;

ClusterConfig cfg;
cfg.seed = 1; cfg.players = 3;                       // slot 0 is the host
cfg.link.minLatencyMs = 20; cfg.link.maxLatencyMs = 70; cfg.link.loss = 0.08;
cfg.machine.spec.seed = 1;                           // same seed, same world on every machine
Cluster c(cfg);
c.run(2000);                                         // two virtual seconds
c.machine(1).move(someCell, somePos);                // a local player action on machine 1
c.machine(2).attackActor(actorId, 45);
bool quiet = c.quiesce();                            // stop the AI, wait until nothing changes
auto always = c.checkAlways();                       // invariants that hold at any time
auto settled = c.checkQuiescent();                   // equality with the host after quiescence
```

Para adaptar ao jogo, siga as etapas dos guias: substitua os tipos do mundo pelos seus, mantenha a estrutura das máquinas (responsabilidade, conexão, resumos, reparos) e acrescente um oráculo e uma variante para cada bug encontrado.

## <a id="how-it-is-tested"></a>Como é testado

```
python -I tools/fakeworld/run_tests.py
```

Compila com CMake (um trabalho por vez, pasta de compilação no diretório temporário do sistema, salvo uso de `--build-dir`), executa todos os testes e verifica cada variante de mutação. Exibe `ALL OK` somente quando todos passam e todas as variantes são detectadas. Precisa de cmake e compilador C++17 (Visual Studio 2022 no Windows).

Cobertura da última execução: 63 testes (483 verificações) e 18 variantes de mutação, todos aprovados.

**Testes de cenário** (34): entrada e sincronização com 2, 3 e 4 jogadores (conexão perfeita e com perda, duplicação e corrupção); luta; transferência de responsabilidade quando o host se afasta; transferência entre convidados preservando o último estado do responsável anterior; ausência de oscilação entre jogadores igualmente próximos; companheiro que segue seu recrutador; disputa de saque (um vencedor, perdedores revertem); encontro criado uma vez; trancar, retirar, colocar e fechar contêiner preservando itens; portas, trancas e teletransportes; NPC de história que não morre em combate, mas pode morrer por efeito de história; mesclagem de etapa de missão e efeitos reenviados; host salva/carrega e convidado reconecta; corrupção silenciosa detectada e reparada por resumos; solicitação repetida de descarte cria um item; acertos falsificados e mal encaminhados; participante tardio recebe tabela de responsabilidade; quatro sessões aleatórias de 12 segundos virtuais com entradas, saídas, salvar/carregar e todos os tipos de ação; mesma semente produz mesmo mundo; execução gravada reproduz resumos idênticos; quadros inválidos; ordenação e eliminação de duplicatas na conexão confiável; reconexão de convidado.

**Testes de mundo e codec** (11): construção determinística, células e carregamento por proximidade, salvar/carregar, reparo de uma chave, efeitos (etapa é máximo, cadáveres, criação idempotente, indicadores persistentes de objetos), ida e volta dos efeitos pela rede, detecção de duplicatas, codec de todos os tipos de mensagem, dados inválidos, inversões de bits e codec de ações.

**Oráculos** executados pelo conjunto após cada cenário: um responsável por época, um controlador de IA por ator, nenhuma atualização obsoleta aceita, nada aplicado duas vezes, nenhum ator ou item duplicado, todas as máquinas iguais ao host após estabilização (resumos e estado exato dos atores), mesma tabela de responsabilidade em toda parte, itens conservados e nenhum reparo após estabilização.

**Variantes de mutação.** Cada variante ativa uma falha e executa o cenário que a protege. Só passa se o cenário passar sem a falha e falhar com ela.

| Variante | Falha ativada |
|---|---|
| `own_transfer_no_ack`, `own_no_hysteresis`, `own_follower_ignored` | falhas de transferência, oscilação e seguidores da biblioteca de responsabilidade, vistas pelo conjunto inteiro |
| `no_dedupe` | conexões e identificadores deixam de descartar duplicatas; mensagens reenviadas são aplicadas duas vezes |
| `hit_no_validation` | responsável pela vítima aplica qualquer acerto, falsificado ou não |
| `hit_by_non_owner` | máquina sem responsabilidade pelo ator aplica um acerto dirigido a ele |
| `pickup_no_arbitration` | host concede toda solicitação de coleta |
| `pickup_no_rollback` | perdedor de disputa de coleta mantém o item |
| `spawn_no_arbitration` | host cria um encontro para cada máquina que faz o sorteio |
| `loot_per_machine` | cada máquina sorteia sozinha o saque do cadáver |
| `pick_per_machine` | cada máquina faz sua própria escolha por nível |
| `container_no_lock` | contêiner pode ficar aberto para dois jogadores simultaneamente |
| `named_killable` | combate pode matar NPC de história |
| `no_session_epoch` | mensagens anteriores ao carregamento do host são aplicadas depois dele |
| `heal_disabled` | divergências de resumos são detectadas, mas nunca reparadas |
| `drop_no_idempotency` | solicitação de descarte reenviada cria um segundo item |
| `join_no_ownership` | estado completo de um participante omite tabela de responsabilidade |
| `owner_keeps_publishing` | responsável anterior continua publicando (junto de uma visão que aceita épocas antigas) |

## <a id="changes-from-the-original"></a>Alterações em relação ao original

- Desacoplado do núcleo fnv-coop: serializador (`wire.h`, sem tabela compartilhada de strings), simulador de conexão (`net.h`, sem limites de banda ou modelador substituível), RNG e tipo de efeito são locais; o código de responsabilidade vem de `../ownership`.
- Nomes neutros: namespace `coop::fakeworld`, `Ref` em vez de referência a formulário, pacote de conteúdo e identificadores inventados. Nada é dado de jogo.
- A lista de efeitos é o pequeno subconjunto demonstrável pelo modelo. Sessões de história, política de missões, captura de efeitos de um jogo e transporte real não fazem parte deste exemplo.
- Dois cenários precisaram de correção para passar neste port:
  - `handoffKeepsLastState` contava estados finais no segundo convidado desde o início; uma transferência anterior (host para convidado) o satisfazia e a variante `own_transfer_no_ack` continuava aprovada. Agora conta somente o que chega após começar a segunda transferência, e a variante detecta a falha.
  - `fightScenario` em conexão com perdas agora permite alguns reparos de resumos (no máximo 8), como as sessões aleatórias. Um ator em movimento pode ficar dos dois lados do limite de uma faixa de posição em dois relatos consecutivos numa conexão com perdas; o reparo então faz seu trabalho.

Licença: MIT, como o restante deste repositório.
