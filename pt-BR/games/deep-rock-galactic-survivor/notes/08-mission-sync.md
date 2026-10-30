# <a id="mission-sync--exploration-goal-mission-sync-step-1"></a>Sincronização de missões - exploração (objetivo "mission sync", etapa 1)

2026-10-21. Jogo: Deep Rock Galactic: Survivor, compilação Steam usada em todas as execuções deste repositório (identidade em NOTES.md). Tudo abaixo foi medido com `coop-run.ps1 -Ui -Lobby -Test worlddiff -Wd "1,0,0,1"` (Escolta, setor 1, nó 1, perigo 2) e o coletor somente de observação `CoopMission` (`-coopmissiondump`, `-coopmissionsec=N`). Os nomes são os tipos e membros do próprio jogo vistos pela interoperabilidade gerada; nenhum código do jogo é reproduzido aqui.

## <a id="escort-mission-who-does-what"></a>Missão de escolta: quem faz o quê

| Elemento | Tipo / membro | Comportamento medido |
|---|---|---|
| Bobby | `Bobby` (MonoBehaviour); `State` (`INTRO, ESCORT, MINING_HEART, BROKEN, OUTRO`), `animState`, `distMoved`, `totalDistance`, `fuel`, `playerActivationRange`, `moveSpeed`, `HandleEscort(bool inRange)`, `Move(dt)` | Início (30,32), fim (160,32), `totalDistance=130`, `moveSpeed=4`, `playerActivationRange=6`. Fica parado até haver um jogador a menos de 6 m **e** combustível de Bobby na carteira. Com combustível e um anão ao lado, percorre 130 m em aproximadamente 30 s (host `20261021-110753-worlddiff`: `distMoved` 41 -> 129, State `RUNNING` -> `BROKEN` no final). |
| Combustível | `Wallet.BobbyFuel` (`ECurrency.BOBBY_FUEL = 22`), coletas `PickupBobbyFuel` de `MaterialBlockBobbyFuel` | Valor de **carteira por jogador**. Bobby lê a carteira local; combustível coletado pelo parceiro não chega ao Bobby do host. |
| Objetivo de escolta | `LevelObjectiveEscort`, tipo `ESCORT` | Progresso = porcentagem do caminho (0..100), controlado pelo movimento de Bobby. |
| Objetivo seguinte | `LevelObjectiveArmTNT`, tipo `ARM_TNT` | **Adicionado à lista principal do rastreador quando ESCORT termina**; `EscortMissionHandler.state` passa de `ESCORT -> PREPARE_TNT`. Lista principal do host `[ESCORT=100, ARM_TNT=0..4]`. |
| Detonadores | `TNTDetonator : MineableBlock` x4 (`numDetonatorsToSpawn`), `TakeDamage` / `Die` / `SetArmed(bool)` | Armados por dano. O bot do host causando dano aos quatro produz `ARM_TNT=4` (`20261021-111555-worlddiff`). |
| Zona de TNT | `BobbyTNTZone`, em (160,0,32) | Existe nos dois lados desde o começo. |
| Controlador | `EscortMissionHandler` (injetado pelo zenject, **não é componente**: `FindObjectsOfType` não o encontra) | Responsável por `state`, `tntProgress`, `detonators`, `dropPod`. Inscreve-se nos eventos dos objetivos; só executa a fase seguinte se o evento de conclusão disparar naquela instância. |
| Cápsula de extração | `DropPod`; `state` `INACTIVE, ANIMATING_IN, ARRIVING_COUNTDOWN, WAITING_FOR_PLAYER, WAITING_FOR_PLAYER_EXIT, ANIMATING_OUT`; `timeoutSeconds=30`, `playerPoint`, `rampDetector`, `IsPlayerOnRamp()`, `IsPlayerInside()`, `hasPlayerBeenOnRamp` | Pousa cerca de 2 s após a fase TNT, espera 30 s e parte (`MISSED_DROPPOD`). **O embarque exige passar primeiro pela rampa:** teleportar um anão diretamente para `playerPoint` não basta; ir primeiro a `rampDetector` e depois entrar encerra a etapa em aproximadamente 7 s (`20261021-114845-worlddiff`). |
| Cápsula de suprimentos | `SupplyPod` (reutilizada por pool, `SummonAt(pos)`), campo `ActivationZone.supplyPod`, `UIManager.ShowSupplyPod` | Não acionada em nenhuma execução até agora; a origem do acionamento ainda precisa ser medida (zonas de ativação). |
| Chefe | `EliminationMissionHandler.SpawnBoss` / `didSpawnBoss`, `EggHuntMissionHandler.SpawnBoss`, `EnemySpawner.liveBosses`, `MissionMapConfig.bossMissions` | Etapas com chefes são um recurso de Eliminação; nenhuma escolta criou um. Nenhum bot chegou a essa parte ainda. |

## <a id="measured-gaps-client-vs-host"></a>Lacunas medidas (cliente versus host)

| ID | Descoberta | Evidência |
|---|---|---|
| G10 | **Bobby é simulado por instância.** O Bobby do host anda de 30 -> 160; o do cliente permanece em (30,32) com `distMoved=0 fuel=0 State=NONE` durante toda a execução. | `20261021-110753-worlddiff` (host `pos=159,4,32 State=BROKEN`, cliente `pos=30,0,32 State=NONE`) |
| G11 | **O parceiro nunca conta para o alcance de Bobby.** Um anão que só existe como cliente não consegue fazer o Bobby do host andar. | Pela construção do código (teste de alcance usa o jogador do próprio host); ainda precisa ser demonstrado por execução com escolta somente do cliente |
| G12 | **O espelhamento de objetivos escreve no campo; eventos de conclusão nunca rodam no cliente.** ESCORT do cliente mostra 100, mas `ARM_TNT` nunca entra no rastreador; o espelhamento por índice escreveria `ARM_TNT` do host no espaço secundário do cliente. | Mesma execução: host `primary[ESCORT=100,ARM_TNT=0]`, cliente `primary[ESCORT=100]`; depois host `ARM_TNT=4`, cliente sem esse objetivo |
| G13 | Combustível é por carteira (veja acima); o cliente que coleta combustível não dá nada ao Bobby do host. | Tipo da carteira; ainda não demonstrado por uma execução |

## <a id="test-harness-findings-not-sync-gaps"></a>Descobertas na estrutura de testes (não são lacunas de sincronização)

- Uma subida de nível encadeada (dois níveis juntos, por exemplo a recompensa por concluir a escolta) deixava `UILevelUpForm` aberto por minutos com `timeScale 0`: a automação respondia a cada formulário uma vez (`_levelUpAnswered`). O jogo e a barreira estavam corretos. Corrigido em `CoopAuto` (responde novamente se o formulário continuar aberto após 4 s); o congelamento anterior está em `20261021-111555-worlddiff` / `20261021-114003-worlddiff` (`mission: frozen form=UILevelUpForm`), e a execução após a correção em `20261021-114352-worlddiff`.
- Bots adicionados como opções de teste: `-coopescortbot=host|client|both` (anão ao lado de Bobby), `-coopescortfuel=N` (atalho na carteira do host para evitar minerar combustível), `-coopescortdet` (host causa dano aos detonadores quando Bobby quebra), `-coopdropbot=...` (rampa, depois cápsula). Com eles, uma etapa de Escolta termina **naturalmente** no host: `20261021-114845-worlddiff` (cápsula `WAITING_FOR_PLAYER` -> `ANIMATING_OUT`; o cliente acompanhou com `stage: peer ended its stage`). Essa é a evidência da etapa 2 do objetivo no lado do host.
- `worlddiff` estava ausente da lista de caminhos de sala em `coop-run.ps1` (a execução parava na tela de abertura); adicionado.

## <a id="startup-crash-found-and-fixed-2026-10-21-afternoon"></a>Falha na inicialização encontrada e corrigida (tarde de 2026-10-21)

Sintoma: as duas instâncias encerravam 5 s após iniciar (`coreclr.dll`, violação de acesso, sempre no mesmo offset `+0x1d1fdd`; WER `APPCRASH`, minidumps em `%LOCALAPPDATA%\CrashDumps`). Parecia problema de ambiente porque o primeiro grupo (11:51-11:54) e o segundo (14:01-14:02) ocorreram com uma sessão interativa de área de trabalho ativa; por isso foram feitas medições:

| Verificação | Resultado |
|---|---|
| Jogo sem BepInEx (`--doorstop-enabled false`), sessão interativa ativa | Executa, sem falha |
| BepInEx sem o plugin, sessão interativa ativa | Executa, sem falha |
| BepInEx + plugin, sessão interativa ativa | Falha aos 5 s (também sem opções cooperativas) |
| Plugin ignorando todos os patches Harmony (`-coopskip=all`) | Executa |
| Busca binária na lista de patches (`-coopskip=<names>`, 7 execuções) | Um patch isolado causa falha: `CoopDownedLockWeaponPatch` (`WeaponHandler.ActivateWeapon`) |
| Log BepInEx antes da falha | `During invoking native->managed trampoline ... NullReferenceException at DMD<WeaponHandler::ActivateWeapon>` (e depois `DMD<TNTDetonator::Die>` para o hook de escolta) |
| Hook instalado tarde (primeiro `StartGame`) | Hooks de escolta funcionam; o hook de arma ainda causava falha |

Causa: o jogo já chama `WeaponHandler.ActivateWeapon` durante a inicialização da cena de título (somente quando a janela é efetivamente renderizada, razão pela qual execuções em sessão desconectada passavam). Um hook Harmony nessa chamada encerrava o processo. O hook fora adicionado no objetivo noturno e nunca executado em sessão interativa; uma inicialização normal de jogador também teria falhado. Correção: o hook foi removido; o bloqueio de ataque agora pausa os controladores de armas do anão (`WeaponHandler.paused`) enquanto ele está caído (`CoopDownedLock.PauseTick`), e os hooks de escolta são instalados no primeiro `StartGame` (`ProbePlugin.InstallLate`). Regra para hooks futuros: nunca inserir hook em método chamado durante a inicialização da cena de título; instalar tarde, manter o corpo do hook em try/catch e preferir alterações de estado a hooks. Auxiliares da busca binária mantidos no plugin: `-coopskip=`, `-coopbreadcrumbs`, `-coopguimask=`, `-coopnolate`.
