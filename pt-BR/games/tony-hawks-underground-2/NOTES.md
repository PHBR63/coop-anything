# <a id="tony-hawks-underground-2-pc-story-co-op-notes"></a>Tony Hawk's Underground 2 (PC): notas de campanha cooperativa

Objetivo: jogar juntos a campanha do modo Story on-line (dois jogadores, internet).
Etapas concluídas: 0-7 (2026-10-24 a 2026-10-26). Mod: https://github.com/LeftGamer1/thug2-coop; relato em [README.md](README.md). As primeiras seções abaixo foram mantidas como escritas na época.

## <a id="game-identity-phase-0"></a>Identidade do jogo (etapa 0)

| | |
|---|---|
| Jogo | Tony Hawk's Underground 2, PC, 2004, Neversoft / port Beenox, inglês |
| Loja | Desconhecida (instalação em disco, executável sem CD; não há versão Steam/GOG). |
| Motor | Motor Neversoft (linhagem THPS4/THUG), scripts de bytecode QB (QScript), arquivos `.prx` |
| Sistema operacional | Windows (Windows) |
| `Game\THUG2.exe` | 2.695.168 bytes, SHA-256 `52fc88849654b34839ec2f96bff3a8c0b7a855df9a207aab9f2fca2e6bd440f3`, CRC32 `88af0474`, timestamp PE 1095202195 (2004-09-14) |
| `Game\THEMOD 1.3.exe` | Mesmo tamanho e organização de seções, 123 bytes diferem de THUG2.exe; SHA-256 `2b1ac8a9282c7817d6999967d0d47bfabaf8b29ac220bbff9f634e107f1095c3`. Não é o original de THEMOD: veja "Instalador de THEMOD" no fim. |
| `THEMOD 1.3.exe` (raiz da instalação) | 2.224.553 bytes, SHA-256 `d3de1fa1a51fdd6b9487321f7e0a7ea99992692e4e738cbc0b875604188fa292`; instalador NSIS de THEMOD (listado com 7-Zip em 2026-10-26, não executado). |
| Scripts | Distribuídos como `.qb` compilados avulsos em `Data\scripts` (223 arquivos, datas de 2004), além de `*_scripts.prx` por fase em `Data\pre`. |

### <a id="observations"></a>Observações

- Ambos os executáveis não estão empacotados (`.text/.rdata/.data/.tls/.rsrc` normais, sem seções SafeDisc). Fonte: análise do cabeçalho PE.
- Nenhum é uma compilação aceita pelo patcher PartyMod: ele exige CRC32 `a8142d3a` (https://github.com/PARTYMANX/partymod-thug2/blob/84908a7/patcher/main.c#L18).
- Nenhum SHA-256 está na lista de executáveis conhecidos de thug2-decomp (https://github.com/CanuckAussieKev/thug2-decomp/blob/07bd387/tools/game/install_manifest.ts#L28).
- O jogo inclui modos on-line (GameSpy, hoje encerrado). Modos de rede em `gamemodes/gamemode.qb` incluem `mode_netgoalattack` ("Goal Attack").
- `game/goalattack.qb` tem eventos conscientes de equipe `goal_attack_completed_goal_other_same_team`, `goal_attack_started_goal_other_same_team`, textos "%n Completed %t! %i to go!", "Complete all selected goals" e opções de conjunto de objetivos `classic_only` / `created_only` (menu de rede: "Classic Goals"). Fonte: varredura própria de nomes/strings QB (`local/tools/qbnames.py`, somente leitura).

### <a id="derived"></a>Deduções

- THUG2 já tem modo on-line em que vários jogadores cumprem objetivos de fase na mesma sessão com equipes. Limita-se a objetivos Classic e criados; objetivos Story não são oferecidos.
- Caminho pela tabela de triagem: "motor com MP e scripts-fonte" -> tornar a lógica Story compatível com rede, principalmente em QB, com DLL nativa para o que QB não alcança.

### <a id="guesses-unverified"></a>Hipóteses (não verificadas)

- Goal Attack por equipe talvez já atribua um objetivo à equipe inteira (sugerido pelos eventos "other_same_team").
- As mudanças do executável THEMOD são pequenas (URL de MOTD e alguns bytes); o conteúdo real provavelmente fica em `Data` (scripts/pre).
- O executável sem CD do testador talvez tenha a mesma organização de THUG2PM.exe (como o repack de 2024), permitindo executar a DLL de thug2-decomp.

### <a id="unknown"></a>Desconhecidos

- O que THEMOD 1.3 altera em Data (sem lista de arquivos; código-fonte não encontrado).
- Se salas OpenSpy funcionam com este executável (o original aponta para hosts GameSpy).
- Como a progressão Story (cenas, fases desbloqueadas, indicadores de capítulos, salvamentos) é controlada; código nativo de Goals & career está cerca de 1% descompilado em thug2-decomp.

## <a id="prior-work-phase-1"></a>Trabalhos anteriores (etapa 1)

Buscas em 2026-10-24: web ("THUG2 story mode co-op mod online", "THUG Pro story mode multiplayer goals co-op", "Tony Hawk Underground 2 story mode multiplayer mod ... career online", russo "тони хоук андеграунд 2 кооператив сюжет мод", "THUG2 THEMOD 1.3 thmods"), repositórios GitHub (thug2, thug2 qb, neversoft qb, qb thps, partymod, thug2 coop, thug2 multiplayer story), issues/PRs deste repositório (thug, tony hawk, neversoft: 0 resultados).

**Nenhum projeto de campanha cooperativa encontrado** nessas buscas. Ainda não consultados: fórum THPSX, Discords THUG Pro / PartyMod, páginas de arquivos ModDB, archive.org.

| Projeto | Link | Licença | Última atividade | O que oferece |
|---|---|---|---|---|
| thug2-decomp (CanuckAussieKev) | https://github.com/CanuckAussieKev/thug2-decomp | Nenhuma declarada (sem LICENSE). | Commit 07bd387, 2026-10-24. | Reimplementação C++ como hook `dinput8.dll`, 73,2% do código por tamanho. Biblioteca de rede 100%, modos on-line 99%, runtime de scripts 100%, Goals & career 1%. Canal de automação (`run_game.ps1 -Commands`, `[features] automation=1`), opções de inicialização por fase, hosts OpenSpy. Exige THUG2PM.exe ou executável sem CD conhecido. Precisa de VS 2026, Node 24, Ghidra 12.1.4. |
| PARTYMOD para THUG2 (PARTYMANX) | https://github.com/PARTYMANX/partymod-thug2 | MIT | Commit 84908a7, 2026-06-06. | Correções, entrada SDL2, OpenSpy on-line. Patcher aceita um executável (CRC32 a8142d3a). |
| THUG Pro (Morten1337, Quazz, Gone) | https://en.wikipedia.org/wiki/THUG_Pro | Fechada. | Última versão em outubro de 2023 (Wikipedia). | Conversão total on-line sobre THUG2; sem campanha, portanto sem história cooperativa. |
| NeverScript (byxor) | https://github.com/byxor/NeverScript | Não conferida. | 2023-05-01 | Compilador/descompilador QB (Go). Cópia mais nova em thug2-decomp/tools/neverscript. |
| QBReader (kennythps) | https://github.com/kennythps/QBReader | Não conferida. | 2015-11-06 | QB para texto. |
| thug-pro-disassembly (byxor) | https://github.com/byxor/thug-pro-disassembly | Não conferida. | 2020-06-02 | Desmontagem anotada de THUG Pro. |
| qcc (donnaken15) | https://github.com/donnaken15/qcc | Não conferida. | 2026-01-05 | Compilador QB em desenvolvimento. |

Jogo oficial: a "equipe" do modo Story (seu skatista e parceiro profissional) é troca de personagem para um jogador, não modo cooperativo (redação da página ModDB; não é mod).

## <a id="next-phase-2-3-proposal"></a>Próximo passo (proposta de etapas 2-3)

1. Descompilar todos os QB (precisa compilar um descompilador: NeverScript em Docker; compilação pelo agente bloqueada aguardando autorização).
2. Comparar Data de THEMOD com dados originais para descobrir alterações (precisa de referência original).
3. Conferir se o executável do testador corresponde à organização de THUG2PM.exe (BPS do PartyMod com entrada compatível ou comparação de bytes em endereços conhecidos de thug2-decomp).
4. Mapear progressão Story em QB: `gameflow.qb`, `goal_utilities.qb`, `cutscene.qb`, `*_scripts.prx` de fase.
5. Protótipo: desbloquear objetivos Story em Goal Attack de rede (equipe), dois clientes em um PC por loopback.

## <a id="phase-2-3-2026-10-24-scripts-and-the-goal-filter"></a>Etapas 2-3 (2026-10-24): scripts e filtro de objetivos

Ferramentas (todas somente de leitura sobre a instalação): NeverScript (cópia de thug2-decomp, fork violetvandal em 73fe0f9) compilado em Docker `golang:1.22.5`; auxiliares Python próprios em `local/tools` (extrator PRE v3 com decodificador LZSS de `src/game/file/pre.cpp` de thug2-decomp, varredura da tabela de nomes QB, preenchimento checksum->nome, busca no executável com capstone 5.0.3).

### <a id="observations-1"></a>Observações

- Executável original carrega `scripts\qdir.txt` de `qb_scripts.pre`; THEMOD carrega `thethug2mod.pre` (string do executável). `Data\pre\thethug2mod.prx` (2007-08-09, 862.422 bytes) contém 209 `.qb` + `qdir.txt`: substituição completa de `qb_scripts.prx`. Os `Data\scripts\*.qb` avulsos são originais de 2004.
- `.qb` de THEMOD tiveram tabelas checksum-nome removidas; NeverScript descompila 206 de 209 com `-lenient` (falham: `game.qb`, `menu/themod.qb`, `skater/walltricks.qb`). Permanecem 104 checksums sem resolução após preencher nomes de scripts originais e strings do executável. Nota: NeverScript exibe `#xxxxxxxx` na ordem de bytes do arquivo (little-endian invertido).
- Mudanças de scripts THEMOD (linhas diferentes, sem distinguir maiúsculas): CAS (`cas_skater_*`, `cas_logos`, `decks`), `player_controlled_vehicle`, `skater/physics`, `bails`, menus, `chapter_info`, `Levels`, `cutscene` (27), `gamemode` (37). `goalattack.qb` só difere por um printf restaurado. Scripts de objetivos e rede são próximos dos originais.
- Objetivos Story são filtrados no script de cada fase, por exemplo `levels/BO/BO_scripts.qb`, `script BO_Goals`: `if ((GameModeEquals is_classic) or (InNetGame))` -> objetivos Classic; senão `if ! InNetGame` -> objetivos Story (`BO_AddGoal_FindJesse`, ...).
- `GoalManager_AddGoalChoices` (THEMOD 0x0055D590) lê indicadores `selected_only`/`classic_only`/`created_only` e chama 0x0055C2F0, que para cada objetivo pula os com parâmetro `net` (0x00554540) e, com `classic_only`, pula os com `edited_goal` (0x00554300); `created_only` mantém só `edited_goal`; `selected_only` mantém os com bit 4 do byte +0x6C. Nenhuma verificação de `classic_mode_goal`.
- Executável tem entrada por IP direto (`TryJoinServerIP`, `join_ip`, `join_private_ip`). `CreateMutexA` é importado; thug2-decomp usa como mutex de quadro, e sua documentação descreve testes de rede com segunda instância.

### <a id="derived-1"></a>Deduções

- "Classic Goals" em Goal Attack de rede significa "todo objetivo não criado acrescentado pela fase". Se o script adicionar objetivos Story numa partida em rede, Goal Attack deve oferecê-los sem alterar o executável.
- Primeiro protótipo só em QB: alterar a condição `InNetGame` de `<LV>_Goals` em cada fase (distribuído como `<LV>_scripts.prx` reempacotado) e manter `thethug2mod.prx` do THEMOD.
- Internet sem GameSpy: host + entrada por IP direto (redirecionamento de porta ou LAN virtual como ZeroTier/Radmin).

### <a id="unknown-needs-a-game-run"></a>Desconhecidos (exigem executar o jogo)

- Se objetivos Story funcionam em rede: pedestres, cenas, diálogos de início, trocas para profissional, temporizadores.
- Se Goal Attack em equipe credita objetivo para todos.
- Progressão Story (capítulos, fases, salvar) fora do modo carreira: indisponível em rede; exigiria atualizar salvamento da carreira no host.
- Se duas instâncias funcionam em um PC com este executável.

## <a id="phase-5-prototype-run-1-2026-10-24"></a>Etapa 5, execução 1 do protótipo (2026-10-24)

Executável de teste `Game\THUG2_coop_test.exe` = THEMOD + 4 patches (offset de arquivo == VA - 0x400000 em .text):
- 0x004D8720: `89 1D` -> `89 05` (parâmetro D3D de apresentação Windowed = 1; mesmo byte escrito por PartyMod).
- 0x005F58D3: `jne` (6 bytes) -> NOPs (criação da janela segue o caminho com bordas, não o de tela cheia WS_POPUP|WS_EX_TOPMOST).
- 0x004E270B: `je` -> `jmp` (pula verificação FindWindowExA de "THUG2" já em execução).
- 0x004E1705: tratador WM_ACTIVATE -> `mov byte [0x7CCBE4],1; xor eax,eax; ret 10h` (permanece ativo, nunca minimiza).

Mod: `Data\pre\BO_scripts.prx` reempacotado com `levels\BO\BO_scripts.qb` alterado para `BO_Goals` acrescentar objetivos Story (não Classic) sempre que `InNetGame`.

Controle: `local/tools/gamectl.ps1` (SendInput/keybd_event, captura de janela) + `scenario_goalattack.sh`. Linha de comando: host `-HOST -NAME P1 -HOSTNAME coop`, cliente `-CONNECT 127.0.0.1 -NAME P2` (analisada em 0x004E1220; ambos iniciam direto na seleção de skatista; host depois recebe HOST OPTIONS com Level: Boston).

### <a id="observations-this-run"></a>Observações (desta execução)
- Duas instâncias rodaram lado a lado em janela (cliente 640x480), a 60 fps; cliente entrou no host por loopback.
- Pausa do host > START GAME > Game Type: Goal Attack > Choose Goals listou objetivos Story de Boston: Find the Special Guest, Find Ben Franklin, Mark Your Territory, Hospital Duty, Arcade Machine High Score, Dance Sucka, Decapitate the Statues, Combo on the RV Ramp, Combo the 4 Benches, Ye Olde Cannon Grind, ... (captura `r2_choose_goals.png`, local).
- Com primeiro patch (Story só quando `GameModeEquals is_goal_attack`), a lista mostrou objetivos Classic: objetivos são adicionados uma vez ao carregar a fase, que ocorre no modo de sala de rede.
- Goal Attack iniciou para ambos (temporizador visível, ambos na lista).
- Ainda não testados: iniciar ou concluir objetivo Story em rede, crédito por equipe, pedestres, cenas.

## <a id="pivot-story-mode-co-op-dll-2026-10-24"></a>Mudança de direção: DLL de modo Story cooperativo (2026-10-24)

Objetivo: modo Story real para ambos (missões de NPCs, cenas). Abordagem: proxy `dinput8.dll` próprio (repositório `thug2-coop`, MinGW i686 em Docker) + `scripts\coop\coop.qb` acrescentado a `thethug2mod.prx` do THEMOD (qdir.txt).

### <a id="observations-runs-on-one-pc-two-windowed-themod-instances"></a>Observações (um PC, duas instâncias THEMOD em janela)
- Modo de um jogador já é servidor + cliente locais (`setservermode on; StartServer; JoinServer`). `SetNetworkMode LAN_MODE` antes de StartServer torna o servidor não local (GameNet::Manager::InNetGame 0x0044E4F0 verdadeiro).
- `InNetGame` (0x005A0D80) / `InMultiplayerGame` (0x005A11B0), visíveis em scripts, são rotinas intermediárias de 2 instruções; recebem hooks para retornar false no cooperativo, fazendo scripts de fase seguirem caminhos de um jogador.
- Condições de conteúdo nativo também precisam disso: PreloadPedestrians (chamada 0x005AB321), Skate::SkipNode (chamada 0x00565BC8).
- Entrada em partida em andamento: GameInProgress de OkToJoin (chamada 0x0052F672) e de HandleJoinRequest (0x0052FB4B; caso contrário, participante fica como observador pendente: "espectador com câmera estranha") respondem "netlobby" no host cooperativo.
- Carreira tem max_players=1: sem heap de segundo skatista -> host trava em Calloc ao criar o skatista cliente. Corrigido com `cleanup preserve_skaters; chosen_leave_server; FlushDeadObjects; InitSkaterHeaps` (ordem de início de dois jogadores; cleanup após LeaveServer trava em CSkater::SetUpNetwork), opção players=2 no host (0x0067EFD0) e omissão de DeleteExtraSkaterHeaps no cleanup da fase (chamada 0x005A0017) em modo cooperativo.
- Skatista de rede não tem componente StatsManager: Script::CallMemberFunction 0x00472980 travava em componente nulo (proteção em 0x004729BA).
- Cliente executava a própria história (cenas introdutórias) até receber o estado do host: CSkaterCareer (módulo skate +0x20), WriteToStructure 0x00585550 / ReadFromStructure 0x00584D00, mais CSkater::WriteChapterInfo 0x005801B0 / ReadChapterInfo 0x00580210 (CHAPTER_STATUS / _INTROS_VIEWED / _OUTTROS_VIEWED), 3.398 bytes por Script::WriteToBuffer. Com isso, cliente inicia capítulo 1 sem introdução, move o próprio skatista e ganha pontos de atributos.
- Canal lateral: conexão TCP própria em porta+1 (5154). Vitórias de objetivos replicadas por trampolim em CGoalManager::WinGoal 0x00558030; PlayCutscene do host (cfunc 0x005AE010) replicado ao cliente. Ainda não testado no jogo.
- Réplica de objetivo verificada: host F9 (depuração) venceu TR_Goal_Gaps27 -> cliente recebeu "goal D0E4352B won by peer"; ambos mostraram diálogo de Tony para avançar capítulo. Host "Yes" -> envia carreira novamente em LaunchLevel (cfunc 0x005654B0, tabela 0x0067FD90) -> ambos carregaram Boston como capítulo 2 (host: câmeras de introdução dos objetivos; cliente: Select Pro Teammate).
- Uma execução anterior idêntica travou ambos ao carregar BO (host na tela de erro de disco após File::Open falhar; cliente depois num som de salto). Não reproduzido na seguinte. Causa desconhecida; LoadPre agora tem log.

## <a id="lobby-2026-10-24"></a>Sala (2026-10-24)
- Host F10 no menu principal: papel host, conexão escutando, servidor reiniciado como LAN (cleanup/leave/heaps/StartServer/JoinServer, depois change_level Load_MainMenu). cfunc de script SetNetworkMode (0x005A0A00, tabela 0x00680150) mantém LAN no cooperativo (início Story / chosen_leave_server definem 0).
- Cliente F11: conexão + hello -> carreira; espera. Host Story > Continue -> hook LaunchLevel (level=<checksum>, não Load_MainMenu 0xE92ECAFE) envia carreira + "join now" -> cliente entra enquanto a fase do host carrega; ambos executam capítulo 1 e cenas introdutórias TR_1A.. em sincronia (capturas iguais quadro a quadro).
- Travamentos corrigidos: entrar no menu principal do host (Allocate nulo) -> entrar só numa fase; réplica de cena + cena local simultâneas (DeleteHeap) -> réplica desligada por padrão ([coop] mirror_cutscenes); objetos substitutos ausentes no cliente (FindObject nulo em CCutsceneData::UpdateStandIn 0x00465AFF / DestroyObjects 0x00463CBD) -> protegidos; "lost connection to the host" durante cenas (tempos de silêncio de ConnectionTask 0x0053EB70) -> omitidos enquanto conexão cooperativa está ativa.
- Fim/pulo de cena replicado: hook na chamada EndMovies(false) 0x0057AF21 de CMovieManager::Update; nome em execução enviado (GetPlayingName 0x0057B030, gerenciador no módulo skate +0x368); parceiro encerra só se estiver na mesma cena. Host Esc -> cliente "cutscene F5012F52 ended by peer" x3, ambos chegaram à jogabilidade.
- Trocas de convidado/profissional: SwapObjectModels (tabela 0x00681950, cfunc 0x005B34A0) replicado como (ID skatista local, outro ID). Ainda não verificado com pedestre realmente trocável; teste de depuração com TRG_EricSkate_01 travou em 0x0048E4D4 (pedestre arbitrário, não alvo de troca).
- Verificação de NPCs (TR, capítulo 1, após introdução): um jogador tem TRG_EricSkate_01, TRG_BamSkate_01, TRG_G_COUNTER_PRO; host cooperativo tem Tony_Advance, Eric, Bam; cliente Eric, Bam. Pedestres são criados; os da história aparecem e somem conforme estado/tempo dos objetivos.
- Automação saiu da entrada do sistema operacional: [debug] automation=1 envolve DirectInput (CreateDevice -> teclado GetDeviceState/GetDeviceData) e lê coop_cmd_<pid>.txt ("key", "wait", "spawn"); capturas por PrintWindow.
- Salvar/carregar história no cliente (SaveToMemoryCard 0x005A97E0 / LoadFromMemoryCard 0x005A8730, type=OptionsAndPros) recusados em modo cooperativo.
- F12 teletransporta ao amigo: posições sincronizadas pela partida de rede (objetos 0/1 m_pos +0x4C correspondem dos dois lados). Obj_SetPosition por script voltava a um ponto de reinício; feito nativamente como CSkater::MoveToNode (m_pos, m_oldPos, física central +0x280 -> +0x98, SetTeleported 0x0045E4C0). Verificado: ambos lado a lado nas duas telas.
- Nome do amigo: nome flutuante do jogo (texto pos3D) vai ao topo da tela em carreira. Substituído no cooperativo: rótulo próprio removido; amigo desenhado por coop_friend_label numa posição 2D projetada com Gfx::Camera de skatercam0 (pos +0x5C, linhas de matriz right/up/back +0x6C, hfov +0xB0 graus em 4:3, focal 320/tan(hfov/2)), limitado à borda, texto "<name>  <m>m", rgba [90 170 255 100].
- "key up" injetado não movia skatista (menus/Esc funcionam): controles leem entrada por outro caminho; desconhecido.
- Bot: comando de automação "goto <object|friend> [radius]" direciona com W/A/D (frente do skatista = linha 2 da matriz em +0xC0+32); alcançou host a 2.413 unidades em 9 s. Controles: WASD move, numérico para manobras (ollie kp2, grind kp8, kickflip kp4); Esc pula cenas, kp2 pula cenas de objetivos; diálogos (Tony sim/não) usam setas + Enter.
- Aberto (2026-10-24, pausado): pontos de objetivos em Boston diferiram uma vez (host 0/1000, cliente 825/1000); pontos = soma das recompensas dos objetivos vencidos (GoalManager_GetActiveRewardPoints 0x0055B7C0) + total_cheat_points. Ainda não reproduzido. Pedido: câmeras de introdução/vitória dos objetivos também no cliente.

## <a id="night-run-2026-10-25-boston"></a>Execução noturna de 2026-10-25 (Boston)
- Duas instâncias carregando os mesmos arquivos: uma caiu na tela de erro de disco (File::Open, abertura exclusiva). Só em teste: importação CreateFileA (0x006450D0) envolvida para acrescentar FILE_SHARE_READ quando multi_instance=1.
- Companheiro profissional: create_select_pro_menu do cliente espera; escolha do host (select_pro_menu_choose) enviada com parâmetros; cliente a executa (scripts criados para o parceiro rastreados por ID único CScript +0xB0, impedindo ecos dos hooks).
- Visão do host pelo cliente ficou NaN após mudança de fase: skatista do host manteve COMPOSITE_FLAG_PAUSED (+0x104 bit 0) no cliente após introdução do capítulo, impedindo retomada da reprodução não local. DLL limpa o indicador no skatista amigo sempre que nenhum filme roda; reprodução também reiniciada após cada LaunchLevel.
- "skatista 0" dos comandos de script (Skate::GetSkater 0x005665C0 chamado de 0x0059F610-0x005B6560) = skatista local no cooperativo (câmeras do objetivo do cliente: PlaySkaterCamAnim em skatista não local não fazia nada).
- Câmeras de objetivo: PlaySkaterCamAnim replicado (skaterId removido), enviado quando começa no remetente (uma visita enfileira tudo de uma vez); KillSkaterCamAnim / fim de EndMovies replicados por nome; fim remoto executa KillSkaterCamAnim Current (restaura câmera). Cliente pula a própria visita aos objetivos do capítulo (PlayIntroCameras from_chapter_intro: setup, KillChapterMenu, cleanup, callback) e mostra a do host.
- beat_first_stat_goal pausava o jogo do cliente e seu diálogo era fechado por KillChapterMenu -> pausa permanente. No cooperativo, a mensagem vira painel, sem pausa.
- Troca por profissional verificada: cliente swap_skaters com TRG_Ped_TeammatePro -> host "swap from peer ... done"; host vê cliente como profissional.
- Código nativo de objetivos/carreira verifica GameNet InNetGame em 19 pontos (gerenciador 0x00551AE0-0x00560D5C, CSkater::GetStat 0x005804E5): numa partida de rede, objetivos vencidos não eram guardados na carreira (perdidos ao recarregar). Redirecionados à verificação consciente do cooperativo. Parâmetros do gerenciador (+0x14 via 0x004A2BA0, GoalManager 0x005591B0; guardados como GoalManagerParams num salvamento Story) agora enviados com a carreira, permitindo a um amigo que retorna receber os objetivos vencidos.
- Reentrada em fase abandonada pelo amigo: restos do skatista antigo travavam o novo (controlador de animação) -> host recarrega a fase, e amigo entra enquanto carrega.
- Troca de modelo replicada no skatista do amigo na cópia do host precisa ser desfeita antes de ele morrer ou mudar de fase (modelo de pedestre em skatista que sobrevive às fases): desfeita em change_level (wrapper coop.qb -> CoopBeforeLevelChange), Cleanup (0x0067F5C8) e perda de conexão; mantida fora da tabela de trocas do jogo (0x007CEDE0).
- Cliente que perde o host em Barcelona travava ~20 s depois em TRG_BA_Ped_Skater02/03 (animação) durante o tratamento nativo de desconexão (desmontagem dos objetivos no meio da fase). Agora sai imediatamente: PauseObjects, quit_network_game, UnpauseObjects e mensagem (coop_client_host_gone). No host, o skatista desconectado é ocultado + pausado e removido no Cleanup da fase (desvio de Skate::RemoveSkater 0x00565790), exceto enquanto esse jogo sai do servidor (hook LeaveServer 0x005A08D0).
- Host saindo ao menu principal envia kHostLeft; amigo também sai. Saída do amigo (pausa > Quit) permitida pelo wrapper level_select_change_level (Load_MainMenu).
- Diálogo de tutorial de atributo no cliente (beat_first_stat_goal) pausava o jogo -> mensagem de painel no cooperativo.
- Demonstração (local/tools/demo.sh, 17 etapas, TR -> Boston -> Barcelona, trocas, objetivos nos dois sentidos, reentrada, perda de host): passa sem travamentos (2026-10-25 09:11). Regressão de um jogador até Barcelona: OK.

## <a id="shipping-2026-10-25--26"></a>Distribuição (2026-10-25 / 26)

### <a id="themods-installer"></a>Instalador de THEMOD
- 7-Zip lista como NSIS 2.46 com `Game/THEMOD 1.3.exe` (2008-11-08, SHA-256 `25874001be0c1f12df47bc8f0dad61869cae0fe90964c12245165732a4cbb5ea`), `Game/data/pre/thethug2mod.prx` (2007-08-09, mesmo SHA-256 do instalado) e plugins NSIS (`HostsManager.dll`, `NSISFilePatch.dll`, ...).
- Executável do instalador contra `THUG2.exe`: 122 bytes em 7 intervalos. 0x1A8A01 `75 9C` -> `90 90` (jnz de checksum do salvamento, mesmo patch PartyMod), 0x1F95BB `75` -> `EB` (SDK GameSpy CD-key, perto de gcd_init 0x005F9540), URLs MOTD -> thmods.com, `ReportStats` -> `RaportStats`, `qb_scripts.pre` -> `thethug2mod.pre`, peerchat -> peerchat1.thmods.com, agente HTTP `GameSpyHTTP/1.0` -> `THEMOD13`.
- Executável THEMOD instalado do testador = instalador + 3 alterações de terceiro desconhecido: 0x0048C170 (CFunc_SetScreenBlur) -> `mov al,1; ret` (desfoque desligado), imediatos do modo 800x600 (0x4D876E / 0x4D878A) -> 1920x1080, host peerchat de volta a `peerchat.gamespy.com`.
- thmods.com não responde (2026-10-26). Único vestígio encontrado: postagem de blog de 2008 listando THEMOD 1.0-1.3 com crédito a "TH Mods" (https://dks-site.blogspot.com/2008/12/tony-hawk-underground-2-mod.html).
- Instalador contém uma cópia completa do executável do jogo; por isso o mod distribui patcher de bytes (`patcher/patch_themod.ps1`): confere tamanho + SHA-256 + cada byte original, escreve `THEMOD 1.3.exe`, nunca sobrescreve. Sua tabela aplicada em Python ao `THUG2.exe` do testador produz o executável do instalador (SHA-256 igual). Ainda não executado no Windows.

### <a id="features-added"></a>Recursos adicionados
- Objetivos compartilhados: wrapper `goal_accept_trigger` -> `CoopSharedGoal mode=start` -> parceiro inicia (`coop_remote_start_goal`); trampolim `WinGoal` segura quem termina primeiro (`coop_goal_done_wait`) até `kGoalDone` do parceiro; objetivos por etapas (treino) compartilhados por `coop_goal_won_chain`.
- Colisão entre jogadores: desvio de `GameNet::Manager::PlayerCollisionEnabled` 0x00534340 (6 bytes `56 8B F1 8A 46 3A`); `[coop] player_collision=` 1 / 0 / vazio (opção de rede do jogo).
- Conversa: desvio de `Sio::KeyInput` 0x005BDE70 (7 bytes `A0 6E E4 7C 00 84 C0`); bytes CP1251 de layout cirílico são transliterados (fontes não têm cirílico). Jogo recebe no máximo 15 caracteres por quadro.
- Teclas: `[keys] host/join/teleport` (F1-F24, letras, dígitos, NumN, Insert..., Ctrl+/Shift+/Alt+).
- Mensagem da sala no host era apagada ao recarregar o menu: exibida por `coop_lobby_open_message` após `is_changing_levels = 0` mais 20 quadros.
- Resolução: configuração de dispositivo 0x004D870B escolhe um de 4 modos pela configuração de Launcher.exe (`mov esi,3; sub esi,edx`); `[display] resolution=WxH` substitui `sub` por NOP (sempre última vaga) e escreve W/H nos imediatos de 640x480 (0x4D8776, 0x4D8792). Janela: argumentos de tamanho empilhados por WinMain (0x4E274C, `push 480; push 640; push 100; push 100`) -> resolução, centralizada (x/y -1), escalada para caber na área útil; `SetWindowPos(0,0,w,h)` após dispositivo (0x4D8891, 14 bytes) substituído por NOP em janela (PartyMod faz igual). Testado em 2026-10-26: janela 1280x720 (cliente 1280x720, centralizada), janela 1920x1080 em tela 1080p (1797x1011), tela cheia 1920x1080, `launcher`.
- Travamento na abertura relatado num PC Windows 11 de amigo em 2K: segundo testador também ocorre com THEMOD 1.3 puro; executar em janela evita. Não reproduzido aqui.
