# <a id="code-vein-2019"></a>Code Vein (2019)

| | |
|---|---|
| Motor | Unreal Engine 4.18 (`++UE4+Release-4.18`), Denuvo ainda presente |
| Versões testadas | Steam (aplicativo 678960), ProductVersion 1.53.93354, SHA-256 do executável `8fa550fe00a8c28c8947a9511128c21924860be0bb4ebf5a09b8a6cf50e0e172` |
| Projetos | [eight8pac/codevein-coop](https://github.com/eight8pac/codevein-coop) (código, MIT; reivindicação: cranebeaker/coop-anything#207); mod Nexus 192 (mais antigo, parcial) |
| Nível de QA | none (somente sessões manuais em dois PCs) |
| Última atualização | 2026-10-29 |

## <a id="where-things-stand"></a>Situação atual

Code Vein já oferece modo cooperativo on-line para host e **um** convidado, conectados por sinais de socorro. O original encerra a sessão quando o host morre, quando o convidado morre definitivamente na sala do chefe e após cada chefe morto, além de proibir modo cooperativo em áreas cujo chefe já morreu. Este projeto mantém a sessão original e contorna esses encerramentos. Um mod Lua UE4SS hospeda e reconecta automaticamente após mortes no campo, do host, na sala do chefe e derrotas de chefes. Uma DLL de hooks nativos (C, MinHook) alcança o que Lua não consegue. Nas sessões de dois PCs: convidado morto definitivamente permanece no mundo, observa o host e reaparece junto dele no descanso seguinte em um Mistle (o parceiro não pode reanimá-lo após o prazo); convidado retido em luta de chefe permite a cena final do host após a vitória; host descansa com convidado conectado; convidado abre seu próprio menu Mistle no mundo do host e sobe de nível (ambos veem nível e HP máximo novos); teletransporte do host por Mistle leva o convidado, inclusive a outra região. A meta é história cooperativa contínua para 3+ jogadores; hoje não há versão distribuída jogável. Código: [eight8pac/codevein-coop](https://github.com/eight8pac/codevein-coop).

## <a id="existing-work"></a>Trabalhos existentes

- **Mod Nexus 192** (2020), descrito como mod cooperativo. Segundo uma resposta de fórum, só permite ao host enviar sinais em áreas cujo chefe morreu; convidado ainda é removido na morte do chefe e barreiras de neblina permanecem. A página não foi obtida (bloqueada), então não está verificado. Fonte: <https://steamcommunity.com/app/678960/discussions/0/7098294290812770549>
- Resposta de 2023 diz que nenhum mod aumenta convidados ou adiciona modo contínuo: <https://steamcommunity.com/app/678960/discussions/0/3875968032471215769>
- Na mesma discussão existe alegação não verificada de mod contínuo pago. Trate como desconhecido.
- **UE4SS funciona neste jogo**: "Ultra Plus for Code Vein" o inclui (<https://www.nexusmods.com/codevein/mods/808>).
- Petição de fãs por limite de 3 jogadores: <https://www.change.org/p/bandai-namco-expand-code-vein-s-player-limit-to-3>
- Regras cooperativas originais: <https://www.shacknews.com/article/114202/how-to-play-co-op-in-code-vein>

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

**Empacotamento.** Pak versão 4, sem criptografia, blocos zlib; Blueprints preparados são separados em `.uasset` (tabela de nomes) e `.uexp` (bytecode). Um leitor pak mínimo, somente de leitura, e localizador de chamadas Kismet respondem à maioria das perguntas sobre quem chama o quê e com quais argumentos, sem extrair nada.

**Executável e Denuvo.** O executável **não tem ASLR** (`DYNAMIC_BASE` desligado); endereços são fixos, e endereços dos exec-thunks UFunction no dump UE4SS podem ser usados diretamente em hooks nativos. Denuvo principalmente **realocou** corpos de funções: o endereço original contém `jmp` de 5 bytes à grande seção `.code`, onde há código simples e legível do compilador. Descompilações direcionadas Ghidra (sem interface, sem análise completa) levam um minuto cada. Sem RTTI; vtables podem ser lidas de objeto ao vivo (ou do executável, pois são dados estáticos).

**UE4SS.** v3.0.1-1181 (`experimental-latest`) injeta corretamente apesar do Denuvo. **`HookLoadMap = 1` causa falha** na primeira viagem de mapa (`UGameEngine::Tick`+0x398); encontrado por divisão sucessiva dos 14 hooks. Nesta compilação, UE4SS só insere hooks em **UFunctions nativas**: funções definidas em Blueprint e BlueprintImplementableEvents não registram hooks, embora chamadas a eventos BP por Lua funcionem. **Hook Lua em `FieldTriggerBase:IsAuthorization` congelou o jogo** na primeira sobreposição de Mistle; evite. Atalhos não disparam por teclas injetadas; controle mods consultando um arquivo de acionamento.

**Camada on-line** (módulo `/Script/Extensions`):
- `UAppOnlineWrapper` envolve OnlineSubsystem Steam (`SteamNetDriver`, retransmissão P2P ligada). `UAppSessionManager` acrescenta sinais de socorro. **`ERescueSignalState` (Idle 0, Sending 1, Receiving 2, CooperativeMode 3, EndOfCooperativeMode 4) é o byte em `AppSessionManager + 0xE08`**. Estado 3 é definido assim que um sinal é emitido, antes de alguém entrar.
- **A sessão só abre com os quatro canais de `ESessionOpenness` abertos: Field = 1, BossArea = 2, Cinematics = 4, EnemyLevelResetByCheckPoint = 8.** `ExpectsBeOpenRaw(bit)` informa um canal. Cenas fecham Cinematics; descanso Mistle fecha EnemyReset por cerca de 2 s; em área com chefe morto, Field permanece fechado.
- Fluxo da sessão no Blueprint da instância (`/Game/Modes/App_GameInstance`): `Event_CreateLobby(PublicConnections,
  UseLAN, Caller)` → nativa `CreateOnlineSessionLatent`; `Event_FindAndJoinSession(Caller)` → nativa `FindAndJoinOnlineSessionsLatent` (busca estrita, depois tentativa mais flexível). O único chamador de ambas é `UserInterface/FieldMenu/BP_FieldMenuUIComponent`, cujo bytecode passa **`PublicConnections = 3`**; o número nunca chega às configurações da sessão (deduzido das tabelas de nomes). **O limite de um convidado é nativo.**
- **Máquina de estados nativa:** inteiro interno em `AppSessionManager + 0xD90` (códigos 0x00 a 0x22) dirige o estado visível por tratador de entrada de estado (corpo `0x146EA3AC0`). Códigos 0x1F e 0x20 definem EndOfCooperativeMode. **`EndCooperativeMode`
  (corpo `0x146E92EF0`)** muda imediatamente para 0x1F (sem outros jogadores) ou define solicitação em `+0xDC0`, convertida logo depois em 0x1F. Seu único chamador direto trata morte de jogador. Morte definitiva do convidado na sala do chefe chega ali cerca de 7,5 s depois, simultaneamente nos dois PCs; host então destrói a sessão.

**Encerramentos observados nas sessões originais de dois jogadores** (logs do host):

| Evento | Resultado |
|---|---|
| Jogador incapacitado | Sessão fechada a novos participantes por cerca de 26 s; convidado permanece |
| Convidado morre no campo | Convidado removido; sessão continua aberta |
| Host morre | Sessão destruída nativamente cerca de 3 s depois |
| Morte definitiva do convidado na sala do chefe | Ambos mudam para EndOfCooperativeMode cerca de 7,5 s depois; host destrói sessão; convidado volta para casa após mais 4 s |
| Entrada na neblina do chefe | Bloqueio de operações, sessão fechada, `BossAreaState` 0→1→2 |
| Chefe morto | `MulticastGainRewards` → `MulticastFinishBossBattle(true)` → `ServerRequestNetworkDisconnect` **do próprio convidado** |
| Área com chefe morto | `IsSendRescueSignal` false (menu desabilitado), canal Field fechado |
| Menu "cancel signal" / "leave" | `DestroyOnlineSessionLatent` (único encerramento que o chama, no host e convidado) |
| Descanso Mistle com convidado conectado | Comando desabilitado (verificações nativas abaixo) |

**Descanso Mistle.** A substituição `IsActionButtonActive` (vtable `+0x660`) desabilita o comando quando `IsOnlineMultiplay()` ou verificação de "mais de um jogador" (`0x140828970`) é true (também por invólucro no início), e com inimigos próximos. `ProcessInputButtonEvent` (vtable `+0x618`) começa pela mesma verificação antes de descansar.

**Mortes.** Primeiro o jogador cai no estado "dying", ainda reanimável (`CharacterHelper:IsDying`; parceiro ou outro jogador pode reanimar). Quando o prazo termina, a morte segue dois caminhos: `CharacterHelper:RequestTryExecuteDeath` -> `0x140508540(world, character, ...)` (quedas e similares, decididas pelo host) e processamento de componente `0x14056AC60` (componente `+0xE8` = personagem; prazo esgotado no convidado é decidido pelo jogo dele). Ambos levam ao escurecimento da morte (`FadeUIComponentIF:RequestDeathFade`, que também mascara temporariamente entradas no controle; somente `RequestUnfade` desse componente libera), à dissolução (`bIsDisappearExpression`, efeito material não revertido por indicadores de visibilidade) e, no convidado, à saída (`SwitchToEndCoop` de `0x14633CFA0`, cerca de 3 s depois). Vetar os dois caminhos para convidado com host vivo mantém "dying" sem sequência de morte; alterar a sequência depois (remover escurecimento, máscaras, modo de entrada) não devolveu controles após reaparecer. `CharacterHelper:RequestPlayerSpawn(ctx, controller,
location, rotation, controller rotation, IsByRespawn, SkipAppear)` no host cria novo pawn para o controlador convidado, com efeito de aparecimento. A reanimação do parceiro não consulta `CharacterHelper:IsNeverRevive`.

**Funcionamento interno do Mistle.** `ProcessInputButtonEvent` (corpo `0x146A1CB70`) posiciona o jogador, solicita fechar EnemyLevelResetByCheckPoint (`0x1408176A0` = CloseOnlineSession(8), evento 0x16), cria ator, define estado do Mistle e continua no callback após a animação de sentar, abrindo o menu. No convidado, a parte de sessão para (somente 0x16 -> 0x19), e alterar estado provoca asserção (`CheckPointBase.cpp:850`, "WITH_EDITOR"). O menu abre em qualquer lugar por `BP_CheckpointUIComponent:Open(None, None, 0, None, WDT_CheckpointMenu_C)`. Entradas são widgets (`WDT_CommonListTextPiece_C_*`; na ordem visual: subir nível, dons, armazenamento, teletransporte, trocar parceiro, presentes, tutorial, sair).

**Onde fica cada estado do convidado.** Sua haze fica em seu PC (`HumanContextComponent:Server_AddExp` no host o alcança, mantendo a cópia do host em 0). Nível visto pelo host (e HP máximo devolvido por `Multicast_SyncTotalMaxHealth`) fica na cópia dele no host. Getter de nível (`HumanContextIF` base `+0x90`) só retorna o nível armazenado quando o personagem está "in charge" (`0x140456A00`, semelhante a autoridade); caso contrário, deriva dos dados do jogador, e o setter grava esse valor derivado, então subir nível normalmente no convidado não altera nada. Nível, dons e equipamento sincronizam uma vez por componente na entrada (`ServerInitialDataSync`, enviado por `0x140465CA0`, protegido por `bIsInitialSynced`); convidado não consegue reenviar depois. Mensagem de subir nível do menu (`0x2c` a componentes `HumanContextIF`) não alcançou a função real `0x1405A2E20` em modo cooperativo.

**Teletransporte Mistle.** O mundo é um mapa persistente (`/Game/Maps/MainGame`) com subníveis de regiões carregados sob demanda, mas esse teletransporte não é movimento: usa `CheckPointUIComponent:RequestPlayerSpawnToCheckPoint(FieldID, PointIndex)`, criando novamente o jogador no destino. Rastreamento solo de dois teletransportes viu recriação (sincronização inicial e multicasts de equipar dons), sem chamadas de teletransporte adiado (`LIBDeferredTeleportManager:BeginDeferredTeleport`, `ScenarioActor:WaitForDeferredTeleportFinished`). `CharacterHelper:RequestPlayerTeleport(target, location, rotation, controller rotation, bSkipAnimation)` move um jogador existente (usado pela ferramenta de teste de outro autor); `CharacterHelper:RequestPlayerSpawn` cria novo pawn para controlador remoto. A implementação nativa `0x1409A1800(component, FieldID, PointIndex)` fornece o destino. Teletransportar com convidado encerra o modo duas vezes: `SwitchToEndCoop` de `0x146678D02` no início (após mensagem de encerramento/sinal, `0x14083A630`) e, ao chegar à região, código de entrada (`SwitchToEndCoop` de `0x146D627CF`, depois `0x1409F1BA0`, que exibe "multiplayer is not possible in this area" e encerra por Blueprint). Home Base é mapa separado: o original encerra o modo e viaja para lá.

**Cenas de história e memórias.** Cenas de campo e introduções de chefes já funcionam com convidado (ambos veem). A cena após o chefe (por exemplo, `Cinematics/Scenario/St09_Mt_Snow/.../BP_ScenarioFlowDiagram_e06700_e06800`) é cadeia de esperas nativas latentes em `ScenarioActor`: `WaitForPreparePolyFinished`, `WaitForLargePolyFinished`, `WaitForDeferredTeleportFinished`, depois `ScenarioManager:PlayMemoryResidue` e `WaitForMemoryResidueFinished`, com `bSpawnPlayerOnExit`. Sem expulsão após chefe, host travou na tela de carregamento no início da cena, antes de existir objeto de memória; ainda não se sabe qual espera bloqueia. A tela de restauração de vestígios (`BP_BCRestorationUIComponent`) consulta `AppSessionManager:IsCreateSession` e `AppOnlineWrapper:GetOnlineOtherPlayerNum`, exibe "ending the distress signal / co-op" (`MultiplayText_0470`/`0480`), destrói sessão e entra na memória (`JumpToMemory`, `MemoryResidueId`). Com sinal emitido, jogador não consegue experimentar memória sozinho; precisa de convidado para testar.

Com a expulsão removida (dois PCs, 2026-10-29), introdução e cena final começam normalmente; controlador de teletransporte adiado (`DeferredTeleportDriver`, estado `Done`, sem tokens de pausa) termina, e host aguarda carregamento antes de `PlayMemoryResidue` até o convidado sair; nesse momento, a cena começa imediatamente. Espera nas etapas de carregamento large-poly. O código de sangue do chefe só é concedido após a memória. Rastrear as UFunctions de espera de `ScenarioActor` por desvios exec-thunk travou a introdução; rastreie uma por vez.

**Sistema de salvamento.** Estado de história usa indicadores string (`UAppSaveManager::SetGameProgress`). Salvamentos ficam nos dados locais do usuário, em `CodeVein\Saved\SaveGames\<account>\`. `-userdir` é ignorado; isole testes trocando a pasta. Copiar `.sav` entre contas Steam funciona com Steam Cloud desligado.

**Teste em um PC.** Segunda cópia encerra imediatamente por mutex de instância única; só uma recebe identidade Steam, e cliente sem ela falhou nativamente em `open 127.0.0.1`. Simular `steam_api` não é opção, pois Denuvo confere propriedade pelo Steam. Testes de dois jogadores usam dois PCs (uma pessoa pode controlar ambos por ferramenta de acesso remoto).

**Armadilhas.** Hooks Lua UE4SS congelaram ou derrubaram o jogo em `FieldTriggerBase:IsAuthorization`, `AppSessionManager:
GetRescueSignalState` (ao enviar sinal) e ao inserir dez ou mais hooks simultâneos em UFunctions de morte/escurecimento (falha na tela inicial em UE4SS.dll); desvios nativos exec-thunk nas mesmas funções foram estáveis. Aceitar convite Steam ou "Join game" encerrou normalmente a cópia de teste e fez Steam abrir a instalação real, usando salvamento real: entre em testes somente pelo sinal de socorro interno.

## <a id="what-we-changed"></a>O que alteramos

Três partes: `CoopSeamless` (Lua, host e convidados), `CoopProbe` (Lua, log de estado somente de leitura) e `CoopNative` (DLL C carregada pelo Ultimate ASI Loader como `winmm.dll`, desvios MinHook, verifica 16 bytes em cada alvo antes de alterar).

- **Modo cooperativo em áreas com chefe morto.** `IsSendRescueSignal` forçado a true, depois `OpenOnlineSession(Field)`. Testado em dois PCs.
- **Expulsão após chefe (entendida e mantida deliberadamente).** A expulsão original é a reação do convidado a `MulticastFinishBossBattle(true)`; inverter o indicador nele mantém conexão, mas trava o host na cena que entra em memória solo. Por isso, a expulsão permanece, e o convidado reconecta depois.
- **Saída e reconexão automáticas (CoopSeamless).** Reconciliador a cada segundo, só após 8 s de calma (on-line, não ocupado, sem bloqueio ou chefe, próprio personagem vivo e não caído, sem sequência de fase, três outros canais abertos; reaparecer reinicia os 8 s). Host sem sessão chama `Event_CreateLobby(3, false, nil)`; com sessão e Field fechado chama `OpenOnlineSession(Field)`; convidado desconectado chama `Event_FindAndJoinSession(nil)` a cada 25 s. Modos host/convidado só ativam quando sessão/conexão *começa* manualmente; cancelar ou sair pelo menu (`DestroyOnlineSessionLatent`) os desativa. Resultados em dois PCs: consulte QA.
- **Recursos nativos (CoopNative + CoopProbe, desligados por padrão, ativados em `plugins\CoopNative.ini`):**
  - `rest_in_coop`: responde "não" às verificações multiplayer somente nas chamadas das funções de comando e entrada do Mistle; host descansa conectado, convidado fica.
  - `veto_endcoop` + `spectate_cam`: mantém sessão quando um jogador morre definitivamente em luta de chefe e outro vive. Exige vetar dois pontos, `EndCooperativeMode` e a pequena função de encerramento `0x14081BDA0`, chamada diretamente por um caminho de morte em Blueprint. Retido, o morto observa um vivo (`SetViewTargetWithBlend`), e sobreposições de morte (`WDT_FadeScreen`, `WDT_DeathParts`) são ocultadas. Na derrota do chefe, convidado retido repete a saída vetada para a cena do host terminar.
  - `keep_dying` (reaparecimento em grupo): veta ambos os caminhos de morte do personagem convidado (host: pawn dele; convidado: próprio pawn) enquanto host vive. Após acabar o prazo de reanimação, host remove o corpo (desvincular controle, destruir) para o parceiro não reviver; convidado observa, e o próximo descanso cria-o junto ao host com `RequestPlayerSpawn` e efeito de aparecimento.
  - `group_teleport`: veta as duas chamadas de encerramento do teletransporte do host (somente esses chamadores, por 60 s), pula mensagens e cria convidado junto ao host quando CoopNative vê a recriação dos personagens dele (`AppCharacter:MulticastInitialDataSync`). `teleport_skip_fields` mantém comportamento original nos destinos listados (destinado a Home Base).
  - Quedas: convidado cuja queda é decidida pelo host (`TryExecuteDeath` durante queda rápida) vai direto à observação: dissolve, corpo removido, retorno no descanso seguinte.
  - `guest_rest`: no convidado, E em Mistle aberto pula descanso original e abre menu próprio; trocar parceiro desativado (deixava-o no carregamento). Subir nível: o menu vira chamada direta a `HumanContextIF` no componente próprio, com `0x140456A00` forçado a true para o pawn durante a chamada (gasta haze, define nível); depois envia `Server_AddExp(0)` uma vez por nível. O host (`levelup_relay`) ajusta o nível de sua cópia com o setter sob a mesma condição forçada e recalcula atributos, atualizando HP máximo.

## <a id="qa"></a>QA

Sem suíte automatizada; nível de QA none. Testes foram sessões manuais em dois PCs (host em cópia completa, troca de salvamento e SHA-256 dos reais antes/depois de cada execução), com logs dos dois lados:

| Caso | Resultado |
|---|---|
| Convidado morre no campo | reconectou automaticamente após 27 s |
| Host morre | sessão encerrou, sinal voltou 8 s após reaparecer; convidado reconectou 27 s após encerramento |
| Morte definitiva do convidado em chefe, depois todos morrem | reconectou após reiniciar a luta |
| Chefe morto | cena final e memória normais para host; convidado reconectou 55 s após expulsão |
| Host encerra pelo menu | modo host desligado, sem novo sinal |
| Convidado sai pelo menu | puxado de volta (bug); correção escrita, ainda não testada com dois jogadores |
| Host descansa em Mistle com convidado (`rest_in_coop`) | funciona, convidado fica; inimigos reiniciam só uma vez por sessão |
| Morte definitiva em chefe (`veto_endcoop`, `spectate_cam`) | convidado permanece observando; morte de todos ainda encerra normalmente |
| Chefe morto com convidado retido | cena final do host funciona; convidado volta para casa e reconecta |
| Morte definitiva no campo (`keep_dying`) | corpo removido após prazo, observa; descanso recria junto ao host, visível e com entrada |
| Convidado em Mistle (`guest_rest`) | menu abre; cura permanece; nível e HP máximo aparecem nos dois; trocar parceiro desativado |
| Dons no convidado | desbloquear/equipar funciona originalmente após trocar para código de sangue do dom |
| Teletransporte Mistle do host (`group_teleport`) | convidado fica e aparece junto, dentro da região e em outra; vê o mundo descarregar por segundos |
| Queda profunda (`keep_dying`) | direto à observação; volta no descanso do host |
| Chefe morto sem expulsão | introdução, luta e cena final iniciam; host espera antes da memória até convidado sair |

## <a id="how-to-play"></a>Como jogar

Ainda não distribuído. Passos e configurações no README do código ([eight8pac/codevein-coop](https://github.com/eight8pac/codevein-coop)): UE4SS v3.0.1 com `HookLoadMap = 0` no host e convidados, mods Lua, opcionalmente Ultimate ASI Loader + CoopNative e mesma senha de pareamento (busca automática entra no primeiro sinal correspondente).

## <a id="known-issues"></a>Problemas conhecidos

- Sem senha, busca automática pode entrar no sinal de desconhecido.
- Convidado cujo host parou deliberadamente continua buscando a cada 25 s.
- Restauração de vestígios bloqueada (entradas do menu podem ser habilitadas; tela ainda recusa).
- Inimigos reiniciam somente no primeiro descanso cooperativo da sessão; descanso convidado não reinicia mundo do host.
- Convidado não abre baús nem vê itens no chão do host. NPCs de história seguem progresso individual (um apareceu duplicado no convidado).
- Durante observação, filtro de saúde baixa e batimentos continuam; convidado reaparecido pisca uma vez antes do efeito.
- Convidado abrir menu Mistle enquanto host descansa causa falha; descansar juntos também; inimigos não reiniciam após primeiro descanso.
- Teletransportar o grupo a Home Base joga host em um buraco (mapa separado; adicionar FieldID a `teleport_skip_fields`).
- Convidado entrar com host sentado em Mistle causa falha.
- Se sinal "fails to go through", criação da sala Steam excede tempo (`k_EResultTimeout` no log); reiniciar Steam resolveu uma vez.

## <a id="next-steps"></a>Próximos passos

1. Progresso do convidado e recompensas de chefe compartilhadas (CoopProgress de Rikka230, eight8pac/codevein-coop#1): teste em dois PCs.
2. Morte do host no chefe com convidado vivo (host observa até todos morrerem).
3. Equipar dons e baús para convidado (provavelmente tratamento no host semelhante ao nível), reiniciar inimigos em todo descanso.
4. Restauração de vestígios e memórias em modo cooperativo (um percorre a memória, outro observa): responder "sem sessão" só à tela de restauração; localizar espera final que trava com convidado presente.
5. Teletransporte em grupo: transição visual para convidado, Home Base, votação. Depois, limite de 3 jogadores (nativo: contagem da sessão Steam ou aceitação de entrada), Home Base juntos.
