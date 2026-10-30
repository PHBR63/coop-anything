# <a id="console-games-through-emulators"></a>Jogos de console por emuladores

Como adicionar modo cooperativo a um jogo de console quando não há versão para PC ou ela não é o alvo adequado. Escrito para um agente que recebeu "torne o jogo X cooperativo", sendo X exclusivo de console. Situação em outubro de 2026. Toda afirmação concreta tem link. Itens **NÃO VERIFICADOS** vieram de uma única fonte secundária ou não puderam ser confirmados numa página primária; confira novamente antes de depender deles.

Guias relacionados: [methods.md](methods.md), [split-screen.md](split-screen.md), [networking.md](networking.md), [reverse-engineering.md](reverse-engineering.md), [automated-qa.md](automated-qa.md).

## <a id="0-ground-rules"></a>0. Regras básicas

- O usuário possui o jogo. Extraia seus próprios discos, cartuchos e BIOS/firmware. Este guia não oferece ROMs, ISOs, BIOS, chaves ou páginas de onde baixar; nada que você escrever deve fazê-lo.
- Prefira port para PC ou descompilação existente. Quase sempre é mais fácil acrescentar cooperação ao código-fonte ou port nativo que a um emulador em execução (seção 6, etapa 1).
- Nunca planeje testes humanos. Controle duas instâncias por scripts e leia RAM para verificar estado (consulte [automated-qa.md](automated-qa.md) e seção 7 abaixo).
- Disponibilidade de emuladores muda rápido, sobretudo Switch. Trate os números de versão abaixo como retratos do momento.

## <a id="1-choosing-a-route"></a>1. Escolhendo um caminho

```
Does a PC port / decomp / recomp of the game exist?
  yes -> add co-op there (engine playbooks). Stop.
  no  -> Does the game already have local co-op / versus / link mode?
           yes -> Route A: emulator netplay (inputs synced). Cheapest.
           no  -> Does the game have an online mode whose servers are dead?
                    yes -> Route C: LAN / private-server revival.
                    no  -> Route B: memory-sync co-op (two emulators, RAM bridge).
Fallback for local co-op games on any emulator: Route D, remote play.
```

| Caminho | Exige modo cooperativo no jogo? | Esforço | Fidelidade | Falha típica |
|---|---|---|---|---|
| A. Jogo em rede pelo emulador | Sim (multiplayer local). | Baixo. | Perfeita, mesmo jogo. | Dessincronização, latência, emulador sem recurso de rede. |
| B. Sincronização de memória | Não. | Alto (engenharia reversa por jogo). | Parcial, somente o sincronizado. | Determinismo, carregamento, câmera, scripts. |
| C. LAN / servidor retomado | Sim (modo de rede). | Médio. | Modo on-line original. | Confiança no servidor, DNS, emulação do adaptador. |
| D. Jogo remoto | Sim (multiplayer local). | Muito baixo. | Perfeita, mas com latência de vídeo. | Atraso de entrada, host possui o jogo. |

## <a id="2-the-generic-methods"></a>2. Métodos genéricos

### <a id="2a-emulator-netplay-input-sync"></a>2a. Jogo em rede no emulador (sincronização de entradas)

Ambas as máquinas executam o mesmo jogo e trocam entradas de controle; o modo cooperativo local faz o restante. Requisitos sempre iguais: mesma compilação de emulador, mesma extração do jogo (região e revisão), mesmas configurações.

| Emulador | Modelo de rede e observações | Fonte |
|---|---|---|
| RetroArch | Instâncias com mesmo núcleo e conteúdo permanecem sincronizadas. Exige mesma versão RetroArch, núcleo e conteúdo exato. Host precisa de TCP 55435 (UPnP ou redirecionamento manual) ou retransmissor. Em princípio, qualquer núcleo com estados salvos deve funcionar, mas PSX, N64, Dreamcast, GameCube, Wii e 3DS aparecem como não compatíveis por desempenho. GBA e PSP são considerados impossíveis. Cabo de conexão não é emulado, apenas multiplayer local no mesmo sistema. Mais de dois jogadores são aceitos. | [FAQ libretro](https://docs.libretro.com/guides/netplay-faq/) |
| Dolphin | Rede integrada. Todos precisam de cópia própria com mesma região/revisão e mesma versão Dolphin. Servidor de travessia só ajuda a conectar, sem acrescentar latência. | [Guia Dolphin](https://dolphin-emu.org/docs/guides/netplay-guide/) (página retornou 403 à leitura; conteúdo obtido em trecho da busca e [cópia](https://central-new.dolphin-emu.org/docs/guides/netplay-guide); fork Slippi com rollback é separado, consulte [menção](https://lemmy.brendan.ie/comment/1236250), **NÃO VERIFICADO**). |
| gopher64 (N64) | P2P listado como recurso; servidor trata sessões e registra IPs. README não informa rollback ou lockstep. | [gopher64](https://github.com/gopher64/gopher64) |
| simple64 (N64) | Tinha rede por servidor na nuvem; projeto arquivado, desenvolvedor migrou para gopher64. | [GameTechWiki simple64](https://emulation.gametechwiki.com:443/index.php/Simple64), [comentário GamingOnLinux](https://www.gamingonlinux.com/2025/08/nintendo-64-emulator-gopher64-recently-added-save-state-slots-and-netplay-cloud-servers/comment_id=282408) |
| Project64 netplay | Apenas afirmação de baixa autoridade de que Project64 KSE tinha o recurso. **NÃO VERIFICADO**. | [Comentário](https://lemmy.brendan.ie/comment/1235709) |
| PCSX2 | Sem rede geral na versão principal. Pedido antigo continua aberto como [issue 772](https://github.com/PCSX2/pcsx2/issues/772); duplicatas (Kaillera, cliente com atraso) fechadas: [8425](https://github.com/PCSX2/pcsx2/issues/8425), [14104](https://github.com/PCSX2/pcsx2/issues/14104). Forks: [pcsx2-online-Update](https://github.com/fraserofsmeg/pcsx2-online-Update) (P2P com atraso, criado para jogos de luta, últimas mudanças em 2012, configurações voltam ao padrão durante rede), [pcsx2-netplay-reborn](https://github.com/YungMoniCA1/pcsx2-netplay-reborn) (5 commits, sem versões, praticamente esqueleto) e port de protótipo lockstep com atraso de setembro de 2026 ([PR](https://github.com/q13007868130/git-demo/pull/1), **NÃO VERIFICADO**, sem retransmissão ou rollback). Conclusão: considere rede indisponível em compilações modernas. | Links na própria linha. |
| DuckStation (PS1) | Sem rede encontrada na versão principal. Compilação comunitária GGPO com rollback de HeatXD existia em 2023. | [Exputer, março de 2023](https://exputer.com/news/playstation/ps1-emulator-rollback-netcode/), [compilação](https://github.com/HeatXD/duckstation-netplay/releases/tag/0.1) (estado atual **NÃO VERIFICADO**). |
| PPSSPP | Modos ad hoc (P2P, concebido para "mesma sala") e infraestrutura, atendidos por servidores voluntários; maioria suporta protocolo Relay, dispensando redirecionamento; jogadores precisam do mesmo deslocamento de portas (padrão 10000). | [Documentação multiplayer](https://www.ppsspp.org/docs/multiplayer/how-to-play), [infraestrutura](https://www.ppsspp.org/docs/multiplayer/infrastructure-servers/) |
| melonDS (DS) | Independente: rede local sem fio e Wi-Fi on-line listados em desenvolvimento nos pacotes de 2026. Núcleo libretro melonDS DS emula substitutos Nintendo WFC (Kaeru WFC padrão) e informa que multiplayer LAN não funciona pela internet, VPN ou túneis. Relato de 2026 diz que o núcleo RetroArch acrescentou LAN. | [libretro melonDS DS](https://docs.libretro.com/library/melonds_ds/), [Generation Amiga, agosto de 2026](https://www.generationamiga.com/2026/08/22/retroarchs-new-melonds-ds-core-adds-wi-fi-and-better-dual-screen-controls/) (**NÃO VERIFICADO** além da documentação). |
| Azahar (3DS, sucessor Citra) | Salas que encaminham tráfego local sem fio pela internet, sem servidor ou conta Nintendo. Segundo um relato, Android recebeu navegador de salas na prévia 2126.0. | [Anúncio Azahar](https://citra.azahar-emu.org/entry/announcing-networking-support/), [Android Authority](https://androidauthority.com/azahar-3ds-emulator-multiplayer-android-3686723) (detalhes Android **NÃO VERIFICADOS**). |
| RPCS3 (PS3) | RPCN substitui PSN de forma gratuita e aberta, permitindo modos on-line próprios dos jogos (inclusive alguns de luta e corrida) entre usuários RPCS3. Alguns exigem servidores comunitários. | [DSOGaming](https://www.dsogaming.com/news/rpcs3-now-supports-online-play-via-psn-emulation/), [GamingOnLinux RPCN 1.4](https://www.gamingonlinux.com/2025/02/playstation-3-emulator-rpcs3-expands-online-play-for-fighting-games-with-rpcn-v1-4/comment_id=276279). Consulte a wiki RPCS3 de rede para lista atual (não lida). |
| Xenia / Xemu | System-link por XLink Kai, seção 2c. | Links em 2c. |
| mGBA | Tem "multiplayer window" executando várias instâncias locais conectadas (útil para cabo de conexão e testes). | [Fórum mGBA](https://forums.mgba.io/printthread.php?tid=5781) |

Regras práticas de latência e determinismo (gerais, sem fonte única):

- Rede com entradas sincronizadas exige emulador determinístico: mesma semente, tempos, sem ajustes de velocidade específicos do host. Emuladores normalmente impõem configurações seguras; não deixe um mod mudá-las.
- Cartões de memória e salvamentos precisam começar idênticos. Forks como PCSX2-Online tornam o cartão do cliente somente leitura e copiam o do host.
- Jogos com muita aleatoriedade interna e lockstep a 60 fps são mais sujeitos à dessincronização; luta em rede com atraso funciona, mas grandes mundos abertos frequentemente não.

### <a id="2b-memory-sync-co-op-frameworks-single-player-to-co-op"></a>2b. Frameworks cooperativos de sincronização de memória (de um jogador para cooperativo)

Dois ou mais emuladores executam o mesmo jogo de um jogador. Uma ponte lê o estado de cada jogador na RAM emulada, envia por TCP/UDP e escreve remotos em vagas livres de atores ou numa sobreposição personalizada. Mesma ideia dos mods de PC de "guardião compartilhado", mas o "processo do jogo" é a RAM convidada do emulador.

| Framework | Emulador | Hooks | Observações e fonte |
|---|---|---|---|
| ModLoader64 | Mupen64Plus modificado vinculado a Node.js (N-API). | Acesso à memória, patches de ROM, rede. | Plataforma N64 independente de jogo; exige Windows 10 ou Linux moderno, OpenGL 3.3, Node 10 ou 12 de 32 bits no Windows. [Repositório](https://github.com/hylian-modding/ModLoader64). Comunidade diz estar parado; tópico de 2024 perguntou se morreu ([cópia Reddit](https://redlib.belloworld.it/r/ZeldaOoT/comments/1f21sk7/is_modloader64_dead)). |
| BizHawk Lua + socket | BizHawk (EmuHawk), vários sistemas 8/16/32 bits, entradas N64, PS1, GBA, DS, 3DS. | Console Lua; Archipelago distribui conector genérico READ/WRITE por domínio de memória. | [README BizHawk](https://github.com/TASEmulators/BizHawk), [README BizHawk Archipelago](https://git.hollymcfarland.com/monorail/Archipelago/raw/branch/main/worlds/_bizhawk/README.md), [bizhook](https://pypi.org/project/bizhook/1.1.0/) |
| Scripts mGBA | mGBA 0.10+ | Só Lua; objeto `emu`, domínios de memória (GBA: wram, iwram, io, palette, vram, oam, cart0-2), callbacks `frame` e `keysRead`, API `socket` (`tcp`, `bind`, `connect`, `accept`, `send`, `receive`, `poll`). | [Documentação](https://mgba.io/docs/scripting.html). Operação sem interface não declarada. |
| Dolphin Memory Engine | Dolphin (GameCube/Wii) | Processo externo acessa memória emulada; converte ordem de bytes (lê little-endian, escreve big-endian); desconecta após acesso malsucedido; também [vínculo Python](https://pypi.org/project/dolphin-memory-engine/1.0.1). | [Repositório](https://github.com/aldelaro5/dolphin-memory-engine). Push em abril de 2026 segundo agregador. |
| Fork Python Dolphin | Fork de Felk. | Scripts Python internos com eventos `frameadvance` e `memorybreakpoint`, texto na tela, módulo de memória, opção `--script`; só Windows x86-64; API mínima, sem versões listadas. | [Felk/dolphin](https://github.com/Felk/dolphin). Não faz parte da versão principal; PR Python parado desde 2022 segundo [nota](https://tasvideos.org/Forum/Posts/498712), **NÃO VERIFICADO**. |
| PCSX2 PINE | PCSX2 (e outros pelo protocolo). | IPC por socket local: ler/escrever 8/16/32/64 bits, comandos de estado salvo e metadados. | Seção 5. |
| Archipelago | BizHawk e clientes por jogo. | Troca de itens e verificações, sem presença compartilhada. | Randomizador de múltiplos mundos, não cooperação no mesmo mundo, mas clientes são padrão de ponte de RAM pronto. [Archipelago](https://docsearch.algolia.com/mcp/docs/repo/archipelagomw/archipelago) (cópia), [randomizador Zelda 64 Recompiled](https://thunderstore.io/c/zelda-64-recompiled/p/RecompRando/MMRecompRando/). |

Padrão arquitetural que funciona em todos:

1. Encontrar estrutura do ator jogador (posição, rotação, ID de animação, vida, item segurado).
2. Encontrar vaga livre de ator/objeto ou lista de efeitos para criar avatar remoto.
3. A cada atualização: ler jogador local, enviar delta, escrever remoto. 10 a 20 Hz com interpolação normalmente bastam.
4. Sincronizar estado discreto (indicadores, itens, portas, chefes) como eventos, não cópias contínuas de memória.
5. Escolher autoridade única para inimigos e RNG ou aceitar que cada um combata cópias próprias. Anchor faz o segundo por padrão; fork adiciona inimigos sob autoridade do host (seção 4).

### <a id="2c-lan-and-online-mode-emulation"></a>2c. Emulação de modos LAN e on-line

Para jogos com rede ou system-link, emule o adaptador e retome o servidor.

| Técnica | Aplicação | Observações e fonte |
|---|---|---|
| Adaptador PCSX2 DEV9 | Jogos PS2 on-line. | Guias SOCOM usam CLR-DEV9 (0.8.9) e DNS comunitário; PCSX2 1.7 precisa de npcap. Servidores oficiais Network Access Disc encerrados. [Funcionalidade on-line PS2 (Wikipedia)](https://en.wikipedia.org/wiki/PlayStation_2_online_functionality), [cópia guia SOCOM](https://red.127.pp.ua/r/SOCOM/wiki/how-to-play-socom-ii-online), [wiki PCSX2, Network Access Disc](https://wiki.pcsx2.net/Network_Access_Disc). Guias em parte antigos; **NÃO VERIFICADOS** para 2026. |
| Horizon / Clank (servidores Medius) | PS2 Ratchet: Deadlocked e Up Your Arsenal. | Emulador de servidor Medius aberto e patches. [Organização Horizon-Private-Server](https://github.com/Horizon-Private-Server), [Clank](https://github.com/xtvaser/clank). Páginas não dizem se funciona em PCSX2. **NÃO VERIFICADO**. |
| Dolphin BBA | GameCube on-line (como Phantasy Star Online). | Adaptador de banda larga com servidor tap; relatos antigos de erros DHCP e falhas Mac. [Bug 8222](https://bugs.dolphin-emu.org/issues/8222?tab=notes), [fórum](https://forums.dolphin-emu.org/Thread-help-with-bba-and-pso-online-play). Estado atual **NÃO VERIFICADO**. |
| Wiimmfi / RiiConnect24 / WiiLink WFC | Nintendo WFC de Wii e DS. | Substitutos comunitários WFC; Dolphin apresentou erros 20100 e 20101 após atualização de segurança. [Guia Wii](https://wii.hacks.guide/wiimmfi), [bug 11455](https://bugs.dolphin-emu.org/issues/11455). |
| XLink Kai | Xenia (Xbox 360), Xemu (Xbox original), consoles reais. | Xenia experimental via fork netplay canary, somente Windows; usuários Xenia e 360 reais não jogam juntos; precisa Npcap. Xemu suporta rede em ponte. [Configuração Xenia](https://www.teamxlink.co.uk/wiki/Xenia_XLink_Kai_Setup), [Xemu](https://www.teamxlink.co.uk/wiki/Xemu_and_XLink_Kai_Setup). Suporte a emulador PS2 não confirmado. |
| Infraestrutura PPSSPP | PSP. | Servidores voluntários imitam os dos jogos. [Documentação](https://www.ppsspp.org/docs/multiplayer/infrastructure-servers/). |

### <a id="2d-remote-play-fallbacks"></a>2d. Alternativas de jogo remoto

Para multiplayer local sem rede no emulador (principal caso: PS2 em PCSX2).

- Steam Remote Play Together: host executa e transmite vídeo; convidados enviam entradas de controle; só host precisa do jogo; convidados veem apenas a janela. Adicione emulador como jogo externo ao Steam. Oficialmente até quatro jogadores. Exige UDP 27031 e 27036, TCP 27036 e 27037. [Tom's Guide](https://www.tomsguide.com/reference/steam-remote-play-together-how-to-use), [GHacks](https://www.ghacks.net/?p=155430) (artigos de lançamento de 2019; menus podem diferir).
- Parsec: mesma ideia, não verificada aqui (nenhuma fonte obtida). **NÃO VERIFICADO**.
- Custo: latência de entrada acrescentada pela codificação de vídeo e rede. Serve para cooperação casual, ruim para ação à distância.

## <a id="3-per-console-table"></a>3. Tabela por console

"Caminho cooperativo" = melhor abordagem para um agente. "Hooks" = recursos para ler/escrever RAM convidada. Nomes de emuladores verificados ou amplamente documentados; estados têm fonte quando encontrada.

| Console | Emuladores principais | Situação da rede | Hooks de sincronização de memória | Trabalho cooperativo relevante |
|---|---|---|---|---|
| NES, SNES, Genesis (e similares 8/16 bits) | BizHawk, núcleos RetroArch, Mesen, bsnes. | RetroArch funciona para multiplayer local no mesmo sistema ([FAQ](https://docs.libretro.com/guides/netplay-faq/)). | Lua BizHawk com conector socket ([README Archipelago](https://git.hollymcfarland.com/monorail/Archipelago/raw/branch/main/worlds/_bizhawk/README.md)). | Clientes Archipelago (randomizadores, não mundos compartilhados). |
| N64 | Baseados em Mupen64Plus (simple64 arquivado, gopher64 ativo), Project64, núcleo ParaLLEl. | gopher64 P2P ([repositório](https://github.com/gopher64/gopher64)); RetroArch lista N64 não compatível ([FAQ](https://docs.libretro.com/guides/netplay-faq/)). | ModLoader64 ([repositório](https://github.com/hylian-modding/ModLoader64)); Lua BizHawk. | Zelda64 Online (OoT, MM), seção 4; recompilações N64 são alternativa moderna ([Zelda 64: Recompiled](https://thunderstore.io/c/zelda-64-recompiled/p/RecompRando/MMRecompRando/)). |
| GameCube, Wii | Dolphin (e forks Slippi, PrimeHack). | Rede integrada Dolphin ([guia](https://dolphin-emu.org/docs/guides/netplay-guide/)); Wii WFC por Wiimmfi ([guia](https://wii.hacks.guide/wiimmfi)); RetroArch não compatível. | Dolphin Memory Engine ([repositório](https://github.com/aldelaro5/dolphin-memory-engine)), fork Python Felk ([repositório](https://github.com/Felk/dolphin)), códigos Gecko/AR semelhantes a pnach. | Wind Waker tem papel de segundo jogador GBA Tingle Tuner, emulado pela porta de controle GBA do Dolphin ([ZeldaWiki](https://zeldawiki.wiki/wiki/Multiplayer) e trecho do guia). Metroid Prime 2: Echoes tem mod de campanha cooperativa em tela dividida sobre o modo versus, com códigos Gecko ([games/metroid-prime-2-echoes](../games/metroid-prime-2-echoes/README.md)); PrimeHack só altera controles e só dirige jogador 1 ([Flathub](https://www.flathub.org/apps/io.github.shiiion.primehack)). |
| PS1 | DuckStation, Mednafen/Beetle, ePSXe. | RetroArch lista PSX não compatível ([FAQ](https://docs.libretro.com/guides/netplay-faq/)); compilação GGPO DuckStation existia em 2023 ([Exputer](https://exputer.com/news/playstation/ps1-emulator-rollback-netcode/)). | PINE originou no PCSX2; servidor no DuckStation só evidenciado indiretamente por [arquivo-fonte espelhado](https://repo.retrodeck.net/Xargon/Duckstation/src/commit/1fd8d2701de0c9887509703a027b8d8bb439cd6a/src/core/pine_server.cpp), estado atual **NÃO VERIFICADO**. | Recriação de fãs Spyro 3 + Crash em UE4 com demonstração de 4 jogadores, não mod de emulador ([Retro Dodo](https://retrododo.com/spyro-crash-finally-work-together-in-new-nostalgic-mod/)). |
| PS2 | PCSX2. | Sem rede principal; forks antigos ou protótipos (2a). | IPC PINE; patches pnach ([documentação](https://pcsx2.net/docs/advanced/writing-patches)); DEV9 para modos on-line. | Servidores Ratchet Horizon; retomada SOCOM; seção 5. |
| PS3 | RPCS3. | RPCN para jogos com modo on-line ([GamingOnLinux](https://www.gamingonlinux.com/2025/02/playstation-3-emulator-rpcs3-expands-online-play-for-fighting-games-with-rpcn-v1-4/comment_id=276279)). | Sem suporte PINE encontrado. Acesso externo possível com ferramentas de memória, mas sem projeto confirmado. **NÃO VERIFICADO**. | Poucos ou nenhum mod de um jogador para cooperativo encontrado. |
| PSP | PPSSPP. | Ad hoc e infraestrutura com retransmissão ([documentação](https://www.ppsspp.org/docs/multiplayer/how-to-play)); rede PSP no RetroArch impossível ([FAQ](https://docs.libretro.com/guides/netplay-faq/)). | PPSSPP tem depurador e visão de memória (não verificados aqui); padrão 2b plausível. **NÃO VERIFICADO**. | Kingdom Hearts: Birth by Sleep tem cooperação nativa no PSP ([RPG Site](https://www.rpgsite.net/news/430-kingdom-hearts-gets-co-op-play-on-psp)). |
| GBA, DS, 3DS | mGBA, melonDS, Azahar, BizHawk. | mGBA tem conexão local em múltiplas janelas; rede GBA RetroArch impossível ([FAQ](https://docs.libretro.com/guides/netplay-faq/)); Wi-Fi melonDS em desenvolvimento independente ([libretro](https://docs.libretro.com/library/melonds_ds/)); salas Azahar ([postagem](https://citra.azahar-emu.org/entry/announcing-networking-support/)). | Lua mGBA com sockets ([documentação](https://mgba.io/docs/scripting.html)); Lua BizHawk. | PK-GBA Multiplayer para Pokémon Gen 3, alpha, possivelmente parado ([PokeCommunity](https://www.pokecommunity.com/threads/pk-gba-multiplayer.484949/), estado **NÃO VERIFICADO**). |
| Xbox, Xbox 360 | Xemu, Xenia (canary). | System-link por XLink Kai, experimental ([Xenia](https://www.teamxlink.co.uk/wiki/Xenia_XLink_Kai_Setup), [Xemu](https://www.teamxlink.co.uk/wiki/Xemu_and_XLink_Kai_Setup)). | Sem ponte RAM verificada. | Nenhum encontrado. |
| Switch | Eden, Ryubing (fork Ryujinx), Citron, outros. | Rede local sem fio LDN existia em Ryujinx e fork ([tech-insider](https://tech-insider.org/eden-vs-ryubing-best-switch-emulator-2026/), **NÃO VERIFICADO**); estado em Eden/Citron não confirmado. | Nenhum verificado. | Não planeje trabalho sem conferir situação legal. Yuzu e Ryujinx originais encerrados após ação Nintendo; relatos de 2026 de notificações DMCA contra forks são **NÃO VERIFICADOS** ([tech-insider](https://tech-insider.org/?p=19175)). Use só emuladores abertos que o usuário já tem. |

## <a id="4-existing-emulator-based-co-op-projects-for-single-player-games"></a>4. Projetos cooperativos existentes baseados em emuladores para jogos de um jogador

Estado é "como encontrado", não promessa. Tipos: `netplay`, `memory-sync`, `port-mod`, `server-revival`, `randomizer`.

| Jogo | Projeto | Tipo | Estado | Link |
|---|---|---|---|---|
| Ocarina of Time, Majora's Mask (N64) | Zelda64 Online (ModLoader64) | memory-sync | Público, 849 commits, README lista itens e progresso compartilhados, jogadores visíveis, modelos personalizados; MM tem modos Basic e Time Sync. Manutenção incerta (tópico Reddit 2024 "morreu?"). | [Z64Online](https://github.com/hylian-modding/Z64Online), [ModLoader64](https://github.com/hylian-modding/ModLoader64) |
| Ocarina of Time (port PC por descompilação) | Anchor para Ship of Harkinian | port-mod | Cliente/servidor; carrega estado salvo do host, compartilha indicadores e itens; compilações noturnas contínuas; relatado como incorporado ao SoH. | [anchor](https://github.com/garrettjoecox/anchor), [XDA](https://www.xda-developers.com/a-zelda-classic-just-got-full-co-op-multiplayer-thanks-to-this-pc-port/) |
| Ocarina of Time (port PC) | OOT True Co-op | port-mod | Fork com sincronização de inimigos/chefes sob autoridade do host sobre SoH + Anchor. Inicial; qualidade **NÃO VERIFICADA**. | [OOT-True-Co-op](https://github.com/bghill95/OOT-True-Co-op) |
| Majora's Mask (port PC, fork Anchor) | anchor-2s2h | port-mod | Fork Anchor para 2 Ship 2 Harkinian; não é múltiplos mundos, exige mesma semente. | [anchor-2s2h](https://github.com/tjoaks/anchor-2s2h) |
| Super Mario 64 | sm64coopdx (continua sm64ex-coop) | port-mod | Organização ativa; salas até 16; funciona em port PC criado da ROM própria via patcher. Não é mod de emulador. | [sm64coopdx](https://github.com/coop-deluxe/sm64coopdx), [PC Gamer](https://pcgamer.com/super-mario-64-emulator-co-op-mod) |
| Super Mario 64 (N64 e PS2) | Recompilação PS2 ligada a N64 por Pico | memory-sync (hardware) | Demonstração pontual de Carl Does Tech Things, sem página pública ou download no artigo. | [Time Extension, fevereiro de 2026](https://www.timeextension.com/news/2026/02/modder-somehow-conjures-super-mario-64-cross-play-between-n64-and-ps2), [vídeo](https://www.youtube.com/watch?v=gCza2KrstxE) |
| Banjo-Kazooie | Banjo-Kazooie Online (ModLoader64) | memory-sync | Listado por Kotaku; repositório atual não conferido. **NÃO VERIFICADO**. | [Kotaku](https://kotaku.com/games/banjo-kazooie-online), [Highlander News](https://www.highlandernews.org/?p=74563) |
| Jak and Daxter (PS2, port PC OpenGOAL) | Mod Teamruns | port-mod | Multiplayer on-line/local na seção Mods do inicializador OpenGOAL; feito para speedrunners; só Jak 1 segundo cobertura. | [DSOGaming](https://www.dsogaming.com/news/the-unofficial-pc-port-of-jak-daxter-now-supports-online-and-local-multiplayer/), [Retro Dodo](https://retrododo.com/jak-daxter-return-with-online-local-multiplayer/) |
| Pokémon Gen 3 (GBA) | PK-GBA Multiplayer | memory-sync | Alpha 4; desenvolvedor silencioso há meses segundo comentário; **NÃO VERIFICADO**. | [PokeCommunity](https://www.pokecommunity.com/threads/pk-gba-multiplayer.484949/) |
| Ratchet: Deadlocked, Up Your Arsenal (PS2) | Servidores Medius Horizon + Clank | server-revival | Servidores on-line aprimorados com mapas/modos personalizados; compatibilidade PCSX2 não confirmada nas páginas. | [Horizon-Private-Server](https://github.com/Horizon-Private-Server), [Clank](https://github.com/xtvaser/clank) |
| SOCOM (PS2) | Servidores comunitários com DEV9 | server-revival | DNS comunitário; confiança nos operadores necessária. | [Cópia do guia](https://red.127.pp.ua/r/SOCOM/wiki/how-to-play-socom-ii-online) |
| Zelda 64: Recompiled (MM) | RecompRando por Archipelago | randomizer | Múltiplos mundos, não cooperação no mesmo mundo. | [Thunderstore](https://thunderstore.io/c/zelda-64-recompiled/p/RecompRando/MMRecompRando/) |
| Spyro 3 + Crash | Recriação de fãs UE4 de qtderg | port-mod | Demonstração, 3 fases, 4 jogadores locais/on-line; não executa jogo original. | [Retro Dodo](https://retrododo.com/spyro-crash-finally-work-together-in-new-nostalgic-mod/) |

Pesquisado sem encontrar nada (nesta pesquisa; ausência de resultados não é prova):

- Kingdom Hearts 1/2: nenhum mod cooperativo PCSX2 ou no ecossistema PC OpenKH encontrado. Mods relacionados são melhorias de uso (Re:Fixed, Re:Fined) e cliente randomizador Archipelago. [Guia Archipelago KH2](https://archipelago.gg/tutorial/Kingdom%20Hearts%202/setup/en), [RPG Site sobre Re:Fixed](https://rpgsite.net/feature/12932-kingdom-hearts-1-2-and-birth-by-sleep-on-pc-get-a-wealth-of-new-nonintrusive-features-and-enhancements-with-the-refixed-mod). Lacuna real e boa candidata a projeto PINE.
- Metroid Prime: sem mod cooperativo para Prime 1 ou 3. Echoes (na Trilogy) tem: modo versus já executa 2-4 jogadores no mesmo mundo; mod carrega campanha nesse modo e corrige suposições de jogador único (salas, salvamentos, análises, alvos dos inimigos, mudanças de itens da história) por Gecko; corpos dos hooks vão para MEM2 livre por patch Dolphin `[OnFrame]`, respeitando limite da lista Gecko ([games/metroid-prime-2-echoes](../games/metroid-prime-2-echoes/README.md)). [PrimeHack](https://www.flathub.org/apps/io.github.shiiion.primehack) só altera controles.
- Paper Mario (N64): nenhum mod cooperativo encontrado; só conversão total de um jogador Star Nova.
- Wind Waker: nenhum mod encontrado; Tingle Tuner nativo é o modo oficial para 2 jogadores ([ZeldaWiki](https://zeldawiki.wiki/wiki/Multiplayer)).
- Ratchet & Clank 1-3 e Sly Cooper: nenhum projeto cooperativo de sincronização de memória encontrado.
- GTA San Andreas: PS2 inclui modo local para 2 jogadores (tela compartilhada, distância limitada, Free Roam e Rampage) segundo [Co-Optimus](https://www.co-optimus.com/game/1167/playstation-2/grand-theft-auto-san-andreas.html); no PC, multiplayer é SA-MP / open.mp ([Lutris open.mp](https://lutris.net/games/grand-theft-auto-san-andreas-open-multiplayer/)). Para cooperação on-line, use PC, não emulação PS2.

## <a id="5-ps2-the-full-agent-workflow"></a>5. PS2: fluxo completo para o agente

PCSX2 tem o melhor acesso à RAM entre consoles "difíceis", mas sem rede; cooperação PS2 geralmente segue B (memória) ou D (jogo remoto).

### <a id="step-1-check-pc-alternatives-first"></a>Etapa 1: confira primeiro as alternativas PC

1. Existe versão PC nativa (GTA SA, KH2 Final Mix por OpenKH, outras)? Use guias de mods PC.
2. Existe descompilação/reimplementação (OpenGOAL para Jak é o modelo; [Jak Teamruns](https://www.dsogaming.com/news/the-unofficial-pc-port-of-jak-daxter-now-supports-online-and-local-multiplayer/))? Cooperação num port é mais barata que num emulador.
3. Pesquise mods conforme [coop-research](../.claude/skills/coop-research/SKILL.md) antes de escrever código.

### <a id="step-2-does-the-game-already-have-local-co-op"></a>Etapa 2: o jogo já tem cooperação local?

Se sim, há duas opções sem trabalhar na RAM:

- Remote Play Together ou ferramenta de transmissão (2d). Sem desenvolvimento, funciona em qualquer emulador.
- Fork PCSX2 com rede. Só para títulos determinísticos no estilo de luta; o mais conhecido foi feito para poucos jogos e dessincroniza em outros ([pcsx2-online-Update](https://github.com/fraserofsmeg/pcsx2-online-Update)). Não recomendado em 2026.

Modos de tela dividida/compartilhada em PS2 costumam reutilizar o caminho do segundo controle; um segundo "controle virtual" por PINE (abaixo) pode bastar para controlar jogador 2 sem nova lógica de jogabilidade.

### <a id="step-3-memory-sync-via-pine"></a>Etapa 3: sincronização de memória por PINE

PCSX2 implementa IPC PINE para programa externo conversar com emulador em execução. Fatos:

- Wiki: [PCSX2 IPC Protocol](https://wiki.pcsx2.net/IPC_Protocol) (403 à leitura automática; conteúdo de trechos da busca). Especificação e referência C++ em [GovanifY/pine](https://github.com/GovanifY/pine) (pasta standard marcada como rascunho; pasta bindings existe; página não lista opcodes).
- Ative nas configurações avançadas PCSX2, vaga/porta padrão 28011, PCSX2 1.7 Qt ou posterior ([notas mcp-pine](https://glama.ai/mcp/servers/dmang-dev/mcp-pine), terceiro **NÃO VERIFICADO**).
- Opcodes: leitura/escrita 8/16/32/64 bits, versão, estado salvo e metadados, num fonte de servidor de referência ([cópia pine_server.cpp](https://repo.retrodeck.net/Xargon/Duckstation/src/commit/1fd8d2701de0c9887509703a027b8d8bb439cd6a/src/core/pine_server.cpp)). Variante posterior tem leitura/escrita em lote 0x20 e 0x21; outro terceiro diz não haver leitura em lote nativa, então clientes encadeiam leituras pequenas ([glama mcp-pine](https://glama.ai/mcp/servers/dmang-dev/mcp-pine)). Confira a versão-alvo.
- Wrapper Python: [pcsx2-memory-accessor](https://pypi.org/project/pcsx2-memory-accessor/).
- RAM principal EE de 0x00100000 a 0x01FFFFFF (32 MiB), memória temporária em 0x70000000, segundo mesma listagem MCP (**NÃO VERIFICADO**, amplamente conhecido, mas confirme na ferramenta).
- Comportamento com várias instâncias não documentado nas páginas encontradas. Testar se segunda instância usa outra vaga ou instalação portátil separada. **NÃO VERIFICADO**.

O que PINE pode ou não fazer:

| Pode | Não pode (ou não documentado) |
|---|---|
| Ler/escrever RAM convidada, consultar metadados, estados salvos. | Injetar chamada de função na thread do jogo; executar Lua no PCSX2 (nenhum recurso de scripts encontrado). |
| Consultar a ~60 Hz por processo de ponte. | Interceptar exatamente a fronteira do quadro (só consulta periódica). |
| Escrever valor a cada atualização para congelá-lo. | Adicionar segundo controle sem patch; use pnach ou escreva estado do controle a cada quadro. |

Injeção de código: PCSX2 carrega `.pnach` chamados `SERIAL_CRC.pnach` das pastas `patches` e `cheats`, com linhas `patch=<place>,<cpu>,<address>,<type>,<data>` ([escrevendo patches](https://pcsx2.net/docs/advanced/writing-patches)). Para algo maior que escrever valor (hook lendo caixa de mensagens RAM preenchida pela ponte), use pnach para instalar pequena rotina MIPS em espaço de código/dados não utilizado e fazê-la consultar a caixa. Esse é o padrão para transformar "consultar memória" em "jogo reage".

Arquitetura recomendada:

```
PCSX2 A  <--PINE-->  bridge A  <--TCP/UDP-->  bridge B  <--PINE-->  PCSX2 B
   |                                                                     |
 pnach: reads mailbox for remote player's pad/avatar / spawns actor       same
```

1. Identifique estruturas de jogador e entrada de controle ([reverse-engineering.md](reverse-engineering.md): Ghidra com carregador PS2 MIPS e depurador PCSX2 para pontos de interrupção).
2. Escreva primeiro registrador somente de leitura. Registre posição/estado e comprove endereços estáveis entre carregamentos (costumam mudar por fase).
3. Adicione caixa de mensagens escrita pela ponte e rotina pnach para ler.
4. Adicione replicação do remoto. Comece com ator "fantasma", depois interação compartilhada real.
5. Adicione sincronização de indicadores e inventário por eventos.

### <a id="step-4-what-to-sync"></a>Etapa 4: o que sincronizar

| Classe | Como | Frequência |
|---|---|---|
| Pose local | Posição, giro horizontal, ID de animação, arma, vida. | 10 a 20 Hz, interpolados. |
| Indicadores, progresso, itens, portas | Diferenças de campo de bits. | Evento. |
| Inimigos, chefes | Autoridade única (host) ou aceitar cópias por jogador. | 5 a 10 Hz para host ou nenhuma. |
| Câmera | Não sincronizar; cada cliente tem a própria. | Nenhuma. |
| Cenas, carregamento | Barreira: aguardar ambos ou desativar pausas das cenas (Jak Teamruns executa em tempo real para não bloquear outro; [DSOGaming](https://www.dsogaming.com/news/the-unofficial-pc-port-of-jak-daxter-now-supports-online-and-local-multiplayer/)). | Evento. |

### <a id="step-5-latency-and-determinism-limits"></a>Etapa 5: limites de latência e determinismo

- Sincronização de memória não é lockstep, tolera RTT de 50 a 150 ms em exploração. Combate de reflexos e quebra-cabeças acoplados à física precisam de autoridade do host ou parecerão errados.
- Emuladores executam livremente; não tente travar quadros. Use interpolação.
- Compatibilidade de salvamentos: ambos começam de estados compatíveis. Abordagem Anchor, carregar estado do host ao entrar, é bom modelo ([anchor](https://github.com/garrettjoecox/anchor)).
- Ajustes de velocidade e overclock (algumas correções Deadlocked usam ciclo EE em 130%, [wiki PCSX2](https://wiki.pcsx2.net/SCES-53285)) mudam tempo, não organização RAM; mantenha clientes idênticos.
- Ponteiros mudam por versão/região. Use serial e CRC do executável (mesma nomenclatura dos pnach) para escolher tabela de endereços.

### <a id="step-6-testing-two-instances-on-one-pc"></a>Etapa 6: testar duas instâncias num PC

- Execute duas instalações PCSX2 portáteis, com vagas PINE diferentes se possível (não documentado; teste). **NÃO VERIFICADO**.
- Execute duas pontes em portas loopback.
- Teste por script ([automated-qa.md](automated-qa.md)): carregue estado, escreva valor de controle no jogador A, verifique por PINE se B vê a posição remota dentro da tolerância após N segundos e confira indicadores do mundo. Ninguém precisa olhar a tela.
- Ambas competem pela GPU; use baixa resolução e renderização por software ou Vulkan na segunda se o tempo de quadros piorar.
- Confira se usuário não está jogando antes de iniciar (regra de PC compartilhado).

## <a id="6-per-console-quick-recipes"></a>6. Receitas rápidas por console

Notas curtas de decisão; detalhes nas fontes acima.

- **N64:** use recompilação/descompilação existente (SM64 coop-dx, SoH + Anchor). Senão ModLoader64 para jogos compatíveis ou Lua BizHawk com retransmissor Node/Python. Rede de jogos para 4 por gopher64.
- **GameCube/Wii:** rede Dolphin para multiplayer local; Dolphin Memory Engine ou fork Python Felk para pontes de um jogador para cooperativo. Wiimmfi para serviços Wii encerrados.
- **PS1:** sem rede na versão principal; Lua BizHawk funciona com PS1 segundo lista de sistemas ([BizHawk](https://github.com/TASEmulators/BizHawk)). Confira ports primeiro (esforços como OpenGOAL).
- **GBA/GB:** Lua mGBA com sockets é o mais limpo; script por instância e retransmissor TCP no meio. Mundos compartilhados tipo Pokémon escrevem dados de "outro treinador" em vagas de NPC.
- **DS/3DS:** use emulação própria de rede local sem fio (salas Azahar, Wi-Fi melonDS), não sincronização RAM, se jogo já oferecer esse modo.
- **PSP:** ad hoc PPSSPP com retransmissores para jogos que tenham ad hoc.
- **PS3/Xbox/360:** RPCN ou XLink Kai para jogos com modo de rede. RAM é território não testado.
- **Switch:** fora do escopo salvo contexto legal explicitamente fornecido pelo usuário; veja tabela.

## <a id="7-legal-and-attribution"></a>7. Questões legais e atribuição

- Não hospede nem forneça links de ROMs, ISOs, chaves ou BIOS neste repositório.
- Mods distribuem somente patches (deltas IPS/xdelta/pnach) aplicados à extração própria. Não distribua dados protegidos por direitos autorais.
- Servidores retomados são infraestrutura de terceiros: informe no README e ofereça hospedagem própria (Anchor tem pública e própria, [README](https://github.com/garrettjoecox/anchor)).
- Emulação Switch é juridicamente sensível: Yuzu e Ryujinx originais encerrados em 2024, sucessores sob pressão segundo fontes secundárias ([tech-insider](https://tech-insider.org/?p=19175)). Limite o trabalho a emuladores abertos existentes e não contribua código de contorno de proteções.
- Crédito e licença: respeite GPL (Z64Online ModLoader64 é GPL-3.0 segundo a página) e confira licença em todo fork utilizado (página Anchor não mostrou arquivo).

## <a id="8-open-questions-and-unverified-items"></a>8. Questões abertas e itens não verificados

Confira antes de dizer ao usuário que funcionam.

1. Se PCSX2 aceita várias vagas PINE em duas instâncias simultâneas.
2. Se algum fork PCSX2 de rede compila sobre master de 2026 e roda jogo real.
3. Se DuckStation tem servidor PINE oficial e se GGPO de HeatXD é mantido.
4. Estado da manutenção de ModLoader64 e Z64Online em 2026 (repositórios existem, atividade incerta).
5. Se BBA Dolphin ainda alcança servidores PSO privados nas compilações atuais.
6. Se Horizon ou Clank funcionam com DEV9 PCSX2.
7. Parsec como jogo remoto (sem fonte obtida).
8. Lista de jogos RPCS3 em rede e existência de ponte RAM para ele.
9. Todos os recursos de rede dos emuladores Switch.
10. Rede Project64 nas compilações atuais.
11. Scripts na versão principal Dolphin (relatados como parados; só fork).

Nintendo Switch tem página própria: [switch.md](switch.md) (rede local sem fio, hooks no seu console, descompilações).
