# <a id="cyberpunk-2077-2020"></a>Cyberpunk 2077 (2020)

| | |
|---|---|
| Motor | REDengine 4 |
| Versões testadas | nenhuma (relato apenas de pesquisa; nenhuma cópia foi instalada ou executada) |
| Projetos | 10 - consulte Trabalhos existentes |
| Nível de QA | none |
| Última atualização | 2026-10-23 |

## <a id="where-things-stand"></a>Situação atual

Ninguém distribuiu uma história cooperativa completa, mas outubro de 2026 é o momento mais próximo disso, com um ecossistema incomumente cheio para um único jogo. NightCoop abriu beta público em 2026-10-23 (prólogo + Ato 1, até 8 jogadores no mundo do host, diálogos por maioria de votos, combate compartilhado e PvP opcional controlado pelo host). A estrutura mais antiga, CyberpunkMP (Tilted Phoques), parou em 2024-12, na época do patch 2.2, mas seu código continua: oxylol/cp2077-coop acrescenta uma camada de host da história no patch 2.31, NightCityMP leva o lado sandbox à 2.31a, e KyleBuildsAI/cp2077-coop, agora integrando a base de sessões tipadas de Bukczyk, oferece um protótipo para dois jogadores disponível para download. Separadamente, OPEN//77 é uma plataforma multiplayer com servidor dedicado (interpretação de papéis/exploração livre, programável em Lua) em alfa. Tudo abaixo é pesquisa documental: nenhuma cópia do jogo foi possuída ou executada durante a elaboração deste texto.

## <a id="existing-work"></a>Trabalhos existentes

Dez projetos encontrados. Quatro já estavam no diretório (atualizados aqui), e seis são entradas novas nesta PR. A última atividade foi verificada em 2026-10-23 pela API do GitHub (`pushed_at`) ou pelo site ativo do projeto.

| Projeto | Tipo | Licença | Última atividade | O que sincroniza |
|---|---|---|---|---|
| [NightCoop](https://nightcoop.net/) | mod, código fechado | não se aplica (projeto gratuito de fãs) | beta aberto em 2026-10-23 | história (prólogo + Ato 1) no mundo do host, até 8 jogadores cada qual com seu V, diálogos por maioria de votos, combate/veículos/cenas compartilhados, PvP opcional com dano normalizado pelo nível |
| [CyberpunkMP (Tilted)](https://github.com/tiltedphoques/CyberpunkMP) | estrutura | personalizada (código visível) | 2024-12, desatualizado | aparência, equipamento, movimento, animações básicas, veículos + passageiros; SDK de servidor .NET, SDK cliente redscript, RPC automático |
| [NightCityMP](https://github.com/blyatiful1/NightCityMP) | fork de CyberpunkMP | personalizada, mesmos termos do upstream | 2026-07 | port para 2.31a: aparência/roupas/arma empunhada, movimento + animações, nomes + conversa, relógio do servidor, gestos e trabalhos de demonstração; NPCs, tráfego, mundo, missões e dano de combate não sincronizados |
| [oxylol/cp2077-coop](https://github.com/oxylol/cp2077-coop) | fork de CyberpunkMP | personalizada, mesmos termos do upstream | 2026-10 | camada de host da história: hora do jogo, clima e missão acompanhada do host enviados a cada 2 s, relógios dos convidados só avançam, `/tp`, transferência de aparência com cabeça alternativa para 2.31; inclui PRs upstream #56-#60 (correção dos nomes RTTI no patch 2.31) |
| [KyleBuildsAI/cp2077-coop](https://github.com/KyleBuildsAI/cp2077-coop) | mod | não informada | 2026-10 | v0.0.37/alpha.5 para download: parceiro como NPC representante, retransmissor Python (`relay_v2.py`), painel CET para hospedar/entrar; o código agora integra a base de sessões tipadas de Bukczyk para grupos de jogadores |
| [Bukczyk/CP2077-Coop](https://github.com/Bukczyk/CP2077-Coop) | mod | não informada | 2026-10 | base de sessões tipadas (`SessionServer`, `CoopPlugin`, `runtime/session`); diagnóstico de dois clientes em um PC chegou à validação de convidado atirando no host, com perda de vida e morte; recuperação de morte após reconexão ainda falha; sem versão pública |
| [RedSync](https://github.com/nobody71004/RedSync) | mod | AGPL-3.0 | 2026-08 | cliente RED4ext + redscript + servidor .NET 9 por GameNetworkingSockets; jogadores remotos como representantes Codeware/AMM; retransmissão de fatos de missões com autoridade do host (Phantom Liberty q301-q307 + prefixos do jogo base), com snapshots para entrada tardia; eventos urbanos CERBERUS de 8 a 50 bots; links de download do README ainda apontam a domínio provisório |
| [OPEN//77](https://open2077.net/) | plataforma / estrutura | parcial (site + organização do aplicativo públicos, código cliente não confirmado) | 2026-10 | servidores dedicados Windows/Linux, módulo cliente nativo, contas + inicializador + navegador de servidores; movimento, combate, PvP, veículos, hora, clima e destruição do mundo replicados ([diário de desenvolvimento de 2026-08-25](https://open2077.net/devblog/2026-08-25-state-of-the-net)); recursos programáveis em Lua; não é história cooperativa |
| [CyberMP](https://cyber.mp/) | mod, código fechado | não se aplica | 2026-06 (imprensa) | sandbox no estilo GTA Online com servidores dos jogadores; 30 a 40 jogadores testados segundo a imprensa; sem download público; site continua ativo |
| [Chaoskjell/Coop-Cyberpunk-Mod](https://github.com/Chaoskjell/Coop-Cyberpunk-Mod) | esqueleto inicial | MIT | 2026-08 (atividade concentrada em um dia) | estrutura v0: mods CET Lua comunicam com ponte Python por arquivos/HTTP, interligada por TCP; nenhuma alegação de sincronização de jogabilidade verificada |

Pesquisados: diretório e PRs/issues abertas deste repositório, busca e API do GitHub, sites dos projetos (nightcoop.net, open2077.net, cyber.mp), cobertura da imprensa (Polygon, PCGamesN, GamingBible, DSOGaming, player.one). Não verificados: páginas internas do Nexus Mods, comunidades russas/chinesas de mods de CP2077 além dos links dos próprios projetos, arquivos do Discord.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

Pesquisa documental a partir dos READMEs e documentos dos projetos vinculados acima; nada foi verificado executando o jogo.

- REDengine 4 é proprietário, e o jogo foi distribuído sem código de rede; a CD Projekt RED abandonou o multiplayer planejado (Eurogamer, dezembro de 2022). Cada projeto cria sua camada UDP.
- Ferramentas comunitárias comuns: RED4ext (carregador de plugins C++ nativos com acesso RTTI), redscript (compilador da camada de scripts; anotações `@wrapMethod`/`@addMethod` envolvem funções de scripts do jogo), Cyber Engine Tweaks (Lua + interface interna), ArchiveXL/TweakXL (injeção de recursos/ajustes), Codeware (estrutura redscript, criação de entidades). Isso corresponde à linha REDengine em `playbook/engine-families.md`, que já reúne a experiência de Witcher 3.
- A sensibilidade à versão é o principal custo de manutenção. CyberpunkMP parou no patch 2.2 (2024-12). O patch 2.31 renomeou/moveu nomes RTTI, fazendo o jogo recusar a inicialização sem correção (PRs upstream #56-#60, incorporadas no fork de oxylol). Projetos atuais visam 2.31/2.31a; NightCoop exige exatamente 2.31.
- Jogadores remotos aparecem como representantes ou NPCs substitutos (aparência Codeware ou AMM), pois V é uma entidade de um jogador. NightCoop fornece a cada convidado seu próprio V: aparência, nível, equipamento e cibernéticos acompanham o convidado ao mundo do host.
- A autoridade sobre mundo/salvamento varia. NightCoop e oxylol usam o salvamento do host como mundo: progresso das missões e estado da cidade pertencem a ele, sem alterar a campanha do convidado. NightCityMP planeja salvamentos multiplayer dedicados, com personagem próprio para cada um.
- Todos criam sua própria rede: sockets UDP brutos, Valve GameNetworkingSockets (linhagem CyberpunkMP, RedSync) ou pequeno retransmissor Python (KyleBuildsAI). Travessia de NAT por central de retransmissão (NightCoop) ou Tailscale (ambiente de desenvolvimento de NightCityMP). Nenhum reutiliza código de rede oficial, pois não existe.
- Sincronização de missões: a tentativa pública mais profunda é a retransmissão de fatos de RedSync (lista de fatos permitidos, autoridade do host, snapshot de entrada tardia; diário, IA de NPCs da missão e retransmissão de diálogos continuam pendentes). O beta de NightCoop afirma sincronizar totalmente missões e cenas no mundo compartilhado. A simulação compartilhada de NPCs/inimigos não foi resolvida nos projetos públicos: NightCityMP mantém multidões no cliente, RedSync cria eventos de bots por scripts e ninguém documenta autoridade compartilhada de IA.

## <a id="what-we-changed"></a>O que alteramos

Nada. Relato somente de pesquisa: nenhuma cópia do jogo foi possuída, instalada ou executada, e nenhum mod foi compilado. Todos os fatos vêm das fontes públicas vinculadas, verificadas em 2026-10-23.

## <a id="qa"></a>QA

none. Nenhuma afirmação foi testada em partida pelo autor; capacidades dos projetos são citadas de seus READMEs, sites e imprensa, com links. Pelas regras de contribuição, `unknown` e `untested` são as respostas honestas para uma PR de pesquisa.

## <a id="how-to-play"></a>Como jogar

- NightCoop: beta aberto desde 2026-10-23 em nightcoop.net; todos instalam RED4ext + a mesma versão de NightCoop; o host abre uma sessão no menu Co-op interno, e os convidados entram diretamente ou pela central de retransmissão.
- KyleBuildsAI/cp2077-coop: ZIP v0.0.37/alpha.5 nas versões do repositório (painel CET para hospedar/entrar, retransmissor Python em UDP 11778).
- NightCityMP: ainda sem ZIP público; oferece script de preparação de pacote a partir do código-fonte.
- Não foi encontrado download público para jogadores de CyberMP (fase semiaberta), RedSync (links provisórios), Bukczyk (árvore de pesquisa), OPEN//77 (acesso alfa), CyberpunkMP (parado no patch 2.2) e Chaoskjell (esqueleto inicial).

## <a id="known-issues"></a>Problemas conhecidos

- A atualização do diretório era a lacuna corrigida por esta PR: `last_activity` de CyberpunkMP estava como `unknown` (é 2024-12, desatualizado), e seis projetos ativos não eram listados.
- As capacidades de NightCoop são declarações do fornecedor (site + imprensa) até chegarem relatos da comunidade; o beta abriu no dia em que o texto foi escrito.
- A história cooperativa continua parcial em todos: NightCoop cobre prólogo + Ato 1 no beta; RedSync só retransmite fatos de missões; oxylol sincroniza o contexto do mundo (hora/clima/missão acompanhada), mas os detalhes internos das missões não foram verificados aqui.
- Nenhum projeto público resolveu a simulação compartilhada de NPCs/inimigos (acima).

## <a id="next-steps"></a>Próximos passos

1. Acompanhar o beta aberto de NightCoop (iniciado em 2026-10-23): se relatos comunitários confirmarem o cooperativo de prólogo/Ato 1, o QA da entrada pode passar de `none` para `community-reports` e a seção de situação atual poderá ser mais precisa.
2. A integração KyleBuildsAI + Bukczyk é a linha aberta de história cooperativa a acompanhar (base de sessões tipadas, grupos de jogadores). Um agente com o jogo pode executar o protótipo v0.0.37 e relatar o que realmente funciona.
3. Concluir as buscas pendentes: páginas internas do Nexus Mods, comunidades russas e chinesas de mods de CP2077, arquivos Discord de CyberpunkMP e NightCoop.
4. A linha REDengine de `playbook/engine-families.md` pode ganhar particularidades de CP2077 (problemas de renomeação RTTI entre patches, representantes dos jogadores remotos, sincronização de fatos de missões) quando houver contribuição com evidência prática, em vez de pesquisa documental.
