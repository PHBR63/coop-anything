# <a id="starcraft-ii-campaign-co-op-lab-notes"></a>Campanha cooperativa de StarCraft II: notas de laboratório

Caderno datado. Cada entrada separa observações de uma execução, deduções e desconhecidos. "Host" cria a partida (jogador 1); "convidado" entra. Testes em um PC executam dois clientes reais numa máquina, de instalação copiada com perfis temporários separados; sessões em dois PCs foram jogadas por testadores pela internet. Compilação 5.0.17.98310, enUS, Windows.

## <a id="2026-10-16-assessment-and-first-api-spikes"></a>2026-10-16: avaliação e primeiros experimentos com API

Fontes: [s2client-proto](https://github.com/Blizzard/s2client-proto) (`sc2api.proto`, `docs/protocol.md`), cliente SC2 do Archipelago (solo, inicia missões pela mesma API), tópico LordDz Heart of the Swarm Co-Op Arcade, SC2CCM (gerenciador de arquivos de campanha, sem multiplayer).

Observado:
- API do cliente comercial cria partidas de qualquer mapa local. Pasta de mapa solta recusada ("map doesn't exist"); `.SC2Map` empacotado funciona.
- Dois clientes API em mapa padrão de classificação entram como jogadores 1 e 2. Com aliança compartilhando controle e gastos, segundo move marine do primeiro e treina em seu quartel com seus minerais; produção termina como unidade do jogador 1. Removendo controle/gastos (mantendo visão), comandos falham com resultado 87: posse é imposta, só funcionam pela aliança.
- Missão original (The Outlaws) com vaga user 6 adicionada roda 450 segundos de jogo com objetivos, IA e ondas intactos nos dois.
- Cliente convidado falha no primeiro `RequestObservation` com identificador acima de 3. Código lê tabela no índice `3 - player` (pressuposto de 1 contra 1). Convidados nunca pedem observações; host faz a leitura.

## <a id="2026-10-16-native-input-and-the-click-bridge"></a>2026-10-16: entrada nativa e ponte de cliques

Observado (mapa padrão e missão, cliques reais `SendInput`):
- Cliques nativos do criador no mundo só selecionam com `InterfaceOptions.raw = true`.
- Cliques e arrastes do convidado não produzem ação, quaisquer opções. Destaques, minimapa e menus funcionam. Inverter ordem de início não muda: criador funciona, participante não.
- Ações API de camada visual do próprio convidado (`unit_selection_point`, `unit_command`) funcionam e aparecem na interface.

Implementada ponte de cliques do convidado. Hooks de mouse/teclado de baixo nível na janela traduzem cliques para ações API de camada visual (seleção, seleção em caixa, comando inteligente), calibrando janela para camada visual. Comandos com alvo (atacar em movimento, habilidades, construção, coleta) usam pequeno script: mapa relata habilidade pendente num banco, ponte envia ordem de sondagem e script a troca pela real um ciclo depois (unidade mais próxima a até 1,25 quando alvo pontual inválido, como coleta).

## <a id="2026-10-1617-networking"></a>2026-10-16/17: rede

Observado:
- Multiplayer API só funciona com clientes conectando a loopback (outro endereço falha JoinGame com erro 12; pysc2 documenta igual). Inicializador retransmite quatro portas entre PCs: conexão TCP (6600, UPnP quando possível) ou P2P Steam sob Spacewar da Valve (480). Só host precisa ser alcançável.
- Testes num PC com bases de porta diferentes não exercitam UDP do retransmissor (jogos conversam diretamente por loopback); só sessões em dois PCs.
- Steam: sala, amigos, convites e retransmissão funcionam entre duas contas reais. Antes tudo passava pelo canal confiável; datagramas UDP agora passam sem confiabilidade quando ambos aceitam. Tráfego pequeno (algumas centenas de KB por 10 minutos), mas maioria é TCP pelo canal confiável; perda causa travadas (sessão: 100% de entrega por 4 minutos, depois 91 a 97% num lado, picos RTT de 8 s).
- Atraso de movimento do convidado é principalmente o próprio atraso de comandos SC2 (0,1 a 0,15 s num PC) mais uma ida e volta de rede.

## <a id="2026-10-17-to-10-19-first-two-pc-sessions-guest-ui"></a>2026-10-17 a 10-19: primeiras sessões em dois PCs, interface do convidado

Sessões Steam entre PCs (The Outlaws, depois missões) funcionaram: ambos jogam, movimentos, ataques e construções do convidado passam. Correções dos relatos: caixa de arraste do convidado (sobreposição do inicializador), barra de recursos (minerais/gás/suprimento compartilhados do primeiro), marcações para ambos, teclas de câmera, deriva do clique com zoom (calibração segue distância e inclinação da câmera), depurador aberto por alguns mapas (minimizado uma vez), erro de mod ausente ao entrar (agora confere dependências de todos os mapas e nomeia ausências).

## <a id="2026-10-18-campaign-hub-story-map"></a>2026-10-18: centro da campanha (mapa da história)

Observado:
- Centro Blizzard (TStory01 reempacotado) e WoL@Kit executam como jogos API solo: introdução, seleção e lançamento. `RequestGameInfo` no original derrubou cliente.
- Lançar missão encerra centro para API (vitória jogador 1, estado 5). Cliente não carrega próximo mapa; 7 a 20 s depois falha seguindo `GameSetNextMap`. Inicializador encerra centro imediatamente.
- Nenhuma biblioteca grava missão escolhida no banco; chamada é encapsulada para registrar.
- Bancos do jogador 1 enviados ao outro no início: em missão com dois, perfil vazio do convidado leu valor do banco do host.

Implementado fluxo: cada um roda seu centro solo; escolha em qualquer centro fecha ambos e inicializadores iniciam missão multiplayer; depois bancos do host vão ao convidado e ambos os centros reabrem.

## <a id="2026-10-19-making-the-campaign-loop-robust"></a>2026-10-19: tornando robusto o ciclo da campanha

- **Objetivos:** qualquer objetivo concluído/falho encerra jogo pela API para ambos (ponte de cliques então recusada). Chamadas de estado nos scripts e biblioteca Kit redirecionadas para manter estado ativo e nome com " (Completed)" / " (Failed)"; leituras retornam estado real.
- **Conferência na conexão:** SHA-256 do inicializador, mapas e todos os mods nos dois PCs; diferenças listadas por arquivo antes de iniciar.
- **Recuperação:** bancos salvos antes de cada missão; se cliente falha ou fecha, ambos voltam ao centro no estado anterior e banco danificado é restaurado.
- **Nova tentativa de início:** SC2 às vezes sai com -2000/-2001 logo após iniciar; segunda tentativa funciona.
- **Transições:** centro fecha 1,5 s após escolha. Reusar processo não funciona: após uma partida ele trava na próxima entrada multiplayer. Cortina de carregamento cobre intervalo entre janelas.
- **Nomes e cores:** escolhidos no inicializador, trocados na conexão.

## <a id="2026-10-20-cutscenes-pings-all-missions"></a>2026-10-20: cenas, marcações, todas as missões

- Cenas: 13 funções de câmera para jogador 1 também para convidado; ambos veem mesmos enquadramentos e rostos; pular exige Esc de um, não de todos.
- Marcações nativas do convidado (Alt+clique), painel e câmera de cada um no minimapa do outro.
- Teste básico de todas as 29 missões WoL@Kit (centro, lançamento por conversa, `-coopwinnow` após 45 s, retorno de ambos): 28/29 passaram; última falhou JoinGame erro 6 até convidado usar raça do primeiro (missões Protoss), depois passou duas vezes.
- `campaign-check`: verificador estático que lista, por mapa, tratamento do inicializador e trabalho do autor (consulte [PORTING.md](PORTING.md)).
- Detecção em nuvem do Windows Defender colocou executável de teste sem assinatura em quarentena várias vezes (Trojan:Win32/Prowloc.A!cl), sempre ao iniciar hooks de entrada. Era a causa das execuções "mortas" antes inexplicadas. Nenhuma exclusão adicionada.

## <a id="2026-10-21-hub-features-and-team-colors"></a>2026-10-21: recursos do centro e cores

- Cores são dados (CGame TeamColors); mods renomeiam, recolorem e acrescentam. Inicializador reconstrói tabela pelos mods da campanha; RGB personalizados acrescentados à tabela de cada missão.
- Conversa no centro: cada centro é jogo separado; jogo não relê banco alterado no disco. Linhas saem por banco e entram como conversa API; centro oculta conversa SC2 e desenha linhas próprias.
- Repetições Mission Archives (WoL@Kit) registradas como escolhas no mapa estelar.
- Variável local Galaxy chamada `text` (nome de tipo) desativa silenciosamente todo script do mapa.

## <a id="2026-10-21-separate-armies"></a>2026-10-21: exércitos separados

Experimento em The Outlaws (WoL@Kit), depois implementação em mapa de testador com segunda vaga user:
- Reescritas: grupos e posse do primeiro contam ambos; definidores de dinheiro/tecnologia espelhados; unidades dadas ao primeiro durante missão (`UnitSetOwner`, `libNtve_gf_RescueUnit`, criação) vão a quem tem unidades mais próximas, alternadamente ou a ambos.
- Recursos coletáveis: alguns por script (biblioteca paga coletor), outros só dados (habilidade automática de paletes Liberty aplica efeito de recursos ao coletor). Os de dados são interceptados no evento de execução da habilidade; outro recebe igual ou metade.
- Observado num PC: convidado entra na vaga e raça do mapa; ambos contam nos objetivos; derrota só com ambos sem exército; resgatados vão ao mais próximo; recursos pagam ambos.
- Armadilha: auxiliares antes do script não leem globais da missão (Galaxy exige declaração prévia). Referenciá-las fazia script inteiro falhar silenciosamente (sem apresentação, 0 minerais). Encapsuladores agora após script, protótipos antes.
- Alianças: convidado copia as do primeiro com todos, exceto controle/gastos. Copiar só hostilidade deixava visão de aliados IA apenas ao primeiro (convidado não via unidades da IA aliada).

## <a id="2026-10-2122-campaigns-on-blizzards-own-scripts"></a>2026-10-21/22: campanhas com scripts Blizzard

Levantamento: quatro mods WoL baseados no original mantêm centro Blizzard, cada um com cinco chamadas iguais `libCamp_gf_LaunchMission`. Kit é cópia renomeada de `libCamp`; maioria dos hooks corresponde diretamente (PORTING.md). Bancos simples do jogador 1 em BankList.xml de cada mapa.

Implementado: `libCamp_gf_LaunchMission` do centro redirecionada à cópia da função (escolha A/B, apresentação, `PrepareForMission`, fim) que registra missão final; testes usam nomes libCamp.

Observado num PC: centro e quatro missões (uma Protoss), cada uma vencida e retorno aos dois centros; regressão WoL@Kit passou.

Armadilha: cliente convidado encerrado forçadamente conserva sua cópia do mapa compartilhado. Sessão seguinte salvando mapa diferente com mesmo nome o guardava como "~00", mas carregava cópia antiga; toda entrada falhava ChecksumError (11) após 3 minutos. Nomes agora incluem hash do conteúdo.

## <a id="2026-10-22-smoke-tests-of-three-more-campaigns-on-blizzards-scripts"></a>2026-10-22: testes básicos de outras três campanhas com scripts Blizzard

Observado num PC, todas as missões iniciadas do centro por `-cooplaunch`, vencidas por `-coopwinnow`, retorno a ambos; missões A/B iniciadas diretamente, pulando escolha:
- Campanha 1: 29/29.
- Campanha 2: 27/29 na primeira. Duas Char (TValerian02A/B), consecutivas, não terminaram carregamento do host em 3 minutos. Ambas passaram na segunda tentativa (uma entrou em cerca de 20 s).
- Campanha 3: 2/29 antes da quarentena Defender na entrada da terceira; outras 27 passaram com executável recompilado, total 29/29.

Deduzido: todas executam cada missão cooperativamente sem alterar campanhas. Desconhecido: por que primeiro carregamento das duas Char excedeu 3 minutos; não se repetiu.

## <a id="2026-10-2223-campaign-state-on-blizzards-scripts-testers-round"></a>2026-10-22/23: estado de campanha nos scripts Blizzard, rodada dos testadores

Sessões em dois PCs relataram créditos variando entre missões (derrota pagando recompensa, vitória deixando menos que antes), melhorias desfeitas após escolha do parceiro e centro quebrado após repetição Mission Archives.

Observado em bancos lidos a cada etapa num PC e no código da biblioteca:
- Toda missão chama `libCamp_gf_PurchaseStorymodeTech()`. Fora de mapa de transição (`GameIsTransitionMap()` false, todas as iniciadas por API), executa compra média de depuração: créditos = recompensas esperadas do caminho esperado menos compras; progresso reinicializado nesse caminho; banco salvo com missão como última bem-sucedida. No centro (transição), retorna imediatamente. TRaynor01-03 repetem compra em `libCamp_gf_LoadCampaignData`.
- Cada missão mantém captura de estado do primeiro início (banco próprio na Blizzard; indicador `MissionSectionExist` e seções no banco WoL@Kit). Fora de transição, carrega sempre que existe, desfazendo compras desde tentativa anterior.
- Centro paga recompensa da última missão a cada abertura até salvamento marcar paga. Fechar sem lançamento (Stop ou escolha do outro) fazia pagar de novo na próxima.
- No fim de repetição fora de transição, salvamento grava captura da missão repetida no banco da campanha: disponíveis/concluídas, melhores tempos, mercenários, tecnologia. Repetir missão inicial deixava só ela no mapa estelar e quebrava salas do centro.
- Cada centro é jogo com bancos próprios; o que lançava escrevia o estado válido, então compras do host sumiam quando parceiro escolhia.

Alterado: chamada de depuração removida; derrota salva como derrota; captura descartada ao iniciar do centro (mantida em nova tentativa e repetição); após repetição, progresso e créditos restaurados da cópia anterior; centro do host salva pouco após abrir e antes de fechar; lojas do parceiro só para consulta (gatilhos de compra desligados); um salvamento cooperativo por campanha, com reinicialização.
Observado depois: créditos após vitória correspondem exatamente a uma recompensa; missões concluídas e créditos sobrevivem a repetições.

Outras descobertas:
- Entrada do convidado migrou de hooks globais para Raw Input após quarentenas repetidas. Raw Input não consome teclas; setas registradas como atalhos enquanto janela convidada está à frente. Enxurrada de `WM_INPUT` impedia `WM_PAINT`, deixando sobreposição de arraste preta até redesenhar com `UpdateWindow`.
- Após clique no minimapa ou atalho de câmera, ponte desconhecia posição e devolvia setas à rolagem do mapa, tornando posição obsoleta novamente: cerca de 20 trocas em 2,5 minutos. Pressionar agora espera próximo relato da câmera.
- Cliente do parceiro falhou segundos após missão; log gráfico mostrava reinicializações "Lost D3D9 device" ao ocultar tela de carregamento. Windows informa jogos D3D de tela inteira exclusiva (`SHQueryUserNotificationState` = `QUNS_RUNNING_D3D_FULL_SCREEN`); inicializador para de desenhar sobreposições nesse caso.
- Inicializador passava `-displayMode 0` e tamanho de janela para todos, sobrescrevendo preferências de exibição. Removido das instalações reais.
- Velocidade: jogos API usam Faster. Medido no relógio a cada 5 s reais: Faster 1,41, Normal 1,00, Slower 0,61 segundos de jogo por segundo real. `GameSetSpeedValue` funciona durante partida; com `GameSetSpeedValueMinimum` e `GameSetSpeedLocked(false)` também desce abaixo do mínimo imposto em Hard/Brutal.
- Uma missão reinicializava quadros da interface após introdução, ocultando painel de marcações; agora reaparece a cada segundo fora de cenas.
- Código público: https://github.com/Cryswar/sc2-coop (MIT), com versões de teste. Arquitetura e lista completa de armadilhas em `docs/`.

## <a id="open-questions"></a>Questões em aberto

- Mais de dois humanos: protocolo aceita lista de portas cliente; 3 a 4 podem funcionar, não testados.
- Campanhas Heart of the Swarm: vários centros, chamada de lançamento na interface da biblioteca, progresso Kerrigan em bancos; análise de viabilidade em andamento.
- Duas facções com progresso próprio: bancos de ambos numa missão e qual fluxo conta.
- Sessões longas e campanha cooperativa completa.
