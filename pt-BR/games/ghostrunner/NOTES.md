# <a id="ghostrunner--co-op-attempt-notes"></a>Ghostrunner: notas da tentativa de modo cooperativo

Sessão 2026-10-21. Guias: coop-anything.
Estado: **triagem e pesquisa concluídas; hook validado; sondagem do código de rede concluída. Ainda sem modo cooperativo.**
Publicado: PR em rascunho #107 / issue de indicação de trabalho #108 no repositório de origem.

Versão curta: não existe mod cooperativo de Ghostrunner em lugar algum. A compilação usa Unreal Engine 4.26, e **UE4SS v3.0.1 injeta e executa Lua nela** (comprovado). As classes de rede do motor (`IpNetDriver`, `SteamNetDriver`, `EOSNetDriver`) estão presentes e carregadas, mas um servidor hospedado pelo jogador não inicia só com comando de console. Tudo aqui exige implementação do zero; nenhum atalho barato funcionou.

---

## <a id="0-game-identity-per-agentsmd-rule-5"></a>0. Identidade do jogo (regra 5 de AGENTS.md)

### <a id="observed"></a>OBSERVADO

- **Ghostrunner** (2020, One More Level / 505 Games). **Versão baseada em GOG.** Instalação: `<game dir>`. Evidências GOG: `goggame-1443435189.info`/`.hashdb`, `gog.ico`; IDs de aplicativos vistos: 1443435189, 1519337965, 1596358146, 1797774287, 2009792833, 2072875151, 1957528513.
- **A cópia em teste é uma distribuição de terceiros (pirata)**, informado pela pessoa que testou em 2026-10-21. Consequência arquitetural: não se pode presumir autenticação por serviço de plataforma (EOS, GOG Galaxy, Steamworks), e nenhum é utilizado. Transporte por retransmissor próprio. Nenhum trabalho com DRM, assinatura de pak ou proteção contra adulteração é feito neste projeto.
- Instalação de 34,28 GB / 117 arquivos avulsos. Pak de conteúdo `Ghostrunner\Content\Paks\Ghostrunner-WindowsNoEditor.pak` = 35.845.557.950 B, mais pak de sobreposição russo (179.256.121 B). Dois arquivos `.sig` (2.188.368 B cada) são **idênticos byte a byte** (SHA-256 `5F7B1F43…FCB77B24`): não são assinaturas genuínas por pak.
- Rodapé do pak: assinatura `0x5A6F12E1`, **versão 11**, offset do índice 35.842.217.633, tamanho 737.712. Após o ponto de montagem, índice **opaco (criptografado/comprimido)**: `Config/*.ini` preparado e nomes de recursos não podem ser lidos estaticamente.
- Inicializador `Ghostrunner.exe` = `BootstrapPackagedGame` padrão UE4, 540.672 B, sem recurso de versão, SHA-256 `487FEA621B582CE57E998ADAC5BB4641B92BA2C75193DA6C180E3A51DA52D560`.
- Binário real `Ghostrunner\Binaries\Win64\Ghostrunner-Win64-Shipping.exe`, **88.627.712 B**, SHA-256 **`8AE0977F794CC3A21EF37550707A048069C81FA2A595B6FD8188CBB06FA94BD4`**. PE x64, TimeDateStamp 2022-06-23 14:24:11Z.
- **Motor: Unreal Engine 4.26**, fork personalizado One More Level. `FEngineVersion` UTF-16LE no executável = `++UE4+Release-4.26` e `++UE4+Release-4.26-CL-0`. Confirmado em execução pelo Patternsleuth do UE4SS: `[PS] Found EngineVersion: 4.26`. Raiz do código-fonte incorporada nas strings: `<engine source root>\Engine\Source\...`.
- Plugins: somente `DLSS`, `OnlineSubsystemGOG`. DLLs incluídas: `EOSSDK-Win64-Shipping.dll` 23.390.688 B, `Galaxy64.dll` 15.274.496 B (GOG), `steam_api64.dll` 290.768 B, `CgSDK.x64_*`, `turbojpeg.dll`, `xaudio2_9redist.dll`, `nvngx_dlss.dll`.
- Sem executável de servidor dedicado. Sem arquivos ou strings de marca EasyAntiCheat/BattlEye. Código EOS *AntiCheatClient* vinculado, mas inativo ("dummy client" segundo strings dos logs do SDK).
- Pontos de integração graváveis avulsos (fora do pak) existentes em disco: `Content\JsonFiles\Bindings.json` (entrada personalizada: tabelas `bindPC` / `bindPAD`, um conjunto por família de dispositivo, **sem índice de jogador**), `Content\JsonFiles\Platforms\OnlineSubsystem\FOnlineSubsystemData.json` = `{"defaultOnlineSubsystemName": "GOG"}`, `Config\Automation\Presets\{BaseTest,GraplingHook}.json` (predefinições de desenvolvimento UTF-16LE), `Content\JsonFiles\Debug.json`.

### <a id="derived"></a>DEDUZIDO

- Pak opaco e `.sig` fictício: **edição de recursos/Blueprints está efetivamente fechada**; todo trabalho cooperativo precisa ocorrer em execução (carregador, sobreposição de configuração, hooks), o que também significa nunca distribuir arquivos do jogo.
- GOG + Galaxy significa ausência de salas/P2P Steamworks pela loja; transporte precisa ser retransmissor próprio ou SDK EOS/Galaxy incluído.

---

## <a id="1-existing-work--nothing-to-revive"></a>1. Trabalhos existentes: nada para retomar

**Não existe mod cooperativo ou multiplayer para Ghostrunner (2020) nem Ghostrunner 2.**

Pesquisados (2026-10-21): núcleo Ghostrunner do Nexus Mods (32 mods: skins de espada, desbloqueador DLSS, ReShade, salvamento, trainer), GameBanana (1 mod: skin de guaxinim), ModDB (**0 mods**), repositórios+código GitHub (620 repositórios "ghostrunner"; `ghostrunner coop` → 1 jogo estudantil de 2017 sem relação), fóruns Steam (só pedidos), Reddit r/GhostRunner (pedidos), YouTube, web geral, lista de configurações personalizadas UE4SS (sem pasta Ghostrunner). Oficial: suporte 505 Games diz "Ghostrunner is a single player game with a campaign"; appdetails Steam de 1139900 e 2144740 não têm categoria multiplayer. Ghostrunner 2 é UE 4.27, não UE5, e também não tem cooperação (RogueRunner.exe é modo de um jogador).

Comunidade de mods existente (comprova profundidade de scripts no motor; tudo baseado em .pak/LogicMods):
- `Dmgvol/Ghostrunner-Mods`: Trainer, WaveMode (cria ondas/drones/lasers), Movement Mod, Collision Visualizer, Unlocker, randomizador GhostrunnerRNG, **Ghost Mod**.
- **Ghost Mod reproduz sua partida anterior como segundo personagem visível e animado ("Kevin") no mundo**: evidência de que um segundo corpo pode existir e ser dirigido por dados gravados.
- Carregadores: `UnrealModLoader` (RussellJerome, MinHook + ImGui, carrega mods Blueprint/SDK); UE4SS (`UE4SS-RE/RE-UE4SS`). Ferramentas: `Dmgvol/GR_Guides` (projeto UE 4.25, UModel, UnrealPak, UAssetGUI). Comunidades: Discord de mods GRSR, Discord oficial GR.

Referências para esse tipo de problema: **Stray Local Co-op** (UE 4.27, somente UE4SS+Lua, usa tela dividida desativada do jogo; só local), **HogWarp** (Hogwarts Legacy UE 4.27, hooks nativos + código de rede próprio; referência on-line), **PoppyCoop** (UE4 fechado para um jogador, Lua UE4SS + retransmissor Python, somente movimento, `automated`), **Pacific Drive Co-op** (código de servidor hospedado pelo jogador UE4 reativado).

---

## <a id="2-netcode-what-is-actually-in-the-build"></a>2. Código de rede: o que existe na compilação

### <a id="observed-1"></a>OBSERVADO

- Código de rede do motor **incluído na compilação, não removido**. Strings de `Ghostrunner-Win64-Shipping.exe` (são **UTF-16LE**, por isso uma busca só ASCII não as encontra): `UIpNetDriver::TickDispatch: Socket->RecvFrom: %i (%s) from %s`, `UNetDriver::InitListen`, `InitConnect`, `IsNetResourceValid`, `NetDriverDefinitions`, `ActiveNetDrivers`, `ServerConnection`, `ClientConnections`, `ENetworkFailure::NetDriverListenFailure`, `ServerReplicateActors`, `ReplicationDriver`, `ServerMove`, `ServerMovePacked`, `ClientAdjustPosition`, `ServerMove_Validate`, `ReplicatedMovement`, `bReplicates`, `SetReplicates`, `RemoteRole`, `NetGUID`, `PacketHandler`, `StatelessConnectHandlerComponent`, `bUseSeamlessTravel`, `NetServerMaxTickRate`, `bClampListenServerTickRate`, `p.NetEnableListenServerSmoothing`.
- Classes NetDriver **carregadas no jogo em execução** (verificadas por `StaticFindObject` UE4SS): `/Script/OnlineSubsystemUtils.IpNetDriver` → válida, `/Script/OnlineSubsystemSteam.SteamNetDriver` → válida, `/Script/OnlineSubsystemRedpointEOS.EOSNetDriver` → válida, `/Script/Engine.NetDriver` → válida. `/Script/OnlineSubsystemUtils.DemoNetDriver` e um driver GOG → **inválidos/ausentes**.
- EOS integrado por Redpoint `OnlineSubsystemEOS` com configurações incorporadas (`EOSNetDriver`, `RedpointEOSPlatformDefault`, `EnableIdentityChecksOnListenServers`, chaves `epic.clientId`/`refreshToken`); executável importa tardiamente 527 funções `EOS_*`, incluindo `EOS_P2P_*` (19), `EOS_Lobby_*` (110), `EOS_Sessions_*` (39).
- **Servidor hospedado pelo jogador NÃO inicia no mundo do menu com um comando de console.** Duas sondagens: `open /Game/Levels/MainMenu/MainMenu?listen` (congelou, sem NetDriver observado antes) e `listen` com `Saved\Config\WindowsNoEditor\Engine.ini` avulso fornecendo `+NetDriverDefinitions=(…IpNetDriver)` mais `DefaultPlatformService=Null` → `ExecuteConsoleCommand ok=true`, mas `FindAllOf("NetDriver")` permaneceu vazio e `GameEngine.NetDriver` inválido por ~12 s. `World.NetMode` não foi lido como número no UE4SS (acesso à propriedade resolveu como objeto), então NetMode não foi observado diretamente.

### <a id="derived-1"></a>DEDUZIDO

- O caminho de servidor existe e a classe é carregável; falta mundo criado com `?listen` (carregamento real de fase) e GameMode disposto a aceitar segundo jogador. O mundo do menu é local inadequado para testar.
- O `EOSNetDriver` no estilo 4.27 é o transporte mais interessante: daria P2P por retransmissão sem redirecionar portas. Usar credenciais EOS incorporadas do jogo é questão de licença, não ação a realizar silenciosamente. **DECIDIDO EM 2026-10-21: serviços de plataforma estão fora.** A cópia em teste é pirata, então não se pode depender de autenticação EOS / GOG Galaxy / Steamworks; reutilizar credenciais incorporadas seria problema de licença e conduta (regras 1, 8, 10 de AGENTS.md). Transporte por retransmissor UDP próprio (IP direto, LAN ou VPN de sobreposição). Presuma necessidade de portas ou VPN: não há atalho "sem redirecionamento" nesta cópia. Nenhum trabalho com DRM, assinatura de pak ou proteção contra adulteração neste projeto.

### <a id="unknown"></a>DESCONHECIDO

- Se fase de jogabilidade com `?listen` produz NetDriver.
- Se `AGhostrunnerGameMode`/`BP_GhostrunnerGameMode` cria segundo pawn (`SpawnDefaultPawnFor` existe no binário; comportamento não testado).
- Se o pawn real usa `UCharacterMovementComponent` (favorável à replicação) ou movimento de parkour personalizado; não observado, pois nenhuma fase de jogabilidade foi acessada nesta sessão.
- Onde o jogo escreve salvamentos/configuração (aparentemente nunca iniciado antes: sem `Saved\` ou `%LOCALAPPDATA%\Ghostrunner`).

---

## <a id="3-runtime-findings-ue4ss"></a>3. Descobertas em execução (UE4SS)

### <a id="observed-2"></a>OBSERVADO

- **UE4SS v3.0.1 injeta em Ghostrunner 4.26 e executa Lua.** Log: `UE4SS - v3.0.1 Beta #0 - Git SHA #d935b5b`, `[PS] Found EngineVersion: 4.26`, `PS scan successful`, `Console created`, `Event loop start`, mods iniciam, sem travamento.
- Artefato fixado: `UE4SS_v3.0.1.zip`, 5.523.402 B, SHA-256 `4B47D4BCEDDD2F561A4E395BFA00924CCFC945AF576A2D0C613E6537846C57EC`, correspondente ao hash registrado independentemente no núcleo (`games/poppy-playtime/NOTES.md`). Baixado da URL oficial de versão; API GitHub não publicou resumo criptográfico desse recurso.
- Mods nativos do UE4SS funcionam: console F10 criado, CheatManager construído+ativado, `BPModLoaderMod` criou diretório `LogicMods`.
- Reflexão de objetos funciona integralmente em Lua: `FindAllOf("World")`, `FindFirstOf`, `StaticFindObject`, leituras de propriedades e funções têm sucesso.
- Objetos vistos no menu principal:
  - GameInstance: `BP_GameManager_C` (`/Game/Blueprints/Managers/BP_GameManager`),
  - GameMode: `GM_MainMenu_C` (`/Game/Blueprints/GM_MainMenu`),
  - PlayerController: `/Script/Ghostrunner.PlayerControllerOML`,
  - Pawn: `BP_MenuPawn_C`,
  - gerenciador ativo: `SaveManagerOML /Engine/Transient.BP_SaveManager_C`.
  - Mundos: `/Game/Levels/MainMenu/MainMenu`, `/Game/Levels/Main_menu/Main_Menu_HEL`, `/Game/Levels/Main_menu/Main_menu_3d` (convenção de mapas `/Game/Levels/<Name>/<Name>`, com subfases).
- Pawn do menu: `Role=3` (Authority), `RemoteRole=1` (SimulatedProxy), `bReplicates=true`: atores não fixados em Role_None; propriedades de replicação ativas, podendo receber papel de rede.
- Controle do menu por entrada injetada (`SendKeys` Enter + clique central sintético) **não** chegou à jogabilidade; pawn permaneceu `BP_MenuPawn_C` por mais de 20 atualizações.
- `UClass:ForEachFunction`/`ForEachProperty` em Lua só percorrem membros próprios da classe (precisa percorrer superclasses para herdados), informação útil antes de criar ferramentas sobre isso.

### <a id="derived-2"></a>DEDUZIDO

- UE4SS é um hook viável: não exigiu configuração de assinatura (padrão), de acordo com a entrada de suporte Patternsleuth para Ghostrunner.
- Com reflexão funcional, o caminho Modelo B (representante + sincronização de estado) está livre em princípio: estado do pawn local é legível, e Lua pode criar/manipular atores.

---

## <a id="4-test-rig-built-in-this-session"></a>4. Ambiente de testes criado nesta sessão

- Cópia com hardlinks em `<test copy>`: **117 hardlinks, 0 bytes copiados** (NTFS, mesmo volume), SHA-256 do executável idêntico, instalação original intacta (verificado: `Binaries\Win64` real segue sem arquivos UE4SS). Sobrescrever um *arquivo* com hardlink alteraria o original; por isso, só arquivos novos são adicionados e nenhum existente substituído.
- UE4SS v3.0.1 instalado em `Ghostrunner\Binaries\Win64\` da cópia (proxy `dwmapi.dll` + `UE4SS.dll` + `Mods\`), com sonda `Mods\M0Probe\Scripts\main.lua` ativada em `Mods\mods.txt`.
- Sobreposição de configuração avulsa em `Ghostrunner\Saved\Config\WindowsNoEditor\Engine.ini` (definições de driver), mantida para próximo teste de carregamento; apenas na cópia.
- Sondas são somente de leitura em relação ao estado: registram; únicos comandos emitidos foram `listen` e um `open …?listen`.
- Execuções iniciadas em janela 1280×720 e encerradas por PID; cada uma ≤70 s.

## <a id="5-chosen-direction-not-yet-built"></a>5. Direção escolhida (ainda não implementada)

**Sincronização de estado** com autoridade do host em Lua UE4SS, transporte por pequeno retransmissor Python (estrutura PoppyCoop: primeiro integração por arquivo, depois UDP). Investigar replicação nativa (Modelo A) só em fase real, com prazo limitado, pois classes existem, mas servidor não iniciou no menu.

## <a id="6-probe-log-chronological-all-runs-on-the-hardlinked-copy"></a>6. Registro cronológico das sondagens (todas na cópia com hardlinks)

Cada execução = iniciar em janela 1280×720, controlar pelo mod Lua `M0Probe`, encerrar por PID.

| # | Teste | Resultado |
|---|---|---|
| 1 | UE4SS v3.0.1 injeta e executa Lua? | **PASS.** `UE4SS - v3.0.1 Beta #0`, `[PS] Found EngineVersion: 4.26`, `PS scan successful`, `Console created`, `Event loop start`. Sem assinatura personalizada. Primeira tentativa Lua falhou por erro próprio de sintaxe, corrigido. |
| 2 | Lua consegue ler objetos? | **PASS.** Mundos, GameMode, GameInstance, PlayerController, pawn, `bReplicates`/`Role`/`RemoteRole`, `SaveManagerOML` legíveis. Caminhos de mapas visíveis. |
| 3 | `listen` com INI de driver em `<game dir>\Ghostrunner\Saved\Config\WindowsNoEditor\Engine.ini` | **TESTE INVÁLIDO.** Nenhum NetDriver apareceu; veja correção abaixo: jogos UE4 empacotados leem `Saved` de `%LOCALAPPDATA%`, então o arquivo nunca foi carregado. Não cite como evidência. |
| 4 | `open /Game/Levels/MainMenu/MainMenu?listen` | Congelou antes de observar NetDriver (~60 s, encerrado). Execução anterior também emitiu `open …?listen` e congelou igual. |
| 5 | `open /Game/Levels/01_INDUSTRIAL/01_01/01_01_World` (caminho do dicionário GhostrunnerRNG) | **Travamento.** Menu permaneceu ~90 s, PlayerController desapareceu e processo encerrou; um relatório UE4 (`UE4CC-Windows-C52FDF964AA3F89357D80489FF657EFB`, 8 crash/CrashContext/UE4Minidump.dmp). Saltar por `open` contorna o fluxo próprio e trava esta compilação. |
| 6 | `listen` com INI no local **correto**, `%LOCALAPPDATA%\Ghostrunner\Saved\Config\WindowsNoEditor\Engine.ini` | Leitura comprovada: `GameEngine.NetDriverDefinitions` vira `TArray` preenchido. Mas `GameEngine.NetDriver` permaneceu `invalid`, sem instância `NetDriver` por 30 s após `listen`. **Definição de driver sozinha não basta; `listen` num mundo independente já carregado não o converte.** Configuração do usuário copiada e restaurada byte a byte (SHA-256 `C808E16C…48272B` verificado antes/depois). |

### <a id="corrections-to-earlier-statements-in-this-file"></a>Correções de declarações anteriores neste arquivo

- **Local da configuração:** jogos UE4 empacotados mantêm `Saved/` em `%LOCALAPPDATA%\<Project>\Saved\`, não na pasta do jogo. Configuração real: `%LOCALAPPDATA%\Ghostrunner\Saved\Config\WindowsNoEditor\`. Já contém `[Core.System] Paths=` (lista de plugins incluindo `EOSOnlineSubsystem`, `DeltaDNAAnalytics`, `CorsairiCue`, `Aura Unreal Plugin`, `SpiderNavigation`, `DonAINavigation`, `DragonIK`, `DLSS`) e **nenhum** `NetDriverDefinitions`.
- **Histórico de falhas limpo:** exatamente um relatório UE4 existe nesta máquina, criado pela sondagem 5. Sondagens 1-4 e 6 não encerraram por falha; congelamentos em 3/4 foram processos travados e encerrados.
- Só um `.sig` é significativo; ambos são idênticos, então a integridade do pak não é realmente imposta contra mods.

### <a id="where-model-a-stands-after-these-probes"></a>Situação do Modelo A após estas sondagens

As partes existem (classe `IpNetDriver` carregável, vetor `NetDriverDefinitions` respeitado, strings `ServerMove`/`InitListen` no binário), mas nenhum servidor foi observado. Restam dois caminhos não testados: (a) carregar mapa **com** `?listen` pelo fluxo próprio em vez de console; (b) caminho Redpoint `EOSNetDriver`. Até testar um deles, Modelo A está `unproven`, não descartado.

## <a id="7-w1-solved-how-to-get-into-a-level-and-the-real-player-pawn-2026-10-21"></a>7. W1 resolvido: entrar numa fase e identificar o pawn real (2026-10-21)

### <a id="observed-3"></a>OBSERVADO

- **Caminho de entrada funcional (fluxo próprio, sem `open`):** tela de título → clique → menu principal → `Ghostrunner` → `Level select` → dificuldade (`Classic mode`) → clicar cartão desbloqueado (`An Awakening`) → fase carrega. Mundo resultante: **`/Game/Levels/Tutorial/L_Tutorial_Persistant`** (mapa persistente do tutorial com "An Awakening" e "Look Inside").
- **Pawn real é `BP_PlayerCharacter_C`**, em `/Game/Levels/Tutorial/L_Tutorial_Persistant.L_Tutorial_Persistant:PersistentLevel.BP_PlayerCharacter_C_…`:
  - **`CharacterMovement` = `CharacterMovementComponent`** (`CharMoveComp`): **CMC padrão UE4, não componente personalizado de parkour**. `MaxWalkSpeed = 1000.0`, `MovementMode = 1` (Walking) ao surgir.
  - `Mesh` = `SkeletalMeshComponent` (`CharacterMesh0`).
  - `Role = 3` (Authority), `RemoteRole = 1` (SimulatedProxy), `bReplicates = true`.
  - Posição inicial `(-20179, -67068, 2099)`.
- **`UGameplayStatics:CreatePlayer` funciona:** definir `GameMapsSettings.bUseSplitscreen = true` e chamar `CreatePlayer(pc, 1, true)` acrescentou segundo `PlayerControllerOML` e segundo pawn. Contagem passou de 1 → 2 e permaneceu estável por várias atualizações. A compilação tolera segundo jogador local.
- **`open <map>?listen` cria NetDriver:** numa execução, `FindAllOf("NetDriver")` informou `count=1` após começar a transição. Depois travou, **mas havia fator de confusão**: `CreatePlayer` já adicionara segundo jogador na sessão, e tela dividida muda o fluxo do menu. Considere "criação do driver funciona" uma indicação, não prova.
- Automação de menu por coordenadas fixas é **frágil**: segundo jogador (área de visualização dividida) desloca o layout, e cliques posteriores erram. Duas de quatro execuções não chegaram à fase por isso.

### <a id="derived-3"></a>DEDUZIDO

- Como o pawn é um `UCharacterMovementComponent` padrão num `Character`, a replicação de movimento UE4 (`ServerMove` / `ClientAdjustPosition`, ambos presentes) é aplicável. Modelo A passou de "especulativo" para "plausível com pawn padrão", o argumento mais forte até agora para replicação nativa.
- Segundo jogador local é útil por si: alternativa de tela dividida e "segundo corpo" pronto para desenvolver representante sem rede.

### <a id="clean-model-a-result-2026-10-21-second-clean-run"></a>RESULTADO LIMPO do Modelo A (2026-10-21, segunda execução limpa)

OBSERVADO, sem fatores de confusão (nenhum `CreatePlayer` na sessão):

- Entrada por menus em `/Game/Levels/Tutorial/L_Tutorial_Persistant`; pawn `BP_PlayerCharacter_C` presente, `PlayerControllers = 1`.
- Emitido `open /Game/Levels/Tutorial/L_Tutorial_Persistant?listen` por `KismetSystemLibrary:ExecuteConsoleCommand` → `ok=true`.
- Em +3 s, +6 s, +10 s, +15 s, +22 s: mundo inalterado, **`NetDriver = nil` o tempo todo**, `PlayerControllers = 1`, mesmo pawn. **Sem travamento, transição ou driver.**
- Observação anterior `NetDriver = count 1` veio de sessão com segundo jogador já criado e que depois travou. **Não** se reproduz em sessão limpa; não deve ser citada como "listen funciona".

Interpretação: com mapa já carregado e independente, `open …?listen` não refaz a transição nem converte o mundo. Consistente com `listen` também não fazer nada. Modelo A precisa de **carregamento real de mapa com `?listen` desde o início** (opção de inicialização / transição de GameMode), não comando num mundo independente em execução. É o próximo experimento e o último barato para Modelo A.

### <a id="unknown-1"></a>DESCONHECIDO

- Se processo novo iniciado diretamente num mapa com `?listen` (mapa inicial ou transição ao começar fase) produz NetDriver. Não testado.
- Se dois jogadores locais sobrevivem à transição e ao reaparecimento em ponto de controle.
- Se o segundo recebe área própria de câmera (não observado na tela).

## <a id="next-actions"></a>Próximas ações

0. **Iniciar como servidor:** carregar mapa com `?listen` desde o carregamento em vez de console num mundo independente ativo (opções: parâmetro de mapa inicial ou hook Lua no início/transição próprios para a URL carregar `listen`). Se também não produzir NetDriver, encerrar Modelo A e seguir integralmente Modelo B.
1. Modelo B mínimo: parceiro simulado por arquivo, criar representante de `BP_PlayerCharacter_C`, conduzi-lo às coordenadas do parceiro. Classe e CMC padrão agora conhecidos.
2. Viabilidade de tela dividida: `CreatePlayer` sobrevive à mudança de fase, e segundo jogador recebe visualização e entrada próprias?
2. Identificar classe do pawn real e se possui `CharacterMovement`.
3. M0.5: parceiro simulado por arquivo → criar e conduzir ator representante às coordenadas dele.
4. Duas instâncias + integração por arquivo → M1; depois trocar por retransmissor UDP.
5. Nada de publicar sem autorização explícita.

## <a id="sources"></a>Fontes

- Versões UE4SS: https://github.com/UE4SS-RE/RE-UE4SS/releases/tag/v3.0.1
- Suporte de jogos UE4SS (lista Patternsleuth, incluindo Ghostrunner): https://docs.ue4ss.com/dev/patternsleuth-games.html
- Mods Ghostrunner usados como referência: https://github.com/Dmgvol/Ghostrunner-Mods
- Guia de mods: https://github.com/Dmgvol/GR_Guides
- 505 Games: declaração de jogo para um jogador https://support.505games.com/support/solutions/articles/150000147366/
- appdetails Steam (sem categoria multiplayer): https://store.steampowered.com/api/appdetails?appids=1139900&l=english
- Stray cooperativo local (precedente UE4SS-Lua): https://github.com/CyberLifeYT/Stray-Local-Co-op-Mod
- HogWarp (precedente on-line UE4 fechado): https://hogwarp.com/

## <a id="8-model-a-closed-model-b-puppet-primitive-proven-2026-10-21"></a>8. Modelo A encerrado; primitiva do representante Modelo B comprovada (2026-10-21)

### <a id="model-a-four-independent-negatives--closed"></a>Modelo A: quatro negativos independentes, ENCERRADO

| Tentativa | Resultado |
|---|---|
| Comando `listen` em mundo independente carregado. | Sem NetDriver (sondagem anterior). |
| `open <map>?listen` numa fase carregada. | Sem efeito: `NetDriver=nil` em +3/6/10/15/22 s, sem transição ou travamento. |
| URL de mapa na linha de comando (`Ghostrunner-Win64-Shipping.exe /Game/Levels/…?listen`). | **Ignorada:** jogo ainda inicia no menu. |
| `UGameplayStatics:OpenLevel(pc, LEVEL, true, "listen")` a partir do menu. | **Trava imediatamente:** chamada Lua nunca retorna, processo morre. |

Partes do motor presentes (classes carregáveis, `NetDriverDefinitions` respeitado), mas o fluxo de fase desta compilação não tolera rede: caminhos que realmente iniciam transição ignoram a opção ou travam. Modelo A encerrado por enquanto, não por ausência de código de rede, mas porque a inicialização de modo/fase não sobrevive a carregamento `?listen`. Reabrir exigiria hooks nativos em `UEngine::LoadMap`/transição, algo que Lua UE4SS não faz (só intercepta UFunctions).

### <a id="model-b-the-puppet-primitive-works"></a>Modelo B: a primitiva do representante funciona

- `bUseSplitscreen = true` + `UGameplayStatics:CreatePlayer(pc, 1, true)` adiciona segundo `PlayerControllerOML` e segundo pawn (comprovado duas vezes).
- Dirigir esse corpo com **dados externos** funciona: a cada atualização o mod calculou um alvo num círculo ao redor do host e chamou `remotePawn:K2_SetActorLocation(target, false, hit, false)`. Resultado `ok=true, res=true`, com posição real **exatamente** igual ao alvo em cada atualização registrada (exemplo: alvo `(-83, 182, 0)` → real `(-83, 182, 0)`; 9 seguidas). É a metade de receber e conduzir um representante demonstrada com chamadas reais do motor.
- Consequência arquitetural: avatar remoto **não** precisa ser um ator criado; caminho comprovado é segundo jogador local como "vaga de parceiro", com pawn dirigido pelo estado da rede. O custo é aparecerem visualizações divididas, problema de experiência a resolver depois.

### <a id="still-blocked-spawning-a-non-player-puppet-actor"></a>Ainda bloqueado: criar um ator representante que não seja jogador

- `UGameplayStatics:BeginSpawningActorFromClass` **existe e está vinculado** (campo lido como `UFunction`), mas todas as variantes falham: `(pc, class, xform, false, nil, nil)`, `(pc, class, xform, false)`, `(pc, class, xform, true)`, `(pc, class, xform)` lançam erro. Valor lançado não é texto: retorna como objeto `UFunction`, ocultando a causa real.
- Causa mais provável: conversão Lua→`FTransform` do UE4SS (a tabela `{Translation=…, Rotation=…, Scale3D=…}` pode não ser aceita). Próximo agente deve testar argumento escalar/estrutura simples em outra função para confirmar, tentar `StaticConstructObject` + `AActor::FinishSpawning` ou usar ator auxiliar Blueprint (convenção comunitária `ModActor` + LogicMods) para criar dentro de BP.
- Não é exigência do primeiro jogável: o caminho de segundo jogador local evita isso.

### <a id="workflow-lesson-cost-me-three-runs"></a>Lição de fluxo de trabalho (custou três execuções)

Automação de entrada precisa da janela do jogo em primeiro plano; `SetForegroundWindow` de processo em segundo plano costuma falhar silenciosamente, e `SendKeys` vai para a janela focada. Corrija controlando pelo Lua e verificando o estado, não por cliques temporizados.
