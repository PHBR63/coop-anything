# <a id="nintendo-switch-co-op-and-local-wireless-mods"></a>Nintendo Switch: mods cooperativos e de rede local sem fio

Jogos de Switch são o alvo de console mais difícil nos aspectos técnico e legal, mas já há pessoas criando mods para eles. Esta página reúne os caminhos e pontos de partida. Tudo aqui pressupõe **seu console com firmware personalizado**. A Nintendo é muito protetora: nunca forneça links nem hospede arquivos de jogos, chaves, firmware ou código-fonte vazado, e nada para trapacear on-line.

## <a id="routes"></a>Caminhos

| Caminho | Quando | Dificuldade |
|---|---|---|
| **Inserir hooks no jogo em um console com firmware personalizado** | Alterar o comportamento de um jogo existente: adicionar rede local sem fio, usar o modo on-line com outro transporte, sincronizar mais estado | Difícil |
| **Rede local sem fio através de uma rede** | O jogo já tem rede local sem fio e você quer jogar à distância | Fácil, existem ferramentas |
| **Descompilação** | Existe uma descompilação do jogo (alguns títulos importantes) | Muito difícil, mas é o caminho mais poderoso |
| **Recompilação estática para PC** | Experimental para Switch; apenas ferramentas iniciais e alegações | O mais difícil, não comprovado |

## <a id="adding-local-wireless-to-a-game-the-common-request"></a>Adicionando rede local sem fio a um jogo (o pedido comum)

A rede local sem fio do Switch passa pelo serviço `ldn` do sistema, e a biblioteca de rede da Nintendo (PIA) normalmente fica sobre ele.

- Um jogo que já tem multiplayer **on-line ou LAN** muitas vezes contém a maior parte do código de sessão. Adicionar rede local sem fio pode significar inserir hooks para a sessão multiplayer existente passar por `ldn` em vez da internet.
- Um jogo com **apenas tela dividida** precisa primeiro de sincronização de rede real (consulte [how-coop-mods-work.md](how-coop-mods-work.md)) e, depois, de um transporte.
- Um jogo **para um jogador** precisa primeiro da implementação cooperativa completa, como em qualquer plataforma.

Etapas para um agente:
1. Confirme os modos multiplayer já existentes (on-line, LAN, rede local sem fio, tela dividida).
2. Localize a criação de sessões: descompile o executável principal com Ghidra (mais REA ou GhidraMCP) e procure chamadas PIA e `nn::ldn`, usando cabeçalhos comunitários do SDK para nomeá-las.
3. Insira hooks nessas funções com um framework de injeção de código e redirecione o tipo de sessão.
4. Teste com dois consoles ou um console contra kinnay/LDN em um PC Linux.

## <a id="starting-points"></a>Pontos de partida

| Ferramenta | O que oferece |
|---|---|
| [Atmosphère](https://github.com/Atmosphere-NX/Atmosphere) | Firmware personalizado de código aberto usado em quase todos os mods de Switch (GPL-2.0). Mods de jogos são carregados pelo LayeredFS e pelos patches exefs. |
| [exlaunch](https://github.com/shadowninja108/exlaunch) | Framework para injetar código C/C++ em aplicativos de Switch e inserir hooks nas funções do jogo (GPL-2.0). |
| [Skyline](https://github.com/skyline-dev/skyline) | A mesma ideia, mas somente para Smash Bros. Ultimate. |
| [nnheaders](https://github.com/open-ead/nnheaders) | Cabeçalhos comunitários do SDK do Switch, para dar nomes legíveis às chamadas descompiladas. |
| [kinnay/LDN](https://github.com/kinnay/LDN) | Implementação em Python do protocolo de rede local sem fio, para estudá-lo e testar contra um console real a partir de um PC Linux. |
| [kinnay/NintendoClients](https://github.com/kinnay/NintendoClients) | Clientes Python e uma wiki que documenta protocolos de rede da Nintendo, incluindo PIA. |
| [ldn_mitm](https://github.com/spacemeowx2/ldn_mitm) + [switch-lan-play](https://github.com/spacemeowx2/switch-lan-play) | Encaminham o tráfego local sem fio por uma rede: permitem jogar à distância títulos que já oferecem esse modo e observar seu comportamento. |
| Ghidra + [REA](https://github.com/morluto/rea) ou [GhidraMCP](https://github.com/LaurieWired/GhidraMCP) | Descompilam o executável do jogo para localizar seu código de sessão e de rede. |

## <a id="decompilations"></a>Descompilações

Alguns grandes jogos de Switch têm projetos ativos de descompilação, escritos em C++ a partir do código do jogo:

- [Super Mario Odyssey](https://github.com/MonsterDruide1/OdysseyDecomp)
- [The Legend of Zelda: Breath of the Wild](https://github.com/zeldaret/botw) (Switch 1.5.0)

Nenhum deles é um port concluído para PC, mas ambos são mapas legíveis do funcionamento do jogo, o que facilita muito a inserção de hooks. Consulte [decomp-and-recomp.md](decomp-and-recomp.md) para saber como descompilações se tornam ports.

## <a id="static-recompilation"></a>Recompilação estática

Transformar jogos de Switch em programas nativos para PC é experimental. Alguns projetos foram anunciados, e um deles teve sua origem publicamente questionada por usar código de emulador. Trate as alegações com cuidado, use apenas projetos com código-fonte público e licença clara e nunca utilize código vazado.

## <a id="emulators"></a>Emuladores

Existem emuladores de Switch, mas muitos foram retirados do ar ou receberam notificações legais. Estes guias não fornecem links para eles. Se usar algum, saiba que seu futuro pode ser incerto.

## <a id="rules"></a>Regras

- Nenhuma chave, firmware, arquivo de jogo ou link para eles neste repositório.
- Nenhum código-fonte vazado ou roubado.
- Nada de trapaças on-line nem uso contra os serviços on-line da Nintendo.
- Documente descobertas e código de sua autoria; nunca redistribua código do jogo.
