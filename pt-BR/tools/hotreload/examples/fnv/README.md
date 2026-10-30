# <a id="how-the-fallout-new-vegas-co-op-mod-wired-it-in"></a>Como o mod cooperativo de Fallout: New Vegas fez a integração

O restante desta ferramenta independe do jogo. Esta nota é o único lugar que cita um jogo: como o mod [fnv-coop](https://github.com/cranebeaker/fnv-coop) (commit e85460f) usou o mesmo padrão, mostrando um mapeamento real entre o ponto de entrada do plugin do jogo e o carregador e o núcleo.

O jogo é de 32 bits e o mod é um plugin xNVSE; portanto, a compilação separada é feita para 32 bits (esta ferramenta também compila e passa nos testes em 32 bits: `python -I tools/hotreload/run_tests.py --arch Win32`).

## <a id="the-mapping"></a>O mapeamento

| Nesta ferramenta | No fnv-coop |
|---|---|
| DLL do carregador (`hotreload_loader.dll`) | `nvcoop.dll`, o plugin xNVSE. Seu ponto de entrada `NVSEPlugin_Load` cria o `CoreHost` |
| DLL do núcleo | `nvcoop_mod.dll`, todo o restante do mod |
| `HotReload_OnFrame()` | chamada a partir da mensagem xNVSE `kMessage_MainGameLoop`, uma vez por quadro |
| `HotReload_OnMessage()` | todas as outras mensagens xNVSE são encaminhadas ao núcleo |
| `HrLoaderApi::user_context` | o `NVSEInterface*` fornecido pelo xNVSE ao plugin |
| `HrLoaderApi::game_dir` | a pasta do jogo, com barra invertida no final |
| pipe de controle | `\\.\pipe\nvcoop-<instance>`, o pipe da ponte já existente no mod, que também atende chamadas de console e estado. A ferramenta de troca é seu cliente |
| `hotreload.py swap --pipe` | `tools/runner/run.py swap --instances 0,1` (resolve os números das instâncias em pipes e pastas de instância) |
| `HotCore_Init` | `NvCore_Init` |
| `COOP_RELOAD_STATE` | `NVCOOP_RELOAD_STATE`, chave do blob `nvreload.state` |
| método `reload.state` | o mesmo nome, registrado pelo núcleo |

## <a id="what-is-specific-to-that-game"></a>O que é específico desse jogo

- **O xNVSE carrega toda `*.dll` da pasta de plugins.** Por isso, a ferramenta de troca copia o novo núcleo para um nome temporário que não termina em `.dll` (aqui, `.swap`) e o renomeia sobre o núcleo. Um arquivo temporário chamado `*.dll` seria identificado como plugin. As cópias em cache ficam em uma subpasta (`nvcoop_cache`), não junto aos plugins.
- **Os arquivos de configuração ficam junto ao módulo.** Os módulos do mod leem `nvcoop.ini` e seus arquivos de dados na pasta do próprio módulo, que é a cópia em cache. Por isso, o carregador original espelhava o INI e os dados na pasta de cache antes de cada carregamento. Esta versão genérica não faz isso: fornece `api->core_dir` ao núcleo, que lê os arquivos dali.
- **Um monitor de arquivos** no carregador original podia disparar um recarregamento quando o arquivo do núcleo mudava (`[loader] watch=1`). Ele foi omitido aqui: a troca é sempre solicitada pelo cliente.
- **Hooks.** O núcleo original aplica patches ao código do jogo; por isso, seu `BeforeUnload` removia todos os hooks, aguardava a saída das threads usando os trampolins como intervalos de código adicionais e reinstalava os hooks se a espera recusasse a operação. Uma proteção de escrita também congelava as outras threads durante a gravação de um patch. Aqui, as mesmas etapas são os callbacks de `DrainHooks` (`suspend`, `resume`, `extraRanges`); o congelamento não faz parte desta ferramenta.
- **Uma sessão cooperativa durante um recarregamento.** A ferramenta de troca original também espera que uma sessão cooperativa em execução volte a funcionar após o recarregamento (o transporte é fechado e reaberto). Essa verificação exige um método do mod e não está em `hotreload.py`; adicione uma chamada ao seu método de estado após o recarregamento se o mod tiver uma conexão de longa duração.
- **A thread de trabalho da biblioteca.** Nesse mod, a biblioteca de sessão cooperativa inicia uma thread de trabalho que fica parada dentro do código do mod. É por isso que `adoptThread` existe: até o registro dessa thread, a espera de saída recusava todo recarregamento com uma sessão em execução.

## <a id="where-to-read-the-original"></a>Onde ler o original

No commit e85460f de fnv-coop:

- `plugin/loader/` (carregador: `loader_host.cpp`, `loader_abi.h`)
- `plugin/reload/` (registro de estado e espera de saída: `reload_state.cpp`, `reload_drain.cpp`, `reload_glue.cpp`)
- `tools/runner/hotswap.py` (cliente)
- `docs/FAST-QA.md` (todo o ciclo de correção ao redor da ferramenta)
