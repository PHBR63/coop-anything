# <a id="crime-scene-cleaner-2024"></a>Crime Scene Cleaner (2024)

| | |
|---|---|
| Motor | Unity 2021.3.45f2, IL2CPP, URP |
| Versões testadas | Compilação Steam 26046462 |
| Projetos | [Crime Scene Cleaner Co-op](https://github.com/gogoigor51-tech/crime-scene-cleaner-coop) (entrada "Crime Scene Cleaner Co-op" no diretório) |
| Nível de QA | automated (mais dois jogadores pelos capítulos 1-6) |
| Última atualização | 2026-10-27 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores podem jogar a história juntos pelo Steam: o cliente acompanha o host em cada trabalho, e quase toda a limpeza, evidências, corpos, móveis e mecanismos das fases são compartilhados, com cada jogador mantendo seu próprio salvamento, relatório, dinheiro e habilidades. Dois jogadores concluíram os capítulos 1-6 na versão 0.4.1; as correções da 0.4.2 foram conferidas em um trabalho e pelas suítes de bots. Não foram testados 3-4 jogadores, modo Nightmare nem os últimos capítulos.

## <a id="existing-work"></a>Trabalhos existentes

- [Crime Scene Cleaner Co-op](https://github.com/gogoigor51-tech/crime-scene-cleaner-coop), 0.4.2, 2026-10: este relato técnico. Criado do zero.
- [coop-anything#176](https://github.com/cranebeaker/coop-anything/pull/176), de KolesovD (PR aberta, 2026-10): relato de protótipo e entrada do diretório para o mesmo jogo. Altera este mesmo arquivo; os dois relatos devem ser combinados quando um deles for incorporado.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- Exclusivamente para um jogador, sem código de rede. Steamworks está presente (`steam_api64`), então o mod controla diretamente a API plana do Steam (ISteamFriends v018, ISteamNetworkingMessages v002): presença enriquecida como diretório de hosts, sem salas.
- BepInEx 6 **be.791** (pre.2 falha com metadados v31). Dumps ISIL do Cpp2IL resolveram a maioria das dúvidas: muitas chamadas do jogo passam por UnityEvents, então frequentemente não há chamador direto para responder "quem chama isto".
- Objetos: `GrabableItemController` (itens), `BodyRagdollController` (corpos), `Taint`/`CleanableDecal` (manchas), `GarbageItem` (van), mais dezenas de tipos de mecanismos das fases. Objetivos são missões do PixelCrushers Dialogue System; contadores (`IncrementEvent`, `BodyQuest`) mantêm seus números em variáveis Lua e somam ao valor lido.
- Salvamentos: `SaveSystem.StartGame(slot)` inicia um *jogo novo* (apaga a vaga); o carregamento usa `SaveSystem.LoadSlot`.
- Trabalhos são cenas; o ponto central é o apartamento. Um bot de censo que carrega todos os trabalhos lista 510 tipos de componentes em 17 cenas (`tools/run-census.ps1`), usado para localizar o que ainda precisava ser compartilhado.

## <a id="what-we-changed"></a>O que alteramos

O `NOTES.md` do repositório do mod contém o registro completo. As decisões mais importantes:

- **Identidade:** cada objeto compartilhado é localizado pelo caminho na hierarquia (e posição inicial para itens), organizado em tabelas. A chave da cena considera somente a tabela de itens + corpos; todas as outras tabelas têm sua própria impressão digital, trocada entre jogadores. Uma tabela divergente (dois salvamentos ligeiramente diferentes, por exemplo no trabalho Villa) é desativada isoladamente, em vez de desativar o trabalho inteiro. Antes da 0.4.2, uma única tabela diferente interrompia toda a sincronização, enquanto o rótulo no canto ainda dizia "2 players".
- **Responsabilidade:** itens e corpos pertencem a quem os segura (épocas, desempate pelo host) e voltam ao host em repouso. Corpos exigiram definir "repouso" como adormecido *e* sem movimento e manter ossos acordados por alguns segundos após um arremesso: ossos colocados para dormir em modo cinemático informavam repouso no ar; transferir um corpo nesse momento o congelava no ar nas duas telas.
- **Eventos do mundo:** eventos de estado pelo host (o mais recente por chave, repetido para quem entra depois) para portas, gavetas, elevadores, manchas, evidências, lixo etc.; lista permitida de chamadas `Type.Method` com argumentos simples, repetidas no mesmo objeto para mecanismos da fase (58 entradas, a partir do censo). IL2CPP unifica corpos de métodos idênticos, então um patch no método de um tipo também dispara em outros: cada repetição primeiro converte ao tipo esperado.
- **Objetivos:** somente indicadores, texto, objetivos adicionados durante o trabalho, objetos de história e reinícios passam entre jogadores; números nunca passam. Combinar contagens fez um corpo contar como 2/2 (BodyQuest soma 1 ao valor Lua lido); combinar a porcentagem de sangue fez o jogo do cliente remover sozinho o sangue restante.
- **Contagens duplas:** após repetir uma coleta da van, o jogo chama `GarbageItem.CollectAndDestroy` novamente; agora o mesmo item da van é coletado uma só vez.
- **O outro jogador:** figura com esqueleto e malha gerada proceduralmente, com a ferramenta equipada copiada do prefab do jogo (usa ferramenta do mesmo tipo quando a outra máquina não possui um modelo melhorado), além de corpo carregado no ombro.

## <a id="qa"></a>QA

- `tools/run-pair.ps1 -Test <name>` inicia duas cópias em um PC (pequenas, sem som, no segundo monitor); bots conectam por UDP no localhost, avançam em lockstep e geram dumps de estado; `tools/<name>_report.py` compara ambos os lados. Suítes: items, stains, bodies, doors, trash, world2 (mecanismos, móveis, objetos de história, indicadores de objetivos, relatórios F9), jobs, laptop, cctv, figure. Uma execução com mutação (`-Mutant table-differ`) comprova que uma tabela diferente não interrompe mais o trabalho. `GATES.md` no repositório do mod vincula cada verificação a um comando.
- Último resultado (2026-10-27, 0.4.2): world2 20/20, bodies 13/13, stains 14/14, jobs 15/15, laptop 9/9, cctv 3/3, world2 com mutação 20/20; testes do núcleo passam.
- Dois jogadores pelo Steam: capítulos 1-6 na 0.4.1; trabalho Villa na 0.4.2.

## <a id="how-to-play"></a>Como jogar

Baixe o ZIP da versão no repositório do mod, extraia na pasta do jogo nos dois PCs (mesma versão do mod) e faça backup de `CrimeCleaner_Data\Saves`. Menu principal → КООПЕРАТИВ (Co-op): o host escolhe Host e uma vaga; o amigo escolhe Join, uma vaga e o host. F8 exibe estado e ping; F9 salva um relatório de bug para ambos.

## <a id="known-issues"></a>Problemas conhecidos

- Cada jogador precisa excluir as gravações de CCTV; a invasão do sistema em si é compartilhada.
- Os máximos dos objetivos podem diferir entre jogadores (o jogo aumenta o máximo de móveis quando uma peça já posicionada é movida e recolocada).
- Uma ferramenta melhorada pode aparecer como básica na tela do outro jogador.
- O rádio do Spa e o reinício do trabalho são compartilhados no código, mas não foram conferidos por jogadores.
- Após acelerar a cena de introdução, a caixa de pizza pode ficar suspensa ao lado do jogador no apartamento.

## <a id="next-steps"></a>Próximos passos

- Gravações de CCTV: só existem após abrir a pasta do notebook na interface; compartilhar a exclusão no nível do apresentador (`HackableComputerPresenter.HandleFileDelete`) e testar com bot que controle a interface.
- 3-4 jogadores, modo Nightmare, últimos capítulos.
- Sujar novamente (respingos da lavadora de alta pressão em manchas limpas) não é compartilhado; as manchas só sincronizam no sentido da limpeza.
