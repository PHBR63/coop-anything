# <a id="co-op-bots-and-playbooks"></a>Bots e roteiros de modo cooperativo

O modo cooperativo falha de formas que um jogador sozinho nunca vê: dois pegam o mesmo item, a morte causada por um não chega à outra máquina, uma etapa de missão dispara duas vezes, alguém que retorna recebe todas as recompensas de novo. Estes testes executam 2 a 4 instâncias reais, controlam cada uma com um bot e verificam, após cada etapa, se todas as máquinas concordam.

É independente de jogo. O executor e os doze roteiros não conhecem nenhum jogo. Toda especificidade fica numa classe, o **adaptador de ações**, escrita por você.

```
playbook (what to do, what must hold)  ->  runner (settle, compare, counters, evidence)  ->  ActionAdapter (your game)
```

* `coopbots/adapter.py`: interface do adaptador (`ActionAdapter`, `Result`, `MissingAction`). Leia a docstring do módulo.
* `coopbots/core.py`: executor: etapas, estabilização, janelas de silêncio, limites de reparo, comparação de estado, contadores de dessincronização, evidências de falha.
* `coopbots/playbooks/`: roteiros escritos somente para a interface do adaptador.
* `coopbots/fakecoop.py`: sessão cooperativa simulada (host e 1 a 3 clientes atrasados) com 30 bugs ativáveis. É o adaptador de teste.
* `coopbots/links.py`: opções de enlaces degradados. `coopbots/refs.py`: referências dos roteiros vindas de um arquivo de cenário.
* `adapters/fnv/`: pequeno adaptador de exemplo para jogo Gamebryo com console de scripts.
* `coopbots/results.py`: modelo do resultado de ações (`ActionResult`, `Fail`, `Why`, `ensure`).
* `run_coop.py`: linha de comando. `run_parallel.py`: um executor por par host/cliente. `run_tests.py`: testes.

## <a id="quick-start"></a>Primeiros passos

A primeira execução não precisa de jogo:

```
python -I tools/bots/run_coop.py --list
python -I tools/bots/run_coop.py --fake --playbook all
python -I tools/bots/run_coop.py --fake --playbook loot_race --bug dup_pickup      # must FAIL: the bug is caught
python -I tools/bots/run_coop.py --fake --playbook quest_sync --link bad_wifi      # lossy link with quiet windows
```

No seu jogo, depois de ter adaptador (você inicia as instâncias e as conecta numa sessão; a ferramenta nunca inicia jogo):

```
python -I tools/bots/run_coop.py --adapter my_game:make_adapter --players 2 \
    --scenario my_scenarios/fight.json --playbook fight
```

`make_adapter(i)` retorna o adaptador da instância `i`; instância 0 é o host. `--scenario` é um arquivo de cenário de [tools/scenarios](../scenarios/README.md), cujo bloco `refs` nomeia o necessário ao roteiro (`--refs file.json` faz o mesmo com JSON simples). Código de saída 0 significa ao menos um roteiro aprovado e nenhum reprovado. Um `SKIP` (falta ação exigida pelo roteiro) nunca é aprovação; se todos forem pulados, a execução sai com 1.

## <a id="how-to-write-an-adapter-for-your-game"></a>Como escrever um adaptador para seu jogo

Um objeto adaptador controla uma instância em execução. Derive de `ActionAdapter`, implemente primeiro a interface com o motor e depois as ações dos roteiros desejados. Tudo que ficar ausente lança `MissingAction`, `supports("take")` informa a ausência, e cada roteiro que precisar disso recebe `SKIP` com o nome da ação ausente.

### <a id="1-the-engine-surface-the-runner-uses-these-after-every-step"></a>1. A interface do motor (usada pelo executor após toda etapa)

```python
from coopbots.adapter import ActionAdapter, Result

class MyGame(ActionAdapter):
    def __init__(self, conn, name="bot"):
        self.conn, self.name = conn, name

    def status(self):
        s = self.conn.sync_status()                  # whatever your netcode can tell you
        return {"seq": s.last_applied,               # number of the last host update this machine applied
                "synced": s.all_clients_caught_up,   # host only; leave out on clients
                "counters": {"mismatches": s.digest_mismatches, "repairs": s.repairs,
                             "bad_messages": s.bad_messages, "apply_failures": s.apply_failures, "rebases": s.rebases}}

    def snapshot(self):
        return {"shared": self.conn.dump_world(),    # must be EQUAL on every machine once synced
                "per_player": self.conn.dump_me()}   # inventory, position: allowed to differ

    def capture(self, directory):                    # optional: logs for a failed step
        ...
```

* `seq` informa ao executor a convergência: ele aguarda todos os clientes relatarem o número do host e o manterem por duas consultas. Sem número de sequência no código de rede, use um contador igual em todas as máquinas quando nada estiver em trânsito (um hash de estado serve).
* `counters` são opcionais. Use `mismatches`, `repairs`, `repaired_effects` (dessincronização encontrada e corrigida) e `bad_messages`, `apply_failures`, `rebases` (nunca aceitáveis). Um contador que aumenta durante a etapa faz a etapa falhar. Nomes adicionais ficam nos registros, mas nunca causam falha.
* `shared` é comparado caminho por caminho entre host e clientes. Deixe de fora elementos individuais ou cosméticos, ou liste-os em `snapdiff_ignore` (padrões fnmatch como `shared/refs/*/in_use*`). `shared` vazio é recusado.

### <a id="2-actions-return-a-result-check-the-postcondition"></a>2. Ações: retorne `Result`, confira a pós-condição

```python
    def take(self, item, count, from_ref):
        before = (self.inventory_count(item), self.inventory_count(item, from_ref))
        self.conn.run("transfer %s %s %d" % (from_ref, item, count))
        after = (self.inventory_count(item), self.inventory_count(item, from_ref))
        if after[0] - before[0] != count or before[1] - after[1] != count:
            return Result(False, "transfer moved %d in and %d out" % (after[0] - before[0], before[1] - after[1]))
        return Result(True)
```

* Recusa normal (porta trancada, disputa perdida) é `Result(False, "reason")`. Lance exceção somente se jogo ou enlace estiver indisponível; o executor registra travamento como etapa malsucedida com rastreamento.
* Confira se o fato realmente ocorreu, não apenas se a chamada retornou. Bot que relata sucesso só porque a chamada foi aceita é a principal fonte de aprovações vazias. O adaptador de exemplo mostra o padrão para `take`, `pickup`, `unlock`, `goto_ref`.
* Todo resultado é `ActionResult(ok, reason, data, action, elapsed_s)`; a classe base envolve o retorno da ação, então você nunca o monta manualmente. Veja "Resultados de ações" abaixo para pré-condições, pós-condições e explicações de falha.
* IDs (`ref`, `item`, `quest`) são strings opacas. Os roteiros apenas devolvem o que receberam do cenário.
* A lista completa de ações e consultas, com o retorno exigido de cada uma, está na docstring de `coopbots/adapter.py`. A tabela abaixo informa as exigências por roteiro.

### <a id="3-run-it"></a>3. Execute

Execute um roteiro com `--adapter`. Corrija o que `SKIP` e `FAIL` indicarem, uma ação por vez. Mantenha o adaptador junto aos testes do jogo. `adapters/fnv/fnv_adapter.py` (menos de 150 linhas) é um exemplo pequeno completo: comandos de console para ações, expressões para consultas e mapeamento de estado.

## <a id="action-results-pre-and-postconditions-and-say-why"></a>Resultados de ações: pré e pós-condições e explicações do motivo

Toda ação retorna `ActionResult` (um `Result` que também conhece o nome da ação e a duração). Uma falha aparece como `code: what the bot saw`, por exemplo `stuck: 312 units left (wanted within 150)`. O código é curto e estável (`result.code`); o restante é para quem lê a etapa malsucedida. `coopbots/results.py` contém o modelo e `Why`, falhas prontas para casos comuns: `stuck`, `too_close`, `too_steep`, `menu_open`, `message_box`, `holstered`.

```python
from coopbots.adapter import ActionAdapter, Why, ensure

class MyGame(ActionAdapter):
    def blockers(self):                              # what stands in the way of input right now
        out = []
        if self.ui.menu_open():
            out.append(("menu", "the %s menu is open" % self.ui.menu_name()))
        if self.ui.message_box():
            out.append(("message_box", "a message box is up"))
        return out

    def goto_ref(self, ref, dist=150):
        def arrived(data):                           # postcondition: the world really changed
            left = self.game.distance(ref)
            if left > dist:
                raise Why.stuck(left, dist)          # "stuck: 312 units left (wanted within 150)"
        return self.act(lambda: self.game.walk_to(ref), free=True, post=[arrived])
```

* `self.act(do, pre=[...], post=[...], free=False)` executa verificações em torno da ação. `free=True` recusa iniciar se `blockers()` listar algo (use `ignore=("holstered",)` em ações que não exigem arma empunhada). Uma verificação malsucedida lança `Fail(code, say)` ou usa `ensure(cond, code, say)`; os dados do resultado identificam qual `phase` falhou: `pre`, `do` ou `post`.
* A classe base acrescenta o texto de `blockers()` atual a toda ação malsucedida; um simples `Result(False, "door is locked")` vira `door is locked: a message box is up`. Sobrescreva `explain(action, result)` para outra nota.
* `adapter.strict = True` lança `ActionFailed` em vez de retornar resultado malsucedido (útil em script pontual).
* `adapter.recent_actions(n)` é o log das últimas ações. O executor o guarda em `failure.json` como `recent_actions` por máquina.
* Ação que retorna `None` lança `TypeError`: retorne um `Result`. `True` ou `False` simples são aceitos.
* Uma pós-condição errada de propósito é como a ferramenta se testa: `tests/test_actions.py` tem adaptador cujo `take` não faz nada, e a pós-condição precisa detectá-lo.

## <a id="fast-rounds-resume-fail-fast-game-speed"></a>Rodadas rápidas: retomada, falha antecipada e velocidade do jogo

Falhar na etapa 4 não deveria custar repetir as etapas 1 a 3.

```
python -I tools/bots/run_coop.py --adapter my_game:make_adapter --playbook fight --from-step 4 --timescale 3
python -I tools/bots/run_coop.py --adapter my_game:make_adapter --playbook fight --only-step 4
python -I tools/bots/run_coop.py --fake --playbook quest_sync --from-step 3        # game free
```

* **Etapas retomáveis.** Um roteiro retomável executa cada etapa por `ctx.run_step(name, body, arrange=...)`. `arrange` é uma função idempotente que prepara o mundo no estado esperado (jogadores armados junto aos inimigos, etapas anteriores definidas, inimigos anteriores mortos). Em execução parcial, a primeira etapa executada recebe `arrange` uma vez; execução completa nunca prepara. Se a preparação for impossível (alvo que precisa viver já morto), falha com tipo `arrange` e orienta executar o roteiro inteiro ou recarregar o cenário. `fight`, `loot_race` e `quest_sync` são retomáveis (`--list` os marca com `R`); os demais recusam `--from-step` com saída 2 e listam os compatíveis. Execute o roteiro inteiro uma vez antes de confiar na aprovação parcial. Uma falha exibe a linha para repetir.
* **Estabilização com falha antecipada.** `ctx.settle()` interrompe cedo se nenhum número de atualização das máquinas nem confirmação do host mudar durante a janela de estagnação (`--settle-stall S`, opção `settle_stall_s`, padrão `max(6, budget / 4)` segundos; 0 desativa). O motivo informa duração da imobilidade, número de atualização de cada máquina e, se `status()` fornecer dicionário `acks`, o que o host sabe que cada cliente recebeu. Contador de divergência que continua aumentando durante a estagnação também é identificado.
* **Velocidade do jogo.** `--timescale X` chama `set_timescale(X)` em todas as máquinas antes da primeira etapa e `set_timescale(1)` no fim, inclusive após falha. Recusa de uma máquina interrompe antes das etapas. Se o adaptador também tiver `timescale()`, detecta uma cópia que aceita, mas roda em outra velocidade, ou continua acelerada depois. Esperas fixas `ctx.pause()` diminuem por X. A especificidade do jogo é um método do adaptador: o exemplo envia um comando de console. Verificações dependentes de tempo real podem precisar de execução em 1x.

## <a id="several-pairs-at-once"></a>Vários pares ao mesmo tempo

```
python -I tools/bots/run_parallel.py --pairs 3 -- --adapter my_game:make_adapter --scenario fight.json --playbook fight
python -I tools/bots/run_parallel.py --only 1 -- --adapter my_game:make_adapter --playbook quest_sync --from-step 3
python -I tools/bots/run_parallel.py --pairs 3 --fake -- --playbook all          # game free smoke test
python -I tools/bots/run_parallel.py --pairs 3 --dry-run -- --playbook fight     # checks and commands only
```

`run_parallel.py` inicia um `run_coop.py` por par host/cliente como subprocesso (`--runner FILE` para executor próprio). Par k corresponde às instâncias `2k` e `2k+1` (`--players-per-pair N` para mais); cada executor recebe `--instances A,B --outdir <out>/pair<k>` (sua fábrica recebe esses números; o primeiro é o host) e encontra o par em `COOP_PAIR`, `COOP_INSTANCES` e, com `--port-base P`, `COOP_PORT` (P + k). Argumentos após `--` vão a todos. O log de cada par é transmitido com prefixo `[pair<k>]`; no fim, uma tabela mostra PASS, FAIL, SETUP, BLOCKED, TIMEOUT ou CRASH por par e o motivo de cada falha; `parallel_summary.json` também contém isso. Códigos: 0 todos aprovados, 1 qualquer FAIL, TIMEOUT ou CRASH, 3 par BLOCKED (executor saiu com 3), 2 problema de preparação. Recusa iniciar se dois pares compartilharem instância, porta ou pasta de saída, ou se `--instances`, `--outdir` ou `--players` vier após `--`. `--preflight module:function` acrescenta verificações próprias (RAM livre, reserva de instância, porta ocupada): a função recebe a lista de planos e retorna textos de problemas. `--timeout S` interrompe executor travado, somente aquele processo. Paralelismo aumenta vazão, não encurta uma rodada individual.

## <a id="the-playbooks"></a>Os roteiros

Cada roteiro é um pequeno script de etapas. Após cada uma, o executor estabiliza, compara estados e verifica contadores. `refs` são os nomes exigidos do cenário (ou de `--refs`). `requires` são os métodos necessários em todas as máquinas; sem eles, o roteiro é pulado.

| roteiro | jogadores | refs | requires | o que cada etapa comprova |
|---|---|---|---|---|
| `fight` | 2-4 | `raiders` (lista), `raider_base?`, `weapon?` | goto_ref, aim_at, fire, target_alive | Todos atiram nos mesmos inimigos; mortos em todas as máquinas, cada um morre uma vez, contagem constante (exige `ref_count`; caso contrário, pula com nota). |
| `ownership_handoff` | 2-4 | `raiders`, `far_pos`, `near_pos` | goto_ref, goto_pos, aim_at, fire, target_alive, owner_of | Host se afasta: controle passa uma vez ao cliente, não oscila quando host retorna, luta continua. |
| `loot_race` | 2-4 | `item`, `item_base` | goto_ref, pickup, inventory_count, ref_enabled, drop | Exatamente um vence a coleta e o grupo tem exatamente 1; mais duas rodadas largando e disputando novamente. |
| `container_share` | 2-4 | `container`, `item_a`, `item_b` | goto_ref, open_container, close_container, take, put, inventory_count | Uma trava de "em uso"; retirar e colocar replicam; nada duplicado ou perdido. |
| `door_lock` | 2-4 | `door`, `locked_door`, `device`, `device_entry`, `locked_box`, `key` | doors, unlock, use_device, is_locked, containers | Host e cliente abrem e fecham porta; porta trancada recusa; chave destranca; entrada de dispositivo destranca caixa. |
| `fast_travel_tether` | 2-4 | `marker`, `anchor`, `tether_radius`, `far_pos`, `hostile?`, `weapon?` | goto_ref, fast_travel, consent, distance_to, cell | Recusado sem consentimento e em combate; todos chegam juntos; quem se afasta é contido pelo vínculo de distância. |
| `dialogue_spectator` | 2-4 | `npc`, `topics`, `speakers?`, `done_quest?`, `done_stage?` | talk, pick_topic, end_dialogue, in_dialogue, spectating | Um fala, demais assistem e são liberados, sem segundo interlocutor, papéis trocam. |
| `consent_vote` | 2-4 | `barrier_quest`, `barrier_stage` e/ou `confirm_ref`, `confirm_quest`, `confirm_from`, `confirm_to` | set_stage, barrier_pass, activate, answer_prompt, consent | Barreira segura até o último passar e aplica uma vez; confirmação de prontidão: recusa, "ainda não" de convidado veta, todos prontos aplica uma vez. |
| `consent_vote_guest_declines` | 2-4 | Mesmos. | Mesmos. | Confirmação para após veto: etapa permanece em todos os lugares. |
| `quest_sync` | 2-4 | `quest`, `stages` | set_stage, start_quest, stage_done, objective flags | Etapas e indicadores dos objetivos correspondem em todas as máquinas; repetir etapa não tem efeito. |
| `save_load_rejoin` | 2-4 | `quest`, `stage_a`, `stage_b`, `reward_item?`, `save_name?` | save_game, load_game, session_leave, session_join, rebases | Cliente sai, host avança, cliente retorna e recupera com cada recompensa uma vez; host carrega salvamento anterior, todos os clientes redefinem a base; segundo retorno não acrescenta nada. |
| `spawn_once` | 2-4 | `marker`, `base` | goto_ref, spawn, ref_count | Host cria um; existe exatamente um em cada máquina e continua sendo um. |

`far_pos` e `near_pos` são `{"ref": id, "dist": units}` ou `{"x": .., "y": .., "z": .., "cell": ..}`. `stages` é `[[stage, [[objective, "displayed" or "completed", 0 or 1], ...]], ...]`.

Um roteiro é uma classe: defina `name`, `needs_refs`, `requires`, escreva `run(ctx)` com blocos `with ctx.step("..."):` e acrescente a `coopbots/registry.py`. Auxiliares em `ctx`: `must`, `expect`, `on_all` (todas as máquinas ao mesmo tempo, uma thread cada), `same_everywhere`, `wait_until`, `pause`, `settle`, `optional` (verificação que pode precisar de ação ausente), `equip_all` e `run_step(name, body, arrange=...)` (etapa que `--from-step` e `--only-step` podem pular ou usar como início; defina `resumable = True` quando todas a utilizarem).

## <a id="what-the-runner-checks-after-every-step"></a>O que o executor verifica após cada etapa

1. **Estabilização:** toda máquina relata o último número do host, estável por duas consultas, ou falha identificando máquinas e números. Para cedo, com motivo, quando nada muda (consulte "Rodadas rápidas").
2. **Janela de silêncio** (opção `quiesce_s`, para enlaces degradados): nada é enviado nesse intervalo, todas as máquinas precisam convergir e nenhum reparo pode ocorrer numa segunda janela.
3. **Comparação de estado:** parte `shared` de cada cliente contra o host.
4. **Contadores:** reparos e divergências não podem aumentar (salvo `strict_counters` desativado, abaixo); mensagens inválidas, falhas de aplicação e redefinições de base nunca podem aumentar (etapa que espera redefinição passa `allow_rebase=True`).
5. **Limite de reparo** (opção `repair_budget_per_min`): reparos por minuto na execução inteira. Padrão não definido; com enlace degradado, padrão 0. Limite acima de 0 no arquivo de perfis exige `repair_budget_reason` ao lado.

Em qualquer falha, escreve `FAIL-<n>-<step>/` com `failure.json` (motivo, estado por máquina, captura, etapas até ali), captura de estado de cada máquina e o que `capture()` produzir, além de `result.json` e `snap/` da execução inteira.

### <a id="impaired-links"></a>Enlaces degradados

`--link bad_wifi` (ou `links.link_options("bad_wifi")`) desativa contadores estritos e acrescenta janela de silêncio e limite. Não degrada a rede por conta própria: inicie o retransmissor de `tools/chaos` entre as instâncias. Perfis: `lan`, `good_wifi`, `bad_wifi`, `mobile_tether`, `transatlantic`, `hell`. Reparos nunca são ignorados: registrados por etapa, precisam parar quando o mundo estabiliza e estão sujeitos ao limite.

## <a id="how-it-is-tested"></a>Como é testado

```
python -I tools/bots/run_tests.py
```

Exibe `ALL OK` somente se todos os testes passarem e todas as variantes forem detectadas. Somente simulações: nenhum jogo é iniciado.

* 138 testes unitários (59 antes dos recursos novos). Todo roteiro passa no mundo simulado com 2, 3 e 4 jogadores, enlace atrasado e enlace com perdas. Adaptador sem ação exigida resulta em roteiro pulado, nunca aprovado. Roteiro sem etapas não aprova. Contagem incorreta de jogadores ou referência ausente causa falha clara. Uma etapa malsucedida salva evidências. O adaptador de exemplo roda contra console em memória; cada pós-condição é testada com console que mente. Linha de comando testada para códigos de saída, `--link`, execução por `--adapter` com referências de cenário.
* 27 variantes de roteiros: roteiro mais comportamento deliberadamente errado do mundo simulado (coleta duplicada, barreira liberada cedo, vínculo de distância não aplicado, cliente que nunca redefine a base, eco obsoleto de vida, cliente que para de aplicar atualizações, ...). Cada uma precisa fazer o roteiro dar FAIL; um teste verifica que todos os 30 bugs simulados têm variante correspondente. `counter_noise` (contadores crescentes) precisa reprovar os 12 roteiros. Um teste comprova que só a comparação de estado detecta criação duplicada que nenhuma consulta investiga.
* Testes de enlace degradado: todos os roteiros passam com perdas; mensagem perdida definitivamente, reparo na janela de silêncio e reparos acima do limite falham; limite acima de 0 exige motivo escrito.
* Recursos novos têm testes próprios no mundo simulado: modelo de resultados (`tests/test_actions.py`: tipo, pré e pós-condições, adaptador mentiroso, modo estrito, todos os motivos explicados: caminhada presa, menu aberto, mensagem, arma guardada, alvo perto ou inclinado demais, evidências em `failure.json`); retomada, estabilização com falha antecipada e velocidade (`tests/test_resume.py`: `--from-step`, `--only-step`, preparação, cliente congelado, cópia que ignora ou recusa velocidade); executor paralelo (`tests/test_parallel.py`: plano, verificações, todos os códigos, subprocessos reais com logs prefixados e tabela única).
* 15 variantes do motor: a suíte roda novamente com uma verificação do próprio executor quebrada (`COOPBOTS_MUTANT`: sem estabilização, comparação de estado ou verificação de contadores; itens pulados contados como aprovados; falhas sem explicação; pós-condições não verificadas; retomada que executa tudo; retomada sem preparação; estabilização que nunca para cedo; velocidade que não chega ao jogo; logs paralelos sem prefixo; saída sempre 0; mesmo conjunto de instâncias para todos os pares; executor travado nunca interrompido; opções proibidas aceitas). Cada uma precisa fazer um teste falhar. Variantes dos recursos novos executam apenas os arquivos de teste que os cobrem.

## <a id="ported-from-fnv-coop-commit-f57aa78"></a>Adaptado do commit f57aa78 de fnv-coop

Atualizado a partir do commit e85460f de fnv-coop: modelo de resultados, etapas retomáveis, estabilização com falha antecipada, `--timescale` e executor de pares paralelos foram generalizados do trabalho mais recente do projeto Fallout. Especificidades permaneceram lá: comandos de velocidade, leituras de menu/arma e detalhes de caminhada e mira estão somente no adaptador de exemplo em `adapters/fnv/`.

Adaptado do projeto cooperativo Fallout: New Vegas ([cranebeaker/fnv-coop](https://github.com/cranebeaker/fnv-coop), commit f57aa78), onde roteiros e executor foram inicialmente escritos contra sua ponte de jogo. Executor, roteiros e mundo simulado foram tornados independentes (IDs como strings opacas, nomes genéricos de história e rede, camada de ações por jogo convertida em interface adaptadora). Permaneceram no projeto Fallout: plano das missões iniciais, verificações de animação/pose e código que controla entrada e funções do motor. O adaptador de console Fallout em `adapters/fnv/` mostra o formato de um primeiro adaptador sem tudo isso.
