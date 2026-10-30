# <a id="multi-agent-workflows-many-cheap-workers-one-careful-lead"></a>Fluxos com vários agentes: muitos executores econômicos, um coordenador cuidadoso

O trabalho cooperativo se divide naturalmente: um agente por auditoria de subsistema, por bug, por teste de fase ou por parte da pesquisa. O padrão que funcionou nos nossos projetos é um coordenador no modelo mais capaz, responsável por planejar, verificar e integrar, e agentes executores em um modelo mais barato e rápido (usamos Claude Sonnet), responsáveis por tarefas delimitadas.

## <a id="the-pattern"></a>O padrão

1. **Comece distribuindo tarefas somente de leitura.** Um executor por subsistema ou bug, somente com leitura, retornando descobertas com arquivo e linha, como um jogador encontra o problema e grau de confiança.
2. **O coordenador verifica as afirmações.** Cerca de uma a cada seis descobertas estava errada na auditoria de Deus Ex. Nunca corrija a partir de uma afirmação não verificada.
3. **Implemente com isolamento.** Cada executor recebe sua própria cópia do pacote de correções, instalação de testes, porta de rede e logs. Estado compartilhado (arquivos, portas, nomes de pipes, janela do jogo) causa interferência. Scripts de inicialização só encerram processos sob sua própria pasta.
4. **Integre depois que os testes passarem.** Executores não fazem commits na árvore principal. O coordenador integra, renomeia conflitos (dois executores criaram classes com o mesmo nome), recompila e executa novamente a suíte completa.
5. **Revisão adversarial.** Um executor cético revisa cada alteração e pode revertê-la.
6. **Considere os limites da máquina.** Cada executor com clientes do jogo consome memória. Em um PC comum, execute um por vez quando os testes forem pesados; pesquisa e leitura de código são tarefas leves.

Bons prompts para executores são autossuficientes: objetivo, caminho do ambiente de trabalho, comandos exatos para compilar e testar, regras (sem travessões na documentação, sem informações pessoais), o que retornar e o que não alterar.

## <a id="tool-by-tool"></a>Ferramenta por ferramenta

As chaves de configuração abaixo foram conferidas na documentação de cada ferramenta em outubro de 2026. As ferramentas mudam; consulte a documentação indicada se algo não funcionar.

### <a id="claude-code"></a>Claude Code

- Executores: a ferramenta Agent recebe o parâmetro `model` (`sonnet`, `opus`, `haiku`); outra opção é definir agentes como arquivos Markdown com front matter YAML em `.claude/agents/`, usando `model: sonnet`. O front matter também aceita `tools`, `isolation: worktree` (worktree Git própria) e `background: true`.
- Um modelo para todos os executores: `CLAUDE_CODE_SUBAGENT_MODEL=sonnet` (mais `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1`) no bloco `env` de `settings.json`.
- Concorrência: `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (padrão 20), `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` (padrão 3).
- Testes longos em segundo plano podem ser interrompidos quando há pouca memória; iniciar Claude Code com `CLAUDE_CODE_DISABLE_BG_SHELL_PRESSURE_REAP=1` desativa esse comportamento.
- Documentação: https://code.claude.com/docs/en/sub-agents

### <a id="openai-codex-cli"></a>OpenAI Codex CLI

- Aumente o número de agentes em paralelo em `config.toml`:
  ```toml
  [agents]
  max_concurrent_threads_per_session = 12   # older versions: max_threads (default was 6)
  default_subagent_model = "<cheaper model>"
  ```
- Agentes personalizados: arquivos TOML em `.codex/agents/` com `name`, `description`, `developer_instructions` e, opcionalmente, `model`.
- Inicie pedindo: "crie um agente por bug, aguarde todos e retorne uma tabela".
- Documentação: referência de configuração do Codex, seção `agents`.

### <a id="gemini-cli"></a>Gemini CLI

- Subagentes em Markdown em `.gemini/agents/`, com `model`, `tools`, `max_turns`. Não há configuração de concorrência documentada; subagentes não podem criar subagentes.
- Para ler as regras deste repositório, defina o nome do arquivo de contexto como `AGENTS.md` em `.gemini/settings.json`.

### <a id="cursor"></a>Cursor

- Agentes em segundo plano (na nuvem) executam em paralelo pelo editor, pela web ou pela API. Lê `AGENTS.md`.

### <a id="opencode"></a>OpenCode

- Agentes em `.opencode/agents/` ou `opencode.json` com `mode: subagent` e um `model`.

### <a id="aider"></a>Aider

- Sem agentes paralelos nativos: execute vários processos do aider em worktrees separadas. Use `--read AGENTS.md` para carregar as regras.

## <a id="workflows-scripted-orchestration"></a>Fluxos de trabalho (orquestração por scripts)

Algumas ferramentas executam um script que inicia dezenas de agentes de forma determinística (sequências como "revise cada subsistema e depois verifique cada descoberta"). Use isso em grandes auditorias e varreduras, por exemplo, um agente por fase em um teste de campanha completa. Limite o tamanho ao que a máquina e seu orçamento suportarem e mantenha a verificação do resultado integrado pelo coordenador.
