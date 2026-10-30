# <a id="sekiro-shadows-die-twice-2019"></a>Sekiro: Shadows Die Twice (2019)

| | |
|---|---|
| Motor | Proprietário da FromSoftware (x64, Windows), com origem compartilhada com Dark Souls III |
| Versões testadas | Steam 1.06 (`sekiro.exe` ProductVersion 1.6.0.0, timestamp PE `0x5fa3e066`, SHA-256 `637aca527538c0ec6e1f136c8ed66046e95dfbdbb1f51926e134d9916398b856`) |
| Projetos | [Sekiro Online](https://www.nexusmods.com/sekiro/mods/577) (invocações no estilo Souls, abandonado em 2021); [sekiro-coop](https://github.com/mstampfli/sekiro-coop) (protótipo contínuo para 2 jogadores, Rust) |
| Nível de QA | none (um cliente real do jogo e o simulador de par do projeto; ainda sem teste com dois clientes) |
| Última atualização | 2026-10-27 |

## <a id="where-things-stand"></a>Situação atual

Ainda não é possível jogar a história de Sekiro continuamente com um amigo. Sekiro Online oferece modo cooperativo no estilo Souls, com sinais de invocação e Steam, mas está sem manutenção desde 2021 e não foi testado por nós. sekiro-coop é a única tentativa de modo contínuo: sua rede e sincronização de eventos do mundo funcionam, mas o segundo jogador não aparece no mundo; as sondagens por inicialização abaixo mostram a dificuldade.

## <a id="existing-work"></a>Trabalhos existentes

- **Sekiro Online** (Nexus #577): v2.05, 2021-06-13. Sinais de invocação, invasões (não podem ser desativadas), 1 host e até 5 fantasmas por Steam P2P, ajuste de nível. Exige chegar primeiro ao Dilapidated Temple. A página informa que o desenvolvimento foi encerrado e menciona uma nova versão "as of 09/03/2025"; nada mais recente foi encontrado. Código fechado.
- **sekiro-coop** ([mstampfli/sekiro-coop](https://github.com/mstampfli/sekiro-coop), 6 commits, último em 2026-06-15, AGPL-3.0-or-later): DLL Rust carregada pelo [me3](https://github.com/garyttierney/me3), desvios MinHook, UDP bruto por IP direto (Steam P2P é apenas um esqueleto vazio), vida dos inimigos com autoridade do host. Seu `docs/HANDOFF.md` planeja controlar um NPC representante por um patch em `common.emevd`; o trabalho não começou.
- Não foi encontrada uma versão de Seamless Co-op (LukeYui) para Sekiro.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- O executável Steam em disco está empacotado (seção `.bind`, `.text` criptografada): padrões AOB só correspondem à imagem descriptografada na memória; buscas estáticas no arquivo não encontram nada.
- O me3 0.11.0 inicia o jogo com Arxan neutralizado (`--disable-arxan true`), bloqueia o pareamento (`--online false`) e pode redirecionar o salvamento para um arquivo separado (`--savefile`).
- O estado de personagem ao vivo é alcançado por `ChrIns` (instância de personagem):
  - handle `+0x08`, identificador do personagem `+0x68`, byte de equipe `+0x74`;
  - vida/postura `+0x1ff8 → +0x18 → +0x130/+0x134/+0x148/+0x14C`;
  - identificador de animação `+0x1ff8 → +0x10 → +0x20`;
  - posição do módulo de física `+0x1ff8 → +0x68 → +0x80`.
- O indicador global de depuração "all no update AI" fica em `debug_flags + 13` (RVA de `debug_flags` na versão 1.06: `0x3d7a369`).

## <a id="what-we-changed"></a>O que alteramos

Nada foi lançado. Todas as alterações são experimentos locais sobre sekiro-coop `1ef5fa8`, descritos em [NOTES.md](NOTES.md):

- Correções de compilação: MinHook recompilado a partir do código incluído no repositório (idêntico byte a byte ao upstream `d94c64d`), em vez da `.lib` pré-compilada.
- Uma sondagem de representante (`SEKIRO_COOP_PUPPET_PROBE=1`) fixa um inimigo e mantém sua posição física ao lado do jogador. Descobertas:
  1. Escrever a posição física **a partir da thread do jogo** (dentro do desvio de SetFlag) move o personagem na tela. A conclusão anterior de sekiro-coop de que o caminho de renderização ignorava essas escritas veio de escritas feitas em uma thread separada de 60 Hz.
  2. Mudar o byte de equipe (6 -> 2) não impede o representante de atacar; congelar toda a IA impede.
  3. O jogo continua puxando o personagem para uma posição inicial armazenada: durante uma pausa de 1 s nas escritas, ele voltou ao ponto de criação, e cerca de 25 a 80% das escritas foram revertidas. Escrever também na cópia `ChrIns+0x1060` não ajudou; `+0x1050` não é mantido pelo jogo. Alterar diretamente a posição entra em conflito com o motor; o representante precisa das chamadas nativas de movimento/teletransporte, animação e IA por personagem.
  4. Escrever a altura do jogador nas encostas fazia a física expulsar o representante a cada quadro (o FPS caiu para cerca de 15); manter a altura do próprio jogo o fazia cair através do mundo.
- A análise offline de uma imagem de memória da versão 1.06 (mantida localmente) encontrou os comandos nativos de scripts (`EventEntityCommandUtil::ChrCmd_*`): EnableLogic por personagem (bit 0 de `[ChrIns+0x50]+0x190`), SetDisableGravity, SetDisableMapHit e o teletransporte nativo `ChrIns->vt[+0x6A0](pos, rot, 1, 0)`. As RVAs estão em [NOTES.md](NOTES.md).
- A versão v3 do representante usa essas chamadas: IA desligada somente para ele, teletransporte nativo a cada 500 ms (ou quando a distância passa de 2 m) e pequenos passos de física nos intervalos. Resultado no PC do usuário: o representante segue suavemente 3 m à frente, não ataca, mantém o FPS normal e quase não pisca. Teletransportar a cada quadro causava cintilação.
- Controle pela rede: o representante segue a posição remota recebida em PlayerSnapshot (testado com o simulador de par reproduzindo o próprio trajeto do jogador). Rotação: a física em +0x70 contém `[0, yaw, 0, 0]` (radianos), yaw = atan2(-dx, -dz). Com a redefinição nativa da animação (`0x9f4c60`) a cada 2 s e teletransporte nativo a cada 50 ms, o representante anda e corre com suas animações de locomoção e olha na direção do deslocamento.
- Corrigido em sekiro-coop: personagens liberados continuavam no registro e derrubavam a transmissão de inimigos do host após morte/recarregamento; o simulador agora responde às novas tentativas de negociação inicial.

## <a id="qa"></a>QA

- Plano de dados do próprio sekiro-coop, reproduzido em um PC contra seu `peer-simulator` por loopback: sessão estabelecida, snapshots remotos e eventos de indicadores/efeitos recebidos, eco do estado dos inimigos do host resolvido para todos os inimigos (`matched=2 unmatched_count=0`). Sem encerramento por dessincronização nem falha.
- Ainda não há teste com dois clientes nem testes com bots; o nível de QA permanece `none`.

## <a id="how-to-play"></a>Como jogar

Ainda não é jogável.

## <a id="known-issues"></a>Problemas conhecidos

- O segundo jogador está invisível (sekiro-coop).
- A conexão é apenas por IP direto, sem travessia de NAT.

## <a id="next-steps"></a>Próximos passos

1. Enviar ação/animação em PlayerSnapshot para exibir ataques, defesas e saltos (a rotação já funciona: o representante vira com o jogador remoto, inclusive parado, e interrompe o ciclo de corrida ao parar).
2. Localizar a função nativa de reprodução de animações pela mesma análise de imagem, para reproduzir as animações do jogador remoto; depois dar ao representante a aparência do jogador (espaços de jogadores remotos da linhagem DS3).
3. Substituir UDP bruto pela retransmissão Steam Spacewar (playbook/networking-steam-spacewar.md).
4. Testes com bots em dois clientes (playbook/automated-qa.md).
