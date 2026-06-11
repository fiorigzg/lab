"""ОДНОРАЗОВАЯ ЧИСТКА (уже применена к corpus_raw/sastra-org 2026-06-10).

Что делает: файлы, скачанные «живым» каналом через r.jina.ai
(download_sastra_live.py), содержали обвязку сайта sastra.org. Скрипт
удаляет её по месту (in place), не трогая сам текст произведения:

  - ШАПКА: меню сайта ("Sastra Jawa", "* Beranda" .. "* Huruf Jawa"),
    блок яванского календаря ("Penanggalan", "Rêbo Pon ..", "Kurup: .."),
    виджеты "Leksikon"/"Telusuri", повтор заголовка, чипы
    "Judul"/"Sambungan"/"Citra", оглавление-самбунган
    (строки вида "N.<название>. Kategori: ..."), служебные пути
    "/sastra/...";
  - ПОДВАЛ: всё от строки "Informasi umum" (сайдбар: проекты, наскахи)
    или "sastra.org © ..." до конца файла.

Затронуты только файлы, в первых 15 строках которых есть "* Beranda"
(маркер jina-канала); остальные не модифицируются.

Запуск: python3 clean_jina_chrome.py  (идемпотентен, можно повторно)
"""
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..", "corpus_raw", "sastra-org")

FURNITURE = {"Judul", "Sambungan", "Citra", "Pencarian Teks", "Leksikon",
             "Telusuri", "Penanggalan", "Lingkup pencarian", "Teks pencarian",
             "Filter pencarian"}


def clean(lines, title):
    # ---- header ----
    body_start = 0
    # menu block present?
    if any(l.strip() in ("* Beranda", "*   Beranda") for l in lines[:15]):
        head = lines[:250]
        # last ToC line wins
        kat = [i for i, l in enumerate(head) if "Kategori:" in l]
        if kat:
            body_start = kat[-1] + 1
        else:
            # cut after the last fixed menu widget
            tel = [i for i, l in enumerate(head) if l.strip() == "Telusuri"]
            if tel:
                body_start = tel[-1] + 1
        # drop remaining furniture right after the cut
        while body_start < len(lines):
            l = lines[body_start].strip()
            if (l in FURNITURE or l == title or l == "" or
                    l.startswith("/sastra/") or l.startswith(": ") or
                    l.startswith("Terakhir diubah") or
                    "variasi ejaan" in l or l.startswith("[dj") or
                    re.match(r"^(Senin|Selasa|Rabu|Kamis|Jumat|Sabtu|Minggu)\s", l) or
                    re.match(r"^(Sênèn|Slasa|Rêbo|Kêmis|Jumuwah|Sêtu|Akad|Ngahad|Ngahat)\s", l) or
                    l.startswith("Kurup:") or l.startswith("* ")):
                body_start += 1
            else:
                break
    # ---- footer ----
    body_end = len(lines)
    for i in range(len(lines) - 1, max(len(lines) - 80, body_start), -1):
        l = lines[i].strip()
        if l == "Informasi umum" or l.startswith("sastra.org ©"):
            body_end = i
    return lines[body_start:body_end]


def main():
    fixed = 0
    for dirp, _, files in os.walk(ROOT):
        for fn in files:
            if not fn.endswith(".txt") or fn.startswith("_"):
                continue
            p = os.path.join(dirp, fn)
            raw = open(p, encoding="utf-8", errors="replace").read().split("\n")
            title, body = raw[0], raw[1:]
            if not any(l.strip() in ("* Beranda", "*   Beranda") for l in body[:15]):
                continue
            cleaned = clean(body, title)
            open(p, "w", encoding="utf-8").write("\n".join([title] + cleaned) + "\n")
            fixed += 1
    print("cleaned:", fixed)


if __name__ == "__main__":
    main()
