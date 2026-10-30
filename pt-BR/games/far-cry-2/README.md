# <a id="far-cry-2-2008"></a>Far Cry 2 (2008)

| | |
|---|---|
| Motor | Dunia (derivado de CryEngine 1), x86 de 32 bits. `FarCry2.exe`, de 28 KB, é um inicializador mínimo que chama `Dunia.dll!RunGame`; motor e rede em `Dunia.dll`, lógica Lua nos arquivos contêineres |
| Versões testadas | Steam, app id 19900, versão 1.03, build id 52164. `Dunia.dll` SHA-256 `6353936a54aa841350bb30ff005727859cdef1aa10c209209b220b399e862765` (20.183.176 bytes). Todos os endereços deste relato correspondem a esse arquivo. Reproduzido num segundo PC (Windows 11 23H2) com arquivo idêntico em 2026-10-24 e executado entre ele e um terceiro (Windows 11 Pro, mesmo arquivo) por Steam em 2026-10-25 |
| Projetos | Nenhum projeto cooperativo público. Protótipo de pesquisa (representante com posição e direção, abaixo): https://github.com/MortyRei/fc2-coop-probe (MIT); correções, retransmissor e testes nas PRs abertas #1-#3 |
| Nível de QA | automated, somente para representante de posição (duas cópias num PC: 20/20, 22/22 por retransmissores; veja QA), mais execução manual em dois PCs por Steam. História, inimigos e mundo sem sincronização, portanto ainda sem o que testar |
| Última atualização | 2026-10-25 |

## <a id="where-things-stand"></a>Situação atual

Não há campanha cooperativa para Far Cry 2, e o multiplayer original não consegue executar a campanha atualmente (abaixo). Um protótipo de pesquisa demonstra a possibilidade de segundo jogador: duas cópias carregam o mesmo salvamento e trocam posição e direção; cada uma cria avatar invencível do parceiro, move-o suavemente e o gira. Funciona no mesmo PC e, por retransmissor Steam (sem IPs ou redirecionamento), entre PCs em redes distintas (uma execução manual em 2026-10-25). Não é modo cooperativo jogável: avatar sem animação de caminhada, armas ou sincronização de vida; missões não compartilhadas. Detalhes e evidências datadas em [NOTES.md](NOTES.md).

## <a id="existing-work"></a>Trabalhos existentes

Pesquisado em 2026-10-19 (web, GitHub, Nexus, ModDB, fóruns Steam; Reddit apenas por resumos de busca): nenhum projeto de campanha cooperativa encontrado. Buscas: "Far Cry 2 campaign co-op mod", a mesma com "Dunia" e "moddb", consulta ampliada co-op / Nexus / Reddit, consulta russa e de servidor dedicado.

- Discussão Steam de 2013 diz que o jogo é para um jogador fora do multiplayer (resposta de usuário): https://steamcommunity.com/app/19900/discussions/0/864973123475897875
- FCSE (Far Cry 2 Engine Extension), mod Nexus 368, inicializador que carrega plugins DLL de `bin\plugins\`: https://www.nexusmods.com/farcry2/mods/368 (página bloqueou WebFetch com HTTP 403; conhecido apenas pelos resumos; licença e fonte desconhecidos). Possível base para DLL cooperativa.
- FC2MPPatcher (GPL-2.0) restaura multiplayer on-line após encerramento dos serviços Ubisoft em 2021-06-01, para 1.03. Sem modo cooperativo ou campanha: https://github.com/halvors/FC2MPPatcher
- ModDB lista reformulações e mapa deathmatch para 16 jogadores, nenhum cooperativo.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para modo cooperativo)

Observações nas cópias de teste; cada ponto tem data e fonte em [NOTES.md](NOTES.md).

- **Arquivos contêineres.** `Data_Win32\*.dat/.fat` são FAT2 versão 5, compressão versão 3 (ID de 2 bits: 0 nenhuma, 1 LZO1x). Gibbed.Dunia (licença zlib, https://github.com/gibbed/Gibbed.Dunia, commit `a43405cab3ea206ed0e9fcc6222fc2e36d545eea`) extrai após dois pequenos patches locais no mapeamento v5 e tamanho do buffer de saída (detalhes nas notas). `Gibbed.FarCry2.ConvertBinaryObject` converte FCB em XML (141 arquivos falharam).
- **Scripts.** Lua **4.0**, vinculado estaticamente a `Dunia.dll`, e grafos visuais "Domino" guardados como Lua. 573 globais, 21 tabelas; `Game` tem 98 métodos. Entradas Lua (VA = 0x10000000 + RVA): `lua_gettop` 0x2AA9C0, `lua_settop` 0x2AA9E0, `lua_getglobal` 0x2AAF90, `lua_dobuffer(L, buf, size, name)` 0x2AB600, `luaL_check_lstr` 0x2D24B0; `lua_State*` principal em `**(void ***)0x11606728`; funções nativas registradas por `FUN_102aa850(0, name, cfunc)`. A API de scripts não retorna posições.
- **Modos de jogo são dados.** `engine\gamemodes\gamemodesconfig.xml` lista entradas `<GameMode>` com serviços; modos de rede marcam serviços com `NetPresence`, mas `FCXSingle` (campanha) não. Conjunto de camadas de missão ativas (caminho de camada de `CMissionComponent`) é o estado que o modo cooperativo precisaria compartilhar.
- **Código de rede.** `NetworkEngine`, `CNetObject*` com funções `Host` / `Controller` / `ThirdParty` (pawns, veículos, projéteis, armas). Replicação de pawn definida em `engine\online\onlineengine\*.netobject.xml` (`CPawnControllerMemento`, `CPawnHostMemento`, `CPawnThirdPartyMemento` e mensagens de tiro, recarga, veículos). Sessões usam Agora (Ubisoft on-line), encerrado em 2021.
- **Multiplayer original hoje.** `-host -login <name> -lan` executa e abre UDP 9000 e 9001. `FC2ServerLauncher.exe -dedicated <cfg>` com `network_type 2` inicia sessão LAN. `-join <IPv4>` fixa tipo de rede 2 e tenta primeiro `gconnect.ubi.com:3074` e `onlineconfigservice.ubi.com`, ambos encerrados; segunda cópia nunca chega ao host LAN. `-noagora` encerra o cliente.
- **Linha de comando.** `-exec`, `-benchmark`, `-host`, `-join`, `-wait`, `-load` (despachante `FUN_10663d40`). `-load <file>` abre literalmente `<profile>\Saved Games\<file>`, mas sai em até 3 s com salvamento normal da campanha; não permite entrar na campanha aqui.
- **Entidades e física.** IDs de 64 bits (Lua os vê como strings decimais). Busca em `FUN_10055820` (thiscall; ECX = `*(void **)0x11644E80`, argumentos: saída, parte baixa e alta do ID); objeto em `holder+0xC`. Física Havok (RTTI presente). Posição do jogador na transformação de movimento de objeto semelhante a `hkpRigidBody`, vtable em RVA `0xE67658`: linhas da matriz em `+0x30` da transformação, posição na última (z para cima). Matriz da entidade (`entity+0x30`, posição em `+0x60`) recalculada a cada quadro; escrevê-la não faz efeito. Endereços de heap mudam por sessão; busca do corpo pela classe e posição mais próxima funcionou sempre.
- **Duas cópias num PC.** Segunda cópia exige mutex próprio (string `FarCry2Instance` em `Dunia.dll`, deslocamento de arquivo 0xE08950) e perfil próprio. Pasta vem da string de 10 bytes `\Far Cry 2` em **0xE0E094** (junto de `\My Games` em 0xE0E0A0 e `\GamerProfile.xml` em 0xE0E080, usada por `CGamerProfileNative`); substitua por outra de 10 bytes, como `\FC2test_A`. O salvamento aberto a segue (`<profile>\saved games\`). A **lista de salvamentos** de Continue / Load Game vem de terceira string, os 19 bytes `My Games\Far Cry 2\` em 0xE089A0; substitua pela mesma pasta (`My Games\FC2test_A\`). Essa string sozinha não move o perfil (ainda abriu o `GamerProfile.xml` real em 2026-10-24); sem ela, lista os salvamentos reais e, num PC onde nunca rodou, não lista nenhum, só New Story (2026-10-25). Os três patches alteram 17 bytes. `GamerProfile.xml` precisa existir ou o cliente sai.

## <a id="what-we-changed"></a>O que alteramos

Somente cópias de teste; nada na instalação, perfil ou salvamentos reais.

1. **Patches de instância única e perfil** (strings do mesmo tamanho na `Dunia.dll` de teste: mutex em 0xE08950, lista de salvamentos em 0xE089A0, perfil em 0xE0E094): permitem duas cópias simultâneas com perfis em janela e salvamentos próprios. Prova: log `CreateFileW` mostra A abrindo `FC2test_A\GamerProfile.xml` e `FC2test_A\saved games\<save>.sav`, B abrindo os de `FC2test_B`, janelas 800x600 conforme perfis (2026-10-24). Receita de 2026-10-19 alterava só 0xE089A0, sem redirecionar perfil; relato de 2026-10-24 chamou isso de desnecessário, incorretamente: cópia em PC novo sem esse patch não listava salvamentos (2026-10-25).
2. **Sondagem interna** (proxy `dinput8.dll` para testes, MinGW, cerca de 850 linhas C, fonte em https://github.com/MortyRei/fc2-coop-probe). Hooks nas importações Winsock, arquivos e `PeekMessage`; acrescenta canal Lua (`coop_cmd.lua` executado na thread principal por `lua_dobuffer`, resultado lido de global Lua), comandos nativos (ler memória, buscar entidade, corpo por classe, teleportar corpo), varreduras de memória, transporte e avatar abaixo. Prova: resultado Lua `alive 3` e posições correspondentes à entidade (notas de 2026-10-19).
3. **Transporte UDP próprio** (loopback 9101 e 9102, não portas 9000 a 9004 do motor): pacote de 28 bytes com sequência, posição e direção, cerca de 16 por segundo por cópia. Prova: logs com `rx` crescente e `remote` de cada cópia igual a `local` da outra; teleporte em uma aparece imediatamente no log da outra.
4. **Avatar do parceiro.** `SpawnEntityFromArchetype(name, x, y, z, rx, ry, rz)` com nome de entidade do jogador cria outro pawn; evento `CFCXCountersComponent_SetInvincible` torna-o invencível (sem isso, recebia dano das escritas fixadas e terminava a missão com "Game over" nas duas). Sondagem escreve posição do corpo a cada ciclo principal, com suavização de 25%. Prova: usuário viu o avatar da outra cópia percorrer círculo de 3 m suavemente, sem cair ou Game over.
5. **Correção de associação do corpo do avatar** (2026-10-24). Bug: mesmo salvamento, ninguém ainda se moveu, avatar nasce sobre o jogador local; busca (corpo mais próximo da classe a até 1 m) retornava **o corpo do próprio jogador local**. Logs mostravam corpos iguais e sondagem escrevia posição remota no jogador local. Correção (8 linhas em `find_body` / `av_tick` / `av_valid`): busca ignora corpo local e espera identificá-lo. Prova (logs e leituras `pos`, não teste automatizado): corpos diferentes nas duas cópias; com `walk 3 20 2` em A, avatar de B seguiu círculo de A a 0,5-1 m, enquanto jogador B ficou parado (desvio de cerca de 0,1 m). Correção na PR #1, ainda não incorporada.
6. **Direção do avatar** (2026-10-24). Corpo físico é cápsula vertical, rotação sempre identidade; olhar com mouse muda só linhas de yaw da matriz da entidade (`entity+0x30`: `(d0,d1,0)`, `(-d1,d0,0)`). Avatar sem controlador mantém a rotação escrita ali; escrever rotação do corpo ou chamar `TeleportEntity` com ângulos não muda nada; `SpawnEntityFromArchetype` usa último argumento (yaw em graus) só ao criar. Agora a sondagem escreve a direção recebida na matriz a cada ciclo (suavização 25%). Prova: teste com duas cópias gira A pelo mouse três vezes e avatar B coincide em 0,0 graus (sondagem sem alteração falhou, preso em 0); usuário viu a rotação.
7. **Modo de rede** (2026-10-24). Endereço fora de 127.x faz vincular todas as interfaces e aceitar só IP do parceiro (outros como `drop`). Prova num PC pelo próprio endereço LAN: 19/19, 30 pacotes falsificados de 127.0.0.1 descartados. Não executado entre PCs (em redes diferentes).
8. **Retransmissor Steam** (`relay/fc2_relay.py`, 2026-10-24/25). Sondagem conversa só com retransmissor local, que leva pacotes como mensagens Steam P2P (Spacewar, AppID 480, sala só para amigos, sessões aceitas só de membros, manutenção de conexão e prazo 20 s), ou UDP simples como substituto nos testes. `scripts/setup-copy.ps1` (cópia, três patches, perfil de teste) e `scripts/start-coop.ps1` (um lado da sessão) preparam e executam cada PC. Prova: QA, execução em dois PCs.

## <a id="qa"></a>QA

Um teste automatizado: `tests/two_copy_walk.ps1` no repositório da sondagem (adicionado em https://github.com/MortyRei/fc2-coop-probe/pull/1, ainda não incorporado). Controla dois clientes reais num PC; ambos já devem ter patches e perfis de teste.

```
powershell -ExecutionPolicy Bypass -File tests\two_copy_walk.ps1 -CopyA <test copy A> -CopyB <test copy B> -OutDir <results folder>
```

Inicia as duas cópias, pressiona Enter até cada log mostrar o próprio salvamento, lê ID do jogador pelo Lua, executa `netstart` em ambas, caminha com A por `walk 3 20 2` e amostra `pos <avatar>` / `pos <player>` em B. Exige: cada cópia lê seu perfil/salvamento; mesmo ID em ambas; corpo do avatar diferente do local; ao menos 10 pacotes/s por sentido; avatar se move (amplitude ao menos 1,5 vez o raio); fica até 1,5 m em média e 2,5 m no máximo da posição de A recebida por B; jogador B desvia até 0,5 m; sem linhas `CRASH` / `ACCESS VIOLATION`; pasta real intacta (capturas antes/depois). Uma proteção encerra ambas se o log nomear a pasta real. Pressiona Enter nas janelas, então o teclado deve ficar livre.

Últimos resultados (2026-10-24, Steam 1.03, um PC, Windows 11 23H2):

```
probe with the avatar-body fix:
RESULT: 16 checks, 0 failed -> PASS   (~2 min)
  link A/B 16.0 / 16.0 packets/s; avatar span 5.92 m; distance to A mean 0.43 m, max 1.07 m;
  B player drift 0.12 m; real profile: new 0, changed 0, removed 0

negative control, probe before the fix:
RESULT: 16 checks, 3 failed -> FAIL
  B player stays put: max drift 16.46 m (B's own player dragged); avatar body A/B: no pointers in the old log line
```

A verificação de desvio detecta o bug de corpo; `avatar moved` e `avatar follows A` também passavam antes. Verificações manuais e de logs anteriores estão datadas em [NOTES.md](NOTES.md).

Adições posteriores ao mesmo teste (PRs #1-#3): fase de direção (A girado três vezes pelo mouse; `avatar heading follows A` até 15 graus), títulos A/B, `-PeerIp` (rede e teste de pacote falsificado) e `-Relay` (cadeia de dois retransmissores UDP):

```
heading added:               RESULT: 18 checks, 0 failed (headings A/B 128.1/128.1, -145.4/-145.4, 149.8/149.8)
  negative control (no heading code): 1 failed, avatar stayed at 0 degrees
peer = own LAN address:      RESULT: 19 checks, 0 failed (30/30 forged packets dropped)
window titles checked:       RESULT: 20 checks, 0 failed
through two udp relays:      RESULT: 22 checks, 0 failed (relay A 837 out / 715 in, 0 dropped)
```

**Dois PCs por Steam, execução manual (2026-10-25).** Redes diferentes, contas Steam amigas, Steam 1.03 em ambos, `scripts/start-coop.ps1` em cada lado (hospedar/entrar). Retransmissor convidado encontrou sala pela lista de amigos e teve sessão aceita; primeira mensagem decodificada com identidade do remetente no deslocamento 16 (formato de 64 bits, confirmado só com duas contas reais). Pacotes nos dois sentidos a cerca de 16/s por aproximadamente 7 minutos, 0 descartados, sem desconexão. `walk 3 20 2` no host: avatar no convidado (amostrado a cada 2 s) percorreu cerca de dois círculos de raio 3 m no centro esperado (2 m/s x 20 s = 40 m), enquanto jogador local ficou a cerca de 0,1 m; usuário viu movimento nas duas telas. Quando convidado parou, host marcou ausência após 20 s. Ainda sem aprovação/reprovação por script; evidências nos logs dos dois lados.

Mais tarde, mesmos PCs (convidado em `--join wait` nos dois últimos):
- **Direção entre PCs:** host girou com mouse 171.3, 81.3, -171.3 e 77.6 graus; avatar remoto (amostrado a cada 2 s) mostrou as quatro direções 1-2 s depois, sem sair do lugar.
- **Convite Steam:** host `--invite <name>`; aceito no segundo PC, retransmissor recebeu callback 333, entrou e estabeleceu conexão/avatar em até 3 s.
- **Join Game** pela lista de amigos (sem convite): entrou na nova sala, também por callback 333 (Steam relata Join Game num amigo em sala acessível como GameLobbyJoinRequested; 337 não observado).
- Todas: 0 descartados, sem linhas de falha ou pasta de perfil real nos logs.

Não cobertos: convite ou Join Game sem retransmissor convidado ativo, sessões longas, perda.

## <a id="how-to-play"></a>Como jogar

Não jogável. Sondagem é ferramenta de pesquisa, não instalador: vive nas cópias de teste alteradas, e ambos devem carregar o mesmo salvamento. `scripts/setup-copy.ps1` e `scripts/start-coop.ps1` (PR #3) configuram e iniciam um lado cada; retransmissor Steam exige Python de 64 bits e `steam_api64.dll` de Steamworks.NET (baixada e conferida por hash via `scripts/get-steam-api.ps1`), mostrando ambos como "playing Spacewar". Fonte, compilação, comandos e receita de duas cópias em https://github.com/MortyRei/fc2-coop-probe (MIT); código do jogo fica lá, não neste repositório.

## <a id="known-issues"></a>Problemas conhecidos

- Avatar desliza em pose ociosa: sem animação, arma, vida ou dano sincronizados. Olha na direção de visão do outro, não de movimento.
- Atravessa cenário (espelha posição remota já submetida a colisão; numa movimentação por script, atravessou árvore).
- Sem sincronização de missões, objetivos, mundo ou veículos.
- Pawn criado por script do arquétipo do jogador se parece com ele; outros `PawnPlayer.<name>` também tinham mesma aparência na campanha.
- Ler memória diretamente causou falha uma vez; `findbody` agora lê por blocos, mas `scan` ainda lê diretamente e pode causar falha.
- Na sondagem publicada sem PR #1, avatar pode se associar ao corpo local quando ambos começam juntos e nunca gira (itens 5 e 6 acima).
- Em modo de rede, porta UDP acessível a quem tiver rota (só pacotes do parceiro são usados; sem criptografia). Retransmissor Steam evita portas abertas.
- Tudo depende da compilação exata 1.03; deslocamentos não portáveis.

## <a id="next-steps"></a>Próximos passos

1. Animação de locomoção: decodificar subobjetos tipados de `CPawnControllerMemento` e `CPawnThirdPartyMemento` (cerca de onze campos em `0x70 .. 0x120`) ou comparar memória de pawn parado e andando e escrever diferenças.
2. Missões: reproduzir camadas ativas e estado Domino na segunda cópia; entradas observadas `Game:MissionSetState` e `SaveGame`.
3. Dois PCs com verificações por script (convidado já amostra avatar; comparar automaticamente com percurso e direção do host).
4. Ampliar teste de duas cópias conforme os recursos chegarem (missões a seguir).
