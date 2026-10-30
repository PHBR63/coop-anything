# <a id="enter-the-gungeon--session-notes"></a>Enter the Gungeon - notas das sessões

## <a id="game-identity-phase-0-recorded-2026-10-18"></a>Identidade do jogo (etapa 0, registrada em 2026-10-18)

- Título: Enter the Gungeon (Dodge Roll / Devolver Digital)
- Loja: Steam, appid 311690
- Steam buildid: 3829397 (LastUpdated do appmanifest 1750969237 = 2025-06-27)
- Depósitos: 311691 manifesto 8878936682682257329, 311694 manifesto 1630144318006415956
- SHA-256 de EtG.exe: 220E76C1263559BB38DA6C1ED8B0F473F2FF67E5234A6CCC93ECAB98725B5B61
- Tamanho de EtG.exe: 650752 bytes; FileVersionRaw 2017.4.27.19333
- Motor: Unity 2017.4.27f1 (de EtG_Data/globalgamemanagers)
- Sistema operacional: Windows (win32)
- Caminho da instalação: `local/install-path.txt` (privado, ignorado pelo Git)
- Idioma configurado: russo
- Arquitetura: x64 (máquina PE de EtG.exe 0x8664). Carrega a `steam_api64.dll` distribuída (SDK Valve), não a x86.

## <a id="phase-0--triage-result"></a>Etapa 0 - resultado da triagem

- Sem entrada em DIRECTORY.md ou data/directory.yaml (grep "gungeon"/"gundion" sem resultados).
- Sem trabalho anterior em games/ neste núcleo.
- Jogo oferece cooperativo local nativo (até 4), mas não cooperativo on-line oficial (declaração dos desenvolvedores, discussões Steam de 2015).
- Pedido do usuário: cooperativo on-line com amigos. Cópia Steam, instalação padrão.
- -> Caminho candidato: caminho 1 (retomar/ampliar tentativas existentes); há várias, veja etapa 1.

## <a id="phase-1--research-done-2026-10-18-sources--web--github-api-this-session"></a>Etapa 1 - pesquisa (2026-10-18, fontes = web + API GitHub nesta sessão)

| Projeto | Onde | Licença | Última atividade confirmada | O que realmente sincroniza (segundo autor) | Relatos de bugs |
|---|---|---|---|---|---|
| **Gungeon Online** v0.101.0 (GoTeamAlex) | thunderstore.io/c/enter-the-gungeon/p/GoTeamAlex/Gungeon_Online | MIT | Thunderstore (data não coletada, desconhecida) | Convites por sala Steam + LAN UDP 27460; semente compartilhada, personagem/animação/arma/mascote/estado, vida/mortes de inimigos, balas/arremessos/blanks/efeitos do chão, mesas/quebráveis/barris, fantasma+reanimação por baú, pausa compartilhada, PvP opcional. NÃO sincroniza: simulação de ataques de inimigos (cada cliente calcula), itens deixados na morte | wiki/registro de mudanças Thunderstore |
| **GungeonTogether** (llamerrr) | github.com/llamerrr/GungeonTogether | MIT | último commit 2026-09-28 (PR #12, scripts de compilação); README ainda diz "ON HOLD" | Sala/convites Steam + P2P prontos; posição/animação do jogador funcionam; inimigos/masmorra planejados. **Sem compilação distribuída:** issues #7/#11/#13 não encontram a DLL | issues GitHub (9 abertas); #2 "Mega Issue of Bugs": clientes não teleportados à partida, invisíveis, falta de sincronização cliente-cliente, troca de jogador não propagada, bugs de interface, sem contornos/sombras remotos, nomes sobre interface, limpeza quebrada |
| **GungeonTogether LAN** v0.3.6 (mamonts) | thunderstore.io/.../mamonts/GungeonTogether_LAN | (desconhecida) | v0.3.6 (Thunderstore) | LAN para 2/TCP 27631; host executa cooperativo nativo, cliente controla jogador 2, câmera/HUD próprios, salas secretas + livro de equipamento. **Bloqueio conhecido: divergência do mapa Sell Creep no 4º andar interrompe partidas**; campanha completa não verificada; feito para Steam EtG 2.1.9 | página Thunderstore + VALIDATION.md no código |
| **Jolly_Coop** v1.3.7 (kleirof) | github.com/kleirof/Jolly_Coop | (não informada) | versão 2026-01-02 (ZIP, SHA-256 e72c3616..., 4 downloads) | Desconhecido: plugin inicia, patches Harmony de 53 KB, OutlineColorManager (contornos), depende de ModTheGungeon API + Gunfig. Nenhum código de rede visto na lista de arquivos, sem leitura integral. Provável melhoria cooperativa local | nenhum (sem issues) |
| Gunnect+ (The_Rot_Bot) | modworkshop.net/mod/34633 | (desconhecida) | 2021 | NÃO é cooperativo: estrutura de interação entre partidas, precisa de Hamachi | comentários modworkshop |

Também encontrados (não avaliados): CoopBot (ItsYuri, Thunderstore), companheiro bot que simula cooperativo, candidato a bot de QA (playbook/automated-qa). GungeonCraft e Ammonomicon API (Thunderstore), infraestrutura de mods.

### <a id="ecosystem-facts-phase-3-shortcuts"></a>Fatos do ecossistema (atalhos da etapa 3)

- Carregadores: ModTheGungeon (clássico, MTG API 1.6.1) e BepInExPack_ETG (Thunderstore). Ambos usados pelos candidatos.
- **Existe pacote NuGet EtG.GameLibs** (v2.1.9.1): Assembly-CSharp.dll descompilado (3,5 MB), Assembly-CSharp-firstpass, PlayMaker, módulos UnityEngine completos, incluídos no repositório Jolly_Coop. Não precisamos descompilar a v2.1.9.
- Unity 2017.4.27f1, C# gerenciado, patches HarmonyX/Harmony são abordagem padrão (guia de famílias: Unity -> BepInEx/Harmony).
- Versão nas fontes: 2.1.9 (corresponde à instalação? buildid 3829397, relação entre 2.1.9 e buildid desconhecida; verificar EtG_Data ou mudanças do jogo depois).

### <a id="observations--derived--guesses--unknowns-rule-4"></a>Observações / deduções / hipóteses / desconhecidos (regra 4)

- Observação: único resultado web "Enter the Gundion" é erro de grafia em piada no Reddit; usuário confirmou Enter the Gungeon.
- Observação: sem entrada em DIRECTORY.md / games/; não coberto. AGENTS.md exige issue "claim a game" (bloqueada: CLI gh não instalado).
- Observação: GungeonTogether NÃO tem compilações publicadas (3 issues abertas pedem DLL).
- Dedução: caminho 1 (concluir existente) é correto; duas linhas viáveis, Gungeon Online (mais completo, jogável) e GungeonTogether (mais ativo, ainda não jogável).
- Dedução: NuGet EtG.GameLibs elimina a parte mais pesada da etapa 3 (descompilação).
- Hipótese: buildid 3829397 corresponde à versão 2.1.9 (ambos visam 2.1.9; LastUpdated acf 2025-06-27).
- Desconhecidos: recursos completos de Jolly_Coop, data do último envio de Gungeon Online, compatibilidade dele com compilação 3829397 (página não informa versão do jogo).

## <a id="environment-notes-private"></a>Notas de ambiente (privadas)

- CLI `gh`: instalada em 2026-10-18 (v2.102.0), ainda não autenticada (exige login GitHub do usuário).
- `python`: instalado em 2026-10-18 (3.12.10) em `%LOCALAPPDATA%\Programs\Python\Python312\python.exe`. `.NET SDK` 8.0.426 instalado. PATH pode precisar de atualização em novos terminais.

## <a id="phase-2--workspace-done-2026-10-18-owner-approved"></a>Etapa 2 - ambiente de trabalho (2026-10-18, autorizado)

- Instalação de teste: `<workspace>/test-install/Enter the Gungeon` (robocopy da real, 202 arquivos / 318,4 MB, 0 falhas).
- Carregador: BepInEx-BepInExPack_EtG 5.4.2101 (versão fixada, Thunderstore oficial).
  - SHA-256 ZIP: 6B97EDB311E961E78CA1CD913A886FD72B1EE936C73300C8992B8BF86FFDE7BA (720997 bytes)
- Mod: GoTeamAlex-Gungeon_Online 0.101.0 (fixado, Thunderstore oficial; enviado em 2026-10-17).
  - SHA-256 ZIP: EF8E276651A089CA48F6DA5714E053C8715E0AAD88046F90CE7E2ED51A2D5546 (111855 bytes)
  - Dependência: BepInEx-BepInExPack_EtG-5.4.2101 (satisfeita).
- Organização: doorstop (winhttp.dll) + BepInEx na raiz de teste; `BepInEx/plugins/GungeonOnline.dll`.

## <a id="phase-3--boot-test-2026-10-18"></a>Etapa 3 - teste de inicialização (2026-10-18)

- Teste: `<test>/EtG.exe` iniciado diretamente com Steam ativo; observado 50 s; lido `<test>/BepInEx/LogOutput.log`.
- Resultado: **PASS no carregamento do plugin.** BepInEx 5.4.21.0 em Unity 2017.4.27.805765, Bits64 Windows; "Loading [Gungeon Online 0.101.0]"; hooks de salvamento ativos; "Gungeon Online 0.101.0 loaded. Press F8 in game to open the multiplayer window."; chainloader concluiu. Sem erros do mod.
- Log Unity (`%USERPROFILE%\AppData\LocalLow\Dodge Roll\Enter the Gungeon\output_log.txt`): chegou ao foyer/seleção (apenas avisos benignos do clipe select_idle). Avisos XInputInterface32 x86/x64 são mensagens habituais do jogo.

### <a id="incident-rule-2--disclosed-to-owner"></a>Incidente (regra 2) - informado ao usuário

- Iniciar diretamente o executável disparou `SteamAPI_RestartAppIfNecessary`: processo de teste encerrou após cerca de 30 s; Steam abriu a instalação REAL (LastPlayed atualizado para 2026-10-18 20:17). O agente encerrou a instância real cerca de 30 s depois, no menu.
- Verificação de dano: `SlotA.save` intacto (mtime 2026-05-15). Nenhuma partida iniciada. `SlotA.options` mtime 8:16:31 (gravado no teste, só opções), `steam_autocloud.vdf` e output_log.txt alterados.
- Mitigação: backup completo de `%USERPROFILE%\AppData\LocalLow\Dodge Roll\Enter the Gungeon\` em `local/locallow-backup-20261018/` ANTES dos próximos testes. Lição: LocalLow é compartilhado por todas as cópias; faça backup antes e restaure depois.
- **Preparação de QA:** dois ambientes `test-install-host\Enter the Gungeon` e `test-install-client\Enter the Gungeon`. Em ambos, `steam_api.dll` substituída pela real (versão x86 correta) de Steamworks.NET Standalone 2025.164.1 (SHA-256: FDAFB7C65E...47EB65DA), com `steam_appid.txt` = 480. Isso permite usar Steam API (salas/convites/retransmissão P2P). Como um PC não pode acessar duas contas Steam ao mesmo tempo, multiplayer completo por contas reais exigirá dois PCs ou simulação Steamworks específica; o passo atual verifica a inicialização com DLL substituída.
- **Teste básico rápido do host:** cópia host iniciada com LocalLow restaurado. Mod carregou (`Gungeon Online 0.101.0 loaded`), acrescentou Multiplayer à pausa e executou autoteste de salvamentos (434/434 iguais). Steam API inicializou (`Starting Steam platform interface`, estatísticas recebidas). Agente encerrou corretamente sem danificar `SlotA.save` (original em backup).

## <a id="phase-6--двухклиентный-qa-lan-2026-10-18--pass"></a>Etapa 6 - QA com dois clientes (LAN, 2026-10-18) - PASS

Descoberta principal: **Gungeon Online inclui estrutura automatizada de testes** (descompilada de `BepInEx/plugins/GungeonOnline.dll`, consulte `local/decomp/GungeonOnline.decompiled.cs`):

- `--gungeon-online-name <name>` - definir nome.
- `--gungeon-online-test host|join` - hospedar/entrar automaticamente na LAN na tela de título (host `HostLan(27460)`, cliente `JoinLan(127.0.0.1:27460)`), depois entrar em Breach.
- `--gungeon-online-test-run <CharacterPrefabSuffix>` - escolher personagem automaticamente (`CharacterPrefabPath.EndsWith(suffix)`) e, no host, iniciar a partida após conexão do parceiro.

`CharacterPrefabPath` conhecidos nos recursos: `PlayerMarine`, `PlayerGuide`, `Player_Rogue`/`Player_Rogue_`, `Player_Convict`(?), `PlayerRobot`, `PlayerBullet`, `PlayerGunslinger`, `PlayerEevee`, `PlayerCoopCultist`, `PlayerCosmonaut`.

### <a id="изоляция-сейвов-правило-2"></a>Isolamento de salvamentos (regra 2)

Antes do teste, `%USERPROFILE%\AppData\LocalLow\Dodge Roll\Enter the Gungeon` foi renomeada para `...REAL-<ts>` (cópia completa do salvamento preservada) e criada pasta vazia de teste. A real foi restaurada depois (confirmado: mtime de `SlotA.save` em 5/15/2026 inalterado). As cópias usam `steam_api.dll` x86 de Steamworks.NET + `steam_appid.txt=480` (Spacewar), evitando sincronização Steam Cloud EtG (appid 311690).

### <a id="прогон-1--связь-2-клиента-локальная-udp-петля"></a>Execução 1 - conexão (2 clientes, UDP local)

Comandos:
```
host : EtG.exe --gungeon-online-name Hosty   --gungeon-online-test host -screen-fullscreen 0 -screen-width 960 -screen-height 540
client: EtG.exe --gungeon-online-name Clienty --gungeon-online-test join -screen-fullscreen 0 -screen-width 960 -screen-height 540
```
Resultado: ambos funcionam simultaneamente (sem mutex de instância única). Host: `Hosting LAN game on port 27460` -> `Connected to Clienty over LAN!`. Cliente: `Joining LAN game at 127.0.0.1:27460` -> `Connected to Hosty over LAN!` -> `Joined from the title screen: entering the Breach.` Estável por cerca de 55 s, sem expirações. Logs: `local/qa-run1/`.

### <a id="прогон-2--полный-забег-pass"></a>Execução 2 - partida completa (PASS)

Comandos (acrescentado `--gungeon-online-test-run`):
```
host : EtG.exe --gungeon-online-name Hosty   --gungeon-online-test host --gungeon-online-test-run Marine ...
client: EtG.exe --gungeon-online-name Clienty --gungeon-online-test join --gungeon-online-test-run Guide  ...
```
Resultado (logs `local/qa-run2-fullrun/`):
- `Test run: picking PlayerMarine` (host), `Test run: picking PlayerGuide` (cliente).
- Host: `Test run: host starting the run.` -> `SETTING GLOBAL RUN SEED TO: 542264008` -> `Floor fingerprint: 20 rooms, 2A7BE448 (LoadingDungeon|Base_Castle(Clone)|542264008)`.
- Cliente: mesma semente `542264008` e **`Floor matches the host's (2A7BE448).`**; geração procedural do andar idêntica.
- Sincronização: `Partner map marker`, `Created the partner's target body for enemies`, `Showing partner's pet Dog`, `Indexed 427 projectile types from 379 guns`, pausa compartilhada (`Clienty paused/unpaused`), SaveSync (`got the host's progress`).
- Cerca de 4 minutos sem `timed out`, `Disconnected`, `Exception` ou `mismatch` nos logs.

Resultado: **dois clientes, mod real, LAN, conexão, escolha de personagens, semente compartilhada, andar idêntico, marcadores/mascotes/pausa/salvamentos, tudo PASS.** Funciona na compilação atual 3829397 (versão 2.1.9).

### <a id="что-не-проверено"></a>O que NÃO foi verificado

- Sala/convites Steam (exige segunda conta ou PC); só LAN testada.
- Estresse/sessões longas, chefes, 4º andar (Sell Creep): GungeonTogether LAN tinha bugs ali; não verificado em Gungeon Online.
- Dessincronizações causadas pela simulação independente de ataques dos inimigos (o próprio autor informa que cada lado calcula separadamente).

### <a id="известные-ограничения-мода-по-декомпиляцииописанию"></a>Limitações conhecidas (descompilação/descrição)

- Não sincronizados: ataques de inimigos (cada cliente calcula, podendo divergir), itens deixados após morrer.
- Todos precisam do mesmo conjunto/versão de mods (protocolo 32; caso contrário, `version mismatch`).

## <a id="phase-3p--кооп-на-3-игроков-gungeontogether-3-player-2026-10-18"></a>Etapa 3p - cooperativo para 3 ou mais (GungeonTogether 3-Player), 2026-10-18

### <a id="почему-именно-этот-мод-разведка"></a>Por que este mod (investigação)

- Gungeon Online é estritamente para 2 (comprovado descompilando `GungeonOnline.dll`): um `RemotePlayerState`, transporte LAN com um par (segunda conexão recusada), `CreateLobby((ELobbyType)1, 2)`, identificador de arma `id*2 + hostFlag`. Jogo base nativo com máximo de 2 locais (segundo = The Cultist).
- Única compilação publicada para 3 ou mais: **Rec-GungeonTogether_3Player** (Thunderstore; criada em 2026-10-12, atualizada em 2026-10-14; categoria "AI Generated"). Demais (`llamerrr/GungeonTogether`, `mamonts/GungeonTogether_LAN`) para 2.
- Sinal de alerta (regra 6): repositório público `AhmetRec/GungeonTogether-3Player` no HEAD = **0.9.0** (tag v0.9.0, csproj 0.9.0), DLL publicada = **0.10.8.0**. Binário difere do código público, portanto apenas o próprio binário serve de base para verificação (foi ele que analisamos).

### <a id="скачанные-пины-rule-8-official-thunderstore-only"></a>Downloads com versões fixadas (regra 8, somente Thunderstore oficial)

- `Rec-GungeonTogether_3Player-0.10.8.zip` - SHA-256 `1B2D51E54547F0C8F3B11D97686249E0177ABCE7A04126A7343D4048BFE82D4F` (277161 bytes).
- `MtG_API-Mod_the_Gungeon_API-1.9.2.zip` - SHA-256 `4941CCF4DC325EB6C9826709E9C75AE3BA77969FDC5363C39369D81388E65571` (1083368 bytes). Dependência do mod de 3 jogadores.

### <a id="статический-анализ-бинарника-rule-4"></a>Análise estática do binário (regra 4)

- Descompilado em `local/decomp/3p/` (72 arquivos, 13285 linhas).
- Sem sinais de alerta: nenhum literal URL/IP, `Process.Start`/`ProcessStartInfo`, `WebClient`/`HttpClient`/`Dns`, `Registry`, `FromBase64String`, `DllImport`/carregamento nativo ou escrita de arquivos. `Reflection.Emit` em `SteamCallbackRouter.cs` é benigno (delegate dinâmico para encaminhar callbacks Steam). `Environment.*` usa só `TickCount` (semente) e `GetCommandLineArgs` (interpretação de `+connect_lobby` Steam).
- Único ConfigEntry: `ProgressSync/Enabled`; sem telemetria/análise/envio de dados.

### <a id="boot-тест-rule-11--pass-только-загрузка-не-игра"></a>Teste de inicialização (regra 11) - PASS (só carregamento, não partida)

- Cópia isolada `test-install-3p\Enter the Gungeon` (robocopy da real, 243 arquivos) + BepInEx 5.4.2101 + MtG_API 1.9.2 + `GungeonTogether.dll` 0.10.8. `GungeonOnline.dll` removida para evitar conflito.
- **Execução 1 - FAIL por erro meu:** substituí `steam_api64.dll` por versão mais recente de Steamworks.NET; `CSteamworks.dll` não achou funções exportadas (`The specified procedure could not be found`), Steam não iniciou e jogo encerrou (código 0). Lição: jogo **x64** (EtG.exe PE machine 0x8664), carrega `steam_api64.dll` **original**, que não deve ser substituída. AppID por `steam_appid.txt=480`.
- **Execução 2 (`steam_api*` original + `steam_appid.txt=480`) - PASS:**
  - `Loading [Gungeon Together 0.10.8]` -> `Gunseon Together starting...` -> `[Progress] Installed 8 progress query patches.` -> `Gunseon Together ready.`
  - Steam iniciado: `Starting Steam platform interface`, `Received stats and achievements from Steam`, sem erro CSteamworks.
  - Rede do mod ativa: tipos Steamworks encontrados; `SendP2PPacket`/`ReadP2PPacket`/`IsP2PPacketAvailable`/`AcceptP2PSessionWithUser` = `Found`; callbacks `LobbyCreated`/`LobbyEnter`/`GameRichPresenceJoinRequested`/`LobbyMatchList` criados.
  - Jogo chegou ao menu; sem exceções do mod (só avisos HarmonyX inofensivos "patch the declared method" e mensagens habituais: áudio `select_idle`, x86 `XInputInterface32.dll`, conquistas devido a appid 480).
- Isolamento (regra 2): `%USERPROFILE%\AppData\LocalLow\Dodge Roll\Enter the Gungeon` renomeada durante o teste e restaurada; `SlotA.save` (125273 bytes, `E9F1C573…`) inalterado.
- **Observação:** enquanto isso, o próprio usuário instalou BepInEx + Gungeon Online na instalação **real** (pasta `BepInEx` criada em 2026-10-18 22:07) e jogou (SlotA.save passou de 125052 a 125273 bytes, mtime 22:26). Ação do usuário, não do agente.
- Limitação: mod de 3 jogadores **somente Steam**; não é possível reproduzir localmente uma sessão real de três clientes; precisa de teste de partida pelo usuário.

### <a id="пакет-для-друзей-phase-7-стиль"></a>Pacote para amigos (estilo da etapa 7)

- `local/friends-package/GungeonTogether-3Player/` + `dist/Enter-the-Gungeon-3Player-Co-op.zip`.
  - ZIP: 1872725 bytes, 38 entradas, SHA-256 `702835F23C67135CB8D2EA9260FA2C576711C35E37CF9D3E320E8EB28C9A3ADD`.
  - Conteúdo: BepInExPack_EtG 5.4.2101 + MtG_API 1.9.2 (`BepInEx/plugins/MtGAPI/*`, `BepInEx/monomod/*`) + `BepInEx/plugins/GungeonTogether.dll` 0.10.8 + README (RU).
- README avisa: incompatível com Gungeon Online (remover `GungeonOnline.dll`), só Steam, mod experimental.

## <a id="next"></a>Próximos passos

- Decisão com usuário (etapa 7): instalar BepInEx + Gungeon Online na instalação Steam REAL para jogar com amigos. Amigos precisam da mesma versão do mod/BepInEx.
- Opcional: verificar salas Steam em dois PCs; estresse prolongado com combate e 4º andar.
- Etapa 8: entrada em `data/directory.yaml` -> `python tools/build_directory.py` -> `games/enter-the-gungeon/README.md` (pelo modelo) -> PR em rascunho (`gh` ainda não autenticado).

## <a id="next-1"></a>Próximos passos

- QA com dois clientes: LAN (UDP 27460) em 127.0.0.1 entre dois ambientes; exige backup/restauração LocalLow; verificar primeiro mutex de instância única.
- Sala Steam: exige simulação steam_api.dll (uma conta por PC) ou segundo PC físico.
- Decisão da etapa 7 pendente com usuário: instalar na instalação REAL para jogar com amigos.
