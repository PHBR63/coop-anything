# <a id="what-is-still-not-in-sync-measured-2026-10-20-night"></a>O que ainda não está sincronizado (medido na noite de 2026-10-20)

Pergunta: após todas as sincronizações de recursos individuais, o que difere entre host e cliente numa fase em execução? Respondida com um censo em vez de raciocínio. Nada foi corrigido nesta passagem; esta é a lista e uma ordem.

Compilação testada: Steam buildid **23854500**, Unity 6000.4.7f1 (consulte [01-core.md](01-core.md)). Papéis em todas as execuções: host Driller / Interrogator, cliente Engineer / Maintenance, bots e modo invencível ativos.

## <a id="method"></a>Método

- **Censo (`-Test worlddiff`).** Após liberar a barreira de carregamento, as duas instâncias registram uma linha por `(category, object name)` em +30 s, +60 s, +120 s, depois a cada 60 s, 20 s após cada nova etapa e quando aparece a tela final: contagem e posição da primeira instância arredondada para 2 m. Categorias: `type:*` (inimigos por `id`, itens coletáveis, zonas de ativação, itens da fase, cápsulas de carga/extração, caixas de itens, projéteis, granadas, geradores) e `obj` (todo GameObject ativo fora da interface por nome, removendo `(Clone)` e números; essa é a rede de captura para classes em que ninguém pensou). O tempo é o **tempo do jogo** (escalado); uma pausa de subida de nível para o relógio daquele lado. Somente leitura: nada criado, movido ou enviado. Custo: cerca de 0,3 s por amostra por instância (engasgo visível, registrado como `wd-end ms=`), 3-9 amostras por execução.
- **Relatório (`worlddiff-report.ps1`).** Para cada rótulo de amostra, ambos os logs são colocados lado a lado. Rótulo em que os papéis estavam em **etapas diferentes** é marcado *não comparável* (execução `20261020-222849`, `t120`: host já na etapa 2, cliente na 1, mostrando 2.268 contra 0 blocos de terreno). Diferença menor que max(2, 10% da contagem maior) é ruído. Divergência só é **persistente** se mantiver o mesmo sinal em ao menos 3 amostras. Código de saída 1 significa ao menos uma divergência persistente.
- **Lista de exclusão** (três regras, cada qual informa quantas linhas ocultou): emissores de áudio em pool (`AudioSourceObject`), temporários sem nome (`New Game Object`), efeitos transitórios (`VFX_*`, `BasicDeathFX*`). Todo o restante permanece no relatório.
- **Execuções da matriz** chegam à segunda etapa pela ajuda existente `-StageEnd win -StageEndDelay 90`, exceto a execução natural. Seleção pelo host com botões reais da sala (`mission_`, `sector_`, `node_`, `hazard_`); botão bloqueado é registrado como `NOT CLICKABLE`, não ignorado.

## <a id="negative-control-the-census-can-fail"></a>Controle negativo (o censo consegue falhar)

| Execução | O que mudou | Resultado |
|---|---|---|
| `20261020-223657-worlddiff` | Nada (referência, 140 s). | Nenhuma linha `GRUNT`. |
| `20261020-223954-worlddiff` | Cliente `-coopworlddiffhide=Grunt` (omite o nome da contagem). | `GRUNT` host 93,3 contra cliente 0, persistente em 3 de 3 amostras. |

Duas opções que parecem controles, mas não são: `-NoMirror` (`20261020-222217`) só desativa visuais de combate, e `-coopboscooff` no cliente (`20261020-223311`) não muda nada observável no censo (a réplica de Bosco não é um objeto adicional nomeado). Nenhuma foi usada como controle.

## <a id="matrix"></a>Matriz

Todas as execuções: os dois papéis, bots; RESULT `worlddiff PASS` significa "medição concluída" (amostras coletadas, sem exceção), não "sincronizado". Duração = segundos de jogo após a liberação, cerca de 4 minutos reais por execução incluindo carregamento.

| # | Missão | Bioma | Setor/Nó | Perigo | Execução | Duração | Resultado |
|---|---|---|---|---|---|---|---|
| m1 | Elimination | Crystalline Cavern | S1 / N1 | H1 | `20261020-222849` | 200 s, etapa 2 amostrada | PASS (`t120` não comparável). Primeira tentativa `20261020-221809`: sem RESULT, consulte G9. |
| m3 | Elimination | Salt Pits | S1 / N4 | H3 | `20261020-225527` | 200 s, etapa 2 amostrada | PASS |
| m4 | Escort | Crystalline Cavern | S1 / N1 | H1 | `20261020-225926` | 200 s, etapa 2 amostrada | PASS |
| m5 | Escort | Crystalline Cavern | S1 / N1 (S2 e N3 não clicáveis) | H3 | `20261020-230326` | 200 s, etapa 2 amostrada | PASS |
| m6 | Escort | Crystalline Cavern | S1 / N1 (N4 não clicável) | H1 | `20261020-231931` | 200 s, etapa 2 amostrada | PASS |
| m2 | Elimination | - | **S2** / N1 | H1 | `20261020-225053`, repetição `20261020-231532` | - | **Não inicia**, nas duas vezes (G2). |
| m7 | Elimination, natural | Crystalline Cavern | S1 / N1 | H1 | `20261020-232755` | Terminou em 440 s (host). | PASS, terminou por `MISSED_DROPPOD`. |
| m7b | Elimination, natural | Crystalline Cavern | S1 / N1 | H1 | `20261020-233928` | ~10 min | Sem RESULT: interrompida pelo inicializador; 4 estouros de tempo de subida de nível no host e 1 no cliente (G1). |

Cobertura que **não** foi alcançada, com motivo: Escort em Salt Pits (nós além de N1 bloqueados nesse perfil), Escort no setor 2 (bloqueado), Elimination no setor 2 (selecionável, mas não inicia, G2), execução natural até vitória ou chefe (bots nunca usam a cápsula de extração; terminou por tempo esgotado).

## <a id="open-points-of-the-four-tasks-each-with-its-reason"></a>Pendências das quatro tarefas, cada uma com seu motivo

| Ponto solicitado | Estado | Por que está aberto | Como seria concluído |
|---|---|---|---|
| Escort em segundo bioma | Não medido. | Nós Escort além de N1 e setor 2 estão **bloqueados neste perfil** (`select ... node=3(NOT CLICKABLE)` em `20261020-231931`, `sector=1(NOT CLICKABLE) node=2(NOT CLICKABLE)` em `20261020-230326`). Desbloquear exigiria alterar o salvamento, não permitido aqui. | Perfil de teste com mais caminhos desbloqueados. |
| Elimination em segundo setor | Não inicia. | Setor 2 é clicável, mas START fica na página de perigo (`20261020-225053`, repetição `20261020-231532`); registrado como G2, causa desconhecida. | Corrigir G2 e repetir `-Wd 0,1,0,0`. |
| Dois biomas e dois níveis de perigo | Coberto. | Biomas: Crystalline Cavern e Salt Pits (Elimination, `225527`); perigos H1 e H3 (`222849`, `225527`, `225926`, `230326`). Salt Pits somente em Elimination, veja acima. | - |
| Execução natural até o fim da missão | Parcial. | `20261020-232755` rodou sem `-StageEnd` até o fim (440 s, `MISSED_DROPPOD`). Repetição `20261020-233928` sem RESULT: inicializador interrompe após ~10 min reais; esta perdeu ~3,7 min nos congelamentos de subida de nível (G1). Não é resultado da ferramenta: a execução estava em andamento quando foi interrompida, salvamentos restaurados. | Corrigir G1 e repetir. |
| Chefe e vitória dos dois lados | Não alcançado. | Bots nunca embarcam na cápsula; execução natural termina por tempo esgotado (`MISSED_DROPPOD`), não vitória; nenhum chefe surge antes. O censo não pode mostrá-los. | Comportamento de bot que jogue pelo objetivo e pela cápsula. |
| Se cliente mostra tela final própria após fim da partida do host | Não comprovado. | Host saiu 0,6 s após a tela final; não foi possível distinguir a tela própria do cliente daquela forçada pelo novo caminho de perda de parceiro (G8). | Repetir com ambos os papéis ativos (a ferramenta agora espera 35 s após o fim). |
| Controle negativo | Coberto. | Uma divergência persistente é o resultado esperado ao ocultar um nome; referência `223657` não tem nenhuma para esse nome. | - |
| `t120` de `20261020-222849` no relatório | Relatado, não ocultado. | Listado como *não comparável* (host etapa 2, cliente etapa 1) com números; nem comparado nem descartado silenciosamente. É regra do relatório, não entrada da lista de exclusão. | - |

## <a id="gap-list"></a>Lista de lacunas

Classes: **bloqueia a partida** / **visualmente errado** / **cosmético** / **esperado**. Frequência = execuções das 5 medições comparáveis (m1, m3-m6), salvo indicação.

### <a id="observed-evidence-in-the-logs"></a>Observadas (evidências nos logs)

| # | Lacuna | Classe | Frequência | Evidência |
|---|---|---|---|---|
| G1 | **Barreira de subida de nível congela a partida por 45 s.** O "concluído" do parceiro chega antes do início da subida local; `ResetBarrier` (em `LevelUpManager.StartFlow`) o apaga, e esse lado espera todo o prazo. | Bloqueia a partida. | Na execução observada, 5 estouros em 10 min (host 4, cliente 1); também 1 em cada `20261020-220651` e `20261020-222849`; relatado ao vivo como travamento de ~1 min. | `20261020-233928` host: `23:34:39.012 xp: remote picks done (localDone=True holding=False)`, `23:34:39.901 xp: barrier reset (StartFlow)`, `23:34:41.934 local picks done, holding until remote picks`, `23:35:26.948 xp: hold timed out after 45s`. Cliente já havia liberado em `23:34:41.956`. Código: `ResetBarrier` define `_remoteDone = false` (`CoopXp.cs`, linha 508 na execução). |
| G2 | **Setor 2 não inicia pela sala.** Botão do setor clicável, START executa o assistente, mas a página de perigo não tem botão para nível 1. | Bloqueia a partida. | 2 de 2 tentativas. | `20261020-225053`, `20261020-231532`: `lobby: start no button for hazard`, `page=HAZ`, etapa 394 e contando. Mesmo fluxo funciona no setor 1. |
| G3 | **Torreta do cliente não aparece no host.** Réplica só host→cliente (`CoopTurret.OnSpawn` retorna se não for host). Host recebe eventos de disparo, então tiros vêm do nada. | Visualmente errado. | 5/5 (exige classe cliente com torreta, aqui Engineer). | `Turret_LMG` host 0 / cliente 2,4-4,7 e `Turret_BASE` host 0 / cliente 2,2-2,3 em todas as amostras; `Head` e `FirePoint` (partes) acompanham. Log do host mostra disparos `skill=Sub_ProjectileWeaponSkill_LMG_Turret`. |
| G4 | **Objetos de projéteis ativos crescem sem limite no host** (e lentamente no cliente). | Visualmente errado / desempenho. | 5/5. | Host `type:Projectile` em t30/t60/t120/t180: 85/362/506/702 (`222849`), 128/252/515/806 (`225527`), 45/133/342/515 (`225926`); cliente 16/28/30/52, 23/41/66/101, 7/7/9/13. Host `combat=... fireRecv=614 hookMirror=614` em `225926`: cada tiro recebido cria projétil réplica. |
| G5 | **Dobro de loot bugs no cliente.** | Visualmente errado. | 5/5. | Médias host/cliente de `type:Enemy LOOTBUG`: 8/16 (`222849`), 5,8/11,6 (`225527`), 7,4/14,8 (`225926`), 6,2/12,4 e 6/12 nas outras duas; razão sempre 2,0. `BlobProjector` e `Projector` acompanham (decalques sob eles). |
| G6 | **Veios de recursos não idênticos.** Um tipo inteiro só existe de um lado. | Visualmente errado. | 4 de 5 execuções diferem em +30 s. | `MorkiteVein` host 16 / cliente 0 (`225926`); `EnorVein` host 1 / cliente 0 (`230326`); `NitraVein` 20 contra 16 (`231931`), `GoldVein` 26 contra 21 (`222849`) (os dois últimos podem ser mineração). |
| G7 | **Objetos Escort existem dos dois lados, idênticos** (Bobby, 4 detonadores, zona TNT, combustível, cápsula de sinalização). | Esperado (bom). | 3 de 3 execuções Escort. | `20261020-225926`: `Bobby=1`, `TNTDetonator=4`, `BobbyTNTZone=1`, `MaterialBlock_BobbyFuel` 8/8, `PickupBobbyFuel` 1/1 em t30 nos dois. |
| G8 | **Fim da partida chega ao cliente apenas como fim de etapa.** Após `MISSED_DROPPOD` do host, cliente registra `stage: peer ended its stage (condition=2) -> raising it locally`, sem tela final nos ~10 s seguintes; ela só apareceu pelo novo caminho de perda de parceiro (ABORT) após saída do host. | Visualmente errado (não confirmado). | 1 execução. | Log do cliente `20261020-232755` 23:27:30.6 (retransmissão) contra `watch: active=CoreOutro` 23:27:48.6 após `peerloss ending the run` 23:27:46.8. Repetição para esclarecer (`233928`) interrompida pelo inicializador (G1). |
| G9 | **Congelamento total esporádico.** Tempo do jogo de ambas as instâncias parou por 7+ minutos após três subidas de nível encadeadas, sem barreira em espera. | Bloqueia a partida. | 1 de ~17 execuções. | `20261020-221809`: última amostra `t120` às 22:10:23, sem `combat fire` após 22:11:06, atualizações continuam com posição e contagem de inimigos idênticas até o inicializador desistir. Não reproduzido em `222849`. Causa desconhecida; G1 é candidato no caso encadeado, mas não comprovado aqui. |

### <a id="derived-reasoned-from-the-observations-not-tested"></a>Deduções (raciocínio a partir das observações, não testado)

- G5: o gerador de loot bugs do cliente provavelmente não é silenciado como os geradores normais de inimigos; assim, cria os próprios insetos junto às réplicas dos do host (razão exatamente 2).
- G4: projéteis réplica dos pacotes `Fire` não são reciclados ao atingir algo; os projéteis próprios do host não crescem assim no cliente, que só recebe 11 tiros no mesmo intervalo.
- G1: a correção é manter um "concluído" pertencente à subida de nível atual em vez de apagar ambos os indicadores em `StartFlow`; o teste `levelup` existente não mede a duração da espera e passa mesmo assim.

### <a id="not-covered-and-why-unknown"></a>Sem cobertura e por quê (desconhecido)

- Dinâmica Escort: Bobby ficou na mesma posição dos dois lados por 180 s (`225926`, posição 30,32), e o objetivo ESCORT permaneceu em 0 porque bots nunca escoltam. Movimento, fases dos detonadores e fase TNT não medidos.
- Chefe e vitória: nunca alcançados (bots não usam a cápsula; terminou por tempo esgotado em ~440 s).
- Contagens de blocos de terreno diferem entre papéis em 10-15% em toda execução (`CC_Block_*`, `Top_*Damage`), e alguns itens mudam o sinal da diferença entre amostras (`LevelPickup_Apoca`, `LevelPickup_Boolo`). Terreno minerado é replicado com atraso, e os papéis mineram quantidades diferentes; provavelmente é sincronização temporal, não demonstrado como lacuna.
- Por que falta o botão de perigo no setor 2 (nível bloqueado nesse perfil ou página diferente).
- Parceiro que permanece conectado, mas para de responder (barreiras).
- Pausa / ESC e reconexão (fora do escopo desta passagem).
- Se o representante mostra o modelo da classe do parceiro: censo só mostra partes do modelo do anão local de cada lado; o representante é um único objeto `CoopPuppet(remote)`.

## <a id="suggested-order-of-fixing"></a>Ordem sugerida de correção

1. **G1** primeiro: afeta toda partida em minutos, custa 45 s por ocorrência e parece travamento para o jogador. Mudança pequena; adicionar verificação de duração da espera (nunca além de poucos segundos) ao teste `levelup`, para o PASS existente não escondê-la.
2. **G2:** uma sala oferecendo setor que não inicia é um beco sem saída. No mínimo, desativar o botão.
3. **G4:** reciclar projéteis réplica; crescem enquanto a partida durar.
4. **G5:** silenciar gerador de loot bugs do cliente (visível e altera itens).
5. **G3:** enviar a torreta do cliente ao host como a do host é enviada ao cliente.
6. Medir antes de corrigir: **G8** (fim de partida sem tela final no cliente), **G6** e **G9** (precisa reproduzir); dar aos bots comportamento Escort para medir a dinâmica.

## <a id="known-log-lines-that-are-not-new"></a>Linhas de log conhecidas que não são novas

`profile: read 'animator' failed` (host, também em execuções anteriores) e `loot: wallet credit failed` (cliente).

## <a id="update-2026-10-21-overnight-fixes"></a>Atualização de 2026-10-21 (correções noturnas)

| Lacuna | Estado |
|---|---|
| G1 congelamentos da barreira de subida de nível / loja (45 s) | **Corrigido na barreira de subida de nível**, contando escolhas em vez do indicador apagado por `StartFlow` (`20261021-043130-barrier`, variante `20261021-042819-barrier` com holdMax de 45 s). Barreira da loja não alterada (mesma estrutura, não reproduzida). Só 150 s de bots medidos, não 10 minutos (consulte STATUS para execução de 600 s, se houver). |
| Disputa da semente do mapa | Corrigida (cliente espera configuração do host). |
| Desbloqueios do host não adotados | Corrigido (ativado por padrão; host reenvia no menu; sala aplica; botões redesenhados). |
| Botão CO-OP / segunda partida | Corrigido (`CoopLobby.ResetForNextRun`, botão criado independentemente do papel). |
| Anão caído podia mover/atirar | Corrigido na etapa de movimento do jogo e na ativação de armas. |
| Classe/visual apenas host→cliente; representante do host sem vaga de visual | Ambos corrigidos. |
| Movimento de inimigos a 2 Hz | 10 Hz (por tempo). Banda cresce ~2,3× com ~30 inimigos. |
| Câmera | Voltou a acompanhar pelo mecanismo do jogo base (enquadramento dos dois anões desligado por padrão; `-coopcameraon` o reativa). |
| G2 setor 2 não inicia, G3 torreta cliente no host, G4 crescimento de projéteis, G5 itens em dobro, G6 veios | **Abertos**, não alterados. |

### <a id="mission-sync-findings-2026-10-21-goal-mission-sync-details-in-08-mission-syncmd"></a>Descobertas de sincronização de missão (2026-10-21, objetivo "mission sync"; detalhes em [08-mission-sync.md](08-mission-sync.md))

| ID | Descoberta | Estado |
|---|---|---|
| G10 | Bobby simulado por instância; nunca se moveu no cliente (`20261021-110753-worlddiff`). | Corrigido: `CoopEscort`, aprovação `20261021-123846-worlddiff`. |
| G11 | Parceiro não contava para alcance nem combustível de Bobby. | Corrigido (host fornece a posição do parceiro a `Bobby.Update`), aprovação `20261021-130744-worlddiff`. |
| G12 | Réplica dos objetivos escrevia diretamente no campo: eventos de conclusão nunca rodavam no cliente, ARM_TNT nunca existia ali, risco de deslocamento de índice. | Corrigido (byte de tipo + `AddProgress`), aprovação `20261021-123846-worlddiff`. |
| G13 | Combustível de Bobby é valor individual de carteira; combustível coletado pelo cliente não chega a Bobby do host. | Aberto. |
| G14 | Objetivos secundários da etapa 2+ diferiam (cliente usava semente da etapa anterior). | Corrigido (cliente espera semente nova), aprovação `20261021-123846-worlddiff`, falha `20261021-124304-worlddiff`. |
| Nota G9 | O "congelamento total esporádico após subidas encadeadas" muito provavelmente era o bot de teste respondendo apenas uma vez ao formulário encadeado (reproduzido e corrigido em `CoopAuto`, consulte STATUS). Não reapareceu em ~20 execuções após a correção. | Causa provável, não comprovada na execução original. |

### <a id="new-open-point-2026-10-21-10-min-barrier-run-20261021-062813-barrier"></a>Nova pendência (2026-10-21, execução de barreira de 10 min `20261021-062813-barrier`)

**Totais de XP divergem em partida longa:** no mesmo instante, cliente mostrava `total=2491.5` e host `total=2453.0` (nível 19 contra 18). A réplica de XP compartilhado (`XpGain`, solicitações de orbes) perde ou conta em dobro cerca de 38 XP em 10 minutos de bots (cliente também estava com atraso artificial de XP de 3 s). Efeito: um lado sobe de nível primeiro e espera o outro (18,1 s em uma ocasião). Não investigado; censo de `totalXp` dos dois lados a cada 30 s mostraria onde diverge. Também: semente do mapa `-1192758820` é um caso de teste em que os bots nunca matam um inimigo (`20261021-061635-barrier`).
