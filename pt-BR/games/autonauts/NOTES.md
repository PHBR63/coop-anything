# <a id="autonauts-co-op-working-notes"></a>Autonauts cooperativo: notas de trabalho

## <a id="identity-observed-2026-10-20"></a>Identidade (observada em 2026-10-20)
- Loja: Steam, aplicativo 979120 (SteamManager.cs). Compilação Steam: desconhecida (manifesto não lido).
- Motor: Unity 2018.4.35f1 (dbb5675dce2d), Mono (MonoBleedingEdge), Windows x64.
- Arquivos datados 2024-10-09 na instalação (usuário acreditava que última atualização fosse 2022).
- SHA-256 Autonauts.exe: ec9ac079a210f6cba1c927f7502ba38ff3499c2fc803178cdc574a2b74ca0c70
- SHA-256 UnityPlayer.dll: e41d7d32228126290ce2bc36ccd16c6fc91d659285e11f2a6b411be6bf092adf
- SHA-256 Assembly-CSharp.dll: 3ecafdbf831a92e9c37bdb25def7a044eaeaed40c9997b96336c361c7ca4155f

## <a id="prior-work-searched-2026-10-20"></a>Trabalhos anteriores (pesquisados em 2026-10-20)
- Sem multiplayer oficial. Desenvolvedor em 2019/20 disse que multiplayer demoraria: https://playco-opgame.com/autonauts/
- Sem mod cooperativo encontrado, só pedidos: https://itch.io/t/175669/pls-add-a-multiplayer-mode https://itch.io/t/161660/multiplayer https://steamcommunity.com/app/979120/discussions/0/1639801448924410169
- Mods Lua (MoonSharp) oficiais desde Industrial: https://videogameschronicle.com/news/autonauts-adds-mod-support-with-free-industrial-expansion . Não serve para rede (isolado, sem interceptação de métodos).
- coop-anything: sem entrada ou pasta na main (2026-10-21). Issues/PRs não pesquisadas (API indisponível). Nexus e Discord não verificados.

## <a id="tools-pinned"></a>Ferramentas (versões fixadas)
- ZIP ILSpy 9.1 (ICSharpCode.Decompiler.dll usada por CLI pequena): sha256 1e925a4ce4c79d68139a486da66c682e2191e51215188816f613866c7276fc55
- BepInEx 5.4.23.5 Windows x64: sha256 82f9878551030f54657792c0740d9d51a09500eeae1fba21106b0c441e6732c4 (não comparado com hash publicado).
- Plugin compilado com Roslyn csc do SDK .NET 8 contra mscorlib do jogo (-nostdlib). NuGet bloqueado no ambiente.

## <a id="observed"></a>Observado
- Jogo inicia com Wine 9.0 + Xvfb (D3D11 por wined3d padrão) e BepInEx; Awake do plugin executa; mundo do menu gera ("ready" em Player.log). -force-glcore falha (sem shaders GL na compilação).
- Arquitetura (salvar/carregar, identificadores, pontos de entrada):
  - SaveJSON.Capture monta JSON completo em memória; LoadJSON.LoadFromDisk define m_FinalString; prefixo permite carregar da memória.
  - Identificadores: contador global ObjectTypeList; GetObjectFromUniqueID; criação CreateObjectFromIdentifier; destruição BaseClass.StopUsing.
  - Entrada: FarmerPlayer.GoToAndAction, Farmer.SendAction, FarmerAction.SendAction; ActionInfo leva UIDs.
  - Células: TileManager.SetTileType é ponto único.
  - 195 chamadas UnityEngine.Random, passo variável: lockstep inviável.
  - Steamworks.NET incluído com pareamento e rede (não usados pelo jogo).

## <a id="inferred"></a>Inferido
- Autoridade do host com captura completa e deltas é modelo adequado.

## <a id="unknown"></a>Desconhecidos
- Tamanho/tempo de captura em salvamentos avançados. Se Savable.Load pode aplicar a objeto ativo.

## <a id="build-log-2026-10-20"></a>Registro de implementação (2026-10-20)
- AutonautsCoop 0.1.0 (BepInEx 5, Harmony), espelho com autoridade do host, TCP.
- Entrada: host SaveJSON.Capture, gzip, cliente; cliente usa carregador nativo com MyFile.Exists/Load alterados para servir string da memória (nome __coop_session__). Salvamentos/autosalvamentos cliente bloqueados.
- Cliente lançou exceção em OffworldMissionsManager.GetMissionObjectType (lista vazia) num mundo novo; corrigido pulando CheckDailyMission no cliente.
- Deltas: host inspeciona salváveis a 5 Hz, envia JSON de alterados, UIDs removidos, transformações Farmers/Animals/Vehicles a 10 Hz, eventos SetTileType e Plot.SetVisible. Resumo antientropia (uid,hash) a cada 10 s; cliente pede divergentes e remove extras.
- Armadilhas:
  1. Savable.Load em execução registra UIDs novamente por ChangeActionable; em objeto registrado aloca NOVO UID. Antes, RemoveActionable.
  2. Criar objetos com filhos (FarmerCarry, ninho de abelhas) quebra registro sem ObjectTypeList.m_Loading = true (campo estático; NÃO chamar SetLoading, apaga registro). Indicador faz CreateObjectFromSaveName + Load agir como carregador.
  3. Filhos salvos dentro do pai E como salváveis superiores (BeesNest). Excluir da sincronização superior qualquer UID aninhado em JSON de outro objeto, nos dois lados.
  4. Campos voláteis "STT" (temporizador), "S"/"ST" em animais mudam por quadro ou reiniciam em Load. Excluídos de hashes/verificação.
  5. CollectionManager.GetPlayers() contém cada jogador por coleção (3 vezes). GetPlayers()[0] usado para entrada; cada máquina ordena seu jogador no índice 0.
  6. UIDs de Plot são locais; alvos de entrada desse tipo enviados como parcela naquela célula.
  7. Novo jogo de campanha: após introdução, jogador fica no canto (83,95 em mapa inicial 84x96); participantes criados em célula livre dentro dos limites.
- QA (test/run.sh): duas cópias Wine 9 + Xvfb, prefixos separados, TCP localhost, bots COOP_TEST=host|client pelo caminho real FarmerPlayer.GoToAndAction. Cerimônias avançadas por OnAcceptClicked. Últimas execuções: 15/15, 15/15, 15/15 (antes das correções antientropia/aninhamento, checksum falhava uma em três).

## <a id="unknown--not-done"></a>Desconhecidos / não feitos
- Construção do participante (edição) e ensino de bots: não encaminhados.
- Transporte Steam não criado. Internet não testada. Windows real, sem Wine, não testado por mim.
- Desempenho avançado: varredura host 34 ms num mundo novo com 1,3 mil objetos no Wine (substituir varredura total por rastreamento de alterações antes de bases grandes).

## <a id="020-steam-transport-2026-10-20"></a>0.2.0 transporte Steam (2026-10-20)
- Steamworks.NET 15.0.1 / SDK 1.51 (Plugins/Steamworks.NET.txt), ISteamNetworkingMessages v002, Matchmaking v009. Reutilizado com aplicativo 979120.
- Bug dessa Steamworks.NET: SteamNetworkingMessage_t.Release() passa m_pfnRelease em vez de ponteiro da mensagem. Chamar SteamAPI_SteamNetworkingMessage_t_Release(msgPtr) por DllImport próprio.
- Limite do par 60 s, não 20: carregar mundo congela thread Unity, parando sinais de atividade dos dois.
- Sala/convite Steam real não testados (2 PCs e contas proprietárias). Enquadramento/pares por substituto UDP: 22/22.

## <a id="030-joiner-building-2026-10-20"></a>0.3.0 construção pelo participante (2026-10-20)
- Interceptações (prefixos cliente enviados ao host): BuildingManager.AddBuilding (8 argumentos), DestroyBuilding, MoveBuildings, GameStateEdit.ConvertDragModels (arraste constrói diretamente, sem AddBuilding). Building.PlayerDeleted virtual (Converter, ConverterFoundation substituem): alterar os três. GameStateEdit.UndoAction é enum privado: interceptar AddUndoAction/Undo por nome.
- Building.StopUsing NÃO remove de MapManager; no cliente precisa MapManager.RemoveBuilding + BuildingManager.RefreshBuilding. Load local de prédio movido deixa mapa obsoleto: recriar se TX/TY/Rotation mudam.
- Prévias de edição (cursor, modelos arrastados) têm SetIsSavable(false), mas usam UIDs. Contador cliente passa a 1e9 após entrada; locais nunca colidem com host. Objeto *salvável* com UID local é efeito colateral da simulação (árvore derrubada soltando madeira/sementes no cliente), eliminado a cada 0,5 s.
- Cliques durante ação não abortável são ignorados por FarmerPlayer.GoToAndAction. Host guarda último clique do participante por 3 s.
- Causa de teste intermitente: célula de descarte às vezes tinha árvore/grama; descarte não acontecia. Busca de célula livre agora exige ausência de objetos e água.
- QA: TCP 20/20 (duas vezes após corrigir), formato UDP 22/22.

## <a id="040-joiner-bot-teaching-2026-10-20"></a>0.4.0 ensino de bots pelo participante (2026-10-20)
- Ensino registra em FarmerPlayer.m_TeachingActions (FarmerPlayer.SendAction e SendActionTeaching); GameStateTeachWorker2.UpdateTeachInstructions converte players[0].m_TeachingActions em instruções; TeachWorkerScriptEdit.OnClickGo confirma por Worker.NewHighScriptTaught(list).
- Projeto: participante usa interface no bot espelhado. Encaminhados: Farmer.StartLearning, Worker.RequestStopLearning, GameStateTeachWorker2.SetTarget/Close (host SetIsTeaching no FarmerPlayer participante), Worker.NewHighScriptTaught (JSON HighInstructionList.Save), StopAllScripts/TogglePauseScript/StartStep, FarmerPlayer.UseWhistle. Host transmite novas m_TeachingActions de volta; participante acrescenta à lista própria.
- FarmerPlayer participante pode ser reconstruído durante ensino (alterações de carga), reiniciando m_Teaching e lista. Manter lista persistente e religar após reconstruir.
- Não reconstruir bot aberto no editor (interface mantém referência): congelar em TeachWorker/SelectWorker; ao fechar, pedir reenvio. Em visão normal, reselecionar nova cópia de bot selecionado reconstruído.
- Alvos Plot nas instruções têm UIDs locais: remapear ao Plot do host na célula.
- Armadilha: graveto ensinado termina na mão do professor; reprodução do bot não encontra nada. Verificar script recebido/iniciado, não bot carregando graveto.
- QA: TCP 27/27 (duas vezes), formato UDP 29/29.

## <a id="050-locks-rename-inventory-2026-10-20"></a>0.5.0 travas, nomes e inventário (2026-10-20)
- Travas de edição: máquinas relatam bot aberto em TeachWorkerScriptEdit com estado TeachWorker/SelectWorker; host guarda uid → (nome, chave do responsável), transmite. OnClickTeach/OnClickGo recusam bot travado; host recusa operações de ensino/script de outros. Etiquetas por IMGUI + Camera.WorldToScreenPoint.
- Renomear: Worker.SetWorkerName encaminhado.
- Inventário: transferências em InventoryBar.DragEnd/OnClick (FarmerCarry.RemoveObject/AddCarry/StowObjects, FarmerInventory/FarmerUpgrades.ReleaseObject/AttemptAdd, FarmerClothes.Add/Remove, Wardrobe/Aquarium). Enviar descritores (UID do portador, tipo/índice da vaga, UID do objeto); host reproduz. Só permite tocar jogador próprio, bots, guarda-roupas, aquários.
- Teclas de inventário usam FarmerPlayer.SendAction diretamente de GameStateBase.UpdateInventoryKeys (sem GoToAndAction). Marcar chamada e encaminhar só ações permitidas.
- HudManager.StartGame vincula barra a players[0] ao carregar, jogador host no participante. Revincular ao próprio; revincular InventoryBar com objeto reconstruído (acompanhar em SetObject).
- Bug: FarmerPlayer.PostCreate instancia FarmerPlayerStatusIndicator sob HudManager.m_IndicatorsRootTransform; telas de inventário ocultam raiz, Awake não executou, SetState lança NRE, jogador participante desaparecia silenciosamente. Ativar raiz e ancestrais inativos durante criação.
- QA: TCP 35/35, formato UDP 37/37.

## <a id="060-menus-world-state-leaving-animations-2026-10-20"></a>0.6.0 menus, estado do mundo, saída, animações (2026-10-20)
- Interagir abre menu por GameStateManager.StartSelectBuilding/StartRenameSign, chamado por SendAction(Engaged) na máquina que interage. Interação do participante executa no host e abria menu na tela errada. Prefixo host redireciona ao par; participante define m_Engager do espelho ao seu jogador e abre. Operações: receita = m_Engager.SendAction(SetValue ResultIndex), fechar = DisengageObject (encaminhado e local), chamadas diretas (Converter/ConverterFoundation.CancelBuild, ResearchStation.CancelResearch/SetCurrentResearchQuest, AnimalStation.StopAll, Storage.ToggleLock, Building.BeginUpgrade, RenameSign.EndEdit para JSON da placa). Escape só remove estado: enviar fechamento para host desengajar.
- Estado: QuestManager (Load = Reset + recarga), ResourceManager, DayNightManager, WorkerScriptManager (Load acrescenta; limpar m_Scripts/m_Folders/m_Stored), WorkerGroupManager (acrescenta; limpar m_Groups), OffworldMissionsManager, enviados ao mudar JSON Save (1 s).
- Desbloqueios individuais: Badge.SetCompleted chama QuestManager.UnlockObject das medalhas locais (não no mundo salvo). Participantes recebem m_ObjectsLocked do host explicitamente, reaplicado após QuestManager.Load.
- QuestManager.CompleteAll lança NRE nesta compilação (não usar em preparação de testes).
- Caminhada procedural (FarmerStateMove: +0,5 y em 5 de 8 quadros; veículos vibrantes +0,1 em 2 de 4); ações por Farmer.StartAnimation(name). Host envia nomes, tira salto do fluxo de posições; participante o repõe ao mover. Worker.Update zera velocidade de animação sem tempo normal: restaurá-la no participante.
- Criar FarmerPlayer com inventário aberto: FarmerPlayer.Restart, FarmerInventory.SetCapacity, GameStateInventory.CheckTargetUpdated acessa painel na cópia destruída e falha durante criação, deixando UID registrado (novas criações: "same key"). Pular callback durante aplicação; em exceção de criação remover objeto parcial e UID dos dicionários ObjectTypeList.
- QA: TCP 42/42 (duas vezes), formato UDP 44/44.

## <a id="070-unlocks-wardrobe-aquarium-2026-10-20"></a>0.7.0 desbloqueios, guarda-roupa, aquário (2026-10-20)
- `QuestManager.m_BuildingsLocked` separado de `m_ObjectsLocked`; ambos seguem host ou paleta atrasa. Reaplicar após carregar seção Quest (reinicia pelas medalhas).
- `WardrobeManager` armazena globalmente, não por construção. Sincronizar como seção própria; limpar `m_Objects` antes de `Load`, sob `ObjectTypeList.m_Loading`.
- `StartWardrobe`/`StartAquarium` no host redirecionados ao participante. `CanDoAction`/`SendAction` conferem `GetActualState()`; interação remota precisa forçar Normal.
- `GameStateInventory.Close` chama `m_Engager.SendAction(Disengage)` no objeto do painel; reconstruído por sincronização, é cópia destruída e não desengaja. Rastrear UID em interação e enviar manualmente.
- Host pode segurar objeto solto enquanto cópia ainda tem pai (graveto na mão, ninho na árvore). Carregar no local não remove pai; separar e recriar.

## <a id="080-version-check-savereload-seats-2026-10-20"></a>0.8.0 versão e lugares salvos/recarregados (2026-10-20)
- Hello leva versões do mod e jogo (`SaveLoadManager.GetVersion()`); protocolo 2. Host envia Info `reject` com motivo, fecha em 2 s. Hosts antigos fecham silenciosamente; participante avisa possível diferença de versão.
- Salvamento já contém FarmerPlayers convidados, faltava responsabilidade. Guardar `{host, seats}` em chave raiz extra `AutonautsCoop` (postfix `SaveJSON.Capture`, inclui automáticos); ler em prefixo `LoadJSON.InitialSetup` (`LoadJSON.m_RootNode`). Jogo ignora chaves desconhecidas.
- Após recarga, `GetPlayers()[0]` continua personagem do host antes de hospedar; ordenação usa UID salvo com Role Off.
- Lugares ligados à instância `TileManager`; mundo novo os limpa.

## <a id="090-bot-server-catapult-spaceport-planning-speed-2026-10-21"></a>0.9.0 servidor de bots, catapulta, espaçoporto, planejamento, velocidade (2026-10-21)
- Biblioteca (`WorkerScriptManager`) e áreas planejadas (`PlanningManager`, `m_PlanningArea` privada, sem UIDs) editadas por chamadas/escritas diretas. Observar seção inteira enquanto editor do participante aberto; enviar ao mudar, host substitui e retransmite. Calcular hash após ida/volta de interpretação JSON ou eco próprio não corresponde.
- Substituir biblioteca perde `StoredScript.m_LinkedBots`; religar de `m_WorkerInterpreter.m_LinkedScriptUID` de cada Worker e `DataStorageCrude.m_LinkedScriptUID`.
- Enviar biblioteca antes de vincular, ou host vincula script que não tem.
- Reconstruir `BotServerSelect` aberto após substituir (`m_Scripts` privada, `CreateScripts`, `UpdateLinkButtons`).
- Mira da catapulta: `GameStateSetTargetTile` prevê `SetTargetTile` a cada passagem do cursor; enviar só em `Close(Restore:false)`.
- `DiscardRegularMission` sorteia substituta: só host. Missões por `m_ID` e `m_Daily`.
- Telas com prédio reconstruído perdem `m_Building`/`m_Engager`; OnDestroy não desengaja. Enviar alternativa ao fechar menu sem evento.
- Velocidade: `TimeManager.m_TimeScale` e `m_PauseScreenEnabled` como seção global; bloquear `ToggleFastTime`/`SetTimeScale` nos participantes.

## <a id="0100-groups-undo-leaverejoin-saves-bug-report-big-bases-2026-10-21"></a>0.10.0 grupos, desfazer, sair/retornar, salvamentos, bugs, bases grandes (2026-10-21)
- Grupos: `WorkerGroupManager` (identificadores/listas UIDs) com painéis `TabWorkers`. Substituir: `SetWorkerGroup(w, null)` nos agrupados, `TabWorkers.RemoveGroup` por grupo, depois `Load` (recoloca painéis/membros). Bot reconstruído perde `m_Group`; restaurar após criar. Botões (`EditGroup.Stop/Play/Pause/DropAll/CallAllChildren`, privados, recursivos) executam no host.
- Desfazer: histórico `GameStateEdit` do participante é local/vazio. Manter passo por participante no host (adicionados, excluídos tipo/célula/rotação, posições anteriores dos movidos); mostrar na paleta definindo enum privado `m_UndoAction` e chamando `UpdateButtons`.
- Sair: salvar JSON FarmerPlayer (carga/inventário/melhorias/roupas aninhados), destruir com filhos, guardar em `AutonautsCoop.parked`. Restaurar sob `ObjectTypeList.m_Loading` preserva UIDs. `CollectionManager.m_Players` retém entradas destruídas/recicladas após StopUsing; removê-las ou `GetPlayers()[0]` quebra. Mundo salvo com participantes ativos: estacioná-los no postfix `LoadJSON.EndLoad`.
- Objetos reciclados: cópia destruída pode ainda avaliar verdadeira com `m_UniqueID == -1`. Conferir UID, não só `(bool)`.
- `ConverterFoundation` nomeia prédio futuro por `"NewID"`, não `"UID"`; tratar como filho aninhado ou Load local causa "same key" e Converter parcial quebra próximos salvamentos.
- Fechar TCP descarta quadros enfileirados; esvaziar antes (fim da sala, recusas). Processar caixa antes de conferir `Alive` ou motivo se perde.
- Salvamentos participantes: bloquear `SaveLoadManager.DoAutosave` privado e QuickSave para nome da sessão; Save As funciona.
- Novo jogo: mundo de fundo define `SaveLoadManager.m_MiniMap = true` (84x96) até terminar; torná-lo false. `m_Options.m_PlayerPosition` retém tamanho anterior; reiniciar ou `WorldGenerator.GetPlayerStartPosition` excede limites em mapa pequeno.
- Bases grandes: serializar tudo custa ~0,035 ms/objeto. Incremental: móveis a cada varredura, alterados por 3 s, movidos e fatia circular (volta completa ~5 s). Caminhos (`SandPath/StonePath/Road*`) e `Floor2D` escolhem rotação por vizinhos localmente; excluir Rotation dos hashes.
- Ambiente de teste: duas instâncias médias (~3 GB cada) mortas por falta de memória; estresse usa mapa pequeno com base densa.

## <a id="011-012-real-saves-garbage-editors-2026-10-2126"></a>0.11-0.12 salvamentos reais, lixo, editores (2026-10-21..26)
- Testar cedo salvamento avançado: primeiro (Settlement, ~10.800 objetos, mods Lua Workshop) quebrou participante em segundos, enquanto suíte de mundo novo passava.
- Programa do bot identifica prédios por `"UID"` no JSON. Só contar `{"ID":"<type>","UID":n` como filhos aninhados, ou atualização de bot destrói esses prédios no participante.
- Jogo salva floats em centésimos inteiros e perde um por ciclo salvar/carregar; carregar valores do host para salvar exatamente, ou toda conferência falha e objetos são reconstruídos.
- Quantidade carregada de armazenamento espera em `m_TempStored` privada por Refresh ignorado em armazenamento empilhado; definir `m_Stored` e limpar temporário manualmente.
- Transmitter de Settlement gera recompensas locais no participante; usar faixa de UIDs exclusiva ou toma próximos do host.
- Mods Lua Workshop também executam no participante; bloquear chamadas `ModManager` que mudam mundo (escrever armazenamento, criar, destruir, mover...).
- Custo de base grande é lixo, não tempo por quadro (GC Unity 2018 pausa ~200 ms com heap 1 GB). Impressões digitais baratas (campos permitidos por reflexão) antes de salvar tudo; enviar texto salvo sem interpretar/resserializar.
- Cabanas: recarregar sem moradores (`Folks` esvaziado), depois cada um; estado espera campo que só `Refresh` aplica, então chamar `SetState` privado diretamente.

## <a id="01237-in-place-reloads-2026-10-26"></a>0.12.37 recargas no local (2026-10-26)
- `Converter.Load` termina com `SetState(saved)`. Converting para Converting executa `EndConverting` local: ingredientes destruídos, estágio contado, callback de conversão concluída disparado. Definir `m_State = Idle` e parar `m_PlaySound` privado antes de Load local.
- `ConverterFoundation.Load` limita `Stage` a stages-1; host salva todos completos no quadro de conclusão. Definir `m_Stage` do JSON após Load.
- `Housing.OnDestroy` percorre `m_Folks`; ao sair, sessão reinicia antes da cena desmontar, então guarda `Role == Client` falha; descartar entradas mortas incondicionalmente.
- Quatro cópias com salvamento avançado cabem num PC 32 GB (kit `mode=four`).

## <a id="01238-0130-native-menus-creative-beta-2026-10-26"></a>0.12.38-0.13.0 menus nativos, Creative, beta (2026-10-26)
- Interface pelos prefabs do jogo: clonar botão de texto (ocultar filhos exceto Shadow/Back/Border/Text), painel de placa (`Prefabs/Hud/RenameSign`) para entrada, aviso (`Prefabs/Hud/Rollovers/WarningRollover`, destruir componente `WarningRollover`) para notificações, `GameStateConfirm` para mensagens (substituir título após `SetConfirm`).
- `BaseMenu`: botões em postfix de `Awake` (antes de `Start` registrar cliques) ou `RegisterGadget` + `AddAction` depois de `Start`.
- Pausa sem linha livre (Planet Scan acima de Save/Load/Continue): margem direita comporta botões 190x70 em 1280x720.
- Título (`State.Start`) antecede menu; `SetState(MainMenu)` pula nos testes. Iniciar mundo ~2 s depois falha em `WorldGenerator.CreateObjects` (prévia de fundo, `m_MiniMap`); iniciar imediatamente.
- Criação Creative (`CreativeTools.OnObjectClicked`) cria localmente: enviar tipo/categoria/extra/shift ao host, reproduzir no personagem participante.
- Participante abrindo Load conectado falha: ocultar `LoadButton` na pausa e recusar `Paused.OnLoad` / `GameStateLoad.Init`.
- Sessão do autor em dois PCs Steam pela internet (2026-10-26): hospedagem, convites, entrada e jogo funcionaram; encontrou os dois problemas acima.
