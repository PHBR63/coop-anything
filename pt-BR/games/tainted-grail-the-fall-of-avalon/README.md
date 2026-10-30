# <a id="tainted-grail-the-fall-of-avalon-2025"></a>Tainted Grail: The Fall of Avalon (2025)

| | |
|---|---|
| Motor | Unity 6000.0.41f1, scripts Mono na branch beta oficial `mono` do Steam |
| Versões testadas | Steam, branch `mono`, buildid 25966682, versão do jogo 1.30.102 (`[1.30a]`) |
| Projetos | TGCoop, "2 Players Steam Coop" ([Nexus](https://www.nexusmods.com/taintedgrailthefallofavalon/mods/211), entrada no diretório) |
| Nível de QA | TGCoop: community-reports. Nosso trabalho abaixo: automated (duas cópias em um PC; somente entrada, salvamentos e visibilidade entre jogadores) |
| Última atualização | 2026-10-19 |

## <a id="where-things-stand"></a>Situação atual

Ainda não é possível jogar bem a história juntos. TGCoop é jogável, mas há relatos de bloqueios de progresso, combate dessincronizado e história fora de sincronia. Nosso mod, criado do zero, coloca um segundo jogador no mundo do host com seu próprio personagem, mantém os dois personagens no salvamento do host e mostra cada jogador ao outro como um corpo em movimento (ainda sem animação); inimigos, história e mundo ainda não são compartilhados. Não há versão distribuída.

## <a id="existing-work"></a>Trabalhos existentes

- **TGCoop** (hektormenta, mod Nexus 211, compilação mais recente observada 0.5.36 de 2026-07-28, sem licença nem código-fonte). BepInEx 5 + Harmony, salas Steam no app id do próprio jogo. Ambos carregam seus salvamentos; o host envia os indicadores verdadeiros da história na entrada e sincroniza três chamadas da história ao vivo, posiciona NPCs, sincroniza portas e objetos; itens derrubados ficam com quem pegar primeiro. Relatos: portão fechado para o parceiro após o diálogo de Odrán, parceiro congelado por diálogo em lutas de chefe, combate dessincronizado, pose A em primeira pessoa, recompensas de missões só para um jogador. Corrigidos na 0.5.36 segundo o autor: inimigos longe do host (o jogo para de simulá-los) e salvamentos do host recusados silenciosamente por estado de combate preso. Segundo o autor, somente o Ato 1 foi realmente testado; última resposta no Nexus em 2026-07-28. Detalhes e causa quando o código a revela: [NOTES.md](NOTES.md).
- Nenhum outro projeto cooperativo encontrado; menções sem nome nos fóruns Steam e os locais pesquisados estão em [NOTES.md](NOTES.md) ("Existing work", "Where we looked"). O Discord do jogo não foi consultado.
- O kit oficial de mods do desenvolvedor, [merlin-workshop](https://github.com/AR-Questline/merlin-workshop), faz somente mods de recursos e dados (substituições Addressables); não permite incluir o código de um mod cooperativo.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Caminho para mods.** A branch beta `mono` usa Mono; BepInEx 5 carrega plugins e Harmony aplica patches ao C# (`TG.Main.dll`, `Awaken.*.dll`), descompilável com os nomes originais. A branch padrão provavelmente usa IL2CPP (não verificado).
- **Sem código de rede.** Somente um jogador; Steamworks.NET existe para recursos Steam e salvamentos na nuvem. O modo cooperativo precisa de transporte próprio e sincronização com autoridade do host.
- **Modelos e IDs.** Estrutura MVC própria: cada estado do mundo é um modelo com ID textual `<Type>:<counter>`; contadores por tipo são salvos com o mundo. Dois jogos a partir do mesmo salvamento começam com os mesmos IDs e divergem assim que um cria algo.
- **História.** Um armazenamento de indicadores: `GameplayMemory` → `ContextualFacts.Set/Change/Remove`, por trás de missões, objetivos e indicadores da história. Histórias usam `Story.StartStory` e `StoryStep.Execute`; interações usam `AbstractHeroAction.StartInteraction`.
- **Um herói.** `Hero.Current` é uma leitura estática feita cerca de 1.190 vezes. O herói é construído como jogador local (visualizações, câmera, componentes de execução); um segundo herói real no mesmo mundo exige exceções por toda parte (tentado, veja NOTES.md). Jogadores remotos são representações substitutas.
- **Salvamentos.** Um espaço de salvamento é um ZIP com um `.data` por domínio (Gameplay, cada área visitada, metadados), escrito por serviço de nuvem (Steam Cloud, Steam sem nuvem, GOG). Entradas adicionais no ZIP são preservadas em todos os salvamentos. New Game+ já exporta um personagem e o restaura em outro mundo; a entrada com personagem próprio se baseia nisso.
- **Áreas** são domínios separados de salvamento, carregados um de cada vez.
- Mais informações e locais no código: [NOTES.md](NOTES.md), "How the game works".

## <a id="what-we-changed"></a>O que alteramos

Nosso mod é um plugin BepInEx com transporte LiteNetLib (UDP) por enquanto; há planos de retransmissão Steam.

- **Entrada com personagem próprio.** Problema: o convidado precisa do mundo do host, mas de seu próprio personagem. Carrega o salvamento do host e, durante o carregamento do jogo, o herói e os itens do host são substituídos pelos do convidado (IDs novos de itens pelos contadores do mundo, uma passagem de restauração); o mundo vê um salvamento normal. Teste: entrar e jogar com seu personagem e todos os itens ao lado do host; variante: entrada sem personagem deve falhar exatamente nas verificações de personagem.
- **Salvamentos somente no host.** O salvamento cooperativo do host é a única cópia permanente do mundo e do personagem de cada convidado (entradas extras no ZIP). O convidado recebe o mundo atual ao entrar, mantém em memória e seu jogo não pode salvar (bloqueador do próprio jogo). Testes: pasta de salvamento do convidado inalterada após a sessão; personagem alterado e armazenado retorna na próxima entrada após ambos os jogos encerrarem; cada teste tem variante de mutação.
- **Visibilidade entre jogadores** (etapa 2 dos guias). Lista de participantes, estado a 20 Hz (sem garantia de entrega), encaminhado pelo host; cada jogador remoto é o corpo de terceira pessoa do próprio jogo, sem as partes exclusivas do herói, interpolado com 100 ms de atraso. Teste: um bot caminha, seu corpo no outro jogo acompanha e termina a até 0,5 m, nos dois sentidos; variante: nenhum estado enviado.
- **Ambiente de teste.** Duas cópias isoladas (pastas próprias de salvamentos e temporários, sem Steam Cloud ou relatórios automáticos de bugs), em janela, um bot em cada jogo, retransmissor de rede degradada e inicializador que encerra uma cópia se os patches Harmony não forem aplicados.

## <a id="qa"></a>QA

- A suíte (no repositório do mod, ainda não público) controla duas cópias reais em um PC com bots internos: `run-suite.ps1 -Quick` (uma sessão, cerca de 2 min) ou `-Full` (também reinicializações, rede degradada e variantes de mutação, cerca de 10 min). Verifica entrada, personagem do convidado, salvamentos só no host, persistência após reiniciar, visibilidade, encerramento limpo e ausência de relatórios de falha. Cada verificação tem variante de mutação que precisa falhar; o avaliador é testado primeiro.
- Último resultado (2026-10-19): `-Full` `SUITE: PASS` em 614 s: autoteste do avaliador 9/9, execução principal 40/40, rede degradada (100 ms por sentido, jitter de 20 ms, perda de 5%) 31/31; as variantes falharam exatamente nas 17 e 1 verificações listadas.

## <a id="how-to-play"></a>Como jogar

Ainda não jogável: não há versão distribuída.

## <a id="known-issues"></a>Problemas conhecidos

- O outro jogador é um corpo masculino padrão, careca, em pose T, sem animação ou equipamento.
- Inimigos, história e mundo não são compartilhados; cada jogo executa os seus.
- O convidado não pode salvar; seu personagem é salvo pelo host.
- Testado somente com duas cópias em um PC por UDP local; ainda sem transporte Steam. Salvamentos GOG não são aceitos.

## <a id="next-steps"></a>Próximos passos

Etapa 3 dos guias: inimigos executados somente no host e exibidos no convidado; dano de ambos os jogadores; itens derrubados aparecem uma vez. Depois animação e aparência do outro jogador; em seguida história e mundo (etapa 4). A arquitetura (host executa todos os scripts, convidados enviam solicitações, tabela de estado compartilhado e individual) está resumida em [NOTES.md](NOTES.md), "World design".
