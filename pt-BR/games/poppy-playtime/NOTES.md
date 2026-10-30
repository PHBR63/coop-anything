# <a id="poppy-playtime--notes"></a>Poppy Playtime — notas

Identificador do jogo: `poppy-playtime`. Sessões: 2026-10-18 e 2026-10-19.

O mod criado aqui fica em repositório próprio: <https://github.com/romannazarov057-spec/PoppyCoop> (mod Lua UE4SS, retransmissor Python, MIT).

## <a id="phase-0--triage-2026-10-18"></a>Etapa 0 — Triagem (2026-10-18)

### <a id="identity-rule-5"></a>Identidade (regra 5)

| Campo | Valor | Fonte |
|---|---|---|
| Título | Poppy Playtime (jogo base = Capítulo 1) | API da loja Steam, appid 1721470 |
| Loja | Steam | confirmação do usuário e `appmanifest_1721470.acf` |
| Instalação | `<game dir>` = `D:\Steam\steamapps\common\Poppy Playtime` (PC do usuário; somente local) | leitura de libraryfolders.vdf |
| Versão / compilação | Steam buildid **21905565** (StateFlags 4 = completo, SizeOnDisk 5.899.523.032 bytes, LastUpdated 1792338989) | `appmanifest_1721470.acf`, 2026-10-18 |
| SHA-256 do inicializador | `1E6CE253F97D663E8E3D6E8F2C7D3E20314D9906BEC5208BFF07578C4E31CC4D` - `<game dir>\WindowsNoEditor\Poppy_Playtime.exe` (345.600 bytes) | Get-FileHash, 2026-10-18 |
| SHA-256 do jogo | `0808123FFE2A8A002CA83DDD090C7796010DEB7C79CB52A79B71463F3DAD5912` - `<game dir>\WindowsNoEditor\Poppy_Playtime\Binaries\Win64\Poppy_Playtime-Win64-Shipping.exe` (80.168.960 bytes) | Get-FileHash, 2026-10-18 |
| Motor | **Unreal Engine 4.27.2**, `FileVersionRaw 4.27.2.0`; estrutura `WindowsNoEditor/`, pacotes `pakchunk0-WindowsNoEditor.pak` (2,65 GB) e `pakchunk0optional` (27 MB) | versão do executável, listagem |
| Lançamento | 12 de outubro de 2021 | API da loja Steam |
| DLC | Capítulos 2-5: appids 1817490, 2555190, 3008670, 4100940 | API da loja Steam |
| Categorias Steam | **Somente um jogador** (sem Remote Play Together, LAN ou categorias cooperativas) | `categories` da API |
| Sistema | Somente Windows | `platforms` da API |
| Vestígios multiplayer nos binários | `Poppy_Playtime\Binaries\Win64` inclui **`vivoxsdk_x64.dll` (5,3 MB)** e **`ortp_x64.dll`**, SDK de voz VoxeX (infraestrutura de voz multiplayer) em jogo solo; também `OpenImageDenoise.dll`, `tbb12.dll` | listagem, 2026-10-18 |

### <a id="answers-to-the-triage-questions"></a>Respostas da triagem

1. Qual jogo exato? Base de Poppy Playtime (Capítulo 1), Steam; instalação ainda baixando.
2. Já foi feito? **Não.** Sem entrada em `DIRECTORY.md`, relato em `games/` ou menção em issue/PR de cranebeaker/coop-anything (API de busca GitHub, `total_count: 0`, 2026-10-18).
3. Motor? Unreal Engine 4, aguardando verificação da instalação.
4. Fonte disponível? Não. Binário fechado, sem scripts-fonte. Há comunidade Nexus (58 mods: utilitários, visuais, menus de cheats, "UETools", "PlaytimeReborn") → mods UE4 por UE4SS/Blueprints comprovadamente viáveis pela comunidade.
5. Multiplayer do motor? No próprio jogo, nenhum distribuído (só categoria solo). **Pista:** TCRF documenta minijogo multiplayer não usado no Capítulo 2 (https://tcrf.net/Poppy_Playtime:_Chapter_2/Multiplayer ; acesso retornou 403, texto só por trecho de busca) → MOB Games tinha trabalho interno com rede UE. Project Playtime, jogo separado do mesmo universo, tem multiplayer UE completo para 6.
6. Legal? Jogadores possuem o jogo (base gratuita no Steam). Mod seria pacote separado, sem arquivos do jogo ou sistema antitrapaça envolvido, pois é solo.

## <a id="phase-1--research-2026-10-18-agent-search-pass"></a>Etapa 1 — Pesquisa (2026-10-18, busca do agente)

### <a id="findings-observations--each-with-source"></a>Descobertas (observações com fontes)

1. **Nenhum mod cooperativo utilizável em 2026-10-18:**
   - Nexus Mods Poppy Playtime: 58 mods, principais são utilitários/visuais/compressores de cenas, nenhum multiplayer (nexusmods.com/poppyplaytime, busca).
   - Repositórios GitHub "poppy playtime" (435 resultados) e "poppy playtime multiplayer": sem projetos cooperativos/multiplayer, só clones de fãs e conteúdo irrelevante. Um resultado parecia página de pirataria, não usado (regra 10).
2. **Um mod multiplayer de fã existiu e foi apagado.** Discussão r/PoppyPlaytime "Anybody have a poppy playtime multiplayer mod?" (2022): https://www.reddit.com/r/PoppyPlaytime/comments/uut6zj/ ; desenvolvedor do vídeo "Poppy Playtime's Multiplayer Mod Is INSANE" (https://www.youtube.com/watch?v=7nRBqSjCB0k) confirmou viabilidade; arquivos apagados. Vídeo posterior: "Scrapped Mods: Poppy Playtime Multiplayer WIP Mod" (https://www.youtube.com/watch?v=RuR7kCDEjeQ).
3. **Conteúdo multiplayer não usado no Capítulo 2** (TCRF acima; só trecho de busca, acesso direto 403).
4. **Derivado multiplayer oficial: Project Playtime** (appid Steam 1961460, gratuito, 6 jogadores: 5 sobreviventes e 1 monstro). Salas privadas/amigos: guias e vídeos 2025-2026 confirmam funcionamento; discussões antigas reclamam da falta de convites. Páginas de estado de servidores indicam operação (baixa confiança). https://store.steampowered.com/app/1961460/
5. **Steam Remote Play Together não compatível** com Poppy Playtime (ausente das categorias). Parsec, com transmissão e controle compartilhado, permite amigos controlarem o mesmo personagem, não modo cooperativo real.
6. **Sem handler Poppy Playtime no Nucleus Co-op** (buscas splitscreen.me/comunidade, 2026-10-18). Nucleus exige tela dividida local ou LAN para unir instâncias; jogo não tem nenhum → não se aplica.

### <a id="derived-conclusions-from-the-observations"></a>Deduzido (conclusões das observações)

- Campanha cooperativa real do Capítulo 1 = **caminho 2, criar do zero**: engenharia reversa UE4 (UE4SS, dump SDK/Dumper-7), estado com autoridade do host; segundo README, dias ou mais de trabalho de agentes, com estados intermediários não jogáveis.
- Opções rápidas para a meta real do usuário (jogar com amigos):
  1. Project Playtime: oficial, gratuito, já permite amigos, modo diferente.
  2. Parsec como copiloto: acompanhar/ajudar um jogador, não cooperativo real.
  3. O próprio mod: recusado naquele momento pelo usuário.

### <a id="guesses-unverified"></a>Hipóteses (não verificadas)

- ~~Capítulo 1 provavelmente também contém vestígios multiplayer como o 2~~ **Confirmado nos binários em 2026-10-18:** SDK de voz VoxeX (`vivoxsdk_x64.dll`, `ortp_x64.dll`) em `Binaries\Win64` da base. Voz não tem finalidade em jogo solo; portanto, existia código multiplayer/serviços on-line nesta compilação UE4.27.2, provavelmente compartilhado com Project Playtime.

### <a id="unknowns"></a>Desconhecidos

- Identificador e hash exatos instalados, pois download incompleto.
- Correspondência do Capítulo 1 Steam a relatos conhecidos de mods (UETools etc. visam compilações específicas).
- População e saúde dos servidores Project Playtime a longo prazo.

## <a id="phase-2--workspace-2026-10-18"></a>Etapa 2 — Ambiente de trabalho (2026-10-18)

Instalação copiada de `<game dir>` a pasta temporária em outro disco (`<test dir>`, 122 arquivos, 5,23 GB, robocopy sem falhas). Instalação e salvamentos reais intactos (regra 2).

- Salvamentos (leitura no PC): `%LOCALAPPDATA%\Poppy_Playtime\Saved\
  SaveGames`; só `SG_Audio.sav` e `SG_Graphics.sav` existiam (configurações, sem história). Backup antes de iniciar testes.
- Ferramenta: **RE-UE4SS v3.0.1** (versão oficial `UE4SS-RE/RE-UE4SS`, arquivo `UE4SS_v3.0.1.zip`, 5.523.402 bytes, SHA-256 `4B47D4BCEDDD2F561A4E395BFA00924CCFC945AF576A2D0C613E6537846C57EC`; sem soma publicada, então fixação própria). Instalada em `Poppy_Playtime\Binaries\Win64` da cópia.

### <a id="observation--ue4ss-works-on-this-build"></a>Observação — UE4SS funciona nesta compilação

Inicialização da cópia registrou:

```
UE4SS - v3.0.1 Beta #0 - Git SHA #d935b5b
Using engine version 4.27 for internal logic ...
PS scan took ... Game: Poppy_Playtime-Win64-Shipping.exe (80168960 bytes)
```

UE4SS examina o jogo, encontra versão **4.27**, resolve offsets e executa Lua próprio dentro do processo (etapa 3).

## <a id="phase-3--understand-2026-10-18"></a>Etapa 3 — Entendimento (2026-10-18)

### <a id="method-repeatable-no-keypresses"></a>Método (repetível, sem teclas)

Mod Lua próprio `CoopProbe` em `Mods\` da cópia, habilitado em `mods.txt`. (a) Comprova hook, registrando jogador local a cada segundo; (b) aciona dumps por código (`DumpAllObjects()`, `GenerateSDK()`), sem depender de Ctrl+J/Ctrl+H humanos. Cobertura de classes completa com `LoadAllAssetsBeforeDumpingObjects = 1` e `...GeneratingCXXHeaders = 1` em `UE4SS-settings.ini`, depois dump no menu; **não precisa entrar no capítulo** para ver classes.

### <a id="observation--the-dumps"></a>Observação — os dumps

- `UE4SS_ObjectDump.txt`: 19 atores no menu, **10.701 após carregar todos os recursos**; arquivo cresceu de 11,2 MB a 23,7 MB.
- Huggy presente, 1774 correspondências, por exemplo `Package /Game/Assets/Characters/Huggie/Scary/Huggy_AI/.../Huggy_RIG`, `/Game/Assets/Blueprints/BridgeBreak/HuggyDeath/...`, rig de câmera `/Game/Player/Rig/CameraRig/Huggy_Jumpscare_camera`.
- `GenerateSDK` (`CXXHeaderDump`) derrubou o jogo após carregar tudo; corresponde ao aviso UE4SS de instabilidade ao continuar além do menu após dump. O dump de objetos era necessário; cabeçalhos podem ser regenerados por classe sem carga completa.

### <a id="observation--levels-from-the-full-object-dump"></a>Observação — fases (dump completo)

- `/Game/Levels/PP_FinalLevel`: mapa principal jogável do Capítulo 1.
- `/Game/Levels/Level_Streaming_Areas`: subníveis carregados sob demanda.
- `/Game/Levels/Power_Room_LightsOn`, `/Game/Levels/AchebesLightingScenarios`: cenários de iluminação/subníveis.
- `/Game/Levels/MainMenu` e `MainMenu_BuiltData`.

### <a id="observation--game-classes-with-the-co-op-relevant-fields-from-cxxheaderdump"></a>Observação — classes e campos relevantes (de `CXXHeaderDump`)

- `APlayerBP_C : ACharacter`: WalkSpeed/RunSpeed/Crouch, `ExtendoHandR/L`, `LengthOfWire`, `InventoryItems`/`StoredInventory`, `ObjectivesText`, `SlotName`/`UserIndex`/`SaveVariable`, saúde/dano, `DeathScreen`, `StartIntro`/`SkipIntro`, `DoorInteraction`. Várias funções recebem `APlayerBP_C* PlayerBP` explicitamente e há campo `User Index`; Blueprint foi pensado para mais de uma instância de jogador.
- `UPoppyPlayTime_GameInstance_C : UGameInstance`: **armazenamento de indicadores** de história/missões: `CurrentObjective : FObjective`, `ObjectiveList : TArray<FObjective>`, `CurrentQuestInt`, `SaveFileName`, `SaveSlot`, `CreateNewObjective/AnnounceObjective/CompleteObjective/FailObjective/DeleteObjective`.
- `APlayerGameModeBP_C : AGameModeBase`: `LoadGame()`/`SaveGame()`, `AsPPSaveGame`, `SlotName`.
- `UPPSaveGame_C`: `FS_SaveData` = `PlayerLocation`, `LevelSaved`, `MapName`, um `TArray<FGuid>` (identificadores de itens coletados), `SaveSlotOne`.
- `USG_Chapters_C`: `CreatedNewGame`.
- GrabPack/interação: `AExtendoHand_C`, `AExtendo_Rope_C`, `UPickUp_Component_C`, `DoorInteraction`, `GrabPackUpgradeStation`, `UHandleReplacement_C`, `UHandleBox_C`.
- Interface/fluxo: `MainMenu_UI_Two_C` (Play/Merch/Settings/Quit), `UPlayMenu_C` (Play = New Game, `Skip Intro()`, `LoadGameButton`).
- Rede presente: `SteamCore`, `OnlineSubsystemSteam`, `OodleNetworkHandlerComponent`, `PacketHandler`, `SessionMessages`; pilha de replicação/on-line compilada, mas dormente (herança Project Playtime); atores próprios não expõem propriedades replicadas.

### <a id="derived"></a>Deduzido

- Modelo: **estado com autoridade do host** (`how-coop-mods-work.md`): um cliente controla inimigos/física/objetivos; demais enviam entrada e recebem estado.
- Mapa único (`PP_FinalLevel` e áreas carregadas) torna transições principalmente manter os mesmos subníveis carregados, não recarregar uma fase.
- Objetivos centralizados em `UGameInstance` correspondem à regra prática de um armazenamento de indicadores; replicar essa estrutura leva a maior parte da campanha.

### <a id="unknowns-1"></a>Desconhecidos

- Classe/grafo real da IA Huggy (lista encontrada, sem leitura detalhada).
- Quais subníveis são essenciais à jogabilidade, quais só iluminação.
- Se pak é criptografado (busca bruta `/Game/Levels/` sem resultado; cabeçalho não começa por assinatura padrão `E1 12 6F 5A`). Extração não necessária e adiada.

## <a id="phase-5--build-first-slice-the-puppet-2026-10-18"></a>Etapa 5 — Implementação, primeira parte: representante (2026-10-18)

Meta (`how-coop-mods-work.md`, etapa 2): segundo ator com forma de jogador no mundo, cuja transformação possa ser controlada por código. Ainda sem rede. Mod: `poppy-coop/PoppyCoop/Scripts/main.lua` na pasta do usuário, instalado na cópia por `poppy-coop/deploy.ps1`.

### <a id="observation--what-works-verified-by-run"></a>Observação — o que funciona, verificado em execução

Uma inicialização (`killed after 110–130 s (NO CRASH)`) faz tudo isto:

```
world = World /Game/Levels/PP_FinalLevel.PP_FinalLevel
playing: pawn=PlayerBP_C ...Player_Level:PersistentLevel.PlayerBP_2
spawn: summon SkeletalMeshActor (try 1, existing=4)
spawn: adopted puppet = SkeletalMeshActor ...PP_FinalLevel:PersistentLevel.SkeletalMeshActor_2147482034
dress: mesh=SkeletalMesh /Game/Player/Rig/Plegs_rig.Plegs_rig materials=0
drive: target=-3792 108 93 actual=-3792 108 93 moved=true
```

Entrar no Capítulo 1, invocar segundo ator, adotá-lo, dar a malha esquelética do jogador e usar `K2_SetActorLocation` em órbita local funcionam; processo sobrevive. Posição efetiva igual ao destino solicitado.

### <a id="observation--the-spawn-api-is-the-trap-source-upstream-issue"></a>Observação — armadilha da API de criação (fonte: issue do projeto original)

- `World:SpawnActor(Class, {}, {})`, chamada usada por `BPModLoaderMod`, retorna **nil** nesta compilação; até caso idêntico `SkeletalMeshActor` falha e processo morre (saída `0xC0000409` / violação de acesso).
- `UGameplayStatics:BeginDeferredActorSpawnFromClass` e `FinishSpawningActor`, alternativa documentada, também retornaram nil e processo morreu (`0xC0000005`).
- Causa no projeto original, aberta na v3.0.1: [UE4SS-RE/RE-UE4SS#527](https://github.com/UE4SS-RE/RE-UE4SS/issues/527), *"UWorld::SpawnActor() crashes too often in a game thread from both Lua and C++"*; falha no caminho de animação/ProcessEvent. `v3.0.1` (2024-02-14) é última estável; `experimental-latest` tem cerca de 1181 commits a mais, ainda não usada.
- **Alternativa funcional:** criar pelo cheat de console do próprio jogo; enviar `summon <class path>` por `KismetSystemLibrary:ExecuteConsoleCommand` (ConsoleEnablerMod cria `CheatManager` funcional), localizar novo ator por `FindAllOf(<ClassName>)` e diferença de nomes antes/depois. É caminho do motor, não reimplementação UE4SS.

### <a id="observation--small-api-facts-that-cost-test-runs"></a>Observação — detalhes de API que custaram testes

- **`AActor::K2_GetActorTransform` não existe** aqui; chamar gera erro. Existem `K2_GetActorLocation`, `K2_GetActorRotation`. Para `FTransform`, usar `UKismetMathLibrary:MakeVector` e `:MakeTransform`, presentes no dump.
- **`K2_SetActorLocation(FVector, bool, FHitResult&, bool)`**: `FHitResult&` é saída; `nil` faz UE4SS falhar, tabela `{}` funciona.
- **Sem `SetAnimInstanceClass`** em `SkeletalMeshComponent`; `AnimClass` é propriedade simples.
- **Aplicar `AnimClass` do jogador (`Plegs_rig_AnimBP_C`) a `SkeletalMeshActor` simples derruba**: AnimBP desreferencia pawn proprietário, que não é `PlayerBP_C` num ator simples; violação perto de nulo.
- **Copiar materiais derruba.** `SetMaterial(i, playerMesh:GetMaterials()[i])` matou reproduzivelmente cerca de 2 s após configurar o corpo em três execuções; sem cópia, mesmo código rodou limpo por 130 s. Causa ainda não isolada (recurso material ou renderização); falha conhecida a evitar.
- Comparação: A (copyAnim=false, copyMaterials=**true**) falha cerca de 2 s após configurar, antes de mover; B (ambos false, 15 s parado, depois mover) sem falha, representante move; C (ambos false, mover logo) sem falha por 130 s.

### <a id="derived-1"></a>Deduzido

- Parte de segundo corpo da etapa 2 é viável, mas somente por `summon` e malha esquelética *simples*, sem AnimBP do jogo nem cópia de materiais. Aparência/comportamento equivalentes (animação, materiais) são problema separado, naquele momento bloqueado pelos hooks UE4SS, não pelo jogo.
- Referência estável e `SetActorLocation` funcional, necessários à rede, comprovados. Transporte pode avançar mesmo com aparência em aberto.

### <a id="unknowns-2"></a>Desconhecidos

- Se falha de material vem do recurso, de `SetMaterial` ou de renderizar a malha com material do jogador.
- Se UE4SS `experimental-latest` resolve #527, permitindo `SpawnActor` normal e talvez animação.
- Se animação ociosa independente (nó único `SetAnimation` com sequência de `/Game/Player/Rig/`, sem AnimBP) evita falha.
 

## <a id="phase-5--build-second-slice-a-transport-seam-and-two-real-clients-2026-10-18"></a>Fase 5 — Construção, segunda etapa: uma interface de transporte e dois clientes reais (2026-10-18)

Objetivo: levar a transformação do boneco de um jogo em execução a outro. O transporte remoto do guia (Steam "Spacewar", AppID 480, por um executável auxiliar — [playbook/networking-steam-spacewar.md](../../playbook/networking-steam-spacewar.md)) é um passo grande, então esta etapa primeiro **separa o transporte da lógica de sincronização** por uma interface e comprova as duas direções usando um substituto que dispensa código de rede: arquivos compartilhados em uma pasta.

- Interface: `CONFIG.transport = "file"`, `CONFIG.netDir`, `CONFIG.driveMode = "peer"`. Cada processo grava seu próprio `<playerId>.state` (`"x y z yaw"`) e conduz seu boneco até a posição do arquivo do outro jogador. `playerId` vem de `playerid.txt` no diretório de trabalho do jogo, permitindo executar duas cópias lado a lado.
- `CONFIG.driveMode = "orbit"` (a demonstração local antiga) permanece como alternativa enquanto não existir um arquivo do par.

### <a id="observation--receive-path-one-instance-a-fake-peer"></a>Observação — caminho de recebimento, uma instância, um par simulado

`poppy-coop/test-peer.ps1` grava um `peer.state` com movimento enquanto um cliente executa. O boneco chega exatamente às coordenadas injetadas e as acompanha conforme mudam:

```
net: A sees peer B at -3400 120 95 -> puppet=-3400 120 95 moved=true     (…then -3200, -3000, …)
```

E a posição do próprio mod aparece em `A.state` (`-3881.63 -34.46 90.15 0.00`), portanto a direção de envio também funciona.

### <a id="observation--two-real-clients-two-instances-on-one-pc"></a>Observação — dois clientes reais, duas instâncias em um PC

Duas cópias da instalação de teste (`poppy-playtime` = jogador A, `poppy-playtime-b` = jogador B), cada uma com seu próprio `playerid.txt`; ambas iniciadas juntas. Duas instâncias desta versão realmente executam lado a lado (~2,2 GB cada). Ambas entraram no Capítulo 1, invocaram um boneco e sincronizaram nos dois sentidos:

```
A: net: A sees peer B at -3963 -24 90 -> puppet=-3963 -24 90 moved=true
B: net: B sees peer A at -3976  -0 90 -> puppet=-3976  -0 90 moved=false
A.state: -3975.87 -0.17 90.15 0.00     B.state: -3963.20 -23.57 90.15 0.00
```

Assim, o boneco de cada cliente fica na *posição real do jogador do outro cliente*, nos dois sentidos. Nova execução limpa: **ambos os processos vivos após 100 s, 0 relatórios de falha**, 28–29 linhas de log do mod cada. (`moved=false` significa que o ator já estava no destino — sem movimento — e não indica erro. Duas instâncias compartilham `%LOCALAPPDATA%\Poppy_Playtime\Saved`, portanto o jogo grava seu ponto de controle ali; o backup foi restaurado após cada execução.)

### <a id="observation--one-unreproduced-two-instance-crash"></a>Observação — uma falha com duas instâncias que não se reproduziu

A primeira execução com duas instâncias gerou um relatório de falha 26 s após o início: `EXCEPTION_ACCESS_VIOLATION reading address 0x10`, e o topo da pilha da thread que falhou é **código UE4SS**, não do jogo:

```
UE4SS                           + 47a916
UE4SS                           + 462c83
Poppy_Playtime-Win64-Shipping   + 11a0eb4
…
UE4SS                           + 5550bc
```

Não reapareceu em uma nova execução limpa, e nenhum cliente daquela primeira execução parou de registrar logs no horário informado, então não está claro a qual deles pertence o relatório. A pilha ser UE4SS coloca a falha na mesma família da issue #527. Hipótese, não fato estabelecido: entrar no nível pelo comando de console `open` (que pula a inicialização normal do menu) deixa a configuração já degradada; essa chamada também produziu a falha `WorldShake_C` anterior.

### <a id="derived-2"></a>Deduzido

- A lógica de sincronização e o transporte agora são separáveis. Independentemente de quem carregue os bytes (Steam, UDP, arquivo), o contrato do mod permanece "uma linha de posição por jogador".
- Testar automaticamente dois clientes é viável em um PC, sem precisar de outra máquina.
- O transporte remoto real ainda precisa ser construído; o transporte por arquivo é um substituto para testes e não atravessa uma rede por si só.

### <a id="unknowns-3"></a>Desconhecidos

- O que foi a falha `0x10` no lado UE4SS, e se duas instâncias mais o atalho `open` a disparam de forma confiável.
- Se o truque de duas instâncias do jogo continua funcionando quando os dois clientes estão em PCs *diferentes* (nada observado ainda — tudo até aqui ocorreu em uma máquina).

## <a id="phase-6--build-third-slice-a-relay-and-a-real-end-to-end-run-over-it-2026-10-18"></a>Fase 6 — Construção, terceira etapa: um retransmissor e uma execução real de ponta a ponta por ele (2026-10-18)

Objetivo: colocar um transporte real por trás da interface. O mod Lua não consegue abrir um socket, então o transporte precisa ser um processo separado, ao lado do jogo, que converse com o mod pelos arquivos que ele já consegue ler e gravar. Esse é o padrão de auxiliar do guia ([networking-steam-spacewar.md](../../playbook/networking-steam-spacewar.md)).

### <a id="where-the-helper-is-written-a-real-constraint-found-by-looking"></a>Em que escrever o auxiliar (uma restrição real, encontrada por inspeção)

Não há cadeia de ferramentas C/C++ nesta máquina: `cl`, `gcc`, `g++`, `clang`, `tcc` estão todos ausentes do PATH, `dotnet` é um runtime sem SDK, e os exemplos Steamworks do guia pressupõem um compilador inexistente aqui. Python 3.8.3 está instalado. A **API C plana** do Steam (`SteamAPI_InitFlat`, `SteamAPI_SteamUser_v023`, …) existe justamente para ser chamada de uma linguagem sem arquivos de cabeçalho, então o auxiliar usa Python + `ctypes`:

- `poppy-coop/relay/cooprelay.py` — um programa, dois transportes:
  - `--transport udp`: o host vincula uma porta, o cliente envia para ela. Substituto do Steam nos testes automatizados; sem download, sem conta, duas instâncias em um PC.
  - `--transport steam`: carrega `steam_api64.dll`, inicializa com appid 480, cria ou entra em um lobby e move as mesmas linhas por `ISteamNetworkingMessages` (rede de retransmissão Steam, portanto sem IPs nem redirecionamento de portas).
- Contrato de arquivos, inalterado do lado do mod: o retransmissor lê `<netdir>\<self>.state` e grava `<netdir>\<peer>.state`, atomicamente (`.tmp` + substituição), para que o leitor do jogo nunca veja uma linha parcialmente escrita.

Adições ao mod para uma máquina executar dois clientes com retransmissores:

- `netdir.txt` no diretório de trabalho do jogo fixa a pasta de transporte daquela cópia (`deploy.ps1 -NetDir`). A cópia A grava `…\net\A\A.state`; a cópia B grava `…\net\B\B.state`; o retransmissor de cada máquina conecta sua própria pasta à rede, então as duas pastas nunca colidem.
- `<netdir>\cmd.txt` é um canal de entrada automatizado, consumido na leitura: `pawnloc X Y Z` teleporta o pawn do jogador local, `console <text>` executa um comando de console. Assim um teste consegue mover um jogador sem uma pessoa no teclado.

### <a id="observation--full-chain-two-clients-both-directions-distinct-positions"></a>Observação — cadeia completa, dois clientes, ambas as direções, posições distintas

`poppy-coop/test-relay.ps1`: jogo A + retransmissor A (host UDP) e jogo B + retransmissor B (cliente UDP); em seguida um `pawnloc` move A até o marco `-3000 800 200`. Após o movimento:

```
net\A\A.state  ->  -2963.87  798.36  200.72  32.86     (game A writes its own position)
net\B\A.state  ->  -2963.87  798.36  200.72  32.86     (same bytes, after going over UDP)
net\B\B.state  ->  -3675.69 -318.04   90.15  34.31     (game B writes its own position)
net\A\B.state  ->  -3675.69 -318.04   90.15  34.31     (same bytes, after going over UDP)
```

E os dois jogos concordam em seus próprios logs:

```
game A: net: A sees peer B at -3676 -318 90  -> puppet=-3676 -318 90  moved=true
game B: net: B sees peer A at -2964 798 201 -> puppet=-2964 798 201 moved=true
```

Portanto a cadeia inteira executa nos dois sentidos — jogo A → arquivo → retransmissor A → UDP → retransmissor B → arquivo → jogo B, e o inverso — com os dois jogadores bem separados, impedindo confundir os números com um ponto de surgimento compartilhado. Nenhum relatório de falha durante a execução.

### <a id="observation--the-dll-shipped-with-the-game-is-too-old-for-the-flat-api"></a>Observação — a DLL distribuída com o jogo é antiga demais para a API plana

O guia alerta que cópias antigas de `steam_api.dll` incluídas nos jogos não possuem `SteamAPI_InitFlat`. É o caso de ambas as cópias da instalação (verificado com `poppy-coop/tools/check_steam_exports.py`):

| cópia | tamanho | API plana |
|---|---|---|
| `Engine\…\Steamworks\Steamv151\Win64\steam_api64.dll` | 265 504 | `SteamAPI_InitFlat` **ausente** (SDK 1.51) |
| `PlaytimeLauncher\…\redistributable_bin\win64\steam_api64.dll` | 301 928 | `SteamAPI_InitFlat` **ausente** |

O backend Steam real portanto precisa da versão independente fixa do Steamworks.NET indicada no guia. Baixada da versão oficial (tag `2025.164.1`, arquivo `Steamworks.NET-Standalone_2025.164.1.zip`): o SHA-256 do zip correspondeu ao resumo publicado pelo GitHub `9412348c…796a537d`, e `Windows-x64/steam_api64.dll` dentro dele teve exatamente o hash fixado no guia `eb17909a…10bfb75` e exportou todos os 31 símbolos da API plana usados aqui.

### <a id="observation--the-steam-backend-initialises-and-creates-a-lobby-one-instance"></a>Observação — o backend Steam inicializa e cria um lobby (uma instância)

Com a DLL fixa no lugar, `poppy-coop/test-steam-smoke.ps1` executa somente o retransmissor no PC do proprietário (sem jogo, sem segunda conta) contra o Steam real:

```
loading D:\coop-work\relay\steam\steam_api64.dll      (SHA-256 matches the playbook pin)
SteamAPI_InitFlat ok, appid 480
logged on as SteamID <owner's id, not reproduced here>
CreateLobby call handle=...
LobbyCreated result=1                                  (k_EResultOK)
LOBBY READY. Friend joins with: --lobby <lobby-id>
LobbyEnter lobby=<lobby-id> response=1                 (k_EChatRoomEnterResponseSuccess)
```

Assim, inicialização, login, criação de lobby e entrada no próprio lobby funcionam pelos protótipos `ctypes`. Durante o teste, o Steam mostra o proprietário jogando "Spacewar" — esperado para AppID 480 e algo que convém saber antes de um teste na conta de alguém.

Nota de inicialização que custou tempo real: sem `argtypes` explícitos em cada função com protótipo, `ctypes` passa um ponteiro de interface de 64 bits à função chamada como um `int` C e o trunca; as chamadas então falham ou derrubam o processo sem indicar a causa. Declarar `c_void_p` para cada parâmetro de ponteiro fez funcionar.

### <a id="derived-3"></a>Deduzido

- O transporte agora é um programa concreto: trocar `--transport udp` por `--transport steam` é toda a diferença entre o caminho de teste e o real, e ambas as pontas compartilham um contrato de arquivos e um formato de mensagem.
- Existe um canal de entrada automatizada no jogo (`cmd.txt`), que as próximas fases precisarão de qualquer forma (mover-se para encontrar Huggy, abrir portas, percorrer uma rota).

### <a id="unknowns-4"></a>Desconhecidos

- O **trecho de mensagens** do backend `steam` não foi testado: inicialização, login e criação de lobby estão comprovados acima, mas transportar uma linha entre dois jogadores não, porque o Steam permite um cliente conectado por PC e o trecho P2P precisa de uma segunda conta Steam em outra máquina. Tudo comprovado até aqui moveu dados por UDP nesta máquina, e não havia uma segunda máquina disponível para este trabalho, portanto esse trecho continua em aberto.
- Se a retransmissão Steam aceita as sessões `ISteamNetworkingMessages` do auxiliar entre dois usuários Spacewar (480) quando houver segunda conta — o guia diz que sim, ainda não observado aqui.
- Se um auxiliar Python é aceitável para distribuição (o jogador precisaria de Python, ou o auxiliar precisaria ser empacotado em um executável).

## <a id="phase-5--build-fourth-slice-the-puppets-looks-measured-not-guessed-2026-10-18"></a>Fase 5 — Construção, quarta etapa: a aparência do boneco, medida em vez de presumida (2026-10-18)

A etapa anterior manteve `copyAnim = false` e `copyMaterials = false`, e as notas então disseram que o boneco não tinha materiais nem animação. Metade disso estava errada, e a maneira como estava errada merece o tempo do próximo agente.

**Observação — os materiais nunca estiveram ausentes.** Um diagnóstico imprime, por slot, o que o componente realmente desenharia (`GetMaterial(i)` resolve a substituição do componente, se existir, ou o material do próprio recurso de malha caso contrário):

```
diag[player]: mesh=/Game/Player/Rig/Plegs_rig slots=1 animInstance=Plegs_rig_AnimBP_C animClass=Plegs_rig_AnimBP_C
diag[player]: slot 0 = Material /Game/Assets/Materials/lambert1.lambert1
diag[puppet]: mesh=/Game/Player/Rig/Plegs_rig slots=1 animInstance=<invalid> animClass=<invalid>
diag[puppet]: slot 0 = Material /Game/Assets/Materials/lambert1.lambert1
```

Mesma malha, mesma quantidade de slots, mesmo objeto de material: só `SetSkeletalMesh` já dá ao boneco o material do jogador, portanto o laço `SetMaterial` que causou falha na etapa anterior é totalmente desnecessário. Observe que o material é um material de forma plana `lambert1` — "correto" e "parece sem textura" são a mesma imagem aqui, exatamente por isso a conclusão precisava vir dos dados em vez da tela.

**Observação — por que o AnimBP do jogador nunca pode ser aplicado ao boneco.** O rig tem 7 ossos (`GetNumBones()` = 7) e a animação do jogador é *procedural*: `Plegs_rig_AnimBP` contém uma conversão dinâmica para `PlayerBP_C` e usa a velocidade e a localização do pawn proprietário. Um `SkeletalMeshActor` simples não possui tal pawn, então o grafo lê por uma conversão que falhou. Essa foi a falha da etapa anterior; nenhuma forma de atribuir a classe a torna válida.

**Observação — uma sequência de caminhada toca sem AnimBP.** O rig inclui uma sequência simples no mesmo esqueleto, `/Game/Player/Rig/Anim/legs_Walk_anim`, portanto há animação de nó único disponível:

```
anim: lookup 'legs_Walk' -> AnimSequence /Game/Player/Rig/Anim/legs_Walk_anim.legs_Walk_anim
anim: playing ..., animInstance now AnimSingleNodeInstance ...AnimSingleNodeInstance_2147480736
diag[puppet]: ... animInstance=AnimSingleNodeInstance animClass=<invalid>
```

`SetAnimationMode(AnimationSingleNode)` + `SetAnimation(seq)` + `Play(true)`. O jogo continuou executando e não gravou relatório de falha. Isso dá ao boneco pernas que caminham por conta própria, sem tomar nada emprestado do rig do jogador.

### <a id="unknowns-5"></a>Desconhecidos

- Se a caminhada *parece* correta para um jogador remoto: a velocidade é escolhida, não deduzida, e isso nada diz sobre orientação ou direção. O comprovado é "uma instância de animação está anexada e o processo sobrevive", não a aparência.
- Os nomes dos ossos retornam como `FNameUserdata` (`tostring` imprime um endereço, não o nome); `:ToString()` realmente imprime o nome, portanto os nomes são legíveis — as *posições* são o que a quinta etapa não conseguiu ler de volta por nenhum caminho seguro.
- As verificações de aparência são conduzidas um comando de console ou uma linha de `cmd.txt` por vez, o que funciona em uma sessão mas ainda não é uma suíte repetível.

### <a id="notes-for-the-next-agent"></a>Notas para o próximo agente

- `tools/screenshot.ps1` salva um PNG da janela do jogo, que o proprietário pode examinar — mas um agente lendo estas notas não consegue ver imagens, então as afirmações visuais permanecem programáticas aqui e o proprietário confirma a aparência real.
- Nesta máquina, observou-se que arquivos `*.ps1` recém-gravados na pasta do projeto permaneciam bloqueados ("usados por outro processo") pelo restante da sessão; por isso as verificações de aparência foram executadas como comandos em linha mais `cmd.txt`, em vez de um arquivo de script.

## <a id="phase-5--build-fifth-slice-why-the-puppet-looked-absent-and-the-thread-rules-2026-10-19"></a>Fase 5 — Construção, quinta etapa: por que o boneco parecia ausente e as regras de threads (2026-10-19)

A quarta etapa terminou com "uma instância de animação está anexada e o processo sobrevive", e um boneco visível em uma captura como, no máximo, alguns pixels. Esta etapa encontrou a razão e pagou por ela com três mortes do jogo.

**Observação — o ator invocado não tem escala própria; a malha do jogador tem 14.37.** O `CharacterMesh0` do pawn do jogador carrega uma escala de componente `14.37 14.37 14.37`, que faz o rig atingir tamanho humano. Um `SkeletalMeshActor` criado por `summon` começa em `1.0`, então o boneco era renderizado com aproximadamente 1/14 do tamanho do jogador — parado a 250–350 unidades, isso dá alguns pixels, e "o boneco não está lá" e "o boneco é microscópico" parecem iguais em um log. Copiar `K2_GetComponentScale()` da malha do jogador para o boneco corrigiu a aparência:

```
diag[player]:  scale=14.37 14.37 14.37  refBone0=0.00 0.00 6.00
diag[puppet]:  scale=14.37 14.37 14.37  refBone0=0.00 0.00 6.00
diag: distance player->puppet = 250.0
```

Lição aplicável a outros rigs: **meça a escala do componente de origem antes de concluir que um ator criado está ausente.** Um comando summon cria um ator com transformação padrão, não uma cópia de algo.

**Observação — o boneco está na tela, comprovado ao movê-lo para a câmera.** Testes de frustum não bastam: a malha do *próprio* jogador informa `WasRecentlyRendered(0.5)=false` (rigs em primeira pessoa frequentemente omitem seu desenho), então false ali não significa nada. A verificação que funcionou foi teleportar o boneco para a posição do jogador, antes desativando o laço de condução (veja abaixo): um quadro anterior e outro posterior diferem em 8334 de 20736 pixels amostrados, enquanto dois quadros da *mesma* cena estática diferem em ~9300 com um limiar forte. É uma mudança grande e real e resolve "ele é renderizado?".

**Observação — comparar pixels não responde "a caminhada move as pernas?" neste jogo.** A cena tem movimento próprio suficiente para o piso de ruído encobrir o sinal:

```
two frames 3 s apart, no command sent, no camera input:
  d>12: 17210/20736   d>40: 12940   d>80: 9342
```

Translação da câmera não é a causa (a posição do pawn é idêntica byte a byte no par). Pares A/B com animação ligada ou desligada ficam entre 93 e 8334 amostras alteradas, dependendo de quando são capturados, então os números não trazem informação. Evidência em espaço de tela só é útil para grandes mudanças, como "o boneco cobre um terço da tela", não para um ciclo de caminhada.

**Observação — os três caminhos para a posição de um osso estão fechados nesta versão.**
1. `USkeletalMeshComponent::GetBoneLocationByName` não existe aqui; pertence a `UPoseableMeshComponent` e chamá-lo gera uma exceção.
2. `USceneComponent::GetSocketLocation` (uma malha esquelética resolve nomes de ossos como sockets) **congelou a thread do mod todas as vezes**: diretamente no laço de tick e enfileirado com `ExecuteInGameThread`, que parou o laço da mesma maneira. Sintoma: `A.state` para de atualizar, nada é registrado, nenhum erro Lua, nenhum relatório de falha; o processo permanece vivo e responsivo. `ExecuteInGameThread` portanto parece suficientemente síncrono para que uma chamada que bloqueie a thread do jogo também bloqueie quem a chamou.
3. Ler a propriedade `CachedBoneSpaceTransforms[i].Translation` de `USkeletalMeshComponent` — leitura de propriedade, não chamada — retorna `-nan 0.00 0.00` e `2.8e37 ...`, ou seja, os bytes errados.

**Observação — o relógio da animação é a prova utilizável de que uma pose está sendo reavaliada.** `UAnimSingleNodeInstance` fornece posição e duração (`GetLength()` = 2,0 s para `legs_Walk_anim`). Amostrando uma vez por segundo com a caminhada tocando:

```
animstat[puppet]: mode=1 playing=true pos=1.24 rate=1.0
animstat[puppet]: mode=1 playing=true pos=0.0  rate=1.0
```

A posição avança continuamente, e uma instância de nó único só avança avaliando a sequência; portanto o esqueleto recebe a pose da caminhada em vez de permanecer na pose de referência. É uma afirmação mais fraca que "as pernas se movem visivelmente", e está expressa dessa forma.

**Observação — as regras de threads, aprendidas com duas falhas e duas saídas silenciosas.**
- Tudo que modifica um UObject (malha, materiais, escala, animação, transformação de ator) deve ser enfileirado com `ExecuteInGameThread`. Alterar a instância de animação diretamente na thread do próprio mod produziu `EXCEPTION_ACCESS_VIOLATION reading address 0x0000000000000010`, com a pilha de chamadas apontando para uma chamada nativa originada na thread do mod.
- Conduzir a transformação do boneco pela thread do próprio mod sobrevive por minutos e então morre **sem relatório de falha e sem erro Lua**, com o log simplesmente parando. Após mover `K2_SetActorLocation`/`K2_SetActorRotation` de `drivePuppet` (e o posicionamento na adoção) para a thread do jogo, o jogo executou quatro minutos no modo contínuo "estacionar o boneco em frente ao jogador", ~244 posicionamentos, com **zero erros Lua e nenhum novo relatório de falha**. Dois pontos de dados não são prova; são a razão para manter a regra.
- Uma morte silenciosa é diagnosticável: o mtime de `A.state` é o sinal de vida do laço de tick. Mtime congelado + processo vivo e responsivo = a thread do mod está bloqueada dentro de uma chamada, e o log nunca dirá isso.
- `log()` gera exceção com um argumento de formato do tipo errado (um UObject em `%.1f`), abortando o restante daquele tick, inclusive comandos enfileirados atrás dele. Formate vetores por uma função auxiliar.

### <a id="derived-4"></a>Deduzido

- Pelos dados, a aparência do boneco é a do jogador: mesmo recurso de malha, mesmo material no slot 0 (`lambert1`), mesma escala de componente (14,37) e uma animação de nó único `legs_Walk_anim` cujo relógio avança. Ele não toma emprestado o AnimBP do jogador, nem pode fazê-lo.
- Uma captura de tela é para o proprietário, não para o agente. Toda afirmação visual nestas notas é um número.

### <a id="unknowns-6"></a>Desconhecidos

- Se a caminhada *parece* convincente em 14,37, e como fica à distância: somente o proprietário pode dizer, por um PNG.
- Se as duas saídas silenciosas foram mesmo as gravações de transformação fora da thread, ou outra coisa nesta máquina após ~10 inicializações seguidas (sem relatório de falha, sem evento de erro do Windows, processo desaparecido). A mudança para a thread do jogo é defensável de qualquer forma, mas a atribuição não está comprovada.
- Os nomes dos ossos agora são legíveis (`GetBoneName(i):ToString()`, 7 deles: `joint3`, `l_leg_JNT`, `joint21`, `joint32`, …), mas não se encontrou forma segura de ler suas posições *com a pose aplicada*, então a verificação por osso continua impossível.

### <a id="notes-for-the-next-agent-1"></a>Notas para o próximo agente

- `animpose <t>` congela a caminhada no tempo `t` e `animplay` a retoma: a forma mais limpa de tornar duas capturas comparáveis. `animstat` imprime o relógio uma vez e depois a cada segundo.
- Se um teste precisa deixar o boneco onde você o colocou, primeiro defina `drive manual`, ou o laço de condução o reposicionará em dois segundos e o teste silenciosamente não medirá nada.
- Nesta máquina, quando se pede ao PowerShell para gravar um `cmd.txt` com várias linhas em um `Set-Content -Value`, a chamada ao shell ocasionalmente trava pela sessão inteira. Gravar as linhas pelo pipe com `Out-File`/`-Append`, uma por chamada, funcionou todas as vezes.

## <a id="todo"></a>A fazer

- [x] Quando a instalação terminar: registrar buildid, SHA-256 do executável, versão da engine — concluído em 2026-10-18 (buildid 21905565, UE 4.27.2, hashes acima).
- [x] Ambiente da Fase 2: cópia de teste + UE4SS v3.0.1 instalado e execução verificada — concluído em 2026-10-18.
- [x] Primeira passagem da Fase 3: dump completo de objetos + inventário de classes importantes + nomes dos níveis — concluído em 2026-10-18.
- [x] Abrir issue "claim a game" em cranebeaker/coop-anything — concluído: #19 (não existe rótulo `in-progress` no upstream, então foi aberta sem rótulo).
- [x] Adicionar entrada de lacuna a data/directory.yaml + regenerar DIRECTORY.md; PR de rascunho — concluído: DIRECTORY.md regenerado (245 entradas), PR de rascunho #20.
- [ ] Ler detalhadamente as classes de IA do Huggy / portas / objetivos; mapear o fluxo de missões do Capítulo 1.
- [x] Interface de transporte + sincronização de dois clientes — concluído em 2026-10-18: sincronização de posição funciona nos dois sentidos entre duas instâncias reais do jogo (transporte por arquivo, um PC). Ainda não pela rede.
- [x] Transporte remoto real, escrito e comprovado pelo substituto de teste — concluído em 2026-10-18: `poppy-coop/relay/cooprelay.py` (Python + ctypes, dois transportes), cadeia completa verificada nos dois sentidos com dois clientes (`test-relay.ps1`). O transporte `steam` propriamente dito não foi testado, aguardando a DLL fixa e uma segunda conta Steam.
- [x] Baixar o `Windows-x64/steam_api64.dll` fixado do Steamworks.NET e executar teste de fumaça somente no backend `--transport steam` — concluído em 2026-10-18: inicialização, login, lobby criado, lobby acessado (todos `result=1`/`response=1`). Hashes do zip e da DLL corresponderam aos valores fixados.
- [ ] Testar o trecho de **mensagens** P2P do Steam — precisa de segunda conta Steam em segunda máquina (perguntado ao proprietário: nenhuma segunda máquina disponível ainda). Até lá, somente UDP está comprovado para transportar as linhas.
- [ ] Acrescentar comportamento cooperativo real à sincronização: enviar transformação completa + estado de animação, em vez de apenas posição; depois sincronizar o objetivo do Capítulo 1 (`UPoppyPlayTime_GameInstance_C`).
- [x] Aparência do boneco, primeira passagem — concluído em 2026-10-18: materiais já corretos (nenhuma cópia necessária); o AnimBP do jogador nunca pode ser aplicado (converte para `PlayerBP_C`); `legs_Walk_anim` de nó único toca no boneco sem falha. Aparência ainda não verificada visualmente.
- [x] Aparência do boneco, segunda passagem — concluído em 2026-10-19: o boneco era renderizado em 1/14 do tamanho porque um ator invocado não tem escala de componente; a malha do jogador carrega 14,37 e o mod agora a copia. Leituras de posição de ossos estão indisponíveis nesta versão (veja a quinta etapa), então uma pose em movimento é comprovada pelo relógio da animação de nó único, não pelos dados dos ossos, e a *aparência* da caminhada ainda depende da confirmação do proprietário por uma captura. Toda modificação do boneco agora executa na thread do jogo.
- [ ] Conduzir a taxa da caminhada pela velocidade sincronizada, em vez de um laço fixo, e escolher a direção pela movimentação do par, em vez de um yaw fixo no código.
- [ ] Pedir ao proprietário que confirme a aparência do boneco por um PNG (`tools/screenshot.ps1`); se a caminhada parecer ruim em 14,37, tentar outra sequência no mesmo esqueleto ou uma pose estática.
- [ ] Atribuir a causa das duas saídas silenciosas: executar um teste prolongado com as gravações de transformação fora da thread restauradas, em uma máquina que não esteja iniciando dez clientes seguidos, e observar se morre novamente.
- [ ] Precisamos do UE4SS `experimental-latest` para #527? Somente se surgir a necessidade de criar atores pelo próprio UE4SS; `summon` ainda evita completamente o problema.
- [x] Inicialização automatizada em um nível para QA (console `open /Game/Levels/PP_FinalLevel`, sem cliques frágeis no menu) — concluída e usada por todas as execuções de teste desde então.
