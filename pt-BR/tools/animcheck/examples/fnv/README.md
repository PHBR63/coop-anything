# <a id="fallout-new-vegas-profile"></a>Perfil de Fallout: New Vegas

`profile.json` é o perfil do animcheck usado com a sonda do modo cooperativo de New Vegas
(`plugin/animprobe` em https://github.com/cranebeaker/fnv-coop).

- **Grupos de animação:** 245 nomes, na ordem do enum público `TESAnimGroup` do xNVSE; assim, um identificador de grupo no fluxo da sonda é um índice nessa lista. As categorias os associam ao que os detectores precisam: `Forward`, `Left` e semelhantes são `walk`; `FastForward` e semelhantes são `run`; `Dodge*` é `dodge`; `Death` é `death`; `Jump*` é `jump`; `Attack*` e `PlaceMine*` são `attack`; `Reload*` é `reload`; `Jam*` é `jam`.
- **Ossos:** os nomes padrão do esqueleto bípede (`Bip01 Pelvis` como raiz, `Bip01 L UpperArm`, `Bip01 L Hand` e o lado direito para a verificação de pose em T, além de coluna, pescoço, cabeça, antebraços, panturrilhas, pés e `Weapon`).
- **Movimentos:** `move_flag_bits` indica que o bit 9 de `move_flags` da sonda representa movimento furtivo e o bit 11 representa natação.
- **Unidades:** cerca de 70 unidades por metro, ângulos em radianos e eixo Z para cima.

O arquivo contém somente nomes. Não inclui arquivos do jogo nem endereços do motor. Use-o como modelo para o perfil de outro jogo: copie-o, substitua os nomes dos ossos, a lista de grupos e as entradas de categorias e execute
`python -I tools/animcheck/cli.py profile your.json`.
