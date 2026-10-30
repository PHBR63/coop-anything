# <a id="balatro-working-notes-local-co-op-balatro-duo"></a>Balatro: notas de trabalho (modo cooperativo local "Balatro Duo")

Estado: 0.6.1, lançado em https://github.com/dobrodeetel/balatro-duo (fonte do mod, instalador, ferramentas de teste). Relato: README.md.

## <a id="identity"></a>Identidade
- Steam appid 2379780, depot 2379781, compilação 17459173, Windows 10 x64
- Versão 1.0.1o-FULL (de `globals.lua`)
- Balatro.exe SHA-256 `0d75fe164accf3312734d4b37ac98788dd15f0b8e4f9bb8b7f90c4e59de93f47`
- Motor: LÖVE 11 com executável fundido (executável e ZIP dos fontes Lua, abre em qualquer leitor ZIP), LuaJIT, luasteam

## <a id="goal"></a>Objetivo
Duas janelas num PC, cada uma com sua partida (baralho, dinheiro, curingas, loja). Apenas pontuação do blind compartilhada: mãos dos dois entram no mesmo total; blind vencido ao alcançar a meta. Host escolhe blinds, pulos e chefe. Multiplicador de dificuldade definido pelo host no jogo.

## <a id="approach"></a>Abordagem
- Carregador: Lovely 0.9.0 (`version.dll`, SHA-256 do ZIP `40b994a055ee75e5f2aba81e7ae06f2c17460e18cc346483089921899fadd1f7`). Sem Steamodded.
- Transporte: LuaSocket (incluído no LÖVE), TCP 127.0.0.1:22123, uma linha de texto por mensagem.
- Patches (padrões Lovely; restante por substituição dinâmica de globais no código acrescentado a `main.lua`):
  - Linha de animação da pontuação de mão em `state_events.lua`: contar pontos próprios, enviar ao parceiro.
  - Verificação de fim de `update_hand_played` em `game.lua`: ao acabar as mãos, esperar parceiro.
  - Verificações `end_round()` de baralho vazio em `game.lua`: o mesmo.
  - Menu principal `UI_definitions.lua`: botão CO-OP.
- Compartilhamento de pontos: pontos do parceiro acrescentados a `G.GAME.chips` somente sem animação de pontuação própria ativa (o destino é calculado ao enfileirar a mão; acrescentar no meio perderia os pontos).
- Meta compartilhada: host calcula `get_blind_amount(ante) * blind.mult * ante_scaling * difficulty`, envia na seleção; ambos substituem resultado de `Blind:set_blind`.
- Chefe: tela de escolha do convidado espera conhecer o chefe do host para aquele ante; novas escolhas do host seguidas com `G.FORCE_BOSS` (hook original em `get_new_boss`).
- Fim da rodada: jogador ocioso quando o total atinge meta espera (venceu, aguardando) o parceiro concluir; quem ainda anima termina antes de encerrar. Ambos sem mãos: ambos perdem.
- Segunda janela: identidade de salvamento `BalatroDuoP2`, perfil de desbloqueios copiado na primeira execução.
- Controles: `SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1` por LuaJIT FFI em SDL2.dll; controle 1 para janela 2, controle 2 para janela 1 (configurável). Janela sem foco ignora mouse.

- Configurações somente no host (dificuldade, modo de baralho, divisão de controles); menu CO-OP do convidado mostra só leitura. Baralho compartilhado: `Game:start_run` do host envia chave de baralho, aposta e ID de desafio; convidado inicia igual (Play bloqueado). Baralho próprio: cada um escolhe baralho e aposta.
- Dicas SDL por FFI: `SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS=1` e `SDL_MOUSE_FOCUS_CLICKTHROUGH=1` (sem a última, clique que dá foco à outra janela é consumido). Jogo escolhe elemento pelo último movimento de mouse; clique primeiro repete movimento até seu ponto.

- Pulos sincronizados por estado, não comando: host envia estados Small/Big (`bst`); convidado pula o que host pulou e ele ainda não. Host só seleciona quando convidado relata mesmo `blind_on_deck`. Motivo: num teste host registrou "skip Big" ao pular Small (causa desconhecida, não reproduzida por cliques); convidado aplicou "skip Big", nada aconteceu, janelas divergiram. Teste com convidado atrasando pulos 8 s (`--duo-test-lag 8`): host esperou, convidado alcançou, 39/39 verificações.

## <a id="observations"></a>Observações
- Lovely ignora `APPDATA` para mods; passe `--mod-dir` (primeira tentativa criou `%APPDATA%\Balatro\Mods\lovely\log` no perfil real).
- LÖVE respeita `APPDATA` para salvamentos, permitindo testes totalmente isolados.
- Duas instâncias rodam lado a lado com Steam aberto; `steam_appid.txt` na pasta do jogo.
- Fila sempre tem evento observador não bloqueante; ocupado deve contar somente eventos bloqueantes.
- SDL detecta DualSense como "DualSense Wireless Controller", gamepad=true.

## <a id="qa-automated-ran-2026-10-23"></a>QA (automatizado, executado em 2026-10-23)
Dois clientes bot (`--duo-bot`), host e convidado, sementes HOSTSEED/GUESTSEED, dificuldade x0.3; verificador compara os dois logs de eventos.
```
rounds=5 selects=5 skips=1 checks=37 failed=0
  r1: target=90 host 60+44=104 guest 44+60=104 won=true
  r2: target=135 host 75+96=171 guest 96+75=171 won=true
  r3: target=180 host 112+116=228 guest 116+112=228 won=true
  r4: target=360 host 304+112=416 guest 112+304=416 won=true
  r5: target=480 host 86+143=229 guest 143+86=229 won=false
  end: BOT gameover ante=2 round=5 (both)
```
Modos de baralho (mesmos bots, host solicita Blue, convidado Yellow, aposta 2), 39/39 cada: `shared` inicia ambos em `b_blue` aposta 2; `own` host `b_blue`, convidado `b_yellow`. Também executada inicialização por botão único (janela 1 inicia 2, organiza metades, copia perfil).

## <a id="040-2026-10-25-from-a-playtest-of-030"></a>0.4.0 (2026-10-25), a partir de teste de 0.3.0
Três relatos após jogar 0.3.0:
1. Após reiniciar, janelas forçadas às metades, embora configuradas sem borda, uma por monitor. Configuração de vídeo ainda dizia Borderless; exigia mudar para Windowed e voltar em cada janela.
   - Causa (vista no fonte): jogo restaura `G.SETTINGS.WINDOW` (screenmode, selected_display) de `settings.jkr` em `Game:set_render_settings`, seguido de `G.FUNCS.apply_window_changes(true)`. Segunda janela tem `settings.jkr` próprio (`BalatroDuoP2`). Depois `D.arrange` chamava `love.window.updateMode` para janela sem alterar `G.SETTINGS.WINDOW`.
   - Correção: opção host "Windows on start": `keep` (padrão) preserva Fullscreen/Borderless. Janela retorna à última posição (`duo_window.txt` por identidade, escrito a cada 2 s em cooperativo), ou à metade se não houver posição. `halves` sempre organiza. `D.arrange` agora define `G.SETTINGS.WINDOW.screenmode='Windowed'` e salva para menu corresponder. Convidado com `settings.jkr` recém-copiado sempre recebe metade.
2. Host clicou seleção de blind enquanto convidado comprava: aviso apareceu, botão nunca mais funcionou, mesmo após retorno.
   - Causa (observada): `select_blind_button` e botão de pulo são `one_press` (`UI_definitions.lua` 1476, 1559). `UIElement:click` define `disable_button = true` (`engine/ui.lua` 967); recusa do mod retornava sem limpar.
   - Correção: recusas limpam `e.disable_button`, inclusive recusas de seleção, pulo e nova escolha no convidado.
3. Pedido: níveis de mãos compartilhados e submenu de compartilhamento. Novo "What is shared...": dificuldade, baralho e aposta, níveis de mãos (`off` / `planets` padrão / `all`). Hook em `level_up_hand` (toda melhoria passa ali). `planets`: argumento de carta é Planeta ou Black Hole; `all` também Space Joker, Burnt Joker, Orbital Tag. Valores negativos (The Arm) nunca enviados. Receptor aplica com `instant=true` e mostra aviso identificado por chave.

QA 0.4.0 (bots; verificador portado para `tools/check_logs.ps1`, chamado por `tools/run_suite.ps1`):
- `run_suite.ps1 -ShopLag 6 -Planets` (convidado fica 6 s em cada loja. Bot host pressiona `select_blind_button` real enquanto ele compra e depois quando pronto. Host usa Pluto e Black Hole, convidado Neptune, por `G.FUNCS.use_card`):
```
rounds=5 selects=5 skips=1 early_clicks=4 refused=4 levels host->guest=13/13 guest->host=1/1 checks=45 failed=0
  r1: target=90 host 60+44=104 guest 44+60=104 won=true
  r2: target=135 host 110+96=206 guest 96+110=206 won=true
  r3: target=180 host 135+135=270 guest 135+135=270 won=true
  r4: target=360 host 400+123=523 guest 123+400=523 won=true
  r5: target=480 host 236+319=555 guest 319+236=555 won=true
  end: BOT quit ante=3 / BOT quit ante=3
```
  Cada segundo clique no botão real registrou `disabled=false` e selecionou.
- `run_suite.ps1 -Planets -Levels off`: `levels host->guest=0/0 guest->host=0/0 checks=42 failed=0` (perderam r5: sem níveis compartilhados, pontuam menos).

## <a id="050-2026-10-26-from-a-playtest-of-040"></a>0.5.0 (2026-10-26), a partir de teste de 0.4.0
1. Pedido: parceiro só recebe pontos depois de contarem no total próprio; sobreposição deve mudar nesse momento.
   - `evaluate_play` calcula `hand_chips*mult` e enfileira animação não bloqueante de `G.GAME.chips` após cartas (`state_events.lua` ~1044).
   - 0.5.0 mantém valor em `r.unsent`, envia `sc` por `D.flush_score` quando a animação alcança `own_target`. Esvazia antes de qualquer `st`, garantindo `sc` antes de `st`.
   - Corrida encontrada pelos bots: host venceu com própria mão e código original encerrou rodada, enquanto última mão do convidado (50) ainda contava. Total host perdeu esses pontos (505 contra 555). Sempre possível, raro quando `sc` saía ao jogar.
   - Correção: `pl` sai ao jogar. `DUO_hp_end` mantém rodada vencida aberta enquanto parceiro conta; `can_play` desativa após vitória. `round_update` encerra após `sc` e `st` do parceiro. Verificador exige totais iguais em toda rodada (antes só nas perdidas).
2. Pedido: opção de ambas as etiquetas para ambos. `D.share_tag` lê etiqueta de `tag_container` do blind pulado (como `skip_blind` original), envia chave, tipo e mão Orbital. Receptor cria `Tag(key)`, adiciona com `add_tag` e executa contexto `immediate`. Host executa `new_blind_choice` imediatamente, pois etiquetas de pacotes esperariam próximo pulo ou saída da loja.
   - Etiqueta host chega antes de seu `bst`; convidado a acrescenta antes do próprio pulo.
   - Boss Tag não copiada: mudaria chefe do receptor e quebraria sincronização.
   - Orbital Tag copiada aumenta só seu lado (`duo_from_peer`, para `levels=all` não dobrar).
   - Double Tag copia recebida como qualquer `add_tag` (comportamento original).
3. Convidado às vezes via tela vazia, sem blinds, ao sair primeiro da loja. Confirmado: tela espera chefe host do novo ante, mas host só enviava `bos` em sua tela de blinds. Próximo chefe sorteado em `reset_blinds` no recebimento de dinheiro; agora envia `bos` desde a loja. Não durante rodada/avaliação: `ease_ante` já aumentou ante, chefe ainda é anterior.
4. Mãos secretas: convidado fez Five of a Kind; só aparecia em sua lista.
   - `evaluate_play` define `hands[text].visible = true`.
   - Planet X / Ceres / Eris têm `softlock` e só entram em `get_current_pool` se `hands[hand].played > 0` (`common_events.lua` 2009).
   - 0.5.0 envia `hv` quando mão secreta aparece. Receptor define `visible`, guarda em `D.peer_known`; patch Lovely no bloqueio também aceita `DUO_hand_known(hand)`. `played` preservado, sem afetar Supernova e Obelisk.
   - `D.peer_known` só na memória (perdido ao sair e continuar, como demais estados cooperativos).

QA 0.5.0:
- `run_suite.ps1 -HostShopLag 6 -Secret -Planets` (host demora 6 s por loja; bot convidado marca Five of a Kind jogada na primeira; host confere `get_current_pool('Planet')`):
```
rounds=5 selects=5 skips=1 early_clicks=0 refused=0 levels host->guest=13/13 guest->host=1/1 checks=56 failed=0
  r5: target=480 host 236+319=555 guest 319+236=555 won=true
  flushes host/guest=9/9 tags host->guest=tag_double guest->host=tag_meteor guest blind waits= secret=Five_of_a_Kind pool=true
  end: BOT quit ante=3 / BOT quit ante=3
```
- `run_suite.ps1 -ShopLag 6 -Planets` (regressão 0.4.0, código final 0.5.0): `early_clicks=4 refused=4 checks=56 failed=0`. r5 `host 236+319=555 guest 319+236=555`: host registrou `apply r=5 +50`, depois `force_end r=5 why=peer=done` (esperou última mão).
- Submenu "What is shared..." com cinco opções cabe na tela (captura, área de trabalho 1807x822). Na loja do ante 1 para 2, convidado relatou `p=blind` aos 86,4 s; host saiu aos 93,0 s: convidado teve tela 6,5 s antes, sem BLINDWAIT. Log com `TAG peer tag_double` antes de `TAG own tag_meteor`. Todo FLUSH registrou `chips >= mine + theirs` (pontuação própria já contada).

## <a id="060-2026-10-27-from-a-playtest-of-050"></a>0.6.0 (2026-10-27), a partir de teste de 0.5.0
Relatos e o que o código informa:
1. Convidado saiu primeiro da loja e ficou em tela vazia enquanto host comprava (foto, ante 1 rodada 1).
   - Motivo desconhecido: sem logs; sobrescritos ao iniciar.
   - Observado: em 0.5.0 só recebia chefe com host na tela de blinds, loja ou início. Perda de `bos`, partida com `host_boss` vazio ou ante diferente (item 5) deixava tela vazia sem saída.
   - 0.6.0: convidado pergunta (`need`), espera até 1 s e mostra blinds com chefe próprio. Adoção abaixo substitui pelo do host ao chegar.
   - Log anterior agora preservado em `duo_log_prev.txt`.
2. Após reinício, blinds desalinhados (foto: convidado rodada 0 com Big disponível, host rodada 1 com Big vencido). Cada janela continuou salvamento de momentos distintos.
   - 0.5.0 nunca comparava posições: host esperava mesma rodada e blind; convidado esperava host.
3. Pedido: mostrar ao host qual blind convidado pressionou (selecionar/pular).
4. Pedido: conferir que acabar as mãos não bloqueie tudo. 0.5.0 definia `G.CONTROLLER.locks.duo_wait` ao esperar, bloqueando toda entrada (curingas, consumíveis, informações).
5. Falha e continuação quebrada (foto 3).
   - Ambos com Double Tag; blind pulado deu Charm Tag (Mega Arcana) aos dois. Cada lado tinha 3 Charm Tags (própria, Double, parceiro).
   - Host abriu dois pacotes ao mesmo tempo e falhou ao fechar.
   - Após reiniciar, host continuou ante 8; convidado começou ante 1, tela vazia.
   - Causa (reproduzida, `run_suite.ps1 -TestTags -OldNbc`): `D.peer_tag` executava `new_blind_choice` da etiqueta recebida enquanto loop original acabava de abrir pacote da etiqueta host. Host mostrou "Oops! Something went wrong: functions/button_callbacks.lua:2133: attempt to index field 'cards' (a nil value)" ao fechar primeiro pacote.
   - Loop original (`update_blind_select`, `skip_blind`, `end_consumeable`) para na primeira etiqueta acionada e repete ao fechar pacote.
   - Causa da continuação quebrada (código): Continue passa por `Game:start_run` como nova partida. Hook host enviava `run` (baralho, aposta); convidado iniciava nova partida.

O que 0.6.0 faz (código):
- Identidade de partida: `G.GAME.duo.id`, criada pelo host e recebida pelo convidado. `G.GAME` serializada por `save_run` (`recursive_table_cull` mantém tabelas simples); ID e divisão de pontos atual voltam com Continue. `save_run` envolvida para gravar essa captura.
- Mensagem `sy`: posição inteira da partida (em partida, ID, ante, rodada, blinds, chefe, fase, baralho/aposta/desafio), enviada ao mudar; substitui `run`, `bos`, `bst`.
- Convidado segue partida host (`guest_reconcile_run`): continua salvamento próprio se ID coincide; caso contrário, começa novo com baralho host. Host reiniciado continua seu salvamento se convidado estiver numa partida com mesmo ID, uma vez por conexão e só após menu principal estar pronto.
- Adoção da tela (convidado): se ante, rodada, blinds ou chefe diferirem dos do host (na tela de blinds dele) por 3 s (imediatamente se só chefe), adota host e reconstrói tela no lugar (mesmo UIBox de `update_blind_select`).
- `tot`: pontuação própria do parceiro na rodada após reconexão/continuação. Só aplica dentro da rodada.
- Esperar não define mais `locks.duo_wait`; apenas Play desativado.
- Etiquetas de pacotes recebidas: loop `new_blind_choice` original executa com tela ociosa (`D.run_pending_nbc`).
- "Play together" espera 2,5 s por convidado ainda ativo antes de abrir outro.
- Cliques de selecionar/pular do convidado enviados como `wish`. Host mostra "Partner wants to: SELECT/SKIP <blind>" e pulsa botão/etiqueta.

Encontrado e corrigido pelos novos testes:
- Host continuava automaticamente 2,5 s após iniciar, na tela inicial. Partida permanecia pausada (`paused=true`, bot imóvel, convidado esperando para sempre). Agora espera `G.MAIN_MENU_UI` e 1,5 s; proteção despausa por 30 s após continuar.
- `tot` aplicado enquanto convidado comprava (`facing_blind` ainda definido), carregando total à rodada seguinte: 156 + 120 = 276. Agora só em estados de rodada; `tot` também espera a rodada correta (resposta chega durante carregamento do blind), em vez de descartar.
- Convidado encerrado e reiniciado: continuação às vezes pausada sob janela de desbloqueio/descoberta (`common_events.lua` 1866 define `paused` e abre sobreposição). Pessoa fecha; bot agora fecha após 3 s.
- Host encerrado enquanto convidado jogava Big no ante 2: convidado sem mãos e desconectado perdia a rodada por `update_hand_played` original e antigo código de terminar sozinho. Agora rodada sem parceiro espera até 90 s (`DUO_hp_end`, `DUO_deck_out_ok`, fim solo em `D.update`). Parceiro atrasado ou no menu reiniciando é esperado até 120 s.
- Alinhamento antes tratava host como correto, retrocedendo convidado adiantado e prendendo host atrasado. Agora (`align_blinds`, ambos), vence quem estiver mais avançado:
  - Atrasado adota posição do outro; se outro dentro do blind, assume posição anterior e seleciona mesmo blind (JOIN). `peer_ready` aceita parceiro já no blind escolhido.
  - `sel` leva rodada alvo; obsoleta é descartada.
  - Entrar solicita pontos do parceiro (`tot`).
  - Progresso = rodada * 4 + pulos no ante; Select e Upcoming comparam iguais.
- Host continuou dentro de pacote Meteor (aberto por etiqueta do convidado na tela de blinds): fechar voltava a BLIND_SELECT com STATE_COMPLETE ativo, sem tela. `D.update` define STATE_COMPLETE=false após 2 s ("REBUILD blind screen"). Possível problema original ao continuar em pacote de etiqueta; não conferido sem mod.
- Mãos próprias desconectadas não contavam em `mine` (hook exigia `D.coop()`). Agora contam e são transferidas por `tot` ao reconectar.
- Corrida: host pressionou Play antes dos pontos do convidado vencerem; convidado encerrou vitória nos cerca de 3 s antes da mão host pontuar (host 230, convidado 202). `pl` agora sai ao pressionar Play (`play_cards_from_highlighted`).
- Janela convidada morta é reaberta pelo host após 10 s (se ele a abriu) e continua sozinha.

QA 0.6.0 (`tools/run_all.ps1`, 9 cenários, prazo 400 s cada; todos jogam até fim do ante 2, aposta 2, dificuldade x0.3):
- 1 atraso na loja + planetas 46/46
- 2 atraso host + secreta + planetas 46/46
- 3 etiquetas empilhadas (Double + Charm, a falha) 41/41; 3 pacotes cada, um por vez
- 4 pedidos + convidado lento 44/44: 6 pedidos clicados, recebidos e vistos; espera nunca bloqueou
- 5 baralhos próprios 39/39
- 6 host encerrado aos 110 s 20/20: continuou, entrou no Big do convidado, totais iguais
- 7 convidado encerrado aos 45 s: falhou na corrida Play, corrigido, reexecução abaixo
- 8 ambos encerrados aos 130 s 17/17
- 9 convidado encerrado, host reabriu 20/20

Execução final dos 9 no código distribuído como 0.6.0 (após correção Play): todos PASS (46, 46, 41, 44, 39, 20, 25, 17, 25 verificações, 0 falhas). Linha de pedido no host conferida por captura: "Partner wants to: SELECT Small Blind".

Não coberto: dois monitores, pessoa com controle, antes acima de 2, falha no meio da animação de mão, Boss Tag / cupons de nova escolha de chefe no convidado.

## <a id="061-2026-10-29-from-a-playtest-of-060"></a>0.6.1 (2026-10-29), a partir de teste de 0.6.0
Retorno: tudo funciona; dois pedidos.
1. Pedido Select pulsava no host, Skip não.
   - Causa: host buscava `tag_container` no UIBox de blind. ID inexistente ali: linha é `tag_<Small|Big>` (`create_UIBox_blind_tag`); botão de pulo não tem ID.
   - Correção: `D.find_uie` percorre árvore até nó `button == 'skip_blind'`; ele e `tag_<blind>` pulsam.
   - Teste bot: convidado pressiona botão real de Small; verificador exige um pulso por pedido e `found=2` para pulos.
2. Traduções. As 60 strings estavam em russo e inglês. Agora 15 idiomas: todos os `G.SETTINGS.language` do jogo (en-us, ru, de, fr, es_ES, es_419, it, pt_BR, pl, nl, id, ja, ko, zh_CN, zh_TW).
   - Novos idiomas em `duo_lang.lua`, acrescentado antes de `duo.lua` (patch Lovely de cópia com duas fontes). Busca código completo antes das duas primeiras letras.
   - Termos de blind, etiqueta, partida, baralho, aposta e mão seguem localização original (ex.: fr Blinde/Badges/partie, pl Przeszkadzajka/Znaczniki, it buio/Patti).
   - Todos têm todas as chaves, contagens de `%s` iguais ao inglês (verificação awk).
   - `tools/lang_test.ps1` muda idioma (`G.FUNCS.change_lang`), abre menu CO-OP e submenu, captura ambos. Os 15 carregaram sem erros. Fontes cobrem CJK, tremas e polonês. Strings longas ampliam caixa; nenhuma cortada. Francês "les deux badges pour les deux" encurtado.
   - Capturas revelaram barra cobrindo título; movê-la abaixo cobria Back. Com menu aberto fica no topo a 75%, até 2 linhas (estado e mensagem mais recente), acima da caixa.
3. Mensagens do instalador em russo se idioma de exibição Windows, formato regional ou idioma de instalação for russo; inglês no restante.
   - `install.ps1` UTF-8 com BOM: Windows PowerShell 5.1 lê scripts sem BOM como ANSI.
   - Máquina de teste: cultura de interface en-US, formato ru-RU e instalação ru-RU; só `Get-UICulture` não bastava.
   - Acrescentados README.txt em inglês e Install.cmd / Uninstall.cmd junto dos arquivos russos.

QA 0.6.1:
- Pedidos, antes de mudanças de barra/idiomas: 47/47 (6 pedidos, ambos os pulos pulsando com `found=2`).
- Capturas dos idiomas: 15/15 carregaram, menus legíveis.
- Código final: cenários 1 e 2 de `run_all.ps1` passaram (46/46 cada).
- Parou ali (nove cenários pareceram excessivos). Cenários 3-9 não reexecutados em 0.6.1. Caminhos não mudaram desde 0.6.0, onde todos passaram.

## <a id="not-covered-yet"></a>Ainda não coberto
- Etiquetas com efeitos imediatos além de Double/Meteor, cópia Orbital Tag e pacotes abrindo no host durante tela de blind com pessoa controlando.
- Posicionamento em dois monitores: máquina mostra um, só ele verificado. Testado manualmente com `tools/win_test.ps1` (perfil separado `wt`): primeira inicialização em metades; convidado movido por SetWindowPos; após reiniciar, `place restore 884x561 at 208,181`. Host mudou para Borderless no menu Video; após reiniciar, `place keep Borderless display 1`, convidado restaurado. Menu Video mostrou Windowed após organizar metades (antiga divergência eliminada). Menu CO-OP, submenu What is shared e Back renderizam.
- Níveis compartilhados com `all` (Space Joker, Burnt Joker, Orbital Tag) sem teste bot; só Planet e Black Hole testados.
- Controle na janela sem foco (exige pessoa pressionando botões).
- Nova escolha de chefe pelo host (Director's Cut / Retcon) e Boss Tag no convidado.
- Antes acima de 2, curingas que leem pontos (Mr. Bones), Hieroglyph/Petroglyph (mudança de ante).
- Sair e continuar durante partida além dos antes 1-2 dos bots (Continue em si coberto acima, 0.6.0).
- Instalação na pasta real do jogo.
