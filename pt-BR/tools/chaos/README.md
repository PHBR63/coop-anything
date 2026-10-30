# <a id="chaos-box-a-bad-network-between-two-copies-of-any-game"></a>Simulador de caos: uma rede ruim entre duas cópias de qualquer jogo

Pequena ferramenta que fica entre host e cliente de qualquer jogo ou mod UDP e degrada o enlace: atraso, variação de latência, perda, perda em rajadas, reordenação, duplicatas, inversão de bits, limite de largura de banda, interrupções em um sentido e desconexões completas. Você muda o perfil enquanto o jogo roda, por script ou linha de comando.

O mesmo modelo de perturbação também existe como arquivo C++ apenas com cabeçalho, para um simulador ou fuzzer independente do jogo usar exatamente a mesma rede. Uma verificação cruzada comprova resultados idênticos entre Python e C++ para a mesma semente.

Por que usar: sincronização cooperativa que funciona em LAN muitas vezes falha na internet real. Uma perda descarta atualização, a reordenação aplica duas fora de ordem, uma duplicata aplica uma duas vezes, uma interrupção longa deixa o cliente para trás. Teste essas situações de propósito, sempre com a mesma semente, para poder repetir e corrigir a falha.

Python 3.8 ou posterior, somente biblioteca padrão. A versão C++ precisa de cmake e compilador C++17 (opcionais, apenas para a verificação cruzada).

## <a id="quick-start-put-the-relay-between-a-host-and-a-client"></a>Primeiros passos: coloque o retransmissor entre host e cliente

O retransmissor escuta numa porta UDP e encaminha cada datagrama ao servidor real através do modelo de perturbação. Cada endereço de cliente recebe seu próprio socket de saída, para o host ver participantes separados, como em NAT.

1. Inicie o host do jogo normalmente. Suponha que ele escute na porta UDP 27970 deste PC.
2. Inicie o retransmissor à sua frente:

   ```
   python -I tools/chaos/chaos.py relay --target 127.0.0.1:27970 --profile bad_wifi --log out/chaos/run.jsonl
   ```

   Exibe uma linha, por exemplo `{"listen": 53211, "rpc": 53212, "log": "out/chaos/run.jsonl"}`. `listen` é a porta de conexão do cliente. `rpc` é a porta de controle (seção abaixo).
3. Direcione o cliente para `127.0.0.1:<listen>` em vez da porta do host. Agora ele conversa com o host pela rede degradada.
4. Mude a rede enquanto o jogo roda:

   ```
   python -I tools/chaos/chaos.py call --rpc-port 53212 set_profile '{"profile":"hell"}'
   python -I tools/chaos/chaos.py call --rpc-port 53212 partition '{"dir":"s2c","on":true,"duration_ms":4000}'
   python -I tools/chaos/chaos.py call --rpc-port 53212 stats
   ```

Opções de `relay`:

| Opção | Significado |
|---|---|
| `--target host:port` | Servidor real. Obrigatório. Pode ser outro PC; nesse caso, o retransmissor envia por qualquer interface local. |
| `--listen N` | Porta UDP para clientes (0 escolhe uma livre, padrão). |
| `--bind ADDR` | Endereço de escuta. Padrão `127.0.0.1`. Use `0.0.0.0` para outros PCs conectarem ao retransmissor. |
| `--profile NAME` | Perfil inicial, padrão `lan`. |
| `--seed N` | Sobrescreve a semente do perfil para obter outra sequência reproduzível. |
| `--rpc-port N` | Porta de controle (0 escolhe uma). Sempre permanece em loopback. |
| `--log FILE` | Escreve log de pacotes (JSON Lines, formato abaixo). |
| `--info-file FILE` | Escreve `{listen, rpc, log}` como JSON quando estiver ativo. Útil para scripts. |
| `--seconds N` | Para após N segundos. Padrão: executar até `shutdown` ou Ctrl+C. |

Duas observações:

- O retransmissor é um salto em um PC. A latência solicitada se soma à real da máquina e é por sentido; um perfil de 35 ms acrescenta cerca de 70 ms de ida e volta.
- Cliente que muda a porta de origem parece um novo participante, como em qualquer NAT.

Se o jogo não puder usar outra porta (porta fixa), execute o host em outra e deixe o retransmissor escutar na porta esperada pelo cliente, ou use uma ferramenta de sistema como [clumsy](https://github.com/jagt/clumsy) (Windows, baseada em WinDivert) nos primeiros experimentos rápidos; volte a este retransmissor quando precisar de sementes reproduzíveis, controle ao vivo por script e log de pacotes.

## <a id="profiles"></a>Perfis

Todos os atrasos são de um sentido, por direção. `loss` é a perda base. `burst_*` controlam um modelo Gilbert-Elliott de dois estados (o enlace alterna entre bom e ruim, com perda muito maior no estado ruim; assim, descartes vêm agrupados como em Wi-Fi e rede móvel reais). A tabela `profiles.json` é a fonte única de dados para as duas linguagens.

| Perfil | Latência +/- variação | Perda base | Rajadas | Reordenação | Duplicação | Limite de banda | Uso |
|---|---|---|---|---|---|---|---|
| `lan` | 0,5 +/- 0,2 ms | 0 | nenhuma | 0 | 0 | nenhum | Referência. Quase perfeita. |
| `good_wifi` | 12 +/- 4 ms | 0,5% | nenhuma | 0 | 0 | nenhum | Wi-Fi doméstico normal. |
| `bad_wifi` | 35 +/- 25 ms | 2% | entrada 1%, saída 25%, perda de 60% no estado ruim | 2% | 0,5% | nenhum | Wi-Fi ocupado ou distante. Principal perfil para bugs de sincronização. |
| `mobile_tether` | 70 +/- 40 ms | 1% | entrada 1%, saída 20%, perda de 50% no estado ruim | 1% | 0 | 2 Mbit/s, fila de 300 ms | Acesso por hotspot de celular. |
| `transatlantic` | 90 +/- 8 ms | 0,3% | nenhuma | 0 | 0 | nenhum | Jogadores em dois continentes. Limpo, mas lento. |
| `hell` | 200 +/- 150 ms | 8% | entrada 3%, saída 10%, perda de 90% no estado ruim | 10% | 5% | 512 kbit/s, fila de 500 ms | Estresse. Se a sincronização sobreviver, é robusta. |

Cada perfil tem semente fixa. Execute o mesmo duas vezes com a mesma sequência de pacotes para obter descartes e atrasos iguais. Os sentidos usam fluxos aleatórios separados, identificados como `c2s` (cliente para servidor) e `s2c` (servidor para cliente).

Parâmetros que podem ser sobrescritos por `set_params`:

| Chave | Significado |
|---|---|
| `latency_ms`, `jitter_ms` | Atraso uniforme de latência mais ou menos variação, nunca abaixo de 0. |
| `loss` | Chance de descartar um pacote no estado bom. |
| `burst_enter`, `burst_exit`, `burst_loss` | Chance por pacote de bom para ruim, de ruim para bom e de perda enquanto ruim. |
| `reorder` | Chance de pacote pular a latência e ultrapassar os anteriores. |
| `duplicate` | Chance de entregar um pacote duas vezes. |
| `corrupt` | Chance de inverter um bit do pacote. |
| `bandwidth_bps`, `buffer_ms` | Limite de taxa com fila que descarta no fim. 0 significa ilimitado. |
| `seed` | Semente aleatória. |

Além do perfil, é possível ativar e desativar a qualquer momento uma partição em um sentido e uma desconexão temporizada nos dois.

## <a id="live-control-json-rpc"></a>Controle ao vivo (JSON-RPC)

O retransmissor atende JSON-RPC 2.0 delimitado por novas linhas via TCP na porta `rpc` (somente loopback). No shell, use `chaos.py call --rpc-port P <method> '<json params>'`. Pelo Python:

```python
import sys
sys.path.insert(0, "tools/chaos")
import client                      # thin functions, the rpc argument is a port, "host:port" or the --info-file path
client.set_profile("out/info.json", "bad_wifi")
client.partition("out/info.json", "s2c", seconds=3)   # host to client blackout for 3 s, then it heals itself
client.disconnect("out/info.json", 5)                  # both directions down for 5 s
print(client.stats("out/info.json"))
```

Ou pelo nível mais baixo, `relay.ChaosClient(port).call(method, **params)`.

| Método | Parâmetros | Efeito |
|---|---|---|
| `status` | | Alvo, perfil, contagem de clientes, parâmetros por sentido, indicadores de partição e interrupção. |
| `stats`, `reset_stats` | | Contadores por sentido: vistos, encaminhados, descartados, duplicados, bytes, motivos de descarte. |
| `profiles` | | Tabela de perfis. |
| `set_profile` | `profile` (ou `name`), `seed?`, `dir?` | Troca perfil. `dir` é `c2s`, `s2c` ou ambos. Reinicializa a semente desse sentido. |
| `set_params` | `params`, `dir?` | Muda valores individuais sem reinicializar a semente. |
| `partition` | `dir`, `on`, `duration_ms?` | Interrupção em um ou dois sentidos. Com `duration_ms`, restaura sozinha. |
| `disconnect` | `duration_ms` | Descarta tudo nos dois sentidos durante um intervalo. |
| `reconnect` | | Encerra uma desconexão antecipadamente. |
| `log_path` | | Caminho do log de pacotes. |
| `shutdown` | | Solicita encerramento do processo retransmissor. |

### <a id="packet-log"></a>Log de pacotes

JSON Lines. Primeira linha como cabeçalho: `{"format":"coopchaos-packetlog","version":1,"profile","seed","start_wall"}`. Depois, uma linha por datagrama: `t` (ms no relógio do retransmissor), `dir`, `peer`, `n` (contador por sentido), `len`, `head` (primeiros 16 bytes em hexadecimal), `verdict` (`fwd` ou `drop`), `reason` (`loss`, `burst`, `partition`, `disconnect`, `bandwidth`), `copies` (atrasos de entrega em ms; duas entradas significam duplicata), `corrupt`. Linhas de eventos têm `event` (`profile`, `params`, `partition`, `disconnect`, `reconnect`). Para alinhar um log aos registros do jogo, compare `head`, `len` e ordem, não números de quadro.

## <a id="use-the-same-network-in-a-simulator-c"></a>Use a mesma rede em um simulador (C++)

`cpp/impair.h` contém apenas cabeçalho, sem sockets ou relógios, com tempo virtual:

```cpp
#include "impair.h"
auto p = coopchaos::profile("bad_wifi");
coopchaos::Impairment c2s(p, "c2s"), s2c(p, "s2c");   // one per direction, same labels as the relay
auto v = c2s.decide(nowMs, sizeBytes);                // v.dropped(), v.reason, v.delaysMs, v.corrupt
for (double d : v.delaysMs) deliverAt(nowMs + d);     // two entries = duplicate
c2s.partition(true); c2s.disconnectUntil(nowMs + 3000); c2s.reconnect();
```

`cpp/profiles_gen.h` é gerado de `profiles.json` por `gen_header.py --write`. Os testes falham se estiver desatualizado. As duas linguagens usam o mesmo fluxo aleatório SplitMix64, com semente derivada do hash FNV-1a de `"<seed>:<label>"`, e a mesma ordem de chamadas e aritmética; assim, perfil, semente e sequência de pacotes produzem resultados idênticos. Mantenha os arquivos alinhados: altere `impair.py`, replique em `impair.h`, e a verificação cruzada mostrará divergências.

## <a id="how-it-is-tested"></a>Como é testado

Um comando na raiz do repositório:

```
python -I tools/chaos/run_tests.py
```

Exibe `ALL OK` quando tudo passa e cada cópia deliberadamente defeituosa é detectada. Leva cerca de três minutos na primeira vez (a parte C++ compila uma vez) e dois nas seguintes. Executa:

1. **Testes Python** (`test_chaos.py`, 20 testes). Estatísticas do modelo em tempo virtual para cada perfil (taxa de perda dentro da tolerância teórica, latência média, agrupamento em rajadas, taxas de reordenação e duplicação, limite de banda, partição em um sentido, desconexão temporizada, determinismo por semente, sentidos independentes). Depois, idas e voltas UDP reais em loopback pelo retransmissor (perfis, mudanças durante a execução, log de pacotes, dois clientes vistos como dois participantes), módulo cliente RPC e linha de comando.
2. **Variantes de mutação Python** (11). A variável de ambiente `COOPCHAOS_MUTANT` quebra um comportamento de propósito (sem perda, sem rajadas, metade da latência, sem reordenação, sem duplicatas, sem limite de banda, sem partição e auxiliar cliente que sempre interrompe os dois sentidos). Um teste nomeado precisa falhar para cada uma. Uma suíte incapaz de distinguir um simulador quebrado de um funcional não tem valor.
3. **Verificação cruzada C++.** `run_tests.py` compila `cpp/` com cmake, um trabalho por vez para economizar memória, executa cerca de 36.000 decisões pela versão C++ e pelo modelo Python (6 perfis, 2 sentidos, com mudanças de corrupção, partição, desconexão, banda, duplicação e reordenação durante a execução) e exige resultados idênticos. Depois, 4 compilações mutantes do cabeçalho C++ (`cpp/CMakeLists.txt`) e um cabeçalho gerado desatualizado precisam ser detectados. Se faltar cmake ou compilador C++, o script exibe `SKIP:` com motivo e a última linha informa que a verificação foi pulada. Nunca afirma ter executado o que não executou.

Opções: `--no-twins` executa apenas testes Python, `--no-cpp` pula C++. Um `CMAKE_TOOLCHAIN_FILE` residual no ambiente para outro alvo (por exemplo, Android NDK) é ignorado nesta compilação. A pasta de compilação é criada na pasta temporária do sistema, não no repositório.

## <a id="files"></a>Arquivos

| Arquivo | Função |
|---|---|
| `impair.py` | Modelo de perturbação. Puro, com semente e tempo virtual. |
| `relay.py` | Retransmissor UDP, servidor JSON-RPC, `ChaosClient`, log de pacotes. |
| `chaos.py` | Linha de comando: `profiles`, `relay`, `call`. |
| `client.py` | Funções simples para scripts de teste. |
| `profiles.json` | Tabela de perfis, fonte oficial dos dados. |
| `gen_header.py` | Gera `cpp/profiles_gen.h` a partir de `profiles.json`. |
| `xcheck.py`, `cpp/` | Verificação cruzada Python/C++ e versão equivalente C++. |
| `test_chaos.py`, `run_tests.py` | Testes e executor de variantes de mutação. |
| `examples/fnv/` | Como o simulador foi usado num projeto cooperativo de Fallout: New Vegas. |

## <a id="limits"></a>Limitações

- O retransmissor é escrito em Python. Testes usam menos de 1.000 pacotes por segundo. Sua vazão não foi medida além disso; para jogo que envie mais, confira os números em `stats`.
- No Windows, pede temporizador de 1 ms durante a execução para pacotes atrasados não serem arredondados ao intervalo padrão de 15,6 ms. O erro acrescentado está coberto pela tolerância do teste (ida e volta média dentro de 14 ms mais 12%, ida e volta LAN abaixo de 15 ms) e não foi medido com mais precisão.
- Somente UDP. Jogo TCP precisa de outra ferramenta.
- Enxerga datagramas inteiros. Se o jogo criptografar ou assinar pacotes, `corrupt` fará o receptor descartá-los, o que já é um teste útil.

## <a id="credits-and-licence"></a>Créditos e licença

MIT, como o restante deste repositório. As ideias vêm de fontes públicas: artigos de rede do Gaffer on Games, modelo de perda Gilbert-Elliott de dois estados e ferramentas como clumsy e netem do Linux que fazem o mesmo no nível do sistema. Nenhum código foi copiado delas.

Adaptado do commit f57aa78 de fnv-coop (https://github.com/cranebeaker/fnv-coop).
