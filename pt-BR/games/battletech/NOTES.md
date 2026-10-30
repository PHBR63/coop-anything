# <a id="battletech-2018-co-op-campaign-feasibility-notes"></a>BattleTech (2018): notas de viabilidade da campanha cooperativa

Estado ao escrever: etapas 0-3 (triagem, pesquisa, análise estática), antes de implementar qualquer coisa. Descobertas posteriores estão no fim.
Data: 2026-10-16.

## <a id="game-identity"></a>Identidade do jogo

| | |
|---|---|
| Loja | Steam, aplicativo 637090, identificador de compilação 20387569 |
| Versão | 1.9.1, BuildNumber 686R, BuildStamp 200226-live-cdbbe62 (`BattleTech_Data/StreamingAssets/version.json`) |
| SHA-256 de `BattleTech.exe` | `a12620dd89f2a7fc51fe228d38ba656574228a1c9412c27ca556fee08c5fc42f` |
| SHA-256 de `Assembly-CSharp.dll` | `9eaa1b3a4dfd80ac03abd47097541e9883a4fa4d4021d877b9b8faa2d23c8b2d` |
| Motor | Unity (Mono, `MonoBleedingEdge`), código C# do jogo em `Assembly-CSharp.dll` |
| Sistema operacional | Windows 11 |
| Mods instalados | nenhum (sem pasta `Mods/`) |

## <a id="prior-work"></a>Trabalhos anteriores

- Nenhum mod de campanha cooperativa encontrado ([busca 1](https://www.nexusmods.com/battletech/mods/584?tab=posts), [Mission Control](https://github.com/CWolfs/MissionControl)). Sem entrada em DIRECTORY.md nem issues ou PRs neste repositório.
- Componentes existentes: carregador ModTek; carregador nativo da HBS desde a versão 1.7 ([ModTek](https://github.com/acook/ModTek)); Mission Control (alterações de contratos e encontros em tempo de execução, lanças extras) e Bigger Drops (mais de 4 unidades do jogador) ([Mission Control](https://github.com/CWolfs/MissionControl)).
- Há multiplayer oficial, mas somente escaramuças PvP. Seu serviço on-line sofreu interrupções, sem aviso oficial de encerramento encontrado ([discussão Steam](https://steamcommunity.com/app/637090/discussions/0/5294572213363418960), [separação do estúdio](https://www.rpgsite.net/news/14992-paradox-and-battletech-developer-harebrained-schemes-to-part-ways-in-2024)).

## <a id="method"></a>Método

O `inspect_managed_artifact` do REA atingiu seu limite de 64 MB de representação de metadados no `Assembly-CSharp.dll` de 13,6 MB. Por isso, metadados e grafo de chamadas IL foram extraídos com dois pequenos scripts `System.Reflection.Metadata` (tipos, campos, métodos, strings de usuário; uma linha por aresta de chamada/campo/ldstr, 641 mil arestas). Nenhum código-fonte descompilado é armazenado aqui.

## <a id="observed-from-shipped-assemblies"></a>Observado (nos assemblies distribuídos)

1. **Toda ação de combate é uma `InvocationMessage`.** Subclasses incluem `MechMovementInvocation`, `AttackInvocation`, `MechMeleeInvocation`, `MechDFAInvocation`, `MechJumpInvocation`, `SensorLockInvocation`, `VentCoolantInvocation`, `ReserveActorInvocation` e `EjectInvocation`. Cada uma contém `RandomSeed` e `InvocationID`, com `ToJSON`/`FromJSON`. Movimento leva o caminho completo `Waypoints` e `FinalOrientation`; portanto, o caminho é calculado pelo emissor, não recalculado por cada receptor.
2. **`InvocationHandler::GenericInvoke` é o ponto único de passagem.** Verifica `IsNetRouted`/`WasNetRouted` e `NetworkGameInstance::IsNetworkGameActive`, enfileira a invocação se houver uma ordem em execução, remove duplicatas por `InvocationID`, define `CombatGameState.NetworkRandom.seed = invocation.RandomSeed`, registra em `MultiplayerGameVerification` e chama `Invoke`. **O modo para um jogador usa o mesmo caminho; multiplayer só acrescenta o roteamento.**
3. **O gerador aleatório da lógica é determinístico.** `NetworkRandom` encapsula `HBS.Math.XorShiftRandom`. Seu construtor usa semente fixa (sem leitura de relógio), redefinida por invocação. `UnityEngine.Random` só é usado para *sortear* a semente nos construtores de invocações (na máquina emissora) e nos visuais (`*Representation`, VFX, câmera, textos flutuantes).
4. **O roteamento é simples retransmissão.** `MessageCenterMessageHandler::HandleNetRoutedMessages` do cliente envolve a mensagem em `NetMessageCenterMessage` e a envia. `MessageCenterMessageHandler::HandleMessage` do servidor encaminha a todas as sessões; o cliente receptor define `WasNetRouted` e republica no `MessageCenter` local.
5. **O jogo inclui servidor completo dentro do processo:** `BattleTechServerInstance`, `GameLobbyManager`, `NetworkSessionManager`, endpoints para Loopback, Lidgren (IP direto, Open.Nat), SSE, PlayByPost e Steam (`SteamServerEndpoint` cria salas por `SteamMatchmaking`). Steamworks.NET (452 tipos, incluindo `SteamNetworking`) fica em `Assembly-CSharp-firstpass.dll`.
6. **Detecção nativa de dessincronização:** `StatsComparer`/`StatsCompareNetworkMessage`, `MultiplayerGameVerification` e `NetworkRandom.RecordHistory`/`GetHistory`.
7. **Existe sincronização de turnos:** `TurnDirector::SendTurnActorActivateMessage` usa barreira `NetSynchronizeMessageRequest` quando há partida de rede ativa (chamada direta nos outros casos).
8. **Equipes:** `TeamController` = {Computer, Player1, Player2}. `Team.LocalPlayerControlsTeam`, `IsLocalPlayer`. `EncounterLayerData::CreatePlayerOneTeam/CreatePlayerTwoTeam` seguem caminhos diferentes no multiplayer.
9. **A IA não é determinística entre máquinas:** `AITeam::getInvocationForCurrentUnit` lê `Time.realtimeSinceStartup` (orçamento de raciocínio), e `AITeam::IsReserveDieRollSuccessful` usa `UnityEngine.Random`. A IA ainda produz invocações normais (`AITeam::make*Invocation`).
10. **Avançar diálogo é interface local:** `CombatHUDDialogItem::Update` lê `Input.GetKeyDown` e `Time.deltaTime`. O jogo tem `DialogueContinueMessage` (mensagem de MessageCenter).
11. **Scripts de história leem o estado da campanha:** `TScript.Ops.BattleTech` chama `GameInstance::get_Simulation` 41 vezes; `Contract` chama 20 vezes.
12. **O gerador aleatório da campanha também é `NetworkRandom`:** `SimGameState::.ctor/Rehydrate/PrepContract` definem sua semente.
13. **Salvar é bloqueado no multiplayer:** `GameInstance::CanSave` verifica `IsMultiplayer`. Tipos de contrato têm indicadores `IsMultiplayer`, `IsSinglePlayerProcedural` e `IsStory`. Contratos de história nunca foram testados em multiplayer.
14. A HBS inclui `0Harmony.dll` e um `BattleTech.ModSupport.ModLoader`.

## <a id="derived"></a>Deduzido

- Combate cooperativo = **lockstep determinístico por invocações**. Exige estado inicial igual nas duas máquinas, todas as invocações (jogadores e IA) passando por uma autoridade de ordenação e barreiras onde o jogo espera interface local (diálogos, ativação de turno, fim de missão).
- Executar IA somente no host e transmitir suas invocações elimina o não determinismo da IA.
- Camada de campanha: convidado precisa do `SimGameState` exato do host (condições TScript o leem). O caminho mais barato é transferir o salvamento do host ao iniciar um contrato. O gerador aleatório da campanha tem semente definida e salva.
- O grande problema das 8 unidades do jogador já foi resolvido por mods comunitários (Bigger Drops, Mission Control).

## <a id="guesses-unverified"></a>Hipóteses (não verificadas)

- Física/raycasts Unity usados na linha de visão e caminhos produzem resultados idênticos em dois PCs com a mesma compilação. A escaramuça multiplayer depende disso; movimentos enviam seus pontos de passagem, reduzindo o risco.
- Gatilhos de encontros da história (região, objetivo, cadeias de diálogo) são dirigidos por mensagens MessageCenter emitidas por invocações e, por isso, repetem de forma idêntica. Alguns podem consultar temporizadores por quadro. `Contract::GetRandomObjectiveStatus` usa `UnityEngine.Random` (local da chamada não rastreado).

## <a id="unknown"></a>Desconhecido

- Se `BattleTechServerInstance` pode executar sem autenticação nos serviços HBS/Paradox (`NetworkServerAuthentication`).
- Se o modo não intercalado (movimento livre fora de combate) tem caminhos adicionais somente locais.
- Se salvamentos de combate (o modo solo permite salvar no meio da missão) são restaurados identicamente em outro PC (necessário para reconectar).
- Comportamento de Flashpoints e missões de história dos DLCs em lockstep.

## <a id="next-steps"></a>Próximos passos

Resumo de viabilidade: (M0) estrutura de mod ModTek e transporte Steam P2P; (M1) lockstep de escaramuça contra IA com verificações de dessincronização; (M2) contrato de campanha com transferência de salvamento; (M3) responsabilidade por unidades e duas lanças; (M4) barreiras de diálogo/turno/fim de missão; (M5) QA com bots.

## <a id="runtime-check-m0-2026-10-16"></a>Verificação em execução: M0 (2026-10-16)

Inicialização de cópia de teste (ModTek v4.5.1, exibindo `/W MODTEK`), uma escaramuça contra IA, 3 rodadas, com patch de log BattletechCoop em `InvocationHandler.GenericInvoke`. O log mostrou:

- `GenericInvoke` recebe toda mensagem MessageCenter (1.242), das quais 25 eram invocações.
- Movimentos da IA (`AbstractActorMovementInvocation`) e do jogador (`MechMovementInvocation`), ataques, reservas e travas de sensores chegaram ao ponto. Isso confirma em execução os itens observados 1-2 e 9.
- Invocações levam `IsNetRouted=True` no modo solo; o roteamento é ignorado somente porque não há jogo de rede ativo.
- `InvocationID` = `<machine prefix>.<counter>`.

## <a id="later-findings-2026-10-17-to-2026-10-19"></a>Descobertas posteriores (2026-10-17 a 2026-10-19)

Registradas integralmente, com cada execução de teste, no [docs/DESIGN.md](https://github.com/Cryswar/battletech-coop/blob/main/docs/DESIGN.md) do projeto. As que respondem às dúvidas acima ou teriam economizado tempo:

- Salvamentos de combate **não** restauram de forma idêntica o estado ao vivo original, mesmo no mesmo PC: componentes retornam em outra ordem, fazendo um acerto crítico escolher outro componente no convidado (seq 207, encontrado por comparação de todos os atributos). Agora ambos partem do mesmo salvamento carregado.
- O primeiro ponto em que se permite salvar combate (`CombatGameState.CanSave`) é após a conversa inicial da missão; por isso, o convidado não a via até a 0.0.12. Corrigido na 0.0.13 por salvamento no briefing, carregado como reinício de combate (`GameInstanceSave.flaggedForRestart`), iniciando o contrato salvo do começo.
- Reiniciar combate recarrega a definição da missão e sorteia novamente lanças e unidades baseadas em tags (`LanceOverride.RequestLance`, `UnitSpawnPointOverride.RequestUnit`); escolhas do host (`selectedLanceDefId`, `selectedUnitDefId`, `selectedPilotDefId`) precisam ser enviadas e regravadas como identificadores explícitos.
- Carregar salvamento enquanto o briefing está aberto (`ProcessLoadedFile`) nunca chega a `CreateCombatFromSave`, mesmo após desaparecer a cortina de carregamento; portanto, o host não consegue recarregar do briefing.
- `InterruptDialogSequence.AfterDialogHide` retorna `SimGameConversationManager.ConversationState`; um prefixo Harmony declarando `ref bool __result` faz HarmonyX recusar o patch e falhar todo o `PatchAll` do mod.
- Nos testes de jogo automático, Player 1 é `AITeam`, que permanece na pilha e mantém `CanSave` false; o teste usa as mesmas condições sem verificar a pilha.
- Movimento livre fora de combate (modo não intercalado) produzia falsas dessincronizações por unidades ainda executando ordens no momento do snapshot; ignorar unidades com `OrderSequence` ativa resolveu.
- Unity trava em "Input initialized" antes de executar código de mods enquanto a tela está suspensa; testes sem supervisão precisam manter a tela acordada.
- ModTek permite um processo por pasta de instalação; a segunda cópia de teste é uma pasta de pequenas cópias de arquivos com junção para `BattleTech_Data` da primeira.
- `MechBayPanel`, `SGBarracksWidget` e outras telas permanecem na cena após o primeiro uso: verifique `UIModule.Visible`, não somente `activeInHierarchy`, antes de redesenhá-las.
- `SGBarracksMWDetailPanel.SetPilot` deixa `tempPilot` nulo até alguma edição; portanto, "edições não confirmadas" é `SGBarracksWidget.IsCurPilotModified()`, não comparação de referências.
- `SimGameState.ReadyMech` e `ScrapInactiveMech` sobrescrevem o argumento `id` (identificador de chassi para identificador de atributo de armazenamento) antes de retornar, e um postfix Harmony vê o valor sobrescrito.

Desde 2026-10-20, o diretório também lista um projeto cooperativo separado de BattleTech, de outro desenvolvedor no Discord do Co-op Anything.
