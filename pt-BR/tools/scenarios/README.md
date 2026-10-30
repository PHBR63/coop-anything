# <a id="scenarios-jump-to-a-starting-state-then-test"></a>Cenários: salte para um estado inicial e teste

Testes cooperativos precisam de estado inicial: "ambos no acampamento de saqueadores, três saqueadores vivos". Recarregar um salvamento por teste custa um minuto ou mais. Esta ferramenta descreve estado inicial e teste num JSON, verifica o arquivo sem jogo e leva cada instância ao estado por reinicialização no local, recarregando apenas quando necessário.

Independe de jogo. A parte do jogo é uma classe pequena (adaptador) escrita por você.

* [SCHEMA.md](SCHEMA.md): formato (objetos, etapas, verificações, regras de salto).
* `scenlib.py`: carregar, validar, planejar saltos, comparar. Funções puras, só biblioteca padrão.
* `runner.py`: executa cenário por adaptadores, mantém o carregado em cada instância, relata `pass`, `fail`, `error`, `partial`, `invalid`. Também esperas de sincronização por eventos e fechamento de janelas.
* `gameadapter.py`: interface implementada por você, com hooks opcionais.
* `prepare_save.py`: linha de comando que cria salvamento preparado (janelas após carregar já fechadas) e mostra o que está pronto.
* `fakegame.py`: simulação em memória de N instâncias num mundo compartilhado, bugs e hooks ativáveis. Para testes e simulações.
* `scen.py`: linha de comando (`list`, `validate`, `plan`, `run`).
* `examples/fnv/`: quatro cenários Fallout: New Vegas e adaptador pequeno de console, incluindo hooks opcionais.

## <a id="quick-start"></a>Primeiros passos

```
python -I tools/scenarios/scen.py list
python -I tools/scenarios/scen.py validate
python -I tools/scenarios/scen.py plan ownership_handoff --prev fight     # would this jump reload the save?
python -I tools/scenarios/scen.py run fight loot_race quest_stage_sync --fake    # dry run, no game
```

Depois escreva seu arquivo junto dos exemplos (copie um) e execute no jogo:

```
python -I tools/scenarios/scen.py --dir my_scenarios run my_scenario --adapter my_game:make_adapter --players 2
```

`make_adapter(i)` retorna `GameAdapter` da instância `i`. Instância 0 é host. A ferramenta nunca inicia jogo; primeiro você inicia as instâncias e as reúne na sessão.

## <a id="how-to-write-an-adapter-for-your-game"></a>Como escrever um adaptador para seu jogo

Derive de `GameAdapter` (consulte `gameadapter.py`) e preencha cinco itens. Depois vêm os hooks opcionais.

```python
from gameadapter import GameAdapter, ScenarioError

class MyGame(GameAdapter):
    OPS = {"op:kill", "op:move", "op:enable", "check:dead", "check:state"}   # what you can do; leave it out to claim everything

    def __init__(self, conn):                  # conn: however you reach ONE running game instance
        self.conn = conn

    def do(self, op, args):                    # op "kill", args {"ref": "<id from the scenario>"}
        if op == "kill":
            self.conn.run_script("kill %s" % args["ref"])
        elif op == "move":
            self.conn.run_script("teleport %s %s" % (args["who"], args["to"]))   # who may be "player"
        else:
            raise ScenarioError("op %s is not implemented" % op)

    def read(self, kind, args):                # a number. 1 and 0 for true and false
        if kind == "dead":
            return float(self.conn.query("is_dead %s" % args["ref"]))
        raise ScenarioError("check %s is not implemented" % kind)

    def load_save(self, name):  self.conn.load(name)
    def save_game(self, name):  self.conn.save(name)
    def reset_state(self, ids): ...            # put these quests or flags back to their start value, no reload
```

Regras para resultados honestos:

1. Lance `ScenarioError` quando o jogo recusar algo (erro de interpretação no console, objeto ausente). Etapa vira `error`, nunca aprovação silenciosa.
2. Omita o que não consegue fazer. Etapa vira `blocked`, cenário termina `partial`. Cenário impossível de executar não é cenário aprovado.
3. `read` deve consultar a própria instância. Cada verificação executa em cada jogador alvo, encontrando bugs exclusivos do convidado.
4. `reset_state` precisa realmente reinicializar. Se não consegue restaurar algo, deixe o objeto fora do cenário ou defina `start.reload`.
5. Acrescente hook de validação se há dados: `scenlib.validate(sc, hooks=[check_ids_exist])`. Recebe cenário e retorna strings de erro, por exemplo identificador GSPG09Ref ausente no dump. No caso comum (identificador existe e de qual tipo), retorne índice de dados por `data_index()`; consulte abaixo.

`examples/fnv/fnv_game.py` é adaptador pequeno e completo para jogo com console de scripts: operação vira linha de console; verificação vira expressão. Leia primeiro.

## <a id="optional-hooks"></a>Hooks opcionais

Cada hook tem padrão significando "jogo não consegue informar"; executor mantém comportamento antigo. Implemente os que o jogo consegue responder. Nomes e formatos são o contrato; outras ferramentas podem chamá-los.

| Hook | Retorno | Uso |
|---|---|---|
| `sync_status()` | `dict` ou `None` | esperas de sincronização por eventos (próxima seção) |
| `popup_count()` | `int` ou `None` | quantidade de janelas bloqueantes abertas; `None` = não sabe informar |
| `dismiss_popup()` | `bool` | dispensar uma janela aberta; `True` quando pressionada |
| `prepared_names(save)` | `[str]` | nomes tentados para cópia preparada de `save`, melhores primeiro (padrão `["coop_<save>_ready"]`) |
| `save_exists(name)` | `bool` ou `None` | se arquivo de salvamento existe |
| `save_stamp(name)` | valor JSON ou `None` | tamanho e horário de salvamento para detectar alteração na origem |
| `ROLLING_SAVES` (atributo) | tupla de nomes | salvamentos regravados pelo jogo (autosave, quicksave); marca não conferida |
| `data_index()` | `dict`, `DataIndex` ou `None` | identificadores conhecidos nos dados, para conferir cenários sem jogo |

Hook que lança `NotImplementedError` ou `ScenarioError` conta como incapaz de informar.

### <a id="event-driven-sync-waits"></a>Esperas de sincronização por eventos

Após recarregar, clientes retornam à sessão do host. Espera fixa é longa ou curta demais; executor lê `sync_status()` de cada instância e retorna assim que a condição vale: todos entraram, aplicaram o confirmado pelo host, e o host considerou correto mais um resumo de estado (checksum barato do compartilhado enviado pelos clientes). Adaptador responde pela própria instância, todas as chaves opcionais:

```
{"role": "host" | "client" | None,
 "head": 120,                  # host: how far the committed stream is (a number that only grows)
 "applied": 120,               # client: how much of it was applied (same unit)
 "joined": true, "syncing": false, "connected": true, "rejected": null,    # client
 "digests": {"received": 4, "ok": 3, "mismatch": 1, "stale": 0, "rateLimited": 0, "repairs": 1},   # host
 "desyncs": [{"id": 7, "key": "state:q1", "host": "25", "client": "0", "repaired": true}]}         # host, id = report number
```

Também falha cedo, com motivo simples, quando sincronização para de avançar:

* Cliente rejeitou entrada: imediatamente, com seu texto.
* Progresso do cliente (entrada, aplicação, estado inicial, conexão) parado por `stall_s` (padrão 30 s): motivo identifica cada cliente ("client 0: applied 50 of 100", "not joined", "link not connected").
* Sem resumo por `digest_stall_s` (padrão 20 s), `stale_limit` resumos obsoletos (3) ou mesma divergência `repeat_limit` vezes (3; mesmas chaves e valores: reparo não funciona). Resultado lista `desyncEntries` divergentes e contadores `digestDelta`.
* `timeout_s` (180 s) e `digest_timeout_s` (60 s) são limites externos.

Todos parametrizáveis: `Runner(..., sync={"stall_s": 10, "repeat_limit": 2})` ou `runner.wait_synced(stall_s=10)`. `stall_s` 0 desativa saída por paralisação. Resultado em `jump.coopSync` do log: `synced`, `seconds`, `reason`, `digestOk`, `settleReason`, `settleSeconds`, `settleRepairs`, `digestDelta`, `desyncEntries`. Etapa de preparação que move, cria ou define estado também espera (até 10 s, paralisação 5 s) clientes aplicarem; registro recebe `syncWait` quando não funciona. Adaptador que retorna `None` mantém comportamento anterior: pausa fixa (`load_wait_s`, `settle_s`) sem `coopSync`.

### <a id="prepared-saves"></a>Salvamentos preparados

Alguns jogos mostram muitas mensagens após carregar. Uma caixa aberta pode manter modo de menu, perdendo entradas de teste; fechá-las exige longa janela sem mensagens. `prepare_save.py` faz isso uma vez e salva resultado com nome de pronto em cada instância:

```
python -I tools/scenarios/prepare_save.py fight --adapter my_game:make_adapter                 # prepare the start save of a scenario
python -I tools/scenarios/prepare_save.py --save autosave --adapter my_game:make_adapter --instances 2,3
python -I tools/scenarios/prepare_save.py --status fight [--adapter my_game:make_adapter]      # what is prepared; no game needed
```

Usa o mesmo `--adapter pkg.mod:factory` de `scen.py run`. `--instances` lista identificadores enviados à fábrica (padrão `0,1`), equivalente a apontar cópias por pipe ou porta: segundo par é `2,3`, com salvamentos guardados sob esses identificadores. Carrega salvamento, dispensa janelas por `popup_count()` e `dismiss_popup()` até nenhuma aparecer por 20 s, salva sob `prepared_names(save)` (próximo nome tentado quando primeiro recusado), carrega preparado e verifica ausência de janelas. Exibe linha JSON por salvamento com `ok`; termina com 1 quando janelas nunca cessam, cópia recusa salvamento ou recarga ainda mostra janela. Saída 2 indica uso inválido (sem adaptador ou sem hooks de janelas).

Fatos num JSON: `./scen_prepared.json`, `$SCEN_PREPARED_FILE` ou `--prepared FILE` (`scen.py run` aceita mesma opção). Chaves por instância e salvamento inicial. Salto só usa preparado se adaptador confirma arquivo (`save_exists`), conferência de recarga passou e origem não mudou (`save_stamp`; `ROLLING_SAVES` isentos). Senão, carrega original e log explica em `jump.loadedSaves[].why`. Quando todas carregam preparado, janela sem mensagens cai de 20 para 4 s como proteção. Plano ainda vê salvamento inicial original; cópia preparada nunca parece salvamento diferente.

Desative com `SCEN_NO_PREPARED=1` no ambiente ou `"start": {"prepared": false}` no cenário.

### <a id="check-ids-against-the-game-data"></a>Conferir identificadores nos dados do jogo

`data_index()` retorna os conhecidos como `{"<id>": "<kind>"}` (tipo é categoria de objeto, lista de categorias ou `None` para qualquer) ou `scenlib.DataIndex(entries, kinds=None, case_sensitive=True, label="the game data")`. `Runner.run` rejeita antes de chamar o jogo se objeto desconhecido ou de outro tipo. Confere todos do glossário; erro indica usos, inclusive preparação (mover, dar, ativar, criar e demais):

```
objects.raider2: id 'GSPG02Ref' is not in the game data (used by setup step enable_raider2 (enable), step all_alive_2 (check));
nearest known id: 'GSPG02Rex' (also close: 'GSPG03Ref', 'GSPG01Ref')
```

Um `base` de objeto é conferido como item ou tipo criável. `kinds=` limita o índice às categorias cobertas. Jogo sem índice pula conferência, declarando isso em `notes`. Sem jogo:

```
python -I tools/scenarios/scen.py validate fight --index ids.json                 # ids.json is {"id": "kind"}
python -I tools/scenarios/scen.py validate fight --adapter my_game:make_adapter   # uses the adapter's data_index()
```

Linhas de console e identificadores específicos ficam no adaptador. `examples/fnv/fnv_game.py` mostra índice a partir de tipos de registro (`records={"GSPG01Ref": "ACHR"}`) e outros hooks.

## <a id="how-it-is-tested"></a>Como é testado

```
python -I tools/scenarios/run_tests.py
```

Exibe `ALL OK` só quando todos passam e todas as variantes são detectadas. Não inicia jogo.

* 120 testes unitários: validador (todo tipo de arquivo inválido), resolução de identificadores, tradução de operações e verificações, tabela de comparação, regras de salto, executor contra `fakegame.py` (convidado que nunca vê mudanças, saque duplicado, criação dupla, transferência ausente, etapas bloqueadas, erros de console, arquivos inválidos nunca chegando ao jogo, salto local ou recarga e salto local com menos de 20 chamadas), adaptador exemplo contra ponte de gravação e linhas de comando. Desses, 61 cobrem os três recursos novos, todos no jogo simulado (tempo virtual, sem esperas reais): sincronização (saudável termina no primeiro resumo correto, cliente preso ou silencioso, entrada rejeitada, conexão morta, divergências obsoletas/repetidas, divergência reparada, limites parametrizados, ausência de hooks mantendo pausa fixa), preparados (preparar, usar, origem alterada, recarga falha, arquivo recusado/ausente, desativação, instâncias, códigos de saída) e índice (desconhecido com mais próximo, tipo errado, operações preparatórias, bases, tipos cobertos, distinção de maiúsculas, executor, linha de comando).
* 20 variantes de mutação. Suíte repetida com um comportamento quebrado (`SCEN_MUTANT`). Primeiras cinco: sem conferir aliases, salto nunca recarrega, cenários esquecem mudanças, toda verificação passa, toda etapa só no host. Mais cinco para esperas (nunca desistir de cliente preso, espera de resumo sem terminar cedo, sucesso só percebido no limite, primeira divergência encerrando espera, falha sem entradas divergentes), sete para preparados (nunca carregados, janela longa, origem obsoleta, salvamento não verificado, sem conferir recarga, salvo antes de fechar janelas, instâncias registradas por posição) e três para índice (nunca consultado, sem correspondência mais próxima, tipo errado aceito). Cada uma precisa causar falha; execução exibe `caught` para cada.

Atualizado a partir do commit e85460f de fnv-coop.

## <a id="ported-from-fnv-coop-commit-f57aa78"></a>Adaptado do commit f57aa78 de fnv-coop

Adaptado do projeto cooperativo Fallout: New Vegas ([cranebeaker/fnv-coop](https://github.com/cranebeaker/fnv-coop), commit f57aa78). Formato, validador, planejador, executor e simulação tornados independentes: identificadores de formulários e ordens de plugins viraram identificadores livres; conferências de dumps viraram hooks de validação; comandos Fallout migraram ao adaptador exemplo.
