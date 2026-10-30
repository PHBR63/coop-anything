# <a id="dungeon-keeper-1997"></a>Dungeon Keeper (1997)

| | |
|---|---|
| Motor | KeeperFX (reescrita em C de código aberto, GPLv2), código de rede lockstep |
| Versões testadas | Compilações KeeperFX alpha 1.4 com os dados originais do jogo GOG |
| Projetos | "Archon mode" do KeeperFX (projeto original, vários jogadores por guardião); branch cooperativa de guardião compartilhado baseada nele; Dungeon Keeper 2 tem um projeto separado, dk2-coop |
| Nível de QA | automated |
| Última atualização | 2026-10-16 |

## <a id="where-things-stand"></a>Situação atual

Versão distribuída: [cranebeaker/dungeon-keeper-coop](https://github.com/cranebeaker/dungeon-keeper-coop) (v0.1.0 beta, código-fonte em [cranebeaker/keeperfx `archon-coop`](https://github.com/cranebeaker/keeperfx/tree/archon-coop)).

De dois a quatro jogadores compartilham um guardião (uma masmorra, uma mão por jogador) durante a campanha, pelo Steam ou por IP direto. Cada jogador vê as mãos dos outros nas cores escolhidas e com seus nomes. Um bot de testes dentro do executável joga as fases e percorre o fluxo da campanha com processos reais do jogo (2 e 3 jogadores, IP e Steam); as execuções passam com 0 dessincronizações.

## <a id="existing-work"></a>Trabalhos existentes

- O KeeperFX original está desenvolvendo o "Archon mode" (vários usuários controlando um jogador) por meio de uma série de PRs de refatoração de UserState em 2026. Desenvolva a partir dele em vez de criar um fork que o contorne.
- Dungeon Keeper 2: dk2-coop (https://ciphercom.github.io/dk2-coop/).

## <a id="what-we-changed"></a>O que alteramos

- Transferimos o estado restante por jogador (possessão, mão, estado de feitiços, posicionamento de salas e câmera) para estado por usuário, para o modo cooperativo archon.
- Fluxo de campanha compartilhado: mapa, instruções, fase, estatísticas, retorno ao mapa, derrota e nova tentativa.
- Provedor de rede Steam sobre a API plana Steamworks (AppID 480), permitindo entrar por convite Steam ou lista de amigos. Consulte [playbook/networking-steam-spacewar.md](../../playbook/networking-steam-spacewar.md).

## <a id="qa"></a>QA

- O bot interno `-archontest` / `-archonflow` escreve os mesmos pacotes de entrada que uma pessoa escreveria, verifica os resultados e registra PASS/FAIL. Oráculo: os checksums de cada turno precisam coincidir nos dois lados (0 dessincronizações).
- Cobertura: jogo dentro das fases, fases 1 a 4, derrota e nova tentativa, percurso pelos menus, desconexões por saída normal e encerramento forçado, fluxos de convite Steam (com uma implementação simulada de `steam_api.dll`).
