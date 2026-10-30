# <a id="a-difficult-game-about-climbing-notes"></a>A Difficult Game About Climbing: notas

Notas brutas de trabalho, de 2026-10-24 a 2026-10-25. Os caminhos usam `<game dir>`. Relato técnico final: [README.md](README.md).

## <a id="identity-observed"></a>Identidade (observada)

- Aplicativo Steam 2497920, identificador da compilação 20993968, Windows x64.
- `<game dir>/A Difficult Game About Climbing.exe`, SHA-256 `9FDC9F180393A7109BEF27279985A81DBC1E399BFE0B3FE3EEBEB58030ADAB39`, versão do arquivo 2021.3.21.1774945.
- Unity 2021.3.21, Mono (`<game>_Data/Managed/Assembly-CSharp.dll` presente, sem `GameAssembly.dll`).
- Steamworks.NET distribuído em `Managed/com.rlabrecque.steamworks.net.dll`; `SteamManager` inicializa com o identificador real do aplicativo.

## <a id="observations"></a>Observações

- `Assembly-CSharp.dll` descompilado com ilspycmd 9.1.0.7988: 271 classes, principalmente scripts do jogo.
- O clone do prefab do jogador se chama `Climber5(Clone)`; 10 Rigidbody2D, 51 transformações do esqueleto sob `HeroCharacter`.
- Braços: `ArmScript_v2` (mãos controladas por mouse/analógico, agarramento com FixedJoint2D/FrictionJoint2D). Pose: `IKControl.OnAnimatorIK` + pesos das camadas de `AnimControl`; `IKControl.LateUpdate` desloca os ossos dos antebraços e das mãos.
- `SaveSystemJ` escreve em `Application.persistentDataPath` a cada 20 s (alternando data.pain / data1 / data2, current.slot) e na primeira entrada na água (datacp.pain).
- BepInEx 5.4.23.5 (SHA-256 `82f9878551030f54657792c0740d9d51a09500eeae1fba21106b0c441e6732c4`) carrega na cópia por winhttp.dll doorstop; o plugin carrega, encontra o escalador e cria representações fantasma.
- Dois clientes em um PC com uma conta Steam iniciam normalmente (conexão UDP usada nos testes). O Unity para de simular uma janela sem foco, a menos que `Application.runInBackground = true`.
- A única exceção vista em `Player.log` é a NullReferenceException de `LocalizationScript.SelectLanguage` do próprio jogo.
- Uma sala Steam exclusiva para amigos foi criada a partir de uma cópia do jogo com `--coop-host`.

## <a id="mistake-worth-recording"></a>Erro que merece registro

As primeiras execuções de teste gravaram na pasta real de salvamento. Editar `<game>_Data/app.info` (nome da empresa/produto) mudou apenas `Player.log`; `persistentDataPath` continuou em `LocalLow/Pontypants/...`. Os arquivos tinham backup prévio e foram restaurados (hashes idênticos); o isolamento foi feito com um postfix Harmony em `Application.get_persistentDataPath`, verificado pelo hash da pasta real antes e depois de uma execução com duas instâncias. Sugestão para os guias: fazer backup dos salvamentos antes da primeira execução de qualquer cópia e verificar o isolamento por hash antes de confiar nele (consulte `playbook/methods.md`).

## <a id="derived"></a>Deduções

- O modo cooperativo com representações fantasma basta para ver amigos escalando; o escalador físico é local, sem latência de entrada.
- Uma corda pode ser aproximada por uma força de mola em direção ao torso do outro fantasma (cada lado aplica sua própria metade).

## <a id="guesses"></a>Hipóteses

- A corda parecerá elástica acima de aproximadamente 100 ms de ping.
- A sincronização de objetos móveis com autoridade do host (balões, pêndulos, peças que caem) será necessária para quebra-cabeças que dependem de tempo preciso.

## <a id="unknown"></a>Desconhecidos

- Caminho Steam com duas contas: entrada na sala, aceitação de sessão `SteamNetworkingMessages`, convite pela sobreposição a partir de cópia iniciada fora do Steam.
- Comportamento em compilações diferentes de 20993968.
- Se o Steam Cloud enviou os salvamentos temporariamente alterados antes da restauração (o Steam estava em execução; o identificador real do aplicativo estava sendo usado).
- Trabalhos cooperativos existentes no Steam Workshop, Nexus, Thunderstore, Reddit, Discord (não pesquisados).

## <a id="sources"></a>Fontes

- https://store.steampowered.com/app/2497920/
- Resultados de busca no GitHub que listam mods BepInEx para um jogador, por exemplo https://github.com/ITR13/A-Difficult-Game-About-Climbing-Mods
- https://github.com/BepInEx/BepInEx/releases/tag/v5.4.23.5
