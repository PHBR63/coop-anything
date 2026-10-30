# <a id="gedonia-2022"></a>Gedonia (2022)

| | |
|---|---|
| Motor | Unity 2019.4.20, execução Mono (Assembly-CSharp.dll), NGUI, céu Enviro, A* Pathfinding, DunGen |
| Versões testadas | Steam, aplicativo 1114220, compilação 16727998 (Gedonia.exe SHA-256 B375205374C5355991FE1C91577CEB729AD9FBC2FC6534FE4EF897288A5DF91B), Windows 11 x64 |
| Projetos | [Gedonia Co-op](https://github.com/Zerbith/gedonia-coop) (entrada "Gedonia / Gedonia Co-op"), reivindicação [#214](https://github.com/cranebeaker/coop-anything/issues/214) |
| Nível de QA | automated |
| Última atualização | 2026-10-26 |

Este é o Gedonia original, não Gedonia 2 (que tem cooperação oficial).

## <a id="where-things-stand"></a>Situação atual

Dois ou mais jogadores podem explorar mundo aberto e história juntos pelo Steam (amigos, convites internos, retransmissão) ou pela rede doméstica. Jogadores, inimigos, história, conversas, pontos de saque, eventos, expedições com masmorras geradas, tempo e clima são compartilhados. Cada recurso tem cenário automatizado com dois clientes; sessões reais com amigos pelo Steam correram bem e os problemas encontrados (0.6.x) estão corrigidos em 0.7.x. Estado: alfa (0.7.1).

## <a id="existing-work"></a>Trabalhos existentes

Nenhum encontrado antes deste projeto (busca web, Nexus, issues e pull requests deste repositório, 2026-10-24).

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Sem código de rede.** UNet só aparece nos exemplos de céu Enviro incluídos. O jogo distribui Steamworks.NET 12 (SDK 1.42) em Assembly-CSharp-firstpass: SteamNetworking P2P clássico com retransmissão alternativa, salas, amigos e presença detalhada; sem SteamNetworkingMessages. Usa seu próprio identificador de aplicativo.
- **Singletons em toda parte.** `PlayerScript.instance` é referenciado cerca de 11.400 vezes. Cada máquina mantém um jogador local e representantes dos demais: clone da raiz (`PlayerFinal`) criado sob contêiner inativo (sem executar Awake), reduzido a Transform/Animator/renderizadores/PlayerModelCustomization, depois ativado sem movimento de raiz ou eventos de animação.
- **Aparência** aplicada por `PlayerModelCustomization.RefreshPlayerModel(...)`, que também lê o jogador LOCAL (visibilidade de capacete/capa em PlayerPrefs, aljava pela arma local, luz da tocha pela furtividade local). Esses valores precisam ser enviados e definidos no representante antes da chamada.
- **Inimigos:** IA `FighterNPCModule` executa de `NPC.Update` por `npc.updateFunction`; todo dano passa por `NPC.Damage(7 args)`. A busca de alvo quer etiqueta "Player"; inimigo atacante abandona alvo sem essa etiqueta ou componente NPC, então os representantes carregam componente NPC desativado. Inimigos em células carregadas dinamicamente (World Streamer, cenas `MediumStr__x..._z...`) carregam/descarregam pela distância.
- **História:** cerca de 980 métodos públicos em `GameManager`, chamados por nome com `GameManager.instance.SendMessage(name)` de respostas de diálogo, confirmações de mistérios, interruptores, sequências e eventos. Missões: `QuestsData.AddQuest/ObjectiveCompleted/ReturnQuest`. Diálogo: `DialogueNPCModule.Talk` → `InterfaceManager.RefreshDialogue` (botões nomeados por índice de resposta, requisitos verificados no jogador local) → `OnDialogueButton`.
- **Estado do mundo:** `SaveLoadManager.WorldDatabase` (Dictionary<int,string>) com identificadores `SaveableItem`; contêineres, minérios e ervas são `Container`, com saque retirado em `InterfaceManager.TakeLootItem`.
- **Salvamentos:** arquivos Easy Save 3 em `%USERPROFILE%\AppData\LocalLow\Oleg Kazakov\Gedonia`, PlayerPrefs em `HKCU\Software\Oleg Kazakov\Gedonia`, ambos nomeados pelo produto Unity (consulte a lição dos guias).
- **Tempo e clima:** Enviro (`EnviroSky.GameTime`, sorteios aleatórios de clima por zona).
- **Expedições:** sorteadas por UnityEngine.Random em cada máquina; fases de masmorras usam DunGen com `ShouldRandomizeSeed = true` (a semente armazenada era ignorada).
- **Viajantes:** `TravellersManager` mantém posição virtual por viajante (46: comerciantes, bardos, sábios, cidadãos, coelhos), criando o NPC quando o jogador local se aproxima; cada salvamento os tinha em posições diferentes.
- Ferramentas: ilspycmd 9.1 para descompilar, BepInEx 5.4.23.5 + HarmonyX; plugin compilado com csc do .NET Framework que acompanha Windows (C# 5).

## <a id="what-we-changed"></a>O que alteramos

Tudo no plugin [Gedonia Co-op](https://github.com/Zerbith/gedonia-coop); cada item tem cenário de teste (`scripts/test-local.ps1 -Scenario <name>`).

- **Transporte:** `ITransport` com Steam P2P (sala só para amigos, convites pela lista interna, solicitações de entrada) e UDP com canal confiável próprio (numeração, confirmações, reenvios). Simulação da API Steam por UDP de loopback segue suas regras (sessões retidas até aceitação, limites de tamanho, perdas), permitindo testar o caminho Steam com dois clientes num PC.
- **Jogadores** (walk, looks, bow): modelo representante, espelhamento de animação (correspondência do clipe dominante da camada 0 cerca de 98%, erro de parâmetro Speed 0), hash de assinatura visual conferido dos dois lados, equipamento/capacete/capa/armas de mods, nome Steam, marcadores em mapa global/minimapa/bússola.
- **Inimigos** (fight, apart, lossy, death): relatos de presença, host escolhe responsável por inimigo com épocas e tempo de retenção; responsável publica, outros espelham e solicitam dano; mortes executam em toda parte, dando corpo saqueável individual a cada jogador. `scripts/check-ownership.ps1` falha se inimigo recebe responsabilidade dupla consecutiva. Bug encontrado: exceção num inimigo cuja célula descarregara abortava o restante da mensagem de responsabilidade. Bug encontrado por jogadores: saquear grava "0" para o corpo no banco do mundo e a sincronização do host apagava o corpo para todos; agora um cadáver permanece até ser saqueado localmente.
- **XP compartilhada** (effects): `PlayerScript.AddExperience` multiplica por intelecto, anéis, sono e bênçãos de masmorra; abates iguais davam XP diferente e níveis divergiam. Mortes copiadas não dão XP; a máquina da morte real envia o valor ganho e jogadores a até 100 m adicionam exatamente isso (subidas de nível pelo ciclo nativo).
- **História** (story, latejoin): transpiler Harmony troca `SendMessage` nos locais de resposta/gatilho por despachante; host numera chamadas e todas as máquinas executam a mesma função nessa ordem; resumos de missões reparam atrasos; alterações no banco do mundo são enviadas a participantes tardios.
- **Conversas compartilhadas** (dialogue): anunciadas; jogadores próximos entram com F; cliques são votos; consenso decide imediatamente, senão vale voto do iniciador após tempo configurável (ou só consenso); requisito de atributo é satisfeito se qualquer integrante o cumprir; custos em dinheiro/itens exigem um integrante que os possua, e só ele paga (a função da história executa em todas as máquinas, então nas demais a remoção de itens é ignorada e o ouro devolvido nessa chamada); só o líder despacha a função.
- **Efeitos e transformações** (effects): `Object.Instantiate` de prefabs `PlayerScript.effectsGos` e `ParticleSystem.Play` no jogador são enviados; receptores criam prefab sob contêiner inativo e removem todos os scripts não visuais e todos os colisores antes de ativar, evitando dano pelas cópias. Formas de lobisomem, demônio de sangue e elementais são corpos separados da mesma lista de prefabs; jogador transformado transmite corpo, posição e todos os estados Animator; os demais mostram uma cópia em vez do representante.
- **Cenas:** `TimelineCutsceneController.StartCutscene` é retido em cooperação; cada jogador segura a tecla de interação até preencher um anel, então host inicia para todos. Os outros ficam ocultos durante a cena.
- **Saque** (loot, farloot, chestgold, chestlid): trava por contêiner concedida pelo host, retiradas transmitidas e aplicadas por item; contêineres não carregados as aplicam quando carregam.
- **Eventos e expedições** (event, eventhandover, expedition, expfull): responsável cria, outros constroem os mesmos inimigos com identificadores iguais; listas de expedições vêm do host, geração usa identificador armazenado como semente (também DunGen); todos os tipos de fase de expedição foram jogados até o fim.
- **Companheiros e invocações** (companions, summons): cada jogador controla seguidores; outros veem espelhos criados do mesmo prefab Resources.
- **Relógio/clima** (clock), **mundos e masmorras** (worlds, dungeon), **viajantes** (travellers), **sons** (postfix Harmony em `AudioSource.PlayOneShot/Play`: nome e caminho do clipe enviados, reproduzidos no representante ou espelho), **pausa** (menu não para mais o tempo em cooperação), **cristais de reaparecimento** (respawn, respawnnorth: o jogo só recarrega ao morrer, o que voltaria o mundo; em cooperação, caído levanta num cristal vinculado com F; cristais ficam em pontos medidos, pois procurar local seco em cada PC colocou um num lago cuja água carregou tarde num PC lento).

## <a id="qa"></a>QA

- `scripts/test-local.ps1 -Transport udp|steam-mock -Scenario <name>` inicia duas cópias (segunda por hardlinks; nome de produto Unity próprio por cópia, separando salvamentos/configurações) com salvamento fixo, executa etapas temporizadas e bots em ambas, registra observações de cada lado (posições, animações, assinaturas visuais, responsabilidade, eventos de história, votos) e capturas de tela.
- 35 cenários. Últimas execuções em 2026-10-26, código 0.7.x: diálogo (resposta paga em ouro só pelo amigo, ouro do host inalterado, mercenário acompanha quem pagou), efeitos (UDP e simulação Steam: golpes do amigo e feitiços do host exibidos no outro lado, ambos de 33 para 183 XP com intelectos 2 e 8, corpo saqueado pelo host continua disponível ao amigo), transformações (seis formas exibidas, representante oculto), cena (retida até ambos segurarem a tecla, iniciada nos dois com diferença de até 10 ms; soltar cedo reinicia o anel), reaparecimento no cristal medido, história; 0 erros em ambos os logs BepInEx. Marcos anteriores (inimigos com 20% de perda, fases de expedição, entrada tardia) no histórico do repositório do mod.
- Após cada execução, salvamentos reais e valores do registro comparados ao backup (inalterados).
- Cliques reais nas janelas de teste não foram automatizados (sem controle da área de trabalho). Testador e amigos usaram menus e conversas compartilhadas manualmente em sessões reais até 0.6.x; adições de 0.7 (anel de confirmação, transformações) só testadas pelos cenários automatizados até agora.

## <a id="how-to-play"></a>Como jogar

Baixe o ZIP nas [releases](https://github.com/Zerbith/gedonia-coop/releases), execute `Install.cmd` (localiza pelo Steam, faz backup dos salvamentos, baixa BepInEx 5.4.23.5 conferindo SHA-256). Menu principal: "Host co-op" (Steam ou rede doméstica) e "Join co-op"; no jogo, botão cooperativo na barra superior ou F8. Todos precisam da mesma versão do mod.

## <a id="known-issues"></a>Problemas conhecidos

- Teletransportes da história movem todos os jogadores.
- Convite na sobreposição Steam pode não abrir quando o jogo inicia fora do Steam; a lista de amigos interna funciona.
- Modos Arena, Survival e Dungeon (separados no menu principal) não ajustados para cooperação.
- Companheiros dos outros permanecem visíveis durante cenas.
- "Uncharted Islands" inacessíveis nesta versão (sem rota de viagem).

## <a id="next-steps"></a>Próximos passos

- Sessões em rede real com mais de dois jogadores.
- Conversa interna (menu cooperativo tem espaço reservado).
- Narração dos textos de missões (TTS) planejada.
