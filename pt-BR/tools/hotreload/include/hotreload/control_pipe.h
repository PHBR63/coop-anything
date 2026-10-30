// Um pequeno canal de controle: um pipe nomeado do Windows que comunica um objeto JSON por linha.
//
//   request : {"id":1,"method":"dev.status","params":{}}\n
//   reply   : {"id":1,"result":{...}}\n          or          {"id":1,"error":{"code":-32601,"message":"..."}}\n
//
// Um cliente por vez. O pipe é atendido em sua própria thread, mas todo método exceto `ping` executa na SUA thread: seu
// laço principal chama Pump() uma vez por quadro, permitindo acessar o estado sem bloqueios e recarregar entre
// quadros. `ping` é respondido na thread do pipe ({"pid":<ID do processo>}), para distinguir "o jogo está ativo, mas seu laço principal
// está travado" de "sem jogo".
//
// Códigos de erro: -32601 método desconhecido, -32000 falha do método, -32001 o laço principal não executou a solicitação a tempo.
// Params pode conter "timeoutMs" (padrão 30000): quanto a thread do pipe espera pelo laço principal.
//
// A biblioteca estática `hotreload_control` não tem outra dependência, então um host pode usá-la sozinha.
#pragma once
#include <condition_variable>
#include <deque>
#include <functional>
#include <memory>
#include <mutex>
#include <string>
#include <thread>

namespace hotreload {

// ---- pequenos utilitários JSON (buscas planas em um objeto; suficientes para o protocolo de controle) ----
std::string JsonEscape(const std::string& s);
// O texto bruto do valor de uma chave de nível superior do objeto JSON `obj`. False se obj não for um objeto ou não tiver essa chave.
bool JsonFindValue(const std::string& obj, const std::string& key, std::string& raw);
bool JsonGetString(const std::string& obj, const std::string& key, std::string& out);   // sem escape
bool JsonGetInt(const std::string& obj, const std::string& key, long long& out);

class ControlServer {
public:
    // Executa na thread que chama Pump(). Retorna true com JSON em `out`, ou false com uma mensagem em `out` (e um código,
    // padrão -32000; defina -32601 para método desconhecido).
    using Handler = std::function<bool(const std::string& method, const std::string& params, std::string& out, int& code)>;

    // pipeName: um nome curto ("mygame-1") ou um caminho completo \.\pipe\name.
    ControlServer(std::string pipeName, Handler handler);
    ~ControlServer();
    ControlServer(const ControlServer&) = delete;
    ControlServer& operator=(const ControlServer&) = delete;

    // Cria o pipe e inicia a thread de atendimento. False (com o motivo) se o nome estiver ocupado ou não puder ser criado.
    bool Start(std::string& err);
    void Stop();
    // Thread principal: executa as solicitações enfileiradas. Retorna quantas foram executadas.
    int Pump();
    const std::string& path() const { return path_; }

private:
    struct Req {
        std::string method, params;
        bool running = false, abandoned = false, done = false, ok = false;
        std::string out;
        int code = -32000;
    };
    void Run();
    void Serve(void* pipe, void* ev, void* stop);
    bool WriteAll(void* pipe, void* ev, void* stop, const std::string& data);
    std::string Handle(const std::string& line);

    std::string path_;
    Handler handler_;
    void* pipe_ = nullptr;
    void* stopEv_ = nullptr;
    std::thread thread_;
    std::mutex mu_;
    std::condition_variable cv_;
    std::deque<std::shared_ptr<Req>> queue_;
    bool stopping_ = false;
};

}  // namespace hotreload
