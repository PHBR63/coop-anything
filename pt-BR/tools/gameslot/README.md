# <a id="gameslot-a-lease-lock-for-running-game-copies"></a>gameslot: trava com prazo de reserva para executar cópias de jogos

Vários agentes, ou vários scripts de um agente, querem executar cópias do mesmo jogo em um PC. Sem uma trava, eles iniciam o jogo ao mesmo tempo, escolhem a mesma pasta de instância ou porta, esgotam a RAM ou encerram os jogos uns dos outros. `gameslot` é uma pequena trava com prazo de reserva que evita tudo isso.

- **Vagas.** A máquina tem N vagas (padrão 2). Um responsável reserva uma ou mais antes de iniciar um jogo e as libera depois de encerrar seus jogos. Os números das vagas são seus: derive deles os nomes de pasta da instância, porta e pipe, e dois responsáveis nunca entrarão em conflito.
- **Reservas expiram.** Uma reserva dura `--ttl` segundos (padrão 900) e é renovada solicitando novamente com o mesmo responsável. Um responsável que falhou não bloqueia o PC para sempre.
- **Ordem de chegada.** As solicitações em espera formam uma fila, para que um pedido de muitas vagas não fique indefinidamente atrás de uma sequência de pedidos pequenos.
- **Proteção de RAM.** Uma solicitação que iniciaria um segundo jogo quando a RAM livre está abaixo de `min_free_gb` (padrão 3) é recusada. O primeiro jogo e as renovações nunca são recusados.
- **Encerramento limitado por PID.** O responsável registra cada processo de jogo iniciado (`register-pid`). Se a reserva expirar e outra pessoa assumir, somente os processos registrados são encerrados, e apenas se o PID ainda tiver o mesmo nome de executável e horário de criação. Um PID reutilizado pertence a outro processo e é preservado. Nada aqui encerra "todos os processos com o nome do jogo", pois o dono do PC pode estar jogando.
- **Uma trava para mudanças de estado.** Toda alteração ocorre sob um arquivo de trava de curta duração, de modo que dois processos nunca consigam a mesma vaga.

Usa apenas a biblioteca padrão do Python. Windows é a plataforma compatível (a identidade dos processos usa a API Win32).

## <a id="quick-start"></a>Primeiros passos

```
python -I tools/gameslot/gameslot.py acquire --owner agent1 --slots 2 --ttl 1800 --wait 600
#  OK lease until ...; SLOTS 0,1          <- instances 0 and 1 are yours

python -I tools/gameslot/gameslot.py register-pid --owner agent1 --pid 1234     # for every game process you start
python -I tools/gameslot/gameslot.py status                                      # JSON: every slot and its lease
python -I tools/gameslot/gameslot.py release --owner agent1                      # after you killed your games
```

Opções de `acquire`: `--slots K` (padrão 1), `--exclusive` (todas as vagas), `--ttl SECONDS`, `--wait SECONDS` (quanto tempo permanecer na fila; 0 significa falhar imediatamente). Códigos de saída: 0 sucesso, 2 uso incorreto, 3 ocupado, 4 não é o responsável.

Chamadores Python podem importar o módulo: `acquire`, `release`, `register_pid` e `status` são funções comuns, e `main(argv)` é a interface de linha de comando.

## <a id="config"></a>Configuração

O estado fica em `GAMESLOT_DIR`, se definido; caso contrário, em `<repo>/local/gameslot` (o Git ignora `local/`). Um `gameslot_config.json` opcional nessa pasta:

```json
{"slots": 2, "min_free_gb": 3.0, "process_name": "Game.exe"}
```

| Chave | Padrão | Significado |
|---|---|---|
| `slots` | 2 | Quantas cópias do jogo podem rodar ao mesmo tempo neste PC |
| `min_free_gb` | 3.0 | Uma nova vaga é recusada se a RAM livre estiver abaixo desse valor (somente quando já houver outra vaga ativa) |
| `process_name` | nenhum | Usada apenas por `status` para listar PIDs de processos de jogo em execução. Nunca é usada para encerramentos |

Defina `GAMESLOT_POLL` (segundos, padrão 10) para mudar a frequência com que um `acquire` em espera tenta novamente.

## <a id="how-it-is-tested"></a>Como é testado

```
python -I tools/gameslot/run_tests.py       # prints ALL OK only if every check passes and every twin is caught
```

18 verificações e 13 variantes de mutação no momento da escrita (última linha da saída: `18 checks, 13 twins, 0 failed`).

- A maioria das verificações usa uma tabela de processos em memória, então nada real é encerrado. Elas cobrem vagas distintas, respostas de ocupado, pedidos de várias vagas com tudo ou nada, renovação, tomada de reservas expiradas, justiça FIFO, proteção de RAM, processos registrados, reutilização de PID e trava do estado (incluindo uma trava obsoleta deixada por um processo morto).
- Uma verificação coloca seis processos reais de `gameslot.py acquire` em disputa por uma vaga e exige exatamente um vencedor.
- Uma verificação inicia dois processos substitutos inofensivos (um interpretador Python em espera), registra um, deixa a reserva expirar, assume a vaga e exige que somente o substituto registrado tenha sido encerrado.
- Cada **variante de mutação** quebra uma proteção de propósito (todas as vagas sempre concedidas, ausência de rollback, reservas que nunca expiram, ausência de fila, ausência de proteção de RAM, encerramento indiscriminado de processos com o nome do jogo, encerramento que ignora reutilização de PID, trava sempre concedida, ...) e executa novamente a mesma verificação. A execução falha se a verificação não detectar o defeito.

Os testes nunca iniciam um jogo nem alteram processos que eles próprios não iniciaram.

## <a id="ported-from-fnv-coop-commit-f57aa78"></a>Adaptado do commit f57aa78 de fnv-coop

Adaptado de `tools/gameslot.py` e seus testes no [fnv-coop](https://github.com/cranebeaker/fnv-coop) (commit f57aa78). Alterações: removidos o nome do jogo, o executável e as pastas (não há valores específicos de jogo no código); `--slots` agora tem padrão 1 e `--exclusive` substitui "sem opção significa todas as vagas"; removida a compatibilidade com uma ferramenta anterior de vaga única; processos registrados agora guardam o nome do executável e o horário de criação, tornando a proteção contra reutilização de PID independente de nomes de jogos; a trava de estado e o executor de testes com variantes de mutação são novos.
