# <a id="remote-control-your-game-from-tests-one-rpc-server-in-the-game-a-main-thread-queue-a-method-registry"></a>Controle o jogo remotamente pelos testes: servidor RPC interno, fila na thread principal e registro de métodos

Todo teste cooperativo automatizado precisa acessar um jogo em execução: colocá-lo em estado conhecido, executar uma linha de console, perguntar "qual é a etapa da missão?", aguardar um evento e ler o estado para comparar duas cópias. Extração de dados da tela e simulação de entradas não fazem isso com confiabilidade. Um pequeno servidor RPC dentro do processo do jogo consegue.

Esta página apresenta o padrão. As ferramentas estão em [`tools/bridge`](../tools/bridge/README.md) (modelo de servidor, cliente Python, formato de comunicação, jogo simulado) e [`tools/inspect`](../tools/inspect/README.md) (tabela ao vivo somente de leitura das cópias). Ambas foram generalizadas do projeto cooperativo de Fallout: New Vegas e não dependem de um jogo específico.

Leia primeiro [automated-qa.md](automated-qa.md) para saber o que um teste deve comprovar e [bots-and-playbooks.md](bots-and-playbooks.md) para os componentes sobre a ponte (bots, cenários). [multi-instance-testing.md](multi-instance-testing.md) cobre a inicialização das cópias.

## <a id="1-the-shape"></a>1. A estrutura

```
 test / bot / inspector (any language)            the game process
 -----------------------------------            -------------------------------------------
  bridge_client.py                                transport thread     main thread (game loop)
    call("exec", {...})  --- one JSON line --->    reads a line   ---> request queue
                                                   waits (timeout)       |  Pump(), once per frame hook
    <--- one JSON line ---  reply  <-------------  replies       <---   adapter -> the game's own calls
```

Quatro partes:

1. **Thread de transporte** que aceita conexões e lê JSON delimitado por quebras de linha. TCP no loopback funciona em todo sistema operacional. Pipe nomeado é a alternativa no Windows.
2. **Fila de solicitações processada na thread principal do jogo.** Código do jogo (console, scripts, formulários, salvar e carregar) quase nunca é seguro para threads. A thread de transporte apenas enfileira e aguarda; uma chamada no hook de quadro executa a solicitação.
3. **Registro de métodos.** O servidor oferece um pequeno conjunto padrão (`ping`, `version`, `exec`, `eval`, `waitFor`, `state`, `save`, `load`, `screenshot`, `events`), e o mod registra seus próprios métodos (`sync.status`, `bot.menu`) ao lado deles.
4. **Adaptador**, o único código específico do jogo: "executar esta linha de console", "avaliar esta expressão", "iniciar este carregamento".

## <a id="2-rules-that-save-you-weeks"></a>2. Regras que economizam semanas

- **Execute chamadas do jogo somente na thread principal.** Uma chamada da thread de transporte funciona em teste e derruba o jogo uma vez a cada cem execuções. Teste a regra: faça `exec` informar a thread usada e falhe a compilação quando não for a do hook de quadro.
- **Responda `ping` na thread de transporte.** Enquanto o jogo carrega ou trava, a thread principal não processa a fila. Um ping que ainda responde (com o tempo desde o último quadro) distingue "carregando" de "morto".
- **Limite de tempo em toda chamada, dos dois lados.** O cliente excede o limite, e o servidor expira solicitações que nenhum quadro processou (o chamador recebe erro claro, e a solicitação abandonada nunca roda depois). Nunca bloqueie um teste indefinidamente em um jogo que parou de processar a fila.
- **Respostas atrasadas não podem confundir a chamada seguinte.** Numere as solicitações e ignore respostas com número anterior.
- **Erros mantêm código e texto.** O erro do próprio jogo ("script command not found", "save exists") chega ao teste sem alterações. Um adaptador que engole erros aprova todos os testes pelo motivo errado.
- **Limite o trabalho por quadro.** Inicie algumas solicitações enfileiradas em cada hook, não todas, evitando que uma rajada congele um quadro. Recuse novas solicitações quando a fila estiver cheia.
- **Verifique as condições de espera do lado do jogo.** `waitFor` avalia uma condição a cada poucos milissegundos na thread principal e responde quando ela for verdadeira ou o tempo acabar. É mais rápido e confiável que um loop cliente com pausas; uma consulta que falha durante carregamento não encerra a espera.
- **Método ausente é normal.** Uma compilação antiga ou módulo desligado pode não ter métodos. Responda "method not found" e deixe as ferramentas exibirem "n/a", em vez de falharem.
- **Caminhos absolutos.** O processo do jogo resolve caminhos relativos a partir da própria pasta. Faça o cliente convertê-los em absolutos antes de enviar.
- **Somente UTF-8 válido.** Texto do jogo costuma usar codificação antiga. Substitua bytes inválidos antes do JSON, ou um caractere estranho pode esconder a resposta.
- **Somente loopback e compilações de teste.** O servidor executa linhas de console para quem conseguir conectar e não tem senha. Vincule a 127.0.0.1 e não o distribua ativado.

## <a id="3-what-to-expose-in-order"></a>3. O que expor, em ordem

1. `ping` e `version` (registre a compilação nos metadados de toda execução).
2. `exec`: uma linha de console, com texto de saída. Se o console não puder indicar uma referência na linha, dê a `exec` um parâmetro `ref` que execute a linha "sobre" essa referência.
3. `eval`: uma expressão convertida em número. Etapa de missão, quantidade de itens, saúde.
4. `waitFor`: a consulta de condição descrita acima.
5. `state`: snapshot JSON do estado compartilhado sincronizado, para comparar máquinas caminho por caminho ([bots-and-playbooks.md](bots-and-playbooks.md)).
6. `events`: buffer circular de eventos (`game.loaded`, `game.saved`, caixa de mensagem exibida, relato de dessincronização). Testes aguardam eventos em vez de pausas e leem os recentes após falhas.
7. `load` e `save`: iniciam a chamada do motor, retornam e terminam quando chega a mensagem "loaded" ou "saved" do próprio jogo. Recuse nomes dos salvamentos do usuário.
8. `screenshot` e métodos próprios para o que os bots exigirem (ler menu, pressionar botão, consultar sincronização).

Separe métodos somente de leitura dos que alteram algo. O inspetor poderá permitir o primeiro grupo e recusar o segundo.

## <a id="4-build-order-that-finds-problems-early"></a>4. Ordem de implementação que encontra problemas cedo

1. **Escreva primeiro o cliente e um jogo simulado.** `tools/bridge/fake_game.py` simula o mesmo comportamento do servidor, incluindo falhas (resposta atrasada, identificador errado, dados inválidos, conexão interrompida). Scripts de teste e bots podem usá-lo antes de existir um jogo real.
2. **Incorpore o servidor ao menor programa com loop principal.** `tools/bridge/cpp/test_server.cpp` é um jogo simulado de cerca de 200 linhas. Execute contra ele os mesmos testes do cliente.
3. **Escreva o adaptador para o jogo real.** Comece somente por `exec`, depois acrescente um método por vez. Cada um recebe um teste cliente.
4. **Adicione métodos personalizados** conforme os bots precisarem. Registre-os com nome contendo ponto e indique quais são somente de leitura.
5. **Inclua o servidor somente em compilações de teste** e leia o endpoint de um arquivo que o jogo escreve ao iniciar, permitindo a cada cópia escolher uma porta livre.

## <a id="5-look-at-your-copies-the-live-inspector"></a>5. Observe as cópias: o inspetor ao vivo

Quando um teste falha com duas cópias rodando, a primeira dúvida é o que cada uma faz. [`tools/inspect`](../tools/inspect/README.md) exibe uma tabela com coluna por cópia: menu, arma, saúde, posição, responsável pelo alvo, contadores de sincronização, dessincronizações recentes e caixas de mensagem. As linhas vêm de uma pequena lista JSON de campos do jogo, lidos pela ponte.

É somente de leitura propositalmente: um invólucro permite um conjunto fixo de métodos de consulta e recusa o restante, de modo que observar nunca altere o observado. Sob a tabela, lista os problemas detectados pelas regras (caixa de mensagem aberta, cópia atrasada, contador alterado). Uma cópia indisponível aparece como coluna informando isso. Execute com `--watch 1` durante um teste, ou uma vez após uma falha.

## <a id="6-test-the-bridge-itself"></a>6. Teste a própria ponte

Uma estrutura de testes que não consegue falhar não vale nada. As ferramentas da ponte executam seus testes contra um jogo simulado e o modelo de servidor C++; cada teste tem uma **variante de mutação**: cópia do código com uma proteção quebrada (limites de tempo ignorados, erros engolidos, chamadas fora da thread principal, ausência de orçamento por quadro, invólucro somente de leitura que aceita escritas, dados obsoletos após atualizar) que o teste correspondente deve detectar. Faça o mesmo com o adaptador: o teste que afirma "isto executa na thread principal" precisa falhar quando você chama o jogo da thread errada.

```
python -I tools/bridge/run_tests.py
python -I tools/inspect/run_tests.py
```

## <a id="checklist-for-an-agent"></a>Lista de verificação para agentes

- [ ] O servidor executa código do jogo somente dentro da chamada por quadro na thread principal, com teste que comprova isso.
- [ ] `ping` responde enquanto a thread principal está travada e informa há quanto tempo.
- [ ] Toda chamada cliente e solicitação enfileirada tem limite de tempo, e respostas atrasadas são ignoradas.
- [ ] Erros do jogo chegam ao teste com código e texto. Nenhum método engole erros.
- [ ] Trabalho por quadro e comprimento da fila são limitados.
- [ ] Escuta somente no loopback e somente em compilações de teste.
- [ ] Caminhos enviados ao jogo são absolutos; texto retornado é UTF-8 válido.
- [ ] Um jogo simulado substitui o real, permitindo executar testes antes da integração.
- [ ] Métodos somente de leitura são separados dos que alteram o jogo, e o inspetor usa somente o primeiro grupo.
- [ ] Os testes da ponte têm variantes de mutação, e todas são detectadas.
