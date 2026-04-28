#!/usr/bin/env python3
"""
LVGL Emscripten HTML Test Tool

Features:
  1. Screenshot the LVGL canvas or full page
  2. Simulate mouse clicks at specified coordinates
  3. Report canvas pixel dimensions (width x height)

Usage:
  python3 test_html.py <url_or_file> [--screenshot <path>] [--click <x,y>] [--wait <ms>]

Examples:
  python3 test_html.py http://localhost:3060/index.html --screenshot out.png
  python3 test_html.py build/index.html --click 400,240 --screenshot clicked.png
  python3 test_html.py http://localhost:3060/index.html --info
"""

import argparse
import os
import sys
import tempfile
import time
import http.server
import socketserver
import threading

from playwright.sync_api import sync_playwright


def find_free_port():
    """Find a free TCP port."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def start_temp_server(directory, port):
    """Start a temporary HTTP server in a background thread."""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

        def log_message(self, format, *args):
            pass  # suppress logs

    httpd = socketserver.TCPServer(("", port), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    return httpd


def resolve_url(target):
    """Convert a local file path to a served URL if necessary."""
    if target.startswith("http://") or target.startswith("https://"):
        return target, None

    abs_path = os.path.abspath(target)
    if not os.path.exists(abs_path):
        print(f"Error: file not found: {abs_path}", file=sys.stderr)
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
    print(f"Serving {directory} at {url}")
    return url, server


def get_canvas_info(page):
    """Return canvas width, height, and bounding box."""
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


def main():
    parser = argparse.ArgumentParser(
        description="Test LVGL Emscripten HTML output"
    )
    parser.add_argument(
        "target",
        help="URL (http://...) or local file path (build/index.html)"
    )
    parser.add_argument(
        "--screenshot", "-s",
        metavar="PATH",
        help="Save screenshot to PATH (captures canvas area)"
    )
    parser.add_argument(
        "--click", "-c",
        metavar="X,Y",
        help="Simulate a mouse click at (X,Y) inside the canvas"
    )
    parser.add_argument(
        "--info", "-i",
        action="store_true",
        help="Print canvas dimensions and exit"
    )
    parser.add_argument(
        "--wait", "-w",
        type=int,
        default=3000,
        help="Wait N milliseconds for WASM init before screenshot/click (default: 3000)"
    )
    parser.add_argument(
        "--full-page",
        action="store_true",
        help="Screenshot the full page instead of just the canvas"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)"
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Show the browser window (useful for debugging)"
    )

    args = parser.parse_args()
    headless = False if args.no_headless else args.headless

    url, server = resolve_url(args.target)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        print(f"Navigating to {url} ...")
        page.goto(url, wait_until="networkidle")

        # Wait for WASM initialization
        if args.wait > 0:
            print(f"Waiting {args.wait}ms for WASM init...")
            time.sleep(args.wait / 1000.0)

        # Get canvas info
        info = get_canvas_info(page)
        if info is None:
            print("Error: No <canvas> element found on page.", file=sys.stderr)
            browser.close()
            sys.exit(1)

        print(
            f"Canvas size: {info['elementWidth']}x{info['elementHeight']} px "
            f"(CSS: {info['cssWidth']}x{info['cssHeight']} px)"
        )

        if args.info:
            browser.close()
            return

        # Screenshot
        if args.screenshot:
            os.makedirs(os.path.dirname(os.path.abspath(args.screenshot)) or ".", exist_ok=True)
            if args.full_page:
                page.screenshot(path=args.screenshot, full_page=True)
            else:
                canvas = page.locator("canvas")
                canvas.screenshot(path=args.screenshot)
            print(f"Screenshot saved: {args.screenshot}")

        # Click
        if args.click:
            try:
                x, y = map(int, args.click.split(","))
            except ValueError:
                print("Error: --click must be in format X,Y (e.g. 400,240)", file=sys.stderr)
                browser.close()
                sys.exit(1)

            canvas = page.locator("canvas")
            box = canvas.bounding_box()
            click_x = box["x"] + x
            click_y = box["y"] + y
            page.mouse.click(click_x, click_y)
            print(f"Clicked at canvas ({x}, {y}) => screen ({click_x:.1f}, {click_y:.1f})")

            # Wait a bit after click for UI to react
            time.sleep(0.5)

            # Re-screenshot if requested after click
            if args.screenshot and not args.full_page:
                canvas.screenshot(path=args.screenshot)
                print(f"Post-click screenshot saved: {args.screenshot}")

        browser.close()

    if server:
        server.shutdown()


if __name__ == "__main__":
    main()
