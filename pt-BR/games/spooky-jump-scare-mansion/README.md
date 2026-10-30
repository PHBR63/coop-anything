# <a id="spookys-jump-scare-mansion-hd-renovation-2017"></a>Spooky's Jump Scare Mansion: HD Renovation (2017)

| | |
|---|---|
| Motor | Unity 2021.3, Mono, Windows x64 (BepInEx 5.4.23.5 ou MelonLoader 0.7, Harmony) |
| Versões testadas | Steam (app 577690), buildid 12368455. SHA-256 de `SpookyUnity.exe`: `ed13875fc3eab0f0afe677c3eee936e1885789b032c78ccab3a59a4c8b79b74a` |
| Projetos | Spooky Together ([spooky-together](https://github.com/multiplayereverything/spooky-together), [pré-lançamento v0.2.11](https://github.com/multiplayereverything/spooky-together/releases/tag/v0.2.11)); entrada "Spooky Together" |
| Nível de QA | automated |
| Última atualização | 2026-10-26 |

## <a id="where-things-stand"></a>Situação atual

Spooky Together permite que 2 a 4 jogadores percorram juntos a mansão: mansão básica, Endless, hospital e Dollhouse. Todos ficam na mesma sala, perseguidos pelos mesmos espécimes; a equipe compartilha chaves, itens e machado. Os finais levam a equipe inteira. Um golpe letal derruba o jogador em vez de encerrar a partida enquanto algum parceiro continuar de pé. É uma versão alpha. O autor jogou com amigos em sessões reais, e funcionou muito bem: quatro jogadores em PCs e contas Steam separados. Cada correção também tem testes por scripts com até quatro cópias do jogo. Ninguém documentou uma campanha completa ainda.

## <a id="existing-work"></a>Trabalhos existentes

Nenhum outro projeto cooperativo para este jogo foi encontrado neste diretório ou nas notas de pesquisa do autor ([`docs/research.md`](https://github.com/multiplayereverything/spooky-together/tree/main/docs)). O jogo é somente para um jogador.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Motor:** Unity Mono; a lógica fica em `SpookyUnity_Data/Managed/Assembly-CSharp.dll` e Harmony pode inserir hooks. Salas são escolhidas de uma sequência. A aleatoriedade de cada sala (portas trancadas, luzes, inversões, rotações, espécimes locais da Dollhouse) vem do gerador aleatório Unity; o mod fornece uma semente do host por sala.
- **Espécimes:** a maioria encontra o jogador lendo `SpookyCharacterController`. Alguns guardam o jogador em variável local ou campo, incluindo estado de corrotina: Spec6, Spec8, Hooked Doll, Frenzy e Nightmare.
- **Estado da partida:** indicadores de quebra-cabeças, notas, `violence` e valores de finais ficam em um armazenamento de chaves lido e escrito pelos scripts das salas. Os finais variam conforme essas chaves e as opções de espécimes e sustos.
- **Steam:** `SteamPlatformInstance` chama `SteamAPI.RestartAppIfNecessary(577690)`. Iniciar `SpookyUnity.exe` diretamente encerra logo após "Discord: init", sem erro no log. Cópias de laboratório precisam de `steam_appid.txt`; instalações reais iniciam pelo Steam.

## <a id="what-we-changed"></a>O que alteramos

A lista completa de recursos está no README e MODLOG do mod. Esta seção reúne lições aplicáveis a outros jogos.

### <a id="retarget-enemies-with-a-transpiler-including-the-player-kept-in-a-variable"></a>Redirecione os inimigos com um transpilador, incluindo o jogador guardado em variável

- **Abordagem:** o host executa todos os espécimes. Um transpilador reescreve as leituras de `.transform` do jogador em cada espécime para `Target(this)`, que retorna o jogador de pé mais próximo. Usos do jogador para vida, câmera e sons permanecem locais. Os golpes de um espécime atingem o jogador perseguido.
- **Bug (corrigido na 0.2.9):** cinco espécimes guardavam o jogador em variável local ou campo; mediam a distância ao host e ignoravam os parceiros. O transpilador agora também reescreve leituras de `.transform` de um `SpookyCharacterController` guardado em variável ou campo, incluindo estado de corrotina.
- **Comprovação:** o roteiro `enemies` conta as leituras reescritas por espécime: Spec6 8, Spec8 12, Hooked Doll 1, Frenzy 2, Nightmare 3.

### <a id="pair-the-clients-own-copy-of-a-spawned-enemy-with-the-hosts"></a>Associe a cópia de inimigo criada pelo cliente à cópia do host

- **Bug:** a criação no host geralmente chega ao cliente antes de o script da própria sala criar sua cópia. O cliente criava imediatamente um substituto e removia a cópia própria 6 s depois; scripts que a guardavam a perdiam, e `Spawned()` executava duas vezes.
- **Correção:**
  - o substituto espera até 1,5 s após a sala do cliente estar pronta;
  - a cópia própria do cliente é associada a um espécime do host ainda à espera de correspondente;
  - uma cópia própria que chega após um substituto (dentro de 10 s) o substitui.

### <a id="shared-keys-one-copy-a-checksum-repair-and-no-double-counting"></a>Chaves compartilhadas: uma cópia, reparo por checksum e nenhuma contagem dupla

- **Cópia compartilhada:** chaves da partida e inventário têm uma cópia compartilhada; alterações de qualquer jogador chegam a todos. A cada 10 s o host compara checksums com cada cliente e repara diferenças.
- **Bug:** um segmento de quebra-cabeça satisfeito pela alteração de um parceiro executava eventos em todas as máquinas; seu `AddKey` contava uma vez por jogador.
- **Correção:** um segmento satisfeito por alteração remota executa os eventos apenas visualmente, ignorando suas gravações em chaves e inventário.
- **Ações concorrentes:** a fornalha da Dollhouse relê os valores compartilhados antes de cada ação e recusa ações que já não se aplicam. As ações dos clientes são executadas em ordem na fornalha do host. Três jogadores pegando a chave simultaneamente produzem uma chave.

### <a id="turn-quit-the-game-scares-into-knock-downs"></a>Transforme sustos que fecham o jogo em derrubadas

Dois sustos fecham o jogo diretamente: a segunda perseguição de Unknown Specimen 1 e a cadeira de susto. Em modo cooperativo, viram derrubadas normais; o susto de um jogador não o remove da sessão.

### <a id="a-mutation-check-for-every-fix"></a>Uma verificação de mutação para cada correção

Cada correção tem uma opção exclusiva de laboratório (`-st-mutate <name>`) que a desativa. `scripts/mutants.ps1` executa o roteiro que protege cada correção com essa opção ativa; todas essas execuções precisam falhar. Isso comprova que o teste enxerga o bug. Há 16 opções: redirecionamento de alvos (três tipos), encaminhamento de golpes, chaves compartilhadas, golpes de armas, botões de elevador, travas obsoletas, associação de criações, fornalha, repetição de quebra-cabeças, finais perdidos, ordem de chaves para entradas tardias, mudanças visuais de salas, criações antecipadas de espécimes, finais durante carregamento de sala e finais aguardando um carregamento que nunca veio. `tests/rules-test.py` verifica o código em segundos, sem o jogo: toda operação de mensagem tem um tratador e é construída em algum lugar; todo estado estático mutável é reiniciado ou marcado; todo `catch` vazio explica por quê; e os números de versão coincidem.

## <a id="qa"></a>QA

- `scripts/run-tour.ps1 -Tour <name> [-Players 4] [-Lag <ms>] [-Steam]` inicia até quatro cópias isoladas, minimizadas e pequenas (480x270, qualidade mínima, 30 fps, prioridade abaixo do normal), sem tomar foco: host BepInEx e clientes MelonLoader ou BepInEx. Executa um roteiro por script e avalia por `tests/verify-lab.py`, que verifica:
  - as verificações do roteiro;
  - quantidade de erros;
  - tendências de heap gerenciado e quantidade de objetos;
  - dessincronização de entidades;
  - sequência de salas;
  - tempo de CPU do mod por quadro (limite 2 ms).
- Jogadores de laboratório agem como jogadores reais. Abrem portas reais, pegam o machado e cortam tábuas. Transferências forçadas ou identificadores falsos de itens quebrariam o jogo e gerariam falhas falsas.
- **v0.2.11, 4 jogadores:**
  - A suíte completa passou 29/29. Inclui atraso de 150 ms, teste prolongado por endereço LAN com atraso de 120 ms e mansões completas EM, KH e Dollhouse.
  - As 7 opções alteradas entre 0.2.10 e 0.2.11 foram reexecutadas; todas foram detectadas.
  - Lição: um roteiro curto dava à regra de inclinação do heap apenas três amostras, dentro de um dente de serra do coletor de lixo. A regra agora exige cinco; o teste prolongado avalia execuções longas.
- **v0.2.9, 4 jogadores:**
  - `rules-test.py` passa.
  - Os novos roteiros `pairing`, `furnace`, `puzzles` e `lateending` passam, junto com `enemies`, `dollprops`, `ending` e `clientending`.
  - A suíte rápida passou 13 de 15 com CPU a 97%. `axe` e `elevator` falharam sob carga e passaram nas repetições.
  - Verificação de mutação: todas as 5 novas opções foram detectadas.
  - `test-transport.ps1`: 5/5.
- **Resultados anteriores:** 0.2.8 passou a suíte rápida 11/11 e mutações 6/6. 0.2.2 passou a suíte completa 17/17, incluindo teste prolongado de 10 minutos com 4 jogadores.
- **Sessões reais:** o autor jogou com três amigos em PCs e contas Steam separados (quatro jogadores), com ótimo funcionamento. Não houve notas estruturadas; o nível permanece `automated`, não `verified-playthrough`.
- O caminho Steam usa salas Steam reais e Steam Networking Sockets entre cópias de laboratório na mesma conta, por 127.0.0.1.
- Não cobertos:
  - espécimes perseguindo parceiros em jogo real (a verificação conta leituras reescritas);
  - quebra-cabeças reais além do segmento de teste;
  - Steam entre duas contas.

## <a id="how-to-play"></a>Como jogar

1. Instale BepInEx 5.4.23 (copie `SpookyTogether.BepInEx.dll` para `BepInEx/plugins/SpookyTogether/`) ou MelonLoader 0.7 (copie `SpookyTogether.MelonLoader.dll` para `Mods/`). Downloads na [página de versões](https://github.com/multiplayereverything/spooky-together/releases).
2. Inicie pelo Steam e pressione **F5**.
3. Conecte:
   - **On-line (Steam):** hospede pelo Steam. Amigos entram pela lista de jogos Steam, por Join Game no perfil do host ou por convite.
   - **LAN / direto:** o host precisa ter TCP 27020 acessível; os demais entram pela lista de servidores LAN ou pelo endereço.
4. O host inicia a partida.

## <a id="known-issues"></a>Problemas conhecidos

- Ataques do chefe Taker são por jogador. O host decide vida do chefe, quando ele aceita golpes e o final.
- Vida, fôlego, lanterna e notas na tela são por jogador.
- Alguns objetos de quebra-cabeças só atualizam na próxima entrada na sala.
- A fornalha Dollhouse reage com pequeno atraso nos clientes com conexão lenta.
- Se o host desconectar, os clientes continuam sozinhos; não há migração de host.

## <a id="next-steps"></a>Próximos passos

- Executar sessão Steam real com duas contas.
- Jogar até um final em modo cooperativo e documentar para `verified-playthrough`.
