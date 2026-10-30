# <a id="middle-earth-shadow-of-war-2017"></a>Middle-earth: Shadow of War (2017)

| | |
|---|---|
| Motor | Firebird, motor da Monolith derivado de LithTech (nome interno "Kraken") |
| Versões testadas | Aplicativo Steam 356190, compilação 3095001 (última atualização 2018-09-05), `x64\ShadowOfWar.exe` 1.0.8874.0, SHA-256 `ed0d95cabb033cd66aaa99d699374881846c3cb03ec345f1123d82d45e0bdaef` |
| Projetos | nenhum jogável; [JustAddMP/ShadowOfWar](https://github.com/JustAddMP/ShadowOfWar) é uma reserva de projeto; pesquisa aqui (reivindicação: cranebeaker/coop-anything#93) |
| Nível de QA | none (ainda sem modo cooperativo) |
| Última atualização | 2026-10-21 |

## <a id="where-things-stand"></a>Situação atual

Não existe modo cooperativo para Shadow of War. Esta pasta reúne pesquisa e engenharia reversa para um modo criado do zero com autoridade do host: execução e instrumentação seguras de uma cópia de teste, mapa dos comandos de console do motor, saída de log ao vivo do sistema Nemesis e funções de eventos, morte, promoção e RNG de Nemesis, com assinaturas de bytes para a compilação Steam acima. Notas brutas com fontes: [NOTES.md](NOTES.md).

## <a id="existing-work"></a>Trabalhos existentes

- [JustAddMP/ShadowOfWar](https://github.com/JustAddMP/ShadowOfWar): somente README, "planejado" (criado em 2026-10-17), parte de um grupo com estrutura compartilhada, [JustAddMP/core](https://github.com/JustAddMP/core).
- Nenhum outro mod cooperativo ou multiplayer encontrado (web, GitHub, Nexus por resultados de busca, fóruns Steam; 2026-10-20). Os recursos on-line (Vendettas, Online Conquest) são assíncronos.
- Ferramentas de modificação compatíveis com esta compilação (todas usam hooks no jogo em execução): [ReaperAnon/Middle-Earth-Mod-Loader](https://github.com/ReaperAnon/Middle-Earth-Mod-Loader) (proxy `bink2w64.dll`) e seus [mods](https://github.com/ReaperAnon/Shadow-Of-War-Mods); [editor de salvamentos](https://github.com/SystematicSkid/shadow-of-war-save-editor), [freecam](https://github.com/SystematicSkid/sow-freecam) e [reconstrução do servidor de serviço](https://github.com/SystematicSkid/shadow-of-war-server) de SystematicSkid; [carregador de recursos](https://github.com/survivalizeed/ShadowOfWarPacketLoader) de survivalizeed. Todos os padrões de bytes correspondem exatamente uma vez nesta compilação; os endereços fixos de *funções* do editor de salvamentos não correspondem (os de dados, sim).

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Código no disco.** SteamStub presente e Denuvo provável (disposição habitual das seções, sem string identificadora; sessão b de NOTES.md), mas a seção de código `.arch` (31 MB), a tabela de funções `.pdata` e `.sdata` são idênticas byte a byte no disco e na memória durante a execução; o executável pode ser lido estaticamente. Base da imagem 0x140000000.
- **Estrutura do motor.** A divisão cliente/servidor do LithTech sobrevive nos caminhos de código (`Game\ClientShellDLL`, `Game\ObjectDLL`, `Game\Shared`), com porta de hospedagem "game NetMesh" e máquina de estados de rede para votação de host. Ainda não se sabe se há divisão real cliente/servidor em tempo de execução.
- **Registro do console.** Lista encadeada de 680 entradas nomeadas (RVA `2A58BE0`): 449 programas de console (ponteiro do manipulador em `+0x38` da entrada) e variáveis, com descrição, arquivo-fonte e linha. Programas relevantes: `Faction.Save` / `Faction.Load` / `Faction.Dump` (mundo Nemesis completo), `FactionMember.Save` / `.Load`, `Faction.SimEvent.*`, `Faction.AdvanceTime`, `QuestMgr.Save` / `.Load`, `Teleport`, `SlowMO.*`, `Replay.*`.
- **Log de depuração.** `debug_print(category, fmt, ...)` incorporado na compilação (RVA `19C83AC`) é um stub de 12 bytes nesta versão; 1.100 pontos de chamada, a maioria condicionada a indicadores de canal de um byte (tabela perto de `2A34D9E`-`2A34DBF`). Com hook e canais Nemesis ativados, registra o sistema ao vivo.
- **Sistema Nemesis.** Internamente "Faction". Toda lógica executa em uma thread do jogo. Cada evento passa por `HandleFactionEventAction(Event, Subject, Other)` (RVA `40C304`), que também aplica promoções; mortes passam por verificação de ressurreição e sorteio aleatório (`RollResurrection`, `6DBD4C`, usando `RandomFloat`). Regiões são facções (`Faction_MtnPass`, `Faction_desert`, ...); capitães ocupam posições (linha, coluna).
- **Aleatoriedade.** Um LCG global de 64 bits (`state = state * 0x0BB38435 + 0x3619636B`, retorna os 32 bits superiores), estado no RVA `2A25C88`, acessado por `RandomFloat` e uma cópia expandida em linha.
- **Salvamentos.** `%LOCALAPPDATA%\WB Games\Shadow of War\<prefix>_ShadowOfWar.sav` e vagas numeradas, alternadas uma vez por sessão. Cada salvamento também passa por `ISteamRemoteStorage::FileWrite`, que `steam.exe` grava em `Steam\userdata\<id>\356190\remote`, mesmo com Steam Cloud desativado para o jogo. Salvamento automático frequente (16 em cerca de 5 minutos).
- **On-line.** Com conexões de saída falhando como em PC desconectado, o jogo chega ao menu e funciona normalmente; tenta novamente dois hosts HTTPS periodicamente. Recusar a criação de sockets faz aparecer uma janela de erro de servidor.

Tabela de funções e assinaturas: NOTES.md, sessões r e s.

| RVA | função | assinatura única (verificada no jogo em execução) |
|---|---|---|
| `40C304` | HandleFactionEventAction | `48 89 5C 24 08 48 89 6C 24 18 48 89 74 24 20 57 41 54 41 55 41 56 41 57 48 83 EC 70 4C 8B FA` |
| `62E670` | seu chamador (também acrescenta reproduções de eventos) | `48 89 5C 24 18 48 89 6C 24 20 56 57 41 54 41 56 41 57 48 81 EC 80 00 00 00` |
| `6DB95C` | ao morrer um capitão: avaliar ressurreição | `48 8B C4 48 89 58 08 48 89 70 10 48 89 78 18 4C 89 60 20 55 41 56 41 57 48 8D 68 A1 48 81 EC A0 00 00 00 4C 8B F2` |
| `6DBD4C` | RollResurrection | `48 89 5C 24 10 48 89 74 24 20 55 57 41 54 41 56 41 57 48 8B EC 48 83 EC 60 48 8B 99 28 02 00 00` |
| `622A84` | SimEvent::Simulate | `48 89 5C 24 08 57 48 83 EC 20 80 3D ? ? ? ? 00 48 8B D9 74 2B` |
| `741284` | AddFactionEventReplay | `48 8B C4 48 89 58 08 48 89 70 10 48 89 78 20 4C 89 40 18 55 41 56 41 57 48 8D 68 B9` |
| `1B3C6C` | RandomFloat | `48 83 EC 28 0F 28 C8 E8 ? ? ? ?` |
| `1807908` | Rng (alvo da chamada de RandomFloat) | resolver a partir de RandomFloat (a etapa LCG também aparece expandida em linha em `FC0E93`) |
| `18DDCC` | LookupFactionMember | `8B 52 08 E9 ? ? ? ? 48 8B 49 20` |
| `18BDB0` | RecordName | `48 85 C9 74 18 F6 41 01 02 74 12 48 8B 41 20` |

## <a id="what-we-changed"></a>O que alteramos

Ainda sem alterações cooperativas. Ferramentas para trabalhar com segurança (ainda não publicadas):

- **sowguard**, proxy `bink2w64.dll` para instalação de teste copiada: recusa execução fora da pasta de teste ou em outra compilação; usa hooks nas chamadas de arquivos ntdll do processo para redirecionar pastas de salvamento a um ambiente isolado e parar o jogo em qualquer escrita na instalação ou salvamentos reais; faz conexões de saída falharem como em PC desconectado; bloqueia escritas `ISteamRemoteStorage` no processo (caso contrário, o cliente Steam gravaria salvamentos da cópia de teste na pasta real do Steam).
- **sowprobe**, sonda por pipe nomeado dentro do jogo: lê memória, busca padrões, segue ponteiros, lê o registro do console; com modo de escrita ativado, captura a saída de depuração.

## <a id="qa"></a>QA

- As ferramentas têm suíte fora do jogo (sem processo do jogo) e compilação de controle negativo com proteções removidas; ambas ficam em repositório não publicado, portanto nenhum resultado é declarado aqui.
- Ao vivo: sete inicializações protegidas na compilação Steam. A conferência posterior contra backup com hashes dos salvamentos reais e pasta Steam detectou duas escritas externas ao processo: NVIDIA App regravando `render.cfg` real e `steam.exe` gravando o salvamento da cópia de teste na pasta real da nuvem Steam (restaurados do backup). A segunda levou ao bloqueio de armazenamento remoto; com ele, uma sessão com 16 salvamentos automáticos deixou salvamentos reais e pasta Steam inalterados. Uma inicialização falhou por causa do primeiro hook de depuração (consulte a lição dos guias sobre hooks em stubs folha); corrigido e testado.
- QA cooperativo: nenhum (nada para testar ainda).

## <a id="how-to-play"></a>Como jogar

Nada para jogar ainda.

## <a id="known-issues"></a>Problemas conhecidos

Nenhum (sem versão distribuída).

## <a id="next-steps"></a>Próximos passos

- Decidir o modelo de sincronização: fluxo de eventos do host a partir de `HandleFactionEventAction` e funções de morte/promoção, ou estado do mundo do host por `Faction.Save` / `Faction.Load`.
- Verificar se a divisão cliente/servidor LithTech é real durante a execução (`GameServerShell`, `clientmgr`, código NetMesh).
- Mapear o personagem do jogador a partir de `GameClient` (RVA `26FFA98`).
