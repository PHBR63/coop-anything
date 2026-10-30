# <a id="middle-earth-shadow-of-war-research-notes"></a>Middle-earth: Shadow of War: notas de pesquisa

Notas brutas, com a fase mais recente por último. Caminhos usam `<game dir>`. Objetivo: cooperativo online em mundo compartilhado
na campanha principal (dois jogadores em um Mordor, um mundo Nemesis).

## <a id="session-2026-10-20-triage-and-research-phases-0-and-1"></a>Sessão 2026-10-20: triagem e pesquisa (fases 0 e 1)

Nada nesta sessão tocou uma instalação do jogo. Cada fato abaixo vem de fontes da web
ou metadados públicos do GitHub; nada foi executado contra o jogo.

### <a id="game-identity"></a>Identidade do jogo

| | |
|---|---|
| Título | Middle-earth: Shadow of War (Monolith Productions / WB Games, 2017) |
| Loja | Steam, aplicativo 356190 ([api.steamcmd.net](https://api.steamcmd.net/v1/info/356190)) |
| Build pública | buildid 3095001, última atualização em 2018-09-05 (mesma fonte). Nenhuma atualização desde então. |
| Executável | `<game dir>\x64\ShadowOfWar.exe`, diretório de trabalho `x64\` (configuração de inicialização do Steam, mesma fonte) |
| SHA-256 do executável | `ed0d95cabb033cd66aaa99d699374881846c3cb03ec345f1123d82d45e0bdaef` (117.732.784 bytes; ver sessão 2026-10-20 b) |
| Versão do arquivo | 1.0.8874.0, horário PE 2018-08-24 |
| Motor | Firebird, motor da Monolith derivado do LithTech; Shadow of War é seu primeiro jogo. O site da Monolith o chama de "V7", e o motor de Shadow of Mordor de "V6" ([Wikipedia: LithTech](https://en.wikipedia.org/wiki/LithTech), [blood-wiki](https://blood-wiki.org/index.php/LithTech)) |
| Arquivos de recursos | `.arch06` (apenas sites de extensões de arquivo, não verificado) |
| DRM | Denuvo no lançamento ([guru3d](https://www.guru3d.com/story/middle-earth-shadow-of-war-pc-drm-was-cracked-within-24-hours/)). Build Steam atual: SteamStub confirmado, Denuvo muito provavelmente ainda presente (ver sessão 2026-10-20 b). |
| Outras versões de PC | Microsoft Store / Game Pass existe (conversor de salvamentos de SystematicSkid move salvamentos entre ela e Steam). Tratar como build diferente. |
| SO | Windows 11 (máquina de testes); detalhes da máquina ficam fora do hub |
| Estúdio | Monolith fechou em 2025-02-25 (Wikipedia). Não se esperam novos patches: bom para deslocamentos estáveis. |

### <a id="observations-checked-directly-with-sources"></a>Observações (conferidas diretamente, com fontes)

Repositório e rastreador:
- Este repositório não tinha entrada de Shadow of War ou Shadow of Mordor em `DIRECTORY.md`,
  `data/directory.yaml` ou `games/` (grep, após `git pull` em 2026-10-20). As únicas ocorrências de LithTech
  são F.E.A.R. e NOLF2 (LithTech muito mais antigo, sem utilidade para os mecanismos internos de Firebird).
- Issues/PRs abertos do hub **não** foram conferidos nesta sessão (GitHub CLI ainda não configurada);
  conferidos antes de assumir o jogo (issue de reserva #93).

Multijogador oficial (nenhum em tempo real):
- Sem cooperativo ou tela dividida; recursos online são só assíncronos: Online Vendettas,
  Online Conquest (atacar fortalezas de outros jogadores), Social Conquest
  ([Twinfinite](https://twinfinite.net/?p=305996), tópicos do fórum Steam).
- Patch de julho de 2018 removeu Market, Gold e War Chests; limite de seguidores 80, de capitães 85
  ([PCGamesN](https://pcgamesn.com/middle-earth-shadow-of-war/shadow-of-war-removes-microtransactions-loot-boxes),
  [TrueTrophies](https://www.truetrophies.com/n15548/huge-middleearth-shadow-of-war-patch-removes-microtransactions)).
- Servidores de Shadow of Mordor encerraram em 2021-01-12; os de Shadow of War continuaram ativos na ocasião
  ([Worthplaying](https://worthplaying.com/article/2021/1/16/news/123693)). Usuário Steam de 2024
  diz que online ainda funciona; nenhum aviso oficial de 2025/2026 encontrado. Estado hoje: desconhecido.

Tentativas cooperativas existentes:
- **JustAddMP/ShadowOfWar** ([repositório](https://github.com/JustAddMP/ShadowOfWar)): criado em
  2026-10-17, um commit, só README, "Status: planned. Work hasn't started yet." Parte de
  uma organização GitHub (criada em 2026-10-08) com 26 repositórios de jogos "planejados" e um framework compartilhado,
  [JustAddMP/core](https://github.com/JustAddMP/core) (C++, inicializador, injeção, salas Steam,
  muito ativo: v0.14.0 em 2026-10-20; nenhum arquivo de licença detectado pela API GitHub).
  O único jogo deles com código real vinculado por este hub é MafiaDE. Também tem um
  espaço reservado `JustAddMP/ShadowOfMordor`. **Nada para retomar**, mas alguém pode começar
  logo: vale contatar para evitar trabalho duplicado.
- Nenhum outro mod cooperativo ou multijogador encontrado para Shadow of War ou Shadow of Mordor: busca
  na web (várias formulações), busca de repositórios GitHub por "shadow of war" (primeiros 30
  resultados lidos), Nexus (busca automatizada bloqueada: 403), fóruns Steam pelos resultados de busca,
  2026-10-20. Reddit, ModDB, Discord e buscas em outros idiomas **ainda não** feitos.

Base de modificação (toda por hooks em binário fechado, sem suporte oficial a mods):
- **ReaperAnon/Middle-Earth-Mod-Loader** ([repositório](https://github.com/ReaperAnon/Middle-Earth-Mod-Loader)):
  carregador de DLL C++, faz proxy de `bink2w64.dll` em `x64\` (original renomeado para `bink2w64_.dll`),
  carrega `plugins\*.dll`, API de plugins com menu ImGui (F10) e log (`` ` ``). Usa MinHook.
  Criado em 2023-10, último commit 2026-10-10. Sem arquivo de licença. 23 estrelas, 6 forks.
- **ReaperAnon/Shadow-Of-War-Mods** ([repositório](https://github.com/ReaperAnon/Shadow-Of-War-Mods)):
  14 plugins nesse carregador (trapaças, árvore de habilidades, raridade de criação de orcs, informações de Uruk, FOV).
  Último commit 2024-01-05. Sem licença. Prova que funções de jogabilidade já foram encontradas e interceptadas.
- **survivalizeed/ShadowOfWarPacketLoader** ([repositório](https://github.com/survivalizeed/ShadowOfWarPacketLoader)):
  carregador de recursos ("hook_loading_routines", "designed_strings"), último commit 2025-01-28,
  sem licença. O mod de sobreposição Nexus abaixo precisa de "Survivalzeed's DLL mod loader".
- **survivalizeed/ShadowOfWarFPS** (MIT, 2024-12): hook de FOV/primeira pessoa.
- **SystematicSkid** (mesmo autor, vários repositórios):
  - [shadow-of-war-save-editor](https://github.com/SystematicSkid/shadow-of-war-save-editor):
    "legacy tools for debugging shadow of war systems", originalmente para fazer engenharia reversa do formato
    de salvamento; README diz que ajudou a comunidade a entender o sistema Nemesis. 2024-01, sem licença.
  - [shadow-of-war-save-converter](https://github.com/SystematicSkid/shadow-of-war-save-converter):
    Python, MIT, 2024-11; salvamentos Game Pass <-> Steam.
  - [shadow-of-war-server](https://github.com/SystematicSkid/shadow-of-war-server):
    reconstrução do backend online, 2025-03. Servidor Rust "Nemesis" (Actix), depurador C++
    que intercepta WinAPI para extrair requisições, tipos de valor "Hydra", "AG Binary protocol". Sem licença.
  - [sow-freecam](https://github.com/SystematicSkid/sow-freecam): 2025-06, mostra uma
    classe `sow::GameClient` com `CameraOwner*` no deslocamento 0x898.
- **Mod Nexus 218**, de GENETICZZ2K (pelo texto dos resultados de busca, página em si 403): sobreposição com
  edição de Uruk/capitães, criação de NPCs, modo de voo. Criar NPCs e editar capitães em
  execução é exatamente o que um cliente cooperativo precisa para espelhar o anfitrião.
- **Tabela Cheat Engine**, de reverser69, v1.1, agosto de 2024 ([GamePressure](https://www.gamepressure.com/download/middle-earth-shadow-of-war-cheat-table-v11-mod/z914e87)).
- Usuários Steam relatam que edições de capitães por tabelas podem quebrar o comportamento de orcs, fazer o jogo
  falhar ou corromper salvamentos ([tópico Steam](https://steamcommunity.com/app/356190/discussions/0/1734342793779694605)).
- Outros jogos em Firebird: nenhum conhecido. Shadow of Mordor usa o motor anterior (V6).

### <a id="derived-reasoned-from-the-above-not-run"></a>Derivado (raciocinado a partir do acima, não executado)

- **Caminho: construir do zero.** Nada jogável existe para retomar. O repositório JustAddMP é um
  espaço reservado; o trabalho anterior útil é o ecossistema de hooks (carregador de mods, plugins, pesquisa de salvamentos
  e backend), não um mod cooperativo.
- **Modelo: autoridade do anfitrião com sincronização de estado.** O jogo não tem replicação em tempo real para
  aproveitar (o backend online é requisição/resposta no estilo HTTP com o backend Hydra,
  não tráfego de jogabilidade entre pares). O anfitrião executa a simulação real e o mundo
  Nemesis; o cliente executa cópia espelhada na qual suas próprias decisões de Nemesis/IA são
  suprimidas e atores remotos são bonecos.
- **Ponto de injeção resolvido:** o carregador proxy `bink2w64.dll` funciona na build
  Steam, então podemos distribuir a camada cooperativa como plugin ou proxy próprio. Só hooks, sem
  arquivos do jogo distribuídos: atende às regras do hub.
- **Build congelada é uma vantagem:** uma build Steam desde 2018-09, estúdio fechado, então
  deslocamentos encontrados pelos mods existentes devem continuar válidos. Fixar buildid 3095001 + hash do executável.
- **Candidatos a reutilização (se a licença permitir):** JustAddMP/core (salas/transporte Steam),
  ferramentas de sincronização do próprio hub (`tools/`, skill coop-sync-testing), carregador de ReaperAnon para
  menus/logs. Nenhum repositório SoW tem licença exceto o mod FPS e o conversor de salvamentos
  (MIT), então podemos aprender com eles, mas devemos pedir aos autores antes de copiar código.

### <a id="biggest-technical-risks-ranked-my-judgement"></a>Maiores riscos técnicos (ordenados, meu julgamento)

1. **O sistema Nemesis é o estado do mundo.** Capitães, patentes, características, memórias,
   promoções, traições e eventos de "tempo passa" são gerados por RNG e ocorrem fora da tela
   (especialmente na morte do jogador). Dois clientes divergem instantaneamente a menos que a simulação
   Nemesis do cliente seja inteiramente desativada e todo evento Nemesis seja reproduzido do anfitrião.
   Ainda não sabemos onde o estado Nemesis vive na memória ou quais funções o alteram
   (o editor de salvamentos de SystematicSkid é a melhor pista). Também em aberto no projeto: o que ocorre quando
   o *cliente* morre (evento Nemesis no anfitrião ou nenhum evento).
2. **Compatibilidade de salvamentos.** O salvamento do anfitrião é o único mundo canônico. O cliente nunca deve
   gravar o próprio salvamento conectado (ou só em posição separada), senão
   sobrescreveria seu mundo Nemesis de um jogador por um espelhado, parcialmente controlado por bonecos. Sabe-se que
   edições de capitães por memória corrompem salvamentos (relatos Steam). Mitigação: copiar
   salvamentos antes de cada sessão, bloquear salvamento automático do cliente, calcular hash do salvamento do anfitrião antes/depois
   das sessões em testes. Salvamentos Steam e Game Pass diferem (existe conversor).
3. **Nenhum segundo personagem de jogador.** O jogo tem um protagonista (Talion, mais Eltariel
   no DLC Blade of Galadriel). O jogador remoto precisa de um peão humanoide criado
   e conduzido por entrada de rede, com combate, habilidades espectrais e dominação. Criar NPCs
   funciona (mod Nexus 218), mas fazer um se comportar como o jogador é terreno desconhecido.
4. **Efeitos globais de tempo.** Mirar com arco desacelera o tempo; execuções/câmeras de morte, Elven Rage e
   cinemáticas provavelmente mudam uma escala de tempo ou câmera global. No cooperativo, a câmera lenta de um
   jogador não deve desacelerar o mundo do outro. Desconhecido como o motor implementa isso.
5. **Escala das batalhas.** Cercos de fortalezas executam centenas de IAs. Sincronização de estado completo pode não caber;
   podemos precisar de eventos sob autoridade do anfitrião mais IA de multidões no cliente.
6. **Missões de história e cenas.** Missões roteirizadas, cinemáticas e teleportes para áreas
   de missão devem depender do anfitrião e levar o cliente junto. Se o jogo
   tem VM de scripts (e onde vive a lógica de missão) é desconhecido.
7. **Serviços online e jogo justo.** O jogo conversa com o backend da WB para Online
   Conquest/Vendettas. Uma sessão cooperativa modificada deve rodar com recursos online desativados para nunca
   enviar estado modificado aos mundos de outros jogadores (regra 10 do hub).
8. **Denuvo (se ainda presente).** Hooks já funcionam nos mods existentes, então provavelmente
   não é bloqueio, mas qualquer proteção contra adulteração deve ser deixada intacta, sem contorno.

### <a id="guesses-unverified-check-before-relying-on-them"></a>Suposições (não verificadas, conferir antes de usar)

- Denuvo pode ter sido removido da build Steam em algum momento (uma afirmação de fórum de 2024).
- O motor Firebird ainda pode conter código de rede cliente/servidor da época LithTech de
  F.E.A.R. 3 ou Guardians of Middle-earth; nesse caso, poderia ser uma base de replicação. Nenhuma
  fonte encontrada em qualquer direção.
- O segundo jogador poderia reutilizar o rig de Eltariel (DLC) ou Celebrimbor.

### <a id="unknowns-to-resolve-in-phase-23"></a>Em aberto (resolver na fase 2/3)

- SHA-256 do executável, versão do arquivo, presença de Denuvo (precisa de instalação copiada).
- Se o hub tem issues/PRs abertos para este jogo (ainda não conferido).
- Onde vive o estado Nemesis, como salvamentos são serializados, se existe camada de script.
- Se os servidores online de Shadow of War ainda funcionam em 2026.
- Situação de licença de cada repositório de mods SoW exceto os dois MIT.
- Se JustAddMP pretende começar SoW em breve.

### <a id="not-searched-yet"></a>Ainda não pesquisado

Reddit (r/shadowofwar, r/ShadowOfMordor), ModDB, Discord de modificação de Shadow of War,
páginas Nexus diretamente (403 na busca automatizada), buscas em russo/alemão/polonês,
Archive.org, guias Steam.

### <a id="next-steps"></a>Próximos passos

1. Copiar a instalação Steam para pasta de teste; registrar hash, versão e presença de Denuvo
   do executável aqui.
2. Fase 3: compilar o carregador de mods + plugin de logs na cópia de teste; ler
   fontes do editor de salvamentos e freecam de SystematicSkid para layouts de classes; mapear as estruturas
   Nemesis e o caminho de salvamento.

## <a id="session-2026-10-20-b-workspace-phase-2-and-exe-identity"></a>Sessão 2026-10-20 b: espaço de trabalho (fase 2) e identidade do executável

### <a id="observations-checked-directly"></a>Observações (conferidas diretamente)

- Instalação Steam: buildid 3095001 (`buildid` e `TargetBuildID` do appmanifest),
  901 arquivos, 117.711.336.590 bytes. Copiada em modo somente leitura com robocopy para uma pasta
  isolada de testes (`<workspace>\local\test-installs\sow-a`, ignorada pelo Git): 901 arquivos, mesmo total
  de bytes, 0 falhas. A instalação Steam foi apenas lida.
- `x64\` contém `ShadowOfWar.exe`, `bink2w64.dll` (alvo proxy do carregador de mods),
  `steam_api64.dll`, `oo2core_5_win64.dll` (Oodle), `amd_ags_x64.dll`, `AnselSDK64.dll`.
- `ShadowOfWar.exe`: 117.732.784 bytes, SHA-256
  `ed0d95cabb033cd66aaa99d699374881846c3cb03ec345f1123d82d45e0bdaef`, FileVersion
  1.0.8874.0, x64, horário PE 1535072130 (2018-08-24, compatível com a atualização Steam de 2018-09-05).
- Layout PE (análise Python do arquivo em modo somente leitura, nada executado): 17 seções. Ponto de
  entrada em `.bind`, a seção SteamStub (invólucro de DRM Steam). `.text` tem 20
  bytes; código fica em seções de nomes estranhos: `.arch` 30,9 MB, `.xtext` 8,5 MB,
  seção de leitura/gravação/execução chamada `.bss` + byte lixo, 73,5 MB com entropia 7,09,
  `.srdata` 1,2 MB com entropia 7,83. Sem strings "denuvo", "vmprotect" ou "themida".

### <a id="derived"></a>Derivado

- SteamStub presente: iniciar a cópia fora do Steam precisa de `steam_appid.txt` e
  variáveis de ambiente `SteamAppId`/`SteamGameId` (ver playbook/methods.md), com Steam em execução.
- Denuvo muito provavelmente ainda está nesta build: executável de 117 MB, `.text` quase vazio e
  seção RWX de alta entropia de 73 MB são o layout usual de Denuvo, e nenhuma atualização posterior o removeu
  até onde a pesquisa encontrou. Não comprovado: sem marcador de string, e não executamos nada
  para conferir. Consequências:
  - Análise estática (Ghidra) do arquivo em disco verá código empacotado/ofuscado;
    código legível só existe após o jogo desempacotar a si próprio em execução. Os mods existentes
    (proxy bink2w64 + MinHook, padrões ou deslocamentos) funcionam em execução, então hooks são
    viáveis sem tocar na proteção.
  - Regra 10 do hub / nossa regra: não contornar, remover ou modificar Denuvo ou SteamStub. Interceptar funções
    do jogo por nossa própria DLL apenas dentro de nosso próprio processo.
  - Em aberto: se Denuvo limita várias cópias simultâneas do jogo em um PC (necessário para testes
    com duas instâncias) ou conta ativações por pasta. Testar com a cópia B depois.

### <a id="unknowns"></a>Em aberto

- Locais de salvamento e configurações (necessários antes da primeira inicialização da cópia, para ela
  não usar os salvamentos reais).
- Se o jogo executa duas instâncias em um PC (mutex/verificações de janela, Denuvo, Steam).

### <a id="next-steps-1"></a>Próximos passos

1. Encontrar onde vivem salvamentos e configurações (Steam Cloud? `%USERPROFILE%\Documents\WB Games\...`?)
   pela documentação e strings de arquivos, e planejar o redirecionamento da cópia de teste antes de iniciá-la.
2. Compilar carregador de mods de ReaperAnon + plugin de logs apenas para a cópia de teste.
## <a id="session-2026-10-20-c-where-saves-and-settings-live-isolation-plan"></a>Sessão 2026-10-20 c: onde ficam salvamentos e configurações, plano de isolamento

### <a id="observations-read-only-listing-of-the-real-save-and-steam-folders-names-and-sizes-only"></a>Observações (listagem somente leitura das pastas reais de salvamento e Steam, apenas nomes e tamanhos)

- `%LOCALAPPDATA%\WB Games\Shadow of War\` contém tudo local:
  - salvamentos: `<8 hex>_ShadowOfWar.sav` mais `<8 hex>_1..5_ShadowOfWar.sav`, ~2,3 MB cada
    (prefixo de 8 hexadecimais é por conta, derivação desconhecida);
  - `render.cfg`: pares `"Key" "float"` em texto simples (resolução, `Windowed`, predefinições de qualidade);
  - `gpu.nfo`;
  - `CloudStorage\`: cache de conteúdo online WB (arquivos `socialcmt*`, `freetrial*`, `mktg-*`),
    ou seja, o jogo baixa dados de eventos/marketing dos servidores WB.
- Steam Cloud: `Steam\userdata\<steam id>\356190\remote\<8 hex>_ShadowOfWar.sav`, mesmo
  tamanho do salvamento local principal. Corresponde a relatos de jogadores de que Steam Cloud restaura salvamentos
  excluídos localmente ([tópico Steam](https://steamcommunity.com/app/356190/discussions/0/4699035289200469903)).
- Builds antigas salvavam em `Documents\WB Games\Shadow of War`
  ([Microsoft Q&A](https://learn.microsoft.com/en-us/answers/questions/5614199/not-saving-data-or-save-files-for-middle-earth-sha));
  essa pasta não existe na máquina de testes.
- Nenhuma chave `WB Games` no Registro em HKCU, HKLM ou WOW6432Node.
- Importações do executável (análise somente leitura; Denuvo deixa tabela estática pequena, a maioria das APIs é
  resolvida em execução): `shell32!SHGetKnownFolderPath` estaticamente. Strings no executável:
  `SHGetFolderPathW`, `getenv`, `\WB Games\`, `\USER\render.cfg`, `render.cfg`,
  `ShadowOfWar.sav`, `STEAMREMOTESTORAGE_INTERFACE_VERSION014`, `CreateMutexA/W`,
  `CreateMutex failed`, UTF-16 `SOFTWARE\WB Games\Kraken\1.00.0000`. Importa `winhttp`
  e `wininet` (serviços online).
- Página PCGamingWiki: 403 na busca automatizada, não lida.

### <a id="derived-1"></a>Derivado

- Salvamentos chegam ao disco de duas formas: arquivos simples sob a pasta conhecida LocalAppData, e
  Steam Cloud por `ISteamRemoteStorage` (v014). Redirecionar só a pasta ainda
  permitiria que a cópia de teste sobrescrevesse o salvamento real na nuvem, que Steam depois traz
  de volta à instalação real.
- `SetEnvironmentVariable LOCALAPPDATA` não redireciona `SHGetKnownFolderPath`
  (lê o perfil do usuário, não o ambiente). O redirecionamento precisa ocorrer dentro
  do processo, pela nossa DLL.
- `CreateMutex failed` sugere mutex de instância única (importa nos testes de duas cópias).
- `\USER\render.cfg` pode ser caminho alternativo (portátil?) de configuração. Desconhecido.

### <a id="isolation-plan-nothing-launched-until-every-step-passes"></a>Plano de isolamento (nada iniciado até cada etapa passar)

1. **Backup com manifesto de hashes** de `%LOCALAPPDATA%\WB Games\Shadow of War` e
   `userdata\<id>\356190` em pasta privada de backup (ler das pastas reais,
   gravar apenas no espaço de trabalho).
2. **Etapa manual no cliente Steam:** desligar Steam Cloud para Shadow of War
   (Propriedades do jogo > Geral) durante os testes. Proteção redundante com a etapa 3.
3. **Nunca iniciar a cópia original sem modificação.** Primeira inicialização só com nosso proxy
   `bink2w64.dll` em `x64\` da cópia (original renomeado para `bink2w64_.dll`, mesmo truque
   do carregador de ReaperAnon). Apenas dentro do processo do jogo, ele:
   - intercepta `SHGetKnownFolderPath` / `SHGetFolderPathW` para LocalAppData (e Documents)
     resolverem para `local\test-installs\sow-a-profile\` neste processo;
   - torna gravações e exclusões de `ISteamRemoteStorage` operações sem efeito (registradas) e informa nuvem
     desativada, para nada alcançar a posição real da nuvem;
   - bloqueia conexões `winhttp`/`wininet` (modo offline; nenhum estado modificado enviado aos servidores
     WB, regra 10 do hub);
   - registra cada arquivo aberto para gravação fora da cópia e da pasta de seu perfil, e
     **encerra o jogo** se um mirar a pasta real de salvamentos ou userdata do Steam
     (falha bloqueando);
   - grava seu próprio log em `local\test-installs\sow-a-profile\coop-log.txt`.
4. **Preparar o perfil isolado** com `render.cfg` em modo janela, 1280x720, predefinição
   baixa, e sem salvamento (novo jogo), ou cópia de um salvamento real se necessário depois.
5. **Iniciar pela cópia**, não pela biblioteca Steam: `steam_appid.txt` (356190)
   junto ao executável, variáveis `SteamAppId`/`SteamGameId`, Steam em execução. Encerrar apenas
   processos cujo caminho esteja dentro de `local\test-installs\`.
6. **Após cada execução:** recalcular hashes das pastas reais contra o manifesto (verificação do
   backup); qualquer diferença = parar e informar. Também conferir que o `x64\` real está intacto.
7. Antes de construir a etapa 3, testar primeiro a DLL de redirecionamento em alvo inofensivo, se
   possível; desconhecido se SteamStub/Denuvo toleram o proxy antes de o carregador de ReaperAnon
   comprová-lo nesta build (documentado como funcional na versão Steam).

### <a id="open-questions"></a>Questões em aberto

- O jogo também lê `getenv("LOCALAPPDATA")` ou `USERPROFILE` em algum lugar? O registro de
  hooks na primeira execução mostrará.
- Onde ficam configurações de controles/áudio/jogabilidade (não em `render.cfg`; talvez no salvamento).
- A camada online WB precisa responder para o jogo chegar ao menu principal offline?

## <a id="session-2026-10-20-d-isolation-steps-1-and-2-done"></a>Sessão 2026-10-20 d: etapas 1 e 2 do isolamento concluídas

- Etapa 1 (backup): `%LOCALAPPDATA%\WB Games\Shadow of War` (28 arquivos) e
  `userdata\<id>\356190` (2 arquivos) copiados para pasta privada de backup, com
  `MANIFEST.sha256` (SHA-256, tamanho, caminho). Cada arquivo de backup teve seu hash comparado ao
  original: 30 arquivos, 0 divergências.
- Observação: salvamento principal, posição 1 e salvamento Steam Cloud têm o mesmo SHA-256,
  então o `.sav` sem número parece ser a posição atual/última usada espelhada na nuvem.
- Etapa 2 (Steam Cloud desligado): feita no cliente Steam. Conferido em somente leitura: o
  `userdata\<id>\7\remote\sharedconfig.vdf` do Steam tem `"356190" { "cloudenabled" "0" }`.
- Próximo: etapa 3, DLL de redirecionamento/proteção. Nada iniciado ainda.

## <a id="session-2026-10-20-e-guard-dll-built-and-tested-offline-isolation-step-3"></a>Sessão 2026-10-20 e: DLL de proteção compilada e testada offline (etapa 3 do isolamento)

O código da proteção e seus testes offline não estão publicados; este hub recebe só o relato,
então resultados de teste são descritos, não reivindicados.

### <a id="built"></a>Construído

- `sowguard`, proxy `bink2w64.dll`: 73 exportações encaminhadas ao original renomeado
  `bink2w64_.dll` (mesmos nomes e ordinais, por pragmas de vinculador `/export:Name=bink2w64_.Name`;
  um arquivo `.def` com linhas `Name=bink2w64_.Name` falhou na vinculação aqui com
  LNK2001 em cada exportação). MSVC 14.44, `/W4 /WX`, CRT estática.
- Intercepta seis funções ntdll dentro do processo: `NtCreateFile`, `NtOpenFile`,
  `NtQueryAttributesFile`, `NtQueryFullAttributesFile`, `NtSetInformationFile`
  (destinos de renomeação/link), `NtDeleteFile`. Observação na máquina de testes (Windows 11 26200):
  todas as seis são stubs simples de syscall de 24 bytes
  (`4C 8B D1 B8 <id> F6 04 25 08 03 FE 7F 01 75 03 0F 05 C3 CD 2E C3`), então copiar bytes é
  um trampolim funcional; sem biblioteca de hooks ou download necessário. Qualquer outro layout encerra
  o jogo (saída `0xC0DE0005`) em vez de supor.
- Redireciona `%LOCALAPPDATA%\WB Games`, `Documents\WB Games` e
  `Steam\userdata\<any id>\356190` para perfil isolado; protege esses caminhos e a instalação
  real (gravação = encerrar, `0xC0DE0010`); registra gravações em outros locais de userdata Steam;
  nega `\Device\Afd` (sockets) quando `block_network=1`.
- Recusas na inicialização: executável fora de `allowed_root` ou dentro da pasta Steam
  (`0xC0DE0002`), executável não tendo tamanho 117.732.784 + SHA-256 registrado (`0xC0DE0003`),
  `steam_appid.txt` não sendo `356190` (`0xC0DE0004`); define `SteamAppId`/`SteamGameId`.
  Caminhos reais vêm do ambiente e Registro em execução, nunca fixados no código.

### <a id="tested-offline-no-game-process"></a>Testado (offline, sem processo do jogo)

- Testes offline: cada caso monta uma árvore fictícia de usuário, carrega a DLL em processo filho em modo teste
  (caminhos reais do usuário recusados) e confere estado em disco + código de saída. Cobre: redirecionamento de
  gravação/leitura/atributos/listagem; barras normais, minúsculas, `\?\`, `NtCreateFile` relativo ao diretório atual e
  ao handle de diretório; renomeação/exclusão/mkdir no perfil; redirecionamento de userdata
  Steam; leitura da instalação permitida; gravação, exclusão, criação e renomeação para dentro da instalação
  encerram com `0xC0DE0010` e deixam a árvore intacta; sockets
  negados/permitidos por opção; quatro recusas de inicialização; todos os 73 encaminhadores resolvem ao
  original; SHA-256 próprio corresponde ao hash do executável acima.
- Um caso falhou inicialmente: teste de encaminhadores buscava `bink2w64_.dll` antes de resolver qualquer
  exportação. Encaminhadores carregam o alvo na primeira resolução (no jogo, a importação
  estática `BinkGoto` do executável faz isso). Corrigido o teste, não a DLL.
- Uma build de controle negativo (redirecionamento e proteção removidos na compilação) falha nos casos dependentes.
- Ensaio da configuração preparada em modo jogo dentro da cópia de teste com executável que não era do jogo: a
  DLL analisou a configuração e recusou com `0xC0DE0003 unknown exe`.
- Salvamentos reais e userdata Steam conferidos novamente contra o manifesto de backup após tudo
  isso: intactos.

### <a id="observed-in-passing"></a>Observado de passagem

- A instalação real tem `x64\steam_appid.txt` (`356190`), criado às 13:59 de
  2026-10-20, cerca de um minuto antes da última gravação de `remotecache.vdf` do jogo pelo Steam,
  e antes de esta sessão olhar a instalação pela primeira vez. Provavelmente o próprio jogo
  o grava ao iniciar (suposição, não confirmada). A cópia de teste o herdou.

### <a id="staged-not-launched"></a>Preparado (não iniciado)

- `x64\` da cópia A: proteção como `bink2w64.dll`, original como `bink2w64_.dll` (hash conferido
  igual ao da instalação real), `sowguard.ini` (modo jogo, `block_network=1`, pasta de backups
  também protegida). `render.cfg` do perfil isolado: `Windowed 1`, 1280x720, qualidades 0,
  limite de 60 fps (significados dos valores parcialmente supostos).
- Script inicializador escrito, não executado: verifica backup, confere Steam em execução e
  nenhum jogo em execução; inicia diretamente o executável da cópia; encerra só processos de cópias de teste ao
  atingir tempo limite; imprime código de saída, log da proteção e verificação do backup.

### <a id="unknown-until-the-first-launch"></a>Desconhecido até a primeira inicialização

- Se Denuvo/SteamStub aceitam hooks ntdll feitos antes do ponto de entrada do jogo.
- Se SteamStub reinicia pelo Steam apesar de `steam_appid.txt`. Nesse caso,
  Steam iniciaria a instalação real sem proteção: observar isso na saída do
  inicializador (script lista todo ShadowOfWar.exe ainda vivo).
- Se o jogo chega ao menu principal com sockets negados e se precisa dos
  servidores WB.

## <a id="session-2026-10-20-f-first-guarded-launch-of-the-test-copy"></a>Sessão 2026-10-20 f: primeira inicialização protegida da cópia de teste

Iniciado (Steam em execução, verificação de backup passou primeiro), tempo limite 300 s.

### <a id="observations"></a>Observações

- Só um processo do jogo, da cópia de teste; nada iniciado da instalação real
  (conferido aos 2 s e no fim). SteamStub **não** reiniciou pelo Steam.
- Proteção aceitou o executável (tamanho + SHA-256), instalou todos os seis hooks ntdll antes do ponto
  de entrada do jogo, e ele executou com eles: Denuvo/SteamStub toleraram os hooks nesta execução.
- Jogo encerrou sozinho com código 0 após 139 s. Sem despejo de falha, sem relatório WER. Por que
  encerrou é desconhecido (ninguém observou a janela; possivelmente a negação de rede).
- Log da proteção, 71 linhas: 20 tentativas de socket negadas (`\Device\Afd\Endpoint`), 32 redirecionamentos,
  0 ocorrências em caminhos protegidos, 0 gravações monitoradas, nenhum FATAL.
- Ordem observada: sockets negados e userdata Steam `<id>\356190\<id>` sondado nos
  primeiros ~1,4 s; depois intervalo de ~68 s sem registros; então inicialização do próprio jogo: sondagens em
  `LocalAppData\WB Games\Shadow of War\` e `Documents\WB Games\Shadow of War\`,
  criação de arquivo `{25FFEBFB-B407-4789-ABEB-43655FEB78C6}` (teste de gravação?), abertura de
  `render.lasterror`, criação de `CloudStorage\`, leitura e regravação de `render.cfg` várias
  vezes, gravação de `gpu.nfo`, gravação em userdata Steam `356190\<id>` (1.178 bytes). Tudo
  foi para o perfil isolado.
- Jogo abriu janela: salvou `WindowWidth 960`, `WindowHeight 516`,
  `ScreenX 480`, `ScreenY 258` no `render.cfg` isolado.
- **Verificação do backup falhou em um arquivo:** o `render.cfg` real foi regravado às
  17:14:04.53, 3 s após iniciar, em formato que o jogo não usa (`"1080"` em vez de
  `"1080.000000"`, linha vazia final), com `Windowed 0` (era 2, sem bordas),
  `TextureQuality 3` (era 2). Salvamentos, gpu.nfo e userdata Steam intactos.
- Causa: o **NVIDIA App** (processo separado). Seu backend atualizou
  `NvBackend\Recommendations\middle_earth_shadow_of_war\*` às 17:14:03.42-04.08 e
  `ApplicationState\928249434.json` às 17:14:04.65. Seu `current_game.lua` para este jogo
  tem `GetConfigFilePath`, `ScreenWidth16by9`, `Render.Setting.TextureQuality` e os
  valores de Display Mode (tela cheia 0, janela 1, sem bordas 2); seu JSON de estado registra
  "Full-screen" e "1920x1080". Grava no caminho LocalAppData real sempre que vê o
  jogo iniciar, de fora do processo do jogo, então a proteção não pode vê-lo nem pará-lo.

### <a id="derived-2"></a>Derivado

- Proteção dentro do processo funciona como projetado no jogo real; a lacuna são outros processos
  que reagem ao início do jogo. "Otimizar" (ou aplicar automaticamente) do NVIDIA App é um; outros
  podem existir em outros PCs (AMD Adrenalin, sobreposições). Adicionar ao playbook como armadilha de QA
  para qualquer configuração de "cópia de teste isolada".
- Pausa de ~68 s provavelmente é Steam/Denuvo ou código online WB atingindo tempo limite nos sockets
  negados (suposição; não verificada).

### <a id="next"></a>Próximo passo

- Opções: restaurar `render.cfg` do backup; impedir que NVIDIA App otimize
  Shadow of War (ou fechá-lo) antes de inicializações de teste.
- Script inicializador: também capturar a pasta de recomendações do NVIDIA App e nomear quem gravou
  quando a verificação de backup falhar; observar a janela para entender por que o jogo sai após ~139 s.

### <a id="seen-on-screen-during-the-same-launch-added-after-the-run"></a>Visto na tela na mesma execução (adicionado depois)

- Com sockets negados, o jogo mostrou diálogo de erro/relatório de bug por não alcançar o
  servidor WB. Passar dele exigiu colar o texto do relatório no site de suporte WB.
  Isso explica o intervalo de ~68 s no log da proteção. O jogo foi depois fechado manualmente no
  menu principal, explicando saída limpa 0 aos 139 s.
- O menu parecia reconhecer dados de salvamento existentes.

### <a id="checked-against-that"></a>Conferido contra isso

- O log da proteção não tem acesso a caminho `.sav` algum (leitura pela pasta real de salvamentos
  seria redirecionada e registrada), e o perfil isolado não tem arquivos `.sav`.
  Os seis salvamentos reais e userdata Steam são idênticos byte a byte ao backup. Portanto, o jogo
  não abriu os arquivos de salvamento neste processo. Desconhecido o que o menu mostrou e de onde
  veio (estatísticas ou conquistas Steam por IPC do Steam são uma suposição).
- `steam-userdata\356190\<id>` é um blob de texto hexadecimal (1.178 bytes) que difere da cópia
  real em 1.061 bytes: regenerado, não copiado. Não é salvamento.

### <a id="consequences"></a>Consequências

- Negar criação de sockets parece um bug ao jogo, não estar offline. Toda
  inicialização pararia nesse diálogo, descartando testes de bot sem supervisão, e
  convidaria relatórios à WB sobre execuções modificadas. Próxima versão da proteção: permitir sockets, falhar conexões
  de saída e DNS como um PC offline, e ver se o jogo inicia
  offline sem diálogo. Desconhecido se precisa do servidor WB para iniciar.
- Ainda em aberto: se Steam atende leituras/gravações de arquivos de `ISteamRemoteStorage` dentro
  do processo do jogo (onde a proteção os redireciona; a gravação de `<id>` no processo
  sugere que sim) ou em `steam.exe` (onde não pode).
- Decidido: manter `render.cfg` regravado pelo NVIDIA (configurações de exibição são corrigidas no
  jogo). A verificação de backup agora informa mudanças de `render.cfg` e `gpu.nfo` só como informação;
  qualquer mudança em salvamentos ou userdata Steam ainda falha e bloqueia inicialização.

## <a id="session-2026-10-20-g-offline-style-network-block-guard-v2"></a>Sessão 2026-10-20 g: bloqueio de rede no estilo offline (proteção v2)

Motivo: negar criação de sockets (v1) fazia o jogo mostrar diálogo de relatório de bug "não alcança servidor"
que precisava de pessoa. Objetivo: parecer um PC desconectado.

### <a id="observations-measured-on-the-test-machine-windows-11-26200"></a>Observações (medidas na máquina de testes, Windows 11 26200)

- Sonda (`test_guard.exe probe`, proteção com `net_trace=1`, `network=allow`) rastreou as requisições
  AFD por trás de cada chamada Winsock; só endereços de documentação não roteáveis
  (192.0.2.1, 2001:db8::1) e loopback:
  - `0x12007` connect (TCP e UDP connect): sockaddr no deslocamento 24 (comprimento 40 para IPv4,
    52 para IPv6);
  - `0x120C7` ConnectEx: cabeçalho TDI de 1 entrada, sockaddr no deslocamento 10 (comprimento 26 / 38);
  - `0x12023` UDP sendto: ponteiro para sockaddr no deslocamento 96, comprimento em 88 (len 104);
  - UDP `connect`+`send`: endereço só no connect, o send é `0x1201F`.
  - `NtDeviceIoControlFile` é stub simples de syscall como as seis funções de arquivo.
- Proteção v2 o intercepta: com `network=offline`, essas três requisições para destino não loopback (ou
  impossível de analisar) retornam `STATUS_NETWORK_UNREACHABLE` sem chegar ao
  driver. Winsock então informa `WSAENETUNREACH` (10051); WinHTTP informa
  `ERROR_WINHTTP_CANNOT_CONNECT` (12029) após 0 ms. Loopback passa.
- Novo caso offline `network_offline`: sockets
  criam; TCP connect, ConnectEx, UDP sendto, UDP connect+send para 192.0.2.1 e TCP,
  ConnectEx, sendto para 2001:db8::1 dão todos 10051; WinHTTP para 192.0.2.1 dá 12029 em
  menos de 2 s; TCP e ConnectEx para servidor em 127.0.0.1, TCP para servidor em ::1 e datagrama UDP
  por 127.0.0.1 funcionam.
- Uma falha falsa no caminho: após colocar a proteção na cópia de teste,
  `sow-a\x64\bink2w64.dll` *é* a proteção, e passá-la como "original" fez o
  proxy encaminhar para segunda cópia de si mesmo. Essa cópia encontrou os stubs já interceptados
  e saiu com `0xC0DE0005` (falha bloqueando), mas não pôde registrar porque a primeira cópia mantém
  o arquivo de log. Corrigida a entrada do teste (`bink2w64_.dll`), e o aparato de testes passou a recusar uma
  build sowguard como original. Lição para o playbook: proxy carregado duas vezes falha
  silenciosamente se seu log é aberto sem compartilhamento de gravação.

### <a id="derived--unknown"></a>Derivado / em aberto

- DNS ainda resolve (serviço DNS Client faz isso fora do processo do jogo), então o
  jogo vê "nome resolve, conexão falha", como um PC cuja rede cai após DNS
  ou um firewall. Desconhecido se ainda mostra o diálogo nesse caso. Se
  mostrar, próxima tentativa: também falhar resolução de nomes.
- Preparado na cópia A com `network=offline`; ensaio com executável que não era do jogo recusado
  (`0xC0DE0003`); verificação de backup intacta (render.cfg só informação). Não iniciado.

## <a id="session-2026-10-20-h-second-guarded-launch-guard-v2-networkoffline"></a>Sessão 2026-10-20 h: segunda inicialização protegida (proteção v2, network=offline)

Janela do NVIDIA App fechada antes de iniciar; serviços `nvcontainer` e processos `NVIDIA
Overlay` continuavam em execução. A janela do jogo foi observada manualmente.

### <a id="observations-1"></a>Observações

- Um processo do jogo, da cópia de teste. Todos os sete hooks instalados; jogo executou 67 s,
  saída 0 (fechado manualmente no menu principal, ver abaixo).
- Log da proteção, 48 linhas: 24 redirecionamentos, 4 recusas offline, 0 ocorrências protegidas, 0 gravações
  monitoradas, nenhuma requisição de rede não analisada, nenhum FATAL.
- Cronologia: +0,7 s userdata Steam `356190\<id>` aberto (leitura, redirecionada); +3,5 s
  início do próprio jogo (sondagens no diretório de salvamentos, arquivo de teste de gravação, `render.lasterror`,
  `CloudStorage\`); +3,8-8,3 s leitura/gravação de `render.cfg`, leitura de `gpu.nfo`; +46,5 s
  `render.cfg` gravado novamente; **+46,7 s duas conexões HTTPS recusadas, para
  3.213.33.214:443 e 184.193.6.155:443, ambas por ConnectEx; repetidas uma vez em +61,9 s,
  recusadas novamente.** Nenhuma outra tentativa de saída.
- Comparado à v1: sem parada de 68 s antes da inicialização do próprio jogo (v1: +1,4 s -> +69 s com
  sockets negados; v2: início em +3,5 s). Na v1, criações precoces de sockets em +0,5-1,4 s
  foram negadas; na v2, permitidas, e nenhuma conectou a destino remoto.
- O `render.cfg` real **não** foi regravado desta vez (mesmo hash, ainda 17:14:04).
  O backend NVIDIA gravou só `ApplicationStorage.json` (17:49:53, na saída do jogo) e
  não atualizou as recomendações Shadow of War. Desconhecido se foi porque
  a janela do App foi fechada ou porque já tinha aplicado suas configurações às 17:14.
- Verificação do backup: intacto (render.cfg só informação).

### <a id="derived-3"></a>Derivado

- Chamadas online ocorrem tarde (cerca de 43 s após iniciar), provavelmente quando o menu principal ou
  seus recursos online carregam; dois hosts, HTTPS, uma repetição 15 s depois. 3.213.33.214 está em
  faixa Amazon AWS (3.0.0.0/8); quem opera o segundo host é desconhecido. Nomes de host
  desconhecidos (DNS ocorre fora do processo; não pesquisados para evitar mais tráfego).
- Visto na tela: **nenhum diálogo de erro**; o jogo chegou ao menu principal e foi fechado
  dali manualmente (saída aos 67 s). Portanto, "conexões falham como em PC desconectado" basta para o
  jogo iniciar e chegar ao menu offline; não é necessário falhar DNS. As duas tentativas HTTPS
  em +46,7 s e +61,9 s ocorrem enquanto o menu principal está aberto e são abandonadas
  silenciosamente.
- Isolamento da fase 2 concluído: cópia A inicia sem supervisão até o menu principal com salvamentos,
  configurações e userdata Steam isolados, rede offline e arquivos reais
  conferidos antes e depois de cada inicialização.
## <a id="session-2026-10-20-i-phase-3-plan-find-player-and-nemesis-data-at-runtime"></a>Sessão 2026-10-20 i: plano da fase 3 (encontrar dados de jogador e Nemesis em execução)

### <a id="what-prior-work-gives-us-read-from-public-source-2026-10-20-no-licenses-stated"></a>O que o trabalho anterior fornece (lido de fontes públicas, 2026-10-20; sem licenças declaradas,
então aprendemos com ele e não copiamos código)

- **SystematicSkid/shadow-of-war-save-editor** (`src/main.cpp`, 2024-01, escrito para a
  mesma build Steam até onde sabemos: jogo sem patches desde 2018-09):
  - Chama comandos de desenvolvedor do próprio jogo, cada um `void(int argc, const char** argv)`,
    por RVA: `0x1C76D08` extrair facções em JSON (`factions.json`), `0x1C76784` extrair um
    membro de facção (`faction_member_single_save.dat`), `0x1C7709C` extrair todos (`all.dat`),
    `0x1C77070` carregar arquivo de salvamento, `0x1C762AC` extrair perfil de facção, `0x1B7663C` dados
    de missão, `0x1BECB58` inventário, `0x1C920D4` adicionar seguidor.
  - Internamente, o sistema Nemesis é **"Faction" / "FactionMember"**: opções de depuração
    `NemesisForge.Debug`, `Faction.Debug.ZonePower`, `.Tribe`, `.TraitCatalyst`,
    `.Reward`, `.BundleMgr`, `FactionMember.Debug.Resurrection`, como bools nos RVAs
    `0x2A34DA3..0x2A34DB8`.
  - Um **registro de variáveis de script**: lista ligada encontrada pelo padrão
    `48 89 05 ? ? ? ? 48 89 05 ? ? ? ? 48 8D 05 ? ? ? ? 48 89 05 ? ? ? ? 48 89 05 ? ? ? ? 48 89 05 ? ? ? ? E8`;
    cada variável tem `name` (+0x08), `description` (+0x10), `file` de origem (+0x18), `line`
    (+0x20), valor bool em +0x38; nó fica em var+0x28.
  - Uma **impressão de depuração** compilada no jogo `(category, fmt, ...)` (categorias como `[LOOT]: `),
    encontrada como alvo de chamada de
    `E8 ? ? ? ? 48 83 C3 10 48 8D 54 24 40 48 89 5C 24 30 48 8D 4C 24 30 E8 ? ? ? ? 84 C0 75 AE`.
  - Banco de strings (texto localizado por ID): ponteiro em RVA `0x2701720`, getter `0x23A6A0`;
    tabelas "lua string lists" entre RVAs `0x1B28C09` e `0x1B399F9`.
- **SystematicSkid/sow-freecam**: global `GameClient*` por
  `48 8B 0D ? ? ? ? E8 ? ? ? ? C7 47` (relativo a rip em +3); `GameClient+0x898`
  CameraOwner, `+0x50` Camera de jogabilidade, `+0x98` transform, transform `+0xAC` posição
  (vec3), depois rotação (quat); int de modo de CameraOwner em `+0x80`.
- **Mods de ReaperAnon** (buscas de padrões de bytes após o jogo iniciar; carregador espera 10 s, depois
  consulta a cada 500 ms): gravação de vida `0F 2F F2 F3 0F 11 93 2C 04 00 00`
  (`movss [rbx+0x42C]`: vida de um personagem em `+0x42C`), verificação "dev bool"
  `48 8D 0D ? ? ? ? E8 ? ? ? ? 84 C0 74 37 48 8B CB`, temporizador de missão, sequência de acertos, raridade
  de criação de orcs, informações de Uruk. O carregador também substitui a chamada `GetActiveWindow` do jogo
  para continuar executando sem foco.
- Nossa própria verificação hoje: o executável tem 1.323 nomes RTTI MSVC, mas só para Havok (`hk*`,
  incluindo `hkaiCharacter`), SDK online WB (`hydra`: Session, Match, PlayerJoined...)
  e std. **Classes do jogo não contêm nomes RTTI**; nomes devem vir do registro de variáveis de script
  e das impressões de depuração.

### <a id="constraints"></a>Restrições

- Código em disco é empacotado (Denuvo): tudo abaixo executa no processo do jogo após
  desempacotar a si próprio (consultar até encontrar padrão conhecido, como fazem os mods existentes). Não modificar
  ou remover Denuvo/SteamStub. Sem depurador conectado (risco antidepuração; também uma
  instalação extra). Sem despejo completo do executável desempacotado por enquanto.
- Só na cópia A de teste, proteção sempre ativa (salvamentos isolados, rede offline). Despejos e
  saídas de dados do jogo ficam privados; publicamos só nomes, deslocamentos e assinaturas.

### <a id="steps"></a>Etapas

1. **Módulo de sondagem (ferramentas).** Adicionar parte `sowprobe` à DLL de proteção: thread em
   segundo plano que espera o jogo desempacotar, mantém execução sem foco
   e atende um pipe nomeado para o cliente fazer perguntas durante a execução:
   `module` (base, seções), `scan <pattern>` (todas as ocorrências), `read <addr> <len>`,
   `rip <addr>` (resolver relativo a rip), `vars` (lista de variáveis de script), `log` (impressões de depuração
   capturadas). Somente leitura por padrão; `write`/`call` só com `probe_write=1`. Um pequeno cliente
   Python.
2. **Conferir cada assinatura e RVA conhecidos na nossa build.** Cada padrão deve ter exatamente uma
   ocorrência; cada RVA do editor de salvamentos deve cair no início de função. Registrar uma
   tabela de assinaturas (padrão, ocorrências, RVA, significado, fonte, data) aqui. Esperar correspondências
   (mesma build), verificar mesmo assim.
3. **Deixar o jogo se descrever.** Extrair registro de variáveis de script (nomes, descrições,
   arquivos-fonte, linhas): mapa dos sistemas do motor. Interceptar impressão de depuração para arquivo de
   log. Ativar variáveis de depuração `Faction.*` / `NemesisForge` e registrar o que o sistema
   Nemesis imprime durante o jogo.
4. **Jogador.** A partir de `GameClient`, encontrar personagem local (alvo seguido pela câmera,
   ou objeto cujo `+0x42C` muda ao jogador sofrer dano). Mapear posição,
   rotação, vida, estado de animação por capturas e diferenças enquanto o jogador se move (teclas
   postadas à própria janela do jogo, sem entrada do SO). O mesmo para um orc próximo.
5. **Mundo Nemesis.** Executar extrações do próprio jogo (`factions.json`, `all.dat`,
   membro único) no ambiente isolado e estudar o formato. Testar `load save` em uma extração:
   se cliente puder carregar o mundo extraído do anfitrião, essa é a sincronização na entrada. Comparar
   extrações antes e depois de evento Nemesis (capitão promovido, morto, traidor) para ver
   o que muda; interceptar código por trás das impressões relacionadas para obter eventos.
6. **Sistema de salvamento.** Registrar cada leitura/gravação de salvamento com horários (proteção já os
   vê), relacionar salvamentos a `all.dat`, encontrar disparador de salvamento automático.

### <a id="needs"></a>Necessidades

- **Salvamento com progresso no ambiente isolado.** Dados Nemesis só existem após o prólogo.
  Proposta: copiar um salvamento existente do backup ao perfil isolado (somente
  ali; original intacto). Alternativa: novo jogo, horas de jogo.
- Depois, só se as etapas 2-5 pararem: instalar Ghidra (+ JDK) ou depurador, ou extrair o
  executável desempacotado para análise estática.

### <a id="risks"></a>Riscos

- Denuvo pode reagir a patches de código em sua faixa protegida (mods existentes modificam código
  do jogo e funcionam, então provavelmente não).
- Chamar comandos de desenvolvedor pode causar falhas ou corromper estado: só no ambiente isolado, falha registrada.
- RVAs do editor de salvamentos podem ser de build diferente da nossa (etapa 2 resolve).

## <a id="session-2026-10-20-j-phase-3-step-1-probe-built-not-yet-run-in-the-game"></a>Sessão 2026-10-20 j: fase 3, etapa 1, sonda construída (ainda não executada no jogo)

- Salvamento real mais recente (arquivo sem número == posição 1, de 2025-11-20) copiado do
  backup somente ao perfil isolado; hashes iguais; verificação de backup intacta.
- `sowprobe` adicionado à DLL de proteção (`probe=1`): espera padrão que só existe
  após o jogo desempacotar (padrão: carga de GameClient do freecam
  `48 8B 0D ? ? ? ? E8 ? ? ? ? C7 47`), registra quanto demorou e atende `ping`, `module`, `scan`, `read`, `rip`, `deref`
  somente leitura em pipe nomeado local. Só lê páginas
  confirmadas, legíveis, sem proteção guard (VirtualQuery primeiro), para nunca acionar uma página
  guard. Pequeno cliente Python conversa com ela.
- Novo caso offline, `probe_serve`, confere cada
  comando contra dados fixos em processo filho vivo (busca de marcador exata e com curingas, leitura,
  resolução relativa a rip, desreferência de ponteiro, leitura não mapeada -> err, comando desconhecido -> err,
  ainda vivo após erros), e `probe_off` (sem pipe sem `probe=1`).
  Cliente Python conferido contra sonda ativa.
- Preparado na cópia A (`probe=1`, `network=offline`). Próximo: iniciar com sonda ativa,
  confirmar que o padrão de prontidão aparece e quando, depois etapa 2 (conferir cada assinatura
  e RVA conhecidos nesta build).

## <a id="session-2026-10-20-k-phase-3-step-2-signatures-checked-in-the-running-game"></a>Sessão 2026-10-20 k: fase 3, etapa 2, assinaturas conferidas no jogo em execução

Cópia A iniciada com proteção + sonda (`network=offline`), deixada no menu principal
(salvamento não carregado). Todas as verificações abaixo são somente leitura (scripts pequenos pela sonda); saídas
brutas mantidas privadas.

### <a id="observations-2"></a>Observações

- Sonda pronta **187 ms** após iniciar; padrão GameClient ocorreu uma vez em RVA `1775F54`.
  Base da imagem `0x140000000` (a preferida), então RVA + 0x140000000 = endereço.
- **Correção da premissa da fase 2/3 "código em disco é empacotado":** todas as 7.559 páginas de
  `.arch` (RVA 0x1000, 31 MB, código do jogo), todo `.pdata` (tabela de desenrolamento, ou seja, início e fim de
  cada função) e `.sdata` são **idênticos byte a byte na memória e em disco**.
  Só as primeiras 2 páginas de `.xtext` (4,6 KB) e 16 bytes de `.idata` diferem (preenchidos ao
  carregar). A parte opaca é `.bss` RWX de 73 MB (código do próprio Denuvo). Então o código do jogo
  pode ser estudado estaticamente pelo arquivo executável (por exemplo, `dumpbin /disasm`, `.pdata` para
  limites de função): sem necessidade de despejo de memória, sem tocar na proteção.
- **Tabela de assinaturas (build Steam 3095001, SHA-256 do executável `ed0d95ca...0bdaef`); contagens de ocorrências
  exatas (busca máximo 16):**

  | o quê | padrão | ocorrências | RVA da ocorrência | resolve para | fonte |
  |---|---|---|---|---|---|
  | global GameClient | `48 8B 0D ? ? ? ? E8 ? ? ? ? C7 47` | 1 | 1775F54 | 26FFA98 (rip +3/7) | freecam |
  | registro de variáveis de script | `48 89 05 ? ? ? ? 48 89 05 ? ? ? ? 48 8D 05 ? ? ? ? 48 89 05 ? ? ? ? 48 89 05 ? ? ? ? 48 89 05 ? ? ? ? E8` | 1 | 816D2A | 2A58BE0 (rip +3/7) | editor de salvamentos |
  | impressão de depuração | `E8 ? ? ? ? 48 83 C3 10 48 8D 54 24 40 48 89 5C 24 30 48 8D 4C 24 30 E8 ? ? ? ? 84 C0 75 AE` | 1 | 36C447 | 19C83AC (call) | editor de salvamentos |
  | locais de chamada de impressão de depuração | sondas 2, 3, 5 do editor de salvamentos | 1 cada | 101A63, 101A99, 4CDCC8 | todos 19C83AC | editor de salvamentos |
  | sondas 0 e 4 do editor de salvamentos | (ver código-fonte dele) | 0 | | | editor de salvamentos |
  | gravação de vida `movss [rbx+42C]` | `0F 2F F2 F3 0F 11 93 2C 04 00 00` | 1 | 2E4D26 | | ReaperAnon |
  | verificação de dev bool | `48 8D 0D ? ? ? ? E8 ? ? ? ? 84 C0 74 37 48 8B CB` | 1 | 2D769F | 2A34D6A (rip +3/7) | ReaperAnon |
  | temporizador de missão | `48 8D 59 10 48 8B F9 48 8B CB E8 ? ? ? ? 84 C0 0F 85` | 1 | 16F382 | | ReaperAnon |
  | outros 13 padrões ReaperAnon (desafios de itens, velocidade élfica, FOV, tempestade de gelo, sequência de acertos, poder montado, equipamento múltiplo, mirian, raridade de orcs, nível de habilidade, pré-requisitos, bloqueios de história, informações de uruk) | ver repositório deles | 1 cada | | | ReaperAnon |
  | chamada GetActiveWindow do carregador de mods | `FF 15 2A D7 16 01` | 1 | C25638 | | carregador de mods |

- **Os RVAs fixos do editor de salvamentos não servem nesta build.** Seus nove RVAs de comando
  (`1C76D08`, `1C76784`, `1C7709C`, `1C77070`, `1C762AC`, `1B7663C`, `1BECB58`,
  `1C920D4`, `23A6A0`) caem todos no meio de funções (sem preenchimento anterior, sem prólogo), e seus
  bools de depuração `2A34DA3..2A34DB8` são todos 0, sem corresponder a entrada do registro. Seus *padrões*
  correspondem. Provavelmente escrito para outra build (Microsoft Store?). **Nunca chamar
  esses RVAs nesta build.**
- **Registro de variáveis de script** (RVA `2A58BE0`, percorrido como faz o editor): 680
  entradas, 170 arquivos-fonte sob `C:\P4\KRAKEN_CODE_STREAM\source\` ("Kraken" é o
  nome interno do motor, como na string `SOFTWARE\WB Games\Kraken` do executável). Entradas
  são registros de 0x40 bytes: `+0` vtable (tipo), `+8` nome, `+0x10` descrição, `+0x18`
  arquivo, `+0x20` linha, `+0x28/+0x30` elos da lista, `+0x38` **ponteiro de tratador para programas
  de console** / valor para variáveis. Tipos por RVA da vtable: `1E69180` programa (449),
  `1E69FD0` bool (69), `1E69FA0` (58, floats?), `1E69FB8` int (28, por exemplo,
  `NetMeshGamePort` = 0x408 = 1032), `1E69F88` (27), `1E69168` string (8,
  `Cloud.APIKey`, `Cloud.Server`...), configurações de renderização (algumas outras).
- Layout do código-fonte é a divisão cliente/servidor LithTech: `Game\ClientShellDLL\` (cliente),
  `Game\ObjectDLL\` e `ObjectDLL_AI\` (objetos do jogo no servidor: `PlayerObj.cpp`,
  `Combat.cpp`, `Quest.cpp`, `SlowMoUtil.cpp`), `Game\Shared\` (incluindo todo código Faction),
  `Engine\Runtime\client\clientmgr.cpp`, `Engine\Runtime\net\NetStateMachine_HostVote.cpp`.
- Programas de console relevantes ao cooperativo (nome: descrição, fonte):
  - `Faction.Save` / `Faction.Load` / `Faction.Dump`: salvar, carregar ou extrair **todos os membros
    de facções e dados relevantes** para arquivo nomeado (FactionConsolePrograms.cpp:254/285/261).
  - `FactionMember.Save` / `.Load` / `.Save.Pos` / `.ProfileDump` / `.SetDead` /
    `.SetHealthPct` / `.SetXPLevel` / `.Rebuild` / `.BuildWithBuilder` / `.SlotAsOverlord`.
  - `Faction.AdvanceTime` ("advances time, and will generate new simevents"),
    `Faction.SimEvent`, `.SimEvent.Generate` / `.Simulate` / `.Flush`,
    `Faction.SimEventDump`, `Faction.AddEvent`, `Faction.ActivateSimEventSequence`: a
    simulação Nemesis fora da tela roda em "SimEvents".
  - `QuestMgr.Save` / `QuestMgr.Load`, `Quest.ListActive`, `Quest.CompleteActiveQuest`,
    `QuestMgr.ReplayQuest`, `QuestMgr.SetQuestComplete`.
  - `Debug.Save` / `Debug.Load` ("a debug save that is not user specific"), User.cpp.
  - `Teleport <x> <y> <z>` (PlayerObj.cpp:4224).
  - `SlowMO.Set` ("time scale denominator"), `.Start`, `.Stop`, `.Pause`, `.Resume` em
    `ObjectDLL\SlowMoUtil.cpp`: câmera lenta é escala de tempo do mundo (no servidor).
  - `GameServerShell.DebugPause` / `.DebugUnpause` / `.PrintPauseFlags` /
    `.ResetWorldIdentical` ("resets the world to its identical state") /
    `.AdvanceTimeOfDay`, definidos em `ClientShellDLL\WorldSimSession.cpp` e
    `GameClientShell.cpp`.
  - `Replay.StartRecordingPlayback` / `.SavePlayback` / `.LoadAndStartPlayback` /
    `.VerifyPlayback` ("runs the loaded playback 10 times and outputs the number of
    successes/failures"): gravação e reprodução de entrada e tempo de quadro (PlaybackMgr.cpp).
  - `NetMeshGamePort` ("port to use for the game NetMesh when hosting"),
    `Net.NSM.HostVote.Timeout` / `.PauseInStart` (máquina de estados de rede com votação de anfitrião).
- Cadeia de câmera no menu principal: `*(26FFA98)` GameClient -> `+0x898` CameraOwner ->
  `+0x50` câmera de jogabilidade = null (esperado fora do mundo).
- Nota de uso da sonda: deslocamentos de `deref` são números estilo C, então hexadecimal precisa de `0x`.

### <a id="derived-4"></a>Derivado

- Usar padrões e nomes do registro, nunca RVAs fixos de outras builds.
- Cada programa de console pode ser encontrado por nome; seu tratador está na entrada `+0x38`. A
  convenção de chamada é desconhecida nesta build (editor usava `(int argc,
  const char** argv)`); conferir na desmontagem antes de chamar qualquer um.
- Motor manteve estrutura cliente/servidor LithTech, tem NetMesh com hospedagem,
  máquina de estados de votação de anfitrião, sistema de reprodução aparentemente determinístico e
  salvamento/carregamento mundial de dados Nemesis. Se a divisão cliente/servidor for real em execução (mundo de
  objetos de servidor local mais cliente), o cooperativo poderia conectar um segundo cliente ao servidor do
  anfitrião em vez de sincronizar tudo manualmente. **Não verificado; a questão em aberto mais
  importante para o projeto cooperativo.**

### <a id="next-1"></a>Próximo passo

- Análise estática do executável: tabela de funções de `.pdata`; desmontar tratadores dos
  programas acima e código server-shell, clientmgr e NetMesh/votação de anfitrião.
- Etapa 3 (precisa de sonda capaz de gravar/interceptar, `probe_write=1`): interceptar impressão de depuração para
  log; chamar programas inofensivos (`Faction.SimEventDump`, `Quest.ListActive`) no ambiente isolado
  quando sua convenção de chamada estiver confirmada estaticamente.

## <a id="session-2026-10-20-l-phase-3-step-3-debug-print-capture"></a>Sessão 2026-10-20 l: fase 3, etapa 3, captura de impressão de depuração

### <a id="built-1"></a>Construído

- Modo `probe_write=1`: comando de pipe `write <addr> <hex>` (registrado) e hooks.
- `hook_debug_print=1`: impressão de depuração (encontrada pelo padrão do local de chamada do editor,
  alvo RVA `19C83AC`) é, nesta build, um **stub de 12 bytes**:
  `4C 89 44 24 18` (mov [rsp+18h],r8), `4C 89 4C 24 20` (mov [rsp+20h],r9), `C3`, `CC`,
  com a função seguinte logo após (desmontagem estática, `dumpbin /disasm`). O hook
  confere exatamente esses 12 bytes, depois os substitui por `mov rax,<stub>; jmp rax` (12
  bytes, sem tocar na função seguinte; rax está livre na entrada). Nosso stub armazena
  rcx/rdx/r8/r9 na área reservada pelo chamador como o original, chama um formatador protegido
  e retorna; informações de desenrolamento são registradas para ele. Saída: `<profile>\debugprint.log`
  (limite 64 MB), buffer circular para `dbg`, contagens por categoria para `dbgstats`.
- Testes cobrem: formato do patch e função vizinha, gravação e releitura, 1.005
  chamadas de 5 threads incluindo argumentos de pilha, ponteiro `%s` inválido (registrado como
  `<fault while formatting> <format>`), `%n` (registrado como `<bad format> <format>`), recusa
  quando stub difere e nenhum hook ou gravação sem `probe_write=1`.

### <a id="in-the-game-launch-4-main-menu"></a>No jogo (inicialização 4, menu principal)

- Hook instalado 330 ms após iniciar, antes da inicialização do próprio jogo; jogo executou normalmente.
- **0 linhas de depuração** nos primeiros mais de 2 minutos: builds de lançamento condicionam quase toda chamada a
  sinalizador de byte por canal, desligado.
- Catálogo estático dos chamadores (script só sobre o executável):
  **1.100 locais de chamada**; categorias incluem `[COMBAT|...]` (maioria), `[QUEST]` (99),
  `[QUEST|JOB]` (47), `[AI|SPAWNAMBIENT|REJECT]` (33), `[FACTION|AMBUSH]` (25),
  `[FACTION|RESURRECTION]` (19), `[FACTION|CATALYST]` (18), `[LOOT]` (18),
  `[FACTION|BUNDLE]` (15), `[SIMEVENT]` (8), `[SIMEVENT|OUTCOME]` (8), `[SLOWMO]` (19).
  449 locais têm proteção `cmp byte ptr [rip+x], 0` / `movzx` nos 64 bytes anteriores à
  chamada; em 651 nenhuma foi encontrada (outros formatos ou incondicionais).
- Tabela de sinalizadores de canal (byte por canal, RVA -> categoria das chamadas condicionadas):
  `2A34D9E` QUESTMGR, `2A34DA0` QUEST|JOB, `2A34DA1` QUEST|PREDICATE, `2A34DA3`
  INVENTORY|PERSISTENT, `2A34DA5` FACTION|CATALYST, `2A34DA6` FACTION|HIJACK, `2A34DA8`
  FACTION|REWARD|REJECT, `2A34DAA` FACTION|GRUNTTRAIT, `2A34DAB` FACTION|STATQUERY,
  `2A34DAE`/`2A34DAF` SIMEVENT, `2A34DB0` SIMEVENT|OUTCOME, `2A34DB1` SIMEVENT|REPLAY,
  `2A34DB2` SIMEVENT|SEQUENCE, `2A34DB3` FACTION|RESURRECTION, `2A34DB4` FACTION|AMBUSH,
  `2A34DB5` LOOT, `2A34DB6` FACTION|BUNDLE, `2A34DB7` FACTION|FORTDEFENSE, `2A34DB8`
  FACTION|TRIBE, `2A34DBC` SLOWMO, `2A34DBE` NEMESISFORGE, `2A34DBF` GAMEMODE|SESSION,
  `2A34F95` QUEST, `2A366B1` FACTION|PURPOSE; canais de combate `2A34D1A..2A34D98`,
  `2A25D80/81` COMBAT|HINTS.
- **Correção da sessão k:** RVAs de bools de depuração do editor (`2A34DA3` inventário,
  `2A34DA5` catalisador de característica, `2A34DAA` característica de soldado, `2A34DAB` consulta de atributos, `2A34DB3`
  ressurreição, `2A34DB4` emboscada, `2A34DB5` saque, `2A34DB8` tribo) são exatamente os sinalizadores
  de canal desta build nessas categorias. Eram 0 porque canais iniciam desligados,
  e não são variáveis do registro, motivo pelo qual a verificação da sessão k não encontrou correspondência.
  Portanto, seus RVAs de *dados* servem nesta build; os de *funções* continuam não servindo.
- Ativados 23 canais com `write` (missão, facção, simevent, saque, câmera lenta, nemesis
  forge, sessão de modo de jogo; combate desligado): sinalizadores relidos como 01. Ainda 0 linhas no
  menu principal (nenhum mundo carregado). Próximo: carregar salvamento isolado e capturar.

## <a id="session-2026-10-20-m-crash-with-the-first-debug-print-hook-root-cause-and-fix"></a>Sessão 2026-10-20 m: falha com primeiro hook de impressão de depuração, causa-raiz e correção

### <a id="observations-3"></a>Observações

- Inicialização 4 (hook v1, 23 canais ativos, gravados manualmente após iniciar): salvamento isolado
  carregado manualmente. Em ~0,3 s após carregar o mundo, o hook capturou 85.558 linhas
  (13 MB): 85.248 `[FACTION|REWARD|REJECT]` ("Reward '...' Failed Filter -
  IncludedTraitMarkerList (...)"), 156 `[FACTION|PURPOSE]`, 104 `[FACTION|TRIBE]`, 49
  `[SIMEVENT|OUTCOME]` (por exemplo, `HandleFactionEventAction: Event =
  FactionMember_RoleSelected_Standard; Subject = Gubu`), 1 `[QUESTMGR]: GameModeSet -
  SinglePlayer`. Um segundo depois, jogo falhou: Application Error, `ShadowOfWar.exe`,
  `0xC0000005`, deslocamento da falha `0x598817`. Salvamentos isolados não regravados; verificação do backup
  intacta.
- Análise estática (executável): `598817` é a primeira instrução real da função
  `598804..59894B` (de `.pdata`): `mov rbx, [rcx+48h]`, ou seja, `this` inválido. Dos seus 5
  chamadores, `F4F41A` fica logo após a impressão `GameModeSet - %s`:
  ```
  F4F3D5  cmp byte ptr [2A34D9E], 0      ; QUESTMGR channel
  F4F3DC  mov r9, [r14+6C60h]            ; value needed after the print
  F4F412  call 19C83AC                   ; debug print (only when the channel is on)
  F4F417  mov rcx, r9                    ; r9 used after the call, not reloaded
  F4F41A  call 598804
  ```
  `r9` é volátil na ABI Win64, mas o compilador sabia que a chamada (stub de 12 bytes)
  não muda registradores e manteve um valor ativo nele. Nosso stub v1 chamava uma função C++
  normal, que destruía r9; o patch `mov rax,imm64; jmp rax` também destruía rax.
  **Causa-raiz: nosso hook, não o jogo.**

### <a id="fix"></a>Correção

- Patch é `jmp rel32` de 5 bytes (+ int3) para página de stub alocada a até 2 GB do
  código do jogo: nenhum registrador tocado. Stub só grava nas duas posições reservadas escritas pelo original
  (`[rsp+18h]`, `[rsp+20h]`), salva e restaura rax, rcx, rdx, r8-r11, xmm0-5
  e RFLAGS, passa `va_list = &[entry rsp + 18h]` (contíguo aos argumentos de
  pilha) e registra informações de desenrolamento para seus pushes.
- Novo teste: código de máquina gerado define rax, rcx, rdx, r8-r11, xmm0-5 e duas sentinelas
  nas posições reservadas do chamador, chama stub e confere tudo depois. O stub interceptado
  e o original passam ("regs ok"); mutante que não restaura r9
  falha ("changed: r9 r11").
- `debug_channels=<rva,...>` define sinalizadores de canal logo após instalar o hook (sem corrida
  com jogador carregando salvamento). Preparado com 22 canais; `FACTION|REWARD|REJECT`
  (`2A34DA8`) desligado por ruído.
- Risco residual não coberto: jogo tem algum código AVX (39 `vzeroupper`, ~22 movimentações de 256 bits
  em `.arch`); stub não salva metades superiores ymm. MSVC emite `vzeroupper`
  antes de chamadas para fora do código AVX, então não devem estar ativas durante esta chamada.

### <a id="lesson-for-the-playbook-hooking"></a>Lição para o playbook (hooks)

- Função-folha minúscula (stub de build de lançamento) pode ter chamadores que dependem de ela não
  tocar registradores *voláteis*: otimização de programa inteiro pode manter valores em rcx,
  rdx, r8-r11 ou rax durante essa chamada. Ao substituí-la, preservar cada
  registrador preservado por ela, gravar só na memória em que gravava e alcançá-la por salto que
  não destrua nada (`jmp rel32` para página próxima). Testar com thunk de captura de registradores
  e mutante, não só com chamadas C++ (que nunca percebem).
## <a id="session-2026-10-20-n-launch-5-fixed-hook-and-an-isolation-failure-via-steam"></a>Sessão 2026-10-20 n: inicialização 5 (hook corrigido) e falha de isolamento via Steam

### <a id="observations-4"></a>Observações

- Hook v2 instalado 330 ms após iniciar; 22 sinalizadores de canal definidos (relidos como 01;
  `FACTION|REWARD|REJECT` deixado 00). Salvamento isolado carregado, ~10 min de jogo manual;
  jogo saiu normalmente (saída 0 após 635 s, sem Application Error). Captura de depuração
  `debugprint.log` 4,1 MB (análise pendente). Modo offline: 8 recusas HTTPS ConnectEx
  (mesmos dois hosts, a cada ~15-45 s).
- Jogo salvou durante a partida: no ambiente isolado, `<prefix>_ShadowOfWar.sav` e `_1_` foram
  regravados (2.361.712 bytes, 19:17:51.955), e a antiga posição 1 movida para `_2_`
  (rotação de salvamentos). Tudo pelo redirecionamento da proteção, como projetado.
- **Verificação do backup falhou:** no `Steam\userdata\<id>\356190\` real,
  `remote\<prefix>_ShadowOfWar.sav` foi regravado às 19:17:51.949 com **os mesmos bytes**
  do salvamento isolado (prefixo SHA-256 `0033D4753E3610BC`), e `remotecache.vdf` às
  19:18:02.908 (tamanho, hora, sha atualizados; `syncstate` 1 -> 3). Salvamentos reais em
  `%LOCALAPPDATA%` e todo o restante do manifesto intactos.
- Proteção não registrou gravação nessa pasta pelo processo do jogo (seria
  redirecionada ou encerraria o jogo). Então outro processo gravou: o cliente Steam.
- Steam Cloud de 356190 continua `cloudenabled 0`; nada indica upload.

### <a id="derived-5"></a>Derivado

- Jogo envia seu salvamento por `ISteamRemoteStorage` além de gravá-lo em disco;
  processo do cliente Steam (`steam.exe`) grava essa cópia em `userdata\<id>\356190\remote`
  mesmo com Steam Cloud desligado para o jogo (mantém cópia local e marca como não sincronizada).
  **Redirecionamento de arquivos dentro do processo não cobre isso.** Correção das sessões c e
  f: gravações de armazenamento remoto Steam não são feitas pelo processo do jogo (a gravação de
  `<id>` vista dentro dele é outro arquivo).
- Antes de nova sessão em que o jogo possa salvar, a proteção deve impedir gravações de
  `ISteamRemoteStorage` no processo do jogo (por exemplo, fazer FileWrite/
  FileWriteAsync/FileDelete/FileForget falharem ou virarem operações sem efeito), e o teste
  deve conferir a pasta real do Steam após salvamento. Até lá: não salvar na cópia de
  teste.

### <a id="proposed-repair-of-the-real-steam-folder"></a>Reparo proposto da pasta real do Steam

- Com Steam totalmente fechado (pode regravar `remotecache.vdf` da memória ao sair),
  restaurar `remote\<prefix>_ShadowOfWar.sav` e `remotecache.vdf` do backup
  verificado, depois repetir a verificação do backup.

### <a id="playbook-lesson-isolation"></a>Lição do playbook (isolamento)

- Cópia de teste isolada não está isolada do cliente da loja. API de salvamento na nuvem Steam
  é atendida por `steam.exe`, que grava na pasta userdata real tudo que
  a cópia de teste salva, mesmo com Steam Cloud desligado para o jogo. Bloquear as
  gravações de armazenamento remoto no processo do jogo e conferir pastas do cliente da loja
  após cada sessão de teste que salva.
- Restaurado (Steam totalmente encerrado, sem processo Steam ou jogo em execução):
  `remote\<prefix>_ShadowOfWar.sav` e `remotecache.vdf` copiados de volta do backup
  verificado com horários originais (robocopy /COPY:DAT); versões escritas pelo teste
  guardadas à parte. Verificação posterior: tudo
  presente, **intacto** (render.cfg só informação). Ainda não visto: o que Steam
  faz com esses arquivos na próxima inicialização (deve encontrá-los iguais ao cache).

## <a id="session-2026-10-20-o-steam-remote-storage-guard-built-tested-offline-staged"></a>Sessão 2026-10-20 o: proteção do armazenamento remoto Steam (construída, testada offline, preparada)

- Estático (executável e `steam_api64.dll` distribuído, SHA-256 `f12cf470954d9d956f7d44f9eb84659890c5722a021548ab88710340c0965230`,
  base da imagem `0x3B400000`, 796 exportações): única importação Steam estática do jogo é
  `SteamInternal_ContextInit` (estilo SDK de acessores em cache). Cada wrapper plano é
  `mov rax,[rcx]; jmp [rax+off]`, fornecendo deslocamentos da vtable de ISteamRemoteStorage (v014):
  FileWrite 0x00, FileRead 0x08, FileWriteAsync 0x10, FileForget 0x28, FileDelete 0x30,
  FileShare 0x38, SetSyncPlatforms 0x40, FileWriteStreamOpen/WriteChunk/Close/Cancel
  0x48/0x50/0x58/0x60, SetCloudEnabledForApp 0xB8, UGCDownloadToLocation 0x1B0;
  ISteamClient::GetISteamRemoteStorage 0x88.
- Proteção (sempre ativa): espera SteamAPI_Init do jogo, obtém a
  mesma interface pela API plana, lê deslocamentos das posições pelos bytes dos wrappers
  (qualquer outro formato: saída `0xC0DE0006`) e substitui esses 12 métodos de gravação da vtable
  por funções que registram e informam sucesso (async/stream: inválido). Leituras intactas.
- Testes offline com `steam_api64.dll` substituto (wrappers exatos byte a byte, vtables com
  contadores; nunca copiado a pasta de jogo): `steam_block`: todas as 12 gravações
  respondidas pela proteção, nenhuma chegou ao "Steam", FileRead passou; mutante sem
  proteção: todas as 12 chegaram. Nota: este compilador emite
  `mov r10,[rax+off]; jmp r10` para esses wrappers, então os do substituto são bytes brutos.
- Preparado na cópia A; o `steam_api64.dll` real da cópia está intacto (hash igual
  ao da instalação real). Verificação do backup intacta.
- Não coberto: ISteamUserStats (conquistas/estatísticas obtidas em testes vão à conta
  Steam real por steam.exe); outras interfaces Steam.
- Próximo: sessão protegida com salvamento automático; depois a verificação do backup deve permanecer
  limpa para `userdata\<id>\356190`.

## <a id="session-2026-10-20-p-guarded-save-session-launch-6-steam-folder-stays-clean"></a>Sessão 2026-10-20 p: sessão de salvamento protegida (inicialização 6), pasta Steam fica limpa

- Verificação prévia com Steam reiniciado após restaurar: intacto (Steam aceitou arquivos
  remotos restaurados).
- Inicialização 6: hook de impressão de depuração + 22 canais ativos em ~330 ms; **proteção de armazenamento remoto Steam ativa
  aos 1.015 ms** (antes de o próprio jogo iniciar). Salvamento isolado carregado e jogado manualmente;
  saída 0 após 608 s; sem falha, sem FATAL/PROTECTED/WATCH.
- **16 salvamentos** na sessão (primeiro em +289,7 s, depois a cada 0,6-46 s jogando:
  salvamento automático é frequente). Cada um grava `<prefix>_ShadowOfWar.sav` e `_1_` em disco
  (redirecionado ao ambiente isolado) e, no mesmo instante, chama
  `ISteamRemoteStorage::FileWrite('\<prefix>_ShadowOfWar.sav', ~2.3 MB)`; todos os 16 bloqueados
  pela proteção (registrados com tamanhos; o último, 2.315.168 bytes, igual ao salvamento final em
  disco). Posições rotacionam uma vez por sessão, no primeiro salvamento (`_1`->`_2`->`_3`).
- **Verificação do backup depois: intacto.** O `remote\<prefix>_ShadowOfWar.sav` real está
  intocado (2.334.736 bytes, 2025-11-20). Steam regravou `remotecache.vdf` na saída do jogo
  (19:45:44) com conteúdo idêntico byte a byte (hash igual ao backup).
- Captura de depuração desta sessão: 3,4 MB (`debugprint.log`, só local); análise pendente.
- Estado do isolamento: redirecionamento de arquivos + proteção (processo do jogo) e proteção do armazenamento remoto
  (API Steam), juntos, mantêm salvamentos reais e pasta remota Steam intactos durante
  uma sessão real de salvamento. Ainda em aberto: ISteamUserStats (conquistas/estatísticas).

## <a id="session-2026-10-20-q-what-the-nemesis-system-logs-debug-print-capture-read-only"></a>Sessão 2026-10-20 q: o que o sistema Nemesis registra (captura de impressão de depuração, somente leitura)

Fontes: duas capturas com 22 canais ativos (combate e `FACTION|REWARD|REJECT` desligados), jogo
manual no salvamento isolado: sessão 5 (42.977 linhas, ~10 min, dois capitães mortos) e
sessão 6 (36.108 linhas, ~6 min jogando, 16 salvamentos automáticos), resumidas em modelos de
mensagem por categoria. Logs brutos ficam privados.

### <a id="observations-5"></a>Observações

- **Uma thread.** Cada linha de cada categoria numa sessão vem de uma única thread
  (sessão 5: 5264, sessão 6: 25236): lógica de facção, missão, SimEvent, saque, emboscada e câmera lenta
  executa toda na mesma thread do jogo.
- **Volume por categoria** (sessão 5 / 6): FACTION|BUNDLE 23.522 / 24.002; QUEST|JOB 5.510 /
  2.948; FACTION|PURPOSE 3.204 / 2.667; FACTION|TRIBE 3.079 / 2.531; SIMEVENT|OUTCOME 1.617 /
  1.260; LOOT 1.532 / 1.132; SLOWMO 1.549 / 142; SIMEVENT 1.176 / 461; FACTION|AMBUSH 1.067 /
  311; QUEST 630 / 597; SIMEVENT|REPLAY 25 / 2; FACTION|CATALYST 24 / 0;
  FACTION|RESURRECTION 7 / 0; mais alguns GRUNTTRAIT, HIJACK, STATQUERY, QUESTMGR,
  GAMEMODE|SESSION.
- **Despacho central de eventos:** `HandleFactionEventAction: Event = <name>; Subject = <captain>;
  Other = <captain|None>` (SIMEVENT|OUTCOME). 40 tipos de evento na sessão 5, por exemplo,
  `FactionMember_RoleSelected_Standard/_Notable/_BazGazDaz` (atribuição de papel, ~1.400 ao
  carregar), `IsPlayerFollowerApply`, `Promote`, `TimePassed`, `PromoteEmpty_Builder*`/
  `PromoteDead_Builder*` `_Simulate`/`_Clear`, `ActiveKilledByPlayer`,
  `BrotherKilledByPlayer`, `ActiveDominationStarted`, `ActiveFlee`, `FleeRunStart`,
  `ActiveTerrorTriggered_*`, `ActiveHateTriggered_All`, `ActiveShowdownGiven_Distance`,
  `ActiveInitialPlayerThreat`, `ActiveGainInterrogationIntel`, `ActiveLevelUpPlayerLimitLevel`,
  `Ambush_Presented_BloodBro`, `ArcherPutsPlayerInLastChance`, reinicializações de missão
  (`CampRaid2_Clear`, `Chase_Clear`, `FeastSingle_Clear`, `Raid_Checkpoint_Clear`,
  `Trial_Clear`), configuração DLC3 (`DLC3_SlayerSetup`, `DLC3_MtnChiefSetup`,
  `DLC3_FakeDeadOverlord`); sessão 6 acrescenta `ActiveInterrogated`, `DatalLevelChanged`,
  `ActiveKillWarg`. Também `Debug_RecruitFollower` (34) e `DEBUG_AddPIS` (16) ao carregar em
  ambas (fluxo normal ou causado pelos canais de depuração: desconhecido).
  143 nomes distintos de capitães aparecem como Subject na sessão 5.
- **Morte de capitão, ao vivo (sessão 5):** `ActiveDominationStarted` -> 26 s depois
  `ActiveKilledByPlayer` -> `AddFactionEventReplay: BR_Single_Died` -> verificação de ressurreição
  (`Killed - Evaluating Resurrection Record 'Resurrection_HeadRemoved'; Attack:
  PC_Bip_Standing_InstaKill_Lvl2_B, TotalInteractionScore = 60`; sem registro de chance: permanece
  morto) -> `BrotherKilledByPlayer` para seu irmão de sangue. Segunda morte: registro
  `Resurrection_Executed`, registro de chance `Resurrection_3rdFew`, **`Chance to resurrect:
  0.100000, roll 0.904506 = Remain Dead`**.
- **Promoções:** 72 s após a segunda morte, `PromoteDead_Builder` (Faction_MtnPass):
  `Promote; Subject = <winner>; Other = <dead>`, `Loser (...) Vacating their position 4, 7`,
  `Winner (...) moving into position 4, 7`. Cinco segundos depois, rajada de simulações
  `PromoteEmpty_BuilderWC` / `PromoteEmpty_Builder_Transform` em
  Faction_desert preenche ~9 posições vazias (`moving into position <row>, <col>`).
- **Reproduções de eventos** (`SIMEVENT|REPLAY`): `BR_Promo_FromSystem` (13), `BR_TimePassed` (8),
  `BR_Single_Died` (2), `BR_TimePassed_CreatePromotions` (2), `BR_Single_Succeed` (2):
  presumivelmente os dados das telas "enquanto você estava fora" do jogo.
- **Regiões (facções):** Faction_MtnPass, _MinasIthil, _Demovolcano, _volcano, _snowMtn,
  _desert_Real, _island, _desert, _desert_mercs_DLC e variantes `_DLC` de seis delas.
  Capitães ocupam posições endereçadas como (linha, coluna) na hierarquia de uma região.
- **Tarefas e SimEvents:** `[QUEST|JOB] Process Job: <job>` com motivos de rejeição (`Random Roll`,
  `PlayerFollower predicate`, `has disabled simevents`, `PrisonerIfFollower predicate`);
  tarefas como `Relationship_Nemesis`, `Relationship_BloodBrother_SpawnIn`,
  `PS_Subject_Cap_Feast`, `PS_Other_Cap_GuardWarCouncil`, `SC_DeathThreat`.
  `[SIMEVENT] Evaluating Event: <event>` (`Challenge_DT`, `FeastSingle_Revenge`,
  `Guard_WarCouncil_Revenge`, `SpyGuardBetrayal`, `Rescue`, `Feast`, `Location`...),
  `Passed` / `Rejected, Unable to find Participant for Required Job ...` /
  `Simulate - <event> (<faction>)`.
- **Missões Nemesis são quests:** `qFeastSingle_*`, `qCampRaid_*`, `qChase_*`, `qGuardWC_*`,
  `qGauntlet_*`, `qFortDefense`, `qspSotP_*`, com estados de máquina `Inactive_OnEnter`
  (773), `SimEventEval_OnEnter` (89), `PreActivate_OnEnter` (89), `Cleanup_OnEnter` (17), e
  `Turning ON quest trigger ...` / `NavMarkerType`.
- **Emboscadas** dependem de chance, com intervalos e adiamento: `(Deferred) Attempting to
  trigger Ambush: <record>`, `Deferring Ambush ... for 7.241 minutes`, `Ignoring Ambush ...
  The faction has changed` / `... within a FactionAmbushDisableBrush`; registros como
  `PC_Damage_BloodBrother_Ambush`, `CheatDeath_FollowerStillLoyal`, `BruzBrothers_Daz_Ambush`,
  `AI_BecomeHighestLevelFollower_Betrayal`, `PC_LowHealth_*`, `PC_Showdown_Ambush`,
  `NewClass*`.
- **Fontes de câmera lenta** (`[SLOWMO] Start: <record>`): `HitCounterSlowMo`, `WraithMode`,
  `WraithDash_Slomo`, `Instakill_01_SM`, `Ranged_Aerial_SlowMo`, `ShadowStrike_SM`,
  `Kill_Decap_TrackHead_SM`, `Identify_Slowmo_Timestop_50_SM`, `Dom_Default_SM` /
  `Dom_UI_SM` / `Dom_Eye_Zoom_*` (dominação), `PreDeathAimStruggle_Faster` e outras;
  definidas por `SetCombatDynamicSlowMo` / `SetCombatWeaponModeSlowMo` /
  `SetPresentationSequenceSlowMo`.
- **Cronologia (sessão 6):** construção Nemesis de 2.500 linhas aos 8,6 s, com jogo ainda
  no menu principal; silêncio até carregar salvamento (~210 s); rajada de carregamento (propósitos,
  tribos, 1.900 avaliações de tarefas); depois, durante o jogo, principalmente linhas de saque, emboscada e câmera lenta.
  `FACTION|BUNDLE` vem em duas rajadas de ~11.500 linhas repetindo características, melhorias
  e conjuntos do soberano da fortaleza (não periódico).

### <a id="derived-for-co-op"></a>Derivado (para cooperativo)

- `HandleFactionEventAction(Event, Subject, Other)` é o hook óbvio para fluxo de eventos Nemesis
  do anfitrião; seu endereço pode ser encontrado pelo local de chamada da string de formato.
- Resultados são aleatórios (sorteio de ressurreição, "Random Roll" de tarefa, chances de emboscada, candidatos
  à promoção): cliente nunca deve realizar esses sorteios; recebe resultados do anfitrião
  (ou estado do mundo por `Faction.Save`/`Load`).
- Toda a lógica Nemesis/missão/emboscada executa em uma thread, simplificando
  pausa, hooks e ordenação de eventos.
- Câmera lenta vem de muitos registros (combate, espectro, mira, apresentação de dominação); cooperativo
  precisa de política por fonte (só apresentação local versus tempo do mundo).

### <a id="next-2"></a>Próximo passo

- Encontrar `HandleFactionEventAction` e funções de promoção/morte estaticamente por suas
  strings de formato; depois decidir o que sincronizar: fluxo de eventos ou estado de `Faction.Save`.

## <a id="session-2026-10-20-r-nemesis-event-death-and-promotion-functions-located-static"></a>Sessão 2026-10-20 r: funções de evento, morte e promoção Nemesis localizadas (estático)

Método (somente leitura, executável; `.arch` idêntico na memória, ver sessão k): encontrar cada
string de formato de log, encontrar referências `lea/mov` relativas a RIP para ela em `.arch`, mapeá-las a
funções por `.pdata` (seguindo entradas encadeadas de desenrolamento), desmontar com
`dumpbin /disasm`, encontrar chamadores (E8/E9 rel32), com pequeno script próprio.
Assinaturas: construídas pela desmontagem com curingas apenas para alvos rel32 de
chamadas/saltos e disp32 relativos a RIP, ampliadas até corresponderem
**exatamente uma vez** em `.arch` (conferido pela ferramenta). Build: Steam 3095001, SHA-256 do executável
`ed0d95ca...0bdaef`, base da imagem 0x140000000.

### <a id="functions"></a>Funções

| RVA (faixa) | nome usado | evidência | protótipo (derivado do uso de registradores) | assinatura única |
|---|---|---|---|---|
| `40C304`-`40C8F3` | **HandleFactionEventAction** | única referência a `"HandleFactionEventAction: Event = %s; Subject = %s; Other = %s"` (1FDD3A8), também a `"Loser (%s) Vacating their position %d, %d, (Event = %s)"` e `"Winner (%s) moving into position %d, %d (Event = %s)"`: **promoções são aplicadas dentro deste tratador** | `void (Mgr* this /*rcx*/, const FactionEventAction* a /*rdx*/)`; `a+0x00` referência subject, `a+0x10` referência other (referências de 16 bytes), `a+0x20` registro de evento, `a+0x56`/`a+0x57` dois sinalizadores; chamador ignora rax | `48 89 5C 24 08 48 89 6C 24 18 48 89 74 24 20 57 41 54 41 55 41 56 41 57 48 83 EC 70 4C 8B FA` |
| `62E670`-`62EA4D` | ApplyFactionEventOutcome (chamador) | único chamador de 40C304 (em 62E8B4) e um chamador de 741284 (em 62E95D) | `(Mgr* this /*rcx*/, const FactionEventAction* a /*rdx*/, ...)`; resolve subject e other da mesma forma | `48 89 5C 24 18 48 89 6C 24 20 56 57 41 54 41 56 41 57 48 81 EC 80 00 00 00` |
| `6DB95C`-`6DBCD2` | OnMemberKilled_EvaluateResurrection | única referência a `"%s: Killed - Evaluating Resurrection Record '%s'; Attack: %s, TotalInteractionScore = %d"`; 4 chamadores (4A066D, 17C05E1, 17C0869, 17C098E) | `(FactionMember* dead /*rcx*/, Record* attack /*rdx*/, ? /*r8*/, bool /*r9b*/)`; escolhe registro de ressurreição, armazena em `dead+0x2C0`, chama 6DBD4C | `48 8B C4 48 89 58 08 48 89 70 10 48 89 78 18 4C 89 60 20 55 41 56 41 57 48 8D 68 A1 48 81 EC A0 00 00 00 4C 8B F2` |
| `6DBD4C`-`6DC157` | RollResurrection | referencia `"%s: Resurrection Table Record: %s"` e `"%s: Chance to resurrect: %f, roll %f = %s"` (strings de resultado `"Remain Dead"` / `"EPIC WIN (set to Resurrect)"`); chamada por 6DB95C e 1BBA058 | `bool (FactionMember* m /*rcx*/, Record* resurrection /*rdx*/)`; `chance = 6DC504(rec)`, `roll = RandomFloat(1.0)`, ressuscita se `chance > roll`; lê `m+0x228` | `48 89 5C 24 10 48 89 74 24 20 55 57 41 54 41 56 41 57 48 8B EC 48 83 EC 60 48 8B 99 28 02 00 00` |
| `622A84`-`622BCD` | SimEvent::Simulate | única referência a `"Simulate - %s (%s)"`; 11 chamadores | `(SimEvent* this /*rcx*/)`; `this+0x48` registro SimEvent, `this+0x40` registro de facção; confere o próprio sinalizador de canal 2A34DAE | `48 89 5C 24 08 57 48 83 EC 20 80 3D ? ? ? ? 00 48 8B D9 74 2B` |
| `741284`-`741580` | AddFactionEventReplay | única referência a `"------------------AddFactionEventReplay: %s------..."`; chamadores 62E95D, 1C1DA72 | `(this /*rcx*/, rdx, r8, r9, stack arg 5 (tested for null), ...)`: pelo menos 5 argumentos, 7 passados em 62E95D | `48 8B C4 48 89 58 08 48 89 70 10 48 89 78 20 4C 89 40 18 55 41 56 41 57 48 8D 68 B9` |
| `1B3C6C`-`1B3C96` | RandomFloat | usada para sorteio de ressurreição; 85 chamadores | `float (float max /*xmm0*/)` = `(Rng() & 0xFFFFFF) * 2^-24 * max` | `48 83 EC 28 0F 28 C8 E8 ? ? ? ?` |
| `1807908` (folha, sem .pdata) | Rng (LCG global) | chamadores: só RandomFloat e 426840 | `uint32 ()`: `state = state * 0x0BB38435 + 0x3619636B; return state >> 32`; **estado: 8 bytes em RVA `2A25C88`** (em .bss) | (bytes de instrução: `48 69 05 ? ? ? ? 35 84 B3 0B 48 05 6B 63 19 36`) |
| `18DDCC` (folha) | LookupFactionMember | 5 chamadores, incluindo 40C326/40C335 | `FactionMember* (this /*rcx*/, const MemberRef* r /*rdx*/)`: id = `*(uint32*)(r+8)`, tabela em `this+0x20` | `8B 52 08 E9 ? ? ? ? 48 8B 49 20` |
| `18BDB0` (folha) | RecordName | 2.214 chamadores | `const char* (Record* r /*rcx*/)`: null se `!r` ou `!(r[1] & 2)`, senão `[r+0x20]` ou `""`; toca só rax e sinalizadores | `48 85 C9 74 18 F6 41 01 02 74 12 48 8B 41 20` |

Dados: `FactionMember+0x498` nome embutido (char[]); `FactionMember+0x2C0` registro
de ressurreição escolhido; `"None"` (1DB4ED8) é o nome usado para subject/other ausente.

### <a id="observations-worth-keeping"></a>Observações a guardar

- **Mais chamadores dependem de registradores voláteis durante chamadas a funções-folha minúsculas** (padrão
  que fez o hook v1 falhar): durante `RecordName` (18BDB0) em 40C380 (rdx, r9), em
  6DBBE0/6DBBEB (r10, rdx), em 622A9E (r9); e durante impressão de depuração em 6DC12E (r10).
  Qualquer hook nessas funções deve preservar cada registrador preservado por elas.
- **O `rand` desses resultados é um LCG global com 8 bytes de estado** (RVA
  `2A25C88`), acessado por RandomFloat. Só duas funções o chamam diretamente; outras
  fontes aleatórias podem existir em outros lugares (não conferido).

### <a id="derived-for-co-op-1"></a>Derivado (para cooperativo)

- Pontos de hook para fluxo Nemesis do anfitrião: `HandleFactionEventAction`
  (40C304) vê cada evento aplicado, incluindo promoções; `OnMemberKilled_EvaluateResurrection`
  e `RollResurrection` decidem mortes; `SimEvent::Simulate` cobre simulação
  fora da tela; `AddFactionEventReplay`, dados de "enquanto você estava fora".
- Cliente não deve chamar `RollResurrection` (ou `Rng`) para resultados compartilhados; aplica
  os resultados do anfitrião. Separadamente: estado LCG único pode tornar execuções de QA reproduzíveis
  (defini-lo antes de um cenário) e ser sincronizado para sequências determinísticas curtas.
- Protótipos vêm só do uso de registradores; significados de campos de estruturas além dos listados são
  desconhecidos.

## <a id="session-2026-10-20-s-located-functions-confirmed-in-the-running-game-read-only"></a>Sessão 2026-10-20 s: funções localizadas confirmadas no jogo em execução (somente leitura)

- Executado com `probe_write=0` e `hook_debug_print=0` (nada no código do jogo modificado;
  proteções de arquivo/rede/Steam ativas), jogo deixado no menu principal, script pelos
  comandos somente leitura da sonda.
- Todas as nove assinaturas da sessão r correspondem **exatamente uma vez** no jogo em execução, no
  RVA encontrado no arquivo, e os 64 bytes ativos em cada uma são iguais ao arquivo: HandleFactionEventAction
  40C304, ApplyFactionEventOutcome 62E670, OnMemberKilled_EvaluateResurrection 6DB95C,
  RollResurrection 6DBD4C, SimEvent::Simulate 622A84, AddFactionEventReplay 741284,
  RandomFloat 1B3C6C, LookupFactionMember 18DDCC, RecordName 18BDB0. Stub de impressão de depuração
  19C83AC sem patch (12 bytes originais).
- **Correção da sessão r:** passo LCG (`48 69 05 ? ? ? ? 35 84 B3 0B 48 05 6B 63 19 36`)
  ocorre **duas vezes** em `.arch`: função `Rng` em 1807908 e uma cópia embutida em parte
  fria da função FC0770 (em FC0E93). Ambas usam o mesmo estado em 2A25C88, então continua
  um estado RNG global, mas também avança por código embutido, não só pelos dois
  chamadores de `Rng`. Localizar `Rng` como alvo da chamada de RandomFloat (`rip RandomFloat+7, 1, 5`);
  verificado ao vivo: 1807908.
- Estado RNG em 2A25C88 lido duas vezes com 5 s de intervalo no menu principal: intacto
  (`33A3E99A5479618B`): nenhum sorteio aleatório no menu, então o passo LCG em si não foi
  observado ao vivo (precisa de sessão de jogo).
- Proteção de armazenamento remoto Steam ativa aos 359 ms. Jogo parado após a verificação
  (saída 0xFFFFFFFF, forçada); verificação do backup intacta; configuração da cópia de teste restaurada.

## <a id="session-2026-10-20-t-is-the-lithtech-clientserver-split-real-at-runtime-static-read-only"></a>Sessão 2026-10-20 t: a divisão cliente/servidor LithTech é real em execução? (estático, somente leitura)

Método: strings e suas referências de código, referências a entradas do registro, vtables e
código que as instala, cadeias de chamadas até a entrada do programa. Só arquivo executável
(`.arch` idêntico na memória). Ferramentas: scripts pequenos próprios.

### <a id="observations-6"></a>Observações

- **Nenhum protocolo cliente/servidor LithTech no binário:** sem strings `ILTServer`, `ILTClient`,
  `CAutoMessage`, `ILTMessage`, IDs de mensagem `MID_*` ou "ServerMgr". Nomes RTTI
  só existem para Havok, SDK `hydra` WB e std.
- **"GameServerShell" é código do cliente.** `GameServerShell.DebugPause` (tratador 177658C)
  lê global GameClient (`26FFA98`, ponteiro do freecam) e muda sinalizadores de pausa
  em `GameClient+0xE90`; `GameServerShell.PrintPauseFlags` (17762C) é `ret 0`;
  `ResetWorldIdentical` / `AdvanceTimeOfDay` passam pelos globais vizinhos do cliente
  `26FFAB0` / `26FFAA8` para código WorldSimSession (`178xxxx`). Todos definidos em
  `Game\ClientShellDLL\` (GameClientShell.cpp, WorldSimSession.cpp).
- **Configurações multijogador existem, mas nada as lê.** Variáveis do registro `LANOnly`
  (bool, 1), `publicserver` (bool, 1), `password` (string), `NetMeshGamePort` (int, 1032),
  `Net.NSM.HostVote.Timeout` (15000), `Net.NSM.HostVote.PauseInStart` (2000) são cada uma
  referenciadas por exatamente duas funções: registro (perto de `AFxxx`) e
  remoção do registro (perto de `1065xxx`/`1069xxx`), tocando só registro e seus elos
  da lista; nenhum código lê seu valor (`+0x38`), e suas strings de nome não têm referências
  de código. Controle: `Physics.Client.PhysicsUpdateRate` *é* lida (1A8C80 em 1A864C).
- **Uma "NetMesh" entre pares com host/join está compilada no jogo** (perto de `119F000`-`11A2000`):
  strings `HostMesh() should only be called when the mesh is disconnected`, `JoinMesh() ...`,
  `SendJoinRequest() should only be called when we're joining`, `Attempt to add NetNode
  with invalid ID / 'All' ID / duplicate ID / duplicate endpoint`, `WriteMessage called
  with an improperly-matched message class`, `DetermineNewHost: Using matchmaking system
  **NOT IMPLEMENTED**`. Objeto NetMesh: vtables `22C1128` + `22C1170` (herança
  múltipla), construtor `119F92C`, destrutor `119FB98`; HostMesh `11A0F5C` e
  JoinMesh `11A1218` são virtuais (sem chamadores diretos); DetermineNewHost `11A0394` virtual.
  Vtable da máquina de estados de rede de votação de anfitrião `1E700A0` (instalada por `11D0094`); vtables
  de classes de mensagens `22BFA60` / `22BFB00`.
- **O único criador de NetMesh é `118056C`,** posição 18 da vtable em
  `1E6AEC0` (classe semelhante a gerenciador de rede; construtor `117F8B0`, destrutor `117FE68`).
  Construtores de votação de anfitrião e classes de mensagens só são alcançados pelas próprias funções
  virtuais da NetMesh.
- **Gerenciador de rede é construído a cada início:** `117F8B0` <- `1178778` <-
  `1178D80` (início do motor; referencia `-cmdfile ..\cmdline.txt`) <- `11725C4` <-
  `8C3E5C` <- `8C3FC8`, entrada do programa MSVC (`sub rsp,28h; call
  __security_init_cookie; jmp __scrt_common_main_seh`), ou seja, ponto de entrada original
  por trás de SteamStub.
- Outro código de rede pertence a outros lugares: websockets em tempo real hydra (`RealtimeWebsocketConnection`,
  `ServerDisconnectMessage`, `PlayerDisconnectedMessage`, libwebsockets) para serviço
  online WB; strings de pareamento são para invasões (`invasion_matchmaking`,
  `InvasionSelfMatchmaking`: Online Conquest); `common.base.network.bsdsocket` é socket
  de depuração remota Havok (`hk2016...\hkBsdSocket.cpp`).
- Suporte a lockstep existe: `FrameUpdateLock.Enable` ("the game will update with a fixed
  frame time") e `FrameUpdateLock.TimeMS` ("milliseconds to lockstep frame updates").
- Modos de jogo são modos de conteúdo orientados por dados (`GameModes/Session`, pontuação, moeda,
  progressão), não modos de rede.

### <a id="derived-verdict"></a>Derivado (veredito)

- **A divisão cliente/servidor LithTech não é uma divisão em execução em Shadow of War.** Os
  comandos de "server shell" operam em singletons do cliente; há um processo, um
  mundo (WorldSimSession dentro de client shell), e nenhum protocolo de mensagens LithTech. Um
  segundo jogador não pode simplesmente se conectar ao "servidor" do anfitrião como no cooperativo F.E.A.R./NOLF2.
- **Uma malha genérica entre pares (NetMesh: hospedar, entrar, nós, mensagens, votação de anfitrião) sobrevive** no
  binário, e seu gerenciador é criado no início, mas nada no jogo lê as configurações
  multijogador que conduziriam a hospedagem, e não existe caminho não virtual para
  HostMesh/JoinMesh. Provavelmente uma camada de rede do motor que o jogo nunca
  usa (ou mantida para recursos não lançados). Ainda poderia ser transporte conduzido por
  nós; desconhecido se é completo o suficiente (criptografia, NAT, confiabilidade).
- Consequência para o projeto: **construir sincronização própria sob autoridade do anfitrião** (estado por
  `Faction.Save`/`Load` e hooks de eventos da sessão r, transporte próprio como
  rede Steam), com NetMesh como opção a avaliar depois, não uma base.

### <a id="unknown"></a>Em aberto

- Se a posição 18 do gerenciador (criar NetMesh) é chamada em execução: é chamada
  virtual, não resolvível estaticamente aqui. Verificação em execução (somente leitura): registrar requisições AFD de bind /
  conexão e ponteiro mesh do gerenciador durante sessão (`net_trace=1`).
- Se a camada NetMesh é completa e utilizável como transporte.
## <a id="sessions-2026-10-20-u-to-2026-10-21-w-a-second-test-copy"></a>Sessões 2026-10-20 u a 2026-10-21 w: uma segunda cópia de teste

- Cópia B usa links físicos para tudo fora de `x64\` apontando à cópia A (893 arquivos, arquivos de recursos e `game\`;
  jogo não gravou nada ali em sete inicializações) e tem cópias reais dos 10 arquivos em
  `x64\` (executável, DLLs, proxy e sua configuração). Hash do executável igual ao de A. Uso em disco: ~0,12 GB.
- Cada cópia tem perfil isolado e pipe de sonda próprios; as janelas ficam lado a lado
  pelas chaves `ScreenX`, `ScreenY`, `WindowWidth`,
  `WindowHeight`, `Windowed` do `render.cfg` isolado. A primeira inicialização completa de uma cópia gravou `"Windowed" "2.000000"` (uma
  janela 1920x1080 em 0,0); redefinir para `1.000000` no ambiente isolado dessa cópia.
- Uma segunda cópia iniciada junto da primeira para na ativação online do jogo e depois na
  verificação de instância única. Como as cópias de teste passaram por ambas foi omitido deste
  relato: o hub não publica contornos de DRM ou verificações de inicialização. Da sessão x em diante, duas
  cópias rodaram lado a lado em um PC, offline.

## <a id="session-2026-10-21-x-achievements-blocked-both-copies-in-the-world-same-save-see-y"></a>Sessão 2026-10-21 x: conquistas bloqueadas; ambas as cópias no mundo (mesmo salvamento, ver y)

> Correção (sessão y): ambas carregaram aqui o mesmo salvamento, a cópia da nuvem que Steam
> atende pela pasta Steam real (salvamento de 2025-11-20), não seus salvamentos isolados. Seus
> resultados só diferem pelo jogo após carregar. A observação sobre estatísticas permanece válida.

### <a id="change"></a>Alteração

- Proteção Steam agora também substitui os métodos de gravação de `ISteamUserStats` do jogo
  (`STEAMUSERSTATS_INTERFACE_VERSION011`, de `ISteamClient`, posição 0x68). Deslocamentos dos
  wrappers planos de `steam_api64.dll` distribuído: `SetStat0` (float) 0x18, `SetStat`
  (int32) 0x20, `UpdateAvgRateStat` 0x28, `SetAchievement` 0x38, `ClearAchievement`
  0x40, `StoreStats` 0x50, `IndicateAchievementProgress` 0x68, `ResetAllStats` 0xA8,
  `UploadLeaderboardScore` 0xF8, `AttachLeaderboardUGC` 0x100. Leituras passam (por exemplo,
  `GetAchievement` 0x30). Wrapper de `UploadLeaderboardScore` usa
  `mov r10,[rcx]; jmp [r10+0xF8]` em vez de rax; verificação de formato aceita ambos.
- Após esta inicialização, conquistas receberam limite próprio de log (estatísticas consumiam a maior parte
  do compartilhado).

### <a id="setup"></a>Preparação

- Cópia A: salvamento isolado próprio, descendente do de 2025-11-20 mais ~20 min
  de jogo de teste anterior (sessões n e p, dois capitães mortos).
- Cópia B: os seis salvamentos do backup, copiados intactos (hashes iguais); Continue
  carrega o salvamento de 2025-11-20.
- Ambas offline; A com hook de impressão de depuração (22 canais), B
  com sonda somente leitura.

### <a id="observations-7"></a>Observações

- Cada cópia carregou seu salvamento e foi jogada manualmente em sequência; paradas após
  575 s (A) e 558 s (B). Ambas ~2,3 GB, respondendo, sem falha, sem linha FATAL, PROTECTED ou
  WATCH em qualquer log.
- Salvamentos: 6 `FileWrite`s bloqueados em A (primeiro em +122,8 s), 11 em B (primeiro em +296 s);
  arquivos foram ao ambiente isolado próprio de cada cópia com rotação usual das posições. Depois, a
  posição 2 de A é seu salvamento próprio anterior e a de B é o de 2025-11-20, então cada uma
  continuou dos próprios dados. Salvamentos principais finais diferem (A `4EF1832137F0...`, B
  `582CAA5553A6...`).
- Proteção de estatísticas ativa aos 359 ms (A) e 437 ms (B). Ao carregar, cada cópia chamou `SetStat`
  para 137 estatísticas (`kills`, `killed_captains`, `game_time_played`, ...); o primeiro valor
  de toda estatística era **igual em A e B** (137 de 137), embora os salvamentos difiram.
  Durante o jogo algumas mudaram (`kills` 9 vezes em A). `StoreStats` 3 vezes (A) e 4
  vezes (B). Tudo bloqueado. Nenhuma chamada a `SetAchievement`, progresso ou placar.
- Rede: mesmos dois hosts HTTPS recusados em +55-64 s e de novo 15 s depois; nada
  mais.
- Impressão de depuração de A: 21.787 linhas de +7,9 s a +207,8 s, depois silêncio até
  parar. `[GAMEMODE|SESSION]: Load:` em +62,8 s. Categorias: `FACTION|BUNDLE` 11.942,
  `QUEST|JOB` 2.907 (818 tarefas rejeitadas por "Random Roll"), `FACTION|TRIBE` 2.168,
  `FACTION|PURPOSE` 2.160, `SIMEVENT|OUTCOME` 1.075 (`HandleFactionEventAction`: 916
  `FactionMember_RoleSelected_Standard`, 51 `_Notable`, 45 `IsPlayerFollowerApply`, 26
  `Debug_RecruitFollower`, 12 `DEBUG_AddPIS`, ...).
- Verificação de backup após parar: intacto (render.cfg só informação).

### <a id="derived-6"></a>Derivado

- Duas cópias podem executar cada uma um salvamento diferente no mundo simultaneamente em um PC e
  uma conta Steam. Nenhuma afetou a outra: ambientes e salvamentos separados, e as partes
  compartilhadas (nuvem e estatísticas Steam) bloqueadas em ambas. As cópias ainda não conversam
  entre si, então isso mostra independência, não como o cooperativo lida com dois mundos
  diferentes.
- Estatísticas Steam pertencem à conta, não ao salvamento: ambas começaram com os mesmos
  valores. Duas cópias desbloqueadas enviariam cada uma seus incrementos à mesma conta.
  Sessões de teste anteriores a este bloqueio enviaram atualizações de estatísticas sem bloqueio; provavelmente
  chegaram à conta (não registradas então, por isso desconhecido quais).
- Salvamento de jogador que entra difere do do anfitrião, como aqui. Com sincronização sob autoridade
  do anfitrião (sessão t), o cliente joga no mundo dele; se seu próprio salvamento
  permanece intacto durante a conexão e o que mantém depois são decisões de projeto.
- Só carregar faz centenas de sorteios na seleção de tarefas Nemesis, então até o
  mesmo salvamento carregado duas vezes divergiria sem sincronizar resultados (um LCG global,
  sessão r).

## <a id="session-2026-10-21-y-unattended-loading-the-game-loads-its-save-from-the-steam-cloud"></a>Sessão 2026-10-21 y: carregamento sem supervisão; jogo carrega salvamento da nuvem Steam

### <a id="observations-static"></a>Observações (estáticas)

- Caminho do menu (visto ao carregar salvamentos manualmente): título "press any key",
  depois lista de campanhas. Um controle real conduziu ambas as cópias de uma vez, então jogo lê
  XInput mesmo sem foco na janela.
- Registro de console: `PlayerInput.SetSimInput` "Runs the listed commands in order, once
  per frame" (comandos de menu `MenuEnter`, `MenuEscape`, `MenuUp`/`Down`/`Left`/`Right`,
  `MessageBoxConfirm`, ...); opções de linha de comando `SkipSplashScreens`,
  `MenuUI.SkipUserConfig`, `runworld`.
- Linha de comando: sem argumentos, motor lê `..\cmdline.txt` (relativo a `x64\`).
  Analisador (`117DE6C`) executa `+Name arg arg` como linha de console `(Name) (arg) (arg)`
  por `1182FA4`, no início do motor (`117CF30`). Tratador de `SetSimInput` (`17B880C`)
  não faz nada enquanto `GameClient+0x888` (entrada do jogador) é nulo, como está tão cedo.
  Não usado.
- APIs de entrada nomeadas na tabela de importações: `RegisterRawInputDevices`/`GetRawInputData`
  (teclado e mouse usam Raw Input, então mensagens de teclas postadas não chegariam ao jogo),
  `XInputGetState`/`XInputSetState` de `XINPUT9_1_0.dll`, `GetActiveWindow`,
  `GetForegroundWindow`.
- Nenhum canal de impressão de depuração informa telas do menu. Dois marcadores: `[GAMEMODE|SESSION]: Load:`
  quando salvamento da campanha foi lido, `[QUESTMGR]: GameModeSet - SinglePlayer` quando
  mundo inicia.

### <a id="change-1"></a>Alteração

- `autoload=1`: controle virtual no usuário XInput 0. Proteção encontra a posição de
  `XInputGetState` do jogo na tabela de importações reconstruída (RVA `1D93098`, início de `.xtext`,
  preenchida ~190 ms após iniciar) e aponta para função própria, que acrescenta pressionamentos de A ao
  que um controle real informa. Começam 20 s após a janela aparecer, depois
  a cada 8 s, até `GameModeSet` (ou 8 pressionamentos).
- `steam_cloud=sandbox`: leituras e gravações de nuvem do jogo vão para
  `steam-userdata\356190\remote\` da cópia (motivo abaixo). `steam_trace=1` registra leituras atendidas
  por Steam.

### <a id="observations-launches-all-unattended"></a>Observações (inicializações, todas sem supervisão)

- Cópia A sozinha, controle parando em `Load:`, `steam_trace=1`: pressionamentos em +23,5 s e
  +31,7 s; logo após o segundo, `GetFileSize('\<prefix>_ShadowOfWar.sav') -> 2334736`
  e `FileRead(...) -> 2334736 of 2334736 bytes`, depois `Load:`. Nenhum `.sav` local
  tocado antes do primeiro salvamento automático, aqui e na sessão x. 2.334.736 bytes é o tamanho do
  salvamento de 2025-11-20 em `remote\` da pasta Steam real; salvamento isolado de A tem
  2.360.880 bytes. Jogo depois ficou no tamanho de menu (~1,25 GB) por 80 s: mais uma tela
  quer entrada.
- Cópia A sozinha, controle parando em `GameModeSet`, nuvem isolada preparada com último salvamento
  próprio de A: pressionamentos em +23,4, +31,6, +39,8 e +48,0 s; `FileRead` isolado de 2.360.880 bytes
  após pressionamento 2; `GameModeSet - SinglePlayer` em ~47,6 s; 2,06 GB aos 76 s.
- Cópia B iniciada enquanto A estava no mundo, mesmas configurações, nuvem isolada preparada com
  salvamento de 2025-11-17 (posição `_2_` do backup): quatro pressionamentos, `FileRead` isolado de 2.328.976
  bytes, mundo iniciado aos 48,1 s, 2,11 GB.
- Ambas no mundo por 90 s sem entrada: ambas respondendo, CPU +73 s (A) e +100 s
  (B), estatísticas bloqueadas ao carregar (137 e 136), nenhuma chamada de conquista, nenhuma linha FATAL ou PROTECTED.
  Sem salvamento automático (ninguém jogou), então arquivos da nuvem intactos. Paradas após 283 s
  (A) e 193 s (B). Verificação do backup: intacto.

### <a id="derived-7"></a>Derivado

- **Correção das sessões j, n, p e x:** jogo nunca carregou salvamentos locais
  isolados. Carrega por `ISteamRemoteStorage::FileRead`, atendido por `steam.exe` pela
  pasta Steam real, então toda cópia de teste até agora carregou a cópia real da nuvem (só leitura;
  nada ali mudou). Arquivos `.sav` locais são gravados, mas não são o que o jogo carrega.
- Com `steam_cloud=sandbox`, cada cópia carrega e mantém salvamento próprio; com controle, uma cópia
  de teste vai da inicialização ao mundo em ~48 s sem teclado, mouse ou foco.

### <a id="unknown-1"></a>Em aberto

- A quais telas os pressionamentos 3 e 4 respondem (não visto).
- Caminho de gravação da nuvem isolada no jogo real: nenhum salvamento automático ocorreu (coberto só pelo
  teste offline).

## <a id="session-2026-10-21-z-the-player-character-in-memory-each-copy-saves-to-its-own-cloud"></a>Sessão 2026-10-21 z: personagem do jogador na memória; cada cópia salva na própria nuvem

### <a id="observations-static-1"></a>Observações (estáticas)

- `Teleport` (tratador de console `19C052C`, "Teleports player to <x><y><z>") obtém o
  jogador como `[[GameClient]+0x888]` (ponteiro GameClient em RVA `26FFA98`), lê a
  posição atual como três floats em `+0xAC` e passa `+0xB8` como rotação ao
  construir o novo transform. `Player.SetOrientation` (`19BFA70`) converte ângulos em
  quaternion (`114A1C0`) e grava por `EF690`/`1152DE4` no mesmo objeto.
  `Player.GetPos` e `Player.GetOrientation` ficam na seção Denuvo (`.bss`), não
  legível.
- Tratador de dano `2E4BE8` (onde fica o padrão de vida de ReaperAnon, gravação em `2E4D26`)
  mantém vida máxima em `+0x428`, vida em `+0x42C`, vida/máxima em `+0x430`, sinalizador de morte
  em `+0x4A0`. Métodos Player junto de `Teleport` (`19B39E4`, `19B3EE0`) o chamam com
  `[player+0x26A8]`.
- `Player.Save` (`19C0984`, 33 bytes) chama `42D9A8(player)`, que (se sinalizador global em
  `2672D91` estiver ativo e `player+0x3879` estiver limpo) arma temporizador em `player+0x3850` com
  0,5 s (`FF0B4`: hora inicial, duração, campo limpo, sinalizador de execução).

### <a id="change-2"></a>Alteração

- Sonda `player` (somente leitura): posição, rotação, vida, máxima, fração por essa cadeia.
- Sonda `pad <buttons> <lx> <ly> <rx> <ry> <ms>`: manter entrada de controle virtual (probe_write=1).
- Sonda `save`: após iniciar mundo, próxima leitura do controle executa `Player.Save` após
  conferir seus 33 bytes e referência GameClient (probe_write=1).

### <a id="observations-live-unattended-copies-a-and-b"></a>Observações (ao vivo, sem supervisão, cópias A e B)

- `player` em A: posição (23987.971, 43092.539, 12789.801), rotação
  (0, 0.9833, 0, 0.1822), vida 708 de 708, fração 1.000.
- Analógico esquerdo à frente por 2 s: posição (+48.4, 0, -86.9); analógico esquerdo à direita por 1,5 s: mais (-315.5,
  0, -69.0) e rotação (0, 0.7686, 0, -0.6397); 2 s após soltar, moveu mais 3
  unidades e parou. Coordenada central ficou 43092.539 o tempo todo.
- Cadeia de câmera do mod freecam (`GameClient+0x898`, `+0x50`, `+0x98`) levou a texto, não
  ponteiro, neste estado; não usada.
- Jogo lê controle em uma thread e registra início do mundo em outra (A: 20172
  e 27508 numa execução, 33432 e 21436 na próxima; B: 10564 e 24464). Todas as linhas de lógica do jogo
  vêm da segunda.
- Ambas as cópias no mundo; jogador de B em (-1801.088, 44902.633, 37119.199), rotação
  (0, 1, 0, 0), vida 708 de 708.
- `save` em A: tratador executou na thread do controle, `Player.Save returned`; 531 ms depois,
  jogo rotacionou posições locais de A e `sandbox cloud FileWrite('\<prefix>_ShadowOfWar.sav') ->
  2360880 bytes written`. Arquivo de nuvem de A mudou (novo hash); o de B não.
- `save` em B, 16 s depois: mesmo padrão 532 ms após solicitação, 2.360.512 bytes para
  nuvem de B (antes: arquivo de 2025-11-17, 2.328.976 bytes). A intacta.
- Nenhuma linha FATAL, PROTECTED ou WATCH. Verificação do backup após parar: intacto.

### <a id="derived-8"></a>Derivado

- Jogador: `[[GameClient]+0x888]`; posição float3 em `+0xAC` (Y é cima), rotação
  quaternion (x, y, z, w) em `+0xB8` (só guinada ao caminhar). Personagem para vida:
  `[player+0x26A8]`, vida `+0x42C`, máxima `+0x428`. Posição e rotação confirmadas por
  movimento; vida só por leitura consistente (708/708, fração 1,0), não por alteração.
- Cada cópia agora salva na própria pasta de nuvem; com caminho de carregamento da sessão y, cada
  cópia mantém progresso próprio entre execuções.
- `Player.Save` pela thread do controle: salvamento ocorre ~0,5 s depois no agendamento do próprio
  jogo, como sugere seu atraso.

### <a id="unknown-2"></a>Em aberto

- Unidades (analógico moveu jogador ~100 unidades em 2 s e ~320 em 1,5 s, provavelmente
  centímetros com aceleração, não conferido).
- Se vida muda como esperado quando jogador é atingido.

## <a id="session-2026-10-21-aa-first-co-op-step-copy-as-player-shown-in-copy-b"></a>Sessão 2026-10-21 aa: primeiro passo cooperativo, jogador da cópia A mostrado na cópia B

### <a id="observations-8"></a>Observações

- Remetente (A, somente leitura) envia posição, rotação e vida 20 vezes por segundo em pacotes UDP
  de 52 bytes para 127.0.0.1; B recebeu ~19,7/s, 0 perdidos, 0 inválidos (3.979 pacotes numa execução).
- B mostra A com o efeito de "última posição conhecida" do próprio jogo, `19C0380(player, &pos)`
  (o que console `TestLKP` chama), no máximo a cada 200 ms e após movimento de 25 unidades.
- Chamá-lo da thread do controle (entrada) fez B falhar: AV em `315D5D`, pois `1309FC`
  (contexto do motor por thread: TlsGetValue, depois global) é nulo ali. Chamadas que
  alocam precisam da thread de simulação.
- Sonda `count` na vtable do jogador (`1F96818`, 41 posições, 2 s): posições 18, 25 e 36 executam
  uma vez por quadro (58,5/s) na thread de simulação; posição 36 (`30BA10`, ~2,5 KB, 104 chamadas)
  é a atualização por quadro. Um pré-hook ali que preserva registradores executa o efeito; sem falha.
- Cópia sem foco pausa a si mesma (menu de pausa; posição e rotação do jogador então
  leem 0,0,0 e identidade; botão B do controle retomou). Com `background_run=1`
  (mensagens de perda de foco consumidas; `GetForegroundWindow`/`GetActiveWindow` retornam a
  janela da própria cópia; `ClipCursor`/`SetCursorPos` ignorados salvo quando realmente à frente), A continuou
  simulando (60 atualizações/s) e caminhou com analógico virtual enquanto B tinha foco.
- Ao vivo (ambas sem supervisão, mesmo salvamento): A caminhou ~100 unidades à frente, depois ~320 à direita; B redesenhou
  efeito pelo caminho e terminou na posição final de A; 277 redesenhos em caminhada
  de ida e volta de 90 s. Visto na tela de B: fantasma do jogador deslizando sem
  animação e aparecendo/desaparecendo, "decently matched up" com A.

### <a id="derived-9"></a>Derivado

- Transporte, amostragem e exibição funcionam de ponta a ponta num PC. Fantasma é o efeito LKP
  recriado a cada atualização (daí desaparecimento e ausência de animação); um jogador remoto real precisa de
  personagem-boneco conduzido por posição, rotação e estado de animação.

## <a id="session-2026-10-21-ab-a-real-character-as-the-remote-players-stand-in-puppet"></a>Sessão 2026-10-21 ab: personagem real como substituto do jogador remoto (boneco)

### <a id="observations-static-2"></a>Observações (estáticas)

- Nenhum comando de criação utilizável na build de lançamento: `Faction.CreateEmergencyPlayerFollower`
  é `ret 0` (`7F8F90`); `NemesisForge.CreateFollower`/`CreateNemesis` (`1C775EC`,
  `1C77604`) criam registro da forja por `[26FFAA8]+0x6D30`, não corpo no mundo.
- Movimento genérico de objeto: `EF690(object, &quat)` define rotação (`+0xB8`, 31 chamadores);
  `19B7AC4(object, &transform)` (onde `Teleport` termina) encaminha para `658CBC(manager
  [2A86880], object, transform, 1)`, que enfileira mensagem de teleporte (com horário
  de `[2702598]`) por `659884`; motor aplica depois. Transform tem 28
  bytes: posição (3 floats), depois quaternion (`1820FC` -> `182110`).

### <a id="observations-live-copy-b"></a>Observações (ao vivo, cópia B)

- Objeto de vida do jogador (`[player+0x26A8]`) tem vtable de classe `1F995E0`; seu `+0x28`
  é o dono (jogador). `findq` (nova busca de heap somente leitura) encontrou 2.108 objetos dessa
  classe; 22 tinham dono cujo `+0x26A8` aponta de volta: todos IA com vtable do dono
  `1FB3640`, vida de 180 a 600 (um 11.165), o mais próximo a 5.823 unidades do jogador.
- `coop_show=puppet`: B escolheu personagem vivo mais próximo (orc com 180 de vida a 8.606
  unidades), depois teleportou-o à posição e rotação de A a cada pacote pela
  thread de simulação. Chegou a até ~6 unidades (jogo o colocou algumas unidades abaixo,
  no chão) com rotação de A; em caminhada de 90 s, 2.540 movimentos, terminando a 4,3 unidades do
  jogador de A; ambas continuaram executando.
- Visto na tela enquanto cópia A era jogada manualmente: orc em B "moved the same, but
  it's a little laggy".
- Primeiras buscas de heap liam cada página privada confirmada e fizeram B crescer de ~2 GB para
  6,3 GB. Agora só leem páginas já no conjunto de trabalho (`QueryWorkingSetEx`):
  após escolha, B ficou em 2,27 GB. Ao iniciar mundo, uma escolha encontrou 0 personagens (2.074
  objetos de vida, nenhum com dono válido ainda); repetição 10 s depois encontrou 23.

### <a id="derived-10"></a>Derivado

- Personagem IA existente pode representar jogador remoto: o próprio teleporte enfileirado
  do jogo o move, e seu objeto de vida o identifica com segurança.
- Fontes de atraso: ~16-20 atualizações de posição por segundo (remetente dorme 50 ms com temporizador de ~15,6 ms),
  cada uma aplicada como teleporte um quadro depois, com IA própria do orc movendo-o
  no intervalo. Próximo: enviar na taxa de quadros do jogo e interpolar (ou extrapolar) na
  thread de simulação a cada quadro; depois parar IA própria do boneco e conduzir animação.
## <a id="session-2026-10-21-ac-smoother-puppet-a-packet-every-frame-interpolated"></a>Sessão 2026-10-21 ac: boneco mais suave (um pacote a cada quadro, interpolado)

### <a id="change-3"></a>Alteração

- Pacote versão 2 (60 bytes) acrescenta relógio do remetente (QPC, microssegundos).
- Remetente: após hook da thread de simulação executar, envia um pacote por quadro do jogo a partir
  dessa thread (callback de quadro antes do trabalho enfileirado). Antes disso, temporizador aguardável
  de alta resolução em `coop_rate_hz` (60) substitui o antigo `Sleep` de 50 ms.
- Receptor: mantém os últimos 128 pacotes e obtém deslocamento de relógio pelo menor
  tempo de recebimento menos envio (medido novamente a cada 10 s). A cada quadro, thread de simulação
  coloca o boneco onde remetente estava há `coop_delay_ms` (50): posição interpolada
  linearmente, rotação por lerp normalizado no arco mais curto, aplicada pelo mesmo
  teleporte enfileirado.
- Caso offline `coop_puppet`: thread de simulação fictícia faz remetente andar +0,5 unidade por quadro
  por 200 quadros; boneco precisa seguir em passos de no máximo 1 unidade, nunca para trás,
  e terminar onde remetente parou.

### <a id="observations-live-unattended-copies-a-and-b-both-background_run1"></a>Observações (ao vivo, sem supervisão, cópias A e B, ambas `background_run=1`)

- A registrou "sending once per game frame from the simulation thread"; B escolheu
  orc de 300 de vida e registrou "puppet moved every frame, 50 ms behind the sender".
- 58,8 pacotes por segundo, 0 perdidos (22.025 pacotes em ~6 min). Contagem de movimentos do boneco
  cresceu com a de pacotes (240 de cada por 4 s).
- A caminhou com analógico virtual (início, velocidade plena, parada); distância entre A e o
  orc de B:

  | Velocidade de A (unidades/s) | orc atrás de A (unidades) |
  |---|---|
  | 37 (iniciando) | 6.0 |
  | 155 | 11.9 |
  | 235 | 14.0 |
  | 0 (parado) | 0.0 |

- Conjunto de trabalho: A 2,12 GB, B 2,09 GB.
- A depois caminhou em circuito (direita 2,5 s, frente 1,5 s, esquerda 2,5 s, trás 1,5 s) por ~50
  minutos; após ~6 minutos permaneceu a até ~700 unidades do início.

### <a id="derived-11"></a>Derivado

- Em velocidade de caminhada, orc fica ~50-70 ms atrás de A: atraso de 50 ms mais cerca de um quadro
  (teleporte aplicado um quadro depois de enfileirado). Já não se move em 16-20
  passos por segundo.
- O que ainda parece errado pertence ao orc em si: IA e animação próprias continuam executando,
  então desliza em vez de caminhar. Próximo: parar IA, conduzir animação pela velocidade de A,
  depois modelo Talion.

### <a id="unknown-3"></a>Em aberto

- Aparência na tela (ainda não observada).
- Atraso e variação de rede reais: só loopback até agora; 50 ms escolhido para loopback.

## <a id="session-2026-10-21-ad-the-puppets-own-ai-off-its-walk-animation-driven-from-copy-a"></a>Sessão 2026-10-21 ad: IA própria do boneco desligada, animação de caminhada conduzida pela cópia A

### <a id="observations-static-build-3095001"></a>Observações (estáticas, build 3095001)

- Personagens IA (vtable de classe `1FB3640`): posição 36 (`175724`) é atualização por quadro
  (`count`: 1.112 chamadas/s, 19 personagens a 58,5 quadros/s). Preenche contexto por quadro
  e define **variáveis nomeadas de animação** em `character+0x120` por definidores: float
  `176D78`, bool `375044` (outros `4192B4`, `1BCF0D4`). Nomes têm hash sem distinção de maiúsculas
  (`h = h*0x397 + table[c]`, tabela em `1DB50D0`). Cerca de 80 nomes definidos por nome no código,
  entre eles `RawMoveMag`, `RawMoveYaw`, `Game_MovementAxisX/Y`, `AIDesiredWorldYaw`, `HasDest`,
  `DestX`, `DestZ`, `WalkAndTalkScale`.
- **Controlador de movimento** `[character+0x2C78]` (seu `+0` é o personagem): modo desejado
  `+0x68`, modo atual `+0x6C` (1 ir até solicitação, 2 ocioso, 3 conduzido por entrada de montaria,
  `UsingMountedInput`), solicitação em `+0x70` (0x25 bytes: byte de destino presente,
  destino x/y/z, direção x/z, tipo de movimento (1 andar, fator de velocidade 0,5; 2 correr, 1,0),
  distância, fator de velocidade, byte "direto" em `+0x24`). `SetMoveRequest` é `3F4BD8`; comportamentos
  de ir até ponto do jogo preenchem solicitação como acima com byte direto 0, o que
  também pede caminho ao navegador do personagem (`[character+0x2528]`, vfunc `+0x140`).
  `2F4274` atualiza cada controlador listado a cada quadro (`2F42C0`); modo 1 (`374CA0`)
  envia `HasDest`/`DestX`/`DestZ` às variáveis de animação.
- **Caminho de decisão IA** (encontrado ao vivo com novo comando de sonda `stacks`, abaixo):
  thread de simulação chama posição 18 da classe IA (`2F94F0`) -> `2F9478` -> posição 119
  (`+0x3B8`, `2F79A4`, tick IA) -> em `2F7B40`, `mov rcx,[r8]; xor edx,edx; call
  1919C8` executa árvore de comportamento do personagem (`[character+0x2D38]`, cujo `+8` é o
  personagem) -> ... -> `3F4A3C` (comportamento de perseguição) -> `SetMoveRequest`: 59 chamadas em 5 s,
  todas por essa cadeia. Código após chamada da árvore (`2F5EB4`) só lê
  `rdx`, então omitir a chamada é seguro.

### <a id="change-4"></a>Alteração

- `coop_puppet_ai=off`: chamada em `2F7B45` é apontada (bytes conferidos, patch pela
  thread de simulação) para salto a filtro que pula árvore cujo `+8` é o boneco.
  Árvore de todos os demais personagens executa como antes.
- `coop_puppet_move=both`: boneco continua teleportado a A a cada quadro, e seu
  controlador recebe solicitação de movimento do próprio jogo (destino meio segundo à frente no movimento
  de A, andar ou correr pela velocidade de A, `coop_run_speed` 300; ocioso quando A para).
  `coop_puppet_move=walk` move só com solicitações (teleportar quando ficar mais de
  `coop_teleport_dist`, 600, atrás).
- Sonda: `stacks <addr> <entry bytes> <ms> [first-argument qword]` registra pilhas de chamadas
  para uma função por alguns segundos (jmp na entrada, stub que preserva registradores com
  informações de desenrolamento, bytes substituídos relocados; restaurado depois). `teleport x y z` move jogador
  desta cópia. `puppet ai on|off`, `puppet walk x y z type [factor]`, `puppet idle`,
  `puppet follow walk|teleport|both|none`; `puppet` e `remote` mostram solicitações, estados ociosos,
  árvores puladas e modo do controlador.
- Quatro páginas de código ao alcance rel32 da imagem são reservadas no início: quando o
  mundo executa, heap do jogo preenche os 2 GB de cada lado da imagem (`stacks` falhou com
  "no free page" no segundo uso).
- Offline: 40 de 40 (`probe_stacks`: filtro pelo primeiro argumento, pilhas pelo stub,
  entrada restaurada; `coop_puppet_walk`: árvore do boneco nunca executa com IA desligada,
  a de outro personagem executa, volta após `puppet ai on`, solicitações de andar e depois correr miram
  à frente, ocioso no fim, preso ao remetente, `teleport` mantém rotação). Controle
  negativo 17 de 17 (com hooks removidos na compilação, árvore do boneco executou 159 vezes).

### <a id="observations-live-copies-a-and-b"></a>Observações (ao vivo, cópias A e B)

- IA desligada: boneco de B ficou em pose ociosa junto ao jogador de B e não atacou
  (captura); `tree_skips` subiu cerca de uma vez por quadro.
- `both`, A caminhando com analógico virtual (215-219 unidades/s): orc ficou 0-14 unidades
  atrás, controlador no modo 1 com solicitações de andar (~12/s), e voltou ao modo 2
  quando A parou (0 unidades atrás). Corrida que virou salto da plataforma
  (~550 unidades/s, depois queda de ~5.700 unidades): 25-40 unidades atrás, seguiu até o fim da queda.
- Visto na tela (`PrintWindow` da janela B, intervalo 150 ms, enquanto A caminhava): pernas do orc
  alternam na passada, braços balançam, poeira nos pés; fica ocioso quando A
  para.
- Só `walk`: orc anda a ~115-130 unidades/s (tipo 1) e corre a ~480 (tipo 2); uma
  solicitação de corrida terminou a até 3 unidades do alvo. Seguindo A, começou ~1,5 s atrasado,
  tomou caminho próprio pela malha de navegação a 150-180 unidades da linha de A e ficou 180-300 atrás. Depois,
  nas mesmas sessões, solicitações isoladas pararam de movê-lo por completo (modo 1, posição
  intacta com precisão de 0,1 unidade).
- Incidentes: `TaskStop` no ciclo de caminhada em segundo plano encerrou só wrapper bash; seu
  `sh.exe` continuou enviando entrada de analógico pela sonda à cópia A *reiniciada*, moveu
  menu inicial e carregou campanha DLC3 (`GameModeSet - DLC3`, outro herói, 430
  de vida), que salvou automaticamente no ambiente de A. Parar esse `sh.exe` e reiniciar A
  carregou de novo a campanha principal no ponto habitual. Ambas depois fecharam com código
  de saída 0 a poucos segundos uma da outra (17:11), nenhum erro de aplicativo registrado; causa
  desconhecida.

### <a id="derived-12"></a>Derivado

- Jogo já separa decidir (árvore de comportamento) de mover (controlador e
  navegador) e animar (variáveis nomeadas, depois movimento de raiz). Pular uma chamada para
  as decisões de um personagem apenas; solicitação de movimento faz a locomoção própria
  animar.
- Fixação mais solicitações ("both") dá posição exata de A com passada própria do orc; sozinho,
  navegador não consegue seguir jogador que anda onde orcs não traçam caminho.

### <a id="unknown-4"></a>Em aberto

- Deslizamento de pés: A anda a ~218 unidades/s, animação de caminhada do orc cobre ~120 e corrida
  ~480; se fator de velocidade da solicitação muda velocidade da passada não foi testado (orc
  de teste já não respondia a solicitações isoladas).
- Por que solicitações isoladas deixam de mover orc após algum tempo.
- O que orc faz com árvore pulada quando jogador de B o ataca ou quando é atingido.

## <a id="session-2026-10-21-ae-a-second-talion-in-copy-b-spawned-not-animated-yet"></a>Sessão 2026-10-21 ae: segundo Talion na cópia B (criado), ainda não animado

### <a id="observations-static-build-3095001-1"></a>Observações (estáticas, build 3095001)

- `Player.SetCharacterModelOverride <name>` (`19C0EFC`, tratadores recebem `(int argc, const
  char** argv)`) busca nome com `1B08BB0` e chama `19BF4B8(player, record, 0)`;
  `Player.ClearCharacterModelOverride` chama `19BB3CC(player, [player+0x2B30], 0)`. Ambos
  usam campos exclusivos do jogador (`+0x2EC8`..`+0x2EE0`): inutilizáveis em NPC.
- Registros são entradas de 40 bytes em tabelas por tipo (contagem `+0x28`, array `+0x38`): ID do tipo
  `+0`, hash de nome `+4` (`423E70`: `h = h*0x397 + table[c]`), nome `+0x20`. Duas tabelas
  compartilham muitos nomes: tipo `0xA66` (281 entradas, `[27018B8]`, o que `1B08BB0` busca) é a
  aparência do personagem (`[character+0x2B30]`: jogador veste
  `PlayerSkin_DarkTalion_ShadowWar`, orc `Orc_Infantry`); tipo `0xA06` (177 entradas)
  contém tipos de personagens criáveis. Personagem IA mantém seu tipo de criação em `+0x2E68`,
  cujo `+0x18` é essa tabela. Nomes incluem `AI_Talion`, `Talion`, `Dark_Talion`,
  `GP_Ranger`, `Gondorian_Soldier`.
- Criação (cadeia registrada ao vivo com `stacks` no construtor IA `49B858` e em
  `1036D0`, 16 criações em 20 s): conjuntos de geradores -> `1045EC` -> `1036D0(context
  [[26FFAB0]+0xF58], name, &transform (position, quaternion), spawn-type record, 1, 1, 0,
  0, 0)` -> `1038F0` -> fábrica de objetos. Solicitações enfileiradas de criação do jogo (`1A9290C` e
  vizinhas) depois armazenam região (`[obj+0x26F0] = 168DA8(obj, 0, 0)`) e área
  (`35DC38(obj, 607610(obj, 0, 0), 0)`); ambos auxiliares repassam `rdx`/`r8`, então devem ser 0.
  `501DA4` torna nome único (acrescenta número), então qualquer nome funciona.

### <a id="change-5"></a>Alteração

- Sonda `spawn <type> [x y z]`: encontra tipo na tabela `0xA06` (pelo boneco
  atual), chama `1036D0` na thread de simulação com rotação do jogador, depois
  etapas de região/área e `10AFB0` (configuração do personagem em que caminho do gerador termina); todas as
  funções conferidas por bytes. Sem teste offline ainda.
- Sonda `stacks` também informa `rcx, rdx, r8, r9` da primeira chamada por pilha.

### <a id="observations-live-copy-b-1"></a>Observações (ao vivo, cópia B)

- `Orc_Infantry`, `GP_Ranger`, `Gondorian_Soldier`, `Talion`, `Dark_Talion` criados junto
  ao jogador de B; `AI_Talion` não criou nada (primeiros campos do registro nulos: stub nesta
  build). Tipos IA criados ativam a si mesmos (`+0x19A8` = 1) e agem sozinhos
  (orc saiu andando; após cinco criações no mesmo ponto junto do jogador de B, captura seguinte
  mostrou luta com contador de acertos).
- `Talion` (captura): rosto de Talion e roupa clássica de patrulheiro, em pose T;
  `+0x19A8` continua 0, então tick IA o pula e posição não acompanha
  teleportes. Gravar 1 ali manualmente fez tick IA executar (filtro pulou sua
  árvore), mas continuou em pose T: ator de cena sem conjunto de animações IA.
- Primeira tentativa das etapas região/área sem argumentos zero fez B falhar (violação
  de acesso em `11FBC8` chamado por `35DC38`); corrigido passando 0, como faz o jogo.

### <a id="derived-13"></a>Derivado

- Jogo pode criar sósia de Talion sob demanda, mas os únicos tipos Talion nesta build
  são stub IA vazio ou ator sem animações IA.
- Caminhos prováveis: colocar aparência Talion em tipo IA humano animado (esqueleto
  humano como o de Talion), ou dar conjunto de animações IA ao ator Talion. Nenhum encontrado ainda.

### <a id="unknown-5"></a>Em aberto

- Como aparência de NPC (`+0x2B30`, tipo `0xA66`) é aplicada e reconstruída.
- Se `GP_Ranger` ou `Gondorian_Soldier` usam esqueleto e animações de Talion.

## <a id="session-2026-10-21-af-the-puppet-is-a-talion-now-spawned-animated-ai-off"></a>Sessão 2026-10-21 af: boneco agora é Talion (criado, animado, IA desligada)

### <a id="observations-static-build-3095001-2"></a>Observações (estáticas, build 3095001)

- Aparência (tipo `0xA66`) aplicada pela virtual `+0x440` do personagem (`3FAFA4` para personagens
  IA; `19BF404` do jogador a chama e acrescenta controle de conjuntos). Na criação,
  configuração `3FAAEC` (posição 12 da classe IA) lê aparência do tipo de criação com `16680C`
  (chamada em `3FAB81`) e constrói modelo a partir dela (`3FA678`).
- Campos do registro de aparência têm nomes em hash (descritor na entrada `+8`: entradas de 16 bytes,
  32 bits baixos = hash de nome do jogo). Calcular hashes das strings do executável nomeou campos
  das primeiras 128 entradas lidas, entre elas `ModelRecord`, `Skeleton`, `BehaviorResource`, `CharacterModelPicker`,
  `CombatTree`, `AISimulationConfig`, `PlayerMovement`, `ProceduralBody`. Bloco de campos
  (entrada `+0x10`) tem layout fixo por tipo; lido ao vivo: `+0x148` modelo (tipo `0xA19`),
  `+0x188` modelo IA, `+0x1C8` esqueleto, `+0x1F0` base de animação, `+0x280` corpo.
- Humanos de Gondor e infantaria orc compartilham `Skeleton_Default` e conjunto de animação
  `OrcInfantry`; registros Talion usam `PlayerSkeleton`. `GP_Ranger` é olog-hai e
  `Human_Ranger` arqueiro orc, apesar dos nomes. `AI_Talion` (aparência) está completo
  (PlayerSkeleton, modelo IA, `talion_anim_base`), mas modelo é `dcBL_DarkTalion`.
- Personagem é ativado (byte em character `+0x19A8`, conferido pelo tick IA; `+0x18`
  num bloco em `+0x1990`) em `3F0D88`, chamado a cada quadro por `E7D070` no objeto de animação (character
  `+0x120`): só após recurso de animação (`+0x1990`) e recurso de comportamento
  (`+0x1998`) definidos, carregamento concluído e instância de comportamento (`anim+0x4A8`, seu
  `+0x10`) existente. Encontrado com monitoramento de gravação por hardware no sinalizador (criar, depois pilha da
  gravação: `3F0E73` <- `E7D070` <- `2FEEC0` <- ... atualização de quadro). `459474` é a
  virtual "definir recurso de comportamento" do objeto de animação (`+0x4B0` e `+0x1878`).

### <a id="change-6"></a>Alteração

- `spawn <type> x y z [appearance | abs:<record> | watch]`: busca de aparência em
  `3FAB81` passa por filtro que responde com a aparência dada durante essa única
  criação; `watch` arma monitoramento de gravação no sinalizador de ativação do novo personagem (sonda `watch`
  mostra ocorrências). Relatório diz o que veste e se está ativo.
- `look <base> <donor> <offset...>`: cópia privada de registro de aparência com alguns
  campos de outro. `animres <character> <resource>`: definir recurso de comportamento.
- `coop_puppet_spawn=<type>`: em vez de assumir personagem mais próximo, B cria um desse
  tipo na posição do remetente, dá a ele recurso de comportamento do próprio jogador de B
  (`player+0x1998`) e usa como boneco. Cópia de teste B agora usa `Talion`.
- Caminho de criação conferido só ao vivo (sem teste offline ainda).

### <a id="observations-live-copy-b-2"></a>Observações (ao vivo, cópia B)

- Aparências Talion em tipos de criação IA: `AI_Talion` e visuais de jogador fizeram jogo
  não criar nada; `Cine_Talion` foi criado, mas nunca ativado. Híbrido
  `Gondorian_Soldier` com modelo Talion renderizou como corpo escuro careca (recursos de Gondor
  não estão carregados nesta região; `Gondorian_Soldier` simples foi igual); um
  `Orc_Infantry` com modelo Talion ativou, mas só mostrou partes do modelo.
- Tipo `Talion` com recurso de comportamento do jogador de B ativou imediatamente e ficou em
  pose natural. Com `coop_puppet_spawn=Talion`, B criou-o 10 s após iniciar mundo
  (primeira tentativa ainda não encontrou personagens), tornou-o boneco com IA desligada e fixou-o a
  A: capturas mostram Talion (roupa clássica) junto ao jogador de B, depois afastando-se com
  passada completa, capa balançando, enquanto A caminhava.
- Mais um incidente: após várias criações de teste num ponto, olog lutou com jogador de B
  (vida caiu a 216 de 708); B reiniciado.

### <a id="derived-14"></a>Derivado

- Transferir aparência Talion a corpo IA não funciona com esqueletos diferentes; ator
  `Talion` de cena mais grafo de comportamento do próprio jogador funciona, e os controles existentes de IA desligada
  e andar/correr funcionam nele sem alteração.

### <a id="unknown-6"></a>Em aberto

- Se grafo do jogador lê cada variável escrita pelo movimento IA (corrida, curvas,
  parada) como as lê para o jogador.
- Se outros personagens tratam substituto como Talion (alvos, facções).
- Deslizamento de pés: ainda não medido neste corpo.
## <a id="status-summary-2026-10-21"></a>Resumo de estado 2026-10-21

Visão condensada das sessões a a af acima; as sessões guardam evidências e fontes.

### <a id="where-we-are"></a>Onde estamos

- Fases 0-4 (triagem, pesquisa, espaço de trabalho, entendimento, escolha) concluídas; estamos na
  fase 5 (construção). Decisão: construir cooperativo do zero (nenhum mod anterior utilizável), autoridade do anfitrião,
  sincronização e transporte próprios.
- Primeiro passo cooperativo funciona em uma direção num PC: cópia A transmite seu jogador (posição,
  rotação, vida) por UDP loopback a cada quadro; cópia B mostra Talion substituto que
  segue A, 50 ms atrás, interpolado, com IA própria desligada e caminhando com animações
  do jogador. Nada vai de B para A ainda; nenhum estado de mundo compartilhado.
- Nível de QA: verificações ao vivo (números da sonda, capturas de janela). Testes offline da proteção estão em
  repositório não publicado, então não são reivindicados aqui.

### <a id="key-technical-facts-build-3095001-rvas-from-image-base-0x140000000"></a>Fatos técnicos principais (build 3095001; RVAs relativos à base da imagem 0x140000000)

- Identidade: aplicativo Steam 356190, build 3095001, `ShadowOfWar.exe` FileVersion 1.0.8874.0,
  SHA-256 `ed0d95ca…0bdaef` (valor completo na sessão b). SteamStub, Denuvo provável; código em
  `.arch`; tabela de importações reconstruída em execução em `.xtext`. Motor "Kraken" (linhagem
  LithTech, fontes sob `Game\ObjectDLL`, `ClientShellDLL`, `Shared`).
- Cliente/servidor LithTech **não** é divisão em execução aqui (um processo, um mundo); existe
  camada entre pares NetMesh, mas nada a usa (sessão t). Daí sincronização própria.
- Nemesis: `HandleFactionEventAction` 40C304, `RollResurrection` 6DBD4C,
  `SimEvent::Simulate` 622A84 e outros (sessões r, s); resultados vêm de um LCG global
  (estado 2A25C88), então clientes nunca devem sortear; programas de console `Faction.Save`/`Load` existem.
- Salvamentos carregados pela API de nuvem Steam (`ISteamRemoteStorage::FileRead`;
  sessão y).
- Jogador: `[[GameClient 26FFA98]+0x888]`, posição `+0xAC`, quaternion `+0xB8`, objeto de vida
  `+0x26A8`. Chamadas do motor que alocam devem executar na thread de simulação; interceptamos
  posição 36 da vtable `1F96818` do jogador (por quadro).
- Personagens IA (vtable `1FB3640`): tick IA na posição 119 (`2F79A4`); chamada da árvore em
  `2F7B40` (filtrada para o boneco); controlador de movimento `[character+0x2C78]`, solicitação
  de movimento `3F4BD8` (destino, andar/correr, pelo navegador); variáveis de animação
  nomeadas (hash `423E70`).
- Registros: tipo de aparência `0xA66` (tabela `[27018B8]`, busca `1B08BB0`; bloco de campos com
  `+0x148` modelo, `+0x1C8` esqueleto) e tipos criáveis `0xA06` (encontrados por `+0x2E68` de qualquer
  personagem IA). Criação: `1036D0(world ctx [[26FFAB0]+0xF58], name, transform,
  type, 1, 1, 0, 0, 0)`, depois região/área (`168DA8`, `607610`/`35DC38`, com argumentos zero) e
  `10AFB0`. Personagem só ativa (`+0x19A8`, definido em `3F0D88`) após recurso de
  comportamento (`+0x1998`, definidor `459474`) definido.
- Substituto: tipo de criação `Talion` é ator de cena (pose T); dado recurso de comportamento do próprio
  jogador de B, ativa e anima. `AI_Talion` é stub nesta build;
  modelo Talion em corpos IA orc ou humanos não funciona (esqueleto, recursos diferentes).

### <a id="guard-test-copies-and-tools-state-now"></a>Proteção, cópias de teste e ferramentas (estado atual)

- `sowguard` (proxy `bink2w64.dll`, código próprio, não publicado): redirecionamento de arquivos a
  perfil por cópia, gravações na instalação e salvamentos reais bloqueadas, rede offline
  (só loopback), nuvem Steam isolada e bloqueio de gravação de estatísticas/conquistas, controle virtual e
  carregamento sem supervisão, execução em segundo plano, hook da thread de simulação, envio/recebimento cooperativo,
  modos de boneco e sonda no processo (leituras e buscas de memória, jogador, entrada de controle,
  teleporte, pilhas de chamadas, monitoramentos de gravação, criação, controle de boneco).
- Duas cópias de teste (A remetente, B receptor) são cópias da instalação; instalação e
  salvamentos reais intactos (conferidos antes de cada inicialização). Cópia B executa `coop_show=puppet`,
  `coop_puppet_ai=off`, `coop_puppet_move=both`, `coop_puppet_spawn=Talion`; cópia A executa
  `coop_send`. Cada uma chega ao mundo sem supervisão em cerca de 48 s.

### <a id="open-questions-and-biggest-risks"></a>Questões em aberto e maiores riscos

- Só uma direção, um PC, loopback: sem transporte real ainda (rede Steam é a
  escolha provável), sem tratamento de latência ou perda além da interpolação.
- Sem mundo compartilhado: inimigos, Nemesis, missões, tempo e RNG executam separadamente por cópia.
  Esta é a maior peça restante.
- Qualidade do substituto não verificada: curvas, parada, corrida, deslizamento de pés; se outros
  personagens o tratam como Talion (pode ser atacado ou ignorado); sem ataques ou combate
  mostrados.
- Tudo depende dos RVAs da build 3095001 (todos conferidos por bytes, recusados se divergirem); atualização
  do jogo quebra isso.
- Patches de código e monitoramento por registrador de depuração executaram bem nas cópias de teste; sessões longas com
  Denuvo/proteção contra adulteração não observadas.
- Higiene de processos: shell remanescente em segundo plano uma vez conduziu menu de A ao DLC3 e
  salvou automaticamente; sempre parar ciclos de entrada `sh.exe` restantes.

### <a id="next-steps-in-order"></a>Próximos passos, em ordem

1. Refinar substituto: medir velocidades de andar/correr, definir `coop_run_speed` (e tentar fator de
   velocidade da solicitação) contra deslizamento de pés; conferir curvas e parada em capturas.
2. Teste offline do caminho de criação (dados fixos com formatos de bytes do jogo).
3. Tornar bidirecional: B envia jogador a A, A também mostra substituto (mesmo código, configuração espelhada).
4. Depois estado do mundo: autoridade do anfitrião para inimigos e eventos Nemesis (interceptar
   `HandleFactionEventAction`, nunca sortear no cliente) e transporte de rede real.

## <a id="session-2026-10-22-ag-the-stand-in-walks-with-the-senders-own-stride-animation-inputs-anim-mode"></a>Sessão 2026-10-22 ag: substituto anda com passada própria do remetente (entradas de animação, modo anim)

### <a id="observations-live-copies-a-and-b-the-stand-in-is-the-spawned-talion-with-the-players-graph"></a>Observações (ao vivo, cópias A e B; substituto é `Talion` criado com grafo do jogador)

- Solicitações próprias de movimento (follow `none`, nada o fixando): andar e correr dão ambos
  ~230 unidades/s, qualquer que seja fator de velocidade da solicitação (0,5-2), limite de velocidade do estado de movimento
  (`[character+0x2CE8]+0x3B0`, lido pela atualização de modo 1 `374CA0`, que envia passada como
  0,5 andar / 1,0 correr) ou `Game_AnimRate` (definido a cada quadro pelo nosso hook). Solicitação mirando
  cenário o deixa preso no modo 1 até teleportar de volta ao chão aberto (era
  o "solicitações isoladas param de funcionar" da sessão ad).
- Capturas `PrintWindow` com câmera de B voltada a A: fixado (teleportado a cada quadro),
  substituto nunca dá passadas. Mantém pose esticada (tronco ereto, pernas para trás) ou,
  com teleportes a cada poucos quadros, desliza com pernas juntas. A "passada completa" da
  sessão af provavelmente era essa pose vista de trás.
- Grafo do jogador é alimentado pela atualização por quadro do jogador (`30BA10`, posição 36 da vtable
  que nosso hook já precede, e `514484`), pelo definidor float `176D78`
  em `player+0x120`: `RawMoveMag`, `RawMoveYaw`, `Game_MovementAxisX/Y`, `PlayerVelocity`,
  `PlayerSmoothVelocity`, `DeltaYaw`, `YawVelocityInDegsPerSec`, valores de câmera e inclinação,
  `Player_Focus`, `Game_SimTimer_TimeScale`, posições de mãos e pés (37 floats, encontrados com
  `stacks` em `176D78`), mais três bools por quadro (`ToggleStealthOn`, `KBMinputActive`,
  `CanHide`, por `375044` -> `375110`). Personagem IA não recebe nada disso.
- `176D78` posta cada valor ao grafo como mensagem (`176E40` -> `114B75C`; fila em
  `[anim+0x1860]` é compartilhada por todos os personagens, grafo é `[anim+0x480]`), então valores são
  capturados ao serem definidos, não relidos.
- Movido só pelas entradas (follow `none` ou `anim`, sem teleportes), substituto anda com
  passada natural: pernas alternadas, calcanhares tocando chão, pés sobre suas sombras, capa balançando
  (tiras de 9 capturas a intervalos de 50 ms, vista lateral). Caminho corresponde ao de A (`root_match.py`,
  substituto fixado a A, depois deixado às entradas enquanto A anda): reta 0,90-0,96 do comprimento
  de A, termina a 18-20; curva (duas direções do analógico) 1,00-1,01, termina a 2-4; andar,
  parar, voltar 0,98, termina a 0,8; meio analógico 0,97, termina a 7,5.
- Modo `anim` em caminhadas conduzidas (`drift.py`, distância ao ponto em que A estava 50 ms antes): quadrado
  de 4,4 s, média 4-5 unidades, máximo 7-12, sem reposicionamento; três quadrados (13 s, 12 curvas fechadas),
  média 15-35, máximo 50-120 entre execuções, reposicionamento ao passar de 150, estabilizado em meio
  segundo após A parar. Jogador do próprio B parado no caminho de A piorou muito (média 68):
  mundo de B tem obstáculos que o de A não tem.
- Corrigir desvio pelas entradas: girar entradas de câmera
  (`CameraYawMinusPlayerYaw`, `CharToCamDeltaYawInDegs`) ou analógico (`RawMoveYaw`,
  `Game_MovementAxisX/Y`) em 30 graus não mudou direção (dentro de 6 graus);
  `DeltaYaw` + 30 graus fez andar em arco (deslocamento líquido 128 de 236 unidades): `DeltaYaw` o gira.
  Direção de perseguição por `DeltaYaw` (com ou sem diferença de orientação, ganhos 0,3-1,
  qualquer sinal) piorou o desvio em toda execução comparado a nenhuma; removida novamente.
- Não transportado: manter botão de salto/parkour de A pressionado (corrida livre, 305-419 unidades/s): substituto
  cobriu 128 de 275-377 unidades. Floats de A então só diferem em `PlayerVelocity` (543); grafo de A
  entra em estados `RunningJump_AutoPicker_*` (nomes vistos em `114B7D0`, que copia nome de
  estado ou clipe dentro do runtime do grafo, `195988`). Nenhum bool para isso também.
- Criação falhou ("the game created nothing") quando posição de A estava onde jogador do próprio B
  estava; funcionou 150 unidades ao lado.

### <a id="change-7"></a>Alteração

- `simhook`: hook de entrada em `176D78` (bytes conferidos; jmp gravado com uma gravação alinhada de 8 bytes;
  stub chama tratador com `rcx`, `rdx`, `xmm2` do próprio definidor) registra 25 entradas nomeadas
  do jogador desta cópia (e lista outros nomes float para sonda `inputs`).
  `SimApplyPuppetInputs` define-as no boneco por `176D78` (bytes conferidos no primeiro uso
  quando cópia não registra nada).
- `coop`: pacotes (versão 3, 164 bytes) transportam entradas e máscara; receptor define entradas
  da amostra exibida (50 ms atrás) a cada quadro. `coop_puppet_move=anim`: movido só
  pelas entradas, reposicionado por teleporte além de `coop_anim_snap` (150) ou 150 acima/abaixo, e
  após A ficar parado por meio segundo, se estiver a mais de 15 unidades ou 15 graus.
  Cópia de teste B executa `anim`. Criação de substituto que falha é repetida a 150 unidades ao redor do remetente.
  Verificações de bytes de `Head()` recusam endereços fora da imagem.
- Sonda: `puppet follow anim`, `puppet inputs on|off`, `puppet snap <units>`,
  `puppet mirror on|off` (entradas próprias desta cópia no boneco), `inputs`.
- Ferramentas (não publicadas): uma conduz jogador de uma cópia numa direção global (ângulo do analógico =
  orientação desejada - guinada da câmera, guinada da câmera = guinada do jogador - `CameraYawMinusPlayerYaw`); outras
  medem caminho e desvio do substituto contra o remetente e capturam janela do jogo.
- Removido: definir `Game_AnimRate` pela velocidade do remetente, e direção por `DeltaYaw`.
- Receptor que não registra nada primeiro pulava entradas silenciosamente (ponteiro do definidor
  só era definido pelo gravador) enquanto as contava como fornecidas; capturas daquele momento
  mostravam fixação por teleporte sem entradas. Corrigido; novo caso offline `coop_puppet_recv`
  (receptor sozinho, pacotes do teste) falhou na DLL antiga e passa com correção.
- Casos offline: `coop_puppet_walk` (entradas de jogador fictício chegam ao boneco, uma quarta
  variável não) e `coop_puppet_recv` (receptor sozinho as aplica; `anim` deixa
  boneco livre enquanto está onde remetente está e o reposiciona quando remetente está a 500
  unidades).

### <a id="derived-15"></a>Derivado

- Para substituto com grafo do jogador, replicar entradas do grafo e deixar movimento de raiz
  próprio movê-lo; não fixá-lo a cada quadro. Teleportes interrompem passada, então
  correções devem ser raras.
- `DeltaYaw` é a alavanca de curva, então correção melhor de desvio é possível, mas precisa primeiro de
  caminho repetível de teste (trechos conduzidos e obstáculos de B fizeram execuções variar em 2x).

### <a id="unknown-7"></a>Em aberto

- Como corrida livre e saltos do botão A chegam ao grafo do jogador.
- Ataques, acertos e outras ações: não transportados.
- Desvio em caminhadas longas com obstáculos só do lado B (substituto é bloqueado, A não).

### <a id="session-ag-continued-free-run-and-drift-corrections"></a>Sessão ag, continuação: corrida livre e correções de desvio

#### <a id="observations-live"></a>Observações (ao vivo)

- Corrida livre (botão A mantido), capturada de B: substituto corre com passada longa e rápida,
  então entradas transportam animação de corrida. Ainda fica atrás: em trechos de 0,7 s, distância
  chegou a 130-150 unidades (média 32-65), sendo reposicionado 1-3 vezes.
- Rastreamento de chamada (nova sonda `trace`: breakpoint de execução em `176EFC`, que toda mensagem
  a grafo chama com grafo em `rcx`) no grafo do jogador de A, 600 ms andando contra
  600 ms em corrida livre: mesmos remetentes nas duas vezes (`176E40` floats ~1.300, `375110` bools
  ~106, `41C028` ~35, um raro). Corrida livre não acrescenta tipo de mensagem; só valores mudam
  (`PlayerVelocity` 543 em vez de ~130).
- Gravar posição do substituto diretamente (`+0xAC`, `+0xB4`) move modelo (capturas
  antes e depois de gravação de 100 unidades, pose ociosa mantida). Usado como correção por quadro em direção
  a A andando (fração da distância, limitada a 4-8 unidades por quadro ou 12% da velocidade de A),
  piorou desvio em toda execução alternada (média 39-67 contra 11-31 sem), então
  não é usado.

#### <a id="derived-16"></a>Derivado

- Distância na corrida livre é velocidade, não pose: velocidade de corrida livre de A vem de outro lugar além
  do movimento de raiz da animação de corrida (provavelmente código de movimento do jogador), então passada do substituto
  corresponde, mas velocidade não. Reposicionamento de 150 unidades esconde isso por enquanto.
