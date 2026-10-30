// Variantes de mutação C++ selecionáveis em execução (tools/mutants/README.md).
//
// Uma "variante" é uma versão deliberadamente defeituosa de um trecho de código. Um teste que protege esse código deve falhar quando a
// variante está ativa; uma variante que não faz um teste falhar revela um teste que não prova nada.
//
// Forma antiga: uma compilação por variante (-DMY_TWIN_28 ...), então 40 variantes significavam 40 compilações.
// Desta forma: compile o código sob teste UMA VEZ com COOP_RUNTIME_MUT definido e escolha a variante quando o programa de testes iniciar:
//
//     set COOP_MUT=add_wrong_operator && my_tests.exe        (variável de ambiente, nome ou número)
//     my_tests.exe --mut add_wrong_operator                   (linha de comando, se main chamar coop_mut::init_from_args)
//
// No código sob teste:
//
//     if (COOP_MUT_IF("add_wrong_operator")) return a - b;    // a variante defeituosa
//     if (!COOP_MUT_IF("skip_range_check")) { checkRange(x); } // código removido pela variante
//
// Sem COOP_RUNTIME_MUT (sua compilação distribuída), COOP_MUT_IF(x) é a constante false: variantes defeituosas são código morto que o
// otimizador elimina, nada lê o ambiente e nada no binário distribuído pode ativar uma variante. Defina
// COOP_RUNTIME_MUT somente para compilações de teste das suas bibliotecas.
//
// Uma variante fica ativa por vez. O nome é qualquer texto sem espaços; números também funcionam (COOP_MUT_IF(3) com COOP_MUT=3).
// O valor "0" ou vazio significa sem variante. set() é para configuração de teste com uma thread; chame antes de iniciar outras threads.
#pragma once

#ifdef COOP_RUNTIME_MUT
#include <cstdlib>
#include <cstring>
#include <string>

namespace coop_mut {

inline std::string readEnv() {
#if defined(_MSC_VER)
    char* buf = nullptr;
    size_t len = 0;
    std::string out;
    if (_dupenv_s(&buf, &len, "COOP_MUT") == 0 && buf) {
        out = buf;
        std::free(buf);
    }
    return out;
#else
    const char* e = std::getenv("COOP_MUT");
    return e ? std::string(e) : std::string();
#endif
}

inline std::string& slot() {
    static std::string v = readEnv();
    return v;
}

inline const std::string& current() { return slot(); }
inline void set(const std::string& value) { slot() = value; }
inline bool any() { return !slot().empty() && slot() != "0"; }
// noinline: sem isso, MSVC recente incorpora o literal do nome da variante à comparação como cargas imediatas
// cargas (add_wron|g_operat|or), então o nome deixa de existir como bytes contíguos no binário.
#if defined(_MSC_VER)
# define COOP_MUT_NOINLINE __declspec(noinline)
#else
# define COOP_MUT_NOINLINE __attribute__((noinline))
#endif
COOP_MUT_NOINLINE inline bool is(const char* name) { return any() && slot() == name; }
COOP_MUT_NOINLINE inline bool is(int number) { return any() && slot() == std::to_string(number); }

// Opcional: permite a main do teste aceitar `--mut NAME` ou `--mut=NAME`. O par é apagado de argv para o analisador de argumentos posicionais
// não o veja. Retorna a variante ativa.
inline const std::string& init_from_args(int argc, char** argv) {
    for (int i = 1; i < argc; ++i) {
        if (std::strcmp(argv[i], "--mut") == 0 && i + 1 < argc) {
            set(argv[i + 1]);
            argv[i][0] = '\0';
            argv[i + 1][0] = '\0';
            break;
        }
        if (std::strncmp(argv[i], "--mut=", 6) == 0) {
            set(argv[i] + 6);
            argv[i][0] = '\0';
            break;
        }
    }
    return current();
}

}  // namespace coop_mut

#define COOP_MUT_IF(x) (::coop_mut::is(x))
#define COOP_MUT_ANY() (::coop_mut::any())
#else
#define COOP_MUT_IF(x) (false)
#define COOP_MUT_ANY() (false)
#endif
