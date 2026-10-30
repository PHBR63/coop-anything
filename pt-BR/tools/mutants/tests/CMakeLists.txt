cmake_minimum_required(VERSION 3.15)
project(coop_mut_tests CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Origem de coop_mut.h. run_tests.py aponta aqui para uma cópia com defeito a fim de comprovar que os testes detectam um cabeçalho quebrado.
set(COOP_MUT_HEADER_DIR "${CMAKE_CURRENT_SOURCE_DIR}/.." CACHE PATH "folder with coop_mut.h")

# Estrutura de teste: as variantes podem ser ativadas com COOP_MUT.
add_executable(coop_mut_cpp_tests cpp_under_test.cpp)
target_include_directories(coop_mut_cpp_tests PRIVATE "${COOP_MUT_HEADER_DIR}")
target_compile_definitions(coop_mut_cpp_tests PRIVATE COOP_RUNTIME_MUT)

# Estrutura distribuída: sem COOP_RUNTIME_MUT, portanto COOP_MUT_IF é a constante false.
add_executable(coop_mut_cpp_prod cpp_under_test.cpp)
target_include_directories(coop_mut_cpp_prod PRIVATE "${COOP_MUT_HEADER_DIR}")

set_target_properties(coop_mut_cpp_tests coop_mut_cpp_prod PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/bin")
