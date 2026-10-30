---
name: coop-revive
description: "Concluir um mod cooperativo existente com bugs, parado ou abandonado: obter a última versão compilada, auditar por subsistema, corrigir em pacote separado e testar com clientes reais do jogo."
---

<a id="revive-an-existing-co-op-mod"></a>
# Retome um mod cooperativo existente

1. Obtenha a versão compilada mais recente (consulte servidores de compilação e páginas de versões; confira o hash).
2. Obtenha código legível: extraia scripts, descompile partes nativas e consiga o código de referência do jogo base.
3. Audite por subsistema com agentes em paralelo e acesso somente de leitura; verifique cada descoberta antes de corrigir.
4. Corrija sem recompilar o original: um pacote novo com subclasses substituídas pelos hooks do próprio mod, um módulo por subsistema. Mantenha `BUGS.md` com itens corrigidos, abertos, refutados e fora de alcance.
5. Teste um host e um cliente real em um PC; depois transforme cada correção em um teste automatizado (`coop-qa`).
6. Simplifique o uso: um instalador por sistema operacional (`playbook/shipping-to-players.md`), hospedagem e entrada com um clique e retransmissão pelo Steam (`coop-networking`).
7. Dê crédito ao autor original e ofereça as correções ao projeto de origem.

Detalhes: `playbook/reviving-abandoned-mods.md`. Exemplo prático: games/deus-ex.
