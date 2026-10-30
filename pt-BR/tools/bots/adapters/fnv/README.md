# <a id="example-adapter-fallout-new-vegas-script-console"></a>Adaptador de exemplo: Fallout: New Vegas (console de scripts)

`fnv_adapter.py` é um `ActionAdapter` pequeno e completo para um jogo Gamebryo com console de scripts e uma ponte para o jogo em execução. Ele exemplifica como um primeiro adaptador pode ser curto; não é um adaptador pronto para todos os roteiros.

Ele implementa: `goto_ref`, `activate`, `pickup`, `take`, `put`, `set_stage`, `unlock`, `set_timescale` e as consultas `inventory_count`, `target_alive`, `ref_enabled`, `is_locked`, `door_open`, `distance_to`, `quest_stage`, `stage_done`, além de `status`, `snapshot` e `capture`. O restante fica de fora; por isso, os roteiros que precisam dessas funções (viagem rápida, diálogo, criação de objetos, ...) recebem `SKIP`, que é a resposta honesta até alguém implementar essas ações.

O que aproveitar dele:

* Uma linha de console por ação, uma expressão por consulta. Os identificadores são IDs do editor ou IDs hexadecimais aceitos pelo console.
* Uma pós-condição após cada ação. `take` e `put` leem ambos os inventários antes e depois e falham se os dois não variarem pela mesma quantidade, detectando transferências que dupliquem ou percam itens. `pickup` falha com "already taken" para quem perde uma disputa e verifica se o objeto realmente desapareceu. `goto_ref` verifica a distância depois do movimento.
* `status()` mapeia os contadores do próprio mod cooperativo para os nomes do executor em uma pequena tabela (`COUNTER_PATHS`).
* Explicação do motivo: `blockers()` lê `ui.status` do mod (menu aberto, caixas de mensagem, arma empunhada), e a classe base acrescenta isso a toda ação malsucedida. `goto_ref` passa por `self.act(...)` com uma pós-condição e falha como `stuck: N units left`.
* `set_timescale` é a única linha específica do jogo no recurso `--timescale`: a linha de console `sgtm X`.

O objeto da ponte precisa de `exec(line)`, `eval(expr)` e `call(method, params)` (para `coop.status`, `state` e `events` do mod). Os testes (`tools/bots/tests/test_adapters.py`) executam o adaptador contra um console em memória, incluindo um console que ignora silenciosamente um comando de cada vez, para demonstrar o disparo de cada pós-condição. Nenhum jogo é iniciado.

O adaptador de cenários correspondente é `tools/scenarios/examples/fnv/fnv_game.py`.
