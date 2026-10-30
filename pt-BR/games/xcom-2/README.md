# <a id="xcom-2-war-of-the-chosen-2017"></a>XCOM 2: War of the Chosen (2017)

| | |
|---|---|
| Motor | Unreal Engine 3 (UnrealScript, SDK oficial de mods) |
| Versões testadas | Steam, XCOM 2 buildid 8270065 (changelist 699444), War of the Chosen + todos os DLCs, Windows x64 |
| Projetos | Team Dragonpunk "Tactical Co-Op" (2016, abandonado); WOTC Co-op Campaign (protótipo, este relato): https://github.com/EvilMask587/xcom2-wotc-coop-campaign |
| Nível de QA | automated (somente camada estratégica; consulte QA) |
| Última atualização | 2026-10-25 |

## <a id="where-things-stand"></a>Situação atual

Ainda não é possível jogar uma campanha cooperativa. Um mod protótipo compartilha a camada estratégica (Avenger): ambos veem a mesma campanha e se alternam nas alterações (um "bastão" de controle), e uma suíte de testes por script com duas instâncias verifica se o estado permanece idêntico. As missões táticas ainda não são compartilhadas.

## <a id="existing-work"></a>Trabalhos existentes

- **Team Dragonpunk, "XCOM 2: Tactical Co-Op"** (Steam Workshop 792693587): criado em 3 de novembro de 2016, última atualização em 3 de setembro de 2017, estado "Final". Dois jogadores dividem o esquadrão nas missões da campanha; soldados podem ser importados do jogo do amigo; sem Ironman. Somente camada tática, sem estratégia compartilhada. Provavelmente anterior ao WotC (última atualização 5 dias após WotC). Nenhum código-fonte público encontrado (busca GitHub "xcom2 coop", "dragonpunk xcom": nenhum resultado). https://steamcommunity.com/sharedfiles/filedetails/?id=792693587
- **robojumper, "WOTC Multiplayer mods"** (Workshop 1571537500): permite executar mods no multiplayer PvP nativo; descontinuado gradualmente em favor do Community Highlander. Não é cooperativo.
- Multiplayer nativo: somente PvP tático.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- Tudo que importa é um **histórico de estados do jogo** (`XComGameStateHistory`): uma lista de quadros, cada qual com objetos de estado alterados e ObjectIDs estáveis. Estratégia e tática usam esse histórico. O SDK de mods inclui todo o código-fonte UnrealScript (`Development/SrcOrig`).
- `XComGameStateNetworkManager` (nativo, chamável por script) já transporta históricos: `SendHistory`, `SendPartialHistory`, `SendMergeGameState`, `SendRemoteCommand` com parâmetros tipados e delegates de recepção. O PvP nativo usa "o jogador ativo é a autoridade": executa o conjunto de regras e envia um histórico parcial no fim do turno.
- Transporte: `IpNetDriverSteamworks`, IP simples ou sockets Steam. No modo IP, o host do cliente precisa ser UM inteiro decimal (127.0.0.1 -> "2130706433"); um host com pontos não envia nada. Cliente e servidor no mesmo PC precisam de portas diferentes.
- Delegates do gerenciador de rede devem apontar para Objects simples: ele sobrevive aos mapas, e um delegate vinculado a um Actor mantém o World antigo vivo (asserção no carregamento do mapa seguinte).
- Cada quadro submetido em um lado é enviado ao parceiro com `SendMergeGameState`. Um estado de mesclagem é aplicado ao quadro atual do receptor (não acrescenta um quadro), então a quantidade de quadros difere; compare conteúdo, não índices. Quadros sem objetos são recusados por SendMergeGameState. Comandos remotos enviados após um estado de mesclagem são tratados antes dele; vários quadros de um tick podem chegar em uma só mesclagem.
- Estados de mesclagem levam objetos novos e removidos com seus ObjectIDs; o contador de identificadores do receptor avança além deles. Se AMBOS os lados criarem objetos, atribuem o mesmo ObjectID, e a mesclagem substitui silenciosamente um objeto pelo outro (testado), justificando um editor por vez.
- Duas instâncias em um PC: o executável mantém o mutex `UnrealEngine3_<n>`; fechar esse handle na primeira instância permite iniciar a segunda. `-nohomedir` mantém configurações, logs e salvamentos na pasta de instalação.

## <a id="what-we-changed"></a>O que alteramos

Mod: https://github.com/EvilMask587/xcom2-wotc-coop-campaign (somente código, sem arquivos do jogo). Detalhes e todas as execuções de testes em [NOTES.md](NOTES.md).

- **Entrada do cliente sem efeitos pós-missão.** Um simples `open Avenger_Root` trata o histórico recebido como retorno de missão e acrescenta 7 quadros e novos ObjectIDs. `CoopHeadquartersGame` (ModClassOverrides) usa o caminho de carregar jogo; sobra somente um quadro inevitável "Pre Mission End UI Sequence Hook".
- **Falsas dessincronizações.** O comando de impressão digital ultrapassava seu estado de mesclagem; agora a comparação ocorre quando o estado chega.
- **Colisões de ObjectID.** O jogador sem o bastão podia criar objetos com identificadores novamente atribuídos pelo detentor. `CoopStrategyRuleset.SubmitGameStates` rejeita quadros que criem objetos sem o bastão (novo = `GetPreviousVersion() == none`; `GetGameStateForObjectID` já resolve identificadores pendentes e nunca informa "novo").
- **Condição de corrida na transferência do bastão.** Uma concessão podia chegar antes dos últimos estados de mesclagem do detentor. O receptor aguarda a impressão digital e o maior ObjectID corresponderem à concessão e passar 1 s sem quadros. Contar mesclagens falhou (comandos e mesclagens não formam pares).
- **Buracos nas salas.** RemoveRoom + StreamInRoom (usados pelo cheat GiveFacility) deixavam salas parcialmente desenhadas. O receptor agora enfileira uma troca como `XGBase.QueueRoomSwap`.
- **Edições perdidas no jogador sem controle.** Toda tela de edição pede primeiro o bastão (diálogo com Cancel); o detentor o transfere quando suas telas de edição fecham; há painel no HUD com "Ask for control".

## <a id="qa"></a>QA

- Duas instâncias em um PC, cada uma com cópia própria do jogo; um bot interno ao mod executa uma lista de etapas por instância; `tools/test_suite.ps1` no repositório do mod verifica ambos os logs: linhas esperadas, ausência de DESYNC / falha / identificadores duplicados de tripulantes / salas obsoletas / limites de tempo excedidos pelo bot e impressões digitais finais iguais.
- Cenários: `baton-objects` (recursos e unidades nas duas direções, concessão logo após um quadro, cadeias de versões verificadas), `facility` (instalação removida e reconstruída, trocas de sala no cliente), `blocked-without-baton`, `edit-gate` (solicitações adiadas enquanto uma tela de edição está aberta, nas duas direções), `clock` (tempo do Geoscape), `projects` (pesquisas e construções iniciadas por um jogador terminam no Geoscape do outro), `rejoin` (processo do cliente encerrado enquanto detém o bastão, reconecta e recebe o histórico novamente), `burst` (muitos quadros em um tick), `client-save` e `client-save-menu` (somente o host salva), `panel-replies` (botão do HUD, respostas adiadas / de outro jogador, Cancel).
- Último resultado da suíte: 11/11 aprovados (2026-10-25, `tools/test_suite.ps1`), um PC, duas instâncias, 127.0.0.1.
- Um salvamento do host feito após receber as mesclagens do cliente recarrega a mesma campanha (impressão digital e tripulação iguais; tempo do Geoscape avança; novo salvamento funciona), conferido manualmente com `@save` / `@load N` do bot (2026-10-25).
- Capturas de tela feitas pelo bot foram conferidas visualmente para trocas de sala, diálogo de espera e painel do HUD.
- Escopo: um PC, duas instâncias, somente camada estratégica. Fora do escopo: dois PCs, rede Steam, sessões longas, queda do host e qualquer elemento tático.

## <a id="how-to-play"></a>Como jogar

Ainda não está jogável. Desenvolvedores: instruções de compilação e teste no README do repositório do mod.

## <a id="known-issues"></a>Problemas conhecidos

- Sem modo cooperativo tático; o protótipo compartilha apenas o Avenger.
- Quem permanece no Geoscape mantém o controle até sair dele.
- Avisos (pesquisa concluída, instalação construída, novas missões) aparecem somente para quem está no Geoscape.
- Uma falha do cliente ao entrar manualmente nas instalações (carregamento de pacotes do motor, tbbmalloc), não reproduzida.

## <a id="next-steps"></a>Próximos passos

- Dois PCs e sockets Steam.
- Fluxo de entrada para partidas reais: host envia o histórico quando um cliente entra (atualmente feito pelo bot), opção de menu para hospedar/entrar.
- Tática: manter um jogador XCom e dividir seu turno em subfases por jogador, com o responsável pela subfase como autoridade e `SendPartialHistory` em cada transferência (modelo PvP).
- Seleção de esquadrão: cada jogador escolhe soldados; travas por soldado.
