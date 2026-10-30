# <a id="planetbase-2015"></a>Planetbase (2015)

| | |
|---|---|
| Motor | Unity, backend Mono (BepInEx 5 x86 + Harmony); versão exata do Unity não registrada |
| Versões testadas | Steam, compilação Windows 1.4.2 (Steam build id 20301361), executada no Linux por Proton 9.0; SHA-256 de `Assembly-CSharp.dll` `245441e4892d10551823334b7171ec712e88e7218913c20d8b44154ca98af045` |
| Projetos | [Planetbase Co-op](https://github.com/Elwynn18/Planetbase-coop); em [DIRECTORY.md](../../DIRECTORY.md) |
| Nível de QA | automated |
| Última atualização | 2026-10-25 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores conseguem administrar uma colônia juntos: um hospeda e o outro entra para jogar na colônia do host. Construções, conexões, comércio, prioridades, velocidade do jogo e configurações passam pelo host. Uma suíte automatizada com duas cópias sob Proton passa em 16/16, incluindo variantes de mutação. Só dois jogadores foram testados, e o jogo não tem avatares; assim, "ver o outro jogador" significa ver suas prévias de posicionamento com seu nome.

## <a id="existing-work"></a>Trabalhos existentes

Pesquisados em 2026-10-25: busca na web (duas consultas), discussões Steam de Planetbase encontradas por elas e diretório, issues e jogos deste núcleo. Nenhum outro projeto cooperativo ou multiplayer de Planetbase foi encontrado. Não pesquisados: páginas Nexus de mods individualmente, Reddit, servidores Discord.

- **[Planetbase Co-op](https://github.com/Elwynn18/Planetbase-coop)** (Elwynn18, MIT), versão 0.2.0, primeiro commit em 2026-10-24. Criado com os guias deste núcleo.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Motor:** Unity com backend Mono: código do jogo em `Planetbase_Data/Managed/Assembly-CSharp.dll`, legível com ILSpy e modificável por Harmony. O jogo é de **32 bits**: BepInEx precisa ser a compilação `win_x86` (`BepInEx_win_x86_5.4.23.5.zip`); a x64 não carrega.
- **Sem código de rede** próprio. O jogo inclui Steamworks.NET (20.2.0), e seu AppID Steam é 403190; o mod reutiliza ambos para transporte Steam, sem instalação adicional para jogar pelo Steam.
- **Salvamentos:** os serializadores do jogo transformam a colônia em XML. O mod os usa para criar um salvamento em memória no host e carregá-lo em quem entra pelo carregador do próprio jogo.
- **Linux:** a compilação Windows roda sob Proton. Wine carrega sua própria `winhttp.dll`, a menos que a opção de inicialização `WINEDLLOVERRIDES="winhttp=n,b" %command%` esteja definida; sem ela, BepInEx nunca inicia.
- **Verificação de versão:** o mod compara `Assembly-CSharp.dll` byte a byte entre os jogadores; assim, qualquer mod que altere esse arquivo em disco aparece como compilação diferente do jogo.

## <a id="what-we-changed"></a>O que alteramos

Planetbase Co-op é um mod novo (caminho 2, criado do zero). Arquitetura: réplica com autoridade do host.

- **Entrada:** a colônia do host é enviada como salvamento criado em memória e carregada pelo carregador do próprio jogo; depois, a simulação de quem entrou é congelada.
- **Sincronização:** ciclo de vida dos objetos (criação/destruição, como XML do próprio jogo), pequenos registros de estado (posições, construção, detentores de recursos, naves, indicadores) e um censo a cada 5 segundos para corrigir divergências.
- **Ações:** ações dos jogadores são capturadas nos pontos de confirmação do jogo (posicionar módulo, criar conexão, botão Trade da janela de comércio) e repetidas no host por ID de objeto.
- **Perigos:** meteoros e raios são reproduzidos nos participantes a partir da semente e alvo do host; tempestades de areia, nevascas e erupções solares são enviadas a cada segundo. O dano é calculado apenas no host.
- **Correções do primeiro teste de jogo (0.2.0):** níveis de acumuladores e tanques de água; contador de colonos do participante mostrava `int.MaxValue`; uma negociação malsucedida do participante podia perder moedas da base; edição das configurações pelo participante podia ser sobrescrita pelo reenvio do host a cada 5 s; progresso de construção pausada não chegava aos participantes.
- **Proteção contra erros:** durante a sessão, um erro do jogo não abre mais a página fatal "ERROR ... Quit"; é registrado, e o participante o envia ao log do host.

## <a id="qa"></a>QA

`test/lab.py` prepara cópias do jogo com hardlinks, cada uma com prefixo Proton próprio, BepInEx e o mod, e executa cada cópia em seu gamescope sem interface; nenhuma janela aparece na área de trabalho do testador. Um bot interno controla cada cópia. As cópias não têm `steamclient.dll`, e o mod bloqueia `SteamAPI.Init` no modo de teste, então os testes nunca alcançam um cliente Steam real. Xvfb não funciona com este jogo (GL por software nunca desenha um segundo quadro).

`python3 -I test/suite.py` executa todos os casos. Cada variante de mutação desativa uma proteção e precisa falhar na verificação indicada:

| Caso | Verificações |
|---|---|
| `boot` | Uma cópia inicia com BepInEx e o mod carregados. |
| `join` | O participante carrega a colônia do host; construções, colonos e recursos correspondem. |
| `refuse` | Participante com versão diferente do mod é recusado. |
| `ships` | Naves em pouso, notificações e configurações chegam ao outro lado. |
| `hazards` | Meteoros, tempestades de areia e prévias de posicionamento aparecem nos dois lados. |
| `twin-no-lifecycle` | Falha: módulo construído pelo host aparece no participante. |
| `twin-no-commands` | Falha: módulo posicionado pelo participante é construído pelo host e replicado de volta. |
| `twin-no-char-states` | Falha: colonos ficam onde o host os mantém. |
| `twin-no-res-states` | Falha: recursos têm o mesmo detentor e posição. |
| `twin-no-census` | Falha: censo restaura o recurso perdido pelo participante. |
| `twin-no-build-states` | Falha: estado e progresso da construção correspondem. |
| `twin-no-ship-states` | Falha: posição da nave em pouso no participante. |
| `twin-no-notices` | Falha: notificação do host exibida ao participante. |
| `twin-no-settings` | Falha: alteração de permissão de pouso do host chega ao participante. |
| `twin-no-edit-flush` | Falha: alteração de permissão de pouso do participante chega ao host. |
| `twin-no-error-guard` | Falha: erro do participante é capturado e relatado. |

Última execução da suíte, 2026-10-26, mod 0.2.0:

```
SUITE: 16/16 passed
  PASS boot (19 s)
  PASS join (59 s)
  PASS refuse (72 s)
  PASS twin-no-commands (90 s) twin caught: FAIL joiner-placed module built by the host and mirrored back (host side) (timeout after 25 s)
  PASS twin-no-lifecycle (123 s) twin caught: FAIL host-built module appears on the joiner (Module: host 4 joiner 3)
  PASS twin-no-res-states (66 s) twin caught: FAIL resources have the same holder and place (4 of 114 off, e.g. 119 host 0:-1:-1:1021.7:925.8 joiner 0:-1:-1:1017.7:922.8)
  PASS twin-no-char-states (117 s) twin caught: FAIL colonists are where the host has them (within 5 m, one walked 8 m+) (4 of 9 off, 3 moved, worst 48.0 m)
  PASS twin-no-census (77 s) twin caught: FAIL census restores the resource the joiner lost (id 119) (timeout after 20 s)
  PASS twin-no-build-states (77 s) twin caught: FAIL construction state and progress match (2 of 5 off, e.g. 132 host ModuleTypeSolarPanel:1:1065.8:943.3:0.50 joiner ModuleTypeSolarPanel:1:1065.8:943.3:0.00)
  PASS ships (90 s)
  PASS twin-no-ship-states (111 s) twin caught: FAIL landing ship position on the joiner (timeout after 60 s)
  PASS twin-no-notices (102 s) twin caught: FAIL host notification shown on the joiner (timeout after 10 s)
  PASS twin-no-settings (99 s) twin caught: FAIL host's landing permission change reaches the joiner (timeout after 10 s)
  PASS twin-no-edit-flush (100 s) twin caught: FAIL joiner's landing permission change reaches the host (timeout after 10 s)
  PASS hazards (146 s)
  PASS twin-no-error-guard (158 s) twin caught: FAIL joiner error caught and reported (received 0, fatal 'coop test: deliberate error to check the error guard')
```

Limites: a suíte roda em um PC por IP direto. Duas pessoas jogaram em dois PCs com duas contas Steam, entrando por convite Steam (relatado pelo autor, sem estrutura de teste): a primeira sessão (0.1.0) encontrou os bugs corrigidos em 0.2.0, e uma posterior usou o instalador de arquivo único no PC do segundo jogador. Raios, nevascas e erupções solares compartilham código de meteoros e tempestades de areia, mas não têm cobertura de testes.

## <a id="how-to-play"></a>Como jogar

Todos precisam de Planetbase 1.4.2 do Steam e da mesma versão do mod.

- **Windows:** baixe [`install/Planetbase-Coop.bat`](https://github.com/Elwynn18/Planetbase-coop/blob/main/install/Planetbase-Coop.bat) e dê dois cliques.
- **Linux (Steam + Proton):** baixe [`install/planetbase-coop.sh`](https://github.com/Elwynn18/Planetbase-coop/blob/main/install/planetbase-coop.sh) e execute `bash planetbase-coop.sh`. Ele também configura a opção de inicialização do Proton (com Steam fechado e backup prévio de `localconfig.vdf`).

Cada instalador encontra o jogo em todas as bibliotecas Steam, confere a compilação, instala BepInEx 5.4.23.5 x86 e o mod mais recente (ambos verificados por SHA-256) e oferece iniciar o jogo. Execute novamente para atualizar; o mesmo menu desinstala. Passos manuais no [README do mod](https://github.com/Elwynn18/Planetbase-coop#readme).

No jogo, pressione **F8**. Host: carregue a colônia, F8 > Host with Steam > Invite. Participante: aceite o convite Steam no menu principal. IP direto também funciona (TCP 47610; redirecione essa porta no roteador do host ou use VPN).

## <a id="known-issues"></a>Problemas conhecidos

- Só o host salva. Se ele sair, os participantes voltam ao menu.
- Uma ação de participante leva uma ida e volta ao host.
- Participantes não veem o feixe do laser antimeteoro, apenas o meteoro desaparecendo.
- Uma construção exatamente na borda da área permitida perto da nave da colônia pode aparecer como bloqueada para um participante.
- Mais de dois jogadores: sem cobertura de testes.

## <a id="next-steps"></a>Próximos passos

- Jogar uma sessão pela internet com duas contas Steam e registrar o que falha.
- Testar três ou mais jogadores.
- Acrescentar testes para raios, nevascas, erupções solares e intrusos.
- Acrescentar execução com latência e perda (`tools/chaos`).
