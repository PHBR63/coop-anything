# <a id="tool-catalogue-for-co-op-work"></a>Catálogo de ferramentas para trabalho cooperativo

Público: agente de programação IA e usuário, sobretudo Windows 10/11, com notas relevantes para Linux/Steam Deck.

Como ler esta página:

- "Visto na documentação" indica comando/fato da documentação oficial durante a pesquisa. "Não verificado" indica listagem de terceiros, memória ou falta de confirmação. Confira antes de confiar.
- "Controlável por agente" indica MCP ou CLI programável sem cliques humanos.
- Licenças conforme páginas na pesquisa. Confira LICENSE antes de redistribuir.
- MCPs terceiros usam suas permissões e frequentemente escrevem em depurador/memória. Leia fonte, fixe versão, só use em cópias de teste.

## <a id="legal-and-safety-note"></a>Nota jurídica e de segurança

Não use para contornar antitrapaça on-line, trapacear em sessões alheias ou redistribuir recursos/código sem direitos. Muitas ferramentas limitam escopo a software próprio (REA/RenderDoc explicitamente). Teste mods cooperativos em sessões privadas com amigos.

## <a id="1-reverse-engineering-for-agents"></a>1. Engenharia reversa para agentes

### <a id="11-agent-native-and-mcp-enabled-analysis"></a>1.1 Análise voltada a agentes e com MCP

| Ferramenta | Uso no trabalho cooperativo | Link oficial | Instalação (documentada salvo indicação) | Interface do agente | Licença / custo | Cuidados |
|---|---|---|---|---|---|---|
| REA (Reverse Engineer Anything) | MCP e CLI únicos para vários mecanismos: Hopper, Ghidra ou IDA para nativo, análise estática JS/.NET, JADX para APK, Binwalk/Unblob para firmware, TShark para pacotes. Entrada única útil quando jogo mistura nativo, scripts e tráfego. | https://github.com/morluto/rea | `npx rea-agents setup` (registra no agente e instala instruções de fluxo; reinicie o agente). CLI independente: `npm install --global rea-agents` | MCP e CLI, mesmos fluxos | MIT no REA; mecanismos mantêm licenças próprias e você precisa possuir IDA/Hopper/JEB | Exige Node.js 22.19+, 24.11+ ou 26+. Suporte Ghidra no Windows descrito como experimental. Obtenha só do repositório oficial, rea.tools ou pacote npm. Pode executar/interagir com alvo sob suas permissões. |
| GhidraMCP (LaurieWired) | Descompila, lista funções/classes/importações/exportações e renomeia métodos/dados por cliente MCP contra Ghidra ativo. | https://github.com/LaurieWired/GhidraMCP | Instale ZIP por Ghidra File > Install Extensions, ative GhidraMCPPlugin em File > Configure > Developer; adicione entrada MCP: `uvx --from git+https://github.com/LaurieWired/GhidraMCP ghidra-mcp --ghidra-server http://127.0.0.1:8080/` | MCP (stdio ou HTTP de fluxo em 8081). Sem interface por PyGhidra (exige `GHIDRA_INSTALL_DIR`) | Apache-2.0; Ghidra gratuito | Versão fixada a uma versão Ghidra (12.1.4 na pesquisa); corresponda. Alterações sem interface perdidas sem `--project DIR`. Porta 8080 deve coincidir nos dois lados. |
| Hex-Rays IDA MCP (oficial) | Servidor oficial Hex-Rays: agente controla IDA (descompilar, desmontar, navegar) sem interface por idalib ou com GUI, com logs inspecionáveis. Baseado na biblioteca IDA Nexus, permitindo clientes compartilharem banco. | https://github.com/HexRaysSA/ida-mcp | `uvx ida-hcli mcp install` (instala plugin GUI e oferece plugins de agentes). CLI: `uvx ida-mcp stdio --agent=<name>` ou `uvx ida-mcp http --host 127.0.0.1 --port 8737` | MCP (stdio/HTTP), plugins Claude Code e Codex | MIT; IDA 9.4+ pago com idalib, Python 3.11+, git e uv | README recomenda desativar outros MCP IDA para não confundir agente. Escolha este ou ida-pro-mcp, não ambos. Só compensa se já possui IDA; Ghidra e REA cobrem gratuitamente. |
| ida-pro-mcp (mrexodia) | Expõe descompilação IDA, desmontagem, referências cruzadas, renomeação, tipos e comentários a LLM. `idalib-mcp` evita GUI. | https://github.com/mrexodia/ida-pro-mcp | Claude Code: `claude plugin marketplace add mrexodia/claude-marketplace`, depois `claude plugin install ida-pro-mcp@mrexodia`. Manual: `pip install https://github.com/mrexodia/ida-pro-mcp/archive/refs/heads/main.zip` depois `ida-pro-mcp --install` | MCP | MIT; IDA Pro pago (8.3+, recomendado 9). IDA Free não aceito. Python 3.11+ | Toda chamada exige identificador de sessão `database` de `idb_open`/`idb_list`, não arquivo. README prevê descontinuar GUI em favor de `idalib-mcp`. Agora existe oficial Hex-Rays acima; use um só. LLMs erram conversões numéricas; use `int_convert`. |
| Ghidra sem interface (analyzeHeadless) | Importação/análise em lote de executável/DLL, scripts posteriores extraem funções, strings e vtables para JSON. Melhor padrão para agente sem GUI. | https://github.com/NationalSecurityAgency/ghidra (documentação: analyzeHeadlessREADME na distribuição, cópia em ghidradocs.com) | Incluído no Ghidra. Formato: `analyzeHeadless <projectDir> <projectName> -import <file> -postScript <script> [args] -scriptPath "<dir>"`. Opções documentadas: `-recursive`, `-overwrite`, `-deleteProject`, `-noanalysis`, `-processor`, `-analysisTimeoutPerFile` | CLI, Java ou Python (PyGhidra) | Apache-2.0, gratuito | Opções variam por versão; leia README incluído. "Script not found" normalmente indica `-scriptPath` ausente. Exige JDK. |
| Binary Ninja MCP (fosdickio) | Plugin e ponte expondo análise Binary Ninja por HTTP a clientes MCP. | https://github.com/fosdickio/binary_ninja_mcp (não verificado; listagens MCP de terceiros) | Plugin Manager ou cópia manual; listagens mencionam configuração automática Claude Desktop/Code. Comando exato não verificado | MCP | Uma listagem diz GPL-3.0 (não verificado); Binary Ninja comercial com nuvem gratuita e edição grátis limitada (conferir termos atuais) | Listagens discordam na versão Python. Outro projeto, binaryninja-mcp de MCPPhalanx, aparece como Apache. Avalie antes de usar. |
| radare2 / r2mcp | Desmontador CLI programável; MCP oficial em C controla radare2 por r2pipe. Triagem rápida sem GUI no Windows/Linux. | https://github.com/radareorg/radare2-mcp | `r2pm -Uci r2mcp`. Configuração MCP executa `r2pm` com argumentos `["-r", "r2mcp"]` | MCP (stdio ou HTTP com autenticação bearer) e CLI r2 | LGPL para radare2 (não verificado); gratuito | Use modos somente leitura e isolado. Autenticação bearer HTTP exige ABI radare2 91 ou superior. |
| Rizin | Fork radare2, papel CLI semelhante. | https://rizin.re (não verificado) | Não verificado | CLI; REA menciona Rizin como mecanismo fornecido pelo chamador | Gratuito, família GPL (não verificado) | Nenhum servidor MCP específico confirmado na pesquisa. |

### <a id="12-debuggers-memory-tools-and-instrumentation"></a>1.2 Depuradores, memória e instrumentação

| Ferramenta | Uso no trabalho cooperativo | Link oficial | Instalação | Interface do agente | Licença / custo | Cuidados |
|---|---|---|---|---|---|---|
| x64dbg | Depurador Windows em modo usuário. Descobre leituras/escritas de posição, vida e inventário e pausa em envio/recepção de rede. | https://github.com/x64dbg/x64dbg | Baixe snapshot GitHub Releases/SourceForge, extraia em pasta gravável, execute `x64\x64dbg.exe` ou `x32\x32dbg.exe` (visto na documentação) | Vários plugins MCP comunitários abaixo; sistema próprio de scripts | Código aberto (licença não confirmada na página obtida); gratuito | Variantes MCP com qualidade desigual. Prefira escrita desativada por padrão. Não anexe a jogos com antitrapaça. |
| Servidores MCP x64dbg (comunidade) | Agente define pontos de interrupção, lê registradores/memória, avança. Variantes: SetsunaYukiOvO/x64dbg-mcp (MIT, JSON-RPC HTTP/SSE, escrita desligada), bromoket/x64dbg_mcp (STDIO, 23 ferramentas), Wasdubya/x64dbgMCP (Python, ~40), AgentSmithers/x64DbgMCPServer (C#), rison1337/x64dbgMCP (GPL v3), plugin Zig com bearer | Pesquisar nomes no GitHub; links de listagens de terceiros, não verificados | Por repositório; comandos não verificados aqui | MCP | Variadas, consulte nomes | Manutenção e estrelas não verificadas. Escolha um, leia código, fixe commit. |
| Cheat Engine | Busca de valores, ponteiros, análise de estruturas, scripts Auto Assembler e Lua para automação. Caminho rápido para estado do jogador/mundo na memória. | https://www.cheatengine.org e https://github.com/cheat-engine/cheat-engine | Baixe de Releases (documentado) | Lua no CE. Pontes comunitárias: crain99/ce-mcp, imrx44/mcp (Python/Lua, mais de 40 ferramentas), CheatEngineNet/CheatEngine.Mcp (beta, gateway stdio), bethington/cheat-engine-server-python (só leitura, processos permitidos), un4ckn0wl3z/MemMCP. Todas de terceiros, não verificadas | Gratuito; licença ausente na página obtida | Instalador historicamente inclui ofertas opcionais; leia telas. Recursos de núcleo exigem driver sem assinatura; evite. Frequentemente detectado por antivírus/antitrapaça. Só jogos próprios desconectados ou sessões privadas. |
| ReClass.NET | Monta estruturas C++ a partir de memória ativa, encontra vtables, gera cabeçalhos C++/C#. Converte offsets descobertos em cabeçalho tipado do mod. | https://github.com/ReClassNET/ReClass.NET | Binários na página GitHub Releases | Só GUI; MCP não encontrado | MIT; gratuito | Principalmente Windows x86/x64; núcleo Linux existe, mas exige WSL/Docker para compilar. Plugin Unreal marcado indisponível. |
| Frida | Injeta JavaScript em processo para interceptar funções e registrar argumentos sem compilar DLL. Sondagens rápidas de rede/API. | https://github.com/frida/frida | `pip install frida-tools` (CLI `frida`, `frida-ps`, `frida-trace`), `pip install frida` para Python, `npm install frida` para Node (documentado) | CLI e vinculações Python/Node. MCP: rmorgans/frida-mcp (Python, MIT), nonsleepr/frida-mcp.ts (Bun, Frida 17+). Manutenção não verificada | Licença não nomeada na página obtida; confira COPYING | Hooks podem derrubar jogo ao anexar cedo. Antitrapaça detecta. Versão servidor deve coincidir com cliente. |
| Process Monitor (Sysinternals) | Monitora arquivos, registro e processos: configurações/salvamentos lidos e DLLs carregadas. Ajuda posicionar proxy DLL. | https://learn.microsoft.com/sysinternals/downloads/procmon (URL atual não verificada; citada antiga docs.microsoft.com) | Extraia ZIP, execute `Procmon.exe` (fonte de ajuda de terceiros) | Opções CLI existem (não verificadas); CSV pode ser lido pelo agente | Gratuito, Microsoft | Exige administrador. Filtre bastante ou log fica enorme. |
| API Monitor (rohitab) | Registra chamadas Win32/COM com argumentos. Mostra uso Winsock/DirectInput. | https://www.rohitab.com/apimonitor (não verificado) | Não verificado | GUI | Gratuito (não verificado) | Pesado em jogos 64 bits, pode derrubar alvos. |
| RenderDoc | Captura quadros D3D11/D3D12/Vulkan/OpenGL. Use em compilações/mods próprios para renderização de personagens cooperativos e interface. | https://github.com/baldurk/renderdoc | Instalador ou ZIP portátil nas versões (documentado) | `renderdoccmd` e API Python no repositório; uso não confirmado aqui. Não verificado para agentes | MIT; gratuito | README limita a depuração de programas próprios, não capturas de jogos comerciais não compilados por você. Sem D3D9/D3D10/Metal. |
| Wireshark / TShark | Captura/lê tráfego (LAN/loopback) para descobrir formato de rede ou verificar protocolo próprio. | https://www.wireshark.org | Instalador Windows inclui Npcap (wiki Wireshark) | `tshark -D` lista interfaces; `-f` recebe filtro (tutorial terceiro, não conferido no manual). REA também integra TShark | GPL, gratuito | Captura loopback usa "Adapter for loopback traffic capture" no Npcap atual. Tráfego criptografado/retransmitido Steam não decodifica. |

### <a id="13-pe-and-binary-triage"></a>1.3 Triagem de PE e binários

| Ferramenta | Função | Link | Instalação | Interface do agente | Licença | Cuidados |
|---|---|---|---|---|---|---|
| Detect It Easy (DiE) | Identifica compilador, compactador, protetor e motor para escolher ferramentas (Unity, Unreal ou próprio). | horsicq/Detect-It-Easy no GitHub (não verificado; memória) | Não verificado | GUI e console existem (não verificado) | Gratuito (não verificado) | Detectar compactador indica necessidade de compilação descompactada. |
| PE-bear | Inspeciona cabeçalhos PE, importações, seções. | hasherezade/pe-bear no GitHub (não verificado; memória) | Não verificado | GUI | Gratuito (não verificado) | Bom para conferências rápidas; agente normalmente prefere Python `pefile` (não verificado, amplamente usado). |

### <a id="14-managed-code-and-unity-decompilation"></a>1.4 Descompilação de código gerenciado e Unity

| Ferramenta | Função | Link | Instalação | Interface do agente | Licença | Cuidados |
|---|---|---|---|---|---|---|
| dnSpyEx | Descompila, depura e edita assemblies .NET/Unity Mono (Assembly-CSharp.dll). Via rápida para patch cooperativo Unity Mono. | https://github.com/dnSpyEx/dnSpy | Página de versões | GUI, janela C# interativa | GPL-3.0 | Editar assemblies no disco é frágil nas atualizações; prefira Harmony por BepInEx/MelonLoader. |
| ILSpy / ilspycmd | Descompila .NET para C# para leitura por agentes; exporta projeto inteiro. | https://github.com/icsharpcode/ILSpy | `ilspycmd` como ferramenta dotnet NuGet (comando exato não na página; provavelmente `dotnet tool install ilspycmd -g`, não verificado) | CLI | MIT | Saída para leitura/comparação, não redistribuição. |
| Il2CppDumper | Unity IL2CPP: recupera nomes de tipos/métodos de `global-metadata.dat` e binário; gera scripts IDA/Ghidra/Binary Ninja. | https://github.com/Perfare/Il2CppDumper | `Il2CppDumper.exe <binary> <global-metadata.dat> <outdir>` (documentado) | CLI | Licença ausente na página obtida | Não remove proteção de metadados (fora do escopo no README). Lista Unity 5.3 a 2022.2; versões novas podem exigir Cpp2IL/forks. |
| Cpp2IL | Recuperação IL2CPP alternativa com saída CLI (`cpp2il_out`). | https://github.com/SamboyCoding/Cpp2IL | `Cpp2IL-Win.exe --game-path=C:\Path\To\Game` (documentado) | CLI | MIT | Branch de desenvolvimento em reescrita, instável; compilações noturnas incluem .NET Framework 4.7.2 para Wine/Proton. |

### <a id="15-unreal-engine-4-and-5"></a>1.5 Unreal Engine 4 e 5

| Ferramenta | Função | Link | Instalação | Interface do agente | Licença | Cuidados |
|---|---|---|---|---|---|---|
| UE4SS | Lua/C++ injetados, extratores (cabeçalhos UHT/C++ com offsets, USMAP, recriação UMAP), visualizador ativo de propriedades. Plataforma frequente de mods UE cooperativos. | https://github.com/UE4SS-RE/RE-UE4SS | Extraia ZIP não dev em `{game}/GameName/Binaries/Win64/` (documentado) | Lua (agente escreve mods em texto); documentação docs.ue4ss.com | MIT | Não é imediato; assinaturas AOB podem precisar atualização por jogo. Só Windows. Proxy padrão `dwmapi.dll`. Compilar exige MSVC C++23, Rust e conta GitHub vinculada à Epic para submódulo Unreal. `--disable-ue4ss` ajuda isolar falhas. |
| Dumper-7 | Injeta DLL em UE4/UE5 para gerar SDK C++ (classes, offsets). | https://github.com/Encryqed/Dumper-7 | Compile DLL x64-Release, injete; saída padrão `C:\Dumper-7` (documentado) | Compilar/injetar por CLI; agente lê cabeçalhos | Licença ausente na página obtida | Exige injetor próprio. Substituir offsets só se autodetecção falhar. Use "Build Only" ao compilar SDK no Visual Studio. |
| UnrealDumper (vários) | Outra família de extratores SDK. | Não verificado | Não verificado |  |  | Não pesquisado; prefira UE4SS/Dumper-7 salvo necessidade. |

### <a id="16-decompilation-and-static-recompilation-projects"></a>1.6 Projetos de descompilação e recompilação estática

| Ferramenta | Função | Link | Instalação | Interface do agente | Licença | Cuidados |
|---|---|---|---|---|---|---|
| decomp.dev | Central de progresso de descompilações com correspondência (mais de 80 segundo resumo), alimentada por objdiff. Descobre se já existe descompilação para fork. | https://decomp.dev (obtenção direta não verificada; descrito na busca) | n/a | Web | n/a | Correspondência disponível para poucos jogos; publicar é juridicamente delicado. Não redistribua recursos originais. |
| DecompPipeline | Descompila funções por agentes: preparação Ghidra, modelos trabalhadores econômicos, oráculo de comportamento em emulador, etapa legível, compilação de port nativo. | https://github.com/GeneralAtrox/DecompPipeline | `python decomp.py --project <workspace> setup`, depois `serve` para interface web; exige Ghidra/Java | CLI/web; controla trabalhadores `claude -p` | MIT | Hoje só Dreamcast SH-4; outras CPUs exigem escrever novo alvo. |
| objdiff | Compara objetos compilados ao alvo durante descompilação. | https://github.com/encounter/objdiff | Não verificado | Ferramenta local e extensão VS Code | MIT ou Apache-2.0 segundo resumo de busca |  |
| decomp-toolkit (dtk) | Ferramentas de descompilação GameCube/Wii num binário. | https://github.com/encounter/decomp-toolkit (não verificado; resultado mostrava fork) | Não verificado | CLI | Não verificado | README splat encaminha GameCube/Wii para cá. |
| splat | Divide ROM/binário em assembly e recursos para N64, PSX, PS2, PSP. | https://github.com/ethteck/splat | `python3 -m pip install -U splat64[mips]` (documentado) | CLI, Python | MIT | Plataformas limitadas (sem GameCube/Wii). |
| N64Recomp | Recompila estaticamente binários N64 para C nativo; permite acrescentar cooperação ao recompilado. | https://github.com/N64Recomp/N64Recomp | Compile com CMake 3.20+ e C++20 (documentado) | CLI, configuração TOML | MIT | Exige ELF com símbolos de descompilação e execução como N64ModernRuntime. README não aborda direitos de ROM; usuário fornece própria. |

## <a id="2-engine-mod-frameworks-and-hooking"></a>2. Estruturas de mods e hooks

### <a id="21-loaders-and-extenders-by-engine"></a>2.1 Carregadores e extensões por motor

| Estrutura | Alvos | Link oficial | Instalação | Linguagem / API | Licença | Cuidados |
|---|---|---|---|---|---|---|
| xNVSE | Fallout: New Vegas | https://github.com/xNVSE/NVSE | Copie DLL/EXE à raiz, não `Data`; inicie `nvse_loader.exe` (resumo do README). Não use ZIP "Code" GitHub. | Plugins nativos e extensões de scripts internos | Não verificado | Steam/GOG compatíveis; Epic, Gamepass e outras não (resumo). |
| SKSE (Skyrim) | Skyrim LE/SE/AE/VR | https://skse.silverlock.org (não verificado; memória) | Não verificado aqui | Plugins C++ | Não verificado | Acoplado à versão do executável. Consulte Address Library. |
| F4SE (Fallout 4) | Fallout 4 | https://f4se.silverlock.org (não verificado; memória) | Não verificado | Plugins C++ | Não verificado | Mesmo acoplamento de versão. |
| OBSE (Oblivion) | Oblivion clássico | Não verificado | Não verificado |  |  | Página xNVSE diz que NVSE deriva de OBSE. Oblivion Remastered é Unreal, usa ferramentas tipo UE4SS. |
| Address Library for SKSE Plugins | Banco de endereços independente de versão para plugins Skyrim | Nexus Mods página 32444, meh321 (resultados de busca) | Download Nexus | Cabeçalho e banco | Não verificado | AE/SE são arquivos separados; Vortex instalou errado para alguns. Estrutura C++ CommonLibSSE-NG (vários forks, licenças diferentes). |
| BepInEx | Unity Mono, Unity IL2CPP, XNA/FNA/MonoGame | https://github.com/BepInEx/BepInEx | Siga guia de versões; página do repositório sem etapas | Plugins C#; integra Harmony | LGPL-2.1 | Só Unity Mono com versões estáveis na pesquisa. IL2CPP sem macOS/ARM. Versões 5/6 (desenvolvimento) têm instruções diferentes. |
| MelonLoader | Unity Mono e IL2CPP | https://github.com/LavaGang/MelonLoader | Copie `MelonLoader`, `version.dll`, `dobby.dll` à pasta ou use instalador oficial (documentado) | Mods C# em `Mods`, plugins em `Plugins` | Apache-2.0 | IL2CPP exige .NET 6. Alguns jogos precisam de outra proxy (`winhttp.dll`, `dinput8.dll`). Depuração abre porta Mono. |
| Harmony | Patches de métodos .NET/Mono em execução | https://github.com/pardeike/Harmony | NuGet `Lib.Harmony` (ou `Lib.Harmony.Thin`) (documentado) | C# | MIT | Harmony 1.x/2.x incompatíveis. |
| UE4SS | Consulte seção 1.5 |  |  |  |  |  |
| REFramework | Jogos Capcom RE Engine (RE2/3/4/7/8, DMC5, SF6, MH Rise, Dragon's Dogma 2 e outros) | https://github.com/praydog/REFramework | Sem VR: extraia só `dinput8.dll` na pasta. Proton: `WINEDLLOVERRIDES="dinput8.dll=n,b" %command%` (documentado) | Lua; documentação refdocs.praydog.com | MIT | DX11/DX12. Steam Deck/Linux exige substituição da DLL. |
| Gibbed.Dunia | Contêineres Far Cry 2 (Dunia): extrai `Data_Win32\*.fat/.dat`, converte objetos FCB a XML | https://github.com/gibbed/Gibbed.Dunia | Compile com SDK .NET; copie `configs` ao lado (visto na compilação) | Ferramentas CLI C# | zlib | FAT2 versão 5: dois patches locais necessários (compressão v5 0=nenhuma, 1=LZO1x; respeitar tamanho de saída), games/far-cry-2. |
| Reloaded-II | Qualquer jogo Windows nativo x86/x64 | https://github.com/Reloaded-Project/Reloaded-II | Guia Quick Start do projeto (não na página obtida) | Mods C# (.NET) | GPL-3.0 | Lista de compatibilidade ausente no repositório. |
| Ultimate ASI Loader | Proxy DLL genérica carrega plugins `.asi` | https://github.com/ThirteenAG/Ultimate-ASI-Loader | Coloque como `dinput8.dll` (ou proxy aceita) na pasta, arquivos `.asi` na raiz ou `scripts`/`plugins` (documentado) | DLLs C++ nativas renomeadas `.asi` | MIT | Trabalho real em `InitializeASI`, não `DllMain` (trava do carregador). ASI dentro de ZIP não carrega. |
| Source SDK 2013 | Mods Source (código HL2, HL2DM, TF2) | https://github.com/ValveSoftware/source-sdk-2013 | Clone e siga compilação do README | C++ | Licença Source 1 SDK, não comercial segundo resumo | Mods não podem ser vendidos. Confira licença para seu uso. |
| UnrealScript (UE1/UE2, UCC/HCC) | Unreal 1, Unreal Tournament 99/2004, Deus Ex e similares | Não verificado | Compilação UCC incluída no jogo/SDK (não verificado) | UnrealScript | Por jogo | Sem pesquisa profunda aqui; consulte engine-families do projeto. |
| Motores Lua (LOVE, Defold, estilo Garry's Mod ou Roblox) | Jogos que carregam Lua do disco | Por motor | Por motor | Lua | Por motor | Frequentemente alvo fácil, scripts em texto; confira `lessons.md` para particularidades. |

### <a id="22-hooking-libraries-native-cc"></a>2.2 Bibliotecas de hooks (C/C++ nativo)

| Biblioteca | O que oferece | Link | Integração | Licença | Cuidados |
|---|---|---|---|---|---|
| MinHook | Hooks API inline mínimos x86/x64 | https://github.com/TsudaKageyu/minhook | vcpkg, CMake; MinGW desde v1.3.2 (documentado) | BSD-2-Clause | Enable/Disable suspende threads; use API enfileirada para muitos hooks. Funções pequenas podem falhar com `MH_ERROR_UNSUPPORTED_FUNCTION`. |
| Microsoft Detours | Instrumenta chamadas Win32 | https://github.com/microsoft/Detours | Distribuído em fonte, compile (vcpkg não confirmado) | MIT | Não utilizável em aplicativos Windows Store. |
| PolyHook 2 | Hooks inline, vtable, IAT/EAT, pontos de interrupção comuns e de hardware | https://github.com/stevemk14ebr/PolyHook_2_0 | CMake com submódulos (`git submodule update --init --recursive`) | MIT | Pontos de hardware são por thread. Suporte Unix parcial. |
| SafetyHook | Hooks C++23 inline/intermediários que pausam threads e corrigem relocações com segurança | https://github.com/cursey/safetyhook | ZIP amalgamado, CMake FetchContent ou submódulo; exige Zydis | BSL-1.0 | Só Windows. Fixe tag, não `origin/main`. Pausa todas as threads ao criar/excluir hooks. |

## <a id="3-running-several-game-copies-on-one-pc-for-tests"></a>3. Várias cópias num PC para testes

| Ferramenta | Função | Link | Método (documentado salvo indicação) | Licença / custo | Cuidados |
|---|---|---|---|---|---|
| Nucleus Co-op (SplitScreen.Me) | Inicia instâncias, atribui controle a cada, posiciona janelas, usa handlers por jogo (executável, mutex, pasta por links, hooks). API de handlers é principal referência para um PC hospedar N jogadores. | https://www.splitscreen.me/docs/handler-api/ e https://github.com/SplitScreen-Me/splitscreenme-nucleus | Baixe na central SplitScreen.Me. Configurações documentadas: `Game.ChangeExe`, `Game.IdInWindowTitle`, `Game.LaunchAsDifferentUsers`, `Game.KeepSymLinkOnExit`, `Game.HookInit` | Gratuito | Só Windows. Mais de 800 handlers segundo resumo. Com emuladores Goldberg/Nemirtingas, instâncias precisam de SteamID/nome próprios. Altere opção por vez ao depurar. Antigo lucasassislar/nucleuscoop teve último push dezembro 2023. |
| Sandboxie-Plus | Ambientes isolados com salvamentos, registro e mutex próprios por cópia. Útil para instância única/caminho fixo. | https://github.com/sandboxie-plus/Sandboxie | Releases; Windows 7+ 64 bits | Licenças por edição (GPL-3.0 em destaque, LICENSE.Plus/Classic separados; Plus mostra "Custom") | Continuação comunitária. CLI `Start.exe` ausente na página, consulte documentação. 738 issues na pesquisa. Jogos GPU/antitrapaça podem recusar isolamento. |
| Goldberg Steam emulator / gbe_fork | Substitui `steam_api(64).dll` para emular rede Steam LAN; duas instâncias locais se encontram sem duas contas. | https://github.com/Detanup01/gbe_fork (listagem AUR) | Troque DLL Steam, adicione `steam_appid.txt`; opcionais `steam_settings/` como `offline.txt`/`disable_networking.txt` (README Goldberg original) | gbe_fork LGPL-3.0 segundo AUR | Só teste de cópias próprias. README original pede remover DRM além de Steamworks; não faça, seria contorno DRM. Nunca serviços on-line/antitrapaça. Só LAN. README antigo alertava contra mesmo appid em várias instâncias na mesma máquina. |
| Instalações por hardlinks ou links simbólicos | Duplicar instalação de 50 GB sem outros 50 GB: `mklink /J` (junção) ou `mklink /H` em arquivos no mesmo volume NTFS; depois configurações/salvamentos separados. | Integrado ao Windows | `mklink /H <link> <target>` para arquivos, `mklink /J <link> <dir>` para diretórios (Windows padrão, não página de projeto) | Gratuito | Hardlinks só no mesmo volume. Escritas na instalação alteram arquivo compartilhado. Nucleus cria links simbólicos. |
| Auxiliares de modo janela/sem bordas | Forçam tela inteira exclusiva para janela, permitindo organizar e capturar instâncias. | Não verificado (muitas ferramentas; pesquisa não confirmou recomendação única) | Prefira modo janela nativo ou configuração Nucleus |  | Tente `-windowed` ou `-w` primeiro, dependem do motor. |

Notas Linux e Steam Deck:

- Nucleus/Sandboxie-Plus só Windows. Linux: prefixos Wine ou Proton separados por instância.
- REFramework exige `WINEDLLOVERRIDES="dinput8.dll=n,b" %command%` nas opções Steam. MelonLoader lista Linux por Wine/Proton ou nativo. BepInEx aceita Unity Mono Linux.
- UE4SS só Windows segundo README, mas jogos UE Windows rodam no Proton com substituição da proxy DLL da mesma forma.
- Goldberg lista Linux (`libsteam_api.so`).

### <a id="31-this-repos-own-tools-for-several-copies-and-sync-tests"></a>3.1 Ferramentas do repositório para múltiplas cópias e sincronização

`tools/gameslot` (reserva exclusiva para uma linha executar cópias por vez) e `tools/gamepool` (instalações isoladas por hardlinks, conjunto de cópias inicializadas reutilizadas, inícios minimizados econômicos, leitura de falhas) cuidam da organização acima para qualquer jogo Windows por configuração específica. Demais ferramentas (caos, gravador, fuzzer, responsabilidade, mundo simulado, cenários, bots, animações) em [tools/README.md](../tools/README.md). Execução de cópias: [multi-instance-testing.md](multi-instance-testing.md).

## <a id="4-agent-workflow-helpers"></a>4. Auxiliares dos fluxos de agentes

| Ferramenta | Função | Link | Instalação | Interface do agente | Licença / custo | Cuidados |
|---|---|---|---|---|---|---|
| Windows-MCP (CursorTouch) | Agente clica, digita, captura tela, executa PowerShell, lê registro e gerencia processos Windows. Útil para inicializadores/editores. | https://github.com/CursorTouch/Windows-MCP | `claude mcp add --transport stdio windows-mcp -- uvx windows-mcp serve` (documentado). Python 3.14+ e `uv` | MCP | MIT | README: acesso completo, operações irreversíveis possíveis. Telemetria anônima padrão (`ANONYMIZED_TELEMETRY=false` desativa). README diz não aceitar videogames. Prefira capturas internas/hook; área de trabalho é lenta, expõe outras janelas, falha em tela inteira exclusiva. |
| Captura de tela e estado dentro do jogo | Adicione comando/hook no mod que grava PNG e JSON de estado. Mais econômico/confiável que captura da área de trabalho para ciclos de agentes. | Código próprio | Específico do motor | Arquivo lido pelo agente | n/a | Mantenha saídas fora do repositório/Git. |
| DiscordChatExporter | Exporta histórico Discord (comunidade de mod ou bugs de amigos) para JSON/HTML/TXT/CSV lidos pelo agente. | https://github.com/Tyrrrz/DiscordChatExporter | ZIP `DiscordChatExporter.Cli.*.zip`, Docker `docker pull tyrrrz/discordchatexporter` ou `winget install Tyrrrz.DiscordChatExporter.CLI` (comunitário) (documentado) | CLI | MIT | README alerta que automatizar usuário viola termos Discord e pode banir; recomenda token de bot para canais acessíveis. Só exporte espaços autorizados, remova nomes/dados antes de commits. Consulte `discord-export.md`. |
| Compilador cruzado mingw-w64 em contêiner | Compila DLL/EXE Windows (`x86_64-w64-mingw32-gcc`) de Linux/WSL/CI sem Visual Studio. | https://www.mingw-w64.org (não verificado) | Sem imagem oficial encontrada. Comunitárias: dockcross windows-x64, icyguider/mingw-w64 em Debian 13; uma parada há 7 anos. Mais seguro instalar pacote mingw-w64 da distribuição na imagem base | CLI | Gratuito | DLL MinGW pode diferir em ABI de jogos MSVC, sobretudo C++ com exceções/STL na fronteira. Use interfaces C. MinHook aceita MinGW; SafetyHook é C++23, compatibilidade não confirmada. |
| GitHub CLI (`gh`) | Cria repositórios, issues, PRs, versões e lê execuções pelo terminal. | https://cli.github.com | `winget install GitHub.cli` (não verificado; memória) | CLI | Gratuito | Autentique com `gh auth login`; nunca cole tokens em arquivos. |

## <a id="suggested-starting-order-for-an-agent"></a>Ordem inicial sugerida para agente

1. Faça triagem: Detect It Easy ou estrutura de instalação identifica motor. Use `engine-families.md`.
2. Escolha carregador na seção 2 e confira mod mínimo carregando.
3. Estática: Ghidra sem interface/REA para nativo, ILSpy/dnSpyEx Mono, Il2CppDumper/Cpp2IL IL2CPP, UE4SS Unreal.
4. Dinâmica só se estática insuficiente: Cheat Engine/x64dbg em cópia desconectada, Frida para sondar funções.
5. Teste duas instâncias com Nucleus e emulador só LAN, em cópias próprias.
6. Fixe e registre ferramentas/MCPs nas notas do jogo para reprodução pelo próximo agente.

## <a id="gaps-and-items-marked-unverified"></a>Lacunas e itens não verificados

- Não houve obtenção direta para SKSE, F4SE, OBSE, Detect It Easy, PE-bear, API Monitor, Rizin, documentação oficial Binary Ninja, MCP oficial Hex-Rays, instalação gh e decomp-toolkit. Linhas dependem de memória/resumos, como indicado.
- Manutenção/licenças das variantes x64dbg, Cheat Engine, Frida e Binary Ninja vêm de terceiros. Abra repositório e confira commits recentes antes de confiar.
- Licenças Cheat Engine, x64dbg, Dumper-7, Il2CppDumper e Frida não visíveis nas páginas obtidas.
