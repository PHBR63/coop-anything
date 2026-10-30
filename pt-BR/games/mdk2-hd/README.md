# <a id="mdk2-hd-2011"></a>MDK2 HD (2011)

| | |
|---|---|
| Motor | Próprio da BioWare (MDK2), renderizador OpenGL 3.0, scripts Lua 3.1 com vinculações tolua |
| Versões testadas | Aplicativo Steam 213350, identificador da compilação 3902, `mdk2hd.exe` SHA-256 `bf5faa81b18837b4c07f35941b107e5c23caa8b105536ccd9c8e5a8e37357f43` |
| Projetos | [mdk2-coop](https://github.com/TommoDotCommo/mdk2-coop) (entrada "MDK2 HD" no diretório) |
| Nível de QA | automated |
| Última atualização | 2026-10-23 |

## <a id="where-things-stand"></a>Situação atual

MDK2 HD não tem multiplayer. mdk2-coop acrescenta cooperação com entrada durante a partida: dois ou mais jogadores avançam juntos pela campanha, com o mundo do host (inimigos, disparos, itens coletáveis, portas, checkpoints, carregamentos de fases, cenas) espelhado em cada cliente. O alfa público [v0.2.0-alpha](https://github.com/TommoDotCommo/mdk2-coop/releases/tag/v0.2.0-alpha) (2026-10-23, pré-lançamento com instalador e inicializador) passou primeiro pela sequência automatizada completa: 31 verificações, incluindo todos os 96 checkpoints com host e cliente. Ninguém terminou a campanha inteira em modo cooperativo ainda; os testes automatizados não resolvem quebra-cabeças nem derrotam chefes.

## <a id="existing-work"></a>Trabalhos existentes

Nenhum encontrado antes deste projeto (pesquisados DIRECTORY.md, issues e PRs deste repositório e a web em 2026-10-20).

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- Tudo fica em `mdk2.tar`, arquivo ustar plano (5842 entradas) com os 101 scripts em código-fonte Lua simples. Substituições por arquivos soltos não se aplicam a scripts, e `dofile()` só lê do contêiner.
- `%LOCALAPPDATA%\MDK2HD\settings.lua` é gravado pelo jogo e executado na inicialização após `mdk2.lua`; uma linha acrescentada pode carregar um mod. Mantenha-o pequeno: o jogo o lê em buffer de pilha de 8 KB e falha se for maior.
- Lua não tem biblioteca io, então a rede exige código nativo. O executável importa DINPUT8.dll; uma proxy dinput8.dll na pasta é a parte nativa. Usa hooks nas funções de quadro, dano, sala e porta e comunica por UDP.
- `debug.lua` acompanha o contêiner: `dofile('debug')` ativa o menu de depuração BioWare (F9), e sua lista de checkpoints também serve de plano de testes.
- O motor executa vários gobs de heróis ao mesmo tempo (o chefe final cria Kurt, Max e Doc com IA); o parceiro pode ser um segundo representante `OBJ_KURT` criado por Lua.
- Salas: a cada quadro, o gerenciador desativa todas e ativa a que contém a câmera e as visíveis dela; o restante fica suspenso. O modo cooperativo precisa ativar salas ao redor de todos os jogadores, com a mesma regra em todas as máquinas, ou OnCreate de uma sala executará só de um lado.
- `gob_delete` apenas marca o gob; ele permanece na tabela (e sua global Lua continua válida) até a limpeza da cena. Buscas por nome no mesmo quadro ainda o encontram.
- Criadores nomeiam cada criação `<spawner>_spawn`; alguns atores criados têm sub-gobs sem informações com o mesmo nome. Associar nomes entre máquinas exige alternativa numérica e deve ignorar essas partes.
- Salvamentos completos (`mdkStartInstantSave` / `mdkStartInstantLoad`) funcionam durante cooperação; caminhos são cortados em 16 caracteres e todas as cópias em um PC compartilham `%LOCALAPPDATA%\MDK2HD`.

Detalhes, endereços e evidências: [NOTES.md](NOTES.md).

## <a id="what-we-changed"></a>O que alteramos

Cada correção abaixo veio de verificação automatizada ou manual que falhou e foi testada novamente; NOTES.md contém as evidências.

- Representante do parceiro com sincronização de posição, orientação e animação; nunca colocado dentro do jogador local.
- Inimigos com autoridade do host (criação, remoção, capturas de estado); criadores no cliente desativados, exceto os de itens.
- Disparos reproduzidos em todas as máquinas; dano encaminhado pelo host; reanimação junto ao parceiro em vez de fim de jogo.
- Lançamentos de projéteis atrasados, incluindo granadas Doganboy, carregam trajetória e tempo de explosão finais; disparos que quicam usam a velocidade do corpo rígido. Animações copiadas de ataque não duplicam lançamentos.
- Coletas, portas por proximidade (abrem para o jogador mais próximo), checkpoints e carregamentos seguidos por todos os clientes.
- Correções de falha: atacante NULL em eventos de dano; manipulador de ciclo de animação de Max excluindo um gob que o representante nunca possuíra.
- Correções de dessincronização encontradas pela comparação de estado: posições obsoletas de representantes após carregar ativavam salas cedo; remoção e recriação com mesmo nome associavam ao gob morrendo; homônimos sem informações criavam cópias com 0 de vida; salas ativadas pela câmera de um lado e pelo corpo do outro.
- Até 16 jogadores (host retransmite), reconexão durante a fase, salvamentos cooperativos e retomada após falha de cliente ou host.
- Incapacitação: golpe fatal derruba o jogador; colega segurando R o levanta; se sangrar até morrer, observa até limpar a área ou alcançar checkpoint; todos derrubados recarregam o checkpoint.
- Dois transportes: UDP direto e salas Steam só para amigos, com convites e identificador de sala (mensagens Steam P2P, sem redirecionar portas).
- Na tela: painel de jogadores, etiquetas de nome, contornos humanos através de paredes (desativados por padrão), balões de conversa e marcações.
- Conversa por texto (T) e marcações (V ou botão central do mouse); voz por proximidade (pressionar para falar, alcance definido pelo host).
- Menus Options > Co-op no estilo do jogo: jogadores, sessão, jogabilidade, dificuldade (Story, Normal, Hard, Nightmare, Custom) e página Controls com predefinições Original, Modern e Custom.
- Inicializador antes do jogo (hospedar, entrar ou solo, transporte, nome, configurações, modo de tela), instalador que verifica o hash da compilação Steam e script de distribuição.
- Cooperação no sofá: 2 a 4 jogadores locais, cada um com janela e controle, executando várias cópias do jogo.
- Cenas: todos começam juntos, pular exige votação com contagem regressiva (Esc), e a parte seguinte espera todos chegarem ao fim. Em saltos de paraquedas e minijogos de torpedo, os demais aparecem como fantasmas. Um sinal antecipado do host (recebido antes de começar a cena local) iniciava reprodução sem relógio e causava erros Lua nos clientes em dois casos de campanha; agora usa o caminho normal de início.
- Roda de personagens (segurar J: Kurt, Max ou Doc a qualquer momento) e roda de emotes por herói (segurar H). Kurt e Max são mais largos que Doc; trocar perto de parede pode prendê-los. Teclas de movimento mantidas os posicionam em pontos próximos até mover. O limite de tempo começava na troca; quem esperava 4 s antes de andar continuava preso. Agora começa com a primeira tecla de movimento mantida.
- Navegador de salvamentos e seletor de fase/checkpoint no inicializador.
- Removido: ampliador de texturas por IA (deixava o jogo mais escuro e sem relevo que o original).

## <a id="qa"></a>QA

- Modo de teste em segundo plano: jogos sem foco, silenciados, controlados por entradas de script internas e capturas do buffer de renderização; o PC continua utilizável durante os testes.
- `tools/qa_all.py full` executa toda a sequência: testes fora do jogo (compilação, oráculos, núcleos de projéteis, controles, reanimação e rede), todas as suítes de recursos com jogos reais, variantes com perda de rede e campanha (todos os 96 checkpoints com host e cliente: caminhar, disparar, acerto no cliente, cliente acompanha, ambos vivos, inimigos associados, vida igual, sem erros Lua, comparação de estado). `--lanes 3` executa suítes lado a lado em cópias separadas; `--campaign-shards 4` divide a campanha entre quatro pares de host/cliente.
- Antes de v0.2.0-alpha (2026-10-23): 30 de 31 verificações passaram, campanha em 4 minutos. A falha era o herói preso acima, bug real que aparecia só com PC ocupado; após a correção, a verificação da roda de personagens passou em 12/12, e tanto o código antigo quanto um mutante sem destravamento falham nela.
- Suítes verificam variantes deliberadamente defeituosas (`MUTANT=...`) quando viável, detectando verificações incapazes de falhar.
- Não cobertos: campanha completa jogada em cooperação, chefes e quebra-cabeças além dos inícios de checkpoints, sessões longas pela internet, convites Steam entre duas contas separadas, controles físicos, microfones e 3 a 4 jogadores no sofá (testados com entrada simulada).

## <a id="how-to-play"></a>Como jogar

Baixe o ZIP nas [Releases](https://github.com/TommoDotCommo/mdk2-coop/releases) do mod, extraia e execute `Install.cmd`. Localiza a instalação Steam, recusa compilações diferentes de Steam 3902 e pergunta Steam ou UDP e hospedar ou entrar; `Uninstall.cmd` remove o mod. Hospede pelo Steam em Options > Co-op > Session (convide amigos ou compartilhe o identificador da sala); por UDP, o host redireciona a porta 27900. Um inicializador abre antes do jogo para hospedar, entrar, jogar solo e ajustar tudo; `Couch.cmd` inicia cooperação no sofá. Para compilar, consulte `docs/DEVELOPMENT.md` do mod (`bridge/` com mingw i686, `tools/install.sh`, `tools/release.sh`).

## <a id="known-issues"></a>Problemas conhecidos

- Convites Steam entre duas contas separadas e sessões longas pela internet ainda não testados.
- Sem migração de host: se ele sair, a sessão termina para todos.
- Host envia cerca de 1,3 Mbit/s com 8 jogadores numa fase movimentada, menos com menos jogadores.
- Algumas cenas acionadas por eventos da fase não têm contagem regressiva até serem vistas uma vez.
- Voz sem cancelamento de eco e sem voz no modo sofá (uma sala, um microfone).
- Itens gerados por criadores de itens executam independentemente em cada máquina e são associados por nome.

## <a id="next-steps"></a>Próximos passos

- Campanha cooperativa completa com jogadores reais, transformando problemas encontrados em verificações automatizadas.
- Testar convites Steam entre duas contas reais e sessão longa pela internet.
- Gravar rotas para o bot de reprodução (a estrutura existe; nenhuma rota de campanha incluída) para cobrir o que a inspeção de checkpoints não cobre: quebra-cabeças e chefes.
