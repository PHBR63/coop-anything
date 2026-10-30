# <a id="animcheck-animation-and-pose-checker"></a>animcheck: verificador de animações e poses

Verifica se um mod cooperativo mostra outros jogadores (e NPCs compartilhados) como realmente são: mesma animação, pose, arma e direção, sem deslizamento, pose em T ou flutuação. Funciona com **qualquer jogo**. Nunca altera o jogo: lê fluxos JSON-lines escritos por uma pequena sonda interna, executa verificações e exibe PASS ou FAIL, além de um relatório HTML. Python 3, somente biblioteca padrão (testes executados com Python 3.11).

O que você fornece por jogo:

1. Uma **sonda** no jogo que escreva o fluxo (formato: [FORMAT.md](FORMAT.md)).
2. Um **perfil**, pequeno arquivo JSON com os nomes dos ossos e a tabela de grupos de animação do jogo (exemplo: [examples/fnv/profile.json](examples/fnv/profile.json)).

O guia prático para agentes é [playbook/animation-sync-checks.md](../../playbook/animation-sync-checks.md).

## <a id="try-it-in-one-minute"></a>Experimente em um minuto

```
python -I tools/animcheck/cli.py demo --out out/animdemo
```

Escreve dois fluxos sintéticos (host e cliente que mostra o representante do jogador host com defeitos inseridos), analisa, exibe as descobertas e grava `out/animdemo/report.html`. Encerra com código 0; a análise da demonstração relata FAIL de propósito.

## <a id="what-it-checks"></a>O que verifica

**Em uma máquina** (fluxo próprio de cada ator, no jogador real e no representante):

| Descoberta | Significado |
|---|---|
| `sliding` | Move-se sem animação de locomoção ou mais rápido/lento que a animação de caminhada/corrida permite. |
| `tpose` | Nenhuma animação em execução ou ambos os braços esticados para os lados (pose de vinculação). |
| `floating`, `sinking` | Altura afastada do solo rastreado, sem salto, queda, nado, derrubada ou ragdoll que a explique. |
| `jitter` | Posição alterna para frente e para trás entre amostras. |
| `rubberband` | Salto repentino de posição, registrado quando retorna bruscamente. |
| `stuck` | Deveria caminhar (você informa quando), mas permanece em animação ociosa. |
| `deathpose` | Animação de vivo em ator morto, animação de morte em ator vivo ou ausência de animação de morte. |

**Entre máquinas** (responsável contra observador, considerando o atraso de interpolação do receptor):

| Contador | Significado |
|---|---|
| `pose_err_p50/p95/max` | Distância média entre ossos correspondentes após alinhamento da raiz, em unidades do mundo. |
| `pos_err_p95`, `facing_err_p95_deg` | Erro de posição e direção. |
| `group_mismatch_pct`, `group_mismatch_episodes` | O observador executa animações diferentes da responsável. |
| `wrong_weapon`, `wrong_aim`, `wrong_facing`, `stance_mismatch`, `dead_mismatch` | Episódios com mais de 400 ms de diferença nesse estado. Episódios menores são transições e não contam. |

Avatares (personagem próprio contra o representante do mesmo jogador em outra máquina) recebem as mesmas métricas em `avatar.*`, separadas das métricas de NPCs.

## <a id="the-probe-stream-in-short"></a>Resumo do fluxo da sonda

JSONL, uma amostra por linha, um arquivo por máquina. Cada amostra tem horário e lista de atores. Cada ator tem ID, posição, rotação (Z para cima) e, opcionalmente, animações em execução, posições dos ossos no espaço do mundo, arma e postura.

```json
{"machine":"host","t_ms":1250.0,"actors":[{"ref":"0x14","pos":[1000,2000,100],"rot":[0.2,0,1.57],
  "anim":{"seqs":[{"slot":0,"group":1,"state":1}]},"bones":{"pelvis":[1000,2000,140],"hand_l":[1000,1988,146]}}]}
```

A lista completa de campos, os dados lidos por cada verificação e o tratamento de várias máquinas estão em [FORMAT.md](FORMAT.md). A sonda de Fallout: New Vegas fica no repositório fnv-coop, em `plugin/animprobe` (https://github.com/cranebeaker/fnv-coop). Lê memória do motor, então permanece lá; serve de exemplo de sonda, e sua saída segue este formato.

## <a id="the-profile"></a>O perfil

Um JSON de perfil informa ao animcheck os nomes do jogo. Todas as chaves são opcionais.

```json
{
  "name": "mygame",
  "bones": {"root": "Hips", "left_upper_arm": "UpperArm_L", "left_hand": "Hand_L",
            "right_upper_arm": "UpperArm_R", "right_hand": "Hand_R"},
  "groups": ["Idle", "Walk", "Run", "Jump", "Death"],
  "categories": {"idle": ["Idle"], "walk": ["Walk"], "run": ["Run"], "jump": ["Jump"], "death": ["Death"]},
  "category_prefixes": {"attack": ["Attack"], "reload": ["Reload"]},
  "default_category": "misc",
  "angle_unit": "rad",
  "units_per_meter": 70.0,
  "move_flag_bits": {"sneak": 9, "swim": 11},
  "thresholds": {"slide_min_speed": 50.0}
}
```

- `bones`: nomes dos nós para as funções usadas pelo analisador: `root` (pelve ou quadris) e os quatro ossos dos braços.
- `groups`: tabela de grupos de animação. Lista (posição = ID) ou objeto `{"5": "Walk"}`. Se a sonda enviar nomes de texto como `group`, você pode omitir `groups` e listar os nomes em `categories`.
- `categories` e `category_prefixes`: a categoria de cada grupo. As categorias são `idle`, `walk`, `run`, `dodge`, `turn`, `aim`, `attack`, `reload`, `jam`, `equip`, `hit`, `death`, `jump`, `block`, `misc`. Entradas são nomes ou IDs de grupo; prefixos correspondem ao início do nome. Verificações de locomoção usam `walk`, `run` e `dodge`; a de suspensão no ar usa `jump`; as de morte usam `death`.
- Grupo desconhecido pelo perfil é `unknown` e aparece no relatório ("groups the profile does not know"). Complete a tabela até a lista ficar vazia; caso contrário, `sliding` pode disparar em animações desconhecidas pelo perfil.
- `angle_unit`: `rad` ou `deg`, para `rot`. `units_per_meter`: todos os limites de distância foram escritos para 70 unidades por metro e são escalados por `units_per_meter / 70`. `thresholds`: sobrescreve qualquer valor de `config.Thresholds`.
- `move_flag_bits`: opcional, números dos bits no inteiro `move_flags` que representam furtividade e natação. Sondas que enviam `stance.sneaking` e `stance.swimming` não precisam dele.

Confira um perfil com `python -I tools/animcheck/cli.py profile my.json`.

O mapeamento de Fallout: New Vegas fica em [examples/fnv/](examples/fnv): seus 245 grupos de animação e nomes dos ossos. Sem `--profile`, usa um pequeno perfil genérico (nomes de ossos como `pelvis`, `hand_l`).

## <a id="command-line"></a>Linha de comando

```
python -I tools/animcheck/cli.py analyze host.probe.jsonl client.probe.jsonl --profile my.json \
    --avatar "player=host:14>client:FF000A" --html report.html --json report.json \
    --assert "avatar.pose_err_p95<=12" --assert "glitches==0"
```

- Arquivos: `name=path` ou apenas um caminho; o primeiro arquivo é a responsável. Acrescente `--owner NAME` para escolher outra.
- `--avatar NAME=OWNERMACHINE:OWNERREF>OBSERVERMACHINE:OBSERVERREF`, referências em hexadecimal. Repita para vários jogadores.
- `--assert "<counter><op><number>"`, operadores `<= >= < > == !=`. Contador inexistente é falha, então erro de digitação não passa. Sem `--assert`, aplicam-se os padrões: `glitches==0`, `wrong_weapon==0`, `wrong_facing==0` e limite de erro de pose (`--pose-tol`, 12) quando há um par para comparar; com avatares, também os equivalentes `avatar.*`.
- `--expect-moving REF:T0-T1` informa que um ator deve caminhar entre dois instantes (ms no relógio do fluxo); ativa a verificação `stuck` para ele.
- `--suppress KIND:REF:T0-T1` ignora descobertas correspondentes, por exemplo, teletransporte deliberado (`*` para qualquer tipo ou ID).
- `--delay-ms`, `--latency-ms`: buffer de interpolação do receptor (100) e janela extra de latência (150).
- `--auto-offset`: estima a diferença entre fluxos que usam relógios diferentes.
- Código de saída 0 = PASS, 1 = FAIL, 2 = argumentos inválidos.

Colete de jogos em execução por TCP (consulte "Collector protocol" em FORMAT.md) e depois analise:

```
python -I tools/animcheck/cli.py collect --connect host=127.0.0.1:9100 --connect client=127.0.0.1:9101 \
    --seconds 10 --hz 20 --out out/run1
```

Pelo Python:

```python
from animcheck.analyze import analyze
from animcheck.counters import check
from animcheck.model import load_stream
from animcheck.profile import Profile

p = Profile.load("my.json")
streams = {"host": load_stream("host.probe.jsonl", profile=p), "client": load_stream("client.probe.jsonl", profile=p)}
report = analyze(streams, p.thresholds(), profile=p,
                 avatars=[{"name": "player", "owner": "host", "owner_ref": 0x14, "observer": "client", "observer_ref": 0xFF000A}])
assert not check(report, {"avatar.pose_err_p95": "<=12", "glitches": "==0"})
```

Primeiro acrescente `tools/` a `sys.path` para importar `animcheck`.

## <a id="html-report"></a>Relatório HTML

`--html report.html` escreve um arquivo autossuficiente (sem scripts ou arquivos externos, temas claro e escuro): linha PASS ou FAIL com as asserções que falharam, todos os contadores, grupos desconhecidos pelo perfil, tabela por par de máquinas, tabela de avatares e toda descoberta com máquina, tipo, ator, início, fim e motivo em uma linha. `--json` escreve os mesmos dados como `animcheck.report.v1`, com objeto `counters` plano para scripts.

## <a id="tuning"></a>Ajuste

Limites ficam em [config.py](config.py), em unidades do mundo (70 por metro) e milissegundos. São valores iniciais. Primeiro registre uma execução limpa em uma máquina (bot que caminha, corre, gira, salta e empunha arma), execute `analyze` e corrija o que for relatado: perfil (grupo desconhecido, osso errado) ou um limite em `thresholds` do perfil. Descobertas esperadas, como teletransporte por script, vão em `--suppress`. Só depois registre a execução em duas máquinas.

## <a id="how-it-is-tested"></a>Como é testado

Um comando na raiz do repositório:

```
python -I tools/animcheck/run_tests.py
```

Exibe `ALL OK` como última linha somente quando ambas as condições são verdadeiras:

1. A suíte unitária passa no código real (somente fluxos sintéticos de sondas; sem jogo ou rede além de loopback).
2. Toda **variante de mutação** é detectada. Uma variante é o mesmo código com um bug deliberado, ativado pela variável de ambiente `ANIMCHECK_MUTANT` (uma por detector, uma por comparação, uma para o verificador de asserções e uma para os nomes de ossos do perfil). A suíte precisa falhar em cada variante e no teste específico indicado em `run_tests.py`, não em outro sem relação.

Fluxos sintéticos vêm de [synth.py](synth.py): caminhantes e atores ociosos controlados por script com defeitos inseridos (deslizamento, pose em T, flutuação, tremor, correções bruscas de posição, pose de morte) e uma cópia atrasada no papel de cliente. Os testes cobrem cada detector em casos limpos e defeituosos, contadores entre máquinas, avatares, perfis (exemplo New Vegas e jogo só com nomes), linha de comando, saídas HTML e JSON e coletor contra uma ponte simulada e um servidor TCP em loopback.

Os testes usam apenas fluxos sintéticos. Calibrar contra um jogo real é uma etapa por jogo: colete uma execução limpa e siga "Ajuste".

## <a id="files"></a>Arquivos

| Arquivo | Função |
|---|---|
| `cli.py` | Linha de comando: `analyze`, `collect`, `demo`, `profile`, `selftest`. |
| `profile.py`, `config.py` | Perfil do jogo e limites. |
| `model.py` | Modelo de fluxo e ator, leitura e escrita JSONL. |
| `detectors.py` | Detectores de uma máquina. |
| `compare.py` | Comparação entre responsável e observador. |
| `analyze.py`, `counters.py`, `report_html.py` | Relatório, asserções e HTML. |
| `collect.py` | Consulta jogos em execução e salva fluxos. |
| `synth.py` | Fluxos sintéticos para testes e demonstração. |
| `run_tests.py`, `tests/` | Comando de teste, suíte e variantes de mutação. |
| `examples/fnv/` | Perfil de Fallout: New Vegas. |

Adaptado do commit f57aa78 de fnv-coop. A sonda interna, verificações estáticas do motor e exportador de registros daquele projeto ficaram de fora por dependerem do motor específico do jogo.
