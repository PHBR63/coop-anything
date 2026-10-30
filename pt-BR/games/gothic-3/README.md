# <a id="gothic-3-2006"></a>Gothic 3 (2006)

| | |
|---|---|
| Motor | Genome; consulte o [Gothic 3 SDK](https://github.com/georgeto/gothic3sdk) não oficial |
| Versões testadas | Compilação Steam 1037023, `Gothic3.exe` 1.75.20108.14 (Community Patch 1.75.14), x86, com Parallel Universe Patch 1.1.1 |
| Projetos | [G3 Together](https://github.com/GGM1k3y23/g3-together) (mod próprio criado do zero sobre o SDK, GPL-3.0-or-later; beta pública, última [v0.6.0-beta](https://github.com/GGM1k3y23/g3-together/releases/tag/v0.6.0-beta) de 2026-10-26). Projetos anteriores: [OTHER-PROJECTS.md](OTHER-PROJECTS.md) |
| Nível de QA | automated (suítes com bots e dois clientes reais em um PC; cada etapa com 3 aprovações e controle negativo que falha), mais uma noite cooperativa com pessoas |
| Última atualização | 2026-10-26 |

## <a id="where-things-stand"></a>Situação atual

G3 Together torna toda a campanha de Gothic 3 jogável para dois. É uma beta pública ([versões](https://github.com/GGM1k3y23/g3-together/releases), última v0.6.0-beta de 2026-10-26), com configuração em um clique em inglês, alemão e polonês. Conexão por IP direto ou LAN virtual como Hamachi. Jogadores veem um ao outro na tela, mapa e bússola, enfrentam os mesmos inimigos, compartilham missões, diálogos e ações da história, cidades libertadas, itens, reputação nas cidades, relógio e salvamentos do host, negociam entre si e reanimam o parceiro incapacitado. Todo recurso tem cobertura por bots que controlam dois clientes reais; na 0.6.0 foram 187 execuções, e os bots jogaram a história principal até o final de Innos. Pessoas jogaram juntas por uma noite. Ainda faltam partidas humanas dos finais de Adanos e Beliar e sessões com mais de dois jogadores.

## <a id="existing-work"></a>Trabalhos existentes

- **G3 Together** (este projeto, desde 2026-10-17): DLL nativa de scripts sobre o Gothic 3 SDK, com [ENet](https://github.com/lsalzman/enet) 1.3.18 (MIT) para IP direto. Host e clientes, responsabilidade regional por NPCs, registro mantido pelo host de história, itens e salvamento da campanha. GPL-3.0-or-later. Código: [GGM1k3y23/g3-together](https://github.com/GGM1k3y23/g3-together) (versões públicas desde 2026-10-22, beta desde 2026-10-25, última v0.6.0-beta). Detalhes abaixo e em [NOTES.md](NOTES.md).
- Projetos anteriores: Myrtana Accord (testado: só estado de missões compartilhado; jogadores não se veem, sem sincronização de NPCs ou combate, reconexão recusada), Gothic 3 Heroes e Gothic 3 Multiplayer de Sative (sem download para testar). Nenhum forneceu história cooperativa utilizável; G3 Together começou do zero para não repetir suas limitações, sem código ou arquivos deles. Detalhes: [OTHER-PROJECTS.md](OTHER-PROJECTS.md).

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

Observado nas cópias de teste, salvo indicação de "análise estática" (leitura de Ghidra ou SDK, sem confirmação em execução). Endereços e código descompilado permanecem privados.

**Carregamento de código e execução de duas cópias**

- Plugins de scripts são DLLs nativas em `scripts/`, carregadas pela exportação `ScriptInit`. O carregador desta compilação exige o nome decorado `_ScriptInit@0`.
- Subclasse de `eCEngineComponentBase` registrada por `eCModuleAdmin::RegisterModule` recebe `Process()` cerca de 100 vezes por segundo no mundo da campanha, além de `WorldActivate`, `WorldDeactivate` e `PreShutdown`. Não exige alterar vtable.
- A lógica passa por scripts nomeados no administrador. Um mod pode trocar seu ponteiro de função (`gSScript::m_funcScript`) e chamar o original. Estados e funções de IA (441 nesta compilação) aceitam invólucros pelos mapas de nomes de `gCScriptAdminExt`. Alguns scripts também são chamados diretamente (`GetAttitude` tem 29 chamadores diretos; `GiveXP` é chamado diretamente pelo script de morte); trocar só o ponteiro não alcança essas chamadas.
- `Gothic3.exe` encerra com código 0 enquanto existir o mutex nomeado `GenomeMutex`. Segunda cópia inicia quando a primeira fecha seu próprio handle.
- Introdução de jogo novo `G3_Intro.bik` (214 s) bloqueia o loop da sessão; nenhum callback por quadro executa. Começa apenas com mundo ativo; um Escape enviado à janela a pula.
- Menus leem a fila de mensagens da janela; teclas de jogo vêm de `DINPUT8.dll`. Teclas enviadas à janela funcionam em menus, não durante a partida.
- Salvamentos, opções e logs usam `SHGetFolderPathA` de seis DLLs do motor e patches. Redirecionar essa importação por cópia dá perfil próprio a cada teste.

**Quem simula o quê**

- Motor só processa entidades numa esfera ao redor da câmera ativa (`[Engine.Setup] Entity.ROI` em `ge3.ini`, 4000 = 40 m nesta instalação; cerca de 45 m medidos). `Entity::GetNPCs()` só lista essas entidades. As mais distantes existem e são localizáveis por GUID, mas ficam congeladas: sem tarefa, e uma morte escrita nelas não persiste. Quando voltam a ser processadas, o motor as posiciona pela rotina. Portanto, um único host não simula o mundo quando os jogadores se separam.
- Entidades dos dados do mundo têm o mesmo GUID em todas as cópias. Criadas em execução (invocações, flechas, itens deixados) recebem identificadores aleatórios e precisam de identificadores de rede.

**Dano, morte e experiência**

- Dano por contato de armas, loop de combate da IA e `gCEntity::DoDamage` terminam em `AddHitPoints`. Numa sonda de ataque de 45 s, 225 de 236 chamadas eram contato de arma; a entrada trocada de `DoLogicalDamage` nunca foi chamada. Envolver `AddHitPoints` (valores negativos) permite decidir golpes de armas e magia, mas não cobre todo dano ou morte (análise estática): `OnTick` aplica veneno e queimadura chamando `AddHitPoints` diretamente, fora da tabela; `AssessHit` pode agendar morte antes de `AddHitPoints`; `RagdollDead` zera a saúde por conta própria.
- Julgamento do golpe (`OnDamage` / `AssessHit`) registra dano; saúde cai depois em `AddHitPoints`. Limita o dano de qualquer atacante exceto o jogador, então só golpes do jogador chegam aos ramos de morte. Chamar `gCEntity::DoDamage` pelo mod causou exceção. Outros resultados aplicados diretamente por `Script_Game.dll` com `AddHitPoints` (aparos, vantagens) também evitam o administrador; relevância desconhecida.
- Corpo do jogador remoto precisa de colisão ligada, ou nenhuma arma o toca.
- Script `Kill` registra a morte: `OnNPCKilled` das missões, experiência por `GiveXP` (paga só com `gCNPC_PS::DefeatedByPlayer` desmarcado, depois marcado), saque e limpeza do grupo. Tarefas de morte `ZS_Dead` / `ZS_RagDollDead` o executam; comando `OnCheatKill` só define as tarefas (análise estática, compatível com execução). NPC espelhado não pode executar `Kill`: em G3 Together duplicava eventos de missão e pagava experiência por mortes de outros jogadores. Zerar saúde e definir AIMode 9 (morto) antes faz `ZS_Dead` somente deitar o corpo.
- `Entity::Kill()` destrói a entidade. Matar NPCs externamente no meio do combate derrubou o jogo várias vezes; golpe letal julgado pelo jogo não.
- Quando o herói morre, `Kill` exibe fim de jogo. Tarefa de nocaute `ZS_LieKnockDown` é a queda não letal original; seu loop cura o herói e o levanta após 5 s (análise estática, tempo observado).

**O jogador é uma entidade**

- NPCs escolhem alvos consultando `GetAttitude(self, other)` para cada NPC processado. Jogador é especial só pela identidade com `Entity::GetPlayer()`; segundo NPC `PC_Hero` é avaliado pelas tabelas de facção, e orcs nunca o atacam. Envolver `GetAttitude` nativo para julgar o corpo remoto como o herói local fez inimigos atacarem jogadores remotos. Um caso deve ficar intacto: NPC fugindo desse corpo (Panic).
- 201 de 847 scripts registrados comparam algo ao jogador (análise estática). Muitos só importam quando o próprio jogador os executa.
- Magia de transformação torna a criatura `Entity::GetPlayer()`, enquanto `gCSession::GetHero()` continua sendo o corpo humano oculto.
- `Shoot` mira no centro da câmera somente para o jogador; qualquer outro atirador lança a flecha ao alvo (análise estática).

**História, diálogos, relógio e salvamentos**

- `gCQuestManager_PS` mantém 570 missões. `RunQuest`, `SucceedQuest` e `FailQuest` alteram estado com efeitos originais (diário, experiência). `gCInfoManager_PS` mantém 4591 opções de diálogo; `InfoGiven` marca uma como contada.
- Missões de matar contam vítimas pelo nome em `gCQuest_PS::OnNPCKilled`, sem verificar autor nem impedir segunda chamada (análise estática).
- Cada linha de diálogo é comando string (69 tipos), executado por `IS_Running_ProcessInfo` na máquina do diálogo. Definir `InfoGiven` em outro lugar não repete nada (análise estática); é preciso enviar resultados, não o indicador.
- Relógio no conjunto de propriedades da entidade `World_MCP`; setters mantêm consistência. Dormir avança o tempo.
- `gCHUDFileManager::SaveGame` / `LoadGame` em Game.dll são salvar/carregar (encontrados com Ghidra, não exportados). Salvamento = `<name>.g3savcpx` e `<name>.g3savcpxdat`. Salvar com segundo `PC_Hero` impede carregar ("current world has more than one hero!"). `LoadGame` ativa mundo novo sem `WorldDeactivate` anterior. Carregar vaga inexistente trava.

**Animação**

- Vaga de movimento 0 de `eCVisualAnimation_PS` é o que o corpo exibe. Movimento iniciado por `Entity::StartPlayAni` logo é substituído pela animação ociosa da postura. Repetir ataques, aparos e desequilíbrios como golpe de combate (`sAICombatMoveInstr`), e gestos como instrução play-ani na unidade de scripts, os fez executar na outra máquina. Caminhada é controlada por movimento (`PSCharacterMovement::SetMovementMode` e objetivo), não por repetir a animação.

## <a id="what-we-changed"></a>O que alteramos

Nada nos arquivos do jogo. G3 Together é mod novo, escrito do zero.

**Arquitetura (uma DLL, `Script_G3Together.dll`, em `scripts/`)**

- Transporte: ENet por IP direto, UDP 34567, host escuta. Estado do jogador a 20 Hz. Protocolo 36 no `master` testado (commit `dff5cfa`).
- Jogadores remotos são representantes criados do modelo do herói (ou criatura, quando transformado), sem IA, com colisão, movidos pelo controlador do jogo e exibindo armas, postura e golpes do jogador.
- Todo NPC tem um responsável, a máquina que o simula: próximo ao host, o host; longe, cliente que o processou primeiro. Outras máquinas o espelham; todos os estados de IA do espelho são envolvidos para executar só tarefa ociosa. `OnTick`, callback e não estado de IA, é ignorado separadamente em espelhos e representantes (commit `2a9e983`).
- Regra única de golpes por máquina, aplicada em `AddHitPoints`: responsável pelo alvo decide; golpes de representantes/espelhos são descartados; golpe no representante de outro jogador é enviado a ele e julgado no herói real. Caminhos que evitam `AddHitPoints` precisam de proteção própria: cópias de magias de área de representante não executam dano de área (`5628884`, após cópia de Hailstorm decidir uma morte antes do filtro).
- Host mantém o registro: missões, diálogos contados, eventos de história, resultados de diálogos, reivindicações de itens, transações de baú/cadáver/comércio, contagens de mortes de missões, relógio e diário de mortes. Diário salvo junto ao salvamento como `<save>.g3t`.
- Campanha: salvamento nativo do host é a campanha. Cliente recebe por ENet (blocos de 16 KB com CRC-32), carrega e sobrepõe seu registro de herói.
- Host recusa cliente com DLLs de jogo/scripts, arquivos de regras ou opções diferentes, informando quais.
- Bot de teste está compilado no mod e só ativa com `qa-enable.txt` na cópia.

**Etapas** (tabela do mod no commit `dff5cfa`; cada uma passou 3 vezes com dois clientes e controle negativo que falha)

| Área | Etapas | O que as suítes mostram | Limites registrados na tabela |
|---|---|---|---|
| Base | 1, P | Módulo do motor, relatório do herói, encerramento limpo; igualdade de instalações na entrada | Arquivos avulsos em subpastas de `Data` e controles personalizados de dificuldade não conferidos |
| Jogadores | 2, V3, V4, T, L | Representantes andam/correm com animações do jogo, seguram armas e exibem golpes (14 a 15 de 15), mostram transformados como criatura; tecla salta para o parceiro | Combates e salvamentos transformados não conferidos; pressionamento em si não feito por bot |
| Responsabilidade por NPCs | 3a, E (E1 a E5), B, C | NPCs do host espelhados; NPCs distantes sob cliente, espelhados no host quando chega e retomados quando cliente sai; companheiros seguem recrutador, inclusive após salvar; aviso a 35 m; mortes distantes aplicadas ao chegar | Só 2 jogadores testados; diário guarda apenas mortes |
| Combate | 3b, 3c, A, A2, V1, V2, V5, H3, P3a, P1 | Alvo decide golpes; experiência só ao autor; sem fim de jogo se parceiro pode ajudar, ao custo de poção de cura; morte se ninguém ajuda; inimigos atacam remotos; lutas espelhadas repetem golpes; duelos atacam jogador certo; companheiros/invocações dão experiência ao jogador; meteoro invocado atua uma vez | Golpes do bot em 3b passam por `OnDamage`; monstros contra herói caído e roubo não conferidos; 37 a 55 % dos ataques amostrados do host vistos no cliente |
| História | 4, 4b, 4c, H, Q | Estado de missões, opções contadas e eventos compartilhados; cliente conversa com NPCs do host; resultados que alteram NPC chegam a todas as máquinas | Comandos de diálogo Attack/Spawn/inventário/grupo parcialmente; ensino e comércio em diálogo não conferidos |
| Itens | 5, 5b, 5c | Itens de chão, baús, cadáveres e comércio como transações do host; primeira reivindicação vence; retirada recusada desfeita | Bot negocia por chamadas de script, não pela tela |
| Salvamentos e tempo | D1, D2, D3, G, G2 | Remove representantes antes de salvar; registro de herói por jogador; entrada recebe campanha pela rede; relógio único; dormir avança para todos | Caminho do menu supostamente usa função com hook; diálogo real de cama não controlado por bot |

Depois disso, a tabela do mod (em `master` `d0cdb38`, 2026-10-21) também lista aprovados: P1 (meteoro invocado), P2 (flechas e virotes como cópias na outra máquina; "flecha que acerta conta uma vez"), P2f (bola de fogo) e HO (curar outro jogador). Execuções de P2/P2f em [RUNTIME-QA-G3TOGETHER.md](RUNTIME-QA-G3TOGETHER.md); em P2, flechas do bot raramente chegam ao alvo, então a verificação de ocorrência única tem 3 aprovações em 5, não consecutivas, e nenhuma para virotes. Adições posteriores em `master` (NPCs revidam cliente, portas/travas compartilhadas, magias de NPCs, criaturas invocadas, reputação) estão em [NOTES.md](NOTES.md) e no histórico, ainda fora desta tabela.

**Estrutura de testes** (no repositório do mod, `qa/`)

- `qa/together.py --suite <name> [--negative-control]` inicia cópias de host e cliente, envia comandos numerados ao bot interno por arquivo, lê respostas no log e exibe `RESULT: PASS` ou `FAIL`.
- Antes de cada execução confere isolamento; antes/depois calcula hash dos salvamentos reais. Encerra só processos que iniciou.
- Duas cópias completas por par, cada qual com perfil redirecionado. Um segundo par (cópias próprias, porta 34568, trava QA e pasta de execução próprias) permite a outro agente testar simultaneamente.
- Cada jogo libera seu handle `GenomeMutex` assim que o bot responde; início que encerra cedo é repetido.
- Capturas só das janelas do jogo (`PrintWindow`), nunca da área de trabalho.

## <a id="qa"></a>QA

Cada etapa tem uma suíte. Conta como concluída após 3 aprovações consecutivas, controle negativo (recurso desligado por comando QA) que falha e suítes anteriores ainda aprovadas. Toda execução exige encerramento limpo dos dois jogos e salvamentos reais intactos. Ao fim de cada suíte de dois jogadores, monitores de invariantes comparam NPCs próximos aos heróis três vezes, com 3 s de intervalo (só relatam, não reprovam).

Mais recente (2026-10-26, v0.6.0-beta, commit `ef449a3`): regressão completa de 187 execuções em três pares de PCs, 181 aprovações em 121 min. Seis falhas reavaliadas: `stageA` e `stageTreasure` passaram na repetição; `stageP2hit` (atirador raramente alcança alvo) e `stageObserveSuspect` (medição tardia) são falhas conhecidas do teste; `stageUpset` também falha na 0.5.1, e a medição `friendlydiag` passou 2 de 3 vezes.

Resultados anteriores (2026-10-19; detalhes e identificadores em [RUNTIME-QA-G3TOGETHER.md](RUNTIME-QA-G3TOGETHER.md)):

| Série | Resultado |
|---|---|
| Regressão completa com monitores de invariantes (38 suítes) | 37 de 38 passaram. `stage3c` falhou por suposição do teste, foi ajustada e passou; controle negativo falhou como exigido. Monitores: sem violação duradoura em nenhuma suíte |
| Regressão antes do pacote (9 suítes) | 8 de 9 passaram. `stage3b` falhou porque o orc aparou o golpe; teste agora tenta outra vez; repetição passou, controle negativo falhou |
| Após acrescentar rastreamento em execução (7 suítes) | 7 de 7 passaram |
| `master` incorporado `dff5cfa` | `stageP1`, `stageP3a`, `stageL` passaram; regressão completa iniciada, resultado desconhecido aqui |
| Longa duração, 2026-10-18 (compilação anterior) | 22 min, 320 ações aleatórias; depois 55 min, 738 ações incluindo 75 carregamentos: nenhuma falha de ação ou encerramento inesperado; memória estabiliza |

Execuções de 2026-10-20 (flechas P2, bola de fogo P2f, correção de giro do representante, duração de criaturas invocadas) em [RUNTIME-QA-G3TOGETHER.md](RUNTIME-QA-G3TOGETHER.md#results-2026-10-20).

## <a id="how-to-play"></a>Como jogar

Baixe o pacote nas [versões](https://github.com/GGM1k3y23/g3-together/releases) (não o ZIP de código-fonte do GitHub) e execute `Setup.cmd` (`Einrichten.cmd` em alemão, `Instalacja.cmd` em polonês) nos dois PCs. Ambos precisam da mesma versão Steam com Community Patch 1.75.14, Parallel Universe Patch 1.1.1 e mesma versão do mod (conferida ao entrar; 0.6.0 usa protocolo 56 e não conecta à 0.5.x). Host permite Gothic 3 no firewall UDP 34567; pela internet, os guias descrevem Hamachi, Tailscale, ZeroTier ou porta redirecionada. Guias em inglês, alemão e polonês estão no README do repositório. Não misture outra DLL cooperativa em `scripts/`.

## <a id="known-issues"></a>Problemas conhecidos

Lista atual: [limitações conhecidas](https://github.com/GGM1k3y23/g3-together/blob/main/docs/PLAYING.md#known-limitations) e [notas v0.6.0-beta](https://github.com/GGM1k3y23/g3-together/releases/tag/v0.6.0-beta). Ainda sem partidas humanas ou preparação pelos bots: finais de Adanos e Beliar, plano de Xardas, quinto templo, revolta de Cape Dun, libertar cidade no meio da campanha, missões de expulsão e saque, nadar para frente e controle por mouse da tela de comércio. Telecinese e magias de gelo/fogo que apagam queimadura ou congelamento só atuam nos NPCs do outro jogador no PC do conjurador.

A lista abaixo registra `master` `d0cdb38` (2026-10-21): problemas do guia e descobertas estáticas em [NOTES.md](NOTES.md); alguns já foram corrigidos. Itens estáticos são identificados: vêm de código e logs arquivados, não de reprodução em execução.

- Falhas: jogo ainda pode encerrar inesperadamente em combate ou logo após morte de inimigo. A falha conhecida no ataque dos orcs (`Entity::AttachTo`, leitura de vtable inválida) tem proteção desde `5bea542`; outras não são descartadas. Uma falha do host executou dados dentro de `Game.dll` após teletransporte do bot (vista uma vez, causa desconhecida).
- Arcos e magias: outro jogador vê cópias de flechas, virotes e bolas de fogo; bola que acerta conta uma vez. Flechas do bot frequentemente não alcançam o alvo na vila; portanto, "flecha que acerta conta uma vez" tem 3 aprovações em 5, não consecutivas, e não foi demonstrado para virotes.
- Criaturas invocadas congelam na outra máquina quando jogadores ficam além de cerca de 40 m, pois o fim da criatura só é enviado com movimento. A suíte passou mesmo assim: não reprova cópia congelada (correção planejada, veja NOTES).
- NPC controlado ou domado (Word of Control, domar) não segue confiavelmente. Estático: tomada pelo host deixa a reivindicação antiga do cliente; tomada falha deixa tarefa Follow adiada.
- Atordoamento e hipnose do cliente passam pelo host e podem não surtir efeito.
- Veneno e doença não são totalmente visíveis na outra máquina, vigor não é enviado, e experiência por morte envenenada pode faltar.
- Reputação compartilhada, mas guarda ainda pode culpar/perseguir jogador errado. Estático: reserva de diálogo pode ser sobrescrita pelo segundo jogador e liberada pelo errado.
- Estático: restaurar herói próprio acrescenta habilidades às da campanha, em vez de substituí-las; herói do cliente pode manter habilidades aprendidas pelo herói do host.
- Representante do parceiro pode atrasar brevemente sob golpes ou animar com imprecisão. Caso aberto: cliente correndo sob golpes de orcs, representante caminha 1 a 2 m atrás. Giro raro (`ZS_HangAround` após desequilíbrio) corrigido desde `a4da3aa`.
- Após entrada, inimigos ou companheiros podem agir diferente entre máquinas.
- Usar simultaneamente a mesma fogueira, assento ou posto de trabalho pode prender um jogador.
- Passos laterais de combate às vezes aparecem parados na outra máquina; posições espelhadas de NPCs desviam cerca de 60 cm (mediana), chegando a cerca de 3 m.
- Tratamento de jogador remoto pelo NPC segue o herói da máquina simuladora (crimes e fama).
- Companheiros ligados aos jogadores pelo nome após carregar; mudar nome os perde. Se host carregar outro salvamento no meio da partida, clientes precisam sair e entrar novamente.
- Corrigido em 2026-10-19 (`9acdaf5`): orcs mortos pelo host ficavam em pé no cliente (espelho recebia tarefa, mas não animação de morte). Agora 12 de 12 deitam; só orcs testados, outras espécies desconhecidas. Primeiras execuções P2 ainda tinham orcs em pé porque seu commit `ce6c5c7` é anterior à correção.
- Não conferidos: combate, salvamento e morte transformados; monstros atacando herói caído; roubá-lo; telas reais de comércio e diálogo de cama; mais de dois jogadores; internet real.

## <a id="next-steps"></a>Próximos passos

- Mais noites cooperativas humanas em LAN virtual; bugs encontrados nelas têm prioridade.
- Criaturas invocadas: enviar fim confiavelmente e fazer `stageCreatureLife` reprovar cópia congelada.
- Flechas: atirador de teste que alcance alvo, depois três `stageP2hit` aprovadas consecutivas, também com virotes.
- Identidade: guardas/crimes por jogador, reservas de diálogo, Word of Control e domesticação, restauração exata do herói.
- Conferir chamadores nativos diretos de `ContinueRoutine` e demais scripts que escapam aos invólucros da tabela; hook direto, como em `Shoot`, cobre ambos.
- Jogo pela internet, depois campanha humana mais longa, depois 1.0.
