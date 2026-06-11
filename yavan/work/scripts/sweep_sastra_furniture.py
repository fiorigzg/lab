"""ОДНОРАЗОВАЯ ЧИСТКА (уже применена к corpus_raw/sastra-org 2026-06-10).

Что делает: удаляет из НАЧАЛА файлов sastra.org служебные строки сайта
("мебель"), которые успели сохраниться до фикса экстрактора в
download_sastra_org.py:
  - повтор заголовка страницы;
  - чипы навигации: "Judul", "Sambungan", "Citra";
  - блок справки поиска: "Pencarian Teks", "Lingkup pencarian",
    "Teks pencarian", "Filter pencarian", строки-описания, начинающиеся
    с ": ", строка про "variasi ejaan" и список замен "[dj : j, ...]";
  - строку "Terakhir diubah: ..." (дата изменения страницы);
  - обрезок HTML-тега вида ...__body">.

Сам текст произведения не меняется: правится только верх файла (зона до
первой содержательной строки, не глубже 40 строк).

Запуск: python3 sweep_sastra_furniture.py  (идемпотентен, можно повторно)
"""
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "corpus_raw", "sastra-org")

FURNITURE = ("Citra", "Judul", "Sambungan", "Pencarian Teks",
             "Lingkup pencarian", "Teks pencarian", "Filter pencarian")


def main():
    fixed = 0
    for dirp, _, files in os.walk(ROOT):
        for fn in files:
            if not fn.endswith(".txt") or fn.startswith("_"):
                continue
            p = os.path.join(dirp, fn)
            lines = open(p, encoding="utf-8").read().split("\n")
            title, body = lines[0], lines[1:]
            out, head_zone, changed = [], True, False
            i = 0
            while i < len(body):
                l = body[i]
                if head_zone and i < 40 and (
                        l in FURNITURE or l == title or l.startswith(": ")
                        or l.startswith("Terakhir diubah") or l == "."
                        or l.startswith("[dj") or l.endswith('__body">')
                        or "variasi ejaan" in l):
                    changed = True
                    i += 1
                    continue
                if l.strip():
                    head_zone = False
                out.append(l)
                i += 1
            if changed:
                open(p, "w", encoding="utf-8").write("\n".join([title] + out))
                fixed += 1
    print("swept files:", fixed)


if __name__ == "__main__":
    main()
