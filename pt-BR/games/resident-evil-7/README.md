# <a id="resident-evil-7-biohazard-2017"></a>Resident Evil 7 biohazard (2017)

| | |
|---|---|
| Motor | RE Engine (TDB 70) |
| Versões testadas | Steam, app 418370, buildid 22773795 (compilação RT/DX12); REFramework nightly-01433 (d4611ae) com csharp-api |
| Projetos | [coop-re7](https://github.com/xXCroissantXx/coop-re7) (entrada no diretório "Resident Evil 7 biohazard") |
| Nível de QA | none (somente testes com bot em um PC; dois jogadores reais não foram testados juntos) |
| Última atualização | 2026-10-29 |

## <a id="where-things-stand"></a>Situação atual

Ainda não é possível jogar a história juntos. Cada jogador joga em seu próprio mundo e vê o outro como um Ethan de corpo inteiro que caminha, corre devagar, se agacha, anda de lado, recua e olha ao redor como o outro jogador, por retransmissão Steam. Os jogadores não atravessam um ao outro. A conexão é feita por um painel dentro do jogo; o representante é reconstruído após carregar salvamentos e ocultado quando os dados do outro param. Inimigos, itens, portas e progresso da história não são compartilhados; salvar fica bloqueado durante a execução do mod.

## <a id="existing-work"></a>Trabalhos existentes

- Nenhum mod cooperativo de RE7 encontrado (GitHub, Nexus, ModDB e busca geral na web, 2026-10-29).
- As opções de terceira pessoa de RE7 são um script de câmera Cheat Engine (mod Nexus RE7 12) e "Third Person Full Model Placeholders". Eles apontaram modelos completos de Ethan, Mia, Zoe e Clancy já incluídos nos arquivos do jogo.
- Mesmo motor: mod multiplayer de RE4 (2023) (claybtv, beta fechado, relatos de picos de atraso e inimigos dessincronizados) e RE2 (2019) Local Couch Co-op (somente local). Nenhum tem código de rede reutilizável.
- EMV Engine, de alphaZomega (Lua para REFramework), foi a referência mais útil para criar atores e animações.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Sem código de rede**: jogo de um jogador. REFramework permite a Lua e C# (plugins-fonte Roslyn em `reframework/plugins/source`, recarregados em execução) acessar o banco de tipos do RE Engine.
- **Jogador**: `app.ObjectManager.PlayerObj` (por exemplo, `Pl0000_Chapter1`). O estado de movimento fica em `app.PlayerMovement` (`get_isCrouch`, `get_isWalk` e campos `WalkSpeed`/`JogSpeed`/`CrouchMoveSpeed`). `app.MovementController.warp(vec3, quat)` move o jogador sem que o controlador de personagem desfaça a mudança.
- **Ethan tem corpo inteiro**, só não aparece na tela: o objeto do jogador contém `ShadowBody`, `ShadowHead` (esqueleto facial completo), `ShadowHandL/R` e `ShadowLowerBody` com **DrawDefault=false, DrawShadowCast=true**. Seu banco de movimentos é `Animation/Player/pl0000/pl0000.motbank` (29 bancos, aproximadamente 5.500 clipes: Walk/Jog/WalkCrouch em F/B/L/R, giros, repousos).
- **Salvamentos**: `app.SaveDataManager`. Toda gravação passa por poucos pontos de entrada `save…Request` (`saveFileAutoRequest`, `saveFileMenuRequest`, `saveFileSystemDataRequest`, `saveFileExpansionDataRequest`, `saveFileBirthdayDataRequest`, `saveFileUniqueDataRequest`). Ignorá-los bloqueia o salvamento de forma limpa.
- **Steam**: `steam_api64.dll` do jogo exporta a API plana moderna (`SteamNetworkingMessages_SteamAPI_v002` e afins); um plugin pode usar a retransmissão Valve pela própria sessão Steam do jogo.

## <a id="what-we-changed"></a>O que alteramos

- **Segundo corpo.** GameObjects construídos em execução (`create` + `createComponent(via.render.Mesh)`) nunca são renderizados em RE7, mesmo com recursos válidos e todos os indicadores de desenho ativados. Uma instância de prefab é renderizada: `app.vr.VrManager.DummyPlayerPrefab` (`Prefab/System/VrDummyPlayer.pfb`) instanciada e depois `set_DrawSelf(true)`. Um substituto por malha Shadow\*: o corpo é a raiz e os demais são vinculados a ele por `SameJointsConstraint`.
- **Malhas de sombra não animam.** RE Engine ignora esqueletos que considera invisíveis. Forçar `DrawDefault=true` em cada parte corrigiu um representante que só deslizava.
- **Animação.** Forneça ao corpo `MotionBankAsset` + `JointMap` do jogador, chame `setupMotionBank()`, adicione uma camada **construída** (`create_instance("via.motion.TreeLayer")` + `.ctor`, `setLayerCount(1)`, `setLayer(0)`), chame `set_Resource(nil)` e depois `changeMotion(bank, id, 0, blend, 2, 0)`. Sem `.ctor`, nenhum clipe é associado. Desativar `app.MotionManager` do substituto congela a animação; mantenha-o ativo.
- **`pl0000_Hands_Stand_Loop` trava a camada.** Nunca é associado e, como primeiro clipe, deixa a pose T permanentemente. O mod o bloqueia e usa `StandDamage_Loop`. Um monitor reconstrói a camada ou o representante inteiro quando um clipe não é associado ou o quadro deixa de avançar.
- **Olhar da cabeça.** `Motion.setLocalRotation` em um hook `UpdateMotion` é aceito, mas sobrescrito antes da renderização. Escrever `via.Joint.set_LocalRotation` antes de `PrepareRendering`, com base em `getCalculatedLocalRotation`, funciona sem congelar ou acumular.
- **Rede.** Plugin C# (UDP para testes, retransmissão Steam para jogar), pacote de 64 bytes com posição, rotação, indicadores de postura e ângulos horizontal/vertical do olhar. O receptor interpola com atraso de 0,15 s, extrapola até 0,1 s para pacotes atrasados, escolhe Walk/Jog/Crouch × F/B/L/R pela velocidade relativa à orientação (usando velocidade adiantada do buffer), suaviza giros e mistura clipes.
- **Carregamentos, mortes e mudanças de área.** Recriam `PlayerObj` e descarregam a pasta em que o representante vive. Um monitor compara o endereço do jogador a cada 0,5 s e repete toda a criação quando ele muda ou os objetos do representante param de responder. Um carregamento passa primeiro por um jogador temporário da cena de carregamento (sem malhas de Ethan); o representante só é criado para um jogador chamado `Pl0000…`.
- **Desconexões.** O representante é ocultado quando a amostra mais recente tem mais de 2 s e reaparece quando os dados retornam.
- **Conexão.** Painel interno mostra seu SteamID (com Copy) e recebe o do amigo. O plugin lê um arquivo de comando de uma linha, alterna entre Steam e bot em tempo real e salva o identificador do amigo para a próxima execução.

## <a id="qa"></a>QA

- Parceiro bot: modo `"bot"` de CoopNet caminha em círculo ao redor do jogador local, alternando postura (caminhada, corrida leve, agachamento) e direção (frente, direita, trás, esquerda) com latência de 80 ms, jitter de ±30 ms e perda de 5% pelo caminho normal de recebimento. O menu mostra o estado real do bot (`botExpect`) ao lado da escolha do representante.
- Resultado de 2026-10-29: postura e direção coincidem nas 12 combinações; olhar da cabeça e afastamento por colisão funcionam. Conferido visualmente e nos logs em um PC.
- Teste de recarga (menu "Tests"): carrega o salvamento da sessão com `SaveDataManager.loadFileAutoRequest` (o mesmo que Continue), 10 rodadas. Resultado de 2026-10-29: representante reconstruído e rede funcionando em 10/10 rodadas, com arquivos de salvamento idênticos byte a byte depois. A animação retornava 7-8 s após o jogador real aparecer. Cinco rodadas atingiram o limite de 90 s do próprio teste, pois carregar o Capítulo 1 leva aproximadamente 80 s; agora o limite é 180 s e o teste informa separadamente tempo de carregamento e reconstrução.
- Caminho Steam: retorno para si mesmo por `ISteamNetworkingMessages` (`relayStatus=100`, sem perda). Duas contas Steam não foram testadas juntas.

## <a id="how-to-play"></a>Como jogar

Os dois jogadores precisam da compilação Steam, REFramework nightly-01433 (somente `dinput8.dll`) com csharp-api e runtime .NET 10. Copie a pasta `reframework` do mod para uma cópia do jogo e carregue o Capítulo 1. No menu REFramework (Insert → Script Generated UI → coop_dummy → Connect), copie seu SteamID para o outro jogador, cole o dele e clique em **Connect to friend**. O representante é criado automaticamente. Instruções completas no [README de coop-re7](https://github.com/xXCroissantXx/coop-re7).

## <a id="known-issues"></a>Problemas conhecidos

- Sem sincronização do mundo: inimigos, itens, portas e história são separados por jogador.
- Salvar fica bloqueado durante a execução do mod.
- Pequenas irregularidades residuais de movimento com jitter simulado intenso.
- Testado somente na área inicial do Capítulo 1.
- Sem representante ao jogar com personagem diferente de Ethan (por exemplo, trechos de Mia).
- O rosto não anima.

## <a id="next-steps"></a>Próximos passos

1. Salvamento opcional com backups automáticos.
2. Teste com dois jogadores em dois PCs (QA ainda é `none`).
3. Indicador de conexão na tela, fora do menu REFramework.
4. Sincronização de mundo com autoridade do host: história e área, portas, itens e depois inimigos.
