# <a id="graveyard-keeper-2018"></a>Graveyard Keeper (2018)

| | |
|---|---|
| Motor | Unity 2020.3.17, Mono (BepInEx 5 + Harmony) |
| Versões testadas | Steam, Windows, compilação 22583570, jogo base sem DLC |
| Projetos | [Back From The Grave](https://github.com/ZlordHUN/GYK-Back-From-The-Grave), [graveyard-keeper-multiplayer](https://github.com/Zonda001/graveyard-keeper-multiplayer); ambos em [DIRECTORY.md](../../DIRECTORY.md) |
| Nível de QA | automated (Back From The Grave 1.2.0 Beta com três correções; graveyard-keeper-multiplayer não testado aqui) |
| Última atualização | 2026-10-20 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores podem compartilhar um mundo de Graveyard Keeper com Back From The Grave (BFTG): um host e um cliente pelo Steam. Nossa suíte de dois clientes (entrada, cena introdutória compartilhada, movimento, sono, comida por atalho, ping) passa em 9/9, mas somente com três correções enviadas ao mod como pull requests. A versão distribuída 1.2.0 Beta ainda tem esses bugs. O mais perceptível: um cliente não consegue comer ou beber nada do próprio inventário ([issue #22](https://github.com/ZlordHUN/GYK-Back-From-The-Grave/issues/22)).

## <a id="existing-work"></a>Trabalhos existentes

Pesquisado em 2026-10-20: busca na web (expressões em inglês e russo), repositórios GitHub, diretório deste núcleo, issues e PRs. Ainda não pesquisados: páginas dos mods no Nexus e suas abas de bugs, guia Steam, Reddit e Discords dos autores.

- **[Back From The Grave](https://github.com/ZlordHUN/GYK-Back-From-The-Grave)** (ZlordHUN, MIT). Última versão 1.2.0 Beta (2026-09-04), último commit 2026-09-19. Cerca de 330 arquivos C#. Autoridade do host por salas Steam e P2P, além de descoberta LAN. O README lista tempo, clima, missões, tecnologia, fabricação, objetos do mundo, combate, itens deixados, zonas, trabalhadores, masmorras, pesca, diálogos e cenas compartilhados, além dos DLCs Stranger Sins, Game of Crone e Better Save Soul. Cada jogador mantém seu inventário. Existe configuração `MaxPlayers`, mas o README informa testes apenas com 2 jogadores. Issues abertas em 2026-10-20: #24 (ping de cerca de 400 ms), #23 (convidar alguém já em uma sala quebra a interface), #22 (cliente não usa comida), #21 (energia do cliente após dormir), #20 (contador do necrotério), #11 (bug de cena).
- **[graveyard-keeper-multiplayer](https://github.com/Zonda001/graveyard-keeper-multiplayer)** (Zonda001, MIT). Compilação mais recente v0.1.5-test2 (2026-08-30, pré-lançamento), último commit 2026-09-11. Principalmente dois arquivos C# grandes. Outro modelo: o segundo jogador tem salvamento pessoal e diário de missões próprio no mundo do host (modelo Stardew). O README lista movimento, tempo, corte de árvores, coleta, canteiros, túmulos, transporte de corpos, construção, fabricação, baús compartilhados e clima. Aldeões NPCs e criaturas de masmorras ainda não são sincronizados. Issues abertas: dessincronização de cliente com mensagens repetidas de NullReferenceException, bloqueio do host e duplicação de itens grandes. O repositório distribui `Steamworks.NET.dll` e `Stitch.dll` de 14 KB em `Multiplayer/lib`. Zonda001 também escreveu o transporte confiável (PR #9) e uma correção de posição de criação (PR #10) em BFTG.
- Não são projetos cooperativos: `maxcraft2222/Graveyard-Keeper-Multiplayer` (README e licença, sem código ou versões), `edfariamaia/GraveyardKeeper-multiplayer` (9 commits, sem licença, último envio em 2026-06). A busca GitHub também retorna repositórios de download gratuito de trainer; trate-os como iscas de malware.
- Graveyard Keeper 2 tem projetos cooperativos próprios. É outro jogo e não é coberto aqui.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Motor:** Unity 2020.3.17 com backend Mono, permitindo o caminho usual: BepInEx 5 x64, Harmony e descompilação de `Assembly-CSharp.dll` com ILSpy. O jogo usa Steamworks.NET 11.0.0 (SDK Steamworks 1.42), Rewired para entradas, interface no estilo NGUI (`BaseGUI`, `GUIElements.me`) e `MainGame.me` para o jogo em execução. Não há sistema antitrapaça nem código de rede.
- **Salvamentos:** `PlatformSpecific.GetSaveFolder()`, resolvido como `%USERPROFILE%\AppData\LocalLow\Lazy Bear Games\Graveyard Keeper`. Aplicar patch nesse método dá a cada cópia de teste uma pasta própria.
- **Segunda cópia em um PC:** `Graveyard Keeper_Data\boot.config` contém `single-instance=`; com essa linha, a segunda cópia encerra imediatamente. Remova-a somente das cópias de teste.
- **Inicialização:** a camada de entradas (Rewired/`LazyInput`) e a interface do menu principal não estão prontas durante o pré-carregamento. Uma interface de mod criada antes da primeira exibição do menu lança `NullReferenceException`. É o bug B1 abaixo.
- **Após a introdução**, a cama recusa a ação com "Can't do that right now." O modo de um jogador faz o mesmo, portanto não é bug do mod. Testes que precisam dormir abrem `SleepGUI` diretamente, como faz `Flow_CharSleep`.
- **Organização do código BFTG:** o csproj compila os arquivos das subpastas `src/**`. As cópias soltas em `src/*/*.cs` são excluídas; corrigi-las não faz diferença. O repositório também inclui uma DLL em `bin/Debug`; compile a partir do código-fonte. `GamePath` no csproj aponta por padrão à instalação Steam. Passe `-p:GamePath=<test copy>` para ler uma cópia de testes.
- **Rede BFTG:** metadados da sala Steam (`mod_version`, `protocol_revision`) e uma mensagem inicial de compatibilidade (`Op.Hello`) pelo canal confiável nativo do Steam decidem a admissão. Depois, o tráfego passa para RNET, camada confiável própria sobre P2P. Inventários: cada cliente envia ao host um snapshot que inclui seu próprio jogador (`player:local`), e o host aprova o uso de consumíveis pessoais com base nessa cópia.

## <a id="what-we-changed"></a>O que alteramos

Três correções de BFTG 1.2.0 (commit 432b1d0), cada uma com teste que falha sem ela. Foram enviadas ao upstream como pull requests: B1 [#25](https://github.com/ZlordHUN/GYK-Back-From-The-Grave/pull/25), B2 [#26](https://github.com/ZlordHUN/GYK-Back-From-The-Grave/pull/26), B3 [#27](https://github.com/ZlordHUN/GYK-Back-From-The-Grave/pull/27).

1. **B1: convite recebido durante o carregamento é perdido.** Se o convite chega antes do menu principal, criar ou abrir `JoinGameGUI` lança `NullReferenceException`, e o convite P2P enviado junto termina em "Error parsing invite". Nenhum é repetido. Correção: `SteamLobbyManager.IsInviteUiReady()` (jogo em execução ou menu principal já mostrado ao menos uma vez, sem tela de carregamento). Até lá, o convite Steam fica pendente e o P2P é adiado. A primeira versão verificava se o menu estava visível naquele momento, bloqueando convites normais porque as telas de entrada e sala o ocultam; `move_sync` detectou isso. Teste: `invite_during_load`. PR [#25](https://github.com/ZlordHUN/GYK-Back-From-The-Grave/pull/25).
2. **B2: o Ready do cliente nunca chega ao host.** Quem entra envia a mensagem inicial de compatibilidade pelo canal confiável nativo do Steam. Se os metadados da sala o validam antes, o host trata a mensagem tardia como tráfego da aplicação, `ReliableTransport.AcceptNativeInbound` fixa a rota como nativa e o cliente, já em RNET, descarta tudo que o host envia. Correção: o host sempre consome `Op.Hello` de membros da sala em `SteamP2PManager.HandleIncomingPacket` (verificação idempotente). A simulação entrega os dados da sala primeiro, portanto toda entrada falhava. No Steam real, depende do momento de chegada; não observado ali. Teste: `join_newgame`. PR [#26](https://github.com/ZlordHUN/GYK-Back-From-The-Grave/pull/26).
3. **B3: o cliente não usa comida ou poções do próprio inventário (issue #22).** O host aprova o uso com base na entrada `player:local` do snapshot do cliente, mas `InventorySync.ShouldSyncWgo` rejeitava todos os objetos de jogador, impedindo o envio dessa entrada. Correção: `ShouldSyncWgo` permite o jogador local somente nos clientes. Teste: `quickslot_food`. PR [#27](https://github.com/ZlordHUN/GYK-Back-From-The-Grave/pull/27).

Relatos de bugs não reproduzidos:

- **#21 (energia do cliente após dormir):** `sleep_energy` e `sleep_energy_client_first` passam. A energia começa a subir de 1,4 a 1,7 s após ambos deitarem, ambos acordam com 100/100 e os relógios diferem em até 0,0004 dia. Sem latência ou perda adicionadas.
- **#24 (ping de cerca de 400 ms):** o ping é de 12 a 27 ms no localhost (um ou dois quadros) e 213 ms com 100 ms adicionados em cada sentido; o mod acrescenta cerca de um quadro à ida e volta. A causa provavelmente está fora do mod ou depende da carga; não confirmada.

## <a id="qa"></a>QA

A estrutura "CoopQA" usa um plugin BepInEx exclusivo de testes e dois scripts Python. Executa host e cliente como duas cópias reais do jogo em um PC, com uma conta Steam.

- **Simulação Steam:** prefixos Harmony substituem as chamadas Steamworks.NET do mod (`SteamUser`, `SteamFriends`, `SteamMatchmaking`, P2P `SteamNetworking`, avatares) e o registro de `Callback<T>`/`CallResult<T>`. Salas e P2P passam por TCP localhost. Funcionamento e partes reproduzidas do Steam real: [networking-steam-spacewar.md](../../playbook/networking-steam-spacewar.md#unity-mono-games-mock-steamworksnet-not-the-dll).
- **Isolamento:** o plugin carrega antes do mod (GUID `aaa.coopqa`) e não faz nada sem `-coopqa` na linha de comando. Cada cópia tem instalação de teste, pasta de salvamentos (patch de `GetSaveFolder`) e arquivos de resultado/estado próprios. O inicializador encerra apenas processos que iniciou.
- **Bot:** listas internas de etapas chamam os mesmos métodos dos botões do menu e da barra de atalhos, aguardam com limite de tempo, verificam e gravam `RESULT: PASS` ou `RESULT: FAIL`. Um canal paralelo exclusivo de QA permite a cada bot publicar uma palavra de estado ("menu", "ate") para os demais. Cada teste verifica sua precondição, por exemplo, que o cliente realmente ainda não chegou ao menu no envio do convite.
- **Dados de teste:** `python run_qa.py make_fixture --save-fixture after_intro` salva o jogo do host após a introdução; testes que partem dali levam cerca de 35 s para preparar, em vez de 140 s.
- **Comandos:** `python run_qa.py <test> [--lag ms] [--drop rate] [--fixture after_intro]` para um teste, `python run_suite.py` para a suíte.

A suíte e suas verificações:

| Teste | Verificações |
|---|---|
| `join_newgame` | sala, convite, Ready, New Game, transferência do salvamento, ambos em jogo e conectados por 20 s |
| `invite_during_load` | cliente inicia 8 s depois; host convida antes da chegada ao menu; cliente ainda consegue entrar |
| `intro` | novo jogo, introdução compartilhada, ambos recuperam o controle |
| `move_sync` | jogadores caminham alternadamente; o outro lado os vê na posição informada |
| `sleep_energy`, `sleep_energy_client_first` | ambos deitam (host ou cliente primeiro); energia sobe em até 3 s após ambos deitarem, acordam totalmente descansados e com mesmo dia/hora |
| `quickslot_food` | cada jogador come pelo atalho 1; um item consumido e energia maior nos dois (host é controle) |
| `ping`, `ping --lag 100` | pelo menos 5 resultados de ping em 60 s, mediana abaixo do limite; sem e com 100 ms adicionais em cada sentido |

Última suíte, 2026-10-20, BFTG 432b1d0 com B1, B2 e B3:

```
RESULT: PASS   join_newgame  (79s)
RESULT: PASS   invite_during_load --stagger 8  (67s)
RESULT: PASS   intro  (146s)
RESULT: PASS   move_sync --fixture after_intro  (54s)
RESULT: PASS   sleep_energy --fixture after_intro  (65s)
RESULT: PASS   sleep_energy_client_first --fixture after_intro  (65s)
RESULT: PASS   quickslot_food --fixture after_intro  (50s)
RESULT: PASS   ping --fixture after_intro  (100s)
RESULT: PASS   ping --fixture after_intro --lag 100  (107s)

SUITE: 9/9 passed in 12.2 min
```

Verificação de mutação: sem B1, `invite_during_load` falha (cliente nunca entra). Sem B2, `join_newgame` falha em "P2 ready" em 4 de 4 execuções. Sem B3, o cliente falha em `quickslot_food` em 3 de 3, enquanto o host passa.

Limites: tudo roda em localhost pela simulação, sem cobrir Steam real (retransmissão, convites pela sobreposição, ordem real de dados da sala e P2P). Movimento usa `GoTo` por script, não teclado. Sono abre `SleepGUI` diretamente. Apenas dois jogadores.

## <a id="how-to-play"></a>Como jogar

Instale BepInEx 5.4.x x64 e a DLL do mod das [versões BFTG](https://github.com/ZlordHUN/GYK-Back-From-The-Grave/releases) nos dois PCs, seguindo o README do mod e usando a mesma versão em ambos. Se o cliente não possui um DLC, desative-o nas configurações do host (`EnableDLCStories`, `EnableDLCRefugees`, `EnableDLCSouls`) antes de criar a sala. Faça backup dos salvamentos primeiro. As correções acima só estarão em uma versão distribuída após o autor incorporá-las.

## <a id="known-issues"></a>Problemas conhecidos

- Na 1.2.0, o cliente não usa comida ou poções do próprio inventário (#22; corrigido por B3, [PR #27](https://github.com/ZlordHUN/GYK-Back-From-The-Grave/pull/27), ainda não distribuída).
- Convite que chega enquanto o jogo carrega é perdido; convide novamente quando o amigo chegar ao menu (corrigido por B1, [PR #25](https://github.com/ZlordHUN/GYK-Back-From-The-Grave/pull/25), ainda não distribuída).
- Convidar jogador que já está em uma sala quebra a interface (#23).
- Jogadores relatam ping de cerca de 400 ms (#24), contador do necrotério mostrando 1 sem cadáver (#20) e bug de cena (#11).
- Mais de dois jogadores não foi testado.

## <a id="next-steps"></a>Próximos passos

- Obter revisão e incorporação de B1, B2 e B3 no upstream ([#25](https://github.com/ZlordHUN/GYK-Back-From-The-Grave/pull/25), [#26](https://github.com/ZlordHUN/GYK-Back-From-The-Grave/pull/26), [#27](https://github.com/ZlordHUN/GYK-Back-From-The-Grave/pull/27)).
- Testar Steam real com duas contas em dois PCs: retransmissão, convites pela sobreposição e ocorrência de B2.
- Repetir testes de sono e ping com `--lag` e `--drop`. Pista para #24: no Steam real, no menu sem conexão, o recebimento P2P levou de 12 a 15 ms por quadro (um log, sem medição por teste).
- Acrescentar testes para #23 (convite a alguém já em sala), #20 e #11.
- Experimentar graveyard-keeper-multiplayer com a mesma estrutura. Também usa Steamworks.NET, podendo reaproveitar a simulação (ainda não tentado).
