# <a id="a-difficult-game-about-climbing-2024"></a>A Difficult Game About Climbing (2024)

| | |
|---|---|
| Motor | Unity 2021.3.21, backend de scripts Mono, física 2D (Rigidbody2D) para o escalador |
| Versões testadas | Aplicativo Steam 2497920, compilação 20993968, SHA-256 do executável `9FDC9F180393A7109BEF27279985A81DBC1E399BFE0B3FE3EEBEB58030ADAB39`, Windows x64 |
| Projetos | ADGAC Co-op 0.1.0 (plugin BepInEx, código-fonte ainda não publicado) |
| Nível de QA | none (somente teste básico manual com dois clientes; consulte QA) |
| Última atualização | 2026-10-25 |

## <a id="where-things-stand"></a>Situação atual

Não existia projeto cooperativo neste repositório nem nas buscas abaixo. Um plugin BepInEx agora oferece "cooperação com fantasmas": cada jogador escala com seu próprio escalador físico e vê os outros como cópias coloridas e identificadas por nome, com uma corda opcional que aproxima os jogadores. O código de salas Steam está escrito e uma sala foi criada por uma cópia do jogo; as mensagens entre duas contas Steam reais estão **não verificadas**.

## <a id="existing-work"></a>Trabalhos existentes

- Este repositório (`DIRECTORY.md`, `games/`): nada, em 2026-10-24.
- Pesquisa de repositórios GitHub por "A Difficult Game About Climbing", com 10 dos 13 resultados lidos: somente mods BepInEx para um jogador (modo gigante, gerenciador de mods, indicadores de mãos, troca de sons, importador VRM, skins). Nenhum é multiplayer.
- Busca na web, com duas formulações: nenhum mod cooperativo ou multiplayer encontrado.
- Não consultados: Steam Workshop/comunidade, Nexus, Thunderstore, Reddit, Discord, página 2 dos resultados do GitHub.
- Um repositório GitHub oferece o jogo "grátis" em um arquivo protegido por senha. Não o baixe.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- `Assembly-CSharp.dll` é pequena (cerca de 270 classes) e é descompilada corretamente com ILSpy 9.1.
- O jogador é um único prefab, `ClimberMain`, criado por `PlayerSpawn` e referenciado por `StaticGameReference.climberMain`. Reaparecimento e teletransporte passam por `PlayerSpawn.Respawn(Vector2)`.
- Corpos físicos (10 Rigidbody2D): torso (`Body`), duas raízes dos braços, duas mãos, dois cursores, conexão das pernas e duas pernas. As mãos agarram usando FixedJoint2D/FrictionJoint2D. O torso fica pendurado nas mãos.
- O esqueleto visível (51 transformações sob `HeroCharacter`) recebe poses por um Animator com pesos de camada e IK (`IKControl.OnAnimatorIK`, `AnimControl`). Não é um ragdoll físico. A IK também desloca os ossos do antebraço e da mão em `LateUpdate`.
- Salvamentos: `Application.persistentDataPath` (`data.pain`, `data1/2.pain`, arquivo de slot), além de PlayerPrefs. O jogo salva a cada 20 s e ao entrar na água pela primeira vez. **Editar `<game>_Data/app.info` em uma cópia do jogo só muda o arquivo de log, não os salvamentos**: as primeiras execuções de teste sobrescreveram assim os salvamentos reais (restaurados a partir de backup feito antes). Isolamento que funciona: um postfix Harmony em `Application.get_persistentDataPath` (verificado calculando hashes da pasta real de salvamentos antes e depois de uma execução com duas instâncias). Sempre faça backup dos salvamentos antes de iniciar qualquer cópia pela primeira vez.
- O jogo já carrega Steamworks.NET (`SteamManager`) com seu AppID real; salas e `SteamNetworkingMessages` podem ser usados diretamente, sem DLLs adicionais.
- Cenas: 0 inicialização, 1 primeira fase, 2 novo jogo+.

## <a id="what-we-changed"></a>O que alteramos

Novo plugin, sem modificar arquivos do jogo:

- Sincronização de pose, cerca de 30 Hz e 570 bytes: posição e ângulo no mundo dos 10 corpos, rotação local dos 51 ossos (quaternion com os três menores componentes) e posição local dos 4 ossos deslocados pela IK.
- Fantasma = clone do escalador local construído sob um pai inativo (para não executar Awake/Start do jogo); depois são removidos todos os MonoBehaviours, Animator, juntas, colisores, rigidbodies e áudio, e os ossos passam a ser controlados pela rede.
- Corda: cada cliente acrescenta uma força de mola em direção ao fantasma do outro jogador além de um comprimento de folga, junto com um renderizador de linha.
- Transporte: sala Steam restrita a amigos mais SteamNetworkingMessages (canal 7); UDP em localhost para testes em um PC.
- `Application.runInBackground = true`; sem isso, uma segunda janela para de simular ao perder o foco.

## <a id="qa"></a>QA

- Sem suíte automatizada. Execute `run-test.ps1` (inicia duas cópias com pastas de salvamento separadas, ligadas por UDP 7001/7002, com fantasmas ao lado do escalador local usando `--coop-ghost-near`).
- 2026-10-25: dois clientes reais do jogo, enlace UDP, cada um exibindo o outro como fantasma com nome e pose própria dos braços; linha da corda renderizada; nenhuma exceção do plugin. A única exceção em `Player.log` vem de `LocalizationScript.SelectLanguage` do próprio jogo.
- Uma sala Steam foi criada por uma cópia do jogo (`--coop-host`). Ainda não houve sessão Steam com uma segunda conta.

## <a id="how-to-play"></a>Como jogar

Consulte o `README.md` do plugin: execute `install.ps1` uma vez (cria uma cópia separada com salvamentos próprios e instala BepInEx 5.4.23.5 verificado por SHA-256), inicie `Play Co-op.bat` e use F8 para hospedar ou entrar.

## <a id="known-issues"></a>Problemas conhecidos

- Objetos do mundo (balões, pêndulos, peças que caem, água) são simulados localmente, então diferem entre jogadores.
- Os jogadores não colidem entre si e não há progresso ou pontos de controle compartilhados.
- A corda usa forças calculadas a partir de posições atrasadas dos fantasmas, ficando elástica com ping alto. Ainda sem ajuste.
- Somente esta compilação do jogo foi verificada.

## <a id="next-steps"></a>Próximos passos

1. Testar com duas contas Steam (entrada pela lista de amigos e pelo ID da sala).
2. Testar o ajuste da corda em escaladas reais; considerar pontos de controle compartilhados ou reinicialização conjunta dos jogadores.
3. Sincronizar a partir do host os objetos móveis do mundo (balões, pêndulos, peças que caem).
4. Teste automatizado: um bot que controle `ArmScript_v2` e verifique se ambos os clientes concordam sobre as posições dos fantasmas.
5. Publicar o código-fonte do plugin em repositório próprio e adicionar a entrada no diretório.
