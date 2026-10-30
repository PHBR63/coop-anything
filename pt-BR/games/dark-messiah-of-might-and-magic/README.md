# <a id="dark-messiah-of-might-and-magic-2006"></a>Dark Messiah of Might and Magic (2006)

| | |
|---|---|
| Motor | Source (ramificação de 2006 da Arkane) |
| Versões testadas | Steam appid 2100, buildid 49752, SHA-256 de `mm.exe`: `f8faaee53a2c9ed72b8c7b83b75608f96a77ab07f374314950701901bda7e34c` |
| Projetos | [wiltOS Dark Messiah Co-op](https://github.com/KingDavidW/DarkMessiah-Coop-Mod-Files) (entrada no diretório "Dark Messiah Co-op Mod (wiltOS)") |
| Nível de QA | community-reports |
| Última atualização | 2026-10-23 |

## <a id="where-things-stand"></a>Situação atual

Já é possível jogar a campanha em modo cooperativo com o mod wiltOS (alpha, versão A2-03.23). Jogadores relatam que é jogável, com atraso quando o ping é alto, falhas no HUD e um bug da grade levadiça que pode impedir o progresso em uma fase. No Linux com Proton, o mod carrega e chega ao menu cooperativo. Uma sessão com entrada de cliente ainda não foi testada.

## <a id="existing-work"></a>Trabalhos existentes

- [KingDavidW/DarkMessiah-Coop-Mod-Files](https://github.com/KingDavidW/DarkMessiah-Coop-Mod-Files): mod atual, GPL-3.0, `dmcoop_server.dll` / `dmcoop_client.dll` pré-compiladas, sem código-fonte no repositório. Último push em 2026-03-23. Usa um servidor mestre da comunidade (`master.wiltostech.com:27010`).
- Depende de [wiltOS Mod Launcher](https://github.com/KingDavidW/DarkMessiah-ModLauncher-Files) e [módulo base Advanced SDK](https://github.com/KingDavidW/DarkMessiah-AdvancedSDK-Mod-Files).
- [Balimbanana/DarkMessiahCoopSetup](https://github.com/Balimbanana/DarkMessiahCoopSetup): predecessor de 2023 (edições de lumps carregadas com `-tempcontent`). O README wiltOS lhe dá crédito pelas primeiras alterações cooperativas.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

O motor Source já tem código de rede cliente/servidor e Dark Messiah foi lançado com um jogo multiplayer separado. O mod executa os mapas de um jogador em um servidor hospedado pelo próprio jogador, com módulos extras carregados pelo inicializador (`info.json` → `modules`) e correções de mapas como MapAdds. Inicia com `-insecure` e `+type singleplayer_and_multiplayer`.

## <a id="what-we-changed"></a>O que alteramos

Nada no mod. Notas de instalação no Linux:

- O inicializador distribui `Steam.dll`; o jogo tem `steam.dll`. Em um sistema de arquivos sensível a maiúsculas e minúsculas, extrair o inicializador sem alterações deixa os dois arquivos. Em vez disso, copie `Steam.dll` por cima de `steam.dll`.
- A ordem de carregamento dos mods pode ser definida sem interface gráfica em `_mods/core/user_settings.json`: `"load_order": ["advanced_sdk", "dm_coop"]`.

## <a id="qa"></a>QA

Verificações realmente executadas (2026-10-23, Linux, KDE Wayland, Proton Experimental, SteamLinuxRuntime_4):

- A interface do inicializador abre com Proton.
- "Launch with Mods" carrega `server_sdk.dll`, `client_sdk.dll`, `dmcoop_server.dll` e `dmcoop_client.dll` (verificado em `/proc/<pid>/maps`).
- O menu principal mostra Find Servers / Create Server. A mensagem "Platform Error: module failed to initialize" da [issue #13](https://github.com/KingDavidW/DarkMessiah-Coop-Mod-Files/issues/13) não apareceu.

Sessão de teste de jogador (2026-10-24, sem teste estruturado): host Linux com Proton, clientes Windows entrando pela internet em um servidor do jogador com porta redirecionada. A sessão funcionou. Os jogadores relataram sincronização "a bit off" (um pouco imprecisa) e atraso ao subir em correntes. Não registrados: ping, quantidade de jogadores e cvars `cl_*` configuradas.

Não testado: o que exatamente é sincronizado em inimigos, portas, itens ou história.

## <a id="how-to-play"></a>Como jogar

1. Faça backup dos arquivos da pasta do jogo substituídos pelo inicializador: `mm.exe`, `steam.dll`, `steam.inf`, `steamclient.dll`, `tier0_s.dll`, `vstdlib_s.dll`.
2. Extraia o Mod Launcher em `<game dir>`, o Advanced SDK em `<game dir>/_mods/advanced_sdk` e os arquivos cooperativos em `<game dir>/_mods/dm_coop`. O Advanced SDK precisa vir primeiro na ordem dos mods.
3. Inicie pelo Steam e clique em **Launch with Mods**.
4. O host clica em Create Server. Os demais usam Find Servers ou digitam `connect <host ip>:27015` no console (a UDP 27015 precisa estar acessível no host).
5. Cvars de cliente sugeridas pelo mantenedor ([#1](https://github.com/KingDavidW/DarkMessiah-Coop-Mod-Files/issues/1)): `cl_predict 0`, `cl_interp 0.01`, `cl_interp_npcs 0.6`.

Para desinstalar, restaure os backups ou use "Verify integrity of game files" no Steam e exclua `_mods`.

## <a id="known-issues"></a>Problemas conhecidos

- Rodas de grades levadiças: manter Use pressionado até terminar o giro deixa o portão fechado, impedindo o progresso. Solte antes de a roda terminar de girar ([#8](https://github.com/KingDavidW/DarkMessiah-Coop-Mod-Files/issues/8)).
- A sincronização parece um pouco imprecisa em partidas normais e subir em correntes tem atraso (sessão de jogador em 2026-10-24).
- Clientes percebem atraso de entrada com ping de aproximadamente 150 ms; redes virtuais como ZeroTier pioraram o problema para um usuário ([#16](https://github.com/KingDavidW/DarkMessiah-Coop-Mod-Files/issues/16)).
- HUD: temporizador de recarga incorreto, mana exibida com limite de 29, ausência de barra de fôlego debaixo d'água; nomes às vezes somem no chat.
- Conflitos com o pacote de mods Unlimited Edition 1.4.1 ([#6](https://github.com/KingDavidW/DarkMessiah-Coop-Mod-Files/issues/6)).

## <a id="next-steps"></a>Próximos passos

- Medir o atraso ao subir em correntes: comparar `cl_predict 1` com `cl_predict 0`, registrando ping e `net_graph`. Hipótese não verificada: correntes usam um modo de movimento que o cliente talvez não antecipe; com `cl_predict 0`, cada movimento de subida espera uma ida e volta completa.
- Registrar o que sincroniza por subsistema (inimigos, portas, itens, história), idealmente com um cliente bot (playbook/automated-qa.md).
- O código-fonte das DLLs cooperativas não é público; portanto, as correções devem ser encaminhadas ao projeto de origem pelo Discord wiltOS ou por issues do GitHub.
