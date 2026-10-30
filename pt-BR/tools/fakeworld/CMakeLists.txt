cmake_minimum_required(VERSION 3.21)
project(coop_fakeworld LANGUAGES CXX)

# A biblioteca de responsabilidade fica na pasta vizinha. Ao copiar fakeworld para seu projeto, aponte aqui para onde você
# a mantém (ou vincule sua própria cópia de coop_ownership).
if(NOT TARGET coop_ownership)
  set(COOP_OWNERSHIP_BUILD_TESTS OFF CACHE BOOL "" FORCE)
  add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../ownership ${CMAKE_BINARY_DIR}/ownership)
endif()

add_library(coop_fakeworld STATIC
  src/wire.cpp src/net.cpp src/effect.cpp src/world.cpp src/messages.cpp
  src/machine_link.cpp src/machine_sim.cpp src/machine_host.cpp src/machine_intent.cpp src/cluster.cpp)
target_include_directories(coop_fakeworld PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(coop_fakeworld PUBLIC coop_ownership)
target_compile_features(coop_fakeworld PUBLIC cxx_std_17)

option(COOP_FAKEWORLD_BUILD_TESTS "Build the fake world tests" ${PROJECT_IS_TOP_LEVEL})

if(MSVC)
  target_compile_options(coop_fakeworld PRIVATE /W4 /permissive- /utf-8 /wd4456 /D_CRT_SECURE_NO_WARNINGS)
else()
  target_compile_options(coop_fakeworld PRIVATE -Wall -Wextra)
endif()

if(COOP_FAKEWORLD_BUILD_TESTS)
  # Uma pasta de saída para todas as configurações, para que um script encontre o executável sem precisar conhecer o gerador.
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
  foreach(cfg DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${cfg} ${CMAKE_BINARY_DIR}/bin)
  endforeach()
  add_executable(coop_fakeworld_tests
    tests/main.cpp tests/test_world.cpp tests/test_engine.cpp tests/test_twins.cpp tests/scenarios.cpp)
  target_link_libraries(coop_fakeworld_tests PRIVATE coop_fakeworld)
  target_include_directories(coop_fakeworld_tests PRIVATE tests)
  if(MSVC)
    target_compile_options(coop_fakeworld_tests PRIVATE /W4 /permissive- /utf-8 /wd4456 /D_CRT_SECURE_NO_WARNINGS)
  else()
    target_compile_options(coop_fakeworld_tests PRIVATE -Wall -Wextra)
  endif()
endif()
