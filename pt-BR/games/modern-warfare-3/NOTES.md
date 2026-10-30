# Modern Warfare 3 (2011) - notas da sessão

Data da sessão: 2026-10-18. Estado do repositório: captura ZIP de `main` (git/gh instalados no fim, ainda não usados). Pedido do usuário: "Quero jogar MW3 (2011) em modo cooperativo com amigos."

## <a id="game-identity-triagemd-step-1--agentsmd-rule-5"></a>Identidade do jogo (triage.md etapa 1 / AGENTS.md regra 5)

- Título: Call of Duty: Modern Warfare 3 (2011), Steam
- Appids Steam: 42680 (um jogador: campanha + Spec Ops, buildid 24615914), 42690 (multiplayer, buildid 24615796)
- Última atualização no PC do usuário: 2026-10-03 09:06:47 UTC
- Executáveis principais:
  - `iw5sp.exe` - 5.625.400 bytes, SHA-256 `A97D2BBC…E8DC1023`
  - `iw5mp.exe` - 6.167.104 bytes, SHA-256 `E4E9531D…5784B286`
- Motor: IW 5.0 (binário fechado). Organização: arquivos `main\*.iwd`, `zone\`, `players2\`
- Sistema: Windows 10 10.0.19045
- Caminhos locais exatos: mantidos em `local/` (privados, conforme AGENTS.md)

## <a id="observations-facts-with-sources"></a>Observações (fatos com fontes)

- Captura do repositório contém **zero** cobertura de Call of Duty: busca sem diferenciar maiúsculas por `duty|warfare|treyarch|infinity ward` no repositório inteiro → 0 resultados (2026-10-18). Portanto, jogo ainda não coberto: precisa de issue indicando trabalho e entrada no diretório.
- `engine-families.md` **não tem linha** da família IW/id Tech de CoD. Lacuna a propor na PR.
- **AlterWare IW5-Mod**: cliente MW3 atual, focado principalmente em um jogador/cooperativo, mais "Bot Warfare" em partidas multiplayer privadas, mods GSC, servidores dedicados, correções de segurança (https://forum.alterware.dev/t/iw5-mod-install-guide/462, https://alterware.dev/). Exige cópia Steam adquirida. Organização ativa em outubro de 2026.
- Política de código AlterWare: IW5-Mod é fechado, embora baseado em trabalho licenciado em MIT (https://forum.alterware.dev/t/why-is-iw5-mod-closed-source/463); README GitHub aponta Gitea próprio (https://git.alterware.dev/alterware), que retornou HTTP 500 em 2026-10-18.
- **Plutonium IW5**: só multiplayer, exige conta (https://docs.cbservers.xyz/games/iw5; FAQ ModDB abaixo confirma).
- **iw5_bot_warfare** (GitHub: inedbots): mod GSC para PlutoniumIW5, com bots de IA reais no multiplayer. Candidato ao requisito de QA automatizado com bots controlando clientes reais.
- **TeknoMW3** (TeknoGods): cliente antigo com LAN/IP direto para multiplayer e Spec Ops; usuários ainda citam em 2026 (ModDB, 2026-03-12). Histórico associado a comunidades próximas à pirataria → cautela jurídica pela regra 10; preferir AlterWare.
- **MW3 Survival Mode: Revived** (ModDB, FreakingNewGuy): lançado em 2026-01-09, ativo (arquivos até outubro de 2026), exige AlterWare, somente Steam. FAQ diz que não funciona em cooperativo: conectar à partida Spec Ops de outro jogador causa dessincronização para ambos (https://www.moddb.com/mods/mw3-survival-mode-revived).
- Arquivo ModDB "MW3 Downgrader [FIX ALTERWARE]" (GalvarinoDev v1.2.1, enviado por volta de 2026-10-18): diz que, para corrigir compatibilidade e usar mods Survival novamente, talvez seja necessário desinstalar Modern Warfare (texto truncado na listagem). Portanto, atualização Steam recente quebrou AlterWare; existe ferramenta de retorno de versão. Instalação do usuário atualizada em 2026-10-03.
- **open-iw5** (GitHub: Rackover): cliente MW3 de código aberto para um jogador/multiplayer; autor diz ser muito experimental, inacabado e provavelmente nunca será concluído.
- Existe guia Steam "How to play Multiplayer / Spec Ops with your friends" (Hamachi), sugerindo que a criação de sala Spec Ops funcionou na versão PC em algum momento (https://steamcommunity.com/sharedfiles/filedetails/?id=2953063348, 2023).
- Sinal de segurança: discussão Reddit "[MW3] 2011 Spec Ops DLC/RCE?" alerta sobre malware em salas/DLCs (conteúdo não acessível, Reddit bloqueia consulta automatizada; não verificado). AlterWare anuncia correções de explorações das versões Steam.
- Wiki: Spec Ops suporta até 2 jogadores, on-line e tela dividida (esta só em console): https://callofduty.fandom.com/wiki/Special_Ops/Modern_Warfare_3

## <a id="derived-my-conclusions-from-the-observations"></a>Deduções (conclusões das observações)

- Caminho 1 (concluir existente) = **AlterWare IW5-Mod** para Spec Ops + Survival cooperativo (2 jogadores on-line, cópias Steam dos dois). Sem código nosso para jogar; tarefa é verificar a compilação exata, documentar, empacotar e abrir PR.
- **Não existe campanha cooperativa MW3 em plataforma alguma nem projeto tentando** (não encontrado nas buscas abaixo). Criar = caminho 2 do zero: sem rede no modo de um jogador, binário fechado, sem descompilação → muito difícil (meses de horas de agentes); aplica-se modelo com autoridade do host como sm64coopdx.
- Atualização Steam de outubro de 2026 é maior risco de compatibilidade AlterWare; testar primeiro na compilação do usuário, IDs acima.
- Para QA posterior (regra 11 / playbook/automated-qa.md), Bot Warfare GSC no multiplayer AlterWare/Plutonium é caminho realista; Spec Ops exigiria dois clientes quase sem interface, questão aberta.

## <a id="guesses-labelled-unverified"></a>Hipóteses (identificadas, não verificadas)

- App de um jogador Steam (42680) quase vazio como segundo app talvez indique que a maioria dos dados é atribuída ao multiplayer (42690, 16,6 GB), embora ambos usem a mesma pasta.
- "IW5 SP Warfare" (YouTube, relacionado a AlterWare) talvez seja mod de combate no lado de um jogador; descrição inacessível, função exata desconhecida.

## <a id="unknowns"></a>Desconhecidos

- Se Spec Ops IW5-Mod funciona nos buildids 24615914 / 24615796 (após atualização de 2026-10-03): não testado.
- Se Spec Ops Steam original on-line ainda funciona em 2026: não testado.
- Texto de licença IW5-Mod: não declarada segundo discussão 463.
- Máximo de jogadores nas salas Spec Ops IW5-Mod: original 2; desconhecido se ampliado.
- Conteúdo/comportamento exato de "MW3 Downgrader": não executado nem obtido (exigiria autorização pelas regras 1/8 antes de baixar do ModDB).

## <a id="checks-that-actually-ran-this-session"></a>Verificações realmente executadas nesta sessão

- Busca sem diferenciar maiúsculas por termos CoD no repositório → 0 resultados.
- Listagem `games/` → 6 relatos, nenhum CoD.
- Manifestos 42680/42690 lidos; executáveis, tamanhos e SHA-256 calculados somente por leitura.
- Buscas: "MW3 2011 co-op mod", "TeknoMW3", "IW5x client", busca cooperativa em russo, "AlterWare IW5 status", "site:forum.alterware.dev iw5 sp warfare".
- Consultas: github.com/alterware, alterware.dev, discussões do fórum (busca bloqueada), moddb.com/mods/mw3-survival-mode-revived (sucesso), Reddit (bloqueado), vídeo YouTube (sem descrição retornada).

## <a id="session-2-2026-10-18-continued--owner-decision--phase-23-progress"></a>Sessão 2 (continuação de 2026-10-18) - decisão do usuário e progresso nas etapas 2/3

Decisão: **campanha cooperativa, criar do zero (caminho 2)**. Spec Ops/AlterWare permanece referência útil, mas não é o objetivo.

### <a id="phase-2-workspace--done"></a>Etapa 2 (ambiente) - concluída

- Cópia isolada autorizada e criada: `<test copy>` por robocopy `/E /COPY:DAT` (296 arquivos, 15,512 GB, saída 1 = sucesso). Original intacto.
- Ferramentas instaladas (autorizadas, winget): Git 2.55.0.5, GitHub CLI 2.102.0, Python 3.13.15.

### <a id="phase-3-understand--new-finds-verified-by-fetch-2026-10-18"></a>Etapa 3 (entender) - novas descobertas (consulta verificada em 2026-10-18)

- **open-iw5** (momo5502, cadeia de forks cydiakk → louvenarde; 590 commits; selo de compilação CI): cliente aberto de um jogador/multiplayer MW3, exige arquivos de servidor dedicado, muito experimental/inacabado. **GPL-3.0** (LICENSE consultada). https://github.com/louvenarde/open-iw5 — ancestral de IW5-Mod fechado (mesmo autor, discussão 463 cita momo5502). Base aberta viável; derivados precisam ser GPL-3.0. Contradição a resolver depois: fórum diz base MIT, enquanto open-iw5 é GPL-3.0; ancestrais diferentes são possíveis. Registrar, não adivinhar.
- **xensik/gsc-tool**: compila E descompila scripts IW5 PC, inclusive campanha. Extrair fastfiles exige Zonetool (https://github.com/ZoneTool/zonetool) ou Jekyll (https://github.com/EthanC/Jekyll). Uso: `gsc-tool -m decomp -g iw5 -s pc <file>`.
- **SyndiShanX/COD-GSC-Source**: GSC/CSC extraídos e formatados de vários CoD, incluindo `IW5-GSC/`; extraídos por Jekyll/ACTS, descompilados por gsc-tool. Referência conveniente; verificação por extração própria de `<test copy>` (regra 4).
- **ate47/atian-cod-tools (ACTS)**: caixa de ferramentas CoD usada pela comunidade (entrada/saída de fastfiles).

### <a id="phase-4-choose--provisional-direction-needs-owner-sign-off"></a>Etapa 4 (escolher) - direção provisória (exige aprovação do usuário)

Sincronização de estado com autoridade do host (guia §1.6: adaptações de motores fechados de um jogador quase sempre usam isso), com **fork GPL-3.0 open-iw5 como ponto de hook**, não injeção bruta de DLL no `iw5sp.exe` fechado:

- Alvo da etapa 1 da ordem de construção: fork inicia uma missão e registra posição, substituindo semanas de engenharia reversa às cegas, pois open-iw5 já analisou o motor.
- Scripts: lógica GSC em fastfiles; extrair/descompilar com Zonetool/Jekyll + gsc-tool da cópia; armazenamento de história (etapa 4) provavelmente acessível por GSC.
- Riscos de longo prazo: scripts supõem um jogador; entidades multiplayer no binário individual; barreiras de cenas/gatilhos (guia §1.5).

## <a id="next-actions"></a>Próximas ações

1. Mostrar rascunho de issue ao usuário; `gh auth login`; abrir issue de trabalho.
2. Clonar open-iw5 + COD-GSC-Source (Git disponível), auditar `src/` para início da campanha e mapas de símbolos.
3. Extrair/descompilar GSC da cópia (Zonetool/Jekyll exigem autorização para download, fontes oficiais fixadas).
4. Fork de cranebeaker/coop-anything, branch `game/modern-warfare-3`, entrada `data/directory.yaml`, relato em `games/modern-warfare-3/`, PR rascunho.
5. Ghidra em `iw5sp.exe` só onde os mapas não bastam (download grande, perguntar antes).

---

## <a id="session-2026-10-18-cont-2--fastfile-format-and-script-layer-verification"></a>Sessão de 2026-10-18 (continuação 2) - formato fastfile e verificação de scripts

Todo o trabalho abaixo usa `<test copy>` (caminho privado em `local/`). Nada na instalação real foi alterado.

### <a id="iw5-fastfile-ff-format--derived-from-openassettools-source-read-not-guessed"></a>Formato fastfile IW5 (.ff) - deduzido do código OpenAssetTools (lido, não adivinhado)

Lido em `Laupetin/OpenAssetTools` (GPL-3.0), arquivos `src/ZoneCommon/Game/IW5/ZoneConstantsIW5.h`, `src/ZoneLoading/Game/IW5/ZoneLoaderFactoryIW5.cpp`, `src/ZoneLoading/Loading/Steps/StepLoadZoneSizes.cpp`, `src/Common/Game/IW5/IW5.h`:

```
offset 0..7   magic (8 bytes)
              "IWffu100" = unsigned zone          <- every SP campaign zone we checked
              "IWff0100" = signed / official IW   <- every MP zone we checked
              "IWffs100" = RSA auth header (only inside signed zones)
offset 8..11  version, u32 LE, expected value 1
offset 12     1 unknown byte (the game ignores it too)
offset 13..20 timestamp, u64 LE
offset 21..   zlib (deflate) stream of the XFile payload   [unsigned zones]
              for signed zones an RSA-signed auth header sits here instead
```

Dados descomprimidos começam com `u32 size`, `u32 externalSize`, depois tabela XFile (9 blocos: TEMP, PHYSICAL, RUNTIME, VIRTUAL, LARGE, CALLBACK, VERTEX, INDEX, SCRIPT) e lista de recursos. Ponteiros são offsets com índice de bloco nos 4 bits superiores (`OFFSET_BLOCK_BIT_COUNT = 4`).

*Consequência:* zona IW5 sem assinatura é cabeçalho de 21 bytes e fluxo zlib. `zlib` padrão de Python descomprime zona inteira sem ferramenta externa.

### <a id="self-built-extraction-tools-this-session"></a>Ferramentas de extração próprias desta sessão

- `mw3-research/tools/ff_probe.py`: lê identificador mágico/versão/horário, descomprime zlib, escreve bloco XFile bruto.
- `mw3-research/tools/ff_scan.py`: varredura por regex no bloco descomprimido.

Executadas na cópia (todas eof=True, trailing=0: exatamente um membro zlib):

| Zona | Em disco | Descomprimida |
|---|---|---|
| `so_stealth_prague.ff` | 656,864 | 1,233,399 |
| `hijack.ff` | 198,766,636 | 300,445,645 |
| `payback.ff` | 173,775,764 | 290,792,230 |

### <a id="verification-of-the-third-party-gsc-dump-ground-rule-4"></a>Verificação da extração GSC de terceiros (regra básica 4)

`SyndiShanX/COD-GSC-Source` é extração descompilada, não nossa. Conferimos contra a cópia procurando, nas zonas descomprimidas, identificadores presentes nesses scripts:

- `hijack.bin` contém `hijack_airplane`, `tarmac_combat_wave`, `pre_zero_g`, `hijack_door_explosion`, todos em `COD-GSC-Source/IW5-GSC/scripts/maps/hijack.gsc`.
- `payback.bin` contém `payback_main`, `payback_util`, `sandstorm_code`, `payback_rescue`, todos em fontes `payback*.gsc`.

Identificadores das duas zonas coincidem; scripts da campanha extraídos correspondem à nossa cópia comercial russa. Nem todo identificador aparece literalmente: tabela IW5 compartilha prefixos/sufixos; fragmentos ficam uma vez (por exemplo, só `tarmac_combat_wave` para `..._wave2/3/4`).

### <a id="openassettools-unlinker-crashes-on-retail-iw5-zones-unresolved"></a>Unlinker de OpenAssetTools falha nas zonas IW5 comerciais (não resolvido)

Existe versão Windows pré-compilada; não foi necessário compilar. Baixado `oat-windows.zip` v0.33.0 (3.636.251 bytes), SHA-256 `4bf366cec03558a4b0f20bc8f197a51f4b9dad0aa3edc52b0e40fef2dd95a4f5` conferido com resumo da API de releases GitHub. Também obtidas v0.32.0 (`473b94f0…927a`) e v0.30.0 (`450d3b7a…ecb6`), ambas com hash verificado.

Comportamento na cópia, `Unlinker.exe --list <zone>`:

| Zona | Identificador mágico | Tamanho | Resultado |
|---|---|---|---|
| `sp_prague.ff` | IWffu100 | 207 | OK |
| `sp_intro.ff` | IWffu100 | 303 | OK |
| `so_trainer2_so_deltacamp.ff` | IWffu100 | 1,693 | OK |
| `code_pre_gfx.ff` | IWffu100 | 3,969 | OK |
| `code_pre_gfx_mp.ff` | IWff0100 | 24,597 | OK |
| `ui_mp.ff` | IWff0100 | 24,597 | OK |
| `patch.ff` | IWffu100 | 112,197 | OK |
| `ui.ff` | IWffu100 | 463,655 | OK |
| `code_post_gfx_mp.ff` | IWff0100 | 253,973 | **Falha** |
| `so_stealth_prague.ff` | IWffu100 | 656,864 | Falha |
| `hijack.ff` | IWffu100 | 198,766,636 | Falha |
| `common.ff` | IWffu100 | 137,962,380 | Falha |
| `common_mp.ff` | IWff0100 | 49,422,357 | Falha |

- Saída `-1073741819` = `0xC0000005`, violação de acesso, offset `0x002f2452` em `Unlinker.exe`, idêntico nas zonas que falham (eventos de aplicativos Windows e relatório WER, `ReportArchive\AppCrash_Unlinker.exe_…`).
- Determinístico (3/3 idênticas). Reproduzido em OAT 0.30.0, 0.32.0, 0.33.0; não é regressão recente.
- Falha *antes* de gravar qualquer saída, no carregamento, não extração. `--include-assets` não limita carregamento (continua falhando); não isola o tipo de recurso assim.
- Diferencial é conteúdo, não identificador ou tamanho bruto: `ui.ff` (463 KB, sem assinatura) carrega; `code_post_gfx_mp.ff` (253 KB, assinado) falha. Zonas pequenas/de patches carregam, mas aparecem vazias; só provam que o fluxo de etapas inicia.
- Estado: **causa raiz não encontrada**. OAT ainda não serve para extrair campanha. Se continuarmos: compilar com símbolos (VS Build Tools 2022 + C++ em instalação) e obter pilha ou executar testes unitários. Correção no projeto de origem seria contribuição real.

### <a id="other-fastfile-tools-ruled-out-for-iw5-2011"></a>Outras ferramentas fastfile descartadas para IW5 (2011)

- **ACTS** (atian-cod-tools) 3.3.0 inclui `data/games/mw3.json`, `mw3sp.json` e `acts-mw23.dll`; esse "mw3" é o reinício de **2023** (Modern Warfare III), não IW5 2011. Sem plugin 2011. API de plugins (`include/acts_api/fastfile.h`, `gsc.h`, `examples/*.c`) é único ponto de integração e exige MSVC para plugin novo.
- **Greyhound** (fork Wraith Archon): extrator de recursos, não scripts IW5.
- **gsc-tool**: compila/descompila IW5, mas exige `.gsc`/`.gscbin` já extraído; não abre fastfile.
- **Zonetool**: de 2021, usa hooks no jogo aberto.
- **Jekyll**: suporte IW5 não encontrado.

### <a id="current-blocker"></a>Bloqueio atual

Fluxo de dispositivo de `gh auth login` expirou pela quarta vez (`failed to authenticate via web browser: context deadline exceeded`); o usuário precisa abrir URL e aprovar enquanto comando aguarda.

### <a id="next-actions-revised"></a>Próximas ações (revisadas)

1. Usuário conclui `gh auth login`; publicar rascunho da issue (texto exato autorizado), continuar fork/PR.
2. Decidir OAT: compilar com símbolos e investigar `0x002f2452` ou ampliar `ff_probe.py` para analisador XFile real (percorrer recursos), sem ferramenta externa. Segundo caminho exige mais trabalho, mas é controlado por nós e segue criar do zero.
3. `ff_scan.py` em todas as zonas para inventário de identificadores de scripts (funções, indicadores `level.*`, dvars), alimentando etapa 4 da história.

---

## <a id="session-2026-10-18-cont-3--stop-the-owners-install-is-the-64-bit-build"></a>Sessão de 2026-10-18 (continuação 3) - PARE: a instalação é de 64 bits

**Substitui a suposição de 32 bits em todas as seções anteriores.** Regra 6 (parar na primeira contradição): jogo difere da suposição das ferramentas/guias; plano pausado para decisão do usuário.

### <a id="observation-verified-on-the-owners-real-install-read-only"></a>Observação (verificada por leitura da instalação real)

- `iw5sp.exe` e `iw5mp.exe` são **amd64**: máquina PE `0x8664` (cabeçalho). Instalação inclui `steam_api64.dll` (119.720 B), `bink2w64.dll` (431.616 B), não `steam_api.dll` / `binkw32.dll` de 32 bits.
- Fastfiles são, portanto, **zonas de 64 bits**: contêiner/cabeçalho XFile IW5 (`IWffu100`, versão 1, 44 bytes, 9 blocos), porém **ponteiros de 8 bytes**. `so_stealth_prague.bin` próprio analisado diretamente:
  - `XAssetList` no offset 44 = `{ int stringCount = 187; <pad4>; char** strings = FOLLOWS; int assetCount = 331; <pad4>; XAsset* assets = FOLLOWS }` (32 bytes).
  - Lista textual de scripts lê corretamente com ponteiros de 8 bytes: 187 strings, primeiras `end`, `tag_origin`, `tag_eye`, `tag_weapon_right`, `footstep_right_large`, … (`FOLLOWS` = `0xFFFFFFFFFFFFFFFF`; `0` = null).
  - Array em `0x1052` é 331 × 16 bytes de `{ u32, u32 0, u64 FOLLOWS }`.
  - Isso explica exatamente a falha do Unlinker: carregador IW5 de OAT é 32 bits e lê `assetCount` da palavra errada.
- Expectativa antiga de 32 bits (`assetCount` na palavra 2) causou a descoberta anterior de leitura errada de XAssetList. Causa raiz agora conhecida.

### <a id="corroboration-independent-sources"></a>Confirmação por fontes independentes

- `eithan1231/open-fastfile`, `reverse/x86-zone/README.md` ("The 64-bit MW3 build cannot be walked, and says so"): instalação Steam em `steamapps/common/Call of Duty Modern Warfare 3` é 64 bits (`steam_api64.dll`), zonas com ponteiros de 8 bytes. XAssetList de `mp_dome` lê `0x201, 0, -1, -1`: contagem e ponteiro de 64 bits. Percurso recusa de imediato; fluxo lê depots de 32 bits.
- **Atualização Activision de 2026** mudou MW3 (2011) para 64 bits, quebrando Plutonium, AlterWare/IW5-Mod e ajustes de FOV. Guias comunitários retornam aos 32 bits pelo console Steam (`download_depot`):
  - "CoD MW3: How to Install the Old (Stable) 32-Bit Version (+DLC)" (`steamcommunity.com/sharedfiles/filedetails/?id=3796576439`).
  - Gist "Alterware/Plutonium-compatible Steam depots" (`gist.github.com/Josu-A/b3698ee46b66225401a5583044f5789a`).
  - ModDB "MW3 Downgrader [FIX ALTERWARE]", "AlterWare FIX After 64-Bit Update".

### <a id="why-this-matters-for-our-plan"></a>Importância para nosso plano

- Todas as bases escolhidas — open-iw5, OAT, AlterWare/IW5-Mod, Plutonium, ferramentas verificadas dos GSC e plano `ff_probe.py` — visam **32 bits**. Instalação atual é 64 bits; open-iw5/analisador não funcionarão sem alterações.
- Dois caminhos:
  1. **(Recomendado) Visar 32 bits.** Adicionar depots antigos a cópia *separada*, nunca original. É padrão do ecossistema; trabalho reutilizável, ferramentas existentes válidas. Reversível.
  2. Visar 64 bits. Sem ferramentas; redescobrir formato inteiro e escrever cliente 64 bits do zero. Muito maior, sem base.
- Localização é **russa** (`UserConfig.language = russian`); baixar depots russos, não ingleses.

### <a id="32-bit-depots-for-the-owners-russian-copy--from-the-gist-above"></a>Depots de 32 bits da cópia russa - gist acima

- Binários de um jogador: `download_depot 42680 42681 5651167211650965131`
- Recursos principais: `download_depot 42690 42682 2661317971072643596`
- Russo: `download_depot 42690 42688 5872940112953203418`
- DLC, só se possuído: `42695`/`42696`/`42697`/`42698`, mesmos manifestos.
- Manifestos não permanentes (Activision altera); reconferir guia/gist antes de usar.
- Destino `steamapps/content/app_<appid>/depot_<id>/`, depois copiados à pasta. Copiaríamos a **diretório de teste separado**, nunca original.

### <a id="unknowns--to-verify"></a>Desconhecidos / a verificar

- Se usuário quer 32 bits e autoriza conta Steam para baixar depots (aproximadamente 8-15 GB), e onde criar cópia isolada.
- Se open-iw5 visa `iw5sp.exe` comercial ou só servidor dedicado (README exige este): conferir fontes.
- Enum `XAssetType` e formato `XAsset` de 64 bits (primeira palavra do array é `0x2d`, além dos 40 tipos de 32 bits); adiado salvo escolha do caminho 2.

---

## <a id="session-2026-10-18-cont-4--open-iw5s-real-base-binary-and-the-dedicated-server"></a>Sessão de 2026-10-18 (continuação 4) - base real de open-iw5 e servidor dedicado

### <a id="correction-to-the-plan-open-iw5-does-not-patch-the-retail-exe"></a>Correção: open-iw5 não aplica patches ao executável comercial

Lido na cópia local, `mw3-research/open-iw5/src/loader/binary_loader.cpp` e `loader.cpp`:

- `load_base()` lê **`iw5mp_server.exe`** e, salvo verificação desligada, exige SHA-256 `F271C305117B79242E254E9F64BD5AA2993CAC8E57975243EBD44CD576418D20`; senão lança *"Your iw5mp_server.exe is incompatible with this client."*
- `load(mode)` = base **+ diferença HDiffPatch** (`src/resources/iw5sp.exe.diff` e `iw5mp.exe.diff`, cerca de 1,6 MB cada, zstd) -> binário cliente, mapeado como módulo no próprio inicializador.
- `README.md`: cliente aberto MW3 individual/multiplayer, exige arquivos de servidor dedicado; aponta app SteamDB **42750**.

Portanto, **não** é patch de `iw5sp.exe` do usuário: é base de **servidor dedicado** + diferença binária de versão fixada. Consequências:

1. Binário dedicado **32 bits** é dependência obrigatória separada do jogo.
2. Base fixada por SHA-256; precisa ser exatamente a compilação usada pelas diferenças. Servidor recompilado pode não coincidir.

### <a id="dedicated-server-facts-public-steam-metadata-apisteamcmdnetv1info42750"></a>Fatos do servidor (metadados públicos Steam, `api.steamcmd.net/v1/info/42750`)

- App **42750**, "Call of Duty: Modern Warfare 3 - Dedicated Server", tipo `Tool`, inicia `iw5mp_server.exe`. **Não instalado** no PC (sem cópia local).
- Buildid público **24939921**, recompilado no fim de agosto/início de setembro de 2026 (`timebuildupdated` 1787706924, `timeupdated` 1788451381). Mais **novo** que jogo (`42680`=24615914, `42690`=24615796); mesma onda de 64 bits. Se novo `iw5mp_server.exe` continua 32 bits é **desconhecido**, fácil de verificar pelo depot pequeno.
- Depots compartilhados (42682-42689, 42692) e **42751** (binário servidor; manifesto público atual `2427974803223634451`).

### <a id="corrected-32-bit-depot-commands-current-from-the-steam-guide-updated-2-oct-2026"></a>Comandos de depots corrigidos (guia Steam atualizado em 2 de outubro de 2026)

IDs mudaram desde o gist anterior; conferir em toda execução. Valores atuais:

- Recursos: `download_depot 42690 42682 6067691797475126381` (aproximadamente 7 GB). *Continuação 3 usava `...2661317971072643596`, agora obsoleto.*
- Binários de um jogador: `download_depot 42680 42681 5651167211650965131`
- Inglês: `download_depot 42690 42683 6381783964590594065`
- Russo: `download_depot 42680 42688 5872940112953203418`
- DLC (só possuído): `42695 9005316271397236436`, `42696 2478272765185873756`, `42697 5810618727794750362`, `42698 5997898371746217629`
- Ressalva do guia: depot de idioma exige licença correspondente ("missing license for depot (No subscription)"). Cópia é RU; deve funcionar.
- Guia **não** cobre binários multiplayer (42691) nem servidor dedicado (42750/42751). Campanha exige SP e base servidor para open-iw5.

### <a id="the-decision-matrix-for-the-owner"></a>Matriz de decisão para o usuário

Três alvos reais. Referências existentes significam ferramentas que já funcionam no alvo.

- **A. Jogo comercial de 32 bits (padrão comunitário).** Depots acima em cópia *separada*. Bases: OAT, Greyhound, ferramentas GSC, nosso analisador, comunidade Plutonium/AlterWare. Download de aproximadamente 7-8 GB; fornece zonas e executáveis 32 bits. Reversível. **Não fornece sozinho open-iw5**, que precisa da base servidor.
- **B. 32 bits + servidor dedicado (open-iw5 conforme projeto).** A mais `iw5mp_server.exe` de 32 bits (42751, manifesto antigo). Única forma de compilar/rodar fork open-iw5. Falta descobrir qual gid antigo de 42751 corresponde à compilação 32 bits de hash `F271C305…`.
- **C. Comercial 64 bits (sem download).** Usar instalação atual. Sem download, porém sem referências: redescobrir zonas, escrever hook/cliente 64 bits próprio, sem analisadores ou injetores. Maior risco/esforço; Valve/Activision também continuam atualizando essa versão.

Recomendação: **B**, com A primeiro; único caminho baseado em ferramentas existentes e testáveis e que corresponde ao projeto real de open-iw5.

### <a id="verification-attempt-steamcmd-2026-10-18"></a>Tentativa de verificação: SteamCMD (2026-10-18)

- O SteamCMD (oficial da Valve, `steamcdn-a.akamaihd.net/client/installer/steamcmd.zip`,
  774.825 B, SHA-256 `7669B170DEE42DB8EE2273775ED7DFB2D173BDBA1B849F70E…`) atualizou a si mesmo normalmente.
- **O SteamCMD recusa caminhos com caracteres não latinos** ("cannot run from a folder path that
  includes non-English characters"). O caminho do nosso espaço de trabalho usa cirílico, então o SteamCMD precisa ser executado
  em um caminho ASCII; usamos `%LOCALAPPDATA%\Temp\opencode\steamcmd` (diretório temporário aprovado).
- **O login anônimo não consegue obter o app 42750**: `download_depot 42750 42751 …` retornou
  *"Depot download failed : missing license for depot (No subscription)"*. Isso é coerente com
  `visibleonlywhensubscribed = 1` e `dependantonapp = 42680` nos metadados do app 42750.
  → É necessária a licença Steam do proprietário.
- Metadados do app 42750 (via `app_info_print`): tipo `Tool`, inicialização `iw5mp_server.exe`,
  buildid público `24939921`. Depots: `42682` compartilhado (+ localizações 42683–42692) de 42690,
  `228989/228990` de 228980 e o único depot específico do app, **42751**.
- **Os tamanhos dos depots são bytes literais de conteúdo** (calibrado): `42681` = 5.625.400 = exatamente
  `iw5sp.exe`; `42691` = 6.167.104 = exatamente `iw5mp.exe`; `42682` = 8.456.418.603 (~7,9 GiB).
  Portanto, o depot `42751` = **117.744 B (~115 KB)** — pequeno demais para um executável de engine de ~6 MB.
- A página de atualização do SteamDB para a build `24939921` (3 de setembro de 2026) lista apenas `admin/server.cfg`,
  `admin/default.dspl`, `admin/TJ_default.dsr` (~127 KiB) — ou seja, o depot 42751 parece ser a
  pasta de configuração `admin/`, e não o executável do servidor. Onde `iw5mp_server.exe` é realmente distribuído (o manifesto
  `42682` atribuído ao próprio app 42750, que pode diferir daquele do app 42690) está **sem solução**
  e requer um login com licença para inspeção.
- Não confirmado pelos metadados: se a recompilação de setembro de 2026 mudou o **binário** do servidor
  (parece que apenas os arquivos `admin/*` mudaram, o que significaria que o executável ainda é a
  build anterior à atualização — provavelmente de 32 bits).

Próxima ação: o proprietário executa um `download_depot 42750 42751 <gid>` no console do cliente Steam
(ou em um login do SteamCMD) para podermos listar os arquivos e, se o executável estiver em outro lugar, localizá-lo.

### <a id="result--the-current-dedicated-server-is-a-dummy-64-bit-stub-decisive"></a>RESULTADO — o servidor dedicado atual é um stub fictício de 64 bits (decisivo)

O proprietário executou `download_depot 42750 42751 2427974803223634451` no console Steam. O depot 42751
contém exatamente um arquivo: **`iw5mp_server.exe`, 117.744 B**. Inspecionado com nossas próprias ferramentas
`mw3-research/tools/pe_probe.py` e `embed_probe.py`:

- PE: **`machine = 0x8664` (amd64), PE32+, 6 seções**, timestamp `1787640969` (~2026-08-30).
- O código é minúsculo (`.text` vsize `0xd4c`, ~3,4 KB); `.rsrc` (95.744 B) é apenas a cadeia
  de assinatura de código DigiCert — **sem engine incorporada**.
- Imports: `USER32.dll`, `KERNEL32.dll`, `VCRUNTIME140.dll`, `api-ms-win-crt-*`.
- Caminho PDB incorporado: **`H:\IW\dev\p4\outrun\iw5\code_source\dummy_server\x64\Release\iw5mp_server.pdb`**
- SHA-256: `6349B95F3EBC49CB3092260FC3CCDE9D791A60BEB52830F53211A711CABCC2B5` — **diferente**
  de `F271C305…`, esperado pelo open-iw5.

Conclusões:

1. A atualização de 2026 substituiu a engine real do servidor dedicado por um **stub fictício x64**. O
   servidor dedicado de MW3 distribuído hoje não faz nada (coerente com o trabalho de "Auto-fix" /
   downgrade da comunidade).
2. **O open-iw5 não consegue usar os arquivos atuais do servidor.** O caminho B agora também exige um
   **manifesto mais antigo (anterior a 2026) do depot 42751** — o `iw5mp_server.exe` real de 32 bits cujo
   hash é `F271C305…`. Encontrar o gid desse manifesto agora é uma incógnita registrada.
3. O caminho A (depots do jogo comercial de 32 bits) não é afetado e continua sendo o pré-requisito; os guias
   de reversão para 32 bits são atuais e confirmados pela comunidade.

### <a id="the-pre-2026-manifests-from-the-community-gist--mw3downgrader"></a>Os manifestos anteriores a 2026 (do gist da comunidade + MW3Downgrader)

Fonte: `gist.github.com/Josu-A/b3698ee46b66225401a5583044f5789a` ("Alterware/Plutonium-compatible
Steam depots", a lista canônica de depots da comunidade) e `github.com/GalvarinoDev/MW3Downgrader`
(MIT, código aberto, inclui SteamRE DepotDownloader; suporta jogo base, MP, Dedicated Server e
DLC e grava em uma pasta `downgrade` separada para o Steam não desfazer a mudança).

Principais manifestos (época de 32 bits):

| App | Depot | Manifesto | Conteúdo |
|---|---|---|---|
| 42680 | 42681 | `5651167211650965131` | Binários SP (`iw5sp.exe`) |
| 42690 | 42682 | `2661317971072643596` | Recursos principais (~8,4 GB) |
| 42690 | 42691 | `4104640605720756125` | Binários MP (`iw5mp.exe`) |
| 42690 | 42683 | `1595601894688570808` | Localização em inglês |
| 42690 | 42688 | `5872940112953203418` | Localização em russo |
| 42690 | 42695..42698 | `9005316271397236436`, `2478272765185873756`, `5810618727794750362`, `5997898371746217629` | DLC 1–4 |
| **42750** | **42751** | **`9089183337461621316`** | **Servidor dedicado real (anterior a 2026)** |

Também confirmado pelo tópico do fórum Plutonium "iw5 Dedicated server Download not working Sept 2026"
(7 de outubro de 2026): *"Parece que o Steam corrigiu a solução alternativa do servidor dedicado. O único arquivo que recebo
agora é iw5mp_server, em vez de receber também iw5mp.exe."*

Próximo: verificar se o hash de `iw5mp_server.exe` anterior a 2026 é `F271C305…` (a base esperada pelo open-iw5).

### <a id="result--pre-2026-server-matches-open-iw5-exactly-path-b-confirmed"></a>RESULTADO — o servidor anterior a 2026 corresponde exatamente ao open-iw5 (caminho B confirmado)

O proprietário executou `download_depot 42750 42751 9089183337461621316`. O
`iw5mp_server.exe` baixado é:

- **4.077.480 B**, PE `machine = 0x014C` (**i386 / 32 bits**, PE32), 5 seções, timestamp
  `1525273957` (~2018-05-02). Imports incluem `steam_api.dll`, `d3d9.dll`, `WS2_32.dll`,
  `WINMM.dll`; os marcadores incluem `iw5`, `demonware`, `zlib` — a engine real.
- SHA-256 = `F271C305117B79242E254E9F64BD5AA2993CAC8E57975243EBD44CD576418D20` — **exatamente**
  o `DEDI_HASH` do open-iw5.

Salvo em `mw3-research/dumps/iw5mp_server_32bit_F271C305.exe` (cópia verificada) para que uma atualização do Steam
não possa removê-lo.

**Conclusão:** a build atual de 2026 distribui um stub fictício x64 para o servidor dedicado, mas o
servidor real de 32 bits (idêntico byte a byte ao esperado pelo open-iw5) pode ser recuperado pelo manifesto anterior a 2026.
O caminho B está confirmado como viável. Trabalho restante para o caminho B: os depots do jogo de 32 bits (recursos principais
42682, binários SP 42681, localização russa 42688) mais a base do servidor acima.

### <a id="chosen-target-and-test-location-owner-decision-2026-10-18"></a>Alvo e local de teste escolhidos (decisão do proprietário, 2026-10-18)

- O proprietário aprovou: usar a **build de 32 bits (caminho B)**; cópia de teste isolada na **unidade E:**.
- Caminho da cópia de teste: **`<test copy>\`** (fora do espaço de trabalho).
- Depots a obter, copiar para a pasta de teste e depois verificar:
  - `42690 42682 2661317971072643596` recursos principais (~8,4 GB)
  - `42680 42681 5651167211650965131` binários SP (`iw5sp.exe`, 32 bits)
  - `42690 42688 5872940112953203418` localização russa
  - `42750 42751 9089183337461621316` base do servidor (já salva em `dumps/`)
- **Nunca** tocar em `<game dir>` (instalação real
  de 64 bits). Obter os depots apenas de `<steam content>\`.
- O proprietário executa as linhas `download_depot` no console Steam (o SteamCMD precisa de um
  login interativo; o console usa o cliente que já está conectado).

## <a id="session-2026-10-19--32-bit-test-copy-built-zone-format--script-inventory"></a>Sessão de 2026-10-19 — cópia de teste de 32 bits criada; formato de zona + inventário de scripts

### <a id="depots-downloaded-and-verified-all-complete"></a>Depots baixados e verificados (todos completos)

O Steam foi fechado durante a sessão, mas `<steam log>` prova que todos os três terminaram:
"Depot download complete" para depot_42682 (23:30:38), depot_42681 (23:32:55), depot_42688
(00:58:54). Fechar o Steam **não** os truncou.

| Depot | Manifesto | Conteúdo | Tamanho |
|---|---|---|---|
| 42690/42682 | `2661317971072643596` | Recursos base (`iw_00`..`iw_24`, zonas de DLC) | 7.032 MiB |
| 42680/42681 | `5651167211650965131` | `iw5sp.exe` (32 bits) | 5.650.432 B |
| 42690/42688 | `5872940112953203418` | Zonas russas + `localized_russian_iw0*.iwd` | 7.725 MiB |

Marcadores de 32 bits confirmados: `main/iw_00.iwd` = 314.819.587 B (o de 64 bits tem ~420 MB). Uma instalação
russa legitimamente **não** tem arquivos base `zone/*.ff` soltos — apenas `zone/russian` (152) + `zone/dlc` (7),
correspondendo exatamente à instalação real.

### <a id="isolated-32-bit-test-copy"></a>Cópia de teste isolada de 32 bits

`<test copy>\` — **14,42 GB**. Criada mesclando com robocopy os depots 42682 + 42688 + 42751,
depois copiando `iw5sp.exe`. Instalação real intacta (somente leitura).

Binários verificados:
- `iw5sp.exe` — 5.650.432 B, PE `0x014C` i386, sha256 `EA284F38…` (timestamp 2012-11-30)
- `iw5mp_server.exe` — 4.077.480 B, PE `0x014C` i386, sha256 `F271C305…` = base do open-iw5
- `admin/` — configurações do dedicado (`server.cfg`, `*.dsr`/`*.dspl`)

### <a id="32-bit-zone-format-confirmed-on-real-campaign-zones"></a>Formato de zona de 32 bits (confirmado em zonas reais da campanha)

`zone\russian\so_stealth_prague.ff` é descompactado para 1.206.736 B (assinatura `IWffu100`, zlib em 21). A
XAssetList no deslocamento 44 tem **16 bytes compactados**: `{int stringCount; char** strings; int assetCount;
XAsset* assets}` com ponteiros de 4 bytes (contra a forma de 32 bytes/ponteiros de 8 bytes da build de 64 bits).
Cada XAsset é `{u32 type; u32 header}` = 8 bytes; o cabeçalho é um deslocamento de arquivo ou `FOLLOWS`
(`0xFFFFFFFF`), indicando que os dados vêm em seguida, no próprio fluxo.

Novas ferramentas (todas nossas, `mw3-research\tools\`):
- `zone_probe.py` — detecta automaticamente o tamanho dos ponteiros; lista strings de script + histograma de tipos de recursos.
- `zlib_scan.py` — encontra fluxos zlib aninhados (pools de strings ScriptFile, texto RawFile).
- `zone_inventory.py` — inventário de identificadores por zona; grava as strings extraídas.
- `hexdump.py`, `pe_probe.py`, `embed_probe.py`.

Tipo conhecido: `0x27` (39) = `ASSET_TYPE_SCRIPTFILE` (`src/game/structs.hpp` do open-iw5).

### <a id="script-identifier-inventory-10-sp-campaign-zones"></a>Inventário de identificadores de scripts (10 zonas de campanha SP)

`mw3-research\inventory\` — total de **23.842 flags distintas**, 2.132.955 strings.

| zona | descompactado | recursos | scriptfile | fluxos zlib | flags |
|---|---|---|---|---|---|
| sp_berlin | 129,840,207 | 3047 | 3 | 5 | 11905 |
| sp_dubai | 20,713,359 | 557 | 19 | 21 | 1413 |
| sp_intro | 558 | 4 | 2 | 0 | 0 |
| sp_ny_harbor | 16,461,491 | 459 | 16 | 18 | 988 |
| sp_ny_manhattan | 66,090,779 | 3352 | 9 | 10 | 5468 |
| sp_paris_a | 19,036,905 | 327 | 3 | 6 | 1808 |
| sp_paris_b | 13,444,185 | 2314 | 3 | 2 | 778 |
| sp_payback | 27,899,505 | 1671 | 15 | 22 | 1672 |
| sp_prague | 405 | 3 | 1 | 1 | 0 |
| sp_warlord | 72,289,579 | 1273 | 42 | 30 | 5219 |

Exemplos de flags recuperadas — a camada de história/estado que a etapa 4 precisa sincronizar:
`NY_HARBOR_OBJ_FOLLOW_SANDMAN`, `NY_HARBOR_OBJ_CONTROL_ROOM`, `NY_HARBOR_OBJ_ESCAPE`,
`NY_HARBOR_OBJ_PLANT_MINE`, `AC130_OBJECTIVE_SUPPORT_FRIENDLIES`, `AC130_FRIENDLIES_DEAD`,
`SO_STEALTH_PRAGUE_OBJ_1`, `SO_STEALTH_PRAGUE_COLLECT_CIVILIAN`, `_stealth_enabled`,
`_stealth_spotted`. `sp_intro` (558 B) e `sp_prague` (405 B) são stubs quase vazios — o conteúdo real
fica nas zonas com os nomes das missões.

### <a id="next"></a>Próximos passos

1. Executar `zone_inventory.py` também nas zonas de missão `so_*`; classificar flags (objetivo / estado /
   interface) e remover ruído (muitas "strings" extraídas são falsos positivos binários).
2. Extrair ScriptFile `.gscbin` por zona (nome + 3 comprimentos + pool zlib + bytecode) como
   referência dos scripts compilados.
3. Continuar a Fase 3: mapear o caminho de inicialização SP do open-iw5 (`iw5sp.exe.diff` contra a base) e os vínculos de símbolos.
4. Autenticação no GitHub quando o proprietário estiver pronto (assumir a issue, fork, PR em rascunho).

## <a id="phase-3-milestone---open-iw5-sp-build--boot-2026-10-19"></a>Marco da Fase 3 — compilação + inicialização SP do open-iw5 (2026-10-19)

Resultado: **BUILD OK, O CLIENTE SP INICIA.**

O upstream `momo5502/open-iw5` foi excluído (GitHub 404). A árvore local veio sem `.git`, portanto
todos os 11 submódulos de dependências estavam **vazios**. Cada dependência foi recuperada de seu repositório canônico. A
branch `xlabs` excluída do gsc-tool (API necessária: `xsk/gsc/interfaces/*`, `xsk/resolver.hpp`,
`xsk/utils/compression.hpp`) sobrevive em `Zelobby/gsc-tool@xlabs` (7d37402, 2022-10-15).

Correções de compilação aplicadas à árvore do nosso fork (necessárias para MSVC 14.44 + dependências atuais):
1. `src/std_include.hpp`: `#undef byte` antes de `<gsl/gsl>` — o
   `tomcrypt_macros.h:434` do libtomcrypt define uma macro semelhante a função `byte(x,n)` que conflita com `gsl::byte`.
2. `src/utils/cryptography.cpp`: 2x `const_cast<ecc_key*>` para `ecc_ansi_x963_export` /
   `ecc_export` (a API do libtomcrypt 1.18.2 não usa const).
3. `deps/premake/libParallel.lua`: adicionar `libParallel/*.c` ao glob — os símbolos `c_locker_*` /
   `c_condvar_*` / `c_thread_parallel` ficam em `parallel_import_c.c`, que o glob `*.cpp`
   não incluía.
4. O caminho cirílico do espaço de trabalho quebra `premake5.exe` (caminhos de arquivo com caracteres estreitos). Compilar por uma
   junção ASCII `<build junction>` -> `<workspace>\mw3-research\open-iw5`.

Versões fixadas das dependências (correções de divergência): libtomcrypt v1.18.2, libtommath v1.2.1, GSL v4.0.0,
gsc-tool xlabs@7d37402. As demais nas pontas das branches (zlib develop, HDiffPatch master, rapidjson
master, udis86 master, zstd dev, minhook master, discord-rpc master).

Compilação: `tools\premake5.exe --file=premake5.lua vs2022` -> `build\open-iw5.sln`; MSBuild
Debug|Win32. Saída `build\bin\Win32\Debug\open-iw5.exe` (9.225.728 bytes).

Inicialização (cópia de teste isolada `<test copy>\`):
- colocado `open-iw5.exe` ao lado de `iw5mp_server.exe` (hash F271C305... == `DEDI_HASH`, correspondência exata).
- executado `open-iw5.exe -singleplayer`; o carregador aplicou `iw5sp.exe.diff` à base do dedicado em memória.
- OBSERVADO: processo ativo + respondendo, título da janela `Call of Duty(R): Modern Warfare(R) 3`,
  ~1,6 GB de RSS; gravou `userraw/console_sp.log`, `players2/config.cfg`,
  `players2/settings_c.zip.iw5`, `players2/settings_s.zip.iw5`.
- Captura de tela de evidência: `mw3-research\docs\evidence\sp_boot.png`.

Conteúdo de `console_sp.log` (219 bytes):
```
[     25693] logfile opened on Mon Oct 19 04:28:20 2026
[     25693] ******* script runtime error ********
[     25693] in call to builtin function "setsaveddvar"
```
`setsaveddvar` é emitido pela tabela de funções internas da própria engine reconstituída (tabela SP em 0x186C68C),
e não pela camada GSC do open-iw5 — um problema de dados/inicialização do jogo, não uma falha do carregador.

Conclusão: cadeia de ferramentas validada de ponta a ponta (compilação -> HDiffPatch -> carregamento PE em memória -> entrada
da engine -> janela + inicialização do sistema de arquivos). A camada de replicação cooperativa continua para a Fase 4+.


## <a id="session-2026-10-19-cont--github-publish-claim-issue--draft-pr"></a>Sessão de 2026-10-19 (cont.) — publicação no GitHub (issue de atribuição + PR em rascunho)

O proprietário autorizou. Etapas e resultados:

- `gh auth login --web` concluído como **Polygon2-1** (fluxo de dispositivo, escopos repo/read:org/gist).
- **Issue de atribuição aberta:** cranebeaker/coop-anything **#39**, "Claim: Call of Duty: Modern Warfare 3
  (2011) — campaign co-op". Não existe rótulo `in-progress` no repositório (o modelo de issue menciona um),
  então ela foi aberta sem rótulo (a issue de atribuição de MW2 #31 também não tem rótulo).
- **Fork:** Polygon2-1/coop-anything -> `game/modern-warfare-3`. A base é a `main` do upstream bffd56f
  (0 commits atrás). Observação: o snapshot zip local que tínhamos estava 13 entradas atrás da main; sempre usar um
  clone atualizado como base.
- **PyYAML instalado** (aprovado pelo proprietário) — `tools/build_directory.py` precisa dele.
- **PR:** cranebeaker/coop-anything **#40**, aberto **em rascunho**, "Modern Warfare 3 (2011): campaign
  co-op write-up + directory entries". O `check` do CI passa; pode ser mesclado, sem conflitos.
  Conteúdo:
  - `games/modern-warfare-3/README.md` (documentação a partir de `templates/game.md`).
  - `games/modern-warfare-3/NOTES.md` (este arquivo; caminhos locais sanitizados para `<game dir>` / `<test copy>`
    / `<steam content>` / `<build junction>` para o PR).
  - `data/directory.yaml`: 2 novas entradas — `AlterWare IW5-Mod` (tipo mod, Spec Ops/Survival, código
    fechado) e uma **lacuna** `(none found)` para cooperativo na campanha com a lista `searched:`.
  - `DIRECTORY.md` regenerado (223/32 -> 224 projetos/33 lacunas).
- A revisão do PR em rascunho pelo proprietário é a próxima etapa humana; a caixa "owner reviewed" ficou desmarcada.

Próximas ações:

1. O proprietário revisa o PR #40; retira o estado de rascunho quando estiver satisfeito.
2. Carregar uma missão de campanha no cliente open-iw5. **CONCLUÍDO** — ver "Marco 2 da Fase 3" abaixo.
3. Fase 4: camada de replicação com autoridade do host (jogadores, entidades, flags de história).
4. PR posterior opcional: linha de família de engine para a engine CoD (IW) em `playbook/engine-families.md`.

## <a id="phase-3-milestone-2---sp-client-runs-a-campaign-mission-2026-10-19"></a>Marco 2 da Fase 3 — cliente SP executa uma missão de campanha (2026-10-19)

Correção da observação anterior "a inicialização para": o erro de execução de script `setsaveddvar` é
**não fatal**. Ele é registrado uma vez durante a inicialização e o jogo continua; a execução anterior simplesmente
nunca entrou em uma fase.

O que realmente faltava era o argumento da fase. Observado na cópia de teste isolada:

- `open-iw5.exe -singleplayer` (sem fase): não chega a uma interface inicial utilizável. O título da janela
  muda para o nome do jogo, o RSS cresce para ~0,5 GB e depois ~0,9–1,1 GB, a janela para de responder e
  o `userraw/console_sp.log` de 219 bytes contendo o erro `setsaveddvar` é tudo que é gravado.
- `open-iw5.exe -singleplayer +map sp_intro`: processo ativo + respondendo, ~1,79 GB de RSS, o mesmo
  erro de inicialização é registrado e a missão carrega e pode ser jogada.

Prova de que é gameplay real de campanha na engine, e não um menu ou diálogo: o OCR do quadro capturado
(`Windows.Media.Ocr`, ru-RU — a cópia de teste é a localização russa) lê legendas
de diálogo em andamento:
- `Трак: Внимание! Вертолет на подходе!`
- `Гринч: Мне это нравится. Сэндман: Наверх по лестнице! За мной!`

Grinch e Sandman são personagens da campanha de Modern Warfare 3. Três quadros amostrados com 12 s de intervalo
diferem entre si, portanto o jogo está em execução, não congelado.

Evidências (capturas locais, não incluídas no commit deste PR): `mw3-research/docs/evidence/`
`sp_intro_subtitle_1.png`, `sp_intro_subtitle_2.png`, `sp_boot_intro_hud.png`,
`sp_intro_gameplay.txt`.

Próximo: Fase 4 — camada de replicação com autoridade do host (jogadores, entidades, flags de história).

