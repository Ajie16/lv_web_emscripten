# Emscripten 移植版本

**将 LVGL v8.4.0 移植到 Emscripten，编译为 JavaScript 在浏览器中运行**

> 本分支恢复了 LVGL v8 的 `lv_drivers` 支持。官方上游在迁移到 v9 时移除了 `lv_drivers`（v9 内置了 SDL 驱动）。如需使用 v9，请访问[官方仓库](https://github.com/lvgl/lv_web_emscripten)。

在线效果：[https://lvgl.io/demos](https://lvgl.io/demos)

---

# 快速开始

## 前置条件

- CMake >= 3.12
- Python 3（Emscripten 依赖）
- Git

## 安装 Emscripten SDK

下载 [Emscripten SDK](https://emscripten.org/) 并确保其在 `PATH` 中。

```bash
git clone https://github.com/emscripten-core/emsdk.git
cd emsdk
./emsdk install 3.1.74
./emsdk activate 3.1.74
source ./emsdk_env.sh
```

> **注意：** Emscripten `latest` 可能引入破坏性变更。版本 `3.1.74` 已验证可与此项目配合使用。

---

## 获取项目

```bash
# 带子模块克隆（lvgl v8.4.0 + lv_drivers）
git clone --recursive https://github.com/Ajie16/lv_web_emscripten.git
cd lv_web_emscripten
```

如果已克隆但未使用 `--recursive`：

```bash
git submodule update --init --recursive
```

---

## 构建

```bash
# 确保 Emscripten 在 PATH 中
source <path-to-emsdk>/emsdk_env.sh

# 创建构建目录
mkdir build && cd build

# 配置（默认演示：lv_demo_widgets）
emcmake cmake .. -DLVGL_CHOSEN_DEMO=lv_demo_widgets

# 编译
emmake make -j$(nproc)
```

生成的 `index.html`（及相关文件）将输出到 `build/` 目录。

---

## 运行与测试

需要通过 HTTP 服务器加载生成的 HTML。直接在浏览器中打开文件会因 WASM 的 CORS/安全限制而无法工作。

```bash
cd build
python3 -m http.server 8080
```

然后在浏览器中打开 `http://localhost:8080/index.html`。

---

## 浏览器兼容性

| 浏览器 | 状态 | 说明 |
|--------|------|------|
| **Edge** | ✅ 推荐 | 完全可用 |
| **Chrome** | ⚠️ 部分支持 | Chrome 可能在某些安全策略下阻止本地/localhost WASM。如遇到问题，请使用 Edge 或部署到真实 HTTP 服务器。 |
| **Firefox** | ⚠️ 需要配置 | 如需离线文件访问，请在 `about:config` 中将 `privacy.file_unique_origin` 设为 `false`。 |

---

## 构建选项

### 选择演示程序

```bash
emcmake cmake .. -DLVGL_CHOSEN_DEMO=lv_demo_widgets
```

可用的演示程序取决于 `lvgl/demos/`。常用选项：
- `lv_demo_widgets`
- `lv_demo_benchmark`
- `lv_demo_stress`
- `lv_demo_music`
- `lv_demo_keypad_encoder`

### 内存优化

默认构建分配 **32 MB** 初始 WASM 内存。可在 `CMakeLists.txt` 中减小：

```cmake
# 减小初始内存并允许增长
set_target_properties(index PROPERTIES LINK_FLAGS "... -s INITIAL_MEMORY=8388608 -s ALLOW_MEMORY_GROWTH=1")
```

| 参数 | 默认值 | 优化值 | 说明 |
|------|--------|--------|------|
| `INITIAL_MEMORY` | `33554432` (32MB) | `8388608` (8MB) | 预分配 WASM 堆内存 |
| `ALLOW_MEMORY_GROWTH` | 未设置 | `1` | 允许堆内存按需增长 |

---

## 项目结构

```
lv_web_emscripten/
├── lvgl/                 # LVGL 核心 (v8.4.0) - 官方子模块
├── lv_drivers/           # 显示/输入驱动 - 官方子模块
├── emsdk_adapter/        # 核心应用源码
│   ├── main.c            # 入口、SDL 初始化、主循环
│   ├── lv_conf.h         # LVGL 配置
│   ├── lv_drv_conf.h     # lv_drivers 配置
│   └── lvgl_shell.html   # Emscripten HTML 壳层
├── skills/               # AI 助手技能（构建、运行、测试工具）
│   ├── lvgl-webbuild/    # 一键构建与运行
│   └── lvgl-webview/     # 浏览器自动化测试（截图、点击、测尺寸）
├── CMakeLists.txt        # 构建配置
└── README.md             # 本文件
```

---

## 已知问题

1. **Chrome 本地/localhost WASM 限制**：Chrome 在某些条件下可能拒绝从 localhost 加载 WASM。请使用 Edge 或部署到真实服务器。
2. **SDL2 端口下载失败**：如果 Emscripten 无法从 GitHub 下载 SDL2（网络/代理问题），请手动将所需 SDL2 发行版 zip 下载到 `emsdk/upstream/emscripten/cache/ports/`，并清除缓存锁文件。

---

## 许可证

与 [LVGL](https://github.com/lvgl/lvgl) 相同 — MIT 许可证。
