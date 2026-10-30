# <a id="research-find-everything-that-already-exists"></a>Pesquisa: encontre tudo que já existe

O erro mais comum é anunciar cedo demais que ninguém criou modo cooperativo para determinado jogo. Dois dos nossos projetos começaram com essa afirmação, e ambos os jogos já tinham modo cooperativo funcional: um estava em uma branch `multiplayer` não padrão de um fork; o outro era uma compilação de 2019 no servidor de compilações do próprio autor. Diga "não encontrado pela busca X" e continue.

## <a id="where-to-look-in-order"></a>Onde procurar, em ordem

1. **Este repositório:** [DIRECTORY.md](../DIRECTORY.md), `games/`, issues e PRs abertas.
2. **Busca na web** com várias expressões: `<game> co-op mod`, `<game> multiplayer mod`, `<game> coop campaign`, `<game> online mod`, o nome do motor mais "coop" e o nome do jogo nos principais idiomas dos fãs (russo para STALKER, alemão e polonês para Gothic, japonês para muitos jogos de console).
3. **GitHub:** busca de código e repositórios; depois, para cada resultado, examine **forks, branches e versões distribuídas**, além da branch padrão. Pesquise tópicos (`coop`, `multiplayer`, `<game-name>`).
4. **ModDB e Nexus:** datas da última atualização, comentários sobre abandono, abas de arquivos e "articles" com diários de desenvolvimento. Ambos bloqueiam algumas buscas automatizadas; use o texto dos resultados de busca e registre isso nas notas.
5. **Archive.org:** sites de projetos encerrados, páginas de download, wikis e discussões de fóruns. Servidores de compilação antigos e índices FTP frequentemente sobrevivem ali ou até continuam on-line.
6. **Comunidades:** Discord e fóruns principais do jogo, guias e discussões da comunidade Steam, Reddit (r/<game>, discussões em r/patientgamers pedindo modo cooperativo).
7. **Outros trabalhos do autor:** o que mais ele lançou no mesmo motor explica bastante sobre o código e pode conter ferramentas compartilhadas.
8. **Mesmo motor, outros jogos:** uma estrutura cooperativa para um jogo semelhante pode representar a maior parte do trabalho. Consulte [engine-families.md](engine-families.md).

## <a id="what-to-record-for-each-find"></a>O que registrar para cada descoberta

- Link, identificador do autor e licença (ou "nenhuma informada").
- Última atividade confirmável (commit, versão, data de publicação), não o selo de atualização.
- O que **realmente** sincroniza. Separe a visibilidade entre jogadores de inimigos compartilhados, missões e história compartilhadas, estado do mundo e itens. As páginas dos autores, matérias e jogadores frequentemente discordam; priorize a página atual do próprio autor e os relatos dos jogadores em relação à imprensa.
- Onde estão os relatos de bugs (rastreador de issues, canal Discord, discussão de fórum).
- A versão compilada mais recente e como foi verificada (hash, número de versão dentro dos arquivos).

## <a id="mining-bug-reports"></a>Levantamento de relatos de bugs

- Comece por rastreadores de issues e discussões de fóruns.
- Discord: leia [discord-export.md](discord-export.md), incluindo a parte dos Termos de Serviço, antes de exportar qualquer coisa.
- Transforme cada mensagem de falha relatada em um teste: um teste de inicialização por fase e uma reprodução por script.

## <a id="reading-foreign-language-sources"></a>Leitura de fontes em outros idiomas

Leia as fontes diretamente e resuma em inglês, mas mantenha as strings técnicas originais (mensagens de erro, nomes de arquivos, comandos de console) sem tradução ao lado do texto traduzido, pois são elas que você pesquisará depois.

## <a id="output"></a>Resultado

Adicione ou corrija entradas em `data/directory.yaml` durante o trabalho, mesmo sem escrever uma linha de código. Uma boa PR de pesquisa é uma das contribuições mais úteis.
