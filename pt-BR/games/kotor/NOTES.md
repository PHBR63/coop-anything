# <a id="star-wars-knights-of-the-old-republic-2003--session-notes"></a>Star Wars: Knights of the Old Republic (2003): notas da sessão

Sessão do agente: 2026-10-18. Repositório: cranebeaker/coop-anything (clonado em `<workspace>/coop-anything`).

## <a id="0-triage--game-identity-rule-5"></a>0. Triagem: identidade do jogo (regra 5)

Observado na máquina de teste (somente leitura, instalação não modificada):

- Loja: Steam. AppID **32370** (verificado na API da loja: appdetails?appids=32370 retorna "STAR WARS™ Knights of the Old Republic™"; 32350 é Starfighter, não KOTOR).
- Instalação: `<Steam library>\steamapps\common\swkotor`
- `appmanifest_32370.acf`: StateFlags=4 (instalado), buildid **4143502**, installdir `swkotor`.
- Executável principal: `swkotor.exe`, tamanho 4.395.008 bytes, FileVersion/ProductVersion **1.0.3.0**, ProductName "Star Wars: Knights of the Old Republic".
- SHA-256 de swkotor.exe: `34E6D971C034222A417995D8E1E8FDD9F8781795C9C289BD86C499A439F34C88`
- Motor: BioWare **Odyssey** (derivado de Aurora), 32 bits, binário fechado, sem código de rede ou extensão de scripts.
- Família do sistema: Windows x64.
- Objetivo da sessão: **campanha cooperativa on-line com amigos** (sem tela dividida).

Observações da instalação (talvez relevantes depois):

- `binkw32.dll` (220.672 B) E `binkw32_real.dll` (375.808 B) presentes, além de `hires_patcher.exe/.pl`, `patch.erf`. Esse par normalmente indica um proxy bink instalado em algum momento (correção/carregador). Não se sabe qual nem quando.
- `32370_install.vdf` na pasta do jogo (artefato do script Steam; conteúdo = instalação no registro, incluindo strings SecuROM, do próprio Steam; sem SecuROM na compilação Steam).
- Pastas `Override/`, `logs/` existem → jogo já executado e possivelmente modificado.
- KOTOR II (aplicativo Steam **208580**) **não instalado** neste PC (sem ACF ou pasta).

## <a id="1-research--existing-co-op-attempts-phase-1"></a>1. Pesquisa: tentativas cooperativas existentes (etapa 1)

O diretório (data/directory.yaml, conferido em 2026-10-16) tinha exatamente uma entrada:

1. **reone multiplayer**: https://github.com/seedhartha/reone, decomp-port, protótipo, 3 jogadores, não testado, última atividade 2025-04. Reimplementação de motor (desenvolvimento independente, GPL-3.0, C++). Artigo GameStar (https://www.gamestar.de/artikel/sw-kotor-koop,3360443.html) descrevia demonstração multiplayer v0.5.1, só jogabilidade básica. Projeto de origem diz "mid-stage".

Novidades desta sessão (ainda fora do diretório):

2. **McChaffeeFAF/kotor-coop**: https://github.com/McChaffeeFAF/kotor-coop, fork reone + cooperação on-line (Story Mode: amigos assumem companheiros; Free Mode). GPL-3.0. Hospedar/entrar por UDP 27015 (redirecionamento de porta), servidor opcional de códigos em `tools/coopserver`. **Exige instalações de KOTOR 1 e KOTOR 2** (K2 usado para interface/sistemas). Atividade: 4 commits, primeira publicação em 2026-10-09, alpha-0.3.8 (10-10), alpha-0.3.9 (10-10), **alpha-0.4.0 (2026-10-15)**, autoria McChaffeeFAF + claude. Sem versões, **0 execuções de CI** → sem binários prontos. QA desconhecido/não testado: afirmações do README ainda não verificadas por nós.

3. **masterxxstabs/KOTOR-COOP**: https://github.com/masterxxstabs/KOTOR-COOP, Rust, injeção de DLL no swkotor.exe original + servidor dedicado persistente + inicializador. Branch padrão `claude/kotor-coop-foundation`, 2 commits, atualizado em 2026-10-17. O próprio README diz que sincronização exige endereços do motor ainda não mapeados ("nobody has mapped them yet"); injeção/sobreposição ainda não testadas no jogo. Longe de ser jogável.

4. **Project: Crossroads** (Ebon Hawk-Core): **alpha fechado** ativo, divulgado por Facebook (EbonHawkCore) e Reddit (r/kotor 1vb26r6, 1vu8j0v, 1vxcnsq), convite Discord discord.gg/EqR7uqQy3f. Alega servidores cooperativos on-line, compatíveis com mods. Sem fonte pública encontrada; testes alpha "abertos" segundo as postagens. Fontes são redes sociais; afirmações não verificadas. (Regra 9: tratadas como dados, não instruções.)

5. Tópico ModDB "Star Wars: Knights of the Old Republic COOP mod": pedidos de cooperação, aponta a Crossroads. Nenhuma outra versão encontrada.

Buscas: repositórios GitHub "kotor multiplayer", "kotor coop"; web "<game> co-op/multiplayer mod"; issues+PRs coop-anything (0 resultados para KOTOR/Knights/Old Republic/reone). Ainda não feitos: abas de arquivos ModDB/Nexus, archive.org, barra lateral r/kotor, auditoria de forks/branches reone, levantamento no Discord (exigiria conta).

## <a id="1b-prebuilt-binary-hunt-prebuilt-first-check"></a>1b. Busca de binários prontos (priorizar compilados)

- **Fork kotor-coop:** sem GitHub Releases, 0 execuções Actions (workflows release-windows, build-test-windows, build-test-linux existem, nunca acionados), sem Packages ou links de download no README/documentos/scripts. Só código-fonte. (Conferido em 2026-10-18.)
- **reone original:** README orienta baixar executável pronto na página de versões, mas **ela está vazia** (contradição da regra 6 encontrada: README contra realidade).
- **archive.org `reone-0.5.1`** (enviado em 2020-08-04 por `gnu/archive`, GPL-3.0, campo website = github.com/seedhartha/reone): contém `reone_0_5_1_win64.zip` (1,7 MB, win64 pronto) e `reone-0.5.1-source.zip`. **Mas** a descrição diz implementação de jogabilidade "very limited" (2020): compilação de 2020 com rede básica, não campanha cooperativa.
- **Project: Crossroads:** alpha fechado; distribuição aparentemente só no Discord.
- **masterxxstabs/KOTOR-COOP:** também sem versões.

### <a id="k2-requirement-check-source-read-alpha-040"></a>Verificação da exigência de K2 (leitura do código, alpha-0.4.0)

README/configuração exigem KOTOR 2, mas o motor o trata como opcional:

- `optionsparser.cpp:77`: padrão de `--k2game` é `""` (vazio).
- `engine.cpp:270-302`: erro só com `--hud k2` sem `--k2game` ou caminho k2 informado que não é instalação válida. HUD K1 (`--hud k1`) não precisa de K2.
- `coopgame.cpp:877`: calcula impressão digital K2 somente `if (!launch.k2Path.empty())`.
- MAS `tools/package/files/scripts/setup.ps1:37` exige pasta K2, e `launcher.ps1:64` usa `hud=k2` por padrão (lançaria erro sem K2).
- **Dedução:** cooperação só com K1 provavelmente funciona com `hud=k1` e `k2game` indefinido; seria preciso contornar configuração automática/editar parâmetros. Não verificado; exige compilação para testar.

## <a id="2-derived--guesses-labelled"></a>2. Deduções / hipóteses (identificadas)

- Dedução: kotor-coop é atualmente o único caminho *recente, de código aberto e campanha cooperativa* que atende ao objetivo sem criar código de rede do zero.
- Hipótese: alpha-0.4.0 provavelmente compila por `tools/package/make_tester_package.ps1`; sem artefatos CI, precisa compilar fonte (VS2022 + vcpkg).
- Hipótese: binkw32_real.dll sugere correção anterior de terceiros (proxy bink); identificar antes de copiar instalação para testes, ou a cópia a herdará.

## <a id="3-unknowns"></a>3. Desconhecidos

- Se kotor-coop realmente permite campanha completa do início ao fim (teste com bots/pessoas necessário).
- O que sincroniza (jogadores/missões/inimigos/mundo/itens), com qual qualidade e detalhes do modelo de rede.
- Se reone original já permite concluir KOTOR 1 (fork herda limitações).
- Crossroads: código, licença, escopo da sincronização, todos desconhecidos sem Discord.
- Se a instalação de teste tem mods (conteúdo de Override/ ainda não inventariado).

## <a id="4-blockers-and-decisions"></a>4. Bloqueios e decisões

- KOTOR 2 (aplicativo 208580) ausente, exigido pelo README; mas veja 1b: motor o trata como opcional, e `--hud k1` funciona sem ele (agora verificado, seção 5).
- Ferramentas de compilação instaladas, compilação concluída (seção 5).
- Ações da conta GitHub (issue de indicação de jogo, fork, PR em rascunho) abertas em sessão posterior.

## <a id="5-build--first-run-severity-verified-2026-10-19"></a>5. Compilação e primeira execução (grau: verificado em 2026-10-19)

Compilado `McChaffeeFAF/kotor-coop` alpha-0.4.0 do código-fonte na máquina de teste.

Ferramentas:

- Visual Studio Build Tools 18 (2026), MSVC 14.51. Gerador: `-G "Visual Studio 18 2026"`.
- vcpkg em `<vcpkg dir>` (precisou sair de caminho com espaços: ffmpeg recusa compilação neles). Todas as 69 dependências instaladas, saída 0 (~44 min).
- CMake encontrou GameNetworkingSockets (transporte cooperativo).

Resultado (Release, `--parallel 8`, saída 0, zero erros):

- `build/bin/engine.exe` (8,77 MB): motor do jogo.
- `launcher.exe` (0,35 MB): interface de configurações gráficas/áudio do reone original. **NÃO é inicializador cooperativo** (chama `engine` sem opções host/join); veja §8. Inicializador cooperativo é `tools/package/files/scripts/launcher.ps1`, via `Play KotOR Co-op.cmd`.
- `texgen.exe`, `toolkit.exe`, `dataminer.exe`, `gff2json.exe`, `nsscomp`.
- DLLs de runtime reunidas ao lado (avcodec, GameNetworkingSockets, libcrypto, protobuf…).

Testes unitários: `build/bin/tests.exe` → **3.650 testes de 526 suítes, 3.639 aprovados, 0 reprovados, 11 pulados** (dependentes de K2 ou opcionais). Saída 0.

### <a id="first-real-run--k1-only-no-kotor-2-verified"></a>Primeira execução real: só K1, sem KOTOR 2 (verificado)

Executado contra cópia isolada, `--hud k1`, sem `--k2game`:

```
engine.exe --game <copy> --hud k1 --headless 1 --control-port <port>
```

Dois fatos sobre a estrutura de testes aprendidos (ambos consumiram tempo):

- **Saída do console NÃO vai para stdout.** Console mantém buffer em memória renderizado na tela (`apps/engine/console.cpp`). Redirecionar stdout não captura nada.
- **Interface de automação é a porta TCP de controle** (`--control-port N`, 127.0.0.1, comandos delimitados por nova linha, uma resposta JSON por linha: `{"id":n,"cmd":"...","ok":true,"output":[...],"frame":n,"time":s,"tick":n}`). Esse é o caminho do controlador bot. `--commands-file` também existe, mas sem destino de saída ou encerramento implícito; acrescente `quit` no fim ou o motor executa para sempre.
- **`Start-Process -ArgumentList` divide caminhos nos espaços.** Coloque entre aspas argumentos com espaço, ou o motor falha com `directory_iterator: cannot find the path "…\Default"`.

O que a execução comprovou (dados K1 reais, não simulados):

- Módulo `end_m01aa`, área `m01aa` carregados: abertura da **Endar Spire**.
- Criatura do jogador criada: nome sorteado "Galon Baillen", posição (15.4, 20.1, -1.3), HP 6/6, nível 1, `faction:0`, `commandable:true`.
- **Trask** presente (ID 7), HP 36/36, nível 3, roupa + pistola blaster equipadas, `dialog:end_trask01`: companheiro do tutorial.
- Objetos reais enumerados: `end_locker01` (baú, 6 itens), `end_door01` (diálogo `end_door01`, keyRequired), `end_trig02`, pontos de referência, cadeiras.
- Simulação a 30 Hz; `tickstatus` → `tick=7 rate=30 gate=0 … rng.gameplay.seed=1792471790 rng.violations=0`. Simulação determinística relata **0 violações**.
- `quit` na porta de controle encerra corretamente.

Conclusão: o fork executa KOTOR 1 sem instalar KOTOR 2, sem interface, e é controlável por bot pelo canal de controle.

## <a id="6-two-client-co-op-qa-severity-verified-2026-10-20"></a>6. QA cooperativo com dois clientes (grau: verificado em 2026-10-20)

Criado `test/harness.ps1`: inicia **dois clientes reais do motor** num PC (host e convidado, ambos sem interface), conecta por UDP localhost com GameNetworkingSockets, controla pelas portas TCP e verifica estado compartilhado. Exibe um `[PASS]/[FAIL]` por verificação e termina com `RESULT: PASS|FAIL`.

Resultado: **23/23 verificações PASS, três execuções limpas consecutivas.** `powershell -File test/harness.ps1`.

O que a suíte comprova (observado, não inferido):

- Host hospeda automaticamente (`--host 27125`), convidado `coopjoin 127.0.0.1:27125` → `state:"joined"`.
- Host vê `players:2`; **0 pacotes perdidos / 0 fora de ordem** na rota cliente.
- **Impressões digitais: `k1:"key=ebe0162bc593f19e …"`, `k2:"absent"`**: sessão realmente sem KOTOR 2 instalado, razão do caminho só K1.
- Story Mode atribui companheiro automaticamente: `slot.status:"assigned"`, `slot.tag:"end_trask"`, `slot.id:330`.
- Convidado carrega módulo do host: `module:"end_m01aa"`, `loaded:true`, `appliedTick:302`, **`replicas:103` objetos do mundo replicados e vinculados** (`bound:103`, `spawned:1`).
- Movimento pelo convidado: `coopmove` → host `accepted:true`; companheiro move (15.42,20.12) → (17.46,20.15), cópia do convidado acompanha exatamente (`pos == localPos`, diferença 0,000). Host tem autoridade; convidado envia só intenção.
- `quit` em ambos encerra corretamente.

### <a id="three-harness-facts-that-cost-the-most-time-all-now-verified"></a>Três fatos que mais consumiram tempo (agora verificados)

1. **`newgame` inicia filme introdutório, que SEGURA a simulação.** Com filme na tela, motor retorna cedo da atualização (`src/libs/game/game.cpp`, caminho `if (_movie) … return;`), então `_coop->afterTick()` não roda. Host nunca detecta o módulo (`generation` fica 0), não envia `ModuleInfo`, convidado não carrega nada. Clique humano remove; na estrutura de testes, envie **`skipmovie`**.
2. **Conversa inicial faz host responder `busy` a todo comando do convidado.** `coopcommand.cpp` rejeita com `CommandReject::Busy` quando `!acceptsInput(game.currentScreen())`, durante conversa. É arquitetura autoritativa correta (host conduz conversas). Remova com salto automático embutido: `autoskipenable 1` + `autoskipentries 1 …` + `autoskipreplies 1 …`.
3. **Host relata `in_game` brevemente *antes* da introdução**, fazendo uma única consulta retornar cedo. Exija estabilidade por várias verificações com contador de atualizações avançando antes de chamar de "jogabilidade normal".

Também: companheiro atribuído ao cliente é `slot.id` em `netstatus` (ID do host), não mapa `controlled` do host. E `weak_ptr` do módulo do host mais comparação `==` fazem "módulo mudou" ser observado uma vez por visita; funciona na prática, mas importa na leitura da replicação.

Isso alcança **nível de QA: automated** no caminho Story Mode com dois clientes. Pendências: loja e minijogos ainda sem verificações.

## <a id="7-extended-co-op-qa-gameplay-gates-severity-verified-2026-10-20"></a>7. QA cooperativo ampliado: verificações de jogabilidade (grau: verificado em 2026-10-20)

`test/harness.ps1` ampliado de 23 para **55 verificações**, adicionando seis fluxos sobre entrada/movimento/encerramento. Resultado: **55/55 PASS, duas execuções limpas consecutivas** (`coop2-suite7.log`, `coop2-suite8.log`).

Novas verificações (cada uma considera ambos os participantes):

- **G9 replicação de diálogo.** Host na conversa inicial de Trask (`end_trask01`); cliente mostra réplica da mesma cena: `conversationReplica` = mesmo diálogo, índice, texto e interlocutor, respostas e tomada de câmera completas (`entry:51`, olho/alvo). `coopmove` do convidado durante diálogo recebe **`busy`** do host (`rejects:{"busy":1}`): host Story conduz conversas por definição.
- **G10 carteira compartilhada.** Host `givegold 1234` → inventário compartilhado cliente mostra `credits:1234`, igual a `partyGold` do host.
- **G11 recipientes.** Convidado clica no baú `end_locker01` (ID 85, 6 itens): companheiro caminha, host abre tela de recipiente própria do cliente (`viewing:85`, 6 itens com tags), convidado executa `cooptake all`, itens entram no inventário compartilhado (`containerItems:0`, `inventory.items:6`). `commandsAccepted` aumenta **sem novas rejeições**.
- **G12 replicação de subida de nível.** Companheiro só sobe até o nível do host; primeiro aumenta-se o jogador host (XP + `levelup` até 13), depois dá-se XP suficiente ao companheiro para `isLevelUpPending`. Cliente vê `sheet.levelUp:true`; convidado usa `cooplevelup` pelas mesmas telas abertas pelo botão HUD, e host aplica: **nível 3 → 4**, sem novas rejeições.
- **G13 combate.** Criatura de modelo `crsghost10` criada junto ao companheiro, selecionada e tornada hostil (`setfaction 1` → `hostile:true`, distância 3,4). Cliente replica, `coopattack` é aceito, e `dumpstate.combat` do host ganha rodada com **`attacker == companion, target == creature`**; companheiro informa `inCombat:true` com esse `attackTarget`. (Perda de HP depende de dados/arma; verifica-se a *rodada* de combate, determinística.)
- **G14 transição de área.** Host `warp end_m01ab` → cliente acompanha: `module` de `end_m01aa` → `end_m01ab`, `generation` 1 → 2, `loaded:true`, **34 réplicas reconstruídas e vinculadas** para novo convés; ambos concordam no nome do módulo.

### <a id="two-facts-the-new-gates-depend-on-verified"></a>Dois fatos exigidos pelas novas verificações (confirmados)

1. **Subida de nível do companheiro limitada pelo nível do host.** `hostSendSheets` (`coopinventory.cpp`) define `allowed = companionLevel < hostLevel`, e `validateCoopLevelUp` (`coopprogress.cpp`) rejeita com `LevelUpUnavailable` quando `level + 1 > hostLevel`. Jogo novo tem jogador no nível 1 e companheiros no 3; **convidado não sobe até o host subir primeiro**. Todo teste precisa aumentar o host antes.
2. **Contadores de rejeição cumulativos.** G9 provoca `busy` deliberadamente; verificações posteriores avaliam aceitação pelo *delta* de `commandsAccepted` / `rejects` por motivo, não por "rejects vazio". Comparação com mapa absoluto falha por `busy:1` antigo.

### <a id="reusable-console-commands-these-gates-use"></a>Comandos de console reutilizáveis nestas verificações

`givegold`, `givexp`, `levelup`, `spawncreature`, `selectobjectbyid`, `setposition`, `setfaction`, `warp` (host); `coopuse`, `cooptake`, `coopclose`, `cooplevelup`, `coopattack` (convidado). Tag do baú Endar Spire: `end_locker01`; modelo hostil padrão: `crsghost10` (facção precisa ser 1 para combate).

## <a id="7b-extended-co-op-qa-round-2-pause-doors-exits-severity-verified-2026-10-20"></a>7b. QA ampliado, rodada 2: pausa, portas, saídas (grau: verificado em 2026-10-20)

Suíte de 55 para **77 verificações**. Resultado: **77/77 PASS, duas execuções limpas consecutivas** (`coop2-suite9.log`, `coop2-suite10.log`). Três fluxos, cada um verificando ambos:

- **G16 propagação de pausa.** Qualquer um pausa o mundo compartilhado. Convidado envia `cooppause 1`; host controla e aplica a ambos, identificando solicitante: ambos relatam `paused:true`, `pausedBy:"GuestPlayer"`. `cooppause 0` retoma (`paused:false` dos dois lados). Pausa do cliente é uma *solicitação* (`CommandType::Pause`) executada pelo host, não pausa local.
- **G17 convidado abre porta.** Portas replicadas: cliente tem cópia da porta do host. `coopdoor <host id>` leva companheiro à porta e envia abertura; host abre a real, réplica mostra `open:true`. **Companheiro precisa estar ao alcance**: primeiro caminha até a porta (como jogador que se aproxima e clica), esperando distância de até 2,5 unidades. Porta de teste: `droidshop` em `tar_m02ab` (destrancada). `commandsAccepted` do host aumenta.
- **G18 confirmação para saída de área.** Companheiro que entra num **gatilho de saída ligado a módulo** solicita saída do grupo. Host inicia confirmação identificando destino e iniciador (`destination:"tar_m03ab"`, `initiator:"GuestPlayer"`, `players:2`); ambos respondem `coopready 1`, e **ambos vão para `tar_m03ab`** (`generation` cliente 3 → 5 nas duas transições). Gatilho: `tar03_npcext` em `tar_m03aa`.

### <a id="two-flow-facts-these-gates-depend-on-verified"></a>Dois fatos de fluxo exigidos (confirmados)

1. **Ação de convidado exige companheiro ao alcance.** `coopdoor` é *aceito* (vinculado ao ator, `seq` atribuído) mesmo a 50 unidades, mas host nunca abre a porta. Clique do cliente caminha antes; estrutura de teste precisa fazer igual (`coopmove` até objeto, depois ação). Aceito ≠ realizado: verifique mudança do mundo no host, não aceitação.
2. **Só gatilhos ligados a módulo iniciam confirmação.** `hostCheckClientExits` (`coopflows.cpp`) pula gatilhos com `linkedToModule()` vazio ou inativos; por isso, maioria da Endar Spire nunca a inicia. `tar03_npcext` inicia. Conversa por script também pode tirar host da jogabilidade durante caminhada (responde `busy`); teste reafirma jogabilidade e tenta caminhar algumas vezes.

### <a id="flows-that-are-not-reachable-from-the-control-port-recorded-not-gated"></a>Fluxos NÃO acessíveis pela porta de controle (registrados, não testados)

- **Loja.** `coopbuy`/`coopsell`/`coopoffer` só agem com tela de loja aberta, que só abre quando script próprio chama `OpenStore` (rotina 378) em conversa (`coopcommand.cpp`, `coopfree.cpp`). Não há recurso de console para criar loja nem iniciar conversa. Sem verificação.
- **Bancada / laboratório.** Mesmo padrão: tela do convidado exige `ShowUpgradeScreen` por script. `coopbench state` e `coopmg` respondem corretamente sem tela (`{"screen":false,"open":false}` / `{"active":false}`); só contrato "nada aberto" é observável, sem valor suficiente para teste.
- **Minijogo (swoop/torreta).** `startMiniGame` exige campo `MINIGAME` da área (`hasMinigame()`); pistas swoop são preparadas por **scripts** na corrida, não por dados estáticos. `showgallerymode swoop` falha em todos os módulos sondados (`end_m01aa`, `tar_m02aa/ab/03aa`, `ebo_m12aa/40aa`, `danm14aa`, `kas_m22aa`). Lógica cooperativa testada unitariamente (`test/game/coopminigame.cpp` chama `game.begin(...)`), mas integração não acessível pelo console. Sem verificação.
- **Free Mode / criação de personagem.** `coopnewguest` exige `clientNeedsGuest()` (cliente Free Mode sem personagem), outro modo de sessão. Fora do escopo da suíte Story.

### <a id="still-open-coverage-honest-gaps"></a>Cobertura ainda aberta (lacunas reais)

Classe/criação de personagem, loja, bancada/laboratório, minijogo e Free Mode continuam sem verificações, veja acima. Próximas adições acessíveis exigiriam sessão Free Mode ou módulo com comerciante/bancada por script que o teste alcançasse caminhando com convidado.

## <a id="8-packaging-build--verify-the-shipped-package-severity-verified-2026-10-20"></a>8. Empacotamento: compilar e verificar o pacote distribuído (grau: verificado em 2026-10-20)

Etapa 7 já implementada no fork em `tools/package/`; trabalho aqui foi **compilar, testar e corrigir o que falhou**, não escrever inicializador. Dois bugs reais encontrados e corrigidos, seguidos de execução completa host->entrada pelo pacote.

### <a id="what-packaging-already-is-source-read"></a>O que já existe no empacotamento (leitura do código)

| Componente | Função |
|---|---|
| `tools/package/make_tester_package.ps1` | ZIP portátil: `engine.exe`, DLLs de runtime, runtime VC++ local, scripts, `texgen.exe`; recusa distribuição se entrar arquivo de jogo. |
| `tools/package/files/scripts/launcher.ps1` | Inicializador WinForms de um clique: detecta instalações, escreve `reone.cfg`, Host / Join / Play solo. |
| `Host.cmd` / `Join.cmd` / `Play KotOR Co-op.cmd` / `Setup.cmd` | Wrappers de comandos. |
| `tools/package/linux/` | Equivalente bash, com `test_launcher.sh` (32 verificações em árvores sintéticas). |
| `tools/coopserver/` | Serviço opcional de código de entrada + retransmissão TURN (Python/Docker). |

**`launcher.exe` NÃO é o inicializador cooperativo.** É a interface gráfica/áudio do reone original (chama `engine` sem opções host/join). O cooperativo é `launcher.ps1`, via `Play KotOR Co-op.cmd`. Fácil confundir; não distribua nem documente `launcher.exe` como interface cooperativa.

### <a id="the-engine-reads-reonecfg-from-its-working-directory-verified"></a>Motor lê `reone.cfg` da pasta de trabalho (verificado)

`--game`, `--hud`, `--coop-name` e outros podem ficar em `reone.cfg` (escrito pelo inicializador), com o restante na linha de comando; opções da linha sobrescrevem o arquivo. **`reone.cfg` lida corretamente com espaços nos caminhos** (analisador Boost preserva valor inteiro da linha), verificado com instalação real acessada por pasta com espaços. Só argumentos na *linha de comando* exigem aspas, problema de `Start-Process`, não do motor.

### <a id="bug-1-fixed-the-package-shipped-the-wrong-vc-runtime"></a>Bug 1 (corrigido): pacote incluía runtime VC++ errado

`make_tester_package.ps1` procurava pasta redistribuível `Microsoft.VC*.CRT` nas instalações Visual Studio e ordenava por **nome**, decrescente. `2019\BuildTools` vem depois de `18\BuildTools`; copiava **VC142 (14.29)** junto de motor compilado com **VC145 (14.51)**. `msvcp140.dll` local escondia runtime novo do sistema, e motor morria ao iniciar com `0xC0000005` (violação de acesso), sem log ou saída.

- Evidência: removendo as 9 DLLs CRT incluídas, mesmo `engine.exe` rodava (`--help` saída 0). Com elas, saída `-1073741819`.
- Correção: ler conjunto de ferramentas pelas importações do motor (`boost_program_options-vc145-...` -> `VC145`), procurar CRT correspondente primeiro, recorrer ao mais novo e avisar incompatibilidade. Também copiar redistribuíveis por cima de arquivos homônimos vindos de `build\bin`.
- Após correção, CRT do pacote inteiro é `14.51.36247.0`, e motor funciona.

### <a id="bug-2-fixed-the-launcher-refused-to-start-without-kotor-2"></a>Bug 2 (corrigido): inicializador recusava começar sem KOTOR 2

Inicializador exigia **ambos** (`Update-Rows` condicionava Host/Join/solo a K1 *e* K2), com `hud` padrão `k2`. Jogador só com K1 recebia "Both games are needed", com **três botões desativados**, até Play solo, embora K1 isolado seja plenamente verificado no motor (`--hud k1`, sem `--k2game`, `k2:"absent"`).

- Correção (Windows `launcher.ps1` + `setup.ps1`, Linux `setup.sh`): KotOR II opcional. Prontidão depende só de K1; `hud` acompanha instalações; seletor HUD fixa visual KotOR sem K2; `Setup` pula pergunta K2 com Enter; READMEs dizem opcional. Auxiliar `cfg_remove` adicionado no Linux e caso K1 isolado em `test_launcher.sh`.
- Autoteste antes/depois (`KOTOR_LAUNCHER_SELFTEST=1`), K2 ausente: `host enabled: False` + "Both games are needed" -> `host enabled: True` + dica de redirecionamento/entrada, linha K2 como "Optional".

### <a id="verified-end-to-end-severity-verified-2026-10-20"></a>Verificado de ponta a ponta (grau: verificado em 2026-10-20)

1. `test_launcher.sh`: **32/32** verificações em árvores sintéticas passam (31 antes; edição inicial quebrou entrada por endereço ao reatribuir `$root`, corrigido restaurando pacote do teste 8 para 9).
2. Pacote criado: ZIP 24,8 MB, sem arquivos de jogo (proteção aprovada), runtime VC145, todos os scripts.
3. **ZIP recém-extraído** executa: porta de controle ativa, "Co-op: host session, mode story", chaves K1 presentes, sem K2.
4. **Host->entrada pelo pacote: 9/9 verificações** (`package-e2e.log`). `engine.exe` empacotado hospedou, segundo `engine.exe` empacotado entrou por `127.0.0.1:<port>`, ambos em `end_m01aa`, replicação limpa (`unmatched:0`, `violations:0`, `replicas:102 bound:102`), tráfego bidirecional, `k2:"absent"`.

Nota: porta de controle recebe **comandos de texto simples delimitados por nova linha** e responde com linha JSON. Enviar objeto JSON produz `Unrecognized command`: resposta é JSON, solicitação não.

Execução local: `powershell -File pkgtest.ps1` (fora do repositório; aponta à instalação isolada e pacote compilado).

## <a id="9-publishing-the-packaging-fixes-severity-verified-2026-10-21"></a>9. Publicação das correções de empacotamento (grau: verificado em 2026-10-21)

Ambas **publicadas**: branch `fix/packaging` enviada ao fork e aberta como PR no projeto original, **[McChaffeeFAF/kotor-coop#1](https://github.com/McChaffeeFAF/kotor-coop/pull/1)**.

- Commits `4ec25f9` (runtime VC++) e `5d45c38` (KotOR II opcional); 8 arquivos, +149/-48.
- Rebase sobre `main` atual original, **alpha-0.4.4** (`c56a05e`): quatro versões avançaram desde alpha-0.4.0 usado nas correções.
- Conflitos: projeto original já mudara padrão `hud` de `k2` para `k1` (`launcher.ps1`, `setup.sh`) e adicionara suporte Steam Deck e melhor detecção (`linux/`). Nossa lógica condicional de HUD mantida sobre a deles, combinando descrição da detecção com KotOR II opcional.
- **alpha-0.4.4 ainda exige KotOR II**: `Update-Rows` continua percorrendo `@("k1","k2")` e desativa Host/Join/solo. Mudar apenas padrão HUD não resolveu o problema de quem só tem KotOR 1; correção segue necessária.

Verificado após rebase:

- Autoteste sem KotOR II: **`host enabled: True`**, com dica de entrada e linha II opcional (antes "Both games are needed" e tudo desativado).
- `linux/test_launcher.sh`: **todas as verificações do inicializador passam** (via Git Bash; WSL sem distribuição nesta máquina, então não pôde rodar por ele).
- Motor C++ intocado na branch; resultado de 77 verificações permanece válido e pacote compilado não mudou.

A suíte está publicada junto ao relato em `games/kotor/test/harness.ps1` no núcleo; as 77 verificações são reproduzíveis, não uma afirmação inédita. Parametrizada (`-GamePath`, `-BinDir`, portas), sem caminhos privados; SHA-256 da cópia publicada `EB6DFAEB9CAE68C36149F62E036485EB93D3C0DDD2F64E8DB6E0E16E5B0D6D7E`. Reexecutada em 2026-10-21 da cópia publicada: **77 passed, 0 failed, RESULT: PASS**.

Nota: passe `-GamePath` e `-BinDir` como caminhos **absolutos**. A estrutura os entrega a `Start-Process`; caminho relativo resolvido pela própria pasta de trabalho falha sem abrir portas (`RESULT: FAIL`), parecendo falha real quando é só caminho incorreto.

### <a id="two-traps-hit-while-publishing-worth-knowing-for-any-repo"></a>Duas armadilhas da publicação (úteis em qualquer repositório)

**`>` em PowerShell 5.1 escreve UTF-16.** Redirecionar comando para arquivo (`git cat-file blob <sha> > f.ps1`) recodifica como UTF-16LE com BOM. Arquivo parece dobrar de tamanho e falha em qualquer hash. Isso consumiu tempo: fez um blob corretamente guardado parecer UTF-16 no banco de objetos Git, quando índice e commit sempre estiveram corretos. Para capturar bytes reais, use `cmd /c "tool > file"` ou leia/escreva com Python. Nunca confie em `>` quando houver hash.

**Fonte tinha codificação dupla, não apenas exibição errada.** Este arquivo tinha 37 travessões, setas, reticências, símbolos de marca e seção gravados como texto corrompido desde a criação: UTF-8 decodificado como cp1252 e recodificado uma vez. A evidência está nos bytes, não na aparência: travessão deveria ser `E2 80 94`, forma corrompida é `C3 A2 E2 82 AC E2 80 9D`; confira decodificação UTF-8 estrita sem `U+FFFD`. Git armazena sem reclamar; só o leitor nota. Estrutura de testes nunca afetada (ASCII e poucos comentários com caracteres de desenho de caixas).

Também: enviar ao núcleo exige remoto **fork** (`git push fork game/kotor`), não `origin`; `origin` é `cranebeaker/coop-anything`, onde esta conta tem só leitura, então push falha com HTTP 403.
