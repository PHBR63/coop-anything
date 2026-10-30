# <a id="clive-barkers-jericho-2007"></a>Clive Barker's Jericho (2007)

| | |
|---|---|
| Motor | MercurySteam ScrapEngine (motor de Scrapland), Lua 5.1.1, D3D9, PhysX 2.7 |
| Versões testadas | DVD comercial, `Jericho.exe` 1.0.0.1, SHA-256 `7fb5b759823283a83b685adc4848289a149f520ddbab6dbc7f9e6131b15d2a62`, Windows 10 e 11; também com SMOD 1.0.3 |
| Projetos | [Jericho Co-op+](https://github.com/dolbaras/jericho-coop) (entrada "Jericho Co-op+", chamado Jericho Co-op antes da 0.2.4); fork MAK-PIVO/jericho-coop (não público desde 2026-10-22), reincorporado na 0.2.1 |
| Nível de QA | automated (campanha inteira por LAN entre dois PCs, menus operados como por um jogador com controles virtuais, todas as separações da história com host/cliente reais); primeira sessão humana pelo Steam (missões 1-8) |
| Última atualização | 2026-10-24 (0.2.7) |

## <a id="where-things-stand"></a>Situação atual

De dois a quatro jogadores podem jogar a campanha inteira juntos, cada um controlando um integrante enquanto a IA controla os demais, por rede local, IP direto ou Steam; dois podem compartilhar um PC em tela dividida. Versões com instalador ([distribuição](https://github.com/dolbaras/jericho-coop/releases), 0.2.7 ao escrever), em inglês, russo, alemão, francês, espanhol e italiano; desde 0.2.3, o atalho instala uma versão mais recente do GitHub antes de iniciar. Todas as fases, poderes, partes da história e cenas passam por testes automatizados. Uma primeira sessão humana no Steam (missões 1-8) encontrou inimigos ignorando convidados, paredes só para eles, scripts retirando controles e ações invisíveis ao host; 0.2.2 corrige. A 0.2.3 dá a cada equipe seu jogador a seguir, sincroniza todos os objetos quebráveis/móveis e mantém incapacitados no lado correto das separações da história. A 0.2.4 insere os jogadores na narrativa (host é alma de Ross, segundo é projeção astral de Jones, jogadores 3-4 são integrantes da equipe), acrescenta modo de exibição/taxa de atualização nas opções Video, renomeia Jericho Co-op+ (faz mais que cooperativo) e corrige problemas da revisão completa/testes de distribuição. A 0.2.5 conclui pendências da 0.2.4 (jogador em tela dividida esperando corpo, runa do chefe final, pastas de qualquer nome), permite iniciar sem mouse e corrige registro do instalador. A 0.2.6 corrige saída parada em aviso D3D e atualiza toda versão anterior, inclusive primeiro teste sem instalador. A 0.2.7 preserva HUD em telas largas, dá dicas individuais, impede parada do motor ao trocar personagem em tela dividida, limita quadros à atualização da tela (dobro em tela dividida), faz Rawlings sempre atender incapacitados 3-4, impede queda do jogador dividido do PC convidado através do mapa no início e corrige falha rara ao desaparecer comandante psíquico no convidado. Campanha inteira concluída por pessoas ainda pendente.

## <a id="existing-work"></a>Trabalhos existentes

- Antes deste projeto, nenhum mod cooperativo/multiplayer encontrado (GitHub, Nexus, ModDB, fóruns Steam por busca web, 2026-10-18). Pedidos: [ModDB](https://www.moddb.com/forum/thread/clive-barkers-jericho-multiplayer), [Steam](https://steamcommunity.com/app/11420/discussions/0/846963710897727939/), [GameFAQs](https://gamefaqs.gamespot.com/boards/934444-clive-barkers-jericho/41226885).
- MAK-PIVO/jericho-coop (MIT, último envio 2026-10-21; não público desde 2026-10-22, trabalho preservado em Jericho Co-op 0.2.1+), fork anterior à 0.2.0 que depois incorporou 0.2.0: salas Steam, QTEs compartilhados, interpolação, portas/objetos/poderes, monitor de controle, indicador large-address-aware, acertos em chefes e poderes Rawlings dos clientes, correção da câmera lenta corpo a corpo. Adaptados com crédito na 0.2.1 (LAA pelo instalador só no executável comercial, original preservado). Não aproveitados: patch em memória de instância única (proxy de testes já trata por variável de ambiente) e, por enquanto, sala reformulada só on-line (remove tela dividida).
- SMOD, ferramentas de modificação e pacote de regras: https://www.nexusmods.com/clivebarkersjericho/mods/2. O mod detecta e segue as regras SMOD do host quando todos o possuem.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Scripts:** jogabilidade Lua 5.1. `*.packed` (BFPK) contém `*.lc`, cabeçalho u32 + bytecode Lua 5.1 padrão com depuração, comprimido por zlib. Os 1533 arquivos descompilam com unluac. Cada fase tem `scripts/` (mapa, gatilhos, inimigos, cenas).
- **Linha de comando:** `-Name:value` define qualquer variável `game.cfg`. `-InitLuaLine:"..."` executa Lua após `init.lua` uma vez e é limpo. O mod o rearma em sua atualização, executando em toda fase. `dofile` aceita caminhos absolutos de arquivos avulsos.
- **Rede do motor:** executável mantém cliente/servidor UDP e biblioteca Lua `Net` de Scrapland, mas o pacote de entrada espera dados de nave Scrapland e derruba servidor (`newpos<=size`, FileSys\FileMem.cpp:46). Não é usado. Transporte próprio no proxy `dinput8.dll`, com entradas `Net` não usadas reescritas para apontar a ele.
- **Equipe:** entidades `WalkChar`. `UsrControl` 0 é local, -1 é IA; `oAI.bEnable` ativa IA. Com IA desligada, `InCtrl_Walk`/`InCtrl_Str` e `Ang` movem o corpo com animações próprias, exibindo remotos. Ações com movimento de raiz (`UseDisp`) não devem mover remoto, para não divergir dos snapshots.
- **Hook por quadro:** `OnRenderDebug` nomeia função Lua chamada a cada quadro renderizado. Independe do tempo do jogo, ao contrário de `Game.AddScheduledFunc`, continuando em câmera lenta.
- **Cenas:** 40 cenas internas. As de primeira pessoa animam braços de um personagem (`FP_<Char>`) e corpos completos dos demais (`<Scene><Char>`). Introduções são Bink. QTEs são callbacks Lua, podendo ser atribuídos a um jogador, aprovados automaticamente ou oferecidos a todos.
- **Vestígios de tela dividida:** código Scrapland ainda presente. Com segunda entidade e chamadas por vista, cada quadro alterna o jogador (cada vista tem metade da taxa). Projeção astral de Jones ocupa o único conjunto de controles; enquanto isso, o mod dirige o outro corpo pelo controle próprio.
- **Unidades de câmera:** `FCam.Ang` definido em radianos, mas `camAng` lê graus. Ocultar modelo com `bObjectVisible`. Propriedades de entidades estão como strings próximas a `TimeSpeed` e `EntityLink`.
- **Instância única:** recusa segunda cópia por `FindWindowA("MercuryGameClass")` dentro de SecuROM. Nos testes, proxy retorna NULL sob variável de ambiente. Código do executável nunca alterado.
- **Janela sem foco:** pausa ao perder foco. Testes simulam primeiro plano e suprimem desativação; também deixam de ler teclado, mouse e DirectInput sem foco, para a digitação do usuário não alcançar o jogo.
- **Ocultar corpo:** com `bCheckFPSVisible`, motor decide visibilidade e ignora `bObjectVisible`: integrante aparece, corpo próprio oculto em todas as vistas (registrado). Desligando `bCheckFPSVisible`, `bObjectVisible` funciona. Cenas ocultam com `Active = 0` (também interrompe).
- **Modelos de primeira pessoa:** `0FP_<char>` / `1FP_<char>` seguem câmera do usuário no campo oculto `id` e aparecem em todas as vistas; motor redefine `bObjectVisible`/`Active` a cada quadro, preservando `id`. Tela dividida oculta braços da outra metade atribuindo usuário não usado (3). Scripts leem `Game.UsrEntity(fp.id)`, que precisa remapear. Indicadores/IDs Lua valem no quadro seguinte ao próximo, ou seja, para a outra vista dividida.
- **Arquivos e avulsos:** `Pack1.packed` junto a `Data0*.packed` é montado e pode conter animações/modelos, não texturas (trava carregamento). SMOD move arquivos para `Packed\` e lê avulsos; assim não lê Pack1, exigindo também arquivos gerados ao lado dos originais. Strings SM3 têm comprimento prefixado e tamanhos de bloco 0, permitindo mudar comprimento do caminho de textura no modelo (texturas do rifle TrueRoss apontavam à pasta Jones).
- **game.log** lista texturas ausentes ("Texture not found"), vistas como superfícies quadriculadas ou chapadas: testes comparam às ausências do original.
- **Steam:** jogo não tem rede Steam; mod usa exemplo Spacewar (480) por `steam_api.dll` de versão fixada só quando escolhido. Sobreposição Steam responde XInput com controles vazios (Spacewar é Steam Input); proxy lê por cópia privada `xinput1_4.dll` enquanto ela está carregada.

Notas detalhadas: [NOTES.md](NOTES.md).

## <a id="what-we-changed"></a>O que alteramos

Tudo fica no repositório do mod. No PC, instalador só adiciona arquivos, define large-address-aware no cabeçalho comercial e gera `Pack1.packed` (com SMOD, avulsos) a partir dos arquivos do jogador; substituições recebem backup e restauração ao desinstalar.

- **Transporte:** ENet em thread de segundo plano (descoberta LAN, IP direto) ou salas/mensagens P2P Steam, escolhidos pelo host. Lua vê as mesmas `Net.Coop*` nos dois.
- **Sessão:** entrada "Co-op", telas por rede, sala (personagem, apelido, prontidão, capítulo/salvamento, segundo local), configurações (dificuldade, resistência, ações exclusivas, QTE, dano da IA aliada, vista de cenas), verificação de versão, salvamentos cooperativos separados.
- **Autoridade do host:** inimigos, gatilhos, cenas, salvamentos e fases. Clientes recebem snapshots (20 Hz, tempo e interpolação), eventos e atualização ao entrar tarde. Acertos, usos, reanimações, poderes (telecinese, runas, fogo, balas fantasmas, Ababanili...), portas e destruição chegam ao mundo do host.
- **História:** ações exclusivas oferecidas ao dono do personagem, com IA alternativa; partes escritas para substituto IA ampliadas para jogadores (portão Brandenburg, restauração do bunker, ato 1 com Ross). Jogadores além dos vivos viram espíritos e podem assumir corpos livres.
- **Cenas:** todos assistem simultaneamente com câmera original; só pula se todos pularem. Vista experimental pelos próprios olhos reproduz em primeira pessoa pelo personagem, com olhar dirigido e animação redirecionada da primeira pessoa.
- **Tela dividida:** segundo local com vista/HUD/controle próprios, hospedando ou entrando; conexão de controles durante execução, projeção astral nos dois sentidos.
- **Chefes/poderes na rede** (do fork): acerto cliente em chefe vulnerável numa parte carrega o osso dessa parte; maldição, calma e cura Rawlings atuam na máquina que controla o alvo.
- **Robustez:** cliente cujos controles ficam tomados fora de cena/história recupera em 12 s; sem corpo após pular cena, recupera; isolado por passagem fechada recebe opção de voltar ao grupo.
- **Etapas por máquina (0.2.2):** scripts para jogador único executam em todas para seu próprio corpo. Etapas que travariam, virariam ou moveriam remoto ficam a cargo dele (orientação/dica, IA alternativa); barreiras invisíveis desativadas ao fim da conversa seguem host.
- **Inimigos (0.2.2):** motor só escolhe alvos entre integrantes IA; host passa a oferecer humano mais próximo. Geradores só no host.
- **Ordens por jogador (0.2.3):** gerenciador de áreas e seguir só atendem usuário local 0. Cada equipe (Alpha/Omega) tem líder: ato 1 Ross lidera todos; depois, primeiro jogador da equipe a lidera, e equipe sem líder vai para quem ainda não lidera. IA segue com perseguição própria e ordem de manter posição a fixa. Em separações, IA segue jogador do mesmo lado.
- **Objetos (0.2.3):** todo objeto colocado quebra para todos, independentemente do nome; empurrados/derrubados/arremessados repousam onde a máquina que os moveu informa pelo host. Entrada tardia recebe ambos os estados.
- **Lados das separações (0.2.3):** host informa quais personagens em cada lado; incapacitado só assume corpo livre do próprio lado, senão espera Rawlings.
- **Atualizações (0.2.3):** atalho executa pequeno inicializador PowerShell: lê última versão por API GitHub, baixa ZIP só das URLs do projeto, confere SHA-256 do recurso, executa instalador sem intervenção e inicia (pelo Steam se instalação Steam); offline só inicia.
- **Idiomas (0.2.2):** textos do mod e entradas SMOD nos seis idiomas, convertidos à página de código (cp1252 ou cp1251 russo); ampliada opção original de proporção, não criada outra.
- **Instalador:** janela de etapas, barra (também botão da tarefa), minutos restantes, seis idiomas; encontra jogo, preserva substituições, atualiza/desinstala. Inclui Python incorporado para gerar animações/correção de Ross dos arquivos do jogador; marca executável comercial large-address-aware e preserva/restaura original.
- **Relatos de bugs:** F11 salva últimos 30 s em AVI Motion-JPEG (quadros escalados na GPU, JPEG via WIC Windows em thread, mantidos em memória).
- **Almas (0.2.4):** host é alma de Ross, segundo projeção Jones (narrativa original: projeta nos outros e usa habilidades); ambos trocam livremente, projeção interrompida com Jones perdido, possuído ou preso. Jogadores 3-4 mantêm personagem, outros corpos acinzentados no menu. Campos só aceitam escrita Lua (ler gera erro/nil); mod repete teste do jogo de corpo selecionável.
- **Exibição (0.2.4):** modo (cheia, janela, sem borda) e atualização no Video original, aplicados por Accept e descartados em Cancel; janela sem borda ocupa monitor por hooks na criação e parâmetros de apresentação D3D9.
- **Correção do motor (0.2.4):** espírito de fogo final (Ababanili, direção em `0x4fc9b0`) escolhe presa sem verificar; todos próximos incapacitados/presos pela runa (impossível no individual) causavam leitura NULL e falha. Manipulador vetorizado retoma essa leitura no caminho próprio sem alvo, só com bytes iguais ao comercial. Arquivo não alterado.
- **Sem mouse (0.2.5):** jogo para com "Mouse not found" se DirectInput não cria mouse (`CreateDevice(GUID_SysMouse)` falha com só controles). Hook fornece dispositivo próprio de mouse imóvel, permitindo jogar em tela dividida na TV.
- **Pastas de qualquer nome (0.2.5):** motor abre via ANSI; caminho Lua passa sem perdas pela página de código, senão nome curto 8.3, senão relativo à pasta de trabalho (atalho/Steam iniciam na pasta do jogo; algumas unidades desativam 8.3).
- **Saída limpa (0.2.6):** último `Release` D3D9 mostra modal "A D3D object has a non-zero reference count" se ainda há referências. Proxy intercepta `Release` (posição 2) e libera antes gravador F11, superfícies de captura/tela dividida quando restam as últimas referências do motor.
- **HUD dividido em telas largas (0.2.7):** disposição que preserva proporções (viewport reduzido à forma da tela completa, cantos às bordas, último lote 2D na viewport de origem) também na vista larga, antes omitida: HUD ficava duas vezes mais largo que alto, mensagens piscavam na outra metade.
- **Limite de quadros e voo da troca (0.2.7):** sem limite original/sincronização vertical, proxy espera antes de `Present` para manter taxa da tela (dobro dividido, cada vista recebe quadros alternados). Voo da alma terminava no quadro de início (cooperativo não desacelera mundo), removendo câmera usada ("Check failed: GetActiveCamera() != this" no dividido); agora final espera 0,1 s.
- **Corpos na mudança de fase (0.2.7):** estados da fase anterior chegavam ao host após carregar e eram retransmitidos; cliente movia corpo do seu segundo local, representante no primeiro segundo antes de assumido, à posição antiga fora do mapa. Host só aceita estados após mensagem de fase carregada; cliente não aceita no primeiro segundo nem cópias retransmitidas de seus corpos.
- **Eventos de inimigos que chamam IA (0.2.7):** clientes espelham ações e eventos; quatro classes terminam aparecer/desaparecer chamando IA (`oAI:OnAfterDisappear()`), que desativada no cliente alcançava ponteiro obsoleto (falha em cerca de uma de dez execuções de uma separação). Clientes ignoram chamada e mantêm efeitos.
- **Atualizar qualquer versão anterior (0.2.6):** instalações sem registro (0.1.0 extraída na pasta) reconhecidas por marcador do proxy/arquivos; instalador atualiza/remove normalmente, sem preservar arquivo de mod antigo como original.
- **Desenvolvimento:** console Lua no teste ativo (UDP 127.0.0.1, só testes), acessado do segundo PC por ssh.

## <a id="qa"></a>QA

Executores em `tools/` do mod (`run_pair.ps1`, `run_bot.ps1`, `run_menu_pair.ps1`, `level_smoke.ps1`, `storylines.ps1`, `puppet_jitter.py`) e executores LAN do ambiente. Toda verificação é execução por script com asserções no log; janelas silenciadas no segundo monitor, nunca duas instâncias D3D no mesmo PC.

Resultados 0.2.6 (2026-10-24):

- Regressão como 0.2.5 (33/33 fases por LAN, tela dividida com controles virtuais, sessão Steam real, nove separações, almas, espera do segundo, sem mouse), mesmos resultados.
- Saída pelo menu do pacote instalado: termina em 1 s no menu principal, após clipe F11 e em fase dividida (DLL 0.2.5 para no diálogo).
- Toda versão instalada como distribuída (0.1.0 extraída, 0.1.1+ por instaladores), atualizada a 0.2.6 e removida: individualmente e nove seguidas, pasta final igual à instalação limpa; cada uma também removida diretamente pelo novo instalador.
- Atualização de 0.2.5 pelo atalho, por fonte local e distribuição real GitHub (checksum igual).
- Teste de almas mostrou terceiro incapacitado sem reanimação em 12 s em algumas execuções; A/B com DLL 0.2.5 igual (IA Rawlings no host nem sempre vem); corrigido na 0.2.7.

Resultados 0.2.7 (2026-10-24):

- Campanha inteira com dois jogadores por LAN entre dois PCs e jogador dividido no convidado: 33/33, sem falha, código final 0.2.7; controles, Steam real, nove separações, teste de almas duas vezes, segundo esperando, início sem mouse.
- Queda do jogador dividido em Rom_Coloseum (usuário, teste de campanha): log mostrou corpos movendo 6000 a 87000 unidades em 10 de 33 inícios; após correção, host descartou estados antigos em todos e nenhum corpo mudou entre fases na campanha.
- Falha cliente em uma separação (WWII_PillBoxes, `AccessViolation at 04A0400B`, chamada IA do comandante psíquico): após correção, eventos de desaparecer/aparecer forçados seis vezes no convidado e separação do chefe final executada, sem falha.
- Rawlings para incapacitado 3-4: host faz IA curar corpo deixado esperando; todas as execuções de almas reanimaram (uma das primeiras quatro pela alternativa).
- Troca de personagem dividida: parada do motor reproduzida após 19 a 37 trocas na 0.2.6 publicada, nenhuma em 3 x 60 e nas 2 x 60 finais corrigidas (lab/splitswitch.ps1).
- Limite medido: 120 quadros/s dividido em tela 60 Hz, 60 sem dividir.
- HUD dividido em vista larga (acima de 1,85): imagens antes/depois de fase em janela 1912x1001 (lab/splithud.ps1), dica só na metade do destinatário, escurecimento em toda a metade; todos os testes divididos repetidos com nova DLL.

Resultados 0.2.5 (2026-10-23):

- Campanha inteira com dois por LAN entre PCs: 33/33 até o final, sem falha; controles virtuais divididos, Steam real, nove separações e almas como 0.2.4.
- Cada correção conferida no jogo: controle do segundo não move primeiro enquanto espera corpo (antes/depois); segundo continua quando Rawlings é preso na runa final, sem efeito da trava de troca do tutorial; corpo abandonado após espera volta à IA ao reanimar; tela dividida começa ao liberar corpo; início com falha do mouse DirectInput (controle ainda joga); pasta com letra grega nos dois PCs (nome curto em um, caminho relativo no outro sem 8.3); atualização Auto retorna a 75 Hz e janela sem borda mantida até reiniciar.
- Instalação limpa, remoção (hash comercial restaurado) e atualização da 0.2.4 publicada pelo atalho/GitHub real. Descobriu atalhos no registro unidos numa linha desde 0.2.3 (remoção deixava-os, atualização seguinte podia falhar); corrigido, com leitura dos registros antigos.
- Republicado no mesmo dia: rótulo cooperativo cobria "Press [ENTER] or START" e janela 4:3 em monitor 16:9 usava disposição 16:9. Verificado em 16:10/4:3, com/sem SMOD, testes em segundo plano sem teclas, com capturas; atualização de 0.2.4 repetida pelo GitHub real.

Resultados 0.2.4 (2026-10-23, código final):

- Campanha inteira com dois por LAN: 33/33 de Alk_Desert ao final, sem falha; tela dividida virtual; Steam real entre duas contas.
- Nove separações com host/cliente reais. Uma derrubou host no chefe final (leitura do motor acima); após correção, mesma separação e leitura forçada (todo Ababanili perdendo presa por quadro durante dois minutos) sem falha.
- Almas em dois PCs: papéis, outros corpos do terceiro acinzentados e troca por mira recusada, segundo movendo livre, projeção interrompida/liberada, terceiro incapacitado esperando e reanimado.
- Exibição: tela cheia no segundo PC a 60 Hz e Auto retornando aos 75 Hz; aviso de reinício nos menus principal/pausa e Cancel sem aplicar.
- Instalação limpa do ZIP e atualização da 0.2.3 publicada pelo atalho (checksum igual, atalho renomeado).

Resultados 0.2.3 (2026-10-23, código final):

- Campanha inteira com dois por LAN: 34 carregamentos até o final, sem falha; nove combinações gráficas sem erro do motor/textura ausente.
- Nove separações com segundo PC hospedando quem avança (história conduzida por etapas) e este PC como quem fica: ondas, lados e avisos iniciaram/terminaram nos dois; caído nunca mudou ao outro lado. Detectada uma separação que definia lados só por gatilho contornável.
- Ambos os ramos de Lost Patrol com bots, incluindo reunião e pular cena.
- Quebrar/mover objetos nos dois sentidos; líderes de equipe com host e convidado.
- Atualização: atalho 0.2.2 para 0.2.3 publicada (checksum igual), checksum errado (inicia versão antiga), offline (3 s).

Resultados 0.2.2 (2026-10-22, código final):

- Campanha inteira LAN (host no segundo PC, cliente aqui com segundo em tela dividida): 33/33 até final, 0 erros Lua, 0 erros do motor, sem falha.
- Dois controles virtuais ViGEm divididos: projeção por ambos, conectar/desconectar controles, botões de cada personagem para segundo. Suíte passava embora jogo falhasse após verificações (ataque corpo a corpo, 4 de 6, também na 0.2.1); agora execução inteira conferida, falha corrigida (6/6 completas).
- Steam com duas contas reais em dois PCs: sala, entrada, fase jogada.
- SMOD, cooperativo e texturas Clive Upscaler (com DXVK) nos dois: saltos com altura total, agachar/levantar do host no cliente, Ross do ato 1; sem defeito.
- Altura dos remotos comparada à do dono: diferença de 20 a 42 unidades antes (dentro/acima do chão), 0 a 2 depois (45 amostras por corpo).
- Correções da primeira sessão humana verificadas entre PCs, maioria com controles virtuais/gravações; novas opções, dicas e instalador operados como jogador e conferidos na tela (seis idiomas, instalar, atualizar, remover, fechar durante instalação).

## <a id="how-to-play"></a>Como jogar

Baixe em https://github.com/dolbaras/jericho-coop/releases, execute `Install Co-op.bat`, inicie e escolha Co-op. Host: Host game, rede (local ou Steam), capítulo, Create session. Demais: Join (local) ou Join through Steam. Internet sem Steam exige UDP 28100 redirecionado pelo host ou LAN virtual para todos. Windows moderno precisa de PhysX legado 9.12.x ou 9.13.x ([tópico Steam](https://steamcommunity.com/app/11420/discussions/0/846945955298387706/)).

## <a id="known-issues"></a>Problemas conhecidos

- Uma sessão humana até agora (missões 1-8 Steam); campanha inteira percorrida por scripts, não pessoas. Relato de cena retirando controle cliente enquanto host andava não reproduzido.
- Steam testado em duas contas reais na mesma LAN; entre redes (retransmissão) e início automático por Join Game (jogo fechado) ainda não testados.
- Vistas divididas alternam quadros, cada uma com metade da taxa.
- Vista de cena pelos próprios olhos é experimental: cenários feitos para uma câmera, retorna à original quando personagem não consegue ver a cena.

## <a id="next-steps"></a>Próximos passos

- Corrigir relatos de partidas humanas (controles reais, Steam entre contas reais); pendências nas issues do mod.
- Campanha cooperativa completa por pessoas, documentada, elevaria para `verified-playthrough`.
