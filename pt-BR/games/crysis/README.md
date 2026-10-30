# <a id="crysis-2007"></a>Crysis (2007)

| | |
|---|---|
| Motor | CryEngine 2 (Crysis Mod SDK, DLL de jogo C++ e Lua) |
| Versão-alvo do jogo | Crysis 1.2.1 (GOG, Steam, EA; DVD atualizado) |
| Compilações / lojas efetivamente testadas de forma independente para este relato | Não verificadas |
| Projetos | [crysis-coop (SeniorStackOverflow)](https://github.com/SeniorStackOverflow/crysis-coop); [Crysis Co-op (projeto ModDB mais antigo)](https://www.moddb.com/mods/crysis-co-op) |
| Nível de QA | `none` para SeniorStackOverflow/crysis-coop; `community-reports` para o projeto ModDB antigo, conforme o diretório |
| Última atualização | 2026-10-18 |

## <a id="where-things-stand"></a>Situação atual

Há **dois esforços cooperativos distintos para Crysis**, não um único projeto contínuo.

- **[crysis-coop](https://github.com/SeniorStackOverflow/crysis-coop)** é uma implementação recente de código aberto em C++/Lua voltada à **campanha para um jogador de Crysis (2007), com 2-4 jogadores**. Inclui instalador, DLL de jogo, inicializador próprio, rede com reconexão, mecanismos de checkpoints de campanha e companheiro opcional controlado por bot/agente de IA. O repositório publica versões ([mais recente](https://github.com/SeniorStackOverflow/crysis-coop/releases/latest)); nesta atualização, a última visível era **v0.11.40**. Os recursos abaixo são **afirmações implementadas/documentadas no repositório**, não uma campanha completa verificada independentemente.
- **[Crysis Co-op](https://www.moddb.com/mods/crysis-co-op)** é um esforço ModDB anterior e separado, relatado como jogável pela comunidade (inclusive em cobertura de 2019). Seu histórico de versões e testes não deve ser atribuído ao projeto mais recente.

## <a id="existing-work"></a>Trabalhos existentes

| Projeto | Implementação / escopo | Rede | Evidências e limitações |
|---|---|---|---|
| [Crysis Co-op (ModDB)](https://www.moddb.com/mods/crysis-co-op) | Tentativa anterior de campanha cooperativa | Descrito como usando conexões ao servidor mestre Steam na reescrita de 2019 | [ModDB](https://www.moddb.com/mods/crysis-co-op), [cobertura de 2019](https://powerupgaming.co.uk/2019/11/13/crysis-co-op-mod-is-more-complete-than-ever/); relatos da comunidade, sem novo teste aqui |
| [SeniorStackOverflow/crysis-coop](https://github.com/SeniorStackOverflow/crysis-coop) | DLL de jogo separada do Crysis Mod SDK, com IA/história para um jogador no servidor e sincronização própria nos clientes | Código curto de conexão, abertura de caminho UDP por NAT, retransmissão WebSocket como alternativa; **não** retransmissão Steam Spacewar | [README](https://github.com/SeniorStackOverflow/crysis-coop/blob/main/README.md), [guia do jogador](https://github.com/SeniorStackOverflow/crysis-coop/blob/main/Mod/README.md), [guia do retransmissor](https://github.com/SeniorStackOverflow/crysis-coop/blob/main/Relay/README.md); QA dentro do jogo não verificado independentemente |

## <a id="how-crysis-works-for-co-op"></a>Como Crysis funciona para o modo cooperativo

Crysis já possui um modo de jogo em rede, mas **a simulação da campanha para um jogador não funciona automaticamente como campanha em rede**. O novo mod executa fases da campanha como mapas de rede e restaura a lógica para um jogador no host. Sua sincronização específica de clientes cobre ações/disparos de IA, posicionamento por scripts, efeitos de fluxo/HUD, cenas, objetivos de missão, objetos interativos e estado do nanosuit.

Os principais pontos de implementação no [repositório mais recente](https://github.com/SeniorStackOverflow/crysis-coop) são:

- **Autoridade do host:** `Code/Mod/CoopAI.cpp`, `Code/Mod/Nodes/CoopFlowNodes.cpp` e os scripts Lua/configurações em `Mod/` adaptam scripts de campanha, IA e eventos de história ao jogo em rede.
- **Entrada/reconexão:** `Code/Mod/CoopRelay.cpp` gerencia identidades, códigos curtos, tentativas de UDP direto e retransmissão alternativa. A [documentação pública do retransmissor](https://github.com/SeniorStackOverflow/crysis-coop/blob/main/Relay/README.md) explica o túnel de pacotes pelo servidor e as reconexões ao recarregar fase ou checkpoint.
- **Persistência da campanha:** `Code/Mod/CoopSave.cpp` e `Code/Mod/CoopCloud.cpp` coordenam salvamentos do motor, inventário/progresso por jogador e checkpoints compartilhados opcionais na nuvem. A intenção é permitir aos participantes retomar o progresso.
- **Inicializador e empacotamento:** `Launcher/`, `Installer/` e os scripts de compilação/empacotamento fornecem inicializador, verificação de versão, instalação a partir dos arquivos legais do próprio jogador e atualizações assinadas.
- **Companheiro de IA:** `Code/Mod/CoopAgent.cpp` e `Launcher/Mcp.cpp` iniciam e controlam um segundo cliente leve. O companheiro pode ser um bot convencional ou receber instruções pelo Model Context Protocol (MCP).

São descrições arquiteturais derivadas do código e da documentação. **Não** afirmam que toda missão, salvamento ou situação extrema de reconexão passou em testes.

## <a id="what-changed-in-the-newer-implementation"></a>O que mudou na implementação mais recente

O projeto recente descreve uma campanha com autoridade do host, em vez de tentar reutilizar regras multiplayer sem alterações. O host dirige a progressão original das missões, e clientes recebem eventos adicionais para um jogador que o multiplayer padrão não transmitiria. Também documenta reanimação de jogadores incapacitados, reinício da equipe no checkpoint, salvamentos de campanha na nuvem, reconexão automática dos clientes e segundo jogador opcional controlado por IA.

Nenhum teste independente com múltiplos clientes foi executado na preparação deste relato. Em particular, não promova o QA do novo projeto para `automated` apenas por incluir companheiro de IA, citar um testador automático nas notas de versão ou distribuir testes do protocolo de retransmissão. Isso é diferente de uma suíte registrada que controle clientes reais e verifique asserções de estado sincronizado.

## <a id="qa"></a>QA

**Classificação atual do novo projeto no catálogo: `none`.** Não foi revisada para esta contribuição nenhuma execução completa de teste multiplayer ou campanha concluída documentada independentemente. O projeto ModDB anterior mantém `community-reports`.

O retransmissor do projeto recente inclui um script de teste de protocolo ([`Relay/test_protocol.py`](https://github.com/SeniorStackOverflow/crysis-coop/blob/main/Relay/test_protocol.py)) que exercita comportamento do servidor, mas passar nesse teste sozinho **não** valida a sincronização real do jogo.

Plano sugerido de QA reproduzível **dentro do jogo**, para colaboradores com cópias locais legítimas:

1. Registrar versão/loja do executável Crysis, versão do mod, sistema operacional, quantidade de clientes e origem do salvamento de teste.
2. Executar host com um cliente real e depois host com três; verificar criação dos jogadores, movimento, combate de IA e consistência do estado de missão.
3. Acionar objetivos por script, cenas e transições de fase; verificar se cada par chega ao mesmo estado de missão.
4. Testar reanimação, reinício quando todos caem, inventários individuais e salvar/carregar checkpoints.
5. Reiniciar o host durante recarregamento, reconectar os pares e depois tentar outro participante hospedando a partir de checkpoint compartilhado.
6. Verificar modos UDP direto e retransmissão forçada, com perda de pacotes e NAT restrito quando disponíveis.
7. Registrar falhas observadas e passos exatos de reprodução. Declarar `automated` somente quando for possível compartilhar a estrutura executada, asserções, quantidade de clientes e resultados de aprovação/falha; declarar `verified-playthrough` somente após campanha completa documentada.

## <a id="how-to-play-the-newer-project"></a>Como jogar o projeto mais recente

Consulte o [guia oficial do jogador](https://github.com/SeniorStackOverflow/crysis-coop/blob/main/Mod/README.md) e a [versão mais recente](https://github.com/SeniorStackOverflow/crysis-coop/releases/latest).

Em resumo: cada jogador precisa da própria cópia de **Crysis 1.2.1** e do mod. Instale a partir do pacote da versão e inicie `CrysisCoop.exe`. O host escolhe **Multiplayer → Co-op game → New campaign** ou **Continue**; o amigo escolhe **Join a friend** e informa o código curto do host. A comunicação usa a infraestrutura própria de retransmissão do mod, não Steam Spacewar. O guia contém links para instruções de Windows e Linux com Wine.

## <a id="known-issues--boundaries"></a>Problemas conhecidos / limites

- **Campanha completa não verificada:** não é apresentada aqui uma campanha inteira com 2-4 jogadores nem uma matriz de compatibilidade entre lojas verificadas independentemente.
- **Dependência do host:** a sessão documentada termina quando o host sai; checkpoints na nuvem permitem *retomar*, não migrar o host sem interrupção durante a partida.
- **Custo do companheiro:** o companheiro de IA opcional inicia outro cliente e exige memória extra; a configuração sem interface não fornece capturas de tela por padrão.
- **Correspondência de versões:** segundo o guia, os clientes devem usar a mesma versão do mod para jogar juntos.
- **Jogo exigido:** o alvo é **Crysis (2007)**, não Crysis Remastered nem uma experiência cooperativa garantida para Crysis Warhead.

## <a id="next-steps-for-agents"></a>Próximos passos para agentes

- Criar uma estrutura de QA reproduzível com clientes reais e publicar resultado datado e legível por máquina, com compilação e quantidade de clientes.
- Exercitar checkpoints de grafos de fluxo/cenas nas **11 fases da campanha** e isolar dessincronizações com registros do host e cliente.
- Validar salvamentos, inventários, entradas após o início e reconexões contra reinícios do host e NAT restrito.
- Confirmar as variantes de configuração Linux/Wine e GOG/Steam/EA, em vez de inferir compatibilidade apenas pelo instalador.
- Manter claramente separadas a avaliação de QA do mod recente e os relatos da comunidade do projeto ModDB histórico.

## <a id="sources"></a>Fontes

- Mod recente: [README do repositório](https://github.com/SeniorStackOverflow/crysis-coop/blob/main/README.md), [guia do jogador em inglês](https://github.com/SeniorStackOverflow/crysis-coop/blob/main/Mod/README.md), [arquitetura do retransmissor](https://github.com/SeniorStackOverflow/crysis-coop/blob/main/Relay/README.md), [versões](https://github.com/SeniorStackOverflow/crysis-coop/releases).
- Mod anterior: [projeto ModDB](https://www.moddb.com/mods/crysis-co-op), [artigo de 2019](https://powerupgaming.co.uk/2019/11/13/crysis-co-op-mod-is-more-complete-than-ever/).
