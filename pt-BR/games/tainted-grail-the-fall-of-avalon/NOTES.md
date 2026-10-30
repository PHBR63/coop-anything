# <a id="tainted-grail-the-fall-of-avalon-working-notes"></a>Tainted Grail: The Fall of Avalon: notas de trabalho

Notas brutas, escritas conforme avançamos; o relato organizado está em README.md. Assumido em
https://github.com/cranebeaker/coop-anything/issues/30 (2026-10-19).

## <a id="triage-playbooktriagemd"></a>Triagem (playbook/triage.md)

1. **Qual jogo.** Tainted Grail: The Fall of Avalon (Questline / Awaken Realms, PC).

   | | |
   |---|---|
   | Loja | Steam, app 1466060, ramo beta `mono` |
   | Compilação | buildid 25966682, versão do jogo 1.30.102 (`[1.30a]`) |
   | SHA-256 do executável principal | `e01f1a4cfa8ebb93f7d5c9ea3925cef2883e1d230741ede76ad4f4c7d1bcd594` (`Fall of Avalon.exe`) |
   | Motor | Unity 6000.0.41f1, scripts Mono no ramo `mono` |
   | SO | Windows 11 |

   O ramo padrão da Steam presumivelmente é IL2CPP (a descrição do TGCoop diz que o BepInEx 5 não
   consegue interceptá-lo); não verificamos. O ramo `mono` é um beta oficial da Steam, portanto um mod
   cooperativo para ele não precisa alterar o jogo além de adicionar o carregador de mods.
2. **Já existe?** Existe um mod cooperativo, TGCoop (abaixo). Não havia nada neste repositório antes de
   assumirmos o trabalho.
3. **Motor.** Unity, backend de scripts Mono (`Fall of Avalon_Data\Managed\`, 279 DLLs; o
   log do jogo diz "[Modding] Mono build"). Código do jogo em `TG.Main.dll` e `Awaken.*.dll`.
   Mods cooperativos Unity de outros jogos (Nitrox, HKMP, QSB, CelesteNet em
   playbook/engine-families.md) mostram o caminho habitual de BepInEx/Harmony; nenhum atende este jogo.
4. **Quanto código-fonte.** Binário fechado, mas Mono: as DLLs gerenciadas são descompiladas em C# legível
   com os nomes originais (ilspycmd 11.1, cerca de 6.200 arquivos para `TG.Main`). BepInEx 5 +
   Harmony conseguem carregá-lo e aplicar patches. O desenvolvedor também publica um kit oficial de criação de mods,
   [AR-Questline/merlin-workshop](https://github.com/AR-Questline/merlin-workshop), um projeto Unity
   com "uma versão simplificada do código-fonte do jogo". Ele cria **apenas mods de recursos e
   dados**: "permite substituir recursos Addressables" (pacotes de recursos, `catalog.json`,
   `mod.meta` em `%USERPROFILE%\AppData\LocalLow\Questline\Fall of Avalon\Mods`), portanto
   não pode conter o código de um mod cooperativo. Sua licença é uma EULA para a ferramenta em beta aberto
   ("ao usar a Ferramenta, você concorda"): uso gratuito exclusivamente para criar mods para o jogo, sem
   lucro, sem compartilhar ou modificar a própria ferramenta, sem fazer engenharia reversa ou descompilar
   a ferramenta ou o jogo. Não a utilizamos.
5. **Multijogador no motor.** Nenhum. O jogo inclui Steamworks.NET e Heathen (recursos Steam,
   saves na nuvem), GOG Galaxy e o módulo do motor Unity `UnityEngine.MultiplayerModule`,
   mas nenhuma biblioteca de rede. Um moderador no fórum Steam: "Não haverá nenhuma forma de
   multijogador neste jogo" (tópico 686368595766265552). Portanto, o cooperativo exige criar uma camada de sincronização
   com autoridade do anfitrião.
6. **Distribuição.** Um plugin BepInEx é distribuído sem arquivos do jogo. Não há antitrapaça na instalação
   (nenhuma pasta EasyAntiCheat ou BattlEye), nem serviço online. O jogo envia relatórios automáticos de erros
   com saves anexados quando um carregamento falha (Unity User Reporting): bloqueie-os nas cópias
   de teste.

## <a id="existing-work"></a>Trabalho existente

- **TGCoop** ("2 Players Steam Coop"), https://www.nexusmods.com/taintedgrailthefallofavalon/mods/211,
  autor hektormenta. BepInEx 5 + Harmony, 2 jogadores, salas Steam e
  SteamNetworkingMessages no app id do próprio jogo, autoridade do anfitrião. Compilação mais recente que encontramos:
  0.5.36 (`TGCoop.dll` datada de 2026-07-28; SHA-256 do zip
  `6a4c372e82b026668e7e75fe0d93ad771b5ce0f83140bd72a5a0ea65315d272e`). Sem arquivo de licença,
  sem código-fonte; readme em espanhol. A página informa que foi criado com auxílio de IA.
  - Modelo de sessão (no readme): os dois jogadores carregam seu próprio save; então o convidado entra e
    o anfitrião envia uma base de estado.
  - Sincronização da história (pela leitura da DLL descompilada): interceptações em tempo real em `StoryFlags.Set`,
    `QuestUtils.SetQuestState`, `QuestUtils.ChangeObjectiveState`; ao entrar, o anfitrião envia apenas
    os fatos booleanos verdadeiros de cada contexto de memória. Outras gravações no armazenamento de flags do jogo
    (`GameplayMemory` → `ContextualFacts`: estados de atores NPC, locais descartados, variáveis
    da história, cenas visitadas) e valores falsos ou não booleanos não são sincronizados.
  - Relatos de erros (comentários no Nexus, de julho a outubro de 2026): após o diálogo de Odrán, o portão da fortaleza
    permanece fechado para o parceiro; iniciar um diálogo durante uma luta contra chefe trava a movimentação do parceiro
    até ele entrar novamente; dessincronização constante no combate (cintilação, teletransporte); pose A, a menos que
    ambos usem terceira pessoa; a caixa de diálogo do mod cobre as escolhas do jogo;
    "uma bagunça cheia de bugs e sujeita a bloqueios de progressão". O autor (2026-07-14): um projeto de hobby, somente o Ato 1
    foi realmente testado; a pose do corpo em primeira pessoa é reconstruída porque o jogo nunca
    calcula uma. O autor não respondeu aos comentários de setembro e outubro.
  - Mais comentários, de 2026-07-21 a 2026-08-06 (colados pelo proprietário em 2026-10-20; respostas do autor
    de 2026-07-26 a 2026-07-28, nenhuma depois):
    - Jogadores: o convidado fica preso correndo sem sair do lugar perto do teletransporte de Archspire (F3, teletransportar
      até o anfitrião, o libera; 2026-08-06); inimigos vivos para um jogador e mortos para o
      outro; um chefe morto apenas para um; entrar na sessão de alguém menos avançado concluiu automaticamente suas
      missões do Ato 1, mas as flags de progressão não acompanharam; receitas de missões secundárias (ferreiro)
      e recompensas de Druid Shrine chegam apenas ao jogador no diálogo; "erros e
      travamentos gerais", resolvidos quando o anfitrião sai e entra novamente.
    - Autor, 2026-07-26, dois erros corrigidos na 0.5.36: (1) "O jogo deixa de simular qualquer coisa
      distante da sua própria câmera"; o anfitrião relatava inimigos que não estava simulando como "não atacando
      ninguém", então a IA do convidado redefinia seus alvos (um monstro perseguindo os dois jogadores), e a
      vida congelada no anfitrião sobrescrevia os golpes do convidado (inimigos "quase impossíveis de matar"). Correção: o
      anfitrião informa "não consigo observar este" e o convidado mantém a autoridade sobre esse inimigo
      até o anfitrião poder vê-lo. (2) "O jogo se recusa a salvar enquanto considera que você está em
      combate"; um atacante fantasma ficou associado ao anfitrião, portanto todos os saves, manuais e
      automáticos, foram recusados silenciosamente durante 4 horas; uma morte do anfitrião fez perder essas horas. "Mudar
      de área limpa o estado preso."
    - Autor, 2026-07-27: jogue o prólogo sozinho e depois conecte; cada jogador mantém seu próprio
      personagem, inventário, ouro, XP e nível, e apenas o mundo e a história são compartilhados; ambos devem
      jogar ou ambos pular o prólogo, senão os gatilhos da história quebram ("o barco de Caradoc simplesmente
      se recusa a funcionar"); a história do convidado "converge para a do anfitrião".
    - Autor, 2026-07-28: incompatibilidades de versão só eram escritas no log (corrigido: aviso
      na tela); chefes são um ponto fraco porque "seus IDs internos diferem por máquina e
      precisam ser pareados pela posição"; falas de diálogo não são reproduzidas para quem escuta,
      apenas texto e escolhas são transmitidos; a limitação a dois jogadores está "bastante enraizada" (um parceiro, um
      corpo substituto, uma conexão).
  - Dedução, não testada: como cada jogador mantém seu próprio mundo e apenas essas três interceptações
    são sincronizadas em tempo real, o estado do mundo fora delas pode divergir; uma causa plausível para o portão
    fechado.
- Menções sem nome: um moderador no fórum Steam em janeiro (ano não exibido, presumivelmente
  2026): "Até onde sei, alguém está trabalhando em um mod multijogador, mas não faço ideia de quanto ele
  avançou" (tópico 686368595766265552); um jogador em abril: "Veja o canal de conversa sobre mods
  no Discord. Tem alguém trabalhando nisso" (tópico 796712917458249380); postagens posteriores sobre um
  mod cooperativo BepInEx no Nexus (585058364697005929, 589558792744841182), presumivelmente TGCoop.
  Não se sabe se as menções de janeiro e abril são ao autor do TGCoop ou a outro projeto.
- Um comentário no Nexus (2026-07-15) afirma que seu autor criou cooperativo local e online e que "outras
  duas pessoas fizeram versões com IA"; nenhum projeto, link ou compilação encontrado.
- Não cooperativo: RealSkye (https://ko-fi.com/realskye) cria mods de Tainted Grail (Avalon Atlas,
  Better UI, Better Movement, Better Mounts, Wyrd Sight, Avalon Mod Manager) e de No Man's Sky.
  A página, lida pelo proprietário em 2026-10-20, não lista mod cooperativo para nenhum jogo. (Ko-fi
  retorna 403 para buscas automatizadas. Dois resumos da página em mecanismos de busca alegavam um
  cooperativo em desenvolvimento, um para Dying Light: The Beast, outro para Tainted Grail "in the
  Restored Land"; nenhum consta na página. Resumos de busca de uma página que não conseguimos abrir não são
  uma fonte.)

## <a id="where-we-looked-2026-10-19-rechecked-2026-10-20"></a>Onde procuramos (2026-10-19, conferido novamente em 2026-10-20)

- Neste repositório: DIRECTORY.md, `games/`, issues e PRs: nada antes de assumirmos o trabalho.
- Busca na web: inglês ("Tainted Grail Fall of Avalon co-op mod", "multiplayer mod",
  "coop online mod BepInEx", tópicos cooperativos no Reddit, TGCoop e seu autor pelo nome), polonês
  ("Upadek Avalonu tryb kooperacji mod multiplayer"), russo ("кооператив мод мультиплеер");
  acrescentados em 2026-10-20: alemão ("Koop Mod Mehrspieler"), chinês ("圣杯传说 阿瓦隆的陨落 联机 mod";
  o título chinês é 《污痕圣杯:阿瓦隆的陨落》), japonês ("マルチプレイ 協力 MOD"), "new release
  October 2026", guias Steam. Apenas artigos gerais, TGCoop (ainda 0.5.36, última atualização
  em 2026-07-28, segundo sua listagem Nexus nos resultados) e o jogo de tabuleiro (um produto
  cooperativo separado). O mecanismo de busca indexa o Nexus mal.
- GitHub: busca de repositórios ("tainted grail coop/multiplayer", "fall of avalon
  coop/multiplayer/mod", "TGCoop", "avalon coop"), busca de código (`Awaken.TG.Main`); acrescentados
  em 2026-10-20: os 30 repositórios "tainted grail" atualizados mais recentemente (até 2026-10-19) e o tópico
  `tainted-grail`. Coleções de mods, o kit oficial e mods para um jogador, sem cooperativo.
  Vários repositórios chamados "free full version", "trainer undetected", "cheats" parecem iscas de
  download: não foram abertos.
- Nexus: página, comentários e arquivos do TGCoop (páginas bloqueadas para buscas automatizadas; lidas pelo
  proprietário e a partir da compilação baixada).
- Fórum Steam: busca "coop mod" (24 resultados), tópicos acima. Declaração do desenvolvedor encontrada
  em 2026-10-20, tópico "Add Co-Op" (4630359473422132923), kpx_ar [developer], 2024-12-03: "Para ser
  sincero, é improvável que isso aconteça. Este jogo foi concebido para uma experiência exclusivamente solo."
- Tópico "mod support" do RPGWatch (63758): 403 para buscas automatizadas; lido pelo proprietário
  em 2026-10-20: nenhum projeto cooperativo.
- ModDB, Reddit: apenas pela busca na web, nada encontrado. Archive.org: não consultado (o jogo
  é de 2025). Discord do jogo: não consultado (decisão do proprietário, 2026-10-19).

## <a id="decision-build-from-zero-not-revive-tgcoop-owners-decision-recorded-2026-10-19"></a>Decisão: criar do zero, sem retomar TGCoop (decisão do proprietário, registrada em 2026-10-19)

Caminho 2 em vez do caminho 1. Motivos: os erros relatados do TGCoop; sua forma de lidar com sincronização e saves
(cada jogador carrega seu próprio save, o anfitrião sobrepõe apenas flags verdadeiras da história, portanto o estado do mundo
fora dessas interceptações pode divergir); e remendos visíveis em seu código (patches "Guard", como
`SaveLoadGuard`, `CombatFlagGuard`, `TppIkGuard`, que suprimem sintomas). Fazer isso corretamente
do zero pareceu o melhor caminho. Nenhum código do TGCoop é usado; sua auditoria orientou o projeto
(o mundo do anfitrião é o mundo compartilhado; o personagem do convidado é incorporado ao save do anfitrião no carregamento).

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para cooperativo)

### <a id="observations-from-the-decompiled-code"></a>Observações (a partir do código descompilado)

- Framework MVC próprio (`Awaken.TG.MVC`): `Model` com IDs de texto `<Type>:<counter>`,
  elementos aninhados `<parentId>:<Type>:<counter>`, contadores por tipo em `IdStorage`, eventos por
  `ModelExtensions.Trigger`, serviços por `World.Services`.
- O estado da história é um armazenamento de chave/valor: `GameplayMemory` → `ContextualFacts.Set/Change/Remove`.
  `StoryFlags.Set`, estado de missão (`Context(quest).Get("state")`) e estado de objetivo ficam todos ali.
  Outros gravadores incluem `ActorsRegister` (`Context("actors")`), `Location`
  (`Context("discarded.places")`), comportamentos de inimigos, variáveis da história, cenas visitadas.
- Um único jogador em toda parte: `Hero.Current` é estático e referenciado em cerca de 1.240 lugares.
- Saves: um zip por slot, um arquivo `.data` por domínio (`Gameplay.data`: herói, itens, missões,
  memória; um arquivo por cena visitada; `MetaData.data`). Todos os saves e preferências passam por
  `CloudService` (Steam Cloud, Steam sem nuvem, GOG, depuração).
- Os modelos são salvos e restaurados na ordem de registro do mundo, em uma única passagem de `RestoreWorld`. Durante
  a restauração, missões do mundo leem atributos do herói (`StatTracker`), e elementos do herói leem modelos do mundo
  (`TrespassingTracker` → `GameRealTime`), portanto herói e mundo dependem um do outro no carregamento.
- New Game+ (`NewGamePlusUtils`) já extrai um personagem (subárvore do herói, itens do herói e do baú
  menos itens de missão, chaves e textos legíveis, diário, missões de conquistas, tempo de jogo) para um blob e
  o restaura em outro mundo (`LoadSystem.DeserializeNewGamePlusCache`).
- A dificuldade é uma configuração indexada pelo GUID `HeroID` do personagem em PlayerPrefs, sem fazer parte do
  slot de save. Story, Easy, Normal, Hard, Survival (restrições de salvamento), Challenge (bloqueado, acrescenta um
  elemento `HeroChallengeMode` ao herói).
- O jogo inclui Steamworks.NET + Heathen, GOG Galaxy, Unity User Reporting (relatórios automáticos de erros
  com saves recentes, logs e configurações anexados quando o carregamento falha), Sentry, GameAnalytics
  e sua própria interceptação `Automations` na tela de título.

### <a id="character-transfer-experiment-2026-10-18"></a>Experimento de transferência de personagem (2026-10-18)

Objetivo: colocar o personagem do jogador B no mundo do jogador A, para que um convidado cooperativo mantenha seu personagem.
Método (plugin BepInEx, apenas na instalação de teste):

1. Exportar o personagem B usando a seleção e o serializador do New Game+.
2. Carregar o save A normalmente. Logo após restaurar o domínio Gameplay, descartar o herói A e seus
   itens e desserializar o blob de B. Durante a leitura do blob, somar
   100000 a cada ID `Item:<n>` (interceptação em `SaveReader.ReadAscii`, por onde todos os IDs passam), para que os itens de B não
   colidam com os itens do mundo A; diário, missões de conquistas e tempo de jogo de B são ignorados.
3. Teletransportar o herói B até a posição do herói A após o carregamento (o blob contém a posição antiga de B).
4. Ao salvar, mover a subárvore do herói e os itens importados de volta ao seu lugar normal na ordem dos modelos
   (após `PlayerJournal`); caso contrário, o recarregamento restaura missões antes do herói e falha.

Resultados:

- Etapas 1 a 3: carrega para a jogabilidade, herói controlável. O mesmo personagem (dois saves de uma
  campanha) como origem e destino.
- Etapa 4, salvar, reiniciar do zero e carregar normalmente: herói, itens e posição intactos, sem erros além
  dos presentes no carregamento normal do mesmo save.
- Dois personagens diferentes (2026-10-18): "Berian" (nível 3, 251 de ouro, 45 itens, jogo novo) no
  mundo de "Selvar" (nível 2, 129 de ouro, 151 itens). Após troca, save, reinício e carregamento
  normal: Berian, nível 3, 251 de ouro, 41 itens na posição de Selvar; sem erros além dos de um carregamento normal.
  Os 4 itens ausentes são os itens de missão, chaves e textos legíveis que o filtro do New Game+ exclui.
- Manter todos os itens (2026-10-18): durante a exportação, `NewGamePlusUtils.ShouldItemBeSaved` é
  sobrescrito para manter cada item pertencente ao herói ou a `HeroStorage`. Berian: 45 de 45 itens após
  troca, save e recarregamento.
- Surgimento durante o carregamento: prefixo em `LoadingScreenUI.CleanupAfterLoading` teletransporta o herói
  importado para a posição do anfitrião + 1,5 m ao longo do vetor direito do anfitrião, ajustado com
  `AstarPath.active.GetNearest(pos, NNConstraint.Walkable)`. Anfitrião em (-95.99, -0.23, 59.27), convidado
  surgiu em (-94.65, -0.24, 58.62) antes de a tela de carregamento desaparecer. Definir `Hero.MoveTo` logo
  após restaurar o blob não persistiu (a posição ainda não foi rastreada).
- Ordens que não funcionaram: restaurar o convidado antes do domínio Gameplay do anfitrião (o herói precisa
  dos modelos do mundo); carregar o domínio Gameplay do anfitrião sem seu herói (as missões precisam do herói).

### <a id="planned-save-design-owners-decision-2026-10-18"></a>Projeto planejado de saves (decisão do proprietário, 2026-10-18)

- Saves cooperativos ficam separados dos saves solo. O save do anfitrião é a única fonte da verdade: o
  mundo e um arquivo de personagem por jogador, identificado pelo Steam ID.
- Ao entrar, o anfitrião envia o save inteiro; o convidado o carrega e substitui o personagem pelo seu
  (a transferência acima). Ao salvar ou sair, o convidado devolve seu personagem ao anfitrião.
- Um único mundo evita divergência entre cópias. Um jogador novo em um save começa como cópia do
  personagem do anfitrião (alternativa de contingência); depois, talvez um personagem novo.
- O cooperativo usa a dificuldade do anfitrião.

### <a id="co-op-save-data-2026-10-19"></a>Dados de save cooperativo (2026-10-19)

- Carregar um slot copia **cada** entrada do zip para o cache de domínios (`LoadSave.LoadSaveSlotToCache`)
  e cada salvamento grava **cada** entrada em cache de volta (`SaveSystem.SaveDomainsAsync`). Entradas extras
  portanto acompanham saves, saves automáticos e saves rápidos sem interceptação; nomes desconhecidos são seguros
  (`LargeFilesStorage` cria um registro vazio sob demanda). Entradas são gravadas com
  `LoadSaveDomainsCache.GetCachedDomainFileWriteStream` + `SaveDomainFileSize`, fora de um salvamento.
- Fim de um salvamento: `SaveInProgressHandle.Dispose` (mantido durante todo o `SaveAsync`).

### <a id="remote-player-body-and-animation-2026-10-19"></a>Corpo e animação do jogador remoto (2026-10-19)

Observações (código descompilado, salvo quando marcado como "testado"):

- O corpo em terceira pessoa do herói é o prefab `VHeroController.maleHeroBodyTPP` /
  `femaleHeroBodyTPP` (masculino: `HeroMale_TPP`). Testado (listagem de componentes de uma instância inativa):
  componentes exclusivos do herói `HeroBodyData`, `ARHeroAnimancer`, `HeroAnimatorClipPlayer`,
  `VCTppSpineIK`, `VCTppHeroAnimationRigging`, `RigBuilder` (+ 2 `Rig`, 6 `MultiAimConstraint`),
  `VCHeroRaycaster`; partes visuais genéricas `KandraRig`, 3 `KandraRenderer`,
  `AnimationPostProcessing`, 14 `MagicaCapsuleCollider`, `CharacterDefaultClothes`,
  `RenderersMarkers`, `RagdollController`.
- `ARHeroAnimancer` está vinculado ao herói local: seu `OnAnimatorMove` move
  `Hero.Current.VHeroController`, e lê `Hero.Current` quando as animações carregam. Um segundo corpo
  não deve mantê-lo.
- `ARAssetReference` mantém um único handle de carregamento (`LoadAsset` duas vezes registra "already used"); o
  corpo do herói é carregado pela referência armazenada em `VHeroController`. Carregue outras cópias
  com `DeepCopy()`.
- Animação do herói: camadas (pernas, máquinas de estados de armas, substituições) reproduzem cada uma um `HeroStateType`, resolvido em
  clipes por recursos `ARHeroStateToAnimationMapping`: mapeamentos básicos e substituições que os itens
  aplicam ao equipar. Pernas em terceira pessoa são um misturador 2D alimentado por `Hero.RelativeVelocity` (y, x)
  (`TppMovementState`). Um corpo remoto pode reproduzir "estado por camada + parâmetro do misturador" pelos
  mesmos mapeamentos.
- Aparência é `BodyFeatures`, um elemento que qualquer proprietário `IWithBodyFeature` pode conter (herói, NPCs,
  `WorldHeroRenderer` do modo foto); ele se serializa sozinho e tem `CopyFrom`.
- O modo foto (`WorldHeroRenderer`) já exibe uma cópia do herói no mundo com características,
  roupas equipadas e poses de equipamento, mas está vinculado a `Hero.Current`.
- Movimento do bot: `PlayerInput.ProcessLateUpdate` define `MoveInput` a partir do Rewired a cada quadro; um
  pós-fixo que o substitui faz o herói andar pelo código de movimento do próprio jogo (testado).
- Área atual: `World.Services.TryGet<SceneService>()?.ActiveSceneRef?.Name`.

### <a id="steam-cloud-from-the-decompiled-code-2026-10-19"></a>Steam Cloud (a partir do código descompilado, 2026-10-19)

Observado no código (`Saving/Cloud/Services/*`, `Saving/Cloud/SteamCloudOrigin.cs`):
- O jogo escolhe `SteamCloudService` quando Steam Cloud está ativado para o usuário; caso contrário,
  `SteamNoCloudService` (`CloudService.CreateCloudService`); GOG tem seu próprio serviço. Todas as leituras
  e gravações de saves passam por ele. O jogo usa diretamente a API Steam (`ISteamRemoteStorage`
  pelo wrapper do Heathen): saves são `Saved/<file>.zip`, configurações são `Saved/PlayerPrefs.data`.
- Um salvamento é `BeginSave(slot ID)`, `SaveSlotFile` por entrada (armazenada como `<name>.data`),
  `EndSave(file name)`; com Steam Cloud, `EndSave` também envia à nuvem. `LoadSave.Save` pausa callbacks Steam
  (`App.canRunCallbacks`) e `SavingWorldMarker` termina com `EndSaveBatch` e
  `PrefMemory.Save`.
- Cada máquina mantém um registro dos arquivos sincronizados com os dois horários (`SteamCloudOrigin`, nas
  preferências *não sincronizadas*, `Unsynchronized/PlayerPrefs.data`, JSON simples). As gravações o atualizam
  em memória; `PrefMemory.Save` o armazena.
- Sincronização na inicialização (`InitCloud`), por arquivo: apenas local e sem registro → enviar; apenas na nuvem e sem
  registro → baixar; apenas na nuvem e conhecido pelo registro → **excluído da nuvem** (considerado
  excluído nesta máquina); apenas local e conhecido pelo registro → **excluído localmente** (a menos que
  a cópia local seja mais recente: conflito); presente nos dois e sem registro → diálogo de conflito; ambos
  alterados desde o registro → diálogo de conflito.

Deduções (para mods e ambientes de teste):
- Grave saves apenas pelo serviço de nuvem e termine com `PrefMemory.Save`; um arquivo adicionado ou
  removido sem o conhecimento do jogo será enviado, excluído ou causará conflito na próxima inicialização.
- Uma cópia de teste com Steam Cloud ativado precisa de sua própria pasta de dados, que nunca seja usada sem
  Steam Cloud (seu registro e seus arquivos precisam permanecer coerentes).
- Um save recebido pelo convidado contém referências a arquivos grandes do anfitrião
  (`SaveSlot.usedLargeFilesIndices`, arquivos `lf_*` por `LargeFilesStorage`); elas não significam nada
  no convidado. Excluir esse save executa `RemoveSaveSlotUsedFilesData`, que poderia remover um
  arquivo grande do próprio convidado com o mesmo índice. Não sabemos o que grava arquivos grandes; não havia nenhum no
  PC de teste (busca em 2026-10-19).

Desconhecido: se a Steam também executa Auto-Cloud para a pasta de saves deste jogo (as notas de NieR: Automata
observaram Auto-Cloud enviar a pasta de uma cópia de teste ao sair). As pastas das cópias de teste são
redirecionadas, portanto Auto-Cloud na pasta real não as veria. Um teste pontual com Steam Cloud
real (`tools/steam-cloud-test.ps1` no repositório do mod) está escrito, mas ainda não foi executado.

### <a id="derived-not-tested"></a>Deduções (não testadas)

- Itens de missão, chaves e textos legíveis em um save cooperativo pertencem à mesma história, portanto são mantidos.
  Caso extremo: um arquivo de convidado mais antigo que o mundo do anfitrião pode conter itens de missões já concluídas.
- O cooperativo deve usar a dificuldade do anfitrião; Survival e Challenge exigem tratamento especial.

### <a id="unknowns"></a>Incógnitas

- Transferência entre saves em pontos muito diferentes da história (os dois mundos de teste estão no prólogo).
- Se todos os itens equipados, habilidades e talentos sobrevivem à transferência.
- Quais efeitos da dificuldade são calculados onde, quando os inimigos passam a ser controlados pelo anfitrião.

### <a id="world-design-2026-10-19-owners-decisions"></a>Projeto do mundo (2026-10-19, decisões do proprietário)

- O jogador de cada jogo é seu único `Hero`; um jogador remoto é um substituto (um NPC que o
  mundo pode ver e combater, vestido com o corpo do jogador). Um segundo `Hero` real por convidado no
  anfitrião foi tentado e rejeitado: o herói é construído como jogador local (visualizações, câmera,
  ~20 partes em execução), portanto cada sistema precisava de outra exceção.
- O mundo do convidado é uma visualização do mundo do anfitrião, seguindo a regra de autoridade do anfitrião do manual
  (`playbook/methods.md` 5, de FNV): o anfitrião executa todos os scripts de história e mundo; uma
  ação do convidado é uma solicitação que o anfitrião executa; efeitos em um herói (itens, ouro, XP) vão para o
  jogador correto segundo uma tabela de regras e são aplicados ali com as chamadas do próprio jogo. Nenhuma etapa da história
  pode executar no convidado (a testar). Um primeiro rascunho deixava o jogo do convidado executar suas próprias
  ações, incluindo história; corrigido porque contradiz essa regra.
- Inicialmente, uma área para todo o grupo; incapacitação e reanimação; sem pausa no menu.
- Em aberto: o que é compartilhado e o que é individual (tabela preliminar: história, mundo, NPCs, tempo
  compartilhados; inventário, nível, atributos por jogador; reputação, crimes, mapa, divisão de recompensas
  propostos); como uma história executada para um convidado lê os atributos dele (o herói do anfitrião é
  `Hero.Current` ali).

## <a id="known-and-expected-bugs"></a>Erros conhecidos e esperados

O que os jogadores do TGCoop relatam, a causa quando seu código a mostra e o que nosso projeto precisa fazer.
"Não implementado" significa que a parte de sincronização em tempo real ainda não existe em nosso trabalho.

| Erro relatado | Causa no TGCoop 0.5.36 | Nosso projeto |
|---|---|---|
| Inimigos em posições diferentes para o convidado; "o monstro fica pulando de um lugar para outro enquanto persegue o anfitrião" | O convidado continua executando sua própria IA de inimigos; o anfitrião envia instantâneos a cada 0,12 s para até 32 NPCs num raio de 60 m; o convidado só corrige desvios acima de 1,2 m (2 m no corpo a corpo) com teletransportes interpolados. Duas IAs disputam cada inimigo. (observado no código) | Não implementado. Um cérebro por inimigo: IA executa apenas no anfitrião; NPCs do convidado têm IA desligada e interpolam posição, rotação e estado de animação do anfitrião. |
| Inimigos pareados incorretamente ou sem sincronização | Cada jogador carrega seu próprio save, portanto os IDs de NPCs diferem; pareados pelo prefixo do ID e pela distância (35 m). (observado no código) | Em grande parte resolvido pelo save único do anfitrião: mesmos IDs nos dois lados ao entrar. NPCs criados durante o jogo precisam de IDs atribuídos pelo anfitrião. |
| Convidado preso após um diálogo ou encontro (Conchur no asilo, lutas contra chefes) | Os gatilhos da história do convidado são acionados localmente. (suposição, não reproduzida) | Não implementado. Gatilhos de história e inícios de cenas executam apenas no anfitrião; o convidado recebe resultados e nunca entra sozinho em um estado bloqueante da história. |
| Sem animações em primeira pessoa | O jogo nunca calcula uma pose de corpo completo em primeira pessoa; TGCoop reconstrói uma. (da resposta do autor) | Não implementado. Enviar estado de movimento (velocidade, direção, ataque, bloqueio, conjuração), animar o jogador remoto no lado receptor com as animações normais de terceira pessoa. |
| Portão permanece fechado para o convidado; história dessincronizada | Apenas `StoryFlags.Set`, estado de missão e estado de objetivo são sincronizados em tempo real. (observado no código) | Save único do anfitrião e sincronização de cada gravação em `ContextualFacts`. |
| Caixa de diálogo do mod cobre as escolhas do jogo | Layout da interface. (relato de jogador) | Projetar a interface de diálogo do espectador para nunca sobrepor a local. |
| Apenas 2 jogadores | Fixado no código. | Arquivos de personagem já são individuais; começar com 2. |
| Inimigos perto do convidado, mas longe do anfitrião: um monstro persegue os dois, inimigos "quase impossíveis de matar" | O jogo deixa de simular entidades longe da câmera local; o anfitrião informava suas cópias congeladas como ociosas e sobrescrevia o dano do convidado. Corrigido na 0.5.36 deixando inimigos não observados sob autoridade do convidado. (resposta do autor) | Não implementado. A etapa 3 deve decidir o que o anfitrião faz com inimigos perto de um convidado e longe de si: mantê-los simulados no anfitrião ou transferir autoridade (etapa 3 do manual: "uma regra de transferência de autoridade"). Teste: convidado combate um inimigo longe do anfitrião; a vida diminui e permanece reduzida. |
| Saves do anfitrião recusados silenciosamente durante horas | O jogo se recusa a salvar em combate; um atacante fantasma manteve o anfitrião "em combate". Corrigido na 0.5.36. (resposta do autor) | Não implementado e um risco real: com saves apenas do anfitrião, seu save é a única cópia. Substitutos dos jogadores remotos jamais devem continuar como alvos de combate após uma luta; avisar os dois jogadores na tela quando um save for recusado. Teste: após uma luta envolvendo o substituto do convidado, o anfitrião consegue salvar. |
| Chefe morto apenas para um jogador | IDs diferem por máquina, pareados por posição. (resposta do autor) | Mesmos IDs nos dois lados pelo save único do anfitrião; mortes vêm do anfitrião (teste de saída da etapa 3). |
| Recompensas de missão (receitas, Druid Shrine) apenas para o jogador no diálogo; flags ausentes ao entrar na sessão de alguém menos avançado | Cada jogador mantém mundo e herói separados. (relato de jogador; causa suposta) | Parcialmente decidido: um mundo (o do anfitrião). Recompensas individuais seguem a tabela de compartilhamento de DESIGN.md (linhas em aberto). |
| Convidado preso correndo sem sair do lugar perto do teletransporte de Archspire | Desconhecida. | Desconhecido até chegarmos à área; acrescentar à rota de teste então. |
| Voz do diálogo não ouvida pelo espectador | Apenas texto e escolhas são enviados. (resposta do autor) | Não implementado (etapa de história). |
| Incompatibilidade de versão apenas no log | (resposta do autor, corrigido depois) | Nossa negociação verifica versões; se o convidado vê a recusa na tela: desconhecido, conferir. |

### <a id="seen-in-our-own-tests"></a>Observados em nossos próprios testes

- **A missão rastreada do convidado vaza para o mundo do anfitrião** (teste de entrada de 2026-10-18, transferência antiga): após
  entrar, o HUD do convidado rastreia "Set a bonfire", uma missão do próprio mundo do convidado. Não observado com
  o carregamento combinado: o convidado rastreia "The Great Escape", do mundo do anfitrião. ("Set a bonfire" acabou
  sendo a dica sobre pontos de talento, não uma missão.) O elemento
  `QuestTracker` do herói acompanha o personagem. A missão rastreada deve vir do mundo do
  anfitrião (ou ser limpa na importação).

- **Save recebido mantém o ID do slot do anfitrião** (2026-10-18): salvo como `Coop_QuickSave_6.zip`, mas
  seu ID nos metadados é o `QuickSave_6` do anfitrião. Na varredura da tela de título do convidado, dois slots reivindicam esse ID;
  o jogo renomeia o que carregar por último (ordem alfabética dos arquivos), e `SaveSlot.IsQuickSave`
  é `ID.Contains("QuickSave")`, portanto um slot cooperativo pode se passar pelo save rápido do convidado. Slots cooperativos
  precisam de IDs próprios. Ainda em aberto (2026-10-19): desde a adoção dos slots cooperativos, o anfitrião sempre envia um
  `Slot_N`, portanto o caso do save rápido desapareceu, mas o slot recebido ainda mantém o `Slot_N`
  do anfitrião e colide com o próprio slot do convidado de mesmo número. Observado na varredura da tela de título do convidado:
  `Slot_38 file=Slot_31`, `Slot_35 file=QuickSave_6` (uma sobra do projeto antigo). O mod
  encontra slots pelo nome do arquivo e não é afetado; um teste que carregava por ID carregou o slot errado
  após reiniciar. **Corrigido em 2026-10-19**: ao carregar os metadados do slot recebido, o jogo
  já lhe atribui um novo ID em caso de colisão (`SaveSlot.EnsureIdIsValid`, apenas em memória).
  Agora o convidado lê os metadados dos bytes recebidos e grava o slot inteiro pelo
  serviço de nuvem, como o salvamento do próprio jogo, com metadados recém-serializados contendo o
  novo ID (veja "Steam Cloud" abaixo). Teste: o convidado possui um slot com o ID do anfitrião; após
  o recebimento, `MetaData.data` no zip deve conter o novo ID do convidado (teste gêmeo: os
  metadados do anfitrião são armazenados sem alteração, e a verificação falha). A suíte completa passa.
  - Descoberta sobre o jogo no caminho: `SaveSlot.ApplyChanges` (chamado ao renomear um slot) nunca
    grava em um slot no PC. `LoadSave.SaveMetadataDomainSynchronous` carrega
    `Saved/<file>.data` pelo serviço de nuvem, mas os slots são `Saved/<file>.zip`
    (o código descompilado de `SteamCloudService` e `SteamNoCloudService` acrescenta `.data` em ambos), portanto não encontra
    nada e retorna. O próximo salvamento completo grava os metadados de qualquer maneira. Uma primeira correção alterava
    `MetaData.data` diretamente no zip (funcionava, mas sem informar Steam Cloud); substituída.
  - Substituído no mesmo dia por saves apenas no anfitrião: o convidado não armazena mais o mundo.

- **Saves apenas no anfitrião** (2026-10-19, decisão do proprietário, implementado): o save cooperativo do anfitrião é a única
  cópia permanente. O convidado mantém o mundo recebido em memória: um slot é criado a partir dos
  metadados nos bytes recebidos, e um prefixo Harmony em `ZipArchiveUtils.LoadArchive` (onde
  os serviços de nuvem Steam abrem o zip de um slot) o fornece da memória, portanto o carregamento do próprio jogo executa
  sem alteração. O jogo do convidado não pode salvar: o modelo `SaveBlocker` do próprio jogo (usado em duelos,
  lutas contra chefes) impede saves do jogador, rápidos e automáticos, mas não o cache de domínios nas trocas de área.
  "Salvar meu personagem" do convidado envia seu personagem; o anfitrião salva imediatamente apenas se
  pudesse salvar manualmente (`LoadSave.CanPlayerSave`); caso contrário, no próximo salvamento. Testado: a
  pasta de saves do convidado é idêntica byte a byte à sua base após uma sessão; save rápido recusado.
  - Classe de erro eliminada: entrar novamente costumava descartar silenciosamente o progresso solo do convidado em seu
    slot `Coop_`. Eliminado, pois não há slot do convidado.
  - Descoberta sobre o jogo: o próprio `LoadSave.Save` ignora bloqueadores de salvamento (apenas as verificações `Can*Save` e
    os menus os consideram); `SavePostpone` é a única verificação dentro de `Save`.
  - Descoberta sobre o jogo: salvar exige `Hero.Grounded`, que é falso durante a natação: o sistema de movimento
    zera a velocidade vertical na água, o controlador de personagem não informa chão,
    e o temporizador de 0,5 s desde o último contato com o chão expira (`VHeroController.UpdateGroundTouchedTimeout`),
    embora a verificação esférica do chão ainda detecte contato. As caminhadas dos bots de teste na praia do prólogo
    às vezes terminam na água, portanto um teste que exige salvar no anfitrião deve colocá-lo em terra antes.
  - Lacunas: o serviço de nuvem GOG abre slots de outra forma (um mundo recebido não carregaria);
    a tecla de save rápido do convidado ainda não faz nada (deveria ser "salvar meu personagem"); um salvamento do
    anfitrião ainda não coleta os personagens atuais dos convidados.

- **Descobertas sobre o projeto do mundo** (2026-10-19, a partir do jogo descompilado; projeto em
  DESIGN.md do mod):
  - Um herói: `Hero.Current` é uma propriedade estática definida pelo próprio modelo do herói, lida 1.190
    vezes em 514 arquivos. A detecção de inimigos (`Perception`) só consulta essa propriedade; o combate usa o
    alvo genérico `ICharacter`, que NPCs usam uns contra os outros.
  - Toda interação entra por `AbstractHeroAction.StartInteraction(Hero, interactable)`,
    toda história por `Story.StartStory` e `StoryStep.Execute` (~210 tipos de etapas em execução),
    toda flag de história por `ContextualFacts.Set/Change/Remove`. Ações misturam efeitos em um
    método (`PickItemAction`: cria o item, registra o furto, preenche o
    inventário do ator, pode iniciar um diálogo, remove o objeto coletável).
  - Gatilhos da história são acionados pelo contato físico com o controlador do herói local (`HeroTrigger`).
  - IDs são contadores por tipo salvos com o mundo (`IdStorage`): idênticos em dois jogos a partir
    de um save, divergentes assim que um deles cria algo.
  - Áreas são domínios de save separados (`Domain.Scene`), carregados um de cada vez.
  - **Prova, rejeitada: um segundo herói no anfitrião, apenas com dados, para um convidado.** Aplicar um patch ao
    getter `Hero.Current` no carregamento do plugin alcança o código do jogo (~1.100 leituras/s); aplicado
    depois, o código já compilado não o utiliza (incorporado por inlining). Mas um herói que não seja o jogador local
    precisa de exceções em toda parte: visualizações (controlador, câmera, HUD, teclas, mira), ~20
    partes em execução que pressupõem corpo e câmera, o wyrd stalker, as consultas do mundo por "único herói"
    (`World.Only<HeroCombat>` e ~45 outras), ossos do corpo. Com seis dessas exceções, ele
    carregou e o anfitrião executou uma coleta para ele (item no inventário do convidado), mas reagiu
    de modo diferente de um herói jogado, e o tutorial da coleta apareceu na tela do anfitrião.
    Conclusão: o herói é construído como jogador local; jogadores remotos funcionam melhor como substitutos
    (a abordagem do Skyrim Together, how-coop-mods-work.md 2.1 do manual).
  - Possível lição para o manual (fase 8, com aprovação do proprietário): uma prova precisa de pergunta,
    resultado sim/não, limite de tempo e regra de parada escritos de antemão; uma falha dentro de uma prova é
    evidência, não um erro a corrigir. Sem isso, esta prova virou uma sequência de patches.
  - Lição sobre o ambiente de teste: Harmony compila patches apenas dentro do jogo; um patch que falhou ali
    fez o carregamento de um save falhar como "corrompido". Agora o inicializador interrompe uma cópia cujos plugins relatam
    um patch com falha antes de qualquer carregamento.

- **Bonecos são substitutos básicos** (2026-10-19, etapa 1 de presença, intencional por enquanto): o outro
  jogador aparece com o corpo masculino padrão do herói, careca, de roupa íntima, na pose T do esqueleto, deslizando.
  Personagens femininas também aparecem como masculinos. Próximas etapas: animação, depois aparência e
  equipamento. Bonecos não têm colisão e inimigos não conseguem vê-los nem atingi-los.

### <a id="expected-problems-derived-not-seen-yet"></a>Problemas esperados (deduzidos, ainda não observados)

- **Travamento ou saída do convidado sem salvar perde progresso**: o personagem do convidado chega ao save
  cooperativo do anfitrião apenas quando o convidado salva. Planejado com sincronização de personagem em tempo real: envios regulares e
  orientados por eventos, negociação na saída normal e save automático do anfitrião quando um convidado sai.
  Um travamento do anfitrião perde personagens enviados que ele ainda não salvou.

- **Seleção de alvos inimigos com dois jogadores**: a IA inimiga conhece apenas `Hero.Current`; no anfitrião, o convidado é um boneco. O boneco deve se tornar um alvo válido (atacável, agressividade, linha de visão), senão inimigos ignorarão o convidado.
- **Dano e dificuldade**: a dificuldade multiplica dano causado e recebido, uso de vigor e mana (`Difficulty.DamageDealt/DamageReceived/...`, aplicado a NPCs por `NpcDifficultyStatModifier`). Golpes do convidado são resolvidos no anfitrião com a dificuldade do anfitrião; dano ao convidado deve usar a armadura e os atributos dele. Decidir se os inimigos escalam com o número de jogadores.
- **Dificuldades Survival e Challenge**: restrições de salvamento e um elemento de herói bloqueado; inicialmente bloquear no cooperativo.
- **IDs de jogador autodeclarados**: personagens no save cooperativo são indexados pelo Steam ID que o convidado
  envia em sua mensagem inicial, e o anfitrião confia nele; um convidado poderia reivindicar o personagem de outro jogador.
  Com transporte Steam, usar o Steam ID do remetente fornecido pela rede Steam.
- **Um recém-chegado sempre joga com uma cópia do herói do anfitrião**, incluindo equipamento. Provisório: um
  convidado de primeira viagem deveria criar seu próprio personagem (projeto em aberto: entrar em uma história muito
  avançada, níveis, equilíbrio). Trazer seu próprio personagem de um save solo é, no máximo, uma opção
  posterior (equilíbrio, abuso). O bot de teste consegue (`join --bring`).
- **Itens de missão de arquivos de personagem desatualizados**: um arquivo de convidado mais antigo que o mundo do anfitrião pode conter itens de missões concluídas.
- **Coletas duplicadas**: os dois jogadores saqueando o mesmo recipiente ou objeto derrubado; o anfitrião deve arbitrar.
- **Tempo, clima, sono, viagem rápida, noites de wyrdness**: efeitos em todo o mundo acionados por um jogador; autoridade do anfitrião necessária.
- **Menus pausam o jogo** no modo de um jogador; no cooperativo não devem pausar o mundo compartilhado.
- **Morte e telas de carregamento**: um jogador carregando uma nova área ou morrendo não deve congelar o outro.

## <a id="co-op-milestones"></a>Marcos do cooperativo

| Data | Marco | Teste | Resultado |
|---|---|---|---|
| 2026-10-19 | Autoteste do avaliador (automated-qa.md do manual, "Teste o avaliador, não apenas o teste"): saídas de sessão conhecidas como boas e ruins, produzidas pelas próprias funções da biblioteca de testes, passam primeiro pelo avaliador real em cada execução da suíte | 9 casos; contra o avaliador antigo, falhou exatamente nas 2 lacunas previstas (uma execução, ou execução gêmea, com verificações ausentes contava como aprovação) | Corrigido; Full: SUITE: PASS em 614 s, cada execução realizou todas as suas verificações (principal 40/40, rede ruim 31/31, execuções gêmeas falharam exatamente em suas 17 e 1 verificações listadas). |
| 2026-10-19 | Lacunas de teste do manual preenchidas: rede ruim (relay, 100 ms em cada sentido, jitter de 20 ms, perda de 5%) e saída (convidado sai pela saída do jogo, anfitrião o vê sair, anfitrião sai, sem relatório de travamento) | `run-suite.ps1 -Full`: nova execução de rede ruim; saída encerra todas as execuções; gêmeos "convidado trava" e "relay limpo" | Em uma conexão real de 108 ms / 5,1% de perda, todas as verificações dentro da sessão passam; o anfitrião percebeu a saída do convidado por tempo limite. SUITE: PASS em 457 s (3 execuções; execução gêmea falhou exatamente em suas 12 verificações listadas). |
| 2026-10-19 | Suíte de testes reestruturada: uma sessão compartilhada executa as verificações de todos os recursos; apenas salvar/recarregar e persistência reiniciam jogos; gêmeos com opções independentes compartilham uma execução; níveis `-Quick` / `-Full`; pastas de saves restauradas para uma base fixada a cada execução | `tools/run-suite.ps1 -Quick` e `-Full`, mesmas verificações e expectativas dos gêmeos de antes (duplicatas combinadas) | Quick: SUITE: PASS em 95 s (22 verificações). Full: SUITE: PASS em 327 s (principal 34/34; execução gêmea falhou exatamente em suas 10 verificações listadas), antes eram 659 s. |
| 2026-10-19 | Enxergar um ao outro, etapa 1 (etapa 2 do manual): slots na lista de participantes, estado do jogador a 20 Hz (não confiável), anfitrião retransmite; cada jogador remoto é o corpo em terceira pessoa do próprio jogo sem os componentes exclusivos do herói, interpolado entre instantâneos com atraso de 100 ms; nos dois sentidos | `tools/presence-test.ps1` + gêmeo (convidado não envia nada: falha exatamente nas 4 verificações de boneco do lado do anfitrião), em `run-suite.ps1` | SUITE: PASS em 659 s (6 casos); convidado andou 16,6 m, boneco do anfitrião terminou a 0,08 m de distância. Por enquanto, o boneco é um corpo padrão em pose T. |
| 2026-10-19 | Slots de save cooperativo: hospedar transforma o mundo em seu próprio slot cooperativo; ao entrar, o anfitrião o salva e envia o mundo atual; personagens dos convidados são armazenados no save do anfitrião (como entradas extras que o cache de domínios do jogo mantém em cada salvamento) e retornam na próxima entrada | `tools/run-suite.ps1`: entrada, persistência (entrar, alterar, salvar, ambos saírem, entrar novamente), cada um com um gêmeo mutante | SUITE: PASS em 470 s (4 casos); convidado manteve 777 de ouro entre sessões, anfitrião 129. |
| 2026-10-18 | Carregamento combinado: personagem do convidado incorporado ao save do anfitrião dentro do carregamento do domínio Gameplay do próprio jogo (herói do anfitrião descartado nas definições, modelos do convidado com novos IDs de itens inseridos em seu lugar, um RestoreWorld); save cooperativo feito no convidado recarrega sem erros e sem o patch anterior da ordem de salvamento | `tools/run-suite.ps1`: entrada + recarregamento (15 verificações, incluindo fim real da tela de carregamento) e gêmeo | SUITE: PASS em 270 s; HUD do convidado rastreia a missão do mundo do anfitrião. |
| 2026-10-18 | Convidado entra no anfitrião por UDP local (LiteNetLib), recebe o save do anfitrião (dividido em blocos, SHA-256 verificado), carrega-o com seu próprio personagem ao lado do anfitrião, ambos estáveis por 30 s | `tools/run-suite.ps1`: teste de entrada + gêmeo mutante (entrada sem personagem deve falhar exatamente nas 3 verificações de personagem), duas instalações isoladas em um PC | SUITE: PASS em 191 s, 10/10 verificações por caso. |

## <a id="test-setup-lessons"></a>Lições sobre o ambiente de teste

- **A simulação de rede do LiteNetLib não faz nada na compilação NuGet.** `SimulateLatency` /
  `SimulatePacketLoss` só funcionam em compilações DEBUG ou `SIMULATE_NETWORK`; na DLL de lançamento
  2.1.4, os métodos estão vazios (`[Conditional]`, `Base.cs` descompilado). Use um relay UDP entre
  as cópias (o nosso: relay 127.0.0.1 com latência, jitter e perda, contando o que
  realmente fez) e verifique suas contagens, não as configurações.
- **A saída do jogo encerra seu próprio processo.** `MenuUI.ExitGame` → `TitleScreenUI.Exit` salva
  preferências, encerra a análise de uso e chama `WindowsKernelHelpers.KillCurrentProcess()`; nenhum callback de saída
  ou destruição do Unity executa, portanto um mod não pode depender deles. Nos testes, o jogo fecha cerca de 3 s
  após o comando.
- **Relatórios de travamento**: um travamento Unity grava
  `%LOCALAPPDATA%\Temp\Questline\Fall of Avalon\Crashes\Crash_<UTC time>\crash.dmp` (compartilhado pelo
  jogo real e todas as cópias de teste), sem diálogo e sem deixar processo em execução. Testes verificam novas
  pastas desde o início da execução.

- **Inicializações do jogo dominam o tempo de teste** (cerca de 45 s por início de sessão; verificações levam segundos).
  Execute as verificações de vários recursos em uma sessão compartilhada e reinicie jogos apenas para testes que exigem
  uma saída (salvar e recarregar, entrar novamente). Gêmeos cujas opções não afetam as verificações uns dos outros podem
  compartilhar uma execução; ela deve falhar exatamente na união de suas verificações.
- **Identifique slots de save pelo nome do arquivo nos testes, nunca pelo ID do slot**: o jogo reatribui IDs na
  inicialização quando dois slots reivindicam um, portanto um ID pode indicar outro slot após reiniciar. E
  restaure as pastas de saves de teste para uma base fixada no começo de cada execução; caso contrário, slots de execuções
  anteriores se acumulam e causam essas colisões.
- Nomes de variáveis no Windows PowerShell 5.1 não diferenciam maiúsculas e minúsculas: um parâmetro `[string]$Restarts` e uma
  lista `$restarts` são uma só variável, e a restrição de tipo transforma a lista em uma string.

- A cópia de teste compartilha `%USERPROFILE%\AppData\LocalLow\Questline\Fall of Avalon` com a instalação
  real, e o jogo reempacota saves na primeira inicialização desta compilação. Redirecione a pasta de dados
  (campo de suporte de `CloudService`) e force `SteamNoCloudService` antes de iniciar uma cópia de teste.
- O jogo também mantém dados temporários de save em `Application.temporaryCachePath` do Unity
  (`%LOCALAPPDATA%\Temp\Questline\Fall of Avalon`): `CachedDomains\` (slot descompactado durante
  o carregamento) e `SaveFiles.zip` (slot sendo gravado). É compartilhado pelo jogo real e por todas as cópias
  de teste; duas cópias carregando ao mesmo tempo corromperam um save. Redirecione `IOUtil.TemporaryCachePath`,
  `ZipArchiveUtils.ZipPath` e o campo de suporte de `LoadSaveDomainsCache.CachedDomainsDirectoryPath`
  por instância (todos estáticos, calculados uma vez).
- Duas cópias executam de uma instalação (sem bloqueio de instância única no código), cada qual com sua própria pasta
  de dados escolhida por uma variável de ambiente lida pelo plugin de isolamento.
- **O isolamento deve bloquear em caso de falha.** Duas cópias iniciadas simultaneamente de uma instalação sofreram uma
  violação de compartilhamento em `BepInEx\config\BepInEx.cfg`; o pré-carregador BepInEx lançou uma exceção (gravada em
  `preloader_<timestamp>.log` na pasta do jogo), Doorstop continuou, e essa cópia executou
  **sem mods**: `SteamCloudService` e a pasta real de saves, exibindo um diálogo de conflito Steam Cloud.
  Saves reais não foram alterados (horários conferidos), mas nada impediu isso. Correções:
  uma instalação por instância (arquivos do jogo com hardlinks, pasta BepInEx própria, pasta de plugins como
  junção para a da primeira instalação), cópias iniciadas uma após a outra e um intertravamento de inicialização
  que encerra uma cópia, a menos que seu plugin de isolamento informe a pasta de dados esperada em até 6 s
  (o jogo inicializa seu serviço de nuvem cerca de 8 s após iniciar). O intertravamento tem seu próprio
  teste negativo.
- Um intertravamento de inicialização precisa de sinais de falha, não de um tempo estimado: o primeiro início após
  recompilar um plugin demorou mais de 6 s e foi encerrado. Encerre por sinais concretos (log BepInEx não
  regravado em 5 s, arquivo de travamento `preloader_*.log`, linha de log do jogo "Initializing Cloud with
  SteamCloudService"), permita até 30 s para a confirmação e espere até todos os processos da
  instalação (jogo e `UnityCrashHandler64`) terem saído.
- Nunca armazene um caminho específico de instalação em um arquivo de configuração BepInEx: uma configuração copiada apontou a
  segunda instalação para os saves da primeira. Derive caminhos de `Paths.GameRootPath`.
- `NetDataWriter.PutBytesWithLength` / `PutArray` do LiteNetLib 2.1.4 armazenam o tamanho como
  `ushort` e truncam silenciosamente arrays acima de 65.535 bytes. Um save de 104 KB chegou como zip quebrado
  sem nenhum erro em lugar algum. Grave blobs com um tamanho `int` por conta própria e envie um SHA-256 junto de
  qualquer coisa que o receptor grave em disco.
- "Na jogabilidade" deve significar que a tela de carregamento desapareceu (`LoadingScreenUI.IsLoading`); o modelo do herói
  existe durante o carregamento, portanto verificações e capturas de tela baseadas nele passam cedo demais.
- Uma janela de teste em foco lê teclado e mouse: uma captura do anfitrião mostrou o inventário com um
  diálogo "Save outfit" aberto que nenhum bot abriu. Cópias de teste devem ignorar entrada do jogador.
- Cópias de teste são forçadas para uma janela 1280x720, 30 FPS, `runInBackground`, por um patch logo
  após `ScreenResolution.Refresh` (onde o jogo aplica suas configurações de exibição).
- Bloqueie `AutoBugReporting.SendAutoReport` nas cópias de teste: carregamentos experimentais quebrados enviariam
  relatórios com saves anexados aos desenvolvedores.
- Automatizar a tela de título: espere `TitleScreenUI.SpawnTitleScreenUI`; carregar antes
  deixa o menu de título desenhado sobre a jogabilidade pelo restante da sessão. "Press any button" pode ser
  pulado definindo `TitleScreenUI.s_shownFocusPopup`.
- Scripts de teste Windows PowerShell 5.1 iniciados em um ambiente PowerShell 7 (aqui: um shell de
  agente) herdam seu `PSModulePath`, carregam os módulos errados e perdem comandos nativos
  (`Get-FileHash`); todas as execuções abortaram. Limpe `PSModulePath` antes de iniciar o 5.1.


