"""Screenshot every scene of built artifacts at phone and laptop width, with headless Chrome.

Usage:
  python shoot_scenes.py <dist-dir> [slug ...] [--out shots] [--scenes 4] [--widths 360,680]

<dist-dir> holds one folder per artifact (dist/<slug>/index.html, as build.mjs writes).
For each slug it captures scenes 1..N at the first width and scene 1 at the others, then
(if Pillow is installed) joins them into shots/<slug>.png so you can look at a whole
artifact in one image. Look at every sheet: overlapping labels, text spilling out of pills,
bars running into knobs and empty scenes are only visible here.

Scenes are reached with window.__alcScene(k) (motion.js scenes()) or a global enter(k).
Engines without either only get scene 1.

Chrome: set CHROME to a Chrome, Edge, Chromium or chrome-headless-shell binary, or the
script looks in the usual places. Headless screenshots work even when your own browser
pane is hidden, where in-app screenshots freeze or come back garbled.
"""
import argparse
import functools
import http.server
import os
import shutil
import subprocess
import sys
import threading
from pathlib import Path

HARNESS = """<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#fff}
iframe{border:0;display:block;width:100%;height:1400px}</style></head><body><iframe id="f"></iframe><script>
const P=new URLSearchParams(location.search),n=P.get('n'),k=+(P.get('k')||0);
const SHIM=`<script>window.AlcherisArtifact={track(){},complete(){},submit(){},resize(h){parent.document.getElementById('f').style.height=h+'px'}};<\\/script>`;
fetch('/'+n+'/index.html').then(r=>r.text()).then(html=>{
  f.srcdoc=html.replace('<head>','<head><base href="'+location.origin+'/'+n+'/">'+SHIM);
  f.onload=()=>{const w=f.contentWindow;setTimeout(()=>{if(!k)return;
    if(w.__alcScene)w.__alcScene(k);else if(typeof w.enter==='function')w.enter(k);},1200)}});
</script></body></html>"""


def find_chrome():
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for name in ("chrome-headless-shell", "google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
        if shutil.which(name):
            return shutil.which(name)
    for p in (
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ):
        if Path(p).exists():
            return p
    sys.exit("No Chrome found. Set CHROME to a Chrome, Edge or chrome-headless-shell binary.")


def serve(root):
    class H(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/__shot.html"):
                body = HARNESS.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                super().do_GET()

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, *a):
            pass

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(H, directory=str(root)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd.server_address[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dist")
    ap.add_argument("slugs", nargs="*")
    ap.add_argument("--out", default="shots")
    ap.add_argument("--scenes", type=int, default=4)
    ap.add_argument("--widths", default="360,680")
    a = ap.parse_args()
    dist = Path(a.dist).resolve()
    out = Path(a.out).resolve()
    (out / "raw").mkdir(parents=True, exist_ok=True)
    slugs = a.slugs or sorted(p.name for p in dist.iterdir() if (p / "index.html").exists())
    widths = [int(w) for w in a.widths.split(",")]
    chrome, port = find_chrome(), serve(dist)
    try:
        from PIL import Image, ImageChops, ImageDraw
    except ImportError:
        Image = None
    for slug in slugs:
        shots = [(widths[0], k) for k in range(a.scenes)] + [(w, 0) for w in widths[1:]]
        files = []
        for w, k in shots:
            png = out / "raw" / f"{slug}-{w}-{k + 1}.png"
            subprocess.run([chrome, "--headless", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},1100",
                            f"--virtual-time-budget={7000 if k else 4000}", f"--screenshot={png}",
                            f"http://127.0.0.1:{port}/__shot.html?n={slug}&k={k}"], capture_output=True, timeout=120)
            files.append((w, k, png))
        if Image is None:
            print(slug, "raw shots in", out / "raw")
            continue
        ims = []
        for w, k, png in files:
            im = Image.open(png).convert("RGB")
            box = ImageChops.difference(im, Image.new("RGB", im.size, "white")).getbbox()
            ims.append((f"scene {k + 1} @{w}", im.crop((0, 0, w, min(im.height, box[3] + 12) if box else im.height))))
        sheet = Image.new("RGB", (sum(i.width + 12 for _, i in ims), max(i.height for _, i in ims) + 22), "#d8dae0")
        x, d = 0, ImageDraw.Draw(sheet)
        for label, im in ims:
            d.text((x + 4, 4), f"{slug}  {label}", fill="black")
            sheet.paste(im, (x, 20))
            x += im.width + 12
        sheet.save(out / f"{slug}.png")
        print(slug, "->", out / f"{slug}.png")


if __name__ == "__main__":
    main()
