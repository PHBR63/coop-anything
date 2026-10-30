# <a id="stalker-shadow-of-chernobyl-2007-and-clear-sky-2008"></a>S.T.A.L.K.E.R.: Shadow of Chernobyl (2007) e Clear Sky (2008)

| | |
|---|---|
| Motor | X-Ray (Shadow of COOP usa a extensão multiplayer xrMPE, baseada em Call of Pripyat) |
| Projetos | Shadow of COOP 8.0 (Arcanum Team, complemento xrMPE) + nosso patch de correções [stalker-soc-coop-fixes](https://github.com/cranebeaker/stalker-soc-coop-fixes); Clear COOP 0.5 (abandonado em novembro de 2024) |
| Nível de QA | automated (patch de correções: teste de inicialização + autoteste dentro do motor); none (Clear COOP) |
| Última atualização | 2026-10-16 |

## <a id="where-things-stand"></a>Situação atual

- **Shadow of Chernobyl:** é possível jogar a história com Shadow of COOP. Um patch de correções (um arquivo `.db` adicional acrescentado ao complemento) corrige um encerramento inesperado no final do jogo e outros bugs. Versão distribuída: [stalker-soc-coop-fixes](https://github.com/cranebeaker/stalker-soc-coop-fixes/releases).
- **Clear Sky:** Clear COOP 0.5 inclui 8 fases e a história só era jogável até Agroprom. Começamos um port para xrMPE 0.9, mas paramos; não há trabalho em andamento. As notas desta página estão disponíveis para quem quiser continuar.

## <a id="how-the-game-works-for-co-op"></a>Como o jogo funciona (para o modo cooperativo)

- `coop.addon` é um arquivo tar com arquivos `.db` do X-Ray; o inicializador carrega todos os `.db` contidos nele, então os patches são acrescentados, sem reempacotar. O servidor calcula checksums de `*.addon`, portanto todos os jogadores precisam de arquivos idênticos.
- Índice `.db` do X-Ray: bloco 1, LZHUF com MAX_FREQ=0x4000 (o valor clássico 0x8000 corrompe a saída após cerca de 97 KB); dados dos arquivos em LZO1X.
- Os indicadores de missões são globais no servidor e os diálogos usam quem está falando, então os clientes provavelmente conseguem entregar missões.
- xrMPE 0.9 carrega arquivos `<name>.dscript` acrescentados aos scripts base: use-os em vez de criar forks dos scripts base.

## <a id="what-we-changed"></a>O que alteramos

- Falha no final do jogo: as fases referenciavam modelos quebráveis (`meshes\brkbl#N.ogf`) que nunca foram distribuídos; substitutos de 1 KB para os índices ausentes corrigem todas as 18 fases.

## <a id="qa"></a>QA

- Teste de inicialização de cada fase em servidor dedicado com cliente local, monitorando `Connection finished` ou `FATAL ERROR` no log.
- Arquivo de autoteste interno ao motor, acionado pela lógica de um delimitador espacial (20/20 verificações).
