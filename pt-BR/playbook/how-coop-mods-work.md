# <a id="how-existing-co-op-mods-work"></a>Como funcionam os mods cooperativos existentes

Objetivo: dar a um agente sem mod anterior em que se apoiar conhecimento suficiente para criar modo cooperativo do zero num jogo de um jogador. Esta página aborda os problemas comuns a todos os projetos, como os projetos importantes os resolveram, as ferramentas por tipo de motor e a ordem de implementação.

Regras de fontes: afirmações sobre projetos têm links. Quando as fontes consultadas não informaram algo, esta página usa `unknown` em vez de adivinhar. Observado significa fato de README ou documentação; inferido significa interpretação de nomes de arquivos ou organização. Nada substitui ler o código do próprio projeto antes de copiar sua arquitetura.

Páginas relacionadas: [engine-families.md](engine-families.md), [reverse-engineering.md](reverse-engineering.md), [methods.md](methods.md), [automated-qa.md](automated-qa.md), [reviving-abandoned-mods.md](reviving-abandoned-mods.md).

---

## <a id="1-the-problems-every-project-solves"></a>1. Os problemas que todo projeto resolve

Todos os projetos abaixo respondem às mesmas oito perguntas. Defina sua resposta a cada uma antes de escrever código de rede.

### <a id="11-remote-players-on-screen-puppets"></a>1.1 Jogadores remotos na tela (representantes)

Um jogo de um jogador tem exatamente um objeto de jogador ligado a entrada, câmera e interface. Um jogador remoto é um segundo objeto com aparência de jogador, mas cujo estado vem da rede, não da entrada local.

- sm64coopdx indexa jogadores localmente: `gMarioStates[0]` é sempre o jogador local; a ordem de `gMarioStates`, `gNetworkPlayers` e `gPlayerSyncTable` difere em cada cliente, e um índice global é o identificador estável ([espelho da documentação de globais Lua](https://bytes.keithhacks.cyou/etc/sm64coopdx/raw/tag/v1.0.4/docs/lua/globals.md)).
- Nitrox lista movimento, animações básicas e HUD de jogadores remotos como trabalho concluído ([README](https://github.com/SubnauticaNitrox/Nitrox)).
- Guias comunitários descrevem HKMP como uma cópia de cada jogador no mundo dos outros ([guia comunitário](https://geroyuni.notion.site/hkmp)).

Padrão: criar um representante por jogador remoto, controlá-lo pela posição, rotação, animação e equipamentos recebidos, interpolar entre atualizações e nunca deixá-lo ler entrada local.

### <a id="12-who-owns-each-entity-authority"></a>1.2 Quem controla cada entidade (autoridade)

Alguém precisa decidir o que um NPC faz. Opções encontradas:

| Modelo | Exemplo | Fonte |
|---|---|---|
| Um host executa toda a IA; demais espelham | OOT True Co-op: uma instância executa a IA; outra mostra os mesmos inimigos; golpes do outro jogador são conferidos pela autoridade | [OOT True Co-op](https://github.com/bghill95/OOT-True-Co-op) |
| Autoridade por área atribuída a um jogador | `Cell` de TES3MP guarda autoridade como GUID RakNet, com `setAuthority` e `hasLocalAuthority` | [Cell.hpp](https://git.cijber.net/mirror/openmw-tes3mp/src/branch/master/apps/openmw/mwmp/Cell.hpp), [resumo de commits Cell.cpp](https://git.cijber.net/mirror/openmw-tes3mp/src/commit/060ebe3d4ac2e78d4acf094a4979de1e29cee7aa/apps/openmw-mp/Cell.cpp) |
| Servidor mantém estado canônico, clientes enviam ações | Nitrox segundo espelho de documentação de terceiros (fonte secundária; confira o original) | [espelho](https://www.mintlify.com/Papela/Nitrox-Cracked-Mod/development/networking) |
| Mundo do líder é a fonte da verdade | Grupos de Skyrim Together Reborn | [guia Wabbanode](https://wabbanode.com/help/skyrim-together/understanding-parties-in-skyrim-together-reborn) |
| Ninguém controla: cada cliente simula sua cópia | HKMP segundo guias: inimigos têm vida separada | [guia HKMP](https://geroyuni.notion.site/hkmp) |
| Replicação do motor decide | Unreal Engine 1 (HX) | veja 2.9 |

Espere precisar de regra de transferência (o responsável sai da célula ou desconecta). OOT True Co-op documenta uma: se um jogo falha, os inimigos do outro pausam por cerca de 1,5 s e retomam com IA local ([README](https://github.com/bghill95/OOT-True-Co-op)).

Copie resultados, não eventos. Quando um NPC morre na máquina responsável, mostre-o morto nas demais como *estado*, sem executar novamente a lógica de morte: em Gothic 3 ela também avançava missões, concedia experiência e sorteava itens; cada morte espelhada duplicava esses efeitos no cliente até a cópia definir só o estado morto (G3 Together, [games/gothic-3/NOTES.md](../games/gothic-3/NOTES.md), etapas 3c e C). O mesmo vale para efeitos de diálogo: transmitir o estado resultante é mais fácil que interpretar cada comando.

### <a id="13-world-quest-and-story-state"></a>1.3 Estado do mundo, missões e história

Parte omitida pela maioria dos projetos, e a mais difícil nos jogos de um jogador.

- TES3MP declara sincronização muito ampla de jogadores, NPCs, mundo e missões; precisa de lista permitida de variáveis de script cliente para evitar excesso de pacotes ([README](https://github.com/TES3MP/openmw-tes3mp)). Isso é possível porque o motor é aberto.
- Skyrim Together Reborn sincroniza missões pelo líder e orienta os membros a esperá-lo antes de avançar ([Wabbanode](https://wabbanode.com/help/skyrim-together/understanding-parties-in-skyrim-together-reborn)).
- Anchor de Ship of Harkinian sincroniza indicadores e concessão de itens para todos da sala/equipe ([README Anchor](https://raw.githubusercontent.com/garrettjoecox/Anchor/main/README.md)).
- Archipelago sincroniza só itens; é estrutura de randomizadores, não mod de estado do mundo ([Archipelago](https://github.com/ArchipelagoMW/Archipelago)).
- Observado em nossa análise NV:MP (fechado, portanto descoberta local, não fonte pública): servidor de história sem sincronização de missões, atores de missão deliberadamente não sincronizados. Trate como `unverified` para outras compilações.

Regra prática: encontre armazenamento de indicadores/variáveis (etapas, globais, eventos). Se toda a história passa por ele, replicar suas escritas de uma autoridade fornece a maior parte do modo cooperativo de história.

### <a id="14-saves-and-level-transitions"></a>1.4 Salvamentos e transições de fase

- Skyrim Together Reborn: salvamentos no PC do líder, não no servidor ([resumo de guias](https://wabbanode.com/help/skyrim-together/understanding-parties-in-skyrim-together-reborn) cobre salvamento rápido; a localização vem de guias secundários, confira).
- DK2 co-op: progresso de campanha e desbloqueios salvos somente no PC host ([DK2 co-op](https://ciphercom.github.io/dk2-coop)).
- Anchor carrega estado salvo de jogador remoto ao entrar ([Anchor](https://raw.githubusercontent.com/garrettjoecox/Anchor/main/README.md)).
- Seamless Co-op destaca sessões persistentes pelo mundo, em vez de acabar a cada chefe ([Gamewatcher, secundário](https://www.gamewatcher.com/elden-ring-seamless-co-op-mod)).

Decida cedo: qual salvamento é canônico e o que os demais persistem (normalmente nada ou só inventário).

O salvamento pode ser mecanismo de entrada numa missão. BattleTech cooperativo não regenera contrato no convidado (conteúdo procedural e scripts leem toda a campanha); host cria salvamento de combate em memória nas instruções da missão e envia; convidado carrega como reinício de missão, ambos começando a mesma missão do início e vendo a abertura (salvamento carregado difere de estado ativo, e reiniciar sorteia novamente; [lessons.md](lessons.md), 74 e 79). Convidado nunca salva: está na campanha host e escreveria nos próprios slots ([games/battletech](../games/battletech/README.md)).

Confira o que um salvamento captura com remotos presentes. Em Gothic 3, corpo remoto é cópia do herói; salvar com ele aborta ao carregar por haver mais de um herói. É preciso interceptar a própria função de salvar para removê-los antes, inclusive no menu. Arquivo auxiliar junto a cada salvamento guarda estado do mod; cada jogador mantém personagem por salvamento host. Quem entra carrega o salvamento enviado pelo host e restaura seu personagem por cima (G3 Together, etapa D em [games/gothic-3/NOTES.md](../games/gothic-3/NOTES.md)).

### <a id="15-cutscenes-and-dialog"></a>1.5 Cenas e diálogos

Nenhuma fonte consultada ofereceu solução geral. Orientações e restrições observadas:

- DK2 co-op orienta deixar cenas terminarem ([DK2 co-op](https://ciphercom.github.io/dk2-coop)).
- Skyrim Together Reborn orienta só líder conversar com NPCs de missão e escolher respostas; outros veem escolhas em notificações ([Wabbanode](https://wabbanode.com/help/skyrim-together/understanding-parties-in-skyrim-together-reborn)).
- Nosso trabalho STALKER encontrou gatilhos que usam quem conversa como interlocutor, enquanto indicadores são globais do servidor (descoberta local ao ler scripts do complemento).

Opções: iniciador decide, líder decide ou votação. Cenas executadas em todos com barreira de espera, ou omitidas para não hosts. Marque `unknown` num jogo novo até testar.

### <a id="16-lockstep-versus-state-sync"></a>1.6 Lockstep versus sincronização de estado

| | Lockstep determinístico | Estado com autoridade host |
|---|---|---|
| Envia | somente entradas | estado (posição, vida, indicadores) |
| Banda | pequena, independente da quantidade | cresce com entidades |
| Exige | determinismo bit a bit, passo fixo igual, mesmo estado inicial | sem determinismo; leitura/escrita de estado |
| Falha como | dessincronização silenciosa | correções bruscas, entidades duplicadas/ausentes |
| Bom para | RTS, motores descompilados/reescritos tornáveis determinísticos | adaptação a jogo fechado inalterado |

Fatos lockstep segundo [Gaffer on Games](https://gafferongames.com/post/deterministic_lockstep/): só entradas; mesmos estado inicial, entradas e passo fixo; quadro n espera entrada n; determinismo até o bit, que pode quebrar entre compiladores, sistemas e ponto flutuante de depuração/distribuição; checksum de todo o estado por quadro detecta divergência.

KeeperFX é candidato, mas README consultado só informa protocolo multiplayer moderno, não modelo ([KeeperFX](https://github.com/dkfans/keeperfx)). `unknown` nas docs públicas; confira código (`net` e pacotes) antes de presumir.

Estado, banda e prioridade: [Gaffer on Games](https://gafferongames.com/post/state_synchronization/) descreve acumulador por objeto, enviando maiores dentro do orçamento de banda e comprimindo diferenças contra bases confirmadas.

Adaptações a jogos fechados de um jogador quase sempre usam estado com autoridade host: não se consegue tornar o motor determinístico.

Exceção: jogo com modo competitivo pode já ser determinístico onde importa. BattleTech (2018) encaminha cada ação de combate como `InvocationMessage` por manipulador único que reinicializa o gerador aleatório lógico com a semente da mensagem, para PvP de escaramuça. Campanha usa mesmo caminho; combate cooperativo usa lockstep dessas mensagens, ordenadas pelo host. Só IA não determinística (orçamento de raciocínio pelo relógio real); apenas IA host pensa, enviando ordens como mensagens normais ([games/battletech](../games/battletech/README.md)). Procure essa camada antes de escolher estado.

### <a id="17-interest-management"></a>1.7 Gerenciamento de interesse

Envie só o próximo ou relevante a cada cliente. Evidências:

- Acumulador Gaffer acima é forma mais simples (prioridade por importância, não distância).
- Nitrox lista sincronização de mundo a longa distância; espelho diz não sincronizar posições exatas de criaturas, mas criação, vida e morte sim ([README](https://github.com/SubnauticaNitrox/Nitrox), [espelho secundário](https://www.mintlify.com/Papela/Nitrox-Cracked-Mod/features/synchronization)).
- TES3MP limita autoridade/atores a células (1.2).
- Relevância Unreal e PVS Source são versões nativas. Páginas Valve/Unreal retornaram 403 ao buscador; sem citação aqui.

Comece sem esse gerenciamento. Acrescente quando medições mostrarem custo de CPU ou banda.

Meça cedo o alcance de processamento do motor: limita autoridade host mais que banda. Gothic 3 só simula até cerca de 40 m da câmera (`Entity.ROI`); entidades distantes existem congeladas; estado escrito (morte) era redefinido ao voltar a processar. Resultados distantes vão a um diário aplicado por cada máquina ao processar a entidade (G3 Together, explorações 1 e 5 e etapa C em [games/gothic-3/NOTES.md](../games/gothic-3/NOTES.md)).

### <a id="18-late-join"></a>1.8 Entrada tardia

Cliente precisa alcançar estado atual. Abordagens:

- Anchor: carregar estado salvo remoto ([Anchor](https://raw.githubusercontent.com/garrettjoecox/Anchor/main/README.md)).
- Lua servidor TES3MP salva/carrega a maior parte dos dados sincronizados ([resumo de busca](https://git.cijber.net/mirror/openmw-tes3mp/src/commit/060ebe3d4ac2e78d4acf094a4979de1e29cee7aa/apps/openmw-mp/Cell.cpp); trecho secundário, confira).
- Skyrim Together Reborn: segue mundo do líder ([Wabbanode](https://wabbanode.com/help/skyrim-together/understanding-parties-in-skyrim-together-reborn)).

Implemente cedo captura na entrada (estado completo, depois diferenças). Também serve para reconexão e como oráculo de teste.

---


## <a id="2-projects"></a>2. Projetos

Cada entrada: método de hook, autoridade/transporte, sincronização e desconhecidos.

### <a id="21-tilted-online-and-skyrim-together-reborn-tiltedevolution"></a>2.1 Tilted Online e Skyrim Together Reborn (TiltedEvolution)

- Repositório: [tiltedphoques/TiltedEvolution](https://github.com/tiltedphoques/TiltedEvolution). Estrutura multiplayer para Bethesda, atualmente Skyrim Special Edition.
- Organização observada: `Code/client` contém hooks do motor, tipos obtidos por engenharia reversa e lógica de sincronização; `Code/server` compila `STServer.dll`, hospedada por `server_runner`; `Code/encoding` reúne mensagens compartilhadas; `Code/immersive_launcher` inicia com cliente carregado; `Code/skyrim_ui` é interface Angular em sobreposição Chromium Embedded Framework; compilação xmake ([README](https://github.com/tiltedphoques/TiltedEvolution)).
- Submódulos: TiltedReverse, TiltedUI, TiltedConnect, TiltedHooks, TiltedScript, cpp-httplib ([.gitmodules](https://raw.githubusercontent.com/tiltedphoques/TiltedEvolution/master/.gitmodules)). TiltedConnect é a camada superior da pilha sobre biblioteca de rede, incluindo fork de GameNetworkingSockets Valve ([TiltedConnect](https://github.com/tiltedphoques/TiltedConnect), [.gitmodules](https://raw.githubusercontent.com/tiltedphoques/TiltedConnect/master/.gitmodules)).
- Autoridade: dedicado e líder hospedando mundo (1.2).
- Desconhecidos nas fontes: técnica exata de hook (TiltedHooks existe, conteúdo não lido), regras por entidade, lista completa sincronizada.
- Lição: camadas de biblioteca de hooks, tipos obtidos por engenharia reversa, mensagens compartilhadas e DLL servidor são bom modelo para vários jogos.

### <a id="22-seamless-co-op-elden-ring-dark-souls"></a>2.2 Seamless Co-op (Elden Ring, Dark Souls)

- Autor LukeYui. GitHub só espelha página Nexus ([repositório](https://github.com/LukeYui/EldenRingSeamlessCoopRelease)); sem fonte ou relato técnico encontrados. Código fechado, arquitetura `unknown`.
- Comportamento de relatos secundários: inicializador próprio, sem matchmaking original/serviços FromSoftware; substitui invocar/sair por início de sessão via itens, mantém sessão pelo mundo, desativa invasões ([Gamewatcher](https://www.gamewatcher.com/elden-ring-seamless-co-op-mod), [Prima Games](https://primagames.com/tips/how-to-download-and-use-the-elden-ring-seamless-co-op-mod)).
- Correção de suposição comum: fontes não dizem que amplia a invocação original. Não descreva assim sem ler binário. Lição relatada é de produto: jogo já tem infraestrutura cooperativa; alteram-se regras de sessão (persistência, não encerrar após chefe).

### <a id="23-sm64coopdx-super-mario-64-decomp-port"></a>2.3 sm64coopdx (port da descompilação de Super Mario 64)

- [coop-deluxe/sm64coopdx](https://github.com/coop-deluxe/sm64coopdx), sucessor de [djoslin0/sm64ex-coop](https://github.com/djoslin0/sm64ex-coop) (arquivado), fork do port PC sm64ex. Sincroniza todas as entidades/fases e, diferente dos anteriores, inimigos/eventos.
- Hook: desnecessário; altera C descompilado diretamente (port é o código-fonte do jogo). Documentos em `docs/c/c.md`, `docs/lua/lua.md`.
- API Lua: campos por jogador `gPlayerSyncTable[]` automaticamente sincronizados com todos; objetos registrados com `network_init_object`, enviados por `network_send_object` ([globais Lua](https://bytes.keithhacks.cyou/etc/sm64coopdx/raw/tag/v1.0.4/docs/lua/globals.md), [manual.lua](https://bytes.keithhacks.cyou/etc/sm64coopdx/src/commit/96e21e13a1231e8e0268e0f01df8eca5243246b3/autogen/lua_definitions/manual.lua); espelho de tag antiga, API pode ter mudado).
- Desconhecidos: biblioteca de transporte, detalhes de topologia.
- Lição: modelo copiado pela maioria das descompilações cooperativas é representantes e sincronização por objeto com registro explícito.

### <a id="24-ship-of-harkinian-anchor-oot-true-co-op-ocarina-of-time"></a>2.4 Ship of Harkinian Anchor, OOT True Co-op (Ocarina of Time)

- [Anchor](https://github.com/garrettjoecox/Anchor): retransmissor genérico Go (`go run .` ou Docker, porta padrão 43383); cliente trata todo estado. Sincroniza salvamento na entrada, indicadores e itens por sala/equipe ([README](https://raw.githubusercontent.com/garrettjoecox/Anchor/main/README.md)).
- [OOT True Co-op](https://github.com/bghill95/OOT-True-Co-op): fork de Ship of Harkinian e Anchor para dois compartilhando mundo num PC. Acrescenta vida compartilhada, posição/animação espelhadas de inimigos e chefes. Uma instância autoritativa executa IA; outra mostra. Novos chefes exigem `ActorSyncAdapter`, não novo código de sincronização. Lacunas: inimigos miram Link autoritativo, sons/partículas IA só na autoridade; desativar `EnemySyncMirroring` retorna a vida compartilhada.
- Lição: indicadores/inventário rendem muito a baixo custo. Autoridade de inimigos é a fronteira e se beneficia de adaptador por tipo e opção de desativação.

### <a id="25-xrmpe-and-stalker-co-op"></a>2.5 xrMPE e STALKER cooperativo

- xrMPE é extensão multiplayer X-Ray; modo cooperativo distribuído como complementos do inicializador ([versões xrMPE](https://github.com/M4dMurloc/xrMPE_Launcher_Release); README sem conteúdo técnico). Notícia japonesa descreve 0.9 como mod de Call of Pripyat com Steam e cooperativo de quatro ([Game*Spark](https://www.gamespark.jp/article/2025/11/29/159983.html)).
- Se é fork completo: página ModDB apagada descrevia "X-Ray Multiplayer Engine-fork"; nenhum repositório encontrado. Trate como `unconfirmed`.
- Descoberta local ao extrair complemento (não fonte pública): lógica Lua X-Ray e LTX em `.db`, indicadores de missão globais do servidor transmitidos aos clientes, checksum do complemento no servidor exigindo cópias idênticas. Reproduza antes de confiar.
- Lição: motor multiplayer existente e lógica roteirizável exigem adaptação de scripts, não código de rede.

### <a id="26-tes3mp-morrowind-on-openmw"></a>2.6 TES3MP (Morrowind sobre OpenMW)

- [openmw-tes3mp](https://github.com/TES3MP/openmw-tes3mp): fork multiplayer OpenMW; servidor personalizável por Lua (CoreScripts); problemas restantes principalmente IA.
- Autoridade: `Cell` guarda GUID RakNet; atores locais/dedicados são conceitos separados tratados por `CellController` ([Cell.hpp](https://git.cijber.net/mirror/openmw-tes3mp/src/branch/master/apps/openmw/mwmp/Cell.hpp), [CellController.hpp](https://git.cijber.net/mirror/openmw-tes3mp/src/commit/73aa83aa03416ed748d108dd26b675d9846f8173/apps/openmw/mwmp/CellController.hpp)).
- Lição: motor aberto permite resultado mais completo (missões inteiras) e divisão limpa: fork do motor para hooks, Lua servidor para políticas.

### <a id="27-nitrox-subnautica-unity"></a>2.7 Nitrox (Subnautica, Unity)

- [Nitrox](https://github.com/SubnauticaNitrox/Nitrox): `NitroxPatcher`, `NitroxClient`, `Nitrox.Server.Subnautica`, `Nitrox.Launcher`, `Nitrox.Model`. Integração Harmony concluída; patcher modifica o jogo em execução.
- Espelho secundário: patcher Harmony com `Dynamic/` (só multiplayer) e `Persistent/`; inicializador aponta às bibliotecas Nitrox; mais de 130 pacotes tipados, UDP LiteNetLib, autoridade servidor ([arquitetura](https://www.mintlify.com/Papela/Nitrox-Cracked-Mod/development/architecture), [rede](https://www.mintlify.com/Papela/Nitrox-Cracked-Mod/development/networking)). Confira wiki original antes de copiar.
- Segundo README: movimento, animações, pegar/descartar itens, construir bases, energia, veículos, chat.
- Lição: Unity com carregador e Harmony é alvo moderno mais fácil. Intercepte métodos que criam/alteram coisas, serialize pacotes e aplique no servidor.

### <a id="28-hkmp-hollow-knight-unity"></a>2.8 HKMP (Hollow Knight, Unity)

- [HKMP](https://github.com/Extremelyd1/HKMP): complementos são assemblies como mods Hollow Knight, divididos entre cliente e servidor; servidor independente não conhece código do jogo; pacotes com IDs de enum e indicadores como `DropReliableDataIfNewerExists` ([wiki](https://github.com/Extremelyd1/HKMP/wiki)).
- Escopo segundo guias: principalmente posições; inimigos, itens e quebráveis individuais ([guia](https://geroyuni.notion.site/hkmp)).
- Desconhecidos: detalhes de hooks e transporte.
- Lição: servidor independente do jogo mais complementos específicos simplifica servidor e permite ampliar sincronização por recurso comunitariamente.

### <a id="29-hx-for-deus-ex-unreal-engine-1"></a>2.9 HX de Deus Ex (Unreal Engine 1)

- HX joga campanha original cooperativamente; página ModDB apagada ([ModDB](https://www.moddb.com/mods/hx)). Sucessor mantido com correções [cranebeaker/deus-ex-coop](https://github.com/cranebeaker/deus-ex-coop); dedicado Docker [MisterCalvin/dxhx-coop-server](https://github.com/MisterCalvin/dxhx-coop-server).
- Descoberta local: `HX.u` embute UnrealScript (centenas de classes), `HX.dll` nativa não tem fonte; correções em pacote separado de subclasses, não recompilando `HX.u`. Método nas notas do repositório.
- Lição: Unreal 1/2 exige principalmente scripts, pois motor já replica atores. Veja [engine-families.md](engine-families.md).

### <a id="210-nvmp-fallout-new-vegas"></a>2.10 NV:MP (Fallout New Vegas)

- Mod com servidor dedicado de história e DLL cliente; estado `partial` segundo [Co-Optimus](https://www.co-optimus.com/article/13884/fallout-new-vegas-co-op-mod-needs-beta-testers.html) (403 ao buscador; afirmação herdada do diretório).
- Rede fechada; nossa engenharia reversa é local e específica da versão (1.3). Lição pública: mod fechado sem missões pode receber plugin separado de extensão de scripts que sincroniza o armazenamento de missões.

### <a id="211-ragecoop-gta-v-story-mode"></a>2.11 RAGECOOP (história GTA V)

- [RAGECOOP-V](https://github.com/RAGECOOP/RAGECOOP-V): exige ScriptHookV e ScriptHookVDotNet 3.6.0+, usa Lidgren modificada, sincroniza balas, veículos, jogadores, NPCs, projéteis e ragdoll simples; suporta história, API de scripts/recursos ([README](https://raw.githubusercontent.com/RAGECOOP/RAGECOOP-V/main/README.md)).
- Desconhecidos: arquitetura servidor, frequência, conflitos.

### <a id="212-keeperfx-and-dk2-co-op"></a>2.12 KeeperFX e DK2 cooperativo

- [KeeperFX](https://github.com/dkfans/keeperfx): GPL-2.0, começou como descompilação, hoje reescrita C/C++ com protocolo multiplayer moderno. Modelo não descrito no README (1.6).
- [DK2 co-op](https://ciphercom.github.io/dk2-coop): baseado em [Flame](https://github.com/DiaLight/Flame); dois na mesma facção Keeper; UDP 7575; mesmas versões de jogo/pacote; progresso só no host. Modelo não informado.

### <a id="213-nucleus-co-op-split-screen"></a>2.13 Nucleus Co-op (tela dividida)

- [Nucleus Co-op](https://github.com/SplitScreen-Me/splitscreenme-nucleus) roda várias instâncias, vincula controle e organiza janelas. Usa links simbólicos, às vezes encerra mutex de instância única, bibliotecas XInput substitutas, LAN ou emulação on-line (Goldberg, Nemirtingas) ([README](https://raw.githubusercontent.com/SplitScreen-Me/splitscreenme-nucleus/master/README.md)).
- Não adiciona modo cooperativo a um jogo de um jogador: precisa já existir forma de conectar instâncias. Útil à estrutura de dois clientes, não solução cooperativa.

### <a id="214-archipelago-item-sync"></a>2.14 Archipelago (sincronização de itens)

- [Archipelago](https://github.com/ArchipelagoMW/Archipelago): randomizador multimundo com servidor central (`MultiServer.py`, inferido do nome) e clientes por jogo (`*Client.py`, inferido). Sincroniza itens entre mundos sem compartilhar espaço. Forma mais barata de cooperativo: trocas ou conjunto compartilhado.

### <a id="215-other-approaches-to-note"></a>2.15 Outras abordagens relevantes

- Archon mode de guardião compartilhado está em desenvolvimento no KeeperFX original ([PRs](https://github.com/dkfans/keeperfx/pulls)); confira antes de criar fork.
- ACGC-PC-Multiplayer (Animal Crossing, port PC de descompilação) usa autoridade host e representantes segundo [repositório](https://github.com/vsimochi/ACGC-PC-Multiplayer), branch `multiplayer`.

---


## <a id="3-tooling-by-engine-type"></a>3. Ferramentas por tipo de motor

### <a id="31-hooking-and-injection"></a>3.1 Hooks e injeção

| Ferramenta | Uso | Fonte |
|---|---|---|
| Extensões de scripts (SKSE, F4SE, xNVSE) | Mecanismo suportado de plugins DLL Bethesda; SKSE carrega de `Data/SKSE/Plugins`, suporta só compilações específicas | [SKSE](http://skse.silverlock.org/) |
| BepInEx | Plugins Unity Mono, IL2CPP e .NET (XNA, FNA, MonoGame); inclui HarmonyX, usa UnityDoorstop | [BepInEx](https://github.com/BepInEx/BepInEx) |
| MelonLoader | Unity Il2Cpp/Mono; proxy DLL (padrão `version.dll`, também `winhttp.dll`, `winmm.dll`, `dinput8.dll`, `d3d11.dll`) | [MelonLoader](https://github.com/LavaGang/MelonLoader) |
| Harmony | Modifica métodos .NET/Mono em execução: código antes/depois ou alteração de IL; nenhum arquivo alterado | [Harmony](https://github.com/pardeike/Harmony) |
| UE4SS | Mods injetáveis UE 4.7 a 5.8: Lua, C++, Blueprint, extração SDK/UHT, propriedades ao vivo; pode exigir assinaturas AOB por jogo | [RE-UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) |
| REFramework | Carregador e Lua para RE Engine (RE2/3/4/7/Village, DMC5, SF6, MH Rise/Wilds, Dragon's Dogma 2 e outros), sistema de plugins | [REFramework](https://github.com/praydog/REFramework) |
| MinHook | Hooks inline x86/x64 mínimos com trampolins; ativação enfileirada de vários hooks | [MinHook](https://github.com/TsudaKageyu/minhook) |
| Detours | Biblioteca Microsoft de hooks de API (MIT, Windows) | [Detours](https://github.com/Microsoft/Detours) |
| Source SDK | Divisão servidor/cliente e scripts de mapas/entidades; [engine-families.md](engine-families.md) | `unknown` (página não consultada) |
| UnrealScript (UE1/UE2) | Lógica em scripts, replicação embutida; distribuir pacote de subclasses | veja 2.9 |
| Descompilações e recompiladores | Descompilações dão o fonte; N64Recomp recompila N64 estaticamente para C, README lista hooks/patches ainda não funcionais; Zelda64Recomp suporta mods | [N64Recomp](https://github.com/N64Recomp/N64Recomp), [Zelda64Recomp](https://github.com/Zelda64Recomp/Zelda64Recomp) |

Regra prática: prefira o hook suportado de mais alto nível (script, carregador, extensão); use inline (MinHook, Detours) só para o que ele não alcança.

### <a id="32-networking-libraries-seen-in-these-mods"></a>3.2 Bibliotecas de rede vistas nestes mods

| Biblioteca | Encontrada em | Propriedades | Fonte |
|---|---|---|---|
| GameNetworkingSockets | Tilted (submódulo) | Mensagens confiáveis/não confiáveis, fragmentação, AES-GCM, faixas, P2P com travessia NAT; dispensa Steam; sem serialização de entidades ou diferenças | [GNS](https://github.com/ValveSoftware/GameNetworkingSockets), [TiltedConnect](https://raw.githubusercontent.com/tiltedphoques/TiltedConnect/master/.gitmodules) |
| LiteNetLib | Nitrox (espelho das docs) | UDP confiável .NET: ordenado, não ordenado, sequenciado; canais; travessia NAT; simulação de perda | [LiteNetLib](https://github.com/RevenantX/LiteNetLib) |
| Lidgren | RAGECOOP (modificada) | UDP .NET; sem desenvolvimento ativo | [Lidgren](https://github.com/lidgren/lidgren-network-gen3), [RAGECOOP](https://raw.githubusercontent.com/RAGECOOP/RAGECOOP-V/main/README.md) |
| ENet | Nosso teste host/cliente de missões | UDP confiável C, MIT | [ENet](https://github.com/lsalzman/enet) |
| RakNet | TES3MP (GUIDs na autoridade Cell; uso inferido) | `unknown` nas páginas consultadas | [Cell.hpp](https://git.cijber.net/mirror/openmw-tes3mp/src/branch/master/apps/openmw/mwmp/Cell.hpp) |
| UDP próprio | HKMP (pacotes de complementos), DK2 (UDP 7575), Anchor (retransmissor estilo TCP, detalhes desconhecidos) | IDs de pacotes e indicadores de confiabilidade próprios | [wiki HKMP](https://github.com/Extremelyd1/HKMP/wiki), [DK2](https://ciphercom.github.io/dk2-coop) |

Para testes numa máquina, escolha simulação de perda/latência embutida (GNS e LiteNetLib listam ambas). Para Steam, [networking-steam-spacewar.md](networking-steam-spacewar.md).

### <a id="33-reverse-engineering-for-agents"></a>3.3 Engenharia reversa para agentes

| Ferramenta | O que oferece ao agente | Fonte |
|---|---|---|
| Ghidra sem interface | Descompilar binários inteiros em lote; automatizar e pesquisar saída | [reverse-engineering.md](reverse-engineering.md) |
| GhidraMCP | Plugin Java com HTTP dentro do Ghidra (`localhost:8080` padrão); ponte MCP Python; descompilar, renomear, listar métodos/classes/importações/exportações; sem interface por PyGhidra | [GhidraMCP](https://github.com/LaurieWired/GhidraMCP) |
| ida-pro-mcp | IDA: descompilar, desmontar, referências, grafo de chamadas, renomear, tipos, patches, busca de bytes; `idalib-mcp` sem interface; README recomenda MCP oficial Hex-Rays; exige IDA pago | [ida-pro-mcp](https://github.com/mrexodia/ida-pro-mcp) |
| REA | Um MCP para Ghidra, IDA, Hopper (e objdump, Rizin); exige Node; `npx rea-agents setup` edita configuração do agente, portanto usuário autoriza | [REA](https://github.com/morluto/rea) |

---

## <a id="4-from-nothing-to-co-op-build-order-for-an-agent"></a>4. Do nada ao modo cooperativo: ordem de implementação para agentes

Trabalhe nesta ordem. Cada etapa termina com teste aprovado por dois clientes por script, sem pessoa. Consulte [automated-qa.md](automated-qa.md).

### <a id="stage-0-recon-hours"></a>Etapa 0: reconhecimento (horas)

1. Pesquise trabalho existente primeiro ([DIRECTORY.md](../DIRECTORY.md), [engine-families.md](engine-families.md)). Retomar ou ampliar é muito mais barato.
2. Registre identidade (compilação, SHA-256, motor). Procure fonte: SDK, descompilação, scripts, reescrita aberta.
3. Classifique: replicação (Unreal, Source)? Scripts (Lua, UnrealScript, similares a Papyrus)? Unity? Descompilação? Escolha ferramentas da seção 3.

### <a id="stage-1-pick-the-hook-point"></a>Etapa 1: escolha o ponto de hook

Preferência: (1) código-fonte/descompilação; (2) multiplayer embutido e scripts; (3) carregador oficial/comunitário (extensão de scripts, BepInEx/Harmony, REFramework, UE4SS); (4) hooks inline em DLL injetada.

Teste de saída: código executa dentro do jogo, registra linha por quadro e lê posição local e ID de mundo. Fácil em Unity/carregadores (horas), moderado em extensões (dias), difícil em motores nativos desconhecidos (semanas, principalmente engenharia reversa e endereços estáveis por compilação).

### <a id="stage-2-make-a-second-player-visible-puppet"></a>Etapa 2: torne o segundo jogador visível (representante)

1. Transporte mínimo: host e cliente, mensagem de estado (ID, ID mundo, posição, rotação, animação, equipamentos), 10 a 20 Hz.
2. Crie representante de NPC/modelo do jogo. Desative IA e entrada, controle pelo estado recebido com interpolação. Sem API de criação, assuma NPC existente: ignore decisão e forneça solicitação de movimento do jogo para animar caminhada; ou crie cópia de cena do personagem e atribua o grafo de animação dele (Shadow of War; [reverse-engineering.md](reverse-engineering.md#reading-and-driving-live-state-from-inside-the-game)). Com grafo do jogador, envie entradas próprias (analógico, velocidade, giro) para mover; fixar posição a cada quadro quebra passadas.
3. Trate desconexão (remover) e células/fases diferentes (ocultar representantes de outras fases).

Teste de saída: script A anda em círculo; host vê o mesmo movimento dentro da tolerância. Primeiro marco difícil: criar ator convincente com segurança e impedir o motor de removê-lo costuma levar mais tempo. Dificuldade moderada a alta.

### <a id="stage-3-authority-model"></a>Etapa 3: modelo de autoridade

Decida por classe (1.2). Padrão: host executa IA/física, clientes enviam entradas e reivindicações de golpes; host valida/transmite. Comece pelo necessário para lutar: posição, vida, morte dos NPCs. Acrescente cedo transferência e opção de desativação (como `EnemySyncMirroring`).

Teste de saída: ambos ferem mesmo inimigo, veem mesma vida/morte, itens aparecem uma vez. Difícil. IA é o trabalho prolongado (TES3MP ainda a lista como principal problema; OOT True Co-op tem lacunas de agressividade, sons, partículas).

### <a id="stage-4-world-and-quest-state"></a>Etapa 4: mundo e missões

1. Localize armazenamento da história (etapas de missão, globais, eventos); intercepte escritas na função comum mais baixa.
2. Replique escritas da autoridade; aplique nas demais com proteção de reentrada (receber não retransmite).
3. Captura na entrada: extrair, enviar, aplicar e passar a diferenças.
4. Defina política de diálogos/cenas (1.5).
5. Itens: coletas do mundo uma vez, contêineres por autoridade, inventário individual.

Teste de saída: host avança missão e cliente lê a mesma etapa; terceiro entra tarde, verifica hash idêntico. Fácil se armazenamento único, muito difícil se espalhado por scripts/objetos (Fallout, Skyrim). Normalmente moderado.

### <a id="stage-5-transitions-and-saves"></a>Etapa 5: transições e salvamentos

1. Mapeie todas as transições (portas, viagem rápida, teleporte roteirizado), conduza pelo host com clientes seguindo e barreira antes de retomar.
2. Salvamento canônico host. Clientes nunca sobrescrevem os próprios ou usam perfil por sessão.
3. Ressincronize captura completa após cada carregamento; suponha todos os IDs alterados.

Teste de saída: 15 transições consecutivas por script, checksums iguais após cada uma. (Nosso teste prolongado Deus Ex percorreu 15 viagens com dois clientes locais.) Difícil, muitos bugs, toca tudo acima.

### <a id="stage-6-automated-two-client-tests"></a>Etapa 6: testes automatizados de dois clientes

1. Duas instâncias reais numa máquina (notas de mutex em [methods.md](methods.md)), ou real e bot sem interface falando protocolo.
2. Comando de hash e comparação por etapa; também detector de divergência, como checksums lockstep.
3. Simule perda, latência e variação pelo transporte.
4. Integre cenários (andar, lutar, missão, transição, reconectar) a script semelhante a CI. Sessão humana de jogo não é plano de teste.

### <a id="realistic-scope"></a>Escopo realista

| Tipo de jogo | Jogadores visíveis | Combate | Missões | Campanha completa |
|---|---|---|---|---|
| Descompilação ou motor aberto | dias | dias a semanas | semanas | semanas a meses |
| Unity com carregador | dias | semanas | semanas | meses |
| Unreal 1/2 com scripts | dias | já existe | já existe | semanas corrigindo bugs |
| Bethesda com extensão | semanas | semanas a meses | meses | não atingido publicamente sem solução centrada no líder |
| Nativo fechado, sem carregador | semanas de engenharia reversa | meses | meses | provavelmente fora de escopo |

Estimativas para agente com revisor humano, não dados medidos.

---

## <a id="5-unknowns-and-gaps-in-this-page"></a>5. Desconhecidos e lacunas desta página

- Tilted: hook exato, responsabilidade por entidade.
- Seamless Co-op: qualquer arquitetura técnica (fechado, sem relato encontrado).
- HKMP, sm64coopdx, TES3MP: transporte interno não confirmado nas páginas.
- KeeperFX/DK2: modelo não informado nas páginas consultadas.
- xrMPE: se é fork completo; repositório do motor não encontrado.
- NV:MP: fontes retornaram 403; internals só de engenharia reversa local.
- Nitrox: arquitetura por espelho de terceiros; confira original.
- Docs de rede Source/Unreal (Valve/Epic) retornaram 403/404; leia diretamente antes de confiar nos detalhes da replicação do motor.

Ao preencher uma lacuna, acrescente fonte e abra uma pull request.

