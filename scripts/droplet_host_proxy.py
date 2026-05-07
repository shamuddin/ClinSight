#!/usr/bin/env python3
"""
Quick reverse proxy for ClinSight on droplet host.
- Serves static UI from /opt/clinsight/frontend/react-app/dist/
- Proxies API to container port 3000
- Proxies vLLM text (port 8000) and vision (port 8001) directly on host
"""
import http.server, socketserver, urllib.request, urllib.error, os, sys

DIST_DIR = "/opt/clinsight/frontend/react-app/dist"
API_PROXY = "http://127.0.0.1:3000"
VLLM_TEXT = "http://127.0.0.1:8000"
VLLM_VISION = "http://127.0.0.1:8001"
PORT = 80

PROXY_PATHS = ["/api/", "/judge/", "/demo/", "/health", "/docs", "/openapi.json"]
VLLM_PATHS  = ["/v1/"]

class Handler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Serve from dist directory
        if path == "/" or not os.path.splitext(path)[1]:
            return os.path.join(DIST_DIR, "index.html")
        # Strip leading / and serve from dist
        return os.path.join(DIST_DIR, path.lstrip("/"))

    def do_proxy(self, target_url):
        try:
            url = target_url + self.path
            req = urllib.request.Request(url, method=self.command)
            # Copy headers
            for h in ["Content-Type", "Authorization"]:
                if self.headers.get(h):
                    req.add_header(h, self.headers[h])
            # Body
            body = None
            cl = self.headers.get('Content-Length')
            if cl:
                body = self.rfile.read(int(cl))
                req.data = body
            with urllib.request.urlopen(req, timeout=30) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ("transfer-encoding", "content-length"):
                        self.send_header(k, v)
                self.send_header("Content-Length", len(resp.read()))
                self.end_headers()
                self.wfile.write(resp.read())
        except Exception as e:
            self.send_error(502, str(e))

    def do_GET(self):
        if any(self.path.startswith(p) for p in PROXY_PATHS):
            return self.do_proxy(API_PROXY)
        if any(self.path.startswith(p) for p in VLLM_PATHS):
            # Try text first, fallback to vision
            try:
                return self.do_proxy(VLLM_TEXT)
            except:
                return self.do_proxy(VLLM_VISION)
        return super().do_GET()

    def do_POST(self):
        if any(self.path.startswith(p) for p in PROXY_PATHS):
            return self.do_proxy(API_PROXY)
        if any(self.path.startswith(p) for p in VLLM_PATHS):
            try:
                return self.do_proxy(VLLM_TEXT)
            except:
                return self.do_proxy(VLLM_VISION)
        self.send_error(405)

    def log_message(self, fmt, *args):
        print(f"[{self.client_address[0]}] {fmt % args}")

if __name__ == "__main__":
    os.chdir(DIST_DIR)
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"=== ClinSight Proxy serving on port {PORT} ===")
        print(f"Static files: {DIST_DIR}")
        print(f"API proxy: {API_PROXY}")
        print(f"vLLM text: {VLLM_TEXT}")
        print(f"vLLM vision: {VLLM_VISION}")
        httpd.serve_forever()
