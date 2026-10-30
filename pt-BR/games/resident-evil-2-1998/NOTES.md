# <a id="resident-evil-2-1998-working-notes"></a>Resident Evil 2 (1998): notas de trabalho

Registro contínuo, entradas mais recentes no fim. Observações, deduções, hipóteses e desconhecidos ficam separados.

## <a id="identity-observed-2026-10-27"></a>Identidade (observada em 2026-10-27)

- Loja: relançamento Steam, AppID 4249110, compilação 21744144 (abril de 2026, Capcom + GOG).
- Executado pelo "Steam Enhancement Pack" de Mulder (mulderland.com), que usa `rebirth\bio2.exe`: executável Sourcenext Biohazard 2 PC v1.1.0 de 2006 com Classic REbirth.
- `rebirth\bio2.exe`: PE32 i386, 6.131.712 bytes, marca de tempo PE 1157628588 (2006-09-07), SHA-256 `00dd7aab0ae5d5f6afef1cb4a9071030c2e8d4edd00e5a24302a70c800c3c232`.
- `rebirth\bio2.exe.Backup` original: SHA-256 `21b2a647cbeddac1ec389be847f22a434a0264a18020589de91cb2824dcb1bf5`. `fc /b` mostra 4 bytes diferentes: 0x116 (0x0F -> 0x2F, LARGE_ADDRESS_AWARE) e soma de verificação PE. O código é o original de 2006.
- `ddraw.dll` = Classic REbirth 1.0.9.1, `dsound.dll` = Ultimate ASI Loader 9.7.1.0 (carrega `*.asi`), `re2_DDraw.dll` + `D3DImm.dll` = dgVoodoo 2.86.5. Patch francês "mod_fr_RE2 V1.0.2" aparece no diálogo MOD SELECTION do Classic REbirth.
- Executáveis próprios do relançamento (`english\LeonU.exe`, `french\LeonF.exe`...) são a compilação GOG do port de 1998, diferentes. Nada abaixo se aplica a eles.

## <a id="prior-work-searched-2026-10-27"></a>Trabalhos anteriores (pesquisados em 2026-10-27)

- Nenhum mod cooperativo ou multiplayer de RE2 1998 encontrado (busca web, este diretório).
- Fontes úteis:
  - BioRand (github.com/IntelOrca/biorand), `biorandmod/biorand.cpp`: hooks para este executável exato (0x4C5E13 carregar jogo, 0x4E3FA0 event_exec, 0x4EF9AA chamada de inicialização de NPC, array de tarefas SCD).
  - biohazard-utils `src/hitscan/Re2Binder.cs`: palavra de teclas 0x988604, identificador do jogador 0x98E9A6.
  - MeganGrass/Resident-Evil-2-Starter-Kit `source/bio2/data.h`: estruturas PS1 (tagGLOBAL, PLAYER_WORK, ENEMY_WORK...). **O executável PC mantém a organização PS1**, conforme offsets conferidos abaixo.
  - biohazard-utils `Script/Opcodes/SceEmSetOpcode.cs` e `OpcodeV2.cs`: formato dos opcodes SCD.
  - yanmingsohu/re2re: desmontagem ddisasm completa de um bio2.exe, mas endereços não correspondem (0x53CAC8 é dado ali); provavelmente outra compilação. Não usada.

## <a id="memory-map-derived-all-checked-in-a-running-game"></a>Mapa de memória (deduzido, todo conferido em execução)

| Elemento | Endereço | Verificação |
|---|---|---|
| `G` (tagGLOBAL) | 0x9864E0, ponteiro em 0x52D7E4 | loop por quadro lê `[0x52D7E4]+0x3C2C` = pEnemy |
| `G.Player` (PLAYER_WORK) | 0x989EF0 | Life +0x156 = 200, Max_life +0x162 = 200; posição muda quando bot anda |
| `G.pEnemy[34]` | 0x98A10C; [0] = Player, [1] = parceiro, [2+n] = em id n | tratador em_set escreve `[id*4 + 0x98A114]` |
| `G.Em_move_tbl[type]` | 0x98A154 (= G+0x3C74) | tipos NPC 0x40..0x5B apontam para 0x4EF110 |
| ppEnemy_end, pFree_work, entidade atual | 0x98862C, 0x988624, 0x988628 | usados pelos loops |
| entidade vazia | 0x98E544 | vagas pEnemy não usadas apontam para cá |
| SaveData | 0x98E79C; stage int16 0x98EB14, room 0x98EB16, tipo de jogador 0x98E9A6 | offsets BioRand +0x378/+0x37A/+0x20A |
| Rotina de controle | 0x4D0F30, controle bruto de `call 0x43BB00` em 0x4D0F53 | palavra de teclas 0x988604 (mantidas), 0x988608 (pressionadas) |
| Mapa de teclas (configuração 0) | 0x5338D8: bit n do jogo <- bits PS1 brutos | bit0 cima 0x1000, bit2 baixo 0x4000, bit8 mira R1 0x0008, bit6/7/12 = 0x00A0 (círculo/quadrado) |
| Tratadores SCD | 0x53AE10\[opcode](SCE_TASK*), Data da tarefa em +0x1C | em_set (0x44) = 0x4E77D0 |
| Loop de entidades por quadro | início 0x4C03CA, chamada de movimento 0x4C0449 `call [G + id*4 + 0x3C74]` | |
| Passagem inicial de entidades da sala | 0x4DF180 (chamada uma vez em 0x4DEE3D) | |
| Emd_load | 0x4B1660 (type, pEm, mem_top); tipos 0x50..0x5A escolhem variantes Leon/Claire por indicadores | |

Offsets da entidade (PS1 = PC): Id +0x08, Pos_x/y/z +0x38/+0x3C/+0x40 (int32), Old xyz +0x44, Cdir_y +0x76, nFloor +0x106, Parts_num +0x107, Status +0x10E, Move_no +0x14C, Life +0x156, pKage_work +0x16C, pSin_parts +0x198. Alocação PC: 0x248 bytes.
`PARTS_W` mantém tamanho 0xAC, mas campos diferem no PC (ponteiros para heap do renderizador).

## <a id="experiments"></a>Experimentos

1. Entrada do bot: hook em `call 0x43BB00` em 0x4D0F53, retornando controle bruto próprio, dirige Leon (UP por 40 quadros moveu x de -24522 a -24932; LEFT mudou Cdir_y de 1200 a -320). Círculo confirma menus, Start/Cross pula introdução.
2. Criar NPC pelo em_set original (SCE_TASK fictícia, Data aponta ao opcode de 22 bytes):
   - Pelo hook de controle: falha em 0x4C0669 (loop de sombras lê pKage_work antes da inicialização). Rotina NPC 0x4EF110 ignora entidades quando bit 0x20000000 de 0x989ED4 está marcado, como ocorre fora do loop.
   - Por trampolim no início do loop por quadro (0x4C03CA): funciona. Claire (tipo 0x51) aparece junto a Leon na fase 5, sala 0x12, com sombra e animação ociosa, vaga 33.
   - Sobrescrever Pos/Cdir após a rotina move e gira Claire.
3. em_set é assíncrono: com `[0x68A204]+0x13` marcado (arquivo carregando), retorna sem avançar Data; chamador deve repetir no quadro seguinte (o agendador faz isso).

## <a id="unknowns"></a>Desconhecidos

- Números de animações de andar/correr/mirar de NPC Claire/Leon (em050/em051).
- Se NPC pode morrer por inimigos ou bloquear portas.
- Armazenamento de indicadores de história (arrays SaveData), necessário para progresso com autoridade do host.

## <a id="session-2026-10-27-continued-puppet-network-follow-host"></a>Sessão 2026-10-27 (continuação): representante, rede, seguir host

Observado (tudo em execução, duas cópias no mesmo PC):

4. `G` = 0x9864E0 (ponteiro em 0x52D7E4). Compilar `tagGLOBAL` do cabeçalho PS1 produz Player +0x3A10, pEnemy +0x3C2C, Sce_aot +0x2370, pSce_aot_on +0x2368, Stop_flg +0x39F4, SaveData +0x82BC: todos conferem. pEnemy tem 34 entradas; tabela de movimento PC indexada por `[G + type*4 + 0x3C74]`, sobrepondo pEnemy[18..33] para tipos não usados 0..15.
5. Início do loop por quadro 0x4C03CA (`mov edx,[0x991FC0]`), chamada de movimento 0x4C0449. 0x4DF180 é somente passagem inicial da sala (uma chamada de 0x4DEE3D); hook ali não executa por quadro.
6. Estado NPC (Routine_0 = 4): Routine_1 = 4 andar ao destino, 5 correr, 6 ocioso. `plc_dest` (0x40, tratador 0x4E7330) escreve destino em +0x1C4/+0x1C6 e +0x1D8/+0x1DA; índice de indicador de chegada em +0x1CB (definido em 0x98EB6C por 0x503120); velocidade +0x1D4. Tipo 8 (passo para trás) deixa NPC parado. `plc_motion` (0x3F, 0x4E72D0): Routine = 4 | a<<8, Move_no = b, +0x1CC = c. `work_set` (0x2E, 0x4E5E90) guarda entidade-alvo em task+0x154.
7. Routine_1 do jogador em movimento: 1 andar, 2 correr, 3 passo para trás, 4 girar (teste de bot).
8. Tratador AOT de porta 0x4E9460, tabela 0x53B46C, sucesso em 0x4E95C4. Submodo `[0x68A204]+9`, modo 4 = porta (0x4C085E), copia IN_DOOR_WORK ao jogador, define corte (0x98EB18), sala anterior (0x98EB1A), sala e fase (chama 0x4DEF00 se mudar fase).
9. Instância única: nome do mutex em 0x525138 (aberto em 0x441EE2); Classic REbirth confere `bio2.658b45ea117473d4.game` e `re2cr.aiory0n5jnqf3r7a.game` (ddraw.dll 0x10065839).
10. Iniciar por `Popen` e conectar pelo pid é pouco confiável aqui (pid impresso para A foi uma vez o processo B); resolva pids pelo caminho do processo.
11. Troca de sala: `ROOM` muda no início da animação da porta; loop da nova sala começa 2-3 s depois; motor reinicia pEnemy[33] ao inicializar.

QA executado em 2026-10-27: `qa_suite.py steam-mock` 17/17, `qa_suite.py udp` 17/17. Steam real com uma conta: inicialização, sala criada, título "en attente du joueur 2". Acompanhamento entre fases manual: cliente da fase 0, sala 0x0F, à fase 5, sala 0x12, controlável depois.

Hipóteses não verificadas:
- Zumbis provavelmente ignoram representante, fora da vaga de parceiro pEnemy[1].
- Vaga em 31 provavelmente não usada nas salas originais.

Desconhecido: cenas, trechos Ada/Sherry, morte, Steam real com duas contas.

## <a id="session-2026-10-27-enemies-chunk-1-where-enemies-take-damage-and-die"></a>Sessão 2026-10-27 (inimigos, parte 1): dano e morte

Deduzido da desmontagem estática de `bio2.exe` (índice capstone), **ainda não conferido em execução**:

- `pEnemy_damage_tbl[48]` = 0x539F50, por Id (0x10..0x2F = tipos inimigos). Segunda tabela 0x53A010 usada se byte 0x6805B3 não é zero (hipótese: dificuldade). Entradas apontam a `ATTACK_WEAPON_EM[19]` (formato PS1, 20 bytes; tabelas PC distam 0x180), indexadas por item id - 1. `Damage` reúne três valores de 10 bits (nível 0..2, por distância ou zona); `SubDamage`, três de 3 bits. Zumbi 0x10: faca 3, pistolas 16/15/14, magnums 900, escopeta 200/60/40.
- `Pl_shot_damage` 0x4D3440 (atirador `PLAYER_WORK*`, `(item-1)<<16 | ...`, tabela de acertos), 6 chamadores (0x4D54F0, 0x4D8660, 0x4D8B40, 0x4D8EA0, 0x4D9140, 0x4F3C70). Em 0x4D3BAD: `Life -= damage; Tmp_routine = Routine; Routine_0 = 2` (atingido), `3` se Life < 0 (morto).
- 0x4D7E30 (18 chamadores em 0x4BA000..0x4BE000, hipótese: projéteis) e 0x4D8260 (dano radial por todas as vagas pEnemy; também subtrai de 0x98EE7C) aplicam igual, com `Damage_flg |= 1` (+0x1D0) e `Damage_no = 1` (+0x1D2).
- `Em_dead_flg_on` 0x4B45A0 (ENEMY_WORK*) marca bit de morte `Em_set_flg` (+0x1CE) via 0x503120 em 0x98EB74 (fase < 3 e bit 0x2000000 de 0x989ED0 limpo) ou 0x98EB94 (segundos 32 bytes). Chamado por 32 rotinas de morte por tipo (0x45708F ... 0x4B0F00).
- 0x4D97B0, que também escreve Life pelo loop por quadro, é dano periódico de veneno do jogador (0x98A108).

Offsets ENEMY_WORK (cabeçalho PS1 compilado): Status_flg +0x154, Down_cnt +0x1C8, At_hit_flg +0x1CA, Sce_flg +0x1CC, Em_set_flg +0x1CE, Damage_flg +0x1D0, Damage_no +0x1D2, Damage_cnt +0x1D3, Tmp_routine +0x1FC, pDamage_work +0x200, tamanho 0x244.

Consequência deduzida: convidado pode relatar golpes com hooks nos três locais `sub [reg+0x156]` (0x4D3BAD, 0x4D7F49/0x4D80F5, 0x4D8344); morto no host = Routine_0 vira 3.

## <a id="session-2026-10-27-enemies-chunk-2-host---client-enemy-snapshot"></a>Sessão 2026-10-27 (inimigos, parte 2): snapshot host -> cliente

re2coop local, não distribuído: pacote tipo 3, protocolo 4. Host envia toda entidade pEnemy[2..33] com Id 0x10..0x3F (não representante nem NPC) a cada dois quadros do loop: vaga, Id, Be_flg, Move_no, Routine_0..3, x/y/z, Cdir_y, Life (20 bytes cada, até 24 para ficar abaixo dos 512 bytes da fila Steam). Cliente guarda o último; aplicado na parte 3.

Observado (duas cópias, fase 5 sala 0x12):
- Criar zumbi 0x10 por em_set funciona em sala sem zumbis: EMD carrega, Life 80, Routine (1, 0, 1, 0), anda sozinho.
- Loop de entidades a 30 Hz, metade da taxa do hook de controle.
- `qa/enemytest.py`: 11/11 em steam-mock e udp (14,5 snapshots/s, cliente recebe zumbi exclusivo do host na vaga 22, diferença de posição 8, mesma Life). `qa_suite.py` ainda 17/17 nos dois transportes.

## <a id="session-2026-10-27-enemies-chunk-3-the-client-mirrors-the-hosts-enemies"></a>Sessão 2026-10-27 (inimigos, parte 3): cliente espelha inimigos do host

re2coop local, não distribuído, `src/enemies.cpp`. Para cada entidade cliente com vaga/Id presentes em snapshot recente (< 0,5 s) da sala atual, ao redor da rotina própria:
- antes: se Routine_0/1 diferirem, aplicar os do host e zerar Routine_2/3 (executa inicialização do estado); copiar Life; se host morto (Routine_0 3 ou Life < 0), definir Routine_0..3 = 3,0,0,0 uma vez. Entidades ainda em Routine_0 = 0 (inicialização) e já mortas ficam intactas.
- depois: escrever Pos / Old pos / Sca_old de posição suavizada por vaga (metade do caminho ao host a cada quadro) e girar Cdir_y pela metade.

Observado (duas cópias, fase 5 sala 0x12, zumbi 0x10 na vaga 22 em ambas):
- **Parte 1 conferida ao vivo:** mirar R1 e disparar quadrado (bruto 0x80) reduz Life de 80 a -1; Routine_0 vai a 3 e depois 7 (7 = deitado morto; Life termina em -1).
- Forçar estado durante Routine_0 = 0 falha em 0x4C0669 (sombra lê pKage_work antes de inicializar).
- Rotina reescreve Pos a cada quadro pelo estado próprio: escritas de teste não persistem, e suavizar a partir de Pos nunca convergiu (diferença constante ~156). Manter posição suavizada própria resolveu (6-10).
- Escrever 3,0,0,0 num zumbi em Routine_0 7 o levantou (1,0,1,0): nunca force morte duas vezes.
- `qa/mirrortest.py --shoot`: 11/11 em steam-mock e udp; `enemytest.py` 11/11; `qa_suite.py` 17/17.

Não testados: zumbi do host caminhando (o criado fica parado; acompanhamento só conferido empurrando a cópia cliente), vários inimigos, outros tipos, inimigos dos scripts de sala, posição do cadáver cliente após morrer (para de sincronizar).

## <a id="session-2026-10-27-enemies-chunk-4-the-clients-hits-reach-the-host"></a>Sessão 2026-10-27 (inimigos, parte 4): golpes do cliente chegam ao host

re2coop local, não distribuído, `src/enemies.cpp` e pacote tipo 4 em `src/coop.cpp`:
- Só cliente: quatro locais `sub word [reg+0x156], reg16` (0x4D3BAD ebx/dx, 0x4D7F49 esi/ax, 0x4D80F5 edi/dx, 0x4D8344 esi/ax; todos `66 29 xx 56 01 00 00`, 7 bytes) desviam a auxiliar que relata entidade/dano, repete `sub` e retorna. Indicadores posteriores não dependem de `sub` (próxima instrução é `cmp`, `mov` ou outro `sub`).
- Golpe = (seq, vaga, Id, dano). Cliente reenvia os de menos de 0,5 s em cada pacote de estado (30/s, até 16); host aplica cada seq uma vez, só na sua fase/sala, como 0x4D3BAD: `Tmp_routine = Routine; Life -= damage; Routine = Life < 0 ? 3 : 2`. Ignora entidade em Routine_0 0, morta ou Id diferente. Seqs começam em GetTickCount(), evitando reutilização após reiniciar cliente.
- Cópia cliente ainda recebe golpe local (resposta imediata); depois Life volta a ser copiada do host (parte 3).

Observado (duas cópias, fase 5 sala 0x12, zumbi 0x10 na vaga 22):
- Um tiro cliente (Claire, R1 + quadrado) tirou 300 Life localmente; host aplicou 300 uma vez (80 -> -220), zumbi chegou a Routine_0 7 (deitado morto); cliente também.
- Uma vez, criar zumbi antes do representante cliente fez dois em_sets compartilharem alocação e derrubou cliente em 0x4C0669: corrida de preparação (comando de depuração 4 contra representante), não código de golpes. `qa/hittest.py` agora espera ambos os representantes.
- `qa/hittest.py`: 11/11 em steam-mock e udp; `qa_suite.py` 17/17, `enemytest.py` 11/11, `mirrortest.py --shoot` 11/11 nos dois.

Não testado / não sincronizado:
- Golpe não letal (Routine_0 2 no host, reação): todos os tiros até então matavam em um golpe.
- Subdano por parte (+0x151..0x153, membros) e Damage_no (+0x1D2) não enviados.
- Se cliente mata sua cópia com golpe não confirmado pelo host (Life diferente), cadáver fica caído enquanto zumbi do host vive.

## <a id="session-2026-10-28-enemies-chunk-5-several-zombies-hits-that-do-not-kill-walking-zombies"></a>Sessão 2026-10-28 (inimigos, parte 5): vários zumbis, golpes não letais e movimento

Deduzido de desmontagem estática e conferido ao vivo (duas cópias, fase 5 sala 0x12, zumbis 0x10 por em_set nas vagas 20-22, Life do host alterada só para teste):
- **Pl_shot_damage escreve mais que Life.** Após `Life -= damage` em 0x4D3BAD, define Damage_flg |= 0x20/0x40/0x80 (lado do tiro, 0x4D3C7D..0x4D3CB0), Damage_no = nível * 3 + zona (0x4D3CCE), **Routine_1 = identificador do item-arma** (0x4D3CDD), Damage_cnt (0x4D3D02) e saúde de partes +0x151..0x153 (0x4D3BC5..0x4D3C39).
- **Rotina de golpe do zumbi** (Routine_0 2, 0x455780) chama `table[Routine_1 * 9 + Damage_no]` em 0x455B9D (tabela 0x526ED4): entradas 0..8 são dados; Routine_1 0 salta para dados. Parte 4 definia Routine 2 com Routine_1 0 no host: falha em 0x8032008C / 0x803E0096 no primeiro golpe não letal (testes anteriores só matavam com um tiro).
- **Rotina de morte** (Routine_0 3, 0x4585B0) chama `table[Routine_1]` em 0x4586A1 (tabela 0x527464) com bit 0 de Status marcado: entrada 0 nula, 1..18 apontam a 0x458BF0, 19 a 0x459E10. Forçar 3,0,0,0 como na parte 3 falha em 0x00000000 quando bit 0 de Status está marcado (visto em 0x2001).
- Rotina de morte zera para -1 a própria Life (80 - 300 no host terminou em -1).
- Zumbis também morrem pelas próprias rotinas (escritas em 0x451DB2, 0x451DEB, 0x453A3D, `dec Life` em 0x452EE9 e 0x453448). Uma vez por execução na preparação anterior: zumbi host em Routine 01 01 05 00, Status 0x2001, Life 80 foi a 07 00 00 00 Life -1 sem golpe (switch de Routine_2 em 0x45359E, caso 6 = 0x453A19). Motivo de entrar na sequência desconhecido.
- Um tiro da arma de Claire neste salvamento (Routine_1 8 após golpe) atingiu os três por 300 cada; tiros seguintes não acertaram nada (hipótese: sem munição).

Alterações locais re2coop, não distribuídas, protocolo 5:
- Golpe cliente = (seq, vaga, Id, dano) e resultados da rotina na entidade, lidos antes do movimento seguinte (`enemies_finish_hits`): Routine_1, Damage_no, Damage_flg, Damage_cnt e diferenças de saúde das partes. Host aplica tudo (Routine = 2 ou 3 | Routine_1).
- Snapshot leva Damage_no e Damage_flg (antigo preenchimento); cliente copia ao adotar Routine_0 2 do host.
- Morte forçada no cliente: Routine_1 do host se 1..18; caso contrário, 1.
- Host instala os mesmos quatro hooks só para log (`local hit ... by player/puppet/other`).

Observado (um tiro cliente, Life do host 2000 / 80 / 2000): 3 golpes registrados, 3 aplicados uma vez; vidas 1700 / -1 / 1700; dois feridos passaram por Routine_0 2 nos dois; morto passou por 3 e 7 nos dois e ficou morto por 5 s; feridos sobreviveram; ao host se afastar, dois zumbis moveram até 2134, e cópias clientes ficaram a até 199 deles.

QA executado em 2026-10-28; `qa_suite.py` agora tem seção 6 = `enemylib.multi_enemy_checks`, e `qa/multitest.py` a executa sozinha:
- steam-mock: `qa_suite.py` 32/32, `enemytest.py` 11/11, `mirrortest.py --shoot` 11/11, `hittest.py` 11/11, `multitest.py` 15/16 (diferença de acompanhamento 682).
- udp: `qa_suite.py` 17/18 (seção 6: três criações do cliente retornaram 0, causa desconhecida), `enemytest.py` 11/11, `mirrortest.py --shoot` 11/11, `hittest.py` 11/11; `multitest.py`, 7 execuções: 3 passaram 16/16, 2 falharam só no acompanhamento (959-1077), 2 porque tiro não acertou (0 golpes, 8/16).
- **multitest é intermitente; causa da falha de acompanhamento observada:** no maior desvio, cliente em Routine_0 5 (agarrado/ferido, `05 01 03 00`), zumbi cliente a 338 dela e 959 da cópia host. Rotina própria ainda executa (só Routine_0/1 forçadas), então agarra a jogadora por conta própria e fica retido. Hipótese não verificada: tiros sem acerto ocorreram enquanto agarrada. É etapa 2 (alvos dos inimigos, dano em jogadores), não corrigida aqui.

Não testados: inimigos dos scripts de sala, outros tipos, perda de partes (membro em -1), golpe host com cliente reagindo a golpe, perda de pacotes de golpes.

## <a id="session-2026-10-28-enemies-step-2a-enemies-never-act-on-the-clients-player-by-themselves"></a>Sessão 2026-10-28 (inimigos, etapa 2a): inimigos nunca agem sozinhos sobre jogador cliente

Observado nos diagnósticos de multitest, duas cópias: zumbis espelhados agarravam jogadora cliente (Routine_0 5, ponteiro de agarrador 0x98A0A4 = zumbi). Causa: Routine 1/1 já é o agarrão; etapa 0 (0x4535A5) define 0x98A0A4 e Routine 5 sem conferir distância (decisão anterior no host). Copiar estado do zumbi agarrando jogador host fazia cópia agarrar jogadora cliente. Alguns agarrões também vinham de quadros iniciais, antes do primeiro snapshot.

Mudança local: no cliente, com host na mesma sala, toda rotina inimiga (Id 0x10..0x3F, espelhada ou não) executa em `PlayerShield`: bloco do jogador e indicadores anteriores (0x989ED0..0x98A10C: SYS_FLAGS, Stop_flg, G.Player, ponteiro de agarrador) são salvos, jogador é colocado na posição do host (decisões correspondem) e bloco restaurado depois. Primeira tentativa de afastá-lo 16000 unidades fazia zumbis mudarem estado a cada quadro (`mirrortest`, "same top-level state": 0/50). Também: mortos espelhados continuam seguindo posição do cadáver host; suavização passou de 1/2 para 3/4 por quadro.

Fatos estáticos conferidos pelos agarrões: 0x4DCA40 é função comum de dano ao jogador (argumentos: dano, ?), 60 chamadas em rotinas inimigas, como mordida em 0x453740. SaveData.Item_work[11] (Id, Num, Size, preenchimento) fica em SaveData + 0x598 = 0x98ED34 (formato PS1, referenciado por Room_flg +0x3D0 e Enemy_flg +0x3D8 já conferidos); Claire usa item 8 com 3 tiros neste salvamento.

Acompanhamento na investida (Routine 01 03 08): zumbi host moveu cerca de 530 unidades entre snapshots; cliente ficou momentaneamente até 700 atrás (latência). `multitest` agora confere percentil 90 (< 400) e máximo (< 1500, distância de correção instantânea).

QA executado em 2026-10-28, duas cópias em um PC; steam-mock e udp, cada um: `qa_suite.py` 33/33, `enemytest.py` 11/11, `mirrortest.py --shoot` 11/11, `hittest.py` 11/11, `multitest.py` 17/17 em 5 de 5 (nova verificação: cliente nunca agarrado). Testes agora reiniciam ambos uma vez se um não chegar ao jogo (`enemylib.start_pair`).

Consequência ainda não implementada, etapa 2b: com a proteção, zumbis host não ferem cliente na mesma sala e só perseguem jogador host.

## <a id="session-2026-10-28-enemies-step-2b-the-hosts-enemies-attack-the-client-too"></a>Sessão 2026-10-28 (inimigos, etapa 2b): inimigos do host também atacam cliente

Fatos encontrados por análise estática e conferidos ao vivo:
- **Loop guarda distância de cada inimigo ao jogador** antes do movimento: `[enemy+0x1F0] = isqrt(dx*dx + dz*dz)` por 0x451780 (0x4C0416..0x4C043A, antes da chamada 0x4C0449). Aproximação de zumbi (Routine 01 02, 0x453010) lê `ebp = [esi+0x1F0]` e procura jogador abaixo de 0x4B0 (1200) no mesmo piso (+0x106 contra 0x989FF6). Mover jogador no hook sem recalcular distância não funcionou no host (zumbi parado a 850 do representante por 25 s) e fazia cópias decidirem pelo jogador cliente (Routine_1 3 contra 2 no host).
- `Pl_damage` (0x4DCA40, dano e modo, retorna 0 vivo / 1 / 2 morto) escreve Life 0x98A046 e indicadores 0x98A044/0x98A0C3; ao morrer, marca bit 0x4000000 de 0x989E6C fora do bloco. Proteção agora também preserva esse bit.
- Controle original (A sozinha, cooperativo desligado, três zumbis, 45 s): agarram (zumbi `01 03 xx`, Leon `05 01 xx`), mordem 20 cada (Leon 50 -> 30 -> 10 -> 0), recuam (`01 05`, afastam), Leon morre (`06`). Nenhum zumbi morreu sozinho.

re2coop local, protocolo 6:
- No host, inimigo mais próximo do representante cliente que do jogador host (histerese de 20%) mira no representante. Movimento em PlayerShield com jogador host sobre ele (Pos, Old, Sca_old, distância em cache), representante afastado e hook na entrada de Pl_damage (`push esi; call 0x50AAA0`, 6 bytes) registrando dano/modo. Pacote 5 envia ao cliente (reenvio por 0,5 s, seq uma vez); cliente chama Pl_damage, preservando regras de dificuldade, morte e indicadores. Snapshot marca alvo representante (bit 7 de Be); proteção cliente então mantém jogador no lugar para esse inimigo.

Observado (`qa/attacktest.py`, host andou cerca de 2600, zumbi criado a 900 do cliente): zumbi host mudou de alvo, aproximou, agarrou (`01 03 03`); 4 mordidas de 20 chegaram uma vez cada (Life 200 -> 170 -> 140 -> 110 -> 90, Pl_damage retornou 0); jogador host ficou em 200. Duas cópias do zumbi mantiveram estado igual.

QA em 2026-10-28, steam-mock e udp: `qa_suite.py` 33/33 cada, enemytest/mirrortest/hittest 11/11 cada; `attacktest.py` 8/8 em 5 de 6 (uma vez host em Routine_0 5 sem perder Life; hipótese: zumbi recuando passou perto); `multitest.py` 17/17 em 5 de 6 (uma vez três zumbis host morreram sem golpe).

Problemas/desconhecidos:
- Jogadora cliente não anima agarrão, só perde Life; zumbi agarra ar ao lado dela.
- Após agarrar representante, zumbi host recua muito (4000-5000 unidades; original menor); hipótese: cálculo usa posição real do jogador host.
- Raro, cerca de 1 em 6 multitest, também antes da etapa 2b: zumbi vai de `01 01 05 00` a `07 00 00 00`, Life -1, sem golpe. Causa desconhecida, não vista no controle original.

## <a id="session-2026-10-28-night-packet-loss-a-rooms-own-enemies-kill-flags-made-host-authoritative"></a>Sessão 2026-10-28 (noite): perda de pacotes, inimigos próprios da sala e mortes com autoridade do host

Perda: `[test] loss=N` descarta N% dos pacotes de saída nas duas cópias; `qa_suite.py` define por `RE2COOP_LOSS`. Executado em udp, perda confirmada nos dois logs:
- 25%: `qa_suite.py` 33/33, `hittest` 11/11, `mirrortest --shoot` 11/11, `attacktest` 8/8 duas vezes, `multitest` 17/17 duas vezes.
- 50%: todos os testes inimigos passam (hittest, mirrortest, attacktest, multitest); `qa_suite.py` 31/33: representante ficou ocioso com host correndo ("puppet runs while host runs", modos [6]) e atrasou 2087. Não investigado.

Inimigos próprios da sala (comando 5 = viajar por porta fictícia à fase/sala/posição):
- Levantamento no salvamento "Leon A_02" (fase 0 sala 0x0F): salas com entidades: 0x00 (6 tipo 0x1F), 0x01 (0x48), 0x03 (9 de 0x1F), 0x04 (6 de 0x1F), **0x05 (3 zumbis 0x10, vagas 2-4)**, 0x07 (três 0x1F, 0x13), 0x09 (cinco 0x21), 0x18, 0x19, 0x1A (0x12), 0x1B. Identidade dos tipos além de 0x10 desconhecida aqui.
- `qa/roomtest.py` (fase 0 sala 0x05): host viaja, cliente segue; mesmos zumbis nas mesmas vagas, snapshot lista todos, diferença p90 28-63, estado igual 149/150. Cliente mata um (pistola Leon, dano 14, Life host de teste 10): morre nos dois, bit de morte marca em ambos (byte 0 de 0x98EB74: 0x08 -> 0x28); ao sair/voltar continua ausente, outros retornam.

**Indicadores de morte eram combinados por OR nos dois sentidos; agora somente host -> cliente, copiados integralmente.** Encontrado quando `roomtest` perdia outro zumbi a cada execução sem arquivos mudarem: B às vezes carregava outro salvamento (tecla perdida no menu de `session.py`), follow_host o levava à sala host, e OR bidirecional injetava bits daquele salvamento e mortes de teste anteriores ainda na memória de B no jogo novo do host. Evidência: A sozinha, cooperativo desligado, carrega 0x98EB74 com bytes A_02 em offset 0x3D8 (`08070000071b00e01c7c...`); em cooperativo, tinha bytes A_08 com OR 0x30. Em jogo real cada um carrega seu salvamento; mesclagem antiga corromperia mundo host. Protocolo 7. Mortes cliente ainda chegam pelos golpes (parte 4) e retornam como bits host. `session.py` agora imprime sala carregada antes de follow_host; `enemylib.start_pair` reinicia ambos se diferirem.

Formato observado: arquivo de 2048 bytes, SAVE_DATA bruto (Stage_no em 0x378, Enemy_flg em 0x3D8).

QA após alteração, 2026-10-28 cerca de 05:50, duas cópias num PC; steam-mock e udp, cada um: `qa_suite.py` 33/33, `enemytest.py` 11/11, `mirrortest.py --shoot` 11/11, `hittest.py` 11/11, `multitest.py` 17/17, `attacktest.py` 8/8, `roomtest.py` 11/11 em 3 de 3 (três zumbis em toda execução).

## <a id="session-2026-10-28-early-morning-other-enemy-types-a-door-back-into-the-same-room"></a>Sessão 2026-10-28 (madrugada): outros inimigos e porta para a mesma sala

`qa/roomtest.py` aceita `RE2COOP_ROOM` / `RE2COOP_TYPE` e `--no-kill` (só presença, vagas, acompanhamento, estado). Fase 0 no A_02, executado em 2026-10-28 por udp: sala 0x03 (9 tipo 0x1F, vagas 2-10) 7/7, p90 31; sala 0x07 (tipo 0x13, vaga 5) 7/7, p90 196; 0x09 (cinco 0x21) e 0x1A (0x12) 7/7 após correção abaixo. Identidade desses tipos desconhecida aqui.

**Falha: porta para a própria sala.** Cliente falhava em 0x4C0669 (sombras, `mov eax, [edi+0x14]` com edi = [entity+0x16C] = 0xA343D100) no representante em 0x09 sempre que era enviado à sala atual. Plugin só detectava mudança por fase/sala, não percebia reconstrução e criava representante durante carregamento; ponteiro da sombra era sobrescrito após verificações pré-loop (proteção pKage nunca disparava). Correção: porta ativa (byte superior de Stop_flg 0x989ED4) conta como troca e adia criação; tentativa de apenas atrasar a 90 quadros de controle não resolveu e fez `qa_suite` não achar representantes após seguir host; voltou a 20.

Também: entidades em_set ficam inativas com pKage fora de 0x988904..+0x68*48 (estruturas de sombra; entradas de inimigos não alinham ao 0x988904 do jogador, por exemplo 0x988D38, 0x988DA0). Em partidas reais, falha atingiria qualquer porta para a mesma sala.

QA ao fim da noite, duas cópias num PC:
- Bateria completa com correção e atraso de 90 (06:25-06:52): steam-mock `qa_suite.py` 31/33, udp 32/33 (representantes ainda invisíveis 1,5 s após seguir, pelo atraso); todo restante passou nos dois: enemytest/mirrortest/hittest 11/11, multitest 17/17, attacktest 8/8, roomtest 11/11; udp `roomtest --no-kill` em 0x03, 0x07, 0x09, 0x1A, cada 7/7; nenhum CRASH nos logs.
- Após voltar a 20 (06:55-07:04): `qa_suite.py` steam-mock 33/33, udp 33/33; `roomtest --no-kill` 0x09 7/7 duas vezes; `roomtest` 0x05 11/11; nenhum CRASH. Testes inimigos não repetidos após reversão, pois atraso só controla criação do representante.

## <a id="session-2026-10-28-day-shared-items-and-story-flags"></a>Sessão 2026-10-28 (dia): itens e história compartilhados

Decisão do usuário: itens e indicadores de história **compartilhados** (item coletado some para ambos; porta destrancada abre para ambos). Autoridade host, como mortes.

Observações estáticas de bio2.exe Sourcenext 1.1.0:
- `0x503120` Flg_on(ULONG* array, n), `0x503140` Flg_off, `0x503170` Flg_ck: bit `0x80000000 >> (n & 31)` do dword `n >> 5`. Flg_on tem 48 chamadores, Flg_off 6.
- Coleta marca bit por Flg_on em `0x4FDFFB` / `0x4FD996`: array SaveData+0x418 (`0x98EBB4`) nas fases 0-3, SaveData+0x438 (`0x98EBD4`) da fase 4 em diante. Número é word nos dados AOT.
- Tabela AOT: `0x988850` (ponteiros), contagem byte `0x98E528`. Entrada: Sce, Sat, piso, super, X, Z, W, D (int16), depois dados; item Sce 2: identificador, quantidade e indicador (words +0x0C/+0x0E/+0x10). Tratadores em `0x53B46C` (Sce 1 porta `0x4E9460`, Sce 2 item `0x4E96C0`).
- Verificação `0x4E9150`: posição do jogador mais deslocamento 620 (0x26C), girado por Cdir_y; passagem de botão roda com `0x200000` nos indicadores Status `0x989ED0`.
- Key_flg (SaveData+0x590, `0x98ED2C`) lido pelo código da porta (`0x4E94C0`, `0x4E9589`).

Observado ao vivo, duas cópias, salvamento 1:
- Salas da fase 0 com itens AOT (indicador entre parênteses): 0x05 (4), 0x06 item 30 x3 (7), 0x09 (13), 0x0E (105, 106), 0x11 (55), 0x12 (22), 0x13 (18), 0x15 (40, 209), 0x16 (57, 59).
- Com Item_flg bit 7 marcado no host e copiado, cliente reentrando em 0x06 não tem mais o AOT de item (antes tinha indicador 7).

Comportamento atual re2coop (v8 local, sem push):
- Intervalos SaveData compartilhados: +0x390..0x3D0 (Scenario_flg, Common_flg), +0x418..0x484 (Item_flg, Item_flg2, Item_c_flg, Map flags), +0x584..0x598 (File_flg, Zapping_flg, Key_flg). Não Room_flg, Enemy_flg (mortes, tipo 2) nem Pri_be_flg.
- Tipo 6, host -> cliente, 4/s durante jogo: cópia host adotada pelo cliente.
- Tipo 7, cliente -> host: Flg_on/Flg_off substituídos por cópias do plugin (jmp de 5 bytes), que no cliente registram cada bit marcado/limpo em intervalo compartilhado. Enviados 4/s até aparecer na cópia host. Primeira versão comparava memória à última cópia host e redefinia base quando jogo saía do loop (carregar salvamento). Abandonada: loop também para em mensagens de coleta e portas, sobrescrevendo coletas feitas ali.
- Comando de depuração 6: chama Flg_on/Flg_off (array, bit, ligado).

QA em 2026-10-28: `qa/storytest.py` 16/16 em udp, steam-mock e udp com 30% de perda. `qa_suite.py` 33/33 em udp e steam-mock; udp com 30%: 32/33, falhou "puppet never further than snap distance" (máximo 1653), problema sob perda visto a 50% na noite anterior; não investigado.

Pendente / desconhecido:
- Resolvido depois no mesmo dia, abaixo: coleta real pelo bot falhou inicialmente; logo após viajar, quadrado nada define.
- Feito depois no mesmo dia, abaixo: item coletado pelo outro na mesma sala ficava visível até reentrar.
- Escritas diretas nos arrays sem Flg_on/Flg_off (busca capstone em .text por operandos de memória nos intervalos, 13 resultados): byte inferior de `0x98EBD0` (SaveData+0x434, último dword Item_flg) é estado de quebra-cabeça escrito em `0x4CB6F0`, `0x4E3A82`, `0x4E3A9C` (qual, desconhecido); Zapping_flg (+0x588/+0x58C) é copiado inteiro em `0x4B7759`. Outros 8 são Item_work em `[i*4 + 0x98ED30]` (índice começando em 1). Esses dois, escritos no cliente, serão sobrescritos; vence estado do host.
- Inventários continuam separados (Item_work por jogador).
- Falha de B em `0x4E2AF2` veio de escrita de depuração -1 em `0x98EAE4` (índice AOT lido pelo jogo), não do plugin.

Coleta real pelo bot, mais tarde em 2026-10-28:
- Logo após viagem de depuração, jogador em Routine `01 00 00 00`; quadrado nada faz. Após um toque em cross (Routine `01 00 01 00`), quadrado marca `0x200000` e, olhando a mesa de 0x06 de (-25252, 3801), Cdir_y 2048, abre mensagem (Status `0x8000`). Quadrado confirma (fitas de tinta 1 -> 4, bit 7 marcado pelo jogo). Motivo do toque cross desconhecido. `pickuptest.py` repete cross + quadrado até 4 vezes.
- Máquina de escrever (AOT Sce 9) compartilha retângulo: após coletar, quadrado abre pedido de salvar; confirmar gasta fita e grava arquivo. Uma execução fez isso em A (novo `Leon A_03_...` em `savedata`, removido manualmente dali). Teste agora cancela por cross e confere ausência de arquivo novo.
- `qa/pickuptest.py` (ambos em 0x06; um coleta pelos botões, outro recebe bit e não mensagem): 11/11 tanto cliente quanto host coletando, em udp com 30% (3 execuções), steam-mock e udp sem perda (ambas as ordens); `qa_suite.py` 33/33 e `storytest.py` 16/16 em steam-mock e udp na mesma série.

Item coletado pelo outro na mesma sala, mais tarde em 2026-10-28:
- Estático: após Flg_on, coleta em `0x4FE005` lê MD1 (byte +6 dos dados); se não for 0xFF, zera Be_flg do objeto em `0x98A61C + MD1 * 0x1F8`, ocultando modelo.
- re2coop faz igual quando bit Item_flg (fases 0-3) ou +0x438 (4+) muda 0 -> 1 por pacote do par (cliente: cópia host; host: alteração cliente), e AOT Sce 2 da sala contém o bit. SharedBlock `items_hidden` conta isso.
- `pickuptest.py` 13/13 (udp e steam-mock, ambas as ordens; qa_suite 33/33 e storytest 16/16 na mesma série): modelo do item 0x06 (MD1 3, Be_flg 0xB nos dois) chega a Be_flg 0 no outro em até 2 s, sem sair. Só conferido na memória: capturas saíram pretas nesse momento, sem conferência visual.
