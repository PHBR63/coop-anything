# <a id="g3-together-runtime-qa-2026-10-17-to-2026-10-20"></a>QA em execução de G3 Together (2026-10-17 a 2026-10-20)

Evidências do nível de QA de G3 Together em [README.md](README.md). IDs de execução e nomes de séries se referem às pastas e logs privados do usuário; não estão publicados. Código-fonte e suítes do mod: [GGM1k3y23/g3-together](https://github.com/GGM1k3y23/g3-together). O teste anterior de Myrtana Accord está resumido em [OTHER-PROJECTS.md](OTHER-PROJECTS.md).

## <a id="tested-stack"></a>Conjunto testado

- Compilação Steam 1037023, `Gothic3.exe` 1.75.20108.14 (Community Patch 1.75.14), x86, arquivos Parallel Universe Patch presentes, balanceamento alternativo ativo.
- Myrtana Accord e o auxiliar de QA antigo movidos para quarentena nas cópias de teste.
- Dois pares de cópias completas da instalação (host e cliente em cada), cada cópia com perfil próprio redirecionado. Par 1 usa UDP 34567; par 2, 34568; cada um tem trava de QA e pasta de execução próprias.
- Os dois jogos de um par rodam no mesmo PC e conectam por 127.0.0.1.

## <a id="how-a-suite-runs"></a>Como uma suíte executa

1. O executor confere os comprovantes de isolamento do par e calcula hashes da pasta real de salvamentos do usuário.
2. Inicia a cópia host, espera o bot interno responder, envia `releaselock` (o jogo fecha seu próprio identificador `GenomeMutex`) e inicia o cliente da mesma forma. Um jogo que encerra cedo (outro detinha o mutex) é reiniciado após pausa aleatória de 3 a 12 s.
3. O bot inicia novo jogo pelo menu (foco e Enter enfileirados para a própria janela), e o executor envia Escape uma vez quando a introdução bloquearia o loop.
4. A suíte envia comandos numerados (teleportar, golpear, pegar, salvar, diálogo, ...) e consulta os logs do mod dos dois jogos buscando o estado exigido.
5. Ao final de uma suíte de dois jogadores, os monitores de invariantes executam (abaixo), ambos os jogos fecham normalmente e o executor confere encerramentos e hashes de salvamentos.
6. Uma etapa exige 3 aprovações consecutivas e controle negativo com falha (recurso desativado por comando QA), mantendo as suítes anteriores aprovadas.

## <a id="invariant-monitors-report-only"></a>Monitores de invariantes (apenas relatam)

Com ambos os jogos rodando, o executor lê os NPCs perto dos dois heróis três vezes, a intervalos de 3 s. Uma ocorrência conta somente se aparecer nas três amostras.

| Regra | Significado |
|---|---|
| `dead_mismatch` | morto numa máquina, vivo na outra |
| `double_sim` | visto nas duas, espelhado em nenhuma: ambas o simulam |
| `foreign_ai` | uma entidade espelhada executa tarefa própria |
| `drift` | vivo nas duas, a mais de 5 m de distância |
| `hp_mismatch` | vivo nas duas, com pontos de vida diferentes |
| `no_motion` | vivo, totalmente sem movimento (pose em T) |

Autoteste `invariantself`: o cliente para de aceitar capturas dos NPCs do host, fazendo as duas máquinas simularem os mesmos NPCs; os monitores devem relatar `double_sim`. Execuções anteriores de desenvolvimento falharam (nenhuma violação antes de cortar o fluxo de capturas). Na versão final, passou em `20261019-175827-together` e `20261019-194507-together`; o controle negativo `20261019-180006-together` (sem corte) não relatou nada e falhou como esperado. A execução `20261019-194507-together` relatou `double_sim`, `drift` e `hp_mismatch` em saqueadores e companheiros de Ardea.

## <a id="runtime-trace"></a>Registro de rastreamento em execução

Desativado por padrão; comando QA `trace on|all|off` ou `trace = on` no INI. Insere hooks no início dos movimentos do motor e nos definidores de tarefas do jogo, escrevendo `g3trace.log` na pasta do jogo: tempo, corpo (espelhado ou representante), movimento ou tarefa e chamador como módulo+RVA. A suíte `tracediag` passou 3 de 3; o caminho por INI, 1 de 1; o controle negativo (nenhum arquivo escrito) se comportou como exigido. A primeira execução de `tracediag` falhou na estrutura de testes: o executor não conseguiu apagar um `g3trace.log` ainda aberto pelo jogo.

## <a id="results-2026-10-19"></a>Resultados, 2026-10-19

| Série | Execuções | Resultado |
|---|---|---|
| Regressão completa (37 suítes, incluindo V1 a V5) | série `20261019a` | 36 de 37 passaram. `stage2` falhou uma vez: representante do cliente executou `ZS_HangAround` por cerca de 2 s no host. Depois, `stage2` passou 4 vezes. Causa encontrada e corrigida em 2026-10-20 (abaixo) |
| Etapa T e vizinhas | série `20261019b` | `stageT` 3 de 3; outras 14 suítes passaram; `stageE3` falhou uma vez (Lester não seguiu após teleporte; IA do jogo) e passou em 2 repetições |
| Sondagem paralela, dois pares simultâneos (`stage2`, `stage3b`, `stageA` em cada) | `parallel-probe-p1`, `-p2` | 5 de 6 passaram; a falha foi a rara ação conhecida do representante em `stage2`. Uma inicialização encontrou o mutex ocupado e foi repetida automaticamente |
| Regressão completa com monitores de invariantes (38 suítes) | `20261019-180209-together` a `20261019-191307-together` | 37 de 38 passaram. Monitores não encontraram violação persistente em nenhuma suíte. `stage3c` falhou ("Client earned 500 XP for kills it had no part in"): desde E1, um cliente pode controlar saqueadores e concluir a missão da invasão sozinho, cuja recompensa compartilhada é permitida. Teste ajustado; `20261019-192246-together` passou, controle negativo `20261019-192435-together` falhou como esperado |
| P3a (eliminações por companheiros e invocações) | série `20261019-p3a`, `-p3a2` | 3 de 3, controle negativo `partyxpoff` falhou como esperado; `stageE3`, `stageE4`, `invariantself` passaram |
| Etapa L (saltar até o parceiro) | `20261019-194701-together` a `-195110-together` | 3 de 3, controle negativo falhou como esperado |
| Meteoro P1 (par 2) | série `p2-stageP1` | 3 de 3, controle negativo `summoncopyhero` falhou como esperado (a cópia matou o alvo outra vez) |
| Regressão pré-empacotamento (9 suítes) | série `20261019-pre-package` | 8 de 9 passaram. `stage3b` falhou em `20261019-195533-together`: orc aparou o golpe de teste (`ZS_ParadeStumble`, 0 dano, nada a relatar). Agora o teste golpeia até 3 vezes se o alvo aparar. Reexecução `20261019-201518-together` passou, controle negativo `20261019-201712-together` falhou como esperado |
| Após o rastreamento em execução (7 suítes) | série `20261019-trace-reg` | 7 de 7 passaram (`stage3b`, `stageA2`, `stageE2`, `stageE3`, `stageV4`, `stageL`, `stageP3a`) |
| `master` incorporada, `dff5cfa` | `20261019-205329-together-p2`, `-205555-together-p2`, `-205901-together-p2` | `stageP1`, `stageP3a`, `stageL` passaram. Regressão completa de `master` no par 2 (41 suítes) havia começado; resultado desconhecido aqui |

Todas as execuções acima terminaram sem alterar os salvamentos reais do usuário.

## <a id="results-2026-10-20"></a>Resultados, 2026-10-20

Das notas dos agentes ([NOTES.md](NOTES.md)); este relato não reexecutou nenhum deles.

| Série | Execuções | Resultado |
|---|---|---|
| Flechas P2, primeira versão (par 2, `ce6c5c7`) | `stageP2`, `20261020-083728` a `-091232-together-p2` | 1 de 3 passou. Toda flecha encontrada pela varredura foi anunciada e copiada (6 de 6 na execução aprovada), cópias de 0 a 16 graus diferentes da original. Falhas: flecha do bot parou no próprio corpo na postura ociosa; uma varredura não encontrou flecha (`spawned=0`). Controle negativo `shotmirroroff` falhou como esperado. Este commit antecede a correção de mortos espelhados, então o cliente ainda mostrava orcs mortos em pé |
| Experimento 0, contatos de flechas | `20261020-122311-together-p2` | Somente diagnóstico. Flechas do host atingiram baú e casa antes do alvo; flechas do cliente atingiram a própria espada e coluna do atirador e ficaram presas |
| Correção da ação do representante (`a4da3aa`) | série `series-20261020-cont20`, DLL `b0ec5c94…` | `stage2` 19 de 20; `ZS_HangAround` em representantes 0 de 20 execuções (antes: ao menos uma vez em 63 de 63 execuções rastreadas). A falha é outro caso, ainda aberto (representante 1 a 2 m atrás de cliente correndo sob golpes de orcs). Regressão nessa DLL 15 de 16; `stageP1` falhou por erro do teste e passou 2 de 2 após a correção |
| Impacto de flecha contado uma vez (`875d676`) | `stageP2hit`, alvo Hamlar | Toda flecha que chegou foi aplicada exatamente uma vez no host; 2 de 4 execuções passaram (uma sem flecha do host chegar em 8 tentativas, outra abortada após travamento do host); reexecução posterior passou: 3 de 5, não três consecutivas. Controle negativo `shotcopyhero` falhou como esperado (golpe duplo). Nenhum virote de besta alcançou o alvo |
| Bola de fogo P2f (`ba72045`) | `stageP2fire` | 3 de 3; bolas de fogo do host e cliente alcançaram Hamlar e foram aplicadas uma vez (a do cliente como reivindicação). Controle negativo `shotcopyhero` falhou como esperado |
| Duração de criaturas invocadas (`760af83`) | `stageCreatureLife`, `20261020-185021`, `-185346`, `-185644-together-p2` | 3 de 3 passaram e o controle negativo `20261020-185959-together-p2` falhou, mas a revisão estática encontrou seis criaturas espelhadas vivas congeladas no host em todas as três após o cliente se afastar 50 m: a suíte rejeita apenas `free`, não `mirrored`. Não comprova o fim da criatura |

## <a id="results-2026-10-17-and-2026-10-18-summary"></a>Resultados, 2026-10-17 e 2026-10-18 (resumo)

- Etapas 1 a 5c, 3c, P: cada uma 3 de 3 mais controle negativo com falha, em 2026-10-17.
- Etapas A, A2, B, C, D1 a D3b, G, G2, H, H3, E1 a E5, Q, V1 a V4: cada uma 3 de 3 mais controle negativo com falha, em 2026-10-18, com regressão completa após cada bloco (25 e depois 32 suítes, todas aprovadas no fim).
- Teste prolongado: 22 min com 320 ações aleatórias com semente, depois 55 min com 738 ações (75 carregamentos, 59 salvamentos, 55 quedas com ajuda, 53 separações): nenhuma ação falhou, nenhum encerramento inesperado, encerramentos normais. Memória de trabalho do host estabilizou em cerca de 1,25 GB; cliente, 1,0 GB. Usou compilação mais antiga (anterior às etapas V e posteriores).
- Primeira inspeção humana em 2026-10-18 (usuário, duas janelas num PC): inimigos ignoravam o jogador remoto e o cliente não via lutas. Viraram etapas V1 e V2, corrigidas e testadas por bots; uma segunda inspeção encontrou orcs em pose T, corrigidos ao reproduzir ataques como movimentos de combate do jogo.

## <a id="not-covered-by-any-suite"></a>Não coberto por nenhuma suíte

Jogo real pela internet, mais de dois jogadores, campanha completa, tela real de comércio e diálogo de cama, teclas reais durante a jogabilidade (bots definem as mesmas tarefas e estados de uma tecla), monstros atingindo herói incapacitado, lutas e salvamentos durante transformação, fim de criatura invocada com jogadores distantes e aplicação exatamente uma vez para virotes de besta.
