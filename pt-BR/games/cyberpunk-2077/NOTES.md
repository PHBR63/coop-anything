# <a id="cp2077-research-notes-2026-10-23-re-verified-2026-10-25"></a>Notas de pesquisa de CP2077 (2026-10-23, reverificadas em 2026-10-25)

Relato apenas de pesquisa: nenhuma cópia do jogo foi comprada, instalada ou executada em qualquer momento (conforme as regras básicas de AGENTS.md). Tudo abaixo é pesquisa documental com fontes.

## <a id="how-data-was-gathered-and-verified"></a>Como os dados foram reunidos e verificados

* Metadados dos repositórios GitHub (pushed_at / stars / license / archived) pelo endpoint público `api.github.com/repos/<owner>/<repo>` em 2026-10-23; todas as datas reverificadas em 2026-10-25. As URLs de API de cada projeto estão em `sources` nas respectivas entradas.
* READMEs dos projetos por `api.github.com/.../readme` (buscas diretas em raw\.githubusercontent retornaram vazias nesta rede; o endpoint de API funcionou).
* Sites ativos dos projetos consultados diretamente: nightcoop.net (o original russo diz "???????? ???? ????" = beta aberta em andamento; aberto em 2026-10-23 15:00 UTC), open2077.net, cyber.mp (todos HTTP 200 em 2026-10-23).
* Cobertura da imprensa: Polygon / PCGamesN / GamingBible / player.one / kocpc; usada para manter NightCoop e CyberMP (dois projetos diferentes) claramente separados.

## <a id="ecosystem-summary-10-projects"></a>Resumo do ecossistema (10 projetos)

1. NightCoop - beta aberta desde 2026-10-23, prólogo + Ato 1, 8 jogadores, diálogos da história por votação majoritária, código fechado, gratuito. O mais próximo de modo cooperativo de história. Fontes: <https://nightcoop.net/> e matéria da Polygon (veja as fontes da entrada).
2. CyberpunkMP (Tilted) - último push em 2024-12-21 (API), da época do patch 2.2, parado. 64 estrelas. Fonte: <https://api.github.com/repos/tiltedphoques/CyberpunkMP>
3. NightCityMP - fork de continuação de CyberpunkMP, patch 2.31a do jogo, último push em 2026-07-20 (API). Voltado a sandbox; NPCs, missões e dano de combate não sincronizados. Fonte: <https://api.github.com/repos/blyatiful1/NightCityMP>
4. oxylol/cp2077-coop - camada de host da história; host envia horário, clima e missão acompanhada a cada 2 s; relógios dos convidados só avançam. Último push em 2026-10-10 (API). Fonte: <https://api.github.com/repos/oxylol/cp2077-coop>
5. KyleBuildsAI/cp2077-coop - v0.0.37/alpha.5 disponível para download (painel CET e retransmissor Python na porta 11778); agora integra a base de sessões tipadas de Bukczyk. Último push em 2026-10-20 (API). Fonte: <https://api.github.com/repos/KyleBuildsAI/cp2077-coop>
6. Bukczyk/CP2077-Coop - base de sessões tipadas (SessionServer / CoopPlugin / runtime/session); diagnóstico com dois clientes em um PC chegou à validação de JOINER-fires-at-HOST com perda de vida e morte; recuperação de morte após reconexão ainda falha. Último push em 2026-10-20 (API). Fonte: <https://api.github.com/repos/Bukczyk/CP2077-Coop>
7. CyberMP - entrada baseada apenas na imprensa: noticiado em 2026-06, sem download público, site ainda ativo. Mantido separado de CyberpunkMP (projetos diferentes). Fontes: matérias PCGamesN e dsogaming (veja as fontes da entrada).
8. OPEN//77 - plataforma de servidor dedicado (RP/exploração livre/scripts Lua), ainda ativa: repositório open77-app da organização recebeu push em 2026-10-25 (API). Não é modo cooperativo de história. Fonte: <https://api.github.com/repos/Open2077/open77-app>
9. RedSync - AGPL-3.0, RED4ext + redscript + servidor .NET 9 sobre GameNetworkingSockets; retransmissão de fatos de missões com autoridade do host (PL q301-q307). Os links de download do README ainda apontam para um domínio de exemplo (your-domain.com); portanto, ainda não existe versão pública. Último push em 2026-08-25 (API). Fonte: <https://api.github.com/repos/nobody71004/RedSync>
10. Chaoskjell/Coop-Cyberpunk-Mod - MIT, estrutura inicial v0 (CET Lua e ponte de arquivos Python), atividade concentrada em um dia de 2026-08, sem sincronização da jogabilidade. Último push em 2026-08-09 (API). Fonte: <https://api.github.com/repos/Chaoskjell/Coop-Cyberpunk-Mod>

## <a id="technical-consensus-fed-into-the-write-ups-how-the-game-works"></a>Consenso técnico (incorporado à seção sobre funcionamento do jogo no relato)

* Conjunto de ferramentas da comunidade: RED4ext (C++/RTTI) + redscript (@wrapMethod) + CET (Lua/UI), mais ArchiveXL/TweakXL + Codeware.
* A sensibilidade à versão é o maior custo de manutenção: renomeações de RTTI em 2.31 impediam o jogo de iniciar (corrigidas pelas PRs #56-#60 do projeto original; o fork de oxylol as inclui).
* Jogadores remotos aparecem como NPCs representantes (Codeware/AMM); NightCoop é a exceção: cada convidado traz seu próprio V.
* Autoridade do mundo: NightCoop/oxylol = o salvamento do host É o mundo; NightCityMP planeja um salvamento multiplayer dedicado.
* Toda a rede é implementada pelos próprios projetos: UDP / GameNetworkingSockets / retransmissor Python; NAT por central de retransmissão ou Tailscale.
* Nenhum projeto público resolve a simulação compartilhada de NPCs/inimigos; a sincronização pública de missões mais aprofundada é a retransmissão de fatos de missões de RedSync.

## <a id="directoryyaml-change-log"></a>Registro de alterações de directory.yaml

* 4 entradas existentes: datas checked atualizadas; last_activity de CyberpunkMP de unknown -> 2024-12 com nota de desatualização; last_activity de oxylol/KyleBuildsAI de unknown -> 2026-10; notas ampliadas; URLs de API acrescentadas às fontes.
* 6 novas entradas: NightCoop / NightCityMP / RedSync / OPEN//77 / Bukczyk / Chaoskjell, inseridas após a entrada KyleBuildsAI para manter o jogo em sequência.
* Executado `python tools/build_directory.py` para regenerar DIRECTORY.md (exigência de CONTRIBUTING).

## <a id="follow-ups-for-the-next-agent"></a>Acompanhamentos para o próximo agente

* Mudar qa de NightCoop: none -> community-reports quando surgirem relatos dos participantes da beta.
* Quem possuir o jogo pode testar KyleBuildsAI v0.0.37 em uso real e relatar os resultados.
* Ainda não pesquisados: páginas aprofundadas do Nexus, fóruns de comunidades russas/chinesas, arquivos do Discord.
