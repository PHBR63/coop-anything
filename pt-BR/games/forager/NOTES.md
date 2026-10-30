# <a id="forager-engineering-notes"></a>Forager: notas de engenharia

Notas que fundamentam [README.md](README.md), para o próximo agente trabalhando neste ou em outro jogo GameMaker YYC. Tudo aqui corresponde à compilação Steam 6160665 (`Forager.exe`, timestamp PE `0x60148428`); endereços são VAs com base de imagem `0x400000` (o executável usa ASLR: endereço no processo = VA - `0x400000` + base do módulo). Código do mod: https://github.com/melogo5/forager-coop. O código descompilado do jogo não é publicado; ele é regenerado a partir da sua cópia pelos passos abaixo.

## <a id="getting-readable-code-out-of-a-yyc-exe"></a>Obtendo código legível de um executável YYC

1. Metadados de `data.win`: UndertaleModTool CLI 0.9.2.0 com scripts C# extrai objetos (pai, sprite, máscara, eventos), salas e suas instâncias, sprites, sons, strings e extensões. Um `data.win` YYC não contém código, mas os dados de objetos e salas estão completos, permitindo reconstruir interiores a partir de um dump de sala.
2. Nomes de funções: toda função YYC empilha um ponteiro para sua string de nome (`gml_Script_PlayerFind`, `gml_Object_objPlayer_Step_0`) no rastreamento de pilha YYC (topo em `01B77490`). Encontre a string e a única função que a referencia: essa é a função. Um script Python monta o mapa de nomes pelas strings do executável; um script Ghidra renomeia funções e exporta pseudo-C por evento de objeto e script, também renomeando chamadas GML para GML.
3. Ghidra 12.1.4 sem interface: de cerca de 4080 nomes, 4015 associados a funções (66 não encontrados, por exemplo `objPlayer/KeyPress_17`), 3969 descompilados. 46 falharam: tempo limite de 300 s ou mais de 14 GB RAM. Tentar uma função por vez com limite de 1 h e buffer de resposta de 2000 MB não ajudou (`objPlayer/Step_0` excede o tempo; `WorldControl/Step_2` e `objPlayer/Step_2` excedem o buffer e, com buffer maior, o descompilador trava; 4096 MB nem inicia). Para essas, exporte a listagem completa e resumo de funções chamadas e strings referenciadas; rastreie o jogo em execução.
4. Anote o pseudo-C: a tabela YYVAR (`{const char* name; int id}` em `.data`, IDs preenchidos pelo runtime na inicialização) mapeia `DAT_xxxxxxxx` para funções internas e variáveis GML; números de posições de variáveis mapeiam para nomes de variáveis de instância (2349). Depois disso, `GETVAR(self, inventory)` se aproxima de GML.
5. Um rastreador na DLL insere hooks nas funções listadas em arquivo de texto junto ao executável (`name<TAB>VA`) e registra a cadeia de chamadas GML. Respondeu à maioria das questões deixadas pelas 46 funções não descompiladas.
6. Uma DLL de sondagem confirmou o básico antes do código cooperativo: proxy `version.dll` carrega; hooks MinHook em `gml_Script_PlayerFind` e `gml_Object_objPlayer_Step_0` funcionam; é possível ler `x`/`y`/`id`, uma global por posição e chamar função interna por nome (`ds_list_size`).

## <a id="runtime-gamemaker-225378-x86-cdecl"></a>Runtime (GameMaker 2.2.5.378, x86, cdecl)

| Elemento | Assinatura |
|---|---|
| Script `gml_Script_X` | `RValue* (CInstance* self, CInstance* other, RValue* result, int argc, RValue** args)` |
| Evento de objeto `gml_Object_X_Event` | `void (CInstance* self, CInstance* other)` |
| Função interna (entrada de tabela) | `void (RValue* result, CInstance* self, CInstance* other, int argc, RValue* args)` |

- **RValue** (16 bytes): `+0` valor (double, int32, int64 ou ponteiro), `+8` indicadores, `+0xC` tipo. Tipo `& 0xFFFFFF`: 0 real, 1 string, 2 array, 3 ptr, 5 undefined, 6 object, 7 int32, 10 int64, 13 bool, 14 iterator. Só os tipos 1 a 3 possuem memória (`FREE_RValue`). Runtime anterior a 2.3: sem estruturas ou métodos.
- **CInstance**: `+0` vtable (`[1]` = `InternalGetYYVarRef(slot)`, thiscall), `+4` `RValue* yyvars` (por posição, passo de 16 bytes, pode ser NULL; nesse caso, use a vtable), `+0x74` indicadores (bit 0 destruído, bit 1 desativado), `+0x7C` object_index, `+0x130` próxima instância ativa.
- **Objeto** (recurso): `+0x44` lista encadeada de instâncias `{next, ?, CInstance*}`.
- Tabela **RFunction** de funções internas (`01B8C014`), 0x4C bytes por entrada: `char name[64]`, `+0x40` função, `+0x44` argc. 2502 entradas nesta compilação; funções além disso (`layer_*`, `tilemap_*`) são encontradas por nome, não índice.

| VA | Função |
|---|---|
| `016AB490` | `YYGML_CallBuiltin(self, other, &ret, argc, fnIndex, RValue** args)` |
| `016CAD50` / `016CAF50` | `Variable_GetValue` / `Variable_SetValue(int instId, int slot, int arrayIndex, RValue*)` (instId >= 100000 instância, < 100000 objeto, -3 todos) |
| `016CA140` / `016CACD0` | `Variable_GetBuiltin` / `Variable_SetBuiltin(CInstance*, varId, arrayIndex, RValue*)` (`x`, `y`, `sprite_index`; índice `0x80000000` = nenhum) |
| `004012B0` | `FREE_RValue` |
| `00409120` | `RValue::operator=` (thiscall, this = destino) |
| `016A52A0` | busca de instância por ID |
| `016ABC10` | `YYSetString` |
| `016AADE0` | `YYError` (erro fatal GML) |
| `016F2D00` | `event_user(self, other, n)` = `Perform_Event(self, other, 7, 10 + n)` em `017DA800` |
| `016E6BA0` | núcleo `instance_destroy` `(self, other, id, executeEvent)`: toda destruição termina aqui |
| `01B7CA98` | instância `global` |
| `01B8E0D0` | sala atual; `+0x80` primeira instância ativa |

YYC chama algumas funções internas diretamente, sem passar pela tabela (`YYGML_instance_destroy` em `016EC110`); insira hook na função central, não na entrada de tabela.

## <a id="facts-about-the-game-that-shaped-the-design"></a>Fatos do jogo que orientaram o projeto

- `PlayerFind(n)` = `ds_list_find_value(global.players, n)`, sempre chamada com 0. É o ponto único de acesso ao jogador, permitindo a troca de ator: insira hook e retorne o representante enquanto executa a ação remota. Roda cerca de 350 vezes por quadro; o hook precisa ser barato.
- Estado da instância do jogador: `inventory`, `inventorySize`, `coins`, `hp`, `invulFrames`, `energy`, `level`, `xpToGain`, `gear`, `tool`, `toolSelected`, `buff`, `cosmetic`, `bomb`. Global: `skillUnlocked`, `featProgress`, `droids`, `assignedDroids`, `ownedLands`, `zoneCurrent`, `deathCount`.
- Por que apenas criar outro `objPlayer` não funciona: reage à mesma entrada global; seus Step e Draw chamam `PlayerFind(0)` e leem o estado do primeiro jogador. Ignorar seus eventos e desenhá-lo é o que o transforma em representante.
- Golpe num recurso: `objPlayer_Step_0 -> UseItem -> UsePickaxe`, que executa `with (target) { killedByPlayer = room_speed; event_user(0) }`. O recurso morre em seu Step com `hp <= 0`; `Destroy_0` chama `GainXp` e `DropItem`.
- Morte: `objPlayer/Step_1` chama `SaveGame` e cria `objGameOver` com `hp <= 0`.
- Listas de suspensão de células guardam vetores `[id, box]`. Deixar nelas um ID destruído ou reativado fazia o host falhar depois, quando `ProcessCulls` acessava o ID obsoleto. Remova IDs de todas as listas ao destruir e reativar.
- O baú azul da masmorra é o mesmo `objTreasureChest`, com outro sprite, e abre sem chave; tratar todo `objTreasureChest` como baú com chave gastava a do host e o deixava esperando pela do convidado.
- `global.droidNames` é ds_grid, não vetor (uma linha por drone: nome, aparência, cor).
- Sons em loop (`sndBombFuse`, laser de `objWatcher`) só param no `Destroy_0` do objeto; uma réplica removida silenciosamente mantém o som para sempre. Pare os sons em loop ao remover a réplica.
- A mira de arco é desenhada por `objPlayer Draw_0`; o representante desenha a mira remota, a menos que esse sprite seja ignorado durante seu desenho.
- `COOP_DEBUG_GODMODE` ativa a invencibilidade do próprio jogo, que também permite andar sobre a água: testes que movem o jogador nesse modo colocam construções na água.

## <a id="official-modding-api-what-stopped-the-first-prototype"></a>API oficial de mods: o que impediu o primeiro protótipo

Mod API 1.0.1, interpretador GML interno ao jogo. Aprendizado do protótipo:

- Retornar ao menu principal descarrega todos os mods e apaga suas `global.*`. O que precisa sobreviver deve ficar nas globais do jogo (`variable_global_set`).
- Evento de rede durante o descarregamento causa falha (`ref_map_wrap` em `WorldControl`). Feche a sessão antes de mudar de sala e adie a mudança.
- Nunca envolva estruturas de dados do jogo (`variable_global_get(..., "grid")`): o descarregamento as destrói junto com o mod.
- `OnStep` não executa com menu aberto; `OnDrawGUI` executa.
- `instance_activate_object` só reativa no próximo quadro; uma captura do mundo exige dois quadros.
- `instance_destroy()` sem argumento é rejeitado; `-1` significa `self`; use `noone` para referência vazia.
- `OnResourceSpawn`/`OnMobSpawn` disparam antes de concluir a configuração do objeto (tipo de minério); envie um quadro depois.
- Sockets somente TCP; sem `buffer_seek`, UDP ou `json_encode`.
- Sem acesso a arquivos, não era possível entregar o mundo do host ao convidado; este copiava manualmente o salvamento antes de cada sessão e após cada compra de ilha.

## <a id="bugs-from-playtests-worth-knowing-about"></a>Bugs das sessões de teste que vale conhecer

Todos foram encontrados em testes com dois PCs, tiveram causa raiz identificada pelos dois logs, foram corrigidos e receberam verificação por script. Tabelas completas em `docs/coop/PLAYTEST*.md` (russo) no repositório do mod.

| Observado | Causa | Correção |
|---|---|---|
| Espada, flechas e cajados do convidado não causavam dano | atingiam a réplica do convidado; a próxima vida enviada pelo host sobrescrevia | queda de vida desde a última escrita do host enviada como golpe |
| Pontos de habilidade incorretos do convidado | escritos numa variável nunca lida; `objPlayer.skills` é nível - 1 - aprendido | escrever no campo real |
| Prateleiras do museu vazias no modo cooperativo | interiores reconstruídos de `data.win` sem código de criação de sala por instância (`gml_RoomCC_rmMuseum_*`), guardado pelo YYC apenas no executável | encontrar funções pelas strings de nome no Ghidra e chamá-las após criar cada instância |
| Host falha depois de muitas destruições | ID obsoleto numa lista de suspensão de célula | remover IDs das listas |
| Salvamentos de mundo quebrados | arquivo de zona com lista `Entities` curta | reparar arquivos antes de carregar o mundo, escrevendo atomicamente e guardando a primeira cópia `.broken` |
| Drone do convidado desaparece após voltar | convidado joga no mundo do host; seus drones não eram salvos | host armazena familiares de cada convidado junto ao arquivo de personagem e restaura na entrada |
| Som infinito de pavio para o convidado | som em loop só parava em `Destroy_0` | veja acima |

## <a id="code-review-findings-2026-10-25"></a>Descobertas da revisão de código (2026-10-25)

Uma revisão de todas as 13.400 linhas da DLL à época encontrou, entre outros: manipuladores ativos após saída de convidado (uma conexão posterior poderia reescrever a posição 99 do host), comprimento de vetor vindo da rede sem validação, coordenadas NaN chegando ao mundo, escrita não atômica do arquivo do personagem convidado, manipulador de exceções vetorizado que poderia entrar em loop numa falha do leitor de pilha GML e convidados desaparecidos sem fechar TCP permanecendo na sessão para sempre. Tudo foi corrigido; a segunda revisão adicionou uma thread de escrita e fila por conexão, quadro de apresentação antes de contabilizar a conexão e validação de todos os valores enviados pelo convidado.
