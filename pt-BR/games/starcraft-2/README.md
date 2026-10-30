# <a id="starcraft-ii-2010-campaign-co-op"></a>StarCraft II (2010): campanha cooperativa

| | |
|---|---|
| Motor | Motor SC2 da Blizzard (scripts Galaxy, dados XML, mapas/mods MPQ); API s2client no cliente comercial |
| Versões testadas | Battle.net comercial 5.0.17.98310 (versão de dados 9C1F3D3D30CA252E33FC67CA05CBE1EA), enUS, Windows 10/11 |
| Projetos | [SC2Coop](https://github.com/Cryswar/sc2-coop) (código do inicializador, MIT, versões de teste) |
| Nível de QA | automated (teste básico local com dois clientes: 29 missões de uma campanha WoL@Kit e de três campanhas com scripts Blizzard, 4 missões de uma quarta) + sessões em dois PCs por testadores |
| Última atualização | 2026-10-23 |

## <a id="where-things-stand"></a>Situação atual

Alfa: versões públicas de teste em [Cryswar/sc2-coop](https://github.com/Cryswar/sc2-coop) (código e versões, MIT). Dois jogadores jogam juntos missões da campanha Wings of Liberty pelo Steam (AppID gratuito Spacewar da Valve como retransmissor) ou por conexão direta, em dois tipos de campanhas personalizadas: campanhas de fãs WoL@Kit e campanhas que mantêm os scripts da própria Blizzard (a maioria dos mods WoL). Ambos compartilham um exército (jogador 1) ou, nos mapas preparados para isso, possuem um cada. Cada jogador circula em sua própria cópia da base Hyperion, e escolher uma missão a inicia para ambos. Sessões de testadores em dois PCs passaram por várias missões, vitórias e objetivos bônus sem problemas que inviabilizassem o jogo. As entradas do convidado passam por uma ponte de cliques, parecendo um pouco menos diretas que as do host.

## <a id="existing-work"></a>Trabalhos existentes

- **Heart of the Swarm Co-Op** (LordDz e equipe, tópico Team Liquid, última publicação em 2019-12): recriação Arcade de missões HotS com escolha de herói por jogador. Somente Arcade (exige mapa do Battle.net), não testada aqui.
- Não foi encontrado modo cooperativo fora do Arcade para as campanhas comerciais (pesquisa de 2026-10-16: GitHub, SC2Mapster, Team Liquid, Reddit, Steam por busca na web). Co-op Missions da própria Blizzard é um modo PvE separado, não a campanha.
- O cliente SC2 de Archipelago controla o jogo comercial pela mesma API (um jogador) e foi uma referência útil.
- [s2client-proto](https://github.com/Blizzard/s2client-proto) da Blizzard e sua [documentação do protocolo](https://github.com/Blizzard/s2client-proto/blob/master/docs/protocol.md) descrevem a API usada aqui.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **API:** o cliente comercial aceita `-listen/-port` e usa s2client-proto por websocket. Pode criar jogos multiplayer de qualquer mapa local, com entrada por portas. Multiplayer só funciona quando todo cliente usa endereço de host de loopback; por isso, o inicializador cria túneis das quatro portas do jogo entre os PCs (um fluxo TCP ou retransmissão P2P do Steam; o UDP do jogo é enviado sem garantia de entrega).
- **Campanha = mapas + mods + bancos.** Missões e base (mapa de história) são arquivos `.SC2Map` dependentes de mods; uma biblioteca de campanha transita entre eles por `GameSetNextMap`/`GameOver`: `libCamp` da Blizzard na campanha comercial e mods derivados, ou a cópia renomeada de Kit (`LibWoLC`/`LibWCMI`) nas campanhas WoL@Kit. Todo progresso fica nos arquivos de banco do jogador 1.
- **Posições de jogadores:** mapas declaram jogadores em `MapInfo`. Adicionar uma posição de usuário (cópia do registro do jogador 1) basta para outro humano; aliança com controle, visão e gastos compartilhados torna ambos responsáveis pelo exército do jogador 1. Mapas com segunda posição própria usam um exército por jogador.
- **Particularidades da API que determinaram tudo** (todas observadas, consulte NOTES.md; lista completa, incluindo bibliotecas de campanha e armadilhas de entrada do Windows, em [PITFALLS.md](https://github.com/Cryswar/sc2-coop/blob/main/docs/PITFALLS.md)):
  - A entrada nativa do criador no mundo precisa de `raw=true` em InterfaceOptions; cliques no mundo de quem entra são descartados, então passam pela API como ações da camada de recursos (ponte de cliques).
  - Qualquer objetivo definido como concluído ou fracassado faz a API encerrar o jogo nos dois clientes (estado 5).
  - `RequestObservation` falha para identificadores de convidados acima de 3 em algumas configurações (suposição 1v1 `3 - player` da API).
  - `RequestGameInfo` falha em mapas de história. `GameOver` de um mapa de história carrega o seguinte, salvo se for limpo.
  - O jogo em execução não relê um banco alterado em disco (`BankLoad` retorna a versão em cache).
  - Um processo que já jogou uma partida não entra em outra multiplayer (entrada trava).
  - Um cliente de entrada encerrado mantém sua cópia do mapa compartilhado; reutilizar o mesmo nome depois carrega a cópia obsoleta e a entrada falha com ChecksumError, exigindo nomes que mudem com o conteúdo.
  - SC2 às vezes encerra com -2000/-2001 logo após iniciar; tentar novamente funciona.
  - `text` é nome de tipo Galaxy: uma variável local chamada `text` desativa silenciosamente todo o script do mapa; também fazem isso uma função que lê uma global da missão declarada depois ou um comentário `/* */` (Galaxy não os possui).
  - Missões iniciadas pela API não são mapas de transição (`GameIsTransitionMap()` é falso). Ambas as bibliotecas tratam isso como início pelo editor: uma compra de tecnologia de depuração recalcula créditos/progresso, snapshots antigos de reinício da missão são carregados, e repetições de Mission Archives gravam progresso antigo de volta. Cada caso exigiu reescrita ou reparo após a missão (2026-10-22/23).
  - Jogos por API rodam em Faster; código de gatilhos pode definir qualquer velocidade durante o jogo após reduzir o mínimo e desbloquear a velocidade. Opções de exibição por linha de comando (`-displayMode`, tamanho da janela) substituem as configurações do jogador.

## <a id="what-we-changed"></a>O que alteramos

O inicializador SC2Coop (C#, .NET Framework; nenhum arquivo de jogo distribuído, tudo criado a partir da instalação do jogador). Integração: [ARCHITECTURE.md](https://github.com/Cryswar/sc2-coop/blob/main/docs/ARCHITECTURE.md).

- **Adaptador de missão** (aplicado a cada mapa na preparação): posição de convidado em `MapInfo`; convidado recebe as alianças do jogador 1 com todos os demais (reaplicadas a cada segundo); chamadas de estado dos objetivos redirecionadas para exibir conclusão/falha como sufixo do nome em vez de encerrar o jogo API; 13 funções de câmera dirigidas ao jogador 1 espelhadas no convidado (cenas); sinais do jogador 1 visíveis ao convidado; cenas puláveis avançam com Esc de um jogador; próximo mapa limpo; dificuldade, cores e velocidade definidas (`-coopspeed` altera a velocidade); caminhos de mapa não transitório das bibliotecas removidos ou reparados; derrota exibe diálogo cooperativo (repetir a missão ou voltar à base); comandos de teste no chat (`-coopwin`, `-coopwinnow`, `-cooplose`, `-coopobj`).
- **Exércitos separados** (mapas com segunda posição de usuário): contagens de unidades e verificações de controle do jogador 1 contam ambos; dinheiro e tecnologia dados ao jogador 1 são espelhados; resgates, reforços e recursos coletados vão para quem encontrou, alternam ou vão para ambos, conforme o host escolher.
- **Adaptador da base:** lançamentos de missão registrados em banco para o inicializador (funções de Kit e Blizzard, repetições de Mission Archives em ambas); uma escolha em uma base lança a mesma missão na outra, mostrando o briefing a ambos; chat retransmitido entre bases; lojas do parceiro apenas para consulta (um exército, progresso do host); base do host salva automaticamente para pagar recompensas uma vez; seleção assume a dificuldade da campanha; `-cooplaunch <mission>`.
- **Fluxo da campanha:** ambas as bases como jogos API individuais; uma escolha em qualquer uma fecha ambas e inicia a missão multiplayer; depois os bancos sincronizam host -> convidado e as bases reabrem. Um salvamento cooperativo por campanha (campanhas compartilham nomes de bancos), com redefinição. Verificação da configuração ao conectar (inicializador, mapas, todos os mods por SHA-256), salvamento automático de bancos antes de missões e reparo após falhas, tratamento de falhas/perda de conexão, cortina de carregamento entre jogos, nomes de jogadores e cores lidas dos dados da campanha.
- **Ponte de cliques** do convidado: seleção, seleção por caixa, ordens, habilidades com alvo (eventos de modo de alvo e ordem de sondagem trocada pela habilidade real), posicionamento de construções, rolagem por setas, sinais com painel próprio. Entradas lidas com Raw Input (sem hooks globais) enquanto a janela do convidado está à frente; sobreposições são ignoradas em tela cheia exclusiva.
- **Transporte:** TCP 6600 com UPnP ou Steam P2P pelo AppID Spacewar (convites de amigos, sala), com sinal periódico de atividade.
- **Verificador de mapas** (`campaign-check`): lista por mapa o que o inicializador trata e o que precisa do autor do mapa. A lista de adaptação está em [PORTING.md](PORTING.md).

## <a id="qa"></a>QA

- **Teste básico** (um PC, dois clientes reais, cópia da instalação, hooks `SC2_COOP_TEST_LAUNCH`/`SC2_COOP_TEST_WIN`): cada missão lançada da base por chat, vencida com `-coopwinnow`, retorno às duas bases. Passaram: 29 missões de uma campanha WoL@Kit (2026-10-20) e 29 de cada uma de três campanhas que mantêm scripts Blizzard (2026-10-22; duas missões de uma campanha passaram na segunda tentativa após o primeiro carregamento ultrapassar o limite de entrada de 3 minutos; uma execução foi retomada após Windows Defender colocar o executável de teste em quarentena). Em uma quarta campanha dessas, 4 missões (2026-10-21). Missões de escolha A/B foram lançadas diretamente, pulando o diálogo. Verificações: ambos entram, estado API permanece em jogo até a vitória, missão termina normalmente, bancos sincronizam e bases reabrem.
- **Testes dirigidos** (um PC, hooks de teste): concluir objetivos mantém os dois em jogo; falha de qualquer cliente retorna ambos à base com bancos intactos (banco truncado restaurado); Stop e perda de conexão encerram toda espera; divergência de configuração informada nos dois lados; câmera de cena idêntica; Esc somente do convidado pula; exércitos separados: derrota só quando ambos são eliminados, resgates vão ao jogador mais próximo, coletas pagam ambos.
- **Estado da campanha** (um PC, bancos lidos após cada etapa, 2026-10-23): créditos após vitória equivalem exatamente a uma recompensa; missões concluídas e créditos sobrevivem a repetições de Mission Archives (duas repetições e uma missão inicial verificadas); velocidade medida pelo relógio do jogo (Faster 1,41, Normal 1,00, Slower 0,61 segundos de jogo por segundo real), também em Brutal.
- **Sessões em dois PCs** por testadores no Steam (2026-10-19 a 2026-10-23): missões 1 a 3 até Hyperion, várias posteriores, vitórias, objetivos bônus, derrotas com repetição, repetições de Mission Archives e um mapa de teste com exércitos separados.
- Não cobertos: campanha cooperativa completa, sessões longas. A qualidade das entradas do convidado é avaliada pelos jogadores.

## <a id="how-to-play"></a>Como jogar

Baixe `SC2Coop.zip` nas [versões do projeto](https://github.com/Cryswar/sc2-coop/releases). Ambos extraem e iniciam `SC2Coop.exe` (encontra e prepara a instalação própria de SC2), marcam Campaign e escolhem a pasta da campanha; um hospeda (Steam ou endereço) e o outro entra. O guia do jogador é `README.txt` no ZIP.

## <a id="known-issues"></a>Problemas conhecidos

- Antivírus: o aprendizado de máquina na nuvem do Windows Defender colocou compilações em quarentena (Trojan:Win32/Prowloc.A!cl). Substituir hooks de entrada globais por Raw Input reduziu a frequência, mas novas compilações de teste de console sem assinatura ainda são sinalizadas ocasionalmente. Assinatura de código é a solução efetiva.
- Comandos do convidado reagem cerca de uma ida e volta de rede depois dos do host. O tráfego do jogo usa principalmente canal confiável, então perda de pacotes no retransmissor aparece como engasgos.
- Em campanhas com scripts Blizzard, a tecnologia de campanha do convidado em exércitos separados ainda não está integrada. Simulator e Arcade da base não são suportados.
- Missões iniciais com scripts Blizzard (TRaynor01-03) ainda executam a configuração de tecnologia de depuração da biblioteca ao carregar; o inicializador repara os efeitos depois, mas não consegue removê-la.
- Um cliente SC2 em tela cheia exclusiva pode falhar quando o inicializador desenha sobre ele ("Lost D3D9 device"); o inicializador detecta e para de desenhar, e os jogadores devem usar Windowed (Fullscreen).
- Alguns gatilhos de missão reagem apenas às entradas do host (avisos de tutorial, diálogos de escolha de missão).

## <a id="next-steps"></a>Próximos passos

- Cooperativo de duas facções com progresso próprio de cada jogador (bancos de ambos em uma missão).
- Campanhas Heart of the Swarm (vários mapas de base, outra biblioteca, progresso de Kerrigan): viabilidade em avaliação.
- Depois: Legacy of the Void (Spear of Adun vinculado ao jogador 1), campanhas personalizadas com bases próprias e opção de trocar raça.
- [NOTES.md](NOTES.md) é o caderno de laboratório datado.
