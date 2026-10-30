# <a id="genesis-alpha-one-2019"></a>Genesis Alpha One (2019)

| | |
|---|---|
| Motor | Unreal Engine 4.23 (`++UE4+Release-4.23-CL-0`) |
| Versões testadas | Epic Games Store, arquivos da compilação datados de 2022-07-26, SHA-256 de `Genesis-Win64-Shipping.exe` `e009335b33199dd5dddc37213823b12180076aa71b9b7e0da5f144af319d953c` |
| Projetos | [genesis-alpha-one-coop](https://github.com/Blackouest/genesis-alpha-one-coop) (protótipo Lua com UE4SS, este relato) |
| Nível de QA | none (somente execuções manuais com duas instâncias em um PC, ainda sem suíte automatizada) |
| Última atualização | 2026-10-25 |

## <a id="where-things-stand"></a>Situação atual

Ainda não é jogável. Em um PC, host e convidado conseguem estar na mesma nave: o convidado entra pelo código de rede do próprio UE, recebe do mod uma cópia da estrutura da nave do host, ambas as telas renderizam, o convidado caminha e os jogadores colidem. Desde 2026-10-26, o convidado também troca e dispara armas (dano real nos dois sentidos, projéteis próprios e impactos na sua tela), tem barra de vida própria, indicação de acertos e dicas. A morte do convidado e a promoção da tripulação estão em desenvolvimento. O mapa/construtor, armários, terminais e PDA ainda não funcionam para o convidado.

## <a id="existing-work"></a>Trabalhos existentes

Nada encontrado. Os desenvolvedores disseram não haver planos de multiplayer ([tópico Steam](https://steamcommunity.com/app/712190/discussions/0/3809532340214341715), [playco-opgame](https://playco-opgame.com/genesis-alpha-one/)). Pesquisados: busca na web, diretório, issues e PRs deste repositório (2026-10-25). Issue de indicação de trabalho: #199.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **O código de rede está incluído na compilação.** Existem as classes IpNetDriver, IpConnection, NetDriver, DemoNetDriver e OnlineBeaconHost. `GameEngine.NetDriverDefinitions` ainda aponta `GameNetDriver` para `OnlineSubsystemSteam.SteamNetDriver`, que **não** é distribuído na versão Epic. Reescrever em memória essa definição para `/Script/OnlineSubsystemUtils.IpNetDriver` e executar `open <current map>?listen` cria um servidor hospedado pelo jogador funcional; `open 127.0.0.1` entra nele.
- **Comandos de console a partir de Lua:** `PlayerController:ConsoleCommand` falha aqui sob UE4SS 3.0.1; `KismetSystemLibrary.ExecuteConsoleCommand` funciona.
- **A nave tem cerca de 31 instâncias de fase em tempo de execução** (`/Game/Maps/Structure/*`, `LevelStreamingDynamic`, criadas a partir do salvamento por `LoadLevelInstance`). O UE não as replica aos clientes. Os nomes são `<Short>_LevelInstance_<N>`, derivados de um contador por processo; por isso, um convidado que primeiro carregou o mesmo salvamento e depois carrega a lista do host na mesma ordem recebe **nomes idênticos** (verificados 31/31). A versão 4.23 não tem `OptionalLevelNameOverride` (verificado nas strings do executável).
- **Auxiliares por jogador:** cada jogador recebe `BP_PlayerRemoteCamera_C`, `BP_PlayerInventoryAvatar_C` (estacionado em z=600000) e `BuilderCharacter_C` (z=-199900). Não são as duplicatas que quebram a visualização.
- **O HUD controla o escurecimento.** `PlayerHudWidget_C` contém `Border FadeOutBorder` (preto opaco) e um `LoadingScreen_Widget_C` aninhado. Várias cópias do HUD permanecem na memória depois de recarregar mapas.
- **A inicialização do jogador é para um jogador:** `Eden_PlayerCharacter_C` tem `IsPlayerInitialized`, `BlockActionFPSPlayerInput`, `PlayerMovementSpeed` e funções BP como `InitializePlayer`, `OnLevelLoadedInitializePlayer`, `InitWeaponsFromSave`, `SpawnBuilderCharacter`.
- **Salvamentos e configuração** ficam em `%LOCALAPPDATA%\Genesis_EGS\Saved`, compartilhado por todas as cópias do jogo. Uma cópia de teste escreve na pasta de salvamentos do usuário; faça backup primeiro.
- O conteúdo DLC só carrega quando iniciado pelo inicializador da Epic; uma cópia iniciada diretamente mostra "connection failed" e executa sem DLC.

## <a id="what-we-changed"></a>O que alteramos

Tudo está no mod Lua UE4SS `CoopProbe` do repositório do projeto; cada item foi observado funcionando em uma execução com duas janelas.

| Problema | Causa raiz | Correção |
|---|---|---|
| O servidor hospedado pelo jogador não inicia | `GameNetDriver` -> SteamNetDriver, ausente na versão Epic | Reescrever NetDriverDefinitions para IpNetDriver em memória antes de `open ?listen` |
| Convidado em um mundo vazio | Instâncias de fase em tempo de execução não são replicadas | O host escreve PackageNameToLoad + transformação de cada fase carregada dinamicamente; o convidado chama `LoadLevelInstance` na mesma ordem (por enquanto, transferência por arquivo no mesmo PC) |
| Convidado preso em "CHARGEMENT" | Fluxo de carregamento para um jogador nunca termina no convidado | Remover `LoadingScreen_Widget_C` |
| Ambas as telas completamente pretas após entrar (a cena ainda é renderizada: HighResShot do motor mostrou a visão normal) | `PlayerHudWidget_C.FadeOutBorder` permanece opaco após a entrada, no host e no convidado | Ocultá-lo quando qualquer cópia permanecer em preto opaco por 6 s |
| Convidado não consegue se mover | Personagem do convidado nunca inicializado: `IsPlayerInitialized=false`, `BlockActionFPSPlayerInput=true`, velocidade 0, CharacterMovement inativo na cópia do host e no próprio pawn do convidado | Definir esses campos com os valores do host e ativar CharacterMovement (Walking) nos dois lados |

Descartados durante a investigação: escurecimento do PlayerCameraManager (observe também que `StopCameraFade` na versão 4.23 deixa o escurecimento no seu *alvo*), `SetEnableWorldRendering`, pós-processamento, alvos de visualização e atores auxiliares duplicados.

## <a id="qa"></a>QA

Ainda sem automação. Todas as execuções: duas instâncias da cópia de teste em um PC, `127.0.0.1`, teclas F9 (host) e F8 (convidado), logs por instância em `Mods/CoopProbe/probe_HHMMSS.log`. Notas de laboratório de cada execução: [NOTES.md](NOTES.md).

## <a id="how-to-play"></a>Como jogar

Não é jogável. Instruções para desenvolvedores no README do projeto.

## <a id="known-issues"></a>Problemas conhecidos

- O convidado não consegue abrir o mapa/construtor nem usar armários, terminais e PDA.
- Morte do convidado: a câmera de promoção do jogo termina no jogador 0 (host); o mod a redireciona, mas ainda é instável (um travamento do host nos testes; o convidado pode aparecer dentro de uma estação de trabalho).
- Armas automáticas disparam uma vez por clique no convidado; a arma do slot 2 não é visível no host.
- O convidado vê a arma do host flutuando: a malha do jogador é apenas de primeira pessoa, sem corpo em terceira pessoa.
- Os estados das portas não são replicados (fechadas no convidado, mas atravessáveis). As cores da nave diferem no convidado.
- A estrutura da nave é transferida por arquivo, então host e convidado precisam estar no mesmo PC por enquanto.
- Travamento intermitente na inicialização, causa desconhecida, sem frames do UE4SS na pilha.

## <a id="next-steps"></a>Próximos passos

1. Concluir a morte do convidado com a regra do jogo (cada morte custa um clone/membro da tripulação; com dois jogadores e um clone restante, um jogador morto aguarda um novo clone).
2. Armários, terminais, PDA e mapa para o convidado: interface no convidado, efeitos no mundo no host.
3. Enviar a estrutura da nave pelo canal de mensagens em vez de um arquivo; depois usar retransmissão Steam (a versão Epic não tem steam_api64.dll).
4. Corpo em terceira pessoa, sincronização de portas e cores, testes automatizados com dois clientes usando as ferramentas do repositório.
5. Botões de hospedar e entrar no menu principal do jogo em vez de F9/F8.
