# <a id="the-witcher-3-wild-hunt-2015"></a>The Witcher 3: Wild Hunt (2015)

| | |
|---|---|
| Motor | REDengine 3 (código-fonte WitcherScript + executável nativo fechado) |
| Versões testadas | Steam, patch Remastered 5.01 (executável 5.0.0.1048522, compilação 25773555, apenas DX12) |
| Projetos | Witcher Online, W3Coop (seu port para 5.01), WitcherMMO, w3m, Witcher3-Multiplayer, Witcher3-MP ([diretório](../../DIRECTORY.md)) |
| Nível de QA | W3Coop (Witcher Online na versão 5.01): automated (2 testes, consulte QA). Outros projetos na versão 5.x: none |
| Última atualização | 2026-10-18 |

## <a id="where-things-stand"></a>Situação atual

Witcher Online é o único projeto utilizável: jogadores se veem, conversam, cavalgam juntos e compartilham escolhas de diálogo em grupo, mas inimigos, NPCs e missões não são compartilhados. Ele só suporta 4.04; a atualização Remastered (5.0, setembro de 2026) quebra sua versão pública. W3Coop, um port para 5.01 com retransmissão pelo Steam (pré-lançamento v0.1.0), compila e passa em dois testes automatizados com dois clientes (visibilidade dos jogadores, movimento); ainda não foi testado entre duas contas Steam reais. Ainda não existe história cooperativa com inimigos e missões compartilhados para nenhuma versão.

## <a id="existing-work"></a>Trabalhos existentes

- [Witcher Online](https://github.com/rejuvenate7/WitcherOnline) (rejuvenate7, GPL-3.0, último envio em 2026-08): mod WitcherScript + cliente nativo ASI (por [WitcherNativeBridge](https://github.com/rejuvenate7/WitcherNativeBridge), MIT, atualizado para 5.01 em 2026-10-08) + servidor UDP Java. Exige Custom Player Characters, Chill Out e Shared Imports (apenas no Nexus, sem código-fonte público).
- [W3Coop](https://github.com/Emillock/witcher3-coop): Witcher Online portado para 5.01 ([fork, branch `remastered-5.01`](https://github.com/Emillock/WitcherOnline/tree/remastered-5.01)), mais retransmissor Steam, pacote para jogadores e a estrutura de testes descrita abaixo. Criado seguindo o fluxo destes guias.
- [WitcherMMO](https://github.com/eofim/WitcherMMO): fork renomeado de Witcher Online; os objetivos de NPCs/missões não foram implementados.
- [w3m](https://github.com/momo5502/w3m) (momo5502): hooks nativos em endereços fixos de um executável anterior à remasterização; inicializador e servidor próprios.
- [Witcher3-Multiplayer](https://github.com/werasik2aa/Witcher3-Multiplayer) (descontinuado em 2026-01) e [Witcher3-MP](https://github.com/Hyjarion/Witcher3-MP) (um envio, 2023).

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Sem código de rede.** Cada tentativa multiplayer acrescenta seu próprio transporte; Witcher Online usa um servidor UDP separado e cria NPCs "fantasmas" a partir dos modelos de entidade de seu próprio DLC para os jogadores remotos.
- **O código-fonte dos scripts é distribuído** em `content\content0\scripts` (1525 arquivos `.ws`; UTF-8 na versão 5.x). Os mods ficam em `<game dir>\mods\<mod>\content\scripts` e são compilados na inicialização junto aos originais. As anotações `@wrapMethod`, `@addMethod`, `@addField`, `@replaceMethod` evitam substituir arquivos inteiros. Na versão 5.x, `@addMethod(Class) import function X(...)` expõe um método nativo não declarado, e o pré-processador (`#ifdef`/`#ifndef`/`#else`/`#endif`, `-scriptdefines=`) funciona inclusive dentro de corpos de funções.
- **Funções nativas de C++:** WitcherNativeBridge (carregado como `.asi` pelo Ultimate ASI Loader em `bin\x64_dx12\dinput8.dll`) permite que outros plugins ASI registrem funções nativas de scripts. Strings de scripts e CNames usam bytes UTF-8 na versão 5.x (UTF-16 na 4.x).
- **Verificação de compilação:** `witcher3.exe -verifyscriptsandexit` compila e encerra; os erros aparecem na janela "Script Compilation Errors" (leia seu controle Edit com `WM_GETTEXT`). Erros em arquivos de mods são exibidos sem o prefixo `[content0]`.
- **Mudanças de API da 5.0 que quebram mods da 4.04:** `map` é palavra-chave; áreas são CNames (`GetCurrentArea() : name`, `GetDeprecatedAreaName(int)`, sem `AreaTypeToName`); os dados das cartas de Gwent passaram para funções nativas indexadas pelo nome da carta (`GetGwentCard`, `GetDeck`, sem `cardIndices`); `CInputManager.IgnoreGameInput` agora é nativo; `.w3strings` v164 e `metadata.store` v7 (pacotes DLC v6 da 4.04 ainda carregam).
- **Mods do Steam Workshop carregam automaticamente** a partir de `steamapps\workshop\content\292030`; um mod do Workshop da época da 4.04 quebra a compilação em toda inicialização. `Documents\The Witcher 3\mods.settings` com `[modName] Enabled=0` desativa um mod específico e é respeitado pelo compilador.
- **Dados do usuário:** `Documents\The Witcher 3` (`dx12user.settings` apenas na 5.x, `gamesaves\`, `mods.settings`). Salvamentos da 4.04 carregam na 5.01 e exibem uma vez o diálogo "skill points reset".
- **Instância única:** mutex nomeado `cdprojekt_red_the_witcher_3_wild_hunt` (CreateMutexA); a segunda cópia exibe "game is already launched" e encerra.

## <a id="what-the-501-port-changes"></a>O que o port para 5.01 altera

- Cliente: leitura e escrita das strings de scripts como UTF-8 na versão 5.x (UTF-16 na 4.x), substituições opcionais por `WO_USERNAME`/`WO_SERVER_IP`/`WO_SERVER_PORT` para várias instâncias em uma instalação.
- Scripts: renomear variáveis `map`; importar com `import` a função nativa `IgnoreGameInput`; tratar áreas como CNames, mantendo os antigos códigos numéricos no transporte (servidor e protocolo inalterados).
- Duelos de Gwent isolados por `#ifdef WO_GWENT_PVP`: precisam de um novo tabuleiro para a versão 5.x (o `gwint_game.redswf` da 4.04 do mod substituiria a interface da remasterização; por isso, não é instalado).
- Custom Player Characters e Chill Out substituídos por declarações provisórias.

## <a id="qa"></a>QA

Estrutura de testes: servidor local e dois clientes do jogo em um PC. Cada cliente roda em seu próprio ambiente Documents isolado (cópias das configurações + um salvamento), com o preset "low" do próprio jogo, RT desligado, limite de 30 FPS, áudio silenciado e hooks internos para que as janelas de teste continuem sem foco e sem capturar mouse, foco ou teclado. Um bot interno (mod de scripts + ASI de testes que fornece `W3T_GetEnv`, `W3T_Log`, `W3T_Quit`) pula os vídeos, fecha o aviso de conta sem responder a questões de consentimento, responde a diálogos do sistema, carrega o salvamento e informa o estado a cada segundo; a estrutura exige a linha PASS de cada bot.

| Teste | O que verifica | Resultado (2026-10-18) |
|---|---|---|
| `see_each_other` | cada cliente cria o fantasma do outro jogador na posição recebida pela rede | PASS (2 clientes) |
| `movement` | um jogador se teletransporta de um lado para outro; a cópia do fantasma no outro cliente chega a até 2 m da posição de rede após cada movimento | PASS (2 clientes, 4 movimentos observados) |
| `movement --relay` | o mesmo, com o segundo cliente conectado apenas pelo retransmissor Steam (host + retransmissor de entrada com uma `steam_api64.dll` simulada) | PASS (2 clientes, também contra o pacote compilado para jogadores) |
| autoteste do retransmissor | 20 pacotes UDP pelos retransmissores de hospedagem e entrada, cliente do jogo iniciando 25 s atrasado; um usuário Steam fora da sala não deve alcançar o servidor | PASS |

Retransmissor Steam ("w3relay", padrão HXCoop de [networking-steam-spacewar.md](../../playbook/networking-steam-spacewar.md)): um executável auxiliar roda como Spacewar (AppID 480), cria uma sala apenas para amigos e transporta os pacotes UDP do Witcher Online pelo Steam; ninguém precisa digitar IP ou redirecionar portas. Ele carrega a `steam_api64.dll` do próprio jogo. Um teste básico com Steam real (inicialização, criação da sala, encerramento limpo) passou; a entrada entre duas contas Steam reais ainda não foi testada.

## <a id="how-to-play"></a>Como jogar

Baixe `W3Coop-0.1.0.zip` nas [versões de W3Coop](https://github.com/Emillock/witcher3-coop/releases) e copie o conteúdo para a pasta do jogo. O host executa `bin\w3coop\Host co-op.cmd` (exige Java 21+) e convida os amigos; os amigos executam `Join co-op.cmd`; então todos iniciam o jogo e carregam um salvamento. É um pré-lançamento: a entrada entre duas contas Steam reais ainda não foi testada.

## <a id="known-issues"></a>Problemas conhecidos

- Os duelos de Gwent estão desativados no port para 5.x.
- Personalização do personagem e sentar em tavernas (dos dois mods de dependência) são implementações provisórias.
- Duas instâncias da remasterização precisam de cerca de 4 GB de VRAM e 10 GB de RAM cada; se outros aplicativos ocuparem a maior parte de uma placa de 12 GB, elas caem para poucos FPS.

## <a id="next-steps"></a>Próximos passos

- Teste real do retransmissor com duas contas; mais testes com bots (conversa, gestos, sincronização de grupo).
- Tabuleiro de Gwent para duelos na versão 5.x.
- Inimigos compartilhados (autoridade do host sobre o estado dos NPCs, dano encaminhado ao host) e progresso de missões (sincronização de fatos): ainda não iniciados em nenhum projeto.
