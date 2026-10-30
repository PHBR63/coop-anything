# <a id="the-witness-2016"></a>The Witness (2016)

| | |
|---|---|
| Motor | Motor próprio (Thekla). Família não confirmada: `detect_engine` não encontrou assinatura |
| Versões testadas | Compilação Steam `11370412` (app `210970`), `witness64_d3d11.exe` SHA-256 `8d672d444df6a6df7130f25a517bdab1af92731fe2138dc5b324d519561d55a5`, Windows |
| Projetos | [witness-coop](https://github.com/TommoDotCommo/witness-coop) (MIT, prévia de desenvolvimento). Ferramentas relacionadas: [witness-randomizer](https://github.com/jbzdarkid/witness-randomizer) (MIT), [witness-trainer](https://github.com/jbzdarkid/witness-trainer) (MIT) |
| Nível de QA | automated (restrito: três quebra-cabeças do tutorial, localhost, veja QA) |
| Última atualização | 2026-10-22 |

## <a id="where-things-stand"></a>Situação atual

Nenhum outro modo cooperativo para The Witness foi encontrado. [witness-coop](https://github.com/TommoDotCommo/witness-coop) é um protótipo de prévia de desenvolvimento que executa duas cópias do jogo em um PC: cada jogador vê o outro como um representante desenhado por sobreposição Direct3D 11; quando um resolve um painel, o outro jogo o marca como resolvido e abre a porta correspondente pela função de portas do próprio jogo. O detector acompanha todos os 594 painéis e 327 portas, mas só três quebra-cabeças do tutorial têm resolução natural automatizada e comparação de estado: os dois primeiros de portas e um preto/branco que energiza outro painel. A progressão de energização dos painéis sincroniza separadamente do estado resolvido; um cabo (aceso por um labirinto do tutorial) foi verificado. Um participante novo (reinício ou primeira entrada tardia) e o recarregamento de salvamento no mesmo processo ressincronizam a partir do outro jogo. Desligamento, outros tipos de cabo, lasers, placas e pontes continuam sem sincronização.

## <a id="existing-work"></a>Trabalhos existentes

Nenhum projeto cooperativo ou multiplayer. Pesquisados sem resultado: este repositório, issues, PRs e busca de repositórios do GitHub, busca na web. Não verificados: Nexus, ModDB, Reddit, archive.org, Discords do jogo e de speedrun, comunidades em outros idiomas (veja `searched:` na entrada do diretório).

Ferramentas que acessam o interior do jogo:

| Projeto | Licença | Último push | Função |
|---|---|---|---|
| [witness-randomizer](https://github.com/jbzdarkid/witness-randomizer) | MIT | 2026-01 | Lê e escreve campos de entidades (painéis, portas) de fora do processo |
| [witness-trainer](https://github.com/jbzdarkid/witness-trainer) | MIT | 2026-09 | Posição e ângulo de câmera, noclip, controle de salvamento, estado de painéis, chamada de abertura de porta, encontrados por varredura de assinaturas |
| Archipelago `worlds/witness` | veja o repositório | n/a | Cliente de randomizador roda junto ao jogo; não foi lido como insere hooks |
| [TheWitnessExplorer](https://github.com/ClementSparrow/TheWitnessExplorer) | nenhuma informada | 2021 | Exploração de recursos em Python |

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para modo cooperativo)

Observado na compilação 11370412 (detalhes e fontes em [NOTES.md](NOTES.md)):

- Jogo para um jogador, nenhum código de rede encontrado. Recursos em `data-pc.zip`.
- Uma tabela global de entidades (`GLOBALS` fica a `0x62D0A0` da base do módulo) contém um vetor de ponteiros indexado pelo ID da entidade. Tipos têm nomes acessíveis por cada entidade (`entity+0x08` para um descritor, nome em `+0x08`): 48 tipos, incluindo `Machine_Panel` (594), `Door` (327), `Power_Cable`, `Pressure_Plate`, `Multipanel`, `Human` (jogador, ID `0x1E465`).
- Posição de câmera (3 floats) e ângulos (2 floats) ficam em endereços estáticos e acompanham o jogador.
- Estado resolvido do painel: float na entidade em `+0x294` (`1.0` quando resolvido), int em `+0x298` (resolvido alguma vez), int de estado em `+0x280`. Uma porta está aberta quando seu valor de energia em `+0x1D0` é `1.0`.
- Resolver altera poucas coisas na memória (15 entidades no primeiro painel): campos do próprio painel, valores de energia na porta de destino e seu nó de grupo, transformações das partes da porta. Escrever esses campos no outro jogo **não** abriu a porta; a abertura começa por chamada de função (`base + 0x8E4B0`, a usada pelo trainer).
- Inicialização: o executável mostra primeiro uma janela de opções gráficas. `-skip_config_dialog -windowed -new_game` inicia o mundo sem entrada do usuário.
- Um proxy `AnselSDK64.dll` (carregado pelo executável da própria pasta) carrega nosso código no jogo. Insere hook em `IDXGISwapChain::Present` e desenha quadriláteros em posições do mundo (modelo de câmera: z para cima, campo de visão vertical de cerca de 60 graus, conferido com capturas em duas direções e durante caminhada). Mudar o campo de posição de um painel não o move na tela.

Desconhecidos: como sincronizar cabos e painéis energizados, efeitos de outras entidades, salvamentos e novos jogos, e diferenças entre compilações de outras lojas (o randomizador já conhece duas com deslocamentos distintos).

## <a id="what-we-changed"></a>O que alteramos

Nada nos arquivos do jogo; a instalação real nunca foi modificada. Nas cópias descartáveis acrescentamos uma DLL proxy com troca de poses e sobreposição do representante, detector de painéis resolvidos e portas abertas, camada de eventos confiável (numeração, confirmação, reenvio, aplicação única e ordenada, épocas e reenvio completo ao reiniciar um participante) e aplicação na thread de renderização com proteção contra eco. Código em [witness-coop](https://github.com/TommoDotCommo/witness-coop).

## <a id="qa"></a>QA

Uma suíte por script (`tools/qa.sh` em witness-coop) reinicia ambos os jogos, controla o jogador A por bot pelo controle interno do mod (sem focar janelas ou usar entrada da área de trabalho: teleportar ao primeiro painel, mirar, clicar para entrar, traçar a linha, clicar para concluir) e compara painéis resolvidos e portas abertas lidos da memória dos dois jogos. Última execução (2026-10-22, uma máquina, localhost, compilação 11370412); dois agentes também executaram o teste de referência simultaneamente, ao lado de um agente MDK2, sem conflito e sem nenhuma janela tomar o foco do jogador:

```
baseline                                 PASS   identical (1 panel, 10 doors); B sent nothing back; real saves and mouse untouched; game at 30 fps
lost first send of every event           PASS   identical; A resent all 11 events
MUTANT: no resend + lost first send      PASS   games diverged (panel 0x64 and door 0x34eda only on A), as required
MUTANT: frame cap off                    PASS   game A read 1123 fps (uncapped), as required
MUTANT: echo guard off                   PASS   B echoed its 2 events back, as required
ALL OK
```

Verificações anteriores: sondagens de memória somente de leitura antes e após resolver; caminhada por script após a qual o log do outro jogo mostrou a posição do primeiro (-199.82, -119.82, 3.73) contra sua câmera real (-199.819, -119.816, 3.727), com 31 ms de idade; capturas do representante e dos marcadores sobre painéis conhecidos.

Execução direcionada adicional (2026-10-22, witness-coop `df7b276`): recuperação após reiniciar participante e variante sem reenvio, ambas PASS. A resolução original do primeiro painel chega aos dois e é confirmada antes de reiniciar B num mundo novo. A sobrevivente mantém PID e estado; B novo recupera todo o progresso (um painel, dez portas) sem eco. Com recuperação desativada, faltam em B exatamente o painel `0x64` e a porta `0x34eda`. Verificações de salvamentos reais, cursor e limite de quadros passam. Isso exercita reenvio completo após as diferenças originais já terem sido confirmadas.

Execução direcionada (2026-10-22, witness-coop `cfb67a0`, saída do comando 0): execução normal e variante que ignora índice zero, ambas PASS. Isolamento dos salvamentos, cursor livre e 30.0 fps passaram. O segundo bot de tutorial (`wbot2.py`) revelou um bug real do adaptador: detector começava no índice 1, ignorando a porta no índice 0 aberta por Tutorial Bend (`0x182`). Antes da correção, ambos tinham dois painéis resolvidos, mas só A tinha a segunda porta aberta. Incluir o índice zero produz estado idêntico (2 painéis, 11 portas); a variante mantém ambos resolvidos, mas perde exatamente essa porta em B. O bot traça a curva real de três nós e verifica a resolução na memória. Posição e percurso do cursor são calibrados para buffer traseiro de 1920x1080.

O gerenciador de entidades guarda um ID base em `globals+8` (observado 1). Mod e sondagens usam índices da tabela; campos de destino usam IDs do motor. Desmontagem em `exe+0xB9F00` subtrai essa base antes de buscar o destino e abrir sua porta. Assim, o destino bruto 1 do segundo painel significa índice 0. Isso corrige a interpretação anterior do destino do primeiro painel como entidade Inanimate; ele também nomeia uma porta após normalização. `wpanel.py` relata o grafo e os dois espaços de nomes de destino.

A progressão de energização dos painéis agora usa efeito confiável separado (tipo 3). O aplicador chama a função de energização do jogo em `exe+0xC2890`, com tipo e prólogo conferidos, na thread de renderização. Energia solicitada fica em `+0x2A4`; o jogo atualiza a energia visível em `+0x2A0`. Ativar um destino não o marca como resolvido. O núcleo acompanha energia na estabilização inicial e nas capturas e tem proteção contra eco separada. Isso é progressão de energização; não replica desligamentos.

A resolução natural do tutorial preto/branco no índice `0x18AF` energiza `0x1B`. Antes do novo evento, B recebia a resolução de origem, mas o destino continuava escuro. Um novo bot traça a rota horizontal do meio e exige que o destino energize sem ficar resolvido. O cenário normal no jogo real também reinicia B após confirmar os efeitos originais e compara painéis resolvidos, portas e painéis energizados nos dois processos. A variante sem energia precisa deixar apenas `0x1B` sem energia em B. Testes T0 de energização cobrem perda, chamadas recusadas, ausência de eco, destinos não resolvidos e capturas de reinício, com quatro variantes detectadas. Protocolo v2 usa `WTP2`/`WTE2`/`WTA2`; ambos precisam da DLL atualizada. Execução direcionada (2026-10-22, witness-coop `9799af8`, saída 0): normal e variante sem energia, ambas PASS. O caso normal inclui reiniciar B após ACKs originais e coincide em 2 painéis resolvidos, 10 portas abertas e 238 painéis energizados. A variante tem 237 energizados em B, faltando só `0x1B`. Ambas mantêm o destino não resolvido. Hashes de salvamentos, salvamentos por instância, cursor livre e 30.0 fps passam; nenhum jogo reservado permanece. Rejeição de eventos/poses v1 com checksum também tem cobertura T0, com controles de aceitação v2.

Verificado até agora: os três primeiros quebra-cabeças do tutorial (dois de portas e uma cadeia de energização preto/branco), um labirinto de cabo, perda aleatória de 30% com semente em localhost, reinício de participante, primeira entrada tardia e recarregamento de salvamento no mesmo processo, cada um com variante que precisa falhar.

Não testados: rede real, mais de dois jogadores, outros quebra-cabeças, outros tipos de cabo ou mecanismo, WAN, tela cheia, janelas fora de 16:9. Sondagens e scripts de teste estão em witness-coop.

## <a id="how-to-play"></a>Como jogar

Ainda não é possível jogar juntos de fato (somente protótipo, duas cópias num PC). Não há instalador nem versão distribuída; configuração de desenvolvimento no [README de witness-coop](https://github.com/TommoDotCommo/witness-coop).

## <a id="known-issues"></a>Problemas conhecidos

- Painéis resolvidos, portas abertas, progressão de energização e um cabo verificado sincronizam. Desligamento, outros cabos, placas, lasers e pontes não. Estado reversível ainda exige política de autoridade/conflitos.
- O representante é um retângulo plano com ponto de direção; aparece através de paredes (sem teste de profundidade).
- Recarregamento no mesmo processo é detectado por heurística (porta conhecida aberta fecha, ou dois ou mais painéis conhecidos ficam não resolvidos) e ressincronizado; portas que fechassem durante o jogo normal disparariam ressincronização extra inofensiva. Carregar outro slot não foi testado.
- Risco de teste para o próximo agente: o jogo mantém salvamentos em `%APPDATA%\The Witness`, independentemente da pasta do executável. Iniciar New Game numa cópia reescreveu o último salvamento e as configurações reais ali. Faça backup e hashes dessa pasta primeiro.

## <a id="next-steps"></a>Próximos passos

1. Estender sincronização aos demais painéis de cabos, placas, lasers, pontes, desligamentos e mais quebra-cabeças. Verificar cada um com resolução natural e comparação de estado; definir autoridade do estado reversível.
2. Rede real (retransmissão Steam ou IP direto), depois testes de latência com chaos (perda aleatória já coberta em localhost).
3. Oclusão e modelo real de representante no lugar do retângulo plano.
4. Ampliar a suíte para mais quebra-cabeças e mecanismos, mantendo o QA honesto; adicionar instalador e versão distribuída; ler o cliente Archipelago para outra visão dos mesmos hooks; concluir as buscas pendentes.
