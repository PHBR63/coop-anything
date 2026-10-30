# <a id="guide-wrap-your-sync-core-in-a-fuzz-target"></a>Guia: adapte seu núcleo de sincronização a um alvo de fuzzing

Este guia vai de "tenho um núcleo de sincronização" a "o fuzzer executa meu núcleo e sei que detecta os bugs relevantes". Leia ao lado dele `example/skeleton_target.cpp` (cerca de 190 linhas, compilado e testado). É o menor alvo completo. `example/example_target.cpp` é a versão com todos os recursos.

Você adapta **a lógica de sincronização**, não o jogo. O fuzzer nunca inicia o jogo. Executa várias cópias do núcleo num processo, conecta-as por rede simulada com perdas, aplica uma sessão aleatória e verifica o resultado. Isso o torna rápido (milhares de sessões por minuto) e reproduzível (uma semente sempre repete a mesma sessão).

## <a id="what-your-core-must-allow"></a>O que o núcleo precisa permitir

Um alvo só pode adaptar código capaz de executar N vezes num processo sob relógio simulado. Confira primeiro quatro coisas:

1. **Sem estado global.** Duas máquinas num processo não podem compartilhar singletons. Se o núcleo usa globais, coloque-as numa estrutura criada por máquina ou adicione hook de reinicialização e dê a cada máquina sua cópia.
2. **Tempo injetável.** O núcleo recebe o tempo do chamador (`tick(nowMs)` ou callback de relógio). Sem relógio real, `sleep` ou threads de temporizador. O exemplo usa passos fixos de 10 ms.
3. **Transporte injetável.** O núcleo envia bytes por callback e recebe por chamada de função. O alvo move bytes pelo `LossyLink`.
4. **Aleatoriedade com semente.** Toda aleatoriedade vem de semente fornecida pelo alvo. Assim, uma semente com falha se reproduz exatamente.

Se o núcleo está acoplado ao motor, separe as chamadas atrás de uma interface pequena e forneça ao alvo uma implementação simulada (um mapa de objetos representando o mundo). Esse mundo simulado é o que os oráculos examinam.

## <a id="step-by-step"></a>Passo a passo

### <a id="1-copy-the-skeleton"></a>1. Copie o esqueleto

```
copy tools\fuzz\example\skeleton_target.cpp tools\fuzz\my_target.cpp
```

Renomeie o alvo (`kRegisterSkeleton`, nome em `TargetInfo`). Exclua a parte 1 (núcleo substituto) e mantenha a parte 2, o adaptador.

### <a id="2-build-the-machines"></a>2. Construa as máquinas

No construtor, crie `s.machines` cópias do núcleo (2 a 4; máquina 0 é o host). Dê a cada uma:

- Callback de envio que chama `net_.send(from, to, bytes)` no `LossyLink` integrado.
- Callback de relato (etapa 5).
- Semente derivada de `s.seed` e do número da máquina.

Defina a conexão inicial: `net_.setLink(s.link)`. Se `s.profile` não estiver vazio, use `linkProfile(s.profile, link)` em vez disso (predefinições: `lan`, `good_wifi`, `bad_wifi`, `mobile`, `hell`). Com transporte próprio, ignore `LossyLink` e `s.link`, mas você passa a implementar perda, duplicação, atraso e reordenação.

### <a id="3-drive-the-clock-advancetoms"></a>3. Avance o relógio: `advance(toMs)`

Avance um relógio virtual em intervalos pequenos (10 ms serve). Em cada intervalo: `net_.advance(now_)`, entregue todo pacote recebido (`net_.poll(m, from, bytes)` e a função receptora do núcleo), depois execute o trabalho periódico conforme a agenda do núcleo (o exemplo atualiza fluxos a cada 50 ms, responsabilidade a cada 200 ms e resumos a cada 2 s).

### <a id="4-map-ops-onto-your-game-applyop"></a>4. Mapeie operações para o jogo: `apply(op)`

As operações são genéricas: `Move`, `Hit`, `Pickup`, `Drop`, `Spawn`, `Activate`, `Join`, `Leave`, `Save`, `Load`, `SetLink`, `Stale`. A tabela está em `include/coopfuzz/fuzz.h`. Faça o que o núcleo permite e ignore o restante (o esqueleto trata apenas `Move`). Regras:

- Uma operação identifica máquina (`op.m`) e números pequenos. Referências são posições: escolha "o ator vivo na posição (a módulo quantidade)", nunca identificador bruto. Isso mantém cada operação válida quando o redutor remove outras.
- Faça como o jogo faria, pela entrada normal do núcleo (alteração local, solicitação ao host), não escrevendo no estado de outra máquina.
- `Stale` pede para injetar mensagem antiga: reproduzir pacote gravado (`c=1`) ou enviar conteúdo antigo num pacote novo (`c=0`). Assim são provocados bugs de eco obsoleto e aplicação dupla. Ignore se o protocolo não tem nada para repetir, mas essas classes de bugs só serão alcançáveis pela duplicação e reordenação da própria rede.

### <a id="5-report-what-each-machine-applies"></a>5. Relate o que cada máquina aplica

Esta etapa faz os oráculos funcionarem. Sempre que uma máquina aplicar ou rejeitar mensagem recebida, chame `logApply(...)` de `TargetBase` (o esqueleto faz isso num callback):

| Argumento | O que informar |
|---|---|
| `machine` | máquina que aplicou |
| `idem` | identificador estável da **mensagem**, igual em toda entrega: por exemplo, remetente e sequência empacotados em 64 bits. Use 0 se não houver identificador (sem verificação de aplicação dupla) |
| `ref` | identificador de rede do objeto, ou -1 |
| `epoch`, `seq` | época de responsabilidade e sequência da atualização transportadas, ou 0 |
| `origin` | máquina que produziu o conteúdo (não a que o encaminhou) |
| `kind` | `Pos`, `PlayerPos`, `Hp`, `Owner`, `Holder`, `Door`, `Spawn`, `Remove`, `Reset`, `Intent` |
| `accepted` | true quando a mensagem alterou o estado, false quando corretamente descartada |
| `worldEpoch` | geração de salvar/carregar na qual a mensagem foi criada, ou 0 |
| `why` | motivo curto de rejeição ("stale epoch", "duplicate"). Rejeições são contadas em `stats()` como `reject_<why>` |

Registre **também as rejeições**. Elas comprovam que as defesas executaram; a linha de cobertura indica as nunca alcançadas pelo fuzzer.

Se o núcleo tem serviço de responsabilidade (quem simula qual ator), chame `logOwn(Grant|Transfer|Release, ref, owner, prevOwner, epoch)` a cada decisão e `logOwn(WorldEpoch, ...)` quando o host substituir o mundo. Sem responsabilidade no jogo, ignore: os oráculos correspondentes não verão eventos e nada verificarão. Declare isso na documentação.

### <a id="6-answer-the-oracle-questions"></a>6. Responda às perguntas dos oráculos

| Método | Significado |
|---|---|
| `view(m)` | tudo que a máquina m tem, como `Thing`s ordenados por identificador de rede. Preencha `ident` para objetos com identidade além desse identificador (ponto de criação, item original), permitindo detectar duplicatas |
| `digest(m, cat)` | hash do estado da máquina m, um por categoria (0 a 3). Igual em todas as máquinas em repouso. Alvo sem categorias pode devolver o mesmo hash para as quatro |
| `repairs(m)` | quantidade de ações de ressincronização ou reparo da máquina m. Contador que nunca diminui. Retorne 0 se não há reparo |
| `heal()` | tornar a conexão perfeita, reconectar todos e parar atividade nova (IA, sinais periódicos que alteram estado). Chamado uma vez após a última operação |
| `quiescent()` | true quando nada está em trânsito, todas as máquinas alcançaram o host e a atividade congelou. Seja rigoroso: é a condição que decide quando comparar estados |
| `connected(m)` | false enquanto máquina m estiver fora da sessão (ignorada na verificação de convergência) |

### <a id="7-register-and-build"></a>7. Registre e compile

No fim do arquivo:

```cpp
const TargetRegistrar kRegisterMine(TargetInfo{"mine", "my sync core", {"bug_one", "bug_two"}, makeMine});
```

`makeMine(const Scenario& s, std::string* err)` constrói o alvo. Deve preencher `*err` e retornar null se `s.bugs` contiver nome desconhecido. Depois:

```
cmake -S tools/fuzz -B build/fuzz -DCOOPFUZZ_TARGET_SOURCES="my_target.cpp;example/example_target.cpp"
cmake --build build/fuzz --config Release --parallel 1
```

Ou defina `COOPFUZZ_CMAKE_ARGS=-DCOOPFUZZ_TARGET_SOURCES=...` e use `python -I tools/fuzz/run.py --target mine`. Passe `-DCOOPFUZZ_TESTS=OFF` para excluir os autotestes da estrutura da sua compilação.

### <a id="8-run-clean-and-fix-your-adapter-first"></a>8. Execute sem mutações e corrija primeiro o adaptador

```
python -I tools/fuzz/run.py --target mine --count 200 --players 3
```

As primeiras falhas normalmente estão no adaptador, não no núcleo. Abra `*.min.report.json`. O cenário minimizado costuma ter de 3 a 10 operações. Pergunte:

- `quiescent()` declarou repouso com pacotes ainda em trânsito? Então `converge` dispara cedo demais.
- `idem` repetiu para mensagens diferentes ou diferiu para a mesma? Isso gera falso `double_apply`.
- `view` inclui estado legitimamente diferente em cada máquina (objetos só locais)? Exclua-o.

Só após 200 sessões sem falha em cada quantidade de jogadores o resultado tem significado. Depois execute mais tempo: `python -I tools/fuzz/run.py --target mine --minutes 2 --players 4`.

### <a id="9-check-that-the-fuzzer-can-fail-on-your-target"></a>9. Confira se o fuzzer consegue falhar no alvo

Execuções limpas nada comprovam até você ver uma falha. Acrescente variantes (consulte "Add your own twin" em [BUG-CLASSES.md](BUG-CLASSES.md)): reative um bug antigo e confirme falha com o oráculo esperado. Mantenha teste que percorra sementes para cada variante (copie `tests/tests.cpp`, `twin(...)`). Mantenha também um que percorra sementes sem mutações e outro que conte eventos alcançados (`stats()`): um fuzzer que nunca provoca transferência, disputa de saque ou salvar/carregar passa pelo motivo errado.

### <a id="10-use-it"></a>10. Use

- Cada falha exibe `FAIL seed N ...` e grava sob `--out`: `fail_seedN_<oracle>.min.scenario.json` (sessão reduzida), `.min.report.json` (violações, estatísticas, logs de responsabilidade e aplicação) e versões `.full.*` da sessão original.
- Reprodução: `coopfuzz --replay <file>.min.scenario.json` (ou `python -I tools/fuzz/run.py --replay <file>`). Saída 1 e linhas `VIOLATION <oracle> <detail>` enquanto houver bug, saída 0 após corrigir.
- Preserve bug corrigido como regressão: `python -I tools/fuzz/run.py --fixture <bug_name>` grava reprodução reduzida (`regress_<bug>.json`) para incluir no commit e reproduzir nos testes.
- Execute `--minutes 2` após cada alteração no núcleo e execução longa (`--minutes 30`) durante a noite.

## <a id="cost-and-limits"></a>Custo e limites

- Uma sessão usa tempo virtual. Na máquina de desenvolvimento, o alvo de exemplo executou cerca de 130 sessões por segundo (3000 sessões de 15 segundos virtuais em 23 segundos). Núcleo real com mundo mais pesado será mais lento.
- O fuzzer só vê o relato do alvo. Bug em campo fora da visão, ou mensagem nunca registrada, é invisível. Amplie visão e log quando encontrar manualmente bug que escapou e adicione uma variante para ele.
- Testa lógica de sincronização contra falhas de rede e disputas de jogadores. Não testa hooks do motor, regras do jogo ou pilha de rede real. Precisam dos bots internos descritos em [automated-qa.md](../../playbook/automated-qa.md).
