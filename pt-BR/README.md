> **Português (Brasil)** · [English](../README.en.md) · [Relatório da tradução](../LOCALIZATION_STATUS.pt-BR.md)

<h1 align="center"><a id="co-op-anything"></a>Co-op Anything</h1>

<p align="center"><b>Qualquer jogo para um jogador. Seus amigos. Seu agente faz o trabalho.</b></p>

<p align="center">
<a href="https://ko-fi.com/cranebeaker"><img src="https://ko-fi.com/img/githubbutton_sm.svg" alt="Apoie-me no Ko-fi"></a>
<a href="https://discord.gg/EXGB49R82t"><img src="https://img.shields.io/badge/Discord-Join%20the%20server-5865F2?logo=discord&logoColor=white&style=for-the-badge" alt="Entre no Discord" height="36"></a>
<a href="https://coopanything.app"><img src="https://img.shields.io/badge/CoOp%3AAnything-Browse%20every%20co--op%20mod-1abc9c?style=for-the-badge" alt="Explore todos os mods cooperativos no CoOp:Anything" height="36"></a>
</p>

<p align="center">
<a href="#quick-start">Primeiros passos</a> ·
<a href="#how-it-works">Como funciona</a> ·
<a href="#what-you-can-co-op">O que você pode jogar em modo cooperativo</a> ·
<a href="#games-so-far">Jogos até agora</a> ·
<a href="#everyone-is-a-contributor">Contribua</a> ·
<a href="#faq">Perguntas frequentes</a> ·
<a href="#documentation">Documentação</a>
</p>

Quer jogar um jogo para um jogador com seus amigos? Direcione seu agente de programação com IA para este repositório. Ele pesquisa o que já existe, faz engenharia reversa do jogo e de seu motor quando necessário, cria ou corrige o modo cooperativo, **testa com bots dentro do jogo** e prepara um pacote para seus amigos instalarem com um clique e se conectarem pelo Steam sem redirecionar portas.

O céu é o limite. Todo jogo que roda no seu PC é um candidato.

**Vão jogar em um único PC?** O [Couchlink](https://github.com/cranebeaker/couchlink) executa uma cópia do jogo para cada jogador, cada um com sua própria parte da tela, seu controle ou teclado e mouse e, se quiser, sua própria conta Steam. Funciona com mods cooperativos e jogos que só oferecem partidas on-line. Os mods feitos aqui podem se integrar a ele: consulte a skill `couchlink`.

Jogos que estão ganhando modo cooperativo agora: **[Deus Ex](https://github.com/cranebeaker/deus-ex-coop)** (lançado) · **[Fallout: New Vegas](https://github.com/cranebeaker/fnv-coop)** · **[Zelda: Ocarina of Time](https://github.com/cranebeaker/ocarina-coop)** (totalmente sincronizado) · **[Dungeon Keeper](https://github.com/cranebeaker/dungeon-keeper-coop)** · **[S.T.A.L.K.E.R. Shadow of Chernobyl](https://github.com/cranebeaker/stalker-soc-coop-fixes)**

Da comunidade: **[Mega Man X](https://github.com/mstan/MegaManXSNESRecomp)** e **[Mega Man X4](https://github.com/mstan/MegaManX4Recomp)** (versões nativas para PC com jogo cooperativo em rede) · **[Pilotwings 64](https://github.com/NoahVl/Birdman64)** (tela dividida) · **[Crab Champions](https://github.com/Dudiebug/CrabMods/blob/main/crabsync/README.md)** · **[Stacklands](https://github.com/Dudiebug/stacklands-coop)** · **[Half Sword](https://github.com/Dudiebug/halfsword-multiplayer-mod)** · **[Enter the Gungeon](https://thunderstore.io/c/enter-the-gungeon/p/GoTeamAlex/Gungeon_Online/)** · **[Clive Barker's Jericho](https://github.com/dolbaras/jericho-coop)** · **[Poppy Playtime](https://github.com/romannazarov057-spec/PoppyCoop)** · **[Divinity II](games/divinity-2-developers-cut)** (tela dividida) · **[Command & Conquer 3](games/command-and-conquer-3)** (campanha cooperativa) · **[Far Cry 2](https://github.com/MortyRei/fc2-coop-probe)** · **[Gothic 3](https://github.com/GGM1k3y23/g3-together)** · **[Fear & Hunger](https://github.com/glynn568-glitch/fear-and-hunger-together)** · **[Modern Warfare 2](https://github.com/stxlvn/mw2_coop)** (campanha cooperativa) · **[Little Nightmares](https://discord.com/channels/1561411702082510879/1562210529504927836)** (no nosso Discord) · o seu será o próximo?

<a id="quick-start"></a>
## Primeiros passos

Diga ao seu agente (Claude Code, Codex, Gemini CLI, Cursor, OpenCode, ...):

```
Leia https://github.com/cranebeaker/coop-anything e siga AGENTS.md.
Quero jogar <game> em modo cooperativo com meus amigos.
```

O agente segue [AGENTS.md](AGENTS.md) e as skills em [`.agents/skills`](.agents/skills) (também disponíveis em `.claude/skills` para Claude Code).

<a id="add-the-mcp-server"></a>
### Adicione o servidor MCP

O **Co-op Anything MCP** permite que qualquer agente pesquise o diretório de projetos cooperativos, identifique o motor de um jogo pela pasta de instalação, leia os guias e as skills e valide contribuições. O Claude Code o reconhece pelo arquivo `.mcp.json` deste repositório; para outros agentes:

```
claude mcp add coop-anything -- python <clone>/tools/mcp/coop_mcp.py
```

Configuração para Codex, Gemini CLI e Cursor: [playbook/mcp.md](playbook/mcp.md). Para trabalhar com binários, combine-o com um MCP de engenharia reversa, como o [REA](https://github.com/morluto/rea) (`npx rea-agents setup`): o Co-op Anything sabe o que fazer; o REA examina o interior do jogo.

<a id="how-it-works"></a>
## Como funciona

Seu agente segue um de dois caminhos.

| | Caminho 1: concluir o que já existe | Caminho 2: criar do zero |
|---|---|---|
| Quando | Já existe um mod cooperativo, mas ele tem bugs, parou de evoluir ou foi abandonado. É o caso da maioria dos jogos mais queridos. | Não existe nada utilizável. |
| Como | Encontrar a última versão compilada, reunir relatos de bugs (issues, fóruns, Discord), auditar o código, corrigir em um pacote separado, testar e distribuir. | Fazer engenharia reversa do jogo e do motor, inserir hooks, exibir o segundo jogador, sincronizar inimigos, mundo e história, lidar com mudanças de fase e salvamentos, testar e distribuir. |
| Skills | `coop-research`, `coop-revive`, `coop-qa`, `couchlink` | `coop-reverse-engineer`, `coop-build-from-zero`, `coop-networking`, `coop-sync-testing`, `coop-qa`, `couchlink` |
| Guia | [Retomando mods abandonados](playbook/reviving-abandoned-mods.md) | [Como funcionam os mods cooperativos](playbook/how-coop-mods-work.md) |

Os dois caminhos terminam da mesma forma: testes automatizados com clientes reais do jogo ([QA](playbook/automated-qa.md)), instalação fácil, comunicação por retransmissão do Steam ([rede](playbook/networking.md)) e uma pull request de volta para este repositório.

<a id="sync-test-tools"></a>
### Ferramentas de teste de sincronização

Ferramentas prontas, independentes de jogo, para criar e testar a sincronização cooperativa em [`tools/`](tools/README.md). Cada uma tem testes, variantes de mutação e um comando que exibe `ALL OK` (`python -I tools/test_all.py` executa todos).

| Ferramenta | O que faz |
|---|---|
| [chaos](tools/chaos) | Retransmissor UDP com controle ao vivo que introduz latência, perda, reordenação, duplicação e interrupções em apenas um sentido entre clientes reais |
| [flight](tools/flight) | Gravador de eventos do mod com analisador: alinha 2 a 4 máquinas, encontra a primeira dessincronização, reduz o caso e escreve um teste de regressão |
| [fuzz](tools/fuzz) | Fuzzer cooperativo para N jogadores com semente reproduzível e oráculos de invariantes: convergência, nenhuma aplicação dupla, um único responsável, nenhuma duplicata ou estado obsoleto |
| [ownership](tools/ownership) | Pequena biblioteca C++: um responsável por NPC, com épocas, transferência de responsabilidade e rejeição de ecos obsoletos |
| [fakeworld](tools/fakeworld) | Mundo de jogo de exemplo em memória para testar a sincronização sem iniciar o jogo |
| [gameslot](tools/gameslot), [gamepool](tools/gamepool) | Trava e conjunto de instâncias já inicializadas para executar várias cópias do jogo com segurança em um PC |
| [scenarios](tools/scenarios), [bots](tools/bots) | Estados iniciais em JSON e roteiros cooperativos com vários bots, com comparação de estado a cada etapa |
| [animcheck](tools/animcheck) | Compara animações e poses entre máquinas e detecta deslizamentos, poses em T, flutuação e correções bruscas de posição |
| [bridge](tools/bridge), [inspect](tools/inspect) | Modelo de servidor RPC interno ao jogo (comando de console, captura de estado, salvar, carregar, captura de tela) com cliente Python e visualização ao vivo de todas as cópias lado a lado |
| [hotreload](tools/hotreload) | Separa o mod em carregador e núcleo e substitui o núcleo com os jogos em execução, sem reiniciá-los |
| [mutants](tools/mutants), [buildlock](tools/buildlock) | Variantes de mutação em tempo de execução para cada correção e uma trava de compilação compartilhada com cache |

[Iteração rápida](playbook/fast-iteration.md) mostra onde se gasta tempo em uma rodada de correção dentro do jogo e qual ferramenta elimina cada espera.

As ferramentas vêm do projeto [fnv-coop](https://github.com/cranebeaker/fnv-coop). A skill `coop-sync-testing` orienta o agente sobre quando usar cada uma.

<a id="what-you-can-co-op"></a>
## O que você pode jogar em modo cooperativo

| Seu jogo é... | Abordagem típica | Ferramentas usadas pelo agente |
|---|---|---|
| Feito em um motor que já tem multiplayer (Unreal 1/2, Source, id Tech, X-Ray) | Fazer a lógica de um jogador funcionar no código de rede existente com mods de scripts | Código-fonte dos scripts, compiladores do SDK, pacotes de mods |
| Bethesda (Gamebryo, Creation) | Plugin de extensão de scripts, sincronização com autoridade do host, reaproveitamento de arquiteturas como a do Tilted Online | SKSE / F4SE / xNVSE, Ghidra, REA |
| Unity | Patches com Harmony por um carregador de mods e biblioteca de rede em C# | BepInEx, MelonLoader, dnSpyEx, Il2CppDumper |
| Unreal Engine 4/5 | Mods Lua ou C++ com um dump de SDK das classes do jogo | UE4SS, Dumper-7 |
| RE Engine, FromSoftware ou outro motor proprietário | Hooks em DLLs; ampliar os recursos on-line do próprio jogo quando existirem | REFramework, MinHook, Ghidra, REA, x64dbg |
| Descompilado ou de código aberto (descompilações de N64, KeeperFX, OpenMW, ports de código-fonte) | Adicionar comunicação de rede diretamente no código | Compilador, projeto descompilado, compilação cruzada com Docker |
| Exclusivo de console (PS1, PS2, N64, Dreamcast, GameCube, Wii, GBA, ...) | Primeiro um port para PC por descompilação ou recompilação; caso contrário, jogo em rede por emulador ou mod de sincronização de memória entre dois emuladores | Descompilações e recompiladores (N64Recomp, XenonRecomp), PCSX2 PINE, Dolphin Memory Engine, Lua no BizHawk / mGBA |
| Binário fechado, sem outros recursos | Engenharia reversa completa do estado, salvamentos e fases; o caminho mais difícil | REA, GhidraMCP, ida-pro-mcp, Frida, Cheat Engine |

Jogos de console: [modo cooperativo em emuladores](playbook/console-emulators.md) e [ports para PC por descompilação ou recompilação](playbook/decomp-and-recomp.md), caminho seguido pelo modo cooperativo de Ocarina of Time.

Modo cooperativo no sofá em um único PC? [Tela dividida](playbook/split-screen.md) usa Nucleus Co-op (Windows) e PartyDeck (Linux e Steam Deck), ambos de código aberto.

Lista completa de ferramentas com instruções de instalação: [playbook/tools.md](playbook/tools.md). Para descobrir quais motores têm projetos cooperativos reutilizáveis: [playbook/engine-families.md](playbook/engine-families.md).

<a id="games-so-far"></a>
## Jogos até agora

| Jogo | O que foi feito | Versão distribuída | Relato técnico |
|---|---|---|---|
| Deus Ex (2000) | Retomada do mod cooperativo HX: pacote de correções, retransmissão pelo Steam e suíte de testes automatizados | [deus-ex-coop](https://github.com/cranebeaker/deus-ex-coop) | [games/deus-ex](games/deus-ex/README.md) |
| Dungeon Keeper (1997) | Modo cooperativo com guardião compartilhado no KeeperFX e retransmissão pelo Steam | [dungeon-keeper-coop](https://github.com/cranebeaker/dungeon-keeper-coop) | [games/dungeon-keeper](games/dungeon-keeper/README.md) |
| S.T.A.L.K.E.R. Shadow of Chernobyl | Patch de correções para Shadow of COOP (final verdadeiro desbloqueado) | [stalker-soc-coop-fixes](https://github.com/cranebeaker/stalker-soc-coop-fixes) | [games/stalker](games/stalker/README.md) |
| Fallout: New Vegas | História cooperativa: missões, resultados de diálogos, carma e reputação compartilhados | [fnv-coop](https://github.com/cranebeaker/fnv-coop) | [games/fallout-new-vegas](games/fallout-new-vegas/README.md) |
| Zelda: Ocarina of Time | Correções para um fork cooperativo totalmente sincronizado do Ship of Harkinian | [ocarina-coop](https://github.com/cranebeaker/ocarina-coop) | [games/ocarina-of-time](games/ocarina-of-time/README.md) |

Há também um [diretório com mais de 230 mods cooperativos e lacunas](DIRECTORY.md) para outros jogos (consulte e pesquise em [coopanything.app](https://coopanything.app)), com o que cada projeto realmente sincroniza e o quanto foi testado.

<a id="everyone-is-a-contributor"></a>
## Todos podem contribuir

Cada agente que trabalha em um jogo devolve o que aprendeu por meio de uma pull request: uma correção, lista de bugs, teste, tentativa que não deu certo ou entrada corrigida no diretório. O agente de uma pessoa avança até certo ponto; o próximo continua dali. Somando esse esforço computacional, até os maiores jogos podem chegar lá.

- Seu agente abre a PR como rascunho; você revisa as diferenças e a publica.
- Cada jogo recebe seu próprio repositório de distribuição, com link em [Jogos até agora](#games-so-far).
- O **nível de QA** de cada entrada informa como ela foi comprovada: sem testes, relatos de jogadores, testes automatizados (bots controlando clientes reais do jogo) ou campanha completa verificada.

[CONTRIBUTING.md](CONTRIBUTING.md) traz os detalhes. Converse com outros colaboradores no [Discord](https://discord.gg/EXGB49R82t).

<a id="faq"></a>
## Perguntas frequentes

<details><summary>Preciso saber programar?</summary>
Não. Você precisa do jogo, de um agente de programação e de um pouco de paciência. O agente pede autorização antes de instalar qualquer coisa ou usar suas contas.
</details>

<details><summary>Meu amigo precisa comprar algo?</summary>
Todos precisam ter o jogo instalado. A retransmissão pelo Steam usa o aplicativo de testes gratuito Spacewar, da Valve; ninguém precisa comprar mais nada.
</details>

<details><summary>Isso é legal?</summary>
Modificar jogos para jogar em modo cooperativo com amigos é algo que a comunidade de mods sempre fez. Este repositório não hospeda arquivos nem recursos de jogos (agentes podem trabalhar com código descompilado no repositório próprio de cada jogo) e não interfere em sistemas antitrapaça ou serviços on-line. Consulte as regras abaixo.
</details>

<details><summary>Vai funcionar com o meu jogo?</summary>
Sim. Alguns jogos exigem mais horas de trabalho do agente do que outros, mas é possível. Consulte primeiro o <a href="DIRECTORY.md">diretório</a>: se já existe um mod cooperativo (caminho 1), a maioria dos projetos leva no máximo alguns dias. Se não existe nada (caminho 2), depende do motor; a tabela acima dá uma ideia.
</details>

<a id="documentation"></a>
## Documentação

- [AGENTS.md](AGENTS.md): regras e mapa de etapas para agentes · [servidor MCP](playbook/mcp.md) · [skills](.agents/skills) · [ferramentas de teste de sincronização](tools/README.md)
- Guias: [triagem](playbook/triage.md) · [pesquisa](playbook/research.md) · [levantamento de bugs no Discord](playbook/discord-export.md) · [engenharia reversa](playbook/reverse-engineering.md) · [ferramentas](playbook/tools.md) · [como funcionam os mods cooperativos](playbook/how-coop-mods-work.md) · [famílias de motores](playbook/engine-families.md) · [retomada de mods](playbook/reviving-abandoned-mods.md) · [rede](playbook/networking.md) · [retransmissão Steam Spacewar](playbook/networking-steam-spacewar.md) · [tela dividida](playbook/split-screen.md) · [emuladores de console](playbook/console-emulators.md) · [Switch](playbook/switch.md) · [descompilação e recompilação](playbook/decomp-and-recomp.md) · [QA automatizado](playbook/automated-qa.md) · [distribuição aos jogadores](playbook/shipping-to-players.md) · [fluxos com vários agentes](playbook/multi-agent-workflows.md) · [caos de rede](playbook/network-chaos-testing.md) · [busca de dessincronizações](playbook/desync-hunting.md) · [fuzzing da sincronização](playbook/fuzzing-coop-sync.md) · [responsabilidade sobre atores](playbook/actor-ownership.md) · [testes com mundo simulado](playbook/fake-world-testing.md) · [várias cópias do jogo](playbook/multi-instance-testing.md) · [bots e roteiros](playbook/bots-and-playbooks.md) · [sincronização de animações](playbook/animation-sync-checks.md) · [iteração rápida](playbook/fast-iteration.md) · [ponte dentro do jogo](playbook/in-game-bridge.md) · [recarregamento do mod em execução](playbook/hot-reloading-your-mod.md) · [sincronização da história por efeitos](playbook/effect-capture-story-sync.md) · [métodos](playbook/methods.md) · [lições](playbook/lessons.md)
- [DIRECTORY.md](DIRECTORY.md) e seu [esquema](data/SCHEMA.md)

<a id="rules"></a>
## Regras

Não inclua arquivos ou recursos de jogos em commits neste repositório. É permitido trabalhar a partir de descompilações; o código de cada jogo fica em seu próprio repositório. Não inclua informações pessoais. Dê crédito aos mods em que se basear e devolva as correções aos projetos originais. Somente modo cooperativo: nada que permita trapacear nas partidas multiplayer de outras pessoas ou interfira em sistemas antitrapaça.

Licença: MIT.
