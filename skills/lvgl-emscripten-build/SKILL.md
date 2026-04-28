---
name: lvgl-emscripten-build
description: Build and serve the LVGL Emscripten web demo. Use when the user wants to compile LVGL to WebAssembly, build the project, run the demo in a browser, switch demos, or serve on a specific port. Triggers include "build", "编译", "serve", "run demo", "启动", "运行", "6000端口", or any request involving Emscripten compilation or local testing of the web demo.
---

# LVGL Emscripten Build & Serve

## Prerequisites

- CMake >= 3.12
- Python 3
- Git
- Emscripten SDK (verified: 3.1.74) in `PATH`

If emsdk is missing, install it:

```bash
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install 3.1.74
./emsdk activate 3.1.74
source ./emsdk_env.sh
```

## Quick Build

```bash
source <path-to-emsdk>/emsdk_env.sh
mkdir -p build && cd build
emcmake cmake .. -DLVGL_CHOSEN_DEMO=lv_demo_widgets
emmake make -j$(nproc)
```

Output: `build/index.html` (single self-contained file with base64-embedded WASM).

## Serve on Port 3060

```bash
cd build
python3 -m http.server 3060
```

Open: `http://localhost:3060/index.html?w=800&h=480`

## Switch Demo

Available `LVGL_CHOSEN_DEMO` values:
- `lv_demo_widgets` (default)
- `lv_demo_benchmark`
- `lv_demo_stress`
- `lv_demo_music`

Clean rebuild when switching:

```bash
cd build
rm -rf * && emcmake cmake .. -DLVGL_CHOSEN_DEMO=lv_demo_benchmark && emmake make -j$(nproc)
```

## URL Parameters

The HTML shell (`lvgl_shell.html`) accepts:
- `?w=<width>` — canvas width (default: 800)
- `?h=<height>` — canvas height (default: 480)
- `?example=<name>` — example selector (default: "default")

Example: `http://localhost:3060/index.html?w=1024&h=600`

## Bundled Script

Use `scripts/build-and-serve.sh` for a one-shot build + serve workflow.

```bash
./skills/lvgl-emscripten-build/scripts/build-and-serve.sh [demo_name] [port]
```

Defaults: demo=`lv_demo_widgets`, port=`3060`.
