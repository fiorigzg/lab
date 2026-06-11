"""Download Javanese texts from sastra.org (Yayasan Sastra Lestari) via the
Wayback Machine (the live site is unreachable from this network).

Input:  /tmp/cdx_full.txt  (CDX list: "<original_url> <timestamp>" per line)
Output: corpus_raw/sastra-org/<top-category>/<slug>.txt
        corpus_raw/sastra-org/_metadata.tsv (appended, resume-safe)
        corpus_raw/sastra-org/_failed.txt   (urls that failed all retries)

Each sastra.org article page is one part of a digitized work; the URL slug
contains title, author, year and internal id, e.g.
  kisah-cerita-dan-kronikal/104-novel/295-rangsang-tuban-padmasusastra-1912-516
Pages are deduplicated by the numeric article id of the last URL segment.

Priority order: literature first, then culture/religion, archives, magazines.
"""
import os
import re
import subprocess
import sys
import threading
import time
import html as htmllib
from concurrent.futures import ThreadPoolExecutor

CDX = "/tmp/cdx_full.txt"
OUT = os.path.join(os.path.dirname(__file__), "..", "corpus_raw", "sastra-org")
META = os.path.join(OUT, "_metadata.tsv")
FAILED = os.path.join(OUT, "_failed.txt")

CATEGORY_ORDER = [
    "kisah-cerita-dan-kronikal",
    "agama-dan-kepercayaan",
    "bahasa-dan-budaya",
    "arsip-dan-sejarah",
    "koran-majalah-dan-jurnal",
]

os.makedirs(OUT, exist_ok=True)


def build_url_list():
    """Dedupe by article id; keep newest snapshot."""
    best = {}
    for line in open(CDX):
        parts = line.split()
        if len(parts) != 2:
            continue
        url, ts = parts
        u = re.sub(r"^https?://(www\.)?sastra\.org(:80)?/?", "", url).strip("/")
        if not u or "?" in u:
            continue
        segs = u.split("/")
        if len(segs) < 3 or not re.match(r"\d+-", segs[-1]):
            continue
        cat = segs[0].replace("basa-dan-budaya", "bahasa-dan-budaya")
        if cat not in CATEGORY_ORDER:
            continue
        art_id = segs[-1].split("-", 1)[0]
        key = (cat, art_id)
        if key not in best or ts > best[key][2]:
            best[key] = (cat, url, ts, segs[-1])
    items = list(best.values())
    items.sort(key=lambda x: (CATEGORY_ORDER.index(x[0]), x[3]))
    return items


def fetch(url, ts):
    wb = f"http://web.archive.org/web/{ts}id_/{url}"
    out = subprocess.run(
        ["curl", "-s", "-L", "--compressed", "--max-time", "120",
         "-A", "Mozilla/5.0 (javanese corpus research; contact: student project)",
         "-w", "\n%{http_code}", wb],
        capture_output=True)
    body = out.stdout.decode("utf-8", errors="replace")
    nl = body.rfind("\n")
    code = body[nl + 1:].strip()
    return code, body[:nl]


def extract(raw):
    t = re.search(r"<title>(.*?)</title>", raw, re.S)
    title = htmllib.unescape(t.group(1)).strip() if t else ""
    title = re.sub(r"^Sastra Jawa\s*-\s*", "", title)
    title = re.sub(r"\s*-\s*Sastra Jawa$", "", title)
    # newest (Joomla 4 Cassiopeia, ~2022+) layout
    block = None
    layout = "new"
    i = raw.find("com-content-article__body")
    if i != -1:
        i = raw.find(">", i) + 1  # skip the rest of the opening tag
        block = raw[i:]
        for marker in ("</main>", "<footer",
                       "com-content-article__navigation",
                       '<div class="ysl-foottxt'):
            k = block.find(marker)
            if k != -1:
                block = block[:k]
    if block is None:  # UIkit (~2017-2021) layout
        m = re.search(r'<article class="uk-article"[^>]*>(.*?)</article>', raw, re.S)
        if m:
            block = m.group(1)
    if block is None:  # old (Joomla ja_purity, ~2013-2016) layout
        layout = "old"
        m = re.search(r'<div id="ja-content">(.*?)<div id="ja-col1">', raw, re.S) \
            or re.search(r'<div id="ja-content">(.*)', raw, re.S)
        if m:
            block = m.group(1)
    if block is None:
        return title, ""
    block = re.sub(r"<script.*?</script>", " ", block, flags=re.S | re.I)
    block = re.sub(r"<style.*?</style>", " ", block, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "\n", block)
    text = htmllib.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    if layout == "new":
        # drop the "Sambungan" table of contents: ends at the last
        # "Kategori: ..." line near the top of the article
        kat = [i for i, l in enumerate(lines[:400]) if "Kategori:" in l]
        if kat:
            lines = lines[kat[-1] + 1:]
        # drop fixed furniture lines (header chips, text-search help block);
        # the title is written to the file separately, so drop it here too
        furniture = ("Citra", "Judul", "Sambungan", "Pencarian Teks",
                     "Lingkup pencarian", "Teks pencarian", "Filter pencarian")
        while lines and (lines[0] in furniture or lines[0] == title
                         or lines[0].startswith(": ")
                         or lines[0].startswith("Terakhir diubah")):
            lines = lines[1:]
        # the text-search help block may span many lines; its last line
        # describes spelling variants ("variasi ejaan ... [dj : j, ...]")
        for i, l in enumerate(lines[:30]):
            if "variasi ejaan" in l:
                lines = lines[i + 1:]
                break
        while lines and (lines[0] == "." or lines[0].startswith("[dj")):
            lines = lines[1:]
    else:
        # body of a digitized work starts at the first "--- N ---" marker
        for i, l in enumerate(lines):
            if re.match(r"^---\s*.+?\s*---$", l):
                lines = lines[i:]
                break
    return title, "\n".join(lines)


io_lock = threading.Lock()
progress = {"done": 0, "total": 0}


def process_item(item):
    cat, url, ts, slug = item
    cat_dir = os.path.join(OUT, cat)
    os.makedirs(cat_dir, exist_ok=True)
    fname = re.sub(r"[^\w\-]", "_", slug)[:150] + ".txt"
    fpath = os.path.join(cat_dir, fname)
    if not os.path.exists(fpath):
        ok = False
        code = ""
        for attempt in range(4):
            try:
                code, body = fetch(url, ts)
            except Exception as e:
                code, body = "exc", str(e)
            if code == "200" and len(body) > 2000:
                title, text = extract(body)
                if len(text) > 200:
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(title + "\n" + text + "\n")
                    with io_lock:
                        with open(META, "a", encoding="utf-8") as f:
                            f.write(f"{cat}\t{slug}\t{title}\t{url}\t{ts}\t"
                                    f"{cat}/{fname}\t{len(text)}\n")
                    ok = True
                break  # extracted, or page has no body text (scan-only)
            if code in ("429", "503", "502", "exc"):
                time.sleep(20 * (attempt + 1))
            else:
                time.sleep(3)
        if not ok:
            with io_lock:
                with open(FAILED, "a", encoding="utf-8") as f:
                    f.write(f"{url}\t{ts}\t{code}\n")
        time.sleep(0.3)
    with io_lock:
        progress["done"] += 1
        if progress["done"] % 50 == 0:
            print(f"{progress['done']}/{progress['total']}", flush=True)


def main():
    items = build_url_list()
    progress["total"] = len(items)
    print(f"{len(items)} unique articles to fetch", flush=True)
    if not os.path.exists(META):
        with open(META, "w", encoding="utf-8") as f:
            f.write("category\tslug\ttitle\turl\tsnapshot\tfile\tchars\n")
    with ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(process_item, items))
    print("finished", flush=True)


if __name__ == "__main__":
    main()
