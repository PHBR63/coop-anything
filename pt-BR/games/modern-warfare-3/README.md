# <a id="call-of-duty-modern-warfare-3-2011"></a>Call of Duty: Modern Warfare 3 (2011)

| | |
|---|---|
| Motor | IW 5.0 (fechado; derivado de id Tech 3) |
| Versões testadas | AppIDs Steam 42680 (SP: campanha + Spec Ops) e 42690 (MP), conjunto de conteúdo de 32 bits; motor testado com o servidor dedicado de 32 bits anterior a 2026 `iw5mp_server.exe` (SHA-256 `F271C305…418D20`) |
| Projetos | AlterWare IW5-Mod (Spec Ops/Survival cooperativo, código fechado); open-iw5 (reimplementação aberta do motor, base da tentativa de campanha cooperativa) |
| Nível de QA | none (campanha cooperativa em fase de engenharia reversa; nenhum teste cooperativo executado) |
| Última atualização | 2026-10-19 |

## <a id="where-things-stand"></a>Situação atual

Não existe campanha cooperativa para Modern Warfare 3 (2011) em nenhuma plataforma, e nenhum projeto tentou implementá-la. O que existe é **Spec Ops / Survival** cooperativo para 2 jogadores: oficial no jogo e acessível hoje no PC pelo cliente fechado AlterWare IW5-Mod (ambos precisam possuir uma cópia no Steam). Este relato descreve uma tentativa de criar a **campanha** cooperativa do zero, partindo de uma reimplementação aberta do motor.

## <a id="existing-work"></a>Trabalhos existentes

- **AlterWare IW5-Mod** - cliente comunitário atual de MW3, com foco principal em jogo para um jogador/cooperativo, além de MP com bots e servidores dedicados. Código fechado; exige uma cópia de propriedade do usuário no Steam. O modo cooperativo é Spec Ops/Survival, não a campanha. ([alterware.dev](https://alterware.dev/), [guia de instalação](https://forum.alterware.dev/t/iw5-mod-install-guide/462))
- **MW3 Survival Mode: Revived** (ModDB, 2026) - leva conteúdo de Survival ao cliente AlterWare; seu FAQ afirma que o modo cooperativo Spec Ops **dessincroniza**, ou seja, a sincronização cooperativa não funciona. [moddb.com/mods/mw3-survival-mode-revived](https://www.moddb.com/mods/mw3-survival-mode-revived)
- **TeknoMW3** (TeknoGods) - cliente antigo que adicionou LAN/IP direto para MP e Spec Ops cooperativo; ainda citado por usuários em 2026, mas historicamente associado ao entorno da pirataria, sendo apenas referência de trabalho anterior.
- **Plutonium IW5** - cliente somente multiplayer; exige conta (https://docs.cbservers.xyz/games/iw5).
- **open-iw5** (momo5502, cadeia de forks cydiakk -> louvenarde) - cliente de MW3 para um jogador e multiplayer, de código aberto **GPL-3.0**, "muito experimental e inacabado"; exige os arquivos do servidor dedicado de MW3 e aplica patches por deltas HDiffPatch. O upstream foi fechado; um fork preservado é https://github.com/louvenarde/open-iw5. Essa é a base do nosso trabalho.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Fases** são fastfiles (`zone/*.ff`, `IWffu100` não assinado): um contêiner zlib externo com `XAssetList` compactada, dados por recurso e fluxos zlib aninhados (conjuntos de strings de ScriptFile, texto de RawFile). A compilação de 32 bits usa ponteiros de 4 bytes e `XAssetList` compactada de 16 bytes; a compilação de 64 bits de 2026 usa ponteiros de 8 bytes (lista de 32 bytes).
- **Scripts** usam GSC compilado em recursos `ASSET_TYPE_SCRIPTFILE` (tipo `0x27`) dentro das zonas. Ali ficam a lógica das missões de campanha, objetivos e armazenamento dos indicadores da história. Só as 10 zonas da campanha SP contêm cerca de 23,8 mil indicadores no nível de scripts e 2,1 milhões de strings.
- **Código de rede:** o lado MP usava Demonware; o lado SP/campanha **não tem código de rede algum**, portanto o modo cooperativo precisa ser criado do zero. O sistema de salvamento é local.
- **32 bits versus 64 bits:** open-iw5 (e todos os clientes comunitários funcionais) precisa do motor de *32 bits*. A atualização Steam de outubro de 2026 substituiu os binários do jogo e o servidor dedicado por versões de 64 bits (o depósito do servidor agora é um esqueleto x64 de 117 KB); o conteúdo de 32 bits precisa ser obtido dos manifestos de depósitos anteriores a 2026.

## <a id="what-we-changed"></a>O que alteramos

- Criamos uma **cópia de teste de 32 bits isolada** a partir de manifestos Steam anteriores a 2026 (42682 recursos, 42681 binários SP, 42688 localização russa, 42751 servidor dedicado). A instalação real nunca foi alterada.
- Escrevemos ferramentas próprias de fastfiles compatíveis com 32 bits (sem extrator de terceiros): analisador de zonas que detecta automaticamente o tamanho dos ponteiros, inventário de strings/indicadores de scripts, extração de zlib aninhado e extração de ScriptFile (`.gscbin`).
- Recuperamos o **servidor dedicado real anterior a 2026** (`iw5mp_server.exe`, 4.077.480 B, PE32 i386), cujo SHA-256 corresponde exatamente à base esperada por open-iw5, e fizemos fork/recompilação de open-iw5: **a compilação funciona e o cliente SP executa uma missão da campanha.** O carregador aplica `iw5sp.exe.diff` à base do servidor dedicado na memória, e a entrada do motor chega à janela e à inicialização do sistema de arquivos. Iniciado diretamente em uma fase (`open-iw5.exe -singleplayer +map sp_intro`), o cliente carrega e executa a missão, com HUD ao vivo e legendas de diálogo lidas por OCR. Um único erro de execução de script `setsaveddvar` é registrado na inicialização e **não é fatal**; ele não interrompe o jogo. Detalhes e correções de compilação estão em `NOTES.md`.

## <a id="qa"></a>QA

- Campanha cooperativa: **none** - nenhum teste cooperativo foi executado.
- O cliente SP open-iw5 foi observado executando uma missão real da campanha (título da janela, cerca de 1,8 GB de memória residente, legendas ao vivo lidas com Windows OCR, capturas de tela). Observação manual, ainda não um teste automatizado.

## <a id="how-to-play"></a>Como jogar

- **Campanha cooperativa: indisponível.**
- **Spec Ops / Survival cooperativo hoje:** AlterWare IW5-Mod, com ambos os jogadores possuindo uma cópia no Steam (https://forum.alterware.dev/t/iw5-mod-install-guide/462).

## <a id="known-issues"></a>Problemas conhecidos

- O GSC da campanha pressupõe exatamente um jogador; não foi comprovado se uma segunda entidade de jogador pode existir no motor SP.
- O repositório upstream de open-iw5 foi excluído (GitHub 404), os 11 submódulos estavam vazios em nossa cópia e ele precisa de uma branch `xlabs` excluída de gsc-tool; o fork está sendo reconstruído manualmente.
- Um erro de execução de script `setsaveddvar` é registrado uma vez na inicialização. **Não é fatal** (a missão continua funcionando); o chamador (qual script define qual dvar antes de existirem as dvars) ainda não foi identificado.
- Iniciar apenas com `-singleplayer` (sem solicitar uma fase) não chega de forma confiável à interface principal interna; é preciso informar explicitamente uma fase para entrar no jogo.
- AlterWare informa que uma atualização Steam de outubro de 2026 quebrou a compatibilidade; existe uma ferramenta comunitária para retornar à versão anterior. Nossa cópia de 32 bits é anterior a isso.

## <a id="next-steps"></a>Próximos passos

- Chegar a uma missão pela interface interna do jogo (iniciar apenas com `-singleplayer` ainda não mostra o menu de forma confiável) e identificar o chamador de `setsaveddvar` para explicar ou silenciar o erro de inicialização.
- Criar a camada de replicação com autoridade do host (jogadores, entidades, indicadores da história) - Etapa 4 em diante.
- Usar o ScriptFile `.gscbin` extraído e os dumps GSC da campanha para mapear quais scripts definem quais indicadores.
- Propor uma linha da família de motores Call of Duty (IW) em `playbook/engine-families.md`.
- Notas brutas das sessões (todas, incluindo manifestos de depósitos e detalhes das ferramentas): `NOTES.md`.
