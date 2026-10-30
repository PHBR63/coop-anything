# <a id="transport-world-sync-and-the-test-harness"></a>Transporte, sincronização do mundo e aparato de testes

> Parte das notas de trabalho de Deep Rock Galactic: Survivor. Extraído literalmente de `NOTES.md` em 2026-10-20 (linhas 262-1194); conteúdo inalterado.
> Estado atual e Ist/Soll: [../STATUS.md](../STATUS.md). Índice: [../NOTES.md](../NOTES.md).

## <a id="test-automation-getting-both-instances-into-a-run-without-clicking"></a>Automação de testes: colocar as duas instâncias em uma partida sem clicar

Iniciar uma missão manualmente em duas janelas é o principal entrave à iteração, e o caminho de missões é
aleatório por instância, então "escolher a mesma missão duas vezes" nem sequer é confiável.

Caminhos candidatos, melhores primeiro:

- **`FixedRunManager.SetupFixedRun(FixedRunInstance, FixedRunData, EType, int)` é público**, e
  `DailyRun` / `WeeklyRun` são objetos `FixedRunInstance` construídos pelo próprio jogo. Partidas fixas usam
  *sementes*, então uma partida fixa iniciada de modo idêntico nas duas instâncias fornece configurações idênticas **e**
  geração idêntica — elimina o problema de combinar missões manualmente junto com o
  dos cliques. `TryGetSavedFixedRun(EMissionType, int, int, out FixedRunInstance)` sugere
  que partidas fixas também persistem, permitindo retomar uma partida em vez de recriá-la.
- **`RunSettingsManager.midRunSaveData`**: existe um salvamento no meio da partida, então "continuar partida" pode permitir que um teste
  retome exatamente a mesma caverna em vez de regenerá-la. Caminho de menor custo para testes repetíveis.
- **Entrada sintética** (`SendInput` via PowerShell): conduzir Play → missão → descida nas duas janelas
  de fora do jogo. Sem mecanismos internos e sem risco ao jogo, mas frágil diante de mudanças de interface
  e animações. Boa alternativa se o caminho da partida fixa resistir.
- Em aberto: a cadeia exata de chamadas de `UIFixedRunButton` / `UIPlaySelectForm` até o início real
  da partida. Essa cadeia precisa ser rastreada antes de construir uma opção `-coopauto`.

### <a id="traced-2026-10-17--chain-found-blocker-identified"></a>Rastreado (2026-10-17) — cadeia encontrada, bloqueio identificado

O assistente de seleção de missão é API pública em `DRS.UI.UIPlaySelectForm` (em `FundayFactory.UI`, classe
base `UIForm` — é necessária uma referência de compilação para ela):

```
StartMainMissionsFlow() / StartFixedRunFlow() / StartEndlessFlow() / StartMasteryFlow()
PageFlowNext()                       <- the wizard's Next button
OnMissionNodeClick(MissionNodeState) / OnMissionSectorClick(...) / OnMainMissionSelect(EMainType)
OnBiomeNext(BiomeLevelData) / OnHazLevelNext(int) / OnClassPageNext(EDwarf)
TrySetPage(EPage) / BuildPageFlow() / SetupPageFlow(List<EPage>)
```

Uma opção `-coopauto` foi implementada com base nisso (ver `CoopAuto.cs` no plugin) e executada nas duas
instâncias. Resultado:

- O formulário **é** encontrado, mas chamar `StartFixedRunFlow()` nele lança `NullReferenceException`,
  e em uma instância `PageFlowNext()` não fez absolutamente nada. Ambos são sinais de um
  formulário **inativo, ainda não inicializado**: `FindObjectsOfType(true)` o retorna enquanto o menu ainda
  está na abertura/menu principal, e seus campos injetados não são conectados até o menu Play abrir.
- Portanto, a peça que falta é **entrar no menu Play**, não o assistente em si. Os acessos corretos
  são `UISceneMenu.PlaySelectForm` (getter público) e `UIMenuSplashForm`; `UIManager` também
  expõe `PlaySelectForm`. `UISceneMenu` não tem método óbvio "Play pressionado" — os botões são
  conectados como callbacks da cena — então o ponto de entrada provavelmente está no formulário de abertura.

Dois caminhos: chamar o tratador Play da abertura/menu pelo mod, ou aceitar **um clique sintético**
para pressionar Play e deixar o mod conduzir o assistente dali em diante (sabe-se que as chamadas do assistente existem e
a semente da partida fixa deriva da data, então ambas as instâncias chegariam à mesma partida).

**Segunda tentativa, com o elo ausente encontrado — também falhou.** `UIMenuSplashForm.OnPlayButton()` é
público e é o botão Play real, então a cadeia é Play -> assistente. Conduzi-la pelo mod resulta em:

```
auto: find UIMenuSplashForm -> 1 found, first active=False
auto: step 1 - OnPlayButton()          -> NullReferenceException
auto: find UIPlaySelectForm  -> 1 found, first active=True
auto: step 2 - StartFixedRunFlow()     -> NullReferenceException
auto: step 3 - PageFlowNext()          -> NullReferenceException   (repeats)
```

Conclusões a conservar:

- `FindObjectsOfType(true)` retorna **cópias de formulários pré-instanciadas e inativas** cujos campos injetados
  são nulos; chamar métodos nelas lança exceções imediatamente. Sempre preferir uma instância
  `activeInHierarchy` (o localizador em `CoopAuto.cs` agora faz isso).
- Escolher um `UIPlaySelectForm` *ativo* ainda lança exceções em seus próprios métodos públicos, então o assistente
  depende de estado interno estabelecido apenas pelo caminho real dos botões do jogo. **Chamar os objetos
  de interface diretamente não é um caminho viável de automação.**
- As opções restantes são **entrada sintética** (enviar um clique real em Play, depois conduzir o assistente
  com entradas reais como faria um jogador), ou interceptar algo que o jogo já faz
  automaticamente. Entrada sintética é a escolha pragmática; a estrutura de `-coopauto` no plugin é
  reutilizável quando a entrada funcionar.

### <a id="third-attempt-state-driven--real-button-invocation-2026-10-17"></a>Terceira tentativa: orientada por estado + acionamento do botão real (2026-10-17)

Esta funciona até a página de tipo de partida. Descobertas, na ordem de importância:

1. **A tela de abertura inicial precisa de um clique real do mouse.** Por mais de 150 segundos, o único formulário ativo foi
   `UISplashForm` (logo da distribuidora), enquanto `UILoadingForm` / `UIMenuSplashForm` ficaram inativos, embora
   o jogo renderizasse normalmente (seu contador de ticks continuava avançando). Espaço/Enter por `SendKeys` não fez
   **nada**; um clique real (`SetCursorPos` + `mouse_event` LEFTDOWN/LEFTUP) no centro da janela
   avançou imediatamente. Portanto, o inicializador deve clicar uma vez na janela após iniciar.
2. **Não conduzir por temporização — conduzir pelo estado de interface observado.** Uma versão anterior disparava cada etapa
   enquanto o jogo ainda estava no logo. A atual lê qual `UIForm` está ativo e
   reage; eliminou toda uma classe de falhas silenciosas.
3. **`UIMenuSplashForm.playButton.onClick.Invoke()` funciona** para sair do menu principal. É o
   equivalente, dentro do processo, a um clique real e foi o que chegou ao assistente.
4. **Página 1 do assistente não tem botão Next — oferece tipos de partida.** Nomes reais de botões encontrados:
   `UIMissionRoadButton_Elim/_Escort/_EggHunt`, `UIFixedRunButton_Daily/_Weekly`,
   `UISetProgressButton_Mastery/_Endless/_Anomaly`, `UIChallengeSetButton_MissionRoad`,
   `UIMasterySetButton_Weapons/_ClassMods/_Biomes`, `UIBackButton`, `UIMutatorSetEntry` e
   abas `UIPlayCrumb`.
5. **As partidas fixas diárias e semanais estão BLOQUEADAS neste perfil** — registrado como
   `UIFixedRunButton_Daily[locked] UIFixedRunButton_Weekly[locked]`. Pressionar um botão bloqueado não faz
   nada, o que fez uma tentativa anterior repetir para sempre sem mudança de estado. Portanto, a partida diária
   com semente de data **não** está disponível atualmente como veículo de teste aqui.
6. `UIMissionRoadButton_Elim` existe, mas fica **inativo** enquanto a página de partidas fixas/desafios está
   à mostra, então um seletor que exige `activeInHierarchy` acaba escolhendo o botão diário bloqueado.
   Navegar à página do caminho de missões passa pelos botões de trilha/abas (`UIPlayCrumb`,
   `UIChallengeSetButton_MissionRoad`).

**Próximo passo da automação:** acionar a aba/trilha do caminho de missões para trocar de página, depois pressionar o
botão Elimination do caminho de missões e continuar pelo assistente. Tudo de que se precisa agora está mapeado;
é iteração, não descoberta. O script inicializador também deve clicar uma vez na janela para remover a
abertura.

### <a id="fourth-attempt-found-the-real-button-class-2026-10-17"></a>Quarta tentativa: encontrada a classe real do botão (2026-10-17)

Duas descobertas que importam mais que tudo acima:

1. **Os botões do jogo são `DRS.UI.UIButton`, não `UnityEngine.UI.Button`.** `UIMenuSplashForm.playButton`
   tem tipo `UIButton`, e `UIButton` expõe seu próprio **UnityEvent `OnClick`** público, além de
   `Interactable`, `IsAvailable`, `IsSelected`, `OnPointerDown/Up/Enter/Exit`, `OnSelect/OnDeselect`
   e `OnButtonClick()` virtual protegido. Acionar o `UnityEngine.UI.Button.onClick` *interno*
   (o que as primeiras tentativas faziam) executa um evento que o jogo não escuta; por isso pressionar
   botões parecia não fazer nada. Também contém `_ClickCoroutine`/`_HoldCoroutine`, então trata
   seus próprios eventos de ponteiro em vez de delegar a um Button simples.
2. **`IsAvailable` expõe o estado de desbloqueio por perfil**, e registrá-lo esclarece a página de tipo de partida:
   ```
   UIBackButton UIChallengeSetButton_MissionRoad UISetProgressButton_Mastery[unavailable]
   UISetProgressButton_Endless[unavailable] UISetProgressButton_Anomaly[unavailable]
   UIFixedRunButton_Daily[unavailable] UIFixedRunButton_Weekly[unavailable] UIPlayCrumb
   ```
   Neste perfil, **só o caminho de missões da campanha está desbloqueado** — Mastery, Endless, Anomaly e
   ambas as partidas fixas estão `[unavailable]`. Portanto, a partida diária com semente de data está mesmo descartada, e
   o caminho da campanha é a única rota automatizável.

Bloqueio atual: pressionar `UIChallengeSetButton_MissionRoad` por `UIButton.OnClick` ainda não
muda a página. Candidatos restantes, melhores primeiro:

- **Calcular a posição do botão na tela por seu `RectTransform` e clicar nele com um evento real
  do mouse.** É a opção mais fiel, sem pressupor qual evento o jogo
  escuta, e já sabemos enviar cliques reais (é o que remove a abertura). O mod
  pode registrar as coordenadas; o inicializador clica nelas.
- Tentar novamente `UIPlaySelectForm.StartMainMissionsFlow()` / `PageFlowNext()` agora que se sabe que o formulário está
  ativo; a `NullReferenceException` anterior era lançada enquanto o formulário ainda estava dormente, então esse
  resultado não é conclusivo.
- Conduzir `OnPointerDown` + `OnPointerUp` com um `PointerEventData`, pois `UIButton` implementa seu
  próprio tratamento de ponteiro.

Também vale registrar para quem retomar: clicar no centro da janela para remover a abertura pode atingir
conteúdo do menu, então esse clique pode fazer parte da navegação. Um clique em ponto reconhecidamente
seguro (ou em posição calculada de botão) tornaria o experimento limpo.

### <a id="two-instance-launcher-two-traps-that-cost-a-debugging-cycle-2026-10-17-after-a-pc-move"></a>Inicializador de duas instâncias: duas armadilhas que custaram um ciclo de depuração (2026-10-17, após mudança de PC)

Executar o par à mão é a razão de existir do inicializador; deu errado duas vezes de formas que valem
registrar, pois ambas parecem exatamente um jogo parado.

1. **Nunca clicar na janela de console do BepInEx.** Com o console do BepInEx ativado
   (`[Logging.Console] Enabled = true`, o padrão), cada instância abre uma janela `ConsoleWindowClass`
   intitulada `BepInEx <version> - DRG Survivor` ao lado da janela `UnityWndClass` do jogo.
   Clicar nela com QuickEdit ativado coloca-a no modo de marcação/seleção, que **bloqueia a próxima gravação
   do processo no console e congela o jogo**: ~180 MB de conjunto de trabalho, ~1 segundo de CPU, nenhuma nova linha
   de log, `Player.log` criado mas vazio. É travamento, não falha — sem entrada no log de eventos, sem
   despejo, e o processo acaba simplesmente encerrando. Corrigir dos dois lados: definir
   `[Logging.Console] Enabled = false` na instalação de teste (o log em disco e o
   `coop-<role>.log` do mod bastam para testes) e escolher a janela do clique **pelo nome de classe** —
   `UnityWndClass` — nunca `Process.MainWindowHandle`, que pode apontar para o console.
2. **`LogOutput.log` apenas recebe acréscimos entre execuções e é compartilhado pelas duas instâncias.** Linhas de uma execução antiga
   parecem atuais, e uma linha antiga `coop: coop loaded, role=..., gameRoot=...` de sessão anterior
   pode ser confundida com a desta sessão. Duas verificações resolvem: horário da última gravação do arquivo e
   `gameRoot` nessa linha (execução de checkout diferente imprime outro caminho). O log próprio
   do mod, `coop-<role>.log`, é por função e o único confiável para resultado de duas instâncias —
   mas BepInEx só o grava quando o plugin está ativo, então sua ausência já é um sinal.

**Verificado após a mudança** (build 23854500): anfitrião `net: host listening on udp 9050`, cliente
`net: peer connected id=0`, contadores bidirecionais subindo dos dois lados (`sent=307 recv=232` anfitrião /
`sent=239 recv=312` cliente a ~20 Hz), `bot=on` em ambos. Uma instância sozinha não é afetada —
chega a ~1,3 GB e taxa normal de ticks, o que permitiu distinguir as duas armadilhas acima de uma
build realmente quebrada.

Ainda vale das sessões anteriores: a partida deve ser iniciada manualmente (assistente não automatizado),
então dois clientes ainda não chegam a uma *partida* sem supervisão — isso só prova o transporte e o caminho
do plugin na nova máquina.

### <a id="fifth-the-real-wizard-sequence-captured-by-a-human-click-through-2026-10-17"></a>Quinta: sequência real do assistente, capturada por cliques humanos (2026-10-17)

`-coopwatch` foi criado exatamente para isso: registra o formulário ativo, os botões ativos do assistente e
seu estado `UIButton.IsAvailable`, e não pressiona **nada**. Uma instância foi iniciada com ele e uma
pessoa clicou até entrar em uma partida. Sequência inteira, em ordem:

```
UISplashForm                                  <- publisher logo; ignores keys, needs a real click
UIMenuSplashForm                              <- main menu; Play
UIPlaySelectForm   UIBackButton UIMissionRoadButton_Elim UIMissionRoadButton_Escort UIPlayCrumb
UIPlaySelectForm   UIBackButton MissionSectorButton_1..5 MissionGateButton_1..3
                                (sector 4,5 and gate 4 report [unavailable]) UIPlayCrumb, UIPlayCrumb (1)
UIPlaySelectForm   UIBackButton ClassSelectButton_Scout/_Gunner/_Engineer/_Driller UIPlayCrumb (1..3)
UIPlaySelectForm   UIBackButton HazLevelButton, HazLevelButton (1), HazLevelButton (2) UIPlayCrumb (1..5)
UILoadingForm
GameController.OnCoreRunStarted player=True
map: rocks=5/81 fingerprint=000000000000000000000000000000000000000000000000000000000001001000000010000000011
map: settings biome=BiomeLevelData mission=Campaign mainMission=Elimination hazard=0
```

O que isso esclarece e o que muda:

- **Não há botão Next em lugar algum do assistente.** Ele avança por *seleção de conteúdo*, nesta
  ordem: tipo de missão → setor/portão → classe do anão → perigo → carregamento. Portanto, a alternativa
  `next / start / confirm / continue / drop` de `DriveWizard()` é inalcançável e deve ser removida, não deixada
  ali como suposição.
- **A página de setor/portão precisa de duas seleções.** Um setor *e* um portão estão ativos na mesma
  captura, então o antigo ciclo "pressionar o primeiro botão sensato em cada etapa" pressionaria o mesmo setor
  repetidamente. O condutor precisa de um plano ordenado com índice de progresso.
- **Nomes dos botões acumulam sufixos de clone do Unity.** `UIPlayCrumb`, `UIPlayCrumb (1)`,
  `UIPlayCrumb (2)` … então correspondência exata de nomes perde duplicados silenciosamente. Comparar pelo nome-base com
  qualquer `" (n)"` final removido.
- **Escolhas determinísticas fazem as duas instâncias se encontrarem.** Ambas compartilham o perfil real, então
  "menor índice disponível", mesma classe e mesmo perigo as colocam na mesma partida — o que
  o trabalho de caverna compartilhada precisa. (`hazard=0` era simplesmente o primeiro botão de perigo.)
- **Uma asserção pronta.** `map: seeds Random=… ` junto de
  `map: rocks=N/81 fingerprint=<81 bits>` e `map: settings biome/mission/mainMission/hazard` é
  exatamente o que um teste com duas instâncias deve comparar, sem precisar de infraestrutura nova.
- **Ainda uma suposição:** se o setor ou o portão deve ser clicado *primeiro* nessa página. Ambos estão
  visíveis juntos e as capturas de 2 s não mostram qual a pessoa clicou antes. O condutor presume
  setor antes do portão e registra cada acionamento; a próxima execução sem supervisão mostrará se a ordem está errada.

### <a id="first-unattended-attempt-the-run-type-tab-needs-a-real-pointer-click-2026-10-17"></a>Primeira tentativa sem supervisão: a aba de tipo de partida precisa de clique real de ponteiro (2026-10-17)

Com o condutor implementado, uma execução `-coopauto` de duas instâncias avança bastante e para exatamente na
barreira da quarta tentativa — desta vez com evidência utilizável:

- **Remover a abertura, pressionar Play e chegar ao assistente funciona.** Play é
  `pressing playButton 'Button_Cut_Play'`, depois do que o assistente aparece. Portanto, `UIButton.OnClick.Invoke()`
  funciona para pelo menos esse botão.
- **A página *inicial* do assistente é a lista de tipos de partida, não a lista de missões.** A captura humana começa
  em `UIMissionRoadButton_Elim / _Escort` porque a pessoa já tinha passado dessa página. A página
  inicial é: `UIBackButton UIChallengeSetButton_MissionRoad UISetProgressButton_Mastery[unavailable]
  UISetProgressButton_Endless[unavailable] UISetProgressButton_Anomaly[unavailable]
  UIFixedRunButton_Daily[unavailable] UIFixedRunButton_Weekly[unavailable] UIPlayCrumb`.
- **Pressionar `UIChallengeSetButton_MissionRoad` por `OnClick` não muda a página.** O log
  mostra o acionamento repetidamente (pela alternativa registrada do condutor) sem a página nunca
  mudar — resultado da quarta tentativa, reproduzido com o mecanismo agora conhecido por funcionar para Play.
  Portanto, `OnClick` basta para alguns botões, mas não para essa aba.
- O condutor consumiu a aba como `plan[0]` e então parou em `plan[1]` (`UIMissionRoadButton_`),
  porque a página esperada nunca apareceu. Alimentá-lo com um acionamento alternativo não ajudou; a página precisa
  mudar de verdade.

Próximo passo, na ordem indicada pelas evidências:

1. **Clique real de ponteiro no botão.** Tanto a abertura quanto Play se comportam corretamente quando conduzidos por eventos
   de mouse do SO, e a quarta tentativa já colocou "calcular a posição do botão na tela por seu
   `RectTransform` e clicar com evento real do mouse" em primeiro lugar. O mod pode registrar o retângulo; o inicializador
   clica nele. É a opção mais fiel e não pressupõe qual evento o jogo usa.
2. `OnPointerDown` + `OnPointerUp` com um `PointerEventData`, já que `UIButton` implementa seu próprio
   tratamento de ponteiro e contém `_ClickCoroutine` / `_HoldCoroutine`.
3. Um clique real na *trilha* (`UIPlayCrumb`), em vez do botão de conjunto, pois a trilha pode ser o
   controle que realmente troca a página.

### <a id="solved-the-wizard-is-driven-by-handler-methods-not-by-button-clicks-2026-10-17"></a>Resolvido: o assistente é conduzido por métodos tratadores, não por cliques de botões (2026-10-17)

Uma segunda execução sem supervisão esclareceu. Dois acionamentos foram emitidos por `UIButton.OnClick`, e o log
mostra claramente que nenhum mudou a página, enquanto uma chamada de *método* mudou:

```
18:04:36  pressing plan[0] UIChallengeSetButton_MissionRoad   (OnClick)  -> page did NOT change
18:04:38  nudge - calling StartMainMissionsFlow()                        -> page DID change
18:04:40  pressing plan[1] UIMissionRoadButton_Elim           (OnClick)  -> page did NOT change
```

- **`UIPlaySelectForm.StartMainMissionsFlow()` funciona** quando o formulário já está ativo. É a transição que a
  quarta tentativa não conseguiu fazer: chamou `StartFixedRunFlow()` em formulário *dormente*, recebeu
  `NullReferenceException` e concluiu que o assistente não podia ser conduzido. Pode — o formulário só precisa
  ter sido aberto antes por Play.
- **`OnClick` é inerte nos botões de seleção do assistente.** Funciona para `playButton`, mas não
  para `UIChallengeSetButton_MissionRoad` ou `UIMissionRoadButton_Elim`. Portanto, a conclusão anterior
  "`UIButton.OnClick` é a única coisa que funciona nestas telas" está errada — certa para o menu
  principal, errada para o assistente.
- **Os tratadores reais são métodos públicos de `UIPlaySelectForm`** (`DRS.UI`), cada um recebendo o que
  selecionar em vez de depender de um evento de botão:

  ```
  StartMainMissionsFlow()                          <- run type;  PROVEN to advance the page
  OnMainMissionSelect(EMainMissionType)            <- mission within the road (Elimination/Escort)
  OnMissionSectorClick(MissionSectorState)
  OnMissionNodeClick(MissionNodeState)
  OnBiomeNext(BiomeLevelData)
  OnHazLevelNext(int hazLevel)
  OnClassPageNext(EDwarf)
  PageFlowNext()
  ```

  Os três que recebem objetos (`MissionSectorState`, `MissionNodeState`, `BiomeLevelData`) precisam do estado
  ativo obtido da página em vez de construído; os de enum/int (`EMainMissionType`, `EDwarf`,
  `hazard`) não. **Esse é o formato da correção**: chamar esses tratadores na ordem do assistente.

- **A alternativa de coordenadas de clique ainda não funciona.** O ponto registrado para a aba era
  `clientx=-11 clienty=720 screensize=1280x720` — negativo e exatamente na altura da tela, ou seja, sem sentido;
  tratar a posição global de um retângulo sobreposto como pixels do cliente está errado aqui (grupo de layout, modo de
  renderização do canvas ou retângulo que não é o elemento visual). Não usar esse caminho até as coordenadas estarem
  corretas; de todo modo, a rota dos tratadores acima é melhor.

Também vale registrar: `UIMissionRoadButton_Escort` estava `[available]` na captura humana, mas
`[unavailable]` nesta execução, e `MissionSectorButton_4/5` estavam indisponíveis em ambas. Portanto, a disponibilidade
do caminho de missões depende do estado, e um condutor deve escolher uma opção *disponível*, não uma
fixa.

### <a id="cpp2il-dummy-assemblies-what-they-do-and-do-not-give-you-2026-10-17"></a>Assemblies fictícios do Cpp2IL: o que fornecem e o que não fornecem (2026-10-17)

Para ler o que um método do jogo realmente *faz*, os assemblies de interop são inúteis — são stubs de chamada
apenas com assinaturas. O próximo nível são os assemblies fictícios do Cpp2IL, que o BepInEx pode manter:

```
; BepInEx/config/BepInEx.cfg
[IL2CPP] DumpDummyAssemblies = true
```

Depois guardar `BepInEx/interop` (renomear, não excluir — se a regeneração falhar, será bom recuperá-lo) e
reiniciar uma vez: Cpp2IL roda novamente e os fictícios ficam em `BepInEx/dummy/`. Nesta build produziu
**129 arquivos**, incluindo `Assembly-CSharp.dll` (3,0 MB) e `FundayFactory.UI.dll` (75 KB). Interop
regenerou corretamente junto deles (132 arquivos), e o carregador em cadeia ainda concluiu, então é seguro
fazer na cópia de teste. Descompilar um único tipo em vez do assembly inteiro:
`ilspycmd -t DRS.UI.UIPlaySelectForm BepInEx/dummy/Assembly-CSharp.dll`.

**Mas os corpos estão vazios.** Os fictícios são melhores que interop, não uma descompilação: Cpp2IL não conseguiu
recuperar o IL, então cada corpo de método é `{ }` (`StartMainMissionsFlow() { }`,
`BuildPageFlow() { return null; }`). O que *fornecem*, com precisão, é:

- **assinaturas**, incluindo os tipos dos argumentos que realmente importam aqui;
- **enums com seus membros**, de onde vem a ordem do assistente abaixo;
- **deslocamentos de campos** (`[FieldOffset(Offset = "0x18")]`) e **tipos aninhados**;
- **endereço nativo de cada método** (`[Address(RVA = "0x9764A0", Offset = "0x9758F0", Length = "0x7A")]`),
  ponto de entrada para trabalho real sobre corpos no Ghidra/IDA contra o binário do jogo (`GameAssembly.dll`).

**Os corpos acabaram não sendo necessários para esta tarefa.** `StartMainMissionsFlow()` comprovadamente mudou
a página do assistente enquanto seu corpo fictício está vazio — portanto são métodos gerenciados comuns, chamáveis
pelo nome, e o jogo faz o trabalho nativamente. Conhecer as *assinaturas* era todo o
requisito; essa é a lição a guardar.

Armadilha prática: redirecionar saída de `ilspycmd` pelo PowerShell grava **UTF-16**, lido como
`u s i n g   S y s t e m ;` em qualquer outra ferramenta. Encaminhar por `Out-File -Encoding utf8`.

### <a id="the-wizards-page-order-from-the-games-own-enum"></a>Ordem das páginas do assistente, pelo enum do próprio jogo

`DRS.UI.UIPlaySelectForm` declara um `EPage` aninhado, a sequência de referência:

```
MISSION_TYPE, MAIN_MISSION_TYPE, MASTERY_TYPE, ANOMALY_TYPE,
MISSION_SECTOR, MISSION_NODE, CHALLENGE, BIOME, HAZ, CLASS, CLASS_ARTIFACT
```

Portanto, a ordem das páginas do caminho de missões é **tipo de partida → tipo de missão principal → setor → nó → desafio → bioma →
perigo → classe**, e os tratadores `On*` correspondem um a um:

```
StartMainMissionsFlow()          -> enters the campaign flow (MISSION_TYPE);  PROVEN to work
OnMainMissionSelect(EMainMissionType)   -> MAIN_MISSION_TYPE (Elimination / Escort)
OnMissionSectorClick(MissionSectorState) -> MISSION_SECTOR
OnMissionNodeClick(MissionNodeState)     -> MISSION_NODE   (the "MissionGateButton" page)
OnChallengeSetNext(ChallengeDataSet) / OnChallengeNext(ChallengeData)
OnBiomeNext(BiomeLevelData)              -> BIOME
OnHazLevelNext(int hazLevel)             -> HAZ
OnClassPageNext(EDwarf)                  -> CLASS
```

Isso corrige a ordem do plano suposta antes (setor, depois portão, sem etapa de desafio/bioma),
e significa que o condutor deve seguir `EPage`, não o layout dos botões. Todos esses tipos estão no
`Assembly-CSharp.dll` fictício (`MissionSectorState`, `MissionNodeState`, `BiomeLevelData`, `EDwarf`,
`EMainMissionType`), então o trabalho restante é obter os objetos de estado ativos para os dois que recebem
um, não descobrir a API.

### <a id="automated-the-wizard-is-now-driven-with-no-human-input-2026-10-17"></a>Automatizado: assistente agora conduzido sem entrada humana (2026-10-17)

Verificado em execução `-coopauto` de duas instâncias. Ambas percorreram todo o assistente sem supervisão e
chegaram à **mesma caverna**, com impressões digitais idênticas do mapa e sem cliques de ninguém:

```
plan[1] UIMissionRoadButton_Elim  -> plan[2] MissionSectorButton_1 -> MissionNodeButton_01
     -> UISelectable_Hex_ClassArtifact -> ClassSelectButton_Scout -> HazLevelButton
auto: IN RUN after 18 steps - automation done          (both instances)
map: rocks=3/81 fingerprint=000000000000000000000000000000000000000000000000001000000000000000000010000000001
map: settings biome=BiomeLevelData mission=Campaign mainMission=Elimination hazard=0
```

Duas descobertas que fizeram funcionar, ambas contraintuitivas:

1. **O caminho de clique é `UIButton.OnButtonClick()`, não `OnClick`.** É um `protected virtual`
   sobrescrito por cada botão do assistente — `UIMissionSectorButton.OnButtonClick()` chama
   `OnMissionSectorClick` do formulário com *seu próprio* `sectorState`, então não é preciso buscar o estado. O
   UnityEvent público `OnClick` é outra coisa e simplesmente não está conectado nesses botões: acioná-lo
   não muda nada. Detalhe útil do assembly fictício: `MissionSectorState` contém
   `List<MissionNodeState> Nodes` e `MissionNodeState GateState`, então o "portão" em si é um nó.
2. **`StartMainMissionsFlow()` deve ser chamado no máximo uma vez.** Chamá-lo novamente após passar da
   primeira página reinicia o fluxo do topo; um condutor que o dispara a cada mudança de página
   percorre o plano e depois é arrastado de volta à primeira página toda vez, exatamente o que o log
   mostrava antes da correção.

### <a id="three-launcherdriver-bugs-worth-not-repeating-2026-10-17"></a>Três erros do inicializador/condutor que não vale repetir (2026-10-17)

Os três produziram sintomas que pareciam mau comportamento do *jogo*:

- **`OnClick` versus `OnButtonClick`** (acima). `OnClick` funciona em `playButton` e não faz nada no
  assistente, então "pressionar o botão não fez nada" na realidade era "o evento errado foi acionado".
- **Um empurrão disparado com frequência excessiva** (acima). `StartMainMissionsFlow()` repetido reinicia
  silenciosamente o progresso do assistente.
- **Detecção da abertura baseada na ausência de evidência.** `coop-click.ps1` decidia que tinha passado da
  abertura se a última linha `auto:` *não* era de abertura. Mas o plugin registra
  `auto: armed, watching UI state` antes de olhar qualquer formulário, então o ciclo declarava sucesso
  imediatamente, não enviava clique algum e ambas as instâncias ficavam no logo da distribuidora por 61 etapas. Agora
  exige evidência **positiva** (`UIMenuSplashForm`, `pressing playButton`, `wizard page`, `IN RUN`).
  Regra a guardar: um ciclo de espera deve parar pela prova de sucesso, nunca pela falta de prova de falha.

Efeito colateral útil da correção: `-coopauto` agora elimina os cliques manuais exigidos em todos os marcos
anteriores, então a sincronização do estado do mundo pode ser medida em uma partida que inicia sozinha.

Nota sobre o perfil: nesta execução, só o setor 1, só `Scout` e só `UIMissionRoadButton_Elim` estavam
disponíveis; todo o resto indicava `[unavailable]`. Escolher "primeiro disponível" é, portanto, a estratégia
certa, e como ambas compartilham o perfil, escolhem a mesma coisa e se encontram em uma partida.

### <a id="steam-must-be-running-or-the-game-boots-to-nothing-2026-10-17"></a>Steam precisa estar em execução, ou o jogo inicia sem nada (2026-10-17)

Custou uma hora, então vem primeiro. Com Steam fechado, a cópia de teste ainda inicia: BepInEx carrega, o
plugin carrega, cada patch Harmony se instala corretamente e o log parece saudável. Mas o jogo então fica
**sem formulário de interface algum** — `auto: step 202 - no active form, waiting` por quatro minutos seguidos —
e nunca chega à abertura ou ao menu. `coop-click.ps1` clica 45 vezes no vazio.

O enganoso é que nada relata erro: sem exceção no log do BepInEx, sem falha, o
processo fica vivo e o único sintoma é a automação dizer "no active form". Se uma execução
parar assim novamente, **conferir se Steam está em execução antes de suspeitar do mod**.

### <a id="enemy-identity-measured-the-hooks-are-not-complete-yet-2026-10-17"></a>Identidade de inimigos, medida: hooks ainda incompletos (2026-10-17)

Etapa 1, passo 1 (atribuir IDs e comparar com a lista do próprio gerador) foi criada para responder exatamente uma
pergunta antes de qualquer envio pela rede: os hooks veem todos os inimigos? Não.

```
host:   reg=51  vs live enemies=61  | spawnAt=10  onSpawn=80  dup=10  noptr=0  die=19  despawn=0  recall=0
client: reg=44  vs live enemies=54  | spawnAt=10  onSpawn=72  dup=10  noptr=0  die=18  despawn=0  recall=0
```

O que os números já dizem (registros em partida real, duas instâncias, sem cliques):

- **`EnemySpawner.SpawnAt` encadeia até `Enemy.OnSpawn`.** Cada uma das 10 chamadas `SpawnAt` chegou
  a um inimigo já registrado (`dup=10`), então `OnSpawn` é o hook que realmente dispara por inimigo;
  `SpawnAt` é a entrada no lado chamador. Aplicar patch em ambos só se o lado chamador for necessário para supressão.
- **`reg` está abaixo da contagem de ativos**, por 10 dos dois lados, então alguns inimigos chegam à lista do gerador
  sem passar por `OnSpawn`, ou um inimigo do pool é reutilizado após ser removido do registro (o ponteiro
  é o mesmo para objeto reutilizado do pool — `ByPointer` usa o ponteiro nativo como chave). Identificar qual
  caso antes de atribuir IDs de rede: um ID que o par nunca conhece causa dessincronização silenciosa.
- **Morte passa por `Die`, não por `DeSpawn`/`Recall`** (`die=19`, os outros dois 0). `Enemy.Die` é,
  portanto, o único caminho de remoção do registro que vale conectar agora.

**Resolvido, e a lacuna é menor do que parecia inicialmente (2026-10-17).** Em vez de seguir caçando o
único hook ausente, o registro agora é completado pela lista do próprio gerador: a cada tick, qualquer inimigo em
`EnemySpawner.Enemies` sem ID recebe um, e um contador registra quantas vezes foi necessário. A
lista mantida pelo jogo passa a ser a autoridade, então a completude já não depende de encontrar cada
hook. Verificado em partida de cinco minutos, ambas as instâncias:

```
host:   enemies=502  reg=502  peak=505  |  onSpawn=1165  dup=10  die=598  despawn=65  rec=10/1
client: enemies=547  reg=547  peak=547  |  onSpawn=1169  dup=10  die=582  despawn=40  rec=10/1
```

`reg` é exatamente igual à contagem de ativos nos dois lados, então já não pode ir pela rede um ID de inimigo que
o par nunca conhece.

`rec=10/1` é o número mais interessante. A varredura precisou agir **uma vez**, recolhendo dez inimigos, e
nunca mais ao longo de 1165 criações e 598 mortes. A suposição acima — reutilização contínua do pool — está,
portanto, **errada**: os dez são uma população única de início de partida que os hooks nunca veem (um pool
pré-aquecido se encaixa, mas não está comprovado). Não vale perseguir mais enquanto a varredura fecha a lacuna, e o
contador denunciará se o comportamento mudar.

**Correção:** o item acima diz que morte só passa por `Die`. Valeu na execução curta em que foi
medido, mas em execução mais longa `DeSpawn` também dispara (`despawn=65` contra `die=598`). Ambos estão conectados,
então nada se perde — mas "somente `Die`" foi uma afirmação forte demais para uma execução curta demais.

### <a id="suppressing-spawnat-does-not-silence-a-client-the-wave-path-bypasses-it-2026-10-17"></a>Suprimir `SpawnAt` não silencia um cliente: o caminho das ondas o contorna (2026-10-17)

A primeira tentativa de impedir o cliente de executar suas próprias ondas foi um prefixo em `EnemySpawner.SpawnAt`
retornando false no cliente. Resultado medido — captura apenas uma fração:
```
host:   enemies=367  reg=367  |  spawnAt=10  onSpawn=943  sup=0   rec=10/1
client: enemies=193  reg=193  |  spawnAt=8   onSpawn=804  sup=8   rec=0/0   noptr=8
```

`sup=8` mostra que a recusa funciona, e `noptr=8` é seu efeito colateral inofensivo (o postfix roda depois com
resultado nulo e conta um ponteiro ausente). Mas o cliente ainda terminou com **193 inimigos**, todos
informados por `OnSpawn`: **943 / 804 chamadas `OnSpawn` contra 10 / 8 chamadas `SpawnAt`.**

Portanto, o mecanismo de ondas não passa por `SpawnAt`. `EnemySpawner.Spawn(SpawnData, ...)` e
`Spawn(Enemy prefab, int count, ...)` são entradas separadas, e a afirmação repetida neste arquivo e
no plano — "`SpawnAt` é o único ponto de passagem de criação" — está **errada**.

Consequência: a supressão deve cobrir toda entrada do gerador, ou mover-se para `OnSpawn`, o único
hook que dispara para cada inimigo. A mesma correção se aplica ao plano, em que a mensagem de criação
de rede seria orientada por `SpawnAt` pelo mesmo motivo.

### <a id="client-spawner-silenced---all-four-entry-points-verified-2026-10-17"></a>Gerador do cliente silenciado — as quatro entradas, verificadas (2026-10-17)

A recusa agora cobre toda entrada do gerador, e as assinaturas abaixo não são suposições: Harmony registra
onde aplicou patch, então isto é o que o jogo realmente tem.

```
EnemySpawner.SpawnAt(Enemy, Vector3, EnemySpawner.EEnemyScaleMode)
EnemySpawner.SpawnAt(EEnemy, Vector3, EnemySpawner.EEnemyScaleMode)
EnemySpawner.Spawn(SpawnData, EnemySpawner.EEnemyScaleMode)                     <- bypassed SpawnAt
EnemySpawner.Spawn(Enemy, Int32, Boolean, EnemySpawner.EEnemyScaleMode, Int32)
```

Medido no cliente, partida inteira: `enemies=0 peak=0`, enquanto o anfitrião executava 296-315 próprios. O cliente
continuou saudável — a posição local avançava entre amostras (`(2.6,0.0,-11.7)` -> `(11.9,0.0,-1.4)`)
— e houve **zero exceções** em qualquer dos logs do BepInEx.

Esse último ponto era a verdadeira questão: `Spawn(SpawnData, ...)`, que retorna lista, agora é inteiramente pulado,
então retorna null, e seus chamadores não o desreferenciam. O jogo tolera um cliente cujo mecanismo de ondas
não produz absolutamente nada, resultado mais forte do que o esperado — sem `SuppressSpawnCount`, sem
`RecallAll`, sem meias-medidas necessárias.

O cliente é, portanto, uma base vazia para inimigos sob autoridade do anfitrião, o que a etapa 1 precisava.

Assinaturas confirmadas, lidas no log em vez de supostas (Harmony imprime onde aplicou patch):

```
EnemySpawner.SpawnAt(Enemy, Vector3, EnemySpawner.EEnemyScaleMode)
EnemySpawner.SpawnAt(EEnemy, Vector3, EnemySpawner.EEnemyScaleMode)
Enemy.OnSpawn(EnemySpawner, ObjectPool`1, Int32, EnemySpawner.EEnemyScaleMode, Single x6)
Enemy.Die(EDamageType, Int64, Boolean) | Enemy.DeSpawn() | Enemy.Recall()
```

O enum aninhado é realmente `EnemySpawner.EEnemyScaleMode`, e os seis parâmetros `Single` de `OnSpawn` são
os modificadores de atributos.

### <a id="a-blocked-run-the-level-up-screen-stops-everything-2026-10-17"></a>Uma partida bloqueada: a tela de subida de nível para tudo (2026-10-17)

Uma captura de ambas as janelas no fim de uma execução mostra as duas em **"LEVEL AUFSTIEG"** — a tela
de escolha de recompensa — com estado idêntico. Dois fatos decorrem disso:

- O espelhamento de XP e a barreira de subida de nível funcionam: ambos os anões subiram juntos e ambos foram
  retidos na escolha, o propósito da barreira.
- **Nada dispensa a tela porque a automação para deliberadamente.** `CoopAuto` define seu
  sinalizador de conclusão ao entrar em uma partida: o log do anfitrião tem 28 linhas `auto:` no total, a última
  é `auto: IN RUN after 19 steps - automation done` — nada depois. Enquanto isso, o jogo pausa a
  partida com a escolha de recompensa aberta, então congela ali. Duas medições independentes confirmam
  ser a pausa, não o código de sincronização: a posição local fica congelada (`pos=(6.6,0.0,10.0)` por muitas
  amostras), assim como as contagens de inimigos (`enemies=61`, `reg=51`), enquanto o contador de passos do próprio bot
  continua subindo (`steps=10851 -> 11331`) — `LateUpdate` ainda roda, o tempo do jogo não.
  Portanto, a correção não é "ensinar outra página ao condutor"; é manter o condutor atendendo
  telas modais após iniciar a partida, em vez de se aposentar.

Agora este é o primeiro bloqueio: nenhuma medição de inimigos/saque/terreno tem valor até uma partida conseguir
passar da primeira subida de nível sem supervisão.

**Os nomes, capturados em uma partida** (o condutor agora continua observando em vez de se aposentar ao entrar,
o que os produziu):

```
auto: watch: active=UICoreForm        <- the in-run HUD
auto: watch: active=UILevelUpForm     <- the screen that blocks everything
```

Congelamento confirmado independentemente do condutor: nas *duas* instâncias, a posição local é idêntica byte a byte
em quatro amostras consecutivas (`(-11.7,0.0,-2.5)` no anfitrião, `(-1.1,0.0,-11.9)` no cliente), com
contagem de inimigos constante, enquanto `auto: watch: active=UILevelUpForm` é o último estado observado. O jogo
realmente pausa a partida nessa tela.

`DRS.UI.UILevelUpForm` contém `skillButtons : UISkillButton[]` e `skillButtonsLeftToRight` para os
cartões, `rerollButton : UIButtonPrice` para "trocar todos", além de `onFinishedCallback` e um `LevelUpManager`
com corrotina `IEStartFlow`.

**Correção de afirmação anterior neste arquivo:** `UISkillButton` é declarado como `class UISkillButton :
UIButton`, então os cartões *não* são estruturalmente invisíveis a uma enumeração de `UIButton` — uma revisão
anterior desta nota dizia que eram, incorretamente. Nada os pressionava simplesmente porque
o condutor já tinha se aposentado antes desse código rodar. Vale distinguir, pois a correção
difere: é "continuar atendendo telas após iniciar a partida", não "aprender um segundo tipo de botão".

A rota escolhida é pressionar um cartão (qualquer um conclui a escolha local; a barreira de XP então espera
o par). Mira especificamente `UISkillButton`, em vez de "primeiro botão pressionável do formulário",
pois a mesma tela contém o controle de troca — um `UIButtonPrice` — e escolhê-lo gastaria
moeda para trocar a oferta em vez de aceitá-la.

A alternativa, se pressionar um cartão não concluir a escolha, é finalizar por
`LevelUpManager`, que detém o fluxo e o callback de término, contornando a apresentação.

### <a id="resolved-the-level-up-no-longer-freezes-a-run-2026-10-17"></a>Resolvido: subir de nível já não congela a partida (2026-10-17)

Pressionar um cartão não responde à escolha. Uma execução medida pressionou `SelectableWindow_SkillSelect`
pelo caminho comum de `UIButton` — o mesmo que funciona no assistente — e a tela continuou
aberta com a partida congelada. A própria API do formulário explica: o clique chega a `OnSkillSelected`,
que só *pré-visualiza* um cartão, enquanto `OnSkillChosen` confirma. Acionar `OnSkillChosen`
diretamente lançou `TargetInvocationException`, e a falha ficou invisível por uma rodada porque o
patch relatava `e.Message` e descartava `e.InnerException` — uma chamada por reflexão esconde o erro
real ali. **Registrar a exceção interna sempre que uma chamada por reflexão puder lançar exceções.**

O que funciona é `LevelUpManager.OnLevelUpFinished()` — ponto de entrada que este módulo já usa para liberar
a barreira de XP, sendo a única chamada nessa área que se sabia avançar o fluxo. O condutor agora a chama
sempre que `UILevelUpForm` está aberto, e a barreira ainda segura até o par também responder.

Verificado em partida: `auto: level-up finished through LevelUpManager` nas duas instâncias, seis vezes,
com posição local mudando entre amostras (`(1.7,0.0,-11.9)` -> `(11.9,0.0,-1.5)` ->
`(4.9,0.0,11.0)`) e contagens de inimigos subindo até 561/464. Uma partida agora sobrevive a subidas de nível repetidas sem
presença humana, requisito de toda medição posterior.

**Limitação que FOI aceita aqui e desde então removida:** o anão não recebia recompensa nessas
subidas de nível, pois `OnLevelUpFinished` termina a tela *sem* confirmar um cartão. Mantinha a partida
viva, mas significava que toda execução automatizada testava um jogo sem melhorias. Superado — ver
"Cartões de subida de nível" abaixo para o caminho de escolha real e sua evidência.

Também vale registrar da mesma execução, pois é o próximo problema: contagens de inimigos do anfitrião e cliente
já divergiram muito (561 contra 464). As duas instâncias agora rodam tempo suficiente para isso importar,
exatamente o que a etapa 1 existe para corrigir.

### <a id="a-stale-binary-looks-exactly-like-a-fix-that-does-not-work-2026-10-17"></a>Um binário antigo parece exatamente uma correção que não funciona (2026-10-17)

A primeira tentativa de testar a correção da subida de nível mediu silenciosamente a build *anterior*: `Copy-Item` falhou
com a DLL aberta por um processo remanescente do jogo, e o script continuou e iniciou mesmo assim. Qualquer
conclusão dessa execução seria errada, e pareceria falha da correção
em vez de falha da implantação.

A etapa de implantação agora encerra o jogo, repete a cópia até o arquivo não estar bloqueado, compara hashes de origem e
destino e **aborta em vez de executar um binário antigo**. Manter essa verificação na execução
sem supervisão: uma build que nunca chegou à pasta plugins produz a mesma evidência de uma alteração quebrada.

### <a id="two-things-that-now-work-and-one-that-needs-tolerating"></a>Duas coisas que agora funcionam e uma que precisa ser tolerada

- A etapa explícita `UISelectable_Hex_ClassArtifact` do plano é pressionada por nome (`plan[4] ... pressed`),
  então a página de artefato já não depende da alternativa — quando aparece onde o plano espera.
- **A ordem das páginas varia.** Neste perfil, o assistente seguiu nó -> classe -> artefato -> perigo, não
  nó -> artefato -> classe como o plano lista, e a alternativa absorveu. O plano deve aceitar
  as duas ordens em vez de pressupor uma.
- **O determinismo se estende à criação.** As duas instâncias criaram o mesmo primeiro inimigo nas mesmas
  coordenadas — `+id=1 type=LOOTBUG/BASE pos=(82.8,0.0,24.2)` tanto no anfitrião quanto no cliente — porque a
  semente é forçada e os bots agem de modo idêntico. Tentador, mas as contagens já divergem (61 versus 54), então
  a identidade ainda deve vir sob autoridade do anfitrião; combinar por tipo+posição só funcionaria
  até a primeira diferença.

### <a id="lesson-one-bad-patch-must-not-take-the-mod-down-2026-10-17"></a>Lição: um patch ruim não deve derrubar o mod (2026-10-17)

`[HarmonyPatch(typeof(EnemySpawner), "SpawnAt")]` sem tipos de argumentos lança
`AmbiguousMatchException` em um método com sobrecargas. Como a instalação dos patches compartilhava um `try` com a
inicialização do plugin, essa única exceção pulou `AddComponent<CoopTick>()` e `CoopNet.Init()` — o mod
ficou **completamente morto**, com único rastro no log do BepInEx (`LogOutput*.log`, que *não* é
`coop-<role>.log`): o log de função por instância simplesmente ficou vazio, parecendo "BepInEx não
iniciou".

Corrigido em dois níveis: hooks de inimigos resolvem e aplicam patch a cada alvo individualmente, com linha própria de log, e
`ProbePlugin.Load()` agora instala patches em um `try` próprio para uma falha de patch degradar em vez de
desativar. Regra a guardar: **nunca deixar a instalação de patches compartilhar um `try` com a inicialização, e ler o
log do BepInEx antes de concluir algo pela ausência de log de função.**

## <a id="next-phase-world-state-sync-enemies-pickups-terrain"></a>Próxima fase: sincronização do estado do mundo (inimigos, itens coletáveis, terreno)

O boneco é só apresentação. Caverna, insetos e saque ainda são por instância, a lacuna
restante entre "dois anões se veem" e "dois anões jogam juntos".

Levantamento do que o jogo oferece (pelos stubs de interop IL2CPP):

- **`Enemy.id` *não* é ID de instância — é o tipo do inimigo.** `id` (e a propriedade `ID`) tem
  tipo `EEnemy`, enum de 45 valores (`GRUNT0`, `FAST_GRUNT`, `MACTERA_SEEKER`, `LOOTBUG`,
  `BOSS_DREADNOUGHT`, `COCOON`, `EXPLODER_CRYO`, …). Resolve a questão em aberto indicada no
  levantamento anterior: um inimigo do pool **não** é identificável individualmente, então a camada de sincronização **precisa**
  de IDs de rede próprios. `id` diz ao cliente *qual* prefab materializar.
- **O gerador expõe API pública de criação/remoção**, permitindo ao cliente materializar inimigos sob autoridade
  do anfitrião sem acessar mecanismos internos: `SpawnAt(EEnemy enemyId, Vector3 position,
  EEnemyScaleMode scaleMode)` e a sobrecarga `SpawnAt(Enemy prefab, …)`, além de `Spawn(SpawnData,
  EEnemyScaleMode)`, `SpawnWave(FixedWaveState)`, `AddFixedWave(...)`, `OnStageBegin()`,
  `OnStageEnd(CoreLevelEndArgs)`, `OnEnemyDeath(EnemyDeathArgs)`, `RecallAll()`,
  `GetLiveSpecialEnemies(EEnemyType)`, `SuppressSpawnCount(float duration, float regainDuration)`,
  `AddGrowth(float hpMod, float dmgMod, float speedMod)`.
  O registro de ativos é `enemies` (`List<Enemy>`) — campo já amostrado pela sonda — e cada
  inimigo contém uma referência de volta, `Enemy.enemySpawner`, então uma busca genérica de "qual inimigo é este"
  não precisa de busca global.
- **Campos que vale enviar pela rede:** `currentHp` (na base `Entity`), `GetHealthNormalized()`,
  `hasAgent`/`agent` (NavMeshAgent — o que desativar em inimigo espelhado), `baseScale`/
  `scaleMod`, `enemyGfx`/`GFXContainer`, `state` (`EEnemyState { INACTIVE, ACTIVE, KNOCKBACK,
  FEARED }`). Observar que `MaxHp` / `Damage` / `MoveSpeed` / `Range` / `AttackSpeed` são objetos `EnemyStat`
  com tratamento próprio de modificadores (ver `EnemyStat.cs` / `EnemyStatHandler.cs`), não números
  simples — ler pelo tratador de atributos em vez de esperar float.
- **`Enemy` expõe eventos que podemos interceptar em vez de consultar repetidamente:** `OnDeath`, `OnTookDamage`,
  `OnHealed`, `OnSetTargetable`, `OnAttackFrame`, `OnKnockback`. `OnDeath` é a maneira de baixo custo de
  replicar mortes.
- **`EnemySpawner` detém o mecanismo de ondas:** `enemies` (registro de ativos), `enemyPrefabs`,
  `poolDictionary`, `liveElites`, `liveBosses`, `levelWaves` e limites de criação
  (`spawnMinX/MaxX/MinY/MaxY`). A criação passa por um `ObjectPool`, nunca `Instantiate`.
- Atributos dos inimigos chegam por `_baseMaxHp`, `_baseMoveSpeed`, `_baseDamage`, `hazardHpScale`,
  `hazardSpeedScale` — relevante porque perigo é uma das configurações que precisam coincidir.

Formato proposto (autoridade do anfitrião, coerente com o resto do mod):

1. **Suprimir o gerador próprio do cliente** para que não execute uma segunda simulação divergente de ondas.
2. Anfitrião transmite estado dos inimigos **só para inimigos próximos do anão do cliente** (gerenciamento de interesse,
   ~10 Hz, agrupados por pacote) — o enxame atinge cerca de 260 entidades, então transmissão completa está
   descartada. O jogo já inclui uma KDTree (`PhysicsSimulation`) se uma consulta por raio for desejada.
3. Cliente cria um inimigo *visual* por ID recebido pela mesma tabela de prefabs e o interpola.
4. Dano do cliente é informado ao anfitrião ("acertei o ID X por N"), o anfitrião aplica, e mortes
   voltam por `OnDeath`. Nunca deixar os dois lados serem donos do HP dos inimigos.
5. Itens coletáveis (`PickupSpawner`) e terreno minerado (itens de `MapGenerator`/estado de blocos) seguem o
   mesmo padrão depois, nessa ordem — importam menos que os insetos.

É a maior peça restante; deve ser um item de trabalho próprio com a mesma disciplina da
sincronização dos jogadores acima (medir em duas instâncias, registrar ambos os lados, não afirmar sem execução).

## <a id="milestone-shared-xp-and-a-synchronised-level-up-pause"></a>Marco: XP compartilhado e pausa sincronizada ao subir de nível

Também verificado ao vivo (build 23854500, 2026-10-17) e confirmado no jogo:

- **XP é compartilhado, não por jogador.** `Player.GainXp(float amount, bool scaleByXpGain = true)` é o
  único ponto de entrada de XP; espelhar cada ganho ao par e aplicar os ganhos dele com
  `scaleByXpGain: false` mantém os dois anões no mesmo total. Medido: anfitrião
  `lvl=4 xp=28.0 total=153.0` (`sharedOut=95 sharedIn=58`) e cliente
  `lvl=4 xp=28.0 total=153.0` (`sharedOut=58 sharedIn=95`) — idênticos, pois cada total é seus
  próprios ganhos mais os do outro (95+58).
- **Escolhas de subida de nível pausam ambos os jogos até os dois jogadores escolherem.** `LevelUpManager` executa um
  fluxo sobre uma fila de subidas de nível (`levelUps`, `StartFlow` → `HandleLevelUps` →
  `OnLevelUpFinished`). O mod só libera `OnLevelUpFinished` quando ambos informam que suas
  escolhas terminaram, mantendo o fluxo aberto até lá. Retenção registrada: 15:18:27.890
  "holding until remote picks" → 15:18:32.007 "remote picks done" → "released" (~4,1 s).
  Um tempo limite de 45 s libera a retenção para que um par perdido não bloqueie a partida.
- Detalhes úteis encontrados ao construir: `Player.currentXp`, `totalXp`, `currentLevel` são
  campos públicos graváveis diretamente; `Player.blockLevelupScreen` existe, mas não foi necessário;
  `CoreGameEvents.OnPlayerXpGain` / `TriggerPlayerXpGain(PlayerXpGainArgs)` é o evento global de XP
  se um observador for preferível a aplicar patch em `GainXp`; o jogo já inclui um
  `Player.RemoteXPPickUp(Vector3, float)` dormente — não usado, mas evidência de que foi projetado em algum momento para
  ter jogadores remotos.

## <a id="milestone-both-players-visible-in-one-shared-cave"></a>Marco: ambos os jogadores visíveis em uma caverna compartilhada

Verificado em uma execução ao vivo de duas instâncias (build 23854500, 2026-10-17):

- **Sincronização de mapa funciona.** Ambas definem `UnityEngine.Random` para um valor compartilhado (20261017)
  em um prefixo de `MapGenerator.CreateMap`; impressões digitais do mapa retornaram **idênticas (0/81
  amostras diferentes)**, e as duas capturas mostram o mesmo terreno.
- **Jogadores se veem.** Cada instância clona a subárvore visual do jogador local,
  posiciona-a nas coordenadas remotas recebidas, e ambos confirmaram ver dois
  anões na mesma caverna. Evidência do log: `puppet: spawned #2 renderers=9 nullMeshes=0`,
  `pos=(-11.5,0,-3.5)` / `puppet pos=(-11.5,0,-3.5)` no outro lado.
- **Causa-raiz do boneco invisível anterior:** o clone foi tirado do jogador do **menu**
  e nunca reconstruído (modelo do menu = 4 renderizadores; anão em partida = 9). A correção
  foi simplesmente reconstruir o boneco ao iniciar a partida. Uma teoria anterior de que
  `FSG.MeshAnimator` deixava `sharedMesh` nulo estava **errada** — `nullMeshes=0` antes e
  depois, e `meshesCopied=0`; esse código de cópia é peso morto e deve ser removido.
- Transporte sustentado durante toda a execução: ~3200 pacotes em cada direção, ~20 Hz, ~90 s.

Ainda em aberto neste marco: o boneco é **estático** (sem animação de caminhada), inimigos não estão
sincronizados, XP/subidas de nível são por instância, e as duas partidas ainda precisavam ser iniciadas com
configurações correspondentes (perigo é transmitido, mas o caminho de imposição no cliente não foi exercitado).

## <a id="measured-co-op-numbers-real-run-build-23854500"></a>Números medidos do cooperativo (partida real, build 23854500)

Da sonda no jogo durante uma missão normal completa (~5 min):

- **Inimigos ativos sobem de 9 a um pico de 261** e ficam em 220–261 no fim da partida.
  Progressão amostrada: 9, 11, 13, 16, 20, 25, 38, 57, 101, 124, 148, 189, 226, **261**.
- `liveElites` atingiu 1; `liveBosses` 0 (missão padrão, não partida de chefe).
- Inimigos legíveis por entidade, incluindo nome de prefab:
  `enemy0 name=Lootbug(Clone) pos=(7.2,0.0,94.5) hp=80 alive=True`.
- Jogador: HP 210 → 220, **15** eventos de queda de HP, posições acompanhadas continuamente, 0 na morte.
- Hooks de ciclo de vida confirmados: `GameController.OnCoreRunStarted`, depois `StartGame` ao descer;
  `enemies=0` após extração.

**Restrição de projeto estabelecida:** sincronizar ingenuamente ~260 entidades a 20 Hz representa ~5 mil atualizações de entidades
por segundo por cliente. Portanto, a camada de entidades precisa de **gerenciamento de interesse mais
codificação de prioridade/delta**, em vez de transmissão de estado completo. (O próprio jogo inclui uma KDTree usada
por `PhysicsSimulation` / `PopulateKDTreeDataJob`, candidata a índice espacial reutilizável.)

**Caminho sem saída registrado:** `AI_Manager._units` *não* é o registro do enxame — permaneceu vazio por uma
partida inteira e seu patch de `Update` nunca disparou, então o gerenciador é inativo/não usado em jogo normal.
O registro real é `EnemySpawner.Enemies` (`List<Enemy>`), acessado por
`GameController.enemySpawner`.

## <a id="stand-spot-problem-measured-solved-by-self-check"></a>Problema do ponto de parada (medido, resolvido por autoverificação)

O objetivo era um ponto de vista fixo para capturas comparáveis. Fatos medidos, um por ponto candidato:

- **Origem do prefab `(0,0,0)`**: morta. 535 inimigos na lista, nenhum visível ou alcançável — a
  origem fica dentro da rocha/fora da caverna.
- **Ponto inicial atribuído pelo jogo (cápsula de pouso)**: morto e pior — o anão fica preso no colisor
  da cápsula e nunca consegue sair.
- **Ponto no círculo de caminhada `(10,0,0)`**: morto. Autoverificação `near=` (inimigos a até 15 unidades)
  ficou 0 por 60 s, e o bot voltou automaticamente a caminhar. Ao mesmo tempo, o anfitrião tinha 390
  inimigos na lista — um enxame completo incapaz de alcançar o jogador. Contagem de lista não é
  evidência de presença; só `near=` é.
- **Caminhar no círculo** (raio 12 ao redor de `(10,0,0)`): vivo. Em minutos, `near=445`,
  `die=589` — inimigos lotam o caminho, armas os matam.

Resultado: `CoopBot` já não confia em ponto fixo algum. `Still` mantém um candidato; se o anfitrião vê
`near=0` por 60 s, registra `bot: spot dead, walking` e retorna à caminhada. O cliente nunca executa a
alternativa (seu gerador é suprimido, então seu `near` é 0 por projeto); continua seguindo
`RemotePos + 2`, o que também mantém os dois anões separados por ~2 unidades na caminhada — cada janela
mostra o outro anão o tempo todo. `check: stand PASS` dispara uma vez quando `near >= 50`.

Modo deus é `player.currentHp = 100000` a cada tick (500 era o máximo do próprio anão, e uma matilha podia
esgotá-lo em um quadro). Estado da partida às 21:33: anfitrião `enemies=560 near=445 die=589`, cliente
`enemies=0 sup=626`, `reg==live` se mantém (a reconciliação o torna verdadeiro por construção).

## <a id="stage-1-enemy-transport--works-verified-by-log-lines-build-of-2146"></a>Etapa 1, transporte de inimigos — FUNCIONA, verificado por linhas de log (build das 21:46)

Espelhamento de criação/morte sob autoridade do anfitrião pelo canal LiteNetLib existente:

- Na rede: `EnemySpawn{netId u16, EEnemy u16, q-pos 3×s16, scale u8}` (0,1 unidade/passo, ponto
  fixo de 16 bits), `EnemyDeath{netId u16}`, `EnemyCensus{count u16}` a cada 5 s. ReliableOrdered.
- Anfitrião envia de `Register`/`OnDied`; cliente nunca envia tráfego de inimigos. Cliente recria por
  `EnemySpawner.SpawnAt(EEnemy, Vector3, EEnemyScaleMode)` com `ApplyingRemote=true` (a proteção que a
  supressão já respeita), usando o ID do anfitrião como chave dos espelhos (`Entry.HostNetId`).
- Callbacks de rede só enfileiram; `ProcessRemote()` drena na thread principal uma vez por quadro —
  objetos Unity nunca são tocados pela thread de rede.

Medido em partida real (log do cliente):

- `check: freeze drift=0,00 units over 2s` — `SetAgentEnabled(false)` realmente congela um espelho.
  Os nomes da API foram extraídos primeiro do assembly real (`SetAgentEnabled`, `SetBehaviour`,
  `get_Agent`, `get_Behaviour`, `hasAgent`), não presumidos pelo plano.
- `check: enemy transport host=30 mirrors=43 spawn=50 death=2 localDie=3 fail=0 miss=0` — a
  contabilidade fecha exatamente (`spawn − death − localDie == mirrors`).
- Transporte de morte é exato: `die=213` do anfitrião correspondeu a `death=213` do cliente na primeira execução de transporte.
- Dois erros encontrados e corrigidos pelos números: (1) as primeiras ~20 mensagens de criação chegaram antes de
  o gerador do cliente existir e foram descartadas (`fail=20`) — agora ficam em `PendingSpawns` e
  tentam novamente (`fail=0`); (2) as próprias armas do cliente matavam espelhos (`localDie=73` na execução 1) — o
  congelamento também elimina a maior parte disso (`localDie=5`), porque um espelho congelado já não entra no
  alcance das armas do cliente; os 5 restantes morreram antes de o congelamento fazer diferença.
- Restante, honestamente: 2 mortes `miss` de IDs criados antes do par conectar; o censo atrasa
  pelas mensagens em trânsito; posições dos espelhos são a captura da criação (capturas de posição por tick são
  o próximo passo, blocos do tamanho de MTU, quantizados).

A janela do cliente agora mostra inimigos reais — enxame do anfitrião, congelado nas posições de criação.

## <a id="stage-1b--position-snapshots-mirrors-follow-the-host-build-of-2201"></a>Etapa 1b — capturas de posição: espelhos seguem o anfitrião (build das 22:01)

Anfitrião retransmite toda posição de inimigo a 2 Hz, dividida em blocos de 120 entradas (961 B < MTU),
`EnemySnapshot{count u8, (id u16, q-pos 3×s16)×N}` por `DeliveryMethod.Sequenced` (esta
build LiteNetLib não tem `UnreliableSequenced`). Cliente aplica movendo o transform do espelho congelado
— agente congelado + teleporte = boneco que segue sem executar IA própria.

Medido em partida real (log do cliente):

- `check: sample moved total=5,4 units (id=5)` — o espelho amostrado comprovadamente segue seu
  original no anfitrião.
- `check: snapshot applied=1031 missed=83 recv=1114` — perdas são a corrida entre canais:
  mortes são ReliableOrdered, capturas Sequenced, então um bloco pode chegar logo após uma morte.
  Cosmético; o próximo bloco omite o inimigo morto.
- Estado final da partida: anfitrião `enemies=192`, cliente `mirrors=172` (`census=192` atrasa pelas mortes
  em trânsito); `fail=0` — a repetição pendente segue funcionando.
- Efeito colateral medido: `localDie=45` — espelhos que se movem com o anfitrião entram no alcance das
  armas do cliente, então ele mata alguns e eles deixam saque exclusivo do cliente. A etapa 2 deve suprimir
  saque gerado por mortes de espelhos (ou mortes causadas pelo cliente), senão o estoque compartilhado começa a
  contar em dobro.

A etapa 1 está concluída: ambas as janelas mostram o mesmo enxame, movendo-se junto.

## <a id="stage-2-loot--discovery-run-build-of-2220"></a>Etapa 2, saque — execução de descoberta (build das 22:20)

Assinaturas verificadas no assembly real:

- `PickupSpawner.SpawnXP(Vector3, Int32, EXPSource, Single) -> Void`
- `PickupSpawner.SpawnLargeXP(Vector3, Int32, EXPSource, Single) -> Void`
- `PickupSpawner.SpawnMaterial(ECurrency, Int32, Vector3, Single) -> Void`
- `PickupSpawner.SpawnMaterialNoForce(ECurrency, Vector3) -> Pickup` ← a única que retorna Pickup
- `Player.OnPickupClaimed(Pickup) -> Void` — caminho real de coleta, dispara com um Pickup.

Medido em partida: anfitrião `spawns=686 claims=4` em ~7 min (bot caminhante raramente coleta), cliente
`spawns=261 sup=261` — supressão sob autoridade do anfitrião se mantém, toda tentativa de criação no cliente é recusada.

Em aberto: campos de valor/ID de `Pickup` não foram encontrados no tipo declarado (zero membros extraídos), então
provavelmente vivem numa classe-base — a extração deve percorrer BaseType em seguida. Plano do caminho espelhado: receptor usa
`SpawnMaterialNoForce` + `SetId(netId)` + define campo de valor por reflexão; coletas transmitem
`{netId}`, receptor remove o espelho e aplica o delta só quando `Wallet.ShouldSaveValue`
indica que é local à partida. Orbes de XP NÃO são espelhadas — o canal XpGain já transporta XP.

## <a id="stage-2-loot--transport-works-build-of-2236"></a>Etapa 2, saque — transporte funciona (build das 22:36)

- Na rede: `LootSpawn{currency u8, value i32, q-pos 3×s16}`, `LootClaim{same}` — coletáveis são combinados por
  (moeda, valor, posição), não por ID, pois as sobrecargas de criação void não retornam Pickup para
  marcar. `PickupSpawner` é acessado por `GameController.pickupSpawner` (encontrado por reflexão de tipos).
- Cliente espelha por `SpawnMaterialNoForce(ECurrency, Vector3)` sob `ApplyingRemoteLoot`;
  valor definido pelo acessor privado `value` (a propriedade pública `Value` é somente leitura).
- Medido: `check: loot mirrors=20 spawn=20 claim=1 miss=1 fail=0` — toda criação espelhada, primeira
  coleta encaminhada, mas PERDIDA: o coletável do anfitrião tinha se espalhado (SpawnMaterial aplica força), então a
  posição de coleta já não corresponde à de criação dentro do raio de 0,5 unidade. Correção: combinar por
  (moeda, valor, mais próximo) em raio maior e registrar distância da perda.
- API Wallet verificada: `Add(CurrencyValue)`, `ShouldSaveValue(ECurrency)`, `GetAmount(ECurrency)`.
  A etapa de crédito (só moedas locais à partida) ainda precisa do caminho de acesso à instância Wallet e do
  construtor CurrencyValue — descoberta em execução, como pickupSpawner.

## <a id="stage-2-loot--full-loop-works-build-of-0011"></a>Etapa 2, saque — ciclo completo funciona (build das 00:11)

Evidência positiva de partida real: `loot: credited cur=2 value=1 total=41…46` — a carteira do cliente
recebe crédito quando o anfitrião coleta. Todo o fluxo executa: criação no anfitrião (itens de teste por
`SpawnMaterial(NITRA, …)` sob `-cooptestloot` a cada 10 s, mais itens reais de mineração de
`Player.TryMine()` chamado pelo bot do anfitrião a cada 30 quadros) → transmissão → espelho no cliente por
`SpawnMaterialNoForce` → coleta no anfitrião → transmissão → cliente remove espelho e credita
(`Wallet.Add(CurrencyValue)`, condicionado por `ShouldSaveValue`). Nitra é local à partida; crédito se aplica.

Ressalvas medidas, todas compreendidas:

- Mensagens de coleta transportam posições do POOL: `OnPickupClaimed` devolve o coletável ao pool antes
  de o postfix rodar, então o transform lê a origem do pool (distâncias das perdas cresceram de 1273→2217 unidades).
  TODA variante de prefixo nesse método falhou na compilação IL do Harmony (`IL Compile Error (unknown
  location)`), incluindo um prefixo void na sobrecarga explícita `(Pickup)` — então o receptor
  combina por (moeda, mais próximo) em até 40 unidades. ~41/197 coletas corresponderam e foram creditadas;
  o restante se perdeu. A posição deve ser capturada de outro hook (por exemplo, o método de coleta do próprio Pickup)
  em trabalho posterior.
- O `value=1` creditado também é lixo do pool — `pk.Value` do anfitrião lido após retornar ao pool.
- `fail=13/80` criações de espelhos — transitório; ainda não investigado.
- Definidor de valor no cliente funciona pelo acessor privado `value` (`Value` público somente leitura).
- `Player.TryMine()` é o ponto de entrada real da mineração (verificado pela extração da API); o bot chamá-lo
  enquanto caminhava produziu materiais naturais sem mudança de caminho. `MapGenerator.blockList`
  é `List<MaterialBlock>` — o tipo é `MaterialBlock`, não `MineableBlock`.

## <a id="stage-2-loot--complete-build-of-0052"></a>Etapa 2, saque — CONCLUÍDA (build das 00:52)

O ciclo completo agora executa com números correspondentes, verificado por linhas positivas de log:

- Transmissão de criação movida para **`Pickup.OnSpawn`** (hook de inicialização por objeto): itens de mineração contornam
  completamente `SpawnMaterial`/`SpawnMaterialNoForce` — medido 146 coletas contra 31 transmissões antes da
  mudança, e `sentCur={0:12 2:151 3:4}` contra `claimCur={2:145 0:1}` depois. OnSpawn vê cada caminho,
  exatamente como `Enemy.OnSpawn` fazia para ondas.
- Créditos do cliente fluem 1:1 com coletas: `loot: credited cur=2 … total=146`. Moeda correta
  (coletas correspondem a espelhos por FIFO — posições do pool continuam lixo, todo prefixo em
  `OnPickupClaimed` falha na compilação IL do Harmony).
- Corrida de mensagens precoces corrigida pelo mesmo padrão de repetição pendente dos inimigos (`fail=0` depois).
- Resíduo conhecido, documentado: valores creditados são `value=1` — `Pickup.OnSpawn` dispara ANTES de o
  jogo definir o valor do coletável (o valor real é aplicado depois pelo acessor `set_value(Int32)`,
  presente na extração da API). A correção é ler o valor após o definidor ou um quadro
  depois; cosmético, contabilidade exata.
- Aparato de testes agora: `-cooptestloot` deixa NITRA(5) no jogador anfitrião a cada 5 s; o ciclo de consulta
  comprova uma build em ~1 min após iniciar a missão, em vez de uma espera cega de 8 minutos.

## <a id="stage-3-terrain--entry-points-verified-build-of-0102"></a>Etapa 3, terreno — pontos de entrada verificados (build das 01:02)

`MaterialBlock` (namespace `Assets_Scripts_LevelGeneration`, encontrado por busca de nome simples em todos os
assemblies carregados — `GetType(name)` perde tipos com namespace):

- `Die(Boolean, Boolean, Boolean)` — entrada de destruição, hook para transmissão `{x,y}`.
- `Setup(MapGenerator, VFXManager, Int32, Int32, RunSettingsManager)` — os dois Int32 são coordenadas
  da grade; receptor resolve o bloco por `MapGenerator.blockList` e destrói silenciosamente.
- `TakeDamage(Double, Player, Boolean, Boolean, Enemy, WeaponHandler)`, `UpdateNeighbors()`,
  `get_MaterialType()`, `Inject(PickupSpawner)` — componentes auxiliares.
- Resíduo de valor do saque confirmado: mesmo um quadro após `OnSpawn`, o valor do coletável ainda é 1 — o
  jogo aplica o valor real tardiamente (pelo acessor `set_value`, provavelmente perto da coleta). Cosmético;
  valores errados por uma constante, contabilidade exata.
