# <a id="tlou2-remastered-co-op-notes"></a>Notas sobre o modo cooperativo de TLOU2 Remastered

Data: 2026-10-23
Estado: somente pesquisa. Nenhuma cópia comercial estava disponível; nenhum mod foi executado.

## <a id="search-log"></a>Registro de pesquisa

- Consultados `DIRECTORY.md` e `games/` deste repositório: somente *The Last of Us Part I* aparecia, como lacuna. Nenhuma entrada nem relato técnico de TLOU2.
- Busca de issues e PRs neste repositório por "last of us": nenhum resultado.
- Pesquisa de repositórios na API do GitHub: "last of us co-op mod", "tlou coop", "tlou2 co-op", "ProjectSync last of us".
- Busca na web: mod de Speclizer, cancelamento pela Sony, ProjectSync, modo cooperativo No Return, resultados do Nexus Mods.
- Lidos: PC Gamer de 2026-07-29 e 2026-09-14; GamingBible de 2026-04-10 e 2026-10-18; repositórios GitHub `Awperati/tlou2-coop` (README, roteiro de desenvolvimento, guia para jogar, versão, commits) e `foufouadi/TLOU2_Co-op` (README, um commit); appdetails do Steam para o aplicativo 2531310.
- Não pesquisados diretamente: Nexus Mods (apenas resultados da web), ModDB, Discord, X (apenas por meio de artigos).

## <a id="observations-public-sources"></a>Observações (fontes públicas)

- O mod de Speclizer chegou a 4v4, com lançamento planejado para setembro de 2026, mas foi cancelado em 2026-09-14 após uma carta da Sony Interactive Entertainment. Nunca foi lançado.
- ProjectSync foi anunciado em 2026-10-18. O primeiro alvo é No Return, depois a história e, por fim, PvP. Até 2026-10-23, não havia download nem repositório público. A promessa é ser gratuito e de código aberto.
- O mod LAN de Awperati tem uma versão v0.1.0 datada de 2026-10-17 e commits até 2026-10-19. O README informa que a ligação com o jogo não está mapeada e os personagens ainda não podem se mover dentro dele. O roteiro de desenvolvimento tem como alvo `tlou-ii.exe`, com timestamp PE `67ED75F7` (2025-04-03).
- O roteiro de Awperati registra entrada sintética por XInput, um carregador `version.dll`, um host com autoridade, um representante do companheiro e o fato de o jogo pausar quando perde o foco.
- O repositório de foufouadi tem um commit (2026-08-02), um clone visual, sincronização de posição por UDP local e nenhuma sincronização de estado de NPCs.
- TLOU2 para PC não tem multiplayer nativo nem API oficial de mods. The Last of Us Online foi cancelado em 2023.

## <a id="derived"></a>Deduções

- O modo cooperativo no sofá é uma segunda camada: precisa primeiro de modo cooperativo funcional e, depois, de inicialização de várias instâncias, isolamento de entradas e tratamento do foco.
- ProjectSync é descrito como modo cooperativo on-line; nada nas fontes afirma que ele pode executar dois clientes em localhost, algo necessário para jogar no mesmo PC.
- Não se pode presumir que um mod voltado à compilação de lançamento de 2025-04-03 funcione em patches comerciais posteriores, muito menos em um repack.
- Retomar o mod de Speclizer não é apropriado: a publicadora pediu que ele não fosse lançado.

## <a id="guesses"></a>Hipóteses

- ProjectSync provavelmente usa um hook em DLL com sessão sob autoridade do host, por analogia com os outros dois projetos. Isso não está confirmado.
- Um handler do Nucleus Co-op para TLOU2 seria viável depois de existir um mod cooperativo, mas a pausa por perda de foco e a instalação grande provavelmente seriam pontos problemáticos.

## <a id="unknowns"></a>Desconhecidos

- Repositório, licença, transporte e data de lançamento do ProjectSync.
- Se ProjectSync oferece LAN ou localhost, ou somente partidas pela internet.
- Se o mod de Awperati dará suporte a compilações comerciais posteriores.
- Se duas instâncias de TLOU2 conseguem rodar em um PC com taxa de quadros jogável.
- Organização dos perfis e salvamentos da versão comercial e quanto do estado da história fica nos salvamentos.
- Se a Sony se oporia a um mod cooperativo gratuito e de código aberto. A carta de cancelamento se dirigia ao projeto de Speclizer; o motivo não é público.

## <a id="test-log"></a>Registro de testes

Nenhum. Não havia cópia comercial disponível, então nada foi iniciado. As entradas do diretório e o relato técnico se baseiam somente nas fontes públicas listadas acima.
