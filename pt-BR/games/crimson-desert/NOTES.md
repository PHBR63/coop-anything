# <a id="crimson-desert--notes"></a>Crimson Desert — notas

## <a id="game-identity-observed-2026-10-19"></a>Identidade do jogo (observada em 2026-10-19)
- Loja: Steam, appid 3321460, ID de compilação Steam 25477059
- Versão de arquivo/produto de CrimsonDesert.exe 1.0.0.2976, timestamp PE 0x6AB28F00, base da imagem 0x140000000
- SHA-256 de CrimsonDesert.exe: 57da440d72f4db974f25fef047cf84c4dadd999a88cb2a3c5af4c9bd67fde1e7
- Motor: BlackSpace (próprio da Pearl Abyss). A instalação inclui steam_api64.dll, sentry, librdkafka, pers.exe.
- SO testado: Linux por Proton (jogo nativo Windows)
- DRM: proteção contra adulteração Denuvo (fonte: https://www.pcgamesn.com/crimson-desert/denuvo-on-steam). Nenhum arquivo de antitrapaça online encontrado em bin64.

## <a id="prior-work-observed"></a>Trabalho anterior (observado)
- ByJunter/CrimsonDesertMultiplayer (cdmp) — https://github.com/ByJunter/CrimsonDesertMultiplayer
  GPL-3.0, v0.2.0 lançada em 2026-10-11; o autor diz que está sem manutenção. Mod ASI (Ultimate ASI Loader winmm.dll).
  Destinado exatamente a 1.0.0.2976 / PE 0x6AB28F00 / compilação Steam 25477059 (src/mod/game/offsets.h) — CORRESPONDE a esta instalação.
  Dois jogadores, cada um em seu save; inimigos compartilhados perto do anfitrião; apenas amigos Steam. Nexus: https://www.nexusmods.com/crimsondesert/mods/3677
- blizz3010/CrimsonDesertCoop — https://github.com/blizz3010/CrimsonDesertCoop
  0.2.3, último push em 2026-07-08, sem licença. Projeto que assume o controle de um companheiro; sincronização de missões/cenas não aplicada.
- No-Context2224: mod ainda não lançado, mais avançado, em desenvolvimento (apenas imprensa: https://wccftech.com/crimson-desert-2-player-co-op-mod-but-more-advanced-soon/)
- Nenhuma issue/PR de coop-anything para este jogo (busca GitHub, 2026-10-19).

## <a id="derived"></a>Deduções
- Caminho de triagem: "Existe um mod cooperativo abandonado" -> retomar cdmp. Ele já executa nesta compilação, portanto jogar hoje exige apenas instalação.
- No Proton, um proxy winmm.dll precisa de WINEDLLOVERRIDES="winmm=n,b" nas opções de inicialização Steam (comportamento padrão do Proton; ainda não testado aqui).

## <a id="unknown"></a>Incógnitas
- Se cdmp funciona no Proton (desconhecido — não executado).
- Se a atualização DLC de 15 de outubro de 2026 alterou a compilação (esta instalação ainda informa 1.0.0.2976).
- Multijogador oficial da Pearl Abyss: discutido publicamente, sem data (desconhecido).

## <a id="checks-actually-run"></a>Verificações realmente executadas
- sha256sum, leitura de cabeçalho PE, leitura de appmanifest, listagem de arquivos de bin64. Nada iniciado, nada instalado.

## <a id="2026-10-19--revive-cdmp-phase-0-2-survey"></a>2026-10-19 — retomada do cdmp: levantamento das fases 0–2
Observado (leitura do repositório cdmp na v0.2.0):
- ~23 mil linhas de C++20 (src + testes). Compilação com MSVC/VS2022 + CMake no Windows; usa SEH (`__try`), SafetyHook, Zydis, ImGui DX12.
- Lista de trabalho em aberto do próprio autor: docs/PLAN-PENDIENTES.md (22 itens). Notas de pesquisa em espanhol, índice em inglês (docs/research/README.md).
- Já existe um método de teste em um PC: `cdmp_peer --mode relay` devolve seu próprio jogador como o "outro" jogador.
- Maiores lacunas para jogar com amigos: convidado não recebe saque/XP/progresso de missões (#17), convidado também vê seus próprios inimigos (#16), chefes (#18), missões/NPCs não compartilhados.
- Correção pequena e bem pesquisada em aberto: etapa 0.2 — golpe final do convidado usa KillCheatReq, que não concede XP e custa ao anfitrião 10–15 de XP de habilidade por morte (pendiente-recompensas-progreso.md §0). Correção proposta: finalizar com AttackByCollisionReq.

Deduções:
- Sem Windows aqui; a compilação precisa de clang-cl + lld-link + SDK/CRT Windows (por exemplo via xwin) em um contêiner podman. mingw não compila SEH do MSVC.
- Instalação de teste: hardlinks nos diretórios de dados de 142 GB, cópia real apenas de bin64 (arquivos do mod + ini ficam ali).

Incógnitas:
- Um segundo caminho de instalação conta como nova ativação Denuvo (limite de 5/dia)? Desconhecido.
- O mod (interceptações inline DX12, Streamline) funciona no Proton/vkd3d? Desconhecido.

## <a id="2026-10-19--build--one-pc-echo-test-on-linuxproton"></a>2026-10-19 — compilação + teste de eco em um PC no Linux/Proton
Observado (verificações que realmente executaram):
- cdmp v0.2.0 (b62a572) compilado no Linux com clang-cl 19 + lld-link + SDK xwin 0.6.5 em podman. Clang 18 falha (MS STL STL1000 exige Clang >= 19).
  Uma correção de código necessária para clang: argumento padrão `Settings s = {}` de enemy_zone.h -> dois construtores (clang rejeita NSDMI de struct aninhada em argumento padrão).
- cdmp_tests.exe no wine do Proton Experimental dentro de SteamLinuxRuntime_4: "All tests passed" (sem contagem por teste).
- dinput8.dll incluído no Ultimate ASI Loader v9.7.4, SHA-256 031a3e55...2daf == dinput8.dll no Ultimate-ASI-Loader-NoPDB_x64.zip oficial (zip e5860e7d...45d1).
- Jogo iniciado de uma instalação de teste com hardlinks + prefixo copiado, por `proton waitforexitandrun` com HOME definido para a pasta home da Steam snap, WINEDLLOVERRIDES="winmm=n,b", área de trabalho virtual wine 1280x720.
  cdmp.log: verificação de compilação aprovada, todas as interceptações instaladas, sobreposição DX12 desenhou mais de 15 mil quadros (vkd3d-proton), boneco de eco criado por cdmp_peer relay,
  mais de 500 eventos reproduzidos, 0 rejeitados, ícone no minimapa exibido, saída normal ("Terminate 시작."). Primeira tentativa de início saiu com código 225 antes de carregar o exe (causa desconhecida; segunda tentativa normal).
- A entrada durante o teste veio de uma pessoa na janela, não de um bot. Ainda sem entrada automatizada.
Incógnitas:
- Efeito do segundo caminho de instalação na contagem de ativações Denuvo (nenhum erro observado).

## <a id="2026-10-19--shared-quests-first-static-pass"></a>2026-10-19 — missões compartilhadas: primeira análise estática
Observado (em docs/research/data/troc_messages_2976.csv do cdmp, a tabela do mod com as 1.114 mensagens Troc internas):
- Hierarquia de progresso visível nos nomes das mensagens: Quest -> Mission -> Stage (+ Sequencer = cenas/cinemáticas roteirizadas, QuestGauge = barras de libertação de acampamentos).
- Avisos de progresso servidor->cliente: UpdateQuestListAck 2808, UpdateMissionListAck 3009, UpdateStageListAck 2724, SubMissionProgressListAck 2102,
  NotifyQuestSaveDataAck 2426, CompleteQuestGaugeAck 2738, UpdateQuestGaugeAck 3088, StageGameEventAck 2222, UpdateStageChartEventAck 2111.
- Solicitações de desenvolvimento/trapaça cliente->servidor ainda registradas: CompleteQuestByCheatReq 2627 (Ack 2889), ResetQuestByCheatReq 2251 (Ack 3078),
  ForcePlayStageDevReq 2885, ForcePlayStageSequencerDevReq 2419, StageChartForceBranchDevReq 2476, MovePlayerByCheatReq 2860, ChangeGameLevelStateByCheatReq 2281.
- cdmp já injeta Reqs de trapaça C->S com sucesso (KillCheatReq, VaryStatCheatReq), portanto o caminho de injeção existe.
Suposições (não testadas, rótulo: suposição):
- "A história segue o anfitrião": capturar Acks de listas de missões/objetivos/etapas do anfitrião, enviar deltas ao convidado, e o convidado injeta CompleteQuestByCheatReq para missões concluídas pelo anfitrião.
  Risco: conclusão por trapaça pode pular recompensas/flags, assim como KillCheatReq pulava XP (veja pendiente-recompensas-progreso.md do cdmp). Testar apenas em um save copiado; nunca salvar nos slots da instalação real.
- Cinemáticas: StageGameEventAck / início de sequenciador do anfitrião poderia acionar ForcePlayStageSequencerDevReq no convidado. Não sabemos se reproduz fora do estado correto do mundo.
Incógnitas:
- Formatos de payload de todas as mensagens acima (precisam de capturas com [sniffer] record=1 e/ou desmontagem dos serializadores).
- Se os IDs de missões são as mesmas chaves nos dois PCs (esperado: chaves de dados estáticos, mesma compilação do jogo -> provavelmente iguais; não verificado).
Próximo:
1. Capturar sessão na cópia de teste com record=1 ao terminar uma etapa de missão / uma barra de acampamento.
2. Desmontar o serializador de CompleteQuestByCheatReq (função de gravação) para obter o layout do payload.

## <a id="2026-10-19--queststage-req-handlers-stub-or-live-static-capstone"></a>2026-10-19 — handlers Req de missão/etapa: stub ou ativo (estático, capstone)
Método: cada Troc C->S tem uma função Process (vf2, RVA em "handler_slot2" de troc_messages_2976.csv do cdmp).
Ela desserializa campos com vfunc Deserializer [+8] (r8d = contagem de bytes) e então chama a lógica do jogo.
Desmontagem linear até o primeiro int3; um handler cujas únicas chamadas são desserializar/vetor/liberar/relatar erro = "stub".
Controle: KillCheatReq (sabidamente funciona no cdmp) -> uma chamada extra exe+0x2C40C00 após a análise = ativo. Scripts: tools/re/ (dis.py; calls.py/classify.py da primeira análise estavam errados, veja a correção abaixo, e não foram mantidos).

Observado (deduzido da desmontagem, compilação 1.0.0.2976):
- STUB na versão comercial (analisa, não faz nada): CompleteQuestByCheatReq 2627, ForcePlayStageDevReq 2885, ForcePlayStageSequencerDevReq 2419,
  ChangeGameLevelStateByCheatReq 2281, MovePlayerByCheatReq 2860, LearnKnowledge*ByCheatReq, ResetHistoryByCheatReq, SetQuestDialogReq (7 instruções).
  Chamadas indiretas verificadas para CompleteQuest/ForcePlay*/ChangeGameLevelState: nenhuma além da análise + caminho de erro.
- ATIVOS: StageChartForceBranchDevReq 2476, ResetQuestByCheatReq 2251, StageBranchStateReq 2436, StageBranchStateDelayEndReq 2105,
  UpdateStageChartDelayedEventReq 2704, StageQuitReq 2325, ReloadStageStartReq 2283, UpdateStageListReq 2454, QuestDialogEndReq 2342,
  QuestDialogInterrogationAnswerCompleteReq 2554, UpdateSequencerGamePlayDataEventReq 2173, RegisterGlobalStageSequencerReq 3046.
- Payloads decodificados:
  - CompleteQuestByCheatReq: u8, u8, u8, depois array até o fim do payload de {u64, u32, u16 (padrão 0x95)} de 14 bytes. (Sem efeito prático: stub.)
  - StageChartForceBranchDevReq: u64 A, u32 B, exatamente 12 bytes. Chama exe+0x2892FE0(stageMgr = session->vf[0x48/8], &res, session, A, B).
Deduções:
- O progresso de missões é dirigido por gráficos de etapas. O atalho "concluir missão" não existe mais; forçar ramificações (Req de desenvolvimento) ou reproduzir as próprias
  Reqs StageBranchState*/QuestDialogEnd do anfitrião no servidor local do convidado são as duas alternativas candidatas.
Incógnitas:
- Significado de A/B (suposição: chave do gráfico de etapas + ID da ramificação). Precisa de captura de jogo normal com record=1.

## <a id="2026-10-19--first-quest-capture-one-pc-cdmp-sniffer-record1-13-min-one-quest-step-done-by-a-person"></a>2026-10-19 — primeira captura de missão (um PC, sniffer cdmp record=1, ~13 min, uma etapa de missão feita por uma pessoa)
Observado (em cdmp_packets_*.log, prévias de payload; little-endian):
- Contagens: UpdateStageStateAck 72 mil (ruído), SetQuestDialogReq/Ack ~900 cada, UpdateStageChartEventReq 823, StageBranchStateReq 53,
  UpdateMissionListAck 98, UpdateStageListAck 82, UpdateQuestListAck 2, NotifyQuestSaveDataAck 2, UpdateQuestGaugeListAck 1.
- Etapa de missão concluída em t=298.98 (tudo no mesmo ms):
  - UpdateQuestListAck len 41: `04 | 01 00 10 A0 (player 0xA0100001) | 00 01 | A5 45 0F 00 (quest 0x0F45A5) | 0x00 x12 | A5 EE 0C 00 (0x0CEEA5) | 0x00 x12 | 02 01`
  - UpdateStageListAck len 12383 (também contém 0x0CEEA5), UpdateMissionListAck len 3802 (missão 0x0F4AB4 primeiro), ~45 EraseNotNoticeChallengeMissionAck,
    depois NotifyQuestSaveDataAck len 19.
  - No carregamento (t=260), o mesmo UpdateQuestListAck era uma lista completa (len 22753).
- Mensagens de etapa contêm pequenos IDs de instância em execução, não chaves estáticas: StageBranchStateReq len 14 = `u64 instance (0x158, 0x17C, ...) | u32 | u16`;
  UpdateStageChartEventReq len 17 = `u64 instance | u32 | u32 | u8`.
  StageBranchStateAck / PrepareSequencerAck pareiam esses IDs com chaves estáticas (0x0F496C, 0x0F4CB1, 0x0F42DB ...) e hashes de 32 bits (0x22B6EC91).
Deduções:
- Chaves de missão/objetivo (faixa 0x0F4xxx) parecem chaves de dados estáticos -> espera-se correspondência entre dois PCs na mesma compilação (não verificado em um segundo PC).
- IDs de instância de etapa são específicos da sessão/PC -> retransmitir StageBranchStateReq / StageChartForceBranchDevReq do anfitrião sem alteração atingiria a etapa errada.
  É necessário um mapa no convidado de chave estática da etapa <-> ID de instância local (a partir de StageBranchStateAck / PrepareSequencerAck / UpdateStageListAck do próprio convidado).
- Unidade candidata de sincronização: deltas UpdateQuestListAck/UpdateMissionListAck do anfitrião (chaves estáticas + estado) -> convidado mapeia para instância local de etapa -> StageChartForceBranchDevReq(u64 instance, u32 branch).
Suposição:
- `02 01` no final do delta de missão = novo estado de missão 2 (concluída?) + flag. Não verificado.
Incógnitas:
- Layouts completos dos elementos UpdateQuestListAck / UpdateMissionListAck / UpdateStageListAck (precisam dos pacotes .bin completos + handlers de cliente 0xBF86C0 / 0xBF9700 / 0xBF8070).
- Se o u64 de StageChartForceBranchDevReq é o ID da instância de etapa em execução (provável, mesma largura/posição de StageBranchStateReq) e quais são os valores de ramificação u32.
Próximo:
1. Decodificar completamente os três Acks de listas a partir do .bin + handlers de cliente.
2. Experimento em um PC na cópia de teste (sem salvar): injetar StageChartForceBranchDevReq para uma instância/ramificação conhecida e observar os Acks.

## <a id="2026-10-19--list-ack--branch-layouts-capture--client-handlers-0xbf86c0-0xbf9700-0xbf8070"></a>2026-10-19 — layouts de lista Ack / ramificação (captura + handlers de cliente 0xBF86C0, 0xBF9700, 0xBF8070)
Observado:
- Cabeçalho comum dos Acks de listas S->C: `u8 scope (4) | u32 player key | u8 a | u8 b`. Lista completa no carregamento: a=1 b=0; delta: a=0 b=1.
- Elemento UpdateQuestListAck = 34 bytes `{u32 quest key, u32, u64, u64 f3, u64, u8 state, u8 flag}` (handler divide por 34).
  Lista completa no carregamento: 669 missões, histograma de estado {2: 618, 5: 25, 3: 17, 1: 9}. Delta da etapa acrescentou missão 0x0F45A5 (ausente no carregamento) com f3=0x0CEEA5, estado 2, flag 1.
- Elemento UpdateMissionListAck = 55 bytes (constante mágica do handler 0x29E4129F = /55): `u32 mission key | u8 1 | u8 state ... | u32 parent key at +30`.
- UpdateStageListAck: constante mágica do handler 0x4EC4EC4F = /52, mas as linhas de dados se repetem a cada 56 bytes (221 elementos em 12376 bytes): `u32 stage key (0x1003A3...) | u8 state | ... | u32 chart key 0x0CEEA5 at +26`. Discrepância de passo não explicada (desconhecida).
- StageBranchStateAck 2981 (len 29 ou 37): `hdr5 | u64 instance | u32 state (0 waiting, 1 branched, 2 ?) | u32 branch (FFFFFFFF = none) | u32 chart-type hash | [u32 hash2, u32 counter]`.
- StageBranchStateReq 2436 (len 14): `u64 instance | u32 branch | u16`. Resposta em ~10 ms: Ack(state 1, branch b) + StageOnBranchEventAck 2524 `hdr5 | u64 instance | u32 branch | u8`.
- 53 pares Req / OnBranch na captura; ramificações vistas: 0 e 5.
Deduções:
- StageChartForceBranchDevReq (u64, u32) tem o mesmo formato de StageBranchStateReq -> u64 = ID de instância de etapa em execução, u32 = ramificação. Teste abaixo.

## <a id="2026-10-19--stagechartforcebranchdevreq-live-test-cdmp-stage_force_test-test-copy-opcode-2476"></a>2026-10-19 — teste ao vivo de StageChartForceBranchDevReq (stage_force_test do cdmp, cópia de teste, opcode 2476)
Verificações que realmente executaram (cdmp.log + captura cdmp_packets_20261019-121524):
- Controle negativo PASS: ForceBranch(instance 0x7FFFFFF0, 0) injetado (visto C>S na captura), sem resposta em 3 s.
- Teste real FAIL: etapa 0x23 (hash 0x22B6EC91) aguardando 21 s (Ack estado 0, ramificação FFFFFFFF); ForceBranch(0x23, 0) injetado (visto C>S em t=66.456),
  nenhum StageBranchStateAck / StageOnBranchEventAck para 0x23 no restante da sessão, nenhum erro de jogo registrado.
  StageBranchStateReq do próprio jogo (0x15D/0x15E/0x15F em t=91) recebeu resposta em 5 ms, portanto o servidor atendia solicitações de ramificação.
- Ainda não executado: teste mutante com opcode stub (sem sentido enquanto o teste real falhar).
Deduções:
- O caminho comercial de forçar ramificação não faz nada visível nesta etapa, exige um u32 diferente (índice da ramificação versus chave da ramificação?) ou recusa sem erro. Não sabemos qual.
Travamento na mesma execução (12:18:12, 90 s após a injeção, bem quando o jogador abriu o menu):
- Log Proton: vkd3d-proton "Device is lost ... Failed to execute pending memory clears" / VK_ERROR_DEVICE_LOST, depois violação de acesso no jogo em exe+0x3BD10E0
  (não em cdmp.asi). O relator de travamento do jogo ("[Crash] 덤프 보내는 중..." = enviando dump) executou.
- Execuções anteriores com cdmp + sobreposição: 18 aberturas de menu, sem travamento. Esta execução também alterou a configuração da janela (área de trabalho virtual Wine removida, jogo Windowed 1280x720).
- Causa: desconhecida. Candidatos: mudança de janela, ramificação forçada, sobreposição cdmp, problema comum de vkd3d/driver.
Execução de isolamento (12:21–12:30, mesma configuração de janela, mesma compilação cdmp + sobreposição + gravação, stage_force_test=0):
- Mundo carregado (12:23), 5 aberturas de menu, saída normal ("Terminate 시작."), nenhum [Crash], DEVICE_LOST ou c0000005 no log Proton.
- Slots de save da cópia de teste não foram alterados pela execução que travou (diferença contra backup: apenas o xml de opções do motor que editamos).
Dedução (fraca, uma execução de cada): a configuração da janela + sobreposição, sozinhas, não reproduziram o travamento em 5 aberturas de menu; a ramificação forçada
na etapa 0x23 continua suspeita, ao lado do acaso. Nada provado em nenhum sentido.

## <a id="2026-10-19--correction-handler-stublive-classification-redone-with-exact-function-bounds"></a>2026-10-19 — CORREÇÃO: classificação de handler stub/ativo refeita com limites exatos de função
Erro: classify.py e calls.py da primeira análise varriam linearmente até o primeiro int3. Aqui, handlers não são separados por preenchimento
int3, portanto as varreduras entravam na função SEGUINTE e atribuíam suas chamadas à anterior. Corrigido em classify2.py: limites da tabela .pdata
RUNTIME_FUNCTION (244.444 entradas). Todos os veredictos "ativo" acima provenientes de classify.py são retirados.
Observado (classify2.py, limites exatos):
- STUB: StageChartForceBranchDevReq 2476 (0x2A5D330–0x2A5D530), ResetQuestByCheatReq 2251, CompleteQuestByCheatReq 2627,
  ForcePlayStageDevReq 2885, ForcePlayStageSequencerDevReq 2419, ChangeGameLevelStateByCheatReq 2281.
- ATIVOS: StageBranchStateReq 2436 -> 0x2891FB0, StageBranchStateDelayEndReq 2105 -> 0x2892210, UpdateStageChartDelayedEventReq 2704 -> 0x28928D0,
  StageQuitReq 2325 -> 0x28934F0, ReloadStageStartReq 2283, UpdateStageListReq 2454 -> 0x287D3C0, QuestDialogEndReq 2342 -> 0x2904F10,
  QuestDialogInterrogationAnswerCompleteReq 2554, UpdateMissionUIStateListReq 2477, UpdateSequencerGamePlayDataEventReq 2173,
  ChangeSequencerPivotReq 2888, RegisterGlobalStageSequencerReq 3046. Controles: KillCheatReq, VaryStatCheatReq ativos (como cdmp os utiliza).
- A função analisada como "forçar ramificação" (0x2892FE0) é a de SubTimelinePauseReq (2406): acrescenta um u32 a um conjunto por etapa
  (dados +0x158, contagem +0x160, condicionado pelo byte +0x28B, marca +0x16 como alterado) e sempre retorna 0. SubTimelineResumeReq (2968) o remove
  por 0x2893260. 0x287CEBF (em ~0x287C200) verifica o conjunto ao percorrer registros por ramificação (u32 em rec-4).
- Assim, a FAIL do teste ao vivo às 12:16 está explicada: StageChartForceBranchDevReq é um stub comercial. Essa execução também serve como execução mutante/negativa.
Deduções:
- Todas as trapaças de missão/etapa foram removidas na versão comercial. A alternativa restante é StageBranchStateReq do próprio jogo (u64 instance | u32 branch | u16),
  enviada pelo mod do convidado com o ID de instância local do convidado. Agora o driver stage_force_test usa por padrão opcode 2436 (payload de 14 bytes).
Ainda não executado: teste ao vivo de StageBranchStateReq.

## <a id="2026-10-19-1618--first-unattended-run-injected-stagebranchstatereq-crashes-the-game-autoload-did-not-work"></a>2026-10-19 16:18 — primeira execução "sem supervisão": StageBranchStateReq injetado trava o jogo (carregamento automático NÃO funcionou)
Configuração: cdmp + novo test_input.cpp ([dev] test_autoload=1: síntese de Raw Input dentro do processo, WM_INPUT com um handle marcador
respondido por uma interceptação de GetRawInputData, GetAsyncKeyState/GetForegroundWindow/GetFocus simulados apenas durante o carregamento automático;
[dev] test_autoquit=1). Teste de etapa com opcode 2436 (StageBranchStateReq, payload de 14 bytes).
Observado:
- Carregamento automático: Enter a cada 4 s, a partir de 15 s após a janela aparecer; o mundo começou a carregar após 14 pressionamentos, MAS uma pessoa
  entrou no mundo pressionando E (tecla de confirmação no título/menu do jogo). Portanto houve entrada humana nesta execução, e não sabemos se
  o Raw Input sintetizado chega ao jogo (Enter pode simplesmente não fazer nada ali).
- Controle negativo PASS (instância inventada 0x7FFFFFF0, sem resposta, sem travamento).
- Alvo: etapa 0x58 (hash 0x22B6EC91), informada como aguardando (Ack estado 0, ramificação FFFFFFFF) por 21 s; StageBranchStateReq(0x58, ramificação 0, 0) injetado.
  53 ms depois: violação de acesso (leitura nula) na thread principal em exe+0xAA1B4D na função ~0xAA1A10:
  `rax = [[[r15+0x58]+0x38]+8]` = 0, depois `mov rdx, [rax + rcx*8]` com rcx = nossa ramificação (0). O relator de travamento do jogo executou.
  Nenhuma perda de dispositivo GPU desta vez. A captura termina pouco antes (últimos registros não descarregados antes de o processo morrer).
- Slot1 de save da cópia de teste não alterado nesta execução.
Deduções:
- StageBranchStateReq não é validado contra a tabela de ramificações da etapa: um índice que a etapa não possui causa travamento.
  O jogo só envia ramificações que sabe existirem, portanto "primeira etapa aguardando, ramificação 0" não é uma sondagem segura.
- O travamento no menu às 12:18 (dispositivo GPU perdido, 90 s após a solicitação stub) tem outra assinatura; ainda desconhecida.
Consequência para sincronização de missões: reproduzir apenas pares (instância, ramificação) que o jogo do anfitrião realmente enviou para a mesma etapa estática,
mapeados ao ID de instância do próprio convidado. Nunca sintetizar números de ramificação.

## <a id="2026-10-19-1623--1627--autoload-checks-without-human-input-fail-game-reads-the-keys-but-ignores-them"></a>2026-10-19 16:23 / 16:27 — verificações de carregamento automático sem entrada humana: FAIL (jogo lê teclas, mas as ignora)
Observado (duas execuções, ninguém tocou na janela, test_autoquit fechou o jogo em cada uma):
- 15 toques sintetizados em E (0x45) (120 ms) em intervalos de 4 s, começando 15 s após a janela aparecer. O jogo leu nosso marcador
  30 vezes por execução (um GetRawInputData por pressionamento/soltura, comando RID_INPUT 0x10000003, buffer de 48 bytes = sizeof(RAWINPUT)),
  também com um hDevice de teclado real de GetRawInputDeviceList (execução 2). O mundo nunca começou a carregar: RESULT FAIL.
Desconhecido (próximo a descartar): se o título exige SEGURAR E, em vez de tocar; se o jogo descarta entrada quando sua
janela não está ativa (rastreado por mensagens WM_ACTIVATE*/foco, não apenas GetForegroundWindow/GetFocus).
- Execução 16:33, uma pessoa deu foco à janela (clique na barra de título) e não pressionou nada: mesma FAIL, 30 leituras. Foco sozinho não é a causa.
- Execução 16:37, WM_INPUT enfileirado (PostMessage, handles marcadores por evento), sem pessoa: FAIL. O jogo leu 29–30 eventos; chama
  GetAsyncKeyState ~100/s, mas nunca para E (0x45). A interceptação RegisterRawInputDevices não viu hwndTarget de teclado (registrado antes
  da nossa interceptação ou com NULL). Suposição: os menus (interface ao estilo HTML/CSS, strings de classe "selector-*" no exe) recebem WM_KEYDOWN/WM_CHAR.
- Execução 16:42, eventos raw MAIS WM_KEYDOWN / WM_CHAR('e') / WM_KEYUP clássicos postados à janela do jogo, sem entrada humana
  (sem entrada humana): PASS. GameLoadingStartReq após o pressionamento 9 (~35 s de pressionamentos), "no mundo" 4 s depois,
  test_autoquit fechou o jogo. Portanto, a interface do título/menu lê mensagens clássicas de teclas, não Raw Input.
  Caminho sem supervisão até o mundo: [dev] test_autoload=1 (tecla padrão E), test_autoquit=1.

## <a id="2026-10-19-1646-1655--record--replay-of-stage-branches-by-static-key-pass-unattended-one-pc-same-save"></a>2026-10-19 16:46–16:55 — gravação + reprodução de ramificações de etapa por chave estática: PASS (sem supervisão, um PC, mesmo save)
Configuração: src/mod/net/stage_replay.cpp do cdmp. Identidade da etapa = chave do sequenciador de PrepareSequencerAck (`hdr5 | u32 player |
u64 instance | u16 | u32 key`), estável entre sessões; IDs de instância não são (chave 0xF4CB1 era 0x159/0x2E0, 0x163, 0x164).
Saves da cópia de teste copiados como backup antes e restaurados entre as duas sessões (sessão de gravação não os alterou).
Observado (sem entrada humana; carregamento automático com 8 pressionamentos em cada vez, test_autoquit fechou o jogo):
- Sessão de gravação ([dev] stage_record=1, 240 s parado no mundo): o próprio jogo enviou StageBranchStateReq para as chaves
  0xF4880, 0xF4CB1, 0xF4CB5: ramificação 0 primeiro, depois ramificação 1 repetidamente (~16 s entre elas). cdmp_stage_record.txt, RESULT PASS.
- Sessão de reprodução ([dev] stage_replay=1, mesmo save): chave 0xF4CB1 surgiu como instância 0x164, aguardando desde t=48.9 s.
  Mais de 2 s depois, o mod enviou StageBranchStateReq(0x164, 0, 0) em t=61.326 — a primeira solicitação de ramificação para 0x164 na
  sessão. Servidor: StageOnBranchEventAck + StageBranchStateAck(estado 1, ramificação 0) em t=61.335 (9 ms). Depois o JOGO continuou
  sozinho com ramificação 1 para 0x164 em t=78.0, como na gravação. Jogo ainda executando 30 s depois: RESULT PASS x2.
  Verificado na captura de pacotes, não apenas no log do driver.
Deduções:
- Reproduzir uma ramificação que o jogo realmente escolheu na instância local encontrada pela chave estática é aceito, e o gráfico de etapas
  continua a partir dela. Esse é o mecanismo de "convidado segue anfitrião" para etapas existentes nos dois mundos.
Limites (honestos): um PC, um jogador, mesmo save, uma etapa, uma execução. Ainda não: segundo PC/jogador, etapas em que anfitrião e convidado
estão em pontos diferentes da história, deltas das listas de missões/objetivos, recompensas. Contraparte mutante já observada: uma ramificação inventada
(16:18) trava o jogo.

## <a id="2026-10-19-1708--live-stage-sync-over-cdmps-network-one-pc-echo-test-pass-2-genuine-applications"></a>2026-10-19 17:08 — sincronização de etapas em tempo real pela rede cdmp, teste de eco em um PC: PASS (2 aplicações reais)
Código: common/stage_sync.h (fila do convidado, teste unitário + verificação mutante: remover a espera de repetição faz falhar tests.cpp:1067/1069),
proto RelKind::StageBranch = 9 (u32 sequencer key | u32 branch | u16 flags, confiável), kVersion 10, mod/net/stage_tracker
(controle compartilhado de instância<->chave), mod/net/stage_sync ([coop] stage_sync=1; [dev] stage_sync_feed=1 = alimentação do teste de eco).
Observado (cdmp_peer --mode relay --delay 50, sem supervisão, saves restaurados ao ponto inicial de gravação/reprodução):
- Alimentação de 3 ramificações gravadas como se fossem do anfitrião em entrada no mundo+20 s -> relay (86 fragmentos confiáveis, 0 descartados) -> metade convidada:
  chave 0xF4CB1 -> nossa instância 0x164, 0xF4CB5 -> 0x165, ambas enviadas em t=85.607 (primeiras solicitações de ramificação delas),
  servidor OnBranch + Ack(estado 1, ramificação 0) em t=85.615. Jogo ainda executando 30 s depois. Verificado na captura.
- Condição de corrida encontrada: a própria ramificação do jogo de 0x163 (chave 0xF4893, t=91.453, respondida em 91.512) voltou pelo eco e o convidado
  enviou a mesma ramificação novamente em 91.515, antes de o rastreador (thread de gravação do sniffer, alguns ms atrasada) ver a resposta. Inofensivo
  (ramificação idêntica), mas o driver contou como "applied 3". Corrigido: uma etapa cuja própria solicitação de ramificação não foi respondida fica "ocupada"
  e não é alterada (teste unitário acrescentado). Execução de confirmação abaixo.
Observado por uma pessoa olhando a janela: a cópia de eco do jogador anima aos solavancos e às vezes se teletransporta.
  Log: 4001 eventos reproduzidos, deslocamento de relógio 0 ms, nada descartado na conexão; 1584 de 3891 posições de movimento descartadas como
  repetidas; configuração de teste usa coop delay_ms=1500 e deslocamento 0,01 m. Causa desconhecida; o autor do cdmp também observou teletransportes ocasionais.
- Execução de confirmação 17:12 com a correção de ocupado (mesma configuração): enviadas 2, aplicadas 2 (0xF4CB1 -> 0x164, 0xF4CB5 -> 0x165); as
  próprias ramificações do jogo que voltaram pelo eco contaram como "reached by our game alone" (4) e não foram reenviadas. Jogo vivo 30 s depois.
  Testes unitários passam (binário novo). Limites: um PC, relay de eco, mesmo save nos dois "lados", apenas primeira ramificação de uma etapa.
- Retrabalho da reprodução 17:18 (todas as ramificações gravadas por StageSyncQueue; deltas de lista de missões gravados como "Q key state flag" e
  usados como oráculo): regressão na gravação de etapas de ambiente, sem supervisão: aplicadas 2 (0xF4CB1 -> 0x163, 0xF4CB5 -> 0x164,
  IDs diferentes de novo), alcançadas sozinho 21, PASS; vivo 30 s depois. Nenhuma alteração de missão nessa gravação, portanto o oráculo de missão não foi testado.

## <a id="2026-10-19--where-a-bad-branch-is-not-validated-static"></a>2026-10-19 — onde uma ramificação inválida é (ou não é) validada (estático)
Observado:
- O handler de StageBranchStateReq chama exe+0x2891FB0, que não tem entrada .pdata: é um único `jmp 0x1502D2B70` para .xtls
  (RVA 0x75C9000, ~250 MB, características 0xE0000020), seguido de bytes que não são código. A lógica de ramificação do servidor é virtualizada
  (VM do protetor); não é legível com desmontagem comum. (tools/re/fn.py: desmontagem de uma única função limitada por .pdata.)
- O ponto do travamento das 16:18, exe+0xAA1B4D, está em uma função normal de cliente (0xAA1A10–0xAA1E5C) que indexa uma tabela de ramificações
  ([[[r15+0x58]+0x38]+8] + branch*8) ao tratar a resposta.
Deduções:
- O servidor aceitou a ramificação inventada e respondeu; o cliente travou ao aplicá-la. Portanto, uma proteção de sincronização de etapas precisa
  ficar no cliente: ler a tabela de ramificações da etapa (contagem/ponteiro) antes de enviar e recusar ramificações fora dos limites.
  Ainda não implementado; a mesma chave estática nos dois PCs deve significar o mesmo gráfico e conjunto de ramificações, portanto isso importa para compilações/dados incompatíveis.

## <a id="2026-10-19-1724--stage-sync-echo-test-under-a-lossy-link-pass"></a>2026-10-19 17:24 — teste de eco de sincronização de etapas numa conexão com perdas: PASS
cdmp_peer --mode relay --delay 60 --loss 5 --jitter 40 (relay descartou 420 de 8518 pacotes, 4,9%), sem supervisão: todas as 3 ramificações
alimentadas chegaram pelo canal confiável (71 fragmentos), aplicadas 2 (0xF4CB1 -> 0x163, 0xF4CB5 -> 0x164) 100 ms após a alimentação,
ramificações próprias devolvidas por eco alcançadas sozinho 2, jogo vivo 30 s depois.

## <a id="2026-10-19--the-echo-copys-stutterteleports-separate-read-only-investigation-its-write-up-is-not-in-this-repo-the-findings-are-below"></a>2026-10-19 — engasgos/teletransportes da cópia de eco (investigação separada, somente leitura; seu relato não está neste repositório, resultados abaixo)
Resumo dos resultados (referências de código conferidas aqui: inject_clock.h:27 kAheadMs=450; coop.cpp:121–124 deslocamento do eco apenas quando offset_m==0):
- Nossa configuração de teste causou boa parte disso: delay_ms=1500 versus limite "adiantado" de 450 ms remarca o horário de cada Move (margem de tempo fixada em
  650 ms, ~40% descartados como repetidos, ações ~1 s atrás das posições); offset_m=0.01 desativa o deslocamento de eco de 2,5 m, portanto a cópia
  fica dentro do jogador e o empurra (jogador derivou ~25 m sem entrada após a cópia surgir).
- Problema real do cdmp também nas configurações padrão: Moves chegam a ~83 Hz e nunca são espaçados; o buffer de interpolação do cliente, de 30 amostras,
  transborda (modelo offline do algoritmo documentado do cliente: ~3700 expulsões por execução com atraso 300), causando parada seguida de
  salto. A proposta P2 do próprio autor (descartar Moves separados por < 22 ms) nunca foi implementada; o modelo prevê 0 expulsões com ela.
- Configurações de teste retornadas a delay_ms=300, offset_m=0. Correções ainda não implementadas nem testadas; uma verificação ao vivo precisa de um bot que ande.

## <a id="2026-10-19-1732-1745--copy-stutter-move-thinning-authors-p2--walking-bot-pass"></a>2026-10-19 17:32–17:45 — engasgos da cópia: espaçamento de Move (P2 do autor) + bot caminhante: PASS
Código: common/move_thinner.h (descarta um Move do jogador < 22 ms após o último mantido, exceto o primeiro após intervalo de 150 ms, troca de pai ou
fora de ordem; um Move descartado é retido e enviado após 60 ms de silêncio), testes unitários + verificação mutante (remover a regra de troca de pai
faz falhar tests.cpp:1058); remote_puppet.cpp aplica isso apenas aos Moves do jogador ([coop] move_thin, padrão 1);
test_input: [dev] test_walk_s (segura W por 4 s / S por 4 s via WM_INPUT + repetição automática WM_KEYDOWN; ClipCursor/SetCursorPos não fazem nada
enquanto o foco é simulado); net/puppet_motion: amostra a posição da cópia ~a cada 20 ms, conta saltos (> 15 m/s) e
parada seguida de salto (parado >= 150 ms, depois > 10 m/s); aquecimento de 3 s acrescentado após a execução 1 mostrar o ajuste brusco do primeiro Move.
Observado (relay de eco, delay_ms 300, offset_m 0, 60 s de caminhada do bot, sem supervisão; o bot move o jogador: 90–103 m por execução;
o jogo lê teclas de movimento pela entrada da janela, nunca GetAsyncKeyState):
- move_thin=0: execução 1, saltos 5 (primeiro em +2,5 s), FAIL; execução 2, saltos 14 + 1 parada seguida de salto, máximo 83 m/s, FAIL.
- move_thin=1: execução 1, saltos 2, ambos nos primeiros 0,3 s (primeiro Move após repouso) e 0 depois; 1945 Moves descartados por estarem
  próximos demais, 3 retidos e liberados nas paradas. Execução 2 (com aquecimento): saltos 0, saltos após parada 0, máximo 9,8 m/s, cópia 91,9 m versus caminhada 91,6 m: PASS.
Limites: um PC, relay de eco, apenas caminhada no plano (sem cavalo, escalada, combate), duas execuções por lado.

## <a id="2026-10-19--client-branch-table-for-a-future-guard-static"></a>2026-10-19 — tabela de ramificações do cliente (para uma proteção futura), estático
Observado (função de cliente 0xAA1A10–0xAA1E5C, código normal):
- Mesmo padrão do servidor: bloqueio em [mgr+8], depois busca de etapa exe+0x1F6C190(mgr, &out, instance) -> objeto da etapa (r15).
- Ponteiro da ramificação = [[[stage+0x58]+0x38]+8][branch]: o objeto de gráfico ([stage+0x58]+0x38) contém um vetor {ponteiro de dados, contagem u32} em
  +8, portanto a contagem está em chart+0x10 (o mesmo layout {dados, contagem} é lido em [[r13+0x50]+0x10]/+0x18 algumas linhas depois).
  Para etapa 0x58 (travamento 16:18), o ponteiro de dados era nulo: essa etapa não tem tabela de ramificações, portanto qualquer ramificação trava.
Dedução: uma proteção é `data != null && branch < count`. Não implementada: precisa do gerenciador de etapas do cliente + bloqueio para chamar a busca
a partir do mod, e só importa se os dados dos dois jogos diferirem, algo que cdmp já impede (mesma compilação, mesma versão do mod).

## <a id="2026-10-19-1751-1803--running-shift-held-with-and-without-thinning"></a>2026-10-19 17:51–18:03 — corrida (Shift segurado) com e sem espaçamento
Observado (relay de eco, atraso 300, sem supervisão, execuções de 60 s; Shift+W/S percorre 218–333 m contra ~90 m andando, portanto Shift realmente corre):
- Primeiro par, medidor antigo (tempo GetTickCount64, regra de salto apenas por velocidade): 20 contra 17 "saltos". Os da execução espaçada eram todos
  de 0,34–0,56 m por ~22 ms: 2–3 quadros do jogo correndo medidos com relógio de ~16 ms, ou seja, ruído do medidor; a execução sem espaçamento também teve
  saltos reais (1,11, 0,83, 1,81 m).
- Medidor corrigido (tempo QueryPerformanceCounter; um salto também deve exceder 0,75 m): move_thin=0, saltos 1 (1,13 m) + 1 parada seguida de salto
  (0,23 m após 171 ms); move_thin=1, saltos 1 (0,88 m) + 1 parada seguida de salto (0,25 m após 193 ms). Ambos "FAIL" pela regra estrita.
Dedução: correndo, o espaçamento não faz diferença mensurável; aproximadamente um pequeno evento por minuto permanece nos dois casos, sem relação com
iniciar ou parar. Os resultados de caminhada acima foram medidos com o medidor antigo, mas seus saltos foram de 0,5–1,8 m (base)
contra nenhum (espaçado), portanto continuam válidos. Causa do resíduo na corrida: desconhecida.

## <a id="2026-10-20-1242-1248--a-person-accepts-a-quest-renees-request-recorded-one-pc-test-copy-cdmp-stage_record1--sniffer"></a>2026-10-20 12:42–12:48 — uma pessoa aceita uma missão ("Renee's Request"), gravada (um PC, cópia de teste, cdmp stage_record=1 + sniffer)
Configuração: saves no ponto de restauração da gravação/reprodução; bot de caminhada, carregamento automático e saída automática desligados; [net] desligado; uma pessoa jogou (execução manual).
Primeira inicialização falhou: Steam não estava executando ("steamclient_init_registry Failed to connect to Steam"), o jogo saiu antes
da inicialização tardia do mod. Reiniciado com Steam aberta: normal. (Lição: verificar `pgrep steam` antes de iniciar.)
Observado (captura cdmp_packets_20261020-124236, t = s desde o primeiro pacote; tools/re/missiondiff.py compara os Acks de listas):
- t=201.6–204.3: ~8 PrepareSequencerAck (preparação de cena) + nova chave de etapa 0xF475E (instância 0x1A5); o próprio jogo enviou
  StageBranchStateReq, ramificações 6, 0, 3, 1 para ela em 6 s (t=204.3–210.3). Nenhum Ack de lista mudou então.
- t=254.147 C>S QuestDialogEndReq 2342, 30 bytes: `u32 0xB01001C1 | u32 0x0F4440 | u32 10 | u32 0 x2 | u32 1 | u16 0 | u32 0xEAC5E173`.
  Em até 40 ms, o servidor enviou:
  - UpdateMissionListAck 3009 DELTA (a=0), 3 linhas de 55 bytes, chaves 0xFFFFF7F8 / F7 / F6 (negativas: -2056..-2058), cada uma
    contendo 0x0D2DA7 (linha 1 em +14, linhas 2–3 em +6); linhas 1 e 3 contêm três floats em +34 ((-10677, 611.5, -3904) e
    (-10680, 611, -3897)): uma posição no mundo.
  - UpdateTraceMissionAck 2346 (missão rastreada 0 -> 0xFFFFF7F7), SetExecuteTimeQuestDialogAck 2163 (`hdr5 | u32 0x869D0124 | u32 0x0D2DAB | ...`).
- Nenhum UpdateQuestListAck (2808), nenhuma alteração de linha em UpdateStageListAck. A lista de missões (3692 bytes, a=0) é reenviada sem alteração a cada ~10 s.
Deduções:
- Aceitar esta missão = a resposta de diálogo (QuestDialogEndReq), não uma ramificação de etapa. O gravador de ramificações de etapa sozinho não consegue
  reproduzi-la, e o oráculo de lista de missões (deltas 2808) não vê nada: missões de "solicitação" ficam na lista de objetivos.
Suposição:
- 0xB01001C1 = ID do ator NPC em execução (mesma família do jogador 0xA0100001); 0x0F4440 = chave estática de diálogo; 10 = a resposta;
  0xEAC5E173 = hash semelhante aos hashes de etapa. 0xFFFFF7Fx = IDs dinâmicos por jogador de uma instância de "solicitação", 0x0D2DA7/0x0D2DAB = seu
  modelo estático. Se for isso, o convidado deve mapear pela chave do modelo, não pelo ID negativo. Não verificado.
Desconhecido: se o servidor aceita QuestDialogEndReq sem diálogo aberto; se 0xB01001C1 é o mesmo após um novo carregamento.

## <a id="2026-10-20-1254-1300--replaying-the-quest-accept-dialog-unattended-two-runs-the-server-rolls-the-request-variant"></a>2026-10-20 12:54–13:00 — reprodução do diálogo de aceitação, sem supervisão (duas execuções): o servidor SORTEIA a variante da solicitação
Código (cdmp, local): common/mission_rows.h (comparação da lista de missões pela linha inteira de 55 bytes; teste unitário + verificação mutante: remover o
teste "same row" faz falhar tests.cpp:1145), stage_tracker grava QuestDialogEndReq/SetQuestDialogObstacleReq e alterações
de missões, stage_replay grava "D op ms hex" / "M key kind state row" e reproduz o diálogo 20 s após entrar no mundo (intervalos
gravados limitados a 3 s). Arquivo de reprodução criado da captura 12:42 por tools/re/rec_from_capture.py (bytes exatos, 5 mensagens
de diálogo + 3 linhas de missão, sem ramificações de etapa). Saves restaurados ao ponto inicial de gravação/reprodução antes de cada execução.
Observado:
- Ambas: o servidor aceitou a conversa reproduzida (obstáculo ativado x2 -> resposta -> obstáculo desativado x2), sem conversa com NPC
  aberta e com o jogador onde o save começa (não junto de Renee); em 4 ms acrescentou os mesmos três slots
  0xFFFFF7F8/7/6 com o mesmo tipo/estado e os mesmos floats de posição. Jogo vivo 30 s depois nas duas vezes.
- A chave do modelo da solicitação nas linhas (+14 na linha 1, +6 nas linhas 2–3) diferiu a cada vez:
  pessoa 0x0D2DA7 ("cozinhar um prato de peixe"), reprodução 1 0x0D2147, reprodução 2 0x0D214C ("cozinhar mingau de peixe", visto na tela).
  SetExecuteTimeQuestDialogAck continha 0x0D2DAB / 0x0D214B, respectivamente.
- A verificação da execução 1 disse PASS porque comparava apenas chave do slot + tipo + estado: um FALSO PASS (percebido na tela durante a verificação manual). Corrigido:
  a linha inteira é comparada e bytes diferentes são registrados; execução 2 = FAIL "row DIFFERS: +14:4C(recorded A7)".
- "Foul-Mouthed Reunion accepted", relatado pela tela na execução 1, era apenas a missão rastreada no carregamento (corrigido numa segunda olhada); sua chave não está
  em nenhuma lista de missões do carregamento (tools/re/findkey.py).
- Steam Cloud: o remotecache.vdf real em userdata/<id>/3321460/ foi regravado no fim de uma execução de teste, mas lista apenas entradas
  antigas (2026-03/09); nenhum save de teste foi enviado. Acompanhar isso.
Deduções:
- QuestDialogEndReq é aceito sem o diálogo aberto (nenhuma verificação de distância/NPC vista): é uma alternativa utilizável.
- Missões de "solicitação" são sorteadas pelo servidor na aceitação; os slots de missão são reutilizados. O cooperativo deve transmitir a
  chave do modelo do anfitrião (0x0D2xxx), não a resposta de diálogo do anfitrião, ou o convidado recebe outra variante.
Desconhecido: se o sorteio é aleatório ou segue o estado do mundo (tempo, semente RNG); qual mensagem, se houver, faz o servidor
aceitar um modelo específico (próximo: análise estática do handler QuestDialogEndReq, exe+0x2904F10, para localizar a escolha do modelo).
Nota sobre o ambiente de teste: `pgrep -f CrimsonDesert.exe` dentro de um comando shell que contém esse texto encontra o próprio shell
(o "ainda executando" observado após execução 2 era o shell da própria verificação). Use `pgrep -x CrimsonDesert.e` ou a saída do inicializador.
Saves conferidos novamente após a saída real: no ponto de restauração.

## <a id="2026-10-20--where-the-request-variant-is-chosen-can-the-client-name-it-static-build-2976"></a>2026-10-20 — onde a variante da solicitação é escolhida; o cliente consegue indicá-la? (estático, compilação 2976)
Ferramentas: tools/re/fn.py, classify2.py, reach.py (busca em largura de chamadas diretas), immscan.py (constantes RNG), iat.py (nomes de importação).
Observado (desmontagem):
- Handler QuestDialogEndReq 0x2A4C510 -> 0x2904F10: apenas validação. Busca NPC/diálogo em tabelas hash, pega a
  entrada de resposta (resposta x 0x70 + 0x10 numa tabela de diálogo), verifica condições (cada falha = código de erro), depois chama
  0x2905DC0(session, &dialog key, answer entry).
- 0x2905DC0 executa a entrada de resposta: para cada chave u16 em sua lista em +0x00/+0x08 -> busca 0x4A1EE0 -> 0x22CF730
  (um erro interrompe a resposta); transforma itens de 16 bytes em +0x10/+0x18 em registros de 40 bytes; agrupa o relógio do jogo
  (limites de 3 h / 21 h, provavelmente o "execute time" em SetExecuteTimeQuestDialogAck); chama 0x2781490 (13 argumentos).
- RNG: um gerador compartilhado, estilo rand do MSVC (x*0x343FD + 0x269EC3, duas etapas -> 32 bits), estado por THREAD (TLS +0x4AD8),
  inicializado sob demanda com GetCurrentThreadId() (getter 0x1378F10, importação resolvida com iat.py). ~50 funções na faixa de
  código de missões o chamam.
- 0x22CF730 começa com uma condição de probabilidade: rand32 % 1.000.000 < [entry+0x50] -> retorna 0 (nada); caso contrário, percorre subentradas
  e chama 0x22CFDD0. 0x22CFDD0 é uma escolha ponderada entre entradas de 0x70 bytes (peso u64 em +0x10): byte de modo 0/1 = cada
  entrada sorteada independentemente contra 1.000.000; modo 2 = um sorteio, subtrair pesos até atingir, aplicar ESSA entrada;
  repetido [+0x14] vezes.
- reach.py a partir de 0x2905DC0 (6 níveis, apenas chamadas diretas): RNG alcançado via 0x22CF730, 0x22CFDD0 e mais profundamente na
  subárvore de 0x2781490 (caminhos 0x2B99540, 0x2B99FD0, 0x1F41BA0, 0x1379340).
- Reqs de cliente que poderiam indicar missão/objetivo/modelo: nenhuma. Toda Req C->S de missão/objetivo foi listada de
  troc_messages_2976.csv; as de trapaça são stubs comerciais (classify2.py: AddTestPlayStageListReq, ManagementForCheatReq,
  ResetQuestByCheatReq, ResetHistoryByCheatReq, SetWantedForDevReq STUB). CheatDirectPlayReq aparece como "ativa" apenas por
  uma chamada genérica (0x2773630, código 0x3F5, provavelmente relatório); lê um u32 + vec3 e nunca os usa: efetivamente um
  stub. As ativas (MissionTriggerInOutReq, RegistNotNoticeChallengeMissionReq, UpdateMissionUIStateListReq,
  RewardAfterRelationalDialogReq) não recebem chave de modelo (não lidas em detalhe).
Deduções:
- Três carregamentos de um save deram três variantes porque a semente é um ID de thread (diferente a cada início) e o número
  de sorteios antes da aceitação difere. Coerente com a observação; não está provado que a variante vem de
  0x22CFDD0, e não de algum uso de RNG sob 0x2781490 (Suposição: 0x22CFDD0 modo 2).
- Alternativa para cooperativo (não testada): anfitrião e convidado executam o mesmo código e dados (mesma compilação obrigatória). Se a thread
  do servidor do convidado tiver o estado RNG do ANFITRIÃO ao processar QuestDialogEndReq do anfitrião, deve realizar os mesmos sorteios e
  escolher a mesma variante. Ambos os lados podem fazer isso numa interceptação de entrada do handler (0x2A4C510, executa na thread
  do servidor): o anfitrião lê *0x1378F10() antes de sua própria aceitação e envia junto com a resposta; o convidado grava antes
  da aceitação injetada. Risco: qualquer sorteio extra (estado diferente do mundo) quebra isso; a verificação das linhas de missão mostraria.
- Teste em um PC que não precisa de pessoa: reproduzir o diálogo duas vezes com estado RNG fixado na mesma constante na
  entrada do handler; mesmo modelo nas duas vezes = determinístico; depois terceira execução com outra constante (espera-se outro modelo).

## <a id="2026-10-20-1315-1350--pinning-the-server-rand-at-the-accept-does-not-fix-the-request-variant-unattended-5-runs"></a>2026-10-20 13:15–13:50 — fixar rand do servidor na aceitação NÃO corrige a variante da solicitação (sem supervisão, 5 execuções)
Código (cdmp, local): mod/net/quest_rng (interceptação intermediária no handler de QuestDialogEndReq, exe+0x2A4C510; define o estado rand
da thread pelo getter exe+0x1378F10; com fixação, interceptações apenas de log no getter e em 0x22CF730/0x22CFDD0 rastreiam 3 s de
sorteios), [dev] stage_replay_rng=<decimal> (0 = desligado). Executor tools/proton/rng_pin_runs.sh (restaura saves antes e
depois de cada execução). Mesmo arquivo de reprodução de antes (a aceitação de Renee's Request na execução manual, bytes exatos).
Observado:
- O handler executa na thread do servidor (812 nestas execuções); a interceptação definiu o estado a cada vez (log "pinned").
- Modelos: fixação 12345 -> 0x0D219C, 0x0D215D, 0x0D2197 (execução rastreada), 0x0D2153, 0x0D2158; fixação 987654321 -> 0x0D2150.
  Mesma fixação, variante diferente: FAIL.
- Rastreio de sorteios, duas execuções com fixação 12345: os sorteios da thread do servidor são idênticos, estado por estado, pelos primeiros ~70 ms
  (5 x [condição de probabilidade 0x22CF730: 2 sorteios, escolha ponderada 0x22CFDD0: 3 sorteios], depois 0x2B039BE em ~70 ms); diferem
  pela primeira vez em ~180 ms (uma sequência 0x1378FB4 de 120 contra 68 sorteios). As linhas de missão voltaram em +16/+3 ms (captura).
- Slot 0xFFFFF7F8 está na lista de missões do carregamento com tipo 2 e modelo 0; o modelo só aparece na aceitação
  (findkey.py: visto pela primeira vez no delta 3009 da aceitação, nas duas execuções).
Deduções:
- A variante é escolhida na aceitação, mas NÃO por esse rand: tudo que esse rand produziu até as linhas de missão e além
  foi idêntico, enquanto a variante diferiu. CORREÇÃO da seção estática acima: a suposição "0x22CFDD0 modo 2
  escolhe a variante" é retirada (essas escolhas são determinísticas com fixação e não a decidem).
Desconhecido: origem da variante. Candidatos: outro gerador (immscan.py encontrou constantes estilo PCG/MT em outros pontos), um
relógio ou o código .xtls virtualizado (dois sorteios individuais em exe+0x104F41EA / 0x104F74A6 aparecem depois na mesma thread).
Opções a partir daqui: (1) encontrar quem grava o modelo (dinâmico: observar o objeto de missão do servidor para slot 0xFFFFF7F8 na
aceitação); (2) após a aceitação no convidado, sobrescrever o modelo no objeto de missão do servidor do convidado com o do anfitrião
(precisa de (1)); (3) aceitar que cada jogador recebe sua própria variante de uma missão de solicitação (missões da história usam ramificações de etapa,
que já sincronizam).
Cópia de teste: saves de volta ao ponto de restauração e cdmp.ini restaurado após cada execução (conferido).

## <a id="2026-10-20-1355-1410--who-writes-the-request-template-forcing-the-hosts-variant-unattended-4-runs"></a>2026-10-20 13:55–14:10 — quem grava o modelo da solicitação; forçando a variante do anfitrião (sem supervisão, 4 execuções)
Código (cdmp, local): mod/net/mission_watch ([dev] mission_watch=1 varredura | 2 observação de gravação por hardware | 3 forçar; lido por
stage_replay de cdmp.ini). Executor: tools/proton/rng_pin_runs.sh com EXTRA_INI.
Observado:
- Varredura (modo 1) na aceitação: 31 dwords == 0xFFFFF7F8 em ~5,4 GB de memória privada RW (4,1 s, thread do servidor bloqueada). 300 ms depois,
  o modelo apareceu em dois objetos (provavelmente servidor e cliente): modelo em chave+16, tipo/estado em chave+4
  (0x0102 -> 0x0105), posição x em chave+36. Uma segunda cópia da chave fica 44 bytes antes de cada uma.
- Observação de gravação por hardware (modo 2, DR0–3 na thread do servidor, definidos por uma thread auxiliar enquanto a do servidor espera):
  disparou em exe+0x1A9B4E1, instrução após `mov [rdi+0x38], rax` em exe+0x1A9B4A0, rax = modelo. 0x1A9B4A0 é a
  atribuição por cópia do objeto de missão (rcx = destino, rdx = origem): chave +0x28, tipo/estado +0x2C/+0x2D, modelo +0x38 (slot principal).
  Thread do servidor; o handler QuestDialogEndReq NÃO está na pilha: 0x2774B20 -> 0x2C33FE0 -> 0x1ABAC90 -> 0x290DBD0 ->
  0x292C450 -> 0x292D600 -> 0x29283A0 -> 0x2928B80 -> 0x1AC8DD0 -> 0x1AC8C13 -> 0x1ABF9A0 -> 0x1A9B4A0 (desempilhamento Wine).
  O modelo já estava em src. A execução então TRAVOU (relator de travamento do jogo): Wine não preencheu Dr6, portanto nosso handler
  recusou a etapa única. Corrigido (considerar como nossa uma etapa única enquanto armado). Apenas cópia de teste; saves restaurados.
- Forçar (modo 3) na cópia: modelo sorteado do slot 0xFFFFF7F8 -> 0x0D2DA7 (valor da execução manual) em src+0x38 antes da
  primeira cópia (+10 ms): a linha do delta 3009 de 0xFFFFF7F8 então correspondeu à gravação manual byte a byte.
  Os slots de objetivo 0xFFFFF7F7/F6 (modelo em +0x30 nos objetos) foram copiados pela primeira vez 6 s depois, portanto o cliente os recebeu
  com o modelo sorteado; o estado do próprio servidor já estava corrigido: SetMissionNewAlarmFalseAck 2212 em +60 s
  reenviou 0xFFFFF7F7 com 0x0D2DA7 (execução T2 não forçada: o sorteado).
  SetExecuteTimeQuestDialogAck 2163 ainda continha sorteado+4 (0x0D2157), não 0x0D2DAB: outro objeto do servidor mantém a variante
  sorteada (um diálogo pendente). Jogo vivo 30 s depois; nada mais verificado (nenhuma pessoa concluiu a solicitação).
- reach.py: nenhuma função com constantes PCG/MT/proporção áurea/murmur em até 7 níveis de chamadas diretas de 0x290DBD0 (2692
  funções) ou 0x292C450 (1786). O sorteio está por trás de chamadas virtuais ou em código virtualizado.
Deduções:
- Gravar o modelo do anfitrião nos objetos de missão do convidado funciona para os slots (imediatamente para o principal), mas os outros
  produtos do sorteio (diálogo pendente, talvez mais) permanecem com a variante do convidado. Não se sabe se concluir a solicitação depois
  segue a receita forçada ou a sorteada (precisa de uma pessoa para cozinhar e entregar, ou mais engenharia reversa).
Suposição: forçar no próprio sorteio (antes de criar qualquer produto) é a correção limpa; encontrá-lo exige observar gravações no
objeto novo da solicitação (src alinhado à página, por exemplo 0x...450000) antes de existir, por exemplo pela sua alocação.

## <a id="2026-10-20-1403-1425--forced-replay-played-by-hand-what-a-person-sees-test-copy"></a>2026-10-20 14:03–14:25 — reprodução forçada jogada manualmente: o que uma pessoa vê (cópia de teste)
Configuração: saves no ponto de restauração; reprodução da aceitação (apenas diálogo, sem ramificações de etapa), mission_watch=3 forçando 0x0D2DA7
em 0xFFFFF7F8/F7/F6; sem saída automática; uma pessoa continuou jogando (execução manual).
Observado (execução manual, dentro do jogo):
- O diário de missões mostrou MINGAU DE PEIXE (o sorteio era 0x0D2158), não o prato de peixe forçado.
- Renee era "desconhecida" para o personagem; a opção de entrega estava desabilitada.
Observado (log + captura):
- Forçando como antes: slot principal forçado na primeira cópia, slots de objetivo 6 s depois; o cliente já havia recebido as
  linhas de objetivo e SetExecuteTimeQuestDialogAck (sorteado+4) com a variante sorteada; SetMissionNewAlarmFalseAck em +34 s
  reenviou 0xFFFFF7F7 com 0x0D2DA7.
- ERRO (na regra de imposição): em 14:19:43 e 14:20:47, conforme a missão avançava, o servidor reutilizou esses objetos (src 0x...35A000 agora contendo chave
  0xFFFFF7F7) e a regra de imposição ("qualquer dword 0x0D0000–0x0DFFFF") sobrescreveu 0x0D25D8 e 0x0D2BD4 (outros campos, provavelmente chaves de
  etapa) com 0x0D2DA7. Tudo nesta sessão após ~14:19 é inconfiável. Apenas cópia de teste; saves restaurados depois.
- Conhecimento: na sessão manual original, o servidor enviou NormalLearnKnowledgeListAck 2439 com 0x0F4A35 em t=204.3,
  quando etapa 0xF475E (a cena de encontro) executou suas ramificações 6,0,3,1; nesta sessão, 0x0F4A35 só veio em t=1019 (o jogador
  falando com ela). Dedução: 0x0F4A35 = conhecer Renee; vem da cena de encontro, que a reprodução apenas de diálogo pulou.
Deduções:
- Um convidado precisa da cena de encontro do anfitrião (ramificações de etapa) além da aceitação, ou NPCs permanecem desconhecidos.
- Forçar a variante do anfitrião na cópia da missão corrige apenas os slots do servidor; a visualização do cliente e o diálogo pendente de entrega
  mantêm o sorteio do convidado. Uma correção completa também precisaria do próprio sorteio (não encontrado: chamadas virtuais / código virtualizado)
  ou vários patches de memória e reescrita de mensagens S2C. A regra de imposição deve ser exata (principal +0x38, objetivos +0x30, apenas
  o valor sorteado, apenas logo após a aceitação), caso volte a ser usada.

## <a id="2026-10-20-1425-1505--looking-for-the-variant-pool-npc-ids-are-per-load-unattended-4-runs"></a>2026-10-20 14:25–15:05 — busca do conjunto de variantes; IDs de NPC são específicos de cada carregamento (sem supervisão, 4 execuções)
Objetivo (decisão do projeto): cada jogador conclui sua própria solicitação, mas ambos recebem a MESMA variante.
Observado:
- Varredura do conjunto (mission_watch=4: cada dword legível igual a uma das 12 variantes vistas até então): fora do mod, apenas 28
  ocorrências em ~5,8 GB, nenhum grupo de 3+ variantes em 1 MB. A maioria fica uma por registro numa grande alocação privada (as tabelas
  de dados carregadas), cada uma como `... u32 n | template | ptr | u32 size | u32 size | n | template+0x1C..` (registros separados, distantes).
  (Uma primeira execução "encontrou" um grupo de 12 variantes: a própria tabela de constantes do mod. Excluída desde então.)
- Duas reproduções (P2, P3) NÃO produziram missão: o servidor nunca confirmou SetQuestDialogObstacleReq para o ator 0xB01001C1.
  ActorLoadDataAck 2005 (ID em execução u32 em +3, chave estática de personagem u32 em +22, nome UTF-16 em +36) mostra por quê: 0xB01001C1
  era "Renee" na sessão manual, "Rhett" em P1 (a aceitação ainda funcionou!), "Owl" em P2 (falhou). A chave estática de Renee,
  0x01C29010, é a mesma nas seis sessões verificadas; seu ID em execução variou de 0xB01001BA a 0xB01001C1.
  Correção: stage_tracker mapeia chave estática <-> ID em execução a partir de 2005; gravações contêm "N runtime static"; a reprodução substitui
  pelo ID em execução do NPC nesta sessão (espera até 60 s para ele carregar). P4 com correção: aceita (variante 0x0D21C3, nova).
- Observação de leitura/gravação por hardware (modo 5) no dword de modelo dos registros de quatro variantes (0x0D2158, 0x0D2147, 0x0D219D,
  0x0D2150), thread do servidor, 3 s a partir da aceitação: nenhum acesso.
Deduções:
- O servidor aceita QuestDialogEndReq para uma chave de diálogo com qualquer ator que aceite como interlocutor (Rhett para
  diálogo de Renee funcionou; uma coruja não): NPC não está estritamente associado ao diálogo. O cooperativo ainda precisa enviar o NPC correto
  (chave estática -> ID em execução do convidado), ou o convidado pode aceitar de outro personagem.
- O seletor não lê esses registros de modelo; o conjunto é mantido em outra forma (tabela de grupos/listas que referencia
  variantes de outra maneira; a chave do modelo é buscada depois). Não sabemos onde.
Variantes distintas vistas até então (13 em 16 aceitações; 0x0D2158 duas vezes): 0x0D2147, 0x0D214C, 0x0D2150, 0x0D2153, 0x0D2158,
0x0D215D, 0x0D2197, 0x0D219C, 0x0D219D, 0x0D21A5, 0x0D21C3, 0x0D21C5, 0x0D2DA7.

## <a id="2026-10-20-1515--correction-the-request-variant-is-the-accept-time-there-is-no-variant-data--14-captures"></a>2026-10-20 15:15 — CORREÇÃO: a "variante da solicitação" é o HORÁRIO de aceitação; não existe variante (dados + 14 capturas)
Fonte 1: decodificação somente leitura dos arquivos de dados da cópia de teste, feita em uma sessão separada. Os scripts decodificadores e
tudo que extraíram NÃO estão neste repositório (dados do jogo), portanto essa fonte não pode ser conferida pelo repositório; os fatos
fornecidos estão incorporados aqui, e o formato é descrito para permitir repetir o trabalho:
- Índice `NNNN/0.pamt`: u32 crc | u32 paz_count | u32 ?; paz_count x {u32 idx, u32 crc, u32 size}; dois blocos de nomes (diretórios,
  arquivos), cada um u32 length + registros trie {u32 parent offset or 0xFFFFFFFF, u8 len, chars}; u32 n + pastas {u32 hash,
  u32 name offset, u32 first file, u32 count}; u32 n + arquivos {u32 name offset, u32 offset, u32 csize, u32 size, u16 paz,
  u16 flags}. Todos os 34 índices são analisados até seu fim exato (2.052.523 entradas).
- Nibble inferior de flags = compressão (0 nenhuma, 2 bloco LZ4 bruto); 0x30 = criptografado (arquivos semelhantes a XML e tabelas de strings; ChaCha20
  no exe, chave não recuperada). As tabelas do jogo (`gamedata/binarystaticinfo__/bin/*.staticinfoheader|body`) não são
  criptografadas nem comprimidas além de LZ4: cabeçalho = contagem, depois {u32 key, u32 body offset}; registro = u32 key,
  u32 name length, name, fields. Chaves estáticas começam em 1.000.000 em todas as tabelas, portanto uma chave não significa nada sem sua tabela.
- 0x0D2147–0x0D2DAB foram procurados como chaves nas 87 tabelas com índice de chaves e como u32 bruto em todos os 134 corpos
  de tabelas: ausentes (uma correspondência de bytes sem relação).
Fatos: Renee = NPC "Raine" (personagem 0x1C2, NOW_Unique_Raine_450).
Mission_HernandCastle_Raine (0x0F42D5) é UMA tarefa fixa: submissões 0xFFFFF7F8 (aceitar; dá Recipe_Fish_Porridge,
carne de peixe x15, trigo x5, sal x5, água x15), 0xFFFFF7F7 (conhecer a receita), 0xFFFFF7F6 (fazer Fish_Porridge), 0x0F4B06
(entregar Fish_Porridge x3). Sem conjunto, pesos ou sorteio nos dados. 0x0D2147..0x0D2DAB não são chaves em nenhuma tabela.
0x0F4440 é a chave de missão (Quest_Node_Her_HernandCastle_MerchantStory), não de diálogo; 0x869D0124 =
QuestDialog_HernandCastle_Raine_Start; 0x0F475E = etapa HerStore_Meat (cena do açougue); 0x0F4A35 = conhecimento sobre
Raine (conhecimento de personagem).
Fonte 2 (esta sessão, 14 capturas; valor SetExecuteTimeQuestDialogAck = valor da linha + 4):
- Reproduções simples, aceitação 42,6–43,9 s após GameLoadingStartReq: 860491–860514.
- Reproduções em que os diagnósticos do mod seguraram a thread do servidor na aceitação (varreduras de memória 4,1–4,3 s; interceptações de rastreio): 860570–860616, ou seja,
  ~+80 = ~4,2 s x 19.
- Sessão manual, 163 s mais tarde no mundo: 863659 (+~3150 = ~165 s x 19).
Dedução: o valor é o horário da aceitação no relógio do jogo (~19 unidades por segundo real), não uma variante aleatória. Todas as
conclusões sobre "variante" acima são RETIRADAS: a fixação RNG (13:15–13:50) não poderia importar; "forçar o modelo do anfitrião"
(13:55–14:25) gravou o horário de aceitação MAIS ANTIGO da sessão manual na missão do convidado (o "Fish Porridge" no cliente sempre esteve correto;
o horário forçado pode ter sido prejudicial); as varreduras de conjunto (14:25–15:05) procuravam um conjunto que não existe.
Ainda válido: reprodução de QuestDialogEndReq funciona sem diálogo aberto; NPCs devem ser convertidos por chave estática; a cena de
encontro faz Raine ser conhecida (0x0F4A35); a cópia de missão exe+0x1A9B4A0 e o layout do objeto (+0x38 = horário de aceitação).
Consequência para o cooperativo: o convidado recebe a mesma solicitação reproduzindo a cena de encontro + aceitação do anfitrião; o campo de horário de aceitação
difere por máquina e não deve ser comparado nem copiado. Unidade/taxa do relógio: desconhecida (~19/s; tempo do jogo?).
Lição: um valor interpretado como "chave de modelo" nunca foi conferido contra as tabelas de dados antes de servir de base ao trabalho.

## <a id="2026-10-20-1500-1530--the-guest-meets-raine-meeting-scene--accept-replayed-unattended-3-runs"></a>2026-10-20 15:00–15:30 — convidado conhece Raine: cena de encontro + aceitação reproduzidas, sem supervisão (3 execuções)
Arquivo de reprodução: ramificações (6, 0, 3, 1) da etapa 0xF475E da sessão manual + diálogo de aceitação (NPC convertido por chave estática) + linhas de
missão; criado da captura 12:42 (tools/re/rec_from_capture.py agora também grava linhas de ramificação).
Observado:
- S1: etapa 0xF475E existe em todo carregamento (PrepareSequencerAck ~t=63, com carregamento do ator Raine), não apenas perto dela.
  Ramificação 6 reproduzida -> em 9 ms StageOnBranchEventAck + NormalLearnKnowledgeListAck 0x0F4A35 (conhecer Raine) +
  StageBranchStateAck(1, 6). Ramificação 6 abriu a tela de loja no convidado (visto na tela: "parado na tela do
  comerciante"); ramificações 0/3/1 nunca foram enviadas e expiraram.
- Causa 1: a fila do convidado só enviava para uma etapa ociosa (estado 0, sem ramificação). Uma cena envia suas ramificações posteriores enquanto a
  etapa está ocupada. Correção (common/stage_sync.h): após concluir aqui a ramificação N do anfitrião, a próxima ramificação dele para essa chave
  vai para a instância parada em N (não ocupada). Teste unitário + verificação mutante (desativar faz falhar tests.cpp:1129). Um teste
  antigo alterado intencionalmente: ele verificava a retenção.
- Causa 2 (erro, também afeta sincronização de etapas em tempo real): StageBranchStateAck chega como payloads de 21, 29 ou 37 bytes (sessão
  manual: 2 / 27 / 39); stage_tracker exigia >= 25 e, portanto, perdia os de 21 e 29 bytes. Corrigido (>= 21).
- S3 com ambas as correções: mod enviou 6, 0, 3, 1 para a instância 0x19F do convidado; acks estado 1/6, 2/0, 7/3, 0/1 em 0,9 s;
  conhecimento 0x0F4A35 na ramificação 6; as três linhas de missão da aceitação iguais às da gravação (horário de aceitação não comparado);
  jogo vivo 30 s depois. Após a última ramificação, a etapa ficou ociosa (estado 0) na ramificação 1: agora contada como concluída quando a enviamos
  (teste unitário).
- Verificação de linha de missão: o campo de horário de aceitação (+14 na linha de tipo 5, +6 nas demais) não é mais comparado.
Ainda não verificado: se o convidado consegue entregar (precisa de uma pessoa para cozinhar Fish_Porridge x3 e falar com Raine) e o que a
tela de loja faz num convidado que não está junto da loja (S3 sem supervisão; ninguém olhou).

## <a id="2026-10-20-1515-1519--a-guest-style-accept-then-a-human-cooks-and-hands-in-completed-test-copy"></a>2026-10-20 15:15–15:19 — aceitação ao estilo convidado, depois uma pessoa cozinha e entrega: CONCLUÍDA (cópia de teste)
Configuração: saves no ponto de restauração; reprodução da cena de encontro da sessão manual (etapa 0xF475E: 6, 0, 3, 1) + aceitação, NPC por
chave estática; sem saída automática; uma pessoa continuou jogando (execução manual; nunca falou com Raine antes da entrega).
Observado (log + captura, t = s desde o início da captura):
- Reprodução: ramificações aplicadas 4, as três linhas de missão iguais às da gravação (exceto horário de aceitação), RESULT PASS.
- t=149.3 NormalLearnKnowledgeListAck 0x0F4D5E (Knowledge_Recipe_Fish_Porridge, da receita concedida na aceitação).
- t=180.1 missão 0xFFFFF7F6 (fazer Fish_Porridge), tipo 2 -> 5; missão de entrega 0x0F4B06 ativada.
- t=201.9 jogador abre conversa com Raine (ID em execução 0xB01001C2 neste carregamento); t=221.4 QuestDialogEndReq
  (Raine, missão 0x0F4440, resposta 11). Em 18 ms: NormalLearnKnowledgeListAck 0x0F4690 (Knowledge_Her_Raine = a
  recompensa de entrega nos dados), 0x0F4B06 tipo 2 -> 5, pai 0x0F42D5 aparece, SetExecuteTimeQuestDialogAck com
  0x31A2E3AF (QuestDialog_HernandCastle_Raine_Complete); em 227.4, as próximas missões (0xF4482, 0xFFFFF80A) aparecem.
- O jogo fechou normalmente (menu, "Terminate").
Dedução: um convidado que nunca conheceu a NPC e recebeu a solicitação apenas por reprodução consegue cozinhar e entregá-la; o servidor a conclui.
Aceitação por reprodução + entrega pelo jogador = "cada jogador conclui a sua própria, mesma solicitação".
Relato do testador (execução manual, 15:25): a missão foi concluída e a recompensa pareceu correta.

## <a id="2026-10-20-1540--correction-branch-6-does-not-open-the-shop-plan-for-live-accept-sharing"></a>2026-10-20 15:40 — CORREÇÃO: ramificação 6 não abre a loja; plano para compartilhar aceitação em tempo real
- Retirado: "ramificação 6 abriu a tela da loja no convidado" (seção 15:00, S1). StoreDataListAck (conteúdo da loja) nas
  capturas: no carregamento (t~14, ~28) em todas as execuções; em S1 também em t=236, ~170 s após ramificação 6, enquanto a cena estava presa
  após sua primeira ramificação; nunca em S2, S3 ou na sessão de entrega manual, em que todas as quatro ramificações executaram. O encontro
  manual original (12:42) também não teve nenhum perto da ramificação 6 (dados da loja em t=270, após a aceitação). Causa da tela da loja em S1:
  desconhecida (a cena presa é o vínculo provável).
- Entrega versus aceitação no anfitrião: a entrega (sessão 15:15) veio com RemoveItemToInventoryAck 2481 x2 e
  UseItemReq 2855 logo após a resposta; a aceitação (12:42) não teve remoção de item, apenas adições. Uma amostra de cada.
- Política de compartilhamento (decisão do projeto, 2026-10-20): missões de solicitação são aceitas em conjunto (convidado recebe a aceitação do anfitrião, incluindo a
  cena de encontro pela sincronização de etapas, para que a NPC seja conhecida); cada jogador cozinha e entrega a sua própria; entregas e recompensas
  não são compartilhadas. Observe que o alerta da página de captura de efeitos se aplica intencionalmente aqui: o servidor do convidado executa sua própria aceitação,
  portanto o convidado também recebe a receita e os ingredientes, como deseja a política.
- Testes das ferramentas upstream (tools/test_all.py, após mesclar main; cmake 3.31.6 de PyPI, com hash fixado, num venv do espaço de trabalho):
  9 de 11 passam; gamepool sai com 2 porque pula no Linux ("needs Windows") e o executor conta isso como falha;
  bots falha em test_specific_reasons pelo texto da mensagem ("'copies' not found in 'round 2: item count in the party is
  wrong ...'"). Nenhum toca em arquivos de Crimson Desert.

## <a id="2026-10-20-1550--live-quest-accept-sharing-protocol-11-one-pc-relay-test-pass"></a>2026-10-20 15:50 — compartilhamento de aceitação de missão em tempo real (protocolo 11), teste de relay em um PC: PASS
Código (cdmp): common/quest_accept.h (formato de transmissão QuestAcceptMsg; AcceptDetector do anfitrião: resposta seguida em até 400 ms
por mudanças de tipo de missão e sem RemoveItemToInventoryAck = aceitação, com remoção = entrega, não compartilhada; GuestAcceptQueue:
espera o NPC por chave estática, nosso ID de jogador e os tipos "anteriores" do anfitrião, envia obstáculo ativado x2 / resposta / desativado x2,
verifica tipos "posteriores", nunca duas vezes; já presente = pular). Testes unitários + 4 gêmeos mutantes (entrega compartilhada, sem verificação
anterior, sem verificação de já presente, ID de NPC mantido: cada um faz um teste falhar). mod/net/quest_share ([coop] quest_share, [dev]
quest_share_feed), RelKind::QuestAccept = 10 (apenas anfitrião -> convidado), protocolo 11. Linhas estritas de ramificação no arquivo de gravação
(parse_branch_line): um "%x" permissivo tinha lido "D 2621 ..." como chave de etapa 0xD (5 ramificações inventadas enfileiradas na primeira execução,
retidas porque tal etapa não existe; uma ramificação inventada pode travar o jogo). Seu gêmeo mutante NÃO foi detectado (a verificação de texto
extra também rejeita essas linhas): duas proteções, um teste.
Observado (relay cdmp_peer, um PC, saves restaurados, harness/echo_quest_test.sh): cena de encontro da alimentação de etapas aplicada como
6, 0, 3, 1 na nossa instância 0x19F; a aceitação chegou, foi enviada ao nosso servidor (5 mensagens) e verificada (accepted 1);
detector do anfitrião contou 0 aceitações (nossa resposta injetada não é considerada nossa: sem ciclo de eco); jogo vivo 30 s depois.
Ainda não: dois PCs; convidado longe do NPC (a espera); entrega pelo convidado após aceitação em tempo real.
