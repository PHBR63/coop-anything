# <a id="star-wars-jedi-knight-ii-jedi-outcast-2002"></a>Star Wars Jedi Knight II: Jedi Outcast (2002)

| | |
|---|---|
| Motor | id Tech 3 (ramificação para um jogador da Raven), executado pelo [OpenJK](https://github.com/JACoders/OpenJK) em `2ba5021`, Windows x64 (MSVC, Ninja) |
| Versões testadas | Steam (aplicativo 6030), `GameData\version.inf` SinglePlayerVersion 1.03. O `jk2sp.exe` comercial (SHA-256 `5d220aefad2262ec49497b25cabe6a4a28ef87ea5949bb07bd5ae0801197ae42`) não é usado: OpenJK lê apenas os `base\assets*.pk3` comerciais. |
| Projetos | [jedi-outcast-coop](https://github.com/Benehiko/jedi-outcast-coop) (original), [Jedi-Outcast-Coop](https://github.com/masonan777/Jedi-Outcast-Coop) (fork que o continua); ambos em [DIRECTORY.md](../../DIRECTORY.md) |
| Nível de QA | automated (carregamento de fases com participante, todos os 26 mapas da campanha); correções de jogabilidade testadas manualmente em tela dividida para dois jogadores em um PC |
| Última atualização | 2026-10-25 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores conseguem jogar a campanha inteira juntos: um hospeda, o outro entra pela rede ou em uma segunda janela no mesmo PC com controle próprio. Scripts de fase, inimigos, poderes da Força e sabre de luz funcionam para quem entra, e um sistema de reanimação substitui a morte enquanto um parceiro está de pé. Texto dos objetivos para participantes, visões remotas (câmeras de segurança, droides) e AT-ST ainda são exclusivos do host. Dois PCs separados e 3–4 jogadores ainda não foram testados.

## <a id="existing-work"></a>Trabalhos existentes

- **[Benehiko/jedi-outcast-coop](https://github.com/Benehiko/jedi-outcast-coop)** (GPL-2.0, último commit em 2026-07). Base de tudo aqui. 31 patches sobre um commit fixado do OpenJK ampliam o modo de um jogador para 4 clientes, acrescentam transporte UDP, descoberta LAN, comando `coop_host`, página de menu Co-op e cliente remoto de **carregamento duplo**. Uma ferramenta Go (`jk2coop`) aplica os patches, compila, instala e inicia. O README lista objetivos/cenas para participantes (Track F) como em desenvolvimento.
- **[masonan777/Jedi-Outcast-Coop](https://github.com/masonan777/Jedi-Outcast-Coop)** (GPL-2.0, 2026-10). Preserva o histórico original e acrescenta um patch cumulativo, `0032`, além de ferramentas Windows. Este relato cobre esse patch.
- **[JACoop](https://github.com/Parricidium/JACoop)** (Jedi Academy) usa a mesma arquitetura de carregamento duplo e serviu de referência útil por ponto de chamada; seu código não é diretamente portável (o código para um jogador de JA é diferente).

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Código-fonte, sem engenharia reversa.** A Raven publicou o código-fonte do modo de um jogador; OpenJK o compila. Game e cgame ficam na mesma DLL (`jospgamex86_64.dll`).
- **Arquitetura de carregamento duplo (de Benehiko):** o host executa a campanha real. Um participante não tem servidor local; executa cgame sobre entidades *provisórias* preenchidas por capturas de estado da rede. Qualquer campo escrito apenas pelo código do host (dados gentity, estado dos ossos Ghoul2, `renderInfo`) fica zerado ou obsoleto no participante, a menos que algo o transmita pela rede.
- **O que é transmitido** são as tabelas de campos de `code/qcommon/msg.cpp` (`NETF` para entidades, `PSF` para o estado do jogador). Acrescentar um campo ali é a maneira mais econômica de levar dados do host aos participantes.
- **"O jogador" é a entidade 0 em todo lugar.** O código para um jogador usa `s.number == 0`, `!ent->s.number`, `g_entities[0]`, `cg_entities[0]` ou `client == 0` para identificar o jogador. No host isso ignora participantes (tratados como NPCs); no participante, `cg_entities[0]` é o *host*. A maioria dos bugs dos participantes vinha de um desses casos. A correção é verificar `G_IsCoopPlayer(ent)` no host e usar "cliente local = `cg.snap->ps.clientNum`" em cgame.
- **Scripts de fase (ICARUS)** referenciam o jogador como `kyle`. Nomes são resolvidos por `ICARUS_EntList` (vence o último registrado), e um bloco `affect("kyle")` é processado no sequenciador dessa entidade quando o script externo inicia. Participantes se registravam como `kyle` depois do host e só o gerenciador de tarefas da entidade 0 rodava; por isso, eventos de script (portas, surgimento de tropas) nunca eram executados, sem aviso.
- **Chamadas do renderizador ao servidor:** o renderizador chama `SV_PointContents`/`SV_Trace` (volumes de neblina, a cada quadro em Bespin). O participante não tem mundo de servidor, então essas chamadas travavam; precisam recorrer ao mapa de colisão local.
- **Atalhos do modo de um jogador que afetam o jogo inteiro:** Force Speed altera o `timescale` do motor (desacelera o jogo de todos), e a rampa de gama do hardware clareia toda a área de trabalho.

## <a id="what-we-changed"></a>O que alteramos

Tudo no patch `0032`. "Confirmado" significa que o autor conferiu o comportamento em tela dividida para dois jogadores em um PC após a correção; "não confirmado separadamente" significa que foi compilado e houve sessões de jogo, mas ninguém verificou aquele comportamento específico.

| Bug | Causa raiz | Correção | Teste |
|---|---|---|---|
| Eventos de script (Jan abrindo a porta reforçada de kejim_post, surgimento de tropas) nunca rodavam com participante presente | Participantes também registravam o nome de script `kyle`, e o último vencia; só o gerenciador de tarefas da entidade 0 atualizava | Nomes de script das vagas de jogadores sempre resolvem para o host; gerenciadores dos participantes rodam; `g_coopScriptLog` registra cada comando de script | Confirmado |
| Tiros do participante saíam abaixo dos olhos | Ponto de saída da arma armazenado por cgame do host para a visão em terceira pessoa do participante | Participante atira dos olhos mais um deslocamento por arma | Confirmado |
| Inimigos ignoravam ou erravam o participante | Pontos dos olhos de NPC/participante escritos somente quando o host os desenha; dezenas de verificações `s.number == 0` | Servidor atualiza a cada quadro pontos de olhos/cabeça/torso e nível de iluminação do participante; verificações de jogador convertidas | Não confirmado separadamente |
| Animações dos inimigos congelavam ou deslizavam na tela do participante | Controlador de animação diferia de `PM_SetAnimFinal` (animações reversas, mapeamento de ossos, mistura); vagas reutilizadas mantinham corpos antigos | Controlador replica o do host; reutilização de vaga detectada por lacuna no tempo da captura de estado | Confirmado, além de log de animação com 0 problemas |
| Participante desconectava em fases de Bespin ("Cannot use streamed MP3 files here") | Objetos móveis enviavam identificadores de som brutos do host; no processo do participante o mesmo número era outro som (por streaming) | Enviar o *nome* do conjunto de sons, resolver localmente | Confirmado |
| Participante travava em mapas com neblina | Renderizador chamava `SV_PointContents` sem servidor local | Recorrer a `CM_PointContents`/`CM_BoxTrace` | Confirmado; encontrado em dump WER simbolizado com o PDB |
| Participante sem barra da Força, incapaz de escolher ou usar poderes | Campos da Força fora de `PSF`; seleção lida do host; uso verificado só para entidade 0 | Campos enviados pela rede; participante envia a seleção (`coopforce`); host verifica uso para participantes | Confirmado |
| Lâmina do sabre arremessado separava do cabo, aura da Força ausente no participante | cgame procurava o dono do sabre por `s.number`, que é 0 nas entidades provisórias; efeitos da Força liam estado exclusivo do host | Buscar por ponteiro de entidade; bits de efeitos da Força enviados nos bits livres de `entityState.powerups` (ampliado para 32 na transmissão) | Confirmado |
| Force Speed fazia a visão do participante engasgar | `timescale` do host desacelerava o servidor inteiro | Com participantes presentes, Force Speed passa a aumentar a velocidade de movimento | Não confirmado separadamente |
| Explosões de objetos quebráveis, detritos, vidro, mira de torretas, sons de objetos móveis, diálogos e mensagens centrais ausentes no participante | Chamadas diretas para cgame exclusivas do host | Novos eventos/campos os transportam | Mira de torreta confirmada; restante não confirmado separadamente |
| Uma morte encerrava a partida para ambos | Fluxo de morte do modo de um jogador | Reanimação: fica caído em vez de morrer enquanto o parceiro está de pé; segure USE por 3 s para reanimar com 25% de vida; todos caídos = missão fracassada | Confirmado |
| Modo cooperativo acessível apenas pelo console / PowerShell | Página de menu Co-op existia, mas nenhum botão a abria | Motor acrescenta botão CO-OP aos menus padrão principal e de pausa no carregamento (processa `ui/coop_buttons.txt`, depois `Menu_PostParse` para atribuir coordenadas de tela); menu hospeda, entra por lista LAN ou IP ou inicia tela dividida | Confirmado |
| Tela dividida exigia script de inicialização | — | `coop_splitscreen` coloca o host na metade esquerda, aguarda a fase, inicia sozinho o jogo do jogador 2 na metade direita e atribui controles por contagem | Confirmado |

## <a id="qa"></a>QA

- **Bot de varredura de fases** (no código de jogo do host, cvars `coop_crawl*`): para cada mapa, aguarda um participante cujo `commandTime` continue avançando, move ambos para pontos de itens/NPCs/portas em modo invencível, bloqueia saídas, registra `MAP_START/JOINED/TOUR/RESULT` e carrega o mapa seguinte. cgame do participante registra sua visão (`P2 MAP/INGAME/ALIVE`). Vídeos e cenas introdutórias são pulados somente na varredura; cena travada por 20 s reais é encerrada.
- **Inicializador:** `powershell -ExecutionPolicy Bypass -File tools\windows\jk2coop-levelcrawl.ps1 [-Maps a,b] [-Dwell 30] [-Mute]`. Pastas de usuário novas por execução, reinício de jogos que travam, monitores de congelamento, relato de novos dumps, saída `RESULT: PASS/FAIL`. `-SelfTest` fornece logs defeituosos conhecidos ao avaliador (precisa dar FAIL); `-TwinKillJoiner` encerra o participante durante o mapa e precisa relatar FAIL ("PASS (twin caught)").
- **Última execução completa (2026-10-25):** `RESULT: PASS (26/26 maps)`, um processo host e um participante durante a campanha inteira, sem travamentos, desconexões, reinícios ou novos dumps. Três cenas introdutórias (artus_topside, valley, bespin_undercity) foram encerradas pelo mecanismo de desbloqueio de cenas; `pit` passou sem encontrar pontos de visita, comprovando apenas carregamento.
- **Sem automação:** sincronização da jogabilidade (Força, sabre, reanimação) verificada manualmente em tela dividida. Dois PCs e 3–4 jogadores: não testados.

## <a id="how-to-play"></a>Como jogar

- Compile do código-fonte (ferramenta `jk2coop` do repositório ou CMake do OpenJK com patches aplicados). O fork também tem `tools/windows/jk2coop-package.ps1`, que empacota uma compilação com instalador (`Install.cmd`) capaz de localizar a instalação própria do jogador (pastas das bibliotecas Steam, GOG, disco) e criar um atalho na área de trabalho; dados do jogo são lidos no lugar por `fs_cdpath`, nunca copiados.
- No jogo: menu principal > **CO-OP** > HOST NEW GAME / entrar pela lista LAN ou por IP (UDP 29070) / START SPLIT SCREEN.

## <a id="known-issues"></a>Problemas conhecidos

- Participantes não recebem a tela de objetivos nem texto de missão (Track F); visões remotas (câmeras de segurança, controle de droides) e AT-ST são exclusivos do host.
- Participantes ficam congelados durante cenas.
- Itens largados flutuam um pouco na tela do participante.
- Ainda não testado em dois PCs separados ou com mais de 2 jogadores.

## <a id="next-steps"></a>Próximos passos

- Teste de rede em dois PCs, depois varredura com 3 jogadores.
- Track F: objetivos e texto de missão para participantes.
- Descobrir se as três cenas introdutórias também travam no jogo cooperativo normal ou apenas sob avanço rápido da varredura.
- Convites Steam (sala + retransmissão) ao lado de IP direto; consulte [networking-steam-spacewar.md](../../playbook/networking-steam-spacewar.md).
- `wp_saber.cpp` ainda tem cerca de 60 verificações `s.number`; JACoop converteu as equivalentes de JA.
