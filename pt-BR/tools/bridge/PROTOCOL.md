# <a id="bridge-protocol-version-1"></a>Protocolo da ponte, versão 1

Formato de transmissão entre um cliente de testes e o servidor RPC dentro do processo do jogo. O servidor C++ (`include/coopbridge/server.h`), o cliente Python (`bridge_client.py`) e o jogo simulado (`fake_game.py`) usam esse protocolo. Esta página basta para implementar servidor ou cliente em outra linguagem.

## <a id="transports"></a>Transportes

Um fluxo de solicitações por conexão. Ambos os transportes carregam os mesmos bytes.

| Endpoint | Significado |
|---|---|
| `tcp://127.0.0.1:PORT` | TCP em endereço de loopback. Funciona em todos os sistemas operacionais. |
| `pipe://NAME` | Pipe nomeado do Windows `\\.\pipe\NAME`, modo de bytes. Clientes remotos são recusados. |

Um servidor pode oferecer ambos. Pode gravar seus endpoints em um pequeno arquivo JSON ao iniciar (`Options::endpointFile`):

```json
{"protocol": 1, "game": "mygame", "pid": 1234, "endpoints": ["tcp://127.0.0.1:41873", "pipe://mygame-0"]}
```

A estrutura de testes que inicia o jogo lê esse arquivo, permitindo ao servidor escolher uma porta livre.

## <a id="framing"></a>Delimitação

- Texto UTF-8. Um objeto JSON por linha, terminada em `\n` (um `\r` antes dela é ignorado). Linhas vazias são ignoradas.
- Solicitações e respostas são objetos JSON. Uma linha maior que 4 MiB fecha a conexão após uma resposta de erro.
- O servidor só escreve UTF-8 válido. Bytes inválidos no texto do jogo são substituídos por U+FFFD. O cliente decodifica com substituição, para que um byte estranho nunca oculte uma resposta.

## <a id="request-and-reply"></a>Solicitação e resposta

```
-> {"id": 7, "method": "exec", "params": {"cmd": "set quest 10"}}
<- {"id": 7, "result": {"ok": true, "output": "ok"}}
<- {"id": 7, "error": {"code": -32602, "message": "exec requires string param 'cmd'"}}
```

- `id`: número ou string escolhidos pelo cliente e repetidos na resposta. `null` é permitido. Um cliente que envia inteiros crescentes consegue reconhecer uma resposta atrasada (consulte Tempos limite).
- `method`: string. `params`: objeto ou ausente.
- A resposta tem `result` ou `error`, nunca ambos. `error` é `{"code": int, "message": string}` e pode acrescentar `data`.
- As respostas na mesma conexão retornam na ordem das solicitações. O servidor executa uma solicitação por conexão de cada vez. Várias conexões podem ficar abertas; suas solicitações entram juntas na fila da thread principal.
- Uma linha que não é JSON recebe `{"id": null, "error": {"code": -32700, ...}}`.

## <a id="timeouts"></a>Tempos limite

- Qualquer solicitação pode conter `params.timeoutMs`. O padrão do servidor para as demais é 30000 ms.
- Uma solicitação que precisa da thread principal aguarda na fila. Se nenhum quadro a executar dentro de `timeoutMs` mais uma pequena tolerância (2 s por padrão), o servidor responde com erro `-32001` e a descarta: ela não será executada depois.
- `load` e `save` respondem com erro `-32002` quando o jogo não termina a operação no prazo. `waitFor` não usa erro: responde `satisfied: false, timedOut: true`.
- O cliente tem seu próprio tempo limite por chamada. Quando desiste, a conexão continua utilizável; a próxima chamada ignora a resposta atrasada da chamada abandonada porque seu `id` é menor que o esperado.

## <a id="which-thread-runs-a-request"></a>Qual thread executa uma solicitação

| Atendidos na thread de transporte (funcionam enquanto o jogo carrega ou trava) | Executados na thread principal do jogo, um hook de quadro por vez |
|---|---|
| `ping`, `version`, `methods`, `events`, métodos personalizados registrados como "direct" | `exec`, `eval`, `waitFor`, `state`, `save`, `load`, `screenshot`, métodos personalizados |

O servidor inicia no máximo `maxCallsPerPump` (padrão 16) solicitações enfileiradas por hook de quadro, para que uma rajada de chamadas não congele um quadro. Quando mais de `maxPending` (padrão 256) aguardam, novas solicitações são recusadas com `-32003`.

## <a id="standard-methods"></a>Métodos padrão

O jogo declara quais suporta. Solicitar um método não suportado ou desconhecido recebe `-32601`. `methods` lista a quais o jogo responde.

### <a id="ping-always"></a>`ping` (sempre)

Resultado: `{"pong": true, "protocol": 1, "game": "name", "pid": 1234, "frames": 5210, "mainLoopAgeMs": 12, "ready": true, "loadedCount": 1}`

`mainLoopAgeMs` é o tempo desde a última execução do hook de quadro, ou `-1` se ainda não houve execução (o jogo continua iniciando). O cliente guarda `pid` para distinguir uma falha do processo (pid desapareceu) de uma conexão fechada.

### <a id="version-always"></a>`version` (sempre)

Resultado: `{"protocol": 1, "game": "name", "build": "abc123", "server": "coopbridge-cpp 1", "pid": 1234}`. Registre nos metadados de cada execução de teste.

### <a id="methods-always"></a>`methods` (sempre)

Resultado: `{"methods": ["ping", "version", "methods", "events", "exec", ...]}`

### <a id="exec"></a>`exec`

Parâmetros: `{"cmd": "console line", "ref": "optional reference", "timeoutMs": n}`. Resultado: `{"ok": bool, "output": "text"}`.
`ok` informa se o jogo aceitou a linha; `output` contém o que foi exibido, ou `""` quando o jogo não captura a saída. `ref` nomeia a referência na qual a linha é executada, no formato documentado pelo adaptador.

### <a id="eval"></a>`eval`

Parâmetros: `{"expr": "expression", "ref": "optional", "timeoutMs": n}`. Resultado: `{"value": number | bool | string}`.

### <a id="waitfor"></a>`waitFor`

Parâmetros: `{"expr" | "cmd": "...", "op": "truthy", "value": 0, "contains": "text", "timeoutMs": 10000, "pollMs": 100, "ref": "optional"}`.

O servidor avalia `expr` (pela avaliação do adaptador) ou executa `cmd` (por exec) na thread principal a cada `pollMs`, até a condição ser satisfeita.

- Com `expr`: número ou booleano é comparado com `op` (`truthy`, `==`, `!=`, `<`, `<=`, `>`, `>=`) e `value`. Uma string só satisfaz um teste `contains`.
- Com `cmd`: o primeiro número da saída é comparado; com `contains`, a saída precisa conter o texto.

Resultado: `{"satisfied": bool, "timedOut": bool, "value": last value, "elapsedMs": n}` e, quando há expiração com consultas que falharam, `"lastError"`. Uma consulta que falha (o jogo está carregando) não encerra a espera.

### <a id="state"></a>`state`

Parâmetros: `{"sections": ["name", ...], "path": "file"}`. Resultado: snapshot JSON do adaptador, limitado às seções solicitadas (todas quando ausentes). Com `path`, o servidor grava o snapshot no arquivo e responde `{"path": "...", "bytes": n}`. O processo do jogo escreve o arquivo, e seu diretório de trabalho é a pasta do próprio jogo; portanto, use um caminho absoluto.

### <a id="save"></a>`save`

Parâmetros: `{"name": "x", "overwrite": false, "timeoutMs": 30000}`. Inicia um salvamento e espera o jogo informar sua conclusão. Resultado: `{"saved": true, "path": "..."}`. O adaptador decide quais nomes são permitidos e pode recusar substituir um salvamento; a recusa é erro do adaptador (o exemplo usa `-32012`).

### <a id="load"></a>`load`

Parâmetros: `{"name": "x", "timeoutMs": 180000}`. Inicia um carregamento e espera o jogo informar que está no mundo. Resultado: `{"loaded": true, "name": "x"}`.

### <a id="screenshot"></a>`screenshot`

Parâmetros: `{"path": "optional file"}`. Resultado: `{"ok": true, "path": "file written"}`.

### <a id="events"></a>`events`

Parâmetros: `{"since": 0, "limit": 0}`. Resultado: `{"events": [{"seq": 5, "tMs": 1200, "type": "game.loaded", "data": {...}}], "next": 5, "dropped": 0, "last": 9}`.

O servidor mantém os últimos 1024 eventos em um buffer circular. Retorna eventos com `seq > since`, dos mais antigos aos mais recentes, até `limit` (0 significa até 1000). `next` é o `seq` do último evento retornado ou `since` se não houver eventos: use-o como `since` na próxima chamada. `dropped` conta eventos posteriores a `since` que o buffer já não contém. `last` é o `seq` mais recente. O servidor acrescenta `game.loaded` e `game.saved`; o jogo acrescenta eventos próprios com `PushEvent(type, data)`.

## <a id="custom-methods"></a>Métodos personalizados

O jogo registra métodos próprios com nomes separados por ponto (`sync.status`, `bot.menu`). Nomes padrão não podem ser substituídos. Um método personalizado recebe o objeto de parâmetros e retorna qualquer valor JSON ou lança uma exceção. Executa na thread principal, exceto quando registrado como direto. Inspetores e painéis só devem chamar métodos personalizados de leitura.

## <a id="error-codes"></a>Códigos de erro

| Código | Nome | Quando |
|---|---|---|
| -32700 | parse error | a linha não é JSON |
| -32600 | invalid request | não é objeto, falta `method`, `id` tem tipo inválido ou linha longa demais |
| -32601 | method not found | método desconhecido ou método padrão não suportado pelo jogo |
| -32602 | invalid params | parâmetro ausente ou com tipo incorreto |
| -32000 | host error | o adaptador ou manipulador lançou exceção; `message` contém o texto |
| -32001 | main thread timeout | nenhum quadro executou a solicitação no prazo |
| -32002 | operation timeout | `load` ou `save` não terminou no prazo |
| -32003 | busy | muitas solicitações aguardam a thread principal |
| -32004 | stopping | servidor em encerramento |
| -32010 a -32099 | game specific | escolhidos pelos adaptadores (salvamento existente, reserva em uso, ...) |

Os clientes convertem respostas com `error` em exceções que preservam `code` e `message`. Método ausente (`-32601`) é a forma normal de uma ferramenta descobrir que o jogo não tem um recurso; por isso, ela o trata como indisponível e continua.

## <a id="versioning"></a>Versionamento

`ping` e `version` carregam `protocol`, um inteiro. A versão 1 é esta página. Regras:

- Adicionar método, campo de resultado ou tipo de evento não altera o número. Clientes ignoram campos desconhecidos.
- Alterar o significado de um campo, removê-lo ou mudar a delimitação aumenta o número. O cliente verifica `protocol` ao conectar e encerra com mensagem clara se a versão for superior à conhecida.

## <a id="security"></a>Segurança

O servidor pode executar linhas de console no jogo. Escuta apenas em loopback, salvo opção explícita do mod por `allowRemote`, e não possui senha. Trate a porta como um depurador: use-a em máquinas e cópias de teste, nunca em uma máquina cuja porta possa ser alcançada por desconhecidos; nunca distribua uma versão com o servidor ativado.
