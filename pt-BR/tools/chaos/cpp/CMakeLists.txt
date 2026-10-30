cmake_minimum_required(VERSION 3.16)
project(coopchaos CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Implementação C++ equivalente a tools/chaos/impair.py, somente em cabeçalho, mais executor de verificação cruzada.
# tools/chaos/xcheck.py executa o controlador e o modelo Python com o mesmo script e compara todos os resultados.
add_executable(chaos_xcheck xcheck.cpp)
target_include_directories(chaos_xcheck PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})

# Compilações de variantes: cada valor de COOPCHAOS_MUTANT quebra um comportamento da implementação C++ equivalente. A verificação cruzada precisa então falhar.
foreach(m 1 2 3 4)
  add_executable(chaos_xcheck_m${m} xcheck.cpp)
  target_include_directories(chaos_xcheck_m${m} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR})
  target_compile_definitions(chaos_xcheck_m${m} PRIVATE COOPCHAOS_MUTANT=${m})
endforeach()

if(MSVC)
  foreach(t chaos_xcheck chaos_xcheck_m1 chaos_xcheck_m2 chaos_xcheck_m3 chaos_xcheck_m4)
    target_compile_options(${t} PRIVATE /W4 /permissive- /utf-8 /fp:precise)
  endforeach()
else()
  # Sem operações de multiplicação e soma fundidas e sem fast-math: a implementação equivalente precisa arredondar exatamente como Python.
  foreach(t chaos_xcheck chaos_xcheck_m1 chaos_xcheck_m2 chaos_xcheck_m3 chaos_xcheck_m4)
    target_compile_options(${t} PRIVATE -Wall -Wextra -ffp-contract=off)
  endforeach()
endif()
