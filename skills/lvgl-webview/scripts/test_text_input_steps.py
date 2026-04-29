#!/usr/bin/env python3
"""
多步骤文本输入测试：打开 lv_demo_widgets，点击 Username 输入框，输入 helloworld，
过程中每个步骤生成截图。
"""
import argparse
import asyncio
import os
import sys
import tempfile
import http.server
import socketserver
import threading

from playwright.async_api import async_playwright


def start_temp_server(directory, port=0):
    """在指定目录启动临时 HTTP 服务器，返回 (server, url)"""
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
        def log_message(self, format, *args):
            pass

    server = ReusableTCPServer(("127.0.0.1", port), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    actual_port = server.server_address[1]
    return server, f"http://127.0.0.1:{actual_port}/index.html"


async def run_steps(url: str, out_dir: str, wait_ms: int = 4000):
    os.makedirs(out_dir, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 800, "height": 600})

        print(f"[Step 0] 导航到 {url} ...")
        await page.goto(url, wait_until="networkidle")
        await asyncio.sleep(wait_ms / 1000)

        # 获取 canvas 元素
        canvas = await page.query_selector("canvas")
        if not canvas:
            print("未找到 canvas 元素！")
            await browser.close()
            return

        box = await canvas.bounding_box()
        print(f"Canvas 尺寸：{box['width']}x{box['height']} px")

        # --- Step 1: 初始状态 ---
        step1 = os.path.join(out_dir, "step1_initial.png")
        await canvas.screenshot(path=step1)
        print(f"[Step 1] 初始状态截图已保存：{step1}")

        # --- Step 2: 点击 Username 输入框 ---
        # 根据 lv_demo_widgets Profile 页面布局，Username 框在左侧中部偏下
        # 相对于 canvas 的坐标（800x480），Username 输入框中心约在 (140, 315)
        username_x = box["x"] + 140
        username_y = box["y"] + 315
        print(f"[Step 2] 点击 Username 输入框 ({username_x}, {username_y}) ...")
        await page.mouse.click(username_x, username_y)
        await asyncio.sleep(1.5)

        step2 = os.path.join(out_dir, "step2_focus.png")
        await canvas.screenshot(path=step2)
        print(f"[Step 2] 获取焦点后截图已保存：{step2}")

        # --- Step 3: 输入 helloworld（逐字符，每次截图）---
        text = "helloworld"
        for i, ch in enumerate(text, start=1):
            await page.keyboard.press(ch)
            await asyncio.sleep(0.3)
            step_path = os.path.join(out_dir, f"step3_input_{i:02d}_{ch}.png")
            await canvas.screenshot(path=step_path)
            print(f"[Step 3-{i:02d}] 输入 '{ch}' 后截图已保存：{step_path}")

        # --- Step 4: 最终状态 ---
        await asyncio.sleep(0.5)
        step4 = os.path.join(out_dir, "step4_final.png")
        await canvas.screenshot(path=step4)
        print(f"[Step 4] 最终状态截图已保存：{step4}")

        await browser.close()
        print("\n所有步骤完成！")


def main():
    parser = argparse.ArgumentParser(description="多步骤文本输入测试")
    parser.add_argument("url", nargs="?", default="", help="目标 URL 或本地 HTML 文件路径")
    parser.add_argument("--out-dir", default="./screenshots", help="截图输出目录")
    parser.add_argument("--wait", type=int, default=4000, help="初始等待毫秒数")
    args = parser.parse_args()

    url = args.url
    if not url:
        # 默认使用 build/index.html
        build_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "build")
        build_dir = os.path.abspath(build_dir)
        if os.path.exists(os.path.join(build_dir, "index.html")):
            server, url = start_temp_server(build_dir)
            print(f"临时 HTTP 服务器已启动：{url}")
        else:
            print("未找到 build/index.html，请指定 URL 或文件路径")
            sys.exit(1)
    elif os.path.isfile(url):
        directory = os.path.dirname(os.path.abspath(url))
        server, url = start_temp_server(directory)
        print(f"临时 HTTP 服务器已启动：{url}")
    elif url.startswith("http://") or url.startswith("https://"):
        pass
    else:
        print(f"无效的目标：{url}")
        sys.exit(1)

    asyncio.run(run_steps(url, args.out_dir, args.wait))


if __name__ == "__main__":
    main()
