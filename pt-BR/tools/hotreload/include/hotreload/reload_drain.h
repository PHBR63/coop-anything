// Drenagem para recarregamento. Antes de desmapear a DLL do núcleo, espera até nenhuma outra thread executar ou ter um quadro na pilha
// no código prestes a ser removido. Windows, dentro do processo. Uma thread ainda dentro travaria o jogo no
// momento em que a DLL fosse desmapeada.
#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace hotreload {

struct CodeRange {
    uintptr_t lo = 0, hi = 0;  // [lo, hi)
    const char* what = "";     // rótulo estático usado em mensagens ("core image", "hook trampoline")
};

struct DrainResult {
    bool drained = false;
    int attempts = 0;
    int scanned = 0;               // threads inspecionadas na última tentativa
    unsigned long busyThread = 0;  // última thread encontrada dentro (0 se drenado)
    unsigned elapsedMs = 0;        // tempo real gasto esperando
    unsigned timeoutMs = 0;        // o limite solicitado
    std::string why;               // vazio quando drenado; caso contrário, uma frase completa para o registro
    std::string where;             // o que fez a última thread contar como ocupada ("instruction pointer 0x... in <label> ..." ou "return address ...")
    // Um objeto JSON com os campos acima (strings escapadas).
    std::string toJson() const;
};

// Espera até timeoutMs. `ignore` = IDs de threads não contabilizadas (o próprio chamador sempre é ignorado). A integração passa
// as ManagedThreads e threads adotadas aqui, pois seus responsáveis as param e aguardam seu fim após a drenagem.
// Uma thread conta como interna quando seu ponteiro de instrução está em um intervalo, ou quando alguma palavra alinhada da pilha ativa
// (do ponteiro da pilha até a base, no máximo 1 MB) aponta para um intervalo (endereço de retorno). Isto é conservador: uma
// palavra antiga pode atrasar a drenagem, nunca fazê-la passar incorretamente. Uma thread que não puder ser aberta, suspensa ou lida, e um
// processo com mais de 4096 threads também contam como ocupados, nunca drenados. timeoutMs 0 = uma tentativa. Um tempo limite
// positivo sempre tem ao menos duas tentativas, mesmo se a primeira varredura sozinha exceder o limite.
// Enquanto threads estão suspensas, isto não aloca nem gera registros.
DrainResult waitDrained(const std::vector<CodeRange>& ranges, const std::vector<unsigned long>& ignore, unsigned timeoutMs);

// A imagem do módulo que contém `anyAddressInCore`, como intervalo.
CodeRange moduleRangeOf(const void* anyAddressInCore);

}  // namespace hotreload
