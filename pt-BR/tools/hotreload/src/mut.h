// Variantes mutantes em execução. Variante viola deliberadamente uma regra de segurança. Testes devem detectar.
//
// Compilações de teste definem HOTRELOAD_RUNTIME_MUT; variante escolhida ao iniciar processo:
//     set HOTRELOAD_MUT=4        (variável de ambiente, lida uma vez)
// ou dentro do processo pelos testes unitários com hotreload_mut::set(n).
// Fontes dizem if (HR_MUT(4)) { ...broken variant... } ou if (!HR_MUT(6)) { ...code the twin removes... }.
// Compilações de produção (sem HOTRELOAD_RUNTIME_MUT) recebem HR_MUT(n) == false: variantes defeituosas são código morto e nada
// lê o ambiente.
//
// Variantes de integração (carregador ou núcleo no host de teste, por tests/scenarios.py):
//    1 drain_off             drenagem diz "ninguém dentro" sem verificar
//    2 adopt_ignored         adoptThread() nada faz; thread de biblioteca pertencente ao núcleo bloqueia drenagem
//    3 managed_ids_ignored   drenagem não ignora ManagedThreads
//    4 no_cache_copy         carregador mapeia arquivo original do núcleo (compilação não pode sobrescrever)
//    5 stale_build_id        carregador mantém id de compilação anterior após recarga
//    6 version_ignored       blob de estado de versão anterior lido como layout atual
//    7 no_state_blob         núcleo antigo nunca entrega estado ao carregador
//    8 save_failure_ignored  participante cujo salvamento falha não veta mais recarga
//    9 no_rollback           carregador permanece morto quando novo núcleo falha ao iniciar
//   10 veto_ignored          carregador descarrega núcleo mesmo se ele recusa
// Variantes unitárias (tests/unit_tests.cpp, executadas com --twin N):
//   14 crc_unchecked         payload corrompido entregue a restore()
//   15 forward_shutdown      shutdown executa na ordem de registro, não inversa
//   16 thread_not_joined     ManagedThread desacopla em vez de fazer join
//   17 drain_ip_only         drenagem examina só ponteiro de instrução, não retornos na pilha
//   18 drain_timeout_ok      timeout de drenagem conta como sucesso
//   19 preflight_ignored     recusas canUnload() não vetam
#pragma once

#ifdef HOTRELOAD_RUNTIME_MUT
#include <cstdlib>

namespace hotreload_mut {
inline int& slot() {
    static int v = [] {
        const char* e = std::getenv("HOTRELOAD_MUT");
        return (e && *e) ? std::atoi(e) : 0;
    }();
    return v;
}
inline int current() { return slot(); }
inline void set(int n) { slot() = n; }
}  // namespace hotreload_mut

#define HR_MUT(n) (::hotreload_mut::current() == (n))
#else
#define HR_MUT(n) (false)
#endif
