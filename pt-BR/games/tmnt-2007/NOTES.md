# <a id="tmnt-2007-pc-co-op-notes"></a>TMNT (2007, PC): notas sobre modo cooperativo

Os endereços se referem a `TMNTGame.exe` 1.0.0.188 (SHA-256 em [README.md](README.md)), base da imagem 0x400000, lidos da imagem descompactada em memória (OEP 0x0076B59F). O executável foi compactado com UPX e teve o cabeçalho UPX removido (`upx -d` recusa) e contém vestígios de SecuROM; os executáveis têm o indicador de compatibilidade RUNASADMIN, então ferramentas de memória precisam de privilégios de administrador.

## <a id="observed"></a>Observado

- Log: "Engine v428-42", "Opening PC BF"; arquivo de dados `turtles.bf`. Mensagens de scripts (`Switch_SwitchMainActor`, `Coop_SetPartner`, `Buttons_RegisterPad`, `Turtle_*`) estão compiladas no executável (Jade AI2C).
- `TMNTcontrol.INI`: um conjunto `[GamePad]`/`[Keyboard]`/`[Mouse]`, sem índice de jogador; inclui ações de depuração (`GHOSTMODE`, `KILLTHEMALL`, `SPECIALLOADMAPMENU`). `COOP=` é o golpe em equipe, não um segundo jogador. `DevicesMapping.ini`: mapeamentos DirectInput de botões por modelo de controle, sem vagas de jogadores.
- Atores principais: `AI_MainActorGet` 0x004B4A50; ator principal 0 em 0x014775F0, ator principal 1 em 0x014775F4 (nulo no modo solo). Escrever ator principal 1 := tartaruga ociosa: sem falha, nada visível.
- Identificador da tartaruga: obj → [+0x18] → [+4] → [+0x48] → +0x6A4 (1-4). Estrutura de IA da tartaruga: porta de E/S +0x708 (0 controlada, -1 ociosa), estado de presença +0x938 (2 ativa, 0 ausente), saúde 0-100.
- `Switch_SwitchMainActor` 0x00575AE0 move apenas o ator principal 0 e a porta; a tartaruga anterior continua viva.
- `Turtle_Spawn` 0x005C1F70 (identificador, ponto de surgimento, deslocamento, porta): teletransporta e torna presente; porta definida por 0x004E5190. Fazer um irmão ocioso surgir com porta 0 coloca uma segunda tartaruga na tela.
- Definir a porta de uma tartaruga como 1 não impede o controle/teclado de movê-la: a porta é uma condição de habilitação, não um índice de controle. As entradas vêm do objeto de E/S compartilhado 0x014F2F60 (leituras por 0x00565D20, em código protegido/virtualizado).
- Gerenciador de controles 0x0063DD40, quatro objetos XInput em mgr+0x30..+0x3C; a leitura `GamePadX360` ~0x00646B30 chama `XInputGetState([this+0xEC], this+0xD8)`. Analógico esquerdo processado em 0x00824BE4/0x00824BE8. Os botões de golpes passam pelo caminho DirectInput.
- Identificadores vistos no caminho de ações: 1 pulo, 8 desarmado, 6 armado, 4 golpe em equipe. Esquiva não passa por esse caminho.
- O jogo consulta cada botão de quatro maneiras (pressionado agora, mantido, uma variante de mantido, duração). Responder somente "pressionado agora" a partir do controle do jogador 2 deixava a maioria dos golpes quebrada; responder às quatro ainda deixa quebrados os movimentos dependentes do histórico (pulo duplo, combos, esquiva, corrida de aproximação).
- Ao expor um segundo controle físico ao jogo, o jogo combina todos os controles em um único estado de entrada (o último prevalece).
- O ponteiro do ator-alvo da câmera em 0x0150A798 é reescrito pelo jogo a cada quadro; sobrescrevê-lo piorou o resultado. Mover a posição do jogador 1 para o ponto médio somente durante a atualização da câmera e restaurá-la depois funciona.
- Global real `IDirect3DDevice9*` em 0x014F5BEC (um hook no EndScene de um dispositivo fictício não desenhou nada).
- Super Family Attack realmente usa o jogador 2 como parceiro; depois, o script do golpe (ofuscado) o afasta voando e o define como ausente; reposicioná-lo e corrigir a câmera não resolveu.

## <a id="derived"></a>Deduzido

- O jogador 2 precisa de histórico de entradas próprio, não apenas de respostas próprias para os botões: a lógica dos movimentos lê o histórico e os temporizadores do objeto de E/S compartilhado. Uma cópia desse objeto por jogador, preenchida pela atualização do próprio jogo e substituída durante a atualização do jogador 2, deve proporcionar equivalência sem trabalho específico por movimento (mesmo formato do segundo registro de controle de The Two Towers).

## <a id="unknown"></a>Desconhecido

- Loja/edição da cópia testada; correspondência com outras compilações.
- Armazenamento da barra de vínculo entre irmãos (desbloquear todas as tartarugas desde o início da fase não foi resolvido).
- Comportamento do jogador 2 em carregamentos de fase e de checkpoints.

## <a id="checks-that-actually-ran"></a>Verificações realmente executadas

Execuções manuais de cada compilação do mod durante o desenvolvimento (2026-10-12 a 2026-10-14) e logs do mod. Ainda não há bot nem teste por script.
