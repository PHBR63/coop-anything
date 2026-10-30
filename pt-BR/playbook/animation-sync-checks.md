# <a id="checking-animation-sync"></a>Verificação da sincronização de animações

Um mod cooperativo pode ter posições perfeitas e ainda parecer quebrado: o amigo desliza pelo chão com animação ociosa, fica em pose em T, segura a arma errada, mira no céu enquanto o jogador original mira em você ou flutua um metro acima do chão. Jogadores percebem isso antes de notar uma dessincronização no estado das missões. Esta página mostra como detectar esses problemas por script, sem observação humana, em qualquer jogo.

A ferramenta é [tools/animcheck](../tools/animcheck/README.md). Ela lê fluxos de sondagem (linhas JSON escritas por um pequeno trecho de código no jogo), executa verificações e exibe PASS ou FAIL com relatório HTML. O formato está em [FORMAT.md](../tools/animcheck/FORMAT.md).

## <a id="what-the-avatar-looks-right-means-as-numbers"></a>O que significa "o avatar parece correto", em números

| Pergunta | Contador |
|---|---|
| O representante assume a mesma pose do jogador real? | `avatar.pose_err_p95` (unidades do mundo, após alinhar o osso raiz e a orientação) |
| Executa as mesmas animações? | `avatar.anim_mismatches`, `avatar.group_mismatch_pct` |
| Mesma arma, inclinação de mira e orientação? | `avatar.wrong_weapon`, `avatar.wrong_aim`, `avatar.wrong_facing` |
| Mesma postura (furtivo, nadando, derrubado, mirando)? | `avatar.stance_mismatch` |
| Comporta-se corretamente por conta própria (sem deslizar, pose em T, flutuar, tremer ou sofrer correções bruscas de posição)? | `avatar.glitches` e `avatar.glitch.<kind>` |
| Está no lugar certo, considerando o atraso de interpolação? | `avatar.pos_err_p95` |

Os mesmos números sem o prefixo `avatar.` cobrem NPCs compartilhados; assim, uma execução verifica jogadores e NPCs, mantendo-os separados.

## <a id="steps"></a>Etapas

1. **Escreva uma sonda.** Código no jogo, somente de leitura, que uma vez por quadro (ou a 10 a 30 Hz) escreva uma linha JSON: para cada ator próximo ao jogador, identificador, posição, rotação, animações em execução, posições dos ossos no espaço do mundo, arma e postura. Siga [FORMAT.md](../tools/animcheck/FORMAT.md). Leia o esqueleto completo em terceira pessoa mesmo na visão em primeira pessoa. Proteja toda leitura bruta de memória do motor para que um offset incorreto produza campo ausente, não falha. A sonda de New Vegas no repositório fnv-coop (`plugin/animprobe`, https://github.com/cranebeaker/fnv-coop) é um exemplo. Outros motores fazem o mesmo pela API de scripts ou plugin nativo.
2. **Escreva um perfil.** Um pequeno JSON com nomes dos ossos raiz e dos braços e a tabela de grupos de animação, com categoria por grupo (ocioso, caminhada, corrida, pulo, morte, ataque...). Copie [examples/fnv/profile.json](../tools/animcheck/examples/fnv/profile.json). Execute `python -I tools/animcheck/cli.py profile your.json`. Extraia a tabela dos dados do próprio jogo ou de uma ferramenta de mods; não adivinhe. Somente nomes entram no perfil, nunca arquivos do jogo.
3. **Registre uma execução limpa em uma máquina.** Um bot (consulte [automated-qa.md](automated-qa.md)) caminha, corre, gira, pula, saca e guarda uma arma, recarrega e nada, se houver água. Depois execute `cli.py analyze run.probe.jsonl --profile your.json --html report.html`. Toda constatação em uma execução limpa é um problema de perfil ou limiar, não um bug do mod. Corrija o perfil (o relatório lista os grupos de animação desconhecidos) ou altere um valor em `thresholds`. Teletransportes por script entram em `--suppress`.
4. **Registre a execução com duas máquinas.** Host e cliente na mesma sessão em um PC, o mesmo script de bot controlando o jogador do host e o representante desse jogador visível no cliente. Grave um arquivo de sondagem por máquina ou consulte ambos com `cli.py collect`, para compartilhar um relógio. Depois:

   ```
   cli.py analyze host.probe.jsonl client.probe.jsonl --profile your.json \
       --avatar "player=host:14>client:FF000A" --html report.html \
       --assert "avatar.pose_err_p95<=12" --assert "avatar.glitches==0" --assert "glitches==0"
   ```

   O argumento avatar identifica o jogador real na máquina responsável e seu representante na observadora.
5. **Transforme em teste.** Coloque o comando na suíte ao lado dos outros testes cooperativos, com as asserções como condição de aprovação, e execute após cada alteração no código de avatar ou animação. O código de saída é 0 para PASS. Um cenário de bot por script que exercite cada família de animações (locomoção, saque de arma, mira, recarga, morte, natação) produz constatações ligadas a uma causa.
6. **Teste o verificador, não somente o jogo.** A ferramenta inclui variantes de mutação: cada detector tem uma cópia com um bug deliberado, e seus testes devem falhar nela. Se acrescentar uma verificação ou alterar um limiar, acrescente uma variante da mesma forma, para detectar verificações que parem de disparar silenciosamente (`python -I tools/animcheck/run_tests.py`).

## <a id="reading-a-finding"></a>Leitura de uma constatação

A ferramenta informa o que ocorreu e quando, não a causa. Estas são as primeiras causas a investigar; confirme cada uma no código do jogo ou com uma segunda execução da sonda.

| Constatação | Causa provável |
|---|---|
| `tpose` com "no sequence running" | O grafo de animação do representante não é alimentado, ou o esqueleto foi trocado após configurar as animações. Confira a ordem de carregamento do modelo e início da animação. |
| `tpose` com "arms straight out" | Pose de vinculação: animações pararam ou nunca foram incorporadas à mistura. Comum logo após reaparecimento, troca de modelo ou de célula. |
| `sliding` sem animação de locomoção | O representante se move apenas pela posição de rede. Envie o estado de movimento (velocidade, direção, postura) à animação, além da posição. |
| `sliding`, "walk animation but 700 u/s" | Animação escolhida por velocidade obsoleta, ou saltos de posição mais rápidos que a interpolação. Examine a velocidade enviada à animação. |
| `floating` ou `sinking` | A altura do representante usa a altura do jogador original sem ajuste ao chão ou à malha de navegação, ou uma postura (nadar, agachar) altera o deslocamento do corpo. |
| `jitter` | Dois escritores movem o mesmo corpo, por exemplo o movimento do próprio jogo e a sincronização de posição. Um deles deve parar. |
| `rubberband` "snapped back" | A correção de posição disputa com o responsável. Procure um pacote atrasado ou fora de ordem aplicado após outro mais recente. |
| `group_mismatch` | O observador executa animação diferente da do responsável: evento perdido (sacar, recarregar, reação a golpe) ou animação escolhida localmente em vez de replicada. |
| `wrong_weapon` | Estado de equipamento não replicado, ou replicado após a animação que o exige. |
| `wrong_aim` | Inclinação da mira não enviada, ou osso de mira sobrescrito pela animação. |
| `deathpose` | O evento de morte chegou ao corpo, mas o grafo de animação manteve o estado vivo, ou o contrário. |
| `stuck` | Um comando de bot ou IA não foi repetido no observador. |

## <a id="pitfalls"></a>Armadilhas

- **Corpo em primeira pessoa.** Muitos jogos exibem somente braços em primeira pessoa. Uma sonda que lê esse modelo informa pose em T e enorme erro de pose no jogador local. Leia o esqueleto em terceira pessoa.
- **Conjuntos de ossos diferentes nas duas máquinas.** O erro de pose usa apenas ossos informados por ambos os lados. Envie os mesmos nomes em todos os lugares.
- **Grupos de animação desconhecidos.** Um grupo ausente do perfil é `unknown`, e `sliding` dispara para ele. O relatório exibe os grupos desconhecidos; acrescente-os.
- **Identificadores.** Um representante tem identificador diferente do jogador real. Sem `--avatar`, o verificador não compara nada, e `compared` vale 0 nos contadores. Confira `avatar.compared` e `compared`: PASS com 0 comparações não é PASS.
- **Relógios.** Dois processos têm dois relógios. Colete em um PC com `collect` (ele marca um relógio compartilhado) ou use `--auto-offset`.
- **Atraso de interpolação.** O verificador espera que o cliente exiba estado de cerca de 100 ms atrás e procura 150 ms para cada lado. Se o mod usar buffer maior, defina `--delay-ms`; não aumente a tolerância de pose para esconder isso.
- **Custo da sonda.** Amostrar 16 atores com 16 ossos não deve alterar o tempo de quadro que você está verificando. Meça.
- **Escala do mundo.** Os limiares assumem cerca de 70 unidades por metro. Defina `units_per_meter` no perfil.

## <a id="where-it-fits"></a>Onde se encaixa

Esta é a camada de "parece correto" sobre as verificações de estado em [automated-qa.md](automated-qa.md): elas comprovam que missão, inventário e posição correspondem; esta comprova que o corpo que mostra esse estado tem a mesma pose, animação e armamento. Execute ambas no mesmo cenário de bot.
