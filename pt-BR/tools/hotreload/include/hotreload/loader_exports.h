/* A API C de hotreload_loader.dll, o carregador permanente. O ponto de entrada do seu plugin (ou um pequeno host) carrega a DLL,
 * chama HotReload_Start uma vez e depois HotReload_OnFrame a cada quadro na thread principal.
 *
 * Se preferir não distribuir uma segunda DLL, vincule a biblioteca estática `hotreload_host` ao seu plugin e use
 * hotreload::CoreHost (loader_host.h) diretamente. A DLL é um invólucro fino em torno dele. */
#pragma once
#include <stdint.h>

#include "hotreload/abi.h"

/* A DLL do carregador define HOTRELOAD_EXPORTS ao ser compilada. Um host que carrega a DLL com GetProcAddress não
 * precisa dessas declarações. */
#ifdef HOTRELOAD_EXPORTS
#define HR_API __declspec(dllexport)
#else
#define HR_API __declspec(dllimport)
#endif

#ifdef __cplusplus
extern "C" {
#endif

typedef struct HotReloadConfig {
    uint32_t size;               /* sizeof(HotReloadConfig) */
    const char* core_path;       /* a DLL do núcleo gerada pela compilação. O carregador nunca mapeia este arquivo diretamente. */
    const char* cache_dir;       /* onde ficam as cópias privadas. NULL ou "" = "hr_cache" ao lado de core_path. */
    const char* game_dir;        /* passado ao núcleo como api->game_dir. Pode ser NULL. */
    const char* pipe_name;       /* pipe de controle, nome curto ("mygame-1") ou caminho completo \.\pipe\. NULL = sem pipe de controle. */
    const char* log_path;        /* NULL ou "" = hotreload.log dentro de cache_dir */
    void* user_context;          /* passado ao núcleo como api->user_context. Pode ser NULL. */
} HotReloadConfig;

/* Inicia o pipe de controle, registra dev.status e dev.reload e carrega o núcleo. Retorna 1 quando o carregador está ativo.
 * Um núcleo que não carrega não faz Start falhar: o carregador continua executando, dev.status informa o motivo e um futuro
 * dev.reload (após corrigir a compilação) o carrega. Retorna 0 se o pipe de controle não pôde ser criado ou Start já foi
 * chamado; HotReload_LastError() informa então o motivo. */
HR_API int HotReload_Start(const HotReloadConfig* config);
/* Thread principal, a cada quadro: atende solicitações de controle, faz um recarregamento pendente e chama on_frame do núcleo. */
HR_API void HotReload_OnFrame(void);
HR_API void HotReload_OnMessage(uint32_t type, void* data, uint32_t len);
/* Registra um método de controle pertencente ao host, não ao núcleo. Sobrevive a recarregamentos. Executa na thread principal. */
HR_API void HotReload_RegisterMethod(const char* name, HrMethodFn fn, void* user);
HR_API const char* HotReload_LastError(void);
/* Para o pipe de controle. Não descarrega o núcleo (o processo está encerrando). */
HR_API void HotReload_Shutdown(void);

#ifdef __cplusplus
}
#endif
