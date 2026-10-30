# <a id="running-several-game-copies-for-tests"></a>Executando várias cópias do jogo para testes

Testes cooperativos precisam de 2 ou mais clientes reais num PC, iniciados por script, frequentemente por vários agentes ao mesmo tempo, numa máquina onde o usuário pode estar jogando. Esta página explica como fazer isso sem prejudicar o jogo, os salvamentos ou o trabalho dos outros.

As ferramentas deste repositório implementam tudo abaixo para qualquer jogo Windows:

- [`tools/gameslot`](../tools/gameslot/README.md): trava com prazo (vagas, proteção de RAM, encerramentos por PID).
- [`tools/gamepool`](../tools/gamepool/README.md): instalações isoladas com hardlinks, auxiliares de inicialização, conjunto de instâncias prontas, perfil econômico e evidências de falhas. Um JSON por jogo guarda suas particularidades.

Adaptadas do projeto cooperativo Fallout: New Vegas, exigem apenas Python. Para inicializadores completos que dão controle e região de tela a cada cópia (tela dividida), veja [split-screen.md](split-screen.md) e a linha Nucleus Co-op em [tools.md](tools.md). A estrutura de testes atendida está em [automated-qa.md](automated-qa.md).

## <a id="the-short-version"></a>Versão resumida

1. Reserve uma vaga primeiro. Nunca inicie um jogo sem uma.
2. Dê a cada cópia uma pasta própria de instalação com hardlinks e configurações, salvamentos e logs privados.
3. Se a segunda cópia fecha logo depois, há verificação de instância única. Faça-a passar dentro do processo do jogo ou use sessões ou ambientes isolados separados.
4. Inicie as cópias por processo desvinculado, minimizadas, uma após a outra, esperando cada uma ficar pronta.
5. Registre todo PID iniciado (com horário de criação). Encerre somente esses.
6. Nunca escreva na instalação, configurações ou salvamentos do usuário; comprove com hashes antes e depois do teste.

## <a id="1-one-isolated-install-per-copy-hard-links"></a>1. Uma instalação isolada por cópia (hardlinks)

Um jogo de 50 GB não precisa de 50 GB por cópia. No mesmo volume NTFS, um hardlink é outro nome para o mesmo arquivo, e uma pasta de hardlinks é criada em cerca de um segundo.

- Espelhe a instalação: hardlink de cada arquivo, pastas reais. Se impossível (volume diferente, sem direito de link simbólico), tente links simbólicos e depois cópias normais. Confira disco livre primeiro: cópias normais exigem o tamanho inteiro por instância.
- Hardlink é o **mesmo arquivo**. Qualquer escrita por ele altera a instalação do usuário. Todo arquivo escrito pelo jogo precisa ser real e privado na instância: configurações, configurações geradas, caches de shaders, log de execução, dumps, pastas de plugins preenchidas e pasta de salvamentos (crie vazia).
- Ao reescrever arquivo privado, apague primeiro e depois escreva, evitando escrever por um link antigo de outra execução. Recuse editar arquivos com mais de um hardlink, qualquer link e qualquer coisa fora da pasta de instâncias.
- Muitos jogos leem configurações e escrevem salvamentos em `Documents` ou `AppData`. Procure opção própria para usar a pasta de instalação (modo portátil), defina-a na configuração privada e acrescente as pastas reais do usuário à lista protegida onde nenhuma ferramenta escreve.
- Comece a configuração privada pela cópia do arquivo do usuário (somente leitura) e aplique as edições. O original normalmente tem a lista necessária de DLCs e mods.
- Registre SHA-256 dos arquivos imutáveis (executável e dados principais) ao criar a instância e confira antes do teste. Hash alterado indica escrita por link ou instalação substituída por atualização.
- `mklink /H` e `mklink /J` do Windows permitem configuração manual; Nucleus Co-op pode criar cópias por links simbólicos ([tools.md](tools.md), seção 3).

`gamepool provision` faz tudo isso pela configuração (`link`, `config_files`, `protected_paths`).

**Jogos Unity sem opção portátil** mantêm salvamentos em `Application.persistentDataPath` (`%USERPROFILE%\AppData\LocalLow\<company>\<product>`), frequentemente uma pasta Steam Auto-Cloud. Unity resolve por `SHGetKnownFolderPath(FOLDERID_LocalAppDataLow)`, importada por `UnityPlayer.dll` (e `GameAssembly.dll` em IL2CPP). Um plugin de carregador exclusivo de testes que altera essa importação cedo nos módulos do próprio jogo (`OnPreInitialization` de MelonLoader), respondendo LocalLow com `<instance>\LocalLow`, dá a cada cópia salvamentos, preferências e análises privados; acrescente `-logFile <instance>\Player.log` para o log. Verificado em Slime Rancher 2 (Unity 6000.0, IL2CPP), pasta real com hashes inalterados entre execuções: [games/slime-rancher-2/qa/SaveIsolation](../games/slime-rancher-2/qa/SaveIsolation). `steam_appid.txt` na cópia impede o Steam de reiniciar a instalação da loja.

## <a id="2-single-instance-checks-named-mutex-and-findwindow"></a>2. Verificações de instância única: mutex nomeado e FindWindow

Muitos jogos recusam uma segunda cópia. Dois mecanismos são comuns:

| Verificação | Funcionamento | Sintoma |
|---|---|---|
| Mutex nomeado | O jogo chama `CreateMutex` com nome fixo ao iniciar e sai se já existir (`ERROR_ALREADY_EXISTS`) | Segunda cópia mostra erro ou fecha em um ou dois segundos com código diferente de zero |
| Classe ou título de janela | O jogo chama `FindWindow` para sua classe/título e sai ou ativa a janela existente | Mesmo sintoma, ou a primeira janela vem para frente |
| Configuração do Unity player | `<Game>_Data/boot.config` contém `single-instance=`; o player sai se já houver cópia. Remova a linha somente nas cópias de teste; arquivo de texto, não executável (Graveyard Keeper, Unity 2020.3) | Segunda cópia fecha imediatamente |

Para distinguir, acompanhe a segunda cópia com Process Monitor ou API Monitor buscando `CreateMutex` e `FindWindow`, ou leia o log de saída. O inicializador de `gamepool` informa quando uma cópia sai em até `watch_s` segundos e seu código, revelando o problema antes do tempo limite. Confira também o caminho da imagem de cada processo: um inicializador que abre outra cópia do jogo original na pasta da loja pode deter o mutex; nesse caso, não é sua cópia que está atrapalhando.

Soluções, da melhor para a pior:

1. **Corrija dentro do processo do jogo.** Mod, plugin ou DLL proxy carregado antes da inicialização envolve `CreateMutexA/W` (e `FindWindowA/W`) no próprio processo. Torne o nome do mutex único por processo; faça a busca de janela retornar ausência ou dê classe única a cada cópia. Apenas o processo do jogo é alterado. Forma da correção:

   ```c
   // Runs inside the game process. Route the game's CreateMutexA calls here (patch the import table or use a hook library).
   HANDLE WINAPI MyCreateMutexA(LPSECURITY_ATTRIBUTES sa, BOOL own, LPCSTR name) {
       char unique[256];
       if (name && strcmp(name, "NameTheGameUses") == 0) {
           snprintf(unique, sizeof unique, "%s-%lu", name, GetCurrentProcessId());
           name = unique;
       }
       return CreateMutexA(sa, own, name);
   }
   ```

   Condicione isso a uma opção ativada só pelas instâncias de teste, nunca pelos jogadores.
2. **Sessões ou ambientes isolados.** Espaços de nomes de mutex e janelas pertencem à sessão Windows e ao ambiente isolado. Execute cada cópia com usuário próprio, caixa Sandboxie-Plus ou VM. Mais pesado, mas sem código. Opções de handlers Nucleus Co-op cobrem essa família ([tools.md](tools.md), seção 3).
3. **Fechar o identificador do mutex externamente.** Tecnicamente possível (`DuplicateHandle` com `DUPLICATE_CLOSE_SOURCE` no identificador da primeira cópia), mas acessa outro processo, e o sistema de permissões de um agente corretamente recusará. O projeto New Vegas abandonou esse caminho. Não o escolha.

Não aplique patch ao executável para remover a verificação nem altere DRM da loja. Esta página trata de executar suas próprias cópias de um jogo que você possui.

`gamepool/tests/fake_game.py` simula ambas as verificações (`--mutex`, `--window-class`) e a correção por nomes únicos (`--rename-mutex`, `--unique-window-class`). A suíte demonstra bloqueio da segunda cópia, relato da saída precoce com código e duas cópias funcionando quando os nomes são únicos.

## <a id="3-launch-from-a-long-lived-process"></a>3. Inicie a partir de um processo duradouro

Um jogo iniciado por comando curto (chamada de shell do agente, script que termina) frequentemente morre ao final do comando, porque o objeto de trabalho do pai fecha e leva os filhos.

- Inicie com `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB`. Se o objeto proibir desvincular, a chamada falha com acesso negado; repita sem essa opção.
- Melhor: um serviço em segundo plano (conjunto de instâncias prontas) controla os jogos; a linha de comando só conversa com ele.
- Alguns jogos usam carregador que inicia o jogo real e sai. O PID lançado é o errado. Encontre o processo real **abaixo do carregador na árvore**, não por aparecer outro com o mesmo nome: agente ou usuário pode ter iniciado simultaneamente. O processo mantém o PID do pai após a saída deste, permitindo a busca posterior.
- Inicie uma cópia por vez. A cópia k precisa estar pronta (sondagem responde) antes de iniciar k+1, pois a primeira pode criar a trava que interrompe a segunda, e inicializações simultâneas disputam disco.
- Defina prontidão por jogo: janela existente, arquivo de prontidão, linha de log, porta ou pipe nomeado respondendo. Consulte repetidamente com prazo; nunca uma única vez.

## <a id="4-minimized-windowed-cheap"></a>4. Minimizadas, em janela, econômicas

Cópias que o usuário não olha devem custar pouco e nunca tomar a tela:

- Inicie com `STARTUPINFO.wShowWindow = SW_SHOWMINNOACTIVE` (7). Abre minimizada sem assumir primeiro plano, preservando o foco da janela ativa do usuário.
- Muitos jogos criam outra janela depois da tela inicial. Continue minimizando novas janelas por alguns segundos após a última surgir (`ShowWindowAsync`, sem ativação). Nunca envie entrada para encontrar ou mover janela.
- Configurações de maior impacto: janela pequena, modo janela (para permanecer minimizado), sem vsync, limite de quadros, sem sombras ou antisserrilhamento, pular introduções. Mantenha execução sem foco (opção de sempre ativo ou segundo plano na maioria dos motores).
- Algumas economias mudam comportamento: menos células carregadas podem causar falha ou corrupção ao carregar salvamento de outra configuração; sem áudio, um teste que espera fala acabar pode parar. Deixe essas opções voluntárias.
- Use logs e capturas internas do jogo como evidência, nunca a área de trabalho que captura outros conteúdos do usuário.
- Confira se iniciar minimizado não trava o motor. Um cliente modificado Unreal Engine 3 (OpenOL), aberto por shell em segundo plano, ficou minimizado e parado logo após a linha do middleware de áudio (CPU ociosa, log silencioso por minutos), até minimizar e restaurar sua janela uma vez. Espere essa linha, restaure uma vez (`ShowWindow` minimiza e restaura) e continue acordando a janela até conectar.

- Mantenha a tela acordada nas execuções sem supervisão. BattleTech (Unity 2018.4) trava em "Input initialized", antes de código de mods, ao iniciar com tela adormecida; ambas as cópias ficaram ali até a tela acordar.
- Carregadores também podem limitar instâncias: ModTek permite um processo por pasta. A segunda cópia BattleTech é uma pasta dos pequenos arquivos superiores mais junção para `BattleTech_Data` da primeira.

`gamepool lowcost` aplica perfil da configuração somente às configurações privadas.

## <a id="5-ram-guard"></a>5. Proteção de RAM

Dois ou três jogos grandes podem levar o PC à paginação, prejudicando a sessão do usuário.

- Mantenha um mínimo de RAM livre (3 GB como ponto inicial) e recuse nova cópia abaixo dele. Primeira cópia e renovações de concessões nunca são recusadas. `gameslot` faz isso com `min_free_gb`.
- Jogos de 32 bits atingem seu limite (cerca de 3 GB de memória de trabalho) antes de encher o PC. O conjunto reinicia uma cópia quando a memória cresce um valor definido desde a inicialização ou passa um limite fixo.
- Meça: amostre memória e CPU de cada cópia ociosa, com e sem perfil econômico (`gamepool measure`).

## <a id="6-pid-scoped-kills"></a>6. Encerramentos restritos a PIDs

O usuário pode jogar no mesmo PC durante os testes. Encerrar pelo nome da imagem (`taskkill /IM Game.exe`) termina sua sessão.

- Registre PID, nome da imagem e horário de criação de todo processo iniciado. Encerre apenas os registrados e somente se os três ainda coincidirem. PID pode ser reutilizado por processo alheio após o seu terminar.
- Registre cada PID também na trava da vaga. Quando o prazo de um detentor que falhou expira e outro assume, o novo detentor encerra só os PIDs registrados naquela concessão.
- Recuse iniciar se já existir processo de jogo que não é seu, salvo indicação explícita de segurança. Pode ser o jogo do usuário.
- Use `taskkill /T` (árvore de processos) para a cópia registrada: carregador e auxiliares abaixo dela devem encerrar junto.
- Teste com processos reais: inicie um chamariz com o mesmo nome, execute seu código de parada e exija que o chamariz continue vivo.

## <a id="7-never-touch-the-owners-game-or-saves"></a>7. Nunca altere o jogo ou os salvamentos do usuário

- Trabalhe em cópias. Instalação somente leitura; configurações e pastas de salvamentos reais na lista protegida.
- Calcule hashes dos salvamentos e configurações antes e depois. Hash alterado é bug da estrutura de testes, não do jogo.
- Teste que carrega salvamento carrega uma cópia na pasta privada da instância.
- Não execute cópias contra serviços on-line ou antitrapaça. São para testes próprios em LAN ou loopback.

## <a id="8-cold-start-or-warm-pool"></a>8. Inicialização do zero ou conjunto pronto

| | Inicialização do zero (`up`, `job`) | Conjunto pronto (`pool up`, `lease`) |
|---|---|---|
| Custo inicial por teste | Minutos (jogo inicializa) | Milissegundos (cópia já ativa) |
| Estado entre testes | Novo | O deixado pelo teste anterior; reinicialize ou marque sujo |
| Uso | Poucos testes ou os que exigem inicialização limpa | Muitos testes curtos, bots que carregam e verificam estado |

O conjunto entrega instâncias inteiras, reinicia as mortas ou sem resposta antes de disponibilizar, recicla após K concessões, crescimento de RAM, marcação de sujeira ou prazo expirado, e dá a cada instância um número de geração. O teste o confere para não conversar com jogo recém-reiniciado que perdeu o estado.

## <a id="9-when-a-copy-crashes"></a>9. Quando uma cópia falha

- Primeiro o código de saída: encerrar em segundos é falha de inicialização (instância única, arquivo ausente, configuração ruim). Encerramento posterior tem registro de falha.
- Reúna logs, linhas de marcação e evento do log Aplicativo do Windows (ID 1000) para o processo. Jogo que falha na saída ou mostra erro próprio pode nunca descarregar seu log; ausência de erro no log não prova nada.
- Passe padrões de log pelo ambiente, não por string de comando, ao consultar eventos.

`gamepool crashlog` faz isso pelo bloco `crash` da configuração.

## <a id="10-test-the-harness-itself"></a>10. Teste a própria estrutura

Uma estrutura incapaz de falhar não vale nada. Crie jogo substituto (script que mantém mutex, busca janela, escreve prontidão e falha) e teste as ferramentas contra ele:

- Processos reais para o que precisa ser real: PIDs, encerramentos, mutexes, classes de janelas, portas, pipes.
- Chamariz com mesmo nome em todo teste de encerramento.
- Variantes de mutação: quebre deliberadamente uma proteção (encerrar por nome, vincular tudo, nunca expirar concessão) e exija falha na mesma verificação. Se continuar passando, não testa nada.

Ambas fazem isso: `python -I tools/gameslot/run_tests.py` e `python -I tools/gamepool/run_tests.py` exibem `ALL OK` somente se toda verificação passar e toda variante for detectada.

## <a id="checklist-for-an-agent"></a>Lista de verificação para agentes

- [ ] Vaga reservada antes de iniciar e liberada depois de encerrar todas as cópias.
- [ ] Cada cópia em pasta própria com hardlinks; configurações, salvamentos e logs privados.
- [ ] Instalação, configurações e salvamentos do usuário protegidos e com hashes antes e depois.
- [ ] Verificação de instância única resolvida dentro do processo ou por sessão/ambiente isolado.
- [ ] Cópias desvinculadas, minimizadas, uma por vez, esperando prontidão de cada uma.
- [ ] Todos os PIDs registrados com criação; nada além deles encerrado.
- [ ] RAM livre verificada antes de outra cópia iniciar.
- [ ] O teste falha quando sua proteção é quebrada (variante de mutação).
