# <a id="the-witness-research-notes"></a>The Witness: notas de pesquisa

Status: protótipo funcional (duas cópias do jogo em um PC, localhost): representação do outro jogador, painéis resolvidos, portas abertas, energização de painéis, cabos acesos, recuperação do estado ao reiniciar e ressincronização após recarregar um save, com uma suíte automatizada. Branch `game/the-witness`. Data: 2026-10-22.

## <a id="game-identity-tested-build"></a>Identidade do jogo (build testada)

- App Steam 210970, build id 11370412 (Windows).
- `witness64_d3d11.exe`: PE32+ x64, 6864896 bytes, SHA-256 `8d672d444df6a6df7130f25a517bdab1af92731fe2138dc5b324d519561d55a5`
- `witness_d3d11.exe`: PE32 x86, 5657600 bytes, SHA-256 `6b8f8d9a3d595843335a96dc0d48fb133d0e77868c769673f7e4e6855811b8f6`
- Recursos empacotados em `data-pc.zip` (cerca de 2,7 GB). Inclui `steam_api(64).dll`, `openvr_api.dll`, Bink 2, Ansel.
- Engine: `unknown` segundo `detect_engine` (133 arquivos examinados, nenhuma assinatura correspondente). A Wikipédia a descreve como uma engine proprietária.

## <a id="observations-with-sources"></a>Observações (com fontes)

- Nenhum mod cooperativo ou multijogador encontrado. O jogo é para um jogador. Pesquisado: diretório deste repositório, `games/`, issues e PRs via `gh` (nada), busca de repositórios GitHub ("the witness multiplayer", "witness coop", "witness64_d3d11") e busca na web por mod multijogador/cooperativo de Witness. Ainda não pesquisado: Nexus, ModDB, archive.org, Reddit, Discords de speedrun/puzzles, comunidades em outros idiomas. Portanto, "nada encontrado" não significa "nada existe".
- [jbzdarkid/witness-randomizer](https://github.com/jbzdarkid/witness-randomizer) (MIT, atualizado em 2026-01-09): processo externo, `Source/Memory.cpp` lê e grava no jogo em execução com `ReadData`/`WriteData` tipados ao longo de uma cadeia de deslocamentos (globais, depois uma tabela de entidades indexada pelo id da entidade, depois um deslocamento de campo).
- [jbzdarkid/witness-trainer](https://github.com/jbzdarkid/witness-trainer) (MIT, atualizado em 2026-09-20): conecta-se com `OpenProcess`, encontra endereços por varreduras de assinatura de padrões de bytes (`AddSigScan`), refaz a varredura quando o jogo recarrega. Recursos do README: noclip, velocidade de corrida, FoV, desativar salvamento, salvar/carregar posição (X, Y, Z, theta), cronômetro do desafio. Afirma que deve funcionar com qualquer lançamento Steam; apenas Windows.
- O Archipelago tem um mundo Witness (`worlds/witness` em ArchipelagoMW/Archipelago); o cliente é um programa separado executado junto do jogo. Como ele intercepta o jogo: ainda não foi lido.
- [ClementSparrow/TheWitnessExplorer](https://github.com/ClementSparrow/TheWitnessExplorer): ferramentas Python para explorar recursos (sem licença, última atualização em 2021).
- Um tópico Steam de 2016 perguntou apenas sobre "cooperativo" por compartilhamento de tela; nenhum mod ([discussão](https://steamcommunity.com/app/210970/discussions/0/458607699611570322/)).

## <a id="memory-layout-work-2026-10-22-static-read-only-on-the-exe"></a>Trabalho no layout de memória (2026-10-22, estático, somente leitura do executável)

Executadas as varreduras de assinatura do randomizer e do trainer sobre `witness64_d3d11.exe` (SHA-256 acima) com um pequeno script (`python -I`, analisando seções PE). Cada assinatura correspondeu exatamente uma vez.

| Item | Fonte da assinatura | Resultado (RVA a partir da base do módulo) |
|---|---|---|
| GLOBALS | `Memory.cpp` do randomizer, `LoadPanelOffsets` | `0x62D0A0` |
| posição da câmera | `Trainer.cpp` do trainer (ajuste +0x10 no trainer) | alvo da varredura `0x6304B0` |
| ângulos da câmera | `Trainer.cpp` do trainer | `0x6303EC` |

Observado no código do randomizer: as entidades são lidas como `[GLOBALS + 0x18]` (array de ponteiros), entrada `id*8`, depois um deslocamento de campo. Para `GLOBALS == 0x62D0A0`, ele fixa `POSITION 0x24`, `ORIENTATION 0x34`, `POWER 0x2A0`, `TARGET 0x2B4`. O mesmo arquivo também fixa uma segunda build (`0x5B28C0`) e deixa `0x62B0A0` como TODO, portanto as builds realmente diferem.

Deduzido, não executado: esta build Steam corresponde a um layout já suportado pelo randomizer, então seus deslocamentos de campos de entidades devem se aplicar. Nada foi conectado a um jogo em execução, portanto nada disso foi verificado em execução ainda.

### <a id="runtime-probe-2026-10-22-first-attach"></a>Sondagem em execução (2026-10-22, primeira conexão)

Conexão somente leitura (`PROCESS_VM_READ`, Windows Python 3.11 + ctypes, sem gravações) a uma cópia descartável da instalação, base do módulo `0x140000000`, jogo no menu/início. Observado: posição e ângulos da câmera lidos como floats plausíveis; o ponteiro do array de entidades foi resolvido; a entidade `0x64` (Tutorial Straight) e `0x1B`, `0x1C` retornaram posições plausíveis (z de 3,7 a 6,7) e `power` = `1.0, 1.0`. Ainda não verificado: se os valores da câmera acompanham o jogador ao se mover e se `power`/estado resolvido mudam quando um painel é resolvido.

Efeito colateral: iniciar a cópia regravou `Launcher.variables` no `%APPDATA%\The Witness` real (um arquivo de configurações do inicializador, não um save). A pasta de saves foi copiada antes (14 arquivos, hashes idênticos) para `local/saves-backup/`.

Segunda sondagem (depois que o jogador iniciou um New Game e passou pela primeira porta). Observado: a posição da câmera mudou de (-36,1, -54,5, 4,4) no menu para (-183,8, -163,4, 3,8) no mundo, cerca de 4,5 m da entidade `0x64`, e permaneceu idêntica em duas amostras com 5 s de intervalo enquanto o jogador ficou parado. Portanto, o endereço da câmera acompanha o jogador (ainda não foi amostrada a variação durante caminhada). Janela da entidade `+0x290..+0x2D0`: o painel resolvido/usado `0x64` tem `1.0` em vários campos float (`+0x290`..`+0x2AC`) e `+0x2B4` = 216795; o painel não resolvido `0x65` tem `+0x29C` = 1.0, `+0x2B4` = 110 e `+0x2BC` = 111. Sem explicação: o que significa 216795 (não é um id plausível de entidade) e qual campo é "resolvido". É necessária uma amostra antes/depois da resolução de um painel.

Terceira sondagem (antes/depois de resolver um painel). Correção: o painel aos pés do jogador era a entidade `0x182` ("Tutorial Bend", a 0,6 m da câmera), não `0x65` (a cerca de 180 m). Observado: resolver `0x182` alterou `+0x290`, `+0x294`, `+0x2A8`, `+0x2AC` para `1.0`, `+0x298` para int `1` e `+0x2B0` para `1.322` (float; significado desconhecido). Após a resolução, seu padrão de campos é igual ao do painel `0x64`, resolvido antes.

Verificação cruzada estática: a assinatura `solvedTargetOffset` do trainer (`84 C0 74 19 0F 2F B7`) resolve para `0x294` neste executável. O trainer lê `solved = (float@0x294 == 1.0)`, `hasEverBeenSolved = int@(0x294+0x04) = +0x298`, `state = int@(0x294-0x14) = +0x280`, nome em `0x294-0x7C = +0x218`, arestas traçadas em `0x294-0x6C = +0x228`. A mudança em execução em `+0x294` e `+0x298` corresponde a isso. Portanto, para a build 11370412: flag de resolvido = float na entidade `+0x294`, já resolvido alguma vez = int em `+0x298` (verificado uma vez, em um painel). `+0x280` (estado) e os dados de arestas traçadas (necessários para mostrar o mesmo caminho) não foram amostrados.

Câmera: acompanhou a entrada no mundo (ver segunda sondagem); variações suaves de caminhada não amostradas.

Descoberta sobre a pasta de saves: o jogo mantém saves em `%APPDATA%\The Witness`, independentemente da pasta de onde o executável roda, portanto uma "cópia de teste" não isola saves. Iniciar um New Game regravou o `.witness_campaign` existente mais recente (e seu png) ali e adicionou arquivos; a inicialização também regravou `Launcher.variables`. O Steam Cloud (`steam_autocloud.vdf`) pode sincronizar essas mudanças (não verificado). Faça backup da pasta antes de qualquer inicialização de teste; aqui o jogador optou por não restaurá-la. Lição para o playbook: verificar onde o jogo grava saves antes de iniciar uma cópia.

## <a id="entity-census-and-puppet-candidates-2026-10-22-read-only-build-11370412"></a>Censo de entidades e candidatos a representação do jogador (2026-10-22, somente leitura, build 11370412)

Observação de inicialização: o executável abre primeiro uma caixa de opções de gráficos/vídeo, e nada carrega até ela ser confirmada. A flag de linha de comando `-skip_config_dialog` (encontrada nas strings do executável, com `-windowed`, `-new_game`, `-no_hud`, `-non_interactive`, `-command`, `-width`, `-height`) a ignora; iniciar `witness64_d3d11.exe -skip_config_dialog -windowed` chegou ao mundo sem entrada do usuário. `powershell.exe` travou a partir desta configuração WSL, enquanto `subprocess.Popen` do Python Windows o iniciou normalmente.

As classes do próprio jogo não têm RTTI (apenas as classes de bibliotecas de terceiros têm), então os tipos de entidades são distinguidos pelo ponteiro da vtable no início de cada entidade (um endereço dentro de `.rdata` do executável, de `0x5156A8` a `0x521678` a partir da base do módulo). Observado no mundo ativo: 49.422 entidades não nulas de 48 tipos. Maiores tipos: `0x518320` (26.675), `0x5156a8` (5.505), `0x516c88` (4.890), `0x51f2c8` (3.119), `0x517ed8` (2.067).

- Painéis são do tipo `0x518ca8` (594 instâncias). As entidades `0x64`, `0x65` e `0x182` são todas desse tipo. (`0x65` também é um painel, a cerca de 180 m do início; a correção anterior sobre "painel errado" era sobre qual estava aos pés do jogador.)
- Uma instância única do tipo `0x518090`, id `0x1e465`, fica com x,y iguais aos da câmera e z = 1,8, enquanto o z da câmera é 3,51: 1,71 acima dela, ou seja, uma altura dos olhos sobre os pés. Deduzido, não provado: esta é a entidade do jogador. Seria a entidade natural para ler a posição do jogador local.
- Entidades vizinhas do tipo `0x5183d0` (39 instâncias, ids a partir de `0x1e467`) ficam a poucos metros do jogador. Não se sabe o que são.

Não se sabe: quais dos 48 tipos desenham uma malha e se mover a posição `+0x24` de uma entidade move sua renderização (a transformação de renderização pode ficar em outro lugar). Esse é o próximo experimento e exige uma gravação na cópia de teste.

### <a id="does-moving-an-entitys-position-field-move-what-is-drawn-2026-10-22"></a>Mover o campo de posição de uma entidade move o que é desenhado? (2026-10-22)

Teste na cópia em execução (as únicas gravações feitas no jogo até agora; cada uma restaurada e relida): gravado z da entidade (`+0x2C`) +3,0 m, mantido por 10 a 24 s, depois restaurado o original. Observado: a gravação foi aplicada e permaneceu durante todo o intervalo (o jogo não a sobrescreveu), e a restauração retornou exatamente o original na leitura. Entidade `0x182` (painel aos pés do jogador, provavelmente fora do quadro): o jogador não viu nada. Entidade `0x64` (painel, a cerca de 8 m): uma captura de tela feita durante o deslocamento parece idêntica à anterior (mesmo painel nos mesmos pixels na porta à frente). Não provado: se o painel brilhante na captura é `0x64`.

Método de captura que não exige instalações: `ctypes` do Python Windows (encontrar a janela com `EnumWindows`, `BitBlt` do DC da tela, gravar o PNG com `zlib`). Funciona nesta cópia em janela.

Deduzido: a posição `+0x24` das entidades de painel é dado de gameplay, não aquilo que posiciona a malha (a geometria da fase provavelmente é pré-calculada ou posicionada por outra transformação). Portanto, "reutilizar um painel existente como representação do jogador gravando sua posição" não funciona. Outros tipos não foram testados (existem 48).

Imports de `witness64_d3d11.exe` que são arquivos comuns ao lado dele e podem ser substituídos por uma DLL proxy sem instalar nada: `AnselSDK64.dll`, `amd_ags_x64.dll`, `openvr_api.dll`, `bink2w64.dll`, `steam_api64.dll`. Ele também importa `D3D11CreateDevice` (d3d11.dll) e `CreateDXGIFactory` / `CreateDXGIFactory1` (dxgi.dll), então uma sobreposição D3D11 é possível carregando a partir de um proxy e interceptando `IDXGISwapChain::Present`. Há um compilador C++ MinGW-w64 instalado aqui; uma sobreposição também precisaria da visão/projeção da câmera (posição e ângulos são conhecidos; o campo de visão ainda não foi lido).

## <a id="proxy-dll-first-code-running-inside-the-game-2026-10-22"></a>DLL proxy: primeiro código executado dentro do jogo (2026-10-22)

Resultado: um proxy para `AnselSDK64.dll` (MinGW-w64, 9 exports) carrega em `witness64_d3d11.exe` na cópia de teste e registra logs de dentro do processo. Verificado por: sua linha de log (`proxy loaded: pid=... host=...witness64_d3d11.exe`), a linha `real Ansel DLL loaded` (o jogo chamou um export Ansel, então os stubs foram exercitados), a memória subindo para 1,7 GB e uma captura do mundo renderizado normalmente. A DLL original é mantida na cópia como `AnselSDK64_real.dll` (SHA-256 começa com `3b0677ae1e01fc17`). A instalação real não foi tocada.

O que deu errado primeiro (útil para o próximo agente):
- Encaminhamentos de exports no arquivo `.def` (`updateCamera = AnselSDK64_real.updateCamera`) fizeram o carregador informar "AnselSDK64_real.dll was not found", embora o arquivo estivesse ao lado do executável. Corrigido fazendo cada export ser um stub naked que chama `LoadLibraryW` com o caminho completo no primeiro uso e faz um salto final para a função real.
- Esse erro de carregador é uma caixa "System Error" do Windows pertencente a `csrss.exe`, não ao jogo: o processo do jogo não mostrava janela, 0 CPU e cerca de 5,8 MB, o que parecia um travamento. A caixa permanece na tela após o processo ser encerrado e aparece em capturas posteriores. Encontre-a enumerando janelas de nível superior com título `<exe> - System Error` e feche-a com `WM_CLOSE`.
- Não fazer E/S em `DllMain` (bloqueio do carregador): o log em um caminho `\\wsl.localhost` roda em uma thread iniciada a partir de `DllMain`.
- Uma captura de toda a área de trabalho (pid 0 no meu script de captura) é a forma rápida de ver essas caixas.

Os imports do executável vindos de `AnselSDK64.dll` não foram listados pelo meu primeiro filtro `objdump`; todos os 9 exports têm stubs. O uso por quadro de `updateCamera` é deduzido do nome, não observado.


## <a id="overlay-drawing-inside-the-games-frame-2026-10-22"></a>Sobreposição: desenhando dentro do quadro do jogo (2026-10-22)

Resultado: a partir da DLL proxy, uma interceptação de `IDXGISwapChain::Present` desenha marcadores no espaço de tela em posições do mundo, e eles coincidem com os objetos corretos. Evidência em captura de tela: um quadrado magenta no painel dourado da porta à frente (entidade `0x293`) e outro na coluna de pedra (entidade `0xc335`), ambos a poucos pixels da previsão do modelo (`0x293`: previsto (1055, 689) em 2405x1353, observado sobre o painel).

Como (código em [witness-coop](https://github.com/TommoDotCommo/witness-coop), `proxy/overlay.cpp`):
- Interceptação: criar um dispositivo D3D11 e uma swap chain fictícios no proxy, ler `Present` em sua vtable (índice 8) e sobrescrever esse campo (`VirtualProtect`), pois swap chains da mesma implementação compartilham a vtable. O `Present` do jogo então chama nossa função, que desenha e chama a original. O jogo funcionou normalmente depois (log: `Present hook called`, recursos criados, backbuffer 2405x1353, formato 28 = `R8G8B8A8_UNORM_SRGB`).
- Desenho: HLSL compilado em execução (`d3dcompiler_47.dll` via `LoadLibrary`), uma chamada de desenho de quadriláteros instanciados com um buffer de constantes de retângulos, profundidade e mesclagem desativadas.
- Modelo da câmera (lido dentro do processo a partir da base do módulo + posição `0x6304C0`, ângulos `0x6303EC`): `forward = (cos(phi)cos(theta), cos(phi)sin(theta), sin(phi))`, `right = (sin(theta), -cos(theta), 0)`, `up = (-sin(phi)cos(theta), -sin(phi)sin(theta), cos(phi))`, z para cima. Campo de visão: 60 graus verticais se ajustam (cerca de 89 graus horizontais em 16:9); calibrado a partir de dois pontos em um quadro, então considerar ±2 graus.

Ainda não verificado: isso foi calibrado na câmera da tela de título (inclinação exatamente 0). Os mesmos endereços acompanharam o jogador antes, mas a projeção não foi conferida durante caminhada no mundo. `updateCamera` (Ansel) nunca foi chamado em cerca de 100 s de execução, portanto não fornece uma câmera por quadro; a câmera vem da memória do jogo.

Verificação de caminhada (mesmo dia). Método: iniciar a cópia com `-skip_config_dialog -windowed -new_game` (começa diretamente no mundo), marcadores nos 16 painéis mais próximos à frente a partir da lista de ids do randomizer, tecla enviada com `SendInput` (scancode `W`, 1,5 s) após trazer a janela para primeiro plano, capturas antes e depois. Observado: a câmera foi de (-201,4, -114,8, 3,73) para (-199,9, -119,5, 3,73) na direção theta = -1,257; o vetor à frente do modelo (cos, sin) = (0,306, -0,952) multiplicado por 4,9 m dá (+1,5, -4,7), a variação observada. Um marcador ficou sobre a extremidade brilhante do túnel inicial antes e depois da caminhada, e os marcadores distantes se espalharam para fora como esperado. Duas direções diferentes (theta 0,225 na tela de título, -1,257 no túnel) se ajustam, então a convenção de ângulos está correta em ambas. Não testado: girar no lugar com o mouse enquanto se observam os marcadores (a matemática foi conferida em apenas duas direções), uma janela fora de 16:9 e tela cheia. A sobreposição não tem teste de profundidade, então os marcadores aparecem através das paredes.

## <a id="two-players-on-one-pc-pose-exchange-and-puppet-2026-10-22"></a>Dois jogadores em um PC: troca de pose e representação do jogador (2026-10-22)

Resultado: duas cópias do jogo, cada uma com a DLL proxy, trocam pose da câmera por UDP em localhost e cada uma desenha a outra como representação do jogador pela sobreposição de `Present`. O Steam permitiu dois processos do mesmo app a partir de duas pastas ao mesmo tempo.

Configuração: uma segunda cópia da instalação (3,9 GB, cerca de 33 s para copiar). `witness_coop.cfg` por cópia (portas `id`, `listen`, `peer` 47001/47002). Uma thread no proxy envia `{magic, id, seq, pos[3], angles[2]}` (36 bytes) a 30 Hz e mantém o pacote mais recente do par. A sobreposição desenha o jogador remoto como um retângulo verde alto dos pés (olhos menos 1,71 m) à cabeça, mais um ponto amarelo 0,7 m à frente da cabeça na direção remota. Ambos os jogos foram iniciados com `-skip_config_dialog -windowed -new_game` e posicionados lado a lado com `SetWindowPos`.

Observado, com um teste antes/depois: A (id 1) recebeu a tecla `W` por 1,6 s e andou cerca de 5 m. Câmera de A lida da memória: (-199,819, -119,816, 3,727). Log de B: `recv ... from id 1 ... pos (-199.82,-119.82,3.73)` e `overlay: remote id 1 age 31ms`. Um pacote anterior (`recv #600`) mostrou uma posição intermediária (-200,59, -117,45), portanto as posições são atualizadas durante a caminhada. A captura de B mostra o corpo verde à frente no túnel inicial com o tamanho e o lugar esperados. A não desenhou nada para B (B está atrás de A, então a representação fica atrás da câmera).

Não testado: mais de dois jogadores, uma rede real (LAN ou internet; apenas localhost), perda ou reordenação de pacotes (ainda sem verificação de sequência), a representação enquanto o remoto gira ou pula, uma representação ocultada por paredes (sem teste de profundidade) ou desenhada enquanto o jogador local está com o cursor de resolução de painel ativo. O corpo é um retângulo plano, não um modelo. A pose é a posição da câmera (olhos), então estados de agachar ou deitar não são separados.

## <a id="shared-panel-and-door-state-2026-10-22"></a>Estado compartilhado de painéis e portas (2026-10-22)

Objetivo: quando um jogador resolve um painel, o jogo do outro o mostra resolvido e a porta bloqueada abre. O projeto segue [effect-capture-story-sync](../../playbook/effect-capture-story-sync.md): a máquina onde acontece detecta, envia efeitos numerados, e o outro lado os aplica diretamente sem reproduzir a entrada do jogador.

### <a id="what-the-game-does-on-a-solve-observed-build-11370412"></a>O que o jogo faz na resolução (observado, build 11370412)

Os nomes de tipos das entidades vêm dos descritores de tipos do próprio jogo: `entity+0x08` aponta para um descritor cujo `+0x08` é o nome (o trainer lê nomes da mesma forma, e a função de porta compara `[entity+8]` com um descritor global). 48 tipos no mundo ativo, entre eles `Machine_Panel` (594), `Door` (327), `Power_Cable` (268), `Pressure_Plate` (263), `Multipanel` (41), `Group` (741), `Inanimate` (26.675), `Collision_Volume` (4.890), `Human` (1, o jogador, entidade `0x1E465`). Descritores no executável: `Machine_Panel` `0x62E670`, `Door` `0x62DE70` (RVAs).

Uma resolução natural do primeiro painel (`0x64`), comparada em todas as entidades entre um snapshot anterior, um snapshot ocioso (base de ruído) e outro 4 s depois (scripts `wsnap`/`wdiff2`, 49.414 entidades, bytes `+0x20..+0x400`): 15 entidades mudaram de uma forma não explicada pelo tempo ocioso.
- Painel `0x64`: `+0x278` `0 -> 1.0`, `+0x280` `0 -> 1` (estado "Solved"), `+0x290` `0 -> 1.0`, `+0x294` `0 -> 1.0` (flag de resolvido), `+0x298` `0 -> 1` (resolvido alguma vez). `+0x2B0` avança o tempo todo (um relógio), então não faz parte de uma resolução.
- O id alvo do painel em `+0x2B4` é `0x34EDB` (um nó de grupo `Inanimate`). A entidade `Door` `0x34EDA` recebeu três palavras de energia `0 -> 1.0` (`+0x1D0`, `+0x1D4`, `+0x1E4`), um `Inanimate` `0xD05D` recebeu o mesmo, e o painel da porta e quatro filhos de colisão/malha se moveram (a porta gira e abre).
- Painéis energizam 18 tipos diferentes de alvos (portas, outros painéis, cabos, grupos, placas, ...) e 341 de 594 painéis não têm alvo válido, então uma resolução não pode ser espelhada com um único caso especial.

### <a id="writing-fields-does-not-open-a-door"></a>Gravar campos não abre uma porta

Gravar exatamente essas 11 palavras no outro jogo (todas as gravações bem-sucedidas) não mudou nada no mundo: a porta ficou fechada. A abertura da porta é iniciada por uma chamada de função, a mesma que o trainer chama (`_doorOpenStart(door, 1.0)`). Nesta build ela é `base + 0x8E4B0` (encontrada pela assinatura do trainer `F2 0F 10 41 24 48 89 68 10`, início 15 bytes antes da correspondência; a desmontagem mostra `this` em `rcx`, o valor em `xmm1`, uma verificação de tipo contra o descritor Door e recursão pelas entidades vinculadas). Chamar `DoorOpenStart(0x34EDA, 1.0)` dentro do outro jogo moveu o painel `0x64` exatamente à posição produzida ali pela resolução real, `(-186.232, -158.897)`, sem crash.

Uma porta está "aberta" quando sua palavra de energia em `+0x1D0` é igual a `1.0` (10 portas lidas como abertas por padrão em um jogo novo, idênticas em ambos os jogos, mais `0x34EDA` após a chamada).

### <a id="implementation-in-the-proxy-dll-witness-coop-proxy"></a>Implementação (na DLL proxy, [witness-coop](https://github.com/TommoDotCommo/witness-coop) `proxy/`)

- Thread detectora (10 Hz): cada `Machine_Panel` resolvido (`+0x294 == 1.0` e `+0x298 == 1`) e cada `Door` aberta (`+0x1D0 == 1.0`) é comparada com seu último valor conhecido; uma mudança vira evento.
- Transporte: eventos são numerados por época do fluxo, confirmados cumulativamente, reenviados a cada 150 ms até confirmação, aplicados uma vez e em ordem, com duplicatas descartadas. Um reinício do par (novo id de sessão nos pacotes de pose) inicia uma nova época e um reenvio completo de cada painel resolvido e porta aberta; a aplicação é idempotente.
- Aplicador (thread de renderização, entre quadros): um painel remoto é gravado como resolvido (as cinco palavras acima); uma porta remota é aberta chamando a função do jogo após verificar o tipo da entidade. Ambos marcam a entidade como suprimida por 5 s para o detector local não reenviar a mudança.
- Canal de controle para desenvolvimento: `witness_cmd.txt` (`door <hexid>`), consultado por uma thread, executado na thread de renderização.

### <a id="two-bugs-found-by-running-it-both-are-in-the-playbooks-warnings"></a>Dois bugs encontrados ao executar (ambos constam nos avisos do playbook)

1. Uma base coletada enquanto o mundo ainda carregava viu 39 portas transitoriamente "abertas"; o outro jogo aplicou 30 delas. Correção: nada é detectado, reenviado ou aplicado até a câmera ser válida e as contagens de painéis e portas serem idênticas em três varreduras separadas por 3 s.
2. A proteção contra eco era apenas uma flag de "conhecido", que o detector redefinia quando a porta ainda não estava energizada um instante após a chamada, então 24 portas voltaram como eco. Correção: janela de supressão por entidade (5 s) após cada aplicação remota.

### <a id="test"></a>Teste

Um bot (Python Windows, `SendInput`) joga como A: caminha 46 m até o primeiro painel (teclas pressionadas por 3 s com verificação de distância), mira com retorno dos ângulos da câmera (0,00255 rad por contagem de mouse na horizontal, 0,00237 na vertical), clica para entrar no puzzle, move o cursor até o círculo inicial (0,218 m à esquerda do centro do painel, 3,6 contagens de mouse por pixel no modo puzzle), pressiona, arrasta até o fim e clica para terminar. Primeira execução, sem flags: A registrou `local panel 0x64 solved -> event` e `local door 0x34eda opened -> event` (11 eventos enviados no total, 11 confirmados); B registrou `remote panel 0x64 applied as solved` e `remote door 0x34eda opened (call ok)` e não emitiu nada de volta; uma comparação de estado dos 594 painéis e 327 portas lidos da memória de ambos os jogos foi idêntica (1 painel resolvido, as mesmas 10 portas abertas).

## <a id="the-mod-repository-2026-10-22"></a>O repositório do mod (2026-10-22)

O protótipo agora fica em seu próprio repositório público, [TommoDotCommo/witness-coop](https://github.com/TommoDotCommo/witness-coop) (MIT, `main`), organizado como mdk2-coop: `proxy/` (código C++ e Makefile), `tools/` (instalação, reinício, bot, comparação de estado, suíte de cenários, sondagens Windows), `README.md`, `CLAUDE.md`, `AGENTS.md`. Sem arquivos do jogo nem dados de terceiros: os marcadores de depuração que usavam a lista de ids de painéis do randomizer foram removidos da sobreposição (serviam apenas para calibração), e o detector encontra painéis e portas por tipo na tabela de entidades ativa. As duas cópias da instalação foram movidas para `local/`, ignorado nesse repositório. `tools/install.sh` recusa qualquer executável cujo SHA-256 não seja o da build suportada e qualquer `AnselSDK64.dll` que não seja o original.

Reexecução a partir do novo repositório (todos os quatro cenários, mesmos resultados de antes da mudança): base PASS, primeiro envio perdido PASS (A reenviou 11), MUTANT sem reenvio divergiu como exigido, MUTANT com proteção contra eco desativada ecoou 2 eventos como exigido.

Um bug revelado pela mudança: na primeira execução base do novo repositório, B registrou `state: local door 0x338d5 opened -> event` sem ninguém ter resolvido nada. `0x338d5` é uma das 10 portas abertas por padrão; foi energizada alguns segundos depois que a condição de "mundo estável", baseada apenas nas contagens, já havia passado. Evidência: o log foi mantido (`evidence_late_door_B.log`, local). Correção: a condição também exige um conjunto idêntico de painéis resolvidos e portas abertas em três varreduras, e mudanças nos primeiros 15 s após a condição são incorporadas à base em vez de enviadas. Aconteceu uma vez em cerca de nove inicializações e não voltou a ocorrer na execução final, então a correção existe, mas sua ativação não foi demonstrada. Lição adicionada a `playbook/methods.md`.

Nível de QA: a suíte atende à definição de `automated` do repositório (um harness em script que controla clientes reais do jogo e verifica o estado compartilhado, com mutantes), então a entrada do diretório está definida como `automated`. Sua cobertura é restrita (um puzzle, localhost), conforme indicado na entrada e na documentação.


## <a id="running-several-copies-and-agents-at-once-2026-10-22"></a>Executando várias cópias e agentes ao mesmo tempo (2026-10-22)

Medições em uma máquina de teste (build 11370412), para planejar vários agentes por jogo:
- Memória: cada Witness em execução ocupa cerca de 1,8 GB residentes (um par, 3,6 GB); a instalação ocupa 3,9 GB no disco (2,7 GB `data-pc.zip`, 1,4 GB `data/videos`).
- Velocidade: o contador de quadros em `base + 0x63954C` (build 11370412, do Memory.cpp do randomizer) avançou a 724 fps com a janela ativa e 10 fps minimizada. (Uma primeira nota aqui dizia 724 fps para uma janela "enviada para trás, sem foco"; isso estava errado, aquela janela ainda era a ativa. A Fase 1 mediu corretamente, ver abaixo.) O jogo não tem limite, então as instâncias precisam de um limite de quadros no proxy.
- Entrada: o executável importa `RegisterRawInputDevices` e `GetRawInputData` (mais `GetCursorPos`, `SetCursorPos`, `ClipCursor`, `SetCapture`), portanto teclado e mouse chegam a ele apenas pela janela com foco; o bot `SendInput` precisa da área de trabalho só para ele.
- Saves: o executável importa `SHGetFolderPathW` (nenhuma variável de ambiente está envolvida), então todas as cópias, e o jogo real do jogador, compartilham `%APPDATA%\The Witness`. Redirecionar essa chamada dentro do proxy isolaria as instâncias e protegeria os saves do jogador (implementado na Fase 1, abaixo).
- Hard links: um `data-pc.zip` com hard link fez a segunda instância simultânea falhar (`error opening bundle file data-pc.zip`, depois `fatal_error_data_corruption` no log), enquanto a primeira funcionou normalmente; todo o resto (executável, DLLs, `data/videos`) compartilha normalmente. Portanto, o zip é uma cópia privada por slot; um slot passa a custar 2,7 GB mais cerca de 40 MB. Não foi testado se o proxy poderia relaxar o modo de compartilhamento do arquivo para um único zip atender a todas as instâncias.
- O Firewall do Windows pergunta uma vez por caminho de executável, e cancelar deixa uma regra Block (uma pasta de teste antiga tinha essas regras); 32 regras Allow restritas (uma por slot e jogo, entrada, apenas de 127.0.0.1, somente dentro da pasta de teste) foram criadas com uma aprovação UAC.

Resultado: uma camada local compartilhada (reservas de slots com proteção de RAM livre, identidade pela pasta do worktree git, pools de instâncias com hard links em NTFS, portas e pastas de execução por agente, bloqueio de entrada da área de trabalho, limpeza limitada por caminho) e ferramentas Witness que a usam. Teste com três agentes simultâneos (dois worktrees Witness e um checkout MDK2 iniciados no mesmo segundo, obtendo slots 4–5, 2–3 e 0–1): base Witness PASS duas vezes, QA próprio do mdk2-coop 34 de 34, sem colisões, nada permaneceu em execução, cópia base intacta. Ainda não coberto: suíte Witness completa de dois agentes (apenas a base rodou), mais de três agentes, MDK2 em mais de um agente com suas próprias varreduras.

## <a id="phase-1-isolation-frame-cap-shared-zip-2026-10-22"></a>Fase 1: isolamento, limite de quadros, zip compartilhado (2026-10-22)

Os três são interceptações da tabela de imports ou de `Present` no proxy (`hooks.cpp`, `config.cpp`, `overlay.cpp` em witness-coop), configuradas em `witness_coop.cfg`.
- **Pasta de saves:** com `save_dir=instance`, a interceptação de `SHGetFolderPathW` retorna `<game folder>\appdata` para `CSIDL_APPDATA` (o jogo solicita csidl 0x1A; linha de log `hooks: SHGetFolderPathW(csidl 0x1a) -> redirected`). Após uma execução base completa (jogo novo, resolução, salvamento automático), o `%APPDATA%\The Witness` real ficou idêntico byte a byte (76 arquivos, todos os SHA-256 iguais), enquanto o `appdata\The Witness` próprio de cada instância continha o novo save e captura. A suíte agora verifica isso após cada cenário. Antes do redirecionamento, uma execução de três agentes havia gravado saves na pasta real.
- **Limite de quadros:** `cap_fps=30` em `Present` (QueryPerformanceCounter, `Sleep(1)` e depois espera ativa). Medido com `wfps.py`: o jogo ativo rodou a 30,0 fps; um jogo que não é a janela em primeiro plano rodou a 9,8 fps. Portanto, o jogo se limita a cerca de 10 fps sempre que não está em primeiro plano (também quando minimizado). Enviar `WM_ACTIVATEAPP`, `WM_ACTIVATE` e `WM_SETFOCUS` à janela a cada 20 quadros (`force_active`, removido novamente) não mudou isso; o mecanismo acabou sendo dois bytes mantidos pelo jogo (encontrados na Fase 2, abaixo). Observado: o jogo também assume sozinho o primeiro plano durante o carregamento, embora seja iniciado com `SW_SHOWNOACTIVATE`; o primeiro plano pertencia ao último jogo iniciado até uma janela neutra assumi-lo.
- **Zip compartilhado:** o log da interceptação mostra `CreateFileA opens data-pc.zip access 0x80000000 share 0`, ou seja, o jogo abre o arquivo exclusivamente, por isso um hard link quebrou a segunda instância. Com `share_zip=1`, a interceptação adiciona `FILE_SHARE_READ` (`-> FILE_SHARE_READ added` em ambas as instâncias): duas instâncias rodaram sobre um arquivo de 2,7 GB com hard link, ambas chegaram a um mundo estável, e a resolução do bot mais a comparação de estado foram idênticas. Um slot de teste agora custa cerca de 40 MB em vez de 2,7 GB.
- Adições à suíte: após cada cenário, saves reais intactos, redirecionamento acionado e arquivos gravados, limite de quadros em vigor; um novo mutante (`cap_fps=0`) que precisa ser lido como sem limite.

## <a id="phase-2-input-teleport-and-screenshots-without-a-focused-window-2026-10-22"></a>Fase 2: entrada, teletransporte e capturas sem janela com foco (2026-10-22)

Resultado: um bot joga o primeiro puzzle **sem nenhuma janela com foco, sem `SendInput` e sem usar a área de trabalho**. Dois desses bots rodaram ao mesmo tempo (dois agentes) junto de um agente MDK2; um monitor amostrando a janela em primeiro plano a cada 0,2 s durante toda a execução (1.648 amostras) nunca viu um jogo assumi-la, o confinamento do cursor do sistema permaneceu na tela inteira, e os saves reais do proprietário ficaram idênticos byte a byte.

Como o jogo recebe entrada (build 11370412; endereços relativos ao módulo; todos lidos do executável, não adivinhados):
- **Movimento do mouse** é entrada bruta: `GetRawInputData` é chamado para cada `WM_INPUT` (registros reais têm handle de dispositivo 0 e tamanho 48). Nosso proxy envia `WM_INPUT` à janela do jogo com um handle privado (`0xC0DE00xx`) e responde à chamada `GetRawInputData` do jogo para esse handle com um registro sintético; isso funciona sem foco na janela. Olhar: 0,0025 rad por contagem. Cursor do puzzle: 3,6 contagens por pixel.
- **Teclas e botões do mouse não são entrada bruta.** Um clique real de `SendInput` não produz registro bruto de botão nem de teclado. São mensagens comuns (`WM_KEYDOWN`, `WM_CHAR`, `WM_LBUTTONDOWN`, ...) consumidas por um segundo loop de mensagens (local de chamada de `PeekMessageA` em `exe+0x345aca`, chamado a cada quadro) e tratadas no próprio código por uma tabela de saltos em `exe+0x345bc0`; o procedimento da janela (`exe+0x37aea0`, encontrado interceptando `RegisterClassExA`) as ignora. Portanto, o proxy envia essas mensagens (`lParam` como o sistema operacional o monta; cliques no centro da janela).
- **Duas condições de liberação.** (1) Os handlers de teclas e botões começam com `cmp BYTE [input_manager+0xE5C], 0 / je skip`, onde `input_manager = [[exe+0x469A060]]`; o byte é zerado quando a janela perde a ativação, então teclas e cliques injetados são descartados até ele ser 1. Movimento do mouse não o verifica. (2) O loop principal executa `Sleep(100)` (cerca de 10 fps; encontrado registrando cada chamada de `Sleep` e seu chamador, `exe+0x69845`) quando o byte em `exe+0x62D394` e o byte `+0x21` do objeto janela `[exe+0x469A5B0]` são ambos 0; `+0x21` é o estado "ativo" da janela, definido por `WM_NCACTIVATE`/`WM_ACTIVATEAPP` com `wParam == 1`. `force_active=1` grava ambos os bytes como 1 a cada quadro na interceptação de `Present`.
- **Efeito colateral que precisou de correção:** acreditando estar ativo, o jogo movia o cursor REAL para o centro da janela a cada quadro (`SetCursorPos`) e o confinava em uma caixa 2x2 (`ClipCursor`), travando o mouse real; percebido comparando `GetCursorPos` e `GetClipCursor` com o retângulo da janela. Com `force_active=1`, o proxy agora torna inoperantes `ClipCursor`, `SetCursorPos`, `SetCapture`, `ReleaseCapture`, `ShowCursor` e responde a `GetCursorPos` com o centro da janela (um cursor virtual); a suíte verifica que o retângulo de confinamento permanece na tela inteira.
- **Teletransporte:** gravar a posição da câmera não faz nada (o jogo a recalcula); gravar a posição da entidade do jogador `0x1E465` (`+0x24`) move o jogador e a câmera acompanha, 1,69 acima dos pés. `tp x y z yaw pitch` a mantém por 12 quadros. Um `W` real mantido por 3 s andou 9,1 m; o `W` injetado fez o mesmo quando o byte de liberação foi mantido.
- **Capturas:** o proxy copia o backbuffer em `Present` para uma textura de preparação e grava um BMP de cima para baixo (`shot <name>`), mesmo com a janela sem foco ou coberta; `tools/bmp2png.py` o converte.

Caminhos sem saída, para ninguém repeti-los: enviar `WM_ACTIVATEAPP`, `WM_ACTIVATE`, `WM_SETFOCUS` à janela (os handlers têm suas próprias pré-condições e a flag de que precisamos é outro byte); falsificar `GetActiveWindow` (a string está no executável, mas o jogo nunca a resolve por `GetProcAddress`; só resolve auxiliares CRT, NVAPI e XInput); uma interceptação de teclado de baixo nível (o jogo não instala nenhuma na inicialização); registros brutos falsos de teclado (ele registra entrada bruta apenas para o mouse); comparação de memória de `.data` com e sem foco (as flags ficam no heap).

Dois erros que a própria suíte detectou: (1) uma base passou enquanto o bot não havia feito nada (ambos os jogos intactos, portanto "idênticos"), porque os caminhos Windows no comando do bot perderam as barras invertidas no shell; a suíte agora exige que o bot informe o painel resolvido e verifica `A emitted a panel event`. (2) O mesmo problema de shell de `eval` com caminhos exportados: colocar todo caminho Windows entre aspas. O antigo bot `SendInput` e o bloqueio de entrada da área de trabalho não são mais usados pela suíte Witness.

## <a id="phase-3-the-sync-core-without-the-game-t0-2026-10-22"></a>Fase 3: o núcleo de sincronização sem o jogo (T0) (2026-10-22)

Resultado: a lógica de sincronização (eventos, confirmações, reenvio, épocas, condição de mundo estável, janela de estabilização, proteção contra eco, reenvio completo) saiu de `state.cpp`/`coop.cpp` e foi para uma biblioteca C++17 pura, `proxy/core/sync_core.{h,cpp}` em witness-coop. Ela vê o jogo apenas por uma interface `World` (varrer, ler e aplicar estado de painéis/portas, pose da câmera), então o fuzzer do hub (`tools/fuzz`, `ITarget`) controla dois núcleos sobre um link com perdas e um mundo falso (fase de carregamento, portas abertas por padrão, uma porta que se energiza sozinha tardiamente, portas em cascata que abrem 200–800 ms após uma resolução, uma porta remota que aparece tarde). `make -C proxy/core test` (ou `python3 proxy/core/tests/run_t0.py`) compila e executa 500 sessões de 150 s com sementes, sem erros (cerca de 1.500 reinícios, dezenas de milhares de pacotes antigos reproduzidos), depois uma vez por gêmeo de bug; todos os 10 gêmeos são detectados (2,7 s no total, sem jogo, sem slot):

`no_resend` e `no_checksum` -> not_quiescent/converge, `no_echo_guard` -> echo_sent, `no_dedupe` -> double_apply, `no_epoch_reset` e `apply_out_of_order` -> out_of_order_apply/converge, `no_resync_on_restart` -> converge, `no_gate` -> spurious_event/converge, `no_settle` -> spurious_event, `wrong_ack_epoch` -> not_quiescent.

O que o simulador encontrou e a suíte real de dois jogos não havia encontrado:
- **Reinícios do par oscilavam.** Qualquer id de sessão diferente era tratado como reinício, então dois pacotes em trânsito de uma sessão velha e uma nova faziam cada lado redefinir o outro para sempre. Sessões e épocas agora só crescem; as antigas são ignoradas. (O id de sessão de produção agora é `time(nullptr)`, que cresce a cada inicialização.)
- **A janela de estabilização engoliu uma resolução real.** Mudanças nos primeiros 15 s após a condição eram incorporadas à base, o que também incorporava uma resolução real de painel nesse período: nunca enviada. Painéis agora nunca são incorporados; portas são incorporadas, exceto nos 5 s após uma resolução local (a cascata dessa resolução). Limite, por projeto e contabilizado no alvo (`startup_flip_beside_a_solve`): uma porta que se energiza sozinha nos 5 s após uma resolução local parece a cascata dessa resolução e é enviada.
- Meu próprio bug: a sessão era lida dos bytes do checksum (deslocamento 36, não 32). Apenas o teste com perdas detectou isso.
- **A cobertura depende de o perfil da sessão corresponder aos tempos do protocolo.** Sete dos dez gêmeos inicialmente não foram detectados porque uma máquina reiniciava a cada 1,4 s enquanto a condição precisa de 9 s ou mais. O perfil agora impede que um jogo saia nos 45 s após iniciar, usa sessões mais longas e um jogador que só age após o mundo carregar e se estabilizar; `no_settle` também precisou que a alteração tardia ocorresse após a condição e que nenhuma resolução a adiasse. Um gêmeo que passa significa que o teste não consegue enxergar aquela proteção, não que a proteção esteja correta.

Não coberto pelo T0: o layout de memória e os tempos do jogo real (o adaptador `GameWorld` em `state.cpp`); apenas a suíte T2 verifica isso. A suíte T2 foi reexecutada na build refatorada (ver a seção QA do README).


## <a id="derived"></a>Deduções

- Posição do jogador e estado de painéis/entidades são acessíveis de fora do processo, e a comunidade já os encontra por varredura de assinatura, portanto um mod pode ser um processo externo ou injetado sem código-fonte. (Confirmado: o mod é uma DLL proxy injetada.)
- Varreduras de assinatura toleram atualizações melhor que endereços fixos, mas os hashes da build acima são os únicos testados.
- Cooperativo aqui significa: mostrar um segundo jogador (representação) e compartilhar progresso (painéis resolvidos, portas abertas, energia, cabos). O protótipo trata tudo como eventos monotônicos, então não há host nem regra de autoridade; estado reversível precisaria de uma.

## <a id="guesses"></a>Hipóteses

- Os puzzles provavelmente são determinísticos a partir da tabela de entidades, exceto as seções de porta aleatória e desafio.

## <a id="unknowns"></a>Desconhecidos

- Família da engine e se ela tem código de rede.
- Se existe alguma camada de script dentro de `data-pc.zip`.
- Se `witness64_d3d11.exe` tem símbolos de depuração ou um pdb conhecido.
- Se as builds GOG/Epic diferem da build Steam.
- Como o cliente Archipelago lê o jogo.
- Desligamento de energia, cabos além do testado, pontes `:slider_cable`, placas, lasers, rede real e mais de dois jogadores: não implementados ou não testados.
- Se alguma porta fecha durante o jogo normal (a heurística de recarga de save interpretaria isso incorretamente como carregamento).

## <a id="next"></a>Próximos passos

1. Estender a sincronização aos outros painéis que acionam cabos, placas, lasers e pontes, com uma resolução natural e comparação de estado para cada um; definir autoridade para estado reversível.
2. Uma rede real (IP direto ou relay), depois execuções com latência e perdas.
3. Mais puzzles na suíte (até agora, três puzzles do tutorial).
4. Oclusão e um modelo real para representar o jogador.
5. Concluir as buscas pendentes (Nexus, ModDB, Reddit, Discord).

## <a id="phase-4-sync-beyond-the-first-puzzle-2026-10-22"></a>Fase 4: sincronização além do primeiro puzzle (2026-10-22)

Cada item abaixo é um commit de witness-coop com um cenário no jogo real e um mutante, mais testes sem jogo (T0).

### <a id="retain-acknowledged-events-until-the-game-applies-them"></a>Reter eventos confirmados até o jogo aplicá-los

Implementação: commit `bfe1b7e` de witness-coop.

#### <a id="observations"></a>Observações

- `SyncCore::onPacket` confirma eventos ordenados ao enfileirá-los, antes de a thread de renderização aplicá-los. Antes, `applyRemote` removia eventos mesmo quando a entidade estava ausente ou `applyDoorOpen` retornava false; este último também incrementava contadores de aplicação e instalava uma proteção contra eco para uma chamada recusada.
- Adicionada uma regressão determinística do receptor, sem jogo (`proxy/core/tests/apply_retry.cpp` em witness-coop). Antes da correção, os casos de painel ausente, porta ausente e porta recusada falhavam; a rejeição por tipo errado passava.
- Após a correção, os quatro casos passam. Cada caso de nova tentativa detecta um gêmeo `noApplyRetry`. Eles verificam ACK antes da aplicação, convergência sem outro pacote, progresso de porta não relacionada, contadores de aplicação corretos e ausência de eco local após o sucesso.
- `make -C proxy/core test`: regressões determinísticas passam, 500 sessões limpas de fuzz passam, todos os 10 gêmeos de fuzz existentes detectados. `make -C proxy`: DLL compila. `git diff --check`: limpo.

#### <a id="derived-1"></a>Deduções

- A confiabilidade do transporte sozinha não garante a aplicação do estado: o receptor precisa manter a responsabilidade por um evento confirmado até seu adaptador de jogo ter sucesso.
- Novas tentativas fazem no máximo uma tentativa por evento enfileirado por quadro, dentro do limite existente de 1.024 eventos de recebimento. Essas mudanças de painéis/portas são monotônicas e independentes, então uma entidade temporariamente indisponível não precisa bloquear outra.

#### <a id="unknowns-1"></a>Desconhecidos

- Não foi induzida entidade ausente nem chamada recusada no jogo real; esses modos de falha são simulados no T0.
- A primeira tentativa base no jogo real falhou durante a inicialização: A nunca registrou o patch da sobreposição nem o início da rede, a busca de entidade do bot retornou uma tabela ilegível, e foram medidos 0 fps. B chegou à condição de mundo estável. Verificações de hashes dos saves, redirecionamento e cursor passaram; a suíte liberou seus slots. Uma segunda tentativa base nova passou: um painel resolvido e dez portas abertas idênticos em ambos os jogos, sem eco de B, sem reenvios, 30,0 fps, verificações de hashes dos saves/redirecionamento/cursor passaram, slots liberados. A primeira falha de inicialização não se repetiu; sua causa continua desconhecida.

### <a id="follow-up-real-game-restart-catch-up"></a>Continuação: recuperação de estado após reinício no jogo real

#### <a id="observations-1"></a>Observações

- Revisada a ordem de construção de estado do mundo do hub (`playbook/how-coop-mods-work.md`, etapa 4), captura de efeitos e orientação sobre dessincronização. Escolhida a verificação ausente de entrada/reentrada no jogo real: o reenvio do estado completo já existe, mas só o simulador sem jogo o cobria.
- Adicionados `tools/restart.sh B` / `tools/install.sh B` seletivos; processo, configuração e DLL carregada de A sobrevivente são preservados. Processos recém-iniciados são registrados imediatamente, em vez de após ambas as inicializações terminarem.
- Adicionados cenários limpo e mutante com recuperação desativada. As pré-condições leem ambos os mundos da memória e exigem que a resolução original tenha chegado a B e que todos os eventos do remetente tenham sido confirmados. Após B reiniciar com `-new_game`, A precisa manter seu PID e estado, e B precisa ter um novo PID e censo completo. O caso limpo exige que todo o estado de resolvido/aberto corresponda e não haja eco de B; o mutante exige especificamente que o primeiro painel e sua porta estejam ausentes em B.
- `bash -n tools/restart.sh tools/install.sh`, compilação Python, compilação da DLL e T0 (regressões de aplicação, 500 sessões limpas de fuzz, os dez gêmeos de fuzz) passam. No jogo real, `tools/qa.sh 'restart catch-up'`: ambos os cenários PASS. O limpo restaurou um painel resolvido e dez portas abertas, sem eco. O mutante deixou exatamente o painel `0x64` e a porta `0x34eda` ausentes em B, depois que os dois eventos originais foram confirmados. Ambas as execuções mantiveram os hashes de saves reais inalterados, redirecionaram saves das instâncias, deixaram o cursor livre e mediram A a 30,0 fps. Todos os jogos reservados foram liberados. Implementação: witness-coop `df7b276`.

#### <a id="derived-2"></a>Deduções

- Reiniciar um receptor só após a confirmação dos eventos originais distingue a recuperação por snapshot da retransmissão de deltas pendentes.

#### <a id="unknowns-2"></a>Desconhecidos

- Entrada tardia pela primeira vez no jogo real, recarga de save no mesmo processo e comportamento WAN continuam sem teste.

### <a id="follow-up-second-tutorial-puzzle-exposes-skipped-door-zero"></a>Continuação: segundo puzzle do tutorial revela porta zero ignorada

#### <a id="observations-2"></a>Observações

- Lido Tutorial Bend `0x182` usando os deslocamentos de grafo do painel de [witness-randomizer Memory.cpp](https://github.com/jbzdarkid/witness-randomizer/blob/master/Source/Memory.cpp), branch da build `GLOBALS == 0x62D0A0`: posições em `+0x3C0`, flags `+0x3C8`, conexões `+0x3D0/+0x3D8`, contagens `+0x3B4/+0x3B8`. Três nós: `(0.8,0.25)`, `(0.8,0.75)`, `(0.2,0.75)`, conexões `0-1`, `1-2`.
- O comando de câmera em pé `tp -182.71 -164.90 3.727 0.303 -0.066` vê a tela do puzzle de frente. O olho real se acomoda em z de aproximadamente 3,896 no piso. Uma captura do backbuffer pelo proxy mostra o círculo inicial em `(1016,640)` em 1920x1080; entrar no modo de mira posiciona inicialmente o cursor em `(960,540)`.
- O posicionamento livre do cursor usa 112 contagens para a direita e 200 para baixo nesta viewport. Um traçado restrito curto parou antes do fim; 40 quadros de `(0,-18)` e depois 40 de `(-18,0)` alcançam ambas as extremidades dos segmentos. Um clique conclui a resolução natural.
- Memória após a resolução: A e B contêm os painéis resolvidos `0x64` e `0x182`; A tem 11 portas abertas, B tem 10. A única diferença é a porta de ID `0x0`, aberta apenas em A. `tools/state_diff.py` terminou com 1 e exatamente essa diferença.
- Causa em `proxy/state.cpp`: a varredura de entidades começa no ID 1. O censo somente leitura começa em 0 e encontra 327 portas, enquanto o adaptador vê 326. `GameEntity(0)`, validação de pacotes e a ponte de chamada de porta aceitam zero no restante.
- Adicionados `wbot2.py`, `wcontrol.py` compartilhado, `wpanel.py` somente leitura e um cenário do segundo tutorial na suíte que exige ambos os painéis resolvidos e ambas as portas específicas abertas. Um mutante que ignora zero precisa manter a resolução do segundo painel em B, mas perder a porta zero. O cenário limpo novo anterior à correção FAILou com exatamente a porta zero ausente em B, enquanto ambos os bots informaram resolvido pela memória. O mutante também reproduziu o mesmo estado de porta ausente. A correção do scanner inclui o índice zero da tabela por padrão, e `skip_entity_zero=1` restaura a varredura antiga para o mutante. Após a correção, verificações de estado limpo/mutante ambas PASS: limpo tem 2 painéis e 11 portas em ambos os lados, sem eco de B; mutante tem ambos os painéis, mas só falta a porta zero em B. Verificações de hashes de saves, redirecionamento, cursor livre e 30,0 fps passam; não restam jogos/reservas. O wrapper retornou inesperadamente 1 após ALL OK; uma repetição com scripts inalterados retornou 0, com ambos os cenários PASS e todos os recursos liberados. A divergência anterior de status não voltou a ocorrer; causa desconhecida. Implementação: witness-coop `cfb67a0`. Sintaxe de shell, compilação Python e verificações de espaços em branco passam. Compilação da DLL e todos os testes T0 existentes passam.

#### <a id="derived-3"></a>Deduções

- O índice zero da tabela é válido nesta build; zero não pode ser usado como sentinela de índice durante o censo. O mod/as sondagens chamam esses índices normalizados da tabela de IDs de entidade; os IDs de engine armazenados pelo jogo usam a base separada descrita abaixo.
- Correção da interpretação anterior dos tipos de alvo: os IDs de eventos e as sondagens deste repositório usam **índices da tabela** de entidades, enquanto os campos de alvo do jogo contêm IDs da engine. Ler `table_base_id = u32([base+0x62D0A0]+8)`, observado `1`. Em `exe+0xB9F00`, o jogo lê o painel `+0x2B4`, subtrai esse ID base, indexa `[globals+0x18]`, verifica o descritor Door e chama `exe+0x8E4B0`. Assim, o alvo `0x34EDB` significa índice de tabela `0x34EDA`, e o alvo `1` significa índice zero. A afirmação anterior de que o primeiro alvo é um Inanimate no índice `0x34EDB` foi um erro de espaço de nomes. `wpanel.py` agora informa tanto o alvo bruto quanto o índice normalizado da tabela.

#### <a id="unknowns-3"></a>Desconhecidos

- Replicação de cabos e painéis energizados continua sem implementação. O segundo painel do tutorial também controla uma porta, então primeiro revelou essa lacuna anterior de correção.

### <a id="follow-up-panel-power-on-progression"></a>Continuação: progressão de energização de painéis

#### <a id="observations-3"></a>Observações

- Um censo de alvos somente leitura encontrou um painel simples de tutorial já energizado no índice `0x18AF`, alvo bruto `0x1C` = índice alvo `0x1B` (Machine_Panel, inicialmente com energia solicitada e visível ambas zero). Seu grafo de 7 nós tem uma rota horizontal central que separa os quadrados pretos dos brancos.
- Resolução natural por entrada do proxy: teletransportar acima do ponto em pé `(-158.745,-69.925,10.0)`, yaw `2.749`, pitch `0.003`; o olho se acomoda em z `6.7143`. Entrar na mira, 80 contagens à esquerda até o início, clicar, 40 quadros de +18 x, clicar para terminar. Uma resolução na origem acende o alvo `0x1B` em A; B recebe a origem resolvida, mas deixa seu alvo com energia `(0,0)`. Capturas no jogo mostram o segundo painel acendendo em A. Hashes de saves reais inalterados durante a sessão de pesquisa; slots liberados.
- Um primeiro teletransporte longo na altura do solo foi deslocado pela resolução de colisão. Chegar acima do solo funciona; o novo bot verifica a posição real da câmera e tenta novamente até três vezes antes de falhar.
- A desmontagem da build 11370412 em `exe+0xC2890` recebe um ponteiro de painel, define energia solicitada `+0x2A4` como `1.0`, trata redesenho/aleatorização e portas vinculadas. A energia visível `+0x2A0` acompanha no loop normal do jogo. O aplicador verifica o tipo Machine_Panel e o prólogo da função, depois a chama na thread de renderização.
- Adicionados testes determinísticos de energização do núcleo; tanto a sincronização ao vivo quanto a recuperação por reinício falharam antes do novo evento. Após a implementação, passam, incluindo primeiros envios descartados, chamadas recusadas retidas além do intervalo de eco, ausência de eco e garantia de que um alvo energizado não seja marcado resolvido. Gêmeos de energia desativada, sem nova tentativa de aplicação, sem proteção contra eco e sem ressincronização são detectados. Regressões de aplicação existentes mais 500 sessões limpas de fuzz e os dez gêmeos antigos passam. A DLL compila.
- O novo evento de tipo 3 compartilha energização de painéis pela fila confiável e por snapshots do estado completo. O estado de energia faz parte da assinatura de mundo estável e tem sua própria proteção contra eco. As assinaturas do protocolo são v2 (`WTP2`, `WTE2`, `WTA2`) para evitar que um receptor antigo ignore silenciosamente o novo vocabulário. Ambas as cópias precisam usar a DLL atualizada.
- No jogo real, `tools/qa.sh 'panel power chain'`: limpo e mutante com energia desativada ambos PASS, saída do comando 0. O limpo também reinicia B após a confirmação de todos os eventos originais: ambos os mundos correspondem em 2 painéis resolvidos, 10 portas abertas e 238 painéis energizados. O alvo permanece não resolvido, B não emite eco de energia e aplica um evento de energia. O mutante preserva ambos os painéis resolvidos e portas, mas tem 237 painéis energizados em B, faltando apenas `0x1B`. Verificações de hashes de saves, redirecionamento de saves da instância, cursor livre e 30,0 fps passam; jogos próprios e slots liberados.
- Fixture de compatibilidade de protocolo: evento e pose v1 com checksum são ignorados, enquanto controles v2 correspondentes são aceitos. Todos os testes de energia e a suíte existente de 500 sessões de fuzz/gêmeos passam. Implementação: witness-coop `9799af8`. Compilação Python e `git diff --check` passam; recompilação final da DLL passa.


#### <a id="derived-4"></a>Deduções

- Ler a energia solicitada para detecção captura a ativação discreta enquanto cada engine anima seu brilho visível. A asserção no jogo real exige que a energia solicitada e a visível cheguem a 1.

#### <a id="unknowns-4"></a>Desconhecidos

- Isso adiciona apenas progressão de energização, correspondendo ao modelo existente de progressão resolvido/aberto. Desligamento de energia, regras de conflito/autoridade para estado reversível e sincronização de cabos continuam sem implementação.

### <a id="follow-up-first-time-late-join"></a>Continuação: primeira entrada tardia

#### <a id="observations-4"></a>Observações

- Adicionados os cenários `late join` e `MUTANT: late join without snapshot` (`tools/suite.py`, `late_join`). Apenas A é iniciado (`restart.sh A`; `restart.sh` agora tolera um par sem arquivo de pid). O bot resolve o painel `0x64` em A enquanto B não existe, depois B é iniciado pela primeira vez com `restart.sh B`.
- A roda com `no_resend=1`, então os eventos originais são enviados uma vez para lugar nenhum e nunca retransmitidos; só o snapshot de estado completo enviado quando A vê a sessão de B pela primeira vez pode entregá-los. O mutante adiciona `no_resync_on_restart=1`.
- Resultado no jogo real (witness-coop, `tools/qa.sh 'late join'`, saída 0): B limpo corresponde a A na memória (1 painel resolvido, 10 portas abertas, 237 energizados, 594 entidades) sem eco; B mutante tem 0 painéis e 9 portas, faltando exatamente `0x64` e `0x34eda`. Verificações de save, cursor e 30,0 fps passam; slots liberados.

#### <a id="derived-5"></a>Deduções

- Primeiro contato e reinício compartilham um caminho de código (`peerSession_` aumenta, flag de snapshot definida), então a entrada tardia é coberta pela mesma proteção; o nome da flag mutante diz "restart", mas controla ambos.

#### <a id="unknowns-5"></a>Desconhecidos

- Entrada tardia com o comportamento padrão de reenvio (eventos reenviados para um B em inicialização) não foi isolada. Recarga no mesmo processo e WAN sem teste.

### <a id="follow-up-same-process-save-reload"></a>Continuação: recarga de save no mesmo processo

#### <a id="observations-5"></a>Observações

- O menu de pausa pode ser controlado por teclado pela entrada dentro do processo (Esc, S, S, Enter = "Load a Game"; o save mais recente é selecionado). O novo `tools/win/wreload.py` faz isso sem foco nem entrada da área de trabalho.
- O jogo mantém um arquivo de save por sessão e o regrava no mesmo lugar; abrir o menu de pausa também salva. Uma primeira recarga, portanto, carregou o estado atual e não mudou nada. O cenário faz backup do primeiro save de B (gravado cerca de um minuto após a inicialização, antes de qualquer progresso), restaura-o após Esc e antes da leitura da lista, depois o carrega. `restart.sh` agora esvazia a pasta própria de saves de cada instância para haver um save conhecido.
- Antes da correção (jogo real, manualmente e depois por script): B voltou a 0 painéis / 9 portas e ficou assim; A não tinha motivo para reenviar (sem mudança de sessão, todos os eventos confirmados). Um carregamento anterior com um save antigo também emitiu as aberturas de portas de inicialização do carregamento e um evento de energia de B como eventos locais, aplicados por A (A mostrou 6 portas abertas extras).
- Correção em `sync_core.cpp` (`reloadSeen`): uma porta conhecida aberta fechando, ou dois ou mais painéis conhecidos não resolvidos (um painel pode ser redesenhado), é interpretado como carregamento. O núcleo volta à condição de mundo estável, incrementa sua sessão (o par então reenvia o estado completo, como num reinício), limpa seu fluxo e supressões de eco, e publica seu próprio estado completo quando estável, para os transientes da inicialização serem incorporados à base. Gêmeo: `no_reload_sync=1` / `Flags::noReloadSync`.
- T0: novo `proxy/core/tests/reload_sync.cpp` (save mais antigo, segunda recarga, progresso apenas no save, cada um com o gêmeo detectado); falhou antes da correção. 500 sessões de fuzz e os 10 gêmeos existentes passam; DLL compila.
- Jogo real, `tools/qa.sh 'same-process'`: B limpo perde e depois recupera o painel `0x64` e a porta `0x34eda` (log mostra "save reload suspected"), nenhum processo reiniciado, B não emitiu eventos, ambos os mundos idênticos; B mutante permanece sem ambos. `tools/qa.sh` completo depois: 17 cenários ALL OK, saída 0. Verificações de save, cursor e 30,0 fps passam; slots liberados.

#### <a id="derived-6"></a>Deduções

- Um carregamento no mesmo processo não tem sinal de sessão, então a regressão de progresso é a única evidência disponível; a heurística poderia interpretar incorretamente uma porta real que fecha.

#### <a id="unknowns-6"></a>Desconhecidos

- Se alguma porta do jogo fecha no jogo normal (acionaria nova estabilização e ressincronização indevidas: inofensivas, mas desperdiçam recursos). A sessão é incrementada em 1, então um reinício real no mesmo segundo que uma recarga poderia ser ignorado pelo par. Carregar um slot de save diferente ou um save de outra sessão não foi testado.

### <a id="follow-up-cables"></a>Continuação: cabos

#### <a id="observations-6"></a>Observações

- `Power_Cable` tem 268 entidades; 167 painéis têm um cabo como alvo. Todos são labirintos de 26+ nós, sem nenhum alcançável pelos bots antigos. O painel `0x293` (grade 5x5, 26 nós, cabo alvo `0x349`, energizado, labirinto simples com flag inicial `0x2` e final `0x1`) fica a 3 m do spawn e tem um cabo preto visível que brilha amarelo após a resolução.
- Resoluções naturais de `0x64` e `0x18af` não mudam palavra de cabo em nenhum jogo. Uma resolução natural de `0x293` muda exatamente um cabo em todo o mundo de A: `0x349` `+0xC4` e `+0xC8` vão de 0 -> 1.0 (dois outros cabos já estão acesos desde o início). B permanece 0. Outras diferenças de cabos entre A e B (`+0x18c`, ponteiros) são estado de carregamento por processo, não estado de resolução.
- O despachante de alvos do jogo é `exe+0xC24F0(target id, source entity)`: seleciona pelo descritor de tipo do alvo (Gauge, Pressure_Plate, Machine_Panel -> `0xC2890`, depois grava o id de origem em `+0x2C8` do alvo, Multipanel, Power_Cable -> `0x175EE0(cable, 0)`, Door -> `0x8EB60`, Light, Laser, Marker e outros). `0x175EE0(cable, 0)` acende o cabo. O loop pelos filhos `Power_Cable` na atualização de painel em `exe+0xB9E00..` só trata cabos marcados `:slider_cable` (pontes deslizantes), não esta cadeia.
- Entrada no painel: de frente a 3 m (posição em pé = posição do painel + 3 * (cos rz, sin rz), yaw = rz + pi, rz = 2*atan2(qz, qw) do quaternion do painel em `+0x34..+0x44`, z do olho igual ao z do painel; um teletransporte acima da altura do teto cai em outro lugar). O painel ocupa cerca de 222 px por unidade de suas coordenadas 0..1, o cursor começa no centro da tela e o movimento livre é 2 contagens por pixel. Um traçado restrito atrasa nos cantos, então o bot envia passos de 16 contagens e lê a contagem de nós traçados no painel `+0x228` (conta o início; a extensão final não a aumenta). Controle em malha fechada por essa contagem substitui estimativas de distância.
- Implementação (witness-coop): evento de tipo 4 (cabo aceso), assinaturas de protocolo v3, `GameCablePowerOnNow` (tipo e prólogo verificados, thread de renderização), detecção no núcleo com as mesmas condições de inicialização e cascata da energia de painéis, proteção contra eco, novas tentativas, snapshots; `Flags::noCableSync` / `no_cable_sync=1`. T0: novo `cable_sync.cpp` falhou antes da mudança; limpo, recuperação após reinício e quatro gêmeos passam; 500 sessões de fuzz e 10 gêmeos passam; DLL compila. `wbot_maze.py` resolve qualquer labirinto simples por BFS; `wstatedump.py`/`state_diff.py` informam cabos acesos.
- Jogo real, `tools/qa.sh 'cable maze'`: A e B limpos correspondem em painéis resolvidos, painéis energizados (238) e cabos acesos (3), B não emite evento de cabo, e um B novo recupera o cabo aceso após a confirmação dos eventos; o mutante deixa exatamente `0x349` apagado em B. Verificações de save, cursor e 30,0 fps passam. `tools/qa.sh` completo depois: 19 cenários ALL OK, saída 0.

#### <a id="derived-7"></a>Deduções

- Chamar o despachante no painel resolvido replicaria todos os tipos de alvo, incluindo o vínculo de retorno de origem `+0x2C8` que nosso caminho de energia de painéis não define; hoje, apenas alvos de portas e cabos são cobertos por eventos dedicados.

#### <a id="unknowns-7"></a>Desconhecidos

- Os outros painéis que acionam cabos, `:slider_cable`, desligamento de cabos e o que `+0x2C8` e as flags `+0x37c` fazem visualmente. Se o brilho do cabo também precisa que o traçado do painel de origem seja mostrado em B. Capturas de B junto ao cabo não foram comparadas (o streaming de B não carregou aquela área após um teletransporte); a asserção é sobre memória.

### <a id="random-packet-loss-t2"></a>Perda aleatória de pacotes (T2)

- `proxy/coop.cpp` de witness-coop: chaves de configuração `drop_pct` e `drop_seed` (LCG determinístico por semente) descartam datagramas de saída apenas na interceptação de envio.
- `tools/suite.py`: cenário "30% random packet loss" (A semente 7, B semente 11, precisam ser idênticos) e "MUTANT: no resend + 30% random loss" (precisam divergir).
- Executado: `make -C proxy/core test` (ALL OK), `make -C proxy` (compila), `tools/qa.sh random`: ambos PASS (base com perdas idêntica, A reenviou 21; mutante: 2 diferenças).
- Ressalva: a divergência do mutante depende de quais datagramas a semente descarta. Determinística por semente, mas os tempos dos pacotes ainda variam, então esta é uma execução. Instabilidade entre execuções repetidas: `unknown`.

### <a id="second-panel-for-the-t2-bot-resolved"></a>Segundo painel para o bot T2 (resolvido)

Uma tentativa inicial de automatizar o segundo painel do tutorial (`0x182`) parou: com a orientação do painel e o círculo inicial desconhecidos, quatro vistas por teletransporte não mostraram tela de puzzle. Ler o grafo do painel (posições, flags e conexões em `+0x3B4..+0x3D8`, como faz o randomizer) e uma captura do backbuffer da vista de frente resolveu isso; a seção do segundo puzzle acima (Continuação: segundo puzzle do tutorial) registra o bot funcional e o bug da porta zero que ele revelou.

