#!/bin/bash
set -e

DEMO_NAME="${1:-lv_demo_widgets}"
PORT="${2:-3060}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
BUILD_DIR="${PROJECT_ROOT}/build"

echo "=== LVGL Emscripten Build & Serve ==="
echo "Demo: ${DEMO_NAME}"
echo "Port: ${PORT}"
echo "Project root: ${PROJECT_ROOT}"
echo ""

# Check emsdk
if ! command -v emcc &> /dev/null; then
    echo "Error: emcc not found. Please activate Emscripten SDK first."
    echo "  source <path-to-emsdk>/emsdk_env.sh"
    exit 1
fi

# Ensure submodules are present
if [ ! -f "${PROJECT_ROOT}/lvgl/lvgl.h" ]; then
    echo "Initializing git submodules..."
    cd "${PROJECT_ROOT}"
    git submodule update --init --recursive
fi

# Build
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

echo "=== Running cmake... ==="
emcmake cmake "${PROJECT_ROOT}" -DLVGL_CHOSEN_DEMO="${DEMO_NAME}"

echo "=== Running make... ==="
emmake make -j$(nproc)

echo ""
echo "=== Build complete: ${BUILD_DIR}/index.html ==="

# Clean up port if occupied
echo "=== Checking port ${PORT}... ==="
PID=$(lsof -ti:"${PORT}" 2>/dev/null || true)
if [ -n "$PID" ]; then
    echo "Port ${PORT} is occupied by PID(s): $PID. Killing..."
    echo "$PID" | xargs kill -9 2>/dev/null || true
    sleep 1
    echo "Port ${PORT} cleaned."
else
    echo "Port ${PORT} appears free (no process found by lsof)."
fi

echo ""

# Find an available port starting from the requested one
cd "${BUILD_DIR}"
python3 -c "
import sys
import socket
import socketserver
import http.server

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def find_free_port(start_port, max_attempts=10):
    for offset in range(max_attempts):
        port = start_port + offset
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind(('', port))
            s.close()
            return port
        except OSError:
            s.close()
    return None

def serve_on_port(port):
    with ReusableTCPServer(('', port), http.server.SimpleHTTPRequestHandler) as httpd:
        print(f'Serving HTTP on 0.0.0.0 port {port} (http://localhost:{port}/)')
        print(f'Open: http://localhost:{port}/index.html?w=800&h=480')
        print('Press Ctrl+C to stop the server.')
        print('')
        httpd.serve_forever()

start_port = ${PORT}
actual_port = find_free_port(start_port)

if actual_port is None:
    print(f'Error: Could not find an available port in range {start_port}-{start_port + 9}')
    sys.exit(1)

if actual_port != start_port:
    print(f'Warning: Port {start_port} is occupied at system level (not visible to lsof).')
    print(f'Automatically switched to port {actual_port}.')
    print('')

try:
    serve_on_port(actual_port)
except KeyboardInterrupt:
    print('\nServer stopped.')
    sys.exit(0)
"
