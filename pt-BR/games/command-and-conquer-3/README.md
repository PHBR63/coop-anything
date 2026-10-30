# <a id="command--conquer-3-tiberium-wars-2007-and-kanes-wrath-2008"></a>Command & Conquer 3: Tiberium Wars (2007) e Kane's Wrath (2008)

| | |
|---|---|
| Motor | SAGE (linhagem de Generals; época de C&C3), x86 |
| Versões testadas | Steam Tiberium Wars 1.10 (buildid 17447444, SHA-256 de `RetailExe\1.10\cnc3game.dat` `af568a89...0d141`; a variante C&C Online `ade9f5b6...a3543` difere apenas no cabeçalho PE: opção large-address-aware e checksum). Kane's Wrath 1.3 identificado, ainda sem trabalho. |
| Projetos | Protótipo de campanha cooperativa (proxy `dinput8.dll`), não publicado, no ambiente de trabalho do usuário; notas em [NOTES.md](NOTES.md) |
| Nível de QA | community-reports (usuário + amigo jogaram a maior parte da missão GDI 1 on-line); testes básicos automatizados com dois clientes em um PC |
| Última atualização | 2026-10-18 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores conseguem jogar juntos uma missão da campanha de Tiberium Wars: um hospeda uma partida multiplayer normal (C&C Online ou LAN), o outro entra, e ambos recebem a missão da campanha com suas próprias facções, scripts, IA, objetivos e cenas durante a missão. Os dois controlam a mesma facção da campanha (unidades e dinheiro compartilhados). Testado pelo usuário e um amigo pelo C&C Online na missão GDI 1 (prólogo): ambos tinham controle completo de unidades, construção e posicionamento. É possível vencer missões, e um fluxo experimental avança os dois PCs para a próxima missão (ainda não testado por pessoas). Vídeos de instruções e facções próprias por jogador não estão prontos. Kane's Wrath tem a mesma estrutura de motor, mas ainda não recebeu um port.

## <a id="existing-work"></a>Trabalhos existentes

Pesquisados em 2026-10-17: este repositório, busca na web e busca de repositórios GitHub; as páginas ModDB estavam atrás de uma verificação Cloudflare (somente texto dos resultados de busca).

- Nenhuma campanha cooperativa oficial para PC em nenhum dos jogos ([resposta Revora](https://forums.revora.net/topic/100755-how-to-play-c-c-3-campaign-co-op-please-help/)). A versão Xbox 360 tinha cooperação contra IA, não a história ([Co-Optimus](https://www.co-optimus.com/game/181/xbox-360/command-and-conquer-3-tiberium-wars.html)).
- Existem missões cooperativas da comunidade como mapas multiplayer personalizados, não a campanha oficial: [COOP Evacuation](https://www.moddb.com/games/cc-tiberium-wars/addons/coop-evacuation-co-operative-mission), [pacote Boyle's Legacy](https://forums.cncnz.com/topic/16232-boyles-legacy-co-op-mission-pack-re-released/), [Co-Op Tiberian Sun Map Pack](https://www.moddb.com/mods/co-op-tiberian-sun-map-pack) (exige Tiberium Essence).
- Não encontrado nessas buscas: qualquer campanha cooperativa implementada no motor de C&C3 ou Kane's Wrath.
- Código-fonte de motor relacionado: a publicação GPL de Generals Zero Hour pela EA ([electronicarts/CnC_Generals_Zero_Hour](https://github.com/electronicarts/CnC_Generals_Zero_Hour)) e [OpenSAGE](https://github.com/OpenSAGE/OpenSAGE) (formato dos mapas) foram as referências principais.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Instalação:** `CNC3.exe` é um inicializador; o jogo real é `RetailExe\1.10\cnc3game.dat`, iniciado como `cnc3game.dat -config "<install>\CNC3_english_1.10.SkuDef"`. `-win`, `-xres`, `-yres` funcionam. Os executáveis Steam de 2025 não estão empacotados. C&C Online ("Tacitus") é um proxy `dsound.dll` e não precisa de inicializador.
- **Mapas:** mapas da campanha ficam em `SP\1.0\SPMaps.big` como `.map` bruto (RefPack, `EAR\0`, RefPack, blocos `CkMp`; organização como no OpenSAGE), além de `map.bin` compilado. Cada mapa da campanha tem uma facção humana e várias facções de IA nomeadas com scripts próprios.
- **Código de rede:** lockstep, da linhagem de Generals. A sala LAN usa somente broadcast (portas 8086-8093) e identifica jogadores por IP. Comandos carregam um índice de jogador; os comandos de uma vaga só são aceitos se nenhuma outra já atuar pelo mesmo jogador (proteção contra falsificação de identidade; consulte seção 12 de NOTES).
- **Início da partida:** `startNewGame` com um GameInfo de sala exclui equipes marcadas, remove todas as facções do mapa exceto civis/creeps (`prepareForMP_or_Skirmish`) e cria facções `Player_N` a partir das vagas. O mapeamento vaga -> Player é o nome do jogador guardado na vaga.
- **Vitória:** uma verificação de vitória de escaramuça considera os jogadores das vagas; mapas da campanha decidem vitória e derrota pelos próprios scripts. Após partidas on-line, um relatório de resultados é enviado ao serviço de classificação.

## <a id="what-we-changed"></a>O que alteramos

Tudo em um proxy `dinput8.dll`; cada ponto de patch é conferido com seus bytes esperados, e a DLL não faz nada em uma compilação desconhecida. Os endereços estão em NOTES.md.

- **Mapa da campanha em partida de sala:** o mapa da sala é substituído pela missão escolhida em ambos os clientes; remoção de facções, facções das vagas e exclusão de equipes são puladas; a facção humana da campanha é marcada como local; cada vaga humana recebe seu nome; a verificação de vitória de escaramuça fica desativada.
- **Ordens do convidado eram descartadas:** a proteção de identidade no recebimento detectava a segunda vaga atuando pela facção da campanha e descartava todos os comandos, até no PC do próprio convidado (descoberto registrando comandos criados pela interface, enviados e processados por quadro nos dois clientes). A verificação é flexibilizada em partidas cooperativas.
- **Não era possível vencer missões:** elas terminam pelo mecanismo clássico de SAGE (scripts eliminam facções inimigas, e a verificação de vitória declara vencedora a última facção). Essa verificação estava desativada no modo cooperativo porque a facção da campanha falhava na regra de eliminação multiplayer no início. Agora a verificação roda, mas em modo cooperativo uma facção só é derrotada quando os scripts da missão a eliminam: a regra de "não sobrou nada" também eliminava facções aliadas de IA (e destruía seus prédios) na primeira verificação. Teste: facções inimigas eliminadas em um quadro fixo nos dois clientes -> VICTORY em ambos.
- **Fluxo de missões (experimental):** a missão atual fica em um arquivo no perfil cooperativo; após a vitória, ambos os clientes a avançam para a próxima missão, e a próxima partida da sala a carrega.
- **Seleção compartilhada:** uma ordem se aplica à seleção lógica do jogador, compartilhada pelas duas pessoas. Cada cliente mantém suas próprias mensagens de seleção e as reenvia antes da próxima ordem caso a seleção do parceiro tenha mudado no intervalo.
- **Encerramento inesperado ao sair de uma partida on-line:** o relatório de resultados criava um registro por jogador e corrompia o heap com a organização de jogadores do modo cooperativo (minidumps WER dos dois jogadores). Partidas cooperativas não são relatadas.
- **Estrutura de testes:** duas instâncias do jogo em um PC por LAN (IP loopback por instância, broadcasts reenviados como unicast, `SIO_UDP_CONNRESET` desativado), cada uma com AppData próprio, mantidas minimizadas, mas "ativas", controladas por mensagens enviadas às janelas e com capturas de tela internas (hook D3D9 em `Present`).

## <a id="qa"></a>QA

- Automatizado (dois clientes reais em um PC, LAN): início da missão sincronizado em ambos (capturas correspondentes, quadros lógicos avançando, fluxo de comandos idêntico), comandos do convidado executados nos dois clientes, restauração da seleção compartilhada (host seleciona, convidado seleciona, host dá ordem: a seleção do host é reenviada primeiro), saída da partida de volta à sala nos dois clientes. São testes básicos com evidências em logs, ainda não uma suíte passa/falha com controles negativos; a estrutura não consegue produzir ordens de movimento pelo mouse (ordens pelo teclado funcionam).
- Teste humano, C&C Online, dois PCs, missão GDI 1: controle compartilhado completo para ambos, sem travamentos ou divergências. Uma peculiaridade: bombardeiros Nod danificaram, mas não destruíram a usina inicial, então uma etapa do tutorial teve de ser concluída manualmente. Não se sabe se é aleatório ou causado pelo modo cooperativo (por exemplo, dificuldade da campanha não aplicada nas partidas de sala).

## <a id="how-to-play"></a>Como jogar

Não publicado. Pacote do usuário: execute `Setup.bat` (localiza a instalação Steam, faz uma cópia separada com hardlinks e a DLL, memoriza pastas), escolha a mesma missão nos dois PCs, clique em Play e hospede uma partida privada não ranqueada para 2 jogadores em qualquer mapa no C&C Online (ou LAN).

## <a id="known-issues"></a>Problemas conhecidos

- Fluxo de missões: depois da vitória, ambos voltam à sala e hospedam uma nova partida para a próxima missão; sem instruções ou vídeos entre missões; sem salvamentos.
- Missão GDI 2 (Pentágono), sem ninguém jogando: derrota após cerca de 40 s quando Nod destrói uma usina aliada (script de derrota da própria missão). Provavelmente normal para jogador inativo; não comparado com uma execução para um jogador. (Um bug cooperativo anterior que causava derrota após 3 s foi corrigido; consulte seção 14 de NOTES.)
- Grupos de controle são compartilhados; estatísticas após a partida mostram nomes estranhos de jogadores.

## <a id="next-steps"></a>Próximos passos

- Vídeos de instruções entre missões; salvamentos.
- Facção própria por jogador: consulte [mission-survey.md](mission-survey.md) para o levantamento de scripts de todas as 39 missões e as regras genéricas sugeridas (e a armadilha de dessincronização `<Local Player>`).
- Conferir com qual dificuldade de campanha as partidas de sala rodam (prólogo: dinheiro e forças de ataque Nod diferem).
- Port para Kane's Wrath (mesmos pontos de integração, endereços diferentes).
