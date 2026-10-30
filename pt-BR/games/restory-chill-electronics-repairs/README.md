# <a id="restory-chill-electronics-repairs-2026"></a>ReStory: Chill Electronics Repairs (2026)

| | |
|---|---|
| Motor | Unity 6000.3.10f1, Mono (scripts em `Restory_Data/Managed/Restory.Assembly.dll`), Zenject, salvamentos FullSerializer, Steamworks.NET |
| Versões testadas | Steam 1.0.033r (atualização Fuzzby, 2026-10-27): SHA-256 de `Restory.Assembly.dll` `98bcbc08ec102865787fafee0ee8f53a0f82b81ce2b6b7d9d9e33335421ed66a`, SHA-256 de `Restory.exe` `ad7e0d4f72226c5741250658762a4b2f2688a9bea4288ba218ec80d7726630c6`, build-guid `eb5bb3732fca4140921c1f890d4ba957`. O trabalho anterior usava 1.0.015r. Windows 11. |
| Projetos | [ReStory Multiplayer](https://github.com/teecil/restory-multiplayer) (plugin BepInEx 5: cooperativo e versus), entrada "ReStory Multiplayer" no diretório |
| Nível de QA | automated (duas cópias reais controladas por bots; consulte QA), mais testes humanos em dois PCs |
| Última atualização | 2026-10-30 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores podem jogar juntos a carreira no salvamento do host: uma loja, uma carteira, um estoque de peças, e-mails e missões compartilhados, cada qual com sua bancada; o dia só termina quando ambos concordam. Dois jogadores jogaram pela internet em dois PCs (por Porthole) durante vários dias do jogo (compilação 1.0.015r), e essas sessões encontraram a maioria dos bugs difíceis; a suíte automatizada com duas cópias passa na compilação Steam atual 1.0.033r. Um modo versus (corrida para montar o mesmo aparelho) também funciona. O caminho por sala Steam existe; ainda não houve sessão com duas contas.

## <a id="existing-work"></a>Trabalhos existentes

Nenhum encontrado: buscas na web pelo título com "multiplayer", "co-op", "mod", "Nexus Mods" e "GitHub" retornaram apenas notícias e páginas de lojas, e este núcleo não tinha entrada, issue ou PR para o jogo (2026-10-30; Steam Workshop e Discord não consultados). O jogo é para um jogador ([Tom's Hardware Italia](https://www.tomshw.it/videogioco/restory-chill-electronics-repairs-i-consigli-per-iniziare)) e não tem código de rede.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Scripts:** toda a jogabilidade em um assembly Mono; descompila corretamente com ILSpy. Serviços são MonoBehaviours vinculados por Zenject ou classes simples; a maior parte do estado fica em serviços com `CaptureState`/`RestoreState` (sistema de salvamento), tornando "enviar o estado salvo do serviço" a principal ferramenta de sincronização.
- **Salvamentos:** `%USERPROFILE%\AppData\LocalLow\Mandragora\Restory\SaveData`, `Story.slot<n>.release-No-<i>.restory` (JSON FullSerializer, recursos do jogo gravados por identificador). A versão 1.0.015r substituiu perfis por vagas de salvamento; "Continue" carrega a maior iteração da última vaga usada. Steam Cloud sincroniza a pasta (a instalação Steam cria `steam_autocloud.vdf`).
- **Objetos:** objetos da sala em `InteractiveObjectRegistry` (objeto -> informações), aparelhos em `DeviceRegistry`, cada um com identificador único. Soltar objetos passa por `DragResolver.ResolveDragResult`, mas vários movimentos não: a bancada é preenchida por `DeviceService.PlaceDeviceContainer` (botão, desempacotamento); serviços criam objetos sozinhos (aparelhos de clientes, contas, dinheiro, caixas de entregador).
- **Caixas:** caixa do entregador (`DeliveryService`), dos clientes (`DevicesFromNpcsService`) e pessoal são mantidas pelos serviços em um local e guardam conteúdo; uma caixa levada para fora dobra (`FoldableObject`) e fica vazia.
- **Dinheiro:** o valor não está nos dados do objeto, mas em `CashMoneyService` (`MoneyAmountHeld`).
- **Missões:** itens de `ToDoListService`, adicionados por scripts de diálogo (`ToDoList_AddItem`), cada um concluído por um tratador que escuta eventos locais; concluir um pode agendar uma visita de história.
- **Tempo e fim do dia:** `TimeSystem` / `MainDayTimeSwitchingService`, bicicleta (`DayEnderFromPlayerInteraction`), tela de fim do dia (`GUI_DayEndWindow`, carimbo). Pausa = menu de pausa exibido (`GamePauseState`, escala de tempo 0).
- **Steam:** o jogo inicializa Steamworks.NET e processa callbacks a cada quadro, permitindo ao mod usar salas e `SteamNetworkingMessages` diretamente. Uma cópia iniciada fora da pasta Steam precisa de `steam_appid.txt`; caso contrário, reinicia pelo Steam na instalação real.
- **Análise de uso:** o jogo executa Unity Services Analytics (`RestoryAnalyticsService`), e o motor grava arquivos de sessão na pasta LocalLow do jogo; execuções de teste devem desativá-los.

## <a id="what-we-changed"></a>O que alteramos

O mod usa autoridade do host: ações do convidado vão ao host, que as aplica e envia o resultado. Destaques, cada qual com o bug que motivou a decisão:

- **Transporte:** UDP com confiabilidade própria, depois separado do enlace para também usar Steam. A primeira partida em dois PCs saturou o upload do host: cada datagrama sem confirmação era reenviado a cada 150 ms sem janela, e o estoque de peças era enviado inteiro (as chaves são JSON dos itens) a cada mudança. Correção: no máximo 32 datagramas sem confirmação em trânsito, reenvio após o tempo medido de ida e volta com espera progressiva, envio apenas das alterações do estoque. Mesmo teste sem interface, com ida e volta simulada de 200 ms: 1,47x -> 1,03x bytes por byte de dados. Um par Steam é um identificador de conta; por isso, cada execução põe um número de execução nos datagramas. Sem isso, um amigo que reiniciasse recebia datagramas atrasados do host destinados à execução anterior.
- **Lista da sala (censo):** a cada 2 s, o host envia todos os identificadores de objetos e aparelhos com assinatura curta; o convidado pede o que falta, esconde o que saiu da sala e remove o que o host não tem mais. Detecta tudo que o jogo cria sem soltar um objeto. Há também um observador duas vezes por segundo para movimentos sem soltura (aparelho do convidado ia para a bancada por desempacotamento, permanecia na mesa do host, e o host podia levá-lo durante o reparo).
- **Bancada:** "na bancada deste jogador" é `DeviceService.PlacedDeviceContainer`, não o estado da caixa (após desempacotar, a caixa mantinha "armazenada", e o aparelho era informado como sobre a mesa).
- **Caixas dos serviços, dinheiro, e-mails, missões, móveis:** cada qual sincronizado pelo estado salvo do serviço no host; retiradas de caixas são numeradas para que estado obsoleto do host não restaure o que o convidado pegou. Dinheiro leva seu valor; o depósito do convidado é feito pelo host. Ao aceitar um pedido por e-mail, o convidado solicita ao host, que só aceita se ainda estiver livre. Missão concluída de um lado é concluída do outro (um item pode terminar assim que é adicionado; portanto, "adicionado" precisa sair primeiro).
- **Jogado fora = removido:** objeto oculto continua no registro e no salvamento do host; caixas descartadas do entregador voltavam no dia seguinte até "desaparecido" significar removido.
- **Regras compartilhadas:** uma pausa para ambos (o outro lado abre seu menu de pausa); bicicleta e carimbo de fim do dia significam "pronto" e exigem ambos.
- **Versus:** os dois recebem o mesmo aparelho; início por contagem regressiva compartilhada (o host repete o tempo restante, evitando que mensagem inicial perdida e reenviada inicie o outro jogador atrasado).

## <a id="qa"></a>QA

- Sem interface: `dotnet run --project mod/RestoryMultiplayer.Tests -c Release` (rede, regras de sincronização, fuzzers, enlace Steam simulado, tráfego com ida e volta simulada de 200 ms). 242/242 em 2026-10-30 (mod 0.13.2).
- Duas cópias reais com bots (`scripts/run_coop_test.py`, `run_coop_ingame_test.py`, `run_race_test.py` no repositório do mod): cada uma é uma cópia da instalação Steam com pasta própria de salvamento; bots movem objetos, retiram peças da caixa do entregador, compram, depositam dinheiro, aceitam pedidos por e-mail, concluem missão, pausam, terminam o dia pela bicicleta e carimbo e reconectam após falha; scripts comparam salas, estoques, carteiras, caixas, e-mails e móveis das duas cópias e conferem que salvamentos reais permanecem intactos. Na 1.0.033r, 2026-10-30, mod 0.13.2: cooperativo 78/78, cooperativo iniciado de um salvamento 11/11, versus 70/70.
- `scripts/check_game_members.py <decompiled game>`: os 61 membros do jogo localizados por nome pelo mod; após a atualização 1.0.033r, só um desapareceu (sombra do neon de competição, removida pelos desenvolvedores).
- Testes humanos: dois jogadores em dois PCs pela internet, conectados por Porthole (rota IP), compilação 1.0.015r (antes da atualização 1.0.033r). Primeiro uma partida versus (2026-10-25); depois, a partir de 2026-10-27, vários dias cooperativos nos mods 0.10.0 a 0.12.x no salvamento do amigo, que hospedava: aceitar pedidos por e-mail, reparar, devolver aparelhos, comprar peças, receber dinheiro de clientes, terminar o dia. Logs dos dois (`BepInEx/LogOutput.log`) foram recolhidos após cada sessão. Problemas encontrados somente nas partidas em dois PCs, todos corrigidos e adicionados à suíte de bots:
  - o convidado não via nenhum aparelho (o registro só era capturado em uma chamada de registro que a loja do convidado nunca fazia; o salvamento de teste sempre tinha aparelhos, então os bots não encontravam isso);
  - o jogo do host consumia todo o upload, e a conversa por voz atrasava (reenvio sem janela e estoque inteiro a cada alteração; consulte Transporte);
  - o host podia levar o aparelho reparado pelo convidado (desempacotar para a bancada não é soltar);
  - dinheiro do cliente aparecia como 0 para o convidado e sumia ao depositar; duas caixas do entregador no mesmo local agiam como uma;
  - três caixas vazias após um dia, rótulo "ready 2/2" persistindo no dia seguinte, regra de um pedido por competição oculta para quem a atingia.
  Os jogadores também pediram o que os bots não podiam avaliar: pausa para ambos, fim do dia somente quando ambos estivessem prontos, regras do host (se o convidado pode aceitar pedidos) e avatares em página acessível durante o jogo. A compilação Steam 1.0.033r foi coberta somente pela suíte automatizada.

## <a id="how-to-play"></a>Como jogar

Consulte o [README do mod](https://github.com/teecil/restory-multiplayer): extraia a versão na pasta do jogo; menu principal e de pausa recebem uma placa "Online play". O host cria uma partida (por IP, UDP 27515, ou Steam), o amigo entra e o host pressiona Start.

## <a id="known-issues"></a>Problemas conhecidos

- Trabalho que o convidado deixa na própria bancada ao fim do dia não é preservado (o dia seguinte começa pelo salvamento do host, no qual o aparelho ainda está na sala).
- Mover a caixa de clientes ou a pessoal para fora do local não é compartilhado.
- Quando os e-mails do host mudam com o aplicativo aberto no convidado, a lista do convidado é reconstruída.
- Rota de sala Steam: ainda sem sessão de duas contas; IP funciona.
- Somente dois jogadores.

## <a id="next-steps"></a>Próximos passos

- Executar sessão por sala Steam com duas contas que possuam o jogo.
- Preservar o trabalho da bancada do convidado no fim do dia (por exemplo, devolver o aparelho à sala com seus dados antes do salvamento de fim do dia do host).
- Conferir os aparelhos da 1.0.033r (Fuzzby, controle PlayMachine) em modo cooperativo.
