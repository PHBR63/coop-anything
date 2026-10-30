# <a id="dragon-age-origins-2009"></a>Dragon Age: Origins (2009)

| | |
|---|---|
| Motor | Eclipse Engine (Aurora aprimorado da BioWare, motor de Neverwinter Nights), x86 de 32 bits, RTTI intacto, sem código de rede |
| Versões testadas | **1.05.13263.0**, `DAOrigins.exe` da compilação GOG numa instalação Steam (aplicativo **47810**, depósito 47811, compilação 21245176). GOG, EA e Steam distribuem executáveis diferentes da mesma versão; biblioteca de endereços DAOLib mapeia os três. |
| Projetos | [dao-coop](https://github.com/vmosenkov/dao-coop), em desenvolvimento, entrada abaixo |
| Nível de QA | automated (dois clientes reais, suíte por scripts) |
| Última atualização | 2026-10-23 |

## <a id="where-things-stand"></a>Situação atual

**Dois jogadores já podem entrar num mundo, controlar integrantes diferentes do grupo, lutar juntos, morrer, ser reanimados e ler um registro real de eventos dentro do jogo**: protótipo funcional, não jogo concluído. Verificado no jogo: DAOLib carrega plugins nativos; convidado **entra pela rede** (host salva e serve pasta da vaga; convidado grava no próprio perfil e carrega, chegando ao mundo do host com mesmos identificadores de objetos); com companheiro contratado antes do salvamento de entrada, **host controla um integrante e convidado outro**, cada jogo espelhando a criatura do outro; posição, vida e estado de morte de criatura hostil do host são espelhados.

Além disso: **arbitragem de combate** (ordens de ataque do convidado viram solicitações; host valida no mundo ativo, ordena ataque ao seu jogo e envia resultado; repete ordem a cada dois segundos para completar golpe), **morte e reanimação** (jogador host caído mantém mundo enquanto integrante vive; após luta, caídos voltam à vida máxima e controle retorna), **reentrada após host carregar outro salvamento** (host salva novamente e serve mundo; convidado recebe, recarrega e retorna) e **painel Event Log dentro do jogo**: tela SWF 8 própria do plugin no HUD, criada de ActionScript 2 com fontes do jogo, preenchida pelo registro da sessão (categorias multiplayer, combate e sistema, abas de filtro, nomes de criaturas, recolhimento por clique). Faltam sincronização de efeitos/saque/animação de morte, transições, menu de hospedagem/entrada, transporte internet e segundo PC físico. O golpe da cópia já é espelhado; demais animações e efeitos não. Única interface é `daocoop.ini` (escrito por `install.ps1` da distribuição).

Registro e movimento corrigidos no mesmo dia (2026-10-23); caminho LAN reverificado em 0.7.3 com `independence-test -PeerIp <this machine's LAN address>` (ambos vinculados a `0.0.0.0`, `dropped 0`, ambos com registros compartilhados): **registro de eventos agora compartilhado** (novo pacote leva cada linha ao outro jogo; laço receptor único despacha todos os tipos, corrigindo também estouro de buffer de transporte), ambos leem mesmas linhas; convidado sem integrante configurado **assume primeiro companheiro automaticamente**, evitando que ambos controlem o mesmo Warden e arrastem um ao outro à mesma posição. Automatizados: independence-test e walk-test passam na compilação de distribuição 0.7.1.
## <a id="existing-work"></a>Trabalhos existentes

- **DAOKadanMP**, `Whocares66-Dev/DAOKadanMP`: repositório **privado**, sem distribuição ou licença. Única tentativa multiplayer ativa; evidência só em issues públicas de DAOLib/DAOEluvianMCP (outubro de 2026): dois jogos num salvamento, entrada por endereço da área de transferência, associação parcial de objetos, baú compartilhado, carregamento de salvamentos na sessão. Lacunas nas mesmas issues: sacos de cadáveres/saque sem sincronização (DAOLib #103), golpes a mais de ~60 m da câmera do host sem acertar (DAOLib #88). Trate como pista para contato, não dependência.
- **Descompilação de 2026** (usuário Reddit `Shot_Let_1344`): seis desenvolvedores, cerca de 3 anos, ~60% descompilado/~55% vinculado de 34.415 funções; publicação só perto de 90% (meta 2027). **Planeja** 64 bits, correções do motor, controles e possível rede/campanhas cooperativas; ainda sem repositório, site ou compilação. Não é artefato atual.
- **xoreos** (GPLv3, reimplementação Aurora) tem DAO como alvo, mas só jogabilidade parcial como observador e sem rede. **OpenDAO / Nikami Aurora** é execução de compatibilidade Godot MIT; também sem multiplayer.
- **Nenhum mod público cooperativo jamais foi distribuído.** Steam Community, Nexus, ModDB, Reddit e fóruns russos/alemães desde 2009 respondem só para um jogador; Nucleus Co-op não tem handler porque não há multiplayer para sobrepor tela dividida.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- Eclipse é motor solo: **sem rede**, uma criatura controlada, inventário de grupo único, tempo real com pausa global, câmera única de diálogo/cena. Modo multiplayer existiu e foi cortado no desenvolvimento (entrevistas de 2021).
- Lógica: **827 comandos numerados de scripts**, executados por VM interna numa thread, com 314 manipuladores de mensagens. Scripts controlam história, IA, gatilhos e mudanças de fase.
- **[DAOLib](https://github.com/Whocares66-Dev/DAOLib)** (GPLv3) é carregador estilo SKSE/CommonLibSSE (`dinput8.dll`) e biblioteca C++ para 1.05.13263.0 GOG/EA/Steam, com [biblioteca de endereços](https://github.com/Whocares66-Dev/DAOAddressLibrary) de mais de 100 mil identificadores. Oferece todos os comandos (chamar, interceptar, ampliar), barramento de mensagens, callback por quadro na thread de scripts, estado de objetos/criaturas (leitura e escrita de propriedades das criaturas), ordens indistinguíveis de cliques, entrada, interface Flash, hooks de salvamento (arquivos auxiliares, `Save`/`Load`/`List`), modos e pausa.
- **Salvamentos são pastas** (`Characters\<name>\Saves\<slot>` com `.das`, `.das.met`, `screen.dds`). Copiar pasta a outro perfil permite carregá-la diretamente; carregar numera novos objetos pelo contador do salvamento. Dois jogos do mesmo salvamento concordam nos identificadores: base da entrada por transferência usada aqui.
- **Instâncias nomeadas**: iniciar com `DAOLIB_INSTANCE=<name>` dá mutex e perfil Documents próprios (`%LOCALAPPDATA%\DAOLib\instances\<name>`), permitindo cópias lado a lado sem alterar perfil real.
- **[DAOEluvianMCP](https://github.com/Whocares66-Dev/DAOEluvianMCP)** é plugin público de bancada MCP que expõe jogo ativo por HTTP/MCP e aceita múltiplas instâncias, estrutura pretendida para testes automatizados.

## <a id="what-we-changed"></a>O que alteramos

Projeto em repositório próprio ([dao-coop](https://github.com/vmosenkov/dao-coop), GPLv3, sem arquivos do jogo). `docs/STATUS.md` traz evidências por etapa; `docs/DESIGN.md`, arquitetura; `docs/TESTING.md`, plano de testes.

| Marco | O que comprova | Teste comprobatório |
|---|---|---|
| M0 | DAOLib carrega plugin e este lê estado ativo na thread do jogo | `loader.log` `daocoop.dll: loaded`; `daocoop.log` `mode explore`, barra do grupo, identificador/área/posição/vida da criatura controlada |
| M1 | Dois processos executam lado a lado como instâncias nomeadas, perfis separados | dois processos `daorigins` ativos; ambos registram perfil próprio preparado |
| M1 | Ambos concordam nos identificadores após mesmo salvamento | ambos: controlado `0x00000082`, área `0x000000ca` |
| M2 | Canal de estado com autoridade do host em dois jogos | `tools\sync-test.ps1`: host 34 ordens de controle; 3.404 enviados / 2.185 recebidos; convidado 2.169 enviados / 3.346 recebidos; **0 descartados**; convidado aplicou **830** posições por `SetPosition`; distância final host/convidado **0,00 m** |
| M3 | **Entrada pela rede sem copiar arquivos manualmente** | `tools\join-test.ps1`: host gravou vaga manual 91 e serviu pasta TCP; convidado recebeu 4 arquivos, gravou no perfil, carregou (`game loaded: slot 91`), alcançou área do host; sincronização continuou (569 posições aplicadas, distância final 0,15 m) |
| M4 | **Avatares separados**: host Warden, convidado companheiro | `tools\two-avatar-test.ps1`: host criou/contratou mabari por `AddToParty` antes de salvar (grupo 2); convidado entrou e selecionou índice 1 por `SelectPartyMemberIndexMessage`; host controlou `0x82` espelhando `0x363` (4.815 aplicações, 0,26 m) e convidado o inverso (5.274, 0,21 m), mesma área |
| M5 | **Canal de vida/morte hostil** | `tools\combat-test.ps1`: host criou ogro com IA desativada (indicador nativo) antes de salvar; causou dano após conexão; convidado recebeu mesmo identificador e vida (`220 → 0`, incluindo morte), aplicou 13 vezes |
| M6 | **Pacote distribuível, configuração e LAN** | `dao-coop-0.6.0.zip` (carregador, endereços, plugin, notas, `daocoop.ini.example`, 6,1 MB) compilado pela predefinição de distribuição; host só com `DAOLIB_INSTANCE` leu papel, carregamento e transferência de `daocoop.ini`; teste de entrada/sincronização **passou na distribuição** e novamente com endereço LAN não loopback (`192.168.56.1`, sockets em `0.0.0.0`) |
| M7 | **Arbitragem com dano real no host** | `tools\attack-test.ps1`: criatura do convidado atacou ogro; comando virou solicitação; host validou atacante/alvo (convidado conhecido, identificador crescente, ambos vivos, mesma área, alvo hostil), ordenou ataque ao próprio jogo e respondeu; ataque chegou (`attack: request ... accepted`), vida do ogro caiu e espelho acompanhou; posições seguiram sincronizadas. `tools\demo-fight.ps1` mostra ambos lutando com mesmo ogro, ataques espelhados |
| M8 | **Morte e reanimação de jogador** | `tools\death-test.ps1` **PASS**: host morto de propósito por hook; mundo segue com convidado/grupo vivo (linhas de estado continuam); hostil derrotado pelo hook; reanimação restaura vida máxima dos caídos e controle do host (avatar com vida positiva). Correção encontrada: cadáver na tabela hostil não conta mais como combate em andamento |
| M9 | **Reentrada após host carregar outro salvamento** | `tools\reload-test.ps1` **PASS**: host carregou segundo salvamento durante sessão, regravou vaga de transferência e serviu; convidado viu indicador de recarga, reinicializou entrada, recebeu/carregou vaga nova (tela de carregamento), reselecionou integrante; sem reinício |
| M10 | **Painel Event Log interno com SWF do plugin** | `tools\ui-shot.ps1` e `tools\ui-join-shot.ps1`: painel ActionScript 2 (`ui/eventlog/frame_1/DoAction.as`) compilado em `ui/coop_eventlog.swf` (SWF 8, `$TitleFont`/`$BodyFont` importadas de `gfxfontlib.swf`) com FFDec; acrescentado ao HUD por `dao::gui::AddScreen`, preenchido de `EventLog` por `Movie::SetArray`/`SetVariable` com contador de revisão; capturas mostram linhas de exemplo, evento real "Another player joined the game.", combate com nomes e filtros ALL/COMBAT/MULTI/SYSTEM |
| M11 | **Pacote 0.7.0 com tela de eventos, retestado na distribuição** | `tools\package.ps1 -Version 0.7.0` criou `dao-coop-0.7.0.zip` (7,0 MB: carregador, endereços, plugin, SWF junto dele, notas, `daocoop.ini.example`); nessa versão, `tools\attack-test.ps1` (pedido aceito/resolvido no host) e `tools\reload-test.ps1` (host troca salvamento, convidado recarrega/retorna), ambos **PASS** |
| M12 | **Eventos compartilhados e jogadores independentes (0.7.1)** | Pacote de eventos do protocolo 8 compartilha linhas (ambos têm as duas entradas: `independence-test`); receptor único despacha por `ReceiveAny` (recepções por tipo bloqueavam-se e host deixava de ver convidado). Sem índice configurado, convidado assume 1 (`party: the guest will take party index 1 by default`); espelho não o reposiciona antes da troca (`applied` 0 depois); anda 2,14 m afastado do host parado e cópia acompanha a 1,12 m; `walk-test` também passa na distribuição |
| M13 | **Instalação por comando único e reverificação LAN (0.7.4)** | Distribuição inclui `install.ps1`: `-GameDir <game folder> -Role host|guest [-PeerIp <host address>] -Apply` extrai e grava `daocoop.ini` para papel (backup do antigo; simulação sem `-Apply`); testado em pasta temporária com `daorigins.exe` fictício (plano, aplicação, ini convidado e `.bak`). LAN reverificada em 0.7.3: `independence-test -PeerIp 192.168.56.1` (ambos 0.0.0.0, `dropped 0`, ambos com duas entradas) |

## <a id="qa"></a>QA

- Compilar: `tools\build.ps1 -Preset debug` (VS 2022 C++, x86, vcpkg: detours/spdlog/directxtex, `x86-windows-static-md`). Implantar só em cópia isolada: `tools\deploy.ps1` (recusa outros caminhos).
- Executar: scripts iniciam host, esperam mundo, iniciam convidado, esperam mundo, conduzem cenário por 60 a 180 s e leem ambos os logs. Suíte: `sync-test`, `join-test`, `two-avatar-test`, `combat-test`, `attack-test`, `death-test`, `reload-test`, `pause-test`, `ui-shot`, `ui-join-shot`; cada um verifica evidências nos dois.
- **Último resultado 2026-10-23: PASS** para `independence-test` (loopback e LAN), `walk-test`, `attack-test`, `death-test`, `reload-test`, `ui-shot`, `ui-join-shot`; `demo-fight` mostra luta compartilhada. Um cenário por teste, dois clientes reais num PC por UDP loopback ou seu endereço LAN não loopback; nível `automated`, não `verified-playthrough`.

## <a id="how-to-play"></a>Como jogar

Ainda não concluído, mas dois jogadores já entram e se movem num mundo:

1. Ambos: executem `install.ps1` (extrai e grava `daocoop.ini` conforme papel: `-GameDir "<game dir>" -Role host -Apply` ou `-Role guest -PeerIp <host LAN address> -Apply`), ou extraiam `dao-coop-0.7.4.zip` na pasta com jogo fechado. Inclui carregador DAOLib, endereços e plugin; nada mais instalado.
2. Copiem `daocoop.ini.example` para `bin_ship\daolib\plugins\daocoop\daocoop.ini`.
3. Host: `role = host`, `handoff = 1`, `add_companion = 1`; carregue salvamento e espere segundos. Convidado: `role = guest`, `peer = <host LAN address>`, `join = 1`, `select_party = 1`; espere no menu.
4. Permita UDP 45830 e TCP 45832 entrando no host, UDP 45831 no convidado.

Por enquanto só LAN, sem menu interno: interface é o ini. Fontes e instalação: https://github.com/vmosenkov/dao-coop.

## <a id="known-issues"></a>Problemas conhecidos

- Em andamento: hospedar/entrar configurado por `daocoop.ini`, não menu.
- Só LAN: endereço testado numa máquina por sua interface não loopback; sem dois PCs físicos ou transporte internet ainda.
- Combate sincroniza posição, vida, alvos, ordens de ataque e morte, não animações/efeitos: golpes podem estar em fases diferentes, e log registra inícios e mortes, não cada acerto/número de dano. IA é do host; cópia convidada só segue estado espelhado.
- Queda do jogador tratada (mundo continua, grupo reanimado após luta), mas sem integração de fim/carregamento para convidado cujo jogo termina e sem sincronização de missões/cenas.
- Ainda sem sincronização de inventário, missão, diálogo, efeito ou transição.
- Só executáveis GOG testados (em instalação Steam); biblioteca aceita invólucros EA/Steam, não testados aqui.
- Maioria em Debug; `attack-test`, `reload-test`, `independence-test` (loopback/LAN), `walk-test`, `ui-menu-test`, `ui-shot` também em distribuição. `combat-test` falha no salvamento Fort Drakon (ogro `CreateObject` inativo não retornado pela consulta hostil); luta coberta por `attack-test`, `walk-test`, `demo-fight`.

## <a id="next-steps"></a>Próximos passos

1. Replicar restante de animações/efeitos (acertos, mortes, feitiços; golpe da cópia já aparece) para telas mostrarem mesma luta; depois saque e sacos de cadáveres.
2. Segundo PC físico em LAN (endereço já exercitado num PC), depois transporte internet (retransmissão Steam).
3. Transições com alinhamento de objetos (`OnAreasBuild`); fluxo de hospedar/entrar além do ini; interface restante (histórico rolável, detalhes de eventos, nomes em linhas multiplayer).

1. Arbitragem real de combate: ataques convidados enviados/resolvidos no host (canal de vida hostil comprovado; dano ainda aplicado pelo plugin host no teste), depois efeitos e saque.
2. Segundo PC físico em LAN (endereço exercitado numa máquina), depois internet (retransmissão Steam).
3. Transições com alinhamento de objetos (`OnAreasBuild`); hospedar/entrar além do ini; ampliar suíte com cenários de combate e transição.
