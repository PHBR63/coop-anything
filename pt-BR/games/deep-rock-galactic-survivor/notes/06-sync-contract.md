# <a id="sync-contract--what-must-be-shared-for-smooth-co-op"></a>Contrato de sincronização - o que deve ser compartilhado para um modo cooperativo fluido

Rascunho de 2026-10-21, a confirmar. Este é o **Soll** (estado desejado) da sincronização; o Ist (estado atual) está em [../STATUS.md](../STATUS.md), e as diferenças medidas em [05-sync-gaps.md](05-sync-gaps.md). Nada aqui afirma que já funciona.

Regra prática: **o host decide, o cliente exibe.** Cada item tem uma autoridade (quem pode alterá-lo), um padrão de qualidade (o que o jogador não deve perceber) e uma forma de comprovação por teste.

## <a id="a-must-be-identical-on-both-sides-determinism"></a>A. Deve ser idêntico nos dois lados (determinismo)

| # | Item | Autoridade | Padrão | Comprovação |
|---|---|---|---|---|
| A1 | Configuração da partida: missão, setor, nó, bioma, perigo, **semente** | host | o cliente nunca gera o mapa antes da chegada da configuração | impressão digital da caverna igual; teste com início do host atrasado (variante de corrida da semente) |
| A2 | Organização do mapa, veios, minérios, objetos da missão (Bobby, detonadores, zona TNT, combustível) | semente | mesmas posições | levantamento `worlddiff`, 0 diferenças fora da lista de exclusões |
| A3 | Classe, mod de classe e aparência de **cada** anão vistos pelo outro lado | cada jogador, informando o outro | o host vê a classe/aparência real do cliente e vice-versa | contagem de renderizadores do representante + identificador da aparência nos dois logs |
| A4 | Desbloqueios do host (armas, melhorias, artefatos) utilizáveis por ambos | host | o cliente joga com eles, **ativado por padrão** | teste de leitura ao vivo com um desbloqueio não padrão |

## <a id="b-host-authoritative-world-state-client-only-mirrors"></a>B. Estado do mundo com autoridade do host (o cliente apenas espelha)

| # | Item | Padrão | Comprovação |
|---|---|---|---|
| B1 | Inimigos: criação, posição, vida, morte | movimento visualmente contínuo (meta = 10 Hz ou extrapolação; hoje 2 Hz), sem inimigos fantasmas ou ausentes | levantamentos iguais; erro de posição sob um perfil de latência |
| B2 | Projéteis, granadas, torres e feixes dos **dois** jogadores | ambos veem os dois; nada se acumula | levantamento; contagem de objetos estável ao longo do tempo (G3, G4) |
| B3 | Saques e itens coletáveis: criação, uma coleta remove para ambos, sem duplicações | nenhum saque duplicado (G5) | teste de coleta + levantamento |
| B4 | Terreno / células mineradas | ambos veem os mesmos buracos | contagens de terreno espelhado |
| B5 | Objetivos e progresso da missão, fim da etapa, vitória/derrota | mesmo estado e mesma tela de encerramento nos dois lados | RESULT nos dois papéis |
| B6 | Barreiras de pausa, subida de nível e loja | nunca duram mais que o tempo real de escolha do outro jogador; expiração é o último recurso (G1: hoje congela por 45 s) | asserção da duração da espera, não apenas de ausência de expiração |

## <a id="c-per-player-state-reported-to-the-host"></a>C. Estado individual informado ao host

| # | Item | Padrão | Comprovação |
|---|---|---|---|
| C1 | Posição, direção, animação, mira da arma (20 Hz) | fluido, sem teletransportes | erro entre posição do representante e posição real |
| C2 | Vida, **incapacitado** (sem movimento ou ataque), círculo de reanimação que se completa, morte | o jogador incapacitado realmente não se move; a reanimação termina com ambos presentes | teste da máquina de estados (hoje: move-se, nunca termina) |
| C3 | Dano causado e recebido pelo cliente | host aplica uma única vez | contagens de `EnemyHit` |
| C4 | XP compartilhada, cartas de subida de nível escolhidas por jogador | cartas diferentes, mesmo nível | teste de cartas |
| C5 | Reserva de Ouro/Nitra e compras na loja | uma carteira, arbitragem do host | teste de barreira da loja |
| C6 | Ganhos próprios do cliente (metaprogressão) separados dos do host | perfil do host é lido; salvamento do cliente intacto | salvamento antes/depois |

## <a id="d-session-lifecycle-where-the-real-test-bugs-lived"></a>D. Ciclo de vida da sessão (onde apareceram os bugs dos testes reais)

| # | Item | Padrão | Comprovação |
|---|---|---|---|
| D1 | Conectar, barreira de prontidão, sala, começar juntos | ambos carregam a mesma fase; nenhum começa sozinho | teste de início pela sala; ordem de início host/cliente invertida |
| D2 | Carregamento: cada um espera o outro | ninguém joga sozinho | teste de espera de carregamento (existe) |
| D3 | Fim da partida -> voltar ao menu -> **segunda partida** sem reiniciar | botão CO-OP recriado, sem estado obsoleto | novo teste: duas partidas seguidas (ausente; o teste real detectou o desaparecimento do botão) |
| D4 | Perda do par no meio da partida | aviso, sem congelamento, saída limpa | existe |
| D5 | Reconexão no meio da partida | opcional; hoje ambos precisam reiniciar | não implementada; decidir escopo |
| D6 | Latência: 50 ms, 150 ms + variação + 2 % de perda, 300 ms + 5 % de perda, interrupção de 3 s | sem dessincronização, congelamento ou eventos duplicados | **ainda não existe estrutura de testes de latência** |

## <a id="e-presentation-only-nice-to-have-must-not-change-state"></a>E. Apenas apresentação (desejável, sem alterar o estado)

Marcador fora da tela, painel de nome/vida do parceiro (fora de escopo segundo S14), câmera original (sem enquadramento cooperativo, decisão 5), nenhum clique visível no assistente quando a partida começa pela sala, avisos.

## <a id="decisions-2026-10-21"></a>Decisões (2026-10-21)

1. **Movimento dos inimigos (B1):** passar os snapshots de 2 Hz para **10 Hz** e então medir.
2. **Desbloqueios do host (A4):** os desbloqueios do host valem para ambos, **ativados por padrão** (hoje apenas com `-coopprofileadopt`, que a versão distribuída não define).
3. **Reconexão (D5):** **desnecessária.** Se um jogador cair, o host continua jogando; o cliente não se reconecta (a partida do cliente termina de forma limpa, como já implementado).
4. **Padrão de latência:** precisa passar com 150 ms + variação + 2 % de perda, sem congelamento nem dessincronização.
5. **Câmera (E):** **permanece como no jogo base**, seguindo o próprio anão. Aceita-se que o outro anão saia da tela; o marcador mostra onde ele está. Portanto, a câmera cooperativa que enquadra os dois anões (`CoopCamera`) deve ser desativada, e o teste `camera` e a linha de STATUS "Camera frames both dwarves" são aposentados e substituídos por "câmera original, marcador visível quando o parceiro está fora da tela".

## <a id="open-not-yet-decided"></a>Em aberto: ainda não decidido

Tipos de missão além de Elimination/Escort (S9 determina apenas missões principais), retransmissão pelo Steam (S10), agressividade por jogador (adiada).
