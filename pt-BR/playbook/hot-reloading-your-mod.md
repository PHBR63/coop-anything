# <a id="hot-reloading-your-mod-swap-the-dll-without-restarting-the-game"></a>Recarregamento do mod em execução: troque a DLL sem reiniciar o jogo

Uma rodada de correção em mod cooperativo que exige reinício custa minutos, quase todos fora do seu código: iniciar o jogo, carregar um salvamento e voltar ao ponto da falha. Se o mod for uma DLL dentro do processo, você pode eliminar essas etapas. Mantenha um carregador pequeno no jogo, coloque o restante do mod em uma segunda DLL e troque essa DLL com o jogo em execução.

Código e testes: [tools/hotreload](../tools/hotreload/README.md). Relacionados: [fast-iteration.md](fast-iteration.md) (a rodada completa de correção, da qual isto é uma parte), [multi-instance-testing.md](multi-instance-testing.md), [automated-qa.md](automated-qa.md), [desync-hunting.md](desync-hunting.md).

**Somente para seu próprio mod na sua própria cópia de um jogo.** Nunca use contra um jogo on-line com sistema antitrapaça. Teste em cópia da instalação e não faça trocas em um jogo que o usuário esteja jogando.

## <a id="when-it-works"></a>Quando funciona

- O mod é uma DLL nativa carregada no processo (plugin de extensão de scripts, plugin ASI, biblioteca injetada). Mods somente de scripts ou dados já recarregam sem isso.
- Você consegue inserir no ponto de entrada do plugin uma chamada executada uma vez por quadro na thread principal.
- Você aceita manter uma separação clara: ponteiros mantidos pelo jogo ou por uma biblioteca não podem apontar para o código substituído.

Se o mod aplica patches ao código do jogo, ainda funciona, mas é preciso restaurar os bytes originais e tirar de uso seus trampolins (consulte "Mods que aplicam patches ao código" abaixo).

## <a id="the-pattern"></a>O padrão

```
 game process
 +------------------------------------------------------------+
 |  loader (stays)            core DLL (swapped)              |
 |  - plugin entry point      - your mod's logic              |
 |  - control pipe            - your threads, hooks, sockets  |
 |  - cache copy of the core  - saves and restores its state  |
 |  - state blob store        - drains before it unloads      |
 +------------------------------------------------------------+
        ^                                   ^
   hotreload.py swap  ---  copies the new DLL over the core file, asks the loader to reload
```

1. **Carregador permanente.** Pequeno, quase nunca muda e nunca é descarregado. Alterá-lo exige reinício normal.
2. **Núcleo recarregável.** O carregador copia o núcleo para um arquivo de cache privado e mapeia a cópia. Isso permite à compilação sobrescrever o original: Windows não permite sobrescrever uma DLL carregada.
3. **Estado versionado.** Tudo que precisa sobreviver é escrito por "participantes" em um bloco de dados mantido em memória pelo carregador e relido pela próxima compilação. Cada participante tem uma versão de organização. Uma versão anterior é convertida por uma etapa `migrate`, ou o participante inicia do zero e informa isso.
4. **Drenagem.** Antes de remover o mapeamento, aguarde até que nenhuma thread execute código do núcleo. Uma thread conta como interna quando seu ponteiro de instrução está na imagem do núcleo ou qualquer endereço de retorno na pilha aponta para ela. Threads pertencentes ao núcleo são excluídas, pois seu responsável aguarda o encerramento delas após a drenagem.
5. **Identificador de compilação.** CRC-32 e tamanho da cópia mapeada. A ferramenta de troca calcula os mesmos valores para o arquivo copiado, comprovando que "a compilação que acabei de criar é a que está rodando".
6. **Recusa limpa.** Uma troca insegura para antes de qualquer descarregamento. O núcleo anterior continua funcionando com todo o estado, e a ferramenta explica o motivo.

## <a id="the-rule-that-bites-every-thread-the-core-owns-must-be-registered"></a>A regra que costuma surpreender: toda thread do núcleo deve ser registrada

Na primeira tentativa em um mod real, a drenagem provavelmente recusará, quase sempre por causa de uma thread. Um trabalhador parado aguardando tarefas tem o ponteiro de instrução no kernel, mas sua pilha contém endereços de retorno do seu código; portanto, conta como estando no núcleo. A drenagem espera que ele saia, ele nunca sai e todo recarregamento excede o limite de tempo.

A solução não é enfraquecer a drenagem. Informe quais threads pertencem a você e serão encerradas por você:

- Inicie suas threads por `hotreload::ManagedThread`. Elas são registradas, paradas e aguardadas automaticamente.
- Para uma thread que não pode iniciar assim (um trabalhador criado por uma biblioteca vinculada), chame `hotreload::adoptThread(tid)` quando começar e `releaseThread(tid)` após aguardar seu encerramento no `shutdown` do participante.
- Qualquer outra execução do seu código, como callback em uma thread do motor, conta como interna durante a chamada, e a drenagem espera corretamente.

A recusa é limpa. O relatório informa `drain timed out ... thread N is still inside the code that
would be unloaded: return address ... points into the core image`, e o mod continua funcionando. O host de teste da ferramenta inclui um núcleo criado com exatamente esse erro e um teste que verifica a recusa.

## <a id="the-other-mistakes-in-the-order-they-show-up"></a>Outros erros, na ordem em que aparecem

| Erro | O que você vê | Correção |
|---|---|---|
| Estado mantido em estática não registrada | contador, sessão ou lista de missões carregadas reinicia após a troca | adicionar participante que salve e restaure |
| Organização salva alterada sem incrementar a versão | dados inválidos após a troca ou `restore` lendo além da carga | incrementar `version`, adicionar `migrate` ou aceitar início do zero |
| `save` que altera estado | recarregamento recusado deixa núcleo antigo parcialmente alterado | `save` deve somente ler |
| Hook não removido em `shutdown` | descarregamento recusado (sonda de vazamento) ou falha posterior do jogo | removê-lo e acrescentar sonda de vazamento para hooks instalados |
| Socket fechado em `shutdown` que o novo núcleo quer usar | pares desconectam a cada troca | guardar handle como inteiro no bloco de dados e deixá-lo aberto |
| Outro mod encadeado sobre seu hook | "hook was chained over by another mod" na recusa | retornar esse motivo de `canUnload`; não descarregar |
| Ponteiro do carregador ou jogo para o núcleo | falha logo após remover o mapeamento | registrar somente pela API do carregador, para que ele remova antes de descarregar |
| `std::string` ou exceção cruzando a separação entre carregador e núcleo | falhas dependentes da compilação | somente tipos C simples nessa fronteira |
| Destrutores estáticos que aguardam threads | jogo trava ao sair | alocar objetos de thread duradouros no heap e deixar o sistema operacional encerrá-los |
| Compilar diretamente sobre o arquivo de núcleo ativo | ferramenta recusa (`--dll` é o núcleo ativo) | compilar em outra pasta e deixar a ferramenta copiar |

## <a id="mods-that-patch-code"></a>Mods que aplicam patches ao código

A integração de recarregamento não conhece seus hooks. Três callbacks os cobrem (`hotreload::SetDrainHooks`):

- `suspend`: restaure os bytes originais para impedir novas entradas em desvios. Retorne quantos hooks não puderam ser removidos.
- `extraRanges`: seus trampolins e código gerado, para considerar ocupada uma thread dentro deles.
- `resume`: reinstale os hooks quando a drenagem recusar, mantendo o núcleo funcional.

A ordem importa. Primeiro remova os hooks, depois execute a drenagem, encerre os participantes na ordem inversa e leia as sondas de vazamento. Registre uma sonda para hooks instalados, fazendo um hook não removido recusar o descarregamento em vez de causar falha.

## <a id="steps-for-an-agent-adding-this-to-a-mod"></a>Etapas para um agente integrar isso a um mod

1. Leia [tools/hotreload/README.md](../tools/hotreload/README.md) e [examples/core/example_core.cpp](../tools/hotreload/examples/core/example_core.cpp).
2. Compile a ferramenta e execute seus testes: `python -I tools/hotreload/run_tests.py`. Eles não exigem jogo.
3. Localize o ponto de entrada do plugin. Decida o que fica no carregador: ponto de entrada, chamada por quadro, encaminhamento de mensagens. Todo o restante é o núcleo. Mantenha uma nota curta de cada global, thread, hook e socket encontrado ao mover código; cada um vira participante, `ManagedThread` (ou `adoptThread`), hook com sonda de vazamento ou handle no bloco de dados.
4. Compile o mod separado (carregador e núcleo). Inicie uma **cópia** do jogo uma vez com o carregador.
5. Execute `python -I tools/hotreload/hotreload.py swap --pipe <name> --dll <core> --dry-run`. Código de saída 2 informa o que falta.
6. Faça a troca real e leia o relatório. Confira `reload.state` para falhas e reinícios do zero, além do log na pasta de cache se a drenagem recusou.
7. Escreva e mantenha um bot ou script que confira o estado importante durante a troca (contador, sessão, tabela de responsabilidade). Consulte [automated-qa.md](automated-qa.md).
8. Registre a separação carregador/núcleo, os participantes e a lista de threads no relato do jogo, evitando que o próximo agente precise redescobri-los.

## <a id="the-round"></a>A rodada

```
build the core only                 (seconds, not a full rebuild)
hotreload.py swap --pipe ...        (the game keeps running; a state blob goes across)
run the test or the bot             (no save load, no menu)
read the failure reason, fix, repeat
```

Execute o teste inteiro, não apenas parte, antes de considerar a correção concluída. Alterações no carregador, no cabeçalho de fronteira ou em algo mantido pelo carregador ainda exigem um reinício.

## <a id="proving-it"></a>Como comprovar

```
python -I tools/hotreload/run_tests.py
```

Compila o carregador, bibliotecas, seis núcleos de exemplo e um host de teste que substitui o jogo; executa testes unitários e cenários de troca (estado preservado, recusas, reversão, thread não registrada) e confere todas as variantes de mutação. Exibe `ALL OK` somente se todos os testes passarem e todas as variantes forem detectadas. Os testes usam o host substituto; para seu mod, acrescente a verificação importante: o estado que interessa, atravessando uma troca, no seu jogo.
