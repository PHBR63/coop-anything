# <a id="world-in-conflict--soviet-assault-2007-2009"></a>World in Conflict + Soviet Assault (2007, 2009)

| | |
|---|---|
| Motor | Masstech (Massive Entertainment), Python 2.5 incorporado para scripts de missão |
| Versões testadas | Steam 1.0.1.1 (b35), aplicativos 21760 + 21910; GOG Complete Edition (Galaxy 2.0.0.3). Mesma compilação, consulte NOTES.md |
| Projetos | nenhum encontrado; somente pesquisa e projeto arquitetural (entrada do diretório: lacuna World in Conflict) |
| Nível de QA | none (testes manuais do protótipo pelo usuário; sem suíte automatizada) |
| Última atualização | 2026-10-17 |

## <a id="where-things-stand"></a>Situação atual

Ainda não existe mod de campanha cooperativa. Protótipo funcional (cópia de teste GOG, 2026-10-17): com quatro pequenos patches no executável, uma partida hospedada em LAN num mapa de campanha executa a missão real; um segundo cliente consegue entrar e observar a missão sincronizada ao vivo. O jogador 2 ainda não pode agir (sem unidades ou reforços, sem neblina de guerra). Detalhes, offsets e logs de teste estão em [NOTES.md](NOTES.md).

## <a id="existing-work"></a>Trabalhos existentes

- Nenhum mod de campanha cooperativa encontrado (buscas na web por "World in Conflict campaign co-op mod", "coop campaign mod moddb", "play campaign with friend", 2026-10-17). Fóruns Massgate, Discords, Reddit e pesquisas em outros idiomas ainda não consultados.
- O multiplayer funciona: LAN, servidor dedicado (`wic_ds.exe` acompanha o jogo) e bots de IA em partidas LAN/DS (`[BotMode]` em `wic_ds.ini`).
- O serviço on-line Massgate é de código aberto (GPL-2.0): https://github.com/ubisoft/massgate . `src/MNetwork` e `src/MCommon2` são as bibliotecas de rede e base vinculadas ao jogo, úteis para nomear estruturas na engenharia reversa.
- Mod Kit com editor WicEd (2007): https://worthplaying.com/article/2007/12/18/news/47533-world-in-conflict-v1005-level-editormod-sdk-available-now/

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

Observado na compilação acima, salvo indicação em contrário.

- **Executáveis e compilações.** `wic.exe` e `wic_online.exe` do Steam têm invólucro SteamStub: seção `.bind`, `.text` criptografada. Não os desempacote. O executável GOG Complete Edition é a mesma compilação sem o invólucro: mesmo timestamp PE e disposição de seções, seções de dados idênticas byte a byte e arquivos de jogo idênticos, exceto dois arquivos de localização. A análise estática usa, portanto, `wic.exe` do GOG e `wic_ds.exe` (idêntico nas duas lojas).
- **Modos de jogo.** RTTI mostra que `EX_MultiPlayerHostMode` deriva de `EX_SinglePlayerMode`: o host multiplayer é o modo de um jogador mais um servidor de rede. `InitGame` do host chama a configuração compartilhada com o booleano de modo de um jogador em 0 (um `push 0` em `0xb3f386` no executável GOG).
- **Arquivos contêiner.** Arquivos `.sdf` começam com `RYS\n` e contêm fluxos zlib brutos. Buscar cabeçalhos zlib recupera os arquivos; o índice de nomes ainda não foi decodificado.
- **Lógica de missão em Python 2.5 no servidor.** Cada mapa tem `python/server.py` (lógica de missão, gerada pelo WicEd e depois editada), `server_autogen.py`, `client.py` (câmeras e cenas no cliente), `mapvars.py` e `allunits.py`. `serverimports.py` encaminha eventos do motor (`OnUnitDestroyed`, `OnZoneTaken`, `OnPlayerConnected`, `OnPlayerLeave`, `OnPlayerAction`, ...) para um sistema de reações, cada uma condicionada a `wicg.IsSinglePlayer()`. Os scripts identificam o jogador humano por uma única constante `PLAYER_HUMAN`, o principal obstáculo na camada de scripts para dois humanos.
- **Uma classe de servidor, um indicador.** Em `wic_ds.exe`, o objeto de jogo do servidor verifica `myIsSinglePlayerGameFlag` em um byte de `EXG_Game`. O manipulador de seleção de papel verifica o mesmo byte: recusa papéis SP em partidas MP e papéis não SP em partidas SP.
- **Mapas de campanha são mapas MP.** Executar o servidor dedicado uma vez por nome padrão de ciclo de mapas mostrou que cada nome MP carrega uma pasta que também é uma missão da campanha. Exemplos: `do_Riviera` → `europe4` (missão 6 de WiC), `do_SpaceNeedle` → `seattle1` (missão 14). Todo mapa da campanha WiC tem um equivalente MP. Três mapas exclusivos de Soviet Assault não têm: `usfarmland5`, `berlin1` e `norway1`. Tabela completa em [NOTES.md](NOTES.md). Um arquivo de mapa contém os modos MP e os dados de um jogador; 19 scripts de missão têm ramificações `OnGameStarted` separadas para um jogador e multiplayer.
- **O servidor dedicado não inicia o modo SP pela configuração.** O ciclo de mapas aceita nomes MP; nomes de pastas são ignorados.
- **O modo de um jogador não tem socket real.** Durante uma missão de campanha, `wic.exe` não tinha sockets TCP e tinha um socket UDP efêmero. O servidor dedicado escuta em TCP/UDP 48000. Junto de `MN_LoopbackConnection` no binário, isso aponta para servidor e cliente no mesmo processo por loopback em memória (inferido).
- **Salvamentos.** `WICP_SaveGameHandler` e `EXCO_Persistent*` existem no cliente; salvamentos cooperativos não foram estudados.

## <a id="what-we-changed"></a>O que alteramos

Patches de protótipo em uma cópia de `wic.exe` do GOG (offsets dessa compilação; detalhes completos em NOTES.md):

| # | Onde | Alteração | Resultado |
|---|---|---|---|
| v1 | `0xb3f387` | `InitGame(0)` do host MP → `InitGame(1)` | host monta a missão de campanha |
| v2 | `0xb3f393`-`0xb3f3d7` | passar a pasta de scripts de um jogador à inicialização Python, como faz esse modo | scripts de missão carregam |
| v3 | `0xb3f7cc`-`0xb3f7e3` | criar jogador local do host com papel e indicadores de um jogador | host joga a missão |
| v4 | `0x7529d8` | `PlayerSetRole` aceita qualquer papel numa partida de um jogador | segundo cliente consegue entrar |

Armadilha encontrada: `-pythondebug` quebra todas as importações Python na compilação comercial (até no modo normal de um jogador), ocultando resultados até ser removido.

Ferramentas: DLL de rastreamento de chamadas com inicializador (código próprio) que registra argumentos e resultados dos pontos de chamada escolhidos; encontrou a etapa com falha em uma execução quando a leitura dos logs não tinha conseguido.

## <a id="qa"></a>QA

Nenhum ainda. Planejado conforme os guias: bot interno pela camada Python, dois clientes reais e comparação do estado da missão.

## <a id="how-to-play"></a>Como jogar

Ainda não jogável.

## <a id="known-issues"></a>Problemas conhecidos

Ainda não se aplica.

## <a id="next-steps"></a>Próximos passos

1. Dar controle ao jogador 2: primeiro compartilhar o controle das unidades do jogador 1 (verificação de ordens no servidor e seleção no cliente), depois forças próprias (AP, zona de lançamento, equipe, visão e conhecimento nos scripts). Mover os patches para uma DLL proxy em tempo de execução, baseada em assinaturas de bytes, para funcionar no executável GOG e no Steam após o stub executar.
2. Camada de scripts: substituir a suposição de um único `PLAYER_HUMAN` (objetivos, câmera, AP, verificações de área) para cada humano ter forças próprias, ou encaminhar ordens do convidado pelo jogador 1 como alternativa.
3. Transporte: retransmissor Steam Spacewar junto ao jogo (consulte [networking-steam-spacewar.md](../../playbook/networking-steam-spacewar.md)), não `steam_api.dll` dentro de `wic.exe`, que já é um aplicativo Steam.
4. Confirmar que compilações GOG e Steam jogam juntas: código e dados iguais sugerem que sim, mas nenhuma partida LAN original entre elas foi testada.
5. Decodificar o índice de nomes `.sdf` para substituir scripts de missão pelo caminho.
