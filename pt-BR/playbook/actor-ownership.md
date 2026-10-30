# <a id="actor-ownership-with-epochs"></a>Responsabilidade sobre atores com épocas

Se o mod cooperativo compartilha NPCs e criaturas entre jogadores, é necessária uma regra para **quem executa cada um**. Sem ela, atores brigam consigo mesmos, tremem, somem ou se multiplicam. Esta página apresenta a regra que funcionou, a classe de bug que ela evita e a pequena biblioteca que a implementa.

Código e testes: [tools/ownership](../tools/ownership/README.md) (a biblioteca) e [tools/fakeworld](../tools/fakeworld/README.md) (mundo simulado que a utiliza). Relacionados: [effect-capture-story-sync.md](effect-capture-story-sync.md), [fake-world-testing.md](fake-world-testing.md), [fuzzing-coop-sync.md](fuzzing-coop-sync.md), [automated-qa.md](automated-qa.md).

## <a id="why"></a>Por quê

Um jogo para um jogador executa a IA de todos os atores na sua máquina. No modo cooperativo, se cada máquina executar a IA de todos, as cópias divergem e cada uma decide atacar, vagar, morrer ou coletar itens por conta própria. Se nenhuma executar, os atores congelam. A solução para a qual todos os mods funcionais convergiram:

- **Exatamente uma máquina simula cada ator.** Essa máquina é a **responsável**. Sua IA é executada.
- Todas as outras exibem o ator a partir das atualizações da responsável, com a IA local desse ator desligada.
- A responsável publica posição, animação, vida e morte. Ninguém mais pode fazê-lo.

Essa resposta é simples. Mantê-la verdadeira enquanto os jogadores caminham, entram, saem e perdem pacotes é a parte difícil, onde surgem os bugs.

## <a id="the-rules"></a>As regras

1. **Uma responsável por ator, definida por uma máquina.** O host decide. Clientes nunca escolhem responsáveis.
2. **Prefira o host, depois o jogador mais próximo.** O host normalmente tem o estado mais estável. Entre convidados, vence o mais próximo; um jogador é candidato se estiver na célula do ator ou em uma célula vizinha carregada.
3. **Toda mudança incrementa uma época.** Época é um contador guardado com o responsável: concessão, transferência e liberação o incrementam. Apenas "responsável" não basta; é necessário "responsável na época 7".
4. **Uma atualização só é válida se vier da responsável na época atual.** Todo o restante é descartado: época anterior (antigo responsável ainda enviando), época posterior (nossa visão está atrasada: perguntar ao host), remetente que não é o responsável e nossa própria atualização retornando.
5. **Mensagens de responsabilidade são idempotentes e independentes de ordem.** Aplicar a mesma mensagem duas vezes, ou uma antiga depois de uma nova, não muda nada. A época é o único elemento que as ordena.
6. **A transferência é uma negociação, não uma troca instantânea.** A antiga responsável mantém a autoridade até que a nova receba seu último estado: `Transfer` (host), depois a antiga envia o estado final, a nova o aplica e envia `Ack`, depois `Commit` (host). Só após o Commit a nova responsável executa a IA. Um limite de espera permite ao host forçar o resultado, para um Ack perdido não paralisar o ator.
7. **Evite oscilações.** Dois jogadores quase à mesma distância transfeririam o ator de um para outro a cada quadro. Mantenha o responsável por um tempo mínimo e só transfira quando um concorrente estiver claramente mais perto (a biblioteca usa 1,5 segundo e 25%).
8. **Pessoas saem.** Quando um responsável sai, seus atores são liberados e atribuídos a outro em uma época maior. Transferência para alguém que saiu é cancelada. Transferência de alguém que saiu é concluída imediatamente.
9. **Quem entra recebe a tabela.** Uma máquina que entra recebe o responsável e a época atuais de cada ator, incluindo os liberados, para ainda reconhecer como obsoletas mensagens tardias de um responsável antigo.

## <a id="the-follower-exception"></a>A exceção dos seguidores

Companheiros quebram a regra 2. Um seguidor precisa ser simulado pelo jogador que o recrutou, onde quer que ele vá. Se o responsável fosse o jogador mais próximo, o ator seria transferido a cada afastamento do recrutador e perderia o comportamento de seguir em cada transferência. Portanto:

- Enquanto um ator tiver recrutador, o recrutador é responsável por ele. Sem tempo mínimo de retenção nem teste de distância.
- Quando o recrutador se desconecta ou dispensa o ator, as regras normais voltam a valer.

A biblioteca oferece isso por `setRecruiter`. O mundo simulado tem um teste em que um companheiro segue seu recrutador para uma célula distante e mantém o mesmo responsável.

## <a id="the-bug-class-stale-and-echoed-assignments"></a>A classe de bug: atribuições obsoletas e retornadas como eco

Todo sistema de responsabilidade acaba encontrando esse problema. O formato:

> Uma máquina recebe uma declaração **mais antiga** sobre quem é responsável por um ator, ou uma cópia antiga do estado do ator, e a trata como verdade.

Isso ocorre por ecos (o host devolve uma solicitação), retransmissões e repetições, cliente respondendo a partir de cache ou resposta a uma pergunta feita antes de o mundo mudar. Como nada na mensagem indica sua idade, quem recebe não consegue distinguir.

Exemplo real documentado publicamente: **Skyrim Together Reborn, pull request [#906](https://github.com/tiltedphoques/TiltedEvolution/pull/906)** ("Fix rapid NPC duplication caused by owners applying stale assignment state"). Como a PR descreve, NPCs podiam se multiplicar rapidamente em algumas áreas, às vezes até travar o jogo. Uma responsável reconciliava um ator recém-atribuído com dados do servidor que apenas repetiam a solicitação original, podendo estar desatualizados. Um NPC morto enquanto a solicitação aguardava era recriado, reiniciando sua referência e recarregando seu modelo. A responsável então liberava a entidade e tratava o ator como novo, repetindo isso a cada ida e volta. Outros jogadores recebiam as entidades liberadas e criavam cópias, aumentando continuamente a contagem. Crédito ao autor por encontrar e corrigir o problema e explicá-lo claramente.

O que aprendemos com isso:

- **Marque a responsabilidade com uma época** e compare épocas em toda mensagem. Uma declaração sobre época anterior é descartada, seja qual for o conteúdo. Assim, uma concessão antiga repetida não sobrescreve o responsável mais recente.
- **Nunca reconstrua um ator durante a transferência.** Não recrie nem redefina referência ou modelo. A nova responsável assume o ator existente a partir do último estado da antiga.
- **Torne a transferência idempotente**, para um Transfer ou Commit repetido não fazer nada na segunda vez.
- **Teste isso deliberadamente.** Reaplique uma atribuição antiga a uma visão e verifique se ela não prevalece; repita atualizações da responsável anterior e confira a rejeição. A biblioteca contém esse teste e uma variante de mutação (ela desativa a ordenação, e o teste precisa falhar).

## <a id="how-to-use-the-library"></a>Como usar a biblioteca

A biblioteca nunca altera sua rede ou relógio. Você fornece fatos; ela retorna mensagens.

No host:

```cpp
#include "coop/ownership.h"
using namespace coop;

OwnershipService svc;
OwnershipView hostView(kHostPlayer);
svc.playerJoined(kHostPlayer);                 // and for every guest that connects

OwnershipService::Out out;
svc.track(actorId, whoIsNear(actor), nowMs, out);        // when the actor appears
svc.evaluate(actorId, whoIsNear(actor), nowMs, out);     // every few hundred ms per actor
svc.setRecruiter(actorId, recruiterSlot, whoIsNear(actor), nowMs, out);   // companions
svc.tick(nowMs, out);                                    // every host tick
for (const OwnMsg& m : out) { hostView.apply(m); broadcast(m); }
```

`whoIsNear` preenche um `Presence` por jogador: conectado, na célula do ator, em uma célula vizinha e distância. Quando um convidado entra, envie `svc.snapshot(...)`. Quando sai, chame `svc.playerLeft(slot, nowMs, out)` e execute novamente `evaluate` para os órfãos retornados.

Em todas as máquinas, incluindo o host:

```cpp
// receiving ownership messages
view.apply(msg);

// before publishing an actor's state
OwnerEpoch epoch;
if (view.mayPublish(id, epoch)) send(stateUpdate, epoch);

// on receiving a state update
switch (view.check(id, fromSlot, updateEpoch)) {
    case UpdateVerdict::Accept: applyState(); break;
    case UpdateVerdict::FutureEpoch: askHostForOwner(id); break;
    default: break;      // stale, not the owner, our own echo, not yet active, unknown
}

// during a handoff
OwnerEpoch e;
if (view.handoffIncoming(id, e)) { applyLastStateYouHave(); sendAckToHost(id, e); }
```

E as duas responsabilidades do lado do jogo que a biblioteca não pode cumprir por você:

- **Responsável antiga**, quando um `Transfer` indicar você como responsável anterior: interrompa a IA, envie seu último estado marcado como "final" e mantenha-o como autoridade até `Commit`.
- **Nova responsável**, somente depois de `Commit`: ative a IA do ator e comece a publicar na nova época.

Se o host puder carregar um mundo salvo, acrescente um contador de sessão a todas as mensagens e descarte as da sessão anterior: as épocas recomeçam em 1 em um novo serviço. Consulte [DESIGN.md](../tools/ownership/DESIGN.md) para detalhes e casos-limite.

## <a id="proving-it"></a>Comprovação

```
python -I tools/ownership/run_tests.py
python -I tools/fakeworld/run_tests.py
```

O primeiro executa testes de regras, transferência e visão, mudanças aleatórias de participantes com confirmações perdidas e mensagens reordenadas e duplicadas, o teste de eco obsoleto e sete variantes de mutação. O segundo aplica as mesmas ideias em um mundo simulado completo com enlaces sujeitos a perdas, onde as regras de responsabilidade definem quem simula o quê. Ambos exibem `ALL OK` somente quando todas as variantes são detectadas. Depois de integrar a biblioteca ao jogo, adicione estas verificações aos testes: nenhum ator controlado por duas máquinas, nenhuma época retrocedendo e nenhum dado de época anterior aplicado. [fake-world-testing.md](fake-world-testing.md) mostra como fazer.
