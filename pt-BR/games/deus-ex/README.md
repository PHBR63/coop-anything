# <a id="deus-ex-2000"></a>Deus Ex (2000)

| | |
|---|---|
| Motor | Unreal Engine 1 (compilação Deus Ex 1112fm) |
| Versões testadas | Steam Game of the Year Edition |
| Projetos | HX 0.9.89.4 (Hanfling, 2019) mais HXFix e HXCoop: https://github.com/cranebeaker/deus-ex-coop |
| Nível de QA | automated |
| Última atualização | 2026-10-16 |

## <a id="where-things-stand"></a>Situação atual

É possível jogar a campanha inteira em modo cooperativo com HX e o pacote HXFix. Mais de 40 testes automatizados com clientes reais do jogo passam, incluindo execuções por retransmissor Steam com latência e perda de pacotes simuladas.

## <a id="existing-work"></a>Trabalhos existentes

- **HX**, de Sebastian Kaufel (Hanfling): conversão cooperativa de toda a campanha usando o próprio código de rede multiplayer de Deus Ex. Última compilação 0.9.89.4 (junho de 2019) em https://builds.hx.hanfling.de/testing/ (mais recente que a página de versões). O desenvolvimento parou com bugs cooperativos conhecidos ainda presentes.
- Patches cooperativos mais antigos de Deus Ex cobriam apenas mapas isolados.
- O Discord Deus Ex Community HQ reúne discussões sobre HX; o deus-ex-randomizer de Die4Ever tem uma variante HX.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para modo cooperativo)

- A lógica do jogo está em UnrealScript nos pacotes `.u`; o motor possui replicação cliente/servidor, então o HX executa a lógica de um jogador (conversas, missões, indicadores, viagens) no servidor e a replica.
- O HX distribui `HX.u` (960 classes, cerca de 120 mil linhas) e a biblioteca nativa fechada `HX.dll`. Não é possível recompilar `HX.u`: o compilador falha em asserções nas classes sem texto de script armazenado, e a DLL fixa a disposição em memória das classes nativas.
- Os scripts foram extraídos com um pequeno leitor de pacotes em Python; `HX.dll` foi descompilada com Ghidra sem interface (2.773 funções, nomes C++ intactos).

## <a id="what-we-changed"></a>O que alteramos

Um pacote separado, HXFix, com subclasses substituídas por hooks de mutator do HX, uma subclasse do tipo de jogo e subclasses das classes de jogador. Destaques (lista completa com causas raiz no BUGS.md do projeto):

- Falha do cliente nas mudanças de mapa (ponteiros Owner obsoletos antes da coleta de lixo).
- Falha quando alguém deixa a tela de inventário aberta durante uma mudança de mapa ou na saída.
- Conversa final que nunca começava (nome do mapa comparado com "NOTHING").
- Jogadores mortos durante uma mudança de mapa chegavam com 0 HP e sem equipamentos.
- Notas (códigos de portas) apagadas a cada mudança de mapa.
- Conversas controláveis por qualquer jogador; conversas forçadas que interrompiam umas às outras.
- Aprimoramento Microfibral Muscle, Use Cell, mods de armas, seleção de munição e Change Ammo para jogadores que entraram na sessão; verificações de nanokey em datalinks nos clientes.
- Bugs dos scripts das missões 2, 3, 4, 5, 9, 10 e 15.
- Loop descontrolado de consulta ao servidor que podia travá-lo.
- HXCoop: retransmissão pelo Steam (AppID 480), dispensando endereço IP e redirecionamento de portas.

## <a id="qa"></a>QA

- Estrutura de testes: host que também participa da partida, mais 1 ou 2 clientes reais em um PC, um ator de teste selecionado por opção de URL e um controlador por jogador que faz os clientes executarem comandos de console, exercitando RPCs reais do cliente para o servidor. Um inicializador exibe PASS/FAIL e falha quando clientes encerram inesperadamente (lê o texto da janela de erro).
- Variantes: por HXCoop com uma implementação simulada de `steam_api.dll`; com simulação `PktLag`/`PktLoss`; com uma instalação cliente sem HXFix (verifica o download automático).
- Verificou-se que cada teste de correção falha quando a correção é desativada.

## <a id="how-to-play"></a>Como jogar

Consulte https://github.com/cranebeaker/deus-ex-coop (o instalador baixa HX de seu servidor oficial; depois hospede com 1 e entre com 2).

## <a id="next-steps"></a>Próximos passos

- Executar uma campanha inteira automaticamente: percorrer todos os mapas em ordem com 2 clientes.
- Publicar as correções na comunidade HX e consultar a possibilidade de incorporá-las ao projeto original.
