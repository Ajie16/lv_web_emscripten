---
name: lvgl-webbuild
description: 构建并运行 LVGL Emscripten Web 演示。当用户需要将 LVGL 编译为 WebAssembly、构建项目、在浏览器中运行演示、切换演示程序或在指定端口提供服务时使用。触发词包括"build"、"编译"、"serve"、"run demo"、"启动"、"运行"、"3060端口"、"构建"、"切换demo"、"Emscripten 编译"或任何涉及 Web 演示本地构建和测试的请求。
---

# LVGL Web 构建与运行

## 前置条件

- CMake >= 3.12
- Python 3
- Git
- Emscripten SDK（已验证版本：3.1.74）在 `PATH` 中

如果缺少 emsdk，按以下步骤安装：

```bash
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install 3.1.74
./emsdk activate 3.1.74
source ./emsdk_env.sh
```

## 快速构建

```bash
source <path-to-emsdk>/emsdk_env.sh
mkdir -p build && cd build
emcmake cmake .. -DLVGL_CHOSEN_DEMO=lv_demo_widgets
emmake make -j$(nproc)
```

输出：`build/index.html`（单文件，内嵌 base64 WASM）。

## 在 3060 端口运行

```bash
cd build
python3 -m http.server 3060
```

访问：`http://localhost:3060/index.html?w=800&h=480`

## 切换演示程序

可用的 `LVGL_CHOSEN_DEMO` 值：
- `lv_demo_widgets`（默认）
- `lv_demo_benchmark`
- `lv_demo_stress`
- `lv_demo_music`
- `lv_demo_keypad_encoder`

切换时建议清理后重新构建：

```bash
rm -rf build/*
cd build
emcmake cmake .. -DLVGL_CHOSEN_DEMO=lv_demo_benchmark && emmake make -j$(nproc)
```

## URL 参数

HTML 壳层（`lvgl_shell.html`）支持以下参数：
- `?w=<宽度>` — 画布宽度（默认：800）
- `?h=<高度>` — 画布高度（默认：480）
- `?example=<名称>` — 示例选择器（默认："default"）

示例：`http://localhost:3060/index.html?w=1024&h=600`

## 一键脚本

使用 `scripts/build-and-serve.sh` 实现一键构建 + 运行：

```bash
./skills/lvgl-webbuild/scripts/build-and-serve.sh [demo名称] [端口]
```

默认值：demo=`lv_demo_widgets`，port=`3060`。
