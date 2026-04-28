cmake_minimum_required(VERSION 3.12)
project (lv_emscripten)

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -O2 -s USE_SDL=2")

include_directories(${PROJECT_SOURCE_DIR} ${PROJECT_SOURCE_DIR}/emscripten_core)

add_subdirectory(lvgl)
file(GLOB MY_SOURCES "emscripten_core/*.c")
file(GLOB_RECURSE LV_DRIVERS_SOURCES "lv_drivers/*.c")
set(SOURCES ${MY_SOURCES} ${LV_DRIVERS_SOURCES})

add_executable(index ${SOURCES})

if(NOT LVGL_CHOSEN_DEMO)
    set(LVGL_CHOSEN_DEMO lv_demo_widgets)
endif()
set_source_files_properties(emscripten_core/main.c PROPERTIES COMPILE_FLAGS -DCHOSEN_DEMO=${LVGL_CHOSEN_DEMO})

set(CMAKE_EXECUTABLE_SUFFIX ".html")
target_link_libraries(index
    lvgl
    lvgl_examples
    lvgl_demos
    SDL2
)
set_target_properties(index PROPERTIES LINK_FLAGS "--shell-file ${PROJECT_SOURCE_DIR}/emscripten_core/lvgl_shell.html -s SINGLE_FILE=1 -s INITIAL_MEMORY=33554432")
