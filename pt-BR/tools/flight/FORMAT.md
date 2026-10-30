# <a id="co-op-flight-record-format-cofr-version-1"></a>Formato do registro de eventos cooperativos (.cofr, versão 1)

Um **registro de eventos cooperativos** é a caixa-preta de uma máquina em uma sessão: o que enviou e recebeu, decisões, alterações aplicadas ao próprio mundo, resumos do estado e notas. Um arquivo por máquina por extração. Coloque lado a lado arquivos de 2 a 4 máquinas para o analisador encontrar onde os mundos divergiram pela primeira vez e por quê.

O formato não conhece nenhum jogo. Tudo o que o jogo escolhe (categorias de resumo, nomes de tipos de mensagem, tipos extras de registro) fica em um **esquema** JSON armazenado no arquivo.

* Gravador: `tools/flight/cpp/` (C++17 independente). O lado C++ é a referência oficial da organização dos bytes.
* Leitor, gravador, analisador, redutor: `tools/flight/*.py` (Python, sem dependências). `cofr.py` também escreve arquivos para testes e ferramentas que acrescentam registros.
* Amostras de referência: `tools/flight/golden/`. `run_tests.py` as lê sempre, e um teste C++ falha se a saída do gravador se afastar delas.

## <a id="1-versioning"></a>1. Versionamento

A assinatura é `COFR`. O cabeçalho contém `version` (u16, atualmente 1).

* Um leitor recusa arquivos cuja assinatura ou versão desconheça.
* Mantêm a versão 1: novos tipos de registro na faixa reservada de 10 a 31, novos bits em `flags`, novas chaves no esquema. Leitores preservam tipos desconhecidos como conteúdo bruto e ignoram chaves desconhecidas do esquema.
* Alterar o cabeçalho do arquivo, o cabeçalho de registro ou a organização de um tipo de registro existente exige versão 2.

## <a id="2-file-layout"></a>2. Organização do arquivo

Um arquivo por máquina por extração. Todos os inteiros são little-endian. `str16` é um comprimento em bytes `u16` seguido de bytes UTF-8.

```
HEADER (64 bytes)
  "COFR" (4)   u16 version (=1)   u16 headerSize (=64)
  u8 slot   u8 role (0 host, 1 client, 2 sim)   u8 reason (0 manual, 1 desync, 2 crash, 3 shutdown, 4 test)   u8 reserved
  u32 protoVersion      your protocol or schema version, free to use
  u64 wallStartMs       unix time in ms when the recorder started
  u64 dumpTUs           recorder time of the dump, in microseconds
  u64 recordsDropped    records the ring overwrote before the dump
  u64 recordCount
  u32 sessionId   u32 epoch   u64 reserved
RECORD (16-byte header + payload), repeated to the end of the file
  u8 type   u8 flags   u16 payloadLen   u32 frame   u64 tUs      then payloadLen bytes
```

* `slot` é o número da máquina (host normalmente 0). `0xFF` significa desconhecido.
* `tUs` representa microssegundos monotônicos desde o início do gravador, comparáveis apenas dentro de um arquivo. Em simulador, todas as máquinas podem compartilhar um relógio virtual. O analisador estima a diferença real entre máquinas a partir de pares de mensagens.
* `frame` é o contador de quadros ou atualizações do jogo quando o registro foi feito.
* Um último registro parcialmente escrito (dump de falha) é aceitável: leitores preservam todos os completos anteriores e relatam o corte.
* O conteúdo tem no máximo 65.535 bytes. Elementos grandes (resumo longo, datagrama grande) são divididos ou cortados pelo gravador.
* `headerSize` permite acrescentar campos em versões posteriores: o leitor salta para `headerSize` para encontrar o primeiro registro.

## <a id="3-record-types"></a>3. Tipos de registro

| Tipo | Nome | Conteúdo |
|---|---|---|
| 1 | Meta | Pares repetidos `str16 key`, `str16 value`. O primeiro é `label`, nome da máquina nos relatórios. |
| 2 / 3 | NetOut / NetIn | Prefixo de 36 bytes, depois bytes do datagrama (abaixo). |
| 4 | TxnCaptured | `u8 kind` (0 confirmação decidida pela máquina, 1 intenção solicitada), `u32 intentId`, `u64 seq` (0 para intenção ainda sem número), `u32 effectCount`, `u64 hash` (hash dos hashes de efeitos, calculado pelo jogo), `u8 cause`, `u32 epoch` |
| 5 | TxnApplied | Um registro por efeito aplicado ao mundo local: `u64 seq`, `u32 epoch`, `u8 origin`, `u32 index`, `u8 flags`, `u8 cause`, `u8 effectTag`, `u64 hash` |
| 6 | Ownership | `u8 op`, `u64 actor`, `u32 epoch`, `u8 fromOwner` (255 nenhum), `u8 toOwner` (255 nenhum), `u8 reason`, `u64 txnId` |
| 7 | Digest | `u8 category`, `u32 epoch`, `u64 seq`, `u64 hash`, `u32 itemCount`, `u16 nShards`, depois cada `u32`, `u32 nKeys`, depois cada par (`u64 key`, `u32 valueHash`) |
| 8 | Marker | `u16 kind`, `str16 text` |
| 9 | Schema | JSON UTF-8, consulte seção 5. O gravador o emite uma vez, logo após Meta. |
| 10 a 31 | reservado | Para versões posteriores. |
| 32 a 255 | definido pelo jogo | Organização descrita por `custom_records` do esquema. |

As palavras "txn" e "effect" pertencem ao formato: uma **txn** é um lote confirmado de alterações numerado por `seq`; um **effect** é uma alteração dentro dele, numerada por `index`. Um jogo com outra estrutura (por exemplo, turnos lockstep) mapeia turno para seq e entrada para efeito, ou omite registros Txn e usa apenas resumos e marcadores.

### <a id="record-flags"></a>Indicadores do registro

| Bit | Nome | Significado |
|---|---|---|
| 1 | truncated | Net: datagrama cortado em `maxRawBytes` do gravador. |
| 2 | derived | Digest: criado de mensagem recebida, não do estado local. |
| 4 | detail | Digest: contém apenas entradas por chave (sem grupos). |
| 8 | bucketed | Digest: fragmentos são grupos de chaves; grupo = chave módulo número de fragmentos. |

### <a id="net-prefix-netout-and-netin"></a>Prefixo de rede (NetOut e NetIn)

```
u32 peer          transport peer id of the other side
u8 channel        send channel; 0xFF on NetIn
u8 mux            first byte of the datagram
u8 msgType        message type, filled by the decoder (0 without one)
u8 decode         0 decoded, 1 the decoder refused or the datagram was cut, 2 no decoder
u32 session   u32 epoch   u64 seqLo   u64 seqHi     filled by the decoder: the range of txn numbers the datagram carries
u32 rawLen        length of the datagram on the wire
then the datagram bytes, at most `maxRawBytes` of them
```

O caminho crítico guarda apenas `peer`, `channel`, `mux`, `rawLen` e os bytes. O gravador executa o decodificador na extração, não no registro do datagrama; portanto, registrar nunca decodifica nada. O analisador associa envio e recebimento pelo hash dos bytes do datagrama (remetente é a máquina NetOut, destinatário a NetIn).

### <a id="peer-ids"></a>IDs de participantes

`peer` é um número do transporte. O analisador o interpreta como vaga da outra máquina. Quando isso não corresponde à realidade (host cujo transporte numera conexões de outra forma), o gravador escreve entradas Meta `peer.<id>` = `<slot>`, usadas pelo analisador. `Recorder::mapPeer(id, slot)` faz isso.

### <a id="ownership"></a>Responsabilidade

Um ator é qualquer elemento sob responsabilidade de uma máquina (NPC, porta, veículo). O esquema informa quais operações atribuem responsável (`ownership_owner_ops`, padrão concessão e transferência). O analisador relata dois responsáveis diferentes para o mesmo `(actor, epoch)` e operação de atribuição com época inferior a outra já vista na máquina. Outras operações (liberação, rejeição por obsolescência, eco ou não responsável) são o funcionamento normal do sistema e nunca são relatadas.

### <a id="txnapplied-flags"></a>Indicadores TxnApplied

`flags` contém bits nomeados pelo esquema (padrão 1 captura de estado, 2 reparo, 4 referência inicial, 8 recuperação). `restate_mask` do esquema (padrão 7) informa quais bits marcam uma aplicação que **reafirma o estado**, em vez de repetir uma transação. O analisador ignora essas aplicações ao comparar conteúdo dos efeitos, procurar aplicações duplas ou ausentes.

### <a id="markers"></a>Marcadores

`kind` é um número nomeado no esquema (padrões: 0 nota, 1 dessincronização, 2 entrada, 3 saída, 4 etapa de teste, 5 salvamento, 6 carregamento, 7 nova base). **O tipo 1 (dessincronização) e o tipo 4 (etapa de teste) mantêm seu significado em todos os esquemas**: outras ferramentas escrevem resumos do tipo 4 e violações do tipo 1, e o analisador relata como descoberta o próprio marcador de dessincronização da máquina. Um marcador de dessincronização cujo texto contenha `ref=#<hex id>` o associa ao ator desse ID; a cadeia causal mostra então seu histórico de responsabilidade.

Linhas de texto de entrada: um marcador (qualquer tipo) cujo texto seja `entry <key as 16 hex digits> <value hash in decimal> <text>` descreve uma entrada do estado do qual foi calculado o resumo, por exemplo `entry c8800ff437102235 10 stage.q1 = 10`. O analisador mostra lado a lado o texto das duas máquinas. `Recorder::entryText(key, valueHash, text)` escreve uma.

## <a id="4-digests"></a>4. Resumos de estado

Um resumo é o hash de uma parte do estado compartilhado. `category` é um número nomeado pelo esquema. Resumos com o mesmo `(category, epoch, seq, derived)` em máquinas diferentes são comparados. Um resumo **derivado** (indicador 2) é extraído de mensagem recebida pelo decodificador; existe no remetente e no destinatário e é idêntico por construção. Portanto, resumos derivados e reais ficam em grupos separados e nunca são comparados entre si.

### <a id="bucketed-digests"></a>Resumos agrupados por chave

O gravador de referência produz resumos agrupados por chave (`bucketedDigest`, `BucketedState`), e `cofr.py` calcula os mesmos bytes.

```
mix(key, valueHash) = low 32 bits of splitmix64(key XOR splitmix64(valueHash))
bucket b            = key mod nBuckets                    (default 256)
shard[b]            = sum of mix(key, valueHash) over the entries of bucket b, modulo 2^32
hash                = FNV-1a 64 over the shards (each as 4 little-endian bytes), starting from the offset basis + itemCount
```

`splitmix64(x)`: `x += 0x9E3779B97F4A7C15; x = (x ^ (x >> 30)) * 0xBF58476D1CE4E5B9; x = (x ^ (x >> 27)) * 0x94D049BB133111EB; return x ^ (x >> 31)` (Sebastiano Vigna, domínio público), tudo em 64 bits. FNV-1a 64: base inicial `14695981039346656037`, primo `1099511628211`.

Como os fragmentos são somas, o resumo independe da ordem das entradas, e um valor alterado muda exatamente um fragmento. Ative o indicador 8 em um resumo cujos fragmentos sejam grupos de chaves; o analisador associa um fragmento diferente às chaves que pertencem a ele. Qualquer outro tipo de fragmento (por exemplo, resumo de 128 regiões do mapa) é comparado fragmento por fragmento, mas nunca associado a chaves.

### <a id="narrowing-digest-bucket-key-value"></a>Refinamento: resumo, grupo, chave, valor

1. **Resumo:** os hashes de duas máquinas diferem.
2. **Grupo:** os fragmentos que diferem.
3. **Chave:** entradas cujo hash de valor difere ou que só existem numa máquina. Vêm de registros de detalhes: registros Digest com indicador 4, contendo até 4.000 pares `(key, valueHash)` cada, vários registros por resumo (mesma categoria, época e seq; `itemCount` é o total). Um tratador de dessincronização escreve o resumo principal mais os detalhes em cada máquina. Para resumo com apenas grupos, o analisador obtém chaves do outro resumo mais recente com detalhes cujas chaves divergentes caem nos grupos divergentes.
4. **Valor:** texto das linhas de entrada (seção 3, Marcadores) em cada máquina.

Um jogo que registra resumo agrupado a cada poucos segundos e escreve detalhes apenas ao detectar dessincronização quase não paga custo nos períodos tranquilos e ainda consegue chegar à chave.

## <a id="5-the-schema"></a>5. O esquema

Texto JSON escrito em todos os arquivos como registro do tipo 9. Todas as chaves são opcionais. **Uma chave presente substitui integralmente o padrão daquela chave; uma ausente mantém o padrão.** O jogo fornece apenas o que muda.

```json
{
 "game": "toy",
 "digest_categories": {"0": "world", "1": "npcs"},
 "marker_kinds": {"0": "note", "1": "desync", "4": "test-step", "9": "checkpoint"},
 "ownership_ops": {"0": "grant", "1": "transfer", "2": "release"},
 "ownership_owner_ops": [0, 1],
 "message_types": {"4": "batch", "5": "ack"},
 "txn_messages": [4, 5],
 "apply_flags": {"1": "snapshot", "2": "repair", "4": "baseline", "8": "catch-up"},
 "restate_mask": 7,
 "custom_records": {
  "40": {"name": "ScriptWrite", "fields": [
   {"name": "seq", "type": "u64"}, {"name": "key", "type": "str16"}, {"name": "value", "type": "i32"}]}
 }
}
```

| Chave | Significado |
|---|---|
| `game` | Texto livre. |
| `digest_categories` | Nomes das categorias de resumo usadas no jogo. ID sem nome aparece como `cat<N>`. |
| `marker_kinds` | Nomes dos tipos de marcador. |
| `ownership_ops` | Nomes das operações de responsabilidade. |
| `ownership_owner_ops` | Operações que atribuem responsável a um ator. |
| `message_types` | Nomes dos tipos de mensagem relatados pelo decodificador. |
| `txn_messages` | Tipos de mensagem cujo intervalo seq é intervalo de transações. Numa cadeia causal, um datagrama trata "diretamente" de uma transação se for um desses tipos e seu intervalo contiver o seq. Omitido: toda mensagem decodificada conta. |
| `apply_flags`, `restate_mask` | Consulte indicadores TxnApplied. |
| `custom_records` | Tipos de registro de 32 a 255 definidos pelo jogo. |

`schemas/default.json` é o padrão (conjunto de exemplo: história, atores, recipientes, objetos, outros). `schemas/example_game.json` é um pequeno esquema personalizado. O padrão também está incorporado no gravador C++ e no leitor Python, e um teste verifica a equivalência entre os três.

### <a id="game-defined-records"></a>Registros definidos pelo jogo

Um tipo de registro de 32 a 255 é seu. Descreva a organização com campos na ordem. Tipos: `u8 u16 u32 u64 i8 i16 i32 i64 f32 f64` (little-endian), `str16` (comprimento u16, UTF-8), `bytes16` (comprimento u16, bytes brutos) e `bytes` (restante do conteúdo; somente no último campo). O analisador exibe esses registros pelo nome, mostra-os na cadeia causal e os considera diretamente relacionados a uma transação se tiverem campo `seq` igual ao seq dela (ou `ref` igual ao ator). Escreva um com `Recorder::custom(type, bytes)`. Sem entrada no esquema, o registro é guardado como bytes brutos e exibido como `Unknown<type>`.

Um esquema externo (`flight.py ... --schema FILE`) substitui o dos arquivos. Assim é possível ler arquivos antigos depois de renomear elementos.

## <a id="6-what-the-analyzer-reports"></a>6. O que o analisador relata

`flight.py diverge a.cofr b.cofr [c.cofr] [d.cofr]` encontra a primeira ocorrência entre:

* `txn-hash`: mesmo `(seq, index)` aplicado com hashes de efeito diferentes. A máquina divergente é identificada quando há três ou quatro.
* `txn-double`: uma máquina aplicou um efeito duas vezes.
* `txn-missing`: aplicado em outro lugar e nunca aqui. Só relatado se esta máquina aplicou um seq posterior ou continuou gravando por mais de 2 segundos depois dele.
* `ownership-conflict`, `ownership-stale`.
* `digest`: hash, grupo ou chave diferente. Com refinamento conforme a seção 4.
* `desync-marker`: máquina escreveu o próprio marcador de dessincronização (menor prioridade).

Exibe chave, máquina ou máquinas suspeitas e uma **cadeia causal**: registros sobre a chave (marcados com `*`), mais transações, eventos de responsabilidade, registros do jogo e mensagens entre máquinas envolvidas, retrocedendo ao último resumo daquela categoria aceito por todos, além de mensagens perdidas ou entregues duas vezes nessa janela. "Perdida" significa enviada e nunca observada na chegada; quando bytes idênticos são retransmitidos, qual cópia se perdeu é uma hipótese (a contagem está correta).

## <a id="7-replay-fixtures-and-the-replay-hook"></a>7. Dados de repetição e o hook de reprodução

O redutor (`shrink.py`) reduz uma lista de etapas independentes e só mantém uma lista menor se a reprodução ainda falhar com a **mesma assinatura de falha**. A parte que conhece seu jogo é o **hook de reprodução**, um comando ou função Python.

* **Dados de teste:** JSON, `{"version": 1, "config": {...}, "steps": [ ... ]}`. A lista pode se chamar `ops` (ou qualquer nome indicado por `--list-key`). Cada etapa precisa ser removível isoladamente, com tempo absoluto e argumentos explícitos. Uma etapa com `"pin": true` nunca é removida (use na verificação final, como `{"op": "quiesce", "pin": true}`).
* **Dados derivados de registros** (`flight.py fixture`): uma etapa `{"op": "deliver", "to": SLOT, "from": PEER, "hex": "<datagram>", "t": ms}` por datagrama recebido não cortado, em ordem de tempo alinhado, mais a etapa fixa de estabilização. Um registro guarda hashes de decisões do host, não as decisões; esses dados reproduzem o que cada máquina recebeu, não o que o host decidiu localmente.
* **Hook de comando** (`--replay-cmd "program args {fixture}"`): o marcador `{fixture}` se torna um arquivo temporário. O programa encerra com 0 se a reprodução convergir, 1 se divergir, 2 para dados inválidos. Pode exibir uma linha JSON `{"diverged": true, "violations": ["..."], "first": {...}}` ou uma linha por regra quebrada, `VIOLATION <rule-name> <detail>`. A assinatura é o nome da primeira regra ou a primeira violação sem números e hashes.
* **Hook Python** (`--replay-py module:function`, com `--replay-path DIR` para importar): a função recebe o dicionário dos dados e retorna `{"diverged": bool, "violations": [...]}`. Pode lançar exceção para dados inválidos.
* `toy_replay.py` implementa ambos como exemplo completo.

* **Dados de registros** (`"format": "cofr-trace-1"`, escritos por `from_failure.py`, reproduzidos no processo por `trace_replay.py`): registros brutos do arquivo `.cofr` de cada máquina; nenhum programa de reprodução é necessário. Cada etapa é um registro inteiro e independente: `{"op": "rec", "slot": 0, "ty": "TxnApplied", "at_ms": 123.4, "hex": "<the 16-byte record header and its payload>"}`. `ty` e `at_ms` (tempo alinhado) são para pessoas e para o redutor. `"headers": {"<slot>": "<hex of that machine's 64-byte header>"}` fornece o cabeçalho de cada máquina (a contagem é reescrita para as etapas mantidas), e o `"schema"` opcional é texto JSON que substitui o esquema nos registros. A reprodução alinha máquinas e classifica as descobertas: `digest-mismatch`, `divergence`, `stuck-sync` (transação aplicada numa máquina e nunca em outra, sem reafirmação de estado posterior naquela máquina), `desync-marker` e `transient-gap` (não é falha). Relata a primeira descoberta que não seja o próprio marcador de dessincronização de uma máquina.

`gentest` escreve os dados reduzidos como `<name>.json` com `"expect": {"converges": true}` e `<name>.cmake` com uma linha `add_test` para seu programa de reprodução. `regress.py DIR` executa todos os dados de teste de uma pasta pelo hook e exibe ALL OK quando cada resultado corresponde à expectativa (`"converges": false` marca bug conhecido ainda aberto). Dados de registros não recebem arquivo `.cmake` nem exigem hook: `regress.py` os reproduz diretamente.
