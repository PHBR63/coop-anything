# <a id="scenario-format-schema-1"></a>Formato de cenário, esquema 1

Um cenário é um arquivo JSON. Descreve o estado inicial, as etapas seguintes e as condições que devem ser satisfeitas em todas as máquinas. O executor coloca todas as instâncias no estado inicial, executa as etapas e informa `pass`, `fail`, `error`, `partial` (uma etapa precisa de algo que o adaptador não oferece) ou `invalid` (o arquivo está incorreto; nenhum jogo foi alterado).

O nome do arquivo é o nome do cenário: `fight.json` contém `"name": "fight"`.

## <a id="top-level"></a>Nível superior

| chave | significado |
|---|---|
| `schema` | sempre `1` |
| `name` | `lower_snake_case`, igual ao nome do arquivo sem `.json` |
| `title`, `description` | texto para pessoas; ambos obrigatórios |
| `players` | de 1 a 4 instâncias do jogo compartilhando um mundo. Jogador 0 é o host |
| `tags` | lista livre de strings |
| `start.save` | nome do salvamento inicial. `start.reload: true` força recarregar mesmo quando já está carregado o mesmo salvamento |
| `start.prepared` | booleano opcional. `false` sempre carrega o `start.save` original, nunca uma cópia preparada (consulte "Prepared saves" no README). Padrão `true`: usa uma cópia preparada se o adaptador tiver uma |
| `reset.keys` | lista `$alias` de objetos de estado (missões, indicadores, variáveis de scripts) redefinidos sem recarregar pelo salto. Toda chave de `set_state` é acrescentada automaticamente |
| `objects` | glossário, explicado abaixo |
| `refs` | nomes opcionais para a ferramenta de bots (`tools/bots`): nome de referência para `$alias`, lista ou objeto aninhado. Os aliases viram identificadores |
| `setup` | etapas executadas durante o salto, após a redefinição |
| `steps` | o teste: etapas e verificações, em ordem. É obrigatória pelo menos uma verificação |

## <a id="the-objects-glossary"></a>O glossário `objects`

Tudo que o jogo precisa localizar é definido aqui uma vez: `alias -> {"id": ..., "kind": ...}`. Depois, as etapas usam `"$alias"`.

```json
"objects": {
  "raider1": {"id": "GSPG01Ref", "kind": "actor"},
  "teddyRef": {"id": "VMS13TeddyBearRef", "kind": "thing", "base": "VMS13TeddyBear"},
  "quest": {"id": "VCG02", "kind": "state"}
}
```

`id` é qualquer string compreendida pelo adaptador: identificador de editor, identificador de formulário, caminho em uma cena, nome. O executor nunca analisa seu conteúdo. `kind` é um destes valores:

| kind | o que representa | usado por |
|---|---|---|
| `actor` | personagem ou criatura no mundo | kill, revive, owner, dead, stat |
| `thing` | objeto colocado no mundo: porta, contêiner, interruptor, marcador, item no mundo | activate, lock, move target, locked |
| `item` | tipo de item que pode estar em um inventário | give, take, item_count |
| `base` | tipo que pode ser criado | spawn, count |
| `place` | área ou célula | in_area, move target |
| `state` | missão, indicador de história ou variável de script | set_state, state, state_reached |

`base` (opcional, em `thing`): identificador do tipo de item recebido ao coletar esse objeto. O planejador de saltos o usa para saber que uma coleta altera os inventários dos jogadores.

A palavra `player` é incorporada. Significa o jogador da instância em que a etapa é executada e é permitida nos campos que a listam.

## <a id="steps"></a>Etapas

Cada etapa tem `id` (`lower_snake_case`, único) e `op`. Chaves opcionais em qualquer etapa:

| chave | significado |
|---|---|
| `on` | `host` (padrão para ações), `guest` (todos menos o host), `all` (padrão para verificações) ou índice de jogador |
| `parallel` | `true` executa uma etapa `all` em todos os jogadores ao mesmo tempo (threads). Use para condições de corrida |
| `note` | texto livre |
| `needs` | nomes de capacidades extras exigidas do adaptador |
| `dirties` | lista de `$alias` alterados pela etapa no mundo. Consulte "Salte para um cenário, não percorra o jogo" |

Operações e seus campos (`?` significa opcional):

| op | campos |
|---|---|
| `set_state` | `key` (estado), `value` |
| `move` | `who` (actor, thing, player), `to` (thing, place, actor) |
| `spawn` | `base`, `at` (thing, place, actor, player), `count?` |
| `give`, `take` | `who`, `item`, `count` (pelo menos 1) |
| `kill`, `revive` | `ref` (actor) |
| `enable`, `disable`, `activate` | `ref` (actor ou thing) |
| `lock` | `ref` (thing), `level` |
| `unlock` | `ref` (thing) |
| `wait` | `seconds` (0 a 120) |
| `save`, `load` | `name` |
| `leave`, `join` | nenhum: este jogador sai da sessão cooperativa ou volta a entrar |
| `action` | `name`, `args?` (objeto; valores `$alias` são resolvidos). Qualquer ação específica do jogo: viagem rápida, escolha de diálogo, resposta de consentimento |
| `check` | `kind` e os campos desse tipo, abaixo |

## <a id="checks"></a>Verificações

`{"op": "check", "kind": ..., <fields>, "value": N, "cmp": "==", "agg": null, "tol": 0, "timeout": 5}`

| kind | campos | leitura |
|---|---|---|
| `state` | `key` | valor atual do estado |
| `state_reached` | `key`, `at` | 1 se o estado já atingiu `at` |
| `item_count` | `who`, `item` | quantidade em posse do detentor |
| `dead`, `disabled`, `locked` | `ref` | 1 ou 0 |
| `in_area` | `ref`, `place` | 1 ou 0 |
| `distance` | `a`, `b` | unidades entre duas coisas |
| `stat` | `ref`, `stat` | valor de ator, como vida |
| `follower` | `ref` | 1 se o ator segue o jogador |
| `count` | `base` | objetos ativos daquela base |
| `owner` | `ref` | qual jogador controla (simula) o objeto |
| `value` | `query`, `args?` | número que o adaptador pode ler pelo nome |

* `cmp` aceita `==`, `!=`, `<`, `<=`, `>`, `>=` ou `same`. `same` significa que todos os jogadores informam o mesmo número, sem precisar conhecê-lo.
* `value` é um número. Use 1 e 0 para verdadeiro e falso.
* `agg` é `sum`, `min` ou `max` dos jogadores nos quais a verificação foi executada. `"agg": "sum", "value": 1` em `item_count` significa que existe exatamente uma cópia no total, detectando duplicação e perda.
* `tol` é a diferença permitida para `==` e `same`.
* `timeout` (segundos, padrão 5, máximo 120): o executor consulta até a condição ser satisfeita ou o tempo terminar. Inclua a espera na verificação, em vez de acrescentar uma etapa `wait`.

## <a id="jump-to-a-scenario-not-through-the-game"></a>Salte para um cenário, não percorra o jogo

`Runner.jump()` leva todas as instâncias ao estado inicial. Só recarrega `start.save` quando necessário:

* nada está carregado naquela instância (um jogo reiniciado conta como vazio);
* outro salvamento está carregado;
* o cenário anterior falhou ou apresentou erro;
* este cenário define `start.reload`;
* o cenário anterior alterou algo usado por este ou algo que não conseguiu nomear.

Caso contrário, o salto ocorre sem recarregar: o adaptador redefine as chaves de estado do cenário (e tudo que o cenário anterior definiu), e então as etapas `setup` são executadas.

As alterações persistentes de um cenário são calculadas pelas etapas: criação, movimento de objetos não jogadores, mortes, ativações de estado, travas, interações (e os tipos de itens fornecidos), `give` e `take` (no jogador: aquele item em seu inventário). Três operações não podem ser nomeadas e forçam recarregamento para o cenário seguinte, representadas por `*`: `load`, `action` e `set_state` sem lista `dirties`. Quando uma mudança de estado não pode afetar o mundo, escreva `"dirties": []` para manter o próximo salto sem recarregar. Quando altera objetos nomeados, liste-os: `"dirties": ["$gate", "$raider1"]`.

`python -I tools/scenarios/scen.py plan NAME --prev OTHER` exibe a decisão sem um jogo.

## <a id="capabilities"></a>Capacidades

Cada etapa exige uma capacidade do adaptador: `op:<op>`, `check:<kind>` ou `action:<name>` (além de sua própria lista `needs`). Um adaptador que retorna um conjunto em `capabilities()` fica limitado a ele. Uma etapa sem a capacidade necessária é informada como `blocked`, nunca `pass`; todas as etapas posteriores também são `blocked`, fazendo o cenário terminar como `partial`. Um adaptador que retorna `None` declara suportar tudo.

## <a id="validation"></a>Validação

`scenlib.validate(scenario, name=None, hooks=())` independe do jogo. Rejeita: `schema` incorreto, nome inválido, ausência de `title`, `description` ou `start.save`, objeto sem `id` ou com `kind` desconhecido, alias desconhecido em qualquer lugar (etapas, `reset`, `dirties`, `refs`, argumentos de `action`), objeto de tipo errado para um campo, `player` onde não é permitido, operações e tipos de verificação desconhecidos, campos ausentes ou inesperados, tipos incorretos, identificadores de etapa duplicados, `on` inválido, verificação sem `value` (ou `cmp: same`), `cmp` ou `agg` inválido, tempo limite fora do intervalo e cenário sem verificação.

`hooks` são funções `f(scenario) -> [error strings]`. Use uma para conferir identificadores nos dados do jogo, por exemplo: este identificador de editor existe no dump e tem o tipo de registro correto. Os exemplos distribuídos não precisam delas.

Para a verificação comum de existência de cada identificador com o tipo declarado pelo cenário, use `scenlib.index_hook(index)`, em que `index` é `{"<id>": "<kind>"}` (ou `scenlib.DataIndex`). `Runner.run` a adiciona automaticamente quando `data_index()` do adaptador retorna um índice. Ela verifica `id` e `base` de todos os objetos em `objects`, nomeia as etapas que os usam (incluindo configuração) e informa o identificador conhecido mais próximo. `scen.py validate --index FILE` e `--adapter pkg.mod:factory` a executam sem um jogo. Também é rejeitado `start.prepared` que não seja booleano.
