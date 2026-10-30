# <a id="the-doors-of-trithius-early-access"></a>The Doors of Trithius (Acesso Antecipado)

| | |
|---|---|
| Motor | Java (JVM): motor Java 2D personalizado em um único `DOT.jar`, com JDK 22 incluído |
| Versões testadas | Steam 0.6.3b (compilação Steam 25513945), SHA-256 de `DOT.jar` `E933BD53726362D5DC83B85E718CCC6BC728B6B971315E7BFAEE80132D9A540A`, SHA-256 de `DOT.exe` `239b396392152b2b72ceb0fe1520561c43675a0d6436bdc4f027d45b31f9ca4e`, Windows 11 |
| Projetos | Trithius co-op, mod javaagent para dois jogadores. Ainda não é público: o repositório de distribuição será aberto após um teste ao vivo sem problemas. Sem entrada no diretório até ter uma fonte pública. |
| Nível de QA | automated |
| Última atualização | 2026-10-18 |

## <a id="where-things-stand"></a>Situação atual

Dois jogadores podem jogar juntos no mesmo mundo pela internet: ambos exploram, lutam, coletam itens, negociam, aceitam trabalhos, alugam quartos, fabricam em bancadas e percorrem o mapa do mundo. O jogo do host é a autoridade, e o convidado usa teclado e mouse como no modo para um jogador. A última noite de teste ao vivo (2026-10-15) terminou como "pronto, mas com atritos": seis constatações em aberto, sendo a pior a perda de ouro do convidado após ser incapacitado. A próxima compilação está agora passando pela suíte de testes.

## <a id="existing-work"></a>Trabalhos existentes

Nenhum neste diretório (verificado em 2026-10-18). Ainda falta uma busca mais ampla (fóruns Steam, Nexus, canais do próprio desenvolvedor). O jogo é exclusivamente para um jogador e não tem código de rede.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- **Código e dados:** um único jar. Os dados do jogo (`modules/*.dat`) são objetos Java serializados dentro dele. O `javap` do próprio JDK do jogo responde às dúvidas de API, e um descompilador permite ler a lógica.
- **Ponto de hook:** as regras passam por um barramento de eventos com classes públicas; a maioria dos serviços depende de um objeto de contexto (`context.player`, bolsa, habilidades, capacidades e serviço de turnos do jogador). Um `-javaagent` pode se inscrever no barramento e chamar os serviços sem alterar arquivos do jogo.
- **Turnos:** máquina de turnos com estados (aguardando, movendo, atacando). Todo o restante age quando o único jogador termina um turno. No mapa do mundo, um passo executa os procedimentos de início de turno uma vez por unidade de custo do terreno (40 a 120), e depois mais um início de turno.
- **Locais e salvamentos:** cada local (cidade, masmorra, mapa do mundo) carrega como uma zona em etapas de preparação (carregar reputação, atualizar atributos, passar tempo). Um salvamento contém os arquivos das zonas e o único jogador. Salvamentos automáticos renomeiam arquivos de zona, o que pode falhar se outro processo os mantiver abertos.
- **Interface:** os painéis do jogo (diálogo, comércio, armazenamento, habilidades) leem diretamente o estado do único jogador, então um segundo jogador precisa de sua própria cópia das entradas de cada painel.

## <a id="what-we-changed"></a>O que alteramos

O mod executa dois jogos completos: host e convidado, cada um com o mod como javaagent.

- **Autoridade do host com janela de personificação.** O convidado envia comandos (mover, atacar, usar, conversar, negociar). O host executa cada um com o código original para um jogador: troca os campos do jogador no contexto (entidade, bolsa, habilidades, receitas, capacidades, fome, cansaço, campo de visão) pelos do convidado, executa o comando e os restaura em um `finally`. Um teste estático verifica que nada execute entre a troca e o `try`. Isso reutiliza todas as regras (dano, saque, fabricação, preços) para o segundo jogador.
- **Atribuição por jogador.** Eventos enfileirados durante um comando do convidado são processados dentro da sua janela; mortes, golpes e desgaste são atribuídos conforme o atacante ou autor da morte do próprio evento. Sem isso, XP, vantagens e mensagens do histórico iam para o host.
- **Réplica, não segunda simulação.** O mundo do convidado é uma réplica criada a partir de snapshots do host. Nunca simula. Snapshots usam gerenciamento de interesse em locais grandes (um local continha 2448 entidades para um limite de 2048).
- **Relógios separados para jogadores distantes.** Em um jogo por turnos, os turnos de um jogador não devem movimentar os monstros do outro. Cada criatura pertence a um relógio (do jogador que ela tem como alvo; caso contrário, do jogador mais próximo dentro de 30 casas; caso contrário, do host). Quando os jogadores se aproximam, os relógios se unem.
- **Confirmações fiéis.** Cada comando responde aplicado, sem efeito, parcial ou recusado, com o motivo que o jogo mostraria a um jogador solo.
- **Verificação de identidade.** A negociação inicial contém a compilação do jogo, o hash do jar e o identificador de compilação do mod. Um par incompatível é recusado, e a mensagem informa ambos os identificadores.
- **Personagens viajam.** O personagem do convidado é salvo no host por nome e pode ser exportado ao jogo próprio do convidado. Arquivos gravados em disco nunca levam estados do mundo do host (por exemplo, o estado de reputação que o convidado usa nos preços das lojas).

## <a id="qa"></a>QA

- Suíte de verificação com cerca de 65 scripts PowerShell. Cada um inicia uma JVM real de host e outra de convidado em um PC, controla ambas por um controlador textual de ações dentro da JVM e lê dumps de estado dos dois jogadores. As primeiras verificações são autotestes da estrutura de testes e do avaliador. Um executor considera falha a ausência de uma linha de resultado e TIMEOUT o tempo excedido.
- Noites de teste ao vivo: agentes de IA jogam como host e convidado por 3 a 4 horas com teclado e mouse, por um retransmissor com modos de atraso, interrupção e perda. Um agente observador avalia uma lista escrita, com o host executando a mesma ação como controle solo.
- Última suíte completa: 63 de 63 PASS na compilação r16 (2026-10-15). A noite ao vivo mais recente (V31, compilação r17, 2026-10-15) está resumida acima. Essas noites ocorrem desde setembro de 2026.

## <a id="how-to-play"></a>Como jogar

Ainda não foi distribuído. O kit do convidado contém dois jars e um script de conexão que o amigo coloca na própria instalação Steam. O host inicia o jogo com o jar de host e fornece um endereço e um segredo ao amigo. Por enquanto, usa IP direto (redirecionamento de porta ou VPN).

## <a id="known-issues"></a>Problemas conhecidos

- Após ser incapacitado, o convidado pode acordar com menos ouro. O próprio jogo retira ouro de um jogador solo incapacitado; a correção em teste removeu a parte causada pelo mod (uma mensagem perdida no histórico).
- Enquanto o host está com uma janela de conversa ou comércio aberta, uma conversa ou negociação do convidado espera (correção em teste).
- Reiniciar o host pode deixar desativada a opção On Guard do convidado.

## <a id="next-steps"></a>Próximos passos

- Executar a próxima noite ao vivo com a compilação atualmente em teste.
- Um processo auxiliar de retransmissão Steam (Spacewar) em vez de IP direto: até agora, apenas estudo de viabilidade.
- Abrir o repositório de distribuição e a entrada no diretório após uma noite sem problemas.
