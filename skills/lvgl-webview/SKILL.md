---
name: lvgl-webview
description: Test and inspect LVGL Emscripten HTML output using browser automation. Use when the user wants to screenshot the LVGL web demo, simulate mouse clicks on the canvas, measure canvas dimensions, or verify the rendered output of the compiled WASM demo. Triggers include "截图", "screenshot", "click", "点击", "test html", "canvas size", "像素", "测试", or any request involving visual verification of the browser-based LVGL demo.
---

# LVGL Emscripten HTML Test

## Prerequisites

- Python 3.8+
- Playwright (installed automatically via bundled venv)

The first run will create a virtual environment under `skills/.venv/` and install dependencies.

## Features

| Feature | Command flag | Description |
|---------|-------------|-------------|
| **Screenshot** | `--screenshot <path>` | Capture the `<canvas>` element (or full page with `--full-page`) |
| **Simulate click** | `--click X,Y` | Send a mouse click at `(X,Y)` relative to the canvas top-left |
| **Canvas info** | `--info` | Print canvas element & CSS dimensions |
| **WASM wait** | `--wait <ms>` | Delay before actions to let WASM initialize (default: 3000 ms) |

## Usage

### Activate environment

```bash
source skills/.venv/bin/activate
```

### 1. Screenshot

```bash
# Screenshot a running server
python3 skills/lvgl-webview/scripts/test_html.py \
    http://localhost:3060/index.html \
    --screenshot screenshot.png

# Screenshot a local file (auto-starts temp HTTP server)
python3 skills/lvgl-webview/scripts/test_html.py \
    build/index.html \
    --screenshot screenshot.png
```

### 2. Simulate click + screenshot

```bash
python3 skills/lvgl-webview/scripts/test_html.py \
    http://localhost:3060/index.html \
    --click 400,240 \
    --screenshot after_click.png \
    --wait 5000
```

> `--click X,Y` coordinates are relative to the **canvas top-left**.

### 3. Get canvas dimensions only

```bash
python3 skills/lvgl-webview/scripts/test_html.py \
    http://localhost:3060/index.html \
    --info
```

Output example:
```
Canvas size: 800x480 px (CSS: 800x480 px)
```

### 4. Full-page screenshot

```bash
python3 skills/lvgl-webview/scripts/test_html.py \
    http://localhost:3060/index.html \
    --screenshot full.png \
    --full-page
```

## Bundled Script

```bash
skills/lvgl-webview/scripts/test_html.py <url_or_file> [options]
```

Common options:
- `--screenshot PATH` — save screenshot
- `--click X,Y` — simulate mouse click
- `--info` — print canvas size and exit
- `--wait 3000` — milliseconds to wait for WASM init
- `--full-page` — screenshot entire page instead of canvas only
- `--no-headless` — show browser window for debugging
