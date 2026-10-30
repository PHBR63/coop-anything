---
name: coop-qa
description: "Comprovar o funcionamento cooperativo sem sessões humanas de teste: instalações isoladas, inicializador do host e N clientes reais, bot interno, asserções de estado compartilhado, detecção de falhas, testes com latência e perda e mutações para verificar que cada teste consegue falhar."
---

<a id="automated-co-op-qa"></a>
# QA automatizado do modo cooperativo

1. Instalações isoladas (cópia ou hardlink), modo janela, sem introdução, com arquivos INI e salvamentos próprios.
2. Inicializador: host e N clientes em um PC, exibe `RESULT: PASS` ou `FAIL`, falha se um cliente encerrar inesperadamente ou travar (leia a janela de erro e o log na tela).
3. Bot interno ao jogo: etapas, esperas com limite de tempo, asserções de estado compartilhado e registros PASS/FAIL.
4. Arquivo da suíte e executor; execute novamente a suíte completa após cada merge.
5. Desative cada correção uma vez: o teste correspondente precisa falhar.
6. Verifique o modo esperado (número de jogadores, mapa, indicadores) antes de verificar os resultados.
7. Faça testes com latência e perda; use uma instalação cliente sem o mod para testar os downloads.
8. Use capturas de tela e logs do próprio jogo, nunca capturas da área de trabalho.

9. Use as ferramentas prontas em `tools/` (simulador de caos, gravador de eventos, fuzzer, reserva e conjunto de instâncias, cenários, bots e verificador de animações), em vez de reescrevê-las; consulte a skill `coop-sync-testing`.

Detalhes: `playbook/automated-qa.md`.
