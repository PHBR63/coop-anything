# <a id="network-chaos-testing-make-the-link-bad-on-purpose"></a>Testes de caos de rede: prejudique o enlace de propósito

Sincronização cooperativa que funciona em LAN frequentemente falha na internet. Esta página mostra como testar isso com redes ruins reproduzíveis, em simulador e entre cópias reais do jogo. A ferramenta fica em [tools/chaos/](../tools/chaos/README.md). Funciona com qualquer jogo ou mod UDP.

Leia primeiro [networking.md](networking.md) sobre modelos de sincronização e transportes, e [automated-qa.md](automated-qa.md) para a estrutura geral dos testes. Esta página cobre a parte do enlace degradado.

## <a id="1-what-a-bad-link-does-to-a-co-op-mod"></a>1. O que um enlace ruim faz a um mod cooperativo

| Problema do enlace | O que falha na camada de sincronização | O que uma boa camada faz |
|---|---|---|
| Perda de pacotes | Uma atualização nunca chega, e as cópias diferem para sempre | Confirma recebimento e reenvia, ou detecta a lacuna e corrige. |
| Perda em rajadas | Várias atualizações seguidas desaparecem; um reenvio só não basta | Reenvia com espera progressiva e corrige comparando estados. |
| Reordenação | Atualização 7 chega antes da 6. Aplicar na ordem de chegada produz estado final errado | Numera toda atualização, armazena lacunas em buffer e aplica na ordem correta. |
| Duplicatas | O mesmo "dar 100 tampinhas" se aplica duas vezes | Torna toda atualização idempotente ou elimina duplicatas por ID. |
| Corrupção | Dados inválidos são aplicados como estado real | Confere checksum de cada mensagem e descarta o que falha. |
| Variação de latência | Jogadores e atores remotos se movem aos trancos; tempos de espera estouram cedo | Buffer de interpolação, limites de espera maiores que a pior variação. |
| Enlace de baixa capacidade | Recuperação grande (entrada tardia, retorno) satura o enlace e impede atualizações ao vivo | Divide em blocos, controla o ritmo e prioriza tráfego ao vivo. |
| Interrupção em um sentido | Cliente escuta o host, mas não consegue falar, ou o contrário | Repete solicitações; não executa duas vezes quando a repetição enfim chega. |
| Desconexão completa | Cliente some por alguns segundos e retorna com estado antigo | Retoma da última atualização confirmada ou envia nova referência inicial. |

A maioria desses bugs não aparece com duas cópias em um PC, porque loopback é perfeito. Degradar o enlace é a única maneira de vê-los antes dos seus amigos.

## <a id="2-three-layers-of-tooling"></a>2. Três camadas de ferramentas

| Camada | Ferramenta | Adequada para | Não adequada para |
|---|---|---|---|
| No motor ou biblioteca | Unreal `NetEmulation`, simulação LiteNetLib, netem no Linux (consulte [networking.md](networking.md#5-testing-netcode)) | Verificações rápidas quando o motor oferece controle | Sementes reproduzíveis, log de pacotes, interrupções programadas em etapas exatas. |
| Sistema inteiro | [clumsy](https://github.com/jagt/clumsy) no Windows | Uma primeira inspeção manual, sem alterar código | Repetir exatamente o mesmo azar, controlar por script de teste. |
| Simulador de caos deste repositório | `tools/chaos` | Perturbações com semente, controle por script e logs entre cópias reais, e o mesmo modelo dentro de simulador | Jogos TCP (somente UDP). |

Use o simulador de caos quando um teste precisar rodar sem interação e falhar da mesma maneira duas vezes.

## <a id="3-the-recommended-order"></a>3. A ordem recomendada

1. **Primeiro o simulador.** Se houver núcleo de sincronização independente do jogo, execute-o pela versão equivalente em C++ (`tools/chaos/cpp/impair.h`) com muitas sementes. É rápido, sem sockets, tempo real ou necessidade do jogo. Um fuzzer sobre essa base é descrito em [fuzzing-coop-sync.md](fuzzing-coop-sync.md).
2. **Cópias reais pelo retransmissor.** Quando a camada sobreviver ao simulador, coloque o retransmissor entre duas cópias reais e execute seu cenário normal com `bad_wifi`, depois `hell`.
3. **Interrupções em etapas escolhidas.** Corte um ou ambos os sentidos no meio do cenário, restaure e verifique se as cópias convergem.
4. **Guarde as sementes que falham.** Cada falha vira um teste de regressão com perfil, semente e etapa do cenário registrados.

Como retransmissor e versão C++ compartilham um fluxo aleatório, "perfil X, semente N" produz os mesmos descartes e atrasos em ambos. Uma falha encontrada no simulador pode ser repetida em cópias reais e vice-versa.

## <a id="4-choosing-profiles"></a>4. Escolhendo perfis

São distribuídos seis, todos em `profiles.json`. Os atrasos são por sentido.

| Perfil | Em termos simples | Execute para descobrir |
|---|---|---|
| `lan` | Quase perfeito | Sua referência. Qualquer falha aqui não é um bug de rede. |
| `good_wifi` | 12 ms, 0,5% de perda | Se o caso normal continua funcionando. |
| `bad_wifi` | 35 ms +/- 25, 2% de perda com rajadas, um pouco de reordenação e duplicação | Principal detector de bugs. Execute todos os cenários com ele. |
| `mobile_tether` | 70 ms, limite de 2 Mbit/s | Tráfego de recuperação e comportamento da fila. |
| `transatlantic` | 90 ms, sem perturbações | Limites de espera e tudo que pressupôs baixa latência. |
| `hell` | 200 ms +/- 150, 8% de perda, 10% de reordenação, 5% de duplicatas, 512 kbit/s | Estresse. Passar aqui indica robustez. |

Adicione seus próprios perfis editando `profiles.json` e executando `python -I tools/chaos/gen_header.py --write`. Os testes verificam depois se a versão C++ continua equivalente.

## <a id="5-a-scenario-template"></a>5. Modelo de cenário

1. Inicie o host e depois o retransmissor à sua frente (`chaos.py relay --target ... --info-file info.json`).
2. Inicie o cliente conectado à porta de escuta do retransmissor.
3. Verifique primeiro o modo: dois jogadores conectados e `stats` do retransmissor mostrando pacotes nos dois sentidos. Um cenário que silenciosamente voltou para um jogador não comprova nada.
4. Defina um perfil: `client.set_profile("info.json", "bad_wifi")`.
5. Execute a ação testada pelo mesmo caminho usado por uma pessoa: concluir etapa de missão, coletar item, abrir porta, alterar objeto.
6. Interrupção opcional: `client.partition("info.json", "s2c", seconds=3)` enquanto o cliente age; depois aguarde a restauração.
7. **Termine o caos e espere estabilizar.** Mude para `lan` (ou chame `reconnect`), aguarde tempo suficiente para a camada reenviar e corrigir (uma janela fixa mais a verificação de que o número da última atualização do host coincide com o confirmado pelo cliente é melhor que apenas esperar um tempo).
8. Compare o estado das duas cópias (captura e diferenças; consulte [desync-hunting.md](desync-hunting.md)).
9. Verifique se o caos realmente ocorreu: `stats` do retransmissor mostra descartes e, nos perfis pertinentes, duplicatas. Uma "aprovação" em um perfil que não descartou nada é vazia.

## <a id="6-what-to-assert"></a>6. O que verificar

- **Convergência.** Depois de terminar o caos e estabilizar o sistema, as duas cópias têm o mesmo estado compartilhado.
- **Sem aplicação dupla.** Recompensas, criações de objetos e contadores mudaram uma vez, não duas.
- **Estado obsoleto não prevalece.** Atualização antiga que chega atrasada não sobrescreve uma nova.
- **Solicitações executadas exatamente uma vez.** Ação enviada duas vezes por repetição do cliente roda uma única vez no host.
- **Correção limitada.** O número de reparos por minuto sob `bad_wifi` permanece pequeno e é zero em `lan`. Reparos indicam que a primeira linha de defesa deixou passar algo. Registre-os e trate o crescimento da contagem como bug.
- **Tempo de recuperação.** Após interrupção de 5 s, as cópias voltam a sincronizar em um número de segundos previamente registrado.

Não faça asserções sobre o instante exato de pacotes individuais. Verifique estado final e contagens, com tolerâncias.

## <a id="7-making-failures-repeatable"></a>7. Tornando falhas reproduzíveis

- Fixe a semente do perfil no teste (`--seed N` ou `set_profile` com `seed`). Exiba-a no início do log.
- Use `--log` para obter um log de pacotes. Ele registra todo datagrama com o veredito (encaminhado ou descartado e por quê). Compare seus primeiros bytes e ordem com seus próprios registros para descobrir em qual datagrama começou a dessincronização.
- Se a execução só oscila sob caos, repita com a mesma semente. Se a falha se repetir, é um bug de sincronização. Caso contrário, outro fator (tempo real, carga do jogo) está envolvido; informe isso no relato.
- A variação de tempo real no retransmissor é pequena, mas existe. O simulador usa tempo virtual e é exatamente reproduzível. Prefira-o quando precisar de repetição idêntica bit a bit.

## <a id="8-pitfalls"></a>8. Armadilhas

- **Latências se somam.** O atraso do retransmissor é por sentido e se acrescenta ao atraso real. 35 ms em cada sentido significam cerca de 70 ms de ida e volta.
- **Os limites de espera do jogo fazem parte do teste.** Sob `hell`, o tempo limite de conexão do jogo pode estourar. Decida se é resultado esperado ("cliente é desconectado após 10 s de interrupção") e verifique-o, em vez de suavizar o perfil.
- **Pacotes criptografados ou assinados.** Nesse caso, `corrupt` faz o receptor descartar o pacote, um teste válido do caminho de descarte. Só testa seu checksum se ele for seu.
- **Retransmissão Steam ou jogos por túnel.** Coloque o simulador entre as extremidades locais do túnel, em loopback, não no trecho Steam. Consulte [networking-steam-spacewar.md](networking-steam-spacewar.md).
- **Uma porta de cliente.** Um cliente que muda a porta de origem parece um novo participante.
- **Portas.** Use um retransmissor por host, com portas próprias, por agente paralelo, para evitar conflitos.
- **Não distribua o simulador dentro do jogo.** É uma ferramenta de testes.

## <a id="9-test-the-box-itself"></a>9. Teste o próprio simulador

Uma ferramenta de caos que silenciosamente não faz nada faria todos os testes passarem. `tools/chaos/run_tests.py` verifica isso: estatísticas do modelo por perfil, idas e voltas UDP reais e um conjunto de variantes de mutação (cada uma quebra um comportamento de propósito, como "sem perda" ou "partição ignorada", e um teste precisa falhar). Execute após qualquer alteração no simulador:

```
python -I tools/chaos/run_tests.py
```

Exibe `ALL OK` somente quando tudo passa e todos os mutantes são detectados.

## <a id="10-what-to-put-in-your-games-qa-section"></a>10. O que colocar na seção QA do jogo

- Perfis executados, com sementes.
- Testes de interrupção (sentido, duração e tempo de recuperação).
- Asserções da seção 6 e o comando que as executa.
- Pendências (por exemplo, um jogo que não pôde ser direcionado ao retransmissor) ficam em uma issue GitHub, não no relato técnico.

## <a id="sources-and-credits"></a>Fontes e créditos

- [Gaffer on Games](https://gafferongames.com/): os artigos de rede sobre capturas de estado, sincronização e confiabilidade são a melhor introdução ao motivo desses problemas.
- [clumsy](https://github.com/jagt/clumsy) (Windows) e `tc netem` do Linux para perturbações no nível do sistema.
- O modelo de dois estados Gilbert-Elliott é a abordagem clássica para produzir perda em rajadas.
