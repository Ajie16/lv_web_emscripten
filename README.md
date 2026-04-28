# Emscripten port

**LVGL v8.4.0 ported to Emscripten to be converted to JavaScript**

> This fork restores `lv_drivers` support for LVGL v8 compatibility. The upstream removed `lv_drivers` when migrating to v9 (built-in SDL drivers). If you need v9, use the [official repo](https://github.com/lvgl/lv_web_emscripten).

The result looks like this: [https://lvgl.io/demos](https://lvgl.io/demos)

---

# How to get started

## Prerequisites

- CMake >= 3.12
- Python 3 (for Emscripten)
- Git

## Install Emscripten SDK

Download the [Emscripten SDK](https://emscripten.org/) and make sure it is in your `PATH`.

```bash
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install 3.1.74
./emsdk activate 3.1.74
source ./emsdk_env.sh
```

> **Note:** Emscripten `latest` may introduce breaking changes. Version `3.1.74` is verified to work with this project.

---

## Get the project

```bash
# Clone with submodules (lvgl v8.4.0 + lv_drivers)
git clone --recursive https://github.com/Ajie16/lv_web_emscripten.git
cd lv_web_emscripten
```

If you already cloned without `--recursive`:

```bash
git submodule update --init --recursive
```

---

## Build

```bash
# Ensure Emscripten is in PATH
source <path-to-emsdk>/emsdk_env.sh

# Create build directory
mkdir build && cd build

# Configure (default demo: lv_demo_widgets)
emcmake cmake .. -DLVGL_CHOSEN_DEMO=lv_demo_widgets

# Build
emmake make -j$(nproc)
```

The output `index.html` (and supporting files) will be generated in the `build/` directory.

---

## Serve and test

You need an HTTP server to load the generated HTML. Simply opening the file directly in a browser will not work due to CORS/security restrictions on WASM.

```bash
cd build
python3 -m http.server 8080
```

Then open `http://localhost:8080/index.html` in your browser.

---

## Browser compatibility

| Browser | Status | Notes |
|---------|--------|-------|
| **Edge** | ✅ Recommended | Fully functional |
| **Chrome** | ⚠️ Partial | Chrome may block local/localhost WASM under certain security policies. Use Edge or a real HTTP server if issues occur. |
| **Firefox** | ⚠️ Needs config | For offline file access, set `privacy.file_unique_origin` to `false` in `about:config`. |

---

## Build options

### Choose a demo

```bash
emcmake cmake .. -DLVGL_CHOSEN_DEMO=lv_demo_widgets
```

Available demos depend on `lvgl/demos/`. Common options:
- `lv_demo_widgets`
- `lv_demo_benchmark`
- `lv_demo_stress`

### Memory optimization

The default build allocates **32 MB** initial WASM memory. You can reduce this in `CMakeLists.txt`:

```cmake
# Reduce initial memory and allow growth
set_target_properties(index PROPERTIES LINK_FLAGS "... -s INITIAL_MEMORY=8388608 -s ALLOW_MEMORY_GROWTH=1")
```

| Flag | Default | Optimized | Description |
|------|---------|-----------|-------------|
| `INITIAL_MEMORY` | `33554432` (32MB) | `8388608` (8MB) | Pre-allocated WASM heap |
| `ALLOW_MEMORY_GROWTH` | Not set | `1` | Allow heap to grow on demand |

---

## Project structure

```
lv_web_emscripten/
├── lvgl/                 # LVGL core (v8.4.0) - official submodule
├── lv_drivers/           # Display/input drivers - official submodule
├── emsdk_adapter/        # Core application sources
│   ├── main.c            # Entry point, SDL init, main loop
│   ├── lv_conf.h         # LVGL configuration
│   ├── lv_drv_conf.h     # lv_drivers configuration
│   └── lvgl_shell.html   # Emscripten HTML shell
├── skills/               # AI agent skills (build & serve helpers)
├── CMakeLists.txt        # Build configuration
└── README.md             # This file
```

---

## Known issues

1. **Chrome local/localhost WASM restrictions**: Chrome may refuse to load WASM from localhost under certain conditions. Use Edge or deploy to a real server.
2. **SDL2 port download failure during build**: If Emscripten fails to download SDL2 from GitHub (network/proxy issues), manually download the required SDL2 release zip to `emsdk/upstream/emscripten/cache/ports/` and clear the cache lock file.

---

## License

Same as [LVGL](https://github.com/lvgl/lvgl) - MIT license.
