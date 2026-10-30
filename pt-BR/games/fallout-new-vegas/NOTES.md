# <a id="fallout-new-vegas---working-notes"></a>Fallout: New Vegas - notas de trabalho

Notas de uma sessão de agente (2026-10-22) iniciada por um pedido: "Quero jogar Fallout: New Vegas em modo cooperativo com meus amigos."

Tudo abaixo foi verificado na máquina da sessão. Os caminhos usam `<game dir>` e `%USERPROFILE%`; nada privado entra neste arquivo.

## <a id="1-triage-the-game-identity-used-for-everything-below"></a>1. Triagem: identidade usada em tudo abaixo

| Campo | Valor |
|---|---|
| Loja | Steam, **versão russa/polonesa/tcheca**, appid `22490` ("Fallout: New Vegas PCR") |
| Steam buildid | 45574, `UserConfig.language = russian` |
| Executável | `FalloutNV.exe`, versão do arquivo **1.4.0.525** |
| SHA-256 (executável) | `40d5a7c967a1ec5df1dc19c25f8df3ca74480aa95e8755171567f1129a3001fa` |
| Dados | `FalloutNV.esm` + `FalloutNV_lang.esp` (textos russos ficam em `_lang.esp`) |
| DLC | nenhum instalado |
| Motor | Gamebryo |

Lido de `appmanifest_22490.acf` na biblioteca Steam (`"name" "Fallout: New Vegas PCR"`, `"installdir" "Fallout New Vegas enplczru"`, `"language" "russian"`).

**Não é a versão inglesa do Steam (appid 22380).** Isso importa porque ambos os projetos FNV dizem "Steam ou GOG" sem mencionar a versão PCR.

## <a id="2-finding-fnv-coop-already-supports-the-pcr-release"></a>2. Descoberta: fnv-coop já aceita a versão PCR

`tools/installer/fnv_find.py` em [fnv-coop](https://github.com/cranebeaker/fnv-coop) procura instalações por appid e nome de pasta; a versão russa e seu appid estão listados:

```python
STEAM_NAMES = ("Fallout New Vegas", "Fallout New Vegas PCR")
...
for appid in ("22380", "22490"):
```

O mesmo arquivo define a única compilação aceita:

```python
SUPPORTED_GAME = (1, 4, 0, 525)
```

`inspect_game()` exige então que `FalloutNV.exe` informe exatamente `1.4.0.525`, uma pasta `Data` com `FalloutNV.esm` e xNVSE `>= 6.3.0`.

A instalação verificada corresponde em todos os pontos: appid `22490`, pasta `Fallout New Vegas enplczru`, `FalloutNV.exe` `1.4.0.525`, `Data\FalloutNV.esm` presente. A versão russa/PCR é **alvo aceito pelo instalador cooperativo**, não um desconhecido. A localização contém só textos (`FalloutNV_lang.esp`); identificadores de formulários, sincronizados pela camada cooperativa, não são localizados. Portanto, a versão russa não é caso especial para sincronizar missões.

Nem o relato fnv-coop deste repositório nem `data/directory.yaml` mencionam PCR. Vale corrigir (seção 6).

## <a id="3-state-of-the-two-co-op-projects-2026-10-22"></a>3. Estado dos dois projetos cooperativos (2026-10-22)

### <a id="nvmp---the-only-thing-a-player-can-use-today"></a>NV:MP - a única opção utilizável hoje

* Estado: jogável, testado pela comunidade. Wiki: <https://nuwiki.nv-mp.com/wiki/Getting_Started>.
* Arquivos cliente: `build_release_client.zip`, **versão 9.4** (publicada em 2026-10-09), 89 MB, em <https://github.com/NVMP/ClientDistribution/releases> (organização oficial NV:MP).
* Necessários: xNVSE (6.3.4 pela wiki; atual 6.4.9), patch de 4 GB e ZIP cliente.
* Hospedar para amigos: `Launch Local Server` no inicializador; amigos usam `Connect via IP` com `<ip>:27015`. Redirecionar UDP+TCP 27015, usar Radmin VPN ou LAN simples.
* Conta Discord exigida só para servidor oficial ATK e servidores SDK públicos; servidor cooperativo local privado não exige.
* **O que não faz: missões.** Não replica etapa, objetivo, global ou estado de script de missão. Atores marcados como de missão são deliberadamente tornados locais no cliente; cada jogador tem seu diário e seus NPCs. (A engenharia reversa dos binários 9.4 em `docs/05-nvmp-intel.md` de fnv-coop confirma: lógica de encontros torna locais atores de missão, sem API de replicação de missões no SDK servidor.) O anúncio de 2016 diz o mesmo: cada jogador mantém seu diário, embora haja um host.

### <a id="fnv-coop---the-story-layer-developer-preview"></a>fnv-coop - camada de história, prévia para desenvolvedores

* Estado: prévia para desenvolvedores, sem lançamento no GitHub. Instalador, inicializador e guia existem (`docs/PLAYER-GUIDE.md`, `tools/installer`, `tools/launcher`), mas o primeiro passo do guia diz para extrair **a versão distribuída**, que não existe.
* Desenvolvimento ativo: issue de acompanhamento atualizada no dia anterior à sessão.
* Roteiro: 10 etapas. Etapas 1, 3, 4, 5, 6, 7 têm código escrito e testes no jogo pendentes; etapa 2 (sincronização de inimigos no jogo real) assumida por outro colaborador; etapa 8 (história principal inteira) tem 99,98% das chamadas de scripts sincronizadas e 65 de 104 etapas de Goodsprings passando no jogo.
* Projetado para executar **junto do NV:MP**: NV:MP fornece avatares, inimigos e combate; fnv-coop fornece estado compartilhado de missões/história.
* Compilar exige Python 3.11+, CMake >= 3.20, gerador VS 2022 com `-A Win32` (x86 obrigatório) e cópia de xNVSE em `third_party/NVSE` (não incluído; ENet incluído).

## <a id="4-what-this-means-for-a-player-who-wants-to-play-tonight"></a>4. Significado para quem quer jogar hoje à noite

A divisão honesta:

* **Avatares, combate, mesmo mundo, agora**: NV:MP. Funciona, tem suporte, amigos podem entrar daqui a uma hora.
* **História compartilhada**: somente fnv-coop, compilando do código-fonte ainda em conclusão. Espere prévia para desenvolvedores, não versão polida.

## <a id="5-what-was-done-in-this-session-observations"></a>5. O que foi feito nesta sessão (observações)

Tudo foi feito numa **cópia** em `<game dir>`; instalação Steam e salvamentos do usuário nunca foram alterados.

1. **fnv-coop compilado do código-fonte** (VS 2022, Win32/x86): `nvcoop.dll` e executáveis de teste de todas as linhas. Precisa de cabeçalhos `third_party/NVSE` (fora do repositório) e cópia cliente `third_party/nvmp` para conferir assinaturas L6.
2. **Dados de missões gerados** dos arquivos: `python -I tools/questdata/run_all.py --data "<game dir>\Data"` produziu 436 cenários, 1183 etapas, 12 missões / 104 estágios / 73 referências NPC resolvidas para o marco Goodsprings.
3. **Versão para jogadores empacotada** pelo empacotador do repositório (`tools/installer/package_release.py`): 27 arquivos, ~4,4 MB, `FNV-CoOp-1.0.0.zip`, SHA-256 conferido; instalada na cópia pelo próprio instalador (que fez backup do que alterou e escreveu `nvcoop.ini`).
4. **Suíte completa executada** (`python -I tools/test_all.py`). Resultado na seção QA do relato técnico.
5. **Quatro bugs encontrados e corrigidos em fnv-coop** (seção 6).

## <a id="6-bugs-found-in-fnv-coop-all-still-present-in-main-at-32e12cc"></a>6. Bugs encontrados em fnv-coop (todos ainda em `main` em `32e12cc`)

Cada um é pequeno, tem causa raiz clara e teste que comprova a correção.

| # | Arquivo | Bug | Correção |
|---|---|---|---|
| 1 | `tools/test_all.py` | `NEEDS` definido duas vezes, primeiro com chamáveis e depois listas de arquivos. A segunda vence; `need[0]` é tupla e `need[0]()` provoca `TypeError: 'tuple' object is not callable`: execução morre em vez de ignorar a suíte com dados ausentes. | Manter tabela de listas, remover primeira definição morta, consultar `missing_data()` sobre ausências. |
| 2 | `tools/installer/fnv_find.py` | `libraryfolders.vdf` / `appmanifest_*.acf` do Steam lidos como UTF-8 com `errors="replace"`. Steam os grava na página ANSI do sistema quando não é UTF-8 (Windows russo, cp1251); cada caractere não ASCII do caminho vira U+FFFD, a pasta deixa de existir e a instalação nunca é encontrada, sem erro. | Tentar UTF-8 primeiro, depois página ANSI (`fnv_ini.ini_encoding()`). Nova verificação e variante de mutação. |
| 3 | `tools/questdata/run_all.py` | `--data` repassado a `effects.py`, mas não a `m1.py`; m1 não resolve assinaturas de formulários: referências sem `sig`, lista de observação do extrator interno (exige `sig == "REFR"`) vazia. | Repassar `--data` também a `m1.py`. |
| 4 | `tools/questdata/extract.py`, `plugin/dialogue/tools/gen_consent_messages.py` | Caminho Steam dos EUA fixo; numa versão regional (`Fallout New Vegas enplczru`), ferramentas não leem nada e produzem saída vazia. | Localizar `Data` como o instalador: `FNV_GAME_DIR`, depois caminho conhecido, depois `fnv_find.candidates()`. |

Correções na branch `fix/portable-paths-and-non-ascii` (três commits) de um fork de `cranebeaker/fnv-coop`. Ainda não estão em `main`.

## <a id="7-blockers-found-on-the-machine-used-for-this-session"></a>7. Impedimentos encontrados na máquina da sessão

Registrados para o próximo agente não redescobri-los (sem caminhos privados ou dados pessoais):

* Ferramentas ausentes precisaram ser instaladas: Python 3.12, CMake 4.4, Visual Studio 2022 Community com MSVC v143 x86/x64 e Windows SDK, Git for Windows.
* 8 GB de RAM: duas cópias de FNV cabem, quatro não (as notas de tela dividida pedem cerca de 10 GB livres para quatro jogadores).
* **Um salvamento é necessário antes de verificar o mundo.** A ponte interna recusa nomes reservados (`autosave`, `quicksave`, `systemsave*`) e não há fluxo automatizado de "New Game"; uma ação humana (começar e salvar na cópia) libera os testes internos.
* Sem DLC instalado; inspeções de missões DLC (etapa 9) não podem executar aqui.

## <a id="8-proposed-follow-up-not-done-in-this-session"></a>8. Continuação proposta (não feita nesta sessão)

1. Acrescentar versão PCR/russa ao relato FNV e notas de `data/directory.yaml`, evitando presumir a inglesa como única. (Feito nesta PR.)
2. Registrar SHA-256 PCR junto do inglês, seguindo a regra de identidade. (Feito nesta PR.)
3. Relatar os quatro bugs ao projeto original com a branch.
4. Quando fnv-coop tiver lançamento real, informar que o instalador aceita appid 22490 e que isso foi conferido nos arquivos reais de uma instalação PCR.
