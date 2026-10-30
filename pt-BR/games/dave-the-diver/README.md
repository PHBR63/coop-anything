# <a id="dave-the-diver-2023"></a>Dave the Diver (2023)

| | |
|---|---|
| Motor | Unity 6000.0.52f1, IL2CPP (BepInEx 6.0.0-be.788 + HarmonyX) |
| Versões testadas | Steam (app 1868140), Windows. `GameAssembly.dll` SHA-256 `8544e01549c9c9329c2c18283f7e35b652b174f59834cfc0279cf8732637be59`, `DaveTheDiver.exe` SHA-256 `d5e61b65ba86c35f92c2fcf749b62c02f2a7fe1b6bd13b0ff8d6a1d3ea2976c3` |
| Projetos | [Daves the Divers](https://github.com/masonan777/Daves-the-Diver-Coop-Mod) (cooperativo local), [Coop-Divers](https://github.com/S1ii/Coop-Divers) (on-line) |
| Nível de QA | automated (agarrões de criaturas nos mergulhos); o restante foi testado manualmente |
| Última atualização | 2026-10-19 |

## <a id="where-things-stand"></a>Situação atual

Duas pessoas já podem mergulhar juntas em um PC. O jogador 2 é um segundo Dave, roxo, controlado pelo lado direito do teclado ou por um controle Xbox, com oxigênio, HUD e equipamento próprios. O sushi bar tem um segundo Dave de restaurante, capaz de servir, limpar e jogar os minijogos. Cenas da história, fazenda e outras atividades secundárias continuam para um jogador.

## <a id="existing-work"></a>Trabalhos existentes

- **[Coop-Divers / DaveTheDiverMP](https://github.com/S1ii/Coop-Divers)** (MIT, último commit em 2026-07). Modo cooperativo on-line com autoridade do host por UDP direto. O README lista peixes, itens coletáveis, chefes, progresso da história e sushi bar sincronizados. Sem versões distribuídas no GitHub. Foi a origem deste projeto, mas **Daves the Divers não compartilha código com ele**.
- **[Daves the Divers](https://github.com/masonan777/Daves-the-Diver-Coop-Mod)** (MIT, 2026-10). Modo cooperativo na mesma tela, em uma única instância. Este relato trata desse projeto.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Sem código de rede, um único jogador em todo lugar.**
  - O código de jogabilidade encontra o jogador por um campo singleton: `InGameManager.playerCharacter`, equivalente a `Singleton.Instance + 0xA8` no código nativo.
  - O código do restaurante faz o mesmo por `SushiBarStaffManagerImpl.m_Dave`.
  - Agarrões, mordidas, barra de pressionar botões repetidamente, atualizações do HUD, câmera e muitos eventos de animação atuam sobre esse único campo.
- **Entradas:**
  - Dave lê os controles em `PlayerCharacter.OnDirectHandler(input)` (`StaffDave.OnDirectHandler` no restaurante), por meio de `InputSystemWrapper` do jogo. Cada mapa de entrada (`Dave`, `InGame`, `QTE`, `MiniGame` .) tem seu próprio manipulador direto.
  - Os minijogos assumem as entradas, então o mapa Dave deixa de receber ações.
- **Agarrões de criaturas** estão espalhados por várias partes: executores de habilidades (`QTEReadyToEnterSkillRunner`, `BiteHoldSkillRunner`, `OpenQTEUISkillRunner`), habilidade `DR.AI.Biteable` e eventos de animação das criaturas (`AniClipEvents.OpenQTEUI`, `PlayDaveAnimation`, `DoDamageEvent`). Todos miram o jogador único.
- **Leitura do código:**
  - Il2CppInterop (`interop/` do BepInEx) fornece as assinaturas.
  - Para os corpos dos métodos, execute Cpp2IL `2022.1.0-pre-release.21` com `--output-as diffable-cs` para organização e offsets dos campos (cerca de 16 s) e `--output-as isil` para os corpos (cerca de 1 min, 800 MB).
  - Depois nomeie os destinos das chamadas com um mapa de RVA. [tools/annotate_isil.py](https://github.com/masonan777/Daves-the-Diver-Coop-Mod/blob/main/tools/annotate_isil.py), no repositório do mod, faz isso.

## <a id="what-we-changed"></a>O que alteramos

A técnica principal é **a vez do jogador 2**. O jogador 2 é um clone em tempo de execução de `PlayerCharacter` do jogador 1. Quando o jogo precisa executar código para o jogador 2, o mod faz `InGameManager.playerCharacter` apontar para ele, chama o método do próprio jogo e restaura o apontador. Isso reutiliza o código de mordidas, agarrões, barra de repetição de botões, itens auxiliares e HUD, em vez de reescrevê-lo. O restante é o estado compartilhado do clone, separado por jogador:

| Bug | Causa raiz | Correção |
|---|---|---|
| A mira por mouse do jogador 1 congelava após a entrada do jogador 2 | Cada ação de entrada tem um único espaço de callback, e o clone sobrescrevia o do jogador 1 | Capturar todos os callbacks de ação antes de clonar e restaurá-los (`ActionCallbacks.cs`) |
| As teclas do jogador 2 também moviam o jogador 1 | Ambos liam o mesmo teclado | As teclas do jogador 2 são lidas por Win32 (`GetAsyncKeyState`) ou XInput. Um teclado virtual que contém apenas as teclas do jogador 1 pode substituir o real (`KeyboardFilter.cs`) |
| A faca do jogador 2 funcionava uma vez | Um recurso compartilhado de comando de ataque corpo a corpo nunca recebia a redefinição do jogador 2 | Dar ao jogador 2 suas próprias cópias dos comandos (`OwnCommands.cs`) |
| Um agarrão de tubarão no jogador 2 congelava o jogador 1 e ocultava o HUD | As sequências de agarrão só funcionam no jogador único | Ignorar o agarrão original no jogador 2 e executar uma imobilização do lado do mod com cópia da barra de repetição de botões (`P2Grab.cs`, `P2MashUI.cs`); o agarrão do sawtooth fica desligado para ambos os mergulhadores |
| Whitetip ficava preso na animação de investida após o jogador 2 escapar | O resultado da barra envia ao peixe `SetTrigger(UserQTESucces0 / UserQTEFail0)` antes de `BiteSkillEnd`; o mod só chamava `BiteSkillEnd` | Enviar o mesmo gatilho e então encerrar a mordida durante a vez do jogador 2 |
| O jogador 1 entrava em pânico quando o jogador 2 era agarrado | O evento de animação `PlayDaveAnimation` inicia a animação de QTE de combate no jogador único | Executá-lo durante a vez do jogador 2 quando a criatura estiver realmente nele |
| Um tubarão-tigre segurando o jogador 2 também agarrava o jogador 1 | Nada impedia um segundo agarrão | Ignorar agarrões no jogador 1 pela criatura que segura o jogador 2 |
| O jogador 1 ficava travado enquanto o jogador 2 jogava um minijogo de sushi | O minijogo controla as entradas; o Dave do jogador 1 só as recebe pelo jogo | O mod controla diretamente o Dave do jogador 1 pelas suas próprias teclas e fornece ao jogador 2 de teclado um controle virtual para o minijogo |

Há mais arquivos em `src/` do repositório, e cada um começa explicando o problema que resolve.

## <a id="qa"></a>QA

- **Bot de testes:** um bot interno (`CoopTest.cs`, seguindo [automated-qa.md](../../playbook/automated-qa.md)). Defina `[Test] AutoRun = true` e inicie o jogo. Ele passa por título -> Continue -> mergulho normal, adiciona o jogador 2 e, para cada criatura de `Saw,Whitetip,Tiger_Shark` e cada mergulhador, cria a criatura e a faz atacar.
- **O que verifica:**
  - O mergulhador correto é atingido ou imobilizado.
  - O outro mergulhador nunca fica travado.
  - Nenhum mergulhador continua travado e o HUD não permanece oculto 4 s após a saída da criatura.
- **Execução de mutação:** o bot repete a suíte com as regras de agarrão do mod desligadas; essa execução **precisa falhar**. Isso comprova que os testes detectam os bugs.
- **Resultados:** `BepInEx\coop_tests.log`.
- **Último resultado (2026-10-19):** execução normal PASS, 6 de 6. Execução de mutação FAIL, conforme exigido: 5 aprovados, 1 reprovado ("P2 still locked 4 s after the creature left").
- **Não cobertos pelo bot:** o sushi bar e as correções de agarrões feitas após essa execução (agarrão duplo do tubarão-tigre, animação do sawtooth). Foram testados apenas manualmente ou ainda não foram testados.

## <a id="how-to-play"></a>Como jogar

Instale BepInEx 6 IL2CPP (`6.0.0-be.788`), inicie o jogo uma vez e compile o mod ou coloque `DaveTheDiverLocalCoop.dll` em `BepInEx\plugins\DaveTheDiverLocalCoop\`. Dentro do jogo, F9 (ou LB + RB no controle) adiciona o jogador 2. O [README do mod](https://github.com/masonan777/Daves-the-Diver-Coop-Mod#readme) contém os controles.

## <a id="known-issues"></a>Problemas conhecidos

- Às vezes o jogador 2 pisca como se fosse atingido quando apenas o jogador 1 foi atacado (sawtooth). O mod registra cada ocorrência e sua causa para investigar.
- Só uma tela de minijogo ou conversa pode estar aberta por vez.
- Cenas da história, fazenda, chefes e outras atividades secundárias são para um jogador ou não foram testados.

## <a id="next-steps"></a>Próximos passos

- Ler os registros de piscadas e impedir a piscada indevida do jogador 2.
- Ampliar o bot de testes para o sushi bar: servir, limpar e minijogos com os dois jogadores.
- Experimentar a abordagem da vez do jogador 2 nas lutas contra chefes.
