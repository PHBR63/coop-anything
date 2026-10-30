# <a id="triage-can-this-game-go-co-op-and-where-do-i-start"></a>Triagem: este jogo pode ter modo cooperativo e por onde começo?

Responda nesta ordem e registre as respostas em `games/<slug>/NOTES.md`.

1. **Qual é o jogo exato?** Título, ano, loja (Steam, GOG, disco), versão ou número da compilação, remasterização ou original. Mods cooperativos frequentemente aceitam apenas uma versão.
2. **Isso já foi feito?** Consulte [DIRECTORY.md](../DIRECTORY.md) e `games/`. Depois execute as buscas de [research.md](research.md). Projetos parcialmente concluídos são os melhores pontos de partida.
3. **Qual é o motor?** Examine a instalação: extensões dos arquivos, nomes de DLLs, informações de versão do executável. Depois consulte [engine-families.md](engine-families.md): outro jogo do mesmo motor pode já ter uma estrutura cooperativa reutilizável.
4. **Quanto código-fonte existe?**
   - Código-fonte completo ou descompilação correspondente (Ocarina of Time, Super Mario 64, Animal Crossing, KeeperFX): adicione rede diretamente ao código.
   - Scripts distribuídos com o jogo (Unreal Engine 1 e 2, Source SDK, scripts STALKER, Papyrus): é possível modificar a maior parte da lógica sem código nativo.
   - Plugin ou extensão de scripts (xNVSE, SKSE, hooks Lua): insira hooks no motor a partir de uma DLL.
   - Nada: apenas binário fechado. Espere muita engenharia reversa; procure com mais cuidado um projeto existente ao qual se juntar.
5. **O motor tem algum multiplayer?** Um modo deathmatch distribuído com o jogo (Deus Ex, STALKER, Unreal) significa que já existem replicação, servidor e cliente. O modo cooperativo passa a consistir em executar a lógica de um jogador (scripts da história, IA, gatilhos, salvamentos) nesse código de rede. Sem código de rede, será necessário construir uma camada de sincronização: lockstep para jogos determinísticos, autoridade do host com sincronização de estado para os demais.
6. **Verificação de distribuição.** Você consegue distribuir as alterações sem distribuir os arquivos do jogo? Há algum sistema antitrapaça ou serviço on-line do qual precisa manter distância?

## <a id="rough-difficulty"></a>Dificuldade aproximada

| Situação | Caminho típico |
|---|---|
| Existe um mod cooperativo abandonado | Retome-o: [reviving-abandoned-mods.md](reviving-abandoned-mods.md) |
| Existe descompilação ou port de código aberto | Adicione rede com autoridade do host ao código (modelo sm64coopdx) |
| O motor tem multiplayer e scripts disponíveis | Torne a lógica da história compatível com rede usando mods de scripts |
| Existe uma estrutura cooperativa para o mesmo motor | Faça o port da estrutura (trabalho semelhante ao Skyrim Together para outros jogos Creation Engine) |
| Jogo de console sem versão para PC | Port para PC por descompilação ou recompilação, se existir; caso contrário, modo cooperativo em emulador: [decomp-and-recomp.md](decomp-and-recomp.md), [console-emulators.md](console-emulators.md) |
| Binário fechado, sem multiplayer, sem scripts | Muito difícil. Encontre colaboradores e comece por pesquisa e um documento de projeto |
