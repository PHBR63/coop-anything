# <a id="probe-stream-format"></a>Formato do fluxo de sondagem

animcheck nunca altera um jogo. Lê **fluxos de sondagem**: linhas JSON escritas por um pequeno código dentro do jogo (ou junto dele) durante a execução. Esta página define o que esse código deve emitir. Qualquer jogo, qualquer motor: se você consegue ler a posição de um ator, suas animações em execução e seu esqueleto uma vez por quadro, pode produzir o fluxo.

A sonda de referência é a de Fallout: New Vegas, no repositório fnv-coop em `plugin/animprobe` (https://github.com/cranebeaker/fnv-coop). É específica do jogo (lê memória do motor); somente o formato é compartilhado aqui. Use como exemplo da estrutura de uma sonda, não como código reutilizável.

## <a id="the-file"></a>O arquivo

Um objeto JSON por linha (JSONL), UTF-8, um arquivo por máquina (ou instância):

```
host.probe.jsonl
client.probe.jsonl
```

Linhas vazias, que não começam com `{` ou que não são JSON válido são ignoradas; comentários e últimas linhas incompletas não causam problemas. Campos extras são ignorados.

## <a id="one-probe-one-line"></a>Uma amostra (uma linha)

| Campo | Tipo | Obrigatório | Significado |
|---|---|---|---|
| `actors` | array | sim | Atores coletados nesta amostra; veja abaixo. |
| `t_ms` | número | sim, exceto se toda linha tiver `rx_ms` | Relógio do próprio jogo, em milissegundos, no momento da coleta. Deve apenas aumentar. |
| `rx_ms` | número | não | Relógio do coletor em milissegundos, compartilhado pelas máquinas em um PC. Adicionado por `collect`. Quando todas as linhas o têm, o analisador o usa para alinhar as máquinas. |
| `machine` | string | não | Nome da máquina ("host", "client"). Pode ser fornecido pelo nome do arquivo ou argumento `name=path`. |
| `frame` | inteiro | não | Contador de quadros do jogo. |
| `v` | inteiro | não | Sua versão do formato. |

Colete entre 10 e 30 Hz. Frequência maior é aceita. Um intervalo acima de 600 ms entre duas amostras de um ator interrompe a sequência (`gap_ms`); portanto, colete ao menos algumas vezes por segundo.

## <a id="one-actor"></a>Um ator

Ator é qualquer elemento com corpo no mundo: jogador, companheiro, NPC, representante de jogador remoto.

| Campo | Tipo | Obrigatório | Significado |
|---|---|---|---|
| `ref` | inteiro ou string | sim | Identificador estável do ator. Inteiro ou texto hexadecimal (`"0x0010A2B3"`, `"FF000A"`). Mesmo identificador em toda amostra. Se o jogo usa nomes como IDs, converta para números na sonda. |
| `pos` | [x, y, z] | sim | Posição no mundo em unidades do jogo. **Z aponta para cima.** Converta na sonda se o motor usa Y para cima. |
| `rot` | [pitch, roll, yaw] | sim | Ângulos de Euler. `rot[2]` é a orientação horizontal (yaw em Z); `rot[0]` é a inclinação da mira. Radianos, salvo se o perfil definir `"angle_unit": "deg"`. |
| `cell` | inteiro ou string hexadecimal | recomendado | Identificador da área ou fase do ator. Mudar `cell` é teleporte, não movimento. Use 0 se o jogo não tiver esse conceito. |
| `valid3d` | bool | não (padrão true) | False enquanto o corpo não estiver carregado ou visível. Detectores de falhas visuais ignoram essas amostras. |
| `dead` | bool | recomendado | O ator está morto. |
| `player` | bool | não | True para personagem de jogador real. |
| `first_person` | bool | não | Câmera em primeira pessoa. O esqueleto em `bones` ainda precisa ser o corpo completo de terceira pessoa (veja abaixo). |
| `anim` | objeto | recomendado | O que está em execução; veja abaixo. Sem ele, a animação do ator nunca é avaliada. |
| `bones` | objeto | recomendado | Posições dos ossos no mundo; veja abaixo. Necessário para a pontuação de pose e verificação de pose T. |
| `weapon` | objeto | não | `{ "out": bool, "aiming": bool, "form": id }`. `out` = arma sacada; `form` = qual item. |
| `stance` | objeto | não | `{ "knocked": int, "swimming": bool, "ragdoll": bool, "sneaking": bool }`. `knocked` é 0 em pé e maior que 0 quando derrubado ou desequilibrado. |
| `move_flags` | inteiro | não | Campo de bits dos estados de movimento. Só é lido se o perfil tiver `move_flag_bits` (veja README), para obter `sneaking` e `swimming`. |
| `ground_z` | número | não | Altura do chão sob o ator, se a sonda puder consultá-la no jogo. Torna exatas as verificações de flutuação e afundamento. Sem ele, o analisador acompanha a última altura apoiada por conta própria. |
| `ai` | objeto | não | `{ "in_combat": bool, "combat_target": id, "package": id }`. Lido, mas não utilizado por nenhuma verificação. |

### <a id="anim-what-is-playing"></a>`anim`: o que está em execução

```json
"anim": { "seqs": [ { "slot": 0, "group": 0, "state": 1 }, { "slot": 1, "group": 3, "state": 1 } ] }
```

Cada entrada de `seqs` é uma animação que o sistema de animação do jogo mantém para este ator:

| Campo | Significado |
|---|---|
| `slot` | Canal ou camada de execução (qualquer inteiro pequeno). Duas amostras são "a mesma animação" quando slot e grupo coincidem. |
| `group` | Grupo, estado ou clipe de animação. **Identificador inteiro** ou **nome textual**. O perfil converte em categoria (repouso, caminhada, corrida etc.). |
| `state` | `1` = em execução. Qualquer outro valor (ou ausente) = carregada, mas não executando. Somente entradas em execução contam. |
| `t`, `begin`, `end`, `freq`, `weight` | Tempo de reprodução, intervalo, velocidade e peso de mistura opcionais. Lidos, mas não utilizados nas verificações. |

Como mapear um motor: use o que o jogo chama de estado atual de animação, uma entrada por camada ou canal ativo. Em animador por camadas, o índice da camada é `slot` e o nome do estado atual é `group`. Em motor por sequências, o espaço da sequência é `slot` e o identificador de seu grupo é `group`. Informe também animações entrando ou saindo da mistura, com `state` 1 enquanto ainda tiverem peso.

Ator com bloco `anim`, mas nenhuma entrada em execução, é avaliado como "sem animação" (verificação de pose T). Sem bloco `anim`, não é avaliado quanto à animação.

### <a id="bones-the-skeleton"></a>`bones`: o esqueleto

```json
"bones": { "pelvis": [1000, 2000, 140], "head": [1000, 2000, 186], "hand_l": [1000, 1988, 146] }
```

Objeto que associa nome do osso à posição **no espaço do mundo** `[x, y, z]` (não local nem relativa ao pai).

- Os nomes são os nomes de nós do motor. O perfil informa qual é o osso raiz e quais são braços e mãos. Nada mais precisa de entrada no perfil.
- Envie 10 a 16 ossos: raiz (pelve ou quadris), coluna, pescoço, cabeça, braços, antebraços, mãos, panturrilhas e pés são um bom conjunto. A pontuação de pose precisa de pelo menos 3 ossos além da raiz presentes nas duas máquinas.
- Envie o **mesmo conjunto de nomes nas duas máquinas**. A pontuação compara somente os ossos relatados por ambos.
- Envie o corpo completo de terceira pessoa mesmo se o jogador estiver em primeira pessoa. Um modelo só de braços produz falsa pose T e falso erro de pose. Se o motor oculta o corpo de terceira pessoa, leia seu esqueleto mesmo assim; se ele não for animado nessa situação, informe `valid3d: false` para ignorar as amostras.
- O erro de posição é medido após alinhar a raiz e girar cada esqueleto pelo próprio `rot[2]`; posição ou orientação diferentes não contam como erro de pose. Somente o formato da pose conta.

## <a id="example-line"></a>Linha de exemplo

```json
{"machine":"host","t_ms":1250.0,"frame":75,"actors":[{"ref":"0x00000014","pos":[1000.0,2000.0,100.0],"rot":[0.2,0.0,1.57],"cell":"0x0000DEAD","valid3d":true,"dead":false,"player":true,"anim":{"seqs":[{"slot":0,"group":1,"state":1}]},"weapon":{"out":true,"aiming":true,"form":"0x00001234"},"stance":{"knocked":0,"swimming":false,"ragdoll":false,"sneaking":false},"bones":{"pelvis":[1000.0,2000.0,140.0],"head":[1000.0,2000.0,186.0],"upper_arm_l":[1000.0,1990.0,172.0],"hand_l":[1000.0,1988.0,146.0],"upper_arm_r":[1000.0,2010.0,172.0],"hand_r":[1000.0,2012.0,146.0]}}]}
```

`python -I tools/animcheck/cli.py demo --out DIR` escreve dois fluxos completos de exemplo para você abrir.

## <a id="several-machines"></a>Várias máquinas

Para comparar o que um cliente exibe com o estado da máquina responsável, registre um fluxo por máquina **ao mesmo tempo** e passe-os juntos: `cli.py analyze host.jsonl client.jsonl`. O primeiro é o responsável (fonte de verdade); os demais são observadores.

- **Mesmos IDs.** Um NPC presente nas duas máquinas deve ter o mesmo `ref`. Se forem diferentes, forneça um mapa no código (`analyze(..., ref_maps=...)`).
- **Avatares.** O personagem próprio de um jogador e seu representante em outra máquina têm IDs diferentes. Informe ao analisador com `--avatar NAME=host:14>client:FF000A` (máquina e ID do responsável, depois máquina e ID do observador). Avatares são pontuados separadamente dos NPCs, nos contadores `avatar.*`; nunca entram nas contagens de NPCs.
- **Relógios.** Dois processos têm dois relógios. Em um PC, consulte ambos com `collect`, que adiciona `rx_ms` a cada amostra, compartilhando um relógio. Se tiver somente `t_ms` de processos diferentes, use `--auto-offset`, que encontra a diferença de relógio que melhor alinha as posições.
- **Buffer de interpolação.** Um cliente geralmente exibe atores remotos cerca de 100 ms no passado. A comparação prevê isso (`--delay-ms`, padrão 100) e procura o melhor alinhamento até 150 ms em cada direção (`--latency-ms`).

## <a id="what-each-check-reads"></a>O que cada verificação lê

| Verificação | Campos lidos |
|---|---|
| sliding | `pos`, `cell`, `anim.seqs` (categoria do grupo), `dead`, `stance` |
| tpose | `anim.seqs`, `bones` (braços e mãos), `dead`, `stance` |
| floating, sinking | `pos`, `ground_z`, `cell`, `anim.seqs` (salto), `stance` |
| jitter | `pos` |
| rubberband | `pos`, `cell` |
| stuck | `pos`, `anim.seqs`, mais janelas de tempo fornecidas por `--expect-moving` |
| deathpose | `dead`, `anim.seqs`, `stance.ragdoll` |
| pose error | `bones`, `rot` |
| group mismatch | `anim.seqs` (slot e grupo) |
| wrong weapon, wrong aim, wrong facing, stance | `weapon`, `rot`, `stance` |

Omitir um campo simplesmente desativa, para aquele ator, as verificações que dependem dele.

## <a id="collector-protocol-optional"></a>Protocolo do coletor (opcional)

Se a sonda não puder escrever arquivos, pode responder a solicitações, e `cli.py collect` a consulta. Um objeto JSON por linha por TCP:

```
request:  {"method": "anim.probe", "params": {}}
reply:    <one probe object as above>        or   {"error": "message"}
```

`--method` muda o nome do método. Um segundo método opcional (`--stats-method`, padrão `anim.stats`) pode retornar medidas de custo da sonda (por exemplo, microssegundos por ator); `collect` as exibe. Se a própria sonda escreve JSONL, ignore isso e execute `analyze` nos arquivos.

## <a id="keep-the-probe-harmless"></a>Mantenha a sonda inofensiva

- Somente leitura. A sonda não deve alterar o jogo, enviar entrada nem mover nada.
- Execute onde o estado é consistente (thread principal ou do jogo, uma vez por quadro ou em temporizador).
- Proteja toda leitura de dados do motor; offset errado ou objeto liberado deve resultar em campo ausente, não falha.
- Meça o custo e mantenha-o baixo, para a coleta não alterar o tempo de quadro que você está verificando.
