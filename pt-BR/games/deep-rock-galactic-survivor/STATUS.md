# <a id="status--ist--soll"></a>Estado: Ist / Soll

Modo cooperativo de Deep Rock Galactic: Survivor. **Fonte única de referência** para o que está verificado, o que falta e o significado de "concluído". Última atualização: **2026-10-20**.

Compilação testada: Steam buildid **23854500**, Unity **6000.4.7f1**, metadados IL2CPP **39**. Identidade completa e hashes: [notes/01-core.md](notes/01-core.md).

## <a id="how-to-read-this"></a>Como ler

- **Ist** = verificado por execução de teste neste projeto, nos dois papéis, com linha `RESULT: … PASS` e ID da execução. Código existente sem execução **não** é Ist.
- **Soll** = requisitos de projeto fixados e critérios de aceitação dos marcos.
- **Lacuna** = item Soll com Ist parcial ou aberto.

Símbolos: ✅ verificado · ⚠️ parcial / só código / afirmação não comprovada · ❌ aberto ou defeituoso.

**O significado de ✅ aqui:** execução automatizada de duas instâncias em **um PC**. **Nenhuma linha tem confirmação humana ainda.** O primeiro teste real em dois PCs (2026-10-21) contradisse várias linhas ✅; agora estão marcadas com ‡ e listadas na próxima seção. Preserve essa distinção: automação aprovada não significa que uma pessoa viu funcionar.

## <a id="goal-ledger-2026-10-21-mission-sync-goal-red--green--twin"></a>Registro do objetivo de 2026-10-21 (sincronização de missão): falha / aprovação / variante

Exploração e medições: [notes/08-mission-sync.md](notes/08-mission-sync.md). Verificação: `coop-run.ps1 -Ui -Lobby -EscortCheck [-EscortClient]` (Escort, setor 1, nó 1, perigo 2; bots de teste; `escort-report.py` compara Bobby e listas de objetivos dos dois logs). **Confirmação humana: nenhuma.** IDs são pastas em `local/work/runs/`. A DLL mudou durante o objetivo; a repetição final de todas as linhas na DLL distribuída é listada no fim desta seção quando existir.

| Etapa | Falha (veredito) | Aprovação (veredito) | Variante / opção |
|---|---|---|---|
| 2 Fim natural de etapa com bots (sem forçar fim) | Antes dos bots: nenhuma execução passou de `MISSED_DROPPOD`. | `20261021-114845-worlddiff` (anão host embarca, etapa termina, cliente segue `stage: peer ended its stage`). | `-coopescortbot`, `-coopescortfuel`, `-coopescortdet`, `-coopdropbot` são apenas opções de teste. |
| 4 Bobby acompanha o host no cliente (G10, G12) | `20261021-121436-worlddiff` (FAIL: `posMax=129.4` m, `clientArm=0`). | `20261021-123846-worlddiff` (PASS: `posMean=0.99 posMax=3.56`, 0 divergências de estado / objetivos, `clientArm=3`). | `-coopescortsyncoff -coopobjlegacy` |
| 4 Parceiro conta para Bobby (G11) | `20261021-131705-worlddiff` (FAIL: `hostMoved=0`; host a 120 m, cliente escolta). | `20261021-130744-worlddiff` e `20261021-131249-worlddiff` (ambos PASS: `hostMoved=129/130`, `posMax=2.38/1.14`). | `-coopescortsyncoff` |
| 3 Objetivo secundário da etapa 2+ igual (G14) | `20261021-124304-worlddiff` (FAIL: `seedMismatch=2`; antes: `20261021-122836-worlddiff`, etapa 2 host `COLLECT`, cliente `LEVEL_PICKUP`, `objMismatch=7`). | `20261021-123846-worlddiff` (PASS: `seedMismatch=0`, `objMismatch=0`). | `-coopobjstageseedoff` |

| 4 Combustível coletado pelo cliente chega a Bobby (G13) | `20261021-132808-worlddiff` (FAIL: `hostMoved=0`, `-coopfuelgiftoff`; também `20261021-160440-worlddiff`). | `20261021-132352-worlddiff` (PASS: só carteira cliente, `hostMoved=129`, host `fuelReceived=3600`); `20261021-160023-worlddiff` (PASS). | `-coopfuelgiftoff`. Limite: teste põe combustível na carteira por `Wallet.Add`; coleta natural no cliente não exercitada. |
| 4 Detonador armado de um lado fica armado do outro | `20261021-163841-worlddiff` (FAIL: cliente danifica detonadores, host `hostArm4=0`). | `20261021-163408-worlddiff` (PASS: `hostArm4=12`). | `-coopdetsyncoff`. Descoberta: hooks em `TNTDetonator.SetArmed` / `Die` nunca disparam (armamento ocorre no código nativo); cada lado consulta o objeto `obstacle` (1 -> 0 ao armar). |
| 6 Fim da partida chega ao cliente como tela final (G8) | `20261021-165529-worlddiff` (FAIL: host `end screen setup condition=MISSED_DROPPOD`, nada no cliente); antes da correção `20261021-114352-worlddiff`. | `20261021-165233-worlddiff` e `20261021-170427-worlddiff` (PASS: tela cliente 0,2 s após host, mesma condição, 0 subidas de nível após fim). | `-coopruneendsyncoff`. `-coopclientpodholdoff` e `-coopxpafterendoff` aplicadas, mas variantes não diferem da aprovação neste cenário. |
| Cápsula do cliente não deve encerrar sua partida sozinha | `20261021-163408-worlddiff` (cliente `MISSED_DROPPOD` 4,9 s antes do host; captura humana "Mission gescheitert" com host ainda jogando). | Par `20261021-171238-worlddiff` (aprovação) / `20261021-171731-worlddiff` (`-coopclientpodholdoff`) não produziu tela final no intervalo em nenhum lado; não demonstra nada: **aplicado, não comprovado**. Evidência indireta: nas execuções G8 posteriores, cliente nunca termina antes do host (0,2 s depois). | `-coopclientpodholdoff` |
| Bloqueio de ataque de anão caído (por estado) | `20261021-151718-downedlock` e `20261021-161643-downedlock` (FAIL, bloqueio desligado: `attackRanWhileDowned=102..120`, `attackBlocked=0`). | `20261021-151422-downedlock`, `20261021-151550-downedlock`, `20261021-161512-downedlock` (PASS: armas pausadas enquanto caído, `attackBlocked=105..128`). | `-coopdownednolock`. Por estado (todos os tratadores `paused`), não contagem de tiros: contador não vê a arma própria. |
| Jogo inicia com mod em sessão interativa da área de trabalho | `20261021-115426-menu` ... travamento 5 s após início (WER `coreclr.dll c0000005`). | Jogo + plugin ativos por 30 s com sessão interativa; execuções desta seção. | Bisseção, causa e regra para próximos hooks em [notes/08-mission-sync.md](notes/08-mission-sync.md). |

Correções no mod: `CoopEscort` (pacote de estado Bobby a 5 Hz host -> cliente, `Bobby.Update` do cliente omitido, host empresta posição do parceiro a `Bobby.Update` naquela chamada para alcance/combustível funcionarem); `CoopObjective` (byte de tipo por objetivo, evitando escrever lista maior do host na vaga errada; aumentos passam pelo `AddProgress` do próprio jogo, executando eventos de conclusão e, com eles, ARM_TNT e cápsula no cliente; cliente espera semente nova dos objetivos secundários em vez de reutilizar a anterior). Correção do bot: `CoopAuto` responde novamente a uma subida de nível encadeada ("congelamento" anterior com `timeScale 0` era o bot respondendo cada formulário só uma vez: `20261021-111555-worlddiff`, `20261021-114003-worlddiff`).

Testes básicos na DLL do ZIP (sha256 `417D9D3F...A484`): `menu` `20261021-171754-menu` PASS, `lobby-start -ProfileScrub -AdoptCheck -MapSync` `20261021-171834-lobby-start` PASS (MAPSYNC, ADOPT), `downedlock` `20261021-172001-downedlock` PASS; `disconnect` cliente sai `20261021-164555-disconnect` PASS, host sai `20261021-164727-disconnect` PASS, referência `-NoPeerLoss` `20261021-164851-disconnect` FAIL como esperado (esses últimos na DLL anterior do mesmo dia).

**Aberto após este objetivo (não concluído):** cápsula de suprimentos / marcadores (nunca acionados, origem desconhecida), chefe e vitória natural (nenhum bot conclui missão), setor 2 e segundo bioma (G2), engasgos dos inimigos (medição por quadro `-coopsmooth` existe; janela cliente gerou poucos quadros para leitura útil), orbes XP no chão: criação idêntica (`orb-report.py`, diferença média +0,1 em 36 pares, `20261021-162915-worlddiff`), mas após coleta cliente manteve 3 orbes a mais em `20261021-162406-enemyerr` (aberto), divergência dos totais XP (G-open), coleta natural de combustível no cliente, barreira da loja.

**Confirmação humana: nenhuma.** ZIP com esta DLL preparado para teste humano.

## <a id="goal-ledger-2026-10-21-overnight-run-red--green--counter-probe-per-step"></a>Registro do objetivo de 2026-10-21 (execução noturna): falha / aprovação / contraprova por etapa

"Falha" = execução com correção desligada (variante de mutação, mesmo caminho do comportamento antigo) ou medição anterior; cada ID é uma pasta de `local/work/runs/` com `result.txt` (vereditos conferidos em 2026-10-21 06:55). Detalhes e limites nas linhas abaixo. **Confirmação humana: nenhuma.**

| Etapa | Falha (veredito) | Aprovação (veredito) | Contraprova / variante |
|---|---|---|---|
| 1 Disputa da semente | `20261021-015440-lobby-start` (FAIL, impressões `MAPSYNC` diferem). | `20261021-015526-lobby-start` (PASS). | `-coopnomapwait` |
| 2 Desbloqueios do host por padrão | `20261021-032004-lobby-start` (FAIL, `ADOPT` 0 classes). | `20261021-031556-lobby-start` (PASS, 4 classes). | `-coopnoadopt` |
| 3 Segunda partida / botão CO-OP | `20261021-035552-secondrun` (FAIL, `button=0`), `20261021-040929-secondrun` (FAIL, sem partida 2). | `20261021-040500-secondrun` (PASS, 2 partidas, impressões iguais). | `-coopmenubuttonsolo`, `-coopnolobbyreset` |
| 4 Caído: não mover, não atirar, reanimar | `20261021-053700-downedlock` (FAIL, `attackRanWhileDowned=5867`), `20261021-041450-downedlock` (FAIL, movimento). | `20261021-053530-downedlock` (PASS), `20261021-041620-downedlock` (PASS). | `-coopdownednolock` |
| 5 Classe/visual nos dois sentidos | `20261021-042015-skin` (FAIL, host `applied=0`). | `20261021-042344-skin` (PASS em ambos). | `-coopskinhostonly` |
| 6 Barreira (G1) | `20261021-042819-barrier` (FAIL, host `holdMax=45.0s`). | `20261021-043130-barrier` (150 s PASS), `20261021-065116-barrier` (600 s PASS, 20 escolhas, 0 estouros). | `-coopbarrierold` |
| 7 Câmera = jogo base | `20261021-044036-cameravanilla` (FAIL, `installed=1`). | `20261021-044148-cameravanilla` (PASS). | `-coopcameraon` |
| 8 Sem cliques visíveis do assistente | `20261021-073753-lobby-start` (FAIL, cobertura desligada, quadros 0/0). | `20261021-073709-lobby-start` (PASS, quadros 107/110). | `-coopnostartcover`; limite: presença da sobreposição, sem captura (sessão bloqueada). |
| 9 Proxy de latência | `20261021-060510-lobby-start` (FAIL, `LAGCHECK` 0 pacotes), `lagproxy.py --selftest-mutant` (FAIL como esperado). | `20261021-060554-lobby-start` (PASS), `--selftest` PASS. | `-LagBypass`, proxy mutante. |
| 10 Estados a 10 Hz + latência | `20261021-053053-enemyerr` (FAIL, p95 1,55 m > 0,8, 2 Hz). | `20261021-053209-enemyerr` (PASS, p95 0,09 m); perfis `20261021-052438` (p150), `-052554` (p50), `-052712` (p300), `-053327` (interrupção durante partida), todos PASS com `NOFREEZE`. | `-coopsnaphz=2` |

**Repetição de toda variante negativa e seu par aprovado na DLL distribuída** (sha256 0BB17FF5…4049; cobertura da etapa 8 adicionada depois: veja linha de regressão para DLL EEA95351…0A1A, agora em `local/release/DrgSurvivorCoop-mod.zip`; ordem do script `local/work/logs/s15`, 2026-10-21 06:57-07:30; todos os vereditos lidos de `result.txt`):

| Etapa | Falha na DLL distribuída | Aprovação na DLL distribuída |
|---|---|---|
| 1 | `20261021-065756-lobby-start` FAIL (`-coopnomapwait`, cliente `haveConfig=False`). | `20261021-065844-lobby-start` PASS (`check: mapwait`, `haveConfig=True`). |
| 2 | `20261021-070211-lobby-start` FAIL (`-coopnoadopt`). | `20261021-065239-lobby-start` PASS (`ADOPT: PASS`, 4 classes). |
| 3 | `20261021-070325-secondrun` FAIL (`-coopmenubuttonsolo`), `20261021-070657-secondrun` FAIL (`-coopnolobbyreset`). | `20261021-065545-secondrun` PASS (2 partidas, impressões iguais). |
| 4 | `20261021-070827-downedlock` FAIL (`-coopdownednolock`). | `20261021-070957-downedlock` PASS. |
| 5 | `20261021-071049-skin` FAIL (`-coopskinhostonly`). | `20261021-071141-skin` PASS. |
| 6 | `20261021-071451-barrier` FAIL (`-coopbarrierold`, 150 s). | `20261021-071800-barrier` PASS (150 s); 600 s: `20261021-065116-barrier` PASS. Sem variante negativa da própria execução de 600 s: contraprova é a de 150 s acima (mesma opção, mesmo caminho). |
| 7 | `20261021-071912-cameravanilla` FAIL (`-coopcameraon`). | `20261021-072024-cameravanilla` PASS. |
| 8 | `20261021-073753-lobby-start` FAIL (`-coopnostartcover`, quadros 0/0). | `20261021-073709-lobby-start` PASS (107/110) e `20261021-073927-lobby-start` PASS (104/113) na DLL final. |
| 9 | `20261021-072108-lobby-start` FAIL (`-LagBypass`, `LAGCHECK` 0 pacotes). | `20261021-072152-lobby-start` PASS. |
| 10 | `20261021-072310-enemyerr` FAIL (2 Hz, p95 1,24 m > 0,8; ~11 kbit/s host→cliente). | `20261021-072428-enemyerr` PASS (10 Hz, p95 0,11 m; ~28 kbit/s); com latência na mesma compilação, `NOFREEZE` PASS: p150 `20261021-072545-enemyerr` (p95 0,20), p300 `20261021-072703-enemyerr` (p95 1,38, limite 5), interrupção na partida `20261021-072822-enemyerr` (p95 0,11, máximo 1,69). |

Limites mantidos: um PC / loopback, bots sem teclado, janelas em segundo plano a 7-8 fps, 12 amostras por execução de erro dos inimigos; **coluna de confirmação humana vazia por definição**.

**Repetição final na DLL distribuída EEA95351…0A1A** (a de `DrgSurvivorCoop-mod.zip`, 07:45-09:00, vereditos de `result.txt` e logs; esta é a tabela de referência, as duas acima são DLLs anteriores):

| Etapa | Falha (opção desligada) | Aprovação |
|---|---|---|
| 1 | `20261021-074609-lobby-start` FAIL (`-coopnomapwait`). | `20261021-074657-lobby-start` PASS. |
| 2 | `20261021-075024-lobby-start` FAIL (`-coopnoadopt`). | `20261021-073927-lobby-start` PASS (`ADOPT: PASS`). |
| 3 | `20261021-075138-secondrun` FAIL (`-coopmenubuttonsolo`), `20261021-075510-secondrun` FAIL (`-coopnolobbyreset`). | `20261021-074233-secondrun` PASS. |
| 4 | `20261021-075640-downedlock` FAIL (`-coopdownednolock`). | `20261021-075811-downedlock` PASS (também `…074404`). |
| 5 | `20261021-075903-skin` FAIL (`-coopskinhostonly`). | `20261021-075954-skin` PASS. |
| 6 | **10 min:** `20261021-082850-barrier` FAIL (`-coopbarrierold`: host `holdMax=45.0s`, 7 estouros, escolhas 10 contra 2); 150 s: `20261021-080304-barrier` FAIL (host `holdMax=45.0s`, 1 estouro). | **10 min:** `20261021-083931-barrier` PASS (20 escolhas, **0 estouros**, host holdMax 4,5 s, cliente 13,0 s, limite 30 s). Aprovações de 150 s oscilam nestes mapas: `…080614` FAIL (cliente holdMax 11,6 s > 10 s), `…084644` FAIL (só 2 escolhas, precisa 3); o teste de 150 s é básico, o par de 10 min é a evidência. |
| 7 | `20261021-080726-cameravanilla` FAIL (`-coopcameraon`). | `20261021-080838-cameravanilla` PASS. |
| 8 | `20261021-081726-lobby-start` FAIL (`-coopnostartcover`, `COVER` 0/0). | `20261021-081810-lobby-start` PASS; também `20261021-073927` (104/113). Só presença da cobertura, sem captura. |
| 9 | `20261021-080924-lobby-start` FAIL (`-LagBypass`). | `20261021-081007-lobby-start` PASS. |
| 10 | 2 Hz (`-coopsnaphz=2`), erro médio: `…084804` 0,43 m (p95 1,15), `…085039` 0,37 m (p95 1,23); `…085316` 0,07 m, mas só 61 pares em movimento, inválido. | 10 Hz, erro médio: `…084923` 0,17 m (p95 0,69), `…085157` 0,25 m (p95 0,85), `…085434` 0,17 m (p95 0,86). **Leitura honesta:** 10 Hz tem cerca de metade do erro médio de 2 Hz, mas nesta compilação limite p95 de 0,8 m não os separa claramente (10 Hz 0,69-0,86, 2 Hz 1,15-1,23); números anteriores 0,09-0,45 m (DLL anterior) ocorreram com inimigos/quadros mais calmos. Banda inalterada (~11 contra ~26-28 kbit/s). Perfis de latência na DLL final ainda não repetidos (tabela 0BB17FF5). |

**Perfis de latência na DLL distribuída EEA95351…0A1A** (todos `-Ui -Lobby -Test enemyerr -EnemyErr -NoFreeze -MapSync -LagCheck`; cada PASS = sem `hold timed out`, sem estouro de carregamento, sem perda de parceiro antes do veredito, cavernas iguais, tráfego proxy confirmado, p95 abaixo do limite):

| Perfil (um sentido) | Execução | Proxy (c2s / s2c / perdidos / duplicados / descartes por interrupção) | Erro médio / p95 / máximo |
|---|---|---|---|
| p50 | `20261021-085757-enemyerr` PASS | 699 / 1235 / 0 / 0 / 0 | 0,05 / 0,09 / 0,17 m |
| **p150** (150 ms ± 30, 2% de perda; exigência do objetivo) | `20261021-085916-enemyerr` PASS | 743 / 1170 / 33 / 0 / 0 | 0,32 / 0,94 / 1,49 m |
| p300 (5% perda, 1% duplicação) | `20261021-090034-enemyerr` PASS | 754 / 1197 / 81 / 15 / 0 | 0,78 / 1,81 / 2,29 m |
| Interrupção de 3 s na partida | `20261021-090152-enemyerr` PASS | 877 / 1292 / 0 / 0 / 231 | 0,34 / 1,00 / 4,61 m (recupera, sem desconectar). |

**2 Hz contra 10 Hz *sob* p150 na DLL distribuída** (3 pares, sem limite, só números; `movingPairs` = inimigos movidos > 1 m entre amostras, mínimo >= 100 para concluir algo):

| Execução | Frequência | média / p95 / máximo (m) | pares em movimento | válida? |
|---|---|---|---|---|
| `20261021-090500-enemyerr` | 2 Hz | 0,08 / 0,36 / 0,84 | 37 | Não (quase não se moveram). |
| `20261021-090619-enemyerr` | 10 Hz | 0,31 / 0,91 / 1,06 | 235 | Sim. |
| `20261021-090737-enemyerr` | 2 Hz | **0,72 / 2,09 / 5,17** | 223 | Sim. |
| `20261021-090856-enemyerr` | 10 Hz | 0,44 / 1,05 / 1,47 | 157 | Sim. |
| `20261021-091016-enemyerr` | 2 Hz | 0,09 / 0,36 / 0,51 | 76 | Não. |
| `20261021-091134-enemyerr` | 10 Hz | 0,47 / 1,12 / 1,70 | 273 | Sim. |

Leitura: sob p150 existe só **uma** execução válida a 2 Hz (média 0,72 m contra 0,31-0,47 nas três válidas a 10 Hz); outras duas a 2 Hz calmas demais. Melhora de 10 Hz **observada sem latência (vários pares) e em um par válido com latência, não estabelecida estatisticamente sob latência**; os perfis mostram ausência de congelamento e divergência a 10 Hz (acima).

(A aprovação da etapa 2 nesta DLL é `20261021-073927-lobby-start`: executada após compilação 07:3x, portanto EEA95351, não 0BB17FF5 anterior.)
## <a id="contradicted-by-the-first-real-two-pc-test-"></a>Contradições do primeiro teste real em dois PCs (‡)

| Linha | O que a pessoa viu / os logs mostraram | Estado |
|---|---|---|
| Caverna e semente compartilhadas | Mapas diferentes; log cliente: `map: seeded ... haveConfig=False` (semente alternativa 20261017) antes de chegar `RunConfig` do host. | ❌ disputa, correção planejada (cliente espera semente). |
| Representante do anão remoto + visual | Host via o anão cliente errado / não via; classe e visual só host→cliente; representante host tinha 4 renderizadores. | ❌ |
| Caído / reanimação | Jogador caído ainda se movia; reanimação nunca concluía. | ❌ (testes cobriam só temporizador). |
| Movimento dos inimigos | Atrasado, aos trancos no cliente (estados a 2 Hz). | ⚠️ parte do projeto até então. |
| Cliente com desbloqueios do host | Adoção desligada por padrão; cliente só jogava Scout. | ❌ |
| Botão CO-OP | Ausente após terminar partida. | ❌ |
| Início da sala | Cliques do assistente acontecem visivelmente "sozinhos". | ⚠️ cosmético. |
| Câmera | Afasta sem limite quando anões se separam. | ⚠️ previsto assim, precisa limite. |

## <a id="ist--verified"></a>Ist: verificado

Linhas com ID foram verificadas naquela execução; interface reexecutada em 2026-10-20. Sem ID, herdadas da matriz anterior de [README.md](README.md#qa), que lista os IDs; não reexecutadas nesta organização das notas.

### <a id="foundation-and-world"></a>Base e mundo

| Área | Estado | Evidência (execução) | Notas |
|---|---|---|---|
| Duas instâncias, transporte | ✅ | Parceiro conectado, contadores nos dois sentidos. | LiteNetLib 2.1.4, UDP 9050, 20 Hz. |
| Caverna, semente, impressão compartilhadas ‡ | ✅ automatizado; confirmação humana: — | 0/81 amostras diferem. | Prefixo `MapGenerator.CreateMap`. | **Disputa da semente corrigida em 2026-10-21:** cliente espera configuração da partida antes de gerar caverna (`CoopMapSync.WaitForRunConfig`, máximo 40 s). Falha (variante `-coopnomapwait`, configuração atrasada 3 s): `20261021-015440-lobby-start`, `MAPSYNC: FAIL`, cliente usou alternativa 20261017. Aprovação (mesmo atraso, correção ativa): `20261021-015526-lobby-start`, `MAPSYNC: PASS`, impressões iguais. Verificação: `coop-run.ps1 -MapSync`.
| Representante do anão remoto + visual ‡ | ⚠️ | `puppet spawned renderers=9`; `20261020-030131-skin` (`applied=1`), negativo `030403`. | Representante é só apresentação. |
| Criação/morte/censo/estado de inimigos | ✅ | `enemy transport … fail=0`; `snapshot applied=… missed=…`. | Posições das réplicas interpoladas linearmente. |
| HP inimigo acompanha host | ✅ | `snapSeen=11 equal=6 drops=1/82`; `-coophpsoff` FAIL. | Cliente mostra números de dano próprios. |
| Criação/coleta/carteira de itens | ✅ | `loot credited`, `miss=0`; `sentCur`/`claimCur` correspondem. | Recursos compartilhados da partida. |
| Terreno (minerado) | ✅ | `terrain recv=3 mirrored=3 miss=0` | |
| XP compartilhado + pausa de subida de nível (G1) | ✅ automatizado por 150 s; confirmação humana: — | Aprovação `20261021-043130-barrier` (XP cliente atrasado 3 s deliberadamente: host `picks=6 holdMax=0.6s timeouts=0`, cliente `picks=6 holdMax=9.6s timeouts=0`); variante negativa `-coopbarrierold` `20261021-042819-barrier` (host `holdMax=45.0s`, isto é, tempo esgotado). | Barreira agora conta escolhas (cada lado envia número acumulado; enésima escolha local continua quando parceiro informou ao menos n), em vez de indicador apagado por `StartFlow` após parceiro já concluir. **Execução maior:** `20261021-060307-barrier` (480 s, mesmo atraso de 3 s, `-NoFreeze` PASS): `picks=11 timeouts=0`, host `holdMax=1.0s`, cliente `holdMax=7.0s`; **10 minutos completos aprovados:** `20261021-065116-barrier` (`-Seed 509820207 -ResultTimeoutSec 1100 -coopbarriersec=600 -coopbarriermaxhold=30`, XP cliente atrasado 3 s, `NOFREEZE` PASS): `picks=20 timeouts=0`, host `holdMax=2.8s`, cliente `holdMax=8.3s` (limite longo: sem espera acima de 30 s, portanto sem estouro de 45 s; teste curto de 150 s mantém 10 s). Execução anterior de 10 min com limite estrito de 10 s, `20261021-062813-barrier` (`-Seed 509820207 -ResultTimeoutSec 1100`, 600 s, `NOFREEZE` PASS): 19 escolhas por lado, **0 estouros**, host `holdMax=4.0s`, cliente `holdMax=18.1s`; sem estouros, mas relatou **FAIL** pelo limite mais estrito. Causa dos 18 s: na escolha #19, cliente chegou ao nível antes (XP total 2491,5 contra 2453 do host no mesmo instante), esperando host obter XP restante com mortes próprias enquanto cliente estava pausado na tela de escolha. É o projeto da barreira (ambos escolhem no mesmo nível), não mensagem perdida, mas mostra **totais XP divergindo em partida longa** (38 XP em 10 min), contrariando nota anterior de totais iguais: aberto, notes/05. Outras tentativas de 10 min: `20261021-055350-barrier` interrompida pelo limite de 600 s do inicializador (10 escolhas, espera máxima 3,7 s); `20261021-061635-barrier` (semente -1192758820) mapa degenerado onde bots não mataram nada (`picks=0`, 3670 inimigos vivos): descoberta sobre caso de teste, não resultado de sincronização. Barreira da loja intocada. Teste de 150 s é rápido; 9,6 s do cliente incluem atraso deliberado e espera própria, com limite 10 s. Verificação: `coop-run.ps1 -Ui -Lobby -Test barrier -ClientExtra '-coopxpdelay=3'`. |
| Cartas de nível por jogador | ✅ | `picked=3 skipped=0`, cartas diferentes por lado. | Não é escolha única compartilhada. |
| Objetivos | ✅ | `recv=26 applied=2 miss=0`, mesmos tipos. | |
| Adoção de configurações | ✅ | Cliente forçado ao nó 5 → `drift=1`; ambos leem configurações do host. | |
| Confirmação de prontidão | ✅ | `held=10.1s helloTx=7`; host `echo=1`; execução atrasada `held=20.3s`. | |
| Retransmissão de etapa + barreira da loja | ✅ | `starts=3`, `endsRemote=2`; `timedOut=0`. | |
| Caído / reanimação / círculo ‡ | ⚠️ | `revived hp=100 alive=True`; `hasFillFactor=1`, 329 atualizações. | Reanimação com 50% da vida máxima. |
| Desbloqueios do host chegam ao cliente pelo fluxo de sala distribuído ‡ | ✅ automatizado; confirmação humana: — | Aprovação `20261021-031556-lobby-start` (`ADOPT: PASS`, 4 classes adotadas, cliente escolhe classe que não possuía); variante negativa `-coopnoadopt` `20261021-032004-lobby-start` (`ADOPT: FAIL`, classe não selecionável). | Três defeitos por trás de "cliente só Scout": adoção desligada por padrão; envio do host atrás de `gc == null`, sem repetir quando SaveData ainda ilegível; sala nunca aplicava adoção (só fluxo do assistente), e botões não redesenhados. Verificação: `coop-run.ps1 -Ui -Lobby -Test lobby-start -ProfileScrub -AdoptCheck` (sem `-coopprofileadopt`). |
| Segunda partida na mesma sessão (botão CO-OP após partida) ‡ | ✅ automatizado; confirmação humana: — | Aprovação `20261021-040500-secondrun` (partida 1, vitória forçada, tela final, menu, **botão CO-OP presente**, segunda partida, `MAPSYNC: PASS runsHost=2 runsClient=2`); variantes negativas: `-coopmenubuttonsolo` `20261021-035552-secondrun` (`button=0`), `-coopnolobbyreset` `20261021-040929-secondrun` (sem segunda partida, `MAPSYNC: FAIL runs=1`). | Causas: botão só criado com papel `solo`; após partida, sala mantinha indicadores, `HaveRunConfig`, impressão do mapa e acionamento Play que reabria automaticamente. `CoopLobby.ResetForNextRun` limpa no menu; sala só reabre após CO-OP. Teste termina pelo mecanismo próprio do jogo, pressiona botão de menu da tela final e dispensa aviso de salvamento em andamento como jogador. |
| Anão caído não pode mover/atirar; reanimação conclui | ✅ automatizado; confirmação humana: — | Aprovação `20261021-053530-downedlock` (ataque: `attackBlockedWhileDowned=4593`, `attackRanWhileDowned=0`, 7070 ativações antes da morte; movimento bloqueado, 0 execuções; reanimado); variante negativa `-coopdownednolock` `20261021-053700-downedlock` (`attackRanWhileDowned=5867`, `blockedWhileDowned=0`, `ranWhileDowned=314`); par anterior só movimento `20261021-041620` / `041450`. | `BasePlayerMovement.UpdateMovement`, `WalkPlayerMovement.UpdateMovement`, `WeaponHandler.ActivateWeapon` não fazem nada enquanto anão local está caído, impedindo sair do círculo. **Limite:** bots não enviam caminhada; comprova supressão da etapa do jogo e ativações, não bloqueio de teclas humanas. Patch de ataque tem try/catch próprio, para falha de patch não desativar mod. |
| Classe/visual do representante do parceiro nos dois sentidos ‡ | ✅ automatizado; confirmação humana: — | Aprovação `20261021-042344-skin` (host `applied=1 meshes=4 remoteDwarf=1 localDwarf=0`, cliente `applied=1 meshes=5 remoteDwarf=0 localDwarf=1`, classes diferentes); variante negativa `-coopskinhostonly` `20261021-042015-skin` (host `applied=0`). | Dois defeitos: só host anunciava anão e só cliente trocava visual; representante host clonado antes de existir modelo da classe (`Model_<class>(Clone)`, contém PlayerSkin), sem vaga de visual (`renderers=4`); agora reconstruído ao aparecer modelo (`renderers=8`). Verificação: `coop-run.ps1 -Ui -Lobby -Test skin`. Objeto de arma/animação do representante sem cobertura. |
| Câmera permanece como jogo base (referência da decisão de projeto corrompida no original) | ✅ automatizado; confirmação humana: — | Aprovação `20261021-044148-cameravanilla` (`installed=0 follow=Player`); variante negativa `-coopcameraon` `20261021-044036-cameravanilla` (`installed=1 follow=CoopCameraFocus`). | Câmera de dois anões desligada por padrão. Números de distância/marcador só informativos (posição dos bots não controlada). Marcador tem teste `indicator`; última aprovação `20261020-172040-indicator` com câmera desligada (= novo padrão). **Repetição no fluxo autônomo falhou (`20261021-045225`, sem veredito): `OnGUI` nunca é chamado (`guiCalls=0`), então desenho IMGUI não pode ser testado sem interação.** |
| Início sem cliques visíveis do assistente (etapa 8) | ✅ automatizado **para cobertura ativa** (sobreposição uGUI, sem precisar OnGUI); ⚠️ pixels não capturados; confirmação humana: — | **Aprovação** `20261021-073709-lobby-start` (`COVER: PASS frames host=107 client=110`: atualizações com canvas, fundo opaco e painel de texto ativos na ordem 32767 durante controle do assistente), repetida na DLL final `20261021-073927-lobby-start` (104 / 113). **Variante negativa** `-coopnostartcover`: `20261021-073753-lobby-start` (`COVER: FAIL frames 0/0`). | Enquanto sala controla páginas do jogo (setor, nó, classe, perigo), cobertura opaca de tela inteira "STARTING RUN ..." as esconde até tela de carregamento (uGUI clonado do canvas da sala, mais cópia IMGUI). **Não demonstrado:** captura real da cobertura (nada capturável com sessão bloqueada: `quser` mostra sessão 2 Disconnected, `LogonUI.exe` ativo, `GetForegroundWindow()` NULL em 14 amostras) e formulários do jogo não desenhando acima de 32767. Primeira versão só IMGUI não testável porque `OnGUI` não é chamado sem janela em primeiro plano (`guiCalls=0`: `20261021-050307`, `-073143`, negativo `-073227`); por isso existe uGUI. Para ver: iniciar pela sala em área de trabalho desbloqueada. |
| Ferramenta de perturbação UDP (etapa 9) | ✅ automatizado; confirmação humana: — | **Aprovação:** `python lagproxy.py --selftest` PASS (none, p50, p150, p300, interrupção medidos com sockets reais); `lobby-start -Lag p150 -LagCheck` `20261021-060554-lobby-start` (`LAGCHECK: PASS c2s=252 s2c=311 lost=14`, `MAPSYNC` PASS em p150 anterior). **Controles negativos:** (a) `lagproxy.py --selftest-mutant` (proxy sem atraso, perda, duplicação) exibe `FAIL` em p50, p150, p300 e `MUTANT FAILED AS EXPECTED`; (b) `-LagBypass` (cliente entra direto, nada passa no proxy) `20261021-060510-lobby-start`: `LAGCHECK: FAIL c2s=0 s2c=0`. | `local/tools/lagproxy.py`, estrutura `-Lag none|p50|p150|p300|blackout` (cliente na porta 9051 via `-coopjoinport`), `-LagCheck`, `-LagBypass`. Atrasos por sentido. Um PC, loopback; temporizador Windows em 1 ms; mutante não cobre janela de interrupção (autoteste a define explicitamente). |
| Movimento inimigo no cliente: estados 2 Hz → 10 Hz (referência da decisão de projeto corrompida no original) | ✅ automatizado (loopback); confirmação humana: — | Erro de posição das réplicas contra originais do host nos mesmos instantes reais (`-Test enemyerr -EnemyErr`, 12 amostras, ~28-33 inimigos): **2 Hz** (`-coopsnaphz=2`) média/p95 = 0,46/1,36, 0,42/1,33, 0,49/1,62 m em `20261021-051648`, `-051924`, `-052201`; **10 Hz** = 0,13/0,40, 0,13/0,45, 0,14/0,40 m em `-051806`, `-052043`, `-052319`. Limite `-EnemyErrP95Max 0.8`: negativo 2 Hz `20261021-053053-enemyerr` **FAIL** (p95 1,55), positivo 10 Hz `20261021-053209-enemyerr` **PASS** (p95 0,09). | Envio agora por tempo (`SnapHz`, padrão 10), não `frameCount % 30`. Janelas em segundo plano aqui só a 7-8 fps; taxa medida ~7,2 rodadas/s, não 10 (num PC normal é maior). Par anterior (`-051037` 2 Hz, 333 inimigos) sem diferença (ambos p95 0,40), pois maioria parada; depende da quantidade em movimento, então só condições iguais comparadas acima. **Banda host→cliente** (proxy, ~66 s incluindo sala): ~11 kbit/s a 2 Hz contra ~26 a 10 Hz com ~30 inimigos; entrada de estado 17 bytes, ~1,4 kbit/s por inimigo a 10 Hz (300 ≈ 410 kbit/s brutos). Sem delta/filtro de distância. |
| Perfis de latência (atraso por sentido; RTT dobro) com 10 Hz | ✅ automatizado; confirmação humana: — | Mesmo teste por `lagproxy.py`, cada `NOFREEZE: PASS` (sem `hold timed out`, sem estouro de carregamento ou perda antes do veredito) e `MAPSYNC: PASS`: **p50** `20261021-052554-enemyerr` (média 0,22 / p95 0,54 m), **p150 = 150 ms ± 30 ms, 2% perda** `20261021-052438-enemyerr` (0,31 / 0,84 m; exigência do objetivo), **p300 = 300 ms, 5% perda, 1% duplicação** `20261021-052712-enemyerr` (0,54 / 1,26 m), **interrupção de 3 s na partida** `20261021-053327-enemyerr` (185 descartes; média 0,53, p95 2,10, máximo 7,63 m, recupera sem desconectar). | Limites: um PC/loopback, temporizador Windows em 1 ms no proxy, janelas limitadas, 12 amostras por execução. Limites p95 ≤ 3 m (p50..p150), ≤ 5 m (p300). Sem variante negativa de "não congela sob latência" (referência seria mesmo código; variante da barreira na linha XP). |
| Regressão após mudanças noturnas (todas autônomas `-Ui -Lobby`) | ✅ automatizado | **DLL distribuída (sha256 EEA95351…0A1A, cobertura uGUI):** menu `20261021-073841-menu`, lobby-start + MAPSYNC + ADOPT + COVER `20261021-073927-lobby-start`, disconnect `20261021-074053-disconnect`, segunda partida `20261021-074233-secondrun`, downedlock `20261021-074404-downedlock`, todos PASS. DLL anterior 0BB17FF5…4049: menu `20261021-065153`, lobby-start `-065239`, disconnect `-065405`, secondrun `-065545`; DLL mais antiga: `…053757-menu`, `…053843-lobby-start`, `…054009`/`…054143-disconnect`, `…054324-secondrun`. | `disconnect` pelo fluxo da sala (antigo `-Auto` exige clique real); `marker=off` esperado (sem IMGUI na sessão bloqueada). |
| Câmera enquadra ambos os anões ‡ | ⚠️ | `farVisible=19–20/20`; `-coopcameraoff` 5/20 e 1/20 → FAIL. | |
| Dano nos dois sentidos | ✅ | `sent=20 applied=20 dmgTotal=532`; recebido 8×10 HP. | Cliente relata, host aplica. |
| Visuais de combate | ✅ | Disparos nos dois sentidos; feixes, granadas, saída da arma, torreta, Bosco, rastros; negativos FAIL. | **Desenho de projétil não comprovado** (lacunas). |
| Teste contínuo de 10 minutos | ✅ | `20261020-040552-soak`, sem exceção/desconexão. | 2900/2915 inimigos, 618 mil estados. |
| Empacotamento de versão | ✅ | `20261020-145500-packageverify` | Cópia limpa, 132 interop, chainloader. |

### <a id="ui-and-flow"></a>Interface e fluxo

| Área | Estado | Evidência (execução) | Notas |
|---|---|---|---|
| Painel host/entrada interno (IMGUI) | ✅ | `RESULT: ui PASS`, `peer=1`. | `-coopui`, F8 oculta. |
| Botão CO-OP → conexão → sala | ✅ | `20261020-201108-menu`: `button=1 connect=1 peer=1 lobby=1` (repetido após correção Image). | Caminho canônico. |
| Estado da sala / barreira de prontidão | ✅ | `20261020-054247-lobby-state`; negativo `054515`. | Revisão do host, bloqueio de prontidão obsoleta. |
| Sala (estrutura/cliques) | ✅ | `20261020-201132-lobby-ui` (repetido após correção Image); negativo `-LobbyUIOff` `20261020-201926` FAIL (limite 420 s). | Contagens/cliques. |
| Visual da sala | ✅ | `20261020-202207-lobbyhold`, capturas passam `-VerifyPanel` em ambos. | Painel opaco, texto, botões; capacidade de falhar do oráculo comprovada. |
| Início pelo assistente ‡ | ⚠️ | `20261020-201214-lobby-start`, `run=1` (após correção Image). | Mesma fase, classes diferentes. |
| Espera na tela de carregamento | ✅ | `20261020-123303-loadform`, `held=1.4s`; negativo `123406`. | Formulário do jogo, pausado. |
| Mensagem de tempo de carregamento esgotado | ✅ | `20261020-172822-loadtimeout`: `timeout=1 form=1 text=1 held=30s`. | Host sozinho, sem parceiro. |
| BACK sai da sala | ✅ | `20261020-172235-lobby-back`: `active=0 left=1 peer=1`. | Protocolo continua ativo. |
| Marcador fora da tela | ✅ | `20261020-172040-indicator` (`offscreen`, `selfOnScreen=1`, 22–23 m); negativo `172202` (`state=off`). | Glifo direcional + distância. |
| Marcador `stale` / `downed` | ✅ | `20261020-202736-marker`: host `stale>0 downed=5 recovered=1`, cliente realmente morreu; negativo `-IndicatorOff` `20261020-202927` FAIL (`state=off`). | `-Test marker -CameraOff -StateSilent 5 -DownSelf`; `recovered` = saiu de `stale` após pacotes retomarem. |
| Parceiro perdido na partida, host permanece | ✅ | `20261020-212227-disconnect` (marcador `no-remote`, representante removido, aviso, partida continua); barreira de nível liberada na detecção `20261020-212435` (`holdReleasedAfter=0,0`); referência `-coopnopeerloss` FAIL: `20261020-205716` (representante e `HaveRemote` permanecem, marcador `stale`), `20261020-210213` (host congelado, `timeAdvanced=0,0`). | Detecção pelo tempo limite LiteNetLib, 5-10 s após processo sumir. |
| Parceiro perdido na partida, cliente permanece | ✅ | `20261020-214714-disconnect` (cliente termina pelo encerramento do jogo após 6 s, `runEnded=1`); host termina e sai: `20261020-214936`; referência FAIL `20261020-211301`. | Cliente não continua sozinho: inimigos são réplicas do host. |
| Missão Escort, mundo | ⚠️ | Bobby, 4 detonadores, zona TNT, combustível idênticos em `20261020-225926`, `230326`, `231931`. | Dinâmica não comprovada: Bobby nunca moveu (bots não escoltam), objetivo ficou 0. |
| Fim natural da missão | ⚠️ | Elimination terminou em ~440 s com `MISSED_DROPPOD` no host (`20261020-232755`); cliente recebeu fim de etapa, sem tela final em 10 s. | Chefe/vitória nunca alcançados (bots não usam cápsula); repetição `233928` interrompida (congelamentos de nível). |
| Biomas / perigos | ⚠️ | Ambos carregam e executam: Crystalline Cavern H1/H3, Salt Pits (Elimination, N4) H3: `20261020-222849`, `225527`, `230326`. | Escort em Salt Pits e setor 2 bloqueado no perfil; **setor 2 não inicia pela sala** (abaixo). |
| Início da sala no setor 2 | ❌ | `20261020-225053`, `20261020-231532`: `lobby: start no button for hazard`. | Botão clicável, assistente nunca conclui. |
| Pendências do censo de sincronização | ⚠️ | Escort em segundo bioma (bloqueado), Elimination setor 2 (não inicia, G2), chefe/vitória (bots não embarcam), tela final do cliente após host terminar (não comprovada). | Motivos e conclusão: "Pendências" de [notes/05-sync-gaps.md](notes/05-sync-gaps.md). |
| Censo das diferenças (`worlddiff`) | ✅ | Controle negativo `20261020-223954` (`GRUNT` 93 contra 0) e referência `223657`. | Medição, não sincronização: lista em [notes/05-sync-gaps.md](notes/05-sync-gaps.md). |
| Torreta cliente no host | ❌ | `Turret_LMG` host 0 / cliente 2,4-4,7 em 5 de 5. | Réplica só host→cliente. |
| Objetos de projéteis | ❌ | Ativos no host crescem 85 → 702 em 180 s (`222849`). | Réplicas de tiros do cliente não são limpas. |
| Loot bugs | ❌ | Cliente com exatamente dobro (`LOOTBUG` 7,4 contra 14,8 em `225926`). | Gerador local provavelmente não silenciado. |
| Reconectar na partida | ❌ | — | Não implementado; ambos reiniciam. |
| Pausa / ESC com parceiro | ⚠️ | Não medido. | Primeiro item do teste manual. |
| Menu cooperativo com mouse real | ✅ (tela de conexão) / ⚠️ (botões da sala) | Cliques do SO no jogo sem opções de teste: CO-OP abre, BACK fecha, HOST inicia (`net: host listening on udp 9050`), ESC fecha; regressões `20261020-235631-menu`, `235654-lobby-ui`, `235735-lobby-start`, `235802-lobby-back`. | Botões uGUI clonados nunca recebiam eventos de ponteiro (testes chamam `onClick.Invoke()`); camada invisível IMGUI agora cobre cada botão; os da sala após conexão ainda não clicados manualmente. |
| Visual da conexão | ✅ | `20261020-203105-connecthold` (`connect=1 hold=20s peer=1`), captura de ambos mostra `PEER CONNECTED`. | Tela imprime caminho completo de `coop-join.txt` (nome do usuário Windows): capturas fora da PR. |
| Convite / retransmissão Steam | ❌ | — | Não implementado. |

### <a id="the-ui-visual-defect-fixed-2026-10-20"></a>Defeito visual da interface (corrigido em 2026-10-20)

Sintoma: **Images** uGUI clonadas (fundo, painel, preenchimentos) não desenhadas, texto TMP fraco, arte da missão atravessando. **Causa raiz:** auxiliares escolhiam componentes por testes de tipo (`is`, `IsInstanceOfType`). Componentes de `GetComponents<Component>()` retornam como wrappers `Component` base nesta versão Il2CppInterop; testes não correspondiam, e `Destroy` adiado removia a **própria Image** (log após ativar: `img0/cr1` em clones limpos, `img1` só no controle intacto). CanvasRenderer não era problema (`cr1` sempre). Outro bug separado: canvas raiz esticado por âncoras 0/1 (resolvia 0x0); agora recebe tamanho do cliente.

**Correção:** preservar Image, Transform e CanvasRenderer pela identidade nativa `.Pointer` (`CloneImage`), resolver tipos preservados por `GetComponentsInChildren(Il2CppType.From(t))` (`StripExtras`). Evidências: `20261020-200837-lobbyhold` (sonda de amostras, todos `img1/cr1`, amostras desenhadas) e `20261020-202207-lobbyhold` (sem sonda): painel opaco, texto e botões dos dois lados; capturas passam no oráculo de pixels (`coop-shot.ps1 -VerifyPanel`: média 13,2, desvio 0,00; captura ruim conhecida tem média 56, desvio 25 e falha).

Ressalva restante: sprite `Btn_Campaign_Background` colorido via `Image.color` fica quase preto, então produção mantém `sprite = null` (quadrilátero simples colorido).
## <a id="soll--design-requirements-locked"></a>Soll: requisitos de projeto (fixados)

Fonte: `local/mod/DrgSurvivorCoop/PLAN.md` §4 (privado). Não alterar silenciosamente.

| ID | Requisito | Aceitação |
|---|---|---|
| S1 | **2 jogadores**, sem projeto para 4. | Host + um cliente. |
| S2 | Ambos sobem de nível juntos; **cada um escolhe a própria carta**. | Cartas diferentes, XP compartilhado; verificado. |
| S3 | Dificuldade permanece igual. | Sem ajuste pelo segundo anão. |
| S4 | Objetivos e itens totalmente compartilhados; **itens consumidos na coleta**. | Uma coleta remove dos dois. |
| S5 | Permanecer no círculo mais rápido com ambos; **perfuração exige ambos**. | Progresso / barreira de objetivo. |
| S6 | **Caído:** indicador fora da tela + círculo de reanimação de ~5 s. | Indicador + reanimação; verificado. |
| S7 | **Progressão permanente = perfil do host para ambos**. | Cliente nunca lê/escreve seu salvamento; host desbloqueia ambos. |
| S8 | Host escolhe missão; cliente entra na mesma. | Adoção automática; verificado. |
| S9 | Escopo: **só missões principais** (Elimination, Escort); Egg Hunt fora. | Caso de teste. |
| S10 | Entrada: host escolhe → parceiro entra **pelo Steam** → Ready → início. | Barreira por IP direto verificada; Steam aberto. |
| S11 | Ouro/Nitra compartilhados; host decide gastos. | Barreira da loja; verificado. |
| S12 | Um Bosco por jogador; uma cápsula de suprimentos, artefato próprio. | Réplica Bosco verificada. |
| S13 | Dano: armas cliente locais, cliente relata acertos, host aplica. | `EnemyHit`; verificado. |
| S14 | Interface nesta passagem: **só LAN/IP direto + marcador na partida**; sem painel de parceiro; Steam depois. | Botão de menu → conexão → sala. |
| S15 | QA visual usa **capturas externas** no caminho canônico de menu. | CopyFromScreen + primeiro plano; sem `-cooplobby`. |

## <a id="soll--ist-gap"></a>Lacunas Soll → Ist

| Soll | Ist | Lacuna | Próximo passo |
|---|---|---|---|
| S10 entrada Steam | Só IP direto. | Sem retransmissão/sala/convite Steam. | Autorização explícita; Spacewar 480. |
| S14 visual da sala | ✅ | — | Concluído em 2026-10-20 (`20261020-202207-lobbyhold`). |
| S14 tela de conexão | ✅ | — | Concluído em 2026-10-20 (`20261020-203105-connecthold`). |
| S6 detalhes do marcador | ✅ | `downed` baseado em HP, mostrado só fora da tela; reanimação nessa execução não integrou teste. | Reanimação em si coberta pela linha anterior de caído/reanimar. |
| S7 perfil host ‡ | Estrutura/leitura ao vivo nos testes; no real, cliente Scout, adoção desativada por padrão. | Equipamento parcial, marcos do cliente. | Host com equipamento; medição da tela final. |
| Barreira de subida de nível | ✅ nos testes. | Congelamentos de 45 s em partidas reais (G1). | Preservar conclusão antecipada do parceiro em `StartFlow`; medir espera no teste `levelup`. |
| Setor 2 da sala | Selecionável. | START nunca conclui (G2). | Descobrir ausência do botão de perigo; desativar setor por enquanto. |
| Outras diferenças (projéteis, loot bugs, torreta cliente, veios) | Lista do censo. | [notes/05-sync-gaps.md](notes/05-sync-gaps.md) | Ordem de correção no arquivo. |
| S9 Mastery | Só missões principais. | Caso de teste fixado. | Desbloquear ou excluir. |
| S13 visual de projétil | Criação ✅ | "Desenhado" não comprovado. | Comparação de quadros fora do processo. |
| S3-S5 agressividade/objetivos | Agressividade só host, sincronização de objetivos ✅ | Cliente sem agressividade própria (adiada). | Depois. |
| Teste em dois PCs | ZIPs verificados em cópia limpa. | Não instalado em ambos. | Lista de transferência §3-4. |

## <a id="definition-of-verified"></a>Definição de "verificado"

Uma afirmação só é verificada se atender a tudo:

1. Duas instâncias, ambos os papéis (salvo item explicitamente de um papel).
2. Linha `RESULT: <test> PASS` com ID em `local/work/runs/<stamp>-<test>/`.
3. Controle negativo quando existe opção (`-XOff` → FAIL).
4. Nenhuma exceção em qualquer log.
5. Para qualquer visual: captura de janela com **CopyFromScreen + primeiro plano**; `PrintWindow` omite a sobreposição nesta compilação.

"Código existe" nunca é relatado como verificado. Use ⚠️ com "só código".

## <a id="evidence-and-maintenance"></a>Evidências e manutenção

- Arquivo de execuções (privado, ignorado pelo Git): `local/work/runs/<stamp>-<test>/`, com logs e capturas por papel.
- Detalhamento público: [NOTES.md](NOTES.md) e [notes/](notes).
- Estado privado: `local/HANDOFF-current.md`; plano principal: `local/mod/DrgSurvivorCoop/PLAN.md`.
- Atualize após cada execução verificada. Mantenha cronologia em `notes/`; não duplique a matriz em `NOTES.md` ou `README.md`.
- Ao corrigir defeito, mova a linha de "lacuna" para "verificado" e cite a execução que comprova, incluindo controle negativo.
