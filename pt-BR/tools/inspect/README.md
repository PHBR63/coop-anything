# <a id="inspect-a-read-only-live-table-of-your-game-copies"></a>inspect: tabela ao vivo e somente de leitura das cópias do seu jogo

Quando um teste cooperativo falha, a pergunta mais imediata é "o que cada cópia está fazendo agora?". Esta ferramenta responde: uma coluna por cópia em execução, uma linha por campo (menu, vida, posição, responsável pelo alvo, contadores de sincronização, dessincronizações recentes, caixas de mensagem recentes e tudo o que o jogo informar), com atualização se solicitada. Abaixo, lista os problemas identificáveis em linguagem simples: caixa de mensagem aberta, cópia atrasada em relação ao host, contador de divergência que mudou.

Ela só observa. Lê as cópias pela ponte interna ao jogo ([tools/bridge](../bridge/README.md)), através de um intermediário que recusa qualquer método capaz de alterar o jogo; assim, uma caixa de mensagem aberta continua aberta, e uma etapa de missão permanece onde está.

Python 3.8 ou posterior, somente biblioteca padrão. Exige um jogo que execute o servidor da ponte (ou as cópias simuladas da demonstração).

## <a id="quick-start-see-it-on-fake-copies"></a>Primeiros passos: observe cópias simuladas

```
python -I tools/inspect/demo.py
```

Inicia host e cliente simulados e uma terceira cópia que não está em execução, atualiza a tabela cinco vezes e, após a segunda atualização, faz o cliente abrir uma caixa de mensagem, perder vida e deixar de receber uma atualização de sincronização. A tabela é produzida pelo mesmo código da ferramenta real, a partir de [examples/demo_fields.json](examples/demo_fields.json).

## <a id="quick-start-your-game"></a>Primeiros passos: seu jogo

1. Execute o servidor da ponte no jogo ([tools/bridge](../bridge/README.md)) e faça-o escrever seu arquivo de endpoint, ou anote sua porta.
2. Escreva uma lista de campos (abaixo). Comece por `examples/demo_fields.json`.
3. Observe:

```
python -I tools/inspect/inspect_live.py --fields local/mygame_fields.json \
    --endpoint host=tcp://127.0.0.1:27990 --endpoint client=tcp://127.0.0.1:27991
python -I tools/inspect/inspect_live.py --fields local/mygame_fields.json --endpoint-file a=run/a.json --endpoint-file b=run/b.json --watch 1
python -I tools/inspect/inspect_live.py --fields local/mygame_fields.json --endpoint a=pipe://mygame-0 --json
```

`--watch SECONDS` atualiza até Ctrl-C (`--count N` para após N atualizações). `--json` exibe os valores brutos e a lista de problemas para um script. Código de saída 0 quando ao menos uma cópia respondeu, 2 quando nenhuma respondeu, 1 para argumentos inválidos. Uma cópia inacessível aparece em uma coluna informando isso; as outras colunas continuam visíveis. Uma cópia que volta é reconhecida na atualização seguinte.

## <a id="the-field-list"></a>A lista de campos

Um arquivo JSON por jogo. Chaves que começam com `_` são ignoradas.

```json
{
  "name": "mygame",
  "eval_allow": ["health"],
  "read_methods": ["sync.status"],
  "fields": [
    {"label": "menu",   "source": "state", "section": "menu", "path": "menu.kind"},
    {"label": "health", "source": "eval",  "expr": "health", "format": "{:g}"},
    {"label": "acks",   "source": "call",  "method": "sync.status", "path": "peers", "template": "slot {slot}: acked {acked}"},
    {"label": "boxes",  "source": "events", "types": ["ui.messagebox"], "last": 3, "template": "#{seq} {text}"}
  ],
  "problems": [
    {"field": "menu", "op": "!=", "value": "none", "say": "{copy}: the {value} menu is open"},
    {"differs": "lastSeq", "say": "lastSeq differs between copies: {values}"}
  ]
}
```

| Chave | Significado |
|---|---|
| `eval_allow` | Primeiras palavras das expressões que o inspetor pode avaliar (sem distinção de maiúsculas). Um campo `eval` cuja expressão comece de outra forma aparece como `refused` e nunca é enviado. |
| `read_methods` | Métodos personalizados da ponte que o inspetor pode chamar. Só podem ler. `exec`, `save`, `load`, `screenshot`, `waitFor` e `quit` são recusados aqui, mesmo se listados. |
| `fields[].label` | Nome da linha. Único. As linhas aparecem na ordem da lista. |
| `fields[].source` | `ping` (resposta ao ping), `version`, `state` (método `state` da ponte, com `section` para ler apenas uma parte; todos os campos `state` compartilham uma solicitação), `eval` (`expr`, `ref` opcional), `events` (`types`: eventos recentes desses tipos, os últimos `last`), `call` (`method` de `read_methods`, `params` opcional). |
| `fields[].path` | Onde ler dentro da resposta: `a.b.0` percorre chaves e posições de listas. Vazio significa a resposta inteira. Um caminho inexistente aparece como `n/a`. |
| `fields[].format` | Texto de formatação Python para um valor. Uma lista preenche `{0} {1}`, um dicionário preenche `{name}`, um número pode usar `{:.0f}` ou `{:08X}`. |
| `fields[].template` | Para uma lista (ou eventos): uma linha por item, preenchida pelas chaves do item. Eventos também têm `{seq}` e `{type}`. `empty` é o texto para uma lista vazia (padrão `none`). |
| `problems[]` | Regras. `{"field", "op", "value", "say"}` dispara para cada cópia cujo valor satisfaça o teste (`op`: `==`, `!=`, `<`, `<=`, `>`, `>=`, `nonempty`, `empty`); `say` pode usar `{copy}`, `{field}`, `{value}`. `{"differs": "field", "say"}` dispara quando as cópias discordam; `say` pode usar `{values}`. |

Um método ausente no jogo (`-32601`) aparece como `n/a` na linha e não é um problema. Qualquer outro erro de método aparece como `error: ...` e entra na lista de problemas.

## <a id="what-it-never-does"></a>O que nunca faz

- Enviar algo capaz de alterar o jogo. Toda solicitação passa por `ReadOnlyBridge`: um conjunto fixo de métodos de consulta (`ping`, `version`, `methods`, `events`, `state`, `eval`), mais `read_methods` da lista de campos, e nada além disso. `eval` somente para expressões em `eval_allow`.
- Fechar uma caixa de mensagem. Para isso, use a etapa de dispensar mensagens do próprio executor.
- Ocultar uma cópia fora do ar. Ela aparece como inacessível e como problema.

## <a id="how-it-is-tested"></a>Como é testado

```
python -I tools/inspect/run_tests.py       # prints ALL OK only if every check passes and every twin is caught
```

23 verificações e 11 variantes de mutação no momento da escrita; cerca de meio minuto. Os "jogos" são cópias simuladas de `tools/bridge/fake_game.py` em portas loopback. Nenhum jogo real é iniciado.

- **Leitura:** toda origem (ping, state, eval, método personalizado, eventos) é lida e formatada; cada atualização lê o jogo de novo e mostra os valores alterados; eventos são lidos a partir de um cursor e listados uma vez; método ausente é `n/a`; caminho ausente é `n/a`; método que falha mostra a mensagem enquanto as outras linhas continuam visíveis; cópia inacessível continua como coluna enquanto as outras aparecem; cópia que desaparece e volta é lida novamente.
- **Somente leitura:** o intermediário recusa `exec`, `save`, `load`, `screenshot`, `waitFor`, `quit` e métodos desconhecidos, mantendo intacto o estado simulado; expressão fora da lista permitida é recusada e nunca enviada; uma atualização completa só chama `eval` e `state` na simulação; uma lista de campos não pode indicar método de escrita.
- **Listas de campos:** nove tipos de listas inválidas são recusados com uma explicação; as listas de exemplo distribuídas carregam.
- **Problemas e tabela:** um par saudável produz `problems: none`; cada regra dispara apenas para sua cópia; colunas ficam alinhadas e células longas quebram linha; a tabela informa quando nada responde.
- **Linha de comando e demonstração:** saída em tabela e JSON, códigos de saída, arquivos de endpoint, `--watch --count`, argumentos inválidos e saída da demonstração.
- **Variantes de mutação:** dados obsoletos devolvidos em uma atualização, métodos de escrita atravessando o intermediário, lista de permissões eval ignorada, lista de campos autorizando escrita, uma cópia morta quebrando a tabela, método ausente exibido como erro, cursor de eventos não preservado, conexão morta nunca reaberta, regras que nunca disparam, regra "differs" desativada e colunas sem preenchimento.

## <a id="files"></a>Arquivos

`inspect_live.py`, `demo.py`, `examples/demo_fields.json`, `examples/fnv/` (`README.md`, `fnv_fields.json`), `test_inspect.py`, `run_tests.py`.

## <a id="generalised-from-fnv-coop-commit-e85460f-githubcomcranebeakerfnv-coop"></a>Generalizado a partir do commit e85460f de fnv-coop (github.com/cranebeaker/fnv-coop)

Generalizado a partir de `tools/bots/inspect_live.py` no [fnv-coop](https://github.com/cranebeaker/fnv-coop), commit e85460f. O que mudou:

- As linhas não são mais fixas no código. O original tinha linhas fixas para menu, arma, vida, posição, bloco de referência e estado cooperativo; agora são uma lista de campos por jogo, lida pelos métodos `ping`, `state`, `eval`, `events` e métodos personalizados somente de leitura da ponte.
- A proteção de somente leitura tornou-se regra da ferramenta: conjunto fixo de métodos de consulta mais `read_methods` da lista de campos, uma lista `eval_allow` de nomes de expressões e recusa incondicional dos métodos de escrita.
- As regras de problemas passaram do código para a lista de campos, com uma regra para "as cópias diferem".
- Cópias são encontradas por endpoint (TCP ou pipe) ou arquivo de endpoint, em vez de número de instância; `--watch` atualiza, e uma cópia que retorna é reconectada.
- Os testes usam cópias simuladas em loopback e variantes de mutação feitas fora do código.

A lista de campos de Fallout: New Vegas fica em [examples/fnv](examples/fnv/README.md).
