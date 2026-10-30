# <a id="metal-gear-solid-v-the-phantom-pain-co-op-notes"></a>Metal Gear Solid V: The Phantom Pain: notas sobre modo cooperativo

Etapa somente de pesquisa (não escrevemos código, instalamos o jogo ou fizemos engenharia reversa). Todas as descobertas vêm de páginas públicas, API do GitHub e busca na web. As datas indicam quando foram verificadas.

## <a id="game-identity"></a>Identidade do jogo

| | Valor |
|---|---|
| Jogo | Metal Gear Solid V: The Phantom Pain |
| Lançamento | 2015 |
| Motor | Fox Engine (Konami, fechado/proprietário) |
| Scripts | Lua 5.1 incorporado; a maior parte da lógica usa scripts |
| Loja testada | nenhuma por nós; mods visam a versão Steam (AppID 287700) |
| Hash do executável | unknown (não calculado; nenhuma instalação alterada) |

Ainda não constava em DIRECTORY.md de coop-anything antes desta etapa. Jogo relacionado não coberto aqui: MGSV: Ground Zeroes (jogo separado, mesmo motor); não foi encontrado projeto cooperativo para ele, mas não houve busca aprofundada.

## <a id="goal"></a>Objetivo

Jogar The Phantom Pain em modo cooperativo com amigos. Hoje só existe uma opção para 2 jogadores (Dynamite). Nada oferece uma compilação jogável para 3 ou mais.

## <a id="research-log"></a>Registro da pesquisa

### <a id="2026-10-28-phase-0-1-triage--research-web-only"></a>2026-10-28 Etapas 0-1: triagem + pesquisa (somente web)

#### <a id="found-with-sources"></a>Descobertas (com fontes)

| Descoberta | O que realmente é | Licença | Última atividade | Jogadores | Utilidade para nós |
|---|---|---|---|---|---|
| [unknown321/dynamite](https://github.com/unknown321/dynamite) | A opção real. Mod cooperativo para 2 jogadores, em desenvolvimento inicial. Vídeos de missões reais completas (missões 5, 15). PC Gamer: "a functioning Metal Gear Solid 5 co-op mod". Distribui `masterserver/` e `hook/`. Exige cópia Steam sem modificações (JP não suportada) e **retorno de versão** antes de instalar (issue #136). | GPL-3.0 **+ Commons Clause** (sem venda) | envio em 2026-09-29; criado em 2025-07-20; vídeo v0.6.0 de 2025-10-31; 476 estrelas, 55 issues abertas | 2 | Alvo do caminho 1: retomar/concluir. Relatos de bugs nas issues GitHub. |
| [Hound-Protocol/Joint-Operations](https://github.com/Hound-Protocol/Joint-Operations) | Objetivo de até 16 jogadores (1 host + 15 clientes) em mundo aberto, Windows + Linux/Proton. Muita estrutura organizacional/documental/de pesquisa; o README afirma **"Nothing is playable yet."** A primeira compilação 0.1 (2 jogadores) está *planejada*. Pretende usar os recursos on-line do próprio jogo + SDK Steamworks. | GPL-3.0-only (documentação CC BY-SA 4.0) | envio em 2026-10-25; criado em 2026-10-21; 0 estrelas, 0 issues | até 16 (planejado) | Acompanhar. As notas públicas de pesquisa/decisões podem ajudar. Política de propriedade intelectual por desenvolvimento independente (não copiará código de Dynamite). |
| [alex-ppg/mgs-v-multiplayer-mod](https://github.com/alex-ppg/mgs-v-multiplayer-mod) | Repositório provisório. README de uma linha; cooperativo como primeiro objetivo. Ainda sem código. | CC0-1.0 | criado + enviado em 2026-10-25; 0 estrelas, 0 issues | unknown | Acompanhar; ainda sem nada utilizável. |
| MGSV Modding Wiki: [Infinite Heaven](https://www.nexusmods.com/metalgearsolidvtpp/mods/1226), [V_Framework](https://mgsvmoddingwiki.github.io/V_Framework/), [IHHook](https://mgsvmoddingwiki.github.io/IHHook), [Zeta](https://mgsvmoddingwiki.github.io/Zeta) | Ferramentas de modificação, não modo cooperativo em si. Infinite Heaven = grande estrutura Lua de missões. V_Framework = camada Lua que expõe interface/som/soldados/chefes/veículos (rompe a separação entre Lua e o executável), exige IH + jogo 1.0.15.3/1.0.15.4. IHHook = proxy `dinput8.dll` que acrescenta API C de Lua. Zeta = gerenciador/estrutura de mods interno. | varia | atual | O motivo de ser viável criar modo cooperativo aqui: hook nativo (IHHook) + amplo controle Lua (IH/V_Framework). |
| [TinManTex/MockFox](https://github.com/TinManTex/MockFox) | Executa o Lua do jogo + scripts IH fora do jogo, em um interpretador Lua; usado para gerar a documentação IH. | consulte o repositório | - | Análise Lua offline sem iniciar o jogo. |

#### <a id="observed-facts-from-sources"></a>Observado (fatos das fontes)

- Fox Engine é fechado/proprietário (Konami); não existe descompilação ou port de código-fonte.
- MGSV usa intensamente scripts Lua 5.1; Lua fica em `data1.dat`/patch `.dat` e dentro de arquivos `fpk`. É nessa camada que as ferramentas IH/V_Framework inserem hooks.
- FOB (Forward Operating Base) é infiltração PvP assíncrona; Metal Gear Online (MGO) é um modo multiplayer separado, sem relação. Nenhum é campanha cooperativa.
- Dynamite é a única compilação em que há relatos de partidas cooperativas reais.

#### <a id="derived-not-verified-by-us"></a>Deduções (não verificadas por nós)

- É uma situação de **caminho 1 (retomar/concluir)**, não de criar do zero: existe um mod funcional para 2 jogadores. A resposta honesta para quem quer jogar agora é Dynamite.
- A presença de `masterserver/` e a exigência de conexão on-line de Dynamite indicam pareamento hospedado e/ou retransmissão, com instâncias sincronizadas por autoridade do host. O transporte exato **não foi confirmado** na documentação pública lida até este ponto.
- Uma campanha cooperativa no Fox Engine quase certamente usa a camada Lua (IH/V_Framework) e um hook nativo (proxy `dinput8.dll` no estilo IHHook) para sincronizar estado/entidades, pois não há código de rede cooperativo incorporado utilizável nem código-fonte.

#### <a id="unknown-next-to-check"></a>Desconhecidos (próximos itens a verificar)

- Modelo exato de rede de Dynamite (IP direto? retransmissão? P2P + servidor principal para pareamento?) e número de compilação suportada / versão exata para retornar (issue #136).
- O que Dynamite realmente sincroniza além de dois jogadores na mesma missão: mundo, Mother Base, itens, responsabilidade sobre salvamentos/progressão. Exige ler a documentação (`webui/docs/docs.md`, `docs/MAKING_OF.md`) e/ou instalar para testes.
- Se Dynamite usa Infinite Heaven como base ou insere hooks independentemente.
- Viabilidade da licença: GPL-3.0 + Commons Clause permite forks/derivados não comerciais; adequada para retomar, não para vender.
- Ground Zeroes: alguma tentativa cooperativa (sem pesquisa aprofundada).

### <a id="2026-10-28-phase-1b-dynamite-deep-dive-its-docs--55-open-issues"></a>2026-10-28 Etapa 1b: análise aprofundada de Dynamite (documentação + 55 issues abertas)

Lidos `docs/MAKING_OF.md` (longo diário de desenvolvimento) e `webui/docs/docs.md` (documentação de usuário), e listadas as issues abertas pela API GitHub. Sem instalação ou código. Isso resolve os desconhecidos de rede/versão/itens sincronizados acima.

#### <a id="observed-from-the-authors-own-docs"></a>Observado (na documentação do próprio autor)

- **Origem:** o autor (unknown321) criou uma reimplementação do servidor principal de MGSV (`fuse`, Go+SQLite) para conectar dois jogadores em um mapa FOB e depois trocou mapa/missão pelos de um jogador, originando dynamite. Primeiro contato de dois jogadores em 2025-04-07.
- **Por que é possível:** uma sessão Fox Engine é nativamente multiplayer (até 16). Missões de um jogador executam sessão com 1; missões FOB usam a mesma sessão, mas permitem entrada de um segundo.
- **Conexão:** sessão Steam P2P, host aceita conexões de entrada, cliente fornece o **SteamID** do host (pela interface ou fixado no código). Uma conexão à rede Steam é necessária para intermediar; após conectar, o cliente conhece o IP do host (há, portanto, superfície para abuso, tratada por listas de bloqueio/permissão em `dynamite.log.txt`). O cliente precisa pressionar Master+UP (`Dynamite.CreateClientSession`) depois de o host carregar, todas as vezes.
- **Duas instâncias de jogador:** missões de um jogador alocam uma instância; editar uma definição `.fox2` acrescenta a segunda para ambas serem renderizadas.
- **Autoridade do host:** inimigos são programados para atacar jogador 0 (host) e ignorar quem entra ("defensor"). A IA é controlada pelo host; comandos de movimento são enviados ao cliente. Dynamite altera o alvo para a entidade de jogador mais próxima.
- **Camada nativa:** começou com alteração de bytes do executável em Go puro (sem DLL) por portabilidade; a lógica de seleção de alvos exigiu migrar para C++ por um proxy `dinput8.dll` baseado em **IHHook** (IHHook faz parte de Infinite Heaven, mas dynamite NÃO é baseado em IH e rejeitou essa base por legibilidade/compatibilidade).
- **Marcadores:** primeiro adaptados a um pacote `AddLocalDamage` (6 números de ponto flutuante), depois substituídos pelas mensagens de rede internas do jogo. Só cerca de 11 instâncias de sincronização de entidades do jogo estão implementadas.
- **Proteção dos salvamentos:** o local é definido em Lua; dynamite faz backup + cópia e executa sobre a cópia (ferramenta `squib`); dados de um jogador intactos, fundos/recursos on-line simulados.
- **Empacotamento:** binário Go único multiplataforma; ferramenta própria `datfpk` para reempacotar (SnakeBite/Makebite e GzsTool rejeitados por não funcionarem adequadamente no Linux / em iteração rápida); configuração `.ini` editada por interface web local; `fuse` local na porta 6667 evita enviar registros cooperativos à Konami (risco de banimento).
- **Plataformas:** Windows 10+ e Linux/SteamOS (Proton exige `WINEDLLOVERRIDES="dinput8.dll=n,b"`).
- **Versão:** última distribuída v0.6.0 (2025-10-31); master recebeu envio até 2026-09-29. Issue #136: atualização Steam de 2026-06-09 quebra a inicialização, tornando obrigatório voltar à anterior (identificador exato da compilação anterior não informado).

#### <a id="what-it-really-syncs-observed"></a>O que realmente sincroniza (observado)

| Área | Estado |
|---|---|
| Visibilidade dos jogadores | Com bugs. Avatar do parceiro frequentemente só aparece no modo FOB, não em missões normais (#109, #59). |
| Inimigos | Parcial. Sinais vitais sincronizados; posições e campo de visão NÃO (#112, #113); IA conduzida pelo host. |
| História/objetivos | Parcial. Objetivos secundários e marcadores não compartilhados (#115, #117); alguns atualizam só no host (#118). |
| Mundo | Parcial. Clima só no host; mecanismos/física dessincronizados; captura de posto não anunciada ao cliente (#98). |
| Itens/equipamento | Individual e parcial. Entrega de equipamento invisível ao parceiro; entrega de munição pode ser do jogador errado; coleta de arma não permitida (#87, #45). |
| Veículos | Quebrados. Apenas uma instância, posição dessincronizada, motorista congelado; tanque no host pode causar falha (#128, #35, #42, #47). |
| Companheiros | Quiet/D-Dog locais (parceiro não vê); D-Horse causa dessincronização de teletransporte (#43, #90, #122). |
| Marcadores (usuário + inimigo) | Funcionam (sincronização personalizada). |

#### <a id="bug-clusters-from-the-55-open-issues"></a>Grupos de bugs (das 55 issues abertas)

- **Conexão/instalador:** #136 (patch de 2026-06-09 impede iniciar), #129/#127 falhas de conexão, #92/#76/#102 instalador, #85 (novo salvamento só conecta após desbloquear missões 1 e 2).
- **Sincronização de inimigos:** #112 posições, #113 campo de visão, #36 vingança, #55 skulls.
- **Sincronização de jogadores:** #109/#59 parceiro invisível, #29/#31 animações, #87 arma não permitida, #94 extração Fulton de carga.
- **Objetivos:** #115 marcadores, #117 objetivos secundários, #118/#95/#83 por missão.
- **Veículos/Walker Gear:** #128/#35/#42/#47/#19, #130/#116/#21.
- **Falhas por missão:** #3 (#13 Pitch Dark), #16 (#43), #103 (#30), #15 (#28), #124 (#10).
- **Melhorias/planejamento:** #58 exploração livre, #123 entrada por convite, #4 itens FOB; `>2 players` (prioridade declarada pelo autor, atualmente impede iniciar).

#### <a id="resolved-from-the-earlier-unknown-list"></a>Resolvidos da lista anterior de desconhecidos

- Modelo de rede: **confirmado** (Steam P2P por SteamID + servidor principal fuse local; autoridade do host).
- Itens sincronizados: **mapeados** (tabela acima).
- Baseado em Infinite Heaven? **Não**, usa apenas IHHook.
- Versão suportada: a versão-alvo é a compilação **anterior ao patch Steam de 2026-06-09** (identificador exato ainda desconhecido).
- Ainda pendentes: número exato da compilação anterior; se correções ainda não lançadas da master alteram os pontos acima.

## <a id="sources"></a>Fontes

- https://github.com/unknown321/dynamite
- https://github.com/unknown321/dynamite/blob/master/docs/MAKING_OF.md
- https://github.com/unknown321/dynamite/blob/master/webui/docs/docs.md
- https://github.com/unknown321/dynamite/issues
- https://www.pcgamer.com/games/action/after-10-years-theres-a-functioning-metal-gear-solid-5-co-op-mod-so-you-and-a-friend-can-be-played-like-a-damn-fiddle-together/
- https://github.com/Hound-Protocol/Joint-Operations
- https://github.com/alex-ppg/mgs-v-multiplayer-mod
- https://mgsvmoddingwiki.github.io/V_Framework/
- https://mgsvmoddingwiki.github.io/IHHook
- https://www.nexusmods.com/metalgearsolidvtpp/mods/1226
- https://github.com/TinManTex/MockFox
