# <a id="thief-ii-the-metal-age-2000"></a>Thief II: The Metal Age (2000)

| | |
|---|---|
| Motor | Dark Engine, atualizado por NewDark (código fechado); multiplayer = "MP beta" de NewDark, `Thief2MP.exe` |
| Versões testadas | Steam (aplicativo 211740, buildid 1970) + NewDark 1.29 MP beta, SHA-256 de `Thief2MP.exe` `e86b0645…1fe0` |
| Projetos | NewDark multiplayer beta (desde 1.27, 2019); [T2MPFix](https://github.com/D3c3453d/T2MPFix): quatro correções separadas (movimento de jogador remoto, bug de direcionamento original, limite de jogadores, dano ambiental). Diretório: "NewDark multiplayer beta (Thief2MP.exe) + T2MPFix" em [DIRECTORY.md](../../DIRECTORY.md) |
| Nível de QA | automated |
| Última atualização | 2026-10-29 |

## <a id="where-things-stand"></a>Situação atual

O MP beta de NewDark permite jogar as missões originais em modo cooperativo (2–3 jogadores originalmente, até 8 com T2MPFix; todos usam a mesma versão). As próprias notas de versão (`mp_release_notes.txt` em `mp.zip`) o chamam de beta: "do not expect a fully working game", e algumas missões têm objetivos de conclusão que somente o host pode cumprir.

Na configuração original, avatares dos outros jogadores aparecem no lugar errado (atrasados, presos na geometria, flutuando, afundando, saltando de posição, em parte porque o direcionamento do motor lê memória não inicializada), o último participante desconecta outros (por exemplo, um 4º jogador expulsa dois), e perigos executados localmente por cada jogo não causam dano (por exemplo, lava). T2MPFix, um proxy `dinput.dll` colocado por todos na pasta do jogo, tem quatro correções separadas, ativadas independentemente em `T2MPFix.ini`. Medido com duas a nove instâncias reais e bot de movimento (abaixo), somente nas missões 1 e 15.

## <a id="existing-work"></a>Trabalhos existentes

- NewDark 1.27/1.28/1.29 incluem `mp.zip` (`Thief2MP.exe`, OSMs seguros para multiplayer, `dark_net.cfg`): TTLG t=146448, t=153456. T2Fix o inclui como componente "Thief 2 Multiplayer Beta" (github.com/Xanfre/T2Fix).
- O antigo mod de fãs "Thief Multiplayer" (2007–2010, OldDark 1.18) é outro projeto (consulte a entrada do diretório).
- Figgis (systemshock.org, tópico 12190, 2023): análise do limite de jogadores para SS2 e T2 e executável modificado (o link Google Drive do vídeo de 2024 agora retorna 404). Seu offset de bytes T2 (0x2F440) não corresponde ao executável 1.27 de `t2_v127.zip`; ali a constante fica no offset 0x2F4FF do arquivo e em 0x3813F na versão 1.29 (`mov [edi+0x136], 4`).
- Guia em vídeo: WungusDasPungus, "How to Make Thief 2 Multiplayer Actually Work" (youtube.com/watch?v=aRiVJqx9cnQ).
- Servidor global para o navegador interno: github.com/sungaila/NewDarkGlobalServer.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

O sistema original de "fantasmas" da Looking Glass move objetos em rede (detalhes e endereços em `NOTES.md`): a responsável só envia um sinal periódico quando a estimativa por extrapolação do receptor difere mais de 4 unidades em algum eixo (intervalo mínimo de 100 ms para jogadores); o receptor prevê com gravidade e um raio que para nas paredes, depois direciona o corpo físico do avatar à estimativa por uma velocidade, colidindo com o mundo no caminho, e só o teletransporta quando o erro ultrapassa 12 unidades. Se esse direcionamento realmente aproxima um avatar em movimento depende de três floats da pilha que o código nunca escreve; no jogo original ele não aproxima, então avatares ficam várias unidades atrás. O transporte é DirectPlay (Windows oferece instalá-lo na primeira execução; as strings de erro do executável o mencionam). Nenhuma variável de configuração controla isso.

## <a id="what-we-changed"></a>O que alteramos

Quatro correções independentes, cada uma com um arquivo-fonte e uma opção em `T2MPFix.ini`. Uma correção desligada (ou com bytes do motor incompatíveis) não instala hooks; assim, se NewDark corrigir um desses problemas, somente aquela correção pode ser desativada. `T2MPFix.log` lista as correções ativas.

1. **Suavização de jogadores remotos**, em duas partes:
   - `send_fix` (`0x554fe0`): enquanto o jogador se move ou gira, envia um sinal a cada 50 ms.
   - `recv_fix` (`0x553dc0`): armazena estados recebidos em buffer e exibe o jogador na trajetória interpolada com pequeno atraso adaptativo (60–300 ms), posicionado a cada quadro pelo teletransporte do motor (`ObjPosUpdate` como alternativa se ele recusar). Jogadores com fluxo na frequência original (sem `send_fix`) mantêm o comportamento original.
2. **Bug de direcionamento original**, `steer_fix` (`0x553f07`): para jogador remoto em movimento, o código decide se aproxima o avatar da previsão testando três floats da pilha que nunca escreveu. No jogo original, o teste falha e os avatares ficam várias unidades atrás (path_dev p95 ~7); um hook nessa cadeia pode inverter o resultado, o que levou à descoberta. Um patch de 6 bytes remove o teste (sempre aproxima). Isso importa para jogadores não interpolados por `recv_fix` (sem T2MPFix).
3. **Limite de jogadores**, `max_players` (`cNetManager::SetMaxPlayers`, vaga 40 da vtable): definido como N+1 para N jogadores, conforme Figgis. No limite original, o último participante faz outros serem expulsos (o limite é 4, então cabem 3 e um 4º expulsa dois). O INI distribuído define 8, o máximo possível: a sessão DirectPlay8 do host tem `dwMaxPlayers = 8` (`0x684254`), então valores maiores são limitados. Um 9º fica em "Joining Game..." e não desconecta ninguém. Um N menor só desloca o bug: com `max_players=3`, um 4º ainda expulsou dois, por isso o INI orienta manter 8.
4. **Dano ambiental**, `damage_fix` (`0x44bce0`): o filtro de dano MP zera, em todas as máquinas, todo dano causado por objeto Local Only (por exemplo, lava, um `Water Flow Group`). O hook permite passar na máquina que hospeda a vítima; assim, cada jogador recebe dano da própria cópia do perigo e nada é aplicado duas vezes.

## <a id="qa"></a>QA

Os caminhos abaixo ficam no repositório T2MPFix (https://github.com/D3c3453d/T2MPFix).

- `mod/tests/`: testes unitários no host para interpolação (6 casos, incluindo teletransporte, intervalo ocioso, volta do ângulo; execuções de mutação falham como esperado), regra de dano local e hooks instalados por cada combinação de correções.
- `tools/qa/test_analyze.py` (autoteste das métricas, incluindo execuções preso, flutuando e parado).
- `tools/qa/regress.sh`: jogos reais em um PC (canal de QA na DLL controla menus, bots controlam jogadores, telemetria dos dois lados, perturbação de rede na DLL). "stock" é o jogo real: a função de direcionamento não recebe hook (a telemetria percorre a tabela de fantasmas). Última execução em 2026-10-29, compilação de `dinput.dll` `817cbee6…` (versão 0.3):

```
PASS stock localhost (control)    travelled  285.8  path_dev p95 7.052 max 14.870  off>1  4346  jumps 2  lag p50 3.03  hb/s 1.3  fixed 0/7119
PASS fixed localhost              travelled  286.1  path_dev p95 0.003 max 0.134  off>1     0  jumps 0  lag p50 0.30  hb/s 16.4  fixed 6802/7120
PASS fixed 60+-30ms 2% loss       travelled  285.2  path_dev p95 0.005 max 0.209  off>1     0  jumps 0  lag p50 0.61  hb/s 15.6  fixed 6780/7112
PASS fixed 150+-75ms 10% loss     travelled  285.2  path_dev p95 0.006 max 0.245  off>1     0  jumps 0  lag p50 0.98  hb/s 11.4  fixed 6710/7100
PASS send_fix only                travelled  287.0  path_dev p95 9.764 max 11.877  off>1  4154  jumps 2  lag p50 2.13  hb/s 16.4  fixed 0/7119
PASS recv_fix only                travelled  285.9  path_dev p95 2.676 max 3.658  off>1  2996  jumps 1  lag p50 1.13  hb/s 1.3  fixed 0/7122
PASS steer_fix only               travelled  286.7  path_dev p95 2.626 max 3.509  off>1  2981  jumps 1  lag p50 1.12  hb/s 1.3  fixed 0/7126
PASS mixed (mover without fix)    travelled  284.3  path_dev p95 2.578 max 3.424  off>1  2816  jumps 1  lag p50 1.09  hb/s 1.3  fixed 0/6891
ALL PASS
```

(path_dev: distância, em unidades Dark, entre o avatar exibido e a trajetória real do jogador; "off>1": quadros a mais de 1 unidade dela, de cerca de 7.100.) O máximo original depende de alguns saltos e varia entre execuções (7,7; 17,7; 14,3; 14,9 nas últimas quatro); seu p95 fica entre 6,5 e 7,3. "send_fix only" é um jogador T2MPFix visto por outro sem a ferramenta: não melhora o original, geralmente piora um pouco (p95 9,8 contra 7,1 aqui), então todos devem instalá-la. Tabelas anteriores (histórico do README, NOTES) chamavam de "stock" o comportamento original sob nosso hook de direcionamento, que por acaso evitava o bug (máximo ~3,0).

Cada correção sozinha, com as demais desligadas:
- `max_players=4` (compilação anterior): 4 instâncias entram e jogam; controle com `max_players=0`: a 4ª desconecta as outras.
- `tools/qa/players.sh` (versão 0.3): `MAXP=8 players.sh 4` e `players.sh 3` PASS (cada instância vê todas as outras a cada segundo por 60 s). Com `max_players=3`, a 4ª expulsou dois jogadores (consulte correção 3).
- `tools/qa/players.sh` (compilação `070f9688…`, mesmo código de correção da 0.3): 5 e 8 jogadores PASS. Uma 9ª instância fica em "Joining Game..." e não desconecta ninguém, mesmo com o limitador removido (o limite era 10; DirectPlay é a restrição). A repetição 8+1 na versão 0.3 falhou com 189 MB de RAM livre e não foi repetida (detalhes em NOTES).
- `damage_fix=1` (`tools/qa/lava.sh`, versão 0.3): o jogador morre na lava de Soulforge; `damage_fix=0`: sai ileso (bug original). Um comando de QA o coloca na lava; a telemetria confirma a posição antes da avaliação.
- Todas as correções e QA desligados: nenhum hook ou patch.

Compilações anteriores com o mesmo código de correção: 4 jogadores, 2 em movimento, path_dev máximo na missão ≤ 0,64; 3 jogadores, 5 minutos, 2 em movimento, máximo 0,23, sem travamento.

## <a id="how-to-play"></a>Como jogar

1. Todos: T2Fix 1.29 com "Thief 2 Multiplayer Beta" (ou NewDark 1.29 + `mp.zip` manualmente).
2. Todos: copiar `dinput.dll` e `T2MPFix.ini` para a pasta do jogo. Na primeira execução, Windows oferece instalar DirectPlay; aceite ou o multiplayer não inicia (se tiver dispensado, `INSTALL.txt` explica como ativar em Recursos do Windows).
3. Host: redirecionar porta 5198 (notas MP de NewDark; também 5199 para servidor global, conforme o vídeo) ou usar uma VPN LAN.

No jogo, um jogador morto é reanimado quando outro interage com ele; só termina quando todos morrem (notas MP de NewDark).

## <a id="known-issues"></a>Problemas conhecidos

- Um jogador sem T2MPFix vê quem usa a ferramenta sem melhora em relação ao original, geralmente um pouco pior; por isso, todos na sessão devem instalá-la.
- Algumas missões têm objetivos de conclusão que apenas o host pode cumprir (notas MP de NewDark).
- IA e outros objetos em rede continuam com o código original de movimento dos fantasmas.
- Alternar de janela com Alt-Tab ainda pausa o jogo daquele jogador, travando ações como salvar para todos (comportamento original).
- Sem cobertura de testes: jogadores em elevadores e plataformas móveis (voltam ao movimento original), escadas, flechas de corda, escalada de bordas, natação, salvar e carregar, mudanças de missão, missões de fãs e sessão pela internet (latência e perda só foram simuladas).

## <a id="next-steps"></a>Próximos passos

- Ampliar o bot caminhante para degraus, escadas e elevadores em missão conhecida; adicionar teste de salvar/carregar e mudança de missão.
- Aplicar a mesma interpolação aos fantasmas da IA.
- Opção de continuar em segundo plano para jogadores (a subclasse de QA já faz isso).
- `max_players` abaixo de 8: recusar participantes além de N em vez de permitir que expulsem outros (hoje só 8 é seguro).
