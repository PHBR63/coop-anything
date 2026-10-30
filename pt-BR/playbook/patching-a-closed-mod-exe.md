# <a id="patching-a-bug-inside-a-mods-own-rebuilt-exe"></a>Corrigindo um bug dentro do executável recompilado de um mod

Às vezes o bug não está no jogo, mas no mod, distribuído como executável recompilado cujo código-fonte é apenas parcialmente público. Você pode ler o código do subsistema relevante, mas o binário usado pelo jogador foi compilado com o código fechado do jogo vinculado; portanto, não basta recompilar. Ainda há tudo de que você precisa: o código público é um mapa do executável, e um pequeno patch independente pode inserir a correção no binário sem seu sistema de compilação.

Esta página descreve o caminho usado em Outlast (OpenOL): uma regra de jogabilidade de uma linha acrescentada a `OLGame.exe` recompilado, com código multiplayer público e motor fechado. Exemplo completo e código: [tools/outlast-coop/exe-patch](https://github.com/G3RKA/OpenOL/tree/main/tools/outlast-coop/exe-patch) em um fork próprio de OpenOL. Leia antes [reverse-engineering.md](reverse-engineering.md) para conhecer as ferramentas de descompilação.

## <a id="when-this-applies"></a>Quando se aplica

- Um mod recompila o executável do jogo (ou DLL), e o bug está na lógica do próprio mod.
- Parte do código do mod é pública (o subsistema com o bug); o restante não.
- Recompilar tudo está fora de alcance: fonte do motor ausente, bibliotecas estáticas fechadas ou compilação impossível de reproduzir byte a byte.
- A correção é pequena e localizada: regra, proteção ou chamada redirecionada, não uma reformulação.

Sem nenhum código público, trata-se de engenharia reversa comum; se todo o código for público, recompile. Esta página cobre o caso intermediário.

## <a id="1-use-the-public-source-as-a-map"></a>1. Use o código público como mapa

Leia o código do subsistema defeituoso antes de abrir o descompilador. Anote nomes de funções, tipos, campos e ordem das operações. Você não vai compilar esse código: vai encontrar as mesmas funções e campos de estruturas no binário e alterar uma coisa. O código indica a aparência esperada do binário; assim, cada endereço e deslocamento recuperado pode ser verificado, em vez de adivinhado.

No Outlast, o subsistema era a replicação de inimigos em `Development/Src/Multiplayer/Src/EnemyChannel.cpp` público do OpenOL: cada cliente executava a IA de cada inimigo posicionado no mapa e o enviava; cada cliente transformava o recebido num segundo representante, mostrando dois inimigos no mesmo lugar. A correção é uma regra (o menor ID de jogador mantém o inimigo real) em dois pontos nomeados no código: `ApplySpawn` e `TickSend`.

## <a id="2-find-the-functions-by-anchoring-on-unique-strings"></a>2. Encontre funções usando strings exclusivas como âncoras

Endereços mudam entre compilações e o binário não tem símbolos; não procure uma função pelo formato. Use uma string exclusiva dela: formato de depuração ou log, mensagem de erro, literal de `Tag`/nome, nome de classe comparado no código. Procure a string na imagem e liste suas referências. Uma boa âncora normalmente leva à função ou a uma chamada de distância.

Execute sem interface para ser reproduzível. O exemplo usa três pequenos scripts Ghidra ([ghidra/](https://github.com/G3RKA/OpenOL/tree/main/tools/outlast-coop/exe-patch/ghidra)): `FindStr` (encontra substring ASCII e UTF-16 e mostra as funções que a referenciam), `RefsTo` (lista funções que referenciam um endereço) e o par `Decomp`/`Dis` para ler uma função. No Outlast, o literal de tag `MultiplayerDummyEnemy` do representante levou diretamente a `ApplySpawn`; seu único chamador direto era o despachante de pacotes. As globais de sincronização de inimigos (`LocalPlayerID`, `SyncEnemies`) foram encontradas da mesma forma e usadas para condicionar o novo código.

## <a id="3-confirm-every-struct-field-offset-against-the-source"></a>3. Confirme cada deslocamento de campo com o código-fonte

O descompilador mostra acessos a campos como deslocamentos brutos (`+0xeb8`, `+0x44`, `+0x18`). Não confie em um isoladamente. Para cada campo alterado, relacione o deslocamento ao código: tamanho do elemento de vetor, ordem dos membros, campo próximo de significado conhecido. Leia uma função compreendida (getter, construtor) para determinar o deslocamento e reutilizá-lo. Um único deslocamento errado escreve no campo errado e corrompe o estado sem que SHA-256 detecte; dedique tempo a esta etapa.

As notas de Outlast registram cada deslocamento junto à linha de origem: `RemoteEnemies` em `+0xeb8` do controlador (contagem `+0xec0`, passo de elemento `0x44`), `CachedEnemies` em `+0xe78`, `DummyEnemy +0x10`, `OwnerID +0x18`, `UObject::Class +0x50` (confirmado porque `Index +0x38` e `Name +0x48` eram visíveis em `GetName()`). Registre assim para permitir nova verificação após atualizar o mod.

## <a id="4-write-the-fix-as-freestanding-c"></a>4. Escreva a correção como C independente

Escreva o patch em C sem runtime: sem libc, importações ou relocações. Precisa rodar como um bloco inserido no executável num endereço desconhecido pelo vinculador; não pode importar funções nem referenciar globais por endereço realocado. Regras práticas para manter o bloco compilado independente de posição:

- **Leia a base da imagem no PEB** e acesse tudo (funções e globais do mod) como *base da imagem + RVA conhecido*. Isso torna a aleatorização de endereços (ASLR) irrelevante: o bloco calcula os endereços reais em execução. No Windows x64: `mov rax, gs:[0x60]` (PEB), depois `mov rax, [rax+0x10]` (`ImageBaseAddress`).
- **Chame funções do mod pela base da imagem**, convertidas em ponteiros de função (`((Fn)(ib + RVA_DESTROYACTOR))(...)`), em vez de vinculá-las.
- **Forneça floats como inteiros imediatos.** Uma constante float cairia em `.rdata` e exigiria relocação. Codifique seu padrão de 32 bits e mova-o para um registrador xmm (`150*150` vira o imediato `0x46afc800`), evitando um conjunto de constantes emitido pelo compilador.
- **Compile sem libc nem informações de desenrolamento:** `-ffreestanding -fno-asynchronous-unwind-tables -fno-stack-protector -fno-ident -mno-red-zone`; depois confira que o objeto não tenha relocações `REL32`/`ADDR64` antes de confiar nele. O `build.py` de Outlast rejeita a compilação se restar qualquer relocação.

Mantenha o bloco pequeno (o de Outlast tem cerca de 1 KB) e use `used`/`noinline` nas funções de entrada para evitar remoção ou expansão inline.

## <a id="5-append-a-section-and-redirect-one-call-site"></a>5. Acrescente uma seção e redirecione um ponto de chamada

Coloque o bloco numa nova seção PE depois da última (a ferramenta de Outlast a chama `.olfix`), ajuste `SizeOfImage` e a contagem de seções e zere o checksum (o carregador não verifica o checksum do executável). Depois redirecione o menor número de chamadas que viabilize a correção, idealmente uma:

- **Chamada direta:** substitua `E8 rel32` por um novo `rel32` para o hook. Ele faz seu trabalho e chama a original pela base da imagem.
- **Chamada virtual:** substitua a chamada indireta (`FF 90 <disp32>`, 6 bytes) por `E8 rel32` mais um `NOP` para manter o tamanho, apontando para o hook; este lê a vtable para acessar a original. Faça isso somente quando uma chamada direta não bastar.

No Outlast, dois pontos foram redirecionados porque a regra tem duas metades (descartar nossa cópia ao receber a do outro cliente e ao preparar o envio da nossa): `call ApplySpawn` direta em `OnBinaryPacket` e `call [rax+0x268]` por vtable (`SendSpawn`) em `TickSend`. Cada hook executa a original e aplica a regra do menor ID.

## <a id="6-ship-it-as-a-script-that-checks-sha-256-and-never-overwrites-its-input"></a>6. Distribua um script que confira SHA-256 e nunca sobrescreva a entrada

Entregue o patch como ferramenta, não binário pronto (você não pode redistribuir o executável do mod; veja [AGENTS.md](../AGENTS.md)). A ferramenta:

- Lê a entrada e **recusa qualquer arquivo cujo SHA-256 não corresponda à compilação exata** usada para escrever o patch. Compilação errada significa deslocamentos errados; recuse em vez de corromper.
- **Nunca escreve na entrada.** Recebe um caminho de saída, recusa se for igual à entrada e preserva o executável original. Reaplicar sobre a saída é recusado pela mesma verificação SHA-256.
- Protege cada byte substituído com `expect` sobre os bytes atuais, interrompendo o patch em caso de endereço errado, em vez de danificar uma instrução aleatória.

O exemplo de Outlast distribui `apply_patch.py` com auxiliar PE em Python puro (`pe.py`) e `build.py` que recompila o bloco a partir de `olfix.c`; o `olfix.json` versionado é a compilação exata dos testes, e um port PowerShell ([`play/apply-native-patch.ps1`](https://github.com/G3RKA/OpenOL/tree/main/tools/outlast-coop/play/apply-native-patch.ps1)) faz o mesmo para jogadores sem Python. Registre os hashes esperados de entrada e saída corrigida para qualquer pessoa confirmar o mesmo arquivo.

## <a id="7-prove-it-with-a-twin-run"></a>7. Comprove com uma execução de controle

Um patch aprovado num teste não prova nada até se comprovar que o teste falha sem ele. Execute a **mesma suíte no executável não modificado com a mesma configuração**: o bug precisa continuar aparecendo. Se o controle também passar, o teste não exercita a correção (caso anterior consumiu a precondição, modo voltou silenciosamente a outro, asserção vazia; veja [automated-qa.md](automated-qa.md)). Só conta um PASS com patch acompanhado de FAIL sem patch.

No Outlast, o grupo A executou ambos lado a lado: o corrigido teve 10 de 10 PASS, incluindo A4 (um responsável), A4b (ID maior carrega primeiro) e A4c (ambos os processos vivos após a transferência); o controle, executável original na mesma execução, teve A4/A4b XFAIL, um inimigo no mesmo local enviado por ambos os clientes, exatamente como nas execuções anteriores.

## <a id="snags-we-hit"></a>Dificuldades encontradas

- **Ghidra sem interface falha com espaços no caminho.** `analyzeHeadless.bat` corrompe caminhos de projeto ou script com espaço. Trabalhe sem espaços: crie uma junção para a pasta de trabalho (`New-Item -ItemType Junction`) e execute por ela. O inicializador `ghidra/gh.ps1` de Outlast pressupõe isso.
- **Retroceda do resultado de substring até o início da string.** A busca encontra o meio de uma string maior, mas referências apontam para seu *endereço inicial*. Recue até o byte anterior ser terminador (dois bytes zero para UTF-16) e liste as referências ao início. `FindStr` faz isso antes de exibi-las.
- **Uma referência nem sempre é um chamador.** Entradas que o descompilador lista como referências a uma função podem ser posições de tabelas de tratamento de exceções ou outras tabelas nativas, não chamadas reais. Confirme lendo a instrução (um `call` real), em vez de confiar na lista de referências cruzadas.
