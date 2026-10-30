# <a id="the-co-op-anything-mcp-server"></a>O servidor MCP do Co-op Anything

`tools/mcp/coop_mcp.py` fornece a qualquer agente compatível com MCP o conhecimento compartilhado deste repositório e algumas ferramentas locais de análise, somente de leitura. Ele precisa de Python 3.9+ e PyYAML (`pip install pyyaml`), sem outras dependências. Lê o seu clone, então `git pull` o atualiza.

| Ferramenta | O que faz |
|---|---|
| `search_directory` | Pesquisa o diretório de projetos cooperativos e lacunas por jogo, motor, estado ou nível de QA, incluindo as fontes de cada entrada para conferir as afirmações |
| `detect_engine` | Examina a pasta de instalação de um jogo e identifica o motor por assinaturas de arquivos (cabeçalhos de arquivos contêiner quando há extensões compartilhadas), com evidências, ferramentas de hooks, alertas sobre sistemas antitrapaça e projetos cooperativos do mesmo motor |
| `game_identity` | Obtém SHA-256, arquitetura, detalhes PE e recurso de versão do executável, além do identificador de aplicativo e de compilação do Steam nas instalações Steam, para registrar a compilação exata |
| `list_docs`, `read_playbook`, `get_skill`, `get_game` | Lê os guias, as skills dos agentes e os relatos técnicos dos jogos |
| `get_test_tool` | Lê o README de uma ferramenta de teste de sincronização em `tools/` (simulador de caos, gravador de eventos, fuzzer, bots e outras) |
| `validate_entry` | Verifica uma entrada do diretório em relação ao esquema antes de contribuir |

Combine-o com um MCP de engenharia reversa, como o [REA](https://github.com/morluto/rea), para trabalhar com binários: o Co-op Anything sabe o que fazer; o REA examina o interior do jogo.

## <a id="setup"></a>Configuração

**Claude Code:** abra este repositório; o `.mcp.json` do projeto oferece o servidor automaticamente. De qualquer outro local (`-s user` o disponibiliza em todas as pastas, não apenas na atual):
```
claude mcp add -s user coop-anything -- python <path to clone>/tools/mcp/coop_mcp.py
```

As skills `coop-*` ficam em `.claude/skills/` deste repositório; portanto, o Claude Code só as vê quando está executando dentro do clone. Para usá-las ao trabalhar na pasta de um jogo, crie links para elas na pasta de skills do usuário; assim, `git pull` também as atualiza. Os caminhos dentro das skills (`local/`, `playbook/`, `games/`) continuam relativos ao clone. `triage-contributions` é a skill dos mantenedores e foi excluída propositalmente.

Windows, no `cmd` (uma junção de diretório não exige privilégios de administrador):
```
for /d %s in ("<path to clone>\.claude\skills\coop-*") do mklink /J "%USERPROFILE%\.claude\skills\%~nxs" "%s"
```
Linux e macOS:
```
for s in <path to clone>/.claude/skills/coop-*; do ln -s "$s" ~/.claude/skills/; done
```

**Codex** (`~/.codex/config.toml`):
```toml
[mcp_servers.coop-anything]
command = "python"
args = ["<path to clone>/tools/mcp/coop_mcp.py"]
```

**Gemini CLI** (`.gemini/settings.json`) e **Cursor** (`.cursor/mcp.json`):
```json
{ "mcpServers": { "coop-anything": { "command": "python", "args": ["<path to clone>/tools/mcp/coop_mcp.py"] } } }
```

Use `python3` em vez de `python` no Linux e no macOS.

Após alterar o servidor, execute seus testes: `python -m unittest tools/mcp/test_coop_mcp.py`.

## <a id="ask-your-agent"></a>Peça ao seu agente

```
Use coop-anything: detect the engine of my <game> install at <folder>, check what co-op work
exists for it and for its engine, and tell me which path (revive or build from zero) fits.
```

O pedido acima solicita a identificação do motor da instalação, a busca de trabalhos cooperativos para o jogo e o motor e a indicação do caminho adequado: retomar um projeto ou criar do zero.
