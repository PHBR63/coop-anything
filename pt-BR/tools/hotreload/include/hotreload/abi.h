/* ABI C estável entre o carregador permanente e a DLL de núcleo recarregável.
 *
 * O carregador permanece no jogo por toda a sessão. O núcleo é copiado para um arquivo privado em cache, mapeado dali,
 * e pode ser descarregado e substituído enquanto o jogo executa.
 *
 * Rules:
 *  - Apenas tipos C simples atravessam esta fronteira: sem std::string, exceções ou objetos CRT. O carregador e o núcleo
 *    podem ser compilados com runtimes diferentes.
 *  - Ambas as structs começam com {abi_version, size}. Novos campos só são acrescentados ao final. Verifique `size` antes de usar um
 *    campo acrescentado posteriormente.
 *  - Cada ponto de entrada do núcleo executa na thread que chama HotReload_OnFrame (o ciclo principal do jogo), entre quadros,
 *    nunca de dentro de outra chamada do núcleo.
 *  - Cada ponteiro recebido pelo núcleo permanece válido até o núcleo retornar de before_unload e ser descarregado.
 */
#pragma once
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HR_ABI_VERSION 1u

/* Destino de saída para métodos de controle: chame out->set(out->h, text) uma vez. O texto é copiado. Em caso de sucesso, deve ser JSON
 * (um número, uma string entre aspas, um objeto...). Em caso de falha, é uma mensagem simples. */
typedef struct HrOut {
    void* h;
    void (*set)(void* h, const char* text);
} HrOut;

/* Um método de controle implementado pelo núcleo. Retorne 1 para sucesso, 0 para falha (mensagem em out). `user` é o valor
 * passado no registro. Executa na thread principal entre quadros. */
typedef int (*HrMethodFn)(void* user, const char* params_json, HrOut* out);

/* carregador -> núcleo */
typedef struct HrLoaderApi {
    uint32_t abi_version;        /* HR_ABI_VERSION */
    uint32_t size;              /* sizeof(HrLoaderApi) conforme compilado pelo carregador */
    uint32_t generation;        /* 1 no primeiro carregamento, +1 por recarregamento bem-sucedido */
    uint32_t is_reload;         /* 0 = primeiro carregamento neste processo, 1 = recarregamento em execução (pode existir um blob de estado) */
    const char* game_dir;       /* a pasta passada pelo hospedeiro a HotReload_Start, pode ser "" */
    const char* core_dir;       /* pasta do arquivo de núcleo ORIGINAL, com barra invertida final. O núcleo executa de uma cópia
                                   em cache, portanto arquivos ao lado da saída da compilação são encontrados aqui, não ao lado do módulo. */
    void* user_context;         /* o ponteiro passado pelo hospedeiro a HotReload_Start (interface do motor, tabela...) */

    void (*log)(const char* line);
    /* Registra um método de controle (veja HrMethodFn). O carregador o remove antes de descarregar o núcleo, portanto o núcleo
     * não precisa cancelar o registro. */
    void (*register_method)(const char* name, HrMethodFn fn, void* user);

    /* Armazenamento de blobs pertencente ao carregador. Sobrevive a recarregamentos (não a reinícios do processo). `version` é opaco ao carregador.
     * blob_get copia min(cap, len) bytes, sempre define *len como o tamanho total e retorna 1 se a chave existir
     * (len e version podem ser NULL); caso contrário, 0. */
    int (*blob_put)(const char* key, const void* data, uint32_t len, uint32_t version);
    int (*blob_get)(const char* key, void* buf, uint32_t cap, uint32_t* len, uint32_t* version);
    void (*blob_erase)(const char* key);

    /* Solicita um recarregamento. O carregador o realiza no próximo limite entre quadros. Pode ser chamado de qualquer thread com segurança. */
    void (*request_reload)(const char* reason);
    /* Chame de before_unload antes de retornar 0, para o relatório de recarregamento informar por que o descarregamento foi recusado. */
    void (*veto_reason)(const char* why);
    /* Campos acrescentados ficam abaixo desta linha. */
} HrLoaderApi;

/* núcleo -> carregador */
typedef struct HrCoreApi {
    uint32_t abi_version;
    uint32_t size;
    /* Chamado uma vez após carregar, na thread principal. Retorne 1 para indicar sucesso. Num recarregamento em execução (api->is_reload), restaure o
     * estado aqui. Retornar 0 faz o carregador descarregar este núcleo novamente e, num recarregamento, reverter ao anterior. */
    int (*init)(void);
    /* Uma mensagem do jogo ou extensor de scripts, repassada sem alterações. Opcional. */
    void (*on_message)(uint32_t type, void* data, uint32_t len);
    /* Uma vez por quadro. Opcional. */
    void (*on_frame)(void);
    /* Chamado antes do descarregamento, na thread principal, entre quadros. O núcleo deve parar suas threads, fechar ou transferir
     * sockets, remover todas as interceptações instaladas e gravar seu estado com api->blob_put. Retorne 1 quando estiver pronto para ser
     * descarregado. Retorne 0 para recusar: o carregador mantém o núcleo carregado, e o núcleo deve continuar totalmente funcional. */
    int (*before_unload)(void);
    /* Campos acrescentados ficam abaixo desta linha. */
} HrCoreApi;

/* A única exportação presente em toda DLL de núcleo (nome C sem decoração):
 *   int HotCore_Init(const HrLoaderApi* api, HrCoreApi* out);   // preencha `out`, retorne 1 em caso de sucesso
 * O carregador verifica api->abi_version == HR_ABI_VERSION e se `out` está completo até before_unload. */
typedef int (*HrCoreInitFn)(const HrLoaderApi* api, HrCoreApi* out);
#define HR_CORE_INIT_EXPORT "HotCore_Init"

#ifdef __cplusplus
}
#endif
