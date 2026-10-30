# <a id="poppy-playtime-2021"></a>Poppy Playtime (2021)

| | |
|---|---|
| Motor | Unreal Engine 4.27.2 |
| Versões testadas | Steam, buildid 21905565 (UE 4.27.2, Windows) |
| Projetos | [PoppyCoop](https://github.com/romannazarov057-spec/PoppyCoop) (criado do zero, em desenvolvimento) |
| Nível de QA | automated (somente sincronização de movimento; sem campanha completa) |
| Última atualização | 2026-10-19 |

## <a id="where-things-stand"></a>Situação atual

Ainda não é possível jogar a história juntos. O que existe é uma base: dois clientes reais, cada um vendo o outro como um representante com formato de jogador na posição correta, com movimento nos dois sentidos por um retransmissor. Os elementos cooperativos reais do Capítulo 1 — portas, GrabPack, objetivos, Huggy — não são sincronizados; portanto, uma dupla não consegue avançar da primeira sala como dupla.

## <a id="existing-work"></a>Trabalhos existentes

- **Nada jogável.** Existiu um mod multiplayer de fã, excluído pelo autor (o desenvolvedor confirmou no Reddit); nenhuma cópia alternativa encontrada. [Discussão no Reddit](https://www.reddit.com/r/PoppyPlaytime/comments/uut6zj/anybody_have_a_poppy_playtime_multiplayer_mod/).
- **PoppyCoop** - este projeto. Mod Lua para UE4SS + retransmissor Python, MIT.
- Dois indícios de que já houve multiplayer internamente: a compilação Steam inclui o SDK de voz VoxeX (`vivoxsdk_x64.dll`, `ortp_x64.dll`) em `Binaries\Win64`, e compilações do Capítulo 2 contêm um minijogo multiplayer não utilizado ([TCRF](https://tcrf.net/Poppy_Playtime:_Chapter_2/Multiplayer)).
- O Steam lista o jogo somente como um jogador (sem Remote Play Together, LAN ou categoria cooperativa); portanto, nada está disponível de fábrica.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Motor / mods:** UE 4.27.2, distribuído sem conteúdo do editor, mas inteiramente baseado em scripts. [UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) v3.0.1 carrega mods Lua no processo, expõe os objetos do jogo e o console e não exige compilador.
- **Código de rede:** o Capítulo 1 não tem rede própria. Tudo é local ao cliente e para um jogador; é preciso adicionar o modo cooperativo por cima: troca de estado com autoridade do host entre dois mods.
- **Fases:** o capítulo inteiro é um mapa, `/Game/Levels/PP_FinalLevel`. Um teste pode entrar nele a partir do menu com o comando de console `open`, evitando automatizar cliques nos menus.
- **Criação de atores:** a reimplementação de `UWorld::SpawnActor` do próprio UE4SS falha nesse motor (issue UE4SS-RE/RE-UE4SS#527, ainda aberta na v3.0.1). O comando de console `summon` cria atores com segurança pelo código do próprio jogo; é assim que o representante é criado.
- **O esqueleto do jogador** é uma malha de 7 ossos (`/Game/Player/Rig/Plegs_rig`) com blueprint de animação *procedural* (`Plegs_rig_AnimBP`) que faz conversão para o pawn proprietário. Ele não pode ser aplicado a um ator independente. O mesmo esqueleto inclui a sequência simples `legs_Walk_anim`, que pode.
- **Salvamentos:** arquivos UE `SaveGame` padrão em `%LOCALAPPDATA%\Poppy_Playtime\Saved\SaveGames` (`SG_Audio.sav`, `SG_Graphics.sav`); o progresso do capítulo fica na fase/GameInstance, não em um salvamento que o mod precise alterar por enquanto.

## <a id="what-we-changed"></a>O que alteramos

1. **Representante invisível** → era criado com escala 1.0, mas o componente da malha do jogador usa 14.37; por isso aparecia com poucos pixels de largura. Correção: copiar `K2_GetComponentScale()` da malha do jogador. Teste: `diag` exibe lado a lado malha, material do slot 0, escala e osso de referência do jogador e do representante; os valores coincidem.
2. **Representante em pose T / sem animação** → o AnimBP do jogador não pode ser aplicado (veja acima). Correção: `SetAnimationMode(AnimationSingleNode)` + `SetAnimation(legs_Walk_anim)` + `Play(true)`. Teste: `animstat` informa `playing=true` e posição que avança no ciclo de 2,0 s.
3. **O jogo encerra após alguns minutos ou o ciclo do mod para silenciosamente** → chamadas a objetos do motor eram feitas pela própria thread do mod. Correção: toda alteração passa por `ExecuteInGameThread`. Teste: 4 minutos posicionando o representante continuamente, 0 erros Lua, nenhum relatório de falha (fora da thread correta, o mesmo teste encerrou duas vezes sem registrar nada).
4. **Sem transporte** → o mod só tem entrada/saída de arquivos; escreve seu estado e lê o do outro jogador. Um retransmissor Python conecta isso a outra máquina. Teste: `tests/test-relay.ps1`, dois clientes reais e dois retransmissores, nos dois sentidos, com posições distintas nos dois logs.

## <a id="qa"></a>QA

- `tests/test-relay.ps1` inicia duas cópias do jogo com o mod instalado, limpa os logs, executa dois retransmissores UDP, espera ambas entrarem no Capítulo 1 e verifica nos logs a posição do outro jogador e a ausência de relatórios de falha. Último resultado: **aprovado**, 2026-10-18; ambos os logs mostram um representante na posição do outro jogador, 0 falhas, e salvamentos e configurações foram restaurados com bytes idênticos ao final.
- Não cobertos: campanha completa, qualquer interação de jogo, trecho de mensagens pelo Steam.

## <a id="how-to-play"></a>Como jogar

Ainda não está pronto para jogadores. Quando estiver: instale UE4SS 3.0.1, coloque `PoppyCoop` em `Mods\`, adicione `PoppyCoop : 1` a `Mods\mods.txt`, execute `relay/cooprelay.py` nas duas máquinas (transporte Steam, uma com `--role host`, outra com `--role client --lobby <id>`) e jogue. As instruções completas estão no [README do PoppyCoop](https://github.com/romannazarov057-spec/PoppyCoop#install).

## <a id="known-issues"></a>Problemas conhecidos

- Somente o movimento é sincronizado. Portas, objetivos, interações e inimigos não são; não é possível concluir o capítulo em modo cooperativo.
- O representante executa um ciclo de caminhada fixo, sem usar a velocidade real do outro jogador; sua orientação horizontal é aproximada.
- O transporte Steam só foi testado até criar e entrar em uma sala. Ninguém trocou mensagens pelo Steam ainda.
- O mod cria um representante local mesmo em uma sessão de um jogador.

## <a id="next-steps"></a>Próximos passos

- Sincronizar o estado do Capítulo 1: classe de objetivos/GameInstance e classes de portas e objetos interativos, para permitir que a dupla avance de fato.
- Controlar a animação pela velocidade sincronizada e a orientação pela direção do movimento.
- Criar uma interface de hospedagem/entrada com um clique para que jogadores não precisem da linha de comando.
- Testar o trecho de mensagens Steam quando houver uma segunda conta Steam disponível.

Notas aprofundadas, com medições por trás de cada afirmação e tentativas sem resultado (sem leitura de ossos utilizável nesta compilação; testes por diferença de tela têm ruído demais neste jogo), estão em [NOTES.md](NOTES.md).
