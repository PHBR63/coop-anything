# <a id="obscure-2004"></a>Obscure (2004)

| | |
|---|---|
| Motor | Próprio da Hydravision (arquivos `.hvp`, modelos `.zwo`, scripts `.hoe`); não RenderWare |
| Versões testadas | Steam app 254460, build 215286, SHA-256 de `Obscure.exe`: `7107439eb6ee1b20cad32e87f7a10a3a95b71c0b5ee26b1ec9139b263577a0f2` |
| Projetos | [obscure-coop](https://github.com/Gyurooo/obscure-coop) (MIT; proxy `xinput1_3.dll`, código-fonte e testes com bots); entrada "Obscure / obscure-coop" |
| Nível de QA | automated para compilações até 1.0 (bots com duas cópias reais em um PC); compilações 1.1 a 1.8 não foram testadas por bots, somente capturas, medições e sessões Steam (veja QA) |
| Última atualização | 2026-10-25 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores em dois PCs jogam a história juntos pelo Steam na compilação 1.11. Sessões Steam relataram funcionamento de entrada, movimento, combate, portas, itens, armas, mortes e carregamento de salvamentos. Pela internet, personagens e inimigos têm movimento suavizado. Opções gráficas: supersampling interno, filtragem 16x, configuração ajustada de ReShade e widescreen 16:9 (sem barras laterais, visão ampliada).

## <a id="existing-work"></a>Trabalhos existentes

- Nenhum mod cooperativo on-line encontrado antes deste (lista de buscas em `NOTES.md`, seção 2).
- O jogo tem modo cooperativo **local** para 2 jogadores em uma tela: jogador 2 pressiona Start em um segundo controle.
- Steam Remote Play Together e Parsec funcionam segundo jogadores (transmitem a tela do host; o amigo não precisa ter o jogo). Links em `NOTES.md`.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- Sem código de rede no executável. Um objeto global `*(0x6ab8e4)` contém:
  - dois espaços para jogadores reais (`+0x4fc`, `+0x500`);
  - indicadores da história (161 bytes em `*(+0xa24)`);
  - gerenciador da fase (`+0x510`: listas de humanos, inimigos e itens);
  - máquina de estados: `+4` = 2 jogando; `+8` = 5 mudar de fase (nome `+0x590`, entrada `+0x5d0`), 3 carregar salvamento (espaço `+0x838`).
- Personagens (`CPlayerHuman`, vtable `0x6449e4`): posição `+0x20`, direção `+0x2c`, vida `+0x54`, estado `+0x60`, estado solicitado `+0x230`, armas em `CPlayerInventory` em `+0x128`.
- **Mortes:** quando o jogador 1 morre sem personagem livre restante, `FUN_0044c2b0` troca os dois jogadores reais; o sobrevivente vira jogador 1. Somente o dispositivo do jogador 1 abre a pausa.
- **Salvamentos:** arquivos `SteamRemoteStorage`. O menu de carregamento chama `FUN_004524d0(slot)` no gerenciador `*(game+0xa20)` e define `+0x838` e `+8 = 3`. É o único local que escreve `+8 = 3`.
- **Renderização:** Direct3D 9, renderizador `*(0x6ab890)`. O retângulo da tela vem de `GetClientRect` em janela; caso contrário, do tamanho do modo. Fontes bitmap são desenhadas em pixels 1:1 por `FUN_0045ba60`. O filtro mip é NONE; só o mip 0 é amostrado.
- **Entrada:** XInput por `xinput1_3.dll` (controles), DirectInput 8 (teclado, menus).
- **Verificações de inicialização:** mutex `obscure_lock`, `IsDebuggerPresent`, Steam precisa estar aberto. O invólucro SteamStub permanece intacto.
- Offsets válidos somente para a compilação acima. Lista completa com evidências: `NOTES.md`.

## <a id="what-we-changed"></a>O que alteramos

Um proxy `xinput1_3.dll` ao lado de `Obscure.exe` (somente nosso código; nenhum arquivo do jogo alterado ou distribuído). Código-fonte: [obscure-coop](https://github.com/Gyurooo/obscure-coop).

- **Transporte:** Steam P2P (app id do próprio jogo, apenas amigos), com modo UDP para testes em um PC. O controle do amigo vira o controle virtual 2 do host; o próprio modo cooperativo local controla o jogador 2.
- **Espelhamento com autoridade do host** na cópia do amigo: personagens, inimigos, itens, portas (com animação), indicadores da história, mudanças de fase, armas, bolsa da equipe, ação Give, menus de inventário, imagens e mensagens de coleta.
- **Ataques:** solicitações de um quadro são registradas como eventos no host e reproduzidas em ordem no convidado.
- **Mortes:** o host acompanha o objeto de jogador real que entrou como jogador 2, não o espaço (falha da 0.7: após a troca por morte, o convidado passava ao personagem morto).
- **Carregamento:** o host detecta `+8 == 3` e envia pacote de carregamento com o nome da transferência. O convidado espera o arquivo em seu espaço cooperativo e executa as mesmas duas etapas para o espaço 0. Ao entrar, o convidado também carrega o salvamento do host sozinho.
- **Pausa após morte:** um host morto vira jogador 2 depois da troca; seu START pergunta "Player 2 quits the party". Em vez disso, o host recebe o menu de pausa, aberto como no ciclo principal, 3 s após morrer ou com F1.
- **Suavização (relato de pequenos engasgos pela internet):**
  - Pacotes levam o horário de envio do host; o convidado exibe personagens e inimigos nesse horário menos um atraso adaptável (jitter p90 + intervalo de envio), interpolando entre capturas de estado.
  - Envios usam frequência fixa de 60 Hz; a aproximadamente 275 fps, as taxas antigas por quadro geravam cerca de 600 pacotes/s.
- **Ciclo de portas:** o convidado forçava o estado da porta a cada quadro, registrando 41.509 mudanças de fase engolidas em 2 minutos e provavelmente ocultando um personagem. Agora força uma vez por uso da porta.
- **Supersampling (`SSAA`):**
  - O buffer traseiro fica 2x ou 4x maior; `Present` o reduz por `StretchRect` LINEAR em uma cadeia de troca extra do tamanho da janela.
  - `GetClientRect` do jogo responde com tamanho maior; o layout acompanha. Tela cheia vira janela sem bordas no caminho de janela.
- **Tamanho de texto com SSAA (`TEXT_SCALE`):** enquanto `FUN_0045ba60` desenha um texto, os quadriláteros de glifos e caixas (renderizador `+0xb8`/`+0xc0`) são escalados em torno da âncora do texto.
- **Filtragem (`ANISO`):** `MINFILTER` LINEAR vira ANISOTROPIC; aproximadamente +4% de detalhe em terreno inclinado (medido).
- **Widescreen 16:9 (`WIDESCREEN`, 1.8):** em tela cheia o jogo desenhava imagem 4:3 com barras laterais (viewport 1920x1440 em x = 320 de 2560x1440). O padrão manter-4:3 do renderizador (`mov [esi+0x298], 1` em `0x5ac1db`) é desativado; um hook na função de FOV da câmera (`FUN_00590230`) mantém a visão vertical 4:3 e amplia a horizontal, fazendo a seleção de objetos visíveis acompanhar (sem aparecimentos súbitos nas bordas). Logotipo e fundo do menu principal são esticados em 16:9.
- **Objetos móveis (1.10)** e **janelas e máquinas de venda quebráveis (1.11):** a física do host decide posições de cadeiras, objetos com rodas e bolas de basquete; o host informa quais janelas e máquinas foram quebradas, e o jogo do amigo executa a mesma função de quebra (fragmentos voando não são sincronizados). Testes em `tests/`.
- **Monitor:** se o ciclo principal parar por 5 s, o log registra onde.

Tentados e abandonados: viés de LOD mip (sem efeito: filtro mip NONE) e texturas de fonte 2x (a substituição pelo endereço da textura atingiu endereço reutilizado e desenhou letras no chão).

## <a id="qa"></a>QA

Testes controlam duas cópias reais em um PC (host + convidado por UDP), por pipe nomeado na DLL (controles virtuais, teclas, comandos de teste), leem a memória dos dois processos e verificam estado do jogo. Scripts: `tests/` em [obscure-coop](https://github.com/Gyurooo/obscure-coop); execute `sh tests/suite.sh`. Cada execução registra a identidade da instalação real e dos salvamentos antes e depois.

Últimos resultados:

| Teste | Compilação | Resultado |
|---|---|---|
| `load_test.py --menu` (morte, pausa aparece no host, LOAD > 01 > YES com controle do host, convidado recarrega, personagem morto vivo nos dois, P2 de volta, controle remoto o move; duas vezes) | 1.0 | 21/21 |
| `load_test.py` (o mesmo com comando de teste `loadslot`; convidado também carregou o salvamento sozinho ao entrar) | 1.0 | 19/19 |
| `death_test.py` (P1 morre, host troca jogadores, convidado mantém personagem, sem falha) | 1.0 | 7/7 |
| `camera_test.py` (câmera do host permanece no jogador do host) | 1.0 | 3/3 |
| `give`, `bag`, `door`, `p2door`, `stall` | 0.5 | 7/7, 9/9, 5/5, 7/7, 4/4 |

Compilações anteriores: testes de espelhamento, fases, inimigos, itens, combate, entrada, inventário por jogador, visão, mensagens e ataques, todos em `NOTES.md`.

**Compilações 1.1 a 1.8 não foram testadas por bots em modo cooperativo;** 1.10 e 1.11 adicionaram testes `props`, `break` e `sbreak`. 1.1 a 1.7 (suavização, ciclo de portas, gráficos, tamanho de texto, suavização de inimigos) foram verificadas por capturas e medições em cópias de teste e sessões Steam. 1.8 (widescreen) foi verificada por capturas do buffer traseiro em tela cheia 2560x1440 e sessão de jogador; `death` e `camera` passaram somente na primeira compilação widescreen.

## <a id="how-to-play"></a>Como jogar

Download Windows: [obscure-coop 1.11](https://github.com/Gyurooo/obscure-coop/releases/tag/v1.11). Consulte o [README de obscure-coop](https://github.com/Gyurooo/obscure-coop#play). Resumo:

- **Amigo:** coloca `xinput1_3.dll` e `obscoop.ini` ao lado de `Obscure.exe` e inicia pelo Steam.
- **Host:** inicia uma cópia da pasta do jogo com `start_host.bat`.
- O salvamento do host carrega nos dois; o amigo pressiona START para entrar.
- Ambos precisam da versão Steam (compilação acima) e da mesma versão do mod.

## <a id="known-issues"></a>Problemas conhecidos

- Na tela do amigo, personagem usando escada, suporte ou fechadura não anima (o resultado ainda é espelhado).
- Configuração de controles precisa ser Player 1 = Game controller 1, Player 2 = Game controller 2; caso contrário, os controles trocam.
- Com ReShade e `SSAA`, ReShade precisa de `ReShade2.ini` (o mod apresenta por cadeia de troca extra) e `DepthCopyBeforeClears=1` para oclusão de ambiente. Ambos em `graphics/` do repositório.
- Somente dois jogadores (o jogo tem dois espaços).

## <a id="next-steps"></a>Próximos passos

- Espelhar interações com escada, suporte e fechadura enviando (tipo, identificador) do objeto-alvo com o evento (estados e classes em `NOTES.md`).
- Executar teste de latência e perda (`tests/chaos_run.sh`, `playbook/network-chaos-testing.md`).
- Executar suíte completa de bots na compilação atual.
- Obscure II (Steam app 254480) é alvo separado; o motor é relacionado, mas nada foi verificado.
