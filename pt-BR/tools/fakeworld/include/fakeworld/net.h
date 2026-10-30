// Pequeno simulador de enlace com perdas em relógio virtual. Mensagens podem atrasar, reordenar-se (variação de latência), perder-se,
// duplicadas e corrompidas (um bit invertido). Tudo é guiado por RNG com semente, então a execução é reproduzível.
// Substitua pelo seu próprio modelo de transporte, se tiver: Machine só precisa de "enviar bytes a um par" e
// "consultar bytes de um par".
#pragma once
#include <cstdint>
#include <deque>
#include <map>
#include <memory>
#include <queue>
#include <vector>
#include "fakeworld/rng.h"
#include "fakeworld/wire.h"

namespace coop::fakeworld {

using PeerId = uint32_t;

// Qual canal a mensagem usou. O simulador trata ambos igualmente (há perdas em ambos); a camada de enlace dentro de
// Machine adiciona sua própria retransmissão para Reliable, e o gancho de gravação informa o canal.
enum class Channel : uint8_t { Reliable = 0, Unreliable = 1 };

struct LinkParams {
    uint32_t minLatencyMs = 0, maxLatencyMs = 0;  // uniforme; variação acima de min provoca reordenação
    double loss = 0;                              // 0..1 por mensagem
    double duplicate = 0;                         // probabilidade de 0..1 de uma cópia extra
    double corrupt = 0;                           // probabilidade de 0..1 de um único bit invertido
};

class InMemoryNetwork {
public:
    explicit InMemoryNetwork(uint64_t seed = 1) : rng_(seed) {}

    void setLink(const LinkParams& p) { link_ = p; }   // aplica-se a todas as direções
    const LinkParams& link() const { return link_; }
    void send(PeerId from, PeerId to, Bytes data);
    // Retira uma mensagem entregue para `self`; false quando nenhuma está esperando.
    bool poll(PeerId self, PeerId& from, Bytes& data);
    void setConnected(PeerId id, bool up);             // inativo: seu tráfego enfileirado é descartado e os envios desaparecem
    bool connected(PeerId id) const;
    void advance(uint64_t nowMs);                      // entrega tudo cujo horário chegou
    size_t inFlight() const { return pending_.size(); }
    bool idle() const;                                 // nada em trânsito e nenhuma mensagem não lida na caixa de entrada

    struct Stats { uint64_t sent = 0, delivered = 0, lost = 0, duplicated = 0, corrupted = 0, droppedDown = 0; };
    const Stats& stats() const { return stats_; }

private:
    struct Msg {
        uint64_t at; uint64_t order; PeerId from, to; Bytes data;
        bool operator>(const Msg& o) const { return at != o.at ? at > o.at : order > o.order; }
    };
    void enqueue(PeerId from, PeerId to, Bytes data);

    Rng rng_;
    LinkParams link_;
    uint64_t now_ = 0, order_ = 0;
    std::map<PeerId, std::deque<std::pair<PeerId, Bytes>>> inbox_;   // por destinatário, em ordem de chegada
    std::map<PeerId, bool> up_;
    std::priority_queue<Msg, std::vector<Msg>, std::greater<Msg>> pending_;
    Stats stats_;
};

}  // namespace coop::fakeworld
