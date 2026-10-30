"""O lado do jogo no executor de cenários: um GameAdapter por instância de jogo em execução (um por jogador).

Escreva uma classe para seu jogo e o executor faz o resto. O executor nunca conversa diretamente com o jogo. Ele fornece a cada
adaptador strings simples: IDs do glossário `objects` do cenário e números e nomes escritos nas etapas.

    class MyGame(GameAdapter):
        OPS = {"op:kill", "op:move", "check:dead", "check:state", "action:fast_travel"}

        def do(self, op, args):              # args: {"ref": "<id>"} para op "kill"
            ...
        def read(self, kind, args):          # kind "dead", args {"ref": "<id>"} -> 0 ou 1
            ...
        def load_save(self, name): ...
        def save_game(self, name): ...
        def reset_state(self, ids): ...      # restaura os valores iniciais dessas chaves de estado, sem recarregar

Tudo que o adaptador não puder fazer é simplesmente omitido de OPS. Uma etapa que precise disso é informada como `blocked`, nunca `pass`.

Ganchos opcionais. Cada um tem um padrão que significa "este jogo não sabe informar", e o executor mantém seu comportamento antigo
(pausa fixa, sem save preparado, sem verificação de ID). Implemente aqueles a que seu jogo pode responder:

    sync_status()            -> dict | None   leituras para esperas por sincronização orientadas a eventos (veja abaixo)
    popup_count()            -> int | None    popups bloqueantes abertos agora (caixas de mensagem, avisos); None = não sabe informar
    dismiss_popup()          -> bool          fecha um popup aberto; True se um foi pressionado
    prepared_names(save)     -> [str]         nomes sob os quais tentar uma cópia preparada de `save`, melhores primeiro
    save_exists(name)        -> bool | None   este save existe; None = não sabe informar
    save_stamp(name)         -> json | None   assinatura de um save (tamanho e horário bastam); None = não sabe informar
    ROLLING_SAVES            -> tuple de nomes que o próprio jogo reescreve; suas assinaturas não provam nada
    data_index()             -> dict | DataIndex | None   IDs conhecidos pelos dados do jogo, para validar cenários

sync_status() responde por ESTA instância; todas as chaves são opcionais:

    role         "host" ou "client" (outro valor, ou None, significa que esta instância não está em uma sessão)
    head         host: até onde vai o fluxo efetivado do host (qualquer número que só aumente)
    applied      cliente: quanto desse fluxo aplicou (mesma unidade de head)
    joined       cliente: True depois de entrar no host
    syncing      cliente: True enquanto ainda aplica sua base inicial
    connected    cliente: False quando o enlace está inativo (padrão True)
    rejected     cliente: texto de uma recusa de entrada, ou None
    digests      host: contadores {"received", "ok", "mismatch", "stale", "rateLimited", "repairs"} dos resumos de estado
                 enviados pelos clientes e comparados pelo host (resumo é uma soma de verificação barata do estado compartilhado)
    desyncs      host: entradas divergentes mais recentes [{"id": número do relato (crescente), "key", "host", "client", "repaired"}]

O executor espera com base nessas leituras após recarregar e retorna assim que a condição se cumpre. Desiste antecipadamente, com motivo
claro, quando nada avança. Um jogo que retorna None (ou lança NotImplementedError ou ScenarioError) mantém a pausa fixa.

data_index() retorna {"<id>": "<kind>"}, em que kind é um de scenlib.KINDS, uma lista de tipos, ou None para "qualquer tipo".
IDs usados pelo cenário que faltarem geram erro que informa o ID conhecido mais próximo. Veja scenlib.DataIndex.
"""


class ScenarioError(Exception):
    "Uma ação foi recusada ou falhou. O executor registra como etapa `error` com este texto."


class GameAdapter:
    OPS = None   # None = "posso fazer tudo"; caso contrário, conjunto de nomes 'op:<op>', 'check:<kind>' e 'action:<name>'
    ROLLING_SAVES = ()   # nomes de saves que o próprio jogo reescreve (autosave, quicksave): uma cópia preparada não é conferida contra eles

    def capabilities(self):
        return None if self.OPS is None else set(self.OPS)

    def do(self, op, args):
        """Executa uma operação que não seja verificação nesta instância. `op` é um de scenlib.OPS (não `wait`, `save`, `load`).
        Lança ScenarioError quando o jogo recusa ou o resultado não é o solicitado."""
        raise NotImplementedError("do(%r)" % op)

    def read(self, kind, args):
        "Responde a um tipo de verificação (veja scenlib.CHECK_KINDS) como número. Booleanos são 1 e 0."
        raise NotImplementedError("read(%r)" % kind)

    def load_save(self, name):
        raise NotImplementedError("load_save")

    def save_game(self, name):
        raise NotImplementedError("save_game")

    def reset_state(self, ids):
        "Restaura os valores iniciais das chaves de estado indicadas (missões, flags, variáveis de script) sem recarregar."
        raise NotImplementedError("reset_state")

    # ---- ganchos opcionais: os padrões dizem "este jogo não sabe informar"
    def sync_status(self):
        "Leituras desta instância para esperas por sincronização orientadas a eventos (docstring do módulo). None = sem leituras."
        return None

    def popup_count(self):
        "Quantos popups bloqueantes estão abertos nesta instância. None = não sabe informar (nesse caso, saves preparados não são possíveis)."
        return None

    def dismiss_popup(self):
        "Fecha um popup aberto. Retorna True quando um foi pressionado. Lança ScenarioError se já estiver fechando."
        raise NotImplementedError("dismiss_popup")

    def prepared_names(self, save):
        """Nomes sob os quais tentar uma cópia preparada de `save`, melhores primeiro. Um segundo nome atende a motores que só aceitam
        determinados prefixos. Nomes usam letras, dígitos, sublinhado e hífen."""
        return ["coop_%s_ready" % save]

    def save_exists(self, name):
        "True ou False quando o jogo sabe dizer se um save existe; None quando não sabe."
        return None

    def save_stamp(self, name):
        "Valor JSON que muda quando o arquivo de save muda (tamanho e horário), ou None quando o jogo não sabe informar."
        return None

    def data_index(self):
        "IDs conhecidos pelos dados do jogo: {\"<id>\": \"<kind>\" | [kinds] | None}, um scenlib.DataIndex, ou None se não houver índice."
        return None
