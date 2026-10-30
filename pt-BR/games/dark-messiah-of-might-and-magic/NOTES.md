# <a id="dark-messiah-of-might-and-magic-working-notes"></a>Dark Messiah of Might and Magic: notas de trabalho

## <a id="game-identity-observed-2026-10-23"></a>Identidade do jogo (observada em 2026-10-23)
- Loja: Steam, appid 2100 ("Dark Messiah of Might & Magic Single Player"), buildid 49752
- SHA-256 de mm.exe (original): f8faaee53a2c9ed72b8c7b83b75608f96a77ab07f374314950701901bda7e34c, 3727360 bytes
- Motor: Source (ramificação de 2006, fork da Arkane). Sistema operacional: binário Windows, executado aqui com Proton no Linux.

## <a id="triage-observed"></a>Triagem (observada)
- Modo cooperativo existente: wiltOS "Dark Messiah Co-op", de KingDavidW, versão A2-03.23 (info.json), repositório https://github.com/KingDavidW/DarkMessiah-Coop-Mod-Files, último push em 2026-03-23, GPL-3.0, distribui bin/dmcoop_server.dll + bin/dmcoop_client.dll pré-compiladas (sem código-fonte no repositório).
- Depende de: wiltOS Mod Launcher (https://github.com/KingDavidW/DarkMessiah-ModLauncher-Files, último push em 2026-03-11) e módulo base Advanced SDK (https://github.com/KingDavidW/DarkMessiah-AdvancedSDK-Mod-Files, último push em 2026-03-23).
- Parâmetros de inicialização de info.json: -insecure, +setmaster add master.wiltostech.com:27010, gameinfo +type singleplayer_and_multiplayer.
- O mm.exe do inicializador (SHA-256 74bb913ef6fc259d8eaa18eae317d9cf1b36c6be905a8f82a065b049e709ec69) difere em 9 bytes do mm.exe original com buildid 49752 (cmp -l). Mesmo tamanho. Finalidade do patch: desconhecida (hipótese deduzida: hook do carregador para bin/wos_dmmm.dll).
- Predecessor antigo: https://github.com/Balimbanana/DarkMessiahCoopSetup (último commit em 2023-03-16), edições de lumps via -tempcontent; creditado no README do wiltOS pelas alterações cooperativas iniciais.

## <a id="known-bugs-from-github-issues-open-as-of-2026-10-23"></a>Bugs conhecidos (issues do GitHub, abertas em 2026-10-23)
- #13 [Linux/Proton] "Platform Error: module failed to initialize" com o módulo cooperativo ativado; sem resposta.
- #8 Roda da grade levadiça fora de sincronia, podendo impedir o progresso; alternativa: soltar Use antes da rotação completa.
- #16 Latência alta com ZeroTier; #1 atraso de entrada do cliente com ping de aproximadamente 150; cvars sugeridas: cl_predict 0, cl_interp 0.01, cl_interp_npcs 0.6 (comentário do mantenedor em 2025-02-14).
- HUD: #9 temporizador de recarga, #10 mana exibida com limite de 29, #11 ausência da barra de fôlego debaixo d'água; #12 nomes ausentes no chat; #3 oscilação da cabeça após usar arco; #5 interface furtiva; #6 conflitos com o pacote de mods Unlimited Edition.

## <a id="unknown"></a>Desconhecidos
- Se #13 ainda é reproduzível com A2-03.23 no Proton atual.
- Máximo de jogadores e alcance da sincronização de inimigos/mundo/itens.

## <a id="install--proton-test-2026-10-23-observed"></a>Instalação e teste com Proton (2026-10-23, observado)
- Commits fixados: ModLauncher 66aca607caa9af05f4e8ca21a2bbc967579d8cdd, AdvancedSDK c5a6fb8f84bf9e6bc4f463b45655d812d1d59e15, Coop 04f3c881cc1a6dc96cbffdffbe23147df1abaec0.
- SHA-256: wos_dmmm.dll 4b3c5bc9...8c83a, client_sdk.dll a15b4746...54bc3, server_sdk.dll cec5327a...0b9d, dmcoop_client.dll 713cd676...1f385, dmcoop_server.dll 4d94721a...3209 (hashes completos em local/).
- O inicializador sobrescreve 6 arquivos da raiz do jogo: mm.exe, steam.dll, steam.inf, steamclient.dll, tier0_s.dll, vstdlib_s.dll. O repositório do inicializador distribui `Steam.dll` (S maiúsculo); o jogo tem `steam.dll`. Em um sistema de arquivos Linux sensível a maiúsculas e minúsculas, uma extração simples deixa OS DOIS arquivos. Copiamos por cima de `steam.dll`.
- A ordem dos mods pode ser definida sem interface gráfica: `_mods/core/user_settings.json` -> "load_order": ["advanced_sdk","dm_coop"].
- Proton Experimental, SteamLinuxRuntime_4, KDE Wayland: a interface do inicializador aparece; "Launch with Mods" carrega server_sdk.dll, client_sdk.dll, dmcoop_server.dll, dmcoop_client.dll (verificado em /proc/<pid>/maps); o menu principal exibe Find Servers / Create Server. A issue #13 "Platform Error" NÃO foi reproduzida.
- `steam -applaunch 2100` em um shell não fez nada (nenhum GameAction em console_log); `xdg-open steam://rungameid/2100` funcionou.
- Ainda não testados: hospedar uma sessão, entrada de cliente, qualquer sincronização durante a partida.

## <a id="tester-playtest-2026-10-24-reported-by-a-tester-not-measured"></a>Sessão de teste de jogador (2026-10-24, relatada por um testador, sem medições)
- Host Linux (Proton), clientes Windows por IP público e UDP 27015 redirecionada. A sessão funcionou.
- "sync was a bit off", "climbing on chains a bit laggy" (sincronização um pouco imprecisa; subir em correntes com algum atraso). Desconhecidos: ping, quantidade de jogadores e cvars usadas.
