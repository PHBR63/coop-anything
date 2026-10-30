# <a id="enter-the-gungeon-2016"></a>Enter the Gungeon (2016)

| | |
|---|---|
| Motor | Unity 2017.4.27f1 (Mono, x64) |
| Versões testadas | Steam, buildid 3829397 (versão 2.1.9, atualizada em 2025-06-27) |
| Projetos | [Gungeon Online](https://thunderstore.io/c/enter-the-gungeon/p/GoTeamAlex/Gungeon_Online/) (entrada do diretório), [GungeonTogether 3-Player](https://thunderstore.io/c/enter-the-gungeon/p/Rec/GungeonTogether_3Player/) (entrada do diretório), [GungeonTogether](https://github.com/llamerrr/GungeonTogether), [GungeonTogether LAN](https://thunderstore.io/c/enter-the-gungeon/p/mamonts/GungeonTogether_LAN/), [Jolly_Coop](https://github.com/kleirof/Jolly_Coop) |
| Nível de QA | automated |
| Última atualização | 2026-10-18 |

## <a id="where-things-stand"></a>Situação atual

Já é possível jogar a partida principal on-line em modo cooperativo para dois jogadores com **Gungeon Online 0.101.0**. Ele oferece convites por sala Steam e conexão LAN (UDP 27460). Dois clientes reais foram conduzidos pela conexão completa até uma partida compartilhada: conectaram pela LAN, escolheram personagens diferentes, geraram o *mesmo* andar procedural e o mantiveram sincronizado. A *simulação dos ataques* dos inimigos não é sincronizada (cada cliente simula o combate por conta própria), e os itens deixados na morte de um jogador também não; o jogo é jogável, mas não um espelho perfeito.

Para **três ou mais jogadores**, a única opção publicada é o experimental **GungeonTogether 3-Player 0.10.8** (somente Steam). É outro fork da linhagem GungeonTogether, ainda inicial: ao carregar, instala patches de sincronização de progresso e inicia uma camada Steam P2P + sala. Ele **não** foi testado em partidas com três clientes aqui (exige três contas Steam/PCs); só foi feito teste de inicialização (consulte QA). Use Gungeon Online para partidas confiáveis de dois jogadores e trate 3-Player como trabalho em andamento.

## <a id="existing-work"></a>Trabalhos existentes

| Projeto | Onde | Licença | Última atividade | O que faz |
|---|---|---|---|---|
| **Gungeon Online** 0.101.0 | [Thunderstore](https://thunderstore.io/c/enter-the-gungeon/p/GoTeamAlex/Gungeon_Online/) | MIT | 2026-10 | Convites por sala Steam + LAN UDP 27460; partida com semente compartilhada, jogador/animação/arma/mascote/estado, vida/morte dos inimigos, balas/arremessos/blanks, objetos quebráveis, fantasma+reanimação, pausa compartilhada e PvP opcional. **Testado aqui: funciona.** |
| **GungeonTogether 3-Player** 0.10.8 | [Thunderstore](https://thunderstore.io/c/enter-the-gungeon/p/Rec/GungeonTogether_3Player/) | MIT | 2026-10 | Sala Steam + P2P, objetivo de 3 jogadores; patches de sincronização de progresso + camada Steam P2P/sala (exige ModTheGungeon API 1.9.2). Compilação inicial, marcada "AI Generated". **Testado aqui: inicializa.** |
| **GungeonTogether** | [GitHub](https://github.com/llamerrr/GungeonTogether) | MIT | 2026-09 | Sala Steam + P2P, sincronização da posição dos jogadores; inimigos/masmorra planejados. **Sem compilação publicada** (issues solicitam a DLL). |
| **GungeonTogether LAN** 0.3.6 | [Thunderstore](https://thunderstore.io/c/enter-the-gungeon/p/mamonts/GungeonTogether_LAN/) | unknown | 0.3.6 | LAN para 2 jogadores/TCP 27631. Impedimento relatado: divergência de mapa do Sell Creep no quarto andar interrompe as partidas. |
| **Jolly_Coop** 1.3.7 | [GitHub](https://github.com/kleirof/Jolly_Coop) | não informada | 2026-01 | Plugin inicializa; melhorias de conveniência para o cooperativo local (contornos dos jogadores, depende de ModTheGungeon API + Gunfig). Nenhum código de rede observado. |

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- Unity 2017.4.27f1, código gerenciado C# em `EtG_Data/Managed/Assembly-CSharp.dll`; mods carregados por BepInEx 5.4 (HarmonyX) ou pelo antigo ModTheGungeon. Este mod usa **BepInExPack_EtG 5.4.2101**.
- O jogo base só oferece **cooperativo local no sofá**, sem on-line; os mods precisam transportar o estado da partida. Gungeon Online usa transporte UDP próprio (LAN) e salas Steam.
- Modelo de rede: **autoridade do host sobre o estado do mundo/partida** (semente compartilhada, geração do andar, sincronização de fase e salvamentos), com simulação de inimigos por cliente. Protocolo versão 32; uma desconexão `version mismatch` significa versões diferentes do mod.
- Salvamentos: `%USERPROFILE%\AppData\LocalLow\Dodge Roll\Enter the Gungeon\SlotA.save` (esse caminho `LocalLow` é **compartilhado por todas as cópias na máquina**; isole-o antes de testar dois clientes). O mod acrescenta sincronização de salvamentos.

## <a id="what-we-changed"></a>O que alteramos

Nenhuma alteração de código. O mod foi verificado como distribuído; as entregas são este relato e a entrada do diretório. O QA foi automatizado com uma **estrutura de testes já incluída no mod** (encontrada ao descompilar `GungeonOnline.dll`), sem necessidade de bots ou scripts de entrada:

- `--gungeon-online-name <name>`
- `--gungeon-online-test host|join` (hospeda / entra na LAN 127.0.0.1:27460 na tela de título)
- `--gungeon-online-test-run <CharacterPrefabSuffix>` (escolhe personagem; o host inicia a partida)

## <a id="qa"></a>QA

Duas cópias isoladas do jogo (nunca a instalação do usuário) com BepInEx + Gungeon Online, cada uma com Steamworks `steam_api.dll` + `steam_appid.txt=480` (Spacewar), para não alterar salvamentos do usuário ou Steam Cloud. A pasta real de salvamentos `LocalLow` foi temporariamente renomeada e restaurada depois.

Execução 1, apenas conexão:

```
host : EtG.exe --gungeon-online-name Hosty   --gungeon-online-test host
client: EtG.exe --gungeon-online-name Clienty --gungeon-online-test join
```

Execução 2, sincronização da partida completa:

```
host : EtG.exe --gungeon-online-name Hosty   --gungeon-online-test host --gungeon-online-test-run Marine
client: EtG.exe --gungeon-online-name Clienty --gungeon-online-test join --gungeon-online-test-run Guide
```

Último resultado da suíte (2026-10-18, PASS):

- Host: `Hosting LAN game on port 27460` e depois `Connected to Clienty over LAN!`
- Cliente: `Joining LAN game at 127.0.0.1:27460` e depois `Connected to Hosty over LAN!`
- Ambos: `Test run: picking PlayerMarine` / `PlayerGuide`; host `Test run: host starting the run.`
- Mesmo andar gerado nos dois: host `Floor fingerprint: 20 rooms, 2A7BE448 (LoadingDungeon|Base_Castle(Clone)|542264008)`; cliente `Floor matches the host's (2A7BE448).`
- Também foram observados sincronizados: marcador do parceiro no mapa, corpo-alvo do parceiro, mascote (`Showing partner's pet Dog`), pausa e progresso salvo.
- Cerca de 4 minutos sem `timed out`, `Disconnected`, `Exception` ou `mismatch` em nenhum log.

Execução 3, teste de inicialização do GungeonTogether 3-Player (2026-10-18, PASS apenas no carregamento):

Uma terceira cópia isolada (`BepInEx 5.4.2101` + `ModTheGungeon API 1.9.2` + `GungeonTogether.dll` 0.10.8) foi iniciada da mesma forma. Como o jogo é **x64**, carrega a `steam_api64.dll` distribuída; a tentativa anterior falhou apenas porque esse arquivo havia sido trocado por uma versão redistribuível mais recente (então `CSteamworks.dll` do jogo não encontrava suas funções exportadas). Mantendo a DLL original e `steam_appid.txt=480`, a execução mostrou:

- `Loading [Gungeon Together 0.10.8]` -> `Gunseon Together starting...` -> `[Progress] Installed 8 progress query patches.` -> `Gunseon Together ready.`
- Steam inicializado (`Starting Steam platform interface`, `Received stats and achievements from Steam`) e rede do mod ativa: encontrou `SteamNetworking`/`SteamMatchmaking`/`SteamApps`, `SendP2PPacket`/`ReadP2PPacket`/`IsP2PPacketAvailable`, todos como `Found`, e criou callbacks `LobbyCreated`/`LobbyEnter`/`GameRichPresenceJoinRequested`/`LobbyMatchList`.
- O jogo chegou ao menu principal; nenhuma exceção do mod (apenas avisos inofensivos do HarmonyX "patch the declared method" e mensagens habituais do áudio/XInput original).

Isso é **teste de carregamento/inicialização, não de partida**: uma sessão real de três clientes exige três contas Steam/PCs; a sincronização da jogabilidade, estabilidade e limite de três jogadores não foram verificados aqui.

## <a id="how-to-play"></a>Como jogar

1. Instale **BepInExPack_EtG 5.4.2101** na pasta do jogo (Thunderstore) e coloque **GungeonOnline.dll** em `BepInEx/plugins/`.
2. Todos iniciam pelo Steam com as mesmas versões dos mods.
3. Pelo Steam: no jogo, pressione **F8**, clique em **Host on Steam** e depois **Invite friend (Steam overlay)**.
4. Pela LAN: host **F8** > **Host on LAN (port 27460)**; outro jogador **F8** > digita o endereço do host > **Join** (ou **Find LAN games**).

Para três ou mais jogadores, instale em vez disso **BepInExPack_EtG 5.4.2101** + **ModTheGungeon API 1.9.2** + **GungeonTogether.dll** 0.10.8 (sem GungeonOnline.dll), inicie pelo Steam, abra o menu do mod (**Ctrl+P**) e use **HOST LOBBY** / **JOIN LOBBY**.

## <a id="known-issues"></a>Problemas conhecidos

- O momento dos ataques dos inimigos não é sincronizado (cada lado simula o seu); espere pequenas dessincronizações.
- Itens deixados na morte de um jogador não são sincronizados.
- O cooperativo em rede de Gungeon Online é para dois; GungeonTogether 3-Player acrescenta três ou mais, mas é exclusivo do Steam e experimental (inicial; partes da partida ainda sem sincronização).
- Versões diferentes do mod desconectam com `version mismatch`.
- GungeonTogether 3-Player é incompatível com Gungeon Online: instale um ou outro (`BepInEx/plugins/GungeonOnline.dll` precisa ser removida para usar o mod de três jogadores).

## <a id="next-steps"></a>Próximos passos

- Verificar o caminho de sala Steam entre dois PCs / duas contas (somente LAN foi testada aqui).
- Testar partidas de GungeonTogether 3-Player com três clientes reais (exige três contas Steam/PCs): confirmar limite de três, fluxo de entrada e sincronização e registrar o que dessincroniza.
- Teste prolongado de estresse: especialmente chefes e quarto andar.
- Questão em aberto: se Gungeon Online funciona bem com outros mods presentes apenas de um lado.
