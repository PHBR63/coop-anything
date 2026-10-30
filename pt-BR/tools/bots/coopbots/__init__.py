"Bots cooperativos independentes de jogo: executor de roteiros, interface de adaptador de ações e mundo cooperativo simulado para testes."
from .adapter import ActionAdapter, MissingAction, Result  # noqa: F401
from .core import (Comparer, Ctx, DictComparer, Machine, Playbook, PlaybookAbort, RunResult, StepFailure,  # noqa: F401
                   run_playbook)
