# <a id="the-lord-of-the-rings-the-two-towers-2002"></a>The Lord of the Rings: The Two Towers (2002)

| | |
|---|---|
| Motor | Stormfront "Fusion" (Xbox), jogado no PC pela recompilação estática [The Two Towers Recompiled](https://github.com/Gumpolas/TooTawersRecomp) v1.9.4 (xboxrecomp 0.12.0) |
| Versões testadas | Xbox comercial dos EUA, `Default.xbe` SHA-256 `ae2d1b5304b3e9572339b693a6a45ad0869bdaeec89aae374b5c14feebbb8d30` (título 0x45410010, versão 1), com código do port v1.9.4 (também v1.9.2) |
| Projetos | Cooperação no sofá sobre o port: [Volverine-Dude/TooTawersRecomp-coop](https://github.com/Volverine-Dude/TooTawersRecomp-coop) (fork do port, MIT; consulte `COOP.md`) |
| Nível de QA | automated (suíte de bots com 14 cenários no jogo real, 73 verificações; consulte QA) |
| Última atualização | 2026-10-21 |

## <a id="where-things-stand"></a>Situação atual

Cooperação local no sofá: dois jogadores em um PC, dois controles, uma câmera compartilhada, jogando as fases da história juntos. Sem rede: um jogo executa com segundo herói, com controle, personagem, armas, vida, munição, experiência e melhorias próprios. É alfa; problemas conhecidos abaixo. Somente código-fonte: cada jogador compila a partir de sua própria cópia.

## <a id="existing-work"></a>Trabalhos existentes

- Nenhum mod, patch ou hack cooperativo encontrado para The Two Towers (diretório Co-op Anything, busca web, 2026-10-17). Sem multiplayer ou código de rede.
- Dois ports para PC, nenhum cooperativo: [The Two Towers Recompiled](https://github.com/Gumpolas/TooTawersRecomp) (MIT no código próprio, partes LGPL de xemu) e [Athelas](https://github.com/Shagg88/Athelas) (MIT; estrutura Linux sem interface é bom modelo para bots).
- Return of the King tem cooperação integrada para 2 jogadores, mas em outro motor (próprio da EA); serve só como referência de projeto.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

Um processo, uma simulação, dois heróis. Tudo abaixo refere-se à versão comercial dos EUA; endereços do port (endereços virtuais xbe).

- **"O jogador" é um conjunto de globais**: `[0x43B15C]` herói, `[0x43B160]` controle, `[0x1CB8B4]` porta do controle e blocos perto de `0x43B1xx` e `0x1B0Cxx`. Jogador 2 é outro herói (gêmeo do primeiro, criado do registro de posicionamento do jogador 1 durante carregamento), cujas atualizações executam com globais trocadas por cópia própria. A maior parte do jogo então funciona sem alterações.
- **Scripts de fase** configuram herói por nome (`@AttachToBone`, `@SetEnemyID`, `@SetWeaponID`...). São repetidos para o gêmeo, com consultas de objetos (0xB4690) respondendo por ele.
- **Registros de herói**: `0x4AB598 + hero byte × 0x348` (byte do herói `[0x4AB69D]`: 1 Aragorn, 2 Legolas, 3 Gimli, 4 Isildur). Experiência em +0x6C, experiência corrente da fase em +0x90, medidor de avaliação de combate em +4. Jogador 2 tem cópia própria, trocada com seu contexto. Melhorias: 80 bytes por herói em `0x4AC5B0 + hero × 0x50`.
- **Tipo de personagem** (+0x2F0) define vida e munição (+0x304, máximo +0x306): Aragorn 0 (30), Legolas 7 (60), Gimli 8 (25).
- **Armas** são objetos (classe 0x174980, responsável +0x11C, identificador +0x2F4 para alcance e dados).
- **Partes que perguntam "é o jogador?"** e precisaram aceitar jogador 2: manipulador de acerto (0x849F0, medidor), prêmio por abate (0x99D40), coletas (0x8FC60 para 0x8F960), escolha de alvo inimiga (0x5A920) e scripts de comportamento, câmera (0x68DC0), escolha de movimentos (função de herói 0xD2310).
- **Checkpoints**: `@SetRespawnId` (0xB0FB0) guarda vida, munição e registro +0x90..+0xB3 em 0x1BB354; Replay após fim de jogo os restaura.
- **Interface inicial**: objeto de tela em 0x4AD050 (+4 próxima tela; 9 estatísticas, 10 loja, 7 salvar, 1 mapa, 6 jogar). Fim de missão 0xF1230(code).

Descobertas, evidências e pistas erradas: [NOTES.md](NOTES.md).

## <a id="what-we-changed"></a>O que alteramos

Cada item foi verificado com bots (capturas de quadros e logs); detalhes e evidências em NOTES.md.

- **Segundo jogador**: menu Co-op (New Game / Load Game, opções), vez do jogador 2 na seleção, controle próprio, HUD (vida, munição, anéis, medidor) e marcadores sobre as cabeças.
- **Posicionamento**: jogador 2 começa junto do primeiro em célula caminhável do mapa de caminhos, acompanha cenas e retorna ao lado do primeiro após cair no vazio.
- **Câmera compartilhada**: enquadra o ponto médio dos heróis e amplia o campo de visão quando se separam; limites Normal 1,3, Wide 1,5.
- **Combate**: inimigos escolhem qualquer herói (ameaça por jogador); acertos, abates e experiência do jogador 2 contam para ele; incapacitação, reaparecimento e fim de jogo para dois.
- **Movimentos próprios do jogador 2**: escolhas leem melhorias compradas do seu herói, não do primeiro; fixação de alvo usa seleção nativa.
- **Checkpoints**: após Replay do fim de jogo, experiência e estatísticas da fase do jogador 2 voltam aos valores do checkpoint, como para o primeiro.
- **Armas próprias do jogador 2**: cópias das armas de seu herói com identificadores correspondentes; Gimli usa alcance do machado e nunca pega arco do primeiro. Armas do primeiro sem cópia nunca são alteradas por seus eventos.
- **Armas à distância**: jogador 2 arremessa ou dispara de sua cópia (arco de Legolas, machado de arremesso de Gimli, arco de Aragorn; Isildur, sem arma própria, usa a de Aragorn), nunca da do primeiro.
- **Munição e coletas**: jogador 2 tem munição do próprio herói; suas coletas a repõem.
- **Após fase**: estatísticas do jogador 1, do 2, loja do 1, do 2, depois salvamento. Experiência e compras do jogador 2 são salvas no registro do herói e voltam ao carregar. Lojas percorrem abas das fases com esquerda/direita; Replay é omitido nas telas em sequência (ambas as lojas e estatísticas do 2).
- **Marcadores de cabeça**: P1/P2 sobre os heróis, projetados pelo volume de visão da câmera, escurecidos se algo é desenhado à frente da cabeça (sonda de profundidade no renderizador Direct3D 11).
- **Dificuldade** (opção cooperativa): dano inimigo, vida dos heróis, espera de reaparecimento e inimigos extras dos criadores.
- **P2 Bot** (opção cooperativa): IA provisória do jogador 2. Mantém-se num círculo ao redor do primeiro e dos companheiros, aproxima e golpeia inimigos próximos só quando ao lado deles, dispara de dentro do círculo contra distantes, bloqueia ocasionalmente, anda quando jogador 1 cai; no Watcher, apara junto a um tentáculo e o ataca após aparar. Deve ser reescrita com configurações adequadas de controle do jogador 2.

## <a id="qa"></a>QA

Suíte de bots executa o jogo real (instalação de teste) quatorze vezes, com ambos os heróis controlados por entradas roteirizadas, bots de navegação ou P2 Bot e seletores que preparam cada situação; confere aprovação/falha no log. Preserva capturas de quadros nativas por execução. Fica no fork, `tools/coop-bot/`.

| Cenário | O que verifica |
|---|---|
| start_place | jogador 2 carrega como Gimli do registro salvo, tipo próprio de personagem, junto do primeiro no mapa de caminhos |
| weapons | jogador 2 recusa armas do primeiro, machado recebe identificador de Gimli, arremessos são machados da cópia própria, munição própria diminui enquanto a do primeiro permanece; movimentos leem melhorias próprias |
| weapons_bow | Isildur jogador 2 dispara da própria cópia, nunca do arco de Legolas jogador 1 |
| kills_post | abate do jogador 2 lhe dá experiência, prêmios executam em seu contexto, primeiro ocioso não recebe; tela de estatísticas recebe experiência da fase; melhorias próprias liberam movimentos, as do primeiro nunca |
| levelup_shops | loja de cada jogador recebe sua subida de nível e pontos |
| pickups | toques do jogador 2 na aljava repõem jogador 2, nunca o primeiro |
| down_respawn | primeiro caído com segundo em pé: sem fim de jogo; primeiro reaparece junto do segundo |
| down_gameover | ambos caídos: fim de jogo |
| menus | fundo do menu Co-op, seleção atribuindo herói a cada um e fase iniciando com herói do segundo |
| camera | câmera amplia até limite Normal quando se separam, ambos os marcadores posicionados; sonda identifica ponto sob o chão como oculto |
| checkpoint | no checkpoint Watcher: após fim e Replay, experiência e estatísticas do segundo retornam aos valores salvos junto das do primeiro; P2 Bot aproxima de tentáculo e apara, nunca dispara ali |
| shop_left | esquerda percorre abas nas duas lojas e é retida onde alcançaria Replay oculto; tela de estatísticas do segundo não tem Replay |
| save_buy | loja do segundo fecha com experiência confirmada, jogo salva (segundo compra melhoria) |
| save_reload | experiência e registro salvo completo do segundo (checksum incluindo melhoria comprada) voltam ao carregar |

Cada cenário também verifica ausência de falha e taxa mediana de pelo menos 50 quadros/s. Configurações e salvamento da cópia são restaurados após cada execução.

Última execução completa (código do port 1.9.4 com alterações cooperativas publicadas, Direct3D 11, 2026-10-21):

```
Co-op bot suite, 2026-10-21 20:19, 24 min: 73 passed, 0 failed of 73 checks in 14 scenarios
```

Não cobertos: segundo controle físico (suíte dirige controle 2 por script), Vulkan, telas 4:3 e os próprios quadros (inspecionados visualmente).

## <a id="how-to-play"></a>Como jogar

Compile o fork da sua própria cópia, como o port: consulte [COOP.md](https://github.com/Volverine-Dude/TooTawersRecomp-coop/blob/coop/COOP.md). `generate.py` do port precisa do `Default.xbe` comercial dos EUA acima. Nunca compartilhe executáveis compilados ou código gerado: contêm código do jogo.

## <a id="known-issues"></a>Problemas conhecidos

- Tentáculos do Watcher não recebem acertos de nenhum herói nos bots; ainda em aberto como P2 Bot vencerá.
- P2 Bot pode ficar preso andando na água antes do chefe Gates of Moria; nenhum teste alcança ali (checkpoint do chefe começa depois).
- Marcadores escurecidos, não ocultos, atrás de paredes (profundidade não distingue parede de orc à frente); sonda só Direct3D 11. Marcadores afastando para fora ao ampliar visão vistos uma vez, sem reprodução.
- Inimigos grandes (troll da caverna): não testado se P2 Bot chega perto o suficiente para acertar.
- Altura de marcadores de convidados hobbits é hipótese; telas 4:3 não verificadas.
- Bots dirigem jogador 2 por entradas roteirizadas; segundo controle físico não coberto.

## <a id="credits"></a>Créditos

- **[The Two Towers Recompiled](https://github.com/Gumpolas/TooTawersRecomp)** de Gumpolas: port nativo que sustenta este modo cooperativo. Recompilação estática, renderizador, menus, heróis extras e configurações tornam tudo possível; cooperação é um conjunto de alterações sobre ele.
- **[xboxrecomp](https://github.com/sp00nznet/xboxrecomp)** de sp00nznet: ferramentas de recompilação estática usadas pelo port (com partes LGPL de xemu).
- **[Co-op Anything](https://github.com/cranebeaker/coop-anything)** de cranebeaker e colaboradores: guias seguidos aqui (triagem, QA com bots, relato e diretório).
- **[Athelas](https://github.com/Shagg88/Athelas)** de Shagg88: notas de Two Towers e estrutura de testes sem interface usadas como referência.
- The Lord of the Rings: The Two Towers pertence aos titulares dos direitos; nada do jogo incluído aqui.

## <a id="next-steps"></a>Próximos passos

- Configurações do controle 2, depois reescrever P2 Bot.
- Tentáculos do Watcher: descobrir o que permite à arma acertá-los.
- Download pronto para jogar, se possível sem distribuir código do jogo.
