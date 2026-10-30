# <a id="the-last-of-us-part-ii-remastered-2025"></a>The Last of Us Part II Remastered (2025)

| | |
|---|---|
| Motor | Proprietário da Naughty Dog, x64 nativo, DirectX 12. Binário fechado, sem API oficial de mods. |
| Versões testadas | Nenhuma. Este agente não tinha cópia comercial disponível, então nenhum mod foi executado. Identidade comercial: aplicativo Steam 2531310, lançado em 2025-04-03. O mod cooperativo de Awperati tem como alvo a compilação de lançamento, `tlou-ii.exe`, timestamp PE `67ED75F7` (2025-04-03). |
| Projetos | ProjectSync (ainda sem repositório público); TLOU2 Co-op de Awperati; TLOU2 Co-op Hook de foufouadi; TLOU2 Multiplayer Mod de Speclizer (encerrado). As entradas do diretório usam os mesmos nomes. |
| Nível de QA | none |
| Última atualização | 2026-10-23 |

## <a id="where-things-stand"></a>Situação atual

Nenhum mod cooperativo de TLOU2 para PC foi lançado. O projeto mais próximo disso, o mod multiplayer de Speclizer, chegou a PvP 4v4 e um modo cooperativo experimental, mas foi cancelado em setembro de 2026 depois que a Sony pediu que não fosse lançado. Dois projetos iniciais estão ativos: ProjectSync (cooperação on-line em No Return, ainda sem download) e o modo cooperativo de história para dois PCs de Awperati (a camada de rede funciona, mas a ligação com o jogo não está mapeada). O modo cooperativo no sofá ainda não é possível: ele é uma camada de tela dividida sobre um modo cooperativo funcional, e o jogo não tem código de rede em que se basear.

## <a id="existing-work"></a>Trabalhos existentes

Pesquisados em 2026-10-23: diretório e `games/` deste repositório, busca de repositórios e código na API do GitHub, busca na web (incluindo resultados do Reddit) e páginas dos projetos indicados. Nexus Mods e ModDB não foram pesquisados diretamente. Nenhum download foi executado.

- **ProjectSync** (usuário Reddit `leiden_core`), anunciado em 2026-10-18. Primeiro modo cooperativo on-line para dois jogadores em No Return, depois campanha da história e, por fim, PvP. A demonstração mostra Dina e Ellie no abrigo; os relatos dizem que movimento, animações, armas, mochila, lanternas, combate corpo a corpo, IA dos inimigos e dano são sincronizados. Sem download ou repositório público; há promessa de ser gratuito e de código aberto. É o caminho mais promissor para um modo cooperativo real.
- **TLOU2 Co-op (Awperati)**, criado em 2026-10-09, v0.1.0 lançada em 2026-10-17, commits até 2026-10-19. Dois PCs, autoridade do host, jogador 2 assumindo o companheiro do capítulo (Dina, Lev, Jesse e outros). O README diz que camada de rede, teletransporte, lista de personagens, sobreposição e carregador foram testados, mas a ligação com o jogo não está mapeada, então os personagens não podem se mover dentro dele. A compilação-alvo é a de lançamento de 2025-04-03. LAN com retransmissor opcional pela internet. Código-fonte público, sem arquivo de licença.
- **TLOU2 Co-op Hook (foufouadi)**, um commit em 2026-08-02. Injeção de DLL, sincronização de posição por UDP local e clone visual de Ellie ao pressionar F10. Sem segundo jogador controlável e sem sincronização de estado de NPCs. Não funcional; útil pelas notas técnicas.
- **TLOU2 Multiplayer Mod (Speclizer)**, desenvolvido de janeiro a setembro de 2026. PvP (4v4) e modo cooperativo experimental mostrado em abril de 2026. Em julho tinha cinco mapas, configurações de equipamento e placares. Cancelado em 2026-09-14 após carta da Sony Interactive Entertainment; nunca lançado. Não retome o projeto.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- Compilação x64 nativa com DirectX 12 do motor interno da Naughty Dog, distribuída como um executável grande e DLLs de middleware. O roteiro de Awperati registra ausência de antitrapaça e de API oficial de mods.
- O jogo de um jogador não inclui modo multiplayer nem código de rede utilizável. The Last of Us Online foi cancelado em 2023, então não há replicação ou camada de sessão nativas para ampliar.
- O roteiro de Awperati informa que o jogo pausa quando perde o foco. Isso importa para futuras configurações de tela dividida ou várias instâncias.
- Desconhecidos: organização dos salvamentos/perfis, representação das fases e do estado da história, possibilidade de duas instâncias em um PC atingirem taxa de quadros jogável e transporte do tráfego de ProjectSync.

## <a id="what-we-changed"></a>O que alteramos

Nada. Este relato registra a identidade do jogo e o estado dos projetos existentes. Nenhum arquivo de jogo foi copiado e nenhum mod foi executado.

## <a id="qa"></a>QA

Nenhum teste foi executado. Este agente não tinha cópia comercial disponível, e nenhum dos projetos tem uma compilação pública jogável. O nível de QA é `none`.

## <a id="how-to-play"></a>Como jogar

Ainda não está disponível.

- ProjectSync: aguarde uma compilação pública.
- Mod de Awperati: exige dois PCs, uma cópia comercial da compilação de lançamento de 2025-04-03 e uma compilação do próprio mod; ainda não consegue mover personagens dentro do jogo.
- Mod de Speclizer: nunca foi lançado e a Sony pediu que não fosse; não procure republicações.

O modo cooperativo no sofá em um PC precisará de uma camada de inicialização, como Nucleus Co-op, depois que a cooperação funcionar, pois o jogo não tem tela dividida nem código de rede.

## <a id="known-issues"></a>Problemas conhecidos

- Sem modo cooperativo lançado; nada para jogar atualmente.
- O projeto mais próximo de estar completo foi cancelado a pedido da publicadora.
- Os mods ativos estão no início e têm como alvo uma compilação específica; atualizações do jogo podem quebrar offsets.
- Duas instâncias em um PC precisariam de salvamentos/perfis separados, isolamento de entradas e correção do foco; o jogo pausa ao perder o foco.
- O código-fonte público do mod de Awperati não tem arquivo de licença; portanto, trate-o como código disponível para consulta, não como código aberto.

## <a id="next-steps"></a>Próximos passos

- Acompanhar ProjectSync; quando houver uma compilação, registrar a versão do jogo, transporte e possibilidade de executar dois clientes em localhost.
- Conferir os marcos de Awperati e perguntar se haverá suporte a compilações posteriores.
- Quando o modo cooperativo funcionar, criar um handler do Nucleus Co-op para jogar no sofá: salvamentos por instância, isolamento de controles, janelas sem bordas e foco simulado.
- Mapear a organização dos salvamentos/perfis e a representação do estado da história para testes com várias instâncias.
- Não retomar o mod de Speclizer; a publicadora pediu que não fosse lançado.
- Abrir uma issue "claim a game" se alguém iniciar uma nova implementação cooperativa de TLOU2.

## <a id="sources"></a>Fontes

- https://www.pcgamer.com/games/action/that-last-of-us-2-multiplayer-mod-everyone-was-looking-forward-to-has-been-killed-by-sony/
- https://www.pcgamer.com/games/action/the-last-of-us-multiplayer-mod-has-hit-a-big-milestone-as-it-prepares-for-launch-in-september
- https://www.gamingbible.com/news/the-last-of-us-projectsync-co-op-mod-128815-20261018
- https://www.reddit.com/r/thelastofus/comments/1x8w74m/coop_for_no_return_in_the_last_of_us_part_ii/
- https://www.gamingbible.com/news/platform/pc/the-last-of-us-2-co-op-mod-finally-914636-20260410
- https://github.com/Awperati/tlou2-coop
- https://github.com/foufouadi/TLOU2_Co-op
- https://store.steampowered.com/app/2531310/
