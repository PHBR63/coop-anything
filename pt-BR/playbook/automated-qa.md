# <a id="automated-qa-prove-co-op-works-without-anyone-playing"></a>QA automatizado: comprove o modo cooperativo sem ninguém jogar

O nível de QA é o campo mais importante do diretório. "Funciona" significa que um script controlou clientes reais, verificou o estado compartilhado e registrou PASS. Esta página reúne a política e as técnicas que funcionaram em quatro motores muito diferentes.

## <a id="policy"></a>Política

- **Não peça a uma pessoa para testar jogando.** O jogo controla a si mesmo, verifica resultados e registra PASS/FAIL. Pessoas jogando são um complemento, não o plano de testes.
- **"Precisa de teste humano" é uma lacuna, não uma etapa.** Se algo ainda não pode ser automatizado, registre uma pendência nas notas ou em issue e construa a peça ausente: bot interno, segundo cliente ou serviço simulado.
- **O bot vive nos scripts ou código do próprio jogo**, não em entrada falsa de mouse ou teclado. Faz o que um jogador faria (indicadores da história, diálogos, mudanças de fase, inventário) e verifica o resultado.
- **Teste cooperação com cooperação.** Execute 2 ou mais clientes reais e compare o estado compartilhado entre eles.
- **Use logs e capturas de tela do próprio jogo**, nunca da área de trabalho. Capturar a área de trabalho grava tudo que estiver na tela do usuário.

## <a id="the-harness-shape-that-keeps-working"></a>Estrutura de testes que continua funcionando

1. **Instalações isoladas.** Copie a instalação da loja (ou use hardlinks), uma vez por vaga de teste. Nunca altere instalação, INIs ou salvamentos do usuário. Configure janela, sem introdução, sem capturar mouse; use renderização por software se duas janelas disputarem a GPU.
2. **Script inicializador** abre host e N clientes em um PC, aguarda o fim, coleta todos os logs e exibe uma linha: `RESULT: PASS` ou `RESULT: FAIL`.
3. **Bot interno** com etapas: aguardar N jogadores, realizar ação (pelo mesmo RPC da entrada de um jogador), esperar, verificar, registrar.
4. **Lista de suíte** (uma linha por teste: nome, mapa, clientes, tempo limite) e executor com resumo. Reexecute tudo após cada merge.
5. **Uma porta e uma instalação por agente paralelo**, para vários agentes testarem sem encerrar os jogos uns dos outros.

Peças prontas dessa estrutura estão em [tools/](../tools/README.md): trava de vaga e conjunto de cópias já inicializadas, cenários JSON, executor de bots com roteiros cooperativos, retransmissor de caos para latência e perda, gravador de eventos de dessincronização, fuzzer do núcleo de sincronização e verificador de animações.

### <a id="examples"></a>Exemplos

| Jogo | Motor | Como o bot funciona | Oráculo |
|---|---|---|---|
| Deus Ex (HX) | Unreal Engine 1 | Ator de teste escolhido por opção de URL (`?HXFixTest=Class`) executa etapas no servidor do jogador; ator controlador por jogador faz clientes reais executarem comandos de console, exercitando RPCs cliente-servidor | Estado do servidor após RPC, relatos dos clientes devolvidos por RPC |
| Dungeon Keeper (KeeperFX) | C personalizado, lockstep | Opção `-archontest`: bot no executável escreve pacotes de entrada como uma pessoa | Checksums por turno nos dois lados, 0 divergências e asserções de jogabilidade |
| Fallout New Vegas | Gamebryo | Plugin xNVSE serve JSON-RPC por pipe nomeado (`exec`, `waitFor`, `state`) | Capturas do mundo separadas em estado compartilhado e individual, comparadas entre clientes |
| Gothic 3 (G3 Together) | Genome | Bot compilado no mod e ativo somente com arquivo de sinalização; lê comandos numerados de arquivo e chama scripts do jogo (gerenciador de missões, avaliação de golpes, tarefas de IA, salvar). Menus por foco e Enter enviado à própria janela. Dois clientes reais por par de teste, dois pares para dois agentes. | Estado lido nos dois clientes (missões, listas de NPCs, vida, inventários, movimentos), monitores de invariantes ao final das suítes, hashes dos salvamentos reais antes e depois |
| Graveyard Keeper (Back From The Grave) | Unity 2020.3 (Mono) | Plugin BepInEx só de teste, inerte sem `-coopqa`, simula Steamworks.NET com Harmony e executa listas de etapas chamando os mesmos métodos dos botões e da barra rápida; inicializador Python abre duas cópias em um PC | Ambos registram PASS; estado trocado entre bots (posições, relógios), verificado dos dois lados; host como controle para ações do jogador |
| STALKER (xrMPE) | X-Ray | Arquivo contêiner de scripts só de teste, conectado pela lógica de um restritor de espaço | Verificações internas escritas no log do jogo |
| The Witcher 3 (adaptação Witcher Online) | REDengine 3 | Mod de scripts de teste e ASI que registra funções nativas (env, log, quit) por WitcherNativeBridge; pula vídeos, carrega salvamento e relata a cada segundo | Cada cliente compara o representante remoto com a posição da rede; todos os bots precisam registrar PASS |
| Outlast (OpenOL) | Unreal Engine 3 | Ainda sem bot. Clientes reais iniciados diretamente no mapa por URL; checkpoint carregado por script na sobreposição de depuração; terceiro parceiro programado entra na sala do retransmissor e injeta pacotes; caminha apenas quando inevitável | Proxy UDP com registro entre clientes e retransmissor decodifica todo pacote e escreve estado compartilhado (posições, vida, modo de inimigos, portas, gatilhos) em JSON; logs mostram o aplicado por cada lado |
| The Doors of Trithius | Java (JVM) | Controlador de verbos textuais em cada JVM (javaagent acompanha arquivo e confirma cada verbo com ok, no-effect, partial ou fail). Cerca de 65 scripts de verificação iniciam host e convidado reais em um PC por TCP. Agentes jogadores de IA jogam noites inteiras com teclado e mouse por retransmissor com atraso, interrupção e perda, enquanto agente observador avalia lista de critérios | Capturas autoritativas dos dois lugares, logs por jogador e host executando a mesma ação como controle solo |

## <a id="rules-learned-the-hard-way"></a>Regras aprendidas na prática

- **Confira que o teste consegue falhar (variantes de mutação).** Desative a correção e execute: precisa falhar. Vários testes "aprovados" não testavam nada até essa verificação.
- **Aprovações vazias.** Um teste que termina cedo ou modo que retorna silenciosamente a um jogador ainda exibe PASS. Confirme o modo inicial (jogadores, indicadores, mapa) e que a etapa de interesse aconteceu.
- **Falha ao sair ainda é falha.** Jogos Unreal Engine 1 mostram "Critical Error" e não descarregam o log ao falhar; ausência de erro no log não prova nada. O inicializador deve conferir se cada janela fecha quando solicitado e ler o diálogo quando não fecha (Win32 `EnumWindows` e `WM_GETTEXT` dos controles filhos).
- **Verificar cedo demais gera falha falsa.** Consulte repetidamente com tempo limite, não uma única vez.
- **Instrumentos mentem.** Contador de FPS limitado ocultou quedas reais; log de dessincronização mostrava turno 0 para todas as divergências. Corrija o instrumento antes de confiar.
- **Teleportes falham silenciosamente.** Um teste colocou jogador dentro de parede e depois "achou" um bug. Confira a pré-condição (realmente dentro do gatilho) antes do resultado.
- **Confira a responsabilidade dos objetos carregados por fluxo.** Valide a identidade da área antes de reutilizar gatilho; registros obsoletos podem sobreviver ao carregamento ([Friend or Foe](../games/spider-man-friend-or-foe/NOTES.md)).
- **Pouca memória mata execuções longas.** Rode um teste por vez em PC ocupado, em lotes curtos, e limpe os processos de jogo que iniciar.
- **Limpe.** Remova arquivos exclusivos de teste do pacote distribuído e compare os arquivos byte a byte depois. Servidores que conferem pacotes rejeitam sobras.
- **Teste o avaliador, não só o teste.** Faça a primeira verificação da suíte ser autoteste do avaliador: envie saída ruim conhecida (linha de resultado ausente, timeout, texto de falha) à função real e exija FAIL. Sem resultado é falha; tempo esgotado é TIMEOUT, não FAIL (The Doors of Trithius).
- **Meça o controle antes de culpar o mod.** Faça o host executar sozinho a mesma ação. Vários "bugs" eram regras do jogo original: jogador caído perde ouro; descanso no mapa-múndi nunca reduz cansaço (The Doors of Trithius).
- **Bots comprovam mecânicas; agentes jogando como pessoas encontram o resto.** Verificações por verbos não exercitam janela de entrada, foco, caminhos do mouse ou menus abertos por pessoa. Uma noite de IA jogando nos dois lugares com teclado e mouse achou defeitos de clique para entrar, painel de diálogo e loja ignorados por todos os testes. Mantenha o host como controle e agente observador avaliando lista escrita (The Doors of Trithius).
- **Monitores de invariantes junto das asserções.** Ao final de toda suíte de dois jogadores, compare objetos compartilhados algumas vezes, com segundos de intervalo, e relate o que persiste: simulado nas duas máquinas, morto só em uma, distante, vida diferente, espelho executando IA própria, corpo sem movimento. Primeiro apenas relate; dê aos monitores autoteste que quebra a sincronização e precisa ser detectado (Gothic 3).
- **Instabilidade causada pelo jogo é corrigida na ação, não na asserção.** Teste de golpe falhou porque o NPC defendeu. Agora tenta novamente até três vezes, como jogador; a asserção continua rígida (Gothic 3).
- **Confira o que o outro vê.** Nome de movimento definido em um corpo não significa movimento em execução; meça se está rodando. Confira também que inimigos escolhem jogadores remotos sozinhos; ataques forçados escondiam que nunca faziam isso (Gothic 3, primeira observação humana).
- **Conte permanência e limites em tempo real se o jogo acelera.** Uma varredura que pulava cenas aumentando a escala temporal media permanência por mapa em tempo de jogo; convidado recebia cerca de 80 quadros em alguns mapas e ainda passava. Cronometre cada etapa pelo relógio real e encerre cenas presas (Jedi Outcast).
- **Cliente conectado não é cliente vivo.** Convidado que falhou permanece conectado até o servidor expirar; convidado vindo do mapa anterior contava como presente ainda carregando o novo. Conte somente enquanto um valor avançado exclusivamente por ele (hora do último comando) continuar mudando (Jedi Outcast).
- **Correspondência exata de erros.** Avaliador que encerrava host por "ERROR" também detectava aviso de mapa inofensivo (`^1ERROR: ref_tag ... invalid target`) e nome de extensão GL. Remova horários e códigos de cor; compare o prefixo real de erro no início da linha, respeitando maiúsculas (Jedi Outcast).
- **Identifique positivamente os processos sob sua responsabilidade.** Encerre só processos iniciados pela execução (PID ou marcador na linha de comando). Encerrar todos pelo nome da imagem destruiu uma sessão ativa de dois jogadores (The Doors of Trithius).

- **Valide o próprio checksum.** Exclua preenchimento e histórico inativo somente com evidência do fluxo nativo; mantenha mutações para campos ativos ([Friend or Foe](../games/spider-man-friend-or-foe/NOTES.md)).
- **Respeite os limites dos dados de teste.** Injete controles antes da etapa de associação medida e termine asserções especiais no horário; mantenha invariantes gerais ativos ([Friend or Foe](../games/spider-man-friend-or-foe/NOTES.md)).

## <a id="testing-online-features-on-one-pc"></a>Testando recursos on-line em um PC

- **Segunda conta Steam:** duas não rodam no mesmo PC. Use `steam_api.dll` simulada; veja [networking-steam-spacewar.md](networking-steam-spacewar.md). Em jogos Unity Mono com Steamworks.NET, aplique patches Harmony ao invólucro gerenciado ([mesma página](networking-steam-spacewar.md#unity-mono-games-mock-steamworksnet-not-the-dll); Graveyard Keeper).
- **Condições de internet:** use emulação de pacotes do motor, se existir (Unreal Engine 1: comandos `PktLag=150`, `PktLoss=5`, `PktOrder=1`, `PktDup=1` no host e clientes), e repita a suíte com ela ativa.
- **Amigo sem o mod:** mantenha segunda instalação sem o pacote e confira se o jogo baixa do host (Unreal Engine 1 `ServerPackages`).
- **Várias cópias de jogos de instância única:** veja técnicas Nucleus Co-op em [methods.md](methods.md) (mutexes renomeados, hooks FindWindow, instalações por hardlinks).

## <a id="what-to-write-in-your-games-qa-section"></a>O que escrever na seção QA do jogo

- Nível de QA alcançado (veja [data/SCHEMA.md](../data/SCHEMA.md)).
- Comando da suíte e último resumo (quantidades de aprovações).
- **Insira proxy decodificador entre clientes e retransmissor.** Não exige mudar o mod, mostra o que cada lado enviou e recebeu (linha por mudança de estado) e oferece arquivo de estado aos bots em vez de ler a tela. Pare o bot se o arquivo ficar obsoleto (> 3 s), evitando caminhada cega após falha do proxy (Outlast, OpenOL).
- **Injete, não caminhe.** Parceiro programado que entra na sala e envia os próprios pacotes de gatilho do protocolo (varredura de `SeqEvent_Touch_0..N`) testou história em minutos sem ninguém no jogo. Associe linhas do receptor aos envios pelo horário (Outlast, OpenOL).
- **Comece no estado desejado.** Inicie clientes diretamente em mapa por linha de comando e carregue checkpoint com um comando; examine uma vez os checkpoints (posição inicial e inimigos próximos) e escolha o que já coloca ambos junto do alvo. Caminhar até ele é a etapa mais lenta e instável (Outlast, OpenOL).
- **Force a gravação imediata dos logs.** Alguns motores escrevem em blocos grandes e atrasados; ler logo após a ação não encontra nada e relata ausência de efeito. Confira a opção de descarga do log (Unreal Engine 3: `-FORCELOGFLUSH`) antes de confiar em log vazio (Outlast, OpenOL).
- **Bot caminhante precisa de regra de progresso, não de movimento.** Mover menos que N não detecta quicar entre obstáculos. Acompanhe a melhor distância ao alvo; sem melhora por duas rajadas é travamento: amplie desvios e desista com mensagem. Pare diante de dano ou movimento especial, não trate agarrão como parede (Outlast, OpenOL).
- **Sem captura da área de trabalho, mesmo na depuração própria.** Captura de tela inteira registrou janela Steam e lista de amigos. Capture só a janela do jogo ou use seu comando; não inclua imagens em commits sem verificar cada pixel (Outlast).
- **Variante também detecta bug de teste.** O primeiro teste de gatilho de parceiro distante passou também no retransmissor sem correção porque caso anterior consumira gatilho de uso único. Executar contra a versão não corrigida revelou isso. Use objetos/gatilhos repetíveis e ordene os casos para não consumirem pré-condições uns dos outros (Outlast, OpenOL).
- **Dê a cada verificação sua própria pré-condição.** Ausência de dano no outro jogador não prova nada se o inimigo nunca atacou; adicione teste que confirme o ataque (linha no log) e avalie ambos juntos (Outlast, OpenOL).
- **Procure a janela de falha do motor em toda asserção.** Cliente travado ou encerrado pode exibir diálogo Windows pertencente ao processo (`EnumWindows`, classe `#32770`, textos dos filhos); transforme em ERROR com o texto e pare, em vez de esperar os testes seguintes expirarem (Outlast, OpenOL).
- **Altere e restaure configuração em gerenciador de contexto.** Testes com outro valor INI (código de sala, opção de sincronização) usam `with IniOverride(...)`, que sempre restaura; compare com backup ao final (Outlast, OpenOL).
- **Informe SKIP, não PASS, se o caso nunca ocorreu.** Se depende de evento incerto (outro jogador morrer primeiro), exiba `SKIP` e motivo, sem reprovar a execução; passar silenciosamente esconderia a lacuna (Outlast, OpenOL).
- **A sobreposição de depuração do mod pode ser canal de controle.** Uma sobreposição Dear ImGui com checkpoints, criação de atores e botão de retransmissor permitiu controlar por poucas teclas e cliques em posições fixas da janela, evitando caminhada e menus; concentre as suposições de layout e confira após atualizar o mod (Outlast, OpenOL).
- **Teste sem jogo o que um convidado tardio recebe e procure código morto.** Um retransmissor pode implementar captura completa (armazenar, enfileirar, reproduzir), mas a etapa final nunca ser chamada pelo ciclo do binário distribuído. O retransmissor independente de Outlast não enviava coletas e estados de cenas e heróis de outros jogadores a entradas tardias, pois o ciclo CLI pulava a drenagem da fila; o jogo escondia o problema pedindo portas e inimigos. Um parceiro simulado envia estado; outro entra depois e lista o recebido, revelando em minutos. Compilação de depuração com duas linhas de log na fila e drenagem mostrou a etapa ausente. Adicione variante de espelho cego para comprovar que a verificação falha.
