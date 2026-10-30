---
name: coop-sync-testing
description: "Criar e testar sincronização cooperativa com as ferramentas prontas em tools/: ponte RPC interna e inspetor ao vivo, recarregamento do núcleo, simulador de caos UDP, gravador de eventos que reduz a primeira dessincronização a um teste de regressão, fuzzer com sementes e oráculos de invariantes, responsabilidade sobre atores com épocas, mundo simulado, reserva e conjunto de instâncias já inicializadas, cenários JSON, bots com roteiros e verificador de sincronização de animações."
---

<a id="co-op-sync-testing-with-the-hub-tools"></a>
# Testes de sincronização cooperativa com as ferramentas do projeto

Cada ferramenta fica em `tools/<name>/`, com README, testes, variantes de mutação e um comando que exibe `ALL OK`. Execute todas com `python -I tools/test_all.py`. Foram generalizadas a partir do projeto fnv-coop; particularidades de cada jogo ficam em um arquivo de configuração ou em um adaptador escrito por você.

| Necessidade | Ferramenta | Guia |
|---|---|---|
| Latência, perda, reordenação, duplicação e partições entre clientes reais | `tools/chaos` | `playbook/network-chaos-testing.md` |
| Encontrar a primeira divergência entre 2 a 4 máquinas, reduzir o caso e gerar teste de regressão | `tools/flight` | `playbook/desync-hunting.md` |
| Milhares de sessões com N jogadores e sementes reproduzíveis, verificadas por invariantes | `tools/fuzz` | `playbook/fuzzing-coop-sync.md` |
| Um responsável por NPC, épocas e transferência sem duplicatas | `tools/ownership` | `playbook/actor-ownership.md` |
| Testar sincronização sem iniciar o jogo | `tools/fakeworld` | `playbook/fake-world-testing.md` |
| Executar várias cópias com segurança e reutilizar instâncias já inicializadas | `tools/gameslot`, `tools/gamepool` | `playbook/multi-instance-testing.md` |
| Estados iniciais conhecidos e reinicialização sem encerrar | `tools/scenarios` | `playbook/bots-and-playbooks.md` |
| Sessões cooperativas com vários bots e comparação de estado após cada etapa | `tools/bots` | `playbook/bots-and-playbooks.md` |
| Jogadores remotos com animação e posição corretas | `tools/animcheck` | `playbook/animation-sync-checks.md` |
| Controlar o jogo pelos testes (console, estado, salvar, carregar, captura de tela) e observar todas as cópias ao vivo | `tools/bridge`, `tools/inspect` | `playbook/in-game-bridge.md` |
| Aplicar uma alteração de código sem reiniciar o jogo | `tools/hotreload` | `playbook/hot-reloading-your-mod.md` |
| Uma variante para cada correção; vários agentes compartilhando a mesma árvore de compilação | `tools/mutants`, `tools/buildlock` | `playbook/fast-iteration.md` |
| Sincronização da história: enviar efeitos, não reexecutar scripts | apenas projeto arquitetural | `playbook/effect-capture-story-sync.md` |

Ordem que funciona:
1. Modele primeiro o mundo (padrão `fakeworld`) e adapte o núcleo de sincronização à interface de alvo do fuzzer. Corrija a causa de toda falha de oráculo; nunca afrouxe o oráculo.
2. Adicione o gravador de eventos ao mod em todas as máquinas. Cada relato de dessincronização vira um registro reduzido e um teste de regressão.
3. Use responsabilidade com épocas para tudo que for simulado (NPCs, objetos físicos).
4. Depois, clientes reais: `gameslot` e `gamepool` para executar cópias, `scenarios` para estados iniciais, roteiros de `bots` para ações cooperativas, `chaos` entre as máquinas e `animcheck` nos fluxos de sondagem.
5. Toda correção é distribuída com um teste e uma variante de mutação que o teste precisa detectar.
6. Mantenha curtas as rodadas dentro do jogo (`playbook/fast-iteration.md`): troque o núcleo em vez de reiniciar, use salvamentos preparados, esperas por eventos, `--from-step`, `--timescale`, pares em paralelo e motivos de falha que identifiquem a causa.

Nunca inicie uma cópia do jogo sem reservar uma vaga, nunca encerre um processo que você não iniciou e nunca altere a instalação ou os salvamentos do usuário.
