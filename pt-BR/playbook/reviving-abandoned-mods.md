# <a id="reviving-a-half-finished-co-op-mod"></a>Retomando um mod cooperativo inacabado

A maioria dos jogos mais queridos já tem alguma tentativa cooperativa em algum lugar: uma versão alfa parada, uma beta fechada, um fork com um colaborador. Concluir uma delas é preferível a começar do zero. Foi esse o caminho que funcionou para Deus Ex (HX, última compilação em 2019) e STALKER Shadow of Chernobyl (patch de correções de Shadow of COOP).

## <a id="1-find-every-fragment"></a>1. Encontre todos os fragmentos

- Pesquise GitHub (código e forks), ModDB, Nexus, Reddit, fóruns Steam, cópias de sites encerrados no archive.org e o Discord da comunidade do jogo. Leia [research.md](research.md).
- Procure a **última compilação**, não a última notícia. Autores frequentemente mantêm uma pasta de compilações ou testes mais recente que a página de versões.
- Confira os outros projetos do autor. O autor de HX também fez uma grande reformulação do mesmo jogo, o que explicou o estilo do código e algumas decisões de projeto.
- Registre a licença ou sua ausência. Sem uma licença, você pode estudar e aplicar patches, mas peça autorização antes de redistribuir os arquivos originais. Distribua suas correções como pacote separado e direcione os jogadores ao download original.

## <a id="2-get-readable-code"></a>2. Obtenha código legível

- **Camada de scripts:** muitos motores mantêm a lógica em pacotes de scripts (UnrealScript em arquivos `.u`, Lua em contêineres, Papyrus). Extraia-os como texto. No HX, um pequeno script Python extraiu 960 classes (cerca de 120 mil linhas) do pacote.
- **Camada nativa:** descompile com Ghidra sem interface (um script `DecompileAll` aplicado a todas as funções, escrito em um arquivo `.c` com índice de funções) ou uma ferramenta para agentes como REA. Mantenha uma ferramenta auxiliar de busca que extraia uma função pelo nome. Consulte [reverse-engineering.md](reverse-engineering.md).
- **Referência do jogo base:** obtenha os scripts originais se já tiverem sido publicados (Deus Ex distribuiu seu UnrealScript), para comparar o mod com o jogo base.

## <a id="3-audit-before-fixing"></a>3. Audite antes de corrigir

Divida o código por subsistema (jogador, dispositivos, conversas, armas, missões, viagens) e atribua cada um a um agente com instruções de somente leitura: listar bugs com arquivo e linha, como um jogador os encontraria e o grau de confiança. Depois **verifique pessoalmente cada afirmação** antes de corrigir. No HX, cerca de uma em seis afirmações estava errada; uma afirmação de que o host não conseguia usar computadores foi refutada por um teste em execução.

Também **compare todas as cópias do protocolo**. O lado servidor de um mod frequentemente existe duas vezes (um servidor independente e uma cópia compilada no jogo, ou um retransmissor e um cliente com IDs de pacotes copiados manualmente), e essas versões divergem. O OpenOL (Outlast) distribui uma cópia do retransmissor que ainda interpreta o formato de pacotes anterior aos canais; os clientes se reconectam silenciosamente a cada 30 s, e retransmissor e cliente discordam nos IDs dos pacotes de inimigos. Uma verificação de 10 minutos com um proxy de registro entre cliente e servidor encontra isso mais rápido que a leitura do código.

## <a id="4-fix-without-touching-the-original-package"></a>4. Corrija sem alterar o pacote original

Recompilar o pacote original muitas vezes é impossível (código ausente, classes nativas cuja disposição em memória fica numa DLL fechada, asserções do compilador). Em vez disso:

- Distribua um **pacote novo** que derive das classes defeituosas e as substitua em tempo de execução: uma subclasse do tipo de jogo, um mutator que substitui atores criados, subclasses de jogador escolhidas no login.
- Agrupe as correções em **módulos** (um por subsistema) aos quais o tipo de jogo encaminha hooks; assim, agentes em paralelo trabalham sem editar o mesmo arquivo.
- Mantenha `BUGS.md`: corrigidos, abertos, refutados e "fora de alcance" (em código nativo que você não pode alterar).

## <a id="5-test-it-live-then-automate"></a>5. Teste em execução e depois automatize

Primeiro coloque um host e um cliente real em execução num PC; depois transforme cada correção em um teste da suíte. Consulte [automated-qa.md](automated-qa.md). Testes em execução encontraram bugs que nenhuma auditoria detectou: cliente que falhava a cada terceira mudança de mapa, falha quando o inventário estava aberto durante a viagem e conversa forçada descartada silenciosamente.

## <a id="6-make-it-easy-to-play"></a>6. Facilite o jogo

- Instalador que encontra o jogo, copia arquivos e edita o INI: um arquivo por sistema operacional; consulte [shipping-to-players.md](shipping-to-players.md).
- Inicializadores para hospedar e entrar. Melhor ainda: retransmissão pelo Steam para ninguém digitar IP; consulte [networking-steam-spacewar.md](networking-steam-spacewar.md).
- README com os três passos e os problemas conhecidos em linguagem simples.

## <a id="7-give-it-back"></a>7. Devolva à comunidade

Publique as correções onde a comunidade original está (Discord, fórum, repositório), dê crédito ao autor original e adicione o projeto ao [diretório](../DIRECTORY.md) com seu nível de QA.
