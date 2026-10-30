#!/usr/bin/env bash
# Inicia uma cópia de TESTE de Crimson Desert (nunca a instalação real) via Proton, fora da interface do Steam.
# Estrutura sob $1: testinst/game (cópia da instalação por hardlinks, com uma cópia real de bin64), testinst/compatdata (prefixo copiado).
# O modo janela 1280x720 vem de user_engine_option_save.xml no prefixo de teste (_displayType Windowed, _viewportSize 1280 720).
# STEAM_ROOT: pasta do cliente Steam; STEAM_HOME: o HOME usado pelo Steam (difere no Steam instalado por snap/flatpak).
set -uo pipefail
W=$(realpath "$1"); STEAM=${STEAM_ROOT:?}; C=$STEAM/steamapps/common
export HOME=${STEAM_HOME:-$HOME}
export STEAM_COMPAT_CLIENT_INSTALL_PATH=$STEAM STEAM_COMPAT_DATA_PATH=$W/testinst/compatdata
export SteamAppId=3321460 SteamGameId=3321460
export PROTON_LOG=1 PROTON_LOG_DIR=$W/harness
export WINEDLLOVERRIDES="winmm=n,b"   # Ultimate ASI Loader como winmm.dll
cd "$W/testinst/game/bin64"
exec "$C/SteamLinuxRuntime_4/run" -- "$C/Proton - Experimental/proton" waitforexitandrun "$W/testinst/game/bin64/CrimsonDesert.exe"
