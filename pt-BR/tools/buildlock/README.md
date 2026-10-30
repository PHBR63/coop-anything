# <a id="buildlock-share-one-build-tree-between-agents-and-cache-the-compiles"></a>buildlock: compartilhe uma árvore de compilação entre agentes e reutilize compilações em cache

Vários agentes no mesmo projeto querem uma única árvore de compilação: outra árvore custa disco e recompilação completa. Mas duas compilações simultâneas na mesma árvore se corrompem. Esta ferramenta protege a árvore com uma trava e controla o CMake para que a trava sempre seja liberada.

| Componente | Função |
|---|---|
| [`buildlock.py`](buildlock.py) | Trava: concessão temporária com prazo, nome do responsável, fila por ordem de chegada e recuperação se o detentor morrer. Classe Python e linha de comando (`run`, `status`, `break`). |
| [`build.py`](build.py) | Controlador CMake que adquire a trava, limpa o ambiente, carrega a linha de comando Visual Studio, configura só quando necessário, compila e opcionalmente usa sccache como cache de compilador. |

Somente biblioteca padrão; Python 3.8 ou superior. Testes executados no Windows; a verificação de processos possui um ramo separado para Linux e macOS.

## <a id="quick-start"></a>Primeiros passos

Compile um projeto numa árvore compartilhada:

```
python -I tools/buildlock/build.py --source . --build build/all --owner agent1 --target my_tests
```

Execute qualquer comando protegido pela trava (teste que lê a saída da compilação, outra ferramenta que escreve na árvore):

```
python -I tools/buildlock/buildlock.py run --tree build/all --owner agent1 -- ctest --test-dir build/all
python -I tools/buildlock/buildlock.py status --tree build/all
```

Em Python:

```python
from buildlock import BuildLock
with BuildLock("build/all.buildlock", owner="agent1").acquire(wait_s=3600):
    run_the_build()
```

A trava é a pasta `<tree>.buildlock`, ao lado da árvore; apagar a árvore não apaga a trava. Escolha um nome com `--owner NAME` (ou variável de ambiente `BUILDLOCK_OWNER`); o padrão é `agent-<pid>`. Use um nome que informe ao próximo agente com quem falar, nunca um nome pessoal.

## <a id="how-the-lock-behaves"></a>Comportamento da trava

- **Um detentor.** A trava é uma pasta criada por `mkdir`, operação atômica. Dentro dela, `lock.json` informa detentor, rótulo, PID, horário de início do processo, token aleatório e último sinal de atividade.
- **Concessão temporária.** Uma thread em segundo plano renova o sinal a cada `lease_s / 3` segundos (`--lease-s`, padrão 120). Enquanto o sinal estiver atualizado e o processo existir, ninguém pode adquirir a trava, independentemente da duração da compilação.
- **Recuperação de trava obsoleta.** Quem espera pode assumir quando o processo detentor desaparece (verificado por PID **e** horário de início, para não confundir PID reutilizado), o sinal é mais antigo que o prazo, a trava supera `--max-hold-s` (padrão 7200, para detentor travado que ainda sinaliza) ou a pasta nunca recebeu `lock.json`. O motivo é escrito em stderr. A quebra ocorre sob proteção breve, somente se a trava ainda tiver o token considerado obsoleto; um concorrente lento nunca quebra uma trava nova.
- **Ordem de chegada.** Quem espera escreve um tíquete e só adquire a trava livre se tiver o tíquete ativo mais antigo. Tíquetes de processos mortos ou sem atualização pelo solicitante por 30 segundos são removidos.
- **Só o detentor libera.** Uma trava quebrada e assumida por outro é preservada, e o sinal de atividade informa o antigo detentor (`[buildlock] the build lock was taken away`).
- **Códigos de saída de `run`.** O código do próprio comando; 3 se a trava não ficou livre em `--wait-s` (padrão 3600), com o detentor identificado na mensagem; 2 para erro de uso.
- **Manualmente.** `buildlock.py break --tree T --only-if-stale` remove a trava somente se obsoleta; sem `--only-if-stale`, remove qualquer trava. Faça isso apenas quando souber que o detentor não existe mais.

## <a id="the-build-driver"></a>O controlador de compilação

`build.py` executa, em ordem:

1. Remove `CMAKE_TOOLCHAIN_FILE`, `CMAKE_GENERATOR`, `CC`, `CXX` e `ANDROID_NDK*` do ambiente, pois um arquivo de ferramentas Android perdido no shell provoca compilação cruzada de tudo. `--keep-env` os mantém.
2. No Windows com gerador Ninja ou Makefile, carrega o ambiente de linha de comando Visual Studio para `--arch` (padrão x64), encontrado por `vswhere` ou indicado por `--vcvars FILE` ou `BUILDLOCK_VCVARS`. `--msvc auto` (padrão) só faz isso quando `cl` não está no PATH; `on` força, `off` nunca faz. Gerador Visual Studio dispensa essa etapa.
3. Escolhe gerador: Ninja se `ninja` estiver no PATH; caso contrário, padrão do CMake (`--generator NAME` substitui).
4. Se a árvore Ninja foi configurada com os mesmos argumentos e `ninja -n` informa não haver trabalho, retorna imediatamente **sem adquirir a trava**; uma compilação sem tarefas nunca espera outra terminar.
5. Adquire a trava, configura se a árvore for nova ou os argumentos tiverem mudado (guardados em `.buildlock-configure.json` na árvore) e compila. A trava é liberada no sucesso, na falha e com Ctrl-C.
6. Exibe `BUILD-TIME <label> <seconds>`.

Opções úteis: `--target T [T ...]`, `--config Release`, `--jobs N` (padrão: `CMAKE_BUILD_PARALLEL_LEVEL` ou 2), `--cmake-arg=-DNAME=VALUE` (escreva o sinal de igual, pois o valor começa com hífen), `--clean`, `--configure-only`, `--keep-going`, `--dry-run` (exibe os comandos), `--no-lock`, `--wait-s`, `--cmake "CMD ..."` (outro programa cmake, também usado pelos testes para executar uma simulação). `--help` lista tudo.

## <a id="sccache-a-compile-cache-for-msvc-and-cmake"></a>sccache: cache de compilação para MSVC e CMake

[sccache](https://github.com/mozilla/sccache) envolve o compilador, calcula hash de cada compilação e responde pelo cache quando já viu a mesma compilação. Recompilar após mudar de branch, ou outro agente compilar as mesmas fontes, passa a custar uma consulta em vez de uma compilação. **Esta ferramenta nunca instala nada.** Instale sccache como suas outras ferramentas (peça autorização ao usuário antes), confira se `sccache --version` funciona no shell de `build.py` e execute:

```
python -I tools/buildlock/build.py --source . --build build/all --sccache on --sccache-stats
```

`--sccache auto` (padrão) usa quando estiver no PATH; `on` encerra com código 2 se ausente; `off` nunca usa.

O que `build.py` acrescenta à configuração com sccache:

| Argumento | Motivo |
|---|---|
| `-DCMAKE_C_COMPILER_LAUNCHER=<sccache>` e `-DCMAKE_CXX_COMPILER_LAUNCHER=<sccache>` | CMake executa todas as compilações por sccache. |
| `-DCMAKE_DISABLE_PRECOMPILE_HEADERS=ON` | sccache não armazena compilação com cabeçalho pré-compilado (`/Yu`, `/Yc`). |
| `-DCMAKE_POLICY_DEFAULT_CMP0141=NEW` e `-DCMAKE_MSVC_DEBUG_INFORMATION_FORMAT=Embedded` (somente MSVC) | `/Zi` escreve PDB compartilhado, não reutilizável pelo cache. `Embedded` é `/Z7`: informações de depuração em cada arquivo objeto. Exige CMake 3.25 ou superior. |

O que saber:

- **Gerador.** Inicializadores de compilador funcionam com Ninja e Makefile, não com gerador Visual Studio. Neste último, `auto` compila sem sccache (e informa isso), e `on` encerra com código 2.
- **CMake anterior a 3.25.** Configure o equivalente: remova `/Zi` e `/ZI` das opções e acrescente `/Z7`.
- **Um cache para todos os agentes.** Agentes executados pelo mesmo usuário no mesmo PC compartilham servidor sccache e pasta de cache. Para mudar pasta ou tamanho, defina `SCCACHE_DIR` e `SCCACHE_CACHE_SIZE` no ambiente antes do primeiro comando sccache.
- **Acertos exigem a mesma compilação.** A chave inclui compilador, linha de comando e fonte pré-processada, que contém caminhos de arquivos. Árvores em caminhos distintos ou com opções diferentes não compartilham acertos. Mantenha um caminho de checkout por projeto.
- **Veja o comportamento.** `--sccache-stats` exibe `sccache --show-stats` após compilar; `sccache --zero-stats` zera os contadores.
- **Após mudar a configuração de sccache**, a próxima execução configura novamente, pois os argumentos mudaram.

Os testes usam um programa `sccache` simulado no PATH e cmake simulado, verificando quais argumentos chegam ao CMake. A economia de compilações de um cache real depende do projeto; leia as estatísticas.

## <a id="how-it-is-tested"></a>Como é testado

```
python -I tools/buildlock/run_tests.py       # prints ALL OK only if every check passes and every twin is caught
```

26 verificações e 22 variantes de mutação; cerca de 45 segundos. Nenhum compilador executa. O controlador usa cmake simulado (`tests/fake_cmake.py`) que registra o solicitado; a trava usa threads, processos substitutos de curta duração iniciados e encerrados pelos próprios testes (somente por PID e enquanto ainda for o mesmo processo) e linha de comando.

- **Trava:** seis threads nunca a detêm simultaneamente; tempo esgotado identifica detentor; só ele libera; sinal detecta perda da trava; recuperação de detentor morto, PID reutilizado, prazo vencido e retenção excessiva; sinal ativo mantém a trava além de três períodos; solicitante não fura fila, tíquetes de processos mortos e de quem deixou de esperar são removidos; aquisição por ordem de chegada; quebra exige token considerado obsoleto e proteção de quebra; pasta nova sem `lock.json` é respeitada brevemente e depois considerada obsoleta; gerenciador de contexto libera após exceção.
- **Linha de comando:** códigos de saída repassados, trava ocupada gera saída 3, três trabalhos reais iniciados a meio segundo de intervalo executam na mesma ordem, recuperação da trava de detentor encerrado, `status` e `break`.
- **Controlador:** trava mantida durante cmake e liberada após configuração ou compilação falhar; árvore sem trabalho retorna sem esperar trava ocupada; reconfigura só ao mudar argumentos; sccache usado, forçado e recusado conforme descrito, incluindo gerador Visual Studio; variáveis indevidas removidas; ambiente Visual Studio (arquivo batch `vcvars` simulado) chega ao cmake; `--dry-run`, `--configure-only`, `--clean`, `--target`.
- **Variantes**, aplicadas externamente: trava sempre concedida; liberação por qualquer um; sinal que nunca detecta ou nunca executa; processo sempre vivo; PID reutilizado não detectado; concessão que nunca vence; ausência de limite de retenção, fila ou expiração de tíquetes; quebra que ignora token; sem tolerância a trava nova; liberação sem efeito; controlador que nunca adquire trava ou sempre espera; configuração nunca repetida; argumentos de sccache ausentes; sccache usado quando desativado; ambiente sujo; ambiente Visual Studio ignorado.

## <a id="files"></a>Arquivos

`buildlock.py`, `build.py`, `run_tests.py`, `tests/` (`fake_cmake.py`, `fake_job.py`).

Generalizado do commit e85460f de fnv-coop (github.com/cranebeaker/fnv-coop): `tools/build/build.py`. Alterações: trava com prazo, sinal de atividade, detentor, fila e recuperação por PID e início do processo, em vez de `mkdir` simples que tenta novamente a cada 15 segundos e nunca recupera; caminho Visual Studio encontrado por `vswhere`, não fixado no script; sccache opcional com configurações MSVC necessárias; configuração repetida quando os argumentos mudam; nada específico de um projeto (removidos caminho de superbuild, reparo de quebras de linha e opção de cabeçalho pré-compilado do original).
