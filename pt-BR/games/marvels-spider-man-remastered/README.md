# <a id="marvels-spider-man-remastered-2022"></a>Marvel's Spider-Man Remastered (2022)

| | |
|---|---|
| Motor | Motor proprietário da Insomniac, 64 bits, DirectX 12. Binário fechado: um `Spider-Man.exe` (121.901.008 bytes) e DLLs de componentes intermediários; dados em `<game dir>\asset_archive\` (arquivo `toc`, `dag`, `a00s034.us` e arquivos contêiner de `g00s000` a `g00s033`) |
| Versões testadas | Versão registrada, nenhum mod testado: Steam, app id 1817070, build id 23986256. SHA-256 de `Spider-Man.exe`: `e297d4d94f1ffe4febf289745e79e7b6fa233a788e7a00f480fc77c55db81ad1`. O executável não contém recurso de versão de arquivo |
| Projetos | Spider-Man Remastered Multiplayer, de hbgda: https://www.patreon.com/hbgda (entrada no diretório "Spider-Man Remastered Multiplayer (hbgda)") |
| Nível de QA | community-reports (nada foi executado para este relato; consulte QA) |
| Última atualização | 2026-10-19 |

## <a id="where-things-stand"></a>Situação atual

Sim, por meio de um beta fechado pago. O mod de hbgda permite que vários jogadores (até 7, segundo relatos) se balancem juntos pelo mundo aberto; exploração livre, esconderijos e desafios de combate ou furtividade supostamente funcionam. É possível entrar em missões da história e secundárias em modo cooperativo, mas elas não foram feitas para isso; jogadores relatam bugs, encerramentos inesperados e cenas quebradas nessas partes.

## <a id="existing-work"></a>Trabalhos existentes

Pesquisado em 2026-10-19: diretório deste repositório, busca na web (os resultados eram notícias; uma consulta direcionada a Reddit, GitHub e X não retornou esses sites), página Nexus e página Patreon. Reddit, GitHub e X não foram pesquisados diretamente.

- **Spider-Man Remastered Multiplayer (hbgda).** Beta fechado para apoiadores do nível "Web-Head", de US$ 10 (ComicBook, 2025-08-26). Não é de código aberto; nenhum repositório público encontrado.
  - A cobertura começa no fim de agosto de 2025: ComicBook em 2025-08-26, Kotaku e Game Rant em 2025-08-27, 80.lv em 2025-08-28.
  - Última atividade: a publicação Patreon mais recente, "SMT Progress Update and Recent Issues", tinha cerca de quatro dias quando consultada em 2026-10-19 (é restrita; seu conteúdo é desconhecido).
  - Um Discord da comunidade tinha mais de 11.000 membros, mais de 2.000 ativos (Insider Gaming, 2025-08-28); nenhum convite público é fornecido aqui.
  - A página Nexus (mods/5696) respondeu HTTP 403 à consulta automatizada de 2026-10-19. A nota anterior do diretório dizia que a equipe Nexus a removeu; não foi possível conferir novamente.
- Nenhum outro projeto cooperativo para a edição Remastered foi encontrado. Os mods multiplayer de Marvel's Spider-Man 2 são projetos separados para outro jogo.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

Observado na cópia instalada (somente listagem de arquivos, sem descompilação):

- Um executável nativo grande; não há scripts soltos na raiz da instalação. Os dados ficam em `asset_archive\` (um arquivo `toc` e arquivos contêiner numerados). Não foi verificado se os contêineres incluem scripts.
- DLLs de componentes intermediários presentes: `steam_api64.dll`, `bink2w64.dll`, `XAudio2_7.dll`, NVIDIA Streamline / DLSS, AMD FidelityFX, Intel XeSS, `crs-client.dll` / `crs-handler.exe` (relator de falhas).
- O jogo para um jogador não oferece multiplayer; portanto, não há código de rede original a reaproveitar.

Desconhecidos: como o mod de hbgda insere hooks, o que sincroniza, seu transporte (Steam ou servidores próprios) e quais compilações aceita. As publicações Patreon que poderiam informar isso são restritas.

## <a id="what-we-changed"></a>O que alteramos

Nada. Este relato registra a identidade do jogo e o estado do mod existente.

## <a id="qa"></a>QA

Nenhum teste foi executado. O nível de QA se baseia em relatos de jogadores na cobertura da imprensa (ComicBook, Kotaku). Ninguém aqui executou o mod na compilação 23986256.

## <a id="how-to-play"></a>Como jogar

Assine o Patreon de hbgda no nível que dá acesso ao beta e siga as instruções de instalação de lá. Baixe somente pelo Patreon; reenvios em outros locais não foram avaliados.

## <a id="known-issues"></a>Problemas conhecidos

Segundo relatos de jogadores em 2025:

- História principal e missões secundárias não foram projetadas para modo cooperativo: espere bugs, encerramentos inesperados e cenas quebradas.
- Beta fechado: acesso limitado e pago.

## <a id="next-steps"></a>Próximos passos

- Registrar quais compilações do jogo o beta atual aceita e se atualizações Steam o tornam incompatível.
- Se alguém com acesso ao beta concordar, documentar o transporte (Steam P2P, IP direto ou servidor hospedado) e os estados sincronizados, sem copiar arquivos do mod.
- Criar um mod cooperativo independente seria um projeto de binário fechado sem código de rede, o caso mais difícil de playbook/triage.md. Participar do mod existente ou aguardar seu avanço é o melhor caminho.

## <a id="sources"></a>Fontes

- https://comicbook.com/gaming/news/marvels-spider-man-co-op-multiplayer-mod-pc/
- https://kotaku.com/spider-man-ps4-pc-multiplayer-mod-great-web-insomniac-2000620767
- https://gamerant.com/spider-man-multiplayer-pc-mod/
- https://80.lv/articles/spider-man-remastered-received-a-fan-made-multiplayer-option
- https://insider-gaming.com/spider-man-co-op-mod/
- https://www.patreon.com/hbgda
