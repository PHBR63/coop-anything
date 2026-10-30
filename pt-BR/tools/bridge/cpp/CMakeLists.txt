cmake_minimum_required(VERSION 3.16)
project(coopbridge_test CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# O servidor usa somente cabeçalhos. test_server.cpp o incorpora a um jogo simulado; tools/bridge/test_cpp_server.py controla esse
# programa com o cliente Python.
#
#   COOPBRIDGE_INCLUDE   pasta que contém coopbridge/server.h (padrão ../include)
#   COOPBRIDGE_MUTANTS   nomes das variantes de mutação. run_tests.py grava uma cópia com defeito dos cabeçalhos em
#                        ${COOPBRIDGE_MUT_DIR}/<name>/coopbridge/ para cada variante; cada uma recebe seu próprio programa de teste.
set(COOPBRIDGE_INCLUDE "${CMAKE_CURRENT_SOURCE_DIR}/../include" CACHE PATH "folder with coopbridge/server.h")
set(COOPBRIDGE_MUTANTS "" CACHE STRING "mutation twin names")
set(COOPBRIDGE_MUT_DIR "" CACHE PATH "folder with one broken header copy per twin")

add_executable(coopbridge_test test_server.cpp)
target_include_directories(coopbridge_test PRIVATE ${COOPBRIDGE_INCLUDE})
set(_targets coopbridge_test)

foreach(m IN LISTS COOPBRIDGE_MUTANTS)
  add_executable(coopbridge_test_${m} test_server.cpp)
  target_include_directories(coopbridge_test_${m} PRIVATE ${COOPBRIDGE_MUT_DIR}/${m})
  list(APPEND _targets coopbridge_test_${m})
endforeach()

foreach(t IN LISTS _targets)
  if(MSVC)
    target_compile_options(${t} PRIVATE /W4 /permissive- /utf-8 /EHsc)
  else()
    target_compile_options(${t} PRIVATE -Wall -Wextra)
    find_package(Threads REQUIRED)
    target_link_libraries(${t} PRIVATE Threads::Threads)
  endif()
endforeach()
