# <a id="battletech-2018"></a>BattleTech (2018)

| | |
|---|---|
| Motor | Unity 2018.4 (Mono), código C# (`Assembly-CSharp.dll`); mods carregam pelo ModTek 4.5.1 (HarmonyX com camada de compatibilidade Harmony 1.2) |
| Versões testadas | Steam app 637090, build id 20387569, BattleTech 1.9.1 (BuildNumber 686R). SHA-256 de `BattleTech.exe`: `a12620dd89f2a7fc51fe228d38ba656574228a1c9412c27ca556fee08c5fc42f`; de `Assembly-CSharp.dll`: `9eaa1b3a4dfd80ac03abd47097541e9883a4fa4d4021d877b9b8faa2d23c8b2d`. Windows 11. |
| Projetos | [battletech-coop](https://github.com/Cryswar/battletech-coop) (MIT, em desenvolvimento, entrada `battletech-coop`); um projeto separado de outro desenvolvedor é listado como "BattleTech Co-op (Co-op Anything Discord)" |
| Nível de QA | automated (duas cópias reais em um PC, por scripts), além de sessões humanas Steam com dois jogadores |
| Última atualização | 2026-10-21 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores podem jogar escaramuças e missões de Campaign ou Career juntos pelo Steam e compartilhar a companhia entre missões: **pré-alpha, não concluído**. Em missão, todos comandam todos os 'Mechs da lança do jogador; o jogo do host tem autoridade, e o convidado reproduz as mesmas ordens. Entre missões, o convidado vê a companhia do host e pode reformar, reparar, renomear, preparar, armazenar e desmontar 'Mechs; treinar, renomear, contratar e dispensar pilotos; comprar e vender; cancelar ordens de serviço e personalizar a companhia. O host aplica tudo e suas próprias mudanças chegam ao convidado. Ambos assistem à abertura da missão (câmera, nave de desembarque, conversa inicial) e a avançam juntos. Ainda não há lanças por jogador.

## <a id="existing-work"></a>Trabalhos existentes

- **battletech-coop** (este relato), [github.com/Cryswar/battletech-coop](https://github.com/Cryswar/battletech-coop), iniciado em 2026-10-16, versões 0.0.2 a 0.0.13 (ZIPs de pré-lançamento com ModTek).
- **BattleTech Co-op (Co-op Anything Discord)**: outro desenvolvedor publicando progresso no tópico BattleTech do Discord Co-op Anything; sem versão pública quando este texto foi escrito. Veja sua entrada no diretório.
- Nenhum mod cooperativo anterior de campanha encontrado (Nexus, GitHub, fóruns Steam, 2026-10-16). O jogo oferece multiplayer competitivo apenas em escaramuças. Mods comunitários relevantes: ModTek (carregador), Mission Control e Bigger Drops (mais unidades do jogador por desembarque), BattleTech Advanced 3062 (pacote grande, não coberto pelos testes).

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

Detalhes e fontes em [NOTES.md](NOTES.md); arquitetura completa e todas as execuções de testes em [docs/DESIGN.md](https://github.com/Cryswar/battletech-coop/blob/main/docs/DESIGN.md) do projeto.

- **O combate já tem camada lockstep.** Toda ação é uma `InvocationMessage` (movimento com caminho completo, ataque, corpo a corpo, salto, trava de sensores, reserva...), passa por `InvocationHandler.GenericInvoke`, que redefine a semente do gerador aleatório lógico (`NetworkRandom`, XorShift de semente fixa) com o `RandomSeed` da própria invocação. O modo competitivo retransmite essas mensagens; o modo de um jogador usa o mesmo caminho sem retransmissão. Portanto, combate cooperativo é lockstep determinístico de invocações, com host ordenando tudo.
- **A IA não é determinística entre PCs** (limite de tempo de decisão de `Time.realtimeSinceStartup`, `UnityEngine.Random` nas escolhas de reserva), mas produz invocações comuns. Só a IA do host pensa; o convidado recebe os resultados pelo fluxo.
- **O serializador do jogo** (`BattletechSerialization`, usado por `NetworkMessageResolver`) serializa e desserializa invocações e contratos; salvamentos são bytes de `SaveBlock<GameInstanceSave>`.
- **A campanha (`SimGameState`) não tem camada de comandos.** As telas chamam métodos diretamente (`InitializeMechLabEntry`, `UpgradePilot`, `StarSystem.HirePilot`, `Shop.Purchase`...); não usa lockstep: o host é responsável, e a cópia do convidado recebe uma captura de estado e mudanças espelhadas.
- **Salvamentos** são arquivos Steam Cloud na pasta do usuário Steam (`userdata/<id>/637090/remote/C0/SGS1`); cópias de teste da instalação os compartilham, então testes nunca devem salvar.

## <a id="what-we-changed"></a>O que alteramos

Mod ModTek escrito para a API Harmony 1.2; transporte por salas Steam e P2P confiável `SteamNetworking` (blocos de 512 KB), com TCP para testes.

- **Lockstep de combate.** Um prefixo em `GenericInvoke` registra toda invocação no host e a transmite com número de sequência; o convidado reproduz em ordem. Ordens do convidado viram solicitações validadas pelo host, que atribui novo ID (`G<player>.<n>`) e publica. Ativações de turno são contadas dos dois lados; a IA do convidado nunca pensa. Resumo por unidade de posição, blindagem e todas as estatísticas (independente de cultura, componentes com chave `def@location`) é comparado após cada ativação; unidades ainda executando ordens são ignoradas, pois geravam alarmes falsos. Testes: `-Combat` (IA joga dos dois lados, convidado reproduz) e `-Shared` (metade das ordens são solicitações do convidado), ambos com `-InjectDesyncAt` como variante de mutação que deve produzir FAIL.
- **Missões de campanha por salvamento.** Contrato regenerado no convidado seria diferente; o host constrói um `GameInstanceSave` em memória e envia, e o convidado carrega por `LoadTransitioning.FileReadComplete`. Até 0.0.12, o salvamento era obtido no primeiro momento em que `CombatGameState.CanSave` permite, após a abertura; o host também recarregava, pois combate carregado não é idêntico ao estado ativo de origem (componentes retornam em ordem diferente; acerto crítico atingiu outro componente). Salvar fica bloqueado no convidado (`TriggerSaveNow`, `SaveGameStructure.Save`, `SaveCampaignResult`) e nas cópias de teste.
- **Abertura para ambos (0.0.13).** O host agora obtém o salvamento no briefing; o convidado carrega com indicação de reinício de combate (`GameInstanceSave.flaggedForRestart`; popup "mission save out of date" é ignorado). `GameInstance.CreateCombatFromSave` executa `Contract.ResetStateForRestart` e um novo `LaunchContract`; ambos iniciam a mesma missão desde o começo sem recarregar no host. O reinício relê a definição e sorteia novamente lanças inimigas por etiquetas (primeira execução: 6 atores no host, 7 no convidado); o host envia as escolhas (lança, unidade, piloto por ponto de criação) com o salvamento, e um postfix em `ResetStateForRestart` as restaura como IDs explícitos. "Begin mission" é compartilhado (aguarda todos os briefings carregarem); falas (`InterruptDialogSequence.AfterDialogHide`, Continue) passam pelo host, que avança e manda os convidados acompanhar. Conversas secundárias temporizadas não são sincronizadas.
- **Visão da nave.** Entre missões, o host envia a campanha como salvamento em memória; o convidado carrega da mesma forma. O novo `SimGameState` existe antes da aplicação do salvamento (companhia padrão, fundos 0); "carregado" significa que `_OnAttachUXComplete` disparou para a companhia recebida. Descoberto no primeiro teste da nave, que comparou companhias e falhou no estado provisório.
- **Mudanças na nave nos dois sentidos.** Capturadas onde as telas chamam o jogo (`InitializeMechLabEntry` para reformas e reparos, `UpgradePilot`, `HirePilot`, `Shop.Purchase`/`SellInventoryItem`, `ReadyMech`, `UnreadyMech`, `Scrap*Mech`, `DismissPilot`, `CancelWorkOrder`, fechamento da tela de heráldica) e enviadas como dados (ordens de instalação/blindagem/estrutura/reparo, pilotos como níveis-alvo de habilidades). O outro lado repete pelas mesmas funções com seus objetos; custos, tempo de reforma e armazenamento comportam-se como no jogo de um jogador. Ao aplicar mudança remota, patches de captura ficam silenciosos (sem eco); em chamadas aninhadas, só a mais externa é enviada.
- **Mesmos IDs em toda cópia.** Pilotos e 'Mechs novos recebem IDs de um contador (`"SGRef_" + ++UIDCount`). Cada alteração leva o contador inicial de seu lado e é aplicada a partir dele; o convidado conta em faixa própria (1e9 × índice do jogador acima do host), impedindo colisões. Sem isso, um piloto contratado no convidado e dispensado depois não seria encontrado no host.
- **Telas abertas são redesenhadas** após mudança remota (Mech Bay `RefreshData`, Barracks `Reset`, listas Store e Hiring Hall), aguardando enquanto MechLab estiver aberto ou um piloto tiver treinamento não confirmado (`SGBarracksWidget.IsCurPilotModified`).
- **Fim de sessão.** Encerrar limpa todo estado de sincronização de combate (estado antigo impedia hospedar novamente); convidado cujo host sai retorna ao menu principal.

## <a id="qa"></a>QA

Execute no repositório do projeto (Windows PowerShell, duas cópias do jogo; veja seu README):

- `tools/two-copy-test.ps1` inicia host e convidado por TCP localhost com `-coop-no-saves`, controla por modos internos, verifica os dois logs e fecha as cópias. Modos: simples (conexão), `-Combat [-Shared] [-SaveTransfer] [-InjectDesyncAt n]`, `-HostQuitTest`, `-ShipView`, `-ShipRequests`.
- `-ShipRequests` faz as duas cópias alterarem a companhia (renomear e reformar 'Mechs, treinar e renomear pilotos, contratar, comprar, vender, armazenar e preparar um 'Mech, cancelar essa ordem, dispensar contratação do outro lado, renomear companhia) e compara resumo de companhia, fundos, pilotos, baias, ordens, quantidades armazenadas e pilotos disponíveis; o último resumo do host precisa ser igual ao final do convidado. Também exige redesenho de Barracks no host.
- `dotnet run --project tests/NetTests`: núcleo de rede com sockets reais localhost.

- `-MissionStart`: host carrega salvamento de carreira, envia a nave e lança o primeiro contrato comum como o Accept da tela de lança; exige que ambos terminem o diálogo inicial com falas idênticas na mesma ordem, pressionamentos de Continue dos dois lados e, depois, itens do fluxo sem dessincronização.

Últimos resultados (2026-10-25, versão 0.0.13): `-MissionStart` PASS (mesma batalha de 8 unidades nos dois, 10 escolhas fixadas, mesmas 3 falas iniciais, 48 itens no fluxo, 0 dessincronizações); `-Combat -Shared` PASS (60 itens, 0 dessincronizações). 2026-10-18, versão 0.0.12: `-ShipRequests` PASS (9 solicitações e 9 atualizações aplicadas, nenhuma recusada, 'Mech preparado com mesmo ID nos dois, resumos iguais). Antes: missão completa com transferência de salvamento e comparação de todas as estatísticas PASS (176 itens, 38 ordens do convidado, 0 dessincronizações), `-InjectDesyncAt` detectado como exigido, `-HostQuitTest` PASS.

Sessões humanas (dois jogadores em dois PCs pelo Steam): missão de campanha com 77 ordens (17 do convidado: movimentos, ataques, salto, corpo a corpo, DFA), 0 dessincronizações; solicitações da nave (renomear e treinar piloto, renomear 'Mech, reforma) aplicadas no host, nenhuma recusada.

## <a id="how-to-play"></a>Como jogar

Baixe o ZIP em [releases](https://github.com/Cryswar/battletech-coop/releases) (pré-lançamento). Todos instalam o mesmo ZIP (ModTek e mod) na pasta do jogo; `BattletechCoop-README.txt` incluído explica instalação, hospedagem, entrada e desinstalação. O host carrega a campanha, abre a janela cooperativa (Ctrl+Shift+C), hospeda pelo Steam e convida; amigos aceitam o convite no menu principal.

## <a id="known-issues"></a>Problemas conhecidos

- A abertura compartilhada (0.0.13) só foi testada em contratos comuns, não em missões da história ou Flashpoints. Conversas secundárias durante missões não são sincronizadas.
- Todos controlam a lança inteira; ainda sem lanças por jogador ou desembarques maiores.
- Viagens, passagem do tempo e aceitação de contratos são do host; se o convidado fizer em sua cópia, perdem-se na próxima atualização. Retratos de pilotos não são sincronizados.
- Atualização completa da nave leva 15 a 20 segundos (carregamento do próprio jogo).
- Sem salvar em combate cooperativo ou retornar à batalha após desconexão.

## <a id="next-steps"></a>Próximos passos

- Testar abertura compartilhada em missões da história e Flashpoints.
- Responsabilidade por lanças por jogador sobre o controle compartilhado e Bigger Drops / Mission Control.
- Bloquear no convidado ações exclusivas do host (viagem, tempo, contratos), em vez de deixar que sejam perdidas.
- Verificar compatibilidade com BattleTech Advanced 3062.
