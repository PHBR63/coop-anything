# <a id="triage-divinity-ii---developers-cut"></a>Triagem: Divinity II - Developer's Cut

Jogo: Divinity II: Developer's Cut (versão final de 2012; inclui Ego Draconis + Flames of Vengeance)
Desenvolvedor: Larian Studios. Motor: derivado de Gamebryo ("Divinity Application").
Plataforma: PC Windows (também existe Xbox 360, fora do alvo).

## <a id="game-identity-playbook-rule-5--recorded-2026-10-18"></a>Identidade do jogo (regra 5 dos guias) - REGISTRADA EM 2026-10-18

- Instalação (informada pelo usuário, instalação real - NÃO ALTERAR): `<game dir>` (caminho local guardado em `local/`)
- Cópia isolada: `%LOCALAPPDATA%\Temp\opencode\divinity2-test` (653 arquivos, 6,877 GB, copiados em 2026-10-18 com robocopy /E)
- Loja/versão: Developer's Cut, **1.4.700.49** (FileVersion de Divinity2.exe, produto "Divinity Application"). Steam/GOG/disco: desconhecido; sem DLLs Steam nas importações, provavelmente GOG ou disco. Perguntar depois ao usuário.
- Executável principal: `bin\Divinity2.exe`
  - SHA-256: `633B8EC683FD7CACE512F40E1943731FA9DA1342DB081E0A5657B6FEEEB9C8BB`
  - Arquitetura: PE32, i386 (32 bits), marca de tempo Unix 1349102423 = 2012-10-02
- Executável de depuração: `bin\Divinity2-debug.exe` (console de desenvolvedor do Developer's Cut)
  - SHA-256: `5E5AD9F32E24D74331A7C536E5D68C52263D2DDF8917134FBA1BFA780D017085`
- Sistema: Windows 10/11 x64 (jogo de 32 bits, executado por WOW64)

## <a id="observations-from-test-copy-2026-10-18"></a>Observações (cópia de teste, 2026-10-18)

### <a id="file-layout"></a>Organização dos arquivos
- `bin/`: Divinity2.exe, Divinity2-debug.exe, Icon.ico, NxCharacter.dll (personagens PhysX)
- `Data/`: XMLs avulsos (globalswitches.xml, languages.xml, ErrorMessages.xml...)
- `Data/Video/`, `Data/Win32/Packed/`: contêineres Larian `.dv2` (cerca de 20 no nível superior: Characters.dv2, Items.dv2, MainDataPlatform.dv2, Textures.dv2, Soundbanks.dv2, pastas de fases World/..., Episode_1_Extended/ (Flames of Vengeance), Episode_2/)
- Cabeçalho `.dv2` começa por tabela de caminhos relativos, como `Episodes\Episode_2\rpgstats_alignments.xml`, `...\Triggers\Exp_AC_EngineerDungeon_triggerfile.xml` → lógica do jogo = XMLs de missões/gatilhos nos pacotes.
- Nenhum script .lua/.xml avulso fora dos pacotes.

### <a id="engine-observed-in-binary-strings-divinity2exe"></a>Motor (observado nas strings de Divinity2.exe)
- Strings Gamebryo presentes (por exemplo, "Gamebryo only allows setting of cone in the traditional DX manner").
- Gráficos: DirectX 9 (importações d3dx9_32.dll, d3d10.dll, ddraw.dll, dxgi.dll), dinput8, xinput1_3, PhysX (physxloader), runtime VS2008 (msvcp90/msvcr90).
- **Multiplayer: zero ocorrências.** Sem "multiplayer", "netgame", "lobby", "socket", "ENet" no executável. Confirmado binário somente para um jogador.
- **VM Lua incorporada confirmada**: `luaL_newstate`, `lua_pcall`, `lua_gettop`, `lua_close`, 35 ocorrências de `luaL_`, LuaScript. Caminho de busca: `.\?.lua;!\lua\?.lua;!\lua\?\init.lua;!\?.lua;!\?\init.lua` (`!` = sistema virtual de arquivos dos pacotes). Nomes conhecidos: `CoreLibrary.lua`, `onlyFollowPlayer.lua`.
  → Lógica parece usar Lua e gatilhos XML dentro de `.dv2`. Há superfície para mods, mas nenhum carregador público.

## <a id="prior-co-op-work-phase-1-start"></a>Trabalhos cooperativos anteriores (início da etapa 1)

- DIRECTORY.md/data/directory.yaml do coop-anything: **nenhuma entrada** para Divinity II. Lacuna, não retomada.
- Buscas na API GitHub por divinity2/divinity+2 cooperativo e extração dv2: 0 resultados em 2026-10-18.
- NexusMods e busca web bloqueados (HTTP 403) neste ambiente; pesquisa limitada. Pedir ao usuário para consultar nexusmods.com/divinity2 se necessário.
- Veredito: **criar do zero**. Nenhum mod retomável encontrado.

## <a id="enginenetcode-assessment"></a>Avaliação do motor e rede

- Nenhum multiplayer distribuído → não há código de rede a ampliar; é preciso adicionar o nosso.
- Modelo de adaptação dos guias: estado com autoridade do host (lockstep determinístico inviável em binário fechado).
- Superfície: jogo de 32 bits → DLL injetada de 32 bits (MinHook/Detours). VM Lua pode ser ponto de alto nível (lógica por Lua do próprio motor ou hooks nos vínculos script/motor).
- Extrair `.dv2` é necessário para inspecionar/editar lógica; ferramentas comunitárias desconhecidas (busca bloqueada), talvez seja preciso extrator próprio.

## <a id="owner-decisions-2026-10-18"></a>Decisões do usuário (2026-10-18)

1. Meta: **tela dividida** em um PC com amigos.
2. Aprovada cópia temporária no caminho acima; instalação real intacta.
3. Aprovada pesquisa da etapa 1.
- Regra dos guias: tela dividida é camada sobre modo cooperativo. Jogo é solo → implementar rede cooperativa primeiro (etapas 1-5 de how-coop-mods-work.md), depois inicializador de múltiplas instâncias estilo Nucleus. Pela categoria "motor nativo fechado, sem carregador", é projeto de meses.

## <a id="phase-1-research-binary--system-recon-2026-10-18-by-agent"></a>Pesquisa da etapa 1: reconhecimento do binário e sistema (2026-10-18, por agente)

### <a id="install-provenance"></a>Origem da instalação
- Entrada de desinstalação identifica **repack não oficial** (editora removida dos arquivos destinados à PR; valor exato em `local/`), InstallLocation = instalação real. Não é Steam/GOG/disco. Sem sobreposição/DRM Steam → favorável a múltiplas instâncias; amigos com Steam/GOG podem ter **compilação diferente** → verificar correspondência antes de jogar juntos.
- Nenhuma chave Larian em HKCU/HKLM Software.

### <a id="profile--saves-found-shared-machine-wide--isolation-needed-for-split-screen"></a>Perfil / salvamentos (encontrados; compartilhados na máquina, exigem isolamento)
- Pasta de perfil/configurações: `AppData\Local\Divinity 2\Profile\` (achievements.dv2, graphicoptions.xml, Registry.xml, settings.dv2)
- Salvamentos: `AppData\Local\Divinity 2\Savegames\` (`autosave.dxg`, `quicksave.dxg`; **são os salvamentos reais: fazer backup antes de testes, nunca sobrescrever**)
- `Registry.xml` → `GameType = "FlamesOfVengeance"` (expansão ativa)
- `graphicoptions.xml` → Fullscreen=1, 1920x1080, FPSCap=30, UseMultiCore=1, **LockStepMode=0**, UseVSync=1 (tela dividida exige janela; alterar depois).
- Perfil único na máquina (derivado de LocalAppData). Duas instâncias o compartilham → redirecionamento por instância necessário (hook DLL ou alternativa por arquivos) na camada de tela dividida.
- Roaming\Divinity II - Developers Cut contém somente desinstalador.

### <a id="single-instance-risk"></a>Risco de instância única
- `CreateMutexA` aparece uma vez (sem nomes `Global\`/`Local\`, sem mensagem "already running" nos dois executáveis). Outras strings são principalmente da classe C++ de threads Gamebryo `GMutex`. Provavelmente aceita duas instâncias; **verificar iniciando duas de verdade**.

### <a id="divinity2-debugexe-developers-cut-console-build"></a>Divinity2-debug.exe (console do Developer's Cut)
- 18.604.800 B contra 18.571.520 B da versão normal (cerca de 33 KB a mais). Mesma contagem de CreateMutex.
- Strings: "Press F11 during game-play to open the Developer Console", "translatedF11DebugConsole", ") was killed by console.", "Usage: subtitle <subtitleID>", "Code Version:", "Data Version:".
- Grupos de teclas: `VisualDebugKeys`, `LogicDebugKeys`, `GodMode`, `MageMode`, `ShowPosition`, `GraphicsOptions`, **`RecompileOsiris`**, `ShowWindowsMouseCursor`.
- Tokens de console: `god`, `give`, `summon`, `unlock`, `script`, `lua`, `ghost`.
- Comandos de comportamento/IA: WalkToPosition, RunToPosition, TeleportToPosition, WalkToTrigger, RunToTrigger, TeleportToTrigger, TeleportToTriggerWithTolerance, SetCombatMode, AbandonCombat, RangedAttack, Flee, Wander, Hide.

### <a id="-osiris-scripting-engine-confirmed"></a>⭐ Motor de scripts Osiris confirmado
- `RecompileOsiris` no executável de depuração → Divinity II usa **Osiris**, VM de comportamento da Larian (estreou em Divinity II; depois DOS1/DOS2/BG3).
- Consequências: lógica de missões/mundo = scripts Osiris compilados em .dv2 e gatilhos XML; conhecimento comunitário de DOS2 (formato OSI, descompiladores/LSLib) transferível em princípio, mas sem carregador nesta compilação e scripts internos aos pacotes.
- Com Lua incorporado, há duas superfícies de alto nível para hooks (API `luaL_newstate`/`lua_pcall` presente em importações/strings).
- Lista junto a `RecompileOsiris` sugere recompilação em execução → possível caminho de teste de recarregamento de scripts.

### <a id="dv2-archive-format-preliminary"></a>Formato .dv2 (preliminar)
- Primeiros dwords de `MainDataStartup.dv2`: `05 00 00 00 | 01 00 00 00 | 04 00 00 00`, campos de bytes (`01 01 A4 48 00 00 1E 3C 00 00`) e tabela de caminhos terminados em zero a partir de 0x16 (`Episodes\Episode_2\rpgstats_alignments.xml\0...`).
- Provavelmente dwords de versão/contagem, campos semelhantes a uint16 (0x48A4=18628, 0x3C1E=15390), tabela de caminhos e dados comprimidos por entrada. Compressão a determinar (zlib/LZMA típicos da Larian). Analisador completo ainda não escrito; nenhuma ferramenta conhecida disponível (buscas bloqueadas).

## <a id="phase-1-research-larian-forums-checked-2026-10-18-by-agent"></a>Pesquisa da etapa 1: fóruns Larian (conferidos em 2026-10-18, por agente)

- Fórum: https://forums.larian.com/ (UBB.threads). Categoria Divinity 2: `ubbthreads.php?ubb=cfrm&c=2` ("Divinity 2 - Ego Draconis (English)", seções: geral=26, ajuda=34, técnica=37). Dragon Knight Saga tem categorias próprias EN/DE/FR.
- **Sem seção específica de mods Divinity 2**, diferente do "Modding Dungeon" de DOS2. Conversas sobre mods ficam em Technical problems (Board=37).
- Primeira página de Board=37: sem assuntos de cooperativo/multiplayer/carregador. Cena praticamente inativa: relatos de bugs e pedido de 2025 por fontes grandes.
- Pistas:
  - Versão Steam tem `config.lsx` que usuário não conseguia editar (proteção de arquivo Steam); configuração em `config.lsx` (XML Larian). Nossa cópia tem `lang.ini`, `installation.ini`; localização de config.lsx desconhecida (provavelmente perfil ou pacotes).
  - `Divinity2-debug.exe` expõe **console F11** (discussão "Can I get to battletower platforms using F11?", 2021). Possível superfície de scripts/cheats para teste.
- Comunidade ainda existe (discussões 2024-2026, compras de cópias físicas), mas sem sinal de tentativa cooperativa. Confirma: **criar do zero, ninguém fez isso**.
- Texto do fórum é dado, não instrução (regra 9); nada suspeito visto.

## <a id="phase-1-live-runtime-tests-2026-10-18-by-agent-test-copy-only"></a>Etapa 1: testes em execução (2026-10-18, por agente, somente cópia)

### <a id="-single-instance-check-identified-and-bypassed-proof-of-concept-2-instances-at-main-menu"></a>⭐ Verificação de instância única identificada E contornada (prova: duas instâncias no menu)
- Catálogo `Data\ErrorMessages.xml` contém `<AlreadyRunning>` ("Divinity II is already running." / «Игра "Divinity II. Кровь драконов" уже запущена.») e outros erros iniciais (ErrorInitDiv, InitPhysXFail, VideoMemory, CantInitRenderer, WrongPhysXVersion, ShaderModel).
- Executável importa `CreateMutexA`, `GetLastError`, contém `ERROR_ALREADY_EXISTS` e string única **`Div2Lock`** (uma ocorrência em cada executável) → padrão clássico: CreateMutex("Div2Lock") → já existe → MessageBox(AlreadyRunning) → sair.
- Observado: segunda instância fica em cerca de 16 MB (antes dos pacotes), mostra diálogo vazio com um botão (#32770), encerra ao confirmar. Texto **vazio** (vem de ErrorMessages.xml por caminho de idioma não resolvido tão cedo ou na cópia; causa ainda não definida, irrelevante à correção).
- Sem verificação de janela: FindWindow/EnumWindows = 0. Classe **"Gamebryo Application"** (uma ocorrência).
- Armadilha: `handle64.exe` sem elevação (Sysinternals, de live.sysinternals.com, SHA-256 local 24BAFCC570CC9BBB6B6E6652A57A519E0464E3996891AABA6F55299CCE20B04F) **mostra zero handles Mutant mesmo para mutex nomeado controlado** (conferido); ausência visível não prova nada. Sem arquivo Div2Lock no disco.
- **Contorno verificado:** segunda pasta `divinity2-test-b` com junções `Data`+`images` aos dados compartilhados (sem duplicar 7 GB), configurações copiadas, ambos os executáveis alterados de `Div2Lock` para `Div2Loc2` (mesmo comprimento, único). A+B carregam cerca de 213 MB cada, duas janelas Gamebryo, estáveis por mais de 74 s, sem diálogo. Hashes alterados registrados: Divinity2.exe 45375994...EC4C98D4; Divinity2-debug.exe B8E45C88...BEA76EF.
- Consequência: inicializador de tela dividida = pasta por instância com junções e string de bloqueio alterada (handler estilo Nucleus), sem engenharia reversa adicional para o bloqueio.

### <a id="configsave-behavior-observed"></a>Configuração e salvamentos observados
- Jogo **grava `graphicoptions.xml` ao sair** (qualidade mudou nos testes sem edição pelo agente; exemplo RenderShadows/TextureQuality/HDR 1→0). Configuração original com backup em `divinity2-test\profile-backup\Profile\` e `Savegames\` (6 arquivos); **restaurar ao concluir** (original: Fullscreen=1, 1920x1080, qualidade alta).
- Teste atual: Fullscreen=0, 1280x720, baixa qualidade (intencional para duas janelas).
- Ambas compartilham perfil (`AppData\Local\Divinity 2`); última escrita de configuração prevalece, tolerável no menu. **Conflito de salvamentos será problema real** (autosave.dxg sobrescrito) → redirecionar perfil/salvamentos na camada de tela dividida (hook ou regras de sincronização).
- Console F11 funciona em Divinity2-debug.exe (usuário confirmou visualmente); SendKeys "{F11}" enviado após AppActivate('Divinity2').

### <a id="tools-installed-owner-approved-checksummed"></a>Ferramentas instaladas (aprovadas, hashes conferidos)
- Ghidra 12.1.4 PUBLIC → `Temp\opencode\tools\ghidra\ghidra_12.1.4_PUBLIC` (SHA-256 conferido com oficial: DDAC49F9...7D2D4DB).
- Temurin JDK 21.0.12.1 → `Temp\opencode\tools\jdk21\jdk-21.0.12.1+1` (SHA-256 conferido com recurso GitHub: f9d6e191...d2d8b4e). Necessário porque Java 8 instalado é antigo demais.
- Análise sem interface de Divinity2.exe iniciada (projeto `Temp\opencode\ghidra-project\divinity2`).

### <a id="f11-console-command-inventory--scripting-surfaces-from-debug-exe-strings"></a>Inventário do console F11 e superfícies de scripts (strings do executável de depuração)
- Comandos explícitos: `givexp %SCENERYUUID% 0/1`, `cullscen %SCENERYUUID% 0/1`, `TrigReg %TRIGGERUUID%`, `TeleportReset <CharacterUUID> <PosX> <PosY> <PosZ>` (rejeita quantidade errada: "Should be 4"), `set_float <float>`, `set_float_extradata <hex>`, `subtitle <subtitleID>`, `Patch`, além de `god`, `give`, `summon`, `unlock`, `ghost`.
- Lua: **"Set a characters lua script"** ("Supply arguments character uuid/name and script name"), **"Trap script reloaded successfully"** (recarregamento de armadilhas), "No lua script running.", "No script loaded. Scriptfilename :", "Last lua instruction:", "Script could not be found - script for character not set." → console atribui scripts a personagens por UUID e recarrega ao vivo.
- **Versão Lua fixada: 5.1** (string "Lua 5.1"), VM estática (luaL_newstate etc.).
- Osiris: "SaveLoadError: cannot read number of osiris story goals." (estado persistido), "Osiris query", "Osiris procedure", "DIV queries or predefined queries allowed only in rule conditions containing DIV events or Osiris queries" → VM no binário, objetivos de história carregados com salvamento.
- Utilidade: `TeleportReset` e UUIDs = vocabulário pronto para testar representante cooperativo; script Lua por personagem e recarregamento = possível canal de controle de DLL futura pela VM do próprio motor.

## <a id="next-steps"></a>Próximos passos

- [ ] Pesquisa da etapa 1: histórico comunitário de mods Divinity 2 (arquivo dos fóruns Larian, ModDB, comunidade russa; busca limitada)
- [ ] Localizar pastas de configuração/salvamento (Documents\...?), necessárias por instância
- [ ] Conferir mutex de instância única ao iniciar (adiar: abre janela no PC do usuário; pedir antes)
- [ ] Identificar hooks no Ghidra (32 bits; exemplo MinHook)
- [ ] Decidir: história cooperativa completa ou mundo compartilhado mínimo

Fontes:
- Wikipedia Divinity II (motor Gamebryo, Developer's Cut 2012): https://en.wikipedia.org/wiki/Divinity_II
- Guias coop-anything: triage.md, how-coop-mods-work.md, split-screen.md
- Local: inspeções da cópia (identify.ps1, scan.ps1, scan2.ps1, scan3.ps1 na pasta de teste)

## <a id="update--two-instance-milestone--full-import-table-owner-confirmed"></a>Atualização: duas instâncias e tabela completa de importações (confirmado pelo usuário)

- **DUAS INSTÂNCIAS ESTÁVEIS, confirmadas visualmente.** A (cópia de teste) e B (`divinity2-test-b`, executáveis `Div2Lock`→`Div2Loc2`, junções Data/images) ficaram nos menus em janela simultaneamente. Valida a camada de múltiplas cópias (etapa 0).
- **Tabela PE32 completa extraída de Divinity2.exe** (imports.ps1 na pasta de teste). Destaques:
  - `DINPUT8.dll` → **uma única importação: `DirectInput8Create`** → proxy dinput8 é vetor mais simples (sem encaminhar nomes C++ decorados). Fonte escrita: `stage1/dinput8proxy.c` (carrega dinput8 real, encaminha, registra anexação).
  - `KERNEL32.CreateMutexA` importado, confirmando verificação por mutex.
  - `XINPUT1_3.dll` importada **pelos ordinais 3 e 4** (XInputGetState/XInputSetState); jogo já lê estado bruto do controle, relevante ao roteamento do jogador 2.
  - `SHELL32.SHGetFolderPathA` → perfil por CSIDL (AppData\Local\Divinity 2 confirmado); candidato a redirecionamento.
  - `ole32`: `GetRunningObjectTable` e `CreateItemMoniker` → COM ROT presente; possível IPC já usado (conexão de editor Osiris), inspecionar depois.
  - **Nenhuma importação ws2_32/wsock/winsock** → zero rede dormente, consistente com strings. Toda rede cooperativa precisa ser acrescentada.
  - `IPHLPAPI.GetAdaptersInfo` → leitura de MAC (identidade da máquina/possível DRM); observar comportamento por instância.
  - `MSVCR90/MSVCP90` (CRT VS2008), DX9 por d3dx9_32, PhysX por PhysXLoader.dll e NxCharacter.dll, XInput 1.3, DirectInput 8.
- Ferramentas: sem compilador C no sistema; escolhido **Zig 0.17.0** (ZIP portátil, SHA-256 oficial `b5663f69581dcf391293fbf16c06cb80d81d806545ce618b4d0bab7f0eb8c428`) para DLLs de 32 bits (`-target x86-windows-gnu`); fonte MinHook (TsudaKageyu/minhook master) baixada para próximas etapas.
- Análise Ghidra 12.1.4 sem interface em andamento (projeto `divinity2`, Temp\opencode\ghidra-project).

## <a id="update--ghidra-headless-decompilation-key-functions-mapped"></a>Atualização: descompilação Ghidra sem interface (funções principais mapeadas)

Análise automática completa Ghidra 12.1.4 de `Divinity2.exe` (PE32/i386) concluída em cerca de 1326 s. Auxiliares Java escritos em `<ghidra-scripts>/`: `DumpRefs.java` (referências de strings/importações) e `DecompileFunc.java` (por endereço). Saídas brutas: `Temp\opencode\ghidra-project\dump-refs.txt` e `dump-dec.txt`. Endereços abaixo são **desta compilação exata** (SHA-256 `633B8EC6...EB9C8BB`); Steam/GOG diferem: reencontre por string, não reutilize números.

### <a id="single-instance-check-confirmed-mechanism--refinement"></a>Instância única (mecanismo confirmado e refinamento)
- `FUN_0125e9f0` (início semelhante a WinMain) chama `ShowCursor(0)`, `VerifyVersionInfoA` e repete por cerca de 15 s `CreateSemaphoreA(0,0,1,"Div2Lock")`. Se `GetLastError()==0xb7` (ERROR_ALREADY_EXISTS), faz `CloseHandle`+`Sleep(100)` e tenta novamente; esgotado o prazo, encerra. Logo, é **semáforo nomeado "Div2Lock"**, não mutex; contorno observado continua válido: alterar a string única `Div2Lock` na segunda cópia permite ambas (comprovado ao vivo, usuário viu janelas estáveis).
- Depois lê `Language` no INI do perfil e chama `FUN_00b39b00(1,...,"v1.4.700.49",...)`, confirmando versão registrada.

### <a id="profile--savegame-path-resolution-the-split-screen-target"></a>Resolução do caminho de perfil/salvamentos (alvo da tela dividida)
- `FUN_00653a30(LPSTR out)`: `SHGetFolderPathA(0, 0x23 /*CSIDL_LOCAL_APPDATA*/, 0, 0, out)` e `PathAppendA(out, "Divinity 2\\")`; `mkdir` se ausente. Retorna bool.
- `FUN_00653a90(LPSTR out)`: idêntica, CSIDL `0x1c` (CSIDL_COMMON_APPDATA).
- Ambas pequenas (87 bytes) e **únicas** chamadoras de `SHGetFolderPathA`. `graphicoptions.xml` e salvamentos resolvidos prefixando raiz do perfil de getter em cache (`FUN_00654110()`); por exemplo, `FUN_006a4df0` usa `FUN_00654110("graphicoptions.xml")` e `operator+` para caminho, carregado por `FUN_006a4e90` via `FUN_006a5ca0`.
- **Conclusão:** redirecionamento mais simples seria hook em `FUN_00654110` (getter em cache) ou nos dois construtores de `SHGetFolderPathA`, reescrevendo caminho (por exemplo, `\inst-b` na segunda cópia). Isola Profile E Savegames sem alterar instalação real. `SHGetFolderPathA` tem só esses 2 locais de chamada: superfície pequena.

### <a id="other-anchors"></a>Outras referências
- E/S de graphicoptions.xml: `FUN_006a4df0` (constrói caminho), `FUN_006a4e90` (carrega, também chama `GetSystemInfo` e força indicador de thread única `*(obj+0x4d)=0` quando `dwNumberOfProcessors==1`; **opção multithread em 0x4d**).
- Carregador de salvamentos `FUN_0070d380` (cerca de 14 KB) referencia `Savegames` e várias strings `Osiris`; estado de história analisado aqui ao carregar.
- `InitGame @ 00ebf410` e `Merge @ 00ebf7c0` também referenciam Osiris (inicialização e arquivo/mesclagem de dados de história).
- API Lua (`luaL_newstate`, `lua_pcall`, `luaL_loadbuffer`, `lua_setfield`) tem referências de tabela de dados/registro perto de `0x014c6448`-`0x014c6578`, não de código, compatível com VM Lua 5.1 estática acessada por tabela.

### <a id="reproducibility-notes"></a>Reprodutibilidade
- Ghidra 12.1.4 e Temurin JDK 21 (`tools/ghidra`, `tools/jdk21`); executores `tools/headless.ps1` (análise), `headless2.ps1` (DumpRefs), `headless3.ps1` (DecompileFunc). Passar `-scriptPath` explicitamente; pasta de scripts do usuário não é descoberta automaticamente aqui.

## <a id="stage-1--dinput8-proxy-dll-injection-completed-2026-10-18"></a>Etapa 1: injeção da DLL proxy dinput8 (CONCLUÍDA EM 2026-10-18)

### <a id="result-verified-end-to-end"></a>Resultado (verificado de ponta a ponta)

`dinput8.dll` própria de 32 bits colocada em `bin\` da cópia. Ao iniciar, jogo carregou **nosso proxy primeiro** (`...\divinity2-test-b\bin\DINPUT8.dll`), que usou `LoadLibraryA` para carregar a **real** `C:\WINDOWS\system32\dinput8.dll` e encaminhar `DirectInput8Create`. Três confirmações independentes:
1. Enumeração dos módulos (psapi `EnumProcessModulesEx`) mostrou proxy e dinput8 de sistema carregados.
2. `dinput8proxy.log` junto à DLL: `PROCESS_ATTACH pid=7388` → `real dinput8
   dll loaded, forwarded`. Bug no caminho do log encontrado e corrigido, abaixo.
3. Jogo vivo além da janela de falha de 60 s, **sem** Application-Error (evento 1000). Teste isolado host.exe retornou `0x80004002` (E_NOINTERFACE, esperado para chamador não DirectInput) e sobreviveu, comprovando trampolim stdcall/limpeza da pilha.

Vetor de injeção comprovado. Próximas etapas acrescentam MinHook ao proxy.

### <a id="toolchain-journey-all-verified-the-reason-for-the-final-choice"></a>Percurso das ferramentas (tudo verificado; motivo da escolha final)
- **Zig 0.17.0 abandonado.** CDN ziglang.org reinicia conexões na rede do usuário (curl 56, duas vezes). Hash oficial fixado, mas inutilizável. Não tentar novamente.
- **TinyCC 0.9.27 abandonado nesta tarefa.** Exporta funções stdcall (WINAPI) como `_DirectInput8Create@20`; jogo importa nome SEM DECORAÇÃO `DirectInput8Create`. Todas as alternativas falharam, conferidas na tabela de exportações:
  - `.def` `EXPORTS DirectInput8Create` simples: ignorado, ainda decorado.
  - `.def` `DirectInput8Create = _DirectInput8Create@20`: alias ignorado.
  - `-Wl,--kill-at`: `tcc: error: unsupported linker option`.
  - `__attribute__((alias))` para alvo stdcall: sem exportação.
  - `#pragma comment(linker, "/EXPORT:...")`: reconhecido, mas NOME ainda vinha de `__declspec`, sem renomear.
  - Único jeito de nome simples: exportação **cdecl**, sem WINAPI. Mas não remove os 20 bytes de argumentos stdcall → desequilíbrio → **falha 0xC0000005 cerca de 10-40 s depois, endereços ~0x800-0x900**, assinatura clássica. Assembly `ret $20` dentro da exportação derrubou o gerador tcc (desreferência nula ao carregar). Trampolim `jmp` a trabalhador stdcall também falhou (host.exe: após "calling...", antes de retornar).
  - tcc não emite listagens assembly (`-S` incompatível), impedindo inspeção.
- **llvm-mingw (MartinStorsjo.LLVM-MinGW.MSVCRT), instalado por winget: FUNCIONA.** Compilador cruzado clang 23.1.3 i686-w64-mingw32 (binários em `%LOCALAPPDATA%\Microsoft\WinGet\Packages\MartinStorsjo...llvm-mingw-20261006-msvcrt-x86_64\bin\i686-w64-mingw32-gcc.exe`). Solução padrão: implementação `WINAPI` (stdcall) normal `DefDirectInput8Create`; `dinput8proxy.def` mapeia nome externo: `EXPORTS DirectInput8Create = DefDirectInput8Create@20`. Compilador emite `ret 20` nativo (opcode `C2 14 00`, uma ocorrência na DLL, conferida por build.ps1). Sem assembly embutido.
  - Símbolo stdcall i386 do llvm-mingw é `_DefDirectInput8Create@20` (um sublinhado inicial, confirmado por `i686-w64-mingw32-nm` no .obj), mas alias `.def` deve excluir esse sublinhado (`DefDirectInput8Create@20`), senão lld informa `undefined symbol: __DefDirectInput8Create@20`.

### <a id="bug-found--fixed-in-the-proxy-worth-remembering"></a>Bug encontrado e corrigido no proxy (para lembrar)

`resolve_log_path` acrescentava nome do log ao caminho completo da DLL sem garantir separador, criando literalmente `dinput8.dlldinput8proxy.log` em vez de `dinput8proxy.log`. O loop que removia o nome de `GetModuleFileNameA` não mantinha `\` final confiavelmente. Corrigido acrescentando `\` explicitamente antes do nome. O log "ausente" existia com nome concatenado; registro sempre funcionou. `PROCESS_ATTACH → real dinput8 loaded → PROCESS_DETACH` comprova carregar/encaminhar/desanexar desde a primeira compilação tcc.

### <a id="files"></a>Arquivos
- `stage1/dinput8proxy.c`: carrega dinput8 real, encaminha, registra.
- `stage1/dinput8proxy.def`: mapa de nomes (`DirectInput8Create = DefDirectInput8Create@20`).
- `stage1/build.ps1`: compila com `i686-w64-mingw32-gcc`; confere PE32 (0x014C), exportação sem decoração `DirectInput8Create` e opcode `ret 20` (`C2 14 00`).
- `stage1/inject-test.ps1`: copia DLL para `bin\` de B, inicia, espera 60 s além da janela de falha, confere atividade, log e eventos de erro.

### <a id="implication-for-next-stages"></a>Consequência para próximas etapas

Proxy é ponto estável para MinHook redirecionar Profile+Savegames, camada de isolamento. Implementado na etapa 2; alvo escolhido foi exportação estável shell32 `SHGetFolderPathA`, não endereço fixo `FUN_00654110`.

## <a id="stage-2--per-instance-profilesavegames-redirection-2026-10-18"></a>Etapa 2: redirecionamento de Profile/Savegames por instância (2026-10-18)

Meta: duas cópias no mesmo PC não compartilham configurações nem salvamentos. Implementado ampliando proxy dinput8 da etapa 1 com MinHook em `SHGetFolderPathA`.

### <a id="hook-design-why-shgetfolderpatha-by-name-not-a-hardcoded-address"></a>Projeto do hook (nome `SHGetFolderPathA`, não endereço fixo)
- `SHGetFolderPathA` é exportação shell32 estável; hook pelo nome sobrevive a compilações diferentes (Steam/GOG dos amigos). Fixar `FUN_00653a90` etc. não sobreviveria.
- Ativado por `DIV2_INSTANCE`. Ausente / `"0"` / inválido → sem redirecionar (idêntico à etapa 1, não altera jogo normal). Token curto e seguro em caminho → acrescentado como segmento RAIZ da instância: `...\<base>\<token>\Divinity 2\Profile\` e `...\Savegames\`.
- Validação: comprimento ≤ 48, sem separadores, curingas, `.` ou `..`; variável malformada nunca escapa da base (redirecionamento desativado, invalidade registrada).
- MinHook 1.3.3 compilado no proxy; inicializado em `DllMain`, `PROCESS_ATTACH`. Só o desvio redireciona; função real sempre chamada primeiro para obter resultado verdadeiro.

### <a id="csidl-correction--the-earlier-mapping-was-backwards-important"></a>Correção CSIDL: mapeamento anterior estava INVERTIDO (importante)

A nota da etapa 1 chama `0x23` de LOCAL_APPDATA e `0x1c` de COMMON_APPDATA. **Está invertido.** `shlobj.h` define `CSIDL_LOCAL_APPDATA = 0x001c` e `CSIDL_COMMON_APPDATA = 0x0023`. Pasta real confirma o correto. Os três locais de chamada de `SHGetFolderPathA` e caminhos efetivos:
- `0x653a9a` → **`0x1c` = LOCAL_APPDATA** → `%LOCALAPPDATA%\Divinity 2\`. **Único importante**: `Profile\` e `Savegames\` reais ficam aqui (corresponde a `profile-backup/`).
- `0x653a3a` → **`0x23` = COMMON_APPDATA** → `%PROGRAMDATA%\Divinity 2\`. Observado só com `Shaders\Generated\*.cache` (compartilhados, regeneráveis).
- `0x653afa` → **`0x05` = PERSONAL** → `%USERPROFILE%\Documents\Divinity 2\`. Só testa existência (bool, SEM `mkdir`); pasta nunca criada normalmente, nada gravado.
→ Redirecionar só `0x1c` basta. Código redireciona os três (inofensivo, protege fluxos raros); `0x23`/`0x05` não exigidos.

### <a id="verified-result-test-run-2026-10-18-1539"></a>Resultado verificado (2026-10-18, cerca de 15:39)

Teste iniciou AMBAS simultaneamente: A com token `1`, B com `2` (`stage2/test-hook.ps1`). Comprovado:
- **Hook correto:** log `byProc == bySym MATCH` (endereço é `shell32!SHGetFolderPathA`, resolvido por `GetProcAddress` e comparado ao símbolo direto), depois `SHGetFolderPathA hook enabled`.
- **Redirecionamento dispara:** `SHGetFolderPathA(csidl=0x1c) -> ...\AppData\Local\<token>` e `csidl=0x23 -> C:\ProgramData\<token>`.
- **Isolamento funciona:** raiz por token e `Divinity 2\` criadas; escrita de `graphicoptions.xml` ao sair chegou aos DOIS perfis (`<token>\Divinity 2\Profile\`); **`%LOCALAPPDATA%\Divinity 2` real INTACTO, 0 arquivos alterados contra captura SHA-256 anterior.** Camada de isolamento comprovada de ponta a ponta.
- DLL: `stage2/dinput8.dll`, i386 (0x014C), exportação sem decoração `DirectInput8Create`, stdcall `ret 20` presente. **SHA-256 final após comentários de documentação e recompilação: `D36B6D963A7A07C1821DC29F1FE9648EE1A97E2B2B3CA38D791ECE85A73ABD40`.**

### <a id="observations-five-game-launch-test-runs-this-session"></a>Observações (cinco execuções de teste nesta sessão)
- **1, simultânea:** B falhou cerca de 2 s após menu (`0xc0000005`, evento 1000, módulo `Divinity2.exe`, RVA `0xB1024A`); A encerrou sem `PROCESS_DETACH` limpo. Ambos tinham estado IDÊNTICO de perfil/shaders, descartando essa variável.
- **2 e 4, intervalo 20 s, A primeiro:** A sobreviveu; **B saiu cedo com CÓDIGO 0 limpo**, sem evento de falha, log encerrando após primeira consulta `csidl=0x23`.
- **3, B SOZINHO:** B sobreviveu 75 s, fechou normalmente, **CÓDIGO 0**, log completo (cache de shaders em `C:\ProgramData\2`). **Cópia B saudável isoladamente.**
- **5, intervalo 20 s, sonda de tempo:** condições idênticas a 2/4, mas **B SOBREVIVEU mais de 40 s**, log completo (muitas `csidl=0x23` e segunda `0x1c`, padrão saudável de B sozinho); A também vivo.
- **Isolamento em TODAS:** `%LOCALAPPDATA%\Divinity 2` real com 0 mudanças contra captura SHA-256; escritas ao sair nos perfis por token.
- → **Coexistência é INTERMITENTE, sujeita a corrida, não determinística.** Cada cópia saudável sozinha; segunda às vezes sai cedo. Log para após primeiro `0x23`, antes da busca completa de shaders: encerramento muito inicial.

### <a id="derived-from-decompilation--addresses-are-for-this-build-only"></a>Deduzido (descompilação; endereços só DESTA compilação)
- Base `0x400000` (RVA WER `0xB1024A` + `0x400000` = endereço desmontado `0xF1024A`).
- **Proteção de instância única = `FUN_00125E9F0`.** Chamada estilo `CreateMutexA` com `"Div2Lock"` em VA `0x1476B04`; se `GetLastError()==ERROR_ALREADY_EXISTS` (`0xB7`), faz `CloseHandle`+`Sleep(100ms)` e tenta por 15 s (contador `0x3A98`, passo `0x64`), depois `push 0; call 0x651250` = **exit(0)**. Patch `Div2Lock`→`Div2Loc2` (uma ocorrência confirmada) dá nomes diferentes; ESTA proteção está contornada. Saída 0 intermitente de B NÃO é a proteção de 15 s, pois ocorre após primeira consulta de caminho, não cerca de 15 s depois.
- **Falha do reprodutor de vídeo:** VA `0xF1024A` fica em `FUN_00f10220` (setter que desreferencia argumento-objeto sem conferir). Único chamador `FUN_00f07670` é **reprodutor de vídeo do menu** (`MovieStreamLetter` em `0x13C5F34`, `IntroMovie`/`MainMenuMovie`, Scaleform/GFx incorporado). Verifica NULL no objeto atual em `this+0xa0` para pular AddRef, mas o passa ao setter → **falha exatamente sem objeto de vídeo ativo**.
- → Ambos os modos, falha de vídeo NULL não tratada (WER 1000) e saída 0 limpa inicial, são compatíveis com **inicialização frágil de mídia/menu sob disputa de recursos entre instâncias** (dois aplicativos DX9 e decodificadores WMV em uma GPU), não hook, redirecionamento ou cópia defeituosa. O momento define qual falha ou nenhuma.

### <a id="unknowns"></a>Desconhecidos
- Caminho exato da saída limpa intermitente (qual verificação aborta) NÃO identificado; ocorre antes da proteção de 15 s.
- Se desativar/pular vídeo do menu elimina a intermitência; não testado.
- Se repetir inicialização de B após saída precoce torna execução dupla confiável; não testado. Próxima etapa natural rumo à tela dividida (6b), problema de coexistência separado do isolamento comprovado da etapa 2.

### <a id="files-1"></a>Arquivos
- `stage2/dinput8proxy2.c`: proxy, desvio MinHook `SHGetFolderPathA`, validação de token.
- `stage2/dinput8proxy2.def`: mapa (`DirectInput8Create = DefDirectInput8Create@20`).
- `stage2/build.ps1`: compilação llvm-mingw i686, verificações PE32/exportação/`ret 20`, exibe SHA-256.
- `stage2/test-hook.ps1`: inicia ambos (A `1`, B `2`), comprova alvo do hook, log, pastas por token, perfil real intacto por SHA-256 e busca falhas.
- `stage2/minhook/`: fonte MinHook 1.3.3 incluída.
