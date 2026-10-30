# <a id="fallout-new-vegas-2010"></a>Fallout: New Vegas (2010)

| | |
|---|---|
| Motor | Gamebryo (plugins xNVSE para hooks nativos) |
| Versões testadas | Steam **edição PCR / russo-polonês-tcheco**, appid `22490`, executável `1.4.0.525`, SHA-256 `40d5a7c967a1ec5df1dc19c25f8df3ca74480aa95e8755171567f1129a3001fa`; edição inglesa Steam appid `22380`, mesma compilação do executável |
| Projetos | NV:MP (multiplayer: jogadores, movimento de NPCs, combate; código de rede fechado); [fnv-coop](https://github.com/cranebeaker/fnv-coop) (camada de sincronização da história) |
| Versão distribuída | Cliente NV:MP 9.4 (2026-10-09); fnv-coop: ainda sem release GitHub, mas instalador, inicializador e guia do jogador estão na árvore |
| Nível de QA | automated (fnv-coop) / community-reports (NV:MP) |
| Última atualização | 2026-10-22 |

## <a id="where-things-stand"></a>Situação atual

Dois projetos, duas respostas diferentes. **NV:MP** oferece o mesmo mundo com outros jogadores: avatares, movimento de NPCs e combate, funcionando hoje. Cada jogador, porém, mantém seu registro de missões; a história não é compartilhada. **fnv-coop** é a camada de história que falta: sincronização com autoridade do host de etapas de missões, objetivos, resultados de diálogos, reputação e carma, planejada para rodar junto com NV:MP. É uma prévia para desenvolvedores: o código foi escrito, os testes automatizados estão aprovados, mas não há versão publicada para jogadores e a maior parte nunca foi executada no jogo.

Se alguém perguntar "podemos jogar a campanha juntos hoje à noite?", a resposta é: no mesmo mundo, sim; com uma história compartilhada, ainda não.

## <a id="existing-work"></a>Trabalhos existentes

- **NV:MP** - jogadores, movimento de NPCs e combate. Código de rede fechado (ENet, UDP 27015), sem sincronização de missões. Cliente 9.4 (2026-10-09) distribuído pelo [ClientDistribution](https://github.com/NVMP/ClientDistribution/releases) oficial; o inicializador e um espelho do SDK de servidor são públicos, mas os binários de cliente e servidor não. Última atividade em 2026-10.
- **fnv-coop** - camada de história descrita aqui. Licença MIT, roteiro de 10 etapas, desenvolvimento ativo (último commit em 2026-10-21). Última atividade em 2026-10.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- A lógica das missões roda como scripts de resultado das etapas no ESM. A sincronização captura os efeitos de uma etapa no host como uma transação e os aplica nos clientes sem reexecutar os scripts; a recompensa acontece uma vez e todos a veem.
- Form IDs não são localizados: a edição russa/PCR guarda textos em `FalloutNV_lang.esp`; portanto, não é um caso especial para uma camada cooperativa. O instalador já a aceita (appid `22490`, pasta `Fallout New Vegas enplczru`).
- O servidor de história do NV:MP não sincroniza missões: o cliente marca atores de missões como locais; NPCs de missões e estado das missões são por jogador. O anúncio de 2016 diz o mesmo: "each player maintains their own quest log" (cada jogador mantém seu próprio registro de missões).
- Salvamentos: fnv-coop usa o salvamento do host como mundo; os demais mantêm seus próprios personagens, inventários, níveis e habilidades.

## <a id="what-we-changed"></a>O que alteramos

Nada no jogo. Esta entrada registra o que uma sessão de agente encontrou e corrigiu no próprio [fnv-coop](https://github.com/cranebeaker/fnv-coop) (quatro bugs, branch `fix/portable-paths-and-non-ascii`, ainda não incorporada):

1. `tools/test_all.py` definia `NEEDS` duas vezes; a segunda prevalecia, e a verificação de pulo chamava uma tupla, falhando com `TypeError: 'tuple' object is not callable`.
2. `tools/installer/fnv_find.py` lia `libraryfolders.vdf` do Steam como UTF-8 com `errors="replace"`. O Steam o escreve na página de código ANSI do sistema quando ela não é UTF-8; caminhos de biblioteca com caracteres não ASCII viravam U+FFFD, e a instalação nunca era encontrada, silenciosamente. Agora: primeiro UTF-8, página ANSI como alternativa.
3. `tools/questdata/run_all.py` encaminhava `--data` a `effects.py`, mas não a `m1.py`; m1 não resolvia assinaturas de formulários e a lista de observação do extrator interno ficava vazia.
4. `tools/questdata/extract.py` e `plugin/dialogue/tools/gen_consent_messages.py` fixavam o caminho Steam dos EUA; em uma edição regional não liam nada. Agora, a pasta `Data` é encontrada pela descoberta da instalação (`FNV_GAME_DIR`, depois o caminho conhecido, depois `fnv_find.candidates()`).

A sessão também compilou fnv-coop do código-fonte, gerou dados de missões de uma instalação real (436 cenários, 1183 etapas), preparou uma versão para jogadores com o empacotador do próprio repositório (27 arquivos, SHA-256 conferido) e a instalou em uma cópia do jogo.

## <a id="qa"></a>QA

- fnv-coop inclui sua própria estrutura de testes: `python -I tools/test_all.py` executa todas as suítes (núcleo de sincronização com simulador de perda/reordenação, fuzzing de caos com sementes, teste prolongado de 4 jogadores, captura de efeitos e aplicação no convidado no jogo real, sincronização de etapas de missões entre duas cópias reais, variantes de mutação para quase toda verificação). É por isso que esta entrada declara `automated`.
- A sessão executou a suíte sobre `main` em `32e12cc` e as quatro correções acima, no Windows, x86, com instalação russa/PCR sem DLC. Resultado: resumo abaixo.
- NV:MP não tem estrutura própria de testes por scripts; o nível `community-reports` vem dos jogadores e da wiki.

## <a id="test-results-fnv-coop-rebased-to-32e12cc-ascii-build-dir"></a>Resultados dos testes (fnv-coop atualizado por rebase para 32e12cc, diretório de compilação ASCII)

Compilado e testado a partir do código em C:\FNVCoOp\dev\fnv-coop (HEAD dddcc34, branch fix/portable-paths-and-non-ascii), com a cópia da edição PCR. Quatro bugs de origem encontrados e corrigidos nessa branch (veja games/fallout-new-vegas/NOTES.md). Dados de missões regenerados da cópia do jogo (436 cenários / 1183 etapas; M1: 12 missões, 104 etapas, 35 objetivos, 1055 INFOs).

**Resumo da suíte completa (python -I tools\test_all.py, executada a partir de caminho ASCII):**
- **PASS** (26): preflight, lint (split strings/tool tests/parse), T1b flight analyzer (fast/full+twins), T4a pool, T4b scenarios, T5 chaos box, T6a bot actions/input driver, T6b co-op playbooks, T7 animcheck (+NPC fight twins), M3 actor ownership playbook/in-game proof, enemy sync (fight/handoff/spawn/corpse), questline sweeps (17 plans), Live wiring in-game proof, Release installer/launcher, L6 nvmp sigs/compat/tests + server hook
- **FAIL** (35): canonical nvcoop.dll build, L2+L1 runner, L3 questdata, L4 synccore, L5 hooks/L6 client patcher, L7 snapshot, L8 dialogue, L9 coverage, L10-L12 hooks, T1a/T2b, story-capture, combat-core/social-core/companions-crime/M4 combat-hooks/M4 real-time VATS/M3 actor port/enemy-anim, spawn-site arbitration/loot-area/world-time/guest intents, Live wiring, repo hygiene
- **Observação:** muitas falhas parecem relacionadas a limitações do ambiente de compilação desta máquina (cmake/ninja ausentes do PATH em algumas linhas de teste, problemas de caminhos/codificação do Windows). A suíte do instalador passou isoladamente (69 verificações, 0 falhas). Extração de dados das missões e suítes de empacotamento/inicializador passam.

## <a id="how-to-play"></a>Como jogar

**NV:MP, hoje.** Instale xNVSE 6.3.4 ou mais recente, execute o patcher de 4 GB, extraia o cliente 9.4 sobre a pasta do jogo e execute `nvmp_launcher.exe` como administrador. O host inicia um servidor local; amigos escolhem "Connect via IP" e informam `<host>:27015`. Redirecione UDP+TCP 27015 ou use uma VPN como Radmin. Conta Discord só é necessária para o servidor oficial ATK e alguns servidores públicos do SDK, não para sessão local privada.

**fnv-coop, quando houver uma versão distribuída.** Hoje é possível compilar: Python 3.11+, CMake >= 3.20, VS 2022 com `-A Win32`, cópia do xNVSE em `third_party/NVSE` e `cmake -S plugin -B build/L1 -G "Visual Studio 17 2022" -A Win32`. O instalador do repositório (`tools/installer/fnv_install.py`) encontra o jogo, verifica `1.4.0.525` e xNVSE presente, faz backup do que altera e instala `nvcoop.dll` em `Data\NVSE\Plugins`. O inicializador escreve `nvcoop.ini` (host escuta UDP 27960 por padrão, 2 a 4 jogadores) e pode testar porta e conexão antes de iniciar o jogo. O guia do jogador na árvore cobre o restante.

**Ambos juntos** é o formato pretendido: NV:MP para os corpos no mundo, fnv-coop para a história.

## <a id="known-issues"></a>Problemas conhecidos

- NV:MP não sincroniza missões, objetivos, estado de diálogos ou reputação: cada jogador mantém seu registro de missões; uma linha de missões pode falhar se outro matar um NPC de missão. VATS não está disponível no multiplayer (reduzir o tempo para vários jogadores não funcionou).
- fnv-coop é uma prévia para desenvolvedores: sem versão publicada nem fluxo de instalação concluído; a maioria dos recursos (inimigos, avatares, combate, saques, estado do mundo) está escrita, mas ainda não foi testada no jogo real. A etapa de sincronização de inimigos do roteiro está assumida por outro colaborador.
- Somente Windows e New Vegas `1.4.0.525`, Steam ou GOG. Missões de DLC ainda não são cobertas.
- A edição russa/PCR funciona com o instalador fnv-coop, mas a wiki NV:MP só menciona Steam e GOG; a PCR não foi testada aqui com NV:MP.

## <a id="next-steps"></a>Próximos passos

- Relatar e incorporar as quatro correções de fnv-coop, para que uma instalação russa/PCR seja encontrada e os dados de missões sejam gerados da pasta `Data` correta.
- Executar a suíte interna de fnv-coop com um salvamento real: uma ação humana (novo jogo, salvar) basta para liberar as verificações de mundo que nenhum teste por script consegue simular.
- Preparar a primeira versão pública de fnv-coop a partir da árvore já existente, para jogadores não precisarem compilar.
