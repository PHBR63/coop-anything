cmake_minimum_required(VERSION 3.21)
project(coop_ownership LANGUAGES CXX)

# A biblioteca: dois arquivos, sem dependências. Adicione esta pasta com add_subdirectory() e vincule coop_ownership.
add_library(coop_ownership STATIC src/ownership.cpp)
target_include_directories(coop_ownership PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_compile_features(coop_ownership PUBLIC cxx_std_17)

option(COOP_OWNERSHIP_BUILD_TESTS "Build the ownership tests" ${PROJECT_IS_TOP_LEVEL})

if(MSVC)
  target_compile_options(coop_ownership PRIVATE /W4 /permissive- /utf-8)
else()
  target_compile_options(coop_ownership PRIVATE -Wall -Wextra)
endif()

if(COOP_OWNERSHIP_BUILD_TESTS)
  # Uma pasta de saída para todas as configurações, para que um script encontre o executável sem precisar conhecer o gerador.
  set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
  foreach(cfg DEBUG RELEASE RELWITHDEBINFO MINSIZEREL)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${cfg} ${CMAKE_BINARY_DIR}/bin)
  endforeach()
  add_executable(coop_ownership_tests
    tests/main.cpp tests/test_ownership.cpp tests/scenarios.cpp tests/test_twins.cpp)
  target_link_libraries(coop_ownership_tests PRIVATE coop_ownership)
  target_include_directories(coop_ownership_tests PRIVATE tests)
  if(MSVC)
    target_compile_options(coop_ownership_tests PRIVATE /W4 /permissive- /utf-8 /D_CRT_SECURE_NO_WARNINGS)
  else()
    target_compile_options(coop_ownership_tests PRIVATE -Wall -Wextra)
  endif()
endif()
