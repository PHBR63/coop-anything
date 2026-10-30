// Primitivas de transmissão do mundo simulado: compactas, little-endian, com verificação de limites.
//
// Uma classe Archive simétrica atende aos dois sentidos: toda função io(Archive&, T&) lê quando o arquivo é um
// leitor e escreve quando é escritor, para codificação e decodificação nunca divergirem. Inteiros são varints LEB128
// (os com sinal usam zigzag), floats têm 4 bytes e precisam ser finitos; strings e arrays têm prefixo de comprimento e são verificados
// contra um limite rígido e a quantidade de bytes restantes. Após qualquer falha, o arquivo é marcado inválido: ok() é false, leituras
// retornam valores zero e as escritas não fazem nada. Substitua pelo serializador real do seu jogo, se houver.
#pragma once
#include <cstddef>
#include <cstdint>
#include <string>
#include <vector>
#include "coop/types.h"

namespace coop::fakeworld {

using Bytes = std::vector<uint8_t>;

constexpr size_t kMaxStringLen = 255;
constexpr size_t kMaxEffectsPerBatch = 1024;

uint32_t crc32(const uint8_t* data, size_t size);

class Archive {
public:
    static Archive writer();
    static Archive reader(const uint8_t* data, size_t size);

    bool reading() const { return reading_; }
    bool ok() const { return ok_; }
    void fail() { ok_ = false; }
    size_t remaining() const { return reading_ ? size_ - pos_ : 0; }
    bool atEnd() const { return reading_ && pos_ == size_; }

    void u8(uint8_t& v);
    void u16(uint16_t& v);
    void u32(uint32_t& v);
    void u64(uint64_t& v);
    void varu(uint64_t& v);
    void vari(int64_t& v);
    void varu32(uint32_t& v);
    void vari32(int32_t& v);
    void f32(float& v);
    void boolean(bool& v);
    void str(std::string& s, size_t maxLen = kMaxStringLen);
    void bytes(std::vector<uint8_t>& b, size_t maxLen);
    // Quantidade de elementos de um contêiner. A leitura verifica n <= maxN e n <= remaining() (cada elemento tem >= 1 byte).
    bool count(size_t& n, size_t maxN);

    // Somente escritor: bytes escritos até agora (vazio após falha).
    std::vector<uint8_t> finish() const;

private:
    bool reading_ = false;
    bool ok_ = true;
    std::vector<uint8_t> out_;
    const uint8_t* in_ = nullptr;
    size_t size_ = 0, pos_ = 0;
};

}  // namespace coop::fakeworld
