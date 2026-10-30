# <a id="example-the-chaos-box-on-a-fallout-new-vegas-co-op-project"></a>Exemplo: o simulador de caos em um projeto cooperativo de Fallout: New Vegas

Este simulador foi escrito para [fnv-coop](https://github.com/cranebeaker/fnv-coop), um mod cooperativo com história compartilhada para Fallout: New Vegas. Esta página lista as partes específicas daquele projeto, para mostrar como um jogo se integra. Nada aqui é necessário para usar o simulador com outro jogo.

## <a id="how-it-plugged-in"></a>Como foi integrado

- A camada de sessão do mod se comunica por ENet (UDP) em estrela: um host e até alguns clientes. O retransmissor fica entre um cliente e o host, exatamente como no README principal: o host escuta em sua porta, o retransmissor escuta em outra, e o cliente recebe a instrução de conectar à porta do retransmissor.
- O simulador de testes do mod, que funciona sem o jogo, tem seu próprio enlace simulado. Seus parâmetros incluíam apenas intervalo de latência, perda, duplicação e corrupção. O mapeamento usado para fornecer ao simulador um perfil de `profiles.json`:

  | Campo do simulador | Origem no perfil |
  |---|---|
  | latência mínima | `latency_ms - jitter_ms` (nunca abaixo de 0) |
  | latência máxima | `latency_ms + jitter_ms` |
  | perda, duplicação, corrupção | mesmos nomes |

  Perda em rajadas, reordenação e limites de largura de banda não faziam parte daquele tipo de enlace. Por isso existe a versão equivalente em C++ apenas com cabeçalho (`cpp/impair.h`): um simulador pode chamar `Impairment::decide` para cada datagrama e obter todos esses efeitos, com os mesmos resultados do retransmissor real para a mesma semente.
- Os scripts de teste para duas cópias do jogo devem iniciar o retransmissor com `--info-file`, ler a porta de controle desse arquivo com `client.py` e mudar o perfil ou interromper um sentido da comunicação em etapas escolhidas de um cenário (por exemplo, `client.partition(info, "s2c", seconds=3)` no meio de uma verificação de sincronização de missão e, depois, verificar se ambas as cópias convergem quando a interrupção termina).
- O formato do log de pacotes (`head`, `len`, ordem) foi projetado para permitir alinhamento com os registros do gravador de eventos do próprio mod, comparando bytes e ordem em vez de números de quadro.

## <a id="what-the-session-layer-had-to-survive"></a>O que a camada de sessão precisava suportar

Os perfis foram escolhidos para atingir os modos de falha de um protocolo de sincronização de história:

| Falha | Perfil ou chamada | O que verifica |
|---|---|---|
| Atualizações perdidas | `bad_wifi`, `hell` | Retransmissão e confirmação de recebimento do registro de efeitos. |
| Atualizações fora de ordem | `bad_wifi` (reordenação de 2%), `hell` (10%) | Lacunas são armazenadas em buffer e aplicadas na ordem correta. |
| Atualizações duplicadas | `bad_wifi`, `hell` | Nada é aplicado duas vezes (sem recompensas duplicadas). |
| Enlace lento e de pouca capacidade | `mobile_tether`, `hell` | Recuperação após uma lacuna sem saturar o enlace. |
| Interrupção do host para o cliente | `partition {"dir":"s2c","on":true,"duration_ms":N}` | O cliente fica para trás e depois recupera o atraso. |
| Interrupção do cliente para o host | `partition {"dir":"c2s", ...}` | As solicitações do cliente são duráveis, repetidas e executadas uma única vez. |
| Interrupção dos dois sentidos | `disconnect {"duration_ms":N}` | Reconexão e retomada ou estabelecimento de uma nova base. |

## <a id="what-is-not-covered"></a>O que não é coberto

- O comportamento do jogo real através do retransmissor (tempo de conexão do ENet, limites de espera com um perfil específico) exige uma execução com duas cópias do jogo. O simulador de caos não inicia jogos; isso cabe ao executor de testes do próprio jogo.
- O retransmissor e o simulador compartilham o modelo de perturbação, mas não o relógio: o retransmissor usa tempo real, e o simulador usa tempo virtual.
