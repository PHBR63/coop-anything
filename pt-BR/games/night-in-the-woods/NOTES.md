# <a id="night-in-the-woods"></a>Night in the Woods

## <a id="identity-observed"></a>Identidade (observada)

- Versão original Steam para PC, aplicativo 481510, compilação 5940043.
- SHA-256 do executável principal: `71C33A2723205469AF2B252F313B8AD051FE4F98ED456C2DB33B969853FE0594`.
- Windows x64; Unity 5.6.2p4; execução de scripts Mono.
- `Assembly-CSharp` referencia Rewired e código de diálogos Yarn. O assembly não referencia rede Unity. A presença de `UnityEngine.Networking.dll` não comprova rede no jogo.

## <a id="existing-work-checked-2026-10-19"></a>Trabalhos existentes (verificados em 2026-10-19)

- Não havia entrada no diretório nem pasta deste jogo no checkout.
- Buscas de issues/PRs restritas a `cranebeaker/coop-anything` não encontraram outro trabalho de Night in the Woods antes de abrir a reivindicação #69.
- Reivindicação: [#69](https://github.com/cranebeaker/coop-anything/issues/69).
- As buscas de issues/PRs e repositórios GitHub acima foram concluídas. ModDB, Discord e arquivos históricos não foram pesquisados; a cobertura deles é desconhecida.

## <a id="observed-game-structure"></a>Estrutura observada do jogo

- `Player.GetAxisRaw` lê um jogador Rewired estático. Movimento lê `Horizontal` e `Vertical`; pulo lê `Jump`; interação passa por auxiliares de diálogo/entrada do jogo.
- `Dialogue` usa `DialogueRunner` do Yarn; `DialogueImplementation` controla confirmação e navegação de opções; `DialogueVariableStorage` delega variáveis de história a `Continuity`.
- `Continuity` controla variáveis de história, inteiros persistentes, progresso do diário e dados de cenas. Grava dados do jogador e persistentes em arquivos `.dat` e `persist.dat` por `GetSaveDataPath`, que no Windows usa `Application.persistentDataPath` da Unity.
- O jogo iniciou da cópia isolada com o patcher de pré-carregamento ativo. Seu log confirma que o redirecionamento de salvamentos foi instalado antes de carregar Assembly-CSharp. Depois, o plugin cooperativo redirecionou caminhos de Continuity para uma pasta por teste na cópia isolada. A pasta ficou vazia durante a inicialização; marcas de tempo dos salvamentos existentes não mudaram (somente metadados conferidos; conteúdos não foram lidos).

## <a id="derived-direction"></a>Direção deduzida

- Começar por jogo conjunto com história compartilhada e autoridade do host: uma Mae, uma história e salvamento canônicos, com participantes contribuindo entradas de movimento e interação.
- Um segundo personagem visível fica para depois, com escopo muito maior, pois exige movimento, colisão, animação, câmera e interações de scripts separados.
- Temporização da história e execução de eventos podem não ser determinísticas. Reproduzir entradas não comprova progresso compartilhado; cena, diálogo e estado de `Continuity` exigem verificações explícitas e possivelmente sincronização.

## <a id="unknown--not-established"></a>Desconhecido / não estabelecido

- Se snapshots da cena e posição do host mantêm clientes alinhados na progressão normal da história, sem atalhos de script.
- Como manter escolhas, cenas temporizadas, eventos por script, diário/contadores persistentes e minijogos consistentes sem duplicar efeitos de história. O conteúdo numérico de `Continuity.vars` agora tem snapshots com autoridade do host, mas o comportamento completo no fluxo de história não foi testado.
- Comportamento em outra máquina, rede real, atraso/perda de pacotes ou após desconexão.
- O mapa de ações Rewired não contém Confirm nem Submit. A confirmação usa `Interact`. Uma inicialização isolada de host passou; resta um aviso de HarmonyX ao verificar uma propriedade Unity ausente nesta compilação.
- A verificação básica com bots e dois clientes reais rodou em 2026-10-19 e 2026-10-20. Conferiu confirmação da tela inicial, acompanhamento da cena/posição do host e correção de variáveis numéricas descritos abaixo. Não foram executados o teste de mutação do progresso completo nem toda a suíte; não se afirma que o modo esteja jogável.

## <a id="prototype-observation-observed-2026-10-20"></a>Observação do protótipo (observada em 2026-10-20)

- O protótipo local agora usa protocolo v3: host envia entradas combinadas, cena ativa, posição mundial de Mae e snapshots com autoridade do host do dicionário numérico `Continuity.vars`. Dicionários são divididos em fragmentos UDP limitados, e clientes só substituem a cópia local ao receber snapshot completo. O cliente corrige a transformação após a atualização do jogador e solicita a cena do host quando a local difere.
- Duas instâncias da cópia isolada conectaram por loopback. Com o comando de preparação exclusivo de QA `scene:MaeRoom`, ambas carregaram `MaeRoom` e informaram jogador habilitado.
- `move_right:45` do bot cliente e `move_right:45` do bot host moveram Mae. Ao fim de cada pulso, as posições diferiam menos de 0,02 unidade mundial.
- `scene:BusStation` somente no host moveu o cliente para `BusStation`; após carregar, a diferença informada era cerca de 0,001 unidade.
- `mutate_first_var`, exclusivo de QA no cliente, alterou a primeira variável de história ordenada, `AngusConstellations`. O snapshot seguinte restaurou o dicionário do cliente sob autoridade do host; ambos informaram 316 variáveis e hash `0F68BB8C`, e o cliente registrou `host snapshot applied`.
- `scene:<name>` é um atalho de preparação de QA que interrompe diálogos locais e chama `Global.LoadLevel` do jogo. Os testes de cena evitaram a progressão normal; o teste de variável foi mutação isolada de dicionário, não teste de escolha em diálogo normal. Não comprovam que escolhas, eventos por script ou salvamentos permaneçam sincronizados.
- A mutação valida somente a replicação do dicionário. Não valida fluxo normal de escolhas, todo o estado salvo/persistente, eventos por script ou jogo cooperativo de ponta a ponta.

## <a id="dialogue-option-sync-work-observed-2026-10-20"></a>Sincronização de opções de diálogo (observada em 2026-10-20)

- Inspeção estática de `DialogueImplementation+<RunOptions>c__Iterator5.MoveNext` mostrou que a navegação de opções visíveis usa diretamente `Rewired.Player.input.GetAxisRaw("Horizontal")` e atualiza `DialogueImplementation.currentOption`; fica fora do patch cooperativo existente de `Player.GetAxisRaw`.
- O jogo usa `runningOptions` para identificar seleção ativa. O estado de opções do host pode ser lido de `Global.dialogue.implementation` por reflexão, evitando dependência de compilação dos detalhes internos.
- O protótipo envia `runningOptions`, `currentOption` e `Dialogue.runningNode` nos pacotes de estado do host (protocolo v6). Cada menu tem identificador de sessão, evitando confundir uma confirmação atrasada de menu anterior no mesmo nó Yarn com a escolha atual. No cliente, um prefixo Harmony no iterador adota o cursor do host somente com nó Yarn correspondente, limita ao número local de opções e limpa indicadores locais de avanço por setas antes de cada passo.
- Inspeção estática mostrou que `Yarn.Unity.Example.DialogueUI.SetOption(int)` chama diretamente o callback `OptionChooser`. Um prefixo Harmony agora registra índice confirmado pelo host, nó Yarn, sessão de opções e identificador de confirmação crescente. O host repete isso nos pacotes; o cliente substitui o índice em `SetOption` uma só vez e apenas quando nó e sessão ativos correspondem.
- O cliente adia uma nova confirmação do host por até 0,5 s quando o snapshot ainda mostra menu ativo sem confirmação nova para aquela sessão. Uma confirmação da mesma sessão libera a entrada; se não chegar, o convidado segue com o cursor local e registra aviso, em vez de esperar indefinidamente.
- O protótipo compilou contra os assemblies isolados. Uma verificação local do protocolo v6 serializou e leu pacotes de cliente e host; o pacote do host preservou índice de cursor `3`/nó `poem_1`/sessão `42` e confirmação `17`/índice `2`/nó `poem_2`/sessão `42`. Todos os prefixos truncados foram recusados; cinco casos locais de predicados nó/sessão passaram.
- A alteração não foi exercitada em diálogo ao vivo com dois clientes. Não comprova visuais de seleção idênticos, efeitos de ramificações iguais ou sincronização de efeitos por script. Ainda é necessário teste de escolha com bots no fluxo normal antes de afirmar sincronização.
- Sincronização de cursor e escolha confirmada passou somente por compilação, protocolo e casos locais de predicados nó/sessão. Não passou em teste de escolhas ao vivo com dois clientes; ramificações e efeitos colaterais permanecem sem verificação.

## <a id="latest-live-loopback-check-observed-2026-10-20"></a>Última verificação ao vivo por loopback (observada em 2026-10-20)

- Duas pastas isoladas, com configurações BepInEx separadas, conectaram por loopback com protocolo v6. Dados do cliente foram copiados da instalação isolada do host.
- A preparação de cena do host moveu ambos para `MaeRoom`; mudar o host para `BusStation` levou o cliente com posições informadas iguais. Em `MaeRoom`, pulsos de 45 quadros do host e convidado moveram Mae; posições diferiam menos de 0,01 unidade após cada pulso.
- A sincronização continua incompleta. Após `mutate_first_var` do convidado em `MaeRoom`, o cliente informou `host snapshot applied`, mas seu hash do dicionário inteiro (`B7EDB636`) diferiu do host (`5DA3C071`) por pelo menos seis segundos. Após forçar `Title` no host, hashes coincidiram (`9662F8C5`), mas o cliente ficou em `TransitionScene` enquanto host informava `Title`. O cliente observou uma confirmação do host, que não avançou o menu inicial do próprio host.
- O caminho de escolhas da v0.6.0 não foi exercitado em menu ativo. Fluxo normal, ramificações iguais, efeitos por script e progresso salvo permanecem sem verificação; não se afirma jogabilidade.

## <a id="follow-up-loopback-check-observed-2026-10-20"></a>Verificação seguinte por loopback (observada em 2026-10-20)

- A v0.6.1 acrescenta nova tentativa após 1,5 s quando o cliente fica em cena diferente da solicitada pelo host; o estado de QA agora inclui primeira variável ordenada e campos ao vivo de opção/sessão/confirmação.
- Após copiar dados a uma segunda pasta e separar configurações BepInEx, dois clientes v0.6.1 conectaram. Forçar transição `MaeRoom` para `Title` no host levou ambos a `Title`; confirmação do convidado continuou o salvamento isolado e levou ambos a `MaeRoom`; depois, movimento do host chegou a `MaeHouse`, seguido pelos dois.
- Pulsos de movimento do convidado em `MaeRoom` moveram Mae nos dois; posições diferiam menos de 0,01 unidade. Mudança do host para `BusStation` produziu posições iguais.
- Mutações de variáveis em `Title`, `MaeRoom` e `MaeHouse` foram corrigidas nas repetições: `AngusConstellations` voltou a `0`, e os hashes completos coincidiram após aplicar snapshots. Uma execução anterior v0.6.0 teve divergência temporária de hash em `MaeRoom`; o estado v0.6.1 agora registra primeira variável e hash para acompanhamento.
- A DLL final v0.6.1 foi recompilada, copiada a ambos e confirmada nos logs BepInEx. Repetir `MaeRoom` → `Title` com ela deixou ambos em `Title`, com hashes iguais. Campos de menu/sessão de QA estavam presentes, mas inativos; nenhum menu real de escolha foi alcançado.

## <a id="sources"></a>Fontes

- [Página Steam](https://store.steampowered.com/app/481510/Night_in_the_Woods/)
- [Diretório do jogo no repositório](https://github.com/cranebeaker/coop-anything/blob/main/DIRECTORY.md)
- [Versão BepInEx 5](https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5)
- Inspeção estática local da compilação isolada; dumps e caminhos específicos da máquina não entram neste repositório.

## <a id="maeroom-to-maehouse-interactive-follow-up-observed-2026-10-20"></a>Acompanhamento interativo de MaeRoom a MaeHouse (observado em 2026-10-20)

- Repetida execução por loopback com DLL v0.6.1 carregada nas duas pastas. Um pulso de 45 quadros do host em `MaeRoom` moveu ambos a x=2,791, com posições iguais. Pulso de 90 quadros à direita moveu ambos para `MaeHouse` em x=9,855, y=-1,373.
- Em `MaeHouse`, pulso de 90 quadros à esquerda do host não alterou nenhuma posição informada. Comandos `interact` dos bots host e convidado foram recebidos, mas nenhum expôs menu Yarn: `optionsActive` permaneceu false; nó/sessão e confirmação de escolha ficaram vazios/zero. Não se afirma resultado de sincronização de escolhas ao vivo.
- Ambos continuaram conectados, na mesma cena, com hash `2F4B5739` de `Continuity.vars` igual. Falha de movimento/interação limitada a esse estado de cena por script; causa desconhecida.

## <a id="fresh-save-opening-choice-check-observed-2026-10-20"></a>Verificação da escolha inicial em salvamento novo (observada em 2026-10-20)

- Protótipo recompilado como v0.6.3, host e convidado iniciados de pastas isoladas em loopback. Confirmação do convidado em `Title` levou ambos a `IntroPoem`; confirmações adicionais avançaram o poema nos dois.
- Seta direita do host seguida de confirmação do convidado alcançou o caminho alterado de `DialogueUI.SetOption`. Ambos registraram confirmação `1`, sessão `1316`, índice `1`, nó Yarn vazio e hash `236FB091`; o convidado não registrou aviso de confirmação ausente. A regra atual aceita a sessão quando ambos os nomes de nó estão vazios.
- Isso confirma que a confirmação foi transportada aos dois na abertura. O índice efetivamente substituído no callback cliente e efeitos posteriores da ramificação não são expostos diretamente pelo estado; resultados idênticos da escolha continuam sem verificação. Não se afirma modo cooperativo jogável.

## <a id="v064-choice-application-diagnostic-run-observed-2026-10-20"></a>Diagnóstico da aplicação de escolhas v0.6.4 (observado em 2026-10-20)

- Protótipo recompilado como v0.6.4, com campos de estado do convidado para última confirmação de escolha aplicada, sessão cliente ativa e confirmação adiada do host.
- Host e convidado iniciados em pastas separadas; ambos informaram conexão por loopback UDP 39752 e chegaram a `IntroPoem` após confirmação do convidado. Ambos informaram o mesmo hash de `Continuity.vars` após a transição.
- Durante confirmações adicionais do bot convidado, o host registrou escolhas 1 e 2 na sessão 245, índice 0 e nó Yarn vazio. Na amostra final, o convidado havia recebido a confirmação 2, mas `lastAppliedChoiceCommitId` ainda era 0, `clientActiveOptionSession` era 0, e `optionsActive` era false nos dois.
- A amostra não estabelece execução do callback com menu ativo. Mostra que receber o pacote de confirmação não basta como evidência de aplicação da escolha no cliente. Índice do callback, ramificação e efeitos continuam sem verificação; não se afirma modo cooperativo jogável.
- A primeira tentativa usou substituição temporária do arquivo de estado, não herdada quando clientes reiniciaram pela interface, deixando arquivos personalizados obsoletos. A amostra bem-sucedida usou `CoopStatus-Host.txt` e `CoopStatus-Client.txt` normais. O log convidado registrou um aviso de recepção UDP antes da conexão dos pares.

## <a id="v065-choice-application-follow-up-observed-2026-10-20"></a>Acompanhamento da aplicação de escolhas v0.6.5 (observado em 2026-10-20)

- A alternativa de `DialogueUI.SetOption` do convidado passou a aceitar uma escolha confirmada do host quando sessão e nó Yarn coincidem, mesmo se `runningOptions` do convidado já for false. Acrescentado log quando o callback substitui o índice.
- v0.6.5 recompilada e carregamento confirmado nos dois. Conectaram por loopback UDP 39752; uma confirmação do convidado levou ambos de `Title` a `IntroPoem`, com hash `236FB091` igual.
- Na execução da abertura por bot, o host registrou confirmação 1 para sessão 251, índice 0 e nó vazio. O estado do convidado avançou `lastAppliedChoiceCommitId` a 1, e o log informou aplicação de confirmação 1 no índice 0 para sessão 251. Ambos informaram `IntroPoem` e hash `236FB091` depois.
- Evidência direta de que o callback `SetOption` do convidado substituiu o índice confirmado pelo host nesta escolha 0. Ramificação e efeitos por script não foram observados independentemente; escolha não zero, entrada normal, progresso mais amplo, salvamentos e modo cooperativo completo continuam sem verificação. Não se afirma modo jogável.
- Oito pulsos posteriores de confirmação do convidado não produziram outra confirmação `SetOption` nem avançaram a cena; ambos ficaram em `IntroPoem`, confirmação 1, hash `236FB091` igual. Motivo desconhecido.

## <a id="v065-progression-and-bot-confirm-diagnostics-observed-2026-10-20"></a>Diagnósticos de progressão e confirmação por bot v0.6.5 (observados em 2026-10-20)

- No par v0.6.5 ainda rodando, comando de cena exclusivo de QA do host moveu ambos de `IntroPoem` a `MaeRoom`; ambos informaram jogador ativo na mesma posição. Dois `move_right:90` consecutivos do host moveram ambos a `MaeHouse`, posição igual (x=9,855, y=-1,373). Após uma amostra anterior, hashes de história diferiam (43AD2F28 e 23FC1D70); amostra posterior coincidiu em C80A7CF8. Tempo e causa da convergência não estabelecidos.
- Inspeção estática do assembly isolado mostra que `SupplementalIntroBrain` faz transição de entrada, espera `Global.IsConfirmOrInteractDown()`, faz transição de saída e chama `LoadLevel(sceneToLoad)`. Em amostra ao vivo, `confirm` do bot host foi enviado ao convidado (contadores de pacotes e confirmações observadas aumentaram), mas o contador observado do host não aumentou, e ambos ficaram em `IntroPoem`. Isso revelou lacuna na entrada do bot de QA do host; não estabelece comportamento de entrada física do host nem confirmação convidado→host nessa cena.
- Alteração local v0.6.6 acrescenta caminho de confirmação único do bot host e contador de confirmações consumidas; compilou contra os assemblies isolados. O par ativo ainda tinha v0.6.5, então a alteração não foi exercitada no jogo.
- Uma amostra posterior de `interact` em `MaeHouse` deixou opções inativas; posição informada abaixo do piso inicial. Nenhum resultado de escolha ou ramificação é afirmado. Progressão normal e interação confiável continuam sem verificação.

## <a id="v066-relaunch-check-observed-2026-10-21"></a>Verificação de reinicialização v0.6.6 (observada em 2026-10-21)

- Após fechar o par anterior, DLL v0.6.6 foi preparada nas duas pastas. Logs de ambas as instâncias confirmam carregamento da v0.6.6.
- Primeira reinicialização informou portas divergentes (host 39753, convidado 39752), sem conexão. Foi incompatibilidade de configuração, não teste de portas iguais.
- `confirm` do bot host na tela inicial deixou `botConfirmConsumed=0` e `confirmObserved=0`. A tela não exercitou o hook de `Global.IsConfirmOrInteractDown`; isso não aprova nem reprova a alteração.
- Correção do bot compilou, mas comportamento no jogo permanece sem verificação. Ramificações normais, efeitos e modo cooperativo completo continuam sem verificação; não se afirma jogabilidade.
- Em tentativa posterior com Steam aberto e ambas as configurações na porta 39753, o estado do host atualizou e informou `waiting on UDP 39753`; convidado informou `connecting to 127.0.0.1:39753`. Continuaram desconectados. Log do convidado: `UDP receive error: An invalid argument was supplied.` Nenhum teste ao vivo de escolhas ou jogabilidade ocorreu nessa tentativa.
