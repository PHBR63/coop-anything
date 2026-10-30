# <a id="metal-gear-solid-v-the-phantom-pain-2015"></a>Metal Gear Solid V: The Phantom Pain (2015)

| | |
|---|---|
| Motor | Fox Engine (Konami, fechado/proprietário; scripts Lua 5.1) |
| Versões testadas | nenhuma por nós (somente pesquisa); os mods visam a versão Steam, AppID 287700 |
| Projetos | [Dynamite](https://github.com/unknown321/dynamite) (2 jogadores), [Joint Operations](https://github.com/Hound-Protocol/Joint-Operations) (16 planejados), [mod de alex-ppg](https://github.com/alex-ppg/mgs-v-multiplayer-mod) (projeto provisório vazio) |
| Nível de QA | none (nenhum teste feito por nós) |
| Última atualização | 2026-10-28 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores já podem jogar The Phantom Pain juntos com **Dynamite**, um mod cooperativo inicial, mas funcional (PC Gamer o chamou de "a functioning Metal Gear Solid 5 co-op mod", com vídeos de missões completas). O projeto declara estar em desenvolvimento inicial e ter bugs, exige uma cópia Steam sem modificações (não japonesa) e requer voltar um patch antes de instalar. **Não existe opção jogável para 3 ou mais jogadores:** Joint Operations pretende chegar a 16, mas "nothing is playable yet", e o repositório de alex-ppg é apenas uma linha provisória. Nesta etapa fizemos somente pesquisa; nada aqui foi instalado, analisado por engenharia reversa ou testado por nós.

## <a id="existing-work"></a>Trabalhos existentes

- **[Dynamite](https://github.com/unknown321/dynamite)**, de unknown321, cooperativo para 2 jogadores, em desenvolvimento inicial. 476 estrelas, 55 issues abertas; versão mais recente v0.6.0 (2025-10-31), master avançou até 2026-09-29 (criado em 2025-07-20). Windows 10+ e Linux/SteamOS (Proton com substituição de `dinput8.dll`). Exige cópia Steam sem modificações (versão JP não suportada), conexão Steam, cerca de 1 GB livre e um amigo; recomenda-se salvamento 100% para acessar todas as missões funcionais. É **obrigatório retornar a uma versão anterior ao patch Steam de 2026-06-09**, que quebra a inicialização (issue [#136](https://github.com/unknown321/dynamite/issues/136)). Licença: **GPL-3.0 com Commons Clause**. Binário Go único; inclui servidor principal próprio ([fuse](https://github.com/unknown321/fuse)) e ferramenta de proteção dos salvamentos ([squib](https://github.com/unknown321/squib)). Documentação: `docs/MAKING_OF.md` (diário detalhado de desenvolvimento) e `webui/docs/docs.md`. É a versão que jogadores e imprensa relatam realmente jogar. Consulte NOTES.md para a arquitetura completa e a análise dos bugs.
- **[Joint Operations](https://github.com/Hound-Protocol/Joint-Operations)**, de Hound Protocol, pretende oferecer até 16 jogadores (1 host + 15 clientes) em mundo aberto, Windows + Linux/Proton, usando os recursos on-line do próprio jogo e o SDK Steamworks. Em 2026-10-25 havia somente organização, documentação, site e pesquisa documental; o README afirma **"Nothing is playable yet"** e planeja a primeira versão, 0.1, para 2 jogadores. GPL-3.0-only (documentação CC BY-SA 4.0); política de propriedade intelectual por desenvolvimento independente (não copiará código do Dynamite).
- **[alex-ppg/mgs-v-multiplayer-mod](https://github.com/alex-ppg/mgs-v-multiplayer-mod)**, repositório provisório criado em 2026-10-25, README de uma linha, modo cooperativo como primeiro objetivo, ainda sem código. CC0-1.0.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Motor:** Fox Engine é fechado e proprietário; não há descompilação ou port de código-fonte. O trabalho cooperativo depende de hooks nativos e scripts, não de alterar um motor aberto.
- **Scripts:** a maior parte da lógica usa **Lua 5.1**, incorporada ao executável, carregada de `data1.dat`/arquivos de patch `.dat` e do interior de arquivos `fpk`. Esse é o ponto de atuação da comunidade de mods.
- **Ferramentas de modificação que tornam o modo cooperativo viável:** [Infinite Heaven](https://www.nexusmods.com/metalgearsolidvtpp/mods/1226) (grande estrutura Lua de missões), [V_Framework](https://mgsvmoddingwiki.github.io/V_Framework/) (camada Lua que expõe interface, som, soldados, chefes e veículos não expostos pelo jogo; exige IH e jogo 1.0.15.3 ou 1.0.15.4) e [IHHook](https://mgsvmoddingwiki.github.io/IHHook) (DLL proxy `dinput8.dll` que acrescenta uma API C de Lua ao Lua do jogo compilado estaticamente). [MockFox](https://github.com/TinManTex/MockFox) pode executar o Lua do jogo e scripts IH fora do jogo para análise offline.
- **Código de rede (como Dynamite realmente funciona, segundo seu `MAKING_OF.md`):** o jogo distribuído não tem código de rede para *campanha* cooperativa, mas uma sessão Fox Engine é nativamente multiplayer (até 16 jogadores); as missões de um jogador apenas executam uma sessão com 1 jogador, e as missões **FOB** usam a mesma sessão com permissão para entrada de um segundo. Dynamite assume o caminho de conexão de início de missão FOB: uma sessão **Steam P2P** conecta host e cliente **por SteamID** (é necessária conexão à rede Steam para estabelecê-la); depois o identificador/geometria da missão é substituído por uma missão de um jogador e uma segunda instância de jogador é alocada por edição de `.fox2`. Há **autoridade do host**, sendo o jogador 0 o host; IA e seleção de alvos dos inimigos são conduzidas pelo host (o alvo é alterado para o jogador mais próximo, pois os inimigos FOB normalmente ignoram quem entra, o "defensor"). Marcadores são sincronizados por um canal interno de mensagens de rede (originalmente um artifício com pacotes de dano). Patches nativos usam um proxy `dinput8.dll` baseado em **IHHook** e alteração direta de bytes do executável em Go; o mod **não** se baseia no Infinite Heaven.
- **Servidor principal:** os registros cooperativos iriam, de outra forma, para o servidor principal da Konami, com risco de banimento on-line; por isso, Dynamite inclui **fuse** (reimplementação Go/SQLite), executado localmente na porta 6667.
- **Proteção de salvamentos:** Dynamite copia o salvamento e executa o modo cooperativo na cópia (ferramenta: **squib**); os dados de um jogador permanecem intactos e os fundos/recursos on-line são simulados, não transferidos.

## <a id="what-we-changed"></a>O que alteramos

Nada. Esta etapa contém apenas pesquisa e entrada de diretório/relato técnico.

## <a id="qa"></a>QA

Não executamos testes. Nível de QA: `none`. Os relatos de partidas com Dynamite vêm de vídeos do autor e cobertura da imprensa, não de testes estruturados.

## <a id="how-to-play"></a>Como jogar

Para 2 jogadores hoje: instale **Dynamite** conforme sua documentação (https://github.com/unknown321/dynamite), com cópia Steam sem modificações (não JP), voltando primeiro um patch (issue #136); depois siga a documentação de usuário distribuída. Os jogadores executam as etapas em suas próprias máquinas; coop-anything não distribui o jogo nem o mod.

## <a id="known-issues"></a>Problemas conhecidos

O que um jogador realmente perceberá no Dynamite (classificado a partir das 55 issues abertas e de `MAKING_OF.md`):

- **Escopo:** somente 2 jogadores (3 ou mais impedem o início); missões de uma lista selecionada, **sem exploração livre**; várias missões não são jogáveis ou são propensas a falhas.
- **Jogadores:** o avatar do parceiro frequentemente só é renderizado em modo FOB, não nas missões normais (pode parecer invisível); faltam animações ao carregar corpos ou se esconder em banheiros.
- **Inimigos:** posições e campos de visão não são sincronizados entre os PCs (sinais vitais são); cada lado executa sua própria IA, então um soldado pode estar em locais diferentes para cada jogador.
- **Objetivos/marcadores:** objetivos secundários e marcadores de objetivo não são compartilhados; alguns objetivos só atualizam para o host.
- **Veículos:** tanques/carros têm bugs de criação e sincronização de posição (a escolha de um tanque pelo host pode causar falha); Walker Gear é invisível para o outro jogador.
- **Companheiros:** Quiet/D-Dog são locais (o parceiro não os vê); D-Horse causa dessincronização por teletransporte.
- **Fluxo:** morte -> reaparecimento após cerca de 10 s (sem falha da missão); reiniciar pelo menu de pausa trava em carregamento infinito; extrair outro jogador por Fulton faz a missão falhar.
- **Configuração:** exige retornar a uma versão anterior do jogo (o Steam desfaz isso ao atualizar); versão JP não suportada; o modo cooperativo não conecta durante a manutenção semanal do Steam.

## <a id="next-steps"></a>Próximos passos

Rede, versão compatível e itens sincronizados estão mapeados (acima e em NOTES.md). Restam:

- **Correções de maior valor na prioridade do próprio autor:** suporte a `>2 player` (a sessão não inicia) e **sincronização de posição/campo de visão dos inimigos** (#112, #113), que mais alteram a sensação de modo cooperativo real. O canal de marcadores já mostra um caminho funcional de sincronização personalizada para reutilizar.
- Compilar o código-fonte (`docs/BUILD.md`, Go) e preparar **instalações de teste isoladas + QA com bots** (`playbook/automated-qa.md`, `tools/`), verificando correções sem sessão humana de teste.
- Comparar scripts originais e Dynamite pelo método do autor (extrair o jogo, formatar com StyLua, `meld`) para localizar exatamente cada patch antes de alterá-lo.
- Confirmar o número exato da compilação anterior a 2026-06-09 para retornar (a issue #136 só informa a data).
- Acompanhar a versão 0.1 (2 jogadores) de Joint Operations e atualizar o diretório quando for distribuída.
