# <a id="slime-rancher-2-2022"></a>Slime Rancher 2 (2022)

| | |
|---|---|
| Motor | Unity 6000.0.73f1, IL2CPP (mods MelonLoader) |
| Versões testadas | Steam, jogo 1.3.0 (`1.3.0 [20260704030000-113492]`), identificador da compilação 24131940, Windows 11 |
| Projetos | [Ranching Together (SR2MP)](https://github.com/pyeight/SlimeRancher2Multiplayer), entrada do diretório "Slime Rancher 2 / Ranching Together" |
| Nível de QA | automated (teste básico + sincronização de dinheiro/jogadores, 2 clientes em um PC; consulte QA) |
| Última atualização | 2026-10-23 |

## <a id="where-things-stand"></a>Situação atual

Sim, já é possível jogar junto. Ranching Together é um mod MelonLoader ativo e de código aberto (GPL-3.0). Segundo sua própria tabela de recursos, quase todos os sistemas são sincronizados; as exceções são o inventário do jogador e partes de Gray Labyrinth e Sanctuary. Na versão 1.3.0, inicia, hospeda e entra em sessões; a sincronização de dinheiro e jogadores passou em teste automatizado com dois clientes reais. O caminho pela internet (redirecionamento de portas, UPnP) não foi testado aqui.

## <a id="existing-work"></a>Trabalhos existentes

| Projeto | Última atividade | Estado | Notas |
|---|---|---|---|
| [Ranching Together / SR2MP de pyeight (Shark)](https://github.com/pyeight/SlimeRancher2Multiplayer), também [Nexus 118](https://www.nexusmods.com/slimerancher2/mods/118) | versão Beta_0.3.9, 2026-09-24; push 2026-09-26 | ativo | Exige exatamente a versão 1.3.0 do jogo (`BuildInfoConstants.cs`), MelonLoader 0.7.3 e Starlight. A lista de colaboradores inclui PinkTarr (autor do antigo NewSR2MP, Nexus 90). |
| [SR2MP de Saty](https://satypardus.itch.io/multiplayer-mod-slime-rancher-2) | atualização 521, 2024-02-10 | descontinuado | Funciona apenas no SR2 0.4.0 segundo sua página itch; o autor o abandonou por causa de IL2CPP. |
| [Egor935/SR2MP](https://github.com/Egor935/SR2MP) | v0.1.6 2025-02-10 (v0.1.7 listada) | desconhecido | Voltado a versões antigas do jogo, segundo as notas de versão. Não testado. |

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- O jogo não tem código de rede. Toda sincronização fica no mod: UDP, autoridade do host, porta padrão 1919, socket IPv6 em modo duplo. O "código de entrada" é o IP e a porta do host codificados (`Shared/Utils/JoinCode.cs`). A hospedagem automática tenta UPnP via Open.NAT (`Shared/Utils/AutoHost.cs`). Não há retransmissão pelo Steam; o host precisa de UPnP, porta UDP redirecionada ou VPN.
- Salvamentos: `Application.persistentDataPath\Steam\<steamid64>\*.sav`, sob `%USERPROFILE%\AppData\LocalLow\MonomiPark\SlimeRancher2`, sincronizados pelo Steam Auto-Cloud. Entrar substitui o salvamento do cliente pelo mundo do host. O mod faz backups em `UserData/SR2MP/SaveBackups/`.
- O jogo inclui opções CLI (`Il2CppMonomiPark.SlimeRancher.CliOptions`: `SaveFileToLoad`, `QATestFilter`, `ProfileScenario*`). Definir `SaveFileToLoad` como caminho completo de um `.sav` faz carregá-lo na inicialização, útil para bots.
- Identificador de jogador SR2MP = SHA-256(nome da máquina + nome de usuário Windows); duas cópias em um PC compartilham identificador. O bot de teste o substitui.
- O cliente SR2MP recusa `127.0.0.1` sem DevMode do mod ativado. Testes em um PC usam o IP da LAN.

## <a id="what-we-changed"></a>O que alteramos

Nada no mod. Ferramentas exclusivas de teste foram acrescentadas em `qa/` (inertes sem seus arquivos de ativação):

- `qa/SaveIsolation`: plugin MelonLoader. Aplica patch à importação `SHGetKnownFolderPath` de `UnityPlayer.dll` e `GameAssembly.dll` para FOLDERID_LocalAppDataLow apontar para `<instance>\LocalLow`. As cópias de teste nunca alteram salvamentos reais ou a pasta Steam Cloud. Funciona em qualquer jogo Unity no Windows que armazene salvamentos em `persistentDataPath`; consulte [multi-instance-testing](../../playbook/multi-instance-testing.md).
- `qa/Bot`: mod MelonLoader. Carrega um salvamento na inicialização por `CliOptions.SaveFileToLoad` e dá a cada cópia seu próprio identificador SR2MP. A cada 0,5 s grava `UserData/CoopQA/state.json` (dinheiro, posição, estado do servidor e cliente, jogadores remotos) e executa comandos numerados de `UserData/CoopQA/cmd.txt` (`host`, `connect`, `addcurrency`, `save`, `quit`).
- `qa/run_coop_test.py`: executor baseado em `tools/gamepool`. Inicia cópias de host e cliente, verifica o estado, exibe `RESULT: PASS/FAIL` e calcula hashes da instalação real e pasta de salvamentos antes e depois.

Bugs encontrados no projeto original (a relatar ao mod):
1. `Server.Start(port, enableIPv6: false)` cria socket IPv4, mas `Server/Managers/NetworkManager.cs:76` sempre passa EndPoint IPv6 para `ReceiveFrom`. O resultado é uma exceção em ciclo contínuo sem espera progressiva: 6,1 milhões de registros, 4,4 GB de log em 6 minutos. Todos os chamadores internos passam `true`, portanto os jogadores não são afetados atualmente.
2. Ao entrar, o cliente registrou `InitialLandPlotsPacket threw: IndexOutOfRangeException` em `AmmoModel.Reset ← SiloStorage.SetModel ← InitialLandPlotsHandler.Handle` (`InitialLandPlots.cs:127`). O salvamento do host tinha silos e o cliente estava no início do jogo. Se os lotes restantes daquele pacote foram ignorados: desconhecido.

## <a id="qa"></a>QA

- Preparação: copie a instalação, crie instâncias com hardlinks usando `tools/gamepool` (configuração como `qa/sr2.example.json`) e instale MelonLoader 0.7.3, Starlight 4.0.4, SR2MP 0.3.9, `CoopQA.SaveIsolation.dll` (em `Plugins/`) e `CoopQA.Bot.dll` (em `Mods/`) em cada instância. Depois: `python -I games/slime-rancher-2/qa/run_coop_test.py --host-ip <LAN IPv4>` (caminhos privados, identificador Steam e nomes de salvamentos ficam em `local/sr2-qa.json`).
- Asserções: ambas as cópias carregam seus próprios salvamentos; eles diferem antes da conexão; servidor executa; cliente conecta; host conta 1 cliente; cada lado vê o outro jogador; dinheiro do cliente igual ao do host após entrar; host +777 chega ao cliente; cliente +111 chega ao host; a visão de cada lado sobre o outro jogador fica a até 2 m (jogadores parados, portanto verificação fraca); instalação e salvamentos reais inalterados.
- 2026-10-23, jogo 1.3.0, SR2MP 0.3.9, Starlight 4.0.4, MelonLoader 0.7.3, um PC, 2 clientes:

  ```
  RESULT: PASS  (16/16 checks)
  ```

  Uma execução anterior com bug do bot (servidor iniciado com `enableIPv6=false`, que nunca responde) falhou em 8/14; portanto, as verificações de conexão e sincronização conseguem falhar.
- Não cobertos: internet, NAT ou UPnP, movimento, slimes, lotes, dispositivos, drones, salvamento no cliente, 3 ou mais jogadores, latência e perda.

## <a id="how-to-play"></a>Como jogar

1. Todos os jogadores: instalem [MelonLoader 0.7.3](https://github.com/LavaGang/MelonLoader/releases/tag/v0.7.3) em Slime Rancher 2. Coloquem [Starlight 4.0.4](https://github.com/ThatFinn/Starlight/releases/tag/v4.0.4) `Starlight.dll` e [SR2MP 0.3.9](https://github.com/pyeight/SlimeRancher2Multiplayer/releases/tag/Beta_0.3.9) `SR2MP.dll` em `Mods`. O README do mod informa Starlight 4.0.3, mas SR2MP 0.3.9 foi compilado com 4.0.4. Todos precisam das mesmas versões.
2. Host: carregue o mundo desejado e abra o menu multiplayer. Use hospedagem automática (UPnP) ou redirecione UDP 1919; depois envie o código de entrada. Sem UPnP ou redirecionamento, use VPN como Tailscale, ZeroTier ou Radmin VPN.
3. Amigos: carreguem uma vaga de salvamento vazia ou nova (entrar a sobrescreve) e informem o código.

## <a id="known-issues"></a>Problemas conhecidos

- Inventário do jogador não sincronizado; entre novamente usando o mesmo salvamento (README do mod).
- Gray Labyrinth, Sanctuary e alguns comportamentos dos slimes só parcialmente sincronizados (README do mod).
- Um erro ao entrar, copiando conteúdo de silos (veja acima). Alguns silos podem divergir; não verificado.
- Sem retransmissão pelo Steam: host precisa de UPnP, porta redirecionada ou VPN.

## <a id="next-steps"></a>Próximos passos

- Relatar os dois bugs ao projeto original com os rastreamentos de pilha acima.
- Ampliar o bot: mover jogador, aspirar e disparar slimes, plantar jardim, conferir silos nos dois lados (bug 2), salvar no cliente e simular latência e perda com `tools/chaos`.
- Transporte por retransmissão Steam (Spacewar, consulte [networking-steam-spacewar](../../playbook/networking-steam-spacewar.md)) eliminaria o redirecionamento de portas; seria necessário propô-lo ao autor do mod.
