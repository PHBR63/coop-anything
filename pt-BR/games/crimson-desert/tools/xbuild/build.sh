#!/usr/bin/env bash
# Uso: build.sh <absolute source dir> [build type]. Exibe BUILD_OK ou BUILD_FAILED.
set -uo pipefail
SRC=$(realpath "$1"); TYPE=${2:-RelWithDebInfo}
podman run --rm -v "$SRC":/src:Z -v cdmp-fetch:/fetch -w /src localhost/cdmp-xbuild:1 bash -c "
  set -e
  cmake -S . -B build-x -G Ninja -DCMAKE_BUILD_TYPE=$TYPE -DCMAKE_TOOLCHAIN_FILE=/opt/clang-cl-msvc.cmake -DFETCHCONTENT_BASE_DIR=/fetch
  cmake --build build-x -j 16
" && echo BUILD_OK || { echo BUILD_FAILED; exit 1; }
