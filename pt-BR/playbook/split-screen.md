# <a id="split-screen-co-op-on-one-pc"></a>Tela dividida: modo cooperativo em um PC

Tela dividida é a versão de sofá do modo cooperativo: várias cópias do jogo executam em uma máquina, cada uma em sua parte da tela e com seu próprio controle (ou teclado e mouse), comunicando-se pela pilha de rede local.

Isso torna a tela dividida uma **camada sobre o multiplayer**:

- Se o jogo já tem modo cooperativo em LAN ou on-line, o trabalho se concentra no inicializador. É aí que as ferramentas existentes se destacam.
- Se é exclusivamente para um jogador, primeiro crie o modo cooperativo (restante destes guias), depois acrescente a camada de tela dividida.

## <a id="starting-points"></a>Pontos de partida

Todos os projetos abaixo têm código-fonte público; agentes podem estudar, fazer forks e ampliá-los.

| Projeto | Plataforma | Licença | Notas |
|---|---|---|---|
| [Nucleus Co-op](https://github.com/SplitScreen-Me/splitscreenme-nucleus) | Windows | GPL-3.0 | Ferramenta mais usada, com mais de 700 "handlers" de jogos em [splitscreen.me](https://splitscreen.me/docs/games). Sua [API de handlers](https://www.splitscreen.me/docs/handler-api/) é o melhor catálogo de técnicas para múltiplas instâncias. |
| [PartyDeck](https://github.com/partydeck/partydeck) | Linux, SteamOS / Steam Deck | MIT | Inicializador mais recente: janelas Gamescope organizadas em sessão KWin, Bubblewrap para cada instância enxergar só seu controle, Proton (via UMU) para jogos Windows, Goldberg para multiplayer pela API Steam, até 4 instâncias, vários teclados e mouses desde 0.5 ([GamingOnLinux](https://gamingonlinux.com/2025/05/partydeck-is-a-split-screen-game-launcher-for-linux-steamos), [AUR](https://aur.archlinux.org/packages/partydeck-bin)). |
| [Couchlink](https://github.com/cranebeaker/couchlink) | Windows | MIT | Criado no Co-op Anything. Uma cópia por jogador em pastas com hardlinks; hook carregado como DLL de sistema substituta para cada cópia enxergar apenas seu controle (XInput, DirectInput, Raw Input e HID) ou teclado e mouse; cada jogador com conta Steam própria ou identidade Steam emulada; receitas assinadas; até 8 jogadores. Para autores de mods: skill `couchlink` aqui e `couchlink-sdk` no repositório dele. |

Antes de usar esses projetos como base:

- **Financiamento do Nucleus Co-op.** A equipe mantém um [Patreon](https://www.patreon.com/nucleus_coop/posts/new-nucleus-co-4-131882021), onde apoiadores recebem compilações e handlers de jogos populares (exemplos recentes incluem Monster Hunter e Subnautica 2) antes de se tornarem públicos; depois são liberados para todos. Alguns usuários criticam isso; outros consideram acesso antecipado normal ([discussão Steam](https://steamcommunity.com/app/3527290/discussions/0/592903515855138582/)). O código é GPL-3.0: você pode estudar, fazer fork e publicar seus handlers e melhorias, desde que derivados permaneçam GPL-3.0 com código-fonte disponível. A interface é antiga; criar uma nova é uma opção legítima.
- **A licença MIT do PartyDeck** é a mais permissiva: você pode reutilizar o código em qualquer projeto, mantendo o aviso de direitos autorais.
- Dê crédito aos dois projetos ao usá-los como base e devolva correções quando fizer sentido.

## <a id="how-split-screen-works-what-to-reuse"></a>Como a tela dividida funciona (o que reutilizar)

| Problema | Técnica | Onde procurar |
|---|---|---|
| Jogo recusa segunda cópia | Renomear ou encerrar mutex de instância única, neutralizar verificações FindWindow, cópias por instância (hardlinks ou symlinks) | API de handlers Nucleus: `KillMutex`, `RenameNotKillMutex`, `SymlinkGame`, `HardlinkGame` |
| Cópias compartilham configurações e salvamentos | Pastas Documents / AppData e INIs por instância. Motores fechados sem variáveis de ambiente: hook em `SHGetFolderPathA` (ou variante W) na DLL injetada, reescrevendo o caminho retornado conforme o token da instância | `UseNucleusEnvironment`, `DocumentsConfigPath` do Nucleus; sandbox Bubblewrap do PartyDeck; relato de Divinity II (proxy dinput8 + MinHook) |
| Steam permite uma cópia, ou o jogo exige sua rede | Emulador da API Steam por instância, para cópias que você possui, somente em LAN | `UseGoldberg` do Nucleus, integração Goldberg do PartyDeck |
| Entrada: toda cópia lê todos os controles | Hooks das APIs de entrada (XInput, DirectInput, entrada bruta) por instância, ou isolamento de dispositivos em sandbox | Hooks de entrada do Nucleus, filtragem de dispositivos Bubblewrap do PartyDeck |
| Organização das janelas e foco | Janelas sem borda redimensionadas por jogador; foco simulado para cópias em segundo plano continuarem rodando | `HookFocus`, `FakeFocus` do Nucleus; Gamescope e KWin do PartyDeck |
| Cópias precisam se encontrar | Apontar para 127.0.0.1 / descoberta LAN; modo LAN de um emulador | Opções de rede dos handlers, LAN Goldberg |

As mesmas técnicas permitem a uma estrutura de QA automatizado executar vários clientes em um PC (consulte [automated-qa.md](automated-qa.md) e [methods.md](methods.md)).

## <a id="the-other-route-a-second-player-inside-one-copy"></a>Outra rota: segundo jogador dentro de uma cópia

Executar várias cópias não é a única forma de jogar no sofá. Em um jogo com carregador de mods e tela compartilhada, você pode **criar um segundo personagem jogável dentro da única cópia em execução**. Sem rede nem segunda janela. Aprendido em Dave the Diver (Unity IL2CPP, BepInEx); consulte [games/dave-the-diver](../games/dave-the-diver/README.md).

- **Clone o jogador 1 em execução.** Clone o objeto e preencha novamente as referências que Unity não copia. Depois encontre e separe o estado ainda compartilhado: callbacks de entrada, tratadores de efeitos, callbacks de habilidades, recursos de comandos, oxigênio ou saúde. A maioria dos bugs iniciais vem desse estado compartilhado.
- **"Vez do jogador 2".** Código para um jogador encontra "o jogador" por um campo, muitas vezes em um singleton. Para reutilizar um sistema para o jogador 2 (agarrar, dano, pedidos de apertos repetidos, itens auxiliares, HUD), aponte esse campo para ele, chame o método do jogo e restaure. É muito menos trabalho que reescrever cada sistema. Localize o campo por descompilação: a mesma leitura `[singleton + offset]` aparece em todo método voltado ao jogador.
- **Eventos de animação dos inimigos** também costumam agir sobre "o jogador": animações de luta, dano por mordida. Insira hooks e execute-os na vez do jogador 2 quando a criatura estiver sobre ele. Nunca decida por "qual jogador está mais perto"; isso escolheu o jogador errado.
- **Entrada:** leia teclas ou controle do jogador 2 abaixo da camada de entrada do jogo (Win32 `GetAsyncKeyState`, XInput), evitando que cheguem ao jogador 1. `GetAsyncKeyState` também lê teclas sem foco na janela; verifique o foco antes de agir. Forneça ao jogo um teclado virtual com apenas as teclas do jogador 1. Quando uma tela do jogo (minijogo) precisar ler o jogador 2, forneça um controle virtual alimentado por suas teclas enquanto a tela estiver aberta.
- **Quando uma sequência não pode rodar duas vezes** (QTE em tela cheia, janela modal), pule-a para o jogador 2. Execute uma versão do mod que chame partes menores do jogo (iniciar/parar animação, dano, gatilho de resultado). Se a janela travar o jogador 1, controle diretamente seu personagem pelos próprios comandos até ela fechar.
- **Limite:** uma câmera. Siga o ponto médio, mantenha ambos visíveis e dê ao jogador 2 um HUD próprio, copiando e mudando as cores do HUD do jogo.
- **Segundo exemplo: Dead Cells** (HashLink, DCCM; [games/dead-cells](../games/dead-cells/README.md)). O jogo tem camada real para segundo controle; jogador 2 recebe objeto de controle próprio vinculado ao controle 2. Menus fazem bloqueio *exclusivo* da entrada do controle 1: ao entregar um menu ao jogador 2, libere esse bloqueio primeiro ou o jogador 1 continuará congelado. Uma segunda instância de HUD não pode compartilhar nada com a primeira (compartilhar minimapa ou contadores causava falhas nas mudanças de área); encontre por varredura de bytecode todas as funções que escrevem em "o HUD" e execute-as com o HUD do responsável. Procure estado mantido por perfil ou partida, não por personagem (roupa, contador de cargas de uma habilidade, contador de mortes, chaves no inventário "do herói"): cada um precisa de cópia por jogador ou regra compartilhada. Uma coleta que abre confirmação ainda pode ser recusada; dê a cópia do item ao parceiro somente quando a coleta terminar.

## <a id="split-screen-inside-one-copy-three-ways-mods-do-it"></a>Tela dividida em uma cópia: três abordagens dos mods

Três mods de outubro de 2026 mostram as principais opções quando todos jogam na mesma cópia. Confira o caso do seu jogo antes de escolher.

| Caso | Exemplo | Funcionamento |
|---|---|---|
| **Jogo tem tela dividida, mas menos jogadores no PC** | [BO3 4-Player Local Splitscreen](https://github.com/LocalPlayer123/BO3-4-Player-Local-Splitscreen-on-PC) (Black Ops III, domínio público) | Executável de PC compilado para 2 jogadores locais; a versão PS4 mantém 4. O mod move todo array por cliente local de `[2]` no PC para nova alocação `[4]` e reescreve cada instrução que o endereça. Só depois aumenta a contagem e amplia os loops de 2 para 4 (armazenamento primeiro, quantidade depois, ou vagas 2 e 3 sobrescrevem memória ativa). Algumas decisões exclusivas de 2 jogadores (organização dos painéis, entrada de controle, vagas de sombra solar) recebem hooks. Todo patch confere os bytes originais e não atua em compilação desconhecida. |
| **Sem tela dividida: desenhar o mundo por jogador** | [SplitScreen for Oblivion](https://www.nexusmods.com/oblivion/mods/56734) (plugin xOBSE, C++) | Renderiza o mundo duas vezes por quadro, uma por câmera, com modo "alternado" que desenha cada visão em quadros intercalados para GPUs mais fracas. O motor trata o jogador 2 como NPC; o plugin aplica a ele regras de jogador (inventário, níveis, fabricação, diálogo) e adapta scripts de missão que consultam "o jogador". O mundo só carrega ao redor do jogador 1, limitando a distância do jogador 2. |
| **Sem tela dividida: personagens extras por estrutura de scripts** | [RE2 Party Mode](https://www.nexusmods.com/residentevil22019/mods/3024) no REFramework (Lua e DLL de controle), baseado em Local Couch Co-op | Cria até 3 personagens adicionais, cada qual com câmera, quarto da tela, inventário e configurações. Inimigos miram no mais próximo em vez do jogador 1; a sala de cada jogador fica carregada dentro da área do jogador 1; chaves e itens de história vão ao jogador 1. |

O que se aplica a outros jogos:

- **Procure primeiro uma compilação de console.** Se tiver mais jogadores locais, ela serve de referência aos arrays, loops e verificações reduzidos no PC. Compare as duas antes de analisar somente o executável de PC.
- **Amplie o armazenamento antes da contagem de jogadores.** Qualquer loop que já alcance as novas vagas sobrescreve o que estiver após o array antigo.
- **Mantenha um responsável pela história.** As três abordagens vinculam progresso, itens-chave e mundo carregado ao jogador 1 e aproximam os outros dele. É a mesma regra da rota de [segundo jogador em uma cópia](#the-other-route-a-second-player-inside-one-copy) acima.
- **Inimigos precisam de regra de alvo.** IA para um jogador persegue "o jogador"; escolha explicitamente o mais próximo.
- **Considere o custo da segunda visão.** Desenhar o mundo duas vezes reduz a taxa de quadros (o mod de Oblivion cita cerca de 60 a 75 por cento da normal). Ofereça modo alternado.

## <a id="ideas-for-agents"></a>Ideias para agentes

- Escreva um handler Nucleus ou perfil PartyDeck para um jogo que acabou de tornar cooperativo e o distribua com a versão.
- Transfira conhecimento entre handlers: jogo que funciona no Nucleus para Windows é candidato ao PartyDeck no Steam Deck, e vice-versa.
- Crie um inicializador moderno sobre o código MIT do PartyDeck ou um fork GPL do Nucleus.
- Registre cada resultado de tela dividida no relato do jogo (`games/<slug>/`), com nível de QA.

## <a id="rules"></a>Regras

Emuladores da API Steam são para LAN, não para entrar em serviços on-line. Não publique handlers pagos ou de acesso antecipado de outras pessoas; escreva os seus.
