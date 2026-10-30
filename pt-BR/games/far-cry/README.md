# <a id="far-cry-2004"></a>Far Cry (2004)

| | |
|---|---|
| Motor | CryEngine 1, x86 de 32 bits. Lógica em `CryGame.dll` (C++, código-fonte no MOD SDK 1.4 oficial) e scripts Lua 4 em `FCData\Scripts.pak` |
| Versões testadas | Steam, app id 13520, versão 1.4.0.1405. `Bin32\FarCry.exe` SHA-256 `21a907fae0b6e2d4b10d546dba0965ef89c39a69f8cb00036307c0564ca1a813`, `CryGame.dll` SHA-256 `db9c7660b698600ae34dd4a18f7ca5989911ad51bf9286ba1cc047ae52ef7634` (timestamp PE `0x44e2f64d`). Todos os endereços abaixo correspondem a essa `CryGame.dll` |
| Projetos | [FarCryCoop](https://github.com/Bantila/FarCryCoop/tree/main) (novo, este relato; MIT); [Assault Coop](https://www.moddb.com/mods/assault-coop) (2011); [FCAV](https://farcry1.itch.io/far-cry-advanced-version) (cooperativo anunciado, não distribuído) |
| Nível de QA | none (FarCryCoop: dois jogadores verificados manualmente pelo autor, sem teste automatizado); community-reports (Assault Coop) |
| Última atualização | 2026-10-22 |

## <a id="where-things-stand"></a>Situação atual

FarCryCoop (0.2 beta, iniciado em 2026-10-18) executa os mapas originais da campanha como jogo em rede. O host executa um servidor e joga como no modo de um jogador; amigos entram como clientes. Movimento, armas, acertos nos inimigos, IA dos inimigos, gatilhos de área, objetivos, mudanças de mapa e reaparecimento após a morte funcionam para dois jogadores. O host também tem salvamentos da campanha (automático em checkpoint, comandos de salvar e carregar, F6 / F7 não testados, carregamento de salvamento após nova inicialização); preservam jogadores e inimigos mortos, mas não o progresso da missão. O inicializador lista mapas na ordem da história e define a dificuldade (os cinco níveis do menu de um jogador). Ainda faltam:
- helicópteros para clientes;
- empurrar objetos físicos;
- cenas para clientes;
- progresso das missões nos salvamentos;
- voo fluido do parapente visto pelos outros jogadores.

A campanha completa não foi concluída. Uma varredura das 20 fases (dois jogos em um PC, mudanças de mapa, saltos por até 4 checkpoints por fase) encontrou:
- 18 fases carregaram inicialmente; **Treehouse e Swamp falharam durante o carregamento** (`CRITICAL ERROR:: ReadPacked i== 20`, [#1](https://github.com/Bantila/FarCryCoop/issues/1), agora contornado: tabela abaixo); após a solução alternativa, todas as 20 carregam, e Treehouse, Swamp, Factory, Dam e Volcano foram verificadas novamente com saltos funcionais entre checkpoints;
- uma mudança de fase **às vezes derruba o host** (corrupção aleatória de heap em `CrySystem.dll`: Bunker -> Steam em 3 de 11 execuções, Cooler -> Boat em 4 de 25, [#2](https://github.com/Bantila/FarCryCoop/issues/2)); a perda de um cliente em Cooler -> Boat ocorreu uma vez e não se repetiu;
- em 9 fases (Training, Carrier, Fort, Research, Bunker, Regulator, Rebellion, Archive, Cooler), os dois ficaram no mesmo lugar após cada salto de checkpoint; em Control, Pier e Fort, o cliente às vezes chegou atrasado ou longe ([#3](https://github.com/Bantila/FarCryCoop/issues/3), fechada: o servidor agora acompanha o deslocamento remoto e o reenvia até o jogador chegar).

**Implementados, mas não testados no jogo:** entrada pelo Steam ("Join Game" do Spacewar), sala do inicializador, cores das camisas dos jogadores e teclas de salvamento F6 / F7. Tudo que se diz abaixo sobre eles descreve a intenção do código, não funcionamento observado.

## <a id="existing-work"></a>Trabalhos existentes

| Projeto | Escopo | Rede | Evidências e limites |
|---|---|---|---|
| [Assault Coop](https://www.moddb.com/mods/assault-coop) v3.0 (2011) | cerca de 7 mapas de campanha reeditados para modo cooperativo, IA aleatorizada | LAN / IP direto | Jogadores relatam missões inacabadas e cenas ausentes. O autor proíbe reutilizar os scripts sem autorização. FarCryCoop aproveitou apenas uma ideia (retransmissão cliente de gatilhos de área), abandonada depois. |
| [FCAV](https://farcry1.itch.io/far-cry-advanced-version) | mod de patches e correções; cooperativo em desenvolvimento | unknown | não distribuído |
| [FarCryCoop](https://github.com/Bantila/FarCryCoop/tree/main) | mapas originais da campanha, em princípio todas as missões, 2 a 4 jogadores (2 testados) | IP direto, VPN; retransmissor Steam Spacewar e sala do inicializador por TCP (ambos não testados) | relatos e todos os endereços em seu `games/far-cry/NOTES.md` |

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

Observações das notas FarCryCoop, cada uma verificada no jogo ou nos logs:

- O modo de um jogador já usa servidor local e cliente local. `Scripts\Default\gamerules.lua` (regras de um jogador) trata `OnClientConnect`, `OnClientDisconnect` e `RespawnPlayer` por posição do servidor.
- O tipo de jogo é a global Lua `g_GameType`. Um mapa de campanha inicia como servidor de rede com `Game:LoadLevelListen` (o host mantém um jogador local) ou `Game:LoadLevelMPServer`. Uma segunda chamada de `LoadLevelMPServer` muda o mapa e mantém os clientes conectados.
- Mods ficam em `<game dir>\Mods\<name>\`, com `.pak` próprio que substitui scripts. Inicie com `FarCry.exe -DEVMODE -MOD:<name>`; comandos Lua de console `#` exigem `-DEVMODE`.
- Um tipo personalizado (`COOP`) pode simplesmente carregar e ampliar as regras de um jogador. Cliente para servidor: `Client:SendCommand` -> `GameRules:OnClientCmd`. Servidor para cliente: `server_slot:SendCommand` / `Server:BroadcastCommand` -> `ClientStuff.ServerCommandTable`.
- **Limite de snapshot:** CryNetwork reúne os dados não confiáveis de um quadro em `CStream`, com buffer fixo de 1124 bytes (8992 bits), descartando silenciosamente escritas excedentes. Um mapa de campanha tem cerca de 650 entidades de rede; perdia-se cerca de 40% de cada snapshot. O próprio jogador ficava no fim da lista e nunca chegava ao cliente.
- **Gatilhos de área** (`AreaTrigger` e outras áreas geométricas) só disparam para o jogador da própria máquina: `CPlayer::Update` executa `m_XAreaMgr.UpdatePlayer` apenas quando `IsMyPlayer()`.
- **IA em servidor dedicado** fica adormecida até ser despertada (`AIEVENT_WAKEUP`). Nunca recebe eventos de animação, porque animações de personagens não avançam sem renderização; ataques corpo a corpo (`KEYFRAME_APPLY_MELEE`) e saltos da IA nunca acontecem.
- **Presença de rede:** entidades da fase surgem com `netPresence = false`. Só jogadores, IA e classes de veículos são enviados. Helicópteros (`Gunship`) não pertencem a uma classe de veículo.
- **Cor do jogador:** a cor da equipe multiplayer usa um segundo shader, `PlayerMaskModulate` (efeito 2, ligado pelo comando de servidor `"FX"`), e exige o modelo `hero_mp.cgf`; o `hero.cgf` de um jogador não tem máscara de cor.
- **Salvamentos:** `CXGame::Save` e `LoadFromStream` retornam antes de completar no multiplayer, e salvar exige um jogador cliente local. Um checkpoint (`GameEvent`) chama `Game:OnAfterSave` depois de definir `_LastCheckPPos`.

## <a id="what-we-changed"></a>O que alteramos

FarCryCoop nunca substitui arquivos do jogo. Tem três partes:
- um pak de mod Lua (tipo de jogo `COOP`);
- um plugin ASI (`FarCryCoopNet.asi`, carregado pelo Ultimate ASI Loader) que aplica hooks por endereço em `CryGame.dll` 1.4;
- um inicializador.

Os endereços foram encontrados com Ghidra (por REA) e conferidos no código do MOD SDK 1.4. Uma `CryGame.dll` recompilada do SDK foi experimentada e rejeitada: precisa de VC 7.1 com STLport do SDK, pois strings STLport atravessam todas as interfaces do motor.

| Bug | Causa raiz | Correção | Como foi verificado |
|---|---|---|---|
| Jogador remoto congelado, sem arma, recarga interminável | cauda do snapshot após 8992 bits descartada | ASI: ordenar `m_lstNetEntities` por prioridade × idade antes de `CXSnapshot::BuildAndSendSnapshot` (`0x3306faba`); hook em `CXServerSlot::SendUnreliableMsg` (`0x3306c620`) e adiamento de atualizações após o orçamento de 8800 bits, priorizando-as na próxima vez | cliente recebe 100% das atualizações enviadas (contadores ASI), próprio jogador com 16 a 17 atualizações/s, posições iguais |
| Missões param em objetivos de alcançar um local | gatilhos só para o próprio jogador | ASI: o `je` em `0x330ae17e` de `CPlayer::Update` salta para código auxiliar. Para remotos no servidor, executa `CXAreaMgr::UpdatePlayer` (`0x330d3ee8`) | monitor registra `AreaTrigger80 Empty->Occupied` quando o cliente entra |
| Inimigos parados no servidor dedicado | representantes adormecidos | Lua: despertar representantes a até 150 m de qualquer jogador uma vez por segundo; os com `bSleepOnSpawn` a até 40 m ou ao receber tiro | comportamentos e alvos da IA no log; inimigos combatem |
| Corpo a corpo da IA nunca acerta | ausência de eventos de animação no servidor dedicado | Lua: em `OnCloseContact`, executar o manipulador do quadro-chave de ataque 0,35 s depois; enviar animação do golpe aos clientes | mutantes atingem e matam; golpe visível no cliente |
| Servidor dedicado falha em cenas | `CMovieUser` e chaves de som CryMovie chamam sistema de entrada / som NULL | ASI: ignorar quando NULL; Lua: `mov_NoCutscenes 1` no servidor dedicado | Training carrega e é jogável |
| Acertos remotos não registrados | causa raiz não identificada | Lua: acertos no cliente (`CHIT`), aplicados pelo servidor com `target:Damage` | verificação do servidor com acerto simulado; autor confirmou no jogo |
| Checkpoints nunca definidos no servidor | `GameEvent:OnTimer` lê `_localplayer` (nil) | Lua: executar com o jogador mais próximo como `_localplayer` | evento no monitor; não observado em todos os mapas |
| Cliente continua planando após o servidor soltá-lo | parapente sem `OnUnBind` cliente | Lua: servidor transmite `VEHOUT`, cliente libera o assento | conferido no jogo |
| Servidor dedicado com apenas 17 snapshots/s | `Sleep` na resolução de temporizador de 15,6 ms | ASI: `timeBeginPeriod(1)` em `FarCry_WinSV` | 35 a 36 snapshots/s |
| Barris empurrados não se movem nos clientes | sem presença de rede | ASI: atribuir presença de rede a `RigidBody` / `DestroyableObject` / `BasicEntity` após movimento no servidor | nenhum erro de pacotes cliente, reaparecimento continua funcional |
| Teclas não funcionam no layout russo | CryInput cria tabela por `GetKeyboardLayout(0)` | ASI: hook antes de CryInput carregar, retornar layout dos EUA | teclas funcionam com layout russo |
| Sem salvamentos em rede | `CXGame::Save` e `LoadFromStream` retornam cedo no multiplayer | Lua, só host: arquivo `Mods\FarCryCoop\save_<name>.lua` com mapa, posição/vida/armadura/armas/munição de cada jogador, IDs da IA morta e ponto de reaparecimento. `Game:OnAfterSave` salva automaticamente no checkpoint. Carregar recarrega mapa com `LoadLevelMPServer`, remove IA morta e reposiciona jogadores | Pier, dois jogos em um PC: salvar, mover ambos 60 m, carregar: ambos voltam ao local salvo; checkpoint grava `save_auto.lua`; início pela entrada `save:<name>` do inicializador coloca ambos no local salvo. F6 / F7 e menu de um jogador "Load Game" não testados ou não conectados |
| Helicópteros parados nos clientes | entidades sem presença de rede, helicóptero voando no host não enviado | ASI: `Gunship` ou `CargoChopper` recebe presença de rede ao mover no servidor e passa a todo snapshot | Pier: host moveu dois helicópteros 40 m, cliente no mesmo local na primeira verificação (diferença 0 m, 28 s). Helicóptero ainda não movido paira de 8 a 34 m mais alto no cliente. Voo real de missão (chefe de Boat) não observado |
| Treehouse e Swamp: falha no carregamento (`ReadPacked i== 20`) | arquivo da fase incorpora estado físico como texto em entidades (Treehouse: entidade 410, `BasicEntity`); `SetStateFromSnapshotTxt` converte em fluxo, leitor do corpo rígido encontra 20 partes onde permite 16. Ignorar erro só desloca a falha | ASI: hook em `SetStateFromSnapshot` do corpo rígido (`CryPhysics.dll` RVA `0x9c9b0`) ignora chamada originada por `SetStateFromSnapshotTxt` em jogo que executou linha `CoopMap(`, `CoopLoad(` ou `Game:Connect(` | Treehouse, Swamp, Factory, Dam e Volcano carregaram nos dois jogos e 3 saltos de checkpoint funcionaram em cada (cliente atrasado no checkpoint 4 de Swamp e 3 de Volcano, [#3](https://github.com/Bantila/FarCryCoop/issues/3)). Desconhecidos: por que o texto não cabe, aparência no jogo dos estados ignorados, outras fases com estados incorporados |
| Todos os jogadores brancos | criação de um jogador sem cor, modelo sem máscara | Lua: servidor envia `PCOLOR`; clientes carregam `hero_mp.cgf`, ativam `PlayerMaskModulate` e envolvem `UpdatePlayerEffectParams` | não testado no jogo |

Entrada na sessão:
- **Ponte Steam (não testada com um amigo real).** Segue [playbook/networking-steam-spacewar.md](../../playbook/networking-steam-spacewar.md): executável de console como Spacewar, `SteamNetworkingMessages` e retransmissor UDP para `127.0.0.1:49011`. O ASI executa uma linha de `Mods\FarCryCoop\join.txt` por `IConsole::ExecuteString`, vtable `+0x80`; `+0x84` é Exit. Verificado em um PC: com `-loop`, um segundo jogo entrou pelo túnel e ficou ao lado do host; com Steam real, a ponte inicia como Spacewar e define presença "connect" quando o servidor fica ativo. A entrada real de um amigo (segunda conta Steam em outro PC) não foi testada.
- **Inicializador:** Rust e Tauri. "Test on one PC" e início por salvamento foram executados no jogo. A sala TCP (não testada no jogo) deve mostrar nomes, cores de camisas e equipamentos antes do início.

## <a id="qa"></a>QA

Nenhum automatizado. Um monitor Lua (`coop_monitor 1`) registra jogadores, IA próxima, veículos e eventos a cada segundo no servidor e cliente. Uma comparação PowerShell lista entidades congeladas, deslocadas ou diferentes no cliente. É auxílio de depuração, não teste com asserções. Todas as afirmações de funcionamento acima, salvo itens marcados não testados (entrada Steam, sala do inicializador, cores de camisas, F6 / F7), foram verificadas com duas instâncias (um PC, host e cliente), não com suíte. Verificações de salvamento, dificuldade, helicópteros e varredura de fases foram controladas por linhas de console enviadas aos jogos, não manualmente; a varredura é um script do autor, não uma suíte de testes.

## <a id="how-to-play"></a>Como jogar

Consulte [INSTALL.md](https://github.com/Bantila/FarCryCoop/blob/main/games/far-cry/release/INSTALL.md). Cada jogador precisa de Far Cry 1.4 e da mesma versão do mod:
1. Copie `Mods`, `Bin32` e o inicializador para `<game dir>`.
2. O host cria a sala e pressiona Start.
3. Amigos entram pela sala (IP direto ou VPN) ou por "Join Game" na lista Steam.

Salvamentos (host): checkpoint salva automaticamente, F6 salva, F7 carrega e um salvamento escolhido na lista de mapas do inicializador continua após reiniciar.

Somente IP direto / VPN pelo console foi verificado manualmente. Sala do inicializador, cores de camisas e "Join Game" do Steam **não foram testados** (INSTALL.md os lista como itens a testar).

## <a id="known-issues"></a>Problemas conhecidos

- Helicópteros: o cliente acompanha após movimento no host; antes disso, pairam até 34 m acima. Voo real de missão (chefe de Boat) não observado.
- **Mudar de fase às vezes derruba o host** (corrupção aleatória de heap; vista em Bunker -> Steam e Cooler -> Boat, [#2](https://github.com/Bantila/FarCryCoop/issues/2)). Treehouse e Swamp só carregam porque o ASI ignora o estado físico incorporado a algumas entidades no jogo cooperativo; esses objetos começam onde a fase os coloca, e sua aparência no jogo não foi observada ([#1](https://github.com/Bantila/FarCryCoop/issues/1), fechada).
- Corrigidos após a varredura: cliente que perdeu um deslocamento é movido novamente pelo servidor, inclusive após cair através do chão ([#3](https://github.com/Bantila/FarCryCoop/issues/3)); erro de conversa da IA em Bunker protegido ([#4](https://github.com/Bantila/FarCryCoop/issues/4)). Em aberto: veículos com menos assentos que jogadores, como Swamp e buggies ([#5](https://github.com/Bantila/FarCryCoop/issues/5)).
- Jogador conectado não consegue empurrar barris ou caixas.
- Clientes não veem cenas.
- A fase tem um parapente: agora surge uma cópia para cada jogador adicional; para os demais, um planador subindo parece cair.
- Salvamentos guardam só jogadores e inimigos mortos. Após carregar, o script da missão recomeça do início do mapa; gatilhos, itens coletáveis e veículos não são salvos.
- No servidor dedicado, IA nunca salta; inimigos podem se mover em pequenos solavancos nos clientes.
- Comandos curtos de console (`coop_map pier`) não fazem nada no cliente do jogo; `#CoopMap("pier")` funciona.

## <a id="next-steps"></a>Próximos passos

- Localizar a falha aleatória na mudança de fase e repetir a varredura das 20 em uma execução.
- Teste de dois clientes por script que verifique estado de jogadores, IA e missão (comparação do monitor e script da varredura são um começo).
- Voo real de helicóptero e parapente visto por clientes.
- Salvar progresso de missão (gatilhos, objetivos, coletas) ou usar salvamentos reais do motor no host: contornar verificações multiplayer de `CXGame::Save`.
- Saltos da IA no servidor dedicado: exigem eventos de animação sem renderização.
- Entrada sem Steam ou VPN (código de entrada, abertura coordenada de portas UDP, retransmissão), como faz o mod cooperativo de Crysis.
