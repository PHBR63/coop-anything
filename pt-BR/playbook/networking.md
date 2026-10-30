# <a id="networking-for-co-op-mods"></a>Rede para mods cooperativos

Como escolher modelo de sincronização, transporte e forma de conectar jogadores ao adicionar modo cooperativo a um jogo de um jogador. Leia antes de projetar; depois consulte [networking-steam-spacewar.md](networking-steam-spacewar.md) para a implementação Steam.

Convenções: toda afirmação concreta tem link. **(não verificado)** indica ausência de fonte confirmatória, ou apenas fonte fraca. **(avaliação)** indica orientação dos autores do guia, não de fonte citada. Confira as licenças antes de distribuir; a coluna de licença reproduz o informado na página do repositório de cada projeto.

## <a id="0-quick-decisions"></a>0. Decisões rápidas

| Pergunta | Padrão | Alternativa |
|---|---|---|
| Modelo de sincronização | Estado com autoridade do host, algumas coisas sob controle do cliente (próprio jogador, câmera) | Lockstep só se motor já determinístico (seção 1) |
| Transporte, rede própria | ENet (C/C++) ou LiteNetLib (C#) para UDP | GameNetworkingSockets para criptografia, ICE e retransmissão Steam numa biblioteca |
| Conectar um amigo | Retransmissão Steam (ISteamNetworkingMessages), veja página Spacewar | Rede sobreposta Tailscale/ZeroTier, depois redirecionamento ou UPnP |
| Código de rede existente, fechado | Proxy UDP local em túnel Steam (seção 4) | NetDriver próprio ou hook no motor |
| Testes | DLL Steam simulada num PC, mais clumsy ou netem para conexões ruins | Simulação do motor (PktLag, PktLoss) |

## <a id="1-sync-models"></a>1. Modelos de sincronização

### <a id="11-the-models"></a>1.1 Os modelos

| Modelo | O que trafega | Quando serve para um mod | Compromissos |
|---|---|---|---|
| Lockstep determinístico | Somente entradas | Motor já determinístico bit a bit (simulação própria, passo fixo, gerador aleatório com semente) | Pouca largura de banda, proporcional à entrada, não ao número de objetos; porém todos precisam produzir resultados idênticos, e ponto flutuante varia entre compiladores, sistemas e instruções. [Gaffer On Games](https://gafferongames.com/post/deterministic_lockstep/) chama garantir isso de quase impossível e diz que seu exemplo fixo só funcionou numa máquina, binário e sistema. Mod não controla temporização do motor; raramente realista. |
| Estado com autoridade do host | Estado dos objetos, com prioridades | Maioria dos jogos de um jogador: cópia host é a verdade | Ambos simulam, host envia correções; resultado aproximado, exigindo combater divergência de extrapolação e saltos ([Gaffer On Games: sincronização de estado](https://gafferongames.com/post/state_synchronization/)). Exige hook de leitura/escrita para cada campo. |
| Interpolação de capturas | Capturas completas; clientes só renderizam | Simulações não determinísticas, física simples, representantes de jogadores/NPCs | Mais banda e atraso de interpolação: cerca de 350 ms a 10 capturas/s, 150 ms a 30/s, 85 ms a 60/s segundo [Gaffer On Games](https://gafferongames.com/post/snapshot_interpolation/). Boa para avatares remotos mesmo com resto baseado em eventos. |
| Autoridade cliente com arbitragem host | Cliente envia estado próprio; host aceita ou veta | Cooperativo entre amigos sem preocupação com trapaça | Mais simples: personagem, câmera e golpes próprios simulados localmente, sem previsão. Host arbitra missões, itens, portas. **(avaliação)** |
| Rollback (estilo GGPO) | Entradas com previsão e ressimulação | Luta e pequenas simulações determinísticas | Exige salvar/carregar todo o estado por quadro e determinismo; [GGPO](https://github.com/pond3r/ggpo) (MIT) é SDK de referência. Irrealista num jogo moderno grande fora do seu controle. |

Prova existente de que sincronizar só jogadores é escopo válido: a wiki HKMP diz sincronizar apenas jogadores e movimentos; inimigos, itens e objetos quebráveis permanecem separados por jogador (resumo por [resultado de busca](https://github.com/Extremelyd1/HKMP), veja também [wiki comunitária](https://geroyuni.notion.site/hkmp)). **(não verificado: texto da wiki visto apenas em resumo de busca.)**

### <a id="12-techniques-that-apply-to-any-model"></a>1.2 Técnicas aplicáveis a qualquer modelo

| Técnica | Definição | Fonte / nota |
|---|---|---|
| Quantização | Menos bits: quaternions pelo método dos três menores (29 contra 128 bits), posições com cerca de 2 mm (50 contra 96 bits) | [Compressão de capturas](https://gafferongames.com/post/snapshot_compression/) |
| Compressão de diferenças | Codificar contra uma base confirmada pelo receptor; objetos inalterados custam um bit | [Compressão de capturas](https://gafferongames.com/post/snapshot_compression/) |
| Acumulador de prioridades | A cada quadro, acrescentar prioridade ao acumulador de cada objeto, enviar os maiores que couberem, zerar os enviados | [Sincronização de estado](https://gafferongames.com/post/state_synchronization/) |
| Gerenciamento de interesse | Só enviar objetos próximos ou na mesma célula/fase | Prática comum **(avaliação)**; em cooperativo de 2-4 normalmente desnecessário, salvo mundos grandes com centenas de NPCs. |
| Confiável e não confiável | Posições não confiáveis (antigas são inúteis), eventos confiáveis | [Documentação Steam Messages](https://partner.steamgames.com/doc/api/ISteamNetworkingMessages) descreve ambos; orientação estilo Nitrox recomenda confiável só para eventos críticos raros, nunca confiável ordenado para movimento ([documento Nitrox de terceiros](https://www.mintlify.com/Papela/Nitrox-Cracked-Mod/development/networking), **documentação de fork não verificada**) |
| Marcas de envio e atraso adaptativo | Marcar cada pacote com relógio de alta resolução do remetente. Receptor mantém cerca de 32 capturas e mostra tempo do remetente menos atraso, interpolando posição/direção entre capturas adjacentes. Atraso = percentil 90 do atraso dos pacotes (contra mais rápido dos últimos cerca de 2 s) + intervalo de envio, limitado a 20..200 ms, variando lentamente. Em grandes saltos (teleportes, portas), reposicionar sem interpolar | Obscure (games/obscure): adotar pacote mais recente era suave num PC, mas engasgava no Steam (RTT 62..78 ms, picos 500 ms); corrigido para jogadores em 1.1 e inimigos em 1.7 (verificado jogando por Steam, sem captura de pacotes) |
| Envio fixo, não por quadro | Enviar em relógio 60 Hz; taxa por quadro cresce com quadros ilimitados | Obscure: cerca de 275 fps resultavam em cerca de 600 pacotes/s no Steam ao enviar a cada 2 quadros |

### <a id="13-what-to-sync-for-story-co-op"></a>1.3 O que sincronizar para história cooperativa

Isso determina se o mod parece cooperativo. Ordem de prioridade, do barato ao difícil. **(avaliação)**, salvo links.

| Camada | Abordagem | Notas |
|---|---|---|
| Avatar | Autoridade cliente, interpolação nos parceiros | Posição, rotação, animação, aparência de equipamentos |
| Autoridade de NPCs/inimigos | Um responsável, host ou jogador próximo, com transferência | Notas TiltedEvolution listam transferência de NPCs e sincronização de NPCs nivelados ([v1.8.1](https://newreleases.io/project/github/tiltedphoques/TiltedEvolution/release/v1.8.1)) |
| Combate/dano | Cliente atacante relata golpe, responsável pelo alvo aplica | Evitar duplicação: ID por golpe |
| Objetos do mundo | Host decide portas, contêineres, coletas e transmite resultado | IDs estáveis (form IDs, fase+índice), nunca endereços |
| Indicadores de missão/história | Host controla; espelhar escritas | Hook na função única de definir variável/indicador, se existir: o mais valioso. Missões sem sincronização são principal fracasso dos mods existentes |
| Diálogo/cenas | Um conduz, demais observam; exigir presença de todos | Área mais difícil; decidir por jogo se pausa para todos ou só executa para quem aciona |
| Inventário, ouro, XP | Individual por padrão; conjunto compartilhado só se desejado | Compartilhamento exige arbitragem host |
| Tempo, clima, aleatoriedade | Host transmite, clientes adotam | |

Casos simples valem distribuição isolada. O código do cliente Anchor de Ship of Harkinian mostra sala com ID de responsável e opções de itens/indicadores ([trecho](https://code.moparisthebest.com/mirror/Shipwright/commit/060878fb2e75c5c2dbbea325169671cf3f9f122f)); sincronizar indicadores é uma opção, não reescrita.

### <a id="14-late-join-level-changes-and-saves"></a>1.4 Entrada tardia, fases e salvamentos

Tudo **(avaliação)** salvo links.

- **Entrada tardia:** host envia captura completa (indicadores, missões, entidades) e passa a diferenças. Anchor solicita estado da equipe logo após carregar um salvamento ([trecho](https://code.moparisthebest.com/mirror/Shipwright/commit/060878fb2e75c5c2dbbea325169671cf3f9f122f)).
- **Transições:** mudar fase não pode destruir estado dos outros. Mantenha todos juntos (seguir líder) ou acompanhe ID de fase por entidade e aplique só atualizações da fase carregada.
- **Carregar durante sessão:** encontre ponto único de solicitação (Obscure: menu lê slot, muda máquina de estados para carregar; escrita única no executável). Host detecta e envia comando com transferência correspondente; convidado espera arquivo em disco e executa os dois passos. Entrada pode usar mesmo caminho, sem escolha manual (games/obscure).
- **Salvamentos:** host como verdade; convidados recebem estado ao conectar. Salvar no cliente não faz nada ou usa slot local separado. Teste salvar, sair e carregar conectado.
- **Reconexão após mapa:** jogos que reconectam a cada mudança precisam ID de conexão para reconhecer mesmo jogador (seção 4).
- **Mensagens grandes:** capturas exigem fragmentação; Steam Messages fragmenta com limites (página Spacewar divide em 60000 bytes e aumenta buffers).

## <a id="2-transports-and-libraries"></a>2. Transportes e bibliotecas

| Biblioteca | Linguagem | Licença | Confiabilidade / extras | Mods usuários segundo fontes |
|---|---|---|---|---|
| [ENet](https://github.com/lsalzman/enet) | C | MIT | UDP confiável, canais | KeeperFX testa regressão ENet e Steam ([página Spacewar](networking-steam-spacewar.md)); demais **não verificados** |
| [GameNetworkingSockets](https://github.com/valvesoftware/GameNetworkingSockets) | C++ (API C, vínculos C#, Go, Rust) | BSD-3-Clause | Confiável/não confiável, fragmentação, AES-GCM-256, P2P ICE com sinalização própria, SDR só Steam | TiltedConnect de TiltedPhoques envolve biblioteca de rede sem nomeá-la ([README](https://raw.githubusercontent.com/TiltedPhoques/TiltedConnect/master/README.md)); **uso GNS em Skyrim Together não verificado** |
| Steam Networking Messages / Sockets | API C por `steam_api.dll` | Termos Steamworks SDK | P2P sem sessão por SteamID, retransmissão Valve (SDR) | KeeperFX net_steam, HXCoop ([Spacewar](networking-steam-spacewar.md)); SSMP Silksong declara suporte Steam completo ([SSMP](https://github.com/Extremelyd1/SSMP)); Elden Ring Seamless usa matchmaking Steam e bloqueia serviço FromSoftware ([guia por busca](https://www.exitlag.com/blog/elden-ring-seamless-co-op/), **não verificado no fonte**) |
| [Epic Online Services P2P](https://dev.epicgames.com/docs/) | SDK C | Termos EOS SDK | Travessia NAT e retransmissão alternativa, ID de conta, gratuito; servidor dedicado não recebe por P2P por não fazer login ([Redpoint](https://docs.redpoint.games/docs/setup/networking/p2p_vs_ip), [Edgegap](https://edgegap.com/blog/can-epic-online-services-eos-relays-allow-for-dedicated-server-or-authoritative-server)) | Nenhum mod conhecido **(não verificado)**; para jogos Epic ou independência de loja |
| [LiteNetLib](https://github.com/RevenantX/LiteNetLib) | C# | MIT | Modos confiáveis, fragmentação, travessia NAT UDP, simulação de perda/latência, Unity/Godot/MonoGame | Nitrox dependente segundo [NuGet](https://www.nuget.org/packages/LiteNetLib/) (Nitrox GPL-3.0, [repositório](https://github.com/SubnauticaNitrox/Nitrox)) |
| Lidgren.Network | C# | MIT segundo repositório **(não verificado, não consultado)** | UDP confiável | Unity/XNA antigos; fonte não conferido |
| [SLikeNet](https://github.com/SLikeSoft/SLikeNet) (fork RakNet) | C++ | Código aberto derivado RakNet, termos por componente no repositório | Plugins cliente/servidor de travessia NAT, exemplo UPnP; RakNet descontinuado | Uso RakNet em mods **(não verificado)** |
| [yojimbo](https://github.com/mas-bandwidth/yojimbo) | C++ | BSD-3-Clause | Cliente/servidor, tokens de conexão, UDP criptografado, mensagens confiáveis ordenadas/não confiáveis, até 100 jogadores | Nenhum mod encontrado; destinado a servidores dedicados, não P2P |
| [Riptide](https://github.com/RiptideNetworking/Riptide) | C# | MIT | UDP/TCP, transporte Steam separado | Nenhum encontrado |
| [Mirror](https://github.com/MirrorNetworking/Mirror) | C# (Unity) | MIT | KCP padrão; Telepathy TCP, WebSockets, transportes Steam comunitários (FizzySteam, FizzyFacepunch) | Jogos feitos com ele, normalmente não mods |
| [FishNet](https://github.com/FirstGearGames/FishNet) | C# (Unity) | Veja repositório | Estrutura Unity | Nenhum encontrado |
| [KCP](https://github.com/skywind3000/kcp) | C, dois arquivos | MIT | Só algoritmo ARQ (UDP por sua conta); autor declara 10-20% mais banda para latência média 30-40% menor que TCP | Dentro de Mirror |
| QUIC | n/a | n/a | Não abordado: sem exemplo de mod **(não verificado)** | |
| [libdatachannel](https://github.com/paullouisageneau/libdatachannel) | C/C++ | MPL-2.0 | Canais WebRTC por SCTP/DTLS, ICE com STUN/TURN, base libjuice | Nenhum; útil para clientes de navegador |
| [libjuice](https://github.com/paullouisageneau/libjuice) | C | MPL-2.0 | Agente ICE leve, STUN/TURN, UDP, sem dependências | Documentação sm64coopdx menciona compilar libjuice ([resumo](https://github.com/coop-deluxe/sm64coopdx), **finalidade não verificada**) |
| UDP simples | qualquer | n/a | Confiabilidade, fragmentação, negociação por sua conta | Muitos mods pequenos; redes UE1 e Source transportadas por proxy são UDP simples |

Notas de mods, conforme fontes disponíveis:

| Mod | Fatos conhecidos de rede | Link |
|---|---|---|
| TiltedEvolution / Skyrim Together Reborn | GPLv3; submódulos TiltedConnect (serialização e camada sobre biblioteca de rede), cpp-httplib; imagem servidor exige UDP 10578 redirecionado | [repositório](https://github.com/tiltedphoques/TiltedEvolution), [.gitmodules](https://raw.githubusercontent.com/tiltedphoques/TiltedEvolution/master/.gitmodules), [Docker Hub](https://hub.docker.com/r/tiltedphoques/st-game-server) |
| Nitrox (Subnautica) | Cliente/servidor, GPL-3.0, LiteNetLib segundo dependentes NuGet | [repositório](https://github.com/SubnauticaNitrox/Nitrox), [NuGet](https://www.nuget.org/packages/LiteNetLib/) |
| HKMP (Hollow Knight) | Hospedar porta, redirecionar ou Hamachi; LGPL-2.1; transporte não informado na página | [repositório](https://github.com/Extremelyd1/HKMP) |
| SSMP (Silksong) | Rede Steam, matchmaking com travessia NAT, IP direto porta 26960 | [repositório](https://github.com/Extremelyd1/SSMP) |
| Ship of Harkinian Anchor | Host configurável, padrão `anchor.hm64.org` porta 43383; protocolo não verificado | [trecho](https://code.moparisthebest.com/mirror/Shipwright/commit/060878fb2e75c5c2dbbea325169671cf3f9f122f) |
| sm64coopdx | Local, IP direto (7777 padrão), servidor CoopNet, Discord | [documentação](https://mintlify.wiki/retired64/sm64coopdx_launcher/features/network), [repositório](https://github.com/coop-deluxe/sm64coopdx) |
| NV:MP (New Vegas) | Sessões baseadas em host sincronizado (imprensa); transporte não informado | [GameSpot](https://www.gamespot.com/articles/fallout-new-vegas-is-getting-a-multiplayer-mod/1100-6434268/), [Prima](https://primagames.com/gaming/fallout-new-vegas-multiplayer-mod-how-it-works-max-players-installation-and-more) |
| KeeperFX cooperativo | Camada `NetSP` substituível com ENet e provedor Steam | [Spacewar](networking-steam-spacewar.md) |
| xrMPE (STALKER) | Não pesquisado aqui | veja [games/stalker](../games/stalker/README.md) |

### <a id="picking-a-library"></a>Escolhendo biblioteca

- **C# / Unity / Mono:** LiteNetLib (MIT, travessia NAT embutida), mais transporte Steam para retransmissão.
- **Hook nativo C++:** ENet para simplicidade; GameNetworkingSockets para criptografia/P2P juntos; ou API plana Steamworks sem cabeçalhos SDK (página Spacewar).
- **Unity com estrutura existente:** Mirror (KCP padrão, transportes Steam comunitários).
- **Rede já existente:** não substitua; transporte em túnel (seção 4).
- **Evite:** RakNet, descontinuado segundo [README SLikeNet](https://github.com/SLikeSoft/SLikeNet); use SLikeNet só para compatibilidade com jogo RakNet.

## <a id="3-connecting-players-without-port-forwarding"></a>3. Conectando jogadores sem redirecionar portas

| Opção | Funcionamento | Vantagens | Desvantagens |
|---|---|---|---|
| **Retransmissão Steam, AppID 480 Spacewar** | Salas e ISteamNetworkingMessages por SteamID na rede Valve ([documentação](https://partner.steamgames.com/doc/features/multiplayer/networking)) | Sem IP/portas, convite e Join Game na sobreposição, gratuito | Ambos como playing Spacewar; salas visíveis a todos 480 salvo filtro; não publica na loja; docs descrevem 480 só como exemplo ([exemplo Steamworks](https://partner.steamgames.com/doc/sdk/api/example)); posição dos termos **não verificada**: nenhuma fonte Valve permitindo ou proibindo mods com 480, também usado por jogos pirateados ([mein-mmo](https://mein-mmo.de/spacewar-raubkopierer-steam/), fonte indireta) |
| AppID Steam próprio | Mesma API, seu ID (taxa Steam Direct de US$100 **não verificada**) | Nome correto e Workshop, sem conflitos 480 | Exige entrada na loja; mod de jogo alheio não pode reivindicá-la **(avaliação)** |
| EOS P2P | Travessia NAT com retransmissão alternativa, ID de conta, gratuito ([Redpoint](https://docs.redpoint.games/docs/setup/networking/p2p_vs_ip)) | Neutro entre lojas, serve Epic e não Steam | Conta Epic por jogador, sem controle de rota, salto extra; limites de pacote **não verificados**; retransmissor não destinado a dedicado ([Edgegap](https://edgegap.com/blog/can-epic-online-services-eos-relays-allow-for-dedicated-server-or-authoritative-server)) |
| Travessia NAT com servidor de encontro | Ambos enviam aos endereços observados por servidor conhecido (ICE/STUN, libjuice, LiteNetLib, plugin SLikeNet) | Controle próprio; matchmaking SSMP faz exatamente isso ([SSMP](https://github.com/Extremelyd1/SSMP)) | Exige servidor; NAT simétrico impede, exigindo retransmissão também |
| Retransmissor hospedado (TURN ou próprio) | Encaminhador UDP em VPS público | Sempre funciona | Paga banda e operação; libjuice inclui servidor STUN/TURN leve ([libjuice](https://github.com/paullouisageneau/libjuice)) |
| Dedicados comunitários | Jogadores alugam servidor; Skyrim Together roda imagem Docker em UDP 10578 ([Docker Hub](https://hub.docker.com/r/tiltedphoques/st-game-server)) | Melhor para 24/7 e muitos jogadores | Custo e configuração |
| VPN sobreposta | LAN virtual pela internet | Serve todo jogo com campo IP, sem código | Todos instalam e entram |
| UPnP / NAT-PMP | Pedir ao roteador abrir porta ([MiniUPnP](https://github.com/miniupnp/miniupnp), BSD-3-Clause) | Automático quando funciona | Muitos roteadores desativam; não resolve CGNAT |
| Redirecionamento de porta | Manual | Sem custo adicional de processamento | Mais difícil para amigos sem conhecimento técnico |

VPNs em detalhe:

| Rede | Fatos | Fonte |
|---|---|---|
| Tailscale | UDP direto quando possível, alternativa DERP mais lenta; Personal gratuito não comercial, até 6 usuários | [conexões](https://tailscale.com/kb/1257/connection-types), [preços](https://tailscale.com/pricing/) por [busca](https://tailscale.com/kb/1251/pricing-faq) |
| ZeroTier | Maioria MPL-2.0; retransmite quando P2P falha, gratuito mas lento | [ZeroTierOne](https://github.com/zerotier/ZeroTierOne) |
| Hamachi | Gratuito: 5 membros por rede | [suporte GoTo](https://support.goto.com/hamachi/help/logmein-hamachi-subscription-types-hamachi-c-hamachi-subscriptions) |
| Radmin VPN | Participantes ilimitados no gratuito declarados só por lista de terceiros **(não verificado)** | [agentdeals](https://agentdeals.dev/vendor/radmin-vpn) |

### <a id="recommendation"></a>Recomendação

- **Padrão para grupos de 2-4 amigos:** retransmissão ISteamNetworkingMessages com sala e descoberta por amigos, como [Spacewar](networking-steam-spacewar.md). Sem porta, IP ou custo de servidor. Produto independente com aplicativo Steam deve usar seu AppID, não 480.
- **Alternativa:** Tailscale/ZeroTier com IP:porta direto, sem código no mod. Preserve campo IP manual e ofereça UPnP por conveniência.
- **Público não Steam:** EOS P2P ou matchmaking com travessia NAT como SSMP.
- Sempre mantenha LAN/IP direto: outras opções se reduzem a isso e é mais fácil testar.

## <a id="4-wrapping-a-games-existing-udp-netcode-local-proxy"></a>4. Envolvendo rede UDP existente (proxy local)

Use com multiplayer fechado, difícil de mudar ou já funcional em LAN (UE1 de Deus Ex, jogos estilo Source, muitos shooters antigos). O mod não altera o motor: processo auxiliar ao lado move pacotes por transporte melhor. HXCoop faz isso em Deus Ex; regras passo a passo na [página Spacewar](networking-steam-spacewar.md#a-relay-instead-of-engine-code-hxcoop-pattern).

```
Client PC                                   Host PC
game --UDP--> 127.0.0.1:P  [proxy] ==Steam/EOS/other== [proxy] --UDP--> game server 127.0.0.1:S
```

Regras necessárias (padrão HXCoop salvo indicação):

| Regra | Motivo |
|---|---|
| Proxy host abre socket UDP por jogador, porta local distinta, com `connect()` ao servidor | Servidor identifica por endereço/porta de origem; socket único faria todos parecerem um |
| Proxy cliente vincula 127.0.0.1 em porta livre; jogo entra ali | Jogo acredita falar com servidor LAN |
| ID de conexão por jogador no túnel | Quem reconecta ao mudar mapa precisa retomar mapeamento, não criar nova posição |
| Datagramas não confiáveis; controle do túnel em canal confiável auxiliar | Jogo já garante confiabilidade; duplicá-la causa bloqueio. Sinais, despedida e expulsão no confiável |
| Sinais de conexão e prazo ocioso | ISteamNetworkingMessages não informa fechamentos iniciados pelo parceiro ([docs](https://partner.steamgames.com/doc/api/ISteamNetworkingMessages)) |
| Sair com processo, limpar sala e presença | Sem proxies órfãos |
| Respeitar MTU: UDP acima de cerca de 1200 bytes pode fragmentar | Pacotes costumam pequenos (UE1 cerca de 512 segundo Spacewar); confira antes de omitir fragmentação |
| Testar com simulação do motor | UE1 tem `PktLag`, `PktLoss`, `PktOrder`, `PktDup`; Unreal moderno usa `NetEmulation.` ([documentação](https://dev.epicgames.com/documentation/unreal-engine/using-network-emulation-in-unreal-engine)) |

Não use proxy se motor não hospedar servidor participante com seu conteúdo, ou rede não transportar missões. Proxy só move bytes; ainda será necessária camada de sincronização (seção 1).

## <a id="5-testing-netcode"></a>5. Testando código de rede

### <a id="51-emulating-bad-networks"></a>5.1 Simulação de redes ruins

| Ferramenta | Plataforma | Uso | Fonte |
|---|---|---|---|
| clumsy | Windows | Latência, perda, adulteração sistêmica, sem mudar código, localhost para localhost; MIT, baseado em WinDivert | [clumsy](https://github.com/jagt/clumsy) |
| tc netem | Linux | `tc qdisc add dev eth0 root netem delay 100ms 10ms loss 0.3% duplicate 1%`; reordenação exige atraso; filho pfifo evita reordenação por variação | [manual](https://man7.org/linux/man-pages/man8/tc-netem.8.html) |
| Unreal `NetEmulation.PktLag/PktLoss/PktDup/PktOrder` | Unreal 4/5 | Console, linha `SETTING=VALUE` ou INI `[PacketSimulationSettings]`; opções de entrada também | [documentação](https://dev.epicgames.com/documentation/unreal-engine/using-network-emulation-in-unreal-engine) |
| LiteNetLib embutido | C# | Perda e latência na biblioteca | [LiteNetLib](https://github.com/RevenantX/LiteNetLib) |
| Loopback + clumsy | Windows | Duas instâncias num PC | [clumsy](https://github.com/jagt/clumsy) |

Perfis sugeridos **(avaliação)**: RTT 50 ms sem perda; 150 ms com variação 30 ms e perda 2%; 300 ms com perda 5% e duplicação 1%; interrupção total de 3 s.

### <a id="52-one-pc-two-players"></a>5.2 Um PC, dois jogadores

- **DLL Steam simulada:** `steam_api.dll` com mesmas exportações planas, SteamIDs pelo `-nick`, UDP localhost entre processos, IDs de sala determinísticos e retenção real da primeira mensagem até AcceptSession. Detalhes e extensões na [página Spacewar](networking-steam-spacewar.md#testing-without-two-steam-accounts-the-mock-dll).
- Steam real permite uma conta por PC; teste genuíno de retransmissão exige contas reais. Duas contas são etapa humana separada, a declarar não testada até realizar.
- Cada cliente em cópia própria da instalação ([AGENTS.md](../AGENTS.md), regra 2).

### <a id="53-what-to-assert"></a>5.3 O que verificar

| Teste | Aprovação |
|---|---|
| Entrar, sair, voltar | Posição reutilizada corretamente, sem entidades fantasma |
| Kill -9 num cliente | Host remove dentro do prazo dos sinais |
| Encerrar host | Clientes saem normalmente ou voltam ao menu, sem travar |
| Host muda mapa | Clientes seguem ou aguardam, sem dessincronizar |
| Entrada tardia em missão | Mesmos indicadores host |
| Salvar/recarregar durante sessão | Estado coincide após carregar |
| Perfis de perda/variação da seção 5.1 | Sem falha, estado converge em N segundos |
| Prolongado | 30-60 min de jogo por bot, hashes periódicos; relatar diferenças e crescimento de memória **(avaliação)** |

Hashes de estado: ambos calculam lista canônica (indicadores, inventário, posições arredondadas) a cada poucos segundos e registram; comparar logs detecta dessincronização economicamente. Para bots, [automated-qa.md](automated-qa.md).

## <a id="6-pitfalls-checklist"></a>6. Lista de armadilhas

- Fixe compilação (SHA-256 do executável) antes de reutilizar deslocamentos/hooks alheios.
- Não use confiável ordenado para movimento; pacote perdido bloqueia os seguintes ([Gaffer](https://gafferongames.com/post/deterministic_lockstep/), bloqueios TCP).
- Protocolo sem ponteiros/endereços; IDs estáveis entre sessões e máquinas.
- Não confie em callbacks de desconexão: acrescente sinais (ISteamNetworkingMessages não informa fechamento remoto).
- Endereçamento do retransmissor não necessariamente IP:porta; envolva em ID próprio de jogador.
- Antitrapaça: modificar jogo on-line com antitrapaça está fora do escopo (AGENTS.md regra 10); Seamless Co-op de Elden Ring bloqueia serviço on-line para caminho separado ([guia](https://www.exitlag.com/blog/elden-ring-seamless-co-op/), indireto).
- Licenças: bibliotecas GPL exigem mod GPL se distribuído vinculado; prefira MIT/BSD (ENet, LiteNetLib, GameNetworkingSockets, yojimbo), salvo mod já GPL.
- Registre desconhecidos em vez de adivinhar: cada não verificado acima convida a testar e enviar PR.

## <a id="sources-not-fetched-or-thin"></a>Fontes não consultadas ou insuficientes

- Referências oficiais EOS P2P retornaram 404 em todas as URLs tentadas; informações acima vêm de terceiros.
- Wiki Valve de rede Source retornou 403; compensação de latência estilo Source não citada.
- Internos de Skyrim Together, NV:MP, Seamless Co-op, sm64coopdx e Anchor: só páginas de repositórios e resumos disponíveis. Leia o código antes de copiar arquitetura.
