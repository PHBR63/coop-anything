# <a id="research-notes-spider-man-friend-or-foe"></a>Notas de pesquisa: Spider-Man: Friend or Foe

Verificado em 2026-10-21. A implementação e as evidências detalhadas ficam no [repositório de código-fonte separado](https://github.com/IlkinQafarov/spider-man-friend-or-foe-online).

## <a id="identity-and-entry-relationship"></a>Identidade e relação entre as entradas

O executável Windows inspecionado é a versão 1.0.0.111, SHA-256 `ebd30047d7e58c95bf7dc4bd1fb4a5780e16aa472b61c25a8c421632662083db`. Ele aceita dois pacotes de idioma coerentes, com conteúdo de jogo compartilhado e arquivos localizados diferentes. Outras compilações não são compatíveis.

As três entradas do diretório descrevem o modo cooperativo local oficial, este protótipo de código-fonte nativo e um protótipo do Discord listado anteriormente. A relação deste último com o código-fonte e o executável é desconhecida. Rótulos anteriores misturavam atribuição ao desenvolvedor com atribuição ao motor Alchemy; nenhuma estabelece uma família de motor para esta compilação inspecionada. As três entradas agora usam unknown até haver corroboração. O [anúncio da distribuidora](https://investor.activision.com/static-files/d8459280-fceb-49b0-9210-86bb7010c3d3) estabelece o contexto cooperativo e das plataformas, não a identidade do motor.

## <a id="observed-and-derived"></a>Observações e deduções

O [registro de estado](https://github.com/IlkinQafarov/spider-man-friend-or-foe-online/blob/main/docs/STATUS.md) atual separa verificações delimitadas com bots que passaram, tentativas anteriores que falharam e recursos não verificados. O cenário 11 atual passou em um caso de teste de 7.200 ticks com três áreas, um de 3.600 ticks com pausa/combate e um ciclo de vida de jogo tranquilo de 361 ticks. Foram usados processos na mesma máquina; isso não comprova funcionamento em WAN nem cooperação na campanha inteira. Um teste básico de sala com uma conta não transportou tráfego do jogo.

Lições úteis das falhas preservadas: volumes de saída obsoletos sobreviveram às mudanças de áreas carregadas dinamicamente; um checksum incluía preenchimento não inicializado e histórico de modos inativos; um caso de teste alterava a entrada após a etapa medida de vinculação nativa. As correções preservam campos semânticos e verificações contínuas, em vez de suprimir divergências. Uma falha posterior na inicialização revelou uma consulta nativa sem limites a nomes de teclas. A proteção delimitada passa nos testes atuais, mas o layout original e o gatilho alvo continuam sem confirmação.

## <a id="unknown-and-next-gate"></a>Desconhecidos e próxima verificação

New Game/Continue da versão comercial, seleção de centro e missões, salvamento/retomada nativos, progressão localizada de NIS, controles físicos e distribuição pelo Steam entre dois PCs continuam incompletos ou não verificados. O próximo passo é uma verificação finita desde New Game da versão comercial até o centro e a primeira missão, com escolhas nativas sincronizadas e prontidão de carregamento. Não se declara teste humano de campanha, binário público ou oráculo de mundo completo.

## <a id="external-sources"></a>Fontes externas

- [Anúncio de lançamento da Activision](https://investor.activision.com/static-files/d8459280-fceb-49b0-9210-86bb7010c3d3): contexto oficial do modo cooperativo e das plataformas.
- [Análise contemporânea para PC](https://www.swiftworld.net/2007/10/13/pc-spider-man-friend-or-foe-review/) e [análise da GameSpot](https://www.gamespot.com/reviews/spider-man-friend-or-foe-review/1900-6180451/): modo cooperativo local e ausência de suporte on-line.
- [Documentação de rede da Valve](https://partner.steamgames.com/doc/features/multiplayer/networking): API de transporte pretendida, não evidência da distribuição deste mod.
- [Registro existente no Discord](https://discord.com/channels/1561411702082510879/1562185850777772152): referência de projeto preservada; não houve acesso à conta nem verificação de compilação aqui.
