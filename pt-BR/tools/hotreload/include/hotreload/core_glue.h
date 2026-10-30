// O lado do núcleo em um recarregamento, em duas chamadas. Vincule a biblioteca estática `hotreload_core` à DLL do núcleo.
//
//   int Init() {                       // HrCoreApi::init
//       ... iniciar threads, instalar ganchos, registrar métodos ...
//       return hotreload::AfterLoad(g_api) ? 1 : 0;        // restaura o estado salvo (ou começa do zero)
//   }
//   int BeforeUnload() { return hotreload::BeforeUnload(g_api) ? 1 : 0; }   // HrCoreApi::before_unload
//
// BeforeUnload faz, nesta ordem: verifica e salva cada participante, drena (espera até que nenhuma thread além das pertencentes ao
// núcleo executa código dele), desliga todos os participantes, verifica sondagens de vazamento e entrega o bloco de estado ao carregador.
// Retorna false para recusar. Uma recusa antes do desligamento deixa o núcleo funcionando integralmente, então o carregador o mantém.
#pragma once
#include <functional>
#include <string>
#include <vector>

#include "hotreload/abi.h"
#include "hotreload/reload_drain.h"
#include "hotreload/reload_state.h"

namespace hotreload {

// Para mods que alteram código do motor: a integração não conhece seus ganchos. Defina-os uma vez para a drenagem considerá-los.
struct DrainHooks {
    // Restaura o código original para que nenhuma thread possa mais entrar em um desvio (os trampolins permanecem alocados).
    // Retorna quantos ganchos não puderam ser removidos (0 = todos removidos). Chamado logo antes da drenagem.
    std::function<int()> suspend;
    // Chamado quando a drenagem recusa: reinstala os ganchos para o núcleo continuar funcionando.
    std::function<void()> resume;
    // Adicione os intervalos de endereços de seus trampolins e código gerado, para uma thread neles contar como ocupada.
    std::function<void(std::vector<CodeRange>&)> extraRanges;
};
void SetDrainHooks(DrainHooks hooks);

// Núcleo antigo: veja a sequência acima. `api` é o HrLoaderApi recebido pelo núcleo.
bool BeforeUnload(const HrLoaderApi* api);
// Núcleo novo: chame ao final de init. Num recarregamento a quente, lê o bloco salvo pelo núcleo anterior e restaura cada
// participante. Também registra o método de controle `reload.state`.
bool AfterLoad(const HrLoaderApi* api);

// O JSON retornado por `reload.state`: participantes e versões, threads ativas e o que o último salvamento, drenagem,
// desligamento ou restauração informaram (notes, failures, leaks, restored, fresh, migrated, dropped, drain).
std::string StatusJson();

}  // namespace hotreload
