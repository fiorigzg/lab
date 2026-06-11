"""Download all posts from alangalangkumitir.wordpress.com via the public
wordpress.com REST API. Saves one .txt per post (title as filename) and a
metadata TSV (id, date, title, url, categories).

Site: AlangAlangKumitir - transcriptions of classical Javanese texts
(serat, suluk, babad, kidung). Some posts are Indonesian-language
commentary/translations - they are kept in the raw corpus and filtered
out at the cleaning stage.
"""
import json
import os
import re
import subprocess
import time
import urllib.parse
import html as htmllib

SITE = "alangalangkumitir.wordpress.com"
API = f"https://public-api.wordpress.com/rest/v1.1/sites/{SITE}/posts/"
OUT = os.path.join(os.path.dirname(__file__), "..", "corpus_raw", "alangalangkumitir")
META = os.path.join(OUT, "_metadata.tsv")

os.makedirs(OUT, exist_ok=True)


def fetch(url):
    out = subprocess.run(
        ["curl", "-s", "--max-time", "90", "-A", "corpus-research/1.0", url],
        capture_output=True, check=True)
    return out.stdout.decode("utf-8", errors="replace")


def html_to_text(s):
    s = re.sub(r"<script.*?</script>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<style.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"</p>", "\n\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = htmllib.unescape(s)
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s)
    return s.strip()


def safe_name(title, post_id):
    name = re.sub(r"[^\w\s\-]", "", htmllib.unescape(title), flags=re.U).strip()
    name = re.sub(r"\s+", "_", name)[:120]
    return f"{name or 'untitled'}__{post_id}.txt"


def main():
    rows = []
    page_handle = None
    total = 0
    while True:
        params = {"number": "100", "fields": "ID,date,title,URL,content,categories"}
        if page_handle:
            params["page_handle"] = page_handle
        url = API + "?" + urllib.parse.urlencode(params)
        data = json.loads(fetch(url))
        posts = data.get("posts", [])
        if not posts:
            break
        for p in posts:
            text = html_to_text(p.get("content", ""))
            title = htmllib.unescape(p.get("title", "")).strip()
            fname = safe_name(title, p["ID"])
            with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
                f.write(title + "\n\n" + text + "\n")
            cats = ";".join(p.get("categories", {}).keys())
            rows.append((str(p["ID"]), p.get("date", "")[:10], title,
                         p.get("URL", ""), fname, cats))
        total += len(posts)
        print(f"fetched {total}/{data.get('found', '?')}")
        page_handle = data.get("meta", {}).get("next_page")
        if not page_handle:
            break
        time.sleep(1)

    with open(META, "w", encoding="utf-8") as f:
        f.write("id\tdate\ttitle\turl\tfile\tcategories\n")
        for r in rows:
            f.write("\t".join(x.replace("\t", " ").replace("\n", " ") for x in r) + "\n")
    print(f"done: {total} posts -> {OUT}")


if __name__ == "__main__":
    main()
