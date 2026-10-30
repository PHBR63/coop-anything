# Tradução completa para português do Brasil

Tradução do fork [PHBR63/coop-anything](https://github.com/PHBR63/coop-anything), baseada no commit `cbb37dc16c164877f50a8a00af673fb1874fddbb`. Revisão consolidada em 2026-10-30 19:45 UTC.

## Cobertura

- **246/246 documentos Markdown** preparados e revisados: 245 com conteúdo humano traduzido e o apontador técnico `CLAUDE.md` preservado.
- **303/303 arquivos não Markdown** preparados: comentários, docstrings, descrições, ajuda e metadados humanos pertinentes traduzidos; código, identificadores, contratos de máquina, licenças e binários preservados.
- **364/364 notas do catálogo** traduzidas. Todos os campos de dados fora de `notes` permanecem iguais.
- Auditoria suplementar: 97 arquivos, 213 comentários e 17 textos humanos adicionais. Nomes técnicos e saídas usadas como contratos de testes continuam literais.

## Organização e inglês original

O README principal está em português. O [README original em inglês](README.en.md) foi preservado byte a byte. Os demais originais permanecem em seus caminhos, e a tradução completa está na árvore [pt-BR](pt-BR/README.md). As ferramentas e fluxos de execução originais continuam nos caminhos da raiz; as cópias localizadas servem também para consulta dos comentários em português.

A licença [MIT original](LICENSE) e as licenças de terceiros permanecem integrais. Nomes de projetos, comandos, endereços, chaves, enums, identificadores e evidências literais não foram traduzidos quando isso alteraria seu significado técnico.

## Validação

- Inventário dos 549 originais e hashes das 549 cópias: [inventário](localization/inventory.json).
- Comparação de 26,893 ocorrências de código inline, 257 blocos e 3,239 títulos.
- Sintaxe e AST funcional de 146 arquivos Python verificadas; código fora dos comentários preservado em 88 arquivos C/C++/C# e 20 scripts; JSON/YAML analisados estaticamente.
- 3,153 aliases de âncoras inglesas adicionados, mantendo as âncoras portuguesas; 104 destinos locais normalizados. Nenhum erro de destino ou fragmento na árvore localizada nem no README principal.
- Três notações técnicas que o Markdown original interpretava como links foram escapadas apenas na tradução, preservando o texto visível.
- Auditoria independente por varredura e amostragem: três correções semânticas aplicadas (disfarce em MW2 e dois qualificadores em NieR). A amostragem não equivale a uma segunda leitura integral de todos os documentos.

Relatórios: [validação final](localization/final-validation.json), [navegação](localization/navigation-report.json), [auditoria suplementar](localization/supplement-coverage.json), [revisão independente](localization/revision-markdown.json) e [terminologia](localization/GLOSSARY.pt-BR.md).

Nenhum código do projeto foi executado nesta tradução. Não foram instalados programas ou modelos. As verificações são estáticas; não demonstram execução dos jogos ou testes do projeto. O commit de publicação usa `[skip ci]` para evitar a execução automática dos workflows do projeto, conforme a restrição desta tarefa. O upstream não foi alterado.

## Notas da alteração

Tradução integral da documentação, guias, instruções de agentes e habilidades, relatos de pesquisa e diretório; tradução de comentários e textos humanos pertinentes de código/configurações; README inicial em português com acesso ao inglês original; navegação localizada e compatibilidade de âncoras; relatórios verificáveis de cobertura e preservação estrutural.
