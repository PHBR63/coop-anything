# <a id="mafia-definitive-edition-research-notes"></a>Mafia: Definitive Edition: notas de pesquisa

Alvo: aplicativo Steam 1030840, compilação 16502642, SHA-256 de `mafiadefinitiveedition.exe` `34B06C6C11326E51001EF2FD82933C7F200ACAD27EDBFCC0C159A7051978675E`, Windows 10 x64. Todo o trabalho até aqui usou uma cópia isolada da instalação (`<lab>\mafia-de`, verificada com os mesmos 4.882 arquivos e 38.908.493.197 bytes da instalação da loja) ou leu o executável sem alterá-lo. A partir da seção da sonda de 2026-10-24, bots iniciaram a cópia de teste, sem rede e sob monitoramento de alterações.

## <a id="2026-10-24-triage-and-research"></a>2026-10-24: triagem e pesquisa

Observado:
- O núcleo não tinha relato para este jogo. Issue #167 e PR #172 tratam do original de 2002 (LS3D).
- MafiaMP: <https://github.com/MafiaHub/MafiaMP>, último push 2026-10-15, pré-lançamento v2.5.1 de 2025-12-21. O cliente usa MinHook e padrões de bytes; por exemplo, `core/hooks/game_director.cpp` insere hook em `C_GameDirector::OnActiveCityChanged` por `hook::get_opcode_address("E8 ? ? ? ? 80 BE ...")`. Licença: MafiaHub OSS, cláusula 5 (<https://github.com/MafiaHub/MafiaMP/blob/master/LICENSE.txt>).
- Cobertura de história do MafiaMP: `sdk/mafia/framework/director/c_game_director.h` (`m_pActiveCityID` em +0x28, `GetInstance`, `GetDistrict`) e declaração antecipada de `I_Mission`. Nada sobre missões, linhas de enredo ou missões de campanha.
- JustAddMP/MafiaDE: <https://github.com/JustAddMP/MafiaDE>, criado em 2026-10-08, pré-lançamento v0.17.1 em 2026-10-21, sem arquivo de licença nele nem em <https://github.com/JustAddMP/core>. `README-dev.md` lista `--transport udp|steam` e `player_sync.lua` gerado.
- Mafia Toolkit: <https://github.com/Greavesy1899/MafiaToolkit>, PolyForm Strict 1.0.0. O código dos arquivos contêiner é zlib ((c) 2017 Rick "gibbed").

Método: busca por padrões
- Reuni os 394 padrões únicos passados aos auxiliares `hook::` nos 462 arquivos-fonte do cliente MafiaMP na branch master e contei as ocorrências de cada um no executável (expressão regular Python, `?` = qualquer byte). Resultado: 382 ocorrem uma vez, 12 várias vezes, 0 ausentes. Não foi conferido se MafiaMP escolhe uma ocorrência específica nos 12 padrões múltiplos.

Deduzido:
- A engenharia reversa do MafiaMP muito provavelmente corresponde à compilação 16502642.

## <a id="2026-10-24-executable"></a>2026-10-24: executável

Observado:
- Seções PE: `.text`, `BINK`, `.interpr`, `.rdata`, `.data`, `.pdata`, `.tls`, `BINKDATA`, `.gfids`, `_RDATA`, `.rsrc`, `.reloc`. Não há `.bind`, portanto não há SteamStub.
- Importação Ghidra 12.1.4 sem interface: carregador PE, `x86:LE:64:default:windows`, callbacks TLS em `0x144b1d900`. `MafiaDefinitiveEdition.pdb` (GUID `1caa58cd-95da-4f0f-8938-6ea47e2b591b`, age 1) não foi encontrado. A análise RTTI registrou cerca de 120 erros "TypeDescriptor . doesn't point to a vfTable". A análise ainda está executando.
- Busca de strings por expressão regular para nomes RTTI MSVC (`.?AV…`) e palavras de história trouxe só 9 resultados; os nomes vêm de outras strings. Classes de história e salvamento encontradas estão no README.
- Caminhos de scripts de Mafia III estão no executável (por exemplo, `/scripts/entities/interactions/int_kill_the_judge_dealer_1_hold.vi`).
- O namespace `hks` (`HeapVisualizer@hks`) está presente.

Desconhecido:
- A função da seção `.interpr`.

## <a id="2026-10-24-script-archives"></a>2026-10-24: arquivos contêiner de scripts

Método:
- Escrevi um leitor SDS v20 próprio, somente de leitura, em Python, adaptando o conhecimento do formato do código Gibbed licenciado em zlib. Armadilhas encontradas nos arquivos reais: o início de 12 bytes e o cabeçalho de arquivo de 52 bytes são seguidos, cada um, por soma de verificação de 4 bytes; portanto, o cabeçalho começa no offset 16, não 12. Cada cabeçalho de recurso de 34 bytes no fluxo de blocos também é seguido por soma de 4 bytes; por isso, os dados ocupam `size - 38` bytes. Blocos Oodle são descomprimidos com `oo2core_8_win64.dll` do jogo (`OodleLZ_Decompress`, tamanho descomprimido conhecido pelo cabeçalho do bloco).

Observado (todos os 150 arquivos em `sds_retail/script`):
- Tipos de recursos: hkAnimation 15.528; Texture 8.261; Generic 9.249; Cutscene 14; Script 1.
- Subtipos Generic pelo primeiro u32, nomeados pela tabela `GenericResource.cs` do Mafia Toolkit: `0x64D0E75C` `.ires.compiled` 4.326; `0x5B770C22` `.vi.compiled` 4.210; `0xB4347D18` `.entity.compiled` 358; `0xA27F694D` `.iprofai` 189; `0x4A336D64` `.iproftime` 150; `0x45F07C8B` `.gxml` 15.
- O único arquivo Lua é `/scripts/missions/statistic_tracking/statistic_tracking.lua`, 19.442 bytes de bytecode Lua 5.1. Em todos os fluxos descomprimidos, `\x1bLua` ocorre uma vez.

Deduzido:
- A lógica de missões não é Lua. Minha suposição anterior estava errada (regra 6). A abordagem mudou para sincronizar estado de história, em vez de chamadas de scripts.

Desconhecido:
- Formato `.vi.compiled`, ambiente que o interpreta e presença de Lua em outras pastas `sds_retail` (não examinadas).

## <a id="2026-10-24-save-location"></a>2026-10-24: local dos salvamentos

Observado:
- No PC de teste, não existia pasta com nome correspondente a mafia, hangar, 2k ou 1030840 em `%LOCALAPPDATA%`, `%APPDATA%`, LocalLow, Documents (redirecionado ao OneDrive), Saved Games, ProgramData ou `userdata\<id>\1030840` do Steam (profundidade 4). Steam marcou o jogo como jogado na instalação, mas nenhum arquivo gravado pelo jogo apareceu.
- Strings do executável: `Hangar 13 Games`, `Mafia Definitive Edition`, `/profiles`, `/profiles/`, `/profiles_b/`, `/profiles_xml/`, `%s/%llu`, `SaveSystem`, `SaveManager`, `SaveAsyncWriteHelper` e `SOFTWARE\2K Games\CrashReport` (registro).

Deduzido (primeira hipótese, corrigida depois):
- Inicialmente supus `<known folder>\Hangar 13 Games\Mafia Definitive Edition\…\profiles\<SteamID64>`. Estava errado; veja abaixo.

Método: busca de importações e referências, sem Ghidra (projeto bloqueado pela análise em execução)
- Analisei a tabela de importações e procurei em `.text` operandos ModRM relativos a RIP (mod=00, rm=101) cujo disp32 alcança uma entrada de importação ou string.
- Importações de pastas: `SHELL32!SHGetFolderPathA` (IAT `0x144a6f8e8`) e `KERNEL32!ExpandEnvironmentStringsA`. Não há `SHGetKnownFolderPath`.

Observado:
- `SHGetFolderPathA` é chamado 5 vezes. Em `0x1406eb87d`, a pasta é `lea edx,[r9+0x1a]` (`CSIDL_APPDATA`), sem strings de salvamento próximas. Em `0x14240d440`, `0x1424196ca`, `0x14241a642` e `0x14241a892`, é `xor r9d,r9d; lea edx,[r9+5]` (`CSIDL_PERSONAL`, Documents).
- Strings próximas: `/edit`, `My Games`, `Mafia Definitive Edition`, `\Saves` e `/gamesaves` (`0x14240d300`-`0x14240d800`). Também `%s%s\%s\Saves\launcconfig.cfg` e `%s%s\%s\Saves\videoconfig.cfg`, cada qual com `My Games` e `Mafia Definitive Edition` (`0x1424196a0`, `0x14241a600`).
- `Hangar 13 Games` (`0x144b1f028`) tem uma referência, em `0x14374209b`, fora do código de salvamento.

Deduzido:
- Salvamentos e configurações de inicializador/vídeo ficam em `<Documents>\My Games\Mafia Definitive Edition\Saves\`. Não foram rastreados os separadores exatos das strings de formatação.
- A pasta independe do caminho de instalação; portanto, uma cópia de teste a compartilha com o jogo real. Se Documents estiver no OneDrive, como no PC de teste, os salvamentos sincronizam na nuvem.

Desconhecido:
- O conteúdo abaixo de `Saves` (`/profiles/`, `%s/%llu` por Steam ID?). Conferir na primeira inicialização monitorada, após redirecionar `CSIDL_PERSONAL` para a cópia de teste.

## <a id="workspace-pitfalls"></a>Armadilhas do ambiente de trabalho

- Uma "cópia de teste" com hardlinks não é isolada. Uma cópia anterior tinha 4.843 arquivos ligados por hardlink à instalação da loja; qualquer escrita alteraria o jogo real. Confira com `fsutil hardlink list` antes de confiar na cópia.

## <a id="2026-10-24-story-api-static-ghidra"></a>2026-10-24: API de história (estática, Ghidra)

Método:
- Análise automática completa Ghidra 12.1.4 (cerca de 2 h), depois scripts próprios sem interface: referências cruzadas de strings com descompilação de cada função referenciadora e busca em `.rdata`/`.data` de arrays de pares `{pointer to ASCII name, pointer into .text}` terminados em `{0, 0}`.

Observado:
- Nomes de classes de história (`C_MissionCloseState`, `C_Quest`, `C_PlotlinesManagerSaveBlock`, `C_GameDirectorGRD`, .) só são usados no registro de tipos para reflexão (por exemplo, hash `0x2aaa22d5` de `C_MissionCloseState`). Não levam ao código dos gerenciadores.
- `0x143812940` é uma verificação genérica de tipo do invólucro de scripts, com 588 locais de chamada; portanto, objetos são expostos ao HavokScript.
- 436 tabelas no estilo `luaL_Reg`, 5.800 entradas. Funções de história e endereços estão no README. Funções de missões chamam um objeto global em `0x14635a740` (+8 interface) pela vtable: `QuestSetActive` → vt+0x70, `SetCurrentAct` → vt+0x1a8. `SetCurrentStoryId` → getter `0x142d61440`, depois `0x142d6e330(mgr, id, -1)`. `SetMissionState` → getter `0x142438260`, depois `0x142438730(mgr, id, bool)`.
- Os primeiros 24 bytes são únicos apenas para `GameOver`, `SetCurrentAct`, `SetCurrentSubAct`, `SetCurrentStoryId`, `SetMissionState`, `Retry` e `CrossedCheckPoint`.

Hipótese:
- `0x14635a740` é `C_GameDirector` ou sua interface de missões. Não confirmado.

## <a id="2026-10-24-probe-dll-and-guarded-launches"></a>2026-10-24: DLL de sondagem e inicializações monitoradas

Método:
- O executável importa `VERSION.dll` (6 funções); um proxy `version.dll` na cópia de teste carrega primeiro. Encaminha as 17 exportações de versão à DLL de sistema e altera a tabela de importações do executável.
- `SHGetFolderPathA` para `CSIDL_PERSONAL`, `CSIDL_APPDATA` e `CSIDL_LOCAL_APPDATA` retorna pasta por instância. A sonda encerra o jogo se a pasta não estiver definida.
- Antes e depois de cada execução, uma estrutura de teste captura: lista de arquivos e hash do executável da instalação real, `Documents\My Games`, Saved Games, `userdata` Steam (recursivo), nível superior de Documents, AppData, LocalAppData, LocalLow e perfil do usuário, além de HKCU `Software\2K Games` e `Software\Hangar 13`.

Observado (primeira execução, on-line, 120 s, sem entrada):
- Redirecionamento funcionou (chamadas de 0x1a e 0x5). O jogo criou `Documents\My Games\Mafia Definitive Edition\Saves\` (`launcconfig.cfg`, `videoconfig.cfg`) e `Data\<SteamID64>\profiles\temporaryprofile\*.pf` ali.
- Monitoramento: instalação e hash do executável inalterados. Só os registros internos do cliente Steam mudaram: `config\localconfig.vdf`, `config\librarycache\<appid>.json`, `gamerecordings\gamerecording.pb`. Nenhuma pasta de armazenamento remoto Steam apareceu.
- Nenhum `GetProcAddress` para funções Steam; a API Steam está vinculada estaticamente.
- Janela de 1280×720 em modo janela. Os 960×540 escritos antes em `videoconfig.cfg` não foram usados.
- **A biblioteca HTTP do jogo escreveu tráfego HTTPS detalhado na saída padrão, incluindo token bearer de login único da 2K.** Contatou `*.my.2k.com` e hosts `sso`, `telemetry` e `promotions` em `api.2kcoretech.online`, enviando por conta própria a um endpoint SSO. Mantenha a saída padrão em arquivo privado, nunca em logs compartilhados.

Método (modo sem rede, todas as execuções posteriores):
- Hooks de importação em `getaddrinfo`, `gethostbyname`, `connect` e `sendto` (importações ws2_32 pelos ordinais 52, 4 e 20) falham para alvos fora do loopback.

Observado:
- Sem rede, o menu principal é alcançado após diálogo "cannot connect to 2K". Nenhum token foi registrado.

## <a id="2026-10-24-bot-input"></a>2026-10-24: entradas dos bots

Observado:
- `WM_KEYDOWN`/`WM_KEYUP` publicados não têm efeito. Teclado lido por DirectInput 8 e controles por XInput: importação e `GetProcAddress` em execução de `XInputGetCapabilities` e `XInputSetState`.
- Hooks somente nas importações XInput não bastaram: a interface ignorava o controle virtual até a sonda também retornar os hooks por `GetProcAddress`.
- A interface segue o cursor real; mover o mouse mudava os avisos para teclado e mouse. Fixar `GetCursorPos` no centro da janela e ignorar `ClipCursor` resolveu.
- Cenas pausavam (com aviso de pular por teclado) ao perder foco. Substituir o procedimento da janela resolveu: `WM_ACTIVATEAPP` e `WM_ACTIVATE` forçados para ativo; `WM_KILLFOCUS` ignorado.
- O jogo consulta `XInputGetState` cerca de 120 vezes por segundo nos menus e 60 em missão.
- Fluxo de início sem rede: introduções (A pula após cerca de 20 s), tela inicial (A), "connecting", "cannot connect to 2K" (A), menu principal (Continue, Story, Free Ride, .). Um percurso por script da inicialização à missão do perfil passou várias vezes, em cerca de 97 s.
- Tocar A, manter A por 1,5 s e pressionar B não pula cenas.

Desconhecido:
- O botão de controle para pular cenas.

## <a id="2026-10-24-chapter-1-call-sequence"></a>2026-10-24: sequência de chamadas do capítulo 1

Método:
- A sonda envolve 579 funções de 8 tabelas (`0x145ad0780`, `0x145af5810`, `0x145af7b50`, `0x145ae3b20`, `0x145ae3450`, `0x145af5d20`, `0x145af45d0`, `0x145af9720`), excluindo metamétodos. Uma entrada só é trocada se ponteiro de nome e função corresponderem à compilação: todas as 579 corresponderam. Log limitado a 8 chamadas por função a cada 5 s, com contagem de chamadas.
- Organização de um objeto de argumento string lida dos valores ao vivo: comprimento u64 em +0x08, hash u32 em +0x10, texto em +0x14 (`mm_10_chase`: comprimento 0x0b, hash `b96a5469`).

Observado:
- A sequência no README, a partir de Continue em um perfil cujo salvamento automático fica no início do capítulo 1. O bot parado chegou ao primeiro checkpoint, `cp_020`, e morreu cerca de 27 s depois na perseguição de carro.
- Antes no mesmo log, ao abrir o menu: `RegisterScriptedMenuEvent("MainMenu", 0..7, …)`.

Deduzido:
- Início de missão, checkpoint, objetivos e morte têm chamadas próprias com identificadores string, permitindo repeti-las no cliente.

## <a id="2026-10-24-chapter-replay-unlock"></a>2026-10-24: desbloqueio da repetição de capítulos

Método:
- Referências cruzadas de `MissionReplayUnlocked`, `PersistentDataStorage`, `S_VariableNumber` e outros.

Observado:
- A lista Chapter Replay (`0x142fe01b0`) lê `MissionReplayUnlocked` do armazenamento de dados de scripts e marca a entrada *i* desbloqueada quando *i* é menor que o valor. O grupo de armazenamento vem do bloco salvo `PersistentDataStorage` (`0x1423632f0`, chave de grupo em `0x14635f3b0`).
- Nomes recebem hash em `0x143cbae50`: FNV-1 de 64 bits (multiplicar por `0x100000001b3`, depois xor), base `0xcbf29ce484222325`. Nome só com dígitos (sem 0 inicial) é interpretado como decimal.
- Perfis `.pf` são XML seguido de 4 bytes. Nos 11 arquivos do perfil de teste, esses bytes são CRC32 do XML, little endian.
- Classes de variáveis: identificador de `S_VariableNumber` `0x48c8e903`, `S_VariableString` `0x48c8e904` (`m_Type` 3 em arquivo salvo), `S_VariableBool` `0x48c8e905`.
- Após acrescentar `MissionReplayUnlocked` = 99 (`S_VariableNumber`, `m_Type` 2) ao `profile_data_storage_persistantdata.pf` do perfil de teste e corrigir o CRC, Story → Chapter Replay listou os 20 capítulos. Capítulo 2 carregou imediatamente e iniciou `mm_20_taxi`.

Hipótese:
- `m_Type` 2 = número, pela ordem dos identificadores. O jogo aceitou, mas o enum completo não foi lido.

## <a id="2026-10-24-all-chapters-from-chapter-replay"></a>2026-10-24: todos os capítulos pelo Chapter Replay

Método:
- Uma inicialização sem rede e monitorada por capítulo: Story → Chapter Replay → entrada *N*; pressionar A no "Continue" da tela de carregamento; registrar até o primeiro `QuestSetCustomState` mais 45 s (ou tela de morte, ou 15 min); encerrar e comparar capturas de estado. Chamadas resumidas do log da sonda (consultas e leituras por quadro removidas).

Observado:
- Todas as 20 entradas registradas; tabela no README. Cada capítulo carrega exatamente uma missão `mm_*`.
- Chapter Replay termina em tela de carregamento aguardando "Continue". Carregar por Continue do menu principal não aguardava.
- Armadilhas do bot, encontradas por capítulo errado ou execução presa:
  - "cannot connect to 2K" não aparece em toda inicialização sem rede. Pressionamentos cegos por tempo acionam Continue no menu e carregam o salvamento automático.
  - Pressão de 0,4 s passou do diálogo ao menu principal (capturas: conectando, diálogo, depois carregamento do salvamento automático).
  - Na lista Chapter Replay, um DOWN às vezes movia duas linhas: 7 pressões de 0,15 s moveram 11 linhas. A lista sempre abre na linha 1.
  - Método funcional: conferir a tela antes de pressionar. O título dourado no canto superior esquerdo está só no menu principal e submenu Story; a borda esquerda da seleção marca a linha destacada.
- Executar o lote enquanto outro jogo rodava em tela cheia no mesmo PC: a cópia parou de responder (Windows informou `AppHangB1`) cerca de 18 s após o outro jogo iniciar; na segunda tentativa, encerrou silenciosamente. O lote precisa do PC sem outros jogos.
- Cada inicialização atualiza a marca de tempo do cache de Notes do Steam (`userdata\<id>\2371090\remotecache.vdf`, aplicativo 2371090), com mesmo conteúdo. O monitor considera esse arquivo um registro interno esperado.

Desconhecido:
- Onde `mm_90_funeral` é jogada: nenhuma entrada Chapter Replay a carregou.
- Checkpoints posteriores aos primeiros de cada missão e chamadas ao fim das missões.
