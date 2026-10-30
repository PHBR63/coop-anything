# <a id="divinity-ii-developers-cut-2012"></a>Divinity II: Developer's Cut (2012)

| | |
|---|---|
| Motor | Derivado de Gamebryo ("Divinity Application", Larian Studios); DX9, PhysX, Lua 5.1 embutido + scripts Osiris |
| Versões testadas | Developer's Cut v1.4.700.49, pacote não oficial (não Steam/GOG); SHA-256 do executável `633B8EC683FD7CACE512F40E1943731FA9DA1342DB081E0A5657B6FEEEB9C8BB`. Compilações Steam/GOG não testadas; provavelmente exigem localizar os endereços novamente. |
| Projetos | Base para tela dividida de 2 jogadores em um PC (esta pasta; ainda sem repositório separado) |
| Nível de QA | automated (camada de isolamento de perfil por instância; alcance exato em QA) |
| Última atualização | 2026-10-18 |

## <a id="where-things-stand"></a>Situação atual

Hoje ninguém consegue jogar Divinity II junto. O executável não tem código de rede (nenhuma importação ou texto de sockets/salas) e não foi encontrada tentativa cooperativa anterior. O projeto está na etapa de fundação: um proxy `dinput8.dll` já é injetado no jogo, e duas instâncias recebem perfis e salvamentos totalmente separados, verificados com duas instâncias reais. Ainda não há jogabilidade cooperativa. Duas instâncias podem rodar em um PC, mas iniciar simultaneamente é instável (condição de corrida no reprodutor de vídeo do menu principal do motor, bug anterior ao nosso trabalho).

## <a id="existing-work"></a>Trabalhos existentes

Nenhum encontrado. Pesquisa em 2026-10-18: nenhuma entrada no diretório deste repositório; buscas pela API GitHub por divinity2 co-op / dv2 unpack retornaram 0 resultados; a seção técnica de Divinity 2 no fórum Larian não tem discussões de modo cooperativo, multiplayer ou carregadores de mods (comunidade praticamente inativa desde 2012); uma varredura do binário não encontrou textos nem importações multiplayer. NexusMods respondeu HTTP 403 no ambiente de pesquisa; não foi conferido manualmente. Se houver mod lá, ele não foi visto aqui. Veredito: criar do zero.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- Motor: "Divinity Application", derivado de Gamebryo, PE de 32 bits (WOW64 no Windows moderno), base da imagem `0x400000`, DX9 + PhysX, runtime VS2008.
- Scripts: máquina virtual Lua 5.1 ligada estaticamente (tabela de registro da API C próxima ao VA `0x014C6448`) e Osiris, sistema de scripts de comportamento da Larian (que estreou neste jogo). Lógica de missões/mundo em gatilhos XML e scripts compilados dentro de pacotes `.dv2`; sem carregador público de mods.
- Código de rede: absolutamente nenhum. Sem importações `ws2_32`/winsock. Todo o código de rede cooperativo precisa ser adicionado.
- Proteção de instância única: semáforo nomeado `"Div2Lock"` (texto no VA `0x1476B04`; função de proteção tenta por aproximadamente 15 s e encerra). Uma segunda cópia pode rodar se o texto for renomeado no executável (mesmo comprimento, uma ocorrência).
- Perfil/salvamentos: construídos por `SHGetFolderPathA` com `CSIDL_LOCAL_APPDATA` (três locais de chamada; somente `0x1c` importa) em `%LOCALAPPDATA%\Divinity 2\`, compartilhado na máquina (Profile + Savegames). Todas as cópias usam o mesmo local, a menos que sejam redirecionadas. O local `0x23` constrói cache de shaders regenerável em ProgramData; `0x05` só verifica existência e nunca escreve.
- Ponto de injeção: o executável importa exatamente uma função de `dinput8.dll` (`DirectInput8Create`) -> um proxy `dinput8` é a forma mais limpa de inserir código no processo.
- A compilação de depuração (`Divinity2-debug.exe`) oferece console F11 com comandos de teleporte / invencibilidade / atribuição de scripts Lua; útil para futuros testes de representantes cooperativos.

## <a id="what-we-changed"></a>O que alteramos

1. Injeção por proxy `dinput8` (Etapa 1, `stage1/`).
   - Necessidade: executar código no processo; o jogo não tem carregador de mods.
   - Correção: `dinput8.dll` de 32 bits que carrega a `dinput8.dll` real do sistema e encaminha `DirectInput8Create`. A forma de exportar importa: a implementação é uma função stdcall e um alias `.def` (`DirectInput8Create = DefDirectInput8Create@20`) produz o nome sem decoração importado pelo jogo, com `ret 20` nativo. Compilado com llvm-mingw (clang i686); TinyCC foi tentado e falha nisso (decoração stdcall ou pilha quebrada); Zig não pôde ser utilizado pela rede de testes.
   - Teste: a enumeração de módulos mostrou proxy e `dinput8` do sistema carregados no jogo; o log registrou attach -> load real -> forward; o jogo ultrapassou a janela de falha de 60 s sem evento de falha; um chamador isolado, sem DirectInput, recebeu o `E_NOINTERFACE` esperado e permaneceu vivo, comprovando a limpeza correta da pilha.

2. Redirecionamento de perfis e salvamentos por instância (Etapa 2, `stage2/`).
   - Bug: todas as cópias compartilham um perfil da máquina; configurações sobrescrevem umas às outras e salvamentos automáticos fariam o mesmo.
   - Causa raiz: a raiz do perfil vem de `SHGetFolderPathA(CSIDL_LOCAL_APPDATA)`; o motor não aceita caminhos por instância.
   - Correção: o proxy da Etapa 1 recebe hook MinHook em `SHGetFolderPathA` (pelo nome, para continuar válido em outras compilações), ativado pela variável de ambiente `DIV2_INSTANCE`: definida com um token curto, esse token vira segmento da raiz da instância, e cada cópia recebe seu próprio `...\Divinity 2\Profile\` e `Savegames\`. Ausente ou inválido -> sem redirecionamento; o jogo normal com uma instância não é alterado. O token é validado (comprimento e caracteres de caminho), impedindo que um valor malformado escape da pasta base.
   - Teste: `test-hook.ps1` inicia ambas as cópias com tokens, calcula hashes do perfil real antes e depois e verifica gravações no encerramento e eventos de falha. Nas cinco execuções, o perfil real permaneceu intacto (0 arquivos alterados), e as gravações finais foram para os perfis redirecionados por token. Veja a ressalva de coexistência em QA.

3. Estrutura de teste da segunda cópia (não é recurso para jogadores).
   - Necessidade: executar duas cópias de um jogo de instância única nos testes acima.
   - Correção: segunda pasta com `Data`/`images` como junções aos dados compartilhados (sem duplicar 7 GB), e texto `Div2Lock` renomeado no executável.
   - Teste: ambas chegaram juntas a menus principais estáveis (usuário confirmou duas janelas); a segunda sozinha também roda e encerra sem problemas, comprovando que a cópia está íntegra.

4. Bug conhecido do jogo documentado, não corrigido: o reprodutor de vídeo do menu principal passa um objeto de vídeo NULL a uma função de definição (RVA da falha `0xB1024A`; chamador é o reprodutor do menu). Sob disputa entre duas instâncias (dois aplicativos DX9 + dois decodificadores WMV na mesma GPU), ocorre violação de acesso não tratada ou encerramento antecipado com código 0. Isso antecede nosso trabalho e torna instável a inicialização das duas instâncias.

## <a id="qa"></a>QA

- Como executar: `stage1/build.ps1` e `stage2/build.ps1` compilam os proxies (verificações de PE32 / exportação / `ret 20`, SHA-256 exibido); `stage2/test-hook.ps1` executa o teste de duas instâncias e verifica: alvo do hook é o verdadeiro `shell32!SHGetFolderPathA`, redirecionamento ocorre nos valores CSIDL relevantes, árvores de perfil por token são criadas, perfil real não tem arquivos alterados em relação à captura SHA-256 anterior e nenhum evento novo de falha aparece.
- Último resultado da suíte (2026-10-18, cinco inicializações): verificações de isolamento passaram em todas (perfil real intacto; gravações finais em perfis por token). Coexistência de duas instâncias é instável: 1 execução simultânea atingiu a falha conhecida do vídeo (WER 1000); em 2 execuções com início escalonado a segunda instância encerrou cedo com código 0; em 1 escalonada ambas permaneceram vivas por mais de 40 s; 1 controle só com a segunda cópia foi saudável (saída 0 após 75 s). Portanto: camada de isolamento = aprovação determinística; duas instâncias simultâneas saudáveis = dependente do tempo, ainda não confiável.

## <a id="how-to-play"></a>Como jogar

Ainda não: não existe versão cooperativa distribuída. As DLLs e scripts aqui são artefatos da estrutura de testes, não um mod para jogadores. Quem quiser reproduzir a camada de isolamento pode compilá-la a partir do código com os scripts `build.ps1` (llvm-mingw, alvo i686) e o código MinHook incluído.

## <a id="known-issues"></a>Problemas conhecidos

- Executar duas instâncias ao mesmo tempo não é confiável: a segunda às vezes encerra imediatamente ou atinge a falha do vídeo do menu (veja acima). Cada cópia é saudável isoladamente; a camada de isolamento em si é determinística.
- Tudo aqui está vinculado a uma compilação do executável (endereços acima para SHA-256 `633B8EC6...EB9C8BB`). Em cópia Steam/GOG será necessário reencontrar endereços por texto, embora o hook `SHGetFolderPathA` seja independente da compilação por projeto.
- A cópia testada é um pacote não oficial, não Steam/GOG. Amigos com cópia de loja podem ter outra compilação; a correspondência de versões precisa ser verificada antes de qualquer plano de jogar juntos.

## <a id="next-steps"></a>Próximos passos

- Etapa 6b: ciclo de tentativas de inicialização e/ou desativação/pulo do vídeo do menu para iniciar duas instâncias com segurança.
- Usar a tabela de registro da API Lua C (próxima ao VA `0x014C6448`) como canal de controle para comandar um segundo personagem pela DLL injetada.
- Depois, o núcleo real de sincronização cooperativa, conforme `playbook/how-coop-mods-work.md` deste repositório, e encaminhamento de janelas/layout/entrada conforme `playbook/split-screen.md`.
