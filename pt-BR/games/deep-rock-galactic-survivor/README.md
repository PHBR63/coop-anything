# <a id="deep-rock-galactic-survivor-2024"></a>Deep Rock Galactic: Survivor (2024)

| | |
|---|---|
| Motor | Unity 6 (IL2CPP, metadados v39) |
| Versões testadas | Compilação Steam `23854500` (Windows) |
| Projetos | [drg-survivor-local-coop](https://github.com/Reudo/drg-survivor-local-coop) (cooperativo local, jogável, MIT); [drg-survivor-coop](https://github.com/Reudo/drg-survivor-coop) (protótipo on-line, arquivado) |
| Nível de QA | plugin local: automated em um PC (resultados abaixo) e partidas manuais do autor; protótipo on-line: automated só em um PC, sem confirmação humana (primeiro teste em dois PCs contradisse partes, [STATUS.md](STATUS.md)) |
| Última atualização | 2026-10-25 |

> **Ist/Soll atual:** [STATUS.md](STATUS.md), estado verificado, defeitos, requisitos e lacunas. Notas detalhadas: [NOTES.md](NOTES.md) e [notes/](notes).

## <a id="local-co-op-plugin-playable-version-100"></a>Plugin cooperativo local (jogável, versão 1.0.0)

[drg-survivor-local-coop](https://github.com/Reudo/drg-survivor-local-coop) coloca dois anões em um jogo no mesmo PC, cada qual em seu controle (plugin BepInEx 6 IL2CPP com Harmony; segundo anão é outro objeto de jogador no mesmo processo, sem rede ou dessincronização). Missões Elimination e Escort: menu próprio, dois HUDs, subidas de nível/loja um após o outro, pausa por jogador, reanimação, XP compartilhada, cápsula exige ambos. On-line funciona por Steam Remote Play Together. ZIP com instalador nas versões do repositório; capturas no README.

- **QA:** estrutura por scripts (`tools/batch_*.ps1`) inicia cópia de teste com controles virtuais e avalia logs/capturas; cada verificação tem indicador de mutação que deve fazê-la falhar. Resultados 2026-10-21 a 2026-10-23 (IDs em `PLAN.md`): menu 11/11, cliques reais de mouse 5/5, início real pelo menu (classe/missão lidas no segundo anão ativo), travas de menu 10/10 (mutação 6 aprovadas, 4 falhas), espelhamento de bônus 5/5 (mutação 0/5), pausa por jogador 5/5 (mutações falham), repetir partida 7/7, reanimação/caixa de saque aprovadas (mutações falham). Autor jogou várias partidas completas com dois controles: sem bugs impeditivos, no máximo visuais pequenos, como indicação incorreta na interface. Sem relato independente; só um PC.
- **Lacunas:** números de dano finais provavelmente incorretos; DLCs não suportados nem testados ativos; outros tipos de missão não oferecidos. Demais no README do projeto.
- Este é o caminho funcional hoje. O protótipo on-line abaixo foi interrompido/arquivado; notas mantidas como pesquisa.

## <a id="where-things-stand"></a>Situação atual

O jogo em si **não tem modo cooperativo**. O restante registra o protótipo **on-line** anterior do zero, quando não existia mod publicado. É um survivors-like de um jogador: um anão, uma caverna e nenhuma rede nos assemblies. Jogar junto exige criar um mod do zero; não havia caminho de concluir mod existente, por isso este relato registra essa iniciativa.

O protótipo ([Reudo/drg-survivor-coop](https://github.com/Reudo/drg-survivor-coop), duas instâncias num PC) **pretende cobrir** todo o ciclo. **Ressalva:** abaixo estão medições automatizadas em um PC; primeiro teste real com dois PCs (2026-10-21) mostrou partes ainda falsas (mapas diferentes por corrida de sementes, anão cliente exibido errado no host, incapacitado movendo, desbloqueios host não ativados por padrão; [STATUS.md](STATUS.md), seção "Contradicted by the first real two-PC test"). Medidos: mesma caverna, ambos visíveis/animados, inimigos com autoridade do host, saques/terreno compartilhados, XP comum com cartas individuais, objetivos espelhados, loja por etapa esperando parceiro, fim de etapa chegando à outra instância, incapacitação/reanimação e cliente usando **desbloqueios do host**, preservando ganhos. Toda afirmação abaixo medida em dois clientes reais no mesmo PC por scripts, não por pessoa em dois PCs.

Ambos também **esperam um ao outro no início**: informam fase carregada, mais rápido fica pausado, host libera juntos. A câmera **enquadra os dois**, centraliza e afasta conforme se separam.

Início agora é uma **sala** real: após hospedar/entrar, ambos chegam à tela interna, host define missão, setor/nó e perigo ao vivo; cliente vê mudanças e escolhe apenas classe/mod; host inicia após prontidão. Mais rápido também fica na **tela de carregamento** ("Fertig geladen - warte auf Spieler 2") até o parceiro carregar.

**Ressalva visual da sala (2026-10-20):** interface clonada do jogo; nesta compilação, **imagens** de painel/fundo/botões não são desenhadas, arte da missão aparece e texto fica fraco. Fluxo, botões e barreira funcionam; `-LobbyIMGUI` oferece alternativa legível. **Lógica** verificada; **aparência**, não. [STATUS.md](STATUS.md).

Falta chegar ao jogador: **sem convites/retransmissão Steam** (painel e sala só IP direto/LAN), inimigos perseguem sempre o host. Barras de vida seguem host; cliente mostra **apenas seu dano**, intencionalmente. Flashes de disparo espelhados quando habilitados nos dados da arma. Pose **e fase do ciclo de caminhada** do parceiro sincronizadas, animação VAT dos inimigos espelhada, Bosco e torre Thumper (com flash) como entidades visuais. Jogo não possui modelo separado da arma segurada; visual do personagem é a aparência do mod de classe.

## <a id="existing-work"></a>Trabalhos existentes

Antes, nada publicado. Buscas GitHub, Nexus, ModDB e Steam sem projeto cooperativo/multiplayer; pesquisa completa dos assemblies sem transporte, socket ou rede Steam. A lacuna em `data/directory.yaml` registra locais/datas.

Protótipo publicado como código em [Reudo/drg-survivor-coop](https://github.com/Reudo/drg-survivor-coop), sem versão, instalador ou DLL; documentado para o próximo agente não recomeçar.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

Leitura por descompilação dos assemblies IL2CPP. **Il2CppDumper não lê este jogo** (metadados v39); Cpp2IL do BepInEx lê. Modificação usa BepInEx 6 (IL2CPP), Harmony e transporte próprio.

- **Nenhuma rede.** Nada tem autoridade sobre outra coisa; toda decisão é nossa. Protótipo para 2, autoridade do host.
- **Geração normal sem semente de partida.** Ninguém chama `Random.InitState`; só `FixedRunInstance` diário/semanal tem semente. `MapGenerator.CreateMap` usa ruído. Por isso gera cavernas diferentes, corrigível ao semear `UnityEngine.Random` igualmente antes de `CreateMap` (comprovado abaixo).
- **`Entity : MonoBehaviour` é âncora natural:** `Player` e `Enemy` derivam, com `currentHp`, `position`, `isAlive`, `TakeDamage`, `Heal`, `Die`.
- **Entrada única XP:** `Player.GainXp(float amount, bool scaleByXpGain = true)`. Evento global correspondente `CoreGameEvents.OnPlayerXpGain` / `TriggerPlayerXpGain(PlayerXpGainArgs)` permite observar sem patch.
- **Subida de nível** em `LevelUpManager`: fila `levelUps` esvaziada por `StartFlow` -> `HandleLevelUps` -> `OnLevelUpFinished`, indicador `flowActive` e evento estático `OnFlowActivity`. Carta *pré-visualizada* em `UILevelUpForm.OnSkillSelected`, só *confirmada* em `OnSkillChosen`; pressionar botão não é escolhê-la.
- **Inimigos** de `EnemySpawner` (registro `enemies`, `enemyPrefabs`, `poolDictionary`, `liveElites`, `liveBosses`), vindos de `ObjectPool`, nunca `Instantiate`. `Enemy` já tem `id`, `OnDeath`, `OnTookDamage`, `OnHealed`, `OnKnockback`. Guarda exatamente **um** `Player`, fixado em `OnCreated(..., Player player, ...)` por propriedade só leitura, impedindo simples redirecionamento da agressividade.
- **Fim de etapa/loja** ligado a `CoreGameEvents.TriggerStageEnd(CoreLevelEndArgs)`; loja `UIShopScreen.Show`, continuar `OnPlayButton`, fechamento pelo próximo `GameController.StartGame`; `UIShopScreen.Hide` nunca chamado ao fechar.
- **Zenject** conecta dependências; usa `FSG.MeshAnimator` e KDTree (`PhysicsSimulation`), possível gestão de interesse do enxame.
- **Salvamentos por usuário, não instância.** Pasta comum, sincronizada Steam Cloud; instâncias escrevem nos mesmos arquivos sem redirecionamento. Três posições numeradas (`drg_save_slot{N}_{rotation}.dat`).
- **Steam obrigatoriamente ativo.** Sem ele, tela preta com `SteamAPI_Init() failed`, sem menu; conferir antes de culpar o mod.

- **Disparos do parceiro visíveis por padrão.** Antes atrás do indicador B3 `-cooptrace`; pacotes Fire chegavam, mas nada era criado. Agora cria prefab real por padrão (`-coopmirroroff` desliga). Verificado sem `-Mirror`: host espelha Bosco cliente, cliente espelha Subata host, `applied=N dropped=0`.

## <a id="what-we-changed"></a>O que alteramos

Plugin BepInEx IL2CPP com Harmony e LiteNetLib (transporte Nitrox) por UDP. Papéis no painel; testes ainda podem fixar por opções. Afirmação só vale com evidências de **ambos**; expiração não é evidência.

- **Hospedar/entrar interno (LAN/IP).** IMGUI com endereço/porta, **Host**/**Join**, ocultado por F8; chama mesmo `CoopNet.Init` dos indicadores, para módulos conhecerem papel antes. *Teste:* sem opções de papel, estrutura pressionou botões; ambos `RESULT: ui PASS role=host/client peer=1`, arena ponta a ponta passou com `peer=1`. Sem Steam.
- **Cavernas idênticas.** Prefixo de `MapGenerator.CreateMap` semeia `UnityEngine.Random` igualmente. *Teste:* 81 posições com `MapGenerator.IsRockBlock`, impressões de 81 bits **iguais, 0/81 diferentes**, confirmadas visualmente. Antes divergiam.
- **Outro anão visível, movendo, virando e animando estado.** Clona subárvore visual local, recria no início e controla por rede/estado. *Causas iniciais:* clone do **menu** (4 renderizadores, 9 na partida); velocidade calculada por quadro de posição que muda cerca de 20/s dava 3 vezes a real, nunca voltava à animação parada. Não há **`SkinnedMeshRenderer`**: pose por transformações, estado distingue vivo/incapacitado; sincroniza hash `AnimState`, não deduz por vida.
- **Fase da caminhada alinhada.** Só hash deixava tempo do clipe independente. `AnimPhase` (tipo 28, não confiável, cerca de 10 Hz) leva `normalizedTime` e hash; só corrige erro de ciclo acima de 0,1, sem reiniciar por pacote. *Teste:* `-Test animphase` PASS nos dois, `good=15/15 moved=1` (host `lastErr=0.08`, cliente `0.00`); `-AnimPhaseOff` falha em `phase=off`, não por expiração.
- **Animações VAT dos inimigos sincronizadas em estado/fase.** Usa `EnemyAnimator`/`ShaderMeshAnimator`, não `Animator`; snapshot inclui índice do clipe/fase host. *Teste:* `-Test enemyanim` PASS ambos (`sent=196`; cliente `seen=42 applied=7 sampled=21 match=21`); `-EnemyAnimOff` falha no cliente por `seen=0 enemyanim=off`.
- **Autoridade de inimigos.** Criação/morte/posição host -> cliente; cliente cria espelhos `Enemy` reais do próprio conjunto. *Teste:* `check: enemy transport host=… mirrors=… spawn=… death=… fail=0`, `check: snapshot applied=… missed=…`, ambos.
- **Dano cliente chega ao host.** Armas locais, relata diferença de vida de `TakeDamage`, host aplica ao inimigo próprio. *Teste:* `sent=20 dmgTotal=532` igual a `applied=20 missed=0 unmatched=0 dmgTotal=532`.
- **Anão cliente recebe dano** do enxame espelhado: espelho é `Enemy` real criado pelo próprio gerador, `OnCreated` recebe jogador cliente. Sem pacote: cada lado controla vida própria. *Teste:* `-NoGod`, 8 × 10 de vida perdidos em ambos na mesma janela, cada acerto com `nearestMirror=0.7–1.2`.
- **Saque/carteiras iguais.** Toda coleta transmitida; receptor remove sua cópia (original no host, espelho cliente), credita **todas** as moedas. *Teste:* `walletDelta={GOLD=+3 NITRA=+6}` iguais, coletas espelhadas (7/2, 2/7), `miss=0`, `credited == claimsRecv`. Corrigidos envio só host, fila consumida só cliente e ausência de moedas persistentes.
- **Terreno minerado igual.** `TerrainDestroy` espelha veios `MaterialBlock` à lista da outra instância. *Teste:* `check: terrain recv=3 mirrored=3 miss=0`.
- **XP comum, cartas individuais.** Ganhos espelhados com `scaleByXpGain: false`; fluxo espera **ambos**, com limite para não travar após perda do par. *Teste:* `lvl/xp/total` iguais, cerca de 4,1 s de espera, cartas **diferentes** (`SupportSkill_*` e `WeaponUpgradeSkill_FireRate`).
- **Objetivos espelhados.** Host lê `LevelObjectiveTracker.PrimaryObjectives` / `SecondaryObjectives` a 1 Hz, transmite `(index, progress)`. Secundários aleatórios; semeia `UnityEngine.Random` antes de `SetupSecondaryObjectives`. *Teste:* `check: objective recv=26 applied=2 miss=0`, tipos iguais.
- **Cliente adota partida host.** Envia perigo, semente, bioma, setor, nó, missão/principal; cliente confirma, assistente **espera** antes da classe. Sinal de 1 Hz foi alternativa que entregou. *Teste:* `held=10.1s helloTx=7` -> host `peer-ready=1 echo=1`; configuração retida: `held=20.3s`. Nó cliente divergente (`-coopdrift`), ambos ainda `biome=Crystalline Cavern(0) … node=0` do host.
- **Lojas por etapa, uma por jogador, moeda comum.** Compras locais diferentes, carteira compartilhada. `UIShopScreen.OnPlayButton` espera par e é invocado novamente para liberar. *Teste:* `heldFor=15,6s releases=1 timedOut=0`, mensagem do par como prova; controle negativo sem barreira falha com `remoteDone=0`.
- **Fim de etapa chega ao parceiro.** Só objetivos não bastam: host chegou à etapa 2, cliente ficou na 1 por 300 s. Pacote usa `CoreGameEvents.TriggerStageEnd` com `ApplyingRemote`, sem eco. *Teste:* loja cliente abriu **17 ms** depois (antes cerca de 14 s), espera caiu de 45 s a 0,5 s, ambos `starts=2`; duas transições `starts=3`, `endsRemote=2`. Negativo `-StageEndNoRelay` falha ambos.
- **Incapacitação, reanimação, corpo.** `Player.Die` ainda leva Animator a `Dying`; reescrever `currentHp` não altera pose porque `isDead` é **Trigger**, não Bool. `Animator.Rebind()` + `Update(0f)` restaura (`SetIdle(false)` alternativo), remoto pelo estado sincronizado, não vida. *Teste:* `anim != Dying#-1546996312` após reanimar e 1 s depois, duas vezes; negativo `alive-but-dying`.
- **Granadas espelhadas mesmo sem posse no receptor.** Nome de habilidade + origem + direção; host envia habilidades equipadas, receptor usa `Player.EquipNewWeapon` **antes da partida**, garantindo conjunto para explosão. *Teste:* cliente `adopt … via=EquipNewWeapon weapons=1->2 registered=1` -> espelho `via=pool` -> `RESULT PASS spawned=1 exploded=1`; arremesso próprio não serve mais como prova. Efeito conhecido: receptor também pode lançar a granada.
- **Ambos carregam antes de jogar.** `CoopLoad` pausa em `StartGame` via `GameController.PauseCore()`, troca `RunLoaded`, host libera com `UnpauseCore()` quando ambos prontos (30 s após perda). *Teste:* cliente atrasado 8 s: host `held=23.5s`, cliente `held=8.0s`, ambos `paused=1 peer=1`; posição/contagem inimiga host congeladas enquanto bot atualizava.
- **Câmera enquadra ambos.** Ponto médio como alvo de câmera virtual; offset de acompanhamento cresce com distância (até 1,6×), afastando sem excluir parceiro. Restaurado fora do cooperativo. *Teste:* separados 20 a 23 unidades, `camera PASS farVisible=19–20/20` ambos; `-coopcameraoff`, `5/20` e `1/20` -> **FAIL**. Marcador permanece se ultrapassar zoom.
- **Vida inimiga host, números individuais.** `EnemySnapshot` leva vida; cliente aplica **só redução** (`hp = min(local, host)`), impedindo cura por snapshot antigo. Armas cliente já causam dano local imediato; por decisão, não exibe números host, sem evento host->cliente. *Teste:* cliente `snapSeen=11 equal=6 drops=1/82 above=4`; `-coophpsoff` falha em estado (`snapEntries=31 hpSeen=0`), não expira.
- **Flashes espelhados.** Disparo recebido usa `ProjectileWeaponSkillData.FlashSettings` por `ImpactLightsManager.AddLight`, independente do projétil. Desativado nos dados continua escuro (Bosco); recurso ausente usa padrão quente pequeno. *Teste:* cliente `flashes=8 disabled=2 failures=0` (Subata host), host `flashes=0 disabled=10` (Bosco cliente); `-MuzzleOff` -> **FAIL** `fireRecv=10 flashes=0`.
- **Cliente usa perfil host e mantém ganhos.** Listas de desbloqueio, níveis meta/equipamento transmitidos como dados nativos; aplicados **na memória, no menu**, antes da classe. Gravações próprias bloqueadas durante empréstimo, devolvido no fim: ID removido só se emprestado e não possuído antes, mantendo ganhos. *Teste:* `client dwarf=00000000 → received {cls=4 mod=9 wpn=29 art=13 oc=0 sets=1} → classPageButtons=4`; meta `90 → 0`, `gold 10 → 0 goldMoved=1`; equipamento `0 → 6 collected=6`. **Arquivo de salvamento** verificado: sem dados emprestados, com ganhos (`classXp 5956 → 5958` para `perfXp=2`).
- **Fim como individual.** Ambos incapacitados acionam encerramento original; sobrevivente continua e reanima. Política em um patch, decidida pelo *estado*, pois ambos ainda viam parceiro vivo 40 ms após morte, pela latência da vida.
- **Estrutura de testes.** Veredictos do mod (`RESULT: <test> PASS|FAIL reason=…`), sem espera adivinhada; toda execução faz backup/**restaura** salvamentos (hash + arquivo sentinela), arquiva logs e encerra processos iniciados.

## <a id="qa"></a>QA

**Execução:** duas instâncias em um PC, bots nos dois anões, log por instância. Papéis pelo painel interno (`-Ui`, acionado por auxiliar de cliques) ou opções nos demais testes. Mod decide quando a questão foi respondida, grava veredicto legível por máquina e pode encerrar; questão sem resposta resulta em `FAIL reason=timeout`, não silêncio. Asserções comparam logs: precisa de evidência do par, sem exceções.

**Última suíte (2026-10-20):** todos abaixo PASS nos dois papéis nas execuções mais recentes:

| Questão | Evidência |
|---|---|
| Mesma caverna | 0/81 amostras da impressão digital diferentes |
| Inimigos | `spawn/death/… fail=0`, `snapshot applied=… missed=…` |
| Dano do cliente | `sent=20 applied=20 dmgTotal=532` nos dois |
| Saque | carteiras iguais, contagens espelhadas, `miss=0` |
| XP/cartas | totais iguais, cartas diferentes, barreira liberada |
| Objetivos | `recv=26 applied=2 miss=0`, tipos iguais |
| Adoção das configurações | cliente forçado a outro nó, ambos leem o do host |
| Barreira da loja | espera `ShopDone` do par, `timedOut=0` |
| Retransmissão de etapa | `starts=3` em duas transições, `endsRemote=2` |
| Incapacitação/reanimação | pose sai de `Dying` e permanece, duas vezes |
| Empréstimo de perfil | `classPageButtons=4`, arquivo conferido antes/depois |
| Interface hospedar/entrar | `RESULT: ui PASS role=host/client peer=1`; ponta a ponta `arena PASS` com papéis da interface |
| Granada espelhada (receptor não tinha) | `adopt … weapons=1->2 registered=1` -> `via=pool` -> `exploded=1` |
| Barreira de carregamento inicial | `-LoadDelay 8`: host `held=23.5s`, cliente `held=8.0s`, ambos `paused=1` |
| Câmera enquadra dois | `camera PASS farVisible=19–20/20`; `-coopcameraoff` `5/20` / `1/20` -> FAIL |
| Vida inimiga segue host | cliente `snapSeen=11 equal=6 drops=1/82 above=4`; `-coophpsoff` -> FAIL `hpSeen=0` |
| Flash espelhado | cliente `flashes=8 disabled=2`; host `disabled=10` (Bosco); `-MuzzleOff` -> FAIL |
| PGL dispara/espelha | `weapons PASS expected=1 received=1 notFired=0`; eventos Fire nos dois sentidos (`20261019-233339-weapons`, repetição de janela 15 s `20261019-235051-weapons`) |
| Feixe elétrico TH0R | `beam=3/2` host, `3/3` cliente, `skills=1/1`; PASS ambos (`20261019-234302-weapons`); `-BeamOff` -> FAIL `beam=0/0 notFired=1` (`20261019-234645-weapons`) |
| Feixe contínuo giratório | host `beam=98/91`, cliente `100/98`, `skills=1/1`; PASS ambos (`20261020-012001-weapons`, `RotatingBeam_CryoCannon`) |
| Granada de zona no chão espelhada | host `sent=1`; cliente `sent=4 spawned=6 exploded=1 adopted=1`; PASS ambos (`20261020-013904-grenade-mirror`, `Groundzone_Acid`); zona criada pela explosão espelhada |
| Espelhos inimigos movem/viram suavemente | cliente `maxStep=0.500 facingApplied=364`; PASS ambos (`20261020-005713-enemysmooth`, compilação final); `-SnapSmoothOff` -> FAIL `maxStep=2.002`, `-EnemyFaceOff` -> FAIL `facingApplied=0` |
| Orbes XP visíveis em ambos, crédito único | host `spawnSent=16 claimSent=15 finishCalls=8`; cliente `spawnRecv=16 applied=16 suppressed=8`; PASS ambos (`20261020-005304-xpsync`); `-XpOff` -> FAIL `spawnSent=0 spawnRecv=0` (`20261020-005512-xpsync`) |
| Círculo de reanimação preenche | `prefab=Projector hasFillFactor=1`, 329/332 atualizações; PASS ambos (`20261020-011703-revivecircle`); `-ReviveVisualOff` -> FAIL `created=0` (`20261020-011516-revivecircle`) |
| Quantidade de vida reanimada proporcional | padrão 50% do máximo: host `maxHp=145 → hp=72`, cliente `130 → 65`; `-coopreviveflat` preserva 100 fixos antigos |
| Zonas de rastro | host `sent=34`, cliente `recv=38 applied=38`, PASS ambos (`20261020-015745-trail`); `-ZoneOff` -> FAIL `sent=0 applied=0` (`20261020-015907-trail`) |
| Granada de zona no chão | `GrenadeWeaponSkillData_Groundzone_Acid`: cliente `spawned=6 exploded=1 adopted=1`, PASS (`20261020-013734-grenade-mirror`) |
| Visual da torre | host `sent=1 stateSent=56`; cliente `spawned=1 states=42 prefab='Turret_THUMPER'`, PASS ambos (`20261020-022442-turret`); `-TurretOff` -> FAIL `sent=0 spawned=0` (`20261020-022622-turret`) |
| Efeito de disparo da torre | host `sent=5`, cliente `recv=5 applied=5 flashes=5`; PASS ambos (`20261020-131050-turretfire`); `-TurretFireOff` -> FAIL `sent=0 recv=0` (`20261020-131227-turretfire`) |
| Modelo remoto da arma | Não aplicável: sem modelo separado de arma segurada (`WeaponHandlers` é contêiner vazio comum, 0 renderizadores; sem `WeaponSkinData`/`WeaponModel`). Aparência do mod de classe é visual do personagem; falha `weaponvisual` esperada e aposentada |
| Estado da sala / prontidão | host rev=2 `blockedPeer=1 blockedStale=1 allowed=1`; cliente `state=2 choice=2 start=1`; PASS ambos (`20261020-054247-lobby-state`); `-LobbyNoReadyGate` -> FAIL (`20261020-054515-lobby-state`) |
| Tela da sala (estrutura/cliques, **não pixels**) | host `sectors=5 nodes=6 classes=5 mods=3 hazards=5`; host altera perigo, cliente vê rev=2, escolhe Engineer/Maintenance e pronto; host pode iniciar; PASS ambos (`20261020-063928-lobby-ui`, `20261020-172313-lobby-ui`); `-LobbyUIOff` -> FAIL (`20261020-063812-lobby-ui`). **Visual: ❌ imagens clonadas não desenhadas, [STATUS.md](STATUS.md)** |
| Início da sala pelo assistente | host Driller/Interrogator, cliente Engineer/Maintenance, mesmo `main=0 biome=0 sector=0 node=0 hazard=1`; `run=1`; PASS ambos (`20261020-064751-lobby-start`) |
| Tela de carregamento espera | `UILoadingForm` real sobre jogo pausado com `Fertig geladen - warte auf Spieler 2`, ocultada ao liberar; host `shown=1 paused=1`, `held=1.4s`; PASS ambos (`20261020-123303-loadform`); `-LoadFormOff` -> FAIL (`20261020-123406-loadform`) |
| Efeito de feixe do jogo | `BeamWeaponSkillData.BeamVFX` = `CryoBeam_VFX`, um prefab ativo; host `sent=56`, cliente `applied=68`, `game=1/0/0`, `fallback=0`; PASS ambos (`20261020-133051-beamgame`); `-BeamOff` -> FAIL ambos (`20261020-133207`), `-GameBeamOff` -> host PASS/cliente FAIL `fallback=68` (`20261020-133320`) |
| Bosco espelhado | host `sent=164`; cliente `recv=173 spawned=1 statesApplied=194 renderers=3 miss=0`; PASS ambos (`20261020-134658-bosco`); `-BoscoOff` -> FAIL ambos (`20261020-134912-bosco`) |
| Aparência da classe host | cliente `ActivateSkin ok dwarf=0 meshes=4`, `applied=1` com host classe 0 / local 1; PASS ambos (`20261020-030131-skin`); `-SkinOff` -> FAIL `applied=0 meshes=0` (`20261020-030403-skin`) |
| Teste prolongado de 10 minutos | PASS ambos após 600 s da liberação; 2900/2915 inimigos, 618 mil snapshots (3671 perdidos), 928 projéteis; nenhuma exceção/limite de snapshot/desconexão; salvamentos restaurados (`20261020-040552-soak`). Correção de criação: `fail=0` em 3921 criações |
| Paridade de criação de espelhos | Antes `fail=29/50`; após `Register` idempotente em `SpawnMirror`: `fail=0 null=0 noEntry=0 noPtr=0`. Mortes locais bloqueadas (`OnDiePrefix`, limite de vida): cliente `20261020-043000-soak` com `localDie=0 miss=0` em 624 criações / 580 mortes; `blocked local mirror death` registrado |

**Ressalvas claras:** a estrutura **força** fim de etapa/partida (`TriggerStageEnd`, `TriggerCoreRunOutro`), permitindo medir em cerca de 90 s em vez de minutos; nunca se observou etapa terminar *sozinha*. Compras/cartas por dados de teste escolhendo botões específicos, não humanos. Painel IMGUI pressionado em coordenadas fixas; não clicado por pessoa nessa execução. Sem suíte de comando único: inicializador é ferramenta local, não parte de repositório.

**Ressalva visual (2026-10-20):** teste verifica estrutura/cliques, não pixels. Pelo caminho canônico de menu, **imagens** uGUI clonadas não aparecem (arte atravessa, texto fraco); aparência quebrada embora lógica verificada. Use botão do menu (`coop-run.ps1 -Menu -Test menu`) para QA visual; atalho `-cooplobby` é inválido para isso, pois cria tela antes da entrada e canvas ativo não desenhado. Ist/Soll e evidências: [STATUS.md](STATUS.md).

## <a id="how-to-play"></a>Como jogar

Não distribuído. Sem instalador ou Steam. Use cópia do jogo, nunca instalação Steam, com Steam ativo e mesma compilação nos dois lados. Inicie ambas; pressione **Host** numa e **Join** noutra, com endereço host (127.0.0.1 no mesmo PC, IP LAN em outros; UDP 9050 padrão). F8 oculta. Ambos chegam à sala: host define tipo, setor/nó, perigo, cliente vê ao vivo e escolhe classe/mod; host inicia após pronto. Cada um informa carregamento; mais rápido espera ("Fertig geladen - warte auf Spieler 2") até ambos, então começa. Estrutura mantém `-coophost` / `-coopclient` nos outros testes e painel separado `-Ui`.

## <a id="known-issues"></a>Problemas conhecidos

O que o jogador perceberia hoje:

- **Sala semitransparente e pouco legível.** Painel/fundo/botões não desenhados, tela da missão atravessa, texto fraco. Botões funcionam. `-LobbyIMGUI` legível. Defeito de renderização, não lógica ausente.
- **Ainda sem convite Steam.** Painel LAN/IP direto, sem retransmissão/convites; para internet, porta UDP host acessível (9050 padrão).
- **Balas do parceiro podem ser invisíveis.** Criadas como projéteis reais reutilizáveis, shader real, mas desenho não *comprovado*: todas verificações internas (visibilidade, callbacks, leitura de quadro) inutilizáveis nesta compilação. **Granadas espelhadas** inclusive sem posse (equipadas ao começar), flashes seguem `FlashSettings`. Vida inimiga segue host; cliente só exibe dano próprio imediato, por decisão.
- **Inimigos só perseguem host.** Cliente recebe dano ao entrar no enxame, mas não atrai. Exige segundo `Player` real no host, não simples troca de alvo.
- **Arma segurada não mostrada.** Aparência da classe aplicada; sem modelo separado de arma, representada por projéteis/feixes/torres. Projeto do jogo, não sincronização ausente.
- **Objetivos de círculo não contam parceiro.** Progresso espelhado, mas host só reconhece um jogador ali.
- **Mastery e equipamentos não testados**, perfil sem modo desbloqueado nem equipamento.
- **Empréstimo não persiste.** Cliente usa desbloqueios host com gravação bloqueada; devolve no fim e grava perfil próprio + ganhos. Decisão, não bug: ambos guardam ganhos próprios, desbloqueios da sessão vieram do host.
- **Execute da cópia**, nunca instalação Steam; mantenha Steam aberto.

## <a id="next-steps"></a>Próximos passos

Primeiro, **estabilidade visual**: corrigir/substituir imagens da sala para painel opaco/legível, capturar conexão e sala pelo caminho canônico. Lógica/testes passam; pendência é desenho. [STATUS.md](STATUS.md).

Ordem adequada:

1. **Visuais de combate restantes:** apenas oráculo externo de desenho de projéteis (posicionar espelho diante da câmera, comparar capturas). Flash da torre, `BeamVFX` contínuo e Bosco feitos; arma segurada não aplicável. Equipamento de granada controlado pelo host: receptor equipar granada adotada é intencional, sem variante de equipamentos distintos.
2. **Agressividade para segundo:** idealmente segundo `Player` real no host, ou comprovar primeiro que espelho não congelado escolhe cliente sozinho.
3. **Regras de objetivos pedidas:** círculo mais rápido com ambos, broca exigindo ambos, cápsula única com artefato individual, Bosco por jogador (espelho pronto, regra não).
4. **Cosméticos:** aparência de classe verificada; modelo explícito da arma não aplicável.
5. **Sala/convite Steam por último** (Spacewar 480 usual para retransmissão gratuita). Painel LAN/IP pronto; Steam exige autorização explícita e segunda conta/sessão, ficando por último.

Duas práticas economizam tempo: medir antes de projetar (mais de um bug óbvio era dado de teste) e fornecer controle negativo que precisa falhar em toda alteração; caso contrário, aprovação só prova que o teste pode passar.
