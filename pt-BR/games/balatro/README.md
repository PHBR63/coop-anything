# <a id="balatro-2024"></a>Balatro (2024)

| | |
|---|---|
| Motor | LÖVE 11 (executável integrado: `love.exe` + ZIP dos códigos Lua), LuaJIT, luasteam |
| Versões testadas | Steam, appid 2379780, build 17459173, versão 1.0.1o-FULL, SHA-256 de `Balatro.exe`: `0d75fe164accf3312734d4b37ac98788dd15f0b8e4f9bb8b7f90c4e59de93f47`, Windows 10 x64 |
| Projetos | [Balatro Duo](https://github.com/dobrodeetel/balatro-duo) (modo cooperativo local em um PC, versão 0.6.1), entrada "Balatro Duo"; [BalatroCoop](https://thunderstore.io/c/balatro/p/GUANZHUTAFEI/BalatroCoop/) (LAN, mesma partida), entrada "BalatroCoop" |
| Nível de QA | automated (clientes bots, 9 cenários incluindo falhas e reinicializações), além de sessões de jogadores até a ante 8 |
| Última atualização | 2026-10-30 |

## <a id="where-things-stand"></a>Situação atual

Duas pessoas podem jogar Balatro juntas em um PC com Balatro Duo: duas janelas, cada jogador com sua própria partida, pontuação de blind compartilhada e host escolhendo os blinds. A retomada após falha ou reinicialização de qualquer janela funciona. Testadores jogaram várias sessões até a ante 8 com mouse e DualSense; o uso do controle na janela sem foco não está coberto pelos testes.

## <a id="existing-work"></a>Trabalhos existentes

- [BalatroCoop](https://thunderstore.io/c/balatro/p/GUANZHUTAFEI/BalatroCoop/) 0.2.2 alpha (2026-10-13): dois jogadores na mesma partida, pontuação combinada de blind, loja compartilhada, baralhos separados, LAN por TCP 22122 (ou túnel). Exige Steamodded e Lovely. Não informa repositório-fonte nem licença.
- [BalatroMultiplayer](https://github.com/Balatro-Multiplayer/BalatroMultiplayer) (GPL-3): PvP (attrition, showdown, survival), não cooperativo. Exige Steamodded e Lovely.
- Balatro Duo (este relato) tem outro projeto: cada jogador mantém sua partida e somente o blind é compartilhado.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- `Balatro.exe` é um executável integrado do LÖVE; os códigos Lua podem ser abertos com qualquer leitor ZIP. [Lovely](https://github.com/ethangreen-dev/lovely-injector) (`version.dll`) aplica patches por padrões ao carregar e pode acrescentar arquivos inteiros a `main.lua`.
- Pontuação: `G.FUNCS.evaluate_play` calcula `hand_chips*mult` de uma vez e agenda uma atualização gradual não bloqueante de `G.GAME.chips` após a animação de cada carta (`state_events.lua` ~1044). Verificação de vitória: `G.GAME.chips - G.GAME.blind.chips >= 0` em `update_hand_played` e `end_round`.
- Tela de blinds: `Game:update_blind_select` monta `G.blind_select` a partir de `G.GAME.round_resets.blind_states`; `create_UIBox_blind_select` recalcula `blind_on_deck` pelos estados. Os botões de selecionar e pular são `one_press` (um clique os desativa).
- O chefe da próxima ante é sorteado ao receber o pagamento (`reset_blinds`); portanto, já é conhecido na loja.
- Etiquetas: etiquetas de pacote são ativadas em `new_blind_choice`, em um ciclo que para na primeira etiqueta acionada e recomeça quando o pacote fecha (`end_consumeable`). Dois pacotes simultâneos causam falha no fechamento.
- Salvamentos: `save_run` serializa `G.GAME` (preserva tabelas simples) em quase toda mudança de estado; Continue chama `Game:start_run({savetext = ...})`, a mesma função de uma nova partida.
- Mãos secretas ficam visíveis quando jogadas; seus planetas são "softlock" e só entram no conjunto disponível depois de a mão ser jogada (`common_events.lua` ~2009).
- Sem código de rede. O jogo usa SDL2 para controles; LÖVE segue `APPDATA` para a pasta de salvamento, mas Lovely não (passe `--mod-dir`).

## <a id="what-we-changed"></a>O que alteramos

Tudo em [Balatro Duo](https://github.com/dobrodeetel/balatro-duo): `lovely.toml` (6 patches por padrões) e `duo.lua` acrescentado a `main.lua`. Detalhes, causas raiz e todos os bugs encontrados pelos testes: [NOTES.md](NOTES.md).

- Duas janelas, TCP em 127.0.0.1:22123, uma linha de texto por mensagem. A segunda tem identidade própria de salvamento (`BalatroDuoP2`). Os controles são divididos entre as janelas (eventos SDL em segundo plano), e a janela sem foco ignora o mouse.
- Pontuação compartilhada de blind: os pontos próprios só são enviados ao parceiro depois de entrarem no total local. Uma rodada vencida aguarda uma mão do parceiro ainda em contagem. Sem mãos restantes: aguarda o parceiro sem bloquear a entrada.
- O host decide os blinds. O convidado acompanha os pulos pelo estado e o chefe do host desde a loja. Seleções/pulos do convidado aparecem na tela do host como desejos.
- Opções: níveis de mãos compartilhados (planetas ou todas as melhorias), ambas as etiquetas de pulo para ambos, mãos secretas compartilhadas (seus planetas entram no conjunto do parceiro).
- Retomada após falha: o estado cooperativo fica em `G.GAME.duo` (identificador da partida, divisão da pontuação atual, mãos secretas do parceiro). Cada lado envia sua posição completa na partida (`sy`). Prevalece o mais avançado: o atrasado alcança o parceiro na tela de blinds ou entra no blind já em andamento. Uma janela de convidado encerrada é reaberta pelo host.
- Texto nos 15 idiomas do jogo (`duo_lang.lua`), usando a terminologia do próprio jogo.

## <a id="qa"></a>QA

- `tools/run_all.ps1` no repositório do mod: 9 cenários, cada um com dois clientes bots jogando partidas reais até o fim da ante 2, com logs comparados por `tools/check_logs.ps1`. Verifica seleções, pulos, metas, totais iguais em todas as rodadas, pontuação enviada somente após a contagem, etiquetas, níveis e desejos.
- Cenários: atraso na loja + planetas; atraso do host na loja + mãos secretas; pilha de etiquetas (Double + Charm nos dois); desejos do convidado + convidado lento; baralhos próprios; host encerrado aos 110 s; convidado aos 45 s; ambos aos 130 s; convidado encerrado e reaberto pelo host.
- Última execução completa em 2026-10-27 (0.6.0): 9/9 aprovados (46, 46, 41, 44, 39, 20, 25, 17, 25 verificações).
- 0.6.1 (2026-10-29): cenários 1-2 (46/46 cada); execução de desejos (47/47); capturas dos idiomas (`tools/lang_test.ps1`, 15/15).

## <a id="how-to-play"></a>Como jogar

Baixe o ZIP em [releases](https://github.com/dobrodeetel/balatro-duo/releases), execute `Install.cmd`, inicie Balatro pelo Steam e vá em main menu -> CO-OP -> Play together (2 windows). Host: mouse e teclado; convidado: controle #1.

## <a id="known-issues"></a>Problemas conhecidos

- Pressionamentos do controle na janela sem foco não estão cobertos pelos testes.
- Vales de novo sorteio de chefe e Boss Tag no convidado não estão cobertos pelos testes.
- Retomada e recuperação de progresso só foram testadas por bots nas antes 1-2.
- Um lado que retoma um salvamento mais antigo joga aquela rodada sozinho (o parceiro já a terminou).
- Iniciar uma segunda janela pelo Steam enquanto uma já roda a abre com o perfil do host.

## <a id="next-steps"></a>Próximos passos

- Cenários de bots para vales de novo sorteio de chefe, Boss Tag e antes mais altas.
- Jogo on-line (o protocolo é TCP simples; o endereço fica em `duo_config.txt`, ainda sem interface).
