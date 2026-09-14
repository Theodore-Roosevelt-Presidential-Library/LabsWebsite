#!/usr/bin/env python3
"""
Local preview server that behaves like GitHub Pages.

    python3 tools/serve.py          # http://localhost:8000
    python3 tools/serve.py 8080

The site uses extensionless URLs (/about, not /about.html). GitHub Pages
resolves those to the .html file automatically; neither `open index.html` nor
`python3 -m http.server` does, so local preview needs this one extra rule.

It also mirrors the two Pages behaviours that matter for catching mistakes
before they ship: a trailing slash on a page URL is a 404 (Pages does not
serve /about/), and a missing page returns 404 rather than a directory listing.
"""

import http.server
import os
import pathlib
import socketserver
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class PagesHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(ROOT), **kw)

    def translate_path(self, path):
        local = super().translate_path(path)
        # An extensionless request that matches a .html file — the Pages rule.
        if not os.path.exists(local) and not path.rstrip("/").endswith("/"):
            candidate = local + ".html"
            if os.path.isfile(candidate):
                return candidate
        return local

    def list_directory(self, path):
        # Pages has no directory listings; a bare directory without index.html
        # is a 404 there, so make it a 404 here too.
        self.send_error(404, "No index in this directory (GitHub Pages would 404)")
        return None

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), PagesHandler) as httpd:
    print(f"TRPL Labs — serving {ROOT} at http://localhost:{PORT}")
    print("Extensionless URLs resolve the way GitHub Pages resolves them. Ctrl-C to stop.\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
