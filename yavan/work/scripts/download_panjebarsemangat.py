"""Скачивание журнала Panjebar Semangat (panjebarsemangat.co.id) из Wayback.

Зачем: Panjebar Semangat — яванский еженедельник (Сурабая, с 1933 г.):
рассказы (cerkak), романы с продолжением (cerita sambung), статьи.
Живой домен с ~2020 г. захвачен спам-сайтом (индонезийские обзоры игр),
поэтому берём ТОЛЬКО снапшоты Wayback до 2020 г.

Два поколения сайта в архиве:
  1) WordPress (2010-2014): статьи в корне домена,
     тело в <div class="single_post">, конец — "This Post Tagged with";
  2) свой движок (2016-2019): страницы berita-NNNN-<slug>.html,
     тело в <div ... id='detail_bar2'>, конец — <div id="katonkanan">.
Категория рубрики есть на странице (Cerita Sambung, Alaming Lelembut,
Yak Opo Kabare и т.д.) — пишется в метаданные, пригодится при очистке
для разделения рассказов и новостных статей.

Выход: corpus_raw/panjebarsemangat/<slug>.txt (1-я строка — заголовок),
метаданные _metadata.tsv (slug, title, category, url, ts, file, chars).
Запуск: python3 scripts/download_panjebarsemangat.py (из work/);
повторный запуск безопасен (резюме по наличию файла).
"""
import html as htmllib
import os
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
import threading

OUT = os.path.join(os.path.dirname(__file__), "..", "corpus_raw",
                   "panjebarsemangat")
META = os.path.join(OUT, "_metadata.tsv")
CDX = ("https://web.archive.org/cdx/search/cdx?url=panjebarsemangat.co.id*"
       "&output=text&fl=urlkey,timestamp,original&filter=statuscode:200"
       "&collapse=urlkey&limit=100000")
SKIP_PATH = re.compile(
    r"co\.id(:80)?/?($|\?|(wp-json|wp-content|wp-includes|wp-login|fonts|"
    r"category|author|tag|feed|page|sample-page|robots\.txt|xmlrpc|"
    r"banner-\d+|favicon|sitemap|\d{4}($|/)))")
ASSET = re.compile(r"\.(jpg|jpeg|png|gif|css|js|ico|pdf|woff2?|ttf|xml|txt)(\?|$)",
                   re.I)

os.makedirs(OUT, exist_ok=True)
io_lock = threading.Lock()


def fetch(url):
    for attempt in range(4):
        out = subprocess.run(
            ["curl", "-s", "-L", "--compressed", "--max-time", "90",
             "-A", "Mozilla/5.0 (corpus research)", url],
            capture_output=True)
        if out.returncode == 0 and out.stdout:
            return out.stdout.decode("utf-8", errors="replace")
        time.sleep(10 * (attempt + 1))
    return None


def strip_tags(block):
    block = re.sub(r"<script.*?</script>", " ", block, flags=re.S | re.I)
    block = re.sub(r"<style.*?</style>", " ", block, flags=re.S | re.I)
    block = re.sub(r"<!--.*?-->", " ", block, flags=re.S)
    text = re.sub(r"<[^>]+>", "\n", block)
    text = htmllib.unescape(text).replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    return [l.strip() for l in text.split("\n") if l.strip()]


def extract(raw):
    """-> (title, category, text) или (None, None, None), если это не статья
    (листинги/служебные страницы не имеют single_post/detail_bar2)."""
    m = re.search(r'<div class="single_post">(.*)', raw, re.S)
    if m:  # поколение WordPress
        block = m.group(1)
        for marker in ("This Post Tagged with", "Berita lain yang terkait",
                       '<div id="sidebar"', "<ul class='postnav'"):
            idx = block.find(marker)
            if idx != -1:
                block = block[:idx]
        lines = strip_tags(block)
        if not lines:
            return None, None, None
        title, category, body_from = lines[0], "", 1
        # шапка: [title, <рубрики...>, "- Posted by", "admin",
        #         "on December 13, 2010", <тело...>] — теги режут её на строки
        for j, l in enumerate(lines[1:12], start=1):
            if re.match(r"^-?\s*Posted by\b", l) or " - Posted by" in l:
                category = " ".join(
                    x for x in lines[1:j] if x != ",").strip(" ,")
                category += " " + l.split("- Posted by")[0].strip(" ,")
                category = category.strip(" ,")
                body_from = j + 1
                # пропустить автора и дату ("on <Month> <d>, <year>"),
                # если дата не была в той же строке (вариант без тегов)
                if not re.search(r"Posted by.*\d{4}", l):
                    k = body_from
                    while k < len(lines) and not re.match(
                            r"^on .*\d{4}$", lines[k - 1]) and k <= j + 4:
                        k += 1
                    if k <= j + 4 or re.match(r"^on .*\d{4}$", lines[k - 1]):
                        body_from = k
                break
        return title, category, "\n".join(lines[body_from:])

    m = re.search(r"<div class='left_bar' id='detail_bar2'>(.*?)"
                  r"<div id=\"katonkanan\"", raw, re.S)
    if m:  # поколение berita-NNNN-*.html
        block = m.group(1)
        mt = re.search(r"<i class='judul_berita'>(.*?)<", block, re.S)
        title = htmllib.unescape(mt.group(1)).strip() if mt else ""
        lines = strip_tags(block)
        category, body, in_body = "", [], False
        for i, l in enumerate(lines):
            if not in_body:
                if l.startswith("Kategori"):
                    category = lines[i + 1] if i + 1 < len(lines) else ""
                if l == "kali" or l.endswith(" kali"):
                    in_body = True
                continue
            if l.startswith(("Berita Liyane", "Komentar", "Tulis Komentar")):
                break
            body.append(l)
        return title, category.strip(" -"), "\n".join(body)

    return None, None, None


def build_url_list():
    raw = fetch(CDX)
    rows = []
    for line in raw.splitlines():
        parts = line.split()
        if len(parts) != 3:
            continue
        urlkey, ts, orig = parts
        if ts >= "2020":          # дальше домен занят спамом
            continue
        if ASSET.search(orig) and "berita-" not in orig:
            continue
        if SKIP_PATH.search(orig):
            continue
        rows.append((urlkey, ts, orig))
    # один urlkey мог остаться с www и без — дедуп по urlkey, новейший ts
    best = {}
    for urlkey, ts, orig in rows:
        if urlkey not in best or ts > best[urlkey][0]:
            best[urlkey] = (ts, orig)
    return [(ts, orig) for ts, orig in best.values()]


def slug_of(url):
    s = url.rstrip("/").rsplit("/", 1)[-1]
    s = re.sub(r"\.html?$", "", s)
    s = re.sub(r"[^\w\-]", "_", s)
    return s[:150] or "untitled"


def grab(item):
    ts, orig = item
    slug = slug_of(orig)
    fpath = os.path.join(OUT, slug + ".txt")
    if os.path.exists(fpath):
        return
    raw = fetch(f"https://web.archive.org/web/{ts}id_/{orig}")
    if raw is None:
        with io_lock:
            print("FAIL fetch", orig, flush=True)
        return
    title, category, text = extract(raw)
    if text is None:
        return  # не статья (листинг и т.п.)
    if len(text) < 200:
        return  # заглушка/обрывок
    with open(fpath, "w", encoding="utf-8") as f:
        f.write((title or slug) + "\n" + text + "\n")
    with io_lock:
        with open(META, "a", encoding="utf-8") as f:
            f.write(f"{slug}\t{title}\t{category}\t{orig}\t{ts}\t"
                    f"{slug}.txt\t{len(text)}\n")


def main():
    items = build_url_list()
    print(f"queue: {len(items)} pages", flush=True)
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(grab, items))
    n = len([f for f in os.listdir(OUT) if f.endswith(".txt")])
    print(f"done: {n} files in {OUT}", flush=True)


if __name__ == "__main__":
    main()
