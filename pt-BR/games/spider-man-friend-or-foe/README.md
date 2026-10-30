# <a id="spider-man-friend-or-foe-2007"></a>Spider-Man: Friend or Foe (2007)

| | |
|---|---|
| Motor | desconhecido para a compilação Windows examinada |
| Compilação examinada | Windows 1.0.0.111, pacotes coerentes em inglês/russo |
| Projeto on-line | [Pesquisa Friend or Foe Online](https://github.com/IlkinQafarov/spider-man-friend-or-foe-online), somente código-fonte |
| QA do projeto completo | none |
| Última atualização | 2026-10-21 |

## <a id="existing-co-op-and-project-relationship"></a>Modo cooperativo existente e relação entre os projetos

O [anúncio de lançamento da Activision](https://investor.activision.com/static-files/d8459280-fceb-49b0-9210-86bb7010c3d3) descreve modo cooperativo com entrada de um parceiro durante a partida. Um [teste contemporâneo para PC](https://www.swiftworld.net/2007/10/13/pc-spider-man-friend-or-foe-review/) descreve dois jogadores em um computador; a [análise da GameSpot](https://www.gamespot.com/reviews/spider-man-friend-or-foe-review/1900-6180451/) informa que não há jogo on-line. Essa é a entrada oficial de modo cooperativo local, independente da pesquisa abaixo.

O projeto público de código-fonte nativo para Windows é um protótipo ativo, sem versão jogável distribuída. A [listagem de projeto existente no Discord](https://discord.com/channels/1561411702082510879/1562185850777772152) permanece separada: sua relação com esse projeto de código-fonte e seu executável não foi estabelecida. A atribuição de motor de uma listagem não constitui evidência para a outra compilação; o diretório agora informa desconhecido de forma consistente. Consulte [NOTES.md](NOTES.md).

## <a id="approach-and-bounded-evidence"></a>Abordagem e limites das evidências

O código implementa hooks para a compilação exata, entradas separadas para jogador local/remoto, temporização fixa de jogo, comparações de estados selecionados, verificação prévia de conteúdo e um inicializador/retransmissor. As [APIs de rede da Valve](https://partner.steamgames.com/doc/features/multiplayer/networking) são o transporte on-line pretendido; sua disponibilidade não comprova a transmissão remota deste protótipo.

O cenário 11 / protocolo de comunicação 3 passou nestas verificações inglês/russo na mesma máquina:

- 7.200 ticks consecutivos de estados selecionados, com três transições de área em Tokyo conduzidas por dados de teste, dados de teclado/controle, variação de latência e transporte simulado. Todos os jogos, inicializadores e retransmissores encerraram com código 0; cada retransmissor enviou/recebeu 921.808 bytes e descartou 0.
- 3.600 ticks de combate/pausa, incluindo 178 quadros congelados e retomada nativa. Todos os processos iniciados pelo teste encerraram com código 0; cada retransmissor enviou/recebeu 461.008 bytes e descartou 0.
- Um ciclo de jogo separado, sem atividade e com dados de teste desativados, chegou a 361 ticks comuns; depois, fechar somente a janela do host entregou uma parada ordenada ao par, com encerramentos normais. Seu percurso controlado antes do jogo levou cerca de 212 segundos para ficar pronto; a verificação terminou em cerca de 221 segundos. Entradas físicas não foram exercitadas.

A execução 033 anterior, do cenário 10, falhou durante a inicialização nativa. O cenário 11 limita a busca insegura de nomes de teclado e usa um layout americano já carregado e validado para nomes internos, preservando rótulos exibidos e configurações do Windows. As novas execuções passaram com layouts americanos; não estabelecem a causa original nem compatibilidade mais ampla com layouts. Falhas e escopo completo dos testes permanecem no [registro de estado](https://github.com/IlkinQafarov/spider-man-friend-or-foe-online/blob/main/docs/STATUS.md) do projeto.

Uma verificação básica separada e autorizada do Steam criou e abandonou uma sala restrita a amigos, sem tráfego de jogo. Ela não certifica transmissão entre dois PCs. O QA do projeto completo permanece **none**.

## <a id="how-to-play-and-remaining-work"></a>Como jogar e trabalho restante

Não há pacote de versão on-line disponível. As [instruções de compilação](https://github.com/IlkinQafarov/spider-man-friend-or-foe-online/blob/main/docs/BUILDING.md) descrevem um ambiente de pesquisa com uma cópia compatível do jogo; recursos do jogo e bibliotecas Steam não são distribuídos.

Menus e deslocamentos da campanha comercial, salvamento/retomada compartilhados, cobertura de missões/chefes/NIS, usabilidade das entradas físicas e partidas Steam com duas contas permanecem incompletos ou não verificados. O deslocamento entre áreas dirigido por dados de teste não comprova a progressão normal da campanha, e hashes amostrados não cobrem o mundo inteiro. O [roteiro](https://github.com/IlkinQafarov/spider-man-friend-or-foe-online/blob/main/docs/ROADMAP.md) registra o trabalho restante.
