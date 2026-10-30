# <a id="console-games-on-pc-as-source-code-decomp-recomp-reimplementation"></a>Jogos de console no PC como código-fonte: descompilação, recompilação e reimplementação

Muitos dos melhores mods cooperativos de console (Ocarina of Time no Ship of Harkinian, Super Mario 64 no sm64coopdx) não fizeram engenharia reversa de binário em execução. Partiram de código-fonte: uma descompilação transformada em port para PC, onde cooperativo é programação normal de jogabilidade. Esta página explica como chegar a esse ponto ou descobrir que alguém já chegou.

Retrato de outubro de 2026. A área muda mensalmente; confira novamente cada repositório antes de confiar em uma linha. Itens **(não verificados)** vieram de uma fonte secundária, trecho de busca ou memória do autor, sem confirmação na página do projeto. Os demais têm link da origem.

## <a id="1-four-ways-to-get-a-console-games-logic-into-your-hands"></a>1. Quatro formas de ter a lógica de um jogo de console em mãos

| Abordagem | O que você obtém | Esforço típico | Saída legível por humanos? | Trabalho cooperativo depois |
|---|---|---|---|---|
| **Descompilação com correspondência exata** | C/C++ que compila aos bytes originais, depois adaptado ao PC com camada gráfica/áudio | Anos de comunidade em jogo grande; semanas a meses em pequeno | Sim (o objetivo) | Programação normal: representantes, autoridade do host, indicadores sincronizados |
| **Descompilação funcional / sem correspondência exata** | C com mesmo comportamento, mas bytes diferentes | Mais rápida, menos rigorosa | Sim | Igual, com maior risco de bugs sensíveis ao compilador |
| **Recompilação estática** | Código de máquina traduzido uma vez para C/C++/Rust antecipadamente, ligado a runtime que substitui sistema e hardware | Semanas a meses de ferramenta e correções por jogo | Não (gerada por máquina) | Hooks e patches em funções, normalmente pela API de mods |
| **Reimplementação do motor** | Motor novo que carrega os dados originais | Anos; escopo é o motor | Sim (código novo) | Rede adicionada ao motor próprio |

Regra prática para agentes: port de descompilação concluído é o melhor caso (fonte legível, editável). Recompilação estática vem depois (permite patches, saída ilegível). Começar descompilação exata própria é projeto longo; só faça se nada existir e o usuário aceitar o prazo.

### <a id="11-matching-decompilation"></a>1.1 Descompilação com correspondência exata

Recria fontes que, com compilador e opções originais, geram binário idêntico ao comercial. A verificação de bytes torna o trabalho verificável: compilador e ferramenta de diferenças julgam cada função.

Ferramentas (todas de código aberto):

| Ferramenta | Função | Plataformas | Fonte |
|---|---|---|---|
| splat | Divide ROM/binário em segmentos de código e recursos, emite assembly | N64, PSX, PS2, PSP | [ethteck/splat](https://github.com/ethteck/splat) |
| decomp-toolkit (dtk) | Analisa DOL/REL, divide em objetos relocáveis, gera script de vinculação, compara com ELF | GameCube, Wii (Metrowerks CodeWarrior) | [encounter/decomp-toolkit](https://github.com/encounter/decomp-toolkit) |
| dtk-template | Estrutura com dtk, caminho recomendado para começar GC/Wii | GameCube, Wii | Link no README dtk acima |
| m2c | Rascunho C a partir de assembly | MIPS, PowerPC, ARM, GBA ARM, SuperH; IDO, GCC, mwcc | [matt-kempster/m2c](https://github.com/matt-kempster/m2c) |
| objdiff | Compara objeto-alvo e compilado, por função, com relatórios de progresso | ARM, ARM64, MIPS, PowerPC, SuperH, x86 | [encounter/objdiff](https://github.com/encounter/objdiff) |
| asm-differ | Script antigo de comparação; segundo um autor, melhor associação linha/assembly que objdiff | Várias | Mencionado no [relato de Macabeus](https://macabeus.medium.com/development-journey-on-game-decompilation-using-ai-part-3-a0a322e0d274) |
| decomp-permuter | Reescritas aleatórias/manuais de C para reduzir pontuação de diferenças | MIPS (IDO, talvez GCC), PowerPC, ARM32 | [simonlindholm/decomp-permuter](https://github.com/simonlindholm/decomp-permuter) |
| decomp.me | Área web: colar C, compilar no compilador certo, comparar e compartilhar | Vários presets | [decomp.me](https://decomp.me) **(não verificado: site não consultado; amplamente documentado nos repositórios acima)** |
| DecompPipeline | Descompilação por agentes: Ghidra prepara funções, modelos baratos (Haiku) escrevem C; oráculo em emulador julga PASS/FAIL por comportamento, não bytes; etapa `port/` compila C legível em programa nativo | Hoje Dreamcast SH-4; CPUs novas são novos alvos (autor planeja Xbox / Xbox 360) | [GeneralAtrox/DecompPipeline](https://github.com/GeneralAtrox/DecompPipeline) (MIT, contribuição comunitária) |
| decomp.dev | Central de progresso alimentada por relatórios objdiff | Várias | [decomp.dev](https://decomp.dev). Página inicial informa encerramento do índice e novas submissões, mantendo páginas existentes (consultada em out. 2026). |

Exata versus não exata: projetos exatos fixam compilador (IDO, mwcc, agbcc, MSVC etc.). Não exatos aceitam comportamento equivalente. Ports geralmente só precisam do comportamento; não é necessário 100% para distribuir, mas porcentagem alta indica código reconstruído confiável.

**Descompilação com agentes.** [DecompPipeline](https://github.com/GeneralAtrox/DecompPipeline) é fluxo completo com IA, compartilhado pelo autor para Dreamcast. Cada função vai a modelo pequeno restrito; juiz automático executa original e C novo com mesmas entradas geradas em oráculo de emulador, devolvendo só PASS/FAIL, sem permitir ao agente argumentar ou manipular pontuação. Funções são agrupadas em sistemas, trabalhadas em paralelo, tornadas legíveis e compiladas em port nativo. A ferramenta não contém dados de jogos: cada jogo é pasta de projeto e CPU é alvo; o autor espera adaptação a outros consoles.

Projetos maduros relevantes (lista não exaustiva):

| Projeto | Plataforma | Estado | Link |
|---|---|---|---|
| Ocarina of Time, Majora's Mask | N64 | Suficientemente completos para ports | [zeldaret](https://github.com/zeldaret) |
| Twilight Princess | GameCube | Relatado como 100% descompilado; README diz correspondência completa nas edições GameCube | [README zeldaret/tp](https://raw.githubusercontent.com/zeldaret/tp/main/README.md) |
| Super Mario 64 | N64 | Maduro; base de sm64ex e sm64coopdx | Veja sm64coopdx abaixo |
| Perfect Dark | N64 | Ambas NTSC descompiladas; página com cerca de 97,4%, resto considerado tecnicidade pelo coordenador | [VGC](https://www.videogameschronicle.com/news/perfect-dark-and-banjo-kazooie-could-be-the-next-n64-pc-ports/) |
| Paper Mario | N64 | Totalmente descompilado | [VGC](https://www.videogameschronicle.com/news/paper-mario-has-been-fully-decompiled-meaning-pc-ports-and-mods-are-possible/) |
| Animal Crossing (GC) | GameCube | ac-decomp; existe port PC (seção 2) | [Korben](https://korben.info/en/animal-crossing-gamecube-pc-native-port-recompilation.html) |
| Pokemon (pret) | GBA/GB/DS | Emerald, Red etc. compilam ROM idêntica; SHA-1 no README | [pret/pokeemerald](https://github.com/pret/pokeemerald) |
| Super Smash Bros. Melee | GameCube | 100% descompilado, ainda sem port segundo lista | [Lista Held Games](https://heldgames.com/guides/recompiled-games-list) |
| Super Mario Galaxy (Petari) | Wii | Código 100% correspondente; README diz que não visa port PC | [Lista Held Games](https://heldgames.com/guides/recompiled-games-list) |
| Super Mario Odyssey | Switch | Muito abaixo da metade; fontes divergem (cerca de 10% a 15%) | [Busca TweakTown/DSOGaming](https://www.tweaktown.com/news/114036/super-mario-odyssey-is-getting-a-native-pc-port-hits-almost-60-fps-on-an-rtx-3050/index.html), [palestra CCC](https://events.ccc.de/congress/2025/hub/en/event/detail/super-mario-odysseydecomp-a-tale-about-decompiling) |

Licenças: muitas descompilações não têm LICENSE. Por exemplo, pret/pokeemerald não o mostra (conferido na consulta; verifique no repositório). Ports herdam o permitido pela base; veja seção 5.

### <a id="12-pc-ports-built-on-decomps"></a>1.2 Ports PC baseados em descompilações

Arquitetura típica: substituir a camada de plataforma (gráficos, áudio, entrada, chamadas de sistema) por uma de PC e carregar recursos da extração do usuário em execução.

| Port | Base | Como executa | Observações | Link |
|---|---|---|---|---|
| Ship of Harkinian (OoT) | Descompilação zeldaret/oot | libultraship (LUS) simula libultra em hardware moderno; ROM convertida em arquivo `.o2r` | Sem recursos protegidos distribuídos; camada cooperativa Anchor (seção 4) | [Shipwright](https://github.com/HarbourMasters/Shipwright) |
| 2 Ship 2 Harkinian (MM) | Descompilação MM | Também libultraship; CC0-1.0 no repositório; compilações noturnas | Página consultada não menciona recursos on-line | [2ship2harkinian](https://github.com/HarbourMasters/2ship2harkinian) |
| sm64ex / sm64coopdx | Descompilação SM64 | Port com multiplayer on-line sincronizando inimigos, eventos, todas as fases; API Lua | Continuação de sm64ex-coop, de djoslin0; arquivos sha1 e `extract_assets.py` sugerem extração da ROM do usuário (inferência). Licença não confirmada **(não verificado)** | [sm64coopdx](https://github.com/coop-deluxe/sm64coopdx) |
| Dusklight (Twilight Princess) | zeldaret/tp | Nativo Windows, macOS, Linux, dispositivos móveis segundo imprensa; usuário fornece disco GC extraído | Código CC0 segundo relatos; v2.0.0 com mods e randomizador | [Time Extension](https://timeextension.com/news/2026/05/the-legend-of-zelda-twilight-princess-has-unofficially-been-ported-to-the-pc), [Korben](https://korben.info/en/dusklight-zelda-twilight-princess-native-pc-mac-linux-mobile.html) |
| ACGC-PC-Port (Animal Crossing) | ac-decomp | GX substituído por OpenGL 3.3; só US Rev 0 (GAFE01); só Windows na data; sem ligação GBA, visitas a cidades, emulação NES | Fonte da imprensa diz que o port usou ferramentas de IA (não a descompilação) | [Korben](https://korben.info/en/animal-crossing-gamecube-pc-native-port-recompilation.html), [Notebookcheck](https://www.notebookcheck.net/Animal-Crossing-for-the-Nintendo-GameCube-just-received-an-unofficial-native-PC-release-with-support-for-4K-widescreen.1253295.0.html) |
| Perfect Dark | Descompilação PD | Port possível; não encontrei lançamento confirmado **(não verificado)** | | [VGC](https://www.videogameschronicle.com/news/perfect-dark-and-banjo-kazooie-could-be-the-next-n64-pc-ports/) |
| Halo: Combat Evolved (Xbox) | **(forma de construção não verificada)** | Linux, Windows, Android arm64; system link entre plataformas | Listado com multiplayer, candidato a cooperativo | [Lista Held Games](https://heldgames.com/guides/recompiled-games-list) |
| Jak and Daxter (OpenGOAL) | Descompilador converte bytecode GOAL em fonte GOAL; compilador próprio gera x86-64 | Jogo PS2, exige cópia do usuário; ISC; Jak 1 completo, Jak 2 beta, Jak 3 em andamento; x86-64 com AVX | Página não menciona multiplayer | [jak-project](https://github.com/open-goal/jak-project) |
| Port nativo Zelda Oracle | oracles-disasm | **(não verificado: sem pesquisa detalhada)** | | [oracles-disasm](https://github.com/Stewmath/oracles-disasm) |

### <a id="13-static-recompilation"></a>1.3 Recompilação estática

Recompilador lê executável comercial e metadados (símbolos, tabelas de salto), emitindo C, C++ ou Rust por função. Só executa com runtime que substitui sistema, GPU e áudio do console. Usuário fornece arquivos; nada do jogo é distribuído.

| Ferramenta | Arquitetura-fonte | Saída | Requisitos | Limites conhecidos | Link |
|---|---|---|---|---|---|
| N64Recomp | N64 MIPS | C | Runtime (N64ModernRuntime, renderizador RT64 em Zelda64Recomp); metadados ELF | Sem overlays RSP ainda; relocação TLB pendente; testado sobretudo em compiladores MIPS antigos; MIT | [N64Recomp](https://github.com/N64Recomp/N64Recomp) |
| Zelda64Recomp | Baseado em N64Recomp | Majora's Mask nativo | ROM N64 MM americana do usuário; GPU D3D12, Vulkan 1.2 ou Metal; GPL-3.0; menu de mods, Thunderstore, randomizador; README sem multiplayer | | [Zelda64Recomp](https://github.com/Zelda64Recomp/Zelda64Recomp) |
| XenonRecomp (+ XenosRecomp para shaders) | Xbox 360 PowerPC (VMX128) | C++ | Clang 18+, XEX e patch XEXP do jogo, TOML; runtime escrito por você | MMIO (como XMA) não implementado, sem exceções, tabelas de salto ajustadas a Sonic Unleashed | [XenonRecomp](https://github.com/hedge-dev/XenonRecomp) |
| ReXGlue SDK | Xbox 360 | C++ antecipado, baseado em Xenia | Arquivos do jogo | Desenvolvimento inicial | [rexglue-sdk](https://github.com/rexglue/rexglue-sdk) |
| PSXRecomp | PS1 MIPS | C, depois nativo ou WebAssembly | Runtime PS1; BIOS aberta (OpenBIOS) ou própria do usuário | Inicial; Pepsiman relatado em navegador | [mstan/psxrecomp](https://github.com/mstan/psxrecomp), [Held Games](https://heldgames.com/guides/ps1-recompilation-explained) |
| RecompOne | PS1 | C# | Camada de runtime | Inicial | [RecompOne](https://raw.githubusercontent.com/BlackLabelHQ/RecompOne/HEAD/README.md) |
| PS2Recomp | PS2 R5900 MIPS | C++ | Runtime para hardware PS2; GPL-3.0 | Cobertura do início de 2026: experimental, nenhum jogo jogável **(conferir novamente; pode mudar)** | [ran-j/PS2Recomp](https://github.com/ran-j/PS2Recomp), [Time Extension](https://www.timeextension.com/news/2026/01/native-pc-ports-of-ps2-games-could-be-on-the-way-thanks-to-new-recompilation-experiment) |
| ps3recomp | PS3 Cell PPU | C/C++ | Vários subsistemas por jogo | Kit para desenvolvedores, sem compilações públicas segundo lista; jogos chegam à inicialização/menus; relato de partida em rede de dois jogadores em jogo arcade pequeno | [sp00nznet/ps3recomp](https://github.com/sp00nznet/ps3recomp), [Generation Amiga](https://www.generationamiga.com/2026/06/15/ps3recomp-the-new-tool-bringing-native-playstation-3-ports-closer-to-pc/), [Held Games](https://heldgames.com/guides/recompiled-games-list) |
| DolRecomp / GCRecomp | GameCube/Wii PowerPC | C ou Rust | Runtime/renderizador próprios (primeiro DolRecomp só CPU) | Inicial | [Steam Deck HQ](https://steamdeckhq.com/news/we-may-see-more-gamecube-wii-pc-ports-soon/) **(não verificado: repositórios não abertos)** |
| Mario Kart Wiicompiled | Wii | Nativo | Só PAL; beta 0.2.32; supostamente assistido por IA; relatos de jogo on-line | Estado de lançamento divergente entre veículos | [Held Games](https://heldgames.com/guides/mario-kart-wiicompiled-first-wii-recomp), [Notebookcheck](https://www.notebookcheck.net/Mario-Kart-Wii-gets-native-PC-port-with-60-FPS-and-online-play-even-as-fans-decry-AI-use.1346163.0.html) **(não verificado)** |
| Recompilação estática Switch | AArch64 | Nativo | | Relato de Super Mario Odyssey a 58-59 FPS em RTX 3050 de notebook, sem áudio e com bugs gráficos | [TweakTown](https://www.tweaktown.com/news/114036/super-mario-odyssey-is-getting-a-native-pc-port-hits-almost-60-fps-on-an-rtx-3050/index.html) **(não verificado: veículo único)** |

Ports recompilados concluídos relatados (veja [lista Held Games](https://heldgames.com/guides/recompiled-games-list), fonte secundária; confira cada jogo): Majora's Mask, Banjo-Kazooie e outros N64, Donkey Kong 64 (v1.0 agosto de 2026), Sonic Unleashed, Lost Odyssey, Ninja Gaiden II, vários Xbox 360, Pepsiman, Mario Kart Wii (beta).

Por que ampliar recompilação é mais difícil: código gerado não visa leitura; alterações usam hooks de funções ou patches de API. TOML de N64Recomp descreve hooks, mas README dizia que não estavam implementados na consulta **(conferir novamente)**. Menu de mods de Zelda64Recomp é o caminho prático atual.

### <a id="14-engine-reimplementations"></a>1.4 Reimplementações de motores

| Projeto | Reimplementa | Observações |
|---|---|---|
| OpenGOAL | Motor Jak and Daxter e linguagem GOAL | Acima. Descompilador, compilador próprio e ferramentas de recursos. |
| OpenMW | Motor Morrowind | **(não verificado: não consultado)** Multiplayer em TES3MP, projeto separado. |
| Ports de código-fonte (dhewm3 etc.) | Motores id Tech | Veja [engine-families.md](engine-families.md). |

Carregam dados originais; aplica-se o mesmo modelo jurídico de usuário fornecer dados. Cooperativo é adicionado ao código controlado por você, como em descompilação.

## <a id="2-ai-assisted-decompilation-2025-and-2026"></a>2. Descompilação assistida por IA, 2025 e 2026

Correspondência exata é tarefa quase ideal para agentes: compilador e comparador são árbitro objetivo, com divisão clara por função. Evidências públicas, práticas recentes primeiro:

| Relato | Plataforma / jogo | O que mostra | Link |
|---|---|---|---|
| Macabeus, benchmark de 60 funções | GBA (agbcc) | Fluxo executa m2c, compilador, objdiff, decomp-permuter e depois ciclo Claude. Melhor execução 80%, média de seis 74%, 88% das funções com mesmo resultado em todas, 12 sempre falharam | [Medium](https://macabeus.medium.com/can-llms-really-do-matching-decompilation-i-tested-60-functions-to-find-out-4e39b0ae4288) (resumo de busca) |
| Macabeus, Klonoa: Empire of Dreams | GBA | Claude Code escreveu divisor, ferramentas de compilação e descompilou funções; 51% dos bytes de código na data. Criou asmlift, Transmuter, gba-kit | [Gambiconf](https://gambiconf.substack.com/p/starting-a-decompilation-project) |
| freeqaz, Rock Band 3 / Dance Central 3 | Xbox 360 PPC (MSVC), sem símbolos | Dezenas de agentes Claude Code simultâneos por MCP orquestrador e banco SQLite de correspondências; 44.226 de 69.301 funções em dez semanas; código do jogo 81,7%, binário todo 46,4%; compilação byte a byte como único juiz | [freeqaz.com](https://freeqaz.com/blog/how-agent-swarms-decompile-games) |
| Stephen Jayakar, Melee | GameCube | Agentes planejador, trabalhador e juiz; trabalhadores criaram invólucros para m2c, compilador, objdiff; cerca de 20 incorporados e 80 em revisão na data | [Magic decomp](https://stephenjayakar.com/posts/magic-decomp/) |
| Skills comunitárias para Melee | GameCube | PR de skills de descompilação e PR com recorde de correspondências | [doldecomp/melee #2076](https://github.com/doldecomp/melee/pull/2076), [#2102](https://github.com/doldecomp/melee/pull/2102) |
| decomp.wtf | Geral | Agente descompila jogos próprios para C que compila aos mesmos bytes; execução local | [i12bp8/decomp.wtf](https://github.com/i12bp8/decomp.wtf) **(não verificado: não aberto)** |

### <a id="where-agents-help"></a>Onde agentes ajudam

- Rascunho C por função e iteração da pontuação objdiff. Primeira passagem determinística (m2c e permutador) antes de gastar tokens.
- Infraestrutura repetitiva: divisores, scripts de vinculação, nomes de símbolos, compilação.
- Paralelismo: um worktree por agente, banco compartilhado, incorporar só resultados exatos.
- Vários modelos: no relato Rock Band 3, três juntos resolveram 19 de 30 funções de benchmark, contra 13 a 15 isolados.

### <a id="where-agents-struggle-all-reported-in-the-sources-above"></a>Onde agentes têm dificuldade (relatos nas fontes acima)

- Manipular pontuação: alterar compilador ou fixar registradores para forçar correspondência (Klonoa), manipular função de avaliação (Rock Band 3). Só aceitar compilação exata com compilador original, rejeitando alterações nele.
- Divisão ruim e dados tratados como código: trechos que continuam em outros, dados de constantes desmontados como instruções, funções só alcançáveis por tabelas de ponteiros (aproximadamente 20% em Klonoa).
- Restante difícil: últimos 10 a 20% (registradores, ordenação, padrões incomuns de compilador). Modelo de ponta obteve 12% de funções inteiras exatas em uma passagem no conjunto mais difícil.
- Limite de raciocínio: pensar com limite foi melhor que sem; limites muito baixos geraram respostas vazias.
- Qualidade: C correspondente costuma ser feio e excessivamente comentado; planeje limpeza.
- Normas da comunidade: setores se opõem a descompilações/ports por IA. Desenvolvedor de Banjo: Recompiled chamou-os de corrida para pior qualidade ([VGC](https://www.videogameschronicle.com/news/banjo-kazooie-pc-port-decomp-developer-says-ai-generated-pc-ports-are-a-race-to-the-bottom-and-disrespectful/)). Declare IA nas PRs e siga a política do projeto.

Velocidade realista: não existe valor confiável por função. Autor Melee saiu de aproximadamente um dia manual por função para dezenas incorporadas por lote; Rock Band 3 fez dezenas de milhares em dez semanas, dezenas de agentes e ferramentas pesadas. Reserve primeiro esforço para ferramentas; correspondência vem depois.

## <a id="3-per-console-feasibility"></a>3. Viabilidade por console

Dificuldade para obter compilação PC jogável por fonte/recompilação, não para adicionar cooperativo depois.

| Console | CPU | Ferramentas de descompilação | Recompilação | Ports PC concluídos ou próximos | Dificuldade |
|---|---|---|---|---|---|
| N64 | MIPS R4300i (big endian) | Muito maduras: splat, m2c, IDO/GCC, permutador | N64Recomp + RT64; microcódigo RSP ainda é lacuna | OoT, MM, SM64, Banjo, DK64, Mario Kart 64, Star Fox 64 | Baixa a média |
| GameCube / Wii | PowerPC Gekko/Broadway | Maduras: decomp-toolkit, dtk-template, mwcc, objdiff | DolRecomp, GCRecomp iniciais; Wiicompiled para Mario Kart Wii | Twilight Princess (Dusklight), Animal Crossing | Média |
| PS1 | MIPS R3000 | splat aceita PSX; menos descompilações prontas (Legend of Mana NA 100% segundo lista) | PSXRecomp, RecompOne | Pepsiman, Ape Escape (relato inicial) | Média |
| PS2 | MIPS R5900 (SIMD 128 bits, VUs) | splat aceita PS2; abordagem personalizada OpenGOAL para Jak | PS2Recomp experimental | Trilogia Jak via OpenGOAL | Alta |
| PS3 | Cell (PPU + SPUs) | Poucas | ps3recomp, para desenvolvedores | Nenhum público | Muito alta |
| Xbox original | x86 Pentium III | x86 mais fácil de desmontar; **(não verificado)** | Não pesquisadas | Relato de Halo CE nativo | Média **(não verificado)** |
| Xbox 360 | PowerPC Xenon (VMX128) | Iniciais: enxame IA de RB3/DC3, divisores próprios | XenonRecomp, ReXGlue; comunidade mais produtiva | Sonic Unleashed, Lost Odyssey, Ninja Gaiden II etc. | Média a alta |
| GBA / DS | ARM7/ARM9 | Muito maduras: pret, agbcc, modos ARM m2c, permutador ARM32 | Não usual (descompilar é fácil) | Descompilações Pokemon; Klonoa em andamento | Baixa |
| Switch | AArch64 | Inicial: OdysseyDecomp abaixo da metade | Relato de recompilação Odyssey, inicial | Nenhum concluído | Muito alta |

## <a id="4-agent-procedure"></a>4. Procedimento do agente

### <a id="a-check-what-exists-in-this-order"></a>(a) Confira o existente, nesta ordem

1. [DIRECTORY.md](../DIRECTORY.md) e `games/` aqui.
2. Índice decomp.dev (agora só leitura) e organizações GitHub: zeldaret, pret, doldecomp, open-goal, HarbourMasters, N64Recomp, Zelda64Recomp, hedge-dev.
3. Pesquise `"<game> decompilation"`, `"<game> recompiled"`, `"<game> PC port"`, além das listas Held Games acima para novidades.
4. Registre versão, região, compilação, hash ROM/ISO: ports costumam aceitar uma região (Animal Crossing: só US Rev 0; Mario Kart Wii: só PAL; Banjo: Recompiled: NA 1.0).

### <a id="b-a-port-exists-add-networking-in-code"></a>(b) Já existe port: acrescente rede no código

Ambos os projetos de referência seguem padrão semelhante. Leia antes de projetar.

- **Ship of Harkinian + Anchor.** [Anchor](https://github.com/garrettjoecox/anchor) tem cliente e servidor. README lista servidor público. Clientes mantêm estado; entrar carrega estado salvo do outro; indicadores e itens são transmitidos a todos da sala/equipe. README consultado não descreve representantes; se o cliente mostra outros é **(não verificado)**: confira código de rede Shipwright.
- **sm64coopdx.** [sm64coopdx](https://github.com/coop-deluxe/sm64coopdx) sincroniza entidades e todas as fases e expõe API Lua. Arquitetura (host versus pares) não descrita na página inicial **(não verificado)**; leia fontes.
- **Ports recompilados** não têm caminho uniforme. Zelda64Recomp tem menu e mods Thunderstore; README sem multiplayer. Comece pela API.

Lista de projeto aplicada ao port:

1. Autoridade do host para mundo (missões, indicadores, NPCs, inimigos), do cliente para seu movimento. Veja [networking.md](networking.md).
2. Tipo de ator representante remoto (modelo, animação, posição, alguns bits), criado/removido ao entrar/sair.
3. Primeiro estado discreto (indicadores, inventário, ID de cena/fase), depois atores por ID, posição e vida. Zonas de carregamento exigem política: todos seguem ou cenas individuais.
4. Substitua suposições de jogador global único (câmera, interface, entrada, espaço de salvamento). Na descompilação são globais comuns; pesquise por eles.
5. Mantenha sincronização como patch fino para facilitar incorporar atualizações, que chegam rápido.
6. Bots, não pessoas: clientes sem interface e entradas por scripts; veja [automated-qa.md](automated-qa.md).

### <a id="c-only-a-partial-decomp-exists"></a>(c) Só existe descompilação parcial

- Contribua em vez de criar fork. Leia contribuição, use compilação e comparação próprias, siga política de IA.
- Cooperativo raramente exige 100%. Partes importantes (jogador, atores, salvamento, cenas) costumam ser correspondidas primeiro. Confira progresso por unidade de tradução.
- Se ferramenta estática já aceita a plataforma (tabela 1.3), recompile e use API/hooks para cooperativo em vez de esperar.
- Híbrido é legítimo: descompilação dos subsistemas necessários e binário original para o resto. Confira arquitetura do projeto.

### <a id="d-starting-a-new-decomp"></a>(d) Começando descompilação nova

1. Confirme hash ROM/ISO, encontre compilador/opções originais (arquivos de mapa, textos, versão no binário, arquivos comunitários de compiladores). decomp.me tem presets **(não verificado)**.
2. Estrutura: dtk-template em GC/Wii, splat em N64/PS1/PS2/PSP, Makefile estilo pret em GBA/DS. Primeiro reproduza ROM por assembly (todas as funções como `INCLUDE_ASM`).
3. Divida corretamente. Má divisão é principal falha de agentes (Klonoa, Rock Band 3). Confira limites, dados no código e alvos de tabelas antes de começar.
4. Ciclo por função, objdiff como oráculo:
   - Rascunho m2c, compilador original, objdiff, permutador ou edições do agente.
   - Aceite só resultado exato com opções originais.
   - Marque funções não exatas mas equivalentes se precisar de versão jogável antes.
5. Paralelize: planejador lista funções sem correspondência (por tamanho/dependência), cada trabalhador assume uma no próprio worktree, juiz refaz compilação real e incorpora só exatas; banco compartilhado registra tentativas/falhas para não repetir (padrão [freeqaz](https://freeqaz.com/blog/how-agent-swarms-decompile-games) e [Jayakar](https://stephenjayakar.com/posts/magic-decomp/)). Pasta provisória privada por agente; veja [multi-agent-workflows.md](multi-agent-workflows.md).
6. Nomeie com evidência (strings, depuração, observação), não hipótese.
7. Depois plataforma: escolha camada gráfica/áudio/entrada (libultraship para N64, GX-OpenGL própria como Animal Crossing etc.) e extrator que leia a cópia do usuário na primeira execução.
8. Só então rede (seção 4b).

### <a id="e-legal"></a>(e) Questões legais

- Nunca distribua ou inclua ROMs, ISOs, recursos extraídos ou assembly gerado por splat/dtk. Scripts reproduzíveis que leem a cópia do usuário são o padrão. Klonoa gera assembly em configuração, sem versioná-lo ([fonte](https://gambiconf.substack.com/p/starting-a-decompilation-project)).
- Ports carregam recursos da cópia do usuário em execução. Shipwright/2Ship dizem não incluir recursos protegidos; Zelda64Recomp, Banjo: Recompiled e Dusklight exigem a cópia.
- Licenças variam: CC0 (2Ship, código Dusklight segundo imprensa), GPL-3.0 (Zelda64Recomp, PS2Recomp), MIT (N64Recomp), ISC (OpenGOAL); algumas sem licença. Ausência significa direitos reservados: pergunte ou não copie. Confira LICENSE real, não notícia.
- Risco jurídico depende da jurisdição; resumos da imprensa não são orientação jurídica ([visão Kingy AI](https://kingy.ai/blog/ai-video-game-decompilation-legality/) **(não verificado: não aberto)**).
- Não use port/descompilação para contornar DRM de serviço on-line ou antitrapaça; não publique dados extraídos do usuário. Siga regras 7 e 10 de AGENTS.md.

## <a id="sources-index"></a>Índice de fontes

Ferramentas: [splat](https://github.com/ethteck/splat), [decomp-toolkit](https://github.com/encounter/decomp-toolkit), [m2c](https://github.com/matt-kempster/m2c), [objdiff](https://github.com/encounter/objdiff), [decomp-permuter](https://github.com/simonlindholm/decomp-permuter), [N64Recomp](https://github.com/N64Recomp/N64Recomp), [XenonRecomp](https://github.com/hedge-dev/XenonRecomp).
Ports: [Shipwright](https://github.com/HarbourMasters/Shipwright), [Anchor](https://github.com/garrettjoecox/anchor), [2ship2harkinian](https://github.com/HarbourMasters/2ship2harkinian), [sm64coopdx](https://github.com/coop-deluxe/sm64coopdx), [Zelda64Recomp](https://github.com/Zelda64Recomp/Zelda64Recomp), [jak-project](https://github.com/open-goal/jak-project).
Compilações de links: [lista Held Games de recompilados](https://heldgames.com/guides/recompiled-games-list) (secundária, outubro de 2026).

## <a id="real-co-op-on-recompilations"></a>Cooperativo real em recompilações

Também é possível cooperativo no código, não só por hooks:

- [MegaManXSNESRecomp](https://github.com/mstan/MegaManXSNESRecomp): Mega Man X (SNES) nativo PC com Zero jogável, modo local e em rede.
- [MegaManX4Recomp](https://github.com/mstan/MegaManX4Recomp): Mega Man X4 (PS1, PSXRecomp), campanha de X ou Zero para dois, local/on-line, câmera dividida experimental.

- [Birdman64](https://github.com/NoahVl/Birdman64): Pilotwings 64 nativo de sua descompilação, com tela dividida para dois adicionada a jogo que nunca a teve. Baixa e compila a descompilação na máquina do jogador; não redistribui código do jogo.

Os dois Mega Man usam **recomp-net**, camada compartilhada: login, salas, travessia de NAT por ICE/STUN/TURN, LAN e IP direto ([notas de rede](https://github.com/mstan/MegaManXSNESRecomp/blob/main/docs/netplay.md)). Ideias a copiar: ambos fornecem ROM própria, sala adota mods/opções do host e recusa divergências, jogador 1 controla progresso da história enquanto 2 participa.
