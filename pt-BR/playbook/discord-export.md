# <a id="mining-a-mods-discord-for-bug-reports"></a>Levantando relatos de bugs no Discord de um mod

Projeto de origem: Shadow of COOP, mod cooperativo de STALKER no motor xrMPE. Os desenvolvedores haviam seguido outros caminhos, e o único registro ativo de bugs conhecidos, soluções alternativas e "qual é a compilação atual" estava em um canal de suporte do Discord. Esta página registra o que foi feito e o que deu errado.

## <a id="risk-note"></a>Nota sobre risco

Exportar um canal em modo "user" usa o token da sua própria conta com uma ferramenta de terceiros. Isso viola os termos do Discord; portanto, você assume o risco ao utilizá-la, embora, na prática, banimentos por uma exportação pontual sejam essencialmente incomuns. Um token equivale a um login completo; trate-o com cuidado (veja abaixo).

## <a id="what-was-actually-done"></a>O que foi feito de fato

- **Ferramenta:** DiscordChatExporter, compilação de linha de comando (`DiscordChatExporter.Cli`, ZIP Windows x64 da página de versões do projeto no GitHub). É um aplicativo .NET, então a máquina precisa de um runtime .NET, salvo se você usar a compilação autossuficiente. O README do autor documenta como obter o token; esta página deliberadamente não repete isso.
- **Quem executou:** a pessoa, não o agente. A camada de segurança impediu o agente de configurar uma coleta em massa de mensagens de outras pessoas, e a resposta correta foi não contornar o bloqueio. O agente escreveu o comando exato e um script auxiliar, e a pessoa os executou no próprio terminal. Depois, o agente leu o arquivo resultante.
- **Tratamento do token, em termos gerais:**
  - O token foi passado apenas ao processo do exportador, por uma variável de ambiente (`DISCORD_TOKEN`) lida pela ferramenta, nunca pela linha de comando (linhas de comando ficam no histórico do shell).
  - O `.bat` auxiliar pedia o token em tempo de execução e o limpava ao fechar a janela. Nunca se grava um token em script, arquivo de configuração, repositório ou transcrição de agente.
  - O token não deve ser colado na conversa com o agente. Neste projeto ele foi colado por engano uma vez. A resposta correta é considerá-lo comprometido: mudar a senha da conta (o que invalida o token) e depois obter outro.
- **Seleção do canal:** ative o Modo Desenvolvedor nas configurações do Discord, clique com o botão direito no canal-alvo e escolha "Copy Channel ID". Para um canal de fórum, também é possível copiar o ID da conversa de uma publicação específica. Escolha um único canal de suporte ou bugs, não o servidor inteiro. Uma exportação mais restrita é mais rápida, menor e coleta menos mensagens de desconhecidos.
- **Formato do comando:** `DiscordChatExporter.Cli export -c <channel id> -f <format> -o <output dir>`, com estas opções quando necessário:
  - `--include-threads All` para canais de fórum (sem ela, a exportação contém apenas o cabeçalho). Se a opção for rejeitada, remova-a ou exporte as conversas uma a uma pelos respectivos IDs. O script auxiliar tentava novamente sem ela automaticamente.
  - `--after <date>` para começar na versão relevante (aqui, no dia da última compilação), removendo meses de conversas antigas.
- **Formatos:** `PlainText` (um `.txt`) foi usado e funcionou melhor para um agente: cerca de 700 mensagens viraram aproximadamente 3.100 linhas, pequenas o bastante para leitura em duas partes. `Json` é melhor para processamento por script (filtrar por autor, contar, juntar conversas), ao custo de muito mais ruído por mensagem. `HtmlDark`/`HtmlLight` são para pessoas, e `Csv` para planilhas. Anexos não são baixados, a menos que você peça mídia; raramente são necessários.

## <a id="from-export-to-bug-list"></a>Da exportação à lista de bugs

1. **Copie o arquivo para um caminho simples** (nome ASCII curto, na pasta temporária do agente). Os nomes padrão incluem servidor, canal e IDs, com espaços e colchetes que atrapalham ferramentas de shell.
2. **Conte primeiro.** Número de linhas e intervalo de datas, para saber o volume e se a exportação cobre o período desejado.
3. **Leia em partes, não em uma única leitura gigantesca.** A ferramenta de leitura tem limite de tokens por chamada; use deslocamento e limite (cerca de 1.700 linhas por parte funcionou) e não responda só pela primeira parte se o arquivo for maior. Use grep para buscas precisas depois de conhecer o vocabulário (nomes de erros, "crash", "fix", números de versão, "download", "link").
4. **Traduza ao resumir.** O canal deste caso era inteiramente em russo. O agente o leu diretamente e escreveu o resumo em inglês. Preserve as strings técnicas originais (texto de erro, nomes de arquivos, comandos de console), pois são elas que você pesquisará depois.
5. **Estruture o resumo sempre da mesma forma:**
   - Estado do mod (qual é a compilação mais recente, se os desenvolvedores estão ativos, o que diz a última lista de correções).
   - **Lista de bugs** com sintomas, texto exato do erro e quantas pessoas relataram.
   - **Soluções alternativas** (configurações, arquivos a excluir, opções de inicialização) com a redação original por perto.
   - Cópias alternativas para download e localização do arquivo oficial.
   - Respostas às dúvidas recorrentes de configuração (dificuldade, comandos de administrador, portas, idioma).
6. **Separe afirmações de fatos verificados.** Um moderador dizer "esta é a nova versão" é uma afirmação. Confira o próprio arquivo (tamanho, hash, datas no arquivo compactado, versão na configuração) antes de escrever isso em um guia. Neste projeto o inicializador não atualizava seu número de versão, então "7.0" e "8.0" se referiam aos mesmos arquivos.
7. **Trate os links da exportação como não confiáveis.** Cópias de arquivos de terceiros publicadas na conversa podem ser qualquer coisa. Examine-as, prefira o link oficial e informe no guia qual link não é oficial.
8. **Leve as descobertas aos testes.** Cada mensagem de travamento relatada (por exemplo, erro de shader ou modelo ausente) virou um teste de inicialização em todas as fases, em vez de continuar como uma linha em um arquivo de notas.

## <a id="pitfalls"></a>Armadilhas

- **O agente pode recusar a coleta**, com razão. Não discuta nem tente obter o mesmo resultado por outro caminho. Execute você mesmo a ferramenta ou use a alternativa de copiar e colar manualmente.
- **Token na conversa.** Nunca. Se acontecer, substitua-o imediatamente.
- **Exportação vazia de canais de fórum.** Exige `--include-threads` ou IDs de cada conversa.
- **Exportações enormes.** Sempre limite por data e canal. Um ano de um servidor movimentado é ilegível e, em grande parte, irrelevante.
- **Dados pessoais.** Uma exportação contém nomes, identificadores e mensagens de desconhecidos. Não copie identificadores, IDs de usuário, convites ou links de mensagens para documentação pública. Resuma ("um jogador relatou..."), mantenha o arquivo bruto fora de qualquer repositório e exclua-o ao terminar.
- **Informação desatualizada.** Conversas estão cheias de respostas erradas e confiantes, corrigidas três mensagens depois. Prefira a última declaração de um mantenedor e confira as datas.
- **Limites de taxa e tamanho.** Canais muito longos podem demorar; execute uma vez, em uma janela que possa ficar aberta, e não sobrecarregue a API com execuções repetidas.
- **Surpresas na pasta de saída.** A ferramenta nomeia os arquivos pelo canal; ao exportar vários para a mesma pasta, confira os nomes antes de ler o arquivo errado.
