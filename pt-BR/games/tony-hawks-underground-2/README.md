# <a id="tony-hawks-underground-2-2004"></a>Tony Hawk's Underground 2 (2004)

| | |
|---|---|
| Motor | Motor Neversoft (linhagem THPS4 / THUG), scripts de bytecode QB (QScript) em arquivos `.prx` |
| Versões testadas | PC, inglês. `THUG2.exe` SHA-256 `52fc88849654b34839ec2f96bff3a8c0b7a855df9a207aab9f2fca2e6bd440f3`, executado como THEMOD 1.3: `THEMOD 1.3.exe` do testador com SHA-256 `2b1ac8a9282c7817d6999967d0d47bfabaf8b29ac220bbff9f634e107f1095c3` (veja "THEMOD" abaixo) |
| Projetos | [thug2-coop](https://github.com/LeftGamer1/thug2-coop) (história cooperativa, este relato) |
| Nível de QA | community-reports (testador e amigo jogam on-line); também há um percurso com dois clientes por script, veja QA |
| Última atualização | 2026-10-26 |

## <a id="where-things-stand"></a>Situação atual

Duas pessoas já conseguem jogar juntas o Story Mode on-line. O host joga sua própria história e usa seu salvamento; o amigo entra na partida e anda de skate na mesma fase com NPCs, cenas e objetivos. É uma versão alfa: testador e amigo jogam pela internet e relatam bugs; ainda não concluíram uma campanha inteira em modo cooperativo.

## <a id="existing-work"></a>Trabalhos existentes

Pesquisado em 2026-10-24 (web em inglês e russo, GitHub, este repositório): nenhum projeto de história cooperativa encontrado. Detalhes e lista completa de buscas em [NOTES.md](NOTES.md).

- [THUG Pro](https://en.wikipedia.org/wiki/THUG_Pro): conversão total on-line baseada em THUG2, código fechado, sem campanha.
- [PARTYMOD](https://github.com/PARTYMANX/partymod-thug2) (MIT): correções e jogo on-line por OpenSpy; sem história cooperativa.
- [thug2-decomp](https://github.com/CanuckAussieKev/thug2-decomp): reimplementação C++ como hook em DLL. Não é usada aqui em tempo de execução, mas seu código descompilado identificou a maioria dos endereços em que este mod insere hooks.
- THEMOD 1.3 (TH Mods, 2007-2008): mod de scripts usado pelo testador e no qual este mod se baseia. Seu site (thmods.com) não responde mais; nenhuma página de download ou autor foi encontrado.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para modo cooperativo)

- **O modo de um jogador já é um jogo em rede**: servidor local e um cliente (`setservermode on; StartServer; JoinServer`). Mudar o modo de rede para LAN antes de `StartServer` torna o servidor acessível; a entrada por IP direto do próprio jogo (UDP 5153) traz um segundo skatista. Posições e animações são sincronizadas pelo jogo.
- **Scripts decidem o que uma fase carrega**: o script `<LV>_Goals` de cada fase acrescenta objetivos clássicos num jogo em rede e objetivos de história nos demais casos. `InNetGame` / `InMultiplayerGame`, visíveis pelos scripts, são funções intermediárias de duas instruções; o mod responde "não" a elas no modo cooperativo, fazendo as fases carregarem o conteúdo de história. Algumas verificações nativas (pedestres, ignorar nós, 19 verificações no gerenciador de objetivos e código da carreira) exigiram o mesmo tratamento.
- **Estado da história**: carreira (`CSkaterCareer` Write/ReadToStructure), informações de capítulos (`CHAPTER_STATUS`, introduções e encerramentos vistos) e parâmetros do gerenciador de objetivos. Serializado por `Script::WriteToBuffer` do próprio jogo (~3,4 KB) e enviado por conexão TCP auxiliar (porta + 1, 5154).
- **Scripts**: `.qb` compilados em `Data\pre\*.prx` (PRE v3, LZSS). O executável de THEMOD carrega `thethug2mod.prx` em vez de `qb_scripts.prx`. NeverScript compila e descompila QB; os scripts do mod são um `coop.qb` acrescentado a esse arquivo.
- **Código nativo**: um proxy `dinput8.dll` aplica patches ao executável na memória ao carregar. Cada patch confere primeiro os bytes substituídos, deixando outras compilações intactas.

## <a id="what-we-changed"></a>O que alteramos

O mod é uma `dinput8.dll` (C++17, MinGW i686) e `scripts\coop\coop.qb`. A lista completa de hooks com endereços está em [NOTES.md](NOTES.md); os principais:

| Problema | Causa raiz | Correção |
|---|---|---|
| Conteúdo de história ausente no jogo em rede | Scripts das fases e verificações nativas consultam `InNetGame` | Modo cooperativo responde que não é jogo em rede aos scripts e às 19 verificações de objetivos/carreira; verificações do próprio motor permanecem |
| Host falhava ao criar o skatista do amigo | Carreira usa `max_players=1`, sem heap de segundo skatista | Reiniciar servidor como na inicialização para dois jogadores (`cleanup preserve_skaters`, `InitSkaterHeaps`, players=2) |
| Amigo executava sua própria história | Cliente carrega a própria carreira | Host envia carreira, capítulos e parâmetros de objetivos na entrada e a cada mudança de fase; salvamento do amigo retorna ao sair |
| Objetivos, cenas e câmeras de objetivos unilaterais | Cada um executa só para quem o acionou | `WinGoal`, fim/omissão de cenas (`EndMovies`), `PlaySkaterCamAnim`/`KillSkaterCamAnim`, trocas de modelo e escolha de parceiro profissional espelhados pela conexão auxiliar |
| Objetivos pareciam competição por terminar primeiro | Objetivo vencido era espelhado para ambos imediatamente | Objetivos compartilhados: objetivo obtido com NPC começa para ambos e é vencido quando os dois concluem; o primeiro espera |
| Nome flutuante do amigo no topo da tela | Rótulo de nome do modo carreira | Rótulo próprio projetado pela câmera do skatista, com distância, visível através de paredes |
| Skatistas atravessavam um ao outro | `GameNet::Manager::PlayerCollisionEnabled` segue opção de rede desativada no modo cooperativo | Hook e `[coop] player_collision=` em `coop.ini` |
| Chat exibia caracteres inválidos em russo | Cirílico chega em CP1251, sem fontes cirílicas no jogo | Hook `Sio::KeyInput` translitera russo, ucraniano e bielorrusso conforme a página de código do teclado |
| Apenas 4 resoluções fixas | Configuração do dispositivo escolhe de 1280x1024 a 640x480 conforme `Launcher.exe` | `[display] resolution=` em `coop.ini` preenche a última opção e sempre a seleciona; janela recebe o mesmo tamanho |
| THEMOD 1.3 não pode mais ser baixado | Site encerrado | Patcher de bytes reconstrói o executável de THEMOD a partir do `THUG2.exe` do jogador (abaixo) |

### <a id="themod"></a>THEMOD

O instalador de THEMOD 1.3 (NSIS, 2.224.553 bytes, SHA-256 `d3de1fa1...`) contém `Game\THEMOD 1.3.exe` (cópia completa do executável do jogo, 122 bytes alterados) e `Game\data\pre\thethug2mod.prx`. Alterações: `jnz` do checksum de salvamento substituído por NOP (0x5A8A01; PartyMod faz o mesmo patch), um `jne` transformado em `jmp` no SDK de chave de CD do GameSpy (0x5F95BB, próximo de `gcd_init`; verificação on-line da chave, não do disco), arquivo de scripts de inicialização renomeado para `thethug2mod.pre` e nomes de servidores encerrados. A cópia do testador tem mais três alterações de outra pessoa (desfoque de tela desativado, 800x600 substituído por 1920x1080, servidor de chat de volta ao GameSpy). Distribuir o instalador distribuiria o executável do jogo; por isso, o mod inclui `patch_themod.bat` / `.ps1`: confere o `THUG2.exe` do jogador (tamanho, SHA-256, cada byte original) e escreve `THEMOD 1.3.exe` ao lado, SHA-256 `25874001be0c1f12df47bc8f0dad61869cae0fe90964c12245165732a4cbb5ea`, idêntico byte a byte ao executável do instalador.

## <a id="qa"></a>QA

- **Percurso com dois clientes por script** (ferramentas locais, não no repositório do mod): duas cópias em janela num PC por loopback, controladas por um canal de automação dentro do processo (`[debug] automation=1` envolve DirectInput e lê um arquivo de comandos por processo). 17 etapas: sala, início de Story, cenas introdutórias puladas pelo host, teleporte, objetivo vencido pelo host, mudança de capítulo para Boston, escolha de parceiro profissional, objetivo compartilhado obtido pelo amigo e concluído por ambos, Barcelona, retorno do amigo, derrota do host. Exibe as linhas de log que mostram cada etapa nos dois lados e falha apenas em encerramento inesperado; ainda não tem asserções PASS/FAIL por etapa nem variantes de mutação. Última execução em 2026-10-25: 17 etapas, sem falhas de processo. Sincronização de objetivos, chat e colisão também foram executados como cenários separados com capturas de tela (2026-10-26).
- **Jogo real**: sessão de cerca de meia hora, host e amigo pela internet via Porthole (compartilhamento de portas Steam). Encontrou mais bugs, corrigidos depois, e levou a opções em `coop.ini` (colisão entre jogadores, teclas, resolução). A compilação corrigida ainda não teve uma sessão real em dois PCs.
- **Não testado**: mod no executável exato gerado pelo patcher (somente na cópia THEMOD do testador, diferente nas três regiões de bytes acima, nenhuma com hooks); execução do patcher no Windows (tabela de bytes verificada ao aplicá-la em Python e comparar o SHA-256).

## <a id="how-to-play"></a>Como jogar

Baixe `thug2-coop.zip` em [Releases](https://github.com/LeftGamer1/thug2-coop/releases), extraia na pasta do jogo, execute `patch_themod.bat` se não houver `THEMOD 1.3.exe`, configure `name=` e, para o amigo, `host_address=` em `coop.ini`. Host: F10 no menu principal, depois Story Mode. Amigo: F11. O host precisa que UDP 5153 e TCP 5154 sejam acessíveis (VPN como Radmin/ZeroTier ou Porthole). Instruções completas no README do repositório.

## <a id="known-issues"></a>Problemas conhecidos

- Em alguns PCs, o jogo (também THEMOD 1.3 sem o mod) falha na tela inicial, observado em Windows 11 e em 2K; `[debug] windowed=1` evita isso.
- Em tela cheia, a resolução em `coop.ini` precisa ser aceita pelo monitor; caso contrário, o jogo fecha depois da tela inicial.
- Se o amigo sair e voltar à mesma fase, a fase do host recarrega.
- Decisões da história (próximo capítulo, mudança de fase, parceiro profissional) são exclusivas do host; só ele salva.

## <a id="next-steps"></a>Próximos passos

- Transformar o percurso em suíte com asserções PASS/FAIL por etapa e uma variante de mutação por recurso de sincronização.
- Jogar uma campanha completa em modo cooperativo e registrar as falhas (capítulos posteriores e objetivos especiais menos testados).
- Carregar `coop.qb` pela DLL em vez de acrescentá-lo ao arquivo de THEMOD, para o mod também funcionar sem os scripts de THEMOD.
