// Como um mod usa o gravador. Alvo de compilação: cofr_example. Execução: cofr_example [pasta de saída]
// Executa uma pequena sessão simulada e escreve um arquivo .cofr ao final, como um mod ao detectar dessincronização.
#include <cstdio>
#include <cstring>
#include "cofr.h"

namespace {

// Seu decodificador de protocolo. Executa quando o gravador gera um despejo, em cada datagrama não truncado.
// Este protocolo simulado é: byte 0 = 0xC0, byte 1 = tipo de mensagem, bytes 2..9 = seq.
bool decodeMyProtocol(const uint8_t* d, size_t n, cofr::NetMeta& m) {
    if (n < 10 || d[0] != 0xC0) return false;   // não é meu protocolo
    m.msgType = d[1];
    std::memcpy(&m.seqLo, d + 2, 8);            // adequado em máquinas little-endian
    m.seqHi = m.seqLo;
    return true;
}

}  // namespace

int main(int argc, char** argv) {
    // 1. Configura e cria um gravador por máquina.
    cofr::Config cfg;
    cfg.slot = 1;                         // número desta máquina; o host normalmente é 0
    cfg.role = cofr::kRoleClient;
    cfg.label = "client-1";               // aparece em relatórios e nomes de arquivos
    cfg.dir = argc > 1 ? argv[1] : "flight";
    cfg.ringBytes = 16u << 20;            // os 16 MB mais recentes de registros são mantidos
    cfg.decoder = decodeMyProtocol;       // opcional
    cfg.schemaJson = R"({"game":"mygame","digest_categories":{"0":"quests","1":"npcs"},"message_types":{"4":"batch","5":"ack"}})";
    cofr::Recorder recorder(cfg);
    recorder.mapPeer(0, 0);               // nesta máquina, o par de transporte 0 é o host, slot de máquina 0

    // Ganchos só precisam da pequena interface, então uma compilação de lançamento pode passar observador nulo.
    cofr::IObserver* obs = &recorder;

    // 2. Seus ganchos o chamam. Aqui, um mundo simulado de chave -> hash de valor que muda quando o host envia um lote.
    cofr::BucketedState world;            // mantém o resumo atualizado, uma entrada por vez
    for (uint64_t seq = 1; seq <= 3; ++seq) {
        obs->setFrame(static_cast<uint32_t>(seq * 60));

        uint8_t batch[10] = {0xC0, 4};
        std::memcpy(batch + 2, &seq, 8);
        obs->netIn(0, batch, sizeof batch);                       // um datagrama chegou do par 0

        world.set(1000 + seq, static_cast<uint32_t>(seq * 10));   // o lote mudou uma entrada do mundo
        cofr::AppliedEvent applied;                               // e o efeito foi aplicado ao mundo local
        applied.seq = seq; applied.index = 0; applied.epoch = 1;
        applied.hash = cofr::hash64(&seq, sizeof seq);            // qualquer hash do efeito que seja igual em todas as máquinas
        obs->applied(applied);

        uint8_t ack[10] = {0xC0, 5};
        std::memcpy(ack + 2, &seq, 8);
        obs->netOut(0, ack, sizeof ack);                          // uma confirmação foi enviada
    }

    // 3. Um resumo em um ponto sem tráfego (a cada poucos segundos basta).
    obs->digest(world.digest(0, 1, 3));

    // 4. Sua verificação encontrou dessincronização: escreve o detalhe por chave, depois gera despejo. onDesync tem limite de frequência.
    recorder.digestDetail(0, 1, 3, world.entries());
    for (const auto& e : world.entries()) recorder.entryText(e.first, e.second, "quest " + std::to_string(e.first) + " = " + std::to_string(e.second));
    std::string path = recorder.onDesync("quests digest differs from the host at seq 3");
    if (path.empty()) {
        std::printf("no file written (is %s writable?)\n", cfg.dir.c_str());
        return 1;
    }
    std::printf("wrote %s\n", path.c_str());

    // 5. Lê de volta, como um teste faria.
    cofr::Trace t;
    std::string err;
    if (!cofr::readTrace(path, t, &err)) { std::printf("cannot read it back: %s\n", err.c_str()); return 1; }
    std::printf("%zu records, slot %d\n", t.records.size(), static_cast<int>(t.header.slot));
    return t.records.size() > 10 ? 0 : 1;
}
