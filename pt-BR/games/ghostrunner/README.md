# <a id="ghostrunner-2020"></a>Ghostrunner (2020)

| | |
|---|---|
| Motor | Unreal Engine 4.26 (fork da One More Level) |
| Versões testadas | Versão GOG, executável de distribuição compilado em 2022-06-23, SHA-256 `8AE0977F794CC3A21EF37550707A048069C81FA2A595B6FD8188CBB06FA94BD4` |
| Projetos | nenhum encontrado (este relato registra uma lacuna e descobertas de hooks da primeira sessão) |
| Nível de QA | none |
| Última atualização | 2026-10-21 |

## <a id="where-things-stand"></a>Situação atual

Hoje ninguém consegue jogar Ghostrunner em modo cooperativo e não existe mod para retomar: as buscas abaixo não encontraram nada em nenhuma plataforma. Esta página acrescenta a parte prática: o motor da compilação é **UE 4.26**, o código de rede **não foi removido**, e **UE4SS v3.0.1 consegue injetar e executar Lua**, provavelmente o hook mais simples que esse jogo terá. Isso torna plausível um protótipo do zero; não significa que esteja próximo. Considere a página uma linha de partida, não um relatório de mod funcional.

## <a id="existing-work"></a>Trabalhos existentes

Pesquisado em 2026-10-21, sem resultados:

- **Nexus Mods**, seção Ghostrunner: 32 mods, todos cosméticos/trainers/salvamentos/DLSS (<https://www.nexusmods.com/games/ghostrunner/mods>). Nenhum multiplayer.
- **GameBanana:** 1 mod (aparência) (<https://gamebanana.com/mods/games/10610>).
- **ModDB:** 0 mods listados (<https://www.moddb.com/games/ghostrunner/mods>).
- **GitHub:** busca de repositórios/código, 620 repositórios "ghostrunner", nenhum cooperativo; `ghostrunner coop` retorna um jogo estudantil de 2017 sem relação.
- **Fóruns Steam / Reddit r/GhostRunner / YouTube:** apenas tópicos de pedidos (<https://steamcommunity.com/app/1139900/discussions/0/3108014879965760313/>).
- **Configurações personalizadas de jogos do UE4SS:** nenhuma pasta Ghostrunner.
- **Oficial:** a distribuidora informa jogo para um jogador com seleção de fases (<https://support.505games.com/support/solutions/articles/150000147366/>); os dados da loja Steam não listam categoria multiplayer (<https://store.steampowered.com/api/appdetails?appids=1139900&l=english>). Ghostrunner 2 (UE 4.27) também não tem modo cooperativo; `RogueRunner.exe` é um modo para um jogador.

Modificações relacionadas relevantes como referência anterior (não cooperativas):

- **Ghost Mod:** reproduz sua partida anterior como um segundo personagem visível e animado ("Kevin"). Comprova que um corpo adicional controlado pode existir sem novos recursos do motor. <https://github.com/Dmgvol/Ghostrunner-Mods>
- **UnrealModLoader** (MinHook + ImGui, carrega Blueprint/LogicMods) <https://github.com/RussellJerome/UnrealModLoader>, **UE4SS** <https://github.com/UE4SS-RE/RE-UE4SS>, **GR_Guides** (projeto UE 4.25, ferramentas UModel/UnrealPak/UAssetGUI) <https://github.com/Dmgvol/GR_Guides>.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Motor:** Unreal Engine 4.26, fork próprio "OML". Versão confirmada duas vezes: `FEngineVersion` em UTF-16 = `++UE4+Release-4.26-CL-0` no executável e Patternsleuth do UE4SS informa `Found EngineVersion: 4.26` em execução.
- **Empacotamento:** um `…-WindowsNoEditor.pak` de 35,8 GB (pak versão 11) com índice criptografado, além de arquivos `.sig` fictícios idênticos byte a byte. `Config/*.ini` processados e nomes dos recursos não são legíveis estaticamente, e editar recursos/Blueprints é efetivamente inviável. Planeje alterações **somente em tempo de execução** (carregador, configuração avulsa, hooks).
- **Código de rede:** compilado e não removido. O executável contém em UTF-16 `UIpNetDriver::TickDispatch`, `UNetDriver::InitListen`/`InitConnect`, `ServerReplicateActors`, `ServerMove`, `ClientAdjustPosition`, `ReplicatedMovement`, `bReplicates`, `NetGUID`, `PacketHandler`. Em execução, `/Script/OnlineSubsystemUtils.IpNetDriver`, `/Script/OnlineSubsystemSteam.SteamNetDriver` e `/Script/OnlineSubsystemRedpointEOS.EOSNetDriver` são **classes carregáveis**. Portanto, um servidor hospedado pelo jogador é um caminho com código disponível, com a ressalva em "O que alteramos".
- **Serviços de plataforma:** versão GOG. `OnlineSubsystemGOG` + `Galaxy64.dll` (salas e P2P GOG), `EOSSDK-Win64-Shipping.dll` com Redpoint `OnlineSubsystemEOS`/`EOSNetDriver` compilado, `steam_api64.dll` presente mas não usada em instalação GOG. O subsistema de execução é escolhido pelo arquivo **avulso** `Content\JsonFiles\Platforms\OnlineSubsystem\FOnlineSubsystemData.json` = `{"defaultOnlineSubsystemName": "GOG"}`, o caminho mais simples para mudar o transporte.
- **Entradas:** o jogo lê seu próprio `Content\JsonFiles\Bindings.json` (tabelas `bindPC` e `bindPAD`). Um conjunto por família de dispositivo, **sem índice de jogador**: pressupõe um jogador local alternando entre mouse/teclado e controle. Qualquer solução de tela dividida ou segundo jogador precisa tratar isso.
- **Fluxo:** `BP_GameManager_C` (GameInstance), `GM_MainMenu_C` (GameMode do menu), `AGhostrunnerGameMode`/`BP_GhostrunnerGameMode`, `PlayerControllerOML`, `PlayerStateOML`, `LevelManager`, `CheckpointManager`/`RevertableObject`, `SaveManagerOML` + `GhostrunnerSaveGameBase`. Mapas ficam em `/Game/Levels/<Name>/<Name>` e usam subníveis (por exemplo, `/Game/Levels/MainMenu/MainMenu`, `MainMenu` + `Main_Menu_HEL` + `Main_menu_3d`). Caminhos das fases estão documentados publicamente no dicionário de nomes de mapa em execução do randomizador (por exemplo, `/Game/Levels/01_INDUSTRIAL/01_01/01_01_World` = "The Climb"; três mapas são "Persistant" e contêm duas fases cada).
- **Onde o jogo grava estado:** `%LOCALAPPDATA%\Ghostrunner\Saved\` - `Config\WindowsNoEditor\*.ini` (configuração avulsa que um mod pode substituir; *não* fica sob a pasta do jogo), `Crashes\`, `Analytics\` e salvamentos. Antes de editar configurações, lembre que são dados do usuário: faça backup.
- **Sem sistema antitrapaça.** Nenhum arquivo ou nome de EAC/BattlEye; o código cliente antitrapaça EOS vinculado está inativo. Não existe serviço on-line deste jogo que possa ser violado.

## <a id="what-we-changed"></a>O que alteramos

Nada foi distribuído. Esta sessão montou uma estrutura de testes e executou três experimentos.

- **Estrutura:** cópia de teste por hardlinks em `<test copy>`, **117 hardlinks, 0 bytes copiados**, sem alterar a instalação original (verificada após cada execução). UE4SS v3.0.1 em `Binaries\Win64` da cópia (proxy `dwmapi.dll`), mod de sondagem em `Mods\M0Probe\Scripts\main.lua`.
- **Experimento 1 - UE4SS carrega? PASS.** Log mostra `UE4SS - v3.0.1`, `[PS] Found EngineVersion: 4.26`, `PS scan successful`, console criado, CheatManager ativado e mods Lua executando. Não foi necessária configuração de assinatura personalizada. É o resultado mais útil desta página.
- **Experimento 2 - podemos ler o jogo pelo Lua? PASS.** `FindAllOf`, `StaticFindObject`, leitura de propriedades e funções funcionam. Estado do menu: GameInstance `BP_GameManager_C`, GameMode `GM_MainMenu_C`, controlador `PlayerControllerOML`, personagem `BP_MenuPawn_C` (com `Role=Authority`, `RemoteRole=SimulatedProxy`, `bReplicates=true`), `SaveManagerOML` ativo.
- **Experimento 3 - um servidor hospedado pelo jogador inicia? NÃO (até aqui).** Com `+NetDriverDefinitions=(…IpNetDriver)` no arquivo correto (`%LOCALAPPDATA%\Ghostrunner\Saved\Config\WindowsNoEditor\Engine.ini`; jogos UE4 empacotados não leem `Saved` da pasta do jogo), a definição **é** respeitada: `GameEngine.NetDriverDefinitions` vira um array preenchido. Mas `listen` deixou `GameEngine.NetDriver` inválido e não criou instância de `NetDriver` em 30 s; `open …?listen` no mapa de menu congelou o jogo antes de se observar um driver. Conclusão: uma definição de netdriver não converte um mundo independente já carregado; o mapa precisa ser carregado com `?listen` por um caminho real de carregamento.
- **Experimento 4 - podemos ir para uma fase pelo console? NÃO.** `open /Game/Levels/01_INDUSTRIAL/01_01/01_01_World` (caminho do dicionário de nomes em execução do randomizador GhostrunnerRNG) manteve o menu por cerca de 90 s, descartou PlayerController e **derrubou o processo** (relatório de falha UE4 + minidump). Os caminhos estão corretos; o fluxo de fases do jogo (estado de `BP_GameManager`) está sendo contornado, e esta compilação não tolera isso.
- **Experimento 5 - o código de rede do motor é acessível por Lua? Parcialmente.** As classes carregam e a configuração é lida, mas nenhum NetDriver foi observado. O modelo A é `unproven`, não descartado: as opções não testadas são carregar um mapa com `?listen` pelo fluxo próprio do jogo e usar Redpoint `EOSNetDriver`.
- **Experimento 6 - uma fase pode ser alcançada sem `open`? PASS.** Usar os próprios menus (clique no título -> `Ghostrunner` -> `Level select` -> `Classic mode` -> `An Awakening`) carrega `/Game/Levels/Tutorial/L_Tutorial_Persistant`. O personagem real é **`BP_PlayerCharacter_C`**, com **`CharacterMovementComponent` padrão** (`CharMoveComp`, MaxWalkSpeed 1000, MovementMode Walking) e `SkeletalMeshComponent`, com `bReplicates=true` e Role=Authority. Isso importa: a replicação de movimento do próprio UE4 se aplica a um CMC padrão, tornando o modelo A *plausível com um personagem padrão*, em vez de especulativo.
- **Experimento 7 - a compilação tolera um segundo jogador local? SIM.** Definir `GameMapsSettings.bUseSplitscreen = true` e chamar `UGameplayStatics:CreatePlayer(controller, 1, true)` criou um segundo `PlayerControllerOML` e outro personagem; a contagem de controladores passou de 1 para 2 e ficou estável. Serve tanto como alternativa de tela dividida local quanto como segundo corpo pronto para um representante sem código de rede algum.
- **Experimento 8 - `open <map>?listen` dentro de uma fase (teste limpo): AINDA NÃO FEITO.** Uma execução chegou a informar `FindAllOf("NetDriver")` = 1 após o início da transição, mas aquela sessão já havia criado um segundo jogador local e então falhou; o resultado tem fatores confundidores e não é reivindicado aqui. A execução limpa é o próximo passo.
- Não feitos: veredito limpo do modelo A e verificação de sobrevivência de dois jogadores locais a uma mudança de fase.
- Efeito colateral relevante: a configuração do usuário `Engine.ini` foi temporariamente alterada no experimento 3 e **restaurada de forma idêntica byte a byte** (SHA-256 conferido antes/depois). Nunca se escreveu na instalação original.

## <a id="qa"></a>QA

Nada está automatizado ainda; o nível honesto de QA é `none`, pois não há recurso cooperativo para testar nem estrutura de dois clientes executada. Os mods de sondagem registram em `Binaries\Win64\UE4SS.log`; cada execução ocorreu em janela e foi encerrada pelo pid. Pelos guias, uma execução com par simulado ou cliente único também não qualificaria como `automated`.

## <a id="how-to-play"></a>Como jogar

Não é jogável em modo cooperativo. Esta página ainda não oferece nada para instalar.

## <a id="known-issues"></a>Problemas conhecidos

- Não existe mod cooperativo; tudo aqui é pesquisa e estrutura de testes.
- O pak é opaco e assinado (assinatura fictícia), tornando inacessível qualquer alteração de Blueprint, recurso ou configuração processada; apenas hooks em execução.
- Ghostrunner mata com um único golpe e não tem conceito de segundo jogador: história, checkpoints e gatilhos de fim de fase pressupõem o jogador único. Esse é o trabalho real, não o transporte.
- A camada de entradas tem um conjunto de teclas para todos os dispositivos locais; seria necessário reformular a classe de entradas para tornar agradável a tela dividida.
- A integração EOS desta compilação usa credenciais incorporadas ao jogo. Reutilizá-las para P2P é uma questão de licença, não um benefício gratuito.

## <a id="next-steps"></a>Próximos passos

1. Entrar deterministicamente em uma fase, chamando pelo Lua a função própria de início de fase ou carregando um caminho conhecido com `?listen`. Repetir a sondagem de NetDriver. Esse único teste decide entre modelo A (retomar a replicação do motor) e B (representante UE4SS + retransmissor próprio).
2. Identificar a classe real do personagem e se ela contém `UCharacterMovementComponent`.
3. Primeiro exemplo do modelo B: par simulado por arquivo, criar um ator representante e movê-lo às coordenadas do par (primeiro marco que vale chamar de progresso).
4. Só depois: transporte (interface por arquivo -> retransmissor UDP) e duas instâncias reais.
