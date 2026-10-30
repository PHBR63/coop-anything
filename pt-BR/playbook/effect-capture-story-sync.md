# <a id="effect-capture-sync-a-story-by-recording-what-scripts-do-not-by-running-them-twice"></a>Captura de efeitos: sincronize a história registrando o que os scripts fazem, sem executá-los duas vezes

Relato de arquitetura para modo cooperativo em jogos de um jogador que contam histórias por scripts: missões, resultados de diálogos, gatilhos e eventos programados. Descreve como manter a história idêntica para todos e encontrar e corrigir divergências.

A ideia: **só o host executa scripts da história. Durante a execução, registra cada alteração primitiva feita no mundo. Essa lista de alterações ("lista de efeitos") é enviada aos clientes, que aplicam as mudanças diretamente sem executar o script.**

O exemplo é [fnv-coop](https://github.com/cranebeaker/fnv-coop), projeto cooperativo de Fallout: New Vegas. A arquitetura é independente de jogo. Onde se lê "etapa de missão", pode-se entender "indicador da história" no seu jogo.

Páginas relacionadas: [how-coop-mods-work.md](how-coop-mods-work.md) (estrutura geral), [networking.md](networking.md) (modelos e transportes), [network-chaos-testing.md](network-chaos-testing.md) (conexão degradada), [actor-ownership.md](actor-ownership.md) (responsável pela simulação), [desync-hunting.md](desync-hunting.md) (encontrar divergência), [fuzzing-coop-sync.md](fuzzing-coop-sync.md) (núcleo testado sem jogo).

## <a id="1-the-problem"></a>1. O problema

Um jogo narrativo de um jogador guarda progresso em tipos de estado: etapas de missões ou capítulos, objetivos, variáveis globais, personagem morto ou desativado, itens entregues, reputação e muitas variáveis de scripts. Scripts alteram isso quando o jogador termina conversa, entra em gatilho ou coleta item.

Ao adicionar jogadores, cada cópia mantém seus scripts. Sem intervenção, executa-os sozinha, e as histórias divergem. As duas correções óbvias falham.

| Correção óbvia | O que dá errado |
|---|---|
| **Repetir o gatilho em todo cliente.** Quando o host avança missão, mandar cada cliente avançar também, executando seus scripts. | Scripts de resultado rodam N vezes. Itens e recompensas duplicam. Personagens são criados duas vezes. Scripts que leem "o jogador" leem o errado. Sorteios dão resultados diferentes em cada máquina. |
| **Enviar só o novo número do estado.** Informar que a missão está na etapa 40. | Os efeitos colaterais de chegar à etapa 40 não ocorrem: porta não destranca, personagem não é ativado, item não é adicionado, próxima missão não começa. O número coincide, o mundo não. |

Skyrim Together Reborn e TES3MP enfrentam o mesmo problema e resolvem partes dele. TES3MP mantém diário, tópicos e facções no servidor e permite scripts locais. Skyrim Together deixa o líder do grupo avançar missões. Ambos descobriram que a história precisa de uma autoridade e registro compartilhado.

## <a id="2-the-idea"></a>2. A ideia

```
 host machine                                        client machine
 ------------                                        --------------
 story script runs  --> capture hooks record        apply effects directly
 (the only place)       each primitive change       (no script is run)
                        |                                  ^
                        v                                  |
                 one ordered, numbered transaction ---- network ----> client applies in order
                 (the effect list)                     acknowledge, resend, repair
```

Vantagens:

- **Sem duplicação.** O script rodou uma vez. Recompensas criadas uma vez, depois descritas como adicionar item X, quantidade 1, a cada destinatário.
- **Sem efeitos colaterais ausentes.** Toda mudança feita pelo script entra na lista.
- **Sorteios feitos uma vez.** Se o script escolheu item aleatório, a lista informa qual. Clientes nunca sorteiam.
- **Dados perfeitos para testes.** Toda transação é dado. Pode ser registrada, reproduzida em mundo simulado, comparada com jogo de um jogador ou reduzida a teste de regressão.

## <a id="3-three-kinds-of-authority"></a>3. Três tipos de autoridade

Decida a fonte de verdade de cada estado e registre.

| Tipo | Autoridade | Exemplos |
|---|---|---|
| **História** | Sempre o host | Etapas, objetivos, resultados de diálogos, globais, reputação compartilhada, finais, mudanças programadas do mundo |
| **Atores** | Um responsável por ator ou área, com **época** (contador que cresce a cada transferência) | Movimento, IA e combate dos NPCs. Só responsável atual na época atual publica estado; demais exibem cópia dirigida remotamente. Veja [actor-ownership.md](actor-ownership.md) |
| **Jogador** | Cada jogador controla seu avatar | Posição, animação, inventário próprio, golpes próprios como atacante |

Esta página trata da primeira linha. As demais seguem as mesmas regras: uma autoridade, mensagens numeradas, nada aplicado duas vezes, nada obsoleto prevalece.

## <a id="4-the-effect-vocabulary"></a>4. Vocabulário de efeitos

Efeito é uma mudança **primitiva** no mundo, pequena o bastante para aplicar diretamente sem script. Escolha vocabulário que cubra as possibilidades dos scripts. New Vegas tem cerca de cinquenta tipos, acrescentados conforme o levantamento dos scripts. Agrupe assim:

| Grupo | Exemplos (nomes independentes de jogo) |
|---|---|
| Progresso | Definir etapa ou indicadores de objetivos, concluir/falhar/iniciar/parar missão |
| Variáveis | Definir global ou variável de script em jogador ou objeto responsável |
| Objetos do mundo | Ativar/desativar referência, mover, trancar/destrancar, abrir/fechar, destruir, definir textura ou ângulo |
| Atores | Matar, ressuscitar, criar, remover, mudar nível em facção, adicionar/remover tópico ou nota |
| Itens | Adicionar/remover para destinatário ou em contêiner, remover todos |
| Valores do jogador | Alterar atributo, reputação ou carma por diferença, adicionar/remover vantagem |
| Ambiente | Definir clima, escala temporal, avançar tempo |
| Sessão | Vínculo do grupo, chegada/liberação de barreira, bloquear salvamento, solicitar salvar |
| Eventos (não estado) | Diálogo forçado, fim de apresentação, pedido de salvamento |

Regras úteis de projeto:

- **Diferenças para números, não valores absolutos.** Adicionar 100 de experiência é exato; diferenças inteiras mantêm cópias idênticas bit a bit, e sequências da seção 5 garantem aplicação única. Floats só para valores realmente fracionários (globais, posições), sempre finitos.
- **Valor `before` em alterações reversíveis.** Permite desfazer, e o reparador de dessincronização distingue divergência real de ruído.
- **Todo efeito nomeia destinatário.** Padrão significa quem causou, todos significa cada jogador, ou usa máscara de jogadores. Recompensas, itens de missão e valores individuais são encaminhados por política, não por quem é o host.
- **Toda transação leva causa.** Resultado de missão, diálogo, console, saque, combate, script, intenção. Essencial para descobrir por que as cópias divergiram.
- **Identifique por nome, não número de ordem de carregamento.** Envie (nome do plugin, identificador local), nunca ID numérico bruto dependente da lista de mods alheia. Registre nomes uma vez por mensagem para reduzir tamanho.
- **Adicionar ou reordenar efeitos quebra compatibilidade.** Acrescente tipos no fim e incremente versão (seção 12).

## <a id="5-transactions-the-story-log-and-acknowledgements"></a>5. Transações, registro da história e confirmações

Todos os efeitos capturados durante um script são enviados como **transação atômica e ordenada**.

- O host atribui a cada transação confirmada número de sequência crescente e sem lacunas, acrescentando ao **registro da história**.
- Clientes aplicam estritamente em ordem, guardam mensagens após lacuna, ignoram duplicatas e confirmam o maior número contíguo aplicado.
- Host reenvia não confirmadas com espera exponencial. Envio ao vivo nunca reinicia o temporizador de retransmissão, ou transações constantes impedem reenvios.
- Cliente muito atrasado recebe recuperação de progresso ritmada por suas confirmações, não inundação de envios ao vivo.
- O registro também permite entrada tardia e reconexão: reproduza-o ou envie captura de estado se foi compactado.

Essa camada é confiável sobre transporte não confiável, deliberadamente. Sobrevive por si a perda, duplicação, reordenação e corrupção, comprováveis com [o simulador de caos](network-chaos-testing.md).

## <a id="6-epochs-stopping-old-messages-from-winning"></a>6. Épocas: impedir que mensagens antigas prevaleçam

Época é contador que muda quando um mundo é substituído. Mensagens de outra época são obsoletas e descartadas. Três são úteis:

| Época | Muda quando | Protege contra |
|---|---|---|
| **Mundo** | Host carrega salvamento antigo (histórico retrocede) | Transações antigas aplicadas na nova linha temporal |
| **Intenção** | Mundo do cliente é substituído (carregamento ou reconexão) | Número antigo de solicitação confundido com novo |
| **Responsabilidade** | Ator ou área muda de responsável | Atualização atrasada do anterior sobrescrevendo estado do novo |

Use também **identificador de sessão** escolhido pelo cliente a cada conexão e repetido nas mensagens seguintes, descartando datagramas de conexão anterior. Skyrim Together Reborn sofreu duplicação em massa por responsabilidade obsoleta: forte argumento para conferir épocas em toda aplicação.

## <a id="7-clients-never-run-the-script-never-apply-your-own-echo"></a>7. Clientes: nunca executar o script nem aplicar o próprio eco

No cliente:

- **Bloqueie scripts da história.** A cópia ainda contém scripts de missões. Suprima-os por hook no ponto de início do motor; só host produz alterações da história.
- **Proteção contra eco.** Durante aplicação remota, sinalize para os próprios hooks não capturarem e reenviarem a mudança.
- **Não execute novamente scripts secundários do efeito.** Definir etapa 40 deve alterar número sem disparar script de mudança de etapa. Alguns motores têm caminho sem scripts de resultado; outros precisam de hook.
- **Scripts por máquina** (conquistas, transições visuais, vibração, interface) continuam locais. Use lista de nomes permitidos em todas as máquinas, garantindo que suas mudanças não sejam enviadas como compartilhadas.

## <a id="8-when-a-client-causes-the-story-to-move-intents"></a>8. Quando o cliente faz a história avançar: intenções

Jogador cliente entra em gatilho, ativa objeto ou coleta algo. O script reativo está vinculado ao jogador do **host** e só roda lá. Então:

- Cliente **detecta** interação e envia **intenção**: ativar objeto X. Não aplica nada localmente, salvo interface (menu abre).
- Host executa **em nome do cliente**, em contexto de jogador atuante: referências a "o jogador" resolvem para o avatar cliente durante o bloco. Efeitos são marcados com cliente como origem; itens e experiência chegam à pessoa certa.
- Resultado volta como transação comum.
- Intenções são numeradas dentro da época de intenção. Host executa cada número exatamente uma vez, em ordem, e confirma. Cliente reenvia até confirmação e após reconexão. Reenvio nunca repete ação.

Tipos necessários: efeitos já aplicados (cliente executou e informa), ativar, entrar em gatilho, coletar, avançar cena, relatos de célula e proximidade do cliente.

## <a id="9-merge-rules-and-policy"></a>9. Regras de combinação e política

Se duas fontes escrevem o mesmo estado, escolha e documente regra por tipo:

| Tipo | Regra |
|---|---|
| Números de etapas | Maior vence (missão não retrocede acidentalmente) |
| Indicadores | OR (uma vez verdadeiro, permanece) |
| Mortes | União |
| Globais | Host vence |
| Resultados mutuamente exclusivos | Primeiro confirmado vence (regra para etapas excludentes) |
| Escolhas aleatórias (listas por nível, sorteios) | Feitas uma vez no host; envia resultado real |

Decida a **política de compartilhamento** com o responsável pelo projeto antes do código; mantenha em dados, um indicador por categoria (diário, tópicos, nível em facção, reputação, carma, mortes, globais, recompensas para todos). Decisões de New Vegas:

| Questão | Decisão |
|---|---|
| Carma e reputação de facções | Compartilhados. O grupo é um personagem na história |
| Itens e recompensas de missões | Todos recebem |
| Diálogo | Quem inicia escolhe. Todos veem falas e resultado |
| Finais e cenas | Host decide. Todos são bloqueados e movidos juntos |
| Transições irreversíveis | Primeiro barreira do grupo: todos presentes e de acordo. Ninguém fica para trás |
| Companheiros | Pertencem a quem recrutou. Só responsável comanda |
| Ganhos de cassino, armazenamento próprio | Individuais |

São exemplos de decisões, não regras para seu jogo.

## <a id="10-join-rejoin-and-baselines"></a>10. Entrada, reconexão e estado de referência

Jogador que entra tarde ou reconecta precisa terminar no mesmo mundo.

- **Entrada nova:** host envia captura compartilhada e o registro a partir daquele ponto.
- **Reconexão na mesma sessão:** cliente informa que tem tudo até N; host continua de N. Transações perdidas são reproduzidas uma vez, nunca duas.
- **Entrada com salvamento próprio:** mundo do cliente vem de arquivo diferente, divergindo de formas desconhecidas. Use **transferência de estado de referência**:
  1. Cliente envia resumo (chave, hash) para cada entrada do mundo acompanhada, em blocos.
  2. Host compara e devolve diferenças: efeitos para forçar valores e chaves do cliente ausentes no host para reverter.
  3. Cliente aplica com semântica forçada e confirma cada bloco; repetições são seguras.
  4. Use forma canônica de floats no hash (converta a 32 bits e arredonde), evitando diferenças falsas por ruído numérico inofensivo.
- **Host carrega salvamento antigo:** muda época do mundo e manda clientes **realinharem**: capturar novamente e reentrar com referência. Alguns indicadores nunca podem ser desfeitos; documente.
- **Recompensas individuais** (itens e experiência anteriores) não fazem parte da diferença do mundo compartilhado. Mantenha livro de registros por jogador no host, envie na entrada e decida como evitar duplicação se o salvamento próprio de cliente reiniciado já contém os itens.

## <a id="11-detect-and-heal-desync"></a>11. Detectar e reparar dessincronização

Prevenção (autoridade única, épocas, IDs idempotentes, scripts sem repetição, escolhas aleatórias compartilhadas) remove a maioria das divergências, não todas. Acrescente proteção:

1. **Resumo.** Cada cliente periodicamente calcula hashes do mundo real em quantidade fixa de **partições** (New Vegas usou 128: 8 classes de entradas × 16 grupos de chaves), em sequência conhecida. Também envia após eventos propensos a divergência (barreiras, cenas) ou pedido do host.
2. **Comparar.** Host compara na mesma sequência. Para cada partição divergente, pede entradas ao cliente.
3. **Reparar.** Responde com efeitos de valores forçados e chaves a reverter, ignorando chaves alteradas desde o resumo (nunca desfaz mudança nova). Só aplica se a época coincidir.
4. **Registrar.** Quais valores divergiram e em qual lado. Divergência repetida na mesma chave é bug, não ruído.
5. **Contar.** Painel de reparos por minuto e categoria. Meta em testes por scripts: zero.

O reparador é rede de segurança, não o plano. Contagem alta nos testes significa primeira linha de defesa quebrada. Veja [desync-hunting.md](desync-hunting.md) para chegar à causa inicial.

## <a id="12-the-wire-format-briefly"></a>12. Formato de rede, brevemente

Detalhes dependem do jogo. Regras essenciais:

- Número mágico, byte de versão, tipo de mensagem, corpo e checksum no fim. Descartar o que não decodifica.
- Mensagens de apresentação e recusa usam invólucro independente de versão, apenas acrescentando campos no fim; compilações incompatíveis ainda explicam por que não podem jogar juntas.
- Incremente versão do formato para mudanças incompatíveis de bytes, incluindo tipo de efeito novo ou reordenado. Incremente também versão do protocolo, inclusive se mudar comportamento sem mudar bytes (regra de combinação, canonicalização de hash).
- Compare na entrada: versão do protocolo, compilação, hash de regras, hash da lista de mods e, na entrada por referência, hash do conteúdo. Divergência gera recusa legível, não sessão corrompida.
- Trate toda entrada como hostil: limite contagens, recuse floats não finitos, nunca confie na vaga informada pelo remetente.
- Uma conexão, vários canais: primeiro um byte de canal, permitindo história, diálogo e outros adaptadores compartilharem transporte.

## <a id="13-how-to-test-it"></a>13. Como testar

Desenvolva **primeiro sem jogo**. O núcleo é código simples que não conhece o motor:

1. **Simulador** com N clientes falsos, relógio virtual e conexão com perdas (use modelo de [tools/chaos](../tools/chaos/README.md), compartilhando a rede degradada entre simulação e cópias reais).
2. **Ida e volta e fuzzing** do formato (truncamento, bits invertidos, contagens hostis).
3. **Invariantes** em toda execução: cópias convergem, nada aplicado duas vezes, um responsável por época, nenhuma criação duplicada, escrita antiga nunca vence, nenhum script da história roda em cliente.
4. **Variantes de mutação.** Para cada proteção, compilação com ela desativada precisa falhar em teste; senão, aprovação pode não testar nada.
5. **Comparação diferencial com um jogador.** Mesmo cenário individual e cooperativo; estado compartilhado deve seguir a trajetória individual a cada checkpoint.
6. **Cópias reais** por último, pelo retransmissor, confirmando o previsto.
7. **Expectativas protegidas.** Referências que agentes não possam afrouxar sem revisão do usuário.

Para o ciclo, veja [automated-qa.md](automated-qa.md) e [fuzzing-coop-sync.md](fuzzing-coop-sync.md).

## <a id="14-worked-example-new-vegas"></a>14. Exemplo prático: New Vegas

New Vegas aplica a arquitetura a motor fechado por plugin de extensão de scripts. Pontos concretos:

- **O que host captura.** Durante scripts de resultado de etapa, diálogo ou objeto, hooks registram etapas e objetivos, globais, ativação/desativação de referências, adição/remoção de itens, valores de atores, reputação, carma, início/fim de missões, movimentos, mortes, criações e variáveis. A lista é confirmada como transação única.
- **Por que não repetir `SetStage`.** Script que adiciona itens e ativa personagem rodaria de novo em todo cliente. Na captura, host roda uma vez; clientes recebem definir etapa, adicionar item a todos, ativar personagem.
- **Encaminhamento individual.** Experiência e tampinhas de missões para todos (recompensa integral por pessoa). Recompensas de listas por nível sorteadas uma vez no host; envia itens reais. Carma e reputação compartilhados.
- **Interações dos clientes.** Convidado que ativa terminal ou entra em gatilho envia intenção; host executa com seu avatar como jogador atuante.
- **Mecanismos da sessão.** Cerca de cinquenta efeitos, registro da história, intenções com épocas, referência para cliente com salvamento próprio, resumo de 128 partições para reparo e canal de diálogo junto ao da história.
- **Política.** Carma/reputação compartilhados, itens/recompensas para todos, iniciador escolhe diálogo, finais/transições irreversíveis exigem grupo todo, companheiros pertencem a quem recrutou.

Intencionalmente excluídos da história compartilhada: scripts por máquina (conquistas, transições visuais), locais por lista de permissões.

## <a id="15-limits-to-expect"></a>15. Limitações esperadas

- **Indicadores irreversíveis persistentes.** Alguns (missão concluída ou falhada) não podem ser removidos ao retroceder. Host com salvamento antigo não consegue reverter totalmente cliente que já concluiu. Documente.
- **Recompensas após reiniciar.** Cliente com salvamento próprio já premiado pode recebê-las de novo, a menos que detecte e trate efeitos do livro de registros da captura como entregar só se ausente.
- **Células carregadas em só uma máquina.** Host simula apenas áreas ao redor. Jogadores em outras precisam de vínculo, responsável pela área ou substituto. Veja [actor-ownership.md](actor-ownership.md).
- **Segurança de threads do motor.** Aplique efeitos na thread principal.
- **Cobertura.** Captura só vê o que tem hook. Levante scripts (extraia todos os comandos usados) e acrescente tipos até cobrir. Comandos desconhecidos devem gerar aviso destacado, não ser ignorados.

## <a id="16-checklist-for-a-new-game"></a>16. Lista para um jogo novo

1. Descubra armazenamento da história e comandos que o alteram. Extraia scripts ou use descompilação.
2. Escolha vocabulário pelos comandos realmente usados. Pesquise, não adivinhe.
3. Ache hooks: início dos scripts e escrita de cada comando primitivo. Registre no momento da escrita, não na chamada do script.
4. Ache caminho para definir sem scripts secundários nos clientes, ou insira hooks e os suprima.
5. Decida compartilhamento com usuário e registre como dados.
6. Escreva núcleo sem motor: efeitos, transações, registro, épocas, intenções, referências, resumos, formato de rede.
7. Teste em simulador com perdas, invariantes e mutações.
8. Integre ao jogo. Teste duas cópias reais pelo [retransmissor de caos](network-chaos-testing.md).
9. Execute comparação diferencial e contagens de reparos; registre números.
10. Escreva as limitações da seção 15 no README do jogo.

## <a id="sources"></a>Fontes

- [Skyrim Together Reborn](https://github.com/tiltedphoques/TiltedEvolution): código aberto. Líder avança missões, um responsável por ator, épocas de responsabilidade.
- [TES3MP](https://github.com/TES3MP/TES3MP): código aberto. Diário, tópicos e facções no servidor, scripts locais, autoridade de célula.
- [VaultMP](https://github.com/foxtacles/vaultmp): representantes de jogadores de código aberto para Fallout.
- [Gaffer on Games](https://gafferongames.com/): interpolação de capturas, sincronização de estado, confiabilidade sobre UDP.
- [fnv-coop](https://github.com/cranebeaker/fnv-coop): projeto New Vegas de origem desta arquitetura.
