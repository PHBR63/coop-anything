# <a id="resident-evil-2-1998"></a>Resident Evil 2 (1998)

| | |
|---|---|
| Motor | Proprietário da Capcom (motor PlayStation de 1998; port Sourcenext para PC de 2006) |
| Versões testadas | Relançamento Steam (AppID 4249110, build 21744144) executando `rebirth\bio2.exe` do Steam Enhancement Pack de Mulder: Sourcenext PC v1.1.0 + Classic REbirth 1.0.9.1, SHA-256 de bio2.exe `00dd7aab0ae5d5f6afef1cb4a9071030c2e8d4edd00e5a24302a70c800c3c232` |
| Projetos | [re2coop](https://github.com/shoukyperry/re2coop) (MIT) |
| Nível de QA | automated |
| Última atualização | 2026-10-28 |

## <a id="where-things-stand"></a>Situação atual

re2coop v0.2 (protótipo) permite que dois jogadores joguem on-line por retransmissão Steam (Spacewar AppID 480) ou UDP direto. O outro jogador é um modelo real de NPC (Leon ou Claire), que caminha, corre e vira com as animações do jogo; o cliente é levado à sala do host sempre que este muda de sala. O host controla o mundo: o cliente espelha os inimigos da sala do host, seus disparos são aplicados pelo host, e os inimigos do host também o atacam. Indicadores de inimigos mortos, itens (um item pego por um some para ambos) e indicadores da história (portas, história, mapas, arquivos) são compartilhados. Inventários permanecem individuais. Cenas e chefes não são sincronizados; duas contas Steam reais ainda não jogaram juntas.

## <a id="existing-work"></a>Trabalhos existentes

- Nenhum mod cooperativo ou multiplayer do jogo de 1998 encontrado (busca na web e neste diretório, 2026-10-27). Mods listados para "Resident Evil 2" são para o remake de 2019 (RE Engine).
- Fontes de engenharia reversa compatíveis com este executável:
  - [BioRand](https://github.com/IntelOrca/biorand), `biorandmod/biorand.cpp`: hooks para este Sourcenext + Classic REbirth exato (carregar jogo, tarefas SCD, inicializar NPC).
  - [biohazard-utils](https://github.com/IntelOrca/biohazard-utils): formatos dos opcodes SCD (`Script/Opcodes/SceEmSetOpcode.cs`, `OpcodeV2.cs`, `Bio2ConstantTable.cs`) e `src/hitscan/Re2Binder.cs` (palavra de entrada 0x988604).
  - [MeganGrass/Resident-Evil-2-Starter-Kit](https://github.com/MeganGrass/Resident-Evil-2-Starter-Kit), `source/bio2/data.h`: estruturas PS1. O executável PC mantém esses formatos (`tagGLOBAL`, `PLAYER_WORK`, `ENEMY_WORK`, `SCE_AOT`, `IN_DOOR_WORK`); offsets conferidos em execução.
  - [yanmingsohu/re2re](https://github.com/yanmingsohu/re2re) é uma desmontagem de outra compilação bio2.exe (endereços não coincidem); não utilizada.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

Sem código de rede. Tudo depende de um global `G` (tagGLOBAL) em 0x9864E0, organizado exatamente como no PS1; os cabeçalhos de estruturas PS1 compilados para i386 dão os offsets PC. Mapa completo: [NOTES.md](NOTES.md).

- **Jogador:** `G.Player` em 0x989EF0. `Routine_0` = 1 enquanto o jogador tem controle; `Routine_1` fornece o movimento: 0 repouso, 1 caminhada, 2 corrida, 3 passo para trás.
- **Entidades:** `G.pEnemy[34]` em 0x98A10C ([0] jogador, [1] parceiro, [2+id] identificador em). O ciclo por quadro começa em 0x4C03CA e chama `[G + type*4 + 0x3C74]` em 0x4C0449.
- **Scripts (SCD):** tabela de tratadores em 0x53AE10, um por opcode, cada um recebendo `SCE_TASK*` (Data em +0x1C, entidade de trabalho em +0x154). Chamar um tratador com tarefa simulada executa um opcode, como `em_set` (0x44) para criar NPC ou `plc_dest` (0x40) para fazê-lo andar. `em_set` é assíncrono: enquanto o EMD carrega (`[0x68A204]+0x13`), retorna sem consumir o opcode; o chamador precisa tentar no próximo quadro.
- **Portas:** o tratador AOT (0x4E9460), após conferir chaves, termina com três gravações: `[0x991F80] = 1`, `G.pSce_aot_on (0x988848) = &IN_DOOR_WORK`, `G.Stop_flg |= 0xFF000000`. A máquina de estados então reproduz a porta e carrega sala ou fase. Um `IN_DOOR_WORK` destrancado artificial pode, portanto, teleportar o jogador a qualquer lugar.
- **Entrada:** a rotina de controle 0x4D0F30 recebe o controle bruto no formato PS1 de `call 0x43BB00` (em 0x4D0F53), mapeia pela tabela de teclas em 0x5338D8 para 0x988604 (mantidas) e 0x988608 (pressionadas). Classic REbirth não altera esse caminho; um hook na chamada dá controle completo a um bot.
- **Instância única:** executável e Classic REbirth recusam segunda cópia pelos mutexes `bio2.658b45ea117473d4.game` e `re2cr.aiory0n5jnqf3r7a.game`. Veja o ambiente de teste abaixo.

## <a id="what-we-changed"></a>O que alteramos

re2coop é plugin ASI carregado pelo Ultimate ASI Loader (`dsound.dll`) do pacote. Só acrescenta arquivos e confere os bytes que altera; em outro executável, desativa-se.

- **Avatar remoto:** cria NPC tipo 0x50 (Leon RPD) ou 0x51 (Claire) no espaço em 31 com o tratador `em_set`. Executa de um trampolim no começo do ciclo de entidades por quadro, onde os opcodes de scripts também rodam. Criar no hook de controle causava falha em 0x4C0669: a passagem de sombras lia `pKage_work` antes da inicialização do NPC. A rotina de NPC 0x4EF110 também ignora entidades com bit 0x20000000 de `Stop_flg` ativo, como ocorre fora do ciclo.
- **Movimento do avatar:**
  - Espelha o movimento remoto com `plc_dest` (tipo 4 caminhada, 5 corrida), atualiza o destino a cada atualização e mantém o NPC parado (Routine 4/6) na orientação remota.
  - Tipo 8 (passo para trás) não faz nada nesses NPCs; recuar aparece como caminhada.
  - O NPC salta para a posição remota acima de 1200 unidades ou após ficar bloqueado por 30 atualizações.
  - O indicador de chegada definido por `plc_dest` nos indicadores da sala (0x98EB6C) é salvo e restaurado em torno da rotina do NPC; scripts da sala nunca o veem.
- **Mudanças de sala:** pEnemy é reconstruído; no primeiro quadro o plugin esquece o representante e limpa seu espaço, oculta (`Be_flg` bit 0) enquanto o outro jogador está fora e recria quando ambos compartilham sala.
- **Seguir host:** se o host estiver em outra sala há 1,5 s e o cliente tiver controle, este passa por porta destrancada artificial até o ponto de entrada, câmera e andar do host. Também cruza fases (testado de fase 0 sala 0x0F até fase 5 sala 0x12).
- **Indicadores de mortes:** os dois arrays de 32 bytes verificados por `em_set` (0x98EB74) vão do host ao cliente a cada segundo, aceitos como estão. Na v0.1 eram combinados por OR nos dois sentidos, misturando mortes de dois salvamentos no mundo do host.
- **Inimigos (autoridade do host):**
  - O host envia os inimigos da sala 15 vezes por segundo (espaço, tipo, rotina, posição, vida, campos de dano). O cliente força suas cópias para esse estado antes de cada atualização do ciclo, mata quando os do host morrem e exclui seu jogador local da IA enquanto o host está na sala.
  - Golpes do cliente (o `sub [enemy+0x156]` de cada rotina de dano) são enviados ao host e aplicados uma vez cada.
  - Ataques inimigos ao representante do cliente são capturados no host em `Pl_damage` (0x4DCA40) e reproduzidos no cliente.
  - Funciona com inimigos criados pelo script da sala (5 tipos testados), não só criações de depuração.
- **Progresso compartilhado (itens e história):**
  - Faixas SaveData: +0x390..0x3D0 (Scenario_flg, Common_flg), +0x418..0x484 (Item_flg e array de itens das fases 4+, Item_c_flg, mapas), +0x584..0x598 (File_flg, Zapping_flg, Key_flg, conferido nas portas). Não inclui Room_flg, indicadores de mortes ou Pri_be_flg.
  - O host envia sua cópia 4 vezes por segundo; o cliente aceita.
  - As funções Flg_on (0x503120) e Flg_off (0x503140) são substituídas pelas do plugin. No cliente, registram cada bit alterado em faixa compartilhada e o enviam até aparecer na cópia do host. Comparar memória perderia coleta durante mensagem ou porta (o ciclo para) e confundiria carregar salvamento com alterações.
  - Coletar define o indicador por Flg_on (0x4FDFFB) e oculta o modelo (object work 0x98A61C + MD1 * 0x1F8, `Be_flg` = 0). Quando o pacote remoto define indicador de item da sala atual, o plugin faz o mesmo, removendo-o imediatamente.
  - Duas gravações ignoram Flg_on: byte de quebra-cabeça em 0x98EBD0 e Zapping_flg; nelas prevalece o host.
- **Rede:**
  - Steam: sala Spacewar só para amigos. O cliente encontra automaticamente o amigo hospedando pela lista, ou usa convite ou ID de sala. Tráfego ISteamNetworkingMessages sem garantia de entrega a 30 Hz.
  - UDP: IP direto para LAN ou VPN.
  - Todo pacote leva checksum do código do executável; parceiro com outra compilação é ignorado.
  - O plugin força `SteamAppId=480`, pois jogo iniciado pelo Steam herda 4249110; jogadores iniciados de formas diferentes não se veriam.
  - `steam_api.dll` carrega no primeiro quadro, não em DllMain (trava do carregador).

## <a id="qa"></a>QA

Duas instâncias reais em um PC, controladas por bots pelo bloco de memória compartilhada do plugin. Os bots escrevem o controle bruto por Python; nos testes de portas, teleportam o jogador para a zona da porta (posição, posição anterior e `Sca_old`).

- **Ambiente de teste:**
  - Duas cópias de `rebirth\`.
  - Em `ddraw.dll` de cada cópia (com backup), um byte dos dois nomes de mutex Classic REbirth é alterado.
  - `[test] multi_instance=1` em re2coop.ini faz o plugin renomear o mutex do executável em memória.
- **Steam:** duas contas não podem rodar no mesmo PC; um simulador de `steam_api.dll` de teste (aproximadamente 200 linhas) implementa as 30 exportações planas usadas pelo plugin em UDP localhost. Reproduz os comportamentos Steam sobre os quais o guia alerta: identidade do remetente no offset 12, resultados de sala duplicados e mensagens retidas até AcceptSessionWithUser.
- **Steam real:** conferido com uma conta. Inicialização, criação de sala e presença avançada funcionam; jogo com duas contas reais ainda não executado.
- **Suíte (`qa_suite.py`, 33 verificações):**
  - conexão nos dois sentidos;
  - representantes visíveis, com tipos corretos;
  - representante caminha e corre junto ao host, estabiliza abaixo de 300 unidades e nunca ultrapassa a distância de reposicionamento;
  - indicadores de mortes chegam ao outro jogador;
  - cliente sai por porta: host o oculta, cliente fica sem representante, retorna e ambos reaparecem;
  - seguir host por porta: cliente com controle, representantes visíveis;
  - zumbis criados no host: espelhados no cliente, mortos nos dois;
  - nenhuma falha nos logs.
- **Outros testes em `qa/`:**
  - `enemytest`, `mirrortest --shoot`, `hittest` (11 verificações cada), `multitest` (17), `attacktest` (8), `roomtest` (zumbis próprios de sala, 11): capturas de inimigos, espelhamento, golpes do cliente, vários zumbis, inimigos do host atacando o cliente.
  - `storytest` (16): cliente recebe indicadores do host; bits definidos ou limpos por qualquer lado pelas funções do jogo chegam ao outro; item coletado pelo host desaparece quando cliente reentra.
  - `pickuptest [client|host]` (13): um jogador coleta fitas de tinta da fase 0 sala 0x06 pelos botões (toque em Cross, depois Square); outro recebe o indicador, modelo some na mesma sala, não pode coletar e nenhum salvamento é escrito (a máquina de escrever ocupa o mesmo local).
- `[test] loss=N` descarta N% dos pacotes enviados por cada cópia.

Últimos resultados, 2026-10-28 (ambos os transportes):

```
SUITE udp: PASS 33/33          SUITE steam-mock: PASS 33/33
STORYTEST: PASS 16/16          (udp, steam-mock)
PICKUPTEST: PASS 13/13         (client and host picking, udp and steam-mock)
```

Antes, na mesma noite: enemytest, mirrortest e hittest 11/11, multitest 17/17, attacktest 8/8, roomtest 11/11 nos dois transportes. Com perda de 25%, tudo passou; com 30%, `qa_suite` ficou 32/33; com 50%, 31/33: o representante fica muito atrás do host sob perdas intensas.

A travessia entre fases foi executada uma vez manualmente: cliente carregou salvamento na fase 0 sala 0x0F, foi levado à fase 5 sala 0x12 e manteve o controle depois.

## <a id="how-to-play"></a>Como jogar

Versão v0.2 em [shoukyperry/re2coop](https://github.com/shoukyperry/re2coop/releases). O pacote tem `installer-hote.bat` e `installer-invite.bat`; localizam o jogo nas bibliotecas Steam, conferem hash e adicionam três arquivos a `rebirth\`. O host carrega um salvamento; o cliente carrega um (de preferência o mesmo) e entra automaticamente no amigo Steam que hospeda, recebendo o progresso do host. Ambos precisam da mesma versão (v0.2 não conversa com v0.1).

## <a id="known-issues"></a>Problemas conhecidos

- Cenas e chefes não sincronizados; animação de agarrão não é mostrada no cliente.
- Inventários individuais.
- Byte de quebra-cabeça (0x98EBD0) e Zapping_flg são escritos sem as funções de indicadores; alterações do cliente são sobrescritas pelo host.
- Sob perda intensa (30% ou mais), o representante pode ficar muito atrás.
- Ao chegar seguindo o host, ambos podem ocupar o mesmo lugar.
- Steam mostra ambos jogando "Spacewar".
- Não testados: duas contas Steam reais, salas de cenas, salas que usam espaço em 31, partes de Ada e Sherry, morte e fim de jogo, inimigos além dos cinco tipos testados.

## <a id="next-steps"></a>Próximos passos

1. Execução Steam real com duas contas.
2. Cenas e chefes; mostrar agarrões no cliente.
3. Trechos com parceiros: deixar o jogador 2 controlar Ada ou Sherry quando o espaço de parceiro do host estiver ocupado.
4. Representante sob perda intensa de pacotes.
