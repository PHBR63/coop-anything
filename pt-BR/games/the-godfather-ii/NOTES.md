# <a id="the-godfather-ii--research-notes"></a>The Godfather II — notas de pesquisa

Verificado: 2026-10-20. Objetivo: campanha de história do PC jogável em cooperativo.

Issue de atribuição: <https://github.com/cranebeaker/coop-anything/issues/78>.

## <a id="identity"></a>Identidade

- **Observado:** versão PC; o objetivo é cooperativo na campanha de história.
- **Jogo:** The Godfather II (2009), desenvolvido pela EA Redwood Shores; PCGamingWiki identifica a engine como Visceral Engine.
- **Loja / ID do pacote:** desconhecido. O executável candidato limpo informa `1.0.764.0`; seu SHA-256 é mantido apenas em `local/identity.md`, ignorado pelo Git.
- **Decisão sobre a build alvo (2026-10-20):** depois de se comprovar que SE v0.56 é incompatível com `1.0.764.0`, a build testada mudou para `1.0.789.0`, obtida do pacote SE v0.56 — um executável de terceiros não verificado, usado apenas como alvo de teste descartável, e não como build a seguir. A cópia isolada `1.0.764.0` é mantida apenas como referência; a iteração acontece em novas cópias isoladas (atualmente `%LOCALAPPDATA%\Temp\opencode\godfather2-test-se`, cuja instalação de origem permanece intacta). O executável `1.0.789.0` incluído no MPR permanece uma build `.789` separada, com bytes diferentes: sua descompilação existente (33.506 funções) corresponde ao executável MPR, não ao SE, e portanto não pode ser usada como base de análise para trabalho com deslocamentos SE. O executável `1.0.789.0` veio do arquivo Multiplayer Revival e não é a build alvo.
- **Sistema operacional alvo:** Windows, com base na instalação Windows fornecida. A instalação original e os saves não foram modificados.
- A página Nexus de Multiplayer Revival diz que exige a build PC `1.0.789.0`, que é o executável incluído no MPR. Isso não estabelece compatibilidade com o alvo limpo `1.0.764.0`; não instalar nem usar MPR nesse alvo.

## <a id="existing-work"></a>Trabalho existente

### <a id="multiplayer-revival-not-story-co-op"></a>Multiplayer Revival (não é cooperativo na história)

- Página: <https://www.nexusmods.com/thegodfather2/mods/95>, de `paindubreak`.
- O autor diz que restaura o multijogador online original do PC usando um servidor de matchmaking da comunidade. Jogadores hospedam partidas; o tráfego do jogo é ponto a ponto. A página descreve lobbies, entrada rápida e hospedar/entrar, não cooperativo na campanha nem estado compartilhado de história.
- Compatibilidade declarada pelo autor: versão PC `1.0.789.0` e um carregador ASI. O cabeçalho da página diz versão 1, enquanto a lista de arquivos diz versão 2 (último envio em 2026-08-06). Nenhum arquivo Nexus foi baixado; um `.asi` copiado preexistente teve seu hash calculado e foi analisado estaticamente, mas não comparado a um hash de arquivo compactado.
- A página lista zero bugs formais, mas suas publicações incluem problemas de conexão/firewall e um relato de limite de 25 FPS. A resposta do autor de 6 de agosto diz que o arquivo inclui um carregador ASI e um executável de Godfather II; inspecionar o conteúdo de qualquer pacote e seus termos de redistribuição antes de usá-lo. Nenhum mod foi baixado ou instalado nesta sessão.
- O serviço online original consta como encerrado no PCGamingWiki. Sua página descreve jogo online para até 16 pessoas e hospedagem própria de partidas personalizadas. A cobertura da época descreve modos multijogador separados, baseados em mapas, incluindo mata-mata em equipe, em vez de campanha compartilhada: <https://www.ign.com/articles/2009/03/18/the-godfather-ii-gets-multiplayer-mode>.
- **Não verificado:** conexão bem-sucedida, sincronização exata do gameplay, comportamento de NAT ou se algum modo oferece cooperativo contra IA.

### <a id="the-godfather-ii-se-a-promising-modding-hook-not-co-op"></a>The Godfather II SE (um ponto promissor para mods, não cooperativo)

- Página: <https://www.nexusmods.com/thegodfather2/mods/40>, de `Greavesy` / `Greavesy899`.
- A versão mais recente listada é `v0.56` (atualizada em 2026-08-26). Sua página descreve um extensor de scripts/menu de mod, carregamento de mods em arquivos soltos, criação de NPCs/itens/veículos, carregamento de checkpoints e substituições SimGroup. Este é o ponto de integração mais forte encontrado até agora para um plugin cooperativo separado, mas nenhum desses recursos prova que exista replicação de campanha.
- A página diz que o arquivo inclui um executável sem DRM. Não foi encontrado link de código-fonte nem licença do extensor; não redistribuir seu executável nem presumir que seu código possa ser reutilizado.
- O manifesto de arquivos Nexus v0.56 lista `GF2ASI.asi`, `dinput8.dll`, `discord_game_sdk.dll`, dados de mod SimGroup e um `godfather2.exe` incluído (SHA-256 do manifesto `31f579a80cfd14f42c0379bbfa5b5b7f151bb06ec5163593023ab5002b1f1286`).
- O arquivo SE v0.56 foi fornecido para teste; seu SHA-256 (`653d037000801abf45133d7f1a011749c71c83c529336b799feb5aeb0b90253f`, 6.055.436 bytes) corresponde ao hash do arquivo no manifesto Nexus, e os 7 arquivos extraídos correspondem aos valores SHA-256 individuais do manifesto. O pacote é autêntico ao Nexus; nada foi hospedado novamente.
- Inspeção do arquivo verificado: o `godfather2.exe` incluído informa versão de arquivo `1.0.789.0` (13.840.384 bytes). Seus bytes diferem dos do executável incluído em Multiplayer Revival (mesma versão e tamanho, SHA-256 `d0339a3d79e73ee8ec542cda79608e8194f0f68d916b74115c59dce0267ae97f`), portanto cada mod distribui sua própria build `.789`. `simgroup_mods/README.txt` documenta que o carregador injeta comportamentos de substituição SimGroup (arquivos `.sgp` de VisceralToolkit) quando o jogo carrega um fluxo SimGroup `.str`; `gf2asi_settings.ini` documenta interceptações de VSync/cadenciamento de quadros e correções de brilho/contraste. Nenhum arquivo declara uma faixa de builds suportadas além do executável incluído.
- **Veredito de compatibilidade:** SE v0.56 exige a build `1.0.789.0` e portanto é incompatível com o alvo limpo `1.0.764.0`. Pela regra de parada, ele não foi instalado na cópia limpa; foi apenas baixado, verificado por hash e extraído em uma pasta separada de inspeção (`%LOCALAPPDATA%\Temp\opencode\godfather2-tools\inspect\se-v0.56`).
- O indicador de bugs Nexus mostrava 3 na verificação. Sua lista visível incluía um crash ao tornar Michael Corleone membro da equipe (relatado para v0.34, última publicação em 2026-09-29), um problema v0.56 marcado como corrigido (última publicação em 2026-09-03) e relatos mais antigos de "não funciona" / inicialização. São relatos do mod, não testes de cooperativo.
- Uma publicação de 25 de setembro de 2026 também relata crash na inicialização com mensagem "api doesnt work"; o autor pediu o erro completo e a lista de mods instalados em 28 de setembro. Nenhuma solução estava visível na verificação.

### <a id="related-engine-tooling"></a>Ferramentas relacionadas à engine

- <https://github.com/Greavesy1899/VisceralToolkit> descreve ferramentas em desenvolvimento para inspecionar/editar jogos Visceral, incluindo The Godfather II. Pode ajudar a inspecionar recursos de fluxos, mas não é um framework cooperativo; o GitHub informa ausência de licença de repositório. Seu conteúdo não foi clonado nem compilado.
- A wiki do toolkit diz que Godfather II usa arquivos de fluxo `.str` versão 12; carregar e salvar no PC são suportados, a edição é parcial e adicionar novas entradas não é suportado. Suas notas de tipos de recursos identificam grafos de navegação, MetaModels e um `VariableDictionary`, mas marcam a maioria dos formatos como desconhecidos e as páginas como incompletas. São pistas, não APIs verificadas de scripts/missões: <https://github.com/Greavesy1899/VisceralToolkit/wiki/File-Resource-Type-Support> e <https://github.com/Greavesy1899/VisceralToolkit/wiki/Resource-Types>.
- PCGamingWiki lista Dead Space 3 com a mesma engine denominada Visceral Engine e documenta uma campanha cooperativa online para dois: <https://www.pcgamingwiki.com/wiki/Dead_Space_3>. É uma referência útil da família de engine, não evidência de que seu código de rede ou ferramentas possam ser reutilizados em The Godfather II.

## <a id="static-binary-observations-isolated-copies-no-binaries-published"></a>Observações estáticas dos binários (cópias isoladas; nenhum binário publicado)

- O `godfather2.exe` `1.0.789.0` incluído no MPR é PE32 x86 e importa `WS2_32.dll` e `DINPUT8.dll`, entre outras APIs Windows. Isso confirma APIs de rede naquele executável, não na build limpa verificada `1.0.764.0`, nem que a campanha de um jogador use replicação multijogador.
- A cópia limpa `1.0.764.0` tem seções PE chamadas `.securom`, `Stext`, `Sitext`, `Srdata`, `Sdata` e `Sidata`; também inclui `paul.dll`. PCGamingWiki lista SecuROM 7.38.0015 para o lançamento comercial no PC. Tratá-la como protegida por DRM; a procedência exata da loja continua desconhecida.
- O `Multiplayer.asi` de Multiplayer Revival também é PE32 x86. Seus imports incluem Winsock (`WS2_32.dll`) e APIs de leitura INI; strings incorporadas mencionam redirecionamento FESL, `Multiplayer.ini`, `Multiplayer.log` e MinHook. Ghidra headless descompilou 84 funções. Seu caminho de entrada da DLL chama `SetProcessDEPPolicy(0)`, grava NOPs nos endereços absolutos `0x006A2B5A` e `0x0068D1B2`, depois inicia uma thread de trabalho no endereço de plugin `0x6B3417D0`. Esses patches e o comportamento da thread não foram mapeados/validados contra o executável alvo. O plugin deriva seus caminhos INI/log ao lado do próprio módulo, portanto o caminho efetivo depende de onde o ASI é carregado. **Ainda não iniciar este plugin:** sua mudança de DEP não foi avaliada em sandbox. Nenhum teste em execução foi feito.
- O inventário de arquivos da cópia `1.0.789.0` incluída no MPR encontrou 2.304 arquivos `.str` soltos, incluindo caminhos na hierarquia de missões/objetivos de Cuba; nenhum `.lua`, `.script`, `.sc` ou `.sco` foi encontrado. Seus arquivos `.db` são `Thumbs.db`, e seus `.xml` são documentos EA Help. A amostra de `GODFATH0.viv` começa com `BIGF`; amostras de arquivos `.str` versão 12 começam com `3slo`. A wiki de VisceralToolkit diz que esses fluxos contêm recursos variados e a maioria dos formatos continua desconhecida, portanto isso não estabelece onde os scripts de história são executados.

## <a id="runtime-isolation-check"></a>Verificação de isolamento em execução

- Windows Sandbox foi habilitado após aprovação explícita. Um teste inicial confirmou que o convidado tinha seu próprio perfil/caminho Documents de `WDAGUtilityAccount`, a cópia limpa do jogo estava mapeada somente para leitura e a rede estava desativada.
- Duas sondagens de inicialização offline na cópia limpa `1.0.764.0`: `godfather2.exe` iniciou e permaneceu ativo por 60–75 segundos, mas não tinha título de janela principal nem janela visível. Respondia segundo a API de processos, depois foi parado dentro do Sandbox. Isso não prova que o jogo chegou ao menu; nenhum gameplay nem sessão de rede foi executado. Instalação original e saves intactos.
- Uma terceira sondagem com `VGpu` habilitada mostrou comportamento idêntico (processo ativo, nenhuma janela visível para o PID do jogo), então a janela vazia não é explicada pela GPU virtual desabilitada. A execução vGPU foi um teste único aprovado, com a rede ainda desativada.
- Uma quarta sondagem que examinou **todas** as janelas do convidado encontrou a causa real: o processo do jogo estava preso atrás de um diálogo de erro de sistema Windows, `godfather2.exe`, informando ausência de `d3dx9_40.dll`; o processo mostrava 0 segundos de CPU enquanto esperava e terminou com código `-1073741515` (`0xC0000135`, STATUS_DLL_NOT_FOUND) quando o diálogo foi dispensado. Uma execução Sandbox posterior informou ausência de `XINPUT1_3.dll`. Ambas pertencem ao runtime legado DirectX 9.0c (DirectX End-User Runtimes, junho de 2010), que um convidado Windows Sandbox limpo não inclui. As observações anteriores de "processo ativo sem janela" eram esse diálogo esperando OK, e o filtro de janela visível não o atribuía porque pertence a outro PID (744). O host Windows 11 executa o jogo, então seu runtime DirectX mascara isso fora do Sandbox.
- Com aprovação explícita, o pacote completo DirectX End-User Runtimes (junho de 2010) foi baixado diretamente do link do centro de downloads Microsoft publicado na página deles (versão 9.29.1974.1, 100.275.120 bytes, SHA-256 `053f76dcbb28802e23341b6a787e3b0791c0fa5c8d4d011b1044172dbf89c73b`; o mesmo hash é registrado independentemente na discussão do repositório winetricks e em outras bases de checksums). Apenas as duas DLLs necessárias foram obtidas de seus CABs (`d3dx9_40.dll` 9.24.950.2656 de `Nov2008_d3dx9_40_x86.cab`; `XInput1_3.dll` 9.18.944.0000 de `APR2007_xinput_x86.cab`); ficam preparadas para a pasta do jogo do convidado em vez de instaladas no sistema, então nada no SO do convidado Sandbox é modificado além da cópia de teste descartável. Um teste de inicialização SE `.789` com essas DLLs preparadas é a verificação ativa.
- A desmontagem confirmou a cadeia de verificação (`local/ghidra_output/disasm_4c7b40_607990.txt`). A inicialização do dispositivo é `FUN_00607990`; a condição de hardware abaixo do mínimo é a pontuação GPU por adaptador de `FUN_0060f390` → `FUN_0060efc0` (9 = passa; 3 = falha de `GetDeviceCaps` → "Could not initialize display hardware"; 7 = `PixelShaderVersion < 0xFFFF0300`; 6 = bits ausentes de capacidades raster/prim; caso contrário, o avaliador de formato `FUN_0060ee70` precisa retornar 9), seguida por `CMP EAX,9 / JNZ …` em VA 0x00607a0c; a emissão em 0x00607b96 é `PUSH EAX` (a pontuação), mapeada pela função de diálogo às mensagens de "display hardware"/"minimum requirements". Apenas na cópia de teste SE descartável, o salto condicional de 6 bytes em 0x00607a0c foi substituído por NOPs (registro em bytes e hashes em `local/identity.md`); a build verificada intacta permanece sem patch, e nenhuma instalação foi tocada.
- Novo teste de inicialização após o desvio (Windows Sandbox, vGPU, rede desativada): a verificação de requisitos mínimos agora passa, e a inicialização para uma etapa depois, no código de erro 1 — "Could not initialize display hardware. Please restart The Godfather™ II." A janela do jogo existia desde o primeiro tick, o processo continuou respondendo com CPU acumulando enquanto o diálogo esperava, e o Sandbox terminou normalmente. Log `local/sandbox-output/gf2_se_boot.txt`, capturas por tick `gf2_se_boot_T20/60/120.png`. Isso move o bloqueio de inicialização da condição de capacidades para o caminho de criação de dispositivo/exibição.
- Uma sondagem D3D9 de 32 bits com vtable bruta foi criada para diagnóstico pontual (`local/dx9probe.c`, `local/dx9probe2.c` — nossos códigos C, chamadas brutas de vtable e conferência com `d3d9.h` oficial; compilados com LLVM-MinGW clang como PE32 x86; cada linha de log é descarregada para resultados parciais sobreviverem a um crash). Base no host com a GPU real: `Direct3DCreate9(32)` funciona, dois adaptadores enumerados, 97 entradas de modo X8R8G8B8, capacidades HAL informam PixelShader/VertexShaderVersion `0xFFFF0300`/`0xFFFE0300`, e os quatro campos de capacidades lidos pelo avaliador do jogo passam nos limites; pela interface oficial `d3d9.h`, `CreateDevice` retornou `D3D_OK` com ponteiros reais de dispositivo (em janela e tela cheia, SWVP e HWVP), um ordinal de adaptador inválido retornou corretamente `D3DERR_INVALIDCALL`, e REF falhou com seu próprio erro (rasterizador de referência ausente). Conjunto de constantes verificado para trabalho posterior: `D3DCREATE_SOFTWARE_VERTEXPROCESSING=0x20`, `HARDWARE=0x40`, `MIXED=0x80` — um bug anterior da sondagem passava `0x100000`, que o runtime comercial trata como comportamento indefinido em vez de HRESULT documentado. Nenhum arquivo do jogo, instalação ou save foi tocado pela sondagem.
- Observação de vtable da sondagem, resolvida (ambas as variantes registradas antes; agora explicadas): no objeto retornado por `Direct3DCreate9`, uma chamada bruta ao slot +0x3C retornava a constante `0x00010001`, enquanto uma chamada a +0x40 com argumentos no formato CreateDevice retornava `D3D_OK` e um dispositivo real. A declaração da interface oficial `d3d9.h` esclarece: `IDirect3D9` tem **14** métodos após IUnknown: slot 15 (+0x3C) é `GetAdapterMonitor`, e slot 16 (+0x40) é `CreateDevice`; a análise anterior havia contado errado a lista de métodos. `0x00010001` era um `HMONITOR`, não um HRESULT — uma chamada de controle `GetAdapterMonitor(0)` no slot +0x3C reproduz exatamente `0x00010001` no host. Conclusão: **a chamada de criação de dispositivo +0x40 do executável do jogo segue o layout oficial da interface e estava correta desde o início; a falha de inicialização é uma falha real do ambiente D3D9, não uma peculiaridade de ABI do jogo.** No host, o slot CreateDevice pertence a `C:\Windows\SYSTEM32\d3d9.dll`; em um processo anterior do host, o mesmo slot apontava para um segundo módulo (observação registrada; o módulo contêiner varia por processo).
- Resultado da sondagem no convidado (Sandbox vGPU) (execução final, binário convidado `d42f8b5e:`): D3D9 funciona pelo adaptador paravirtual — 1 adaptador, identidade informada como a GPU do host sob GPU-PV (modelo omitido), as capacidades HAL de classe host (incluindo PS/VS 3.0) estão todas presentes, e os quatro campos lidos pelo avaliador do jogo passam nos limites; mas a enumeração de modos expõe exatamente um modo de exibição de 32 bits (índices seguintes retornam `D3DERR_INVALIDCALL`). O controle `GetAdapterMonitor` no slot +0x3C retorna o mesmo HMONITOR do host, confirmando o layout. CreateDevice pelo slot oficial +0x40 tem sucesso no convidado para dispositivos HAL em janela — SWVP, HWVP, MIXED e focus=NULL retornaram `D3D_OK` com ponteiros reais — enquanto tela cheia exclusiva retorna `D3DERR_INVALIDCALL` (esperado em uma tela virtual de um modo), REF falha sem rasterizador de referência e NULLREF tem sucesso. Fato ambiental específico do convidado: a implementação CreateDevice do objeto IDirect3D9 é sustentada não pela imagem d3d9.dll, mas por `C:\Windows\SYSTEM32\apphelp.dll` (a engine de shims de compatibilidade de aplicativos envolve a interface D3D9 no convidado Sandbox). Conclusão para a falha de inicialização: "Could not initialize display hardware" do jogo modificado (código de erro 1) corresponde ao jogo solicitando uma configuração de exibição/modo que a tela virtual de um modo não atende — e a sondagem prova que dispositivos HAL simples em janela FUNCIONAM no convidado.
- Opções de modo de inicialização existem na própria tabela de strings do executável SE (lidas do binário `.789` verificado, sem modificar arquivo do jogo): `-windowed`, `-fullscreen`, `-resolution`, um arquivo de comandos `cmd.txt`, chaves de configurações de janela `Window.Fullscreen` / `Window.FullScreen`, `Window.Width`, `Window.Height`, `Window.Top`, `Window.Left`, `Window.VSync`, `Window.Hz`, `Window.State`, `Window.Bright`, `Window.Gamma` em `settings.txt`, mais as strings de interface `ClearResolutionList` / `AddResolutionOption` / "No supported resolutions available." Portanto, forçar modo em janela não exige patch no executável. O teste de inicialização v3 iniciou a cópia de teste `.789` modificada com `-windowed` (robocopy da pasta descartável apenas para o convidado; log sobrescrito por execução, como antes).
- Descompilação do executável SE (primeira execução Ghidra, concluída em 2026-10-20): 33.512 funções, projeto `gf2_game_10789_se`, corpus `local/ghidra_output/godfather2_10789_se.c` + índice de funções `.tsv`. O diálogo de falha gráfica é `FUN_0068b590` (@0x0068b590): parâmetro 2 = "Display hardware video memory exhausted", parâmetro 3 (ou 1, ou qualquer valor fora de 2..7 exceto a ramificação 4..7) = "Could not initialize display hardware", parâmetros 4..7 = "Your Graphics Card does not meet The Godfather® II minimum requirements.", depois `MessageBoxW(MB_ICONERROR-family 0x40010)` e `__exit(-1)`. O jogo o registra uma vez na inicialização do renderizador `FUN_0068bd30` (local 0x0068beab `PUSH 0x68b590; CALL 0x0060e780`) no slot `PTR_FUN_00f15a3c`; todas as emissões de erro passam por ele. Os códigos de erro visíveis no descompilador são apenas 1 (inicialização de dispositivo FUN_00607990), 2 (12 locais, validação de shaders/alvos) e 21 chamadas sem argumento que Ghidra omitiu (20 dentro de FUN_004c7b40 — o validador de técnica/shader/técnica — provável origem dos códigos 4..7). Foi gerado um dump completo da desmontagem de FUN_004c7b40 e FUN_00607990 para recuperar os códigos empilhados; o dump é `local/ghidra_output/disasm_4c7b40_607990.txt`. Patch candidato (apenas cópias de teste): redirecionar o imm32 de registro `PUSH 0x68b590` (4 bytes em 0x0068bead) para um stub em espaço livre que absorve códigos 4..7 e repassa o resto ao diálogo original — mantém visíveis falhas de inicialização/VRAM e deixa FUN_0068b590 intacta para diagnósticos futuros. Confirmado desde então: os códigos 4..7 vêm da comparação `CMP EAX,9 / JNZ` após a chamada do avaliador na inicialização de dispositivo, e o desvio menor que funcionou foi substituir esse salto por NOPs (ver os itens abaixo).
- Repetição com `VGpu` habilitada (mesma configuração vGPU; rede ainda desativada): o jogo novamente chegou à sua verificação de capacidades, e a captura do convidado mostra o mesmo diálogo, "Your Graphics Card does not meet The Godfather™ II minimum requirements."; o processo terminou com código `-1`. O log do convidado dessa execução registrou apenas o primeiro tick de observação (a captura de tela desativou varreduras posteriores), então a evidência do diálogo vem da captura mais a entrada de saída. Conclusão: a verificação de capacidades DirectX do jogo rejeita o caminho de exibição do Sandbox nos modos `WARP` e `vGPU`, possivelmente porque o adaptador paravirtual informa ausência de memória de vídeo dedicada, exatamente os critérios de "GPU da era de 1998" que um teste da era RTS usaria. Contornar essa única verificação na cópia de teste descartável (derivado da descompilação SE, apenas cópias de teste, nunca distribuídas) é o próximo passo para desbloquear. Log vGPU: `local/sandbox-output/gf2_se_boot.txt` (sobrescrito pela execução vGPU).
- Cadeia da causa concluída (2026-10-20, apenas cópias de teste). **Inicialização de exibição:** `FUN_00607990` monta `D3DPRESENT_PARAMETERS` via `FUN_006073e0` (chamada com as globais `Window.*`) ou recorre a `FUN_00608b50` (`memset` PP; `Windowed = (DAT_0120587f == 0)`; formato `A8R8G8B8` se tela cheia, caso contrário 0). A ramificação de tela cheia impõe às configurações o menor modo enumerado e depois escolhe um modo adequado; numa tela virtual de um modo, chega a `2032×1074@32`. `CreateDevice` é o slot oficial da vtable +0x40 com `pp = 0x011d9188` (área BSS de `.data` preenchida em execução — minha leitura anterior de "PP estático" foi um erro aritmético de endereço: `0x011d9188 − 0x400000 = 0x00DD9188`, além dos dados brutos da seção). Falha → `PUSH 1` em `0x00607b85` = "Could not initialize display hardware". **Configurações de inicialização:** `FUN_0068d010` lê `Window.Fullscreen` padrão **1** (`FUN_0069bc30("Window.Fullscreen",1)`; desmontagem `PUSH 0x1` em VA `0x0068d1d2`), `Window.Width` padrão `0x400`, `Window.Height` padrão `0x300`, `Window.Hz` padrão `0x3C`, e os aplica via `FUN_0069e3e0` (cria `Godfather2WndClass`) → `FUN_0068bd30` (inicialização do renderizador). `-windowed`/`-fullscreen` na linha de comando substituem a flag, mas sozinhos não salvaram a inicialização — a falha do convidado se repetiu. **Sondagem v5 (convidado, vGPU):** adicionados PPs no formato do jogo e variantes de tela cheia no modo nativo — janela funciona em todos os formatos testados (A8R8G8B8/X8R8G8B8, W/H 0 ou 800×600/1024×768/2032×1074, `IMMEDIATE`, profundidade automática D24S8, SWVP/HWVP/MIXED), enquanto **tela cheia exclusiva falha com `D3DERR_INVALIDCALL` em todas as variantes, inclusive no próprio modo enumerado do adaptador `2032×1074@32` com `hz` 0/32/60 e ambos os formatos** — a exibição paravirtual Sandbox não consegue alternar modos exclusivos. Conclusão: o jogo precisa rodar em janela no convidado. **Inicialização v4** (cópia de teste com padrão `Window.Fullscreen` modificado de 1→0 no deslocamento de arquivo `0x28D1D3`): o diálogo de inicialização de dispositivo desapareceu; novo crash `0xC0000005` (WER: módulo com falha `godfather2.exe`, deslocamento `0x0029F57F` → VA `0x0069F57F`). **Análise do crash:** `FUN_0069f440` é um detector legado de fabricante de GPU chamado por `FUN_0069f8b0` (inicialização de opções de qualidade) apenas quando `QualityOptions.ConfigType` está ausente das configurações; faz `strstr(DeviceID,"VEN_")` e desreferencia o resultado +4 **sem verificar NULL** — o `DeviceID` do adaptador paravirtual não contém `VEN_` → violação de acesso. **Inicialização v6** (cópia de teste também com entrada de `FUN_0069f440` modificada para `MOV EAX,4; RET` — caminho de "fabricante desconhecido"): **o jogo inicia em janela e chega à tela interativa de seleção de idioma** (inglês e vários outros idiomas europeus), continua respondendo com CPU acumulando por toda a janela de 160 segundos do harness, capturas `gf2_se_boot_T20/60/120.png`. `settings.txt`/`cmd.txt`/`joypad.txt` do convidado estavam ausentes após a execução; o carregador SE gravou um marcador `GF2SE.txt` vazio. Ambos os patches existem **somente** na cópia de teste descartável (`godfather2-test-se`), cujo SHA-256 atual é `201269a2…`; o pacote verificado intacto permanece intocado.
- **Marco (2026-10-20 23:27): o jogo chega ao menu principal dentro do Windows Sandbox.** Após escolha manual do idioma na janela Sandbox (o seletor de idioma não pôde ser confirmado por entrada injetada), o menu principal apareceu com `Resume Game / Play Online / New Game / Options / Unlocks / Credits / Bonus Materials / Select Profile / Quit to Windows` e versão `1.0.789.0` no canto inferior esquerdo. Captura `local/sandbox-output/seq_T150.png` (execução v10, log `gf2_se_boot.txt`). Descobertas de entrada dessas execuções: o procedimento de janela `FUN_0069de10` encaminha mensagens de mouse a `FUN_0069eb50`; `WM_MOUSEMOVE` move o destaque do menu apenas no modo relativo/delta (flag de captura `DAT_0112a065`), `WM_LBUTTONDOWN` não é tratado, e `WM_LBUTTONUP` alterna a captura do mouse via `FUN_0069e8b0` — cliques injetados moveram o destaque para Polski sem confirmar. O cursor do SO convidado é fixado pelo caminho de entrada RDP do Sandbox (`SetCursorPos` não tem efeito; `GetCursorPos` permaneceu 515,410), então um clique real do host é o caminho confiável de entrada por enquanto; entrada automatizada para QA precisará de outro canal.
- **Local de configurações e saves resolvido (2026-10-20).** O jogo não mantém `settings.txt` na pasta do jogo: fica em `%LOCALAPPDATA%\EA Games\<localized title>\settings.txt`, onde a pasta do título é um nome localizado. O formato é texto simples com linhas `Key = value` e CRLF; o arquivo preparado (871 bytes) contém `Window.Fullscreen = false`, `Window.Width = 1280`, `Window.Height = 720`, `Window.VSync = 0`, `Window.Gamma = 0.80000001`, `QualityOptions.ConfigType = 4`, mais chaves de áudio/controles/qualidade. Esse é o equivalente por arquivo dos dois patches da cópia de teste: `Window.Fullscreen = false` remove a tentativa de tela cheia exclusiva, e `QualityOptions.ConfigType = 4` (não zero) evita o detector de fabricante de GPU que falha em `FUN_0069f440`. Saves da campanha ficam em `Documents\EA Games\<localized title>\`: `profiles.dat` (1296 bytes; assinatura `9A E8 0D 1D`, versão 4, uma entrada de perfil) e uma pasta `<profile-id>` (`3280000`) com arquivos de save localizados e um autosave. Cópias das configurações e saves foram preparadas (originais intactos) em `local/sandbox-input/gf2profile/`, e o script de inicialização Sandbox agora as copia para o perfil do convidado sob os nomes de pasta do título em inglês e localizado antes de iniciar. Com configurações + perfil preparados, o seletor de idioma não aparece mais, e o menu principal mostra **Resume Game** ativo; captura `local/sandbox-output/seq_T90.png` (execução v12).
- **Ponto de integração ASI validado (2026-10-20).** O `dinput8.dll` do pacote SE é Ultimate ASI Loader (strings UTF-16 `ASI Loader`, `*.asi`, `scripts\`, `\modloader\modloader.asi`). Um plugin de teste mínimo (`local/cooptest.c` → `cooptest.asi`, PE32 i686, DllMain grava uma linha de marcador, sem interceptações) foi colocado na pasta `scripts\` da cópia de teste descartável. A execução v12 produziu `local/sandbox-output/cooptest_loaded.txt`: `cooptest.asi loaded; game=C:\Games\GF2Test\godfather2.exe; module=C:\Games\GF2Test\scripts\cooptest.asi` — **o carregador carrega plugins ASI de terceiros de `scripts\`**, que é o ponto de injeção que um plugin cooperativo pode usar (mesmo mecanismo do extensor SE e do ASI Multiplayer Revival).
- **Marco (2026-10-21 00:08): gameplay de campanha em execução dentro do Windows Sandbox.** A causa de `Resume Game` desabilitado/perfil desconhecido era o locale do jogo: ele grava `Locale = en` nas configurações na primeira execução, enquanto os saves preparados usam outro locale. Após adicionar a chave `Locale` com o idioma dos saves ao `settings.txt` preparado (mantendo `profiles.dat` e a pasta de saves preparados na pasta localizada `Documents\EA Games`), o perfil foi reconhecido e o jogo carregou diretamente a campanha — captura `local/sandbox-output/seq_T60.png` mostra HUD do jogo (dinheiro, retrato, barra de vida, NPC da equipe, minimapa) sem a introdução de Cuba. Layout de `profiles.dat`: assinatura `9A E8 0D 1D`, versão 4, contagem de perfis 1, nome de perfil em string larga, id do perfil (o nome decimal da pasta de saves). `settings.txt` é lido/gravado em `%LOCALAPPDATA%\EA Games\<localized title>\`; saves e `profiles.dat` em `Documents\EA Games\<localized title>\`. Alternar o locale seleciona a pasta localizada do título. O convidado Sandbox ficou estável durante o carregamento (respondendo, CPU acumulando, sem eventos WER).
- **Entrada (confirmada, 2026-10-21): navegação por teclado nos menus funciona** no Sandbox (setas + Enter). O caminho do mouse permanece vinculado a RDP (`SetCursorPos` ineficaz, cliques injetados não confiáveis), então teclado é o canal pretendido para automatizar menus; o próximo teste injeta `WM_KEYDOWN`/`WM_KEYUP` (`VK_UP` ×8 e depois `VK_RETURN`) no menu principal e verifica destaque/capturas para ver se teclas injetadas por mensagem são respeitadas ou se a engine lê apenas o estado real das teclas.
- **Inicialização → menu → Resume Game → campanha automatizados (2026-10-21 00:25).** A execução v14 provou que `WM_KEYDOWN`/`WM_KEYUP` injetados (enviados a `Godfather2WndClass`) chegam à engine e controlam a interface: aos 40 s, a tela inicial localizada estava visível, os `VK_UP` injetados a dispensaram e moveram a seleção do menu, e `VK_RETURN` aos 60/80 s ativou **Resume Game** — apareceu uma tela de carregamento com o mapa da cidade, depois a cena inicial da missão (personagem em primeiro plano, depois um carro em chamas), tudo sem entrada manual (`menu_after_up_4/5.png`, `menu_after_enter_6/8.png`, `seq_T240.png`, `seq_T450.png`). A interface mudou para o idioma dos saves quando a chave `Locale` correspondeu, confirmando pastas de dados controladas por locale. Isso dá um caminho totalmente automatizado até a campanha para execuções QA; a próxima questão é se o movimento no jogo também aceita teclas injetadas ou só entrada real (DirectInput).
- **Percurso manual completo capturado (2026-10-21 01:04, execução v17, quadros a cada 5 s `seq2_1..34`).** Sequência de telas: inicialização preta -> tela inicial clara -> **menu principal (localizado)** -> **a entrada de perfil** -> lista de perfis contendo exatamente uma entrada (`profiles.dat` a armazena como string larga e id de perfil `0x00320C80` = pasta `3280000`) -> volta ao menu principal com **o item de continuar** destacado -> **diretamente ao gameplay na mansão Corleone** (Dominic, `19$`, minimapa, NPCs) **sem introdução de Cuba**. Tentativas anteriores de automação falharam porque `Resume Game` era pressionado sem selecionar primeiro o perfil, iniciando a sequência de introdução em vez do save. O mouse Sandbox se comporta de modo estranho (entrada RDP), enquanto o jogo funciona bem na área de trabalho normal.
- **Máquina de estados de tela sem supervisão (2026-10-21, execução v18).** Para automatizar totalmente o caminho da inicialização à campanha, o script convidado agora classifica a tela a cada 5 s por uma assinatura de tons de cinza 4×4 da região da janela do jogo (ferramenta de referência no host `local/screenstate.ps1`; assinaturas de referência incorporadas ao script para MENU, PROFILE e SPLASH) e controla uma máquina de fases: fase 0 tela inicial → `VK_UP`; fase 1 menu → `VK_DOWN`×6 + `VK_RETURN` (abrir tela de perfil); fase 2 perfil → `VK_UP`×2 + `VK_RETURN` (selecionar "22"); fase 3 menu → `VK_UP`×8 + `VK_RETURN` (Resume Game); fase 4 carregamento → nenhuma entrada adicional; fase 5 gameplay alcançado. Novas tentativas são limitadas (máximo de 3/4/6 tentativas), e a etapa de perfil só envia `VK_RETURN` após o primeiro `VK_UP`, para o botão de criar perfil não ser acionado acidentalmente. Toda decisão é registrada com as três distâncias de assinatura em `local/sandbox-output/gf2_se_boot.txt`.


## <a id="research-log"></a>Registro de pesquisa

### <a id="checked"></a>Verificado

- `DIRECTORY.md` e `games/` do repositório: nenhuma entrada Godfather II antes desta nota.
- Aberta a issue de atribuição exigida: <https://github.com/cranebeaker/coop-anything/issues/78>.
- Busca de issues e PRs GitHub por `Godfather 2`: nenhum resultado na API pública. Os comandos exigidos `gh issue list` / `gh pr list` não puderam rodar porque GitHub CLI (`gh`) não está instalado.
- Buscas de repositórios GitHub por `Godfather II coop`, `godfather2 multiplayer` e `The Godfather II mod`: nenhum repositório correspondente retornado.
- Buscas na web em inglês por campanha cooperativa, mod cooperativo, cooperativo online e mod multijogador de Godfather II; verificados resultados de Nexus Mods, ModDB, GameBanana, GameFAQs, PCGamingWiki e cobertura da imprensa. Os resultados concretos foram a restauração multijogador e as ferramentas de modificação acima; nenhum projeto cooperativo de campanha apareceu.
- Tentadas buscas em russo, alemão, italiano e espanhol; o serviço de busca retornou HTTP 429, então não foram concluídas.

### <a id="not-checked-yet"></a>Ainda não verificado

- O Discord/servidor da comunidade do jogo, guias Steam em profundidade, Archive.org e tópicos completos de bugs/issues fora das páginas Nexus.
- ID da loja/pacote da cópia limpa, compatibilidade/API detalhada do SE e replicação de IA/história/estado do mundo do multijogador original.

## <a id="assessment-and-next-steps"></a>Avaliação e próximos passos

- **Deduzido:** a restauração existente é uma forma de recuperar os modos originais de partidas online do jogo, não uma solução para a campanha de história solicitada. Nenhuma tentativa de cooperativo na campanha foi encontrada nas buscas acima; isso é um resultado de pesquisa, não prova de inexistência.
- **Ponto de parada:** `1.0.764.0` é o executável original do jogo, mas suas seções PE e `paul.dll` indicam proteção SecuROM. A análise Ghidra desse executável limpo produziu referências inválidas/sobreposições de funções e terminou com `-1`; a descompilação parcial é inutilizável e não foi usada. Não se tentou desempacotar/descriptografar. O executável MPR `1.0.789.0` também não é uma base limpa.
- **Próximo:** a build alvo precisa ser escolhida explicitamente. O arquivo SE v0.56 tem um manifesto com hash correspondente, mas o executável `1.0.789.0` dentro dele é um binário de terceiros não verificado e exige essa build, então uma tentativa cooperativa usando seu carregador significa trocar o alvo isolado por uma cópia baseada em `.789`, enquanto um caminho somente `.764` significa criar nosso próprio carregador e perder os pontos de integração de ambos os mods (a análise estática do executável SecuROM permanece bloqueada em qualquer caso). Qualquer que seja o caminho, um Sandbox limpo primeiro precisa do runtime legado DirectX 9.0c (`d3dx9_40.dll`, `XINPUT1_3.dll`) instalado no convidado, o que exige um download oficial Microsoft. A issue de atribuição está aberta (#78).
- **Desconhecido:** loja (Steam, EA app, disco ou outra), se amigos têm cópias correspondentes, procedência/licenciamento das builds comunitárias `.789` dentro de SE e MPR e permissão do autor SE para reutilizar código. Hashes dos executáveis ficam em `local/identity.md`, ignorado pelo Git.
- **Verificações realmente executadas:** cópia do candidato limpo em uma pasta de teste isolada; leitura dos metadados de versão e SHA-256; leitura estática de cabeçalhos/imports PE e strings imprimíveis; Ghidra 12.1.4 headless com Temurin JDK 21.0.12.1+1 descompilou 84 funções de Multiplayer Revival e 33.506 funções do executável incluído no MPR. Uma execução Ghidra no `1.0.764.0` limpo terminou com `-1` e extensos avisos de fluxo inválido/sobreposição de funções; saída parcial não usada. Uma sondagem de pastas do shell restrita ao processo mostrou que mudar `USERPROFILE` não redireciona `SHGetFolderPathW(CSIDL_PERSONAL)`. Quatro execuções offline do Windows Sandbox (duas sondagens simples de inicialização, uma vGPU e uma varredura de todas as janelas) identificaram o runtime DirectX legado ausente por trás da inicialização vazia. O arquivo SE v0.56 foi verificado por SHA-256 contra o manifesto Nexus e inspecionado; não foi instalado em nenhuma cópia do jogo. Nenhum teste de dois clientes ou cooperativo foi executado.

## <a id="sources"></a>Fontes

- <https://www.pcgamingwiki.com/wiki/The_Godfather_II>
- <https://www.nexusmods.com/thegodfather2/mods/95>
- <https://www.nexusmods.com/thegodfather2/mods/40>
- <https://www.ign.com/articles/2009/03/18/the-godfather-ii-gets-multiplayer-mode>
- <https://github.com/Greavesy1899/VisceralToolkit>
- <https://github.com/Greavesy1899/VisceralToolkit/wiki/File-Resource-Type-Support>
- <https://github.com/Greavesy1899/VisceralToolkit/wiki/Resource-Types>
- <https://www.pcgamingwiki.com/wiki/Dead_Space_3>
- <https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file>
- <https://www.microsoft.com/en-us/download/details.aspx?id=8109> (DirectX End-User Runtimes de junho de 2010; fonte oficial dos componentes ausentes `d3dx9_40.dll` / `XINPUT1_3.dll` identificados no log Sandbox)
- <https://github.com/Winetricks/winetricks/pull/1690> (registro independente do mesmo SHA-256 `053f76dc…` para o redistribuível de junho de 2010 republicado pela Microsoft)
- <https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build>
- <https://github.com/adoptium/temurin21-binaries/releases/tag/jdk-21.0.12.1%2B1>

- **Iteração no host (2026-10-21 ~01:30) — a configuração funcional.** A entrada RDP Sandbox é o gargalo, então o alvo de iteração mudou para o **host**: a cópia descartável `%LOCALAPPDATA%\Temp\opencode\godfather2-test-se` é iniciada diretamente na máquina de teste (janela 1280x720, inicialização rápida), e o jogo vê um perfil preexistente com seus saves de campanha. Um script controlador `local/host-drive.ps1` observa `local/host-cmd.txt` e executa comandos na janela do jogo (`ENTER/UP/DOWN/ESC/SPACE/W/A/S/D`, `VK <code> <n>`, `CLICK x y`, `MOVE x y`, `SHOT/WIN label`, `EXIT`), registrando em `local/host-drive.log` e capturando quadros em `local/host-shots/`. A busca da janela usa `EnumWindows` + correspondência de classe (no host, `FindWindowW` não retorna nada). **Rota sem supervisão verificada no host:** `ENTER` (dispensar aviso inicial) -> modo de demonstração -> **clique na entrada de perfil** -> confirmar aviso de salvamento automático -> **clicar em continuar** -> campanha carrega (mapa de Nova York, primeiro objetivo "Sweet Life Bakery") **sem introdução de Cuba**. Só teclado não confirma o perfil (o foco fica no item "criar perfil", então `VK_RETURN` ali criaria outro perfil) — é preciso clicar no perfil, e no host cliques reais funcionam; essa é a vantagem concreta sobre o Sandbox. Quadros: `local/host-shots/003_after_enter.png` (demonstração), `001_after_click22.png` (aviso de salvamento automático), `003_after_next2.png` (menu principal), `005_loaded.png` (mapa da campanha). Foi feito backup das pastas EA Games da máquina (com manifesto SHA-256) antes da primeira execução no host; os cinco arquivos ainda eram idênticos byte a byte depois.
- **Trabalho de interceptação dentro do processo (2026-10-21 ~01:50), estado de `local/coopcore.c` -> `coopcore.asi`.** O plugin é carregado pelo carregador SE (Ultimate ASI Loader) de `scripts\` e executa dentro do processo: registra seu ponto de carregamento, mantém uma thread de atividade e registra contagens de quadros. Tentativas de interceptação: (a) interceptação inline de `FUN_00607990` (inicialização de dispositivo) **causou crash** — a função recebe argumentos e o wrapper não os encaminhava — substituída por consulta da global do ponteiro de dispositivo `DAT_01205750`; (b) interceptação por objeto da vtable de `IDirect3DDevice9::Present` (slot 17 de uma vtable de implementação d3d9 de 175 entradas) **também causou crash** — copiar e trocar é inseguro aqui, então foi abandonado; (c) interceptação inline de `FUN_006080a0` instala sem problemas e o jogo continua, mas a função só é usada no caminho de redefinição do dispositivo (`FUN_00608250`), não por quadro, então o contador permanece 0. Foi verificado que a vtable do dispositivo fica inteiramente dentro de `d3d9.dll` (base `0x709D0000`, 175 entradas), então o objeto é o dispositivo D3D9 bruto, não um wrapper da engine. Próximo: interceptações IAT de `GetMessageW`/`PeekMessageW` para um tick confiável por quadro.
- **API de scripts encontrada (2026-10-21 ~02:00).** O jogo registra uma API de scripts/comportamentos (`FUN_00468cb0`): `RegisterScriptName`, `GetPositionValues`, `SetPositionValues`, `GetPlayerPosition`, `TEMP_POS`, `CreatePosition`, `GetPlatform`, mais `GetPlayerInfo` e pontos de integração Lua (`iMsgLuaGetPlayerVenue`, `FUN_00408240`). Esse é o ponto natural para cooperativo: a engine já expõe leitura/gravação da posição do jogador a scripts, e o extensor SE pode injetar comportamentos por arquivos de substituição SimGroup `.sgp`.

- **Objeto do jogador localizado (2026-10-21 ~02:40).** Método: um scanner de memória no plugin (código próprio) compara a seção `.data` do executável (VA `0x00E50000`–`0x01228A38`) uma vez por segundo e informa trios de floats vizinhos que mudam juntos; com o personagem se movendo em uma fase, surgiram trios em escala de mundo, relacionados à descompilação. Resultado: a engine mantém a **transformação do alvo de visão da câmera — isto é, o personagem do jogador — em `0x0112A840`** (floats `x,y,z` em `0x0112A840/44/48`, float de ângulo em `0x0112A84C`) e o **olho da câmera em `0x0112A850`** (`0x0112A850/54/58`, ângulo em `0x0112A85C`). Fonte na descompilação: a atualização da câmera `FUN_006d24d0` (VA `0x006D24D0`) copia suas transformações de olho/alvo para essas globais (`_DAT_0112a850 = *piVar11; _DAT_0112a840 = param_1[0xc];`), e a câmera segue o ponteiro de ator em `param_1[0x36]` (seus slots de vtable `+0x10`/`+0x14` retornam as transformações de olho/alvo). O plugin agora registra o estado do jogador a 5 Hz em `coopcore_player.txt` ao lado do jogo (`player x y z | lookang | cam x y z | camang`).
- **Realidade da entrada no host (2026-10-21).** Entrada sintética de mouse **não** chega à interface do jogo: a janela captura o mouse (`ClipCursor`), a engine lê o ponteiro por Raw Input, e `SetCursorPos`/`mouse_event` são ignorados; `WM_MOUSEMOVE` baseado em `PostMessage` só move o destaque do menu enquanto a engine está em modo de cursor capturado (`DAT_0112a065`), e `WM_LBUTTONDOWN` não é tratado pelo procedimento de janela da engine. Teclado funciona no menu principal (confirmado), mas não na tela de perfil. Consequência para o projeto: automação de menus precisa usar entrada real ou acontecer dentro do processo (nosso plugin), não por entrada sintética do SO.
- **Notas de compilação do plugin (2026-10-21).** `local/coopcore.c` -> `coopcore.asi` (PE32 i686, LLVM-MinGW) é preparado na pasta `scripts\` da cópia descartável; o carregador SE (Ultimate ASI Loader) o carrega. Lições que custaram crashes: wrappers de interceptação precisam encaminhar os argumentos do chamado; não trocar a vtable do dispositivo D3D9 (175 entradas) — isso derruba o jogo; ler nomes de imports da INT (`OriginalFirstThunk`) e modificar a IAT (`FirstThunk`); uma exceção numa thread de plugin encerra o processo inteiro, e MinGW não tem SEH, então todo percurso de ponteiros precisa de limites verificados; o scanner precisa ficar dentro da faixa `.data` comprometida; e o formatador float precisa ser `sprintf`, não uma escrita manual de dígitos.

- **Transformação do jogador e ponteiro de ator (2026-10-21 ~03:00).** A engine compõe a matriz de mundo do jogador a cada quadro em `FUN_0088d6e0` (VA `0x0088D6E0`, `__fastcall`): lê a posição do ator (`*(undefined8 *)(iVar6 + 0x30)` e `*(float *)(iVar6 + 0x38)`) e armazena a matriz 4x4 composta na global `0x0112E210` (`_DAT_0112e210 = local_80[0] ... fRam0112e21c = local_80[3]`). O ator em si é `FUN_00471610(context) = context + 0xD0`, e o contexto é o gerenciador global de mundo/atores `DAT_012233A0` (também tem um array de atores em `+0x04` e contagem em `+0x0C`). Consequências: **posição de mundo do jogador = primeira linha da matriz em `0x0112E210`** (x,y,z,1), e a **posição do objeto ator fica no deslocamento `+0x30`**; as globais de alvo de visão/olho da câmera (`0x0112A840`/`0x0112A850`) só são preenchidas em alguns modos de câmera (permaneceram zero no interior da mansão). O plugin agora transmite `matrix | actor | cam` a 5 Hz para `coopcore_player.txt` e confere a matriz contra `*(manager + 0xD0) + 0x30`, que é a referência necessária para representar outro jogador: gravar a mesma transformação em um segundo ator a cada quadro.

- **Mais dois bugs do plugin, ambos dignos de lembrar (2026-10-21 ~03:40).** (1) **Erro de um byte no trampolim:** o salto de volta à função original precisa ser calculado a partir de `trampoline + 11`, não `trampoline + 10` — `E9 rel32` ocupa bytes 6..10, então a próxima instrução fica em +11. Com a base errada, a CPU caía no meio de uma instrução (`IN AL,DX` -> falha de instrução privilegiada `0xC0000096` dentro de `FUN_0088d6e0`); em outra interceptação, por acaso caía num byte inofensivo e passou despercebido. (2) **Toda aritmética de ponteiros precisa verificar limites**: ler `camera + 0xD8` sem validar o tamanho do objeto causava violação de acesso *a cada quadro*; o handler de exceções vetorizadas a absorvia, e o jogo travava em tela preta em vez de encerrar. O plugin agora valida cada ponteiro com `is_readable(ptr, need)` (região comprometida + acesso totalmente dentro dela) antes de desreferenciar, e o VEH só absorve até 5000 falhas e registra cada 50ª. Com ambos corrigidos, o jogo fica estável e a interceptação da câmera informa o ator seguido (`camera follow actor = 1af83940`).

- **Menu principal e campanha alcançados no host (2026-10-21 02:00–04:00).** Com o perfil preparado (configurações + saves), o jogo chega ao menu principal (build `1.0.789.0`, captura `local/host-shots/003_after_next2.png`) e à campanha (mapa de Nova York com objetivo "Sweet Life Bakery", depois a mansão com HUD, `local/host-shots/005_loaded.png` e quadros posteriores com o personagem andando na rua e um NPC conversando). Sem introdução de Cuba — o perfil existente é carregado e seu save continua.
- **Inspetor externo `local/coopscan.c` -> `coopscan.exe` (código próprio, PE32).** Conecta-se a `godfather2.exe` em execução com ReadProcessMemory/WriteProcessMemory, sem reinício nem interceptação no jogo: `find` imprime a matriz do jogador e procura objetos de personagem, `dump <addr>` faz um dump hexadecimal de um objeto, `list` percorre o gerenciador de mundo, `puppet <actor> [dx]` copia a linha da matriz do jogador para um ator a cada 16 ms. Isso substituiu o ciclo de "derrubar o jogo e reiniciar" do plugin interno.
- **Não gravar às cegas na memória da engine (2026-10-21 04:30).** Gravar uma posição no objeto seguido pela câmera causou crash: `0xC0000005` em `0x4D006874` com módulo de falha "unknown" — `+0x40` desse objeto contém um **ponteiro**, e sobrescrevê-lo com floats fez a engine desreferenciar lixo. O objeto seguido pela câmera não é o personagem do jogador. O caminho fundamentado na descompilação é: interceptar `FUN_0088d6e0` para capturar seu contexto, o ator do jogador é `context + 0xD0`, e a posição do ator fica em `actor + 0x30`; o plugin agora faz exatamente isso e valida cada ponteiro com `is_readable()`.
- **Realidade da entrada, final (2026-10-21).** A engine lê o mouse por Raw Input: `SetCursorPos`, `mouse_event` e `WM_MOUSEMOVE`/`WM_LBUTTONDOWN` não controlam a interface (apenas o destaque de passagem do mouse se moveu no Sandbox). Teclado funciona no menu principal (confirmado), mas não na tela de perfil, que exige clique real. Portanto, automação de menus precisa vir de um dispositivo real ou de dentro do processo.
- **Layout de dados do jogo (final).** `settings.txt` fica em `%LOCALAPPDATA%\EA Games\<localized title>\` (`Key = value`, CRLF, chaves `Window.*`, `QualityOptions.*`, `Locale`), saves de campanha e `profiles.dat` em `Documents\EA Games\<localized title>\` (id de perfil `0x00320C80` = pasta `3280000`). A chave `Locale` (`en`/`ru`) seleciona o idioma *e* a pasta localizada do título — por isso os saves localizados eram invisíveis até a chave `Locale` corresponder.

- **Experimento de representação do jogador (2026-10-21 00:45–01:00).** O objeto personagem do alvo da câmera fica em `0x14A17B20` com vtable `0x00D6B350`; a engine lê sua posição pelo slot virtual `+0x48` (`(**(code **)(*(int *)(iVar6 + -0x1f30) + 0x48))(&local_b0)` em `FUN_0088d6e0`, onde `iVar6 = **(int **)(DAT_012233a0 + 4)`). A cadeia do gerenciador de mundo é `DAT_012233a0` -> `+0x04` (array) -> `+0x0C` (contagem) -> entrada -> `-0x1F30` = objeto personagem. A matriz de mundo do jogador é `0x0112E210` (4x4, linha 0 = x,y,z,1), e alvo de visão/olho da câmera são `0x0112A840` / `0x0112A850`. A ferramenta externa `coopscan.exe nearpos` encontra toda linha de transformação em cache (x,y,z,1.0) perto do jogador; os resultados mais próximos são as próprias cópias do jogador, outros (`0x2448xxxx`) são matrizes em cache por personagem. **Gravar a posição do jogador nessa matriz em cache não move o personagem** — a engine recalcula a transformação autoritativa a partir da cinemática do personagem a cada quadro, e a gravação é sobrescrita. A representação dentro do processo (interceptação do plugin na atualização de câmera `FUN_006d24d0`, configuração `coop_puppet.cfg` com `enabled/target/offset/dz`) mantém o valor no cache (a linha em cache do NPC acompanhou o jogador exatamente), mas o renderizador ainda usa a transformação cinemática, então o modelo ainda não se move. Dois caminhos permitidos: chamar o próprio setter de posição do personagem (o getter é o slot `+0x48` da vtable `0x00D6B350`, provavelmente há um setter na mesma vtable) ou controlar a camada de scripts/comportamentos da engine, que já expõe comandos de movimento (`moveToPos`, `moveToPathingFailure`, `combatMoveToCSARange`, ... registrados em torno de `0x004acd20`/`0x004acc70` na descompilação), mais a API de scripts `SetPositionValues` / `GetPlayerPosition` / `GetPlatform` (`FUN_00468cb0`).
- **Ferramentas criadas (todo código próprio, nada redistribuído):** `local/coopcore.c` -> `coopcore.asi` (plugin no jogo: 5 interceptações da engine, log de quadros, redirecionamento de caminhos para isolamento de perfil, gravador da representação, rede de segurança VEH), `local/coopscan.c` -> `coopscan.exe` (inspetor externo: `find`, `list`, `dump`, `chars`, `nearpos`, `snap`, `diff`, `puppet`), `local/poolscan.ps1` (dump de contêiner), `local/host-drive.ps1` (controlador de entrada/capturas no host: teclas, cliques reais, quadros), `local/bytepatch.c` (modificador de bytes do executável), `local/dx9probe.c` (diagnóstico D3D9).

- **Vtable de personagem analisada (2026-10-21 01:00–01:20) — a questão aberta da representação.** A vtable da classe do alvo da câmera é `0x00D6B350`. O slot `+0x48` é um **thunk getter** de posição: `81 C1 C0 03 00 00 / E9 25 52 D5 FF` = `ADD ECX,0x3C0; JMP 0x0054DBEA`, então a posição fica atrás de `this+0x3C0` (possivelmente num subobjeto). O slot `+0x44` é um getter de estado booleano (`XOR EAX,EAX; CMP [ECX+0x220],0; SETNE AL; RET`). O slot `+0x4C` é um despachante que resolve um subobjeto em `this+0x1E40` (+0xB8) e chama seu slot de vtable `+0x4C` — bom candidato a **setter**. A cadeia do gerenciador de mundo é `DAT_012233A0` -> `+0x04` (ponteiro para array) -> `+0x0C` (contagem) -> entrada (por exemplo, `0x14A19A50`) -> `-0x1F30` -> vtable `0x00D6B350`; o local da chamada é `(**(code **)(*(int *)(iVar6 + -0x1f30) + 0x48))(&local_b0)` em `FUN_0088d6e0`. **O `this` dessa chamada ainda não foi identificado** — o objeto em `0x14A17B20` contém essa vtable, mas seu `+0x3C0` tem dados de string, portanto é outra instância. A busca empírica (`local/findpos.ps1`, procura a posição do jogador dentro de um objeto) também não o encontrou. Próximo passo: identificar o chamador de `FUN_0088d6e0` (o `this` que ele passa) ou interceptar o getter `0x00D6B350[0x48]` no plugin, capturar `this` e ler `this+0x3C0` para entender o layout; o setter correspondente deve ficar ao lado do getter na mesma vtable.
- **Estado ao fim desta sessão:** o jogo roda na máquina de teste pela cópia descartável, a campanha carrega diretamente (sem introdução de Cuba), o plugin está carregado com cinco interceptações da engine, a posição do jogador é lida a 5 Hz, objetos de personagem e suas linhas de transformação em cache são encontrados no heap, e existe um gravador de representação dentro do processo, mas a transformação autoritativa de um segundo personagem ainda é desconhecida. Perfil, configurações e saves da máquina são idênticos byte a byte ao backup anterior à sessão, e a instalação original está intacta (`godfather2.exe` SHA-256 `A5632356C94A270DAB518E0E1FA569AD40FD6520C1013CF99B023E95252AD338`).


## <a id="handoff-how-to-continue-2026-10-21"></a>Passagem de trabalho: como continuar (2026-10-21)

Configuração funcional (iteração no host, sem precisar de Sandbox):

1. Cópia de teste: `%LOCALAPPDATA%\Temp\opencode\godfather2-test-se` (SHA-256 do executável
   `201269a29eef055c050cd1e17a4faee24df888544d8f09299bee156050c601bc`; pacote SE
   intacto em `godfather2-tools\inspect\se-v0.56`).
   O plugin fica em `scripts\coopcore.asi`; o carregador SE o detecta.
2. Iniciar o jogo: `Start-Process %LOCALAPPDATA%\Temp\opencode\godfather2-test-se\godfather2.exe`
   (diretório de trabalho = a cópia). Perfil/configurações/saves são redirecionados pelo
   plugin para `<copy>\profile\`, então os arquivos da própria máquina permanecem intactos.
3. Caminho do menu (mouse/teclas são limitados por RDP no Sandbox, mas normais no host):
   qualquer tecla na tela inicial -> selecionar o perfil existente -> continuar o jogo salvo -> uma missão.
4. Ferramentas (todo código próprio, em `local/`):
   - `local/coopscan.exe` — inspetor/gravador externo para o jogo em execução:
     `find` (estado do jogador), `list` (gerenciador do mundo), `dump <addr>` (dump hexadecimal),
     `chars` (objetos da vtable de personagem), `nearpos <radius>` (linhas de transformação
     perto do jogador), `snap <file>` / `diff <file>` (snapshots do heap),
     `puppet <actor> [dx]` (gravar a posição do jogador em um ator).
   - `local/findpos.ps1 <obj>` — localizar a posição do jogador dentro de um objeto.
   - `local/poolscan.ps1` — fazer dump do contêiner de personagens.
   - `local/host-drive.ps1` — controlador de entrada/capturas (teclas, mouse real, quadros).
   - `local/bytepatch.exe` — modificador de bytes do executável de teste.
   - `local/dx9probe.exe` — sondagem do ambiente D3D9.
   - `local/coopcore.c` -> `coopcore.asi` — plugin no jogo (interceptações, log,
     redirecionamento de perfil, gravador da representação, proteção VEH).

Próxima tarefa imediata (a única questão aberta): identificar a transformação autoritativa de um
segundo personagem. Concretamente — interceptar o getter de posição `0x00D6B350[0x48]`
(`ADD ECX,0x3C0; JMP 0x0054DBEA`) no plugin, registrar seu `this` e o valor em
`this+0x3C0`, depois procurar o setter correspondente na mesma vtable (slot
`+0x4C` parece um despachante para um subobjeto). Quando o campo autoritativo for
conhecido, gravar nele a posição do jogador transforma o NPC numa representação visível de
"jogador 2" — a primitiva básica para o segundo jogador em rede.

### <a id="se-npc-inspector-as-an-oracle-2026-10-21-session-2"></a>NPC Inspector do SE como oráculo (2026-10-21, sessão 2)

O menu ScriptHook do mod SE tem uma janela **NPC Inspector**. Observado no membro da equipe
"Joe Primanti" (valores lidos de capturas do inspetor):

- `SimNPC: 1B603A00`, `Supporting Entity: 1B8F1200` — ambos handles do heap; os
  primeiros 0x1000 bytes de nenhum dos objetos contêm a posição exibida (verificado com
  `findpos.ps1`).
- Posição exibida com 6 casas decimais (por exemplo, `156.101730 10.222837 -220.644165`);
  ela é **derivada, não armazenada**: `findpos ALL` (varredura RW completa, tolerância 0,02) não encontra
  trio em lugar algum do processo. Corresponde a `FUN_0054dbf0` = `(min+max)*0.5` de uma
  AABB do nó em `*(this+0x18)`, slot `+0x18`. Portanto, o estado autoritativo
  é o mínimo/máximo da AABB (ou uma transformação de nó), e a posição exibida é seu
  centro.
- `Supporting Material Type` / `Flags` mudam entre inspeções (25/1FF0000 ->
  4/1FF0000) — material sob os pés, útil como verificação de referência real.

Novo experimento (em execução): `local/nearwatch.c` -> `nearwatch.exe x y z seconds r`
registra cada trio de floats a até `r` da posição do inspetor, espera enquanto
o companheiro caminha, depois informa antigo->novo por trio. O movimento real do companheiro
é o agrupamento de campos cuja variação é igual ao vetor de movimento entre
duas capturas do inspetor. `local/delta-analyze.ps1` agrupa o relatório pela variação.
Justificativa: qualquer que seja a representação (cantos da AABB, linha de matriz do nó), uma translação
pura a desloca pela mesma variação, então a técnica de comparação por variação é
independente de representação.

Ferramentas adicionadas: `local/nearwatch.c` (observador), `local/delta-analyze.ps1`
(agrupamento de variações).

### <a id="character-position-slots-found-2026-10-21-session-2-second-half"></a>Campos de posição de personagem encontrados (2026-10-21, sessão 2, segunda metade)

Método que funcionou: `local/findtrip.exe <x> <z> <ylo> <yhi> [tol_xz]` — varredura RW
completa de trios de floats correspondendo a (x, ?, z), com uma janela y AMPLA. Por que as
buscas anteriores falharam:

1. `findpos.ps1` exigia correspondência dos três componentes, mas a engine armazena
   a posição em várias alturas (pés / centro / cabeça). O NPC Inspector
   exibe a posição dos PÉS: y do inspetor=10,010 contra y da matriz do jogador=11,145
   (diferença 0,945 = deslocamento dos pés). Portanto, uma busca com y restrito nunca corresponde ao
   valor do inspetor nos campos de altura central.
2. `findpos ALL` tinha prazo de 25 s e limite de região de 64 MB — esgotou o tempo antes
   de alcançar as alocações 0x43xxxxxx onde ficam a maioria das cópias.

Famílias de campos observadas (jogo em execução, 1.0.789.0):

- JOGADOR (centro na matriz 0x0112E210, caso y=11,145): cópias estáticas .data em
  0x0019E670 (y = centro-0,946), 0x0019E6C0, 0x0019EA40 (y = centro+0,555),
  0x0019EA50 (y = centro-0,555), 0x0019F370/0x0019F3E0 (z armazenado como z+1000!),
  0x0019F500, 0x0019F770, 0x0019F930, mais 0x0112A840 (alvo de visão da câmera),
  0x01130620, 0x011F6E40, 0x012070A0, 0x012073A0 e 300+ cópias no heap em
  pools de renderização/animação (0x22D5xxxx, 0x23883xxx, 0x24C13xxx, 0x3AC49xxx, ...).
- COMPANHEIRO "Joe Primanti" (SimNPC 1B603A00), posição do inspetor
  (30,933395 10,210006 -53,035728): 32 cópias exatas, nenhuma em .data — um bloco
  de registros em 0x43438958–0x4344492C mais pools 0x2270B230/0x2270D530/0x22712C30,
  0x43708C30/0x4370BF30/0x43724630. A família de um pedestre parecia igual
  (5 cópias coerentes em 0x00199E50/0x0019A240/0x0019A250/0x0019A260/0x0019A6E0
  — estas ESTAVAM em .data, então .data também contém registros de alguns NPCs; a regra de layout
  ainda é desconhecida).

A "caça à variação" (`local/deltahunt.c`) é a forma confiável de atribuir campos a
um personagem em movimento: registrar toda memória RW, esperar um arquivo de parada, depois informar cada
trio cuja variação seja igual à do jogador (lida de 0x0112E210). Um companheiro que
caminha por outro trajeto precisa de sua própria variação, obtida de duas capturas do inspetor.

Teste de gravação de representação (`local/puppetdrive.c`): gravador externo a 100 Hz colocando
jogador+deslocamento nas 24 cópias de campos do companheiro. Resultado: **nenhum movimento** —
as cópias são vistas somente leitura; a engine recalcula a cinemática a cada quadro.
Segundo teste (`local/puppetdrive2.c`) controla rigidamente os 29 campos, incluindo os
prováveis ossos do esqueleto (0x2633D930, 0x26345B30, 0x3CADCC30, 0x403465E0,
0x4343E928 — cada um a 0,2..0,9 m da posição dos pés). Resultado: pendente.

Plano alternativo se os ossos também falharem: capturar o gravador de um campo de cache com um
watchpoint de hardware (minidepurador externo: DebugActiveProcess + breakpoint de gravação DR0)
e percorrer o caminho de código para trás até a fonte autoritativa.

**Lição de crash/travamento (2026-10-21):** o `apply_puppet` do plugin gravou 16 bytes
(linha float4 terminando em `1.0`) no campo 0x43438958 e **travou o jogo**. A
dword após um trio de posição NÃO é preenchimento — contém um ponteiro/flag. Todas as
gravações de posição precisam ser de 12 bytes. Gravações externas de 12 bytes (puppetdrive) eram
seguras. O plugin foi recompilado: `apply_puppet` agora grava 12 bytes em uma lista de
alvos de linhas repetidas `target <hex> [yoff]` em `coop_puppet.cfg`
(a configuração é relida a cada segundo, então a representação pode ser reconfigurada sem
reiniciar o jogo). A gravação interna acontece na interceptação da câmera
(`FUN_006d24d0`), isto é, após a atualização por quadro da engine — o momento que o
controlador externo não conseguia alcançar.

### <a id="what-the-position-slots-really-are-2026-10-21-later"></a>O que os campos de posição realmente são (2026-10-21, mais tarde)

- **A faixa 0x0019xxxx é PILHA DE THREAD, não .data.** Fica abaixo da base
  do executável (0x00400000). As "cópias de posição do jogador" encontradas ali antes eram
  variáveis locais de pilha do próprio código de posição da engine. Gravá-las corrompe a
  pilha — foi isso que travou o jogo nas duas vezes.
- Watchpoint de hardware em 0x0019F500 (watchwrite.exe) capturou os gravadores: o
  framework de interface Apt (`c:\packages001_pc\apt\0.19.optimized\source\apt\_AptValue.h`)
  empilhando variáveis locais, mais matemática vetorial em 0x0043A2EF/0x0043A47C/0x0043A653. Tudo
  temporário, não a fonte da transformação.
- Globais reais confirmadas na imagem do executável: matriz do jogador 0x0112E210 e alvo de visão
  da câmera 0x0112A840. A global da matriz é o campo +0x198 de um objeto .data
  (base 0x0112E078, vtable 0x00E32A84, nome da instância "WhiteboxCar"); existe um gêmeo no heap
  de cada objeto desses (0x0434E078 para o jogador). 17 pares encontrados.
- A posição do companheiro NÃO está nos primeiros
  0x2000 bytes de qualquer objeto prefixado por vtable (varredura ampla findobj: 0 resultados), nem armazenada como par
  mínimo/máximo de AABB (findaabb: 0 resultados). ESTÁ armazenada como ~26–54 trios de floats seguidos por
  1.0 (aparência de linha de matriz), incluindo um par .data/heap (0x01163640 /
  0x04213640 em uma sessão) — mas o 4º float não é confiavelmente w=1 (um campo
  retornou 51,37), então são estruturas de 4 campos, não matrizes puras.
- Gravar as linhas de matriz do companheiro dentro do processo no momento da CÂMERA é sobrescrito
  pela engine depois no quadro (observado: o valor retornou ao original).
  Foi implementada a transferência da gravação para a interceptação D3D9 PRESENT (fim do quadro);
  gravar 26 dessas linhas **causou crash** — um desses campos é crítico.

### <a id="open-end-handoff"></a>Questão aberta (passagem de trabalho)

A primitiva de gravação da transformação autoritativa continua aberta. Próximos passos em ordem:

1. Watchpoint de hardware (watchwrite.exe funciona e é somente leitura) numa das
   linhas de matriz do companheiro enquanto ele CAMINHA: capturar o código gravador,
   depois ler essa função em `godfather2_10789_se.c` para encontrar a origem de onde
   copia. Esse é o experimento decisivo e não exige gravações no jogo.
2. Interceptar no plugin o getter de posição `FUN_0054dbf0` (o prólogo tem exatamente
   6 bytes: 55 8B EC 83 E4 F0), registrando (nó, posição) — PRECISA registrar num
   array simples, sem sprintf/E/S de arquivo na interceptação: a primeira tentativa gerou
   5000 falhas absorvidas pelo VEH (no plugin) e derrubou o jogo.
3. Controlar a própria camada de comportamentos da engine em vez de memória bruta: a VM de scripts
   registra `SetPositionValues` / `GetPlayerPosition` / `moveToPos`
   (`FUN_00468cb0`), e o handle SimNPC (inspetor) é a entidade sobre a qual chamá-los.
   Isso mantém consistente a cinemática da engine e é a primitiva correta
   para cooperativo no longo prazo.

Inventário de ferramentas em `local/`: findtrip (busca de posição, y amplo, filtro
w=1 opcional), findval (busca de valor de 32 bits), findobj (objetos com uma vtable
contendo posição), findaabb (pares mínimo/máximo), watchwrite (minidepurador com
watchpoint de hardware e dump de registradores), deltahunt (busca de variação em todo o heap),
nearwatch (observar trios próximos a um ponto), puppetdrive/2 (gravação rígida externa a 100 Hz),
coopscan (dump/list/chars/snap/diff).

### <a id="render-pipeline-vs-game-state-2026-10-21-later-still"></a>Pipeline de renderização versus estado do jogo (2026-10-21, ainda mais tarde)

Uma execução de watchpoint de hardware em 0x01163640 (o endereço .data que contém repetidamente
a posição do companheiro) capturou **uma instrução, 0x004175BA**, dentro de
`FUN_00417560` — uma multiplicação de matrizes 4x4 (`out = a * b`, gravada com `movaps
[edx], xmm5` num loop de 4 iterações). A captura de registradores/endereços de retorno identificou
três locais de chamada: `FUN_00419b80 + 0x106` (0x00419C86) e `FUN_0041b9d0`
(0x0041BA8C). Sua descompilação mostra que a origem é um array por thread alcançado
por `fs:0x2C` (TLS), indexado por `*(entity+0x18)`, com rotação/escala em
`+0x6C/+0x70/+0x74`. Portanto, 0x01163640/0x01163610/0x011629d0 são **matrizes
de renderização**, e os gêmeos .data/heap (0x01163640 <-> 0x04303640) são memória temporária de renderização,
não estado do jogo. Gravá-los não pode mover um personagem — coerente com
todas as tentativas fracassadas de gravação de representação até agora.

Busca de variação em todo o heap (deltahunt com a própria variação do companheiro obtida de duas
capturas do inspetor, -14,29/+0,04/-41,52 numa caminhada de 44 m): **apenas dois campos
em todo o processo se moveram por essa variação**, e um deles é a memória temporária de renderização
acima. Conclusão: **a posição do companheiro não é armazenada como trio de floats
em lugar algum** — é uma entidade de simulação cuja posição é integrada e
mantida em outra representação (corpo físico, handle ou derivada sob demanda).

Próximo passo decorrente: não perseguir trios de floats. Capturar o caminho de *leitura*
— observar o próprio buffer de exibição do NPC Inspector SE enquanto ele
atualiza (o SE calcula o valor exibido, então seu código revela
a fonte autoritativa) ou interceptar o setter de scripts da engine
(`SetPositionValues`) pelo plugin e deixar a engine mover o personagem.

### <a id="the-se-inspector-read-path-statically-decoded-2026-10-21"></a>Caminho de leitura do inspetor SE, decodificado estaticamente (2026-10-21)

Análise estática de `GF2ASI.asi` (DLL PE32, base da imagem 0x10000000, sem empacotamento:
as strings do inspetor são ASCII simples nos deslocamentos de arquivo 0x0F0C3C–0x0F1434):

- O rótulo "Position:" fica em VA `0x100F21BC`, referenciado de exatamente um lugar,
  `0x10091802` (`push 0x100F21BC`). O código ao redor é a aba
  General do inspetor: `lea eax,[ebp-0x48]; push eax; call 0x10074730` preenche um buffer de 12 bytes,
  depois três pares `cvtps2pd`/`movsd` e um printf o passam como três
  doubles.
- `0x10074730`: `call 0x10074680` com ECX = objeto inspecionado, `add eax,0x30`,
  depois `call 0x10073180` (conversão de coordenadas para a saída). Portanto, a posição
  é `object + 0x100`.
- `0x10074680` é a decisiva: copia quatro `movups` de
  `ecx+0xD0`, `ecx+0xE0`, `ecx+0xF0`, `ecx+0x100` para uma matriz local de 16 floats
  e converte cada linha. **A transformação de mundo de um personagem é uma matriz 4x4 em
  `object + 0xD0`; sua 4ª linha é a posição.** Isso corresponde ao próprio compositor da engine
  (`FUN_0088d6e0`, ramificação A, lê uma posição em `ctx+0x100`).

`findmat.exe` (novo, local) procura exatamente essa estrutura: uma matriz de 16 floats
com linhas 0..2 ortonormais, `w = 1` e a 4ª linha igual a uma posição dada.
No companheiro, encontra 30 objetos: três na altura dos pés com o valor
exato do inspetor (`0x04396720`, `0x043968E0`, `0x229A9E30` naquela execução) e uma série
de 27 na altura central (`0x22B0xxxx`–`0x22B8xxxx`) cujas posições variam suavemente
dentro de alguns decímetros — um histórico/rastro de movimento, não uma única transformação.

Gravar a posição do jogador na 4ª linha dos três objetos na altura dos pés
dentro do processo em PRESENT (gravações de 12 bytes, `w` preservado) deixou o modelo parado sobre
seu marcador — esses objetos não são o que a renderização do esqueleto lê. O próximo
passo barato: colocar o watchpoint de hardware num dos objetos de rastro
(`0x22B0xxxx`) enquanto o companheiro caminha; seu gravador é o código de movimento/IA, e
sua origem é a transformação de simulação que uma representação precisa gravar.
### <a id="watchpoint-on-a-found-matrix-it-is-a-transient-buffer-2026-10-21"></a>Watchpoint numa matriz "encontrada": é um buffer transitório (2026-10-21)

O watchpoint de hardware na linha de translação de uma das 21 correspondências findmat
(`0x430B4B30`) disparou 12 vezes num único endereço de DLL, `0x6EF6CC8E`, com
`rep movsb` nos bytes anteriores a EIP e um cursor de origem avançando byte a byte
(`ESI 0x015477BD..C0`), isto é, uma **cópia genérica de bytes de um buffer de
carregamento/streaming** — não uma atualização de personagem. Portanto, as correspondências de
"4x4 ortonormal com a translação correta" nessa região do heap são conteúdos transitórios de buffer que
por acaso satisfazem o teste; a caça a matrizes por valor se esgotou.

O resultado sólido permanece: o inspetor SE prova o *layout*
(`object+0xD0` = matriz de mundo, 4ª linha = posição em `object+0x100`). O que
ainda falta é a *identidade do objeto*: qual objeto do heap é o companheiro.

Próximo passo recomendado (bem delimitado, sem mais buscas às cegas): o SE mantém seu
alvo do inspetor na própria `.data` (base da imagem 0x10000000, seção .data em
VA 0x10179000). Encontrar o ponteiro estático lido pelo código do inspetor
(`movl (%edi), %ecx` em 0x100917CB) rastreando para trás a partir do prólogo da função de 0x10091802
e de estáticas como `0x10179400`, depois ler o objeto alvo e
sua matriz +0xD0 diretamente — esse é o objeto em que o próprio SE confia, e o
mesmo em que uma representação deveria gravar. Alternativa de maior valor no longo prazo:
interceptar o setter de scripts `SetPositionValues` da engine e deixar a engine mover o
personagem.
### <a id="inspector-chain-traced-why-present-time-writes-cannot-work-2026-10-21"></a>Cadeia do inspetor rastreada; por que gravações no momento de Present não funcionam (2026-10-21)

- A função de entrada do inspetor é `0x10091740` (`movl %ecx,%edi` em +0x2B, então
  `this` -> EDI). Ela tem exatamente um chamador, `0x1008F891`, que passa
  `lea 0x10(%edi), %ecx` — isto é, o contexto do inspetor é `inspector_object+0x10`,
  e `*(context)` é o objeto alvo inspecionado (cuja matriz `+0xD0`
  e posição `+0x100` o SE exibe).
- O objeto inspecionado NÃO é o SimNPC: `SimNPC+0xD0` contém dados de handle/registro
  (`3, 0, ptr, 0, ...`), não uma matriz. O alvo é outra entidade.
- As strings `SetPositionValues` / `moveToPos` / `GetPlayerPosition` não
  existem em GF2ASI.asi: o SE chama funções da engine diretamente, não pelos
  nomes de scripts. "Teleport" no ASI é apenas o rótulo de um botão de menu (referenciado
  de 0x1008D6F0 e 0x1008F793, ambas chamadas de registro de interface).

**Por que toda gravação direta de transformação falhou:** o renderizador posiciona o esqueleto
antes no quadro que nossa interceptação PRESENT. Gravar a matriz de mundo em PRESENT,
portanto, chega um quadro tarde para o esqueleto, e gravar antes é
sobrescrito pela própria cinemática da engine. O personagem só pode ser movido
pelo caminho de atualização da engine (seu setter / comportamento de script), não
alterando uma matriz. Essa é a conclusão de toda a busca de transformações e
reordena o trabalho: a próxima tarefa é localizar o setter da engine
(a função que o próprio jogo chama quando um NPC recebe ordem de ir a uma posição),
por exemplo, observando a gravação em `entity+0xD0` antes no quadro — definir o
watchpoint na matriz de uma entidade *conhecida* e deixar a *engine* mover essa entidade
(um NPC caminhando sozinho ou o jogador se teletransportando), depois ler a pilha de chamadas
do gravador — em vez de gravar e observar.
### <a id="the-se-has-no-direct-set-position-call-2026-10-21"></a>O SE não tem chamada direta de "definir posição" (2026-10-21)

Varrer .text de GF2ASI.asi por chamadas `E8` cujo destino cai na faixa de
endereços do jogo (0x00400000–0x01230000) produz exatamente seis locais:
FUN_005d9ab0+0xAA, FUN_005d93e0 (construtor no estilo LinkedObject),
FUN_004b6060 (construtor de objeto pequeno), FUN_0094bf90 (construtor de interface/parâmetro),
FUN_0059fd60+0x2DF e FUN_005167d0+0x8EB. Nenhum é setter de posição: o SE
acessa funcionalidade do jogo pela camada de interface/scripts, não por chamada direta
à engine. Portanto, não há atalho para o setter dentro do SE.

Consequência para a próxima sessão: implementar a chamada à própria VM de scripts do jogo
pelo nosso plugin. Peças relevantes da engine (todas no corpus descompilado):
`FUN_00468cb0` registra nomes de scripts, `FUN_00468ea0` mostra o padrão
de chamada (`iVar1 = *(int *)(DAT_012233f4 + 0x18)`, `FUN_00625ca0` empilha nome,
`FUN_00633cb0` busca, `FUN_00636570` invoca). Decodificar esses três auxiliares e
chamar `SetPositionValues` / um comportamento `moveToPos` no handle SimNPC
do companheiro é a próxima tarefa concreta e delimitada — e também a primitiva correta
para cooperativo em rede depois.
### <a id="script-vm-object-located-calling-conventions-disassembled-2026-10-21"></a>VM de scripts: objeto localizado, convenções de chamada desmontadas (2026-10-21)

Endereços ativos no jogo em execução: `DAT_012233F4` contém `0x04750C4C`; a VM é
`*(0x04750C4C + 0x18)` = `0x1ABC0108`. Layout da VM: `+0x08` = ponteiro de pilha,
`+0x10` = objeto de limites da pilha (`+0x20`/`+0x24`), `+0x40` = tabela de globais
(primeira dword 5 = tag de tabela, `+0x44` = objeto tabela).

Convenções exatas de chamada, lidas do executável real com llvm-objdump:

- `FUN_00625ca0` = **cdecl(vm, const char* name)**. Prólogo
  `push ebp; mov ebp,[esp+0xC]` -> arg2 = nome; `mov eax,[esp+8]` -> arg1 = vm.
  Empilha um valor na pilha da VM: grava tipo 4 e um id de string, avança
  `vm+0x08` em 8. Nome NULL empilha um valor zero.
- `FUN_00636570` = a invocação. **cdecl com 3 argumentos na pilha** (ponteiro
  de código de continuação, ponteiro para o frame preparado, comprimento em bytes) **mais a VM em
  ESI**, isto é, uma convenção personalizada de registradores. O único local de chamada no jogo
  (`0x00468F2B`) empilha `0x6261E0`, `lea eax,[esp+0x10]` e
  `stack_top - args_start`, depois `add esp,0x10`.
- `FUN_00633cb0` = busca cdecl(vm, table_value, key_value, depth), retorna um
  ponteiro para o valor resolvido.

Como a invocação recebe a VM em ESI, uma chamada de plugin precisa de um pequeno stub assembly
(definir ESI = VM, empilhar os 3 argumentos, chamar 0x00636570) — não uma chamada C comum.
Plano para a sessão de implementação: espelhar a sequência exata de
`FUN_00468ea0` (empilhar nome -> buscar nas globais -> empilhar argumentos -> invocar com a
continuação `0x6261E0`) primeiro para um getter inofensivo (`GetPlayerPosition`),
registrar o resultado e só então chamar `SetPositionValues` no companheiro. Fazer isso
na própria thread do plugin com VEH ativo.
### <a id="script-vm-lookup-works-invoke-from-a-render-hook-faults-2026-10-21"></a>VM de scripts: busca funciona, invocação de uma interceptação de renderização falha (2026-10-21)

Implementado no plugin e testado ao vivo:

- `DAT_012233F4` -> `0x04750C4C` -> `+0x18` forneceu a VM (`0x1AB90108` naquela
  execução); `FUN_00625ca0(vm, "GetPlayerPosition")` empilhou o nome e
  `FUN_00633cb0(vm, vm+0x40, stack_top-8, 0)` o resolveu nas globais.
  **A busca teve sucesso: tipo 6 (função), valor 0x1A2E4650.** Portanto, a
  API de scripts é acessível pelo plugin, e `GetPlayerPosition` realmente existe
  na tabela global da VM.
- A invocação é o problema. A primeira tentativa usou um stub inline-asm; a segunda usou
  um stub de bytes montado à mão (`push esi; mov esi,[esp+8]; ...; call; add esp,12;
  pop esi; ret`) com a continuação 0x6261E0. Nas duas vezes o jogo morreu na
  invocação: VEH registrou ~5000 falhas absorvidas num endereço fixo do plugin e
  o processo terminou. Portanto, `FUN_00636570` não pode ser chamada da interceptação de câmera —
  a VM quase certamente só é válida enquanto a própria atualização de scripts do jogo está
  rodando, e chamá-la de uma interceptação de renderização corrompe seu estado.

Próximo passo no caminho da VM: interceptar a função de scripts/atualização do jogo e emitir a
chamada de dentro dela (mesma thread, VM ativa) ou, melhor, encontrar onde o próprio
código do jogo empilha e invoca uma função de script pelo nome e reutilizar esse wrapper.
O resultado da busca (tipo 6, valor 0x1A2E4650) é uma boa referência para esse trabalho: ele
identifica o objeto de função `GetPlayerPosition` na VM.
### <a id="script-vm-the-safe-helpers-found-2026-10-21"></a>VM de scripts: auxiliares seguros encontrados (2026-10-21)

Buscar a global da VM (`DAT_012233f4`) no corpus produz seis funções:

- `FUN_0043e140` — construtor do proprietário da VM (armazena `param_1` em `DAT_012233f4`);
  `FUN_0043e250` — seu destrutor.
- **`FUN_0043e480`** — auxiliar seguro de "resolver nome de script": empilha o nome,
  busca nas globais, copia o valor resolvido sobre o topo da pilha,
  verifica `type == 6`, depois chama **`FUN_006255e0`** (auxiliar de remoção da pilha) e
  retorna se o nome é uma função. Esse é um exemplo seguro e completo da
  sequência empilhar/buscar/remover com limpeza da pilha — usá-lo como referência para
  qualquer busca por nome.
- `FUN_00468ea0` / `FUN_00468f40` — wrappers de "chamar função de script":
  EAX = nome, EDI = contagem de argumentos, `[ebp+8]`/`[ebp+0xC]` descrevem os
  argumentos; `FUN_004c8460` os empilha; `FUN_00636570` invoca com a
  continuação `0x6261E0`. `FUN_00468f40` é o mesmo para `CallLuaFunction`.

Portanto, a VM tem uma API interna adequada (`FUN_0043e480` para buscas,
`FUN_00468ea0`/`FUN_00468f40` para chamadas) que mantém a pilha equilibrada. A próxima
tentativa de mover um personagem deve chamar `FUN_00468ea0` (ou espelhá-la exatamente,
incluindo `FUN_006255e0` para cada empilhamento) em vez da `FUN_00636570` bruta, e
deve rodar enquanto a atualização de scripts do jogo estiver ativa.

### <a id="script-vm-the-wrapper-fails-too---the-vm-needs-the-script-update-context-2026-10-21"></a>VM de scripts: o wrapper também falha — a VM precisa do contexto de atualização de scripts (2026-10-21)

A segunda tentativa ao vivo usou o wrapper de chamada do próprio jogo `FUN_00468ea0` por um
stub de bytes montado à mão (nome em EAX, contagem de argumentos 0 em EDI, duas dwords
zero na pilha limpas pelo `ret 8` do wrapper), chamado uma vez da interceptação de câmera.
O log registrou `vm: calling GetPlayerPosition via FUN_00468ea0`, e o
processo morreu antes de `vm: call returned`. Junto da falha anterior de invocação
bruta, isso é conclusivo: **a VM de scripts não pode ser controlada pelas interceptações de câmera ou
present** — ela só é válida enquanto a própria atualização de scripts do jogo está
em execução. Chamá-la de qualquer interceptação de renderização/atualização corrompe seu estado e
derruba o processo.

O teste de VM está novamente desativado no plugin; o jogo está estável.

O próximo passo desta linha de trabalho é, portanto, mais restrito e concreto: localizar a
atualização de scripts do jogo (a função que aciona a VM a cada quadro — seu proprietário é
`DAT_012233f4`, a entrada do interpretador é `FUN_00635ab0`, alcançada a partir de
`FUN_00636570`), interceptar essa função e emitir a chamada `FUN_00468ea0` de
dentro dela enquanto a VM estiver ativa. Só então `SetPositionValues` será acessível.
