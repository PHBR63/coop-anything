# <a id="gothic-3-preparation-notes-2026-10-16-and-2026-10-17"></a>Notas de preparação de Gothic 3 (2026-10-16 e 2026-10-17)

## <a id="observed-locally"></a>Observado localmente

- Revisão Co-op Anything: `abd32804f9bfc137162cce98a58fedb0287e1c32`.
- Revisão SDK: `90bfd344de4510dda7ac9da7461cc7f1eac911f7`.
- Instalação Steam local encontrada; metadados do executável identificam CP 1.75.14 e x86. Evidência privada da identidade em `local/identity.json`.
- Arquivos Parallel Universe presentes. A instalação não deve ser descrita como original limpa.
- `detect_engine` do upstream não retorna correspondência para esta instalação. Não tem assinatura Genome; isso não contradiz a identificação de Gothic 3 como Genome pelo SDK.
  2026-10-21: esta branch acrescenta assinatura Genome (`SharedBase.dll` mais `Engine.dll`; evidência também lista `Game.dll`, `Script.dll`, `Projects_compiled.pak`) e dica de hooks pelo SDK Gothic 3. Verificado: ambas as cópias isoladas agora retornam `Genome (Piranha Bytes)` com os quatro projetos Gothic 3 como projetos da mesma engine, inclusive pelo servidor stdio; as pastas de fontes do repositório e do mod e um layout Source sintético (`engine.dll` sem `SharedBase.dll`) não. Não verificado: outros jogos Genome (Risen, ELEX), cujo layout de arquivos é desconhecido aqui.
- Cópia isolada da instalação criada. Preparação inicial sem isolamento de salvamentos; a continuação abaixo substitui esse estado.

## <a id="searched"></a>Pesquisado

- Diretório local, registros e guia de famílias de engines para Gothic/Genome.
- Issues e PRs públicos abertos no GitHub, REST sem autenticação, primeiros 100 de cada: um resultado de cada, sem correspondências Gothic/Genome em 2026-10-16.
- Buscas web: Gothic 3 multiplayer coop mod Genome g3sdk; Gothic 3 SDK multiplayer; Gothic 3 Heroes Pigeonade GitHub multiplayer.
- Busca pública de repositórios GitHub por Gothic 3 multiplayer e Gothic 3 Heroes exato: nenhum repositório-fonte candidato retornado.
- Página do autor no Nexus e relato de teste Gothic Up; README e configuração de compilação do repositório primário do SDK.
- Não houve acesso a conta Discord, login, busca em arquivos históricos ou auditoria exaustiva de forks/branches. Pesquisa preliminar, não evidência de que nenhum outro trabalho exista.

## <a id="inference"></a>Inferência

Avaliar projetos existentes é o próximo passo. Uma implementação nova de rede é prematura até avaliar Heroes e o mod antigo.

## <a id="unknown"></a>Desconhecido

Versão/hash atual de Heroes, fonte e licença; compatibilidade da pilha completa de patches e jogabilidade com dois clientes. Testes de inicialização na continuação substituem o estado inicial sem execução.

## <a id="continuation-artifact-triage-and-profile-isolation"></a>Continuação: triagem de artefatos e isolamento de perfil

- Pull git fast-forward: já atualizado. Verificações públicas de issues/PRs abertos retornaram novamente um de cada e nenhuma correspondência Gothic/Genome. Ferramentas MCP nativas coop-anything disponíveis e usadas para triagem e identidade.
- Usuário confirma que arquivos Heroes e G3MP não estão disponíveis localmente. Download Nexus exige login; versão Heroes é vinculada pelo Discord. Nenhuma conta nem canal privado acessado. Verificações dos artefatos exatos solicitados continuam abertas.
- Buscas GitHub mais amplas sem autenticação: Gothic3Heroes (0), gothic3 multiplayer (0), G3MP (4, maioria não relacionada), Pigeonade (0), gothic3 (21), Gothic 3 exato (52). A busca ampla encontrou yevh/Gothic3 / Myrtana Accord. O resultado anterior restrito não comprovava ausência de projeto cooperativo.
- Myrtana: uma branch main e versão v0.35.0-beta.1 no commit 327c0b0a2409db1f7ba0ba9a7f09cb171c5500e0; nenhum fork retornado. Arquivo oficial de 3,15 MB baixado, SHA-256 publicado e 31 checksums internos verificados. Pacote contém PowerShell e binários nativos, mas não fonte do núcleo C++. Cinco hashes publicados da pilha correspondem à referência armazenada; três arquivos atuais agora diferem intencionalmente pelo isolamento. Instalador lido, não executado. Veja COMPATIBILITY.md e evidência privada de pesquisa.
- G3MPFHook no commit 6f059f1e877bfb9fb72e87a8f7719a7cfd992abc é ferramenta de depuração/montagem a quente sob MIT, não comprovação de implementação cooperativa. Sem versões/forks retornados; uma branch master inspecionada. Não instalado.
- Inspeção local salva encontrou Script_AnimLab.dll na referência copiada original. Foi preservada e desativada somente na cópia de teste para não alterar silenciosamente a nova referência.
- Proxy x86 local de pastas do shell implementado, sem alterações de registro nem perfil global. Seis nomes de bibliotecas importadas de engine/PUP redirecionados; backup de todos os originais. Identificadores desconhecidos de pastas são rejeitados de forma segura. Caminhos conhecidos de perfil mapeiam para dentro da instalação de teste.
- Verificações realmente executadas: compilação Release nativa; sonda independente para seis pastas de perfil mais gravação local, rejeição de pasta desconhecida e acesso a pasta do sistema; 28 hashes/tabelas de importação de binários ativos; 12 salvamentos protegidos inalterados; verificação completa de referência/sobreposição dos 235 arquivos-fonte; verificações das oito ferramentas MCP. Nenhum processo do jogo nem instalador de mod iniciado.
- Classificação do diretório legado corrigida para alpha: página do autor rotula a versão Public Alpha, e atividade pública do autor no índice do fórum em 2024 torna injustificada uma afirmação categórica de abandono. Heroes e Myrtana adicionados com níveis honestos de QA e DIRECTORY.md regenerado.
- Escopo restante: verificar caminho de salvamento no nível de API não comprova todo acesso possível em runtime. Mods/inicializadores externos adicionados exigem outra auditoria. Desenvolvimento de fonte novo ainda precisa de núcleo utilizável e licenciado; Myrtana pode ser avaliado como artefato sem afirmar que seu núcleo nativo é de código aberto.

## <a id="continuation-real-client-startup-and-bounded-sdk-diagnostics"></a>Continuação: inicialização de cliente real e diagnósticos limitados do SDK

- Verificação fast-forward do upstream permaneceu atualizada. Última consulta sem autenticação às listas abertas retornou três issues e dois PRs, sem Gothic/Genome nos títulos/corpos.
- Arquivo Myrtana fixado preparado manualmente na cópia de teste após revisão das importações; instalador nunca executado. Auxiliar QA GPL do SDK compilado separadamente acrescentado. Auditoria nativa agora cobre 32 módulos ativos. Comparação completa de referência/sobreposição ainda verifica todos os 235 arquivos originais e mudanças esperadas na cópia.
- Contradição relatada: diagnóstico do pacote cita Update Pack 1.04.x, mas instalador e manifesto de hashes não o comprovam. Nenhum pacote adicional assim foi instalado. Compatibilidade completa da pilha suportada continua desconhecida.
- Modo janela 960×720 falhou tanto na cópia base quanto na modificada; restaurar 1024×768 permitiu iniciar. O mod real carregou, informou layout nativo verificado e o cliente real entrou no servidor local. Boas-vindas de rede e estado somente menu observados.
- Exportações do auxiliar SDK local corrigidas: carregador de scripts desta versão exige `_ScriptInit@0`. Exportações decorada e alias agora existem. Compilação sozinha não detectara a incompatibilidade do carregador.
- Bot de menu valida mundo inicial/sem herói/sem permissão de salvar, consulta de pasta isolada de salvamentos e registro real de cliente no servidor. Desanexar callback antes de fechar janela de forma adiada evita a violação de acesso anterior no encerramento síncrono. Uma execução limitada posterior de menu passou. Controle negativo exigindo mundo inexistente falhou com o timeout de estado esperado e limpou seus processos.
- Experimentos de bot falhos: iniciar sessão diretamente no mundo inicial; depois reiniciar mundo de campanha mais iniciar sessão. O segundo carregou o mundo de campanha, mas a inicialização da sessão não retornou. Sequências de entrada incompletas desativadas por padrão; não comprovam bug do mod na entrada normal pelo menu.
- Hashes dos salvamentos originais permaneceram inalterados em todas as execuções completas. Nenhum teste real de salvar/carregar descartável nem jogabilidade com dois clientes passou. Criação de proxies remotos continua desligada. QA do diretório permanece none. Veja RUNTIME-QA.md; comprovantes privados e logs completos por execução permanecem em local/runtime/.

## <a id="continuation-menu-driven-campaign-entry-claude-code-session-2026-10-16"></a>Continuação: entrada na campanha pelo menu (sessão Claude Code, 2026-10-16)

### <a id="observed-from-private-run-logs-re-read-this-session"></a>Observado (de logs privados de execução, relidos nesta sessão)

- Execução 230338: `startmenu` (WM_COMMAND para "Neues Spiel", id 20571, pelo despachante GUI do jogo) seguido de `confirmnewgame` ("Ja", id 20711, na confirmação modal) chegou a `running=1 save_allowed=1 world=G3_World_01 hero=PC_Hero` com a pasta de salvamentos no perfil isolado. Nenhuma entrada do SO simulada. Myrtana registrou `world=1 gameplay=1` e os NPCs iniciais de Ardea.
- A chamada externa `startmenu` nunca registrou retorno: o novo jogo continua executando dentro do quadro de despacho do auxiliar. Ele portanto recusou todo comando posterior que não fosse somente leitura como aninhado, então nenhuma tentativa de salvar ocorreu.
- Execução 231120 (`focusnew`/`focusyes`) só definiu foco GUI; o que ativou os botões não foi registrado. Não conta como entrada só por bot. Nela, o diálogo de salvamento do jogo abriu, com "Speichern" e "Löschen" desativados antes de escolher slot.
- Execuções 230522 e 231025 não produziram log do auxiliar (flag QA não ativada); somente diagnóstico.
- `isolation/verify.py` passa na conta Windows do proprietário; hash da DLL QA implantada igual ao da compilação atual.

### <a id="derived"></a>Deduzido

- Entrada na campanha por bot resolvida em princípio; impedimento é a própria proteção de aninhamento do auxiliar, não jogo nem mod.

### <a id="tried-in-this-session-runs-232208-to-233840"></a>Tentado nesta sessão (execuções 232208 a 233840)

1. `startmenu` + `confirmnewgame` em linha com proteção de aninhamento relaxada (232208): campanha iniciou, depois hook de sessão deixou de ser chamado cerca de 3 s depois. Causa não era o aninhamento.
2. Foco + Enter enfileirado na própria fila de mensagens da janela do jogo (`pressenter`, 232506): entrada só por bot sem auxiliar na pilha. Mesma parada após ativação do mundo.
3. Causa: cena de abertura `Data/Video/G3_Intro.bik` (cabeçalho Bink: 5354 quadros a 25 fps = 214 s) bloqueia laço de sessão; nem driver de quadros Myrtana nem hook QA executam. Proprietário identificou pela tela. CPU baixa, janela responsiva, sem diálogos extras.
4. Executor enfileira um Escape (`WM_KEYDOWN/UP VK_ESCAPE`, enviado só à janela visível do processo do jogo, sem entrada do SO). Isso pulou a introdução em toda execução (desde 233218). Depois espera a linha Myrtana `Native new character qualified` antes de enviar comando.
5. `gCWorld::CreateSaveGame("CoopQA_Smoke")` retornou 3, `ExistsSaveGame` = 0 e nenhum arquivo apareceu. Nem engine nem Myrtana registrou salvamento. Este não é o caminho real de salvamento do jogo. Salvamento nativo interno ainda não testado.
6. Myrtana persiste progresso cooperativo como ponto de controle da campanha no servidor (`campaign.g3coop`: `G3COOP_CAMPAIGN 3 …`, `player|1|QAHost|…`, `native_inventory|1|…`). A suíte valida esse ponto de controle em vez de salvamento nativo.
7. Sair de campanha ativa: Myrtana recusou `WM_CLOSE` bruto enviado ("window close before DefWindowProc") e caminho de menu "Spiel beenden" → "Ja" ("menu quit before termination flag"). Admitiu `WM_SYSCOMMAND/SC_CLOSE` (caminho de fechar pela barra de título via DefWindowProc) com menu aberto: "Native early window close admitted", depois engine registrou `DestroyEngine - all engine modules destroyed`.
8. Pergunta de novo jogo lê "… ein neues Spiel MIT Alternativem Balancing …": opção de balanceamento alternativo do Community Patch está ativada na cópia de teste.

### <a id="checks-that-ran"></a>Verificações executadas

- `smoke.py --game --suite campaign`: PASS duas vezes (233733, 233814). Valida: estado de menu e pasta isolada de salvamentos, registro do cliente no servidor, novo jogo só por bot, introdução pulada, qualificação do personagem Myrtana, `running=1 paused=0 save_allowed=1 world=G3_World_01 hero=PC_Hero` com pasta isolada, ponto de controle do servidor contendo personagem e inventário do host, encerramento normal da engine e hashes idênticos dos 12 salvamentos protegidos.
- `--suite menu`: PASS (233809). `--suite menu --negative-control`: FAIL conforme exigido (233840).
- Só um cliente. Nenhuma validação de dois clientes, combate, inventário, missões ou recarga executada. Nível de QA continua `none`.

### <a id="unknown-1"></a>Desconhecido

- Se salvamento nativo (diálogo do jogo ou F5) funciona com Myrtana e onde grava.
- "Continue campaign" de Myrtana (reiniciar servidor sem `--new`, recarregar ponto de controle) não testado.
- Myrtana também grava diários de intenções por campanha no cliente: `<game dir>/CoopSaves/native-{npc,inventory,reputation}-intents-<owner>-<campaign>.txt` (+ `.lock`). Persistem entre execuções. Antes de testar "Continue campaign", decidir se cada execução começa com `CoopSaves` vazio (arquivado na pasta da execução), para sobras de campanhas anteriores não afetarem resultados. Verificação da cópia local agora permite só esse padrão de nomes ali; após a alteração passou novamente.

## <a id="continuation-two-clients-2026-10-17"></a>Continuação: dois clientes (2026-10-17)

### <a id="observed"></a>Observado

- Segunda cópia completa da instalação (cópia cliente) criada da cópia host verificada com comprovante de hash; tem seu próprio perfil redirecionado. Verificação de isolamento passa.
- Segundo `Gothic3.exe` encerrou com código 0 logo após carregar módulos de patch. Processo host mantém mutex nomeado `\Sessions\1\BaseNamedObjects\GenomeMutex`. Depois de o plugin QA do host fechar seu próprio handle para ele, cliente iniciou normalmente. Nenhuma verificação de classe de janela encontrada.
- Cliente entrou como jogador 2 ("Xardas companion / co-op hero"), servidor admitiu vínculo de personagem da campanha e cada cliente registrou o outro na lista.
- `g3coop_tuning.ini` distribuído: `spawn_in_world_proxies = 0`, `shared_npc_scene = 0`, `shared_npc_death = 0`, `shared_npc_kill_xp = 0`, `character_sync = 0`. Mortes de NPCs na cena inicial de Ardea (dois escravos) vistas só no host; servidor nada registrou sobre elas.
- Sincronização de missões funciona na configuração distribuída: `RunQuest` do host chegou ao cliente em 4 s; conclusão do cliente registrada como "Native quest completion deferred ... awaiting_canonical", servidor registra "progress=completed committed=1", depois ambos aplicam.
- Suíte `coop`: 3 de 3 PASS; controle negativo FAIL conforme exigido. Myrtana também grava `CoopSaves/quest-intents-<owner>-<campaign>.txt`; verificações da cópia agora permitem nomes de diários de missão, saque e morte (tipos das strings da DLL).
- Suíte `rejoin`: FAIL. Após fechar normalmente e reiniciar com novo jogo, cliente registrou "Campaign character binding deferred: reason=3" a cada dois segundos e nunca recebeu missões da campanha.

### <a id="derived-1"></a>Deduzido

- Nível de QA `automated` justificado para o escopo "dois jogadores numa campanha, estado compartilhado de missões nos dois sentidos", não para cooperativo de história completo.
- Reentrada provavelmente exige carregar o salvamento nativo do próprio jogador vinculado à campanha.

### <a id="unknown-2"></a>Desconhecido

- Salvamento nativo com Myrtana; se "world clock synced to host" chega a disparar; compartilhamento de saque, reputação e inventário; comportamento com opções experimentais ligadas.

## <a id="continuation-path-decision-2026-10-17"></a>Continuação: decisão de caminho (2026-10-17)

Objetivo do proprietário: jogar Gothic 3 cooperativamente com amigos.

### <a id="observed-1"></a>Observado

- Início da sessão: upstream tem um commit novo (páginas do guia de consoles), sem issues ou PRs Gothic, Genome ou Myrtana.
- LICENSE Myrtana no ZIP verificado: "This starter kit is released under the MIT License, except where noted." Nada no pacote é indicado como excluído; arquivo também diz para seguir a licença do SDK Gothic 3 ao vinculá-lo. Repositório GitHub sem licença detectada (NOASSERTION). Nota anterior "MIT para o kit inicial" interpretou isso de modo restrito demais: como escrito, binários distribuídos (`Script_G3Coop.dll`, `g3coop_server.exe`) também estão sob MIT.
- Ferramentas presentes: Java 22, Docker 28.4. Ghidra não instalado.

### <a id="derived-2"></a>Deduzido

- Caminho 1 de AGENTS.md (terminar o existente) se aplica: Myrtana existe e tem bugs. Conforme reviving-abandoned-mods.md: descompilar camada nativa, auditar, corrigir em pacote separado, testar ao vivo e automatizar, depois facilitar jogar e devolver correções ao autor.

### <a id="unknown-3"></a>Desconhecido

- Se o autor considera os binários cobertos pelo texto MIT; perguntar antes de redistribuir binários modificados.

## <a id="continuation-decompiling-myrtana-2026-10-17"></a>Continuação: descompilar Myrtana (2026-10-17)

### <a id="observed-2"></a>Observado

- Ghidra 12.1.4 (versão oficial, SHA-256 `ddac49f9...d4db` correspondeu às notas da versão) sem interface em `Script_G3Coop.dll` do ZIP verificado: 21.975 funções, 1 falha de descompilação. Saída permanece no ambiente privado do proprietário.
- Verificação de vínculo retorna códigos de motivo; para motivo 3, mod mostra "Co-op: this character already has campaign progress. Use Continue or select a new character profile." Motivo 2 pede New Game ou importação explícita; alternativa pede carregar o salvamento correspondente à campanha do personagem.

### <a id="derived-3"></a>Deduzido

- Suíte `rejoin` falha testou fluxo errado: jogador que retorna deve carregar seu salvamento nativo marcado pela campanha, não iniciar novo jogo. Motivo 3 é mod funcionando conforme projetado. Resultado de reentrada no registro deve dizer isso.
- Salvamento nativo portanto necessário para jogar em várias sessões; testá-lo é o próximo passo.
- Salvamento nativo: F5 enviado à janela não salvou (jogo lê teclas de jogabilidade por outro caminho). Hook `IsSaveAllowed` de Myrtana só registra estado F5 e repassa resposta do jogo. Myrtana aciona um "QuickSave" nativo por duas chamadas internas Game.dll alcançadas de `gCGUIManager::HandleMessage` (+0x78, +0x7e), verificando opcode E8 antes. Diálogo de salvamento abre pela GUI; botão "Speichern" fica desativado até escolher slot.
- Sair da campanha: proteções de fechar e carregar recusam enquanto objeto global de estado Myrtana mostra trabalho pendente (várias flags e contador); uma vez definido, nada na proteção o limpa.

### <a id="contradiction-stop-and-report-agents-rule-6"></a>Contradição (parar e informar, regra 6 de AGENTS)

- Notas da versão prometem "See and fight beside other players" e estado compartilhado de NPCs. Arquivo de ajustes distribuído diz que corpos remotos são experimentais e desligados ("frozen_ghost": pose estática, possível piscada; reprodução de animação não suportada; comportamento com dois jogos aberto), e `shared_npc_scene` é "autoridade de vida para um NPC" para um único alvo configurado (`Orc_GameStartRaider_Scout_01`); `shared_npc_control` "ainda não replica animação, seleção de alvo, morte ou XP dos NPCs". Documentos citados (`docs/PROXIMITY_INVESTIGATION.md`, `docs/CAPABILITY_AUDIT.md`) não estão no repositório público.
- Deduzido: Myrtana oferece rede, identidade, persistência de campanha e sincronização de missões/reputação/saque/inventário, mas não jogadores visíveis animados nem sincronização geral de inimigos e combate.

## <a id="continuation-build-from-zero-chosen-2026-10-17"></a>Continuação: construção do zero escolhida (2026-10-17)

Proprietário escolheu construir mod cooperativo próprio sobre o SDK Gothic 3 (caminho 2 de AGENTS.md) e reutilizar tudo aprendido. Myrtana permanece referência, não dependência.

### <a id="observed-private-ghidra-analysis-of-the-games-gamedll-no-decompiled-game-code-leaves-the-workspace"></a>Observado (análise privada Ghidra de Game.dll do jogo; nenhum código descompilado sai do ambiente)

- Rotina "QuickSave" de Myrtana chama duas funções internas Game.dll alcançadas de `gCGUIManager::HandleMessage`: getter singleton de `gCHUDFileManager` e `gCHUDFileManager::LoadGame(name)`. Carrega o slot "QuickSave"; não salva.
- `gCHUDFileManager::SaveGame(name)` só chama a exportada `gCWorld::SaveGameWorld(name, image, &header, 0x18)`. Cabeçalho de 24 bytes é `1` seguido de ano, dia, hora, minuto e segundo lidos do conjunto de propriedades de relógio da entidade `World_MCP`. Um mod pode salvar como o jogo usando só funções exportadas.
- `gCHUDFileManager::LoadGame(name)` lê cabeçalho, para sessão, desativa pools de threads, troca ou recarrega mundo, chama a exportada `gCWorld::LoadGameWorld` e move a câmera do jogador à posição salva. Recriá-la de funções exportadas dá mais trabalho; diálogo GUI de carregar é o primeiro caminho mais seguro.
- `Gothic3.exe` e `Engine.dll` não importam biblioteca Steam; `Engine.dll` lê entrada por `DINPUT8.dll`, por isso teclas enviadas à janela chegam aos menus, mas não às teclas de jogabilidade como F5.

### <a id="own-mod-stage-1-hook-point"></a>Mod próprio, etapa 1 (ponto de hook)

- Título de trabalho G3 Together (`Script_G3Together.dll`), GPL-3.0-or-later, ambiente privado por enquanto.
- Subclasse de `eCEngineComponentBase` registrada em `ScriptInit` com `eCModuleAdmin::RegisterModule` recebe `Process()` cerca de 100 vezes por segundo no mundo de campanha, além de `WorldActivate`/`WorldDeactivate`/`PreShutdown`. É a interface de módulos da própria engine; sem precisar alterar vtable.
- Bot de teste agora vive no mod (ativo só com arquivo de flag). Uma troca de perfil move Myrtana e auxiliar antigo para quarentena em ambas as cópias e registra no comprovante; ambas as verificações de isolamento seguem esse registro.
- Teste de conclusão da etapa 1 passou: novo jogo por bot, mod registra `world=G3_World_01 hero=PC_Hero pos=... yaw=...` a cada segundo, a 95–103 quadros por segundo.
- Vídeo de introdução só começa após mundo ativo. Escape enviado durante carga se perde e vídeo executa os 214 s completos; executor agora espera o relatório por segundo do mod parar antes de enviar Escape.
- Bug aberto no mod: fechar o jogo causa falha no encerramento da engine em `Engine.dll+0x5B2B6` com registrador apontando para nossa DLL, mesmo quando módulo se desregistra em `PreShutdown`. Em análise.

### <a id="own-mod-stage-2-second-player-visible"></a>Mod próprio, etapa 2 (segundo jogador visível)

- Transporte: ENet 1.3.18 (MIT, tag git fixada ao commit), host listen, estado a 20 Hz com hash do mundo, posição e quatérnio de rotação. ENet precisa ser compilado com `/Gz` como o alvo de script Gothic.
- Timeouts ENet padrão derrubavam cliente entrando após cerca de 9 s: laço da engine do cliente para durante carga do mundo e introdução. Timeouts do par agora são 60–180 s e clientes reconectam automaticamente.
- Boneco: `Entity::Spawn(Template("Slave_01"), pose)`, colisão desligada, `Entity::MoveTo` a cada quadro com interpolação; removido quando jogador sai, fica obsoleto ou está em outro mundo.
- Teste de conclusão da etapa 2 passou 3 de 3: ambos mostram o boneco do outro; cliente percorre círculo de 3 m em oito passos e boneco do host acompanha a até 50 cm (erros 2,5–42 cm, idênticos nas execuções); boneco desaparece quando cliente sai; ambos encerram normalmente. Controle negativo (exige ponto 10 m distante) falha conforme exigido.
- Ainda não: animação, aparência real do jogador, IA do NPC boneco (ainda executa rotina entre movimentos).
- Etapa 2b (movimento do boneco), tudo no jogo distribuído, sem novos recursos: slot 0 de animação de `eCVisualAnimation_PS` (`GetMotionDesc(type 0)`) é o movimento visível do corpo. Movimentos de locomoção (`_Move_`) não podem ser reproduzidos com `StartPlayAni`; engine só os toca enquanto corpo se desloca. Alimentar controlador de movimento do boneco (`PSCharacterMovement::SetMovementMode` + `SetMovementGoal`) com modo do herói remoto faz a engine escolher caminhada, corrida ou sprint. Reiniciar um goto de IA a cada 150 ms mantinha corpo na pose inicial.
- NPC criado continua reagindo à percepção (observando luta de Ardea, suspeitos) mesmo com tarefa ociosa; definir propriedade de rotina `AIMode` como `Abandoned` e nome de rotina vazio parou isso.
- Bug encontrado pelo rastreio a 5 Hz: comparar relógio ENet com GetTickCount fazia estados recentes parecerem obsoletos após underflow sem sinal; boneco recriado mais de 400 vezes numa execução enquanto teste anterior mais fraco ainda passava.
- Etapa 2 mais rigorosa passou 3 de 3 (controle negativo falha): uma criação por jogador, somente tarefa ociosa, pelo menos 10 amostras de caminhada/corrida durante caminhadas reais (84–85), boneco a até 60 cm do jogador após cada parada (0–1,6 cm).
- Bonecos agora usam o próprio template do herói `PC_Hero` (adaptador Myrtana o rejeita; razão não documentada). Nos testes o jogo ainda resolve jogador real por `Entity::GetPlayer()` e por nome nos dois lados, e etapa 2 passa 3 de 3 com ele. Bonecos são imortais porque template pode carregar inventário inicial do herói.

### <a id="own-mod-stage-3a-npcs-with-host-authority"></a>Mod próprio, etapa 3a (NPCs com autoridade do host)

- Identidade de NPC entre cópias: `eCEntityProxy(entity).GetEntityID()` (GUID) no host, `Entity(bCPropertyID(bCGuid(raw)))` no cliente. Mesmos dados de mundo geram mesmos GUIDs.
- NPCs espelhados nos clientes continuavam recebendo tarefas dos scripts de cena (`ZS_RevolutionAttack` na batalha de Ardea, `ZS_Boss`, `ZS_HangAround`) cerca de seis vezes por segundo; desfazê-las a cada quadro deixava janelas de um quadro. Limpar alvos de combate para impedir isso derrubou o jogo duas vezes em `gCScriptProcessingUnit::sAICombatMoveInstr` (instrução de combate ativa com alvo vazio).
- Correção funcional: envolver todo estado e função de IA registrados (441 nesta versão) pelos mapas de nomes de `gCScriptAdminExt`; entrada superior da pilha de runtime nomeia estado em execução, então um wrapper pode despachar todos os originais. Corpos que conduzimos executam só tarefa ociosa. Chamadas wrapper sem estado envolvido são contadas e foram 0 em toda execução. Arrays por DLL (`gSScriptDLL`) continham entrada nula nesta versão e derrubaram primeira tentativa; mapas do admin funcionam.
- `CanReceivePerceptionFrom` é script simples (`gSScript`); filtro nele instala, mas nunca disparou nestas execuções.
- Teste de conclusão da etapa 3a passou 3 de 3 (controle negativo falha): 11–17 NPCs vistos nos dois lados, todos vivos espelhados, nenhum manteve IA do jogo em duas amostras, erro de posição mediano 5–15 cm (pior 137 cm), todo NPC morto no host (escravos na luta de Ardea) morto no cliente, encerramentos limpos.

## <a id="2026-10-17-own-mod-stage-3b-damage-with-host-authority-in-progress"></a>2026-10-17: mod próprio, etapa 3b (dano com autoridade do host), em andamento

Observado (runtime, somente cópias de teste):
- gCEntity::DoDamage (Game.dll) chama script admin `DoLogicalDamage` (vítima, causador), depois `AddHitPoints` (vítima, causador, -DamageReceiver.DamageAmount) se o primeiro retornou não zero. Nomes de script lidos em runtime das globais bCString Game.dll RVA 0x3f188c / 0x3f1890.
- Julgamento de acerto (AssessHit, Script_Game.dll RVA 0x2b580) só registra dano em DamageReceiver.DamageAmount (68 de It_1H_Sword_Rust_01 num escravo); pontos de vida caem depois. `OnDamage` chama AssessHit diretamente; `DoLogicalDamage` chama após proteções que exigem golpe em andamento (DamageType da arma é None fora de um golpe, estado de ação/animação do atacante).
- Chamar DoLogicalDamage de um bot sem golpe real retorna 0 (sem dano).
- Chamar gCEntity::DoDamage diretamente do mod gerou exceção: não fazer isso.

Construído (ainda não verificado por suíte aprovada):
- combat.cpp: um filtro em `DoLogicalDamage` e `OnDamage`. Cliente, vítima é NPC espelhado: medir mudança direta de HP mais dano registrado, desfazer ambos, enviar HitNpc(guid, delta) ao host. Host, vítima é boneco: o mesmo, enviar HitPlayer(delta) ao cliente, cujo herói o sofre por AddHitPoints. Host aplica HitNpc por AddHitPoints e Kill() a 0 HP. Protocolo v5 (mensagens 7/8, confiáveis).
- QA: arm <template>, hitnpc <guid>, hitpuppet <id>, hp, combatoff (controle negativo), gamestr <rva>.
- Suítes stage3b e combatdiag de together.py.

Em aberto:
- stage3b ainda não passou (primeiras execuções: zero dano porque bot acertava pelo caminho errado).
- Golpes reais ainda não conduzidos por bot; contador por hook (logical_calls) pretende mostrar lutas NPC da invasão inicial passando pelo filtro DoLogicalDamage.
- Limites conhecidos: morte no host usa Kill() em vez da própria escolha de nocaute/morte do jogo; herói do cliente a 0 HP ainda sem reação de morte; bonecos sem armas (sem sincronização de equipamento).

Atualização (combatdiag, somente host, mesmo dia):
- Acerto QA por OnDamage + AddHitPoints(-recorded) agora causa dano imediatamente: batedor orc 459 -> 392 (registrado 67, It_1H_Sword_Rust_01). Filtro viu chamada.
- Contradição: logical_calls=0 durante invasão inicial, embora orcs e escravos lutassem (pontos de vida caíram). Assim, golpes corpo a corpo NPC NÃO chegam à nossa entrada `DoLogicalDamage` trocada. Ou Game.dll chama script por caminho que evita o ponteiro gSScript, ou acertos NPC usam outra rota. Qual é desconhecido; resolver antes de confiar no filtro para golpes reais.

## <a id="2026-10-17-workspace-moved"></a>2026-10-17: ambiente de trabalho movido

Mod agora vive em seu próprio repositório ao lado de um ambiente privado (cópias de teste, SDK, compilações) e deste clone do guia. Observado ao recompilar de diretório novo: compress.c de ENet 1.3.18 não compila sob /Gz (funções do codificador de intervalos são armazenadas em ponteiros ENET_CALLBACK = __cdecl); compilar esse arquivo com /Gd. Um diretório antigo escondera isso com arquivo-objeto desatualizado. Suítes das etapas 1, 2 e 3a passaram novamente no novo layout (uma execução cada, 2026-10-17).

## <a id="2026-10-17-how-hits-really-reach-hit-points-hit-path-probe-stage-3b-design"></a>2026-10-17: como acertos realmente chegam aos pontos de vida (sonda do caminho de acerto), projeto da etapa 3b

Observado (mod próprio, cópias isoladas; sonda envolveu o script `AddHitPoints` e registrou endereços de retorno na pilha, módulo+RVA, durante invasão inicial no host):
- 225 de 236 chamadas em 45 s: dano de contato de arma. `gCTouchDamage_PS::TriggerTarget` (Game.dll RVA 0x693b0) chama script admin cujo nome é propriedade do conjunto TouchDamage da arma, depois `AddHitPoints(victim, -DamageReceiver.DamageAmount)`, depois efeitos do acerto. Exemplo: vítima Hamlar, fonte It_Axe_OrcWaraxe_01, -8.
- 11 chamadas: laço de combate IA `gCScriptProcessingUnit::sAICombatMoveItlLoop` (RVA 0x16dd00) chama `OnHit`, depois `AddHitPoints` (fonte: o próprio NPC atacante).
- `gCEntity::DoDamage` (RVA 0x666d0) chama `DoLogicalDamage`, depois `AddHitPoints`; não visto na invasão.
- Os três chegam a `AddHitPoints` por `gCScriptAdmin::CallScript` -> `RunScript`, e a entrada `gSScript::m_funcScript` trocada é o que executa. A entrada `DoLogicalDamage` trocada nunca foi chamada na invasão, explicando a contradição anterior.
- No cliente, NPCs espelhados ainda atingem uns aos outros por dano físico de contato (armas colidem mesmo com IA desligada).

Deduzido (projeto, verificado pela suíte da etapa 3b):
- Impor autoridade do host em um lugar, script `AddHitPoints` (só valores negativos). Cliente: próprio herói atingiu NPC espelhado -> enviar valor ao host, não aplicar nada; NPC espelhado atingiu outro espelhado ou herói -> descartar (host simula isso). Host: algo atingiu boneco de jogador remoto -> encaminhar àquele jogador, cujo herói sofre por `AddHitPoints`.
- `Entity::Kill` remove corpo da lista de NPCs e da vista; deixar NPCs morrerem com `Routine.FullStop(); Routine.SetTask("ZS_RagDollDead")`, no host e cliente.

Desconhecido:
- Resultados que `Script_Game.dll` aplica chamando AddHitPoints diretamente (aparadas, vantagens) evitam admin e não são cobertos.
- Nocaute em vez de morte (ZS_Unconscious) ainda não decidido pelo host.
- Golpes reais do jogador ainda não conduzidos por bot; suíte acerta por `OnDamage` + `AddHitPoints`.

Resultado da etapa 3b (2026-10-17, commit do mod "Stage 3b"): suíte `stage3b` passou 3/3 com host e cliente; controle negativo (filtro em passagem direta no cliente) falha conforme exigido ("Client changed the NPC's hit points itself"); suítes 1, 2 e 3a continuam passando; encerramento limpo da engine e salvamentos reais inalterados em toda execução. Corrigidos no caminho: julgamento do próprio cliente iniciava estado de morte antes de confirmação do host (agora só após host informar NPC morto), e alvo na borda de interesse de 40 m tornava verificação instável (suíte agora escolhe invasor perto do cliente).

## <a id="2026-10-17-stage-4-shared-quest-state-own-mod"></a>2026-10-17: etapa 4, estado compartilhado de missões (mod próprio)

Observado:
- gCQuestManager_PS contém 570 missões nesta versão (Steam, CP 1.75.14). Estado lido com `quest->AccessStatus()`; `RunQuest`, `SucceedQuest`, `FailQuest` no gerenciador o mudam com os efeitos colaterais do jogo; `gCQuest_PS::SetStatus` define diretamente.
- Em toda execução da etapa 4, toda mudança aplicada passou pelas funções do gerenciador (forced=0).
- Mod do cliente conecta ao host ainda no menu principal; estado enviado nesse momento não pode ser aplicado (sem jogo ativo). Cliente agora pede estado completo do host ao entrar no jogo e após toda reconexão.

Decisões (compartilhado ou por jogador):
- Estado de missão: compartilhado, host decide. Jogo de cada jogador aplica pelo gerenciador, então cada herói recebe a experiência da missão uma vez (progresso compartilhado, recompensa individual).
- Ainda não coberto: estado de diálogo/informação (gCInfoManager_PS), contadores de entrega, posição de enclave e política, recompensas de itens em diálogos, objetos do mundo.

Resultado: suíte `stage4` passou 3/3 (mudanças chegam em uma consulta de 0,5 s nos dois sentidos e para entrada tardia); controle negativo (sincronização de missões desligada no cliente) falha conforme exigido; suítes 1 a 3b continuam passando.

## <a id="2026-10-17-stage-4b-shared-dialog-state-can-a-client-hold-a-dialog"></a>2026-10-17: etapa 4b, estado compartilhado de diálogos; um cliente consegue manter diálogo?

Observado:
- gCInfoManager_PS contém 4591 opções de diálogo (gCInfo_PS) nesta versão; `InfoGiven` marca opção como contada e `ConditionPlayerKnows` de outras opções a lê. Nomes mais longos de missão e informação cabem em 62 bytes.
- Suíte `stage4b` (opções contadas chegam à entrada tardia, host -> cliente, cliente -> host; opção intocada continua não contada) passou 3/3; controle negativo falha; suítes anteriores continuam passando. Uma execução 3b falhou porque gravação do arquivo de comandos do bot QA colidiu com leitura do mod (violação de compartilhamento Windows); bot agora tenta novamente, e nova execução passou.
- Chamar `gCInfoManager_PS::StartInfoManager(hero, Diego)` na invasão inicial retornou false igualmente no host e cliente (Diego lutava), então não diz nada sobre cooperativo.

Deduzido de Script_Game.dll (descompilado, privado):
- Diálogo executa dentro da IA do NPC: reação no RVA 0xae9b0 define tarefa `ZS_Talk` quando jogador se dirige a ele e não há diálogo ativo; estado IA `ZS_Talk` (RVA 0x24ff0, registrado de `Reaction_Tasks\ZS_Talk.cpp`) chama `PSInfoManager::Start` e continua em `ZS_Talk_Loop`.
- Cliente do mod mantém NPCs espelhados fora de todo estado IA exceto sua tarefa ociosa, então provavelmente ainda não consegue conversar com NPC de autoridade do host. Não verificado até existir cena calma de teste.

## <a id="2026-10-17-stage-4c-a-clients-dialog-with-a-host-owned-npc"></a>2026-10-17: etapa 4c, diálogo de cliente com NPC de autoridade do host

Correção da entrada acima: a afirmação deduzida "cliente provavelmente não consegue conversar com NPC de autoridade do host" estava errada. Testado: no cliente, `AssessTalk(mirrored Diego, hero)` retornou 1 e diálogo executou pelo gerenciador de informações do próprio jogo, embora modo IA do NPC espelhado seja Abandoned (10).

Observado:
- Nomes registrados relacionados à conversa (dos mapas do admin de scripts em runtime): scripts `AssessTalk` (Script_Game.dll RVA 0x30d50), `PlayerOpenDialog` (0x6bcf0), `StartSayRefuseTalk`; estados IA `ZS_Talk`, `ZS_Talk_Loop`, `PS_Interact_Talk`, `IS_Running_SelectInfo`, `IS_Running_ProcessInfo`.
- `AssessTalk(npc, player)` recusa NPCs em combate; quando aceita, ambos recebem o outro como alvo atual e a tarefa `ZS_Talk`.
- Na invasão inicial ninguém conversa. Invasão vem em ondas: limpá-la (só QA) exigiu duas ou três rodadas de matar todo invasor em até 300 m; depois Diego, Gorn e Milten mudam para conversa casual.
- `Entity::Kill()` em invasores durante luta derrubou host cerca de um segundo depois (EIP=0, violação de acesso em Gothic3.exe). Matar por `AddHitPoints` e `ZS_RagDollDead` não.
- Logo após invasão, Hamlar inicia sozinho diálogo com herói do host (informação importante).

Construído: cliente informa host quando seu herói começa ou termina diálogo com NPC espelhado; host mantém esse NPC parado (sem rotina, tarefa ociosa, IA bloqueada) até diálogo acabar ou jogador desconectar. Cliente para de mover NPC durante diálogo e o deixa executar `ZS_Talk`/`ZS_Talk_Loop`.

Primeira execução 4c: cliente ouviu BPANKRATZ31453, BPANKRATZ31454 e, após escolher primeira opção, FILLER926; Diego do host não moveu (0 cm) e foi liberado depois; todas as três opções contadas chegaram ao host.

Resultado da etapa 4c: suíte `stage4c` passou 3/3; controle negativo (host ignora aviso de diálogo) falha conforme exigido, com timeout em "host holds Diego"; suítes 1 a 4b continuam passando. Em 2 de 8 execuções anteriores, `AssessTalk` do cliente foi recusado uma vez (visto com `has_info=0` enquanto herói do host estava no diálogo de Hamlar); suíte agora repete como jogador faria e registra cada recusa. Desconhecido: por que essa informação ficou brevemente indisponível. Também corrigido: vídeo de introdução do cliente pausava fluxo de estado tempo suficiente (5 s) para host remover e recriar boneco; limite agora 15 s e jogos desconectam ativamente ao encerrar.

## <a id="2026-10-17-stage-5-world-items-own-mod"></a>2026-10-17: etapa 5, itens do mundo (mod próprio)

Decisões (compartilhado ou por jogador): inventário de cada herói pertence a seu jogador. Itens no mundo pertencem ao host: o que um pega desaparece para todos, e primeira solicitação vence.

Observado:
- Ao redor da posição inicial em Ardea há 34 itens de mundo em até 30 m (poções, pilhas de ouro, maçãs, pão, taça de prata, pedra de teleporte); `Entity::GetEntities()` retornou 243 entidades no alcance.
- Nomes registrados relacionados a itens incluem função IA `_AI_TakeItem` (Script_Game.dll RVA 0x4adb0), estado de jogador `PS_Normal_Take` (0x82240), scripts `OnItemReceived` (0xb60b0), `PlayerOpenLoot`, `PlayerOpenTrade`, `AssessTakeItem`, `SendPerceptionTakeItem`, `PickPocket`.
- Coletar: `PS_Normal_Take` com item como alvo atual do herói executa `_AI_TakeItem`, terminando em `PSInventory::InsertStack(item)`. Depois GUID do item não resolve mais (entrou numa pilha). Bot pode pegar como jogador: `NPC.SetCurrentTarget(item)` e tarefa `PS_Normal_Take`.
- `OnItemReceived` só é chamado por `gCInventory_PS::TransferItemsTo` (inventário para inventário: comércio, saque, entrega), não ao pegar do chão.
- `Entity::Decay()` remove item de mundo imediatamente (GUID para de resolver, sai de `GetEntities`).
- Pilha de ouro (`It_Gold_Stack_01`) chega ao inventário como moedas de outro template; o que coleta acrescenta deve ser lido do inventário, não do nome do item de mundo.

Construído: mod envolve `_AI_TakeItem` para herói local, anota antes GUID do alvo e informa coleta quando esse GUID some. Cliente solicita ao host; host remove item (Decay) e avisa todos, ou recusa se já sumiu, e cliente devolve o acrescentado. Coletas do próprio host anunciadas igualmente.

Ainda não coberto: NPCs coletando itens, itens largados no mundo, baús e cadáveres (saque), comércio.

Resultado da etapa 5: suíte `stage5` (coleta do cliente some no host, coleta do host some no cliente, ambos pegando um item o deixam com exatamente um jogador, coleta de item já ausente no host é recusada e devolvida, item intocado permanece) passou 3/3; controle negativo (sincronização de itens desligada no cliente) falha conforme exigido; suítes 1 a 4c continuam passando.

## <a id="2026-10-17-stages-5b-and-5c-plunder-and-trade-own-mod"></a>2026-10-17: etapas 5b e 5c, saque e comércio (mod próprio)

Observado:
- Após invasão inicial, baús próximos ao início tinham conteúdo igual no host e cliente (dados estáticos do mundo), mas todo cadáver orc diferia: saque sorteado por máquina (por exemplo host It_Gold:48, cliente It_Gold:47 mais machado). No cliente, cadáveres espelhados também mantinham armas.
- `OnItemReceived` só chamado por `gCInventory_PS::TransferItemsTo` para itens `Book_CPT`, então não é hook geral de transferências.
- `PlayerOpenLoot` / `PlayerOpenTrade` (Script_Game.dll RVA 0x6bfd0 / 0x6c4c0) registram parceiro, mudam página GUI e colocam jogador em `PS_HUD`; transferências em si vêm da tela (`TransferItemsTo`). `PlayerOpenTrade` também chama `PSInventory::StackTradingGold` no comerciante.
- Após cliente regravar sua cópia de inventário, ordem das pilhas difere do host; referencie pilhas pelo template de item, não índice.
- Todo NPC carrega item `Fist`; não é mercadoria.
- Definir `ZS_RagDollDead` externamente num NPC em luta derrubou host uma vez (violação de acesso em Script.dll+0x13ea3, logo após `gCQuestManager_PS::OnNPCKilled`). QA agora mata com acerto letal real (vida em 1, depois golpe de arma julgado pelo jogo). Host ainda define essa tarefa quando acerto de cliente mata NPC (etapa 3b): risco conhecido.

Construído: host envia conteúdo de baús e cadáveres perto de qualquer jogador (e comerciante com quem cliente negocia) sempre que muda; cliente sobrescreve sua cópia. Cliente que abriu saque ou comércio envia o que jogador mudou como transação única (deltas no lado do recipiente: item e ouro juntos numa compra); host aplica tudo ou nada e, numa recusa, cliente desfaz mudança no herói, inclusive mudanças posteriores ainda não informadas. Encontrado pelo teste de corrida e corrigido: conteúdo chegando do host entre coleta do cliente e próxima consulta sobrescrevia coleta sem informar, e ambos ficavam com item.

Resultados: suíte `stage5b` (cadáveres mostram conteúdo do host, coletas de cliente e host aparecem no outro, dois jogadores pegando uma pilha, coleta tardia recusada desfeita) passou 3/3; controle negativo falha; suítes anteriores continuam passando. Suíte `stage5c` (cliente vê mercadorias do host, compra move item e ouro no host, compra recusada é desfeita) passou na primeira execução; série pendente.
- Nomes de itens não são identificadores únicos: Diego carregava `Appow:20` e `Arrow:20`; recriar inventário no cliente por nome produzia `Arrow:40`. Recipientes agora sincronizados por ID de template de item (ID de propriedade do template, idêntico em toda máquina), com nome só para logs.

Resultados (2026-10-17): suítes `stage5b` e `stage5c` passaram 3/3 cada com conteúdos indexados por ID de template; ambos os controles negativos (sincronização de recipientes desligada no cliente) falham conforme exigido; suítes 1 a 5 continuam passando. Não coberto: telas reais de comércio e saque (bot usa PlayerOpenLoot/PlayerOpenTrade e transferências de inventário), vender ao comerciante e suas regras de preço, NPCs coletando itens, itens largados no mundo, qualidade de item (conteúdo recriado com qualidade 0).

## <a id="2026-10-17-killing-an-npc-on-behalf-of-a-client-stage-3b-follow-up"></a>2026-10-17: matar um NPC em nome de um cliente (continuação da etapa 3b)

Observado (Script_Game.dll, descompilada privadamente; verificações em runtime nas cópias de teste):
- Julgamento de acerto (AssessHit) limita dano de qualquer atacante exceto jogador e o define como 0 se mataria (exceto alguns tipos de vítima): acerto real de boneco de cliente deixou orc de pé com 0 pontos de vida. Só acertos do jogador chegam às ramificações de morte (`ZS_RagDollDead` quando `IsDeadlyDamage`, senão `ZS_Unconscious`, `ZS_LieKnockDown`, ...).
- Falha após morte QA: violação de acesso em `Entity::AttachTo` (Script.dll+0x13e80) chamada do script callback da engine `GetCombatMoveLength` (Script_Game.dll RVA 0xaa270) num movimento de combate de outro NPC, um quadro após tarefas de morte definidas manualmente em invasores lutando. Causa não comprovada.
- Scripts relacionados à morte: `Kill` (RVA 0x1bc30: vítima primeiro, assassino segundo; gerenciador de missões `OnNPCKilled`, hooks de história, `GiveXP` para jogador), `GiveXP` (0x4e160), `CanBeKilled` (0x2da00), `OnCheatKill` (0xab020: morte pelo console; self = quem mata, other = alvo; para alvo, limpa alvo de combate, define `ZS_RagDollDead`, ou `ZS_Dead` para algumas espécies). Com argumentos invertidos, não fazia nada.

Alterado: quando acerto de cliente mataria, host define vida do NPC como 0 e o mata com `OnCheatKill` (boneco do cliente como assassino), depois avisa aquele cliente, que recompensa seu próprio herói com `GiveXP(hero, NPC, -1)` (primeiro teste: 0 -> 200 de experiência). Antes ninguém ganhava experiência por morte causada por cliente.

## <a id="2026-10-17-outside-review-claude-models-via-api-hypotheses-to-test"></a>2026-10-17: revisão externa (modelos Claude por API), hipóteses a testar

Duas perguntas foram aos modelos Claude por API (pacotes e respostas permanecem no ambiente privado). A pergunta de falha foi recusada por Fable 5.1 (alternativa após recusa encaminhou a Opus 4.8, coerente com categoria cibernética); revisão de projeto respondida por Fable 5.1. Pontos são hipóteses até testar:

- [Hipótese] Autoridade do host tem raio: Genome carrega setores e processa NPCs só perto da câmera local, então cliente distante não tem NPCs do host para espelhar. Teste: herói cliente a 600/1500/4000 m.
- [Hipótese] Menu ESC e inventário pausam sessão; se `Process()` parar, boneco fica obsoleto e ENet pode desconectar. Teste: abri-los em cada lado por 30 s e contar chamadas Process.
- [Deduzido] Entidades criadas em runtime (criações, largadas, flechas, invocações) recebem GUIDs diferentes por máquina. Teste: comparar conjuntos de GUIDs NPC/item perto de ambos os heróis uma vez por segundo na invasão e após largar algo.
- [Deduzido] Acertos aplicados pelo host por `AddHitPoints` não disparam percepção do NPC: sem retaliação, sem crime. Teste: cliente atinge NPC pacífico; observar tarefa e alvo no host.
- [Deduzido] Herói cliente a 0 pontos de vida não tratado (original: fim de jogo); bonecos imortais.
- [Hipótese] Paridade de instalação: balanceamento alternativo, PUP e opções de patch mudam dano e XP; calcular hashes ao entrar.
- [Hipótese] Trocas de ponteiros e wrappers IA podem não sobreviver a `LoadGame` do host.
- [Resposta sobre falha, inferência] Entidade liberada na falha GetCombatMoveLength provavelmente era alvo de combate de lutador sobrevivente, morta externamente no mesmo quadro junto com outras; mitigações sugeridas: uma morte por quadro, limpar referências à vítima (mas limpar alvos de outros NPCs já causou falha aqui), redefinir proxies SPU do admin de scripts após nossas próprias chamadas CallScript.
- Projeto de salvamento sugerido: salvamento nativo do host é a campanha; clientes carregam cópia e mod restaura herói de cada jogador de registro individual em arquivo auxiliar.

## <a id="2026-10-17-exploration-1-how-far-host-authority-reaches-radiusdiag"></a>2026-10-17: exploração 1, até onde vai a autoridade do host (radiusdiag)

Observado (host permanece no início em Ardea; cliente se afasta):
- `Entity::GetNPCs()` e `Entity::GetEntities()` só listam o processado ao redor do herói local: cerca de 20 NPCs em ~45 m e ~240 entidades no início. Porém 405 dos 414 donos de opções de diálogo resolvem por nome (`Entity::GetEntity`) no host, com posições a até 3,3 km: entidades distantes existem, mas fora das listas de processamento.
- Mover herói cliente com `Entity::MoveTo` não move área processada: 30 s depois cliente ainda processava NPCs de Ardea (agora a 0,5–3,3 km), e NPC ao lado do herói não tinha tarefa.
- Com `Entity::Teleport(target)` do próprio jogo, cliente processa novo local em 5 s: 12–32 NPCs com tarefas (`ZS_HangAround`, ...). A 3,3 km, guarda Sven reagiu ao herói (`ZS_ReactToZone`, depois `ZS_Attack`). Nenhum espelhado: no host mesmos NPCs existem, mas sem tarefa nem movimento (um, Fadi, deslocou 1,4 m em 30 s; inexplicado), e listas do host nada contêm perto do cliente.

Deduzido: assim que jogadores se separam, cada máquina executa NPCs ao redor do próprio herói com IA própria, sem sincronização, e cópias de regiões distantes do host ficam congeladas. Autoridade do host por espelhamento só se sustenta dentro de seu raio de processamento. Campanha com amigos precisa de autoridade regional: máquina que processa NPC o controla, host registra resultados.

Além disso: movimentos QA para locais distantes devem usar `Entity::Teleport`, não `MoveTo`.

## <a id="2026-10-17-exploration-2-inventory-and-esc-menu-pausediag"></a>2026-10-17: exploração 2, inventário e menu ESC (pausediag)

Observado (cada lado abriu página por 25 s por `gCGUIManager::OpenInventory` / `gCSession::OpenMenu`):
- Inventário: sessão não pausada (`IsPaused` 0); trabalho por quadro do mod, rede e boneco do outro lado continuam recentes (idade do estado 17–69 ms); NPCs do host continuam movendo.
- Menu ESC: sessão pausada (`IsPaused` 1), mas módulo da engine do mod continua executando: contador de quadros sobe, estado recente (35–61 ms), boneco permanece. Preocupação da revisão de menus pararem mod e derrubarem conexões não se confirma nesta configuração.
- Ainda não medido: se NPCs do host congelam enquanto ele fica no menu ESC (provável, pois sessão pausa); cooperativo deveria então proibir ou compartilhar pausa.

## <a id="2026-10-17-exploration-3-the-games-own-save-and-load-savediag"></a>2026-10-17: exploração 3, salvar e carregar pelo próprio jogo (savediag)

Salvar/carregar nativo em Game.dll desta versão (Steam 1037023 + CP 1.75.14), encontrado com Ghidra; mod verifica bytes do prólogo antes de chamar, recusando outra versão em vez de falhar:
- Getter singleton `gCHUDFileManager` no RVA 0xa92d0; `SaveGame` em 0xa9e90 e `LoadGame` em 0xa9a10, ambos `__stdcall(this, bCString const* name)` (primeira tentativa como `__thiscall` fez jogo procurar nome vazio).
- Salvamento grava `<name>.g3savcpx` (~66 KB) e `<name>.g3savcpxdat` (~2,1 MB) na pasta de salvamentos do perfil.

Observado (três correções necessárias, depois uma execução completa aprovada):
- Carregar slot inexistente deixa jogo travado. Proteção: `gCWorld::ExistsSaveGame` primeiro.
- Salvamento feito com boneco do cliente (cópia `PC_Hero`) existente não pode ser carregado: FATAL "current world has more than one hero!". Mod agora remove todos os bonecos antes de salvar; voltam na próxima atualização de rede.
- `LoadGame` ativa novo mundo sem WorldDeactivate anterior, então mod falhava nas entidades ainda mantidas do mundo antigo. Agora esquece todas também em WorldActivate.
- Depois: host salvou, carregou seu próprio salvamento, hooks de funções do mod ainda apontavam para DLL do mod, cliente permaneceu conectado e boneco reapareceu. Depois cliente carregou cópia do salvamento do host: ambos passaram a se ver e ter 16 NPCs em comum; ambos encerraram normalmente.

Ainda não medido: se estado de missões e itens realmente coincide após cliente carregar salvamento do host (só missão intocada comparada, 0 nos dois) e como herói próprio de cada jogador (nível, inventário) sobrevive quando todos carregam o mundo do host.

Deduzido: projeto de salvamento da revisão é viável em princípio: salvamento nativo do host é campanha, clientes carregam cópia. Herói próprio de cada jogador ainda precisa de registro individual restaurado após carga.

## <a id="2026-10-17-outside-review-2-architecture-for-players-who-split-up-hypotheses-to-test"></a>2026-10-17: revisão externa 2, arquitetura para jogadores que se separam (hipóteses a testar)

Fable 5.1 foi solicitado (respondeu por si) a criticar plano "aviso de distância primeiro, depois autoridade regional com host guardando registros, sem servidor de mundo". Pontos, todos não verificados até executar teste:
- [Inferência] Sem servidor de mundo: Genome tem uma área processada ao redor do herói local e nenhum modo sem interface; servidor seria mais um jogo com uma área. Processo separado de *registro* (missões, solicitações, mortes, relógio) poderia ser extraído depois para migração de host, mas não é simulação de mundo.
- [Inferência] Separar simulação de registro: IA, posições e dano pertencem a quem processa NPC ("proprietário"); solicitações de itens, transações de recipientes, estado de missões/informações, registros de mortes e relógio ficam com host para toda região. Etapas 4 a 5c permanecem válidas, pois só precisam resolver GUIDs.
- [Inferência] Autoridade "persistente" em vez de "host vence sobreposições": primeira máquina que processa NPC o mantém até sair de sua lista de processamento (com histerese de ~1 s), desconectar ou pausar. Evita transferências em luta, origem das falhas deste mod. Exige espelhamento simétrico (toda máquina envia o que controla, espelha o restante).
- [Inferência] Diário do mundo no host (indexado por GUID: morto/caído + assassino, coletado, conteúdo, mudanças de rotina), aplicado sob demanda ao entrar entidade na lista de processamento de uma máquina; gravações imediatas em entidades congeladas só se teste mostrar segurança e persistência no salvamento. Imitar forma nativa de NPC morto (comparar conjuntos de propriedades antes/depois de morte real) em vez de inventar uma.
- [Hipótese] NPCs podem ser reposicionados na rotina ao entrar no processamento (deslocamento de 1,4 m de Fadi); então snapshot de transferência deve ser aplicado depois de processar NPC, e posições dispensam streaming a cópias congeladas.
- [Inferência] Comandos de diálogo que mudam mundo (ativar/teleportar NPC, modo IA, estado de guarda, criações por script) só executam onde diálogo ocorreu; marcar `InfoGiven` no host provavelmente não os reproduz. Conferir classes `gCInfoCommand*`. Apontado como maior lacuna ausente destas notas.
- [Inferência] Limite de distância: puxar de volta não garante consistência (limite de 35 m com raio de 45 m ainda deixa NPCs não processados pelo host na área do cliente) e é ruim em combate; aviso basta.
- Experimentos propostos: E1 área processada e reativação (onde NPC reaparece), E2 gravações em entidades congeladas e salvamento nativo, E3 comparação de GUIDs em runtime, E4 morte nativa por cliente distante, E5 relógio, E6 host no menu ESC como registro, E7 comandos de diálogo.

## <a id="2026-10-17-exploration-4-install-parity-suite-parity"></a>2026-10-17: exploração 4, paridade de instalação (suíte `parity`)

Mod agora calcula impressão digital na inicialização (94 ms): Game.dll, Script.dll, Engine.dll, toda DLL em `scripts`, arquivos de regras (Templates, Infos, Quests: conteúdo completo), demais arquivos `Data` (só nome e tamanho) e opções: estrutura de configuração da própria engine (`eCApplication::GetEngineSetup`: Difficulty, AlternativeBalancing, AlternativeAI, MinHitDuration, XPModifier, QuickLoot), mais linhas `[Game]` de `Ini/ge3.ini` (para ExtendedContent). Cliente envia com apresentação; host recusa diferente e nomeia partes. Observado: engine informou `difficulty=Medium alternative_balancing=1 alternative_ai=1 min_hit_duration=6
xp_modifier=100` nesta instalação, igual a ge3.ini, então deslocamentos de estrutura do SDK correspondem à versão. Com `XPModifier=150` na cópia cliente, engine informou 150 (jogo lê `<game dir>/Ini/ge3.ini`) e host recusou: "install differs from the host: options"; cliente para de reconectar após recusa. Passou 3/3; controle negativo (opção inalterada, portanto sem recusa) falhou como esperado. Não coberto: arquivos soltos em subpastas `Data`, controles de dificuldade personalizada (local de armazenamento desconhecido), opções mudadas no menu após entrar.

## <a id="2026-10-17-exploration-5-writes-to-npcs-the-host-does-not-process-farwritediag-fables-e2"></a>2026-10-17: exploração 5, gravar em NPCs não processados pelo host (farwritediag, E2 de Fable)

Host sozinho no início; três NPCs a 0,8–1,1 km mortos como host mata por cliente (vida em 0, `OnCheatKill`), outro movido 4 m com `MoveTo`; depois salvar e carregar nativo; depois teleporte do jogo a cada um.

Observado:
- NPCs não processados informam vida 1 e nenhuma tarefa. Após matar: vida 0, não morto, sem tarefa; persiste por 15 s, salvar e carregar.
- Ao chegar (processados novamente), todos os três estavam vivos com vida cheia (600/700) e tarefa de rotina (`ZS_Boss`, `ZS_HangAround`, `ZS_WaitForFreeDestination`). Morte num NPC não processado não persiste.
- Mesma morte alguns segundos após chegar funciona (`ZS_Dead`, dead=1) para todos e continuam mortos quando host vai a 1,3 km e volta ao anel de 200 m.
- Movimento: numa execução, NPC movido (`ZS_HangAround`) ficou no novo local após salvar, carregar e processar; na seguinte, outro (`ZS_Guard`) voltou ao posto (0,8 m do início) quando processado.
- NPCs a 200–240 m foram reposicionados (moveram pouco, por exemplo 0,6–1,4 m) sem receber tarefa: há anel externo onde engine posiciona NPCs pela rotina antes de executar IA.

Deduzido: resultados de região distante não podem ser gravados nas cópias congeladas do host. Devem ficar em diário (por GUID) e ser aplicados quando NPC entra na lista processada de uma máquina, onde caminho existente de morte funciona. Posições dispensam streaming às cópias congeladas; rotinas posicionam NPCs ao ativar.

## <a id="2026-10-17-stage-3c-experience-goes-to-whoever-earned-it"></a>2026-10-17: etapa 3c, experiência vai para quem a ganhou

Encontrado ao repetir etapa 3b: experiência do cliente crescia sem nossa recompensa (e variava de 100 a 250 com ela). Diagnóstico (host mata invasores com próprios golpes, cliente nunca acerta): host +1650 XP, cliente +1250.

Observado (Script_Game.dll, Ghidra): implementação de `GiveXP` chamada diretamente (não por admin de scripts) do script de morte NPC e de nocaute. Ambos recompensam jogador quando assassino é jogador ou seu líder de grupo e `gCNPC_PS::DefeatedByPlayer` do NPC ainda não está definido; depois o definem. No cliente, NPCs espelhados morrem pela tarefa de morte, então todo espelho morto pagava este cliente.

Alterado: cliente define `DefeatedByPlayer` em todo NPC enquanto o espelha (restaurado ao liberar). Host já recompensa assassino real (`SendKilled` -> `GiveXP` na máquina dele).
- Marcar só quando host informou "caído/morto" deixou 500 XP: vida chega antes da flag de morte.
- Após marcar desde o início, +500 restantes vieram 44 ms após missão `Ardea_Revolution` do host mudar: gerenciador do cliente paga recompensas quando estado sincronizado chega. Recompensas de missão para todo jogador mantidas por decisão (comum em cooperativo); suíte 3c desliga sincronização de história para medir só XP de morte.
- Suíte stage3c: 3/3 passaram (XP cliente inalterado com mais de 11 espelhos mortos, XP host cresceu); controle negativo (`xpguardoff`) falhou como esperado (cliente +200).
Também corrigido nas suítes: etapa 3b agora aceita morte de invasor por outro entre solicitações do cliente quando solicitações aplicadas não poderiam matar (7 × 58 < 435 hp), e exige ausência de recompensa do cliente nesse caso; corrida da etapa 5 aceita "já ausente" para coletor mais lento.

## <a id="2026-10-17-static-analysis-by-a-second-agent-codex-dialog-commands-processing-range-clock-death-hero"></a>2026-10-17: análise estática por segundo agente (Codex): comandos de diálogo, alcance de processamento, relógio, morte, herói

Só análise estática (Ghidra somente leitura, SDK); relatórios ficam no ambiente privado. Pontos comparados aos resultados em runtime desta semana estão marcados.
- Alcance de processamento: esfera "ROI" da engine, raio de `ge3.ini` `[Engine.Setup] Entity.ROI` (4000.0 = 40 m nas duas cópias, verificado), console `EntityROI`, `eCEntityAdmin::SetROISphere`; reconstruída com limiar de movimento de 2,5 m e caixas delimitadoras de entidades, compatível com ~45 m medidos (conferido com exploração 1). Centro é câmera ativa, relida a cada quadro, então segundo centro não é possível. `Entity::Teleport` move câmera com herói; `MoveTo` não (compatível com exploração 1). SDK declara `eSSetupEngine::Entity_ROI` como int, binário usa float. Paridade ainda não calcula hash de `[Engine.Setup]`.
- Morte: `Entity::IsDead()` é `AIMode == 9`, `IsDown()` é 8. `OnCheatKill` só para NPC e define tarefa `ZS_Dead` ou `ZS_RagDollDead`; script `Kill` (executado por elas) define AIMode 9 e faz registros: missão `OnNPCKilled`, `GiveXP` protegido por `DefeatedByPlayer`, geração de saque, limpeza de grupo e interação. Explica exploração 5 (NPC distante nunca executa tarefa, portanto nunca morre) e confirma descoberta 3c. `ZS_Dead` com AIMode já 9 segue caminho rápido sem `Kill`. `Entity::Kill()` destrói entidade (compatível com resultado anterior de corpo desaparecido).
- Nocaute executa auxiliar separado (AIMode 8, missão `OnNPCDefeated`, mesma regra XP).
- Comandos de diálogo: não há classes `gCInfoCommand*` nesta versão (hipótese de Fable errada); cada linha de script info é comando string com até duas entidades e dois IDs, despachado por `IS_Running_ProcessInfo` em Script_Game.dll entre 69 comandos (`ECommand` no SDK). `gCInfo_PS::SetInfoGiven` só armazena flag, então sincronizar InfoGiven não reproduz nada. Comandos que mudam mundo incluem Attack, OpenDoor, SetClass, SetPAL, Sleep, flags de diálogo Set*Enabled, SetRevolution/RaidEnabled, Set*Point, SetRoutine, SetGuardStatus, MoveTo, SetSectorStatus, StartRevolution, Spawn, Humanize, JoinNPC/JoinPlayer, GiveAll, ResetCrime, ModReputEnc. Por jogador: GiveXP, SetGameEvent/ClearGameEvent, SetChapter, ModReputPol.
- IDs em runtime: IDs de entidade são aleatórios na construção; `eCNode::SetID`, exportado e protegido, registra entidade novamente com novo ID.
- Relógio: entidade `World_MCP`, conjunto de propriedades de relógio (Year, Day, Hour, Minute, Second, Factor) com setters mantendo relógio interno consistente; floats de "hora do mundo" são HH.MM, não horas decimais; `PlayerSleep` salta relógio, `PS_DuskToDawn` o acelera (fator 3840).
- Registro do herói: nível e XP, pontos de aprendizado, mapa completo de atributos (base e modificador separados), pilhas de inventário com qualidade e dados de aprendizado/ativação, equipamento e atalhos rápidos, arrays de fama política e crimes, eventos de jogo, capítulo; fama e crimes da cidade vivem nas entidades enclave, não no herói.
- Correção (mesmo dia): nossa recompensa nunca funcionou. `GiveXP` recebe self = NPC e other = quem ganha (como script de morte chama); passávamos invertidos, retornava 0 e nada dava (`givexpdiag`: resultado 0; invertido: resultado 1, +50 por escravo). Toda experiência do cliente antes medida na etapa 3b vinha do script de morte do próprio espelho. Com ordem corrigida, assassino recebe uma vez (3b: 0 -> 100 pelo orc). Verificação "experiência do cliente cresceu" da 3b só ganhou significado quando espelhos pararam de pagar.

## <a id="2026-10-17-stage-a-no-game-over-in-co-op-player-death-and-knock-out"></a>2026-10-17: etapa A, sem fim de jogo no cooperativo (morte e nocaute do jogador)

Exploração (herodiag, herodeathdiag) antes da mudança:
- Herói cliente recebia acertos encaminhados como `AddHitPoints` simples: a 0 pontos de vida continuava andando (PS_Normal, AIMode 0) por 30 s ou mais: efetivamente imortal.
- Herói host atingido por orc pelo julgamento do jogo caía a 0 pontos (`ZS_LieKnockDown`, AIMode 8 "caído", estado `ZS_Unconscious_Loop`) e levantava após 5–10 s com 20, depois 30 pontos de vida.
- Caminho de morte (trapaça de matar com orc como assassino): `ZS_Dead`, AIMode 9, `ZS_Dead_Loop` em qualquer máquina; sessão seguia sem pausa, outro lado ainda via boneco, mas jogador nunca levantava (solo exigiria carregar). Estático: script `Kill` imprime `GO_GameOver` (mensagem tipo 13) quando vítima é jogador.

Alterado:
- `downed.cpp`: quando wrapper IA vai executar `ZS_Dead` ou `ZS_RagDollDead` para herói local, para herói e define tarefa de nocaute `ZS_LieKnockDown` (Kill nunca executa: sem mensagem de fim de jogo nem efeitos de missão/XP da morte do herói).
- Acertos de jogador encaminhados pelo host agora carregam atacante (GUID NPC ou ID de jogador quando herói acerta); cliente julga acerto contra próprio herói com arma do atacante (`OnDamage` + `AddHitPoints`), então armadura, tropeços, nocautes e mortes são decididos ali. Protocolo 15.
- Bonecos recebem AniState do remetente (enviado com estado do jogador, protocolo 16) antes de reproduzir movimento: só com nome de movimento, boneco host ficava de pé enquanto cliente jazia nocauteado (StartPlayAni ignorava movimentos deitado no estado de pé; leitura anterior do log dizendo que "boneco os reproduziu" contara movimento informado, não reproduzido).
- Suíte stageA: orc no host bate no herói cliente (12 acertos julgados -> caído a 0 hp -> levanta com 60); host mostra boneco cliente deitado (movimento reproduzido `Hero_LieKnockDown_..._Ambient_Loop`); trapaça de matar em cada máquina resulta em nocaute e herói levanta; sessão intacta. Controle negativo (`downedoff`): herói permanece morto.

Ainda não coberto: monstros atacando herói caído (nenhum perto do início), se humanos roubam herói nocauteado, resgate pelo parceiro (hoje temporizador do jogo o levanta), morte do herói fora do cooperativo (redirecionamento sempre ligado com mod ativo).

## <a id="2026-10-18-stage-a2-a-knocked-out-player-waits-for-a-partner-owners-choice"></a>2026-10-18: etapa A2, jogador nocauteado espera parceiro (escolha do proprietário)

Análise estática (segundo agente, relatório privado): laço de nocaute do herói `ZS_Unconscious_Loop` cura +10 pontos de vida por segundo e chama `ContinueRoutine` após tempo de tarefa passar de 5 s (rotina `Rtn_Player` então o levanta); `ZS_Unconscious_End` é saída só dos NPCs.
Alterado (downed.cpp): enquanto parceiro puder ajudar (conectado, mesmo mundo, não caído), tempo de tarefa do herói nocauteado fica em 0 e vida em 1; parceiro a até 2,5 m por 3 s o levanta (`FullStop`, um quarto da vida, `ContinueRoutine`). Se ninguém puder ajudar (sozinho, todos caídos, parceiro saiu), temporizador do jogo volta a correr. Estados de jogador carregam flag "caído" (protocolo 17).
Mensagens por `GUI2::PrintGameMessage` (hud.cpp; análise estática: tipo 13 é só texto vermelho, não fim de jogo; ~6 s, centralizado): "<Name> liegt am Boden ...", "Du bist niedergeschlagen ...", "<Name> hat dir aufgeholfen."
Suíte stageA2 (3/3; controle negativo `holdoff`: levantou sem ajuda, falhou como esperado): cliente fica caído 20 s ou mais com host a 10 m; host é informado; host ao lado -> levanta com 50/200 hp; ambos caídos -> primeiro levanta sozinho (liberado), outro espera e recebe ajuda.

## <a id="2026-10-18-stage-b-distance-warning"></a>2026-10-18: etapa B, aviso de distância

range.cpp: cliente a mais de 35 m do host recebe "Zu weit vom Host: Hier wird nichts abgeglichen." (laranja), host "<Name> ist weit entfernt (N m)."; abaixo de 25 m ambos recebem liberação; lembrete a cada 60 s enquanto distantes. Distâncias dos estados de jogador; outro mundo conta como distante.
Suíte stageB (3/3 + controle negativo `rangeoff`): cliente movido a 60 m e de volta.
Verificação visual: infraestrutura agora captura janelas do jogo (qa/shot.py, PrintWindow, PNG); mensagem laranja legível nas duas telas (primeiro texto cliente, mais longo, cruzava toda tela e foi encurtado). Visto de passagem: nestas execuções caixa de tutorial "Tipp" fica aberta na tela.

## <a id="2026-10-18-stage-c-world-journal-for-deaths"></a>2026-10-18: etapa C, diário de mortes do mundo

journal.cpp: toda máquina observa NPCs que processa e não espelha (seus arredores); quando um morre ali, informa morte (GUID) ao host (protocolo 18). Host registra e repassa aos outros clientes; suas próprias mortes vão a todos. Morte registrada só é aplicada numa máquina quando ela processa NPC, 0,7 s após entrar na lista (OnEnterProcessingRange do jogo redefine vida antes), com vida 0 e `OnCheatKill`, tendo boneco daquele jogador como assassino (sem experiência na máquina aplicadora). Host nunca espelha NPC com morte pendente; cliente não conduz espelho morto localmente mas vivo no snapshot host.
Suíte stageC: (1) cliente mata Zakosh a 700 m do host; host o tem pendente, vivo e congelado; após teleportar até lá está morto (`ZS_Dead`). (2) Host mata escravo e sai; cliente chegando sozinho (não espelhado) o encontra morto pelo diário. Controle negativo: `journaloff` no cliente.
Limites: só mortes (sem itens, recipientes, nocautes); diário em memória, ainda não salvo com salvamento do host (etapa D); reaparecimento de animais após dias do próprio jogo segue normal.
- Correção (etapa C, mesma noite): aplicar morte registrada com trapaça executava script `Kill` também na máquina aplicadora: cliente ganhava experiência pelos invasores do host (800 XP na 3c) e gerenciador de missões concluía invasão sozinho (+500). O mesmo valia para mortes espelhadas (tarefa `ZS_RagDollDead` -> `Kill`), que só passavam 3c pelo momento de execução. Ambos agora definem morte como estado: vida 0, AIMode 9, depois `ZS_Dead`, que com AIMode já 9 só deita corpo (análise estática). Progresso de missões, experiência e saque vêm só da máquina da morte (compartilhados por história e recipientes). Custo: NPCs espelhados não caem mais como ragdolls; deitam imediatamente.

## <a id="2026-10-18-stage-d1-the-journal-and-puppets-with-the-games-own-save"></a>2026-10-18: etapa D1, diário e bonecos com salvamento do próprio jogo

persist.cpp intercepta `gCHUDFileManager::SaveGame` e `LoadGame` de Game.dll (ambos começam com 9 bytes de instruções completas independentes de posição; salto de 5 bytes ao mod, 9 bytes executados de trampoline; prólogos verificados antes, outras versões recusadas). Todo salvamento, pelo menu ou QA, agora remove bonecos antes: anteriormente, salvar no menu com jogador remoto presente manteria segundo herói e abortaria ao carregar ("current world has more than one hero!", exploração 3). Após salvar com sucesso, grava `<save>.g3t` (diário, uma linha por morte); carregar substitui diário pelo desse arquivo (nenhum se ausente). Suíte stageD1: cliente mata NPC distante, host salva com boneco presente, carrega, morte ainda registrada e aplicada ao chegar lá. Controle negativo `persistoff`.
Não verificado: se botão de salvar do menu passa por `gCHUDFileManager::SaveGame` (presumido; hook na função também chamada pelo salvamento QA).

## <a id="2026-10-18-stage-d2d3a-each-players-own-hero"></a>2026-10-18: etapa D2/D3a, herói próprio de cada jogador

hero.cpp grava e lê registro de herói: nível, experiência, pontos de aprendizado, valores base e máximos de atributos (tags STR DEX INT ALC SMT THF HP MP SP), toda pilha de inventário (ID template, quantidade, qualidade, slot equipado, categoria; habilidades aprendidas são ensinadas novamente). Restauração: desequipar e excluir pilhas (não habilidades), criar e equipar registradas, depois níveis, experiência, pontos e atributos.
- stageD2 (host sozinho): registrar; depois espada, experiência e ferimento mudam herói; carregar registro devolve exatamente resumo registrado (nível, xp, lp, atributos, hash de inventário). Negativo `herorestoreoff`.
- D3a: quando host salva, avisa cada cliente (protocolo 19); cada um grava registro próprio para aquele nome; cliente carregando esse salvamento recebe registro 3 s após mundo executar. stageD3a: herói cliente (espada, +150 XP) difere do host; host salva; cliente carrega cópia do salvamento do host e tem próprio herói (resumo idêntico), não o do host. Negativo `herorestoreoff`.

Ainda não coberto: salvamento viajar automaticamente ao cliente (copiado pelo teste), participante novo sem registro (recebe cópia do herói host), posição, atalhos rápidos, efeitos ativos, fama política e reputação de cidade nas entidades enclave.

## <a id="2026-10-18-stage-d3b-joining-a-campaign-over-the-network"></a>2026-10-18: etapa D3b, entrar na campanha pela rede

Campanha atual do host é último salvamento carregado ou gravado. Quando cliente conecta (só então: salvamento posterior nunca força jogador conectado a carregar), host envia três arquivos (`.g3savcpx` ~66 KB, `.g3savcpxdat` ~2,1 MB, `.g3t`) em blocos confiáveis ENet de 16 KB com tamanhos e CRC-32s (protocolo 20). Cliente verifica, armazena como `G3T_host_<name>.*` (nunca sobre salvamento próprio; registros de herói usam mesmo nome) e carrega sozinho; seu registro próprio, se existir, é aplicado por cima. Primeira vez na campanha: herói já em jogo (novo jogo antes de entrar) é mantido como registro do jogador; no menu principal não há nenhum e jogador recebe cópia do herói host no salvamento (informado na tela).
Suíte stageD3b: host pega poção do mundo e salva; cliente inicia e fica no menu principal; 0,4 s após iniciar, campanha chegou, carrega, cliente executa em G3_World_01, poção também ausente ali, host vê cliente. Controle negativo `campaignoff` (host nada envia).
Também corrigido na infraestrutura: segundo jogo só inicia após primeiro liberar trava de instância única (`releaselock`, como join_both); arquivos de testes anteriores removidos antes (arquivo auxiliar antigo fizera controle negativo D1 passar).
Repetições (mesma noite): D3b 3/3 + negativo, D3a 3/3 + negativo, negativo D1 falha como deveria após corrigir arquivo antigo; regressão completa de etapas anteriores verde na compilação D.

## <a id="2026-10-18-stage-g-one-time-of-day"></a>2026-10-18: etapa G, um horário do dia

clock.cpp: host envia relógio do jogo (propriedades de relógio World_MCP: timestamp, ano, dia, hora, minuto) a cada 5 s (protocolo 22); cliente divergindo mais de 120 segundos de jogo (relógio corre no fator 12, então intervalo de atualização é 60 segundos de jogo) é ajustado pelos próprios setters (`PSClock::SetYear/SetDay/SetHour/
SetMinute`). Suíte stageG: host avança relógio seis horas (12:07 -> 18:07); 12 s depois cliente mostra 18:10 como host (2 segundos de jogo separados). Visto de passagem: cliente que começou novo jogo depois já fora corrigido duas vezes ao entrar. Controle negativo `clockoff`.
Consequência: dormir no cliente é desfeito pelo relógio host em 5 s (sono só no host por enquanto).
Resultados G: 3/3, negativo (`clockoff`: 21599 s separados) falhou como esperado; regressão amostral das etapas próximas à rede (2, 3a, 3b, A2, B, C, D3b, 4, 5b, savediag) verde.

## <a id="2026-10-18-stage-g2-a-sleep-moves-time-on-for-everyone"></a>2026-10-18: etapa G2, dormir avança tempo para todos

Cliente cujo relógio salta mais de 1800 segundos de jogo num quadro (dormir, esperar) envia horário ao host (protocolo 22); host avança se pedido for posterior ao próprio horário (nunca volta) e envia imediatamente; correções do próprio cliente vindas do host não contam como salto. Suíte stageG2: relógio cliente salta 12:08 -> 18:08; em 8 s host está em 18:10 como cliente (1 s separados). Negativo `clockoff`.
Não coberto: diálogo real de cama/sono (salto feito pelo comando QA; análise estática diz que `PlayerSleep` salta igual), recuperação de vida ao dormir (fica na máquina de quem dorme).

## <a id="2026-10-18-stage-h-dialog-effects-on-the-world"></a>2026-10-18: etapa H, efeitos de diálogo no mundo

Exploração (infodiag): wrapper IA vê `IS_Running_ProcessInfo`, que executa cada linha de script de diálogo na máquina da conversa (sua unidade de processamento é a de World_MCP). `PSInfoManager::GetCurrentCommand()` na entidade mundo fornece linha: comando, entidades 1 e 2, IDs 1 e 2. Diálogo de Diego do cliente na 4c executou `Say` ×4, `SetGameEvent Diego_WarIsLost`, `End`: evento só definido no herói cliente.
- H1: eventos de história (PlayerMemory.PlayerKnows do herói, definidos por SetGameEvent, limpos por ClearGameEvent) são terceiro domínio de história junto a missões e informações (protocolo 23); eventos limpos viajam como 0. Suíte stageH1: definir no cliente -> conhecido no host, limpar -> ausente, definir no host -> conhecido no cliente. Negativo: história desligada.
- H2: após comando de diálogo mudar primeira entidade (SetClass, SetPAL, Set*Enabled, Set*Point, FullStop, SetRoutine, SetGuardStatus, MoveTo, SetRevolution/RaidEnabled, StartRevolution, Humanize, JoinNPC, JoinPlayer), máquina executora lê estado resultante 0,7 s depois (flags de diálogo, guarda, classe, alinhamento político, imortalidade, nome de rotina, posição, invasão/revolução/estado enclave) e envia (protocolo 24); host repassa; toda máquina define sua cópia (mudança reinicia rotina salvo NPC espelhado; posição só para não espelhados). SetSectorStatus envia estado resultante do setor. Repassar resultado em vez do comando evita interpretar formatos de argumentos.
  Não coberto: Attack, Spawn, Give/Grant/GiveAll/Erase (inventários), OpenDoor, vínculo de grupo de JoinNPC / JoinPlayer (só campos de estado), ResetCrime, reputação.

## <a id="2026-10-18-soak-test-25-min-of-mixed-player-actions"></a>2026-10-18: teste prolongado (25 min de ações variadas de jogadores)

Nova suíte `soak`: host e cliente fazem mistura aleatória com semente de caminhada (goto IA), separar 60 m e reunir, acertos, coletas, quedas com ajuda, resultados de diálogo, sono, salvar e carregar, verificando saúde após cada ação e registrando conjunto de trabalho de ambos os processos.
Primeira execução: host falhou após cerca de um minuto de ações: EXCEPTION_ACCESS_VIOLATION em Game.dll no RVA 0x117C09, `gCNavZone_PS::DetectCollisionCircleExit` chamado com zona de navegação nula (ECX=0), enquanto herói host executava goto IA e boneco cliente andava após cliente saltar 60 m e voltar. Reprodução de 20 ciclos exatamente dessas duas ações (`navdiag`) não falhou. Causa não comprovada.
Encontrado no log: host aceitara estados completos de NPC (inclusive posições) enviados pelo cliente após resultados de diálogo (simulados no teste) enquanto cliente estava longe com cópias antigas; host recolocava próprios NPCs em movimento em locais antigos. Corrigido: posições só viajam após comando MoveTo (protocolo 25), e campos enclave são gravados pelos membros gCEnclave_PS. (Toda execução desde etapa 1 também registra oito "Cannot get property 'Status' in propertyset 'gCEnclave_PS'" do próprio jogo; não relacionado.)
Continuação (mesma noite): falha reproduz com host sozinho, sem cliente nem boneco (`gotodiag2`: herói enviado pelo goto IA do próprio jogo, `Entity::StartGoto`, a pontos aleatórios de círculo de 15 m em Ardea). Rastreio da navegação mostrou entidade de zona (gCNavigation_PS +0xac) como `Nav_NavZone 1 Edge` logo antes; `gCNavigationMap::DetectEvades` pede zona de navegação dessa entidade e chama DetectCollisionCircleExit sobre resultado nulo. Portanto não é falha cooperativa, mas goto para pontos arbitrários (ação QA; jogo só envia herói a pontos válidos de interação). Se jogo sem mod falha igual não foi testado (bot exige mod). Ação de caminhada agora usa pequenos passos diretos.
Resultado depois: 22 minutos, 320 ações (102 rajadas de passos, 40 acertos, 34 cargas, 28 salvamentos, 27 coletas, 24 sonos, 23 quedas com ajuda, 22 resultados de diálogo, 20 separações), nenhuma ação falha, ambos ativos e vendo-se sempre, encerramentos limpos, salvamentos reais intocados. Conjunto de trabalho: cliente estável (1006 -> 1021 MB), host 1150 -> 1220 MB após aquecimento em 34 cargas (não demonstrado vazamento; observar sessões maiores).
Teste longo (55 min, 738 ações: 232 rajadas de passos, 101 acertos, 75 cargas, 59 salvamentos, 60 sonos, 57 coletas, 55 quedas com ajuda, 53 separações, 46 resultados de diálogo): passou, sem ação falha, encerramentos limpos. Conjunto de trabalho: host 1144 MB após aquecimento, 1260 MB no meio, 1246–1279 MB no fim (estabiliza); cliente ~1000–1015 MB.

## <a id="2026-10-18-stage-h3-the-rest-of-the-dialog-effects-puppets-could-not-be-hit"></a>2026-10-18: etapa H3, demais efeitos de diálogo; bonecos não podiam ser atingidos

Varredura dos scripts de toda opção de diálogo (`infoscan`): perto do início Milten e Diego dão itens (Give), Hamlar GiveAll, Topork desafia duelo (`Attack npc player Duel`, missão Topork_Duell), Lester entra (`JoinPlayer npc true`, exige evento GetLester). `Spawn` não usado em diálogo algum; `JoinNPC` também não.
- Itens (Give/GiveAll/Erase): lado do NPC é majoritariamente criado na hora; quem conversa recebe item, outros não, comportamento cooperativo desejado. Inventários das cópias NPC não sincronizados.
- Lutas (H3b): comando Attack executa script de percepção `AssessTarget` (self = atacante, other = alvo, args = gEAttackReason: Duel 17, Enemy 12, ...; análise estática Script_Game.dll). Cliente conversando com NPC do host envia a ele, que chama AssessTarget contra boneco do cliente ao terminar retenção do diálogo (protocolo 26). Suíte stageH3b: cliente conversa na opção de duelo Topork (outro orc, Hamlar, interrompeu ameaçando numa execução: teste conversa de novo até parceiro ser Topork), Topork do host ataca.
- Encontrado no caminho: **NPCs do host nunca conseguiam atingir cliente.** Topork atacou boneco (estado ZS_Attack_PowerAttack, alvo = boneco) por 20 s sem acerto: bonecos criados sem colisão (etapa 2, quando reposicionados todo quadro), então arma alguma tocava. Com colisão, 13 acertos em 20 s chegaram ao herói cliente. Até agora todo acerto host→cliente das suítes vinha do comando QA.

## <a id="2026-10-18-stage-e-regional-ownership-npcs-far-from-the-host-companions"></a>2026-10-18: etapa E, autoridade regional (NPCs distantes do host; companheiros)

Cada NPC é simulado numa máquina, sua proprietária; as demais o espelham (protocolos 27 a 29).
- E1: cliente envia ao host NPCs que processa e ninguém lhe envia (sua região); host repassa; quem simulou primeiro mantém NPC (snapshots de cliente de NPC enviado pelo host são recusados; host para de enviar NPC que espelha). Host conduz espelhos de clientes só enquanto os processa. Quando proprietário para de enviar (saiu), espelho fica obsoleto após 3 s e outra máquina o simula. Suíte stageE1: cliente em Zakosh controla 37 NPCs; host chega e espelha 35 (owner 2) em vez de executá-los duas vezes; posições coincidem (mediana 0 cm, NPCs andando até 2,6 m); cliente sai e host retoma todos os 35. Negativo: `ownoff`.
- F/E2: regras de acerto únicas em toda máquina: acerto por corpo simulado em outro lugar (boneco, NPC espelhado) descartado (proprietário decide); acerto do nosso herói em NPC simulado alhures vai ao proprietário, que aplica e mata (morte paga nosso herói por SendKilled); acerto no boneco de outro jogador vai àquele jogador e é julgado contra herói real (agora nos dois sentidos, retransmitido pelo host). Suíte stageE2: na região cliente, herói host mata NPC do cliente em 11 acertos no cliente e recebe experiência; NPCs do cliente atacam host sozinhos e seus acertos chegam ao herói (8–10 por execução). Negativo: filtro host desligado. "Assassino" agora é próprio NPC, não boneco remetente: boneco removido logo após morte (jogador saiu) derrubou cliente em eCEntity::QueryEntityProxyInternal a partir dos estados do NPC morrendo.
- E3: companheiros. Estado de seguir do jogo (ZS_FollowPlayer_Loop) segue `GetPlayer()`, herói local. Cliente que recruta NPC host (JoinPlayer true no diálogo) assume controle: deixa de espelhar (IA própria novamente, ZS_FollowPlayer); host deixa de enviar e espelha snapshots cliente; JoinPlayer false ou saída devolve controle. Suíte stageE3: cliente recruta Lester; host o mostra como do cliente (owner 2); cliente anda 12 m e Lester segue nos dois. Negativo: resultados de diálogo não repassados.

Ainda não coberto: lutas NPC contra NPC entre proprietários (descartadas), companheiro após salvar/carregar, 3+ jogadores.
- Remover boneco durante luta NPC contra ele derrubou cliente duas vezes na E2 (host sai em combate; violação de acesso em SharedBase sob estado IA executado no wrapper, Game.dll+0x169724 na pilha, logo após "puppet 1 removed"). Correção: antes de destruir boneco, todo NPC o descarta como alvo atual, alternativo, atacante atual/anterior e alvo de magia; os que o perseguiam reiniciam rotina (Forget de remote.cpp). Lição para qualquer mod cooperativo: destruir corpo proxy exige mesma limpeza que jogo faz com entidades próprias.
- Regras de solicitação após revisão estática do diff E1–E3 (segundo agente): primeiro jogador que recruta mantém NPC, segundo pedido recusado (host -> jogador, WorldState tipo 6); só snapshots de quem reivindicou são aceitos; devolver (JoinPlayer false) descarta espelho host imediatamente e cliente deixa de enviar por 5 s; reivindicação sem snapshots por 15 s (ou jogador que saiu antes do primeiro) termina, e jogador conectado é informado (tipo 6). stageE3 agora também devolve Lester e verifica retomada de reivindicação silenciosa.
- E4, NPC contra NPC na fronteira regional (protocolo 31): acerto de nosso NPC em NPC simulado alhures vai ao proprietário da vítima (HitNpcMsg carrega GUID do atacante), que aplica usando seu espelho do atacante; letal mata como solicitação de jogador, mas não paga ninguém (DefeatedByPlayer marcado antes). Caminho é laço de combate IA (Game.dll gCScriptProcessingUnit::sAICombatMoveItlLoop -> AddHitPoints) ou dano de contato (gCTouchDamage_PS::TriggerTarget -> gCEntity::DoDamage); ambos terminam em AddHitPoints, onde está filtro (análise estática, segundo agente). Suíte stageE4: Lester do host, movido à região cliente, ataca Zakosh do cliente (AssessTarget, motivo Enemy): Zakosh 600 -> 325 pontos no cliente, espelho host acompanha, e acertos de NPCs cliente em Lester voltam ao host. Negativo: `npchitsoff`.
- Segunda revisão estática (segundo agente), corrigido: luta de diálogo pendente descartada se alguém entrou nesse meio-tempo (IDs de jogador reutilizam slots), jogador saiu ou mundo mudou; reivindicações de companheiros do cliente terminam com conexão, e toda reivindicação termina com mudança de mundo/carga; acerto NPC cujo atacante não resolve no proprietário é descartado em vez de atribuído à vítima.
- Corrida de relógio (G2 falhou uma vez na regressão final): atualização host no mesmo quadro do salto de sono cliente, antes da verificação por quadro, voltava relógio e perdia sono. Verificação agora também executa quando atualização chega; por 5 s após pedir avanço ao host, cliente não volta seu relógio.
- Lições QA da regressão final: suposição anterior à autoridade regional (todos NPCs do host) falhou 3a uma vez (batedor primeiro processado pelo cliente permanece dele); como bonecos colidem, invasão inicial feriu cliente entre dois dumps de herói (D3a agora limpa invasão antes); saque aleatório deixou cadáver vazio (5b agora escolhe um com conteúdo); teleporte QA de 700 m uma vez nunca retornou no jogo (cliente travado sem exceção, mesma família da falha goto IA: ferramenta QA, não mod).
- Missões e companheiros, descobertas estáticas (segundo agente, Ghidra): gCQuest_PS::OnNPCKilled conta mortes pelo nome da vítima (DeliveryEntities / DeliveryCounter / DeliveryAmounts), não verifica assassino nem protege contra segunda chamada; JoinPlayerSlavery define líder = GetPlayer(), Waiting = false, PartyMemberType = Slave (3); gCParty_PS é salvo (GetSaveGameRelevance = 2). Consequências: morte na região cliente só conta no gerenciador dele salvo host contar; companheiro recrutado no cliente não é de ninguém no salvamento host.
- Terceira revisão (segundo agente) no estado comitado, avaliado para dois jogadores:
  - Companheiros ligados a jogadores por nome. Com dois há só um cliente, então conflito de nomes impossível; cliente que muda nome entre salvar e entrar perde companheiro (documentado).
  - Luta de diálogo pendente descartada por entrada não relacionada só importa com 3+ jogadores.
  - Arquivo auxiliar lido antes do retorno da carga nativa; se falhar, diário e companheiros podem vir do salvamento falho. Improvável, mantido como conhecido.
  - Crédito de missão host pode se perder se NPC não resolver no host ao chegar morte. Todos NPCs do mundo resolvem por GUID mesmo sem processamento (diário depende disso), então risco baixo.
  - stage5b ignorava silenciosamente verificação de coleta tardia sem cadáver com saque; agora falha.
- Etapa Q encontrou falha: contar morte cliente nas missões host com cópia host ainda viva (último invasor inicial) concluía missão com NPC em pé; host falhou em Script.dll dois segundos depois (E5, uma vez). Agora só conta quando NPC morto também em seu lado (NPC não processado pelo host conta imediatamente, estará morto quando host chegar).
- Revisão final Q/E5 (segundo agente), casos extremos mantidos após primeiro teste humano: estado auxiliar aceito antes do retorno nativo (sem reversão se carga falha); contagem pendente de missão não salva nele; morte de NPC não resolvível no host não repetida; host entrega companheiro salvo antes de cliente confirmar adoção (se falha, solicitação expira e é oferecida de novo, 15/20 s); companheiros ligados pelo nome exibido.
- 2026-10-18: issue de reivindicação publicada pelo proprietário: https://github.com/cranebeaker/coop-anything/issues/16

## <a id="2026-10-18-first-human-look-owner-two-windows-on-one-pc--what-the-bots-missed"></a>2026-10-18: primeiro olhar humano (proprietário, duas janelas num PC) — o que bots não viram

- Inimigos host nunca escolhiam boneco cliente como alvo (0 de ~40 escolhas medidas depois por dump de alvo por NPC); cliente não podia ser ferido. Todo teste anterior "NPC atinge cliente" forçara ataque (agressividade QA, duelo por diálogo). Correção em teste: boneco entra no grupo do herói local (como companheiros); inimigos então o escolhem e acertam cliente.
- Cliente não via lutas: NPCs espelhados andavam desarmados, sem postura de combate, e ataques não apareciam. Inventários dos espelhos vazios (própria IA que preenche equipamento nunca executou; AssureAll congelou cliente), então armas empunhadas devem ser criadas e postas na mão (HoldStacks) pelo snapshot do proprietário; postura (AniState) também viaja. Armas agora coincidem; ataques ainda recaem principalmente no laço ambiente da postura (aberto).
- Lição ao guia: QA por bot deve conferir também o que outro jogador vê (animação, itens empunhados, postura) e comportamento IA espontâneo (inimigo escolhe remoto sozinho), não só dados replicados.

## <a id="2026-10-18-why-enemies-ignored-the-remote-player-and-the-fix-stage-v1"></a>2026-10-18: por que inimigos ignoravam remoto e a correção (etapa V1)

Análise estática (segundo agente, Ghidra, Script_Game.dll; detalhes privados):
- NPCs escolhem alvos em scanner chamado por `AssessActivePerception` (RVA 0x295F0 / 0x92F0). Percorre `Entity::GetNPCs()`, consulta script `GetAttitude(self, other)` **por nome** para cada NPC e mantém entidade mais próxima por atitude (Hostile/Predator atacadas por `AssessTarget`, Angry ameaçada, Panic provoca fuga).
- Jogador só é especial pela identidade com `Entity::GetPlayer()`: slot fixo (atacado quando `IsUpset`) e ramo próprio de atitude (`GetAttitudeToPlayer`: crimes e fama por facção). Segundo NPC `PC_Hero` recai nas tabelas de alinhamento político e espécie. Para orcs contra humano com alinhamento None ambas dão 0: nunca alvo.
- Grupo (líder = jogador) sem ramo em `GetAttitude`; companheiros julgados por facção própria.

Observado (linha QA `NEARX end`): boneco em `GetNPCs()`, alinhamento 0, espécie 0 (humano), modo IA 10. Correção: envolver script `GetAttitude` (trocar `gSScript::m_funcScript`); quando `other` é boneco, chamar original com herói local. Boneco deixa de entrar no grupo (isso o punha na lista de seguidores). Resultado: com wrapper orcs escolheram boneco toda execução; desligado (`attitudeoff`), nenhuma.
Novo problema: orc mirando boneco desarmado frequentemente só vira e anda (`ZS_Attack_TurnLeft/Right`, `Goto`, `GoBack`) e nunca golpeia (1 de 7 execuções com acerto ao colocar cliente junto de orc livre); cliente com espada teve acertos em 2 de 3. Chamadas diretas (não por nome) de `GetAttitude` (29 funções, por exemplo `OnAttack`) ainda veem atitude 0; se isso ou postura do alvo causa espera está em investigação.

## <a id="2026-10-18-attack-motions-on-mirrors-and-puppets-stage-v2-the-motion-owner"></a>2026-10-18: ataques em espelhos e bonecos (etapa V2): proprietário do movimento

Estático (Ghidra): movimentos de combate (`gCScriptProcessingUnit::sAICombatMoveStart`, Game.dll RVA 0x16ABB0) tocam no slot 0 e depois chamam `eCVisualAnimation_PS::SetMotionOwner(0, 5)`; animações de script (`sAIPlayAniStart`) definem owner 4; `Entity::StartPlayAni` (Script.dll RVA 0x166F0), usado para reproduzir nome recebido, define owner 6. Enumeração de proprietário sem nome no SDK.
Observado (stageV2, contadores cliente, duas execuções cada): após `StartPlayAni`, movimento está no slot 0 imediatamente em 99,7% dos inícios, então nome encontrado. 150 ms depois permanece em 11–12% com owner 6, e 93–94% definindo owner 5 logo após `StartPlayAni` (716/764, 849/916). Algo fora dos estados IA substitui movimentos slot 0 cujo proprietário não é "combate" pelo laço ambiente; owner 5 os mantém.
Continuação (mesma noite): espera era culpa do teste. Suíte colocara cliente 2,5 m ao lado de orc livre num deslocamento fixo, possivelmente em parede ou telhado; orc só andava e virava. A 1,5 m do orc na linha ao herói host (chão transitável), orc golpeou boneco desarmado em 4 de 4 (HackAttack, PowerAttack, QuickAttack) e acertos chegaram ao cliente; negativo (`attitudeoff`) 0 alvos. Wrapper agora salta do `GetAttitude` nativo (Script_Game.dll RVA 0xE3B0, prólogo de 6 bytes `55 8B EC 83 E4 F8`), então 29 chamadores diretos também veem boneco como herói; entrada da tabela de scripts aponta à mesma função. Efeitos colaterais nesses chamadores (dano, comentários, preços) sob revisão estática.
Regressão após correção (32 suítes): três verificações presumiam inimigos ignorando cliente e foram ajustadas (contar só golpes cliente que acertam; escolher orc simulado pela própria máquina; ignorar item de mãos nuas `Fist`, que NPC desarmado segura e nunca é saque). Todas 32 verdes depois. Pacote G3Together-2d73cde.

## <a id="2026-10-18-late-owners-second-look--t-pose-and-attacks-done-the-games-way"></a>2026-10-18 (tarde): segundo olhar do proprietário — pose T e ataques pelo caminho do jogo

- Proprietário viu orcs em pose T no cliente. Correção V2 anterior (owner 5 slot 0 após `StartPlayAni`) mantinha nome enquanto nada executava: com `IsMotionRunning(0)` como medida, ~80% dos espelhos cliente sem movimento ativo (host 1–6%). Lição: medir se movimento executa, não qual nome está no slot.
- Nenhum owner funciona sozinho (1, 3, 4: 0 de ~130 ataques host executando no cliente; 5 congela): owner 5 avança pelo laço de combate SPU (`sAICombatMoveItlLoop`), que nada conduz num `StartPlayAni`.
- Correção: reproduzir ataques, defesas e cambaleios como movimento de combate do próprio jogo: `gCScriptProcessingUnit::
  sAICombatMoveInstr(new sAICombatMoveInstr_Args(self, nullptr, action, phase), &routine->GetSPU(), false)` no espelho, ação e fase extraídas do nome (`Orc_Stand_None_2H_P0_PowerAttack_Hit_...`), sem alvo. `Recover` separado fica a cargo do movimento ativo (iniciar um causava falha ocasional). Resultado: espelhos sem movimento ativo 1–4%, 37–55% dos ataques host vistos executando no cliente (era 0).
- Golpes dos jogadores (bonecos) iguais: invasão limpa, 14/15 e 15/15 vistos na outra máquina, 0/15 sem correção. Golpe bot: definir tarefa `PS_Melee` e estado `PS_Melee_Attack`, como `OnPlayerAction` numa tecla.

## <a id="bows-and-spells-ranged-qa-tools-checked-agent-b-2026-10-19-pair-2-run-20261019-181053-together-p2"></a>Arcos e magias, ferramentas QA à distância conferidas (agente B, 2026-10-19, par 2, execução 20261019-181053-together-p2)

Observado (`rangeddiag`, branch agent-b em 9deb53d, ambos os sentidos):
- `inventory`, `ready`, `aimat` (Target), `mana`, `flying` respondem como esperado: arco mais flechas empunhados, magia `It_Spell_Meteor` empunhada (use 15), corpo virado ao alvo a 12 m, foco definido, mana 200/200.
- `act PS_Ranged-PS_Ranged_Aim` / `PS_Ranged_Shoot`: tarefa e estado definidos, uma flecha por tiro aparece no atirador (projéteis 1, 2, 3; flechas na barra 50 a 47). Alvo nunca ferido (200/200 em todas as máquinas, ambos os sentidos), sem experiência. Observador nunca tem projétil (0 contra 3 do atirador).
- `act PS_Magic-PS_Magic_Loop`, depois `PS_Magic_Cast`: estado definido, mas sem meteoro (`Smn_*` 0), sem projétil novo, mana 200: magia não lançada.
- Capturas: caixa tutorial "Tipp: Die Orks wurden besiegt" aberta nas duas máquinas durante lançamentos; no cliente herói visivelmente ainda segura espada após `ready It_Spell_Meteor`; câmera host aponta ao céu.

Deduzido, não testado: caminho do jogador mira com câmera, não corpo nem foco, então flechas voam para onde câmera olha (explica erros). Se caixa aberta ou falta de animação bloqueia magia: desconhecido. Nomes usados existem em Script_Game (`PS_Ranged_*`, `PS_Magic_*`), assim como `_AI_Shoot`, `_AI_Cast`, `_AI_Cast_Begin`, `_AI_Cast_Execute`, `_AI_StartCastPhase`, `MagicProjectile`, `MagicMeteor`, `MagicSummon*`: próximo passo é caminho NPC.

## <a id="bows-and-spells-step-2-shooting-and-casting-by-the-games-scripts-agent-b-2026-10-19-pair-2"></a>Arcos e magias, passo 2: atirar e lançar pelos scripts do jogo (agente B, 2026-10-19, par 2)

Estático (Script_Game, detalhes privados): estados de jogador e IA NPC terminam no mesmo código. Fase 5 de `_AI_StartCastPhase` executa `FuncOnCast` da magia, senão por `SpellType` `MagicProjectile`/`MagicInstant`/`MagicSummon`, com self = conjurador, other = alvo, int = pilha de inventário; mana paga na fase 2. Flecha disparada pelo script `Shoot` (PS_Ranged.cpp, também chamado de `ZS_Attack_Loop`): cria flecha nova na mão e, só se atirador é `Entity::GetPlayer()`, mira no centro da tela da câmera (caminho físico); para outros voa em linha com `SetTarget(other)`. Boneco reproduzindo `Shoot` portanto segue ramo NPC sozinho.

Observado (suíte `rangedbot`, execuções 20261019-182204 a -190738-together-p2, ambos os sentidos):
- Meteoro (`castat`: magia e alvo no conjurador, mana mínima, depois FuncOnCast): `Spl_Meteor`, FuncOnCast `MagicSummon`, cria `Smn_Meteor`, 130 mana. Em toda execução e sentido: alvo morto no host (proprietário), conjurador +50 XP, inclusive meteoro cliente em aldeão do host. Observador nunca tem entidade `Smn_Meteor` (0 contra 1 do conjurador).
- Bola de fogo (`MagicProjectile`, `Mis_Fireball`, 15 mana): do host matou alvo; do cliente não feriu.
- Arco (`shootat` = script `Shoot`, depois flecha redirecionada, deixada ou substituída): recarga e aljava funcionam (50, 49, 48). Flecha geralmente para a 1–2 m da mão, mesmo na mira da câmera. Acertos só do host (3 e uma morte numa execução, uma morte noutra). Desativar colisão do arco empunhado nada mudou. Causa desconhecida.
- Descoberta lateral: no cliente, orcs mortos pelo host apareceram de pé com armas em duas capturas (lista NPC de ambas: mortos, `ZS_Dead`/`ZS_RagDollDead`).

## <a id="p1-summons-the-meteor-first-agent-b-2026-10-19-pair-2-commit-3b91686-protocol-36"></a>P1 invocações, meteoro primeiro (agente B, 2026-10-19, par 2, commit 3b91686, protocolo 36)

Observado: `Smn_Meteor` é entidade breve (cerca de 1 s) criada por `MagicSummon` na pose do alvo, conjuntos ScriptRoutine, Interaction, Damage, Effect2; proprietário Interaction é conjurador. Acertos chegam a AddHitPoints com meteoro como fonte (other), então atacante do filtro (proprietário da fonte) é conjurador.
Abordagem: máquina conjuradora envolve `MagicSummon`, encontra nova invocação um quadro depois (nome de template, proprietário = conjurador), dá ID de rede (id conjurador << 24 | contador) e anuncia (item de magia, template, pose, GUID alvo); fim também anunciado. Outra máquina reproduz `MagicSummon` no boneco conjurador com mesma magia; cópia pertence ao boneco e acertos descartados pela regra 1 do filtro (acertos por bonecos). Sem alvo ali, template criado na pose do conjurador. Cópia removida 1,5 s após fim do original.
Suíte `stageP1` (cliente lança, depois host, em aldeão simulado pelo host): 3× verde (DLL 37bbc731...): cópia ligada no observador, do boneco, nenhum acerto aplicado (bloqueios em escravos, Milten, Hamlar, chefe orc), alvo perdeu vida uma vez no host, morte deu +50 XP ao conjurador. Negativo `summoncopyhero` (cópia do próprio herói observador) vermelho: cópia matou alvo no host segunda vez (delta -2548 aplicado). stage2, stage3a, stageA, stageT verdes na mesma DLL.
Ainda não coberto: invocações longas (esqueleto, golem, demônio: NPCs exigindo espelhamento de movimento), entrada tardia ou observador carregando área após magia, salvar/carregar com invocação existente.

## <a id="2026-10-19-agent-a-merges-and-regressions-summary"></a>2026-10-19: agente A, mesclagens e regressões (resumo)

### <a id="observed-3"></a>Observado

Arcos, magias e P1 (agente B) estão nas seções anteriores.

- V5 (commit `7ed76c4`): `GetAttitude` responde Panic quando self foge e alvo é other. Wrapper substituía boneco antes da verificação, então NPC fugindo o julgava hostil. Agora preservado; `stageV5` 3/3, negativo `fleekeepoff` falhou.
- Movimentos espelhados (commit `6a768af`, diagnóstico `syncdiag`): gestos e quedas iniciados com `StartPlayAni` substituídos pela postura em 150 ms (4 de 91 e 4 de 77 ainda apareciam). Como instruções play-ani na unidade de scripts do corpo: 98 de 98 e 54 de 55. Espelhos da aldeia sem nada executando: 1–5 de 80–100 (antes 19–26).
- A2 refeita conforme proprietário (commit `b2d6c54`): ajudar custa uma poção de cura; único template de poção encontrado em runtime `It_Potion_Health`; ninguém capaz de ajudar por 5 s significa morte como solo. `stageA2` 3/3, negativo `potionoff` falhou. Na segunda execução, acerto substituiu tarefa de morte; agora definida novamente.
- Regressão completa (série `20261019a`, 37 suítes): 36 passaram. `stage2` falhou uma vez: boneco cliente executou `ZS_HangAround` no host por ~2 s e virou após cambalear. Visto em 1 de 15 execuções naquela DLL, nunca em 80 anteriores.
- Transformações (commit `bce0585`): após `StartTransform`, `Entity::GetPlayer()` é criatura (`Wolf`, `Bloodfly`), enquanto `gCSession::GetHero()` continua corpo humano oculto; mod enviava humano. `stageT` 3/3 (Wolf duas vezes, Bloodfly uma), negativo `shapeoff` falhou.
- Dois agentes paralelos (commits `02d3c1c`, `c5c84cb`, `9deb53d`): segundo par de cópias na porta 34568, trava QA e pasta próprias; cada agente em sua worktree git e branch. Jogos do segundo par encerravam com código 0 ao iniciar porque jogo do outro mantinha `GenomeMutex`. Correção: todo jogo libera handle assim que bot responde, e saída precoce é repetida. Sonda paralela: 5 de 6 verdes; vermelha era giro conhecido `stage2`.
- Monitores de invariantes (commit `05444a6`): verificações só informativas ao fim de toda suíte com dois jogadores. Autoteste `invariantself` informa `double_sim` quando cliente para de receber snapshots (`20261019-175827-together`, `20261019-194507-together`); negativo nada informa.
- Regressão com monitores (execuções `20261019-180209-together` a `20261019-191307-together`, 38 suítes): 37 passaram; sem violação duradoura nos monitores. `stage3c` falhou por suposição anterior à E (cliente pode controlar invasores e concluir missão sozinho); teste ajustado, passou, negativo falhou.
- P3a (commit `f6b0510`): morte por companheiro ou invocação entre máquinas paga jogador (Lester mata pescador, cliente 500 a 550 XP). `stageP3a` 3/3, negativo `partyxpoff` falhou.
- Etapa L (commit `f6b0510`): tecla coloca herói 1,5 m atrás do parceiro; 3/3, negativo falhou. Decisão do proprietário: aproximação opcional em vez de limite rígido de distância.
- Regressão pré-pacote (série `20261019-pre-package`): 8 de 9. `stage3b` falhou em `20261019-195533-together`: orc aparou golpe de teste (`ZS_ParadeStumble`, dano 0). Teste agora golpeia até 3 vezes; repetição passou, negativo falhou.
- Rastreio em runtime (commit `7bc88a1`, branch agente A, fora de `master` ao escrever): intercepta início de movimento da engine e setters de tarefas; registra corpo, movimento/tarefa e chamador como módulo+RVA. `tracediag` 3/3. Maioria dos movimentos espelhados vem da locomoção; tarefas nos espelhos passam por `AISetTask`.
- `master` = `dff5cfa` (monitores P5, L, P3a, P1). `stageP1`, `stageP3a`, `stageL` passaram na DLL mesclada.

### <a id="derived-4"></a>Deduzido

- Quando teste falha por comportamento do jogo (NPC apara), repita ação como jogador faria; não afrouxe asserção.
- Leitura estática não diz qual chamador define tarefa num espelho em runtime; rastreio dos setters com endereços diz.

### <a id="unknown-4"></a>Desconhecido

- Causa do raro giro `ZS_HangAround` do boneco.
- Por que orcs mortos no host às vezes ficam em pé no cliente.
- Por que flechas bot param junto à mão.
- Resultado da regressão completa de `master` `dff5cfa` no par 2 (iniciada ao escrever).
- Se carga paralela torna giro mais frequente.

## <a id="2026-10-19-late-runtime-trace-and-the-standing-dead-orcs-agent-a"></a>2026-10-19 tarde: rastreio em runtime e orcs mortos em pé (agente A)

Observado:
- Rastreio (G3 Together `trace on`, arquivo `g3trace.log`) intercepta Engine `eCVisualAnimation_PS::PlayMotion` (RVA 0x30860) e Game `gCScriptRoutine_PS::SetCurrentTask` (0x66100) / `AISetTask` (0x164350) após verificar prólogos, e registra corpo, movimento/tarefa e chamador módulo+RVA. Suíte `tracediag` 3/3, negativo correto (sem arquivo sem comando).
- Host, `ZS_Dead`: reproduz `<skeleton>_Stand_None_None_P0_LieDead_Begin_N_Back...` (chamador Game.dll+0x16b485), depois `<skeleton>_LieDead_None_None_P0_Ambient_Loop_N_Back...` a cada ~400 ms (Game.dll+0x16a90c).
- Espelho cliente, `ZS_Dead` após AIMode 9 primeiro: nenhum movimento; slots de locomoção 1–3 continuavam caminhadas e posturas no cadáver. 0 de 4 deitados no negativo.
- Correção (deitar espelho: parar movimento e slots 1–3, tocar Begin, depois laço em AniState 19 como instrução play-ani): `deaddiag` 3/3, 12 de 12 deitados; regressão mesclada 15/15.

Deduzido:
- Corpos fora da tela não animam: matrizes de ossos mantêm pose antiga, então altura dos ossos só comprova corpos em vista.

Desconhecido:
- Se outras espécies (animais, humanos) morrem igual no cliente; só orcs da aldeia inicial testados.

## <a id="p2-arrows-first-version-agent-b-2026-10-20-pair-2-commit-ce6c5c7-on-agent-b-protocol-37"></a>P2 flechas, primeira versão (agente B, 2026-10-20, par 2, commit ce6c5c7 em agent-b, protocolo 37)

Estático (Script_Game e Game.dll, detalhes privados): PS_Ranged do jogador chama script `Shoot` diretamente, não pela tabela, então interceptado no lugar (endereço da entrada da tabela, prólogo verificado antes). Para jogador, `Shoot` define ShootVelocity = DamageHitMultiplier da flecha empunhada × 200 e mira em `PSCamera::GetScreenCenterPickPoint()`. Desliga colisão só com atirador e outra entidade, não partes do corpo do herói. `gCProjectile_PS::OnTouch` desarma projétil ao primeiro contato (grupo de colisão 6).

Abordagem: máquina atiradora anuncia própria flecha um quadro após aparecer (template, pose, TargetDirection, ShootVelocity, estilo de trajetória, comportamento de contato, dano, alvo). Observador cria cópia do template pertencente ao boneco atirador e dispara igual. Regra 1 do filtro descarta acertos, como cópias de meteoro.

Observado (`stageP2`, execuções 20261020-083728 a -091232-together-p2):
- Toda flecha criada pelo jogo atirador anunciada e copiada (6 de 6 por execução verde). Cópias do boneco. Voaram como original: diferença de 0–16 graus, distância parecida, salvo mundo observador diferente (cliente ainda mostrava alguns orcs mortos pelo host em pé; `ce6c5c7` não contém correção de espelhos mortos `9acdaf5` do agente A, verificado com `git merge-base --is-ancestor` em 2026-10-21).
- Negativo `shotmirroroff`: sem cópias, vermelho como pretendido.
- 1 de 3 verdes. Nas vermelhas falhou flecha do próprio atirador:
  - Bot dispara em postura ociosa; nova flecha começa dentro de `Body_Player`/`Head_Player` e para imediatamente. Preparar antes (estado `PS_Ranged_Aim`, 2 s) geralmente evita e deixa jogo definir tração (multiplicador 0,74).
  - Numa execução, varredura QA informou `spawned=0`: não achou flecha nova do atirador em 2 s. É contagem da varredura, não retorno de `Entity::Spawn` (veja experimento 0 e nota do agente C abaixo).
- Nenhuma flecha (original ou cópia) feriu NPC. Trajetórias físicas passaram a 10 cm do peito e seguiram sem chamar AddHitPoints. Causa desconhecida.

Deduzido: falhas na postura ociosa pertencem ao atirador de teste. Na execução `spawned=0`, existência da flecha desconhecida; espelhamento só anuncia as encontradas, então execução não separa atirador de espelhamento.

Ainda não coberto: exatamente uma aplicação numa execução (exige flecha que acerte); bestas; magias de projétil (MagicProjectile); entrada tardia.

## <a id="2026-10-20-the-rare-puppet-turn-agent-a"></a>2026-10-20: giro raro do boneco (agente A)

Observado:
- Rastreio com cadeias (percurso de ponteiros de quadro do hook `AISetTask`) e busca por endereço nas tabelas do admin: após reação a acerto (`ZS_Stumble`, `ZS_Slide`), jogo executa `ContinueRoutine` (Script_Game.dll RVA 0xa5ea0) para boneco; `SelectRoutineTask` (0xa9440: arena, `ZS_FollowPlayer` ou rotina) definia `ZS_HangAround` todo quadro por ~3 s e boneco virava parado.
- Envolver entrada `ContinueRoutine` da tabela e não executá-la para bonecos (commit `a4da3aa`, DLL `b0ec5c94…`): `ZS_HangAround` pelo menos uma vez em 63 de 63 antes, 0 de 20 depois; `stage2` 19 de 20 (vermelha é outro caso aberto: cliente correndo sob acertos orc, boneco 1–2 m atrás).
- Contagem de 63 não separa `ZS_HangAround` curto na criação (rastreio anterior naquela manhã o viu substituído após 16–350 ms) da cadeia de 3 s acima. Giro visível mais raro: séries `stage2` daquele dia antes da correção tiveram 2 de 10, 1 de 15, 3 de 15 e 4 de 20 vermelhas, nem todas giro (erros de teste abaixo e uma com cliente sob ataque).
- Duas falhas anteriores "boneco não chega ao passo" eram de teste: acertos orc empurraram herói cliente 1,3 m adiante, boneco seguiu exatamente.
- Interromper cambaleio nos bonecos fazia jogo reiniciá-lo todo quadro (até 257 vezes); revertido, cambaleio preservado (cosmético, direção pode diferir).

Deduzido:
- Reações a acerto no boneco julgadas pelo script de dano do próprio host (Script_Game.dll RVA 0xb4f50, cadeia de Game.dll+0x16093b), que também inicia cambaleio ali.

Desconhecido:
- Se `ContinueRoutine` também é alcançado sem tabela. Chamadores nativos diretos não verificados; wrapper cobre só tabela (como `Shoot`, que exigiu interceptação no lugar).

## <a id="why-the-bots-arrows-never-hurt-npcs-experiment-0-agent-b-2026-10-20-pair-2-run-20261020-122311-together-p2"></a>Por que flechas do bot nunca feriam NPCs: experimento 0 (agente B, 2026-10-20, par 2, execução 20261020-122311-together-p2)

Hook QA em `gCProjectile_PS::OnTouch` (exportado por Game.dll) registra todo contato. Conjunto de propriedades verificado antes de chamar `FuncOnTargetHit` é `eEPropertySetType_NPC` (30): acerto significa "entidade tocada é figura". Tipo de contato é conjunto que produziu contato: 14 = CollisionShape, 100 = Animation (zonas de acerto dos ossos).
Observado:
- Flechas host (4 tiros em aldeão a 5 m) tocaram baú (`G3_Object_Interact_Animated_Chest_01`), geometria sem nome e parede de casa; nunca alcançaram alvo. Buscador de posição só evitava figuras, não objetos.
- Flechas cliente tocaram própria espada e depois própria coluna do atirador (`PC_Hero type=100 bone=Hero_Spine_Spine_1`), prendendo ali. Nesta execução acompanhava leituras `spawned=0`: flecha presa é movida para sob o atingido e sai de `Entity::GetEntities`, então varredura QA não encontra.

Deduzido:
- Zonas de ossos realmente registram contatos. `Shoot` desliga colisão só com forma do atirador, não zonas de ossos. Bot disparando ocioso pode portanto acertar a si mesmo.
- Hipóteses do lado NPC (atravessamento entre quadros, zonas inativas em NPCs passivos) desnecessárias para explicar erros nesta execução. Não excluídas para flechas que passaram a 10 cm do alvo e seguiram (P2 acima).

Desconhecido:
- Se autoacerto fere atirador; por que linha cliente da mão ao alvo cruzou próprias costas.

## <a id="p2-spell-projectiles-the-fireball-first-agent-b-2026-10-20-pair-2-commit-ba72045-on-agent-b-protocol-38"></a>P2 projéteis mágicos, bola de fogo primeiro (agente B, 2026-10-20, par 2, commit ba72045 em agent-b, protocolo 38)

`MagicProjectile` chamado por nome (`_AI_StartCastPhase`), então entrada da tabela envolvida. Projétil conjurador (`Mis_Fireball`, linha com alvo definido, velocidade 100) anunciado como flecha, com item de origem. Cópia recebe magia desse item, como original por `MagicProjectile`; o atingido pode ler magia.
Observado (`stageP2fire`, 3 verdes): bolas de fogo host e cliente chegaram a Hamlar na primeira tentativa (perseguem alvo). Cópia tocou mesma figura na outra máquina. Host aplicou cada uma uma vez: sua diretamente, cliente como solicitação. Negativo `shotcopyhero` (cópia do herói observador) vermelho: acerto da cópia também contado.

Flechas comparadas (`stageP2hit`, alvo Hamlar, commit `875d676` em agent-b, DLL `f3c6e4f7…`): sempre que flecha alcançou alvo, host aplicou exatamente uma vez (sua diretamente, cliente como solicitação); cópia tocou mesmo ponto e não contou. 2 de 4 verdes: numa nenhuma flecha host chegou em 8 tentativas, outra abortada (host travou após teleporte, sem relatório). Negativo `shotcopyhero` vermelho (acerto duplo). Repetição posterior verde, total 3 de 5: ainda sem três verdes seguidas. Virotes de besta não chegaram ao alvo na aldeia, então aplicação única não demonstrada para eles.

## <a id="2026-10-20-static-npc-spells-world-callbacks-and-crash-signatures-agent-c"></a>2026-10-20: magias NPC estáticas, callbacks do mundo e assinaturas de falhas (agente C)

Somente estático, referência de fonte do mod `d4dc47e`; sem processos de jogo, instalações ou testes em runtime. Evidência lida de cópias isoladas de projetos Ghidra e logs QA existentes. Descompilação detalhada e logs específicos da máquina permanecem privados. Referências abaixo são RVAs DLL ou caminhos-fonte do mod.

Observado no código:
- `NpcRecord` tem HP/pose/animação/equipamento, não relógios de estado NPC nem tipo de grupo. Filtragem IA (`src/ai.cpp`) não para de modo geral scripts normais como OnTick/OnEnterProcessingRange.
- `MagicHypnosis` (`Script_Game+0x543b0`) inicia `ZS_MagicSleep`, cujo laço NPC sai acima de TaskTime30; laço Hypnosis registrado separadamente tem outro limite e não é selecionado por esse lançamento.
- `CanControl` (`+0x549a0`) exige caster == GetPlayer local. Controle/domesticação usam auxiliar `+0x54770` para dispensar membros Controlled e matar Summoned antes de adicionar novo Controlled. `MagicCallAnimals` (`+0x54160`) redireciona animais existentes; não cria seguidores.
- Veneno define bit4 e timestamp do relógio do mundo, depois OnTick fornece perda de HP. Doença define bit8 e stamina0. Replicação deve considerar callbacks ativos, não só aparência.
- Névoa usa bit64 global por NPC; nova névoa encerra existentes, e término/saída de processamento limpa estado amplamente. Simulações completas independentes de cópias visuais não preservariam ciclo de vida.
- Callbacks de roubo/crime (`+0x60930`, `+0x60670`) verificam jogador local explicitamente. Transições enclave (`+0x602d0`) mudam campos de crime/fama/membro além de estado. Tratamento nativo de missão EnterArea (`Game+0x158e20`) incrementa DeliveryCounter, ausente da sincronização atual de estado de missão.
- Reaparecimento natural (`Script_Game+0xac3c0`) depende de idade de calendário, seleção aleatória e distâncias do jogador local/vizinhos. Diário só de mortes não tem geração explícita de nova vida do mesmo GUID.

Correções das hipóteses antigas de falha:
- `Script.dll+0x13EA3` (dentro de `Entity::AttachTo`) é `mov edx,[eax+0xA0]`, após ler vtable da entidade passada. Entidade não nula e já passou verificação; ECX0 no contexto da exceção não é desreferência falha. Cinco instâncias arquivadas têm vtables inválidas. Chamador externo/violação de vida útil continuam desconhecidos.
- `Game.dll+0x2BD1F3` está na string de dados `CurrentAttackerEntity` em `.rdata`, não numa função de teleporte. Era EIP da falha host (2026-10-20 13:10, par 2, uma vez, logo após teleporte do bot, origem daquela interpretação); ESP `0x0019E849` sem alinhamento de 4 bytes e EBP `0xAA101779`. Retorno/ponteiro de função corrompido ou corrupção anterior de pilha é candidato, não causa comprovada.
- Varredura diagnóstica de pilha fornece candidatos a endereços de módulos, não cadeia desenrolada de chamadas; registrar deslocamentos da pilha, tipo bruto de acesso da exceção (inclusive execução) e ponteiros de entrada relevantes antes de inferir causa.

Próximos passos deduzidos: encaminhar intenção de magia ao proprietário simulador de cada NPC com identidade real de jogador e contexto; aplicar resultados uma vez; preservar estado/ grupo/ciclo de vida nas transferências e cargas. Testar lançamentos host/cliente/simultâneos, alvos inelegíveis, intenções duplicadas, expiração e reentrada. Reproduzir script solo original com boneco não equivale automaticamente ao conjurador real. Propostas de implementação/teste, não novas afirmações de recursos funcionais.

Verificação cruzada: OnTick chama AddHitPoints diretamente (`Script_Game+0xb11ab → +0x35b50`), evitando wrapper de dano do mod só na tabela. Veneno/queima espelhados precisam de proteção própria de tick ou representação só visual; filtro atual não protege genericamente efeitos de estado.
Depois (commit `2a9e983`, 2026-10-20 21:47, pela mensagem): veneno e doença em NPC de outra máquina lançados no proprietário, OnTick ignorado em espelhos e bonecos. Não retestado neste registro.

## <a id="agent-c-second-static-assignment-2026-10-20-request-labelled-1800"></a>Segunda tarefa estática do agente C (2026-10-20, solicitação marcada 18:00)

Evidência privada em `g3-workspace/re/findings/*-c.md`; nenhum jogo iniciado, instalado ou parado, nenhuma fonte do mod alterada. Descobertas estáticas e interpretações de execuções arquivadas.

Observado (código e execuções arquivadas):
- Reatribuição de GUID suportada por `eCNode::SetID` exportado (Engine.dll RVA 0x20DAB0). Remove chave antiga do mapa SceneAdmin, atribui novo `bCPropertyID` de 20 bytes por valor e registra novamente. Chaves existentes sobrescritas sem verificar identidade. Proxies existentes retêm IDs armazenados. Veja `entity-guids-c.md` para ABI, bytes brutos de prólogo, implicações de salvamento e proposta de chamada direta.
- Hailstorm e Meteor chegam a `DoLogicalDamage` nativo antes de `AddHitPoints`. Hailstorm escolhe alvos independentemente em cada nuvem simulada. Na falha `20261020-165728-together-p2`, nuvem observadora julgou alvo de pouca vida enquanto delta HP foi rejeitado; alvo morreu sem conclusão de solicitação/XP remota. `AssessHit` pode agendar morte antes do filtro; RagdollDead grava HP zero diretamente.
- Morte normal orc deixa cadáver; não exclui entidade imediatamente. Wrappers Entity de script copiam ponteiros brutos de entidade/propriedades, diferente de proxies nativos. GameHit QA chama OnDamage diretamente em AssessHit e não atualiza LastInflictor por DoLogicalDamage.
- ArmyOfDarkness faz 6/8/10 tentativas de criação (grupos iguais Skeleton/SlaveZombie nos limiares INT 250 e 300), após limpar grupo Summoned anterior. OnTick mata criaturas Summoned não esperando a mais de 4000 unidades do jogador local. Dados nativos de grupo relevantes ao salvamento.
- OnHit usa atacante Self e CurrentTarget; OnDamage usa vítima Self e fonte de dano Other. Reset define diretamente HP/SP/MP máximos. Ghost combina entrada local, câmera, foco e movimento. DuskToDawn muda fator do relógio para 3840, escala de tempo do console e por fim redefine valores do jogador.
- Resolvidos 21 nomes IA que inventário runtime listou sem endereço original (444 nomes, 423 com RVA): 19 definições no projeto privado Script_Game, duas em Script_paru. Ponteiros originais de registro e corpos reais em `missing-ai-complete-c.tsv` e `missing-ai-c.md`. Hold/Use/Equip podem criar, dividir ou excluir pilhas; SayBossNews/Bribe podem mudar crime/combate. LieKnockDown só avança corrotina.
- Restauração pessoal atual preserva pilhas Skill existentes e ensina ausentes; forma união com habilidades já presentes na campanha carregada, não substituição exata. Registro não codifica completamente aprendizado/ativação. Veja `xp-attributes-c.md` para comparação completa de caminhos de morte/missão/diálogo/professor/companheiro/invocação/consumível/vantagem.

Deduzido:
- Trocar chave da entidade antes de vincular referências de grupo/alvo/proprietário. Cache `missing` de espelhos precisa de nova tentativa explícita após criação atrasada.
- Execução Hailstorm sustenta fortemente defeito de autoridade anterior ao filtro, não perda demonstrada de ID do proprietário: filtro só em `AddHitPoints` não impede toda morte.
- Código ragdoll posterior pode inspecionar causador antigo após GameHit QA.
- Caminho de adoção por escravidão não restaura fielmente Summoned tipo 5. Snapshots comuns de relógio não representam transação DuskToDawn inteira.
- Cliente carrega salvamento host cujo herói é do host, então habilidades aprendidas dele permanecem após restauração no cliente (estático; não reproduzido em runtime).

Desconhecido:
- Atribuição exata da morte Hailstorm: execução sem rastreio Task e com orcs ativos.
- Chamador real da antiga falha AttachTo (`crash-lifetimes-c.md` lista pontos de medição de buffer circular/AV). Nenhuma das 21 entradas IA recém-testada em runtime.

## <a id="agent-c-actor-identity-and-social-world-reactions-2026-10-20"></a>Agente C: identidade de atores e reações sociais do mundo (2026-10-20)

Continuação estática, referência `d4dc47e`. Acréscimos nela que C verificou como implementados (sem registro em outro ponto destas notas; resumos das mensagens de commit): F1 de A (`58b3a14`, NPCs reagem a golpes cliente por AssessTarget com ReactToDamage) e W1 (`96fd5d0`, portas e trancas iguais para todos, estado de mundo tipo 10), Charm de B (`fae2751`, Charm em NPC de outra máquina executa ali) e correção de cópias de magia em área `5628884` (`MagicAreaDamageTick` interceptado no lugar, ignorado em cópias de bonecos). C não iniciou jogo nem teste. Detalhes privados: `re/findings/social-identity-c.md`, `social-crime-identity-c.md`, `social-player-context-c.md`, `social-mod-gaps-c.md`. Plano concreto A/B em `social-coop-auftraege-c.md`. Endereços são RVAs Script_Game.dll salvo módulo indicado.

Observado (código):
- SendPerceptionTakeItem (0x32840) chama CanReceivePerceptionFrom e AssessTakeItem diretamente, então wrapper de percepção só na tabela não cobre. Item lido do alvo atual do ator. Contar roubo e decidir testemunhas são caminhos separados.
- AssessPlayerWeapon (0x2F780) exige GetPlayer local; AssessPlayerZone (0x2FCA0) usa `Entity::IsPlayer` (Script.dll RVA 0x14900), comparação de ponteiro contra entidade jogador em cache. AssessPlayerSneaking (0x2F5B0) sem proteção direta de jogador, mas percepção ativa normal o chama do slot local.
- ZS_ReactToZone_Loop (0x224C0) busca GetPlayer novamente após temporizador do estado e usa para distância/Goto. ZS_GotoPlayerZone (0x30280) também busca zona do jogador local tardiamente.
- `gCNPC_PS::WriteSaveGame`/`ReadSaveGame` (Game.dll RVAs 0x144E90/0x144D00) carregam explicitamente memória de crime/luta ligada ao jogador e proxies de alvo. `gCPlayerMemory_PS::WriteSaveGame`/`ReadSaveGame` (Game.dll RVAs 0x14E740/0x14E630) carregam quatro arrays políticos.
- `_AI_SayGuardNews` (0x3A3C0) define/limpa DIA_BRIBE, DIA_EXCUSE e DIA_PROVOKE em PlayerMemory; story.cpp compartilha PlayerKnows como eventos de mundo. Severidade da guarda também usa valores globais do processo.
- Retenções talk.cpp não são reservas plenamente exclusivas: Begin repetido sobrescreve detentor, End não verifica identidade e diálogos locais host não integrados.

Deduzido:
- Mapear corpo remoto ao herói local em GetAttitude dá resposta compartilhada de atitude, mas não contexto persistente de ator para crime, diálogo ou estados IA posteriores.
- Preservar identidade do item antes de remoção ou mudança de foco e vincular efeitos de crime à transação de inventário aceita. Não generalizar uma proteção de jogador a todo script.
- Corrigir só argumento de entrada deixaria dependências tardias acima.
- Suporte a salvamento nativo não é replicação ao vivo nem registro por jogador.
- Opções erradas de diálogo para jogador não envolvido são candidato a teste, não falha reproduzida. Não bloquear todos DIA_* cegamente.
- Identidade de sessão, participante persistente e corpo visível atual precisam de tratamento distinto em desconexão, transformação, salvamento e transferência de autoridade.

Primeiro teste vertical proposto: cliente pegar propriedade alheia com host inocente perto, seguido de aviso ao alvo correto e reentrada. Trabalho posterior cobre feedback completo de combate, conflitos diálogo/missão, cancelamento de interação, reentrada de mundo e tempo coordenado. Aceitação em runtime permanece com A/B nos próprios pares; descobertas e instruções de teste, não recursos novos testados.

## <a id="agent-c-outside-review-of-cross-system-transitions-2026-10-20"></a>Agente C: revisão externa de transições entre sistemas (2026-10-20)

Consulta Fable 5.1 autorizada pelo proprietário revisou pressupostos abstratos, depois conjunto limitado de trechos versionados (A d2e331f8, B 760af83f). Revisão concluída sugeriu testar transferências recusadas com efeitos nativos duradouros, consistência mundo/salvamento pessoal e reações interrompidas por troca de boneco. Hipóteses e propostas, não novos resultados runtime.

Verificações estáticas locais limitam sugestões:

- Salvamento nativo do mundo host conclui antes de notificação Campaign fazer cliente gravar registro pessoal. Mudanças de recipientes observadas por consulta periódica; conjunto pendente vazio sozinho não prova que todas chegaram ao host. Testar ordem alcançável salvar/transferir; não afirmar duplicação observada só por essa ordem.
- Respostas de recipientes e notificações Campaign usam mesmo canal confiável. Não inventar reordenação arbitrária dessas mensagens. Compensação existente de recipientes deve entrar no experimento.
- Nome local da campanha transferida e prefixo do registro de herói consistentes. Incerteza da revisão resolvida pelo caminho local completo.
- ItemTook enviado após entidade local desaparecer. Perda inversa proposta não pode ser inferida só de animação de coleta de vários quadros.
- Duas conclusões nativas de missão podem recompensar corretamente dois elegíveis. Contar efeitos autorizados por destinatário e seguir causa pela replicação.
- Reproduzir resultado pode disparar lógica nativa. Igualdade de hashes cobre só campos selecionados numa versão comparável. Nenhum comprova correção semântica.

Manter simulação distribuída e mecanismos por domínio existentes salvo experimento estabelecer motivo concreto para mudar. Revisões seguintes devem levar última resposta, limitações, referência exata da fonte e evidência nova.

## <a id="agent-c-poison-and-disease-implementation-handoff-2026-10-20"></a>Agente C: passagem da implementação de veneno e doença (2026-10-20)

Continuação estática contra B f1ad45e3, protocolo 40; sem nova afirmação runtime. Plano de veneno antes ausente agora nas descobertas privadas.

Observado (código; RVAs Script_Game.dll):
- OnTick nativo (0xB0EF0) chama AddHitPoints diretamente em 0xB11AB, depois pode selecionar inconsciência ou morte.
- Bytes de entrada 55 8B EC 83 E4 F8 são três instruções completas. ABI registrada stdcall de quatro argumentos, RET 10h, apesar dos três na descompilação.
- Veneno contribui -5 por callback executado, não comprovadamente -5 por segundo. Doença inicialmente zera vigor e tem regeneração diferente para jogador/NPC. Vigor (SP) ausente de NpcRecord e PlayerState, então nenhum estado SP viaja.
- Reaplicação bem-sucedida renova timestamp do mundo mesmo já envenenado. Duas aplicações no mesmo segundo podem ter bits/timestamps idênticos antes/depois. MagicPoison/Disease e AssessHit contêm caminhos de aplicação.
- Curas específicas de veneno/doença visam other; HealOther limpa estados e cura HP, enquanto Cure comum só cura HP no corpo examinado. Roteamento HealOther atual de B cobre jogadores, não NPCs externos.
- other=None de OnTick e CurrentAttacker posterior não são procedência armazenada confiável da magia. IsMirrored só vira true após body.pacified.

Deduzido e proposto (não testado):
- Bloquear só gravação HP deixa decisão posterior ativa. Proteção proposta: entrada OnTick nativa para réplicas externas, preservando corpo controlado local e simulação autoritativa NPC. Conferir impressão digital completa específica da versão antes de alterar.
- Observar setter de estado aceito dentro do contexto de origem; estender roteamento de alvos HealOther a NPCs externos.
- Manter origem até conclusão real Kill/Defeat nativa. Hooks de conclusão propostos preservam semântica nativa de ator/nocaute e usam um caminho de recompensa com proteção de duplicatas, incluindo destinatários locais e remotos.
- Proteger transição conhecida de autoridade além de body.pacified. Transferência precisa de tempo de estado, origem e estado canônico de derrotado, distintos da flag temporária de supressão XP do espelho.

Limpeza e integração de recompensas conferidas independentemente; revisão final corrigiu dois pressupostos, e itens acima são versões corrigidas: não existe transporte SP em que confiar, e HealOther alcança só jogadores. Cadência nativa de tick, cobertura completa de limpeza e hooks propostos ainda exigem testes isolados de B. (`2a9e983` de B depois ignorou OnTick em espelhos e bonecos; veja primeira seção C.)

## <a id="agent-c-death-attribution-creature-lifetime-and-first-frame-arrows-2026-10-20"></a>Agente C: atribuição de morte, vida útil de criaturas e flechas no primeiro quadro (2026-10-20)

Análise estática (quarta tarefa C) contra commit 7595022 (protocolo 40, incluindo DeedContext 32fbcfe: net.h registra quem fez ato e com quê). Sem jogos, compilações, instalações ou mudanças no mod. Detalhes privados: death-events-c.md, creature-distance-c.md, review-b-c.md, arrow-spawn-c.md. Trechos fixos, pontos nativos de chamada e bytes de hooks verificados; não é aceitação em runtime.

Observado (código e execuções arquivadas; RVAs Script_Game.dll):
- Kill nativo (0x1BC30) e Defeat (0x27510) são duas entradas adequadas a rotina de conclusão por vítima. Chamadores diretos incluem limpeza e combate, ignorados por wrappers da tabela de registro.
- OnCheatKill para vítima e seleciona tarefa de morte, mas não grava CurrentAttacker. Passar vítima nos dois argumentos não substitui por isso atacante antigo.
- Ramo de distância de criatura invocada de OnTick sai antes do dano veneno/queima, limpa líder de grupo, mas deixa CurrentAttacker. Morte nativa por queda o limpa explicitamente.
- Kill pode chamar NotifyEnclave, que pode chamar Kill(None, outro membro). Entity::Kill nativo é mecanismo diferente de remoção.
- Um lançamento pode matar várias vítimas; invocação pode matar repetidamente; nocaute e morte posterior têm efeitos XP/crime distintos.
- Snapshots de criaturas do cliente param além de 40 m. Reivindicações host evitam liberação normal de obsolescência de três segundos, enquanto verificador de cópia renova temporizador por IsMirrored (pacified), não pacote recente. Três `stageCreatureLife` aprovados (`20261020-185021`, `-185346` e `-185644-together-p2`) aceitaram seis criaturas ArmyOfDarkness espelhadas vivas no host após cliente afastar 50 m: suíte rejeita só `free`, não `mirrored`. Trata de invocações, não devolução de NPC de E1, cujo cliente desconecta.
- Dois defeitos TakeOver no código: tomada host deixa reivindicação anterior cliente; tomada falha deixa tarefa Follow atrasada 700 ms. Nenhum UAF ou estouro concreto demonstrado nos três relatórios numéricos de estado.
- Flecha `spawned=0` é timeout da varredura de lista/proprietário, não retorno de Entity::Spawn. Anexação nativa precoce e OnExitProcessingRange -> Entity::Kill de projétil são caminhos distintos.

Deduzido e proposto (não testado):
- Capturar procedência confirmada da solicitação antes do estado de morte atrasado; validar autoridade sobre vítima e propriedade da origem antes. Motivo de limpeza deve prevalecer sobre contexto antigo de acerto/estado.
- Usar reentrância e identidades de conclusão por vítima em vez de herdar um assassino global. Separar identidade da ação-fonte e da conclusão, incluir gerações de vida/sessão e migrar caminho existente de recompensa em vez de acrescentar segundo. Contadores locais do processo mais nomes sozinhos não são identidades persistentes de deduplicação.
- Enviar fins de criaturas confiavelmente, independente do interesse de movimento; limpar registros de réplica/reivindicação juntos. Invocações temporárias não devem ser oferecidas novamente como escravos persistentes. `stageCreatureLife` precisa falhar com cópia `mirrored` congelada.
- Registrar criação, contato, anexação, saída de alcance, deterioração e destruição por GUID de flecha antes de mudar comportamento.

Desconhecido:
- Causa dos oito tiros `spawned=0` em `20261020-204556-together-p2` (`shots=8 announced=0 unresolved=8`, sem log de contato nem GUID novo). Experimento 0 acima mostra uma possibilidade (autoacerto, flecha anexada ao atirador), mas esta execução não tem evidência de contato.

Plano de morte recebeu três verificações independentes. Implementação e aceitação isolada runtime ficam com agentes de jogabilidade.

## <a id="agent-c-release-day-guard-and-transport-review-2026-10-21"></a>Agente C: revisão de proteção e transporte no dia da versão (2026-10-21)

Candidato estático fdb1229 comparado à referência empacotada 64ad370. Sem edições, compilações, instalações ou nova aceitação runtime. Relatórios privados: attachto-guard-c.md, release-review-c.md, hamachi-net-c.md; rascunho de documentos de jogador e formulário vazio de teste também preparados aos agentes.

Observado (código e logs arquivados de falha):
- Registradores coincidem com leitura falha de slot VTable de AttachTo, não argumento Entity nulo. Retorno correspondente de GetCombatMoveLength segue construção do wrapper Other. Rotina usa só Self.Species e ação no resultado.
- Registrador de falhas varre palavras da pilha por endereços nos módulos; não desenrola quadros. Pontos nativos de chamada sustentam cadeia candidata por alvo salvo de ação de combate.
- Nova sincronização de reputação pode sobrescrever mudanças locais não examinadas quando estado host chega antes da varredura cliente de 500 ms; ordem confiável de pacotes não protege mudanças locais. Reversão de roubo pendente usa contador global de itens devolvidos em vez de corresponder à transação recusada.
- Host vincula todas as interfaces IPv4. ENet incluído limita payload UDP a 1392 bytes por padrão; pode significar 1420 incluindo cabeçalhos internos IPv4/UDP.
- Snapshots NPC chegam a 3031 bytes de aplicação; blocos de salvamento a 16012. ENet fragmenta, mas pacotes grandes com flags zero são promovidos a fragmentos confiáveis salvo selecionar UNRELIABLE_FRAGMENT explicitamente. Perder fragmento NPC pode reter snapshots posteriores atrás de sua sequência confiável.
- Timeouts ENet, expiração de boneco em 15 s e obsolescência NPC em três segundos são mecanismos distintos. Nenhum simulador configurável de latência/perda existente encontrado; desativar tratador de snapshots não testa perda UDP nem retransmissão.

Deduzido e proposto (não testado por C):
- Proteção restrita revisada independentemente passa wrapper Entity vazio para Other, sem vincular alvo bruto suspeito. Passar null reentraria na busca SPU Other original. Validar implementação original antes de envolver. Evita uma desreferência desnecessária, não todos os usos do alvo antes/depois nem origem não comprovada da corrupção. Proteção runtime exige regressão de combate. Ignorar globalmente IA de entidades mortas ou chamar IsKilled virtual num ponteiro suspeito não comprova vida útil segura.
- MTU host ENet 1200 antes de estabelecer conexão e lotes NPC de 18 registros, mantendo limite receptor 48 e layout de rede. Agregação de datagramas significa que só lotes menores não limitam tamanho UDP.

Desconhecido:
- GUID exato do alvo e histórico de destruição por trás da falha AttachTo.
- MTU real VPN/caminho (não medido, portanto nenhum MTU Hamachi universal afirmado).

Depois em `master` (mensagens de commit, não retestado aqui): `5bea542` fornece wrapper vazio a GetCombatMoveLength (QA `movelength`, suíte `stageRaid`); `66e44e1` define MTU ENet 1200 e 18 NPCs por mensagem; cliente agora informa atos não relatados antes de aceitar contadores host e mantém roubos retidos por cima.

Escolha do pacote e aceitação runtime ficam com agentes da versão e proprietário. Textos distinguem pacote alternativo de candidato não aprovado; identidade final ZIP e salvamento alternativo compatível não são inventados intencionalmente.

## <a id="2026-10-21-code-review-of-the-2026-10-2021-notes"></a>2026-10-21: revisão de código das notas de 2026-10-20/21

Revisão das seções acima achou contradições; cada uma conferida com histórico git do mod e descobertas privadas, e seções corrigidas no lugar. Nenhum jogo iniciado nem teste executado para revisão.

Observado:
- `ce6c5c7` (P2 flechas, primeira versão) não contém correção de espelho morto `9acdaf5`; todas as referências posteriores acima (`d4dc47e`, `5628884`, `760af83f`, `d2e331f8`, `f1ad45e3`, `32fbcfe`, `7595022`, `64ad370`, `fdb1229`) contêm (`git merge-base --is-ancestor`). Orcs mortos em pé nas primeiras P2 portanto não contradizem correção.
- Seis cópias espelhadas congeladas são criaturas ArmyOfDarkness em `stageCreatureLife`, não NPCs E1.
- `Game.dll+0x2BD1F3` era EIP da falha, não palavra de varredura da pilha.

Deduzido:
- `0x100b4f50` de A é VA do RVA Script_Game.dll 0xb4f50: mesmo rastreio escreve `ContinueRoutine` como `0x100a5ea0`, que notas dão como RVA 0xa5ea0.

Desconhecido:
- Se `ContinueRoutine` tem chamadores nativos diretos (veja seção do giro).
- Se união de habilidades na restauração aparece em runtime.
