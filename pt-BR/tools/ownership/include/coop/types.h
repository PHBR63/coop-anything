// Pequenos tipos compartilhados da biblioteca de responsabilidade sobre atores. C++17 simples, sem dependências.
#pragma once
#include <cstddef>
#include <cstdint>

namespace coop {

// Vaga de jogador. A vaga 0 é sempre o host (máquina que executa OwnershipService).
// O serviço mantém um bit por vaga em um byte, portanto há no máximo 8 vagas.
using PlayerId = uint8_t;
constexpr uint8_t kMaxSlots = 8;
constexpr PlayerId kHostPlayer = 0;
constexpr PlayerId kNoPlayer = 0xFF;

// Fowler-Noll-Vo 1a, 64 bits. Usado no resumo de responsabilidade. Os mesmos bytes sempre produzem o mesmo hash.
inline uint64_t hash64(const void* data, size_t size, uint64_t seed = 1469598103934665603ull) {
    const uint8_t* p = static_cast<const uint8_t*>(data);
    uint64_t h = seed;
    for (size_t i = 0; i < size; ++i) { h ^= p[i]; h *= 1099511628211ull; }
    return h;
}

}  // namespace coop
