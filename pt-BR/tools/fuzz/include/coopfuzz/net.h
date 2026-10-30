// Enlace com perdas embutido: uma rede de datagramas com tempo virtual entre N máquinas em um processo.
// Mensagens podem atrasar (latência uniforme, então a variação as reordena), perder-se, duplicar e corromper-se (um bit invertido).
// Seu alvo pode usá-lo para seus pacotes, ou fornecer seu próprio transporte e ignorar este arquivo.
#pragma once
#include <cstdint>
#include <queue>
#include <deque>
#include <string>
#include <vector>
#include "coopfuzz/rng.h"

namespace coopfuzz {

using Bytes = std::vector<uint8_t>;

struct LinkParams {
    uint32_t minLatencyMs = 0, maxLatencyMs = 0;  // uniforme; variação acima de min provoca reordenação
    double loss = 0;                              // 0..1 por mensagem
    double duplicate = 0;                         // probabilidade de 0..1 de uma cópia extra
    double corrupt = 0;                           // probabilidade de 0..1 de um único bit invertido
};

// Predefinições nomeadas: lan, good_wifi, bad_wifi, mobile, hell. Retorna false para um nome desconhecido.
bool linkProfile(const std::string& name, LinkParams& out);
std::vector<std::string> linkProfileNames();

class LossyLink {
public:
    LossyLink(int endpoints, uint64_t seed);

    void setLink(const LinkParams& p) { link_ = p; }   // aplica-se a todas as direções
    const LinkParams& link() const { return link_; }

    void send(int from, int to, Bytes data);
    bool poll(int at, int& from, Bytes& data);          // retira uma mensagem recebida; false quando nenhuma está pendente
    void advance(uint64_t nowMs);                       // entrega tudo cujo horário chegou

    void setConnected(int id, bool up);                 // inativo: seu tráfego enfileirado é descartado e os envios desaparecem
    bool connected(int id) const;
    bool idle() const;                                  // nada em trânsito e nenhuma mensagem não lida na caixa de entrada

    struct Stats { uint64_t sent = 0, delivered = 0, lost = 0, duplicated = 0, corrupted = 0, droppedDown = 0; };
    const Stats& stats() const { return stats_; }

private:
    struct Msg {
        uint64_t at, order;
        int from, to;
        Bytes data;
        bool operator>(const Msg& o) const { return at != o.at ? at > o.at : order > o.order; }
    };
    void enqueue(int from, int to, Bytes data);

    Rng rng_;
    LinkParams link_;
    uint64_t now_ = 0, order_ = 0;
    std::vector<std::deque<std::pair<int, Bytes>>> inbox_;
    std::vector<bool> up_;
    std::priority_queue<Msg, std::vector<Msg>, std::greater<Msg>> pending_;
    Stats stats_;
};

}  // namespace coopfuzz
