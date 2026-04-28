---
name: lvgl-webview
description: 使用浏览器自动化测试和检查 LVGL Emscripten HTML 输出。当用户需要对 LVGL Web 演示进行截图、在画布上模拟鼠标点击、测量画布尺寸或验证编译后的 WASM 演示渲染结果时使用。触发词包括"截图"、"screenshot"、"click"、"点击"、"test html"、"canvas size"、"像素"、"测试"、"webview"或任何涉及浏览器端 LVGL 演示视觉验证的请求。
---

# LVGL Web 视图测试

## 前置条件

- Python 3.8+
- Playwright（首次运行会自动通过捆绑的虚拟环境安装）

首次运行会在 `skills/.venv/` 下创建虚拟环境并安装依赖。

## 功能

| 功能 | 命令参数 | 说明 |
|------|---------|------|
| **截图** | `--screenshot <路径>` | 截取 `<canvas>` 元素（使用 `--full-page` 截取整页） |
| **模拟点击** | `--click X,Y` | 在画布左上角为原点的 `(X,Y)` 位置发送鼠标点击 |
| **画布信息** | `--info` | 打印画布元素尺寸和 CSS 尺寸 |
| **WASM 等待** | `--wait <毫秒>` | 操作前延迟，等待 WASM 初始化完成（默认：3000 毫秒） |

## 使用方法

### 激活环境

```bash
source skills/.venv/bin/activate
```

### 1. 截图

```bash
# 对已运行的服务截图
python3 skills/lvgl-webview/scripts/test_html.py \
    http://localhost:3060/index.html \
    --screenshot screenshot.png

# 对本地文件截图（自动启动临时 HTTP 服务器）
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html \
    --screenshot screenshot.png
```

### 2. 模拟点击 + 截图

```bash
python3 skills/lvgl-webview/scripts/test_html.py \
    http://localhost:3060/index.html \
    --click 400,240 \
    --screenshot after_click.png \
    --wait 5000
```

> `--click X,Y` 坐标以 **画布左上角** 为原点。

### 3. 仅获取画布尺寸

```bash
python3 skills/lvgl-webview/scripts/test_html.py \
    http://localhost:3060/index.html \
    --info
```

输出示例：
```
Canvas size: 800x480 px (CSS: 800x480 px)
```

### 4. 整页截图

```bash
python3 skills/lvgl-webview/scripts/test_html.py \
    http://localhost:3060/index.html \
    --screenshot full.png \
    --full-page
```

## 捆绑脚本

```bash
skills/lvgl-webview/scripts/test_html.py <url或文件> [选项]
```

常用选项：
- `--screenshot 路径` — 保存截图
- `--click X,Y` — 模拟鼠标点击
- `--info` — 打印画布尺寸后退出
- `--wait 3000` — 等待 WASM 初始化的毫秒数
- `--full-page` — 截取整页而非仅画布
- `--no-headless` — 显示浏览器窗口（用于调试）
