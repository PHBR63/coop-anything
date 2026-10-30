# <a id="claim-audit--can-the-current-workflows-prove-each-line-of-the-sync-contract"></a>Auditoria das afirmações: os fluxos atuais conseguem comprovar cada linha do contrato de sincronização?

2026-10-21. As linhas seguem [06-sync-contract.md](06-sync-contract.md). Veredito por linha: **P** = existe um teste com controle negativo que falha; **W** = existe um teste, mas ele é fraco (sem controle ou verificando a coisa errada); **M** = ausente.

## <a id="what-every-current-test-shares-the-blind-spots"></a>O que todos os testes atuais compartilham (os pontos cegos)

1. **Um PC, localhost, latência zero.** Nenhum teste consegue detectar uma disputa que dependa de um parceiro lento ou atrasado. O teste real encontrou assim a disputa da semente.
2. **As duas instâncias são iniciadas pela estrutura de testes em ordem fixa e favorável**, controladas por bots, com opções de teste (`-coopprofileadopt`, `-Auto…`) que um jogador nunca define. Assim, "funciona com as opções" está comprovado; "funciona como distribuído" não está (desbloqueios do host).
3. **Os testes são escritos para o que o código faz** e depois recebem um controle negativo. Não partem de um requisito. O jogo real revelou requisitos para os quais ninguém escreveu testes (jogador caído poder se mover, botão após uma partida).
4. **Uma execução é uma fase, iniciada uma vez.** Nada exercita partida → menu → segunda partida.
5. **As verificações visuais olham apenas para a estrutura ou para um oráculo de pixels na sala.** A existência de representante, câmera e projétil "desenhado" é comprovada por contagens de objetos, não pelo que aparece na tela.

## <a id="row-by-row"></a>Linha por linha

| Contrato | Veredito | Motivo |
|---|---|---|
| A1 configuração antes do mapa | **W** | Existe teste de impressão digital, mas o host nunca atrasa; a disputa (`haveConfig=False`) não pode ocorrer. Precisa da variante com host atrasado. |
| A2 mapa e objetos da missão | **P** (censo, com controle negativo `-coopworlddiffhide`) | Mede, mas não impõe; depende de A1. |
| A3 classe/visual dos dois anões | **W** | O teste `skin` cobre apenas host→cliente; a visão da classe do cliente pelo host não é testada. |
| A4 desbloqueios do host | **W** | `profile-adopt` só passa com `-coopprofileadopt`; o caminho padrão não é testado (e está desativado). |
| B1 estado e movimento dos inimigos | **W** | Existem testes de censo/transporte; a suavidade tem `enemysmooth` para interpolação, mas não há medida de erro de posição a 10 Hz ou sob latência. |
| B2 projéteis, torretas e feixes nos dois sentidos | **W** | Réplicas host→cliente têm testes com controles; torreta cliente→host não é replicada (G3), a contagem de projéteis cresce (G4): o censo detecta, mas nenhum teste falha por isso. |
| B3 itens coletáveis, sem duplicatas | **W** | `loot` comprova as solicitações de coleta; duplicatas G5 só aparecem no censo. |
| B4 terreno | **P** | |
| B5 objetivos, término, vitória | **W** | `runend` força o resultado (`-RunEndForce`); os bots nunca chegam à vitória natural/chefe. |
| B6 barreiras | **W** | `levelup`/`shop` verificam ausência de estouro de tempo e contagem de cartas, **não o tempo de retenção** (G1). |
| C1 posição/animação | **W** | O representante existe/anima; sem medida do erro em relação ao real. |
| C2 caído, reanimação | **W/M** | Círculo e temporizador de reanimação têm controles; "jogador caído não pode se mover/atacar" e "reanimação termina com ambos presentes" não são testados. |
| C3 dano | **P** | |
| C4 XP / cartas | **P** | |
| C5 carteira / loja | **P** | |
| C6 separação da progressão permanente | **P** (teste de salvamentos) | Backup/restauração de salvamentos em um PC, verificados. |
| D1 começar juntos | **W** | Início pela sala funciona com o assistente; inversão da ordem de início e cliente atrasado não são testados. |
| D2 espera de carregamento | **P** | `loadform`, `loadtimeout`, execução com atraso. |
| D3 segunda partida após o término | **M** | Nada volta ao menu e inicia novamente. |
| D4 parceiro perdido | **P** | `disconnect`, nos dois sentidos, referência FAIL. |
| D5 reconexão | não exigida (decisão 3) | |
| D6 perfis de latência | **M** | Sem modelador de rede na estrutura de testes. |
| E marcador | **P** | `indicator`, `marker`. |
| E câmera | será substituído | O teste `camera` verifica enquadramento, retirado pela decisão 5; nova asserção: a câmera acompanha apenas o próprio anão. |

## <a id="tooling-that-is-missing-needed-to-close-the-wm-rows"></a>Ferramentas ausentes (necessárias para fechar as linhas W/M)

1. **Modelador de latência/perda** entre as duas instâncias, para executar D6, B1 e a disputa da semente. Opções no Windows: um pequeno proxy UDP próprio em 127.0.0.1 (atraso, variação de latência, perda, duplicação, interrupção), dentro do modo de teste do mod ou como script de ferramenta. Preferível: proxy próprio (sem instalar driver ou exigir administrador, reproduzível); um driver como Clumsy precisaria de autorização explícita.
2. **Variante de início tardio:** `-LoadDelayRole host` existe para carregamento; ampliá-lo para atrasar o envio de configuração da partida pelo host, reproduzindo a disputa A1 com uma referência que falha.
3. **Modo com configuração distribuída:** executar a estrutura de testes com os padrões da versão e sem opções exclusivas de teste, verificando no log as mesmas linhas de adoção/perfil que um jogador receberia.
4. **Teste de segunda partida:** terminar a partida, aguardar o menu, verificar a existência do botão CO-OP, iniciar novamente e comparar impressões digitais.
5. **Asserções da máquina de estados:** caído → entrada e posição congeladas; reanimação termina em até N s; tempo de retenção verificado em `levelup`/`shop`.
6. **Sonda de erro de posição:** comparar as posições do representante/réplica com as reais em instantes fixos (exige ambos os logs com relógio comum do jogo; o censo já alinha pelo tempo do jogo).
7. **Coluna confirmada por pessoa:** uma lista de verificação executada em dois PCs, uma linha por linha do contrato, para STATUS mostrar "automatizado" e "humano" separadamente.

## <a id="result"></a>Resultado

Apenas cerca de um terço das linhas do contrato (B4, C3–C6, D2, D4, E-marcador) pode ser comprovado hoje por um controle negativo que falha. A maioria das linhas "✅" mede a existência de um mecanismo, não o cumprimento do requisito percebido pelo jogador. Ordem recomendada: ferramentas 2 e 3 (baratas, fecham A1/A4), depois 4 e 5, depois 1 (modelador de latência); então corrigir B1 a 10 Hz e medir sob os perfis de latência.

## <a id="update-2026-10-21-after-the-overnight-run"></a>Atualização de 2026-10-21 (após a execução noturna)

O que mudou desde a auditoria acima (IDs das execuções em [../STATUS.md](../STATUS.md)):

| Contrato | Antes | Agora |
|---|---|---|
| A1 configuração antes do mapa | W | **P** `lobby-start -MapSync -ConfigDelaySec 3`, variante `-coopnomapwait` |
| A3 classe/visual nos dois sentidos | W | **P** `-Test skin`, variante `-coopskinhostonly` |
| A4 desbloqueios do host | W | **P** `lobby-start -ProfileScrub -AdoptCheck` sem `-coopprofileadopt`, variante `-coopnoadopt` |
| B1 movimento dos inimigos | W | **P** `-Test enemyerr -EnemyErr -EnemyErrP95Max 0.8`, variante `-coopsnaphz=2` |
| B6 barreiras | W | **P** `-Test barrier` (tempo de retenção, estouros de tempo), variante `-coopbarrierold` |
| C2 caído | W/M | **P** `-Test downedlock` (movimento + ativação de arma), variante `-coopdownednolock` |
| D3 segunda partida | M | **P** `-Test secondrun -MapSync -ExpectRuns 2`, variantes `-coopmenubuttonsolo`, `-coopnolobbyreset` |
| D6 latência | M | **W** Existem ferramenta e execuções (`-Lag`, `lagproxy.py`), mas não é possível uma variante que falhe para "não congela". |
| E câmera | seria substituído | **P** `-Test cameravanilla`, variante `-coopcameraon` |
| E início sem cliques visíveis | - | **W** Implementado, não pode ser verificado sem interação (`OnGUI` nunca é chamado nas execuções autônomas da sala). |

Ainda **W/M** (não comprovados por um controle que falha): B2 (torreta do cliente G3, crescimento de projéteis G4), B3 (itens duplicados G5), B5 (vitória natural), C1 (erro de posição do representante), E marcador no fluxo da sala, ESC/pausa com um parceiro e tudo o que uma pessoa precisa ver. A coluna "Mensch" de `local/MANUAL-TEST.md` está vazia de propósito.

**Novo ponto cego encontrado neste trabalho:** execuções autônomas não desenham IMGUI (contagem de `CoopTick.OnGUI` igual a 0); por isso, toda verificação dependente da sobreposição (tela de início, marcador fora da tela, avisos) só pode ser executada em uma sessão normal da área de trabalho. O antigo fluxo de abertura `-Auto` também precisa de um clique real e não funciona em um shell oculto. Use `-Ui -Lobby` para o restante.
