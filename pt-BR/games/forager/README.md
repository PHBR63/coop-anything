# <a id="forager-2019"></a>Forager (2019)

| | |
|---|---|
| Motor | GameMaker Studio 2, compilado com **YYC** (GML compilado para código de máquina x86; `data.win` não tem blocos CODE/VARI/FUNC). Runtime GameMaker 2.2.5.378 |
| Versões testadas | Compilação Steam 6160665 (versão interna 4.1.9, GEN8 2.2.2.302, compilada em 2021-01-29), Windows. SHA-256 de `Forager.exe` `ad2b90f164320f646c340b0be60af966851dfdc74dce366580f3dcd531853ae6` (marca de tempo PE `0x60148428`), `data.win` `0f5ccbfbbd80dd7eb5f1c4fde676c4c1f8f1dc77e24bcce9086d8ec2b38144e8`, `steam_api.dll` `af17df745250d1814eaa274fff7b0faeb43381e6762e026267e5859778477abd` |
| Projetos | [Forager Co-op Mod](https://github.com/melogo5/forager-coop) (MIT; versões v0.1.0 e v0.1.1) |
| Nível de QA | automated: sessões por script controlam de 2 a 4 clientes reais em um PC e exibem PASS/FAIL por verificação, com variantes de mutação. Também houve nove testes em dois PCs, oito pelo Steam |
| Última atualização | 2026-10-30 |

## <a id="where-things-stand"></a>Situação atual

Até quatro jogadores podem jogar um mundo Classic on-line: host e até três convidados, entrando por convite Steam (F2 no mundo) ou por LAN/VPN. Mundo, inimigos, construções, baús, ilhas, tempo e clima, nível e XP, moedas, árvore de habilidades, museu, missões de NPCs e masmorras são compartilhados; cada convidado mantém inventário, equipamentos, familiares e roupa próprios. O mod é um único `version.dll` junto a `Forager.exe`; nenhum arquivo do jogo é alterado. Está disponível como beta: o desafio Void não funciona em modo cooperativo, e às vezes um convidado carrega um mundo ligeiramente diferente, corrigido pelo mod em segundos.

## <a id="existing-work"></a>Trabalhos existentes

- **Forager Co-op Mod** (https://github.com/melogo5/forager-coop): começou em 2026-10-16 como protótipo na API oficial de mods (`mods/CoopTest` no repositório, congelado), reescrito como patch nativo `version.dll` em 2026-10-17. 149 commits até 2026-10-29, cerca de 16.500 linhas C++. Público desde 2026-10-28.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Sem scripts para editar.** YYC compila cada script GML e evento de objeto em função nativa de `Forager.exe`. Os nomes sobrevivem: cada função escreve um ponteiro para seu próprio nome (`gml_Object_objPlayer_Step_0`) no rastreamento de pilha YYC, então a função que referencia essa string é a procurada. Ghidra 12.1.4 (sem interface) nomeou e descompilou 3969 de cerca de 4080 funções dessa forma. 46 (incluindo `objPlayer/Step_0`, `Step_2`, `WorldControl/Step_2`, `SaveGame`) excedem tempo ou memória do descompilador; foram lidas em listagens e pelo rastreamento do jogo em execução. A CLI UndertaleModTool extrai objetos, salas, sprites e strings de `data.win`.
- **Um jogador atrás de uma função.** `objPlayer` se adiciona a `global.players`, e 365 funções obtêm o jogador por `PlayerFind(n)`. Uma sonda com hook viu somente `n = 0` (cerca de 1,4 milhão de chamadas em 4 minutos, aproximadamente 350 por quadro), e nenhum código percorre a lista: a abstração existe, mas não é usada.
- **Entrada global** (`InputCheck*` lê `global.inputStatus`); portanto, um segundo `objPlayer` reage às mesmas teclas.
- **Sem pausa.** Menus abertos não pausam; cerca de 30 objetos verificam `IsMenuOpen` por conta própria e param.
- **Desativação fora de vista.** `WorldControl/Step_1` chama `CullObject` (desativa tudo fora de `global.camera*`) e `ProcessCulls` (reativa o que voltou à vista). Objetos desativados no host ficam invisíveis ao código dele; um convidado distante joga em mundo congelado se o host não o mantiver ativo.
- **Mundo aleatório e temporizado.** `ResourceSpawn` cria recursos e inimigos em terrenos próprios aleatórios; itens surgem por `DropItem` em dezenas de eventos `Destroy_0`. Somente uma máquina pode executar isso.
- **Salvamentos** guardam um jogador (`SaveGame`, `SerializeCharacterChunk`); o mundo fica em `saveData<N>/Zones/*.cin`.
- **Steam.** O jogo já carrega e inicializa `steam_api.dll` (Steamworks SDK aproximadamente 1.41) e chama `SteamAPI_RunCallbacks` por quadro; uma DLL pode usar salas, convites e P2P `ISteamNetworking` pela API plana, com callbacks na thread do jogo. Salas e P2P funcionam sob o identificador do próprio Forager, 751780.
- **API oficial de mods** (1.0.1) tem sockets TCP, mas não `buffer_seek`, UDP ou JSON. Mods são descarregados a cada retorno ao menu principal (seus `global.*` e estruturas do jogo encapsuladas são destruídos; evento de rede durante descarregamento causa falha), `OnStep` não executa com menu aberto e mods não podem gravar arquivos, impedindo entregar o salvamento do host ao convidado. Essas limitações congelaram o primeiro protótipo e motivaram a DLL nativa.

Estruturas em execução, endereços usados pela DLL e lista de hooks estão em [NOTES.md](NOTES.md).

## <a id="what-we-changed"></a>O que alteramos

Mod: https://github.com/melogo5/forager-coop (MIT). Documentação de desenvolvimento, análises de testes e revisão de código estão em russo, em `docs/coop/`.

**Modelo.** `version.dll` atua como proxy da biblioteca Windows de mesmo nome e insere hooks com MinHook. Confere a marca de tempo PE do executável e apenas encaminha chamadas em outras compilações. O host tem autoridade: o mundo vive e é salvo somente nele; o convidado recebe o salvamento em uma vaga temporária (99, removida depois) e então um fluxo de mudanças. Cada outro jogador é um segundo `objPlayer` com eventos próprios (Step, Alarm, Mouse) ignorados, mas Draw executado (representante). Como `objPlayer` herda `parAlly`, inimigos miram nos representantes sem código extra.

**Troca de ator.** O hook de `PlayerFind` retorna o ator atual: normalmente o jogador local, mas, enquanto o host executa uma ação do convidado, o representante desse convidado. O código do jogo lê desse representante dano da ferramenta, habilidades, efeitos e equipamentos; saídas dirigidas ao jogador (`GainXp`, `GainItem`, moedas, `DmgPlayer`, avisos) vão ao convidado, não ao host. Um golpe do convidado viaja como `hit(hostInstanceId, dmg)`; o host executa `event_user(0)` do objeto com o representante como ator.

Partes principais e os problemas resolvidos:

| Área | Problema | Correção |
|---|---|---|
| Desativação fora de vista | mundo ao redor de convidado distante estava adormecido no host | hooks em `instance_deactivate_object` e `ds_list_add` mantêm ativo tudo dentro de uma caixa do tamanho da câmera ao redor de cada convidado; `ProcessCulls` repete para cada caixa |
| Destruições | objetos desativados pelo convidado sobreviviam à destruição no host (20 árvores no host contra 71 no convidado) | identificadores destruídos removidos de toda lista de células adormecidas; réplicas desativadas também destruídas |
| Reconciliação | convidados às vezes carregavam árvores extras ou ausentes | a cada 5 s o host envia objetos ao redor de cada convidado; divergência vista duas vezes seguidas é corrigida |
| Inimigos fantasmas | golpes do convidado não acertavam inimigos | inimigos do convidado são réplicas exatas do host; criações locais e réplicas obsoletas são removidas |
| Dano à distância e de espada | flechas, cajados e espadas atingiam a réplica do convidado, e a saúde do host sobrescrevia o dano | antes de gravar a saúde do host na réplica, toda redução desde a última gravação é enviada como golpe ao host |
| Itens deixados | itens duplicados ou coletados pelo jogador errado | vão diretamente ao inventário de quem quebrou ou matou o objeto, enviados só a esse convidado |
| Baús, estações | dois jogadores no mesmo baú ou fornalha | host arbitra; o segundo a abrir recebe aviso de ocupado e seu menu fecha |
| Habilidades | pontos do convidado gravados em variável não usada; árvores divergiam | árvore única: habilidade comprada por qualquer um é repetida para todos por `ItemEdit`/`StructureEdit` do jogo; pontos continuam individuais |
| Progresso compartilhado | nível, XP, moedas, desbloqueios de estruturas | mantidos pelo host e transmitidos; desbloqueios copiados com `StructureEdit(s, 11, true)` |
| Museu, missões | doações perdidas, "Quest not found" | doações combinadas como grade (máximo por célula); estado de missões dos NPCs consultado a cada segundo e aplicado por `NPCSetQuest`/`NPCSetState` quando o NPC existe |
| Masmorras | primeiro bloqueadas, depois jogadores separados | todos entram e saem juntos; peças de quebra-cabeça, lanternas, chaves, gelo da chave do chefe e baús sincronizados; morte reaparece na entrada e reinicia os carrinhos daquele jogador |
| Interiores | entrar na torre do mago ou museu parava o mundo dos outros | interiores reconstruídos na sala do mundo a partir de dump de salas de `data.win`; código de criação por instância do museu chamado por endereço |
| Morte | fim de jogo encerrava a sessão | reaparecimento na ilha inicial, sem salvar, sem fim de jogo |
| Jogadores | somente 2 | estrela pelo host, até 3 convidados, identificador por conexão nunca reutilizado na sessão |
| Transporte | exigia IP, Hamachi ou Radmin | sala Steam só para amigos, convite F2, `+connect_lobby`; quadros divididos em pacotes P2P de 512 KB; convidados TCP e Steam na mesma sessão |
| Robustez | convidado lento congelava o host; convidado desaparecido permanecia para sempre | thread e fila de escrita por conexão, TCP keepalive, quadro de apresentação antes de contar a conexão; host valida todo valor recebido |

## <a id="qa"></a>QA

- **Várias cópias em um PC.** Com `steam_appid.txt` (`751780`) junto ao executável, `Forager.exe` inicia sem relançar pelo Steam; duas a quatro cópias rodam lado a lado.
- `tools/gametest/coopflow.ps1` inicia host e convidado e controla menus por mensagens de janela (sem mouse real); `regress.ps1` executa uma sessão de mundo novo com opções de depuração (`COOP_DEBUG_AUTOHIT`, `_BUILD`, `_STORAGE`, `_COINS`, ...) e exibe PASS/FAIL por verificação a partir dos dois logs e de `error.log`. Cerca de 40 scripts cobrem recursos individuais (`sharedskills.ps1`, `museum.ps1`, `traps.ps1`, `relay.ps1` para três jogadores, `four.ps1` para quatro).
- `COOP_DEBUG_PORT=1` abre porta de consulta no jogo: ler objetos e variáveis, chamar scripts (`query.ps1`).
- `mutants.ps1` executa cada verificação normalmente (deve PASS) e com a correção desativada por `COOP_DEBUG_MUTANT` (deve FAIL).
- Últimos resultados registrados (documentação do mod, não reexecutados para este relato): `regress.ps1` 9/9 PASS após revisão de código (2026-10-25). Após o teste 9 (2026-10-27, `regress.ps1 -HostSlot 5`), todos PASS exceto "shared chest": nesse salvamento, o `instance_nearest` do auxiliar de depuração não via o baú por estar desativado; o código de armazenamento não havia mudado. Quatro jogadores (`four.ps1`, 2026-10-20): cada cópia vê as outras três; itens chegam somente ao destinatário (convidado 1: 10 de 10; convidado 2: 35 de 35; convidado 3: 0).
- Nove testes em dois PCs entre 2026-10-19 e 2026-10-27, oito por convites Steam; o mais longo durou 3 h 15 min. Logs de ambos analisados após cada sessão; análises em `docs/coop/PLAYTEST*.md` no repositório do mod. Três e quatro jogadores testados somente como cópias em um PC.

## <a id="how-to-play"></a>Como jogar

Cada jogador precisa de Forager no Steam na compilação acima. Baixe `version.dll` em https://github.com/melogo5/forager-coop/releases/latest e coloque junto a `Forager.exe` em `<game dir>`. Host: menu principal, COOP, CREATE, escolha salvamento ou novo mundo Classic; depois F2 no mundo para convidar. Convidado: aceite o convite Steam ou selecione COOP, digite um nome, escolha o servidor LAN do host e JOIN. LAN e VPN usam TCP 7790 e UDP 7791. Para desinstalar, exclua `version.dll`.

## <a id="known-issues"></a>Problemas conhecidos

- Desafio Void não funciona em modo cooperativo (reaparecimento fora da arena, temporizador e contagem de inimigos travados no convidado).
- Convidado ocasionalmente carrega mundo ligeiramente diferente (árvores extras ou ausentes), corrigido em segundos.
- Somente mundos Classic. Mods da API oficial do Forager não são compatíveis.
- Somente host compra ilhas e recebe conquistas Steam.

## <a id="next-steps"></a>Próximos passos

- Void: descobrir como o jogo cria e remove a arena (chamadores, mudanças no mundo e globais), como foi feito para interiores e mapa de terrenos após comprar ilhas.
- Fabricação usando baú aberto por outro jogador: o conteúdo de quem fecha sobrescreve o consumido na fabricação. Exige mesclagem, não apenas trava.
- Causa raiz do mundo ocasionalmente diferente no convidado. O mod registra `world: WARNING the world came incomplete` quando o snapshot vem incompleto.
- Testar três e quatro jogadores em PCs separados.
