# <a id="agent-notes-dragon-age-origins"></a>Notas de agentes: Dragon Age: Origins

Notas de trabalho para adicionar modo cooperativo a **Dragon Age: Origins - Ultimate Edition** (Steam app 47810, 1.05.13263.0). Plano e evidências ficam no repositório próprio `dao-coop`; este é o registro do colaborador para o núcleo, ponto de partida do próximo agente. Iniciado em 2026-10-20.

## <a id="triage-phase-0"></a>Triagem (etapa 0)

| | |
|---|---|
| Jogo | Dragon Age: Origins - Ultimate Edition, 2009 |
| Loja / versão | Steam, app 47810, build id 21245176, jogo **1.05.13263.0** (compilações GOG, EA e Steam diferem; todas são 1.05.13263.0) |
| Motor | **Eclipse** (próprio da BioWare, Aurora aprimorado, motor de Neverwinter Nights), x86 de 32 bits, RTTI intacto |
| Modo cooperativo existente | **nunca houve um público**; entrada do diretório é uma lacuna |
| Código-fonte disponível | não; projeto fechado de descompilação de 2026 cerca de 60% concluído planeja rede/co-op (não é um artefato disponível) |
| Superfície de modificação | carregador de plugins nativos (DAOLib, estilo SKSE); VM de scripts com 827 comandos; barramento de mensagens do motor; interface Flash |
| Caminho | 2 (criar do zero), mas **não do zero em engenharia reversa**: DAOLib já mapeia o motor. |

## <a id="what-exists-phase-1-checked-2026-10-20"></a>O que existe (etapa 1, verificado em 2026-10-20)

- **Nenhum mod cooperativo público de DAO.** Pesquisados GitHub (repositórios/código/tópicos), Nexus, ModDB, GameBanana, Steam Community, Reddit, fóruns russos/alemães/poloneses, archive.org, YouTube, central de handlers Nucleus Co-op. Evidências negativas e registro das buscas nas notas da sessão; o resumo abaixo é o relevante.
- **DAOLib** - https://github.com/Whocares66-Dev/DAOLib - GPLv3, carregador estilo SKSE/CommonLibSSE (`dinput8.dll`) e biblioteca C++ para DAO 1.05.13263.0 em GOG/EA/Steam. Biblioteca de endereços (mais de 100 mil IDs estáveis) em https://github.com/Whocares66-Dev/DAOAddressLibrary. Versões públicas v0.1.0 (2026-10-10) até v0.5.0 (2026-10-18). Expõe: os 827 comandos de script chamáveis/interceptáveis, mensagens do motor, callback por quadro na thread de scripts, estado de objetos/criaturas, ordens semelhantes a cliques, injeção de entrada, telas Scaleform próprias, hooks de salvamento e arquivos auxiliares de salvamento, modos/pausa.
- **DAOKadanMP** - `Whocares66-Dev/DAOKadanMP`, **privado** (GitHub 404 sem autenticação, ausente na lista pública de repositórios). Única tentativa multiplayer ativa; evidências apenas no texto público de issues DAOLib/DAOEluvianMCP: dois processos no mesmo salvamento, entrada por endereço na área de transferência, correspondência parcial de IDs entre host/convidado, baú compartilhado, carregamento de salvamentos feitos na sessão. Lacunas dessas issues: corpos/itens de mortos sem sincronização (DAOLib #103), golpes a mais de 60 m da câmera do host sem efeito (DAOLib #88). Sem versão, licença ou download: contato a investigar, não dependência.
- **DAOEluvianMCP** - https://github.com/Whocares66-Dev/DAOEluvianMCP - plugin de bancada de testes MCP GPLv3: expõe um jogo ativo por MCP/HTTP, controla-o e suporta múltiplas instâncias em portas próprias. Estrutura pretendida de QA automatizado para dois clientes.
- **DAO Turn Based** (Nexus 7053), **DAO Photo Cam** (7060), **DAO Elgara Shaders** (7061), **Extended Item Variations** (7069) - plugins públicos DAOLib; nenhum com rede. Descobertas do mod por turnos sobre motor (pausa, fila de comandos, relógio) em `dev/TURN_BASED.md` de DAOLib.
- **Projeto de descompilação de 2026** - usuário Reddit `Shot_Let_1344`, 6 desenvolvedores, cerca de 3 anos, 60% descompilado/55% vinculado de 34.415 funções; lançamento só perto de 90% (meta 2027), **planeja** 64 bits, controle, inventários por jogador, reformulação de pausa e possível suporte de rede e campanhas cooperativas. Ainda sem repositório, site ou compilação. Trate como possibilidade futura; nenhum vínculo público com o autor de DAOLib encontrado.
- **xoreos** (reimplementação Aurora GPLv3) tem DAO como alvo, mas só jogabilidade parcial como espectador, sem rede. **OpenDAO / Nikami Aurora** é runtime de compatibilidade Godot MIT separado; sem multiplayer.

## <a id="engine-facts-that-shape-the-design"></a>Fatos do motor que orientam o projeto

- Sem rede ou divisão cliente/servidor; uma criatura controlada por vez, um inventário do grupo, tempo real com pausa global, uma câmera de diálogo/cena.
- Lógica na VM de scripts interna, numa thread; comandos precisam ser chamados nela (DAOLib fornece callback por quadro).
- Existiu um modo multiplayer, cortado durante o desenvolvimento (entrevistas de 2021).
- Duas cópias podem rodar num PC como **instâncias nomeadas** DAOLib (`DAOLIB_INSTANCE=<name>`): mutex e perfil Documents próprios, inicializados uma vez pelos salvamentos do perfil padrão.
- Um salvamento é uma pasta; o convidado pode receber o do host, gravá-lo no próprio perfil e carregar; ambos concordam em todos os IDs de objeto (`dev/SAVES.md` de DAOLib, observado em 2026-10-12 na sessão do mod privado: convidado no mundo do host 9 a 19 s depois).

## <a id="chosen-approach"></a>Abordagem escolhida

Dois processos, autoridade do host: convidado entra por **transferência de salvamento**, seguida de sincronização de estado (jogadores, ordens, hostis, efeitos, transições), com dano resolvido pelo host. Ambos compartilham o grupo (sem precisar criar representantes: os mundos contêm os mesmos objetos). UDP em LAN primeiro (jogadores na mesma rede local), retransmissão Steam/Spacewar depois. Projeto e marcos completos em `dao-coop/docs/DESIGN.md`.

## <a id="session-log-2026-10-20"></a>Registro da sessão (2026-10-20)

- Jogo assumido: cranebeaker/coop-anything#79. Lacuna do diretório atualizada com DAOLib / DAOAddressLibrary / DAOEluvianMCP, mod privado KadanMP, plano de descompilação e issue de indicação de trabalho.
- Identidade registrada: executável `bin_ship\daorigins.exe`, 9.674.752 bytes, FileVersion 1.05.13263.0, SHA-256 `A79621C2D2020C6F838096150E30F8E51FA263DBC9121E04E3D8C633975892F8`; cópia ativa é **compilação GOG** (sem `.bind`, timestamp de vínculo 0x4eb19d53), com executável original envelopado pelo Steam guardado ao lado como backup; depot Steam 47811, build id 21245176.
- Ambiente verificado: carregador DAOLib 0.5.0 funcionando na instalação (`loader.log`: 103293 IDs de endereço, ponto de entrada redirecionado, menu principal alcançado); duas **instâncias nomeadas** (`DAOLIB_INSTANCE=host` e `=guest`) rodaram lado a lado numa cópia completa isolada, cada uma com perfil Documents próprio inicializado pelos salvamentos, sem escrita no perfil real.
- Esqueleto do plugin (`dao-coop`) compila com DAOLib, VS 2022 C++ e vcpkg (detours/spdlog/directxtex, triplet `x86-windows-static-md`).
- Marcos 0 e 1 verificados no jogo (2026-10-20): plugin compilado carrega (`daocoop.dll: loaded` no log) e lê estado ativo (`mode explore`, barra do grupo, ID/área/posição/vida da criatura controlada); duas instâncias nomeadas lado a lado, em perfis próprios e no mundo, após carregar o mesmo salvamento **concordaram no ID da criatura controlada e no ID da área**, alinhamento necessário à entrada por transferência. Estrutura completa de teste de duas instâncias executada; rede ainda inexistente (marco 2 a seguir).

- BioWare sem modo cooperativo em 2009: https://www.eurogamer.net/dragon-age-has-no-co-op-multiplayer
- Modo multiplayer cortado (entrevistas de 2021): https://www.thegamer.com/dragon-age-origins-multiplayer-cut/
- DAOLib: https://github.com/Whocares66-Dev/DAOLib , documentação https://whocares66-dev.github.io/DAOLib/
- DAOAddressLibrary: https://github.com/Whocares66-Dev/DAOAddressLibrary
- DAOEluvianMCP: https://github.com/Whocares66-Dev/DAOEluvianMCP
- DAO Turn Based (Nexus): https://www.nexusmods.com/dragonage/mods/7053
- Projeto de descompilação na imprensa: https://www.pcgamesn.com/dragon-age-origins/modders-decompiling-source-code
- Discussão/ wiki da linhagem do motor DAO: https://en.wikipedia.org/wiki/Dragon_Age:_Origins
- xoreos: https://github.com/xoreos/xoreos
- Aplicativo Steam: https://store.steampowered.com/app/47810/Dragon_Age_Origins__Ultimate_Edition/

## <a id="2026-10-23--combat-arbitration-deathrevive-rejoin-in-game-event-log"></a>2026-10-23 - arbitragem de combate, morte/reanimação, retorno, Event Log interno

Tudo verificado no jogo na instalação isolada; os scripts citados estão no repositório `dao-coop`.

- **Arbitragem de combate** (`tools\attack-test.ps1`, PASS). `dao::commands::OnStart` do convidado vê a ordem de ataque de sua criatura; o plugin a transforma em AttackRequestPacket (ID da solicitação, atacante, alvo), impedindo ataque local. Host valida (convidado conhecido, ID crescente, objetos existentes, alvo vivo, mesma área, hostil), chama `dao::orders::Attack` no próprio jogo e responde AttackResultPacket; convidado repete o ID duas vezes numa resposta de atacante inválido. Host repete a ordem a cada cerca de 120 quadros para completar o golpe; espelhamento de posição é ignorado só nos 30 primeiros quadros. `tools\demo-fight.ps1` mostra ambos lutando contra o mesmo ogro.
- **Morte e reanimação** (`tools\death-test.ps1`, PASS). Queda do jogador host não encerra o mundo enquanto houver membro vivo; após combate, `RevivePartyAfterFight` leva a vida dos caídos de zero ao máximo e devolve o controle ao avatar do host. Cadáver na tabela de hostis não significa mais combate em andamento (isso impedia reanimação).
- **Retorno do convidado** (`tools\reload-test.ps1`, PASS). Quando o host carrega outro salvamento durante a sessão, `OnGameLoaded` (segundo carregamento e seguintes) marca mundo recarregado, salva novamente o slot de transferência e o serve; convidado vê o indicador, reinicializa entrada, recebe e carrega o novo slot (tela de carregamento) e seleciona novamente seu membro do grupo.
- **Event Log interno** (`tools\ui-shot.ps1`, `tools\ui-join-shot.ps1`, PASS). Tela HUD SWF 8 do plugin: fonte ActionScript 2 (`ui/eventlog/frame_1/DoAction.as`) compilada por FFDec para `ui/coop_eventlog.swf`, com `$TitleFont`/`$BodyFont` importadas de `gfxfontlib.swf`; sequência e gerador do invólucro adaptados de `tools/movie.py` de DAOTurnBased (GPLv3, mesmo autor de DAOLib). Plugin adiciona a tela com `dao::gui::AddScreen(L"CoopEventLog", L"coop_eventlog", dao::gui::kLayerHud)` e `ShowScreen`, envia as oito últimas linhas de `EventLog`, categorias e revisão por `Movie::SetArray`/`SetVariable`; tela redesenha só em nova revisão. Painel se organiza por `dao::world::ScreenSize()` em pixels, tem abas ALL/COMBAT/MULTI/SYSTEM e se recolhe à última linha ao clicar. Capturas em `dao-coop/docs/images/`.
- **Nomes de criaturas no log**: `dao::script::api::GetName` (comando 275) fornece "?????", "????????", "???"; log em UTF-8 e ponte da interface converte para caracteres largos por `MultiByteToWideChar` para AS2.
- Também verificados antes na mesma sessão: canal de dano/morte, pacote de distribuição pelo endereço LAN, acordo de pausa. `docs/STATUS.md` no projeto contém evidências de cada rodada.

## <a id="2026-10-23-later--shared-event-log-and-independent-players"></a>2026-10-23 (mais tarde) - Event Log compartilhado e jogadores independentes

O testador relatou eventos diferentes nos painéis e jogadores arrastados para uma posição única. Causas e correções:

- **Dessincronização do log.** Cada jogo escrevia só os eventos gerados localmente (host com linhas de combate, convidado com entrada). Protocolo 8 adiciona `EventPacket` (232 bytes, categoria + texto UTF-8): `Notify` envia cada linha, receptor a adiciona ao próprio `EventLog` (`event(remote): ...`).
- **Bug de transporte revelado.** Buffer de pacotes pendentes dimensionado pelo pacote de estado (176), mas evento tem 232; cada tipo tinha `Receive` próprio varrendo o socket e retendo um datagrama pendente. Com quarto tipo, as varreduras se bloqueavam por falta de acesso (host relatava `recv 0`, convidado descartava centenas). Corrigido com `sizeof(EventPacket)` e único loop de despacho `Transport::ReceiveAny` no plugin.
- **Jogadores presos na mesma posição.** Convidado sem `select_party` controlava o Warden do host; o espelhamento reescrevia sua posição com a do host a cada pacote (teleportado de volta). Agora assume índice 1 por padrão; espelhamento ignorado até a troca e contadores de aplicação começam dali.
- Automatizado: `independence-test.ps1` (IDs diferentes, `applied` do convidado 0, distância máxima 2,14 m, representante 1,12 m, ambas as linhas de entrada em ambos os logs) e `walk-test.ps1` PASS na distribuição 0.7.1. `combat-test` com ogro artificial não passa no salvamento Fort Drakon: o ogro de `CreateObject` não é retornado pela consulta de hostilidade ali; caminho de combate coberto por `attack-test` e `demo-fight`.
- **Caminho LAN reverificado em 0.7.3** (2026-10-23, endereço desta máquina `192.168.56.1`): `independence-test -PeerIp 192.168.56.1` PASS; ambos vinculados a `0.0.0.0` e enviando ao endereço LAN, `dropped 0` nos dois lados, pacote de evento levando ambas as entradas aos dois logs. Dois PCs físicos continuam sem teste.
