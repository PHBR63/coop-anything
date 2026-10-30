# <a id="the-legend-of-zelda-ocarina-of-time-1998"></a>The Legend of Zelda: Ocarina of Time (1998)

| | |
|---|---|
| Motor | Ship of Harkinian (port nativo para PC a partir da descompilação, libultraship) |
| Versões testadas | Compilações a partir de N64 NTSC 1.0 (US), SHA-1 ad69c91157f6705e8ab06c79fe08aad47bb57ba7. Windows 11, VS 2022 v143, compilação Debug |
| Projetos | Anchor (modo cooperativo do Ship of Harkinian, incorporado ao projeto original em 2025-11); OOT True Co-op (fork de sincronização de inimigos); Shipwright-Online (fork com autoridade do host); [ocarina-coop](https://github.com/cranebeaker/ocarina-coop) (correções sobre Shipwright-Online) |
| Nível de QA | community-reports (Anchor); none (forks, incluindo ocarina-coop) |
| Última atualização | 2026-10-16 |

## <a id="where-things-stand"></a>Situação atual

Anchor sincroniza jogadores, inventário e indicadores do mundo, mas cada jogador enfrenta sua própria cópia dos inimigos. Shipwright-Online vai além (autoridade do host para inimigos, chefes, interruptores, pedras, músicas) e lista seus bugs conhecidos (em alemão). ocarina-coop dá continuidade: correções desses bugs e das lacunas encontradas em inspeções das masmorras posteriores. Nada disso foi jogado por duas pessoas ainda; portanto, ninguém pode afirmar até onde uma partida cooperativa chega hoje.

## <a id="existing-work"></a>Trabalhos existentes

- **Anchor**: https://github.com/garrettjoecox/anchor (servidor), cliente em https://github.com/HarbourMasters/Shipwright/tree/develop/soh/soh/Network/Anchor. O servidor é um retransmissor genérico: pacotes com `targetClientId` vão para esse cliente, pacotes de equipe vão para a equipe e todo o restante é enviado à sala inteira (consulte `client.go`). Assim, os forks podem acrescentar tipos de pacote sem mudar o servidor.
- **OOT True Co-op**: https://github.com/bghill95/OOT-True-Co-op (autoridade sobre inimigos e chefes).
- **Shipwright-Online**: https://github.com/fReEsPiRiT-Spiritsoft/Shipwright-Online. Fork do SoH 9.2.3, cerca de 480 commits atrás do projeto original na verificação. A autoridade por sala ("roommaster") é negociada entre clientes com pacotes `ROOM_MASTER_ASSIGN`, não pelo servidor.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- Cada jogador executa o jogo completo. Atores (inimigos, interruptores, plataformas) ficam na sala atual; o código descompilado de cada um está em `soh/src/overlays/actors/ovl_*/`.
- O progresso persistente fica nos indicadores de cena (switch, clear, chest, collect) e do contexto de salvamento. Anchor usa hooks em `OnFlagSet` / `OnSceneFlagSet` e os envia nos dois sentidos. A maior parte da progressão nas masmorras já depende disso.
- O problema é o que não depende desses indicadores: estado interno dos atores (animação de interruptor, função de ação de chefe, atores de nível de água, mortes de inimigos com vários quadros) e cenas.
- Shipwright-Online congela atores sem autoridade com hooks `ShouldActorUpdate` e transmite suas posições. Efeitos colaterais desse congelamento explicam vários bugs, por exemplo atores de nível de água que nunca se movem no cliente sem autoridade.

## <a id="what-we-changed"></a>O que alteramos

Cada item apresenta bug, causa raiz no código e correção. Testes: apenas compilação (consulte QA).

- **Interruptores de olho, chão e cristal funcionavam em um só sentido:** o indicador chegava, mas o ator de um interruptor já aberto nunca o relia. A correção executa novamente a transição de estado do próprio interruptor quando chega uma alteração remota do indicador.
- **Cena nunca termina para um jogador:** cenas iniciadas por atores em um cliente não tinham caminho de liberação nos demais. Adicionado monitor no cliente que libera cenas órfãs. Cenas por script (índice 0xFFF0 ou superior) ainda não são cobertas.
- **Inimigos noturnos inconsistentes:** o indicador de noite do host agora faz parte da sincronização de tempo, e o encaminhamento de dano do cliente espera a presença do responsável pela sala.
- **Níveis de água:** atores de água de Deku Tree, Lake Hylia e Water Temple executam localmente em vez de ficarem congelados, com um evento global do nível de Water Temple.
- Em andamento: sequências de morte de todos os chefes (a correção existente de Gohma parece código morto), sincronização de ações de King Dodongo (a escolha de ação pode ser rastreada na descompilação, ao contrário da nota do projeto original), sequência de abates de inimigos de Deku Tree, mortes de inimigos em vários quadros (Lizalfos, Dodongos), paredes destrutíveis com bombas, flores-bomba e lacunas das inspeções de Forest/Fire/Water, Shadow/Spirit/Well/Ice/GTG e Ganon's Castle/mundo externo.

## <a id="qa"></a>QA

- Cada correção compila na compilação Debug completa. Um agente revisor examinou cada commit em busca de dessincronizações, ciclos de eco, falhas e regressões no modo de um jogador.

## <a id="how-to-play"></a>Como jogar

Ainda sem versão distribuída. Quando houver: baixe o ZIP em [ocarina-coop Releases](https://github.com/cranebeaker/ocarina-coop/releases), execute `Play Co-op.bat`, informe nome e código da sala e selecione sua própria ROM na primeira execução.

## <a id="known-issues"></a>Problemas conhecidos

- Cenas por script podem deixar um jogador esperando; teletransportar-se até o responsável pela sala pelo menu de rede destrava a situação.
- O fork está atrasado em relação ao Ship of Harkinian original, sem suas correções recentes.

## <a id="notes-for-the-next-agent"></a>Notas para o próximo agente

- Compilação no Windows: se `CMAKE_TOOLCHAIN_FILE` apontar para Android NDK no ambiente, remova essa definição antes de configurar. Uma compilação Debug paralela precisa de cerca de 15 GB de disco e pode esgotar o heap do compilador; `-m:1 -p:CL_MPCount=4` funcionou.
- Crie primeiro a estrutura de testes com dois clientes. Duas janelas SoH em um PC contra servidor Anchor local (`go run .` ou executável nightly) é a configuração óbvia.
