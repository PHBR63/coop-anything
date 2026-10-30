# <a id="bridge-remote-control-a-running-game-from-tests"></a>bridge: controle remoto de um jogo em execução a partir dos testes

Um pequeno servidor RPC fica dentro do processo do jogo. Scripts de teste se conectam para executar comandos de console, ler valores, esperar condições, capturar estado, carregar e salvar, tirar capturas de tela e ler um registro de eventos, sem pessoa ao teclado. É isso que permite a um bot ou executor controlar duas ou mais cópias reais. Nada é específico de um jogo: tudo que interage com ele fica atrás de uma classe adaptadora escrita por você.

| Componente | O que é |
|---|---|
| [`include/coopbridge/server.h`](include/coopbridge/server.h) | Modelo de servidor C++17 apenas com cabeçalho, incorporado pelo mod. Thread de transporte, fila de solicitações drenada na thread principal do jogo (uma chamada `Pump()` por hook de quadro), registro de métodos e métodos padrão por trás de um adaptador. TCP em loopback em todas as plataformas, mais pipe nomeado no Windows. |
| [`include/coopbridge/json.h`](include/coopbridge/json.h) | Pequeno valor JSON, analisador e gravador usados pelo servidor. Seu adaptador também pode utilizá-los. |
| [`bridge_client.py`](bridge_client.py) | Cliente Python, somente biblioteca padrão. TCP ou pipe nomeado do Windows, limite de tempo em toda chamada, erros distintos (`RpcError`, `CallTimeout`, `WaitTimeout`, `ConnectionLost`, `GameCrashed`, `ProtocolError`) e linha de comando. |
| [`PROTOCOL.md`](PROTOCOL.md) | Formato de transmissão, métodos, códigos de erro e regras de versionamento. |
| [`fake_game.py`](fake_game.py) | Jogo simulado com o mesmo comportamento de servidor para testes e demonstrações. Pode injetar falhas (respostas tardias, ID errado, dados inválidos, conexão interrompida). |
| [`cpp/test_server.cpp`](cpp/test_server.cpp) | Pequeno jogo simulado que incorpora o servidor C++. Os testes o controlam pelo cliente Python. Também é o exemplo mais curto de incorporação. |

O padrão e as armadilhas estão em [playbook/in-game-bridge.md](../../playbook/in-game-bridge.md). A tabela ao vivo que lê uma ponte é [tools/inspect](../inspect/README.md).

Python 3.8 ou posterior para o cliente. O servidor precisa de compilador C++17 (compilado com Visual Studio 2022 e CMake).

## <a id="quick-start-try-the-client-without-a-game"></a>Primeiros passos: experimente o cliente sem um jogo

```
python -I tools/bridge/fake_game.py --name demo --set health=80      # prints {"endpoint": "tcp://127.0.0.1:PORT", ...}
python -I tools/bridge/bridge_client.py --endpoint tcp://127.0.0.1:PORT ping
python -I tools/bridge/bridge_client.py --endpoint tcp://127.0.0.1:PORT exec "inc health 5"
python -I tools/bridge/bridge_client.py --endpoint tcp://127.0.0.1:PORT waitfor health --op ">=" --value 85 --timeout-ms 2000
```

Em Python:

```python
sys.path.insert(0, "tools/bridge"); from bridge_client import Bridge, WaitTimeout, RpcError
with Bridge.connect("tcp://127.0.0.1:27990", wait_s=60) as g:    # waits for the game to open the port
    print(g.version())                       # record this in every test run's metadata
    g.require("exec", "waitFor")             # a clear error if the game lacks a method
    g.load("base_save")
    g.exec("set quest 10")
    g.wait_for(expr="quest", op=">=", value=10, timeout_ms=5000)     # raises WaitTimeout, never hangs
    page = g.events(); g.wait_event("game.saved", since=page["next"], timeout_s=30)
```

O endpoint é `tcp://127.0.0.1:PORT` ou `pipe://NAME` (Windows). `COOPBRIDGE_ENDPOINT` fornece um padrão, e `endpoint_from_file(path)` lê o arquivo escrito pelo jogo ao iniciar, permitindo que ele escolha uma porta livre.

## <a id="quick-start-put-the-server-in-your-mod"></a>Primeiros passos: coloque o servidor no seu mod

Copie `include/coopbridge/` para o mod (ou acrescente a pasta ao caminho de inclusão). Escreva o adaptador, inicie o servidor uma vez e chame `Pump()` uma vez por quadro.

```cpp
#include <coopbridge/server.h>

class MyAdapter : public coopbridge::Adapter {
public:
    coopbridge::Capabilities capabilities() const override {       // only what your game can do
        coopbridge::Capabilities c; c.exec = c.eval = c.state = true; return c;
    }
    coopbridge::ExecResult Exec(const std::string& line, const std::string& ref) override {
        return { /*ok*/ RunConsoleLine(line, ref, &out), out };   // your game's call; throw coopbridge::Error on failure
    }
    coopbridge::json::Value Eval(const std::string& expr, const std::string& ref) override { return EvalExpression(expr, ref); }
    coopbridge::json::Value State(const std::vector<std::string>& sections) override { return BuildSnapshot(sections); }
};

MyAdapter adapter;
coopbridge::Server server;

void OnPluginStart() {
    coopbridge::Options opt;
    opt.game = "mygame";  opt.build = GIT_HASH;
    opt.tcpPort = 27990;                       // or 0 for a free port, plus opt.endpointFile = "bridge-endpoint.json"
    opt.pipeName = "mygame-0";                 // Windows only, optional
    if (!server.Start(opt, adapter)) Log("bridge: %s", server.lastError().c_str());
    server.Register("sync.status", [](const coopbridge::json::Value&) { return BuildSyncStatus(); });   // your own methods
}
void OnFrameHook() { server.Pump(); }          // the game's main thread, once per frame
void OnShutdown()  { server.Stop(); }
```

O que você precisa saber:

- **Todo método do adaptador roda dentro de `Pump()`, na thread principal.** Você pode chamar o jogo livremente ali. A thread de transporte nunca interage com o jogo.
- **Falhas são exceções.** Lance `coopbridge::Error(code, message)` para um código próprio (use -32010 a -32099) ou qualquer `std::exception` (relatada como -32000). O cliente recebe `RpcError` com esse código e texto.
- **`load` e `save` iniciam o trabalho e retornam.** Chame `server.NotifyLoaded()` / `server.NotifySaved(path)` nos hooks de carregamento e salvamento. A solicitação aguarda essa notificação e responde `-32002` se ela nunca chegar.
- **Métodos personalizados:** `server.Register("name", fn)` executa `fn` na thread principal. Passe `false` como terceiro argumento para um método que só leia dados seguros entre threads e precise responder durante o carregamento. `PushEvent(type, data)` (qualquer thread) alimenta o log `events`.
- **Limites:** no máximo `maxCallsPerPump` solicitações iniciadas por quadro (16), no máximo `maxPending` aguardando (256); `slackMs` após o limite da própria solicitação, o chamador recebe `-32001`. Todos ficam em `coopbridge::Options`.
- **Escuta apenas em loopback.** `tcpHost` precisa ser endereço loopback, salvo se você definir `allowRemote`. Não há senha: consulte a nota de segurança em PROTOCOL.md. Incorpore o servidor em compilações de teste, não nas versões distribuídas.
- **Exceções precisam estar ativadas** na compilação do código que inclui o cabeçalho.
- `Stop()` é para a thread principal (no encerramento); faz falhar solicitações ainda em espera e aguarda o término de todas as threads.

## <a id="methods"></a>Métodos

`ping`, `version`, `methods` e `events` sempre existem. `exec`, `eval`, `waitFor`, `state`, `save`, `load` e `screenshot` existem quando o adaptador os declara em `capabilities()`. Um método ausente no jogo responde `-32601`, tratado pelas ferramentas como "indisponível". Parâmetros, resultados e códigos de erro estão em [PROTOCOL.md](PROTOCOL.md).

## <a id="how-it-is-tested"></a>Como é testado

```
python -I tools/bridge/run_tests.py       # prints ALL OK only if every check passes and every twin is caught
python -I tools/bridge/run_tests.py --no-cpp     # the Python part only; the last line then says the C++ stage was skipped
```

28 testes de cliente, 22 de servidor C++, 13 variantes do cliente e 12 variantes C++ no momento da escrita. Uma execução leva cerca de três minutos, principalmente nas compilações e inicializações de processos. Nenhum jogo real é iniciado. A compilação vai para `tools/bridge/build/` (ignorada pelo Git) ou `COOPBRIDGE_BUILD_DIR`, um trabalho de compilação de cada vez; o script remove `CMAKE_TOOLCHAIN_FILE` do ambiente porque uma configuração residual de outro alvo escolheria o compilador errado. Se faltar cmake ou compilador C++, a etapa C++ exibe SKIP e a última linha não é simplesmente `ALL OK`.

- **Cliente contra jogo simulado (`test_bridge.py`):** métodos padrão e resultados, capturas de estado em arquivo com caminho relativo, `wait_for` e `wait_event` com cursores, erro do jogo preservando código e mensagem, método não compatível, chamada que esgota o tempo com resposta tardia ainda a caminho e descartada na chamada seguinte, resposta com ID errado, dados inválidos, resposta dividida em duas partes, resposta de 2 MB, conexão interrompida (conexão fechada com jogo vivo e falha quando o PID desaparece), duas threads na mesma conexão, conexão enquanto o jogo ainda inicia, servidor que nunca responde ao ping, protocolo mais novo, análise do endpoint, arquivo de endpoint, padrão do ambiente e linha de comando com códigos de saída.
- **Servidor C++ contra cliente Python (`test_cpp_server.py`):** o programa de `cpp/test_server.cpp` é iniciado e controlado por TCP e pipe nomeado. Verificações: cada método padrão de ponta a ponta; adaptador sempre na thread que chama `Pump()`; exceções preservam código e mensagem; métodos desconhecidos e não compatíveis; linhas e IDs inválidos; solicitações enviadas juntas numa escrita ou em duas metades; UTF-8 inválido do jogo substituído; thread principal travada produz `-32001` enquanto `ping` ainda responde e solicitação abandonada nunca executa; rajada de 40 chamadores atendida sem ultrapassar o orçamento por quadro; fila cheia responde `-32003`; 200 atualizações de 8 clientes não se perdem; cursor de eventos e contagem de transbordamento; linha longa demais; `load` ou `save` que nunca termina; host fora de loopback e porta ocupada recusados; `Stop()` fecha clientes TCP e pipe abertos, termina o processo e remove o arquivo de endpoint.
- **Variantes de mutação:** cada uma quebra uma proteção numa cópia de `bridge_client.py` ou `server.h`, e o teste correspondente precisa falhar. Variantes do cliente: limites de tempo ignorados, erros suprimidos, IDs de resposta não conferidos, resposta tardia não descartada, resposta dividida sem buffer, ausência de repetição de conexão, falha do jogo não diferenciada de conexão fechada, toda interrupção relatada como falha do jogo, `wait_for` que nunca lança erro, cursor de eventos ignorado, caminho relativo enviado sem ajuste, ausência de trava entre threads, ausência de verificação do protocolo. Variantes do servidor: chamadas fora da thread principal, sem orçamento por quadro, sem limite de fila, limite de espera da thread principal que nunca dispara, erros suprimidos, respostas com ID errado, cursor de eventos parado, escuta em todos os endereços, uma solicitação tratada por leitura, espera sem prazo, método desconhecido que tem sucesso, salvamento sem limite de tempo.

Fora da suíte: a ramificação de sockets não Windows do cabeçalho (a suíte compila com Visual Studio 2022) e qualquer jogo real.

## <a id="files"></a>Arquivos

`bridge_client.py`, `fake_game.py`, `PROTOCOL.md`, `include/coopbridge/` (`server.h`, `json.h`), `cpp/` (`CMakeLists.txt`, `test_server.cpp`), `test_bridge.py`, `test_cpp_server.py`, `run_tests.py`, `examples/fnv/README.md`.

## <a id="generalised-from-fnv-coop-commit-e85460f-githubcomcranebeakerfnv-coop"></a>Generalizado do commit e85460f de fnv-coop (github.com/cranebeaker/fnv-coop)

Generalizado de `tools/runner/nvbridge.py` (cliente Python) e `plugin/bridge/` (servidor interno) do [fnv-coop](https://github.com/cranebeaker/fnv-coop), commit e85460f. O que mudou:

- Console, analisador de expressões, busca de formulários, hooks de salvamento e código de captura de tela do jogo foram colocados atrás da classe `Adapter`. Métodos padrão são declarados por `capabilities()`.
- O cliente Python ganhou transporte TCP ao lado do pipe Windows, `CallTimeout` separado de conexão perdida, descarte de respostas tardias, verificação de versão do protocolo, arquivo de endpoint e padrão do ambiente. Não depende mais de módulo auxiliar específico de jogo.
- Nomes de métodos ficaram neutros: `bridge.version` virou `version`, `loadSave` virou `load`, `saveGame` virou `save`. Métodos de reserva, `plugins` e `quit` do original não fazem parte do conjunto padrão.
- O servidor ganhou orçamento de solicitações por quadro, limite de fila, verificação de loopback e arquivo de endpoint; testes controlam o servidor real com cliente real em vez de verificar cada metade isoladamente.
- Os testes originais usavam opções de compilação dentro do código para mutantes. Aqui, o executor cria cópias defeituosas de fora; os cabeçalhos distribuídos não carregam opções de teste.

Os nomes de métodos e comandos de console de Fallout: New Vegas estão em [examples/fnv/README.md](examples/fnv/README.md).
