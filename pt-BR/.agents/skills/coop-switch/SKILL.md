---
name: coop-switch
description: "Modificar jogos de Nintendo Switch para modo cooperativo ou rede local sem fio: localizar o código de sessão (PIA, nn::ldn) com Ghidra, inserir hooks com exlaunch no Atmosphere, testar com ldn_mitm ou kinnay/LDN e usar descompilações existentes."
---

<a id="switch-co-op-and-local-wireless"></a>
# Modo cooperativo e rede local sem fio no Switch

1. Um console com firmware personalizado (Atmosphere). Nunca coloque chaves, firmware ou arquivos de jogos em um repositório; mantenha distância dos serviços on-line da Nintendo.
2. Descubra os modos multiplayer já existentes: on-line, LAN, rede local sem fio, tela dividida.
3. Se já existe modo on-line ou LAN, localize a criação de sessões (chamadas PIA e `nn::ldn`) com Ghidra e REA ou GhidraMCP, nomeando as chamadas do SDK com nnheaders.
4. Insira hooks nessas funções com exlaunch (Skyline para Smash Ultimate) e redirecione o tipo de sessão para rede local sem fio.
5. Se existe apenas tela dividida ou jogo para um jogador, crie primeiro a sincronização cooperativa (`coop-build-from-zero`).
6. Confira primeiro se existe uma descompilação do jogo (Super Mario Odyssey, Breath of the Wild).
7. Teste com dois consoles ou um console e kinnay/LDN em um PC Linux; ldn_mitm mostra o comportamento dos jogos que já oferecem rede local sem fio.

Detalhes: `playbook/switch.md`.
