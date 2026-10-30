---
name: coop-build-from-zero
description: "Criar modo cooperativo para um jogo de um jogador que não tem mod cooperativo: escolher um ponto de hook, representar o segundo jogador, escolher um modelo de autoridade, sincronizar o mundo e a história, tratar transições de fase e salvamentos e testar com dois clientes reais."
---

<a id="build-co-op-from-zero"></a>
# Crie o modo cooperativo do zero

A ordem importa: cada etapa precisa funcionar e ser testada antes da próxima.

1. Ponto de hook: extensão de scripts, carregador de mods (BepInEx, UE4SS, REFramework), DLL injetada ou port de código-fonte. Consulte `playbook/tools.md`.
2. Transporte: escolha uma biblioteca e um método de conexão (`coop-networking`). Comece com IP direto em um único PC.
3. Segundo jogador visível: crie um representante do jogador remoto e transmita sua transformação e animação.
4. Autoridade: o host controla inimigos, NPCs e objetos do mundo; cada jogador controla a si mesmo. Use lockstep somente se o jogo for determinístico.
5. Interações: portas, coleta de itens, dano e mortes, com decisão do host.
6. História: indicadores de missões, diálogos e cenas. Decida, para cada parte do estado, se será compartilhada ou individual.
7. Transições: mudanças de fase, salvamentos, entrada após o início e desconexões.
8. Testes em todas as etapas com clientes reais do jogo (`coop-qa`).
9. Distribuição: um instalador por sistema operacional que encontre o jogo, instale o carregador e o mod com versões fixadas e conferência de SHA-256, atualize e desinstale. Consulte `playbook/shipping-to-players.md`.

Estude primeiro como os mods existentes fizeram cada etapa: `playbook/how-coop-mods-work.md`.
