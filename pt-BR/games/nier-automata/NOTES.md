# <a id="nierautomata-working-notes"></a>NieR:Automata: notas de trabalho

Notas contínuas, mais recentes no fim. Observações, deduções, hipóteses e desconhecidos separados.

## <a id="game-identity"></a>Identidade do jogo

- Loja: Steam, aplicativo 524220, compilação 7020666.
- `NieRAutomata.exe` SHA-256: `5171bed09e6fec7b21bf0ea479dbd2e1b228695c67d1f0b478549a9be2f5726a`, timestamp PE 2021-06-23.
- Motor próprio PlatinumGames (nome desconhecido). Apenas nativo; lógica parcialmente na camada `hap` (classes `hap::BunkerAction`, `script_export`), história compilada para mruby (fonte: `shared/sdk/mruby.*` de AutomataMP).
- Sistema testado: Windows 11.

## <a id="existing-work"></a>Trabalhos existentes

- AutomataMP de praydog: https://github.com/praydog/AutomataMP. Jogadores, animações, Pod e inimigos por ENet com servidor Go.
- nier-coop, fork voltado à história para dois: https://github.com/egoriyNovikov/nier-coop. Projeto em `docs/COOP_CONCEPT.md`. História ainda não sincronizada.

## <a id="2026-10-18-isolated-test-copies"></a>2026-10-18: cópias de teste isoladas

Observado:
- Documents por `SHGetSpecialFolderPathA(CSIDL_PERSONAL)` (única importação shell); `%APPDATA%\PlatinumGames\NierAutomata\config.ini` por `getenv("APPDATA")` (string `APPDATA` em .rdata, importação `getenv`).
- Primeiro início de cada cópia regravava `SystemData.dat` real (byte 16 de 1 para 0; restaurado do backup). Process Monitor identificou **NVIDIA App**, não jogo. `nvcontainer.exe` inicia `NvBackend\ApplicationOntology\OAWrapper.exe -a nier_automata -p <new install dir> -s`, que "otimiza" nova instalação gravando Documents real. Redirecionamentos no jogo não impedem outro processo. Correção: desligar otimização automática NVIDIA ou reutilizar pastas.
- Steam Auto-Cloud envia pasta real quando cópia com mesmo appid sai; arquivo danificado também vai à nuvem. Restaurar antes de sair. Steam não sincroniza lançamento de executável iniciado externamente.
- Guarda de escrita `NtCreateFile` (recusa Documents real, `%APPDATA%\PlatinumGames` e instalação da loja) com ambos redirecionamentos: três execuções (título, salvamento carregado), zero escritas bloqueadas e arquivos reais intactos.
- Demais escritas externas: caches NVIDIA, shaders D3D, log da sobreposição Steam.
- Duas cópias simultâneas (mod renomeia evento único `NieR:AutomataEvent`).
- `data\*.cpk` por hardlinks; só leitura.

## <a id="2026-10-18-test-bot"></a>2026-10-18: bot de teste

- Controle XInput virtual 0 (hook `XInputGetState` em `xinput1_4.dll`) basta do título ao mundo: botão, Continue, escolher salvamento, Yes, Start Game. Salvamento concluído oferece Chapter Select.
- Capturas internas copiando buffer D3D11 no hook de apresentação, sem área de trabalho.

## <a id="2026-10-18-story-phase"></a>2026-10-18: fase da história

Observado na compilação 7020666:
- `.text` criptografado em disco (SteamStub, `.bind`). Buscar referências na memória ativa.
- Fase é string `16_AB_bunker_Order` (Bunker, salvamento inicial A) ou `60_05_AB_Forest_Castle` (concluído no Resistance Camp). Mesmo nome em quatro globais: base + `0x13ecc34`, `0x13f8548`, `0x145b6a8`, `0x1495548`.
- `+0x1495544` é int32 antes do nome (256 no primeiro, 512 no segundo), comparado a `0x100`.
- Assinatura: `8b 3d ? ? ? ? 81 ff 00 01 00 00 75 ? 48 8d 15 ? ? ? ? 48 8d 0d` (mov edi,[id]; cmp edi,100h; jnz; lea rdx; lea rcx,[name]).

Deduções:
- Nomes seguem lista LiveSplit v1.01 (`00_85_A_RobotM_Pro_2ndArea`, ...): https://github.com/Henny022/NierAutomataSplitter. Endereços desse divisor não se aplicam.

Desconhecidos:
- Significado do int32 antes do nome. Qual das quatro cópias o jogo trata como fonte.
- Como trocar fase (chamada Chapter Select).

## <a id="2026-10-18-automated-co-op-smoke-test"></a>2026-10-18: teste básico cooperativo automatizado

- Duas cópias num PC/conta Steam: ambas carregam mesmo salvamento pelo bot; uma Host Game (servidor Go), outra Join Game em 127.0.0.1. Verificações: sessão, papéis, cada um vê outro a até 3 m da posição declarada, mesma fase, host 2B e cliente assume 9S. PASS (0,12 m e 0,03 m).
- Pressões cegas temporizadas falharam duas vezes (perda no título deslocou sequência, entrando em License ou Exit Game > Yes). Reconhecer tela antes de cada pressão resolveu. Comparar quadro todo insuficiente (título/menu diferem ~5/255 em média); comparar cabeçalho e centro do menu.
- Bot não deve executar no hook de apresentação: jogo deixou de apresentar (janela sem responder) na entrada de nome alcançada por erro; bot dependente ficou silencioso.
- Após usuário desativar "Automatically optimize newly added games" NVIDIA, primeiro início da pasta nova slot4 ainda chamou `OAWrapper.exe ... -g c` (ler), sem `-s` (escrever); SystemData.dat intacto.

## <a id="2026-10-18-story-flags-scene-states"></a>2026-10-18: indicadores da história (estados de cena)

Observado em 7020666:
- Scripts definem/limpam por `SceneStateSystem.set` / `.reset` (tabela encontrada por CRC32 de "Class.method", `sdk::ScriptFunctions` AutomataMP). Argumento `hap::SceneStateName const&` aponta CRC32 em +0x20, nome curto em +0x38: `q410/REQ`, `hacking_state/last_9S`, `p300_PV_block_off`, `em2100/DIE`, `Unlock_RCtoAP`.
- Scripts chamam `set` todo quadro (~4000/min), capítulo limpa ~1500. Registrar só mudanças reais, último valor por CRC.
- Chapter Select concluído, Ch. 02-01 como 2B: `30_AB_Ruined_City_ForcedLanding`, identificador 256. Menu pede 2B/9S, escolhendo A/B nos compartilhados.

## <a id="2026-10-18-cutscenes-story-events"></a>2026-10-18: cenas (eventos de história)

Observado em 7020666:
- Vídeos `movie/ev%04x.usm` (formato .rdata); eventos montam `ev%04x_Start`/`ev%04x_End` do identificador. Código `mov r8d, [rdi+4]; lea rdx, <format>; lea rcx, [rsp+20h]; call sprintf`, mesmos bytes Start/End; interceptar ambos, distinguir formato apontado por lea.
- Chapter Select 03-03 (Battle with Adam): `Event start ev0250` (nascimento Adam, ~57 s, "Hold to Skip"), `Event end ev0250`, `ev0251` inicia/termina imediatamente. Hook do formato de vídeo não disparou.
- Busca estilo Cheat Engine (capturas dentro/fora de duas cenas, seções graváveis) deixou 23 bytes candidatos sem vencedor; interceptar início/fim mais simples, dá identificador.

## <a id="2026-10-18-route-and-chapter-select"></a>2026-10-18: rota e Chapter Select

Observado em 7020666:
- Rota/herói são indicadores: `Route/A`, `Route/B`, `Route/C`, `PL/2B`, `PL/9S`, `PL/A2`. `SceneStateSystem.has` informa rota. Capítulo compartilhado como 2B dá `Route/A` + `PL/2B`, 9S dá `Route/B` + `PL/9S`; carregar ambos salvamentos A dá `Route/A` + `PL/2B`.
- `this` de `SceneStateSystem.has` deve ser objeto recebido pelas chamadas nativas de `SceneStateSystem.set`. `SceneStateSystem::get()` de AutomataMP (categoria `@SceneState`) erra 8 bytes nesta compilação; `has` falhou.
- Confirmação Chapter Select (base + `0x95cb30`): lê segmento em tabela de entradas 0x54 bytes (id int16 +0xc, nome +0xe, herói ou -1 +0x4), define herói/rota, chama `0x9c5a00(id, phase name, n)` que grava global e limpa história, depois define byte lido pelo laço para carregar mundo. Argumentos iguais 2B/9S; escolha só nos indicadores.
- Carregar salvamento copia fase dos dados, sem `0x9c5a00`.
- Encontrado por interrupções de hardware internas (registradores em toda thread por `SetThreadContext`, manipulador vetorial registra instrução, pilha por `RtlVirtualUnwind` sobre `.pdata`, execução registra rcx/rdx/r8/r9). Sem depurador anexado; SteamStub não interferiu. Uma execução dá cadeia completa de quem grava global.

Deduções:
- Chapter Select só salta a inícios e existe em salvamento concluído; não alinha livremente a história entre jogadores.

Desconhecidos:
- Mudança durante jogo normal (bot ainda não alcançou natural).
- Se `0x9c5a00` com byte de carregamento funciona dentro do mundo.
- Significados de `n` (0xf no segmento escolhido, `51_AB_MainDesert`) e identificador 256/512.

## <a id="2026-10-18-talking-to-the-commander-story-step-inside-a-phase"></a>2026-10-18: conversa com Commander (etapa dentro de fase)

Observado em 7020666, salvamento "Test", `16_AB_bunker_Order`, objetivo "Reboot: Speak with the Commander":
- Bot teleporta junto ao NPC (posição na lista + `Pl0000.setPosRotResetHap`, voltado para ele); Commander única com modelo `0x11020`. Segurar B próximo inicia conversa.
- Conversa termina com novo marcador, mas fase, indicadores `SceneStateSystem.set` e eventos não mudam. Etapas internas guardadas em outro local.
- Sem foco pausa conversa ("PAUSED"), linhas não avançam sozinhas; A avança.
- Teleportar a posição suposta do hangar derrubou 2B do Bunker no espaço; só posições conhecidas.

Desconhecidos:
- Onde missão atual e etapa ficam.

## <a id="2026-10-18-where-the-story-step-is-stored-does-the-clients-game-follow-the-hosts-conversation"></a>2026-10-18: onde fica a etapa; cliente acompanha conversa do host?

Observado em 7020666, "Test", `16_AB_bunker_Order`; offsets da base:
- Comparação de seções graváveis (`snap`/`filter`): duas ociosas antes, uma durante, duas depois; só bytes estáveis antes, diferentes durante, estáveis depois. Duas execuções, ~1.600 bytes comuns; quase tudo floats de câmera/matriz, tabela de ponteiros e última fala (`1010_S0030_G0200_001_a2b`).
- Um int32 mudou igual: `+0x14952c8`, 130 antes, 140 depois; bloco de int32 -1 (0xFFFFFFFF).
- Interrupção de escrita (`watch`) capturou duas na próxima conversa em `+0x9480b6` (`mov [rip+...], eax`, `89 81 98 00 00 00 89 05 ? ? ? ? 89 af 54 06 00 00`). Valor de campo pendente (`[obj+0x650]`, indicador `[obj+0x654]` limpo pelo código); também escrito em `[[obj+0x130]+0x98]`.
- Referências: começo de história por fase Chapter Select (`+0x9c5a00`) grava -1 (`+0x9c5c0c`); `+0x8dd2b7` também -1; `+0x921f03` lê.
- RTTI `QuestManager` com `StaticArray<sQuestState, 30>`/`StaticArray<sQuestMsgInfo, 100>`, instâncias `.data` pelas vtables (`find` novo); nenhum byte mudou na conversa.
- Duas cópias em sessão, ambas Test/130: host conversa, vira 140 e objetivo Gathering Intel; cliente fica 130 sem conversa/objetivo novo. `tools/qa/coop_smoke.py --scenario commander` no fork do usuário, RESULT: PASS (host 130 para 140, cliente 130 para 130).

Deduções:
- Global é progresso interno (etapa): início reinicia, conversa move.
- Conversa do host não chega sozinha; mod precisa transmitir resultado.

Hipóteses não verificadas:
- Etapas aumentam de dez, conforme numeração de pontos PlatinumGames.

Desconhecidos:
- Objeto com etapa pendente e função definidora a chamar no cliente.
- Missão da etapa; se só alterá-la dá novo objetivo.
- Se etapa muda em transição natural (ainda não alcançada).

Armadilhas:
- `bot.load` às vezes escolhe errado (tecla perdida?): 2 de 9 sessões carregaram outro, uma `60_05_AB_Forest_Castle` em vez de Bunker. Conferência detecta; repetições passaram.
- Primeiro B perto da Commander pode anteceder indicação; cenário tenta duas vezes. A após fim faz 2B pular; parar assim que etapa mudar.

## <a id="2026-10-19-the-story-step-comes-from-the-phases-action-graph-a-natural-phase-change"></a>2026-10-19: etapa vem do grafo de ações; transição natural

Observado em 7020666, "Test", `16_AB_bunker_Order`; offsets da base:
- Etapa pendente em objeto estático `+0xf68af0` (primeiro membro `StaticArray<UIPlHudManager::sUICtrl, ...>`, provavelmente HUD): valor `[+0x650]`, indicador `[+0x654]`. `+0x8fae70(int step)` guarda sob trava se diferente de 0 e do pendente, ativa indicador; atualização HUD `+0x947f80` copia à global no próximo quadro. Início chama com -1 (`+0x3d59a7`).
- Mod chamando `setstep 140` em 130 nada muda: jogo chama todo quadro com 130 (`+0x3e37f4`, `ecx = [rbx+0xb4]`), restaurando imediatamente.
- `rbx` é `hap::HapGoalLocationAction` (RTTI por vtable com `rtti` novo), ação do grafo mantendo marcador no alvo (Commander, objeto `NPC`); etapa em `+0xb4`. Mesma função define alvo (`+0x8141a0`, gerenciador `+0x125df80`; posição tripla `+0x1268920`).
- Grafo: 24 `hap::Action*` (`DynamicArray<Action*>` em `+0x28`): condições, `SendCommand`, `MemorySaveAction`, `HapGoalLocationAction`, `AreaAction`, `CameraAction`, `DelayAction`, outras. Cada ação tem identificador hash32 `+0x18` estável, indicadores `+0x1c` (byte `+0x1e`: 0x20 iniciou, 0xa0 concluiu, 0 não chegou) e hash de estado `+0x20` (`0x26b80d1f` concluído).
- Conversa conclui `ConditionBlock` `0x4c4e6dc1`, objetivo antigo `0x883b60bd`/130 e seguintes; começa objetivo `0x39a20c1d`/140 no hangar e `AreaAction` `0xa9864814`. Estado escrito por `+0x3ec550(action, state)` (hash, indicador concluído para `0x26b80d1f`, notificação pelo id); `+0x356080` encapsula.
- Caminhando: `AreaAction` termina no outro extremo do piso; junto à unidade de voo host (`0x10010`), cena `ev0200` inicia, etapa 140 para -1; após carregar, `20_AB_buker_Aerial_battle` (grafia do jogo). Laço `+0x3aaa30` chama `+0x9c5d20()`, copiando novo bloco 0x399c0 bytes (nome e etapa).
- Sessão com host andando e cliente parado: host muda fase; cliente fica `16_AB_bunker_Order`/130, sem cena. Cliente mostrou `loading=1` por segundos simultaneamente. `tools/qa/coop_smoke.py --scenario hangar` no fork, RESULT: PASS.

Deduções:
- Global só espelha objetivo atual. Para acompanhar, mover grafo cliente (concluir mesmas ações por id), não escrever etapa.
- Transição natural do host também não acontece no cliente.

Hipóteses não verificadas:
- Concluir `ConditionBlock` `0x4c4e6dc1` no cliente por `+0x3ec550` (estado `0x26b80d1f`) faz grafo seguir igual.
- `loading=1` breve é reação do mod à transição, não jogo.

Desconhecidos:
- Condição de `ConditionBlock` (fim da conversa, indicador); conteúdo adicional do segundo argumento `+0x3ec550` além do hash (`+0x8`, `+0x10`).
- Segurança de concluir ações externamente.
- Por que interrupção no nome não capturou nada (threads posteriores sem armamento?).

Armadilhas:
- Bunker gira: coordenada salva pode virar espaço vazio num minuto. Teleportar à posição atual da entidade, lida antes de `goto`.
- `bot.load`: cursor em New Game chegou a confirmação de apagar/criar (No selecionado); outra vez apontava Test mas carregou outro. Provável, não comprovado: mouse real parado sobre janela realça item. Cópias agora sem mouse (mensagens descartadas, `GetCursorPos` longe), bot confere realce e ponteiro antes de A, recua de New Game. Nove carregamentos corretos depois.
- `find` levou mais de 30 s por ler memória GPU de escrita combinada; ignorar `PAGE_NOCACHE`/`PAGE_WRITECOMBINE` reduziu a ~2 s.

## <a id="2026-10-19-evening-moving-the-clients-story-graph-the-player-character-asks-for-the-phase-change"></a>2026-10-19 (noite): movendo grafo cliente; personagem pede transição

Observado em 7020666, "Test", `16_AB_bunker_Order`; offsets da base:
- Executável criptografado no disco (Steam DRM); o código foi lido da memória de uma cópia de teste em execução.
- `+0x356080(action, state hash, param)` é caminho nativo de mudar estado. Monta descrição `{ +0x0 state hash; +0x8 a ref-counted state object looked up by the hash (+0x3eddd0); +0x10 param }` (`+0x3cfeb0`) e passa a `+0x3ec550`. Retorna false se hash/parâmetro iguais; senão guarda hash em `[action+0x20]`, objeto `+0x28`, parâmetro `+0x30`, define `0x800000` nos indicadores (`+0x1c`) para `0x26b80d1f`, notifica pelo id. Dezenas de milhares de chamadas em minutos, quase sempre sem alteração.
- Grafo pertence a nó nomeado pela etapa (`M1010_S0030_GM`). Grafo: hash `+0x18` (`0x312961f6` em todas), vetor `+0x30`, quantidade `+0x38`. Ações apontam de volta em `+0x8`.
- Uma cópia sem conversar: concluir `ConditionBlock` `0x4c4e6dc1` por `+0x356080` move 130 para 140, mostra Gathering Intel, 9S fala próxima linha; grafo segue como após conversa.
- Concluído não é estado único: maioria `0x26b80d1f`; `AreaAction` após Commander terminou `0x4a063532` (uma cópia) ou `0xcc7564cb` (cooperativo), indicador definido fora de `+0x3ec550`. `+0x3aaaf0` compara com `cee3b8c9, 26b80d1f, a09a3421, b649891d, ecbccdf8, ee3e0a30`.
- Esse `AreaAction` cobre início de Test (entrada do hangar), não outro extremo; cena junto à unidade só depois. Cenário de ontem caminhava e alcançava por acaso; hoje falhou duas vezes em duas.
- Personagem pede transição, não `SendCommand`: ~40 s de voo após `ev0200`, manipulador `Pl0000` (`+0x50d6b9`, após comparar float e estado `0x6bff8489`) chama `+0x81a440`, definindo `[+0x11ea898] = 1` (estado principal). Laço (`+0x83c8f0`) chama `+0x3aaa30`, `+0x9c5d20`, que recebe bloco de `[+0x1421f08]` (começa "TY"). Pilha: `+0x50d6be <- +0x503960 <- +0x42c574 <- +0x4a048f <- +0x270cae`. Mais chamadores de `+0x81a440`: `+0x47cff1`, `+0x4ab623`, `+0x691315`, não examinados.
- Fork do usuário agora move grafos (`StoryActionSync`, `ID_STORY_ACTION`): hook `+0x3ec550` aprende grafos; host inspeciona por quadro, envia ações cujo indicador concluído surge (fase, hash grafo, id ação, hash estado); cliente aplica quando própria ação iniciou (tolerância 0,5 s para comandos autoconcluídos fazerem trabalho). Dois clientes (`tools/qa/coop_smoke.py`): `--scenario commander` acompanha 140; `--scenario hangar` também reproduz `ev0200`, muda `20_AB_buker_Aerial_battle`; RESULT: PASS, outros três também. Host enviou 47 ações de ~20 grafos no hangar (cena tem próprios).
- Sem transferência, indicador de carregamento cliente não foi escrito durante transição host (interrupção, zero acertos). `loading=1` breve da manhã não reapareceu.

Deduções:
- Mover por ids funciona sem saber condições; cliente reproduz falas, cena e transição próprias.

Hipóteses não verificadas:
- Interceptar `+0x81a440` retém mudanças próprias do cliente até host.

Desconhecidos:
- Significados `M1010`/`S0030` (missão/etapa?) e quem preenche buffer TY.
- Outros três chamadores de `+0x81a440`.
- Efeito em missões secundárias e entrada no meio da fase.

Armadilhas:
- Interrupção em `+0x3ec550` enche buffer instantaneamente (muito frequente); observar chamador.
- Mudar estado só na thread do jogo (`hapset` do bot pelo hook por quadro).

## <a id="2026-10-20-holding-the-clients-phase-change-graph-names-personal-graphs"></a>2026-10-20: retendo transição cliente; nomes e grafos pessoais

Observado em 7020666; offsets da base:
- `+0x81a440` são duas escritas e `ret`: `[+0x11ea89c] = 1`, `[+0x11ea8a0] = 0` (estado principal). Encontrada pela chamada em `Pl0000`: `ba 89 84 ff 6b 48 8d 4c 24 60 e8 ?? ?? ?? ?? 89 74 24 70 48 8d 54 24 60 48 8b cf e8 ?? ?? ?? ?? 90 48 8d 4c 24 68 e8 ?? ?? ?? ?? 90 e8` (último `e8` chama, retorno `+0x50d6be`).
- Outros: `+0x691314` após tocar `BGM_Player_Die` (junto de `BGM_Sleep_In`) em `+0x690d20`; `+0x47cff0` em `+0x47a9c0`, função de estado chamada por 12 manipuladores, ramo estado `0xc5` e `[+0x10668] <= 0`; `+0x4ab622` em `+0x4aaf10` (de manipulador `Pl0000`), verifica modelo (`0x10200`, `0x10203`).
- Vida zero não inicia morte; cair sob Bunker não termina, então chamador de morte não observado.
- Hook no fork retém pedido cliente `+0x81a440` de `+0x50d6be` na sessão, libera quando host muda. Duas cópias: cliente pediu 4,9 s antes; liberado 0,04 s após fase host chegar; ambos `20_AB_buker_Aerial_battle` (`coop_smoke.py --scenario hangar`, RESULT: PASS).
- Grafos nomeados: `[+0x0]` para descrição, `[+0x28]` da descrição para nome Shift-JIS terminado em zero. Bunker: `M1010_S0030_GM` (etapa), イベント再生 (reprodução de evento), フェーズイベント再生 (evento de fase), 敵セット (conjunto inimigo), メール (correio), 武器屋/道具屋 (loja de armas/itens), アイテム (item), outros.
- Mundo aberto, concluído `60_05_AB_Forest_Castle`: ~100 grafos, maioria objetos: 宝箱 / 共通宝箱 (baús), 採取ポイント (coleta), 釣りエリア (pesca), 自販機 (venda automática), ロボショップ (loja robô), 実績 (conquistas), ファストトラベル (viagem rápida), ベッド (cama), 依頼者_q210 (doador da missão q210). `+0x1c` é 0 na maioria, `0xffffffff` em 共有スクリプト (script compartilhado), 3, 0xa, 0x3e8...0x3ec em alguns (desconhecido).
- Primeiro ponteiro da descrição não é pai: nomes `q150/RUN_13`, `q340_1_1/REQ`, `DLC_plato/3` (parecem estados de cena).
- Host mantém pessoais os grafos com essas palavras ou `q` + três dígitos; mundo aberto enviou 49 ações, reteve 14 (lojas, máquinas, coleta, conquista); `--scenario world` PASS.
- Entrar após conversa recebe todas as ações concluídas da fase; cliente 130 para 140 sem conversar (`--scenario midjoin`, PASS).

Deduções:
- Reter pedido basta nesta transição; é indicador, pode liberar depois pelo hook por quadro.
- História não é só `M####`: cena e transição vêm de grafos de eventos/inimigos; filtrar só missão principal quebraria voo. Excluir palavras pessoais conhecidas o mantém.

Hipóteses não verificadas:
- `+0x47cff0` é morte em outra forma (voo, invasão), `[+0x10668]` vida.
- Grafos secundários sempre nomeados `q###`, como doador.

Desconhecidos:
- Objeto responsável pelo grafo (missão/layout), para distinguir sem lista de palavras.
- Se história muda sem `+0x81a440` (algum `SendCommand`).

Armadilhas:
- Coordenada fixa da Commander falhou (bot falou com soldado ao lado); usar entidade `0x11020` na posição atual.
- Com terceira cópia ativa, segunda saiu ao iniciar nas duas tentativas ("AutomataMP shutting down" após hooks DX12); duas iniciaram. Causa não examinada.
- Nomes nos logs Shift-JIS: ler cp932; console Windows cp1251 não os imprime.

## <a id="2026-10-21-the-bunkers-ring"></a>2026-10-21: anel do Bunker

Observado em 7020666, "Test", `16_AB_bunker_Order`, duas cópias em sessão:
- Bunker é anel no eixo x (centro y 188,55, z -0,68). Ao caminhar, controlador (`+0x83bb60`) gira anel sob herói, mantido embaixo. Salas, NPCs, unidades do hangar giram juntos. Teleportar não gira.
- Objeto anel é comportamento da entidade `0xf1200` (classe `Bunker`). Linhas da matriz (0, cos a, -sin a), (0, sin a, cos a), (1, 0, 0); ângulo a também em `+0x94`.
- Herói no cliente é representante do host, então ele girava anel cliente. Coordenadas iguais eram lugares diferentes: Commander girava no cliente, parada no host.
- Escrever posição a mais de 5 m não foi aceito pela física; representante corria ~10 s ao alvo e terminava 2 a 5 m sob piso. `Pl0000.setPosRotResetHap` move imediatamente.
- Controlador para com `[ctrl+0xe8]`. No fork egoriyNovikov/nier-coop, controlador cliente só lembra posição do herói, recebe ângulo host e posições são transmitidas no referencial do anel. `coop_smoke.py --scenario commander`: ângulos iguais, representante a 0,04 m do host (PASS).

Deduções:
- Toda posição compartilhada relativa ao anel; só um jogo o controla.

Armadilhas:
- Clone 2B em captura era androide YoRHa com marcador de missão, não segundo representante.

## <a id="2026-10-22-flying-from-the-bunker-together"></a>2026-10-22: voando juntos do Bunker

Observado em `20_AB_buker_Aerial_battle`, duas cópias; host saiu do hangar e cliente seguiu:
- Cada jogo voa duas unidades (`BehaviorFlightUnit`, `0x10010`): herói dirigido pelo jogador e parceiro da história pela IA em formação. Cliente dá unidade do herói ao próprio herói.
- Mesmas coordenadas perto da origem; posição remota utilizável diretamente.
- Colocar representante no lugar do parceiro impedia virar batalha vista de cima. Solo, câmera começa 20 m e vai ~46 m em 12 s; sessão ficava 13 a 16 m, parceiro continuava mecha disparando para baixo. Sem assumir parceiro, voo normal.
- IA puxa unidade à formação ~0,3 m/quadro; suavização deixava erro 2 m. Definir por quadro mantém mediana 0,01 m.
- Quem não dirige é abatido; jogo repete bloco de checkpoint ~50 s (solo também).

Deduções:
- Script espera IA. Parceiro permanece nativo; só sua unidade acompanha remoto (fork egoriyNovikov/nier-coop, `coop_smoke.py --scenario hangar` verifica posição e câmera além de 35 m, PASS).

Desconhecidos:
- Transmitir rotação/inclinação, transformação mecha, disparos (não sincronizados).

## <a id="2026-10-22-the-next-block-can-have-the-same-phase-name"></a>2026-10-22: próximo bloco pode ter mesmo nome de fase

Observado:
- No voo, pede próximo bloco (`+0x81a440`) repetidamente; todos `20_AB_buker_Aerial_battle`.
- Fork retinha pedido até nome host mudar (2026-10-20). Nunca mudou; cliente esperou no escuro por 1,5 min.

Deduções:
- Carregar próximo bloco é contador, não mudança de nome. Host envia quantidade carregada; cliente libera quando cresce, mesmo se host carregou segundos antes do pedido. `--scenario hangar` verifica ausência de pedido retido.

## <a id="2026-10-22-talking-to-an-npc-the-clients-story-talks"></a>2026-10-22: conversas com NPC; história cliente

Observado em 7020666, offsets da base:
- 9S cliente podia segurar B na Commander e conversar inteiro; etapa 130 para 140, host 130 (grafos divergem).
- Interação chama `+0x7cfbb0` por quadro com alvo (e variante `+0x7cfdb0` com medidor); pressionar chama virtual 125 (`[vtable+0x3e8]`) do comportamento alvo. `BehaviorAppBase` (`+0x41e860`, assinatura `40 53 48 83 ec 40 48 c7 44 24 20 fe ff ff ff 48 8b d9 ba fb 0e cb 28`) posta `ON_TALK` (hash `0x28cb0efb`); `NPC` (`+0x6ff040`) verifica estado e salta. Interrupções: posição 125 uma vez por pressão, consulta por quadro.
- Indicador que `BehaviorAppBase.setTalkDisable` / `setTalkEnable` escrevem é `[behavior+0xbcc]`, lido pela consulta.
- Scripts mruby, classe `EntityPuid` (`talk?`, `signal?`, `startTalk`, `endTalk`, `setTalkMark`, ... em `+0x2fec90`). `talk?` (`+0x337640`) verifica `ON_TALK` e marca tratado. `startTalk` (`+0x336b30`) define parceiro em `hap::TalkMan` (estático `+0xfbf630`, `[+0x668]` conversando, `[+0x66c]` identificador do parceiro). Interrupções em `talk?`/`signal?` não dispararam na Commander; escrita em `TalkMan` capturou `startTalk` de fibra retomada de `hap::SceneStateObj`.
- `hap::TalkMan` guarda NPCs com marca em `[+0x688]` (vetor), `[+0x690]` (quantidade). Vazio no Bunker/130 e mundo aberto concluído.
- `[behavior+0x66c]` identifica layout que colocou objeto (`0x6aae9bcb` Commander). Objetivo da Commander é `hap::HapGoalLocationAction` de `M1010_S0030_GM`, `[+0xc0]` tem mesmo id; objetivo de lugar tem `0xffffffff`.
- Fork ignora virtual 125 no cliente quando objetivo iniciado/não concluído de grafo não pessoal aponta layout alvo; mostra dica para host agir. `coop_smoke.py --scenario client_talk`: B do cliente não inicia, fica 130; host conversa, cliente acompanha 140 (PASS).

Deduções:
- NPC de história identificado pelo objetivo, sem lista. Comerciantes/conversa informal sem objetivo continuam usáveis.

Desconhecidos:
- Doador antes de aceitar missão, ainda sem objetivo. Não visto; cópias sem salvamento adequado.
- Onde escolha de diálogo ocorre (conversa permitida ainda pode ter escolhas).

## <a id="2026-10-22-phase-changes-outside-the-request"></a>2026-10-22: transições fora do pedido

Observado:
- Chapter Select inicia por `+0x9c5a00` (de `+0x95cf46`), não `+0x81a440`/`+0x9c5d20` (interrupções nos três durante seleção do título).
- `SaveState.loadFromMemory` salta a `+0x9c5d20` (`+0x38e9a0`), função que aplica bloco seguinte (`bool()`, verifica `TY` em `[+0x1421f08]`). Script pode mudar fase sem pedido.
- Outros escritores do estado (`[+0x11ea89c]`) só zeram ou são o próprio laço.
- Vida aparente (`[behavior+0x858]`, retorno `getHp`) zero não inicia morte nem Bunker nem mundo; barra cheia. Precisa dano.

Deduções:
- Além de `+0x81a440`, `SaveState.loadFromMemory` é caminho conhecido de transição no mundo. Fork agora registra chamadas (substituição na tabela de scripts, código intacto).

Desconhecidos:
- Quais scripts chamam `SaveState.loadFromMemory` e se `+0x691314` é morte real (precisa morrer lutando).

## <a id="2026-10-23-a-death-in-co-op-the-real-health-quest-givers-flight-unit-angles"></a>2026-10-23: morte cooperativa, vida real, doadores, ângulos de voo

Observado:
- Sessão no deserto (`51_AB_MainDesert`, dois clientes num PC): 9S morreu contra inimigo; host foi à morte também, embora 2B longe/viva. Ambos pediram próxima fase da mesma chamada, retorno `+0x4ab627`; host 24 ms primeiro.
- Vida real `[behavior+0x10668]`, copiada a `+0x858` por quadro (`+0x428b96`); por isso escrever `+0x858` não dura.
- Doador secundário antes de aceitar é colocado por ação do grafo (`EntityLayoutArea` / `EntityLayoutAction`). Entrada de layout (busca id `+0x3d8240`) aponta `EntityLayoutsMixin` em `[+0x38]`, dentro da ação em `+0x50`. Conferidos 23 NPCs Resistance Camp: todos de grafos `オブジェ配置` (posicionamento de objetos); q210 tem próprio `依頼者_q210` (requester_q210).
- `BehaviorFlightUnit` mantém ângulos Euler (`+0x90`) e quaternion (`+0x60`) em zero enquanto gira. Orientação em outro lugar, candidato osso raiz do modelo.

Deduções:
- Morte cliente chegou ao host por representante (2026-10-29).
- Doador identificável pelo grafo que o colocou (`qNNN`), sem lista de NPCs.

## <a id="2026-10-29-the-heros-death-shared-death-in-co-op"></a>2026-10-29: morte do herói; morte compartilhada

Observado:
- Estado `[Pl0000+0x670]`; atualização seleciona por ele (`+0x503968`, 0xd4 estados). `start_animation` (virtual `+0x90`) o define; "animações" enviadas por AutomataMP são esses estados.
- `0x33`, `0x34`, `0x35` são mortes, seguem a `0x36` (`+0x4aaf10`). `0x36` monta Body Report e, se virtual `+0x350` é true (controlado por jogador), pede próxima fase em `+0x4ab622`: Game Over. Modelos 9S `0x10200`/`0x10203` só escolhem texto.
- Jogo mata assim (`+0x47bf1a`, `+0x42a5a4`): `+0x10668` e `+0x858` = 0, `start_animation(0x35, 0, 0, 0 or 1)`. Repetir pelo mod dá queda, relatório, Continue e recarga completos. Bunker carrega Game Over imediatamente, sem relatório.
- `[Pl0000+0x10364]` float é invulnerabilidade em quadros. `setEventMuteki` (`+0x4eca50`) põe 300, `changePlayer` 60; dano (`+0x47a9c0`) compara.

Deduções:
- Morte dupla de 2026-10-23: `Die` cliente (`0x35`) transmitido como animação; representante host (marcado controlado para entrada) morreu e chamou Game Over host.
- Fork envia morte em pacote próprio. Representante não recebe estados de morte, mantém invulnerabilidade alta. Outro jogo mata próprio herói como nativo; Game Over cliente espera host. Bot confere em duas cópias (`coop_smoke.py --scenario death|death_world|death_host`).

Desconhecidos:
- Aparência de acertos inimigos no representante invulnerável (sem dano, mas reação?). Precisa luta.
- `+0x691314`, outro chamador perto de `BGM_Player_Die`, ainda não visto.
