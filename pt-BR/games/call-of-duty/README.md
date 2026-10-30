# <a id="call-of-duty-2003-and-united-offensive-2004"></a>Call of Duty (2003) e United Offensive (2004)

| | |
|---|---|
| Motor | IW 1.0 (derivado do id Tech 3) |
| Versões testadas | CoD 1.5 (`version.inf` ExtVersion=1.5), UO 1.51 (ExtVersion=1.51), pacotes de idioma francês. Identidade das compilações (marcas de tempo PE) em [NOTES.md](NOTES.md). |
| Projetos | nenhum encontrado; entradas "Call of Duty" e "Call of Duty: United Offensive" no diretório (`kind: gap`) |
| Nível de QA | none |
| Última atualização | 2026-10-25 |

## <a id="where-things-stand"></a>Situação atual

**Somente pesquisa: nada está jogável.** Até onde estas buscas alcançam, não existe mod cooperativo de campanha para nenhum dos dois jogos. Este relato mapeia o que ainda existe no motor para um jogador e o que um mod cooperativo exigiria. A parte nativa de rede está em estágio inicial e aberta a colaboradores; confira as PRs e issues abertas sobre "call of duty" antes de começar do zero.

## <a id="existing-work"></a>Trabalhos existentes

- "CoD 1 Cooperative Mod": apenas um nome, em uma resposta de 2025 em uma [discussão Steam](https://steamcommunity.com/discussions/forum/0/2284960483102477437/). Nenhum link, autor ou versão compilada encontrado.
- [Call of Duty 1 Splitscreen PC v1.1](https://www.moddb.com/downloads/call-of-duty-1-splitscreen-pc-v11) (ModDB, 2024): ZIP de 318 bytes para multiplayer em tela dividida, não modo cooperativo de campanha.
- [CoDUO-YAP](https://github.com/Clippy95/CoDUO-YAP) (GPL-3.0, ativo em 2026-10): plugin para um jogador e multiplayer de UO (tela larga, FOV, entrada bruta, ajustes de um jogador). Carrega como proxy `ddraw.dll` ou ASI. Não oferece modo cooperativo; as perguntas frequentes dizem que não oferece suporte ao CoD 2003. A base mais útil para UO.
- [Open CoD:UO](https://github.com/opencoduo/coduomp) (2026): código-fonte reconstruído do cliente **multiplayer**, motor de servidor e módulo de jogo de UO. Sem arquivo de licença nem código de IA. Útil para estudar estruturas do motor; consulte o autor antes de usá-lo como base.
- iw1x / CoDExtended / libcod / t1x: extensões de cliente e servidor multiplayer para CoD 1.1 / UO. Não são para um jogador.
- Um item da Steam Workshop chamado "Call of Duty 2 - Deluxe Edition" (2327804851) era, na verdade, um mod de Men of War: Assault Squad 2, sem relação com estes jogos.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

Análise estática com Ghidra somente da compilação 1.5. Detalhes, endereços e categorias de evidência estão em [NOTES.md](NOTES.md). Nada abaixo foi verificado em tempo de execução.

- **O executável para um jogador mantém a separação cliente/servidor do Quake 3.** Executa um servidor e um cliente no mesmo processo. O servidor aloca **4 vagas de clientes** (`SV_Startup`), lê pacotes para as quatro e cria snapshots por cliente. A DLL do jogo (`gamex86.dll`) também trata clientes 0-3: conectar, iniciar, processar lógica e desconectar recebem um número de cliente; cada jogador ganha sua própria entidade de IA "sentient", e as entidades 0-3 são reservadas aos clientes.
- **O que foi removido:** o transporte de rede se reduz a um loopback dentro do processo (nenhuma biblioteca de sockets é importada). `SVC_DirectConnect` configura somente a vaga 0, e o servidor envia snapshots apenas ao cliente 0. O cliente local lê parte do estado do servidor diretamente da memória compartilhada, em vez de recebê-lo pela rede.
- **Portanto, o modo cooperativo usaria autoridade do host e o código de rede do próprio jogo, não lockstep:** o jogador 2 executaria um `CoDSP.exe` normal como cliente do host. Isso exige um módulo nativo (transporte, conexão às vagas, envio a todas as vagas) e trabalho nos scripts.
- **Scripts:** a lógica de fases é GSC em texto simples dentro dos arquivos `.pk3`: 809 arquivos em CoD com 1210 referências a `level.player`; 315 arquivos em UO com 1916. Scripts compartilhados definem `level.player` com `getent("player", "classname")`, que falha quando há mais de uma entidade correspondente. Assim, o plano mantém o host como `level.player` e dá aos outros jogadores outro classname, como o modo cooperativo de World at War faz com o host.
- **Executável de UO:** o código não está criptografado na cópia testada. Os nomes de seções SafeDisc são vestígios. A mesma organização do motor é esperada, mas não foi conferida.

A ordem da campanha, uma tabela de contagem por missão e uma classificação aproximada das missões com veículos estão em [NOTES.md](NOTES.md), em "Script (GSC) analysis".

## <a id="what-we-changed"></a>O que alteramos

Nada ainda. Não há código nesta PR.

## <a id="qa"></a>QA

Nenhum. Nenhum teste foi executado contra o jogo.

## <a id="how-to-play"></a>Como jogar

Não está jogável.

## <a id="known-issues"></a>Problemas conhecidos

Ainda não se aplica.

## <a id="next-steps"></a>Próximos passos

1. **O módulo nativo** para `CoDSP.exe` 1.5. É o impedimento atual, e o trabalho inicial já começou. Para assumir essa parte, comente na PR ou abra uma issue indicando sua intenção. Comece pelas notas de engenharia reversa e verifique primeiro cada endereço em tempo de execução.
2. Camada de scripts para o jogador 2, a partir do plano em [NOTES.md](NOTES.md): primeiro as bibliotecas compartilhadas (`_load`, `_loadout`, `_spawner`, `_mg42`, `_autosave`), depois os gatilhos de cada missão, começando pelos mapas pequenos.
3. Mesma análise para UO 1.51 (`CoDUOSP.exe`, `uo_gamex86.dll`).
4. Objetivos do mod concluído (em NOTES.md): começar com 2 jogadores, arquitetura para 4; retransmissão Steam Spacewar (AppID 480), com IP direto como alternativa; estado de incapacitado e reanimação, ou reaparecimento ao lado do companheiro após 5 s; progressão dirigida pelo host com seleção de fase; diagnósticos claros em falhas de inicialização.
