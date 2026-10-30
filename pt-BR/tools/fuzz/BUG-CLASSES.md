# <a id="co-op-sync-bug-classes"></a>Classes de bugs de sincronização cooperativa

Toda camada de sincronização cooperativa encontra o mesmo conjunto de bugs, em qualquer jogo. Esta página dá nome a eles, descreve sua aparência num jogo real, qual oráculo os detecta e qual variante de mutação do alvo de exemplo os ativa.

Uma **variante de mutação** é uma cópia de um trecho correto com um bug reintroduzido de propósito. Os oráculos só são confiáveis se falharem em todas as variantes. `python -I tools/fuzz/run_tests.py` verifica se todas são detectadas. Execute uma: `python -I tools/fuzz/run.py --bug two_owners --count 100`.

## <a id="the-oracles"></a>Os oráculos

| Oráculo | Condição necessária | Exigência ao seu alvo |
|---|---|---|
| `converge` | Após a recuperação da conexão e o fim do tráfego, todas as máquinas conectadas têm as mesmas entidades e valores do host, e os resumos por categoria são iguais | `view`, `digest`, `connected`, `quiescent` |
| `double_apply` | A mesma mensagem (mesmo ID) nunca é aceita duas vezes na mesma máquina | um `idem` em cada registro de aplicação |
| `multi_owner` | Cada ator tem um responsável por época, e as épocas nunca retrocedem | registro de responsabilidade (`logOwn`) |
| `stale_applied` | Nada desatualizado é aplicado: época anterior de responsabilidade, sequência que não avançou, atualização de quem não é responsável, solicitação anterior ao último carregamento do host | registro de aplicação com `epoch`, `seq`, `origin`, `worldEpoch` |
| `echo_adopted` | Uma máquina nunca aplica o eco da própria atualização como novidade | registro de aplicação com `origin` |
| `dup_thing` | Nenhuma máquina tem duas entidades com o mesmo ID de rede ou duas cópias da mesma identidade (posição de criação, item original) | `view` com `ident` |
| `repairs_after_quiescence` | Quando tudo está inativo, o número de ações de reparo ou ressincronização permanece zero | `repairs` |
| `not_quiescent` | Após a recuperação da conexão, o tráfego realmente para dentro do prazo (nada é reenviado para sempre) | `quiescent` |

`setup` não é um oráculo: é relatado quando o cenário cita um alvo ou bug ausente na compilação.

## <a id="the-catalogue"></a>O catálogo

| # | Classe | Variante (`--bug`) | Detectada por |
|---|---|---|---|
| 1 | Aplicação dupla | `no_idempotency` | `double_apply`, `converge` |
| 2 | Atualização perdida | `no_retransmit` | `converge`, `not_quiescent` |
| 3 | Eco obsoleto reaplica atribuição antiga e causa duplicatas | `stale_assignment_echo` | `dup_thing`, `converge` |
| 4 | Responsabilidade dupla | `two_owners` | `multi_owner` |
| 5 | Responsável anterior continua escrevendo | `stale_epoch_accepted` | `stale_applied` |
| 6 | Ordem das atualizações não imposta | `stale_seq_accepted` | `stale_applied` |
| 7 | Eco da própria atualização adotado | `echo_adopted` | `echo_adopted` |
| 8 | Identidade de criação duplicada | `spawn_dup` | `dup_thing` |
| 9 | Disputa por item atendida duas vezes | `pickup_dup` | `dup_thing` |
| 10 | Transferência recria o ator | `handoff_respawn` | `dup_thing` |
| 11 | Reparos nunca estabilizam | `digest_unstable` | `repairs_after_quiescence` |
| 12 | Solicitação anterior a um carregamento aceita | `no_world_epoch` | `stale_applied` |

### <a id="1-double-apply-no_idempotency"></a>1. Aplicação dupla (`no_idempotency`)

Um pacote chega duas vezes (duplicado pela rede ou pela lógica de reenvio), e a segunda cópia também é aplicada. No jogo: uma porta alterna duas vezes e termina fechada, um item é acrescentado duas vezes ao contêiner, dano é causado em dobro. Correção: dê a cada mensagem um ID (remetente e sequência) e descarte IDs já aplicados. A verificação precisa cobrir todos os caminhos da mensagem, incluindo reenvio e reparo.

### <a id="2-lost-update-no_retransmit"></a>2. Atualização perdida (`no_retransmit`)

Uma mensagem se perde numa conexão com perdas e nunca é reenviada; uma máquina mantém um valor antigo para sempre. A variante envia cada item do fluxo uma única vez. No jogo: indicador de missão que nunca chega ao convidado, eliminação não vista, porta fechada numa tela. Correção: confirme o que recebeu e reenvie o que não foi confirmado, ou envie resumos periódicos e repare diferenças. O oráculo mostra máquinas que nunca convergem ou tráfego que nunca para.

### <a id="3-stale-echo-re-applies-an-old-assignment-stale_assignment_echo"></a>3. Eco obsoleto reaplica atribuição antiga (`stale_assignment_echo`)

Classe por trás de um bug real: depois de solicitar uma atribuição, o responsável recebe apenas um eco do estado transportado na solicitação. Aplicar essa captura pode desfazer alterações feitas durante o trânsito. No bug real, um ator morto enquanto sua atribuição viajava foi ressuscitado; o responsável o tratou como novo, transferiu-o e repetiu o ciclo até centenas de cópias lotarem a área e o jogo falhar. Isso foi encontrado e corrigido no código de Skyrim Together Reborn, pull request #906 em [tiltedphoques/TiltedEvolution](https://github.com/tiltedphoques/TiltedEvolution/pull/906). A correção mantém o estado local de um ator pelo qual a máquina já responde e deixa o acompanhamento normal de alterações relatar diferenças.

Na variante: clientes preveem seus próprios golpes, e a mensagem de responsabilidade do host leva uma captura (vida, indicador de morte). Com o bug ativo, o novo responsável adota a captura, um ator já morto retorna e ele solicita sua redescoberta como novo; o host cria uma segunda cópia com a mesma identidade. O oráculo vê `dup_thing`. Exige uma pequena coincidência (morte e atribuição se cruzando na rede), então o teste dessa variante usa mais sementes que os demais.

Correção: resposta à sua própria solicitação não é novidade. Aceite apenas o que ainda não sabia (responsável, época), nunca estado que você alterou depois de enviar a solicitação.

### <a id="4-double-ownership-two_owners"></a>4. Responsabilidade dupla (`two_owners`)

Uma transferência não incrementa a época; duas máquinas podem se considerar responsáveis pelo ator na mesma época e ambas simulá-lo. No jogo: inimigo sofre correções bruscas de posição, luta contra dois jogadores ao mesmo tempo ou morre numa tela e permanece vivo na outra. Correção: cada concessão, transferência e liberação recebe uma nova época; só aceite atualizações da época atual e do responsável atual.

### <a id="5-old-owner-still-writes-stale_epoch_accepted"></a>5. Responsável anterior continua escrevendo (`stale_epoch_accepted`)

A autoridade aceita uma atualização de posição de uma máquina que deixou de ser responsável, ou de uma época anterior, e o ator volta a uma posição antiga. Correção: confira responsável e época antes de aplicar cada atualização.

### <a id="6-update-order-not-enforced-stale_seq_accepted"></a>6. Ordem das atualizações não imposta (`stale_seq_accepted`)

Dentro da mesma época, as atualizações são numeradas. Se uma antiga chega depois de outra mais recente (reordenação) e é aplicada, o ator retrocede. Correção: mantenha a última sequência por (ator, época) e descarte tudo que não for mais recente.

### <a id="7-echo-of-your-own-update-adopted-echo_adopted"></a>7. Eco da própria atualização adotado (`echo_adopted`)

O host retransmite seu movimento para todos, inclusive você; você o aplica como se outra pessoa tivesse movido seu personagem. Com latência, isso o puxa de volta à posição de instantes atrás. Correção: marque as transmissões com a origem e ignore as originadas por você.

### <a id="8-duplicate-spawn-identity-spawn_dup"></a>8. Identidade de criação duplicada (`spawn_dup`)

Dois jogadores acionam o mesmo encontro simultaneamente e ambos o criam, ou o host o cria duas vezes. No jogo: duas cópias do mesmo guarda ou NPC de missão duplicado. Correção: uma autoridade decide as criações, identificadas pela identidade (ponto de criação, não ID de rede). Rejeite uma segunda solicitação da mesma identidade.

### <a id="9-loot-race-served-twice-pickup_dup"></a>9. Disputa por item atendida duas vezes (`pickup_dup`)

Dois jogadores coletam o mesmo item no mesmo instante e ambos o recebem. A variante faz o host conceder uma cópia ao perdedor. Correção: o host escolhe um vencedor por item e responde ao perdedor com "contested".

### <a id="10-handoff-re-creates-the-actor-handoff_respawn"></a>10. Transferência recria o ator (`handoff_respawn`)

Ao transferir responsabilidade, o novo responsável (ou host) recria o ator com outro ID de rede, deixando o antigo para trás. No jogo: corpo fantasma ou inimigo duplicado após cada mudança de área. Correção: a transferência muda o campo de responsável da mesma entidade. Nunca cria ou destrói.

### <a id="11-repairs-never-settle-digest_unstable"></a>11. Reparos nunca estabilizam (`digest_unstable`)

O resumo calculado de cada lado não é a mesma função do mesmo estado (um arredonda a posição, outro calcula hash de um campo ignorado pelo parceiro). Cada verificação então falha e dispara ressincronização completa para sempre. No jogo: engasgos periódicos ou enxurrada de tráfego de ressincronização. Correção: calcule hash exatamente dos campos que ambos consideram compartilhados e teste que mundos iguais gerem resumos iguais. O oráculo exige contagem zero de reparos depois que tudo fica inativo.

### <a id="12-request-from-before-a-load-is-accepted-no_world_epoch"></a>12. Solicitação anterior a um carregamento aceita (`no_world_epoch`)

O host carrega um salvamento. Solicitações feitas no mundo antigo chegam depois e são aplicadas ao novo; um item coletado antes do carregamento é aplicado após ele. Correção: marque solicitações com uma época do mundo incrementada pelo host ao carregar e rejeite divergências (clientes reenviam o que ainda fizer sentido).

## <a id="add-your-own-twin"></a>Acrescente sua própria variante

1. Encontre um bug corrigido (ou um clássico desta lista) no seu núcleo de sincronização.
2. Coloque uma opção em volta da correção: indicador em tempo de execução definido por `Scenario::bugs`, ou `#ifdef` de compilação onde não couber indicador. Deve ficar desativada por padrão.
3. Registre o nome do bug em `TargetInfo::bugs` do alvo e leia-o na fábrica de alvos.
4. Execute `python -I tools/fuzz/run.py --bug <name> --count 200`. Precisa falhar com o oráculo esperado. Se passar, os oráculos não enxergam essa classe no seu alvo: acrescente o registro, as operações ou a categoria de resumo ausentes e tente novamente.
5. Salve uma reprodução minimizada com `--fixture <name>` e mantenha um teste que percorra sementes e exija detecção da variante (veja `tests/tests.cpp`, `twin(...)`).
