# <a id="mutants-mutation-twins-you-can-switch-on-at-run-time"></a>mutants: variantes de mutação ativáveis em tempo de execução

Uma **variante** é uma cópia deliberadamente defeituosa de um trecho do código, por exemplo `a - b` no lugar de `a + b`. O teste que protege esse código deve falhar quando a variante estiver ativa. Uma variante que nenhum teste percebe indica que o teste não comprova nada sobre esse trecho, e você descobre isso antes de o bug voltar.

O método antigo compila o código uma vez por variante: 40 variantes, 40 compilações. Esta ferramenta compila uma vez. A versão defeituosa fica no código atrás de uma opção, e você escolhe a variante ao iniciar o programa de testes:

```
set COOP_MUT=add_wrong_operator && my_tests.exe        (a name or a number)
```

| Componente | Função |
|---|---|
| [`coop_mut.h`](coop_mut.h) | Opção C++ implementada apenas no cabeçalho. `COOP_MUT_IF("name")` é falso e não tem custo, a menos que a compilação use `COOP_RUNTIME_MUT`. |
| [`coop_mut.py`](coop_mut.py) | A mesma ideia para Python: `coop_mut.mut("name")`. |
| [`run_twins.py`](run_twins.py) | Lê uma tabela de variantes (nome e teste que deve falhar), executa cada teste uma vez sem variante e depois cada variante, relatando detecção ou falha de detecção. |
| [`twins.example.json`](twins.example.json) | Tabela pronta para executar. |

As partes Python usam apenas a biblioteca padrão; o cabeçalho C++ também usa apenas a biblioteca padrão de C++. Os testes compilam o cabeçalho como C++17 com Visual Studio 2022 no Windows.

## <a id="quick-start"></a>Primeiros passos

**C++.** Coloque o cabeçalho no caminho de inclusão e envolva a variante defeituosa:

```cpp
#include "coop_mut.h"

int add(int a, int b) {
    if (COOP_MUT_IF("add_wrong_operator")) return a - b;   // the twin: a broken variant
    return a + b;
}
bool isEven(int x) {
    if (!COOP_MUT_IF("even_check_removed")) return x % 2 == 0;   // a twin that removes code
    return true;
}
```

Compile o código testado **para seus testes** com `COOP_RUNTIME_MUT` definido; na compilação distribuída, deixe-o indefinido:

```cmake
add_library(core_rt STATIC core.cpp)                 # the test build
target_compile_definitions(core_rt PRIVATE COOP_RUNTIME_MUT)
add_library(core STATIC core.cpp)                    # the shipped build: COOP_MUT_IF(x) is the constant false
```

O `main` do teste também pode aceitar `--mut NAME`: chame `coop_mut::init_from_args(argc, argv);` primeiro.

**Python.**

```python
import coop_mut

def add(a, b):
    if coop_mut.mut("add_wrong_operator"):
        return a - b
    return a + b
```

`COOP_MUT=add_wrong_operator python my_tests.py` ativa a variante. `coop_mut.active("name")` é um gerenciador de contexto para testes no mesmo processo, e `coop_mut.ENABLED` é False quando nenhuma variante é selecionada.

**A tabela.** Um arquivo JSON informa qual teste deve falhar para cada variante:

```json
{
  "label": "core",
  "cmd": ["build/core_tests.exe", "{test}"],
  "real_regex": ", 0 failed",
  "caught_regex": ", [1-9][0-9]* failed",
  "scan": ["src/**/*.cpp"],
  "twins": {
    "add_wrong_operator": "test_add",
    "even_check_removed": ["test_even", "test_range"]
  }
}
```

```
python -I tools/mutants/run_twins.py core_twins.json
python -I tools/mutants/run_twins.py tools/mutants/twins.example.json --verbose
```

A última linha será `<label>: real tests pass, all N twins caught - ALL OK` somente quando todas forem detectadas. O código de saída é 0 nesse caso, 1 quando uma variante não é detectada ou a execução real falha, 2 quando a tabela está errada. Cada coluna é descrita no início de [`run_twins.py`](run_twins.py) (`--help` a exibe).

## <a id="add-a-twin-for-every-fix"></a>Acrescente uma variante para cada correção

Faça isso sempre que corrigir um bug. Leva dois minutos e mantém a correção funcionando.

1. Escreva o teste que falha no bug. Execute e observe a falha.
2. Faça a correção.
3. Mantenha o comportamento antigo atrás de uma variante: `if (COOP_MUT_IF("short_name_of_the_bug")) { old, broken code } else { fixed code }`. Para uma correção que adiciona uma verificação, escreva `if (!COOP_MUT_IF("name")) { the new check }`.
4. Acrescente a linha à tabela: `"short_name_of_the_bug": "the_test_from_step_1"`.
5. Execute `run_twins.py`. Precisa informar `caught`. Leia os demais resultados:

| Resultado | Significado | O que fazer |
|---|---|---|
| `MISSED` | O teste indicado passou com a variante ativa. Não protege esse código, ou a variante não está integrada. | Faça o teste verificar o que a correção alterou ou corrija o nome da variante. |
| `WRONG TEST` | O teste indicado passou, mas outro falhou. A variante quebra outra coisa. | Corrija a tabela (indique o teste que falha) ou restrinja a variante. |
| `BUILD CRASH` | Uma variante de tempo de compilação não compilou (veja abaixo). | A variante precisa compilar e depois falhar no teste. |
| `UNLISTED` / `STALE` | Com `"scan"`: uma variante usada no código não está na tabela, ou uma linha não tem ponto de chamada. | Acrescente a linha ou apague a linha sem uso. |

Quando você fornece `caught_regex`, uma variante que falha porque o programa encerrou inesperadamente não conta como detectada; assim, uma falha de processo não é confundida com uma verificação que falhou. Erros do carregador (DLL ausente, imagem inválida) nunca contam como detecção. Travamentos contam.

Mantenha nomes curtos e ligados ao bug, não à linha. Números também funcionam (`COOP_MUT_IF(7)`, `"7": "test_x"`). Uma variante fica ativa por vez. Nunca deixe `COOP_RUNTIME_MUT` definido na compilação distribuída.

## <a id="compile-time-twins"></a>Variantes em tempo de compilação

Alguns defeitos não podem ficar atrás de um `if`, como um tipo diferente ou membro removido. Forneça à tabela um comando `twin_build`, executado uma vez por variante com a variável de ambiente `COOP_MUT` definida para ela (sua compilação lê a variável e passa uma opção `-D`), seguido do teste. Se não compilar, o resultado é `BUILD CRASH`; após a última variante, o executor recompila sem mutação para deixar a árvore limpa. Variantes com compilação executam uma por vez.

## <a id="how-it-is-tested"></a>Como é testado

```
python -I tools/mutants/run_tests.py       # prints ALL OK only if every check passes and every twin is caught
```

20 verificações e 28 variantes; leva cerca de um minuto, principalmente nas compilações C++. `--no-cpp` pula a parte C++ e informa isso; `--build-dir DIR` (ou `COOP_BUILD_DIR`) escolhe a pasta de compilação, por padrão dentro do diretório temporário do sistema (mantenha o caminho curto: Visual Studio falha com mais de 260 caracteres).

- **Executor**, com programas de teste simulados: todas as variantes detectadas; uma variante sem efeito é `MISSED`, sem `ALL OK`; uma que quebra o teste errado é `WRONG TEST`; uma que impede a compilação é `BUILD CRASH`, com recompilação sem ela; falha na execução real interrompe tudo; erro do carregador, encerramento sem o texto esperado e travamento julgados corretamente; lista em que um teste basta; ambiente do processo pai nunca deixa uma variante vazar para a execução real; varredura do código; erros de tabela e saída 2; execuções paralelas; `--only`, `--list`, `--json`; tabela de exemplo.
- **`coop_mut.py`**: desativado por padrão, `0` e vazio significam desativado, correspondência exata de nomes e números, `set`, `active` (também após exceção), formas de `--mut`, processo filho lê seu próprio ambiente.
- **`coop_mut.h`**: compilado duas vezes com CMake. Com `COOP_RUNTIME_MUT`, as quatro variantes são detectadas pelos testes indicados; `--mut NAME`, `--mut=NAME` e `--mut 4` funcionam; `COOP_MUT=0` e nome parcial não selecionam variante. Sem a definição, o programa ignora `COOP_MUT` e `--mut`, e o binário não contém nomes de variantes nem a string `COOP_MUT`.
- **Variantes das próprias ferramentas**, cada uma aplicada externamente: teste de detecção que sempre responde sim ou nunca responde; erros do carregador contados como detecção; execução real omitida; ambiente que vaza; ausência de detecção de teste errado; falha de compilação ignorada; ausência de recompilação; varredura que não encontra nada; ausência de tratamento de tempo limite; relatório nunca escrito; ausência de validações da tabela; `--only` ignorado; em `coop_mut.py`, ambiente ignorado, correspondência por prefixo, `active` sem restauração, `0` como variante, argumentos não removidos; em `coop_mut.h`, nome ou número que nunca corresponde, opção ignorada, correspondência por prefixo e compilação distribuída ainda ativável.

## <a id="files"></a>Arquivos

`coop_mut.h`, `coop_mut.py`, `run_twins.py`, `twins.example.json`, `run_tests.py`, `tests/` (`cpp_under_test.cpp`, `CMakeLists.txt`, `py_under_test.py`, `py_mut_checks.py`, `fake_suite.py`, `fake_build.py`).

Generalizado do commit e85460f de fnv-coop (github.com/cranebeaker/fnv-coop): `tools/mut/fnvcoop_mut.h` e `run_twins.py`. Alterações: macro e variável são `COOP_MUT_IF` e `COOP_MUT`; variantes têm nome e número; a tabela indica o teste que deve falhar, em vez de um comando para toda a suíte; variante que quebra outro teste ou não compila é relatada separadamente; fontes podem ser comparadas à tabela por varredura; há uma opção Python.
