# <a id="celeste-2-player-co-op-setup-guide"></a>Celeste cooperativo para 2 jogadores: guia de configuração

Objetivo: você e um amigo jogarem juntos a minicampanha cooperativa **Partnership** na versão **Steam (PC)** de Celeste.

Ambos devem seguir todas as etapas. O modo cooperativo não funciona se somente um tiver os mods.

> Este guia usa o jogo Steam original com mods. Nada aqui modifica ou contorna o Steam, nem interfere no jogo de outras pessoas. Todos os mods são gratuitos e têm download público.

## <a id="what-you-need"></a>O que você precisa

- Celeste no Steam, no Windows. (Na prática, os mods são voltados ao Windows; Everest suporta Linux/macOS, mas este guia foi escrito para Windows.)
- Cerca de 1 GB livre em disco para Everest e os mods.
- Ambos os jogadores no mesmo servidor CelesteNet e no mesmo canal.

## <a id="step-1-install-everest"></a>Etapa 1: instalar Everest

Everest é o carregador de mods. Há duas formas de instalá-lo. **Olympus** é a interface gráfica amigável usada pela maioria dos jogadores.

### <a id="option-a-olympus-recommended-for-a-normal-install"></a>Opção A: Olympus (recomendado para instalação normal)

1. Acesse as versões do Olympus: <https://github.com/EverestAPI/Olympus/releases> e baixe o instalador mais recente para Windows.
2. Execute-o. Ele encontra a instalação de Celeste e instala Everest.
3. Depois, Olympus também serve para instalar e atualizar mods (Etapa 2).

Site oficial e ajuda: <https://everestapi.github.io/>.

### <a id="option-b-manual-miniinstaller"></a>Opção B: manual (MiniInstaller)

Use esta opção se mantém Celeste em uma pasta separada (por exemplo, uma cópia cuja instalação principal você não quer alterar), como foi feito na instalação de teste deste repositório.

1. Baixe a versão Everest marcada como `stable` em <https://github.com/EverestAPI/Everest/releases> (por exemplo, `everest-main.zip`).
2. Extraia **na pasta de Celeste** (a que contém `Celeste.exe`). Isso acrescenta `MiniInstaller-win64.exe` e suas bibliotecas. Antes, faça uma cópia de segurança da pasta se quiser preservar os arquivos originais.
3. Execute `MiniInstaller-win64.exe`. Ele aplica patches ao jogo e cria `Mods/`. Everest mantém os arquivos anteriores aos mods em `orig/`.
4. Inicie `Celeste.exe` uma vez para confirmar que Everest abre.

## <a id="step-2-install-the-mods"></a>Etapa 2: instalar os mods

Você precisa de **cinco** mods. Instale todos os cinco nas duas máquinas.

| Mod | Download | Finalidade |
|---|---|---|
| CelesteNet.Client | <https://gamebanana.com/mods/53695> | camada multiplayer |
| Co-op Helper | <https://gamebanana.com/mods/453706> | entidades sincronizadas usadas pelos mapas cooperativos |
| MaxHelpingHand | <https://gamebanana.com/mods/53687> | exigido por Partnership |
| LunaticHelper | <https://gamebanana.com/mods/53692> | exigido por Partnership |
| Partnership | <https://gamebanana.com/mods/150725> | a própria campanha cooperativa |

> **Atenção:** a página GameBanana de MaxHelpingHand se chama **"Maddie's Helping Hand"**. O nome mudou anos atrás, mas o identificador interno foi mantido; se um mapa exigir `MaxHelpingHand`, é esse o mod. Procurar "MaxHelpingHand" no GameBanana não o encontra de forma óbvia.

### <a id="with-olympus"></a>Com Olympus

Abra Olympus, procure cada mod pelo nome e instale. Olympus obtém as dependências; se oferecer MaxHelpingHand ou LunaticHelper como dependência de Partnership, aceite.

### <a id="manually"></a>Manualmente

1. Para cada mod, baixe o ZIP da versão na página indicada acima.
2. Crie uma pasta em `Mods/` com o nome do mod e extraia o ZIP **nela**, de modo que exista `<Celeste>/Mods/<ModName>/everest.yaml`. Por exemplo: `Mods/Partnership/everest.yaml`, `Mods/CelesteNet.Client/everest.yaml`.
3. O nome da pasta não importa para Everest; o `everest.yaml` dentro dela importa.
4. Se o ZIP já contiver uma pasta no primeiro nível, extraia essa pasta em `Mods/`, em vez de acrescentar um nível de aninhamento.

Não coloque os ZIPs brutos em `Mods/`; extraia-os.

## <a id="step-3-connect-with-celestenet"></a>Etapa 3: conectar com CelesteNet

1. Inicie Celeste pelo Steam. Deve aparecer uma entrada Everest / CelesteNet no menu principal (CelesteNet acrescenta sua própria página de configurações e sobreposição dentro do jogo).
2. Abra as configurações de CelesteNet e defina um **nome de exibição** (o que seu parceiro verá).
3. Escolha um **servidor**. O servidor público CelesteNet é o padrão. Ambos devem usar o mesmo servidor. Se quiser um próprio, o servidor CelesteNet pode ser hospedado por você (consulte <https://github.com/0x0ade/CelesteNet>).
4. Conecte. Sua entrada deve aparecer na sobreposição CelesteNet.

## <a id="step-4-make-a-private-channel"></a>Etapa 4: criar um canal privado

Um canal é uma sala no servidor. Sem um canal privado, você compartilha o mapa com todas as outras pessoas daquele servidor.

1. Na sobreposição CelesteNet, use os controles de canal para criar um canal (por exemplo, `partner-<something-only-you-two-know>`).
2. **Defina uma senha** ou mantenha o nome impossível de adivinhar.
3. Seu parceiro entra informando o mesmo nome de canal e senha.
4. Antes de iniciar o mapa, confirme que os nomes dos dois aparecem na sobreposição.

A página do mod Partnership contém um link para um vídeo da comunidade sobre CelesteNet e canais privados.

## <a id="step-5-play-partnership"></a>Etapa 5: jogar Partnership

1. No menu principal, abra a **seleção de capítulos** e encontre **Partnership** na lista de mods.
2. Inicie o primeiro capítulo. Foi projetado para exatamente dois jogadores, não para jogar sozinho.
3. O progresso é registrado no mapa cooperativo, separado do salvamento original.

## <a id="troubleshooting"></a>Solução de problemas

- **Um mod não carrega / "missing dependency" ao iniciar.** Partnership precisa de MaxHelpingHand e LunaticHelper. Confirme que ambos existem como pastas com seus próprios `everest.yaml` em `Mods/`.
- **Vocês não conseguem se ver.** Confiram servidor e canal iguais e se ambos realmente conectaram (a sobreposição CelesteNet mostra a lista de jogadores). Reinicie Celeste após mudar o servidor.
- **Estranhos aparecem no mapa.** Vocês estão em um canal público; criem ou entrem em um privado.
- **Somente um instalou os mods.** As duas máquinas precisam da lista completa. O mapa não carregará para quem estiver sem alguma dependência.
- **Log do Everest para depuração:** `log.txt` na pasta de Celeste (Everest não usa o nome `everest-log.txt`). Lista todos os mods carregados e erros.
- **Você copiou Celeste para uma pasta separada, mas o Steam continua abrindo a instalação normal.** A cópia precisa de um arquivo `steam_appid.txt` contendo `504230` junto a `Celeste.exe`; sem ele, a inicialização é encaminhada à instalação Steam. Uma instalação Steam normal não precisa disso.
- **Links antigos de download.** Alguns guias e até o README de CelesteNet apontam para `gamebanana.com/gamefiles/<id>`. Hoje redirecionam à página correta, mas, se um levar a um destino estranho, use as páginas da tabela acima.

## <a id="note-on-the-test-install-used-for-this-write-up"></a>Nota sobre a instalação de teste deste relato

Para não alterar a instalação Steam do usuário, os testes usaram uma **cópia separada** do jogo em `local/` (ignorada pelo Git), com Everest instalado nela. Sua configuração pode usar uma cópia ou a instalação normal; para preservar o jogo original, copie a pasta Celeste para outro local e instale Everest na cópia.
