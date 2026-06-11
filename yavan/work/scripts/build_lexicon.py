"""СБОРКА ЛЕКСИКОНА КОРНЕЙ для лемматизатора (lexicon/roots.txt).

Зачем: лемматизатор работает по принципу "снимай аффикс -> проверяй, что
получился существующий корень". Для проверки нужен список корней яванского.
Готового машиночитаемого нет, но в сыром корпусе лежат словари, которые мы
ИСКЛЮЧИЛИ из текстового корпуса как "не-текст" -- здесь они наоборот полезны:

1. Javanese-English Dictionary (Horne, 1974), 31 файл со sastra.org --
   основной современный словарь. Формат: заголовочное слово на отдельной
   строке, толкование -- следующей длинной строкой. Берём заголовки.
   Статьи-аффиксы ("a-", "-ake") пропускаем, составные через дефис оставляем.
2. Списки dasanama (синонимические ряды кави <-> современный язык,
   Padmasusastra 1897, Winter 1875 и др.) -- дают архаичную/поэтическую
   лексику стихов (tembang). Формат: "Слово :" и строки синонимов через "|".
   Берём все слова.
2a. Javaansch-Nederduitsch Woordenboek (Gericke & Roorda, 1847), 20 частей
   -- самый полный словарь яванского XIX века, добавляет классическую
   лексику. Транскрипция sastra.org уже модернизирована (kunci, не
   koentji). Формат: "слово :" на отдельной строке, толкование следом.
   Чистые перенаправления ("zie X.") пропускаем -- это отсылки от
   словоформ к корням, а не корни.
3. Частотная добавка из самого корпуса НЕ делается: частотные словоформы
   заблокировали бы снятие аффиксов (правило "слово уже в лексиконе ->
   оставить как есть"). Частоты корпуса используются только как тай-брейк
   при выборе из нескольких кандидатов (см. jav_lemmatizer.py) и
   кэшируются здесь в lexicon/freq.tsv.

Все слова прогоняются через ту же normalize(), что и корпус (lowercase,
сворачивание диакритики, oe->u, tj->c, dj->j) -- иначе формы не совпадут.

Выход: lexicon/roots.txt (1 корень на строку), lexicon/freq.tsv.
Запуск: python3 scripts/build_lexicon.py (из work/, после clean_corpus.py).
"""
import glob
import os
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(__file__))
from clean_corpus import normalize  # noqa: E402  (та же нормализация!)

RAW = "corpus_raw"
OUTDIR = "lexicon"
WORD = re.compile(r"^[a-zà-ÿêèéåăṭḍ]+(?:-[a-zà-ÿêèéåăṭḍ]+)*$")

# служебные пометы Horne, попадающие на отдельные строки
HORNE_NOISE = {"a", "b", "c", "ng", "kr", "ki", "ka", "var", "rg", "ltry",
               "inf", "sms", "see", "also", "or", "oj", "kn", "md"}


def horne_headwords():
    words = set()
    files = glob.glob(os.path.join(
        RAW, "sastra-org", "*", "*javanese-english-dictionary-horne*.txt"))
    for path in files:
        for ln in open(path, encoding="utf-8", errors="replace"):
            w = ln.strip().lower()
            if (not w or " " in w or len(w) < 3 or w in HORNE_NOISE or
                    w.startswith("-") or w.endswith("-")):
                continue
            if WORD.match(w):
                words.add(normalize(w))
    return words


def dasanama_words():
    """Берём ТОЛЬКО строки-синонимические ряды ("a | b | c.") и заголовки
    ("Слово :") -- иначе в лексикон утекают колофоны и предисловия самих
    словарей (anggitanipun..., kaecap ing...)."""
    words = set()
    files = glob.glob(os.path.join(RAW, "sastra-org", "*", "*dasanama*.txt"))
    for path in files:
        for ln in open(path, encoding="utf-8", errors="replace"):
            ln = ln.strip()
            if ln.startswith("---"):
                continue
            if ln.endswith(":") and len(ln.split()) <= 3:
                ln = ln.rstrip(" :")            # заголовок ряда
            elif "|" not in ln:
                continue                        # не синонимический ряд
            for w in re.split(r"[|,.()]| ", ln):
                w = w.strip().lower()
                if len(w) >= 3 and WORD.match(w):
                    words.add(normalize(w))
    return words


def gericke_headwords():
    """Заголовки Gericke & Roorda 1847: строки вида "слово :", толкование
    следующей строкой. Перенаправления "zie X." не берём."""
    words = set()
    files = glob.glob(os.path.join(RAW, "sastra-org", "*", "*gericke*.txt"))
    for path in files:
        lines = [l.strip() for l in
                 open(path, encoding="utf-8", errors="replace")]
        for i, ln in enumerate(lines):
            if not ln.endswith(":"):
                continue
            w = ln.rstrip(" :").lower()
            if len(w) < 3 or not WORD.match(w):
                continue
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            if nxt.lower().startswith("zie ") and len(nxt) < 60:
                continue
            words.add(normalize(w))
    return words


def corpus_freq():
    cnt = Counter()
    for b in ("sastra", "jurnal", "arsip", "majalah"):
        p = os.path.join("corpus_clean", f"corpus_segments_{b}.txt")
        if not os.path.exists(p):
            continue
        for ln in open(p, encoding="utf-8"):
            cnt.update(ln.split())
    return cnt


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    horne = horne_headwords()
    dasa = dasanama_words()
    gericke = gericke_headwords()
    roots = horne | dasa | gericke
    with open(os.path.join(OUTDIR, "roots.txt"), "w", encoding="utf-8") as f:
        for w in sorted(roots):
            f.write(w + "\n")
    print(f"horne: {len(horne)}, dasanama: {len(dasa)}, "
          f"gericke: {len(gericke)}, всего корней: {len(roots)}")
    cnt = corpus_freq()
    with open(os.path.join(OUTDIR, "freq.tsv"), "w", encoding="utf-8") as f:
        for w, c in cnt.most_common():
            if c >= 3:
                f.write(f"{w}\t{c}\n")
    print(f"частоты: {len(cnt)} типов токенов")


if __name__ == "__main__":
    main()
