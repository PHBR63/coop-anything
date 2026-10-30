# <a id="celeste-2018"></a>Celeste (2018)

| | |
|---|---|
| Motor | XNA/FNA (linhagem MonoGame, C#) |
| Versões testadas | Steam PC, compilação atual, com Everest `stable-1.6623.0` |
| Projetos | CelesteNet, Co-op Helper, Partnership, Intertwined (consulte o diretório) |
| Nível de QA | community-reports |
| Última atualização | 2026-10-16 |

## <a id="where-things-stand"></a>Situação atual

Celeste não tem multiplayer integrado. Existe um conjunto funcional de mods, igual para todos: instale **Everest** (carregador), depois **CelesteNet** (coloca outros jogadores na fase, com conversa e emotes) e opcionalmente **Co-op Helper** (entidades sincronizadas entre jogadores). Para um objetivo realmente compartilhado, dois jogadores instalam um mapa cooperativo baseado nesses dois. A campanha cooperativa pretendida é **Partnership**, minicampanha projetada para exatamente dois jogadores.

Isso *não* oferece sincronização da história original, inimigos ou estado do mundo pelo CelesteNet. Duas pessoas podem estar na mesma fase e se ver, mas progresso, mortes e itens são individuais. A experiência de jogar uma campanha juntos vem de um mapa cooperativo, não do jogo base. Não há modo cooperativo de entrada imediata para a história original.

## <a id="existing-work"></a>Trabalhos existentes

| Projeto | O que é | Autor | Licença | Última atividade |
|---|---|---|---|---|
| [CelesteNet](https://gamebanana.com/mods/53695) | Mod multiplayer on-line (Everest). Jogadores, conversa, emotes, sessões por mapa. Cliente v2.4.2. [Código-fonte](https://github.com/0x0ade/CelesteNet) (MIT), [site](https://celestenet.0x0a.de/). | 0x0ade | MIT | cliente 2024-12, repositório 2026-06 |
| [Co-op Helper](https://gamebanana.com/mods/453706) | Biblioteca auxiliar para CelesteNet: entidades/gatilhos com estado sincronizado entre jogadores e modo beta "Co-op Everywhere". v1.1.4. [Código-fonte](https://github.com/corkr900/CoopHelper). | corkr900 | CC BY-NC-ND 4.0 | 2026-09 |
| [Partnership](https://gamebanana.com/mods/150725) | Minicampanha cooperativa para dois jogadores baseada em CelesteNet + Co-op Helper. v1.0.1. O mais próximo de uma campanha cooperativa jogável. | MunTheory | CC BY-NC-ND 4.0 | 2022-01 |
| [Intertwined](https://gamebanana.com/mods/713075) | Mapa Summit cooperativo para dois, com mortes vinculadas, de Expert a Grandmaster. v1.1.3. Inclui 14 dependências auxiliares. | Clantis | CC BY-NC-ND 4.0 | 2026-10 |

Antigo, substituído: **GhostNet** (mod multiplayer anterior ao CelesteNet) está obsoleto; CelesteNet o substituiu.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Motor:** FNA/XNA, C#. Código em `Celeste.dll`; recursos em `Content/`.
- **Carregador:** **Everest** aplica patches na instalação e carrega mods de `Mods/`. Mods declaram dependências em `everest.yaml`. Everest resolve a ordem pelo grafo de dependências; nomes de pasta não importam.
- **Modelo multiplayer:** CelesteNet é **cliente/servidor**, não ponto a ponto. Cada jogador conecta a um servidor CelesteNet (público ou próprio). Jogadores aparecem no mesmo mapa como fantasmas/avatares; um "canal" agrupa jogadores. Celeste não tem código de rede nativo, então o servidor não tem autoridade sobre o jogo original.
- **Entidades cooperativas:** Co-op Helper acrescenta entidades que, se usadas na construção do mapa, sincronizam estado pelo CelesteNet (portas, interruptores, criações). Isso torna o objetivo compartilhado, em vez de apenas o espaço.
- **Salvamentos:** progresso original por perfil em `Saves/`. Mapas cooperativos mantêm progresso próprio; os salvamentos originais dos dois jogadores são independentes.
- **Leitura do código:** mods são C# com API Everest e a maioria tem código aberto; o jogo é fechado e só existem binários distribuídos.

## <a id="what-we-changed"></a>O que alteramos

Esta é uma PR de documentação. Nenhum código de jogo ou mod foi alterado.

- **Corrigida a entrada Celeste no diretório.** Apontava para cópia de arquivos de terceiros (`vgtimes.com`) como URL do projeto, listava `open_source: unknown` para mod MIT público e tinha `last_activity: 2024-07` / v2.3.1 desatualizados. Agora aponta para o código do CelesteNet e a página GameBanana ativa, com fatos atuais.
- **Acrescentadas entradas** para Co-op Helper, Partnership e Intertwined, os projetos de que uma sessão de dois jogadores realmente precisa.
- **Corrigida afirmação em nossas notas.** Uma nota anterior dizia que o link do README de CelesteNet para `gamebanana.com/gamefiles/12267` estava quebrado e apontava para mod de Team Fortress 2. Não está: redireciona à página correta de CelesteNet (`mods/53695`). O mod TF2 vinha do espaço separado de identificadores `Mod` do GameBanana (`apiv11/Mod/12267`). Consulte a lição em "Problemas conhecidos".

## <a id="qa"></a>QA

**Nível de QA: community-reports.** Não há estrutura automatizada para Celeste neste repositório e nenhuma foi criada aqui. O que foi efetivamente verificado nesta rodada:

- **Dependências satisfeitas (estático).** Os cinco mods preparados (CelesteNet.Client 2.4.2, CoopHelper 1.1.4, Partnership 1.0.1, MaxHelpingHand 1.40.10, LunaticHelper 1.1.1) declaram Everest e dependências entre si compatíveis com Everest `1.6623.0` instalado e as versões acima; todas as dependências obrigatórias resolvem. Trata-se de leitura dos arquivos `everest.yaml`, não teste de execução.
- **Integridade dos downloads.** Cada artefato foi conferido por hash (SHA-256 e MD5 quando publicado pela fonte). MD5 `f14f38265dc4c23699ac38090f8c691b` do LunaticHelper corresponde à página GameBanana; os demais foram conferidos contra os bytes obtidos.
- **Inicialização e carregamento de mods (verificados).** A instalação isolada iniciou e o log do Everest (`log.txt`) mostra os cinco mods carregando e registrando, terminando em `DONE LOADING`, sem erros fatais: CelesteNet.Client 2.4.2, CoopHelper 1.1.4, LunaticHelper 1.1.1, MaxHelpingHand 1.40.10, Partnership 1.0.1. Apenas avisos de configurações da primeira execução, três dependências *opcionais* de MaxHelpingHand ausentes (BounceHelper, FrostTempleHelper, FlaglinesAndSuch) e conflito de substituição de sprite.
- **Armadilhas encontradas:** Everest grava `log.txt` na pasta do jogo, não `everest-log.txt`. Uma cópia da instalação precisa de `steam_appid.txt` contendo `504230` junto a `Celeste.exe`; caso contrário, Windows/Steam intercepta a inicialização e inicia a instalação Steam em vez da cópia.

Não executados: dois clientes reais conectados a um servidor, qualquer asserção sobre estado compartilhado. Criar testes de Celeste controlando dois clientes exigiria esforço grande: o jogo não executa sem interface, e CelesteNet precisa de servidor e clientes autenticados.

## <a id="how-to-play"></a>Como jogar

Guia passo a passo para o usuário: [SETUP.md](SETUP.md). Versão curta:

1. Instale Everest (pelo Olympus ou MiniInstaller manual).
2. Instale CelesteNet, Co-op Helper, MaxHelpingHand, LunaticHelper e Partnership.
3. Inicie, defina um nome CelesteNet e conecte ao servidor.
4. Crie um canal privado e convide seu parceiro.
5. Inicie Partnership na seleção de capítulos.

## <a id="known-issues"></a>Problemas conhecidos

- **Sem cooperação na história original.** CelesteNet exibe jogadores no mesmo mapa; não sincroniza história, inimigos ou mundo. Só mapas cooperativos feitos com Co-op Helper compartilham objetivos.
- **Partnership é curto e inacabado.** É minicampanha ("ainda não muitos capítulos"), segundo o próprio autor, com última versão em 2022.
- **É fácil errar as dependências.** Partnership precisa de MaxHelpingHand e LunaticHelper. A **página GameBanana de MaxHelpingHand chama-se "Maddie's Helping Hand"** (renomeada, mantendo o nome em everest.yaml); buscar "MaxHelpingHand" no GameBanana não a encontra facilmente. Intertwined precisa de 14 auxiliares.
- **Links antigos `gamefiles/<id>` e espaços de identificadores GameBanana.** Os identificadores `Mod` e `GameFile` ficam em espaços separados. `gamebanana.com/gamefiles/12267` redireciona corretamente ao CelesteNet, mas `apiv11/Mod/12267` na API é um mod de Team Fortress 2 sem relação. Verifique a qual espaço um número pertence antes de declarar um link quebrado.

## <a id="next-steps"></a>Próximos passos

- **Teste de conexão com dois clientes:** o carregamento com um passou; o próximo passo comprovável é conectar dois ao mesmo servidor, verificar se se veem e se um interruptor Co-op Helper sincroniza.
- **QA automatizado:** Celeste não funciona sem interface. O caminho plausível é dois clientes em janela e servidor CelesteNet próprio, usando entidades sincronizadas de Co-op Helper como oráculo (colocar interruptor num mapa de teste e verificar que ambos veem a mudança). É um projeto à parte.
- **Entrada de menu cooperativo:** CelesteNet só acrescenta **Mod Options** (configurações do Everest) e sobreposição dentro do jogo; não há item "Co-op" no menu principal. Um pequeno mod Everest poderia acrescentá-lo (menu de texto com conexão / canal / início rápido de Partnership). Não criado aqui.
- **Intertwined:** sua árvore de 14 dependências não foi instalada. Verifique antes de recomendá-lo em lugar de Partnership.
