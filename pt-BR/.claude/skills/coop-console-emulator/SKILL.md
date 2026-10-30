---
name: coop-console-emulator
description: "Adicionar modo cooperativo a jogos de console (PS1, PS2, N64, GameCube, Wii, GBA, ...) por emuladores: jogo em rede para multiplayer local, mods de sincronização de memória entre duas instâncias para jogos de um jogador e emulação de adaptador de rede para modos on-line."
---

<a id="console-co-op-through-emulators"></a>
# Modo cooperativo em consoles por emuladores

1. Confira primeiro se existe versão para PC, port para PC a partir de descompilação ou recompilação estática (`coop-decomp-port`). Código nativo é preferível à emulação para o modo cooperativo.
2. Se o jogo já tem modo cooperativo local ou em tela dividida, use o recurso de jogo em rede do emulador: as entradas são sincronizadas e ambos devem usar a mesma compilação, ROM ou ISO e configurações. Jogo remoto (Parsec, Steam Remote Play Together) é a alternativa.
3. Se o jogo tem modo on-line ou LAN, emule o adaptador de rede e procure um servidor que tenha retomado o serviço.
4. Se o jogo é apenas para um jogador, crie um mod de sincronização de memória. Um programa externo lê e escreve a RAM de duas instâncias pela interface do emulador (scripts Lua, IPC como PCSX2 PINE, acesso à memória do Dolphin) e sincroniza indicadores, itens, posições e inimigos com autoridade do host. Estude primeiro os projetos existentes (Z64Online no ModLoader64, clientes Archipelago).
5. Mapeie a RAM do jogo (bancos de cheats, rastreadores e randomizadores existentes são fontes valiosas), decida o que será compartilhado ou individual e exiba o jogador 2 como ator representante ou marcador.
6. Teste com duas instâncias do emulador em um PC, simulando latência e perda de pacotes (`coop-qa`).
7. Nunca compartilhe ROMs, ISOs ou arquivos de BIOS; cada pessoa deve extrair sua própria cópia.

Detalhes: `playbook/console-emulators.md`.
