# <a id="tmnt-2007-pc"></a>TMNT (2007, PC)

> **Em desenvolvimento, sem estabilidade.** Este é um protótipo experimental em desenvolvimento ativo. Ainda não foi lançado e não está pronto para jogar; espere movimentos ausentes, recursos desativados e falhas ocasionais.

| | |
|---|---|
| Motor | Ubisoft Jade ("Engine v428-42" no log do jogo; scripts de jogabilidade compilados no executável) |
| Versões testadas | PC comercial, `TMNTGame.exe` 1.0.0.188 (compactado com UPX, vestígios de SecuROM), SHA-256 `701d9f00f8c1edf790466f2ecfeb72a64fe7ccdc491f7c370ae11c1942740589`; loja/edição desconhecida |
| Projetos | Modo cooperativo local no sofá por injeção de DLL (privado, em andamento; ainda sem repositório público) |
| Nível de QA | none (ainda sem testes estruturados ou automatizados) |
| Última atualização | 2026-10-25 |

## <a id="where-things-stand"></a>Situação atual

Um segundo jogador consegue controlar outra tartaruga na tela simultaneamente ao jogador 1, em um processo do jogo em um PC com dois controles. Movimento, salto, ambos os ataques, vida, seleção de alvo pelos inimigos, reaparecimento e câmera compartilhada no ponto médio funcionaram em execuções manuais durante o desenvolvimento, não em teste estruturado. O jogador 2 ainda não tem todos os movimentos (salto duplo, combos, esquiva, movimentos que exigem corrida prévia), e os movimentos em equipe ficam desativados enquanto ele está presente. Não lançado.

## <a id="existing-work"></a>Trabalhos existentes

- Nenhum mod cooperativo para a versão PC foi encontrado (GitHub, central de handlers Nucleus Co-op, busca na web; 2026-10-12). Apenas as versões PSP e DS tinham multiplayer.
- [xan1242/UbiTMNTHax](https://github.com/xan1242/UbiTMNTHax): plugin ASI para o mesmo executável (modo janela, pular inicializador, múltiplas instâncias). Não é cooperativo, mas serve de referência para hooks nesta compilação.
- [hogsy/jaded](https://github.com/hogsy/jaded): fork comunitário do código-fonte do motor Jade de 2006; útil para estruturas, mas não carrega dados de TMNT.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

Detalhes e endereços (para a compilação acima) estão em [NOTES.md](NOTES.md).

- Normalmente só uma tartaruga aparece; um irmão surge brevemente para movimentos em equipe (Brother Throw, Super Family Attack). Turtle Swap apenas altera qual objeto tartaruga é o "main actor 0"; os outros objetos continuam vivos.
- O motor tem duas vagas de ator principal (a segunda fica vazia no modo solo) e "portas de E/S" por tartaruga, mas a porta é somente uma chave liga/desliga: todas as tartarugas presentes leem o mesmo objeto compartilhado de entrada.
- A entrada passa pela biblioteca Gear da Ubisoft (DirectInput 8 e XInput 1.3). O jogo combina todos os controles em um estado de entrada; assim, um segundo controle físico também controla o jogador 1.
- O mutex do inicializador impede uma segunda instância; tela dividida com múltiplas instâncias não é um caminho simples.

## <a id="what-we-changed"></a>O que alteramos

Tudo fica em uma DLL injetada (uma DLL hospedeira injetada uma vez e uma DLL do mod recarregável durante a execução). Nenhum arquivo do jogo é alterado.

- **Uma segunda tartaruga:** a própria função de criação de tartarugas posiciona um irmão ocioso junto ao jogador 1, com a porta aberta.
- **Entrada própria:** durante a atualização da tartaruga do jogador 2, as leituras compartilhadas de analógico e ações recebem os valores do controle 2; o movimento é relativo à câmera. O DualSense do jogador 2 é lido diretamente por HID e ocultado da lista DirectInput do jogo (caso contrário, o jogo o escolhe como controle 1 ou o combina à entrada do jogador 1).
- **Inimigos miram no jogador 2:** na atualização da IA inimiga, o ator principal 0 é trocado pelo jogador 2 quando esse inimigo está mais perto dele e restaurado depois.
- **Barra de vida** do jogador 2 (hook D3D9 EndScene no dispositivo real do jogo), vinculada à vida de 0 a 100 da tartaruga.
- **Câmera:** observa o ponto médio horizontal entre as tartarugas; o jogador 2 fica limitado à proximidade do jogador 1 e é trazido de volta se cair num abismo; reaparece automaticamente após morrer.
- **Movimentos em equipe desativados** enquanto o jogador 2 está presente: após um desses movimentos, o jogo transforma o parceiro em um ajudante controlado por script (no código ofuscado), que o faz voar para longe e o marca como ausente.

## <a id="qa"></a>QA

Ainda sem suíte automatizada. Os resultados acima vêm de execuções manuais durante o desenvolvimento, não de um teste. O próximo passo é um script de entrada do controle 2 e um log que compare os estados de movimento dos jogadores 1 e 2 para a mesma entrada (consulte a página de QA automatizado dos guias e o relato de The Two Towers).

## <a id="how-to-play"></a>Como jogar

Não lançado.

## <a id="known-issues"></a>Problemas conhecidos

- Faltam ao jogador 2 movimentos dependentes do histórico de entrada (salto duplo, combos, esquiva, movimentos com corrida prévia).
- Movimentos em equipe ficam desativados quando o jogador 2 está na fase.
- Os irmãos continuam sendo desbloqueados durante a fase, como no jogo base.
- Carregamentos de fase e recargas de checkpoints com o jogador 2 não foram testados; ele pode não sobreviver a essas transições.
- O jogo falhou uma vez quando uma nova compilação do mod foi recarregada durante uma partida; as compilações mudam frequentemente.

## <a id="next-steps"></a>Próximos passos

- Igualar a entrada como em [The Two Towers](../lotr-two-towers/NOTES.md): dar ao jogador 2 uma cópia própria do objeto de entrada (um registro virtual de segundo controle), deixar a leitura nativa do jogo preenchê-la e executar a etapa de controle do jogador 2 com essa cópia substituída temporariamente.
- Teste de reprodução do controle 2 que verifique se o jogador 2 alcança os mesmos estados de movimento do jogador 1.
- Movimentos em equipe usando o jogador 2 como parceiro.
