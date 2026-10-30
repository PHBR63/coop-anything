# <a id="star-wars-knights-of-the-old-republic-2003"></a>Star Wars: Knights of the Old Republic (2003)

| | |
|---|---|
| Motor | reone (reimplementação de motor de código aberto), em um fork |
| Versões testadas | Steam (app 32370), `swkotor.exe` v1.0.3.0, buildid 4143502, em Windows x64 |
| Projetos | [KotOR co-op](https://github.com/McChaffeeFAF/kotor-coop) (fork de reone) - entrada no diretório |
| Nível de QA | automated |
| Última atualização | 2026-10-21 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores já conseguem jogar juntos a campanha de KotOR 1, on-line, por IP:porta. O host conduz a história e os convidados controlam os companheiros do grupo; campanha, inimigos e estado do mundo são compartilhados. É uma versão alfa: a única rota funcional, exige compilar a partir do código-fonte e ainda tem sistemas inteiros inacabados (veja Problemas conhecidos).

É um fork de [reone](https://github.com/seedhartha/reone), a reimplementação gratuita do motor de KotOR e KotOR II. O reone original é para um jogador; o fork acrescenta a camada cooperativa. Só há código-fonte: nenhuma versão no GitHub ou CI; é preciso compilar com Visual Studio e vcpkg.

**De quem é o fork.** [McChaffeeFAF/kotor-coop](https://github.com/McChaffeeFAF/kotor-coop) **não** é nosso: é o projeto de McChaffeeFAF, que encontramos e testamos. Apenas corrigimos dois bugs nos scripts de empacotamento e devolvemos as correções; consulte [O que alteramos](#what-we-changed). O motor e a camada cooperativa são trabalho de McChaffeeFAF, derivados do reone de seedhartha.

## <a id="existing-work"></a>Trabalhos existentes

- [reone](https://github.com/seedhartha/reone) - a reimplementação do motor da qual deriva este fork. GPL-3.0. O original é para um jogador. Uma [matéria](https://www.gamestar.de/artikel/sw-kotor-koop,3360443.html) da GameStar de 2020 descreve uma demonstração multiplayer com dois membros do grupo controlados por humanos, visando modo cooperativo para três jogadores; apenas a jogabilidade básica funcionava em v0.5.1. O trabalho deste fork descende dessa demonstração, e a antiga entrada do diretório se baseava nessa afirmação.
- [KotOR co-op (fork de McChaffeeFAF)](https://github.com/McChaffeeFAF/kotor-coop) - fork com camada cooperativa on-line. GPL-3.0, alpha-0.4.0 (2026-10-15). A única rota viável de código aberto encontrada; não há binários pré-compilados utilizáveis.

A procura de binários prontos não encontrou nada executável: nenhuma versão no fork, 0 execuções de CI, 0 issues. É necessário compilar a partir do código-fonte.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para modo cooperativo)

- **Motor.** reone reimplementa o motor Odyssey da BioWare; lê os dados do próprio jogo comercial (`chitin.key`, BIFs, ERFs, 2DAs, GFFs) sem alterá-los. A instalação de KotOR II é *usada para recursos e sistemas de interface*, mas não é obrigatória: o motor roda KotOR 1 com o HUD de KotOR sem ela (verificado: `k2:"absent"` no estado da sessão, `--hud k1`, sem `--k2game`).
- **Scripts.** A lógica usa a máquina virtual de scripts da BioWare (NWScript); o motor executa o bytecode `.ncs` comercial. Grande parte do trabalho cooperativo durante a partida é decidir quais telas comandadas por scripts fazem sentido com mais de um jogador.
- **Código de rede.** O fork acrescenta um host autoritativo. O host controla simulação, estado da campanha e fluxo de conversas; convidados enviam *intenções* (mover, abrir, atacar, usar), e o host decide e replica o resultado. A réplica local dos objetos do host no cliente usa os IDs de objetos do host; o estado relata a integridade das réplicas (`replicas`, `bound`, `unmatched`, `violations`) para tornar a divergência visível, em vez de silenciosa.
- **Sessões.** Story Mode (host conduz a história, convidados controlam companheiros) e Free Mode (convidados trazem seus personagens). A rede usa UDP direto: host numa porta, convidados por `--join ip:port`. Um serviço de códigos de entrada (`tools/coopserver`, Python/Docker) é opcional e substitui o IP:porta compartilhado por um código curto (sem redirecionar portas).
- **Automação.** O motor tem uma **porta de controle por console** (`--control-port N`) para testes por script: comandos de texto separados por quebras de linha em 127.0.0.1, cada um respondido com uma linha JSON. Isso permite o QA abaixo sem uma pessoa.

## <a id="what-we-changed"></a>O que alteramos

Dois bugs dos scripts de empacotamento do fork, corrigidos, **enviados para um fork pessoal do repositório de McChaffeeFAF e abertos como PR para o projeto dele**: [McChaffeeFAF/kotor-coop#1](https://github.com/McChaffeeFAF/kotor-coop/pull/1) (commits `4ec25f9` e `5d45c38`, rebaseados em `c56a05e` = alpha-0.4.4). A PR contém branch e diferenças; enquanto não for incorporada, um clone novo de `main` ainda apresenta os dois bugs:

1. **O pacote incluía o runtime VC++ errado e falhava ao iniciar.** Causa raiz: o script procurava pastas de redistribuição `Microsoft.VC*.CRT` nas instalações de Visual Studio e ordenava por *nome*, então `2019\BuildTools` prevalecia sobre `18\BuildTools`. Copiava **VC142 (14.29)** junto a um motor compilado com **VC145 (14.51)**; a `msvcp140.dll` local ocultava o runtime mais recente do sistema, e o motor encerrava com `0xC0000005`, sem log ou saída. Correção: ler o conjunto de ferramentas das importações do próprio motor (`boost_program_options-vc145-...`), selecionar esse CRT e avisar sobre incompatibilidade. Teste: o motor empacotado agora executa; após extrair o ZIP, hospeda uma sessão.
2. **O inicializador recusava iniciar sem KotOR II.** Causa raiz: a prontidão exigia *ambos* os jogos; quem tinha só KotOR 1 via Host / Join / solo **desativados**, inclusive Play solo, embora o motor funcione só com KotOR 1. Correção (`launcher.ps1`/`setup.ps1` no Windows, `setup.sh` no Linux): KotOR II opcional; prontidão baseada em KotOR 1; HUD conforme o que estiver instalado. Teste: uma primeira execução sintética sem KotOR II agora escreve `hud=k1` e nenhum `k2game`.

Nada na instalação comercial ou nos salvamentos foi alterado; todos os testes usaram uma cópia.

## <a id="qa"></a>QA

- **Suíte de dois clientes:** `games/kotor/test/harness.ps1` (publicada com este relato). Inicia dois clientes reais do motor num PC (host e convidado, ambos sem interface), conecta-os por UDP localhost, controla-os pelas portas TCP de controle e verifica o estado compartilhado nas **duas** posições. Execute com `powershell -ExecutionPolicy Bypass -File harness.ps1` (parâmetros: `-GamePath`, `-BinDir`, portas). **77 critérios**, `RESULT: PASS` em duas execuções consecutivas (2026-10-20), em alpha-0.4.0, com ambos no mesmo PC por localhost. Não reexecutada na atual alpha-0.4.4. Cobre entrada/módulo/movimento, diálogo, carteira, contêineres, subida de nível, combate, transições de área, propagação de pausa, convidado abrindo uma porta ao alcance e verificação de prontidão para sair da área.
- **Testes unitários:** 3.650 testes / 526 suítes: 3.639 aprovados, 0 falhas, 11 ignorados.
- **Empacotamento:** estrutura de testes do inicializador Linux 32/32; **host->join completo pelo pacote compilado: 9/9** verificações, ambos os clientes empacotados em `end_m01aa`, replicação limpa (`unmatched: 0`, `violations: 0`), tráfego nos dois sentidos, `k2:"absent"`.
- **Sem critérios automatizados (lacunas declaradas):** loja, bancada/laboratório, minijogos de swoop/torreta e Free Mode / geração de personagem não são acessíveis pela porta de controle sem comerciante/bancada por script ou outro modo de sessão. Estão registrados, não são declarados como comprovados.

## <a id="how-to-play"></a>Como jogar

1. Compile o fork a partir do código-fonte (Visual Studio + vcpkg; `-G "Visual Studio 18 2026"`). Não há versões distribuídas: é necessário compilar.
2. Empacote com `tools/package/make_tester_package.ps1`; o jogador executa **Play KotOR Co-op.cmd** e escolhe Host ou Join. O inicializador encontra as instalações sozinho.
3. Host: hospeda pelo inicializador e compartilha IP:porta; o amigo entra com `--join ip:port`. Outra opção é configurar o serviço de códigos de entrada para usar códigos curtos.
4. KotOR II é opcional; sem ele, joga-se KotOR 1 com o HUD de KotOR.

## <a id="known-issues"></a>Problemas conhecidos

- **Alfa.** Espere telas inacabadas e problemas de acabamento.
- **Somente código-fonte.** Sem binários; é necessário um conjunto de ferramentas de desenvolvimento para jogar.
- **Uma máquina.** Ambos os clientes rodaram no mesmo PC por localhost. Não houve teste entre redes.
- **Versão da suíte.** Os 77 critérios foram executados em alpha-0.4.0, não na atual alpha-0.4.4.
- **Correções ainda não distribuídas.** Dois bugs de empacotamento estão corrigidos na [PR #1 para o fork](https://github.com/McChaffeeFAF/kotor-coop/pull/1), ainda não incorporada; até isso ocorrer, um clone novo continua falhando ao iniciar e exigindo KotOR II.
- **Telas bloqueadas para companheiros.** Durante conversas, o host responde `busy` aos comandos dos convidados: é intencional (o host conduz o diálogo), mas impede ações do convidado durante a cena.
- **A ação do convidado é aceita mesmo quando não pode ser realizada**, como abrir uma porta fora do alcance do companheiro. O host só a executa quando o companheiro está perto o suficiente.
- **Sistemas sem critérios automatizados**, como loja, bancada, minijogos e Free Mode, podem funcionar mal em modo cooperativo; ninguém os automatizou ainda.

## <a id="next-steps"></a>Próximos passos

- Criar critérios automatizados para loja, bancada e minijogos (exigem comerciante/bancada por script ou sessão Free Mode).
- Uma **campanha completa** cooperativa verificada elevaria o QA de `automated` para `verified-playthrough`; ninguém concluiu a campanha em modo cooperativo.
- Obter revisão e incorporação das [duas correções de empacotamento](https://github.com/McChaffeeFAF/kotor-coop/pull/1) no fork; estão numa PR aberta, não em `main`.
