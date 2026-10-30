# <a id="shipping-to-players-one-file-per-os"></a>Distribuição aos jogadores: um arquivo por sistema operacional

O mod funciona no seu PC. Agora seu amigo precisa instalá-lo, e cada etapa manual (encontrar a pasta do jogo, escolher a compilação correta do carregador, descompactar no lugar certo, definir uma opção de inicialização) é uma oportunidade de desistir ou cometer um erro sutil. Distribua **um arquivo por sistema operacional** que faça a instalação inteira e teste-o da mesma forma que o jogador o executará.

Aprendizado de Planetbase ([games/planetbase](../games/planetbase/README.md)): explicar a instalação manual a um amigo levou mais tempo que a sessão. Um `.bat` para Windows e um `.sh` para Linux que fazem tudo colocaram o segundo jogador no jogo na primeira tentativa. MDK2 HD ([games/mdk2-hd](../games/mdk2-hd/NOTES.md)) distribui a mesma ideia como um script PowerShell com invólucros `.cmd`.

## <a id="what-the-file-does-in-order"></a>O que o arquivo faz, em ordem

1. **Encontre o jogo sem perguntar.** Leia o caminho de instalação do Steam (registro do Windows `HKCU\Software\Valve\Steam` `SteamPath`, depois `HKLM\SOFTWARE\WOW6432Node\Valve\Steam` `InstallPath`; no Linux, `~/.steam/steam`, `~/.local/share/Steam` e caminhos Flatpak e Snap), analise cada biblioteca em `steamapps/libraryfolders.vdf` e leia `installdir` de `appmanifest_<appid>.acf`. Ofereça `--game-dir` para os demais casos.
2. **Confira a compilação do jogo** antes de escrever: compare o hash do arquivo do qual o mod depende (executável principal ou `Assembly-CSharp.dll` para Unity) com a compilação testada. Se não corresponder, explique como restaurá-lo (Steam > Verificar integridade) e pare, a menos que o jogador insista.
3. **Instale o carregador** (BepInEx, UE4SS, extensão de scripts) pela URL oficial da versão, com versão fixada e conferência de SHA-256. Escolha a arquitetura correta: Planetbase é de 32 bits e o BepInEx x64 não carrega. Se já houver carregador, confira se é a compilação correta em vez de reinstalar por cima.
4. **Instale o mod** da mesma forma: arquivo fixado, SHA-256 conferido e backup da versão anterior.
5. **Defina o necessário para o sistema operacional.** No Proton, BepInEx exige a opção de inicialização `WINEDLLOVERRIDES="winhttp=n,b" %command%`. O Steam guarda opções de inicialização em `userdata/<id>/config/localconfig.vdf` e reescreve esse arquivo ao encerrar; portanto, feche o Steam antes (peça autorização), faça backup, altere apenas esse valor e combine com um `WINEDLLOVERRIDES` existente em vez de substituí-lo.
6. **Ofereça iniciar o jogo** (`steam://rungameid/<appid>`) e exiba as duas linhas necessárias ao jogador: como hospedar e como entrar.
7. **Desinstale pelo mesmo arquivo** e **atualize executando-o novamente**.

## <a id="what-it-must-not-do"></a>O que o arquivo não deve fazer

- Executar qualquer download sem consentimento do jogador. Um script que substitui a si mesmo equivale a executar um script baixado sem lê-lo (regra 8 de AGENTS.md): peça autorização e nunca faça isso em execução não interativa ou com `--yes`; apenas informe que existe uma versão mais recente.
- Confiar em um hash obtido no mesmo lugar que o arquivo. Um manifesto junto ao mod detecta corrupção, não um repositório comprometido; fixe o hash do carregador no próprio script.
- Escrever fora da pasta do jogo, exceto no único arquivo da plataforma que precisa alterar (com backup prévio).
- Pedir direitos de administrador logo no início. Tente e, se a pasta estiver protegida, ofereça reiniciar com elevação.
- Esconder o que fez. Mantenha um log, mostre um resumo e indique-o em toda mensagem de erro.

## <a id="make-it-usable-by-someone-who-never-opened-a-terminal"></a>Torne utilizável por quem nunca abriu um terminal

- Windows: um `.bat` aberto com duplo clique. Um `.bat` pode conter seu corpo PowerShell após um cabeçalho `<# : ... #>`, mantendo tudo em um arquivo. Espere a mensagem "Windows protected your PC" do SmartScreen; diga no README quais botões pressionar.
- Linux: `bash file.sh`. Confira as ferramentas necessárias (`curl` ou `wget`, `sha256sum`, `unzip`) e mostre o comando de instalação para as principais distribuições quando faltar alguma.
- Toda falha termina com uma caixa explicando o que fazer em linguagem simples, não com um rastreamento de pilha.
- Menu por padrão (instalar ou atualizar, desinstalar, sair); `install`, `uninstall`, `--yes` e `--game-dir` na linha de comando para permitir controle pelos testes.

## <a id="test-it-like-a-player"></a>Teste como um jogador

Execute em cópias de teste, nunca na instalação do usuário (regra 2 de AGENTS.md). Os scripts de Planetbase leem substituições por variáveis de ambiente (`COOP_STEAM_ROOT`, `COOP_FAKE_STEAM_RUNNING`, um `COOP_SOURCE` local) para que um teste aponte para uma pasta Steam simulada e uma versão local. Cubra: primeira instalação, atualização sobre a versão anterior, recusa de compilação incorreta do jogo sem alterar nada, desinstalação e segunda execução que encontre tudo já concluído. Instale a versão anterior como um jogador antes de testar uma atualização: a atualização de Jericho Co-op+ falhou para jogadores com dois atalhos porque todos os testes usavam apenas um ([lessons.md](lessons.md), lição 45).

Depois envie o arquivo para alguém que nunca viu o mod e observe onde essa pessoa encontra dificuldades.
