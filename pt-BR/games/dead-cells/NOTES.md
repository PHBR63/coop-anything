# <a id="dead-cells--co-op-notes"></a>Dead Cells - notas de modo cooperativo

Objetivo do usuário: cooperação local no sofá, um PC, dois controles, dois heróis reais; equivalência de saque por jogador (frascos, mutações, armas iniciais, repetir cada escolha exclusiva para P2). Preferência por mod Steam Workshop.

## <a id="observations-sourced"></a>Observações (com fontes)
- Ausente de DIRECTORY.md e games/ de coop-anything (2026-10-23).
- Motor: Haxe/HashLink, jogo v35 (linha Boot.logClientInfos).
- Ferramentas oficiais (ModTools/ModsDoc.pdf): pacotes de dados (CDB, salas) e scripts .hx só para estrutura de fases/listas de inimigos. Não permitem segundo jogador.
- DCCM (github.com/dead-cells-core-modding/core, MIT): mods C# em .NET 10 com hooks HashLink (Hook_<Class>.<method> += ...), eventos (IOnHeroUpdate), serialização Hxbit, comando de envio ao Workshop em mdk/DCCMTool. Último commit de desenvolvimento 2026-10-20, versão 35.14.1.
- Itens Workshop DCCM 3633185550 e DeadCellsMultiplayerMod 3657857836: ambos mostram remoção por violar Steam Community & Content Guidelines (2026-10-23). Motivo desconhecido.
- DeadCellsMultiplayerMod (github.com/vaiserYT/DeadCellsMultiplayerMod, MIT, 584 commits, último 2026-10-19): host/cliente ON-LINE (TCP 1234 ou Steam P2P). Jogador remoto é fantasma (GhostKing : entidade KingSkin), não Hero real. Sem local/tela dividida.
- Hero tem campo `controller` do tipo ControllerAccess (biblioteca Controller de deepnight), candidato para vincular P2 ao controle 2.

## <a id="derived"></a>Deduções
- Caminho 2 (criar do zero) para cooperação LOCAL, reutilizando DCCM e lições do mod on-line (armadilhas de verificações null em cenas/morte/Homunculus).
- Usar rota "segundo jogador na mesma cópia" (playbook/split-screen.md, Dave the Diver): criar segundo Hero real, trocar game.hero durante vez de P2 nos sistemas, câmera compartilhada no ponto médio.

## <a id="unknowns"></a>Desconhecidos
- Se outro dc.en.Hero pode ser criado/atualizado no mesmo Level sem quebrar singletons (Game.hero, HUD, interface de inventário).
- Se Steam manterá mod de código DCCM no Workshop.

## <a id="2026-10-23--reverse-engineering-game-v35-findings-from-bytecode-via-crashlink"></a>2026-10-23 - engenharia reversa (v35, bytecode por crashlink)
- Entrada: tool.Controller lê UM GamePad quando `gc` definido, senão combina activeGamepads (padIsDown f@2444). Controles físicos viram GamePad na ordem de criação (libs.heaps.GamePad.onDevice f@2472); controlador inicial possui todos. Logo P2 = novo Controller(s2d), mode=ENABLE_PAD, gc = GamePad 2 do controlador inicial; gc inicial = controle 1.
- Hero.init (f@1935) sempre define `controller = Boot.ME.controller.createAccess("hero")`; trocar após init para P2.
- Construtor Hero (f@4902) clona game.data.inventory; cada herói tem inventário, HeroMainSkillsManager e HealBlackBoard próprios (cargas do frasco `blackboard.healings`); frascos/armas/mutações já são individuais.
- Mudança de fase: Game.activateSubLevel (f@663) e loadMainLevel (f@656) chamam hero.clean(), depois Game.initHero (f@665). Hook em clean remove P2, initHero o recoloca.
- Câmera: Viewport.update (f@2875) mira tracked.spr.x/y. Compartilhar = posicionar sprite P1 no ponto médio durante chamada.
- Mutações: PerkMaster.onActivate(by) abre `new ui.PerkSelect(by, npc)`; cada jogador ativa Guillain. TierSelect (atributo de pergaminho) aberto por Hero.applyItemPickEffect(this).
- ReplaceItem/ReplaceSingleItem/ReplaceItemWithDual não recebem herói (usam game.hero); trocar game.hero durante construtor/validação/atualização da vez P2.
- Hook_Hero.init do DCCM define Game.HeroInstance = self para QUALQUER herói; criar P2 deixa referência nele. Mod usa Game.ME.hero.
- Compilação: Ubuntu dotnet-sdk-10.0 e MDK nupkg de win-x64.zip (sem rede, sem precisar nuget.org).

## <a id="status"></a>Estado
- v0.1.0 compilado e copiado para <game dir>\coremod\mods\DeadCellsLocalCoop. QA: untested (ainda não executado no jogo).

## <a id="owner-design-backlog-decide-after-first-working-test--do-not-implement-yet"></a>Pendências de projeto do usuário (decidir após primeiro teste funcional - NÃO implementar ainda)
- Câmera v2 (ideia do usuário, 2026-10-23): centrada no ponto médio, *arrastando* esquerda/direita/cima/baixo conforme deslocamento de cada personagem (zona morta suave/antecipação), em vez de só mover com ambos na mesma borda. Motivo: limite rígido da v0.1.1 obriga ambos a encostar na borda para avançar, correndo sem visão contra inimigos/armadilhas; perigoso em biomas altos com plataformas móveis e abismos (nuvens/torres). Rever após base funcionar.
- Atual: v0.1.1 = câmera média + limite horizontal rígido + retorno vertical após 1,5 s.

## <a id="playtest-1-owner-2026-10-23-v011--qa-level-player-reports"></a>Teste humano 1 (usuário, 2026-10-23, v0.1.1) - QA: relatos de jogadores
Funcionou: P2 criado no controle 2 (P1 controle 2, P2 controle 3), movimento, câmera média (usuário gostou).
Bugs corrigidos em v0.2.0 (não testada):
- P1 congelado após menu ReplaceItem de P2: menus abrem ControllerAccess EXCLUSIVO no controlador inicial (construtor f@2477 define parent.exclusiveId); v0.1 sobrescrevia ui.controller sem liberar, mantendo exclusividade para sempre. Correção: liberar acesso original e dar acesso exclusivo P2 ao menu.
- Jogadores empurravam-se: hook Entity.canHaveRepellingWith retorna false para par de heróis.
- Cópias de equipamento trocado/descartado (log mostrou ThunderShield #720 "Equipped" copiado): itens que já estiveram em inventário são de propriedade de alguém; descartes durante coleta/menus P2 nunca copiados. DeathMoney deixa de copiar (consumíveis permitidos: pergaminhos *Tier, QuarterUp, Food/Meat).
- Tubos iniciais (en.inter.Random*Spawner, desbloqueios RandomBow/RandomShield/RandomCC/Recycling): usuário quer configuração própria para cada jogador. Cada tubo agora sorteia item separado para P2 (spawnItem chamado de novo), reservado por jogador, lado a lado.
- HUD P2: segunda ui.HUD criada/atualizada no contexto P2 (game.hero, game.hud, HUD.ME apontam a P2), leftFlow espelhado no canto inferior direito; minimapa P1 oculto, dinheiro/células/abates no alto à direita.
Cosmético, usuário aceita deixar: P2 sem cabeça.
- Lição de implantação: reenviar mesmo caminho preparado gravou silenciosamente compilação ANTERIOR no PC (usuário executou v0.1.1 de novo). Sempre preparar cada versão em pasta nova, conferir lendo de volta (SHA-256) e linha "[LocalCoop] vX loaded". DLL v0.2.0 sha256 b155a45c...de6c6 conferida no PC.

## <a id="playtest-2-v020---v021"></a>Teste humano 2 (v0.2.0) para v0.2.1
- Congelamento P1 em menus P2: CORRIGIDO (usuário confirmou).
- Falha: Null access .isFullscreen em Hero.updateInteraction (preUpdate P2) e 5 vezes ItemDrop.minimapTracking null: v0.2.0 trocava game.hud/HUD.ME pelo HUD P2 durante atualização, mas ele não tem minimapa. v0.2.1 nunca troca game.hud; relatos herói/HUD (setHealings, updateAmmo, tiers, buffs...) durante P2 são dirigidos ao seu HUD.
- Tubos iniciais são ARMORY: en.inter.ArmoryButton.onActivate (f@23374) solta ItemDrops a até 3 células da alavanca (inArmory=false, gravidade), retrai os demais na sala (animação para cima) e desativa outras alavancas. Random*Spawner.spawnItem nunca era chamado. v0.2.1: arsenal cooperativo; cada um puxa sua alavanca; primeira só libera tubo escolhido (reservado), parceiro escolhe outro ou cópia do mesmo; alavancas desligam após ambos escolherem. Itens ainda inArmory não coletáveis.
- Contadores P1: HUD.rightFlow ocupa toda largura e alinha embaixo; verticalAlign=Top os eleva.
- Mapa = ação 9 = SELECT (Share/Create/View), Tab no teclado (Options.configController f@5790).

## <a id="playtest-3-v022---v030-verified-on-pc-sha256-dd9915df"></a>Teste humano 3 (v0.2.2) para v0.3.0 (conferida no PC, sha256 dd9915df...)
Causas no bytecode:
- Barra de vida: Hero.updateLifeBar (f@2025) escreve ui.HUD.ME.heroLifeBar; vida P2 ia à barra P1 (mostrava dano P2, branco incorreto, som de pouca vida repetido; barra P2 presa na parte laranja de recuperação). Correção: HUD.ME = HUD responsável durante updateLifeBar e contextos P2; HUD P2 compartilha minimapa e contadores P1.
- Falha "Null access .alpha" em Hero.postUpdate (spr null): P2 atualizava após limpeza quando morte P1 desmontava fase. Proteção: ignorar pre/fixed/postUpdate P2 se spr/_level null.
- Morte P1 encerrava partida com P2 vivo: chegava a Hero.onDie sem Hero.kill. Incapacitar/reanimar também em onDie.
- Estátua de teletransporte: Teleport.onActivate chama HUD.ME.minimap.chooseTarget(..., startTeleport(by)); minimapa lê seu `controller`, então P1 escolhia. Trocar acesso para P2 ao ativar; parceiro segue saltos maiores que 8 células.
- Pergaminhos BrutalityUp/SurvivalUp/TacticUp/QuarterUp (e escolha por TierSelect) passam por Hero.applyItemPickEffect, não pickItem. Parceiro recebe igual após fechar TierSelect.
- Planta carnívora = en.ltrap.CarnivorousPlant; fixedUpdate só verifica pr.Game.ME.hero. Executar com game.hero = mais próximo.
- Duplicação: P1 descartou SeismicStomp por ReplaceItem (fora da profundidade de coleta, novo InventItem), coleta P2 o copiou. Agora propriedade por permanentId; descartes durante qualquer menu replace/dropAndUpdateItem nunca copiados.

## <a id="playtest-4-v030---v031"></a>Teste humano 4 (v0.3.0) para v0.3.1
- Ambos os bugs eram regressão minha: v0.3.0 apontou HUD P2 aos contadores P1; HUD.onResize acessa aboveMapFlow.getProperties(bossCellCount).paddingRight, null (contador fora do fluxo P2), criação falha; caminho de erro destrói HUD P2 e HUD.onDispose (f@5346) define this.minimap.destroyed = true; minimapa compartilhado P1 morre, construtor LevelTransition (ZDoor, porta quebrada do Giant) falha em getTile null.
- Correção: só compartilhar minimapa; sempre zerar hud2.minimap antes de destruir hud2; restaurar HUD.ME se liberação o limpou.
- Processo: build.sh ocultou compilação falha e DLL antiga foi preparada uma vez; agora falha em erros de compilação.

## <a id="playtest-5-v031---v032"></a>Teste humano 5 (v0.3.1) para v0.3.2
- Falha ao sair de PrisonStart: HUD P2 compartilhava MiniMap P1; Game.activateSubLevel chama HUD.initHero, reconstrói mapa; onResize P2 também executava minimap.onResize (reatribuía get_pixelScale), causando MiniMap.initUI reflow null .x e falha HUD P1. Lição: nunca compartilhar subobjetos HUD entre instâncias.
- v0.3.2: nada compartilhado no HUD P2; sem troca global HUD.ME (só em Hero.updateLifeBar); exceções no HUD P2 capturadas e registradas uma vez em vez de derrubar (cosmético).

## <a id="playtest-6-v032-first-session-with-no-crash---v040-verified-on-pc-sha256-f04cc7aa"></a>Teste humano 6 (v0.3.2, primeira sessão sem falhas) para v0.4.0 (conferida no PC, sha256 f04cc7aa...)
- Ícones de recarga piscando e som "ready" repetindo no HUD P1: BeheadedActiveSkillsManager.fixedUpdate (f@23217) obtém ícones por HeroActiveSkillsManager.hudGetSkillPower e ui.HUD.ME.skillPowers; gerenciador P2 gravava seus tempos nos ícones P1 por quadro. Busca no bytecode (gamecode/hudscan.py) por funções tool/hero, en/Hero, mainSkills, weapon que leem global HUD (g@426): 39. Todas individuais agora usam HUD.ME do responsável (HudRouting.cs); compartilhadas (dinheiro, células, mapa, morte) continuam no HUD P1.
- Pergaminho dado duas vezes: propriedade P1 era game.hero, P2 durante sua vez; Partner(P2) retornava P2. Agora P1 é referência guardada; applyItemPickEffect resultante de TierSelect (SurvivalUp de AnyUp) não é compartilhado de novo.
- P1 bloqueado após teleporte P2: MiniMap.fullscreen (f@3314) torna minimap.controller exclusivo em P1; MiniMap.restore libera acesso que mapa contém. Agora libera P1 ao entregar a P2, concede exclusividade P2 e libera ao fechar.
- Em aberto: P2 flutuou após salto duplo até golpear para baixo (usuário: temporário). Causa desconhecida, precisa de reprodução.

## <a id="playtest-7-v040-first-full-biome--prison-depths---v050-verified-on-pc-sha256-be83ca47"></a>Teste humano 7 (v0.4.0, primeiro bioma completo + Prison Depths) para v0.5.0 (conferida no PC, sha256 be83ca47...)
- Mapa não revelado: neblina pintada ao desenhar minimapa (MapMask.drawRec f@3522 para MapFow.drawRec f@3430; círculo em MiniMap.postUpdate). v0.4.0 ocultava minimapCont; nada revelava. Agora desenhado fora da tela (x = -100000), restaurado quando mapa inteiro abre ou ShowMinimap=true.
- Atributo survival P2 ausente no HUD: algumas escritas após sua vez. Valores corrigidos a cada quadro pelos atributos reais (Entity.survivalTier/brutalityTier/tacticTier contra HUD.tierBar.*.value).
- Indicações presas no teclado após Esc: Controller.updateMainMode (f@2447) deveria voltar ao pressionar controle; P1 fixado a um controle não voltava. Alternativa: atividade em seu controle (GamePad.lastActivity) restaura indicações de controle.
- Salto na planta: CarnivorousPlant.onTouch (f@26845) ignora não inimigo diferente de game.hero; toques P2 agora no contexto P2. fixedUpdate prefere quem está em cima ao mais próximo.
- Forja menor mostrava itens P1: SmallBlacksmith.openUI (f@14941) cria ui.ForgeUnderground() de game.hero. onActivate do ferreiro no contexto de quem ativa; ForgeUnderground/ForgeLegendary recebem controle P2 como demais menus.
- HUD sobreposto após bioma 1: disposição reaplicada por quadro, alinhamento P1 acompanhado por instância, HUD P2 reconstruído se jogo o destrói.
- Fonte só uma vez: Fountain.onActivate (f@13844) verifica game.hero e define `used`. Agora um uso por jogador (indicadores P1/P2 por fonte), contexto do ativador. Frasco único em dificuldades altas é ItemDrop "FlaskRefill" do construtor (genData.flaskRefill): agora saque individual, cópia para parceiro.
- Bloqueio por porta (Prison Depths): TriggeredDoor.onDistantTrigger (f@21492) fecha quando placa/gatilho dispara novamente. Se separar jogadores, outro é trazido ao lado de quem fechou. Porta da sala de mutação (PerkMaster.setDoor f@26126, aberta com getAvailablePerks()==0 para game.hero) espera ambos. Escape novo: P2 segura Back/Select 1,5 s e P1 vem até ele.
- Não reproduzida: porta exata do bug 8 (sem captura preservada); se não for TriggeredDoor, usar reagrupamento.

## <a id="playtest-8-v050---v060-built-sha256-66f88974-deploy-waits-for-the-game-to-be-closed"></a>Teste humano 8 (v0.5.0) para v0.6.0 (compilada, sha256 66f88974...; implantação espera jogo fechar)
- Fonte por jogador e forja como P2: funcionamento confirmado no log.
- Indicações presas no teclado de novo: causa descoberta. Enums Haxe sem argumentos são singletons comparados por ponteiro (Controller.updateMainMode f@2447 contra g@15232/g@15009; ControlIcon.setAction f@4401 lê Boot.ME.controller.mainMode). `new MainMode.MM_*()` em C# cria terceiro valor diferente dos dois: ícones presos e troca nativa morta. ==/!= C# de HaxeEnum compara índice, ocultando problema. Singletons reais capturados do jogo (updateMainMode no modo só teclado; onAnyPadEnabled em lista vazia) no controle P2.
- Minimapa: minimapCont é filho do fluxo rightFlowR (reposiciona filhos, desfazendo escritas x). Agora FlowProperties.isAbsolute + globalToLocal para canto superior esquerdo. Visibilidade controlada pelo jogo (barras de chefe ocultam).
- Pausa P2: Game.update abre ui.pause.DefaultPause só na ação 8 de game.controller. Start P2 (índice GamePad 5) agora abre no seu contexto e controle (padrão dos demais menus).
- Fantasmas da foice: função de criação (f@36200, tool/weap/AdeleScythe.hx) passa game.hero como pai. Hook do construtor troca por P2 se foice está no inventário P2.
- Diverse Deck: pow.DiverseDeckBase.doActive lê owner._level.game.hero (transformInventoryItem em P1). doActive de variantes e Base.fixedUpdate no contexto do responsável pelo poder. Atualização própria P2 usa game.hero = P1 (AsP2Acting swapHero:false); outras habilidades que leem game.hero podem ter igual bug.
- Abates dobrados: Mob.notifyHeroOfDeath (f@1062) chama onMobDeath e addKillCount em todo herói vivo. Agora uma contagem por inimigo (mesmo herói ainda pode somar duas vezes, como Scissor).
- Venda: ItemDrop.recycle (f@10054) destrói item; agora deixa cópia equivalente ao parceiro como na coleta.
- Altares de recompensa (usuário sugeriu sala por jogador): cada um escolhe. ItemAltar.disable(picked) (f@16519) desativa todos na mesma sala/linha; primeira escolha os mantém ativos só para parceiro (além da cópia da primeira). Escolha dele (altar ou cópia) fecha grupo.
- Barras: HUD.updateLifeSize (f@5325) amplia 217..350px conforme vida máxima; se cruzaria centro, nova chamada com overrideMaxLife=1.0 (menor barra).
- Porta após baú amaldiçoado ainda fechada (imagem: laranja gradeada junto ao baú). Usuário pediu botão: L3 (índice 10, "analogClick"): L3 P1 traz P2, L3 P2 traz P1. Substitui segurar Select P2.
- Índices GamePad: A0 B1 X2 Y3 Back4 Start5 LT6 RT7 LB8 RB9 L3 10 R3 11 Dpad12-15 (inicialização MAPPING).
- Ferramenta: gamecode/dumpall.py grava gamecode/alldis.txt (todas funções, alvos de chamadas nomeados); pesquisar nele em vez de descompilar função a função.

## <a id="playtest-9-v060-first-full-run-start-to-bank-fully-playable-with-minor-issues---v070-verified-on-pc-sha256-dbd3c5f8"></a>Teste humano 9 (v0.6.0, primeira partida completa até Bank: totalmente jogável com problemas menores) para v0.7.0 (conferida no PC, sha256 dbd3c5f8...)
- Confirmados: reagrupamento L3 (constante), altares individuais, fonte, forja, pausa P2, indicações (sem reclamação).
- Cópias infinitas ao recusar loja e ocasional terceira cópia: cópia do parceiro criada logo após Hero.pickItem retornar, mas coleta ainda indecisa (ReplaceItem, confirmação) podia ser recusada. Agora aguarda conclusão real (origem destruída, item movido, altar desativado ou item no inventário); recusa (sem menu, item no lugar) não copia e remove marca de propriedade. Cabines (ShopBooth.buy adiado, fora de onActivate) nunca copiam.
- Arena: cine.EnterRoomBoss e similares chamam BossDoor.closeAndLock (f@8875) quando P1 (game.hero) entra; parceiro trazido se porta separar.
- Cartões Bank: LockedDoorButton.hasKey (f@25290) conta só inventário game.hero. Leitor agora no contexto de quem tem chave (canBeActivated/onActivate/onFocus).
- Diverse Deck Watcher: carga em game.data.gameFlags[DiverseDeckWatcher.gameDataChargekeyName], compartilhada. Métodos Watcher P2 com nome estático trocado para "<name>_coopP2".
- Ainda aberto: P2 flutuando após salto duplo (aleatório, sem gatilho).

## <a id="v071-owner-request-no-playtest-yet-verified-on-pc-sha256-96fa6304"></a>v0.7.1 (pedido do usuário, ainda sem teste humano; conferida no PC, sha256 96fa6304...)
- Pedido de encontrar outros locais como cartão Bank: busca de bytecode (gamecode/invscan.py, funções X.hero.inventory.hasItem/countItemKind/removeOne) encontrou chaves só de game.hero em LockedDoorButton (portas/cartões), BankSubTeleporter.get_heroHasCard, CemeteryGraveCave.hasKey/consumeKey, HiddenTrigger.trigger (zonas, incluindo chefes), Merchant.talk, EliteShrine, BreakableGroundConditional, RedTeleporter, VineLadder, HomonFountain, TopLighthouseGetAway, Mob.onDie/checkForExecute (efeitos de itens, não chaves).
- Correção: chaveiro compartilhado. Inventory.countItemKind/hasItem/removeOne de jogador também veem CHAVES do parceiro (identificadores *Key, *Key<n>, *Keycard, ALKey*; não runas Meta*, Richter*, aparências). Usar chave ausente no jogador consultado consome a do parceiro.
- Portas de chefes: âncora agora é quem pisou no HiddenTrigger que iniciou a cena (P1 ou P2).
- Não encontrado: item "rose key"; identificadores Rose são salas (RoseKeyConverter*), cobertos se chaves seguem padrão *Key.

## <a id="v080-owner-requests-verified-on-pc-sha256-fa4e226c-not-playtested"></a>v0.8.0 (pedidos do usuário; conferida no PC, sha256 fa4e226c...; sem teste humano)
- Escolher controle P1: ordenados por hxd.Pad.index (estável por físico; "preto" sempre P1). Configuração salva SwapPads inverte. No jogo, segurar Back+Start por 1 s num controle o torna P1 (vibração e textos "PLAYER 1"/"PLAYER 2"); F10 troca pelo teclado. Nomes registrados no log.
- Simulação da sala de roupas/cabeças pelo bytecode: roupa = User.heroSkin, cabeça = User.heroHeadSkin, UM valor no perfil; todos desenhados dele (Hero.getSkinInfo para User.getHeroSkinInfos; HeroHead.init/initHead leem heroHeadSkin). Skinner/SkinSelector e TailorDaughter/HeadSelector abrem com controle P1 e aplicam a game.hero (SkinSelector.close chama game.hero.applySkin, que escreve perfil). Antes de v0.8.0, P2 no guarda-roupa abriria menu P1 e mudaria roupa P1; adotaria a mesma roupa na próxima porta (P2.initGfx relê perfil). Cabeças iguais; P2 de qualquer modo sem cabeça visível.
- Agora: ativação P2 abre menu no controle e contexto P2; escolha salva como P2Skin/P2Head na configuração, perfil restaurado à escolha P1; P2 desenhado com valores próprios (getSkinInfo/getGlowColorsData/HeroHead.init com valores do perfil trocados). Câmera restaurada à visão compartilhada se menu a deixou em P2.

## <a id="published-2026-10-27"></a>Publicado (2026-10-27)
- Repositório: https://github.com/Osman-Mujic/DeadCellsLocalCoop (público, MIT), pré-lançamento v0.8.0 com DeadCellsLocalCoop-0.8.0.zip (SHA-256 a92963d2...096e6; DLL é compilação instalada no PC do usuário, fa4e226c...). PR rascunho: cranebeaker/coop-anything#237.
- Compilação: props MDK leem propriedade MSBuild DCCM_ROOT; variável de ambiente de mesmo nome quebra (todos tipos DCCM não encontrados). build.sh agora usa DCCM_DIR.
