# <a id="lobby-ui-and-late-visual-mirrors"></a>Sala, interface e espelhamentos visuais posteriores

> Parte das notas de trabalho de Deep Rock Galactic: Survivor. Extraída literalmente de `NOTES.md` em 2026-10-20 (linhas 3399-3840), sem mudanças de conteúdo no original.
> Estado atual e Ist/Soll: [../STATUS.md](../STATUS.md). Índice: [../NOTES.md](../NOTES.md).

## <a id="turret-visual-mirror-2026-10-20"></a>Espelhamento visual da torre (2026-10-20)

A torre não é projétil nem chamada `WeaponSpawnTurret.OnSpawn` no recurso testado: `SpawnWeaponSkill_TurretThumper` cria `WeaponSpawnThumperTurret`, que sobrescreve `OnSpawn` e `DeSpawn`. Aplicar patches no virtual base e na sobrescrita juntos causa a falha 0xc0000005 documentada; o hook fica em `SpawnWeaponHandler.Spawn`/`Despawn`.

- **Host:** postfix de `Spawn(Vector3)` registra tratador e habilidade de criação e observa lista pública `activeSpawns`. Quando a instância aparece, envia `TurretSpawn` (33, ID/habilidade/posição/vida); `TickHostState` envia `TurretState` (34, posição quantizada + orientação horizontal compactada, 4 Hz); `Despawn` envia `TurretDespawn` (35). A varredura chama `SpawnWeaponHandler.Spawn(player position)` diretamente porque arma de teste recém-equipada não recebe a atualização normal de implantação.
- **Cliente:** resolve habilidade, clona hierarquia e desativa todos os `WeaponHandler`/`Collider` do clone. `_turretTop` da habilidade é **null** no cliente (referência resolvida na instância criada); fonte visual tenta `animatingTop` da classe derivada, `TurretDeploymentPrefab` e torre local ativa. Nunca chama `OnSpawn`/`DoUpdate`, logo não atira nem causa dano.
- **Positivo** (`20261020-022442-turret`): host `sent=1 stateSent=56`; cliente `spawned=1 states=42 miss=14 prefab='Turret_THUMPER'`, `RESULT: PASS` nos dois papéis.
- **Negativo** (`20261020-022622-turret`, `-TurretOff`): ambos `sent=0 spawned=0`, `RESULT: FAIL`.
- **Limites:** clone é visual estático. Efeitos/animações de disparo, mira por parte e fonte exata do prefab ainda exigem trabalho; estados recebidos antes da fonte visual existir contam como `miss` (14), não falhas.

### <a id="turret-fire-vfx--client-side-added-still-blocked-on-the-host-firing-2026-10-20"></a>Efeitos de disparo da torre - cliente implementado, ainda bloqueado pelo disparo no host (2026-10-20)

O espelho cliente agora tem clarão luminoso real, não apenas pulso de escala:

- `CoopCombat.FlashAt(from, settings, skill)` é o caminho compartilhado de luz (o `Flash(e)` de disparo remoto também o chama); `CoopCombat.MuzzleAt(WeaponHandler, fallbackFrom)` resolve `WeaponHandler.data.FlashSettings` e `firePoint` do próprio clone e chama o mesmo `ImpactLightsManager`.
- `CoopTurret` guarda um `WeaponHandler` da hierarquia clonada (preferindo `ProjectileWeaponHandler`), chama `MuzzleAt` ao receber `TurretFire` e conta `FireFlashes` / `FireFlashMiss`. Veredito cliente `turretfire` agora exige `FireFlashes > 0`; pulso de escala sozinho não basta.
- `OnTurretShot` também busca `ProjectileWeaponHandler`s filhos; `weaponHandler`/`spawnWeaponHandler` da criação nem sempre é quem dispara. Agora só são registrados tratadores sem correspondência semelhantes a torres; tiros Bosco/drone não inundam mais o hook.

Medido (`20261020-125033-turretfire`, criação direta `SpawnWeaponSkill_TurretThumper`, início automático confiável):

```
host:   turret: spawn sent id=1 skill='SpawnWeaponSkill_TurretThumper' native='WeaponSpawnThumperTurret'
host:   turret: fire hook unmatched handler='Bosco_ProjectileWeaponSkill_Base' (x5)
host:   check: turretfire sent=0 recv=0 applied=0 flashes=0
client: turret: spawned id=1 ... prefab='Turret_THUMPER'
client: check: turretfire sent=0 recv=0 applied=0 flashes=0
RESULT: FAIL (both)
```

Espelhamento e criação continuam corretos, mas a torre Thumper criada diretamente pelo desenvolvedor nunca dispara: os únicos eventos `ProjectileWeaponHandler.ShootProjectileInDirection` são do Bosco. O caminho do cano no cliente está pronto, mas não exercitado; só roda quando host envia `TurretFire`.

**Sonda de campos (`20261020-125843-turretfire`): tratador inicializado, porém é um `WeaponHandler` simples.** A criação registra os campos reais:

```
turret: fields wh='Sub_ThumperWeaponSkill' swh='SpawnWeaponSkill_TurretThumper'
        wsd='Sub_ThumperWeaponSkill' owner=1 ext='SpawnWeaponSkill_TurretThumper' fire='FirePoint'
turret: child[0] type='WeaponHandler' data='Sub_ThumperWeaponSkill' dType='WeaponSkillData'
        proj=0 beam=0 lightning=0 expl=0 melee=0 ground=0 auto=0 enabled=1 owner=1 fire='FirePoint'
```

A criação direta está toda conectada; Thumper simplesmente não usa tratador de projétil/raio/explosão, e `OnShoot` tampouco é chamado pelo tratador simples. A batida real é o **callback de animação `OnReloadUpdate(t)`**, normalmente controlado pela recarga do tratador de criação. A criação direta de desenvolvimento não tem recarga ativa; callback nunca rodava.

**Correção e verificação (`20261020-131050-turretfire`, `20261020-131227-turretfire`).** A atualização de estado (`CoopTurret.OnUpdate`, já a 4 Hz no host) avança `ThumperClock` de 0..1 para `WeaponSpawnThumperTurret`, chama `OnReloadUpdate`, e `OnReloadFire` espelha batida como `TurretFire` (limite de 0,5 s). `ApplyFire` cliente usa `CoopCombat.MuzzleAt`, mostrando clarão real `ImpactLightsManager` no `FirePoint`; veredito `turretfire` exige `flashes > 0`.

```
positive 20261020-131050:
host:   turret: thump fire id=1 t=0.25 / 0.50 / ...
host:   check: turretfire sent=5 recv=0 applied=0 flashes=0
client: check: turretfire sent=0 recv=5 applied=5 flashes=5
RESULT: PASS both

negative 20261020-131227 (-TurretFireOff):
both:   check: turretfire sent=0 recv=0 applied=0 flashes=0
RESULT: FAIL both
```

A atualização cliente mostra também `muzzle=5/5/...` junto ao cano do jogador, contando o clarão da torre separadamente do pulso de escala. O ouvinte `OnShoot` continua como alternativa inofensiva: preserva callback original e o limite de 0,5 s impede envio duplo se a recarga real também estiver ativa.

Limitações: conduzir `OnReloadUpdate` a 4 Hz é aproximação de desenvolvimento da cadência real de recarga; espelho é **visual**, caminho de dano do host inalterado; implantação natural não verificada. Não afirme intervalo exato da batida antes de testar a implantação natural.

### <a id="reliable-test-auto-start-2026-10-20"></a>Início automático confiável de testes (2026-10-20)

Clique da área de trabalho em janela de fundo não é confiável para automação. `-LobbyAutoPlay` reutiliza entrada automática testada + `UISplashForm.AdvanceFlow` + escolha de salvamento + `OnPlayButton`, com `-LobbyUIOff`; não constrói tela de sala, e `CoopAuto` conduz assistente. Formato:

```
coop-run.ps1 -Ui -Auto -Test <name> -LobbyAutoPlay -LobbyUIOff ...
```

`20261020-125033-turretfire` chegou à partida, criação e veredito em 1min18s; tentativas anteriores por clique expiravam após 3min48s sem entrar na partida. Só estrutura de testes alterada; jogo normal continua com botão Play real.

## <a id="co-op-lobby--l0-measurement-2026-10-20"></a>Sala cooperativa - medição L0 (2026-10-20)

Metas do marco G: sala real interna (tela própria), host define missão/dificuldade e cliente vê alterações ao vivo, cliente escolhe apenas **classe + modificador de classe**, host só inicia quando cliente pronto. Manter carregamento com "Fertig geladen - warte auf Spieler 2" tem prioridade explicitamente menor.

Sonda: `-cooplobbyprobe` / `-cooptest=lobbyflow` (`CoopLobby.cs`), uma instância host:

```
coop-run.ps1 -Deploy -Auto -Test lobbyflow -LobbyProbe -TestQuit both -Only host
```

Arquivo: `local/work/runs/20261020-053637-lobbyflow/`.

```
RESULT: lobbyflow PASS reason=sources=1 sectors=5 nodes=6 hazards=0 classes=5 mods=15
  hide=ok handlers=8 errors=4 fallbacks=1 driveErrors=0 launched=1 role=host
```

Observações do log:

- **Fonte no menu: `UIPlaySelectForm.runSettingsManager` + `form.missionRoadManager`.** `rs.MissionRoadState` é null em Play; só atribuído após escolher missão principal. `missionRoadManager.GetMissionRoadState(Elimination)` / `.EliminationState` retorna caminho ativo: **5 setores x 6 nós**, cada qual com `Data.Biome`, `IsLocked`, `MinHazIndex`, `IsCompleted()`. É o listado na sala.
- **`rs.GetHazardLevels()` gera NRE no menu** antes de escolher bioma (`lobbyflow: step=rs.GetHazardLevels failed ... NullReferenceException`). Índice de perigo 0 funciona por `OnHazLevelNext(0)` com página aberta. Ler lista após etapa de nó (ou botões da própria página), não ao pressionar Play.
- **`form.SetVisibility(false, true)` não desativa formulário** (`hide=ok hidden=0`); tratador continua executando enquanto oculto. Sala precisa **cobrir** assistente com superfície própria em tela cheia, não ocultá-lo por essa chamada.
- **Caminho medido:** `StartMainMissionsFlow` -> `OnMainMissionSelect` -> setor -> classe -> artefato de classe -> `OnHazLevelNext` -> `UILoadingForm`. `OnMainMissionSelect`, `OnClassPageNext`, `OnClassArtifactPageNext`, `OnHazLevelNext` funcionaram.
- **`OnMissionSectorClick` gera NRE** tanto com `MissionSectorState` do gerenciador quanto com `sectorState` do botão (4 erros). Caminho correto é `UIMissionSectorButton.OnButtonClick`: sonda pressionou `MissionSectorButton_1`, avançando à página CLASS (índice 4). Página de setor é **combinada**: mantém abas e adiciona `MissionNodeButton_01..06` e linhas `UIMutatorSetEntry` só de exibição. Primeiro nó escolhido por padrão; página de nó pulada, tratador não exercitado.
- Assistente transfere a `UILoadingForm` **antes de existir `GameController`**; sonda conta como `launched=1 why=loadingform`. Neste caso, carregamento espera entrada (ficou 80 s aberto em execução anterior). Marco precisa também **continuar** formulário, não apenas mantê-lo visível.
- Listas de classe/modificador do cliente vêm dos recursos ativos `ClassData` / `ClassArtifactData`, filtrados por `SaveDataManager.IsClassUnlocked` / `IsUnlocked` (perfil adotado do host, I1). Medidos **5 recursos de classe e 15 de modificador**; primeira classe liberada DRILLER, primeiro modificador `ClassArtifactData_Driller_Interrogator`.

Deduções de projeto:

- Sala usa **caminho dos botões** para missão/setor/nó (`OnButtonClick` do jogo); pode usar tratadores para classe/modificador/perigo. Botões são comprovados para todas as escolhas.
- Tela da sala **cobre** `UIPlaySelectForm`, não a oculta.
- Perigos lidos após nó; ao pressionar Play, só missão/setor/nó garantidos.
- Escolher classe e modificador é exatamente o exposto ao cliente; missão, setor, nó, bioma, perigo, mutadores pertencem ao host. Aparência/arma inicial seguem modificador.

Desconhecidos declarados:

- Se `OnMissionSectorClick` funciona com outro estado (por exemplo, da página atual). Desnecessário com botões funcionando, mas seria API mais limpa se corrigida.
- Por que carregamento espera entrada aqui (continuação automática versus entrada obrigatória). Marco começa sondando `UILoadingForm.Show`/`SetVisibility`/`OnInput`.

### <a id="l1--protocol--readystart-gate-2026-10-20"></a>L1 - protocolo e barreira de prontidão/início (2026-10-20)

Pacotes **38 `LobbyState`, 39 `LobbyChoice`, 40 `LobbyStart`** em `CoopNet.cs`; máquina de estados e barreira em `CoopLobby.cs` (`-cooplobbystate`, `-cooptest=lobby-state`). Teste usa ambas no menu principal pelo painel de entrada, sem assistente nem partida.

**Positivo** (`20261020-054247-lobby-state`, `-Ui -Lobby -Test lobby-state`):

```
host:   RESULT: lobby-state PASS reason=host rev=2 blockedPeer=1 blockedStale=1 allowed=1
        choiceRecv=2
client: RESULT: lobby-state PASS reason=client state=2 choice=2 start=1 rev=2
        stateRecv=2 choiceSent=2
```

Sequência: host `rev=1` -> `TryStart` bloqueado por `peer-not-ready` -> cliente escolhe em `rev=1` (ENGINEER / `ClassArtifactData_Engineer_Maintenance`) -> host muda para `rev=2`, `hazard=2` -> `TryStart` bloqueado por `stale-rev` (prontidão ainda da revisão 1) -> cliente escolhe em `rev=2` -> `TryStart` permitido -> `LobbyStart` rev=2 seed=20261017 -> cliente recebe.

**Negativo** (`20261020-054515-lobby-state`, `-LobbyNoReadyGate`):

```
host:   RESULT: lobby-state FAIL reason=ready-gate-off start allowed before peer ready, rev=1
client: RESULT: lobby-state FAIL reason=timeout after 120s
```

Barreira não é vazia: desativada, host inicia antes do cliente pronto e teste falha.

Dedução: repetição da revisão basta para invalidar prontidão antiga após mudança do host. Início é autoritativo: cliente não inicia pela própria escolha, espera `LobbyStart`. Pendências L2/L3: validar classe/modificador contra perfil do host, tela real e passar escolhas ao assistente.

### <a id="l2--the-real-lobby-screen-2026-10-20"></a>L2 - tela real da sala (2026-10-20)

Tela é **clone do canvas raiz da interface do jogo**, removidos todos os filhos, com objetos clonados `Image`/`UIButton`/`TextMeshProUGUI` para painéis, botões e rótulos (`CoopLobbyUI.cs`). Canvas ScreenSpaceOverlay, `sortingOrder = 1000`, cobre `UIPlaySelectForm`, bloqueia raycasts. Assistente não é conduzido enquanto ativa (`CoopAuto.DriveWizard` retorna cedo).

**Positivo** (`20261020-063928-lobby-ui`, `-Ui -Lobby -Test lobby-ui`):

```
host:   RESULT: lobby-ui PASS reason=host active=1 sectors=5 classes=5 mods=3 hazard=1
        start=1 rev=2
client: RESULT: lobby-ui PASS reason=client active=1 stateRecv=2 choiceSent=6 start=1 rev=2
```

Sequência: host abre em `rev=1`, clica perigo H2 -> `rev=2`; cliente recebe, escolhe ENGINEER / `ClassArtifactData_Engineer_Maintenance`, pressiona READY; host vê `peerRev=2`, permite START; `LobbyStart` rev=2 chega. Tela expõe 5 setores, 6 nós, 5 classes, 3 modificadores da classe local e 5 perigos; dados de `form.missionRoadManager`, lidos após carregamento assíncrono.

**Negativo** (`20261020-063812-lobby-ui`, `-LobbyUIOff`): ambas permanecem `role=solo` e expiram, `RESULT: ... FAIL`. A tela é efetivamente testada.

Fatos medidos de implementação (custaram várias execuções; preservar):

- **`AddComponent<T>` não funciona nos tipos de interface.** Armazenamento genérico Il2CppInterop (`MethodInfoStoreGeneric_AddComponent_Public_T_0`) lança exceção no inicializador para `RectTransform`/`Canvas`/`Image`/`TMP`. `Instantiate` do canvas raiz, imagens, botões e textos do jogo funciona e é usado. Clone mantém `CanvasScaler`, `GraphicRaycaster` e EventSystem da cena; só Canvas/CanvasScaler/GraphicRaycaster sobrevivem ao filtro de componentes.
- `CanvasGroup.blocksRaycasts` é **somente leitura** na interoperabilidade; CanvasGroup raiz é removido pelo filtro, não configurado.
- **Fluxo inicial precisa escolher salvamento.** `UISplashForm.AdvanceFlow()` sozinho chegava a `SAVE_SLOT`, sem escolher; `SaveDataManager` vazio e Play lançando `NullReferenceException`. `OnSaveSlotSelected(ESaveSlot.Slot1)` funciona; perfil de teste usa Slot1.
- **Pressionar Play precisa dos gerenciadores e estabilização.** Espere `UIMenuSplashForm.saveDataManager.SaveData != null` e `metaManager != null`, mais 2 s, depois chame `UIMenuSplashForm.OnPlayButton()` diretamente.
- **Caminho de missões carrega de forma assíncrona.** Um `ReadMenuData` imediato viu `sectors=0`. `CoopLobby.EnsureMenuData` tenta na thread principal até haver setores; só então envia primeiro `LobbyState`. Painel reconstrói quando `UiDataReady` muda.
- **Ações dos botões:** `UnityEngine.UI.Button.onClick` não aceita `Action` gerenciado diretamente. `DelegateSupport.ConvertDelegate<UnityAction>(new Action(...))` + `onClick.AddListener` funciona; L2 chama o mesmo `Button.onClick` alcançado por ponteiro. `UIButton` original do clone é destruído e evento substituído; Back clonado não aciona o Back do jogo.

Desconhecidos declarados:

- Tela conferida estruturalmente e por cliques programáticos. Clique físico separado não testado; usa mesmo `Button.onClick`, mas caminho EventSystem/ponteiro não foi comprovado independentemente.
- `ScreenCapture.CaptureScreenshot` não gerou arquivo, tampouco exceção. Revisão visual de captura/layout pendente; recursos vêm do jogo e teste comprova atividade/interação.
- Classe padrão do host veio de `runSettingsManager.selectedClass` (Engineer), não fixa. Ambos escolheram Engineer/Maintenance por coincidência no positivo; classes diferentes de ponta a ponta ficam para L3.

### <a id="l3--start-through-the-real-wizard-2026-10-20"></a>L3 - iniciar pelo assistente real (2026-10-20)

START de L2 agora conduz `UIPlaySelectForm` com escolhas da sala e cria partida real. Teste `-cooplobbystart` / `-cooptest=lobby-start`, execução `20261020-064751-lobby-start`, `-Ui -Lobby -Test lobby-start`:

```
RESULT: lobby-start PASS host   active=1 sectors=5 classes=5 mods=3 hazard=1 start=1 rev=2
  run=1 dwarf=0 mod='ClassArtifactData_Driller_Interrogator'
RESULT: lobby-start PASS client active=1 stateRecv=2 choiceSent=6 start=1 rev=2
  run=1 dwarf=1 mod='ClassArtifactData_Engineer_Maintenance'
saves: restored and verified (14 files, canary removed)
```

- **Configurações de ambos são as escolhidas pelo host:** `main=0 biome=0 sector=0 node=0 hazard=1`; host Driller/Interrogator, cliente Engineer/Maintenance. Mesma fase, classes diferentes.
- **Controlador segue páginas, não índices de etapas.** Ordem observada `CAMPAIGN -> CLASS -> NODE -> CLASS -> ARTIFACT -> HAZ`: reutilizou missão/setor anteriores e revisitou classe. Cada atualização lê botões ativos e pressiona objeto escolhido: setor/nó por nome, classe por anão, modificador por `UIClassArtifactButton.data.name`, perigo por `UIHazLevelButton.hazLevel`. Botões L0/L2 são único caminho confiável; nunca chama API de tratadores diretamente.
- **Carregamento:** assistente transfere a `UILoadingForm`; automação continua por `UILoadingForm.OnLoadingComplete()` quando `waitingForInput` verdadeiro. Permite chegar a `GameController.StartGame` e barreira `CoopLoad`. Normalmente uma tecla faz isso; trabalho P2 manterá "Fertig geladen - warte auf Spieler 2" em vez de continuar logo.
- **Validação host:** `HostStartClicked` confere `PeerDwarf`/`PeerClassMod` do cliente por `SaveDataManager.IsClassUnlocked`/`IsUnlocked` antes de `LobbyStart`. Tela cliente já filtra; proteção adicional no protocolo.
- **Temporização:** `lobby-start` espera `ProbeState.Gc != null` mais 5 s; `run=1` representa fase real, não formulário/pacote.
- **Pendente:** revisão visual/layout. Funcionalmente comprovado (dados, atualizações, prontidão, início, `Button.onClick` programático); clique físico e captura sem prova independente. Lista de polimento visual permanece: efeitos de disparo da torre, feixe, arma segurada, entidades/animações Bosco/torre, granada somente visual.

### <a id="p2--loading-screen-hold-2026-10-20"></a>P2 - retenção na tela de carregamento (2026-10-20)

Requisito implementado. `CoopLoad` guarda `UILoadingForm` ativo enquanto a partida está armada, pausa em `StartGame`, reexibe o mesmo formulário sobre o jogo pausado, define `tipText = "Fertig geladen - warte auf Spieler 2"`, limpa indicação de pressionar tecla e oculta só ao liberar barreira. Controle negativo: `-cooploadformoff` / `-LoadFormOff`.

Positivo `20261020-123303-loadform`, PASS em ambos:

```
check: load started role=host delay=0.0s timeout=30s
check: load form shown=1 role=host text='Fertig geladen - warte auf Spieler 2' paused=1
check: load held role=host paused=1 form=1 delay=0.0s
check: load released role=host via=both held=1.4s peer=1 timeout=0 paused=1 wait=1
RESULT: loadform PASS reason=host ... run=1 wait=1
```

Negativo `20261020-123406-loadform` (`-LoadFormOff`): ambos `FAIL reason=loadform wait=0`, `check: load held ... form=0`. Teste não vazio.

Medições/deduções:

- Formulário real sobrevive à conclusão do carregamento; `SetVisibility(true, true)` reexibe, `tipText` funciona. Sem sobreposição própria.
- `locPressAnyKey` é `LocalizedString` de Unity Localization, não TMP; `pressAnyKeyText.text = ""` oculta corretamente.
- Retenção até `PeerReady` do host, exatamente diferença de carregamento do parceiro (1,4 s). Jogo pausado atrás; fase nunca aparece durante espera.
- `loadform` espera `ProbeState.Gc` + 5 s e exige `CoopLoad.WaitShownEver`: PASS comprova partida real **e** tela de espera exibida.
- Layout exato (título/logotipo, posição da dica) ainda sem revisão visual; log comprova visibilidade e texto definido.

## <a id="bosco-mirror--done-2026-10-20"></a>Espelhamento Bosco - concluído (2026-10-20)

Ambos têm `Bosco` próprio ativo; cliente usa o seu como fonte visual do companheiro do host.

- Pacote 41 `BoscoState` a 10 Hz: posição x/y/z, yaw (ushort), `state`, `speedFrac`, indicadores de frenagem/ativo. Host acha `Bosco` próprio (`player.Pointer == Player.Pointer`, ativado), envia posição/orientação/estado/velocidade/indicadores.
- Cliente esvazia fila, clona o **próprio** Bosco uma vez, desativa componente `Bosco`, `WeaponHandler`s e `Collider`s, mantém `Animator`, aplica posição/orientação, define `ID_SPEED`/`ID_BRAKE`; `ID_SALUTE` aciona na transição de estado. Clone só visual, `CoopPuppetBosco`; Bosco local continua visível.
- Positivo `20261020-134658-bosco`: host `RESULT: bosco PASS sent=164`; cliente `recv=173 spawned=1 statesApplied=194 renderers=3 miss=0`; inicializador `RESULT: PASS`.
- Negativo `-BoscoOff` `20261020-134912-bosco`: ambos FAIL `sent=0 recv=0 spawned=0 statesApplied=0 renderers=0`; inicializador `RESULT: FAIL`. `CoopBosco.Tick` executa `MaybeTest` mesmo desativado, produzindo veredito Bosco, não timeout.
- Limites: animação aproximada (velocidade/frenagem/saudação, sem parâmetros completos de inclinação/vertical); clone sem dano/comportamento Bosco host. Bosco cliente segue autoritativo para ações próprias. Revisão visual pendente.

## <a id="co-op-ui-pass--back-fixed-marker-rebuilt-verified-2026-10-20"></a>Revisão da interface cooperativa - BACK corrigido, marcador reconstruído (VERIFICADO, 2026-10-20)

Decisões: LAN/IP direto e marcador na partida; **sem painel do parceiro**; prova visual por capturas externas da janela. Plano completo em `~/.commandcode/plans/coop-ui-plan.md` (privado).

**Implementado:**

- **BACK na sala não é mais inoperante.** `CoopLobby.LeaveLobby()` define `LeftLobby`; `CoopLobbyUI.Tick` recusa reconstruir enquanto definido. Pacotes/prontidão/início continuam (`TickUiWithoutScreen`), então cliente que pressionou BACK recebe `LobbyStart`; só a tela fecha. Reinicia em `OnLobbyOpen` / entrada no menu / Host/Join explícitos.
- **Marcador (`CoopIndicator`):**
  - estados explícitos `off | no-remote | no-camera | stale | suppressed | onscreen | offscreen | downed`;
  - símbolo direcional (`<<`, `>>`, `^^`, `vv`) e distância em metros;
  - parceiro caído: marcador vermelho `DOWN`;
  - parceiro obsoleto: `CoopNet.RemoteStateSeq` marcado na thread principal; após 2 s sem `PlayerState`, desaparece em vez de deixar fantasma;
  - suprimido durante sala, retenção de carregamento, START ou tela modal pausada;
  - limites de `CoopScreen.ClientSize()` (Win32 `GetClientRect`), não `Screen.width/height`;
  - só `CameraController.instance.cam` aceito: alternativa antiga `Camera.main` é câmera da interface nesta compilação e fazia todo remoto parecer fora da tela;
  - `-coopindicatoroff` é controle negativo.
- **Arquivos novos:** `CoopScreen.cs` (tamanho visível do cliente), `MarkerMath.cs` (geometria pura: dentro da tela, inversão atrás da câmera, interseção da borda). Separada do desenho para teste sem quadro.

**Limites de interoperabilidade encontrados compilando (não tentar de novo):**

- `Mathf.Rad2Deg`, `GUIUtility.RotateAroundPivot`, `GUIStyle(…)` (só construtor `IntPtr`), `TextAnchor` (precisa `UnityEngine.TextRenderingModule`) e `GUI.DrawTexture` (nem sobrecarga 2 nem 4 argumentos) estão **ausentes**. Marcador desenha símbolo textual em `GUI.Box` padrão, sem textura ou rotação.

**Compilação:** `dotnet build -c Release` aprovada (0 erros, 7 avisos anteriores).

**Verificado em duas instâncias (2026-10-20):**

- **Marcador positivo** (`20261020-172040-indicator`, `-Test indicator -CameraOff`), PASS em ambos:
  ```
  host   RESULT: indicator PASS state=offscreen onscreen=2 offscreen=1303 selfOnScreen=1
         downed=0 noCamera=0 errors=0 maxDist=23,1 enabled=1
  client RESULT: indicator PASS state=offscreen onscreen=0 offscreen=1324 selfOnScreen=1
         downed=0 noCamera=0 errors=0 maxDist=22,3 enabled=1
  ```
  Parte dentro da tela é verificada no anão **local** (`selfOnScreen=1`), acompanhado pela câmera; parte remota é amostra real fora da tela. Exigir remoto visível mediria o cenário de teste: primeira tentativa falhou por isso com `onscreen=0`.
- **Marcador negativo** (`20261020-172202-indicator`, `-IndicatorOff`), FAIL em ambos: `state=off … enabled=0 maxDist=0,0`; marcador realmente testado.
- **BACK** (`20261020-172235-lobby-back`), PASS em ambos: `RESULT: lobby-back PASS back=1 active=0 left=1 peer=1`. Antes a tela reconstruía no próximo ciclo; assinatura de falha agora `active=1`.
- **Regressão da sala** (`20261020-172313-lobby-ui`), PASS em ambos: `host active=1 sectors=5 classes=5 mods=3 hazard=1 start=1 rev=2`.
- **Regressão do início pelo assistente** (`20261020-172401-lobby-start`), PASS em ambos: `run=1`, host Driller/Interrogator, cliente Engineer/Maintenance, mesmo `hazard=1`.
- Toda execução restaurou e conferiu salvamentos; inicializador encerrou ambos os processos.

Pendentes nesta revisão: estados obsoleto/interrompido e caído não exercitados (invencibilidade e parceiro conectado todo o teste); próxima medição dedicada com `-NoGod` e silêncio forçado. Oráculo de captura externa (U6) ainda não escrito.

## <a id="lobby-images-marker-states-and-connect-screen--closed-2026-10-20-evening"></a>Imagens da sala, estados do marcador e tela de conexão - encerrados (noite de 2026-10-20)

### <a id="why-the-cloned-images-were-invisible"></a>Por que Images clonadas eram invisíveis

Medido em log pós-ativação (`check: lobby postactivate crComp ...`): após `Destroy` adiado, todo clone de `CloneImage`/`StripExtras` ficava **sem Image** (`img0/cr1`), mas controle não filtrado mantinha (`img1/cr1`). CanvasRenderer sobreviveu; hipótese anterior de destruição dele estava errada. Testes de tipo (`c is T`, `IsInstanceOfType`) não funcionam em componentes devolvidos por `GetComponents<Component>()` pelo invólucro base `Component` nesta Il2CppInterop. Correção compara `.Pointer` nativo e resolve tipos preservados por `GetComponentsInChildren(Il2CppType.From(t))`. Segundo bug independente: canvas raiz esticado com âncoras 0/1 resulta em 0x0; agora recebe tamanho do cliente.

- Sonda `20261020-200837-lobbyhold`: amostras de cor desenhadas (quadrilátero simples colorido, material-modelo, sprite null). Manter sprite `Btn_Campaign_Background` renderiza quase preto; produção usa `sprite = null`.
- Captura de produção `20261020-202207-lobbyhold`: painel opaco, texto e botões, ambos os papéis.

### <a id="pixel-oracle"></a>Oráculo de pixels

`coop-shot.ps1 -VerifyPanel <png,...>` amostra área vazia (x 55-80%, y 56-64% da janela) e exige luminância média 8-22 e desvio <= 3. Calibração: captura boa média 13,2 / desvio 0,00; ruins conhecidas (arte da missão atravessando) média 56 / desvio 25-27, ambas falham. Script agora organiza host à esquerda e cliente à direita antes de capturar: com sobreposição, ambos os "papéis" eram a janela da frente.

### <a id="regressions-after-the-imageroot-size-fix-all-pass-on-both-roles-saves-restored-and-verified"></a>Regressões após corrigir Image/tamanho da raiz (todas PASS em ambos, salvamentos restaurados e conferidos)

| Teste | Execução |
|---|---|
| `menu` | `20261020-201108-menu` |
| `lobby-ui` | `20261020-201132-lobby-ui` |
| `lobby-start` | `20261020-201214-lobby-start` |
| `lobby-ui -LobbyUIOff` (negativo) | `20261020-201926-lobby-ui`: FAIL, `timeout after 420s` |

Log host de `lobby-start` contém `profile: read 'animator' failed`, já presente antes (como `20261020-064751-lobby-start`); sem relação com esta mudança.

### <a id="marker-stale--downed--test-marker"></a>Marcador `stale` / `downed` (`-Test marker`)

Opções: `-coopstatesilent=<s>` (cliente para `PlayerState` por `<s>` segundos, 6 s após barreira), `-coopdownself` (cliente chama `Player.Die` real aos 16 s, sem invencibilidade); inicializador `-StateSilent <s> -DownSelf`, sempre `-CameraOff` para parceiro ficar fora da tela. Host exige `stale>0`, `downed>=5` amostras e `recovered>=1` (saiu de `stale` para estado novo após retorno dos pacotes) em 45 s; veredito cliente só comprova ações solicitadas.

- Positivo `20261020-202736-marker`: host `state=downed stale=352 downed=5 recovered=1 enabled=1`; cliente `silenceSkipped=95 selfDowned=1 isDownedAtDeath=1`.
- Negativo `20261020-202927-marker` (`-IndicatorOff`): host FAIL `state=off stale=0 downed=0 recovered=0 enabled=0`.
- Primeira execução (`20261020-202527-marker`) teve host PASS e cliente FAIL: teste lia `CoopDowned.IsDowned` 16 s após morrer, quando anão já levantara. Corrigido para capturar no momento da morte, não afrouxado.
- Não coberto aqui: reviver na mesma execução (coberto na linha anterior de caído/reviver).

### <a id="connect-screen--test-connecthold"></a>Tela de conexão (`-Test connecthold`)

Normalmente desaparece cerca de um segundo após parceiro conectar. Teste a mantém aberta 20 s com parceiro conectado. `20261020-203105-connecthold`: `connect=1 hold=20s peer=1` em ambos; capturas mostram `PEER CONNECTED (0 MS) - OPENING THE MISSION MENU...`. A tela imprime caminho completo de `coop-join.txt`, incluindo usuário Windows; capturas não podem ser publicadas.

## <a id="partner-lost-mid-run-2026-10-20-night"></a>Perda do parceiro durante a partida (noite de 2026-10-20)

### <a id="measured-first--coopnopeerloss--the-old-behaviour-kept-as-baseline-and-negative-control"></a>Medido antes (`-coopnopeerloss` = comportamento antigo, preservado como referência e controle negativo)

Tratador só limpava `PeerConnected`; `HaveRemote` nunca redefinido. Cliente saindo após 20 s (`-Test disconnect -QuitAfter 20`), host sobrevivente mostrava `haveRemote=1`, representante na última posição, marcador `stale`, sem mensagem (`20261020-205716`, FAIL). Se saída durante escolha de nível, host congelava: `xpHold=1`, `timeAdvanced=0,0` por toda janela de 16 s (`20261020-210213`, FAIL); só saía pelo limite de 45 s. Detecção é timeout LiteNetLib (`reason=Timeout`, cerca de 5-10 s após processo morrer, pois jogo encerrado não envia desconexão).

### <a id="fix-cooppeerlosscs-hooks-in-coopnet-coopxp-coopshop-coopload"></a>Correção (`CoopPeerLoss.cs`, hooks em `CoopNet`, `CoopXp`, `CoopShop`, `CoopLoad`)

Na thread principal, ao detectar: `HaveRemote=false` (barreiras posteriores passam e ausência de parceiro conta como solo na regra de caído), libera imediatamente barreira de nível/loja/carregamento, remove representante, marcador vira `no-remote`, desenha aviso ("Partner getrennt - du spielst solo weiter" / "Host getrennt - der Run wird beendet"). Cliente não continua sem host; encerra por `CoreGameEvents.TriggerCoreRunOutro(ABORT)` após 6 s, salvo se tela final já aberta. Não reconecta; `PlayerState` posterior definiria `HaveRemote`, mas não há fluxo de reconexão.

Auxiliares: `-coopquitafter=<s>`, `-coopquitonlevelup` (não confirma nível, sai após 3 s), `-coopnopeerloss`; inicializador `-QuitAfter`, `-QuitOnLevelUp`, `-QuitterRole`, `-NoPeerLoss`. `-Test disconnect`: quem sai registra PASS e encerra; sobrevivente avalia (`haveRemote=0`, sem barreira, representante removido, `no-remote`, aviso; host vivo e tempo avançando; cliente `runEnded=1`; barreira ativa liberada em até 2 s da detecção).

| Caso | Execução | Resultado |
|---|---|---|
| Cliente sai, host sobrevive | `20261020-212227-disconnect` | PASS |
| Cliente sai ao subir nível, host aguardando | `20261020-212435-disconnect` | PASS, `holdReleasedAfter=0,0` |
| Host sai, cliente sobrevive | `20261020-214714-disconnect` | PASS, `runEnded=1` |
| Host força fim e depois sai | `20261020-214936-disconnect` | PASS (tela final aberta, sem segunda conclusão) |
| Negativo, host sobrevivente, `-NoPeerLoss` | `20261020-205716`, `20261020-210213` | FAIL |
| Negativo, cliente sobrevivente, `-NoPeerLoss` | `20261020-211301` | FAIL |

Aviso legível em captura externa (`CopyFromScreen`, janela host após perda). Limite IMGUI: `GUI.Box` padrão é translúcido com texto apagado sobre HUD; aviso usa fundo opaco, fonte maior (restaurada após desenhar) e três sobreposições do desenho.

### <a id="regression-after-the-change-all-pass-on-both-roles-saves-restored-and-verified"></a>Regressão após mudança (todas PASS em ambos, salvamentos restaurados e conferidos)

`xpsync` `20261020-213321`, `stage -StageEnd win` `20261020-213458`, `shop -StageEnd win` `20261020-213635`, `loadform` `20261020-213716`, `loadtimeout -Only host` `20261020-213833`, `lobby-start` `20261020-213914`, `lobby-back` `20261020-213942`, `marker` `20261020-214119`, `indicator` `20261020-214235`, `levelup -TestMinSec 120` `20261020-214453`.

Uma `levelup` falhou antes (`20261020-213147`, `timeout after 420s`): bot parou desde minuto 4 no enxame, nível 2, e segunda escolha nunca ocorreu; sem exceção nem perda de parceiro. Repetição imediata passou; registrado como posição instável do bot, não correção.

Linhas de log **não** novas: `profile: read 'animator' failed ... NullReference` (host, também antes da mudança no dia 20) e `loot: wallet credit failed` (cliente, também em 2026-10-19).

### <a id="not-covered"></a>Não coberto

Reconexão durante partida; Pause/ESC com parceiro conectado (não medido, primeiro item do teste manual); parceiro conectado que para de responder (só marcador `stale` medido; comportamento das barreiras não medido).
