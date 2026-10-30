# <a id="sekiro-shadows-die-twice--co-op-notes"></a>Sekiro: Shadows Die Twice — notas do cooperativo

Sessão 1: 2026-10-27. Fase 0 (triagem) até uma primeira rodada de sondagens ao vivo.

## <a id="game-identity-owner"></a>Identidade do jogo (proprietário)

- Loja: Steam (informado pelo proprietário; instalação sem arquivos de emulador/desinstalador)
- Versão: 1.06 (ProductVersion de sekiro.exe: 1.6.0.0)
- SHA-256 de sekiro.exe: 637aca527538c0ec6e1f136c8ed66046e95dfbdbb1f51926e134d9916398b856 (68.005.144 bytes)
- SHA-256 de steam_api64.dll: fc20547408a7c34f0bd4946a34c21aab48a75e3b98dce9e55969f486d37b212f
- `pack.dat` (512 bytes, parece criptografado) na raiz do jogo: finalidade desconhecida
- Engine: proprietária FromSoftware, x64, Windows
- Modo desejado: online (amigos em seus próprios PCs)

## <a id="prior-work-in-this-repo"></a>Trabalho anterior neste repositório

- `data/directory.yaml` tem duas entradas Sekiro (verificado em 2026-10-16): Sekiro Online, sekiro-coop.
- Sem `games/sekiro/`, sem issues ou PRs mencionando Sekiro (verificado em 2026-10-27).
- playbook/engine-families.md lista Sekiro em FromSoftware; detalhes internos de Seamless Co-op não são públicos.

## <a id="observations-with-sources"></a>Observações (com fontes)

1. **Sekiro Online** — https://www.nexusmods.com/sekiro/mods/577
   - v2.05, última atualização em 2021-06-13 (correção para atualização do cliente Steam de 2021-06-08).
   - Página: não é mais desenvolvido; "uma nova versão está sendo feita desde 09/03/2025". Nada mais recente encontrado.
   - Estilo Souls: sinais de invocação (servidor só para sinais), P2P por Steam, convites de amigos Steam, 1 host + 5 fantasmas, invasões (não podem ser desativadas), escalonamento de nível.
   - É preciso concluir o tutorial e chegar primeiro ao Templo Dilapidado.
   - Problemas conhecidos: falhas, ficar preso após um golpe mortal num inimigo morto, versões incompatíveis entre si.
   - Versão exigida do jogo não informada na página. Código fechado.
2. **sekiro-coop (Rust)** — https://github.com/mstampfli/sekiro-coop
   - Projeto contínuo para 2 jogadores em Sekiro 1.06 (Steam), injetado por me3, MinHook.
   - README: não jogável pelo usuário final; jogador remoto não é renderizado no mundo (principal impedimento).
   - Possui: snapshots de jogadores a 60 Hz, eventos confiáveis de flags/itens/XP/teleporte (aplicação protegida por variável de ambiente), estado de inimigos do host a 5 Hz, hash de dessincronização a cada 60 quadros. Rollback escrito, mas não ativo.
   - Rede: UDP bruto por IP direto, sem travessia NAT; Steam P2P é um stub vazio.
   - 6 commits, 0 estrelas, sem versões publicadas. AGPL-3.0-or-later.
3. Nenhuma versão de Seamless Co-op (LukeYui) para Sekiro encontrada nas buscas.

## <a id="derived"></a>Deduzido

- Caminho mais rápido para jogar com amigos: Sekiro Online (funciona atualmente segundo relatos da comunidade, não testado por nós; exige Steam em cada PC).
- Cooperativo contínuo de história: somente sekiro-coop, um protótipo. O trabalho do caminho 1 (ampliar) seria renderizar o jogador remoto, conectar retransmissão Steam (Spacewar) ao stub Steam P2P vazio e depois fazer QA.

## <a id="unknown"></a>Desconhecido

Se Sekiro Online 2.05 ainda funciona no cliente Steam atual.

## <a id="session-1-cont-audit-of-sekiro-coop--1ef5fa8-2026-06-15"></a>Sessão 1 (continuação): auditoria de sekiro-coop @ 1ef5fa8 (2026-06-15)

### <a id="observations"></a>Observações
- Cópia de teste em `<test dir>` (cópia da instalação Steam; mesmos tamanhos/mtimes).
- O executável do proprietário corresponde ao alvo do mod: PE TimeDateStamp 0x5fa3e066 (= "1.06 exe stamp" de HANDOFF.md), SizeOfImage 70066176 (= contagem de bytes de HANDOFF.md).
- Bug: `crates/sekiro-sdk-sys/src/version.rs` tem `SIZE_V1_06 = 0x042D_8000` com comentário "= 70066176"; 70066176 é 0x042D_2000. Só usado como alternativa quando a detecção de versão por AOB falha.
- O executável Steam no disco tem seção `.bind` e `.text` criptografada (entropia 8,0, zero prólogos `48 89 5C 24 08`). Todos os 42 padrões AOB de aob.rs não encontram correspondência no arquivo: a validação AOB estática precisa da imagem descriptografada na memória (varredura em runtime ou dump do processo ativo).
- docs/HANDOFF.md (2026-04-19) diz: plano de dados validado contra peer-simulator; jogador remoto NÃO renderizado (gravações brutas na posição ChrIns são ignoradas pela renderização); desbloqueio planejado = alterar `common.emevd` (desempacotamento UXM + Yabber DCX) para a própria VM EMEVD do jogo chamar RequestAnimationPlayback / CharacterWarpRequest num boneco NPC reaproveitado. Não iniciado.
- CharacterWarpRequest teleporta somente para pontos predefinidos, não XYZ (HANDOFF §5) — um boneco suave provavelmente ainda precisa do caminho nativo de teleporte/posição.
- O repositório inclui binários me3 v0.11.0 em tools/me3/bin. Pela regra 8, usamos me3 de sua versão oficial (github.com/garyttierney/me3) com SHA-256.
- Compilar exige Windows + MSVC; este ambiente cloud não alcança static.rust-lang.org nem crates.io.

### <a id="derived-1"></a>Deduzido
- Compilação, inicialização e toda verificação ao vivo devem executar no PC do proprietário.

## <a id="session-1-cont-first-live-run-2026-10-27"></a>Sessão 1 (continuação): primeira execução ao vivo, 2026-10-27

Configuração (PC do proprietário, comandos executados pelo proprietário):
- sekiro-coop @ 1ef5fa8 do arquivo GitHub; cadeia de ferramentas 1.78.0 (de rust-toolchain.toml), MSVC 2022.
- O primeiro `cargo build` encontrou um STATUS_ACCESS_VIOLATION isolado de rustc em sekiro-sdk-bridge; recompilar de forma idêntica passou. (`-C linker-plugin-lto` naquele comando é a própria opção cargo para `lto = "thin"`.)
- MinHook: `vendor/minhook/{src,include}` incluído é idêntico byte a byte ao oficial TsudaKageyu/minhook @ d94c64d. `MinHook.x64.lib` recompilado dele com cl/lib (/MD /O2) por vcvars64.bat e vinculado com MINHOOK_LIB_DIR em vez do pré-compilado `vendor/lib/MinHook.x64.lib`.
- me3 v0.11.0 `me3-windows-amd64.zip` da versão oficial: SHA-256 1ddc6c3d9468aa6c7f99bd6b080aa94977e0d6fab771368ca89387a1c8cda4b7 = resumo do arquivo GitHub (e = zip incluído em sekiro-coop). Authenticode de me3.exe / me3-launcher.exe válido, assinante Gary Tierney.
- Inicialização: `me3 launch -g sekiro -e <test dir>\sekiro.exe --disable-arxan true --online false
  --savefile coop-test.sl2 -p sekiro-coop.me3`. Backup dos salvamentos do proprietário feito antes.

### <a id="observations-log-solo-no-session"></a>Observações (log, solo, sem sessão)
- me3: "Sekiro: Shadows Die Twice 1.06.0.0 Worldwide"; dearxan informa arxan detected: false; substituição do salvamento por coop-test.sl2 aplicada.
- Mod: `module loaded version=V1_06 size=70066176 base=0x140000000 has_base_addrs=true` (detecção baseada em AOB, então o erro de SIZE_V1_06 não importou).
- `hook installation finished installed=6 total=6`: SetFlag 0x1406c4520, ApplyEffect 0x1409f54a0, DeleteEffect 0x140bfb6d0, GiveItem 0x14091c970, AddExperience 0x1407c0ef0, WarpBonfire 0x14068e870.
- Estado do jogador legível (hp 320/320, postura 120/120, animação, posição, IGT). Eventos de transição SetFlag e chamadas ApplyEffect/DeleteEffect registrados. Tabelas de parâmetros encontradas: AtkParam_Pc 443, AtkParam_Npc 2396, SpEffectParam 3096, BehaviorParam 3128, NpcParam 1279, ItemLotParam 1926.
- Contagem do registro chrins=2 pouco após carregar. Nenhuma falha na abertura de novo jogo.

### <a id="not-yet-checked"></a>Ainda não verificado
- Sessão UDP (duas instâncias ou peer-simulator), aplicação remota, transmissão de estado de inimigos.

## <a id="session-1-cont-data-plane-vs-peer-simulator-2026-10-27"></a>Sessão 1 (continuação): plano de dados contra peer-simulator, 2026-10-27

Configuração: peer-simulator (compilado da mesma árvore) `--bind 127.0.0.1:28001 --peer 127.0.0.1:28000
--as client --fake-events`; jogo como host com SEKIRO_COOP_BIND=127.0.0.1:28000, SEKIRO_COOP_PEER_ADDR=127.0.0.1:28001. Somente loopback.

### <a id="observations-1"></a>Observações
- `session established seed=MatchSeed(...)` em segundos após carregar.
- Snapshots remotos chegam (`remote=peer=Client hp=420/420 pos=(..) anim=790010/790020`).
- BridgeEvents remotos chegam a cada 300 quadros (EventFlagSet 11100100, SpEffectApplied 4800).
- Host transmite EnemyStates; eco resolvido: `matched=2 unmatched_count=0`, `applied=0` (SEKIRO_COOP_APPLY_REMOTE não definida), divergências = HP-1 do simulador.
- Log peer-sim: snapshots enviados a cada segundo, EnemyStates ecoados com HP-1.
- Sem encerramento por dessincronização, sem falha. Execução anterior sem par escutando: UDP `os error 10054` a cada 2 s, laço de nova tentativa funciona, jogo não afetado.
- => Reproduz as afirmações do autor sobre o plano de dados nesta máquina (nível de QA: um cliente de jogo + simulador; não dois clientes reais).

## <a id="session-1-cont-puppet-probe-v2--remote-player-rendering-blocker-2026-10-27"></a>Sessão 1 (continuação): sonda de boneco v2 — impedimento à renderização do jogador remoto, 2026-10-27

Mudança (branch local `coop/puppet-probe` sobre 1ef5fa8, não publicada): novo `crates/sekiro-coop-dll/src/puppet.rs`, ativado por SEKIRO_COOP_PUPPET_PROBE=1. Fixa o ChrIns de equipe 6 mais próximo a até 12 m e grava Hero+(3,0,0) na posição de seu módulo físico (`ChrIns+0x1ff8 → +0x68 → +0x80`) dentro do desvio SetFlag; cada salto verificado com VirtualQuery, handle em ChrIns+0x08 reconferido antes de cada gravação.

### <a id="observations-log--owner-watching-the-screen"></a>Observações (log + proprietário olhando a tela)
- Fixado `char_id=10201000 handle=268484639 dist=11.9`.
- Gravações executaram em ThreadId(3) (chamador SetFlag); o ticker alternativo é ThreadId(2).
- ~200 gravações/s; o jogo mudou o valor entre duas gravações nossas em ~8% dos casos (180 de 2273). Posição relida acompanhou Hero+3 m.
- Proprietário: o inimigo teleportou visivelmente para perto (atrás) dele e o matou. => Gravar a posição física da thread do jogo REALMENTE move um personagem na tela.
- Após morte/recarga, o ponteiro ChrIns antigo não continha mais o handle; a sonda registrou stale=1, descartou o alvo, sem falha. O mesmo handle depois reapareceu no registro com novo ponteiro. Não houve nova fixação: o registro (alimentado só por ApplyEffect) não tinha entrada de equipe 6 em até 12 m.

### <a id="derived-2"></a>Deduzido
- A conclusão de docs/HANDOFF.md §3 "o caminho de renderização ignora gravações no módulo físico" não se sustenta. Seu experimento gravava da thread ticker de 60 Hz e relia imediatamente. A posição de um boneco pode ser conduzida por hook na thread do jogo sem o pipeline EMEVD/UXM.
- Ainda em aberto para um boneco utilizável: parar sua IA/hostilidade, reproduzir animações do jogador remoto, usar personagem com aparência do jogador, manter alvo após recargas.

### <a id="run-3-2026-10-27-1630-stale-build-fps"></a>Execução 3 (2026-10-27 16:30): compilação desatualizada, FPS
- O novo puppet.rs (gravação de equipe / nova fixação / orientação) não chegou ao disco do proprietário: a transferência entregou a versão anterior (9175 bytes em vez de 12490). O log confirma: linhas de estatísticas sem campos `repins`/`team_*`. O proprietário viu o mesmo comportamento da execução 2.
- Proprietário: FPS caiu a ~15 enquanto o boneco era mantido. Log: o jogo movia sua altura em ~0,3–0,4 m contra cada gravação (altura do Hero numa inclinação = dentro do terreno), ~300 gravações/s (várias por quadro). Correção: manter altura resolvida pelo jogo, máximo de uma gravação a cada 8 ms.
- Reenviado com verificação SHA-256 por releitura do arquivo no disco do proprietário.

### <a id="run-4-2026-10-27-1635-team-write--re-pin--heading-game-resolved-height"></a>Execução 4 (2026-10-27 16:35): gravação de equipe + nova fixação + orientação, altura resolvida pelo jogo
- FPS normal (proprietário). Fixação e nova fixação funcionaram: `re-pinned (same handle)` após morte, repins=1.
- Byte de equipe ChrIns+0x74: 6 → 2 gravado uma vez por fixação (team_before=6, team_now=2). Se o boneco parou de atacar: ainda não observado claramente. Outros inimigos (equipe 6) atacaram normalmente.
- Manter a altura resolvida pelo jogo fez o boneco cair através do mundo: y -43 → -66 → -98 → … → -265 m, animação 10000/10001 perto do fim, depois referência obsoleta/remoção. O proprietário o viu "desaparecer".
- Correção: manter a altura do jogo somente dentro de [Hero-1 m, Hero+2 m], senão Hero+0,2 m.

### <a id="run-5-2026-10-27-1643-height-reset"></a>Execução 5 (2026-10-27 16:43): redefinição da altura
- Boneco mantido ~3 m à frente do Hero durante toda a sessão (2467 gravações, 0 referências obsoletas, 5 redefinições de altura, FPS normal). Proprietário: no primeiro quadro atrás (orientação começa em +X), depois à frente ao se mover.
- Byte de equipe permaneceu 2 (era 6), mas o boneco continuou atacando (animações 3000/3002) e errava por ser reposicionado a cada 8 ms. => Equipe 2 sozinha não para sua IA.
- Próximo: flag global de depuração all_no_update_ai (debug_flags+13) como auxílio de teste; desativação de IA por personagem ainda por encontrar.

### <a id="run-6-2026-10-27-1647-global-ai-freeze-debug_flags13-0--1"></a>Execução 6 (2026-10-27 16:47): congelamento global de IA (debug_flags+13: 0 → 1)
- Proprietário: boneco não ataca mais; não tem animação; só acompanha quando o proprietário circula perto dele e fica para trás ao andar reto.
- Log: mesmo com toda IA congelada, o jogo revertia ~80% das gravações (2530/3147). Distância ao Hero majoritariamente 3,0 m, às vezes 6–9 m andando reto.
- Deduzido: a cópia que reverte não é a IA; provavelmente a própria cópia da engine física (proxy de personagem) sincronizada de volta ao módulo físico a cada quadro. Gravações persistem só ao atingir o ponto certo do quadro; saltos grandes são visíveis, pequenos passos por quadro se perdem.
- Próximo: varredura somente leitura de cópias espelhadas a partir de ChrIns (BFS pelos campos de ponteiros, profundidade 3, ≤4000 objetos, verificados com VirtualQuery) para toda tripla float igual à posição, duas vezes com 10 s de intervalo e gravações pausadas 1 s antes de cada varredura.

### <a id="run-7-2026-10-27-1653-mirror-scan-from-the-chrins"></a>Execução 7 (2026-10-27 16:53): varredura de cópias espelhadas a partir de ChrIns
- Varredura A (boneco voltara ao ponto de surgimento durante a pausa): 8 resultados, sobretudo cópias de posição de surgimento/origem: chr+0xe0, chr+0x1050, chr+0x1060, chr+0x50>+0x1a0, chr+0x58>+0x5a0, chr+0x18>+0x28>+0x1a0, chr+0x50>+0x18>+0x58>+0x138, chr+0x58>+0x340>+0x0>+0x258.
- Varredura B (boneco longe da origem): 3 resultados: chr+0x1050, chr+0x1060, chr+0x18>+0x28>+0x80.
- Ambas atingiram o limite de 4000 objetos; o caminho conhecido chr+0x1ff8>+0x68>+0x80 não foi alcançado.
- Deduzido (hipótese): chr+0x1050/+0x1060 = cópias de transformação ativas dentro de ChrIns; chr+0x18>+0x28 provavelmente é outro caminho ao módulo físico (mesmo +0x80).
- Próximo: gravar também em chr+0x1050/+0x1060, contar reversões por cópia; varrer com raiz no objeto de módulo físico.

### <a id="run-8-2026-10-27-1657-write-chr0x10500x1060-too-scan-from-physics-module"></a>Execução 8 (2026-10-27 ~16:57): gravar também chr+0x1050/+0x1060; varrer a partir do módulo físico
- Proprietário: FPS ~20 novamente; boneco "difícil de prender", acompanha alguns metros andando reto, depois fica para trás.
- Reversões por cópia: chr+0x1050 reverteu 2 vezes em 7056 gravações (não mantido pelo jogo, portanto provavelmente não é cópia ativa); chr+0x1060 reverteu junto com a posição física toda vez (1851 contra 1856). Taxa geral de reversão ~26%, redefinições de altura 57.
- Durante cada pausa de gravação de 1 s, o boneco voltava exatamente ao ponto de surgimento ([-198.86, -40.00, 243.24], igual à varredura A das execuções 6/7). Ambas as varreduras portanto viram a posição de origem.
- Varredura P (do objeto de módulo físico, 3434 objetos): phys+0x90, phys+0x1a0, phys+0x8>+0xe0, phys+0x8>+0x50>+0x1a0, phys+0x8>+0x58>+0x5a0. phys+0x8 é um ponteiro de volta ao ChrIns (mesmos sufixos da varredura C).
- Deduzido: algo reaplica uma posição de origem/alvo armazenada ao módulo físico a cada quadro. Mexer na posição luta contra esse sistema; é preciso encontrar o caminho nativo de movimento/teleporte (ou a sincronização de personagens remotos do jogo). Tentativa e erro por inicialização via proprietário é lenta demais para isso.
- Próximo proposto: despejar a imagem descriptografada de sekiro.exe da memória (somente leitura, mantida em local/, nunca comitada) e analisá-la offline (desmontador) para encontrar funções nativas de teleporte / animação / desativação de IA por personagem e como slots de jogadores da linhagem DS3 são criados.

## <a id="session-1-cont-offline-analysis-of-a-106-memory-image-2026-10-27"></a>Sessão 1 (continuação): análise offline de uma imagem de memória 1.06, 2026-10-27

Imagem: módulo `sekiro.exe` lido do jogo ativo com ReadProcessMemory (70.066.176 bytes, SHA-256 33533c5a…; mantido em `local/`, nunca comitado). `.text` descriptografada (entropia 6,65, 27.572 prólogos `48 89 5C 24 08`); 32 dos 42 AOBs de sekiro-coop encontram correspondência única (DeleteEffect não encontra porque o dump foi feito com os desvios do mod instalados). Ferramentas: GNU objdump na imagem bruta, um pequeno percorredor MSVC-RTTI (descritor de tipo → localizador de objeto completo → vftable).

### <a id="observations-rvas-for-steam-106-module-base-0x140000000"></a>Observações (RVAs para Steam 1.06, base do módulo 0x140000000)
- Comandos de script são classes locais em `NS_SPRJ::EventEntityCommandUtil::ChrCmd_*` (RTTI), cada uma com um método que encaminha a um `EventChrEntity` (vftable 0x29ac0b8, ponteiro ChrIns em +0x10):
  - `ChrCmd_EnableLogic(int id, bool)` → limpa/define bit 0 de `[ChrIns+0x50]+0x190` (ChrCtrl); também zera 16 bytes em +0x80 de outro objeto por personagem. RVA 0x9ede00.
  - `ChrCmd_SetDisableGravity(int, bool)` → `[[ChrIns+0x1ff8]+0x68]+0x92b = b` (0x9f5450).
  - `ChrCmd_SetDisableMapHit(int, bool)` → bit 0x10 de `[ChrIns+0x50]+0x194` (0x7de220).
  - `ChrCmd_Warp(int point, bool)` → resolve o ponto em posição/rotação, depois `ChrIns->vt[+0x6A0](chr, const float4* pos, const float4* rot, 1, 0)` (0x9f81f0, mesmo slot para ChrIns/EnemyIns/PlayerIns), depois `ChrIns+0x1a10 |= 2`.
  - vt[+0x6A0] → vt[+0x698] (0x9f8100): define `ChrIns+0x1af5`, chama `ChrCtrl->vt[+0x70](pos, rot, a, b)`, depois `vt[+0x680]()`, `vt[+0x678](a)`.
  - Quatérnio de rotação: módulo físico +0x70.
  - Outras classes de comando presentes: SetTeamType, WarpDmy, ChangeThink, ResetThink, EnableInvincible, SetNetworkUpdateValue, ChrResetAnimation.
- RTTI também tem ChrManipulator / ComManipulator (vftables 0x29d2ae0 / 0x29d2fb8).

### <a id="derived-3"></a>Deduzido
- Boneco v3 usa ChrIns::Warp (vt+0x6A0) na thread do jogo (protegido verificando se o slot é base+0x9f81f0) e EnableLogic desativado por personagem em vez da flag global de depuração.

### <a id="run-9-2026-10-27-2105-puppet-v3-native-warp-every-33-ms--per-character-logic-off"></a>Execução 9 (2026-10-27 ~21:05): boneco v3 (teleporte nativo a cada 33 ms + lógica por personagem desativada)
- Proprietário: boneco não ataca (EnableLogic por personagem desativado funciona sem congelar IA global), FPS normal, segue o jogador, mas pisca. Log perdido (a inicialização seguinte o limpou).
- Hipótese: vt[+0x698] redefine estado por teleporte (`ChrIns+0x1b94 = 1.0f` quando 0xa4a650 é true; interpolação de renderização), então teleportar 30×/s causa piscadas.
- Próximo: híbrido — teleporte nativo a cada 500 ms ou com erro >2 m, passos físicos brutos a cada 8 ms entre eles.

### <a id="run-10-2026-10-27-2115-hybrid-move"></a>Execução 10 (2026-10-27 21:15): movimento híbrido
- Teleporte nativo a cada 500 ms ou com erro >2 m (108 teleportes em ~40 s), passos físicos brutos a cada 8 ms entre eles (2742). Distância ao Hero manteve 3,0–3,3 m, stale=0, bit de lógica permaneceu limpo (`[ChrIns+0x50]+0x190 = 2`), sem ataques. Proprietário: movimento suave, piscadas "praticamente desapareceram", FPS normal.
- Entre teleportes, o jogo ainda o move em ~60% das vezes (sobrescrito 1689/2850), mas pouco o bastante para não aparecer. O boneco continua com sua própria animação (405010, ocasionalmente 7020).
- Estado do boneco: posição resolvida. Em aberto: conduzi-lo pelo snapshot de rede do jogador remoto, reproduzir as animações dele, ter aparência de jogador.

### <a id="run-11-2026-10-27-2127-puppet-driven-by-the-network-sourcenet--peer-simulator---mirror"></a>Execução 11 (2026-10-27 21:27): boneco conduzido pela rede (SOURCE=net) + peer-simulator --mirror
- Falhou: remote_fresh=0, remote_stale=1380. O simulador negociou conexão, depois não enviou nada aguardando os primeiros snapshots da DLL (enviados só no jogo); a tolerância da DLL expirou após 9 s ("peer grace expired" em todo quadro, 3.700 linhas de log) e nenhum snapshot chegou.
- Sem posição remota, o passo do boneco retornava antes de desativar lógica/gravar equipe, então o inimigo fixado permanecia hostil (equipe 6, lógica ligada) e matou o proprietário. Depois o jogo fechou sem diálogo de erro após morte/recarga; causa ausente do log.
- Correções: simulador envia sinais de vida enquanto espera; boneco é neutralizado (lógica desligada, equipe 2) antes de qualquer retorno antecipado; taxa do log de tolerância limitada.
- Causa da falha (log Application Error do Windows): AV 0xc0000005 em sekiro_coop.dll no RVA 0xac37c (mesma DLL, PE stamp 0x6ae0ed0a). Desmontagem: `live::chrins_snapshot` de sekiro-coop lendo `[[ChrIns+0x1ff8]+0x18]` num ChrIns liberado. Chamado da transmissão EnemyStates do host, que só executa com sessão (execuções solo anteriores nunca passavam ali). Entradas do registro sobrevivem à morte/recarga.
- Correção: podar o registro a cada quadro (handle em +0x08 deve corresponder, todo salto mapeado por VirtualQuery) e reconferir imediatamente antes de cada snapshot/gravação de HP.
- Observação lateral: o log de eventos do proprietário também mostra AVs em cargo.exe (21:11) e powershell.exe (20:55) em módulos desconhecidos, além da AV anterior de rustc na primeira compilação. Sem explicação; convém lembrar se aparecerem falhas não relacionadas.

### <a id="run-12-2026-10-27-2135-network-driven-puppet-second-try"></a>Execução 12 (2026-10-27 21:35): boneco conduzido pela rede, segunda tentativa
- Correção do registro se manteve (sem falha). Boneco neutralizado (sem ataques), mas "só corre reto": sem sessão e, portanto, sem posição remota; sem gravação de posição, sua última animação o levava embora.
- Sem sessão: o único Handshake do simulador saiu 0,03 s antes de a DLL vincular seu socket (os error 10054) e se perdeu; o simulador recebeu o handshake da DLL e declarou sessão ativa, enquanto a DLL continuou expirando e reenviando. O handshake de sekiro-coop envia uma vez e espera, então o lado que inicia primeiro pode perder seu pacote.
- Correções: simulador responde a toda nova tentativa Handshake; boneco mantém última posição sem dados.

### <a id="run-13-2026-10-27-2143-network-driven-puppet-works"></a>Execução 13 (2026-10-27 21:43): boneco conduzido pela rede funciona
- Inicialização por script .cmd (um comando colado havia sido cortado, iniciando o jogo original sem perfil nem substituição do salvamento; o principal foi gravado, mas nenhum mod carregou, então nada modificado tocou nele).
- Sessão ativa (simulador respondeu a uma repetição de handshake); remote_fresh=2383, remote_stale=0; ~2 teleportes/s. Proprietário: boneco segue seu caminho como esperado, mas treme e não vira.
- O jogo o movia entre nossos passos em ~80% das vezes (1820/2383): root motion de sua própria animação de corrida com lógica desligada.
- Offline: `ChrCmd_ChrResetAnimation(false)` termina em `0x9f4c60(chr)` = redefinição do módulo de animação `[ChrIns+0x1ff8]+0x28` por 0xb442c0 (a variante `true`, 0x9f4c80, também define `[[ChrIns+0x50]+0x20]+0x1334 = 1`).
- Próximo (boneco v4): redefinir animação a cada 2 s (chamada verificada por bytes), quatérnio yaw (0, sin, 0, cos) do movimento do alvo gravado em físico +0x70 e passado ao teleporte, alvo suavizado. Registra rotação e orientação do herói para calibrar a convenção yaw.

### <a id="run-14-2026-10-27-2150-puppet-v4-animation-reset-yaw-easing"></a>Execução 14 (2026-10-27 21:50): boneco v4 (redefinição de animação, yaw, suavização)
- Redefinição executou a cada 2 s (29 redefinições, 0 recusadas pela verificação de bytes), sem falha.
- Proprietário: boneco fica "invertido" em relação ao jogador, treme ao virar.
- Log: físico +0x70 do Hero lê `[0, θ, 0, 0]` com θ em radianos (±π), não quatérnio; havíamos gravado (0, sin, 0, cos). Calibração em 8 amostras da direção do Hero (dx, dz): θ = atan2(dx, dz) + π = atan2(-dx, -dz), todas dentro de ~0,15 rad.
- Correção: gravar `[0, yaw, 0, 0]`; recalcular alvo yaw só após 0,15 m de movimento e suavizar pelo arco mais curto.

### <a id="run-15-2026-10-27-2153-yaw-fixed"></a>Execução 15 (2026-10-27 21:53): yaw corrigido
- Proprietário: boneco agora olha para onde se move. Não anda: desliza/teleporta. Está na pose redefinida (ociosa); entre teleportes nativos (a cada 500 ms), o jogo ainda o puxa de volta, então salta a cada teleporte.
- Próximo: (a) verificação rápida com intervalo menor de teleporte agora que sua animação está redefinida (piscadas da execução 9 podem ter vindo da disputa com seu ciclo de corrida); (b) caminhada real exige conduzir a própria locomoção do boneco por entrada de movimento (ChrManipulator / ChrCtrl) ou chamada nativa de reprodução de animação — ainda não encontrada.

### <a id="run-16-2026-10-27-2335-native-warp-every-50-ms"></a>Execução 16 (2026-10-27 23:35): teleporte nativo a cada 50 ms
- Proprietário: boneco o segue suavemente com animação de corrida.
- Log: ~16 teleportes/s, passos brutos entre eles, remote_fresh=1728, remote_stale=0, redefinições de animação a cada 2 s. A animação alterna entre 405001/405003/405010 (sua própria família de caminhada/corrida): teleportes nativos frequentes o movem como movimento real e a locomoção do jogo escolhe o ciclo. As piscadas da execução 9 (33 ms) sumiram agora que sua animação foi redefinida.
- 50 ms é o novo padrão.
- Estado: boneco conduzido pela rede, inofensivo, caminhando/correndo suavemente e olhando na direção do deslocamento. Em aberto: virar parado (sem yaw em PlayerSnapshot), ações (ataques, deflexões, saltos), aparência do jogador, retransmissão Steam, teste real com dois PCs.

### <a id="run-17-2026-10-27-2342-yaw-in-playersnapshot"></a>Execução 17 (2026-10-27 23:42): yaw em PlayerSnapshot
- PlayerSnapshot ganhou `yaw: f32` (físico +0x70 do Hero, elemento 1); boneco vira para o yaw remoto (alternativa: direção de movimento); simulador o espelha. Formato de rede mudou: DLL e simulador recompilados juntos.
- Proprietário: boneco vira com ele, inclusive parado. Ao parar, às vezes mantém a animação de corrida (redefinição só a cada 2 s).
- Correção: redefinir animação assim que o alvo não se mover 5 cm por 200 ms.

### <a id="run-18-2026-10-27-2347-stop-reset"></a>Execução 18 (2026-10-27 23:47): redefinição ao parar
- Proprietário: geralmente para corretamente; ocasionalmente mantém a animação de corrida.
- Hipótese: um teleporte periódico após redefinir é lido como movimento e reinicia o ciclo.
- Mudança: sem teleportes periódicos enquanto o alvo está parado (só para corrigir >2 m), e redefinições adicionais a cada 400 ms por 1,7 s após parar.

### <a id="run-19-2026-10-27-2349-no-simulator"></a>Execução 19 (2026-10-27 23:49): sem simulador
- Proprietário: boneco congelou no lugar com animação de corrida.
- Log: remote_fresh=0 por toda a execução; DLL recebeu os error 10054 em 75 tentativas de handshake; log do simulador terminou na execução anterior (não iniciou desta vez; causa desconhecida, provavelmente processo/handle de log remanescente). A lógica de parada nunca executou porque não chegaram dados.
- Correções: redefinir animação do boneco quando os dados de rede pararem; script de inicialização exclui logs antigos, inicia simulador, verifica execução e recusa iniciar o jogo se ele não executar.

### <a id="run-20-2026-10-27-2356-stop-handling-confirmed"></a>Execução 20 (2026-10-27 23:56): tratamento da parada confirmado
- Script informou simulador em execução antes de iniciar o jogo.
- Proprietário: "tudo funciona como deveria" — boneco segue, vira com ele e abandona a animação de corrida quando ele para. Uma execução, observada pelo proprietário; sem verificação automatizada.

## <a id="session-1-cont-actions--native-forceplayanimation-offline-2026-10-28"></a>Sessão 1 (continuação): ações — ForcePlayAnimation nativo (offline, 2026-10-28)

### <a id="observations-106-image"></a>Observações (imagem 1.06)
- RTTI: `EventEntityCommandUtil::ComCmd_ForcePlayAnimation(int, int)` (vftable 0x29ac598, método 0x754720) e `ComCmd_PlayAnimation` (0x29ac588 / 0x754800) encaminham para `EventChrEntity` vt[+0x38] e vt[+0x30].
- vt[+0x38] = 0x750e00: `0xbd84c0([[ChrIns+0x1ff8]+0x58], anim_id)`. 0xbd84c0 armazena o ID em module+0x10 e em `[owner+0x20]+0x24` (owner por 0xb271d0). vt[+0x30] = 0x751120: mesma chamada, mas somente quando 0xbd8430 diz que o módulo está ocioso (PlayAnimation versus ForcePlayAnimation).
- RTTI também lista `NetworkManipulator` e `NetAIManipulator`: provavelmente como o jogo conduz jogadores remotos; não analisados.

### <a id="run-21-plan-puppet-v5"></a>Plano da execução 21 (boneco v5)
- Aprender a animação de repouso do remoto (inalterada ≥1 s enquanto parado). Quando a animação remota mudar para outra coisa parado, chamar 0xbd84c0 (verificada por bytes) com `SEKIRO_COOP_PUPPET_ACTION_ANIM` (padrão 3000, ID de ataque inimigo visto na execução 8). Redefinições de parada e periódicas são suspensas por 1,5 s depois. Toda transição de animação remota é registrada para mapear IDs a ações. Script de inicialização copia o log da DLL para junto dele.

### <a id="run-21-2026-10-28-0135-forceplayanimation-works"></a>Execução 21 (2026-10-28 ~01:35): ForcePlayAnimation funciona
- 10 chamadas forçadas, 0 recusadas; 300 ms depois, a animação do boneco lia 3000 em 9 de 10 casos (uma vez 7000). Proprietário: boneco golpeia quando ele ataca, esquiva ou bloqueia e salta quando ele salta.
- O salto do boneco provavelmente vem do caminho de posição/altura, não da animação forçada (hipótese).
- IDs de animação remotos (= do proprietário), na ordem de teste dele (ataque ×3, bloqueio ×2, salto ×2, esquiva ×2, correr e parar). Deduzidos da ordem, não confirmados:
  - repouso 790010 (também 0); ataque 790040; bloqueio 50203000 → 50203010;
  - salto 201001 → 201011 → 201040; esquiva 213300 / 213301; correr/parar 1151, 1200, 1500, 1510.
- Desconhecido: se o proprietário tinha a katana (790040 pode ser golpe desarmado).

### <a id="run-22-plan"></a>Plano da execução 22
- Forçar só IDs mapeados (padrão 790040 → 3000), também em movimento. Sonda de catálogo: enquanto o proprietário fica parado, tocar 18 IDs inimigos candidatos, um a cada 3 s, registrando se cada um foi aplicado, para ele nomear semelhantes a bloqueio, esquiva e salto. Deslocamento de espelhamento de 5 m para os golpes errarem.

### <a id="run-22-2026-10-28-0145-catalog"></a>Execução 22 (2026-10-28 01:45): catálogo
- Recompilar exigiu segunda tentativa: STATUS_ACCESS_VIOLATION de rustc novamente (terceira AV de ferramenta de desenvolvimento no PC do proprietário; causa desconhecida).
- Catálogo em c1020 (char 10201000): 3001, 3002, 3003, 3005, 3010 foram aplicados (animação do boneco = ID após 300 ms); 4000, 5000, 5001, 5010, 6000–6002, 7000, 7001, 7010 não (permaneceu em 405002). Proprietário: nº 2 um ataque com salto, nº 3 uma investida, depois a investida novamente, depois nada visível.
- ID remoto 790040 também permaneceu por >1 s enquanto o proprietário ficava parado, e um combo de 3–4 golpes não mudava o ID entre acertos. Hipótese: `+0x1ff8 → +0x10 → +0x20` é camada base/estado (790010 ocioso, 790040 ocioso em combate após golpe), não a animação de ataque. Bloqueio aparece como 50203000 → 50203010 → 50203012 (e 400 no meio ao se mover).
- Plano da execução 23: observar campos u32 de Hero sm+0x10 / sm+0x28 / sm+0x58 / chr+0x20 para valores parecidos com animação (6–8 dígitos) e encontrar o slot de ataque; catálogo rápido (152 IDs, 0,4 s cada) registrando quais o boneco aceita.

### <a id="run-23-2026-10-28-0152-action-slots-found"></a>Execução 23 (2026-10-28 01:52): slots de ações encontrados
- Catálogo rápido (152 IDs, 0,4 s cada) em c1020: aceitou 3000–3010, 3012, 3014, 3015, 3020, 3100. Nada em 4000–9900, 7001–7030, 10000–10040, 400000–410000 foi aplicado. Proprietário: um parecido com salto perto de nº 2–3 (3001/3002), parecido com esquiva perto de nº 4–5 (3003/3004).
- Varredura de slots Hero: o objeto TimeAct `[ChrIns+0x1ff8]+0x10` tem dois anéis de 5 entradas, passo 0x28. Anel em +0x20 (+0x48, +0x70, +0x98, +0xc0) = camada base (700000, 790010, 790500, 790040, 201001, 50203000, 213300, 1151 ...). Anel em +0x34 (+0x5c, +0x84, +0xac, +0xd4) também recebe os golpes de combo 50300000, 50300100, 50300010, 50300110, 50300020, 50300030, ataque com salto 50308000/50308050, aparar 50002000 (hipótese), mais ações da camada base. +0xf8/+0x100 misturam ambos.
- Deduzido: o ID de animação do snapshot é o anel +0x20; ataques precisam do anel +0x34.

### <a id="run-24-plan"></a>Plano da execução 24
- PlayerSnapshot ganha `action_id` + `action_seq`: qualquer slot +0x34 mudando para ID não zero é nova ação. Mapa do boneco: golpe de combo 1/2/3/4+ → 3000/3001/3005/3006, salto e ataque com salto → 3002, esquiva 213300/213301 → 3004; bloqueio/aparar → nada (nenhum correspondente encontrado). Formato de rede alterado.

### <a id="run-24-2026-10-28-0158-actions-over-the-network"></a>Execução 24 (2026-10-28 ~01:58): ações pela rede
- Proprietário: ataques do boneco seguem o ritmo do combo; ao esquivar, golpeia em arco (3004); ao saltar, faz golpe simples (3002); sem reação ao bloqueio (nenhum mapeado).
- Log: golpes de combo 50300000 → 50300010 → 50300020 → 50300030 chegaram em ordem e todos foram reproduzidos (3000, 3001, 3005, 3006; animação do boneco = ID desejado 300 ms depois sempre). Outros IDs do anel de ação vistos: 600, 401, 432, 433, 443, 11 (mover/virar, hipótese), 201050 (variante de salto).
- Bug: uma ação é gravada em 4–5 slots ao longo de ~100 ms; action_seq então subia 4–5 vezes por ação e o boneco forçava a mesma animação com essa frequência. Correção: contar um ID uma vez, salvo após 300 ms. Mapeamento de salto/esquiva removido (nenhum semelhante em c1020).
- Deduzido: um boneco inimigo só mostra os movimentos do próprio inimigo. Movimentos exatos exigem boneco que use o conjunto de animações do jogador (c0000), para reproduzir os IDs remotos como são.

## <a id="session-1-cont-spawning-a-character-offline-2026-10-28"></a>Sessão 1 (continuação): criar um personagem (offline, 2026-10-28)

### <a id="observations-106-image-1"></a>Observações (imagem 1.06)
- `CSDebugChrCreator` (vftable 0x2a952a8) é alocado no construtor WorldChrMan (0xa46b80, `[this+0x3148]`) e processado pela atualização WorldChrMan (0xa50a1c: vt[+0x10]). Etapas: STEP_Idle 0xc0ff70 (define +0x1b0 = 1), STEP_Load 0xc0ff80, STEP_LoadWait 0xc10010.
- `CSDebugChrPerfChecker::_STEP_CreateChr` (0xc15f00) o conduz: +0x118 = ID NpcParam (buscado em SoloParamRepository por 0x10c6750), +0x114 = segundo ID (ThinkParam, hipótese), +0x1a4 = distância à frente do Hero, depois `0xc0f2a0(creator, model)`.
- 0xc0f2a0: só se +0x1b0 != 0, armazena número do modelo em +0x1a0 e executa 0xc10880: posição = posição Hero + frente × (+0x1a4) + cima × (+0x1a8), ângulo de +0x1ac, nome formatado do número do modelo em +0x120, depois muda para a etapa de carga.
- IDs de modelo (lista de personagens soulsmodding.com): Owl c5060, jogador c0000, c1020 = Samurai General (boneco das execuções 8–24; c1010 é o soldado Ashina).

### <a id="run-25-plan"></a>Plano da execução 25
- `SEKIRO_COOP_SPAWN=5060:auto`: 10 s após carregar, registrar linhas NpcParam 50600000–50609999, pegar a primeira, verificar criador (vftable, byte ocioso, bytes da função de solicitação), definir campos e solicitar modelo 5060 a 4 m à frente do Hero; depois fixar o personagem com esse ID NpcParam. Desconhecido: se a versão comercial processa o criador (+0x1b0) e se um personagem criado chega ao registro do mod (alimentado pelo hook ApplyEffect).

### <a id="run-25-2026-10-28-0210-spawn-works"></a>Execução 25 (2026-10-28 02:10): criação funciona
- Log: linhas NpcParam para c5060 = 50600000, 50600080, 50601000, 50601010, 50601080, 50609080, 50609090, 50609091. Vftable do criador OK, byte ocioso +0x1b0 = 1 (a versão comercial o processa), bytes da solicitação OK; modelo 5060 / NpcParam 50600000 / think 50600000 solicitado.
- Proprietário: Owl apareceu e o matou. O código do boneco nunca o fixou: o personagem criado não apareceu no registro do mod (alimentado só pelo hook ApplyEffect).
- Offline: STEP_LoadWait termina com `creator+0x1b8 = 0xa492e0(WorldChrMan, &creator+0x100)`, o ChrIns criado. Correção: observar +0x1b8 após a solicitação, conferir ID do personagem = ID NpcParam, fixá-lo e desligar sua lógica imediatamente.

### <a id="run-26-2026-10-28-0220-spawned-owl-as-the-puppet"></a>Execução 26 (2026-10-28 02:20): Owl criado como boneco
- Primeira inicialização travou em me3-launcher (sem janela do jogo, sem log do mod); após fechá-lo, a segunda funcionou. Causa desconhecida.
- Log: personagem criado fixado 48 ms após solicitar (char id 50600000, handle 268795904), bit de lógica limpo, equipe 2; 7135 passos, 497 teleportes, 9 ações forçadas, remote_fresh=7136, stale 0.
- Proprietário: Owl virou boneco, segue, responde a ataques com movimentos de combo, reage só a ataques (só ataques mapeados). FPS caiu para 25–30.
- Desconhecido: causa do FPS. 65 redefinições de altura na execução (hipótese: deslocamento X de 5 m coloca Owl, maior, na geometria, e a física luta com gravações brutas como nas execuções 3–5).

### <a id="run-27-plan"></a>Plano da execução 27
- Teste de FPS em fases desde a fixação: A normal 0–40 s, B só teleportes 40–80 s, C sem gravações de posição 80–120 s, D normal + catálogo rápido (187 IDs, 0,4 s) para Owl enquanto o proprietário fica parado.

### <a id="run-27-2026-10-28-0226-owl-catalog-fps-phases"></a>Execução 27 (2026-10-28 02:26): catálogo Owl, fases de FPS
- Fases executaram (A 0–40 s, B 40–80 s, C 80–120 s, D depois); 0 redefinições de altura desta vez. Proprietário não informou FPS por fase: causa ainda desconhecida.
- Owl (c5060, NpcParam 50600000) aceitou 3000–3049 (exceto 3022), 3060, 3061, 3063–3066, 3068, 3069, 3090–3093, 3100; nada em 3200–6900 (passo 100) — esses o deixaram em 40000 (ocioso).
- Proprietário: bloqueio e aparar apareceram nos últimos ~20 s, isto é, entre 3090–3093 e 3100 (únicos IDs aceitos então); salto difícil de identificar, muitos ataques com salto.
- Execução 28: catálogo lento (3 s cada) de 3090, 3091, 3092, 3093, 3100, 3060, 3061, 3063–3066, 3068, 3069 para o proprietário nomear bloqueio, aparar, esquiva, salto.

### <a id="run-28-2026-10-28-0233-owl-slow-catalog"></a>Execução 28 (2026-10-28 02:33): catálogo lento Owl
- Proprietário: FPS estável em 60 em todas as fases da execução 27, então a queda na 26 não é o código do boneco (hipótese: ponto de criação na geometria; a 26 teve 65 redefinições de altura, a 27 nenhuma).
- Todos os 13 IDs tocaram (animação do boneco = ID 300 ms depois). Proprietário: nº 4 (3093) = bloqueio; nº 8 (3063) = esquiva, sem certeza. Nenhum aparar ou salto simples nomeado.
- Mapa da execução 29: bloqueio 50203000 e aparar 50002000 → 3093, esquiva 213300/213301 → 3063, salto nenhum.

### <a id="run-29-2026-10-28-0238-owl-actions"></a>Execução 29 (2026-10-28 02:38): ações Owl
- Proprietário: ataques certos; manter bloqueio toca a própria animação de bloqueio (3093); aparar parece semelhante (também 3093); esquiva (3063) toca combo de dois golpes: ID errado.
- Execução 30: cada esquiva toca o próximo candidato de 3061, 3064, 3060, 3065, 3066, 3068, 3069 (registrado com seu número) para o proprietário nomear o certo.

### <a id="run-30-2026-10-28-0243-owl-dodge"></a>Execução 30 (2026-10-28 02:43): esquiva Owl
- Log: esquivas 1–7 tocaram 3061, 3064, 3060, 3065, 3066, 3068, 3069 em ordem. Proprietário: nº 2 (3064) é passo para trás com lançamento de bombinha. Esquiva → 3064.
- Também visto: pressionar bloqueio brevemente dá 50203000, depois 50002000 (aparar) em ~0,5 s.
- Mapa atual de ações do boneco Owl: golpes de combo 1–4 → 3000/3001/3005/3006, bloqueio e aparar → 3093, esquiva → 3064, salto → nenhum (altura acompanha). Observado pelo proprietário, sem verificação automatizada.

### <a id="run-31-plan-player-model-puppet"></a>Plano da execução 31: boneco com modelo do jogador
- `SEKIRO_COOP_SPAWN=0:auto` (modelo c0000): criar com a primeira linha NpcParam em 0–9999; se não houver, registrar IDs baixos de NpcParam e não criar. `SEKIRO_COOP_PUPPET_ANIM_PASSTHROUGH=1`: boneco toca os IDs de ação remotos como são (só IDs de 6–8 dígitos).
- Desconhecido: se c0000 pode ser criado como personagem inimigo/NPC (risco de falha; cópia de teste).

### <a id="run-31-2026-10-28-0248-c0000-spawn-crashes-the-game"></a>Execução 31 (2026-10-28 02:48): criar c0000 derruba o jogo
- Linhas NpcParam para modelo 0: 0, 1, 10, 11, 12, 100, 540, 541, 542. Criado c0000 com NpcParam 0 / think 0; criado e fixado após 49 ms; jogo falhou ~0,3 s depois.
- Application Error do Windows: AV de sekiro.exe no RVA 0x9cbf09, em 0x9cbe40, acessor de slot de equipamento (asserções "slotIdx>=0", "slotIdx<EQUIP_SLOT_IDX_Num"); leu `[equip+slot*4+0x24]` por ponteiro de equipamento inválido. Deduzido: personagem c0000 não tem dados de equipamento com NpcParam 0. Não em sekiro_coop.dll.
- Execução 32: o mesmo com NpcParam 540 (hipótese: linha de NPC humano que talvez tenha equipamento).

### <a id="run-32-2026-10-28-0252-c0000-with-npcparam-540"></a>Execução 32 (2026-10-28 02:52): c0000 com NpcParam 540
- Mesma falha, mesmo lugar (sekiro.exe RVA 0x9cbf09, acessor de slot de equipamento 0x9cbe40).
- Chamadores de 0x9cbe40 incluem 0x79dbe0 (passa `rcx+0x98`, slot 0–0x18) e 0x7ceaf0, 0x9cb210.
- Deduzido: personagem c0000 feito pelo criador de inimigos não tem os dados de equipamento do jogador lidos pelo caminho de modelo/renderização c0000. Um boneco com aparência de Wolf precisa do caminho de personagem jogador (PlayerIns + seus dados de jogo, como jogadores remotos de DS3), não do criador de depuração. Não tentado.
- Script de inicialização de volta ao boneco Owl (5060, mapa de ações).

## <a id="session-1-cont-wolf-looking-puppet--research-offline-2026-10-28-0300"></a>Sessão 1 (continuação): boneco com aparência de Wolf — pesquisa (offline, 2026-10-28 ~03:00)

### <a id="observations-106-image-2"></a>Observações (imagem 1.06)
- RTTI: `PlayerIns` (vftable 0x2a2b338), `ReplayGhostIns` (0x2a2d190, deriva de PlayerIns: seu construtor 0xa39100 chama o construtor PlayerIns 0xa217a0), `ReplayManipulator` (0x29d5ae8), `ReplayRecorder`, `PlayerGameData`, `EquipGameData`, `ChrAsm`, `CSDisplayGhost`, `FrpgNetWanderingGhostDb`, pacote `tag_DP_REGULAR_REPLAY_GHOST`. Strings "Play Replay Ghost", "Create Replay Ghost", "compressedGhostData", "replayGhostIns!=NULL".
- Chamadores do construtor PlayerIns: 0xa058a0, 0xa05a80, 0xa06180 (fábricas junto ao código WorldChrMan) e os dois construtores ReplayGhostIns.
- Construtor ReplayGhostIns 0xa39100(this, ?, ?, replayData, type): armazena replayData em +0x2298, aloca um objeto de 0xa10 bytes em +0x2290 (0x7bfe80; hipótese: seu próprio PlayerGameData) e o preenche de replayData+0xd4 (0x7c4250) e da flag em replayData+0xc (0x7c4260).
- 0xa077e0: encontra slot livre (passo 0x38) numa tabela e chama 0xa057a0 → variante de construtor 0xa39280 (tipo 3), depois define `ghost+0x1a3c = 1`. Chamado de 0xa493c0 (código WorldChrMan).
- A criação do criador de depuração (0xa492e0) passa por 0xa075d0, não pelo caminho de replay; com modelo c0000 constrói personagem sem dados de jogador, causando as falhas das execuções 31–32.

### <a id="sekiro-online-205-owner-provided-dinput8dll-sha-256-b40dd9c3-kept-in-local"></a>Sekiro Online 2.05 (dinput8.dll fornecida pelo proprietário, SHA-256 b40dd9c3…, mantida em local/)
- readme: LukeYui, P2P por Steam, servidor de invocação para sinais, até 6 jogadores, sincronização de mundo/eventos/inimigos. Sem texto de licença. Compilado em 2021-06-10 (PE stamp 0x60c26c70); não empacotado.
- Estaticamente, contém só endereços absolutos de globais do jogo (WorldChrMan 0x3d7a1e0 ×23, SoloParamRepository 0x3d978b0, outros); chamadas a funções do jogo não aparecem como constantes e suas strings são parcialmente ofuscadas por XOR. Descobrir seu caminho de criação exige rastreamento dinâmico. Paramos aqui; não copiamos seu código.

### <a id="derived--next"></a>Deduzido / próximo
- Um boneco com aparência de Wolf é PlayerIns (ou ReplayGhostIns) com seu próprio PlayerGameData. Próximo: mapear argumentos de 0xa058a0 / 0xa05a80 / 0xa06180 (slot de jogador de rede?), ou construir bloco mínimo de replay para 0xa077e0 e conduzir o fantasma com nossas chamadas de teleporte/animação.

### <a id="net-player-path-offline-and-run-33-plan"></a>Caminho de jogador de rede (offline) e plano da execução 33
- `0xa7a840` (código de rede) → `0xa49460(WorldChrMan, id, data)` → `0xa07960(WorldChrMan+0x40, id,
  data)`: primeiro slot de jogador livre a partir do índice 1 (slot 0 = local; passo de slot 0x38) → `0xa05a80` → construtor PlayerIns `0xa217a0(this, init, data)`, que armazena `[data+8]` em `PlayerIns+0x2000` (hipótese: PlayerGameData, como PlayerIns+0x1FA0 de DS3). Depois vt[+0x6e8](chr, 0x2a0b0c0).
- Globais do jogo: GameDataMan 0x3d5aac0 (código de equipamento 0x9cbf0e lê `[GameDataMan]+8` → +0x278); Sekiro Online o referencia 11 vezes.
- Execução 33 (`SEKIRO_COOP_SPAWN_PLAYER=1`): registrar Hero+0x2000 contra `[GameDataMan]+8`; se iguais e os bytes de 0xa49460 corresponderem, chamá-lo com data = {id 1, PlayerGameData do Hero} e fixar o resultado (lógica/equipe intactas, passagem direta de animação ligada).

### <a id="run-33-2026-10-28-0308-playerins-created-then-crash"></a>Execução 33 (2026-10-28 03:08): PlayerIns criado, depois falha
- Log: Hero+0x2000 = `[GameDataMan]+8` (PlayerGameData confirmado); contagem de slots WorldChrMan+0x40: 6; 0xa49460 retornou PlayerIns (vtable 0x2a2b338), handle = handle Hero + 1, char id 0.
- Falha ~0,3 s depois: sekiro.exe 0x803bfd em 0x803a00: `chr->vt[+0x308]()` (0xa2a0f0, retorna PlayerIns+0x21f8) era nulo. O construtor copia +0x21f8 de data+0x18.
- Layout de dados lido do construtor: +0 int id, +4 int tipo de manipulator (0x7f8480: 0 ChrManipulator, 1 PadManipulator, 2 NetworkManipulator, 3 ReplayManipulator, 5 NetAIManipulator; vftables 0x29d2ae0 / 0x29d4b30 / 0x29d4530 / 0x29d5ae8 / 0x29d3eb8), +8 PlayerGameData, +0x10 opcional, +0x18 → +0x21f8, +0x20 → +0x2260. O manipulator fica em ChrIns+0x58.
- Execução 34: preencher +0x18 e +0x20 com os próprios valores do Hero (objeto compartilhado), tipo 0; registrar vtable de +0x21f8 do Hero e vtable do manipulator.

### <a id="run-34-2026-10-28-0313-second-wolf-exists-no-animations"></a>Execução 34 (2026-10-28 03:13): segundo Wolf existe, sem animações
- Campos Hero: objeto +0x21f8 com vtable RVA 0x2b19648, +0x2260 = 0, manipulator Hero = PadManipulator (0x29d4b30). Com data +0x18/+0x20 copiados do Hero e tipo de manipulator 0 (ChrManipulator), 0xa49460 criou um PlayerIns (handle Hero+1) e o jogo NÃO falhou.
- Proprietário: um fantasma (segundo Wolf) apareceu, mas não mostrava animações.
- Log: 1472 passos, 176 teleportes, 21 redefinições de animação, 18 chamadas ForcePlayAnimation, 0 recusadas; 300 ms depois, o ID de animação PlayerIns lia 0 (ou 790010 / 200000), nunca o ID forçado.
- Deduzido: num PlayerIns, ForcePlayAnimation (0xbd84c0) não inicia animações de jogador; movimentos vêm do script de comportamento alimentado pelo manipulator (Pad para jogador local, NetworkManipulator para remotos no estilo DS3).
- Próximo: tentar tipo 2 (NetworkManipulator) e descobrir o que lê; ou alimentar o manipulator do boneco com a entrada de controle do remoto para o próprio comportamento do jogo reproduzir os movimentos.

### <a id="run-35-plan-input-copy"></a>Plano da execução 35: cópia de entrada
- Layout base de ChrManipulator de seu construtor 0x7e3220 (0x340 bytes): vetores em +0x10..+0x50, +0x60, +0x80..+0xe0; dois arrays de 81 bytes +0xf4 e +0x145; 81 dwords em +0x198; escalares até +0x2fc; +0x300 qword (ponteiro?) e +0x310..+0x330.
- `SEKIRO_COOP_PUPPET_INPUT_COPY=1`: a cada passo, copiar bytes +0x10..+0x300 do manipulator Hero (+0x58, PadManipulator) para o do boneco PlayerIns (tipo 0, ChrManipulator). `NOPOS=1`: um teleporte ao lado do Hero, depois nenhuma gravação de posição, para somente a entrada movê-lo. Só teste local (sem atraso de rede): o boneco deve copiar imediatamente os movimentos do proprietário.

### <a id="run-35-2026-10-28-0321-input-copy"></a>Execução 35 (2026-10-28 03:21): cópia de entrada
- Proprietário: segundo Wolf vira com ele, mas fica parado, sem animações; quando ataca, aparece barra de postura como se tivesse sido atingido (hipótese: PlayerGameData / objeto +0x21f8 compartilhado).
- Log: cópia do manipulator executou (src PadManipulator 0x29d4b30 → dst ChrManipulator 0x29d2ae0); vetor de movimento +0x10 copiado (por exemplo, [-0.52, 0, -0.85]); primeiros 16 bytes de ação em +0xf4 permaneceram 0; animação do boneco era 790010 (ociosa), então seu sistema de animação executa.
- Caminho de rede após 0xa49460 (0xa7a8cc..): `0x9f5170(chr, type)` (ChrIns+0x70 = type, depois 0x9f64d0), `chr->vt[+0x90]()` (PlayerIns 0xa23790), tipos 1/2/12 limpam bit 3 de +0x1a11, depois 0x89bb20(…, handle, type, 1, -1, -1, 0) e teleporte inicial perto do Hero.
- Execução 36: fazer essas etapas após criação (tipo 1), manter cópia de entrada, registrar ChrCtrl+0x120/+0x358.

### <a id="run-36-2026-10-28-0328-post-create-steps-make-it-invisible"></a>Execução 36 (2026-10-28 03:28): etapas após criação o tornam invisível
- Etapas executaram (tipo 1, vt+0x90 OK, ChrIns+0x70 = 1, equipe virou 2). PlayerIns estava ~5 m do Hero (posição no log), mas o proprietário não o via. Hipótese: tipo 1 (fantasma branco) exige configuração de renderização de fantasma, ou vt+0x90 / bit +0x1a11 o oculta.
- ChrCtrl+0x120 = ChrIns+0x58 tanto para Hero quanto boneco (+0x358 nulo): a cópia foi ao manipulator usado por ChrCtrl. Ainda sem movimento na execução 35. Hipótese: consumidor chama getters virtuais do manipulator; os getters base de ChrManipulator ignoram campos copiados (PadManipulator os sobrescreve). Próximo: tipo 2 (NetworkManipulator) e sua fonte de dados, ou copiar para boneco tipo PadManipulator com leitura do controle desativada.
- run-net.cmd voltou ao boneco Owl; run-wolf.cmd mantém teste PlayerIns.

## <a id="state-at-pause-2026-10-28-0330"></a>Estado na pausa (2026-10-28 03:30)
- Funcionando: Owl (c5060) criado pelo ChrCreator de depuração como boneco inofensivo conduzido pela rede: segue, vira, golpes de combo / bloqueio / aparar / esquiva mapeados (observado pelo proprietário, simulador em loopback).
- Em andamento: boneco com aparência de Wolf pelo caminho de jogador de rede do jogo (PlayerIns criado, estável sem etapas posteriores, ainda sem animações).
- Não iniciado: retransmissão Steam, teste com dois PCs, QA automatizado.

### <a id="run-37-plan-playerins-with-a-padmanipulator"></a>Plano da execução 37: PlayerIns com PadManipulator
- run-wolf.cmd: tipo de manipulator 1 (PadManipulator, construtor 0x7ed3a0), sem etapas após criação, sem cópia de entrada, NOPOS (um teleporte ao lado do Hero). Pergunta: um segundo PlayerIns com seu próprio PadManipulator se move pelo controle local? Se sim, o próximo passo é alimentar a leitura de controle desse manipulator com a entrada do remoto.

### <a id="run-37-2026-10-28-0334-playerins-with-padmanipulator"></a>Execução 37 (2026-10-28 03:34): PlayerIns com PadManipulator
- Proprietário: todo controle passou ao clone (ele movia e agia pelo controle; o próprio personagem parou de responder). Portanto, um segundo PlayerIns com PadManipulator anima e age plenamente; a fonte de entrada é a única parte ausente.
- Vtables de manipulators (1.06): Pad sobrescreve slots base 0x0 (atualização: 0x7f2210 → 0x7ef930 salvo se global 0x3d5b4a8 definida), 0x8 (destrutor), 0x38, 0x48, 0x50, 0x58, 0xa0, 0xa8, 0xb0; Network sobrescreve 0x0, 0x8, 0x48, 0xb0, 0xc0–0xd0, 0xf0, 0x100–0x130. PadManipulator (0x450 bytes) possui subobjetos em +0x350 (0x4f30 bytes, construtor 0x8d4780) e +0x358 (0x26a8, 0x8d45a0). Vtable Pad tem 46 slots.
- Execução 38: copiar a vtable Pad somente para o manipulator do clone, substituindo slot 0 por nossa função que copia os campos processados do manipulator Hero (+0x10..0x300, 0x310..0x340, 0x360..0x410, 0x420..0x428, 0x438..0x450) em vez de ler o controle. Esperado: proprietário mantém controle, clone o espelha.

### <a id="run-38-2026-10-28-0338-clone-mirrors-the-owner-locally"></a>Execução 38 (2026-10-28 03:38): clone espelha o proprietário localmente
- Proprietário: seu personagem volta a obedecer, e o clone repete os movimentos. Mantendo bloqueio: clone volta à postura normal após alguns segundos (hipótese: estado de manutenção vive nos subobjetos PadManipulator +0x350/+0x358, não copiados).
- => Um segundo jogador com aparência de Wolf que reproduz os próprios movimentos do jogo funciona localmente: PlayerIns por 0xa49460 + PadManipulator (tipo 1) + troca de slot 0 na vtable por objeto.

### <a id="run-39-plan-the-same-over-the-network"></a>Plano da execução 39: o mesmo pela rede
- Novo pacote `ManipState { frame, bytes }` (campos PadManipulator Hero nos intervalos de cópia, ~1 KB, a cada tick). Slot 0 do clone copia o último estado recebido (< 500 ms), senão limpa a entrada. Simulador espelha ManipState com o mesmo atraso de 500 ms. Posição: entrada conduz o clone; teleporte nativo à posição remota só com erro > 1,5 m (ou > 3 m de altura), no máximo a cada 250 ms. Formato de rede alterado (DLL e simulador recompilados juntos).

### <a id="run-39-2026-10-28-0342-no-session-clone-at-the-origin"></a>Execução 39 (2026-10-28 03:42): sem sessão, clone na origem
- Processo do simulador vivo (tasklist), mas não gravava nada; DLL recebia 10054 em toda tentativa de sessão, então não chegavam snapshots nem ManipState (remote_fresh 0, manip rx 0).
- Clone criado na origem do mundo (x 0, z 0) e, sem posição remota, nunca moveu para perto do Hero; seu slot 0 de manipulator nunca foi chamado (clone_updates 0). Hipótese: personagens distantes não são atualizados.
- Correções: em modo de correção, teleportar clone uma vez ao lado do Hero; scripts esperam o log do simulador mostrar "peer-simulator starting" (até 30 s) antes de iniciar o jogo.

### <a id="run-40-2026-10-28-0346-clone-visible-animations-but-teleports"></a>Execução 40 (2026-10-28 03:46): clone visível, animações, mas teleporta
- Sessão ativa; ManipState recebido 367 vezes; 25 correções de posição; clone_updates = 0 e remote_manip_used = 0: nossa substituição do slot 0 da vtable Pad nunca foi chamada.
- Proprietário: clone repetia animações, mas teleportava em vez de andar.
- Deduzido (revê execução 38): movimentos do clone não vêm de nossa cópia. Slot 0 da vtable Pad (0x7f2210: retorna global 0x3d5b4a8, senão 0x7ef930) parece getter de dispositivo, não atualização por quadro. Clone provavelmente lê o controle local pelos próprios subobjetos PadManipulator (+0x350, construtor 0x8d4780; +0x358, construtor 0x8d45a0), agindo imediatamente enquanto correções o puxam à posição remota atrasada, causando teleportes.
- Próximo: encontrar onde esses subobjetos leem o controle (ou qual método preenche campos do manipulator a cada quadro) e alimentar ali o estado remoto somente para o clone.
- Atualização ChrCtrl (0x7dee05): manipulator = ChrCtrl+0x358 ou +0x120; se vt[+0xf0]() (ou bits de lógica) → vt[+0x48](this, dt, ChrCtrl, 0), senão vt[+0x50](this, dt, ChrCtrl). Sobrescritas Pad: 0x7ef120 / 0x7ef300. Estas são as atualizações por quadro.
- Execução 41: vtable do clone envolve slots 0x48 e 0x50: chamar original e então sobrescrever intervalos de cópia com último ManipState remoto (ou limpar se nenhum recente).

### <a id="run-41-2026-10-28-0350-update-wrappers-work-still-teleports"></a>Execução 41 (2026-10-28 03:50): wrappers de atualização funcionam, ainda teleporta
- Log: clone_upd_calls = remote_manip_used (1432 no fim): atualização envolvida executou e aplicou estado remoto sempre (slot 0 ainda nunca chamado). ManipState chegou ~12/s (simulador reproduz no máximo uma entrada vencida por tick). 31 teleportes em ~40 s (erro > 1,5 m).
- Proprietário: clone ainda teleporta.
- Execução 42: abaixo de 4 m, ajustar posição bruta em 4% do erro por passo (quando > 0,3 m); teleporte nativo só além de 4 m ou 3 m de altura; registrar distância do clone à posição remota.

### <a id="run-42-2026-10-28-0353-nudges"></a>Execução 42 (2026-10-28 03:53): pequenos ajustes
- Proprietário: teleportes mais suaves, mas clone ainda não anda (sem animação de caminhada/corrida).
- Execução 43a/b: `run-wolf.cmd - none` (sem sobrescrita: atualização de controle do clone preservada; espera-se andar imediatamente pelo controle local) e `run-wolf.cmd - base` (sobrescrever só parte ChrManipulator < 0x340). Indica se caminhar vem dos campos sobrescritos ou de outro lugar.

### <a id="run-43-2026-10-28-0358-none--base"></a>Execução 43 (2026-10-28 03:58): none / base
- Proprietário: em ambos os modos clone desliza, às vezes dá saltos, sem animação de caminhada. Mesmo sem sobrescrita, clone agora não anda. Hipótese: nossa substituição de slot 0 (retorna 0; slot 0 parece getter do dispositivo de controle) deixa a atualização do clone sem dispositivo, e locomoção vem do estado nos subobjetos PadManipulator, não dos campos base.
- Execução 44 (run-wolf-local.cmd, sem rede): NOPOS, copiar do manipulator Hero a cada atualização, mais subobjetos +0x350 (0x4f30) e +0x358 (0x26a8) qword a qword, ignorando qwords que sejam ponteiros legíveis em qualquer objeto.

### <a id="run-44-2026-10-28-0401-sub-object-copy"></a>Execução 44 (2026-10-28 04:01): cópia de subobjetos
- Proprietário: clone não anda nem mantém bloqueio; FPS caiu a 16 (varredura qword com VirtualQuery a cada atualização). Log: 420 atualizações envolvidas, 840 cópias de subobjetos, ID de animação do clone 0. Abandonado.
- Execução 45 (run-wolf-local.cmd): manter slot 0 da vtable Pad (sem substituição), wrappers ligados sem sobrescrita (intervalos none), NOPOS. Pergunta: clone anda com seu dispositivo de controle e proprietário mantém controle (na 37 sem wrappers ele o perdeu)?

### <a id="run-45-2026-10-28-0405-slot-0-kept-no-overwrite"></a>Execução 45 (2026-10-28 04:05): slot 0 mantido, sem sobrescrita
- Proprietário: clone ainda não anda. Observa que clone tem braço protético enquanto seu personagem (salvamento inicial) ainda não. Hipótese: clone não totalmente inicializado (aparência de padrões, movimento talvez bloqueado por estado definido na inicialização do caminho de rede).
- Execução 46: etapas após criação (0x9f5170 type + vt+0x90) com tipo 0 em vez de 1 (tipo 1 o tornou invisível na 36), sem sobrescrita, slot 0 mantido.

### <a id="run-46-2026-10-28-0409-init-with-type-0"></a>Execução 46 (2026-10-28 04:09): inicializar com tipo 0
- Proprietário: clone visível, sem brilho de fantasma, agora sem prótese (corresponde ao personagem); seu personagem obedece; clone ainda não anda. Além disso: na execução 37 clone deslizava com pequenos saltos e nunca dava passos. Portanto animação de locomoção nunca funcionou nele, qualquer que fosse a entrada; ações (ataques, bloqueio) tocam.
- Vftables `WalkAnim` / `WalkAnim_Enemy` 0x29d6170 / 0x29d6240 só referenciadas por 0x7f57e0 (registra callbacks; parece conexão de menu de depuração), não são pista.
- Execução 47: comparação única de valores pequenos (< 0x10000) entre Hero e clone, ambos parados, em ChrIns (0x2300), ChrCtrl (0x600) e primeiros 32 módulos de +0x1ff8 (0x300 cada).

### <a id="run-47-2026-10-28-0414-hero-vs-clone-state-diff-both-standing"></a>Execução 47 (2026-10-28 04:14): comparação de estado Hero e clone (ambos parados)
- 400 valores u32 pequenos diferentes (limite atingido). Selecionados:
  - ChrIns: +0x78 hero 0xa000 / clone 0xa001; +0x128 4 / 0; +0x10ec 1 / 0; +0x2040 4 / 6; +0x2224 2 / 0; +0x1210..+0x1990 tabela preenchida para Hero, vazia para clone.
  - ChrCtrl (+0x50): +0x8 0 / 6; +0x118 0 / 5; +0x2c4 1 / 0; +0x408 6 / 0x16; muitos bytes +0x414..+0x5f4 definidos como 1 para Hero, 0 para clone (tabela por ação).
  - Módulos +0x1ff8: diferenças em módulos 0x8–0x70 (maioria no módulo 0x10 = TimeAct, 66).
- Execução 48: copiar ChrIns +0x78, +0x128, +0x10ec Hero → clone uma vez (15 s após fixação), registrar antigo/novo.

### <a id="runs-48-49-2026-10-28-0420-0426"></a>Execuções 48–49 (2026-10-28 04:20–04:26)
- Execução 48: ChrIns +0x78, +0x128, +0x10ec copiados Hero → clone: ainda sem caminhada.
- Execução 49: salvamento principal do proprietário (S0000.sl2 da conta Steam) copiado sobre coop-test.sl2 (backup do salvamento de teste como coop-test.sl2.bak-20261028; S0000.sl2 só lido). Ainda sem caminhada.
- Situação: clone PlayerIns reproduz ações (ataques, bloqueio) e muda de posição, mas nunca entra em animações de locomoção, com qualquer fonte de entrada, tipo de inicialização 0/1 ou salvamento. Hipótese: variáveis de comportamento que selecionam caminhada/corrida (nível de velocidade etc.) são gravadas por caminho exclusivo do jogador local ou vêm do caminho de rede (NetworkManipulator) para remotos.
- Próximo (offline, sem execuções): encontrar quem grava variáveis de comportamento de locomoção do jogador e sua condição; comparar com sobrescritas NetworkManipulator (0x29d4530: slots 0x48, 0xb0, 0xc0–0xd0, 0xf0, 0x100–0x130).

### <a id="offline-where-locomotion-comes-from-2026-10-28-0440"></a>Offline: de onde vem a locomoção (2026-10-28 ~04:40)
- Tabela de descritores de variáveis de comportamento em 0x3b08e10 (passo 0x10: ponteiro do nome, flags): "Behavior", "Init_wild", depois IsLockon, MoveAngle, MoveSpeedLevel, MoveDirection, TurnAngle, IsEnableFootIk, IK de mão, AddBlend00–09, OriginalityAddBlend00–04, JumpAngle, JumpStickLevel, AttackAngle, AttackStickLevel, ... (nomes UTF-16 em 0x2a77210+). Usuários: 0xb41480/0xb414f0 (+0x3b08e10), 0xb3cef0, 0xb442c0 (redefinição de animação), 0xb46380, 0xb46820 (+0x3b08e18 → 0xff1cd0 o vincula), 0xb463e0 / 0xb46870 (+0x3b08e28). Campo +0xd04 do módulo de animação = variante de comportamento.
- Ligações HKS: "env" → 0x1404c00 → ponteiro do tratador 0x3ead050 = 0x1010a60 (instalado por 0x1010450, com "act" 0x3ead058 = 0x1010790); "hkbFireEvent" registrado em 0x13f78c0.
- Deduzido: HKS do clone executa (ações tocam), então escolher caminhada/corrida depende de variáveis de comportamento como MoveSpeedLevel/MoveAngle que ele nunca recebe. Plano: encontrar armazenamento de valores hkb em runtime (módulo de comportamento → hkbCharacter → grafo de comportamento → valores de variáveis), comparar Hero e clone enquanto Hero corre, depois enviar essas poucas variáveis e gravá-las no clone a cada quadro. Nenhuma execução ainda.

### <a id="run-50-2026-10-28-0434-behavior-variable-scan"></a>Execução 50 (2026-10-28 04:34): varredura de variáveis de comportamento
- Percurso de ponteiros dos módulos Hero 0x10/0x28/0x58, profundidade 3, 4001 objetos; floats 0 parado e 0,5–3 correndo: 300 resultados (limite). Valor do clone 0 no mesmo caminho, por exemplo `[[[bag+0x28]+0x20]+0x140]+0x344` Hero 2,0 (parecido com MoveSpeedLevel), `...+0x128]+0x5c` 0,5, `[[[bag+0x58]+0x30]+0x188]` vários 2,41, `[[[bag+0x58]+0x160]+0x3d8]+0x60/+0x68` -0,68/0,73 (direção?).
- Hipótese: `[bag+0x28]+0x20` é o personagem Havok de comportamento; +0x140/+0x148 um hkArray de valores de variáveis (dados, tamanho).
- Execução 51: na atualização envolvida do manipulator do clone, copiar todo o array de variáveis Hero para o clone (mínimo dos tamanhos); registrar ambos os tamanhos.
- Execução 51: nenhuma cópia (bvar_copies 0): verificação de tamanho +0x148 rejeitou array. Execução 52: copiar 0x400 bytes fixos de `[X+0x140]` (o que a varredura leu) e registrar cabeçalho em X+0x148.
- Execução 52: cabeçalho em X+0x148 = tamanho 0x58, capacidade 0x158, mas `[X+0x140]` = 0x970000002c (não ponteiro): caminho da varredura não estável; cópias 0 novamente.
- RTTI: hkbVariableValueSet vftable 0x2c14748, hkbBehaviorGraph 0x2c14788 (vista +0x38: 0x2c14870), hkbCharacter 0x2c408b0.
- Execução 53: encontrar objetos hkbVariableValueSet por vtable a partir do conjunto de módulos (profundidade 5, ≤ 6000 objetos, uma vez por personagem, registrado), copiar array de palavras do Hero (+0x10, tamanho +0x18) e array quádruplo (+0x20, tamanho +0x28) para o clone em cada atualização envolvida.

### <a id="run-53-2026-10-28-0446-the-clone-has-no-hkbvariablevalueset"></a>Execução 53 (2026-10-28 04:46): clone não tem hkbVariableValueSet
- Hero: dois objetos hkbVariableValueSet alcançáveis do conjunto de módulos (0x32ce9320, 0x26816b30). Clone: nenhum (mesma busca). Busca executou na thread do jogo e congelou-o por ~15–20 s; wrapper de atualização do clone executou uma vez; nenhuma cópia.
- Deduzido: clone PlayerIns não tem instância de grafo de comportamento Havok com variáveis (ou não é alcançável da mesma forma). Suas ações tocam, mas locomoção, selecionada pelo grafo a partir de variáveis, não pode. Isso explica toda execução desde a 34.
- Próximo (offline): comparar a criação do jogador local (chamadores do construtor PlayerIns 0xa058a0 por 0xa078a0, 0xa06180 por 0xa05ce0 ← 0xa080f0/0xa08430/0xa50120) com o caminho de jogador de rede usado (0xa05a80), e encontrar onde o grafo de comportamento do jogador (c0000 hkx) é instanciado. Faça buscas assim na thread ticker, nunca na thread do jogo.

### <a id="offline-0450-player-creation-paths-are-the-same"></a>Offline (04:50): caminhos de criação do jogador são iguais
- Jogador local: 0xa493d0 (WorldChrMan, define +0x88) → 0xa078a0 (slot 0) → 0xa058a0, dados construídos por 0x7f8730: {id, tipo 1 (Pad), [GameDataMan]+8, +0x10 0, +0x18 [0x3d67408]+0x31e0, +0x20 0} → construtor PlayerIns 0xa217a0 → vt[+0x6e8](chr, 0x2a0b0c0). Nosso clone recebe o mesmo formato de dados (+0x18 copiado de Hero+0x21f8) por 0xa49460. Chamado pela rotina de início do jogo 0xa73430.
- Classes de comportamento (RTTI): SprjChrBehaviorModule 0x2a790a8, SprjChrBehaviorSyncModule 0x2a7a7f8, SprjChrBehaviorScriptModule 0x2a7a3b8, SprjChrBehaviorDataModule 0x2a76c20. Chamadores do construtor Havok hkbCharacter levam a 0x100c570 (← 0xffb350, 0xffb8f0).
- Execução 54: registrar conjuntos de módulos Hero e clone por vtable e primeiros campos do módulo de comportamento.

### <a id="run-54-2026-10-28-0452-module-bags"></a>Execução 54 (2026-10-28 04:52): conjuntos de módulos
- Hero e clone têm mesmos módulos nos slots 0x0–0x118 (inclusive 0x8 SprjChrBehaviorScriptModule, 0x28 SprjChrBehaviorModule, 0x30 SprjChrBehaviorSyncModule, 0xb8 SprjChrBehaviorDataModule), e os primeiros campos do módulo de comportamento contêm os mesmos tipos (+0x18 SprjBehaviorCharacterProxyDriver, +0x20 CSBehRaycastInterface, +0x28 SprjFD4LocationHkaPoseImporter).
- Só Hero tem: 0x120 NtcChrHitWallModule, 0x128 CSChrDockingModule, 0x138 CSWireActionHitChangeModule (extras do jogador local).
- Portanto clone realmente tem módulo de comportamento; o "sem hkbVariableValueSet" da execução 53 provavelmente foi o limite de busca. Locomoção bloqueada em outro lugar: candidatos são módulos locais ausentes ou verificação de jogador local nas funções HKS env usadas para movimento.

### <a id="offline-0500-islocalplayer"></a>Offline (05:00): IsLocalPlayer
- Módulos exclusivos locais são criados em 0xa34c90 (configuração de módulos PlayerIns, chamada de 0xa39750) sob `0x9f3430(chr)` = `[WorldChrMan]+0x88 == chr` (IsLocalPlayer): HitWall por 0xbd9160 (slot 0x24 → bag+0x120), WireActionHitChange por 0xbd9890 (0x27 → +0x138), Docking por 0xbd8da0. 0x9f3430 tem ~260 pontos de chamada; vt+0x90 de PlayerIns (0xa23790) também a chama.
- `ModuleSyncBehaviorTestStep` (teste de depuração: STEP_Init 0xaeaa40, Update 0xaead70, Finish 0xaea860) exercita SprjChrBehaviorSyncModule; não acompanhado além disso.
- Execução 55: interceptar 0x9f3430 (verificada por bytes) para retornar true ao clone (demais inalterados).

### <a id="run-55-2026-10-28-0458-clone-as-local-player"></a>Execução 55 (2026-10-28 04:58): clone como "jogador local"
- Hook instalado; 0x9f3430 respondeu true para clone 32.585 vezes; sem efeitos colaterais visíveis (câmera, HUD, controle do proprietário normais). Clone ainda não andava.
- Wrapper de atualização do manipulator do clone executou só 124 vezes (execuções 41–43: ~800–1400), então atualização ChrCtrl do clone pode ser rara (LOD de atualização / limitação?) — nova pista: se atualização de personagem é limitada, comportamento/locomoção não avançariam.
- run-wolf-local.cmd tem hook desativado novamente.
- Próximo: conferir a frequência de atualização ChrIns / comportamento do clone contra Hero (contar chamadas por segundo) e o que decide a taxa de atualização de um personagem.
- Proprietário (05:01): há algum tempo (execuções locais, sem gravação de posição), clone nem desliza; só fica parado. Nessas execuções nada o movia: sua entrada não era processada. O deslizamento anterior vinha de nossos teleportes/ajustes (execuções de rede) e, na 37, do controle compartilhado. Compatível com a pista de atualização limitada (124 atualizações de manipulator numa execução).

### <a id="offline-0505-update-omission"></a>Offline (05:05): omissão de atualização
- Strings "OmissionUpdateNum.Near/Far", "All Omission Mode", "IsOmission"; comando de script `ChrCmd_ForceSetOmissionLevel(int, bool, int)` (vftable 0x29ac838, 0x7543e0 → EventChrEntity vt+0x1e0 = 0x74fae0): se ChrIns+0x1ff0 == -2, bit 0 de ChrIns+0x1a10 = force, ChrIns+0x110 = level. Personagens com omissão só atualizam a cada vários quadros.
- Execução 56: a cada passo definir +0x110 do clone com o valor do Hero e bit 0 de +0x1a10; registrar os valores dos dois uma vez.
