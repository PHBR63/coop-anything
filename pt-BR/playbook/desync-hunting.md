# <a id="desync-hunting-with-traces-and-shrinking"></a>Busca de dessincronizações com registros e redução de casos

Uma dessincronização ocorre quando duas máquinas discordam sobre o mundo compartilhado. Examinar dois arquivos de log é uma forma lenta de descobrir o primeiro momento da divergência. Esta página transforma isso em um ciclo curto e reproduzível: **registrar, encontrar a primeira divergência, localizar a chave e o valor, reduzir a execução que falha e guardá-la como teste.** As ferramentas ficam em [tools/flight](../tools/flight/README.md) e servem para qualquer jogo; as ideias também valem se você escrever suas próprias ferramentas.

## <a id="the-loop"></a>O ciclo

1. **Registre** em todas as máquinas, o tempo todo, em um buffer circular que custa cerca de um microssegundo por evento.
2. **Extraia o registro** quando sua verificação detectar dessincronização (e em falhas e sob solicitação).
3. **Encontre a primeira divergência** entre os registros de 2 a 4 máquinas.
4. **Refine a localização** do resumo para o agrupamento, a chave e o valor, com as mensagens que levaram até ali.
5. **Reproduza** na estrutura de testes e **reduza** a execução às poucas etapas relevantes.
6. **Preserve** como teste de regressão que falha até o bug ser corrigido.
7. **Verifique que as ferramentas conseguem falhar:** quebre algo de propósito e veja se os testes detectam.

## <a id="1-record-the-right-things"></a>1. Registre as informações certas

Registre o que alguém depurando pediria, sem comprometer os quadros:

- **Todo datagrama de entrada e saída**, como bytes, com par e canal. Decodifique depois, na extração, nunca no caminho crítico.
- **Todo efeito aplicado ao mundo local**, com hash do conteúdo, número da transação (`seq`) e índice. O mesmo efeito precisa ter o mesmo hash em todas as máquinas.
- **Toda decisão do host** (seus commits), com hash.
- **Mudanças de responsabilidade** (quem controla qual ator, em qual época).
- **Resumos** do estado compartilhado a cada poucos segundos, em um ponto estável, com época e seq para comparar as máquinas no mesmo momento.
- **Marcadores** de entradas, salvamentos, carregamentos e qualquer outra coisa que deva aparecer na cadeia.

Torne os hashes **estáveis**: calcule sobre o conteúdo do efeito, não ponteiros ou endereços; percorra mapas em ordem classificada; calcule hashes de números de ponto flutuante pelos bits. Um hash diferente entre duas máquinas saudáveis produz falsas dessincronizações, e cada uma custa uma hora.

Defina um **limite de custo adicional e teste-o.** A medição de desempenho dos testes do gravador falha se um quadro custar mais de 100 microssegundos.

## <a id="2-digests-that-point-at-the-bug"></a>2. Resumos que apontam para o bug

Um hash único de todo o estado informa que existe dessincronização, mas não onde. Um **resumo por agrupamentos** é melhor: calcule o hash de cada entrada como (chave, hash do valor), some as entradas em 256 agrupamentos por `key mod 256` e armazene as 256 somas. A soma independe da ordem, uma mudança de valor altera exatamente um agrupamento e o resumo pode ser atualizado uma entrada por vez (`BucketedState`), sem percorrer o mundo inteiro.

- Registre o resumo por agrupamentos a cada poucos segundos. O custo é quase nulo.
- **Ao detectar dessincronização, grave também o detalhe:** cada par (chave, hash do valor) do estado comparado e uma linha legível por entrada (`entry <key> <value hash> quest_stage intro = 77`). O analisador consegue então partir do agrupamento diferente até a chave e mostrar o valor em cada máquina.
- Compare resumos do mesmo `(category, epoch, seq)`. Um resumo obtido enquanto há mensagens em trânsito não representa dessincronização.

## <a id="3-read-the-first-divergence"></a>3. Leia a primeira divergência

```
python -I tools/flight/flight.py diverge host.cofr client1.cofr client2.cofr
```

No par de exemplo em `tools/flight/golden` (um script no cliente sobrescreveu silenciosamente um valor), a saída é:

```
FIRST DIVERGENCE (digest) at 680.000ms: world digest (epoch 1, seq 5) differs: ...
  key: world:0xA21A963AA6B76AAB   suspect slot(s): [0, 1]   (2 candidate(s) in total)
  narrowing: bucket(s) 171 of 256
    key 0xA21A963AA6B76AAB (bucket 171)  [from this digest]
      slot 0: value hash 10  stage.q1 = 10
      slot 1: value hash 99  stage.q1 = 99
  causal chain, window 290.000ms .. 680.000ms:
        ...
        325.000ms slot 1 TxnApplied   seq=4[0] origin=0 epoch=1 tag=1 hash=8d0f343480ecf481
        325.000ms slot 1 ScriptWrite  seq=4 key=stage.q1 value=99
```

Leia de cima para baixo: **o que** difere (a chave e os dois valores), **quem** está diferente (com três ou quatro máquinas o analisador identifica a minoria) e **como chegou ali** (a cadeia entre o último resumo em que todos concordavam e o divergente; linhas marcadas com `*` tratam diretamente da chave). Só a primeira descoberta importa. As seguintes costumam ser consequências.

Significado habitual de cada tipo de descoberta:

| Descoberta | Causa habitual |
|---|---|
| `txn-hash`: o mesmo efeito tem hashes diferentes | O efeito foi calculado de modo diferente em duas máquinas: entrou algo não determinístico (ordem de iteração, ponto flutuante, relógio local, número aleatório). |
| `txn-double`: aplicado duas vezes | Um datagrama duplicado ou retransmitido não foi deduplicado. A cadeia mostra "message delivered 2 times". |
| `txn-missing`: aplicado em outro lugar, nunca aqui | Um datagrama foi perdido e nunca reenviado ou foi descartado por um filtro. A cadeia mostra "message lost in transit". |
| `ownership-conflict` | Duas máquinas acreditam controlar o mesmo ator na mesma época: corrida na transferência de responsabilidade. |
| `ownership-stale` | Uma máquina aceitou mudança de responsável com época mais antiga: falta de verificação da época. |
| `digest` com todos os hashes de efeitos iguais | Algo fora do caminho de sincronização alterou o estado em uma máquina: script local, rotina de IA, limpeza, carregamento. No exemplo, o registro `ScriptWrite` revela isso. |
| `desync-marker` | Sua verificação informou algo que não é uma diferença visível de estado, como uma atualização obsoleta aceita. |

## <a id="4-reproduce-and-shrink"></a>4. Reproduza e reduza

Um registro mostra o que aconteceu uma vez. Para corrigir e evitar regressão, é necessária uma execução menor que possa ser reproduzida sob demanda.

- Sua estrutura de testes (fuzzer, simulador, bot por script) reproduz uma **fixture**, uma lista JSON de etapas. Forneça ao redutor um **hook de reprodução**, comando ou função Python que execute a fixture e informe se o bug ainda aparece. O contrato tem poucas linhas ([tools/flight/FORMAT.md](../tools/flight/FORMAT.md), seção 7), e `toy_replay.py` é um exemplo funcional.
- `flight.py fixture` pode criar uma fixture dos registros (uma etapa por datagrama recebido), reproduzindo o que cada máquina recebeu. Decisões locais do host aparecem no registro apenas como hashes; para elas, use o cenário em que sua estrutura produziu a falha.
- `flight.py shrink` executa depuração delta (ddmin): remove blocos de etapas e mantém uma lista menor somente se a reprodução **continuar falhando da mesma forma**. A correspondência da assinatura da falha importa: sem ela, uma redução transforma facilmente o bug em outro mais simples. Nos testes da ferramenta, uma fixture de exemplo com 31 etapas é reduzida às 3 relevantes.
- Torne as etapas **independentes**: cada uma tem seu próprio tempo absoluto e argumentos explícitos, de modo que remover qualquer subconjunto preserve uma execução válida. Marque a verificação final com `"pin": true` para nunca removê-la.

```
python -I tools/flight/flight.py shrink fixture.json --replay-cmd "build/my_replay {fixture}" -o shrunk.json
python -I tools/flight/flight.py gentest shrunk.json --name stale_echo --target my_replay
python -I tools/flight/flight.py report host.cofr client.cofr -o report.html --shrink shrunk.json
```

## <a id="5-keep-it-as-a-test"></a>5. Preserve como teste

`gentest` grava a fixture reduzida com `"expect": {"converges": true}` e uma linha CMake `add_test` para o programa de reprodução. O teste **falha enquanto o bug existe e passa quando ele é corrigido**; portanto, é incluído antes da correção. `regress.py DIR` executa todas as fixtures da pasta e exibe `ALL OK` quando cada uma atende à expectativa; marque uma fixture com `"converges": false` enquanto o bug for uma pendência conhecida.

## <a id="6-prove-the-tools-can-fail"></a>6. Comprove que as ferramentas conseguem falhar

Uma ferramenta que afirma não haver divergência só tem valor se fosse capaz de afirmar o contrário. As ferramentas flight incluem **variantes de mutação**: cada uma quebra algo de propósito (buffer circular que descarta o registro mais novo em vez do mais antigo, resumo que ignora valores, redutor que aceita outra falha), e a suíte precisa falhar. Faça o mesmo com suas verificações, conforme [QA automatizado](automated-qa.md): desligue a correção e o teste precisa ficar vermelho.

## <a id="pitfalls"></a>Armadilhas

- **Relógios diferem.** O analisador estima a diferença entre máquinas por mensagens pareadas; precisa de mensagens nos dois sentidos. Com tráfego em um só sentido, usa os relógios de calendário e avisa.
- **Identificadores de pares não são posições.** O analisador pressupõe que o identificador do par no transporte é a posição da outra máquina. Se o host numera conexões de outro modo, registre o mapeamento (`mapPeer`) ou nada será pareado.
- **Buffer circular pequeno perde o início.** As notas de alinhamento informam "lost N old records". Use um buffer maior ou extraia antes; uma dessincronização iniciada antes do registro mais antigo não pode ser rastreada até a causa.
- **Latência não é perda.** Uma transação ainda não recebida só está ausente depois de a máquina aplicar uma posterior ou continuar registrando por mais 2 segundos.
- **Datagramas truncados não podem ser decodificados ou reproduzidos.** Mantenha o limite acima da maior mensagem ou aceite a lacuna.
- **Registros contêm datagramas brutos.** Podem incluir nomes de jogadores e conversas. Inspecione antes de anexar a uma issue pública.

## <a id="where-to-go-next"></a>Onde continuar

- [tools/flight/README.md](../tools/flight/README.md): como adicionar o gravador ao mod, todos os comandos e os testes.
- [tools/flight/FORMAT.md](../tools/flight/FORMAT.md): formato do arquivo e esquema para escrever registros em qualquer linguagem.
- [QA automatizado](automated-qa.md): estrutura de testes em que os registros se integram. [Rede](networking.md): transporte subjacente.
