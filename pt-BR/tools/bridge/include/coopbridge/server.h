// coopbridge/server.h: servidor RPC dentro do jogo para testes. Apenas cabeçalho, C++17.
//
// Um servidor fica dentro do processo do jogo. Uma thread de transporte aceita conexões e lê
// solicitações JSON delimitadas por novas linhas (veja PROTOCOL.md). Cada solicitação que acessa o jogo é colocada numa
// fila; o jogo chama Server::Pump() uma vez por interceptação de quadro, e Pump() executa as solicitações enfileiradas
// nessa thread. Seu adaptador, o único código que acessa o jogo, portanto sempre é chamado na
// thread principal do jogo.
//
//   class MyAdapter : public coopbridge::Adapter {
//     Capabilities capabilities() const override { Capabilities c; c.exec = true; return c; }
//     ExecResult Exec(const std::string& line, const std::string&) override { return {true, RunConsole(line)}; }
//   };
//
//   coopbridge::Options opt;  opt.game = "mygame";  opt.tcpPort = 27990;
//   server.Start(opt, adapter);          // uma vez, no início do plugin
//   server.Pump();                       // uma vez por quadro, na thread principal
//   server.Stop();                       // no encerramento, na thread principal
//
// Transportes: TCP em endereço de loopback (todos os SOs) e, no Windows, pipe nomeado. O servidor nunca
// escuta num endereço fora de loopback, a menos que Options::allowRemote esteja definido.
//
// Métodos do adaptador informam falhas lançando coopbridge::Error (código e mensagem próprios) ou qualquer
// std::exception (código -32000). O servidor os transforma em respostas de erro.
#pragma once

#include "json.h"

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <deque>
#include <functional>
#include <list>
#include <map>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <thread>
#include <utility>
#include <vector>

#ifdef _WIN32
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#ifdef _MSC_VER
#pragma comment(lib, "ws2_32.lib")
#endif
#else
#include <arpa/inet.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <sys/select.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <unistd.h>
#include <cerrno>
#endif

namespace coopbridge {

constexpr int kProtocolVersion = 1;

// Códigos de erro transportados em {"error":{"code":...}}. Veja PROTOCOL.md.
namespace errc {
constexpr int kParse = -32700;            // a linha não é JSON
constexpr int kInvalidRequest = -32600;   // JSON, mas não um objeto de solicitação com método em string
constexpr int kMethodNotFound = -32601;   // método desconhecido ou não suportado pelo adaptador
constexpr int kInvalidParams = -32602;    // um parâmetro está ausente ou tem tipo errado
constexpr int kHost = -32000;             // o adaptador ou handler falhou
constexpr int kMainThreadTimeout = -32001;  // a thread principal do jogo não executou a solicitação a tempo
constexpr int kTimeout = -32002;          // carregamento ou salvamento não terminou a tempo
constexpr int kBusy = -32003;             // solicitações demais esperando pela thread principal
constexpr int kStopping = -32004;         // o servidor está encerrando
}  // namespace errc

class Error : public std::runtime_error {
public:
    Error(int code, const std::string& message) : std::runtime_error(message), code_(code) {}
    int code() const { return code_; }
private:
    int code_;
};

struct ExecResult {
    bool ok = false;        // o jogo aceitou e executou a linha
    std::string output;     // o que a linha imprimiu, "" quando o jogo não consegue capturar
};

// Quais métodos padrão este jogo suporta. Um método não listado responde -32601.
struct Capabilities {
    bool exec = false, eval = false, state = false, save = false, load = false, screenshot = false;
};

// Tudo que o servidor precisa do jogo. Cada método executa na thread principal, dentro de Pump().
// Sobrescreva apenas o que seu jogo consegue fazer e informe em capabilities().
class Adapter {
public:
    virtual ~Adapter() = default;
    virtual Capabilities capabilities() const { return Capabilities(); }
    // Executa uma linha de console (ou script). `ref` é "" ou uma referência na qual a linha deve executar.
    virtual ExecResult Exec(const std::string& /*line*/, const std::string& /*ref*/) { throw Error(errc::kMethodNotFound, "exec is not supported"); }
    // Avalia uma expressão e retorna número, bool ou string.
    virtual json::Value Eval(const std::string& /*expr*/, const std::string& /*ref*/) { throw Error(errc::kMethodNotFound, "eval is not supported"); }
    // Um instantâneo JSON do estado do jogo. `sections` vazio significa tudo.
    virtual json::Value State(const std::vector<std::string>& /*sections*/) { throw Error(errc::kMethodNotFound, "state is not supported"); }
    // Inicia o carregamento de um save. Retorna imediatamente e chama Server::NotifyLoaded() quando o jogo estiver no mundo.
    virtual void Load(const std::string& /*name*/) { throw Error(errc::kMethodNotFound, "load is not supported"); }
    // Inicia um salvamento. Retorna imediatamente e chama Server::NotifySaved(path) quando o arquivo for gravado.
    virtual void Save(const std::string& /*name*/, bool /*overwrite*/) { throw Error(errc::kMethodNotFound, "save is not supported"); }
    // Grava uma captura de tela. `path` é "" (você escolhe) ou o arquivo desejado. Retorna o caminho gravado.
    virtual std::string Screenshot(const std::string& /*path*/) { throw Error(errc::kMethodNotFound, "screenshot is not supported"); }
};

// Um método personalizado. Lance exceção para falhar. Executa na thread principal, salvo registro com onMainThread=false.
using Handler = std::function<json::Value(const json::Value& params)>;

struct Options {
    std::string game = "game";        // informado por `version`
    std::string build;                // informado por `version` (hash git, ID de compilação)
    int tcpPort = 0;                  // -1 = sem TCP, 0 = escolher porta livre, caso contrário essa porta
    std::string tcpHost = "127.0.0.1";  // deve ser endereço de loopback, salvo allowRemote
    bool allowRemote = false;         // permite tcpHost fora de loopback. Qualquer pessoa que alcance a porta pode executar linhas de console.
    std::string pipeName;             // Windows: \\.\pipe\<pipeName>. "" = sem pipe
    std::string endpointFile;         // se definido, um arquivo JSON com os endpoints é gravado em Start e removido em Stop
    int defaultTimeoutMs = 30000;     // para solicitações sem timeoutMs
    int slackMs = 2000;               // tempo extra que uma solicitação pode esperar por um Pump() após seu próprio tempo limite
    size_t maxCallsPerPump = 16;      // solicitações iniciadas por chamada de Pump() (esperas já em andamento são sempre atualizadas)
    size_t maxPending = 256;          // solicitações que podem esperar pela thread principal. As excedentes recebem -32003
    size_t eventCapacity = 1024;      // eventos mantidos para `events`
    size_t maxLineBytes = 4u << 20;   // tamanho máximo da linha de solicitação
};

struct Stats {
    uint64_t frames = 0;         // chamadas de Pump()
    uint64_t served = 0;         // solicitações executadas na thread principal
    uint64_t maxDrained = 0;     // máximo de solicitações iniciadas por um Pump()
    uint64_t rejectedBusy = 0;   // solicitações recusadas com -32003
    int64_t mainLoopAgeMs = -1;  // ms desde o último Pump(), -1 se nunca executou
};

class Server {
public:
    Server() = default;
    ~Server() { Stop(); }
    Server(const Server&) = delete;
    Server& operator=(const Server&) = delete;

    // Inicia as threads de transporte. False (veja lastError()) quando nenhum transporte conseguiu iniciar.
    bool Start(const Options& opt, Adapter& adapter) {
        if (running_) { error_ = "already started"; return false; }
        opt_ = opt;
        adapter_ = &adapter;
        error_.clear();
        endpoints_.clear();
        stopping_ = false;
        startMs_ = NowMs();
        if (opt_.tcpPort < 0 && opt_.pipeName.empty()) { error_ = "no transport: set tcpPort or pipeName"; return false; }
#ifdef _WIN32
        WSADATA wsa;
        if (WSAStartup(MAKEWORD(2, 2), &wsa) != 0) { error_ = "WSAStartup failed"; return false; }
        wsaStarted_ = true;
#endif
        if (opt_.tcpPort >= 0 && !StartTcp()) { Stop(); return false; }
        if (!opt_.pipeName.empty() && !StartPipe()) { Stop(); return false; }
        WriteEndpointFile();
        running_ = true;
        return true;
    }

    // Interrompe o transporte e reprova as solicitações ainda esperando. Chame na thread principal (ou quando Pump() não estiver executando).
    void Stop() {
        stopping_ = true;
        if (tcpAcceptor_.joinable()) tcpAcceptor_.join();
        if (pipeAcceptor_.joinable()) StopPipeAcceptor();
        CloseListeners();
        {
            std::lock_guard<std::mutex> g(qmu_);
            for (auto& j : inbox_) j->FinishErr(errc::kStopping, "the server is stopping");
            inbox_.clear();
        }
        for (auto& j : pending_) j->FinishErr(errc::kStopping, "the server is stopping");
        pending_.clear();
        std::list<std::unique_ptr<Conn>> conns;
        {
            std::lock_guard<std::mutex> g(connMu_);
            conns.swap(conns_);
        }
        for (auto& c : conns)
            if (c->th.joinable()) c->th.join();
        if (running_ && !opt_.endpointFile.empty()) std::remove(opt_.endpointFile.c_str());
#ifdef _WIN32
        if (wsaStarted_) { WSACleanup(); wsaStarted_ = false; }
#endif
        running_ = false;
    }

    // Chame uma vez por quadro na thread principal do jogo. Executa solicitações enfileiradas e atualiza esperas em andamento.
    void Pump() {
        frames_.fetch_add(1);
        lastPumpMs_.store(NowMs());
        pumpThread_.store(std::hash<std::thread::id>()(std::this_thread::get_id()));

        std::deque<std::shared_ptr<Job>> take;
        {
            std::lock_guard<std::mutex> g(qmu_);
            while (!inbox_.empty() && take.size() < opt_.maxCallsPerPump) {
                take.push_back(inbox_.front());
                inbox_.pop_front();
            }
        }
        if (take.size() > maxDrained_.load()) maxDrained_.store(take.size());
        for (auto& job : take) {
            if (job->IsAbandoned()) continue;
            served_.fetch_add(1);
            Dispatch(job);
        }
        for (auto it = pending_.begin(); it != pending_.end();) {
            Job& j = **it;
            if (j.IsAbandoned() || j.step(j)) it = pending_.erase(it);
            else ++it;
        }
    }

    // Verdadeiro quando chamado da thread que chama Pump(). Útil para asserções num adaptador.
    bool OnPumpThread() const { return pumpThread_.load() == std::hash<std::thread::id>()(std::this_thread::get_id()); }

    // Adiciona um método personalizado. Nomes de métodos padrão não podem ser substituídos. Pode ser chamado a qualquer momento com segurança.
    void Register(const std::string& name, Handler fn, bool onMainThread = true) {
        std::lock_guard<std::mutex> g(regMu_);
        methods_[name] = Entry{std::move(fn), onMainThread};
    }

    // Adiciona um evento para `events`. Qualquer thread.
    void PushEvent(const std::string& type, const json::Value& data = json::Value()) {
        std::lock_guard<std::mutex> g(evMu_);
        Event e;
        e.seq = ++lastSeq_;
        e.tMs = NowMs() - startMs_;
        e.type = type;
        e.data = data;
        events_.push_back(std::move(e));
        while (events_.size() > opt_.eventCapacity) events_.pop_front();
    }

    // Informe ao servidor que o jogo concluiu um carregamento / salvamento. Chame da thread principal (ou de qualquer thread).
    void NotifyLoaded() {
        loaded_.fetch_add(1);
        PushEvent("game.loaded");
    }
    void NotifySaved(const std::string& path) {
        { std::lock_guard<std::mutex> g(saveMu_); lastSavedPath_ = path; }
        saved_.fetch_add(1);
        json::Value d = json::Value::object();
        d.set("path", path);
        PushEvent("game.saved", d);
    }
    // Para `ping`: defina como verdadeiro quando o jogo estiver pronto para testes (por exemplo, no menu principal).
    void SetReady(bool ready) { ready_.store(ready); }

    const std::vector<std::string>& endpoints() const { return endpoints_; }
    int tcpPort() const { return tcpBoundPort_; }
    const std::string& lastError() const { return error_; }
    Stats stats() const {
        Stats s;
        s.frames = frames_.load();
        s.served = served_.load();
        s.maxDrained = maxDrained_.load();
        s.rejectedBusy = rejectedBusy_.load();
        const uint64_t last = lastPumpMs_.load();
        s.mainLoopAgeMs = last ? static_cast<int64_t>(NowMs() - last) : -1;
        return s;
    }

private:
    using Clock = std::chrono::steady_clock;
    static uint64_t NowMs() {
        return static_cast<uint64_t>(std::chrono::duration_cast<std::chrono::milliseconds>(Clock::now().time_since_epoch()).count()) + 1;
    }

    // ------------------------------------------------------------------------------------------ tarefas
    struct Job {
        std::string method;
        json::Value params;
        uint64_t deadlineMs = 0;
        std::mutex mu;
        std::condition_variable cv;
        bool done = false, abandoned = false, ok = true;
        int errCode = 0;
        std::string errMsg;
        json::Value result;
        std::function<bool(Job&)> step;   // definido para esperas: retorna verdadeiro ao terminar

        void FinishOk(json::Value r) {
            std::lock_guard<std::mutex> g(mu);
            ok = true; result = std::move(r); done = true;
            cv.notify_all();
        }
        void FinishErr(int code, const std::string& msg) {
            std::lock_guard<std::mutex> g(mu);
            ok = false; errCode = code; errMsg = msg; done = true;
            cv.notify_all();
        }
        bool IsAbandoned() {
            std::lock_guard<std::mutex> g(mu);
            return abandoned;
        }
    };

    struct Entry {
        Handler fn;
        bool onMainThread = true;
    };

    struct Event {
        uint64_t seq = 0, tMs = 0;
        std::string type;
        json::Value data;
    };

    // ------------------------------------------------------------------------------------------ fluxos
    class Stream {
    public:
        virtual ~Stream() = default;
        // > 0: bytes lidos. 0: nada chegou ainda. < 0: o par saiu.
        virtual int Read(char* buf, int cap) = 0;
        virtual bool Write(const char* data, size_t n) = 0;
        virtual void Close() = 0;
    };

#ifdef _WIN32
    using SockT = SOCKET;
    static constexpr SockT kBadSock = INVALID_SOCKET;
    static void CloseSock(SockT s) { closesocket(s); }
    static int LastSockError() { return WSAGetLastError(); }
    static bool IsTimeout(int e) { return e == WSAETIMEDOUT || e == WSAEWOULDBLOCK; }
#else
    using SockT = int;
    static constexpr SockT kBadSock = -1;
    static void CloseSock(SockT s) { ::close(s); }
    static int LastSockError() { return errno; }
    static bool IsTimeout(int e) { return e == EAGAIN || e == EWOULDBLOCK || e == EINTR; }
#endif

    class SockStream : public Stream {
    public:
        explicit SockStream(SockT s) : s_(s) {
#ifdef _WIN32
            DWORD ms = 100;
            setsockopt(s_, SOL_SOCKET, SO_RCVTIMEO, reinterpret_cast<const char*>(&ms), sizeof ms);
#else
            timeval tv;
            tv.tv_sec = 0;
            tv.tv_usec = 100000;
            setsockopt(s_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
#endif
            int one = 1;
            setsockopt(s_, IPPROTO_TCP, TCP_NODELAY, reinterpret_cast<const char*>(&one), sizeof one);
        }
        ~SockStream() override { Close(); }
        int Read(char* buf, int cap) override {
            const int r = static_cast<int>(::recv(s_, buf, cap, 0));
            if (r > 0) return r;
            if (r == 0) return -1;
            return IsTimeout(LastSockError()) ? 0 : -1;
        }
        bool Write(const char* data, size_t n) override {
            size_t off = 0;
            while (off < n) {
                int flags = 0;
#ifdef MSG_NOSIGNAL
                flags = MSG_NOSIGNAL;
#endif
                const int w = static_cast<int>(::send(s_, data + off, static_cast<int>(n - off), flags));
                if (w <= 0) {
                    if (w < 0 && IsTimeout(LastSockError())) continue;
                    return false;
                }
                off += static_cast<size_t>(w);
            }
            return true;
        }
        void Close() override {
            if (s_ != kBadSock) { CloseSock(s_); s_ = kBadSock; }
        }
    private:
        SockT s_;
    };

#ifdef _WIN32
    class PipeStream : public Stream {
    public:
        explicit PipeStream(HANDLE h) : h_(h) {}
        ~PipeStream() override { Close(); }
        int Read(char* buf, int cap) override {
            DWORD avail = 0;
            if (!PeekNamedPipe(h_, nullptr, 0, nullptr, &avail, nullptr)) return -1;
            if (avail == 0) { Sleep(2); return 0; }
            DWORD n = 0;
            if (!ReadFile(h_, buf, avail < static_cast<DWORD>(cap) ? avail : static_cast<DWORD>(cap), &n, nullptr) || n == 0) return -1;
            return static_cast<int>(n);
        }
        bool Write(const char* data, size_t n) override {
            size_t off = 0;
            while (off < n) {
                DWORD w = 0;
                if (!WriteFile(h_, data + off, static_cast<DWORD>(n - off), &w, nullptr) || w == 0) return false;
                off += w;
            }
            return true;
        }
        void Close() override {
            if (h_ != INVALID_HANDLE_VALUE) {
                FlushFileBuffers(h_);
                DisconnectNamedPipe(h_);
                CloseHandle(h_);
                h_ = INVALID_HANDLE_VALUE;
            }
        }
    private:
        HANDLE h_;
    };
#endif

    struct Conn {
        std::unique_ptr<Stream> stream;
        std::thread th;
        std::atomic<bool> done{false};
    };

    // ------------------------------------------------------------------------------------------ transportes
    static bool IsLoopback(const std::string& host) {
        if (host == "localhost") return true;
        in_addr a;
        if (inet_pton(AF_INET, host.c_str(), &a) != 1) return false;
        return (ntohl(a.s_addr) >> 24) == 127;
    }

    bool StartTcp() {
        if (!opt_.allowRemote && !IsLoopback(opt_.tcpHost)) {
            error_ = "tcpHost '" + opt_.tcpHost + "' is not a loopback address (set allowRemote to listen there)";
            return false;
        }
        sockaddr_in addr;
        std::memset(&addr, 0, sizeof addr);
        addr.sin_family = AF_INET;
        addr.sin_port = htons(static_cast<unsigned short>(opt_.tcpPort));
        if (inet_pton(AF_INET, opt_.tcpHost == "localhost" ? "127.0.0.1" : opt_.tcpHost.c_str(), &addr.sin_addr) != 1) {
            error_ = "bad tcpHost '" + opt_.tcpHost + "' (an IPv4 address is needed)";
            return false;
        }
        listen_ = ::socket(AF_INET, SOCK_STREAM, 0);
        if (listen_ == kBadSock) { error_ = "socket() failed"; return false; }
#ifndef _WIN32
        int one = 1;
        setsockopt(listen_, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);
#endif
        if (::bind(listen_, reinterpret_cast<sockaddr*>(&addr), sizeof addr) != 0) {
            error_ = "cannot bind " + opt_.tcpHost + ":" + std::to_string(opt_.tcpPort) + " (error " + std::to_string(LastSockError()) + ")";
            return false;
        }
        if (::listen(listen_, 16) != 0) { error_ = "listen() failed"; return false; }
        sockaddr_in bound;
        std::memset(&bound, 0, sizeof bound);
#ifdef _WIN32
        int len = sizeof bound;
#else
        socklen_t len = sizeof bound;
#endif
        if (::getsockname(listen_, reinterpret_cast<sockaddr*>(&bound), &len) == 0) tcpBoundPort_ = ntohs(bound.sin_port);
        endpoints_.push_back("tcp://" + opt_.tcpHost + ":" + std::to_string(tcpBoundPort_));
        tcpAcceptor_ = std::thread([this] { TcpAcceptLoop(); });
        return true;
    }

    void TcpAcceptLoop() {
        while (!stopping_.load()) {
            fd_set rf;
            FD_ZERO(&rf);
            FD_SET(listen_, &rf);
            timeval tv;
            tv.tv_sec = 0;
            tv.tv_usec = 100000;
            const int r = ::select(static_cast<int>(listen_) + 1, &rf, nullptr, nullptr, &tv);
            ReapConns();
            if (r <= 0) continue;
            const SockT c = ::accept(listen_, nullptr, nullptr);
            if (c == kBadSock) continue;
            AddConn(std::unique_ptr<Stream>(new SockStream(c)));
        }
    }

#ifdef _WIN32
    std::string PipePath() const { return "\\\\.\\pipe\\" + opt_.pipeName; }

    bool StartPipe() {
        pipeFirst_ = CreateNamedPipeA(PipePath().c_str(), PIPE_ACCESS_DUPLEX | FILE_FLAG_FIRST_PIPE_INSTANCE,
                                      PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS,
                                      PIPE_UNLIMITED_INSTANCES, 65536, 65536, 0, nullptr);
        if (pipeFirst_ == INVALID_HANDLE_VALUE) {
            error_ = "cannot create pipe " + PipePath() + " (error " + std::to_string(GetLastError()) + "): is the name already in use?";
            return false;
        }
        endpoints_.push_back("pipe://" + opt_.pipeName);
        pipeAcceptorDone_ = false;
        pipeAcceptor_ = std::thread([this] { PipeAcceptLoop(); pipeAcceptorDone_ = true; });
        return true;
    }

    void PipeAcceptLoop() {
        HANDLE h = pipeFirst_;
        pipeFirst_ = INVALID_HANDLE_VALUE;
        while (!stopping_.load()) {
            if (h == INVALID_HANDLE_VALUE) {
                h = CreateNamedPipeA(PipePath().c_str(), PIPE_ACCESS_DUPLEX,
                                     PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS,
                                     PIPE_UNLIMITED_INSTANCES, 65536, 65536, 0, nullptr);
                if (h == INVALID_HANDLE_VALUE) { Sleep(200); continue; }
            }
            const BOOL c = ConnectNamedPipe(h, nullptr) ? TRUE : (GetLastError() == ERROR_PIPE_CONNECTED);
            if (!c || stopping_.load()) { CloseHandle(h); h = INVALID_HANDLE_VALUE; continue; }
            AddConn(std::unique_ptr<Stream>(new PipeStream(h)));
            h = INVALID_HANDLE_VALUE;
            ReapConns();
        }
        if (h != INVALID_HANDLE_VALUE) CloseHandle(h);
    }

    // ConnectNamedPipe bloqueia, portanto um cliente descartável desperta o aceitador. Tente novamente até ele sair.
    void StopPipeAcceptor() {
        for (int i = 0; i < 400 && !pipeAcceptorDone_.load(); ++i) {
            HANDLE h = CreateFileA(PipePath().c_str(), GENERIC_READ | GENERIC_WRITE, 0, nullptr, OPEN_EXISTING, 0, nullptr);
            if (h != INVALID_HANDLE_VALUE) CloseHandle(h);
            Sleep(5);
        }
        pipeAcceptor_.join();
        if (pipeFirst_ != INVALID_HANDLE_VALUE) { CloseHandle(pipeFirst_); pipeFirst_ = INVALID_HANDLE_VALUE; }
    }
#else
    bool StartPipe() {
        error_ = "named pipes need Windows: use a TCP port";
        return false;
    }
    void StopPipeAcceptor() {}
#endif

    void CloseListeners() {
        if (listen_ != kBadSock) { CloseSock(listen_); listen_ = kBadSock; }
    }

    void AddConn(std::unique_ptr<Stream> s) {
        std::lock_guard<std::mutex> g(connMu_);
        if (conns_.size() >= 64) return;  // o fluxo fecha em seu destrutor
        auto c = std::unique_ptr<Conn>(new Conn());
        c->stream = std::move(s);
        Conn* raw = c.get();
        conns_.push_back(std::move(c));
        raw->th = std::thread([this, raw] { Serve(raw); raw->done = true; });
    }

    void ReapConns() {
        std::list<std::unique_ptr<Conn>> dead;
        {
            std::lock_guard<std::mutex> g(connMu_);
            for (auto it = conns_.begin(); it != conns_.end();) {
                if ((*it)->done.load()) { dead.push_back(std::move(*it)); it = conns_.erase(it); }
                else ++it;
            }
        }
        for (auto& c : dead)
            if (c->th.joinable()) c->th.join();
    }

    void Serve(Conn* c) {
        Stream& s = *c->stream;
        std::string buf;
        char chunk[4096];
        while (!stopping_.load()) {
            const int n = s.Read(chunk, sizeof chunk);
            if (n < 0) break;
            if (n == 0) continue;
            buf.append(chunk, static_cast<size_t>(n));
            size_t nl;
            while ((nl = buf.find('\n')) != std::string::npos) {
                std::string line = buf.substr(0, nl);
                buf.erase(0, nl + 1);
                if (!line.empty() && line.back() == '\r') line.pop_back();
                if (line.empty()) continue;
                std::string out = HandleLine(line);
                out.push_back('\n');
                if (!s.Write(out.data(), out.size())) return;
            }
            if (buf.size() > opt_.maxLineBytes) {
                const std::string out = Reply(json::Value(), false, ErrorObj(errc::kInvalidRequest, "request line too long")) + "\n";
                s.Write(out.data(), out.size());
                return;
            }
        }
    }

    void WriteEndpointFile() {
        if (opt_.endpointFile.empty()) return;
        json::Value v = json::Value::object();
        json::Value eps = json::Value::array();
        for (const auto& e : endpoints_) eps.push(e);
        v.set("protocol", kProtocolVersion).set("game", opt_.game);
#ifdef _WIN32
        v.set("pid", static_cast<uint64_t>(GetCurrentProcessId()));
#else
        v.set("pid", static_cast<uint64_t>(::getpid()));
#endif
        v.set("endpoints", std::move(eps));
        FILE* f = OpenForWrite(opt_.endpointFile);
        if (!f) return;
        const std::string text = v.dump() + "\n";
        std::fwrite(text.data(), 1, text.size(), f);
        std::fclose(f);
    }

    // ------------------------------------------------------------------------------------------ solicitações
    static json::Value ErrorObj(int code, const std::string& message) {
        json::Value e = json::Value::object();
        e.set("code", code).set("message", message);
        return e;
    }

    static FILE* OpenForWrite(const std::string& path) {
#ifdef _MSC_VER
        FILE* f = nullptr;
        if (fopen_s(&f, path.c_str(), "wb") != 0) return nullptr;
        return f;
#else
        return std::fopen(path.c_str(), "wb");
#endif
    }

    static std::string Reply(const json::Value& id, bool ok, json::Value payload) {
        json::Value resp = json::Value::object();
        resp.set("id", id);
        resp.set(ok ? "result" : "error", std::move(payload));
        return resp.dump();
    }

    static bool IsStandard(const std::string& m) {
        static const char* names[] = {"exec", "eval", "waitFor", "state", "save", "load", "screenshot"};
        for (const char* n : names)
            if (m == n) return true;
        return false;
    }

    bool Supported(const std::string& m) const {
        const Capabilities c = adapter_->capabilities();
        if (m == "exec") return c.exec;
        if (m == "eval") return c.eval;
        if (m == "waitFor") return c.eval || c.exec;
        if (m == "state") return c.state;
        if (m == "save") return c.save;
        if (m == "load") return c.load;
        if (m == "screenshot") return c.screenshot;
        return false;
    }

    json::Value PingResult() const {
        json::Value r = json::Value::object();
        const Stats s = stats();
#ifdef _WIN32
        const uint64_t pid = GetCurrentProcessId();
#else
        const uint64_t pid = static_cast<uint64_t>(::getpid());
#endif
        r.set("pong", true).set("protocol", kProtocolVersion).set("game", opt_.game).set("pid", pid)
            .set("frames", s.frames).set("mainLoopAgeMs", s.mainLoopAgeMs).set("ready", ready_.load())
            .set("loadedCount", loaded_.load());
        return r;
    }

    json::Value VersionResult() const {
        json::Value r = json::Value::object();
#ifdef _WIN32
        const uint64_t pid = GetCurrentProcessId();
#else
        const uint64_t pid = static_cast<uint64_t>(::getpid());
#endif
        r.set("protocol", kProtocolVersion).set("game", opt_.game).set("build", opt_.build).set("server", "coopbridge-cpp 1")
            .set("pid", pid);
        return r;
    }

    json::Value MethodsResult() const {
        json::Value arr = json::Value::array();
        for (const char* n : {"ping", "version", "methods", "events"}) arr.push(n);
        for (const char* n : {"exec", "eval", "waitFor", "state", "save", "load", "screenshot"})
            if (Supported(n)) arr.push(n);
        {
            std::lock_guard<std::mutex> g(regMu_);
            for (const auto& kv : methods_) arr.push(kv.first);
        }
        json::Value r = json::Value::object();
        r.set("methods", std::move(arr));
        return r;
    }

    json::Value EventsResult(const json::Value& params) const {
        const uint64_t since = static_cast<uint64_t>(params.get("since").asInt(0));
        size_t limit = static_cast<size_t>(params.get("limit").asInt(0));
        if (limit == 0 || limit > 1000) limit = 1000;
        json::Value arr = json::Value::array();
        uint64_t next = since, dropped = 0, last = 0;
        {
            std::lock_guard<std::mutex> g(evMu_);
            last = lastSeq_;
            if (!events_.empty() && events_.front().seq > since + 1) dropped = events_.front().seq - since - 1;
            size_t n = 0;
            for (const auto& e : events_) {
                if (e.seq <= since) continue;
                if (n++ >= limit) break;
                json::Value v = json::Value::object();
                v.set("seq", e.seq).set("tMs", e.tMs).set("type", e.type).set("data", e.data);
                arr.push(std::move(v));
                next = e.seq;
            }
        }
        json::Value r = json::Value::object();
        r.set("events", std::move(arr)).set("next", next).set("dropped", dropped).set("last", last);
        return r;
    }

    std::string HandleLine(const std::string& line) {
        json::Value req;
        std::string perr;
        if (!json::parse(line, req, perr)) return Reply(json::Value(), false, ErrorObj(errc::kParse, "parse error: " + perr));
        if (!req.isObject()) return Reply(json::Value(), false, ErrorObj(errc::kInvalidRequest, "request must be an object"));
        const json::Value id = req.get("id");
        if (!(id.isNull() || id.isNumber() || id.isString())) return Reply(json::Value(), false, ErrorObj(errc::kInvalidRequest, "id must be a number, a string or null"));
        if (!req.get("method").isString()) return Reply(id, false, ErrorObj(errc::kInvalidRequest, "missing method"));
        const std::string method = req.get("method").asString();
        const json::Value params = req.get("params");
        if (!params.isNull() && !params.isObject()) return Reply(id, false, ErrorObj(errc::kInvalidParams, "params must be an object"));

        // Atendidos na thread de transporte: funcionam enquanto a thread principal está ocupada ou carregando.
        if (method == "ping") return Reply(id, true, PingResult());
        if (method == "version") return Reply(id, true, VersionResult());
        if (method == "methods") return Reply(id, true, MethodsResult());
        if (method == "events") return Reply(id, true, EventsResult(params));

        bool mainThread = true;
        Handler handler;
        if (IsStandard(method)) {
            if (!Supported(method)) return Reply(id, false, ErrorObj(errc::kMethodNotFound, "this game does not support " + method));
        } else {
            Entry e;
            {
                std::lock_guard<std::mutex> g(regMu_);
                auto it = methods_.find(method);
                if (it == methods_.end()) return Reply(id, false, ErrorObj(errc::kMethodNotFound, "unknown method: " + method));
                e = it->second;
            }
            mainThread = e.onMainThread;
            handler = e.fn;
        }
        if (!mainThread) {
            try {
                return Reply(id, true, handler(params));
            } catch (const Error& e) {
                return Reply(id, false, ErrorObj(e.code(), e.what()));
            } catch (const std::exception& e) {
                return Reply(id, false, ErrorObj(errc::kHost, e.what()));
            } catch (...) {
                return Reply(id, false, ErrorObj(errc::kHost, "unknown exception"));
            }
        }

        auto job = std::make_shared<Job>();
        job->method = method;
        job->params = params;
        int timeoutMs = static_cast<int>(params.get("timeoutMs").asInt(opt_.defaultTimeoutMs));
        if (timeoutMs < 0) timeoutMs = 0;
        job->deadlineMs = NowMs() + static_cast<uint64_t>(timeoutMs);
        {
            std::lock_guard<std::mutex> g(qmu_);
            if (inbox_.size() >= opt_.maxPending) {
                rejectedBusy_.fetch_add(1);
                return Reply(id, false, ErrorObj(errc::kBusy, "too many requests are waiting for the main thread"));
            }
            inbox_.push_back(job);
        }
        // O prazo da própria solicitação mais uma tolerância para um Pump() percebê-lo. Se a thread principal não chamar pump
        // (tela de carregamento, travamento), o chamador recebe -32001 em vez de silêncio.
        const uint64_t hardMs = static_cast<uint64_t>(timeoutMs) + static_cast<uint64_t>(opt_.slackMs);
        std::unique_lock<std::mutex> lk(job->mu);
        bool finished = job->cv.wait_for(lk, std::chrono::milliseconds(hardMs), [&] { return job->done; });
        if (!finished) {
            job->abandoned = true;
            return Reply(id, false, ErrorObj(errc::kMainThreadTimeout, "the main thread did not run the request in time (is the game loading?)"));
        }
        if (!job->ok) return Reply(id, false, ErrorObj(job->errCode, job->errMsg));
        return Reply(id, true, job->result);
    }

    // ------------------------------------------------------------------------------------------ lado da thread principal
    template <class F>
    static void RunGuarded(Job& job, F&& fn) {
        try {
            fn();
        } catch (const Error& e) {
            job.FinishErr(e.code(), e.what());
        } catch (const std::exception& e) {
            job.FinishErr(errc::kHost, e.what());
        } catch (...) {
            job.FinishErr(errc::kHost, "unknown exception");
        }
    }

    static bool Compare(const std::string& op, double v, double rhs) {
        if (op == "==") return v == rhs;
        if (op == "!=") return v != rhs;
        if (op == "<") return v < rhs;
        if (op == "<=") return v <= rhs;
        if (op == ">") return v > rhs;
        if (op == ">=") return v >= rhs;
        return v != 0;  // "truthy"
    }
    static bool ValidOp(const std::string& op) {
        return op == "truthy" || op == "==" || op == "!=" || op == "<" || op == "<=" || op == ">" || op == ">=";
    }
    static bool FirstNumber(const std::string& s, double& out) {
        const size_t p = s.find_first_of("0123456789-.");
        if (p == std::string::npos) return false;
        const char* b = s.c_str() + p;
        char* e = nullptr;
        const double d = std::strtod(b, &e);
        if (e == b) return false;
        out = d;
        return true;
    }

    struct WaitState {
        uint64_t startedMs = 0, nextPollMs = 0;
        json::Value last;
        std::string lastError;
    };

    // Uma consulta de waitFor. Verdadeiro quando a condição for satisfeita.
    bool EvaluateWait(const json::Value& p, WaitState& w) {
        const std::string op = p.get("op").asString("truthy");
        const double rhs = p.get("value").asNumber(0);
        const bool hasContains = p.find("contains") != nullptr;
        const std::string contains = p.get("contains").asString();
        const std::string ref = p.get("ref").asString();
        if (p.find("expr") != nullptr) {
            const json::Value v = adapter_->Eval(p.get("expr").asString(), ref);
            w.last = v;
            if (hasContains) return (v.isString() ? v.str() : v.dump()).find(contains) != std::string::npos;
            if (!v.isNumber() && !v.isBool()) return false;
            return Compare(op, v.asNumber(), rhs);
        }
        const ExecResult r = adapter_->Exec(p.get("cmd").asString(), ref);
        w.last = json::Value(r.output);
        if (hasContains) return r.output.find(contains) != std::string::npos;
        double d = 0;
        if (!FirstNumber(r.output, d)) return false;
        w.last = json::Value(d);
        return Compare(op, d, rhs);
    }

    bool StepWait(Job& job, WaitState& w) {
        const uint64_t now = NowMs();
        const int pollMs = static_cast<int>(job.params.get("pollMs").asInt(100));
        if (now >= w.nextPollMs) {
            bool satisfied = false;
            try {
                satisfied = EvaluateWait(job.params, w);
                w.lastError.clear();
            } catch (const std::exception& e) {
                w.lastError = e.what();  // uma consulta que falha (jogo carregando) não encerra a espera
            }
            if (satisfied) {
                json::Value r = json::Value::object();
                r.set("satisfied", true).set("timedOut", false).set("value", w.last).set("elapsedMs", now - w.startedMs);
                job.FinishOk(std::move(r));
                return true;
            }
            w.nextPollMs = now + static_cast<uint64_t>(pollMs < 1 ? 1 : pollMs);
        }
        if (now >= job.deadlineMs) {
            json::Value r = json::Value::object();
            r.set("satisfied", false).set("timedOut", true).set("value", w.last).set("elapsedMs", now - w.startedMs);
            if (!w.lastError.empty()) r.set("lastError", w.lastError);
            job.FinishOk(std::move(r));
            return true;
        }
        return false;
    }

    void Dispatch(const std::shared_ptr<Job>& jobp) {
        Job& job = *jobp;
        const json::Value& p = job.params;
        const std::string& m = job.method;
        auto str = [&](const char* key) -> const std::string* {
            const json::Value* v = p.find(key);
            return (v && v->isString()) ? &v->str() : nullptr;
        };
        RunGuarded(job, [&] {
            if (m == "exec") {
                const std::string* cmd = str("cmd");
                if (!cmd) throw Error(errc::kInvalidParams, "exec requires string param 'cmd'");
                const ExecResult r = adapter_->Exec(*cmd, p.get("ref").asString());
                json::Value out = json::Value::object();
                out.set("ok", r.ok).set("output", r.output);
                job.FinishOk(std::move(out));
            } else if (m == "eval") {
                const std::string* expr = str("expr");
                if (!expr) throw Error(errc::kInvalidParams, "eval requires string param 'expr'");
                json::Value out = json::Value::object();
                out.set("value", adapter_->Eval(*expr, p.get("ref").asString()));
                job.FinishOk(std::move(out));
            } else if (m == "state") {
                std::vector<std::string> sections;
                const json::Value& s = p.get("sections");
                if (s.isString()) sections.push_back(s.str());
                else if (s.isArray())
                    for (const auto& it : s.items()) sections.push_back(it.asString());
                const json::Value v = adapter_->State(sections);
                if (const std::string* path = str("path")) {  // um dump grande vai para um arquivo
                    const std::string text = v.dump();
                    FILE* f = OpenForWrite(*path);
                    if (!f) throw Error(errc::kHost, "cannot open " + *path);
                    std::fwrite(text.data(), 1, text.size(), f);
                    std::fclose(f);
                    json::Value out = json::Value::object();
                    out.set("path", *path).set("bytes", static_cast<uint64_t>(text.size()));
                    job.FinishOk(std::move(out));
                } else {
                    job.FinishOk(v);
                }
            } else if (m == "waitFor") {
                if (!str("expr") && !str("cmd")) throw Error(errc::kInvalidParams, "waitFor requires string param 'expr' or 'cmd'");
                if (!ValidOp(p.get("op").asString("truthy"))) throw Error(errc::kInvalidParams, "waitFor: bad 'op'");
                WaitState w;
                w.startedMs = NowMs();
                job.step = [this, w](Job& j) mutable { return StepWait(j, w); };
                if (!job.step(job)) pending_.push_back(jobp);
            } else if (m == "load") {
                const std::string* name = str("name");
                if (!name || name->empty()) throw Error(errc::kInvalidParams, "load requires string param 'name'");
                const uint64_t before = loaded_.load();
                adapter_->Load(*name);
                const std::string saveName = *name;
                job.step = [this, before, saveName](Job& j) {
                    if (loaded_.load() > before) {
                        json::Value r = json::Value::object();
                        r.set("loaded", true).set("name", saveName);
                        j.FinishOk(std::move(r));
                        return true;
                    }
                    if (NowMs() >= j.deadlineMs) { j.FinishErr(errc::kTimeout, "timed out waiting for the game to finish loading"); return true; }
                    return false;
                };
                pending_.push_back(jobp);
            } else if (m == "save") {
                const std::string* name = str("name");
                if (!name || name->empty()) throw Error(errc::kInvalidParams, "save requires string param 'name'");
                const uint64_t before = saved_.load();
                adapter_->Save(*name, p.get("overwrite").asBool(false));
                job.step = [this, before](Job& j) {
                    if (saved_.load() > before) {
                        std::string path;
                        { std::lock_guard<std::mutex> g(saveMu_); path = lastSavedPath_; }
                        json::Value r = json::Value::object();
                        r.set("saved", true).set("path", path);
                        j.FinishOk(std::move(r));
                        return true;
                    }
                    if (NowMs() >= j.deadlineMs) { j.FinishErr(errc::kTimeout, "timed out waiting for the game to finish saving"); return true; }
                    return false;
                };
                pending_.push_back(jobp);
            } else if (m == "screenshot") {
                const std::string path = adapter_->Screenshot(p.get("path").asString());
                json::Value out = json::Value::object();
                out.set("ok", true).set("path", path);
                job.FinishOk(std::move(out));
            } else {
                Handler fn;
                {
                    std::lock_guard<std::mutex> g(regMu_);
                    auto it = methods_.find(m);
                    if (it == methods_.end()) throw Error(errc::kMethodNotFound, "unknown method: " + m);
                    fn = it->second.fn;
                }
                job.FinishOk(fn(p));
            }
        });
    }

    // ------------------------------------------------------------------------------------------ estado
    Options opt_;
    Adapter* adapter_ = nullptr;
    std::string error_;
    std::vector<std::string> endpoints_;
    std::atomic<bool> stopping_{false};
    bool running_ = false;
    uint64_t startMs_ = 0;

    SockT listen_ = kBadSock;
    int tcpBoundPort_ = 0;
    std::thread tcpAcceptor_;
    std::thread pipeAcceptor_;
    std::atomic<bool> pipeAcceptorDone_{true};
#ifdef _WIN32
    HANDLE pipeFirst_ = INVALID_HANDLE_VALUE;
    bool wsaStarted_ = false;
#endif

    std::mutex connMu_;
    std::list<std::unique_ptr<Conn>> conns_;

    std::mutex qmu_;
    std::deque<std::shared_ptr<Job>> inbox_;
    std::list<std::shared_ptr<Job>> pending_;   // apenas thread principal

    mutable std::mutex regMu_;
    std::map<std::string, Entry> methods_;

    mutable std::mutex evMu_;
    std::deque<Event> events_;
    uint64_t lastSeq_ = 0;

    std::atomic<uint64_t> frames_{0}, served_{0}, maxDrained_{0}, rejectedBusy_{0}, lastPumpMs_{0};
    std::atomic<size_t> pumpThread_{0};
    std::atomic<uint64_t> loaded_{0}, saved_{0};
    std::mutex saveMu_;
    std::string lastSavedPath_;
    std::atomic<bool> ready_{false};
};

}  // namespace coopbridge
