# <a id="vanquish-2010"></a>Vanquish (2010)

| | |
|---|---|
| Motor | Platinum Engine (próprio, C++; física Havok) |
| Versões testadas | nenhuma (somente pesquisa) |
| Projetos | nenhum encontrado |
| Nível de QA | none |
| Última atualização | 2026-10-22 |

## <a id="where-things-stand"></a>Situação atual

Hoje ninguém consegue jogar Vanquish em modo cooperativo, e nenhum projeto está tentando implementá-lo. O jogo não tem multiplayer de nenhum tipo e não existe nada utilizável para retomar. É uma lacuna para criar do zero, e difícil: um port de console fechado, com motor próprio, sem código de rede, camada de scripts ou estrutura cooperativa para jogos do mesmo motor.

## <a id="existing-work"></a>Trabalhos existentes

As buscas (diretório do repositório, pesquisa de repositórios e código no GitHub, busca na web incluindo menções a Nexus e ModDB, fóruns Steam) não encontraram nenhum projeto cooperativo ou multiplayer, ativo ou abandonado. O que existe no Nexus Mods para o port de PC se limita a uma tabela/trainer do Cheat Engine (limitadores do traje ARS, alternância AR, ajustes de combate corpo a corpo) e pacotes de texturas/skins. Tópicos dos fóruns Steam pedem modo cooperativo, mas não apresentam nenhum projeto.

Desconhecidos: archive.org, comunidades de mods em japonês (a cena de mods de Bayonetta / Vanquish para PC) e projetos privados no Discord. As fontes estão na entrada do diretório.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

Fatos e desconhecidos, pois nada foi executado em uma instalação local:

- **Motor:** Platinum Engine, motor C++ próprio da PlatinumGames, da mesma família de Bayonetta e NieR: Automata (que usa uma variante profundamente reformulada). Física Havok. Sem código-fonte público ou descompilação conhecida.
- **Scripts:** `unknown`. O port de PC armazena dados em arquivos contêiner semelhantes a pacotes; existem ferramentas para arquivos de Bayonetta PC (por exemplo, plugins Noesis), e há relatos de que parte delas serve para Vanquish, mas nada foi verificado aqui.
- **Código de rede:** nenhum. A PlatinumGames confirmou no lançamento que o jogo não possui modos multiplayer e que nenhum foi desenvolvido; o port de PC é uma conversão direta da versão de console.
- **Câmera lenta:** a mecânica central (modo Augmented Reaction, deslizar com propulsão) altera localmente a escala de tempo, tornando o projeto de mundo compartilhado muito mais difícil que em um jogo de tiro em terceira pessoa comum: todos os clientes desaceleram quando um jogador ativa o modo AR, ou o AR fica apenas local e dessincroniza o combate.

## <a id="what-we-changed"></a>O que alteramos

Somente pesquisa: entrada do diretório e este relato técnico.

## <a id="qa"></a>QA

Não se aplica (somente pesquisa). `python -I tools/test_all.py` foi executado; houve uma falha preexistente sem relação com este trabalho (`check_msvc_environment[vcvars_ignored]`, o ambiente isolado não tem MSVC).

## <a id="how-to-play"></a>Como jogar

Não é possível hoje.

## <a id="known-issues"></a>Problemas conhecidos

Não se aplica.

## <a id="next-steps"></a>Próximos passos

Para quem assumir o trabalho, nesta ordem:

1. Registre a identidade do jogo: identificador de compilação Steam do executável atual e seu SHA-256, além dos formatos de arquivos em disco.
2. Levante ferramentas da cena de mods dos jogos relacionados (Bayonetta PC, NieR: Automata): extratores de arquivos, plugins Noesis e símbolos das tabelas Cheat Engine do trainer existente. São os primeiros pontos de entrada no binário.
3. Faça análise estática de `Vanquish.exe` no Ghidra: localize a organização do estado do jogo, o ator do jogador e os caminhos de entrada e câmera. Os endereços conhecidos da tabela CE existente são o ponto de partida.
4. Escolha o modelo de rede conforme os guias. Autoridade do host com sincronização de estado é a única opção realista, e a câmera lenta do modo AR exige uma decisão de projeto antes de escrever código.
5. É um projeto longo. Expectativa realista: meses de engenharia reversa antes de dois modelos de Sam aparecerem na mesma sala.
