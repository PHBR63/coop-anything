# <a id="ownership-design"></a>Projeto de responsabilidade

Este é o conjunto completo de regras de `coop_ownership`, na ordem necessária para integrá-lo a um mod. A versão curta está no [README](README.md), e a história por trás do projeto em [playbook/actor-ownership.md](../../playbook/actor-ownership.md).

Adaptado do commit f57aa78 de fnv-coop ([github.com/cranebeaker/fnv-coop](https://github.com/cranebeaker/fnv-coop)).

## <a id="the-model"></a>O modelo

- Cada ator ativo tem **um responsável**: a máquina que executa sua IA e publica seu estado. Todas as outras exibem uma cópia dirigida pelas atualizações do responsável.
- Cada mudança de responsabilidade incrementa a **época** do ator. Uma atualização só é válida se levar a época atual e vier do responsável atual.
- O **host** (vaga 0) é o único que decide. Executa `OwnershipService`. Toda máquina, inclusive o host, executa uma `OwnershipView` que aplica as mensagens do host e avalia as atualizações.
- A biblioteca nunca envia nada. Retorna valores `OwnMsg`, que você transmite a todos. Nunca lê um relógio. Você fornece `nowMs`, permitindo aos testes usar um relógio virtual.

## <a id="messages"></a>Mensagens

| Tipo | Direção | Significado |
|---|---|---|
| `Grant` | host para todos | `owner` é responsável pelo ator na época `epoch`. Usado para o primeiro responsável, para assumir após a saída de um jogador e para cancelar uma transferência |
| `Transfer` | host para todos | Inicia a transferência de `prevOwner` para `owner`. Contém a época que o novo responsável terá. Essa época só entra em vigor em `Commit` |
| `Ack` | novo responsável para host | "Apliquei o último estado do responsável anterior, estou pronto". Contém a época de Transfer |
| `Commit` | host para todos | Transferência concluída: `owner` tem autoridade em `epoch` |
| `Release` | host para todos | Ninguém é responsável pelo ator em `epoch` (célula descarregada para todos, responsável saiu) |

`encode` / `decode` fornecem uma representação compacta em bytes (tipo, identificador varint, época varint, responsável, responsável anterior). `decode` recusa tipos desconhecidos, varints excessivamente longos ou grandes, entrada truncada e bytes extras no fim. Você pode usar seu próprio serializador.

## <a id="choosing-an-owner-pickowner"></a>Escolha do responsável (`pickOwner`)

Entrada: uma `Presence` por jogador (`connected`, `inCell`, `adjacent`, `distance`), responsável atual e indicação de que o ator ainda está dentro do tempo mínimo de permanência.

1. **Elegível** significa conectado e (na célula do ator ou em célula vizinha carregada).
2. Entre os elegíveis, o **host vence** se for elegível. Caso contrário, vence o mais próximo. Distâncias iguais são desempatadas pela menor vaga.
3. Sem responsável atual, ou com responsável desconectado: escolha o melhor jogador, ou ninguém.
4. Sem elegíveis, ou se o melhor já é o responsável: mantenha o responsável. Um ator cujo responsável se afastou, sem ninguém por perto, fica dormente com ele.
5. Responsável atual deixou de ser elegível (saiu da região da célula): troque imediatamente para o melhor.
6. Caso contrário, aplica-se **histerese**, evitando oscilações:
   - enquanto `minHoldMs` (padrão 1500) não tiver passado desde a última mudança, mantenha o responsável;
   - depois disso, o host assume assim que se tornar elegível;
   - outro jogador assume somente se estiver pelo menos `switchMargin` (padrão 25 por cento) mais próximo.

`distance` pode usar qualquer unidade; ela serve apenas para comparação.

## <a id="the-follower-exception"></a>A exceção de seguidores

`setRecruiter(actor, player, ...)` mantém um companheiro sob responsabilidade de quem o recrutou, aonde quer que vá, sem tempo mínimo nem teste de elegibilidade. A máquina do recrutador deve simular seu seguidor porque o ator sai da área de todos os outros jogadores quando o recrutador sai. `setRecruiter(actor, kNoPlayer, ...)` ou a saída do recrutador (`playerLeft`) encerra a exceção, e o ator volta às regras normais.

## <a id="handoff"></a>Transferência

```
host                old owner            new owner
 | Transfer(e+1) ---->|------------------->|
 |                    | keeps publishing   | applies the last state it has seen
 |                    | at epoch e; sends  |
 |                    | its final state    |
 |<------------------------------ Ack(e+1) |
 | Commit(e+1) ------>|------------------->|
                      | stops              | starts its AI, publishes at e+1
```

- Enquanto uma transferência está pendente, o responsável anterior continua sendo a autoridade: atualizações dele na época anterior são aceitas. Atualizações do novo responsável na nova época recebem `NotYetActive`.
- Somente uma transferência por ator de cada vez. `evaluate` não faz nada para um ator com transferência pendente.
- `onAck` aceita Ack somente do novo responsável pendente e na época pendente. Acks duplicados ou obsoletos retornam false e não alteram nada.
- `tick` força um resultado após `handoffTimeoutMs` (padrão 1000): se o novo responsável continua conectado, o host envia `Commit` mesmo assim (contado como confirmação forçada); caso contrário, envia `Grant` de volta ao anterior em uma época maior (contado como transferência abortada).
- O novo responsável não deve iniciar sua IA antes de receber `Commit`. O anterior deve parar sua IA ao perceber que `Transfer` se refere a ele, enviar seu estado final e parar de publicar em `Commit`. A biblioteca fornece os sinais (`handoffIncoming`, os tipos `OwnMsg`). Executar essas ações é sua responsabilidade.

## <a id="players-leaving-and-joining"></a>Saída e entrada de jogadores

`playerLeft(p, ...)`:

- Atores de `p` recebem `Release` (nova época) e são retornados, permitindo chamar `evaluate` novamente e atribuí-los a outra pessoa.
- Transferência pendente **para** `p` é cancelada. O responsável anterior recebe `Grant` em época maior, ou `Release` se também tiver saído.
- Transferência pendente **de** `p` é confirmada imediatamente, dando o ator ao novo responsável.
- Vínculos de recrutamento com `p` são removidos.

`snapshot(out)` produz a atribuição atual como mensagens `Grant` e `Release` para uma máquina entrando ou reconectando. Aplique-as a uma visão nova (primeiro `view.clear()`). Atores liberados são incluídos com sua época, mantendo obsoletas as mensagens atrasadas do responsável anterior após a reconexão.

`current(id, out)` responde por um ator, por exemplo quando uma máquina envia uma atualização `FutureEpoch` e o host quer corrigi-la.

## <a id="the-view"></a>A visão

`apply(msg)` retorna `Applied`, `Duplicate` ou `Stale`. Regras:

- Grant, Commit, Release: época mais antiga é `Stale`. Mesma época é `Duplicate` se o responsável for igual e `Stale` se diferir. Época mais nova é aplicada.
- Transfer: apenas registrado como pendente (o responsável ainda não muda). Repetições de Transfer e Transfers anteriores ao estado atual são `Duplicate` ou `Stale`.
- Ack é uma mensagem do lado do host, ignorada pelas visões.
- Um Commit recebido sem seu Transfer (perdido) ainda é aplicado.

Assim, mensagens podem ser duplicadas, reordenadas ou repetidas sem prejuízo. Isso elimina o bug de eco obsoleto descrito no guia.

`check(id, from, epoch)` retorna um veredito por atualização:

| Veredito | Significado | Ação |
|---|---|---|
| `Accept` | do responsável atual na época atual | aplicar |
| `NotOwner` | época correta, remetente errado | descartar |
| `StaleEpoch` | época mais antiga: um antigo responsável ainda está enviando | descartar |
| `FutureEpoch` | época mais nova que a conhecida: nossa visão está atrasada | descartar, consultar o host (`current`) |
| `NotYetActive` | remetente é o novo responsável de uma transferência não confirmada | descartar; será válida após Commit |
| `EchoOfSelf` | remetente é esta máquina: nossa própria publicação voltou | descartar |
| `UnknownActor` | sem registro | descartar ou consultar o host |

`mayPublish(id, epochOut)` só é true enquanto esta máquina for responsável. Marque a atualização com `epochOut`. `digest()` calcula hash de `(id, owner, epoch)` dos atores com responsável: visões iguais produzem digests iguais, permitindo comparar máquinas a baixo custo em testes ou verificações periódicas.

## <a id="things-to-know"></a>Pontos importantes

- **Salvar e carregar no host.** Um novo `OwnershipService` inicia as épocas em 1 novamente. Se puder carregar um mundo salvo no host, marque cada mensagem com um contador de sessão e descarte as de sessões anteriores, como faz o mundo simulado (consulte [../fakeworld](../fakeworld/README.md)). Épocas só ordenam mensagens dentro de uma sessão.
- **Vagas.** Um byte de indicadores de conexão, portanto 8 vagas. `PlayerId` 255 significa ninguém.
- **Atores mortos e desativados.** Chame `untrack` quando um ator desaparecer definitivamente (um `Release` é emitido se havia responsável). Atores dormentes sem jogador elegível mantêm o responsável.
- **Ordem de bytes do digest.** `digest()` calcula hash dos bytes nativos de identificadores de 32 bits; compare digests entre máquinas com a mesma ordem de bytes (os alvos comuns de PC e console são little endian).

## <a id="test-faults"></a>Falhas de teste

As opções `OwnershipFaults` (globais ao processo, definidas com `OwnershipFaultScope`, nunca em produção) recriam bugs conhecidos: `noEpochBump`, `acceptStaleEpoch`, `adoptEcho`, `transferNoAck`, `noHysteresis`, `followerIgnored`, `acceptNonOwner`. Cada uma tem um cenário em `tests/` que deve falhar quando a opção está ativa. Essa é a ideia das variantes de mutação: um teste que você nunca viu falhar é um teste em que não pode confiar.
