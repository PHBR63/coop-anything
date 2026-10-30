# <a id="core-identity-engine-and-early-findings"></a>Núcleo: identidade, motor e primeiras descobertas

> Parte das notas de trabalho de Deep Rock Galactic: Survivor. Extraída literalmente de `NOTES.md` em 2026-10-20 (linhas 1-261); conteúdo inalterado.
> Estado atual e Ist/Soll: [../STATUS.md](../STATUS.md). Índice: [../NOTES.md](../NOTES.md).

# <a id="deep-rock-galactic-survivor--working-notes"></a>Deep Rock Galactic: Survivor - notas de trabalho

Slug: `deep-rock-galactic-survivor`
Objetivo: modo cooperativo on-line (2 ou mais jogadores) para um jogo distribuído apenas para um jogador.

> Estado privado específico da máquina (caminhos reais de instalação, logs, dumps, salvamentos) fica em `local/`, ignorado pelo Git. Este arquivo deve ser seguro para publicação.

## <a id="identity"></a>Identidade

- **Jogo:** Deep Rock Galactic: Survivor. Desenvolvedora **Funday Games**, distribuidora Ghost Ship Publishing. Exclusivo Steam, Windows x64.
- **Loja / appid:** Steam `2321470` (depósito `2321471`).
- **Motor:** Unity, **IL2CPP x64**. `GameAssembly.dll` + `DRG Survivor_Data/il2cpp_data/ Metadata/global-metadata.dat` (metadados IL2CPP **v39**).
- **Compilação testada (atual):** Steam buildid `23854500`, **Unity 6000.4.7f1** (`UnityPlayer.dll` FileVersion `6000.4.7.15975364`), `build-guid=86f484871c2549f690a3fdbf26aebc8c`.
  - `DRG Survivor.exe` SHA-256 `5abca214deecb763d0cec4d6194c519ac9bd215052987a601c96e75d67e8679a`
  - `GameAssembly.dll` SHA-256 `250bbb4bb0491dee3c9d7f312276d9ecfce04cd98fda14cca1ab67cb289829ba`
  - `global-metadata.dat` SHA-256 `49202e38cb7e400c6895ce6188d81bbf2676af29a90e71493bd03513178a10d8`
- **Compilação anterior (substituída):** Steam buildid `20237659`, Unity 2022.3.59 IL2CPP, `build-guid=43d5554851e8403c9db7df2bc6cc9e34`.
  - `DRG Survivor.exe` SHA-256 `b788e1755d229679140a62e14c8bc175391c064cabce60ef217aac468b47a1db`
  - `GameAssembly.dll` SHA-256 `fcbac8f75fb8e508136b240e2eac2db5fff5d9271eac43df400996672dee06a3`
- **Strings do aplicativo:** `app.info` = `Funday Games` / `DRG Survivor`.

## <a id="modding-stack-verified-on-build-23854500"></a>Ferramentas de modificação (verificadas na compilação 23854500)

- **BepInEx 6 IL2CPP**, versão de desenvolvimento `6.0.0-be.789+6cea286`, carrega e executa (`Chainloader startup complete`) **somente após uma solução alternativa**, abaixo. Usa o runtime .NET 6 incluído e gera `BepInEx/interop/*.dll` (132 assemblies nesta compilação, incluindo `Assembly-CSharp.dll` e `UnityEngine.CoreModule.dll`) por Cpp2IL.
- **Solução para Unity 6 / metadados v39 (reproduzida e corrigida):** a configuração padrão restaura trechos removidos do IL usando bibliotecas-base Unity; neste jogo, isso gera interoperabilidade inválida e o chainloader encerra com `FileNotFoundException: Could not load ... 'UnityEngine.CoreModule'`. Correção:
  1. Em `BepInEx/config/BepInEx.cfg`, deixe o valor vazio: `UnityBaseLibrariesSource =` (mantenha a chave, remova a URL).
  2. Exclua `BepInEx/interop` e `BepInEx/unity-libs`.
  3. Reinicie; a interoperabilidade é regenerada sem restauração de código removido (`Not performing unstripping as unity libs are not specified`) e o chainloader conclui. Custo: ausência das bibliotecas-base Unity restauradas. Relatado ao upstream em [BepInEx#1350](https://github.com/BepInEx/BepInEx/issues/1350).
- **Nota sobre ferramentas de terceiros:** `Il2CppDumper` v6.7.46 **não lê** metadados v39 ("ERROR: Metadata file supplied is not a supported version[39]"); use Cpp2IL (incluído no BepInEx) ou sua saída de interoperabilidade.
- **Assemblies do próprio jogo** (da interoperabilidade): `Assembly-CSharp.dll` (código principal), `FundayFactory.UI.dll`, `FundayGames.Audio`, `FundayGames.Attributes`, `FundayGames.LocalPrefs`, `FundayGames.PlatformService` (+`.Steam`).
- **Bibliotecas relevantes:** **Zenject** (injeção de dependências; código conectado por instaladores/singletons, não globais `MonoBehaviour`), **KDTree** (consultas espaciais; provável busca de inimigos/alvos, relevante para gerenciamento de interesse), **UniTask** (assíncrono), PrimTween/DOTween (interpolações), Cinemachine (câmera), Steamworks.NET.
- **Namespace:** o código fica sob `DRS.*` (por exemplo, `DRS.UI`).

## <a id="observations-facts-from-a-source"></a>Observações (fatos de uma fonte)

- O jogo é **somente para um jogador**. Os desenvolvedores responderam no Discord oficial em fevereiro de 2024: o foco é a experiência individual; modo cooperativo não está em desenvolvimento e talvez nunca aconteça. Relatado por gamepressure.
- **A modificação é estabelecida e aberta:** BepInEx **6** (Unity IL2CPP, versão de desenvolvimento) é o carregador comunitário; existe comunidade Thunderstore `deep-rock-galactic-survivor` com `BepInExPack_IL2CPP` pré-configurado, e o Nexus lista um pacote BepInEx e cerca de 15 mods.
- **Código de referência comprova o padrão de hooks** (mods de BlueRaja, MIT): `BasePlugin` BepInEx com `Harmony.CreateAndPatchAll`, aplicando patches aos tipos IL2CPP do jogo. Expõe namespace **`DRS.*`** (por exemplo, `DRS.UI`), tipos `RarityWeight`, `PickupSpawner`, `Economy`, enum `ECurrency` (GOLD, NITRA, RED_SUGAR, BISMOR, ...). Assembly de interoperabilidade referenciado: `BepInEx/interop/Assembly-CSharp.dll`.
- **Steamworks.NET** acompanha a compilação (`Plugins/x86_64/steam_api64.dll`), permitindo depois retransmissão Steam (Spacewar AppID 480) para hospedar/entrar sem redirecionar portas.

## <a id="derived-my-reasoning-not-yet-verified-in-game"></a>Deduções (raciocínio próprio, ainda não verificado no jogo)

- **Caminho 2 - criar do zero.** Não há cooperativo para retomar. Unity IL2CPP + BepInEx é o alvo moderno mais simples segundo a tabela de motores dos guias.
- **Modelos reutilizáveis (mesmo motor):** Nitrox (Subnautica: BepInEx + Harmony + LiteNetLib, autoridade do servidor), HKMP (Hollow Knight), Quantum Space Buddies (Outer Wilds), CelesteNet (Celeste). Nitrox é o mais semelhante estruturalmente.
- **Modelo de sincronização:** estado com autoridade do host (não é possível tornar um binário fechado determinístico, descartando lockstep).
- **Superfície a mapear:** anão(s), enxame e projéteis, dano e mortes, orbes XP, materiais coletáveis, relógio/objetivos, fases de chefes e dois fluxos exclusivos de um jogador sem equivalente cooperativo: **escolha de carta ao subir de nível** (o jogo pausa) e **fim da missão / extração**.

## <a id="guesses-believed-but-untested"></a>Hipóteses (consideradas prováveis, mas não testadas)

- Representantes dos anões usando modelos do próprio jogo são viáveis; sincronizar centenas de inimigos do enxame é a parte difícil (largura de banda e autoridade, não visibilidade).
- A pausa de subida de nível precisa de política (congelar ambos ou decidir por quem escolhe primeiro).

## <a id="unknowns"></a>Desconhecidos

- Duas instâncias podem rodar em um PC? (mutex de instância única / verificação de janela ainda não testados.)
- Modelo de entidades, comportamento de atualização/passo fixo e criação/agrupamento de inimigos, ainda não extraídos.
- Formato do estado de salvamento/partida e local da progressão entre partidas.
- Diferenças de versão: relatos comunitários mostram uma versão posterior em **Unity 6** (`1.1.73p`, Unity `6000.4.7f1`). O código cooperativo precisa fixar uma compilação; as assinaturas serão diferentes.

## <a id="sources"></a>Fontes

- https://www.gamepressure.com/newsroom/deep-rock-galactic-survivor-drg-coop-and-multiplayer-explained/za6929
- https://steamcommunity.com/app/2321470/discussions/0/4371376043390476657/
- https://github.com/BlueRaja/Deep-Rock-Galactic-Survivor-Mods
- https://www.nexusmods.com/games/deeprockgalacticsurvivor
- https://thunderstore.io/c/deep-rock-galactic-survivor/p/BepInEx/BepInExPack_IL2CPP/
- https://github.com/BepInEx/BepInEx/issues/1350

## <a id="how-the-game-works-from-the-interop-dump-build-23854500"></a>Como o jogo funciona (dump de interoperabilidade, compilação 23854500)

- **Nenhum código de rede.** Busca em toda a árvore por Photon/Mirror/Netcode/NetworkManager/sockets/`TcpClient`/`UdpClient` não encontrou **nada**. A camada precisa ser escrita do zero; não há multiplayer do motor para aproveitar.
- **`Entity` (`Entity : MonoBehaviour`) é a âncora de sincronização.** Campos: `currentHp` (long), `IsPlayer` (bool), `pierceStopValue`; `position` (Vector3); `isAlive`. Métodos: `TakeDamage(long dmg, bool isCrit, EDamageType, bool doFx, EDamageSource, Entity source, bool ignoreReduction)`, `Heal(long, EHealType)`, `Die(EDamageType, long overkill, bool)`, `ApplyStatusEffect(s)`, `OnGamePaused`/`OnGameUnpaused`. Tanto `Player : Entity` quanto `Enemy : Entity`.
- **`Player`** acrescenta `EMoveControlType { DISABLED, FORCED, FULL_CONTROL }` e um `PlayerControlled : MonoBehaviour` associado que gerencia movimento/animação (`_moveSpeed`, `_origTarget`, Idle/Forward/Backward/Left/Right). A subclasse **`DummyPlayer : Player`** já existe: base pronta para representante.
- **Inimigos usam conjuntos reutilizáveis:** `EnemySpawner.poolDictionary` -> `ObjectPool<Enemy>` por tipo `EEnemy`; `Enemy.OnSpawn(...)`, `Enemy.ownerPool`. A reutilização torna os IDs de instância instáveis; a camada precisa de **IDs de rede próprios**.
- **IA centralizada em `AI_Manager`** (singleton `_instance`, `_units`, `Add`/`Remove`/`Update`), ponto de controle da autoridade: executar no host e suprimir nos clientes.
- **Injeção Zenject:** gerenciadores conectados por `Inject(...)` (por exemplo, `LevelUpManager`, `RunStateManager`, `SaveDataManager`). Assim o mod obtém referências ativas.
- **Subida de nível:** `LevelUpManager` (`flowActive`, `StartFlow`, `HandleLevelUps`, `OnPrePlayerLevelGain`/`OnPlayerLevelGain`). Fluxo de pausar e escolher carta que não tem equivalente no modo de um jogador e precisa de uma política cooperativa.
- **Partida/etapas:** `RunStateManager` (índice, objetivos principais/secundários, `SaveToMidRunData`). **Salvamento:** `DRS.SaveSystem` (`SaveDataManager`, `PCSaveFileManager`, `PCMidRunSaveManager`, `MidRunSaveBuilder`, `MidRunSaveData`), com variantes PC e GDK.
- **Atenção:** `Assets.Scripts.PhysicsOptimisation` usa Unity Jobs/**Burst** (`lib_burst_generated.dll`), e o jogo inclui **KDTree** + `TextmeshDOTS`; busca/movimento de inimigos pode ser parcialmente compilado com Burst, mais difícil de interceptar que código gerenciado.

### <a id="co-op-implications-design-sketch--phase-4"></a>Implicações cooperativas (esboço de projeto - etapa 4)

- **Comportamentos obrigatórios (decisões de projeto):**
  - **Ambos ganham experiência juntos:** XP/progressão compartilhada, não individual.
  - **Escolhas de subida de nível sincronizadas:** quando aparece seleção de recompensa/melhoria, o jogo deve pausar nos **dois** clientes até **ambos** escolherem. (Hoje `LevelUpManager` pausa só a instância local.)
- Modelo: **sincronização de estado com autoridade do host** (um binário fechado não pode ser tornado determinístico bit a bit).
- **Geração da fase precisa ser idêntica:** veja o marco de transporte abaixo; o jogo não tem semente de partida, então o mod fixa `UnityEngine.Random` em um valor compartilhado antes de `MapGenerator.CreateMap`. Verificado: impressões digitais idênticas nos mapas das duas instâncias.
- Representantes: clonar o prefab de jogador / `DummyPlayer` do jogo; controlar transformação + animação pela rede; desativar entrada e IA.
- Combate: replicar resultados de `Entity.TakeDamage`/`Die`/`Heal` do host; convidados aplicam com proteção contra reentrada, para que um acerto aplicado não seja retransmitido.
- Inimigos: host executa `AI_Manager`; convidados espelham posição/vida. Ordem dos marcos: jogadores visíveis -> combate compartilhado -> enxame sincronizado -> objetivos.
- Subida de nível: congelar ambos no fluxo de cartas ou decidir por quem escolhe primeiro.

## <a id="build-log"></a>Registro de compilação

- **Plugin de sondagem v0.0.2 compila e carrega** (plugin `BepInEx` IL2CPP, `net6.0`, Harmony). Receita: referenciar `BepInEx/core/{BepInEx.Core,BepInEx.Unity.IL2CPP,0Harmony, Il2CppInterop.Runtime}.dll` e os assemblies necessários de interoperabilidade (`Assembly-CSharp`, `UnityEngine`, `UnityEngine.CoreModule`, `Il2Cppmscorlib`, `Il2CppSystem`, `Il2CppSystem.Core`), todos com `Private=false`. Nota: curinga de `<Reference>` agrupado por `%(Item.Filename)` na pasta de interoperabilidade **não** resolve; liste explicitamente os assemblies.
- Resultado ao vivo: `Loading [DRG Survivor co-op probe 0.0.2]` -> `probe: Load() called` -> `probe: Harmony patches applied` -> `Chainloader startup complete`. Código gerenciado próprio executa dentro do jogo.
- Hooks: `GameController.StartGame` / `OnCoreRunStarted` (captura `player` da partida), `Player.Awake`, `AI_Manager.Update` (amostra a cada 120 quadros) e `Entity.TakeDamage`. Grava `probe.log` ao lado do executável e o log BepInEx. Sinais: posição, `CurrentHP`, `isAlive`, contagem de `AI_Manager._units` (pico) e eventos de dano do jogador.
- `GameController.stageIndex` **não** é exposto à interoperabilidade (sem propriedade gerada), então a indicação de etapa foi removida da sondagem.

## <a id="next-steps"></a>Próximos passos

- Criar o controlador do representante: instanciar o prefab do próprio jogo e movê-lo pelas posições recebidas (já transportadas pela rede); iniciar a camada de combate/inimigos com autoridade do host dimensionada ao enxame medido.

## <a id="transport-milestone-two-instances-verified"></a>Marco de transporte (duas instâncias, verificado)

- **Duas instâncias rodam lado a lado em um PC**, sem mutex de instância única. Ambas permaneceram ativas (cerca de 1,34 GB cada), em janela 1280x720/900x600.
- **Transporte funciona:** plugin BepInEx + **LiteNetLib 2.1.4** (compilação `lib/netstandard2.1`; a `net8.0` não carrega no runtime .NET 6 do BepInEx). Host escuta UDP 9050, cliente conecta por loopback; papel escolhido por `-coophost` / `-coopclient` (mais `-coopaddr=`, `-coopport=`, `-cooplatency=`). Simulação de latência já preparada para testes posteriores de perda/latência.
- **Troca bidirecional sustentada de estado de jogador** durante cerca de 70 s no menu: host `sent=1427 recv=1376`, cliente `sent=1359 recv=1409` (a cada 3º quadro, cerca de 20 Hz, canal não confiável). Evidências: `local/dumps/twoclient-host.log`, `twoclient-client.log`. (Posições `(0,0,0)` porque ambas estavam no menu; movimento real exige ambas em uma partida.)
- Cada instância grava seu próprio `coop-<role>.log`, pois **`LogOutput.log` do BepInEx é compartilhado por ambas** na mesma pasta e sobrescrito.

### <a id="environment-gotchas-found-needed-for-any-two-instance-work"></a>Armadilhas de ambiente encontradas (relevantes para qualquer trabalho com duas instâncias)

- **Perfil/salvamentos são por usuário, não por instalação:** `%USERPROFILE%\AppData\LocalLow\Funday Games\DRG Survivor\` (sincronizado com Steam Cloud). Duas instâncias e qualquer cópia de teste leem e escrevem os salvamentos do jogador (`drg_save_slotN_*.dat`, `drg_current_run_slotN.dat`, `localprefs.dat`). Regra: backup da pasta antes e restauração depois; solução adequada (redirecionamento por instância) ainda necessária antes de partidas cooperativas reais. Backup em `local/backup/localLow-DRGS-*`.
- Uma segunda instância às vezes abre, mas fica parada (sem `Update`); é obrigatório verificar que ambas atualizam antes de confiar no resultado.

## <a id="design-decisions-design-decisions"></a>Decisões de projeto (decisões de projeto)

Requisitos definidos pelo autor (não deduzidos do jogo).

- **Número de jogadores: 2.** Não projete para 4.
- **Melhorias individuais:** ambos sobem de nível juntos, mas cada um escolhe sua carta. (Exceção para algumas melhorias compartilhadas pode ser discutida depois, não agora.)
- **Dificuldade inalterada** por enquanto, sem ajuste para o segundo anão.
- **Objetivos e saques totalmente compartilhados**, com exceção importante: **itens deixados são consumidos**. Se um anão coleta uma orbe XP ou qualquer item, deve desaparecer para o outro. Coletas precisam de responsabilidade e sincronização de remoção, não só de posição.
- **Objetivos são a parte difícil.** Exemplos:
  - Objetivos de permanecer alguns segundos em um círculo devem **progredir mais rápido com ambos dentro dele**.
  - **A broca** (surge após tempo definido para avançar de etapa) exige **presença dos dois anões**.
  - Novas telas de recompensa/objetivo ainda não foram testadas.
- **Morte e incapacitação:**
  - **Indicador fora da tela:** ícone flutuante que mostra sempre onde está o outro anão fora da câmera local.
  - **Reanimação:** sobrevivente permanece no círculo ao redor do anão morto por cerca de **5 segundos** para reanimá-lo.
- **Metaprogressão usa o perfil do HOST para ambos** (decisão que substitui o perfil real compartilhado anterior). Desbloqueios vêm só do host: se ele tem Driller, o parceiro pode usá-lo; caso contrário, não. Progresso dos **dois** personagens é creditado ao host; Scout no host e Driller no parceiro avançam ambos no salvamento do host. O salvamento próprio do parceiro não é lido nem escrito para a partida. Como os resultados do cliente chegam ao caminho de salvamento do host é **desconhecido** e precisa ser medido antes de implementar.
- **Economia da equipe:** Ouro e Nitra em reserva única; gastos (loja, novas escolhas, novas escolhas de artefatos) arbitrados pelo host. **Bosco:** um por jogador, host simula ambos. **Supply Pod:** uma cápsula global, cada jogador escolhe seu artefato. **Modelo de dano:** armas do cliente rodam localmente; ele relata acertos e o host aplica (exposição a trapaça aceita para 2 amigos).
- **Host escolhe a missão**, e cliente deve **entrar na mesma**, com mesma broca e estado de fase. É a adoção de configurações, que deve ser totalmente automática, não ajustada à mão.
- **Escopo atual: só missões principais** (Elimination, Escort Duty). Outros tipos não precisam funcionar ainda, e **Egg Hunt está expressamente fora do escopo** (exige DLC Heavy Duty).
- **Entrada pretendida (mais adiante):** host escolhe missão, parceiro **entra pelo Steam**, pressiona **Ready**, e só então o host pode começar. Prontidão é barreira real, não botão cosmético.

  Isso corresponde às descobertas da automação: neste perfil, o **único tipo desbloqueado é a campanha Mission Road** (`UIChallengeSetButton_MissionRoad`), com Mastery, Endless, Anomaly e as duas partidas fixas como `[unavailable]`. Missões principais são, portanto, o escopo desejado e o único acessível.
