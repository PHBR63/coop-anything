# <a id="baldis-basics-plus-2020"></a>Baldi's Basics Plus (2020)

| | |
|---|---|
| Motor | Unity 2020.3.49f1, Mono, Windows x64 (BepInEx 5.4.23.5 ou MelonLoader 0.7.3, Harmony) |
| Versões testadas | Steam (aplicativo 1275890), versão 0.14.5, buildid 24261910. SHA-256 de `BALDI.exe` `b9bd86d050c90811d037a978ab246b7c06c9370bf25d0e8f83b35d3a1a120026`, SHA-256 de `Assembly-CSharp.dll` `635b0d164a7050942077f3a7509ad2e4dc49a4d860e476ebe6906c7508dfa367` |
| Projetos | Baldi Together ([baldi-plus-coop](https://github.com/multiplayereverything/baldi-plus-coop), [pré-lançamento v0.9.2](https://github.com/multiplayereverything/baldi-plus-coop/releases/tag/v0.9.2)); entrada "Baldi Together" no diretório |
| Nível de QA | automated |
| Última atualização | 2026-10-26 |

## <a id="where-things-stand"></a>Situação atual

Baldi Together permite a até quatro jogadores percorrer juntos os andares de Hide & Seek, em LAN ou on-line pelo Steam. O host executa o jogo real; NPCs, portas, itens coletáveis, loja e resultados seguem o host. Cada jogador pode ser capturado individualmente e então observa os companheiros. É uma versão alfa. O modo principal é coberto por testes automatizados com processos reais; os testes manuais do autor (principalmente sozinho, ainda sem amigos) indicaram que funciona bem na maior parte. Eventos aleatórios seguem o host (0.9.2): neblina, Mystery Room, régua quebrada e castigo são reproduzidos no jogo de todos; os demais executam somente no host. Excursões escolhem a mesma viagem Pitstop em cada cópia. Challenges e Endless não foram validados.

## <a id="existing-work"></a>Trabalhos existentes

Uma busca em 2026-10-26 não encontrou outro projeto cooperativo ou multiplayer para Baldi's Basics Plus. Cobriu este diretório, pesquisas na web (somente mods para um jogador e menus de mods no itch.io e GameBanana) e as [discussões Steam](https://steamcommunity.com/app/1275890/discussions/0/2963893984920858040), onde o modo cooperativo é assunto de jogadores, não um projeto. O [projeto multiplayer no GameBanana](https://gamebanana.com/mods/668785) é para Baldi's Basics Classic, não Plus. Não pesquisados: Discord de mods do BB+ e sites em outros idiomas. Lista completa em [`docs/IDEAS.md`](https://github.com/multiplayereverything/baldi-plus-coop/blob/main/docs/IDEAS.md) do mod. O jogo é exclusivamente para um jogador.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Motor e scripts:** Unity Mono; toda a lógica está em `BALDI_Data/Managed/Assembly-CSharp.dll` e aceita hooks Harmony. Fases são geradas por semente. Mesma semente e compilação produzem o mesmo mapa, mas o posicionamento aleatório de itens gratuitos não é estável entre máquinas; o host reconcilia a lista de itens antes de o cliente entrar.
- **Sem código de rede.** Tudo acima do transporte usa protocolo próprio do mod: quadros TCP com prefixo de tamanho de 4 bytes, negociação de versão exata e hash do mapa, depois estado com autoridade do host.
- **Steam já está presente.** O jogo inclui Steamworks.NET (`com.rlabrecque.steamworks.net.dll`, networking sockets v012, matchmaking v009) e `steam_api64.dll`. Seu `SteamManager` chama `SteamAPI.Init` e `SteamAPI.RunCallbacks` por quadro e pausa uma partida quando a sobreposição Steam abre.
- **Salvamentos:** partidas multiplayer não geram salvamento retomável. O modo de laboratório (`-bt-lab`) redireciona os caminhos para a pasta do mod; testes nunca alteram os salvamentos do usuário.

## <a id="what-we-changed"></a>O que alteramos

A lista completa de recursos está no README do mod. Esta seção reúne lições aplicáveis a outros jogos.

### <a id="link-liveness-must-not-depend-on-the-game-loop"></a>A atividade da conexão não pode depender do loop do jogo

- **Bug:** o log de um jogador mostrava um cliente migrando para novo host enquanto o host ainda rodava. Antes da 0.9.0, o único tráfego regular era um sinal a cada 2 s enviado por `Update`, e o socket expirava após 15 s de silêncio. Assim, um host cujo loop parasse por 15 s parecia morto e provocava migração dos clientes. Carregamento, engasgo ou possivelmente Alt+Tab podem interromper o loop por esse tempo. O host também removia clientes travados dessa forma.
- **Segunda causa:** a fila de recepção removia o par em 512 pacotes enfileirados, e a de envio em 128. Com poses de um cliente chegando enquanto o host estava parado, isso correspondia a cerca de 25 s, ou 9 s com três clientes. Conexão ruim que retivesse TCP por alguns segundos também enchia a fila de envio.
- **Correção (protocolo 14):**
  - A thread de escrita do socket envia quadro de manutenção de 1 byte (`0x00`) após 2 s sem tráfego, descartado pelo leitor. O loop parado mantém a conexão. Processo ou rede mortos ainda expiram após 15 s.
  - A manutenção só começa após o primeiro quadro do par. Assim, compilações anteriores ainda recebem mensagem de incompatibilidade de versão em vez de quadro desconhecido.
  - O cliente mede o silêncio do host: "The host isn't responding" após 5 s; migra (LAN) ou sai (Steam) após 60 s.
  - Filas limitadas por tamanho (8 MB aguardando o loop, 4 MB não enviados por conexão), não por contagem de pacotes.
- **Lição:** se o sinal de atividade vem do loop do jogo, um carregamento longo parece desconexão. Envie manutenção pela thread de rede e diferencie "o outro lado foi embora" de "o outro lado está ocupado".

### <a id="a-tcp-chaos-proxy"></a>Um proxy de caos TCP

O simulador de caos central (`tools/chaos`) degrada datagramas UDP. Em TCP, o kernel corrige perdas, reordenação e duplicações; o jogador percebe atraso, bloqueios no início da fila, limite de banda, interrupções e conexões cortadas. [`tests/tcp-chaos.py`](https://github.com/multiplayereverything/baldi-plus-coop/blob/main/tests/tcp-chaos.py) é um proxy de loopback com semente reproduzível que modela esses efeitos por direção e lê `tools/chaos/profiles.json` (com cópia incorporada como alternativa):

- atraso e variação de latência, com bytes sempre saindo em ordem;
- perdas Gilbert-Elliott convertidas em bloqueio de retransmissão: segmento perdido fica retido por um prazo de retransmissão, e tudo atrás espera;
- controle de banda com contrapressão (proxy para de ler quando o buffer enche);
- porta de controle com um comando JSON por linha: `set_profile`, `stall` (interrupção à qual TCP sobrevive), `cut` (fecha todas as conexões intermediadas), `stats`, `shutdown`.

```
python -I tests/tcp-chaos.py --listen 7801 --target 127.0.0.1:27015 --profile bad_wifi --control 7802
python -I tests/tcp-chaos.py call 7802 '{"cmd":"stall","dir":"both","seconds":8}'
python -I tests/tcp-chaos.py selftest
```

É um único arquivo Python sem dependências; qualquer conexão TCP de jogo pode usá-lo.

### <a id="use-the-games-own-steamworks-not-spacewar-480"></a>Use o Steamworks do próprio jogo, não Spacewar 480

Quando um jogo Steam já inclui e inicializa Steamworks.NET, o mod pode usar essa cópia:

- salas Steam (`bt=1`, mais versão exata do mod e protocolo nos dados da sala);
- `SteamNetworkingSockets.CreateListenSocketP2P` e `ConnectP2P` pela retransmissão Valve;
- presença enriquecida `connect` = `+connect_lobby <id>`, dando aos amigos **Join Game** no perfil do host;
- convites da sobreposição (`GameLobbyJoinRequested_t`, `GameRichPresenceJoinRequested_t`) e argumento de inicialização `+connect_lobby`.

Nada é baixado ou incluído no pacote, o Steam mostra o jogo real e nenhum `steam_appid.txt` é gravado. O protocolo exigiu uma alteração: interface `IPacketLink`, permitindo uma conexão Steam como enlace Transport, com um quadro Transport por mensagem Steam confiável. Negociação e tudo acima são iguais à LAN. Confira primeiro se `SteamManager` chama `RunCallbacks` a cada quadro e procure efeitos colaterais. Aqui, abrir a sobreposição pausa o jogo; por isso, INVITE FRIENDS aparece só na sala. Salas Steam não têm migração de host, pois ela exige endereços.

### <a id="random-events-one-schedule-the-hosts"></a>Eventos aleatórios: uma programação, a do host

Cada cópia cria a mesma lista de eventos aleatórios do andar a partir da semente. Ordem de início, intervalos e duração vêm de `UnityEngine.Random` em execução; duas cópias com temporizadores próprios divergem. Em Hide & Seek, só o host inicia os temporizadores. Uma cena de desafio os inicia diretamente ao carregar; o mod bloqueia `EnvironmentController.StartEventTimers` nos mundos clientes.

O host envia anúncio, início e fim por índice na lista compartilhada. Clientes reproduzem a vinheta e a introdução na TV. Para efeitos individuais (neblina, Mystery Room, régua quebrada e infração de regra, luzes e música do castigo), o cliente executa `Begin` do evento, desativando seu temporizador final para que só End do host o encerre. A raiva de Baldi causada pelo castigo fica no host. O teste executa neblina no host e verifica sua ativação/desativação no cliente. Uma variante de mutação que nada envia deve falhar, e falha.

Pitstop também escolhia sua sala de excursão com `UnityEngine.Random`, podendo gerar locais diferentes e falhar a correspondência do mundo. Agora a escolha deriva da semente da partida e do andar.

### <a id="only-lobby-members-may-connect"></a>Somente membros da sala podem conectar

O socket Steam de escuta do host aceitava qualquer SteamID que chamasse, até três. A regra de [networking-steam-spacewar](../../playbook/networking-steam-spacewar.md) também vale para sockets orientados a conexão: somente membros da sala entram. A lista de membros pode chegar um instante após a chamada de entrada; quem ainda não aparece fica aguardando até 5 s antes de ser recusado.

### <a id="testing-steam-with-one-account"></a>Testando Steam com uma conta

Uma conta Steam não abre conexão P2P consigo mesma, mas a maior parte do caminho Steam pode ser testada em um processo:

- **`SteamAppId` em vez de arquivo:** o inicializador de laboratório define `SteamAppId=1275890` e `SteamGameId=1275890` antes do executável, como faz o Steam. `SteamAPI.Init` funciona sem o Steam iniciar o jogo e sem escrever `steam_appid.txt` na pasta.
- **`SteamNetworkingSockets.CreateSocketPair`:** fornece duas conexões interligadas no mesmo processo pela API real. Vincule uma a Transport de host e outra a Transport de cliente e execute a negociação e os quadros reais.
- **Sala real sem exposição:** HOST ON STEAM abre sala real só para amigos, marcada `bt=lab` e nunca listada pelo filtro público. O teste confere os dados e a presença Join Game, sai e verifica fechamento e remoção da presença.

Isso encontrou dois bugs antes de qualquer sessão real:

- o lado que fechava nunca encerrava seu próprio par, porque Steam não publica callback para fechamento local, deixando jogador fantasma;
- o menu caía na página de opções após HOST ON STEAM.

Isso não cobre a retransmissão Valve entre duas contas.

## <a id="qa"></a>QA

- `scripts/test.ps1`: 26 verificações de transporte: enlace ocioso sobrevive além do prazo de leitura, par bruto silencioso ainda expira, 1.500 pacotes enfileirados aguardam loop parado. Sua variante (`BT_MUTANT=no-keepalive`) deve falhar na verificação ociosa, e falha.
- `scripts/link-test.ps1` (host BepInEx, cliente MelonLoader, por `tcp-chaos.py` com `bad_wifi`): 7/7. Cliente aguardou 25 s de parada do host (`-bt-lab-stall-host 25`) sem cair ou migrar, e host o manteve. Ambos sobreviveram a interrupção bidirecional de 10 s, sincronizados. Conexão cortada ainda foi detectada. Com `-bt-lab-no-keepalive`, cliente cai em 14.998 ms e migra, reproduzindo o bug relatado e comprovando que o teste falha.
- `run-tour.ps1 -Steam` (um processo, Steam conectado): 17/17 na 0.9.2, incluindo restrição da sala; variante sem restrição falha. Par de sockets Steam sob dois Transports reais (conectar, ambas as direções, quadro de 64 KB, 200 quadros em ordem, quadro final antes de fechar, lado que fecha encerra seu par), páginas Steam, sala real `bt=lab` com presença Join Game e saída.
- `launch-lab.ps1 -EventSync` com `tests/verify-events.py` (0.9.2): 7/7; variante sem sincronização de eventos falha (2/7). `client_events_host_only` no teste do núcleo: cliente solicitado a iniciar seus próprios temporizadores deve recusar; uma variante que permite isso falha.
- `scripts/lab-suite.ps1` na 0.9.2 (segundo PC, sem atividade): todos os percursos, LAN de dois processos, sincronização de NPCs, núcleo, encontros 45/45, longa duração 12/12 (custo do mod cerca de 0,2 ms por quadro), testes de conexão e loja, sem repetições. Cópias de laboratório usam pequenas janelas minimizadas e baixa prioridade. Antes, na 0.9.0: verificações de transporte e variante; percursos de recursos (sala 32, observador 16, áudio de Hide & Seek 7, interface de observador 18, itens 18, Beans 14, Arts and Crafters 16, Mrs. Pomp 17, The Test 15, Dr. Reflex 16, Chalkles 15, Hall Monitor 25, compat-fail 3); testes de dois processos (LAN 15/15, sincronização de NPCs 15/15, núcleo cooperativo 14/14, longa duração 12/12, conexão 7/7). Toda inicialização usa `-bt-lab -bt-diagnostics` e somente processos do teste.
- Teste de encontros com dois processos passou 45/45 na compilação final após falha intermitente anterior. Algumas inicializações de dois processos param no início e são repetidas uma vez.
- **Testes manuais:** autor jogou principalmente sozinho e relata bom funcionamento na maior parte. Ainda não jogou com amigos.
- Ainda não coberto: sessão Steam entre duas contas pela retransmissão Valve.

## <a id="how-to-play"></a>Como jogar

Instale BepInEx 5.4.23.5 ou MelonLoader 0.7.3 (um carregador por cópia; as duas compilações jogam juntas); extraia o ZIP correspondente da [página de versões](https://github.com/multiplayereverything/baldi-plus-coop/releases) em `<game dir>`. Selecione **MULTIPLAYER** na tela inicial.

- **LAN:** HOST GAME; amigos usam JOIN GAME ou FIND LAN GAMES.
- **Steam:** inicie pelo Steam, depois STEAM GAME → HOST ON STEAM. Amigos entram por convite, Join Game no perfil do host ou FIND STEAM GAMES.
- Todos precisam da mesma versão do jogo (0.14.5) e do mod.

## <a id="known-issues"></a>Problemas conhecidos

- Sala Steam termina quando o host sai; somente LAN migra para novo host.
- Abrir a sobreposição Steam pausa a partida.
- Flood, party, gravity, Balder Dash e student shuffle executam somente no host; seus NPCs e portas aparecem para todos, mas efeitos individuais (água, balões, visão invertida) não.
- Challenges, Endless e outros mods não foram testados com o modo cooperativo. Vencer um desafio encerra o jogo do host, desconectando todos.
- Entre antes de iniciar a partida; entrada em andamento não é compatível.

## <a id="next-steps"></a>Próximos passos

- Executar sessão Steam real com duas contas pela retransmissão Valve.
- Validar Challenges e Endless (vitória e resultados para todos, cadernos repetidos) e reproduzir os efeitos locais dos eventos restantes.
- Jogar uma partida cooperativa completa e documentar para `verified-playthrough`.
