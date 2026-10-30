# <a id="gamepool-run-several-copies-of-a-game-for-tests"></a>gamepool: execute várias cópias de um jogo para testes

Ferramentas para executar 2 ou mais cópias de qualquer jogo Windows em um PC, mantê-las abertas entre testes e ler os vestígios de falha. Foram feitas para testar mod cooperativo com clientes reais; nada no código é específico de um jogo. Particularidades ficam em um arquivo JSON.

| Parte | O que faz |
|---|---|
| **Instalações isoladas** (`provision`) | Constrói `<instances>/0`, `1`, ... espelhando a pasta por hardlinks (quase sem gastar disco), com cópias privadas dos arquivos escritos pelo jogo (configurações, salvamentos, pastas de plugins). Só lê a instalação original. |
| **Auxiliares de inicialização** (`up`, `down`, `status`, `job`) | Reservam vagas, iniciam cópias uma após outra, minimizadas e sem foco, por processo desacoplado que sobrevive ao comando. Relatam encerramento antecipado (sinal típico de instância única). Encerram somente processos próprios. |
| **Conjunto já inicializado** (`pool up`, `pool lease`, ...) | Serviço mantém N cópias e as concede temporariamente aos testes. Reinicia cópia morta, sem resposta, com crescimento excessivo de RAM, marcada suja ou com concessão expirada. Iniciar jogo grande demora minutos; obter concessão, milissegundos. |
| **Pares host/cliente** (`up --pairs N`, `provision --pairs N`, `status --pairs`) | Iniciam N pares, cada qual com porta e configurações privadas, recusam falta de RAM ou porta e mostram uma linha por par. |
| **Hook de troca** (`swap`) | Pede ao adaptador substituir código nas cópias abertas (integração de recarregamento a quente), verifica todas antes, para na primeira falha e confere cada uma depois. |
| **Perfil de baixo custo** (`lowcost`) | Edita somente configurações privadas: janela pequena, limite de quadros, sem sombras ou vídeos iniciais. Linhas são dados da configuração. |
| **Verificação básica e sondagem** (`smoke`, `probe`) | Iniciam e verificam cópias por um período (vivas, prontas, RAM, CPU, janelas minimizadas), ou registram estados das janelas de uma cópia nova. |
| **Evidências de falha** (`crashlog`) | Copia logs, seleciona marcadores de falha e acrescenta registro de falha de aplicativo do Windows. |
| **Medição** (`measure`) | Coleta RAM e CPU das cópias do conjunto para comparar perfis numericamente. |

A trava de vagas é separada: [`tools/gameslot`](../gameslot/README.md). Toda inicialização reserva uma vaga primeiro. Para as técnicas (hardlinks, instância única, iniciar minimizado), leia [playbook/multi-instance-testing.md](../../playbook/multi-instance-testing.md).

Somente biblioteca padrão Python (3.8 ou superior; testado em 3.11). Somente Windows.

## <a id="quick-start"></a>Primeiros passos

1. Copie [examples/fnv.json](examples/fnv.json) para `local/mygame.json` (`local/` é ignorado pelo Git) e edite: `game_dir` para instalação, `process_name` para nome da imagem do processo, `launch.exe` para o iniciador e seção `link` para arquivos escritos pelo jogo. Recusa executar enquanto `game_dir` contiver `<placeholder>`.
2. Construa as cópias (quantas vagas existirem, padrão 2):

   ```
   python -I tools/gamepool/gamepool.py --config local/mygame.json provision --n 2
   ```

3. Inicie, examine, encerre:

   ```
   python -I tools/gamepool/gamepool.py --config local/mygame.json up --n 2
   python -I tools/gamepool/gamepool.py --config local/mygame.json status
   python -I tools/gamepool/gamepool.py --config local/mygame.json down
   ```

   `up` recusa iniciar junto de processo de jogo que não iniciou (o usuário pode estar jogando). Passe `--allow-foreign` somente ao confirmar que as cópias não colidem.

4. Execute teste: `job --id t1 --n 2 -- python my_test.py` reserva 2 vagas, executa com `GAMEPOOL_INSTANCES=0,1` e `GAMEPOOL_JOB=t1` no ambiente, copia logs de `collect_logs` para `<state>/runs/t1/` e sempre libera as vagas.

5. Ou mantenha cópias prontas para vários testes:

   ```
   python -I tools/gamepool/gamepool.py --config local/mygame.json pool up --size 2
   python -I tools/gamepool/gamepool.py pool lease --owner t1 --n 2        # prints the lease as JSON
   python -I tools/gamepool/gamepool.py pool release --id L1 [--dirty]
   python -I tools/gamepool/gamepool.py pool status
   python -I tools/gamepool/gamepool.py pool down
   ```

   Em Python:

   ```python
   sys.path.insert(0, "tools/gamepool"); from gplib.client import lease
   with lease("my-test", n=2, ttl_s=900, timeout_s=600) as L:
       L.instances                     # [0, 1], host first
       L.check(0)                      # raises PoolError if instance 0 was restarted under you
       L.dirty(0, "loaded a foreign save")   # recycled when the lease ends
       L.renew()                       # extend during a long test
   ```

   Sair do bloco libera a concessão; uma exceção marca todas as instâncias como sujas. A comunicação do teste com o jogo (ponte, socket, arquivos) é definida pelo teste.

6. Ou execute pares host/cliente e troque código neles; veja [Pares](#pairs) e [Troca](#swap).

O serviço escuta somente em 127.0.0.1; porta e token aleatório ficam em `<state>/pool/pool.json`. `pool up --fake` usa instâncias simuladas em memória (nada é iniciado), permitindo experimentar concessões. Estado fica em `GAMEPOOL_DIR` ou `<repo>/local/gamepool`.

## <a id="pairs"></a>Pares

Teste cooperativo precisa de pares: host e cliente que entra nele. Vários pares só funcionam com portas e configurações próprias e memória suficiente. `--pairs N` cuida disso.

```
python -I tools/gamepool/gamepool.py --config local/mygame.json provision --pairs 3
python -I tools/gamepool/gamepool.py --config local/mygame.json up --pairs 3 --dry-run     # the plan, nothing is started
python -I tools/gamepool/gamepool.py --config local/mygame.json up --pairs 3
python -I tools/gamepool/gamepool.py --config local/mygame.json status --pairs
python -I tools/gamepool/gamepool.py --config local/mygame.json down
```

- **Organização.** `up --pairs N` reserva 2N vagas e agrupa números de instância de dois em dois; o primeiro é host. Par k usa porta `pairs.port_base + <the host's instance number>`. Instâncias são exclusivas por vaga; agentes simultâneos nunca recebem a mesma porta, mesmo se um tiver vaga 0 e o outro começar na 1. `provision --pairs N` constrói 2k (host) e 2k+1 (cliente) assim; `--first-pair K` acrescenta pares K em diante, e `show`/`destroy` aceitam as mesmas opções.
- **Configurações por par.** `pairs.edits` (abaixo) é escrito nas configurações privadas antes de iniciar, preenchendo `{port}`, `{role}`, `{pair}`, `{host}` e `{client}`. Também funcionam em `launch.args` e `launch.env`; cada cópia recebe `GAMEPOOL_PORT`, `GAMEPOOL_ROLE` e `GAMEPOOL_PAIR`. `up` reescreve com os números reais, independentemente das vagas concedidas. Usa a mesma proteção de toda escrita: recusa arquivo que seja hardlink da instalação.
- **RAM.** Antes de reservar vagas, `up --pairs` compara RAM livre ao necessário: `pairs.copy_gb` por cópia nova e `pairs.reserve_gb` para Windows e ferramentas. Cópias deste responsável já abertas contam como já cobertas. Recusa com saída 4 e informa quantos pares cabem. `--no-ram-check` ignora; `--free-ram-gb X` planeja com outro valor. Meça uma cópia com `measure` e preencha `pairs.copy_gb`; padrão cauteloso é 2,0.
- **Portas.** Também confere se cada porta está livre (vinculação a 127.0.0.1 nos protocolos `pairs.proto`), ignorando pares cujo host já é deste responsável. Porta ocupada gera saída 4 com nome do par e libera vagas. `--no-port-check` ignora.
- **`--dry-run`** exibe plano JSON (instâncias presumidas como primeiras vagas, pares, portas, memória), sem iniciar nada. Saída 4 se início real seria recusado.
- **Estado.** `status --pairs` mostra linha por par: `{pair, owner, port, host: {instance, pid, alive, ready}, client: {...}, state}`; `state` é `up`, `partial` (uma cópia saiu) ou `down`. `ready` consulta o adaptador. `status` comum ganha `pair`, `role`, `port` para cópias iniciadas com `--pairs`. `down` esquece pares e processos.

`--n` e `--pairs` devem coincidir (`--pairs 2` equivale a `--n 4`).

## <a id="swap"></a>Troca

Jogos com ferramenta de recarregamento a quente (código novo sem reiniciar) a integram pelo adaptador. `gamepool.py` não conhece ferramentas específicas: consulta o adaptador e confere o resultado.

```python
# my_adapter.py
from gplib.adapter import Adapter

class MyAdapter(Adapter):
    def can_swap(self, i, pid, payload):        # None when copy i can be swapped, else the reason it cannot
        return None if my_tool_has_pipe(i) else "no reload pipe"
    def swap(self, i, pid, payload):            # do the swap; payload is the --arg KEY=VALUE pairs
        my_tool_reload(i, dll=payload["dll"])
        return {"detail": "reloaded"}           # or {"ok": False, "detail": "why"}, or raise
```

```
python -I tools/gamepool/gamepool.py --config local/mygame.json swap --arg dll=out/core.dll            # every copy `up` started
python -I tools/gamepool/gamepool.py --config local/mygame.json swap --pair 1 --dry-run
python -I tools/gamepool/gamepool.py --config local/mygame.json swap --instances 1,0 --settle-s 30 --out swap.json
```

- **Primeiro conferir.** Consulta `can_swap` em todos os alvos antes de alterar qualquer cópia. Se uma recusar, nada é trocado (saída 2). Adaptador sem hook recusa todas com `no swap hook`.
- **Depois uma por vez**, na ordem fornecida (`--instances 1,0` troca 1 primeiro). Primeira falha interrompe (saída 1); demais ficam `skipped`.
- **Verificação após cada troca.** Precisa continuar o mesmo processo registrado (reiniciar é falha, pois `down` e o conjunto identificam pelo processo), e `probe` precisa aprovar dentro de `--settle-s` (padrão 20 segundos).
- **Só cópias próprias.** Alvos vêm dos processos registrados por `up` para este responsável; confere se continuam os mesmos. Cópia não executando gera saída 2.
- **Relatório.** JSON em stdout (e `--out FILE`): `ok`, `swapped`, conteúdo da troca, linha por cópia com instância, par, papel, PID, `status` (`swapped`, `failed`, `skipped`, `can_swap` em simulação) e `detail`. Progresso em stderr.
- Alvos: `--instances 0,1`, `--pair K` (repetível, ambas as cópias), ou todas iniciadas pelo responsável como padrão.

## <a id="config-file"></a>Arquivo de configuração

Um JSON por jogo. `_notes` e demais chaves com `_` são ignoradas. Caminhos aceitam `%VARS%`. `{i}` (número da instância), `{instance_dir}`, `{game_dir}`, `{role}` são preenchidos onde a tabela indica.

| Chave | Significado |
|---|---|
| `name` | Nome de exibição; também nomeia a pasta padrão das instâncias |
| `game_dir` | Instalação a espelhar. Somente leitura, nunca escrita |
| `instances_root` | Destino das cópias (padrão `<state>/instances/<name>`). Hardlinks exigem mesmo volume NTFS de `game_dir`. Não pode conter `game_dir` nem estar dentro dele |
| `process_name` | Nome da imagem do processo, como `Game.exe`. Reconhece cópias e lista processos externos |
| `launch.exe` | O que iniciar, relativo à instância ou absoluto. `launch.args` e `launch.env` aceitam `{i}`; cópia também recebe `GAMEPOOL_INSTANCE` e `GAMEPOOL_INSTANCE_DIR` |
| `launch.window` | `minimized` (padrão, sem mudar foco), `hidden` ou `normal` |
| `launch.spawns_game` | `true` se `exe` carrega o jogo real e sai. Processo real é encontrado na árvore abaixo do carregador |
| `launch.stagger_s`, `child_wait_s`, `watch_s` | Pausa após cada início, prazo para achar filho do carregador, tempo mínimo de sobrevivência para contar como iniciado |
| `link.modes` | Ordem de tentativas: `hardlink`, `symlink`, `copy` |
| `link.per_instance_files` | Arquivos privados reais por cópia (configurações reescritas, marcadores). Nunca vinculados |
| `link.empty_dirs`, `link.per_instance_dirs` | Pastas vazias por cópia (salvamentos, capturas) ou com conteúdo não vinculado (plugins) |
| `link.root_skip_suffixes` | Saída em execução na raiz (`.log`, `.dmp`), nunca compartilhada |
| `link.pinned_files` | Arquivos com SHA-256 registrado em `provision`, conferido antes de `job` |
| `config_files` | Por configuração privada: `base` (origem somente leitura, opcional), `fallback_base`, `encoding` (padrão `latin-1`, preservando todos os bytes), `edits` como `[section, key, value]`. Cada nome também deve estar em `per_instance_files` |
| `write_files` | Arquivos privados extras: `{ "relative/path": "text with {i}" }` |
| `protected_paths` | Pastas em que nenhuma ferramenta pode escrever (configurações e salvamentos do usuário) |
| `ready` | Critério de prontidão. `type` é `process`, `window`, `file`, `log_line`, `tcp_port` ou `named_pipe`, mais campos necessários (`path`, `text`, `base_port`, `name`, `title_contains`), `timeout_s`, `poll_s`, `settle_s` |
| `crash` | `logs` (relativos à instância), `markers` (texto de linha de falha), `wer_match` (regex do registro Windows) |
| `collect_logs` | Padrões relativos à instância, copiados por `job` após execução |
| `lowcost.rows`, `lowcost.post_checks` | Perfil econômico e valores que precisam valer após aplicação |
| `adapter` | `"file.py:Class"` opcional para comportamento do jogo; veja abaixo |
| `pool` | Padrões do serviço: `recycle_after`, `ws_growth_mb`, `ws_max_mb`, `slot_ttl_s`, `tick_s` |
| `pairs` | Para `--pairs`: `port_base` (27960), `copy_gb` (memória por cópia aberta, 2,0), `reserve_gb` (livre, 2,0), `proto` (`udp`, `tcp` ou `both`, protocolos da verificação de porta, padrão `both`), `edits` (`{"File.ini": [["Section", "Key", "{port}"]]}`, escrito em arquivos privados por par; cada arquivo também deve estar em `link.per_instance_files`) |

A sonda `file` é excluída antes de iniciar; arquivo anterior não faz cópia reiniciada parecer pronta. `log_line` lê log que o jogo precisa renovar em toda inicialização.

[examples/fnv.json](examples/fnv.json) traz os valores do projeto cooperativo Fallout: New Vegas com marcadores `<game dir>`. Bom modelo para jogos estilo Gamebryo com INIs.

### <a id="low-cost-rows"></a>Linhas de baixo custo

Cada linha é `{file, section, key, value, why, status}`. `status` é texto livre exibido na tabela (`required`, `standard`, `guess`, `opt-in` no exemplo). Linha com `"opt_in": "name"` só é aplicada com `--opt name=value` (`pool up --opt grids=3`, `lowcost apply --instance 0 --opt grids=3`); `"value_from_option": true` usa esse valor, e `"option_regex"` rejeita outros. `lowcost doc` exibe tabela Markdown; `lowcost verify` lista chaves presentes nas bases.

### <a id="adapters"></a>Adaptadores

O conjunto precisa de quatro respostas da cópia: pronta, saudável, execute uma vez (carregar salvamento), concessão encerrada (soltar trava no jogo). `swap` acrescenta `can_swap` e `swap` (veja [Troca](#swap)). Sondas embutidas respondem às primeiras pelo bloco `ready`. Jogo com ponte interna (plugin que responde pings e carrega salvamentos) usa algumas linhas Python:

```python
# my_adapter.py, next to your config
from gplib.adapter import Adapter

class MyAdapter(Adapter):
    def probe(self, i, pid):            # healthy right now?
        return my_bridge_ping(i)
    def after_ready(self, i, pid):      # once after each start and restart
        my_bridge_load_save(i, "base")
    def on_release(self, i):            # a lease ended
        my_bridge_unlock(i)
```

E `"adapter": "my_adapter.py:MyAdapter"` na configuração. O arquivo é seu código e executa com seus direitos. A ferramenta usada por New Vegas (cliente de pipe para o plugin interno) não foi adaptada; é exatamente o tipo de elemento de um adaptador.

## <a id="what-it-never-does"></a>O que nunca faz

- Escrever em `game_dir`, em arquivo com mais de um hardlink, link, pasta fora de `instances_root` ou qualquer coisa em `protected_paths` (`instances.guard_write`).
- Encerrar processo que não iniciou. Cada PID é registrado com imagem e horário de criação em `gameslot`; encerra só se os três ainda coincidirem.
- Encontrar jogo por "apareceu processo novo com esse nome". Percorre a árvore do carregador, nunca selecionando jogo iniciado por outra pessoa ao mesmo tempo.
- Fechar handles, injetar ou ler memória de outro processo.
- Iniciar duas cópias simultaneamente ou iniciar sem reservar vaga.

## <a id="how-it-is-tested"></a>Como é testado

```
python -I tools/gamepool/run_tests.py       # prints ALL OK only if every check passes and every twin is caught
```

54 verificações e 50 variantes de mutação quando escrito; aproximadamente três minutos por iniciar processos reais. Nenhum jogo real é iniciado. O jogo é `tests/fake_game.py`, script Python que mantém mutex nomeado, procura classe de janela, escreve prontidão, escuta porta, age como host (escuta) ou cliente (conecta) de um par, ou falha, sem janela visível.

- **Configuração e instalações:** exemplo New Vegas carrega, mas recusa marcadores; recusa configurações vinculadas, chaves desconhecidas e pasta de instâncias contendo instalação ou dentro dela; hardlinks para arquivos grandes, arquivos privados para configurações; hashes da instalação e configurações/salvamentos do usuário antes e depois; provisionar sobre link antigo nunca escreve por ele; destruir mantém instalação; hashes fixados; disco; modo de cópia.
- **Processos substitutos reais:** iniciar duas cópias, registrar PIDs na vaga, encerrar e comprovar que processo-isca de mesmo nome continua; registro adulterado (PID reutilizado) não é encerrado; filho encontrado por árvore, externos ignorados; mutex ou classe de janela fixos impedem segunda cópia, com código de saída relatado; nome por processo permite ambas; falha produz marcadores encontrados pelo relatório; trabalhos passam, falham, expiram, detectam arquivo fixado ausente e sempre liberam vagas; travas de arquivos das instâncias.
- **Prontidão:** sondas de arquivo, linha de log, TCP, pipe e processo; espera com limite e morte; adaptador personalizado carregado da configuração.
- **Política do conjunto (simulações em memória):** concessões exclusivas, host primeiro, reciclar após K concessões, concessões sujas/expiradas, renovação, encerrar só PIDs próprios, recolher PIDs de serviço falho, reiniciar após falha, nunca conceder instância morta, falta de resposta, crescimento de RAM, falhas ao iniciar, renovar vaga e registrar PID.
- **Pilha inteira:** serviço e cliente loopback, vagas reais, conjunto de dois substitutos reais que sobrevive a encerramento de cópia e devolução suja e termina sem cópias e com isca viva; verificação básica limpa após sucesso ou cópia nunca pronta; sonda inicia e encerra uma; CLI de ponta a ponta (provision, status, up, down, crashlog, job, `pool up --fake` com lease, release, status, down).
- **Pares:** cálculo de organização (portas com instâncias não começando em 0, quantidades ímpares e repetições recusadas); RAM e texto de recusa; validação; `provision --pairs`, `--first-pair`, conflitos `--n`, configurações por par, recusa de editar arquivo vinculado à instalação; `up --pairs` com substitutos reais: cada host escuta sua porta e cliente correspondente conecta; segundo `up` não recusa portas próprias; porta ocupada ou pouca RAM não inicia nada nem reserva vaga; `--dry-run` não inicia; outro agente na vaga 0 muda números e arquivos acompanham; `status --pairs` mostra `up`, depois `partial` ao encerrar cliente e nada após `down`; tudo pela CLI.
- **Troca:** simulação não troca; todas trocadas em ordem com conteúdo; uma recusando interrompe antes de tocar qualquer cópia; exceção ou retorno de falha interrompem demais; cópia não saudável após troca ou encerrada durante ela falha; `--pair` e `--instances` escolhem e mantêm ordem; argumentos inválidos, cópia parada e adaptador sem hook recusados.
- **Variantes:** cada uma quebra uma proteção (validação, raiz, arquivos privados, escrita por links, disco, hashes fixados, proteção de escrita, linhas opcionais, sondas, `after_ready`, relato de encerramento, busca de filho por nome, liberação de vaga, travas, substitutos deixados abertos, concessão dupla, falta de reciclagem/expiração, encerrar processos externos, falhas não percebidas, conceder mortos, pares compartilhando porta, host/cliente trocados, ignorar RAM ou cópias já abertas ou memória configurada, não conferir porta ou recusar portas próprias no segundo `up`, estado sempre `up`, configurações não reescritas em `up`, falta de validação dos pares, trocar sem conferir antes, continuar após falha, não conferir resultado, descartar conteúdo, ignorar falha retornada...) e repete a mesma verificação contra ela.

Fora da suíte: jogos reais, `measure`, minimizar janelas visíveis (substituto não mostra nenhuma, testes não alteram a tela) e hardlinks entre volumes (a verificação de disco usa espaço livre simulado).

## <a id="files"></a>Arquivos

`gamepool.py` (CLI), `gplib/` (`config`, `instances`, `inifile`, `lowcost`, `launcher`, `jobqueue`, `adapter`, `pairs`, `poolcore`, `backend`, `fakes`, `daemon`, `client`, `poolcli`, `smoke`, `crashlog`, `measure`, `winproc`), `examples/fnv.json`, `tests/fake_game.py`, `run_tests.py`.

## <a id="ported-from-fnv-coop-commit-f57aa78"></a>Adaptado do commit f57aa78 de fnv-coop

Adaptado de `tools/pool/`, `tools/runner/` (`instances`, `winproc`, `launchprobe`, `crashlog`, `jobqueue`, `multismoke`, `run`) e testes de [fnv-coop](https://github.com/cranebeaker/fnv-coop) (commit f57aa78). Mudanças:

- Caminhos Fallout: New Vegas, nomes de executáveis, chaves INI e cliente da ponte removidos do código. Configurações, perfil econômico, logs e prontidão agora são dados. Valores New Vegas em `examples/fnv.json`.
- Chamadas da ponte viraram interface do adaptador e sondas `ready`.
- Instâncias numeradas por vaga; estado por responsável, evitando compartilhamento entre agentes.
- Busca do carregador por árvore, não por novo nome de processo.
- Proteções mais rígidas: escrever dentro das instâncias e fora de todos os caminhos protegidos.
- Testes refeitos com substitutos simulados; variantes aplicadas pelo executor de fora do código (o conjunto antigo tinha opções exclusivas de teste).

## <a id="generalised-from-fnv-coop-commit-e85460f"></a>Generalizado do commit e85460f de fnv-coop

Pares, proteção de RAM e troca vêm de `tools/runner/run.py`, `instances.py`, `pairs.py` de [fnv-coop](https://github.com/cranebeaker/fnv-coop) (commit e85460f), que iniciavam pares New Vegas e trocavam o núcleo do plugin no jogo aberto. Mudanças:

- Nada específico de jogo. Porta/papel escritos originalmente em configuração de plugin são linhas `pairs.edits` e marcadores dos argumentos de inicialização. Memória por cópia é `pairs.copy_gb`.
- Original usava números fixos (par k = 2k e 2k+1, porta base + k). Aqui seguem vagas concedidas, com porta pelo número da instância host; agentes no mesmo PC não colidem.
- Recarregamento em si (chamada pipe a plugin) continua externo: `swap` chama `can_swap` e `swap` do adaptador, com verificações ao redor (perguntar a todos antes, parar na primeira falha, mesmo processo, saudável novamente).
- Porta ocupada é verificada junto da RAM; `status --pairs` relata par que perdeu cópia.
