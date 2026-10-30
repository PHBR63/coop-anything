# <a id="tiberium-wars-mission-script-survey-co-op-planning"></a>Levantamento dos scripts de missões de Tiberium Wars (planejamento cooperativo)

Gerado em 2026-10-18 por `tools/mapscripts.py` a partir dos 39 mapas de campanha em `SP\1.0\SPMaps.big` (Steam 1.10). Decodifica as listas de scripts de cada mapa (formato do OpenSAGE) e conta todas as condições e ações cujos argumentos nomeiam o lado humano da campanha, uma de suas equipes ou um marcador `<Local Player...>`. As contagens representam itens de scripts, não a frequência de execução.

## <a id="summary"></a>Resumo

- Controle compartilhado (ambos os humanos no lado da campanha): **não é necessário editar mapas**. Os scripts veem exatamente o lado para o qual foram escritos. O prólogo percorreu as etapas do tutorial sem alterações.
- Como as missões terminam: todas terminam por objetivos e scripts, principalmente eliminando os lados inimigos (`PLAYER_KILL`), para a verificação do último lado sobrevivente do motor declarar a vitória. Apenas GDI 3-3 usa `VICTORY`/`DEFEAT` explícitos e GDI 3-4 usa `QUICKVICTORY`. O modo cooperativo precisa manter essa verificação do motor ativa (feito em 0.0.5, veja NOTES).
- Uma facção por jogador: toda missão referencia o lado humano de 14 a 174 vezes. Quase todas as referências pertencem a sete tipos (tabela abaixo), então parece viável uma **regra genérica do motor para cada tipo**, em vez de editar 39 mapas manualmente. As necessidades de cada regra estão na seção de facções próprias abaixo.
- `<Local Player>` aparece em 18 das 39 missões (412 referências). Na lógica lockstep precisa significar o lado da campanha nos dois PCs; caso contrário, os jogos avaliariam jogadores diferentes e perderiam sincronização. Com controle compartilhado, o jogador local dos dois PCs já é o lado da campanha.

## <a id="kinds-of-references"></a>Tipos de referências

| Categoria | referências | missões |
|---|---|---|
| Verificações do lado humano (qualquer unidade/estrutura, em área, pertencimento, contagens) | 647 | 39 |
| Verificações de contato com o lado humano (atacado por, descoberto, avistado) | 334 | 32 |
| Unidades/estruturas entregues ao lado humano (transferência, equipes de reforço, criação) | 276 | 29 |
| Dinheiro (definir, conceder, limitar) | 128 | 37 |
| Permissões de tecnologia/construção, poderes, melhorias | 279 | 33 |
| Revelação do mapa | 199 | 32 |
| Diplomacia e seleção de alvos pela IA | 139 | 26 |
| (entre todos os anteriores) escrito como `<Local Player>` em vez do nome do lado | 412 | 18 |

Não incluídos acima (menos numerosos, principalmente apresentação): sons em uma equipe, contadores de eliminações, referências a objetos, seleção de objetos, eventos de radar e indicadores de painel (cerca de 110 referências).

## <a id="own-factions-what-each-kind-would-need"></a>Facções próprias: o que cada tipo exigiria

Esboço do plano: o jogador 2 recebe um segundo lado humano, clonado do lado da campanha e aliado a ele; o lado da campanha continua sendo o jogador 1. Depois, no motor e sem editar mapas:

| Tipo | Regra para dois lados humanos | Risco |
|---|---|---|
| Verificações do lado humano | existência e presença em área: verdadeiro se **qualquer** lado satisfizer; comparações de contagem (`PLAYER_HAS_OBJECT_COMPARISON`, usadas em verificações de derrota como ter 0 estruturas): **soma** dos dois lados | é preciso ler o operador para distinguir perda total de possuir ao menos N; a soma cobre os dois casos |
| Verificações de contato (atacado por, descoberto, avistado) | qualquer lado | baixo |
| Unidades entregues ao lado humano | por padrão, jogador 1; divisão opcional (alternar equipes ou conforme a chegada do reforço) | experiência de cada missão: reforços são o principal desejo do segundo jogador |
| Dinheiro | dividir ou duplicar concessões (opção); `SET_MONEY` define para ambos | equilíbrio, não correção |
| Tecnologia, poderes, melhorias | aplicar aos dois lados | baixo |
| Revelação do mapa | ambos os lados (a cobertura do mapa já é compartilhada entre aliados) | baixo |
| Diplomacia, seleção de alvos pela IA | aplicar a ambos; o inimigo preferencial da IA escolhe qualquer um | baixo |
| `<Local Player>` | sempre o lado da campanha (jogador 1) na lógica; apresentação (câmera, EVA) continua por PC | precisa vir antes de tudo, ou o jogo perde sincronização |

Unidades iniciais: a maioria dos mapas posiciona previamente de 1 a 117 objetos para o lado humano (tabela abaixo); eles poderiam ser divididos entre os lados no carregamento (por exemplo, alternando esquadrões) ou mantidos no jogador 1.

## <a id="per-mission"></a>Por missão

| Missão | lado humano | scripts | refs. ao lado humano | via `<Local Player>` | VICTORY/DEFEAT explícitos | objetos humanos pré-posicionados |
|---|---|---|---|---|---|---|
| aliens_1_1_london | Plyr_Alien_A | 106 | 28 | 27 | 0 | 17 |
| aliens_1_2_munich | Plyr_Alien_A | 97 | 50 | 48 | 0 | 4 |
| aliens_1_3_croatia | Plyr_Alien_A | 30 | 15 | 14 | 0 | 11 |
| aliens_1_5_italy | Plyr_Alien_A | 102 | 28 | 7 | 0 | 49 |
| gdi_0_1_prologue | GDI_a | 262 | 102 | 17 | 0 | 1 |
| gdi_1_1_pentagon | Plyr_GDI_a | 166 | 54 | 0 | 0 | 7 |
| gdi_1_2_langley | Plyr_Gdi_a | 103 | 62 | 0 | 0 | 1 |
| gdi_1_3_hampton | Plyr_GDI_a | 66 | 17 | 0 | 0 | 25 |
| gdi_1_4_white_house | Plyr_GDI_A | 136 | 64 | 62 | 0 | 6 |
| gdi_2_1_weapons_factory | Player_GDI | 96 | 51 | 0 | 0 | 5 |
| gdi_2_2_nod_port | PlyrGDI_A | 234 | 49 | 0 | 0 | 5 |
| gdi_2_4_nuke_facility | Plyrfactiongdi | 135 | 46 | 0 | 0 | 11 |
| gdi_3_1_albania | PlyrGDI_A | 219 | 27 | 0 | 0 | 117 |
| gdi_3_3_croatia | PlyrGDI_A | 313 | 89 | 0 | 2 | 5 |
| gdi_3_4_sarajevo | PlyrGDI_A | 251 | 53 | 0 | 1 | 14 |
| gdi_4_1_munich_outskirts | PlyrGDI_A | 310 | 14 | 0 | 0 | 8 |
| gdi_4_2_stuttgart | PlyrGDI_A | 217 | 118 | 0 | 0 | 2 |
| gdi_4_3_cologne | PlyrGDI_A | 187 | 57 | 0 | 0 | 1 |
| gdi_4_4_berne | PlyrGDI_A | 138 | 40 | 0 | 0 | 18 |
| gdi_5_1_tower | PlyrGDI_A | 174 | 52 | 6 | 0 | 2 |
| gdi_5_2_relay_node | PlyrGDI_A | 179 | 77 | 7 | 0 | 8 |
| nod_0_1_prologue | Nod_a | 145 | 45 | 8 | 0 | 3 |
| nod_1_1_white_house | Plyr_NOD_A | 226 | 40 | 40 | 0 | 16 |
| nod_1_2_andrews_afb | NOD_A | 229 | 133 | 108 | 0 | 10 |
| nod_1_3_hampton | Plyr_Nod_a | 72 | 37 | 1 | 0 | 20 |
| nod_1_4_dccity | Plyr_N_a | 88 | 34 | 0 | 0 | 14 |
| nod_2_1_brazilianjungle | Nod_a | 130 | 35 | 5 | 0 | 34 |
| nod_2_3_coastal_brazil | Nod_a | 189 | 37 | 2 | 0 | 29 |
| nod_3_1_slovenia | PlyrNOD_A | 212 | 73 | 2 | 0 | 2 |
| nod_3_2_sarajevo | PlyrNOD_A | 305 | 85 | 0 | 0 | 13 |
| nod_4_1_broken_hill | PlyrNOD_A | 231 | 66 | 0 | 0 | 14 |
| nod_4_2_sydney_west | NOD_A | 119 | 58 | 27 | 0 | 7 |
| nod_4_4_sydney_interior | NOD_A | 111 | 25 | 0 | 0 | 37 |
| nod_4_5_ayers_rock | NOD_A | 139 | 85 | 17 | 0 | 6 |
| nod_5_1_nuke_recovery | Plyrfactionnod | 95 | 28 | 0 | 0 | 11 |
| nod_5_2_mapkey | Plyr_Nod_a | 62 | 25 | 0 | 0 | 9 |
| nod_5_4_operation_stiletto | PlyrNOD_A | 173 | 174 | 0 | 0 | 9 |
| nod_5_5_the_tower | Plyr_N_a | 84 | 18 | 0 | 0 | 8 |
| tutorial_pc | PlyrGDI_Blue | 85 | 47 | 14 | 0 | 1 |
