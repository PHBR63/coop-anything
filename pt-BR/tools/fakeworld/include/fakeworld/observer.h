// Hook para gravador de eventos e oráculos de teste. Toda função de retorno tem um corpo padrão sem efeito.
#pragma once
#include <cstdint>
#include "fakeworld/effect.h"
#include "fakeworld/messages.h"
#include "fakeworld/types.h"
#include "coop/ownership.h"

namespace coop::fakeworld {

struct IEngineObserver {
    virtual ~IEngineObserver() = default;
    // Mensagem da aplicação (Envelope codificado) saindo de ou chegando à máquina `self`. channel: 0 confiável, 1 não confiável.
    virtual void onSend(PlayerId /*self*/, uint64_t /*nowMs*/, PeerId /*to*/, uint8_t /*channel*/, const Bytes& /*envelope*/) {}
    virtual void onRecv(PlayerId /*self*/, uint64_t /*nowMs*/, PeerId /*from*/, uint8_t /*channel*/, const Bytes& /*envelope*/) {}
    // Uma mensagem foi descartada antes de chegar à aplicação (crc inválido, sessão obsoleta, impossível de decodificar).
    virtual void onDrop(PlayerId /*self*/, uint64_t /*nowMs*/, PeerId /*from*/, const char* /*reason*/) {}
    // Uma mensagem de responsabilidade foi aplicada à visão desta máquina (host: também quando a emite).
    virtual void onOwnership(PlayerId /*self*/, uint64_t /*nowMs*/, const OwnMsg& /*m*/, ApplyResult /*r*/) {}
    // Uma atualização de ator foi avaliada pela verificação de época/responsável.
    virtual void onActorUpdate(PlayerId /*self*/, uint64_t /*nowMs*/, NetId /*id*/, PlayerId /*from*/, OwnerEpoch /*epoch*/, UpdateVerdict /*v*/) {}
    // Um efeito de história foi aplicado ao mundo local (host: no commit; clientes: no recebimento).
    virtual void onEffectApplied(PlayerId /*self*/, uint64_t /*nowMs*/, uint64_t /*txnSeq*/, const Effect& /*e*/) {}
    // Resumo periódico de estado (tempo monotônico, por categoria).
    virtual void onDigest(PlayerId /*self*/, uint64_t /*nowMs*/, Category /*cat*/, uint64_t /*hash*/) {}
    // Uma ação local de jogador/host entrou na máquina (fluxo de entrada reproduzível).
    virtual void onAction(PlayerId /*self*/, uint64_t /*nowMs*/, const Action& /*i*/) {}
    // Uma divergência de resumo foi reparada (lado do host): quais chaves diferiam.
    virtual void onRepair(PlayerId /*self*/, uint64_t /*nowMs*/, PlayerId /*target*/, Category /*cat*/, size_t /*keys*/) {}
};

}  // namespace coop::fakeworld
