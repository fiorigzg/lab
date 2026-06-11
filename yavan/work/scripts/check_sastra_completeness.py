"""ПРОВЕРКА ПОЛНОТЫ sastra.org и добор недостающего.

Зачем: основной список страниц брался из Wayback CDX — туда могли не попасть
страницы, которые архив никогда не сохранял (или добавленные на сайт позже
снапшотов). Официальная статистика сайта (июнь 2026): 2653 коллекции.

Что делает:
1. Обходит листинги 5 категорий ЖИВОГО сайта через прокси r.jina.ai
   (включая подкатегории и пагинацию ?start=N), собирает все URL статей.
2. Сравнивает ID статей (число в начале последнего сегмента URL) с уже
   скачанными файлами в corpus_raw/sastra-org/*/.
3. Недостающие статьи скачивает тем же живым каналом (md_to_text из
   download_sastra_live), складывает в те же папки и _metadata_live.tsv.

Запуск: python3 scripts/check_sastra_completeness.py (из work/);
повторный запуск безопасен (резюме по наличию файла).
"""
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from download_sastra_live import fetch_jina, md_to_text, META, io_lock  # noqa: E402
from download_sastra_org import OUT  # noqa: E402

CATS = ["kisah-cerita-dan-kronikal", "agama-dan-kepercayaan",
        "bahasa-dan-budaya", "arsip-dan-sejarah", "koran-majalah-dan-jurnal"]
BASE = "https://www.sastra.org"

ART = re.compile(
    r"https://www\.sastra\.org/((?:%s)(?:/[a-z0-9-]+)*?/(\d+)-[a-z0-9-]+)"
    % "|".join(CATS))
SUB = re.compile(
    r"https://www\.sastra\.org/((?:%s)/[a-z0-9-]+/?)(?=[\")\s])" % "|".join(CATS))
START = re.compile(r"\?start=(\d+)")


def crawl_listings():
    """BFS по листингам; возвращает {article_id: url}."""
    seen_pages, articles = set(), {}
    queue = [f"{BASE}/{c}" for c in CATS]
    while queue:
        url = queue.pop(0)
        if url in seen_pages:
            continue
        seen_pages.add(url)
        code, md = fetch_jina(url)
        if code != "200":
            print("  listing failed:", code, url, flush=True)
            time.sleep(10)
            continue
        for m in ART.finditer(md):
            articles.setdefault(m.group(2), BASE + "/" + m.group(1))
        # подкатегории (без числового последнего сегмента)
        for m in SUB.finditer(md):
            sub = (BASE + "/" + m.group(1)).rstrip("/")
            last = sub.rsplit("/", 1)[-1]
            if not re.match(r"\d+-", last) and sub not in seen_pages:
                queue.append(sub)
        # пагинация
        for m in START.finditer(md):
            base = url.split("?")[0]
            pg = f"{base}?start={m.group(1)}"
            if pg not in seen_pages:
                queue.append(pg)
        print(f"listing ok: {url} (queue {len(queue)}, "
              f"articles {len(articles)})", flush=True)
        time.sleep(2)
    return articles


def existing_ids():
    ids = set()
    for dirp, _, files in os.walk(OUT):
        for fn in files:
            if fn.endswith(".txt") and not fn.startswith("_"):
                m = re.match(r"(\d+)-", fn)
                if m:
                    ids.add(m.group(1))
    return ids


def main():
    articles = crawl_listings()
    have = existing_ids()
    missing = {k: v for k, v in articles.items() if k not in have}
    print(f"\nна сайте найдено статей: {len(articles)}; "
          f"скачано ранее: {len(have)}; недостаёт: {len(missing)}", flush=True)
    for art_id, url in sorted(missing.items(), key=lambda x: int(x[0])):
        cat = url.removeprefix(BASE + "/").split("/")[0]
        slug = url.rsplit("/", 1)[-1]
        fname = re.sub(r"[^\w\-]", "_", slug)[:150] + ".txt"
        fpath = os.path.join(OUT, cat, fname)
        if os.path.exists(fpath):
            continue
        code, md = fetch_jina(url)
        if code == "200":
            title, text = md_to_text(md)
            if len(text) > 200:
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(title + "\n" + text + "\n")
                with io_lock:
                    with open(META, "a", encoding="utf-8") as f:
                        f.write(f"{cat}\t{slug}\t{title}\t{url}\tlive\t"
                                f"{cat}/{fname}\t{len(text)}\n")
                print("saved:", slug, flush=True)
            else:
                print("no text:", slug, flush=True)
        else:
            print("fail", code, slug, flush=True)
        time.sleep(2)
    print("done", flush=True)


if __name__ == "__main__":
    main()
