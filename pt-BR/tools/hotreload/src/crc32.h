// CRC-32 (o de zlib). Usado no identificador da compilação de um arquivo de núcleo e nas somas de verificação de blocos de estado.
#pragma once
#include <cstddef>
#include <cstdint>

namespace hotreload {

inline uint32_t Crc32Update(uint32_t crc, const void* data, size_t n) {
    static const struct Table {
        uint32_t t[256];
        Table() {
            for (uint32_t i = 0; i < 256; ++i) {
                uint32_t c = i;
                for (int k = 0; k < 8; ++k) c = (c & 1) ? (0xEDB88320u ^ (c >> 1)) : (c >> 1);
                t[i] = c;
            }
        }
    } table;
    const uint8_t* p = static_cast<const uint8_t*>(data);
    for (size_t i = 0; i < n; ++i) crc = table.t[(crc ^ p[i]) & 0xFF] ^ (crc >> 8);
    return crc;
}

// CRC-32 em uma única operação, com o valor retornado por zlib.crc32().
inline uint32_t Crc32(const void* data, size_t n) { return Crc32Update(0xFFFFFFFFu, data, n) ^ 0xFFFFFFFFu; }

}  // namespace hotreload
