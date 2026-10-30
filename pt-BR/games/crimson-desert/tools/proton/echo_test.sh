#!/usr/bin/env bash
# Teste de eco em um PC: retransmissor cdmp_peer + cópia de teste do jogo; encerra o retransmissor depois.
# Estrutura sob $1 como em run_game.sh, mais harness/ (estes scripts e seus logs), cdmp/build-x/bin/cdmp_peer.exe
# e wineprefix-tests/ (prefixo Wine temporário para o retransmissor). STEAM_ROOT: pasta do cliente Steam.
W=$(realpath "$1"); C=${STEAM_ROOT:?}/steamapps/common
export WINEPREFIX=$W/wineprefix-tests WINEDEBUG=-all
"$C/SteamLinuxRuntime_4/run" -- "$C/Proton - Experimental/files/bin/wine" "$W/cdmp/build-x/bin/cdmp_peer.exe" --mode relay --delay ${PEER_DELAY:-50} --offset 0 ${PEER_EXTRA:-} > "$W/harness/peer.log" 2>&1 &
sleep 8
timeout 900 "$W/harness/run_game.sh" "$W" > "$W/harness/game-echo.log" 2>&1; rc=$?
"$C/SteamLinuxRuntime_4/run" -- "$C/Proton - Experimental/files/bin/wineserver" -k 2>/dev/null
wait
echo "game exited: $rc"
