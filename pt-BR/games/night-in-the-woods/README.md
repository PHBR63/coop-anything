# <a id="night-in-the-woods-2017"></a>Night in the Woods (2017)

| | |
|---|---|
| Motor | Unity 5.6.2p4 (Mono) |
| Versões testadas | Compilação Steam para PC 5940043 (AppID 481510) |
| Projeto | [Código-fonte do protótipo Night in the Woods Co-op](https://github.com/SamuelAustin2001/night-in-the-woods-coop) (experimental, não é uma versão jogável verificada) |
| Nível de QA | none (verificações básicas por bots; sem suíte reproduzível) |
| Última atualização | 2026-10-21 |

## <a id="where-things-stand"></a>Situação atual

Um protótipo local de host/cliente sincroniza entradas, cena e posição de Mae, além do dicionário numérico de variáveis de história do Yarn. Ele não foi lançado nem comprovado como modo cooperativo jogável: escolhas, efeitos de scripts, estado persistente dos salvamentos e uma execução completa da história não foram verificados.

## <a id="existing-work"></a>Trabalhos existentes

Foram pesquisados o GitHub e este repositório em busca de trabalhos cooperativos anteriores de Night in the Woods. ModDB, Discord e fontes de arquivo não foram pesquisados; portanto, trabalhos existentes nesses locais são desconhecidos. O código-fonte experimental do plugin está publicado no [repositório específico do jogo](https://github.com/SamuelAustin2001/night-in-the-woods-coop); não há uma versão empacotada para jogadores.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

A compilação Steam testada é um jogo Unity 5.6.2p4 para Windows x64 que usa Mono. `Player` lê as ações do Rewired, `DialogueRunner` do Yarn gerencia os diálogos e `Continuity` armazena variáveis numéricas da história e dados persistentes/de salvamento. O assembly não referencia os recursos de rede do Unity. Os salvamentos são serializados como arquivos `.dat` no diretório de dados persistentes do Unity.

O protótipo usa uma história compartilhada com autoridade do host: os dois participantes contribuem com entradas de movimento, salto, interação e confirmação de diálogos para a mesma Mae. O host envia snapshots de cena e posição e o dicionário numérico `Continuity.vars`. Salvamentos do convidado são suprimidos. As variáveis numéricas são enviadas em fragmentos UDP de tamanho limitado e aplicadas apenas após a chegada de um snapshot completo.

## <a id="what-we-changed"></a>O que alteramos

- Mapeamos as entradas do jogador, diálogos Yarn, variáveis de história de `Continuity` e caminhos de salvamento em uma cópia isolada da compilação Steam 5940043.
- Criamos um protótipo host/cliente com BepInEx para entradas compartilhadas, acompanhamento da cena/posição do host e replicação das variáveis numéricas da história.
- Acrescentamos um comando de mutação de variáveis exclusivo dos bots. Uma mutação de `AngusConstellations` no cliente foi corrigida pelo snapshot do host; os dois clientes passaram então a informar 316 variáveis com hash `0F68BB8C`.

## <a id="qa"></a>QA

Foram verificações pontuais por bots em duas instâncias da compilação Steam conectadas por loopback, não uma suíte automatizada mantida.

- Uma confirmação do cliente moveu os dois clientes de `Title` para `IntroPoem`.
- Em `MaeRoom`, selecionada pelo QA, pulsos de movimento do host e do cliente moveram Mae; as posições ficaram a até 0,02 unidades de mundo após cada pulso.
- Uma mudança de cena de QA exclusiva do host moveu o cliente para `BusStation`; as posições diferiram em cerca de 0,001 unidade após o carregamento.
- O bot cliente alterou `AngusConstellations`; após o host enviar seis fragmentos de variáveis, os dois arquivos de estado informaram 316 variáveis e hash `0F68BB8C`. O cliente registrou `host snapshot applied`.
- Falhas: uma confirmação do host na tela de título foi observada pelo cliente, mas não avançou o host. Em `MaeHouse`, um pulso de movimento para a esquerda no host não moveu Mae, e a interação de host/cliente não abriu um menu de opções do Yarn; a causa é desconhecida. Em uma verificação anterior de mutação em `MaeRoom`, o cliente informou `host snapshot applied`, mas o hash do dicionário inteiro continuou diferente por pelo menos seis segundos. Os hashes coincidiram depois de uma transição forçada para `Title`, porém o convidado ainda estava em `TransitionScene` enquanto o host informava `Title`. Uma repetição posterior com v0.6.1 corrigiu a mutação e produziu hashes iguais.
- Uma tentativa posterior, partindo de uma nova inicialização, não conseguiu conectar: o convidado informou `UDP receive error: An invalid argument was supplied.` Nenhum resultado é reivindicado para essa tentativa.

A configuração direta da cena contorna o fluxo normal da história. O teste de variáveis verificou apenas a correção do dicionário, não a progressão das escolhas de diálogo.

## <a id="how-to-play"></a>Como jogar

O repositório de código-fonte contém instruções experimentais de compilação e instalação, mas não há uma versão empacotada para jogadores. O protótipo não foi comprovado como modo cooperativo jogável; use-o somente se souber compilar e diagnosticar um mod inacabado.

## <a id="known-issues"></a>Problemas conhecidos

- Há uma única Mae compartilhada; os jogadores não aparecem como personagens separados.
- O comportamento normal das escolhas de diálogo e dos eventos por scripts não foi testado quanto a divergências.
- Dados persistentes de diário/contadores e progresso de salvamento não são replicados; entrada após o início e recuperação após desconexão não foram implementadas.
- A rede usa UDP direto sem autenticação, destinado a uma LAN ou VPN confiável. O comportamento em uma rede real é desconhecido.

## <a id="next-steps"></a>Próximos passos

- Testar escolhas normais de diálogo e transições de cena com bots, comparando o estado da história entre host e cliente.
- Sincronizar ou documentar explicitamente o estado persistente de diário/contadores e a responsabilidade pelos salvamentos.
- Adicionar um executor reproduzível de testes básicos e testar perda de pacotes, reconexões e uma sessão real em LAN/VPN.
- Continuar investigando as falhas ao vivo de escolhas, movimento/interação, hash da história e UDP antes de oferecer o mod aos jogadores.
