# <a id="actor-ownership-with-epochs"></a>Responsabilidade sobre atores com épocas

Uma pequena biblioteca C++17 que decide **qual máquina simula cada ator** em um mod cooperativo e rejeita atualizações de máquinas que já não são responsáveis por ele. Dois arquivos de cabeçalho e código-fonte, sem dependências, código de rede ou relógio. Você informa quem está perto de quê, e ela informa o que enviar.

Ela existe porque o mesmo bug reaparece em todo mod cooperativo que compartilha NPCs: duas máquinas se consideram responsáveis pelo mesmo ator, ou uma mensagem do responsável anterior chega atrasada e prevalece. As épocas resolvem isso. Leia a [página do guia](../../playbook/actor-ownership.md) para entender os motivos e [DESIGN.md](DESIGN.md) para todas as regras e casos extremos.

Adaptada do commit f57aa78 de fnv-coop (repositório público [github.com/cranebeaker/fnv-coop](https://github.com/cranebeaker/fnv-coop)), onde controla a responsabilidade sobre NPCs no modo cooperativo de Fallout: New Vegas. As partes específicas do jogo foram removidas; este é o núcleo genérico.

## <a id="what-you-get"></a>O que você recebe

| Componente | Executado em | Função |
|---|---|---|
| `coop::OwnershipService` | somente no host | Escolhe um responsável por ator (jogador mais próximo, preferência pelo host, histerese, companheiros seguem quem os recrutou), executa transferências e emite `OwnMsg` |
| `coop::OwnershipView` | todas as máquinas, incluindo o host | Aplica `OwnMsg` e responde se a máquina pode publicar o ator e se deve aceitar a atualização |
| `coop::OwnMsg` + `encode` / `decode` | transmissão em rede | Cinco tipos de mensagem (Grant, Transfer, Ack, Commit, Release) e um formato compacto opcional em bytes |
| `coop::OwnershipFaults` | somente nos testes | Opções que reproduzem bugs conhecidos, usadas pelas variantes de mutação |

## <a id="embed-it"></a>Integre ao projeto

Copie `include/coop/` e `src/ownership.cpp` para o projeto ou use CMake:

```cmake
add_subdirectory(path/to/tools/ownership)      # tests are off when it is not the top level project
target_link_libraries(my_mod PRIVATE coop_ownership)
```

O loop do host, resumidamente:

```cpp
#include "coop/ownership.h"
using namespace coop;

OwnershipService svc;                    // host only
OwnershipView view(kHostPlayer);         // every machine has one, with its own slot number
svc.playerJoined(kHostPlayer);

OwnershipService::Out out;
svc.track(actorId, presence, nowMs, out);        // presence: who is near this actor right now
svc.tick(nowMs, out);                            // once per host tick, drives handoff timeouts
for (const OwnMsg& m : out) { view.apply(m); broadcast(m); }
```

Em cada máquina, ao enviar ou receber atualizações de atores:

```cpp
OwnerEpoch epoch;
if (view.mayPublish(actorId, epoch)) send(update, epoch);        // only the owner may publish

switch (view.check(actorId, fromPlayer, updateEpoch)) {          // on receive
    case UpdateVerdict::Accept: applyUpdate(); break;
    case UpdateVerdict::FutureEpoch: askHostForCurrentOwner(); break;
    default: drop(); break;                                      // stale, not owner, echo, unknown
}
```

Quando `view.handoffIncoming(id, epoch)` retorna verdadeiro, você é o novo responsável em uma transferência: aplique o último estado recebido do responsável anterior e envie um `Ack` ao host. A página do guia explica todo o protocolo de confirmação.

Limites: até 8 posições de jogador; a posição 0 é o host. A biblioteca não é segura para múltiplas threads (use uma instância por thread). IDs e épocas têm 32 bits.

## <a id="how-it-is-tested"></a>Como é testada

```
python -I tools/ownership/run_tests.py
```

Compila com CMake (um trabalho por vez, pasta de compilação no diretório temporário do sistema, a menos que você passe `--build-dir`), executa todos os testes e verifica todas as variantes de mutação. Exibe `ALL OK` somente se todos os testes passarem e todas as variantes forem detectadas. Exige cmake e um compilador C++17 (Visual Studio 2022 no Windows).

Cobertura da última execução: 30 testes (134 verificações) e 7 variantes de mutação, todos aprovados.

- Testes das regras de escolha do responsável (preferência pelo host, mais próximo, empates, histerese, tempo de permanência).
- Testes de transferência: épocas e confirmação final, confirmação forçada por tempo esgotado, saída no meio da transferência, capturas de estado para novos participantes.
- Testes da visão: mensagens idempotentes e independentes de ordem, todos os vereditos de atualização, ida e volta no formato de rede, entradas truncadas e inválidas.
- Testes de cenários: entradas e saídas aleatórias com confirmações perdidas e mensagens reordenadas e duplicadas (um responsável por época, épocas nunca retrocedem e todas as visões terminam iguais à do host), repetição de atribuição antiga (eco obsoleto), saída e retorno, ausência de alternância instável, companheiros e manutenção da autoridade do responsável anterior até Ack e Commit.

**Variantes de mutação.** Cada variante ativa uma falha de `OwnershipFaults` e executa o cenário que a verifica. Ela passa somente se o cenário funcionar sem a falha e falhar com ela.

| Variante | Falha ativada |
|---|---|
| `own_no_epoch` | mudanças mantêm a época anterior |
| `own_stale_epoch` | visões aceitam épocas e mensagens mais antigas |
| `own_adopt_echo` | repetição de uma atribuição antiga sobrescreve uma mais recente |
| `own_transfer_no_ack` | transferência é confirmada sem esperar pelo novo responsável |
| `own_no_hysteresis` | responsabilidade alterna de forma instável conforme a distância |
| `own_follower_ignored` | companheiros ficam sob responsabilidade de quem estiver mais perto |
| `own_accept_non_owner` | visões aceitam atualizações de qualquer jogador |

## <a id="changes-from-the-original"></a>Alterações em relação ao original

- Renomeada para o namespace `coop` e desvinculada do formato de rede, dos tipos e do código de sessão de fnv-coop. O formato de rede agora é `encode` / `decode` nesta biblioteca.
- Os três cenários de conjunto de máquinas (sem alternância instável, seguidor, transferência que mantém o último estado) foram reescritos para rodar diretamente no serviço e nas visões, dispensando um mundo simulado nos testes da biblioteca. As versões originais desses cenários continuam em [../fakeworld](../fakeworld/README.md).
- `OwnershipView::check` e a lógica do serviço não foram alterados.

Licença: MIT, como o restante deste repositório.
