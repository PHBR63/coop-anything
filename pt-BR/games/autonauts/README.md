# <a id="autonauts-2019"></a>Autonauts (2019)

| | |
|---|---|
| Motor | Unity 2018.4.35f1, Mono (plugin BepInEx 5 + HarmonyX) |
| Versões testadas | Steam (app 979120), compilação Windows, arquivos de instalação de 2024-10-09 (versão 140.2); testes automatizados no Windows (kit de testes) e Wine 9 |
| Projetos | AutonautsCoop ([Shocklinks/autonauts-coop](https://github.com/Shocklinks/autonauts-coop)), entrada "AutonautsCoop" |
| Nível de QA | automated |
| Última atualização | 2026-10-26 |

## <a id="where-things-stand"></a>Situação atual

AutonautsCoop 0.13.0 é o primeiro beta. Dois ou mais jogadores compartilham um mundo Autonauts: um host e convidados por convites Steam ou IP, iniciando pelos próprios menus do jogo. Convidados andam, carregam, constroem, ensinam e programam bots; usam menus de construções, servidor de bots, grupos, catapultas, espaçoporto, planejamento e menu de criação do modo Criativo; o mundo inteiro coincide em todos os lados (checksum do mundo completo). Testes automatizados com clientes reais passam com 2 e 4 jogadores, em mundo novo e salvamento avançado (mapa 420x240, aproximadamente 10.800 objetos, 53 bots). Uma sessão Steam real entre dois PCs pela internet funcionou (teste do autor, 2026-10-26). Pendente: testes reais mais amplos (mais jogadores, salvamentos e conexões piores).

## <a id="existing-work"></a>Trabalhos existentes

- Sem multiplayer oficial. Comentário do desenvolvedor (2019/20): multiplayer "isn't something that will happen for a while" (não acontecerá tão cedo) ([playco-opgame.com](https://playco-opgame.com/autonauts/)).
- Nenhum mod cooperativo encontrado antes deste (GitHub, Nexus, Steam Workshop e fóruns por busca na web, 2026-10-20). Apenas pedidos de jogadores: [itch.io 1](https://itch.io/t/175669/pls-add-a-multiplayer-mode), [itch.io 2](https://itch.io/t/161660/multiplayer), [Steam](https://steamcommunity.com/app/979120/discussions/0/1639801448924410169).
- O suporte oficial a mods Lua (MoonSharp) é isolado em sandbox e não intercepta métodos do jogo; não permite implementar rede.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Sem código de rede.** Inteiramente para um jogador, com 195 chamadas a `UnityEngine.Random` e passo de tempo variável; lockstep não é realista. O mod usa autoridade do host: a simulação do convidado fica congelada, espelhando o host.
- **Salvamentos são um documento JSON.** `SaveJSON.Capture` constrói o mundo inteiro em memória; `LoadJSON` o lê por `MyFile.Load`. Entrada = capturar no host, comprimir com gzip, enviar e fazer o carregador do convidado ler da memória (patch em `MyFile.Exists`/`Load` para nome reservado de salvamento).
- **Objetos:** cada objeto tem UID de `ObjectTypeList`; `Savable.Save/Load` fornecem JSON completo por objeto. Esse JSON é o formato das diferenças. Filhos (itens carregados, ninhos de abelhas, construção de uma planta) são salvos dentro do pai.
- **Pontos de concentração da entrada:** `FarmerPlayer.GoToAndAction` (cliques), `BuildingManager.AddBuilding/DestroyBuilding/MoveBuildings` e `GameStateEdit.ConvertDragModels` (edição), `Worker.NewHighScriptTaught` (ensino), `InventoryBar.DragEnd/OnClick` (inventário), `GameStateManager.Start*` (telas de construções).
- **Dados dos gerenciadores fora dos objetos:** missões/pesquisa, tabelas de desbloqueio (`m_ObjectsLocked` e `m_BuildingsLocked`, parcialmente por jogador via insígnias), recursos, hora do dia, biblioteca de scripts, grupos de bots, missões fora do mundo, guarda-roupa global e áreas de planejamento. Cada um é sincronizado como "seção do mundo".
- Armadilhas por versão (registro de UIDs, objetos reutilizados, telas que perdem sua construção quando ela é reconstruída etc.) estão em [NOTES.md](NOTES.md).

## <a id="what-we-changed"></a>O que alteramos

O mod vive em seu próprio repositório; aqui estão a arquitetura e as partes difíceis.

- **Entrada:** captura de estado pelo carregador do próprio jogo; UIDs próprios do convidado vão para uma faixa alta para nunca colidir com os do host.
- **Diferenças:** o host envia JSON dos objetos alterados, UIDs removidos, movimento a 10 Hz, mudanças de terreno e névoa, animações e seções do mundo. A cada 10 s envia resumo (uid, hash), e convidados solicitam novamente os itens divergentes.
- **Aplicação no convidado:** `Savable.Load` no próprio objeto (primeiro remove o registro do UID), verificado por novo salvamento; caso contrário, recria sob `ObjectTypeList.m_Loading = true` para preservar UIDs.
- **Entrada do convidado** vai ao host em mensagens pequenas e é reproduzida pelas mesmas chamadas do jogo; resultados voltam pela sincronização. Cobre cliques, edição com desfazer, ensino, mudanças de inventário, menus, servidor de bots, grupos, mira de catapultas e missões do espaçoporto.
- **Editores compartilhados** (biblioteca de scripts, áreas de planejamento, grupos) enviam a seção inteira após edição local. O host substitui sua cópia e a retransmite. Planejamento e grupos permitem um editor por vez (quem alterar primeiro, até 5 s após a última mudança); a biblioteca combina por script (mesclagem em três vias contra a cópia inicial do autor da mudança).
- **Saída:** o personagem do convidado (posição, mãos, bolsos, melhorias, roupas) é retirado do mundo e guardado no salvamento do host. Retorna ao reconectar, no mesmo lugar ou ao lado do host se o local tiver recebido construção.
- **Bases grandes:** detecção incremental. Objetos móveis são revistos em toda varredura, assim como os alterados ou movidos recentemente; os demais entram em um ciclo de aproximadamente 5 s. Rotação de caminhos é excluída dos hashes porque cada máquina a deduz dos vizinhos.
- **Steam:** ISteamNetworkingMessages e salas só para amigos pelo Steamworks.NET incluído no jogo. `SteamNetworkingMessage_t.Release()` dessa versão tem um bug; o mod chama diretamente a liberação nativa.
- **Verificação de versão** (mod e jogo) com recusa legível, "Host has ended the lobby." quando o host encerra, avisos de entrada/saída e ZIP de relatório de bug com um clique, incluindo o log do host.
- **Interface interna:** hospedar, convidar e encerrar pela pausa; entrar por painel no menu principal; avisos no popup do próprio jogo, construídos com seus prefabs. Criações do modo Criativo feitas pelo convidado são reproduzidas no host.

## <a id="qa"></a>QA

- `test/run.sh "<game dir>" "<BepInEx dir>" <work dir>` no repositório do mod: duas cópias sob Wine + Xvfb com prefixos separados, controladas por bots internos pelo caminho real de entrada (`COOP_TEST=host|client`).
  - `COOP_TRANSPORT=udp` executa os mesmos testes com substituto UDP do enquadramento de mensagens Steam.
  - `COOP_BIG=1` executa o teste de estresse de base grande.
- A suíte verifica:
  - entrada: quantidades de objetos e checksum do mundo completo;
  - edição: construir, arrastar, mover, excluir, desfazer;
  - ensino, travas de edição, renomear, transferências de inventário nos dois sentidos;
  - menus: receitas, pesquisa, guarda-roupa, servidor de bots, grupos, catapulta, espaçoporto, planejamento;
  - velocidade e pausa, seções do mundo;
  - sair/reentrar (local livre ou construído), salvar/recarregar host com personagens armazenados;
  - recusa de versão, "lobby ended", salvamento automático bloqueado no convidado, Save As do convidado carregando seu próprio personagem, relatório de bug.
- Kit Windows (duas ou quatro cópias em um PC, mesmos bots), últimos resultados de 2026-10-26: **116/116** teste completo (mundo novo, 0.13.0); **18/18** em salvamento avançado (0.12.37) (420x240, 10.803 objetos, 53 bots; 1 reconstrução no convidado em 4,5 min); **46/46** quatro jogadores (host + 3 convidados: entrada conjunta, visibilidade e movimento, plantas, verificações do mundo, desconexão e retorno) em mundo novo (0.12.37); **18/18** teste de menus internos (0.13.0) (botões de pausa/menu principal, painel de entrada, avisos, criação no Criativo, Load bloqueado nos convidados; capturas conferidas). Quatro jogadores no salvamento avançado (0.12.37): 46/47 (duplicata ao reconectar descrita em Problemas conhecidos).
- Resultados anteriores Linux/Wine (2026-10-21, mod 0.10.0): **101/101 por TCP, 84/84 pelo substituto UDP, 7/7 no teste de base grande**. Base: aproximadamente 8.000 objetos com 400 bots e 4.000 itens; entrada em aproximadamente 70 s; mundos coincidiram após 90 s de alterações intensas.

## <a id="how-to-play"></a>Como jogar

1. Baixe o ZIP mais recente na [página de versões](https://github.com/Shocklinks/autonauts-coop/releases) e extraia na pasta do jogo, ao lado de `Autonauts.exe` (inclui BepInEx 5.4.23.5).
2. Host: carregue um mundo, pressione Esc e Host Multiplayer (lado direito da pausa); a janela de convite Steam abre. Esc > Invite Friends a reabre; Esc > Stop Hosting encerra a sessão.
3. Convidados: aceitem o convite ou cliquem com botão direito no host no Steam > Join Game. Sem Steam: menu principal > Multiplayer, digite o IP do host (host redireciona TCP 27015).

Cada jogador precisa da própria cópia do jogo e da mesma versão do mod (divergências são recusadas com mensagem). F8 abre a janela do mod: porta, nome, estado e ZIP de relatório de bug.

## <a id="known-issues"></a>Problemas conhecidos

- Beta: só uma sessão Steam entre dois PCs até agora. Grupos maiores, outros salvamentos e conexões ruins precisam de relatos reais.
- Convidados não podem carregar salvamentos conectados (causa falha): o botão Load fica oculto.
- Elementos imóveis (por exemplo, conteúdo de depósitos) podem levar alguns segundos para atualizar nos convidados.
- Áreas de planejamento e grupos de bots são editados por um jogador por vez (alterações de outro são desfeitas com aviso). A biblioteca combina por script.
- Um desbloqueio recebido com o menu de construção aberto só aparece ao reabrir a edição.
- O convidado sofre uma pausa de aproximadamente 200 ms a cada 100 s em salvamento grande (em investigação).
- Logo após reconectar em base movimentada, um item colocado em máquina naquele momento pode duplicar por aproximadamente 3 s, até a autoverificação do convidado removê-lo.
- Insígnias e Autopedia são por jogador.

## <a id="next-steps"></a>Próximos passos

- Reunir relatos do beta (F8 > Save bug report dos dois jogadores).
- Corrigir a pausa periódica do convidado e a duplicata ao reconectar.
- Sessões reais com 3 ou mais jogadores e mapas médios/grandes pela internet.
