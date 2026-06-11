"""Second download channel for sastra.org: fetches the LIVE site through the
r.jina.ai reader proxy (sastra.org blocks our network directly, but is up;
allorigins proxy proved too flaky).

Only items whose newest Wayback snapshot is 2022+ are attempted (older URLs
were reorganized and 404 on the live site). Walks the list in REVERSE order
so it meets the Wayback channel in the middle. Same output directories and
resume rule (skip existing .txt); 404s are left for the Wayback channel.

r.jina.ai returns readability-extracted markdown; converted to plain text
here. Unkeyed rate limit ~20 rpm => 2 workers with ~5s pacing.
"""
import os
import re
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from download_sastra_org import OUT, build_url_list

META = os.path.join(OUT, "_metadata_live.tsv")
FAILED = os.path.join(OUT, "_failed_live.txt")

io_lock = threading.Lock()
progress = {"done": 0, "total": 0}


def fetch_jina(url):
    out = subprocess.run(
        ["curl", "-s", "--max-time", "120",
         "-A", "Mozilla/5.0 (javanese corpus research; student project)",
         "-w", "\n%{http_code}", "https://r.jina.ai/" + url],
        capture_output=True)
    body = out.stdout.decode("utf-8", errors="replace")
    nl = body.rfind("\n")
    return body[nl + 1:].strip(), body[:nl]


def md_to_text(md):
    """Convert jina reader markdown to plain text; '' if error page."""
    m = re.search(r"^Title:\s*(.*)$", md, re.M)
    title = m.group(1).strip() if m else ""
    title = re.sub(r"\s*-\s*Sastra Jawa$", "", title)
    if "Warning: Target URL returned error" in md or title.startswith("Error:"):
        return title, ""
    i = md.find("Markdown Content:")
    if i == -1:
        return title, ""
    body = md[i + len("Markdown Content:"):]
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", body)          # images
    body = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", body)        # links -> text
    body = re.sub(r"^#{1,6}\s*", "", body, flags=re.M)          # headings
    body = re.sub(r"^\*\s\*\s\*\s*$", "", body, flags=re.M)     # hrules
    body = re.sub(r"[ \t]+", " ", body)
    body = re.sub(r"\n\s*\n+", "\n", body)
    lines = [l.strip() for l in body.split("\n") if l.strip()]
    while lines and (lines[0] == title or lines[0] in ("Judul", "Sambungan", "Citra")):
        lines = lines[1:]
    return title, "\n".join(lines)


def process_item(item):
    cat, url, ts, slug = item
    cat_dir = os.path.join(OUT, cat)
    os.makedirs(cat_dir, exist_ok=True)
    fname = re.sub(r"[^\w\-]", "_", slug)[:150] + ".txt"
    fpath = os.path.join(cat_dir, fname)
    if not os.path.exists(fpath):
        ok = False
        code = ""
        for attempt in range(3):
            try:
                code, body = fetch_jina(url)
            except Exception as e:
                code, body = "exc", str(e)
            if code == "200" and len(body) > 500:
                title, text = md_to_text(body)
                if len(text) > 200:
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(title + "\n" + text + "\n")
                    with io_lock:
                        with open(META, "a", encoding="utf-8") as f:
                            f.write(f"{cat}\t{slug}\t{title}\t{url}\tlive\t"
                                    f"{cat}/{fname}\t{len(text)}\n")
                    ok = True
                break  # extracted, or live page is a 404 -> leave to wayback
            if code in ("429", "503", "502", "exc"):
                time.sleep(60)
            else:
                time.sleep(5)
        if not ok:
            with io_lock:
                with open(FAILED, "a", encoding="utf-8") as f:
                    f.write(f"{url}\tlive\t{code}\n")
        time.sleep(2)  # pacing: with ~7s fetch latency stays under 20 rpm
    with io_lock:
        progress["done"] += 1
        if progress["done"] % 50 == 0:
            print(f"{progress['done']}/{progress['total']}", flush=True)


def main():
    items = [it for it in build_url_list() if it[2] < "2022"]
    items.reverse()
    progress["total"] = len(items)
    print(f"{len(items)} items with pre-2022 snapshots (reverse, via r.jina.ai; "
          f"404s are left to the wayback channel)", flush=True)
    if not os.path.exists(META):
        with open(META, "w", encoding="utf-8") as f:
            f.write("category\tslug\ttitle\turl\tsnapshot\tfile\tchars\n")
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(process_item, items))
    print("finished", flush=True)


if __name__ == "__main__":
    main()
