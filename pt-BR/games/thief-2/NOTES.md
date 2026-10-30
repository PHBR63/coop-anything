# <a id="thief-ii-the-metal-age-co-op-notes"></a>Thief II: The Metal Age: notas cooperativas

Notas de trabalho escritas durante a execução. Observações, deduções, hipóteses e desconhecidos separados.

## <a id="game-identity-rule-5"></a>Identidade do jogo (regra 5)

| Campo | Valor |
|---|---|
| Loja | Steam, aplicativo 211740, buildid 1970 |
| Executável original | `thief2.exe` (OldDark 1.18 + ddfix), SHA-256 `f21cfc6d5fa73404637621e06cb20cade31a733508692fa8f7296a078dc74386` |
| Motor | Dark Engine (Looking Glass), modificado por NewDark (não oficial, fechado) |
| Executável MP alvo | NewDark 1.29 `Thief2MP.exe`, SHA-256 `e86b0645295e24f85747607c106beb9e94e4c21314f09156d4813c931d521fe0` (5.615.616 bytes) |
| MP 1.27 (referência) | SHA-256 `a22b3d0e6a254fe5247019bbd5a4d93bcfec234b51e67adf898825a442d45927`, timestamp PE 2019-06-15 |
| Sistema | Windows (PE 32 bits, i386); testado de WSL2 no Windows |

## <a id="downloads-pinned"></a>Downloads (fixados)

| Arquivo | SHA-256 | Fonte |
|---|---|---|
| `t2_v127.zip` (NewDark 1.27) | `33caca92a14acdb366211b464fbaa73113e028e9d024c9636e5a74890157ce26` | cópia TTLG t=146448 (MediaFire via bit.ly/2KV5oDU) |
| `t2_v129.zip` (NewDark 1.29) | `c2de1addf3e61b81ec55de6b4df0154d42a174b0c2e9fce4cc3c768855183952` | identificador Google Drive fixado em `fetchresources.sh` de T2Fix; MD5 `991b0ad2…` corresponde a TTLG t=153456 |
| `T2Fix_1.29-2026-09-16.exe` | `4982266e7777683285dcf88311377257fe6be8880010458b3c6255bf2c78730f` | github.com/Xanfre/T2Fix releases (desnecessário no fim: Inno 6.4.3, innoextract master não interpreta) |

## <a id="sources"></a>Fontes

- Vídeo (WungusDasPungus, "How to Make Thief 2 Multiplayer Actually Work"): https://www.youtube.com/watch?v=aRiVJqx9cnQ
- NewDark 1.27: https://www.ttlg.com/forums/showthread.php?t=146448 (adicionou beta multiplayer em executável separado)
- NewDark 1.29: https://www.ttlg.com/forums/showthread.php?t=153456
- T2Fix: https://www.ttlg.com/forums/showthread.php?t=149669, https://github.com/Xanfre/T2Fix
- Figgis, melhorias SS2/T2 MP: https://www.systemshock.org/index.php?topic=12190.0
- Servidor global: https://github.com/sungaila/NewDarkGlobalServer
- Complemento de roupas: https://github.com/vfig/t2mpfun

## <a id="observations"></a>Observações

- "Thief 2 Multiplayer" no diretório (mod de fãs de 2007 para OldDark 1.18) é outro projeto. Desde 1.27 (2019-06-15), equipe NewDark distribui beta próprio em `mp.zip`, `Thief2MP.exe`. Vídeo e T2Fix usam esse.
- Notas 1.28/1.29 listam correções de falhas na lista de servidores/leitura e etiquetas centradas. Nada sobre movimento de avatares/fantasmas (release_notes.txt em t2_v129.zip).
- `mp_release_notes.txt` no `mp.zip` 1.29: beta, não esperar jogo completo; algumas condições de conclusão só possíveis pelo host; vivo reanima morto interagindo com ele; fim só com todos mortos; sem conversa integrada.
- Executável usa sistema "ghost" Looking Glass: RTTI `cGhostLocalHash`, `cGhostRemoteHash`; mensagens `GhostFullHB`, `GhostNormHB`, `GhostMiniHB`, `GhostHBTerse`, `GhostRotHB`, `GhostObjHB`, `GhostAIHB`. Só configurações `ghost_local_frame_rate`, `ghost_local_process_ms`, `ghost_spew`; nenhuma suavização remota.
- Figgis (2023) lista não resolvido: jogador remoto preso na geometria e depois transportado à posição correta. Corresponde ao relato do usuário.
- Byte de limite Figgis "offset 0x2F440 in Thief2MP.exe": no 1.27 é prólogo de função (`6a ff 68 …`), não `04`. Resolvido: constante em 0x2F4FF no 1.27 e 0x3813F no 1.29 (`mov [edi+0x136], 4`, abaixo). Offset errado, descoberta (limite N+1) correta. Executável modificado no Google Drive do vídeo retorna 404 (2026-10-26).
- Transcrição: quarto jogador expulsa dois (patch Figgis corrige); navegador falha em T2Fix 1.27 (corrigido 1.29); teleportes em missões de fãs quebram sessões; itens coletados por cliente podem desaparecer.

## <a id="derived-from-the-ghidra-122-decompile-of-the-129-mp-exe-addresses-are-preferred-vas-base-0x400000"></a>Deduções (descompilação Ghidra 12.2 do MP 1.29; endereços virtuais preferidos, base 0x400000)

Fluxo ghost (movimento de objetos em rede):

| Endereço | Função |
|---|---|
| `0x5516e0` | atualização por quadro (dt em ms): cada ghost local `0x5556a0`, depois remoto `0x554980` |
| `0x5556a0` | local: executa preditor do receptor no próprio estado, consulta `0x554fe0` sobre envio, envia por `0x554d40` |
| `0x554fe0` | decisão: monta sinal (posição do modelo físico +0x34); só envia se previsão erra mais de 4 unidades num eixo (`0x81a108` = 4,0 vezes escala individual), velocidade erra 20, direção diverge, muda modo ou atividade de 30 s. Intervalo mínimo por tipo em `0x889f1c` = {0, 500, 250, 100} ms; tipo 3 é jogador |
| `0x5539d0` | recebe sinal (manipuladores `0x552620..0x552800` convergem aqui), copia ao bloco remoto (+0x0c), adiciona propriedade `AvatarZOffset` ao z |
| `0x553bd0` para `0x553520` | previsão: gravidade fora do chão, mescla velocidade, pos += vel vezes dt; raio (`0x54a880`) para em paredes |
| `0x553dc0` | dirige avatar à previsão: erro d = previsão menos posição física. Se módulo de d ao quadrado > 144 (`0x81a9a0`) ou indicador 0x200000: transporte por `0x5534c0` (falha se esferas físicas não cabem, `0x547220`). Senão velocidade física d vezes 2,0 (`0x819aa0`) ou velocidade prevista + d; movimento por física local com colisões |
| `0x516c90` | objeto para modelo físico (posição `+0x34`) |
| `0x41a940` | comando do motor (EAX = string) |

Conclusão: avatar remoto é corpo físico local perseguindo estimativa grosseira. Pode ficar 12 unidades distante antes de reposicionar, colide com portas/escadas já ultrapassadas pelo real, segue previsão com gravidade/raio (afunda/flutua até próxima atualização); remetente só corrige após erro de 4 ou mais. Corresponde a todos os sintomas; sem configuração desses limites.

Interface e entrada para automação:
- Procedimento da janela (`0x6999d0`) trata `WM_ACTIVATEAPP(FALSE)` chamando pausa (vtable +0x5c); janela inativa congela todo laço (Figgis também viu salvamentos pararem até todos voltarem com alt-tab).
- Mouse vai à fila Looking Glass `0x689480` ({x, y, tipo, tempo, botões}).
- `screen_dump` captura só buffer 3D, vazio nos menus.
- Sessão Windows bloqueada impede D3D de apresentar; nada testável ao vivo.

## <a id="fix-t2mpfix-mod-dinputdll-proxy"></a>Correção: T2MPFix (mod/, proxy dinput.dll)

Quatro correções independentes, um módulo por cada, ativadas por chave `T2MPFix.ini` (`mod/src/fixes.h`). Desligada ou sem assinaturas correspondentes, não instala hook; `T2MPFix.log` tem estado por correção e linha `active:`. Núcleo (`main.c`) controla hooks (`0x5516e0`, `0x554fe0`, `0x554d40`, `0x553dc0`) porque QA precisa de alguns mesmo com correções desligadas; avatar integra por `ghost_send_force` e `ghost_steer_pre`/`ghost_steer_post`; cada hook só instalado se correção ou QA exigem (`ghost_hooks_needed`, testado unitariamente). Tudo desligado não intercepta nada. Função de direção `0x553dc0` só interceptada para `recv_fix`: hook muda direção original (correção 2), então telemetria lê remotos percorrendo hash `0x8c5a80` em torno do quadro.

1. Suavizar remotos, duas metades:
   - `send_fix` (`fix_send.c`): ghost do jogador local força `0x554fe0` a enviar a cada 50 ms ao mover/girar e um sinal ao parar. Medidos 16,3 sinais/s contra 1,3 original.
   - `recv_fix` (`fix_recv.c`), só remetentes comprovadamente com `send_fix` (12 sinais/s em movimento, inalcançável pelo original): armazena estados (tempo, posição, velocidade, direção), mostra agora menos atraso (1,5 vezes intervalo médio + 2 vezes variação, limitado 60..300 ms; extrapolação sem gravidade, máximo 100 ms). Grava interpolação no bloco previsto; 0x200000 faz código original transportar. Se recusar porque corpo não cabe, `0x559c30` (ObjPosUpdate) posiciona assim mesmo. Ainda desnecessário nos testes.
   - Isoladas: `send_fix` dá ~16 sinais/s, mas direção original prende na geometria (path_dev não melhora); `recv_fix` nada faz sem remetente usando `send_fix`. Verificado em `regress.sh` (send_only, recv_only).
2. `steer_fix` (`fix_steer.c`): patch de 6 bytes na direção original; seção de pilha não inicializada abaixo.
3. `max_players` (`fix_players.c`): `SetMaxPlayers(N+1)` quando gerenciador existe (abaixo).
4. `damage_fix` (`fix_damage.c`): hook no filtro de dano; seção lava abaixo.

## <a id="test-results-2026-10-29-version-03-build-dinputdll-817cbee6"></a>Resultados (2026-10-29, versão 0.3, compilação `dinput.dll` `817cbee6…`)

Compilação reproduzível (duas limpas idênticas byte a byte). Contra `070f9688…` (testes de 8 abaixo), fontes diferem só em versão, comentários e comando QA `place` (inativo sem QA). Testes host: `make -C mod test` e `tools/qa/test_analyze.py` passam.

`tools/qa/regress.sh`, ALL PASS, saída 0 (missão 1, 70 s por cenário):
```
PASS stock localhost (control)    travelled  285.8  path_dev p95 7.052 max 14.870  off>1  4346  jumps 2  lag p50 3.03  hb/s 1.3  fixed 0/7119
PASS fixed localhost              travelled  286.1  path_dev p95 0.003 max 0.134  off>1     0  jumps 0  lag p50 0.30  hb/s 16.4  fixed 6802/7120
PASS fixed 60+-30ms 2% loss       travelled  285.2  path_dev p95 0.005 max 0.209  off>1     0  jumps 0  lag p50 0.61  hb/s 15.6  fixed 6780/7112
PASS fixed 150+-75ms 10% loss     travelled  285.2  path_dev p95 0.006 max 0.245  off>1     0  jumps 0  lag p50 0.98  hb/s 11.4  fixed 6710/7100
PASS send_fix only                travelled  287.0  path_dev p95 9.764 max 11.877  off>1  4154  jumps 2  lag p50 2.13  hb/s 16.4  fixed 0/7119
PASS recv_fix only                travelled  285.9  path_dev p95 2.676 max 3.658  off>1  2996  jumps 1  lag p50 1.13  hb/s 1.3  fixed 0/7122
PASS steer_fix only               travelled  286.7  path_dev p95 2.626 max 3.509  off>1  2981  jumps 1  lag p50 1.12  hb/s 1.3  fixed 0/7126
PASS mixed (mover without fix)    travelled  284.3  path_dev p95 2.578 max 3.424  off>1  2816  jumps 1  lag p50 1.09  hb/s 1.3  fixed 0/6891
ALL PASS
```

- Máximo original depende de poucos reposicionamentos, varia: 7,65 (2026-10-28), 17,66, 14,34, 14,87 (2026-10-29); p95 6,5 a 7,3. Só send_fix continua sem melhora, normalmente pior (p95 9,8 contra 7,1).
- Autoteste do avaliador: limite impossível exibe FAIL e sai 1; dump de falha durante execução também reprova; limites reais saem 0.
- `MAXP=8 players.sh 4` PASS duas vezes: limite 4 para 9, cada linha vê exatamente 3 remotos a cada segundo de 60 s. `players.sh 3` PASS (4 para 4, cada vê 2).
- **`max_players=N` não impede jogador extra salvo N = 8.** `players.sh 3 client3` FAIL, depois manual: com 3 na sala (Host/Client1/Client2) e `max_players=3` (limite 4), Client3 aceito; sala virou "Host, Client3" e Client1 recebeu "Network Connection Lost!". Bug original um jogador depois. Em 8, DirectPlay impede nono (abaixo); por isso padrão 8 e documentação manda manter.
- `players.sh 8 client8` FAIL em 2026-10-29 04:00 com 189 MB livres após 9 instâncias (aprovado abaixo tinha 1,2 GB): host voltou ao menu. Log sobrescrito; não se sabe se nunca entrou na sala ou caiu. Repetição precisa de ~5 GB livres.
- `lava.sh`: primeiro `lava.sh 1` FALHOU por caminhada terminar na borda, não lava (captura); repetições PASS. Errou 4 de 10. Agora confere última posição (vala ~80,29,-4,8, borda z 1,5 a 3), tenta até 3 vezes e falha como preparação. Sem conferir, `damage_fix=0` na borda seria PASS vazio. Caminhada depois substituída por comando QA `place x y z` (`obj_pos_update` no local preservando direção): `lava.sh` coloca 80,29,-4 e confere. Compilação `817cbee6…`: `lava.sh 1` PASS (80,0 29,0 -5,6, dano 3 vezes, morre), `lava.sh 0` PASS (80,0 29,0 -3,9, vida cheia na lava), ambas primeira tentativa.
- Estrutura: `lanes.py kill` só encerra processos das linhas (nenhum Thief2MP restante); suítes recusam sessão bloqueada (`check_unlocked`, também testado com nome de processo ativo: saída 1 com motivo).

## <a id="test-results-2026-10-28-modules-build-dinputdll-04d806c9-mission-1"></a>Resultados (2026-10-28, módulos, `dinput.dll` `04d806c9…`, missão 1)

`tools/qa/regress.sh`, ALL PASS (original = direção não interceptada, jogo real):
```
PASS stock localhost (control)    travelled  260.3  path_dev p95 6.481 max 7.652  off>1  3896  jumps 1  lag p50 3.04  hb/s 1.3  fixed 0/6519
PASS fixed localhost              travelled  260.1  path_dev p95 0.003 max 0.127  off>1     0  jumps 0  lag p50 0.30  hb/s 16.5  fixed 6209/6527
PASS fixed 60+-30ms 2% loss       travelled  259.8  path_dev p95 0.004 max 0.125  off>1     0  jumps 0  lag p50 0.62  hb/s 15.7  fixed 6182/6517
PASS fixed 150+-75ms 10% loss     travelled  257.8  path_dev p95 0.013 max 0.236  off>1     0  jumps 0  lag p50 0.98  hb/s 11.6  fixed 6093/6503
PASS send_fix only                travelled  259.8  path_dev p95 9.177 max 12.000  off>1  3482  jumps 2  lag p50 1.68  hb/s 16.5  fixed 0/6519
PASS recv_fix only                travelled  259.7  path_dev p95 2.401 max 3.060  off>1  2668  jumps 0  lag p50 1.02  hb/s 1.3  fixed 0/6529
PASS steer_fix only               travelled  257.1  path_dev p95 2.378 max 3.006  off>1  2702  jumps 1  lag p50 1.09  hb/s 1.4  fixed 0/6514
PASS mixed (mover without fix)    travelled  257.3  path_dev p95 2.438 max 3.124  off>1  2667  jumps 1  lag p50 1.08  hb/s 1.3  fixed 0/6396
```

- Só send_fix: jogador T2MPFix visto por outro sem mod; pior que original (ramo sem correção com sinais frequentes, dois reposicionamentos a 12 unidades).
- Só recv_fix: steer_fix desligado, mas igual porque leitura não inicializada tomou caminho bom atrás de `hk_steer` desta compilação. Não confiável.
- Cada correção isolada, demais desligadas:
  - `max_players=4`: 4 instâncias na missão por mais de 60 s; host vê 3 a cada quadro. Controle `max_players=0`: client1 perde conexão na sala, host/client3 em "Waiting...".
  - `tools/qa/players.sh` (2026-10-29, `070f9688…`, demais desligadas): `players.sh 5` e `players.sh 8 client8` PASS. Sala lista 8; cada linha vê N-1 em cada segundo de 60 s; host `cap field 4 -> 9`. Nono (client8) em "Joining Game...", sem erro, nunca entra, ninguém cai. ~480 MB por instância; nove deixaram 1,2 GB de 15 livres.
  - Sem limite (= DLL v0.2 `148633d5…`), `max_players=9`, nove instâncias: campo 4 para 10, sala para em 8. Nono espera mais de 2 min sem erro (laço ativo); oito jogam e veem 7 remotos por 60 s. Oito do DirectPlay é limite real; restrição só o documenta no log.
  - Padrão distribuído `max_players=8`, grupo comum: `MAXP=8 players.sh 4` PASS (4 para 9, três remotos).
  - `damage_fix=1` (`tools/qa/lava.sh 1`): host só em Soulforge entra na lava; log dano de objeto 1739 (`Water Flow Group`), "Host has died". `damage_fix=0`: vida cheia na lava.
  - Logs: tudo ligado, cada um desligado, todos desligados; cada desligado registra "off in T2MPFix.ini", nada instala; tudo e QA desligados, nenhum hook/patch.

## <a id="test-results-2026-10-26-newdark-129-mp-steam-build-1970-2-instances-on-one-pc-mission-1"></a>Resultados (2026-10-26, MP NewDark 1.29, Steam 1970, duas instâncias num PC, missão 1)

Linhas "stock" medidas com direção interceptada para telemetria, mudando original (seção pilha): mais próximas de `steer_fix` que do jogo real.

Estrutura: `tools/qa/run_ab.sh` (A/B, sessão e bot idênticos, só ini diferente), métrica `tools/qa/analyze.py`. Um executa `tools/qa/bots/walker.txt` (andar, correr, saltar, deslocar lateralmente, girar, agachar, recuar, circular; laço 30 s), outro parado; 65 s medidos. path_dev = distância do avatar exibido ao caminho real (sem atraso).

| Execução | path_dev p95 | path_dev max | quadros a mais de 1 unidade do caminho | lag p50 | sinais/s |
|---|---|---|---|---|---|
| original, cliente em movimento, localhost | 2.371 | 3.031 | 2338 / 5926 | 0.982 | 1.3 |
| T2MPFix, cliente em movimento, localhost | 0.002 | 0.077 | 0 / 5926 | 0.314 | 16.3 |
| original, host em movimento, localhost | 2.367 | 3.041 (atraso máximo 14.3, 1 reposicionamento) | 2360 | 1.053 | 1.3 |
| T2MPFix, host em movimento, localhost | 0.002 | 0.066 | 0 | 0.307 | 16.3 |
| original, 60±30 ms, 2% perda | 2.428 | 3.38 | 2171 | 1.054 | 1.3 |
| T2MPFix, 60±30 ms, 2% perda | 0.004 | 0.094 | 0 | 0.648 | 16.3 |
| original, 150±75 ms, 10% perda | 2.651 | 7.13 | 2328 | 1.291 | 1.3 |
| T2MPFix, 150±75 ms, 10% perda | 0.011 | 0.249 | 0 | 1.059 | 16.3 |

Rede prejudicada na DLL antes do receptor (só QA, mais simples que retransmissor UDP diante das portas DirectPlay). Inspeção visual: captura host mostra avatar cliente no chão na posição de telemetria (tools/qa, não versionadas).

Transporte DirectPlay: Windows oferece instalação no primeiro início; executável tem `Could not initialize DirectPlay` (0x683f60), `DPlay initialization error: %s (0x%X)`, `DPlayException`, RTTI `cCDPlayer`. Não importa sendto/recvfrom/bind; DLLs DirectPlay fazem sockets.

- Limite: campo +0x136 de `cNetManager` (4 em `0x438d39`), `SetMaxPlayers` = vtable posição 40 (`0x43a230`, stdcall). Sala original com quatro: Client3 expulsou Client1/Client2 (reproduzido). Limite 5 mantém quatro.
- Superior: `DPN_APPLICATION_DESC` DirectPlay8 host (em `0x68424d`: dwSize 0x48, flags 0x40 NODPNSVR) tem `dwMaxPlayers = 8` (`mov [ebp+0x28],8` em `0x684254`, única escrita; sem SetApplicationDesc depois), recusando nono qualquer que seja limite. `max_players` limitado a 8. Manipulador (`0x437c20`) envia identificadores num `int[8]` fixo, adequado até 10. Cinco/oito testados ao vivo (abaixo).

## <a id="stock-steering-reads-uninitialized-stack-fixed-by-steer_fix"></a>Direção original lê pilha não inicializada (corrigida por `steer_fix`)

Descoberto quando divisão em módulos moveu código de `hk_steer` e controle *original* piorou (máximo path_dev 3,0 para 7,5, atraso p50 1,0 para 3,0) no mesmo jogo. A/B com DLLs antigas/novas por lado: só receptora importava.

`0x553dc0` (direção), jogador em movimento (`|pred vel|^2 > 1`), em `0x553f07`: `fld [esp+0x14]; fld [esp+0x10]; fld [esp+0x18]`, `|.|^2` comparado a 1,0, `jp 0x553fbd`. Três floats nunca escritos nesse caminho (Ghidra `local_24/20/1c`).
- `|garbage|^2 <= 1` para `0x553fbd`: velocidade física só prevista; avatar nunca reduz distância, fica atrás até transporte de 12 unidades.
- Senão, velocidade = previsão menos posição + velocidade prevista (puxa à previsão com constante 1 s).
- Vagas contêm sobras de chamada anterior na mesma profundidade; hook na cadeia (`hk_steer` antigo) muda resultado. DLL antiga deixava valores grandes por acaso; jogo puro não.

Medido (host observa, client1 anda enviando como original, 70 s, missão 1):

| Receptor | path_dev p95 | max | lag p50 |
|---|---|---|---|
| original real (sem hook de direção, telemetria do hash ghost) | 6.63 | 7.75 | 3.03 |
| original atrás do novo `hk_steer` (sem correção) | 6.49 | 7.52 | 3.06 |
| original atrás do antigo `hk_steer` (sem correção), o "original" das tabelas anteriores | 2.39 | 3.00 | 1.09 |
| patch: ler `d = pred - pos` em vez disso (corrigir só acima de 1 unidade) | 5.63 | 8.11 | 1.15 |
| patch: eliminar ramo (sempre corrigir), distribuído como `steer_fix` | 2.37 | 3.04 | 1.09 |

Linhas antigas "stock" (máximo ~3) eram original mais pilha favorável do hook; real ~7,7 (depois p95 6,5 a 7,3, máximo 17,7 por poucos reposicionamentos). Variante `d` é provável intenção, mas pior aqui; `steer_fix` substitui por NOP o `jp` em `0x553f35` (`0f 8a 82 00 00 00` para `66 0f 1f 44 00 00`), conferindo 52 bytes desde `0x553f07`.

## <a id="lava-does-no-damage-in-multiplayer-fixed-by-damage_fix"></a>Lava não causa dano no multiplayer (corrigido por `damage_fix`)

Observado: Soulforge (missão 15, `miss16`), vala inicial nada faz em `Thief2MP.exe`, mata em `thief2.exe`; concha física machuca em ambos. Reproduzido sem hooks e com `max_players=0`.

Rastreado em compilação descartável, cada etapa registrada no jogo:
- Lava é sala de água com grupo de fluxo 2. Objeto 1739 (`Water Flow Group`, `FlowGroup` = 2) tem FireStim/WaterStim. Mudança de meio chama callback físico (`0x486d00`), propagador (`0xab9a70`, `cPeriodicPropagator`), liga 1739 ao jogador e envia FireStim intensidade 14 imediatamente e a cada 1000 ms. Tudo funciona em MP.
- Receptores: `M-GarrettDiffNormal` Amplify 0,8 (11,2), depois `FireDamaged` `damage` (efeito 21, manipulador `0x596fc0`), chama `IDamageModel::DamageObject` (`0x5a4da0`) com vítima jogador, culpado 1739, dano 11 a 12.
- `DamageObject` executa filtros (`0x5963f0`, vetor model+0x20). Filtro `0x44bce0` (só MP, `__stdcall` vítima/culpado/msg/data) zera dano e retorna 1, logo `DamageObject` retorna 1 ("status quo").
- Lógica: permite sem rede ou vítima só local; culpado hospedado aqui e vítima proxy envia dano ao responsável (`0x44c080`) e zera local; culpado não hospedado nem proxy zera salvo `LocalCopy` (saída da consulta reutiliza argumento, então propriedade ausente também bloqueia). Medido: jogador f1c 0/f20 1/f24 0; lava 1739 f1c 0/f20 0/f24 1 (`IObjectNetworking` em `0xab83ac`, posições +0x1c proxy, +0x20 hospedado, +0x24 só local).
- Resultado: dano cujo culpado é só local descartado em todas as máquinas. `dark_net.dml` torna `physical` hospedados; concha funciona por isso.

Correção: hook no filtro; culpado só local e vítima hospedada aqui (não proxy) retorna 0 (sem opinião), deixando dano passar. Cada máquina aplica a objetos próprios (jogador, IA no host); proxies continuam filtro original bloqueados, sem duplicar. Verificado: host/cliente morrem em ~2 s na lava; outro mantém vida cheia.

## <a id="lessons-candidates-for-playbooklessonsmd"></a>Lições (candidatas a playbook/lessons.md)

Enviadas a `playbook/lessons.md`: `ret N` e `-mstackrealign` = 60, hook que altera direção = 62 (61, métrica de desvio, vem de QA), registrar cada etapa = 64, sessão bloqueada = 65. Foco já coberto na lição 23 e `playbook/methods.md`.

- `0x516c90` é `__stdcall` (`ret 4`), embora Ghidra mostre função comum de um argumento. Chamar cdecl deslocou ESP 4 por chamada, derrubando ambos no primeiro quadro. Conferir `ret N` de toda função, não só assinatura descompilada.
- Hooks de MSVC recebem pilha alinhada a 4 bytes; clang/gcc i686 pressupõem 16 e emitem `movapd` na pilha. Compilar com `-mstackrealign`; falha aparece como violação no endereço 0xffffffff.
- Thief2MP pausa tudo em `WM_ACTIVATEAPP(FALSE)`, só aceita mouse injetado quando janela *não* está em primeiro plano. Para duas instâncias: substituir procedimento, consumir desativação, enviar ativação sintética, manter ambas no fundo. Coordenadas escaladas por 1,28 do cliente 800x600 (menus baseados em 640x480).
- Estímulo sem efeito: registrar cada etapa (propagador, sensor, receptor, efeito, modelo, filtros) ao vivo antes de ler mais código; descompilador removera blocos "inalcançáveis", causa real era filtro três camadas depois.
- Hook pode mudar comportamento sem tocar dados: direção lê pilha nunca escrita, sobras decidiam deriva. Medir controle sem hooks na cadeia e fazer A/B também do modo original de refatorações.
- Sessão bloqueada faz testes visuais/entrada falharem silenciosamente (D3D não apresenta); conferir `LogonUI` primeiro.

## <a id="unknowns"></a>Desconhecidos

- Remotos em elevadores/plataformas móveis (sinais relativos a objeto usam direção original), escadas, flechas de corda, escalada de bordas, nado, salvar/carregar, troca de missão, missões de fãs e internet (rede ruim só simulada na DLL): não testados.

Resolvidos: taxa de sinais e limite de transporte (seção de deduções); várias instâncias `Thief2MP.exe` num PC (testado com quatro).
