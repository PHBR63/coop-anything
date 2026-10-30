# <a id="co-op-fuzzer-random-sessions-and-invariant-oracles-for-any-sync-core"></a>Fuzzer cooperativo: sessões aleatórias e oráculos de invariantes para qualquer núcleo de sincronização

Uma pequena estrutura C++17 que testa a **lógica de sincronização** de um mod cooperativo sem o jogo. Executa 2 a 4 cópias do núcleo em um processo, conecta-as por uma rede simulada com falhas (atraso, variação de atraso, perda, duplicação, corrupção), aplica uma sessão aleatória (movimentos, golpes, disputas por itens, criação de entidades, portas, entradas, saídas, salvamento e carregamento pelo host, conexões ruins, repetição de mensagens antigas), recupera a rede, espera a atividade cessar e verifica o resultado com **oráculos**:

| Oráculo | Condição necessária |
|---|---|
| `converge` | Após a atividade cessar, todas as máquinas têm as mesmas entidades e valores do host |
| `double_apply` | Nada é aplicado duas vezes |
| `multi_owner` | Um responsável por ator em cada época de responsabilidade; épocas só crescem |
| `stale_applied` | Nada desatualizado é aplicado (época antiga, sequência antiga, máquina não responsável, solicitação anterior a um carregamento) |
| `echo_adopted` | Uma máquina nunca adota o eco da própria atualização |
| `dup_thing` | Nenhum ator ou item duplicado (mesmo ID de rede ou mesma identidade duas vezes) |
| `repairs_after_quiescence` | Reparos por minuto são 0 depois de toda a atividade cessar |
| `not_quiescent` | O tráfego realmente para após a recuperação da conexão |

Quando uma condição falha, o fuzzer exibe a **semente** que falhou, reduz a sessão a poucas operações e escreve um arquivo de cenário reproduzível e um relatório JSON.

É um **modelo acompanhado de guia**. Você implementa uma interface (`ITarget`) que envolve seu núcleo de sincronização. Dois alvos completos estão incluídos; nenhum exige um jogo ou núcleo de sincronização:

- `example/skeleton_target.cpp` (191 linhas): o menor alvo. Comece aqui.
- `example/example_target.cpp`: mundo completo com autoridade do host (atores com épocas de responsabilidade, itens, portas, encontros, salvamento e carregamento pelo host, fluxos confiáveis, resumos de estado e reparos) com **12 variantes de mutação**, uma por classe conhecida de bug.

Documentos: [GUIDE.md](GUIDE.md) (integração do seu núcleo passo a passo), [BUG-CLASSES.md](BUG-CLASSES.md) (classes de bugs, como aparecem no jogo e qual oráculo as detecta) e a página do guia [fuzzing-coop-sync.md](../../playbook/fuzzing-coop-sync.md).

## <a id="quick-start"></a>Primeiros passos

Você precisa de `cmake`, um compilador C++17 (Visual Studio 2022 no Windows) e Python 3.

```
python -I tools/fuzz/run_tests.py                      # build, run all tests, prints ALL OK
python -I tools/fuzz/run.py --minutes 2 --players 4    # fuzz the example target for two minutes with 4 players
python -I tools/fuzz/run.py --bug two_owners --count 100   # switch a bug on: the run must FAIL, shrink and write a report
python -I tools/fuzz/run.py --target skeleton --count 200
```

A primeira chamada compila em `tools/fuzz/build` (ignorado pelo Git). Uma execução sem falhas termina com `RESULT: ALL OK`. Uma execução com falha encerra com código 1 e exibe, por exemplo:

```
FAIL seed 6 (2 machines): dup_thing: m0 has two copies of identity 2 (...)
  shrunk 377 -> 4 ops, 2 machines, 5799 ms in 94 runs; still fails: dup_thing
  minimized scenario: tools/fuzz/out/fail_seed6_dup_thing.min.scenario.json  (hash 680756bd)
  report:             tools/fuzz/out/fail_seed6_dup_thing.min.report.json
  replay: coopfuzz --replay tools/fuzz/out/fail_seed6_dup_thing.min.scenario.json
```

(Por `run.py`, os caminhos são absolutos. As falhas ficam em `tools/fuzz/out`, ignorado pelo Git; altere o destino com `--out`.)

Opções de `run.py` (encaminhadas ao executável): `--minutes M` ou `--count K`, `--seed S`, `--players 2..4` (0 ou ausente varia por semente), `--duration MS`, `--profile lan|good_wifi|bad_wifi|mobile|hell`, `--target NAME`, `--bug NAME` (repetível), `--replay FILE`, `--fixture BUG`, `--out DIR`, `--no-shrink`, `--max-fail N`, `--list-bugs`, `--list-targets`, `--quiet`; para o controlador, `--no-build`, `--rebuild`. Códigos de saída: 0 se todos os invariantes forem mantidos, 1 se um invariante falhar, 2 para erro de uso ou compilação.

## <a id="use-it-on-your-own-game"></a>Use no seu próprio jogo

Leia [GUIDE.md](GUIDE.md). Em resumo: copie `example/skeleton_target.cpp`, substitua o núcleo simulado por chamadas ao seu, registre o que cada máquina aplica, responda às perguntas dos oráculos (`view`, `digest`, `quiescent`, `repairs`), registre o alvo, compile com `-DCOOPFUZZ_TARGET_SOURCES="my_target.cpp"`, execute sem falhas; depois reative bugs anteriores como variantes e confira se os oráculos os detectam.

## <a id="layout"></a>Organização

| Caminho | Conteúdo |
|---|---|
| `include/coopfuzz/fuzz.h` | toda a API pública: operações, cenário, `ITarget`, `TargetBase`, registro, oráculos, execução, redução, relatório |
| `include/coopfuzz/net.h`, `src/net.cpp` | conexão interna com perdas e configurações predefinidas de conexão |
| `include/coopfuzz/rng.h` | gerador de números aleatórios com semente (mesma semente, mesma sessão em todas as plataformas) |
| `src/scenario.cpp` | gerador de sessões e JSON de cenário |
| `src/oracles.cpp` | oráculos |
| `src/runner.cpp` | execução, espera de inatividade, redutor, relatório JSON |
| `src/main.cpp` | linha de comando |
| `example/` | os dois alvos |
| `tests/` | testes internos (estrutura própria pequena, sem dependências) |
| `run.py`, `run_tests.py` | controlador e executor dos testes |

## <a id="how-it-is-tested"></a>Como é testado

`python -I tools/fuzz/run_tests.py` compila com cmake (uma tarefa de compilação por vez) e exibe `ALL OK` somente se tudo abaixo passar:

- Oráculos sobre logs criados manualmente: cada um aceita um log válido e sinaliza um inválido.
- O executor sinaliza um alvo que nunca fica inativo e outro que continua fazendo reparos.
- A conexão perde, duplica e atrasa tráfego e descarta o tráfego de uma máquina que cai.
- O gerador e o JSON de cenário são determinísticos e preservam os dados na ida e volta; executar com a mesma semente produz o mesmo resultado.
- 300 sessões sem falhas com 2 a 4 jogadores satisfazem todos os oráculos; uma proteção de cobertura confirma que realmente provocam concessões e transferências de responsabilidade, mortes, disputas por itens, disputas de criação, carregamentos do host, entradas, saídas, repetição de mensagens obsoletas, pacotes perdidos e duplicados.
- **Todas as variantes de mutação são detectadas pelos oráculos**, pelos testes C++ e novamente pela linha de comando (12 no alvo de exemplo, 1 no esqueleto), cada uma com o tipo esperado de violação.
- Sessões sem falhas funcionam nas cinco configurações de conexão, e bugs injetados continuam sendo detectados na pior delas.
- Uma execução com falha é reduzida (por exemplo, de 203 para 3 operações), o cenário reduzido continua falhando e o mesmo arquivo passa após a remoção do bug.
- O relatório JSON é válido e contém semente, violações, informações de redução e logs.
- A linha de comando: códigos de saída, `--replay`, `--fixture`, entrada inválida.

Foi executado no Windows 11 com Visual Studio 2022 (MSVC 19.40) e cmake 4.1. O código é C++17 padrão com cmake padrão. Quem compilar em outro ambiente deve executar o mesmo comando.

## <a id="ported-from"></a>Origem da adaptação

Adaptado do commit f57aa78 de fnv-coop ([github.com/cranebeaker/fnv-coop](https://github.com/cranebeaker/fnv-coop)), onde aplica fuzzing a um núcleo de sincronização de Fallout: New Vegas. A lógica dos oráculos, o gerador de cenários, o redutor e o mundo de exemplo vêm de lá. Esta versão independe do jogo: o núcleo de sincronização, transporte e modelo de caos são substituídos pela interface `ITarget` e uma pequena conexão interna com perdas; o mundo de exemplo ganhou uma classe de bug (eco obsoleto de atribuição, veja BUG-CLASSES.md) e um alvo esqueleto. O adaptador específico de Fallout não faz parte deste repositório.

## <a id="license"></a>Licença

MIT, como o restante deste repositório.
