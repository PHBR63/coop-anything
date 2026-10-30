# <a id="example-the-inspector-on-a-fallout-new-vegas-co-op-project"></a>Exemplo: o inspetor em um projeto cooperativo de Fallout: New Vegas

O [fnv-coop](https://github.com/cranebeaker/fnv-coop) (commit e85460f) exibia estas linhas para cada cópia em execução. [fnv_fields.json](fnv_fields.json) contém essa tabela como uma lista de campos. O inspetor não depende dela;
ela mostra como os métodos e expressões de um jogo se integram.

## <a id="endpoints"></a>Endpoints

Cada cópia disponibilizava a ponte em um pipe, `pipe://nvcoop-<instance>`:

```
python -I tools/inspect/inspect_live.py --fields tools/inspect/examples/fnv/fnv_fields.json \
    --endpoint host=pipe://nvcoop-0 --endpoint client=pipe://nvcoop-1
```

## <a id="where-the-rows-come-from"></a>De onde vêm as linhas

| Linha | Fonte |
|---|---|
| role, lastSeq, acks, allSynced, digest, mismatches | método `coop.status` do plugin: `role`, `lastSeq`, `host.peers[{slot, acked, joined}]`, `host.allSynced`, `desyncs.digests{ok, mismatch, repairs}` |
| menu, msg queue | método `bot.menu` do módulo de bots: `kind`, `msgCount` |
| boxes | `ui.status`, `recentBoxes[{seq, script, text}]` |
| position, cell | `ref.info` para a referência do jogador `FalloutNV.esm:14` (`x`, `y`, `z`, `cell`) |
| weapon drawn, equipped, health | expressões de console `player.IsWeaponOut`, `player.GetEquippedObject 5` e `player.GetAV Health` pelo `eval` da ponte |

O original também exibia um bloco para uma referência escolhida (distância, saúde, responsável) ao passar `--ref`. Em uma lista de campos, isso corresponde a um campo `call` com `params` definido para essa referência, por exemplo `{"label": "target owner", "source": "call", "method": "coop.owner", "params": {"ref": "FalloutNV.esm:104C70"}, "path": "owner"}`.
`eval_allow` contém a primeira palavra completa de cada expressão (`player.isweaponout`, ...). Todos os métodos em `read_methods` são apenas de leitura. A linha `msg queue` aqui usa o `msgCount` bruto; o original subtraía o índice da caixa exibida na tela.

## <a id="problems-it-names"></a>Problemas identificados

Menu aberto, caixas de mensagem na fila, nenhum item equipado, host informando que nem todos os clientes estão sincronizados, divergência de digest e cópias com valores diferentes de `lastSeq`.
