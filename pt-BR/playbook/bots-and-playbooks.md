# <a id="bots-and-playbooks-scripted-co-op-runs-with-a-state-check-after-every-step"></a>Bots e roteiros: sessões cooperativas por scripts com verificação de estado após cada etapa

[QA automatizado](automated-qa.md) define o que um teste precisa comprovar. Esta página apresenta os mecanismos reutilizáveis: **cenários** JSON que colocam cada instância em um estado inicial conhecido, **roteiros** que conduzem 2 a 4 bots por uma ação cooperativa e um pequeno **adaptador** escrito para seu jogo. Código em [`tools/scenarios`](../tools/scenarios/README.md) e [`tools/bots`](../tools/bots/README.md). Ambos funcionam primeiro sem jogo (em mundo cooperativo simulado); você pode vê-los passar e detectar bugs antes de integrar o jogo.

## <a id="the-three-layers"></a>As três camadas

```
scenario   JSON: start save, objects, setup, steps and checks      tools/scenarios
playbook   Python: what 2 to 4 bots do, what must be equal after    tools/bots/coopbots/playbooks
           every step
adapter    Python, one class per game: how one instance does it    your game (example: tools/bots/adapters/fnv)
```

* O **cenário** responde onde o teste começa. O executor recarrega o salvamento somente quando necessário; nos demais casos, redefine missões e indicadores no local. Assim, começar custa segundos, não um carregamento de salvamento.
* O **roteiro** responde o que os jogadores fazem e o que precisa ser verdadeiro em todos os lugares. Nunca altera o jogo diretamente. Chama métodos do adaptador, como `pickup`, `take`, `set_stage`.
* O **adaptador** responde como meu jogo faz isso. Uma primeira versão tem menos de 150 linhas. Métodos não implementados fazem os roteiros que precisam deles informar `SKIP`, nunca `PASS`.

## <a id="what-gets-checked-after-every-step"></a>O que é verificado após cada etapa

O executor, não o autor do roteiro, faz a parte repetitiva sempre:

1. **Estabilização.** Esperar todos os clientes informarem o número da última atualização do host. Sem esperas fixas.
2. **Janela silenciosa** (conexões degradadas). Nada é enviado por alguns segundos; todas as máquinas precisam ter convergido e nenhum reparo pode ocorrer.
3. **Comparação de capturas de estado.** Estado compartilhado do host contra cada cliente, caminho por caminho.
4. **Contadores de dessincronização** não podem aumentar: divergências, reparos, mensagens inválidas, aplicações com falha, realinhamentos forçados.
5. **Reparos por minuto** permanecem dentro de um limite (zero por padrão).
6. Em qualquer falha: pasta `FAIL-<n>-<step>/` com motivo, estado e captura de cada máquina e o que o adaptador registrar (logs, rastreamento de eventos), para localizar depois a primeira divergência.

Isso torna um roteiro melhor que uma asserção apenas no fim: o bug é detectado na etapa que o causou; uma execução aparentemente boa, mas com máquinas divergentes, ainda falha.

## <a id="which-bug-class-each-playbook-catches"></a>Que tipo de bug cada roteiro detecta

| Roteiro | Bug que ele procura |
|---|---|
| `fight` | morte que não chega a outra máquina; segunda morte contada quando dois jogadores atiram juntos; inimigo morto revivido por atualização obsoleta; inimigos duplicados |
| `loot_race` | dois jogadores recebem o mesmo item; item desaparece para todos |
| `container_share` | dois jogadores dentro de um contêiner; retirada ou depósito duplicado ou perdido; conteúdos divergentes entre máquinas |
| `door_lock` | estado de porta, fechadura ou terminal nunca visto por uma máquina; abertura de porta trancada |
| `dialogue_spectator` | segundo interlocutor com o mesmo NPC; espectador preso à visualização; script final executado só em uma máquina |
| `consent_vote` | etapa irreversível acionada quando o primeiro aprova, em vez do último; um "ainda não" que não a impede; acionamento duplo |
| `quest_sync` | etapas de missão ou indicadores de objetivos não aplicados por um lado; etapa repetida fazendo a missão avançar |
| `fast_travel_tether` | viagem sem consentimento ou durante combate; jogador vinculado que se afasta |
| `ownership_handoff` | controle de inimigo que não muda quando o host sai; controle oscilando entre lados; duplicatas após transferência |
| `save_load_rejoin` | jogador reconectado recebendo todas as recompensas novamente; cliente que não acompanha o carregamento de salvamento antigo pelo host |
| `spawn_once` | criação que aparece duas vezes em um cliente |

## <a id="getting-from-nothing-to-a-green-run"></a>Do zero a uma execução aprovada

1. **Execute os simulados.** `python -I tools/bots/run_coop.py --fake --playbook all`; depois adicione `--bug dup_pickup` a um roteiro e veja falhar. Leia `coopbots/fakecoop.py`: é um adaptador funcional e uma declaração das regras assumidas (host com autoridade, primeira coleta vence, barreiras aguardam todos).
2. **Escreva a interface do adaptador com o motor:** `status()`, `snapshot()`, `capture()`. Para `seq`, serve qualquer número de sequência ou hash de estado igual em todas as máquinas quando não há nada em trânsito. Coloque somente estado compartilhado em `snapshot()["shared"]`.
3. **Adicione ações uma por vez, na ordem exigida pelo roteiro.** Comece por `quest_sync` (definir e ler etapa), depois `loot_race`, depois `fight`. Execute o roteiro após cada implementação: `FAIL` mostra o comportamento do jogo, `SKIP` mostra o que falta.
4. **Verifique a pós-condição de toda ação.** `take` só está correto quando ambos os inventários mudaram pela mesma quantidade. Um bot que relata sucesso porque a chamada retornou produz aprovações vazias.
5. **Escreva cenários do jogo** (copie um arquivo de `tools/scenarios/examples/fnv`) com bloco `refs`, permitindo usar o mesmo arquivo no executor de cenários e no roteiro.
6. **Ative conexões degradadas** (`--link bad_wifi`) com o retransmissor de caos de [`tools/chaos`](../tools/chaos) entre instâncias, após a execução limpa passar.
7. **Comprove que os testes podem falhar.** Introduza um bug deliberado (desative uma mensagem de sincronização) e confirme que o roteiro correto falha. As opções `--bug` do mundo simulado são o modelo.

## <a id="rules-that-kept-the-results-honest"></a>Regras que mantiveram os resultados honestos

- **Pular não é passar.** O executor sai com código diferente de zero se nada passou e exibe `SKIP` com a ação ausente.
- **Uma etapa de cenário que o adaptador não consegue executar é `blocked`,** assim como todas as posteriores. O cenário termina como `partial`, nunca `pass`.
- **Compare por máquina.** Cada verificação roda em todos os jogadores-alvo. Detectar um bug que só aparece no convidado é o objetivo.
- **Disputas usam `parallel`.** `"parallel": true` executa uma etapa em todos os jogadores simultaneamente, uma thread por jogador.
- **Todo roteiro tem variantes.** Uma variante é o mesmo roteiro contra um mundo com um comportamento deliberadamente errado. Se ela passar, o roteiro não testava nada. As ferramentas incluem 27 variantes de roteiros, 20 de cenários e 15 do executor; seus comandos só exibem `ALL OK` quando todas são detectadas.
- **Sem entrada falsa.** O bot chama os scripts ou código do jogo como chegaria uma ação de jogador. Sem simular teclado ou mouse, sem captura da área de trabalho; veja [QA automatizado](automated-qa.md).
- **Assuma a responsabilidade pelos processos que iniciar** e encerre somente eles. Em um PC comum, execute instâncias com testes pesados uma sessão por vez ([fluxos com vários agentes](multi-agent-workflows.md)).

## <a id="example-the-fallout-new-vegas-port"></a>Exemplo: adaptação para Fallout: New Vegas

[fnv-coop](https://github.com/cranebeaker/fnv-coop) é onde essas ferramentas foram escritas. `tools/scenarios/examples/fnv` inclui quatro cenários (`fight`, `loot_race`, `quest_stage_sync`, `ownership_handoff`) e um adaptador de console; `tools/bots/adapters/fnv` inclui o adaptador de ações correspondente. São exemplos da estrutura, não uma afirmação de que o jogo está resolvido: o adaptador implementa o que sua lista `SKIP` não menciona.

## <a id="what-to-write-in-your-games-qa-section"></a>O que escrever na seção QA do jogo

- Quais roteiros rodaram, com quantos jogadores e as linhas de resumo (quantidades `PASS` e `SKIP`).
- Lista `SKIP` do adaptador: ações ainda ausentes no jogo.
- Se uma execução com perdas (`--link`) passou e qual perfil usou.
- Comandos das suítes e última saída.

## <a id="fast-rounds-resumable-steps-fail-fast-waits-game-speed-parallel-pairs-action-results"></a>Rodadas rápidas: retomada de etapas, esperas que falham cedo, velocidade do jogo, pares em paralelo, resultados de ações

Uma rodada de correção no jogo real é lenta pelo que você repete, não pelo que testa. Estes recursos do trabalho em Fallout: New Vegas agora estão nas ferramentas ([`tools/bots/README.md`](../tools/bots/README.md) traz os comandos):

- **Etapas retomáveis.** Escreva cada etapa para que as anteriores possam ser puladas: forneça uma função `arrange` que prepare o estado esperado (jogadores posicionados e armados, etapas anteriores definidas, inimigos anteriores mortos). Precisa ser idempotente e usar somente ações dos bots. `--from-step N` e `--only-step N` reexecutam uma etapa 4 com falha sem etapas 1 a 3 nem recarregar salvamento. Uma execução completa nunca prepara etapas dessa forma; aprovação parcial não é aprovação do roteiro: execute tudo antes de considerar a correção pronta. Se uma etapa não puder ser preparada (o inimigo necessário vivo já morreu), deve falhar e pedir "reload the scenario", não adivinhar.
- **Estabilização com falha antecipada.** Uma espera de sincronização sem progresso por alguns segundos não vai terminar bem. Pare quando nenhum número de atualização ou confirmação avançar durante a janela de estagnação e informe quem está atrasado e quanto, em vez de gastar todo o limite e exibir apenas timeout. Reparos não contam como progresso: repetir o mesmo reparo de divergência é um ciclo.
- **Velocidade do jogo.** Adicione um hook do adaptador para o multiplicador de tempo e a opção `--timescale X`. Defina após preparar o cenário; restaure 1 no final, em falha e em Ctrl-C; pare antes de qualquer etapa se uma cópia recusar (velocidades diferentes já geram dessincronização); reduza por X somente esperas fixas. Confira a velocidade lendo-a de volta quando o jogo permitir.
- **Pares em paralelo.** Cada par host/cliente é uma sessão própria, em porta própria; vários pares podem rodar juntos em um PC se houver RAM. Um executor por par como subprocesso, prefixo em cada linha de log, tabela PASS/FAIL combinada e códigos de saída distintos para "blocked" e "setup problem". Recuse iniciar se dois pares compartilham instância, porta ou pasta de saída. Isso aumenta a capacidade de processamento, não reduz uma rodada.
- **Resultados de ações.** Toda ação retorna `ok`, `reason` e `data`, verifica pré-condição antes e pós-condição depois e falha com `code: what the bot saw`: distância restante de caminhada travada, menu ou janela de mensagem no caminho, estado da arma, alvo perto demais ou íngreme demais para mirar. Permita ao adaptador listar o que bloqueia entrada (`blockers()`) e acrescente a lista a toda falha. Um motivo como "failed" custa uma rodada de diagnóstico toda vez. Guarde as últimas ações de cada máquina na pasta de falha.
