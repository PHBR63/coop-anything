# <a id="co-op-flight-recorder-and-desync-analyzer"></a>Gravador de eventos cooperativos e analisador de dessincronização

Uma caixa-preta para mods cooperativos de qualquer jogo. Cada máquina registra o que enviou, recebeu, decidiu e aplicou, além de resumos de estado, em um pequeno arquivo `.cofr` ("co-op flight record"). Coloque arquivos de 2 a 4 máquinas lado a lado; o analisador informa **onde os mundos divergiram primeiro, até o grupo de hash, a chave e o valor, e quais mensagens levaram até ali**. Depois pode reduzir a execução problemática às poucas etapas relevantes e escrever um teste de regressão.

Duas partes, um formato:

| Parte | Onde | O que faz |
|---|---|---|
| Gravador | `cpp/` | C++17 independente (só biblioteca padrão). Buffer circular em memória, escrito em arquivo em dessincronização, falha ou solicitação. Aproximadamente um microssegundo por evento. |
| Analisador | `*.py` | Python 3, sem dependências ou conhecimento do jogo. Leitura e exibição formatada, alinhamento de 2 a 4 máquinas, primeira divergência, redução por depuração delta, geração de regressões, relatório HTML. |
| Formato | [FORMAT.md](FORMAT.md) | Organização dos bytes, esquema, algoritmo de resumo e contrato do hook de reprodução. Permite escrever arquivos em qualquer linguagem. |

O guia [Busca de dessincronizações com rastreamentos e redução](../../playbook/desync-hunting.md) mostra o fluxo completo.

### <a id="host-portability"></a>Portabilidade entre ambientes

No Windows, ao criar nova compilação CMake, o executor tenta Visual Studio 2026, Visual Studio 2022 e depois Ninja. Ninja exige compilador C++17 configurado no PATH. Cache CMake existente mantém seu gerador; caminhos de compilador contendo "Visual Studio" não transformam uma compilação Ninja em MSBuild.

Comandos de reprodução podem ser listas de argumentos (preferíveis para chamadas de API) ou strings. Strings Windows usam aspas no estilo CRT, incluindo caminhos com espaços, barras invertidas antes de aspas e aspas duplicadas dentro de argumentos entre aspas. Strings POSIX mantêm análise `shlex`. Nenhum caminho permite execução por shell. O grupo `PortabilityTests` confere ambos os analisadores e a escolha de gerador/cache sem jogo nem todas as versões Visual Studio instaladas.

## <a id="try-it-in-one-minute"></a>Experimente em um minuto

O repositório inclui dois pares de rastreamentos de exemplo feitos pelo gravador C++ ([golden/](golden)). Em `desync_*`, um script do cliente sobrescreveu silenciosamente um valor:

```
python -I tools/flight/flight.py diverge tools/flight/golden/desync_host.cofr tools/flight/golden/desync_client.cofr
```

```
FIRST DIVERGENCE (digest) at 680.000ms: world digest (epoch 1, seq 5) differs: ... differing 0xA21A963AA6B76AAB: slot 0 'stage.q1 = 10' vs slot 1 'stage.q1 = 99'
  key: world:0xA21A963AA6B76AAB   suspect slot(s): [0, 1]   (2 candidate(s) in total)
  narrowing: bucket(s) 171 of 256
    key 0xA21A963AA6B76AAB (bucket 171)  [from this digest]
      slot 0: value hash 10  stage.q1 = 10
      slot 1: value hash 99  stage.q1 = 99
  causal chain, window 290.000ms .. 680.000ms:
        290.000ms slot 0 TxnCaptured  commit seq=3 ...
        ...
        325.000ms slot 1 TxnApplied   seq=4[0] origin=0 epoch=1 tag=1 hash=8d0f343480ecf481
        325.000ms slot 1 ScriptWrite  seq=4 key=stage.q1 value=99
```

A cadeia começa no último resumo em que as máquinas concordaram e termina no divergente; o bug fica entre eles. `ScriptWrite` é um registro definido pelo jogo (veja o esquema abaixo).

## <a id="add-the-recorder-to-your-mod"></a>Adicione o gravador ao mod

[cpp/example_usage.cpp](cpp/example_usage.cpp) é um exemplo completo, compilado e executado. Etapas:

1. **Adicione os arquivos.** Inclua `tools/flight/cpp` no caminho de cabeçalhos e `cofr.cpp` na compilação, ou use `add_subdirectory(tools/flight/cpp)` e vincule o alvo `cofr`. Nada mais: `cofr.h` e `cofr.cpp` usam só a biblioteca padrão. Os hooks do jogo precisam apenas de `observer.h`.
2. **Crie um `cofr::Recorder` por máquina.** Forneça espaço, papel, rótulo, pasta e, opcionalmente, esquema e decodificador:

   ```cpp
   cofr::Config cfg;
   cfg.slot = 1; cfg.role = cofr::kRoleClient; cfg.label = "client-1";
   cfg.dir = "flight";                  // dumps go here
   cfg.ringBytes = 16u << 20;           // the newest 16 MB of records are kept
   cfg.schemaJson = R"({"game":"mygame","digest_categories":{"0":"quests","1":"npcs"}})";
   cfg.decoder = decodeMyProtocol;      // optional, see below
   cofr::Recorder recorder(cfg);
   recorder.mapPeer(0, 0);              // transport peer 0 is the host (slot 0), if your peer ids are not slots
   ```
3. **Chame pelos hooks.** Envolva envio e consulta de transporte e a função que aplica alterações ao mundo:

   ```cpp
   obs->setFrame(frame);                          // once per frame
   obs->netOut(peer, bytes, size);                // every datagram sent
   obs->netIn(peer, bytes, size);                 // every datagram received
   obs->captured(commit);                         // the host decided a change set (cofr::CapturedEvent)
   obs->applied(effect);                          // one effect applied to the local world (cofr::AppliedEvent, with a hash of the effect)
   obs->digest(world.digest(0, epoch, seq));      // every few seconds at a quiet point
   obs->ownership(event);                         // an actor changed owner
   obs->marker(cofr::kMarkNote, "player joined"); // anything you want to see in the chain
   ```
   `obs` é um `cofr::IObserver*`: o gravador em compilação de teste; pode ser nulo na distribuída.
4. **Descarregue quando houver problema.** `recorder.onDesync("what you saw")` escreve marcador e arquivo (por padrão, no máximo 8 por execução e um a cada 30 s); `recorder.dump(path)` escreve sob demanda; `recorder.dumpCrash()` serve para filtro de falha e não espera a trava. Na dessincronização, escreva primeiro os detalhes para o analisador chegar à chave: `recorder.digestDetail(category, epoch, seq, entries)` e um `recorder.entryText(key, valueHash, "readable text")` por entrada. `cofr::BucketedState` mantém o resumo atualizado uma entrada por vez.
5. **Torne estáveis os hashes de efeitos.** O analisador compara o hash do mesmo efeito em máquinas diferentes. Calcule sobre o conteúdo, não ponteiros, endereços ou dados variáveis entre execuções (`cofr::hash64` é FNV-1a 64; qualquer hash estável serve).

### <a id="the-decoder-and-the-schema"></a>Decodificador e esquema

* **Decodificador** (opcional): `bool(const uint8_t* data, size_t size, NetMeta& out)`. Executa ao descarregar, nunca ao registrar datagrama. Preencha tipo da mensagem, sessão, época e intervalo de números de alteração (`seqLo`, `seqHi`) carregado. Sem ele, todos os datagramas permanecem como bytes brutos e o analisador ainda associa envios e recebimentos. Com ele, associa datagrama à transação transportada. Pode informar que um datagrama contém resumo do estado do remetente (`NetMeta::hasDigest`); o gravador acrescenta então registro Digest "derivado".
* **Esquema** (JSON opcional, guardado em todo arquivo): nomes de categorias de resumo, tipos de marcadores, operações de responsabilidade e mensagens, e organização dos seus próprios registros (32 a 255, escritos com `recorder.custom(type, bytes)`). Sem esquema, usa o conjunto de exemplo (história, atores, contêineres, objetos, outros). Lista de chaves na seção 5 de [FORMAT.md](FORMAT.md); [schemas/example_game.json](schemas/example_game.json) é um exemplo pequeno.

### <a id="from-another-language"></a>A partir de outra linguagem

O formato consiste em registros little-endian simples; qualquer linguagem pode escrevê-lo. `cofr.py` tem um escritor (`cofr.dump(path, header, records)`); organização exata em [FORMAT.md](FORMAT.md). Um mod C#, Lua ou Rust pode escrever diretamente ou enviar eventos a um auxiliar pequeno.

## <a id="analyzer-commands"></a>Comandos do analisador

Todos executam como `python -I tools/flight/flight.py <command> ...`. Acrescente `--schema FILE` a print, align, diverge, report ou fixture para substituir o esquema dos arquivos.

| Comando | O que faz |
|---|---|
| `print FILE [--type NetIn,Digest] [--limit N]` | Exibe um rastreamento formatado. |
| `align FILE FILE [FILE FILE]` | Alinha 2 a 4 máquinas: diferenças de relógio, mensagens correspondentes, perdidas e duplicadas. |
| `diverge FILE FILE [...] [--json] [--check]` | Primeira divergência, reduzida a grupo, chave e valor, com cadeia causal. `--check` encerra com 1 se encontrar. |
| `report FILE FILE [...] -o report.html [--shrink shrunk.json]` | Relatório HTML independente: máquinas, linha do tempo, primeira divergência, cadeia e reprodução mínima. |
| `fixture FILE FILE [...] -o fixture.json` | Constrói dados de reprodução: uma etapa por datagrama recebido por máquina. |
| `shrink fixture.json --replay-cmd "prog {fixture}" -o shrunk.json` | Depuração delta até lista mínima com a mesma falha. `--replay-py module:function` usa função Python em vez de programa. |
| `gentest shrunk.json --name stale_echo [--out DIR]` | Escreve teste de regressão: dados reduzidos e linha CMake `add_test`. |
| `regress DIR --replay-cmd "prog {fixture}"` | Executa todos os casos da pasta pelo hook; exibe ALL OK se cada resultado corresponder ao esperado. |
| `schema [FILE]` | Exibe esquema padrão ou verifica e reexibe um arquivo de esquema. |
| `from-failure [PATH ...]` | Converte execução de bot com falha em reprodução off-line e caso de regressão; veja a próxima seção. Igual a `from_failure.py`. |

### <a id="the-replay-hook"></a>Hook de reprodução

O redutor não conhece o jogo. Você fornece um **hook de reprodução**: programa (ou função Python) que recebe os dados, reproduz no ambiente de testes e informa se o bug persiste. Contrato na seção 7 de [FORMAT.md](FORMAT.md); [toy_replay.py](toy_replay.py) é exemplo completo das duas formas, usado nos testes:

```
python -I tools/flight/flight.py shrink fixture.json --replay-cmd "python -I tools/flight/toy_replay.py {fixture}" -o shrunk.json
python -I tools/flight/flight.py shrink fixture.json --replay-py toy_replay:replay --replay-path tools/flight -o shrunk.json
```

Etapas precisam ser independentes (qualquer subconjunto é válido); uma marcada `"pin": true` nunca é removida. Usa o algoritmo ddmin de Zeller e Hildebrandt; lista menor só vale se mantiver a assinatura da falha. Redução que transforma o bug em outro é rejeitada.

## <a id="from-a-failed-game-run-to-a-regression-case"></a>De uma execução de jogo com falha a um caso de regressão

Quando uma etapa do bot (`tools/bots`) falha, o executor salva `failure.json` e evidências de cada cópia em pasta `FAIL-*`. Com ambas ainda abertas, isto só lê arquivos e leva alguns segundos:

```
python -I tools/flight/from_failure.py                         # the newest failure under ./coop-bots-out
python -I tools/flight/from_failure.py coop-bots-out/RUN       # every failure.json below that run folder
python -I tools/flight/from_failure.py host.cofr client.cofr   # two recordings given directly
python -I tools/flight/from_failure.py FAIL-DIR --instances DIR --report failure.html
```

Localiza as gravações do host e cliente indicadas, passa pelo analisador, exibe **REPRODUCED** ou **NOT REPRODUCED**, compara com o que os bots viram no estado ao vivo (`counters`, `seq` e `synced` de cada máquina, veja [tools/bots](../bots/README.md)), reduz os registros à mesma falha e escreve `tools/flight/regress/<name>.json`. `--no-write` só dá o veredito; `--report FILE.html`, relatório completo com reprodução mínima; `--json`, resultado bruto. Saída 0 = todas reproduzidas, 1 = ao menos uma não reproduzida, 2 = gravações ausentes ou ilegíveis.

* **Onde procura gravações.** Entrada de máquina em `failure.json` indica gravação por `flight_dump` (caminho ou `{"path": ...}`), `flight`, `recording`, `cofr` ou `trace`, no topo ou no dicionário `capture` retornado por `capture()` do adaptador (também vale qualquer valor cujo nome corresponda a `--pattern`, padrão `*.cofr`). Caminhos relativos são tentados em `<root>/<instance>/`, `<root>/`, subpasta `<machine name>/` da falha, pasta da falha e depois como escritos. `<root>` vem de `--instances DIR` ou variável `COOP_INSTANCES_ROOT`: pasta com uma subpasta por cópia. Sem caminho registrado, usa o arquivo correspondente mais novo escrito nos 10 minutos anteriores, na subpasta de falha da máquina ou cópia do jogo.
* **O caso.** Guarda registros reduzidos como `cofr-trace-1` (seção 7 de [FORMAT.md](FORMAT.md)); `python -I tools/flight/regress.py tools/flight/regress` reproduz em um segundo sem jogo ou programa de reprodução. Fixa a evidência gravada: passa enquanto ela mostrar a falha. Gravação não muda ao corrigir mod; a comprovação exige nova execução: repita a luta, execute `from_failure.py` na nova pasta, e NOT REPRODUCED (saída 1) indica sucesso. `--expect-converges` inverte o caso (falha até o analisador parar de ver a falha). `--schema FILE` usa outro esquema, preservado no caso. Caminhos de máquinas são removidos.
* **Formato próprio.** A parte genérica só lê `.cofr`. Para outro formato, forneça `--converter module:function` (módulo em `--converter-path DIR`, ou `path/to/file.py:function`) e, se os nomes não forem `*.cofr`, `--pattern GLOB`. O hook é uma função:

  ```python
  def convert(path: str, info: dict) -> bytes:
      """path: the recording as found. info: {"name": ..., "role": ..., "instance": ...} of the machine (a value may be None).
      Return the bytes of a version 1 .cofr file (FORMAT.md). Raise any exception to report that the file cannot be converted."""
  ```

  O conversor padrão retorna o arquivo intacto. O caso escrito mantém os registros convertidos; reproduz sem seu conversor.

## <a id="how-it-is-tested"></a>Como é testado

Um comando na raiz executa tudo e exibe `ALL OK`:

```
python -I tools/flight/run_tests.py
```

| Parte | O que executa |
|---|---|
| C++ (cmake, Visual Studio 2022 no Windows, `--parallel 1`) | `cofr_tests`: 40 testes (comportamento do gravador, volta do buffer, truncamento, threads, resumos por grupos, registro de esquema, registros personalizados, arquivos de referência, custo), 12 variantes de mutação; mais o exemplo. Compilado em pasta temporária do sistema (`COFR_BUILD_DIR` altera), sem escrever no repositório. |
| Python | 115 testes: leitura/escrita do formato, regras do esquema, alinhamento de 2 a 4 máquinas, todos os tipos de divergência, redução do escopo, redutor com programa e função Python, regressões, HTML, CLI de ponta a ponta e ferramentas falha-para-caso (48: localizar gravações, conversor, comparação de estados, etapas de redução, casos/reprodução, saídas), todos com gravações simuladas do escritor `cofr.py` e pastas de falha simuladas. |
| C++ escreve, Python lê | Testes C++ escrevem rastreamentos de referência e outro com todos os registros e opções; Python lê campo por campo, recalcula resumo por grupos pelos detalhes, obtém os mesmos bytes e os reescreve idênticos. No sentido inverso, Python escreve e teste C++ lê. Teste de divergência de formato falha se os bytes diferirem de `golden/`. |
| Variantes de mutação | Uma **variante** quebra algo deliberadamente e a suíte precisa falhar. 12 C++ reintroduzem bugs (buffer cheio descarta registro novo, datagramas recebidos não registrados, corte não sinalizado, valor alterado invisível nos grupos...). 140 Python editam fontes (divergência mais recente em vez da primeira, reparos contados como divergências, etapas fixadas removidas, relatório sem escape, conversor ignorado, gravação mais antiga escolhida...) e cada uma precisa reprovar a suíte. |

Exige Python 3, cmake 3.20 ou superior (para `ctest --test-dir`) e compilador C++17. Executado com Python 3.11, cmake 4.1 e Visual Studio 2022. A execução completa leva alguns minutos, principalmente nas variantes Python. Opções: `--quick` só testes Python rápidos (segundos, exibe `QUICK OK`); `--no-cpp` pula C++; `--no-twin` pula variantes Python; `--only A,B` só classes Python A e B (usado pelas variantes falha-para-caso). Somente a execução completa exibe `ALL OK`. Para regenerar referências após mudar deliberadamente o formato: execute `cofr_tests` C++ com `COFR_WRITE_GOLDEN=1` e `COFR_GOLDEN_DIR=tools/flight/golden`, depois a suíte novamente.

### <a id="recording-overhead"></a>Custo da gravação

O benchmark de `cofr_tests` exige limite de 100 microssegundos por quadro. No PC de origem (x64 Release, execuções repetidas): 0,01 a 0,2 microssegundo por quadro ocioso (par de confirmações a cada meio segundo, resumo a cada dois segundos) e 7 a 22 microssegundos por quadro ocupado (20 datagramas enviados, 20 recebidos, 10 efeitos aplicados). Resumo por grupos de 20.000 entradas custa cerca de 0,1 ms. Após alterar uma entrada em estado de 200.000, `BucketedState` produz o novo resumo em aproximadamente 3 microssegundos (mediana), frente a 1 ms da passagem completa.

## <a id="what-it-does-not-do"></a>O que não faz

* Registra o que os hooks relatam. Alteração não vista pelos hooks não entra.
* O rastreamento contém hashes das decisões do host, não as decisões; dados derivados reproduzem o recebido por cada máquina, não o decidido pelo host.
* Associar envio ao recebimento depende de o ID remoto do transporte significar o espaço da outra máquina (ou entrada `mapPeer`). Com bytes idênticos retransmitidos, qual cópia se perdeu é uma hipótese; a quantidade está correta.
* O buffer mantém os registros mais novos. Dessincronização anterior ao registro mais antigo aparece como nota de alinhamento ("lost N old records"). Use buffer maior ou descarregue antes.

## <a id="credits-and-origin"></a>Créditos e origem

Adaptado do commit f57aa78 de fnv-coop ([github.com/cranebeaker/fnv-coop](https://github.com/cranebeaker/fnv-coop)), feito para um mod de Fallout: New Vegas. Esta versão é independente de jogo: formato `.cofr` neutro com esquema configurável, gravador com pequena interface própria de observação sem dependência do núcleo daquele projeto e analisador que lê do esquema tudo que é específico. Permaneceram no fnv-coop: decodificador do protocolo, invólucros do transporte e destino de efeitos, adaptador do modelo do motor, serviço do plugin (filtro de falhas, comandos da ponte) e cache de resumos do estado.

Atualizado a partir do commit e85460f de fnv-coop.

Ideias de projetos abertos: gravar e reproduzir como em [rr](https://rr-project.org/); simulação determinística, capturas de estado e detecção de dessincronização de [Gaffer on Games](https://gafferongames.com/); depuração delta (ddmin), Andreas Zeller e Ralf Hildebrandt, "Simplifying and Isolating Failure-Inducing Input" (2002). FNV-1a: Glenn Fowler, Landon Curt Noll e Phong Vo; SplitMix64: Sebastiano Vigna (domínio público).

Licença: MIT, como o restante do repositório.
