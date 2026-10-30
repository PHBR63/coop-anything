<a id="directory-entry-schema"></a>
# Esquema das entradas do diretório

`data/directory.yaml` é uma lista de entradas. Uma entrada equivale a um projeto cooperativo para um jogo. Um jogo pode ter várias entradas (mods concorrentes ou sucessivos). `tools/build_directory.py` gera `DIRECTORY.md` a partir dessa lista; edite o YAML, nunca a tabela.

```yaml
- game: Deus Ex                       # nome de exibição do jogo base
  year: 2000                          # ano de lançamento do jogo base
  engine: Unreal Engine 1             # família do motor; consulte playbook/engine-families.md
  project: HX                         # nome do mod / projeto
  url: https://example.org/hx         # página principal (repositório, Nexus, ModDB, site)
  other_urls: []                      # cópias alternativas, convites Discord, forks
  kind: mod                           # mod | fork | decomp-port | official | emulator-netplay | framework
  status: alpha                       # playable | partial | alpha | prototype | abandoned | official
  coop_scope:                         # o que é compartilhado, somente com confirmação de fonte
    players_visible: yes              # os jogadores conseguem ver uns aos outros
    story: yes                        # yes | partial | no | unknown
    enemies: yes
    world_state: partial
    items: per-player
  players: "2-8"                      # conforme declarado pelo projeto
  networking: direct-ip               # direct-ip | vpn-needed | steam-relay | dedicated-server | hosted-relay | lan | unknown
  open_source: no                     # yes | no | partial (licença em notes, se conhecida)
  last_activity: 2019-06              # YYYY-MM da última versão/commit confirmados
  qa: community-reports               # consulte os níveis de QA abaixo
  notes: Última compilação oficial 0.9.89.4. Correções de retomada em games/deus-ex.
  sources:                            # toda afirmação acima precisa de uma destas fontes
    - https://example.org/source
  checked: 2026-10-16                 # data da última verificação da entrada
  up_for_adoption: false              # opcional; true = o autor parou e quer alguém para continuar
  made_with_coop_anything: false      # opcional; true = criado ou retomado com Co-op Anything (o site sinaliza)
```

<a id="qa-levels-the-flag-that-matters-most"></a>
## Níveis de QA (o indicador mais importante)

| qa | Significado |
|---|---|
| `none` | Ninguém relatou testes, ou só existem afirmações do autor. |
| `community-reports` | Jogadores relatam partidas (fórum, Steam, Discord, Reddit), sem testes estruturados. |
| `automated` | Uma estrutura de teste por scripts controla clientes reais do jogo e verifica o estado compartilhado (consulte playbook/automated-qa.md). |
| `verified-playthrough` | Uma campanha inteira foi concluída em modo cooperativo e documentada com os problemas conhecidos. |

Lacunas (nenhum projeto encontrado) usam `kind: gap`, `project: "(none found)"`, `status: none`, `url` vazio e uma lista `searched:` com os locais e datas pesquisados (por exemplo: "GitHub, Nexus, ModDB, fóruns Steam por busca na web, 2026-10-16; Reddit não consultado"). Nesse caso, `sources` pode ficar vazio.

Defina `up_for_adoption: true` quando o autor tiver parado de trabalhar no projeto e aceitar que outra pessoa continue. Mantenha `status` fiel ao progresso alcançado; o indicador apenas informa a necessidade de um novo responsável. Essas entradas também aparecem em uma seção própria de `DIRECTORY.md`.

Regras: não adivinhe. O desconhecido é `unknown`. Toda entrada precisa de pelo menos uma URL de fonte e uma data em `checked`.
