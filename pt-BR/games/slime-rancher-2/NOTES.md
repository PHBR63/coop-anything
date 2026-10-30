# <a id="slime-rancher-2-notes"></a>Notas de Slime Rancher 2

## <a id="identity-tested-build"></a>Identidade (compilação testada)
- Steam, buildid 24131940, versão 1.3.0, Unity 6000.0.73f1 IL2CPP, Windows 11
- SHA-256 SlimeRancher2.exe: fb186f4b9d02a47817a0c1d8e7581d7b9a6b77d65e034355f39dae138e61fc28
- SHA-256 GameAssembly.dll: 786006ede0d198f6e15a2c01f90ef9108afe694745fa0ad894e1c3ed342385b7

## <a id="triage-2026-10-23"></a>Triagem 2026-10-23
### <a id="observations-sourced"></a>Observações (com fontes)
- Nenhuma entrada em DIRECTORY.md / data/directory.yaml / games/ para Slime Rancher 1 ou 2; nenhuma issue do projeto encontrada pela API de busca do GitHub.
- **Ranching Together (SR2MP)**, https://github.com/pyeight/SlimeRancher2Multiplayer, GPL-3.0, ativo (último push 2026-09-26), versão mais recente Beta_0.3.9 (2026-09-24), arquivo SR2MP.dll com sha256 9cf2823c635e0d4e515828b14a50e8b42442f45bfb31e175f6a80984f437ea28 (digest do GitHub). 3 issues abertas (cosméticas).
  - `SR2MP/BuildInfoConstants.cs`: MinimumGameVersion = ExactGameVersion = "1.3.0"; corresponde a esta instalação.
  - `SR2MP/AssemblyInfo.cs`: VerifyLoaderVersion(0,7,3); MelonLoader 0.7.3. README: Starlight 4.0.3 necessário.
  - Rede: UDP direto, porta padrão 1919. Código de entrada = IP:porta codificado (`Shared/Utils/JoinCode.cs`). Hospedagem automática por UPnP via Open.NAT (`Shared/Utils/AutoHost.cs`). Sem retransmissão pelo Steam.
  - Tabela de recursos no README: maioria dos sistemas sincronizados; parcialmente: Gray Labyrinth, Sanctuary e alguns comportamentos dos slimes; não sincronizado: inventário do jogador. Entrar SOBRESCREVE o salvamento do cliente; use uma vaga de salvamento vazia.
- Antigos/inativos: SR2MP de Saty (itch.io, descontinuado, somente SR2 0.4.0); Egor935/SR2MP (última versão v0.1.7, versões antigas do jogo). NewSR2MP de PinkTarrLargo (Nexus 90), estado desconhecido; Ranching Together parece seu sucessor (mesmo convite Discord a7wfBw5feU), dedução não verificada.

### <a id="derived"></a>Deduções
- Caminho 1 (mod funcional existente). Não é necessário criar modo cooperativo; a tarefa é instalar, verificar e talvez melhorar com retransmissão Steam/sem redirecionar portas.

### <a id="unknown"></a>Desconhecidos
- Se o roteador do host aceita UPnP.

## <a id="workspace--qa-2026-10-23"></a>Ambiente de trabalho + QA 2026-10-23
### <a id="observations"></a>Observações
- Log do MelonLoader: `Game Version: 1.3.0 [20260704030000-113492]`, Unity 6000.0.73f1. ZIP ML 0.7.3 x64 (sha256 5b2b2f3d.a416) instalado manualmente; gera assemblies de interoperabilidade na primeira execução (~30 s).
- SR2MP.dll 0.3.9 contém a string "4.0.4" (MinimumStarlightVersion = Starlight.BuildInfo.CodeVersion na compilação). Starlight 4.0.4 (lançado em 2026-09-24, na mesma hora do SR2MP 0.3.9) carrega normalmente. O README ainda informa 4.0.3; está desatualizado. Não foi testado se 4.0.3 é rejeitado.
- Salvamentos: `Application.persistentDataPath` = `%USERPROFILE%\AppData\LocalLow\MonomiPark\SlimeRancher2\Steam\<steamid64>\`, uma pasta Steam Auto-Cloud (`steam_autocloud.vdf`). Uma cópia de teste gravaria nos salvamentos reais e na nuvem. Correção usada: plugin ML exclusivo de testes `CoopQA.SaveIsolation` aplica patch à importação `SHGetKnownFolderPath` de UnityPlayer.dll e GameAssembly.dll (ambas a importam) e responde a FOLDERID_LocalAppDataLow com `<instance>\LocalLow`. Executa em OnPreInitialization; cedo o suficiente (Unity resolveu LocalLow uma vez, após o patch: `redirected=1`). Player.log redirecionado por `-logFile`. Pasta real de salvamento e instalação verificadas por hash antes/depois de cada execução: inalteradas.
- `steam_appid.txt` (1657630) na cópia basta: sem reiniciar pelo Steam, SteamAPI funciona e uma segunda cópia inicia (sem verificação de instância única). Menu principal ~11 s; RAM ~2,4 GB no menu, ~3,3 GB no mundo por cópia.
- O jogo tem a classe de opções CLI `Il2CppMonomiPark.SlimeRancher.CliOptions` (`SaveFileToLoad`, `QATestFilter`, `ProfileScenario*`). Definir `CliOptions.SaveFileToLoad = <full path to .sav>` (postfix em `CliOptions.Initialize`) faz o jogo carregar esse salvamento ao iniciar, pulando o menu. Usado pelo bot de teste.
- Identificador de jogador SR2MP = SHA-256(MachineName + UserName)[..9] (`Shared/Utils/PlayerIdGenerator.cs`): duas cópias em um PC recebem o mesmo identificador. O bot define `PlayerIdGenerator.cachedPlayerId` por cópia (somente teste).
- O cliente SR2MP recusa 127.0.0.1 sem DevMode (`Client/Client.cs:117`); os testes usam o IP da LAN.
- **Bug no projeto original (não afeta jogadores):** `Server.Start(port, enableIPv6: false)` cria socket IPv4, mas `Server/Managers/NetworkManager.cs:76` sempre usa EndPoint IPv6Any em `ReceiveFrom`, causando ArgumentException em ciclo contínuo sem espera progressiva (6,1 milhões de registros, Latest.log de 4,4 GB em 6 min). Todos os chamadores internos do mod passam `true` (`Commands.cs:26`, `MultiplayerUI.Action.cs:14`). Encontrado porque a primeira versão do bot passava `false`.
- **Bug no projeto original (afeta jogadores, impacto desconhecido):** ao entrar, o cliente registrou uma vez `Packet handler for InitialLandPlotsPacket threw: IndexOutOfRangeException at AmmoModel.Reset ← SiloStorage.SetModel
  ← InitialLandPlotsHandler.Handle (InitialLandPlots.cs:127)`. O salvamento do host tinha silos; o do cliente era do início do jogo. Se lotes posteriores daquele pacote foram ignorados: desconhecido (não verificado).

### <a id="qa-run-2026-10-23-localqarun_coop_testpy-two-real-clients-on-one-pc-lan-ip"></a>Execução de QA 2026-10-23 (local/qa/run_coop_test.py, dois clientes reais em um PC, IP da LAN)
- Execução 1: FAIL 8/14 (bug do bot acima: o servidor nunca respondeu); demonstra que as verificações de conexão/sincronização conseguem falhar.
- Execução 2: **PASS 16/16**: ambas as cópias iniciam e carregam seus salvamentos via CliOptions; salvamentos diferentes antes da conexão (3183 contra 250 newbucks); servidor em execução; cliente conectado; host conta 1 cliente; cada lado vê o outro jogador; dinheiro do cliente igual ao do host após entrar (3183); host +777 leva cliente a 3960; cliente +111 leva host a 4071; posições remotas a até 2 m (d=0.00, jogadores parados: verificação fraca); salvamentos reais e instalação inalterados.
- Não testados: internet / NAT / UPnP, movimento, slimes, lotes, dispositivos, salvamento no cliente, mais de 2 jogadores, latência/perda.
