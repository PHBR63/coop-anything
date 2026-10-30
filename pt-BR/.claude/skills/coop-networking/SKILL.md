---
name: coop-networking
description: "Escolher e implementar rede para um mod cooperativo: modelo de sincronização, biblioteca de transporte e conexão entre amigos sem redirecionamento de portas (retransmissão Steam Spacewar, EOS, VPN), além de adaptar código de rede UDP existente a um retransmissor."
---

<a id="co-op-networking"></a>
# Rede para modo cooperativo

- Modelo de sincronização: sincronização de estado com autoridade do host para a maioria dos motores de jogos de um jogador; lockstep somente para jogos determinísticos.
- Transporte: ENet, GameNetworkingSockets, Steam Networking Messages, EOS P2P, LiteNetLib ou o próprio código de rede do motor.
- Sem redirecionar portas: retransmissão pelo Steam via AppID 480 (os jogadores executam o Steam e aparecem como "playing Spacewar"); uma implementação simulada de `steam_api.dll` para testes em um PC.
- Código de rede UDP existente: um retransmissor local junto ao jogo, um socket por conexão remota no host e identificadores de conexão para permitir reconexões nas mudanças de mapa.
- Sempre teste simulando latência e perda de pacotes.

Detalhes: `playbook/networking.md`, `playbook/networking-steam-spacewar.md`.
