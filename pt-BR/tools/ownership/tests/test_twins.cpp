// Variantes de mutação. Cada variante ativa uma classe conhecida de bug (indicador OwnershipFaults) e executa o cenário que a cobre
// esse comportamento. O cenário precisa passar sem a falha e relatar uma violação com ela. Se uma variante passar enquanto o
// cenário também passar sob a falha, ele não detectaria aquele bug e a variante reprova.
#include <string>
#include "minitest.h"
#include "scenarios.h"

using namespace coop;
using namespace coop::testing;

#define OWN_TWIN(name, flag, scenario)                                                                    \
    TEST(twin, name) {                                                                                    \
        CHECK_MSG((scenario), "the scenario must pass without the fault");                                \
        OwnershipFaults f; f.flag = true;                                                                 \
        { OwnershipFaultScope s(f); CHECK_MSG(!(scenario), "the scenario did not catch the fault " #flag); } \
    }

OWN_TWIN(own_no_epoch, noEpochBump, churnHolds(1, 400))
OWN_TWIN(own_stale_epoch, acceptStaleEpoch, staleEchoRejected())
OWN_TWIN(own_adopt_echo, adoptEcho, staleEchoRejected())
OWN_TWIN(own_transfer_no_ack, transferNoAck, handoffKeepsLastState())
OWN_TWIN(own_no_hysteresis, noHysteresis, noFlap())
OWN_TWIN(own_follower_ignored, followerIgnored, followerStaysWithRecruiter())
OWN_TWIN(own_accept_non_owner, acceptNonOwner, churnHolds(1, 400))
