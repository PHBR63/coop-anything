// Modelo de degradação da rede, somente cabeçalho. Espelho exato de impair.py: mesmo fluxo SplitMix64, mesma
// ordem de chamadas e mesma aritmética; perfil + semente + sequência de pacotes produz resultados idênticos em ambos
// (verificado por tools/chaos/xcheck.py). Puro e com tempo virtual: sem sockets nem relógios.
//
// Uso em simulador ou fuzzer:
//   auto p = coopchaos::profile("bad_wifi");             // veja profiles_gen.h (gerado de profiles.json)
//   coopchaos::Impairment c2s(p, "c2s"), s2c(p, "s2c");  // um por direção, mesmos rótulos do retransmissor
//   auto v = c2s.decide(nowMs, sizeBytes);               // v.dropped() / v.reason / v.delaysMs / v.corrupt
//   for (double d : v.delaysMs) deliverAt(nowMs + d);    // 2+ entradas = duplicata
//   c2s.partition(true); c2s.disconnectUntil(nowMs + 3000); c2s.reconnect();
// Reinicialize com outra semente: p.seed = 42 antes de construir.
#pragma once
#include <cstdint>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace coopchaos {

#ifndef COOPCHAOS_MUTANT
#define COOPCHAOS_MUTANT 0   // compilações de variantes definem 1..4; cada uma deve fazer a verificação cruzada falhar
#endif

struct Params {
    uint64_t seed = 1;
    double latencyMs = 0, jitterMs = 0;   // atraso = latência +/- variação uniforme, limitado ao mínimo 0
    double loss = 0;                      // perda base no estado bom
    double burstEnter = 0, burstExit = 0.5, burstLoss = 1.0;   // Gilbert-Elliott
    double reorder = 0;                   // probabilidade de um pacote pular a latência
    double duplicate = 0, corrupt = 0;
    uint64_t bandwidthBps = 0;            // 0 = ilimitado
    double bufferMs = 200;                // profundidade da fila no limite antes do descarte na cauda

    static Params make(uint64_t seed, double lat, double jit, double loss, double be, double bx, double bl,
                       double reorder, double dup, double corrupt, int64_t bw, double buf) {
        Params p;
        p.seed = seed; p.latencyMs = lat; p.jitterMs = jit; p.loss = loss;
        p.burstEnter = be; p.burstExit = bx; p.burstLoss = bl; p.reorder = reorder;
        p.duplicate = dup; p.corrupt = corrupt; p.bandwidthBps = static_cast<uint64_t>(bw); p.bufferMs = buf;
        return p;
    }
    double expectedLoss() const {
        double s = burstEnter + burstExit;
        double piBad = s > 0 ? burstEnter / s : 0.0;
        return (1 - piBad) * loss + piBad * burstLoss;
    }
};

enum class Reason { None, Loss, Burst, Partition, Disconnect, Bandwidth };

inline const char* reasonName(Reason r) {
    switch (r) {
        case Reason::Loss: return "loss";
        case Reason::Burst: return "burst";
        case Reason::Partition: return "partition";
        case Reason::Disconnect: return "disconnect";
        case Reason::Bandwidth: return "bandwidth";
        default: return "";
    }
}

struct Verdict {
    std::vector<double> delaysMs;   // vazio = descartado
    Reason reason = Reason::None;
    bool corrupt = false;
    bool dropped() const { return delaysMs.empty(); }
};

class Rng {
public:
    Rng() = default;
    Rng(uint64_t seed, const std::string& label) {
        uint64_t h = 0xCBF29CE484222325ULL;
        for (unsigned char c : std::to_string(seed) + ":" + label) { h ^= c; h *= 0x100000001B3ULL; }
        s_ = h;
    }
    uint64_t u64() {
        s_ += 0x9E3779B97F4A7C15ULL;
        uint64_t z = s_;
        z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
        z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
        return z ^ (z >> 31);
    }
    double random() { return static_cast<double>(u64() >> 11) * (1.0 / 9007199254740992.0); }
    double uniform(double a, double b) { return a + (b - a) * random(); }
    uint64_t below(uint64_t n) { return u64() % n; }
private:
    uint64_t s_ = 0;
};

class Impairment {
public:
    Impairment(const Params& p, const std::string& label) : label_(label) { setParams(p, true); }

    void setParams(const Params& p, bool reseed = false) {
        p_ = p;
        if (reseed) { rng_ = Rng(p.seed, label_); bad_ = false; freeAtMs_ = 0.0; }
    }
    const Params& params() const { return p_; }
    Rng& rng() { return rng_; }

    Verdict decide(double nowMs, uint32_t size) {
        Verdict v;
#if COOPCHAOS_MUTANT != 4
        if (partitioned_) { v.reason = Reason::Partition; return v; }
#endif
        if (nowMs < downUntilMs_) { v.reason = Reason::Disconnect; return v; }
        if (bad_) { if (rng_.random() < p_.burstExit) bad_ = false; }
        else if (rng_.random() < p_.burstEnter) bad_ = true;
        double lossp = bad_ ? p_.burstLoss : p_.loss;
        if (rng_.random() < lossp) { v.reason = bad_ ? Reason::Burst : Reason::Loss; return v; }
        double queueMs = 0.0;
        if (p_.bandwidthBps > 0) {
            double txMs = size * 8 * 1000.0 / static_cast<double>(p_.bandwidthBps);
#if COOPCHAOS_MUTANT == 1
            txMs *= 0.9;
#endif
            double start = nowMs > freeAtMs_ ? nowMs : freeAtMs_;
            if (start - nowMs > p_.bufferMs) { v.reason = Reason::Bandwidth; return v; }
            freeAtMs_ = start + txMs;
            queueMs = freeAtMs_ - nowMs;
        }
        v.delaysMs.push_back(oneDelay(queueMs));
        if (p_.duplicate > 0 && rng_.random() < p_.duplicate) v.delaysMs.push_back(oneDelay(queueMs));
        v.corrupt = p_.corrupt > 0 && rng_.random() < p_.corrupt;
        return v;
    }

    void partition(bool on) { partitioned_ = on; }
    void disconnectUntil(double ms) { downUntilMs_ = ms; }
    void reconnect() { downUntilMs_ = -1.0; }

    // Inverte um bit (o índice vem do mesmo fluxo, como em flip_bit de impair.py).
    void flipBit(std::vector<uint8_t>& data) {
        if (data.empty()) return;
        uint64_t i = rng_.below(data.size() * 8);
        data[i / 8] ^= static_cast<uint8_t>(1u << (i % 8));
    }

private:
    double oneDelay(double queueMs) {
        double base;
        if (rng_.random() < p_.reorder) base = 0.0;
        else {
#if COOPCHAOS_MUTANT == 2
            double d = p_.latencyMs + rng_.uniform(0.0, p_.jitterMs);
#else
            double d = p_.latencyMs + rng_.uniform(-p_.jitterMs, p_.jitterMs);
#endif
            base = d > 0.0 ? d : 0.0;
        }
#if COOPCHAOS_MUTANT == 3
        return base;
#else
        return base + queueMs;
#endif
    }

    std::string label_;
    Params p_;
    Rng rng_;
    bool bad_ = false, partitioned_ = false;
    double freeAtMs_ = 0.0, downUntilMs_ = -1.0;
};

}  // namespace coopchaos

#include "profiles_gen.h"

namespace coopchaos {

inline Params profile(const std::string& name) {
    for (const auto& kv : allProfiles()) if (kv.first == name) return kv.second;
    throw std::out_of_range("unknown chaos profile: " + name);
}

}  // namespace coopchaos
