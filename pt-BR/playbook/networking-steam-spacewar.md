# <a id="steam-spacewar-appid-480-networking-no-ips-no-port-forwarding"></a>Rede Steam "Spacewar" (AppID 480): sem IPs nem redirecionamento de portas

Como dar salas Steam, entrada por amigos e tráfego P2P retransmitido a qualquer mod cooperativo, sem digitar IP ou alterar o roteador. Dois exemplos funcionais:

- **Integrado ao jogo:** a compilação cooperativa KeeperFX (Dungeon Keeper) tem camada de rede Steam, `src/net_steam.cpp`, junto dos demais provedores.
- **Retransmissor ao lado, sem mudar o motor:** `HXCoop.exe` para Deus Ex (veja [games/deus-ex](../games/deus-ex/README.md)). Cria a sala, inicia o jogo e leva os pacotes UDP do próprio jogo pelo Steam. Use quando o código de rede do motor for fechado ou difícil de alterar.

## <a id="the-idea"></a>A ideia

Qualquer usuário Steam pode executar AppID **480 "Spacewar"**, aplicativo de exemplo gratuito da Valve. Se um jogo carregar `steam_api.dll` com `steam_appid.txt` contendo `480` junto ao executável, o Steam o trata como Spacewar e fornece a API Steamworks completa:

- **Salas** (ISteamMatchmaking). Host cria sala só para amigos; amigo entra por convite, clicando com botão direito no host e escolhendo Join Game, ou pelo ID da sala.
- **Mensagens P2P** (ISteamNetworkingMessages). Tráfego por SteamID pela rede de retransmissores Valve; sem IPs, redirecionamento ou problemas de NAT.
- **Janela de convite da sobreposição e presença detalhada** (ISteamFriends).

A ressalva: ambos aparecem como "playing Spacewar", salas ficam visíveis para todos os usuários 480 no mundo salvo filtro por dados de sala, e isso não permite publicar na loja Steam. Para mod entre amigos, tudo bem.

Ambos precisam do Steam aberto e conectado. Ninguém precisa possuir nada.

## <a id="getting-a-32-bit-steam_apidll"></a>Obtendo steam_api.dll de 32 bits

Use a versão "Standalone" de Steamworks.NET (github.com/rlabrecque/Steamworks.NET/releases). Os dois exemplos usam `Windows-x86/steam_api.dll` da versão 2025.164.1:

- SHA-256 `fdafb7c65ec7d4182b42bf92cc8671c68e4dc547cc6e613899d2618a47eb65da`
- Exporta `SteamAPI_InitFlat` e a interface de mensagens `..._v002`.

Cópias de jogos antigos (como Fallout New Vegas) não exportam a API plana; não as use.

`CreateLobby(self, eLobbyType, maxMembers)`: tipo 1 = somente amigos. `SteamNetworkingMessages` deve usar o getter `..._SteamAPI_v002`, não o de servidor de jogo.

**Join Game sem o jogo aberto** provavelmente inicia Spacewar (AppID 480), não seu mod. Peça ao amigo iniciar o mod antes de aceitar convite ou clicar Join Game.

**Confira primeiro a cópia do jogo.** Um jogo Steam recente pode incluir `steam_api64.dll` com API plana: a de The Witcher 3 Remastered (`bin\x64_dx12`, versão 10.87.46.89) exporta todas as funções e versões de interfaces abaixo. O retransmissor pode carregá-la da instalação do jogador, sem download ou redistribuição.

Para jogos de 64 bits, use `Windows-x64/steam_api64.dll` da mesma versão:

- SHA-256 `eb17909a76668cf9ae0b92a618a34a50f6c73d3a6787cb4dd8ce36a8b10bfb75`

Confira a arquitetura: executável de 32 bits exige DLL PE32 i386; 64 bits exige x64. Vários deslocamentos de estruturas diferem (abaixo).

### <a id="the-games-copy-may-not-have-it-and-what-to-do-with-no-compiler"></a>A cópia do jogo pode não oferecer a API; e como proceder sem compilador

A verificação precisa ser executada, pois frequentemente a resposta é não: `steam_api64.dll` de Poppy Playtime (Steamworks 1.51, nas pastas `Engine\...\Steamv151\Win64` e `PlaytimeLauncher`) **não tem `SteamAPI_InitFlat`**; presumir o contrário falharia tarde. Poucas linhas Python resolvem: `ctypes.WinDLL(path)` e `getattr(dll, name)` para cada símbolo, sem ferramentas de compilação.

O mesmo recurso serve quando não há compilador C/C++. A API C plana permite chamadas sem cabeçalhos Steamworks: `ctypes` controla inicialização, getters `SteamAPI_ISteam*`, `ManualDispatch_*`, salas e `NetworkingMessages` diretamente, usando os deslocamentos desta página. Um programa com `--transport udp|steam` fornece substituto de testes controlável por script (UDP localhost, sem segunda conta, dois clientes num PC) e caminho Steam real pelo mesmo código. Evidência: Poppy Playtime, [games/poppy-playtime/NOTES.md](../games/poppy-playtime/NOTES.md), etapa 6.

## <a id="design-no-sdk-headers-dynamic-loading-only"></a>Projeto: sem cabeçalhos SDK, somente carregamento dinâmico

`LoadLibrary("steam_api.dll")`, depois `GetProcAddress` para cada função da **API C plana**. São funções C `__cdecl` cujo primeiro argumento é o ponteiro da interface. Sem cabeçalhos SDK ou bibliotecas de importação, mantendo o repositório GPL limpo e funcionando com mingw. Se faltar a DLL, mostre erro claro e volte ao código de rede normal.

### <a id="functions-used-exact-export-names"></a>Funções usadas (nomes exatos das exportações)

```
SteamAPI_IsSteamRunning           SteamAPI_InitFlat           SteamAPI_GetHSteamPipe
SteamAPI_ManualDispatch_Init      SteamAPI_ManualDispatch_RunFrame
SteamAPI_ManualDispatch_GetNextCallback  SteamAPI_ManualDispatch_FreeLastCallback
SteamAPI_ManualDispatch_GetAPICallResult

Interface getters (each returns the interface pointer):
SteamAPI_SteamUser_v023  SteamAPI_SteamMatchmaking_v009  SteamAPI_SteamFriends_v018
SteamAPI_SteamNetworkingMessages_SteamAPI_v002  SteamAPI_SteamNetworkingUtils_SteamAPI_v004

SteamAPI_ISteamUser_GetSteamID  SteamAPI_ISteamUser_BLoggedOn
SteamAPI_ISteamMatchmaking_CreateLobby / JoinLobby / LeaveLobby / SetLobbyData /
    SetLobbyJoinable / GetLobbyOwner
SteamAPI_ISteamFriends_SetRichPresence  SteamAPI_ISteamFriends_ActivateGameOverlayInviteDialog
SteamAPI_SteamNetworkingIdentity_SetSteamID64 / GetSteamID64
SteamAPI_ISteamNetworkingMessages_SendMessageToUser / ReceiveMessagesOnChannel /
    AcceptSessionWithUser / CloseSessionWithUser
SteamAPI_SteamNetworkingMessage_t_Release
SteamAPI_ISteamNetworkingUtils_SetGlobalConfigValueInt32
```

`SteamAPI_InitFlat(char errMsg[1024])` retorna 0 em sucesso, 1 em falha genérica, 2 sem Steam aberto, 3 em incompatibilidade de versão. Escreva `steam_appid.txt` = `480` se ausente.

### <a id="callbacks-manual-dispatch-no-c-ccallback-classes"></a>Callbacks: despacho manual (sem classes C++ CCallback)

Chame `ManualDispatch_Init()` uma vez. Depois, a cada quadro:

```
pipe = SteamAPI_GetHSteamPipe();
ManualDispatch_RunFrame(pipe);
while (ManualDispatch_GetNextCallback(pipe, &msg)) {
    if (msg.callback == 703 /* SteamAPICallCompleted_t */) {
        // async call result (e.g. LobbyCreated, LobbyEnter from CreateLobby/JoinLobby)
        buf = malloc(done->param_size);
        if (ManualDispatch_GetAPICallResult(pipe, done->call, buf, done->param_size, done->callback, &failed) && !failed)
            handle(done->callback, buf);
    } else handle(msg.callback, msg.param);
    ManualDispatch_FreeLastCallback(pipe);
}
```

IDs dos callbacks:

| Callback | Id |
|---|---|
| GameLobbyJoinRequested | 333 |
| GameRichPresenceJoinRequested | 337 |
| LobbyEnter | 504 |
| LobbyChatUpdate | 506 |
| LobbyCreated | 513 |
| SteamAPICallCompleted | 703 |
| SteamNetworkingMessagesSessionRequest | 1251 |
| SteamNetworkingMessagesSessionFailed | 1252 |

### <a id="struct-layouts-windows-pragma-packpush-8"></a>Organização das estruturas (Windows, `#pragma pack(push, 8)`)

```
CallbackMsg_t            { int32 hSteamUser; int32 callback; uint8 *param; int32 param_size; }
SteamAPICallCompleted_t  { uint64 call; int32 callback; uint32 param_size; }
LobbyCreated_t           { int32 result; uint64 lobby; }                // 8-byte aligned
LobbyEnter_t             { uint64 lobby; uint32 perms; bool locked; uint32 response; } // 1 = success
LobbyChatUpdate_t        { uint64 lobby; uint64 user_changed; uint64 making_change; uint32 state_change; }
                          // state flags: left 0x2, disconnected 0x4, kicked 0x8, banned 0x10
GameLobbyJoinRequested_t { uint64 lobby; uint64 friend; }
GameRichPresenceJoinRequested_t { uint64 friend; char connect[256]; }
```

- **SteamNetworkingIdentity** tem 136 bytes. Trate como buffer opaco (KeeperFX aloca 160) e preencha/leia só por `SetSteamID64` / `GetSteamID64`. Callbacks de solicitação/falha da sessão começam com essa identidade.
- **SteamNetworkingMessage_t** (32 bits, DLL compilada com MSVC): `data` em 0, `size` em 4, identidade do remetente em **12** na `steam_api.dll` real de 32 bits (Steamworks.NET Standalone 2025.164.1; confirmado entre contas reais em Clive Barker's Jericho, 2026-10-21). O alinhamento de 8 bytes dos cabeçalhos sugere 16, mas isso lê remetente 0: mensagens descartadas como desconhecidas, sem explicação, enquanto solicitação de sessão (identidade em 0) parece correta. Leia 16 e 12, use o que decodificar ID não zero (KeeperFX faz isso) e registre qual venceu. Simulação que escreve em 16 passa de qualquer forma; só teste com duas contas detecta. Sempre chame `SteamNetworkingMessage_t_Release`.
- **SteamNetworkingMessage_t em 64 bits** (`steam_api64.dll`): `data` em 0 (ponteiro de 8 bytes), `size` em **8**, identidade em 16. Ler `size` em 4 gera lixo. `FriendGameInfo_t` e os callbacks acima mantêm a mesma organização em x64.

### <a id="messaging-rules-learned-the-hard-way"></a>Regras de mensagens aprendidas na prática

- **Aceitar sessão:** primeira mensagem de SteamID desconhecido gera SessionRequest (1251). Chame `AcceptSessionWithUser` ali, ou mensagens ficam retidas/descartadas. Host aceita desconhecidos; clientes só aceitam o host.
- **Sem evento de desconexão:** ISteamNetworkingMessages não informa encerramento do parceiro. KeeperFX resolve de três formas:
  - Canal de controle (1) leva despedida, expulsão com motivo e sinal de conexão a cada 1 s.
  - Parceiro silencioso por 20 s é removido.
  - Indicadores de saída/desconexão de LobbyChatUpdate e SessionFailed também removem.
- **Responda sinais antes dos dados do jogo.** Retransmissor do amigo entra enquanto o jogo carrega; por um minuto só trafegam sinais. Se host acompanhar apenas quem enviou dados, convidado vê silêncio e desiste. Acompanhe cada membro que falar no controle e faça convidado entrar novamente, em vez de sair, se host silenciar (retransmissor The Witcher 3, encontrado em teste de dois clientes).
- **LobbyCreated chega duas vezes no Steam real:** resultado da chamada `CreateLobby` (703) e callback geral (513). Trate de modo idempotente; uma simulação que envia uma vez não revela isso (teste básico real do retransmissor The Witcher 3).
- **Canais:** dados confiáveis e ordenados no 0. Dados sem sequência ou não confiáveis com `Unreliable` no mesmo canal. Todos acrescentam `NoNagle`. Indicadores: Unreliable 0, NoNagle 1, Reliable 8.
- **Mensagens grandes:** capturas de salvamento/ressincronização divididas em pedaços de 60000 bytes com cabeçalho de 1 byte (inteiro/parte/último), depois remontadas. Eleve `SendBufferSize`, `RecvBufferSize` e `RecvMaxMessageSize` a 32 MB por `SetGlobalConfigValueInt32`. Se envio confiável falhar por buffer cheio, espere cerca de 5 ms e tente novamente.
- **Convites:**
  - Após LobbyCreated, host chama `SetLobbyData` e `SetRichPresence("connect", "+connect_lobby <id>")`, depois `ActivateGameOverlayInviteDialog(lobby)`.
  - Sobreposição pode não abrir em D3D9 antigo (não abriu em Clive Barker's Jericho, mesmo carregada): liste amigos on-line no menu próprio (`GetFriendCount(4)`, `GetFriendByIndex`, `GetFriendPersonaState` != 0), envie `ISteamMatchmaking::InviteUserToLobby(lobby, friend)` para o escolhido; amigo recebe convite normal.
  - Aceitar com jogo ativo gera callback 333.
  - Join Game na lista gera 337 com string de conexão.
  - Sem jogo ativo, Steam o inicia com `+connect_lobby <id>` na linha de comando; interprete isso também.
- **ID da sala:** exiba e copie à área de transferência como alternativa manual (`-steamjoin <id>`).

## <a id="testing-without-two-steam-accounts-the-mock-dll"></a>Testando sem duas contas Steam: DLL simulada

Um PC só executa uma conta Steam; não dá para testar dois jogadores localmente com Steam real. Crie uma simulação: cerca de 400 linhas C compiladas em DLL com mesmo nome e exportações planas (repositório Deus Ex coop fornece uma em `steamlink/mock/`). Ela:

- Simula SteamID pelo argumento `-nick`.
- Passa mensagens entre os dois processos por UDP localhost.
- Simula criação/entrada em salas com IDs determinísticos.
- Como Steam real, retém primeira mensagem de desconhecido até AcceptSession.
- Pode simular convite aceito ou clique Join Game (ambiente `KFX_MOCK_STEAM_INVITE`).

Substitua a `steam_api.dll` real nas duas instalações de teste e execute testes normais de duas instâncias. **Copie a simulação e amplie as exportações conforme o jogo exigir** (HXCoop adicionou chamadas da lista de amigos usadas para encontrar host).

### <a id="unity-mono-games-mock-steamworksnet-not-the-dll"></a>Jogos Unity Mono: simule Steamworks.NET, não a DLL

Se jogo/mod usa Steamworks.NET (invólucro C# gerenciado), dispensa simulação nativa. Plugin BepInEx exclusivo de teste pode alterar o invólucro com Harmony, preservando `steam_api64.dll`. O mod cooperativo Graveyard Keeper (Back From The Grave) foi testado assim: cerca de 1.100 linhas C# na simulação e 300 no transporte.

- **Encontre chamadas:** pesquise no mod `Steam(User|Friends|Matchmaking|Networking|Utils)\.`; prefixo Harmony para cada uma retorna dados falsos e ignora original. Falhe claramente se método não existir.
- **Callbacks:** `Callback<T>` registra com despachante nativo. Prefixe `Callback<T>.Register` e `Unregister` para cada tipo usado, guarde instância e delegado (campo `m_Func`) numa tabela própria e invoque por `Update` na thread principal. Para `CallResult<T>.Set`, assuma só identificadores emitidos pela simulação (comece num valor fixo alto), encaminhando os reais ao Steam.
- **Ordem de carregamento:** patches antes do registro do mod; plugin deve carregar primeiro. GUID que ordena primeiro (`aaa.coopqa`) bastou. Não faça nada sem opção de comando (`-coopqa`).
- **Mantenha Steam real para o restante:** cliente continua conectado, e jogo verifica DLCs e conquistas normalmente. Só simule chamadas multiplayer usadas pelo mod.
- **IDs e transporte:** SteamIDs individuais de faixa reservada (900000000 + número do jogador), IDs de sala do tipo chat. Dados e P2P por TCP localhost, uma porta por jogador.
- **Copie regras usadas pelo mod:** envios não confiáveis acima de 1200 bytes e qualquer envio acima de 1 MB falham; primeiro pacote desconhecido gera `P2PSessionRequest_t`, retido até `AcceptP2PSessionWithUser`; criação dispara `LobbyCreated_t` e `LobbyEnter_t`; entrada dispara `LobbyDataUpdate_t` e `LobbyEnter_t` no convidado, `LobbyChatUpdate_t` nos membros; toda alteração dispara `LobbyDataUpdate_t` em todos; quando proprietário sai, próximo membro assume. Adicione opções de latência extra e perda não confiável.
- **Erro de configuração precisa falhar.** `AccessTools.Method` sem tipos de parâmetros lança exceção em sobrecarga. O plugin parava sem iniciar bot, e o teste só esgotava prazo. Exiba `RESULT: FAIL` para erros e faça inicializador falhar se a cópia não escrever estado.
- **Simulação escolhe ordem de eventos.** A nossa sempre entregava dados da sala antes do primeiro P2P. Isso fez uma corrida falhar em toda entrada: apresentação tardia de compatibilidade prendia transporte ao canal errado. Ordem inversa ocultaria. Onde Steam não promete ordem, acrescente opção para cada uma (ainda não fizemos isso).

## <a id="reusing-it-for-deus-ex-unreal-engine-1-co-op"></a>Reutilizando para Deus Ex (Unreal Engine 1)

KeeperFX tinha camada de rede substituível (`struct NetSP`), permitindo Steam como outra implementação. **UE1 não tem isso.** Usa `UTcpNetDriver` (IpDrv), UDP NetDriver/NetConnection definido em `DeusEx.ini` sob `[Engine.GameEngine] NetworkDevice=` / `[IpDrv.TcpNetDriver]`. Opções:

1. **NetDriver próprio (melhor encaixe):** pacote C++ nativo com `USteamNetDriver` / `USteamNetConnection`, subclasses de `UNetDriver` / `UNetConnection`. `LowLevelSend` vira `SendMessageToUser` (não confiável; UE1 já fornece confiabilidade); `TickDispatch` esvazia `ReceiveMessagesOnChannel` para `ReceivedRawPacket`. Aponte `NetworkDevice` no INI. Mapeie host da URL para SteamID, como `open steam.76561198xxxxxxxxx`, ou ID da sala. Exige cabeçalhos públicos UE1 (SDK Deus Ex / UT432) e compilação compatível MSVC 6, pois motor é MSVC de 32 bits.
2. **Proxy UDP local (sem código do motor):** pequeno executável auxiliar ou DLL com o jogo. Vincula 127.0.0.1:7790 no cliente e fala com host por Steam P2P. Host encaminha à porta real. O jogo faz `open 127.0.0.1`. Caminho mais rápido para algo funcionar; mesma ideia da DLL simulada invertida.

Nos dois casos, reutilize diretamente carregamento dinâmico, despacho manual, fluxo de sala/convites, regra de aceite, sinais e prazo e DLL simulada. Como UE1 tem confiabilidade própria, Unreliable em tudo costuma ser correto. Divisão em 60000 bytes provavelmente desnecessária: pacotes UE1 têm cerca de 512 bytes.

## <a id="finding-the-host-without-codes"></a>Encontrando host sem códigos

Convidado HXCoop dispensa ID de sala: percorre amigos (`GetFriendCount` / `GetFriendByIndex`, indicador 4 = amigos imediatos) e chama `GetFriendGamePlayed`. Amigo com AppID 480 nos 24 bits inferiores de `FriendGameInfo_t.m_gameID` e `m_steamIDLobby` não zero (deslocamento 16) está hospedando. Entre e confira chave própria (`hxcoop=1`) para não entrar no Spacewar real.

## <a id="a-relay-instead-of-engine-code-hxcoop-pattern"></a>Retransmissor em vez de código do motor (padrão HXCoop)

- Host: socket UDP local por jogador remoto, com `connect()` à porta do jogo em 127.0.0.1. Mensagens Steam do jogador saem por seu socket; respostas voltam ao mesmo jogador. Jogo vê clientes 127.0.0.1 separados.
- Cliente: vincule 127.0.0.1 em porta livre, inicie jogo conectado a ela, encaminhe tudo ao SteamID do host.
- Pacotes do jogo não confiáveis com NoNagle (motor já garante confiabilidade). Sinais e despedida confiáveis no canal 1.
- **Só membros da sala passam.** Antes de encaminhar novo participante ao servidor local, confira SteamID na sala (`GetNumLobbyMembers` / `GetLobbyMemberByIndex`) e descarte outros. Adicione as duas exportações à simulação.
- Saia ao encerrar o jogo, deixe sala e limpe presença detalhada.
- Simulação de atraso/perda do próprio motor (UE1 possui comandos `PktLag=`, `PktLoss=`, `PktOrder=`, `PktDup=`) substitui economicamente latência do retransmissor nos testes.

## <a id="tcp-games-a-stream-relay"></a>Jogos TCP: retransmissão de fluxos

O padrão acima é UDP. Para TCP (muitos ports e jogos em rede de emuladores), retransmita fluxos:

- Dê a cada conexão **ID de fluxo**, envie pequenos quadros Steam: `open(id)`, `data(id, bytes)`, `close(id)`.
- Envie **confiável e ordenado**, como TCP exige, em blocos de cerca de 16000 bytes.
- Se envio confiável falhar por buffer cheio, espere alguns ms e repita; nunca descarte dados do fluxo.
- Propague fechamento nos dois sentidos: socket local fechado envia `close(id)`; `close(id)` remoto fecha socket local. Caso contrário, um lado fica preso à conexão semiaberta.
- Host abre conexão TCP ao servidor por ID remoto, como UDP abre socket por jogador.

## <a id="writing-the-helper-exe-gotchas"></a>Escrevendo o executável auxiliar: armadilhas

- Se outra ferramenta o inicia com saída redirecionada, chame `setvbuf(stdout, NULL, _IONBF, 0)`; caso contrário, log chega tarde ou nunca.
- Confira se stdin é console antes de `_kbhit` / `_getch` em menu; com redirecionamento, comportam-se mal.
- Ao iniciar servidor local como filho, use `CREATE_NEW_PROCESS_GROUP` e encerre com Ctrl+Break (`GenerateConsoleCtrlEvent`) para saída normal; coloque em objeto de trabalho que encerra ao fechar, evitando sobreviver ao auxiliar.
- Macros: `__declspec(dllexport)` e `__cdecl` na ordem aceita por mingw podem falhar no MSVC. Teste DLL simulada com ambos se suportar os dois.

## <a id="packaging-and-status"></a>Empacotamento e estado

- Distribua `steam_api.dll` (ou `steam_api64.dll`) junto ao auxiliar e faça-o escrever `steam_appid.txt` (`480`), evitando falha por ausência.
- Linha de estado honesta e específica: diga se tráfego real já passou (não só conectado ao Steam); se alguém entra em sala alheia (chave ausente), informe claramente que não é uma sala cooperativa de <game>.

## <a id="status--unknowns"></a>Estado / desconhecidos

- Todos os testes simulados passam com 0 dessincronizações: jogo na fase, campanha de 3 fases, progressão, desconexões normais/forçadas e ambos os convites. Regressão ENet também passa.
- Teste real Steam de uma instância passou:
  - `InitFlat` funcionou, criação retornou ID.
  - ID exibido e copiado à área de transferência.

  `ActivateGameOverlayInviteDialog` retorna void, sem valor de sucesso; ninguém viu a sobreposição.
- Jogo real com duas contas (Clive Barker's Jericho, 2026-10-21, dois PCs na mesma LAN, contas amigas):
  - Remetente em **12**, não 16; com 16 ninguém entrava.
  - Corrigido, amigo entra pela lista de partidas no jogo e sessão funciona (sala, fase, mundo), ida e volta 6-19 ms.
  - Convite da sobreposição não abriu em D3D9: `InviteUserToLobby` pela lista própria (acima).
  - Teste por script com duas contas (host lê ID do log num PC; outro entra pelo ID) agora roda em toda regressão.
  Pendentes: início automático por Join Game sem jogo aberto e dois PCs em redes diferentes (retransmissor, não LAN).
- HXCoop: testes passam por simulação com clientes reais retransmitidos. Para duas contas reais, confira primeiro o deslocamento do remetente.
