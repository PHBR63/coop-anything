---
name: couchlink
description: "Jogar um jogo cooperativo, um mod cooperativo ou qualquer jogo on-line em tela dividida em um PC com Couchlink (uma cópia por jogador, cada um com sua parte da tela, controle ou teclado e mouse e, opcionalmente, conta Steam própria) e integrar a ele um mod criado aqui por meio de uma receita ou do SDK do Couchlink."
---

<a id="couch-co-op-on-one-pc-with-couchlink"></a>
# Modo cooperativo no sofá em um PC com Couchlink

O [Couchlink](https://github.com/cranebeaker/couchlink) (MIT, Windows 10 e 11) executa uma cópia do jogo por jogador no mesmo PC, posiciona cada cópia em um monitor ou parte dele e fornece a cada cópia somente o controle (ou teclado e mouse) correspondente. As cópias se conectam pelo multiplayer do próprio jogo: LAN, servidor de um mod cooperativo ou Steam. Até 8 jogadores.

Use esta skill quando alguém quiser jogar com amigos no mesmo sofá em vez de pela internet, ou quando um mod cooperativo feito com estes guias também precisar funcionar em tela dividida.

<a id="playing"></a>
## Como jogar

1. Baixe o ZIP da versão do Couchlink em https://github.com/cranebeaker/couchlink e execute `couchlink.exe`.
2. **Library (biblioteca)**: jogos instalados que já têm uma receita aparecem em "On this PC". Outros jogos Steam instalados aparecem em "Try it", com configurações padrão seguras. Jogos compatíveis que você não possui ficam listados abaixo.
3. **Players (jogadores)**: pressione A em um controle ou Enter em um teclado para ocupar um lugar. Um teclado e um mouse juntos contam como um jogador.
4. **Steam**: uma conta é suficiente; todas as cópias rodam nela. Para jogos que conectam jogadores somente pelo Steam (salas on-line, convites), forneça uma conta própria a cada jogador adicional pelo cartão do lugar dele ("Steam"). O Windows pede permissão uma vez; depois o jogador faz login. Cada conta precisa ter sua própria cópia do jogo.
5. **Screens (telas)**: arraste os jogadores para os monitores ou divida uma tela.
6. Pressione Play. Se o jogo exigir uma configuração inicial (instalador de mod, primeira execução), a biblioteca avisa antes de Play.

<a id="adding-a-game-or-a-co-op-mod"></a>
## Adicionando um jogo ou mod cooperativo

Escolha a menor solução que atenda à necessidade. O guia completo, com exemplos, é a skill `couchlink-sdk` do repositório Couchlink: https://github.com/cranebeaker/couchlink/blob/main/skills/couchlink-sdk/SKILL.md

- **Uma receita** (um arquivo JSON): como iniciar o jogo, onde ficam os salvamentos, quais verificações de instância única remover, qual modo Steam usar e qual servidor iniciar primeiro, se necessário. As variáveis de modelo `$SEAT`, `$PLAYER`, `$WIDTH`, `$HEIGHT`, `$X`, `$Y` fornecem argumentos próprios a cada cópia. Valide com `cargo run -q -p couchlink-nucleus --example check_recipe -- my-game.json` e compartilhe no Discord; receitas publicadas são assinadas e chegam a todas as instalações.
- **Um mod cooperativo integrado ao Couchlink**: faça a receita passar o lugar e o nome do jogador pela linha de comando ou pelo ambiente; o lugar 0 hospeda e os demais se conectam a `127.0.0.1` na sua porta. Assim, não são necessários artifícios de entrada.
- **Componentes do Couchlink no seu inicializador**: os crates são MIT (`couchlink-hook` para controles, teclado e mouse por cópia; `couchlink-steam` para configuração Steam por cópia; `couchlink-core` para receitas e lugares). Outra opção é controlar o serviço Couchlink pela API WebSocket local (`docs/protocol.md` no repositório).

<a id="testing-without-people"></a>
## Testes sem pessoas

Siga a skill `coop-qa`: nada de sessões humanas de teste. Para Couchlink, isso significa uma receita aprovada por `check_recipe`, uma sessão iniciada por script contra o serviço local (`start_session`, depois aguarde `running` nos eventos `session`) e os bots do próprio mod verificando se todas as cópias entraram no host.
