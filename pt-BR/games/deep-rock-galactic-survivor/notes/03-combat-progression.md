# <a id="combat-progression-saves-and-run-mechanics"></a>Combate, progressão, saves e mecânicas de partida

> Parte das notas de trabalho de Deep Rock Galactic: Survivor. Extraído literalmente de `NOTES.md` em 2026-10-20 (linhas 1195–3398); conteúdo sem alterações.
> Estado atual e Ist/Soll: [../STATUS.md](../STATUS.md). Índice: [../NOTES.md](../NOTES.md).

## <a id="roadmap-current"></a>Roteiro (atual)

Um plano principal com a lista completa de trabalho restante e critérios PASS está em
`local/mod/DrgSurvivorCoop/PLAN.md` (privado). Ordem: A visuais de personagem → B visuais de combate →
C objetivos → D loja/melhorias → E correção do valor de saque → F incapacitação/reanimação → G interface + sala Steam → H contribuir de volta.

- **Marco A (sincronização de classe do personagem) — VERIFICADO.** Novo pacote `CharClass` (12): anfitrião envia `EDwarf`
  como byte; cliente armazena `HostDwarf`. Execução com duas instâncias: `check: char self=3 role=host` ==
  `check: char host=3 self=3 role=client`. **Visual da skin VERIFICADO (2026-10-20).** O bloqueio anterior era
  o boneco **antes da partida**: ele não tem componente `PlayerSkin`. Após iniciar a partida, o boneco é recriado
  e passa a ter um; assim, o reempacotamento tipado e `ActivateSkin(playerSkin, skinData, false)` funcionam.
  Execução `20261020-030131-skin` (`-SkinTest`, classe 0 do anfitrião / local 1): cliente `ActivateSkin ok dwarf=0
  meshes=4`, `check: skin ... applied=1 meshes=4`, PASS nos dois. Negativo `-SkinOff`
  (`20261020-030403-skin`): cliente FAIL `applied=0 meshes=0`. O caminho com `AddComponent` vazio não é
  usado. Detalhes completos em `PLAN.md`.
- **Marco C (sincronização de objetivos) — VERIFICADO.** Pacote `Objective` (13): anfitrião lê
  `LevelObjectiveTracker.Primary/SecondaryObjectives → ObjectiveProgress.Progress`, cliente espelha.
  Dois erros corrigidos: descoberta do rastreador percorrendo a cena (FindObjectsOfType retornava 0) e determinismo
  dos objetivos secundários (inicializar `UnityEngine.Random` antes de `SetupSecondaryObjectives`). Log:
  `check: objective recv=26 applied=2 miss=0`, tipos correspondem (ambos `COLLECT_POINTS` + `LEVEL_PICKUP`).
- **Indicador fora da tela (F parte 1) — VERIFICADO.** `CoopIndicator.cs` desenha um marcador "REMOTE" na
  borda da tela quando o anão remoto está fora da câmera (`check: indicator offscreen remote=… edge=…`).
- **Estado incapacitado (F) — código escrito, VERIFICAÇÃO BLOQUEADA por mudança no fluxo do assistente.**
  - Implementado: `CoopDowned.cs` (flag de incapacitação + detecção de remoto incapacitado pela vida sincronizada) e um prefixo
    Harmony em `GameController.OnPlayerDeath()` que impede o fim de jogo e marca incapacitação
    (`check: downed role=…`). Ainda não verificado porque a partida não inicia mais.
  - **Novo bloqueio:** o save avançou (partidas anteriores desbloquearam conteúdo), portanto o fluxo do assistente
    mudou: a página inicial agora mostra `UIMutatorSetEntry` ×6 (seleção de modificadores) e
    `UISetProgressButton_Mastery/Endless/Anomaly` agora estão disponíveis. `UIPlaySelectForm.StartMainMissionsFlow()`
    lança exceção (`Exception thrown by target of invocation`), e pressionar `UIMutatorSetEntry` não
    avança. O plano do assistente `CoopAuto` está desatualizado e precisa de engenharia reversa da etapa de modificadores,
    ou de reiniciar o save. A dispensa da abertura agora é feita no mod (`UISplashForm.AdvanceFlow()`), em vez
    do clique externo de mouse pouco confiável.
  - `MutatorSetEntry` fica em `UIMissionRoadPage`/`UIMissionNodePage`/`UIChallengeSetSelectPage`
    (campo `mutatorEntries`), portanto modificadores são uma etapa de seleção do percurso de missão, não uma aba da página inicial.
- **Ambiente de teste: classes diferentes + opção de invencibilidade — VERIFICADO.**
  - Página de classe vem *antes* da página de artefato de classe (o plano antigo de `CoopAuto` as invertia; corrigido).
  - Save 3 tem apenas **Scout** desbloqueado (Gunner/Engineer/Driller `[unavailable]`). Forçar uma classe
    bloqueada no assistente trava a página de artefatos (todos ficam `[unavailable]`).
  - Correção: anfitrião mantém Scout; cliente substitui por **Engineer** via `RunSettingsManager.SetClass(EDwarf)`
    *depois* da etapa de artefato (índice 6 do plano), não durante o assistente. Verificado:
    anfitrião `check: char self=3`, cliente `check: char host=3 self=1` (Scout=3, Engineer=1), ambos `alive=True`.
  - Opção `-coopnogod` desativa a fixação `currentHp=100000` do bot → bot sofre dano e morre
    (`hpDrops=6, alive=False`), pré-requisito para o teste de incapacitação. Inicializador: `coop-run.ps1 -NoGod`.
  - Substituir a classe exige `UIClassSelectPage.runSettingsManager`; `RunSettingsManager` é um objeto
    Il2Cpp simples (não MonoBehaviour), acessível pelo campo da página, não por `FindObjectsOfType`.
- **Sistema de armas / melhorias / efeitos de status — MAPEADO (base do marco B).**
  - `WeaponHandler` (MonoBehaviour) é a base; subclasses: `ProjectileWeaponHandler` (AutoCannon,
    AlternatingProjectile, Boomerang, ImpactAxe, Lok1, StubbySMG), `BeamWeaponHandler` (LocalSpaceBeam,
    RotatingBeam→SludgePump, ShardDiffractor), `GrenadeWeaponHandler` (Groundzone, LeadBurster,
    PlasmaBurster, Trap), `OrbitingDroneWeaponHandler` (CarrierDrone), além de CoilGun, LinkProjectile,
    RocketSwarm, Trail, Spawn, StunExplosion, WaveCooker, AttachedGroundzone. O caminho de IA/torreta é
    `AIWeaponHandler` (MonoBehaviour, separado de `WeaponHandler`).
  - Melhorias são dados (hierarquia `WeaponSkillData`/`ASkillData`; por exemplo `BeamWeaponSkillData`,
    `ProjectileWeaponSkillData`→`AlternatingProjectileSkillData`, `ArtifactSkillData`). Dados de habilidade de arma
    expõem `GetStatusEffectData()` → `List<StatusEffectData>`.
  - `EDamageType` = KINETIC, CRYO, FIRE, ACID, PLASMA, ELECTRICAL. `EStatusEffect` = NONE, SLOW, STUN,
    BURN, ELECTROCUTE, CORRODE, FROZEN. Portanto, "arma + melhorias → dano de fogo" é exatamente
    `EDamageType.FIRE` + `EStatusEffect.BURN`, aplicado no anfitrião e transportado no projétil
    (`Projectile.Shoot(... statusEffects, EDamageType damageType, ...)`).
  - **Conclusão de sincronização:** efeitos são calculados pelo anfitrião (dano + status aplicados no anfitrião); o cliente
    já espelha o *resultado* (vida/morte dos inimigos pela sincronização de inimigos). O que NÃO é sincronizado é o *visual*
    (partículas de projétil/boca de arma/granada/torreta/status) — esse é o trabalho de eventos de criação do marco B.
- **Assistente automático CORRIGIDO (causa raiz encontrada).** O assistente travava na tela Hauptmissionen: pressionar o
  cartão de campanha `UIChallengeSetButton_MissionRoad` não fazia nada e a página nunca avançava (o mod então
  o pressionava a cada 2 s como alternativa de contingência, piorando a aparência do problema).
  - Causa raiz: o mod dispensava a abertura da editora por conta própria com `UISplashForm.AdvanceFlow()`. O fluxo da
    abertura inclui `ShowSaveSlotSelectorIfNeeded` (seleção/carregamento do save), portanto pulá-lo deixava a
    campanha parcialmente inicializada; `StartMainMissionsFlow()` então lançava NullReferenceException dentro de
    `UIMissionSelectPage.Show(...)`, e a página não podia mudar. (O próprio log do mod só identificou a exceção
    depois que `Cause()` desembrulhou `TargetInvocationException`.)
  - Correção: **nunca avançar a abertura pelo mod.** Dispensá-la com clique real do mouse. Então o driver de API
    volta a funcionar sem alterações. Verificado ponta a ponta: anfitrião `IN RUN after 20 steps`, cliente
    `IN RUN after 19 steps`, ambos `peer connected`, `alive=True`, `check: char self=0` / `host=0 self=1`.
  - Evidência de que a causa é a abertura, não o cartão: com clique real na abertura, o cartão de campanha
    avançou normalmente e o assistente percorreu `UIMissionRoadButton_` → `MissionSectorButton_` →
    `MissionNodeButton_` → `ClassSelectButton_` → `ClassArtifact` → `HazLevelButton` → IN RUN. Uma reprodução
    de mouse real gravada (`tools\coop-wizard.ps1`) chegou a IN RUN da mesma forma, enquanto `AdvanceFlow` não.
  - O fluxo de páginas do assistente agora é registrado pela assinatura dos botões (`auto: wizard page: …`), tornando a sequência
    visível no log, em vez de presumida.
  - `UIMutatorSetEntry` serve apenas para exibição (`Show`/`Hide`, realce ao passar por `OnSelect`); não tem ação de clique, portanto
    nunca deve ser pressionado como alternativa de contingência.
  - Recompensas de subida de nível são atendidas automaticamente por `ServeLevelUp` do mod (no ramo durante a partida do driver automático);
    ativar `-coopwatch` agora também dispensa a abertura, permitindo automatizar recompensas sem o driver do assistente.
- **Incapacitação / reanimação (F) — código pronto, conclusão da reanimação ainda não observada.** `CoopDowned` marca incapacitação e um
  prefixo em `GameController.OnPlayerDeath` bloqueia o fim de jogo; o bot sobrevivente resgata (entra num círculo de 3 m),
  e o anão incapacitado se reanima após 5 s. Dois erros do ambiente de teste encontrados: resgate com posição relativa parecia
  congelado (o jogo regrava a posição entre atualizações; agora uma meta absoluta é gravada), e um falso
  "remoto incapacitado" disparava assim que um lado começava a partida (agora exige ter visto vida do remoto > 0).
  Num teste completo anterior, **ambos** foram incapacitados antes de completar os 5 s, portanto ninguém podia reanimar; a
  vida do resgatador agora é fixada apenas durante o resgate, para sobreviver à janela de resgate.
  - **VERIFICADO ponta a ponta, inteiramente automatizado** (`coop-run.ps1 -Auto -NoGod`):
    `check: downed role=client (game-over blocked)` → anfitrião `check: downed remote role=host (remote hp=0)` →
    `check: rescue started role=host dist=11,8` → `check: revive started role=client dist=2,8` →
    `check: revived role=client hp=100 alive=True`, e a partida continuou. Nenhuma tela de fim de jogo apareceu.
- **Visuais de combate (B) — etapa B1 concluída: evento de disparo sincronizado.** Novo `PacketType.Fire = 14` contendo
  posição da boca da arma (ponto fixo de 0,1 unidade) e direção da mira (1/10000), enviado sem garantia de entrega.
  - Interceptação: um *prefixo* Harmony em `ProjectileWeaponHandler.ShootProjectileInDirection(pData, direction, …)`.
    Ele contém o handler de disparo, portanto `handler.owner` identifica o atirador; apenas a arma do próprio jogador
    local retransmite (`ProjectileShootPatch`). Limitado a ~25 eventos/s.
  - Verificado (`coop-run.ps1 -Auto -NoGod`): anfitrião `shots 85 fireSent=85 fireRecv=115`,
    cliente `shots 117 fireSent=117 fireRecv=91` - disparos de cada lado chegam ao par, nos dois sentidos.
  - **Renderizar um visual está bloqueado pela própria compilação.** `GameObject.CreatePrimitive` retorna objetos
    cujo material é `Hidden/InternalErrorShader` (esta compilação não inclui recursos padrão do Unity), portanto nenhuma
    primitiva procedural poderá ser visível. `Shader.Find("Sprites/Default")` / `Unlit/Color` / `Standard`
    retornam shaders sem variantes compiladas (`Shader.Find` funciona, o desenho não produz nada - sintoma de
    "aplicado, mas invisível"), e um shader emprestado de um renderizador da cena era `FX/RT_Blobs`, um shader VFX
    que também não desenha nada numa malha simples. Veja a tentativa de traçante em `CoopCombat`.
  - Portanto, o traçante está **desligado por padrão** (`-cooptrace` o reativa), e B2 deve reutilizar os recursos
    do próprio jogo: clonar um visual existente como `CoopPuppet` clona a subárvore do jogador ou, melhor,
    - resolver o prefab real de projétil/VFX da habilidade de disparo e criá-lo. `Projectile.Shoot(WeaponHandler,
    ProjectileSettings, Vector3 origin, Vector3 direction, List<StatusEffectData>, EDamageType, float)` e
    `Projectile.SetInitialState(Vector3 origin, Vector3 direction, int pierce, ProjectileSettings, …)` são
    os pontos de criação; `ProjectileSettings` é pequeno e serializável (LifeTime, Speed,
    VFXThrottleFraction, OverrideDamageScalar, Ricochet, RicochetOnEnemy, SurvivesEnvironmentCollision).
  - `-cooptracerdebug` (e `coop-run.ps1 -TracerDebug`) ainda existem para testar novamente uma abordagem de desenho;
    imprimem o shader escolhido e a posição do traçante na tela.
- **Visuais de combate (B) — etapa B2: resolução do projétil real funciona, criação exige o pool do jogo.**
  O pacote Fire agora também contém o **nome** do recurso da habilidade de disparo. É a chave correta: ambas
  as instâncias executam o mesmo conteúdo, portanto o recurso de habilidade do anfitrião é o do cliente.
  - Cliente indexa cada `ProjectileWeaponSkillData` por `Resources.FindObjectsOfTypeAll` - **33 recursos**
    numa partida, e todos os disparos foram resolvidos (`noSkill=0 noPrefab=0`). Logs do anfitrião confirmam que o disparo contém
    o recurso: `shot skill='ProjectileWeaponSkill_Subata' prefab=True`.
  - `ProjectileWeaponSkillData.ProjectilePrefab` é uma referência de componente `Projectile`, portanto o prefab
    real é acessível: `Instantiate` produziu `DamageProjectile_Kinetic_Medium(Clone)` com componente
    `Projectile` ativo e `ProjectileSettings` não nulo.
  - **Bloqueio:** `Projectile.SetInitialState(...)` lança `Il2CppException` (NRE mascarada) num
    `Instantiate` simples. O projétil do pool entregue pelo jogo passou primeiro por
    `Init(ObjectPool<Projectile>, LayerMaskLibrary)`; um clone novo tem esses campos nulos. Próxima etapa:
    obter o pool de projéteis + biblioteca de máscaras de camada do jogo (ou reutilizar uma instância do pool já inicializada por `Init`)
    antes de `SetInitialState`/`Shoot`.
  - Segunda descoberta: `ProjectileSettings.Speed` leu **1000** para `Bosco_ProjectileWeaponSkill_Base`, portanto não
    é uma velocidade inicial em unidades/segundo - a velocidade real vem de `FireConfigs` da habilidade
    (`FirePointOffset`, `worldDirStartOffset`, `RotateDirPerShot`, `BurstShots`, `BurstFireRate`).
  - Segurança mantida em todos os casos: o espelho é criado com `damageScalar` 0 e sem efeitos de status, portanto um cliente
    nunca pode causar dano a um inimigo do anfitrião e dessincronizar o enxame.
  - Tudo isso está sob `-cooptrace` (ainda desligado por padrão), portanto uma partida normal não é afetada.
- **Visuais de combate (B) — etapa B3: infraestrutura de criação localizada, ainda falta uma peça.**
  Um `Instantiate` simples não funciona, mas o jogo tem a entrada correta: `Assets.Scripts.SkillSystem.
  ProjectileProviderStandard(WeaponSkillData data, LayerMaskLibrary layerMaskLibrary, BulletTrailVFXSystem
  bulletTrailVFXSystem)` cria um pool cujo `Get()` entrega um projétil já processado por
  `Projectile.Init(pool, layerMaskLibrary)`. `UpdateProjectilePrefab(Projectile)` redireciona um provedor para
  o prefab de qualquer habilidade, portanto uma única instância pode atender todos os disparos do par.
  - Infraestrutura emprestada dos próprios handlers de armas do jogador local (o provedor é um campo em
    `LinkProjectileWeaponHandler`; `LayerMaskLibrary` é uma **propriedade** em `WeaponHandler`, motivo pelo qual
    uma varredura apenas de campos não encontrou nada - erro simples que custou uma execução).
  - Progresso verificado: `combat: masks=True trails=False`, depois
    `combat: projectile provider built for 'Bosco_ProjectileWeaponSkill_Base'`. O provedor é construído.
  - A peça ausente era `Player.BulletTrailVFXSystem` - propriedade pública injetada no jogador
    (vfx, máscaras de camada e a maioria dos gerenciadores chegam em `Player.Inject(...)`). Obtê-la do jogador,
    em vez de procurar uma arma que comporte projéteis, resolveu a lacuna.
  - **Verificado (cliente, nesta execução):** `combat: masks=True trails=True` ->
    `combat: projectile provider built for 'ProjectileWeaponSkill_Subata'` ->
    `combat: mirror projectile #1/#2/#3 skill='ProjectileWeaponSkill_Subata'
    prefab=DamageProjectile_Kinetic_Medium go=DamageProjectile_Kinetic_Medium(Clone)`.
    Contadores `proj=109/0` - 109 criados, 0 falhas (antes `proj=0/98`), com `live=0`, portanto o jogo também
    os recupera. O cliente agora cria projéteis reais do jogo, do pool, neutros em dano.
  - Uma captura em sequência do cliente durante o combate mostra uma cena totalmente renderizada com projéteis, clarões de disparo
    e VFX de impacto. Um quadro não permite atribuir um projétil individual ao fluxo espelhado, portanto a
    *criação* está provada, e a *visibilidade* tem fortes indícios, mas ainda não foi isolada.
  - Sonda de renderização acrescentada (apenas `-cooptrace`): 0,4 s após criar, informa sobrevivência do objeto, distância
    percorrida, estado enabled/isVisible de cada renderizador, shader, camada e máscara da câmera.
    Adiada intencionalmente - `Renderer.isVisible` é gravado durante o descarte de visibilidade, portanto perguntar no quadro de criação
    sempre responde falso.
  - **Resultado da sonda (cliente):** `active=True travelled=9,2 rends=1 drawn=0 layer=9 camHas=True on-screen
    [r0 en=True vis=False URP/URP_Matcap_Unlit_Simple]`. Portanto o projétil espelhado está vivo, moveu-se
    ~9 unidades, tem exatamente um renderizador **ativado**, contém um **shader real do jogo** (não
    `Hidden/InternalErrorShader`, como as primitivas procedurais), está na camada 9 que a câmera principal
    **realmente** renderiza e dentro da área visível - mesmo assim, o descarte do Unity informa que não foi desenhado.
  - Essa combinação (ativado, camada certa, na tela, shader real, ainda `vis=False`) aponta para limites ou
    configuração de malha que o jogo realiza no próprio caminho `Shoot(...)`, contornado aqui ao chamar
    `SetInitialState` diretamente. **Experimento de controle antes de investigar:** executar a mesma sonda nos
    projéteis do próprio anfitrião. Se também informarem `vis=False` em +0,4 s, o sinal simplesmente não serve naquele
    ponto de amostragem, e o visual espelhado está correto - hipótese mais barata de descartar primeiro.
  - Tudo permanece sob `-cooptrace`; uma partida normal não é afetada, e o evento Fire em si (B1) está
    verificado e sempre ativo.

- **Estímulo de teste para armas: qualquer uma das 75 habilidades de arma pode ser equipada sob demanda (compilação 14:34).**
  O bloqueio abaixo ("nada lança granadas e não é possível anexar uma") acabou sendo o *ponto de entrada errado*,
  não uma preparação ausente. O jogo tem um modo público e nomeado de dar uma arma a um jogador, e funciona:

  ```text
  check: dev weapons n=75 role=host [0]AlternatingProjectileSkillData_Boltshark [1]BeamWeaponSkill_Electrical_TH0R
    [2]BeamWeaponSkill_RotatingBeam_CryoCannon … [25]Driver_ProjectileWeaponSkill_ChimeraFragcannon
    … [43]GrenadeWeaponSkillData_Leadburster [44]GrenadeWeaponSkill_Cryo [45]GrenadeWeaponSkill_HEGrenade
    … [48]ImpactAxeSkillData … [61]ProjectileWeaponSkill_AutoCannon …
  check: dev give 'GrenadeWeaponSkill_HEGrenade' via=EquipNewWeapon handler=yes data='…' owner=self
    weapons=1->2 registered=1 role=host
  grenade: throw #1 handler skill='GrenadeWeaponSkill_HEGrenade' own=1 dir=-0,15/0,99
  grenade: throw #1/1 base skill='GrenadeWeaponSkill_HEGrenade' prefab='Grenade_HE' from=(9.8,1.0,7.0)
  RESULT: grenade PASS reason=handlerThrows=7 baseThrows=7        (host)
  RESULT: grenade PASS reason=handlerThrows=12 baseThrows=12      (client)
  ```

  - **O caminho:** `Player.EquipNewWeapon(WeaponSkillData, bool)`, além de `EquipNewWeaponAtActionbarIndex`,
    `EquipBoscoWeapon`, `RemoveEquippedWeapon`, `HasWeapon`, `GetWeaponCount` e a lista realmente
    acionada pelo jogo: `Player.weapons` (`List<WeaponHandler>`) com `WeaponAdded`.
  - **Opções auxiliares:** `-coopdev-weapons` lista uma vez cada recurso `WeaponSkillData`; `-coopdev-give=<name[,name]>`
    os equipa no início da partida (`coop-run.ps1 -DevWeapons -DevGive <names>`). Cada concessão registra a contagem de armas
    antes/depois, portanto "o jogo aceitou" é um número, não uma suposição.
  - **Por que a primeira tentativa falhou, precisamente:** `GrenadeWeaponSkillData.AddWeaponHandler(go)` +
    `Init(data, owner, firePoint)` produz um handler aparentemente completo (dados corretos, proprietário correto), mas
    nunca inserido em `Player.weapons` - portanto o jogo nunca o aciona. Inicialização correta é necessária,
    mas insuficiente; o *registro* é a metade ausente.
  - **`weapons=1` no início da partida**, embora o anão carregue visivelmente Subata e Bosco: a arma inicial
    desenhada também não está nessa lista. Convém saber antes de interpretar a contagem como "número de armas".
  - **Fatos do catálogo de armas produzidos:** 75 recursos de habilidade de arma nas duas instâncias, incluindo a
    linha `Driver_*` (um conjunto inteiro de anão), `BeamWeaponSkill_*`, `ImpactAxeSkillData`, `CoilGun`,
    `DefenseDrone*`, `Boomerang`, `AlternatingProjectile*`, `LinkProjectile*` e oito habilidades de granada;
    a lista também contém armas de **inimigos** (`EnemyProjectile*`, `ExploderWeaponData*`), portanto um filtro
    por nome precisa excluí-las.
  - **Torretas também são cartas:** `SpawnWeaponSkill_Turret_Flamethrower` foi oferecida numa subida de nível, portanto a
    parte "torreta" do marco B é uma arma `SpawnWeaponSkill`, não um tipo `Turret`.

- **Uma armadilha de instrumentação medida duas vezes: em objetos de interoperabilidade, `GetType()` e `is` descrevem o wrapper.**
  Uma granada equipada pelo jogo foi lançada sete vezes numa partida enquanto a sonda informava
  `grenade handlers=0`, porque `h is GrenadeWeaponHandler` era falso para ela. `GetType().Name` não é melhor -
  cada carta de subida de nível imprimiu o tipo-base declarado `ASkillData`. Ambos só são confiáveis para objetos que este
  mod criou por conta própria pelo tipo gerenciado (um `AddComponent<GrenadeWeaponHandler>()` em execução satisfez
  `is`). **O discriminador confiável é o nome do recurso** do jogo (`data.name`), usado agora nas verificações
  de granada. O mesmo erro estava no log de ofertas de cartas e na preferência de preparação;
  ambos passaram a usar nomes depois disso.

- **Inicializador: o console "preso na abertura" era um defeito real e também clicava em partidas em andamento.**
  `coop-click.ps1` executava de forma síncrona por até 240 s e clicava em **todas** as janelas de jogo a cada rodada, com o
  papel mapeado apenas por marcadores de log. Assim, (a) o console continuava mostrando a última linha `host=on-splash` enquanto
  `coop-run.ps1` aguardava em silêncio e (b) uma instância já no menu ou numa partida continuava recebendo cliques
  centrais - que pressionam botões da interface. Duas execuções de hoje "travaram na abertura" e se condenaram silenciosamente.
  Agora: papel→PID pela linha de comando do processo (`-coophost`/`-coopclient`), cliques apenas nas instâncias que
  ainda estão antes de concluir a abertura, aviso explícito `GAVE UP after Ns` e linha de progresso ao vivo por papel durante
  a espera de resultado (além do aviso antecipado "nenhuma instância chegou a uma partida após 90s"). Verificado na execução seguinte:
  `phase: run-started t=+31,5s` / `auto: IN RUN after 14 steps`.

- **Visuais de combate (B) — granadas: a preparação não tem arma de granada e não é possível anexar uma (compilação 13:42).**
  O plano dizia "interceptar `Grenade.Throw`/`ShootGrenade`, transmitir, criar no cliente". Medido primeiro, em três
  etapas, cada uma respondendo uma pergunta diferente:

  1. **Algo lança uma granada?** Não. `check: grenade dump weapons=2
     [WeaponHandler:'ProjectileWeaponSkill_Subata':self, WeaponHandler:'Bosco_ProjectileWeaponSkill_Base':self]
     grenadeHandlers=0 inScene=13 active=0 skillAssets=10` nos **dois** papéis - o anão tem sua arma principal e
     Bosco, sem handler de granada, e os 13 objetos `Grenade` do pool nunca ficaram ativos. Portanto a preparação não tem
     nada a medir: este perfil tem **nada equipado** (`EquippedGear = []` no save, a lacuna `eq=0`
     já registrada para I1).
  2. **A fábrica do próprio jogo consegue anexar uma?** Não desta forma.
     `GrenadeWeaponSkillData.AddWeaponHandler(player.gameObject)` retornou um **`WeaponHandler`** simples (não um
     `GrenadeWeaponHandler`), com proprietário definido por `Init(...)` depois; `grenadeHandlers=0` em seguida e nenhum
     lançamento em 25 s. A fábrica acrescenta o que a classe *base* acrescenta - a entrada errada para uma granada.
  3. **O próprio componente de granada pode ser anexado?** Pode ser criado, mas não é acionado.
     `AddComponent<GrenadeWeaponHandler>()` + `Init(data, player, player.FirePoint, null)` com
     `GrenadeWeaponSkill_HEGrenade` fornece um handler real -
     `check: grenade give 'GrenadeWeaponSkill_HEGrenade' via=AddComponent+Init handler=GrenadeWeaponHandler
     isGrenade=1 data='GrenadeWeaponSkill_HEGrenade' owner=self` - e ainda **nenhum lançamento em 25 s**. Um
     handler inicializado corretamente (dados, proprietário, ponto de disparo) é necessário, mas insuficiente: a lista de armas
     é montada pelo jogo a partir da classe e do equipamento no início da partida, e um handler anexado depois não faz parte
     dela.

  Mais duas execuções da etapa 3 (`20261019-135025`, `20261019-135619`) produziram **nenhum dado**: a automação ficou
  em `auto: waiting on splash (leave it to a real click)` - o clique do inicializador não funcionou - e o teste
  expirou. Isso é instabilidade do ambiente de teste, registrada para não ser interpretada como resultado.

  **O que ainda assim foi obtido, e tem valor:**
  - O inventário de recursos de granada é idêntico nas duas instâncias (10 recursos), portanto um espelho pode resolver uma habilidade
    pelo nome, exatamente como o espelho de projétil: `Bosco_GrenadeGroundzone_Fire:GRENADE`,
    `Bosco_GrenadeWeaponSkill_Cryo:GRENADE`, `Driver_GrenadeWeaponSkill_ProximityMines:TRAP`,
    `GrenadeWeaponSkillData_Groundzone_Acid|Fire:GRENADE`, `GrenadeWeaponSkillData_Leadburster:GRENADE`,
    `GrenadeWeaponSkill_Cryo|HEGrenade|PlasmaBurster|ShredderSwarm:GRENADE`.
  - `Grenade.Throw` tem sobrescritas (`GrenadeShredderSwarm`, `LeadBursterGrenade`) que não chamam a base, portanto
    **não** é a entrada única; `GrenadeWeaponHandler.ThrowGrenadeInDirection` é, e só `TrapWeaponHandler`
    a sobrescreve. As duas interceptações estão instaladas e contadas lado a lado, portanto um lançamento visto numa e não na
    outra identifica um prefab de subclasse, em vez de ocultá-lo.
  - Os saves ficam numa **subpasta de Steam ID**: `%USERPROFILE%\AppData\LocalLow\Funday Games\DRG Survivor\
    steam\<SteamID>\drg_save_slot{1..3}_{0..3}.dat` (as notas anteriores diziam "a mesma pasta" - fica um
    nível mais abaixo).
  - Um resultado nomeado agora separa os dois zeros: `NO_GRENADE_THROWN` (nenhuma arma) de
    `HANDLER_NOT_DRIVEN` (handler presente, jogo nunca dispara). O texto está na compilação; as duas execuções
    que o mostrariam falharam no ambiente, portanto permanece **não observado** até a próxima execução bem-sucedida.

  **Substituído pela compilação acima:** o bloqueio não era ausência de preparação, mas o ponto de entrada errado. Uma
  granada *pode* ser equipada sob demanda por `Player.EquipNewWeapon`, e o jogo a lança (7/12 lançamentos,
  PASS nos dois papéis). A hipótese de equipamento também estava errada por si: `EGearSlotType` é
  `TOOL, ARMOR, GRINDER, WEAPON_MOD, TANK, COMPANION` - não existe slot de arma ou granada no conjunto, e
  `GearData` contém atributos, sem `WeaponSkillData`. Um espelho de granada agora é uma tarefa de código com estímulo funcional.

- **Visuais de combate (B) — oráculo de desenho: cinco caminhos dentro do processo encerrados, todos com evidências (compilação 03:30).**
  A lacuna após B3 era limitada e honesta: o cliente cria projéteis reais do pool (`proj=109/0`) e uma
  captura de combate parece correta, mas "o projétil espelhado é realmente desenhado" nunca foi *provado*.
  A investigação produziu seu próprio tipo de resultado - **toda leitura dentro do processo oferecida por esta compilação está encerrada**, cada
  uma com evidência exata, para ninguém precisar repeti-las:

  1. `Renderer.isVisible` - nenhuma informação (controle A/B de B3: os próprios projéteis do jogo informam `vis=False`,
     exatamente como os do espelho, em todos os momentos).
  2. Um `MonoBehaviour` gerenciado acrescentado durante a execução para contar `OnWillRenderObject` -
     `TypeInitializationException -> NullReferenceException`, ou seja, a classe il2cpp para um componente gerenciado
     injetado durante a execução não é inicializada. (`AddComponent<CoopTick>()` no carregamento do plugin funciona, portanto é o
     tipo *injetado* que falha, não o mecanismo.)
  3. `Camera.Render()` - **nem sequer existe na assembly de interoperabilidade**; o jogo nunca o chama e IL2CPP só
     inclui o que a compilação usa.
  4. `Camera.CopyFrom()` - o mesmo.
  5. `Texture2D.ReadPixels` de uma RenderTexture - **retorna preto**. Este é decisivo: a sonda tentou
     todas as cinco câmeras da partida, um quadro cada, e cada leitura foi `mean=0`
     (`Camera(en=1) RT_Camera(en=1,rt) Camera(en=1) Main Camera(en=0) UICamera(en=1)`), *inclusive* lendo a
     própria textura 256x256 de `RT_Camera`, que o jogo certamente renderiza a cada quadro. Portanto o problema é a leitura,
     não a escolha da câmera.

  ```text
  03:26:32.280 check: b3draw cameras Camera(en=1) RT_Camera(en=1,rt) Camera(en=1) Main Camera(en=0) UICamera(en=1) -> trying 'Camera'
  03:26:32.397 check: b3draw camera 'Camera' rendered nothing, trying 'Camera'
  03:26:34.108 check: b3draw camera 'Camera' rendered nothing, trying 'RT_Camera'
  03:26:34.165 check: b3draw camera 'RT_Camera' rendered nothing, trying 'Main Camera'
  03:26:34.207 check: b3draw camera 'Main Camera' rendered nothing, trying 'UICamera'
  03:26:34.252 RESULT: b3draw FAIL reason=verdict=NO_RENDERING_CAMERA
  ```

  **O controle mostrou seu valor aqui.** `NO_RENDERING_CAMERA` é o resultado que justifica o controle positivo:
  sem ele, esta execução teria informado `MIRROR_NOT_DRAWN` e levado o próximo agente a procurar um erro visual
  que a medição nunca observou. Ocultar o anão - certamente na tela - também não mudou nenhum pixel,
  e foi isso que disse "o instrumento está cego", não "o espelho está ausente".

  Dois fatos sobre a compilação surgiram e merecem ser preservados:
  - **`Camera.main` é `UICamera`**, e `Camera.allCameras` lista *apenas câmeras ativadas* - uma durante a partida, a
    câmera da interface. O mundo é desenhado por câmeras que não estão nessa lista, motivo pelo qual a busca precisou
    passar por `Resources.FindObjectsOfTypeAll<Camera>()`.
  - Um projétil estacionado pode ser produzido sob demanda: `CoopCombat.SpawnParkedMirror` cria pelo caminho normal
    do espelho e zera sua velocidade, como qualquer oráculo futuro precisa (um projétil voando só responde
    "foi desenhado" em alguns momentos).

  **O que permanece:** o espelho é criado, usa pool, é neutro em dano, contém um shader real do jogo e está numa
  camada renderizada - e nenhuma leitura disponível contradiz que ele é desenhado. O que ainda não está provado é que
  ele é desenhado. O oráculo restante está **fora do processo** (capturar a janela do jogo enquanto um espelho estacionado é
  mantido diante de uma câmera e comparar dois quadros); todos os caminhos internos são conhecidos como encerrados.

- **Visuais de combate (B) — experimento de controle B3: o sinal `isVisible` é inutilizável, não o visual.**
  A questão era se o espelho é realmente desenhado, porque a sonda informava `vis=False` para um
  objeto vivo, em movimento, ativado, na camada correta e na tela. A solução foi parar de medir
  o espelho sem referência: `-cooptraceab` coloca **os dois tipos numa instância**. Um prefixo Harmony em
  `Projectile.SetInitialState` (o único método privado por onde todo projétil passa) registra os projéteis
  do jogo como `kind=local`; `CoopCombat.InMirrorSpawn` marca a chamada do próprio mod, para seu
  projétil ser registrado como `kind=mirror`; e a *mesma* sonda amostra ambos em +0,1/0,25/0,4/0,8 s. A opção
  também devolve o disparo local ao caminho do espelho, portanto real e espelho são criados da mesma boca de arma
  no mesmo quadro.
  - **Observação** (`coop-run.ps1 -Deploy -Auto -Test b3 -TracerAB -Only host`, log arquivado):
    `check: B3 result=PASS verdict=SIGNAL_UNUSABLE local_vis=0/33(n=36 done=6) other_vis=0/0 mirror_vis=0/8(n=8 done=2)`
    - Todas as 33 observações vivas dos **próprios** projéteis do jogo informaram `vis=False`, em todos os momentos, com
      `rends=1 en=True layer=9 camHas=True on-screen` e shader real
      (`URP/URP_Matcap_Unlit_Simple`) - leitura idêntica byte a byte às 8 observações do espelho.
    - `combat: probe kind=local … travelled=2,4 / 5,2 / 8,0 / 16,0` é a mesma curva de ~22 u/s do
      espelho, `3,1 / 6,6 / 9,7 / 18,0`, portanto os dois tipos realmente se moveram e foram amostrados em voo.
    - Projéteis reciclados são visivelmente diferentes (`active=False`), portanto a sonda distingue estados.
    - Contadores das interceptações provam a infraestrutura: `hookReal=11 hookMirror=3`.
  - **Dedução:** nesses momentos, `Renderer.isVisible` não contém **nenhuma informação** sobre se um
    projétil desenhado pelo jogo está na tela nesta compilação. O `vis=False` anterior no espelho portanto
    **não é evidência** de que seu visual está quebrado, e a linha de investigação B3 "seguir o caminho `Shoot(...)` do jogo"
    está encerrada. O instrumento era a parte quebrada, não o visual.
  - **Sem alteração nesta execução:** `Renderer.bounds.extents` voltou como `bounds=n/a` para todos os renderizadores, portanto a
    hipótese de limites não foi confirmada nem refutada - a propriedade não é acessível da forma como a sonda
    a solicita (mesma lacuna de reflexão que oculta `isVisible`).
  - **Desconhecido (lacuna honesta):** "o projétil espelhado é realmente desenhado" ainda **não está provado**. Está
    provado que nenhuma leitura disponível o contradiz e que a leitura aparentemente contrária não tinha
    sinal. Ambos os oráculos indicados aqui foram tentados depois e estão **encerrados**: a diferença de pixels do objeto estacionado não
    consegue ler um quadro (veja a seção do oráculo de desenho mais abaixo - `Texture2D.ReadPixels` retorna preto, e
    `Camera.Render`/`Camera.CopyFrom` não existem na assembly de interoperabilidade), e o
    `MonoBehaviour` injetado para `OnWillRenderObject` não consegue ser construído. **O único oráculo restante fica fora do
    processo:** manter um espelho estacionado diante da câmera (a função auxiliar existe e funciona) e comparar duas
    capturas da janela do jogo feitas externamente.
  - **Efeito colateral útil da execução:** a automação chegou à missão em **~54 s** a partir do
    carregamento do plugin (fases: menu em +19 s, assistente com 7 etapas de 2 s cada, `run-started` em +35,6 s, primeiro disparo em
    +48 s, veredicto em +49 s). Os antigos "3–4 minutos até começar a missão mais espera fixa de 80 s" eram majoritariamente
    espera estimada, não inicialização.
- **Ambiente de teste (técnica relevante ao repositório, não apenas a este jogo).** Três fatores viabilizaram a execução acima
  e são reutilizáveis para cada marco posterior:
  - O mod encerra seu próprio teste: `-cooptest=<name>` o faz decidir quando a pergunta foi respondida, escrever
    `RESULT: <name> PASS|FAIL reason=… role=…` no log de cada papel e sair. O inicializador consulta essa linha,
    em vez de esperar uma quantidade estimada de segundos, e um teste sem resposta informa FAIL após um tempo limite
    (`-cooptesttimeout`, padrão 420 s), em vez de não produzir linha alguma. Veredictos nomeiam seus
    resultados inconclusivos (`MIRROR_MISSED`, `NO_REAL_ALIVE`), em vez de ocultá-los.
  - Toda etapa entre carregamento do plugin e partida registra `phase: <name> t=+Ns dt=Ms`, portanto o custo de inicialização é atribuído,
    em vez de estimado. (Ressalva: marcadores registrados antes do primeiro quadro usam outra base de tempo -
    `plugin-load t=+2,0s` precede `first-tick t=+0,3s` - portanto apenas `dt` entre marcadores de tempo de quadro é
    confiável.)
  - A implantação é verificada: a cópia da DLL é conferida por SHA-256 contra a saída da compilação, porque um binário antigo
    parece exatamente uma correção sem efeito. Execuções de teste arquivam logs e capturas em
    `local/work/runs/<stamp>-<test>/`, fazem backup prévio do perfil de save e sempre encerram os processos que
    iniciaram.

## <a id="stage-1-damage--client-hits-now-reach-the-host-build-of-1822"></a>Dano da etapa 1 — golpes do cliente agora chegam ao anfitrião (compilação das 18:22)

As armas do cliente antes atingiam apenas seus próprios espelhos congelados; o anfitrião nunca recebia o dano, portanto
o cliente não contribuía para uma morte, exceto sua própria morte local incorreta (`localDie`). O modelo aceito está
implementado: **o cliente executa suas armas localmente e informa o dano; o anfitrião o aplica ao
inimigo sob sua autoridade**.

- Observado: `check: hit sent=20 dmgTotal=532 flushes=15` (cliente) e
  `check: hit recv=20 applied=20 missed=0 unmatched=0 dmgTotal=532` (anfitrião) na mesma execução. Ambos os totais
  de dano são **idênticos**, e cada um dos 20 golpes foi aplicado - portanto os dois lados concordam no
  valor, não apenas na contagem.
- Transmissão: `EnemyHit` (0x0F) = `count(u16) × (hostId u16, dmg i32)`, ReliableOrdered. O dano informado é o
  **delta de vida produzido pelo próprio `TakeDamage` do cliente**, não o valor de entrada: o espelho contém a
  mesma armadura do original, portanto o delta já é final, e o anfitrião o aplica com
  `ignoreReduction: true`. Uma segunda aplicação de armadura faria os dois lados divergirem por um fator fixo.
- Golpes são somados **por inimigo** e enviados a ~16 Hz, portanto uma rajada de dano em área custa uma entrada, não um
  pacote (20 golpes em 15 envios). Aplicado em `CoopEnemy.DrainHits` na thread principal.
- Anfitrião aplica pelo próprio caminho do jogo, `Enemy.TakeDamage(dmg, false, KINETIC, doFx:false,
  PROJECTILE, hostPlayer, ignoreReduction:true)`, portanto morte, crédito pela morte e saque vêm do código real,
  em vez de serem reproduzidos manualmente. `entitySource` é o anão do anfitrião (o jogador remoto real não
  existe deste lado), portanto as mortes atualmente são atribuídas ao anão do anfitrião - lacuna conhecida para
  o trabalho de estatísticas por anão (PLAN.md I2).

### <a id="cost-patching-a-virtual-method-and-its-override-kills-the-game"></a>Custo: aplicar patch a um método virtual *e* à sua sobrescrita encerra o jogo

A primeira tentativa aplicou patch **tanto** a `Entity.TakeDamage` (virtual) quanto a `Enemy.TakeDamage` (sua sobrescrita).
Ambas as instâncias morreram ~1 s após carregar o plugin, de forma determinística, com
`0xc0000005` (violação de acesso) em `coreclr.dll` no mesmo deslocamento; o log do mod simplesmente parou após
`test: begin`, e BepInEx mostrou `Il2CppInterop ... During invoking native->managed trampoline`.
Sem Player.log, sem dump - e o inicializador informou `verdict: FAIL` sem linha RESULT, formato
esperado para "os processos morreram".

Aplicar patch apenas à sobrescrita (`Enemy.TakeDamage`) funciona, e essa é a regra: **aplicar patch à sobrescrita, nunca ao
par virtual+sobrescrita.** As interceptações existentes já a seguiam (`Enemy.Die`/`DeSpawn`/`Recall` são
sobrescritas e recebem patch dessa forma); `TakeDamage` foi o primeiro ponto em que foi violada. Confirmado pelos
dummies Cpp2IL: `Entity.TakeDamage` é `public virtual bool`, `Enemy.TakeDamage` é `public override bool`,
e ambos estavam sendo redirecionados.

Também aprendido com os mesmos dummies, e útil preservar: a assinatura e seus padrões são
`Entity.TakeDamage(long dmg, bool isCrit=false, EDamageType=KINETIC, bool doFx=false,
EDamageSource source=PROJECTILE, Entity entitySource=null, bool ignoreReduction=false)`. Saber disso
permitiu substituir a chamada por reflexão por uma direta, mais simples e mais segura em IL2CPP.

## <a id="incoming-damage--the-clients-dwarf-is-already-in-danger-build-of-1839"></a>Dano recebido — o anão do cliente já corre perigo (compilação das 18:39)

Antes de escrever algo para "inimigos precisam conseguir ferir o cliente", medimos se já
conseguiam. Conseguem, e por uma razão estrutural, não por sorte:

- Um espelho é um **`Enemy` real criado pelo gerador do próprio cliente**, portanto o jogo lhe entregou o jogador
  do cliente na criação. O enxame de espelhos do cliente considera o anão do cliente seu alvo e o ataca.
- Medido com `-coopnogod -coopswarm -cooptest=damage -cooptestmin=120` (invencibilidade desligada, cliente junto
  do espelho mais próximo para que o anão realmente fique ao alcance): o cliente perdeu **8×10 de vida em ~34 s**, cada golpe
  registrado com a distância que permite atribuí-lo - `nearestMirror=0,7–1,2`,
  `type=GRUNT0/BASE`/`FAST_GRUNT/BASE`, `enemiesWithin5=2–7`. O anfitrião sofreu **8×10 de vida na mesma
  janela**. Ambos os lados são feridos na mesma taxa enquanto estão no enxame.

Portanto também não é necessário pacote de dano nesta direção. Cada lado tem autoridade sobre a vida de seu próprio anão:
o cliente calcula os próprios golpes, o anfitrião lê o resultado como `remoteHp` em `PlayerState`, e
incapacitação/reanimação já se baseia nesse número. `EnemyHit` (cliente -> anfitrião) e isto (local ao cliente) são a
mesma regra, "quem executa a simulação de uma entidade controla sua vida", aplicada aos dois tipos de entidade.

### <a id="still-open-aggro-and-it-is-not-a-cheap-fix"></a>Ainda em aberto: agressividade, e não é uma correção barata

`Enemy.Player` é uma propriedade **somente leitura**, respaldada por um campo privado que
`OnCreated(..., Player player, ...)` define uma vez na criação, e uma instância tem exatamente um `Player`. No
anfitrião, cada inimigo portanto mira o anão do anfitrião, e nada no anfitrião consegue mirar o anão do cliente.
"Agressividade do anfitrião contra o boneco" não é uma reatribuição de alvo; exige um segundo `Player` *real* no
anfitrião (inicialização DI, HUD, câmera). Consequência hoje: o enxame segue o anfitrião, e o cliente é atingido porque
ocupa o mesmo espaço - não porque os inimigos o escolheram.

**Decisão de projeto (18:40):** idealmente, o parceiro *deveria* atrair sua própria agressividade, mas isso está **registrado como
objetivo posterior e deliberadamente sem prioridade agora**. Anotado em PLAN.md B2 e no arquivo do plano sob
"Später (bewusst NICHT priorisiert)". A tentativa mais barata ao retomar é remover
`SetAgentEnabled(false)` para ver se um espelho descongelado escolhe o cliente sozinho; a prova deve ser uma
*redução de distância* por vários segundos, não um golpe acidental.

### <a id="two-measurement-traps-this-cost"></a>Duas armadilhas de medição que isso custou

- **Invencibilidade oculta todo dano.** O bot de teste fixa a vida em 100000, portanto toda execução anterior informava
  `hpDrops=0` — o que não diz nada sobre inimigos e foi brevemente interpretado como "o cliente está seguro". Questões
  de dano exigem `-coopnogod`.
- **Uma instância sair invalidou a janela da outra.** O anfitrião atingiu seu limite após 12 s e
  saiu; o cliente então passou 85 s sozinho, sem parceiro, com uma barreira de subida de nível pendente (`barrier=both`)
  e um conjunto de espelhos congelado, e seu "1 golpe, depois nada" veio dessa janela morta. A primeira
  conclusão ("espelhos congelados não atacam") estava errada exatamente por isso. `CoopTest.MinSec`
  (`-cooptestmin=<s>`) agora retém o veredicto até ambos os lados terem a mesma janela de observação, e a
  repetição inverteu o resultado. Um teste com duas instâncias precisa tratar o tempo de vida da outra como parte
  de sua própria medição.

## <a id="level-up-cards-the-reward-screen-is-drivable-and-every-earlier-run-took-no-reward-build-of-1852"></a>Cartas de subida de nível: a tela de recompensa é controlável, e todas as execuções anteriores não recebiam recompensa (compilação das 18:52)

A automação respondia às subidas de nível chamando `LevelUpManager.OnLevelUpFinished`. Isso avança o fluxo
e mantém a partida viva, razão da escolha - mas também encerra a tela **sem confirmar
uma carta**. A consequência nunca havia sido percebida: *nenhuma* partida automatizada havia aplicado uma melhoria, portanto
todo o sistema de melhorias estava sem teste e "a partida passou" significava "a partida passou sem melhorias".

A tela é controlável; a tentativa anterior de pressionar uma carta falhou por uma razão documentada que vale preservar:

- O callback de pressionamento de `UISkillButton` chega a `UILevelUpForm.OnSkillSelected`, que apenas **pré-visualiza** uma
  carta. Por isso pressioná-lo deixava a partida congelada.
- A confirmação é o público **`UILevelUpForm.OnSkillChosen(UISkillButton, SkillRaritySet)`** - a chamada que o
  jogo faz quando o jogador confirma.
- Os dados da carta são acessíveis sem nomear campos privados: `UISkillButton.SkillRarity` (público) fornece
  `SkillRaritySet`, e `SkillRaritySet.SkillData.name` é o nome legível da carta.

`CoopUpgrade.cs` (novo) escolhe; `CoopAuto.ServeLevelUp` agora tenta uma carta real **primeiro** e mantém o
atalho pelo gerenciador apenas como último recurso para evitar que uma tela trave a partida - e o conta
(`Skipped`), portanto "a partida continuou" não pode mais ocultar "o anão não ganhou nada".

Medido (`-Test levelup -TestMinSec 120`), PASS nos dois papéis com `skipped=0`:

```
host   picked=3   SupportSkill_MoveSpeed / SupportSkill_MiningSpeed / SupportSkill_MoveSpeed   (index 0)
client picked=3   WeaponUpgradeSkill_FireRate ×3                                               (index 1)
```

- Os dois lados escolhem **cartas diferentes**, como desejado: a escolha é por jogador, não uma escolha compartilhada
  ecoada duas vezes. Cada instância recebe sua própria lista (ordem observada difere: anfitrião
  `Damage/FireRate/ReloadSpeed`, cliente `FireRate/Damage/ReloadSpeed`), e o mod prefere intencionalmente um
  índice diferente por papel para impedir aprovação por coincidência de escolhas.
- A barreira de XP não é afetada: `local picks done, holding until remote picks` → `remote picks done`
  em torno de cada escolha.
- O teste precisa de **duas** escolhas, não uma: a falha interessante é a segunda abertura do formulário,
  após o fluxo já ter passado uma vez pela barreira.

Isso removeu o último "atalho só da automação" no caminho de subida de nível: uma partida agora aplica melhorias reais,
portanto medições posteriores de dano/progressão medem um jogo real.

## <a id="run-settings-adoption-the-levels-matched-by-coincidence-and-now-they-match-on-purpose-build-of-1909"></a>Adoção das configurações de partida: níveis coincidiam por acaso e agora coincidem intencionalmente (compilação das 19:09)

Ambas as instâncias geravam um mapa idêntico muito antes de isso existir. O motivo não era
sincronização - o bot de teste percorre os dois assistentes pela mesma ordem fixa de páginas em
saves parecidos, portanto ambos clicavam no mesmo bioma, setor e nó. Só o
perigo era imposto pela rede (e a semente). Qualquer diferença - outro
save, outro estado de desbloqueios, uma pessoa escolhendo de um lado - colocaria os dois anões em
cavernas diferentes, e nada detectaria isso.

`RunConfig` agora contém a identidade completa da partida: perigo, semente, bioma, setor, nó, tipo de missão, tipo
de missão principal. O anfitrião lê seu próprio `RunSettingsManager` e transmite a cada 1 s
por `CoopTick`; o cliente aplica no prefixo de `MapGenerator.CreateMap`.

- **O envio periódico não é um detalhe opcional.** O cliente chega à sua própria preparação de partida *antes* de o anfitrião iniciar
  a dele: o cliente pressiona Play quando o assistente do bot termina, e se a configuração só fosse enviada no
  início da partida do anfitrião, o cliente já poderia ter passado de sua preparação. Reenviar é idempotente.
- **A identidade do nó é (bioma, índice de setor, índice de nó)**, não um objeto. Ambas as instâncias leem os mesmos
  recursos `MissionSectorData`, portanto os mesmos três índices identificam o mesmo nó dos dois lados. O cliente
  o resolve por seu próprio percurso de missão e aplica com o próprio
  `SetupMissionRoadNode(nodeState)` do jogo - chamada feita quando um jogador clica nesse nó. Definir os
  campos derivados manualmente exigiria adivinhar quais importam.
- **O teste exige uma divergência deliberada.** `-coopdrift` (apenas cliente) faz o cliente pressionar o
  *maior* `MissionNodeButton_` disponível, enquanto o anfitrião pressiona o menor. Sem isso, os dois lados
  concordam por construção, e "configurações corresponderam" não prova nada.

Medido (`-Test settings -Drift -TestMinSec 60`), PASS nos dois papéis:

```
host   check: settings role=host gathered  settings biome=Crystalline Cavern(0) hazard=0 sector=0 node=0 mission=0/0 mutators=off
client auto: DRIFT - client takes 'MissionNodeButton_05' instead of the lowest node
client check: settings role=client applied=1 drift=1 (CreateMap) settings biome=Crystalline Cavern(0) hazard=0 sector=0 node=0 mission=0/0 mutators=off
```

`drift=1` é a questão central: o cliente realmente escolheu nó 5, a adoção realmente o trouxe de volta
ao nó 0 do anfitrião, e o estado do próprio jogo então é igual nos dois lados. Os outros quatro campos
já coincidiam (ambos os assistentes escolheram as mesmas páginas de perigo/missão/setor), portanto nó é o campo que esta
execução de fato prova - também o campo que decide qual caverna será usada.

**Duas coisas medidas da maneira difícil:**

- **`PrepNewRun` não é a interceptação.** Parece o lugar certo - monta configurações de nível e modificadores
  a partir das configurações, portanto adotar antes de seu corpo executar seria anterior à geração
  de terreno. Nunca disparou. Todas as execuções informaram adoção em `CreateMap`, e o
  método não tem chamador em nenhuma parte de `Assembly-CSharp` descompilado (é `internal`, portanto a assembly da interface
  pode chamá-lo, ou pode atender caminhos de desafio/infinito/nova tentativa, em vez de partida iniciada pelo
  assistente de missão). O patch foi removido em vez de mantido como código não exercitado. Consequência honesta:
  a adoção ocorre antes da geração do terreno, mas não comprovadamente antes das configurações do nível - tudo
  lido depois lê o gerenciador corrigido, e a impressão digital do mapa é idêntica.
- **Uma redefinição no início da partida apagou as evidências e fez um recurso funcional parecer quebrado.** O cliente aplica as
  configurações no menu, antes da existência da partida; limpar contadores ao iniciar deixou um log
  com `applied=1 drift=1` junto de um teste que expirava com `drift=0 none`. Redefina apenas o controle por
  partida, nunca os fatos que descrevem o que aconteceu antes dela.

## <a id="readiness-handshake-the-client-may-not-choose-before-it-holds-the-hosts-data-build-of-1926"></a>Negociação de prontidão: o cliente não pode escolher antes de ter os dados do anfitrião (compilação das 19:26)

"Ambos os lados geraram o mesmo mapa" era, até agora, uma questão de tempo. O anfitrião transmitia suas configurações
uma vez por segundo, e o assistente do cliente leva ~40 s, portanto os dados sempre venciam a corrida - mas nada
*garantia* isso, e a garantia é o que uma sessão cooperativa realmente precisa: o cliente não deve criar sua
partida a partir do que seu próprio menu tiver selecionado. Portanto o cliente agora espera.

**A troca**, toda sem interface e testável sem nenhuma interface:

1. Cliente envia `Hello` (16) assim que existe um socket de par - e continua solicitando a cada 2 s enquanto
   espera (veja a armadilha abaixo).
2. Anfitrião responde com `RunConfig` completo.
3. Cliente confirma com `ReadyEcho` (17), informando os valores que tem.
4. Anfitrião compara com o que enviou e informa `echo=1`.

**A barreira** é `CoopAuto.HoldForHandshake`: o assistente do cliente não pressiona nada até a etapa 3
ocorrer, com uma saída após 30 s que registra e prossegue, para impedir que a perda do par trave o assistente - mesmo
formato do tempo limite de 45 s da barreira de subida de nível.

Medido, PASS nos dois papéis, duas vezes:

```
normal                 client: check: handshake role=client ready=1 held=10,1s helloTx=7
                       host:   check: handshake role=host peer-hello=1 peer-ready=1 echo=1 cfgTx=4
gate forced (-ConfigDelaySec 15)
                       client: held=20,3s        host: echo=1
```

**Duas verificações, não uma, intencionalmente.** A negociação responde "os dados chegaram?", e o teste `settings`
responde "o jogo executa com eles?". Uni-los num veredicto impediria uma falha de indicar
qual metade quebrou - e elas realmente podem falhar independentemente: um valor pode chegar intacto e ainda ser
sobrescrito depois pelo assistente.

**A armadilha que fez a negociação parecer pronta sem transportar nada.** `Hello` é enviado uma vez ao carregar
o mod (~3 s), e o anfitrião não tem `RunSettingsManager` até ~25 s; assim, a resposta era "ainda não há nada a
enviar", e a transmissão de 1 Hz fazia todo o trabalho em silêncio. A ida e volta estava implementada, registrada e
inútil. Agora a solicitação é repetida a cada 2 s enquanto a barreira espera, o que a torna uma verdadeira
solicitação/resposta - e `helloTx=7` nas evidências acima prova exatamente que foi exercitada,
não apenas estava presente.

**O que resta do marco G do plano** é apenas a apresentação: tela de hospedar/entrar no jogo, sala
Steam e convites. O protocolo subjacente (configurações, negociação, barreira de prontidão) agora existe e está
verificado - motivo pelo qual as opções podem continuar como caminho de teste: o ambiente precisa de entrada sem interface.

## <a id="where-the-unlocks-live-and-whether-the-game-reads-them-live-build-of-2001"></a>Onde ficam os desbloqueios e se o jogo os lê em tempo real (compilação das 20:01)

A adoção de perfil do anfitrião (I1) começa com uma medição, porque o plano exige e porque adivinhar aqui
custaria caro: a resposta decide se adotar é uma troca em memória ou um recarregamento de arquivo de save.

`SaveData` é o objeto que contém tudo que vale adotar:

```
Version Timestamp
Challenges
WeaponSaveData          ClassModSaveData        BiomeSaveData      MutatorSaveData
MetaStatUpgrades        MileStoneStates
UnlockedChallengeSetIds UnlockedWeaponIds       UnlockedArtifactIds
UnlockedClassArtifactIds OverclockUnlockedWeaponIds UnlockedClassIds
DailyScore WeeklyScore BiomeScore ...
```

A sonda alterou uma dessas listas em memória e repetiu a consulta do próprio jogo:

```
check: profile role=client profile cls=4 wpn=29 art=13 mod=9 oc=0 meta=18 wpnSave=0 dwarf=11110000
check: profile live=yes cleared=4 before=11110000 afterClear=00000000 restored=11110000
```

`live=yes` é o resultado: limpar `UnlockedClassIds` fez `SaveDataManager.IsClassUnlocked` retornar
falso para todos os anões **no mesmo quadro**, e restaurar a lista os trouxe de volta. Portanto o estado de
desbloqueio é lido em tempo real de `SaveData` - sem cache montado no carregamento, sem necessidade de recarregar. A adoção pode então
ocorrer no menu, antes de o cliente escolher classe, exatamente a janela que a barreira de prontidão da
seção anterior já oferece. Particularidades de equipamento e níveis de melhorias permanentes são lidos do mesmo objeto, portanto
"adoção é uma troca de dados de save" deixa de ser suposição do plano e vira propriedade medida.

**Três tentativas de alcançar o save, e o motivo de cada falha é a parte útil:**

- `GameController` não existe no menu. Surge ao iniciar uma partida - portanto o caminho natural
  (`gc.saveDataManager`) é inacessível justamente na janela necessária à adoção, e a sonda ficou no
  menu informando "ainda sem GameController", enquanto o assistente executava sem ela.
- `SaveDataManager.SaveData` e `PCSaveFileManager.Data` são ambos **somente leitura**. Nenhum pode ser simplesmente
  atribuído, portanto adoção exige patch no getter ou alteração do objeto existente no próprio lugar.
- O bloqueio real: **`MetaManager.saveDataManager` não é um campo no tipo de interoperabilidade.** Campos e
  propriedades parecem igualmente plausíveis na descompilação, e só listar os membros resolveu:

```
type DRS.Meta.MetaManager fields={ isWrapped pooledPtr}
type DRS.Meta.MetaManager props={ OldPriceData statUpgradeCollection ... saveDataManager wallet
                                  runSettingsManager ... ArtifactRerolls ... transform gameObject ...}
```

  `GetFields()` retorna apenas o controle interno do próprio Il2CppInterop, enquanto todo membro real - inclusive
  os privados - é uma *propriedade*. Ler um campo privado pelo nome não encontra nada, e o código falha
  silenciosamente, no momento mais enganoso. Vale saber para toda futura busca de gerenciador neste
  jogo, portanto também está nas armadilhas do manual.

**Outra descoberta importante:** ambas as instâncias de teste leem o *mesmo* perfil de save
(`%USERPROFILE%\AppData\LocalLow\Funday Games\DRG Survivor\steam`). Portanto, no momento desta medição,
"save do anfitrião" e "save do cliente" eram o mesmo arquivo, e um teste de adoção de perfil não teria
nada a adotar. As duas metades disso são corrigidas na próxima seção: o inicializador agora pode colocar as duas
instâncias em slots diferentes e devolver os saves depois.

**Ainda não medido:** I2 - como o fim de uma partida transforma estatísticas em graduação, maestria e marcos. É a
segunda incógnita do plano e o pré-requisito para creditar o progresso do cliente ao anfitrião.

## <a id="two-separate-save-profiles---and-giving-the-players-saves-back-build-2024"></a>Dois perfis de save separados - e devolução dos saves do jogador (compilação 20:24)

I1 exige perfis *diferentes* no anfitrião e no cliente, senão não há nada a adotar. Duas
coisas precisaram ser corrigidas antes mesmo de testar isso.

**Slots separados.** O jogo mantém três slots de save lado a lado numa pasta
(`drg_save_slot{N}_{rotation}.dat`), portanto as instâncias podem apontar para slots diferentes. A escolha
persistida fica em `PlayerPrefs`, compartilhado pelas duas instâncias - forçá-la ali moveria ambas - portanto o mod
força o slot em `PCSaveFileManager.Load`, e só quando solicitado pelo inicializador (`-coopsave=N`).
Medido:

```
host   save: forced slot0 (read back Slot1) before load 1
client save: forced slot1 (read back Slot2) before load 1
host   check: saves peerSlot=1 mySlot=0 separateFiles=yes sameProfile=yes
```

`separateFiles=yes` é a propriedade do ambiente que agora tem teste (`-Test saves`, PASS nos dois lados).

**Mas os slots contêm a mesma progressão.** `sameProfile=yes`: Slot1 e Slot2 informam
`cls=4 wpn=29 art=13 mod=9 oc=0 meta=18`. Portanto apontar as instâncias para slots diferentes separa os
*arquivos*, mas não o *conteúdo* - um testador jogou os três slots até o mesmo ponto. Isso importa para
o projeto do teste, e por isso o veredicto `saves` é "arquivos diferentes", não "números diferentes": o
segundo falharia por uma razão sem relação com o código testado. I1, em vez disso, *limpará*
as listas de desbloqueio do cliente em memória antes do assistente, para o anfitrião ter algo real a lhe fornecer.

A mesma medição respondeu outra pergunta: o perfil do cliente trafega pela rede
(`ProfileReport = 18`, inteiros simples como no restante da negociação), portanto o anfitrião compara com números
que o cliente realmente possui, em vez daqueles que esperava ter enviado.

**O ambiente gravava nos saves do jogador e nunca os restaurava.** `Backup-Saves` copiava o perfil
antes do teste e nada o devolvia - portanto cada execução deixava seu progresso no save real. Isso
foi corrigido: `Restore-Saves` executa no `finally` após os processos do jogo terminarem e verifica a si próprio
contra o backup. Duas coisas resultaram de fazer isso honestamente:

```
saves: restored and verified (14 files, canary removed)
```

- **A primeira tentativa quebrou o layout dos saves**, e a verificação por hash detectou isso. A raiz do backup é o
  *conteúdo* de `steam`, não a pasta; restaurar um nível de diretório acima deixou o jogo sem
  pasta `steam`. Foi reparado a partir do backup e verificado como idêntico byte a byte (14 arquivos,
  `differences=0`) antes de qualquer outra execução. Ambas as funções agora compartilham um `$script:saveDir`, para as duas
  cópias não divergirem novamente.
- **Horários de arquivo não provam que uma restauração executou.** `Copy-Item` preserva `LastWriteTime`, portanto um mtime inalterado
  significa "cópia fiel" *ou* "nada aconteceu" - e uma execução que nunca chega à jogabilidade não grava nada,
  exatamente o caso produzido por `-Test saves`. A restauração então cria um arquivo sentinela
  *depois* de fazer o backup e exige que ele desapareça depois; a linha arquivada acima é a prova.

**Estado:** `saves` PASS (ambos os papéis), restauração verificada, saves idênticos byte a byte ao estado anterior à execução.
Próximo: I1 propriamente dito - listas de desbloqueio do anfitrião para o cliente, aplicadas no menu antes de escolher classe, com
o perfil do próprio cliente limpo para tornar a adoção visível.

## <a id="the-hosts-unlocks-now-reach-the-client-before-it-picks-a-class-build-2038"></a>Desbloqueios do anfitrião agora chegam ao cliente antes de escolher classe (compilação 20:38)

Primeiro incremento real de I1, cuja forma foi decidida pela medição das duas seções acima: o
jogo lê `SaveData` em tempo real, portanto adoção é uma troca em memória que pode acontecer no menu - exatamente
onde a barreira de prontidão da negociação já retém o cliente.

**As seis listas de desbloqueio trafegam literalmente.** `UnlockedClassIds`, `UnlockedClassArtifactIds`,
`UnlockedWeaponIds`, `UnlockedArtifactIds`, `OverclockUnlockedWeaponIds`, `UnlockedChallengeSetIds` são
lidas de `SaveData` do anfitrião como as strings armazenadas pelo próprio jogo e chegam como strings
(`ProfileAdopt = 19`). Nada no protocolo precisa saber o que um ID *significa*: `IsUnlocked` e
`IsClassUnlocked` comparam exatamente essas strings, portanto um formato presumido incorretamente não consegue funcionar pela metade. As
contagens são limitadas no recebimento (16 listas, 8192 itens por lista) porque vêm da rede.

**A ordem torna isso correto, em vez de sorte.** O cliente aplica as listas dentro da mesma
barreira `TryConfirmConfig` que retém seu assistente, e ela agora também espera pelo payload quando a adoção
está ativa. Assim, a página de classe - construída após abrir a barreira - só pode mostrar as opções do anfitrião.

**E o cliente deixa de gravar seu perfil.** `PCSaveFileManager.RequestSave` e `ForceSave` são ignorados
enquanto o cliente usa desbloqueios emprestados; caso contrário, uma solicitação de salvamento os persistiria no
arquivo do próprio cliente, transformando "emprestado para esta partida" em "meu para sempre". Esse é o núcleo de I3.

`-Test profile-adopt` passa nos dois lados, com `SaveData` do cliente esvaziado antes para haver algo
a adotar (os três slots contêm progressão idêntica, medida anteriormente):

```
client  check: profile-scrub role=client cleared before={4 9 29 13 0 1} after={0 0 0 0 0 0} dwarf=00000000
client  check: profile-adopt role=client received {cls=4 mod=9 wpn=29 art=13 oc=0 sets=1}
client  check: profile-adopt role=client applied  {cls=4 mod=9 wpn=29 art=13 oc=0 sets=1}
client  auto: wizard page: UIBackButton ClassSelectButton_Scout ClassSelectButton_Gunner
                     ClassSelectButton_Engineer ClassSelectButton_Driller UIPlayCrumb ...
client  auto: step 22 - pressing (OnButtonClick) plan[4] ClassSelectButton_ 'ClassSelectButton_Driller'
client  RESULT: profile-adopt PASS reason=applied={...} class=ENGINEER classPageButtons=4 received=2
host    RESULT: profile-adopt PASS reason=peerClasses=0 deficit=1 adoptSent=2 mine={... dwarf=15}
```

O próprio save do cliente não oferecia **nenhuma** classe (`dwarf=00000000`), o anfitrião entregou 56 IDs, e a
página de classe então ofereceu **quatro** - entre elas Driller, uma classe que o save do cliente nunca desbloqueou.

**Por que a asserção fica na página de classe, e não na classe final:** este ambiente substitui intencionalmente
a classe do cliente depois (`OverrideClientClass`, do trabalho de visuais de personagem), portanto
`class=ENGINEER` é uma decisão do ambiente de teste. "A página ofereceu quatro classes a um cliente cujo save não oferecia
nenhuma" não pode ser verdade pelo motivo errado; "o cliente joga de Driller" poderia.

**Dois erros do ambiente expostos nesta execução**, ambos influenciando resultados silenciosamente:

- **O jogo pula etapas do assistente por conta própria.** O cliente estava em `plan[3] MissionNodeButton_` enquanto a
  página de *classe* aparecia, porque esse save lembra seu último nó e todos os botões da página de nós estão
  inativos - portanto um plano rígido espera para sempre ali, com sintoma indistinguível de uma adoção
  quebrada. O plano agora avança para uma etapa posterior cujo botão realmente está na página e registra
  `auto: skipped plan[3]` quando faz isso.
- **`classPageButtons` era a contagem da *última* página, não da página de classe.** Cada mudança de página a preenchia de novo,
  portanto a página de perigo a deixava zerada e uma adoção *bem-sucedida* informava falha. Agora é um máximo: um
  fato sobre uma partida precisa sobreviver às páginas seguintes.

**Fora deste incremento, e vale dizê-lo em vez de deixar implícito:** níveis de melhorias permanentes, inventário/conjunto
de equipamentos e graduação do jogador. As seis listas decidem *o que o cliente pode escolher*; estes decidem *quão
forte ele é*. I2 (creditar o progresso do cliente de volta ao anfitrião no fim da partida) permanece intocado.

## <a id="the-corpse-that-keeps-walking-die-runs-the-animator-never-comes-back---fixed-build-of-2306"></a>O cadáver que continua andando: `Die` executa, o animador nunca retorna - CORRIGIDO (compilação das 23:06)

Relatado em teste de jogo: "o outro anão às vezes continua correndo como cadáver após uma reanimação". Medido, e
a causa não está onde parece:

```
host  check: corpse die       dmg=KINETIC hp=0 alive=0 anim=Idle#1432961145 t=12.96
host  check: downed role=host (game-over blocked)
host  check: corpse anim-end  Walk condition=DIE hp=0 alive=0 anim=Idle#1432961145 t=12.96
host  check: revived          hp=100 alive=True | after={hp=100 alive=1 anim=Dying#-1546996312}
host  check: corpse after-revive hp=100 alive=1 anim=Dying#-1546996312 t=2.64
client  downed: stood up on its own (hp=13) hp=13 alive=1 anim=Dying#-1546996312 t=0.74
```

- **`Player.Die(EDamageType, long, bool)` executa.** O mod só ignora `GameController.OnPlayerDeath`, portanto
  a própria morte - e com ela a animação de morte - ainda ocorre.
- **`Player.IsAlive` é uma propriedade somente leitura (derivada), mas a animação é um estado separado.**
  `WalkPlayerAnimator.HandleEndCondition(DIE)` muda o animador para `Dying` (hash `-1546996312`; o
  `Idle` normal é `1432961145`). Regravar `currentHp` não o altera.
- **Assim a pose permanece morta enquanto o anão se move**, e o mesmo ocorre na recuperação do próprio jogo: vida de 0 para
  13 também deixa o animador em `Dying`. "Às vezes" depende de qual caminho veio primeiro, não de a pose
  às vezes se recuperar - nenhum caminho a recupera.

`BasePlayerAnimator` não declara equivalente de `HandleEndCondition` nos stubs (só `UpdateAnimator`,
`SetIdle`, `SetMiningWeight`), portanto o retorno precisou ser encontrado por medição, que
resolveu a questão (`20261018-225649-corpse`, ambos os papéis idênticos byte a byte):

```
corpse params   n=8 {isIdle:Bool isDead:Trigger isAngry:Trigger moveSpeed:Float
                     isMining:Trigger isPickUp:Bool flying:Bool flyType:Int}
corpse baseline hp=145 alive=1 anim=Idle#1432961145 t=0,00 trueBools=[isIdle]
```

**A pose de morte é acionada por um Trigger (`isDead`), não por um booleano** - portanto não há estado booleano preso a limpar:
`SetBool` não limpa um gatilho, e o único booleano definido é `isIdle`, estado ocioso normal que
o jogo regrava a cada quadro. Uma etapa "limpar todos os booleanos" foi escrita primeiro, executou e foi removida
novamente: não mudou nada e alterou estado sem relação. A pose precisa ser redefinida no nível de **estado**,
e `Animator.Rebind()` + `Update(0f)` faz exatamente isso:

```
corpse reset where=revive before={hp=100 alive=1 anim=Dying#-1546996312 trueBools=[isIdle]}
             step1(rebind)={hp=100 alive=1 anim=Idle#1432961145 t=0,00} fixedBy=rebind
corpse stable t=+1,0s hp=100 alive=1 anim=Idle#1432961145 dying=0 restores=1/1
```

A redefinição executa nos **dois** caminhos que trazem um anão de volta - reanimação do próprio mod (`CoopDowned.ReviveTick`)
e autocura do jogo (`downed: stood up on its own`), que produzem o cadáver da mesma forma - e
`BasePlayerAnimator.SetIdle(false)` é mantido depois, como indicado na passagem de trabalho.

**Verificado ponta a ponta, duas vezes**, `-Test corpse -NoGod -TestQuit none` (`20261018-230341-corpse` e
`20261018-230838-corpse`), PASS nos dois papéis nas duas vezes:

```
host   RESULT: corpse PASS reason=restores=1 clean=1 stable=1/1 last='revive fixedBy=rebind' anim=Idle#1432961145
client RESULT: corpse PASS reason=restores=1 clean=1 stable=1/1 last='self-stand fixedBy=rebind' anim=Idle#1432961145
```

A segunda execução teve mais oito reanimações, todas redefinidas da mesma forma
(`corpse stable ... dying=0 restores=8/8`, `fixedBy=rebind` em cada uma). `-TestQuit none` importa: caso contrário,
o inicializador deixa a primeira instância que termina sair, e o par fica sem parceiro para
acionar a reanimação que ainda espera.

**Dois defeitos na própria verificação, ambos encontrados por falhar pelo motivo errado.** A primeira
versão amostrava a pose uma vez em +1 s, independentemente do estado, e reprovou o cliente
(`20261018-225649-corpse`) - mas ele havia **morrido novamente 0,7 s após uma redefinição que comprovadamente
funcionou**, portanto `hp=0` com `Dying` era o jogo correto, não o erro. A amostra agora só conta enquanto
o anão está **vivo**, e um anão vivo em `Dying` ainda falha imediatamente. O segundo é o alerta do
manual: uma verificação que não pode falhar não prova nada, portanto `-CorpseNoReset` executa o mesmo teste com
a redefinição deliberadamente omitida. Ele informa o erro e FAIL (`20261018-231400-corpse`):

```
corpse reset  where=revive skip=flag(nreset) fixedBy=none
corpse stable alive-but-dying hp=100 alive=1 anim=Dying#-1546996312 t=2,15 restores=1/0
RESULT: corpse FAIL reason=restores=1 clean=0 stable=0/1 last='revive fixedBy=none(flag)' anim=Dying#-1546996312
```

**Lacuna honesta:** nenhuma execução aprovada teve nova morte dentro da janela de 1 s, portanto a condição de estar vivo não foi
exercitada novamente depois da execução que a motivou; o que as execuções aprovadas provam é que essa condição não pode
produzir um falso PASS. E isso corrigiu a pose do anão *local* - a animação do boneco ainda não é sincronizada
(`CoopPuppet` só controla posição), um item separado.

## <a id="both-down-ends-the-run---and-two-ways-the-first-attempts-were-wrong"></a>Ambos incapacitados encerra a partida - e duas formas em que as primeiras tentativas estavam erradas

Decisão de projeto: quando ambos os anões estão incapacitados, a partida termina como no solo. Um testador também forneceu
o mecanismo do encerramento natural do *próprio* jogo, que vale registrar porque explica todos os
fins não forçados nesta sessão: **o primeiro elite morre, a fase da cápsula de transporte começa com uma curta
contagem regressiva (21 s no caso observado), e perder a cápsula encerra a partida imediatamente** -
`MISSED_DROPPOD`. Por isso partidas terminavam sozinhas após ~4–5 minutos e uma partida que nunca chegava
lá nunca terminava.

**Tentativa 1 - apenas no patch de morte.** O patch pode perguntar "meu parceiro está incapacitado agora?", mas a vida
do parceiro chega uma ida e volta depois: medido, ambos morreram com 40 ms de diferença e cada um ainda via um parceiro vivo, portanto
ambos seguiram o caminho normal de incapacitação e a partida ficou presa por minutos.

**Tentativa 2 - na atualização, pelas flags.** `IsDowned && RemoteDowned` disparou enquanto o anão estava *em pé*: o
`IsDowned` do cliente permaneceu definido enquanto sua própria vida era 13 (`downed=1` no log da atualização, hp=13 na mesma linha),
portanto a partida foi declarada com ambos incapacitados por uma flag antiga. Isso também expôs a própria flag antiga - o
`Tick` do bot retorna cedo enquanto `IsDowned` está definido, portanto o anão ficava parado embora vivo.

**Tentativa 3 - o que está implementado agora.** Um teste compartilhado, `CoopDowned.CannotRevive()`, lê a vida realmente
presente dos dois lados (com a condição `everSawRemoteAlive`, para o substituto hp=0 do menu não ser considerado parceiro incapacitado), e
*ambos* os chamadores o usam - patch de morte (permitir o fim de jogo do próprio jogo?) e atualização (encerrar a partida) - para
não divergirem sobre o significado de "incapacitado". A atualização também limpa uma flag que sobrevive à incapacitação, baseada
na vida, porque `isAlive` deriva dela. E a regra exige `ProbeState.Gc != null`: medido, uma
versão sem essa condição disparou no menu (`selfHp=0 remoteHp=0 haveRemote=0`) e pediu para encerrar uma partida que não
existe.

**Verificado:** o falso positivo no menu desapareceu com a condição, e a limpeza da flag antiga disparou repetidamente numa
execução (`stood up on its own (hp=13), flag cleared`). O fim de jogo do próprio jogo *realmente* executa quando o patch
o permite - uma execução anterior terminou para o cliente com `end screen setup condition=DIE`, enquanto seu próprio
log mostrava `both down ... remoteHp=0`.

**Não verificado ponta a ponta, e uma nova descoberta na tentativa:** o jogo **levanta um anão incapacitado por conta
própria** - vida 0 para 13 em cerca de um segundo, três vezes numa execução, sem o caminho de reanimação do mod (sua
linha `check: revived` nunca apareceu). Portanto "ambos incapacitados" é uma janela de cerca de um segundo, não um estado
preso, e só é terminal quando ambos ficam com vida <= 0 tempo suficiente para a vida do outro lado chegar. A
regra permanece conservadora: só dispara quando a partida realmente não pode continuar, direção segura em que
errar - mas ainda é preciso produzir a execução que a verifica ponta a ponta. O que o jogo
faz com um anão incapacitado (autorrecuperação e sua interação com o estado de incapacitação do mod) é a questão
em aberto aqui.

## <a id="the-loan-ends-with-the-run-and-the-client-keeps-what-it-earned-build-2156"></a>O empréstimo termina com a partida, e o cliente mantém o que ganhou (compilação 21:56)

**Decisão de projeto** (perguntada, porque as duas regras se contradiziam): o cliente mantém seu próprio progresso
obtido, e apenas os dados emprestados continuam emprestados. Nada na transferência I1 nem no bloqueio I3 foi
enfraquecido para isso - o empréstimo agora é *devolvido* quando a partida termina, para o salvamento do próprio jogo
gravar um perfil que pertence ao cliente, acrescido de tudo que ganhou jogando.

- **Capturado antes de aplicar o empréstimo**: `CaptureOwnBorrowed()` registra as seis listas, níveis de melhorias permanentes e
  equipamentos como estão, porque após `ApplyPeerAdopt` já não pertencem ao cliente.
- **Devolvido no fim da partida**: `EndLoan()` executa no pós-fixo de `GainRunEndRankXp` (após o crédito,
  para o crédito fazer parte do que será gravado) e em `UIEndScreen.Setup` como contingência, porque uma partida pode
  terminar por `DIE`, `WIN`, `MISSED_DROPPOD` ou `ABORT`. É idempotente.
- **Por campo, e "ganho" é uma subtração, não uma permissão geral**: um ID é removido quando o anfitrião o emprestou e
  o cliente não o tinha (`host \ own`), portanto tudo que o cliente ganhou durante a partida - ausente
  de ambos - sobrevive. Níveis de melhorias permanentes mantêm os do próprio cliente mais seu aumento acima do nível emprestado; itens
  de equipamento são pareados por `HC` (hash por item, não `ID`, que é só o tipo), para uma obtenção na partida não ser
  confundida com instância emprestada.
- **Então** `BlockWrites` é liberado e `SaveDataManager.Save(true)` do próprio jogo grava. I3 continua bloqueando
  tudo *durante* a partida, mantendo o empréstimo fora do arquivo no decorrer dela.

**Erro de ciclo de vida na primeira tentativa, útil registrar porque era invisível:** o instantâneo era
limpo por `Reset("StartGame")`, mas o empréstimo é feito *no menu*, antes da partida - portanto o log do fim da partida
dizia `nothing to give back (own=False peer=True)`, e o recurso inteiro não fazia nada, embora *parecesse*
conectado. O ciclo do empréstimo agora depende da adoção, não do início da partida.

**Verificado no nível de arquivo, não pelas linhas de log do próprio mod.** Os arquivos de save são **JSON**
(`drg_save_slot{N}_{rotation}.dat`, `{"Version":9,...}`), portanto o executor agora copia os slots usados para o
arquivo da execução antes de restaurar os saves do jogador, permitindo ler diretamente o estado final:

```
client  check: loan ended why=rankXp wpn=29->0 cls=0 metaSum=90 gear=0

client slot after the run     UnlockedClassIds  weapons  meta levels  gear  classXp  credits
  drg_save_slot1_1/2.dat (*)  []                0        18 x 5       0     5958     141836
  drg_save_slot1_3.dat        []                0        18 x 5       0     5935     141818
  drg_save_slot1_0.dat        []                0        18 x 5       0     5956     141834
```

(*) a gravação mais recente (`Timestamp` 214523795, correspondente à execução).

- **A metade emprestada está ausente**: o anfitrião emprestou 4 classes, 29 armas, 18 entradas de melhorias permanentes no nível 0 e 6
  equipamentos; o arquivo do cliente não contém nenhum deles.
- **A metade ganha está presente**: o total de XP de classe do arquivo é 5958, e o próprio log do cliente mediu
  `classXp 5956 -> 5958` para `perfXp=2`. Os créditos acompanharam (141834 -> 141836). Era isso
  que antes era calculado e depois descartado.

**Ainda não exercitado pela preparação, e identificado como tal:** as regras de "ganho além do empréstimo" exigem
algo obtido durante uma partida cooperativa - uma arma ou equipamento derrubado do lado do cliente - e o mundo
do cliente tem seu gerador suprimido, portanto nem a diferença de conjuntos nem a subtração `HC` foram observadas
em execução numa partida.

## <a id="i2-first-measurement-what-a-run-end-does---and-two-harness-defects-found-on-the-way"></a>I2, primeira medição: o que faz o fim de uma partida - e dois defeitos do ambiente encontrados no caminho

A questão de I2 é o que o fim de uma partida transforma em progresso permanente, pois é aí que o perfil emprestado
de I1 e o perfil do próprio cliente se encontrariam. O ponto de entrada é declarado, não adivinhado, e
o crédito é direto:

```
host  runend: GainRunEndRankXp(161) BEFORE classXp=5956 playerRank=19 classLevels=58 runStartRank=DRILLER:14/3155
host  runend: GainRunEndRankXp AFTER  classXp=6117 playerRank=19 classLevels=58
host  runend: end screen setup condition=MISSED_DROPPOD
```

`PlayerRankManager.GainRunEndRankXp(int performanceXp)` é público, e o total de XP de classe aumentou exatamente
seu argumento (5956 + 161 = 6117). A tela final então informa a condição. Ao redor disso, pelas
*declarações* (corpos são stubs, portanto isso é o que existe, não o que foi chamado):

- `ScoreManager` transforma a partida numa pontuação com pesos explícitos - `GOLD=5`, `NITRA=7`,
  `CRAFTING_MATERIAL=15`, `RED_SUGAR=3`, `SECONDARY_OBJECTIVE=500`, `PLAYER_LEVEL=100`, `ARTIFACT=1000`,
  `WIN_MOD=1.25`, além de uma tabela de perigo - e dispara `OnFinalScore`.
- `UIEndScreen.ShowProgression(int rankXpEarned, int creditsEarned)` é o lado de exibição dos dois números.
- Maestria tem quatro gravadores: `SaveDataManager.TrySetWeaponMastery`, `TrySetClassModMastery`,
  `TrySetBiomeMastery`, `TrySetMutatorMastery`.
- Marcos passam por `MilestoneTracker.GiveMilestoneReward(MilestoneData, doSave)` e
  `MilestoneSaveUpdate.NewlyCompletedMilestones`.

**Defeito 1 - a ajuda de resgate era permanente.** O ramo de resgate do bot aumenta sua própria vida para 100000 para
o resgatador sobreviver à janela de reanimação de 5 s. O jogo *não* limita `currentHp` à vida máxima do anão, portanto
os 100000 simplesmente permaneciam: medido, um cliente cujo ramo de resgate disparou uma vez ficou com ~99900 pelo resto
da partida, sofrendo 10 de dano por golpe, e **sua partida não podia mais terminar por morte**, enquanto a do anfitrião terminava.
Uma ajuda do ambiente removia silenciosamente um resultado inteiro de todo teste que a utilizasse. Corrigido: a vida
anterior à fixação é capturada e devolvida quando o ramo de resgate termina (`bot: rescue pin released, hp back to 63`).

**Defeito 2 - ambos os anões incapacitados simultaneamente travam a partida.** Com `-NoGod`, ambos foram incapacitados com poucos segundos
de diferença e permaneceram assim: `hp=0 alive=False` por 139 atualizações do anfitrião e 119 do cliente (~3,5 minutos), sem
`UIEndScreen.Setup` e sem crédito. Ninguém pode reanimar ninguém - não existe parceiro vivo - e o estado de
incapacitação do mod impede o fim de jogo. Uma partida solo teria terminado. Isso pertence ao item de
incapacitação/reanimação (F), não a I2, mas está registrado aqui porque remove silenciosamente o fim de partida de qualquer
teste com duas mortes e porque "ambos incapacitados" precisa de comportamento definido de qualquer forma.

**A forma confiável de chegar ao fim de partida neste ambiente** é deixar a invencibilidade ativada e permitir que a missão chegue
ao seu próprio encerramento, já observado pelo piloto automático:

```
auto: watch: active=CoreOutro      <- the mission is ending (drop pod phase)
runend: GainRunEndRankXp(161) ...
auto: watch: active=UIEndScreen
```

**Visto uma vez e útil saber (F, não I2):** o caminho de incapacitação/reanimação comprovadamente executou na mesma sessão -
`check: downed remote role=client (remote hp=0)`, `check: rescue started role=client dist=13,3`,
`check: revived role=host hp=100 alive=True`. Registrado como observação; o teste próprio de F continua em aberto.

**Ainda em aberto:** gravações de maestria e marcos exigem uma partida que realmente jogue (o gatilho abaixo encerra uma
sob demanda, mas a partida encerrada não tem nada a concluir).

**Um fim de partida pode ser forçado, e isso tornou o restante mensurável.** Esperar uma missão acabar sozinha
não é um teste: de quatro tentativas, uma chegou ao encerramento, uma ficou presa com ambos os anões incapacitados e uma
não havia terminado após 9 minutos. `CoreGameEvents.TriggerCoreRunOutro(ECoreRunEndCondition)` é público e
estático, a mesma entrada usada pelo fim da própria missão, portanto `-cooprunendforce=<win|die|abort>`
executa a cadeia real sob demanda. Medição inteira: ~90 segundos, em vez de ~9 minutos, ambos os lados, duas vezes.

```
host    runend: forcing condition=DIE via CoreGameEvents.TriggerCoreRunOutro
host    GainRunEndRankXp(2)  BEFORE classXp=5956  AFTER classXp=5958   end screen condition=DIE    writesBlocked=0
client  GainRunEndRankXp(3)  BEFORE classXp=5956  AFTER classXp=5959   end screen condition=DIE    writesBlocked=0

host    GainRunEndRankXp(17) classXp 5956->5973   condition=WIN   stages=1
client  GainRunEndRankXp(18) classXp 5956->5974   condition=WIN   stages=1
```

**Cada lado credita seu próprio perfil com seu próprio desempenho** (`runStartRank` indica a classe que cada um
realmente jogou: anfitrião DRILLER, cliente ENGINEER). O caminho `WIN` se comporta como `DIE` nesse aspecto,
portanto o crédito não depende de vitória.

Marcos ficaram em 78/281 em todas as partidas *forçadas*, inclusive vitórias - mas uma vitória forçada 20 segundos
após começar não tem progressão de etapa, perigo nem marcos a concluir, portanto isso é uma limitação da
preparação e **não** evidência de que marcos não sejam afetados. Um fim de partida *real* (invencibilidade desligada, 592 mortes) os
alterou: `milestones 78/281 -> 79/282`, portanto o caminho de gravação de marcos está ativo e grava no fim da partida.

> **Corrigido posteriormente** ("Uma partida que realmente joga", abaixo). Contar apenas *conclusões* ocultava o que
> muda constantemente: a soma de `Progress` da mesma lista avança meio milhão numa partida de três minutos,
> por instância e proporcionalmente às próprias mortes dessa instância. E um fim de partida forçado *alcança* o
> caminho de conclusão de marcos - o que não alcança sem supervisão é a tela final, porque uma vitória exibe
> um popup de equipamento encontrado que nada dispensava. Portanto a limitação da preparação era real, mas localizada, e a
> frase "grava no fim da partida" estava certa pelo motivo errado.

**A colisão que I2 existe para encontrar, medida.** Com adoção ativada e o mesmo fim forçado:

```
client  check: profile-scrub ... after={0 0 0 0 0 0} metaSum=90
client  check: profile-adopt ... applied {cls=4 mod=9 wpn=29 art=13 oc=0 sets=1}
client  save: blocking the client's writes (RequestSave) - adopted unlocks are in memory only
client  runend: GainRunEndRankXp(3) BEFORE classXp=5956 AFTER classXp=5959  writesBlocked=2
client  runend: end screen setup condition=DIE
```

O cliente joga a partida, o jogo calcula e aplica seu XP de graduação, e o bloqueio de gravação de I3 então descarta
tudo: o progresso ganho pelo próprio cliente nunca chega ao arquivo, porque o bloqueio está na solicitação
de salvamento, não nos dados emprestados dentro dela. Isso é uma decisão de projeto, não erro em qualquer metade -
I3 está correto ao impedir que desbloqueios emprestados se tornem permanentes, e I2 está correto ao dizer que o jogo credita a partida -
mas as duas regras agora se contradizem exatamente nesse ponto.

## <a id="gear-transport-works-and-the-cache-needed-rebuilding-build-2103"></a>Transporte de equipamentos funciona, e o cache precisava ser reconstruído (compilação 21:03)

A terceira parte de I1: o *inventário* do cliente, não só seus desbloqueios e força. Equipamento é a primeira
coisa neste mod **estruturada**, em vez de lista de strings, e isso mudou a forma do
trabalho em dois pontos.

**1. Equipamentos não podem trafegar como objetos vivos.** `GearSaveData` tem doze membros, três deles arrays
(`S`, `SG`, `ST`); `GearEquipSaveData` tem seis arrays. A listagem em execução esclareceu o que são:

```
GearSaveData      props={ HC:Int32 ID:String R:Int32 L:Int32 U:Int32 N:Boolean
                          S:Il2CppStructArray`1 SG:Il2CppStructArray`1 ST:Il2CppStructArray`1
                          RQ:Int32 LQ:Int32 F:Int32 ... }
GearEquipSaveData props={ ID:String A,C,G,Ta,To,W:Il2CppStructArray`1 ... }
```

Portanto tudo é uma *propriedade* (novamente a regra de interoperabilidade), e todo `int[]` é um `Il2CppStructArray<int>`.
Transmitir `GearSaveData` exigiria que ambos os lados concordassem num detalhe de execução; o mod, em vez disso,
transporta itens próprios para transmissão (`GearItem`/`EquipItem`, inteiros e arrays simples, arrays como contagem + valores), e
o cliente reconstrói objetos do jogo - arrays preenchidos por índice, propriedades gravadas pelo
mesmo acessador genérico usado para leitura.

**2. O save não é o que o jogo mostra.** `GearManager` contém `AllGear` (`List<GearView>`), que, medido
na negociação, *espelha exatamente o save* - anfitrião `allGear=6 saveGear=6`, cliente `allGear=0 saveGear=0`
- como seria esperado de um cache do carregamento. Substituir `SaveData.GearSaveData` e parar aí
deixaria a tela de inventário mostrando os itens do próprio cliente, enquanto o save dizia outra coisa.

A reconstrução passa pelo carregador do próprio jogo, e o log foi organizado para indicar *qual* metade da chamada
faz o trabalho, porque os corpos descompilados são stubs e nenhuma metade pode ser deduzida deles:

```
client  RESULT: profile-adopt PASS ... {gear 0->6 hostGear=6 collected=6 glvl=18 load=3
                                        manager=0->6 loaderFilled=0} hostGear=6 loadedGear=6
```

**`loaderFilled=0` é a descoberta**: `SaveDataManager.LoadGear(GearManager)` *retorna* a lista reconstruída
(6 itens), mas **não** a armazena no campo `AllGear` lido pela interface. O mod a atribui. Se eu tivesse presumido
"o carregador carrega", o inventário teria permanecido vazio e o save pareceria perfeitamente
adotado - mesmo formato de erro da carteira de melhorias permanentes, em outro subsistema.

Os contadores foram gravados e lidos de volta (`collected=6 glvl=18 load=3`), portanto não são "nenhuma exceção, então
presumivelmente certo", mas valores comprovadamente presentes no save depois.

**Lacuna explícita: a metade do conjunto equipado não foi verificada.** `EquippedGear` é transportado e
reconstruído, mas *ambos* os perfis não têm nada equipado (`saveEquipped=0` nos dois, e o próprio
`equippedList=15` do anfitrião com lista vazia no save é coerente com "15 registros de slots, nenhum preenchido"). Uma
preparação com conjunto equipado seria necessária para mostrar que os slots do cliente acompanham - o que exige
controlar a interface de equipamentos para equipar algo primeiro no anfitrião.

## <a id="player-rank-measured-and-deliberately-not-adopted"></a>Graduação do jogador: medida e deliberadamente não adotada

O último item de I1 acabou não valendo implementar, e a evidência está nas configurações, em vez de
numa partida:

- `PlayerRankSettings` tem um membro: `ClassRanksPerPlayerRank`. `ClassRankSettings` tem um: `RankXP`.
- Portanto `Rank` deriva por classe de `Xp` pelos limiares de XP, e `PlayerRank` é um *agregado* das
  graduações de classe. Nenhum acrescenta modificador de atributo, moeda ou item.

Graduação orienta marcos, telas de progressão e a exibição "XP ganho" de `UIEndScreen` - não a força da
partida. Um cliente de graduação baixa portanto não é mais fraco, única razão para existir I1. E como
graduação *é* progresso, adotá-la contrariaria diretamente I3 (o progresso do próprio cliente deve continuar
seu) quando o crédito de fim de partida (I2) estiver implementado.

Há uma segunda razão, mecânica, para não alterá-la: `PlayerRankManager` armazena em cache as graduações lidas no carregamento
(`ranks`, `dataLoaded`, `PlayerRank`, `TotalClassLevels`) - mesma separação cache/save dos equipamentos, mas
sem nada a ganhar ao conectá-los.

## <a id="meta-levels-and-the-cached-values-they-feed-build-2045"></a>Níveis de melhorias permanentes e os valores em cache que alimentam (compilação 20:45)

A segunda metade de I1: não só o que o cliente pode *escolher*, mas quão forte é. Níveis de melhorias permanentes ficam
em `SaveData.MetaStatUpgrades` como pares `{Id, Level}`, portanto trafegam como pares e são reconstruídos com o
construtor do próprio jogo - mesma regra literal das listas de IDs.

**A parte que silenciosamente não funcionaria.** `MetaManager` não lê os níveis quando a partida precisa
deles: calcula `StartingGold`, `StartingNitra` e `ArtifactRerolls` em campos em cache, e a única
chamada de `UpdateWalletUpgrades()` está dentro do próprio `MetaManager`. Substituir níveis e parar ali
deixaria a lista parecendo perfeitamente adotada e a partida usando os números antigos - uma mudança que parece
funcionar e não funciona. Assim, o mod chama `UpdateWalletUpgrades()` após aplicar, a atualização do próprio jogo,
em vez de reimplementá-la.

**Medido, incluindo os valores derivados:**

```
client  check: profile-scrub role=client ... dwarf=00000000 metaSum=90
client  check: profile-adopt role=client received {cls=4 mod=9 wpn=29 art=13 oc=0 sets=1}
                                        meta=18 metaSum=0 gold=0 rerolls=0
client  RESULT: profile-adopt PASS ... meta 90->0 hostMetaSum=0 gold 10->0 hostGold=0 goldMoved=1
host    RESULT: profile-adopt PASS reason=peerClasses=0 deficit=1 adoptSent=2
```

`gold 10->0`: com nível 5 na preparação divergente, o cálculo de carteira do próprio jogo produziu 10 de ouro inicial, e
após adotar os níveis 0 do anfitrião e atualizar, produziu os 0 do anfitrião. A adoção alcança o
estado derivado do jogo, não apenas seu armazenamento.

**A preparação não tinha nada a medir - terceira ocorrência desse padrão.** As 18 entradas de melhorias permanentes do anfitrião estão
*todas no nível 0*, portanto `0 -> 0` parece idêntico se a adoção aconteceu ou se nunca alterou nada.
A preparação divergente então define os níveis do cliente para um valor distinto de 5, em vez de 0: seu trabalho é tornar o
perfil do cliente *diferente* do anfitrião, não mais pobre. O veredicto compara somas, portanto um perfil
intocado não pode passar - e `goldMoved` é informado explicitamente, tornando uma verificação de carteira pulada por falta
de diferença visível, em vez de silenciosamente aprovada.

**Ainda em aberto em I1:** inventário/conjunto de equipamentos e graduação do jogador. Depois I2, creditar o progresso do cliente de volta
ao anfitrião no fim da partida.

## <a id="a-run-that-actually-plays-milestones-complete-at-the-end-screen-and-mastery-is-empty-build-of-2345"></a>Uma partida que realmente joga: marcos concluem na tela final, e maestria está vazia (compilação das 23:45)

O último item aberto de I2 era a única preparação incapaz de responder: o fim forçado executava a cadeia de fim 20
segundos após iniciar a missão, portanto não havia etapas, perigo nem nada a concluir. A preparação agora existe
- `-RunEndDelay 180` joga por três minutos e *depois* termina por `CoreGameEvents.TriggerCoreRunOutro`,
de modo que a partida tem mortes, níveis e uma etapa concluída. Ampliar a sonda ao número antes
invisível transformou três leituras separadas de "nada aconteceu" em resultados.

**Marcos: a contagem de concluídos era a observação errada.** Entradas de `MileStoneStates` são
`{Guid, Progress, IsCompleted}` - lidas do arquivo de save, que é JSON - e a sonda só contava
conclusões. Assim, `78/281 -> 78/281` em todas as execuções anteriores era lido como "o caminho de gravação está morto", quando só significava
"nada cruzou seu limiar ainda". Somado sobre a lista, uma partida de três minutos o move meio milhão:

```
host    milestonesStart=78/281 p=2452142  -> 78/281 p=3022974  -> end screen: 82/284 p=3022983   kills=456
client  milestonesStart=78/281 p=2452142  -> 78/281 p=2719156  -> end screen: 78/281 p=2719156   kills=221
```

Três fatos numa linha, nenhum visível antes:

- **Progresso é gravado durante a partida**, por instância, proporcional à jogabilidade *da própria*
  instância: +570.832 no anfitrião contra +267.014 no cliente, com 456 contra 221 mortes (razão 2,14 contra
  2,06). Mesmo padrão na execução anterior (+543.036 / +266.941 contra 457 / 210 mortes). Cada lado
  avança sua própria cópia do perfil, exatamente o que a decisão posterior "o cliente mantém o que ganhou"
  pressupõe.
- **O crédito em si não altera nada** (`p=3022974 -> p=3022974`), portanto o crédito de fim de partida não é a origem do
  progresso dos marcos.
- **O caminho de conclusão executa na tela final, e só ali**: o anfitrião passou de `78/281 -> 82/284`, ou seja, quatro
  marcos concluídos *e* três novas entradas na lista. É `PostEvaluateMilestones` /
  `GiveMilestoneReward` trabalhando - o caminho que todas as execuções anteriores informavam como inativo porque a
  tela final nunca executava.

**Maestria está vazia neste perfil, e o arquivo de save confirma.** Após uma partida de três minutos com 445 mortes:

```
"WeaponSaveData":[],"BiomeSaveData":[],"MutatorSaveData":[],"ClassModSaveData":[]
```

É um slot jogado lido diretamente de um backup, não uma leitura incorreta durante a execução - as quatro listas
de maestria estão vazias, e uma partida jogada não cria entrada em nenhuma. Isso corresponde à página de tipo de partida do perfil,
onde só a campanha Mission Road está desbloqueada e **Mastery está `[unavailable]`**. Portanto o item "caminho de gravação
de maestria" do plano está **bloqueado por uma preparação, não em aberto**: precisa do modo Mastery desbloqueado (ou de um perfil
que o tenha jogado), e nenhuma quantidade de código neste perfil produzirá um número para ler.

**O bloqueio entre crédito e tela final é um popup que ninguém dispensava.** Uma vitória exibe
`UIGearFoundForm` antes da tela final, e o piloto automático - que já aprendeu a atender `UILevelUpForm`
- não tinha caso para ele, portanto o anfitrião ficava no popup de equipamento, enquanto o cliente (que não ganhou equipamento) prosseguia:

```
host  runend: GainRunEndRankXp AFTER  ... 23:44:44.660
host  phase: gearfound-open                23:44:46.024
host  runend: end screen setup condition=WIN milestones=82/284   23:44:46.058   <- 1.4 s after the credit
```

`UIGearFoundForm.OnContinueButton()` é o próprio handler do botão, portanto o piloto automático agora o chama, da mesma
forma que chama `UILevelUpForm.OnSkillChosen`. Com isso, os dois papéis informam `endScreens=1 condition=WIN`.

**E um veredicto descrevia uma cadeia ainda não terminada.** O veredicto `runend` é escrito no
pós-fixo de crédito, *antes* da tela final - portanto imprimia `endScreens=0 condition=none` e leituras
vazias da tela final (`->?`) sobre uma cadeia ainda executando. Isso foi interpretado como "o fim forçado nunca
chega à tela final", simplesmente errado: na execução sem tela final do anfitrião, o motivo era
o popup de equipamento acima, não a imposição. O veredicto agora é adiado uma ou duas atualizações (tolerância de 15 s, para uma partida
que realmente nunca chega à tela final ainda ter veredicto) e contém os valores reais.

**Correção da seção anterior:** "milestones 78/281 -> 79/282 numa partida real" é coerente com isso,
e a frase adjacente - um fim forçado "não tem progressão de etapa, perigo nem marcos a
concluir" - estava só parcialmente correta. Um fim forçado *executa* o caminho de conclusão; o que não consegue é chegar
à tela final sem supervisão, por causa do popup de equipamento.

**O que ainda não foi exercitado:** o cliente não concluiu marcos nestas execuções (seu próprio progresso é
menor), portanto "ambos os lados concluem os seus próprios" é inferido do resultado do anfitrião mais o progresso por
instância, não medido no cliente. E maestria permanece impossível de medir aqui.

## <a id="the-partners-dwarf-the-puppet-now-plays-the-pose-the-remote-is-actually-in-build-0001"></a>O anão do parceiro: o boneco agora reproduz a pose real do remoto (compilação 00:01)

A outra metade do relato do "cadáver", que a correção anterior não alterou: a pose do anão local
é reparada, mas o *parceiro* vê um `CoopPuppet` controlado apenas por posição e rotação.
Um anão incapacitado para de se mover, portanto o boneco ficava em `Idle` - um anão em pé onde a tela do parceiro
deveria mostrar um cadáver.

**Medido primeiro, e a medição mudou o plano.** A correção óbvia é controlar o
`Animator` do boneco, portanto a primeira questão era se a pose ficava ali. Ler a árvore de jogador numa partida real
(20261018-234503) resolveu: **nenhum `SkinnedMeshRenderer` em lugar algum** (`[m/0]` em todos os nós, 8 renderizadores
em `GFXContainer`), e os conjuntos de malhas não mudam entre vivo e incapacitado:

```
puppet: view local=alive ... localMesh=[6:,TankBody_Model,Cube,Cube,Quad_1x1m,GraplingHook]
puppet: view local=down  ... localMesh=[6:,TankBody_Model,Cube,Cube,Quad_1x1m,GraplingHook]
```

Portanto duas camadas candidatas estavam erradas antes de escrever qualquer coisa: não é um esqueleto com skin nem troca de malha
do corpo. O que *difere* é o estado do animador (`Idle#1432961145` versus `Dying#-1546996312`), e o boneco
já o acompanhava para locomoção (`Idle`/`Running`), portanto a pose é transportada por **animação de transformações na
hierarquia de partes do corpo** - exatamente o que `Animator` controla. Isso tornou o animador a camada
correta, mas também descartou a versão barata da correção: *derivar* incapacitado/morto da vida exige adivinhar um
nome de parâmetro, e a medição anterior (20261018-235525) mostrou a suposição resultando em `Idle` para um remoto
incapacitado.

**Assim, o estado trafega em vez de ser presumido.** Novo pacote `AnimState` (tipo próprio, não campo em
`PlayerState`: um par numa compilação antiga leria `PlayerState` incompleto e dessincronizaria todos os pacotes seguintes,
enquanto um tipo desconhecido simplesmente é ignorado). Ele contém `GetCurrentAnimatorStateInfo(0)
.fullPathHash` do jogador local, enviado quando muda e uma vez por segundo, porque o canal não é confiável e perder
"estou morrendo" deixaria o boneco do parceiro em pé sobre um cadáver até a próxima mudança de estado. O boneco
o reproduz:

```
puppet: played remote anim Idle#1432961145            <- and Running#256545655 while walking
puppet: mirror remote=down puppet={Idle#1432961145}   <- the remote is a corpse, the puppet is standing
puppet: played remote anim Dying#-1546996312          <- 100 ms later the pose is on it
puppet: sample down +1,0s dying=1 puppet={Dying#-1546996312} remoteAnim=-1546996312
puppet: played remote anim Idle#1432961145
puppet: sample up +1,0s dying=0
RESULT: puppet PASS reason=down=1/1 up=1/1            <- both roles
```

`-Test puppet` (`-NoGod -TestQuit none`, mesma preparação de `corpse`) amostra **1 s após cada mudança do estado de vida
do remoto** e conta correto ou não - formato já usado pela verificação `corpse`, portanto o veredicto é uma
proporção, não uma opinião. Precisa das **duas** metades: um boneco preso em `Dying` passa na primeira e falha na
segunda, o mesmo erro pelo outro extremo.

**Controle negativo é uma execução real, não uma opção.** Antes de o boneco reproduzir o estado remoto
(20261018-235525), a mesma amostra teria lido `dying=0` com o remoto incapacitado - a linha de log está na execução
acima (`puppet: view local=alive remote=down ... puppetAnim=Idle#1432961145`). Portanto a verificação não é cega;
falhava uma hora antes de passar.

O controle derivado de parâmetros em `CoopPuppet.UpdateAnimation` permanece apenas como **alternativa** para um par
que nunca enviou estado: é uma suposição (mapeia velocidade derivada para os nomes que parecem movimento),
e, fora disso, disputaria com a resposta real ao fazer a máquina de estados sair dela.

**O que isso não afirma:** o veredicto é sobre *estado de pose*, não pixels. O boneco agora reproduz o
mesmo estado de animador do anão do parceiro, num clone com as mesmas malhas e controlador -
que a pose de morte apareça como cadáver na tela é inferido disso e não foi verificado por
captura. As amostras também são pequenas: um par incapacitado/em pé por instância por execução, mesma convenção de `corpse`.

### <a id="the-walk-cycle-now-follows-the-same-phase-build-2231"></a>O ciclo de caminhada agora acompanha a mesma fase (compilação 22:31)

`AnimState` continha só `fullPathHash`, portanto o boneco reproduzia o estado correto a partir de seu **próprio** tempo
de clipe: a pose estava certa, os dois ciclos de caminhada não estavam alinhados. `AnimPhase` (pacote 28, não confiável,
~10 Hz) acrescenta `normalizedTime`; repete o hash de estado, recuperando também um `AnimState` perdido
por um pacote de fase. O boneco usa `Animator.Play(hash, 0, phase)` quando o estado muda e,
no mesmo estado, só corrige quando o erro de fase excede 0,1 - reproduzir o estado a cada pacote
reiniciaria a pose dez vezes por segundo.

- `-Test animphase` no bot caminhante: **PASS nos dois papéis**, `good=15/15 moved=1`
  (`20261019-223142-animphase`). Anfitrião `lastErr=0.08 corrections=0`, cliente `lastErr=0.00
  corrections=12`. `moved=1` significa que a fase remota mudou entre amostras, portanto não é uma aprovação
  trivial por Idle constante.
- Negativo `-AnimPhaseOff` (`-coopanimphaseoff`, `20261019-223338-animphase`): ambos os lados FAIL no
  estado (`phase=off (negative control)`), não por tempo limite do teste.
- Ainda em aberto: a correção é discreta (10 Hz + limiar 0,1), portanto uma mudança de estado muito rápida pode
  mostrar breve divergência antes do próximo pacote. Animações de arma/equipamento, Bosco/torreta
  e estado do animador inimigo continuam sem sincronização.

## <a id="the-loot-value-was-never-wrong---the-plan-was-build-0037"></a>O valor do saque nunca estava errado - o plano estava (compilação 00:37)

O plano tinha um item aberto desde o trabalho de saque da etapa 2: *"o valor transmitido lê 1, porque
`Pickup.OnSpawn` dispara antes de o jogo definir o valor; interceptar `set_value` ou ler um quadro depois -
cosmético"*. Ele lê um quadro depois há bastante tempo (consumo de `SpawnedQueue`), portanto a pergunta honesta
era se esse adiamento ajudava. Medir virou o item do avesso.

**O adiamento não ajuda, e não havia nada a ganhar.** Ambos os campos, na criação *e* uma atualização depois, em
130 amostras:

```
loot: send read=1 atSpawn=1 differs=0 type=CURRENCY Value=1 value=1
check: loot value= send={sent n=50 min=1 max=1 sum=50 differs=0} ...
```

`Value` é um *método* getter nesta compilação e `value` é o campo bruto, portanto ambos foram lidos. Nenhum jamais
muda, nos itens da própria preparação nem nos itens naturais de mineração misturados.

**Por que 1 é a verdade, de duas maneiras independentes:**

- **A API diz isso.** `SpawnMaterial(ECurrency material, int count, Vector3 position, float forceMod)` -
  o parâmetro é uma **`count`**, não uma quantidade de valor. `SpawnMaterial(NITRA, 5, …)` cria *cinco itens coletáveis de uma unidade*,
  e o anfitrião transmitiu exatamente cinco por geração. Não existe "valor real aplicado depois" para um item coletável
  de material; um item é uma unidade.
- **A carteira do próprio jogo diz isso.** O anfitrião coleta seus próprios itens, portanto sua carteira é a contabilidade *do jogo*,
  aumentando 1:1 com as coletas:

```
check: loot value= send={sent n=10 ...} wallet={Nitra=10} pickups=10 claims=10
check: loot value= send={sent n=50 ...} wallet={Nitra=50} pickups=50 claims=50
check: loot value= send={sent n=80 ...} wallet={Nitra=80} pickups=80 claims=80
```

**Portanto o critério PASS do plano era impossível.** Exigia `value != 1`, justamente o que esta
compilação nunca pode produzir - o item levaria o próximo agente a "corrigir" comportamento certo, e qualquer verificação
escrita a partir dele só poderia falhar. A verificação `loot` agora afirma a invariante que realmente deve valer -
um coletável contém uma unidade, e a soma corresponde à contagem (`min == max == 1`, `sum == n`), nos dois lados
do fluxo - e dá PASS nos dois papéis (`20261019-003708-loot`).

**Uma opção que não controlava nada, removida.** `-cooplootvaloff` foi escrita para devolver a leitura antiga
no momento da criação como controle negativo e depois excluída: seleciona entre dois números *sempre*
iguais (`differs=0`), portanto não consegue fazer a verificação falhar, e um controle incapaz de falhar não é
controle. A evidência é a coluna `differs=0`, não uma argumentação.

**Duas notas do ambiente das três execuções necessárias:** a verificação disparou após cinco transmissões, e o anfitrião saiu
(padrão `-TestQuit both`), portanto o cliente - que ainda não havia espelhado nada - perdeu o parceiro e
expirou; esta verificação exige `-TestQuit none`, como `corpse`. E os números da carteira no *veredicto* são lidos
naquele instante (`hostWallet={Nitra=0} hostClaims=0` no motivo PASS), portanto a série 1:1 acima é o
que deve ser lido, da linha periódica de log, não do veredicto.

## <a id="the-shop-between-stages-is-reachable-and-the-currency-now-runs-both-ways-build-0152"></a>A loja entre etapas é acessível, e a moeda agora trafega nos dois sentidos (compilação 01:52)

O marco D tinha uma metade restante: cartas de subida de nível concluídas, loja após a etapa não. Agora ela
é acessível intencionalmente, e sua economia foi medida - com a questão de projeto resolvida no meio
do trabalho.

**O fim de uma etapa pode ser forçado, e é isso que abre a loja.** Esperar uma etapa terminar sozinha é a
mesma incerteza do fim da partida (`~9 minutes, or never`), e o jogo tem o mesmo tipo de entrada:
`CoreGameEvents.TriggerStageEnd(CoreLevelEndArgs)` é público e estático, e os argumentos contêm o mesmo
`ECoreRunEndCondition` usado no fim da partida. Nova ajuda de teste `-StageEnd win`, e a loja surge **~20 ms depois nas
duas instâncias**:

```
shop: forcing stage end condition=WIN via CoreGameEvents.TriggerStageEnd role=host
shop: show #1 baseReroll=5 reroll=0/0 heal=30/0 wallet={GOLD=0 ... NITRA=35 ...} role=host
shop: caller of Show = ... < CoreGameEvents.TriggerStageEnd < CoopShop.Tick < CoopTick.Update < ...
```

Ambos os lados mostram os **mesmos preços** (`baseReroll=5 reroll=0/0 heal=30/0`), e uma compra é local e
pessoal: a cadeia do próprio jogo executa `Show -> SelectBestButton -> OnButtonSelect -> OnPurchaseComplete`; as
duas instâncias compraram itens *diferentes* (`WeaponUpgradeSkill_Damage` versus `SupportSkill_Armor`), cada uma pagando
da própria carteira. **O mod não pressiona nada na loja** - as seis interceptações de loja só escutam.

**A decisão de projeto, porque não era o que o código fazia:** cada jogador tem sua **própria loja** (as
recompensas são pessoais - uma melhoria de arma melhora a arma *daquele* jogador), mas a **moeda é compartilhada**:
coletas trafegam nos dois sentidos e ambos os lados sempre creditam, mantendo as carteiras idênticas. Mais uma barreira
de loja como a de subida de nível - **implementada e medida mais abaixo**.

**O que o código realmente fazia, em três pontos, todos corrigidos:**

- `ClaimPostfix` era **exclusivo do anfitrião**, portanto um cliente que coletasse um item espelhado não avisava ninguém. O anfitrião mantinha
  o original (mesmo saque, coletável duas vezes), e sua carteira nunca mudava por ele.
- A fila de coletas era consumida **dentro do bloco exclusivo do cliente** de `CoopLoot.Tick`, portanto `ApplyClaim` nunca executava
  no anfitrião. Medido: o cliente enviou 3 coletas, e o anfitrião contou 0 recebidas.
- `CreditWallet` **ignorava moedas salvas pelo jogo** (`Wallet.ShouldSaveValue`), deixando o coletor
  como único remunerado pelas moedas persistentes - divergência exatamente nas moedas gastas na loja.

Agora: ambos os papéis transmitem coletas, ambos as consomem, o receptor remove sua *própria* cópia (original do
anfitrião, espelho do cliente) e credita, e a condição foi removida, não invertida. A preparação
gera nitra **e** ouro sobre o anão *do cliente* (`-TestLoot`, com `-Still` para nenhum anão se afastar
dali), exercitando a direção que era silenciosa:

```
host:   claimsSent=7 claimsRecv=2 miss=0 credited=2 walletDelta={GOLD=+3 NITRA=+6}
client: claimsSent=2 claimsRecv=7 miss=0 credited=7 walletDelta={GOLD=+3 NITRA=+6}
```

As direções se espelham exatamente (7/2 contra 2/7), cada coleta recebida encontrou sua cópia local
(`miss=0`), cada uma creditou uma vez (`credited == claimsRecv`) - e **as duas carteiras aumentaram na mesma
quantidade**, como solicitado. PASS nos dois papéis, duas vezes.

**Dois defeitos encontrados no caminho, ambos do tipo silencioso que este projeto continua pagando:**

- A transmissão de coleta estava num `catch { }` vazio. Uma execução mostrou o cliente contando 7 coletas com
  `claimsSent=0`: a transmissão falhava e nada o dizia. Agora registra uma vez - uma exceção engolida num
  caminho cujo único trabalho é enviar é indistinguível de "nada aconteceu".
- `MirrorList` do cliente mantinha entradas de espelhos coletados pelo *próprio cliente* (o jogo devolve o objeto
  ao pool, a lista não se importava). É a contraparte simétrica de `ForgetOrigin` do anfitrião e, com
  cada coletável valendo 1 nesta preparação, o pareamento FIFO errado resultante seria invisível - no jogo real,
  creditaria um valor pertencente a um saque que ninguém coletou. Ambos os lados agora esquecem o que coletaram.

## <a id="a-stage-end-reached-nobody---the-client-played-stage-1-forever-build-0228"></a>O fim de uma etapa não chegava a ninguém - o cliente jogava a etapa 1 para sempre (compilação 02:28)

A barreira da loja deixou uma pergunta que acabou sendo maior. Em sua preparação, as duas lojas
abriam com ~14 s de diferença porque **cada** instância forçava seu próprio fim de etapa - algo que só funciona por ação de uma
ajuda de teste. Uma partida real não tem essa ajuda: quando a etapa de um jogador acaba, a do outro também acaba?

**Medido primeiro, sem o cliente poder forçar nada** (`-StageEndHostOnly`, portanto o fim de etapa do anfitrião é
o único existente):

```
host   02:18:06  check: stage starts=1 endsGame=0 endsAid=1 forced=1
host   02:18:51  check: stage starts=2 endsGame=0 endsAid=1 forced=1     <- host is in stage 2
client 02:21:54  check: stage starts=1 endsGame=0 endsAid=0 forced=0     <- 300 s later, still stage 1
host   RESULT: stage PASS reason=starts=2 …        client   RESULT: stage FAIL reason=timeout after 300s
```

**O fim de uma etapa não se propagava de forma alguma.** O cliente ficou na etapa 1 pela partida inteira. Os objetivos são
espelhados (`CoopObjective`, marco C), o que nunca foi suficiente: espelhar o *progresso* não encerra a
etapa da outra instância. O tempo limite de 45 s da barreira da loja do anfitrião é o único motivo de ele não travar ali - uma
preparação de partida única ocultando uma falha de dois jogadores.

**Encontrar o sinal exigiu um desvio útil de registrar:** `GameController.stageIndex` parece a leitura óbvia
e não compila - na listagem, pertence a uma classe iteradora aninhada gerada pelo compilador
(`__4__this`, `__2__current` logo acima), não a `GameController`. Funciona a entrada já usada neste arquivo:
um pós-fixo em `CoreGameEvents.TriggerStageEnd`, que dispara na instância cuja etapa termina,
com a origem contada separadamente (`aid` / `game` / `remote`). Essa distinção é toda a medição -
o fim forçado e um real são a mesma chamada.

**A correção** é um pacote `StageEnd` (22) contendo `CoreLevelEndArgs.EndCondition`, anfitrião -> cliente. O cliente
aciona a *mesma* entrada localmente, com `ApplyingRemote` definido para nunca devolver o pacote por eco. Reutilizar
`TriggerStageEnd` faz o cliente executar sua cadeia real de fim de etapa - loja, próxima etapa - em vez de
algo inventado. Medido após a retransmissão:

```
client 02:25:29.234  stage: peer ended its stage (condition=0, recv #1) -> raising it locally
client 02:25:29.251  shop: show #1 …                     <- its shop, 17 ms after the host's stage end (was 14 s)
client 02:25:30.348  shop: released after holding 0,5s    <- the barrier held 0.5 s, not the 45 s timeout
client 02:25:31.145  GameController.StartGame             <- stage 2
host   RESULT: stage PASS reason=starts=2 endsAid=1 peerShopDone=1 sent=1
client RESULT: stage PASS reason=starts=2 endsRemote=1 recv=1
```

Dois resultados: as lojas agora abrem juntas, e a retenção da barreira caiu da saída de emergência de 45 s
para 0,5 s de negociação real. A barreira funcionava desde o início; etapas separadas ocultavam isso.

**O controle negativo** (`-StageEndNoRelay`, anfitrião encerra sua etapa sem informar) reprova nos *dois*
lados, cada um com motivo diferente intencionalmente:

```
host   FAIL reason=starts=2 endsAid=1 sent=0 peerShopDone=0                                <- "I got there, alone"
client FAIL reason=no new stage 120s after the end: starts=1 ends=0/0/0 recv=0             <- the diagnosis
```

Esse formato vem de uma regra seguida pela verificação: **cada lado deve mostrar evidência do par, e um
tempo limite não é evidência.** O anfitrião chegar sozinho à etapa 2 é exatamente o que a execução quebrada fazia, portanto seu
critério é `ShopDone` do par - que só existe se o par teve loja - em vez de "avancei". O
critério do cliente é `endsRemote`, pois nesta preparação só pode obter fim de etapa do outro lado.
E, como o lado que não ouve nada não tem fim a partir do qual medir, o relógio do cliente também começa no início
de sua própria etapa; sem essa referência, o lado reprovado só informaria um simples "timeout after 300s", o
veredicto pouco útil que este projeto continua encontrando.

**Duas transições, porque uma não consegue falhar.** Ambas as metades da cadeia têm lógica de rearmar - a barreira
reinicia quando uma loja abre, e a flag `done` do par é *consumida* quando este lado sai - portanto uma única
transição mede só o caso que funciona mesmo se nenhuma rearmar. A ajuda agora repete
(`-StageEndRepeat`, relógio reiniciando após cada disparo para o próximo fim ocorrer depois da loja e na nova
etapa):

```
02:44:43.232 client shop: show #1 …                    -> released after holding 0,8s
02:44:44.981 client GameController.StartGame            <- stage 2
02:45:03.718 client shop: show #2 … (reroll=5/0)        <- the second shop, re-armed
02:45:03.727 client stage: end #2 (from the peer)
02:45:06.258 client GameController.StartGame            <- stage 3

host   PASS reason=starts=3 want=3 endsAid=2 peerShopDone=2 sent=2 forced=2
client PASS reason=starts=3 want=3 endsRemote=2 recv=2
```

Ambos os caminhos de rearmar funcionam, e a retransmissão dispara duas vezes sem eco (`endsRemote=2` no cliente, `sent=0`).
A primeira execução desta preparação foi um **falso positivo no cliente**: eu havia colocado `-coopstageendrepeat` dentro da
condição exclusiva do anfitrião no inicializador, portanto o cliente mantinha o padrão 1, verificava *uma* transição e escrevia
seu veredicto após a primeira - a segunda transição estava no log e em veredicto nenhum. A contagem é uma
expectativa, não uma imposição, e agora fica fora dessa condição. Vale generalizar: **um parâmetro que decide
o que uma verificação espera não pertence a um bloco que decide o que um papel pode fazer.**

**Limites explícitos:** a retransmissão é só anfitrião -> cliente, porque o anfitrião é a autoridade
da etapa (os objetivos do cliente são espelhos). Um fim de etapa gerado pelo próprio cliente é registrado como
`stage: end #N (game's own)` e *não* retransmitido - se isso for alcançável, é o ponto a
ampliar. Duas transições são medidas, ambas forçadas; uma etapa que termina *sozinha* (objetivo completo) nunca foi
observada em nenhum lado, e o comportamento quando ambos os lados terminam uma etapa no mesmo segundo não
foi testado.

## <a id="the-shop-barrier-built-and-the-two-bugs-it-took-build-0209"></a>A barreira da loja: implementada, e os dois erros que exigiu (compilação 02:09)

Foi solicitada ("Sim, barreira como na subida de nível") e está implementada: `UIShopScreen.OnPlayButton` é retido
por um prefixo que retorna `false` até o par informar conclusão, e liberado ao invocar o mesmo método novamente -
formato já usado por `CoopXp` em `LevelUpManager.OnLevelUpFinished`. A mensagem é um novo pacote
(`ShopDone = 21`), tipo próprio pelo mesmo motivo de `AnimState`: uma compilação antiga ignora um tipo desconhecido
em vez de dessincronizar por um pacote mais longo.

```
green  host:   show=1 play=2 holds=1 heldFor=15,6 releases=1 timedOut=0 remoteDone=1 sent=1 left=stage-start screenActive=0   PASS
       client: show=1 play=1 holds=0 heldFor=0,0  releases=0 timedOut=0 remoteDone=1 sent=1 left=stage-start screenActive=0   PASS
red    both:   show=1 play=1 holds=0 timedOut=0 remoteDone=0 sent=0                                                 (barrier off)
```

A execução reprovada é o controle negativo (`-ShopNoBarrier`): mesma preparação, todo continuar passa direto,
`remoteDone=0` - portanto a verificação distingue uma barreira que se comunicou de uma que não.

**O piloto automático primeiro precisou aprender a pressioná-lo.** Nada havia fechado uma loja numa execução automatizada: a
primeira sala que chegou a uma a deixou aberta, e uma barreira sem saída da loja não poderia ser medida.
`CoopAuto` agora pressiona o próprio `OnPlayButton` da tela, exatamente a chamada retida pela barreira,
portanto um pressionamento automatizado e um do jogador passam pela mesma lógica.

**Erro 1, e o motivo de a primeira verificação não poder funcionar: `UIShopScreen.Hide` nunca é chamado.** A
primeira execução da barreira reteve e liberou *corretamente* - anfitrião pressionou em `02:05:45.886`, reteve, recebeu a conclusão do cliente
em `02:06:01.126`, liberou após 15,2 s - e a partida prosseguiu (`GameController.StartGame` 0,6 s depois),
enquanto `hide` permaneceu 0. A verificação esperou `hide` e expirou nos dois lados. A saída observada da loja
é o **início da próxima etapa**, que agora aciona o veredicto; o próprio estado ativo da tela é registrado
nesse momento (`left=stage-start screenActive=0`), tornando a afirmação evidência, não crença.

**Erro 2, meu: `OnRemoteShopDone` nunca definia `_remoteDone`.** A mensagem era contada, registrada e tratada -
mas apenas no ramo "já estou retendo". Assim, funcionava no lado que pressionasse primeiro e
era invisível no outro. Assinatura medida: o cliente reteve por exatamente `heldFor=45,0` (tempo limite
de segurança), enquanto o anfitrião parecia perfeito, e `ShopDone` do par havia chegado *13 s antes mesmo de abrir a loja
do cliente*:

```
02:05:45.895 client: shop: remote done (localDone=False holding=False)   <- arrives with no shop open yet
02:06:00.238 client: shop: show #1 ...
02:06:01.105 client: shop: local done, holding until the peer leaves the shop
02:06:46.117 client: shop: hold timed out after 45s -> releasing
```

Não é um caso extremo corrompido; é o formato normal de uma defasagem de transição de etapa: as duas lojas **não**
abrem juntas. Esta preparação força o fim da etapa independentemente em cada instância (cada uma tem temporizador próprio de 30 s
após seu início, e os inícios das partidas tinham ~14 s de diferença), portanto o anfitrião comprou, saiu e informou
o mundo antes de a loja do cliente existir. **Um `ShopDone` recebido antes de abrir a loja deste lado significa "meu
parceiro já passou"** - exatamente o que a barreira existe para estabelecer - portanto a flag agora é mantida
através de `Show` e *consumida* quando este lado sai (`Release` ou passagem imediata). Apagá-la em
`Show` descartava a mensagem; nunca limpá-la desarmaria a barreira após um uso.

**E a verificação não detectou o erro 2.** Ela afirmava `!holding` no fim, e um *tempo limite* libera a partida
exatamente como a mensagem do par - portanto um bloqueio de 45 s e uma negociação correta pareciam idênticos. `timedOut` é
agora contado, e a verificação falha nele. Vale lembrar nas outras verificações deste repositório: quando uma
proteção tem o mesmo efeito visível que o sucesso, "recuperou" não significa "funcionou".

**A defasagem que esta seção justificou acabou sendo um erro real.** Escrevi aqui que as duas
lojas abrindo com ~14 s de diferença eram propriedade da preparação (cada instância forçando seu próprio fim), e que
se um fim real se propaga era "questão de progresso de etapa, não de loja". A primeira metade estava
certa; a segunda, errada: **o fim de uma etapa não chegava de forma alguma à outra instância** - medido, corrigido e
relatado na próxima seção. A própria barreira se comporta corretamente nas duas ordens, o que esta
preparação conseguia medir.

## <a id="play-test-observations-recorded-for-later-2026-10-19"></a>Observações de teste de jogo, registradas para depois (2026-10-19)

Quatro pontos levantados após uma sessão de jogo. Registrados com o que o código faz *hoje*, para a próxima
sessão começar com fatos, sem reler tudo. Nenhum está implementado, salvo indicação.

### <a id="1-revive-amount-flat-or-percentage-decided--50-of-max-hp--coopreviveflat-keeps-100"></a>1. Quantidade de reanimação: fixa ou percentual? (DECIDIDO — 50% da vida máxima, `-coopreviveflat` mantém 100)

Hoje é **fixa e definida no código**: `CoopDowned.ReviveHp = 100` (com `ReviveRadius = 3.0`,
`ReviveSeconds = 5.0`). O anão incapacitado portanto se levanta com exatamente 100 de vida, qualquer que seja seu máximo: com
400 de vida, é reanimação de 25%; com 150, é 67%. Qual se deseja é uma decisão real, pois
as duas produzem curvas de dificuldade muito diferentes numa partida longa. Alterar exige uma constante e uma medição,
não reformular o projeto. Vale decidir junto com o ponto 2.

**Decidido (2026-10-20):** 50% da vida máxima por padrão; `-coopreviveflat` restaura os antigos 100 fixos.
`CoopDowned.ReviveHpFor(maxHp)` é a regra única usada pelo caminho de reanimação. Uma verificação ao vivo em
`-Test revivecircle` registrou anfitrião `maxHp=145 hp=72` e cliente `maxHp=130 hp=65`, ambos `mode=50%`.
O próprio fluxo de incapacitação/reanimação foi verificado antes (`check: revived ... hp=100`); esta execução verifica a
nova regra num `Player.maxHp` real (`Stat.Value`), não numa constante calculada à mão.

### <a id="2-a-visible-fill-circle-like-the-mission-objectives-implemented"></a>2. Um círculo visível de preenchimento, como os objetivos de missão (IMPLEMENTADO)

Hoje **não há visual**: reanimação é raio de 3 unidades e temporizador de 5 s, e o único vestígio é uma linha de log
(`revive: started` / `revived`). O jogo já desenha um círculo que preenche para objetivos de missão, portanto o caminho barato
é reutilizá-lo: decalque de área no chão ancorado no anão incapacitado, preenchendo enquanto o sobrevivente fica
dentro. Restrição aprendida no trabalho do HUD: malhas procedurais e shaders internos **não** renderizam nesta
compilação, portanto deve reutilizar o visual de área no chão do próprio jogo em vez de desenhar um círculo.

**Implementado (2026-10-20):** `CoopReviveVisual` clona `ActivationZone.areaProjector` (o círculo real de missão,
shader `FX/FX_Decal_Zone`) num `DecalProjector` local, ajusta sua escala com o progresso e grava
`_Fill_Factor` do shader. O jogador incapacitado vê o círculo ao redor de si; o sobrevivente executa o mesmo temporizador de 3 m /
5 s contra `CoopNet.RemotePos` e o vê ao redor do parceiro. Não precisa de pacote, pois só
o visual é calculado. `-Test revivecircle` positivo `20261020-011703-revivecircle`: `prefab=Projector`,
`hasFillFactor=1`, 329/332 atualizações, PASS nos dois; negativo `-ReviveVisualOff`
`20261020-011516-revivecircle`: `created=0`, FAIL nos dois. A alternativa GroundZone permanece para partidas sem
`ActivationZone` na cena; a missão atual de teste tem duas.

### <a id="3-monsters-stutter-and-never-turn-on-the-client-fixed--see-enemy-mirror-smoothing--facing-below"></a>3. Monstros engasgam e nunca giram no cliente (CORRIGIDO — veja "Suavização + orientação de espelhos de inimigos" abaixo)

- **Engasgos:** posições de inimigos trafegam anfitrião -> cliente como `EnemySnapshot` a **2 Hz**
  (`CoopEnemy.SendSnapshots`, `Time.frameCount % 30 == 0`), e o cliente **define a posição diretamente**, sem
  interpolação. Duas atualizações de posição por segundo, instantâneas - essa é a trepidação observada.
- **Sem rotação:** rotação **nem sequer trafega na rede**. Pacote 8 contém apenas `(id u16, q-pos 3s16)`, e
  os espelhos também ficam congelados (`SetAgentEnabled(false)`), portanto sua própria IA tampouco pode girá-los.
- Não é regressão, mas o limite visível do projeto atual. A correção tem duas partes independentes:
  (a) suavizar o fluxo existente de 2 Hz (mover rumo ao último instantâneo em vez de saltar, ou aumentar a taxa /
  enviar deltas) e (b) transmitir a orientação para o espelho girar - ângulo compactado u8 custa um byte por
  inimigo por instantâneo. O enxame atinge perto de 260 entidades vivas, portanto trabalho por inimigo por atualização deve ser barato.
- Já medido e não deve ser confundido com isto: `check: snapshot applied=… missed=…` mostra que as
  *posições* chegam e são aplicadas. A reclamação é de suavidade e orientação, não de dados ausentes.
- **Resolvido (2026-10-20):** orientação agora é um byte compactado no instantâneo, e o cliente move cada
  espelho rumo à posição mais recente com limite de velocidade e por quadro, em vez de saltar. Positivo e
  ambos os controles negativos registrados na seção final deste arquivo.

### <a id="4-xp-on-the-ground-is-not-synced-fixed--see-xp-orb-sync-below"></a>4. XP no chão não é sincronizado (CORRIGIDO — veja "Sincronização de orbes de XP" abaixo)

- O que **é** sincronizado é o **total de XP**: cada `Player.GainXp` é espelhado como `XpGain` (pacote 3) e aplicado
  com `scaleByXpGain: false`, portanto ambos os anões sobem de nível juntos (verificado: totais idênticos nos dois lados).
- O que **não** é sincronizado são os **orbes no chão**. Diferentemente de moedas, transmitidas como
  `LootSpawn`/`LootClaim`, coletáveis de XP não têm pacote. Cada instância só vê orbes gerados por suas *próprias*
  mortes: anfitrião mata, anfitrião vê orbes, cliente não - e o XP ainda chega como número,
  exatamente por isso os totais coincidem enquanto o chão parece vazio.
- Se os orbes devem ser visíveis aos dois (pedido justo - são o principal retorno de "o combate recompensa"), o
  formato é o mesmo do saque: transmitir a criação do orbe, removê-lo nos dois lados quando qualquer jogador coletar,
  e fazer o lado coletor enviar a coleta. É preciso evitar XP duplo: o total já é
  espelhado, portanto um orbe espelhado não pode também conceder XP localmente.
- **Resolvido (2026-10-20):** orbes trafegam como pacote 30 (`XPManager.Spawn`), coletas como pacote 31
  (`XPManager.Claim`/`FinishPickup`). O receptor encontra o orbe no buffer estático
  `XPManager.xpPositions` e o remove sob `ApplyingRemoteXp`; `Player.GainXp` é
  suprimido para essa cópia, portanto só `XpGain` do coletor é aplicado. `-Test xpsync`
  `20261020-005304-xpsync` PASS nos dois (`spawnSent=16`, `claimSent=15`, cliente `applied=16`,
  `suppressed=8`); `-XpOff` `20261020-005512-xpsync` FAIL. Detalhes no fim deste arquivo.

## <a id="arena-test-fixture-2026-10-19"></a>Preparação de teste de arena (2026-10-19)

O bot caminhante é ruim para verificações estáticas: os anões circulam, terreno e ritmo das ondas mudam
a câmera, e não é possível estacionar um projétil ou alvo a uma distância conhecida. Uma arena opcional foi acrescentada
ao protótipo local e medida.

- Opções: `-Arena` (anfitrião + cliente), `-ArenaProbe` (só medir), `-ArenaNoClear` e `-ArenaWaves`
  (controles negativos), além de substituições de raio/separação/distância do alvo/tipo do alvo. Padrões:
  `radius=10`, `separation=2`, `dummy distance=2`, `dummy=GRUNT0`. O bot caminhante antigo permanece
  padrão para testes de enxame/objetivo.
- A arena é ancorada na caverna ao redor do início do jogador (não no centro do mapa; o centro era uma parede e
  a câmera permanecia na cápsula), limpa esse raio por `MineableBlock.Die` do próprio jogo,
  suprime ondas do anfitrião, cria um alvo `LEVEL_START` e posiciona ambos os anões em pontos fixos.
- **Medido:** `check: arena-clear role=host cleared=57 open=0 rocks=57 veins=0 ms=2
  anchor=(17.2,0.0,39.9)` e o mesmo no cliente; `check: arena dummy role=host type=GRUNT0 id=1
  pos=(17.2,0.0,41.9) hp=1000000000 pinned=1 enemies=1`; cliente `check: arena info ...
  dummyPos=(17.2,0.0,41.9) ... near=1 mirrors=1`; ambos os lados `RESULT: arena PASS ...`.
- Controles negativos nomeados: `-ArenaWaves` → anfitrião `RESULT: arena FAIL reason=WAVES_LEAKED ...`, e
  `-ArenaNoClear` → ambos `RESULT: arena FAIL reason=NOT_CLEARED ...`.
- Dois erros expostos e corrigidos pela preparação: o teste de limpeza comparava distância a um raio **ao quadrado**
  (`d <= r2`), portanto uma arena de raio 10 limpava 1872 blocos (quase o mapa inteiro) e deixava ambas
  as câmeras enquadrando partes sem relação da caverna; e o detector de abertura do anfitrião lia apenas as últimas 60 linhas do log,
  portanto continuava clicando no centro de jogos já em andamento. O indicador remoto do cliente também usava
  `Camera.main` (câmera da interface nesta compilação), em vez de `CameraController.cam`, e informava todo
  anão remoto como fora da tela. O auxiliar de captura agora coloca as duas janelas lado a lado.
- **Não afirmado:** teste `hit` da arena (`-Test hit -Arena`) ainda informa `HitsSent=0`; eventos de disparo do cliente
  são retransmitidos, mas o espelho do alvo não sofre dano. A preparação normal de `hit` já
  verifica dano do cliente chegando ao anfitrião (`sent=20 applied=20`), portanto é seleção de alvo da arena, não
  um defeito cooperativo recém-descoberto. A câmera do jogo ainda antecipa o movimento e coloca o anão local perto da
  borda inferior; cosmético, não investigado.

**Veredicto:** manter a arena como preparação estática opcional (posições fixas, um alvo, supressão de ondas,
limpeza de blocos) e parar de investir em seus subcasos de câmera/golpes. Já compensou o esforço ao
encontrar erros de limpeza excessiva, abertura e indicador. Usar a preparação caminhante para testes de enxame/objetivo e
seguir para o próximo marco cooperativo; revisitar a arena só quando for necessária uma verificação estática de combate/visual.

## <a id="objective-state-at-run-start-the-boolo-kappe-812"></a>Estado dos objetivos no início da partida (o Boolo-Kappe 8/12)

Observado: o objetivo secundário mostrava `SAMMLE BOOLO-KAPPE 8/12` desde o começo de toda missão,
embora nada tivesse sido coletado. Dois fatos separados explicavam:

1. **8/12 é a meta do objetivo, não seu progresso.** `ObjectiveProgress.progress` é 0 no
   início (`check: objective-start role=host primary[COLLECT_POINTS=0] secondary[LEVEL_PICKUP=0]`).
   O texto `8/12` do HUD é a meta/definição do objetivo (quantidade exigida de Boolo-Cap), não o
   progresso em execução que espelhamos, portanto "nada coletado ainda" está correto, e o rótulo não muda até
   o próprio objetivo mudar. O valor realmente coletado é o campo `ObjectiveProgress.progress`,
   que é 0 no início.
2. **Toda missão escolhia o mesmo secundário porque a semente era fixa.** `CoopNet.SharedSeed` era
   a constante `20261017`; `CoopObjective.SeedPrefix` inicializava `UnityEngine.Random` com ela antes de
   `SetupSecondaryObjectives`. Pior, a primeira tentativa gerava a nova semente em
   `OnCoreRunStarted`, que executa *após* `SetupSecondaryObjectives` no anfitrião: ele escolhia seu
   secundário com a constante antiga, enquanto o cliente usava a nova semente (observado anfitrião
   `objective: seeded Random=20261017`, cliente `objective: seeded Random=901174632`).

Correção: o anfitrião agora gera nova semente aleatória no prefixo de `SetupSecondaryObjectives`, imediatamente
antes de `UnityEngine.Random.InitState`, e o cliente a recebe pelo envio periódico existente de
`RunConfig`; `MapGenerator.CreateMap` usa o mesmo valor. Semente fixa só está disponível
para testes reproduzíveis (`-coopseed=<int>` / `coop-run.ps1 -Seed <int>`). Medido numa execução de arena
com semente aleatória: anfitrião `run: new shared seed=-802946283`, ambos os pares
`objective: seeded Random=-802946283` antes de `SetupSecondaryObjectives`, ambos
`map: seeded Random=-802946283`, e o teste de arena PASS (`cleared=35`). A caverna e o objetivo
secundário agora são aleatórios por missão e idênticos nos dois pares.

`CoopObjective.Reset` em `StartGame` e `OnCoreRunStarted` só limpa o rastreador em cache, o
mapa `Latest` e os pacotes enfileirados, para a próxima etapa/partida não continuar gravando no rastreador anterior.
Deliberadamente **não** zera o progresso dos objetivos do anfitrião: isso alteraria o estado real
do jogo e não atualizava o HUD. Se a meta 8/12 continuar aparecendo, é o secundário Boolo-Cap
selecionado para aquela semente; o progresso real é o valor separado de `ObjectiveProgress`.

## <a id="milestone-g-in-game-hostjoin-ui-2026-10-19"></a>Marco G: interface de hospedar/entrar dentro do jogo (2026-10-19)

- `CoopJoinUI.cs` desenha um painel de IP direto/LAN (endereço, porta, Host, Join, F8 para ocultar) antes da partida,
  inclusive na abertura da editora, e chama o mesmo `CoopNet.Init` em execução usado pelas opções `-coophost` /
  `-coopclient`. Define a fase do bot do cliente; as barreiras existentes de configuração/mapa/objetivo não
  mudam, portanto o anfitrião ainda inicia a partida e o cliente segue.
- O modo `-Ui` do inicializador inicia ambas as instâncias **sem** opções de papel, passa `-coopui` e
  `-cooplog=host|client` (logs separados para os dois processos simultâneos), e o auxiliar de clique
  pressiona Host na janela do anfitrião e Join na do cliente nas coordenadas fixas do painel.
- **Verificado:** `RESULT: ui PASS reason=ui role=host peer=1 peers=1` e o mesmo para o cliente, sem
  opções de papel. A execução ponta a ponta `-Ui -Arena -Test arena` também deu PASS (`cleared=26`, `peer=1`,
  `peerMirrors=1`) com papéis escolhidos pela interface. O teste `ui` falha em 45 s se faltar qualquer papel ou o
  par.
- **Não incluído:** sala/relay/convite Steam. Exige conta Steam e aprovação
  explícita; a interface atual é só LAN/IP direto (UDP 9050 por padrão, mesma compilação do jogo nos dois
  lados). F8 oculta o painel; o caminho de papel por linha de comando permanece para todos os demais testes.

Os campos de texto do painel são um pequeno botão de foco por clique com caracteres IMGUI, porque a assembly
de interoperabilidade não expõe `GUI.TextField`; endereço/porta padrão (`127.0.0.1:9050`) dispensam digitação para
duas instâncias no mesmo PC.

## <a id="grenade-mirror-with-different-loadouts-2026-10-19"></a>Espelho de granadas com conjuntos de armas diferentes (2026-10-19)

O próprio lançamento já era espelhado (`GrenadeThrow`, pacote 25): nome da habilidade, origem e direção,
reproduzido com `Grenade.Throw(..., isOriginal:false)` e explosão com dano suprimido. Só passava
quando **ambos** os anões tinham a mesma granada. O caso realista - receptor sem a granada do
anfitrião - falhava com `NO_EXPLOSION`: o receptor recorria a um
`Object.Instantiate` simples do prefab, sem pool/handler de granada inicializado; assim a granada voava,
mas nunca explodia.

O que não funcionou, ambos medidos:

- Criar o handler no lançamento (`AddWeaponHandler` + `Init`, com e sem adicioná-lo a
  `Player.weapons`) lança uma NRE mascarada ou deixa um handler cujo `GetGrenadeFromPool()` é nulo.
  Um handler criado depois do início da partida não é acionado.
- Tratar "existe um `WeaponHandler` com este nome de habilidade" como "já possuo" era um falso sinal:
  o handler criado pela metade correspondia pelo nome enquanto seu pool ainda era nulo, portanto a adoção pulava a única
  chamada que o corrigiria. **`Player.HasWeapon(data)` é o único predicado confiável.**

A correção tem duas partes:

1. `GrenadeLoadout` (pacote 26), anfitrião -> cliente: as habilidades de granada realmente contidas em `Player.weapons`
   do anfitrião, enviadas no início da partida e quando o conjunto muda (uma carta pode acrescentar uma).
2. `CoopGrenade.TryAdoptPending` equipa cada uma por
   `Player.EquipNewWeapon(data, false)` do próprio jogo na janela entre `OnCoreRunStarted` e `StartGame`
   (mesma janela usada pelo estímulo `-DevGive`), tentando por 20 s porque `EquipNewWeapon` lança exceção
   até o jogador da partida estar realmente pronto. `Adopted` é cumulativo, não zerado em `StartGame`: a
   redefinição de início havia apagado exatamente o fato informado no veredicto.

Medido (`coop-run.ps1 -Deploy -Auto -Arena -Test grenade-mirror-damage -DevGiveHostOnly
-DevGive GrenadeWeaponSkill_HEGrenade`, execução `20261019-201723`):

```
client: check: grenade host-loadout recv=2 n=1 [GrenadeWeaponSkill_HEGrenade]
client: check: grenade adopt 'GrenadeWeaponSkill_HEGrenade' via=EquipNewWeapon handler=yes weapons=1->2 registered=1
client: check: grenade mirror spawned skill='GrenadeWeaponSkill_HEGrenade' … via=pool
client: grenade: mirror exploding (damage suppressed)
client: RESULT: grenade-mirror-damage PASS reason=sent=1 spawned=1 exploded=1 adopted=1
host:   RESULT: grenade-mirror-damage PASS reason=sent=1
```

Três mudanças desta execução além do recurso:

- Um lançamento que chega enquanto o receptor ainda está no **menu** é descartado (`Gc == null`), em vez
  de criar contra o anão do menu. A antiga criação de handler durante a partida fez exatamente isso na primeira
  tentativa e prejudicou a adoção posterior.
- O teste reconhece papéis: o anfitrião pode passar como remetente, mas o **cliente deve mostrar o espelho recebido
  sendo criado e explodindo**. Com adoção, o cliente também lança sua própria granada, e a regra antiga
  `sender || receiver` aprovava o cliente antes de o espelho recebido explodir
  (`sent=1 spawned=1 exploded=0`).
- **Efeito colateral conhecido, ainda não alterado:** a adoção dá a arma ao receptor, portanto ele também
  dispara essa granada. Uma variante apenas visual - criar handler/pool no início da partida e depois removê-lo de
  `Player.weapons` para o jogo não o acionar - manteria os conjuntos distintos e ainda precisa de sua
  própria medição.

## <a id="run-start-load-barrier-2026-10-19"></a>Barreira de carregamento no início da partida (2026-10-19)

Requisito de projeto: o anfitrião inicia a partida; o cliente adota todas as configurações e só escolhe seu próprio
personagem; e as duas partidas não devem começar até **ambos** os lados concluírem o carregamento. A adoção
de configurações já fazia a segunda parte. O problema de tempo era real: nas execuções acima, o
`StartGame` do anfitrião e o do cliente tinham **14–16 s de diferença**, portanto um anão já estava na caverna enquanto
o outro ainda carregava.

`CoopLoad.cs` implementa a barreira com a entrada de pausa do próprio jogo:

- `OnCoreRunStarted` a arma (uma nova partida, não uma transição de etapa).
- O pós-fixo de `GameController.StartGame` marca "carregado", e a atualização seguinte chama o público
  `GameController.PauseCore()` e envia `RunLoaded(ready)`.
- O anfitrião espera sua própria prontidão **e** a do cliente; então envia `RunLoaded(go)` e chama
  `UnpauseCore()`; o cliente despausa quando `go` chega. Um tempo limite de 30 s libera um par perdido, para a
  barreira não bloquear uma sessão (mesmo formato das barreiras de subida de nível, loja e etapa).

Duas descobertas do teste:

- **O `ready` do lado mais rápido pode chegar antes de o lado mais lento sequer armar a barreira.** Medido: cliente
  `load peer-ready` em 20:09:52, seu próprio `OnCoreRunStarted` em 20:10:05. A primeira versão redefinia
  `PeerReady` ao armar, e o cliente então informava `peer=0`, apesar de `readyRx=1`. O pacote agora
  contém a **semente compartilhada como época da partida**; uma prontidão da época atual sobrevive ao armamento, uma antiga
  não pode liberar a nova partida.
- **`PauseCore` realmente pausa o jogo.** Durante a retenção de 23,7 s do anfitrião, sua posição e contagem de inimigos
  ficaram constantes, enquanto o contador `steps` do bot continuou aumentando (`Update` do mod executa, o tempo do jogo
  não). `IsPaused()` leu 1 nos dois lados.

Medido com um cliente deliberadamente atrasado (`-Test load -LoadDelay 8`, que passa
`-cooploaddelay=8` apenas ao cliente; execução `20261019-202123-load`, que também informa
`saves: restored and verified (14 files, canary removed)`):

```
host:   check: load held role=host paused=1
host:   check: load go sent role=host wait=23,5s
host:   RESULT: load PASS reason=local=1 peer=1 go=1 paused=1 held=23,5s timeout=0
client: check: load held role=client paused=1 delay=8,0s
client: check: load local-ready role=client after=8,0s
client: check: load released role=client via=go held=8,0s peer=1 go=1 paused=1
```

O controle negativo é uma instância só (`-Only host`): nenhum par informa prontidão, portanto a partida deve
liberar por tempo limite e o veredicto deve ser `FAIL timeout=1`.

**Escopo honesto:** "carregado" é `GameController.StartGame`, ponto em que o nível é jogável, não uma interceptação
do formulário literal da tela de carregamento. O resultado visível é o nível na tela, congelado até o parceiro
estar pronto; então ambos despausam.

## <a id="camera-frames-both-dwarves-2026-10-19"></a>Câmera enquadra os dois anões (2026-10-19)

A câmera segue um `Player`, portanto, no círculo do bot de teste, o parceiro simplesmente não aparece:
os dois bots percorrem o mesmo círculo em fases opostas, ou seja, **20–23 unidades de distância** pela partida inteira.
O marcador fora da tela (`CoopIndicator`) compensava, mas um marcador não é o parceiro.

A origem do projétil **não** era o erro: a execução de granadas registra
`mirror spawned … from=(97.7,1.0,68.7)` contra `remotePos=(97.7,0.0,68.7)` (execução
`20261019-201723`) — o espelho começa no ponto de disparo do anão remoto, uma unidade acima dos pés.
O que o fazia parecer "vindo do nada" era o ponto de disparo poder estar fora da visão local.

Câmera medida (sonda `-coopcameraprobe`, execução `20261019-203618-camera`):

```
vcam=CinemachineVirtualCamera follow=Player lookAt=none
pipeline=CinemachineTransposer/CinemachineComposer/CinemachineBasicMultiChannelPerlin
lensFov=25,0 lensOrtho=0 aspect=1,78 (host) / 1,50 (client)
transposer followOffset=(-9.6,33.9,-26.0) binding=LockToTargetWithWorldUp
```

Portanto o jogo **não usa FramingTransposer**, e o enquadramento nativo de grupo `CinemachineTargetGroup`
(a solução limpa, com enums e campos expostos pela interoperabilidade) exigiria substituir o componente
de corpo da câmera do jogo. Isso não foi feito. Em vez disso:

- Uma transformação `CoopCameraFocus` fica no **ponto médio** dos dois anões e é atribuída como
  `vCam.Follow`; o `CinemachineComposer` existente mira ali, tornando os anões simétricos.
- O próprio `m_FollowOffset` do transposer é multiplicado por `1 + max(0, sep-10)/40`, limitado a 1,6. Isso
  afasta a câmera na direção isométrica do jogo: amplia a visão sem alterar FOV/perspectiva
  e sem mover a câmera para dentro da caverna.
- `Follow`, deslocamento e todo campo alterado pelo módulo são restaurados no início da partida e quando não há
  remoto, preservando solo/menu. `-coopcameraoff` mantém o acompanhamento original como controle.

Medido na compilação final (execução `20261019-204847-camera`, sem arena):

```
host:   RESULT: camera PASS reason=mode=focus+dolly samples=20 far=20 farVisible=19 both=19 maxSep=21,8
client: RESULT: camera PASS reason=mode=focus+dolly samples=20 far=20 farVisible=20 both=20 maxSep=20,6
```

A compilação imediatamente anterior (execução `20261019-204538-camera`) mediu **20/20 ambos** nos dois lados;
a única amostra ausente na compilação final é um transiente de amortecimento da câmera, coberto pelo marcador
fora da tela. O z da área visível dos anões aumentou de ~40–48 (original) para ~49–63 com o afastamento; todo
quadro amostrado, exceto esse, tinha ambos dentro da área visível. O controle negativo é a mesma medição
com `-coopcameraoff`:

```
host:   RESULT: camera FAIL reason=mode=none … far=20 farVisible=5
client: RESULT: camera FAIL reason=mode=none … far=20 farVisible=1
```

O teste `camera` só conta amostras com separação ≥ 12 e exige ≥ 90% com o remoto
na área visível; baseia-se em estado, não em tempo limite. O marcador fora da tela permanece como alternativa
para casos extremos (um jogador que corre para muito longe).

## <a id="enemy-hp-sync-the-client-keeps-its-own-damage-numbers-2026-10-19"></a>Sincronização da vida inimiga; cliente mantém seus próprios números de dano (2026-10-19)

Esclarecimento de projeto: o cliente não deve ver os números de dano do anfitrião - os próprios bastam. Eu havia
criado primeiro um canal `EnemyDamage` anfitrião->cliente (cliente `events=10 total=400 text=10/0` via
`DamageTextAnimationSystem.SpawnText`, que exige `PreWarm()` em `DamageTextSystem(Clone)`),
medido e depois removido. O que realmente faltava era o valor de vida.

- `EnemySnapshot` agora contém `hp(i32)` por entrada (blocos de 100 entradas, 12 B cada, em vez de 120 x 8 B).
  O cliente só aplica dano: `currentHp = min(currentHp, snapshotHp)`. Um instantâneo
  anterior ao próprio golpe informado pelo cliente portanto nunca cura o espelho; a próxima atualização do anfitrião
  alcança o valor.
- As próprias armas do cliente já chamam `TakeDamage` no espelho localmente, portanto seus números são
  imediatos. Não existe evento de número do anfitrião, e ele continua aplicando golpes do cliente com `doFx=false`.
- PASS (`20261019-210726-hpsync`, arena): anfitrião `hits=10 total=351 dummyHp=999999856 snapSent=34`;
  cliente `snapSeen=11 equal=6 drops=1/82 above=4`. Os próprios golpes do cliente nunca acertaram nesta
  preparação (`hit sent=0/0`), portanto toda queda observada veio do anfitrião - evidência direta do
  caminho anfitrião->cliente.
- Controle (`20261019-211019-hpsync`, `-HpSyncOff`): cliente FAIL por estado
  (`snapEntries=31 hpSeen=0 hpSync=off`), não pelo tempo limite genérico; anfitrião continua PASS.
- Limite conhecido: só dano, portanto cura inimiga não é espelhada. Nenhum inimigo que se cura aparece no
  conteúdo testado. O alvo de arena fica com ~1e9 de vida, portanto os valores absolutos são pequenos relativamente
  ao total; contadores de quedas, não o total, são a evidência.

## <a id="mirrored-muzzle-flash-2026-10-19"></a>Clarão de disparo espelhado (2026-10-19)

O clarão de disparo do jogo é uma luz, não um prefab: `ProjectileWeaponSkillData.FlashSettings`
(`ImpactFlashSettings`: cor/alcance/duração/atraso/Enabled) é entregue a
`Assets.Scripts.VFXSystem.ImpactLightsManager.AddLight(position, settings)`. `CoopCombat.Drain` agora
chama `Flash(e)` para cada Fire recebido, antes e independentemente do espelho de projétil (com
`-cooptrace` desligado não há projétil, mas o clarão ainda acontece). `Lights()` encontra o gerenciador da cena
por `Resources.FindObjectsOfTypeAll`, guarda em cache e registra encontrado/MISSING no primeiro uso.

- Verificado (`20261019-213116-muzzle`): cliente `flashes=8 disabled=2 failures=0` (`ProjectileWeaponSkill_Subata`
  do anfitrião), anfitrião `flashes=0 disabled=10` (`Bosco_ProjectileWeaponSkill_Base`
  do cliente, cujo `FlashSettings.Enabled=false` nos próprios dados do jogo).
  `disabled=10` com `flashes=0` no anfitrião inicialmente pareceu "o código nunca executou", porque a
  linha de atualização omitia o contador de desativados; a linha inicial `coop flags: muzzle=True` e o campo
  `disabled` no veredicto resolveram. Contadores aparecem como
  `muzzle=flashes/noSettings/failures/disabled`.
- Negativo (`20261019-213321-muzzle`, `-MuzzleOff`): ambos FAIL por estado
  `fireRecv=10 flashes=0 muzzle=off`, não pelo tempo limite genérico.
- O cliente da automação carrega Bosco, para o qual o jogo não produz clarão; essa direção é
  "desativação respeitada", não "sem código de clarão". Um cliente com arma produz as mesmas chamadas AddLight no
  anfitrião. Não se inventa clarão para uma arma que explicitamente o desativa; apenas um recurso de configurações **ausente**
  recorre a um pequeno padrão de cor quente.

## <a id="weapon-coverage-per-handler-vs-per-weapon-and-the-muzzle-origin-2026-10-19"></a>Cobertura de armas, por handler versus por arma, e a origem do disparo (2026-10-19)

Questão em aberto: cada arma precisa de código próprio? **Não para armas de projétil.** A interceptação Fire fica
em `ProjectileWeaponHandler.ShootProjectileInDirection`; o par resolve
`ProjectileWeaponSkillData` pelo nome do recurso e usa `ProjectilePrefab` e
`ProjectileSettings` desse recurso. Um caminho de código atende todas. **Testes** por arma ainda são necessários porque
os recursos contêm prefabs/configurações diferentes, e código por **categoria** é necessário para handlers que
não são `ProjectileWeaponHandler`.

Medido com `-Test weapons -Mirror -DevGive "…"` (execução `20261019-215130-weapons`, 10 habilidades):

- espelhadas nos dois lados: `Subata`, `Bosco_ProjectileWeaponSkill_Base`, `M1000`, `Boomstick`,
  `ImpactAxeSkillData` - `noAsset=0 noPrefab=0 failed=0`.
- nunca disparadas pelo caminho simples `-DevGive`: `AutoCannon`, `Leadstorm_Minigun`,
  `GrenadeLauncher_PGL`, `AlternatingProjectileSkillData_Boltshark`,
  `LinkProjectileSkillData_BreachCutter`, `BeamWeaponSkill_Electrical_TH0R`. O caminho simples acrescenta todas
  as armas, mas a automação só dispara a que estava ativa no início da partida, além de Bosco.

A varredura (`-DevSweep <sec>`) torna a matriz real: limpa `Player.weapons`, equipa uma habilidade por vez
no slot 0 da barra e dispara por `ProjectileWeaponHandler.ShootProjectileInDirection`
(mesmo caminho observado pela interceptação). Execuções:

- `20261019-220450-weapons`: `AutoCannon` 9/10 e `Leadstorm_Minigun` 9/9 aplicadas nos dois lados;
  `Boltshark` chegou ao espelho, mas `noPrefab`; `PGL` retornou da chamada manual sem Fire;
  `BreachCutter` era `not-projectile`; a última arma (feixe) foi pulada por erro de ordenação.
- `20261019-220839-weapons` com o resolvedor alternado: `Boltshark` espelha ambos os prefabs,
  `DamageProjectile_Electric_Bolt` e `DamageProjectile_Acid_Bolt` (27/28 anfitrião, 32/33 cliente,
  `applied`), e a última arma agora recebe sua janela.
- `AlternatingProjectileSkillData` herda de `ProjectileWeaponSkillData`, mas tem `Projectiles[]`, não um
  único `ProjectilePrefab`; `SpawnMirrorProjectile` agora percorre esse array circularmente.

O que resta é realmente por categoria de handler, não por arma:

- `LinkProjectileSkillData_BreachCutter` — **concluído.** O handler é `LinkProjectileWeaponHandler`
  (não `ProjectileWeaponHandler`); um pós-fixo Harmony em seu `Get()` público envia o mesmo pacote Fire
  com `pData.name`, `firePoint` e o `externalAimDirection` da base. Verificado
  (`20261019-222018-weapons`): `LinkProjectileSkillData_BreachCutter` aplicada 9/10 nos dois lados,
  `noAsset=0 noPrefab=0 failed=0`.
- `ProjectileWeaponSkill_GrenadeLauncher_PGL` — **concluído.** A varredura agora segura o gatilho
  (`CoopDev.HoldTrigger`, só desenvolvimento; `Player.ShouldManualTriggerWeapon` retorna verdadeiro e
  `primaryTriggerDown` é reafirmado após `Player.Update`), em vez de gravar o campo uma vez; assim,
  a lógica de ativação do próprio jogo dispara. O tiro é observado em
  `Grenade.ShootGrenade(WeaponHandler, Vector2, GrenadeLauncherSkillData, Vector3, bool)`, método de base
  sem sobrescrita. A interceptação da base `ProjectileWeaponHandler.ShootProjectileInDirection` não consegue
  ver a sobrescrita de PGL, e aplicar patch ao virtual e à sobrescrita é o travamento documentado `0xc0000005`,
  portanto a entrada de lançamento da granada é a interceptação segura. Execuções `20261019-233339-weapons` (janela de 6 s)
  e `20261019-235051-weapons` (15 s, compilação final): `expected=1 received=1 notFired=0`,
  `RESULT: PASS` nos dois papéis; anfitrião vê o evento Fire `ProjectileWeaponSkill_GrenadeLauncher_PGL`
  do cliente e vice-versa. A janela de 15 s importa: PGL pode precisar de
  ~4 s para ficar pronto, e uma repetição de 6 s falhou (`20261019-234848-weapons`, `notFired=1`). O
  receptor ainda passa pelo caminho normal de Fire/espelho.
- `BeamWeaponSkill_Electrical_TH0R` — **concluído, mas não é um `BeamWeaponHandler`.** O recurso é um
  `LightningBeamSkillData` (subclasse de `BeamWeaponSkillData`), e seu `AddWeaponHandler` cria
  `LightningBeamHandler : WeaponHandler`, com `ActivateWeapon`, `ActivationLogic` próprios e uma
  corrotina `IEActivate`. Não tem `isBeaming` e nunca chama `StartBeaming`; o reempacotamento anterior como
  `BeamWeaponHandler` lia deslocamentos errados, por isso a execução antiga via `beaming=0`. A varredura agora
  chama `LightningBeamHandler.ActivateWeapon()`; um pós-fixo nesse método envia um `BeamState` (29)
  por rajada, e a linha remota dura 0,2 s. Execução `20261019-234302-weapons`: `RESULT: PASS` nos dois
  papéis, `beam=3/2` anfitrião e `3/3` cliente, `skills=1/1`, `notFired=0`; a primeira chamada do anfitrião informou
  `fired=1`. Controle negativo `-BeamOff` (`20261019-234645-weapons`): ambos os papéis FAIL
  `notFired=1`, `beam=0/0`, portanto a aprovação é do caminho espelhado, não do log de ativação.
- `BeamWeaponSkill_RotatingBeam_CryoCannon` — **concluído, caminho contínuo.** É um
  `BeamWeaponHandler` real (`StartBeaming`/`StopBeaming`). Varredura `20261020-012001-weapons`
  (`-DevSweep 15`): anfitrião `beam=98/91`, cliente `100/98`, `skills=1/1`, `RESULT: PASS` nos dois;
  linhas `beam: local start/send/applied` presentes. Os dois primeiros logs de varredura ainda liam
  `beaming=0`, porque o feixe começa ~3 s após equipar; a janela de 15 s cobre isso. ShardDiffractor,
  SludgePump e LocalSpaceBeam compartilham esse caminho de handler, mas não foram varridos individualmente.
  **BeamVFX do jogo - CONCLUÍDO (20261020-133051-beamgame).** `CoopBeam` resolve
  `BeamWeaponSkillData.BeamVFX` (`VFXAssetGeneric`), mantém um prefab vivo por feixe, define
  `Hovl_Laser.MaxLength` e usa o cubo de depuração como alternativa. `-Test beamgame` usa estímulo direto de
  `CoopDev` (`isBeaming=true` + `OnLocalStart`, nunca `StartBeaming`): positivo PASS nos dois,
  anfitrião `sent=56`, cliente `applied=68`, `game=1/0/0`, `noAsset=0`, `fallback=0` e
  `beam: game vfx ... prefab='CryoBeam_VFX' range=5.0`. Negativo `-BeamOff`
  (`20261020-133207-beamgame`) FAIL nos dois `sent=0 applied=0 game=0`; negativo `-GameBeamOff`
  (`20261020-133320-beamgame`) anfitrião PASS/cliente FAIL `game=0 fallback=68`. As execuções anteriores `notFired`
  usavam o nome curto de concessão `RotatingBeam_CryoCannon`; o recurso é
  `BeamWeaponSkill_RotatingBeam_CryoCannon`, portanto `CoopDev` informava `NOT_FOUND` e nunca o
  equipava. O estímulo direto é uma preparação de teste; `ActivationLogic` do próprio jogo não iniciava o
  feixe nas execuções de início automático. Caminho de recurso verificado; comprimento/alinhamento exatos não conferidos por pixels.

O teste `weapons` é por papel e exclui de `missingRecv` uma habilidade disparada por este lado (o par
a espelha; não é devolvida por eco ao remetente). PGL, TH0R e o feixe rotativo contínuo estão
aprovados; as variantes não testadas do caminho contínuo estão nomeadas acima, sem conclusão implícita.

**Erro de origem (testador: "os projéteis do cliente vêm da direção errada").** `OnLocalShot` usava
`Player.FirePoint` para todos os handlers. Handlers de Bosco/drone disparam de seu próprio
`WeaponHandler.firePoint`, portanto o espelho começava na arma do anão. Medido (`20261019-214847-hpsync`,
cliente): `from=(51.6,1,84.5) handlerFP=(51.6,1,84.5) playerFP=(53.6,1,82.4)`,
`dir=(0.2,-1,-0.1)`. A direção está no espaço do mundo e aponta para o alvo; só a origem estava errada.
`handler.firePoint` agora é preferido, com `Player.FirePoint` como alternativa.

**Sonda de HUD (`-coophudprobe`).** Nos dois lados, slot #1 é `ProjectileWeaponSkill_Subata`,
`handler=Subata`, `ownerSelf=1`, `inPlayerWeapons=1`; slots 2–4 estão vazios. O bot do cliente dispara
Bosco, uma arma de drone que não ocupa a barra de ações, portanto o slot Subata da barra está ocioso
e não mostra estado de disparo/recarga. A vinculação está correta; é diferença de estímulo/conjunto, não
um handler ausente. No jogo normal, a arma da barra é a disparada pelo jogador.

## <a id="the-partners-projectiles-were-gated-off-by-default-2026-10-19"></a>Os projéteis do parceiro ficavam desativados por padrão (2026-10-19)

Observação do teste de jogo: ambos os jogadores disparam suas armas, mas nada do parceiro é visível.
Causa: `CoopCombat.Enabled` era **false** por padrão e só era ativado por `-cooptrace`/`-Mirror`.
O pacote Fire era recebido e `Flash(e)` reproduzia a luz do disparo, mas `SpawnMirrorProjectile`
retornava imediatamente, portanto o par nunca criava um visual. Era a condição do experimento B3, não um
erro de renderização.

`Enabled` agora é verdadeiro por padrão; `-coopmirroroff` é o controle negativo. A sonda
`isVisible` por projétil permanece opcional (`CoopCombat.Probe`, definida por `-cooptrace`/`-coopb3draw`), porque esse
sinal lia falso até para os próprios projéteis do jogo - não é uma condição de jogabilidade nem prova de
invisibilidade.

Verificado numa partida cooperativa normal sem `-Mirror` (`20261019-221411-hpsync`): anfitrião espelha
`Bosco_ProjectileWeaponSkill_Base` do cliente, e o cliente espelha
`ProjectileWeaponSkill_Subata` do anfitrião, ambos como prefab real `DamageProjectile_Kinetic_Medium`, com
`applied=N dropped=0` e sem linhas `combat: probe`. `hpsync` PASS nos dois lados.

## <a id="harness-the-restore-canary-had-become-permanent-2026-10-19"></a>Ambiente de teste: a sentinela de restauração havia se tornado permanente (2026-10-19)

Toda execução desde 19:25 terminava com `saves: VERIFY FAILED - hashes match but the canary survived`.
A causa era uma restauração parcial anterior que deixara `coop-restore-canary.txt` na pasta de saves; o backup
seguinte o copiava, portanto a restauração fielmente restaurava uma árvore contendo o marcador e informava
falha para sempre. `Backup-Saves` agora remove o marcador do backup antes de registrá-lo, e o arquivo
perdido foi excluído. Os próprios dados de save foram verificados intactos (`drg_save_slot*.dat`, `localprefs.dat`);
só o marcador do ambiente estava errado.

## <a id="enemy-vat-animation-sync-2026-10-19"></a>Sincronização da animação VAT inimiga (2026-10-19)

O campo `Anim` do instantâneo agora contém o estado VAT do inimigo do anfitrião: índice de clipe + 1 nos 16 bits
superiores, fase normalizada nos 16 inferiores. O anfitrião lê
`EnemyAnimator.meshAnim.currentAnimIndex/currentAnimTime/currentAnimation.length`; o cliente
resolve o clipe `meshAnim` do espelho pelo índice (mesmo prefab/ordem), chama `meshAnim.Play(idx)` na
mudança de clipe e define `currentAnimTime = phase * length` quando a fase diverge mais de 0,2.
Reproduzir a malha diretamente evita passar por `EnemyAnimator.PlayVATClip` e seu caminho de eventos de
animação num espelho.

- A primeira tentativa usava hash de estado de `Animator` padrão e expirou (`20261019-230123`): o
  enxame anima por `Assets.Scripts.EnemyAnimator` / `ShaderMeshAnimator` (VAT), não por estado de
  `Animator`. Esse canal errado foi removido.
- PASS (`20261019-231004-enemyanim`, enxame normal): anfitrião `sent=196`; cliente `seen=42 applied=7
  sampled=21 match=21` - todo espelho amostrado mantinha o último clipe aplicado.
- Negativo (`20261019-231303-enemyanim`, `-EnemyAnimOff`): cliente FAIL por estado
  `seen=0 enemyanim=off`; anfitrião não tem `SnapAnimSent` e expira. Esse é o controle.
- Limites: só índice de clipe/fase, sem mistura/estado de parâmetros; a ordem dos índices é presumida idêntica para
  o mesmo prefab (confirmada no enxame testado); fase corrigida na taxa de 2 Hz dos instantâneos; espelhos
  não foram verificados quanto a jogabilidade por eventos de animação (testes usam invencibilidade). O próprio
  `EnemyAnimator` do espelho não sobrescreveu a malha durante o teste.

## <a id="enemy-mirror-smoothing--facing-2026-10-20"></a>Suavização + orientação de espelhos de inimigos (2026-10-20)

Observação de teste de jogo nº 3 corrigida: o cliente não teletransporta mais espelhos na taxa de 2 Hz dos instantâneos, e
a orientação do anfitrião agora chega ao espelho.

- **Transmissão:** `SnapEntry` contém um byte compactado de rotação horizontal (0..255 = 0..360 graus). A entrada tem 17 bytes;
  blocos de 56 entradas ficam abaixo da MTU (60 entradas eram rejeitadas por SteamNetworkingSockets a 1020
  bytes após acrescentar o byte de rotação). A taxa dos instantâneos continua 2 Hz — o ciclo de quadros fornece os
  quadros ausentes.
- **Posição:** `CoopEnemy.TickMirrors` executa a cada quadro no cliente e move cada espelho rumo ao
  instantâneo mais recente com `Vector3.MoveTowards`, limitado a 12 m/s e 0,5 m por quadro. Uma distância grande
  (criação, reutilização do pool, engasgo) é fechada em vários quadros, em vez de um salto.
- **Orientação:** a rotação compactada é aplicada com `Quaternion.Slerp` (mesma constante de convergência de 10 Hz);
  um espelho congelado agora gira junto com o original.
- **Positivo** (`20261020-001101-enemysmooth`, enxame normal): anfitrião `sentChunks=66 facing=846`;
  cliente `applied=731 maxStep=0.412 facingApplied=142`, `RESULT: PASS` nos dois papéis.
- **Negativo de suavização** (`20261020-000933-enemysmooth`, `-SnapSmoothOff`): cliente FAIL
  `maxStep=2.002`; o caminho antigo de salto é o controle.
- **Negativo de orientação** (`20261020-001231-enemysmooth`, `-EnemyFaceOff`): anfitrião FAIL `facing=0`,
  cliente FAIL `facingApplied=0`.
- O teste (`-Test enemysmooth`) exige que o cliente tenha se movido em muitos pequenos passos
  (`maxStep <= 0.75`) e aplicado pelo menos 10 giros do anfitrião; o anfitrião deve enviar tanto
  blocos quanto orientação. Ambos os controles negativos se baseiam em estado, não em tempos limite.
- **Repetição na compilação final** (`20261020-005713-enemysmooth`, compilação `2C4B9760140340BE`, blocos de 56 entradas):
  anfitrião `sentChunks=65 facing=953`; cliente `applied=770 maxStep=0.500 facingApplied=364`,
  `RESULT: PASS` nos dois papéis. Nenhuma linha "packet size exceeded" nesta execução.

## <a id="soak-2026-10-20-600-s-two-instances"></a>Teste prolongado de 2026-10-20 (600 s, duas instâncias)

- `20261020-040552-soak`: PASS nos dois após 600 s depois da liberação. Anfitrião 2900 inimigos vivos, cliente
  2915; 618.215 instantâneos aplicados / 3671 não encontrados; 928 eventos de projétil em cada sentido; nenhuma correspondência com
  `Exception`, `NullReference`, `0xc0000005`, padrões de tamanho de instantâneo, desconexão ou falha de criação.
  Saves restaurados e verificados (14 arquivos, sentinela removida).
- **Corrigido durante o teste prolongado:** `SpawnMirror` chamava `SpawnAt` e depois procurava o `Enemy` retornado em
  `ByPointer`; o pós-fixo de registro ainda não havia executado, portanto 29/50 espelhos eram descartados como
  `MirrorSpawnFailed`. Agora chama o idempotente `Register(e, "mirror-spawn", scale)` antes da
  busca. Depois: `fail=0 null=0 noEntry=0 noPtr=0` em `spawn=3921`. Também corrigido o
  parâmetro Harmony de `SpawnWeaponHandler.Despawn` (`ws`, não `spawn`).
- **Corrigido (2026-10-20):** `localDie=0`, `miss=0` em `20261020-043000-soak` (600 s, 624 criações,
  580 mortes de cada lado; `blocked local mirror death id=...` no log do cliente). `Enemy.Die` local do cliente
  para espelhos é bloqueado (`OnDiePrefix`), o golpe mortal ainda é informado, e
  `OnDamageEnd` limita o espelho a 1 de vida; `DeSpawn` do anfitrião o remove. O antigo
  `localDie=249`/`miss=249` desapareceu.
- As quedas `hp hurt ... nearestMirror` são esperadas: o enxame espelhado de cada instância ataca seu próprio
  anão (veja `CoopDamage`).

## <a id="xp-orb-sync-2026-10-20"></a>Sincronização de orbes de XP (2026-10-20)

Observação de teste de jogo nº 4 corrigida: ambas as instâncias agora veem os mesmos orbes de XP, e cada orbe concede uma vez.

- **Criação:** um pós-fixo em `XPManager.Spawn(Vector3, float)` envia pacote 30 com a posição
  quantizada e o modificador de força. Só o anfitrião envia; o cliente aplica dentro de
  `ApplyingRemoteXp` e registra o novo orbe como espelho.
- **Coleta:** prefixos em `XPManager.Claim(int)` e `XPManager.FinishPickup(int)` enviam pacote 31
  com a posição do orbe. Um conjunto de posições quantizadas impede o mesmo orbe local de enviar duas vezes.
- **Remoção sem XP duplo:** o receptor resolve o orbe pelo buffer estático
  `XPManager.xpPositions` (`NativeArray<float3>`, lido por reflexão porque a interoperabilidade
  não expõe o tipo de elemento), chama `Claim` + `FinishPickup` sob `ApplyingRemoteXp`, e
  o prefixo de `Player.GainXp` retorna falso para essa cópia. O `GainXp` normal do coletor é a
  única concessão e é espelhado como pacote 3.
- **Positivo** (`20261020-005304-xpsync`, enxame normal): anfitrião `spawnSent=16 claimSent=15
  finishCalls=8`; cliente `spawnRecv=16 applied=16 mirrorSeen=16 claimRecv=15 claimApplied=8
  suppressed=8`, `RESULT: PASS` nos dois papéis.
- **Negativo** (`20261020-005512-xpsync`, `-XpOff`): anfitrião `spawnSent=0`, cliente
  `spawnRecv=0`, `RESULT: FAIL` nos dois papéis. Esse é o controle.
- **Limites:** coletas são pareadas pela posição mais próxima (6 m), portanto um espelho que derivou além disso não é
  encontrado; a execução enviou 15 coletas para 8 finalizações porque `Claim` e `FinishPickup` podem disparar
  no mesmo orbe em posições ligeiramente diferentes. As 8 finalizações do anfitrião corresponderam aos 8 ganhos remotos
  do cliente, portanto não foi observado XP duplo, mas ainda é necessário um teste prolongado maior com dois jogadores para a
  condição de corrida de coleta simultânea.

## <a id="trail-ground-zones-2026-10-20"></a>Áreas de rastro no chão (2026-10-20)

Armas de rastro não são projéteis e não chamam `GroundZone.Init`; depositam áreas por
`GroundZoneDispenser.TryPlaceGroundZone`, portanto nem a interceptação de projétil nem a antiga de GroundZone.Init
as viam.

- **Estímulo:** `CoopDev` detecta `TrailWeaponSkillData`, reempacota o handler como
  `TrailWeaponHandler`, chama `ActivateWeapon()`, depois `EnableGroundZones()` se o dispensador
  estiver ausente e `BaseLogicTick(0.5f)`. Uma arma de teste recém-equipada não recebe a atualização do handler
  do próprio jogo; acioná-la é o que faz o dispensador colocar áreas.
- **Transmissão:** pós-fixo em `GroundZoneDispenser.TryPlaceGroundZone` envia pacote 32 com nome da habilidade,
  posição quantizada, raio e duração. Só habilidades de rastro são enviadas (granadas de área no chão já
  criam sua área pela explosão espelhada).
- **Cliente:** resolve o recurso de rastro pelo nome, obtém
  `TrailWeaponSkillData.GroundZoneParams.GroundZonePrefab`, instancia, chama
  `InitVisualsOnly(life, radius, null)` e posiciona. O visual expira com sua duração.
- **Positivo** (`20261020-015745-trail`): anfitrião `sent=34`; cliente `recv=38 applied=38 miss=0`,
  `RESULT: PASS` nos dois papéis.
- **Negativo** (`20261020-015907-trail`, `-ZoneOff`): anfitrião `sent=0`; cliente `applied=0`,
  `RESULT: FAIL` nos dois papéis.
- **Limites:** a área do cliente é só visual; não aplica dano/lentidão do anfitrião. A contagem
  de áreas difere (34 enviadas contra 38 aplicadas), porque o rastro do próprio cliente também gera áreas locais não
  contadas como remotas; o teste só conta o caminho remoto. O primeiro patch de `GroundZone.Init` era
  ambíguo/não disparava para nada e é mantido só como proteção sem ação; a interceptação do dispensador é o
  caminho confiável.

## <a id="remote-weapon-visual--not-applicable-no-held-model-2026-10-20"></a>Visual de arma remota — não se aplica (sem modelo empunhado) (2026-10-20)

O pacote `WeaponState` (36) e um caminho de objeto apenas visual estão implementados, mas as armas de Driller
testadas **não têm modelo empunhado** para clonar:

- O GameObject de `WeaponHandler` é o objeto compartilhado `Player/WeaponHandlers`
  (`DropPod/DropPodModel/PlayerPoint/Player/WeaponHandlers`) com **0 renderizadores**. Os únicos
  renderizadores parecidos com armas na árvore do jogador são os ossos das mãos (`mixamorigHand.L/R`, 1 cada); não há
  nó de modelo `PGL`/`Subata`.
- Clonar esse handler portanto produz 0 renderizadores; `-Test weaponvisual`
  (`20261020-025641-weaponvisual`) termina no cliente com `applied=0 renderers=0 miss=255`. O anfitrião envia a
  última habilidade equipada (PGL); o cliente encontra o handler, mas nenhum modelo.
- A troca atual de skin/mod de classe funciona (GFX remoto recebe o mod de classe do anfitrião), portanto o antigo
  "bloqueio de skin" acabou. O jogo **não tem modelo separado de arma empunhada**: `WeaponHandlers` é o
  contêiner vazio compartilhado, `WeaponSkillData` não contém prefab de modelo, e não existe tipo `WeaponSkinData` /
  `WeaponModel` na assembly. A skin do mod de classe é o visual do personagem; a
  arma é representada pelos VFX de habilidade/projétil/feixe. Um objeto empunhado não se aplica aqui.
- Não afirmar visual de objeto empunhado. O pacote é inofensivo e o caminho de objeto é protegido (nenhum objeto vazio
  fica na cena); retirar `-Test weaponvisual` da matriz. `-WeaponVisualOff`
  permanece como controle negativo.










