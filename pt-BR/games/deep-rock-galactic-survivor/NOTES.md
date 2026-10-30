# <a id="deep-rock-galactic-survivor--working-notes"></a>Deep Rock Galactic: Survivor - notas de trabalho

Slug: `deep-rock-galactic-survivor`
Objetivo: modo cooperativo on-line (2 jogadores) para um jogo distribuído apenas para um jogador.

> **Leia primeiro:** [STATUS.md](STATUS.md) - a referência única de Ist/Soll (estado atual/desejado): o que foi verificado, o que está quebrado e o que significa estar concluído. Este arquivo é o índice das notas detalhadas de trabalho.
> O estado operacional privado fica em `local/` (ignorado pelo Git): `local/HANDOFF-current.md` (estado/instalação/teste atuais) e `local/mod/DrgSurvivorCoop/PLAN.md` (plano principal).

## <a id="current-state-2026-10-20"></a>Estado atual (2026-10-20)

- **O modo cooperativo por IP direto/LAN tem todos os recursos implementados em duas instâncias**, verificados por execuções automatizadas. Sincronização de estado com autoridade do host: jogadores, inimigos, saques, terreno, XP/cartas, objetivos, configurações, incapacitação/reanimação, câmera, sala/prontidão/início e espera de carregamento.
- **Interface:** o caminho botão CO-OP -> tela de conexão -> sala de missão foi verificado logicamente (`20261020-182244-menu`: `button=1 connect=1 peer=1 lobby=1`). **Defeito visual:** as **Images** clonadas do uGUI (painel/fundo/preenchimentos de botões) não são desenhadas nesta compilação e o texto TMP fica fraco, deixando a arte da missão aparecer através deles. A interface temporária legível é a alternativa IMGUI (`-LobbyIMGUI`). Detalhes e evidências: [STATUS.md](STATUS.md).
- **Distribuição:** os ZIPs de `DrgSurvivorCoop-0.1.4` foram verificados a partir de uma cópia limpa (`20261020-145500-packageverify`). A instalação e o teste básico em dois PCs ainda estão pendentes.
- **QA visual:** somente o caminho pelo botão do menu é válido. **Não** use `-cooplobby`/AutoHost para capturas de tela; esse atalho cria a sala antes do caminho de entrada pelo menu e produz um canvas ativo e clicável, mas não desenhado.

## <a id="verified-at-a-glance"></a>Visão geral do que foi verificado

| Área | Estado | Evidência |
|---|---|---|
| Transporte, duas instâncias | ✓ | UDP 9050, par conectado, contadores nos dois sentidos |
| Caverna / semente / representante compartilhados | ✓ | impressão digital: 0 de 81 diferentes; `puppet spawned renderers=9` |
| Inimigos: criação/morte/snapshot/vida | ✓ | `enemy transport … fail=0`, `snapshot applied=…` |
| Saques / terreno | ✓ | variações da carteira coincidem; `terrain recv=3 mirrored=3 miss=0` |
| XP, cartas de subida de nível, pausa | ✓ | totais idênticos; cartas diferentes em cada lado; barreira liberada |
| Objetivos, retransmissão de etapa, loja | ✓ | `recv=26 applied=2 miss=0`; `starts=3`; `timedOut=0` |
| Adoção de configurações + negociação inicial | ✓ | `drift=1`, `echo=1`, `held=…` |
| Incapacitação / reanimação / círculo | ✓ | `revived hp=100`; `hasFillFactor=1` |
| Dano nos dois sentidos | ✓ | `sent=20 applied=20 dmgTotal=532`; dano recebido de 8 a 10 de vida |
| Efeitos visuais de combate | ✓ | disparo/feixe/granada/torre/Bosco/boca da arma/rastro; **desenho não comprovado** |
| Botão CO-OP -> conexão -> sala | ✓ lógica | `20261020-182244-menu` |
| Estado da sala / prontidão / início | ✓ | `20261020-172313-lobby-ui`, `20261020-172401-lobby-start` |
| Espera de carregamento + texto de expiração | ✓ | `20261020-123303-loadform`, `20261020-172822-loadtimeout` |
| BACK / marcador fora da tela | ✓ | `20261020-172235-lobby-back`, `20261020-172040-indicator` (- `172202`) |
| Empacotamento / teste prolongado | ✓ | `20261020-145500-packageverify`, `20261020-040552-soak` |

A matriz completa, o Soll (requisitos de projeto), a tabela de lacunas e a definição de "verificado" estão em [STATUS.md](STATUS.md).

## <a id="known-open-items"></a>Pendências conhecidas

- **Visual da sala:** causa raiz das Images clonadas não renderizadas (material / alfa de CanvasRenderer / registro do canvas); nova captura da tela de conexão; disposição em 900×600.
- **Oráculo de desenho dos projéteis:** a criação foi comprovada, o desenho não; comparação fora do processo.
- **Convites/retransmissão Steam** (Spacewar), **agressividade** (adiada), **metade de equipamento de I1**, **dados de teste de Mastery**, **marcos do cliente**, **teste básico em dois PCs**.
- **Marcador:** os caminhos `stale` e `downed` existem apenas no código (sem teste de silêncio forçado/incapacitação).

## <a id="detailed-notes"></a>Notas detalhadas

O registro cronológico de 3.840 linhas foi dividido em 2026-10-20. O conteúdo não mudou.

- [notes/01-core.md](notes/01-core.md) - identidade, ferramentas de modificação, modelo do motor e registro inicial de compilação.
- [notes/02-transport-world.md](notes/02-transport-world.md) - estrutura de testes, transporte, inimigos, saques, terreno e primeiros marcos.
- [notes/03-combat-progression.md](notes/03-combat-progression.md) - dano, subidas de nível, configurações, salvamentos, loja, incapacitação e efeitos visuais de combate.
- [notes/04-lobby-ui-visuals.md](notes/04-lobby-ui-visuals.md) - espelhamento de torre, sala L0-L3, Bosco e revisão da interface (incluindo o defeito visual).

O arquivo anterior à divisão está arquivado de forma privada em `local/archive/NOTES-2026-10-20-full.md`.

## <a id="canonical-test-paths-proven"></a>Caminhos canônicos de teste (comprovados)

```powershell
# Real UI path: menu button -> connect -> peer -> lobby
coop-run.ps1 -Menu -Test menu

# Hold the lobby for a screenshot (canonical path)
coop-run.ps1 -Menu -Test lobbyhold
coop-shot.ps1 -Phase lobby -Seconds 40 -Interval 2 -OutDir ..\work\shots\lobby

# Regressions
coop-run.ps1 -Ui -Lobby -Test lobby-ui
coop-run.ps1 -Ui -Lobby -Test lobby-back
coop-run.ps1 -Ui -Lobby -Test lobby-start

# Marker (+ negative), load hold, load timeout
coop-run.ps1 -Auto -Test indicator -CameraOff
coop-run.ps1 -Auto -Test indicator -CameraOff -IndicatorOff
coop-run.ps1 -Auto -Test loadform
coop-run.ps1 -Auto -Test loadtimeout -Only host
```

Regras: nunca inicie o jogo sem autorização explícita; faça backup do perfil de salvamento; use 1280×720 ou mais para a interface; um teste = ambos os papéis + um identificador de execução + controle negativo quando disponível.

## <a id="notes-discipline"></a>Disciplina das notas

- **STATUS.md é a verdade atual.** Não duplique sua matriz aqui.
- Este arquivo é o índice; os arquivos em `notes/` preservam os detalhes cronológicos e as medições por trás de cada afirmação.
- Código existente sem teste não é verificação. Uma afirmação exige uma execução (`RESULT: … PASS`) e, para efeitos visuais, uma captura da janela (CopyFromScreen + primeiro plano; `PrintWindow` omite a sobreposição nesta compilação).
