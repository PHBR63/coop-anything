---
name: coop-decomp-port
description: "Executar nativamente no PC um jogo de console a partir de código-fonte (descompilação, recompilação estática ou reimplementação do motor) para adicionar modo cooperativo no código, como Ocarina of Time no Ship of Harkinian e Super Mario 64 no sm64coopdx."
---

<a id="decomp-or-recomp-a-console-game-for-co-op"></a>
# Descompile ou recompile um jogo de console para modo cooperativo

1. Procure um port para PC, descompilação ou recompilação estática existentes do jogo e região exatos. Contribuir para um projeto é preferível a recomeçar.
2. Se já existe port para PC, adicione rede ao código: autoridade do host, indicadores e itens sincronizados, estado salvo na entrada e representantes dos jogadores remotos. Estude como Anchor (Ship of Harkinian) e sm64coopdx fizeram isso.
3. Se só existe recompilação (N64Recomp, XenonRecomp, recompiladores de PS2 e PS3), adicione o modo cooperativo por hooks de mods ou patches. O código continua sendo traduzido por máquina, então espere mais engenharia reversa.
4. Se a descompilação é parcial, ajude a concluir as partes necessárias (jogador, atores, salvamentos, carregamento de cenas), em vez do jogo inteiro.
5. Ao começar uma descompilação, separe o binário (splat, decomp-toolkit) e obtenha correspondência função por função, usando objdiff como oráculo. Agentes podem trabalhar em funções em paralelo; o coordenador verifica cada correspondência e monitora tentativas de manipular a pontuação. Para uma sequência executada por agentes e julgada por um oráculo de comportamento, comece pelo DecompPipeline (github.com/GeneralAtrox/DecompPipeline; alvo Dreamcast, adicione um alvo para outras CPUs).
6. Questões legais: nunca distribua ROMs, ISOs ou recursos extraídos. Os ports extraem os recursos da cópia do próprio jogador em tempo de execução.

Detalhes: `playbook/decomp-and-recomp.md`.
