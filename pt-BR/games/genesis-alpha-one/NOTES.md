# <a id="genesis-alpha-one--co-op-notes"></a>Genesis Alpha One — notas sobre modo cooperativo

## <a id="phase-0-triage-2026-10-25"></a>Etapa 0: triagem (2026-10-25)

### <a id="observations-sourced"></a>Observações (com fontes)
- Desenvolvedora: Radiant Worlds, distribuidora Team17, lançado em 2019. Steam app 712190.
- Motor: Unreal Engine 4 (entrevista Epic, https://www.unrealengine.com/developer-interviews/how-a-trio-of-developers-elegantly-blended-multiple-genres-to-create-first-person-shooter-ship-builder-genesis-alpha-one).
- Só um jogador. Desenvolvedores disseram não ter planos multiplayer/cooperativos (https://steamcommunity.com/app/712190/discussions/0/3809532340214341715; https://playco-opgame.com/genesis-alpha-one/).
- Sem entrada em DIRECTORY.md, games/ ou guias deste repositório. Nenhum mod cooperativo encontrado na web.

### <a id="game-identity-observed-on-owners-install-2026-10-25"></a>Identidade do jogo (instalação do usuário, 2026-10-25)
- Loja: Epic Games Store (manifesto .egstore; CatalogItemId 983b27f33cff4600990584a9ba37b271, AppName "Puma"). Pasta `Genesis_EGS`.
- Arquivos datados de 2022-07-26. Windows de 64 bits.
- `Genesis_EGS/Binaries/Win64/Genesis-Win64-Shipping.exe`, 52.022.272 bytes, SHA-256 e009335b33199dd5dddc37213823b12180076aa71b9b7e0da5f144af319d953c
- `Genesis.exe` (inicializador mínimo), SHA-256 be78b86cb93bd91e33c16b1c189cfd2ae0851feeb8752652d0c3b87633ec9fa4
- String no executável: `++UE4+Release-4.23-CL-0`, portanto Unreal Engine 4.23.
- Pak único, `Genesis_EGS-WindowsNoEditor.pak` (6,3 GB), versão 8, indicador de índice criptografado 0 e GUID de criptografia zerado: índice não criptografado (criptografia dos recursos não verificada).
- Strings: GameNetDriver, PendingNetGame, BeaconNetDriver, DemoNetDriver, ReplicatedMovement / OnRep_ReplicatedMovement, /Script/OnlineSubsystemUtils, NoOnlineSubsystem, OnlineSubsystemMcp. Rede do motor compilada. `strings` não achou `IpNetDriver` (só cvar `net.IpNetDriverUseReceiveThread`); servidor hospedado é **desconhecido**, testar em execução com `open <map>?listen`.
- Sem steam_api64.dll na versão Epic: retransmissor Steam Spacewar exigiria DLL Steamworks própria no mod.

### <a id="tools-2026-10-25"></a>Ferramentas (2026-10-25)
- UE4SS v3.0.1 (última estável), https://github.com/UE4SS-RE/RE-UE4SS/releases/tag/v3.0.1
  - UE4SS_v3.0.1.zip SHA-256 4b47d4bceddd2f561a4e395bfa00924ccfc945af576a2d0c613e6537846c57ec
  - zDEV-UE4SS_v3.0.1.zip SHA-256 af777d2af33fce4d520de35a8665e417376bcc530fec647778012ce6cdf51b2b
  - CRCs corretos. AINDA não comparados aos hashes publicados no GitHub (página inacessível nesta sessão).
- Dumper-7: só código, sem binário; commit 90d1f390d26e31a1f71d29af56c6bd2f240b7493. Exige MSVC Windows. Dump SDK/cabeçalhos do próprio UE4SS pode bastar para 4.23.

### <a id="unknowns"></a>Desconhecidos
- Se a versão distribuída mantém IpNetDriver / suporte a servidor hospedado.
- Se UE4SS suporta esta compilação.
- Issue aberta pelo usuário: https://github.com/cranebeaker/coop-anything/issues/199 (2026-10-25). Sem outras issues/PRs Genesis na listagem.

### <a id="hypotheses-unverified"></a>Hipóteses (não verificadas)
- Caminho 2, criar do zero. UE4 inclui replicação; se Blueprints/C++ não a previram, jogador 2 precisa de representante e sincronização com autoridade do host para inimigos, módulos da nave, tripulação/clones e planetas procedurais.
- Ferramentas-base: UE4SS (hooks Lua/C++, console) + SDK Dumper-7, conforme playbook/engine-families.md.
</content>
</invoke>

## <a id="phase-2-workspace-2026-10-25"></a>Etapa 2: ambiente de trabalho (2026-10-25)
- Cópia completa feita por rsync (tamanho, SHA-256 do executável e hash do último MiB do pak iguais). Original intacta.
- UE4SS v3.0.1 (UE4SS_v3.0.1.zip) extraído em `<test dir>/Genesis_EGS/Binaries/Win64/` (proxy dwmapi.dll).
- UE4SS-settings.ini (original .orig): MajorVersion=4, MinorVersion=23, ConsoleEnabled=1, GuiConsoleVisible=1, GraphicsAPI=dx11.
- Sondagem só de leitura `Mods/CoopProbe` (F7 registra classes de rede, NetDriverDefinitions, mundo/modo/personagem; F9: `open <current map>?listen`).
- Ainda não executado. Desconhece-se início sem Epic (executável contém OnlineSubsystemMcp).

## <a id="phase-3-first-runtime-probe-2026-10-25-owner-launched-the-test-copys-shipping-exe-directly"></a>Etapa 3: primeira sondagem em execução (2026-10-25, usuário iniciou o Shipping da cópia diretamente)
### <a id="observations-ue4sslog"></a>Observações (UE4SS.log)
- Cópia funciona sem Epic. UE4SS v3.0.1 conecta e encontra GUObjectArray etc. com configuração padrão, sem ajustes por jogo.
- Primeiro início: usuário relatou Fatal Error; log sobrescrito pelo segundo, causa **desconhecida**. Segundo normal.
- Classes presentes: IpNetDriver, IpConnection, NetDriver, DemoNetDriver, OnlineBeaconHost.
- `GameEngine.NetDriverDefinitions`: uma entrada, `GameNetDriver -> OnlineSubsystemSteam.SteamNetDriver` (remanescente Steam).
- Mundo inicial `/Game/Maps/GameStart_Gb`, GameMode `FirstPersonGameMode_C`, personagem `Eden_PlayerCharacter_C`. World.NetDriver ausente, independente.
- ConsoleEnablerMod: "ConsoleClass, GameViewport, or ViewportConsole is invalid" ao iniciar; registra F10 e ^ depois de entrar.
- F9 v1 falhou: `PlayerController:ConsoleCommand` gera "UObject instance is nullptr". V2 troca por `KismetSystemLibrary.ExecuteConsoleCommand`.
### <a id="hypothesis"></a>Hipótese
- `open ?listen` falharia como está: SteamNetDriver pode estar ausente no Epic; v2 troca definição em memória para IpNetDriver antes de abrir.
- Usuário relata DLC só pelo Epic (verificação de direitos, provável OnlineSubsystemMcp / argumentos de autenticação). Início direto não tem DLC.
  - Plano: viabilidade/sincronização sem DLC na cópia; para jogar, distribuir complemento UE4SS dwmapi.dll + UE4SS.dll + Mods/ na instalação Epic, iniciando pelo Epic com DLC. Nunca manipular tokens do inicializador.
  - Desconhecido: necessidade de direitos DLC iguais entre host/convidado.

## <a id="phase-3b-listen-server-works-2026-10-25"></a>Etapa 3b: servidor hospedado funciona (2026-10-25)
### <a id="observations-ue4sslog-probe-v2"></a>Observações (UE4SS.log, v2)
- Classes `OnlineSubsystemSteam.SteamNetDriver` e `SteamNetConnection` **ausentes** no Epic; definição original `GameNetDriver` não funciona.
- Após redefinir `GameNetDriver` para `/Script/OnlineSubsystemUtils.IpNetDriver` em memória e executar `open /Game/Maps/LoadGame?listen` por `KismetSystemLibrary.ExecuteConsoleCommand`: World.NetDriver = `IpNetDriver /Engine/Transient.IpNetDriver_...`, mesmos GameMode/personagem. Firewall Windows pediu permissão (socket aberto).
- Usuário em `/Game/Maps/LoadGame`, não GameStart_Gb. Reabrir recarrega mapa; preservação do progresso desconhecida.
### <a id="next"></a>Próximo
- V3: F8 entra no endereço `host.txt` (127.0.0.1 padrão), F7 registra papel, conexões, PlayerControllers e personagens; logs por instância em `Mods/CoopProbe/probe_HHMMSS.log`.
- `Lancer_fenetre.bat` em Win64 inicia segunda instância em janela para teste no mesmo PC.

## <a id="phase-3c-first-same-pc-join-attempt-failed-2026-10-25"></a>Etapa 3c: primeira entrada no mesmo PC falhou (2026-10-25)
### <a id="observations-per-instance-probe-logs"></a>Observações (logs por instância)
- Duas cópias de teste simultâneas num PC, segunda em janela pelo Lancer_fenetre.bat.
- **Teclas UE4SS disparam em todas as instâncias, com ou sem foco.** Cada F8/F9 pressionado executou em ambas: `open 127.0.0.1` do host desmontou seu servidor, F9 do cliente recriou host. Nenhuma entrada válida tentada, resultado **desconhecido**.
- Host chegou uma vez a `role: SERVER/listen, client connections: 0` (10:45:33).
- Menu em `/Game/Maps/MainMenu` (MainMenuGameMode_C, MainMenuCharacter_C).
### <a id="fix"></a>Correção
- V4: papel travado por instância (primeiro F9 vira host e ignora F8; primeiro F8 vira cliente e ignora F9).
### <a id="lesson-for-the-playbook-ue4ss-multi-instance"></a>Lição dos guias (UE4SS com várias instâncias)
- RegisterKeyBind é global entre processos no desktop; testes precisam de papel por instância (trava, argumento ou arquivo), não foco.

## <a id="phase-3d-first-successful-join-2026-10-25-same-pc-127001-probe-v4"></a>Etapa 3d: PRIMEIRA ENTRADA BEM-SUCEDIDA (2026-10-25, mesmo PC, 127.0.0.1, v4)
### <a id="observations"></a>Observações
- Host: `SERVER/listen`, 1 cliente, 2 PlayerControllers, 2 Eden_PlayerCharacter_C. FirstPersonGameMode_C criou segundo personagem.
- Cliente: `CLIENT (connected to a server)`, `/Game/Maps/LoadGame` pela rede, 2 personagens replicados, sem GameMode (correto), primeiro PlayerController sem Pawn.
- Usuário vê cliente preso no carregamento; host fica preto ao entrar convidado.
### <a id="hypotheses-unverified-1"></a>Hipóteses (não verificadas)
- Tela preta host: lógica Blueprint individual no novo personagem / PostLogin (GetPlayerController(0), transição de câmera, alvo visual) afetando controlador do host.
- Cliente espera inicialização só do servidor ou personagem possuído.
### <a id="next-1"></a>Próximo
- V5 `deep.lua`: F7 extrai todos PCs (local, personagem, alvo, transição), personagens (controlador, papel, posição), níveis e widgets na viewport. F6 interrompe transição de câmera e visualiza próprio personagem local.

## <a id="phase-3e-startup-crash-and-save-folder-finding-2026-10-25"></a>Etapa 3e: falha inicial e descoberta da pasta de salvamentos (2026-10-25)
### <a id="observations-1"></a>Observações
- Falha intermitente ao iniciar (2 de cerca de 8), "Unhandled exception", SecondsSinceStart 0, sem Lua/teclas (UE4SS.log termina após "Event loop start"). Relatórios em `%LOCALAPPDATA%\Genesis_EGS\Saved\Crashes`. Pilha com cerca de 70 quadros recursivos ntdll (+161dd4 / +1623d4) e Genesis-Win64-Shipping (+1062b02, +10636b8, +10637d7, +13a7eaa, +13ac1f4, +14ac86b, +16079e3, +19e8b91, +1c81846). Sem UE4SS.dll, PDB ou símbolos.
- Desconhece-se ocorrência sem UE4SS (testar renomeando dwmapi.dll).
- **Cópia compartilha salvamentos/configurações reais** (`%LOCALAPPDATA%\Genesis_EGS\Saved`): SaveGames/Savegame2.sav e PlayerProfile2.sav reescritos nos testes. Backup SaveGames + Config em `<test dir>/_backup_saves_20261025` com SHA-256. Regra 2 exige pasta por cópia; redirecionamento na UE4.23 distribuída desconhecido.

## <a id="phase-3f-why-the-guest-is-stuck-2026-10-25-probe-v5-deep-dump"></a>Etapa 3f: por que o convidado trava (2026-10-25, dump profundo v5)
### <a id="observations-2"></a>Observações
- Host: 2 PCs `BP_PlayerController_EdenAlpha_C` (local=true com FirstPersonHUD_C; remoto com próprio personagem). Ambos veem seu personagem. Papéis dos personagens 3 (Authority), remoto 2 (AutonomousProxy).
- Cliente: PC local `BP_PlayerController_EdenAlpha_C` possui `Eden_PlayerCharacter_C` (papel 2), HUD FirstPersonHUD_C; host como SimulatedProxy (1); outro `PlayerController` simples não local sem personagem.
- **Host tem 31 níveis `LevelStreamingDynamic` (módulos criados do salvamento); cliente, 0.** Instâncias dinâmicas não replicadas pelo UE4.
- Widgets em ambas viewports: BlueprintSubtitleWidget_C, PlayerHudWidget_C. Nenhum UserWidget de carregamento.
- F6 (StopCameraFade + SetViewTarget próprio) não limpou preto do host: não é transição PlayerCameraManager, ou não essa. `FadeAmount` retornou invólucro, não número (bug do dump).
### <a id="hypotheses"></a>Hipóteses
- Carregamento convidado espera níveis da nave nunca recebidos.
- Preto host desconhecido, talvez HUD/pós-processamento disparado na entrada.
### <a id="next-probe-v6"></a>Próximo (v6)
- `levels.lua`: F5 host grava PackageNameToLoad/WorldAsset + LevelTransform por nível em `Mods/CoopProbe/levels.txt`; F4 cliente carrega por `LevelStreamingDynamic::LoadLevelInstance` (arquivo compartilhado só teste).
- Dump também lista UserWidgets com load/fade/black/transit/screen no nome e visibilidade.

## <a id="phase-3g-ship-levels-load-on-the-guest-then-the-guest-is-kicked-2026-10-25-probe-v6"></a>Etapa 3g: níveis da nave carregam no convidado, depois ele é expulso (2026-10-25, v6)
### <a id="observations-3"></a>Observações
- Host exporta 31 dinâmicos, todos `/Game/Maps/Structure/` (GB_Bridge, hm_Divider_Glass*, hm_Corridor_Glass*, su_Greenhouse_medium, hm_Crewq_big, re_storage_sml, Re_TractorBeam, re_refinery_sml...). Pacotes `<Short>_LevelInstance_<N>`, N 32..62 em ordem; grade de 384 unidades, yaw só 0/90/180.
- Cliente: `LoadLevelInstance` válido em 31/31; depois voltou ao menu. Host com 0 conexões, PC remanescente sem personagem e personagem em 0,0,0.
- Host tem `LoadingScreen_Widget_C` fora da viewport; cliente tem dois `LoadingScreen_Widget_C`, um visibilidade 0 (Visible).
### <a id="hypothesis-unverified-matches-ue4-source-behaviour"></a>Hipótese (não verificada, corresponde ao UE4)
- Instâncias cliente recebem números próprios `_LevelInstance_<N>`; visibilidade chama `ServerUpdateLevelVisibility(<client name>)`, servidor desconhece pacote e desconecta. Atores também usam caminhos, então nomes precisam coincidir de qualquer modo.
### <a id="next-probe-v7"></a>Próximo (v7)
- Exportar nome curto host; importar com `LoadLevelInstance(..., OptionalLevelNameOverride=<host name>)` só se parâmetro existir (registrar parâmetros UFunction); listar nomes cliente após 4 s.

## <a id="phase-3h-no-level-name-override-in-423-2026-10-25"></a>Etapa 3h: sem substituição de nome na 4.23 (2026-10-25)
### <a id="observations-4"></a>Observações
- F4 v7 falhou antes de carregar: `StaticFindObject("/Script/Engine.LevelStreamingDynamic:LoadLevelInstance"):ForEachProperty` -> "UObject instance is nullptr" (UE4SS 3.0.1).
- Strings incluem `LoadLevelInstance`, `LoadLevelInstanceBySoftObjectPtr`, `_LevelInstance_`, `ServerUpdateLevelVisibility(_Validate)`, mas **não** `OptionalLevelNameOverride`; não se escolhem nomes por Blueprint/Lua na 4.23.
- V6: host 32..62; cliente já carregara próprio salvamento antes, talvez nomes já coincidissem; não registrados. Expulsão por nome não comprovada.
### <a id="next-probe-v7b"></a>Próximo (v7b)
- Importar com nomes do motor e listar nomes cliente a cada segundo por 6 s.
- `hooks.lua`: RegisterHook em ServerUpdateLevelVisibility (host vê relatos), ClientWasKicked, ClientReturnToMainMenu(WithTextReason), ClientUpdateLevelStreamingStatus, K2_OnLogout de GameModeBase.

## <a id="phase-3i-instance-names-do-match-2026-10-25-1402-probe-v7b"></a>Etapa 3i: nomes realmente coincidem (2026-10-25 14:02, v7b)
### <a id="observations-5"></a>Observações
- Primeiro carregamento por instância: `_LevelInstance_1..31`; reabertura host `?listen` gera `32..62`.
- Convidado também carregara salvamento (1..31); F4 gerou `_LevelInstance_32..62` na mesma ordem: **31 idênticos ao host**, listados em t+1 s.
- Hook `ServerUpdateLevelVisibility` também dispara no chamador (visto independente), com pacote da instância.
- Até t+6 s, nenhum RPC de visibilidade do convidado ou expulsão/menu em ambos. Estado posterior aguarda F7 do usuário.
### <a id="conclusion-so-far"></a>Conclusão até aqui
- Expulsão v6 **não** foi por nomes (ou já coincidiam também). Causa desconhecida.
- Numeração determinística por processo (contador global), que mod real pode usar/alinha.

## <a id="phase-3j-guest-stays-connected-with-the-ship-loaded-but-invisible-2026-10-25-1405"></a>Etapa 3j: convidado continua conectado com nave carregada, mas invisível (2026-10-25 14:05)
### <a id="observations-guest-f7-after-f4-import"></a>Observações (F7 convidado após F4)
- Ainda `CLIENT (connected to a server)`, possui personagem, StreamingLevels 31 com nomes iguais.
- Sem chamada `ServerUpdateLevelVisibility` após importar (31 anteriores eram do próprio salvamento antes de entrar): níveis importados nunca se tornaram visíveis.
- Dois `LoadingScreen_Widget_C`, um visível (0): carregamento interminável.
- Personagem próprio em 42,-155,319, visto no host em 43,-310,98 (posição não convergiu).
### <a id="next-probe-v8"></a>Próximo (v8)
- F3 convidado registra IsLevelLoaded/IsLevelVisible/ShouldBeLoaded, chama SetShouldBeLoaded/SetShouldBeVisible(true) em todos e oculta/remove LoadingScreen_Widget_C.
- Perguntar se host volta ao recuperar foco (renderização sem foco?).

## <a id="phase-3k-ship-visible-on-the-guest-both-screens-black-2026-10-25-1410-probe-v8"></a>Etapa 3k: nave visível no convidado, ambas as telas pretas (2026-10-25 14:10, v8)
### <a id="observations-6"></a>Observações
- Após F4, 31/31 carregados, visíveis e ShouldBeLoaded antes de F3; ausência de RPC v7b pode ser limitação do hook ou chegada posterior, desconhecido.
- F3 ocultou/removeu ambos `LoadingScreen_Widget_C` (visibilidades 2 e 0). Convidado agora **preto**, não carregamento. Host preto com ou sem foco.
- Convidado conectado, PC local possui personagem.
### <a id="derived"></a>Dedução
- Preto comum fica sob carregamento. Provável transição de câmera: F6 usava `StopCameraFade`, que na UE4.23 define FadeAmount para *alvo* FadeAlpha.Y, não limpando destino preto.
### <a id="next-probe-v8b"></a>Próximo (v8b)
- F6 chama `PlayerCameraManager:SetManualCameraFade(0, black, false)` no controlador local de cada janela.

## <a id="phase-3l-not-a-camera-fade-2026-10-25-1417-probe-v8b"></a>Etapa 3l: não é transição de câmera (2026-10-25 14:17, v8b)
### <a id="observations-7"></a>Observações
- `SetManualCameraFade(0)` retornou sucesso em ambas, que continuam pretas. Alvos são personagens próprios.
- Host F7: 1 conexão, posições estáveis. Convidado conectado, 31 níveis visíveis, carregamento removido.
### <a id="hypotheses-open"></a>Hipóteses (abertas)
- Valor escalar global de MaterialParameterCollection (escurecimento) definido pela entrada do novo jogador, afetando todas as vistas.
- Câmera do personagem desativada ou escurecimento em volume/câmera de pós-processamento.
### <a id="next-probe-v9"></a>Próximo (v9)
- F2: MaterialParameterCollection, escalares atuais/padrão por KismetMaterialLibrary.GetScalarParameterValue, CameraComponent ativo/peso pós-processamento, posição de câmera, PostProcessVolumes, bHidden do personagem, visibilidade/opacidade PlayerHudWidget.

## <a id="phase-3m-full-black-no-ui-at-all-2026-10-25-1435-probe-v9"></a>Etapa 3m: preto completo, nenhuma interface (2026-10-25 14:35, v9)
### <a id="observations-8"></a>Observações
- Captura do usuário: ambas completamente pretas, nada desenhado.
- F2 em ambas: câmera na altura dos olhos (host -190,373,178; convidado 42,-155,399), personagem visível, PlayerHudWidget visibilidade 4 (SelfHitTestInvisible), opacidade 1. Nenhum MaterialParameterCollection, CameraComponent ou PostProcessVolume listado (FindAllOf vazio ou laços falhando silenciosamente, desconhecido).
- Strings incluem `SetEnableWorldRendering` / `GetEnableWorldRendering` (UGameplayStatics) e `SetSuppressViewportTransitionMessage`.
### <a id="hypothesis-1"></a>Hipótese
- Carregamento chama `UGameplayStatics::SetEnableWorldRendering(false)` durante construção; convidado o redispara no host (PostLogin) e cliente, sem reativar porque carregamento nunca termina para dois.
### <a id="next-probe-v10"></a>Próximo (v10)
- F2 registra GetEnableWorldRendering, F1 chama SetEnableWorldRendering(true) local.
- Hooks GameplayStatics.SetEnableWorldRendering (quem/valor), GameModeBase.K2_PostLogin.

## <a id="phase-3n-world-rendering-is-on-2026-10-25-1440-probe-v10"></a>Etapa 3n: renderização do mundo está ligada (2026-10-25 14:40, v10)
### <a id="observations-9"></a>Observações
- Ambas: `GetEnableWorldRendering = true` no preto. F1 `SetEnableWorldRendering(true)` não muda. Hook não viu chamada do jogo, só nossa.
- Hook `GameModeBase:K2_PostLogin` registrado, nunca disparou na entrada (BlueprintImplementableEvent talvez não implementado ou outro caminho necessário, desconhecido).
### <a id="hypothesis-2"></a>Hipótese
- Quadro renderizado, mas coberto por efeito combinável (capacete/visor, morte/clone) na câmera/gerenciador, ou exposição.
### <a id="next-probe-v11"></a>Próximo (v11)
- F1: `ShowFlag.PostProcessing 0`, `r.DefaultFeature.AutoExposure 0`, `r.TonemapperFilm 0`; listar CameraComponent (dono, ativo, PostProcessBlendWeight, quantidade de efeitos), zerar pesos.

## <a id="phase-3o-not-post-processing-either-2026-10-25-1445-probe-v11"></a>Etapa 3o: também não é pós-processamento (2026-10-25 14:45, v11)
### <a id="observations-10"></a>Observações
- Controle só host, F9 e F1: imagem mais clara, comandos alcançam renderizador.
- Com dois: F1 não altera, preto total.
- Câmeras: `FirstPersonCamera` do personagem (ativa), `BuilderCharacter_C`, `BP_PlayerRemoteCamera_C` (só host), `CameraActor`s (um host, dois convidado), três `CineCameraActor`s inativas e muitas de terminais (BP_StorageTerminal, BP_GreenhouseTerminal2, BP_HealthStation, BP_GalaxyTerminal, BP_TractorBeamTerminal, BP_RefineryTerminal, StandKeyboardWorkstationPlayer...). Nenhuma com efeitos de pós-processamento combináveis.
- PlayerCameraManager continua no personagem próprio (dumps anteriores).
### <a id="ruled-out"></a>Descartados
- Transição de câmera, interruptor de renderização, sobreposição pós-processada, widget de carregamento, alvo errado.
### <a id="next-probe-v12"></a>Próximo (v12)
- Registrar ações na entrada: KismetSystemLibrary.ExecuteConsoleCommand, PlayerController.ConsoleCommand, StartCameraFade, ClientSetCameraFade, (Client)SetCinematicMode, SetViewTargetWithBlend, ClientSetViewTarget, SetGamePaused, GameUserSettings.ApplySettings/SetScreenResolution, UserWidget.AddToViewport.

## <a id="phase-3p-probe-v12-crashed-the-game-2026-10-25-1451"></a>Etapa 3p: v12 derrubou o jogo (2026-10-25 14:51)
### <a id="observations-11"></a>Observações
- Falhou ao chegar ao menu. Console UE4SS: "Tried to execute UFunction::FuncPtr hook but there was no function map entry for UFunction: 0000000000000000 None. No original function to execute. Executing ProcessInternal instead.", depois Object_ExecuteUbergraph / ProcessInternal.
- Últimas chamadas: AddToViewport StartGame_C (z=1), AddToViewport LoginFailedWidget_C (z=15). Cópia fora do Epic mostra falha de login.
- UE4SS informou "Registered native hook" para novas funções (GameUserSettings.ApplySettings/SetScreenResolution, UserWidget.AddToViewport), "script hook" para K2_OnLogout.
### <a id="derived-unverified"></a>Dedução (não verificada)
- Um hook nativo alterou função intermediária compartilhada por otimização de código idêntico MSVC com outra UFunction; esta rodou sem entrada no mapa UE4SS e falhou. Hook desconhecido.
### <a id="lesson-for-the-playbook-ue4ss-301-on-shipping-ue4-builds"></a>Lição (UE4SS 3.0.1 em versões distribuídas UE4)
- Preferir RegisterBeginPlayPostHook / NotifyOnNewObject / RegisterProcessConsoleExecPreHook e hooks de scripts BP a muitas chamadas RegisterHook nativas; adicionar nativos um a um.
### <a id="next-probe-v13"></a>Próximo (v13)
- Voltar aos hooks v10 estáveis com observadores seguros ativados por F9/F8: BeginPlay de todo ator (classe/nome), novos UserWidgets, todo comando console.
- Primeiro envio v13 acrescentava código após `return M` em hooks.lua, gerando "hooks.lua:23: <eof> expected near 'M'"; mod inteiro não carregou, teste sem log. Corrigido; scripts passam por Lua 5.4 (`tools/check_lua.sh`) antes da cópia.

## <a id="phase-3q-what-the-host-spawns-when-the-guest-arrives-2026-10-25-1508-probe-v13"></a>Etapa 3q: o que o host cria ao chegar convidado (2026-10-25 15:08, v13)
### <a id="observations-12"></a>Observações
- Host no segundo da entrada (15:08:08): só BeginPlays, sem comando/widget novo: Genesis_PlayerState_C, CameraActor, PlayerCameraManager, BP_PlayerController_EdenAlpha_C, **BP_PlayerRemoteCamera_C, BP_PlayerInventoryAvatar_C, BuilderCharacter_C**, Eden_PlayerCharacter_C.
- Conjunto próprio do host, criado por reabertura `?listen`, tem os mesmos auxiliares BP_PlayerRemoteCamera_C, BP_PlayerInventoryAvatar_C, BuilderCharacter_C. Cada jogador recebe um de cada, mas código individual provavelmente procura instância única.
- Convidado recebe módulos replicados (`BP_Bld_*`), tripulação (`CrewCharacterClass_C` com `Crew_HealthStatus_C`), robôs (`Rob1_Robot_C`), portas, armas (pistola, barreira de energia, multikit, biosucker, escopeta de energia, sentinela), BP_Galaxy_C, Genesis_GameState_C/PlayerState_C, BP_MiniMapPlayer, PlayerSpectator_C. Nada registrado depois de 15:08:09.
- Sufixos de índice dos objetos UE diminuem: novos têm números menores.
### <a id="hypothesis-3"></a>Hipótese
- Auxiliar duplicado do convidado, provável BP_PlayerRemoteCamera_C, assume vista/alvo do host.
### <a id="next-probe-v14"></a>Próximo (v14)
- F1 só host: listar auxiliares com dono/instigador/posição; destruir duplicado mais novo de BP_PlayerRemoteCamera_C, BuilderCharacter_C, BP_PlayerInventoryAvatar_C e CameraActor, um por tecla.

## <a id="phase-3r-duplicate-helper-actors-are-not-the-cause-2026-10-25-1514-probe-v14"></a>Etapa 3r: auxiliares duplicados não são causa (2026-10-25 15:14, v14)
### <a id="observations-13"></a>Observações
- Auxiliares por jogador, Instigator próprio Eden_PlayerCharacter_C, sem dono: BP_PlayerRemoteCamera_C e BP_PlayerInventoryAvatar_C em (0,0,600000), BuilderCharacter_C em (0,0,-199900). Cada PlayerCameraManager possui CameraActor em 0,0,0. Três CineCameraActors (_0, _1, _3).
- Destruir BP_PlayerRemoteCamera_C e BuilderCharacter_C convidado (F1 host duas vezes ou mais) não recuperou imagem.
### <a id="next-probe-v15"></a>Próximo (v15)
- F1 ambas: capturas internas (`shot`, `HighResShot 1`) para distinguir quadro preto de quadro normal não apresentado.

## <a id="phase-3s-the-engine-still-renders-the-ship-while-the-window-is-black-2026-10-25-1518-probe-v15"></a>Etapa 3s: motor renderiza nave com janela preta (2026-10-25 15:18, v15)
### <a id="observations-14"></a>Observações
- F1 ambas pretas: `HighResShot 1` gravou `HighresScreenshot00000.png`, 1234x694, corredor iluminado/porta/mira normais. Mesmo nome nas duas, origem desconhecida.
- `shot` (buffer de apresentação) não gravou `ScreenShot*.png`.
### <a id="derived-unverified-1"></a>Deduções (não verificadas)
- Cena renderiza; falha é apresentar viewport à janela (desenho/apresentação parou ou algo cobre no Slate, como carregamento MoviePlayer).
- Se `shot` não grava no individual, ausência não prova nada; se grava, viewport não desenhada no preto.
### <a id="next-probe-v15b"></a>Próximo (v15b)
- F1: host captura agora, cliente após 4 s (números diferentes). Usuário faz controle individual antes.

## <a id="phase-3t-the-host-renders-fine-behind-the-black-opening-the-map-brings-the-image-back-2026-10-25-1522-probe-v15b"></a>Etapa 3t: host renderiza atrás do preto; mapa recupera imagem (2026-10-25 15:22, v15b)
### <a id="observations-15"></a>Observações
- `HighResShot 1` (só cena, sem UMG): host sozinho 15:22:12 e preto 15:22:52 mostram **mesmo corredor normal**, 1234x694. Convidado 15:22:56, 1280x720: mundo preto quase vazio com segmento de porta flutuante (níveis não importados nesta execução).
- `shot` não gravou nem no controle: sem informação nesta compilação.
- Usuário: abrir mapa no host recupera imagem. Log: `BuilderModeWidget_C`, `BP_ShipCamera_C`, `BP_MapSensedAlienRadar_C` criados (mapa é modo construtor/nave).
- Após `?listen`, jogo chamou `slomo 1` dez vezes.
- Imagem: https://github.com/Blackouest/genesis-alpha-one-coop/blob/main/docs/img/2026-10-25_engine-shots_host-solo_host-black_guest.png
### <a id="derived-1"></a>Dedução
- Cena host renderiza; preto por interface sobreposta (HighResShot exclui UMG). Provável imagem preta integral no HUD, ativada na entrada pela lógica individual e desativada pelo mapa/construtor.
### <a id="next-probe-v16"></a>Próximo (v16)
- F1 lista Images/Borders visíveis cuja cadeia chega à viewport, com visibilidade, opacidade/cor; marca opacos quase pretos. F1 novamente os oculta.

## <a id="phase-3u-black-screen-solved---fadeoutborder-in-the-hud-2026-10-25-1530-probe-v16"></a>Etapa 3u: TELA PRETA RESOLVIDA - `FadeOutBorder` do HUD (2026-10-25 15:30, v16)
### <a id="observations-16"></a>Observações
- F1 ambas: 128 Images/Borders visíveis em widgets da viewport. Único preto integral: **`Border FadeOutBorder` em `PlayerHudWidget_C`**, visibilidade 4, opacidade 1, cor 0,0,0,1. Outros 17 são fundos escuros normais (PlayerHealthWidget, PlayerCurrentWeapon, AlienMotionTracker, CrewWeaponSelectionItem, TalkScreen, TutorialWarning, ControllerButtonHintWidget, dicas LoadingScreen).
- Após F1 duas vezes, **ambas mostram jogo**. Host primeira pessoa normal. Convidado vê mundo atrás de "CHARGEMENT" (LoadingScreen_Widget_C dentro do HUD); **arma host move com ele**, comprovando replicação, mas sem corpo host (malha só primeira pessoa).
- LoadingScreen_Widget_C dentro de PlayerHudWidget_C nas duas máquinas.
- Imagem: https://github.com/Blackouest/genesis-alpha-one-coop/blob/main/docs/img/2026-10-25_both-windows-after-hiding-FadeOutBorder.jpg
### <a id="derived-2"></a>Deduções
- Transição individual (`FadeOutBorder`) permanece preta na chegada de segundo, em ambos. Abrir mapa/construtor limpa também, segundo usuário.
- Remotos precisam de corpo em terceira pessoa; malha do jogador só primeira pessoa.
### <a id="next-probe-v17-automatic-flow"></a>Próximo (v17, fluxo automático)
- Host só F9, exporta níveis após 6 s.
- Convidado só F8; conectado com personagem, importa (+4 s), remove carregamento (+6 s).
- Ambos: ocultar FadeOutBorder se preto por 6 s. F1 só o oculta agora.

## <a id="phase-3v-v17-automatic-flow-ran-but-the-fade-watch-never-fired-2026-10-25-1540"></a>Etapa 3v: fluxo automático v17 executou, mas observador não disparou (2026-10-25 15:40)
### <a id="observations-17"></a>Observações
- Host F9 exportou 31 em +6 s. Convidado F8 conectou com personagem em 2 s, importou 31/31 em +4 s, removeu 3 LoadingScreen_Widget em +10 s. Ambos pretos, sem linha de ocultação FadeOutBorder.
- Mapa ainda limpa host, nada limpa convidado.
- Várias cópias PlayerHudWidget/LoadingScreen de carregamentos anteriores simultâneas.
### <a id="derived-3"></a>Dedução
- Observador zerava contador ao encontrar cópia não preta; nunca chegava a 3 atualizações (bug v17).
### <a id="next-probe-v17b"></a>Próximo (v17b)
- Contar qualquer cópia preta, ocultar todas após 3 verificações; registrar quantidade de cópias/pretas nas mudanças.

## <a id="phase-3w-both-windows-render-the-ship-automatically-2026-10-25-1600-probe-v17b"></a>Etapa 3w: AMBAS AS JANELAS RENDERIZAM A NAVE automaticamente (2026-10-25 16:00, v17b)
### <a id="observations-18"></a>Observações
- 3 cópias FadeOutBorder por lado. Host sem preto até entrada 16:00:10, então 1 preta, oculta 16:00:14. Convidado 1 preta desde conexão 16:00:11, oculta 16:00:15. **Confirma FadeOutBorder como única causa**, só ele ocultado.
- Captura: host com arma/dicas, convidado interior iluminado com módulos importados/dicas. https://github.com/Blackouest/genesis-alpha-one-coop/blob/main/docs/img/2026-10-25_both-windows-render-ship-v17b.jpg
- Host funciona. Convidado surge alto, só gira câmera; sem movimento, escolha de armas ou mapa.
- Dumps anteriores: z=319 no convidado, z=98 na vista host.
### <a id="hypothesis-4"></a>Hipótese
- Fluxo individual desativa entrada/movimento até concluir carregamento, evento nunca executado no convidado.
### <a id="next-probe-v18"></a>Próximo (v18)
- F2 extrai PC local (entrada mover/olhar ignorada, cursor, variáveis BP relevantes), personagem (posição, velocidade, InputEnabled, papel, CharacterMovement modo/gravidade/velocidade/ativo, BP) e posições de todos. Segunda tecla: ResetIgnoreInputFlags, SetIgnoreMove/LookInput(false), EnableInput, SetMovementMode(Walking), SetInputMode_GameOnly.

## <a id="phase-3x-the-guests-player-character-is-never-initialized-2026-10-25-1606-probe-v18"></a>Etapa 3x: personagem convidado nunca inicializado (2026-10-25 16:06, v18)
### <a id="observations-f2-dump"></a>Observações (F2)
| | Personagem host (servidor) | Personagem convidado (convidado) |
|---|---|---|
| IsPlayerInitialized | true | **false** |
| BlockActionFPSPlayerInput | false | **true** |
| PlayerMovementSpeed | 1400 | **0** |
| CharacterMovement | modo 1 (Walking), ativo, MaxWalkSpeed 1400 | **modo 3 (Falling), inativo**, MaxWalkSpeed 1200 |
| ReplicatedMovementMode | 1 | 0 |
| posição | -189,373,98 | 42,-155,319 (host vê 43,-310,98) |
- Entrada mover/olhar não ignorada nos dois PlayerControllers; cursor desligado.
- Correções genéricas (ResetIgnoreInputFlags, SetIgnoreMove/LookInput(false), EnableInput, SetMovementMode(Walking), SetInputMode_GameOnly) executadas; convidado ainda não move, troca armas ou abre mapa.
- Usuário: convidado só vê parte da nave; partes ausentes desconhecidas.
### <a id="next-probe-v19"></a>Próximo (v19)
- F2 lista funções de inicialização em Eden_PlayerCharacter_C e BP_PlayerController_EdenAlpha_C; estado de todos, incluindo cópia convidada host.
- F2 novamente: em todo não inicializado/não simulado, copiar valores (IsPlayerInitialized, BlockActionFPSPlayerInput=false, PlayerMovementSpeed, ativar CharacterMovement, MaxWalkSpeed, Walking).

## <a id="phase-3y-guest-can-move-2026-10-25-1617-probe-v19"></a>Etapa 3y: CONVIDADO CONSEGUE ANDAR (2026-10-25 16:17, v19)
### <a id="observations-19"></a>Observações
- Cópia convidada no host (papel 3) também sem inicialização: init=false, block=true, velocidade 0, CharacterMovement inativo. Próprio convidado (2) igual, modo 3. Host visto pelo convidado (1) também init=false, mas proxy simulado não alterado.
- F2 duas vezes definiu em ambos IsPlayerInitialized=true, BlockActionFPSPlayerInput=false, PlayerMovementSpeed=1400, CharacterMovement ativo, MaxWalkSpeed 1400, Walking.
- Usuário: **convidado anda** na nave; **colisão entre jogadores funciona**; host vê convidado. Porta parece fechada no convidado, mas atravessável (estado não replicado, colisão do servidor prevalece).
- Ainda sem mapa, coleta de arma (HUD de seleção aparece), armários/telas.
- Funções BP de Eden_PlayerCharacter_C: InitializePlayer, OnLevelLoadedInitializePlayer, SetPlayerInitValues, InitWeaponsFromSave, InitializeFlashlight, InitializePostProcessess, InitializeAlienAbility, SpawnBuilderCharacter, SpawnPlayerRemoteCamera, SpawnPlayerInventoryAvatar, SetLoadedOxygen, SetTutorialAfterLoad, OnLoadingFinishedShowConfirm, PossessFinished, HolsterAndBlockPlayerWeaponSelection, InitializePlayerAfterBuildingMenu, OnGenesisInitiated, TeleportPlayerToRandomStartPosition... BP_PlayerController_EdenAlpha_C: SpawnMapMarker, EnableMouseCursor.
- Imagem: https://github.com/Blackouest/genesis-alpha-one-coop/blob/main/docs/img/2026-10-25_guest-moves-v19.jpg
### <a id="derived-4"></a>Dedução
- Movimento funciona pela replicação CharacterMovement UE (previsão cliente + ServerMove). Demais ações executam Blueprint individual local sem autoridade: armas, possuir BuilderCharacter para mapa, terminais. Precisam executar no host para o convidado.
### <a id="plan-next-session"></a>Plano (próxima sessão)
1. Chamar inicialização própria (`OnLevelLoadedInitializePlayer` / `InitializePlayer`, `InitWeaponsFromSave`) no host para o convidado, sem copiar valores.
2. Canal convidado-host sem RPC novo: RPC servidor confiável com string (candidato `PlayerController:ServerChangeName`, hook host); retorno por `ClientMessage`.
3. Encaminhar eventos `InpActEvt_*` BP para executar no personagem do remetente no host; tratar GetPlayerController(0) / GetPlayerCharacter(0) por janela de personificação (relato Doors of Trithius).
4. Corpo remoto de terceira pessoa, portas e partes ausentes da nave.

## <a id="phase-4a-guest-actions-step-1-2026-10-25-probe-v20"></a>Etapa 4a: ações do convidado, passo 1 (2026-10-25, v20)
### <a id="plan"></a>Plano
- Movimento funciona, demais ações Blueprint locais sem autoridade.
- Canal com RPCs existentes: convidado -> host `PlayerController.ServerChangeName("COOP|...")`, hook host; host -> convidado `PlayerController.ClientMessage("COOP|...")`, hook convidado. F6 envia ping, host precisa responder pong.
- F6 também intercepta todos `InpActEvt_*` em Eden_PlayerCharacter_C, BP_PlayerController_EdenAlpha_C e BuilderCharacter_C, revelando ações das teclas (arma, mapa, usar).
- Inicialização automática: host inicializa cópia convidada após reabertura; convidado seu personagem após revelar (`initfix.apply`).

## <a id="phase-4b-channel-works-guest-actions-identified-2026-10-25-1640-probe-v20"></a>Etapa 4b: canal funciona; ações identificadas (2026-10-25 16:40, v20)
### <a id="observations-20"></a>Observações
- Inicialização em ambos (host 16:39:39, convidado 16:39:50).
- **Canal bidirecional:** `ServerChangeName("COOP|ping 16:40:10")` chegou ao hook host pelo BP_PlayerController_EdenAlpha_C convidado; `ClientMessage("COOP|pong 16:40:10")` retornou no mesmo segundo. Sem falha nos dois hooks nativos.
- 154 eventos `InpActEvt_*` de 486 funções interceptados nas três classes (`/Game/EdenAlpha1/Blueprints/Player/...`).
- Teclas convidado disparam localmente `InpActEvt_PC_SelectWeapon_1_..._50/_51` (pressionar/soltar), `PC_SelectWeapon_2_..._48/_49`, `PC_ActivateBuilderMode_..._23` (TAB), movimento e frequentes `ChangeInputType_90` / `KeyboardAnyKeyConfirm_82`. No host, TAB também `BuilderCharacter_C.InpActEvt_PC_ActivateBuilderMode_18` (possui construtor); `PC_Fire_25` visto.
### <a id="next-probe-v21"></a>Próximo (v21)
- Convidado encaminha ações do próprio personagem, salvo mover/olhar/saltar/agachar/correr/ruído de tipo de entrada, como `act|<event name>`; host chama evento no personagem remetente com FKey vazio. Hooks automáticos.

## <a id="phase-4c-forwarding-works-end-to-end-actions-do-nothing-yet-2026-10-25-1828-probe-v21"></a>Etapa 4c: encaminhamento ponta a ponta funciona, ações ainda sem efeito (2026-10-25 18:28, v21)
### <a id="observations-21"></a>Observações
- Todas chegaram e executaram no personagem convidado sem erro Lua: `PC_SelectWeapon_1/2` (pressionar/soltar), `PC_ActivateBuilderMode_23` (TAB), `PC_HoldUse_12/13`, `PC_Use_19/20`, `PC_Multitool_43`.
- Usuário: HUD de seleção aparece **no host e convidado**, sem troca. Mapa TAB, PDA T, armários/telas sem efeito.
### <a id="derived-5"></a>Deduções
- Blueprint encaminhado usa auxiliares jogador-0 para interface (host mostra seleção alheia).
- Cópia convidada host sem equipamento: inicialização só copiou indicadores, `InitWeaponsFromSave` nunca rodou.
### <a id="next-probe-v22"></a>Próximo (v22)
- F2 por personagem: armas/inventário/equipamento/construtor/ferramenta/posição/item/lanterna/hud/oxigênio (valores, nomes, tamanhos). F2 host novamente chama `InitWeaponsFromSave` convidado, extrai outra vez.

## <a id="phase-4d-the-guest-has-no-weapons-and-shares-the-hosts-hud-2026-10-25-1839-probe-v22"></a>Etapa 4d: convidado sem armas, HUD compartilhado com host (2026-10-25 18:39, v22)
### <a id="observations-host-side-before-and-after-forwarding-the-guests-weapon-keys"></a>Observações (host antes/depois das teclas convidadas)
- Host próprio: WeaponSlot1=BP_WeaponPistol_C, WeaponSlot2=BP_WeaponPowerShotgun_C, NoWeapon=BP_NoWeapon_C, Multitool=BP_Weapon_Multikit_C, CurrentWeaponInUse=BP_NoWeapon_C.
- Cópia convidada: **WeaponSlot1/2, NoWeapon, Multitool, CurrentWeaponInUse ausentes**. BuilderCharacterOwner e PlayerInventoryAvatar próprios.
- **Ambos apontam ao mesmo `PlayerHud` (PlayerHudWidget_C_2147482146)**, do host. No convidado, ambos também usam seu HUD único. Todo caminho `PlayerHud` atua na interface local.
- `InitWeaponsFromSave` na cópia host não deu armas; pcall mostrou valor de função, talvez a chamada tenha falhado, desconhecido.
- Após `PC_SelectWeapon_1/2` e `PC_EquipSentryGun` encaminhados, personagem **host** mudou (CurrentWeaponInUse Pistol, IsWeaponEquiped true, CurrentInventorySlot 1, LastSelectedSlot 2); convidado vazio. Desconhece-se se usuário também pressionou no host, mas padrão corresponde a jogador-0/HUD comum.
### <a id="derived-6"></a>Deduções
- Armas convidadas precisam existir no host: criar quatro atores das mesmas classes, propriedade do personagem, ou executar inicialização com ele como jogador 0.
- Ações precisam de personificação: durante execução host, buscas jogador-0 e referência HUD devem resolver convidado.

## <a id="phase-4e-guest-weapons-damage-health-and-death-2026-10-2526-probes-v23-v37"></a>Etapa 4e: armas, dano, vida e morte do convidado (2026-10-25/26, v23-v37)
Registro completo em docs/NOTES.md do projeto. Principais descobertas:
- UE4SS 3.0.1 ocultava erros de chamadas Blueprint; experimental UE4SS_v3.0.1-1183-gcdbc0b66 fornece erros legíveis e `ForEachProperty` funcional.
- Mensagens sem RPC novo: convidado -> host `PlayerController.ServerChangeName("COOP|...")` com hook host; retorno `ClientMessage("COOP|...")` com hook convidado.
- Armas por `AddEquipmentToInventory(WeaponID, Slot)` no personagem convidado, host e cliente. `InpActEvt_*` encaminhados miram com rotação convidada e causam dano real.
- Fire local não chega a `AttemptToUpdatePrimaryAction`; `PlayerShootsWeapon()` próprio mostra projétil/impacto. Munição confere `GetPlayerCharacter(0).PlayerState.Ammunition`, então host envia reserva.
- Todo feedback Blueprint convidado no host visa jogador 0: tremor (`GetPlayerController(0).ClientPlayCameraShake`), pós-processamento de dano sem vínculo, transições HUD, dicas, promoção, `BP_PromotedCaptain` termina com `GetPlayerCharacter(0).OnPromotionFinished`. Host intercepta/desfaz/redireciona; convidado reproduz localmente.
- Morte convidada fica atrás de DoOnce (`Temp_bool_IsClosed_Variable_6`), reaberto só no fim da ressurreição original.
