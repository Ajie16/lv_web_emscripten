---
name: lvgl-webview
description: 使用浏览器自动化测试和检查 LVGL Emscripten HTML 输出。当用户需要对 LVGL Web 演示进行截图、在画布上模拟鼠标点击/双击/长按/拖拽/滚轮、发送键盘按键（方向键/回车/ESC等）、测量画布尺寸或验证编译后的 WASM 演示渲染结果时使用。触发词包括"截图"、"screenshot"、"click"、"点击"、"双击"、"长按"、"拖拽"、"滚轮"、"键盘"、"方向键"、"回车"、"test html"、"canvas size"、"像素"、"测试"、"webview"或任何涉及浏览器端 LVGL 演示交互验证的请求。
---

# LVGL Web 视图测试

## 前置条件

- Python 3.8+
- Playwright（首次运行会自动通过捆绑的虚拟环境安装）

首次运行会在 `skills/.venv/` 下创建虚拟环境并安装依赖。

```bash
source skills/.venv/bin/activate
```

## 功能一览

| 功能 | 命令参数 | 说明 |
|------|---------|------|
| **截图** | `--screenshot <路径>` | 截取 `<canvas>` 元素（加 `--full-page` 截取整页） |
| **单击** | `--click X,Y` | 在画布 `(X,Y)` 位置单击 |
| **双击** | `--double-click X,Y` | 在画布 `(X,Y)` 位置双击 |
| **长按** | `--long-press X,Y` | 在画布 `(X,Y)` 位置长按（默认 800ms） |
| **拖拽** | `--drag X1,Y1 --to X2,Y2` | 从起点拖拽到终点 |
| **滚轮** | `--scroll <delta>` | 在画布中心滚动（模拟编码器输入） |
| **键盘** | `--key <按键>` | 发送键盘按键（可多次使用） |
| **画布信息** | `--info` | 打印画布元素和 CSS 尺寸 |
| **WASM 等待** | `--wait <毫秒>` | 操作前延迟等待 WASM 初始化（默认：3000ms） |

> 所有坐标均以 **画布左上角** 为原点。

---

## 使用示例

### 1. 截图

```bash
# 对运行中的服务截图
python3 skills/lvgl-webview/scripts/test_html.py \
    http://localhost:3060/index.html \
    --screenshot screenshot.png

# 对本地文件截图（自动启动临时 HTTP 服务器）
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html \
    --screenshot screenshot.png

# 整页截图
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html \
    --screenshot full.png --full-page
```

### 2. 鼠标操作

```bash
# 单击
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html --click 400,240

# 双击
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html --double-click 400,240

# 长按 1.5 秒
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html --long-press 400,240 --duration 1500

# 拖拽（从左侧滑到右侧）
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html --drag 100,240 --to 700,240

# 滚轮（模拟编码器，正值向下/向右，负值向上/向左）
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html --scroll 5

# 组合操作：点击 + 截图
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html --click 400,240 --screenshot clicked.png
```

### 3. 键盘操作

```bash
# 按回车确认（适用于 lv_demo_keypad_encoder 等键盘型 demo）
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html --key Enter --screenshot after_enter.png

# 方向键导航 + 回车确认
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html \
    --key ArrowDown --key ArrowRight --key Enter \
    --screenshot navigated.png

# 按 ESC 关闭弹窗
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html --key Escape
```

**常用按键名称：**
- `Enter` — 回车确认
- `Escape` / `Esc` — 取消/关闭
- `ArrowUp` / `ArrowDown` / `ArrowLeft` / `ArrowRight` — 方向键
- `Tab` — 切换焦点
- `Space` — 空格
- `Backspace` — 退格

### 4. 仅获取画布尺寸

```bash
python3 skills/lvgl-webview/scripts/test_html.py \
    http://localhost:3060/index.html --info
```

输出示例：
```
Canvas 尺寸：800x480 px（CSS：800x480 px）
```

### 5. 完整交互流程示例

```bash
# 打开 demo，等待加载，按回车关闭欢迎弹窗，然后截图
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html \
    --wait 5000 \
    --key Enter \
    --screenshot result.png
```

---

## 捆绑脚本

```bash
skills/lvgl-webview/scripts/test_html.py <url或文件> [选项]
```

常用选项：
- `--screenshot 路径` — 保存截图
- `--click X,Y` — 鼠标单击
- `--double-click X,Y` — 鼠标双击
- `--long-press X,Y` — 鼠标长按（配合 `--duration`）
- `--drag X1,Y1 --to X2,Y2` — 鼠标拖拽
- `--scroll delta` — 滚轮滚动
- `--key 按键名` — 键盘按键（可多次使用）
- `--info` — 打印画布尺寸后退出
- `--wait 3000` — 等待 WASM 初始化的毫秒数
- `--full-page` — 截取整页
- `--no-headless` — 显示浏览器窗口（用于调试）
