# <a id="example-the-bridge-in-a-fallout-new-vegas-co-op-project"></a>Exemplo: a ponte em um projeto cooperativo de Fallout: New Vegas

Esta página lista as partes da ponte específicas de [fnv-coop](https://github.com/cranebeaker/fnv-coop) (commit e85460f), um mod de história compartilhada para Fallout: New Vegas. O cliente e o servidor na pasta superior não precisam dessas particularidades. O exemplo mostra o que o jogo coloca no adaptador e nos métodos personalizados.

O código original está em `tools/runner/nvbridge.py` (cliente) e `plugin/bridge/` (servidor interno ao jogo) naquele repositório. O servidor era um plugin carregado pela extensão de scripts do jogo, e `Pump()` era chamado pelo hook do plugin a cada quadro.

## <a id="endpoints"></a>Pontos de conexão

O original abria um pipe por cópia do jogo: `\\.\pipe\nvcoop-<instance>`, com números de instância 0, 1, ... para as cópias em um PC. Nesta ponte, isso corresponde a `pipe://nvcoop-0`, `pipe://nvcoop-1` (defina `Options::pipeName = "nvcoop-" + instance`).

## <a id="method-names"></a>Nomes dos métodos

| fnv-coop | esta ponte | Observação |
|---|---|---|
| `bridge.version` | `version` | `{gitHash, dirty, buildTime, protocol, pid}` passou a ser `{protocol, game, build, server, pid}`. Coloque o hash Git em `Options::build`. |
| `loadSave` | `load` | O original concluía quando a extensão de scripts disparava a mensagem de pós-carregamento; esse hook chama `NotifyLoaded()`. |
| `saveGame` | `save` | O menu de salvamento do motor exige um nome começando com `autosave`. O adaptador recusava nomes reservados, caracteres incomuns e arquivos existentes, a menos que `overwrite` estivesse definido; usava o código -32012 para um salvamento existente. A mensagem de salvamento chama `NotifySaved(path)`. |
| `exec {cmd, ref}` | `exec {cmd, ref}` | Mesmo formato. |
| `eval` (no cliente) | `eval {expr, ref}` | O cliente original enviava a linha de console `printc "NVCOOP_EVAL=%g" (<expr>)` por `exec` e analisava o número. Nesta ponte, `Eval` do adaptador faz isso. |
| `waitFor` | `waitFor` | Mesmos parâmetros. O original consultava `printc` da mesma forma para `expr`. |
| `state` | `state` | O original retornava uma captura de estado montada por seu próprio módulo, opcionalmente em um arquivo. |
| `lock.acquire`, `lock.renew`, `lock.release`, `lock.info` | não incluídos | Uma concessão temporária que permitia a várias linhas de teste compartilhar uma cópia do jogo. Adicione como métodos personalizados se precisar; reserve os códigos -32010 e -32011 para eles. |
| `plugins`, `quit` | não incluídos | Registre como métodos personalizados se desejar. |
| `coop.status`, `coop.owner`, `ui.status`, `bot.menu`, `bot.menu.press`, `bot.fire`, `ref.info`, `world.query`, ... | métodos personalizados | Registrados pelo mod e pelo módulo de bots, não pela ponte. [tools/inspect/examples/fnv](../../../inspect/examples/fnv/README.md) lista os métodos lidos pelo inspetor. |

## <a id="console-quirks-the-adapter-handles"></a>Particularidades do console tratadas pelo adaptador

- O console do jogo não aceita `<hexFormID>.Command`. Uma linha para qualquer referência diferente do jogador identifica a referência em `ref`, como `"Plugin.esm:HEX"` ou identificador de tempo de execução, e o adaptador executa a linha usando essa referência como a referência chamadora do console. Um `ref` sem referência carregada correspondente é um erro (o original usava -32013). Linhas `player.X` não precisam de `ref`.
- Verificações de missões e atores usavam expressões como `GetStage <hex FormID>`: identificadores de editor não eram resolvidos pelo analisador do console, então os testes usam FormIDs hexadecimais.
- Um caminho fornecido a `state` ou `screenshot` é resolvido pelo processo do jogo, cujo diretório de trabalho é a pasta do jogo; por isso, os auxiliares Python enviam caminhos absolutos. `Bridge.state_to_file` e `Bridge.screenshot` fazem isso.

## <a id="shape-of-the-adapter"></a>Estrutura do adaptador

```cpp
class FnvAdapter : public coopbridge::Adapter {
    Capabilities capabilities() const override { /* exec, eval, state, save, load, screenshot */ }
    ExecResult Exec(const std::string& line, const std::string& ref) override;   // console line, or with `ref` as the calling reference
    json::Value Eval(const std::string& expr, const std::string& ref) override;  // runs printc "NVCOOP_EVAL=%g" (<expr>) and parses the number
    // Load/Save issue the engine call; the script extender's PostLoadGame / SaveGame messages call NotifyLoaded / NotifySaved.
};
```

Este é um esboço de onde entra o código original, não um segundo plugin.
