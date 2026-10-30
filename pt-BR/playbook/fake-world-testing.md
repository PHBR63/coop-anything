# <a id="fake-world-testing-test-your-sync-without-the-game"></a>Testes com mundo simulado: teste a sincronização sem o jogo

A maioria dos bugs de sincronização cooperativa não é do motor, mas de lógica: mensagem aplicada duas vezes, responsável antigo ainda enviando atualizações, dois jogadores pegando o mesmo item, novo participante sem metade do estado. Você pode encontrar tudo isso sem iniciar o jogo. Modele como dados simples a parte do mundo sincronizada, execute várias cópias com relógio virtual sobre uma rede simulada com perdas e confira se concordam.

Código de exemplo: [tools/fakeworld](../tools/fakeworld/README.md). Usa [tools/ownership](../tools/ownership/README.md) ([actor-ownership.md](actor-ownership.md)). Execute com `python -I tools/fakeworld/run_tests.py`. Relacionados: [fuzzing-coop-sync.md](fuzzing-coop-sync.md), [network-chaos-testing.md](network-chaos-testing.md), [automated-qa.md](automated-qa.md).

## <a id="why-a-fake-world"></a>Por que um mundo simulado

- **Rápido.** Toda a suíte de exemplo (63 testes, incluindo quatro sessões aleatórias de 12 segundos virtuais) roda em cerca de um segundo. Você pode executá-la após cada edição, assim como cada agente trabalhando em paralelo.
- **Determinístico.** Mesma semente, mesmo mundo, mesma execução. Uma falha é uma semente e o nome de um teste, não uma história.
- **Dispensa o jogo.** Nada para iniciar, nenhuma janela ou salvamento a corromper, sem precisar manter livre o PC do usuário.
- **Falhas sob demanda.** Perda, duplicação, reordenação, corrupção e jogadores saindo e entrando no meio de um combate são parâmetros, não sorte.
- **Oráculos honestos.** O mundo simulado conhece a verdade, então uma verificação como não criar ou perder itens ocupa uma linha.

Isso não substitui os testes no jogo real. Encontra primeiro os bugs de lógica, com baixo custo, deixando para os bots internos ([automated-qa.md](automated-qa.md)) apenas as surpresas do motor.

## <a id="what-goes-in-the-model"></a>O que entra no modelo

Somente o que você sincroniza. No exemplo: células e carregamento por proximidade, atores com um responsável, vida e morte, contêineres e itens no chão, portas e fechaduras, pontos de criação com reaparecimento, jogadores com inventários e etapas de missões. No seu jogo pode ser um mapa de peças, lista de salas de masmorra ou tabela de indicadores. Mantenha os dados simples: IDs, números e pequenos mapas. Tudo que entraria em um arquivo de salvamento pertence ao modelo.

## <a id="the-ingredients"></a>Os ingredientes

1. **Mundo construído por semente.** Uma chamada gera o mesmo mundo estático em todas as máquinas, como carregar os mesmos dados do jogo. Use um pequeno gerador aleatório com semente controlado por você, nunca o da plataforma.
2. **Relógio virtual.** As máquinas nunca leem o relógio real. A estrutura chama `tick(nowMs)`. O tempo é um número que pode avançar de 10 em 10 ms; assim, 12 segundos de jogo levam milissegundos.
3. **Conexão com perdas.** Latência com variação (que causa reordenação), perda, duplicação e inversão de um bit. Usa semente, portanto é reproduzível. Sobreponha sua camada confiável (números de sequência, confirmações, retransmissão, CRC) conforme as necessidades do transporte real.
4. **Máquina.** Um participante: cópia própria do mundo, manipuladores de protocolo e uma IA barata de NPCs para os atores sob sua responsabilidade. Ações do jogador local passam por um único ponto de entrada (`doAction`), permitindo que uma lista de ações seja um roteiro completo e reproduzível.
5. **Conjunto de máquinas.** N máquinas, rede, entrada e saída, salvamento e carregamento do host.
6. **Resumos de estado.** Hash do mundo por categoria e por chave, com floats quantizados em faixas para eliminar diferenças de arredondamento. Máquinas comparam esses resumos; diferenças persistentes são reparadas enviando a cópia do host apenas das chaves afetadas. Isso também é sua rede de segurança no jogo.
7. **Oráculos.** Verificações durante e depois de um cenário (abaixo).
8. **Variantes de mutação.** Opções que reproduzem bugs conhecidos (abaixo).
9. **Gravador.** Registre todas as entradas recebidas por uma máquina (ticks, ações, mensagens) e reproduza-as em máquinas novas sem rede. Uma execução com falha vira teste de regressão e é reduzida facilmente.

## <a id="oracles-that-earn-their-keep"></a>Oráculos que justificam seu uso

Sempre válidos (verificar após cada etapa):

- Um responsável por ator por época e uma máquina controlando a IA de cada ator.
- Nada obsoleto aceito: toda atualização aceita veio do responsável na época atual.
- Nada aplicado duas vezes: IDs já aplicados são contados, e a contagem deve permanecer zero.
- Nenhum ator duplicado de um ponto de criação, nem dois itens de uma solicitação de descarte.

Válidos após o conjunto ficar inativo (`quiesce`: IA congelada, nada em trânsito, resumos estáveis):

- Toda máquina igual ao host: resumos e estado exato dos atores.
- Mesma tabela de responsabilidade em todos os lugares.
- Conservação de itens: chão mais contêineres mais todos os inventários igual à quantidade inicial do mundo.
- Nenhum reparo por resumo necessário. Um reparo indica divergência remendada. Conte os reparos e permita poucos em uma conexão com muita perda.

## <a id="scenarios"></a>Cenários

Cada cenário é uma função que cria um conjunto de máquinas, provoca um evento, espera estabilizar e retorna verdadeiro somente se todos os invariantes forem mantidos. Escreva um para cada classe de bug que conseguir nomear:

- Dois jogadores pegam o mesmo item no mesmo instante (um vencedor, cópia do perdedor revertida).
- Dois jogadores abrem o mesmo contêiner (um detentor da trava, conservação de itens ao retirar, colocar e fechar).
- Três jogadores carregam a mesma célula (o encontro aparece uma vez).
- Host se afasta no meio de uma luta (ator muda de responsável sem perder vida ou posição).
- Script de história mata um ator que o combate não deve matar.
- Mensagem entregue duas vezes ou mensagem antiga atrasada (não pode ser reaplicada).
- Convidado sai e volta; host carrega um salvamento.
- Corrupção silenciosa numa máquina (resumos precisam encontrá-la e repará-la).
- Sessão aleatória: movimentos, ataques, coletas, uso de contêineres, entradas, saídas e salvamentos aleatórios, com conexão limpa e com perdas, verificando os invariantes sempre válidos a cada etapa.

## <a id="mutation-twins"></a>Variantes de mutação

Um teste que você nunca viu falhar pode não testar nada. Uma **variante de mutação** prova que a proteção funciona: ative uma falha que reproduza um bug conhecido, execute o mesmo cenário e exija que **falhe**. A variante passa somente se o cenário funcionar sem a falha e falhar com ela. Nosso script exibe `ALL OK` somente quando todas forem detectadas.

São baratas de criar: cada falha é um `if` no código testado, protegido por um indicador desativado em produção (`hitNoValidation`, `pickupNoArbitration`, `noDedupe`, `noEpochBump`...).

Descoberta real na adaptação do exemplo: a variante de transferência confirmada sem esperar pelo novo responsável continuou passando. O cenário verificava se o novo responsável havia recebido ao menos um estado final, mas uma transferência anterior e diferente já havia entregue um à mesma máquina. O cenário era fraco, não o código. A correção foi contar somente o que chega após o início da transferência testada, e a variante falhou como deveria. Verificar que o cenário passa primeiro e falha com a mutação é o que revela esse tipo de lacuna.

## <a id="build-your-own-in-this-order"></a>Crie o seu, nesta ordem

1. Liste o estado sincronizado e as mensagens que o transportam. Esse é seu mundo e formato de rede.
2. Escreva o mundo como dados simples, com construção por semente, salvar, carregar e resumo de estado. Teste apenas isso.
3. Escreva a conexão com perdas e uma camada confiável pequena. Teste ordenação e remoção de duplicatas isoladamente.
4. Escreva a máquina, começando pelo host: aplicar mensagem, publicar estado. Acrescente um recurso por vez.
5. Acrescente o conjunto de máquinas e os oráculos sempre válidos antes do segundo recurso.
6. Para cada recurso, adicione cenário, indicador de falha e variante de mutação, nessa ordem.
7. Acrescente a sessão aleatória por último. Ela encontra interações que você não imaginou.
8. Quando um teste real ou fuzzer encontrar um bug, reproduza-o aqui primeiro, corrija-o e mantenha o teste.

Você pode copiar o exemplo e mudar os tipos ou aproveitar apenas a organização. O código é um ponto de partida. A lista de mensagens e os oráculos serão próprios.

## <a id="limits"></a>Limites

Um modelo não informa o comportamento do motor: quando um hook dispara, o que recarregar faz com uma referência ou em qual quadro uma animação começa. Tudo que você descobrir sobre o motor por engenharia reversa entra no modelo como regra; o que o modelo não pode conhecer exige um teste no jogo real. Use o mundo simulado para lógica de protocolo e estado, um fuzzer ([fuzzing-coop-sync.md](fuzzing-coop-sync.md)) e conexões de caos ([network-chaos-testing.md](network-chaos-testing.md)) para ampliar a cobertura, e bots em clientes reais ([automated-qa.md](automated-qa.md)) para comprovar a realidade.
