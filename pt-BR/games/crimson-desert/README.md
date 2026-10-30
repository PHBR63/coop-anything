# <a id="crimson-desert-2026"></a>Crimson Desert (2026)

| | |
|---|---|
| Motor | BlackSpace Engine (Pearl Abyss, interno) |
| Versões testadas | Compilação Steam 25477059, `CrimsonDesert.exe` 1.0.0.2976 (versão do jogo 2.03.02), timestamp PE `0x6AB28F00`, SHA-256 `57da440d72f4db974f25fef047cf84c4dadd999a88cb2a3c5af4c9bd67fde1e7`; Linux, Proton Experimental |
| Projetos | [cdmp (ByJunter)](https://github.com/ByJunter/CrimsonDesertMultiplayer), [CrimsonDesertCoop (blizz3010)](https://github.com/blizz3010/CrimsonDesertCoop), mod não lançado de No-Context2224; consulte as três linhas Crimson Desert em [DIRECTORY.md](../../DIRECTORY.md) |
| Nível de QA | none (somente testes em um PC) |
| Última atualização | 2026-10-21 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores conseguem se ver e lutar contra inimigos próximos do host com o alpha cdmp de ByJunter, mas a história não é compartilhada: cada um permanece em seu salvamento. Esta pasta documenta a retomada de cdmp voltada ao progresso compartilhado de missões (indicação de trabalho: [cranebeaker/coop-anything#51](https://github.com/cranebeaker/coop-anything/issues/51)). Até agora:
- cdmp compila no Linux e roda sob Proton;
- mensagens de missões/etapas estão mapeadas;
- **compartilhamento experimental de missões** (protocolo 11): ramificações de etapas e aceitações de missões do host são repetidas no servidor próprio do convidado. Testado somente em um PC:
  - uma solicitação secundária ("Renee's Request"), aceita só por repetição, com a cena de encontro repetida antes para tornar o NPC conhecido, foi depois preparada e entregue por um jogador humano: o servidor a concluiu e concedeu a recompensa;
  - compartilhamento de aceitação ao vivo pelo retransmissor cdmp: cena de encontro e aceitação aplicadas e verificadas;
  - ainda não experimentado entre dois PCs;
- a cópia do outro jogador não salta mais ao caminhar (redução de frequência de Move).

## <a id="existing-work"></a>Trabalhos existentes

- **cdmp** de ByJunter, [GitHub](https://github.com/ByJunter/CrimsonDesertMultiplayer) e [Nexus](https://www.nexusmods.com/crimsondesert/mods/3677). Mod ASI C++20, GPL-3.0, v0.2.0 (2026-10-11), autor não o mantém mais. Somente compilação 1.0.0.2976. Sincroniza movimento, equipamento, cavalo, corda, horário do dia, marcador de mapa e inimigos hostis próximos do host. Somente amigos Steam. Notas de pesquisa (espanhol, índice em inglês) em `docs/research/`. Fork de retomada: [CaptCapybara-cmd/CrimsonDesertMultiplayer](https://github.com/CaptCapybara-cmd/CrimsonDesertMultiplayer).
- **CrimsonDesertCoop** de blizz3010, [GitHub](https://github.com/blizz3010/CrimsonDesertCoop), 0.2.3, último push em 2026-07-08, sem licença. Jogador 2 assume um companheiro. O README diz que sincronização de missões e cenas não é aplicada.
- **No-Context2224**: não lançado, conhecido apenas pela imprensa ([Wccftech](https://wccftech.com/crimson-desert-2-player-co-op-mod-but-more-advanced-soon/)).
- Pearl Abyss comentou sobre modo multiplayer oficial; nenhuma data encontrada.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- O jogo de um jogador mantém a separação MMO de sua origem: o cliente fala com servidor interno ao processo por 1.114 mensagens "Troc" (`u16 opcode | u8 slot | u16 len | payload`). cdmp insere hooks nos dois pontos centrais (`ClientNet::PostPacket` exe+0x35C670, `ClientNet::OnRecvPacket` exe+0x35CA00) e pode injetar pacotes nos dois sentidos. Tabela de mensagens com RVAs dos tratadores: `docs/research/data/troc_messages_2976.csv` de cdmp.
- Cada mensagem C->S tem função Process (vfunc 2), que desserializa campos um por um (`Deserializer` vfunc +8, contagem de bytes em `r8d`) e chama a lógica do jogo. Delimite funções pela tabela `.pdata`, não pelo preenchimento int3 (tratadores são compactados sem preenchimento; consulte a correção em [NOTES.md](NOTES.md)).
- **Progresso de missão** é dirigido por diagramas de etapas: Quest -> Mission -> Stage, com sequenciadores para cenas por script.
  - `UpdateQuestListAck` (2808), `UpdateMissionListAck` (3009), `UpdateStageListAck` (2724): cabeçalho `u8 scope | u32 player key | u8 a | u8 b` (lista completa a=1 b=0, delta a=0 b=1), depois registros fixos: quest de 34 bytes `{u32 key, u32, u64, u64, u64, u8 state, u8 flag}`, mission de 55 bytes, linhas de stage a cada 56 bytes. Chaves Quest e Mission são chaves estáticas de dados (faixa 0x0F4xxx).
  - Etapas são referenciadas por **IDs de instância em tempo de execução** (números pequenos como 0x158), diferentes por sessão: `StageBranchStateReq` (2436) `u64 instance | u32 branch | u16`; `StageBranchStateAck` (2981) `hdr | u64 instance | u32 state | u32 branch [| u32 chart hash ...]` (conteúdos de 21, 29 ou 37 bytes); `StageOnBranchEventAck` (2524). Uma cena envia várias ramificações seguidas (açougue: 6, 0, 3, 1).
  - **Aceitar uma missão de NPC** é resposta de diálogo, não ramificação de etapa: `SetQuestDialogObstacleReq` (2621, `u32 actor | u8 on`) para jogador e NPC, `QuestDialogEndReq` (2342, 30 bytes: `u32 npc runtime id | u32 quest key | u32 answer | ...`), depois os obstáculos desligados. O servidor aceita sem diálogo aberto. A aceitação muda linhas da lista de missões (3009), não da lista de quests; a entrega também remove itens (`RemoveItemToInventoryAck` 2481).
  - **NPCs:** IDs de atores em tempo de execução mudam a cada carregamento (`ActorLoadDataAck` 2005: u32 runtime id em +3, u32 static character key em +22, nome UTF-16 em +36). Identifique o NPC pela chave estática entre PCs.
  - O NPC se torna "conhecido" (chave de conhecimento, `NormalLearnKnowledgeListAck` 2439) pela primeira ramificação da cena de encontro; sem isso, a opção de entrega permanece desativada.
  - Linhas de missão carregam o **instante de aceitação no relógio do jogo** (cerca de 19 unidades por segundo jogado). Difere entre sessões. Inicialmente foi interpretado como "variante da solicitação" sorteada; essa hipótese foi retirada (consulte [NOTES.md](NOTES.md), 2026-10-20 15:15): os dados da solicitação definem uma tarefa fixa.
- **Rotinas vazias da versão comercial** (processam e não fazem nada): `CompleteQuestByCheatReq`, `ResetQuestByCheatReq`, `StageChartForceBranchDevReq`, `ForcePlayStageDevReq`, `ForcePlayStageSequencerDevReq`, `ChangeGameLevelStateByCheatReq`. Trapaças de missão não são atalho. `StageBranchStateReq`, `StageBranchStateDelayEndReq`, `UpdateStageChartDelayedEventReq`, `QuestDialogEndReq` e outras do próprio jogo estão ativas.
- Salvamentos: `%LOCALAPPDATA%\Pearl Abyss\CD\save\<steam account id>\slot*`; configurações visuais em `user_engine_option_save.xml` ao lado (`_displayType` Windowed/Borderless/FullScreen, `_viewportSize`).
- Proteção contra adulteração Denuvo; nenhum antitrapaça on-line observado em `bin64`.

## <a id="what-we-changed"></a>O que alteramos

Tudo na branch [`dev/quest-stage-tests`](https://github.com/CaptCapybara-cmd/CrimsonDesertMultiplayer/tree/dev/quest-stage-tests) do fork de retomada (sobre [`fix/clang-cl-build`](https://github.com/CaptCapybara-cmd/CrimsonDesertMultiplayer/tree/fix/clang-cl-build)).

- **Correção de compilação clang-cl** (`src/common/enemy_zone.h`): clang rejeita argumento padrão que depende dos inicializadores de membros de uma estrutura aninhada dentro da classe externa; dividido em dois construtores.
- **Sincronização de etapas de missão** (`[coop] stage_sync=1`, desativada por padrão):
  - o host envia cada ramificação escolhida pelo jogo (`StageBranchStateReq`), identificada pela chave estática do sequenciador da etapa;
  - o convidado a aplica à própria instância da etapa quando estiver esperando nela e segue as ramificações posteriores da cena na instância que está na ramificação anterior do host;
  - só são enviadas ramificações escolhidas pelo jogo real: um número inventado faz o jogo travar;
  - regras e testes: `src/common/stage_sync.h`.
- **Compartilhamento de aceitação de missão** (`[coop] quest_share=1`, desativado por padrão, exige `stage_sync=1`; protocolo 11):
  - o mod do host detecta uma aceitação (resposta de diálogo que muda linhas de missão sem remover itens) e a envia com a chave estática do NPC e as linhas alteradas;
  - o mod do convidado espera esse NPC carregar e suas próprias linhas corresponderem ao estado inicial do host, envia a mesma conversa ao servidor próprio e confere as linhas. Entregas e recompensas nunca são compartilhadas: cada jogador conclui a própria solicitação;
  - regras e testes: `src/common/quest_accept.h`.
- **Redução de frequência de Move** (`[coop] move_thin=1`, ativada por padrão): os Moves do outro jogador são reduzidos a cerca de 40 Hz, proposta do próprio autor de cdmp. Sem isso, o buffer de 30 amostras do cliente transbordava, e a cópia parava e saltava.
- **Ferramentas de teste de desenvolvimento** (chaves `[dev]`, todas desativadas por padrão):
  - `test_autoload` / `test_autoquit`: o mod pressiona E dentro da própria janela até o mundo carregar e fecha sem salvar ao terminar o teste. Menus respondem a `WM_KEYDOWN`/`WM_CHAR`, não a Raw Input.
  - `test_walk_s`: move o jogador para frente e para trás. O mouse é preservado (`ClipCursor`/`SetCursorPos` não fazem nada). Um medidor de movimento registra `Puppet motion: RESULT` para a cópia.
  - `stage_record` / `stage_replay`: registra ramificações de etapas, respostas de diálogo de missão e mudanças de quest/mission de uma sessão e as repete num novo carregamento (NPCs convertidos pela chave estática). As linhas de missão registradas são a verificação de aprovação/falha (o horário de aceitação não é comparado).
  - `stage_sync_feed`, `quest_share_feed`: testes em um PC de sincronização de etapas e compartilhamento de aceitação por `cdmp_peer`.
  - `stage_replay_rng`, `mission_watch`: diagnósticos da hipótese de variante retirada (fixação e rastreamento do gerador aleatório do servidor, varredura de memória, monitoramento de escritas por hardware); não são para jogar.
  - `stage_force_test`: caso de mutação (solicitação de desenvolvimento vazia, ramificação inventada).

## <a id="qa"></a>QA

O nível de QA permanece **none**: todas as verificações até agora rodaram em um PC, e não há teste com dois jogadores. As execuções abaixo foram autônomas. Detalhes e datas em [NOTES.md](NOTES.md).

- Testes unitários (`cdmp_tests.exe` sob Wine do Proton): todos passam, incluindo mensagem de ramificação, fila de sincronização e redutor de Move. Mutações: remover a espera de repetição da fila ou a regra de mudança de pai do redutor faz a suíte falhar.
- Registro/repetição por chave estática: ramificação registrada numa sessão aplicada a outro ID de instância na seguinte. O servidor respondeu em 9 ms, e o jogo prosseguiu.
- Sincronização de etapas por `cdmp_peer`:
  - 2 de 2 ramificações fornecidas aplicadas às etapas próprias desse mundo, sem travamento;
  - após corrigir uma disputa, ramificações do próprio jogo retornadas como eco não são mais reenviadas;
  - novamente PASS com 5% de perda de pacotes e variação de latência de 40 ms.
- Cópia caminhando, 60 s de caminhada por bot em cada execução:
  - sem redução: 5 e 14 saltos;
  - com redução: 0 saltos após aquecimento nas duas execuções, máximo 9,8 m/s, distância da cópia igual à caminhada;
  - correndo (Shift pressionado): cerca de um pequeno salto ou parada por minuto com ou sem redução, sem efeito mensurável nessa situação.
- Carregamento automático do mundo: 3 de 3 execuções após mudar para `WM_KEYDOWN`.
- Repetição de aceitação de missão (2026-10-20), a partir de salvamento fixo, sem interação salvo indicação:
  - aceitação registrada de solicitação secundária repetida sem diálogo aberto: o servidor criou as mesmas linhas de missão;
  - com cena de encontro repetida primeiro (4 ramificações encadeadas), o NPC ficou conhecido;
  - execução manual: após cena e aceitação repetidas, uma pessoa preparou o prato e o entregou; o servidor concluiu a solicitação e concedeu a recompensa definida nos dados do jogo.
- Compartilhamento de aceitação ao vivo por `cdmp_peer`: cena de encontro aplicada (4 ramificações), aceitação enviada e verificada, jogo ainda ativo 30 s depois; o host não confundiu a resposta repetida do convidado com uma nova aceitação.
- Testes unitários da mensagem de aceitação, detector e fila, com quatro variantes de mutação (entrega compartilhada, sem verificação do estado inicial, sem verificação de "já aceito", ID do NPC não convertido): cada uma faz a suíte falhar.

## <a id="how-to-play"></a>Como jogar

Use a versão de ByJunter do Nexus (ambos os jogadores, mesma compilação do jogo 2.03.02, amigos Steam). No Linux/Proton, acrescente `WINEDLLOVERRIDES="winmm=n,b" %command%` às opções de inicialização Steam para usar o carregador `winmm.dll` (funcionou no teste básico acima). Faça backup dos salvamentos; não salve enquanto outro jogador estiver no seu mundo.

## <a id="known-issues"></a>Problemas conhecidos

- História, NPCs e itens coletáveis são individuais, exceto pelo compartilhamento experimental de missões; por padrão, só inimigos hostis perto do host são compartilhados.
- Compartilhamento de missão exige ambos no mesmo ponto da história (linhas do convidado devem corresponder ao estado inicial do host) e não foi testado entre dois PCs. Convidado longe do NPC aguarda seu carregamento (até 10 minutos).
- Compartilhamento de aceitação repete a aceitação no convidado; assim, seu próprio servidor também lhe dá os itens dessa aceitação (desejado aqui: cada um conclui a própria solicitação).
- Funciona em uma única compilação; qualquer patch o desativa até atualizar os offsets.
- Um travamento no Proton ao abrir menu (vkd3d-proton `VK_ERROR_DEVICE_LOST`) logo após injetar uma solicitação vazia; não reproduzido desde então. Tratado como desconhecido.

## <a id="next-steps"></a>Próximos passos

1. Sessão em dois PCs com sincronização de etapas e compartilhamento de missões ativos (convidado não aceita nada e mesmo assim deve receber a solicitação).
2. Convidado longe do NPC quando o host aceita (a espera) e convidado entregando após aceitação ao vivo.
3. Detecção de aceitação/entrega em mais missões (até agora, uma amostra de cada).
4. Proteção no cliente que leia a tabela de ramificações da etapa antes de enviar, recusando uma incompatível.
5. Jogadores em pontos diferentes da história; missões principais; testes de sincronização sem jogo com `tools/` do núcleo (mundo simulado, fuzzer) para a fila de aceitações.
6. Bot caminhante: escalada e montaria; encontrar a causa do pequeno resíduo ao correr.

## <a id="tools-in-this-folder"></a>Ferramentas nesta pasta

- `tools/xbuild/`: imagem podman com clang-cl 19, lld-link e Windows SDK/CRT de xwin 0.6.5 (baixe o tarball da versão em `dl/` e confira o SHA-256 primeiro; construir a imagem aceita a licença SDK da Microsoft), além de arquivo de toolchain CMake e `build.sh <abs source dir>` que exibe BUILD_OK/BUILD_FAILED.
- `tools/re/`: scripts capstone + pefile, executados em imagem fixada por hash contra seu próprio `bin64` montado somente para leitura: `dis.py` (desmontagem num RVA), `classify2.py` (tratador vazio ou ativo, limites exatos de .pdata), `disp2.py` (busca de offset de operando), `callers.py` (chamadores diretos), `cap.py` (extrai conteúdos de uma captura `.bin` de cdmp), `questlist.py` / `rows.py` (decodificam Acks de listas), `sections.py`, `missiondiff.py` (mudanças de listas quest/mission numa captura), `rec_from_capture.py` (cria arquivo de repetição de uma captura), `findkey.py`, `immscan.py`, `reach.py`, `iat.py`, `bytes.py`.
- `tools/proton/run_game.sh`: inicia cópia de teste com hardlinks e prefixo próprio pelo Proton. `rng_pin_runs.sh` (repetições autônomas de um salvamento restaurado), `echo_test.sh` (retransmissor cdmp_peer + jogo) e `echo_quest_test.sh` (teste em um PC de compartilhamento de aceitação pelo retransmissor). Todos obtêm a pasta Steam de `STEAM_ROOT`.
