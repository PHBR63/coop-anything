// Alvo esqueleto: menor exemplo completo de envolver núcleo de sincronização na interface ITarget.
// Leia primeiro isto, depois GUIDE.md. example_target.cpp é exemplo completo.
//
// Parte 1 representa SEU núcleo: pequena sincronização de posição com autoridade host para 2 a 4. Nada sabe sobre o
// fuzzer. Comunica-se com o mundo só por callback de envio, onPacket(), tick() e alguns acessores, formato que seu núcleo real
// precisa ter (veja GUIDE.md, "What your core must allow").
// Parte 2 é adaptador: possui N núcleos, conecta pelo LossyLink embutido, avança relógio virtual, mapeia operações ao núcleo,
// relata o que cada máquina aplicou e responde às perguntas dos oráculos.
#include <algorithm>
#include <functional>
#include <set>
#include "coopfuzz/fuzz.h"

namespace coopfuzz {
namespace {

// ====================================================================== parte 1: núcleo de sincronização testado
uint32_t sum32(const uint8_t* p, size_t n) {
    uint32_t h = 2166136261u;
    for (size_t i = 0; i < n; ++i) { h ^= p[i]; h *= 16777619u; }
    return h;
}
void put32(Bytes& b, uint32_t v) { for (int i = 0; i < 4; ++i) b.push_back(static_cast<uint8_t>(v >> (8 * i))); }
uint32_t get32(const Bytes& b, size_t at) { uint32_t v = 0; for (int i = 0; i < 4; ++i) v |= static_cast<uint32_t>(b[at + static_cast<size_t>(i)]) << (8 * i); return v; }

struct Pos { int x = 0, y = 0; };

// Relato de mensagem aplicada: o núcleo chama isto sempre que aplica ou rejeita mensagem. Núcleos reais precisam desse hook.
using ReportFn = std::function<void(int machine, uint64_t idem, int player, uint32_t seq, int origin, bool accepted, const char* why)>;

class PosCore {
public:
    // Pacotes: 1 = posição cliente (seq, x, y), 2 = confirmação de posição (seq), 3 = tabela (versão, posições de todos), 4 = confirmação de tabela.
    PosCore(int id, int players, bool dedupeTables, std::function<void(int, Bytes)> send, ReportFn report)
        : id_(id), n_(players), dedupe_(dedupeTables), send_(std::move(send)), report_(std::move(report)), pos_(static_cast<size_t>(players)),
          lastSeq_(static_cast<size_t>(players), 0), tableAcked_(static_cast<size_t>(players), 0) {}

    void setLocalPosition(int x, int y) {   // thread do jogo diz: meu jogador moveu
        pos_[static_cast<size_t>(id_)] = {x, y};
        if (id_ == 0) { ++version_; return; }
        ++localSeq_;
    }
    void tick() {                           // chamado a cada 50 ms de tempo virtual
        if (id_ != 0) {
            if (ackedSeq_ < localSeq_) {
                Bytes b; b.push_back(1); put32(b, localSeq_); put32(b, static_cast<uint32_t>(pos_[static_cast<size_t>(id_)].x)); put32(b, static_cast<uint32_t>(pos_[static_cast<size_t>(id_)].y));
                send(0, b);
            }
            return;
        }
        for (int c = 1; c < n_; ++c) {
            if (tableAcked_[static_cast<size_t>(c)] >= version_) continue;
            Bytes b; b.push_back(3); put32(b, version_);
            for (auto& p : pos_) { put32(b, static_cast<uint32_t>(p.x)); put32(b, static_cast<uint32_t>(p.y)); }
            send(c, b);
        }
    }
    void onPacket(int from, const Bytes& d) {
        if (d.size() < 5 || sum32(d.data(), d.size() - 4) != get32(d, d.size() - 4)) return;   // corrompido: descartar, remetente reenviará
        size_t body = d.size() - 4;
        switch (d[0]) {
            case 1: if (id_ == 0 && body >= 13) onClientPos(from, get32(d, 1), static_cast<int>(get32(d, 5)), static_cast<int>(get32(d, 9))); break;
            case 2: if (id_ != 0 && body >= 5) ackedSeq_ = std::max(ackedSeq_, get32(d, 1)); break;
            case 3: if (id_ != 0 && body >= 5 + static_cast<size_t>(n_) * 8) onTable(d); break;
            case 4: if (id_ == 0 && body >= 5) tableAcked_[static_cast<size_t>(from)] = std::max(tableAcked_[static_cast<size_t>(from)], get32(d, 1)); break;
            default: break;
        }
    }
    bool settledWith(const PosCore& host) const { return id_ == 0 || (ackedSeq_ == localSeq_ && myVersion_ == host.version_); }
    uint32_t version() const { return version_; }
    uint32_t tableAcked(int c) const { return tableAcked_[static_cast<size_t>(c)]; }
    Pos position(int p) const { return pos_[static_cast<size_t>(p)]; }

private:
    void send(int to, Bytes b) { put32(b, sum32(b.data(), b.size())); send_(to, std::move(b)); }
    void onClientPos(int from, uint32_t seq, int x, int y) {
        uint64_t idem = (1ull << 62) | (static_cast<uint64_t>(from) << 32) | seq;
        if (seq <= lastSeq_[static_cast<size_t>(from)]) report_(0, idem, from, seq, from, false, "old sequence");
        else {
            lastSeq_[static_cast<size_t>(from)] = seq;
            pos_[static_cast<size_t>(from)] = {x, y};
            ++version_;
            report_(0, idem, from, seq, from, true, "");
        }
        Bytes a; a.push_back(2); put32(a, lastSeq_[static_cast<size_t>(from)]);   // sempre confirmar para cliente parar de reenviar
        send(from, a);
    }
    void onTable(const Bytes& d) {
        uint32_t version = get32(d, 1);
        if (dedupe_ && version <= myVersion_) {
            report_(id_, (2ull << 62) | (static_cast<uint64_t>(version) << 8), -1, version, 0, false, "old table");
        } else {
            for (int p = 0; p < n_; ++p) {
                if (p == id_) continue;   // máquina possui própria posição e nunca a recebe de volta do host
                pos_[static_cast<size_t>(p)] = {static_cast<int>(get32(d, 5 + static_cast<size_t>(p) * 8)), static_cast<int>(get32(d, 9 + static_cast<size_t>(p) * 8))};
                report_(id_, (2ull << 62) | (static_cast<uint64_t>(version) << 8) | static_cast<uint64_t>(p), p, version, 0, true, "");
            }
            myVersion_ = std::max(myVersion_, version);   // variante defeituosa mantém deduplicação desligada; tabela antiga reaplicada
        }
        Bytes a; a.push_back(4); put32(a, myVersion_);
        send(0, a);
    }

    int id_, n_;
    bool dedupe_;
    std::function<void(int, Bytes)> send_;
    ReportFn report_;
    std::vector<Pos> pos_;
    uint32_t localSeq_ = 0, ackedSeq_ = 0, myVersion_ = 0, version_ = 0;
    std::vector<uint32_t> lastSeq_, tableAcked_;
};

// ====================================================================== parte 2: adaptador controlado pelo fuzzer
class SkeletonTarget : public TargetBase {
public:
    SkeletonTarget(const Scenario& s, bool noDedupe) : net_(s.machines, s.seed * 77 + 3), n_(s.machines) {
        LinkParams link = s.link;
        if (!s.profile.empty()) linkProfile(s.profile, link);   // esqueleto ignora operações SetLink; enlace inicial constitui todo o caos
        net_.setLink(link);
        for (int m = 0; m < n_; ++m) {
            cores_.emplace_back(new PosCore(
                m, n_, !noDedupe, [this, m](int to, Bytes b) { net_.send(m, to, std::move(b)); },
                [this](int machine, uint64_t idem, int player, uint32_t seq, int origin, bool ok, const char* why) {
                    // UM relato por mensagem aplicada ou rejeitada. Oráculos leem estes.
                    logApply(machine, idem, player < 0 ? -1 : static_cast<int>(0x100 + static_cast<uint32_t>(player)), 0, seq, origin, ApplyKind::PlayerPos, ok, 0, why);
                }));
        }
    }

    uint64_t now() const override { return now_; }
    int machines() const override { return n_; }
    bool connected(int) const override { return true; }   // este esqueleto não tem entrada ou saída
    uint64_t repairs(int) const override { return 0; }    // esqueleto sem caminho de reparo, portanto não pode reparar
    void apply(const Op& op) override {
        if (op.kind != OpKind::Move) return;               // todo o resto está fora deste núcleo: ignorar
        int m = std::max(0, std::min(n_ - 1, op.m));
        ++counters_["op_move"];
        cores_[static_cast<size_t>(m)]->setLocalPosition(std::max(0, std::min(1000, op.a)), std::max(0, std::min(1000, op.b)));
    }
    void advance(uint64_t toMs) override {
        while (now_ < toMs) {
            now_ = std::min<uint64_t>(now_ + 10, toMs);
            net_.advance(now_);
            for (int m = 0; m < n_; ++m) { int from = 0; Bytes d; while (net_.poll(m, from, d)) cores_[static_cast<size_t>(m)]->onPacket(from, d); }
            while (now_ >= next50_) { next50_ += 50; for (auto& c : cores_) c->tick(); }
        }
    }
    void heal() override { frozen_ = true; net_.setLink(LinkParams()); }   // enlace perfeito; fuzzer não envia mais operações depois disto
    bool quiescent() const override {
        if (!frozen_ || !net_.idle()) return false;
        for (int m = 1; m < n_; ++m)
            if (!cores_[static_cast<size_t>(m)]->settledWith(*cores_[0]) || cores_[0]->tableAcked(m) != cores_[0]->version()) return false;
        return true;
    }
    std::vector<Thing> view(int m) const override {   // tudo que a máquina m acredita sobre o mundo, ordenado por id de rede
        std::vector<Thing> v;
        for (int p = 0; p < n_; ++p) {
            Thing t; t.netId = 0x100 + static_cast<uint32_t>(p); t.type = 0; t.hp = 100;
            Pos q = cores_[static_cast<size_t>(m)]->position(p);
            t.x = q.x; t.y = q.y;
            v.push_back(t);
        }
        return v;
    }
    uint64_t digest(int m, int cat) const override {   // igual em todas as máquinas quando concordam
        uint64_t h = 1469598103934665603ull + static_cast<uint64_t>(cat);
        for (auto& t : view(m)) { h ^= static_cast<uint64_t>(t.x) * 1000003u + static_cast<uint64_t>(t.y); h *= 1099511628211ull; }
        return h;
    }

private:
    LossyLink net_;
    int n_;
    bool frozen_ = false;
    uint64_t now_ = 0, next50_ = 50;
    std::vector<std::unique_ptr<PosCore>> cores_;
};

std::unique_ptr<ITarget> makeSkeleton(const Scenario& s, std::string* err) {
    bool noDedupe = false;
    for (auto& b : s.bugs) {
        if (b == "no_dedupe") noDedupe = true;
        else { if (err) *err = "unknown bug class for target skeleton: " + b; return nullptr; }
    }
    return std::make_unique<SkeletonTarget>(s, noDedupe);
}

const TargetRegistrar kRegisterSkeleton(TargetInfo{"skeleton", "smallest complete target: host-authoritative player positions, 1 bug class", {"no_dedupe"}, makeSkeleton});

}  // namespace
}  // namespace coopfuzz
