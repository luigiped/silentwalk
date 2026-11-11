#!/usr/bin/env python3
"""Server locale con supporto Range (206), necessario a Safari iOS per l'audio.
`python3 -m http.server` NON supporta Range: su iPhone l'audio non partirebbe.

Uso: python3 scripts/serve.py [porta]   → http://<IP-del-Mac>:8000/
"""
import os, re, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not rng or not os.path.isfile(path):
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)", rng)
        size = os.path.getsize(path)
        start = int(m.group(1)) if m and m.group(1) else 0
        end = int(m.group(2)) if m and m.group(2) else size - 1
        if m and not m.group(1) and m.group(2):
            start, end = size - int(m.group(2)), size - 1
        end = min(end, size - 1)
        if start > end:
            self.send_error(416); return None
        f = open(path, "rb"); f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._remaining = end - start + 1
        return f

    def copyfile(self, src, dst):
        n = getattr(self, "_remaining", None)
        if n is None:
            return super().copyfile(src, dst)
        while n > 0:
            buf = src.read(min(64 * 1024, n))
            if not buf: break
            try: dst.write(buf)
            except (BrokenPipeError, ConnectionResetError): break
            n -= len(buf)

    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

if __name__ == "__main__":
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"http://0.0.0.0:{port}/")
    ThreadingHTTPServer(("0.0.0.0", port), RangeHandler).serve_forever()
