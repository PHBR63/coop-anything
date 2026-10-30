/*
 * Divinity II: Developer's Cut — Etapa 1: DLL proxy dinput8.dll.
 *
 * Objetivo: injeção no carregamento sem injetor externo. O jogo estaticamente
 * importa exatamente uma função de DINPUT8.dll (DirectInput8Create), então este
 * proxy fica na pasta bin\ do jogo, carrega a dinput8.dll real do sistema e
 * encaminha a chamada. Em PROCESS_ATTACH registra marcador em dinput8proxy.log
 * ao lado da DLL, comprovando injeção antes de adicionar ganchos MinHook.
 *
 * Compile (alvo de 32 bits; jogo PE32/i386) com llvm-mingw i686 gcc:
 *   i686-w64-mingw32-gcc -shared -o dinput8.dll dinput8proxy.c dinput8proxy.def -luser32
 *
 * Problema e solução de nome de exportação / convenção de chamada:
 *   O jogo importa o nome SEM DECORAÇÃO "DirectInput8Create" e o CHAMA como
 *   stdcall (o chamado remove os 5x4=20 bytes de argumentos). Com TinyCC isso era
 *   impossível: tcc decora exportações stdcall como "_DirectInput8Create@20", seu
 *   vinculador rejeita --kill-at, ignora aliases .def e seu assembly inline não consegue
 *   emitir trampolim stdcall funcional (tudo verificado; detalhes em NOTES.md). Então
 *   mudamos para compilador cruzado llvm-mingw (clang) i686. Aqui a solução é padrão:
 *   a implementação é função WINAPI (stdcall) normal cujo nome tem um
 *   sublinhado inicial em C (DefDirectInput8Create), e dinput8proxy.def mapeia
 *   o nome exportado voltado ao jogo para ela:
 *       EXPORTS DirectInput8Create = _DefDirectInput8Create@20
 *   fornecendo exportação com nome e convenção corretos. A função stdcall
 *   "ret 20" é emitido nativamente pelo compilador, sem assembly inline.
 *
 * NUNCA coloque na instalação real; só em cópias de teste (veja NOTES.md).
 */
#include <windows.h>

/* Tipos mínimos de DirectInput8Create (evita depender de dinput.h). */
typedef const IID *LPCGUID;

/* Ponteiro de função real, resolvido da dinput8.dll do sistema (stdcall). */
typedef HRESULT (WINAPI *fn_DirectInput8Create)(
    HINSTANCE, DWORD, REFIID, LPVOID *, LPUNKNOWN);

static fn_DirectInput8Create pReal = NULL;
static char g_logPath[MAX_PATH] = "dinput8proxy.log";

static void log_line(const char *msg)
{
    /* Acréscimo simples no estilo CREATE_ALWAYS. Identificadores só FILE_APPEND_DATA podem ser
     * exigentes quanto ao compartilhamento; use escrita genérica + acréscimo em arquivo existente. */
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
        return; /* mantém o caminho relativo padrão "dinput8proxy.log" */
    /* Remove tudo a partir da última barra invertida para buf terminar em "...bin\". */
    while (n > 0 && buf[n - 1] != '\\' && buf[n - 1] != '/')
        n--;
    buf[n] = '\0';
    /* Garante separador final antes de acrescentar o nome do registro.
     * (Acrescentar sem separador produzia o incorreto "dinput8.dlldinput8proxy.log".) */
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
    if (pReal)
        return 1;
    char sysdir[MAX_PATH];
    UINT len = GetSystemDirectoryA(sysdir, MAX_PATH);
    if (len == 0 || len >= MAX_PATH)
        return 0;
    lstrcatA(sysdir, "\\dinput8.dll");
    HMODULE real = LoadLibraryA(sysdir);
    if (!real)
        return 0;
    pReal = (fn_DirectInput8Create)
        GetProcAddress(real, "DirectInput8Create");
    return pReal != NULL;
}

/* A implementação stdcall exportada pelo .def como "DirectInput8Create".
 * O sublinhado inicial no nome C é o que "= _DefDirectInput8Create@20" do .def
 * referencia (símbolos C i386 Windows têm prefixo sublinhado, stdcall acrescenta @20). */
HRESULT WINAPI DefDirectInput8Create(
    HINSTANCE hinst, DWORD dwVersion, REFIID riidltf,
    LPVOID *ppvOut, LPUNKNOWN punkOuter)
{
    if (!load_real_dinput8()) {
        log_line("dinput8proxy: real dinput8.dll NOT loaded\r\n");
        return E_FAIL;
    }
    return pReal(hinst, dwVersion, riidltf, ppvOut, punkOuter);
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
    } else if (reason == DLL_PROCESS_DETACH) {
        log_line("dinput8proxy: PROCESS_DETACH\r\n");
    }
    return TRUE;
}
