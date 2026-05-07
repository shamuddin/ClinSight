#!/usr/bin/env python3
"""Simple reverse proxy: port 8000 -> port 3000 for ClinSight frontend+API."""
import http.server, socketserver, urllib.request, urllib.error, sys, os

TARGET = "http://127.0.0.1:3000"
PORT = 8000

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            url = TARGET + self.path
            req = urllib.request.Request(url)
            for h,v in self.headers.items():
                if h.lower() not in ('host','content-length','content-type'):
                    req.add_header(h,v)
            resp = urllib.request.urlopen(req, timeout=30)
            self.send_response(resp.getcode())
            for h,v in resp.getheaders():
                if h.lower() not in ('transfer-encoding','content-encoding'):
                    self.send_header(h,v)
            self.end_headers()
            self.wfile.write(resp.read())
        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")
    def do_POST(self):
        try:
            url = TARGET + self.path
            content_len = int(self.headers.get('Content-Length',0))
            body = self.rfile.read(content_len)
            req = urllib.request.Request(url, data=body, method='POST')
            for h,v in self.headers.items():
                if h.lower() not in ('host','content-length'):
                    req.add_header(h,v)
            resp = urllib.request.urlopen(req, timeout=120)
            self.send_response(resp.getcode())
            for h,v in resp.getheaders():
                if h.lower() not in ('transfer-encoding','content-encoding'):
                    self.send_header(h,v)
            self.end_headers()
            self.wfile.write(resp.read())
        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")
    def log_message(self, format, *args):
        pass  # silent

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), ProxyHandler) as httpd:
        print(f"Proxy on port {PORT} -> {TARGET}")
        httpd.serve_forever()
