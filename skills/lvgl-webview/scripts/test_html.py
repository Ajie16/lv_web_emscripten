#!/usr/bin/env python3
"""
LVGL Web 视图测试工具 — 浏览器自动化脚本

功能：
  1. 截图 LVGL Canvas 或整页
  2. 模拟鼠标操作（单击、双击、长按、拖拽、滚轮）
  3. 模拟键盘输入（方向键、回车、ESC、Tab 等）
  4. 获取 Canvas 像素尺寸信息

用法：
  python3 test_html.py <url_or_file> [选项]

示例：
  # 截图
  python3 test_html.py build/index.html --screenshot out.png

  # 单击
  python3 test_html.py build/index.html --click 400,240 --screenshot clicked.png

  # 双击
  python3 test_html.py build/index.html --double-click 400,240

  # 长按 1 秒
  python3 test_html.py build/index.html --long-press 400,240 --duration 1000

  # 拖拽
  python3 test_html.py build/index.html --drag 100,400 --to 700,400

  # 滚轮（模拟编码器）
  python3 test_html.py build/index.html --scroll 5

  # 键盘 — 回车确认
  python3 test_html.py build/index.html --key Enter

  # 键盘 — 方向键导航
  python3 test_html.py build/index.html --key ArrowDown --key ArrowRight --key Enter

  # 获取尺寸
  python3 test_html.py build/index.html --info
"""

import argparse
import os
import sys
import time
import http.server
import socketserver
import threading

from playwright.sync_api import sync_playwright


def find_free_port():
    """查找一个空闲的 TCP 端口。"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def start_temp_server(directory, port):
    """在后台线程启动临时 HTTP 服务器。"""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

        def log_message(self, format, *args):
            pass  # 静默日志

    httpd = socketserver.TCPServer(("", port), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def resolve_url(target):
    """将本地文件路径转换为可访问的 URL（如需要则启动临时服务器）。"""
    if target.startswith("http://") or target.startswith("https://"):
        return target, None

    abs_path = os.path.abspath(target)
    if not os.path.exists(abs_path):
        print(f"错误：文件不存在：{abs_path}", file=sys.stderr)
        sys.exit(1)

    if os.path.isfile(abs_path):
        directory = os.path.dirname(abs_path)
        filename = os.path.basename(abs_path)
    else:
        directory = abs_path
        filename = "index.html"

    port = find_free_port()
    server = start_temp_server(directory, port)
    url = f"http://localhost:{port}/{filename}"
    print(f"正在提供 {directory} 的访问：{url}")
    return url, server


def get_canvas_info(page):
    """返回画布的宽度、高度和边界框信息。"""
    info = page.evaluate("""
        () => {
            const canvas = document.querySelector('canvas');
            if (!canvas) return null;
            const rect = canvas.getBoundingClientRect();
            return {
                elementWidth: canvas.width,
                elementHeight: canvas.height,
                cssWidth: rect.width,
                cssHeight: rect.height,
                offsetLeft: rect.left,
                offsetTop: rect.top
            };
        }
    """)
    return info


def parse_xy(text):
    """解析 'X,Y' 字符串为整数元组。"""
    try:
        x, y = map(int, text.split(","))
        return x, y
    except ValueError:
        print(f"错误：坐标格式必须是 X,Y（例如 400,240），收到：{text}", file=sys.stderr)
        sys.exit(1)


def get_canvas_screen_pos(page, canvas_x, canvas_y):
    """将画布相对坐标转换为屏幕绝对坐标。"""
    canvas = page.locator("canvas")
    box = canvas.bounding_box()
    return box["x"] + canvas_x, box["y"] + canvas_y


def main():
    parser = argparse.ArgumentParser(
        description="LVGL Web 视图测试工具 — 截图、模拟鼠标和键盘交互"
    )
    parser.add_argument(
        "target",
        help="URL（http://...）或本地文件路径（build/index.html）"
    )

    # 截图
    parser.add_argument(
        "--screenshot", "-s",
        metavar="路径",
        help="保存截图到指定路径（截取 Canvas 区域）"
    )
    parser.add_argument(
        "--full-page",
        action="store_true",
        help="截取整页而非仅 Canvas"
    )

    # 等待
    parser.add_argument(
        "--wait", "-w",
        type=int,
        default=3000,
        help="操作前等待 WASM 初始化的毫秒数（默认：3000）"
    )

    # 信息显示
    parser.add_argument(
        "--info", "-i",
        action="store_true",
        help="打印 Canvas 尺寸后退出"
    )

    # 鼠标 — 单击
    parser.add_argument(
        "--click", "-c",
        metavar="X,Y",
        help="在 Canvas 的 (X,Y) 位置单击"
    )

    # 鼠标 — 双击
    parser.add_argument(
        "--double-click",
        metavar="X,Y",
        help="在 Canvas 的 (X,Y) 位置双击"
    )

    # 鼠标 — 长按
    parser.add_argument(
        "--long-press",
        metavar="X,Y",
        help="在 Canvas 的 (X,Y) 位置长按"
    )
    parser.add_argument(
        "--duration",
        type=int,
        default=800,
        help="长按持续时间（毫秒，默认：800）"
    )

    # 鼠标 — 拖拽
    parser.add_argument(
        "--drag",
        metavar="X1,Y1",
        help="拖拽起点（Canvas 相对坐标）"
    )
    parser.add_argument(
        "--to",
        metavar="X2,Y2",
        help="拖拽终点（Canvas 相对坐标）"
    )

    # 鼠标 — 滚轮
    parser.add_argument(
        "--scroll",
        type=int,
        metavar="DELTA",
        help="在 Canvas 中心滚动（正值向下/向右，负值向上/向左，模拟编码器）"
    )

    # 键盘 — 单键
    parser.add_argument(
        "--key", "-k",
        action="append",
        metavar="KEY",
        help="发送单个键盘按键（可多次使用）。常用键：Enter, Escape, Tab, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, Space, Backspace"
    )

    # 键盘 — 输入字符串
    parser.add_argument(
        "--type", "-t",
        metavar="TEXT",
        help="输入任意文本（支持字母、数字、符号，模拟连续按键输入）"
    )

    # 浏览器模式
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="显示浏览器窗口（用于调试）"
    )

    args = parser.parse_args()
    headless = not args.no_headless

    url, server = resolve_url(args.target)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        print(f"正在导航到 {url} ...")
        page.goto(url, wait_until="networkidle")

        # 等待 WASM 初始化
        if args.wait > 0:
            print(f"等待 {args.wait}ms 让 WASM 初始化...")
            time.sleep(args.wait / 1000.0)

        # 获取 Canvas 信息
        info = get_canvas_info(page)
        if info is None:
            print("错误：页面中未找到 <canvas> 元素。", file=sys.stderr)
            browser.close()
            sys.exit(1)

        print(
            f"Canvas 尺寸：{info['elementWidth']}x{info['elementHeight']} px "
            f"（CSS：{info['cssWidth']}x{info['cssHeight']} px）"
        )

        if args.info:
            browser.close()
            return

        # === 鼠标操作 ===

        # 单击
        if args.click:
            cx, cy = parse_xy(args.click)
            sx, sy = get_canvas_screen_pos(page, cx, cy)
            page.mouse.click(sx, sy)
            print(f"单击：Canvas ({cx}, {cy}) => 屏幕 ({sx:.1f}, {sy:.1f})")
            time.sleep(0.3)

        # 双击
        if args.double_click:
            cx, cy = parse_xy(args.double_click)
            sx, sy = get_canvas_screen_pos(page, cx, cy)
            page.mouse.dblclick(sx, sy)
            print(f"双击：Canvas ({cx}, {cy}) => 屏幕 ({sx:.1f}, {sy:.1f})")
            time.sleep(0.3)

        # 长按
        if args.long_press:
            cx, cy = parse_xy(args.long_press)
            sx, sy = get_canvas_screen_pos(page, cx, cy)
            page.mouse.move(sx, sy)
            page.mouse.down()
            print(f"长按：Canvas ({cx}, {cy})，持续 {args.duration}ms...")
            time.sleep(args.duration / 1000.0)
            page.mouse.up()
            print("长按释放")
            time.sleep(0.3)

        # 拖拽
        if args.drag:
            if not args.to:
                print("错误：--drag 必须与 --to 一起使用", file=sys.stderr)
                browser.close()
                sys.exit(1)
            x1, y1 = parse_xy(args.drag)
            x2, y2 = parse_xy(args.to)
            sx1, sy1 = get_canvas_screen_pos(page, x1, y1)
            sx2, sy2 = get_canvas_screen_pos(page, x2, y2)
            page.mouse.move(sx1, sy1)
            page.mouse.down()
            print(f"拖拽：Canvas ({x1},{y1}) => ({x2},{y2})")
            time.sleep(0.1)
            page.mouse.move(sx2, sy2)
            page.mouse.up()
            time.sleep(0.3)

        # 滚轮
        if args.scroll is not None:
            canvas = page.locator("canvas")
            box = canvas.bounding_box()
            cx, cy = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
            delta = args.scroll
            page.mouse.move(cx, cy)
            # 水平滚轮模拟编码器（LVGL encoder 通常映射到水平滚轮）
            page.mouse.wheel(delta_x=delta * 10, delta_y=0)
            print(f"滚轮：Canvas 中心，delta={delta}")
            time.sleep(0.3)

        # === 键盘操作 ===

        if args.key:
            for key in args.key:
                page.keyboard.press(key)
                print(f"按键：{key}")
                time.sleep(0.2)

        if args.type:
            page.keyboard.type(args.type)
            print(f"输入文本：{args.type}")
            time.sleep(0.2)

        # === 截图 ===

        if args.screenshot:
            os.makedirs(os.path.dirname(os.path.abspath(args.screenshot)) or ".", exist_ok=True)
            if args.full_page:
                page.screenshot(path=args.screenshot, full_page=True)
            else:
                canvas = page.locator("canvas")
                canvas.screenshot(path=args.screenshot)
            print(f"截图已保存：{args.screenshot}")

        browser.close()

    if server:
        server.shutdown()


if __name__ == "__main__":
    main()
