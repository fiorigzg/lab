"""Download Javanese literature sections from ki-demang.com (Joomla site).

Sections:
  - cerita-cekak-jawa          : ~30 modern Javanese short stories (cerkak)
  - cerita-sambung-rajapati    : serial novel "Rajapati"
  - cerita-sambung-ting        : serial novel "Ting"
  - babad-tanah-jawi           : Babad Tanah Jawi (chronicle, prose retelling)
  - bharatayuddha              : Bharatayuddha retelling

One .txt per article page, plus _metadata.tsv per run.
"""
import os
import re
import subprocess
import time
import html as htmllib

BASE = "https://ki-demang.com"
SECTIONS = [
    "cerita-cekak-jawa",
    "cerita-sambung-rajapati",
    "cerita-sambung-ting",
    "babad-tanah-jawi",
    "bharatayuddha",
    # разделы меню "naskah kina", добранные при проверке полноты:
    "negara-kertagama",     # Negarakertagama (пересказ)
    "pararaton",            # Параратон (пересказ)
    "ramayana",             # яванский пересказ Рамаяны
    "suluk-padhalangan",    # сулуки ваянга
    "sinopsis-pakeliran",   # синопсисы ваянг-спектаклей
    "puspawarna",           # статьи/заметки
]
OUT = os.path.join(os.path.dirname(__file__), "..", "corpus_raw", "ki-demang")
os.makedirs(OUT, exist_ok=True)


def fetch(url):
    for attempt in range(5):
        out = subprocess.run(
            ["curl", "-s", "-L", "--max-time", "60",
             "-A", "Mozilla/5.0 (corpus research)", url],
            capture_output=True)
        if out.returncode == 0 and out.stdout:
            return out.stdout.decode("utf-8", errors="replace")
        time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"failed after retries: {url}")


def extract_text(raw):
    m = re.search(r'<div[^>]*class="[^"]*item-page[^"]*"[^>]*>(.*)', raw, re.S)
    block = m.group(1) if m else raw
    # cut at footer/nav markers if present
    for marker in ('<div id="ja-col1"', '<div class="pagination', '<ul class="pagenav'):
        idx = block.find(marker)
        if idx != -1:
            block = block[:idx]
    block = re.sub(r"<script.*?</script>", " ", block, flags=re.S | re.I)
    block = re.sub(r"<style.*?</style>", " ", block, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", "\n", block)
    text = htmllib.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    return text.strip()


def main():
    rows = []
    for sec in SECTIONS:
        listing = fetch(f"{BASE}/index.php/{sec}")
        slugs = sorted(set(re.findall(rf'href="(/index\.php/{sec}/[^"#]+)"', listing)))
        print(f"{sec}: {len(slugs)} pages")
        for slug in slugs:
            url = BASE + slug
            name = slug.rsplit("/", 1)[-1]
            fname = f"{sec}__{name}.txt"
            fpath = os.path.join(OUT, fname)
            if not os.path.exists(fpath):
                try:
                    raw = fetch(url)
                except RuntimeError as e:
                    print("SKIP", e)
                    continue
                text = extract_text(raw)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(text + "\n")
                time.sleep(2)
            else:
                text = open(fpath, encoding="utf-8").read()
            rows.append((sec, name, url, fname, str(len(text))))

    meta = os.path.join(OUT, "_metadata.tsv")
    with open(meta, "w", encoding="utf-8") as f:
        f.write("section\tslug\turl\tfile\tchars\n")
        for r in rows:
            f.write("\t".join(r) + "\n")
    print(f"done: {len(rows)} pages -> {OUT}")


if __name__ == "__main__":
    main()
