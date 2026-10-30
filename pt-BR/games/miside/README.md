# <a id="miside-2024"></a>MiSide (2024)

| | |
|---|---|
| Motor | Unity 2021.3.35f1, IL2CPP, Windows x64 (BepInEx 6.0.0-be.790 Unity.IL2CPP, HarmonyX, Il2CppInterop) |
| Versões testadas | Steam (app 2527500), buildid 19029065. `MiSideFull.exe` SHA-256 `562723c950c2be95ecbdc516530aee56b97837e2ac6610b8b5bce394e23022c0` |
| Projetos | MiSide Together ([miside-coop](https://github.com/multiplayereverything/miside-coop), [v0.3.2](https://github.com/multiplayereverything/miside-coop/releases/tag/v0.3.2)); entrada "MiSide Together" no diretório |
| Nível de QA | automated |
| Última atualização | 2026-10-27 |

## <a id="where-things-stand"></a>Situação atual

MiSide Together permite que 2 a 4 jogadores acompanhem juntos a história de MiSide. O host conduz. Todos carregam o mesmo capítulo, veem os mesmos diálogos, cenas e Mita e veem os outros jogadores como o personagem principal em sua pose real. É uma versão alfa. Todos os capítulos foram percorridos por testes automatizados com cópias ocultas do jogo em um PC. Os computadores das cenas 13 a 15 ainda não são compartilhados, e o Steam só foi testado com uma conta.

## <a id="existing-work"></a>Trabalhos existentes

- [QuestionBlock64/MiSide-Multiplayer](https://github.com/QuestionBlock64/MiSide-Multiplayer): mod multiplayer de MiSide em desenvolvimento, último envio em 2026-09. MiSide Together aproveitou ideias (retransmissão do rosto de Mita, olhar para o jogador mais próximo, lista de hooks de morte, clonagem de menus nativos). O repositório não tem licença; nenhum código foi copiado.
- Nenhum outro projeto cooperativo foi encontrado neste diretório. Steam Workshop, Nexus e sites em outros idiomas não foram pesquisados.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Motor:** IL2CPP. BepInEx 6 gera assemblies de interoperabilidade na primeira inicialização, cerca de 89 em aproximadamente um minuto, e os patches Harmony passam por Il2CppInterop. Descompilar a interoperabilidade fornece apenas assinaturas, sem corpos dos métodos. A opção `-mt-trace Type1,Type2` registra o endereço nativo de cada método e todas as chamadas durante o jogo, permitindo descompilar as funções realmente executadas.
- **História:** linear e por scripts. É conduzida por `UnityEvent`s em `ObjectInteractive.Click()` (a interação genérica de pressionar E), volumes de gatilho, linhas do tempo (`CutscenePlay`) e `Dialogue_3DText`. Por isso, retransmitir *eventos* da história foi mais adequado que retransmitir estado. Quem chega depois recebe a reprodução dos eventos da cena a partir de um histórico de atualização.
- **Carregamento de capítulos:** `SceneManager.LoadScene("Scene 1 - RealRoom")` carrega uma cena quebrada, com NRE a cada quadro e sem `PlayerMove`. O caminho do próprio jogo funciona: definir `GlobalGame.LoadingLevel` como o nome do capítulo e carregar `SceneLoading`. As mudanças de capítulo cooperativas executam `Scene_Load` do jogo em todas as máquinas.
- **Jogador:** `PlayerMove` é o controlador (`animPerson` é o Animator do corpo, além de `TeleportPlayer`). `PlayerPerson.meshes` e `meshHead` são os renderizadores do corpo. Itens segurados ficam vinculados sob os ossos das mãos, em `GlobalTag.playerRightItem`.
- **Steam:** `steam_api64.dll` acompanha o jogo, e Steamworks.NET está na interoperabilidade. Iniciar diretamente o executável faz o Steam reiniciá-lo e descartar os argumentos; por isso, as cópias de laboratório contêm `steam_appid.txt` (2527500).
- **Primeira inicialização:** uma instalação nova (sem configurações na pasta de salvamento) para em `SceneLoading` em um seletor LANGUAGE e VOICE (`ChangeLanguageStart`) até alguém escolher; cópias automatizadas ficam presas no carregamento sem erro em log. O laboratório responde como um jogador: `ChangeLanguage(i)`, `ChangeVoice(i, true)` e `Apply()`, com índices lidos dos botões de inglês (`ChangeLanguageStartButton.index`, diferenciados pelos pais `Language` / `Voice`).
- **Salvamentos:** clientes continuam a partir dos arquivos do host. Os próprios salvamentos recebem backup durante a conexão e são restaurados depois, ou na próxima inicialização após uma falha.

## <a id="what-we-changed"></a>O que alteramos

A lista completa de recursos está no README do mod e em [docs/SYNC.md](https://github.com/multiplayereverything/miside-coop/blob/main/docs/SYNC.md). [docs/SYNC-INVENTORY.md](https://github.com/multiplayereverything/miside-coop/blob/main/docs/SYNC-INVENTORY.md) classifica todos os scripts dos 19 capítulos. Esta seção reúne as lições aplicáveis a outros jogos.

### <a id="inventory-the-whole-game-before-syncing-it"></a>Inventarie o jogo inteiro antes de sincronizá-lo

Um percurso de um jogador (`inventory`) carrega todos os capítulos. Lista scripts, linhas de diálogo, escolhas e linhas do tempo em `SYNC-INVENTORY.md`, sem nenhum item não classificado. Cada linha informa como sincroniza, quem é responsável e qual percurso a comprova. O trabalho segue essa lista em vez de perseguir relatos de bugs.

### <a id="the-host-runs-every-cutscene"></a>O host executa todas as cenas

- **Bug:** cenas iniciadas pelos gatilhos de cada máquina divergiam, e um cliente podia iniciar uma que o host nunca via.
- **Correção:** durante um capítulo, o início de cena no cliente vira uma solicitação. O host inicia a cena, e todas as máquinas a reproduzem pelo comando e relógio do host. Os outros jogadores ficam ocultos durante a cena e são reunidos junto ao host em terreno seguro depois.
- **Comprovação:** no percurso `hostcut`, a cena do cliente ficou a 0,13 s da do host.

### <a id="held-items-read-the-rule-from-the-game-not-from-a-list-per-cutscene"></a>Itens segurados: leia a regra do jogo, não de uma lista por cena

- **Regra:** se a configuração da interação coloca um item na mão do jogador, apenas quem pressionou o faz, e todos veem o item no espaço da mão direita dele. Isso abrange o avião de brinquedo, telefone, cartucho e baterias, colher, arco e lápis da cena 2. As demais interações são espelhadas: cada jogador executa a mesma animação em seu personagem no mesmo local.
- **Detecção:** o mod lê a regra nos dados de interação do jogo; não mantém uma lista por cena.
- **Armadilha:** o item é o próprio objeto, movido para a mão quando a animação de coleta chega ao momento correspondente. A primeira versão observava o objeto errado, e algumas aprovações anteriores de testes eram falsas. Confira o que realmente termina sob o osso da mão.

### <a id="a-cutscene-can-be-playing-without-having-been-started"></a>Uma cena pode estar em reprodução sem ter sido iniciada

- **Bug:** na porta de saída da cena 12, o host entrou na cena e o cliente não, terminando separados por 4 m. Duas causas: o comando do host chegou um pouco antes de a história do cliente ativar o objeto da cena, sendo ignorado; e a linha do tempo do cliente já estava tocando desde a ativação, sem nunca executar `Playable_Animation.Play` (que coloca o jogador nela). Um terceiro fator: o evento da porta também inicia uma animação do jogador (esconder-se de Mita) que só é disparada no host.
- **Correção:** tentativas de início de cena são repetidas por 5 s, como os demais eventos da história, e o estado de reprodução só conta quando `Play` realmente rodou naquela máquina. O host informa toda animação que sua história inicia no próprio jogador; um cliente que não iniciou a mesma em até um segundo a reproduz (conferida pela chave própria do objeto cliente, que difere quando a ordem dos objetos irmãos difere).
- **Comprovação:** cena 12 no percurso de todos os capítulos, com os jogadores terminando a 0,00 m de distância.

### <a id="a-copy-of-the-first-person-body-needs-its-shadows-back"></a>Uma cópia do corpo em primeira pessoa precisa recuperar suas sombras

- **Bug:** o outro jogador parecia sem volume e claro demais ao lado de Mita. Os materiais usam o mesmo shader toon e valores iguais; a diferença é que o corpo em primeira pessoa tem `receiveShadows` desligado, mantendo a cópia completamente iluminada mesmo na sombra.
- **Correção:** ativar `receiveShadows` na cópia. Um dump de laboratório (`MT-LOOK`) lista shader, sondas, indicadores de sombra e valores toon de cada renderizador do corpo local, da cópia e dos demais personagens; assim o problema foi descoberto.

### <a id="presses-must-survive-a-machine-that-is-a-moment-behind"></a>Pressionamentos precisam sobreviver a uma máquina um pouco atrasada

- **Bug:** um pressionamento recebido por um cliente cujos objetos da sala ainda não estavam ativos ou estavam em outra ordem era perdido. Isso quebrava as alavancas da cena 17.
- **Correção:** repetir o pressionamento por até 5 s e localizar o objeto pela chave, usando seu nome como alternativa. Só são compartilhados pressionamentos que realmente funcionaram no remetente; pressionar algo ainda não habilitado pela história não faz nada para ninguém.

### <a id="il2cpp-stripping"></a>Remoção de código no IL2CPP

- **`Animator.parameters`** lança TypeLoadException com Il2CppInterop, e `get_parameters` foi removido. A compilação lê todos os AnimatorController dos dados do jogo do usuário com UnityPy: 282 parâmetros em 109 controladores. A tabela é incorporada e consultada pelo nome do controlador. As sobrecargas de string `Get/Set*` funcionam.
- **`GUILayout.BeginArea`** também foi removido. O painel F5 usa chamadas simples de `GUI`, e cada componente ausente usa um rótulo com tratamento de Input como alternativa.

## <a id="qa"></a>QA

- `scripts\run-tour.ps1 -Tour <name>` executa um percurso com 2 a 4 cópias ocultas de laboratório por loopback. `scripts\lab-suite.ps1` executa todos, um por vez. O laboratório faz backup e restaura a pasta de salvamentos do usuário e recusa iniciar enquanto o MiSide do próprio usuário estiver em execução.
- As linhas de log são avaliadas por `tests/verify-lab.py`:
  - `MT-CHECK`: asserções;
  - `MT-METRIC`: custo dos quadros, incluindo o pior;
  - `MT-STATE`: a cada 2 s, posição, rotação e estado de jogadores, NPCs, linhas de diálogo e linhas do tempo, alinhados entre máquinas em números de dessincronização;
  - `MT-ANIM`: atraso do início de cada animação de NPC nos clientes.
- **v0.3.2:** os 21 percursos passam com 2 a 4 jogadores, incluindo migração de host e teste com 120 ms de latência. `scripts\interactions-all.ps1` pressiona todas as interações de todos os capítulos com 2 jogadores: 17 de 18 capítulos passam. Resta a cena 13, em que o outro jogador continua sentado no PC após o host pegar o cartucho (só quem pressionou executa, portanto esperado).
- Não cobertos: a coleta do telefone da cena 1 em si (a abertura da cena segura o host no laboratório) e uma sessão Steam de duas contas pela retransmissão da Valve.

## <a id="how-to-play"></a>Como jogar

1. Instale BepInEx 6 (Unity.IL2CPP, win-x64), compilação be.790, em `<game dir>` e inicie o jogo uma vez.
2. Extraia uma [versão distribuída](https://github.com/multiplayereverything/miside-coop/releases) em `<game dir>`.
3. Abra **MULTIPLAYER** no menu principal. O host escolhe HOST GAME.
4. Os amigos escolhem JOIN <name> (STEAM), JOIN <name> (LAN) ou entrada por endereço (F5, TCP 27030).

Todos precisam da mesma compilação do jogo e do mod.

## <a id="known-issues"></a>Problemas conhecidos

- As pastas dos computadores das cenas 13 e 15, a conversa por telefone da cena 14 e o jogo de PC da cena 14 funcionam separadamente para cada jogador.
- O Tetris portátil é individual.
- A cena 19 (Glasses) não pode ser iniciada pelo menu de capítulos, nem no modo de um jogador. Acesse-a pela história.
- Um jogador que entra no meio do capítulo aguarda no menu até o início do próximo.

## <a id="next-steps"></a>Próximos passos

- Compartilhar os computadores das cenas 13 a 15.
- Fazer o percurso de todos os capítulos aceitar o assento da cena 13 e comprovar a coleta do telefone da cena 1.
- Executar uma sessão Steam real com duas contas.
- Concluir a história em modo cooperativo e documentar para `verified-playthrough`.
