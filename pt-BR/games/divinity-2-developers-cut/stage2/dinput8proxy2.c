/*
 * Divinity II: Developer's Cut - etapa 2: proxy dinput8 + interceptação de caminho por instância.
 *
 * A etapa 1 (stage1/) provou que a injeção por proxy dinput8.dll funciona: o jogo importa uma
 * função (DirectInput8Create) de DINPUT8.dll, portanto um proxy em bin\ carrega primeiro,
 * encaminha para o dinput8 real do sistema e nos permite executar código dentro do processo na inicialização.
 *
 * A etapa 2 acrescenta a primeira interceptação real: redirecionamento de Profile+Savegames por instância para duas
 * cópias do jogo num PC não sobrescrevam configurações e saves umas das outras (necessário para
 * tela dividida). Usa MinHook (incluído em minhook/) para interceptar SHGetFolderPathA.
 *
 * POR QUE interceptar SHGetFolderPathA (em vez de um endereço fixado no código):
 *   Os três construtores de caminhos do jogo fazem: SHGetFolderPathA(csidl) -> PathAppendA
 *   ("Divinity 2\"), depois uma operação de existência do tipo _access/_mkdir. Esta compilação do exe tem exatamente
 *   3 pontos de chamada:
 *     0x653a9a: csidl 0x1c = CSIDL_LOCAL_APPDATA   -> %LOCALAPPDATA%\Divinity 2\
 *                é o ÚNICO que importa: Profile\ + Savegames\ reais ficam aqui.
 *                Cria o diretório (referência real: corresponde a profile-backup/).
 *     0x653a3a: csidl 0x23 = CSIDL_COMMON_APPDATA  -> %PROGRAMDATA%\Divinity 2\
 *                observado contendo apenas Shaders\Generated\*.cache (compartilhado, regenerável).
 *     0x653afa: csidl 0x05 = CSIDL_PERSONAL        -> %USERPROFILE%\Documents\Divinity 2\
 *                uma sondagem pura de existência (retorna bool, SEM mkdir); pasta nunca criada
 *                durante execuções normais, portanto nada é gravado aqui.
 *   Redirecionar 0x23 e 0x05, portanto, é inofensivo, mas NÃO necessário para isolamento; só 0x1c
 *   garante a separação de Profile+Savegames. Redirecionar os três não custa nada e
 *   protege fluxos raros. Fixar o endereço de um construtor quebraria em qualquer outra compilação do exe
 *   (amigos Steam/GOG); SHGetFolderPathA é uma exportação estável de shell32, portanto interceptá-la pelo
 *   nome é robusto entre compilações.
 *
 * NOTA: o desvio executa ANTES de o jogo acrescentar seu próprio nome de pasta, portanto o token se torna
 * um segmento RAIZ da instância: ...\<base>\<token>\Divinity 2\Profile\ e ...\Savegames\.
 *
 * OPÇÃO DE ATIVAÇÃO (preserva o jogo normal com uma instância):
 *   Lê a variável de ambiente DIV2_INSTANCE. Ausente/vazia/"0"/inválida -> sem redirecionamento (comporta-se
 *   exatamente como na etapa 1). Defina como token curto e seguro para caminhos (por exemplo, "1","2","host","join")
 *   -> cada construtor de pasta do jogo recebe "\<token>" ao final. Cada instância usa seu próprio
 *   valor de DIV2_INSTANCE, portanto duas cópias num PC nunca compartilham Profile/Savegames.
 *
 * ERRO CONHECIDO DO JOGO (sem relação com esta DLL, encontrado em teste com duas instâncias):
 *   Iniciar duas instâncias no MESMO instante pode causar o travamento de uma na inicialização com
 *   0xc0000005, RVA da falha 0xB1024A. Causa: o reprodutor de vídeo do menu principal (FUN_00f07670,
 *   "MovieStreamLetter") passa um objeto de vídeo NULL ao setter FUN_00f10220, que
 *   o desreferencia incondicionalmente. O gatilho é concorrência no tempo de inicialização/carregamento de vídeo, não
 *   perfis, shaders ou redirecionamento (verificado: ambas as instâncias tinham perfil e
 *   estado de shaders idênticos ao travar). A interceptação desta DLL não está envolvida. Veja a etapa 2 de NOTES.md.
 *
 * Compile (32 bits; o jogo é PE32/i386) com llvm-mingw i686 gcc - veja build.ps1.
 *
 * NUNCA coloque isto na instalação real; apenas em cópias de teste (veja NOTES.md).
 */
#include <windows.h>
#include <shlobj.h>
#include "minhook/include/MinHook.h"

/* ---------------------------------------------------------------- Encaminhamento */
/* DirectInput8Create real (stdcall), resolvido a partir de dinput8.dll do sistema. */
typedef HRESULT (WINAPI *fn_DirectInput8Create)(
    HINSTANCE, DWORD, REFIID, LPVOID *, LPUNKNOWN);

static fn_DirectInput8Create pReal_DI8Create = NULL;
static char g_logPath[MAX_PATH] = "dinput8proxy.log";
static char g_instanceToken[MAX_PATH] = "";   /* não vazio => redirecionamento ativado */

static void log_line(const char *msg)
{
    HANDLE f = CreateFileA(g_logPath, FILE_GENERIC_WRITE, 0,
                           NULL, OPEN_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    if (f == INVALID_HANDLE_VALUE)
        return;
    SetFilePointer(f, 0, NULL, FILE_END);
    DWORD written = 0;
    WriteFile(f, msg, (DWORD)lstrlenA(msg), &written, NULL);
    CloseHandle(f);
}

static void resolve_log_path(HINSTANCE h)
{
    char buf[MAX_PATH];
    DWORD n = GetModuleFileNameA(h, buf, MAX_PATH);
    if (n == 0 || n >= MAX_PATH)
        return;
    while (n > 0 && buf[n - 1] != '\\' && buf[n - 1] != '/')
        n--;
    buf[n] = '\0';
    static const char name[] = "dinput8proxy.log";
    if (n + 1 + sizeof(name) < MAX_PATH) {
        if (n > 0 && buf[n - 1] != '\\' && buf[n - 1] != '/') {
            buf[n] = '\\';
            buf[n + 1] = '\0';
        }
        lstrcpyA(g_logPath, buf);
        lstrcatA(g_logPath, name);
    }
}

static int load_real_dinput8(void)
{
    if (pReal_DI8Create)
        return 1;
    char sysdir[MAX_PATH];
    UINT len = GetSystemDirectoryA(sysdir, MAX_PATH);
    if (len == 0 || len >= MAX_PATH)
        return 0;
    lstrcatA(sysdir, "\\dinput8.dll");
    HMODULE real = LoadLibraryA(sysdir);
    if (!real)
        return 0;
    pReal_DI8Create = (fn_DirectInput8Create)
        GetProcAddress(real, "DirectInput8Create");
    return pReal_DI8Create != NULL;
}

HRESULT WINAPI DefDirectInput8Create(
    HINSTANCE hinst, DWORD dwVersion, REFIID riidltf,
    LPVOID *ppvOut, LPUNKNOWN punkOuter)
{
    if (!load_real_dinput8())
        return E_FAIL;
    return pReal_DI8Create(hinst, dwVersion, riidltf, ppvOut, punkOuter);
}

/* ---------------------------------------------------------------- Interceptação de caminho */
/* SHGetFolderPathA real (stdcall): HRESULT(HWND,int,HANDLE,DWORD,LPSTR). */
typedef HRESULT (WINAPI *fn_SHGetFolderPathA)(HWND, int, HANDLE, DWORD, LPSTR);
static fn_SHGetFolderPathA pReal_SHGetFolderPathA = NULL;

/* Verificação de CSIDL: shlobj.h define CSIDL_LOCAL_APPDATA=0x001c, CSIDL_COMMON_APPDATA=0x0023,
 * CSIDL_PERSONAL=0x0005. Inicialmente inverti 0x1c/0x23; o aviso de redefinição de macro
 * da compilação detectou isso. Valores recebem máscara 0x00FF para que os bits de flags combinados por OR pelo chamador
 * (CSIDL_FLAG_CREATE 0x8000 etc.) continuem correspondendo; todos os IDs CSIDL cabem no byte inferior.
 *
 * Desvio: redireciona os três construtores de pastas do jogo (todos fazem PathAppend de "Divinity 2\"
 * após SHGetFolderPathA retornar). Cada redirecionamento é registrado com seu csidl para o teste
 * mostrar exatamente quais construtores executam (esperado: só 0x1c na inicialização - os outros dois
 * apontam para pastas inexistentes após execuções normais). Chamadores desconhecidos que solicitarem um
 * desses CSIDLs também receberiam o diretório do token; não há esses chamadores no exe
 * (3 locais no total), e dinput8/d3d9/PhysX não usam SHGetFolderPathA - e o token
 * diretório é válido + gravável, portanto o pior caso é inofensivo e visível no log. */
static HRESULT WINAPI Detour_SHGetFolderPathA(
    HWND hwnd, int csidl, HANDLE hToken, DWORD dwFlags, LPSTR pszPath)
{
    HRESULT hr = pReal_SHGetFolderPathA(hwnd, csidl, hToken, dwFlags, pszPath);
    int id = csidl & 0x00FF;
    if (SUCCEEDED(hr) && g_instanceToken[0] &&
        (id == 0x1c || id == 0x23 || id == 0x05)) {
        /* acrescenta "\<token>"; o próprio chamador então acrescenta "Divinity 2\", portanto o
         * layout final é <base>\<token>\Divinity 2\Profile. Crie <base>\<token>
         * agora (um único nível; o _mkdir do chamador então funciona abaixo dele). */
        char tmp[MAX_PATH];
        lstrcpynA(tmp, pszPath, MAX_PATH);
        if (lstrlenA(tmp) + 1 + lstrlenA(g_instanceToken) < MAX_PATH) {
            lstrcatA(tmp, "\\");
            lstrcatA(tmp, g_instanceToken);
            if (!CreateDirectoryA(tmp, NULL) &&
                GetLastError() != ERROR_ALREADY_EXISTS) {
                char m2[160];
                wsprintfA(m2, "dinput8proxy: CreateDirectory '%s' failed err=%u\r\n",
                          tmp, GetLastError());
                log_line(m2);
            }
            lstrcpynA(pszPath, tmp, MAX_PATH);
            char msg[300];
            wsprintfA(msg, "dinput8proxy: SHGetFolderPathA(csidl=0x%02x) -> '%s'\r\n",
                      id, pszPath);
            log_line(msg);
        }
    }
    return hr;
}

static void init_hook(void)
{
    if (MH_Initialize() != MH_OK) {
        log_line("dinput8proxy: MH_Initialize FAILED\r\n");
        return;
    }
    /* Resolve o alvo da interceptação de duas maneiras e prefere GetProcAddress: &SHGetFolderPathA
     * poderia, em princípio, ser um thunk de importação local à DLL (nesse caso, interceptá-lo
     * interceptaria só NOSSAS chamadas, não as do exe do jogo, que vão direto para shell32).
     * Ambos os endereços são registrados para a execução de teste provar que são a mesma função. */
    LPVOID target = NULL;
    HMODULE s32 = GetModuleHandleA("shell32.dll");
    if (!s32)
        s32 = LoadLibraryA("shell32.dll");     /* nossa importação o mantém carregado de qualquer forma */
    LPVOID byProc = s32 ? (LPVOID)GetProcAddress(s32, "SHGetFolderPathA") : NULL;
    LPVOID bySym  = (LPVOID)&SHGetFolderPathA;
    target = byProc ? byProc : bySym;
    char mb[224];
    wsprintfA(mb, "dinput8proxy: hook target shell32!SHGetFolderPathA byProc=%p "
                  "bySym=%p %s\r\n",
              byProc, bySym,
              (byProc && byProc == bySym) ? "MATCH" :
              (byProc ? "(differ - using byProc)" : "(bySym fallback)"));
    log_line(mb);
    if (!target) {
        log_line("dinput8proxy: no SHGetFolderPathA target, hook skipped\r\n");
        return;
    }
    if (MH_CreateHook(target, &Detour_SHGetFolderPathA,
                      (LPVOID*)&pReal_SHGetFolderPathA) != MH_OK) {
        log_line("dinput8proxy: MH_CreateHook(SHGetFolderPathA) FAILED\r\n");
        return;
    }
    if (MH_EnableHook(target) != MH_OK) {
        log_line("dinput8proxy: MH_EnableHook FAILED\r\n");
        return;
    }
    log_line("dinput8proxy: SHGetFolderPathA hook enabled\r\n");
}

static void read_instance_token(void)
{
    char buf[MAX_PATH];
    DWORD n = GetEnvironmentVariableA("DIV2_INSTANCE", buf, MAX_PATH);
    if (n > 0 && n < MAX_PATH && lstrcmpA(buf, "0") != 0) {
        /* Valida: curto (preserva espaço em MAX_PATH para os sufixos do próprio jogo) e
         * seguro para caminhos - sem separadores/curingas/travessia, para o token nunca apontar
         * para fora de <base>. Inválido -> redirecionamento DESLIGADO (jogo normal com uma instância). */
        int ok = (n <= 48) && lstrcmpA(buf, ".") != 0 && lstrcmpA(buf, "..") != 0;
        for (DWORD i = 0; ok && i < n; i++) {
            char c = buf[i];
            if (c == '\\' || c == '/' || c == ':' || c == '*' || c == '?' ||
                c == '"' || c == '<' || c == '>' || c == '|')
                ok = 0;
        }
        if (ok) {
            lstrcpynA(g_instanceToken, buf, MAX_PATH);
            char msg[128];
            wsprintfA(msg, "dinput8proxy: DIV2_INSTANCE='%s' (redirection ON)\r\n",
                      g_instanceToken);
            log_line(msg);
        } else {
            char msg[160];
            wsprintfA(msg, "dinput8proxy: DIV2_INSTANCE='%s' INVALID - redirection "
                      "OFF\r\n", buf);
            log_line(msg);
        }
    } else {
        log_line("dinput8proxy: DIV2_INSTANCE unset (redirection OFF)\r\n");
    }
}

BOOL WINAPI DllMain(HINSTANCE h, DWORD reason, LPVOID reserved)
{
    (void)reserved;
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(h);
        resolve_log_path(h);
        char pidbuf[64];
        wsprintfA(pidbuf, "dinput8proxy: PROCESS_ATTACH pid=%u\r\n",
                  GetCurrentProcessId());
        log_line(pidbuf);
        if (!load_real_dinput8())
            log_line("dinput8proxy: FAILED to load real dinput8.dll\r\n");
        else
            log_line("dinput8proxy: real dinput8.dll loaded, forwarded\r\n");
        read_instance_token();
        init_hook();
    } else if (reason == DLL_PROCESS_DETACH) {
        log_line("dinput8proxy: PROCESS_DETACH\r\n");
    }
    return TRUE;
}
