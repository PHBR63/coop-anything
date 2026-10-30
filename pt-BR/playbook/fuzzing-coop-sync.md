# <a id="fuzzing-co-op-sync-find-the-desync-before-your-friends-do"></a>Fuzzing da sincronização cooperativa: encontre a dessincronização antes dos seus amigos

A maioria dos bugs de sincronização cooperativa não é simplesmente código errado: são duas coisas acontecendo ao mesmo tempo. Dois jogadores saqueiam o mesmo baú. Um pacote chega duas vezes. O responsável por um inimigo muda enquanto o anterior ainda transmite. O host carrega um salvamento com uma solicitação em trânsito. Jogar não vai explorar todos esses casos, mas um computador pode tentar milhares por minuto contra a lógica de sincronização, sem executar o jogo.

A ferramenta fica em [tools/fuzz/](../tools/fuzz/README.md). Esta página descreve o método. O passo a passo para adaptar seu código está em [tools/fuzz/GUIDE.md](../tools/fuzz/GUIDE.md), e a lista de bugs em [tools/fuzz/BUG-CLASSES.md](../tools/fuzz/BUG-CLASSES.md).

## <a id="1-what-a-fuzzer-for-sync-is"></a>1. O que é um fuzzer de sincronização

1. **Uma sessão simulada.** De 2 a 4 cópias do núcleo de sincronização em um processo, relógio virtual e uma rede com falhas entre elas (atraso, variação de latência, perda, duplicação, corrupção).
2. **Um plano aleatório, a partir de uma semente.** Lista de ações temporizadas dos jogadores: mover, atacar, pegar, soltar, criar um encontro, abrir porta, entrar, sair, salvar e carregar no host, piorar a conexão, reproduzir mensagem antiga. A mesma semente produz o mesmo plano em todas as máquinas.
3. **Restabelecer, esperar, comparar.** Após a última ação, a conexão fica perfeita, tudo congela e a estrutura de teste espera até não haver nada em trânsito. Então compara o que cada máquina considera verdadeiro.
4. **Oráculos.** Regras que precisam valer, verificadas no estado final e no log de tudo que cada máquina aplicou.
5. **Um redutor.** Quando uma regra é violada, a estrutura remove ações até restar o menor plano que ainda provoca a falha. Uma falha de 400 ações normalmente se reduz a 3 a 10. Esse é o relato do bug.

Como tudo usa tempo virtual em um processo, uma sessão leva milissegundos, uma falha é reproduzida exatamente e um agente pode executar o processo em ciclo após cada alteração.

## <a id="2-the-rules-worth-checking"></a>2. Regras que vale a pena verificar

| Regra | Significado simples |
|---|---|
| Convergência | Em repouso, todas as máquinas mostram o mesmo mundo do host |
| Nada aplicado duas vezes | Um pacote duplicado ou reenvio não altera nada uma segunda vez |
| Um responsável por ator em cada época | Duas máquinas nunca simulam o mesmo ator na mesma época, e épocas só aumentam |
| Nada obsoleto aplicado | Épocas antigas, números de sequência antigos, máquinas sem responsabilidade e solicitações anteriores ao carregamento de um salvamento são rejeitados |
| Sem eco | Uma máquina não adota o eco da própria atualização |
| Sem duplicatas | Não há dois atores ou itens com a mesma identidade (mesmo local de criação, mesmo item original) |
| Reparos se estabilizam | Quando tudo está em repouso, contadores de ressincronização e reparo permanecem em zero |
| Repouso significa repouso | Após restabelecer a conexão, o tráfego cessa por conta própria |

Essas são as regras em torno das quais o fuzzer foi construído. O catálogo, com a manifestação de cada bug em um jogo, está em [BUG-CLASSES.md](../tools/fuzz/BUG-CLASSES.md). Um caso é documentado publicamente: um eco obsoleto de atribuição fazia o responsável ressuscitar um inimigo morto e redescobri-lo como novo, repetidamente, até centenas de cópias derrubarem o jogo. Foi encontrado e corrigido no código de Skyrim Together Reborn, [TiltedEvolution pull request 906](https://github.com/tiltedphoques/TiltedEvolution/pull/906).

## <a id="3-how-to-use-it-on-a-new-game"></a>3. Como usar em um novo jogo

1. **Permita executar o núcleo N vezes em um processo.** Sem globais, com tempo e transporte injetados e aleatoriedade com semente. Se estiver acoplado ao motor, separe as chamadas ao motor atrás de uma interface pequena e forneça ao fuzzer um mundo simulado. É a maior etapa e beneficia todos os outros testes também.
2. **Adapte-o como alvo.** Copie o esqueleto de 190 linhas, mapeie operações genéricas ao jogo, relate cada mensagem aplicada ou rejeitada e responda a `view`, `digest`, `quiescent` e `repairs`.
3. **Corrija primeiro o adaptador.** Falhas iniciais geralmente estão na estrutura de teste: `quiescent()` prematuro, identificador de mensagem instável, estado em `view` que pode legitimamente diferir. Só confie nos oráculos após 200 sessões sem falhas.
4. **Comprove que o fuzzer consegue falhar no alvo.** Reintroduza um bug passado por um seletor (variante de mutação) e exija falha pelo oráculo correto. Um fuzzer que nunca foi visto falhando não demonstrou nada.
5. **Monitore a cobertura.** Conte o que as sessões provocaram: transferências de responsabilidade, disputas de saque perdidas, disputas de criação perdidas, carregamentos do host, mensagens antigas reproduzidas, duplicatas rejeitadas. Se um contador fica em zero, aquela defesa nunca foi testada.
6. **Execute frequentemente.** Dois minutos após cada alteração e uma execução longa à noite. Salve cada bug corrigido como cenário de regressão reduzido e reproduza-o nos testes.

## <a id="4-lessons"></a>4. Lições

- **Reduza antes de ler.** O cenário minimizado é o relato do bug. Leia as 4 operações, não as 400.
- **Falha de convergência geralmente é sintoma.** A ferramenta relata primeiro a regra violada mais específica (aplicação dupla ou obsoleta) e deixa `converge` por último.
- **Registre também as rejeições.** Uma rejeição correta comprova que uma defesa foi executada. A linha de cobertura de uma execução sem falhas mostra quais defesas o fuzzer alcançou.
- **Algumas variantes precisam de coincidência.** Um abate e uma atribuição se cruzando na rede é raro; essa variante precisa de mais sementes que as outras. Dê à variante rara sua própria contagem de sementes, em vez de afrouxar o oráculo.
- **Não corrija o oráculo para aprovar uma semente.** Se um alvo sem mutações falha, o adaptador mente ou o núcleo tem um bug. Decida qual é o caso antes de alterar algo.
- **Não substitui o jogo.** O fuzzer só vê o que o alvo relata; não testa os hooks do motor nem a pilha de rede real. Combine-o com bots internos ([automated-qa.md](automated-qa.md)) e, para sockets reais, um retransmissor que simule conexão ruim ([network-chaos-testing.md](network-chaos-testing.md)).

## <a id="5-run-it"></a>5. Execução

```
python -I tools/fuzz/run_tests.py                          # build and test everything, prints ALL OK
python -I tools/fuzz/run.py --minutes 2 --players 4        # fuzz for two minutes with 4 players
python -I tools/fuzz/run.py --bug two_owners --count 100   # a switched-on bug must make this fail
python -I tools/fuzz/run.py --replay tools/fuzz/out/fail_seed6_dup_thing.min.scenario.json
```
