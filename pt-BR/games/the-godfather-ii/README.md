# <a id="the-godfather-ii-2009"></a>The Godfather II (2009)

| | |
|---|---|
| Motor | Visceral Engine (segundo PCGamingWiki; não confirmado pelo binário) |
| Versões testadas | `1.0.789.0` incluído no pacote do mod SE v0.56 do Nexus: **executável de terceiros não verificado**, não uma compilação de referência; execute somente em cópia descartável. Nela, inicia a campanha, com menu e jogabilidade confirmados. Versão comercial limpa `1.0.764.0` examinada somente de forma estática |
| Projetos | Multiplayer Revival (partidas multiplayer, não campanha) <https://www.nexusmods.com/thegodfather2/mods/95>; extensão de scripts The Godfather II SE (hook para mods, não cooperativo) <https://www.nexusmods.com/thegodfather2/mods/40>; VisceralToolkit (ferramentas de recursos/fluxos, em desenvolvimento) <https://github.com/Greavesy1899/VisceralToolkit> |
| Nível de QA | none (ainda sem suíte automatizada de asserções; já existem um percurso manual reproduzível de inicialização e ferramentas para criar uma) |
| Última atualização | 2026-10-21 |

## <a id="where-things-stand"></a>Situação atual

Ainda não existe projeto cooperativo de campanha para este jogo, e nenhum foi encontrado nas fontes públicas. O que mudou nesta rodada foi a base para esse projeto: agora o jogo é **executável e observável** em uma cópia isolada, e um pequeno plugin de código próprio carrega dentro dele pelo carregador ASI da extensão SE, oferecendo um ponto de hook compatível para um mod cooperativo.

Concretamente: o executável `1.0.789.0` incluído no SE v0.56 (novamente: executável de terceiros não verificado, utilizável somente como alvo de teste descartável) inicia de uma cópia descartável, chega ao menu principal, carrega um perfil de campanha existente e **entra diretamente na campanha, sem a introdução em Cuba**, executando a missão com HUD, NPCs e mapa do mundo. Nosso plugin lê a transformação mundial do jogador no motor a 5 Hz, e objetos de personagens e suas linhas de transformação podem ser localizados no processo ao vivo por inspetor externo. A única ponta em aberto é o local autoritativo da transformação de um segundo personagem, onde um representante do "jogador 2" precisaria escrever.

Registro de pesquisa com todos os endereços, causas de falha e caminhos sem saída: [NOTES.md](NOTES.md).

## <a id="existing-work"></a>Trabalhos existentes

- **Godfather II Multiplayer Revival** (<https://www.nexusmods.com/thegodfather2/mods/95>, de `paindubreak`, último envio 2026-08-06): restaura os modos originais de partidas on-line pelo servidor comunitário FESL/pareamento; após iniciar a partida, o jogo é ponto a ponto. Exige a compilação `1.0.789.0` e carregador ASI. É o multiplayer competitivo original, não uma campanha com história compartilhada, e não foi instalado nem iniciado aqui. O serviço original da EA está encerrado (PCGamingWiki); a retomada tem apenas relatos da comunidade.
- **The Godfather II SE** (<https://www.nexusmods.com/thegodfather2/mods/40>, de `Greavesy`/`Greavesy899`, v0.56, última atualização 2026-08-26): extensão de scripts/menu de mods com carregamento de arquivos avulsos, criação de NPCs/itens/veículos, carregamento de checkpoints e substituições de SimGroup. Inclui **executável do jogo de terceiros não verificado**, de compilação desconhecida e sem código-fonte ou licença públicos; não o trate como compilação-alvo nem o redistribua. Sua lista de bugs inclui relatos de falhas de API/inicialização. **Seu carregador é o hook usado aqui**: o `dinput8.dll` do pacote é o Ultimate ASI Loader e carrega plugins de terceiros em `scripts\*.asi`, permitindo distribuir um mod cooperativo como ASI.
- **VisceralToolkit** (<https://github.com/Greavesy1899/VisceralToolkit>, sem licença publicada): ferramentas de inspeção/edição para jogos do motor Visceral. A wiki identifica arquivos de fluxo `.str` versão 12 de Godfather II e lista tipos de recursos (grafos de navegação, MetaModels, `VariableDictionary`), com a maioria dos formatos marcada como desconhecida. Útil como pista para leitura de recursos, não como estrutura cooperativa.
- **Modo cooperativo de Dead Space 3** (<https://www.pcgamingwiki.com/wiki/Dead_Space_3>) usa um motor com o mesmo nome e foi lançado com campanha cooperativa para dois jogadores. É uma referência da família de motores sobre suas capacidades; nenhum código ou ferramenta foi encontrado ou reutilizado dele.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Recursos:** três arquivos contêiner `GODFATH*.viv` (assinatura `BIGF`) e cerca de 2.300 arquivos de fluxo `.str` versão 12 avulsos (assinatura `3slo`), cobrindo caminhos de missões e objetivos; sem arquivos Lua/scripts distribuídos.
- **Objetos do motor:** o motor mantém a matriz mundial do jogador em uma global (`0x0112E210` na compilação `1.0.789.0`) e as transformações de alvo/olho da câmera em `0x0112A840` / `0x0112A850`. Personagens são objetos com vtable de classe (`0x00D6B350`); sua posição é lida por getter virtual (`vtable+0x48` -> `this+0x3C0`). O motor reescreve a transformação de cada personagem pela própria cinemática a cada quadro; portanto, um representante só pode ser controlado dentro do processo e após essa atualização.
- **Scripts:** o motor expõe uma camada de scripts/comportamento aos dados do jogo (`GetPlayerPosition`, `SetPositionValues`, `CreatePosition`, `GetPlatform`, comandos de movimento como `moveToPos`): uma forma prevista de mover personagens que ainda não existe em nenhum mod público.
- **DRM:** o executável comercial limpo é protegido por SecuROM (seções `.securom` e `paul.dll`; PCGamingWiki informa 7.38.0015). A descompilação estática pelo Ghidra falha nesse executável (erros de fluxo inválido/sobreposição); não o descompacte. O executável não verificado `1.0.789.0` de terceiros do pacote SE descompila corretamente, por isso os endereços de memória nas notas vêm dele; é apenas alvo descartável de teste, não compilação de referência.

## <a id="what-we-changed"></a>O que alteramos

Nada em qualquer instalação, e nada publicado. Somente dentro de uma **cópia descartável**:

- três patches de bytes em `godfather2.exe` da cópia (cada um registrado nas notas privadas de identidade): verificação de capacidade abaixo dos requisitos, padrão de `Window.Fullscreen` e detector de fabricante de GPU que desreferencia um resultado NULL de `strstr`;
- plugin ASI próprio (`scripts\coopcore.asi`, código próprio), com cinco hooks do motor, log de estado do jogador a 5 Hz, redirecionamento de caminhos que preserva o perfil real EA Games da máquina, escritor do representante e tratador de exceções vetorizado como proteção;
- ferramentas próprias: inspetor/escritor externo para o jogo em execução, localizador de posição, extrator de contêineres, controlador de entrada/captura de tela, aplicador de patches de bytes no executável e sonda de ambiente D3D9.

Perfil, configurações e salvamentos de campanha preexistentes da máquina foram verificados como idênticos byte a byte ao backup anterior, e o hash do executável da instalação original permanece inalterado.

## <a id="qa"></a>QA

Ainda sem asserções automatizadas. Existe um procedimento reproduzível e as ferramentas para automatizá-lo:

1. iniciar a cópia descartável no host; o plugin redireciona caminhos do perfil para a cópia, sem escrever nos reais;
2. percurso do menu: qualquer tecla na abertura -> selecionar o perfil existente com clique real do mouse -> retomar o jogo salvo -> uma missão; a campanha carrega diretamente, sem introdução;
3. `coopcore_player.txt` junto ao executável passa a mostrar a posição ao vivo do jogador, e o inspetor externo pode extrair e comparar objetos do motor.

A mesma inicialização foi reproduzida no Windows Sandbox (vGPU, rede desativada), onde foram medidas as limitações dos modos de exibição. Observe que entradas sintéticas de mouse não alcançam a interface ali (o motor lê o ponteiro por Raw Input), por isso o host é a opção mais rápida para iterar.

## <a id="how-to-play"></a>Como jogar

Não há o que jogar: não existe versão cooperativa distribuída. O procedimento interno de teste é o percurso de menu acima.

## <a id="known-issues"></a>Problemas conhecidos

- A identidade da compilação varia: a cópia limpa informa `1.0.764.0`, enquanto os pacotes Multiplayer Revival e SE incluem compilações próprias e diferentes de `godfather2.exe`. Qualquer patch deve ser novamente derivado por compilação; todos os endereços nas notas pertencem somente à compilação SE `1.0.789.0`.
- A interface lê o mouse por Raw Input; a navegação por teclado funciona nos menus, mas a tela de perfil exige um clique real.
- Nossos hooks não alteram o tratamento de mouse dentro do jogo; portanto, um bot de teste por script ainda não consegue controlar o personagem por teclas sintéticas.

## <a id="next-steps"></a>Próximos passos

1. Encontrar a transformação autoritativa de um segundo personagem. Estabelecido: não é uma simples tripla de floats (uma busca de diferenças no heap inteiro não encontra nenhuma); os pares `.data`/heap como `0x01163640`/`0x04303640` são área temporária de renderização escrita pela multiplicação de matrizes `FUN_00417560` (chamadores `FUN_00419b80`, `FUN_0041b9d0`, dados de origem em TLS); escrever uma matriz no momento de PRESENT ocorre um quadro tarde demais para o esqueleto. A VM de scripts é o caminho correto: localizada ao vivo, `GetPlayerPosition` resolve para tipo 6 (uma função) por `FUN_00625ca0` + `FUN_00633cb0`, e os invólucros de chamada do jogo são `FUN_00468ea0`/`FUN_00468f40`, com limpeza da pilha em `FUN_006255e0`. Próximo: chamar o invólucro (não a `FUN_00636570` bruta) enquanto a atualização de scripts estiver ativa e mover o companheiro com `SetPositionValues`.
2. Com um local gravável, controlar um segundo personagem a partir da posição do jogador, criando o primeiro representante visível do "jogador 2", e verificar que o motor não o sobrescreva após a escrita.
3. Automatizar o percurso manual de inicialização (controlar o menu por teclas injetadas e acrescentar um monitor que verifique a chegada ao mapa da campanha).
4. Depois, escolher o hook cooperativo e o modelo de rede conforme `playbook/how-coop-mods-work.md` e `playbook/networking-steam-spacewar.md`.
