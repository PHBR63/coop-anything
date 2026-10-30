# <a id="fallout-tactics-brotherhood-of-steel-2001"></a>Fallout Tactics: Brotherhood of Steel (2001)

| | |
|---|---|
| Motor | Proprietário (Micro Forte), 32 bits, DirectX 7; scripts Lua por [FTSE](https://github.com/melindil/FTSE) |
| Versões testadas | GOG 1.27, SHA-256 de `BOS.exe` `C5B91FE56EF8DE118CE22CCD5E6512F217CA16C8B8758EA14C626229EB5A4E40`, com FTSE 0.60a, no Windows 11 |
| Projetos | [fallout-tactics-coop](https://github.com/thennak3/fallout-tactics-coop) (mod próprio, criado do zero, MIT; beta, versão mais recente [v0.10.4-beta](https://github.com/thennak3/fallout-tactics-coop/releases/tag/v0.10.4-beta) de 2026-10-30) |
| Nível de QA | automated (bots internos controlam 2 a 4 cópias reais em um PC e comparam o estado de cada uma), além de sessões jogadas por pessoas em dois PCs |
| Última atualização | 2026-10-28 |

## <a id="where-things-stand"></a>Situação atual

Dois a quatro jogadores conseguem jogar a campanha juntos com um único esquadrão compartilhado: cada jogador pode dar ordens a qualquer personagem, e a campanha em uso é a do host. Quem entra copia o salvamento do host e pode participar no meio da missão. Conversas, comércio, recrutamento, evolução de nível, coleta de itens, combate por turnos, mapa-múndi e encontros aleatórios são sincronizados; uma verificação de divergência realinha as cópias sem recarregar. Está em beta (v0.10.0-beta): os bots cobrem cada recurso, e duas pessoas jogaram em dois PCs em uma rede doméstica, encontrando e corrigindo vários bugs (0.9.1 a 0.9.4).

## <a id="existing-work"></a>Trabalhos existentes

- **fallout-tactics-coop** (este projeto, desde 2026-10-20): uma DLL (`netlog.dll`) carregada pelo script Lua do FTSE, que insere hooks no jogo em memória (nada em disco é alterado). Código-fonte: [thennak3/fallout-tactics-coop](https://github.com/thennak3/fallout-tactics-coop).
- Tentativas anteriores, nenhuma com download (encontradas por busca na web em 2026-10-20; as páginas dos fóruns recusaram acesso, então apenas os resumos da busca foram lidos): um mod cooperativo do clã TBC com jogador "battlemaster" controlando a IA (TTLG, por volta de 2003), "The COOP Mod" no NMA (mapas multiplayer originais, alegadamente 40% concluído) e instruções NMA e GameSAS para copiar mapas de campanha para o multiplayer. Tópicos Steam de 2014 e 2022 dizem não existir campanha cooperativa. Detalhes em [NOTES.md](NOTES.md).

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **O multiplayer usa lockstep.** Cada ordem é um registro de comando de 27 bytes enviado ao host, que o retransmite a todas as cópias, e todas o executam no mesmo quadro (executor de comandos Actor, `0x5747e0`). O jogo foi distribuído apenas com multiplayer esquadrão contra esquadrão; por isso, o mod executa a campanha dentro de uma sessão multiplayer com um esquadrão compartilhado. As mensagens do mod trafegam no mesmo fluxo como registros do comando `0x30`.
- **O que lockstep não cobre:** telas de um jogador que alteram o jogo em apenas uma cópia (conversas, escambo, telas de recrutamento e personagem). O mod captura a tabela de entidades, inventários, variáveis e atributos quando a tela abre e envia as diferenças como delta quando ela fecha, aplicado por todas as cópias no mesmo quadro. A tabela de entidades (World+0x743, entradas de 8 bytes, lista livre em World+0x74f) é a parte difícil: o delta carrega os dados de gerenciamento para todas as cópias distribuírem as mesmas vagas depois.
- **Salvamentos** são copiados pela conexão TCP própria do mod (porta 47701, também usada para descoberta por UDP e consultas de quem entra). Mudanças de mapa, entradas no meio da sessão e raras ressincronizações completas usam um salvamento rápido do host carregado por todas as cópias.
- **Aleatoriedade** vem de um LCG com semente por quadro no World, idêntico em todas as cópias. Os hooks Lua do FTSE são a exceção: `OnBurstAttack` usava `math.random` com semente do relógio, separando as cópias em toda luta com NPCs até ser substituído por um gerador determinístico.
- Ferramentas: Ghidra pelo REA, leitor de dumps para minidumps WER e bots internos descritos abaixo. Endereços e como foram encontrados estão em [NOTES.md](NOTES.md).

## <a id="what-we-changed"></a>O que alteramos

O histórico completo está em [NOTES.md](NOTES.md); principais correções e os testes que as demonstraram:

- **Rajadas de NPCs tinham resultados diferentes em cada cópia:** `OnBurstAttack` Lua do FTSE usava RNG com semente do relógio; substituído por gerador Park-Miller determinístico. Execuções de caos (todas as cópias agindo aleatoriamente) deixaram de divergir (3 jogadores, 38/38).
- **Lojas não pausam ninguém:** o estoque do comerciante é criado em todas as cópias no mesmo quadro, e a negociação é enviada como delta. Enquanto uma loja está aberta, movimentos de itens dos outros jogadores (dar, pegar, largar, equipar, desequipar, usar) aguardam e executam juntos quando ela fecha, pois a loja cria e destrói entidades somente na cópia do comprador (`trade_host --inv-chaos` falhou duas vezes; depois 48/48; `trade_join --inv-chaos` 49/49).
- **Coleta de itens:** somente a cópia de quem coletava removia entradas mortas da lista de itens de um recipiente, fazendo as cópias divergirem para sempre. Agora todas eliminam essas entradas após uma coleta (`loot`, 24/24).
- **Combate por turnos:** jogador da vez e End Turn funcionam para todos; as configurações do host (modo por turnos, dificuldade, fogo amigo...) se aplicam a todas as cópias (`turnbased` com 4 jogadores, 69/69; `tbauto` 29/29).
- **Verificação de divergência:** a cada 25 quadros, cada cópia calcula hashes de posições, HP, tabela de entidades, inventários, equipamentos e atributos; ao detectar diferença, todas seguram um quadro e adotam os valores do host. Antes, a comparação parava após a primeira correção quando um carregamento reiniciava a contagem de quadros; agora é por salvamento carregado (`drift_equip`, 25/25).
- **Crescimento da tabela de entidades durante tela privada** antes forçava salvamento e recarga; agora o delta informa isso, e cada cópia amplia a tabela pelo mecanismo do próprio jogo (`talk_host --grow-table` 30/30, `talk_join --grow-table` 31/31).
- **Travamento ao sair de sessão para o menu principal:** a função da tela Load Game (`0x4ca7b0`) remove um argumento da pilha (`ret 4`) e era chamada sem ele; encontrado em um minidump WER (`menu_join --menu-cancel`: a chamada antiga encerra com 0xC0000409; corrigido, 36/36).
- **Mapa-múndi:** só o host move o grupo; os outros veem a viagem e podem marcar um ponto com sua cor (`worldmap`, 33/33). Somente a cópia do host sorteia encontros aleatórios; as demais a acompanham (`encounter`, 26/26).
- **Entrada:** consultas fixas de 1-2 s foram reduzidas a 250 ms (entrada no meio da sessão de 7,9 s para 3,5 s), e o objeto DirectPlay da tela Multiplayer é mantido ativo em vez de liberado: sua liberação bloqueava por 3 s, e o próximo objeto DirectPlay esperava por ele até em outra thread (de Join ao jogo de 3,6 s para 1,2 s, v0.10.1-beta).
- **Dois PCs:** WSAECONNRESET do Windows após ICMP de porta inacessível interrompia a descoberta; desativado com SIO_UDP_CONNRESET (dois PCs).

## <a id="qa"></a>QA

- `python -I test/run_test.py <test>` no repositório do mod inicia 2 a 4 cópias de teste em um PC, cada uma com bot interno (`src/bot_scenarios.inc`), e verifica os logs. Todo teste compara, em cada quadro de captura compartilhada: posição e HP de todos os atores, todos os inventários com mãos e armaduras, gerenciamento da tabela de entidades, variáveis de missões, atributos, esquadrão e estoque do comerciante. Cada cenário acrescenta verificações próprias (negociação concluída, turno passado, nenhuma recarga e assim por diante). Execuções de caos falham diante de qualquer relato de divergência.
- Resultados de 0.9.3 e 0.9.4, código em v0.10.0-beta (execuções direcionadas, 2026-10-28): `worldmap` 33/33, `trade_host --inv-chaos` 48/48, `trade_join --inv-chaos` 49/49, `drift_equip` 25/25, `talk_host --grow-table` 30/30, `talk_join --grow-table` 31/31, `menu_join` 34/34, `menu_join --menu-cancel` 36/36, `dropin` 37/37, `resync` 25/25, `encounter` 26/26, `recruitnew_host` 29/29, `chaos` (containers.sav, com equipamento) 22/22. A suíte completa (`test/run_suite.py`) não foi executada novamente para essas versões.
- Pessoas: dois jogadores em dois PCs na mesma rede doméstica, em 2026-10-27 (os bugs encontrados foram corrigidos nas versões 0.9.1 a 0.9.3).

## <a id="how-to-play"></a>Como jogar

Cada jogador precisa de Fallout Tactics da GOG (1.27; confira o hash acima), [FTSE 0.60a](https://github.com/melindil/FTSE/releases/tag/0.60a) e ZIP do mod da [página de versões](https://github.com/thennak3/fallout-tactics-coop/releases), extraído ao lado de `BOS.exe`. O host escolhe Multiplayer > Start Co-op e carrega um salvamento; amigos selecionam a sessão `[Co-op]` do host na lista Multiplayer e pressionam Join. Os jogadores precisam alcançar o PC do host: rede doméstica ou LAN virtual como Tailscale ou ZeroTier. Passos completos no README do mod.

## <a id="known-issues"></a>Problemas conhecidos

- Enquanto um jogador conversa com alguém que não seja comerciante, ou usa o recrutador, os jogos dos outros pausam até a conversa fechar.
- Um personagem que entra no esquadrão por conversa da história (não pelo recrutador) ainda exige salvamento e recarga para todos.
- Ainda não jogado pela internet.

## <a id="next-steps"></a>Próximos passos

- Coleta em cadáveres, participante carregando salvamento próprio, fala forçada por scripts, apostas, comerciantes que não sejam intendentes e tela de recrutamento múltiplo ainda não têm testes com bots.
- A tabela de entidades cresceu de 2.000 para 16.000 vagas em uma noite de jogo; só cresce quando a lista livre acaba, então vagas livres podem estar sendo perdidas em algum ponto.
- Personagem que entra por conversa da história: o caminho desativado que o recria em todas as cópias alterou o estado de IA de um NPC em uma delas.
