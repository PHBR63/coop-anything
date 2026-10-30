# <a id="hot-reload-swap-your-mods-dll-inside-a-running-game"></a>Recarregamento a quente: troque a DLL do mod dentro do jogo em execução

Uma pequena biblioteca C++17, uma DLL carregadora e um cliente Python que inserem uma DLL recém-compilada em um jogo já em execução, preservando o estado do mod. A rodada de editar, compilar, trocar e testar deixa de exigir "reiniciar o jogo e carregar um salvamento" e passa a levar poucos segundos.

Funciona com qualquer jogo Windows cujo mod seja uma DLL carregada no processo (plugin de extensão de scripts, plugin ASI, biblioteca injetada). Nada conhece um jogo específico. Leia a [página do guia](../../playbook/hot-reloading-your-mod.md) para conhecer o método e os erros e [examples/fnv](examples/fnv/README.md) para a integração de um mod real.

**Uso adequado:** esta é uma ferramenta de desenvolvimento para seu próprio mod na sua cópia do jogo. Nunca a use contra um jogo on-line com antitrapaça.

## <a id="how-it-works"></a>Como funciona

Você divide o mod em dois:

| Metade | Onde permanece | O que contém |
|---|---|---|
| **Carregador** (`hotreload_loader.dll` ou a biblioteca estática `hotreload_host` no seu plugin) | No jogo durante toda a sessão. | Pipe de controle, cópia de cache do núcleo, carregar / descarregar / recarregar, armazenamento de bloco de dados que sobrevive às recargas. |
| **Núcleo** (sua DLL, exporta `HotCore_Init`) | Mapeado de cópia privada em cache, substituído a cada troca. | Todo o restante: lógica do mod, threads, hooks, sockets. |

Por que uma cópia em cache: Windows não permite sobrescrever uma DLL carregada durante a compilação. O carregador mapeia `cache\core.<pid>.<n>.dll` e mantém a saída da compilação desbloqueada, para a compilação e a ferramenta de troca poderem substituí-la a qualquer momento.

Uma troca a partir de `hotreload.py`:

1. Ler `dev.status` da cópia em execução: localização do arquivo do núcleo, compilação ativa e geração.
2. Copiar a nova DLL ao lado do arquivo do núcleo com nome temporário e renomeá-la sobre ele (o carregador nunca vê um arquivo parcialmente escrito).
3. Chamar `dev.reload`. No jogo, entre dois quadros: o núcleo antigo **salva** o estado versionado de cada participante e **drena** (espera até nenhuma thread executar código do núcleo), depois **encerra** (para threads, remove hooks), e o carregador o desmapeia. O carregador mapeia a nova cópia, e o novo núcleo **restaura** o estado.
4. Conferir o resultado: o ID da compilação em execução corresponde ao CRC-32 e tamanho do arquivo copiado, a geração aumentou, nada foi revertido, o registro não informa falhas nem vazamentos.

Se algo der errado antes do desmapeamento, o núcleo antigo continua com seu estado. Se o novo falhar ao iniciar, o carregador mapeia o antigo novamente.

## <a id="what-you-get"></a>O que você recebe

| Componente | Onde | Função |
|---|---|---|
| `hotreload_loader.dll` | Compilado por CMake. | Carregador permanente com API C simples (`HotReload_Start`, `HotReload_OnFrame`, ...). |
| `hotreload_host` (biblioteca estática) | `src/loader_host.cpp`, `include/hotreload/loader_host.h` | Mesmo carregador como classe, para vincular ao seu plugin. |
| `hotreload_core` (biblioteca estática) | `src/reload_state.cpp`, `reload_drain.cpp`, `core_glue.cpp` | Para o núcleo: registro de estado, `ManagedThread`, `adoptThread`, drenagem, `BeforeUnload` / `AfterLoad`. |
| `hotreload_control` (biblioteca estática) | `src/control_pipe.cpp` | Servidor de pipe nomeado JSON-lines. Sem outra dependência. |
| `hotreload.py` | Esta pasta. | Cliente: `swap` (com `--dry-run`, `--force`, `--root`, vários `--pipe`) e `status`. Somente biblioteca padrão. |
| Núcleos de exemplo, host de teste | `examples/` | Seis compilações de um núcleo de exemplo com estado versionado e duas threads próprias, e um substituto do jogo. |
| Testes unitários, cenários, variantes de mutação | `tests/`, `run_tests.py` | Consulte "Como é testado". |

## <a id="split-your-mod-loader-and-core"></a>Divida o mod: carregador e núcleo

1. **Escolha a parte permanente.** O ponto de entrada do plugin (função chamada pelo carregador de mods do jogo) permanece no carregador. Faz três coisas: chama `HotReload_Start` uma vez, `HotReload_OnFrame` a cada quadro na thread principal e encaminha as mensagens desejadas por `HotReload_OnMessage`. Todo o restante vai para o núcleo.

   ```cpp
   HotReloadConfig cfg{};
   cfg.size = sizeof cfg;
   cfg.core_path = "C:\\games\\mygame\\mods\\mymod_core.dll";   // the file your build output gets copied over
   cfg.pipe_name = "mymod-0";                                   // the control pipe
   cfg.user_context = engineInterface;                          // handed to the core as api->user_context
   HotReload_Start(&cfg);                                       // in your entry point
   ...
   HotReload_OnFrame();                                         // every frame, main thread
   ```

2. **Faça o núcleo exportar uma função e preencher quatro callbacks.** Consulte [examples/core/example_core.cpp](examples/core/example_core.cpp), cerca de 240 linhas.

   ```cpp
   extern "C" __declspec(dllexport) int HotCore_Init(const HrLoaderApi* api, HrCoreApi* out) {
       g_api = api;
       out->abi_version = HR_ABI_VERSION; out->size = sizeof(HrCoreApi);
       out->init = &Init;                      // start threads, install hooks, then hotreload::AfterLoad(g_api)
       out->on_frame = &OnFrame;               // optional
       out->on_message = &OnMessage;           // optional
       out->before_unload = &BeforeUnload;     // return hotreload::BeforeUnload(g_api) ? 1 : 0
       return 1;
   }
   ```

3. **Registre cada parte de estado que precisa sobreviver**, com número de versão (abaixo).
4. **Registre todas as threads pertencentes ao núcleo** (próxima seção). Essa é a regra que costuma causar problemas.
5. **Mantenha a fronteira em C simples.** Entre carregador e núcleo, passam somente os tipos de [include/hotreload/abi.h](include/hotreload/abi.h): sem `std::string`, exceções ou objetos do runtime de qualquer lado. Nada no núcleo pode apontar para dentro do carregador, e nada mantido pelo carregador pode apontar para o núcleo (o carregador remove seus métodos de controle antes de cada descarga).
6. **Compile o núcleo numa pasta que o jogo não lê** e deixe `hotreload.py` copiá-lo sobre o arquivo ativo. A ferramenta recusa `--dll` quando esse argumento é o arquivo ativo.

### <a id="state-versioned-saved-before-restored-after"></a>Estado: versionado, salvo antes, restaurado depois

```cpp
static bool save(hotreload::Writer& w)                    { w.u64(g_counter); w.str(g_label); return true; }
static bool restore(uint32_t, hotreload::Reader& r)       { g_counter = r.u64(); g_label = r.str(); return true; }
static void fresh()                                       { g_counter = 0; g_label.clear(); }
COOP_RELOAD_STATE(my_module, "my_module", /*version*/ 1, /*order*/ 50, nullptr, save, restore, nullptr, shutdown, fresh);
```

- Incremente `version` sempre que o formato salvo mudar. Uma nova compilação que não consegue ler o formato anterior (sem função `migrate`) reinicia aquele participante **do zero**, e `hotreload.py` exibe um aviso identificando-o. Uma função `migrate(savedVersion, reader)` converte o formato antigo em vez disso.
- `save` pode executar e depois ser descartado (uma etapa posterior pode recusar a recarga), então não pode mudar nada. Retornar false de `save` recusa a recarga e mantém o núcleo antigo em execução.
- O bloco de dados tem um CRC por participante e um para o bloco inteiro. Dados danificados nunca chegam a `restore`: aquele participante recebe `fresh()`.
- Ordem: salvar e restaurar executam em `order` crescente; encerramento em ordem decrescente. Coloque hooks primeiro (número baixo) e sessões depois, para o encerramento parar sessões antes de remover hooks.
- Identificadores válidos em todo o processo (`SOCKET`, `HANDLE`) podem ser salvos como inteiros e continuam válidos após o desmapeamento se `shutdown` não os fechar.

### <a id="threads-register-every-thread-the-core-owns"></a>Threads: registre todas as threads do núcleo

> **Toda thread pertencente ao núcleo precisa ser registrada, ou a drenagem recusará indefinidamente.**

A drenagem comprova que é seguro desmapear o núcleo examinando todas as outras threads do processo: conta como interna quando o ponteiro de instrução está na imagem do núcleo **ou qualquer endereço de retorno na pilha aponta para ele**. Uma thread executora estacionada à espera de trabalho tem o ponteiro de instrução no kernel, mas sempre tem quadros do núcleo na pilha; portanto, está "dentro".

O responsável por essa thread a interrompe e aguarda seu término no `shutdown` de um participante, que roda depois da drenagem. Por isso, a drenagem precisa ser instruída a ignorá-la:

- Inicie a thread com `hotreload::ManagedThread`, e ela será registrada automaticamente.
- Uma thread que não pode ser iniciada assim (executora criada por biblioteca vinculada, `std::thread` em código fora do seu controle) precisa de `hotreload::adoptThread(tid)` ao iniciar e `releaseThread(tid)` depois de aguardar seu término.
- Uma thread sem nenhum desses registros faz a drenagem esgotar o prazo sempre. A troca é recusada de forma limpa (saída 1, relatório `drain timed out ... thread 1234 is still inside the code that would be unloaded`), o núcleo antigo continua e nada se perde. O núcleo de exemplo compilado como `core_unregistered` faz exatamente isso, e o cenário `unregistered_thread_refuses` verifica a recusa.
- Uma thread que não é sua (as do próprio jogo) não é problema se não houver código do núcleo na pilha. Se o motor chamar o núcleo de sua própria thread (hook, callback), ela conta como interna enquanto a chamada roda, e a drenagem aguarda sua saída.

### <a id="mods-that-patch-code-in-the-game"></a>Mods que modificam código no jogo

A camada de integração não conhece seus hooks. Forneça três callbacks uma vez, com `hotreload::SetDrainHooks`: `suspend` restaura o código original para impedir novas entradas em desvios, `resume` reinstala os hooks quando a drenagem recusa, e `extraRanges` acrescenta os intervalos de endereços dos trampolins para uma thread em código gerado contar como ocupada. Registre uma sonda de vazamento para hooks instalados (`hotreload::global().addLeakProbe`), para um hook não removido impedir a descarga.

## <a id="quick-start-no-game-needed"></a>Primeiros passos (sem jogo)

Compile, inicie o host de teste e troque para a segunda compilação de exemplo:

```
cmake -S tools/hotreload -B build/hotreload
cmake --build build/hotreload --config Release --parallel 1
mkdir build\hotreload\demo
copy build\hotreload\bin\core_v1.dll build\hotreload\demo\core.dll
build\hotreload\bin\hotreload_test_host.exe --loader build\hotreload\bin\hotreload_loader.dll --core build\hotreload\demo\core.dll --pipe demo
```

Em um segundo terminal:

```
python -I tools/hotreload/hotreload.py status --pipe demo
python -I tools/hotreload/hotreload.py swap --pipe demo --dll build/hotreload/bin/core_v2.dll --dry-run
python -I tools/hotreload/hotreload.py swap --pipe demo --dll build/hotreload/bin/core_v2.dll
```

O relatório JSON vai para stdout; o progresso, para stderr. Encerre o host de teste com `python -I -c "import sys; sys.path.insert(0,'tools/hotreload'); import hotreload; c=hotreload.PipeClient.connect('demo'); c.call('host.quit')"` ou feche a janela.

Para seu jogo, substitua o host de teste pelo carregador e o núcleo de exemplo pelo seu. Inicie o jogo uma vez e, após cada compilação:

```
python -I tools/hotreload/hotreload.py swap --pipe mymod-0 --dll build/mymod_core.dll
```

Várias cópias em execução (host e cliente de um teste cooperativo): repita `--pipe`. Todas são verificadas primeiro; nada é alterado se alguma não puder recarregar. Depois, são trocadas uma após a outra, parando na primeira falha.

### <a id="options"></a>Opções

| Opção | Significado |
|---|---|
| `--pipe NAME` | Pipe de controle da cópia em execução (nome curto ou caminho completo `\\.\pipe\...`). Repita para várias cópias. |
| `--dll PATH` | Núcleo recém-compilado. |
| `--dry-run` | Verifica todas as cópias e relata `would swap` ou `unchanged`. Não altera nada. |
| `--force` | Recarrega mesmo se a cópia já executar esses bytes. |
| `--root DIR` | Recusa se o arquivo do núcleo de alguma cópia não estiver em `DIR` (proteção contra sobrescrever outra instalação). |
| `--reload-timeout-s N` | Quanto aguardar por `dev.reload` (padrão 90). |
| `--replace-wait-s N` | Quanto repetir se o arquivo do núcleo estiver bloqueado (padrão 5). |
| `--connect-wait-s N` | Quanto esperar o pipe aparecer (padrão 3). |
| `--out FILE` | Também escreve o relatório JSON num arquivo. |

### <a id="exit-codes"></a>Códigos de saída

| Código | Significado |
|---|---|
| 0 | Toda cópia executa a nova compilação (ou já executava), ou `--dry-run` não encontrou problema. |
| 1 | Uma cópia falhou. O relatório identifica a verificação. O núcleo antigo pode continuar ou ter sido restaurado. |
| 2 | **Recusado antes de qualquer alteração**, com motivo em stderr e no relatório. |

O que produz cada resultado:

| Situação | Resultado |
|---|---|
| Sem pipe de controle (jogo parado ou sem carregador). | Saída 2, "no control pipe". |
| Compilação monolítica: pipe responde, mas não tem `dev.status` / `dev.reload`. | Saída 2, "monolith build". |
| Carregador antigo: `dev.status` sem `buildId`, impossibilitando comprovar a troca. | Saída 2, "old loader". |
| `--dll` não é núcleo (sem exportação `HotCore_Init`: carregador, arquivo de texto ...). | Saída 2. |
| `--dll` é o próprio arquivo ativo da cópia. | Saída 2. |
| Arquivo do núcleo fora de `--root`. | Saída 2. |
| Uma de várias cópias não pode recarregar. | Saída 2, as outras também não são alteradas. |
| Drenagem recusa (thread ainda interna, geralmente não registrada). | Saída 1, núcleo antigo continua. |
| `save` ou `canUnload` de participante recusa. | Saída 1, núcleo antigo continua. |
| Inicialização do novo núcleo falha. | Saída 1, antigo é mapeado novamente com seu estado. |
| Carregador mapeia o arquivo original, bloqueando a compilação. | Saída 1, "cannot replace". |
| Alteração do próprio carregador. | Impossível: ele nunca é descarregado; reinicie uma vez. |

## <a id="build-id"></a>ID da compilação

O ID é `<crc32 hex>-<size in bytes>` dos bytes exatos mapeados (cópia de cache). O carregador o relata em `dev.status`. `hotreload.py` calcula o mesmo texto para o arquivo copiado e compara: "o núcleo em execução é a compilação que acabei de copiar" é um fato verificado, não uma expectativa. Uma recarga que responde `ok`, mas mantém a compilação antiga, falha na verificação.

## <a id="the-control-channel"></a>O canal de controle

Pipe nomeado Windows, um objeto JSON por linha, um cliente por vez:

```
{"id":1,"method":"dev.status"}                    ->  {"id":1,"result":{"loaded":true,"generation":2,"buildId":"a1b2c3d4-95744",...}}
{"id":2,"method":"dev.reload","params":{"reason":"hotswap","timeoutMs":90000}}
{"id":3,"method":"nope"}                          ->  {"id":3,"error":{"code":-32601,"message":"unknown method: nope"}}
```

- `ping` responde na thread do pipe (`{"pid":...}`), permitindo distinguir "jogo ativo, laço principal travado" de "sem jogo".
- Todos os outros métodos rodam na **thread principal**: `HotReload_OnFrame` executa as solicitações enfileiradas. Um método pode acessar estado sem travas, e a recarga ocorre entre quadros. Se o laço principal não executar a solicitação a tempo, o cliente recebe `-32001`.
- Embutidos: `dev.status` (loaded, generation, reloadCount, corePath, cachePath, buildId, resultado da última recarga), `dev.reload` e, na camada de integração do núcleo, `reload.state` (participantes, versões, threads ativas, resultado das últimas operações de salvar, drenar, encerrar ou restaurar).
- Registre métodos próprios com `api->register_method(name, fn, user)` no núcleo (removidos antes de cada descarga) ou `HotReload_RegisterMethod` no host (preservados). O texto da resposta precisa ser JSON.
- Só um cliente pode manter o pipe por vez. Executor de testes e ferramenta de troca não devem mantê-lo simultaneamente.

O pipe é apenas local (clientes remotos são rejeitados). Não tem autenticação: não o aponte para algo que você não permitiria a outro programa do PC acionar.

## <a id="files-the-loader-writes"></a>Arquivos escritos pelo carregador

Ao lado do arquivo do núcleo (ou em `cache_dir`): `hr_cache\<core stem>.<pid>.<n>.dll` (cópia mapeada, excluída ao descarregar; antigas de processos mortos removidas ao iniciar) e `hr_cache\hotreload.log` (cada carregamento, recarga, recusa e linha de log do núcleo). O núcleo encontra arquivos ao lado da saída da compilação por `api->core_dir`, pois seu próprio arquivo de módulo é a cópia de cache.

## <a id="how-it-is-tested"></a>Como é testado

```
python -I tools/hotreload/run_tests.py
```

Compila com CMake (um trabalho por vez, pasta sob o temporário do sistema salvo `--build-dir`; `--arch Win32` compila 32 bits), executa testes unitários e cenários de troca e verifica cada variante de mutação. Exibe `ALL OK` somente se tudo passar e todas as variantes forem detectadas. Exige cmake e Visual Studio 2022. Nenhum jogo é iniciado: o substituto é `hotreload_test_host.exe`, programa que carrega o carregador, mantém laço principal e atende o pipe. Os cenários o iniciam e encerram por PID.

Cobertura da última execução: 37 testes unitários (131 verificações), 16 cenários de troca e 20 variantes de mutação, todos aprovados em 64 bits e novamente em 32 bits.

- **Testes unitários:** leitor e gravador de bytes, CRC-32, registro (salvar, restaurar, migrar, incompatibilidade de versão, conteúdo e bloco corrompidos, pré-verificação, ordem de encerramento, sondas de vazamento), threads (`ManagedThread`, `adoptThread`), drenagem (thread estacionada no código detectada pelo endereço de retorno, threads listadas ignoradas, tempo esgotado como falha), auxiliares JSON e pipe de controle (ping sem laço principal, métodos na thread que bombeia a fila, erros, clientes sucessivos, tempo esgotado).
- **Cenários de troca** (cada qual inicia o host, executa `python -I hotreload.py` e confere o resultado): estado preservado e ID alterado, com PID do host e threads mantidos; duas cópias; inalterado e forçado; simulação; `status`; seis recusas (sem pipe, monolítico, carregador antigo, não é núcleo, próprio arquivo ativo, fora de `--root`); tudo ou nada; incremento de versão sem migração (início do zero, aviso); thread não registrada (drenagem recusa, antigo continua); falha ao salvar (veta recarga); núcleo que falha ao iniciar (reversão e troca válida posterior funcionando).

**Variantes de mutação.** Cada uma quebra deliberadamente uma regra, compilada só na versão de teste e ativada por `HOTRELOAD_MUT=<n>` (ou nome de falha no cliente). O teste protetor precisa passar sem defeito e falhar com ele.

| Variante | Defeito ativado | Detectada por |
|---|---|---|
| `drain_off` | Drenagem afirma "ninguém dentro" sem examinar. | `unregistered_thread_refuses` |
| `adopt_ignored` | `adoptThread` não faz nada. | `swap_carries_state` |
| `managed_ids_ignored` | Drenagem não ignora `ManagedThread`s. | `swap_carries_state` |
| `no_cache_copy` | Carregador mapeia original, bloqueando compilação. | `swap_carries_state` |
| `stale_build_id` | Mantém ID antigo após recarga. | `swap_carries_state` |
| `version_ignored` | Formato antigo de estado lido como atual. | `swap_carries_state` |
| `no_state_blob` | Núcleo antigo nunca transfere o estado. | `swap_carries_state` |
| `save_failure_ignored` | Falha de `save` não veta mais a recarga. | `save_failure_vetoes` |
| `no_rollback` | Carregador permanece inativo quando novo núcleo falha. | `bad_core_rolls_back` |
| `veto_ignored` | Carregador descarrega apesar da recusa. | `save_failure_vetoes` |
| `exit1_on_refusal` | Cliente sai com 1 em vez de 2 na recusa. | `refuse_no_control_channel` |
| `no_buildid_check` | Cliente não recusa carregador antigo. | `refuse_old_loader` |
| `dry_run_writes` | `--dry-run` copia a DLL. | `dry_run_changes_nothing` |
| `root_ignored` | `--root` não é aplicado. | `refuse_outside_root` |
| `crc_unchecked` | Conteúdo corrompido chega a `restore`. | Teste unitário. |
| `forward_shutdown` | Encerramento segue ordem de registro. | Teste unitário. |
| `thread_not_joined` | `ManagedThread` se desanexa em vez de aguardar término. | Teste unitário. |
| `drain_ip_only` | Drenagem verifica só ponteiro de instrução. | Teste unitário. |
| `drain_timeout_ok` | Tempo de drenagem esgotado conta como sucesso. | Teste unitário. |
| `preflight_ignored` | Recusas de `canUnload` não vetam. | Teste unitário. |

## <a id="limits"></a>Limitações

- Somente Windows. Não pressupõe tamanho de ponteiro (testado em 64 e 32 bits).
- O carregador nunca é descarregado. Mudar carregador, `abi.h` ou algo mantido por objeto do lado do carregador exige uma reinicialização normal do jogo.
- Um cliente de controle por vez.
- Testes usam host substituto, não jogo real. Um motor real acrescenta threads, hooks e callbacks; num mod novo, execute primeiro `--dry-run`, depois uma troca num salvamento descartável, e leia `hr_cache\hotreload.log` e `reload.state` se a drenagem recusar.
- Threads brutas, hooks e sockets do núcleo não registrados são responsabilidade do mod: a biblioteca encontra o problema de threads (drenagem recusa), mas não vê um hook instalado sem uma sonda de vazamento.

## <a id="changes-from-the-original"></a>Alterações em relação ao original

Generalizado do commit e85460f de fnv-coop ([github.com/cranebeaker/fnv-coop](https://github.com/cranebeaker/fnv-coop)).

- Renomeado para namespace neutro `hotreload`, exportação `HotCore_Init`, `COOP_RELOAD_STATE` e chave do bloco de estado `coop.reload.state`. Protocolo de transmissão, ID de compilação, sequência de recarga e drenagem são os mesmos.
- Carregador não depende mais da interface de plugins do jogo nem da ponte original. Pipe de controle é um servidor pequeno autossuficiente (`hotreload_control`). Todos os métodos executam na thread principal, eliminando a barreira de chamadas em andamento do original.
- Removidos espelhamento de configuração (copiar INI e arquivos de dados do mod para cache) e monitor de arquivos. `api->core_dir` informa ao núcleo onde fica a saída da compilação.
- Modificação de hooks e proteção de escrita que congela threads não incluídas. `SetDrainHooks` é a interface genérica para elas.
- Cliente recebe nome de pipe em vez de número de instância, troca várias cópias e tem proteção `--root` em vez de verificar a pasta da instância.
- Novos: núcleo de exemplo, host de teste, testes unitários, cenários e variantes de mutação.

Licença: MIT, como o restante deste repositório.
