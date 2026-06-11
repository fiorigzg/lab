# -*- coding: utf-8 -*-
"""ОЧИСТКА сырого корпуса (corpus_raw -> corpus_clean). БЕЗ лемматизации —
она выполняется отдельным скриптом поверх результата этого.

Этапы (подробное обоснование в work/SOURCES.md и scripts/README.md):

1. ОТБОР ФАЙЛОВ
   - исключаются двуязычные словари/грамматики/списки слов sastra.org
     (по заголовку: dictionary, dictionnaire, woordenboek, kamus, leksikon,
     paramasastra, spraakkunst, synoniemen, dasanama, ...);
   - исключаются страницы "pangkalan data" (индексы БД сайта);
   - файлы, в которых после очистки < 30 токенов (в т.ч. нотации гамелана),
     исключаются целиком;
   - корпус раскладывается по "вёдрам" (источники не смешиваем):
       sastra  -- литература: sastra-org/kisah-cerita-dan-kronikal,
                  agama-dan-kepercayaan, bahasa-dan-budaya (минус словари),
                  alangalangkumitir (яванские посты), ki-demang;
       arsip   -- sastra-org/arsip-dan-sejarah (архивы, письма);
       jurnal  -- sastra-org/koran-majalah-dan-jurnal (журналы 1920-30-х);
       majalah -- panjebarsemangat (еженедельник 2010-х: рассказы, статьи).
     Статьи из sastra-org/_recovered/ (добор перебором ID, категория
     неизвестна) раскладываются по названию (см. bucket_of).
     Основной корпус для эмбеддингов = ведро sastra.

2. АРТЕФАКТЫ ОЦИФРОВКИ (построчно)
   - маркеры страниц "--- 12 ---", "--- 1-2 : 13 ---";
   - строки-сноски: "[", "]", чисто числовые строки, "N xxx. (kembali)";
   - редакторские пометки (индонез.): строки с "§", "Teks asli:",
     "Kurang/Lebih satu suku kata", "kembali", "Sambungan", "Citra";
   - обрывы слов на границах страниц: токены вида "[kêka...]", "[...lih]";
   - инлайн-номера сносок "[61]";
   - заголовки пупухов "652. Asmaradana" (строка = номер + одно слово);
   - нотации гамелана (строки, где > половины токенов содержат цифры).

3. ФИЛЬТР ЯЗЫКА (построчно, т.к. в текстах чередуются яванские строфы и
   индонезийские переводы): скоринг по стоп-словам яванского (нгоко+крама),
   индонезийского, голландского, английского. Строка остаётся, если
   яванский счёт строго больше суммы остальных; короткие строки без
   стоп-слов наследуют решение предыдущей строки.

4. НОРМАЛИЗАЦИЯ
   - lowercase;
   - сворачивание диакритики: ê è é -> e, å ă â -> a, í ì î -> i,
     ó ò ô -> o, ú ù û -> u, ṭ -> t, ḍ -> d, ñ -> n;
   - старая (довоенная) орфография: oe -> u, tj -> c, dj -> j
     (стандартные замены Van Ophuijsen -> современная; замена старого
     "j"=/y/ не выполняется, т.к. неотличима от современного j);
   - пунктуация удаляется; дефис внутри слова сохраняется (редупликации:
     tata-tata); разделители стихов "|" и "||" трактуются как границы
     предложений.

5. ТОКЕНЫ-ЗАМЕНЫ (по инструкции: местоимения и числительные -> токены)
   - последовательности цифр -> ORDINAL1;
   - личные местоимения (нгоко/крама, полный список в PRONOUNS) -> PRON1.

6. ВЫХОД
   corpus_clean/texts/<ведро>/<имя>.txt -- очищенный текст,
       1 предложение = 1 строка (имя файла = как в сыром корпусе);
   corpus_clean/corpus_text_<ведро>.txt -- 1 строка = 1 текст (для SVD);
   corpus_clean/corpus_segments_<ведро>.txt -- 1 строка = 1 предложение
       (для CBoW; получен из тех же текстов);
   corpus_clean/_excluded.tsv -- какие файлы исключены и почему;
   corpus_clean/_stats.txt -- статистика.

Запуск: python3 scripts/clean_corpus.py  (из папки work/)
"""
import os
import re
import sys
import unicodedata
from collections import Counter

RAW = "corpus_raw"
OUT = "corpus_clean"

# ---------------------------------------------------------------- buckets --
# статьи sastra.org, добранные перебором ID (probe_sastra_ids.py), лежат в
# _recovered/ без категории -- раскладываем по названию: довоенные журналы
# (Kajawèn, Pusaka Jawi и пр.) -> jurnal, коллекции архивов -> arsip
RECOVERED_JURNAL = re.compile(
    r"kajaw[eè]n|pusaka jawi|s[eê]dya tama|darma kanda|narpawandawa|"
    r"waspada|panji pustaka", re.I)
RECOVERED_ARSIP = re.compile(r"koleksi warsadiningrat|arsip", re.I)

def bucket_of(relpath, title=""):
    if relpath.startswith("sastra-org/arsip-dan-sejarah"):
        return "arsip"
    if relpath.startswith("sastra-org/koran-majalah-dan-jurnal"):
        return "jurnal"
    if relpath.startswith("sastra-org/_recovered"):
        if RECOVERED_JURNAL.search(title):
            return "jurnal"
        if RECOVERED_ARSIP.search(title):
            return "arsip"
        return "sastra"
    if relpath.startswith("panjebarsemangat/"):
        return "majalah"          # журнал 2010-х -- отдельный регистр
    return "sastra"

# словари/грамматики/списки слов -- не естественный текст
EXCLUDE_TITLE = re.compile(
    r"dictionary|dictionnaire|woordenboek|wordenboek|kamus|leksikon|"
    r"paramasastra|spraakkunst|synoniemen|grammatica|dasanama|"
    r"javaansch.*taal|woordenlijst|pangkalan.?data|wawaton.?panyerat|"
    r"frekuensi.?kata", re.I)

# ------------------------------------------------------------- stop words --
JAV = {"ing", "kang", "iku", "ora", "lan", "saka", "karo", "wis", "ana",
       "iki", "kanthi", "dening", "marang", "sing", "ingkang", "punika",
       "menika", "wonten", "boten", "mboten", "sampun", "dhateng", "saking",
       "ugi", "inggih", "kaliyan", "dene", "yen", "menawa", "menawi",
       "nanging", "amarga", "amargi", "supaya", "supados", "banjur",
       "lajeng", "uga", "apa", "punapa", "kados", "kaya", "sarta", "tuwin",
       "utawi", "utawa", "datan", "tan", "kalawan", "miwah", "ingsun",
       "sira", "dadya", "dadi", "dados", "arsa", "badhe", "bakal", "wus",
       "sampun", "maring", "aneng", "neng", "ono", "iso", "isa", "ake",
       "dhumateng", "kagem", "dhewe", "piyambak", "malih", "maneh",
       "sanget", "banget", "mawi", "tanpa", "sajroning", "salebeting"}
IND = {"yang", "dengan", "tidak", "dari", "untuk", "pada", "adalah",
       "dalam", "dan", "akan", "sudah", "telah", "bisa", "karena",
       "mereka", "kita", "saya", "anda", "tersebut", "sebagai", "juga",
       "atau", "itu", "ini", "oleh", "ke", "di", "secara", "tetapi",
       "namun", "agar", "supaya", "jika", "kalau", "saat", "ketika",
       "sehingga", "kemudian", "yaitu", "ialah", "bahwa", "para",
       "merupakan", "terhadap", "seperti", "antara", "banyak", "lebih"}
ENG = {"the", "of", "and", "to", "in", "is", "was", "for", "with", "that",
       "this", "are", "be", "or", "from", "by", "an", "not", "his", "her"}
DUT = {"de", "het", "van", "en", "een", "der", "den", "te", "dat", "die",
       "met", "voor", "zijn", "aan", "op", "is", "niet", "ook", "naar",
       "worden", "wordt", "deze", "bij", "uit", "over", "tot"}
# слова, общие для jav и ind, не должны давать счёт ни тому ни другому
AMBIG = JAV & IND
JAVX, INDX = JAV - AMBIG, IND - AMBIG

PRONOUNS = {"aku", "kula", "kawula", "ingsun", "ingwang", "kowe", "kowé",
            "sira", "sampeyan", "panjenengan", "panjenenganipun",
            "dheweke", "dheke", "piyambakipun", "kita", "awakmu",
            "awakku", "slirane", "sliramu"}

# ------------------------------------------------------------ line filters --
PAGE_MARK = re.compile(r"^---\s*.+?\s*---$")
PUPUH_HEAD = re.compile(r"^\d+\.?\s+[A-Za-zÀ-ÿê]+\s*$")
NUM_ONLY = re.compile(r"^[\d\s.\-:()\[\]]+$")
EDITORIAL = re.compile(
    r"^§|teks asli\s*:|kurang satu|lebih satu|kirang sa|langkung sa|"
    r"prayoginipun|kembali\)|^sambungan$|^citra$|^judul$|tanggal masehi|"
    r"^lingkup pencarian|^teks pencarian|^filter pencarian", re.I)
BROKEN_WORD = re.compile(r"\[[^\]\[]*\.\.\.[^\]\[]*\]")   # [kêka...] / [...lih]
FOOTNOTE_REF = re.compile(r"\[\s*\d+\s*\]")               # [61]

def is_notation_line(line):
    toks = line.split()
    if len(toks) < 3:
        return False
    dig = sum(1 for t in toks if any(c.isdigit() for c in t))
    return dig / len(toks) > 0.5

def lang_score(line):
    words = re.findall(r"[a-zà-ÿêèéåăôíìóòúùṭḍ]+", line.lower())
    j = sum(1 for w in words if w in JAVX)
    i = sum(1 for w in words if w in INDX)
    e = sum(1 for w in words if w in ENG)
    d = sum(1 for w in words if w in DUT)
    return j, i + e + d

# ------------------------------------------------------------- normalize --
FOLD = str.maketrans({
    "ê": "e", "è": "e", "é": "e", "ë": "e",
    "å": "a", "ă": "a", "â": "a", "à": "a", "á": "a",
    "í": "i", "ì": "i", "î": "i", "ï": "i",
    "ó": "o", "ò": "o", "ô": "o", "ö": "o",
    "ú": "u", "ù": "u", "û": "u", "ü": "u",
    "ñ": "n", "ç": "c"})

def normalize(text):
    # мягкие переносы (U+00AD, в журнальной вёрстке внутри слов) -- склейка
    text = text.replace("\xad", "")
    text = text.lower().translate(FOLD)
    # ṭ/ḍ и прочие комбинированные диакритики
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    # довоенная орфография -> современная
    text = re.sub(r"oe", "u", text)
    text = re.sub(r"tj", "c", text)
    text = re.sub(r"dj", "j", text)
    return text

def tokenize(sentence):
    out = []
    for tok in re.findall(r"[a-z]+(?:-[a-z]+)*|\d+", sentence):
        if tok.isdigit():
            out.append("ORDINAL1")
        elif tok in PRONOUNS:
            out.append("PRON1")
        else:
            out.append(tok)
    return out

SENT_SPLIT = re.compile(r"(?<=[.?!;])\s+|\s*\|\|\s*|\s*\|\s*")

# ---------------------------------------------------------------- pipeline --
def clean_file(path):
    """-> list of sentences (each = list of tokens)"""
    lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
    body = lines[1:]                                  # строка 1 = заголовок
    kept, prev_jav = [], True
    for ln in body:
        ln = ln.strip()
        if not ln:
            continue
        if (PAGE_MARK.match(ln) or NUM_ONLY.match(ln) or
                ln in ("[", "]") or EDITORIAL.search(ln) or
                PUPUH_HEAD.match(ln) or is_notation_line(ln)):
            continue
        ln = BROKEN_WORD.sub(" ", ln)
        ln = FOOTNOTE_REF.sub(" ", ln)
        j, o = lang_score(ln)
        if j + o == 0:                # нет сигнала -- наследуем решение
            keep = prev_jav
        else:
            keep = j > o
            prev_jav = keep
        if keep:
            kept.append(ln)
    sentences = []
    for ln in kept:
        for s in SENT_SPLIT.split(normalize(ln)):
            toks = tokenize(s)
            # отбрасываем короткие сегменты и "разрядку" заголовков
            # (п а н г к у р), где большинство токенов -- одиночные буквы
            if len(toks) >= 3 and \
                    sum(1 for t in toks if len(t) == 1) <= len(toks) // 2:
                sentences.append(toks)
    return sentences

def main():
    os.makedirs(OUT, exist_ok=True)
    excluded, stats = [], Counter()
    buckets = ("sastra", "arsip", "jurnal", "majalah")
    corp_text = {b: open(os.path.join(OUT, f"corpus_text_{b}.txt"), "w",
                         encoding="utf-8") for b in buckets}
    corp_seg = {b: open(os.path.join(OUT, f"corpus_segments_{b}.txt"), "w",
                        encoding="utf-8") for b in buckets}
    for dirp, _, files in os.walk(RAW):
        for fn in sorted(files):
            if not fn.endswith(".txt") or fn.startswith("_"):
                continue
            src = os.path.join(dirp, fn)
            rel = os.path.relpath(src, RAW)
            title = open(src, encoding="utf-8", errors="replace").readline().strip()
            if EXCLUDE_TITLE.search(title) or EXCLUDE_TITLE.search(fn):
                excluded.append((rel, "dictionary/grammar/wordlist"))
                continue
            b = bucket_of(rel, title)
            sents = clean_file(src)
            ntok = sum(len(s) for s in sents)
            if ntok < 30:
                excluded.append((rel, f"too short after cleaning ({ntok} tok)"))
                continue
            flat = rel.replace("/", "__")
            os.makedirs(os.path.join(OUT, "texts", b), exist_ok=True)
            with open(os.path.join(OUT, "texts", b, flat), "w",
                      encoding="utf-8") as f:
                for s in sents:
                    f.write(" ".join(s) + "\n")
            corp_text[b].write(" ".join(" ".join(s) for s in sents) + "\n")
            for s in sents:
                corp_seg[b].write(" ".join(s) + "\n")
            stats[b + "_files"] += 1
            stats[b + "_tokens"] += ntok
            stats[b + "_sents"] += len(sents)
    for f in list(corp_text.values()) + list(corp_seg.values()):
        f.close()
    with open(os.path.join(OUT, "_excluded.tsv"), "w", encoding="utf-8") as f:
        f.write("file\treason\n")
        for r, why in excluded:
            f.write(f"{r}\t{why}\n")
    with open(os.path.join(OUT, "_stats.txt"), "w", encoding="utf-8") as f:
        for k in sorted(stats):
            f.write(f"{k}: {stats[k]}\n")
        f.write(f"excluded_files: {len(excluded)}\n")
    for k in sorted(stats):
        print(f"{k}: {stats[k]}")
    print("excluded:", len(excluded))

if __name__ == "__main__":
    main()
