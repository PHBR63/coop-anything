# <a id="earlier-gothic-3-co-op-projects-checked-2026-10-16-and-2026-10-17"></a>Projetos cooperativos anteriores de Gothic 3 (verificados em 2026-10-16 e 2026-10-17)

Nenhum deles ofereceu ao usuário uma história cooperativa utilizável; por isso, G3 Together foi criado do zero para não repetir suas limitações. Nenhum código ou arquivo desses projetos é usado no G3 Together.

| Projeto | O que foi possível verificar | Resultado |
|---|---|---|
| [Myrtana Accord](https://github.com/yevh/Gothic3) v0.35.0-beta.1 (Yevh, 2026-09) | ZIP oficial (SHA-256 `c2c5b2752755aad7d27009cc04bc47c515f93b32f0e2409b039ab0fdf8d0ae4e` e seus 31 checksums internos conferidos; os cinco hashes fixados da pilha corresponderam à instalação). Arquivo de licença: MIT "exceto onde indicado", sem nenhuma indicação. Código-fonte do núcleo C++ ausente tanto do arquivo quanto da árvore pública (estado `327c0b0`). Testado com dois clientes reais e as configurações distribuídas. | O estado das missões é compartilhado nos dois sentidos; nada mais é. Os jogadores não se veem, a sincronização de NPCs e combate está desativada e a reconexão com um jogo novo é recusada. |
| Gothic 3 Heroes (Pigeonade) | Um [relato prático de 2026-09-19](https://gothic.org.pl/gothic/modyfikacje/gothic-3-heroes-w-trybie-kooperacji/) cita a versão 0.3, convites Steam e troca de itens. Distribuição apenas pelo Discord. | Não testado: nenhum arquivo, licença ou código-fonte disponível. |
| [Sative's Gothic 3 Multiplayer](https://www.nexusmods.com/gothic3/mods/1) | Update3 (2016-03-25), "Public Alpha", exige CP 1.75.14. O autor informa perda de inventário e combate com inimigos sem sincronização. Uma resposta do autor em 2024 no índice do fórum impede comprovar a classificação como abandonado. | Não testado: o download exige login no Nexus. |

## <a id="myrtana-accord-test-qa-level-automated-scope-shared-quest-state"></a>Teste do Myrtana Accord (nível de QA `automated`, escopo: estado compartilhado das missões)

Duas cópias completas da instalação com perfis redirecionados, preparadas manualmente a partir do ZIP verificado (o instalador não foi executado), um `g3coop_server.exe` local em 127.0.0.1 e as configurações distribuídas. Um plugin de SDK em cada jogo recebeu comandos numerados de um executor Python; os hashes dos salvamentos reais do usuário foram conferidos antes e depois de cada execução, sem alterações.

- `coop`, 3 de 3 PASS (2026-10-17, execuções `000901`, `001012`, `001120`): os dois jogadores foram admitidos e listados pelo outro; três missões compartilhadas estavam Open em ambos; o host executa `Montera_Revolution` e o cliente lê Running (4 s); o cliente conclui `Faring_Revolution` e ambos leem Succeeded (0,5 a 4 s); `Silden_Revolution` permanece Open.
- Controle negativo (exigir um estado impossível no cliente): FAIL, conforme necessário.
- `rejoin`: FAIL. Após um jogo novo, o cliente registrou "Campaign character binding deferred: reason=3" a cada dois segundos e nunca recebeu as missões da campanha.
- O mod recusou o encerramento do jogo durante uma campanha em 3 de 7 execuções.
